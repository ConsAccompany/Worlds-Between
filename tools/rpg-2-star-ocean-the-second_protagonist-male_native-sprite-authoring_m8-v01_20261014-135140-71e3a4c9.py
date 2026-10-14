"""Draw original 32x48 protagonist sprites pixel by pixel at final resolution.

The concept sheet is a visual reference only. No source image pixels are resized,
cropped, traced, or used in these PNGs. Run with the bundled Pillow Python.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "game" / "assets" / "characters" / "native-prototypes"
PREVIEW = ROOT / "outputs" / "character-native-preview"
CITY = (
    ROOT
    / "game"
    / "assets"
    / "environments"
    / "rpg-2-star-ocean-the-second_scifi-city_environment-background_m8-v02_20261013-232003-48d0ab67.png"
)

C = {
    "outline": "#222329",
    "outline_warm": "#332d2b",
    "hair_dark": "#302b2d",
    "hair": "#473835",
    "hair_light": "#72534a",
    "hair_glint": "#96705b",
    "skin_shadow": "#995d49",
    "skin": "#d5a07b",
    "skin_light": "#efbd92",
    "cheek": "#b9755a",
    "coat_dark": "#51433d",
    "coat": "#6b5648",
    "coat_light": "#92735c",
    "coat_hem": "#392f30",
    "shirt": "#cec1a6",
    "shirt_light": "#e5d7b9",
    "trouser": "#6d6154",
    "trouser_light": "#908071",
    "boot": "#3e3431",
    "boot_light": "#645044",
    "teal_dark": "#1c4854",
    "teal": "#287784",
    "teal_light": "#53b2b8",
    "teal_glint": "#9dd0c9",
    "leather": "#8c654d",
    "metal": "#d4b784",
    "pack_dark": "#3c3532",
    "pack": "#624b3b",
}


def draw_south(d: ImageDraw.ImageDraw) -> None:
    p = lambda points, col: d.polygon(points, fill=C[col])
    r = lambda box, col: d.rectangle(box, fill=C[col])

    # Feet and trousers: the final row touches the fixed (16,44) anchor.
    p([(9, 34), (15, 34), (15, 41), (13, 43), (8, 43), (8, 40)], "outline")
    p([(17, 34), (23, 34), (24, 40), (23, 43), (17, 43), (16, 41)], "outline")
    r((10, 35, 14, 39), "trouser")
    r((18, 35, 22, 39), "trouser")
    r((10, 36, 11, 38), "trouser_light")
    r((19, 36, 20, 38), "trouser_light")
    p([(8, 40), (14, 40), (15, 44), (7, 44)], "boot")
    p([(17, 40), (23, 40), (25, 44), (17, 44)], "boot")
    r((9, 41, 13, 41), "boot_light")
    r((18, 41, 22, 41), "boot_light")

    # Broad explorer coat, leftward scarf tail and independent sleeves.
    p([(9, 20), (23, 20), (26, 26), (25, 35), (21, 38), (17, 36),
       (15, 36), (11, 38), (7, 35), (7, 26)], "outline")
    p([(9, 22), (23, 22), (24, 29), (23, 35), (20, 36), (17, 34),
       (14, 34), (11, 36), (9, 35), (8, 29)], "coat")
    p([(8, 22), (5, 24), (4, 30), (6, 34), (9, 34), (10, 29)], "outline")
    p([(8, 24), (6, 25), (5, 30), (7, 32), (9, 31)], "coat")
    p([(24, 22), (27, 25), (28, 31), (26, 34), (23, 33), (22, 28)], "outline")
    p([(24, 24), (26, 26), (27, 31), (25, 32), (23, 30)], "coat")
    r((5, 32, 8, 34), "skin_shadow")
    r((6, 32, 7, 33), "skin")
    r((25, 32, 27, 34), "skin_shadow")
    r((25, 32, 26, 33), "skin")
    r((8, 30, 10, 31), "shirt")
    r((23, 30, 25, 31), "shirt")
    p([(12, 23), (20, 23), (21, 34), (16, 33), (11, 34)], "shirt")
    r((15, 24, 18, 31), "shirt_light")
    r((15, 33, 20, 34), "leather")
    r((17, 33, 18, 34), "metal")
    r((10, 25, 11, 33), "coat_light")
    r((22, 24, 23, 33), "coat_dark")
    p([(23, 29), (26, 30), (25, 36), (23, 37)], "coat_hem")
    r((22, 26, 23, 28), "teal_dark")
    r((22, 27, 23, 28), "teal_light")  # diamond badge, visible at 40px
    r((22, 27, 22, 27), "teal_glint")
    p([(10, 19), (13, 17), (21, 18), (23, 22), (21, 24), (16, 25),
       (11, 23), (7, 27), (7, 32), (5, 32), (5, 26)], "teal_dark")
    p([(11, 19), (20, 19), (22, 22), (18, 24), (12, 22)], "teal")
    r((12, 20, 19, 20), "teal_light")
    r((8, 25, 9, 29), "teal")
    r((7, 29, 7, 31), "teal_light")

    # Neck, ears, face, and the pronounced asymmetric, tousled short hair.
    r((13, 17, 19, 21), "skin_shadow")
    p([(10, 10), (13, 7), (21, 8), (24, 12), (23, 17), (20, 20),
       (13, 20), (10, 17)], "outline")
    p([(11, 11), (14, 9), (21, 9), (22, 12), (22, 17), (19, 19),
       (13, 19), (11, 16)], "skin")
    r((12, 14, 12, 16), "skin_light")
    r((11, 15, 11, 16), "cheek")
    r((22, 14, 23, 16), "skin_shadow")
    r((13, 14, 14, 14), "outline")
    r((19, 14, 20, 14), "outline")
    r((17, 17, 18, 17), "cheek")
    r((15, 18, 18, 18), "outline_warm")
    r((16, 18, 17, 18), "skin_light")

    p([(8, 6), (6, 5), (8, 3), (10, 4), (11, 2), (15, 3), (17, 1),
       (20, 3), (22, 2), (24, 4), (27, 3), (26, 6), (28, 8),
       (25, 9), (26, 12), (22, 13), (20, 11), (18, 10), (16, 12),
       (13, 11), (10, 14), (8, 12), (7, 9), (5, 8)], "outline")
    p([(8, 6), (10, 5), (13, 5), (15, 3), (18, 4), (20, 3),
       (23, 5), (25, 5), (24, 8), (26, 8), (24, 10), (21, 9),
       (18, 8), (16, 10), (14, 9), (11, 12), (9, 11), (9, 8), (7, 8)], "hair")
    p([(6, 7), (10, 7), (9, 10), (6, 9)], "hair_dark")
    p([(10, 5), (15, 4), (13, 6), (10, 7)], "hair_light")
    p([(15, 4), (18, 3), (20, 5), (17, 5)], "hair_light")
    p([(21, 4), (24, 6), (22, 7), (19, 6)], "hair_light")
    r((9, 8, 11, 8), "hair_glint")
    r((17, 5, 19, 5), "hair_glint")
    p([(13, 9), (17, 7), (18, 9), (15, 12), (13, 12)], "hair_dark")
    p([(20, 9), (22, 9), (22, 13), (20, 11)], "hair_dark")


def draw_north(d: ImageDraw.ImageDraw) -> None:
    p = lambda points, col: d.polygon(points, fill=C[col])
    r = lambda box, col: d.rectangle(box, fill=C[col])
    p([(9, 34), (15, 34), (15, 41), (14, 44), (7, 44), (8, 39)], "outline")
    p([(17, 34), (23, 34), (24, 39), (25, 44), (17, 44), (16, 41)], "outline")
    r((10, 35, 14, 40), "trouser")
    r((18, 35, 22, 40), "trouser")
    p([(7, 41), (14, 41), (15, 44), (7, 44)], "boot")
    p([(18, 41), (24, 41), (25, 44), (17, 44)], "boot")
    r((9, 41, 12, 41), "boot_light")
    r((20, 41, 23, 41), "boot_light")
    p([(9, 20), (23, 20), (27, 25), (25, 34), (22, 37), (18, 35),
       (15, 35), (11, 37), (7, 35), (6, 26)], "outline")
    p([(9, 22), (23, 22), (25, 26), (23, 35), (20, 35), (17, 33),
       (15, 33), (12, 35), (9, 35), (7, 26)], "coat")
    p([(7, 22), (4, 25), (4, 32), (6, 34), (9, 32), (10, 26)], "outline")
    p([(8, 24), (6, 25), (5, 31), (7, 32), (9, 30)], "coat")
    p([(25, 22), (28, 25), (28, 32), (26, 34), (23, 32), (22, 26)], "outline")
    p([(24, 24), (26, 25), (27, 31), (25, 32), (23, 30)], "coat")
    r((5, 32, 8, 34), "skin_shadow")
    r((25, 32, 27, 34), "skin_shadow")

    # Pack shape is deliberately wider than the narrow coat, with turquoise roll.
    p([(9, 21), (11, 18), (21, 18), (24, 21), (25, 33), (22, 35),
       (10, 35), (7, 33)], "outline")
    p([(10, 22), (12, 20), (20, 20), (23, 22), (23, 32), (21, 33),
       (11, 33), (9, 31)], "pack")
    r((10, 23, 22, 24), "leather")
    r((11, 26, 21, 31), "coat_dark")
    r((12, 27, 20, 30), "pack")
    r((12, 27, 13, 32), "leather")
    r((19, 27, 20, 32), "leather")
    r((13, 32, 20, 32), "leather")
    r((13, 31, 14, 31), "metal")
    r((19, 31, 20, 31), "metal")
    # Emblem needs a large teal center, not a tiny copied detail.
    p([(16, 26), (19, 28), (16, 31), (13, 28)], "teal_glint")
    p([(16, 27), (18, 28), (16, 30), (14, 28)], "teal")
    p([(7, 19), (9, 17), (23, 17), (26, 19), (26, 23), (23, 24),
       (9, 24), (6, 23)], "outline")
    p([(8, 19), (11, 18), (22, 18), (25, 19), (25, 22), (23, 23),
       (9, 23), (7, 22)], "teal_dark")
    r((10, 19, 23, 20), "teal")
    r((12, 19, 20, 19), "teal_light")
    r((10, 18, 11, 23), "leather")
    r((21, 18, 22, 23), "leather")

    # Hair dominates upper outline; rear crown stays ragged and unlike a bun.
    p([(7, 6), (5, 5), (8, 4), (10, 5), (12, 2), (16, 3), (18, 1),
       (21, 3), (24, 2), (25, 5), (28, 6), (26, 8), (28, 10),
       (25, 13), (25, 17), (22, 20), (11, 20), (8, 17),
       (7, 12), (5, 10)], "outline")
    p([(8, 7), (11, 6), (13, 4), (16, 4), (19, 3), (23, 4),
       (25, 6), (25, 9), (26, 10), (23, 12), (24, 16),
       (21, 18), (12, 18), (9, 16), (9, 11), (7, 10)], "hair")
    p([(8, 8), (12, 7), (12, 12), (10, 15), (8, 12)], "hair_dark")
    p([(20, 8), (24, 7), (25, 12), (23, 16), (21, 15)], "hair_dark")
    p([(13, 6), (17, 4), (20, 5), (18, 8), (14, 9)], "hair_light")
    p([(12, 10), (16, 8), (21, 9), (22, 12), (18, 11), (13, 14)], "hair_light")
    r((14, 5, 17, 5), "hair_glint")
    r((18, 8, 20, 8), "hair_glint")
    r((14, 14, 19, 15), "hair_dark")
    r((13, 18, 20, 19), "teal_dark")
    r((15, 18, 18, 18), "teal")


def draw_side(d: ImageDraw.ImageDraw, facing: str) -> None:
    p = lambda points, col: d.polygon(points, fill=C[col])
    r = lambda box, col: d.rectangle(box, fill=C[col])
    east = facing == "east"
    # The two sides are hand-composed; the east view is not a pixel mirror.
    if east:
        p([(10, 35), (16, 35), (16, 41), (15, 44), (8, 44), (9, 40)], "outline")
        p([(17, 34), (22, 35), (24, 41), (24, 44), (17, 44), (16, 41)], "outline")
        r((11, 36, 15, 40), "trouser")
        r((18, 36, 22, 40), "trouser_light")
        p([(8, 41), (15, 41), (16, 44), (8, 44)], "boot")
        p([(17, 41), (24, 41), (25, 44), (16, 44)], "boot")
        r((10, 41, 13, 41), "boot_light")
        r((19, 41, 23, 41), "boot_light")
        p([(7, 20), (21, 19), (24, 23), (26, 32), (23, 36),
           (12, 37), (7, 34), (6, 25)], "outline")
        p([(8, 22), (21, 21), (23, 24), (24, 32), (22, 35),
           (12, 35), (8, 33), (7, 26)], "coat")
        p([(8, 22), (5, 24), (4, 32), (7, 34), (10, 31)], "outline")
        p([(8, 24), (6, 25), (5, 31), (7, 32), (9, 30)], "coat_dark")
        p([(21, 23), (26, 25), (27, 31), (25, 34), (22, 33)], "outline")
        p([(22, 25), (25, 26), (26, 31), (24, 32), (22, 30)], "coat")
        r((24, 32, 26, 34), "skin_shadow")
        r((25, 32, 26, 33), "skin")
        r((11, 22, 15, 31), "pack_dark")
        r((12, 24, 15, 30), "pack")
        r((12, 19, 15, 23), "teal_dark")
        r((12, 20, 15, 21), "teal")
        r((14, 20, 15, 20), "teal_light")
        r((15, 24, 15, 30), "leather")
        r((19, 26, 20, 31), "shirt")
        r((21, 27, 22, 28), "teal_glint")
        p([(14, 18), (21, 17), (23, 20), (22, 23), (18, 24),
           (14, 22), (10, 26), (9, 30), (7, 30), (8, 24)], "teal_dark")
        p([(15, 18), (21, 18), (22, 20), (19, 22), (15, 21)], "teal")
        r((10, 24, 10, 28), "teal_light")
        r((16, 17, 20, 20), "skin_shadow")
        p([(12, 10), (17, 7), (23, 9), (26, 12), (27, 15),
           (24, 16), (22, 19), (15, 19), (12, 16)], "outline")
        p([(13, 11), (17, 9), (23, 10), (25, 12), (26, 15),
           (23, 15), (21, 18), (15, 18), (13, 15)], "skin")
        r((22, 13, 23, 13), "outline")
        r((23, 16, 24, 16), "cheek")
        p([(7, 6), (6, 4), (10, 4), (12, 2), (15, 3), (18, 1),
           (22, 3), (25, 2), (26, 5), (29, 5), (27, 8),
           (28, 11), (25, 12), (21, 10), (18, 12), (15, 11),
           (13, 14), (9, 13), (8, 10), (6, 9)], "outline")
        p([(8, 6), (12, 5), (14, 4), (18, 3), (22, 4), (25, 4),
           (26, 7), (25, 9), (22, 8), (18, 10), (15, 9),
           (12, 12), (9, 11), (8, 9)], "hair")
        p([(8, 7), (12, 6), (11, 9), (8, 9)], "hair_dark")
        p([(13, 5), (18, 4), (16, 7), (12, 8)], "hair_light")
        p([(20, 4), (24, 5), (22, 7), (18, 8)], "hair_light")
        r((15, 4, 17, 4), "hair_glint")
        p([(20, 9), (24, 8), (25, 11), (21, 10)], "hair_dark")
    else:
        p([(9, 35), (15, 34), (16, 41), (15, 44), (7, 44), (8, 40)], "outline")
        p([(17, 35), (23, 35), (24, 41), (25, 44), (17, 44), (16, 41)], "outline")
        r((10, 36, 14, 40), "trouser_light")
        r((18, 36, 22, 40), "trouser")
        p([(7, 41), (15, 41), (16, 44), (6, 44)], "boot")
        p([(17, 41), (24, 41), (25, 44), (17, 44)], "boot")
        r((8, 41, 12, 41), "boot_light")
        r((20, 41, 23, 41), "boot_light")
        p([(10, 20), (23, 20), (26, 25), (25, 34), (20, 37),
           (10, 36), (6, 32), (8, 23)], "outline")
        p([(11, 22), (22, 21), (25, 26), (24, 33), (20, 35),
           (11, 34), (8, 31), (9, 25)], "coat")
        p([(8, 22), (5, 25), (5, 31), (7, 34), (10, 33), (12, 24)], "outline")
        p([(9, 24), (7, 26), (6, 31), (8, 32), (10, 30)], "coat")
        r((6, 32, 8, 34), "skin_shadow")
        r((6, 32, 7, 33), "skin")
        p([(23, 22), (27, 24), (28, 31), (25, 34), (22, 31)], "outline")
        p([(24, 24), (26, 25), (27, 31), (25, 32), (23, 29)], "coat_dark")
        r((21, 22, 25, 31), "pack_dark")
        r((22, 24, 25, 30), "pack")
        r((21, 19, 25, 23), "teal_dark")
        r((22, 20, 25, 21), "teal")
        r((22, 20, 23, 20), "teal_light")
        r((21, 25, 21, 31), "leather")
        r((13, 26, 14, 31), "shirt")
        r((10, 27, 11, 28), "teal_glint")
        p([(11, 18), (19, 17), (22, 20), (22, 23), (18, 24),
           (13, 22), (20, 27), (23, 29), (25, 28), (23, 24)], "teal_dark")
        p([(12, 18), (19, 18), (20, 20), (17, 22), (13, 21)], "teal")
        r((22, 25, 23, 27), "teal_light")
        r((13, 17, 18, 20), "skin_shadow")
        p([(10, 9), (17, 7), (22, 10), (23, 16), (19, 19),
           (11, 19), (9, 16), (6, 15), (7, 12)], "outline")
        p([(10, 11), (17, 9), (21, 11), (22, 16), (19, 18),
           (11, 18), (10, 15), (7, 15), (8, 12)], "skin")
        r((10, 13, 11, 13), "outline")
        r((8, 16, 9, 16), "cheek")
        p([(5, 5), (7, 4), (9, 5), (11, 2), (14, 3), (18, 1),
           (20, 3), (23, 3), (26, 5), (25, 8), (27, 10),
           (24, 12), (21, 11), (18, 13), (15, 11), (12, 13),
           (9, 11), (6, 12), (5, 9), (3, 8)], "outline")
        p([(6, 6), (10, 5), (12, 4), (17, 3), (21, 4), (24, 5),
           (24, 8), (22, 9), (19, 9), (16, 11), (13, 10),
           (10, 12), (7, 10), (5, 8)], "hair")
        p([(7, 5), (12, 4), (11, 6), (7, 8)], "hair_light")
        p([(15, 4), (19, 3), (20, 6), (16, 6)], "hair_light")
        p([(21, 6), (24, 7), (23, 10), (19, 8)], "hair_dark")
        r((8, 5, 10, 5), "hair_glint")
        p([(8, 9), (11, 7), (13, 9), (10, 12), (6, 12)], "hair_dark")


def render_one(direction: str, timestamp: str) -> dict[str, str | int]:
    im = Image.new("RGBA", (32, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if direction == "south":
        draw_south(d)
    elif direction == "north":
        draw_north(d)
    else:
        draw_side(d, direction)
    # Keep the hair peaks within the common 38–42 visible-pixel envelope.
    # The crown remains irregular at y=3; this is native pixel cleanup, not
    # a resized concept cutout.
    for y in (0, 1, 2):
        for x in range(32):
            im.putpixel((x, y), (0, 0, 0, 0))
    bbox = im.getbbox()
    assert bbox is not None and bbox[3] == 45, (direction, bbox)
    assert 38 <= bbox[3] - bbox[1] <= 42, (direction, bbox)
    assert im.getpixel((16, 0))[3] == 0
    assert len(im.getcolors(maxcolors=10000) or []) <= 32
    name = (
        "rpg-2-star-ocean-the-second_protagonist-male"
        f"_native-idle-{direction}_m8-v01_{timestamp}-{uuid.uuid4().hex[:8]}.png"
    )
    out = OUT / name
    im.save(out)

    # QA only: a separate 640x360 logical-frame preview for each direction.
    # Compositing the native PNG at exact 1:1 with a downsampled environment
    # does not resample, recolor, or modify the sprite asset itself.
    with Image.open(CITY) as source_city:
        scene = source_city.convert("RGBA").resize((640, 360), Image.Resampling.LANCZOS)
    sprite_x, foot_y = 320, 239
    scene.alpha_composite(im, (sprite_x - 16, foot_y - 44))
    scene_name = (
        "rpg-2-star-ocean-the-second_protagonist-male"
        f"_native-scene-preview-{direction}_m8-v01_{timestamp}-{uuid.uuid4().hex[:8]}.png"
    )
    scene.save(PREVIEW / scene_name)

    return {
        "direction": direction,
        "sprite": str(out.relative_to(ROOT)).replace("\\", "/"),
        "preview": str((PREVIEW / scene_name).relative_to(ROOT)).replace("\\", "/"),
        "dimensions": [32, 48],
        "visible_bbox": list(bbox),
        "unique_rgba_colors": len(im.getcolors(maxcolors=10000) or []),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    rows = [render_one(direction, timestamp) for direction in ("south", "west", "north", "east")]
    manifest = OUT / (
        "rpg-2-star-ocean-the-second_protagonist-male"
        f"_native-idle-manifest_m8-v01_{timestamp}-{uuid.uuid4().hex[:8]}.json"
    )
    manifest.write_text(json.dumps({"frames": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(manifest)
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
