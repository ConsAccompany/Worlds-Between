#!/usr/bin/env python3
"""Strict selective seven-pose revision packer for the heroine combat set.

This tool is intentionally NOT an art or motion approval step.  It copies the
current, contract-bound v01 spritesheet byte-for-byte at the decoded RGBA level,
replaces exactly cells 16..22 from a Claude-authored revision manifest, and writes
a new four-file package under outputs/heroine-packer19/.  All other cells,
including unused cell 29, remain exact copies of the baseline sheet.

Usage:
  python -I <this> --revision <manifest.json> --out-dir <short-folder> \
      --tag <YYYYMMDD-HHMMSS-xxxxxxxx> --write
  python -I <this> --revision <manifest.json> --out-dir <short-folder> \
      --tag <YYYYMMDD-HHMMSS-xxxxxxxx> --check
  python -I <this> --self-test

The v01 package-builder is imported read-only; its constants and JSON formatting
are reused rather than copied into a second packaging framework.
"""

from __future__ import annotations

import argparse
import copy
import datetime
import hashlib
import importlib.util
import io
import json
import os
import re
import secrets
import shutil
import sys
import zipfile
from functools import lru_cache
from pathlib import Path, PurePosixPath

from PIL import Image, __version__ as PIL_VERSION

# Importing the read-only v01 builder must not leave bytecode caches in tools/.
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
# Windows native sources can exceed MAX_PATH; preserve repository containment.
if os.name == "nt" and not str(ROOT).startswith("\\\\?\\"):
    ROOT = Path("\\\\?\\" + str(ROOT))
BASE_COMMIT = "dedf44ddb83e29d3864da4dca9a6b9fe1e6673cf"
BASELINE_PKG_REL = "game/data/heroine-sea-combat-v01"
BASELINE_INDEX_NAME = (
    "rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet-index_"
    "v01_20261020-201338-38ecfcb0.json"
)
BASELINE_INDEX_REL = BASELINE_PKG_REL + "/" + BASELINE_INDEX_NAME
BASELINE_INDEX_SHA256 = "1abb5b67b3bf59c02b3c747068789a01509812aee97c105b9f5c15c7a60ffa49"
OUTPUT_ROOT_REL = "outputs/heroine-packer19"
REVISION_SCHEMA = "worlds-between.heroine-combat-pose-revision/1"
REVISION_KEYS = {
    "schema",
    "baselineIndex",
    "baselineIndexSha256",
    "cell",
    "pivot",
    "tickRate",
    "overrides",
    "artApproved",
}
OVERRIDE_KEYS = (
    "dodge-a",
    "dodge-b",
    "skill-tel-a",
    "skill-tel-b",
    "skill-strike",
    "skill-contact",
    "skill-recover",
)
CHANGED_CELLS = tuple(range(16, 23))
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
TAG_RE = re.compile(r"^[0-9]{8}-[0-9]{6}-[0-9a-f]{8}$")
SHORT_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
STEM = "rpg-2-star-ocean-the-second_heroine-sea-combat_pose-revision_"


def _load_builder():
    matches = sorted((ROOT / "tools").glob("*heroine-sea-combat_package-builder_v01_*.py"))
    if len(matches) != 1:
        raise RuntimeError("expected exactly one package-builder v01, found %d" % len(matches))
    spec = importlib.util.spec_from_file_location("hsea_package_builder_v01", matches[0])
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load package-builder v01")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.ROOT.resolve() != ROOT.resolve():
        raise RuntimeError("package-builder v01 has a different producer root")
    return module


try:
    BUILDER = _load_builder()
except Exception as exc:  # noqa: BLE001 - fail closed with a visible diagnostic
    print("PACK FAILED: cannot import read-only package-builder v01: %s" % exc, file=sys.stderr)
    raise SystemExit(1)

CELL_W = BUILDER.CELL_W
CELL_H = BUILDER.CELL_H
PIVOT = list(BUILDER.PIVOT)
TICK_RATE = BUILDER.TICK_RATE
COLUMNS = BUILDER.COLUMNS
ROWS = BUILDER.ROWS
CELL_COUNT = BUILDER.CELL_COUNT
USED_CELL_COUNT = BUILDER.USED_CELL_COUNT
UNUSED_CELLS = list(BUILDER.UNUSED_CELLS)
ACTION_ORDER = list(BUILDER.ACTION_ORDER)
LOOP_ACTIONS = set(BUILDER.LOOP_ACTIONS)
LOOP_START = dict(BUILDER.LOOP_START)
SET_SCHEMA = BUILDER.SET_SCHEMA
INDEX_SCHEMA = BUILDER.INDEX_SCHEMA
PROVENANCE_SCHEMA = BUILDER.PROVENANCE_SCHEMA
SHEET_W = COLUMNS * CELL_W
SHEET_H = ROWS * CELL_H


class PackFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PackFailure(message)


def is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_link_like(path: Path) -> bool:
    """True for symlinks and Windows reparse points such as directory junctions."""
    try:
        if path.is_symlink():
            return True
        st = os.lstat(path)
    except OSError:
        return False
    return bool(getattr(st, "st_file_attributes", 0) & 0x400)  # FILE_ATTRIBUTE_REPARSE_POINT


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return BUILDER.sha256_file(path)


def relative_path(path: Path) -> str:
    try:
        return owner_relative(path)
    except ValueError as exc:
        raise PackFailure("path is outside producer root: %s" % path) from exc


def owner_relative(path: Path) -> str:
    resolved = path.resolve()
    if os.name == "nt" and not str(resolved).startswith("\\\\?\\"):
        resolved = Path("\\\\?\\" + str(resolved))
    return resolved.relative_to(ROOT.resolve()).as_posix()


def _reject_constant(value: str):
    raise PackFailure("non-finite JSON number rejected: " + value)


def _no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise PackFailure("duplicate JSON object key rejected: %r" % key)
        result[key] = value
    return result


def read_json_strict(path: Path, label: str):
    require(path.is_file(), "missing %s JSON: %s" % (label, owner_relative(path)))
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), "%s JSON must not start with a UTF-8 BOM" % label)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PackFailure("%s JSON is not valid UTF-8: %s" % (label, exc)) from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_no_duplicate_keys,
            parse_constant=_reject_constant,
        )
    except PackFailure:
        raise
    except Exception as exc:  # noqa: BLE001 - malformed JSON is a gate failure
        raise PackFailure("%s JSON is malformed: %s" % (label, exc)) from exc
    require(isinstance(value, dict), "%s JSON root must be an object" % label)
    return value


def safe_repo_path(value, label: str) -> Path:
    require(isinstance(value, str) and value, "%s must be a non-empty repo-relative path" % label)
    value = value.replace("\\", "/")
    require("\x00" not in value, "%s contains a NUL byte" % label)
    require(re.fullmatch(r"[A-Za-z0-9._/-]+", value) is not None,
            "%s contains unsupported characters: %r" % (label, value))
    pure = PurePosixPath(value)
    require(not pure.is_absolute(), "%s must not be absolute: %r" % (label, value))
    require(pure.parts, "%s is empty" % label)
    require(all(part not in ("", ".", "..") for part in pure.parts),
            "%s contains a traversal component: %r" % (label, value))
    require(not pure.parts[0].endswith(":"), "%s must not contain a drive/ADS prefix" % label)
    path = ROOT / pure
    current = ROOT
    for part in pure.parts:
        current = current / part
        if _is_link_like(current):
            raise PackFailure("%s must not traverse a symlink or reparse point: %s" % (label, value))
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise PackFailure("%s escapes producer root: %r" % (label, value)) from exc
    return resolved


def require_hash(value, label: str) -> str:
    require(isinstance(value, str) and HASH_RE.fullmatch(value) is not None,
            "%s must be a lowercase 64-hex SHA256" % label)
    return value


def validate_tag(tag: str) -> str:
    require(isinstance(tag, str) and TAG_RE.fullmatch(tag) is not None,
            "--tag must be YYYYMMDD-HHMMSS-xxxxxxxx (lowercase 8-hex unique id)")
    try:
        stamp = datetime.datetime.strptime(tag[:15], "%Y%m%d-%H%M%S").replace(
            tzinfo=datetime.timezone.utc)
    except ValueError as exc:
        raise PackFailure("--tag timestamp is not a valid UTC timestamp") from exc
    now = datetime.datetime.now(datetime.timezone.utc)
    require(stamp <= now + datetime.timedelta(minutes=5),
            "--tag timestamp is in the future; generated names must use actual UTC time")
    return tag


def resolve_out_dir(value: str) -> Path:
    require(isinstance(value, str) and value, "--out-dir must be a non-empty path")
    value = value.replace("\\", "/")
    require(not PurePosixPath(value).is_absolute(), "--out-dir must be repo-relative")
    if "/" not in value:
        value = OUTPUT_ROOT_REL + "/" + value
    require(value.startswith(OUTPUT_ROOT_REL + "/"),
            "--out-dir must be a short folder under " + OUTPUT_ROOT_REL + "/")
    path = safe_repo_path(value, "--out-dir")
    root = (ROOT / OUTPUT_ROOT_REL).resolve()
    try:
        rel = path.relative_to(root)
    except ValueError as exc:
        raise PackFailure("--out-dir must be under " + OUTPUT_ROOT_REL + "/") from exc
    require(rel.parts, "--out-dir must name a folder below " + OUTPUT_ROOT_REL + "/")
    require(len(rel.parts) <= 3, "--out-dir nesting is too deep for a short package folder")
    for part in rel.parts:
        require(SHORT_RE.fullmatch(part) is not None,
                "--out-dir components must be lowercase short names: %r" % part)
    return path


def decode_png(path: Path, expected_size, label: str):
    require(path.is_file(), "%s is missing: %s" % (label, owner_relative(path)))
    require(path.suffix == ".png", "%s must have a lowercase .png suffix" % label)
    try:
        with Image.open(path) as probe:
            probe.verify()
        with Image.open(path) as opened:
            require(opened.format == "PNG", "%s is not a PNG" % label)
            require(opened.size == expected_size,
                    "%s must be %dx%d, got %s" % (label, expected_size[0], expected_size[1], opened.size))
            require(opened.mode == "RGBA", "%s must be RGBA, got %s" % (label, opened.mode))
            opened.load()
            rgba = opened.convert("RGBA")
    except PackFailure:
        raise
    except Exception as exc:  # noqa: BLE001 - malformed image is a gate failure
        raise PackFailure("malformed PNG %s: %s" % (label, exc)) from exc
    raw = rgba.tobytes()
    require(len(raw) == expected_size[0] * expected_size[1] * 4,
            "%s decoded to an unexpected byte length" % label)
    alpha = sorted(set(raw[3::4]))
    return {
        "rgba": rgba,
        "raw": raw,
        "alpha_values": alpha,
        "bbox": rgba.getbbox(),
    }


def opaque_palette(raw: bytes) -> set[bytes]:
    return {
        raw[index:index + 3]
        for index in range(0, len(raw), 4)
        if raw[index + 3] == 255
    }


def validate_cell_png(path: Path, palette: set[bytes], label: str):
    info = decode_png(path, (CELL_W, CELL_H), label)
    require(set(info["alpha_values"]) <= {0, 255},
            "%s must use binary alpha (0/255), got %r" % (label, info["alpha_values"]))
    require(info["bbox"] is not None, "%s is fully transparent" % label)
    raw = info["raw"]
    colors = {
        raw[index:index + 3]
        for index in range(0, len(raw), 4)
        if raw[index + 3] == 255
    }
    require(colors, "%s has no opaque pixels" % label)
    extra = sorted(colors - palette)
    require(not extra, "%s uses %d colour(s) outside the baseline palette" % (label, len(extra)))
    return info


def validate_native(path: Path, kind: str, expected_sha: str, label: str):
    require(path.is_file(), "%s is missing: %s" % (label, owner_relative(path)))
    require(path.suffix == "." + kind, "%s must have a lowercase .%s suffix" % (label, kind))
    require(sha256_file(path) == expected_sha, "%s SHA256 disagrees with revision manifest" % label)
    require(zipfile.is_zipfile(path), "%s is not a readable ZIP/native container" % label)
    required = {
        "pxo": {"mimetype", "data.json", "preview.png"},
        "ora": {"mimetype", "stack.xml", "mergedimage.png"},
    }[kind]
    expected_mime = {
        "pxo": "application/x-pixelorama",
        "ora": "image/openraster",
    }[kind]
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            require(len(names) == len(set(names)), "%s contains duplicate ZIP entries" % label)
            require(required <= set(names), "%s is missing required native entries" % label)
            mime = archive.read("mimetype").decode("ascii")
            require(mime == expected_mime, "%s has the wrong native mimetype" % label)
            require(archive.testzip() is None, "%s has a corrupt native entry" % label)
    except PackFailure:
        raise
    except Exception as exc:  # noqa: BLE001 - malformed native file is a gate failure
        raise PackFailure("malformed native %s: %s" % (label, exc)) from exc


def validate_actions(actions, label: str) -> None:
    require(isinstance(actions, dict), label + " actions must be an object")
    require(set(actions) == set(ACTION_ORDER), label + " actions must have exactly the eight v01 names")
    for name in ACTION_ORDER:
        action = actions[name]
        require(isinstance(action, dict), "%s action %s must be an object" % (label, name))
        allowed = {"loop", "tick_rate", "frames"}
        if name in LOOP_ACTIONS:
            allowed.add("loop_start")
        require(set(action) == allowed, "%s action %s has unexpected keys" % (label, name))
        require(action["loop"] is (name in LOOP_ACTIONS),
                "%s action %s loop semantics changed" % (label, name))
        require(is_int(action["tick_rate"]) and action["tick_rate"] == TICK_RATE,
                "%s action %s tick_rate must be integer 30" % (label, name))
        frames = action["frames"]
        require(isinstance(frames, list) and frames, "%s action %s frames must be non-empty" % (label, name))
        for frame in frames:
            require(isinstance(frame, dict) and set(frame) == {"cell", "ticks"},
                    "%s action %s frame has unexpected keys" % (label, name))
            require(is_int(frame["cell"]) and 0 <= frame["cell"] < CELL_COUNT,
                    "%s action %s cell is not an integer 0..29" % (label, name))
            require(is_int(frame["ticks"]) and frame["ticks"] > 0,
                    "%s action %s ticks must be a positive integer" % (label, name))
        if name in LOOP_ACTIONS:
            require(is_int(action["loop_start"]) and 0 <= action["loop_start"] < len(frames),
                    "%s action %s loop_start is invalid" % (label, name))
            require(action["loop_start"] == LOOP_START[name],
                    "%s action %s loop_start differs from checked v01 semantics" % (label, name))


@lru_cache(maxsize=1)
def load_baseline():
    index_path = safe_repo_path(BASELINE_INDEX_REL, "baseline index")
    require(index_path.is_file(), "baseline index is missing: " + BASELINE_INDEX_REL)
    index_raw = index_path.read_bytes()
    index_sha = sha256_bytes(index_raw)
    require(index_sha == BASELINE_INDEX_SHA256,
            "baseline index SHA256 differs from the contract: %s != %s" % (index_sha, BASELINE_INDEX_SHA256))
    index = read_json_strict(index_path, "baseline index")
    require(set(index) == {"schema", "sets"}, "baseline index has unexpected keys")
    require(index["schema"] == INDEX_SCHEMA, "baseline index schema/version is not " + INDEX_SCHEMA)
    require(isinstance(index["sets"], dict), "baseline index sets must be an object")
    require(set(index["sets"]) == {"hero:female"}, "baseline index must contain exactly hero:female")
    manifest_name = index["sets"]["hero:female"]
    require(isinstance(manifest_name, str) and PurePosixPath(manifest_name).name == manifest_name,
            "baseline index manifest must be a bare filename")

    manifest_path = safe_repo_path(BASELINE_PKG_REL + "/" + manifest_name, "baseline manifest")
    manifest = read_json_strict(manifest_path, "baseline manifest")
    require(set(manifest) == {
        "schema", "set_id", "character", "art_status", "art_approved", "motion_approved",
        "default_adoption", "note", "source_provenance", "sheet", "cell_size", "pivot",
        "authored_facing", "logical_scale", "display_proportion", "actions",
    }, "baseline manifest has unexpected keys")
    require(manifest["schema"] == SET_SCHEMA, "baseline manifest schema/version mismatch")
    require(manifest["set_id"] == "heroine-sea-combat-v01",
            "baseline manifest set_id must remain heroine-sea-combat-v01")
    require(manifest["character"] == {"member_id": "hero", "appearance": "female"},
            "baseline manifest identity changed")
    require(manifest["art_approved"] is False and manifest["motion_approved"] is False,
            "baseline manifest unexpectedly claims art/motion approval")
    require(manifest["default_adoption"] is False, "baseline manifest unexpectedly claims default adoption")
    require(manifest["cell_size"] == [CELL_W, CELL_H], "baseline manifest cell_size must be [136, 144]")
    require(manifest["pivot"] == PIVOT, "baseline manifest pivot must be [64, 136]")
    require(manifest["authored_facing"] == "right", "baseline manifest authored_facing changed")
    require(manifest["logical_scale"] == 0.5, "baseline manifest logical_scale changed")
    require(manifest["display_proportion"] == "0.65", "baseline manifest display_proportion changed")
    validate_actions(manifest["actions"], "baseline")

    sheet_name = manifest["sheet"]
    provenance_name = manifest["source_provenance"]
    require(isinstance(sheet_name, str) and PurePosixPath(sheet_name).name == sheet_name,
            "baseline sheet must be a bare filename")
    require(isinstance(provenance_name, str) and PurePosixPath(provenance_name).name == provenance_name,
            "baseline source_provenance must be a bare filename")
    sheet_path = safe_repo_path(BASELINE_PKG_REL + "/" + sheet_name, "baseline sheet")
    provenance_path = safe_repo_path(BASELINE_PKG_REL + "/" + provenance_name,
                                     "baseline source provenance")
    manifest_sha = sha256_file(manifest_path)
    sheet_sha = sha256_file(sheet_path)
    provenance_sha = sha256_file(provenance_path)

    provenance = read_json_strict(provenance_path, "baseline source provenance")
    require(set(provenance) == {
        "schema", "set_id", "package_directory", "build_reference_tag", "character",
        "art_status", "art_approved", "motion_approved", "default_adoption", "note",
        "packaging", "sheet", "manifest", "index", "build_tool", "source_manifests",
        "sources", "actions", "authored_durations", "action_order", "frozen_counts",
    }, "baseline source provenance has unexpected keys")
    require(provenance["schema"] == PROVENANCE_SCHEMA,
            "baseline source provenance schema/version mismatch")
    require(provenance["set_id"] == "heroine-sea-combat-v01",
            "baseline source provenance set_id changed")
    require(provenance["package_directory"] == BASELINE_PKG_REL,
            "baseline source provenance package_directory changed")
    require(provenance["sheet"]["file"] == sheet_name and provenance["sheet"]["sha256"] == sheet_sha,
            "baseline source provenance does not bind the baseline sheet")
    require(provenance["manifest"]["file"] == manifest_name and
            provenance["manifest"]["sha256"] == manifest_sha,
            "baseline source provenance does not bind the baseline manifest")
    require(provenance["index"]["file"] == BASELINE_INDEX_NAME and
            provenance["index"]["sha256"] == index_sha,
            "baseline source provenance does not bind the baseline index")
    require(provenance["packaging"]["unused_cells"] == UNUSED_CELLS,
            "baseline provenance unused_cells changed")
    require(provenance["packaging"]["used_cell_count"] == USED_CELL_COUNT,
            "baseline provenance used_cell_count changed")

    sources = provenance["sources"]
    require(isinstance(sources, list) and len(sources) == USED_CELL_COUNT,
            "baseline provenance must contain exactly 29 source records")
    source_by_cell = {}
    for record in sources:
        require(isinstance(record, dict), "baseline source record must be an object")
        cell = record.get("cell")
        require(is_int(cell) and 0 <= cell < CELL_COUNT, "baseline source cell is invalid")
        require(cell not in source_by_cell, "baseline source cell is duplicated")
        require(isinstance(record.get("pose"), str) and record["pose"],
                "baseline source pose is invalid")
        for field in ("source_png", "native_pxo", "native_ora"):
            safe_repo_path(record.get(field), "baseline source " + field)
        for field in ("source_png_sha256", "native_pxo_sha256", "native_ora_sha256"):
            require_hash(record.get(field), "baseline source " + field)
        source_by_cell[cell] = record
    require(set(source_by_cell) == set(range(USED_CELL_COUNT)),
            "baseline provenance source cells must be 0..28")

    seven_cells = {}
    for cell in CHANGED_CELLS:
        record = source_by_cell[cell]
        pose = OVERRIDE_KEYS[cell - 16]
        require(record["pose"] == pose,
                "baseline provenance cell %d must be %s, got %s" % (cell, pose, record["pose"]))
        seven_cells[pose] = cell
        source_path = safe_repo_path(record["source_png"], "baseline source " + pose)
        require(sha256_file(source_path) == record["source_png_sha256"],
                "baseline source PNG SHA256 mismatch for " + pose)
        source_info = decode_png(source_path, (CELL_W, CELL_H), "baseline source " + pose)
        require(set(source_info["alpha_values"]) <= {0, 255},
                "baseline source %s does not use binary alpha" % pose)
        require(source_info["bbox"] is not None, "baseline source %s is fully transparent" % pose)

    sheet_info = decode_png(sheet_path, (SHEET_W, SHEET_H), "baseline sheet")
    require(sheet_info["bbox"] is not None, "baseline sheet is fully transparent")
    sheet_raw = sheet_info["raw"]
    for cell in CHANGED_CELLS:
        record = source_by_cell[cell]
        source_info = decode_png(safe_repo_path(record["source_png"], "baseline source"),
                                 (CELL_W, CELL_H), "baseline source " + record["pose"])
        origin = ((cell % COLUMNS) * CELL_W, (cell // COLUMNS) * CELL_H)
        cell_bytes = sheet_info["rgba"].crop(
            (origin[0], origin[1], origin[0] + CELL_W, origin[1] + CELL_H)).tobytes()
        require(cell_bytes == source_info["raw"],
                "baseline provenance source does not match baseline sheet cell " + record["pose"])
    for cell in UNUSED_CELLS:
        origin = ((cell % COLUMNS) * CELL_W, (cell // COLUMNS) * CELL_H)
        cell_bytes = sheet_info["rgba"].crop(
            (origin[0], origin[1], origin[0] + CELL_W, origin[1] + CELL_H)).tobytes()
        require(set(cell_bytes) == {0}, "baseline unused cell is not fully transparent")

    return {
        "index_path": index_path,
        "index": index,
        "index_sha": index_sha,
        "manifest_path": manifest_path,
        "manifest": manifest,
        "manifest_sha": manifest_sha,
        "sheet_path": sheet_path,
        "sheet_sha": sheet_sha,
        "sheet_rgba": sheet_info["rgba"],
        "sheet_raw": sheet_raw,
        "sheet_palette": opaque_palette(sheet_raw),
        "provenance_path": provenance_path,
        "provenance": provenance,
        "provenance_sha": provenance_sha,
        "source_by_cell": source_by_cell,
        "seven_cells": seven_cells,
    }


def load_revision(path: Path, baseline) -> dict:
    data = read_json_strict(path, "revision manifest")
    require(set(data) == REVISION_KEYS, "revision manifest has missing or unknown top-level keys")
    require(data["schema"] == REVISION_SCHEMA,
            "revision manifest schema/version must be " + REVISION_SCHEMA)
    require(data["baselineIndex"] == BASELINE_INDEX_REL,
            "revision baselineIndex must be the contract v01 index path")
    require(data["baselineIndexSha256"] == BASELINE_INDEX_SHA256,
            "revision baselineIndexSha256 must equal the contract-bound index SHA256")
    require(data["baselineIndexSha256"] == baseline["index_sha"],
            "revision baselineIndexSha256 disagrees with the actual baseline index")
    require(isinstance(data["cell"], list) and len(data["cell"]) == 2 and
            all(is_int(value) for value in data["cell"]),
            "revision cell must be two integers")
    require(data["cell"] == [CELL_W, CELL_H], "revision cell must be [136, 144]")
    require(isinstance(data["pivot"], list) and len(data["pivot"]) == 2 and
            all(is_int(value) for value in data["pivot"]),
            "revision pivot must be two integers")
    require(data["pivot"] == PIVOT, "revision pivot must be [64, 136]")
    require(is_int(data["tickRate"]) and data["tickRate"] == TICK_RATE,
            "revision tickRate must be integer 30")
    require(data["artApproved"] is False, "revision artApproved must be false")

    overrides = data["overrides"]
    require(isinstance(overrides, dict), "revision overrides must be an object")
    require(set(overrides) == set(OVERRIDE_KEYS),
            "revision overrides must contain exactly the seven v01 pose keys; "
            "missing=%r unknown=%r" % (sorted(set(OVERRIDE_KEYS) - set(overrides)),
                                        sorted(set(overrides) - set(OVERRIDE_KEYS))))
    parsed = {}
    cells = {}
    for pose in OVERRIDE_KEYS:
        entry = overrides[pose]
        require(isinstance(entry, dict),
                "revision override %s must be an object" % pose)
        require(set(entry) == {"png", "sha256", "pxo", "pxoSha256", "ora", "oraSha256"},
                "revision override %s has missing or unknown keys" % pose)
        png_path = safe_repo_path(entry["png"], pose + ".png")
        pxo_path = safe_repo_path(entry["pxo"], pose + ".pxo")
        ora_path = safe_repo_path(entry["ora"], pose + ".ora")
        png_sha = require_hash(entry["sha256"], pose + ".sha256")
        pxo_sha = require_hash(entry["pxoSha256"], pose + ".pxoSha256")
        ora_sha = require_hash(entry["oraSha256"], pose + ".oraSha256")
        require(sha256_file(png_path) == png_sha,
                "revision PNG SHA256 disagrees for %s: %s" % (pose, owner_relative(png_path)))
        info = validate_cell_png(png_path, baseline["sheet_palette"], "revision " + pose)
        require(sha256_file(pxo_path) == pxo_sha,
                "revision PXO SHA256 disagrees for %s: %s" % (pose, owner_relative(pxo_path)))
        validate_native(pxo_path, "pxo", pxo_sha, "revision %s PXO" % pose)
        require(sha256_file(ora_path) == ora_sha,
                "revision ORA SHA256 disagrees for %s: %s" % (pose, owner_relative(ora_path)))
        validate_native(ora_path, "ora", ora_sha, "revision %s ORA" % pose)
        cell = baseline["seven_cells"][pose]
        cells[pose] = cell
        parsed[pose] = {
            "cell": cell,
            "png_path": png_path,
            "png_sha": png_sha,
            "pxo_path": pxo_path,
            "pxo_sha": pxo_sha,
            "ora_path": ora_path,
            "ora_sha": ora_sha,
            "rgba": info["rgba"],
            "raw": info["raw"],
            "alpha_values": info["alpha_values"],
        }
    require(sorted(cells.values()) == list(CHANGED_CELLS),
            "revision pose cells must be exactly 16..22 per baseline provenance")
    return {
        "path": path,
        "data": data,
        "overrides": parsed,
        "cells": cells,
        "sha256": sha256_file(path),
    }


def output_names(tag: str) -> dict[str, str]:
    return {
        "sheet": STEM + "spritesheet_" + tag + ".png",
        "manifest": STEM + "spritesheet-manifest_" + tag + ".json",
        "index": STEM + "spritesheet-index_" + tag + ".json",
        "provenance": STEM + "source-provenance_" + tag + ".json",
    }


def build_outputs(baseline, revision, tag: str, out_dir: Path):
    names = output_names(tag)
    if os.name == "nt":
        for name in names.values():
            require(len(str(out_dir / name)) <= 255,
                    "output path is too long for this Windows runtime: " + owner_relative(out_dir / name))
    sheet = Image.frombytes("RGBA", (SHEET_W, SHEET_H), baseline["sheet_raw"])
    override_cells = set(CHANGED_CELLS)
    for pose in OVERRIDE_KEYS:
        cell = revision["cells"][pose]
        origin = ((cell % COLUMNS) * CELL_W, (cell // COLUMNS) * CELL_H)
        sheet.paste(revision["overrides"][pose]["rgba"], origin)

    for cell in range(CELL_COUNT):
        origin = ((cell % COLUMNS) * CELL_W, (cell // COLUMNS) * CELL_H)
        got = sheet.crop((origin[0], origin[1], origin[0] + CELL_W, origin[1] + CELL_H)).tobytes()
        if cell in override_cells:
            pose = OVERRIDE_KEYS[cell - 16]
            want = revision["overrides"][pose]["raw"]
        else:
            want = baseline["sheet_rgba"].crop(
                (origin[0], origin[1], origin[0] + CELL_W, origin[1] + CELL_H)).tobytes()
        require(got == want, "internal packing mismatch at cell %d" % cell)
    for cell in UNUSED_CELLS:
        origin = ((cell % COLUMNS) * CELL_W, (cell // COLUMNS) * CELL_H)
        cell_bytes = sheet.crop(
            (origin[0], origin[1], origin[0] + CELL_W, origin[1] + CELL_H)).tobytes()
        require(set(cell_bytes) == {0}, "unused cell %d is not transparent" % cell)

    buffer = io.BytesIO()
    sheet.save(buffer, format="PNG", optimize=False, compress_level=9)
    sheet_bytes = buffer.getvalue()
    decoded = Image.open(io.BytesIO(sheet_bytes)).convert("RGBA")
    require(decoded.size == (SHEET_W, SHEET_H), "encoded revision sheet dimensions changed")
    require(decoded.tobytes() == sheet.tobytes(), "encoded revision sheet does not decode byte-exactly")

    manifest = copy.deepcopy(baseline["manifest"])
    manifest["sheet"] = names["sheet"]
    manifest["source_provenance"] = names["provenance"]
    manifest["note"] = (
        baseline["manifest"]["note"]
        + " Selective seven-pose revision package "
        + tag
        + ": only cells 16..22 are replaced from the revision manifest; art/motion remain unapproved."
    )
    manifest_bytes = BUILDER.json_bytes(manifest)

    index = copy.deepcopy(baseline["index"])
    index["sets"]["hero:female"] = names["manifest"]
    index_bytes = BUILDER.json_bytes(index)

    prov = copy.deepcopy(baseline["provenance"])
    prov["package_directory"] = owner_relative(out_dir)
    prov["build_reference_tag"] = tag
    prov["art_status"] = "unapproved-heroine-sea-combat-pose-revision-motion-pending"
    prov["art_approved"] = False
    prov["motion_approved"] = False
    prov["default_adoption"] = False
    prov["note"] = (
        "Technical selective revision packing evidence only. Seven pose cells were replaced from "
        "the revision manifest; the other 22 poses and unused cell 29 are byte-exact baseline sheet "
        "copies. This package is not art approval, motion approval or default adoption."
    )
    prov["packaging"]["method"] = (
        "Exact decoded baseline sheet copy with seven RGBA cell replacements at provenance-derived "
        "cell origins; no resize, resample, filter or alpha blend."
    )
    prov["packaging"]["pillow_version"] = PIL_VERSION
    prov["packaging"]["sheet_columns"] = COLUMNS
    prov["packaging"]["sheet_rows"] = ROWS
    prov["packaging"]["cell_count"] = CELL_COUNT
    prov["packaging"]["used_cell_count"] = USED_CELL_COUNT
    prov["packaging"]["unused_cells"] = UNUSED_CELLS
    prov["sheet"] = {
        "file": names["sheet"],
        "sha256": sha256_bytes(sheet_bytes),
        "width": SHEET_W,
        "height": SHEET_H,
        "mode": "RGBA",
        "cell_size": [CELL_W, CELL_H],
        "pivot": PIVOT,
    }
    prov["manifest"] = {
        "file": names["manifest"],
        "sha256": sha256_bytes(manifest_bytes),
        "schema": SET_SCHEMA,
    }
    prov["index"] = {
        "file": names["index"],
        "sha256": sha256_bytes(index_bytes),
        "schema": INDEX_SCHEMA,
    }
    tool_path = Path(__file__).resolve()
    require(re.fullmatch(r"[a-z0-9_./-]+", owner_relative(tool_path)) is not None,
            "packer tool path must be lowercase")
    prov["build_tool"] = {
        "path": owner_relative(tool_path),
        "sha256": sha256_file(tool_path),
    }
    prov["baseline_package"] = {
        "base_commit": BASE_COMMIT,
        "index": {"file": BASELINE_INDEX_REL, "sha256": baseline["index_sha"]},
        "manifest": {
            "file": owner_relative(baseline["manifest_path"]),
            "sha256": baseline["manifest_sha"],
        },
        "sheet": {
            "file": owner_relative(baseline["sheet_path"]),
            "sha256": baseline["sheet_sha"],
        },
        "provenance": {
            "file": owner_relative(baseline["provenance_path"]),
            "sha256": baseline["provenance_sha"],
        },
    }
    prov["revision"] = {
        "schema": REVISION_SCHEMA,
        "manifest_file": owner_relative(revision["path"]),
        "manifest_sha256": revision["sha256"],
        "tag": tag,
        "changed_cells": list(CHANGED_CELLS),
        "art_approved": False,
        "motion_approved": False,
    }

    records = []
    for cell in range(USED_CELL_COUNT):
        old = copy.deepcopy(baseline["source_by_cell"][cell])
        if cell in override_cells:
            pose = OVERRIDE_KEYS[cell - 16]
            entry = revision["overrides"][pose]
            old["pose"] = pose
            old["role"] = "revision"
            old["source_png"] = owner_relative(entry["png_path"])
            old["source_png_sha256"] = entry["png_sha"]
            old["source_dimensions"] = [CELL_W, CELL_H]
            old["source_mode"] = "RGBA"
            old["source_alpha_values"] = entry["alpha_values"]
            old["native_pxo"] = owner_relative(entry["pxo_path"])
            old["native_pxo_sha256"] = entry["pxo_sha"]
            old["native_ora"] = owner_relative(entry["ora_path"])
            old["native_ora_sha256"] = entry["ora_sha"]
            old["baseline_source_png"] = baseline["source_by_cell"][cell]["source_png"]
            old["baseline_source_png_sha256"] = baseline["source_by_cell"][cell]["source_png_sha256"]
        records.append(old)
    prov["sources"] = records
    provenance_bytes = BUILDER.json_bytes(prov)

    outputs = {
        names["sheet"]: sheet_bytes,
        names["manifest"]: manifest_bytes,
        names["index"]: index_bytes,
        names["provenance"]: provenance_bytes,
    }
    return outputs, names, sheet


def verify_outputs(baseline, revision, tag: str, out_dir: Path, outputs, names, sheet_image):
    require(set(outputs) == set(names.values()), "internal output name set mismatch")
    require(out_dir.is_dir(), "output directory is missing: " + owner_relative(out_dir))
    entries = list(out_dir.iterdir())
    require(all(path.is_file() and not _is_link_like(path) for path in entries),
            "output directory may contain only regular files")
    require({path.name for path in entries} == set(outputs),
            "output directory must contain exactly the four package files")
    for name, data in outputs.items():
        path = out_dir / name
        require(path.read_bytes() == data,
                "output file bytes differ from in-memory package: " + name)

    sheet_sha = sha256_bytes(outputs[names["sheet"]])
    manifest_sha = sha256_bytes(outputs[names["manifest"]])
    index_sha = sha256_bytes(outputs[names["index"]])

    with Image.open(io.BytesIO(outputs[names["sheet"]])) as opened:
        require(opened.format == "PNG", "revision sheet is not PNG")
        require(opened.size == (SHEET_W, SHEET_H), "revision sheet is not 816x720")
        require(opened.mode == "RGBA", "revision sheet is not RGBA")
        opened.load()
        out_rgba = opened.convert("RGBA")
    override_cells = set(CHANGED_CELLS)
    for cell in range(CELL_COUNT):
        origin = ((cell % COLUMNS) * CELL_W, (cell // COLUMNS) * CELL_H)
        got = out_rgba.crop((origin[0], origin[1], origin[0] + CELL_W, origin[1] + CELL_H)).tobytes()
        if cell in override_cells:
            pose = OVERRIDE_KEYS[cell - 16]
            want = revision["overrides"][pose]["raw"]
            require(got == want, "changed cell %d does not equal its revision source bytes" % cell)
        else:
            want = baseline["sheet_rgba"].crop(
                (origin[0], origin[1], origin[0] + CELL_W, origin[1] + CELL_H)).tobytes()
            require(got == want, "untouched cell %d is not baseline-exact" % cell)
    for cell in UNUSED_CELLS:
        origin = ((cell % COLUMNS) * CELL_W, (cell // COLUMNS) * CELL_H)
        got = out_rgba.crop((origin[0], origin[1], origin[0] + CELL_W, origin[1] + CELL_H)).tobytes()
        require(set(got) == {0}, "unused cell %d is not fully transparent" % cell)

    manifest = read_json_strict(out_dir / names["manifest"], "output manifest")
    require(set(manifest) == set(baseline["manifest"]), "output manifest key set changed")
    require(manifest["actions"] == baseline["manifest"]["actions"],
            "output manifest actions/frames/ticks/loop semantics changed")
    require(manifest["set_id"] == baseline["manifest"]["set_id"],
            "output manifest set_id changed")
    require(manifest["character"] == baseline["manifest"]["character"],
            "output manifest identity changed")
    for key in baseline["manifest"]:
        if key in {"sheet", "source_provenance", "note"}:
            continue
        require(manifest[key] == baseline["manifest"][key],
                "output manifest preserved field changed: " + key)
    require(manifest["sheet"] == names["sheet"], "output manifest sheet filename is wrong")
    require(manifest["source_provenance"] == names["provenance"],
            "output manifest provenance filename is wrong")
    require("revision" in manifest["note"] and "unapproved" in manifest["note"],
            "output manifest note does not identify the unapproved revision")

    index = read_json_strict(out_dir / names["index"], "output index")
    require(set(index) == set(baseline["index"]), "output index key set changed")
    require(index["schema"] == baseline["index"]["schema"], "output index schema changed")
    require(index["sets"] == {"hero:female": names["manifest"]},
            "output index does not point at the new manifest")

    prov = read_json_strict(out_dir / names["provenance"], "output provenance")
    require(prov["set_id"] == "heroine-sea-combat-v01", "output provenance set_id changed")
    require(prov["sheet"]["file"] == names["sheet"] and prov["sheet"]["sha256"] == sheet_sha,
            "output provenance sheet hash mismatch")
    require(prov["manifest"]["file"] == names["manifest"] and
            prov["manifest"]["sha256"] == manifest_sha,
            "output provenance manifest hash mismatch")
    require(prov["index"]["file"] == names["index"] and prov["index"]["sha256"] == index_sha,
            "output provenance index hash mismatch")
    require(prov["build_tool"]["path"] == owner_relative(Path(__file__).resolve()),
            "output provenance build_tool path mismatch")
    require(prov["build_tool"]["sha256"] == sha256_file(Path(__file__).resolve()),
            "output provenance build_tool hash mismatch")
    require(prov["baseline_package"]["base_commit"] == BASE_COMMIT,
            "output provenance baseline commit mismatch")
    require(prov["baseline_package"]["index"]["sha256"] == baseline["index_sha"],
            "output provenance baseline index hash mismatch")
    require(prov["baseline_package"]["manifest"]["sha256"] == baseline["manifest_sha"],
            "output provenance baseline manifest hash mismatch")
    require(prov["baseline_package"]["sheet"]["sha256"] == baseline["sheet_sha"],
            "output provenance baseline sheet hash mismatch")
    require(prov["baseline_package"]["provenance"]["sha256"] == baseline["provenance_sha"],
            "output provenance baseline provenance hash mismatch")
    require(prov["art_approved"] is False and prov["motion_approved"] is False,
            "output provenance must remain art/motion unapproved")
    require(prov["revision"]["changed_cells"] == list(CHANGED_CELLS),
            "output provenance changed-cell list mismatch")
    require(prov["revision"]["manifest_sha256"] == revision["sha256"],
            "output provenance revision manifest hash mismatch")
    require(len(prov["sources"]) == USED_CELL_COUNT, "output provenance source count changed")
    for cell in range(USED_CELL_COUNT):
        record = prov["sources"][cell]
        require(record["cell"] == cell, "output provenance sources are not cell-ordered")
        if cell in override_cells:
            pose = OVERRIDE_KEYS[cell - 16]
            entry = revision["overrides"][pose]
            require(record["role"] == "revision", "output provenance role not revision at cell %d" % cell)
            require(record["source_png"] == owner_relative(entry["png_path"]),
                    "output provenance PNG path mismatch at cell %d" % cell)
            require(record["source_png_sha256"] == entry["png_sha"],
                    "output provenance PNG hash mismatch at cell %d" % cell)
            require(record["native_pxo"] == owner_relative(entry["pxo_path"]),
                    "output provenance PXO path mismatch at cell %d" % cell)
            require(record["native_pxo_sha256"] == entry["pxo_sha"],
                    "output provenance PXO hash mismatch at cell %d" % cell)
            require(record["native_ora"] == owner_relative(entry["ora_path"]),
                    "output provenance ORA path mismatch at cell %d" % cell)
            require(record["native_ora_sha256"] == entry["ora_sha"],
                    "output provenance ORA hash mismatch at cell %d" % cell)
        else:
            require(record == baseline["source_by_cell"][cell],
                    "output provenance untouched source record changed at cell %d" % cell)

    return {
        "out_dir": out_dir,
        "names": names,
        "hashes": {
            names["sheet"]: sheet_sha,
            names["manifest"]: manifest_sha,
            names["index"]: index_sha,
            names["provenance"]: sha256_bytes(outputs[names["provenance"]]),
        },
        "changed_cells": list(CHANGED_CELLS),
    }


def check_existing(out_dir: Path, outputs, require_all: bool) -> None:
    if not out_dir.exists():
        require(not require_all, "output directory does not exist: " + owner_relative(out_dir))
        return
    require(out_dir.is_dir() and not _is_link_like(out_dir),
            "output path is not a regular directory: " + owner_relative(out_dir))
    entries = list(out_dir.iterdir())
    require(all(path.is_file() and not _is_link_like(path) for path in entries),
            "output directory contains a non-regular or symlink entry")
    names = {path.name for path in entries}
    extras = sorted(names - set(outputs))
    require(not extras, "refusing to overwrite unrelated files in output directory: %r" % extras)
    if require_all:
        missing = sorted(set(outputs) - names)
        require(not missing, "existing result is missing package files: %r" % missing)
    mismatched = sorted(
        name for name in names
        if (out_dir / name).read_bytes() != outputs[name]
    )
    require(not mismatched,
            "refusing to overwrite nonmatching existing file(s): %r" % mismatched)


def write_outputs(out_dir: Path, outputs) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        destination = out_dir / name
        if destination.exists():
            continue
        temporary = out_dir / (".tmp-" + secrets.token_hex(4))
        try:
            temporary.write_bytes(data)
            os.replace(temporary, destination)
        finally:
            if temporary.exists():
                temporary.unlink()


def execute(revision_arg: str, out_arg: str, tag: str, mode: str, announce: bool = True) -> dict:
    require(mode in {"write", "check"}, "internal mode must be write or check")
    validate_tag(tag)
    baseline = load_baseline()
    revision_path = safe_repo_path(revision_arg, "--revision")
    revision = load_revision(revision_path, baseline)
    out_dir = resolve_out_dir(out_arg)
    outputs, names, sheet_image = build_outputs(baseline, revision, tag, out_dir)

    if mode == "write":
        check_existing(out_dir, outputs, require_all=False)
        write_outputs(out_dir, outputs)
        check_existing(out_dir, outputs, require_all=True)
    else:
        check_existing(out_dir, outputs, require_all=True)

    result = verify_outputs(baseline, revision, tag, out_dir, outputs, names, sheet_image)
    if announce:
        if mode == "write":
            print("PACK BUILD OK tag=%s out=%s changed_cells=%s" % (
                tag, owner_relative(out_dir), ",".join(str(c) for c in CHANGED_CELLS)))
        else:
            print("PACK CHECK OK tag=%s out=%s changed_cells=%s" % (
                tag, owner_relative(out_dir), ",".join(str(c) for c in CHANGED_CELLS)))
        for name in (names["index"], names["manifest"], names["sheet"], names["provenance"]):
            print("%s  %s" % (result["hashes"][name], name))
        print("baseline_index_sha256=%s base_commit=%s" % (baseline["index_sha"], BASE_COMMIT))
        print("sources=7 native_pxo=7 native_ora=7 untouched_cells=22 unused=29 set_id=heroine-sea-combat-v01")
    return result


def utc_tag() -> str:
    return (
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
        + "-"
        + secrets.token_hex(4)
    )


def make_fixture_png(path: Path, size, color, alpha: int) -> None:
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    for y in range(20, 60):
        for x in range(20, 60):
            if x < size[0] and y < size[1]:
                image.putpixel((x, y), (color[0], color[1], color[2], alpha))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")


def self_test() -> int:
    tag = utc_tag()
    validate_tag(tag)
    short_id = tag[-8:]
    fixture_root = (ROOT / OUTPUT_ROOT_REL / ("f-" + tag)).resolve()
    require(not fixture_root.exists(), "fixture root unexpectedly exists: " + owner_relative(fixture_root))
    fixture_root.mkdir(parents=True)
    fixtures = fixture_root / "fixtures"
    cells = fixture_root / "cells"
    fixtures.mkdir()
    cells.mkdir()
    cases = []
    log_lines = []

    def log(line: str) -> None:
        log_lines.append(line)
        print(line)

    baseline = load_baseline()
    valid_data = {
        "schema": REVISION_SCHEMA,
        "baselineIndex": BASELINE_INDEX_REL,
        "baselineIndexSha256": BASELINE_INDEX_SHA256,
        "cell": [CELL_W, CELL_H],
        "pivot": PIVOT,
        "tickRate": TICK_RATE,
        "overrides": {
            pose: {
                "png": baseline["source_by_cell"][cell]["source_png"],
                "sha256": baseline["source_by_cell"][cell]["source_png_sha256"],
                "pxo": baseline["source_by_cell"][cell]["native_pxo"],
                "pxoSha256": baseline["source_by_cell"][cell]["native_pxo_sha256"],
                "ora": baseline["source_by_cell"][cell]["native_ora"],
                "oraSha256": baseline["source_by_cell"][cell]["native_ora_sha256"],
            }
            for cell, pose in zip(CHANGED_CELLS, OVERRIDE_KEYS)
        },
        "artApproved": False,
    }
    valid_path = fixtures / "valid.json"
    valid_path.write_bytes(BUILDER.json_bytes(valid_data))

    def fixture_path(name: str) -> Path:
        return fixtures / (name + ".json")

    def write_case(name: str, mutate) -> Path:
        data = copy.deepcopy(valid_data)
        mutate(data)
        path = fixture_path(name)
        path.write_bytes(BUILDER.json_bytes(data))
        return path

    def case(label: str, path: Path, out_rel: str, needle: str, mode: str = "write") -> None:
        try:
            execute(owner_relative(path), out_rel, tag, mode, announce=False)
        except (PackFailure, BUILDER.BuildFailure) as exc:
            message = str(exc)
            require(needle.lower() in message.lower(),
                    "case %s failed with an unexpected diagnostic: %s" % (label, message))
            target = (ROOT / out_rel).resolve()
            require(not target.exists(), "case %s mutated the output directory on failure" % label)
            cases.append({"case": label, "expected_failure": True, "diagnostic": message,
                          "pass": True})
            log("SELFTEST CASE OK  %-28s %s" % (label, message))
            return
        raise PackFailure("case %s unexpectedly succeeded" % label)

    pass_out = OUTPUT_ROOT_REL + "/pass-" + short_id
    result = execute(owner_relative(valid_path), pass_out, tag, "write", announce=False)
    require(result["hashes"], "successful pack returned no hashes")
    pass_dir = ROOT / pass_out
    require(pass_dir.is_dir(), "successful pack did not create the output directory")
    with Image.open(pass_dir / result["names"]["sheet"]) as opened:
        require(opened.convert("RGBA").tobytes() == baseline["sheet_rgba"].tobytes(),
                "baseline-cell fixture pack did not reproduce the baseline decoded sheet")
    execute(owner_relative(valid_path), pass_out, tag, "check", announce=False)
    cases.append({"case": "successful-pack-and-check", "expected_failure": False,
                  "output_dir": pass_out, "hashes": result["hashes"], "pass": True})
    log("SELFTEST CASE OK  successful-pack-and-check %s" % owner_relative(pass_dir))

    mod_png = cells / "modified-dodge-a.png"
    with Image.open(ROOT / baseline["source_by_cell"][16]["source_png"]) as opened:
        mod_rgba = opened.convert("RGBA")
    mod_raw = bytearray(mod_rgba.tobytes())
    replacement = None
    for index in range(0, len(mod_raw), 4):
        if mod_raw[index + 3] == 255:
            old_color = bytes(mod_raw[index:index + 3])
            replacement = next(value for value in sorted(baseline["sheet_palette"]) if value != old_color)
            mod_raw[index:index + 3] = replacement
            break
    require(replacement is not None, "could not build a modified fixture cell")
    Image.frombytes("RGBA", (CELL_W, CELL_H), bytes(mod_raw)).save(mod_png, format="PNG")
    mod_data = copy.deepcopy(valid_data)
    mod_data["overrides"]["dodge-a"]["png"] = owner_relative(mod_png)
    mod_data["overrides"]["dodge-a"]["sha256"] = sha256_file(mod_png)
    mod_path = fixture_path("modified-cell")
    mod_path.write_bytes(BUILDER.json_bytes(mod_data))
    mod_out = OUTPUT_ROOT_REL + "/passmod-" + short_id
    mod_result = execute(owner_relative(mod_path), mod_out, tag, "write", announce=False)
    mod_dir = ROOT / mod_out
    with Image.open(mod_dir / mod_result["names"]["sheet"]) as opened:
        packed = opened.convert("RGBA")
    origin = (((16 % COLUMNS) * CELL_W), ((16 // COLUMNS) * CELL_H))
    got = packed.crop((origin[0], origin[1], origin[0] + CELL_W, origin[1] + CELL_H)).tobytes()
    require(got == bytes(mod_raw), "modified fixture cell was not packed from its source bytes")
    require(got != baseline["sheet_rgba"].crop(
        (origin[0], origin[1], origin[0] + CELL_W, origin[1] + CELL_H)).tobytes(),
        "modified fixture cell unexpectedly equals the baseline cell")
    for cell in range(CELL_COUNT):
        if cell == 16:
            continue
        cell_origin = ((cell % COLUMNS) * CELL_W, (cell // COLUMNS) * CELL_H)
        cell_bytes = packed.crop(
            (cell_origin[0], cell_origin[1], cell_origin[0] + CELL_W, cell_origin[1] + CELL_H)).tobytes()
        want = baseline["sheet_rgba"].crop(
            (cell_origin[0], cell_origin[1], cell_origin[0] + CELL_W, cell_origin[1] + CELL_H)).tobytes()
        require(cell_bytes == want, "modified pack changed untouched cell %d" % cell)
    execute(owner_relative(mod_path), mod_out, tag, "check", announce=False)
    cases.append({"case": "modified-cell-pack-and-check", "expected_failure": False,
                  "output_dir": mod_out, "hashes": mod_result["hashes"],
                  "changed_cell": 16, "pass": True})
    log("SELFTEST CASE OK  modified-cell-pack-and-check %s" % owner_relative(mod_dir))

    palette_color = sorted(baseline["sheet_palette"])[0]
    bad_color = next(
        value for value in ((1, 2, 3), (3, 2, 1), (254, 1, 253))
        if value not in baseline["sheet_palette"]
    )

    def set_override_png(data, pose: str, path: Path) -> None:
        data["overrides"][pose]["png"] = owner_relative(path)
        data["overrides"][pose]["sha256"] = sha256_file(path)

    dim_png = cells / "dim-135x144.png"
    make_fixture_png(dim_png, (135, 144), palette_color, 255)
    pal_png = cells / "palette-extra.png"
    make_fixture_png(pal_png, (136, 144), bad_color, 255)
    alpha_png = cells / "alpha-128.png"
    make_fixture_png(alpha_png, (136, 144), palette_color, 128)
    broken_png = cells / "broken.png"
    broken_png.write_bytes(b"\x89PNG\r\n\x1a\nnot-a-complete-png")
    broken_pxo = cells / "broken.pxo"
    broken_pxo.write_bytes(b"not a zip container")

    def dimensions(data):
        set_override_png(data, "dodge-a", dim_png)

    def palette(data):
        set_override_png(data, "dodge-a", pal_png)

    def alpha(data):
        set_override_png(data, "dodge-a", alpha_png)

    def png_malformed(data):
        set_override_png(data, "dodge-a", broken_png)

    def native_malformed(data):
        data["overrides"]["dodge-a"]["pxo"] = owner_relative(broken_pxo)
        data["overrides"]["dodge-a"]["pxoSha256"] = sha256_file(broken_pxo)

    def bad_hash(data):
        data["overrides"]["dodge-a"]["sha256"] = "0" * 64

    def missing_key(data):
        del data["overrides"]["dodge-a"]

    def unknown_key(data):
        data["overrides"]["dodge-c"] = copy.deepcopy(data["overrides"]["dodge-a"])

    def bad_path(data):
        data["overrides"]["dodge-a"]["png"] = "../outside-root.png"

    def bad_cell_metadata(data):
        data["cell"] = [136, 144.0]

    def bad_tick_metadata(data):
        data["tickRate"] = True

    def bad_art_approval(data):
        data["artApproved"] = True

    for index, (label, mutate, needle) in enumerate((
        ("dimensions-135x144", dimensions, "136x144"),
        ("palette-outside-baseline", palette, "palette"),
        ("alpha-not-binary", alpha, "binary alpha"),
        ("malformed-png", png_malformed, "malformed PNG"),
        ("malformed-native-pxo", native_malformed, "ZIP/native"),
        ("bad-png-hash", bad_hash, "SHA256"),
        ("missing-override-key", missing_key, "seven v01 pose keys"),
        ("unknown-override-key", unknown_key, "seven v01 pose keys"),
        ("path-traversal", bad_path, "traversal"),
        ("malformed-cell-metadata", bad_cell_metadata, "cell"),
        ("malformed-tickrate-metadata", bad_tick_metadata, "tickRate"),
        ("art-approved-must-be-false", bad_art_approval, "artApproved"),
    )):
        path = write_case(label, mutate)
        out_rel = OUTPUT_ROOT_REL + "/n-%02d-%s" % (index, short_id)
        case(label, path, out_rel, needle)

    try:
        execute(owner_relative(valid_path), OUTPUT_ROOT_REL + "/../escape-" + short_id,
                tag, "write", announce=False)
    except (PackFailure, BUILDER.BuildFailure) as exc:
        message = str(exc)
        require("out-dir" in message.lower(), "out-dir traversal failed with unexpected diagnostic: " + message)
        cases.append({"case": "out-dir-traversal", "expected_failure": True,
                      "diagnostic": message, "pass": True})
        log("SELFTEST CASE OK  out-dir-traversal             %s" % message)
    else:
        raise PackFailure("out-dir traversal unexpectedly succeeded")

    check_missing_out = OUTPUT_ROOT_REL + "/n-miss-" + short_id
    try:
        execute(owner_relative(valid_path), check_missing_out, tag, "check", announce=False)
    except (PackFailure, BUILDER.BuildFailure) as exc:
        message = str(exc)
        require("does not exist" in message.lower(),
                "check-missing failed with unexpected diagnostic: " + message)
        require(not (ROOT / check_missing_out).exists(),
                "check-missing created an output directory")
        cases.append({"case": "check-missing", "expected_failure": True,
                      "diagnostic": message, "pass": True})
        log("SELFTEST CASE OK  check-missing                %s" % message)
    else:
        raise PackFailure("check of a missing result unexpectedly succeeded")

    overwrite_out = OUTPUT_ROOT_REL + "/n-over-" + short_id
    overwrite_dir = ROOT / overwrite_out
    overwrite_dir.mkdir(parents=True)
    sheet_name = result["names"]["sheet"]
    sentinel = b"sentinel: must not be overwritten"
    (overwrite_dir / sheet_name).write_bytes(sentinel)
    try:
        execute(owner_relative(valid_path), overwrite_out, tag, "write", announce=False)
    except (PackFailure, BUILDER.BuildFailure) as exc:
        message = str(exc)
        require("refusing to overwrite" in message.lower(),
                "overwrite refusal failed with unexpected diagnostic: " + message)
        require((overwrite_dir / sheet_name).read_bytes() == sentinel,
                "overwrite refusal mutated the nonmatching file")
        cases.append({"case": "overwrite-refusal", "expected_failure": True,
                      "diagnostic": message, "pass": True})
        log("SELFTEST CASE OK  overwrite-refusal            %s" % message)
    else:
        raise PackFailure("nonmatching overwrite unexpectedly succeeded")

    tamper_out = OUTPUT_ROOT_REL + "/n-tamp-" + short_id
    tamper_dir = ROOT / tamper_out
    shutil.copytree(pass_dir, tamper_dir)
    with (tamper_dir / result["names"]["manifest"]).open("ab") as handle:
        handle.write(b" ")
    try:
        execute(owner_relative(valid_path), tamper_out, tag, "check", announce=False)
    except (PackFailure, BUILDER.BuildFailure) as exc:
        message = str(exc)
        require("nonmatching" in message.lower() or "differ" in message.lower(),
                "tampered check failed with unexpected diagnostic: " + message)
        cases.append({"case": "tampered-check", "expected_failure": True,
                      "diagnostic": message, "pass": True})
        log("SELFTEST CASE OK  tampered-check               %s" % message)
    else:
        raise PackFailure("tampered result unexpectedly passed --check")

    try:
        link = cells / "symlink-escape.png"
        link.symlink_to((ROOT / baseline["source_by_cell"][16]["source_png"]).resolve())
        link_data = copy.deepcopy(valid_data)
        link_data["overrides"]["dodge-a"]["png"] = link.relative_to(ROOT).as_posix()
        link_data["overrides"]["dodge-a"]["sha256"] = baseline["source_by_cell"][16]["source_png_sha256"]
        link_path = fixture_path("symlink-escape")
        link_path.write_bytes(BUILDER.json_bytes(link_data))
        case("symlink-escape", link_path, OUTPUT_ROOT_REL + "/n-link-" + short_id, "symlink")
    except OSError as exc:
        cases.append({"case": "symlink-escape", "skipped": True,
                      "reason": "Windows symlink creation unavailable: %s" % exc})
        log("SELFTEST CASE SKIP symlink-escape               %s" % exc)

    summary = {
        "schema": "worlds-between.heroine-combat-pose-revision-selftest/1",
        "fixture_only": True,
        "note": ("Bounded fixture-only self-test. Source fixtures are the current baseline cells; "
                 "no new artwork or motion was authored, and no game/data package was written."),
        "tag": tag,
        "base_commit": BASE_COMMIT,
        "baseline_index_sha256": baseline["index_sha"],
        "tool_path": owner_relative(Path(__file__).resolve()),
        "tool_sha256": sha256_file(Path(__file__).resolve()),
        "pass_output": pass_out,
        "pass_hashes": result["hashes"],
        "modified_output": mod_out,
        "modified_hashes": mod_result["hashes"],
        "cases": cases,
    }
    summary_path = fixture_root / ("summary_" + tag + ".json")
    summary_path.write_bytes(BUILDER.json_bytes(summary))
    log_path = fixture_root / ("selftest_" + tag + ".log")
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8", newline="\n")
    log("SELFTEST OK tag=%s cases=%d summary=%s" % (
        tag, len(cases), owner_relative(summary_path)))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", help="Claude-authored revision manifest (repo-relative)")
    parser.add_argument("--out-dir", help="short folder under " + OUTPUT_ROOT_REL + "/")
    parser.add_argument("--tag", help="actual UTC YYYYMMDD-HHMMSS-xxxxxxxx tag")
    parser.add_argument("--write", action="store_true", help="write a validated revision package")
    parser.add_argument("--check", action="store_true", help="rebuild in memory and verify an existing package")
    parser.add_argument("--verify", action="store_true", help="alias for --check")
    parser.add_argument("--self-test", action="store_true", help="run bounded fixture-only self-tests")
    args = parser.parse_args()

    if args.self_test:
        require(not any((args.revision, args.out_dir, args.tag, args.write, args.check, args.verify)),
                "--self-test cannot be combined with pack arguments")
        return self_test()

    modes = [name for name, active in (("write", args.write), ("check", args.check or args.verify))
             if active]
    require(len(modes) == 1, "exactly one of --write or --check/--verify is required")
    require(args.revision is not None, "--revision is required")
    require(args.out_dir is not None, "--out-dir is required")
    require(args.tag is not None, "--tag is required")
    execute(args.revision, args.out_dir, args.tag, modes[0], announce=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (PackFailure, BUILDER.BuildFailure) as exc:
        print("PACK FAILED: %s" % exc, file=sys.stderr)
        raise SystemExit(1)
