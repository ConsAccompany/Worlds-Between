#!/usr/bin/env python3
"""Independent negative-contract check for exploration source-bank manifests.

The existing native-bank checker is executed unchanged.  The positive case runs
the real zexplore25 manifest.  Four negative cases copy the referenced assets
into an isolated fixture tree, mutate one contract surface, and require the
checker to refuse (nonzero exit).  The harness records the actual command,
exit code, stdout and stderr, verifies that the real referenced assets are
byte-identical before and after, and removes only verified fixture directories.

This is a technical source-bank check.  It does not approve art, infer
true-fluid motion, integrate runtime assets, or touch ledgers, Git or defaults.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import traceback
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT_SLUG = "rpg-2-star-ocean-the-second"
SUBJECT = "exploration-source"
VARIANT = "test-only-v01"
MARKER = ".lexplore-negative-contract-fixture"
DEFAULT_CHECKER = (
    ROOT
    / "tools"
    / "rpg-2-star-ocean-the-second_exploration-source_native-bank-check_test-only-v01_20261021-212850-493fd162.py"
)
REQUIRED_DIRECTIONS = {"south", "west", "north", "east"}


def win_long(path):
    """Return a Windows extended-length path; leave POSIX paths alone."""
    p = Path(path)
    if os.name != "nt":
        return p
    s = str(p)
    if s.startswith("\\\\?\\"):
        return Path(s)
    absolute = os.path.abspath(s)
    if absolute.startswith("\\\\"):
        return Path("\\\\?\\UNC\\" + absolute[2:])
    return Path("\\\\?\\" + absolute)


def ensure_dir(path):
    os.makedirs(str(win_long(path)), exist_ok=True)


def read_bytes(path):
    with open(str(win_long(path)), "rb") as handle:
        return handle.read()


def write_bytes(path, data):
    ensure_dir(Path(path).parent)
    with open(str(win_long(path)), "wb") as handle:
        handle.write(data)


def read_text(path):
    return read_bytes(path).decode("utf-8")


def write_text(path, text):
    write_bytes(path, text.encode("utf-8"))


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    try:
        with open(str(win_long(path)), "rb") as handle:
            digest = hashlib.sha256()
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
            return digest.hexdigest()
    except OSError as exc:
        return "ERROR:" + type(exc).__name__ + ":" + str(exc)


def path_is_file(path):
    try:
        return os.path.isfile(str(win_long(path)))
    except OSError:
        return False


def path_exists(path):
    try:
        return os.path.exists(str(win_long(path)))
    except OSError:
        return False


def list_dir(path):
    try:
        return os.listdir(str(win_long(path)))
    except OSError:
        return []


def is_within(child, parent):
    # abspath is lexical and does not touch the filesystem, so it is safe for
    # paths longer than MAX_PATH.  Fixture roots are created by this harness and
    # are never symlinks.
    child_abs = os.path.normcase(os.path.abspath(str(child)))
    parent_abs = os.path.normcase(os.path.abspath(str(parent)))
    return child_abs == parent_abs or child_abs.startswith(parent_abs + os.sep)


def display_path(path):
    p = Path(path)
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except (OSError, ValueError):
        return str(p)


def safe_rmtree(case_root, fixtures_root, run_tag):
    """Remove one fixture directory only after containment and marker checks."""
    case_root = Path(case_root)
    fixtures_root = Path(fixtures_root)
    case_abs = os.path.abspath(str(case_root))
    fixtures_abs = os.path.abspath(str(fixtures_root))
    record = {
        "target": case_abs,
        "fixturesRoot": fixtures_abs,
        "contained": False,
        "markerVerified": False,
        "removed": False,
    }
    if case_abs == fixtures_abs or not is_within(case_abs, fixtures_abs):
        raise RuntimeError("refusing recursive deletion outside verified fixture root")
    record["contained"] = True
    marker = case_root / MARKER
    if not path_is_file(marker):
        raise RuntimeError("refusing deletion without fixture marker")
    marker_value = read_text(marker).strip()
    if marker_value != run_tag:
        raise RuntimeError("refusing deletion with mismatched fixture marker")
    record["markerVerified"] = True
    shutil.rmtree(str(win_long(case_root)))
    record["removed"] = not path_exists(case_root)
    return record


def collect_manifest_files(value, found=None):
    """Collect every file-like path referenced anywhere in a manifest."""
    if found is None:
        found = set()
    if isinstance(value, dict):
        file_value = value.get("file")
        if isinstance(file_value, str):
            found.add(file_value)
        exact_source = value.get("exact_source")
        if isinstance(exact_source, str):
            found.add(exact_source)
        for child in value.values():
            collect_manifest_files(child, found)
    elif isinstance(value, list):
        for child in value:
            collect_manifest_files(child, found)
    return found


def read_entries(manifest):
    """Yield entries the existing checker actually opens from directions."""
    for bank in manifest["directions"].values():
        yield bank["static"]
        for entry in bank["idle"]:
            yield entry
        for entry in bank["walk"]:
            yield entry
        for bridge in bank["stop_bridges"].values():
            for entry in bridge:
                if isinstance(entry, dict) and "file" in entry:
                    yield entry
        yield bank["pxo"]
        yield bank["ora"]


def source_input_entries(manifest):
    for entry in manifest.get("source_inputs", {}).values():
        if isinstance(entry, dict) and "file" in entry:
            yield entry


def resolve_manifest_path(value):
    p = Path(value)
    if p.is_absolute():
        return p
    return ROOT / p


def snapshot_assets(manifest_path, checker_path):
    manifest_raw = read_bytes(manifest_path)
    manifest = json.loads(manifest_raw.decode("utf-8"))
    references = sorted(collect_manifest_files(manifest))
    files = {}
    missing = []
    for reference in references:
        path = resolve_manifest_path(reference)
        if path_is_file(path):
            files[reference] = sha256_file(path)
        else:
            files[reference] = "MISSING"
            missing.append(reference)
    payload = "\n".join(f"{key}={files[key]}" for key in sorted(files)).encode("utf-8")
    return {
        "referencedCount": len(references),
        "existingCount": len(references) - len(missing),
        "missing": missing,
        "aggregateSha256": sha256_bytes(payload),
        "files": files,
        "manifestSha256Raw": sha256_bytes(manifest_raw),
        "checkerSha256Raw": sha256_file(checker_path),
    }


def run_subprocess(command, timeout):
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return {
            "exitCode": completed.returncode,
            "timedOut": False,
            "stdout": completed.stdout or "",
            "stderr": completed.stderr or "",
            "elapsedSeconds": round(time.monotonic() - started, 3),
        }
    except subprocess.TimeoutExpired as exc:
        def to_text(value):
            if value is None:
                return ""
            if isinstance(value, bytes):
                return value.decode("utf-8", "replace")
            return value

        return {
            "exitCode": None,
            "timedOut": True,
            "stdout": to_text(exc.stdout),
            "stderr": to_text(exc.stderr),
            "elapsedSeconds": round(time.monotonic() - started, 3),
        }


def compact_native_result(out_dir):
    candidates = sorted(
        (
            Path(out_dir) / name
            for name in list_dir(out_dir)
            if "native-bank-proof" in name and name.endswith(".json")
        ),
        key=lambda item: item.name,
        reverse=True,
    )
    if not candidates:
        return None, None, None
    path = candidates[0]
    raw = read_bytes(path)
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {
            "path": str(path),
            "parseError": type(exc).__name__ + ": " + str(exc),
            "sha256Raw": sha256_bytes(raw),
        }, path, sha256_bytes(raw)
    checks = parsed.get("checks", [])
    failed = [check.get("check") for check in checks if not check.get("passed")]
    return {
        "path": str(path),
        "sha256Raw": sha256_bytes(raw),
        "passed": parsed.get("passed"),
        "checkCount": len(checks),
        "failedChecks": failed,
        "artApproved": parsed.get("artApproved"),
        "humanPlaytest": parsed.get("humanPlaytest"),
    }, path, sha256_bytes(raw)


def classify(run, expected, native_result):
    stdout = run["stdout"]
    stderr = run["stderr"]
    exit_code = run["exitCode"]
    native_lines = [line for line in stdout.splitlines() if line.startswith("NATIVE_BANK")]
    native_line = native_lines[0] if native_lines else None
    fail_lines = [line for line in stdout.splitlines() if line.startswith("FAIL ")]
    has_traceback = "Traceback (most recent call last)" in stderr
    proof_says_true = bool(native_line and re.match(r"NATIVE_BANK\s+True\b", native_line))
    proof_says_false = bool(native_line and re.match(r"NATIVE_BANK\s+False\b", native_line))
    if run["timedOut"]:
        kind = "timeout"
    elif exit_code == 0 and proof_says_true and native_result and native_result.get("passed") is True:
        kind = "accepted"
    elif exit_code == 0:
        kind = "accepted-without-proof"
    elif has_traceback:
        kind = "refused-exception"
    elif fail_lines or proof_says_false:
        kind = "refused-diagnostic"
    else:
        kind = "refused-nonzero"

    if expected == "accept":
        passed = kind == "accepted"
    else:
        passed = exit_code not in (0, None) and kind not in ("accepted", "accepted-without-proof")
    return {
        "kind": kind,
        "passed": passed,
        "nativeBankLine": native_line,
        "failLines": fail_lines,
        "traceback": has_traceback,
        "explicitDiagnostic": bool(fail_lines or has_traceback or native_line),
        "exceptionLine": (stderr.strip().splitlines()[-1] if has_traceback and stderr.strip() else None),
    }


def execute_case(name, expected, manifest_path, out_dir, checker_path, python_exe, timeout, mutation, fixture):
    ensure_dir(out_dir)
    command = [
        python_exe,
        "-X",
        "utf8",
        "-I",
        str(checker_path),
        str(manifest_path),
        "--out-dir",
        str(out_dir),
    ]
    run = run_subprocess(command, timeout)
    native_result, native_path, native_sha = compact_native_result(out_dir)
    verdict = classify(run, expected, native_result)
    return {
        "case": name,
        "expected": expected,
        "command": command,
        "commandDisplay": subprocess.list2cmdline(command),
        "cwd": str(ROOT),
        **run,
        "nativeResult": native_result,
        "nativeResultPath": str(native_path) if native_path else None,
        "nativeResultSha256Raw": native_sha,
        "classification": verdict,
        "refused": run["exitCode"] not in (0, None),
        "passed": verdict["passed"],
        "fixture": fixture,
        "mutation": mutation,
    }


def build_fixture(source_manifest_path, case_name, fixtures_root, run_tag):
    case_root = fixtures_root / (case_name + "-" + uuid.uuid4().hex[:8])
    ensure_dir(case_root / "files")
    write_text(case_root / MARKER, run_tag)
    data = json.loads(read_bytes(source_manifest_path).decode("utf-8"))
    originals = []
    for entry in [*source_input_entries(data), *read_entries(data)]:
        reference = entry.get("file")
        if isinstance(reference, str) and reference not in originals:
            originals.append(reference)
    mapping = {}
    inverse = {}
    missing = []
    for reference in originals:
        source = resolve_manifest_path(reference)
        if not source.is_file():
            missing.append(reference)
            continue
        suffix = Path(reference).suffix.lower() or ".bin"
        destination = case_root / "files" / (str(len(mapping)).zfill(4) + suffix)
        write_bytes(destination, read_bytes(source))
        mapping[reference] = str(destination)
        inverse[str(destination)] = reference
    for entry in [*source_input_entries(data), *read_entries(data)]:
        reference = entry.get("file")
        if reference in mapping:
            entry["file"] = mapping[reference]
        elif reference in missing:
            entry["file"] = str(case_root / "files" / ("missing-" + sha256_bytes(reference.encode("utf-8"))[:12]))
        exact_source = entry.get("exact_source")
        if isinstance(exact_source, str) and exact_source in mapping:
            entry["exact_source"] = mapping[exact_source]
    return {
        "caseRoot": case_root,
        "data": data,
        "mapping": mapping,
        "inverse": inverse,
        "missing": missing,
        "originals": originals,
    }


def finalize_fixture(fixture, mutation):
    case_root = fixture["caseRoot"]
    data = fixture["data"]
    manifest_path = case_root / "manifest.json"
    write_text(manifest_path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    for entry in read_entries(data):
        path = Path(entry["file"])
        if not path.is_absolute() or not is_within(path, case_root):
            raise RuntimeError("checker input was not redirected into fixture: " + str(path))
        if not path_is_file(path):
            raise RuntimeError("checker input missing in fixture: " + str(path))
    return {
        "caseRoot": case_root,
        "manifestPath": manifest_path,
        "manifestSha256Raw": sha256_file(manifest_path),
        "filesCopied": len(fixture["mapping"]),
        "filesMissing": fixture["missing"],
        "originals": len(fixture["originals"]),
        "mutation": mutation,
    }


def mutate_png_hash(data, inverse, case_root):
    entry = data["directions"]["south"]["idle"][1]
    path = Path(entry["file"])
    before = read_bytes(path)
    after = before + b"\x00"
    write_bytes(path, after)
    return {
        "type": "altered-png-bytes-hash",
        "entry": "directions.south.idle[1]",
        "targetOriginal": inverse.get(str(path)),
        "bytesBefore": len(before),
        "bytesAfter": len(after),
        "originalSha256": sha256_bytes(before),
        "mutatedSha256": sha256_bytes(after),
        "declaredSha256Updated": False,
        "declaredSha256": entry.get("sha256"),
    }


def mutate_missing_direction(data, inverse, case_root):
    removed = data["directions"].pop("west")
    return {
        "type": "missing-direction",
        "removedDirection": "west",
        "remainingDirections": sorted(data["directions"]),
        "removedDirectionFileReferences": len(collect_manifest_files(removed)),
    }


def mutate_truncated_pxo(data, inverse, case_root):
    entry = data["directions"]["south"]["pxo"]
    path = Path(entry["file"])
    before = read_bytes(path)
    after = before[:64]
    write_bytes(path, after)
    entry["sha256"] = sha256_bytes(after)
    return {
        "type": "truncated-pxo-archive",
        "entry": "directions.south.pxo",
        "targetOriginal": inverse.get(str(path)),
        "bytesBefore": len(before),
        "bytesAfter": len(after),
        "originalSha256": sha256_bytes(before),
        "mutatedSha256": sha256_bytes(after),
        "declaredSha256Updated": True,
    }


def mutate_ora_merged(data, inverse, case_root):
    from PIL import Image

    entry = data["directions"]["south"]["ora"]
    path = Path(entry["file"])
    before = read_bytes(path)
    with zipfile.ZipFile(io.BytesIO(before)) as archive:
        original_stack = archive.read("stack.xml")
        original_merged = archive.read("mergedimage.png")
        image = Image.open(io.BytesIO(original_merged)).convert("RGBA")
        replacement = Image.new("RGBA", image.size, (0, 0, 0, 0))
        buffer = io.BytesIO()
        replacement.save(buffer, format="PNG")
        replacement_png = buffer.getvalue()
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as rebuilt:
            for info in archive.infolist():
                payload = replacement_png if info.filename == "mergedimage.png" else archive.read(info.filename)
                rebuilt.writestr(info, payload)
        after = output.getvalue()
    write_bytes(path, after)
    entry["sha256"] = sha256_bytes(after)
    with zipfile.ZipFile(io.BytesIO(after)) as check:
        stack_unchanged = check.read("stack.xml") == original_stack
        merged_changed = check.read("mergedimage.png") != original_merged
    return {
        "type": "altered-ora-merged-composite",
        "entry": "directions.south.ora",
        "targetOriginal": inverse.get(str(path)),
        "bytesBefore": len(before),
        "bytesAfter": len(after),
        "originalSha256": sha256_bytes(before),
        "mutatedSha256": sha256_bytes(after),
        "originalMergedSha256": sha256_bytes(original_merged),
        "mutatedMergedSha256": sha256_bytes(replacement_png),
        "stackXmlUnchanged": stack_unchanged,
        "mergedCompositeChanged": merged_changed,
        "declaredSha256Updated": True,
    }


def long_path_probe(fixtures_root, run_tag):
    if os.name != "nt":
        return {"status": "skipped-non-windows"}
    probe_root = fixtures_root / ("long-path-probe-" + uuid.uuid4().hex[:8])
    ensure_dir(probe_root)
    write_text(probe_root / MARKER, run_tag)
    segments = ["d" * 70, "e" * 70, "f" * 70]
    probe_file = probe_root.joinpath(*segments) / "probe.txt"
    payload = "long-path-ok-" + run_tag
    write_text(probe_file, payload)
    record = {
        "status": "ok",
        "path": str(probe_file),
        "pathLength": len(str(probe_file)),
        "wrote": True,
        "readBack": read_text(probe_file) == payload,
    }
    record["cleanup"] = safe_rmtree(probe_root, fixtures_root, run_tag)
    return record


def make_note(result):
    lines = [
        "# Exploration source negative-contract check - short QA note",
        "",
        f"- Run tag: `{result['runTag']}`",
        f"- Checker: `{display_path(result['checker']['path'])}`",
        f"- Checker SHA-256: `{result['checker']['sha256']}`",
        f"- Manifest: `{display_path(result['manifest']['path'])}`",
        f"- Manifest SHA-256: `{result['manifest']['sha256']}`",
        f"- Python: `{result['python']['executable']}` ({result['python']['version']})",
        f"- Timeout per checker run: {result['timeoutSeconds']} s",
        "",
        "## Safety guard",
        "",
        f"- Referenced real assets: {result['guard']['before']['referencedCount']} "
        f"({result['guard']['before']['existingCount']} present, "
        f"{len(result['guard']['before']['missing'])} missing).",
        f"- Aggregate SHA-256 before: `{result['guard']['before']['aggregateSha256']}`",
        f"- Aggregate SHA-256 after: `{result['guard']['after']['aggregateSha256']}`",
        f"- Real referenced assets unchanged: **{result['guard']['unchanged']}**.",
        f"- Fixture cleanup verified under marker-checked temp roots: **{result['cleanup']['allRemoved']}**.",
        f"- Long-path probe: {result['longPathProbe'].get('status')} "
        f"(path length {result['longPathProbe'].get('pathLength')}, "
        f"readBack={result['longPathProbe'].get('readBack')}, "
        f"removed={result['longPathProbe'].get('cleanup', {}).get('removed')}).",
        "",
        "## Actual checker runs",
        "",
        "| Case | Expected | Exit | Timed out | Classification | Passed |",
        "|---|---|---:|---|---|---|",
    ]
    for case in [result["positive"], *result["negatives"]]:
        lines.append(
            f"| {case['case']} | {case['expected']} | {case.get('exitCode')} | "
            f"{case.get('timedOut')} | {case['classification']['kind']} | {case['passed']} |"
        )
    lines.extend(["", "## Case detail", ""])
    for case in [result["positive"], *result["negatives"]]:
        lines.append(f"### {case['case']}")
        lines.append("")
        lines.append(f"- Command: `{case['commandDisplay']}`")
        lines.append(f"- Exit: `{case.get('exitCode')}`; elapsed: {case.get('elapsedSeconds')} s")
        native = case.get("nativeResult") or {}
        lines.append(
            f"- Checker proof: passed={native.get('passed')}; checks={native.get('checkCount')}; "
            f"failed={len(native.get('failedChecks', []))}"
        )
        if case["classification"].get("nativeBankLine"):
            lines.append(f"- NATIVE_BANK: `{case['classification']['nativeBankLine']}`")
        if case["classification"].get("failLines"):
            for line in case["classification"]["failLines"][:6]:
                lines.append(f"- Diagnostic: `{line}`")
        if case["classification"].get("exceptionLine"):
            lines.append(f"- Exception: `{case['classification']['exceptionLine']}`")
        if case.get("mutation"):
            lines.append(f"- Mutation: `{json.dumps(case['mutation'], ensure_ascii=False)}`")
        if case.get("fixture"):
            lines.append(
                f"- Fixture files copied: {case['fixture'].get('filesCopied')}; "
                f"cleanup removed: {case.get('cleanup', {}).get('removed')}"
            )
        lines.append(
            f"- Full stdout/stderr preserved in the result JSON "
            f"({len(case.get('stdout', ''))} / {len(case.get('stderr', ''))} chars)."
        )
        lines.append("")
    lines.extend(
        [
            "## Concrete checker blind spots observed",
            "",
            "- `source_inputs` and `exact_source` provenance references are never opened or hash-checked by "
            "the checker. A manifest can cite missing or wrong source PNG/ORA files and still pass the "
            "direction-bank checks.",
            "- Archive parse errors are uncaught. A truncated PXO exits nonzero with a traceback and writes "
            "no proof JSON; a consumer must treat that as refusal and must not require a result file.",
            "- The checker validates the four-direction set and per-frame geometry, but does not "
            "schema-validate bank lengths, `duration_ms`, `walk_model`, or that `stop_bridges` has exactly "
            "one key per walk phase. Missing/extra keys can crash or go unchecked.",
            "",
            "## Scope and limitations",
            "",
            "- Positive fixture: existing `zexplore25` manifest. This proves that bank satisfies this "
            "checker; it is not art acceptance.",
            "- Liang Xu exploration source package: **not checked**. No Liang Xu exploration source "
            "manifest/package was present at run time, so no Liang acceptance claim is made.",
            "- No art generation, runtime integration, accounts, ledger, Git index/commit, or default "
            "changes. No true-fluidity or art-acceptance inference.",
            f"- Overall harness result: **{result['summary']['passed']}**.",
            "",
        ]
    )
    return "\n".join(lines)


def resolve_cli_path(value, prefer_root=False):
    p = Path(value)
    if p.is_absolute():
        return p.resolve()
    root_candidate = (ROOT / p).resolve()
    cwd_candidate = (Path.cwd() / p).resolve()
    if prefer_root:
        return root_candidate
    if cwd_candidate.exists() or not root_candidate.exists():
        return cwd_candidate
    return root_candidate


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--checker", default=str(DEFAULT_CHECKER))
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--keep-fixtures", action="store_true")
    args = parser.parse_args()

    started_utc = datetime.now(timezone.utc)
    run_tag = started_utc.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    manifest_path = resolve_cli_path(args.manifest)
    checker_path = resolve_cli_path(args.checker, prefer_root=True)
    out_dir = resolve_cli_path(args.out_dir)
    python_exe = str(Path(args.python).resolve())

    if not manifest_path.is_file():
        print("HARNESS_ERROR manifest not found: " + str(manifest_path), file=sys.stderr)
        return 2
    if not checker_path.is_file():
        print("HARNESS_ERROR checker not found: " + str(checker_path), file=sys.stderr)
        return 2

    ensure_dir(out_dir)
    run_root = out_dir / ("run-" + run_tag)
    fixtures_root = run_root / "fixtures"
    positive_out = run_root / "positive-native"
    ensure_dir(fixtures_root)
    ensure_dir(positive_out)

    before = snapshot_assets(manifest_path, checker_path)
    result = {
        "project": PROJECT_SLUG,
        "subject": SUBJECT,
        "purpose": "negative-contract-check",
        "variant": VARIANT,
        "runTag": run_tag,
        "startedUtc": started_utc.isoformat(),
        "tool": {"path": str(Path(__file__).resolve()), "sha256Raw": sha256_file(__file__)},
        "checker": {"path": str(checker_path), "sha256": sha256_file(checker_path)},
        "manifest": {"path": str(manifest_path), "sha256": sha256_file(manifest_path)},
        "python": {"executable": python_exe, "version": platform.python_version()},
        "timeoutSeconds": args.timeout,
        "guard": {"before": before},
        "positive": None,
        "negatives": [],
        "longPathProbe": None,
        "cleanup": {},
        "summary": {},
        "scope": {
            "liangXuChecked": False,
            "liangXuReason": "No Liang Xu exploration source manifest/package present at run time.",
            "artApproved": False,
            "trueFluidity": False,
            "runtimeIntegrated": False,
            "ledgerOrGitChanges": False,
            "defaultChanges": False,
        },
    }

    positive = execute_case(
        "positive-zexplore25",
        "accept",
        manifest_path,
        positive_out,
        checker_path,
        python_exe,
        args.timeout,
        mutation=None,
        fixture={"kind": "original-manifest", "path": str(manifest_path)},
    )
    result["positive"] = positive

    cases = [
        ("negative-altered-png-hash", "refuse", mutate_png_hash),
        ("negative-missing-direction", "refuse", mutate_missing_direction),
        ("negative-truncated-pxo", "refuse", mutate_truncated_pxo),
        ("negative-altered-ora-merged", "refuse", mutate_ora_merged),
    ]
    for case_name, expected, mutation_fn in cases:
        case_root = None
        try:
            fixture = build_fixture(manifest_path, case_name, fixtures_root, run_tag)
            case_root = fixture["caseRoot"]
            mutation = mutation_fn(fixture["data"], fixture["inverse"], case_root)
            fixture_meta = finalize_fixture(fixture, mutation)
            case_out = case_root / "checker-out"
            case = execute_case(
                case_name,
                expected,
                fixture_meta["manifestPath"],
                case_out,
                checker_path,
                python_exe,
                args.timeout,
                mutation=mutation,
                fixture={
                    "kind": "isolated-copy",
                    "caseRoot": str(case_root),
                    "manifestPath": str(fixture_meta["manifestPath"]),
                    "manifestSha256Raw": fixture_meta["manifestSha256Raw"],
                    "filesCopied": fixture_meta["filesCopied"],
                    "filesMissing": fixture_meta["filesMissing"],
                },
            )
            if args.keep_fixtures:
                case["cleanup"] = {"kept": True, "removed": False, "target": str(case_root)}
            else:
                case["cleanup"] = safe_rmtree(case_root, fixtures_root, run_tag)
            result["negatives"].append(case)
        except Exception:
            error = traceback.format_exc()
            cleanup = {"removed": False}
            if case_root is not None and not args.keep_fixtures:
                try:
                    cleanup = safe_rmtree(case_root, fixtures_root, run_tag)
                except Exception:
                    cleanup = {"removed": False, "error": traceback.format_exc()}
            result["negatives"].append(
                {
                    "case": case_name,
                    "expected": expected,
                    "passed": False,
                    "harnessError": error,
                    "cleanup": cleanup,
                    "classification": {"kind": "harness-error", "passed": False},
                }
            )

    result["longPathProbe"] = long_path_probe(fixtures_root, run_tag)
    result["guard"]["after"] = snapshot_assets(manifest_path, checker_path)
    before_files = result["guard"]["before"]["files"]
    after_files = result["guard"]["after"]["files"]
    changed = {}
    for key in sorted(set(before_files) | set(after_files)):
        if before_files.get(key) != after_files.get(key):
            changed[key] = {"before": before_files.get(key), "after": after_files.get(key)}
    result["guard"]["changed"] = changed
    result["guard"]["unchanged"] = (
        not changed
        and result["guard"]["before"]["aggregateSha256"] == result["guard"]["after"]["aggregateSha256"]
        and result["guard"]["before"]["manifestSha256Raw"] == result["guard"]["after"]["manifestSha256Raw"]
        and result["guard"]["before"]["checkerSha256Raw"] == result["guard"]["after"]["checkerSha256Raw"]
    )

    remaining_fixtures = sorted(list_dir(fixtures_root)) if path_exists(fixtures_root) else []
    result["cleanup"] = {
        "allRemoved": all(
            case.get("cleanup", {}).get("removed") for case in result["negatives"]
        )
        and result["longPathProbe"].get("cleanup", {}).get("removed", False),
        "remainingFixtures": remaining_fixtures,
        "fixturesRoot": str(fixtures_root),
        "keepFixtures": args.keep_fixtures,
    }
    if not remaining_fixtures and path_exists(fixtures_root):
        try:
            os.rmdir(str(win_long(fixtures_root)))
            result["cleanup"]["fixturesRootRemoved"] = True
        except OSError:
            result["cleanup"]["fixturesRootRemoved"] = False

    result["summary"] = {
        "passed": bool(
            positive["passed"]
            and all(case.get("passed") for case in result["negatives"])
            and result["guard"]["unchanged"]
            and result["cleanup"]["allRemoved"]
            and result["longPathProbe"].get("status") in ("ok", "skipped-non-windows")
        ),
        "positiveAccepted": positive["passed"],
        "negativeCount": len(result["negatives"]),
        "negativesRefused": sum(1 for case in result["negatives"] if case.get("passed")),
        "realAssetsUnchanged": result["guard"]["unchanged"],
        "fixtureCleanupVerified": result["cleanup"]["allRemoved"],
        "liangXuChecked": False,
        "artApproved": False,
    }
    result["finishedUtc"] = datetime.now(timezone.utc).isoformat()

    stamp = run_tag
    result_path = run_root / (
        PROJECT_SLUG + "_" + SUBJECT + "_negative-contract-result_" + VARIANT + "_" + stamp + ".json"
    )
    note_path = run_root / (
        PROJECT_SLUG + "_" + SUBJECT + "_qa-note_" + VARIANT + "_" + stamp + ".md"
    )
    write_text(result_path, json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    write_text(note_path, make_note(result) + "\n")

    for case in [result["positive"], *result["negatives"]]:
        print(
            "CASE",
            case["case"],
            "expected=" + str(case.get("expected")),
            "exit=" + str(case.get("exitCode")),
            "kind=" + str(case.get("classification", {}).get("kind")),
            "passed=" + str(case.get("passed")),
        )
    print(
        "NEGATIVE_CONTRACT",
        result["summary"]["passed"],
        "positive=" + str(result["summary"]["positiveAccepted"]),
        "negatives=" + str(result["summary"]["negativesRefused"]) + "/" + str(result["summary"]["negativeCount"]),
        "guard_unchanged=" + str(result["guard"]["unchanged"]),
        "cleanup=" + str(result["cleanup"]["allRemoved"]),
        "liang_checked=False",
        display_path(result_path),
    )
    return 0 if result["summary"]["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
