"""Author Liang Xu's native 32x48 animation frames from her approved idle pixels.

The hair/face region is copied pixel-for-pixel from each direction's idle art.
Limbs, coat tails, tablet position, and poses below the head are drawn natively.
Running this script recreates the same separately saved PNG frames and manifest.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "native-animation"
STAMP = "m8-v01_20261014-181000"
STEM = "rpg-2-star-ocean-the-second_liang-xu_native-animation"
SOURCE = {
    "south": "rpg-2-star-ocean-the-second_liang-xu_native-idle-south_m8-v03_20261014-175132-e17b4c09.png",
    "west": "rpg-2-star-ocean-the-second_liang-xu_native-idle-west_m8-v03_20261014-175132-b52910e1.png",
    "north": "rpg-2-star-ocean-the-second_liang-xu_native-idle-north_m8-v03_20261014-175132-c742d602.png",
    "east": "rpg-2-star-ocean-the-second_liang-xu_native-idle-east_m8-v03_20261014-175132-d853a711.png",
}
P = {
    "ink": "#161923", "coat": "#363c43", "coat_lit": "#51565b",
    "coat_shade": "#242b35", "navy": "#263851", "navy_light": "#3e5875",
    "copper": "#d2a16d", "copper_dark": "#79533f",
    "boot": "#292b31", "boot_lit": "#4b4546",
    "skin": "#d9a681", "skin_shade": "#a96f58",
    "silver": "#dfd8d3", "energy": "#8bd7e4", "energy_light": "#d0f4f4",
}


def color(name: str) -> str:
    return P[name]


def poly(d: ImageDraw.ImageDraw, pts: list[tuple[int, int]], fill: str, outline: str | None = "ink") -> None:
    d.polygon(pts, fill=color(fill), outline=color(outline) if outline else None)


def box(d: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], fill: str, outline: str | None = None) -> None:
    d.rectangle(xy, fill=color(fill), outline=color(outline) if outline else None)


def line(d: ImageDraw.ImageDraw, pts: list[tuple[int, int]], fill: str, width: int = 1) -> None:
    d.line(pts, fill=color(fill), width=width)


def head(direction: str) -> Image.Image:
    source = Image.open(HERE / SOURCE[direction]).convert("RGBA")
    if source.size != (32, 48):
        raise ValueError(f"Idle source size changed: {SOURCE[direction]}")
    im = Image.new("RGBA", (32, 48), (0, 0, 0, 0))
    im.paste(source.crop((0, 0, 32, 19)), (0, 0))
    return im


def front_legs(d: ImageDraw.ImageDraw, phase: int) -> None:
    # Stance alternates at knees and feet; every sole remains on row 44.
    shifts = {1: (-2, 1), 2: (-1, 0), 3: (1, -2), 4: (0, -1)}
    left, right = shifts[phase]
    poly(d, [(11, 33), (16, 33), (15 + left, 40), (14 + left, 42),
             (10 + left, 41)], "coat_shade")
    poly(d, [(17, 33), (21, 33), (23 + right, 41), (19 + right, 42),
             (17 + right, 39)], "navy")
    box(d, (10 + left, 40, 15 + left, 44), "ink")
    box(d, (11 + left, 40, 14 + left, 43), "boot")
    box(d, (17 + right, 40, 22 + right, 44), "ink")
    box(d, (18 + right, 40, 21 + right, 43), "boot")
    box(d, (11 + left, 40, 11 + left, 42), "boot_lit")
    box(d, (18 + right, 40, 18 + right, 42), "boot_lit")


def side_legs(d: ImageDraw.ImageDraw, direction: str, phase: int) -> None:
    # The passing leg crosses behind the forward leg without a body translation.
    sign = 1 if direction == "east" else -1
    offsets = {1: (2, -2), 2: (1, -1), 3: (-2, 2), 4: (-1, 1)}
    front, back = offsets[phase]
    back_x = 12 + sign * back
    front_x = 18 + sign * front
    poly(d, [(12, 33), (17, 33), (back_x + 3, 41),
             (back_x, 42), (10, 39)], "coat_shade")
    poly(d, [(17, 33), (21, 33), (front_x + 3, 42),
             (front_x, 41), (16, 39)], "navy")
    box(d, (back_x, 40, back_x + 5, 44), "ink")
    box(d, (back_x + 1, 40, back_x + 4, 43), "boot")
    box(d, (front_x, 40, front_x + 5, 44), "ink")
    box(d, (front_x + 1, 40, front_x + 4, 43), "boot")
    box(d, (front_x + 1, 40, front_x + 1, 42), "boot_lit")


def front_body(d: ImageDraw.ImageDraw, direction: str, phase: int,
               action: str) -> None:
    front_legs(d, phase)
    # Long asymmetric tails fan out on contact frames while the trunk stays put.
    flare = {1: -2, 2: -1, 3: 2, 4: 1}[phase]
    poly(d, [(10, 28), (22, 28), (24 + flare, 41),
             (19, 40), (17, 36), (15, 40), (8 + flare, 42)], "coat_shade")
    poly(d, [(10, 31), (16, 33), (15, 39), (8 + flare, 40)], "coat", None)
    poly(d, [(18, 33), (23, 30), (23 + flare, 39), (19, 38)], "navy", None)
    poly(d, [(10, 19), (21, 19), (23, 33), (17, 37), (9, 33)], "coat")
    box(d, (11, 22, 12, 30), "coat_lit")
    box(d, (20, 22, 21, 29), "coat_lit")
    if direction == "south":
        poly(d, [(10, 19), (13, 20), (19, 20), (22, 19),
                 (22, 24), (19, 23), (16, 25), (12, 23), (9, 24)], "coat_shade")
        box(d, (15, 20, 17, 22), "copper")
        line(d, [(16, 24), (16, 33)], "copper_dark")
        box(d, (15, 30, 16, 31), "copper")
    else:
        poly(d, [(10, 19), (22, 19), (22, 24), (16, 22), (10, 24)], "coat_shade")
        line(d, [(16, 23), (16, 35)], "navy", 2)
        box(d, (15, 25, 17, 26), "copper")
    # Arms counter-swing against the legs; hands and tablet move independently.
    swing = {1: (2, -2), 2: (1, -1), 3: (-2, 2), 4: (-1, 1)}[phase]
    ly, ry = swing
    if action == "attack" and phase == 1:
        ly, ry = -5, -7
    elif action == "attack":
        ly, ry = -7, -8
    elif action == "hit":
        ly, ry = -4, -3
    poly(d, [(10, 20), (7, 22), (5, 29 + ly), (8, 31 + ly),
             (11, 26), (12, 22)], "coat")
    poly(d, [(21, 20), (24, 21), (27, 29 + ry), (24, 31 + ry),
             (21, 27), (20, 22)], "coat")
    box(d, (6, 30 + ly, 8, 32 + ly), "skin", "ink")
    box(d, (24, 30 + ry, 26, 32 + ry), "skin", "ink")
    # Tablet is always on Liang's right, even when it rises to cast a pulse.
    ty = 20 if action == "attack" else 24 + ry
    poly(d, [(23, ty), (28, ty - 1), (29, ty + 8), (24, ty + 9)], "ink", "copper_dark")
    box(d, (24, ty + 2, 27, ty + 7), "navy")
    line(d, [(25, ty + 3), (27, ty + 3)], "navy_light")
    if action == "attack" and phase == 2:
        line(d, [(29, 21), (31, 19)], "energy_light")
        box(d, (29, 22, 30, 24), "energy")
    elif action == "hit":
        # Recoil is an asymmetric arm/coat pose, without displacing the head.
        line(d, [(5, 24), (3, 22)], "energy")


def side_body(d: ImageDraw.ImageDraw, direction: str, phase: int) -> None:
    side_legs(d, direction, phase)
    sign = 1 if direction == "east" else -1
    flare = {1: -2, 2: -1, 3: 2, 4: 1}[phase]
    poly(d, [(10, 28), (21, 28), (23 + flare, 41),
             (17, 39), (10 + flare, 42), (8, 40)], "coat_shade")
    poly(d, [(9, 32), (13, 29), (15, 39), (10 + flare, 40)], "coat", None)
    poly(d, [(16, 30), (21, 30), (22 + flare, 39), (17, 38)], "navy", None)
    poly(d, [(10, 19), (20, 19), (23, 32), (16, 36), (8, 32)], "coat")
    poly(d, [(11, 19), (17, 21), (22, 19), (22, 24),
             (16, 25), (10, 23)], "coat_shade")
    box(d, ((19, 21, 21, 23) if sign > 0 else (12, 21, 14, 23)), "copper")
    swing = {1: 2, 2: 1, 3: -2, 4: -1}[phase]
    poly(d, [(10, 22), (7, 24), (7 + swing, 32),
             (10 + swing, 34), (13, 29)], "coat_lit")
    box(d, (7 + swing, 33, 10 + swing, 35), "skin", "ink")
    # Terminal remains visible near the hand, with directional overhang.
    tx = 23 + swing if sign > 0 else 3 + swing
    poly(d, [(tx, 26), (tx + 5, 25), (tx + 6, 34), (tx + 1, 35)],
         "ink", "copper_dark")
    box(d, (tx + 2, 27, tx + 4, 32), "navy")


def render(direction: str, action: str, phase: int) -> Image.Image:
    im = head(direction)
    d = ImageDraw.Draw(im)
    if direction in ("south", "north"):
        front_body(d, direction, phase, action)
    else:
        side_body(d, direction, phase)
    assert im.size == (32, 48) and im.mode == "RGBA"
    assert im.getpixel((0, 0))[3] == 0 and im.getpixel((31, 47))[3] == 0
    assert any(im.getpixel((x, 44))[3] for x in range(6, 27))
    return im


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frames: list[dict[str, object]] = []
    combinations = [("walk", direction, phase)
                    for direction in ("south", "west", "north", "east")
                    for phase in range(1, 5)]
    combinations += [("attack", "south", 1), ("attack", "south", 2),
                     ("hit", "south", 1)]
    for action, direction, phase in combinations:
        key = f"liang_xu:{action}:{direction}:{phase}"
        unique_id = hashlib.sha256(key.encode()).hexdigest()[:8]
        name = f"{STEM}-{action}-{direction}-phase-{phase:02d}_{STAMP}-{unique_id}.png"
        dest = OUT / name
        im = render(direction, action, phase)
        im.save(dest)
        with Image.open(dest) as check:
            assert check.size == (32, 48) and check.mode == "RGBA"
        frames.append({"action": action, "direction": direction, "phase": phase,
                       "path": "game/assets/characters/native-animation/" + name,
                       "size": [32, 48], "anchor": [16, 44],
                       "stage": "native_animation_prototype"})
        print(dest)
    manifest = OUT / f"{STEM}-manifest_{STAMP}-c09d742e.json"
    manifest.write_text(json.dumps({
        "character_id": "liang_xu",
        "generator": "game/assets/characters/directional-prototypes/" + Path(__file__).name,
        "source_idle_manifest": "game/assets/characters/directional-prototypes/"
                                "rpg-2-star-ocean-the-second_liang-xu_native-idle-manifest_"
                                "m8-v03_20261014-180100-9d804f2a.json",
        "status": "prototype_not_accepted",
        "frame_count": len(frames),
        "frames": frames,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(manifest)


if __name__ == "__main__":
    main()
