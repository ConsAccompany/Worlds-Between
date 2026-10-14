"""Hand-place Liang Xu's native 32x48 exploration pixels.

This is authored at the game resolution; no concept artwork is resampled.
"""

from pathlib import Path
import json
from PIL import Image, ImageDraw


OUT = Path(__file__).parent
STEM = "rpg-2-star-ocean-the-second_liang-xu_native-idle"
STAMP = "m8-v03_20261014-175132"
IDS = {"south": "e17b4c09", "west": "b52910e1", "north": "c742d602", "east": "d853a711"}
PREVIEW_IDS = {"south": "f3128e01", "west": "f3128e02", "north": "f3128e03", "east": "f3128e04"}

P = {
    "ink": "#161923", "hair": "#302e35", "hair_dark": "#22242d",
    "hair_light": "#514a50", "silver": "#dfd8d3", "silver_mid": "#a8adb4",
    "skin": "#d9a681", "skin_shade": "#a96f58", "skin_light": "#efc6a1",
    "coat": "#363c43", "coat_lit": "#51565b", "coat_shade": "#242b35",
    "navy": "#263851", "navy_light": "#3e5875", "copper": "#d2a16d",
    "copper_dark": "#79533f", "boot": "#292b31", "boot_lit": "#4b4546",
    "eye": "#21272e",
}


def polygon(d, points, fill, outline=None):
    d.polygon(points, fill=P[fill], outline=P[outline] if outline else None)


def rect(d, box, fill, outline=None):
    d.rectangle(box, fill=P[fill], outline=P[outline] if outline else None)


def base(direction):
    im = Image.new("RGBA", (32, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if direction in ("south", "north"):
        # Boots start below coat but terminate on the shared (16, 44) anchor.
        rect(d, (10, 39, 15, 44), "ink")
        rect(d, (17, 39, 22, 44), "ink")
        rect(d, (11, 40, 14, 43), "boot")
        rect(d, (18, 40, 21, 43), "boot")
        rect(d, (11, 40, 11, 42), "boot_lit")
        rect(d, (18, 40, 18, 42), "boot_lit")
        # Long, asymmetric coat tail creates a distinct narrow inverted V.
        polygon(d, [(9, 28), (23, 28), (24, 42), (19, 41),
                    (17, 36), (15, 41), (8, 42)], "coat_shade", "ink")
        polygon(d, [(10, 30), (16, 33), (15, 39), (9, 40)], "coat")
        polygon(d, [(18, 33), (23, 29), (23, 40), (19, 39)], "navy")
        d.line([(17, 33), (17, 39)], fill=P["copper_dark"], width=1)
        # Wider angular shoulders and forearms.
        polygon(d, [(10, 19), (7, 21), (5, 31), (8, 33),
                    (11, 28), (11, 22)], "coat", "ink")
        polygon(d, [(21, 19), (25, 21), (27, 31), (24, 33),
                    (21, 28), (21, 22)], "coat", "ink")
        rect(d, (6, 28, 8, 30), "coat_lit")
        rect(d, (24, 28, 26, 30), "coat_lit")
        rect(d, (6, 32, 8, 34), "skin", "ink")
        rect(d, (24, 32, 26, 34), "skin", "ink")
        polygon(d, [(11, 19), (21, 19), (23, 34), (17, 37),
                    (9, 34)], "coat", "ink")
        rect(d, (11, 22, 12, 31), "coat_lit")
        rect(d, (20, 22, 21, 30), "coat_lit")
    else:
        # Side view retains the same feet and ankle height.
        rect(d, (12, 40, 17, 44), "ink")
        rect(d, (17, 40, 23, 44), "ink")
        rect(d, (13, 40, 16, 43), "boot")
        rect(d, (18, 40, 22, 43), "boot")
        polygon(d, [(10, 27), (21, 27), (23, 41), (17, 39),
                    (11, 42), (8, 40)], "coat_shade", "ink")
        polygon(d, [(9, 31), (13, 30), (15, 39), (10, 40)], "coat")
        polygon(d, [(15, 30), (21, 29), (22, 39), (17, 38)], "navy")
        polygon(d, [(10, 19), (19, 19), (23, 32), (16, 36),
                    (8, 33)], "coat", "ink")
        polygon(d, [(11, 20), (7, 24), (7, 32), (10, 34),
                    (13, 30)], "coat_lit", "ink")
        rect(d, (7, 33, 10, 35), "skin", "ink")
        d.line([(12, 21), (13, 31)], fill=P["coat_lit"], width=1)
    return im, d


def south():
    im, d = base("south")
    # Stand-up collar carries the copper throat ring.
    polygon(d, [(10, 17), (13, 19), (19, 19), (22, 17),
                (23, 24), (19, 23), (16, 25), (12, 23), (9, 24)], "coat_shade", "ink")
    rect(d, (15, 20, 17, 22), "copper")
    rect(d, (16, 20, 16, 21), "copper_dark")
    d.line([(16, 24), (16, 34)], fill=P["copper_dark"], width=1)
    rect(d, (15, 30, 16, 31), "copper")
    # Neck, face and high pulled-back bun with a right-hand overhang.
    rect(d, (13, 16, 19, 20), "skin_shade", "ink")
    polygon(d, [(11, 9), (20, 8), (22, 11), (21, 16),
                (18, 19), (13, 18), (10, 15)], "skin", "ink")
    rect(d, (13, 14, 18, 15), "skin_light")
    rect(d, (12, 13, 13, 13), "eye")
    rect(d, (19, 13, 20, 13), "eye")
    d.point((16, 17), fill=P["skin_shade"])
    polygon(d, [(10, 10), (11, 6), (15, 5), (19, 6),
                (22, 10), (21, 13), (20, 10), (18, 9),
                (15, 10), (12, 12), (10, 15)], "hair", "ink")
    rect(d, (15, 5, 18, 6), "hair_light")
    polygon(d, [(18, 5), (19, 2), (22, 2), (25, 4),
                (25, 7), (22, 9), (20, 8)], "hair", "ink")
    rect(d, (21, 3, 23, 4), "hair_light")
    # Four-pixel broad unilateral silver forelock, not a one-pixel highlight.
    polygon(d, [(10, 8), (12, 6), (15, 7), (16, 8),
                (13, 10), (12, 15), (10, 17), (9, 14)], "silver", "ink")
    d.line([(11, 9), (11, 15)], fill=P["silver_mid"], width=1)
    # Field tablet reinforces her mentor / researcher identity.
    polygon(d, [(23, 25), (28, 24), (29, 34), (24, 35)], "ink", "copper_dark")
    rect(d, (24, 26, 27, 32), "navy")
    d.line([(25, 27), (27, 27)], fill=P["navy_light"], width=1)
    return im


def north():
    im, d = base("north")
    polygon(d, [(10, 17), (22, 17), (23, 24), (19, 23),
                (16, 22), (12, 23), (9, 24)], "coat_shade", "ink")
    polygon(d, [(11, 22), (21, 22), (21, 34), (17, 37),
                (10, 34)], "coat", "ink")
    d.line([(16, 22), (16, 36)], fill=P["navy"], width=2)
    rect(d, (15, 24, 17, 26), "copper")
    rect(d, (16, 25, 16, 25), "coat_shade")
    d.line([(11, 28), (12, 32)], fill=P["coat_lit"], width=1)
    d.line([(20, 28), (21, 32)], fill=P["coat_lit"], width=1)
    rect(d, (13, 16, 19, 20), "skin_shade", "ink")
    polygon(d, [(10, 8), (14, 5), (20, 5), (23, 9),
                (22, 17), (19, 20), (12, 19), (9, 16)], "hair", "ink")
    polygon(d, [(19, 4), (20, 2), (24, 2), (26, 5),
                (25, 8), (22, 9), (19, 7)], "hair", "ink")
    rect(d, (21, 3, 23, 4), "hair_light")
    d.line([(14, 8), (20, 8)], fill=P["hair_light"], width=1)
    # Silver wedge emerges from the left temple and stays visible from behind.
    polygon(d, [(11, 7), (14, 6), (15, 9), (13, 12),
                (12, 16), (9, 17), (9, 11)], "silver", "ink")
    d.line([(11, 10), (11, 15)], fill=P["silver_mid"], width=1)
    # Tablet tucked by her right hip.
    polygon(d, [(23, 27), (27, 28), (27, 35), (24, 35)], "ink", "copper_dark")
    rect(d, (24, 29, 26, 33), "navy")
    return im


def side(direction):
    im, d = base(direction)
    east = direction == "east"
    # Side profiles are placed independently, never mirrored from each other.
    if east:
        polygon(d, [(12, 17), (17, 19), (20, 18), (23, 23),
                    (19, 24), (16, 25), (11, 23)], "coat_shade", "ink")
        polygon(d, [(13, 8), (20, 8), (23, 12), (23, 16),
                    (20, 19), (14, 18), (11, 15)], "skin", "ink")
        rect(d, (21, 13, 22, 13), "eye")
        polygon(d, [(10, 10), (12, 6), (18, 5), (21, 8),
                    (20, 11), (16, 10), (13, 14), (11, 17)], "hair", "ink")
        polygon(d, [(10, 4), (12, 2), (16, 2), (18, 5),
                    (16, 8), (12, 8)], "hair", "ink")
        polygon(d, [(17, 6), (20, 7), (21, 10), (19, 13),
                    (19, 18), (17, 19), (16, 16), (17, 11)], "silver", "ink")
        d.line([(18, 9), (18, 16)], fill=P["silver_mid"], width=1)
        rect(d, (19, 21, 21, 23), "copper")
        polygon(d, [(22, 26), (27, 25), (28, 34), (23, 35)], "ink", "copper_dark")
        rect(d, (24, 27, 26, 32), "navy")
    else:
        polygon(d, [(11, 18), (15, 18), (20, 17), (21, 23),
                    (16, 25), (12, 24), (9, 22)], "coat_shade", "ink")
        polygon(d, [(10, 11), (13, 8), (20, 8), (22, 15),
                    (19, 18), (12, 19), (9, 16)], "skin", "ink")
        rect(d, (9, 13, 10, 13), "eye")
        polygon(d, [(10, 9), (13, 6), (19, 5), (22, 10),
                    (22, 16), (19, 14), (17, 10), (12, 11)], "hair", "ink")
        polygon(d, [(18, 4), (20, 2), (23, 2), (25, 5),
                    (24, 8), (20, 8)], "hair", "ink")
        polygon(d, [(10, 8), (13, 6), (14, 8), (12, 12),
                    (11, 17), (9, 17), (8, 13)], "silver", "ink")
        d.line([(10, 10), (10, 15)], fill=P["silver_mid"], width=1)
        rect(d, (12, 21, 14, 23), "copper")
        polygon(d, [(4, 25), (9, 26), (9, 35), (4, 34)], "ink", "copper_dark")
        rect(d, (5, 27, 7, 32), "navy")
    return im


def main():
    entries = []
    for direction, make in (("south", south), ("west", lambda: side("west")),
                            ("north", north), ("east", lambda: side("east"))):
        path = OUT / f"{STEM}-{direction}_{STAMP}-{IDS[direction]}.png"
        im = make()
        assert im.size == (32, 48)
        assert any(im.getpixel((x, 44))[3] > 0 for x in range(10, 24))
        assert im.getpixel((0, 0))[3] == 0
        im.save(path)
        print(path)
        preview = ("rpg-2-star-ocean-the-second_liang-xu_native-game-preview-"
                   f"{direction}_m8-v03_20261014-180100-{PREVIEW_IDS[direction]}.png")
        entries.append({"direction": direction, "path": path.name,
                        "preview": "outputs/" + preview, "size": [32, 48],
                        "anchor": [16, 44], "stage": "directional_idle_prototype"})
    manifest = OUT / "rpg-2-star-ocean-the-second_liang-xu_native-idle-manifest_m8-v03_20261014-180100-9d804f2a.json"
    manifest.write_text(json.dumps({"character_id": "liang_xu", "generator": Path(__file__).name,
                                    "source": "hand-authored-native-pixels", "frames": entries},
                                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(manifest)


if __name__ == "__main__":
    main()
