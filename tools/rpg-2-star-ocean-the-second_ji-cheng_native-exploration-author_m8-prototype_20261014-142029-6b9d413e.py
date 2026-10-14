"""Draw Ji Cheng's four-direction native-resolution exploration animation.

The character sheet is used only as identity reference. Every pixel is drawn
on the final 32x48 canvas; no concept art is downsampled or mirrored.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "game" / "assets" / "characters" / "native-animation"
PREFIX = "rpg-2-star-ocean-the-second_ji-cheng"
DIRECTIONS = ("south", "west", "north", "east")
P = {
    "edge": "#171b1c", "edge_lit": "#33383a", "hair": "#292d30",
    "hair_light": "#4b5052", "hair_silver": "#a6aaa7", "hair_tip": "#d0cfbf",
    "stubble": "#676764", "skin_shadow": "#b09181", "skin": "#dbbfaa",
    "skin_light": "#f1d5bc", "eye": "#444d4a", "coat_dark": "#1d302b",
    "coat": "#304c3d", "coat_light": "#54715b", "coat_hem": "#273a32",
    "shirt": "#232b29", "shirt_light": "#4e5550", "trouser": "#303334",
    "trouser_light": "#545556", "boot": "#252626", "boot_light": "#56504a",
    "glove": "#282b2a", "metal": "#a78654", "metal_light": "#dcc68c",
    "lens": "#b9d3ca", "satchel": "#3d342b", "satchel_light": "#79644a",
}


def poly(d: ImageDraw.ImageDraw, points, color: str) -> None:
    d.polygon(points, fill=P[color])


def rect(d: ImageDraw.ImageDraw, box, color: str) -> None:
    d.rectangle(box, fill=P[color])


def legs(d: ImageDraw.ImageDraw, facing: str, phase: int) -> None:
    if phase == 0:
        offsets = ((0, 0), (0, 0))
    else:
        # Contact, passing, opposite contact, passing. The foot baseline stays 44.
        offsets = {
            1: ((-2, -1), (2, 1)),
            2: ((-1, 0), (1, 0)),
            3: ((2, 1), (-2, -1)),
            4: ((1, 0), (-1, 0)),
        }[phase]
    if facing in ("south", "north"):
        for index, center in enumerate((12, 20)):
            offset, lift = offsets[index]
            hip = center + (offset // 2)
            toe = center + offset
            poly(d, [(hip - 3, 33), (hip + 2, 33), (toe + 2, 40 - lift),
                     (toe - 2, 40 - lift)], "edge")
            poly(d, [(hip - 2, 34), (hip + 1, 34), (toe + 1, 40 - lift),
                     (toe - 1, 40 - lift)], "trouser_light" if index else "trouser")
            poly(d, [(toe - 3, 40 - lift), (toe + 2, 40 - lift),
                     (toe + 3, 44), (toe - 3, 44)], "boot")
            rect(d, (toe - 2, 43, toe + 2, 43), "boot_light")
    else:
        sign = 1 if facing == "east" else -1
        for index, center in enumerate((13, 19)):
            offset, lift = offsets[index]
            toe = center + offset * sign
            poly(d, [(center - 2, 33), (center + 2, 33),
                     (toe + 2, 41 - lift), (toe - 2, 41 - lift)], "edge")
            rect(d, (toe - 2, 40 - lift, toe + 2, 43),
                 "trouser" if index == 0 else "trouser_light")
            poly(d, [(toe - 3, 42), (toe + 2, 41), (toe + 3 * sign, 44),
                     (toe - 3 * sign, 44)], "boot")
            rect(d, (toe - 2, 43, toe + 2, 43), "boot_light")


def coat(d: ImageDraw.ImageDraw, facing: str, phase: int) -> None:
    sway = 0 if phase == 0 else (1, 0, -1, 0)[phase - 1]
    if facing == "south":
        # Open, unequal coat tails frame the charcoal trousers.
        poly(d, [(8, 29), (14, 31), (12 + sway, 40), (7 + sway, 40),
                 (6 + sway, 36)], "edge")
        poly(d, [(9, 30), (13, 32), (11 + sway, 39), (8 + sway, 39)], "coat_dark")
        poly(d, [(19, 30), (24, 28), (26 - sway, 37), (25 - sway, 40),
                 (21 - sway, 40)], "edge")
        poly(d, [(20, 31), (23, 30), (24 - sway, 38), (22 - sway, 39)], "coat_hem")
    elif facing == "north":
        poly(d, [(8, 29), (14, 31), (12 + sway, 40), (7 + sway, 40)], "edge")
        poly(d, [(9, 30), (13, 32), (11 + sway, 39), (8 + sway, 39)], "coat")
        poly(d, [(19, 30), (24, 29), (26 - sway, 39), (21 - sway, 40)], "edge")
        poly(d, [(20, 31), (23, 31), (24 - sway, 39), (22 - sway, 39)], "coat_dark")
    elif facing == "west":
        poly(d, [(10, 29), (23, 29), (25 + sway, 38),
                 (21 + sway, 41), (17, 36), (13, 40), (9 + sway, 39)], "edge")
        poly(d, [(11, 30), (22, 30), (23 + sway, 38),
                 (21 + sway, 39), (17, 34), (12, 39), (10 + sway, 38)], "coat")
        poly(d, [(18, 35), (22, 35), (23 + sway, 39), (21 + sway, 39)], "coat_hem")
    else:
        poly(d, [(9, 29), (22, 29), (24 + sway, 39),
                 (20, 40), (16, 36), (11 + sway, 41), (7 + sway, 38)], "edge")
        poly(d, [(10, 30), (21, 30), (22 + sway, 38),
                 (20, 39), (16, 34), (11 + sway, 39), (9 + sway, 38)], "coat")
        poly(d, [(9, 35), (13, 35), (11 + sway, 39), (9 + sway, 38)], "coat_dark")


def body(d: ImageDraw.ImageDraw, facing: str) -> None:
    poly(d, [(10, 19), (22, 19), (26, 23), (24, 34), (8, 34), (6, 24)], "edge")
    poly(d, [(10, 20), (22, 20), (24, 24), (22, 33), (10, 33), (8, 24)], "coat")
    poly(d, [(12, 20), (20, 20), (19, 32), (13, 32)], "shirt")
    if facing == "south":
        poly(d, [(9, 21), (14, 21), (17, 26), (14, 28)], "coat_light")
        poly(d, [(23, 21), (19, 21), (16, 26), (19, 28)], "coat_dark")
        rect(d, (17, 27, 17, 32), "metal")
        d.line((20, 22, 12, 34), fill=P["satchel_light"], width=2)
    elif facing == "north":
        d.line((12, 22, 20, 33), fill=P["satchel_light"], width=2)
        rect(d, (10, 22, 11, 31), "coat_light")
        rect(d, (22, 22, 23, 32), "coat_dark")
    else:
        x = 11 if facing == "west" else 21
        poly(d, [(x - 3, 20), (x + 1, 20), (x + 1, 29), (x - 2, 31)], "coat_light")
        d.line((21 if facing == "west" else 10, 22,
                11 if facing == "west" else 21, 33), fill=P["satchel_light"], width=2)
    # High collar and a small research case. Their positions are intentionally
    # handed, never generated by horizontal mirroring.
    rect(d, (12, 18, 20, 22), "edge")
    rect(d, (13, 19, 19, 21), "shirt")
    case_x = 22 if facing in ("south", "east") else 8
    rect(d, (case_x, 31, case_x + 4, 37), "edge")
    rect(d, (case_x + 1, 32, case_x + 3, 36), "satchel")
    rect(d, (case_x + 1, 33, case_x + 3, 33), "satchel_light")
    rect(d, (case_x + 2, 35, case_x + 2, 35), "metal")


def arms(d: ImageDraw.ImageDraw, facing: str, phase: int) -> None:
    if phase == 0:
        swing = (0, 0)
    else:
        swing = {1: (-2, 2), 2: (0, 0), 3: (2, -2), 4: (0, 0)}[phase]
    if facing in ("south", "north"):
        for index, x in enumerate((6, 25)):
            off = swing[index]
            poly(d, [(x, 22), (x + 2, 23), (x + 2, 30 + off),
                     (x, 34 + off), (x - 2, 31 + off), (x - 1, 25)], "edge")
            poly(d, [(x, 23), (x + 1, 24), (x + 1, 30 + off),
                     (x, 32 + off), (x - 1, 30 + off)], "coat")
            rect(d, (x - 1, 32 + off, x + 1, 34 + off), "glove")
            rect(d, (x, 31 + off, x + 1, 31 + off), "coat_light")
    else:
        # Far arm is mostly hidden; near arm stays in front of the coat.
        x = 8 if facing == "west" else 23
        y = 32 + swing[0]
        poly(d, [(x - 2, 23), (x + 1, 22), (x + 3, 26),
                 (x + 2, y), (x, y + 2), (x - 2, y)], "edge")
        poly(d, [(x - 1, 24), (x + 1, 23), (x + 2, 27),
                 (x + 1, y), (x - 1, y)], "coat_light")
        rect(d, (x, y, x + 2, y + 2), "glove")


def hair_and_face(d: ImageDraw.ImageDraw, facing: str, phase: int) -> None:
    tail = 0 if phase == 0 else (1, 0, -1, 0)[phase - 1]
    if facing == "south":
        poly(d, [(10, 7), (13, 4), (21, 5), (24, 8), (23, 16),
                 (21, 20), (12, 20), (8, 16), (8, 10)], "edge")
        rect(d, (11, 10, 21, 18), "skin_shadow")
        rect(d, (12, 10, 20, 17), "skin")
        rect(d, (14, 15, 15, 15), "eye")
        rect(d, (19, 15, 20, 15), "eye")
        rect(d, (17, 17, 18, 17), "skin_shadow")
        # Her right side (screen right) is shaved; left curtain falls to shoulder.
        poly(d, [(11, 7), (16, 5), (21, 6), (22, 9), (20, 11),
                 (17, 8), (13, 10), (11, 16), (8, 20 + tail),
                 (7, 22 + tail), (6, 18), (8, 10)], "hair")
        poly(d, [(12, 7), (16, 6), (20, 7), (17, 8), (12, 12)], "hair_light")
        rect(d, (21, 10, 23, 14), "stubble")
        d.line((21, 12, 23, 10), fill=P["hair_light"])
        d.line((8, 18, 7, 21 + tail), fill=P["hair_silver"], width=2)
        rect(d, (7, 21 + tail, 8, 22 + tail), "hair_tip")
        rect(d, (12, 19, 13, 20), "hair_silver")
        rect(d, (23, 15, 23, 17), "metal_light")
    elif facing == "north":
        poly(d, [(10, 6), (14, 4), (21, 5), (24, 9), (23, 18),
                 (20, 21), (11, 21), (8, 18), (8, 10)], "edge")
        poly(d, [(10, 8), (15, 5), (22, 7), (21, 16),
                 (18, 19), (12, 18), (9, 16)], "hair")
        poly(d, [(11, 8), (15, 6), (20, 7), (16, 9), (11, 13)], "hair_light")
        # The asymmetric part line and silver ends must survive in rear view.
        rect(d, (21, 10, 22, 18), "stubble")
        poly(d, [(9, 16), (12, 18), (11, 22 + tail), (8, 21 + tail)], "hair_silver")
        rect(d, (8, 21 + tail, 10, 22 + tail), "hair_tip")
        rect(d, (18, 18, 20, 20), "hair_silver")
    elif facing == "west":
        poly(d, [(11, 7), (16, 4), (23, 6), (25, 10), (23, 17),
                 (18, 19), (11, 17), (8, 13)], "edge")
        poly(d, [(10, 8), (16, 5), (22, 7), (23, 13),
                 (18, 17), (11, 16), (8, 12)], "hair")
        poly(d, [(11, 11), (18, 9), (21, 11), (20, 18), (15, 19),
                 (9, 17)], "skin")
        poly(d, [(10, 8), (16, 5), (21, 7), (18, 10),
                 (14, 11), (11, 17), (9, 20 + tail), (7, 19 + tail),
                 (7, 13)], "hair")
        rect(d, (10, 15, 10, 15), "eye")
        d.line((8, 18, 7, 20 + tail), fill=P["hair_silver"], width=2)
        rect(d, (7, 20 + tail, 8, 21 + tail), "hair_tip")
        rect(d, (22, 13, 23, 15), "stubble")
        rect(d, (22, 16, 22, 18), "metal_light")
    else:  # east; exposed shaved side is visible, unlike the west profile.
        poly(d, [(10, 7), (15, 4), (22, 6), (25, 10), (24, 16),
                 (20, 19), (11, 18), (8, 13)], "edge")
        poly(d, [(11, 9), (15, 6), (21, 7), (23, 11),
                 (21, 17), (13, 17), (9, 13)], "skin")
        poly(d, [(10, 8), (15, 5), (21, 7), (18, 8),
                 (14, 11), (12, 18), (10, 21 + tail), (8, 20 + tail),
                 (8, 13)], "hair")
        poly(d, [(15, 7), (21, 7), (23, 10), (21, 14),
                 (19, 15), (19, 11)], "stubble")
        d.line((19, 9, 22, 10), fill=P["hair_light"])
        rect(d, (22, 15, 22, 15), "eye")
        d.line((9, 18, 9, 21 + tail), fill=P["hair_silver"], width=2)
        rect(d, (8, 21 + tail, 10, 22 + tail), "hair_tip")
        rect(d, (20, 16, 20, 18), "metal_light")
    # Place facial marks last so the sweeping curtain cannot erase her gaze.
    if facing == "south":
        rect(d, (13, 14, 14, 14), "eye")
        rect(d, (19, 14, 20, 14), "eye")
        rect(d, (17, 17, 18, 17), "skin_shadow")
    elif facing == "west":
        rect(d, (11, 15, 11, 15), "eye")
    elif facing == "east":
        rect(d, (21, 15, 21, 15), "eye")


def magnifier(d: ImageDraw.ImageDraw, facing: str) -> None:
    # A folded loupe rides the belt; even when the face is partly hidden the
    # warm circle gives Ji a second, non-color-only identity cue.
    cx = 23 if facing in ("south", "east") else 9
    d.ellipse((cx - 2, 26, cx + 2, 30), outline=P["metal"], width=1)
    rect(d, (cx, 27, cx, 28), "lens")
    d.line((cx + 1, 30, cx + 3, 33), fill=P["metal_light"], width=1)


def frame(facing: str, phase: int) -> Image.Image:
    image = Image.new("RGBA", (32, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(image)
    legs(d, facing, phase)
    coat(d, facing, phase)
    body(d, facing)
    arms(d, facing, phase)
    hair_and_face(d, facing, phase)
    magnifier(d, facing)
    return image


def inspect(image: Image.Image) -> dict:
    assert image.mode == "RGBA" and image.size == (32, 48)
    assert all(image.getpixel(xy)[3] == 0 for xy in ((0, 0), (31, 0), (0, 47), (31, 47)))
    assert any(image.getpixel((x, 44))[3] for x in range(7, 26)), "grounded feet"
    box = image.getbbox()
    assert box and box[1] >= 3 and box[3] == 45, box
    colors = len({image.getpixel((x, y)) for y in range(48) for x in range(32)
                  if image.getpixel((x, y))[3]})
    assert colors <= 32, colors
    return {"visible_bbox": list(box), "opaque_colors": colors}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    rows = []
    unique_images = set()
    for facing in DIRECTIONS:
        for action, phases in (("idle", (0,)), ("walk", range(1, 5))):
            for phase in phases:
                image = frame(facing, phase)
                verification = inspect(image)
                content = image.tobytes()
                assert content not in unique_images, (facing, action, phase)
                unique_images.add(content)
                name = (f"{PREFIX}_native-{action}-{facing}-phase-{phase:02d}"
                        f"_m8-prototype_{stamp}-{uuid4().hex[:8]}.png")
                path = OUT / name
                image.save(path, optimize=True)
                rows.append({"action": action, "direction": facing, "phase": phase,
                             "path": path.relative_to(ROOT).as_posix(),
                             "size": [32, 48], "anchor": [16, 44],
                             "stage": "native_exploration_prototype", **verification})
    assert len(rows) == 20
    manifest = {
        "character_id": "ji-cheng", "source_concept": "outputs/rpg-2-star-ocean-the-second_ji-cheng_character-sheet_v01_20261013-190436-dcea1a37.png",
        "generator": Path(__file__).relative_to(ROOT).as_posix(),
        "status": "prototype_not_accepted", "frame_count": len(rows),
        "canvas": [32, 48], "anchor": [16, 44], "frames": rows,
    }
    path = OUT / f"{PREFIX}_native-exploration-manifest_m8-prototype_{stamp}-{uuid4().hex[:8]}.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(path)
    print("frames=20; unique=20; RGBA=20; floor-anchor=20")


if __name__ == "__main__":
    main()
