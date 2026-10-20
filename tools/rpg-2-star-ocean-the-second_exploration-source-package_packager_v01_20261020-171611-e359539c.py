#!/usr/bin/env python3
"""Lossless exploration PNG-source packager for the opt-in exploration sprite-set pilot.

Reads the producer source contract ``worlds-between.exploration-source.v1`` and publishes a
runtime package that the existing ``game/scripts/exploration_sprite_set_pilot.gd`` loader
already understands:

  <out>/<set>.json          schema worlds-between.exploration-sprite-set.v1
  <out>/<registry>.json     schema worlds-between.exploration-sprite-set-registry.v1
  <out>/<provenance>.json   source hashes, byte-copy mapping and output hashes
  <out>/png/<frame>.png     exact byte copies of the validated source PNGs

The source contract is fixed for the current heroine-capability path: actor_id
``protagonist-female``, density 2, frame_size [80,112], pivot [40,104], exactly the actions
idle/walk and exactly the directions south/west/north/east. idle clips have 1..16 poses
and walk clips 2..16 poses; every duration_ms is an integer 40..2000. Referenced files are
relative to the source manifest, must stay inside its folder, must not use absolute paths,
traversal, symlinks/junctions or duplicate filenames, and must match the global lowercase
``project_subject_purpose_variant_YYYYMMDD-HHMMSS-uniqueid.png`` rule.

Every PNG must be an 80x112 8-bit RGBA PNG with hard 0/255 alpha, a fully transparent
border, no non-zero alpha at or below row 104, and (idle) exactly 96 source px of body whose
last opaque row is 103. Walk bodies may not exceed the loader's 48 logical px limit. No
image is edited, requantized, resampled or re-encoded: the validated source bytes are
written unchanged.

Usage:
  python -I <this> --source <manifest.json> --out <new-empty-destination> [--repo-root <root>]

``--out`` must be new, or an existing empty directory. Existing files are never
overwritten. Validation happens before staging; publication is a single directory rename,
so an invalid source leaves no partial usable package. ``--repo-root`` resolves relative
arguments against that root and requires both source and output to remain inside it.
No network access is used.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import io
import json
import os
import re
import secrets
import shutil
import struct
import sys
import traceback
from pathlib import Path

try:
    from PIL import Image
except Exception:  # pragma: no cover - reported as a normal refusal below
    Image = None

SCHEMA_SOURCE = "worlds-between.exploration-source.v1"
SCHEMA_SET = "worlds-between.exploration-sprite-set.v1"
SCHEMA_REGISTRY = "worlds-between.exploration-sprite-set-registry.v1"
SCHEMA_PROVENANCE = "worlds-between.exploration-source-package-provenance.v1"
ACTOR = "protagonist-female"
SUBJECT = "hero-female"
DENSITY = 2
FRAME_W = 80
FRAME_H = 112
PIVOT_X = 40
PIVOT_Y = 104
DIRECTIONS = ("south", "west", "north", "east")
ACTIONS = ("idle", "walk")
MIN_FRAMES = {"idle": 1, "walk": 2}
MAX_FRAMES = 16
MIN_DURATION_MS = 40
MAX_DURATION_MS = 2000
BODY_SOURCE_PX = 96
MAX_BODY_SOURCE_PX = 97
LAST_OPAQUE_ROW = PIVOT_Y - 1
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PROJECT_SLUG = "rpg-2-star-ocean-the-second"
NAME_RE = re.compile(
    r"^(?P<project>[a-z0-9][a-z0-9-]*)_"
    r"(?P<subject>[a-z0-9][a-z0-9-]*)_"
    r"(?P<purpose>[a-z0-9][a-z0-9-]*)_"
    r"(?P<variant>[a-z0-9][a-z0-9-]*)_"
    r"(?P<stamp>\d{8}-\d{6})-"
    r"(?P<uid>[a-z0-9]{4,32})\.png$"
)
DRIVE_RE = re.compile(r"^[a-zA-Z]:")
RESERVED = {"con", "prn", "aux", "nul"} | {f"com{i}" for i in range(1, 10)} | {f"lpt{i}" for i in range(1, 10)}
PNG_DIR = "png"


class Refusal(Exception):
    """A checked refusal with a list of concrete reasons."""

    def __init__(self, errors, kind="invalid-source"):
        self.errors = [str(error) for error in errors]
        self.kind = kind
        super().__init__("; ".join(self.errors))


# ---------------------------------------------------------------------------
# Filesystem helpers (explicit UTF-8, extended-length paths when needed)
# ---------------------------------------------------------------------------


def _fs(path):
    text = os.path.abspath(os.fspath(path))
    if os.name == "nt" and len(text) >= 248 and not text.startswith("\\\\?\\"):
        return "\\\\?\\" + text
    return text


def _exists(path):
    try:
        return os.path.exists(_fs(path))
    except OSError:
        return False


def _is_file(path):
    try:
        return os.path.isfile(_fs(path))
    except OSError:
        return False


def _is_dir(path):
    try:
        return os.path.isdir(_fs(path))
    except OSError:
        return False


def _link_kind(path):
    """Return 'symlink'/'junction' for a reparse-point path, else ''."""
    try:
        if os.path.islink(_fs(path)):
            return "symlink"
    except OSError:
        pass
    try:
        if Path(_fs(path)).is_junction():
            return "junction"
    except (OSError, AttributeError):
        pass
    return ""


def _read_bytes(path):
    with open(_fs(path), "rb") as handle:
        return handle.read()


def _write_new(path, data):
    os.makedirs(_fs(os.path.dirname(os.fspath(path))), exist_ok=True)
    with open(_fs(path), "xb") as handle:
        handle.write(data)


def _mkdir(path):
    os.makedirs(_fs(path), exist_ok=False)


def _new_stage_dir(parent):
    # Do not use tempfile.mkdtemp here: its Windows directory ACL interacts badly with the
    # workspace sandbox (a following mkdir under the new directory is denied). A plain mkdir
    # with an exclusive generated name is equivalent and works in the same directory.
    for _attempt in range(100):
        candidate = Path(parent) / (".exp-pack08-stage-" + secrets.token_hex(6))
        try:
            os.mkdir(_fs(candidate))
            return candidate
        except FileExistsError:
            continue
    raise RuntimeError("could not create a unique package staging directory")


def _rmtree(path):
    try:
        shutil.rmtree(_fs(path))
    except FileNotFoundError:
        pass


def _norm_key(path):
    return os.path.normcase(os.path.realpath(os.path.abspath(os.fspath(path))))


def _inside(child, parent):
    child_key = _norm_key(child)
    parent_key = _norm_key(parent)
    try:
        return os.path.commonpath([child_key, parent_key]) == parent_key
    except ValueError:
        return False


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path):
    digest = hashlib.sha256()
    size = 0
    with open(_fs(path), "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def _json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _display(path):
    return os.path.abspath(os.fspath(path)).replace("\\", "/")


def _repo_display(path, repo):
    if repo is not None:
        try:
            return Path(os.path.realpath(path)).relative_to(Path(os.path.realpath(repo))).as_posix()
        except ValueError:
            pass
    return _display(path)


# ---------------------------------------------------------------------------
# Strict JSON and path checks
# ---------------------------------------------------------------------------


class _DuplicateKey(ValueError):
    pass


def _pairs_hook(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise _DuplicateKey(f"duplicate object key {key!r}")
        out[key] = value
    return out


def _reject_constant(text):
    raise ValueError(f"non-finite JSON number {text}")


def _parse_json(raw, label):
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise Refusal([f"{label}: not valid UTF-8 ({exc})"])
    try:
        data = json.loads(text, object_pairs_hook=_pairs_hook, parse_constant=_reject_constant)
    except (json.JSONDecodeError, _DuplicateKey, ValueError) as exc:
        raise Refusal([f"{label}: invalid JSON ({exc})"])
    return data


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _relative_parts(value, label, errors, require_png):
    if not isinstance(value, str):
        errors.append(f"{label}: file must be a string")
        return None
    if value == "" or value.strip() == "":
        errors.append(f"{label}: file path is empty")
        return None
    if "\x00" in value:
        errors.append(f"{label}: file path contains NUL")
        return None
    normalized = value.replace("\\", "/")
    if normalized.startswith("/") or normalized.startswith("//") or DRIVE_RE.match(normalized):
        errors.append(f"{label}: absolute file paths are not allowed: {value!r}")
        return None
    parts = normalized.split("/")
    for part in parts:
        if part in ("", ".", ".."):
            errors.append(f"{label}: traversal or empty path component in {value!r}")
            return None
        if ":" in part:
            errors.append(f"{label}: ':' is not allowed in a path component: {value!r}")
            return None
        if part.endswith(" ") or part.endswith("."):
            errors.append(f"{label}: trailing space/dot path component is not allowed: {value!r}")
            return None
        if part.split(".", 1)[0].lower() in RESERVED:
            errors.append(f"{label}: reserved Windows device name in {value!r}")
            return None
        if len(part.encode("utf-8")) > 255:
            errors.append(f"{label}: path component is longer than 255 UTF-8 bytes")
            return None
    if require_png and not parts[-1].endswith(".png"):
        errors.append(f"{label}: frame files must end in .png: {value!r}")
        return None
    return parts


def _resolve_inside(base, value, label, errors, require_png):
    parts = _relative_parts(value, label, errors, require_png)
    if parts is None:
        return None
    current = Path(base)
    for part in parts:
        current = current / part
        if _exists(current):
            kind = _link_kind(current)
            if kind:
                errors.append(f"{label}: {kind} path component is not allowed: {value!r}")
                return None
    if not _exists(current):
        errors.append(f"{label}: file does not exist: {value!r}")
        return None
    if not _is_file(current):
        errors.append(f"{label}: not a regular file: {value!r}")
        return None
    resolved = Path(os.path.realpath(current))
    if not _inside(resolved, base):
        errors.append(f"{label}: resolved path escapes the manifest folder: {value!r}")
        return None
    return resolved


# ---------------------------------------------------------------------------
# PNG validation
# ---------------------------------------------------------------------------


def _analyze_png(data, label, action):
    """Validate one PNG entirely in memory; return (info, errors). Never re-encodes."""
    errors = []
    info = {
        "width": None,
        "height": None,
        "bit_depth": None,
        "color_type": None,
        "mode": None,
        "body_height": None,
        "top_opaque_row": None,
        "last_opaque_row": None,
    }
    if not data.startswith(PNG_SIGNATURE):
        return info, [f"{label}: not a PNG (bad signature)"]
    if len(data) < 33:
        return info, [f"{label}: truncated PNG"]
    length = int.from_bytes(data[8:12], "big")
    chunk_type = data[12:16]
    if chunk_type != b"IHDR" or length != 13:
        return info, [f"{label}: first PNG chunk is not a 13-byte IHDR"]
    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
        ">IIBBBBB", data[16:29]
    )
    info.update(width=width, height=height, bit_depth=bit_depth, color_type=color_type)
    if (width, height) != (FRAME_W, FRAME_H):
        errors.append(f"{label}: PNG is {width}x{height}, not {FRAME_W}x{FRAME_H}")
    if bit_depth != 8:
        errors.append(f"{label}: PNG bit depth is {bit_depth}, not 8")
    if color_type != 6:
        errors.append(f"{label}: PNG color type is {color_type}, not 6 (RGBA)")
    if compression != 0 or filter_method != 0:
        errors.append(f"{label}: unsupported PNG compression/filter method")
    if interlace != 0:
        errors.append(f"{label}: interlaced PNG is not accepted")
    if Image is None:
        return info, errors + [f"{label}: Pillow is required to validate PNG pixels"]
    try:
        with Image.open(io.BytesIO(data)) as probe:
            if probe.format != "PNG":
                errors.append(f"{label}: decoder did not identify a PNG")
            probe.verify()
        with Image.open(io.BytesIO(data)) as image:
            if getattr(image, "n_frames", 1) != 1:
                errors.append(f"{label}: animated/multi-frame PNG is not accepted")
            if image.mode != "RGBA":
                errors.append(f"{label}: decoded mode is {image.mode}, not RGBA")
            if image.size != (FRAME_W, FRAME_H):
                errors.append(f"{label}: decoded size is {image.size}, not {(FRAME_W, FRAME_H)}")
            image.load()
            alpha = image.getchannel("A")
            values = alpha.tobytes()
    except Exception as exc:
        return info, errors + [f"{label}: PNG decode failed ({type(exc).__name__}: {exc})"]

    if len(values) != FRAME_W * FRAME_H:
        return info, errors + [f"{label}: alpha plane has {len(values)} pixels, expected {FRAME_W * FRAME_H}"]

    min_x, min_y, max_x, max_y = FRAME_W, FRAME_H, -1, -1
    partial = 0
    border = 0
    below_floor = 0
    for index, alpha_value in enumerate(values):
        if alpha_value == 0:
            continue
        x = index % FRAME_W
        y = index // FRAME_W
        if alpha_value != 255:
            partial += 1
        if x == 0 or y == 0 or x == FRAME_W - 1 or y == FRAME_H - 1:
            border += 1
        if y >= PIVOT_Y:
            below_floor += 1
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x)
        max_y = max(max_y, y)

    if partial:
        errors.append(f"{label}: {partial} partial-alpha texel(s); alpha must be 0 or 255")
    if border:
        errors.append(f"{label}: {border} non-transparent texel(s) on the image border")
    if below_floor:
        errors.append(f"{label}: {below_floor} non-transparent texel(s) at y >= {PIVOT_Y}")
    if max_y < 0:
        errors.append(f"{label}: frame is empty")
        return info, errors

    body_height = max_y - min_y + 1
    info.update(body_height=body_height, top_opaque_row=min_y, last_opaque_row=max_y)
    if body_height > MAX_BODY_SOURCE_PX:
        errors.append(
            f"{label}: body is {body_height} source px, taller than {MAX_BODY_SOURCE_PX} "
            f"(48 logical px at density {DENSITY})"
        )
    if action == "idle":
        if max_y != LAST_OPAQUE_ROW:
            errors.append(f"{label}: idle soles end on row {max_y}, not {LAST_OPAQUE_ROW}")
        if body_height != BODY_SOURCE_PX:
            errors.append(
                f"{label}: idle body is {body_height} source px, not exactly {BODY_SOURCE_PX} "
                f"(48 logical px)"
            )
    return info, errors


# ---------------------------------------------------------------------------
# Source contract
# ---------------------------------------------------------------------------


def _resolve_arguments(args):
    errors = []
    cwd = Path.cwd()
    repo = None
    if args.repo_root:
        candidate = Path(args.repo_root)
        if not candidate.is_absolute():
            candidate = cwd / candidate
        candidate = Path(os.path.abspath(candidate))
        if not _exists(candidate) or not _is_dir(candidate):
            raise Refusal([f"--repo-root is not an existing directory: {args.repo_root}"], "bad-arguments")
        if _link_kind(candidate):
            raise Refusal([f"--repo-root is a {_link_kind(candidate)}: {args.repo_root}"], "bad-arguments")
        repo = Path(os.path.realpath(candidate))

    def resolve_arg(value):
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = (repo or cwd) / candidate
        return Path(os.path.abspath(candidate))

    source = resolve_arg(args.source)
    out = resolve_arg(args.out)

    if not _exists(source):
        errors.append(f"--source does not exist: {args.source}")
    elif _link_kind(source):
        errors.append(f"--source is a {_link_kind(source)}: {args.source}")
    elif not _is_file(source):
        errors.append(f"--source is not a regular file: {args.source}")
    if repo is not None and _exists(source) and not _inside(os.path.realpath(source), repo):
        errors.append(f"--source is outside --repo-root: {_display(source)}")
    if repo is not None and not _inside(out, repo):
        errors.append(f"--out is outside --repo-root: {_display(out)}")
    if _norm_key(source) == _norm_key(out):
        errors.append("--source and --out must be different paths")
    if errors:
        raise Refusal(errors, "bad-arguments")

    source = Path(os.path.realpath(source))
    return {"repo": repo, "source": source, "out": out}


def _read_source_manifest(ctx):
    source_path = ctx["source"]
    raw = _read_bytes(source_path)
    label = f"source manifest {_display(source_path)}"
    data = _parse_json(raw, label)
    errors = []
    if not isinstance(data, dict):
        raise Refusal([f"{label}: top-level JSON value must be an object"])
    if data.get("schema") != SCHEMA_SOURCE:
        errors.append(f"{label}: schema must be {SCHEMA_SOURCE!r}")
    if data.get("actor_id") != ACTOR:
        errors.append(f"{label}: actor_id must be {ACTOR!r}")
    if data.get("density") != DENSITY or not _is_int(data.get("density")):
        errors.append(f"{label}: density must be the integer {DENSITY}")
    if data.get("frame_size") != [FRAME_W, FRAME_H]:
        errors.append(f"{label}: frame_size must be [{FRAME_W}, {FRAME_H}]")
    if data.get("pivot") != [PIVOT_X, PIVOT_Y]:
        errors.append(f"{label}: pivot must be [{PIVOT_X}, {PIVOT_Y}]")

    actions = data.get("actions")
    clips = {}
    if not isinstance(actions, dict):
        errors.append(f"{label}: actions must be an object")
    else:
        missing_actions = [action for action in ACTIONS if action not in actions]
        extra_actions = sorted(str(key) for key in actions.keys() if key not in ACTIONS)
        if missing_actions:
            errors.append(f"{label}: actions is missing {missing_actions}")
        if extra_actions:
            errors.append(f"{label}: actions has non-contract key(s) {extra_actions}")
        for action in ACTIONS:
            if action not in actions:
                continue
            by_direction = actions[action]
            clips[action] = {}
            if not isinstance(by_direction, dict):
                errors.append(f"{label}: actions.{action} must be an object")
                continue
            missing_dirs = [direction for direction in DIRECTIONS if direction not in by_direction]
            extra_dirs = sorted(str(key) for key in by_direction.keys() if key not in DIRECTIONS)
            if missing_dirs:
                errors.append(f"{label}: actions.{action} is missing direction(s) {missing_dirs}")
            if extra_dirs:
                errors.append(f"{label}: actions.{action} has non-contract direction(s) {extra_dirs}")
            for direction in DIRECTIONS:
                if direction not in by_direction:
                    continue
                frame_list = by_direction[direction]
                if not isinstance(frame_list, list):
                    errors.append(f"{label}: actions.{action}.{direction} must be an array")
                    continue
                count = len(frame_list)
                if count < MIN_FRAMES[action] or count > MAX_FRAMES:
                    errors.append(
                        f"{label}: actions.{action}.{direction} needs {MIN_FRAMES[action]}..{MAX_FRAMES} "
                        f"poses, got {count}"
                    )
                clips[action][direction] = frame_list

    source_dir = source_path.parent
    seen_paths = {}
    seen_names = {}
    frames = []
    for action in ACTIONS:
        for direction in DIRECTIONS:
            entries = (clips.get(action) or {}).get(direction)
            if entries is None:
                continue
            for index, entry in enumerate(entries):
                where = f"actions.{action}.{direction}[{index}]"
                if not isinstance(entry, dict):
                    errors.append(f"{label}: {where} must be an object")
                    continue
                file_value = entry.get("file")
                duration = entry.get("duration_ms")
                if not isinstance(file_value, str):
                    errors.append(f"{label}: {where}.file must be a string")
                    file_value = None
                if not _is_int(duration) or duration < MIN_DURATION_MS or duration > MAX_DURATION_MS:
                    errors.append(
                        f"{label}: {where}.duration_ms must be an integer "
                        f"{MIN_DURATION_MS}..{MAX_DURATION_MS}"
                    )
                if file_value is not None:
                    name_check = Path(file_value.replace("\\", "/")).name
                    match = NAME_RE.match(name_check)
                    if not match:
                        errors.append(
                            f"{label}: {where}.file must match the lowercase "
                            "project_subject_purpose_variant_YYYYMMDD-HHMMSS-uniqueid.png rule: "
                            f"{file_value!r}"
                        )
                    else:
                        try:
                            _dt.datetime.strptime(match.group("stamp"), "%Y%m%d-%H%M%S")
                        except ValueError:
                            errors.append(f"{label}: {where}.file has an invalid timestamp: {file_value!r}")
                    if name_check in seen_names:
                        errors.append(
                            f"{label}: {where}.file reuses filename {name_check!r} "
                            f"already used by {seen_names[name_check]}"
                        )
                    else:
                        seen_names[name_check] = where
                resolved = None
                if file_value is not None:
                    resolved = _resolve_inside(source_dir, file_value, f"{label}: {where}", errors, True)
                if resolved is not None:
                    key = _norm_key(resolved)
                    if key in seen_paths:
                        errors.append(
                            f"{label}: {where}.file reuses source file already used by {seen_paths[key]}"
                        )
                    else:
                        seen_paths[key] = where
                if not _is_int(duration) or duration < MIN_DURATION_MS or duration > MAX_DURATION_MS:
                    duration = None
                clip_entry = {
                    "action": action,
                    "direction": direction,
                    "index": index,
                    "source_rel": file_value,
                    "source_path": resolved,
                    "file_name": Path(file_value.replace("\\", "/")).name if isinstance(file_value, str) else None,
                    "duration_ms": duration,
                    "data": None,
                    "sha256": None,
                    "bytes": None,
                    "png": None,
                }
                if resolved is not None:
                    try:
                        frame_bytes = _read_bytes(resolved)
                    except OSError as exc:
                        errors.append(f"{label}: {where}.file cannot be read ({exc})")
                    else:
                        png_info, png_errors = _analyze_png(
                            frame_bytes, f"{label}: {where} ({file_value})", action
                        )
                        errors.extend(png_errors)
                        clip_entry.update(
                            data=frame_bytes,
                            sha256=_sha256_bytes(frame_bytes),
                            bytes=len(frame_bytes),
                            png=png_info,
                        )
                frames.append(clip_entry)

    source_files = []
    optional_sources = data.get("source_files")
    if optional_sources is not None:
        if not isinstance(optional_sources, list):
            errors.append(f"{label}: source_files must be an array when present")
        else:
            seen_source_files = set()
            for index, value in enumerate(optional_sources):
                where = f"source_files[{index}]"
                descriptor = value if isinstance(value, dict) else None
                if descriptor is not None:
                    value = descriptor.get("file")
                if not isinstance(value, str):
                    errors.append(f"{label}: {where} must be a relative path string or file descriptor")
                    continue
                declared = descriptor.get("sha256") if descriptor is not None else None
                if declared is not None and (not isinstance(declared, str) or not re.fullmatch(r"[0-9a-f]{64}", declared)):
                    errors.append(f"{label}: {where} has an invalid sha256 pin")
                    continue
                resolved = _resolve_inside(source_dir, value, f"{label}: {where}", errors, False)
                if resolved is None:
                    continue
                key = _norm_key(resolved)
                if key in seen_source_files:
                    errors.append(f"{label}: {where} repeats a source file")
                    continue
                seen_source_files.add(key)
                try:
                    sha256, size = _sha256_file(resolved)
                except OSError as exc:
                    errors.append(f"{label}: {where} cannot be read ({exc})")
                    continue
                if declared is not None and declared != sha256:
                    errors.append(f"{label}: {where} does not match its sha256 pin")
                    continue
                source_files.append(
                    {"source_rel": value, "source_path": resolved, "sha256": sha256, "bytes": size, "descriptor": descriptor}
                )

    if errors:
        raise Refusal(errors, "invalid-source")
    counts = {
        action: {direction: len((clips.get(action) or {}).get(direction, [])) for direction in DIRECTIONS}
        for action in ACTIONS
    }
    return {
        "path": source_path,
        "raw": raw,
        "sha256": _sha256_bytes(raw),
        "data": data,
        "dir": source_dir,
        "frames": frames,
        "source_files": source_files,
        "counts": counts,
    }


def _check_destination(out):
    if _exists(out):
        kind = _link_kind(out)
        if kind:
            raise Refusal([f"--out is a {kind}; refusing to publish: {_display(out)}"], "bad-destination")
        if not _is_dir(out):
            raise Refusal([f"--out exists and is not a directory: {_display(out)}"], "bad-destination")
        try:
            with os.scandir(_fs(out)) as scan:
                if any(True for _ in scan):
                    raise Refusal(
                        [f"--out is not empty; existing files are never overwritten: {_display(out)}"],
                        "bad-destination",
                    )
        except OSError as exc:
            raise Refusal([f"--out cannot be inspected ({exc}): {_display(out)}"], "bad-destination")
        return {"existed": True}
    parent = out.parent
    if not _exists(parent) or not _is_dir(parent):
        raise Refusal(
            [f"--out parent directory does not exist or is not a directory: {_display(parent)}"],
            "bad-destination",
        )
    kind = _link_kind(parent)
    if kind:
        raise Refusal(
            [f"--out parent is a {kind}; refusing to publish: {_display(parent)}"], "bad-destination"
        )
    return {"existed": False}


# ---------------------------------------------------------------------------
# Package construction
# ---------------------------------------------------------------------------


def _generated_name(stamp, subject, purpose, variant, extension, errors):
    unique = secrets.token_hex(4)
    name = f"{PROJECT_SLUG}_{subject}_{purpose}_{variant}_{stamp}-{unique}.{extension}"
    if not re.match(
        r"^[a-z0-9][a-z0-9-]*_[a-z0-9][a-z0-9-]*_[a-z0-9][a-z0-9-]*_[a-z0-9][a-z0-9-]*_\d{8}-\d{6}-[a-z0-9]{4,32}\.[a-z0-9]+$",
        name,
    ):
        errors.append(f"generated output name violates the global naming rule: {name}")
    return name


def _make_names(errors):
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    set_name = _generated_name(stamp, SUBJECT, "exploration-sprite-set", "runtime-v01", "json", errors)
    registry_name = _generated_name(
        stamp, SUBJECT, "exploration-sprite-set-registry", "runtime-v01", "json", errors
    )
    provenance_name = _generated_name(
        stamp, SUBJECT, "exploration-source-package-provenance", "v01", "json", errors
    )
    return {
        "stamp": stamp,
        "package_uid": secrets.token_hex(4),
        "set": set_name,
        "registry": registry_name,
        "provenance": provenance_name,
    }


def _set_manifest(source, names):
    actions = {}
    for action in ACTIONS:
        actions[action] = {}
        for direction in DIRECTIONS:
            actions[action][direction] = [
                {"file": f"{PNG_DIR}/{frame['file_name']}", "duration_ms": frame["duration_ms"]}
                for frame in source["frames"]
                if frame["action"] == action and frame["direction"] == direction
            ]
    return {
        "schema": SCHEMA_SET,
        "set_id": f"{SUBJECT}-exploration-source-{names['stamp']}-{names['package_uid']}",
        "actor_id": ACTOR,
        "density": DENSITY,
        "frame_size": [FRAME_W, FRAME_H],
        "pivot": [PIVOT_X, PIVOT_Y],
        "actions": actions,
    }


def _registry_manifest(names):
    return {"schema": SCHEMA_REGISTRY, "actors": {ACTOR: names["set"]}}


def _provenance_manifest(source, ctx, names, set_hash, registry_hash, copied, set_size, registry_size):
    packager_path = Path(__file__).resolve()
    packager_hash, packager_size = _sha256_file(packager_path)
    frames = []
    for frame in source["frames"]:
        png = frame["png"] or {}
        frames.append(
            {
                "action": frame["action"],
                "direction": frame["direction"],
                "index": frame["index"],
                "source_file": _repo_display(frame["source_path"], ctx["repo"]),
                "source_relative_to_manifest": frame["source_rel"],
                "output_file": f"{PNG_DIR}/{frame['file_name']}",
                "sha256": frame["sha256"],
                "bytes": frame["bytes"],
                "width": png.get("width"),
                "height": png.get("height"),
                "bit_depth": png.get("bit_depth"),
                "color_type": png.get("color_type"),
                "body_height": png.get("body_height"),
                "last_opaque_row": png.get("last_opaque_row"),
                "duration_ms": frame["duration_ms"],
            }
        )
    source_files = [
        {
            "source_file": _repo_display(item["source_path"], ctx["repo"]),
            "source_relative_to_manifest": item["source_rel"],
            "sha256": item["sha256"],
            "bytes": item["bytes"],
            **({"descriptor": item["descriptor"]} if item.get("descriptor") is not None else {}),
        }
        for item in source["source_files"]
    ]
    output_files = [
        {"file": item["file"], "sha256": item["sha256"], "bytes": item["bytes"]} for item in copied
    ]
    output_files.extend(
        [
            {"file": names["set"], "sha256": set_hash, "bytes": set_size},
            {"file": names["registry"], "sha256": registry_hash, "bytes": registry_size},
        ]
    )
    return {
        "schema": SCHEMA_PROVENANCE,
        "created_utc": _dt.datetime.now(_dt.timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "actor_id": ACTOR,
        "density": DENSITY,
        "frame_size": [FRAME_W, FRAME_H],
        "pivot": [PIVOT_X, PIVOT_Y],
        "naming": {
            "rule": "project_subject_purpose_variant_YYYYMMDD-HHMMSS-uniqueid.ext",
            "stamp": names["stamp"],
            "generated_output_names_unique": True,
            "lowercase": True,
        },
        "packager": {
            "file": packager_path.name,
            "sha256": packager_hash,
            "bytes": packager_size,
        },
        "source_manifest": {
            "file": _repo_display(source["path"], ctx["repo"]),
            "sha256": source["sha256"],
            "bytes": len(source["raw"]),
        },
        "source_root": _repo_display(source["dir"], ctx["repo"]),
        "copy": {
            "method": "byte-for-byte read/write of validated source PNG bytes",
            "image_editing": "none",
            "requantizing": "none",
            "resampling": "none",
            "atlas_or_sheet": "none",
            "network_used": False,
            "import_metadata_copied": False,
        },
        "counts": source["counts"],
        "source_pngs": frames,
        "source_files": source_files,
        "runtime_set": {"file": names["set"], "sha256": set_hash},
        "registry": {"file": names["registry"], "sha256": registry_hash},
        "output_files": output_files,
        "no_overwrite": True,
    }


def _stage_package(source, ctx, names, destination_state):
    errors = []
    set_manifest = _set_manifest(source, names)
    registry_manifest = _registry_manifest(names)
    stage = None
    try:
        stage = _new_stage_dir(ctx["out"].parent)
        png_dir = stage / PNG_DIR
        _mkdir(png_dir)
        target_names = set()
        copied = []
        for frame in source["frames"]:
            target = png_dir / frame["file_name"]
            if target.name in target_names:
                errors.append(f"duplicate output PNG name: {target.name}")
                continue
            target_names.add(target.name)
            _write_new(target, frame["data"])
            digest, size = _sha256_file(target)
            copied.append({"file": f"{PNG_DIR}/{target.name}", "sha256": digest, "bytes": size})
            if digest != frame["sha256"]:
                errors.append(f"copied PNG hash mismatch: {target.name}")
        _write_new(stage / names["set"], _json_bytes(set_manifest))
        set_hash, set_size = _sha256_file(stage / names["set"])
        _write_new(stage / names["registry"], _json_bytes(registry_manifest))
        registry_hash, registry_size = _sha256_file(stage / names["registry"])
        provenance = _provenance_manifest(
            source, ctx, names, set_hash, registry_hash, copied, set_size, registry_size
        )
        _write_new(stage / names["provenance"], _json_bytes(provenance))
        if errors:
            raise Refusal(errors, "package-construction")
        _verify_stage(stage, source, names, set_hash, registry_hash)
        return stage
    except Exception:
        if stage is not None:
            _rmtree(stage)
        raise


def _verify_stage(stage, source, names, set_hash, registry_hash):
    errors = []
    expected_files = {f"{PNG_DIR}/{frame['file_name']}" for frame in source["frames"]}
    expected_files.update({names["set"], names["registry"], names["provenance"]})
    found_files = set()
    for root, _dirs, files in os.walk(_fs(stage)):
        for name in files:
            relative = os.path.relpath(os.path.join(root, name), _fs(stage)).replace("\\", "/")
            found_files.add(relative)
    if found_files != expected_files:
        missing = sorted(expected_files - found_files)
        extra = sorted(found_files - expected_files)
        if missing:
            errors.append(f"staged package is missing output file(s): {missing}")
        if extra:
            errors.append(f"staged package has unexpected output file(s): {extra}")

    set_path = stage / names["set"]
    registry_path = stage / names["registry"]
    provenance_path = stage / names["provenance"]
    try:
        set_data = json.loads(_read_bytes(set_path).decode("utf-8"))
        registry_data = json.loads(_read_bytes(registry_path).decode("utf-8"))
        provenance_data = json.loads(_read_bytes(provenance_path).decode("utf-8"))
    except Exception as exc:
        raise Refusal([f"staged manifest verification failed: {exc}"], "internal-verification")

    if set_data.get("schema") != SCHEMA_SET or set_data.get("actor_id") != ACTOR:
        errors.append("staged set manifest schema/actor_id is wrong")
    if set_data.get("density") != DENSITY or set_data.get("frame_size") != [FRAME_W, FRAME_H]:
        errors.append("staged set manifest density/frame_size is wrong")
    if set_data.get("pivot") != [PIVOT_X, PIVOT_Y]:
        errors.append("staged set manifest pivot is wrong")
    set_actions = set_data.get("actions")
    if not isinstance(set_actions, dict):
        errors.append("staged set manifest actions is not an object")
    else:
        for action in ACTIONS:
            actual_action = set_actions.get(action)
            if not isinstance(actual_action, dict):
                errors.append(f"staged set manifest is missing actions.{action}")
                continue
            for direction in DIRECTIONS:
                actual_frames = actual_action.get(direction)
                expected_count = source["counts"][action][direction]
                if not isinstance(actual_frames, list) or len(actual_frames) != expected_count:
                    errors.append(
                        f"staged set manifest {action}/{direction} count is wrong "
                        f"(expected {expected_count})"
                    )
                    continue
                for frame, actual in zip(
                    [
                        item
                        for item in source["frames"]
                        if item["action"] == action and item["direction"] == direction
                    ],
                    actual_frames,
                ):
                    if not isinstance(actual, dict):
                        errors.append(f"staged set manifest {action}/{direction} frame is not an object")
                        continue
                    if actual.get("file") != f"{PNG_DIR}/{frame['file_name']}":
                        errors.append(f"staged set manifest {action}/{direction} file reference is wrong")
                    if actual.get("duration_ms") != frame["duration_ms"]:
                        errors.append(f"staged set manifest {action}/{direction} duration is wrong")
    if registry_data.get("schema") != SCHEMA_REGISTRY or registry_data.get("actors", {}).get(ACTOR) != names["set"]:
        errors.append("staged registry does not point protagonist-female at the emitted set")
    if provenance_data.get("schema") != SCHEMA_PROVENANCE:
        errors.append("staged provenance schema is wrong")
    if _sha256_file(set_path)[0] != set_hash:
        errors.append("staged set manifest hash changed during verification")
    if _sha256_file(registry_path)[0] != registry_hash:
        errors.append("staged registry hash changed during verification")

    for frame in source["frames"]:
        relative = f"{PNG_DIR}/{frame['file_name']}"
        target = stage / relative
        if not _is_file(target):
            errors.append(f"staged PNG is missing: {relative}")
            continue
        data = _read_bytes(target)
        if _sha256_bytes(data) != frame["sha256"]:
            errors.append(f"staged PNG is not a byte-for-byte copy: {relative}")
            continue
        info, png_errors = _analyze_png(data, relative, frame["action"])
        errors.extend(png_errors)
        if info.get("width") != FRAME_W or info.get("height") != FRAME_H:
            errors.append(f"staged PNG size is wrong: {relative}")
    if errors:
        raise Refusal(errors, "internal-verification")


def _publish(stage, out, destination_state):
    if destination_state["existed"]:
        if not _exists(out) or not _is_dir(out) or _link_kind(out):
            raise Refusal([f"--out changed during packaging: {_display(out)}"], "bad-destination")
        try:
            with os.scandir(_fs(out)) as scan:
                if any(True for _ in scan):
                    raise Refusal(
                        [f"--out became non-empty during packaging: {_display(out)}"], "bad-destination"
                    )
        except OSError as exc:
            raise Refusal([f"--out cannot be re-inspected ({exc})"], "bad-destination")
        try:
            os.rmdir(_fs(out))
        except OSError as exc:
            raise Refusal([f"cannot release the existing empty --out ({exc})"], "bad-destination")
    elif _exists(out):
        raise Refusal(
            [f"--out appeared during packaging; refusing to overwrite: {_display(out)}"],
            "bad-destination",
        )
    try:
        os.rename(_fs(stage), _fs(out))
    except OSError as exc:
        raise Refusal([f"atomic publication failed ({exc})"], "publication")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def package(args):
    if Image is None:
        raise Refusal(["Pillow is required to validate PNG pixels (pip install Pillow)"], "environment")
    ctx = _resolve_arguments(args)
    source = _read_source_manifest(ctx)
    destination_state = _check_destination(ctx["out"])
    names_errors = []
    names = _make_names(names_errors)
    if names_errors:
        raise Refusal(names_errors, "naming")
    stage = _stage_package(source, ctx, names, destination_state)
    try:
        _publish(stage, ctx["out"], destination_state)
    finally:
        if _exists(stage):
            _rmtree(stage)
    set_path = ctx["out"] / names["set"]
    registry_path = ctx["out"] / names["registry"]
    provenance_path = ctx["out"] / names["provenance"]
    return {
        "ok": True,
        "source": {
            "path": _repo_display(source["path"], ctx["repo"]),
            "sha256": source["sha256"],
            "bytes": len(source["raw"]),
            "frame_count": len(source["frames"]),
            "counts": source["counts"],
        },
        "out": _display(ctx["out"]),
        "package": {
            "set": {"file": names["set"], "sha256": _sha256_file(set_path)[0]},
            "registry": {"file": names["registry"], "sha256": _sha256_file(registry_path)[0]},
            "provenance": {"file": names["provenance"], "sha256": _sha256_file(provenance_path)[0]},
            "png_count": len(source["frames"]),
        },
        "no_overwrite": True,
        "network_used": False,
    }


def _build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Package validated worlds-between.exploration-source.v1 PNG sources into the "
            "existing exploration sprite-set runtime contract without editing image bytes."
        ),
        epilog=(
            "--out must be new or an existing empty directory. Existing files are never overwritten. "
            "See the module docstring for the full source contract."
        ),
    )
    parser.add_argument("--source", required=True, help="source-manifest JSON (schema worlds-between.exploration-source.v1)")
    parser.add_argument("--out", required=True, help="new or existing-empty destination directory")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="optional repository root: resolve relative paths against it and require source/out inside it",
    )
    return parser


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        result = package(args)
    except Refusal as exc:
        print(json.dumps({"ok": False, "kind": exc.kind, "errors": exc.errors}, indent=2, ensure_ascii=False))
        return 1
    except Exception as exc:  # unexpected: report, never suppress
        traceback.print_exc()
        print(
            json.dumps(
                {"ok": False, "kind": "internal-error", "errors": [f"{type(exc).__name__}: {exc}"]},
                indent=2,
                ensure_ascii=False,
            )
        )
        return 70
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
