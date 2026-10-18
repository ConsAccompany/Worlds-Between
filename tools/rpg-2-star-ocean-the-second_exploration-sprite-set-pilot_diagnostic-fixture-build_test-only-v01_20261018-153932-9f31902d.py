"""Builds (or with --check, byte-verifies) the TEST-ONLY diagnostic fixtures of the exploration sprite set pilot.

These are NOT ART and NOT an approval candidate: each 80x112 frame is a hazard-striped box with an arrow for its
facing, white tick bars for its frame number and a solid ID patch whose exact RGB encodes actor, action, facing and
frame, so a Godot capture can prove which frame the runtime drew. They exist to exercise the loader contract of
game/scripts/exploration_sprite_set_pilot.gd (80x112 master cell, density 2, ground pin (40, 104), 96-texel idle
body = 48 logical px, binary alpha, nothing opaque on the border) and say nothing about smooth motion or design.

Outputs under game/tests/fixtures/spriteset-diag-test-only-9f31902d/: 2 actors x 4 facings x (2 idle + 4 walk)
frames, one set manifest per actor, one fixture registry, and four deliberately invalid frames (wrong size,
partial alpha, opaque border, floating idle) used by the negative tests.
Usage: python -I <this file> [--check]
"""
import io
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261018-153932-9f31902d"
SLUG = "rpg-2-star-ocean-the-second"
DIR_REL = "game/tests/fixtures/spriteset-diag-test-only-9f31902d"
OUT = ROOT / DIR_REL
W, H = 80, 112
PIN = (40, 104)
DIRECTIONS = ["south", "west", "north", "east"]
ACTORS = {
    # actor id: (file tag, outline RGB, idle G, walk G, idle durations ms, walk durations ms)
    "protagonist-female": ("female", (255, 0, 255), 40, 200, [470, 410], [130, 130, 130, 130]),
    "protagonist-male": ("male", (0, 255, 0), 60, 220, [500, 350], [150, 150, 150, 150]),
}
HAZARD = [(240, 200, 0), (32, 32, 32)]
WHITE = (255, 255, 255)
PANEL = (16, 16, 16)
BODY = (22, 8, 58, 104)  # x0, y0, x1, y1 (exclusive): 36 x 96 texels, soles on row 103 = pin row - 1


def name(purpose, ext):
    return f"{SLUG}_spriteset-diag_{purpose}_{STAMP}.{ext}"


def id_rgb(actor, action, direction, frame):
    tag, _, idle_g, walk_g, _, _ = ACTORS[actor]
    return (50 + 50 * DIRECTIONS.index(direction), idle_g if action == "idle" else walk_g, 30 + 40 * frame)


def arrow(px, direction):
    # Arrow inside the 28x28 panel at x 26..53, y 12..39, pointing to the facing (screen-down = south).
    cx, cy = 40, 26
    for y in range(13, 39):
        for x in range(27, 53):
            dx, dy = x - cx + 0.5, y - cy + 0.5
            along, across = {"south": (dy, dx), "north": (-dy, dx), "east": (dx, dy), "west": (-dx, dy)}[direction]
            head = -2 <= along <= 11 and abs(across) <= 11 - along
            shaft = -11 <= along < -2 and abs(across) <= 3
            if head or shaft:
                px[x, y] = WHITE + (255,)


def frame_image(actor, action, direction, frame):
    _, outline, _, _, _, _ = ACTORS[actor]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()
    x0, y0, x1, y1 = BODY
    for y in range(y0, y1):
        for x in range(x0, x1):
            edge = x < x0 + 2 or x >= x1 - 2 or y < y0 + 2 or y >= y1 - 2
            px[x, y] = (outline if edge else HAZARD[((x + y) // 4) % 2]) + (255,)
    for y in range(12, 40):
        for x in range(26, 54):
            px[x, y] = PANEL + (255,)
    arrow(px, direction)
    for y in range(46, 62):  # ID patch 24 x 16 texels (12 x 8 logical px)
        for x in range(28, 52):
            px[x, y] = id_rgb(actor, action, direction, frame) + (255,)
    for tick in range(frame + 1):  # frame number as white bars, 4 x 8 texels each
        for y in range(68, 76):
            for x in range(27 + tick * 7, 31 + tick * 7):
                px[x, y] = WHITE + (255,)
    if action == "walk" and frame in (1, 3):  # lifted "foot" notch, left on f2, right on f4
        nx0 = 24 if frame == 1 else 42
        for y in range(96, 104):
            for x in range(nx0, nx0 + 14):
                px[x, y] = (0, 0, 0, 0)
    return img


def png_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=False)
    return buf.getvalue()


def build():
    files = {}
    registry = {"schema": "worlds-between.exploration-sprite-set-registry.v1",
                "purpose": "TEST-ONLY fixture registry for the exploration sprite set pilot checks. Diagnostic frames, not art.",
                "art_status": "diagnostic-test-fixture; not art; not an approval candidate; never a default",
                "actors": {}}
    for actor, (tag, _, _, _, idle_ms, walk_ms) in ACTORS.items():
        actions = {}
        for action, durations in (("idle", idle_ms), ("walk", walk_ms)):
            actions[action] = {}
            for direction in DIRECTIONS:
                entries = []
                for frame, duration in enumerate(durations):
                    file = name(f"{tag}-{action}-{direction}-f{frame + 1}", "png")
                    files[file] = png_bytes(frame_image(actor, action, direction, frame))
                    entries.append({"file": file, "duration_ms": duration})
                actions[action][direction] = entries
        manifest = {"schema": "worlds-between.exploration-sprite-set.v1",
                    "set_id": f"spriteset-diag-{tag}-hd2-test-only-v01",
                    "actor_id": actor,
                    "art_status": "diagnostic-test-fixture; not art; not an approval candidate; never a default",
                    "author": "tools/" + Path(__file__).name,
                    "density": 2, "frame_size": [W, H], "pivot": list(PIN),
                    "id_patch": {"rect_texels": [28, 46, 24, 16],
                                 "rgb": "R = 50 + 50 * facing index (south, west, north, east); G = idle %d / walk %d; B = 30 + 40 * frame index" % (ACTORS[actor][2], ACTORS[actor][3])},
                    "actions": actions}
        set_file = name(f"{tag}-set-manifest", "json")
        files[set_file] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
        registry["actors"][actor] = set_file
    files[name("fixture-registry", "json")] = (json.dumps(registry, indent=2) + "\n").encode("utf-8")
    base = frame_image("protagonist-female", "idle", "south", 0)
    files[name("invalid-wrong-size", "png")] = png_bytes(base.crop((8, 16, 72, 112)))
    partial = base.copy()
    partial.putpixel((40, 80), (240, 200, 0, 128))
    files[name("invalid-partial-alpha", "png")] = png_bytes(partial)
    border = base.copy()
    border.putpixel((0, 60), (255, 0, 255, 255))
    files[name("invalid-opaque-border", "png")] = png_bytes(border)
    floating = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    floating.paste(base.crop((0, 4, W, 104)), (0, 0))
    files[name("invalid-floating-idle", "png")] = png_bytes(floating)
    return files


def main():
    check = "--check" in sys.argv[1:]
    files = build()
    longest = max(len(str(OUT / f)) for f in files)
    bad = []
    if check:
        for f, data in files.items():
            p = OUT / f
            if not p.is_file() or p.read_bytes() != data:
                bad.append(f)
        extra = sorted(p.name for p in OUT.iterdir() if not p.name.endswith(".import") and p.name not in files) if OUT.is_dir() else []
        print(json.dumps({"mode": "check", "files": len(files), "mismatched": bad, "unexpected": extra, "longest_path": longest}))
        sys.exit(1 if bad or extra else 0)
    OUT.mkdir(parents=True, exist_ok=True)
    for f, data in files.items():
        (OUT / f).write_bytes(data)
    print(json.dumps({"mode": "build", "files": len(files), "dir": DIR_REL, "longest_path": longest}))


if __name__ == "__main__":
    main()
