"""Yonkers outskirts survey annex room 1 (天线走廊 / Antenna Walkway): native pixel-art v03 scene.

v03 is a bounded art pass over v02 (creator: "继续精修室外画面"). Same layer stack, sprite boxes,
clue markers, props and collision footprints; changed: a back-lit parapet with coping overhang,
drip shadow, rain streaks, spalls and a jagged cast shadow on the deck; localized deck wear
(traffic polish, damp wall foot, cracks, chipped corners, rust drips, clustered moss) instead of
even grain; an authored grating rhythm (unequal panels, three panel types, glints only where lit);
a foreshortened concave dish B (inner rim shadow, lit far wall, back shell, rear truss, feed
shadow); antennas A and C recomposed so no texel sits above y 66 (the HUD covers y 0-61).

One 640x360 Pixelorama/OpenRaster project, built only from hand-placed primitives in this file
(rects, lines, ellipses, polygons and seeded pixel texture). No generated, traced, resampled or
palette-reduced image is used anywhere (the nonruntime material-depth reference was read only as
art direction). Every layer has binary alpha.

Layers, bottom to top (runtime export in brackets):
  1-9   sky, back parapet, wall kit, deck, walkway, deck detail, cast shadows, doors, front
        parapet                                                     [flattened -> corridor plate]
  10-12 antenna A lattice Yagi, antenna B dish, antenna C guyed whip [each cropped 128x152 ->
        a y-sorted sprite anchored at (clue x, 210)]
  13    foreground occluder (corner shrubs on the front parapet)     [drawn above the heroine]

Usage: python -I <this file>
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import random
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261017-224447-15709be4"
VERSION = "v03"
PREFIX = "rpg-2-star-ocean-the-second_yonkers-antenna-room1"
OUT = ROOT / "outputs" / "yonkers-room1-v03_15709be4"
RUNTIME_ENV = ROOT / "game/assets/environments/yonkers-antenna-room1"
RUNTIME_PROPS = ROOT / "game/assets/props/yonkers-antenna-room1"
PIXELORAMA_VERSION = "v1.2.3-stable"
W, H = 640, 360

# Clue x positions are the unchanged runtime CLUE_POSITIONS x; antennas stand on a shared base line.
ANTENNA_X = (163, 320, 477)
BASE_Y = 210  # first deck row in front of every plinth; sprite anchor y (y-sort key)
SPRITE_TOP = 58  # sprite boxes stay y 58..209 (same Sprite2D offset as v02) ...
HUD_BOTTOM = 62  # ... but the 62 px header must hide nothing:
ART_TOP = 66  # no antenna texel above y 66 (4 px clear of the header edge)
SPRITE_W, SPRITE_H = 128, BASE_Y - SPRITE_TOP

HEX = {
    # sky and distant ridge
    "sky0": "#7aa3b4", "sky1": "#93b7c2", "sky2": "#adcbcb", "cloud": "#dbe7df", "cloud_sh": "#b9cdc8",
    "hill_far": "#7f9c98", "hill": "#64837b", "hill_dk": "#4f6c64",
    "tree_far": "#4a6b54", "tree": "#3a5a44", "tree_dk": "#2b4536", "tree_hi": "#628456",
    # warm masonry, one step darker than v02: the sun is behind the parapet, so its face is in shade
    "st_hi": "#bfb08c", "st": "#9c9073", "st_mid": "#81785f", "st_dk": "#645e4c", "st_deep": "#47443a", "mortar": "#33342d",
    "lichen": "#9a9d72",
    # deck slabs (cooler, mossy) plus localized wear: traffic polish, damp stain, rust drip
    "dk_hi": "#878b76", "dk_a": "#747966", "dk_b": "#6c715e", "dk_c": "#646957", "dk_seam": "#474c40",
    "dk_sh": "#55594b", "dk_sh2": "#45493d", "dk_worn": "#7f8472", "dk_wet": "#4f5749", "dk_rust": "#6a5843",
    # walkway grating
    "gr_hi": "#7f8d87", "gr": "#56645f", "gr_mid": "#4a5755", "gr_dk": "#3a4646", "gr_hole": "#222b2d",
    "gr_glint": "#b9c8c0", "plate": "#6f7c78", "plate_hi": "#93a29b",
    # restrained teal technology (accepted room 2 kit)
    "ink": "#151d21", "deep": "#263239", "slate": "#34434a", "steel": "#526269", "edge": "#839087",
    "teal_dk": "#1b5c68", "teal": "#4fa5a2", "glow": "#8be9d7",
    "br_dk": "#674927", "br": "#a67b3d", "br_hi": "#d6af64",
    "wood": "#514031", "wood_hi": "#806247",
    # foliage
    "lf_dk": "#223b2a", "lf": "#355a33", "lf_mid": "#4f7a3c", "lf_hi": "#7a9d4c", "moss": "#5c6b3b", "moss_hi": "#7e8b4d",
    "moss_dk": "#46532f",
    "flower": "#e8e2c4",
    # clue accents
    "warn": "#d58b4c", "warn_dk": "#7c4a2f", "frost": "#dcecea", "frost_mid": "#a6c4c8",
    "paper": "#d7c7a5", "paper_dk": "#a99b7e", "rust": "#8a5a3a",
}
RGB = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in HEX.items()}
RGBA = {k: np.array(v + (255,), np.uint8) for k, v in RGB.items()}

SCENE_LAYERS = [
    "sky-and-ridge", "back-parapet-masonry", "wall-kit-and-ivy", "deck-slabs", "walkway-grating-and-trench",
    "deck-detail-cables-moss", "cast-shadows", "doors-and-side-walls", "front-parapet",
    "antenna-a-lattice-yagi", "antenna-b-dish", "antenna-c-guyed-whip", "foreground-occluder",
]
PLATE_LAYERS = SCENE_LAYERS[:9]
ANTENNA_LAYERS = SCENE_LAYERS[9:12]


class Layer:
    def __init__(self):
        self.a = np.zeros((H, W, 4), np.uint8)

    def px(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < W and 0 <= y < H:
            self.a[y, x] = RGBA[c]

    def rect(self, x0, y0, x1, y1, c):
        """Inclusive fill."""
        x0, y0, x1, y1 = max(int(x0), 0), max(int(y0), 0), min(int(x1), W - 1), min(int(y1), H - 1)
        if x1 >= x0 and y1 >= y0:
            self.a[y0:y1 + 1, x0:x1 + 1] = RGBA[c]

    def box(self, x0, y0, x1, y1, fill, outline="ink"):
        self.rect(x0, y0, x1, y1, outline)
        self.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill)

    def hline(self, x0, x1, y, c):
        self.rect(min(x0, x1), y, max(x0, x1), y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, min(y0, y1), x, max(y0, y1), c)

    def line(self, x0, y0, x1, y1, c):
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def shape(self, draw_fn, c):
        m = Image.new("L", (W, H), 0)
        draw_fn(ImageDraw.Draw(m))
        self.a[np.array(m) > 0] = RGBA[c]

    def ellipse(self, x0, y0, x1, y1, c):
        self.shape(lambda d: d.ellipse((x0, y0, x1, y1), fill=255), c)

    def poly(self, pts, c):
        self.shape(lambda d: d.polygon([(int(round(x)), int(round(y))) for x, y in pts], fill=255), c)

    def name_at(self, x, y):
        if self.a[y, x, 3] == 0:
            return None
        return NAME_OF[tuple(int(v) for v in self.a[y, x, :3])]


NAME_OF = {v: k for k, v in RGB.items()}


def composite(layers):
    out = np.zeros((H, W, 4), np.uint8)
    for lay in layers:
        m = lay.a[..., 3] == 255
        out[m] = lay.a[m]
    return out


# ----------------------------------------------------------------------------- foliage helpers
def clump_mass(lay, rng, cx, cy, rx, ry, count, light=True, flowers=0):
    """Pixel foliage: dark mass, mid clumps offset up-left, a few lit leaves and optional flowers."""
    clumps = []
    for _ in range(count):
        a = rng.uniform(0, math.tau)
        r = math.sqrt(rng.random())
        clumps.append((cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r, rng.randint(2, 4)))
    clumps.sort(key=lambda c: c[1])
    for x, y, r in clumps:
        lay.ellipse(x - r, y - r + 1, x + r, y + r, "lf_dk")
    for x, y, r in clumps:
        if r >= 3:
            lay.ellipse(x - r + 1, y - r + 1, x + r - 2, y + r - 2, "lf")
    if light:
        for x, y, r in clumps:
            if y < cy + ry * 0.35:
                lay.px(x - r + 2, y - r + 1, "lf_mid")
                lay.px(x - r + 3, y - r + 1, "lf_mid")
                lay.px(x - r + 2, y - r + 2, "lf_mid")
                if rng.random() < 0.55:
                    lay.px(x - r + 2, y - r + 1, "lf_hi")
    for _ in range(flowers):
        x, y, _r = rng.choice(clumps)
        lay.px(x, y - 1, "flower")


def tendril(lay, rng, x, y, length):
    for i in range(length):
        x += rng.choice((-1, 0, 0, 0, 1)) * (1 if i % 3 == 0 else 0)
        lay.px(x, y + i, "lf_dk")
        if i % 3 == 1:
            side = rng.choice((-1, 1))
            lay.px(x + side, y + i, "lf_mid" if rng.random() < 0.5 else "lf")
            lay.px(x + side, y + i + 1, "lf")
    lay.px(x, y + length, "lf")


# ----------------------------------------------------------------------------- 1 sky and ridge
def sky_layer(rng):
    L = Layer()
    for y in range(0, 104):
        for x in range(W):
            if y < 70:
                c = "sky0" if not (y >= 67 and (x + y) % 2 == 0 and y % 2 == 1) else "sky1"
            elif y < 84:
                c = "sky1" if not (y >= 81 and (x + y) % 2 == 0) else "sky2"
            else:
                c = "sky2"
            L.a[y, x] = RGBA[c]
    # clouds: flat-bottomed puffs
    for cx, cy, w in [(62, 72, 34), (210, 66, 46), (372, 70, 30), (452, 64, 40), (604, 70, 34)]:
        for i in range(5):
            ox = int((i - 2) * w / 5)
            r = int(w / 5) + (3 if i in (1, 2, 3) else 0) - abs(i - 2)
            L.ellipse(cx + ox - r, cy - r, cx + ox + r, cy + 3, "cloud")
        L.rect(cx - w // 2, cy + 2, cx + w // 2, cy + 3, "cloud_sh")
    # far ridge, near ridge
    for x in range(W):
        yf = int(84 + 4 * math.sin(x / 41.0) + 3 * math.sin(x / 17.0 + 1.3))
        L.rect(x, yf, x, 103, "hill_far")
        yn = int(91 + 3 * math.sin(x / 29.0 + 2.0) + 2 * math.sin(x / 11.0))
        L.rect(x, yn, x, 103, "hill")
        if (x * 7) % 5 == 0:
            L.px(x, yn, "hill_far")
    # distant relay towers on the far ridge (the signal network this walkway belongs to)
    for tx, base, ht in [(266, 92, 20), (598, 92, 16), (40, 90, 12)]:
        L.line(tx - 3, base, tx, base - ht, "hill_dk")
        L.line(tx + 3, base, tx, base - ht, "hill_dk")
        for yy in range(base - ht + 3, base, 4):
            half = int(3 * (yy - (base - ht)) / ht)
            L.hline(tx - half, tx + half, yy, "hill_dk")
        L.px(tx, base - ht - 1, "hill_dk")
        L.px(tx + 1, base - ht + 2, "hill_dk")
    # treeline just behind the parapet
    for x in range(-4, W + 6, 5):
        cx, cy, r = x + rng.randint(-2, 2), 97 + rng.randint(-3, 2), rng.randint(4, 6)
        L.ellipse(cx - r, cy - r, cx + r, cy + r + 6, "tree")
    for x in range(-4, W + 6, 7):
        cx, cy, r = x + rng.randint(-2, 2), 95 + rng.randint(-2, 3), rng.randint(2, 3)
        L.ellipse(cx - r, cy - r, cx + r, cy + r, "tree_far")
        L.px(cx - 1, cy - r, "tree_hi")
    for x in range(W):
        for y in range(99, 104):
            if (x + y * 3) % 4 == 0:
                L.px(x, y, "tree_dk")
    return L


# ----------------------------------------------------------------------------- 2 back parapet
PILASTERS = (88, 241, 398, 556)


def masonry(L, rng, x0, x1, y0, y1, course=9, tones=("st", "st", "st_mid", "st_mid", "st_dk"), shade_rows=0):
    y = y0
    row = 0
    while y <= y1:
        h = min(course, y1 - y + 1)
        x = x0 - (rng.randint(0, 12) if row % 2 else 0)
        while x <= x1:
            w = rng.randint(16, 28)
            tone = rng.choice(tones)
            if shade_rows and y > y1 - shade_rows * course:
                tone = {"st": "st_mid", "st_mid": "st_dk", "st_dk": "st_dk"}[tone]
            bx0, bx1 = max(x, x0), min(x + w - 1, x1)
            if bx1 >= bx0:
                L.rect(bx0, y, bx1, y + h - 1, tone)
                L.hline(bx0, bx1, y + h - 1, "mortar")
                if x + w - 1 <= x1:
                    L.vline(bx1, y, y + h - 1, "mortar")
                lit = {"st": "st_hi", "st_mid": "st", "st_dk": "st_mid"}[tone]
                dark = {"st": "st_mid", "st_mid": "st_dk", "st_dk": "st_deep"}[tone]
                L.hline(bx0, bx1 - 1, y, lit)
                L.hline(bx0, bx1 - 1, y + h - 2, dark)
                for _ in range((bx1 - bx0) * h // 14):
                    L.px(rng.randint(bx0, bx1 - 1), rng.randint(y + 1, y + h - 3), dark if rng.random() < 0.7 else lit)
            x += w
        y += h
        row += 1


DARKER = {"st_hi": "st", "st": "st_mid", "st_mid": "st_dk", "st_dk": "st_deep", "st_deep": "mortar", "mortar": "mortar",
          "lichen": "st_mid"}
LIGHTER = {"st": "st_hi", "st_mid": "st", "st_dk": "st_mid", "st_deep": "st_dk", "mortar": "st_deep", "st_hi": "st_hi"}


def shade_wall(L, rng, x0, x1, y0, y1, course, tones, under_coping=0):
    """Masonry seen against the light: block tops pick up a little sky light on part of their width,
    weathering comes as small clusters (not salt-and-pepper), the courses under the coping sit in its shadow."""
    y = y0
    row = 0
    while y <= y1:
        h = min(course, y1 - y + 1)
        x = x0 - (rng.randint(0, 14) if row % 2 else rng.randint(0, 4))
        while x <= x1:
            w = rng.randint(14, 34)
            tone = rng.choice(tones)
            if y < y0 + under_coping:
                tone = DARKER[tone]
            bx0, bx1 = max(x, x0), min(x + w - 1, x1)
            if bx1 >= bx0:
                L.rect(bx0, y, bx1, y + h - 1, tone)
                L.hline(bx0, bx1, y + h - 1, "mortar")
                if x + w - 1 <= x1:
                    L.vline(bx1, y, y + h - 1, "mortar")
                # sky light on the upper arris of part of the block only
                lit_to = bx0 + int((bx1 - bx0) * rng.uniform(0.35, 0.8))
                L.hline(bx0, lit_to, y, LIGHTER[tone])
                L.hline(bx0 + 1, bx1 - 1, y + h - 2, DARKER[tone])
                for _ in range(max(1, (bx1 - bx0) // 16)):
                    cx, cy = rng.randint(bx0 + 1, max(bx0 + 1, bx1 - 3)), rng.randint(y + 2, max(y + 2, y + h - 4))
                    L.rect(cx, cy, cx + rng.randint(0, 2), cy + rng.randint(0, 1), DARKER[tone])
            x += w
        y += h
        row += 1


def streaks(L, rng, xs, y0, max_len, avoid=()):
    """Rain streaks: one tone darker than whatever is there, dithering out at the tail."""
    for x in xs:
        if any(a0 <= x <= a1 for a0, a1 in avoid):
            continue
        n = rng.randint(max_len // 4, max_len)
        width = 2 if rng.random() < 0.3 else 1
        for i in range(n):
            if i > n * 0.65 and (i + x) % 2:
                continue
            for dx in range(width):
                name = L.name_at(x + dx, y0 + i)
                if name in DARKER:
                    L.px(x + dx, y0 + i, DARKER[name])


def spall(L, x, y, w, h):
    """A spalled patch: shadowed recess under the broken top edge, lit lower lip."""
    L.rect(x, y, x + w, y + h, "st_dk")
    L.hline(x + 1, x + w - 1, y, "st_deep")
    L.vline(x, y, y + h - 1, "st_deep")
    L.hline(x + 1, x + w, y + h, "st")
    L.px(x + w // 2, y + 1, "mortar")


def parapet_layer(rng):
    L = Layer()
    # coping: lit top (rows 99-101), front face (102-105), drip edge and underside (106-107)
    L.rect(0, 99, W - 1, 101, "st_hi")
    L.rect(0, 102, W - 1, 105, "st")
    L.hline(0, W - 1, 106, "st_deep")
    L.hline(0, W - 1, 107, "mortar")
    x = -rng.randint(0, 20)
    while x < W:
        w = rng.randint(24, 38)
        L.vline(x, 101, 105, "st_dk")
        L.px(x + 1, 102, "st_hi")
        if rng.random() < 0.35:  # chipped lower corner on the front face
            L.rect(x + 1, 104, x + rng.randint(2, 4), 105, "st_dk")
            L.px(x + 1, 106, "st_mid")
        if rng.random() < 0.5:  # broad weathering on the face
            sx = x + rng.randint(4, max(5, w - 8))
            L.hline(sx, sx + rng.randint(3, 8), 104, "st_mid")
        x += w
    for _ in range(26):  # notches in the top arris (sky shows through)
        cx = rng.randint(0, W - 3)
        L.a[99, cx:cx + rng.randint(1, 3), 3] = 0
        L.px(cx, 100, "st")
    for _ in range(34):  # lichen and pitting on the lit top
        cx, cy = rng.randint(0, W - 3), rng.randint(99, 101)
        L.px(cx, cy, "lichen" if rng.random() < 0.6 else "st")
        if rng.random() < 0.5:
            L.px(cx + 1, cy, "lichen")
    # wall face in shade; the first three courses under the coping are darker still
    shade_wall(L, rng, 0, W - 1, 108, 151, course=9, tones=("st_mid", "st_mid", "st_dk", "st_dk", "st"), under_coping=4)
    L.rect(0, 152, W - 1, 155, "st_deep")
    L.hline(0, W - 1, 152, "st_dk")
    for x in range(0, W, 3):  # damp line at the wall foot
        if rng.random() < 0.6:
            L.px(x, 155, "mortar")
    for x, y, w, h in [(140, 127, 6, 3), (214, 136, 5, 3), (318, 118, 7, 4), (455, 129, 5, 3), (528, 140, 6, 3), (108, 145, 4, 2)]:
        spall(L, x, y, w, h)
    piers = [(p - 2, p + 22) for p in PILASTERS]
    streaks(L, rng, sorted(rng.sample(range(2, W - 2), 46)), 108, 30, piers)
    # pilasters: lit west face, shaded front, capped with an overhanging stone that shadows its own top course
    for px0 in PILASTERS:
        L.rect(px0 - 2, 92, px0 + 17, 93, "st_hi")
        L.rect(px0 - 2, 94, px0 + 17, 96, "st")
        L.hline(px0 - 2, px0 + 17, 97, "st_deep")
        L.hline(px0 - 1, px0 + 16, 98, "mortar")
        L.px(px0 - 2, 92, "st")
        L.rect(px0, 99, px0 + 15, 155, "st_mid")
        L.rect(px0, 99, px0 + 2, 155, "st")
        L.vline(px0, 99, 155, "st_hi")
        L.rect(px0 + 12, 99, px0 + 15, 155, "st_dk")
        L.vline(px0 + 15, 99, 155, "st_deep")
        L.hline(px0 + 1, px0 + 14, 99, "st_deep")
        L.hline(px0 + 3, px0 + 11, 100, "st_dk")
        for yy in range(109, 156, 10):
            L.hline(px0, px0 + 15, yy, "st_deep")
            L.px(px0 + 1, yy + 1, "st_hi")
            L.px(px0 + 2, yy + 1, "st")
        streaks(L, rng, [px0 + 5, px0 + 9], 101, 26)
        L.rect(px0 - 1, 150, px0 + 16, 157, "st_dk")
        L.hline(px0 - 1, px0 + 16, 150, "st")
        L.px(px0 - 1, 150, "st_hi")
        L.hline(px0 - 1, px0 + 16, 157, "mortar")
    return L


# ----------------------------------------------------------------------------- 3 wall kit and ivy
JUNCTION_X = (198, 360, 420)  # wall boxes feeding antenna A, B, C


def junction_box(L, x0, y0, light="glow"):
    L.box(x0, y0, x0 + 16, y0 + 20, "slate")
    L.hline(x0 + 1, x0 + 15, y0 + 1, "edge")
    L.vline(x0 + 1, y0 + 2, y0 + 19, "steel")
    L.vline(x0 + 15, y0 + 2, y0 + 19, "deep")
    L.vline(x0 + 8, y0 + 3, y0 + 18, "deep")
    L.rect(x0 + 3, y0 + 4, x0 + 6, y0 + 7, "teal_dk")
    L.px(x0 + 4, y0 + 5, light)
    L.px(x0 + 5, y0 + 5, light)
    L.rect(x0 + 10, y0 + 9, x0 + 11, y0 + 12, "br")
    L.rect(x0 + 6, y0 + 21, x0 + 10, y0 + 22, "deep")  # conduit gland


def wall_kit_layer(rng):
    L = Layer()
    # cable tray along the wall, broken by the pilasters
    spans = [(38, 87), (105, 240), (258, 397), (415, 555), (573, 601)]
    for x0, x1 in spans:
        L.hline(x0, x1, 116, "deep")
        for x in range(x0, x1 + 1):
            if (x // 3) % 3 != 0:
                L.px(x, 115, "ink" if (x // 7) % 2 else "deep")
        L.hline(x0, x1, 117, "edge")
        L.rect(x0, 118, x1, 119, "slate")
        L.hline(x0, x1, 120, "ink")
        for x in range(x0 + 6, x1, 30):
            L.rect(x, 121, x + 1, 124, "br_dk")
            L.px(x, 121, "br")
    # brass service pipe with flanges
    for x0, x1 in [(105, 240), (415, 555)]:
        L.hline(x0, x1, 139, "br_hi")
        L.hline(x0, x1, 140, "br")
        L.hline(x0, x1, 141, "br_dk")
        for x in range(x0 + 10, x1, 34):
            L.rect(x, 138, x + 2, 142, "br")
            L.vline(x, 138, 142, "br_hi")
            L.vline(x + 2, 138, 142, "br_dk")
    # junction boxes and their conduits down to the deck
    for i, x0 in enumerate(JUNCTION_X):
        junction_box(L, x0, 124, "warn" if i == 0 else "glow")
        cx = x0 + 8
        L.vline(cx - 1, 147, 156, "edge")
        L.vline(cx, 147, 156, "steel")
        L.vline(cx + 1, 147, 156, "deep")
    # west patch cabinet
    L.box(46, 112, 72, 153, "teal_dk")
    L.hline(47, 71, 113, "teal")
    L.vline(47, 114, 152, "teal")
    L.vline(59, 115, 151, "ink")
    for yy in range(120, 146, 4):
        L.hline(50, 56, yy, "deep")
        L.hline(62, 69, yy, "deep")
    L.px(51, 116, "glow")
    L.px(53, 116, "glow")
    L.px(64, 116, "warn")
    L.rect(57, 130, 58, 134, "br_hi")
    L.rect(45, 150, 73, 155, "deep")
    # east switch cabinet near the maintenance door
    L.box(574, 110, 598, 154, "slate")
    L.hline(575, 597, 111, "edge")
    L.vline(575, 112, 153, "steel")
    L.rect(578, 116, 594, 128, "teal_dk")
    for i, x in enumerate(range(580, 594, 3)):
        L.rect(x, 118, x + 1, 126 - (i % 3) * 2, "glow" if i < 3 else "teal")
    L.hline(578, 594, 132, "deep")
    for yy in range(136, 150, 3):
        L.hline(579, 593, yy, "deep")
    L.rect(595, 138, 596, 142, "br_hi")
    # enamel sign beside the dish: antenna glyph
    L.box(262, 110, 284, 124, "teal_dk")
    L.hline(263, 283, 111, "teal")
    L.vline(273, 113, 121, "paper")
    L.line(268, 114, 273, 117, "paper")
    L.line(278, 114, 273, 117, "paper")
    L.hline(270, 276, 121, "paper")
    L.px(266, 113, "paper_dk")
    L.px(280, 113, "paper_dk")
    # ivy over the coping and down the wall
    for cx, cy, rx, ry, n, fl in [(12, 103, 16, 6, 18, 2), (128, 103, 18, 5, 18, 1), (300, 104, 14, 5, 12, 0),
                                  (350, 104, 12, 4, 10, 1), (452, 103, 16, 5, 14, 2), (528, 104, 14, 5, 12, 0),
                                  (620, 102, 14, 6, 14, 1)]:
        clump_mass(L, rng, cx, cy, rx, ry, n, flowers=fl)
        for k in range(rng.randint(2, 4)):
            tendril(L, rng, cx + rng.randint(-rx + 3, rx - 3), cy + 3, rng.randint(8, 26))
    for px0 in (88, 556):
        clump_mass(L, rng, px0 + 8, 98, 9, 4, 8)
        tendril(L, rng, px0 + 4, 100, 30)
        tendril(L, rng, px0 + 11, 100, 18)
    # weeds at the wall base
    for x in range(40, 600, 9):
        if rng.random() < 0.55:
            L.px(x, 155, "moss")
            L.px(x + 1, 154, "moss_hi" if rng.random() < 0.5 else "lf_mid")
            L.px(x - 1, 155, "lf")
    return L


# ----------------------------------------------------------------------------- 4 deck slabs
ROW_EDGES = [156]
for _h in (11, 12, 13, 14, 15, 16, 17, 18, 19):
    ROW_EDGES.append(ROW_EDGES[-1] + _h)  # 156 .. 291 with a perspective step


DK_LIT = {"dk_hi": "dk_hi", "dk_worn": "dk_hi", "dk_a": "dk_worn", "dk_b": "dk_a", "dk_c": "dk_b"}
DK_DARK = {"dk_hi": "dk_a", "dk_worn": "dk_a", "dk_a": "dk_b", "dk_b": "dk_c", "dk_c": "dk_sh"}
POLISH = {"dk_c": "dk_b", "dk_b": "dk_a", "dk_a": "dk_worn", "dk_worn": "dk_worn", "dk_hi": "dk_hi", "dk_sh": "dk_b",
          "dk_seam": "dk_sh"}
# Where boots actually go: the approach in front of each plinth and the two door aprons.
TRAFFIC = [(ANTENNA_X[0], 223, 44, 11), (ANTENNA_X[1], 223, 46, 11), (ANTENNA_X[2], 223, 44, 11),
           (70, 226, 40, 10), (575, 224, 36, 11), (250, 228, 60, 7), (400, 228, 60, 7)]
# Hand-placed cracks: start point and a heading; each gets a short branch and moss in its widest part.
CRACKS = [(244, 214, 1), (382, 222, 1), (548, 216, -1), (108, 229, 1), (276, 196, 1), (560, 174, -1), (140, 168, 1)]


def deck_layer(rng):
    L = Layer()
    for r in range(len(ROW_EDGES) - 1):
        y0, y1 = ROW_EDGES[r], ROW_EDGES[r + 1] - 1
        h = y1 - y0 + 1
        sw = int(round(h * 2.3))
        x = -rng.randint(0, sw) if r % 2 else -sw // 2
        while x < W:
            x1 = x + sw - 1
            # slab tone follows a slow field so neighbouring slabs weather together instead of flickering
            f = math.sin((x + sw / 2) / 57.0 + r * 0.8) + 0.6 * math.sin((x + sw / 2) / 23.0 - r * 1.4) + rng.uniform(-0.45, 0.45)
            tone = "dk_a" if f > 0.85 else ("dk_b" if f > -0.35 else "dk_c")
            if rng.random() < 0.03:
                tone = "dk_hi"
            L.rect(x, y0, x1, y1, tone)
            lit, dark = DK_LIT[tone], DK_DARK[tone]
            L.hline(x, x + int((x1 - x) * rng.uniform(0.4, 0.9)), y0, lit)
            L.vline(x, y0, y1 - 1, lit)
            L.hline(x, x1, y1, "dk_seam")
            L.vline(x1, y0, y1, "dk_seam")
            # a few small clusters of wear instead of even grain
            for _ in range(max(1, sw * h // 60)):
                cx, cy = rng.randint(x + 2, x1 - 3), rng.randint(y0 + 1, y1 - 2)
                L.rect(cx, cy, cx + rng.randint(0, 2), cy + rng.randint(0, 1), dark)
                if rng.random() < 0.3:
                    L.px(cx - 1, cy, lit)
            if rng.random() < 0.12:  # chipped corner showing the bedding below
                L.rect(x1 - rng.randint(2, 4), y1 - rng.randint(1, 2), x1 - 1, y1 - 1, "dk_sh2")
                L.px(x1 - 1, y1 - 3, "dk_seam")
            x += sw
    # traffic polish: lighter, joints filled and worn
    for cx, cy, rx, ry in TRAFFIC:
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if d < 1 and (d < 0.55 or (x * 3 + y * 5) % 4 == 0):
                    n = L.name_at(min(max(x, 0), W - 1), min(max(y, 0), H - 1))
                    if n in POLISH and not (n == "dk_seam" and rng.random() < 0.5):
                        L.px(x, y, POLISH[n])
    # damp foot of the wall: a cool stain with a ragged, dithered lower edge
    for x in range(0, W):
        depth = 6 + int(3 * math.sin(x / 19.0) + 2 * math.sin(x / 7.0 + 1.0))
        for y in range(156, 156 + depth):
            n = L.name_at(x, y)
            edge = y >= 156 + depth - 2
            if n and (not edge or (x + y) % 2 == 0):
                L.px(x, y, "dk_seam" if n == "dk_seam" else ("dk_wet" if y < 156 + depth - 3 else "dk_sh2"))
    for sx, sy, d in CRACKS:
        x, y = sx, sy
        path = []
        for i in range(rng.randint(10, 17)):
            path.append((x, y))
            x += d
            if rng.random() < 0.45:
                y += rng.choice((-1, 1))
        for i, (x, y) in enumerate(path):
            L.px(x, y, "dk_seam")
            if 3 < i < len(path) - 3:
                L.px(x, y + 1, "dk_sh2")
        bx, by = path[len(path) // 2]
        for i in range(rng.randint(3, 6)):
            by += 1
            bx += rng.choice((-1, 0, 1))
            L.px(bx, by, "dk_seam")
        mx, my = path[len(path) // 3]
        L.px(mx, my - 1, "moss")
        L.px(mx + 1, my - 1, "moss_hi")
    return L


# ----------------------------------------------------------------------------- 5 walkway grating + cable trench
WALK_Y0, WALK_Y1 = 244, 281
TRENCH_Y0, TRENCH_Y1 = 236, 242
TRENCH_X0 = 120


# Unequal panels (sum 580 px, x 30..609). Kinds: "bar" = bearing-bar grating with cross rods every `rod` px,
# "plate" = the newer chequer-plate replacement by antenna A, "old" = dull rust-stained panels by B and C.
PANELS = [(46, "bar", 6, 0.2), (52, "bar", 5, -0.1), (40, "plate", 0, 0.0), (58, "bar", 7, 0.3), (44, "bar", 6, -0.3),
          (50, "bar", 5, 0.1), (62, "old", 7, -0.6), (42, "bar", 6, 0.25), (54, "bar", 5, -0.15), (48, "old", 6, -0.5),
          (38, "bar", 7, 0.0), (46, "bar", 6, 0.35)]
# Sun glints: only on bar tops that face the light, a handful across the whole lane.
GLINTS = [(58, 250), (101, 259), (196, 253), (213, 271), (262, 256), (371, 250), (409, 265), (437, 256), (521, 262),
          (552, 250), (586, 268), (139, 274)]


def walkway_layer(rng):
    L = Layer()
    x0, x1 = 30, 609
    gy0, gy1 = WALK_Y0 + 3, WALK_Y1 - 3
    px0 = x0
    for pi, (pw, kind, rod, bright) in enumerate(PANELS):
        pxe = px0 + pw - 1
        blobs = [(px0 + rng.randint(6, pw - 6), rng.randint(gy0 + 4, gy1 - 4), rng.randint(3, 6)) for _ in range(4)] if kind == "old" else []
        missing = px0 + rng.randint(8, pw - 10) if kind == "old" else -1
        # light patches: where the sun reaches between the antennas' shadows; brighter panels get more of them
        n_patch = 0 if kind == "old" else (1 if bright < 0 else 2 + (bright > 0.25))
        patches = [(px0 + rng.randint(4, pw - 4), rng.randint(gy0 + 6, gy1 - 3), rng.randint(6, 14), rng.randint(3, 6)) for _ in range(n_patch)]
        for y in range(gy0, gy1 + 1):
            k = (y - gy0) % 3
            for x in range(px0 + 1, pxe):
                lit = any(((x - bx) / rx) ** 2 + ((y - by) / ry) ** 2 < 1 for bx, by, rx, ry in patches)
                if kind == "plate":
                    row, shift = (y - gy0) % 4, ((y - gy0) // 4 % 2) * 3
                    lug = row == 0 and (x + shift) % 6 == 0
                    c = ("plate_hi" if lit else "plate") if lug else ("gr_mid" if row == 1 and (x + shift) % 6 == 0 else "gr")
                else:
                    on_rod = (x - px0) % rod == 0 and x != missing
                    if k == 0:
                        c = "gr_hi" if lit else "gr"
                    elif k == 1:
                        c = "gr" if on_rod else "gr_mid"
                    else:
                        c = "gr_mid" if on_rod else ("gr_hole" if bright < -0.2 else "gr_dk")
                    if kind == "old" and c in ("gr_hi", "gr") and any((x - bx) ** 2 + ((y - by) * 1.6) ** 2 <= r * r for bx, by, r in blobs):
                        c = "dk_rust" if c == "gr" else "rust"
                L.px(x, y, c)
        # frame: dark seam on the left, lit lip on the right edge of the previous panel, corner rivets
        L.vline(px0, gy0, gy1, "gr_dk")
        L.vline(pxe, gy0, gy1, "gr_mid")
        for ry in (gy0 + 1, gy1 - 1):
            L.px(px0 + 2, ry, "gr_hi")
            L.px(pxe - 2, ry, "gr_hi")
        px0 += pw
    assert px0 == x1 + 1
    # the first rows sit in the shadow of the trench lip
    for y in range(gy0, gy0 + 3):
        for x in range(x0, x1 + 1):
            n = L.name_at(x, y)
            L.px(x, y, {"gr_hi": "gr", "gr": "gr_mid", "gr_mid": "gr_dk", "plate": "gr", "plate_hi": "plate", "dk_rust": "br_dk"}.get(n, n))
    # boot polish: short runs of bright bar top where the lane is walked most (in front of markers and doors)
    for cx, spread, runs in [(ANTENNA_X[0], 40, 5), (ANTENNA_X[1], 44, 6), (ANTENNA_X[2], 40, 5), (60, 30, 4), (585, 24, 4)]:
        for _ in range(runs):
            y = gy0 + 3 * rng.randint(3, 8)
            x = cx + rng.randint(-spread, spread)
            for xx in range(x, x + rng.randint(3, 8)):
                if L.name_at(xx, y) == "gr":
                    L.px(xx, y, "gr_hi")
    for gx, gy in GLINTS:
        gy = gy0 + 3 * ((gy - gy0) // 3)
        L.px(gx, gy, "gr_glint")
        L.px(gx - 1, gy, "gr_hi")
        L.px(gx + 1, gy, "gr_hi")
    for x, y in [(36, gy1), (34, gy1 - 1), (603, gy0 + 1), (232, gy0), (420, gy1)]:
        L.px(x, y, "moss")
        L.px(x + 1, y, "lf")
    # brass nosing, top and bottom; worn back to steel where boots cross it
    L.hline(x0, x1, WALK_Y0, "gr_hi")
    L.hline(x0, x1, WALK_Y0 + 1, "br_hi")
    L.hline(x0, x1, WALK_Y0 + 2, "br_dk")
    L.hline(x0, x1, WALK_Y1 - 2, "gr_dk")
    L.hline(x0, x1, WALK_Y1 - 1, "br")
    L.hline(x0, x1, WALK_Y1, "br_dk")
    for x in range(x0 + 6, x1, 24):
        L.px(x, WALK_Y1 - 1, "br_dk")
    for cx, half in [(ANTENNA_X[0], 9), (ANTENNA_X[1], 12), (ANTENNA_X[2], 9), (44, 12), (592, 10)]:
        for x in range(cx - half, cx + half + 1):
            if (x * 7) % 5 != 0:
                L.px(x, WALK_Y0 + 1, "edge" if (x % 3) else "br")
    # covered cable trench running into the maintenance door (signals go to room 2); unequal covers, one lifted
    L.hline(TRENCH_X0, 601, TRENCH_Y0, "dk_seam")
    L.hline(TRENCH_X0, 601, TRENCH_Y0 + 1, "edge")
    L.rect(TRENCH_X0, TRENCH_Y0 + 2, 601, TRENCH_Y1 - 1, "steel")
    L.hline(TRENCH_X0, 601, TRENCH_Y1 - 1, "slate")
    L.hline(TRENCH_X0, 601, TRENCH_Y1, "deep")
    L.vline(TRENCH_X0, TRENCH_Y0, TRENCH_Y1, "deep")
    x = TRENCH_X0
    for length in [18, 24, 20, 30, 22, 16, 26, 22, 28, 18, 24, 20, 30, 22, 26, 20, 24, 30, 18, 26, 22]:
        x += length
        if x >= 601:
            break
        L.vline(x, TRENCH_Y0 + 1, TRENCH_Y1 - 1, "deep")
        L.px(x + 1, TRENCH_Y0 + 2, "edge")
        L.hline(x - length // 2 - 2, x - length // 2 + 1, TRENCH_Y0 + 3, "slate")
        L.px(x - length // 2 - 2, TRENCH_Y0 + 3, "ink")
    # lifted cover: cables in the open trench (teal signal line, brass power line)
    L.rect(250, TRENCH_Y0 + 1, 263, TRENCH_Y1 - 1, "ink")
    L.hline(250, 263, TRENCH_Y0 + 3, "teal_dk")
    L.hline(251, 262, TRENCH_Y0 + 4, "teal")
    L.hline(250, 263, TRENCH_Y0 + 5, "br_dk")
    L.px(256, TRENCH_Y0 + 5, "br")
    L.rect(264, TRENCH_Y0 - 1, 279, TRENCH_Y0 + 1, "steel")
    L.hline(264, 279, TRENCH_Y0 - 1, "edge")
    L.hline(264, 279, TRENCH_Y0 + 2, "deep")
    return L


# ----------------------------------------------------------------------------- 6 deck detail
def conduit_v(L, x, y0, y1):
    L.vline(x - 1, y0, y1, "edge")
    L.vline(x, y0, y1, "steel")
    L.vline(x + 1, y0, y1, "deep")
    for y in range(y0 + 6, y1, 11):
        L.rect(x - 2, y, x + 2, y + 1, "br")
        L.hline(x - 2, x + 2, y, "br_hi")


def conduit_h(L, x0, x1, y):
    L.hline(x0, x1, y - 1, "edge")
    L.hline(x0, x1, y, "steel")
    L.hline(x0, x1, y + 1, "deep")


def anchor_plate(L, x0, y0):
    L.box(x0, y0, x0 + 12, y0 + 7, "steel", "deep")
    L.hline(x0 + 1, x0 + 11, y0 + 1, "edge")
    for bx in (x0 + 2, x0 + 10):
        L.px(bx, y0 + 5, "ink")
        L.px(bx, y0 + 4, "edge")
    L.rect(x0 + 5, y0 + 1, x0 + 7, y0 + 3, "br")
    L.px(x0 + 6, y0 + 2, "ink")


def detail_layer(rng):
    L = Layer()
    # floor conduits: wall junction box -> antenna plinth
    jx = [x + 8 for x in JUNCTION_X]
    conduit_v(L, jx[0], 157, 199)
    conduit_h(L, 190, jx[0], 199)
    conduit_v(L, jx[1], 157, 199)
    conduit_h(L, 349, jx[1], 199)
    conduit_v(L, jx[2], 157, 199)
    conduit_h(L, jx[2], 458, 199)
    # risers from each plinth down into the trench
    for x in (186, 343, 489):
        conduit_v(L, x, 211, TRENCH_Y0)
    # machine tread prints along the back strip toward antenna A (patrol route)
    for t in range(0, 80, 4):
        x = 40 + t
        y = 191 + int(4 * math.sin(t / 26.0))
        L.hline(x, x + 1, y, "dk_seam")
        L.hline(x, x + 1, y + 6, "dk_seam")
        if t % 8 == 0:
            L.px(x, y + 1, "dk_sh")
            L.px(x, y + 7, "dk_sh")
    # raised cable trough behind the dish: B's feeders run along the wall base to its junction box
    L.rect(290, 160, 361, 167, "st")
    L.hline(290, 361, 160, "st_hi")
    L.vline(290, 160, 185, "st_hi")
    L.rect(290, 168, 361, 185, "st_mid")
    L.hline(290, 361, 168, "st_dk")
    L.hline(290, 361, 185, "st_deep")
    L.vline(361, 160, 185, "st_dk")
    for x in range(292, 360, 12):
        L.rect(x, 161, x + 10, 166, "steel")
        L.hline(x, x + 10, 161, "edge")
        L.vline(x + 10, 161, 166, "deep")
        L.px(x + 5, 163, "ink")
    for x in range(296, 360, 16):
        L.vline(x, 170, 183, "st_dk")
    L.px(300, 184, "moss")
    L.px(352, 184, "moss_hi")
    L.hline(291, 362, 186, "dk_seam")
    # stone planter in the north-west corner, overgrown
    L.rect(44, 166, 98, 172, "st")
    L.hline(44, 98, 166, "st_hi")
    L.rect(44, 173, 98, 184, "st_mid")
    L.hline(44, 98, 173, "st_dk")
    L.hline(44, 98, 184, "st_deep")
    L.vline(98, 166, 184, "st_dk")
    for x in range(52, 98, 12):
        L.vline(x, 174, 183, "st_dk")
    L.hline(45, 99, 185, "dk_seam")
    clump_mass(L, rng, 71, 160, 26, 9, 34, flowers=3)
    tendril(L, rng, 50, 168, 10)
    tendril(L, rng, 90, 168, 8)
    # faded safety-zone paint around each antenna pad (dashed, worn through in places)
    for x0, x1 in [(ANTENNA_X[0] - 42, ANTENNA_X[0] + 31), (ANTENNA_X[1] - 33, ANTENNA_X[1] + 41), (ANTENNA_X[2] - 48, ANTENNA_X[2] + 64)]:
        for x in range(x0, x1 + 1):
            if (x // 3) % 2 == 0 and rng.random() < 0.6:
                L.px(x, 213, "paper_dk")
                if (x // 6) % 3 == 0:
                    L.px(x, 213, "warn_dk")
        for y in range(184, 214):
            if (y // 3) % 2 == 0 and rng.random() < 0.6:
                L.px(x0, y, "paper_dk")
                L.px(x1, y, "paper_dk")
    # guy-wire anchors for antenna C
    anchor_plate(L, 429, 200)
    anchor_plate(L, 525, 200)
    anchor_plate(L, 494, 166)
    # cable drum against the wall (axis vertical)
    L.ellipse(224, 159, 257, 168, "wood_hi")
    L.ellipse(224, 175, 257, 184, "wood")
    L.rect(227, 164, 254, 179, "ink")
    for y in range(165, 179, 2):
        L.hline(228, 253, y, "deep")
        L.px(228 + (y * 5) % 24, y, "steel")
    L.ellipse(224, 159, 257, 168, "wood_hi")
    L.ellipse(229, 161, 252, 166, "wood")
    L.ellipse(236, 162, 245, 165, "ink")
    L.hline(226, 255, 168, "wood")
    L.hline(225, 256, 184, "st_deep")
    # spare-parts crate with a coil on the lid
    L.rect(380, 160, 412, 166, "wood_hi")
    L.hline(380, 412, 160, "paper_dk")
    L.rect(380, 167, 412, 179, "wood")
    for y in (171, 175):
        L.hline(381, 411, y, "br_dk")
    L.vline(380, 160, 179, "br_dk")
    L.vline(412, 160, 179, "br_dk")
    L.rect(380, 167, 382, 169, "br")
    L.rect(410, 167, 412, 169, "br")
    L.ellipse(388, 158, 402, 164, "ink")
    L.ellipse(391, 159, 399, 163, "wood_hi")
    L.hline(390, 400, 158, "deep")
    L.hline(380, 412, 180, "st_deep")
    # rust drips under the anchor plates and the riser clamps
    for x, y, n in [(433, 208, 5), (529, 208, 5), (498, 174, 6), (189, 214, 4), (346, 214, 4), (492, 214, 4)]:
        for i in range(n):
            if (i + x) % 3 != 2:
                L.px(x + (i // 3), y + i, "dk_rust")
        L.px(x + 1, y, "dk_rust")
    # moss only where it would grow: clusters along the damp wall foot, in slab joints near the plinths,
    # in the stair and door corners and along the lane's shaded edges; none in the traffic zones
    def moss_cluster(cx, cy, size):
        for _ in range(size * 3):
            x, y = cx + rng.randint(-size, size), cy + rng.randint(-size // 2, size // 2)
            if any(((x - tx) / rx) ** 2 + ((y - ty) / ry) ** 2 < 0.7 for tx, ty, rx, ry in TRAFFIC):
                continue
            L.px(x, y, rng.choice(("moss_dk", "moss", "moss")))
        L.px(cx - 1, cy - 1, "moss_hi")
        L.px(cx, cy - 1, "moss")
        if size > 2:
            L.px(cx + 1, cy - 2, "moss_hi")
    x = 40
    while x < 598:
        if not any(p - 4 <= x <= p + 20 for p in PILASTERS):
            moss_cluster(x, 158 + rng.randint(0, 3), rng.randint(2, 4))
        x += rng.randint(14, 34)
    for p in PILASTERS:
        moss_cluster(p - 2, 158, 3)
        moss_cluster(p + 18, 159, 2)
    for cx, cy, s in [(118, 207, 3), (194, 206, 2), (288, 206, 3), (352, 208, 2), (458, 208, 2), (500, 206, 3),
                      (44, 236, 3), (596, 236, 3), (104, 196, 2), (424, 192, 2), (560, 196, 3), (272, 170, 2)]:
        moss_cluster(cx, cy, s)
    for x in range(42, 600, 4):
        if rng.random() < 0.28 and not any(abs(x - tx) < rx * 0.6 for tx, _ty, rx, _ry in TRAFFIC[:3]):
            L.px(x, WALK_Y1 + 1, rng.choice(("moss", "lf", "moss_dk")))
    return L


# ----------------------------------------------------------------------------- 8 doors and side walls
def doors_layer(rng):
    L = Layer()
    # west pier (top coping strip and lit inner face) with the stair down to the surface
    for y0, y1 in [(94, 235), (290, 317)]:
        # v03: the pier face is in the same back-light shade as the parapet (one step darker than v02)
        L.rect(0, y0, 29, y1, "st_mid")
        for y in range(y0 + 7, y1, 11):
            L.hline(0, 29, y, "st_dk")
            L.px(rng.randint(2, 27), y + 1, "st")
        L.vline(0, y0, y1, "st_dk")
        L.vline(28, y0, y1, "st")
        L.rect(30, y0 + 4, 37, y1, "st_mid")
        L.vline(37, y0 + 4, y1, "st_dk")
        for y in range(y0 + 10, y1, 9):
            L.hline(30, 37, y, "st_dk")
    L.hline(0, 29, 94, "st_hi")
    clump_mass(L, rng, 14, 120, 13, 18, 22, flowers=2)
    clump_mass(L, rng, 22, 196, 10, 12, 12)
    # stair treads descending west, darker with depth
    tones = [("st", "st_dk"), ("st_mid", "st_dk"), ("st_mid", "st_deep"), ("st_dk", "st_deep"), ("st_deep", "mortar"), ("mortar", "mortar")]
    x = 37
    for tread, riser in tones:
        L.rect(x - 5, 236, x, 289, tread)
        L.vline(x - 5, 236, 289, riser)
        L.hline(x - 5, x, 236, "st_deep")
        x -= 6
    L.rect(0, 236, x, 289, "mortar")
    L.hline(0, 37, 237, "st_deep")
    L.hline(0, 37, 288, "st_deep")
    # stair handrail
    L.hline(0, 37, 283, "br_hi")
    L.hline(0, 37, 284, "br_dk")
    for xx in (4, 20, 35):
        L.vline(xx, 284, 289, "br_dk")
    # exit plate on the pier
    L.box(6, 170, 24, 182, "teal_dk")
    L.hline(7, 23, 171, "teal")
    L.vline(15, 173, 179, "paper")
    L.line(12, 176, 15, 179, "paper")
    L.line(18, 176, 15, 179, "paper")
    # east: maintenance block wall with the open door to room 2
    for y0, y1 in [(86, 231), (290, 317)]:
        L.rect(610, y0, 639, y1, "st_dk")
        L.rect(602, y0 + 4, 609, y1, "st_mid")
        L.vline(602, y0 + 4, y1, "st")
        for y in range(y0 + 8, y1, 10):
            L.hline(610, 639, y, "st_deep")
            L.hline(602, 609, y, "st_dk")
            L.px(rng.randint(612, 637), y + 2, "st_mid")
        L.vline(610, y0, y1, "st_mid")
    L.hline(610, 639, 86, "st_hi")
    L.rect(610, 87, 639, 89, "st")
    # door: lintel, jambs, dark interior with a teal console glimmer, half-open steel leaf
    L.rect(598, 226, 639, 235, "st")
    L.hline(598, 639, 226, "st_hi")
    L.hline(598, 639, 235, "st_deep")
    L.rect(598, 236, 603, 289, "st")
    L.vline(598, 236, 289, "st_hi")
    L.vline(603, 236, 289, "st_dk")
    L.rect(604, 236, 639, 289, "ink")
    L.rect(604, 236, 639, 240, "deep")
    L.rect(624, 250, 636, 266, "deep")
    for i in range(3):
        L.rect(626 + i * 4, 254, 627 + i * 4, 256, "teal")
    L.hline(626, 635, 260, "teal_dk")
    L.rect(604, 240, 615, 289, "slate")
    L.vline(604, 240, 289, "edge")
    for y in range(246, 288, 8):
        L.hline(605, 615, y, "deep")
    L.vline(615, 240, 289, "ink")
    # threshold plate
    L.rect(596, 282, 639, 289, "steel")
    L.hline(596, 639, 282, "edge")
    for xx in range(598, 639, 6):
        L.px(xx, 285, "deep")
    # door lamp
    L.rect(593, 214, 600, 219, "slate")
    L.rect(594, 220, 599, 223, "teal")
    L.hline(594, 599, 220, "glow")
    L.px(593, 221, "ink")
    L.px(600, 221, "ink")
    clump_mass(L, rng, 626, 98, 14, 8, 14, flowers=1)
    tendril(L, rng, 616, 104, 26)
    tendril(L, rng, 632, 104, 40)
    return L


# ----------------------------------------------------------------------------- 9 front parapet
def front_layer(rng):
    L = Layer()
    L.hline(0, W - 1, 291, "dk_seam")  # deck edge under the railing
    # coping seen from above and behind: lit top, short front face, dark drip edge; the outer wall is in shade
    L.rect(0, 292, W - 1, 293, "st_hi")
    L.rect(0, 294, W - 1, 296, "st")
    L.hline(0, W - 1, 297, "st_deep")
    L.hline(0, W - 1, 298, "mortar")
    x = -rng.randint(0, 16)
    while x < W:
        w = rng.randint(22, 40)
        L.vline(x, 293, 296, "st_dk")
        L.px(x + 1, 294, "st_hi")
        if rng.random() < 0.4:
            L.rect(x + 1, 296, x + rng.randint(2, 4), 296, "st_dk")
        x += w
    for _ in range(30):
        cx = rng.randint(0, W - 2)
        L.px(cx, 292 + rng.randint(0, 1), "lichen" if rng.random() < 0.6 else "st")
    shade_wall(L, rng, 0, W - 1, 299, 317, course=7, tones=("st_mid", "st_dk", "st_dk"), under_coping=3)
    streaks(L, rng, sorted(rng.sample(range(2, W - 2), 40)), 299, 18)
    L.rect(0, 318, W - 1, H - 1, "st_deep")  # under the footer bar; keeps the plate opaque
    # railing set on the coping (the heroine always stands behind it)
    L.hline(38, 601, 286, "br_hi")
    L.hline(38, 601, 287, "br_dk")
    for x in range(44, 600, 40):
        L.rect(x, 287, x + 1, 291, "br_dk")
        L.px(x, 287, "br")
        L.px(x, 292, "st_deep")
    for x in range(40, 600, 13):
        if rng.random() < 0.45:
            L.px(x, 291, "moss")
            L.px(x + 1, 291, "lf")
    return L


# ----------------------------------------------------------------------------- 10-12 antennas
def plinth(L, x0, x1, top):
    L.rect(x0, top, x1, top + 7, "st")
    L.hline(x0, x1, top, "st_hi")
    L.vline(x0, top, BASE_Y - 1, "st_hi")
    L.rect(x0, top + 8, x1, BASE_Y - 1, "st_mid")
    L.hline(x0, x1, top + 8, "st_dk")
    L.hline(x0, x1, BASE_Y - 1, "st_deep")
    L.vline(x1, top, BASE_Y - 1, "st_dk")
    L.vline(x0, top + 8, BASE_Y - 2, "st")
    for x in range(x0 + 6, x1 - 2, 9):
        L.px(x, top + 11, "st_dk")
    L.px(x0 + 3, top + 13, "moss")
    L.px(x1 - 3, top + 14, "moss")
    L.px(x1 - 4, top + 14, "moss_hi")


def bolt(L, x, y):
    L.px(x, y, "br_hi")
    L.px(x + 1, y, "br_dk")
    L.px(x, y + 1, "br_dk")


def antenna_a():
    """Strongest but jumpy: tall lattice mast with two Yagi arrays, amber beacon, jitter readout."""
    L = Layer()
    cx = ANTENNA_X[0]
    plinth(L, cx - 22, cx + 26, 192)
    for x in (cx - 18, cx + 20):
        bolt(L, x, 195)
    # lattice legs (two visible faces), tapering 28 px -> 10 px; v03 top lowered 12 px so the beacon clears the HUD
    top, bottom = 82, 194
    def leg_x(side, y):
        t = (bottom - y) / (bottom - top)
        return cx + side * (14 - 9 * t)
    for y in range(top, bottom + 1):
        lx, rx = int(round(leg_x(-1, y))), int(round(leg_x(1, y)))
        L.px(lx - 1, y, "ink")
        L.px(lx, y, "edge")
        L.px(lx + 1, y, "steel")
        L.px(rx - 1, y, "steel")
        L.px(rx, y, "slate")
        L.px(rx + 1, y, "ink")
    rungs = list(range(bottom - 2, top, -14))
    for i, y in enumerate(rungs):
        lx, rx = int(round(leg_x(-1, y))), int(round(leg_x(1, y)))
        L.hline(lx, rx, y, "ink")
        L.hline(lx + 1, rx - 1, y - 1, "steel")
        if i + 1 < len(rungs):
            y2 = rungs[i + 1]
            lx2, rx2 = int(round(leg_x(-1, y2))), int(round(leg_x(1, y2)))
            L.line(lx + 1, y - 1, rx2 - 1, y2 + 1, "slate")
            L.line(rx - 1, y - 1, lx2 + 1, y2 + 1, "deep")
    # feeder cable down the right leg, clamped
    for y in range(88, 192):
        x = int(round(leg_x(1, y))) + 2
        L.px(x, y, "ink" if y % 9 else "br")
    # service platform near the top
    L.rect(cx - 13, 106, cx + 13, 108, "steel")
    L.hline(cx - 13, cx + 13, 106, "edge")
    L.hline(cx - 13, cx + 13, 109, "ink")
    L.hline(cx - 13, cx + 13, 100, "slate")
    for x in (cx - 13, cx - 4, cx + 5, cx + 13):
        L.vline(x, 100, 106, "slate")
    # upper Yagi pointing east (toward the city), lower Yagi pointing west
    L.hline(cx - 6, cx + 46, 88, "ink")
    L.hline(cx - 6, cx + 46, 87, "edge")
    for i, x in enumerate(range(cx + 2, cx + 47, 7)):
        half = 7 - i
        L.vline(x, 88 - half, 88 + half, "ink")
        L.px(x, 88 - half, "edge")
    L.rect(cx - 8, 86, cx - 5, 91, "slate")
    L.hline(cx - 42, cx + 2, 120, "ink")
    L.hline(cx - 42, cx + 2, 119, "edge")
    for i, x in enumerate(range(cx - 6, cx - 43, -7)):
        half = 5 - i // 2
        L.vline(x, 120 - half, 120 + half, "ink")
        L.px(x, 120 - half, "edge")
    # amber obstruction beacon on top
    L.vline(cx, 76, 81, "ink")
    L.rect(cx - 2, 73, cx + 1, 75, "warn")
    L.px(cx - 2, 73, "br_hi")
    # interference sparks off the upper array tip
    for x, y in [(cx + 50, 84), (cx + 52, 86), (cx + 49, 92), (cx + 53, 91), (cx + 55, 88)]:
        L.px(x, y, "warn")
    L.px(cx + 51, 89, "br_hi")
    # sensor-band warning placard on the tower (a patrol machine glyph)
    L.poly([(cx, 140), (cx - 6, 151), (cx + 6, 151)], "ink")
    L.poly([(cx, 142), (cx - 4, 150), (cx + 4, 150)], "warn")
    L.rect(cx - 1, 146, cx + 1, 147, "ink")
    L.px(cx, 145, "ink")
    # jitter readout cabinet bolted to the plinth's west side
    x0, y0 = cx - 37, 166
    L.box(x0, y0, x0 + 16, BASE_Y - 1, "slate")
    L.hline(x0 + 1, x0 + 15, y0 + 1, "edge")
    L.vline(x0 + 1, y0 + 2, BASE_Y - 2, "steel")
    L.rect(x0 + 3, y0 + 4, x0 + 13, y0 + 16, "teal_dk")
    L.hline(x0 + 4, x0 + 12, y0 + 12, "glow")
    for x, yt in [(x0 + 5, y0 + 6), (x0 + 8, y0 + 8), (x0 + 11, y0 + 5)]:
        L.vline(x, yt, y0 + 12, "warn")
        L.px(x + 1, y0 + 11, "warn_dk")
    for i in range(4):
        L.rect(x0 + 3 + i * 3, y0 + 26 - i * 2, x0 + 4 + i * 3, y0 + 27, "glow")
    L.hline(x0 + 3, x0 + 13, y0 + 30, "deep")
    L.hline(x0 + 3, x0 + 13, y0 + 33, "deep")
    L.rect(x0 + 13, y0 + 20, x0 + 14, y0 + 22, "br_hi")
    L.hline(x0 + 17, cx - 16, y0 + 18, "ink")
    return L


def antenna_b():
    """Weaker but steady: a big tilted dish on a pedestal, smooth sine, intact cable to a ground stake."""
    L = Layer()
    cx = ANTENNA_X[1]
    plinth(L, cx - 28, cx + 28, 192)
    for x in (cx - 24, cx + 22):
        bolt(L, x, 195)
    # turntable ring
    L.ellipse(cx - 16, 184, cx + 16, 195, "ink")
    L.ellipse(cx - 15, 185, cx + 15, 193, "steel")
    L.ellipse(cx - 12, 186, cx + 12, 191, "slate")
    L.hline(cx - 13, cx - 2, 185, "edge")
    # pedestal column
    L.rect(cx - 6, 138, cx + 6, 188, "steel")
    L.vline(cx - 6, 138, 188, "ink")
    L.vline(cx + 6, 138, 188, "ink")
    L.vline(cx - 5, 138, 188, "edge")
    L.rect(cx + 3, 138, cx + 5, 188, "slate")
    for y in (150, 172):
        L.rect(cx - 7, y, cx + 7, y + 2, "br")
        L.hline(cx - 7, cx + 7, y, "br_hi")
        L.hline(cx - 7, cx + 7, y + 2, "br_dk")
    # elevation yoke
    L.rect(cx - 10, 128, cx + 10, 138, "slate")
    L.hline(cx - 10, cx + 10, 128, "edge")
    L.rect(cx - 10, 128, cx - 10, 138, "ink")
    L.rect(cx + 10, 128, cx + 10, 138, "ink")
    L.rect(cx - 2, 130, cx + 2, 134, "deep")
    # dish: a foreshortened bowl tipped back toward the sky (minor/major 0.53, v02 was a near-round 0.68 face).
    # Concave cues at 1x: the sun-side (upper-left) rim throws a hard crescent of shadow into the bowl, the far
    # lower-right inner wall is the brightest part, curvature rings centre low-right, the back shell shows as a
    # dark lip below the rim, a rear truss runs to the yoke, and the feed horn's shadow lands inside the bowl.
    dcx, dcy, a, b, rot = cx - 4, 104, 36, 19, math.radians(-16)

    def ell(scale, ox=0.0, oy=0.0, n=96):
        pts = []
        for k in range(n):
            t = k / n * math.tau
            x, y = a * scale * math.cos(t), b * scale * math.sin(t)
            pts.append((dcx + ox + x * math.cos(rot) - y * math.sin(rot), dcy + oy + x * math.sin(rot) + y * math.cos(rot)))
        return pts

    def mask(pts):
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).polygon([(int(round(x)), int(round(y))) for x, y in pts], fill=255)
        return np.array(m) > 0

    # rear truss: yoke -> back ring (drawn first; the shell and bowl cover its upper part)
    ring = ell(0.5, 6, 11)
    for k, (yx, yy) in zip((10, 34, 58, 82), ((cx - 9, 129), (cx - 3, 128), (cx + 4, 128), (cx + 9, 129))):
        rx_, ry_ = ring[k]
        L.line(yx, yy, rx_, ry_, "ink")
        L.line(yx + 1, yy, rx_ + 1, ry_, "slate")
    L.hline(cx - 12, cx + 12, 127, "ink")
    L.hline(cx - 11, cx + 11, 126, "steel")
    # back shell: dark convex lip under the rim, with a stiffening ring line
    L.poly(ell(1.02, 3, 6), "ink")
    L.poly(ell(0.98, 3, 5), "deep")
    shell_ring = ell(0.9, 3, 6)
    for k in range(52, 92):
        p0, p1 = shell_ring[k % 96], shell_ring[(k + 1) % 96]
        L.line(p0[0], p0[1], p1[0], p1[1], "slate")
    # rim (2 px lip) and bowl
    L.poly(ell(1.0), "ink")
    L.poly(ell(0.96), "steel")
    bowl = mask(ell(0.9))
    L.a[bowl] = RGBA["steel"]
    lit_far = mask(ell(0.62, 8, 4)) & bowl
    L.a[lit_far] = RGBA["edge"]
    hot = mask(ell(0.16, 17, 7)) & bowl
    L.a[hot] = RGBA["frost_mid"]
    shadow = bowl & ~mask(ell(0.9, 6, 5))
    L.a[shadow] = RGBA["slate"]
    deep_shadow = bowl & ~mask(ell(0.9, 3, 2.5))
    L.a[deep_shadow] = RGBA["deep"]
    # curvature rings (panel seams) only where the bowl is lit, centred toward the low-right vertex
    for scale, ox, oy in ((0.68, 2.5, 1.5), (0.4, 5, 3)):
        for x, y in ell(scale, ox, oy, 160):
            ix, iy = int(round(x)), int(round(y))
            if L.name_at(ix, iy) in ("steel", "edge"):
                L.px(ix, iy, "slate" if L.name_at(ix, iy) == "steel" else "steel")
    vx, vy = int(round(dcx + 6)), int(round(dcy + 3))
    L.rect(vx - 1, vy - 1, vx + 1, vy, "slate")
    L.px(vx, vy - 1, "ink")
    # rim light: the upper-left lip catches the sun, the lower-right lip turns away
    outer = ell(0.98)
    for k in range(96):
        p0, p1 = outer[k], outer[(k + 1) % 96]
        ang = k / 96 * 360
        c = "frost" if 150 <= ang <= 300 else ("edge" if 300 < ang <= 340 or 120 <= ang < 150 else "slate")
        L.line(p0[0], p0[1], p1[0], p1[1], c)
    # feed horn on three struts, held in front of the bowl toward the sky; its shadow falls inside the bowl
    fx, fy = int(round(dcx - 1)), int(round(dcy - 4))
    sx_, sy_ = fx + 9, fy + 7
    L.rect(sx_ - 2, sy_ - 1, sx_ + 2, sy_ + 1, "deep")
    L.px(sx_ - 3, sy_, "deep")
    inner = ell(0.94)
    for k in (8, 40, 72):
        rx_, ry_ = inner[k]
        L.line(rx_ + 1, ry_ + 1, fx + 1, fy + 1, "ink")
        L.line(rx_, ry_, fx, fy, "edge")
    L.box(fx - 3, fy - 4, fx + 3, fy + 2, "slate")
    L.hline(fx - 2, fx + 2, fy - 3, "edge")
    L.rect(fx - 2, fy - 1, fx + 1, fy + 1, "br")
    L.px(fx - 2, fy - 1, "br_hi")
    # status box on the pedestal: smooth sine, two of four bars
    x0, y0 = cx + 8, 150
    L.box(x0, y0, x0 + 20, y0 + 20, "slate")
    L.hline(x0 + 1, x0 + 19, y0 + 1, "edge")
    L.rect(x0 + 3, y0 + 3, x0 + 17, y0 + 10, "teal_dk")
    for i in range(15):
        L.px(x0 + 3 + i, y0 + 6 + int(round(2 * math.sin(i / 2.4))), "glow")
    for i in range(4):
        L.rect(x0 + 4 + i * 4, y0 + 17 - i, x0 + 5 + i * 4, y0 + 17, "glow" if i < 2 else "deep")
    # intact cable: box -> pedestal -> plinth side -> brass ground stake, with a service tag
    L.vline(x0 + 10, y0 + 21, 191, "ink")
    L.vline(x0 + 11, y0 + 21, 191, "deep")
    L.px(x0 + 10, 180, "br_hi")
    L.hline(cx + 29, cx + 33, 203, "ink")
    L.hline(cx + 29, cx + 33, 204, "deep")
    sx = cx + 34
    L.rect(sx, 190, sx + 3, BASE_Y - 1, "br_dk")
    L.vline(sx, 190, BASE_Y - 1, "br")
    L.rect(sx - 1, 188, sx + 4, 190, "br")
    L.hline(sx - 1, sx + 4, 188, "br_hi")
    L.rect(sx - 1, 202, sx + 4, 204, "br_hi")
    L.line(x0 + 11, 176, x0 + 15, 179, "ink")
    L.box(x0 + 14, 179, x0 + 19, 185, "paper", "ink")
    L.hline(x0 + 15, x0 + 18, 181, "teal_dk")
    L.px(x0 + 16, 183, "teal_dk")
    return L


def antenna_c():
    """Wind dropouts: weathered guyed mast, bright new radome, wind ribbon, frosted battery, old head."""
    L = Layer()
    cx = ANTENNA_X[2]
    plinth(L, cx - 16, cx + 16, 194)
    bolt(L, cx - 12, 197)
    bolt(L, cx + 11, 197)
    # guy wires (drawn first so the mast sits over their collar)
    collar = (cx, 116)
    for ax, ay in [(435, 202), (531, 202), (500, 168)]:
        L.line(collar[0], collar[1], ax, ay, "ink")
        steps = int(max(abs(ax - collar[0]), abs(ay - collar[1])))
        for s in range(4, steps, 5):
            L.px(collar[0] + (ax - collar[0]) * s / steps + 1, collar[1] + (ay - collar[1]) * s / steps, "edge")
        tx, ty = ax + (collar[0] - ax) * 0.12, ay + (collar[1] - ay) * 0.12
        L.rect(tx - 1, ty - 3, tx + 1, ty + 1, "br")
        L.px(tx - 1, ty - 3, "br_hi")
    # weathered mast: 6 px, faded orange/white obstruction bands, rust flecks
    rng = random.Random(77)
    for y in range(90, 196):
        band = ((y - 90) // 14) % 2 == 0
        lit, mid, dark = ("warn", "warn_dk", "rust") if band else ("paper", "paper_dk", "st_dk")
        L.px(cx - 3, y, "ink")
        L.px(cx - 2, y, lit)
        L.px(cx - 1, y, mid)
        L.px(cx, y, mid)
        L.px(cx + 1, y, dark)
        L.px(cx + 2, y, "ink")
        if rng.random() < 0.22:
            L.px(cx + rng.choice((-1, 0, 1)), y, rng.choice(("rust", "br_dk", "st_mid")))
    for y in (116, 152):
        L.rect(cx - 5, y - 1, cx + 4, y + 2, "br_dk")
        L.hline(cx - 5, cx + 4, y - 1, "br")
        L.px(cx - 5, y, "ink")
        L.px(cx + 4, y, "ink")
    # step bolts up the west side
    for y in range(124, 192, 8):
        L.px(cx - 4, y, "edge")
        L.px(cx - 4, y + 1, "ink")
    # crossarm with two vertical dipole whips
    L.hline(cx - 16, cx + 15, 98, "ink")
    L.hline(cx - 16, cx + 15, 97, "edge")
    for wx in (cx - 14, cx + 13):
        L.vline(wx, 87, 110, "ink")
        L.vline(wx - 1, 88, 109, "edge")
        L.rect(wx - 1, 97, wx + 1, 99, "slate")
    # new radome capsule (clearly brighter than the weathered mast) with its whip; v03 tip at y 68, below the HUD
    L.vline(cx, 68, 72, "ink")
    L.px(cx, 68, "edge")
    L.box(cx - 6, 72, cx + 5, 91, "paper")
    L.vline(cx - 5, 73, 90, "frost")
    L.vline(cx + 4, 73, 90, "paper_dk")
    L.hline(cx - 5, cx + 4, 73, "frost")
    L.rect(cx - 5, 85, cx + 4, 86, "br")
    L.hline(cx - 5, cx + 4, 85, "br_hi")
    L.px(cx - 4, 75, "frost")
    # wind ribbon streaming east from the upper collar
    L.poly([(cx + 3, 104), (cx + 12, 102), (cx + 20, 106), (cx + 26, 103), (cx + 22, 108), (cx + 13, 109), (cx + 3, 108)], "warn")
    L.line(cx + 5, 108, cx + 14, 109, "warn_dk")
    L.line(cx + 16, 107, cx + 22, 108, "warn_dk")
    L.rect(cx + 2, 103, cx + 3, 109, "ink")
    # clamped readout: trace, gap, dashes (dropouts)
    x0, y0 = cx + 4, 130
    L.box(x0, y0, x0 + 18, y0 + 13, "slate")
    L.hline(x0 + 1, x0 + 17, y0 + 1, "edge")
    L.rect(x0 + 2, y0 + 3, x0 + 16, y0 + 10, "teal_dk")
    for i, dy in enumerate((0, -2, 0, -1)):
        L.px(x0 + 3 + i, y0 + 7 + dy, "glow")
    for x in (x0 + 9, x0 + 12, x0 + 15):
        L.px(x, y0 + 8, "teal")
    L.rect(x0 - 1, y0 + 5, x0, y0 + 8, "br_dk")
    # backup battery on the plinth's east side: frost crust, one amber cell of four
    bx0, by0 = cx + 20, 180
    L.rect(bx0, by0, bx0 + 24, by0 + 6, "steel")
    L.hline(bx0, bx0 + 24, by0, "edge")
    L.box(bx0, by0 + 6, bx0 + 24, BASE_Y - 1, "slate")
    L.vline(bx0, by0, BASE_Y - 1, "ink")
    L.vline(bx0 + 24, by0, BASE_Y - 1, "ink")
    for tx in (bx0 + 4, bx0 + 17):
        L.rect(tx, by0 - 3, tx + 3, by0, "br_dk")
        L.hline(tx, tx + 3, by0 - 3, "frost")
    L.hline(bx0 + 1, bx0 + 23, by0 + 1, "frost")
    for x in range(bx0 + 1, bx0 + 24, 3):
        L.px(x, by0 + 2, "frost_mid")
    for x, d in [(bx0 + 3, 3), (bx0 + 9, 2), (bx0 + 15, 4), (bx0 + 21, 2)]:
        L.vline(x, by0 + 7, by0 + 6 + d, "frost_mid")
        L.px(x, by0 + 7, "frost")
    for i in range(4):
        L.rect(bx0 + 4 + i * 5, by0 + 16, bx0 + 6 + i * 5, by0 + 19, "warn" if i == 0 else "deep")
    L.hline(bx0 + 3, bx0 + 21, by0 + 23, "deep")
    L.hline(cx + 3, bx0 - 1, 192, "ink")
    # the swapped-out head lying on the deck by the west anchor, cracked and dull
    hx, hy = cx - 33, 198
    L.box(hx, hy, hx + 12, hy + 7, "st_mid")
    L.hline(hx + 1, hx + 11, hy + 1, "paper_dk")
    L.line(hx + 5, hy + 2, hx + 8, hy + 6, "ink")
    L.rect(hx + 8, hy + 1, hx + 9, hy + 6, "br_dk")
    L.hline(hx + 13, hx + 15, hy + 4, "ink")
    return L


# ----------------------------------------------------------------------------- 7 cast shadows
SHADE = {}


def shade_of(name):
    if name in SHADE:
        return SHADE[name]
    explicit = {"dk_hi": "dk_b", "dk_a": "dk_sh", "dk_b": "dk_sh", "dk_c": "dk_sh2", "dk_sh": "dk_sh2", "dk_sh2": "dk_seam",
                "dk_seam": "st_deep", "gr_hi": "gr", "gr": "gr_dk", "gr_dk": "gr_hole", "gr_hole": "gr_hole",
                "edge": "steel", "steel": "slate", "slate": "deep", "deep": "ink", "ink": "ink", "br_hi": "br", "br": "br_dk",
                "br_dk": "wood", "moss_hi": "moss", "moss": "lf", "lf": "lf_dk", "lf_mid": "lf", "lf_hi": "lf_mid", "lf_dk": "lf_dk",
                "st_hi": "st", "st": "st_mid", "st_mid": "st_dk", "st_dk": "st_deep", "st_deep": "mortar", "mortar": "mortar",
                "wood_hi": "wood", "wood": "br_dk", "paper_dk": "st_dk",
                "lichen": "st_mid", "dk_worn": "dk_b", "dk_wet": "dk_sh2", "dk_rust": "br_dk", "gr_mid": "gr_dk",
                "gr_glint": "gr", "plate_hi": "plate", "plate": "gr", "moss_dk": "lf_dk", "paper": "paper_dk",
                "teal": "teal_dk", "glow": "teal", "warn": "warn_dk", "frost": "frost_mid", "frost_mid": "edge", "rust": "br_dk"}
    SHADE[name] = explicit.get(name, name)
    return SHADE[name]


def shadow_layer(under, antennas, extra_casters, wall_layers=()):
    """Darken deck-level pixels under projected antenna silhouettes (sun high in the north-west, behind the
    parapet). v03 also projects the parapet, its pilasters and the ivy on the coping, so the wall throws a
    jagged band of shade (about 11 px, deeper at the pilasters) across the foot of the deck."""
    L = Layer()
    mask = np.zeros((H, W), bool)
    for lay in wall_layers:
        ys, xs = np.nonzero(lay.a[..., 3] == 255)
        sel = (ys >= 90) & (ys <= 155)
        for x, y in zip(xs[sel], ys[sel]):
            h = 155 - y
            ix, iy = int(round(x + 0.62 * h)), int(round(156 + 0.2 * h))
            for dx in (0, 1):
                if 0 <= ix + dx < W:
                    mask[156:iy + 1, ix + dx] = True
    for lay in antennas:
        ys, xs = np.nonzero(lay.a[..., 3] == 255)
        for x, y in zip(xs, ys):
            h = BASE_Y - 1 - y
            if h < 0:
                continue
            fx, fy = x + 0.62 * h, BASE_Y + 0.2 * h
            ix, iy = int(round(fx)), int(round(fy))
            for dx in (0, 1):
                if 0 <= ix + dx < W and 0 <= iy < H:
                    mask[iy, ix + dx] = True
    for x0, y0, x1, y1 in extra_casters:
        mask[y0:y1 + 1, x0:x1 + 1] = True
    mask[:157] = False
    mask[WALK_Y1 + 1:] = False
    mask[:, :38] = False
    mask[:, 598:] = False
    ys, xs = np.nonzero(mask)
    for x, y in zip(xs, ys):
        if under[y, x, 3] == 255:
            name = NAME_OF[tuple(int(v) for v in under[y, x, :3])]
            L.a[y, x] = RGBA[shade_of(name)]
    return L


# ----------------------------------------------------------------------------- 13 foreground
def foreground_layer(rng):
    """Corner shrubs at the stair and the maintenance door (the heroine's feet tuck behind them there),
    plus low tufts along the parapet coping. Nothing covers the lane, the markers or the antennas."""
    L = Layer()
    clump_mass(L, rng, 8, 292, 20, 25, 56, flowers=3)
    clump_mass(L, rng, 632, 292, 20, 25, 56, flowers=2)
    for x, n in [(160, 8), (300, 6), (470, 7)]:
        clump_mass(L, rng, x, 299, 10, 4, n)
    L.a[:291, 24:616] = 0
    L.a[:268] = 0
    return L


# ----------------------------------------------------------------------------- build
def build_scene():
    rng = random.Random(20261017)
    sky = sky_layer(rng)
    parapet = parapet_layer(rng)
    kit = wall_kit_layer(rng)
    deck = deck_layer(rng)
    walk = walkway_layer(rng)
    detail = detail_layer(rng)
    antennas = [antenna_a(), antenna_b(), antenna_c()]
    under = composite([sky, parapet, kit, deck, walk, detail])
    contact = [(ANTENNA_X[0] - 37, BASE_Y, ANTENNA_X[0] + 28, BASE_Y + 1), (ANTENNA_X[1] - 28, BASE_Y, ANTENNA_X[1] + 38, BASE_Y + 1),
               (ANTENNA_X[2] - 33, BASE_Y, ANTENNA_X[2] + 45, BASE_Y + 1), (224, 185, 258, 186), (380, 181, 413, 182),
               (38, 157, 597, 160), (38, 157, 45, 243), (590, 157, 597, 243)]
    shadows = shadow_layer(under, antennas, contact, (parapet, kit))
    doors = doors_layer(rng)
    front = front_layer(rng)
    fg = foreground_layer(random.Random(3141))
    layers = [sky, parapet, kit, deck, walk, detail, shadows, doors, front] + antennas + [fg]
    return layers


def sprite_box(index):
    x = ANTENNA_X[index]
    return x - SPRITE_W // 2, SPRITE_TOP, x + SPRITE_W // 2, BASE_Y  # x0, y0, x1 (excl), y1 (excl)


def to_img(arr):
    return Image.fromarray(arr, "RGBA")


def png_bytes(img):
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=False)
    return buf.getvalue()


DT = (2026, 10, 17, 22, 44, 46)


def ora_bytes(name, names, imgs, flat):
    w, h = flat.size
    root = ET.Element("image", {"w": str(w), "h": str(h), "name": name, "version": "0.0.3"})
    stack = ET.SubElement(root, "stack")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", DT), "image/openraster", compress_type=zipfile.ZIP_STORED)
        z.writestr(zipfile.ZipInfo("mergedimage.png", DT), png_bytes(flat), compress_type=zipfile.ZIP_DEFLATED)
        for i, (ln, img) in reversed(list(enumerate(zip(names, imgs)))):  # ORA lists the top layer first
            src = f"data/layer{i:02d}.png"
            z.writestr(zipfile.ZipInfo(src, DT), png_bytes(img), compress_type=zipfile.ZIP_DEFLATED)
            ET.SubElement(stack, "layer", {"name": ln, "src": src, "x": "0", "y": "0", "opacity": "1.0",
                                           "visibility": "visible", "composite-op": "svg:src-over"})
        z.writestr(zipfile.ZipInfo("stack.xml", DT), ET.tostring(root, encoding="utf-8", xml_declaration=True),
                   compress_type=zipfile.ZIP_DEFLATED)
    return buf.getvalue()


def pxo_bytes(export_name, names, imgs, flat):
    w, h = flat.size
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": False, "metadata": {}, "name": n,
                   "new_cels_linked": False, "opacity": 1.0, "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": True} for n in names]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0} for _ in names],
                    "duration": 1.0, "metadata": {}}]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": json.dumps(export_name),
                      "frame_current_tag": "0", "include_tag_in_filename": "false", "interpolation": "0",
                      "lines_count": "1", "new_dir_for_each_frame_tag": "false", "number_of_digits": "4",
                      "number_of_frames": "1", "orientation": "0", "repeat_count": "0", "resize": "100",
                      "save_quality": "0.75", "separator_character": "\"_\"",
                      "sheet_layers_as_separate_files": "false", "split_layers": "false"}
    palette = [{"name": "yonkers-antenna-room1-v03", "colors": [{"color": c, "index": i} for i, c in enumerate(HEX.values())]}]
    data = {"author_company": "", "author_contact": "", "author_display_name": "", "author_real_name": "",
            "brushes": [], "color_mode": 5, "current_frame": 0, "current_layer": len(names) - 1,
            "export_profile": export_profile, "fps": 6.0, "frames": frames_json, "guides": [], "layers": layer_json,
            "license": "", "metadata": {"declared_palette": palette}, "next_keyframe_id": 0, "palettes": [],
            "pixelorama_version": PIXELORAMA_VERSION, "project_current_palette_name": "", "pxo_version": 7,
            "reference_images": [], "size_x": w, "size_y": h, "symmetry_points": [w - 1.0, h - 1.0], "tags": [],
            "tile_mode_x_basis_x": w, "tile_mode_x_basis_y": 0, "tile_mode_y_basis_x": 0, "tile_mode_y_basis_y": h,
            "tilesets": [], "user_data": "", "vanishing_points": []}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        def add(name, payload):
            z.writestr(zipfile.ZipInfo(name, DT), payload, zipfile.ZIP_DEFLATED)
        add("data.json", json.dumps(data, separators=(",", ":")))
        add("mimetype", "application/x-pixelorama")
        add("preview.png", png_bytes(flat))
        add("image_data/frames/1/", b"")
        for i, img in enumerate(imgs, start=1):
            add(f"image_data/frames/1/layer_{i}", img.tobytes())
            add(f"image_data/frames/1/indices_layer_{i}", b"\x00")
    return buf.getvalue()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rel(p):
    return str(p.relative_to(ROOT)).replace("\\", "/")


ANTENNA_SLUGS = ("antenna-a-lattice-yagi", "antenna-b-dish", "antenna-c-guyed-whip")
ANTENNA_READS = [
    "天线 A / Antenna A (scifi.outskirts:0): tallest silhouette, open lattice mast with two Yagi arrays and an amber beacon; "
    "jumpy amber spikes over a full four-bar readout, sparks off the array tip, a sensor-band placard with a machine glyph and "
    "patrol tread prints on the deck behind it = strongest but unreliable",
    "天线 B / Antenna B (scifi.outskirts:1): tilted concave parabolic dish (shadowed inner rim, lit far wall, back shell, rear truss) on a turntable pedestal, smooth teal sine with two of four bars, "
    "an unbroken cable from the status box to a brass ground stake with a checked service tag = weaker but steady and intact",
    "天线 C / Antenna C (scifi.outskirts:2): thin weathered (rusted) guyed mast under a bright new radome, amber wind ribbon, "
    "dropout readout, frost-crusted backup battery with one amber cell, the dull cracked old head on the deck = new head did not "
    "fix the wind/cold dropouts",
]


def runtime_names():
    return {
        "plate": RUNTIME_ENV / f"{PREFIX}_corridor-plate_unapproved-v03_{STAMP}.png",
        "foreground": RUNTIME_ENV / f"{PREFIX}_foreground-occluder_unapproved-v03_{STAMP}.png",
        "antennas": [RUNTIME_PROPS / f"{PREFIX}_{slug}_unapproved-v03_{STAMP}.png" for slug in ANTENNA_SLUGS],
    }


def build():
    layers = build_scene()
    arrs = [lay.a for lay in layers]
    for a in arrs:
        assert set(np.unique(a[..., 3]).tolist()) <= {0, 255}, "binary alpha only"
    plate = composite(layers[:9])
    assert (plate[..., 3] == 255).all(), "plate must be opaque"
    for i in range(3):
        x0, y0, x1, y1 = sprite_box(i)
        alpha = layers[9 + i].a[..., 3]
        inside = np.zeros_like(alpha, bool)
        inside[y0:y1, x0:x1] = True
        assert not (alpha[~inside] > 0).any(), f"antenna {i} leaves its sprite box"
        assert not (alpha[:ART_TOP] > 0).any(), f"antenna {i} reaches above y {ART_TOP} (HUD covers y 0-{HUD_BOTTOM - 1})"
    fg = layers[12].a
    flat = composite(layers)
    used = {tuple(int(v) for v in c) for c in flat[..., :3].reshape(-1, 3)} | {tuple(int(v) for v in c) for a in arrs for c in a[a[..., 3] == 255][:, :3]}
    assert used <= set(RGB.values()), "every pixel comes from the declared palette"

    OUT.mkdir(parents=True, exist_ok=True)
    RUNTIME_ENV.mkdir(parents=True, exist_ok=True)
    RUNTIME_PROPS.mkdir(parents=True, exist_ok=True)
    names = runtime_names()
    imgs = [to_img(a) for a in arrs]
    flat_img = to_img(flat)
    stem = f"{PREFIX}_corridor-scene-layers_unapproved-v03_{STAMP}"
    files = {"ora": ora_bytes(stem, SCENE_LAYERS, imgs, flat_img), "pxo": pxo_bytes("yonkers-room1-v03", SCENE_LAYERS, imgs, flat_img),
             "png": png_bytes(flat_img)}
    for ext, data in files.items():
        (OUT / f"{stem}.{ext}").write_bytes(data)
    runtime = {"plate": png_bytes(to_img(plate)), "foreground": png_bytes(to_img(fg))}
    names["plate"].write_bytes(runtime["plate"])
    names["foreground"].write_bytes(runtime["foreground"])
    antenna_items = []
    for i, path in enumerate(names["antennas"]):
        x0, y0, x1, y1 = sprite_box(i)
        crop = png_bytes(to_img(np.ascontiguousarray(layers[9 + i].a[y0:y1, x0:x1])))
        path.write_bytes(crop)
        antenna_items.append({"layer": ANTENNA_LAYERS[i], "clue": f"scifi.outskirts:{i}", "reads_as": ANTENNA_READS[i],
                              "crop_from_layer_xywh": [x0, y0, SPRITE_W, SPRITE_H], "anchor": [ANTENNA_X[i], BASE_Y],
                              "runtime_png": {"file": rel(path), "sha256": sha(crop), "hash_algorithm": "sha256-bytes"}})
    manifest = {
        "project": "Worlds Between (rpg-2-star-ocean-the-second)",
        "scene": "Yonkers outskirts survey annex room 1 (天线走廊 / Antenna Walkway), scifi.outskirts room 1",
        "version": "v03 bounded art pass over v02 (creator rejected the v02 outdoor look: 继续精修室外画面); same layout, props, "
                   "sprite boxes and collision footprints; parapet depth, localized deck wear, grating rhythm, concave dish B, "
                   "A/C tips below the 62 px HUD",
        "status": "UNAPPROVED. Codex and the creator have not inspected it. Scene counters unchanged (3/12); no Game Bible, ledger or Git index change.",
        "hud_clearance": {"hud_rows": [0, HUD_BOTTOM - 1], "first_allowed_antenna_row": ART_TOP,
                          "top_texel_row": {ANTENNA_SLUGS[i]: int(np.nonzero(layers[9 + i].a[..., 3].any(axis=1))[0][0]) for i in range(3)}},
        "authorship": "Native pixel art from hand-placed primitives and seeded pixel texture in the source tool, by Claude (Claude Code, "
                      "signed-in Claude Max firstParty, no API key). No generated, traced, resampled or palette-reduced image anywhere; "
                      "every pixel is one of the declared palette colours; binary alpha.",
        "style_reference": "accepted interiors (NYC public facilities rooms 1/2, Yonkers maintenance room 2): warm masonry, ivy, worn "
                           "metal, brass, restrained teal technology; teal/brass/ink/slate kit colours are the accepted room 2 fixture palette",
        "canvas": [W, H], "palette_size": len(HEX), "palette": HEX,
        "layers_bottom_to_top": SCENE_LAYERS,
        "editable_sources": {ext: {"file": rel(OUT / f"{stem}.{ext}"), "sha256": sha(d), "hash_algorithm": "sha256-bytes"} for ext, d in files.items()},
        "runtime_exports": {
            "plate": {"from_layers": PLATE_LAYERS, "rule": "alpha-over composite of layers 1-9, fully opaque, drawn at (0,0) 640x360 with nearest filtering",
                      "file": rel(names["plate"]), "sha256": sha(runtime["plate"]), "hash_algorithm": "sha256-bytes"},
            "antennas": antenna_items,
            "foreground": {"from_layers": ["foreground-occluder"], "rule": "layer 13 as is, drawn at (0,0) above the heroine (z_index 1)",
                           "file": rel(names["foreground"]), "sha256": sha(runtime["foreground"]), "hash_algorithm": "sha256-bytes"},
        },
        "runtime_layout": {
            "antenna_sprite": "Sprite2D, centered=false, position=(clue x, %d), offset=(-64, -%d); host y_sort_enabled so the heroine (feet "
                              "origin) passes behind an antenna when her feet are above y %d" % (BASE_Y, SPRITE_H, BASE_Y),
            "clue_markers": "drawn on the floor in front of each plinth at (163,228) (320,228) (477,228); captions to the right of each marker",
            "interaction": "unchanged CLUE_POSITIONS radius 45 plus 42 px around each floor marker",
            "collision": "13 feet-point Rect2 blockers in survey_annex.gd (back wall to y 166, west pier and east wall with the stair and "
                         "door openings at y 236-281, front parapet from y 281, planter, cable drum, crate, the three plinths, C's three "
                         "guy anchors, and the raised cable trough behind dish B so the heroine is never fully hidden there); axis slide; "
                         "a start inside a blocker can walk out",
            "header": "English only, this room only: Save moves to x 398 and the back button widens to 125 px at x 503 so "
                      "'Return outside' fits (right edge 628)",
        },
        "source_tool": rel(Path(__file__)),
    }
    path = OUT / f"{PREFIX}_corridor-scene-manifest_unapproved-v03_{STAMP}.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(path)
    print("palette", len(HEX), "used", len(used))
    return manifest


if __name__ == "__main__":
    build()
