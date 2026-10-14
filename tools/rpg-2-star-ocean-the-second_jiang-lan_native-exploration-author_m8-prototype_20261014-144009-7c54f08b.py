"""Author Jiang Lan's native-resolution four-direction exploration prototype.

This constructs pixels at their final 32x48 resolution. The approved portrait
is an identity reference, never a downsampled or mirrored animation source.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "game" / "assets" / "characters" / "native-animation"
PREVIEW_OUT = ROOT / "docs" / "character-visuals"
CITY = ROOT / "game" / "assets" / "environments" / "rpg-2-star-ocean-the-second_scifi-city_environment-background_m8-v02_20261013-232003-48d0ab67.png"
PREFIX = "rpg-2-star-ocean-the-second_jiang-lan"
DIRECTIONS = ("south", "west", "north", "east")
P = {
    "edge": "#191c1d", "hair": "#2c2929", "hair_high": "#5a4e49",
    "hair_shadow": "#202020", "stubble": "#514d49", "skin": "#d9aa89",
    "skin_light": "#efc5a4", "skin_shadow": "#ac806a", "eye": "#333638",
    "coat": "#343637", "coat_light": "#565554", "coat_shadow": "#24272a",
    "vest": "#c0b9a9", "vest_shadow": "#8a8d88", "vest_light": "#e0d9c7",
    "orange": "#f08327", "orange_light": "#ffb05b", "orange_shadow": "#9d4c20",
    "goggle": "#3b4141", "glass": "#a6d4d0", "glass_light": "#e4ece1",
    "strap": "#77614a", "metal": "#a6a69e", "trouser": "#393c3e",
    "trouser_light": "#5f6060", "boot": "#282a2b", "boot_light": "#777670",
    "glove": "#303333", "gadget": "#585d5d",
}


def rect(d: ImageDraw.ImageDraw, box, color: str) -> None:
    d.rectangle(box, fill=P[color])


def poly(d: ImageDraw.ImageDraw, points, color: str) -> None:
    d.polygon(points, fill=P[color])


def legs(d: ImageDraw.ImageDraw, facing: str, phase: int) -> None:
    positions = {
        0: ((0, 0), (0, 0)),
        1: ((-2, 0), (2, 1)),
        2: ((-1, 1), (1, 0)),
        3: ((2, 1), (-2, 0)),
        4: ((1, 0), (-1, 1)),
    }[phase]
    if facing in ("south", "north"):
        for index, center in enumerate((12, 20)):
            delta, lift = positions[index]
            toe = center + delta
            poly(d, [(center - 3, 33), (center + 2, 33),
                     (toe + 3, 40 - lift), (toe - 3, 40 - lift)], "edge")
            poly(d, [(center - 2, 34), (center + 1, 34),
                     (toe + 2, 40 - lift), (toe - 2, 40 - lift)],
                 "trouser" if index == 0 else "trouser_light")
            poly(d, [(toe - 3, 40 - lift), (toe + 2, 40 - lift),
                     (toe + 4, 43), (toe + 3, 44), (toe - 3, 44)], "boot")
            rect(d, (toe - 2, 43, toe + 3, 44), "orange_shadow")
            rect(d, (toe - 1, 43, toe + 2, 43), "orange")
            rect(d, (toe - 1, 39 - lift, toe + 1, 40 - lift), "metal")
    else:
        direction = 1 if facing == "east" else -1
        for index, center in enumerate((13, 19)):
            delta, lift = positions[index]
            toe = center + delta * direction
            poly(d, [(center - 2, 33), (center + 2, 33),
                     (toe + 2, 40 - lift), (toe - 2, 40 - lift)], "edge")
            rect(d, (min(center, toe) - 1, 35, max(center, toe) + 1,
                     40 - lift), "trouser" if index else "trouser_light")
            poly(d, [(toe - 3, 41 - lift), (toe + 2, 41 - lift),
                     (toe + 4 * direction, 44), (toe - 3 * direction, 44)], "boot")
            rect(d, (toe - 2, 43, toe + 2, 44), "orange_shadow")
            rect(d, (toe - 1, 43, toe + 1, 43), "orange")


def body(d: ImageDraw.ImageDraw, facing: str, phase: int) -> None:
    # The pale asymmetrical tool vest and two different hip gadgets are the
    # second identity cue after the spiked haircut and forehead goggles.
    poly(d, [(8, 21), (12, 18), (21, 18), (25, 22), (24, 35),
             (8, 35), (7, 27)], "edge")
    poly(d, [(10, 21), (12, 19), (21, 19), (24, 23), (22, 34),
             (9, 34), (8, 26)], "coat")
    poly(d, [(13, 19), (20, 19), (19, 32), (13, 32)], "coat_shadow")
    if facing == "south":
        poly(d, [(9, 21), (13, 20), (15, 27), (13, 34),
                 (9, 34), (8, 27)], "vest")
        rect(d, (10, 22, 11, 31), "vest_light")
        poly(d, [(21, 20), (25, 22), (24, 31), (21, 35), (19, 29)], "vest_shadow")
        d.line((11, 23, 18, 32), fill=P["strap"], width=2)
        rect(d, (13, 26, 15, 27), "metal")
        rect(d, (20, 26, 22, 28), "gadget")
        rect(d, (21, 27, 21, 27), "orange")
    elif facing == "north":
        poly(d, [(9, 21), (12, 20), (13, 34), (9, 34)], "vest_shadow")
        poly(d, [(19, 20), (23, 21), (24, 33), (19, 34)], "vest")
        rect(d, (21, 22, 22, 31), "vest_light")
        d.line((10, 23, 22, 33), fill=P["strap"], width=2)
        rect(d, (18, 27, 19, 28), "orange")
    elif facing == "west":
        poly(d, [(8, 21), (12, 20), (14, 27), (12, 35), (8, 34)], "vest")
        rect(d, (9, 22, 10, 32), "vest_light")
        d.line((11, 23, 22, 32), fill=P["strap"], width=2)
        rect(d, (18, 25, 20, 28), "gadget")
    else:
        poly(d, [(19, 20), (24, 22), (24, 34), (21, 35), (18, 28)], "vest")
        rect(d, (22, 22, 23, 31), "vest_light")
        d.line((11, 32, 22, 22), fill=P["strap"], width=2)
        rect(d, (13, 26, 15, 28), "gadget")
    rect(d, (8, 32, 24, 34), "coat_shadow")
    rect(d, (14, 33, 18, 34), "metal")
    # Folded-tool cases differ in width and shape, visible from the back too.
    lx, rx = (7, 23) if facing != "north" else (8, 24)
    rect(d, (lx - 1, 32, lx + 2, 38), "edge")
    rect(d, (lx, 33, lx + 1, 37), "gadget")
    rect(d, (lx, 34, lx + 1, 34), "orange")
    poly(d, [(rx - 2, 32), (rx + 1, 32), (rx + 3, 35),
             (rx + 1, 38), (rx - 2, 38)], "edge")
    rect(d, (rx - 1, 33, rx + 1, 37), "gadget")
    rect(d, (rx, 35, rx + 1, 35), "orange")
    # Hanging orange tool strap moves one pixel with alternate contact.
    tail = 0 if phase == 0 else (1, 0, -1, 0)[phase - 1]
    rect(d, (24, 34, 25, 39 + tail), "orange")
    rect(d, (24, 38 + tail, 24, 40 + tail), "orange_shadow")


def arms(d: ImageDraw.ImageDraw, facing: str, phase: int) -> None:
    sway = {0: (0, 0), 1: (-2, 2), 2: (-1, 1),
            3: (2, -2), 4: (1, -1)}[phase]
    if facing in ("south", "north"):
        for index, x in enumerate((6, 26)):
            y = 31 + sway[index]
            poly(d, [(x, 22), (x + 2, 22), (x + 3, 28),
                     (x + 1, y + 2), (x - 2, y + 1), (x - 2, 27)], "edge")
            poly(d, [(x, 23), (x + 1, 23), (x + 2, 28),
                     (x, y), (x - 1, y)], "coat_light")
            rect(d, (x - 2, y - 2, x + 1, y), "orange_shadow")
            rect(d, (x - 1, y - 2, x + 1, y - 1), "orange")
            rect(d, (x - 1, y + 1, x + 1, y + 3), "glove")
    else:
        near = 8 if facing == "west" else 24
        y = 31 + sway[0]
        poly(d, [(near - 2, 22), (near + 2, 22), (near + 3, 28),
                 (near + 2, y + 2), (near - 2, y + 2)], "edge")
        poly(d, [(near - 1, 23), (near + 1, 23), (near + 2, 29),
                 (near + 1, y), (near - 1, y)], "coat_light")
        rect(d, (near - 2, y - 2, near + 1, y), "orange")
        rect(d, (near - 1, y + 1, near + 1, y + 3), "glove")


def head(d: ImageDraw.ImageDraw, facing: str, phase: int) -> None:
    flick = 0 if phase == 0 else (1, 0, -1, 0)[phase - 1]
    if facing == "south":
        poly(d, [(10, 10), (12, 8), (22, 9), (24, 12),
                 (23, 19), (20, 21), (12, 21), (9, 17)], "edge")
        poly(d, [(11, 11), (22, 10), (22, 18), (19, 20),
                 (12, 20), (10, 17)], "skin")
        rect(d, (13, 16, 14, 16), "eye")
        rect(d, (19, 16, 20, 16), "eye")
        rect(d, (17, 19, 18, 19), "skin_shadow")
        rect(d, (10, 13, 11, 17), "stubble")
        rect(d, (22, 13, 23, 17), "stubble")
        poly(d, [(8, 10), (6 + flick, 7), (5 + flick, 8),
                 (8, 5), (11, 7), (10, 4), (16, 6),
                 (18, 4), (22, 6), (25, 5), (24, 10),
                 (20, 12), (14, 10), (11, 13)], "hair")
        poly(d, [(6 + flick, 7), (10, 6), (14, 7),
                 (11, 8)], "hair_high")
        poly(d, [(11, 7), (13, 3), (15, 6)], "hair")
        poly(d, [(17, 7), (20, 3), (21, 7)], "hair")
        poly(d, [(22, 8), (25, 4), (24, 10)], "hair")
        d.line((7 + flick, 7, 11, 8), fill=P["orange"], width=1)
        d.line((18, 5, 20, 7), fill=P["orange_shadow"])
        # Paired square goggles remain on the forehead, not over the eyes.
        rect(d, (10, 9, 16, 12), "edge")
        rect(d, (11, 9, 15, 11), "orange")
        rect(d, (12, 10, 14, 11), "glass")
        rect(d, (18, 9, 24, 12), "edge")
        rect(d, (19, 9, 23, 11), "orange")
        rect(d, (20, 10, 22, 11), "glass")
        rect(d, (16, 10, 18, 10), "strap")
    elif facing == "north":
        poly(d, [(9, 10), (12, 7), (21, 8), (24, 12),
                 (24, 19), (10, 19)], "edge")
        rect(d, (11, 12, 22, 18), "stubble")
        poly(d, [(8, 10), (5 + flick, 8), (9, 5),
                 (13, 7), (12, 4), (18, 7), (21, 4),
                 (25, 8), (22, 11), (11, 12)], "hair")
        poly(d, [(8, 8), (13, 6), (18, 8), (14, 9)], "hair_high")
        poly(d, [(12, 7), (14, 3), (16, 7)], "hair")
        poly(d, [(19, 7), (21, 3), (23, 8)], "hair")
        d.line((7 + flick, 8, 11, 9), fill=P["orange"])
        rect(d, (10, 13, 23, 14), "goggle")
        rect(d, (17, 13, 20, 14), "orange_shadow")
    elif facing == "west":
        poly(d, [(10, 10), (13, 8), (22, 9), (24, 13),
                 (22, 19), (15, 21), (10, 17)], "edge")
        poly(d, [(10, 12), (22, 10), (21, 19),
                 (14, 20), (9, 16)], "skin")
        rect(d, (10, 15, 10, 15), "eye")
        rect(d, (21, 12, 22, 18), "stubble")
        poly(d, [(9, 10), (5 + flick, 9), (8, 6),
                 (12, 7), (12, 4), (18, 6), (20, 4),
                 (24, 8), (22, 11), (13, 11), (10, 14)], "hair")
        poly(d, [(12, 7), (15, 3), (17, 6)], "hair")
        poly(d, [(18, 7), (22, 3), (21, 8)], "hair")
        d.line((6 + flick, 9, 11, 8), fill=P["orange"])
        rect(d, (9, 9, 16, 12), "edge")
        rect(d, (10, 9, 15, 11), "orange")
        rect(d, (11, 10, 14, 11), "glass")
        rect(d, (17, 10, 21, 11), "goggle")
    else:  # east is independently drawn, with the shaved side more exposed.
        poly(d, [(10, 10), (13, 8), (22, 9), (24, 13),
                 (24, 17), (20, 21), (12, 20), (9, 17)], "edge")
        poly(d, [(11, 10), (22, 11), (24, 16),
                 (20, 20), (12, 19)], "skin")
        rect(d, (22, 15, 22, 15), "eye")
        poly(d, [(10, 12), (13, 10), (13, 18), (11, 18)], "stubble")
        poly(d, [(8, 9), (7 + flick, 7), (11, 6),
                 (13, 4), (18, 6), (21, 4), (24, 6),
                 (25, 9), (21, 11), (14, 10), (12, 13)], "hair")
        poly(d, [(12, 7), (15, 3), (17, 7)], "hair")
        poly(d, [(19, 7), (22, 3), (23, 8)], "hair")
        d.line((18, 5, 22, 7), fill=P["orange"])
        rect(d, (17, 9, 24, 12), "edge")
        rect(d, (18, 9, 23, 11), "orange")
        rect(d, (19, 10, 22, 11), "glass")
        rect(d, (13, 10, 16, 11), "goggle")
    # High standing collar links portrait and all four sprite views.
    rect(d, (12, 19, 20, 21), "edge")
    rect(d, (13, 20, 19, 21), "coat_shadow")
    rect(d, (12 if facing != "east" else 20, 20,
             13 if facing != "east" else 21, 20), "orange")


def frame(facing: str, phase: int) -> Image.Image:
    im = Image.new("RGBA", (32, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    legs(d, facing, phase)
    body(d, facing, phase)
    arms(d, facing, phase)
    head(d, facing, phase)
    return im


def inspect(im: Image.Image) -> dict:
    assert im.mode == "RGBA" and im.size == (32, 48)
    assert all(im.getpixel(corner)[3] == 0 for corner in
               ((0, 0), (31, 0), (0, 47), (31, 47)))
    assert any(im.getpixel((x, 44))[3] for x in range(7, 26))
    box = im.getbbox()
    assert box and box[1] >= 3 and box[3] == 45, box
    colors = len({im.getpixel((x, y)) for y in range(48) for x in range(32)
                  if im.getpixel((x, y))[3]})
    assert colors <= 32, colors
    return {"visible_bbox": list(box), "opaque_colors": colors}


def game_scale_preview(city: Image.Image, sprite: Image.Image, direction: str,
                       stamp: str) -> Path:
    canvas = city.copy()
    # Hero feet at (320,253), matching the central science-city plaza scale.
    canvas.alpha_composite(sprite, (320 - 16, 253 - 44))
    name = (f"{PREFIX}_native-{direction}-game-scale-preview_m8-prototype_"
            f"{stamp}-{uuid4().hex[:8]}.png")
    path = PREVIEW_OUT / name
    canvas.save(path, optimize=True)
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEW_OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    rows = []
    seen = set()
    idle_by_direction = {}
    for facing in DIRECTIONS:
        for action, phases in (("idle", (0,)), ("walk", range(1, 5))):
            for phase in phases:
                im = frame(facing, phase)
                checks = inspect(im)
                pixels = im.tobytes()
                assert pixels not in seen, (facing, action, phase)
                seen.add(pixels)
                if action == "idle":
                    idle_by_direction[facing] = im
                name = (f"{PREFIX}_native-{action}-{facing}-phase-{phase:02d}"
                        f"_m8-prototype_{stamp}-{uuid4().hex[:8]}.png")
                path = OUT / name
                im.save(path, optimize=True)
                rows.append({"action": action, "direction": facing, "phase": phase,
                             "path": path.relative_to(ROOT).as_posix(),
                             "size": [32, 48], "anchor": [16, 44],
                             "stage": "native_exploration_prototype", **checks})
    assert len(rows) == 20
    city = Image.open(CITY).convert("RGBA").resize(
        (640, 360), Image.Resampling.LANCZOS)
    previews = [game_scale_preview(city, idle_by_direction[facing], facing, stamp)
                for facing in DIRECTIONS]
    manifest = {
        "visual_id": "jiang-lan", "display_name_zh": "蒋岚", "region": "科技",
        "source_portrait": "outputs/rpg-2-star-ocean-the-second_jiang-lan_character-sheet_hairstyle-v02_20261013-161317-c21bd255.png",
        "generator": Path(__file__).relative_to(ROOT).as_posix(),
        "status": "prototype_not_accepted", "frame_count": 20,
        "canvas": [32, 48], "anchor": [16, 44], "frames": rows,
        "game_scale_previews": [p.relative_to(ROOT).as_posix() for p in previews],
        "preview_note": "Static 640x360 composite over existing science city art, not an in-engine capture or a nature-region test.",
    }
    out = OUT / (f"{PREFIX}_native-exploration-manifest_m8-prototype_"
                 f"{stamp}-{uuid4().hex[:8]}.json")
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(out)
    print("frames=20; unique=20; RGBA=20; game-scale-previews=4")


if __name__ == "__main__":
    main()
