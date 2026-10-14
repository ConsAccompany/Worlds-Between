"""Author Zhao Ling's separate, native 32x48 exploration PNG frames.

The pixels are constructed at final resolution; the character sheet is a design
reference, never resampled. Re-running this file deterministically replaces its
own 20 PNGs and manifest, and touches no other character assets.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "native-animation"
STAMP = "m8-v01_20261014-142000"
PREFIX = "rpg-2-star-ocean-the-second_zhao-ling_native-exploration"
COLORS = {
    "ink": "#1d222b", "deep": "#252b35", "hair": "#30333d",
    "hair_light": "#535760", "hair_cyan": "#547e8b",
    "skin": "#dfae91", "skin_shadow": "#ae7868", "eye": "#537a82",
    "shirt": "#bcc0b6", "jacket": "#444a50", "jacket_lit": "#63686c",
    "jacket_shadow": "#313941", "teal": "#3995a9", "teal_lit": "#73c7cf",
    "teal_deep": "#225c72", "metal": "#a68a65", "metal_lit": "#d0b389",
    "boot": "#30323a", "boot_lit": "#607078", "pack": "#34444d",
}


def box(d: ImageDraw.ImageDraw, coords: tuple[int, int, int, int], fill: str,
        outline: str | None = None) -> None:
    d.rectangle(coords, fill=COLORS[fill],
                outline=COLORS[outline] if outline else None)


def poly(d: ImageDraw.ImageDraw, coords: list[tuple[int, int]], fill: str,
         outline: str | None = "ink") -> None:
    d.polygon(coords, fill=COLORS[fill],
              outline=COLORS[outline] if outline else None)


def line(d: ImageDraw.ImageDraw, coords: list[tuple[int, int]], fill: str,
         width: int = 1) -> None:
    d.line(coords, fill=COLORS[fill], width=width)


def feet_and_legs(d: ImageDraw.ImageDraw, direction: str, phase: int) -> None:
    # Neither the head nor ground anchor bobs. Sole row 44 stays occupied.
    spread = {0: (0, 0), 1: (-3, 2), 2: (-1, 1),
              3: (2, -3), 4: (1, -1)}[phase]
    left, right = spread
    if direction in ("east", "west"):
        sign = 1 if direction == "east" else -1
        left, right = left * sign, right * sign
    poly(d, [(11, 32), (16, 32), (14 + left, 41),
             (10 + left, 42), (10, 36)], "jacket_shadow")
    poly(d, [(17, 32), (22, 32), (22 + right, 41),
             (17 + right, 42), (16, 36)], "deep")
    box(d, (9 + left, 41, 14 + left, 44), "ink")
    box(d, (10 + left, 41, 13 + left, 43), "boot")
    box(d, (17 + right, 41, 22 + right, 44), "ink")
    box(d, (18 + right, 41, 21 + right, 43), "boot")
    box(d, (10 + left, 41, 11 + left, 41), "boot_lit")
    box(d, (18 + right, 41, 19 + right, 41), "boot_lit")


def torso(d: ImageDraw.ImageDraw, direction: str, phase: int) -> None:
    swing = {0: (0, 0), 1: (2, -2), 2: (1, -1),
             3: (-2, 2), 4: (-1, 1)}[phase]
    left_swing, right_swing = swing
    if direction == "north":
        poly(d, [(10, 19), (22, 19), (24, 33), (19, 37),
                 (10, 36), (8, 32)], "jacket")
        box(d, (11, 22, 22, 34), "pack", "ink")
        box(d, (13, 24, 20, 31), "jacket_shadow")
        box(d, (13, 24, 20, 25), "metal")
        box(d, (15, 27, 18, 28), "teal")
        line(d, [(11, 20), (10, 32)], "metal")
        line(d, [(22, 20), (23, 32)], "metal")
    elif direction == "south":
        poly(d, [(10, 19), (22, 19), (24, 32), (20, 37),
                 (12, 37), (8, 32)], "jacket")
        poly(d, [(12, 20), (20, 20), (19, 32), (14, 32)], "shirt", None)
        poly(d, [(10, 20), (14, 20), (16, 26), (12, 24)], "jacket_lit")
        poly(d, [(19, 20), (22, 20), (21, 25), (17, 26)], "jacket_shadow")
        line(d, [(20, 22), (12, 35)], "metal", 2)
        box(d, (17, 27, 19, 29), "teal")
        box(d, (14, 33, 18, 34), "metal")
    else:
        # Backpack remains on the physical back, not a flipped drawing.
        back_x = (7, 10) if direction == "east" else (22, 25)
        box(d, (back_x[0], 23, back_x[1], 32), "pack", "ink")
        box(d, (back_x[0] + 1, 26, back_x[1] - 1, 28), "teal_deep")
        poly(d, [(11, 19), (21, 19), (23, 32), (19, 36),
                 (11, 36), (9, 32)], "jacket")
        poly(d, [(12, 20), (20, 20), (19, 27), (14, 28)], "jacket_lit")
        box(d, ((12, 25, 13, 29) if direction == "west" else
                (19, 25, 20, 29)), "teal")
    # Swinging sleeves are drawn over the torso; a radio tablet is always in
    # her left hand, so side views are authored independently.
    poly(d, [(10, 21), (7, 24), (6 + left_swing, 31),
             (9 + left_swing, 33), (12, 27)], "jacket_shadow")
    poly(d, [(22, 21), (25, 23), (26 + right_swing, 31),
             (23 + right_swing, 33), (20, 27)], "jacket_lit")
    box(d, (6 + left_swing, 31, 8 + left_swing, 33), "skin", "ink")
    box(d, (24 + right_swing, 31, 26 + right_swing, 33), "skin", "ink")
    tablet_x = max(2, 2 + left_swing)
    box(d, (tablet_x, 27 + left_swing, tablet_x + 5,
            34 + left_swing), "ink", "metal")
    box(d, (tablet_x + 1, 29 + left_swing, tablet_x + 4,
            32 + left_swing), "teal_deep")
    line(d, [(tablet_x + 2, 30 + left_swing),
             (tablet_x + 3, 30 + left_swing)], "teal_lit")


def head_south(d: ImageDraw.ImageDraw) -> None:
    # Her heavy left fringe and oversized right earcup are silhouette anchors.
    box(d, (11, 8, 22, 19), "skin", "ink")
    box(d, (13, 17, 20, 20), "skin_shadow")
    poly(d, [(10, 9), (11, 5), (15, 3), (23, 5),
             (24, 10), (20, 11), (17, 9), (15, 14),
             (9, 18), (7, 15)], "hair")
    poly(d, [(8, 13), (12, 7), (17, 6), (15, 12),
             (11, 18), (7, 19)], "hair_light", None)
    line(d, [(14, 5), (18, 4), (22, 7)], "hair_light")
    box(d, (15, 15, 16, 15), "eye")
    box(d, (20, 15, 21, 15), "eye")
    box(d, (18, 18, 19, 18), "skin_shadow")
    line(d, [(18, 4), (23, 5), (26, 8)], "teal_lit", 2)
    box(d, (23, 10, 28, 17), "ink")
    box(d, (24, 11, 27, 16), "teal")
    box(d, (25, 12, 26, 14), "teal_lit")
    line(d, [(28, 12), (28, 2)], "metal", 2)
    box(d, (27, 1, 29, 2), "metal_lit")


def head_north(d: ImageDraw.ImageDraw) -> None:
    poly(d, [(10, 7), (13, 4), (20, 4), (24, 7),
             (24, 17), (21, 20), (12, 20), (9, 17)], "hair")
    poly(d, [(10, 8), (14, 5), (21, 6), (22, 11),
             (18, 15), (11, 13)], "hair_light", None)
    line(d, [(12, 16), (18, 19), (22, 15)], "deep")
    box(d, (6, 10, 10, 17), "ink")
    box(d, (7, 11, 9, 16), "teal")
    box(d, (23, 10, 27, 17), "ink")
    box(d, (24, 11, 26, 16), "teal")
    line(d, [(9, 9), (12, 5), (20, 4), (25, 9)], "teal_lit", 2)
    line(d, [(28, 13), (28, 2)], "metal", 2)
    box(d, (27, 1, 29, 2), "metal_lit")


def head_west(d: ImageDraw.ImageDraw) -> None:
    poly(d, [(12, 8), (14, 5), (20, 4), (24, 8),
             (22, 17), (15, 20), (10, 17)], "hair")
    poly(d, [(7, 11), (12, 6), (16, 6), (16, 11),
             (10, 18), (5, 18)], "hair_light", None)
    poly(d, [(11, 11), (17, 9), (19, 17), (14, 20),
             (10, 17)], "skin", "ink")
    box(d, (10, 15, 11, 15), "eye")
    box(d, (17, 10, 22, 17), "ink")
    box(d, (18, 11, 21, 16), "teal")
    box(d, (19, 12, 20, 14), "teal_lit")
    line(d, [(16, 5), (21, 7), (23, 11)], "teal_lit", 2)
    line(d, [(25, 12), (25, 2)], "metal", 2)
    box(d, (24, 1, 26, 2), "metal_lit")


def head_east(d: ImageDraw.ImageDraw) -> None:
    poly(d, [(9, 8), (14, 4), (20, 4), (23, 7),
             (25, 16), (20, 19), (12, 18)], "hair")
    # Her own left fringe hides behind the head in this view; the right side
    # is close cropped, unlike a mirrored west frame.
    poly(d, [(10, 8), (15, 5), (19, 5), (16, 13),
             (11, 15)], "hair_light", None)
    poly(d, [(16, 10), (22, 10), (25, 15), (22, 20),
             (17, 18)], "skin", "ink")
    box(d, (22, 15, 23, 15), "eye")
    box(d, (10, 10, 15, 17), "ink")
    box(d, (11, 11, 14, 16), "teal")
    box(d, (12, 12, 13, 14), "teal_lit")
    line(d, [(12, 10), (14, 6), (21, 5)], "teal_lit", 2)
    line(d, [(9, 13), (9, 2)], "metal", 2)
    box(d, (8, 1, 10, 2), "metal_lit")


HEADS = {"south": head_south, "west": head_west,
         "north": head_north, "east": head_east}


def render(direction: str, phase: int) -> Image.Image:
    im = Image.new("RGBA", (32, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    feet_and_legs(d, direction, phase)
    torso(d, direction, phase)
    HEADS[direction](d)
    return im


def validate(frames: list[dict[str, object]]) -> None:
    assert len(frames) == 20
    for direction in HEADS:
        hashes = set()
        for phase in range(5):
            im = render(direction, phase)
            assert im.mode == "RGBA" and im.size == (32, 48)
            bounds = im.getbbox()
            assert bounds[0] >= 1 and bounds[2] <= 31, (direction, phase, bounds)
            assert bounds[3] == 45, (direction, phase, bounds)
            for point in [(0, 0), (31, 0), (0, 47), (31, 47)]:
                assert im.getpixel(point)[3] == 0
            assert any(im.getpixel((x, 44))[3] for x in range(6, 27))
            hashes.add(hashlib.sha256(im.tobytes()).hexdigest())
        assert len(hashes) == 5, direction
    assert render("west", 0).tobytes() != render("east", 0).tobytes()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frames: list[dict[str, object]] = []
    for direction in ("south", "west", "north", "east"):
        for phase in range(5):
            action = "idle" if phase == 0 else "walk"
            variant = direction if phase == 0 else f"{direction}-phase-{phase:02d}"
            key = f"zhao-ling:{action}:{variant}"
            unique_id = hashlib.sha256(key.encode()).hexdigest()[:8]
            name = f"{PREFIX}-{action}-{variant}_{STAMP}-{unique_id}.png"
            im = render(direction, phase)
            destination = OUT / name
            im.save(destination)
            with Image.open(destination) as saved:
                assert saved.size == (32, 48) and saved.mode == "RGBA"
            frames.append({
                "action": action, "direction": direction,
                "phase": phase, "path": "game/assets/characters/native-animation/" + name,
                "size": [32, 48], "anchor": [16, 44],
                "stage": "native_exploration_prototype",
            })
    validate(frames)
    manifest_name = f"{PREFIX}-manifest_{STAMP}-b123903c.json"
    manifest = OUT / manifest_name
    manifest.write_text(json.dumps({
        "visual_id": "zhao-ling", "character": "赵铃 / Zhao Ling",
        "source_portrait": "outputs/rpg-2-star-ocean-the-second_zhao-ling_character-sheet_v01_20261013-193120-54215370.png",
        "generator": "game/assets/characters/directional-prototypes/" + Path(__file__).name,
        "status": "prototype_not_accepted",
        "frame_count": len(frames), "frames": frames,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(manifest)


if __name__ == "__main__":
    main()
