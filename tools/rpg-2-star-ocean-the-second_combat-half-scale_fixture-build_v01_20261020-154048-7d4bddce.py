"""Build the synthetic, diagnostic-only 136x144 combat-sprite fixture for the logical_scale 0.5 check.

The sheet is a deterministic code-drawn mannequin strip: NOT ART, never reviewed or shipped. It exists only
to exercise the optional half-scale loader path with whole source cells and whole per-frame pivots.
"""
from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "game" / "tests" / "fixtures" / "csp-half-scale-v01_7d4bddce"
STAMP = "20261020-154048"
ID = "7d4bddce"
STEM = "rpg-2-star-ocean-the-second_combat-half-scale"
SHEET_NAME = f"{STEM}_sheet_not-art-v01_{STAMP}-{ID}.png"
MANIFEST_NAME = f"{STEM}_fixture_not-art-v01_{STAMP}-{ID}.json"
INDEX_NAME = f"{STEM}_fixture-index_not-art-v01_{STAMP}-{ID}.json"

CELL_W = 136
CELL_H = 144
COLUMNS = 10
ROWS = 4
BASE_PIVOT = [68, 140]
DODGE_PIVOT = [66, 140]


def png_bytes(width: int, height: int, rgba: bytearray) -> bytes:
    def chunk(tag: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)

    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)
        raw.extend(rgba[y * stride:(y + 1) * stride])
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")


def put(rgba: bytearray, width: int, x: int, y: int, color: tuple[int, int, int, int]) -> None:
    if 0 <= x < width and 0 <= y < (len(rgba) // (width * 4)):
        off = (y * width + x) * 4
        rgba[off:off + 4] = bytes(color)


def fill(rgba: bytearray, width: int, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int, int]) -> None:
    for y in range(y0, y1):
        for x in range(x0, x1):
            put(rgba, width, x, y, color)


def draw_cell(rgba: bytearray, width: int, cell: int) -> None:
    cx = (cell % COLUMNS) * CELL_W
    cy = (cell // COLUMNS) * CELL_H
    tint = 40 + (cell * 17) % 120
    body = (tint, 70 + (cell * 29) % 100, 210 - (cell * 13) % 90, 255)
    limb = (20 + (cell * 11) % 80, 150 - (cell * 7) % 60, 90 + (cell * 23) % 100, 255)
    # Head, torso and two planted legs: a readable opaque mannequin.
    fill(rgba, width, cx + 52, cy + 26, cx + 84, cy + 58, body)
    fill(rgba, width, cx + 50, cy + 60, cx + 86, cy + 102, limb)
    fill(rgba, width, cx + 54, cy + 102, cx + 64, cy + 142, body)
    fill(rgba, width, cx + 72, cy + 102, cx + 82, cy + 142, body)
    # Right-facing asymmetric arm, so a mirrored draw is visibly and geometrically asymmetric.
    fill(rgba, width, cx + 86, cy + 64, cx + 104, cy + 96, limb)
    fill(rgba, width, cx + 104, cy + 68, cx + 112, cy + 80, body)
    # Cell-index marker: deterministic and opaque, never part of any acceptance art.
    marker = 6 + (cell % 5) * 4
    fill(rgba, width, cx + 8, cy + 8, cx + 8 + marker, cy + 8 + marker, (230, 40 + (cell * 3) % 120, 40, 255))
    # Two source texels at the base pivot: the whole 2x2 block is opaque magenta for geometry spot checks.
    fill(rgba, width, cx + BASE_PIVOT[0], cy + BASE_PIVOT[1], cx + BASE_PIVOT[0] + 2, cy + BASE_PIVOT[1] + 2, (255, 0, 255, 255))


def action(loop: bool, cells: list[int], ms: int, overrides: dict[int, list[int]] | None = None) -> dict:
    frames = []
    for cell in cells:
        frame = {"cell": cell, "ms": ms}
        if overrides and cell in overrides:
            frame["pivot"] = overrides[cell]
        frames.append(frame)
    return {"loop": loop, "frames": frames}


def main() -> None:
    FIXTURE.mkdir(parents=True, exist_ok=True)
    width = CELL_W * COLUMNS
    height = CELL_H * ROWS
    rgba = bytearray(width * height * 4)
    for cell in range(COLUMNS * ROWS):
        draw_cell(rgba, width, cell)
    (FIXTURE / SHEET_NAME).write_bytes(png_bytes(width, height, rgba))

    actions = {
        "idle": action(True, [0, 1, 2, 3], 240),
        "move": action(True, [4, 5, 6, 7, 8, 9, 10, 11], 90),
        "attack": action(False, [12, 13, 14, 15, 16, 17], 50),
        "skill": action(False, [18, 19, 20, 21, 22, 23], 75),
        "dodge": action(False, [24, 25, 26, 27], 60, {25: DODGE_PIVOT, 26: DODGE_PIVOT}),
        "guard": action(True, [28, 29], 180),
        "hit": action(False, [30, 31, 32], 80),
        "defeat": action(False, [33, 34, 35, 36], 80),
    }
    # attack/skill/hit frame durations differ slightly so boundary checks exercise several offsets.
    for frame, ms in zip(actions["attack"]["frames"], [50, 50, 70, 90, 70, 60]):
        frame["ms"] = ms
    for frame, ms in zip(actions["skill"]["frames"], [75, 75, 75, 75, 75, 75]):
        frame["ms"] = ms
    for frame, ms in zip(actions["hit"]["frames"], [80, 80, 80]):
        frame["ms"] = ms

    manifest = {
        "schema": "worlds-between.combat-sprite-set/1",
        "set_id": "synthetic-diagnostic-hero-female-half-scale-v01",
        "character": {"member_id": "hero", "appearance": "female"},
        "art_status": "synthetic-diagnostic-test-fixture-not-art",
        "art_approved": False,
        "note": "NOT ART: code-drawn 136x144 half-scale loader/playback fixture. Never review or ship as character art.",
        "sheet": SHEET_NAME,
        "cell_size": [CELL_W, CELL_H],
        "pivot": BASE_PIVOT,
        "authored_facing": "right",
        "logical_scale": 0.5,
        "display_proportion": "0.65",
        "actions": actions,
    }
    (FIXTURE / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")

    index = {
        "schema": "worlds-between.combat-sprite-set-index/1",
        "art_status": "synthetic-diagnostic-test-fixture-not-art",
        "art_approved": False,
        "note": "Synthetic half-scale diagnostic fixture for the optional combat-sprite-set loader. Not art.",
        "sets": {"hero:female": f"res://tests/fixtures/csp-half-scale-v01_7d4bddce/{MANIFEST_NAME}"},
    }
    (FIXTURE / INDEX_NAME).write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"WROTE {FIXTURE / SHEET_NAME}")
    print(f"WROTE {FIXTURE / MANIFEST_NAME}")
    print(f"WROTE {FIXTURE / INDEX_NAME}")


if __name__ == "__main__":
    main()
