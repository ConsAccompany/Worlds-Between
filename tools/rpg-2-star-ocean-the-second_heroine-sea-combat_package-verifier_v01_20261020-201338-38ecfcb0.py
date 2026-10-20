#!/usr/bin/env python3
"""Independent verifier for the heroine Sea-of-Stars-direction combat package.

This script deliberately does not import the builder. It re-reads the actual v01/v02/v03
source manifests and PNGs, rebuilds the expected action/cell mapping, rebuilds the sheet
in memory and compares every decoded cell byte with the original PNG. It also validates
the schema, types, loop starts, integer-tick durations, all eight required actions,
provenance hashes and the untouched source/native files.

Usage:
  python -I <this> --report <outputs/...json>

Exit 0 only when every check passes. No Godot is run; the loader tick schema is being
implemented concurrently by the integration owner.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
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
BASE_REVISION = "11973af6492ef60a99ca1f2eacb01e12c091ccb9"

CELL_W, CELL_H = 136, 144
PIVOT = [64, 136]
COLUMNS, ROWS = 6, 5
CELL_COUNT = COLUMNS * ROWS
SET_SCHEMA = "worlds-between.combat-sprite-set/1"
INDEX_SCHEMA = "worlds-between.combat-sprite-set-index/1"
PROVENANCE_SCHEMA = "worlds-between.combat-sprite-set-provenance/1"
ACTION_ORDER = ["idle", "attack", "move", "guard", "dodge", "skill", "hit", "defeat"]
LOOP_ACTIONS = {"idle", "move", "guard"}
LOOP_START = {"idle": 0, "move": 0, "guard": 1}

SOURCE_EXPECTED = {
    "idle": [("base", 8), ("idle-b1", 6), ("idle-b2", 8), ("idle-b1", 6)],
    "attack": [
        ("atk-antic-a", 2), ("atk-antic-b", 2), ("atk-smear", 1),
        ("atk-contact", 2), ("atk-follow", 2), ("atk-recover", 2), ("idle-b1", 1),
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
EXPECTED_CELLS = {}
for _action in ACTION_ORDER:
    for _pose, _ticks in EXPECTED_SOURCE[_action]:
        if _pose not in EXPECTED_CELLS:
            EXPECTED_CELLS[_pose] = len(EXPECTED_CELLS)
EXPECTED_CELL_POSE = {cell: pose for pose, cell in EXPECTED_CELLS.items()}
EXPECTED_SOURCE_ROLE = {}
for _pose in ["base", "idle-b1", "idle-b2", "atk-antic-a", "atk-antic-b", "atk-smear", "atk-contact", "atk-follow", "atk-recover"]:
    EXPECTED_SOURCE_ROLE[_pose] = "v01"
for _pose in ["move-a", "move-b", "move-c", "move-d", "guard-a", "guard-b", "guard-c", "dodge-a", "dodge-b",
              "skill-tel-a", "skill-tel-b", "skill-strike", "skill-contact", "skill-recover"]:
    EXPECTED_SOURCE_ROLE[_pose] = "v02"
for _pose in ["hit-a", "hit-b", "hit-c", "down-a", "down-b", "down-c"]:
    EXPECTED_SOURCE_ROLE[_pose] = "v03"


class VerifyFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerifyFailure(message)


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
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def read_json(path: Path) -> dict:
    require(path.is_file(), "missing JSON: " + relative(path))
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            value = json.load(handle)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerifyFailure("invalid JSON in %s: %s" % (relative(path), exc)) from exc
    require(isinstance(value, dict), "JSON root is not an object: " + relative(path))
    return value


def one(pattern: str) -> Path:
    matches = sorted(ROOT.glob(pattern))
    require(len(matches) == 1, "expected exactly one match for %s, found %d" % (pattern, len(matches)))
    return matches[0]


def source_frames(frames, label: str) -> list[tuple[str, int]]:
    require(isinstance(frames, list) and frames, label + " must be a non-empty list")
    result = []
    for frame in frames:
        require(isinstance(frame, dict), label + " frame must be an object")
        require(isinstance(frame.get("pose"), str) and frame["pose"], label + " pose must be a string")
        require(is_int(frame.get("ticks")) and frame["ticks"] > 0, label + " ticks must be a positive integer")
        result.append((frame["pose"], frame["ticks"]))
    return result


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )
    require(completed.returncode == 0, "git %s failed: %s" % (" ".join(args), completed.stderr.strip()))
    return completed.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, help="QA report JSON to write")
    parser.add_argument("--package-dir", default=PKG_REL, help="package directory (defaults to the checked package)")
    args = parser.parse_args()

    checks: list[dict] = []
    failures: list[str] = []
    limitations = [
        "No Godot run: the loader tick_rate/loop_start implementation is concurrent and is not in this checkout at verification time; coordinator must run the combined loader/game path.",
        "Technical packing only. Art and motion are not creator-approved; this package is not a default and does not change default adoption.",
        "The requested explicit one-tick base tail makes attack 13/30 s, dodge 9/30 s, skill 14/30 s and hit 8/30 s, versus the shorter source clips/arena visual durations; the source clips were not reauthored.",
        "Sheet RGBA bytes are exact and the unused cell is transparent. Runtime texture filtering/import settings are integration concerns; nearest sampling is required to preserve hard alpha and avoid sampling neighbours.",
        "The v01/v02/v03 source manifests are TEST-ONLY authored-motion evidence. The base still is the source referenced by v01's approved static baseline; this verifier does not grant any new approval.",
        "No commit, staging, ledger, Bible, Site, registry, account or billing change was made.",
    ]

    def check(check_id: str, condition: bool, detail: str) -> None:
        entry = {"id": check_id, "pass": bool(condition), "detail": detail}
        checks.append(entry)
        if not condition:
            failures.append(check_id)

    package_dir = Path(args.package_dir)
    if not package_dir.is_absolute():
        package_dir = ROOT / package_dir
    sheet_path = package_dir / SHEET_NAME
    manifest_path = package_dir / MANIFEST_NAME
    index_path = package_dir / INDEX_NAME
    provenance_path = package_dir / PROVENANCE_NAME
    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = ROOT / report_path

    provenance = None
    manifest = None
    index = None
    sheet = None
    sources = {}
    source_manifest_data = {}
    source_manifest_paths = {}

    try:
        require(package_dir.is_dir(), "package directory is missing")
        require(sheet_path.is_file(), "sheet is missing")
        require(manifest_path.is_file(), "manifest is missing")
        require(index_path.is_file(), "index is missing")
        require(provenance_path.is_file(), "provenance manifest is missing")

        expected_files = {SHEET_NAME, MANIFEST_NAME, INDEX_NAME, PROVENANCE_NAME}
        present_files = {path.name for path in package_dir.iterdir() if path.is_file()}
        check("package_file_set", present_files == expected_files,
              "package contains exactly the four expected files; present=%s" % sorted(present_files))

        index = read_json(index_path)
        manifest = read_json(manifest_path)
        provenance = read_json(provenance_path)
        source_manifest_paths = {
            "v01": one("outputs/hero-sea-motion-v01/*_manifest_test-only-v01_*.json"),
            "v02": one("outputs/hero-sea-motion-v02/*_manifest_test-only-v02_*.json"),
            "v03": one("outputs/hero-sea-motion-v03/*_manifest_test-only-v03_*.json"),
        }
        source_manifest_data = {role: read_json(path) for role, path in source_manifest_paths.items()}

        # ---- index ----
        check("index_schema", index.get("schema") == INDEX_SCHEMA, "index schema is %r" % index.get("schema"))
        sets = index.get("sets")
        check("index_sets", isinstance(sets, dict) and list(sets.keys()) == ["hero:female"],
              "index sets must be exactly one hero:female key")
        mapped = sets.get("hero:female") if isinstance(sets, dict) else None
        check("index_relative_manifest", isinstance(mapped, str) and mapped == MANIFEST_NAME and "/" not in mapped and "\\" not in mapped and ".." not in mapped,
              "index maps hero:female to the adjacent relative manifest name")
        check("index_manifest_resolves", (package_dir / str(mapped)).is_file() if isinstance(mapped, str) else False,
              "index manifest path resolves next to the index")

        # ---- manifest metadata ----
        check("manifest_schema", manifest.get("schema") == SET_SCHEMA, "manifest schema is %r" % manifest.get("schema"))
        check("manifest_set_id", isinstance(manifest.get("set_id"), str) and manifest["set_id"] == "heroine-sea-combat-v01",
              "set_id is the package identity")
        character = manifest.get("character")
        check("manifest_character", character == {"member_id": "hero", "appearance": "female"},
              "character is hero/female")
        check("manifest_art_unapproved", manifest.get("art_approved") is False and manifest.get("motion_approved") is False,
              "art_approved=false and motion_approved=false")
        check("manifest_not_default", manifest.get("default_adoption") is False, "default_adoption=false")
        check("manifest_art_status", isinstance(manifest.get("art_status"), str) and "unapproved" in manifest["art_status"],
              "art_status explicitly unapproved / motion pending")
        check("manifest_sheet_relative", manifest.get("sheet") == SHEET_NAME and "/" not in str(manifest.get("sheet")) and "\\" not in str(manifest.get("sheet")),
              "sheet is the adjacent relative spritesheet name")
        check("manifest_provenance_relative", manifest.get("source_provenance") == PROVENANCE_NAME,
              "source provenance is the adjacent relative file name")
        check("manifest_cell", manifest.get("cell_size") == [CELL_W, CELL_H], "cell_size is [136,144]")
        check("manifest_pivot", manifest.get("pivot") == PIVOT, "pivot is [64,136]")
        check("manifest_pivot_even", PIVOT[0] % 2 == 0 and PIVOT[1] % 2 == 0, "0.5-scale pivot is even")
        check("manifest_facing", manifest.get("authored_facing") == "right", "authored_facing is right")
        check("manifest_scale", manifest.get("logical_scale") == 0.5 and not isinstance(manifest.get("logical_scale"), bool),
              "logical_scale is numeric 0.5")
        check("manifest_proportion", manifest.get("display_proportion") == "0.65", "display_proportion is the string '0.65'")

        # ---- actions ----
        actions = manifest.get("actions")
        require(isinstance(actions, dict), "manifest actions must be an object")
        check("actions_order", list(actions.keys()) == ACTION_ORDER, "action order is %s" % ACTION_ORDER)
        check("actions_all_eight", len(actions) == 8 and set(actions.keys()) == set(ACTION_ORDER), "all eight required actions present")
        check("defeat_maps_down", "defeat" in actions and "down" not in actions, "authored down is mapped to the required defeat action")
        observed_cells: dict[int, list[str]] = {}
        all_used_cells = set()
        for action in ACTION_ORDER:
            entry = actions.get(action)
            require(isinstance(entry, dict), "action %s must be an object" % action)
            check("action_%s_keys" % action, set(entry.keys()) <= {"loop", "loop_start", "tick_rate", "frames"},
                  "action %s uses only loop/loop_start/tick_rate/frames" % action)
            check("action_%s_loop" % action, entry.get("loop") is (action in LOOP_ACTIONS), "action %s loop flag" % action)
            check("action_%s_tick_rate" % action, is_int(entry.get("tick_rate")) and entry.get("tick_rate") == 30,
                  "action %s tick_rate is integer 30" % action)
            if action in LOOP_ACTIONS:
                check("action_%s_loop_start" % action, is_int(entry.get("loop_start")) and entry.get("loop_start") == LOOP_START[action],
                      "action %s loop_start is %d" % (action, LOOP_START[action]))
            else:
                check("action_%s_no_loop_start" % action, "loop_start" not in entry, "non-loop action %s has no loop_start" % action)
            frames = entry.get("frames")
            require(isinstance(frames, list) and frames, "action %s frames must be a non-empty list" % action)
            check("action_%s_frame_count" % action, len(frames) == len(EXPECTED_SOURCE[action]),
                  "action %s has %d frames" % (action, len(EXPECTED_SOURCE[action])))
            if len(frames) != len(EXPECTED_SOURCE[action]):
                continue
            observed_ticks = sum(frame["ticks"] for frame in frames
                                 if isinstance(frame, dict) and is_int(frame.get("ticks")))
            check("action_%s_duration_ticks" % action, observed_ticks == EXPECTED_TICKS[action],
                  "action %s totals %d integer ticks" % (action, EXPECTED_TICKS[action]))
            for frame_index, (pose, ticks) in enumerate(EXPECTED_SOURCE[action]):
                frame = frames[frame_index]
                require(isinstance(frame, dict), "action %s frame %d must be an object" % (action, frame_index))
                check("frame_%s_%d_keys" % (action, frame_index), set(frame.keys()) == {"cell", "ticks"},
                      "frame uses exactly cell+ticks (no ms) at %s[%d]" % (action, frame_index))
                check("frame_%s_%d_cell" % (action, frame_index), is_int(frame.get("cell")) and frame.get("cell") == EXPECTED_CELLS[pose],
                      "%s[%d] cell is %d for %s" % (action, frame_index, EXPECTED_CELLS[pose], pose))
                check("frame_%s_%d_ticks" % (action, frame_index), is_int(frame.get("ticks")) and frame.get("ticks") == ticks,
                      "%s[%d] is %d ticks for %s" % (action, frame_index, ticks, pose))
                cell = frame.get("cell")
                if is_int(cell):
                    all_used_cells.add(cell)
                    observed_cells.setdefault(cell, []).append("%s[%d]" % (action, frame_index))
        check("cells_all_29_used", all_used_cells == set(range(29)), "all 29 effective cells are referenced")
        check("cells_no_unused_reference", 29 not in all_used_cells, "the transparent unused cell is not referenced")
        check("cells_unique_count", len(EXPECTED_CELLS) == 29, "cell map has 29 distinct poses")
        check("base_reused", len(observed_cells.get(0, [])) == 5, "base cell is used by idle/attack/dodge/skill/hit")
        check("guard_pattern", actions["guard"]["frames"] == [
            {"cell": EXPECTED_CELLS["guard-a"], "ticks": 2},
            {"cell": EXPECTED_CELLS["guard-b"], "ticks": 6},
            {"cell": EXPECTED_CELLS["guard-c"], "ticks": 6},
        ] and actions["guard"]["loop_start"] == 1, "guard-a2,guard-b6,guard-c6 with loop_start 1 intro-once")
        check("attack_tail", actions["attack"]["frames"][-2:] == [
            {"cell": EXPECTED_CELLS["idle-b1"], "ticks": 1},
            {"cell": EXPECTED_CELLS["base"], "ticks": 1},
        ], "v01 attack keeps final idle-b1 then one base tick")
        check("dodge_tail", actions["dodge"]["frames"][-1] == {"cell": EXPECTED_CELLS["base"], "ticks": 1}, "dodge ends with base 1 tick")
        check("hit_tail", actions["hit"]["frames"][-1] == {"cell": EXPECTED_CELLS["base"], "ticks": 1}, "hit ends with base 1 tick")
        check("skill_tail", actions["skill"]["frames"][-1] == {"cell": EXPECTED_CELLS["base"], "ticks": 1}, "skill ends with base 1 tick")
        check("defeat_hold", actions["defeat"]["loop"] is False and actions["defeat"]["frames"][-1]["cell"] == EXPECTED_CELLS["down-c"],
              "defeat is one-shot and holds the final down-c cell")

        # ---- source manifests and files ----
        provenance_manifests = provenance.get("source_manifests")
        require(isinstance(provenance_manifests, list) and len(provenance_manifests) == 3, "provenance must list three source manifests")
        for record in provenance_manifests:
            role = record.get("role")
            require(role in source_manifest_paths, "unexpected provenance source role")
            path = source_manifest_paths[role]
            check("source_manifest_%s_path" % role, record.get("path") == relative(path), "%s manifest path matches" % role)
            check("source_manifest_%s_sha" % role, record.get("sha256") == sha256_file(path), "%s manifest SHA-256 matches" % role)

        v1 = source_manifest_data["v01"]
        v2 = source_manifest_data["v02"]
        v3 = source_manifest_data["v03"]
        for role, manifest_data in (("v01", v1), ("v02", v2), ("v03", v3)):
            check("source_%s_cell" % role, manifest_data.get("cell") == [CELL_W, CELL_H], "%s source cell is 136x144" % role)
            check("source_%s_pin" % role, manifest_data.get("pinNative") == PIVOT, "%s source pin is 64/136" % role)
        raw_frames = {
            "idle": source_frames(v1["clips"]["idle"]["frames"], "v01 idle"),
            "attack": source_frames(v1["clips"]["attack"]["frames"], "v01 attack"),
            "move": source_frames(v2["clips"]["move"]["frames"], "v02 move"),
            "guard": source_frames(v2["clips"]["guard"]["enter"], "v02 guard enter") + source_frames(v2["clips"]["guard"]["frames"], "v02 guard loop"),
            "dodge": source_frames(v2["clips"]["dodge"]["frames"], "v02 dodge"),
            "skill": source_frames(v2["clips"]["skill"]["frames"], "v02 skill"),
            "hit": source_frames(v3["clips"]["hit"]["frames"], "v03 hit"),
            "defeat": source_frames(v3["clips"]["down"]["frames"], "v03 down"),
        }
        check("source_frames_exact", all(raw_frames[action] == SOURCE_EXPECTED[action] for action in ACTION_ORDER),
              "actual v01/v02/v03 frame ticks match the checked source sequences")
        check("source_flags", v1["clips"]["idle"].get("loop") is True and v1["clips"]["attack"].get("then") == "base"
              and v2["clips"]["move"].get("loop") is True and v2["clips"]["guard"].get("loop") is True
              and v2["clips"]["dodge"].get("then") == "base" and v2["clips"]["skill"].get("then") == "base"
              and v3["clips"]["hit"].get("then") == "base" and v3["clips"]["down"].get("hold") is True,
              "source loop/then/hold flags match the runtime mapping")

        base_info = v1["poseFiles"]["base"]
        base_path = ROOT / base_info["path"]
        check("base_source_path", base_info.get("path", "").startswith("outputs/hero-sea-v01/")
              and "battle_still-native136" in Path(base_info["path"]).name and "1294c865" in Path(base_info["path"]).name,
              "base is the approved outputs/hero-sea-v01 native136 1294c865 still")
        check("base_source_sha", base_info.get("sha256") == "4ce65a7915c0c0270a4ca353152b45b7d68b42672cb1483dd4f3e9cf4ac9d5e6"
              and base_path.is_file() and sha256_file(base_path) == base_info["sha256"],
              "base source SHA-256 is frozen and unchanged")

        provenance_sources = provenance.get("sources")
        require(isinstance(provenance_sources, list) and len(provenance_sources) == 29, "provenance must list 29 sources")
        provenance_by_cell = {record.get("cell"): record for record in provenance_sources}
        check("provenance_cells", set(provenance_by_cell.keys()) == set(range(29)), "provenance cell map covers 0..28")

        for pose, cell in EXPECTED_CELLS.items():
            role = EXPECTED_SOURCE_ROLE[pose]
            if role == "v01":
                if pose == "base":
                    png_path = base_path
                    png_sha = base_info["sha256"]
                    pxo_path = one("outputs/hero-sea-v01/*battle_still-editable*.pxo")
                    ora_path = one("outputs/hero-sea-v01/*battle_still-layered*.ora")
                else:
                    info = v1["poseFiles"][pose]
                    png_path = ROOT / "outputs/hero-sea-motion-v01" / info["name"]
                    png_sha = info["sha256"]
                    pxo_path = ROOT / "outputs/hero-sea-motion-v01" / v1["files"][pose + ".pxo"]["name"]
                    ora_path = ROOT / "outputs/hero-sea-motion-v01" / v1["files"][pose + ".ora"]["name"]
                pxo_sha = sha256_file(pxo_path)
                ora_sha = sha256_file(ora_path)
            elif role == "v02":
                info = v2["files"][pose + ".png"]
                png_path = ROOT / "outputs/hero-sea-motion-v02" / info["name"]
                png_sha = info["sha256"]
                pxo_path = ROOT / "outputs/hero-sea-motion-v02" / v2["files"][pose + ".pxo"]["name"]
                ora_path = ROOT / "outputs/hero-sea-motion-v02" / v2["files"][pose + ".ora"]["name"]
                pxo_sha = v2["files"][pose + ".pxo"]["sha256"]
                ora_sha = v2["files"][pose + ".ora"]["sha256"]
            else:
                info = v3["files"][pose + ".png"]
                png_path = ROOT / "outputs/hero-sea-motion-v03" / info["name"]
                png_sha = info["sha256"]
                pxo_path = ROOT / "outputs/hero-sea-motion-v03" / v3["files"][pose + ".pxo"]["name"]
                ora_path = ROOT / "outputs/hero-sea-motion-v03" / v3["files"][pose + ".ora"]["name"]
                pxo_sha = v3["files"][pose + ".pxo"]["sha256"]
                ora_sha = v3["files"][pose + ".ora"]["sha256"]

            check("source_%s_role" % pose, role in png_path.as_posix(), "%s uses the %s source" % (pose, role))
            check("source_%s_png_sha" % pose, png_path.is_file() and sha256_file(png_path) == png_sha,
                  "%s PNG SHA-256 matches its source manifest" % pose)
            check("source_%s_native_pxo" % pose, pxo_path.is_file() and sha256_file(pxo_path) == pxo_sha,
                  "%s native PXO exists and is unchanged" % pose)
            check("source_%s_native_ora" % pose, ora_path.is_file() and sha256_file(ora_path) == ora_sha,
                  "%s native ORA exists and is unchanged" % pose)
            with Image.open(png_path) as opened:
                opened.load()
                check("source_%s_format" % pose, opened.format == "PNG" and opened.size == (CELL_W, CELL_H) and opened.mode == "RGBA",
                      "%s is exact 136x144 RGBA PNG" % pose)
                rgba = opened.convert("RGBA")
                raw = rgba.tobytes()
                alpha_values = sorted(set(rgba.getchannel("A").tobytes()))
            sources[pose] = {"path": png_path, "raw": raw, "rgba": rgba, "alpha_values": alpha_values, "sha256": png_sha,
                             "pxo": pxo_path, "ora": ora_path, "pxo_sha": pxo_sha, "ora_sha": ora_sha}

            record = provenance_by_cell.get(cell, {})
            check("prov_%s_pose" % pose, record.get("pose") == pose, "%s provenance pose matches cell %d" % (pose, cell))
            check("prov_%s_source" % pose, record.get("source_png") == relative(png_path) and record.get("source_png_sha256") == png_sha,
                  "%s provenance source path/SHA match" % pose)
            check("prov_%s_native" % pose, record.get("native_pxo") == relative(pxo_path) and record.get("native_pxo_sha256") == pxo_sha
                  and record.get("native_ora") == relative(ora_path) and record.get("native_ora_sha256") == ora_sha,
                  "%s provenance PXO/ORA path/SHA match" % pose)
            expected_users = [action for action in ACTION_ORDER if any(p == pose for p, _ in EXPECTED_SOURCE[action])]
            check("prov_%s_users" % pose, record.get("used_by_actions") == expected_users, "%s provenance action users match" % pose)

        check("native_counts", len({record["native_pxo"] for record in provenance_sources}) == 29
              and len({record["native_ora"] for record in provenance_sources}) == 29,
              "29 distinct PXO and 29 distinct ORA sources")
        check("source_manifest_count", len(provenance_manifests) == 3, "three source manifests frozen")
        check("provenance_frozen_counts", provenance.get("frozen_counts") == {
            "source_png": 29, "native_pxo": 29, "native_ora": 29, "source_manifests": 3,
        }, "provenance frozen counts are 29/29/29/3")

        # ---- provenance actions / durations / hashes ----
        check("provenance_schema", provenance.get("schema") == PROVENANCE_SCHEMA, "provenance schema")
        check("provenance_identity", provenance.get("set_id") == "heroine-sea-combat-v01"
              and provenance.get("character") == {"member_id": "hero", "appearance": "female"}, "provenance identity")
        check("provenance_unapproved", provenance.get("art_approved") is False and provenance.get("motion_approved") is False
              and provenance.get("default_adoption") is False, "provenance records no approval/default")
        check("provenance_packaging", provenance.get("packaging", {}).get("cell_count") == 30
              and provenance.get("packaging", {}).get("used_cell_count") == 29
              and provenance.get("packaging", {}).get("unused_cells") == [29], "packaging grid records 30 cells, 29 used, unused [29]")
        check("provenance_action_order", provenance.get("action_order") == ACTION_ORDER, "provenance action order")
        prov_actions = provenance.get("actions")
        require(isinstance(prov_actions, list) and len(prov_actions) == 8, "provenance must list eight actions")
        for action, record in zip(ACTION_ORDER, prov_actions):
            check("prov_action_%s_name" % action, record.get("name") == action, "provenance action %s" % action)
            check("prov_action_%s_ticks" % action, record.get("duration_ticks") == EXPECTED_TICKS[action]
                  and record.get("duration_seconds_fraction") == "%d/30" % EXPECTED_TICKS[action],
                  "%s provenance duration is %d/30" % (action, EXPECTED_TICKS[action]))
            check("prov_action_%s_frames" % action, record.get("frames") == [
                {"index": i, "pose": pose, "cell": EXPECTED_CELLS[pose], "ticks": ticks}
                for i, (pose, ticks) in enumerate(EXPECTED_SOURCE[action])
            ], "%s provenance frame map" % action)
        check("provenance_durations", provenance.get("authored_durations") == {
            action: {"ticks": EXPECTED_TICKS[action], "seconds_fraction": "%d/30" % EXPECTED_TICKS[action]}
            for action in ACTION_ORDER
        }, "provenance authored durations are exact integer ticks/30")

        sheet_sha = sha256_file(sheet_path)
        manifest_sha = sha256_file(manifest_path)
        index_sha = sha256_file(index_path)
        check("provenance_sheet_sha", provenance.get("sheet", {}).get("file") == SHEET_NAME
              and provenance.get("sheet", {}).get("sha256") == sheet_sha, "provenance sheet SHA matches")
        check("provenance_manifest_sha", provenance.get("manifest", {}).get("file") == MANIFEST_NAME
              and provenance.get("manifest", {}).get("sha256") == manifest_sha, "provenance manifest SHA matches")
        check("provenance_index_sha", provenance.get("index", {}).get("file") == INDEX_NAME
              and provenance.get("index", {}).get("sha256") == index_sha, "provenance index SHA matches")
        build_tool = ROOT / provenance.get("build_tool", {}).get("path", "")
        check("provenance_build_tool", build_tool.is_file() and provenance.get("build_tool", {}).get("sha256") == sha256_file(build_tool),
              "provenance build-tool SHA matches")

        # ---- sheet bytes ----
        with Image.open(sheet_path) as opened:
            opened.load()
            check("sheet_format", opened.format == "PNG" and opened.mode == "RGBA" and opened.size == (COLUMNS * CELL_W, ROWS * CELL_H),
                  "sheet is an 816x720 RGBA PNG")
            sheet = opened.convert("RGBA")
        check("sheet_sha", sha256_bytes(sheet_path.read_bytes()) == sheet_sha and sheet_sha == provenance.get("sheet", {}).get("sha256"),
              "sheet file SHA-256 is stable")
        check("sheet_multiple", sheet.width % CELL_W == 0 and sheet.height % CELL_H == 0, "sheet dimensions are exact cell multiples")

        rebuilt = Image.new("RGBA", (COLUMNS * CELL_W, ROWS * CELL_H), (0, 0, 0, 0))
        for pose, cell in EXPECTED_CELLS.items():
            rebuilt.paste(sources[pose]["rgba"], ((cell % COLUMNS) * CELL_W, (cell // COLUMNS) * CELL_H))
        check("sheet_independent_rebuild", rebuilt.tobytes() == sheet.tobytes(), "independent RGBA rebuild equals the sheet")
        for pose, cell in EXPECTED_CELLS.items():
            origin = ((cell % COLUMNS) * CELL_W, (cell // COLUMNS) * CELL_H)
            packed = sheet.crop((origin[0], origin[1], origin[0] + CELL_W, origin[1] + CELL_H))
            check("cell_%s_bytes" % pose, packed.tobytes() == sources[pose]["raw"],
                  "%s cell is byte-for-byte equal to the source PNG's decoded RGBA" % pose)
            check("cell_%s_alpha" % pose, sorted(set(packed.getchannel("A").tobytes())) == sources[pose]["alpha_values"],
                  "%s cell preserves the source alpha set" % pose)
        unused = sheet.crop(((29 % COLUMNS) * CELL_W, (29 // COLUMNS) * CELL_H,
                             (29 % COLUMNS) * CELL_W + CELL_W, (29 // COLUMNS) * CELL_H + CELL_H))
        check("unused_cell_transparent", unused.getbbox() is None and set(unused.getchannel("A").tobytes()) == {0},
              "cell 29 is fully transparent")
        check("sheet_alpha_hard", set(sheet.getchannel("A").tobytes()) <= {0, 255},
              "sheet alpha contains only 0/255, no partial-alpha blend")
        check("cell_bleed", all(sheet.crop(((cell % COLUMNS) * CELL_W, (cell // COLUMNS) * CELL_H,
                                            (cell % COLUMNS) * CELL_W + CELL_W, (cell // COLUMNS) * CELL_H + CELL_H)).tobytes() == sources[pose]["raw"]
                                 for pose, cell in EXPECTED_CELLS.items()),
              "every cell region exactly matches its own source (no packing bleed)")

        # ---- repository scope ----
        head = git("rev-parse", "HEAD")
        check("base_revision", head == BASE_REVISION, "checkout HEAD is the assigned base 11973af")
        status = git("status", "--porcelain")
        tracked_changes = [line for line in status.splitlines() if not line.startswith("??")]
        check("no_tracked_changes", not tracked_changes, "git status has no tracked/staged changes")
        allowed_prefixes = (
            "game/data/heroine-sea-combat-v01/",
            "tools/rpg-2-star-ocean-the-second_heroine-sea-combat_package-builder_",
            "tools/rpg-2-star-ocean-the-second_heroine-sea-combat_package-verifier_",
            "outputs/heroine-sea-combat-v01/",
        )
        untracked = [line[3:] for line in status.splitlines() if line.startswith("??")]
        unexpected_untracked = [path for path in untracked if not path.startswith(allowed_prefixes)]
        check("scope_untracked", not unexpected_untracked, "all untracked paths are the new package/tools/QA scope")
        check("no_staged_changes", not git("diff", "--cached", "--name-only"), "git index is untouched")
        check("no_unstaged_tracked_changes", not git("diff", "--name-only"), "no tracked working file changed")
        loader = ROOT / "game/scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd"
        battle = ROOT / "game/scripts/battle_arena.gd"
        check("existing_loader_present", loader.is_file() and battle.is_file(), "existing loader and battle code are present and untouched")

        verdict = "pass" if not failures else "fail"
        report = {
            "schema": "worlds-between.combat-sprite-set-verification/1",
            "verdict": verdict,
            "checked_at_utc": datetime.now(timezone.utc).isoformat(),
            "base_revision": BASE_REVISION,
            "python": sys.version.split()[0],
            "pillow": PIL_VERSION,
            "platform": platform.platform(),
            "package": {
                "directory": Path(args.package_dir).as_posix(),
                "sheet": {"file": SHEET_NAME, "sha256": sheet_sha, "size": [sheet.width, sheet.height]},
                "manifest": {"file": MANIFEST_NAME, "sha256": manifest_sha},
                "index": {"file": INDEX_NAME, "sha256": index_sha},
                "provenance": {"file": PROVENANCE_NAME, "sha256": sha256_file(provenance_path)},
                "verifier": {"file": relative(Path(__file__).resolve()), "sha256": sha256_file(Path(__file__).resolve())},
            },
            "checks": checks,
            "failed_checks": failures,
            "actions": [
                {"name": action, "ticks": EXPECTED_TICKS[action], "seconds_fraction": "%d/30" % EXPECTED_TICKS[action],
                 "loop": action in LOOP_ACTIONS, "loop_start": LOOP_START.get(action)}
                for action in ACTION_ORDER
            ],
            "cells": [
                {"cell": cell, "pose": pose, "origin": [(cell % COLUMNS) * CELL_W, (cell // COLUMNS) * CELL_H],
                 "source_png": relative(sources[pose]["path"]), "source_png_sha256": sources[pose]["sha256"]}
                for pose, cell in sorted(EXPECTED_CELLS.items(), key=lambda item: item[1])
            ],
            "art_approved": False,
            "motion_approved": False,
            "default_adoption": False,
            "limitations": limitations,
        }
    except VerifyFailure as exc:
        failures.append("verifier_failure")
        checks.append({"id": "verifier_failure", "pass": False, "detail": str(exc)})
        report = {
            "schema": "worlds-between.combat-sprite-set-verification/1",
            "verdict": "fail",
            "checked_at_utc": datetime.now(timezone.utc).isoformat(),
            "base_revision": BASE_REVISION,
            "package": {"directory": Path(args.package_dir).as_posix()},
            "checks": checks,
            "failed_checks": failures,
            "art_approved": False,
            "motion_approved": False,
            "default_adoption": False,
            "limitations": limitations,
        }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    if report["verdict"] != "pass":
        print("PACKAGE VERIFY FAILED: %s" % ", ".join(failures), file=sys.stderr)
        return 1
    print("PACKAGE VERIFY OK")
    print("sheet_sha256=%s" % report["package"]["sheet"]["sha256"])
    print("manifest_sha256=%s" % report["package"]["manifest"]["sha256"])
    print("index_sha256=%s" % report["package"]["index"]["sha256"])
    print("checks=%d cells=%d actions=%d" % (len(checks), len(EXPECTED_CELLS), len(ACTION_ORDER)))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VerifyFailure as exc:
        print("PACKAGE VERIFY FAILED: %s" % exc, file=sys.stderr)
        raise SystemExit(1)
