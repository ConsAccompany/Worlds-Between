#!/usr/bin/env python3
"""Independent static verifier for a Windows native/playtest package.

This tool never launches the game, never runs Godot, and never edits the bundle.
It checks the bytes and declarations that can be established statically.

Manifest interface (deliberately small and explicit)
---------------------------------------------------
The JSON may be the manifest object itself, or an object with one wrapper key
``manifest``, ``bundleManifest`` or ``data``.  The following fields are read:

Required:
  sourceCommit            40 lowercase hex characters.  ``--expect-source-commit``
                          optionally pins it.
  files                   Mapping keyed by BASENAME only.  Each value is an
                          object with integer ``bytes`` and hex ``sha256``.
                          Nested paths/absolute paths/traversal are rejected.
  nativeReleaseExport     Boolean.  True selects the native-export gate; False
                          selects the developer runtime+PCK gate.  If omitted,
                          a template block or a non-editor executable selects
                          native, while a Godot editor runtime selects developer.
                          Contradictory kind/label declarations are rejected.

Native-export additional requirement:
  template                Object (also accepted as ``templateProvenance``,
                          ``exportTemplate``, ``engine.template`` or
                          ``template_provenance``) with:
                            source or url     official Godot 4.7.2 download URL
                            version           ``4.7.2-stable`` (or ``4.7.2``)
                            sha256            64 hex characters
                            signed/unsigned   exactly one coherent declaration
                            file              optional basename; if present it
                                              must be listed and hash-match
  The native main executable's PE certificate table must agree with the
  signed/unsigned declaration.  An unsigned MVP is accepted; a signing
  certificate is never required by this verifier.

Optional:
  label, buildTag, launchers (mapping name->basename), launcherDefaultFlags,
  pck/mainPack/pack, entrypoint/mainExe.  ``manifest.passed`` is intentionally
  ignored and is never used as evidence.

Usage:
  python <tool> --bundle DIR --manifest JSON --output UNIQUE.json
  python <tool> --bundle DIR --manifest JSON --output UNIQUE.json --require-native
  python <tool> --self-test

Exit codes: 0 pass, 1 verification failure, 2 input/output error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import struct
import sys
import shutil
import uuid
from datetime import datetime, timezone

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
EDITOR_RE = re.compile(r"^Godot_v[0-9][^/]*_win64(?:_console)?\.exe$", re.I)
OFFICIAL_HOSTS = (
    "godotengine.org",
    "downloads.godotengine.org",
    "downloads.tuxfamily.org",
    "github.com/godotengine/",
)
SAFE_VERSION = re.compile(r"^4\.7\.2(?:[-.]stable)?$", re.I)
DANGEROUS_EXT = {
    ".exe", ".dll", ".com", ".scr", ".sys", ".drv", ".cpl", ".msi", ".hta",
    ".bat", ".cmd", ".ps1", ".vbs", ".vbe", ".js", ".jse", ".wsf", ".wsh",
    ".pck",
}
TEXT_LAUNCHER_EXT = {".cmd", ".bat", ".ps1", ".sh"}
LICENSE_WORDS = re.compile(
    r"(license|licence|notice|copyright|third[-_ ]?party|credits|authors)",
    re.I,
)
PRIVATE_WORDS = re.compile(
    r"(^|[._ -])(auth|authentication|credentials?|secrets?|tokens?|"
    r"passw(?:or)?d|api[_-]?key|private[_-]?key|id_rsa|id_ed25519|"
    r"netrc|npmrc|pypirc|cookies?|sessions?)([._ -]|$)",
    re.I,
)
PRIVATE_EXTS = {".pem", ".key", ".pfx", ".p12", ".jks", ".keystore", ".ppk"}
PRIVATE_EXACT = {
    ".env", ".netrc", ".npmrc", ".pypirc", "project.godot",
    "export_presets.cfg", "export_credentials.cfg", "auth.cfg",
    "credentials.cfg", "secrets.cfg",
}
RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def ext_path(path):
    """Return an extended-length Windows path for all file I/O."""
    s = os.path.abspath(os.fspath(path))
    if os.name != "nt" or s.startswith("\\\\?\\"):
        return s
    if s.startswith("\\\\"):
        return "\\\\?\\UNC\\" + s[2:]
    return "\\\\?\\" + s


def display_path(path):
    s = os.fspath(path)
    if s.startswith("\\\\?\\UNC\\"):
        return "\\\\" + s[8:]
    if s.startswith("\\\\?\\"):
        return s[4:]
    return s


def is_reparse(st):
    attrs = getattr(st, "st_file_attributes", 0)
    return bool(attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400))


def read_text(path):
    with open(ext_path(path), "r", encoding="utf-8-sig", errors="strict", newline="") as f:
        return f.read()


def read_head(path, count):
    with open(ext_path(path), "rb") as f:
        return f.read(count)


def sha256_file(path):
    h = hashlib.sha256()
    with open(ext_path(path), "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def walk_files(root):
    """Yield (relative POSIX path, absolute extended path, size).

    Reparse points are rejected at every level, so no path can escape through
    a symlink or Windows junction.  The caller separately checks containment.
    """
    root_ext = ext_path(root)
    files = []
    stack = [(root_ext, "")]
    while stack:
        directory, prefix = stack.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                path = os.path.join(directory, entry.name)
                st = entry.stat(follow_symlinks=False)
                if entry.is_symlink() or is_reparse(st):
                    raise ValueError("reparse point/symlink: " + (prefix + entry.name))
                rel = entry.name if not prefix else prefix + "/" + entry.name
                if entry.is_dir(follow_symlinks=False):
                    stack.append((path, rel))
                elif entry.is_file(follow_symlinks=False):
                    files.append((rel, path, st.st_size))
                else:
                    raise ValueError("unsupported filesystem entry: " + rel)
    return sorted(files, key=lambda item: item[0].casefold())


def parse_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.strip().lower() in {"true", "yes", "1"}:
            return True
        if value.strip().lower() in {"false", "no", "0"}:
            return False
    return None


def safe_basename(name):
    if not isinstance(name, str) or name in {"", ".", ".."}:
        return False, "not a non-empty basename"
    if any(ch in name for ch in '/\\:*?"<>|'):
        return False, "path separator, drive/stream colon, or Windows-invalid character"
    if name != os.path.basename(name):
        return False, "not a bare basename"
    if name.rstrip(" .") != name:
        return False, "trailing dot/space is unsafe on Windows"
    if any(ord(ch) < 32 for ch in name):
        return False, "control character"
    if name.split(".")[0].upper() in RESERVED:
        return False, "Windows reserved device name"
    return True, ""


def license_notice(name):
    return bool(LICENSE_WORDS.search(name)) and os.path.splitext(name)[1].lower() in {
        ".json", ".txt", ".md", ".html", ".htm",
    }


def private_reason(name):
    if license_notice(name):
        return None
    low = name.lower()
    stem, suffix = os.path.splitext(low)
    if low in PRIVATE_EXACT or stem in PRIVATE_EXACT:
        return "known private auth/config filename"
    if low.startswith(".env"):
        return "environment file"
    if suffix in PRIVATE_EXTS:
        return "private key/certificate/keystore extension"
    if PRIVATE_WORDS.search(stem):
        return "private credential/config keyword"
    return None


def parse_pe(path):
    """Parse the bytes the task asks about, plus the Authenticode table."""
    with open(ext_path(path), "rb") as f:
        dos = f.read(0x40)
        info = {"mz": False, "pe": False, "machine": None, "optional_magic": None,
                "pe_offset": None, "has_authenticode": None,
                "certificate_offset": None, "certificate_size": None,
                "file_size": os.path.getsize(ext_path(path))}
        if len(dos) < 0x40 or dos[:2] != b"MZ":
            return info, "missing MZ header"
        info["mz"] = True
        pe_offset = struct.unpack_from("<I", dos, 0x3C)[0]
        info["pe_offset"] = pe_offset
        if pe_offset < 0x40 or pe_offset > info["file_size"] - 24:
            return info, "e_lfanew outside file"
        f.seek(pe_offset)
        nt = f.read(24)
        if len(nt) < 24 or nt[:4] != b"PE\0\0":
            return info, "missing PE signature"
        info["pe"] = True
        machine, sections, _ts, _sym, _num, size_opt, _chars = struct.unpack_from(
            "<HHIIIHH", nt, 4
        )
        info["machine"] = machine
        if size_opt < 2 or size_opt > 4096:
            return info, "invalid optional-header size"
        opt = f.read(size_opt)
        if len(opt) < size_opt:
            return info, "truncated optional header"
        info["optional_magic"] = struct.unpack_from("<H", opt, 0)[0]
        if info["optional_magic"] == 0x20B:
            if size_opt < 0x70:
                return info, "PE32+ optional header too small"
            if len(opt) >= 0x70:
                nrva = struct.unpack_from("<I", opt, 0x6C)[0]
                if nrva >= 5 and len(opt) >= 0x98:
                    cert_off, cert_size = struct.unpack_from("<II", opt, 0x90)
                    info["certificate_offset"] = cert_off
                    info["certificate_size"] = cert_size
                    info["has_authenticode"] = cert_size > 0
                    if cert_size > 0 and cert_off + cert_size > info["file_size"]:
                        return info, "Authenticode table outside file"
        return info, ""


def parse_pck(path):
    head = read_head(path, 16)
    if len(head) < 8 or head[:4] != b"GDPC":
        return {"magic": head[:4].decode("latin-1"), "version": None}, "missing GDPC magic"
    return {"magic": "GDPC", "version": struct.unpack_from("<I", head, 4)[0]}, ""


def pck_basename(token):
    token = token.replace("\\", "/").rsplit("/", 1)[-1]
    token = token.rsplit("%", 1)[-1]
    token = re.sub(r"^~[^/\\]*?0", "", token)
    return token.casefold()


def find_template(manifest):
    for key in ("template", "templateProvenance", "exportTemplate", "template_provenance"):
        value = manifest.get(key)
        if isinstance(value, dict):
            return value, key
    engine = manifest.get("engine")
    if isinstance(engine, dict):
        for key in ("template", "templateProvenance", "exportTemplate"):
            value = engine.get(key)
            if isinstance(value, dict):
                return value, "engine." + key
    return None, None


def signing_declaration(template):
    signed = parse_bool(template.get("signed"))
    unsigned = parse_bool(template.get("unsigned"))
    status = template.get("signing") or template.get("signatureStatus")
    values = []
    if signed is not None:
        values.append("signed" if signed else "unsigned")
    if unsigned is not None:
        values.append("unsigned" if unsigned else "signed")
    if isinstance(status, str):
        low = status.strip().lower()
        if low in {"unsigned", "none", "no", "false"}:
            values.append("unsigned")
        elif low in {"signed", "yes", "true"}:
            values.append("signed")
        elif low:
            return None
    unique = set(values)
    if len(unique) == 1:
        return unique.pop()
    return None


def normalize_kind(manifest):
    for key in ("bundleKind", "packageKind", "kind"):
        value = manifest.get(key)
        if isinstance(value, str):
            low = value.strip().lower()
            if "developer" in low or "playtest" in low or "runtime" in low:
                return "developer"
            if "native" in low or "export" in low or "release" in low:
                return "native"
    return None


class Report:
    def __init__(self, bundle, manifest, require_native, expected_commit):
        self.bundle = bundle
        self.manifest = manifest
        self.require_native = require_native
        self.expected_commit = expected_commit
        self.checks = []
        self.warnings = []
        self.limitations = []
        self.members = []
        self.native = None
        self.bundle_kind = None
        self.source_commit = None
        self.manifest_sha256 = None

    def check(self, name, ok, detail="", status=None):
        if status is None:
            status = "pass" if ok else "fail"
        self.checks.append({
            "name": name,
            "status": status,
            "passed": status == "pass",
            "detail": str(detail)[:2000],
        })
        return bool(ok)

    def fail(self, name, detail):
        return self.check(name, False, detail)

    def na(self, name, detail):
        return self.check(name, True, detail, status="not_applicable")

    def warn(self, name, detail):
        self.warnings.append({"name": name, "detail": str(detail)[:2000]})

    def limit(self, detail):
        self.limitations.append(str(detail))

    def finish(self):
        failures = [c for c in self.checks if c["status"] == "fail"]
        counts = {
            "pass": sum(c["status"] == "pass" for c in self.checks),
            "fail": len(failures),
            "not_applicable": sum(c["status"] == "not_applicable" for c in self.checks),
        }
        result = {
            "tool": "rpg-2-star-ocean-the-second_mvp_native-windows-package-check_v01",
            "verifiedAtUtc": datetime.now(timezone.utc).isoformat(),
            "bundle": display_path(self.bundle),
            "manifest": display_path(self.manifest),
            "manifestSha256": self.manifest_sha256,
            "sourceCommit": self.source_commit,
            "bundleKind": self.bundle_kind,
            "nativeRelease": bool(self.native),
            "requireNative": bool(self.require_native),
            "passed": not failures,
            "counts": counts,
            "failures": failures,
            "warnings": self.warnings,
            "limitations": self.limitations,
            "checks": self.checks,
            "members": self.members,
            "manifestPassedIgnored": True,
        }
        return result


def verify_bundle(bundle, manifest_path, require_native=False, expected_commit=None):
    report = Report(bundle, manifest_path, require_native, expected_commit)
    bundle = os.path.abspath(os.fspath(bundle))
    manifest_path = os.path.abspath(os.fspath(manifest_path))
    report.bundle = bundle
    report.manifest = manifest_path

    bundle_ok = os.path.isdir(ext_path(bundle)) and not os.path.islink(ext_path(bundle))
    report.check("input-bundle-directory", bundle_ok, display_path(bundle))
    manifest_ok = os.path.isfile(ext_path(manifest_path)) and not os.path.islink(ext_path(manifest_path))
    report.check("input-manifest-file", manifest_ok, display_path(manifest_path))
    if not bundle_ok or not manifest_ok:
        report.limit("Input path missing or is a symlink; no package claim is made.")
        return report.finish()

    try:
        root_stat = os.stat(ext_path(bundle), follow_symlinks=False)
        report.check("bundle-root-no-reparse-point", not is_reparse(root_stat), display_path(bundle))
    except OSError as exc:
        report.fail("bundle-root-stat", str(exc))

    try:
        manifest_stat = os.stat(ext_path(manifest_path), follow_symlinks=False)
        report.check("manifest-no-reparse-point", not is_reparse(manifest_stat), display_path(manifest_path))
    except OSError as exc:
        report.fail("manifest-stat", str(exc))

    try:
        raw_manifest = open(ext_path(manifest_path), "rb").read()
        report.manifest_sha256 = hashlib.sha256(raw_manifest).hexdigest()
        manifest = json.loads(raw_manifest.decode("utf-8-sig"))
        report.check("manifest-json-utf8", isinstance(manifest, dict), "decoded as UTF-8 JSON object")
    except Exception as exc:
        report.fail("manifest-json-utf8", f"{type(exc).__name__}: {exc}")
        report.limit("Manifest could not be parsed; no package claim is made.")
        return report.finish()

    if isinstance(manifest, dict) and "files" not in manifest:
        for wrapper in ("manifest", "bundleManifest", "data"):
            inner = manifest.get(wrapper)
            if isinstance(inner, dict) and "files" in inner:
                merged = dict(manifest)
                merged.update(inner)
                manifest = merged
                report.warn("manifest-wrapper", "used wrapper key: " + wrapper)
                break

    report.check(
        "manifest-passed-not-trusted", True,
        "manifest.passed/checks are ignored; every gate below is recomputed",
    )
    if "passed" in manifest:
        report.warn("manifest-passed-field", "present and ignored: " + repr(manifest.get("passed"))[:120])

    source_commit = manifest.get("sourceCommit")
    report.source_commit = source_commit if isinstance(source_commit, str) else None
    report.check(
        "manifest-source-commit",
        isinstance(source_commit, str) and bool(HEX40.fullmatch(source_commit)),
        repr(source_commit)[:120],
    )
    if expected_commit:
        report.check(
            "source-commit-expected",
            isinstance(source_commit, str) and source_commit.lower() == expected_commit.lower(),
            f"expected {expected_commit}",
        )

    native_flag = parse_bool(manifest.get("nativeReleaseExport"))
    if manifest.get("nativeReleaseExport") is not None and native_flag is None:
        report.fail("manifest-native-release-flag", "nativeReleaseExport must be boolean")
    kind_hint = normalize_kind(manifest)
    template, template_key = find_template(manifest)

    try:
        disk_list = walk_files(bundle)
        report.check("bundle-no-reparse-points", True, f"{len(disk_list)} regular files")
    except Exception as exc:
        report.fail("bundle-no-reparse-points", f"{type(exc).__name__}: {exc}")
        report.limit("A symlink/junction or unsupported entry prevented a complete walk.")
        return report.finish()

    disk = {rel: (path, size) for rel, path, size in disk_list}
    disk_cf = {}
    disk_collisions = []
    for rel in disk:
        key = rel.casefold()
        if key in disk_cf:
            disk_collisions.append((disk_cf[key], rel))
        disk_cf[key] = rel
    report.check("bundle-no-case-collisions", not disk_collisions, str(disk_collisions[:5]))

    manifest_real = os.path.normcase(os.path.realpath(ext_path(manifest_path)))
    bundle_real = os.path.normcase(os.path.realpath(ext_path(bundle)))
    manifest_inside = False
    manifest_rel = None
    try:
        if os.path.commonpath([bundle_real, manifest_real]) == bundle_real:
            manifest_inside = True
            manifest_rel = os.path.relpath(manifest_real, bundle_real).replace("\\", "/")
    except ValueError:
        pass

    files_obj = manifest.get("files")
    report.check(
        "manifest-files-mapping",
        isinstance(files_obj, dict) and len(files_obj) > 0,
        f"type={type(files_obj).__name__} count={len(files_obj) if isinstance(files_obj, dict) else 0}",
    )
    expected = {}
    expected_cf = {}
    if isinstance(files_obj, dict):
        for key, info in files_obj.items():
            safe, why = safe_basename(key)
            report.check("manifest-safe-basename-" + repr(key)[:120], safe, why)
            if not safe:
                continue
            cf = key.casefold()
            if cf in expected_cf:
                report.fail("manifest-case-duplicate-" + key, "duplicates " + expected_cf[cf])
                continue
            expected_cf[cf] = key
            expected[key] = info
            if not isinstance(info, dict):
                report.fail("manifest-entry-object-" + key, type(info).__name__)
                continue
            size = info.get("bytes")
            digest = info.get("sha256")
            report.check(
                "manifest-bytes-" + key,
                isinstance(size, int) and not isinstance(size, bool) and size >= 0,
                repr(size)[:80],
            )
            report.check(
                "manifest-sha256-" + key,
                isinstance(digest, str) and bool(HEX64.fullmatch(digest.lower())),
                repr(digest)[:80],
            )

    exes = [name for name in expected if name.lower().endswith(".exe")]
    editor_runtime = [name for name in exes if EDITOR_RE.fullmatch(name)]
    if require_native:
        native = True
    elif native_flag is not None:
        native = native_flag
    elif kind_hint is not None:
        native = kind_hint == "native"
    elif template is not None:
        native = True
    elif editor_runtime:
        native = False
    else:
        native = None
    report.native = native
    report.bundle_kind = "native-windows-export" if native else (
        "developer-runtime-pck" if native is False else "undeclared"
    )
    report.check(
        "bundle-kind-declared",
        native is not None,
        f"nativeReleaseExport={manifest.get('nativeReleaseExport')!r} "
        f"kindHint={kind_hint!r} template={template_key!r}",
    )
    if native_flag is not None and kind_hint is not None and native_flag != (kind_hint == "native"):
        report.fail("bundle-kind-consistency", "nativeReleaseExport contradicts bundleKind")
    if native is None:
        native = False
        report.bundle_kind = "undeclared"

    label = str(manifest.get("label") or "")
    if native:
        report.check(
            "native-label-consistency",
            not re.search(r"developer|not a native release|runtime\+pck", label, re.I),
            label[:300],
        )
    else:
        report.check(
            "developer-label-consistency",
            not re.search(r"(?<!not a )native (?:release )?export", label, re.I) or
            "not a native release" in label.lower(),
            label[:300],
        )

    expected_all_cf = set(expected_cf)
    if manifest_inside and manifest_rel:
        expected_all_cf.add(manifest_rel.casefold())

    for key, info in expected.items():
        actual_rel = key if key in disk else disk_cf.get(key.casefold())
        if actual_rel is None or actual_rel not in disk:
            report.fail("file-present-" + key, "listed in manifest but missing from bundle")
            continue
        path, actual_size = disk[actual_rel]
        if actual_rel != key:
            report.warn("filename-case-" + key, "on-disk name is " + actual_rel)
        try:
            actual_real = os.path.normcase(os.path.realpath(ext_path(path)))
            contained = os.path.commonpath([bundle_real, actual_real]) == bundle_real
        except ValueError:
            contained = False
        report.check("member-contained-" + key, contained, actual_rel)
        declared_size = info.get("bytes") if isinstance(info, dict) else None
        report.check(
            "member-size-" + key,
            isinstance(declared_size, int) and not isinstance(declared_size, bool) and
            actual_size == declared_size,
            f"actual={actual_size} declared={declared_size!r}",
        )
        try:
            actual_sha = sha256_file(path)
        except Exception as exc:
            report.fail("member-sha256-" + key, f"{type(exc).__name__}: {exc}")
            actual_sha = None
        declared_sha = info.get("sha256") if isinstance(info, dict) else None
        report.check(
            "member-sha256-" + key,
            isinstance(declared_sha, str) and actual_sha is not None and
            actual_sha.lower() == declared_sha.lower(),
            f"actual={actual_sha} declared={declared_sha!r}",
        )
        member = {
            "name": key,
            "bytes": actual_size,
            "sha256": actual_sha,
            "declaredBytes": declared_size,
            "declaredSha256": declared_sha,
        }
        report.members.append(member)

        reason = private_reason(key)
        report.check("no-private-auth-config-" + key, reason is None, reason or "no private marker")

    extras = []
    for rel in disk:
        if rel.casefold() not in expected_all_cf:
            extras.append(rel)
    for rel in extras:
        reason = private_reason(rel)
        report.check("no-private-extra-" + rel, reason is None, reason or "no private marker")
        ext = os.path.splitext(rel)[1].lower()
        dangerous = ext in DANGEROUS_EXT
        if not dangerous:
            try:
                dangerous = read_head(disk[rel][0], 2) == b"MZ"
            except Exception:
                dangerous = False
        report.check(
            "no-dangerous-extra-" + rel,
            not dangerous,
            "unreferenced executable/script/pack" if dangerous else "benign unreferenced file",
        )
        if not dangerous:
            report.warn("benign-extra-" + rel, "not listed in manifest.files; not an executable/script/pack")

    for name in expected:
        if name not in disk:
            continue
        suffix = os.path.splitext(name)[1].lower()
        is_pe_name = suffix in {".exe", ".dll", ".scr"}
        if not is_pe_name:
            try:
                is_pe_name = read_head(disk[name][0], 2) == b"MZ"
            except OSError:
                is_pe_name = False
        if not is_pe_name:
            continue
        try:
            info, error = parse_pe(disk[name][0])
        except Exception as exc:
            report.fail("pe64-amd64-" + name, f"{type(exc).__name__}: {exc}")
            continue
        ok = (
            error == "" and info["mz"] and info["pe"] and
            info["machine"] == 0x8664 and info["optional_magic"] == 0x20B
        )
        report.check(
            "pe64-amd64-" + name, ok,
            f"MZ={info['mz']} PE={info['pe']} machine={info['machine']!r} "
            f"optionalMagic={info['optional_magic']!r} error={error or 'none'}",
        )
        if info["has_authenticode"] is not None:
            report.warn(
                "authenticode-" + name,
                "present" if info["has_authenticode"] else "absent",
            )

    report.check(
        "no-editor-runtime-for-native",
        (not native) or (not editor_runtime),
        ("editor runtime(s): " + ", ".join(editor_runtime)) if editor_runtime else "no Godot editor runtime",
        status="fail" if (native and editor_runtime) else ("not_applicable" if not native else "pass"),
    )
    if editor_runtime and not native:
        report.warn("developer-runtime-present",
                    "Godot editor runtime + PCK; not a native export: " + ", ".join(editor_runtime))
        report.limit("Developer runtime+PCK bundle contains a Godot editor runtime; it cannot pass the native gate.")
    if editor_runtime:
        versions = {m.group(1) for m in (re.match(r"^Godot_v([^_]+)_win64", n, re.I) for n in editor_runtime) if m}
        report.check(
            "editor-runtime-version", versions <= {"4.7.2-stable"},
            "declared runtime version: " + ", ".join(sorted(versions)),
        )

    pcks = [name for name in expected if name.lower().endswith(".pck")]
    report.check("exactly-one-pck", len(pcks) == 1, str(pcks))
    pck_name = pcks[0] if len(pcks) == 1 else None
    if pck_name and pck_name in disk:
        try:
            pck_info, pck_error = parse_pck(disk[pck_name][0])
            report.check("pck-header-magic", pck_error == "", f"{pck_info} error={pck_error or 'none'}")
        except Exception as exc:
            report.fail("pck-header-magic", f"{type(exc).__name__}: {exc}")
    elif pck_name:
        report.fail("pck-header-magic", "PCK listed but missing")

    launchers = []
    declared_launchers = manifest.get("launchers")
    if isinstance(declared_launchers, dict):
        for role, value in declared_launchers.items():
            if not isinstance(value, str):
                report.fail("launcher-declared-" + str(role), "not a basename string")
                continue
            actual = value if value in expected else expected_cf.get(value.casefold())
            report.check("launcher-declared-" + str(role), actual is not None, value)
            if actual:
                launchers.append(actual)
    elif declared_launchers is not None:
        report.fail("launchers-shape", "launchers must be a mapping")

    pck_refs = set()
    for name in expected:
        if os.path.splitext(name)[1].lower() not in TEXT_LAUNCHER_EXT:
            continue
        try:
            text = read_text(disk[name][0]) if name in disk else ""
        except Exception as exc:
            report.fail("launcher-utf8-" + name, f"{type(exc).__name__}: {exc}")
            continue
        if re.search(r"--editor\b", text, re.I):
            report.fail("launcher-no-editor-flag-" + name, "--editor present")
        refs_here = set()
        for match in re.finditer(r"""(?i)([^\s"'<>|]+\.pck)""", text):
            token = pck_basename(match.group(1))
            pck_refs.add(token)
            refs_here.add(token)
        if pck_name:
            report.check("launcher-pck-reference-" + name, refs_here == {pck_name.casefold()},
                         str(sorted(refs_here)))

    declared_pck = manifest.get("pck") or manifest.get("mainPack") or manifest.get("pack")
    if isinstance(declared_pck, str):
        declared_base = declared_pck.replace("\\", "/").rsplit("/", 1)[-1]
        report.check("declared-pck-basename", bool(pck_name) and declared_base == pck_name,
                     f"declared={declared_base!r} actual={pck_name!r}")
        pck_refs.add(declared_base.casefold())
    report.check(
        "pck-reference-present",
        bool(pck_name) and (pck_name.casefold() in pck_refs or bool(declared_pck)),
        "launcher/manifest reference: " + ", ".join(sorted(pck_refs)),
    )
    if declared_launchers is None:
        report.na("launcher-metadata", "not declared; native entrypoint may be the executable itself")

    flags = manifest.get("launcherDefaultFlags")
    if isinstance(flags, list):
        joined = " ".join(str(item) for item in flags)
        report.check("launcher-no-editor-default-flags", not re.search(r"--editor\b", joined, re.I), joined[:300])
        if not native:
            report.check("developer-main-pack-flag", "--main-pack" in joined, joined[:300])

    if template is None:
        if native:
            report.fail("native-template-provenance", "template block missing")
            report.limit("Native export template provenance was not declared.")
        else:
            report.na("native-template-provenance",
                      "developer runtime+PCK bundle has no native export template")
            report.limit("No native export template provenance: this is a declared developer runtime+PCK bundle.")
    else:
        report.check("template-provenance-object", isinstance(template, dict), template_key)
        source = template.get("source") or template.get("url") or template.get("downloadUrl")
        official = parse_bool(template.get("official"))
        if official is False:
            report.fail("template-official-source", "official=false")
        elif not isinstance(source, str):
            report.fail("template-official-source", "official source URL missing")
        else:
            low = source.lower()
            host_ok = any(host in low for host in OFFICIAL_HOSTS)
            version_ok = "4.7.2" in low
            report.check("template-official-source", host_ok and version_ok, source[:500])
        version = template.get("version") or template.get("godotVersion")
        report.check("template-version", isinstance(version, str) and bool(SAFE_VERSION.fullmatch(version)),
                     repr(version)[:120])
        template_sha = template.get("sha256") or template.get("templateSha256")
        report.check("template-sha256", isinstance(template_sha, str) and bool(HEX64.fullmatch(template_sha.lower())),
                     repr(template_sha)[:120])
        template_file = template.get("file")
        if isinstance(template_file, str) and template_file:
            safe, _ = safe_basename(template_file)
            actual = template_file if safe and template_file in expected else expected_cf.get(template_file.casefold())
            report.check("template-file-listed", bool(actual), template_file)
            if actual and isinstance(template_sha, str) and actual in disk:
                report.check("template-file-sha256", sha256_file(disk[actual][0]) == template_sha.lower(),
                             actual)

        signing = signing_declaration(template)
        report.check(
            "unsigned-status-declared",
            signing in {"signed", "unsigned"},
            "coherent signed/unsigned declaration required; got " + repr(signing),
        )
        if signing in {"signed", "unsigned"}:
            main_name = manifest.get("entrypoint") or manifest.get("mainExe")
            if not isinstance(main_name, str):
                main_name = next((n for n in exes if n not in editor_runtime), exes[0] if exes else None)
            if main_name in disk:
                try:
                    pe_info, _pe_error = parse_pe(disk[main_name][0])
                    has_sig = bool(pe_info.get("has_authenticode"))
                    report.check(
                        "declared-signature-matches-header",
                        (signing == "signed") == has_sig,
                        f"declared={signing} AuthenticodeTable={has_sig} exe={main_name}",
                    )
                    if signing == "signed":
                        report.limit("Authenticode table presence was checked; cryptographic trust and certificate validity were not.")
                except Exception as exc:
                    report.fail("declared-signature-matches-header", f"{type(exc).__name__}: {exc}")
            elif native:
                report.fail("declared-signature-matches-header", "main executable unavailable")

    if native:
        entry = manifest.get("entrypoint") or manifest.get("mainExe")
        if isinstance(entry, str):
            report.check("native-entrypoint-listed", entry in expected, entry)
        non_editor = [n for n in exes if n not in editor_runtime]
        report.check("native-main-executable", bool(non_editor), str(non_editor))
        report.check("native-external-pck", bool(pck_name), str(pck_name))
        report.limit("Static verifier: no launch, rendering, input, save or gameplay behavior was exercised.")
        report.limit("Template archive is not fetched; official URL/version/hash are declaration checks, not an upstream download.")
    else:
        report.limit("Developer runtime+PCK bundle, not a native Windows release export.")
        report.limit("Static verifier: no launch, rendering, input, save or gameplay behavior was exercised.")

    report.check(
        "no-signing-certificate-required",
        True,
        "unsigned MVP accepted when the manifest declares unsigned and the PE certificate table is absent",
    )
    return report.finish()


# ---------------------------------------------------------------------------
# Embedded controlled self-tests (tiny fixtures, no game/test-suite execution)
# ---------------------------------------------------------------------------

def _make_pe(path):
    data = bytearray(0x400)
    data[0:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<H", data, 0x84, 0x8664)
    struct.pack_into("<H", data, 0x86, 0x0001)
    struct.pack_into("<H", data, 0x94, 0x00F0)
    struct.pack_into("<H", data, 0x96, 0x0002)
    struct.pack_into("<H", data, 0x98, 0x020B)
    struct.pack_into("<I", data, 0x98 + 0x6C, 16)
    struct.pack_into("<I", data, 0x98 + 0x90, 0)
    struct.pack_into("<I", data, 0x98 + 0x94, 0)
    with open(ext_path(path), "wb") as f:
        f.write(data)


def _write_manifest(root, manifest):
    with open(ext_path(os.path.join(root, "manifest.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _refresh_files(root, manifest, template=None):
    files = {}
    for name in sorted(os.listdir(ext_path(root))):
        if name == "manifest.json":
            continue
        path = os.path.join(root, name)
        if os.path.isfile(ext_path(path)):
            files[name] = {"bytes": os.path.getsize(ext_path(path)), "sha256": sha256_file(path)}
    manifest["files"] = files
    if template is not None:
        manifest["template"] = template
    _write_manifest(root, manifest)


def _fixture(base):
    root = os.path.join(base, "fixture")
    os.makedirs(ext_path(root))
    _make_pe(os.path.join(root, "game.exe"))
    with open(ext_path(os.path.join(root, "game.pck")), "wb") as f:
        f.write(b"GDPC" + struct.pack("<I", 3) + b"\0" * 16 + b"fixture-payload")
    with open(ext_path(os.path.join(root, "run.cmd")), "w", encoding="utf-8", newline="\r\n") as f:
        f.write('@echo off\r\n"%~dp0game.exe" --main-pack "%~dp0game.pck" %*\r\n')
    with open(ext_path(os.path.join(root, "license-notice.json")), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"notice": "test-only notice, not a private config"}, f)
    manifest = {
        "label": "Native Windows MVP export test fixture",
        "sourceCommit": "d5f204373c17c62e45e92dea14c3a2e85c525062",
        "nativeReleaseExport": True,
        "launchers": {"normal": "run.cmd"},
        "launcherDefaultFlags": ["--main-pack <pck>"],
        "pck": "game.pck",
        "entrypoint": "game.exe",
        "passed": True,
        "template": {
            "official": True,
            "source": "https://godotengine.org/download/archive/4.7.2-stable/",
            "version": "4.7.2-stable",
            "sha256": "a" * 64,
            "signed": False,
            "unsigned": True,
        },
    }
    _refresh_files(root, manifest)
    return root


def _copy_case(base, name):
    src = os.path.join(base, "fixture")
    dst = os.path.join(base, "case-" + name)
    shutil.copytree(ext_path(src), ext_path(dst))
    return dst


def _load_manifest(root):
    with open(ext_path(os.path.join(root, "manifest.json")), "r", encoding="utf-8") as f:
        return json.load(f)


def self_test():
    results = []
    scratch = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work")
    os.makedirs(ext_path(scratch), exist_ok=True)
    base = os.path.abspath(os.path.join(scratch, "nv56-selftest-" + uuid.uuid4().hex[:8]))
    os.makedirs(ext_path(base), exist_ok=False)
    try:
        _fixture(base)

        def case(name, mutate, expect_pass, expect_fragment=None):
            root = _copy_case(base, name)
            mutate(root)
            report = verify_bundle(root, os.path.join(root, "manifest.json"), require_native=True)
            ok = report["passed"] == expect_pass
            fragment_ok = True
            if expect_fragment:
                haystack = " ".join(
                    f"{c['name']} {c['detail']}" for c in report["checks"] if c["status"] == "fail"
                ).lower()
                fragment_ok = expect_fragment.lower() in haystack
            ok = ok and fragment_ok
            results.append({"case": name, "expectedPassed": expect_pass, "actualPassed": report["passed"],
                            "expectedFailureFragment": expect_fragment, "ok": ok})
            if not ok:
                print("SELFTEST FAIL", name, json.dumps(report["failures"], indent=2)[:3000])

        def set_label(root, label):
            manifest = _load_manifest(root)
            manifest["label"] = label
            _write_manifest(root, manifest)

        case("native-valid", lambda root: None, True)
        case("native-playtest-label", lambda root: set_label(root, "NATIVE WINDOWS UNSIGNED PLAYTEST CANDIDATE - not a final release"), True)
        case("native-developer-label-rejected", lambda root: set_label(root, "DEVELOPER runtime+PCK bundle"), False, "native-label-consistency")
        case("changed-pck-bytes", lambda root: _flip_byte(os.path.join(root, "game.pck"), 20),
             False, "member-sha256-game.pck")
        case("changed-pck-size", lambda root: _append_byte(os.path.join(root, "game.pck")),
             False, "member-size-game.pck")
        case("manifest-hash-lie", lambda root: _set_manifest_hash(root), False, "member-sha256-game.pck")
        case("missing-pck", lambda root: _remove(os.path.join(root, "game.pck")), False, "file-present-game.pck")
        case("missing-launcher", lambda root: _remove(os.path.join(root, "run.cmd")), False, "file-present-run.cmd")
        case("wrong-pck-reference", _wrong_pck_reference, False, "launcher-pck-reference")
        case("path-traversal-key", _path_traversal, False, "manifest-safe-basename")
        case("editor-runtime-native", _add_editor_runtime, False, "no-editor-runtime-for-native")
        case("unsigned-not-declared", _remove_unsigned, False, "unsigned-status-declared")
        case("signed-without-cert", _claim_signed, False, "declared-signature-matches-header")
    finally:
        if os.path.commonpath([os.path.realpath(base), os.path.realpath(scratch)]) != os.path.realpath(scratch) or not os.path.basename(base).startswith("nv56-selftest-"):
            raise RuntimeError("refusing cleanup outside generated self-test workspace")
        shutil.rmtree(ext_path(base), ignore_errors=True)

    passed = all(item["ok"] for item in results)
    print(json.dumps({"selfTest": passed, "cases": len(results), "results": results}, indent=2))
    return 0 if passed else 1


def _flip_byte(path, offset):
    with open(ext_path(path), "r+b") as f:
        f.seek(offset)
        old = f.read(1)
        f.write(b"X" if old != b"X" else b"Y")


def _append_byte(path):
    with open(ext_path(path), "ab") as f:
        f.write(b"X")


def _set_manifest_hash(root):
    man = _load_manifest(root)
    man["files"]["game.pck"]["sha256"] = "0" * 64
    _write_manifest(root, man)


def _remove(path):
    os.remove(ext_path(path))


def _wrong_pck_reference(root):
    path = os.path.join(root, "run.cmd")
    with open(ext_path(path), "w", encoding="utf-8", newline="\r\n") as f:
        f.write('@echo off\r\n"%~dp0game.exe" --main-pack "%~dp0other.pck" %*\r\n')
    man = _load_manifest(root)
    _refresh_files(root, man, template=man.get("template"))


def _path_traversal(root):
    man = _load_manifest(root)
    man["files"]["../escape.exe"] = {"bytes": 1, "sha256": "0" * 64}
    _write_manifest(root, man)


def _add_editor_runtime(root):
    path = os.path.join(root, "Godot_v4.7.2-stable_win64.exe")
    _make_pe(path)
    man = _load_manifest(root)
    _refresh_files(root, man, template=man.get("template"))


def _remove_unsigned(root):
    man = _load_manifest(root)
    for key in ("signed", "unsigned", "signing", "signatureStatus"):
        man["template"].pop(key, None)
    _write_manifest(root, man)


def _claim_signed(root):
    man = _load_manifest(root)
    man["template"]["signed"] = True
    man["template"]["unsigned"] = False
    _write_manifest(root, man)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--bundle", help="bundle directory (required unless --self-test)")
    parser.add_argument("--manifest", help="manifest JSON (required unless --self-test)")
    parser.add_argument("--output", help="new unique JSON result path (required unless --self-test)")
    parser.add_argument("--require-native", action="store_true",
                        help="force the native-export gate even if the manifest says developer")
    parser.add_argument("--expect-source-commit", help="pin the expected 40-hex source commit")
    parser.add_argument("--self-test", action="store_true", help="run embedded controlled fixtures")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()
    if not args.bundle or not args.manifest or not args.output:
        parser.error("--bundle, --manifest and --output are required unless --self-test")

    bundle = os.path.abspath(args.bundle)
    manifest = os.path.abspath(args.manifest)
    output = os.path.abspath(args.output)
    if os.path.exists(ext_path(output)):
        print("OUTPUT_EXISTS: refusing to overwrite " + display_path(output), file=sys.stderr)
        return 2
    try:
        output_real = os.path.normcase(os.path.realpath(ext_path(output)))
        bundle_real = os.path.normcase(os.path.realpath(ext_path(bundle)))
        if os.path.commonpath([bundle_real, output_real]) == bundle_real:
            print("OUTPUT_INSIDE_BUNDLE: choose a path outside the verified bundle", file=sys.stderr)
            return 2
    except ValueError:
        pass

    report = verify_bundle(bundle, manifest, args.require_native, args.expect_source_commit)
    parent = os.path.dirname(output)
    if parent:
        os.makedirs(ext_path(parent), exist_ok=True)
    with open(ext_path(output), "x", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(
        "PACKAGE_CHECK", "PASS" if report["passed"] else "FAIL",
        f"kind={report['bundleKind']} nativeRelease={report['nativeRelease']} "
        f"checks={len(report['checks'])} failures={len(report['failures'])} "
        f"warnings={len(report['warnings'])}",
    )
    for failure in report["failures"]:
        print("FAIL:", failure["name"], "-", failure["detail"])
    print("RESULT:", display_path(output))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
