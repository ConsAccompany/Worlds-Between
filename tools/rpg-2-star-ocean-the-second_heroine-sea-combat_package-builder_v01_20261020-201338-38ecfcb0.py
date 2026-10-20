#!/usr/bin/env python3
"""Deterministic technical packer for the heroine Sea-of-Stars-direction combat set.

This is NOT art production and NOT an approval. It reads the existing separately
authored 136x144 RGBA pose PNGs and packs them into one runtime spritesheet plus a
combat-sprite-set/1 manifest, index and a source-provenance manifest. No pixel is
repainted, resampled, filtered or re-coloured; every sheet cell is an exact copy of
its source PNG's decoded RGBA bytes.

Usage:
  python -I <this> --write
  python -I <this> --check      # rebuild in memory and compare every package byte

The source manifests are the actual v01/v02/v03 TEST-ONLY manifests. Their frame
ticks are validated, not guessed. Durations stay integer ticks at 30 Hz; no ms.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sys
from pathlib import Path

from PIL import Image, __version__ as PIL_VERSION

ROOT = Path(__file__).resolve().parents[1]
PKG_REL = "game/data/heroine-sea-combat-v01"
TAG = "20261020-201338-38ecfcb0"
STAMP = "v01_" + TAG
PREFIX = "rpg-2-star-ocean-the-second_heroine-sea-combat_"

SHEET_NAME = PREFIX + "spritesheet_" + STAMP + ".png"
MANIFEST_NAME = PREFIX + "spritesheet-manifest_" + STAMP + ".json"
INDEX_NAME = PREFIX + "spritesheet-index_" + STAMP + ".json"
PROVENANCE_NAME = PREFIX + "source-provenance_" + STAMP + ".json"

CELL_W, CELL_H = 136, 144
PIVOT = [64, 136]
COLUMNS, ROWS = 6, 5
CELL_COUNT = COLUMNS * ROWS
USED_CELL_COUNT = 29
UNUSED_CELLS = [29]
TICK_RATE = 30
SET_SCHEMA = "worlds-between.combat-sprite-set/1"
INDEX_SCHEMA = "worlds-between.combat-sprite-set-index/1"
PROVENANCE_SCHEMA = "worlds-between.combat-sprite-set-provenance/1"

ACTION_ORDER = ["idle", "attack", "move", "guard", "dodge", "skill", "hit", "defeat"]
LOOP_ACTIONS = {"idle", "move", "guard"}
LOOP_START = {"idle": 0, "move": 0, "guard": 1}

# Exact expected source sequences. If a source manifest changes, packaging fails
# instead of silently following a changed schema. The four one-shots with a
# declared then:base get an explicit one-tick base frame in the runtime action.
SOURCE_EXPECTED = {
    "idle": [("base", 8), ("idle-b1", 6), ("idle-b2", 8), ("idle-b1", 6)],
    "attack": [
        ("atk-antic-a", 2), ("atk-antic-b", 2), ("atk-smear", 1),
        ("atk-contact", 2), ("atk-follow", 2), ("atk-recover", 2),
        ("idle-b1", 1),
    ],
    "move": [("move-a", 3), ("move-b", 3), ("move-c", 3), ("move-d", 3)],
    "guard": [("guard-a", 2), ("guard-b", 6), ("guard-c", 6)],
    "dodge": [("dodge-a", 4), ("dodge-b", 4)],
    "skill": [
        ("skill-tel-a", 4), ("skill-tel-b", 3), ("skill-strike", 1),
        ("skill-contact", 2), ("skill-recover", 3),
    ],
    "hit": [("hit-a", 2), ("hit-b", 3), ("hit-c", 2)],
    "defeat": [("down-a", 3), ("down-b", 3), ("down-c", 3)],
}
APPEND_BASE = {"attack", "dodge", "hit", "skill"}
EXPECTED_SOURCE = {
    name: SOURCE_EXPECTED[name] + ([("base", 1)] if name in APPEND_BASE else [])
    for name in ACTION_ORDER
}
EXPECTED_TICKS = {name: sum(ticks for _, ticks in frames) for name, frames in EXPECTED_SOURCE.items()}
EXPECTED_CELLS = {
    pose: index
    for index, pose in enumerate(dict.fromkeys(pose for name in ACTION_ORDER for pose, _ in EXPECTED_SOURCE[name]))
}
EXPECTED_SOURCE_ROLE = {}
for _pose in ["base", "idle-b1", "idle-b2", "atk-antic-a", "atk-antic-b", "atk-smear", "atk-contact", "atk-follow", "atk-recover"]:
    EXPECTED_SOURCE_ROLE[_pose] = "v01"
for _pose in ["move-a", "move-b", "move-c", "move-d", "guard-a", "guard-b", "guard-c", "dodge-a", "dodge-b",
              "skill-tel-a", "skill-tel-b", "skill-strike", "skill-contact", "skill-recover"]:
    EXPECTED_SOURCE_ROLE[_pose] = "v02"
for _pose in ["hit-a", "hit-b", "hit-c", "down-a", "down-b", "down-c"]:
    EXPECTED_SOURCE_ROLE[_pose] = "v03"


class BuildFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BuildFailure(message)


def is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def one(pattern: str) -> Path:
    matches = sorted(ROOT.glob(pattern))
    require(len(matches) == 1, "expected exactly one match for %s, found %d" % (pattern, len(matches)))
    return matches[0]


def read_json(path: Path) -> dict:
    require(path.is_file(), "missing JSON: " + relative(path))
    with path.open("r", encoding="utf-8", newline="") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), "JSON root is not an object: " + relative(path))
    return value


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def validate_source_frames(frames, label: str) -> list[tuple[str, int]]:
    require(isinstance(frames, list) and frames, label + " frames must be a non-empty list")
    result = []
    for frame in frames:
        require(isinstance(frame, dict), label + " frame must be an object")
        pose = frame.get("pose")
        ticks = frame.get("ticks")
        require(isinstance(pose, str) and pose, label + " frame pose must be a non-empty string")
        require(is_int(ticks) and ticks > 0, label + " frame ticks must be a positive integer")
        result.append((pose, ticks))
    return result


def load_sources():
    v1_path = one("outputs/hero-sea-motion-v01/*_manifest_test-only-v01_*.json")
    v2_path = one("outputs/hero-sea-motion-v02/*_manifest_test-only-v02_*.json")
    v3_path = one("outputs/hero-sea-motion-v03/*_manifest_test-only-v03_*.json")
    v1, v2, v3 = read_json(v1_path), read_json(v2_path), read_json(v3_path)
    for manifest, label in ((v1, "v01"), (v2, "v02"), (v3, "v03")):
        require(manifest.get("cell") == [CELL_W, CELL_H], label + " cell must be [136, 144]")
        require(manifest.get("pinNative") == PIVOT, label + " pinNative must be [64, 136]")
        if "tickSeconds" in manifest:
            require(abs(float(manifest["tickSeconds"]) - 1.0 / TICK_RATE) < 2e-9,
                    label + " tickSeconds must represent 1/30 s")
        else:
            require(label == "v03", label + " is missing tickSeconds")

    require(v1["clips"]["idle"].get("loop") is True, "v01 idle must loop")
    require(v1["clips"]["attack"].get("loop") is False, "v01 attack must be one-shot")
    require(v1["clips"]["attack"].get("then") == "base", "v01 attack then must be base")
    require(v2["clips"]["move"].get("loop") is True, "v02 move must loop")
    require(v2["clips"]["guard"].get("loop") is True, "v02 guard must loop")
    require(v2["clips"]["dodge"].get("then") == "base", "v02 dodge then must be base")
    require(v2["clips"]["skill"].get("then") == "base", "v02 skill then must be base")
    require(v3["clips"]["hit"].get("then") == "base", "v03 hit then must be base")
    require(v3["clips"]["down"].get("hold") is True, "v03 down must hold its last frame")

    guard_enter = validate_source_frames(v2["clips"]["guard"].get("enter"), "v02 guard enter")
    require(len(guard_enter) == 1, "v02 guard enter must contain exactly one frame")
    guard_loop = validate_source_frames(v2["clips"]["guard"].get("frames"), "v02 guard loop")
    guard = guard_enter + guard_loop

    raw_frames = {
        "idle": validate_source_frames(v1["clips"]["idle"].get("frames"), "v01 idle"),
        "attack": validate_source_frames(v1["clips"]["attack"].get("frames"), "v01 attack"),
        "move": validate_source_frames(v2["clips"]["move"].get("frames"), "v02 move"),
        "guard": guard,
        "dodge": validate_source_frames(v2["clips"]["dodge"].get("frames"), "v02 dodge"),
        "skill": validate_source_frames(v2["clips"]["skill"].get("frames"), "v02 skill"),
        "hit": validate_source_frames(v3["clips"]["hit"].get("frames"), "v03 hit"),
        "defeat": validate_source_frames(v3["clips"]["down"].get("frames"), "v03 down"),
    }
    for action in ACTION_ORDER:
        require(raw_frames[action] == SOURCE_EXPECTED[action],
                "%s source frames differ from the checked expected sequence: %r" % (action, raw_frames[action]))

    base_info = v1["poseFiles"]["base"]
    require(base_info.get("path", "").startswith("outputs/hero-sea-v01/"), "base source must be outputs/hero-sea-v01")
    require("battle_still-native136" in Path(base_info["path"]).name, "base source must be the native136 battle still")
    require("1294c865" in Path(base_info["path"]).name, "base source must be the 1294c865 still")
    base_path = ROOT / base_info["path"]
    require(base_path.is_file(), "base PNG missing: " + relative(base_path))
    require(sha256_file(base_path) == base_info["sha256"], "base PNG SHA-256 disagrees with v01 manifest")

    sources = {}
    for pose in EXPECTED_CELLS:
        role = EXPECTED_SOURCE_ROLE[pose]
        if role == "v01":
            if pose == "base":
                png_path = base_path
                png_sha = base_info["sha256"]
                native_pxo = one("outputs/hero-sea-v01/*battle_still-editable*.pxo")
                native_ora = one("outputs/hero-sea-v01/*battle_still-layered*.ora")
                pxo_sha = sha256_file(native_pxo)
                ora_sha = sha256_file(native_ora)
            else:
                info = v1["poseFiles"][pose]
                png_path = ROOT / "outputs/hero-sea-motion-v01" / info["name"]
                png_sha = info["sha256"]
                native_pxo = ROOT / "outputs/hero-sea-motion-v01" / v1["files"][pose + ".pxo"]["name"]
                native_ora = ROOT / "outputs/hero-sea-motion-v01" / v1["files"][pose + ".ora"]["name"]
                pxo_sha = v1["files"][pose + ".pxo"]["sha256"]
                ora_sha = v1["files"][pose + ".ora"]["sha256"]
        elif role == "v02":
            info = v2["files"][pose + ".png"]
            png_path = ROOT / "outputs/hero-sea-motion-v02" / info["name"]
            png_sha = info["sha256"]
            native_pxo = ROOT / "outputs/hero-sea-motion-v02" / v2["files"][pose + ".pxo"]["name"]
            native_ora = ROOT / "outputs/hero-sea-motion-v02" / v2["files"][pose + ".ora"]["name"]
            pxo_sha = v2["files"][pose + ".pxo"]["sha256"]
            ora_sha = v2["files"][pose + ".ora"]["sha256"]
        elif role == "v03":
            info = v3["files"][pose + ".png"]
            png_path = ROOT / "outputs/hero-sea-motion-v03" / info["name"]
            png_sha = info["sha256"]
            native_pxo = ROOT / "outputs/hero-sea-motion-v03" / v3["files"][pose + ".pxo"]["name"]
            native_ora = ROOT / "outputs/hero-sea-motion-v03" / v3["files"][pose + ".ora"]["name"]
            pxo_sha = v3["files"][pose + ".pxo"]["sha256"]
            ora_sha = v3["files"][pose + ".ora"]["sha256"]
        else:
            raise BuildFailure("unknown role for " + pose)

        for path, expected, label in ((png_path, png_sha, "PNG"), (native_pxo, pxo_sha, "PXO"), (native_ora, ora_sha, "ORA")):
            require(path.is_file(), "%s missing: %s" % (label, relative(path)))
            require(sha256_file(path) == expected, "%s SHA-256 disagrees with source manifest: %s" % (label, relative(path)))

        with Image.open(png_path) as opened:
            opened.load()
            require(opened.format == "PNG", "source is not PNG: " + relative(png_path))
            require(opened.size == (CELL_W, CELL_H), "source cell is not 136x144: " + relative(png_path))
            require(opened.mode == "RGBA", "source is not RGBA: " + relative(png_path))
            rgba = opened.convert("RGBA")
            raw = rgba.tobytes()
            alpha_values = sorted(set(rgba.getchannel("A").tobytes()))
            require(len(raw) == CELL_W * CELL_H * 4, "unexpected RGBA byte length")
            require(rgba.getbbox() is not None, "source cell is fully transparent: " + relative(png_path))

        sources[pose] = {
            "pose": pose,
            "role": role,
            "source_png": relative(png_path),
            "source_png_sha256": png_sha,
            "source_png_bytes": raw,
            "source_rgba": rgba,
            "source_alpha_values": alpha_values,
            "native_pxo": relative(native_pxo),
            "native_pxo_sha256": pxo_sha,
            "native_ora": relative(native_ora),
            "native_ora_sha256": ora_sha,
        }

    require(len(sources) == USED_CELL_COUNT, "expected 29 distinct source poses")
    manifest_paths = {"v01": v1_path, "v02": v2_path, "v03": v3_path}
    manifest_data = {"v01": v1, "v02": v2, "v03": v3}
    return sources, manifest_paths, manifest_data


def build_manifest():
    actions = {}
    for action in ACTION_ORDER:
        entry = {"loop": action in LOOP_ACTIONS}
        if action in LOOP_ACTIONS:
            entry["loop_start"] = LOOP_START[action]
        entry["tick_rate"] = TICK_RATE
        entry["frames"] = [{"cell": EXPECTED_CELLS[pose], "ticks": ticks} for pose, ticks in EXPECTED_SOURCE[action]]
        actions[action] = entry
    return {
        "schema": SET_SCHEMA,
        "set_id": "heroine-sea-combat-v01",
        "character": {"member_id": "hero", "appearance": "female"},
        "art_status": "unapproved-heroine-sea-combat-source-poses-motion-pending",
        "art_approved": False,
        "motion_approved": False,
        "default_adoption": False,
        "note": ("Technical runtime spritesheet packed from existing separately authored poses; not creator-approved art or motion, "
                 "not a default. The authored down sequence is mapped to the required defeat action and holds its last frame."),
        "source_provenance": PROVENANCE_NAME,
        "sheet": SHEET_NAME,
        "cell_size": [CELL_W, CELL_H],
        "pivot": PIVOT,
        "authored_facing": "right",
        "logical_scale": 0.5,
        "display_proportion": "0.65",
        "actions": actions,
    }


def build_index():
    return {"schema": INDEX_SCHEMA, "sets": {"hero:female": MANIFEST_NAME}}


def build_sheet(sources):
    sheet = Image.new("RGBA", (COLUMNS * CELL_W, ROWS * CELL_H), (0, 0, 0, 0))
    for pose, index in EXPECTED_CELLS.items():
        x = (index % COLUMNS) * CELL_W
        y = (index // COLUMNS) * CELL_H
        sheet.paste(sources[pose]["source_rgba"], (x, y))
    buffer = io.BytesIO()
    sheet.save(buffer, format="PNG", optimize=False, compress_level=9)
    return sheet, buffer.getvalue()


def build_provenance(sheet_bytes, manifest_bytes, index_bytes, sources, manifest_paths, manifest_data, build_tool: Path):
    sheet_sha = sha256_bytes(sheet_bytes)
    manifest_sha = sha256_bytes(manifest_bytes)
    index_sha = sha256_bytes(index_bytes)

    source_records = []
    for pose, index in sorted(EXPECTED_CELLS.items(), key=lambda item: item[1]):
        used_by = [action for action in ACTION_ORDER if any(p == pose for p, _ in EXPECTED_SOURCE[action])]
        source_records.append({
            "cell": index,
            "cell_origin": [(index % COLUMNS) * CELL_W, (index // COLUMNS) * CELL_H],
            "pose": pose,
            "role": sources[pose]["role"],
            "used_by_actions": used_by,
            "source_png": sources[pose]["source_png"],
            "source_png_sha256": sources[pose]["source_png_sha256"],
            "source_dimensions": [CELL_W, CELL_H],
            "source_mode": "RGBA",
            "source_alpha_values": sources[pose]["source_alpha_values"],
            "native_pxo": sources[pose]["native_pxo"],
            "native_pxo_sha256": sources[pose]["native_pxo_sha256"],
            "native_ora": sources[pose]["native_ora"],
            "native_ora_sha256": sources[pose]["native_ora_sha256"],
        })

    action_records = []
    for action in ACTION_ORDER:
        frames = EXPECTED_SOURCE[action]
        ticks = EXPECTED_TICKS[action]
        record = {
            "name": action,
            "loop": action in LOOP_ACTIONS,
            "tick_rate": TICK_RATE,
            "frame_count": len(frames),
            "duration_ticks": ticks,
            "duration_seconds_fraction": "%d/%d" % (ticks, TICK_RATE),
            "frames": [
                {"index": frame_index, "pose": pose, "cell": EXPECTED_CELLS[pose], "ticks": frame_ticks}
                for frame_index, (pose, frame_ticks) in enumerate(frames)
            ],
        }
        if action in LOOP_ACTIONS:
            record["loop_start"] = LOOP_START[action]
            record["loop_cycle_ticks"] = ticks - sum(t for _, t in frames[:LOOP_START[action]])
        if action == "defeat":
            record["holds_last"] = True
        action_records.append(record)

    source_manifest_records = []
    for role in ("v01", "v02", "v03"):
        path = manifest_paths[role]
        data = manifest_data[role]
        clips = {}
        for name, clip in data["clips"].items():
            if name in ("hit", "down") and role == "v03":
                pass
            elif name in ("idle", "attack") and role != "v01":
                continue
            elif name in ("move", "guard", "dodge", "skill") and role != "v02":
                continue
            elif name in ("hit", "down") and role != "v03":
                continue
            record = {"loop": clip.get("loop")}
            if "enter" in clip:
                record["enter"] = [{"pose": f["pose"], "ticks": f["ticks"]} for f in clip["enter"]]
            if "frames" in clip:
                record["frames"] = [{"pose": f["pose"], "ticks": f["ticks"]} for f in clip["frames"]]
            if "then" in clip:
                record["then"] = clip["then"]
            if "hold" in clip:
                record["hold"] = clip["hold"]
            clips[name] = record
        source_manifest_records.append({
            "role": role,
            "path": relative(path),
            "sha256": sha256_file(path),
            "declared_tick_seconds": data.get("tickSeconds"),
            "cell": data.get("cell"),
            "pinNative": data.get("pinNative"),
            "clips": clips,
        })

    provenance = {
        "schema": PROVENANCE_SCHEMA,
        "set_id": "heroine-sea-combat-v01",
        "package_directory": PKG_REL,
        "build_reference_tag": TAG,
        "character": {"member_id": "hero", "appearance": "female"},
        "art_status": "unapproved-heroine-sea-combat-source-poses-motion-pending",
        "art_approved": False,
        "motion_approved": False,
        "default_adoption": False,
        "note": ("Technical packing evidence only. Source poses remain the authored TEST-ONLY v01/v02/v03 files; "
                 "this package is not art approval, motion approval or default adoption."),
        "packaging": {
            "method": "Pillow RGBA paste at exact cell origins; no resize, no resample, no filter, no alpha blend.",
            "pillow_version": PIL_VERSION,
            "sheet_columns": COLUMNS,
            "sheet_rows": ROWS,
            "cell_count": CELL_COUNT,
            "used_cell_count": USED_CELL_COUNT,
            "unused_cells": UNUSED_CELLS,
        },
        "sheet": {
            "file": SHEET_NAME,
            "sha256": sheet_sha,
            "width": COLUMNS * CELL_W,
            "height": ROWS * CELL_H,
            "mode": "RGBA",
            "cell_size": [CELL_W, CELL_H],
            "pivot": PIVOT,
        },
        "manifest": {"file": MANIFEST_NAME, "sha256": manifest_sha, "schema": SET_SCHEMA},
        "index": {"file": INDEX_NAME, "sha256": index_sha, "schema": INDEX_SCHEMA},
        "build_tool": {"path": relative(build_tool), "sha256": sha256_file(build_tool)},
        "source_manifests": source_manifest_records,
        "sources": source_records,
        "actions": action_records,
        "authored_durations": {
            action: {
                "ticks": EXPECTED_TICKS[action],
                "seconds_fraction": "%d/%d" % (EXPECTED_TICKS[action], TICK_RATE),
            }
            for action in ACTION_ORDER
        },
        "action_order": ACTION_ORDER,
        "frozen_counts": {
            "source_png": len(source_records),
            "native_pxo": len(source_records),
            "native_ora": len(source_records),
            "source_manifests": len(source_manifest_records),
        },
    }
    return provenance


def verify_sheet_cells(sheet: Image.Image, sources) -> None:
    require(sheet.mode == "RGBA", "sheet mode is not RGBA")
    require(sheet.size == (COLUMNS * CELL_W, ROWS * CELL_H), "sheet dimensions are not 816x720")
    used = set()
    for pose, index in EXPECTED_CELLS.items():
        used.add(index)
        origin = ((index % COLUMNS) * CELL_W, (index // COLUMNS) * CELL_H)
        cell = sheet.crop((origin[0], origin[1], origin[0] + CELL_W, origin[1] + CELL_H))
        require(cell.tobytes() == sources[pose]["source_png_bytes"],
                "packed cell does not equal source PNG RGBA bytes: " + pose)
        require(sorted(set(cell.getchannel("A").tobytes())) == sources[pose]["source_alpha_values"],
                "packed cell alpha values changed: " + pose)
    for index in UNUSED_CELLS:
        origin = ((index % COLUMNS) * CELL_W, (index // COLUMNS) * CELL_H)
        cell = sheet.crop((origin[0], origin[1], origin[0] + CELL_W, origin[1] + CELL_H))
        require(cell.getbbox() is None, "unused cell is not transparent")
        require(set(cell.getchannel("A").tobytes()) == {0}, "unused cell alpha is not zero")
    require(len(used) == USED_CELL_COUNT, "not all 29 cells are used")


def output_bytes(sources, manifest_paths, manifest_data, build_tool: Path):
    sheet, sheet_bytes = build_sheet(sources)
    verify_sheet_cells(sheet, sources)
    manifest_bytes = json_bytes(build_manifest())
    index_bytes = json_bytes(build_index())
    provenance_bytes = json_bytes(build_provenance(sheet_bytes, manifest_bytes, index_bytes, sources,
                                                   manifest_paths, manifest_data, build_tool))
    return {
        SHEET_NAME: sheet_bytes,
        MANIFEST_NAME: manifest_bytes,
        INDEX_NAME: index_bytes,
        PROVENANCE_NAME: provenance_bytes,
    }


def check_existing(outputs) -> None:
    package_dir = ROOT / PKG_REL
    require(package_dir.is_dir(), "package directory is missing")
    for name, expected in outputs.items():
        path = package_dir / name
        require(path.is_file(), "missing package file: " + name)
        require(path.read_bytes() == expected, "package bytes differ on regeneration: " + name)
    extras = sorted(path.name for path in package_dir.iterdir() if path.name not in outputs)
    require(not extras, "package directory contains unexpected files: %r" % extras)


def write_package(outputs) -> None:
    package_dir = ROOT / PKG_REL
    package_dir.mkdir(parents=True, exist_ok=True)
    allowed = set(outputs)
    extras = sorted(path.name for path in package_dir.iterdir() if path.name not in allowed)
    require(not extras, "refusing to overwrite unrelated package files: %r" % extras)
    for name, data in outputs.items():
        destination = package_dir / name
        temporary = destination.with_name(destination.name + ".tmp")
        temporary.write_bytes(data)
        os.replace(temporary, destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write the package files")
    mode.add_argument("--check", action="store_true", help="regenerate in memory and compare every package byte")
    args = parser.parse_args()

    sources, manifest_paths, manifest_data = load_sources()
    build_tool = Path(__file__).resolve()
    require(re.fullmatch(r"[a-z0-9_./-]+", relative(build_tool)), "build tool path is not lowercase")
    outputs = output_bytes(sources, manifest_paths, manifest_data, build_tool)

    if args.write:
        write_package(outputs)
        print("PACKAGE BUILD OK")
    else:
        check_existing(outputs)
        print("PACKAGE BUILD CHECK OK")
    for name, data in outputs.items():
        print("%s  %s" % (sha256_bytes(data), name))
    print("sources=%d native_pxo=%d native_ora=%d source_manifests=%d cells=%d unused=%s" % (
        len(sources), len(sources), len(sources), len(manifest_paths), USED_CELL_COUNT, UNUSED_CELLS))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BuildFailure as exc:
        print("PACKAGE BUILD FAILED: %s" % exc, file=sys.stderr)
        raise SystemExit(1)
