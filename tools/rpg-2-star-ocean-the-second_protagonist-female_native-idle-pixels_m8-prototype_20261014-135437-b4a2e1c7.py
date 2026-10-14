"""Hand-authored 32x48 RGBA pixel-idle study of the female protagonist.

Each facing is painted natively at logical game resolution. No concept-art
downsampling is involved. This is a prototype; walk frames are still needed.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "game" / "assets" / "characters" / "native-prototypes"
OUT.mkdir(parents=True, exist_ok=True)
PREVIEW = ROOT / "outputs"
PREVIEW.mkdir(parents=True, exist_ok=True)
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
SLUG = "rpg-2-star-ocean-the-second_protagonist-female"

P = {
    "edge": "#202529", "hair_dark": "#29272b", "hair": "#463632",
    "hair_light": "#856149", "hair_glint": "#b4835b",
    "skin_shadow": "#ad684e", "skin": "#d9956c", "skin_light": "#f0bb89",
    "coat_dark": "#493a31", "coat": "#705240", "coat_light": "#977357",
    "shirt_dark": "#a69c88", "shirt": "#e0d2b5", "shirt_light": "#f6e9cb",
    "teal_dark": "#12484d", "teal": "#2c7880", "teal_light": "#65b7b8",
    "pack_dark": "#3a302c", "pack": "#69503c", "pack_light": "#9b7650",
    "pants_dark": "#393834", "pants": "#645b50", "pants_light": "#918273",
    "boot_dark": "#292725", "boot": "#594638", "boot_light": "#88684e",
    "metal": "#c5b793", "metal_shadow": "#756f61",
}


def frame() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGBA", (32, 48), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def poly(d, pts, fill, outline=True):
    d.polygon(pts, fill=P[fill], outline=P["edge"] if outline else None)


def rect(d, xy, fill):
    d.rectangle(xy, fill=P[fill])


def px(d, points, fill):
    for point in points:
        d.point(point, fill=P[fill])


def legs(d, back=False):
    poly(d, [(9, 32), (15, 32), (15, 40), (14, 42), (9, 42), (8, 39)], "pants")
    poly(d, [(17, 32), (23, 32), (24, 39), (23, 42), (18, 42), (17, 39)], "pants")
    rect(d, (10, 34, 12, 39), "pants_light")
    rect(d, (19, 34, 21, 39), "pants_light")
    poly(d, [(8, 40), (15, 40), (15, 44), (8, 44)], "boot")
    poly(d, [(17, 40), (24, 40), (24, 44), (17, 44)], "boot")
    rect(d, (9, 41, 13, 41), "boot_light")
    rect(d, (18, 41, 22, 41), "boot_light")
    if not back:
        rect(d, (8, 43, 15, 44), "boot_dark")
        rect(d, (17, 43, 24, 44), "boot_dark")


def south():
    im, d = frame()
    # High side ponytail is an 8px-wide shape, projecting beyond the head.
    poly(d, [(10, 6), (8, 3), (5, 4), (2, 8), (1, 13), (3, 17),
             (1, 22), (2, 28), (5, 26), (7, 21), (6, 16),
             (8, 11), (11, 9)], "hair_dark")
    poly(d, [(7, 5), (4, 8), (3, 13), (5, 17), (3, 22),
             (3, 26), (5, 24), (6, 20), (5, 16), (7, 10)], "hair")
    rect(d, (3, 9, 4, 14), "hair_light")
    rect(d, (2, 19, 4, 25), "hair_light")
    px(d, [(3, 16), (2, 26)], "hair_glint")
    # Teal bedroll side profile gives a second stable silhouette cue.
    poly(d, [(24, 17), (29, 18), (30, 21), (28, 24), (25, 23)], "teal_dark")
    rect(d, (26, 19, 28, 21), "teal")
    rect(d, (27, 20, 27, 20), "teal_light")
    legs(d)
    poly(d, [(8, 19), (12, 17), (21, 17), (26, 21), (25, 31),
             (22, 36), (18, 33), (15, 34), (10, 36), (8, 31)], "coat_dark")
    poly(d, [(10, 20), (13, 19), (20, 19), (23, 21), (22, 32),
             (19, 34), (18, 29), (14, 29), (13, 34), (10, 32)], "coat")
    poly(d, [(13, 22), (19, 22), (20, 30), (12, 30)], "shirt")
    rect(d, (14, 24, 16, 27), "shirt_light")
    poly(d, [(8, 20), (5, 25), (6, 33), (9, 34), (11, 25)], "coat")
    poly(d, [(23, 20), (27, 24), (26, 32), (23, 34), (21, 25)], "coat")
    rect(d, (6, 31, 9, 34), "skin")
    rect(d, (23, 31, 26, 34), "skin")
    rect(d, (6, 34, 9, 36), "coat_dark")
    rect(d, (23, 34, 26, 36), "coat_dark")
    # Raised collar and asymmetrical scarf tail.
    poly(d, [(11, 18), (21, 18), (23, 22), (19, 25), (12, 24), (9, 21)], "teal_dark")
    poly(d, [(11, 19), (21, 19), (21, 22), (18, 24), (12, 23)], "teal")
    rect(d, (11, 20, 16, 20), "teal_light")
    poly(d, [(21, 22), (24, 25), (24, 30), (22, 33), (21, 29)], "teal_dark")
    rect(d, (22, 25, 22, 29), "teal_light")
    # Face / hair cap / eyes.
    poly(d, [(10, 8), (14, 6), (19, 7), (22, 10), (22, 17),
             (19, 21), (13, 21), (10, 17)], "skin")
    rect(d, (12, 14, 19, 16), "skin_light")
    poly(d, [(9, 9), (11, 6), (15, 4), (20, 6), (23, 10), (22, 14),
             (20, 12), (17, 9), (14, 11), (11, 11), (9, 14)], "hair_dark")
    poly(d, [(11, 8), (15, 5), (18, 6), (21, 9), (17, 8), (14, 10)], "hair")
    px(d, [(13, 6), (16, 5), (18, 7)], "hair_light")
    rect(d, (7, 7, 9, 8), "teal_dark")
    px(d, [(8, 7)], "teal_light")
    rect(d, (12, 15, 13, 15), "edge")
    rect(d, (18, 15, 19, 15), "edge")
    px(d, [(16, 18)], "skin_shadow")
    # Fixed community diamond on front left chest.
    poly(d, [(21, 25), (23, 27), (21, 29), (19, 27)], "metal")
    px(d, [(21, 27)], "teal_light")
    rect(d, (10, 31, 23, 32), "coat_dark")
    rect(d, (15, 31, 17, 32), "metal")
    return im


def north():
    im, d = frame()
    legs(d, back=True)
    # Side ponytail remains visibly external even behind the pack.
    poly(d, [(10, 5), (7, 3), (4, 5), (2, 9), (2, 14), (0, 19),
             (1, 24), (0, 28), (3, 27), (6, 23), (7, 17),
             (6, 13), (10, 9)], "hair_dark")
    poly(d, [(6, 5), (4, 9), (4, 14), (2, 19), (2, 25),
             (4, 24), (6, 17), (6, 10)], "hair")
    rect(d, (3, 9, 4, 14), "hair_light")
    rect(d, (1, 19, 3, 25), "hair_light")
    px(d, [(1, 26)], "hair_glint")
    poly(d, [(8, 19), (11, 17), (22, 17), (25, 21), (24, 34),
             (20, 36), (17, 32), (14, 33), (11, 36), (8, 33)], "coat_dark")
    poly(d, [(10, 20), (22, 20), (24, 23), (22, 32), (19, 34),
             (17, 30), (14, 30), (12, 34), (9, 31)], "coat")
    poly(d, [(7, 20), (5, 24), (6, 34), (9, 34), (11, 23)], "coat")
    poly(d, [(24, 20), (27, 25), (26, 34), (23, 34), (21, 23)], "coat")
    rect(d, (6, 31, 9, 35), "skin")
    rect(d, (23, 31, 26, 35), "skin")
    rect(d, (6, 34, 9, 36), "coat_dark")
    rect(d, (23, 34, 26, 36), "coat_dark")
    # Turquoise bedroll must read above square backpack.
    poly(d, [(9, 19), (10, 17), (23, 17), (25, 19), (24, 22),
             (8, 22)], "teal_dark")
    rect(d, (11, 18, 21, 20), "teal")
    rect(d, (12, 18, 19, 18), "teal_light")
    rect(d, (12, 18, 13, 22), "pack_light")
    rect(d, (20, 18, 21, 22), "pack_light")
    poly(d, [(10, 22), (22, 22), (24, 25), (23, 33),
             (20, 35), (11, 35), (9, 32), (9, 25)], "pack_dark")
    poly(d, [(11, 23), (22, 23), (22, 32), (20, 34),
             (12, 34), (10, 32)], "pack")
    rect(d, (11, 24, 12, 32), "pack_light")
    rect(d, (20, 24, 21, 32), "pack_light")
    poly(d, [(16, 26), (19, 29), (16, 32), (13, 29)], "metal")
    px(d, [(16, 29)], "teal")
    rect(d, (13, 33, 19, 33), "pack_light")
    # Nape and high off-centre ponytail knot.
    poly(d, [(10, 9), (13, 5), (20, 5), (23, 9), (22, 18),
             (19, 21), (12, 20), (9, 17)], "hair_dark")
    poly(d, [(11, 9), (14, 6), (19, 7), (21, 10), (20, 17),
             (16, 19), (12, 17)], "hair")
    rect(d, (13, 7, 15, 9), "hair_light")
    rect(d, (17, 8, 18, 13), "hair_light")
    poly(d, [(7, 6), (10, 3), (13, 4), (15, 7), (12, 9), (9, 9)], "hair_dark")
    rect(d, (9, 4, 10, 6), "hair_glint")
    rect(d, (7, 6, 9, 7), "teal_dark")
    px(d, [(8, 6)], "teal_light")
    rect(d, (13, 19, 18, 20), "teal")
    return im


def west():
    im, d = frame()
    # Ponytail trails on the opposite side from her gaze.
    poly(d, [(19, 6), (23, 5), (27, 8), (28, 13), (30, 17),
             (28, 21), (29, 25), (26, 23), (24, 17), (21, 12)], "hair_dark")
    poly(d, [(23, 7), (26, 10), (26, 15), (28, 19), (27, 22),
             (25, 17), (22, 11)], "hair")
    rect(d, (26, 11, 27, 16), "hair_light")
    rect(d, (27, 18, 28, 21), "hair_light")
    # Back-mounted roll and pack.
    poly(d, [(22, 19), (27, 19), (28, 25), (25, 32), (21, 31)], "pack_dark")
    rect(d, (24, 21, 27, 27), "pack")
    poly(d, [(22, 17), (28, 17), (29, 19), (27, 22), (22, 21)], "teal_dark")
    rect(d, (24, 18, 27, 19), "teal")
    rect(d, (27, 19, 27, 19), "teal_light")
    legs(d)
    poly(d, [(10, 20), (15, 18), (22, 20), (25, 25), (23, 34),
             (19, 36), (15, 33), (11, 35), (8, 31)], "coat_dark")
    poly(d, [(11, 21), (17, 19), (22, 22), (22, 31),
             (19, 34), (16, 31), (12, 34), (10, 30)], "coat")
    rect(d, (14, 24, 18, 29), "shirt")
    poly(d, [(10, 21), (7, 24), (7, 32), (10, 34), (13, 27)], "coat")
    rect(d, (7, 30, 9, 34), "skin")
    rect(d, (7, 34, 10, 36), "coat_dark")
    poly(d, [(11, 18), (20, 18), (21, 23), (16, 25), (10, 22)], "teal_dark")
    poly(d, [(11, 19), (19, 19), (18, 23), (13, 23)], "teal")
    poly(d, [(11, 22), (8, 25), (6, 29), (8, 30), (13, 24)], "teal_dark")
    rect(d, (8, 26, 9, 27), "teal_light")
    # Side profile looks left; bangs and a one-pixel nose jut left.
    poly(d, [(12, 9), (17, 7), (22, 9), (23, 16),
             (19, 20), (13, 19), (10, 15), (9, 14)], "skin")
    rect(d, (10, 15, 15, 16), "skin_light")
    poly(d, [(10, 10), (14, 6), (20, 6), (23, 10),
             (23, 15), (20, 13), (18, 9), (15, 10), (11, 13), (9, 13)], "hair_dark")
    poly(d, [(13, 8), (17, 7), (20, 9), (16, 9), (12, 12)], "hair")
    px(d, [(15, 7), (18, 8)], "hair_light")
    px(d, [(11, 14)], "edge")
    px(d, [(10, 18)], "skin_shadow")
    rect(d, (12, 30, 22, 31), "coat_dark")
    rect(d, (15, 30, 16, 31), "metal")
    px(d, [(21, 25)], "teal_light")
    return im


def east():
    im, d = frame()
    # Different side is drawn directly rather than relying on a mirror.
    poly(d, [(11, 5), (8, 4), (4, 8), (4, 14), (2, 19),
             (4, 23), (3, 26), (7, 23), (8, 17), (11, 12)], "hair_dark")
    poly(d, [(7, 7), (5, 11), (6, 16), (4, 20), (5, 23),
             (7, 18), (9, 12)], "hair")
    rect(d, (5, 10, 6, 15), "hair_light")
    rect(d, (4, 18, 5, 22), "hair_light")
    poly(d, [(5, 18), (10, 18), (11, 22), (9, 32), (5, 31)], "pack_dark")
    rect(d, (6, 21, 9, 28), "pack")
    poly(d, [(4, 16), (11, 16), (12, 20), (9, 22), (4, 21)], "teal_dark")
    rect(d, (5, 18, 9, 19), "teal")
    rect(d, (6, 18, 8, 18), "teal_light")
    legs(d)
    poly(d, [(10, 20), (17, 18), (22, 20), (26, 26), (24, 32),
             (20, 35), (17, 32), (12, 36), (9, 34)], "coat_dark")
    poly(d, [(11, 21), (17, 20), (22, 22), (24, 30),
             (20, 33), (17, 30), (13, 34), (10, 30)], "coat")
    rect(d, (15, 24, 20, 29), "shirt")
    poly(d, [(22, 21), (26, 24), (26, 33), (23, 34), (21, 27)], "coat")
    rect(d, (24, 31, 26, 34), "skin")
    rect(d, (23, 34, 26, 36), "coat_dark")
    poly(d, [(11, 18), (21, 18), (23, 22), (18, 25), (12, 23)], "teal_dark")
    poly(d, [(12, 19), (21, 19), (21, 22), (17, 23)], "teal")
    poly(d, [(22, 22), (26, 24), (28, 28), (26, 30), (21, 24)], "teal_dark")
    rect(d, (24, 25, 25, 26), "teal_light")
    poly(d, [(12, 9), (16, 7), (21, 8), (23, 12),
             (24, 14), (22, 18), (18, 20), (12, 18), (10, 14)], "skin")
    rect(d, (19, 15, 23, 16), "skin_light")
    poly(d, [(9, 10), (13, 6), (19, 6), (23, 10),
             (23, 13), (20, 10), (17, 9), (14, 12), (10, 15)], "hair_dark")
    poly(d, [(12, 8), (17, 7), (20, 9), (17, 10), (13, 11)], "hair")
    px(d, [(13, 7), (17, 8)], "hair_light")
    px(d, [(21, 14)], "edge")
    px(d, [(22, 18)], "skin_shadow")
    rect(d, (10, 30, 22, 31), "coat_dark")
    rect(d, (16, 30, 17, 31), "metal")
    px(d, [(12, 25)], "teal_light")
    return im


def main():
    entries = []
    environment = ROOT / "game" / "assets" / "environments" / (
        "rpg-2-star-ocean-the-second_scifi-city_environment-background_"
        "m8-v02_20261013-232003-48d0ab67.png"
    )
    # The same 640x360 logical target used by the Godot exploration scene.
    background = Image.open(environment).convert("RGBA").resize(
        (640, 360), Image.Resampling.LANCZOS
    )
    for facing, maker in [("south", south), ("west", west),
                          ("north", north), ("east", east)]:
        image = maker()
        assert image.size == (32, 48)
        assert image.mode == "RGBA"
        assert image.getpixel((12, 44))[3] > 0
        assert image.getpixel((20, 44))[3] > 0
        assert image.getpixel((0, 0))[3] == 0
        name = f"{SLUG}_native-idle-{facing}_m8-prototype_{STAMP}-{uuid4().hex[:8]}.png"
        path = OUT / name
        image.save(path, optimize=True)
        entries.append((facing, path))
        review = background.copy()
        ground = Image.new("RGBA", review.size, (0, 0, 0, 0))
        shade = ImageDraw.Draw(ground)
        shade.ellipse((312, 225, 328, 231), fill=(16, 30, 31, 90))
        review.alpha_composite(ground)
        # No sprite scaling or interpolation: one authored pixel = one scene pixel.
        review.alpha_composite(image, (304, 185))
        preview_name = (
            f"{SLUG}_native-idle-{facing}-city-review-640x360_"
            f"m8-prototype_{STAMP}-{uuid4().hex[:8]}.png"
        )
        review.save(PREVIEW / preview_name, optimize=True)
        print(f"preview-{facing}: {PREVIEW / preview_name}")
    for facing, path in entries:
        print(f"{facing}: {path}")


if __name__ == "__main__":
    main()
