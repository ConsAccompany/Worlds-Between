#!/usr/bin/env python3
"""Independent validator for Worlds Between runtime combat sprite-set manifests.

Reads ONLY the target manifest named by --manifest and the PNG it references.
It does not read the set index, import project code, or mutate source art.
Writes a JSON report to --out and exits 0 only when every predicate passes.

CLI:
  python <this-file> --manifest runtime-spritesheet-manifest.json --out report.json
  python <this-file> --self-test

Self-test builds tiny temporary fixtures (never project images) for a valid set
plus mismatch/missing-action/zero-tick/blank-cell/bool-tick/missing-PNG/bad-SHA
malformed cases.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import traceback
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    Image = None
    PIL_IMPORT_ERROR = str(exc)
else:
    PIL_IMPORT_ERROR = ""

SET_SCHEMA = "worlds-between.combat-sprite-set/1"
DISPLAY_PROPORTION = "0.65"
AUTHORED_FACINGS = ("left", "right")
SUPPORTED_SCALES = (1.0, 0.5)
# All eight canonical actions are required for production, including skill.
CANONICAL_ACTIONS = {
    "idle": True,
    "move": True,
    "guard": True,
    "attack": False,
    "dodge": False,
    "hit": False,
    "defeat": False,
    "skill": False,
}
MAX_TICK_RATE = 1000
MAX_FRAME_UNITS = 2147483647
SUPPORTED_IMAGE_MODES = {"1", "L", "LA", "P", "RGB", "RGBA"}
LIMITATIONS = [
    "Static schema, geometry and pixel checks only; no Godot import/load, playback timing, motion fluidity, art quality or human acceptance is claimed.",
    "Reads only --manifest and its declared PNG; set-index membership and the loader's external set key are not validated.",
    "Tick/timing values must be exact JSON integers; integral floats (which the GDScript loader tolerates) are rejected as malformed rather than silently coerced.",
    "Only a declared top-level sheet_sha256 is verified; when absent no hash field is invented. Other sha-looking fields are reported but not guessed as sheet bindings.",
    "Non-empty means at least one alpha>0 pixel in the referenced cell; palette indices and alpha extrema are checked inside the declared cell bounds.",
    "Text hashes bind raw file bytes with no normalization. PNG decode uses Pillow; engine import/compression settings are outside this checker.",
]


class Report:
    def __init__(self) -> None:
        self.checks: list[dict] = []
        self.failures: list[str] = []

    def add(self, check_id: str, ok: bool, detail: str) -> bool:
        self.checks.append({"id": check_id, "ok": bool(ok), "detail": detail})
        if not ok:
            self.failures.append(f"{check_id}: {detail}")
        return bool(ok)

    def fail(self, check_id: str, detail: str) -> None:
        self.add(check_id, False, detail)


def is_int(value: object) -> bool:
    """Exact JSON integer. bool is a subclass of int and is explicitly rejected."""
    return type(value) is int


def is_number(value: object) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float))


def vec2(value: object) -> tuple[int, int] | None:
    if not isinstance(value, list) or len(value) != 2:
        return None
    if not all(is_int(part) for part in value):
        return None
    return (value[0], value[1])


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_sheet(manifest_path: Path, sheet: str) -> Path:
    if sheet.startswith("res://"):
        rest = sheet[len("res://"):]
        for parent in (manifest_path.parent, *manifest_path.parent.parents):
            if (parent / "project.godot").is_file():
                return parent / rest
        return manifest_path.parent / rest
    candidate = Path(sheet)
    return candidate if candidate.is_absolute() else manifest_path.parent / candidate


def palette_problem(image: "Image.Image") -> str | None:
    if image.mode != "P":
        return None
    palette = image.getpalette()
    if not palette:
        return "P-mode PNG has no palette"
    colors = len(palette) // 3
    if colors <= 0:
        return "P-mode PNG palette has no colors"
    raw = list(image.get_flattened_data()) if hasattr(image, "get_flattened_data") else list(image.getdata())
    bad = sum(1 for index in raw if index >= colors)
    if bad:
        return f"{bad} pixel index(es) outside palette range 0..{colors - 1}"
    transparency = image.info.get("transparency")
    if isinstance(transparency, int) and not 0 <= transparency < colors:
        return f"transparency index {transparency} outside palette range 0..{colors - 1}"
    if isinstance(transparency, (tuple, list)) and len(transparency) != 3:
        return "tRNS transparency key must be one index or an RGB triple"
    return None


def cell_pixel_facts(image_rgba: "Image.Image", cell: tuple[int, int, int, int]) -> dict:
    alpha = image_rgba.crop(cell).getchannel("A")
    amin, amax = alpha.getextrema()
    histogram = alpha.histogram()
    opaque = int(sum(histogram[1:]))
    return {
        "alpha_min": int(amin),
        "alpha_max": int(amax),
        "opaque_pixels": opaque,
        "bbox_alpha_gt0": list(alpha.getbbox()) if alpha.getbbox() else None,
    }


def validate(manifest_path: Path, out_path: Path | None = None) -> tuple[int, dict]:
    report = Report()
    result: dict = {
        "tool": "worlds-between-combat-runtime-spritesheet-validator",
        "tool_path": str(Path(__file__).resolve()),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "input_mode": "read-only manifest+sheet; the only write is --out",
        "manifest": {"path": str(manifest_path)},
        "sheet": {},
        "sha_fields_observed": [],
        "target_contract": {},
        "checks": report.checks,
        "failed_predicates": report.failures,
        "limitations": LIMITATIONS,
    }

    if Image is None:
        report.fail("runtime.pillow", f"Pillow unavailable: {PIL_IMPORT_ERROR}")
        return finish(report, result, out_path)

    try:
        raw = manifest_path.read_bytes()
    except OSError as exc:
        report.fail("input.manifest_readable", f"cannot read {manifest_path}: {exc}")
        return finish(report, result, out_path)

    manifest_sha = hashlib.sha256(raw).hexdigest()
    result["manifest"]["sha256"] = manifest_sha
    result["manifest"]["bytes"] = len(raw)
    report.add("input.manifest_readable", True, f"read {len(raw)} bytes; sha256={manifest_sha}")

    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        report.fail("manifest.valid_json", f"UTF-8 JSON parse failed: {exc}")
        return finish(report, result, out_path)
    if not isinstance(data, dict):
        report.fail("manifest.object", f"top-level JSON must be an object; got {type(data).__name__}")
        return finish(report, result, out_path)

    report.add("manifest.schema", data.get("schema") == SET_SCHEMA,
               f"expected {SET_SCHEMA!r}; got {data.get('schema')!r}")

    # Character identity: a valid, non-empty member id; hero must name an appearance.
    member_id = None
    character = data.get("character")
    if not isinstance(character, dict):
        report.fail("character.object", f"character must be an object; got {type(character).__name__}")
    else:
        member_id = character.get("member_id")
        identity_ok = isinstance(member_id, str) and member_id.strip() != ""
        report.add("character.member_id", identity_ok,
                   f"member_id must be a non-empty string; got {member_id!r}")
        appearance = character.get("appearance")
        if "appearance" in character:
            report.add("character.appearance_type", isinstance(appearance, str),
                       f"appearance must be a string when present; got {appearance!r}")
        if member_id == "hero":
            report.add("character.hero_appearance", appearance in ("male", "female"),
                       f"hero requires appearance male/female; got {appearance!r}")

    # Scale / display proportion / facing.
    scale_value = data.get("logical_scale")
    scale_ok = is_number(scale_value) and float(scale_value) in SUPPORTED_SCALES
    report.add("manifest.logical_scale", scale_ok,
               f"logical_scale must be exactly 1 or 0.5 (bool rejected); got {scale_value!r}")
    scale = float(scale_value) if scale_ok else None
    half_scale = scale == 0.5

    report.add("manifest.display_proportion", data.get("display_proportion") == DISPLAY_PROPORTION,
               f"display_proportion must be exactly {DISPLAY_PROPORTION!r}; got {data.get('display_proportion')!r}")
    facing = data.get("authored_facing")
    report.add("manifest.authored_facing", facing in AUTHORED_FACINGS,
               f"authored_facing must be 'left' or 'right'; got {facing!r}")

    for field, expected_type in (("set_id", str), ("art_status", str)):
        if field in data:
            report.add(f"metadata.{field}_type", isinstance(data[field], expected_type),
                       f"{field} must be {expected_type.__name__}; got {data[field]!r}")
    if "art_approved" in data:
        report.add("metadata.art_approved_type", isinstance(data["art_approved"], bool),
                   f"art_approved must be bool; got {data['art_approved']!r}")

    # Sheet path and declared hash (verify only if present; never invent).
    cell = vec2(data.get("cell_size"))
    cell_ok = cell is not None and cell[0] > 0 and cell[1] > 0
    report.add("sheet.cell_size", cell_ok,
               f"cell_size must be two positive exact integers; got {data.get('cell_size')!r}")
    if cell_ok and half_scale:
        report.add("sheet.cell_size_even_at_half_scale", cell[0] % 2 == 0 and cell[1] % 2 == 0,
                   f"0.5 scale requires even cell dimensions; got {cell}")
    pivot = vec2(data.get("pivot"))
    pivot_ok = pivot is not None and cell_ok and 0 <= pivot[0] < cell[0] and 0 <= pivot[1] < cell[1]
    report.add("sheet.pivot_in_cell", pivot_ok,
               f"pivot must be two exact integers inside the cell; got {data.get('pivot')!r}, cell={cell!r}")
    if pivot_ok and half_scale:
        report.add("sheet.pivot_even_at_half_scale", pivot[0] % 2 == 0 and pivot[1] % 2 == 0,
                   f"0.5 scale requires even pivot values; got {pivot}")

    sheet_value = data.get("sheet")
    sheet_ok = isinstance(sheet_value, str) and sheet_value.strip() != ""
    report.add("sheet.declared", sheet_ok,
               f"sheet must be a non-empty string path; got {sheet_value!r}")

    sha_fields = [key for key in data if isinstance(key, str) and "sha" in key.lower()]
    if sha_fields:
        result["sha_fields_observed"] = sorted(sha_fields)
    declared_sha = data.get("sheet_sha256") if "sheet_sha256" in data else None
    if declared_sha is not None:
        sha_format_ok = isinstance(declared_sha, str) and len(declared_sha) == 64 and all(
            ch in "0123456789abcdefABCDEF" for ch in declared_sha)
        report.add("sheet.sha256_format", sha_format_ok,
                   f"sheet_sha256 must be 64 hex chars when present; got {declared_sha!r}")
    else:
        report.add("sheet.sha256_present", True,
                   "no sheet_sha256 declared; no hash field invented or required")

    sheet_path = None
    if sheet_ok:
        sheet_path = resolve_sheet(manifest_path, sheet_value)
        result["sheet"]["path"] = str(sheet_path)
        result["sheet"]["declared_sheet_sha256"] = declared_sha
        result["sheet"]["sha256_present"] = declared_sha is not None
        exists = sheet_path.is_file()
        report.add("sheet.file_exists", exists, f"missing PNG: {sheet_path}")
        if exists:
            actual_sha = sha256_file(sheet_path)
            result["sheet"]["actual_sha256"] = actual_sha
            result["sheet"]["bytes"] = sheet_path.stat().st_size
            if declared_sha is not None:
                report.add("sheet.sha256_matches", str(declared_sha).lower() == actual_sha,
                           f"declared sheet_sha256={declared_sha!r}; actual={actual_sha}")

    # Actions: all eight, exact loop flags, exact integer timing, in-bounds cells.
    actions = data.get("actions")
    cell_count = None
    columns = None
    image = None
    image_rgba = None
    if not isinstance(actions, dict):
        report.fail("actions.object", f"actions must be an object; got {type(actions).__name__}")
        actions = {}

    image_loaded = False
    if sheet_path is not None and sheet_path.is_file():
        try:
            with Image.open(sheet_path) as opened:
                opened.load()
                fmt = opened.format
                mode = opened.mode
                size = opened.size
                image = opened.copy()
            report.add("sheet.png_format", fmt == "PNG", f"expected PNG; got {fmt!r}")
            report.add("sheet.image_mode", mode in SUPPORTED_IMAGE_MODES,
                       f"supported 8-bit PNG modes {sorted(SUPPORTED_IMAGE_MODES)}; got {mode!r}")
            result["sheet"]["width"], result["sheet"]["height"] = size
            if cell_ok:
                width_ok = size[0] % cell[0] == 0
                height_ok = size[1] % cell[1] == 0
                report.add("sheet.cell_multiple", width_ok and height_ok,
                           f"sheet {size[0]}x{size[1]} must be a multiple of cell {cell[0]}x{cell[1]}")
                if width_ok and height_ok:
                    columns = size[0] // cell[0]
                    rows = size[1] // cell[1]
                    cell_count = columns * rows
                    result["sheet"]["columns"] = columns
                    result["sheet"]["rows"] = rows
                    result["sheet"]["cell_count"] = cell_count
            image_rgba = image.convert("RGBA")
            palette_error = palette_problem(image)
            if image.mode == "P":
                report.add("sheet.palette_bounds", palette_error is None,
                           palette_error or "palette indices and transparency key are in range")
            if image.mode not in SUPPORTED_IMAGE_MODES:
                report.fail("sheet.alpha_bounds_known", f"cannot assert 8-bit alpha bounds for mode {mode!r}")
            image_loaded = True
        except Exception as exc:  # Pillow decode errors vary by version.
            report.fail("sheet.png_decode", f"Pillow could not decode {sheet_path}: {exc}")
    else:
        report.add("sheet.png_decode", True, "not attempted because PNG is missing")

    present = set(actions)
    unknown = sorted(present - set(CANONICAL_ACTIONS))
    missing = sorted(set(CANONICAL_ACTIONS) - present)
    report.add("actions.known_only", not unknown, f"unknown actions: {unknown}" if unknown else "no unknown actions")
    report.add("actions.all_eight_required", not missing,
               f"missing required actions: {missing}" if missing else "idle, move, guard, attack, dodge, hit, defeat, skill all present")

    actions_summary: dict = {}
    for name in sorted(present & set(CANONICAL_ACTIONS)):
        entry = actions[name]
        prefix = f"actions.{name}"
        if not isinstance(entry, dict):
            report.fail(prefix, f"action must be an object; got {type(entry).__name__}")
            continue

        expected_loop = CANONICAL_ACTIONS[name]
        loop = entry.get("loop")
        report.add(f"{prefix}.loop", isinstance(loop, bool) and loop == expected_loop,
                   f"loop must be exactly {expected_loop!r}; got {loop!r}")

        frames = entry.get("frames")
        if not isinstance(frames, list) or not frames:
            report.fail(f"{prefix}.frames", f"frames must be a non-empty array; got {frames!r}")
            continue

        has_rate = "tick_rate" in entry
        rate = entry.get("tick_rate")
        rate_ok = has_rate and is_int(rate) and 1 <= rate <= MAX_TICK_RATE
        if has_rate:
            report.add(f"{prefix}.tick_rate", rate_ok,
                       f"tick_rate must be an exact integer in 1..{MAX_TICK_RATE}; got {rate!r}")

        pixel_cache: dict[int, dict] = {}
        cumulative_ticks = 0
        cumulative_ms = 0
        frame_ends: list[str] = []
        action_ok = True
        for index, frame in enumerate(frames):
            fprefix = f"{prefix}.frames[{index}]"
            if not isinstance(frame, dict):
                report.fail(fprefix, f"frame must be an object; got {type(frame).__name__}")
                action_ok = False
                continue

            cell_index = frame.get("cell")
            if cell_count is None:
                # Geometry is already failed elsewhere; check type only, not invented bounds.
                report.add(f"{fprefix}.cell_type", is_int(cell_index),
                           f"cell must be an exact integer; got {cell_index!r} (bounds unavailable until sheet geometry passes)")
                cell_index_ok = False
            else:
                cell_index_ok = is_int(cell_index) and 0 <= cell_index < cell_count
                report.add(f"{fprefix}.cell", cell_index_ok,
                           f"cell must be an exact integer in 0..{cell_count - 1}; got {cell_index!r}")
            if not cell_index_ok:
                action_ok = False

            frame_pivot = pivot
            if "pivot" in frame:
                frame_pivot = vec2(frame["pivot"])
                frame_pivot_ok = (
                    frame_pivot is not None
                    and cell_ok
                    and 0 <= frame_pivot[0] < cell[0]
                    and 0 <= frame_pivot[1] < cell[1]
                )
                report.add(f"{fprefix}.pivot_in_cell", frame_pivot_ok,
                           f"per-frame pivot must be exact integers inside the cell; got {frame['pivot']!r}")
                if frame_pivot_ok and half_scale:
                    report.add(f"{fprefix}.pivot_even", frame_pivot[0] % 2 == 0 and frame_pivot[1] % 2 == 0,
                               f"0.5 scale requires even per-frame pivot; got {frame_pivot}")
                if frame_pivot is None:
                    action_ok = False

            if has_rate and rate_ok:
                report.add(f"{fprefix}.timing_mode", "ms" not in frame,
                           "'ms' is forbidden when tick_rate is used (no mixed clocks)")
                ticks = frame.get("ticks")
                ticks_ok = is_int(ticks) and 1 <= ticks <= MAX_FRAME_UNITS
                report.add(f"{fprefix}.ticks", ticks_ok,
                           f"ticks must be an exact integer in 1..{MAX_FRAME_UNITS}; got {ticks!r}")
                if ticks_ok:
                    cumulative_ticks += ticks
                    frame_ends.append(f"{cumulative_ticks}/{rate}")
                else:
                    action_ok = False
            elif not has_rate:
                report.add(f"{fprefix}.timing_mode", "ticks" not in frame,
                           "'ticks' requires an action tick_rate; both clocks must not be mixed")
                ms = frame.get("ms")
                ms_ok = is_int(ms) and 1 <= ms <= MAX_FRAME_UNITS
                report.add(f"{fprefix}.ms", ms_ok,
                           f"ms must be an exact integer in 1..{MAX_FRAME_UNITS}; got {ms!r}")
                if ms_ok:
                    cumulative_ms += ms
                    frame_ends.append(f"{cumulative_ms}/1000")
                else:
                    action_ok = False

            if image_loaded and cell_index_ok and cell is not None:
                if cell_index not in pixel_cache:
                    col = cell_index % columns
                    row = cell_index // columns
                    box = (col * cell[0], row * cell[1], (col + 1) * cell[0], (row + 1) * cell[1])
                    facts = cell_pixel_facts(image_rgba, box)
                    facts["cell_box"] = list(box)
                    pixel_cache[cell_index] = facts
                facts = pixel_cache[cell_index]
                nonblank = facts["alpha_max"] > 0
                report.add(
                    f"{fprefix}.pixels_nonblank", nonblank,
                    f"cell {cell_index} alpha max={facts['alpha_max']}"
                    + ("" if nonblank else "; fully transparent action frame is forbidden"),
                )
                report.add(f"{fprefix}.pixels_alpha_bounds",
                           facts["alpha_min"] >= 0 and facts["alpha_max"] <= 255,
                           f"cell {cell_index} alpha range {facts['alpha_min']}..{facts['alpha_max']} must be within 0..255")
                if facts["alpha_max"] == 0:
                    action_ok = False

        loop_start = entry.get("loop_start", 0)
        if "loop_start" in entry:
            loop_start_ok = (
                loop is True
                and is_int(loop_start)
                and 0 <= loop_start < len(frames)
            )
            report.add(f"{prefix}.loop_start", loop_start_ok,
                       f"loop_start must be an exact integer frame index for a looping action; got {loop_start!r}")
        else:
            report.add(f"{prefix}.loop_start_default", True, "loop_start absent; default 0 applies")

        actions_summary[name] = {
            "loop": loop,
            "frame_count": len(frames),
            "timing": "ticks" if has_rate else "ms",
            "tick_rate": rate if rate_ok else None,
            "duration_ticks": cumulative_ticks if has_rate and rate_ok else None,
            "duration": frame_ends[-1] if frame_ends else None,
            "frame_end_rationals": frame_ends,
            "loop_start": loop_start if "loop_start" in entry else 0,
            "ok": action_ok,
        }

    result["actions"] = actions_summary

    if cell == (136, 144) and pivot == (64, 136):
        result["target_contract"] = {
            "cells_136x144": True,
            "pivot_64_136": True,
            "logical_scale": scale,
            "display_proportion": data.get("display_proportion"),
            "matches_required_target_contract": scale == 0.5 and data.get("display_proportion") == DISPLAY_PROPORTION,
        }
    else:
        result["target_contract"] = {
            "cells_136x144": cell == (136, 144),
            "pivot_64_136": pivot == (64, 136),
            "logical_scale": scale,
            "display_proportion": data.get("display_proportion"),
            "matches_required_target_contract": False,
        }

    return finish(report, result, out_path)


def finish(report: Report, result: dict, out_path: Path | None) -> tuple[int, dict]:
    result["checks"] = report.checks
    result["failed_predicates"] = report.failures
    result["summary"] = {"checks": len(report.checks), "failed": len(report.failures)}
    result["status"] = "PASS" if not report.failures else "FAIL"
    result["hash_binding"] = {
        "algorithm": "sha256",
        "text_normalization": "none; raw bytes",
        "manifest_sha256": result.get("manifest", {}).get("sha256"),
        "sheet_sha256_actual": result.get("sheet", {}).get("actual_sha256"),
        "sheet_sha256_declared": result.get("sheet", {}).get("declared_sheet_sha256"),
    }
    code = 0 if not report.failures else 1
    if out_path is not None:
        result["report_path"] = str(out_path)
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: could not write report {out_path}: {exc}", file=sys.stderr)
            return 2, result
    return code, result


# ---------------------------------------------------------------------------
# Self-test: tiny generated fixtures only. No project image is read.
# ---------------------------------------------------------------------------

def _write_fixture_sheet(path: Path, blank_cells: set[int] = frozenset()) -> None:
    """Palette PNG, 4x2 cells of 16x12 (64x24), 0.5-scale-compatible geometry."""
    cell_w, cell_h, cols, rows = 16, 12, 4, 2
    width, height = cell_w * cols, cell_h * rows
    palette = [0, 0, 0]
    for index in range(1, 9):
        palette.extend(((index * 29) % 256, (index * 57) % 256, (index * 91) % 256))
    image = Image.new("P", (width, height), 0)
    image.putpalette(palette)
    pixels = [0] * (width * height)
    for cell_index in range(cols * rows):
        if cell_index in blank_cells:
            continue
        col, row = cell_index % cols, cell_index // cols
        for y in range(row * cell_h + 2, row * cell_h + cell_h - 2):
            for x in range(col * cell_w + 2, col * cell_w + cell_w - 2):
                pixels[y * width + x] = cell_index + 1
    image.putdata(pixels)
    image.save(path, format="PNG", transparency=0)


def _base_manifest(sheet_path: Path) -> dict:
    manifest = {
        "schema": SET_SCHEMA,
        "set_id": "checker-selftest-zhao-ling-combat-v01",
        "character": {"member_id": "zhao-ling"},
        "art_status": "checker-self-test-fixture-not-art",
        "art_approved": False,
        "note": "NOT ART: generated checker fixture, temporary only.",
        "sheet": sheet_path.name,
        "cell_size": [16, 12],
        "pivot": [8, 10],
        "authored_facing": "right",
        "logical_scale": 0.5,
        "display_proportion": "0.65",
        "actions": {
            "idle": {"loop": True, "loop_start": 0, "tick_rate": 30,
                     "frames": [{"cell": 0, "ticks": 2}, {"cell": 1, "ticks": 2}]},
            "move": {"loop": True, "tick_rate": 30,
                     "frames": [{"cell": 1, "ticks": 2}, {"cell": 2, "ticks": 2}]},
            "guard": {"loop": True, "loop_start": 1, "tick_rate": 30,
                      "frames": [{"cell": 2, "ticks": 2}, {"cell": 3, "ticks": 2}]},
            "attack": {"loop": False, "tick_rate": 30,
                       "frames": [{"cell": 4, "ticks": 1}, {"cell": 5, "ticks": 2, "pivot": [8, 8]}]},
            "dodge": {"loop": False, "tick_rate": 30,
                      "frames": [{"cell": 5, "ticks": 2}, {"cell": 6, "ticks": 1}]},
            "hit": {"loop": False, "tick_rate": 30,
                    "frames": [{"cell": 6, "ticks": 2}, {"cell": 7, "ticks": 1}]},
            "defeat": {"loop": False, "tick_rate": 30,
                       "frames": [{"cell": 7, "ticks": 3}]},
            "skill": {"loop": False, "tick_rate": 30,
                      "frames": [{"cell": 0, "ticks": 2}, {"cell": 4, "ticks": 2}]},
        },
    }
    if sheet_path.is_file():
        manifest["sheet_sha256"] = sha256_file(sheet_path)
    return manifest


@contextmanager
def workspace_tempdir():
    """Normal-mode workspace temp dir; Windows sandbox rejects nested writes inside 0700 temp dirs."""
    path = Path(__file__).resolve().parent / f".wb-cs-validator-selftest-{uuid.uuid4().hex[:8]}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def run_self_test() -> int:
    if Image is None:
        print(json.dumps({"self_test": "FAIL", "error": f"Pillow unavailable: {PIL_IMPORT_ERROR}"}))
        return 2
    cases: list[dict] = []
    all_ok = True
    with workspace_tempdir() as temp:
        root = Path(temp)

        def make_case(name: str, mutate=None, blank_cells=frozenset(), sheet_name="sheet.png"):
            case_dir = root / name
            case_dir.mkdir()
            sheet = case_dir / sheet_name
            if sheet_name != "missing.png":
                _write_fixture_sheet(sheet, set(blank_cells))
            manifest = _base_manifest(sheet)
            if mutate is not None:
                mutate(manifest, sheet)
            manifest_path = case_dir / "manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            return manifest_path

        def add_case(name: str, expected_code: int, expected_failure: str | None, manifest: Path):
            nonlocal all_ok
            try:
                code, result = validate(manifest, None)
            except Exception:
                cases.append({"name": name, "status": "FAIL", "error": traceback.format_exc()})
                all_ok = False
                return
            failed = result.get("failed_predicates", [])
            matched = expected_failure is None or any(expected_failure in item for item in failed)
            ok = code == expected_code and matched
            all_ok = all_ok and ok
            cases.append({
                "name": name,
                "status": "PASS" if ok else "FAIL",
                "exit": code,
                "expected_exit": expected_code,
                "expected_failure_substring": expected_failure,
                "failed_predicates": failed,
                "checks": result.get("summary", {}),
            })

        add_case("valid_all_eight_tick_actions", 0, None, make_case("valid"))

        def mismatch(manifest, sheet):
            manifest["cell_size"] = [16, 10]
            manifest["pivot"] = [8, 8]
        add_case("mismatch_sheet_geometry", 1, "sheet.cell_multiple", make_case("mismatch", mismatch))

        def missing_action(manifest, sheet):
            del manifest["actions"]["skill"]
        add_case("missing_skill_action", 1, "actions.all_eight_required", make_case("missing_action", missing_action))

        def zero_ticks(manifest, sheet):
            manifest["actions"]["idle"]["frames"][0]["ticks"] = 0
        add_case("zero_ticks", 1, "actions.idle.frames[0].ticks", make_case("zero_ticks", zero_ticks))

        def bool_ticks(manifest, sheet):
            manifest["actions"]["idle"]["frames"][0]["ticks"] = True
        add_case("bool_ticks_not_int", 1, "actions.idle.frames[0].ticks", make_case("bool_ticks", bool_ticks))

        add_case("blank_transparent_cell", 1, "pixels_nonblank",
                 make_case("blank_cell", blank_cells=frozenset({0})))

        def missing_png(manifest, sheet):
            manifest["sheet"] = "missing.png"
            manifest.pop("sheet_sha256", None)
        add_case("missing_png", 1, "sheet.file_exists", make_case("missing_png", missing_png, sheet_name="missing.png"))

        def bad_sha(manifest, sheet):
            manifest["sheet_sha256"] = "0" * 64
        add_case("declared_sha_mismatch", 1, "sheet.sha256_matches", make_case("bad_sha", bad_sha))

    print(json.dumps({"self_test": "PASS" if all_ok else "FAIL", "cases": cases}, indent=2))
    return 0 if all_ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate one runtime combat sprite-set manifest and its PNG sheet.")
    parser.add_argument("--manifest", type=Path, help="target runtime-spritesheet-manifest JSON (read only)")
    parser.add_argument("--out", type=Path, help="uniquely named JSON report path")
    parser.add_argument("--self-test", action="store_true", help="run generated tiny fixture self-tests")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()
    if args.manifest is None or args.out is None:
        parser.error("--manifest and --out are required unless --self-test is used")
    try:
        code, _ = validate(args.manifest, args.out)
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        return 2
    return code


if __name__ == "__main__":
    raise SystemExit(main())
