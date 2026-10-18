"""Yonkers outskirts survey annex room 1 (天线走廊 / Antenna Walkway): native pixel-art v06 outdoor readability pass.

The creator rejected the outdoor look again after v05 (4b9d66f1). Codex's 1x judgement of v05: the back wall is busy and
mechanical in small values and competes with the three antennas, the utility cabinets and the dish base are flat slabs,
and the composition still reads schematic next to the accepted Yonkers room 2. v06 imports the v05 author unchanged (which
imports v04 and the committed v03 author unchanged), rebuilds the same 13 layers and replaces or adds these passes:
  1. calm back wall: the wall face is in shade (the sun is behind the parapet), so it is re-coursed as long ashlar in a
     narrow value range (two new half-step stone tones), joints one step darker instead of mortar-black, catch-light on
     some blocks only, broad value masses instead of per-block noise, no spalls, repair stones, lime bloom or per-pixel
     damp; quiet zones behind each antenna (no marks at all, a darker field behind the pale dish); one stepped crack,
     two broad rain-wash runs and six short weeps outside the quiet zones; calm pilasters (lit west arris, turned east
     edge, uneven drums) instead of the v05 4-row stripes;
  2. utility volume: the three wall junction boxes and the two wall cabinets get a visible top face with a short lit
     front arris, a lid-lip shadow, a lit west edge, a turned east edge, a kick base and a soft wall shadow; the three
     boxes are no longer identical (lamp / louvres / meter window); the crate and the dish's cable trough are redrawn
     as top face + front face + base course with chamfered corners; the planter is re-toned the same way; all floor
     fixtures get a contact shadow with a short tail away from the sun;
  3. antenna bases and cabinets, colour only: plinths A and C get a lit top face, a crisp front arris, a shaded front
     face and a dark foot; the dish base B is a drum (lit west, turned east) under the same lit top; the readout
     cabinets and the battery get a top face, lid-lip shadow, turned edge and kick base. Antenna alpha equals v05;
  4. calmer deck: weathering patches on about a third of the slabs instead of all, fewer lichen rosettes, leaves and
     broken / lost / raised / sunken slabs; the dashed safety-paint boxes around the pads lose their verticals and fade;
  5. calmer front parapet face and side piers: their v05 ashlar keeps its shapes but its values are compressed into the
     same narrow shaded range (stone pixels only; door, lamp, stair, plates and ivy untouched).
Unchanged: sky, skyline, coping silhouette above y 92, foreground, antenna alpha (sprite boxes, anchors 163/320/477 at
y 210, HUD clearance, clue ids), the walk lane and grating, the doors layer's non-stone pixels, and everything in
survey_annex.gd (clue positions, markers, collision, transitions). Every pixel uses the declared palette (v05 colours
plus two named half-step stone tones); alpha is binary. No generated, traced, resampled or palette-reduced image; the
seeded rng only chooses layout among authored shapes (block widths, which blocks get a catch-light).

Outputs go to outputs/yonkers-room1-v06_c8f0d900/ only. Nothing under game/ is written (runtime stays on v03).

Usage: python -I <this file>
"""

from __future__ import annotations

import importlib.util
import json
import math
import random
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261018-084726-c8f0d900"
V05_AUTHOR = ROOT / "tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_scene-quality-refinement-author_unapproved-v05_20261018-043851-4b9d66f1.py"
OUT = ROOT / "outputs" / "yonkers-room1-v06_c8f0d900"
EXPORTS = OUT / "exp"  # short folder name: the full paths must stay under Windows MAX_PATH in the primary checkout
PREFIX = "rpg-2-star-ocean-the-second_yonkers-antenna-room1"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V5 = load("yk1v05_author", V05_AUTHOR)
A, V4 = V5.A, V5.V4
W, H = A.W, A.H
Layer, composite = A.Layer, A.composite

# Two half-step stone tones so the shaded wall can carry its courses with less contrast than v05's full steps.
EXTRA_HEX_V06 = {"st_half_lit": "#8e846a", "st_half_dk": "#726b55"}
for _k, _v in EXTRA_HEX_V06.items():
    _rgb = tuple(int(_v[i:i + 2], 16) for i in (1, 3, 5))
    assert _rgb not in A.NAME_OF, _k
    A.HEX[_k], A.RGB[_k], A.RGBA[_k], A.NAME_OF[_rgb] = _v, _rgb, np.array(_rgb + (255,), np.uint8), _k
A.SHADE.update({"st_half_lit": "st_mid", "st_half_dk": "st_dk"})
V5.DN.update({"st_half_lit": "st_mid", "st_half_dk": "st_dk"})
V5.UP.update({"st_half_lit": "st", "st_half_dk": "st_mid"})
V5.STONE |= {"st_half_lit", "st_half_dk"}
STONE = V5.STONE
HALF_DN = {"st_hi": "st", "st": "st_half_lit", "st_half_lit": "st_mid", "st_mid": "st_half_dk", "st_half_dk": "st_dk", "st_dk": "st_deep",
           "st_deep": "st_deep", "mortar": "mortar", "lichen": "st_mid", "st_wet": "st_deep", "st_cool": "st_mid", "st_cool_dk": "st_dk",
           "lich_y": "lich_y_dk", "lich_y_dk": "st_dk"}
HALF_UP = {"st_half_dk": "st_mid", "st_mid": "st_half_lit", "st_half_lit": "st", "st_dk": "st_half_dk", "st": "st_hi", "st_hi": "st_hi"}
# compress v05 ashlar into the shaded range: shapes stay, contrast halves
CALM = {"st_hi": "st_half_lit", "st": "st_half_lit", "st_mid": "st_mid", "st_dk": "st_half_dk", "st_deep": "st_dk", "mortar": "st_dk",
        "st_wet": "st_dk", "st_cool": "st_mid", "st_cool_dk": "st_half_dk", "lichen": "st_mid", "lich_y": "st_half_lit", "lich_y_dk": "st_mid"}
PILASTERS, BAYS = A.PILASTERS, V5.BAYS
name = V5.name

# quiet wall behind each antenna: (x0, x1, field tone). The pale dish gets a darker field, the dark lattice and the
# thin guyed whip a plain mid field.
QUIET = [(118, 212, "st_mid"), (270, 374, "st_half_dk"), (450, 510, "st_mid")]


def quiet_at(x):
    for x0, x1, tone in QUIET:
        if x0 <= x <= x1:
            return tone
    return None


# ----------------------------------------------------------------------------- 1 calm back wall
CRACK = [(522, 109), (522, 117), (531, 117), (531, 127), (538, 127), (538, 137)]
WASH6 = [(226, 22), (531, 30)]  # broad rain-wash run below a leaking coping joint (x, cells)
DAMP6 = [60, 236, 392, 446, 586]  # where water reaches the wall foot


def calm_block(T, rng, bx0, by0, bx1, by1, tone, close_right, quiet):
    T.rect(bx0, by0, bx1, by1, tone)
    T.hline(bx0, bx1, by1, "st_dk")  # bed joint one step darker, not mortar-black
    if close_right:
        T.vline(bx1, by0, by1, "st_dk")
    if quiet or bx1 - bx0 < 8:
        return
    if rng.random() < 0.4:  # some blocks still catch a little sky on their upper arris
        T.hline(bx0 + 1, bx0 + int((bx1 - bx0) * rng.uniform(0.3, 0.7)), by0, HALF_UP[tone])
    if rng.random() < 0.15:  # a worn lower corner
        T.hline(bx1 - 3, bx1 - 1, by1 - 1, HALF_DN[tone])


def calm_wall(L, rng, bx0, bx1):
    courses = rng.choice(([10, 9, 10, 9, 10], [9, 10, 10, 9, 10], [10, 10, 9, 10, 9]))  # rows 108..155
    T = Layer()
    y = 108
    for ci, h in enumerate(courses):
        x = bx0 - rng.randint(0, 20)
        while x <= bx1:
            q = quiet_at(x + 18)
            w = rng.randint(30, 52) if q else rng.randint(22, 44)
            b0, b1 = max(x, bx0), min(x + w - 1, bx1)
            cx = (b0 + b1) / 2
            q = quiet_at(cx)
            if ci == len(courses) - 1:
                tone = "st_half_dk"  # the wall foot is the most shaded and damp course
            elif q:
                tone = q
            else:
                f = math.sin(cx / 47.0 + ci * 0.9) + 0.7 * math.sin(cx / 113.0 - ci * 0.4) + rng.uniform(-0.35, 0.35)
                tone = "st_half_dk" if f > 1.05 else ("st_half_lit" if f < -1.25 else "st_mid")
            calm_block(T, rng, b0, y, b1, y + h - 1, tone, x + w - 1 <= bx1, q is not None)
            x += w
        y += h
    m = np.zeros((H, W), bool)
    m[108:156, bx0:bx1 + 1] = True
    L.a[m] = T.a[m]


def calm_pilasters(L, rng):
    """Lit west arris, half-lit face, turned east edge, uneven drums with a short lit upper arris, a damp foot."""
    for k, p in enumerate(PILASTERS):
        for y in range(100, 156):
            for x in range(p, p + 16):
                r = x - p
                c = "st" if r <= 1 else ("st_half_lit" if r <= 10 else ("st_mid" if r <= 13 else "st_half_dk"))
                if y >= 151:
                    c = HALF_DN[c]
                L.px(x, y, c)
        y = 100 + k * 3 + 8
        while y < 148:
            for x in range(p, p + 16):
                L.px(x, y, "st_mid" if x - p <= 13 else "st_dk")
            L.hline(p + 1, p + 3 + (y % 4), y + 1, "st")
            y += rng.choice((10, 11, 12, 13))
        V5.stamp(L, p + 12, 112 + k * 7, ["dm", ".l"], {"d": "st_dk", "m": "st_half_dk", "l": "st_half_lit"})
        if k in (1, 3):
            V5.stamp(L, p + 6, 104 + k * 5, [".y.", "yYy", ".y."], {"y": "lich_y_dk", "Y": "lich_y"})
        for x in range(p + 2, p + 9):
            L.px(x, 155, "moss_dk" if x % 3 else "moss")
        L.hline(p, p + 15, 99, "st_deep")
    for k, p in enumerate(PILASTERS):  # caps exactly as v05 drew them
        L.rect(p - 2, 92, p + 17, 92, "st")
        L.hline(p - 1, p + 12 - k, 92, "st_hi")
        L.rect(p - 2, 94, p + 17, 96, "st_mid")
        L.hline(p - 2, p + 17, 94, "st")
        L.px(p + 4 + k * 3, 92, "st_dk")
        L.a[92, p + 14 - k:p + 16 - k, 3] = 0


def parapet_pass6(L):
    rng = random.Random(6061)
    joints_all, depth_all = [], []
    for bx0, bx1 in BAYS:
        calm_wall(L, rng, bx0, bx1)
        C = Layer()
        joints, depth = V5.coping(C, rng, bx0, bx1, 99, 4, notch_p=0.15, sag_p=0.2, tones=("st", "st", "st", "st_hi"), arris_p=0.35)
        m = np.zeros((H, W), bool)
        m[99:108, bx0:bx1 + 1] = True
        L.a[m] = C.a[m]
        joints_all += joints
        depth_all += depth
    for sx0, sx1, d in depth_all:  # the coping's drip shadow: one dark row, deeper where a stone sags
        for x in range(sx0, sx1 + 1):
            for y in range(108, 108 + min(d, 3)):
                c = name(L, x, y)
                if c in STONE:
                    L.px(x, y, "st_dk" if y == 108 else HALF_DN[c])
    weeps = [jx for jx in joints_all if quiet_at(jx) is None and not any(p - 3 <= jx <= p + 19 for p in PILASTERS)][::2][:6]
    for i, jx in enumerate(weeps):
        n = 6 + (i * 5) % 7
        for k in range(n):
            if k > n * 0.6 and k % 2:
                continue
            c = name(L, jx, 110 + k)
            if c in STONE:
                L.px(jx, 110 + k, HALF_DN[c])
    for k, (cx, n) in enumerate(WASH6):
        for x, y in V5.blob(random.Random(660 + k), cx, 110, n, cx - 6, 109, cx + 6, 140, dirs=((0, 1), (0, 1), (0, 1), (1, 0), (-1, 0))):
            c = name(L, x, y)
            if c in STONE and c != "st_dk":
                L.px(x, y, HALF_DN[c])
    for (xa, ya), (xb, yb) in zip(CRACK, CRACK[1:]):
        L.line(xa, ya, xb, yb, "st_dk")
        if xa == xb:
            for y in range(min(ya, yb), max(ya, yb) + 1):
                if name(L, xa + 1, y) in STONE:
                    L.px(xa + 1, y, HALF_UP.get(L.name_at(xa + 1, y), L.name_at(xa + 1, y)))
    for k, d in enumerate(DAMP6):  # damp only where water comes down: one compact cluster at the foot, moss in its joint
        for x, y in V5.blob(random.Random(670 + k), d, 154, 26, d - 8, 150, d + 8, 155):
            c = name(L, x, y)
            if c in STONE:
                L.px(x, y, "moss_dk" if y == 155 else "st_dk")
    calm_pilasters(L, rng)


# ----------------------------------------------------------------------------- 2 utility volume on the wall
STEEL = {"top": "edge", "hi": "plate_hi", "face": "slate", "lit": "steel", "turn": "deep", "out": "ink"}
TEAL = {"top": "teal", "hi": "frost_mid", "face": "teal_dk", "lit": "teal", "turn": "deep", "out": "ink"}
BOX_TOP_H = 3
WALL_BOXES = [(x0, 124, x0 + 16, 144) for x0 in A.JUNCTION_X] + [(46, 112, 72, 153), (574, 110, 598, 154)]


def volume_box(L, x0, y0, x1, y1, pal, top_h):
    """A box seen from the walkway: a top face above the front face (open corners, so the silhouette is chamfered),
    a short lit front arris, a shadow row under the lid lip, a lit west edge, a turned east edge and a kick base."""
    ty = y0 - top_h
    L.rect(x0 + 1, ty, x1 - 1, y0 - 1, pal["top"])
    L.hline(x0 + 1, x1 - 1, ty, pal["out"])
    L.vline(x0, ty + 1, y1, pal["out"])
    L.vline(x1, ty + 1, y1, pal["out"])
    L.hline(x0 + 1, x0 + 1 + int((x1 - x0) * 0.45), y0 - 1, pal["hi"])
    L.rect(x0 + 1, y0, x1 - 1, y1 - 1, pal["face"])
    L.hline(x0 + 1, x1 - 1, y0, pal["turn"])
    L.vline(x0 + 1, y0 + 1, y1 - 2, pal["lit"])
    L.vline(x1 - 1, y0, y1 - 1, pal["turn"])
    L.hline(x0 + 1, x1 - 1, y1 - 1, pal["turn"])
    L.hline(x0, x1, y1, pal["out"])


def wall_kit_volume(K):
    for i, x0 in enumerate(A.JUNCTION_X):
        volume_box(K, x0, 124, x0 + 16, 144, STEEL, BOX_TOP_H)
        K.vline(x0 + 9, 127, 141, "deep")  # door seam
        K.rect(x0 + 11, 132, x0 + 12, 135, "br")  # latch
        K.px(x0 + 11, 132, "br_hi")
        if i == 0:  # A: the warning lamp under a small hood
            K.rect(x0 + 3, 128, x0 + 6, 131, "teal_dk")
            K.hline(x0 + 3, x0 + 6, 127, "edge")
            K.px(x0 + 4, 129, "warn")
            K.px(x0 + 5, 129, "warn")
        elif i == 1:  # B: louvres and a steady lamp
            for y in (133, 135, 137, 139):
                K.hline(x0 + 3, x0 + 7, y, "deep")
            K.px(x0 + 4, 128, "glow")
            K.px(x0 + 5, 128, "teal")
        else:  # C: a meter window with its needle, lamp on the door
            K.rect(x0 + 3, 128, x0 + 7, 131, "frost_mid")
            K.hline(x0 + 3, x0 + 7, 128, "edge")
            K.line(x0 + 4, 131, x0 + 6, 129, "ink")
            K.px(x0 + 13, 128, "glow")
        K.rect(x0 + 6, 145, x0 + 10, 146, "deep")  # conduit gland
    # west patch cabinet (teal)
    volume_box(K, 46, 112, 72, 153, TEAL, BOX_TOP_H)
    K.vline(59, 115, 150, "ink")
    for yy in range(120, 146, 4):
        K.hline(50, 56, yy, "deep")
        K.hline(62, 69, yy, "deep")
    K.px(51, 116, "glow")
    K.px(53, 116, "glow")
    K.px(64, 116, "warn")
    K.rect(57, 130, 58, 134, "br")
    K.px(57, 130, "br_hi")
    K.rect(45, 154, 73, 155, "ink")
    K.hline(46, 72, 154, "deep")
    # east switch cabinet (steel); its top meets the coping, so a 2-row top face
    volume_box(K, 574, 110, 598, 154, STEEL, 2)
    K.rect(578, 116, 594, 128, "teal_dk")
    K.hline(578, 594, 116, "deep")
    for i, x in enumerate(range(580, 594, 3)):
        K.rect(x, 118, x + 1, 126 - (i % 3) * 2, "glow" if i < 3 else "teal")
    K.hline(578, 594, 132, "deep")
    for yy in range(136, 150, 3):
        K.hline(579, 593, yy, "deep")
    K.rect(595, 138, 596, 142, "br")
    K.px(595, 138, "br_hi")


def wall_box_shadow(P, K):
    """Soft shadow of each box on the shaded wall: two columns east and two rows under, half a step darker."""
    for x0, y0, x1, y1 in WALL_BOXES:
        cells = [(x, y) for x in (x1 + 1, x1 + 2) for y in range(y0 - 1, y1 + 3)] + [(x, y) for y in (y1 + 1, y1 + 2) for x in range(x0 + 2, x1 + 3)]
        for x, y in cells:
            if 0 <= x < W and 0 <= y < H and K.a[y, x, 3] != 255:
                c = name(P, x, y)
                if c in STONE and c not in ("st_deep", "mortar"):
                    P.px(x, y, HALF_DN[c])


# ----------------------------------------------------------------------------- 3 floor fixtures (deck-detail layer)
CRATE = (380, 412, 157, 165, 179)  # x0, x1, lid top, front top, front bottom
TROUGH = (290, 361, 160, 167, 185)
PLANTER = (44, 98, 166, 173, 184)
DETAIL_EDIT_RECTS = [(377, 154, 415, 181), (288, 158, 363, 187), (43, 165, 99, 185)]  # crate, trough, planter (x0, y0, x1, y1)
PAINT_BOXES = [(A.ANTENNA_X[0] - 42, A.ANTENNA_X[0] + 31), (A.ANTENNA_X[1] - 33, A.ANTENNA_X[1] + 41), (A.ANTENNA_X[2] - 48, A.ANTENNA_X[2] + 64)]


def crate6(L):
    x0, x1, lt, ft, fb = CRATE
    L.a[154:181, 377:416] = 0
    L.rect(x0 + 1, lt, x1 - 1, ft - 1, "wood_hi")  # lid seen from above
    L.hline(x0 + 1, x1 - 1, lt, "wood")
    L.hline(x0 + 1, x1 - 1, lt + 4, "wood")  # lid plank seam
    L.hline(x0 + 1, x0 + 15, ft - 1, "paper_dk")  # worn front arris, short
    L.vline(x0, lt + 1, fb, "br_dk")
    L.vline(x1, lt + 1, fb, "br_dk")
    L.rect(x0 + 1, ft, x1 - 1, fb - 1, "wood")
    L.hline(x0 + 1, x1 - 1, ft, "br_dk")  # under the lid lip
    for y in (170, 174):
        L.hline(x0 + 1, x1 - 1, y, "br_dk")
    L.vline(x0 + 1, ft + 1, fb - 1, "wood_hi")
    L.vline(x1 - 1, ft, fb - 1, "br_dk")
    L.hline(x0, x1, fb, "br_dk")
    for bx in (x0, x1 - 2):  # brass corner brackets, the west one catching light
        L.rect(bx, ft, bx + 2, ft + 2, "br")
    L.px(x0, ft, "br_hi")
    L.ellipse(388, 156, 402, 162, "ink")  # cable coil on the lid
    L.ellipse(391, 157, 399, 161, "wood_hi")
    L.hline(390, 398, 156, "deep")
    L.px(392, 157, "steel")


def trough6(L):
    x0, x1, tt, ft, fb = TROUGH
    L.a[158:188, 288:364] = 0
    L.rect(x0, tt, x1, ft - 1, "st")  # stone top with steel lids
    L.hline(x0 + 1, x1 - 1, tt, "st_mid")
    for i, x in enumerate(range(x0 + 2, x1 - 10, 12)):
        L.rect(x, tt + 1, x + 10, ft - 2, "edge")  # steel lids face the sky, so they are lit like the stone
        L.hline(x, x + 4, tt + 1, "plate_hi")
        L.vline(x + 10, tt + 1, ft - 2, "steel")
        L.px(x + 5, tt + 3, "slate")
        if i == 2:
            L.hline(x + 1, x + 9, tt + 3, "steel")  # one older lid
    L.hline(x0 + 1, x0 + 32, ft - 1, "st_hi")  # short lit front arris
    L.rect(x0, ft, x1, fb, "st_half_dk")  # the front faces away from the sun
    L.hline(x0, x1, ft, "st_dk")  # shadow under the top's lip
    L.vline(x0, ft + 1, fb - 2, "st_mid")
    L.vline(x1 - 1, ft, fb - 1, "st_dk")
    L.vline(x1, ft, fb - 1, "st_deep")
    for x in (303, 322, 341, 353):  # unequal block joints in the front
        L.vline(x, ft + 2, fb - 4, "st_dk")
    L.hline(x0, x1, fb - 3, "st_mid")  # base course lip
    L.rect(x0, fb - 2, x1, fb - 1, "st_dk")
    L.hline(x0, x1, fb, "st_deep")
    for x, y in ((x0, tt), (x1, tt), (x0, fb), (x1, fb)):
        L.a[y, x, 3] = 0  # chamfered corners
    for x in (300, 301, 352):
        L.px(x, fb - 1, "moss")
    L.px(353, fb - 2, "moss_hi")


def planter6(L):
    x0, x1, tt, ft, fb = PLANTER
    for y in range(tt, fb + 1):
        for x in range(x0, x1 + 1):
            c = name(L, x, y)
            if c not in STONE:
                continue  # ivy and tendrils stay
            if y < ft:
                n = "st_hi" if y == ft - 1 and x < x0 + 24 else ("st_mid" if y == tt else "st")
            elif y == ft:
                n = "st_dk"
            elif y >= fb - 1:
                n = "st_deep" if y == fb else "st_dk"
            else:
                n = "st_mid" if x == x0 else ("st_deep" if x >= x1 - 1 else ("st_dk" if (x - x0) % 12 == 8 else "st_half_dk"))
            L.px(x, y, n)


def safety_paint6(L):
    """The dashed boxes around the pads read as a diagram: drop their verticals and fade the front line."""
    for x0, x1 in PAINT_BOXES:
        for y in range(184, 213):
            for x in (x0, x1):
                if name(L, x, y) in ("paper_dk", "warn_dk"):
                    L.a[y, x, 3] = 0
        for x in range(x0, x1 + 1):
            c = name(L, x, 213)
            if c == "paper_dk":
                L.px(x, 213, "dk_hi")
            elif c == "warn_dk":
                L.px(x, 213, "dk_rust")


def fixture_contact(sh, under, feet):
    """Contact under floor fixtures: a dark row under the base, then a short tail away from the sun (lower right)."""
    for x0, x1, base in feet:
        for dy, xa, xb, depth in ((1, x0, x1 + 1, 2), (2, x0 + 2, x1 + 3, 1), (3, x0 + 6, x1 + 4, 1)):
            y = base + dy
            for x in range(xa, xb + 1):
                if (dy == 3 and x % 2) or under[y, x, 3] != 255:
                    continue
                c = A.NAME_OF[tuple(int(v) for v in under[y, x, :3])]
                for _ in range(depth):
                    c = A.shade_of(c)
                sh.a[y, x] = A.RGBA[c]


# ----------------------------------------------------------------------------- 4 antenna bases and cabinets (colour only)
CABINETS = {  # layer index: [(x0, y0, x1, y1, lid rows)] boxes drawn by the v03 antenna functions
    9: [(126, 166, 142, 209, (167, 168))],
    10: [(328, 150, 348, 170, (151, 152))],
    11: [(497, 180, 521, 209, ()), (481, 130, 499, 143, (131, 132))],
}


def plinth_volume(L, i):
    x0, x1, top = V4.PLINTHS[i]
    span = x1 - x0
    for y in range(top, A.BASE_Y):
        for x in range(x0, x1 + 1):
            if name(L, x, y) not in STONE:
                continue  # bolts, rust, moss, steel parts keep their colour
            t = (x - x0) / span
            if y == top:
                n = "st_mid"  # far edge of the top face
            elif y < top + 4:
                n = "st"
            elif y == top + 4:
                n = "st_hi" if t < 0.55 else "st"  # crisp front arris, lit only toward the sun
            elif y == top + 5:
                n = "st_dk"  # the cap overhangs the face a little
            elif y == A.BASE_Y - 1:
                n = "st_deep"
            elif y >= A.BASE_Y - 3:
                n = "st_dk"
            elif i == 1:  # dish base: a drum, lit west, turned east; the front faces away from the sun
                n = "st_mid" if t < 0.2 else ("st_half_dk" if t < 0.55 else ("st_dk" if t < 0.93 else "st_deep"))
            else:
                n = "st_mid" if x == x0 else ("st_deep" if x >= x1 - 1 else "st_half_dk")
            L.px(x, y, n)
    for cx in (x0 + 9, x1 - 7):  # two chips in the front arris
        if name(L, cx, top + 4) in STONE:
            L.px(cx, top + 4, "st_mid")
            L.px(cx + 1, top + 4, "st_dk")
            L.px(cx + 1, top + 5, "st_deep")


def cabinet_volume(L, x0, y0, x1, y1, lid):
    """Recolour slate pixels only: lid rows as a top face, a lid-lip shadow, a turned east edge and a kick base."""
    def swap(x, y, to, frm=("slate",)):
        if name(L, x, y) in frm:
            L.px(x, y, to)
    for y in lid:
        for x in range(x0 + 1, x1):
            swap(x, y, "steel" if y == lid[-1] else "edge", ("slate", "steel", "edge"))
    if lid:
        for x in range(x0 + 1, x0 + 1 + (x1 - x0) // 2):
            swap(x, lid[0], "plate_hi", ("edge",))
        for x in range(x0 + 2, x1):
            swap(x, lid[-1] + 1, "deep")
    for y in range(y0 + 1, y1):
        swap(x1 - 1, y, "deep")
        swap(x0 + 1, y, "steel")
    if y1 - y0 > 20:
        for y in range(y1 - 4, y1):
            for x in range(x0 + 2, x1 - 1):
                swap(x, y, "deep")


def antenna_volume(layers):
    for i in range(3):
        L = layers[9 + i]
        before = L.a[..., 3].copy()
        plinth_volume(L, i)
        for box in CABINETS[9 + i]:
            cabinet_volume(L, *box)
        assert (L.a[..., 3] == before).all(), "antenna alpha must not change"


# ----------------------------------------------------------------------------- 5 calmer deck
RAISED6 = [(1, 120), (4, 520), (5, 90)]
SUNKEN6 = [(2, 205), (4, 360)]
BROKEN6 = [(3, 140), (2, 470), (5, 545)]
LOST6 = [(4, 110), (5, 205), (2, 585)]
LICHEN6 = [(60, 199), (268, 189), (556, 182), (84, 232)]
LEAVES6 = [(44, 200), (594, 231), (104, 162), (520, 161)]


def deck_layer6(rng):
    """The v05 deck with the same slab layout rules, but weathering patches on about a third of the slabs and fewer
    special slabs, lichen and leaves."""
    saved = (V5.RAISED, V5.SUNKEN, V5.BROKEN, V5.LOST, V5.LICHEN, V5.LEAVES, V5.blob)
    V5.RAISED, V5.SUNKEN, V5.BROKEN, V5.LOST, V5.LICHEN, V5.LEAVES = RAISED6, SUNKEN6, BROKEN6, LOST6, LICHEN6, LEAVES6
    patch_rng = random.Random(4646)
    blob5 = saved[-1]

    def blob6(r, cx, cy, n, x0, y0, x1, y1, dirs=((1, 0), (-1, 0), (0, 1), (0, -1), (1, 0), (-1, 0))):
        cells = blob5(r, cx, cy, n, x0, y0, x1, y1, dirs)
        if r is rng and patch_rng.random() > 0.33:
            return set()  # an in-slab weathering patch: keep only about a third of them
        return cells
    V5.blob = blob6
    try:
        return V5.deck_layer(rng)
    finally:
        V5.RAISED, V5.SUNKEN, V5.BROKEN, V5.LOST, V5.LICHEN, V5.LEAVES, V5.blob = saved


# ----------------------------------------------------------------------------- 6 calmer front parapet and piers
def calm_values(L, y0, y1, x0=0, x1=W - 1, keep=()):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = name(L, x, y)
            if c in CALM and c not in keep:
                L.px(x, y, CALM[c])


# ----------------------------------------------------------------------------- build
def build_scene():
    layers, _ = V4.build_scene()
    sky, parapet, kit, _deck, walk, detail, _shadow, doors, front, a, b, c, fg = layers
    parapet_pass6(parapet)
    wall_kit_volume(kit)
    V5.kit_pass(kit, parapet)
    wall_box_shadow(parapet, kit)
    deck = deck_layer6(random.Random(4040))
    V5.walkway_pass(walk)
    V5.detail_pass(detail)
    crate6(detail)
    trough6(detail)
    planter6(detail)
    safety_paint6(detail)
    under = composite([sky, parapet, kit, deck, walk, detail])
    X = A.ANTENNA_X
    contact = [(X[0] - 37, A.BASE_Y, X[0] + 28, A.BASE_Y + 1), (X[1] - 28, A.BASE_Y, X[1] + 38, A.BASE_Y + 1),
               (X[2] - 33, A.BASE_Y, X[2] + 45, A.BASE_Y + 1), (224, 185, 258, 186), (380, 180, 413, 181),
               (38, 157, 597, 160), (38, 157, 45, 243), (590, 157, 597, 243), (45, 185, 100, 186), (290, 186, 363, 187)]
    shadows = A.shadow_layer(under, [a, b, c], contact, (parapet, kit))
    V4.contact_pass(shadows, under)
    fixture_contact(shadows, under, [(224, 257, 185), (380, 412, 180), (44, 98, 185), (290, 361, 186)])
    V5.piers_pass(doors)
    calm_values(doors, 92, 235, 1, 27, keep=("st_hi",))
    calm_values(doors, 92, 225, 611, 639, keep=("st_hi",))
    calm_values(doors, 291, 317, 1, 27, keep=("st_hi",))
    calm_values(doors, 291, 317, 611, 639, keep=("st_hi",))
    V5.front_pass(front)
    calm_values(front, 299, 317)
    V5.plinth_pass(layers)
    antenna_volume(layers)
    return [sky, parapet, kit, deck, walk, detail, shadows, doors, front, a, b, c, fg]


def write_gpl(path):
    lines = ["GIMP Palette", "Name: yonkers-antenna-room1-v06", "Columns: 8", "#"]
    for k, v in A.HEX.items():
        r, g, b_ = (int(v[i:i + 2], 16) for i in (1, 3, 5))
        lines.append(f"{r:3d} {g:3d} {b_:3d}\t{k}")
    data = ("\n".join(lines) + "\n").encode("utf-8")
    path.write_bytes(data)
    return data


def build():
    layers = build_scene()
    v05_layers = V5_REF()
    arrs = [l.a for l in layers]
    for a_ in arrs:
        assert set(np.unique(a_[..., 3]).tolist()) <= {0, 255}, "binary alpha only"
    for i in range(9, 13):
        assert (arrs[i][..., 3] == v05_layers[i].a[..., 3]).all(), "antenna and foreground alpha equal v05: " + A.SCENE_LAYERS[i]
    for i in range(3):
        x0, y0, x1, y1 = A.sprite_box(i)
        alpha = arrs[9 + i][..., 3]
        inside = np.zeros_like(alpha, bool)
        inside[y0:y1, x0:x1] = True
        assert not (alpha[~inside] > 0).any() and not (alpha[:A.ART_TOP] > 0).any()
    plate = composite(layers[:9])
    assert (plate[..., 3] == 255).all(), "plate must be opaque"
    flat = composite(layers)
    used = set()
    for a_ in arrs:
        used |= {tuple(int(v) for v in c_) for c_ in a_[a_[..., 3] == 255][:, :3]}
    assert used <= set(A.RGB.values()), "declared palette only"
    OUT.mkdir(parents=True, exist_ok=True)
    EXPORTS.mkdir(parents=True, exist_ok=True)
    imgs = [A.to_img(a_) for a_ in arrs]
    flat_img = A.to_img(flat)
    stem = f"{PREFIX}_readability-layers_unapproved-v06_{STAMP}"
    files = {"ora": (OUT / f"{stem}.ora", A.ora_bytes(stem, A.SCENE_LAYERS, imgs, flat_img)),
             "pxo": (OUT / f"{stem}.pxo", A.pxo_bytes("yonkers-room1-v06", A.SCENE_LAYERS, imgs, flat_img)),
             "png": (OUT / f"{PREFIX}_readability-native-640x360-flat_unapproved-v06_{STAMP}.png", A.png_bytes(flat_img))}
    for p, data in files.values():
        p.write_bytes(data)
    gpl_p = OUT / f"{PREFIX}_native-palette_unapproved-v06_{STAMP}.gpl"
    gpl = write_gpl(gpl_p)
    plate_p = EXPORTS / f"{PREFIX}_corridor-plate-readability_unapproved-v06_{STAMP}.png"
    fg_p = EXPORTS / f"{PREFIX}_foreground-occluder_unapproved-v06_{STAMP}.png"
    plate_b, fg_b = A.png_bytes(A.to_img(plate)), A.png_bytes(A.to_img(arrs[12]))
    plate_p.write_bytes(plate_b)
    fg_p.write_bytes(fg_b)
    antennas = []
    for i, slug in enumerate(A.ANTENNA_SLUGS):
        x0, y0, x1, y1 = A.sprite_box(i)
        crop = A.png_bytes(A.to_img(np.ascontiguousarray(arrs[9 + i][y0:y1, x0:x1])))
        p = EXPORTS / f"{PREFIX}_{slug}_unapproved-v06_{STAMP}.png"
        p.write_bytes(crop)
        antennas.append({"layer": A.ANTENNA_LAYERS[i], "clue": f"scifi.outskirts:{i}", "reads_as": A.ANTENNA_READS[i],
                         "crop_from_layer_xywh": [x0, y0, A.SPRITE_W, A.SPRITE_H], "anchor": [A.ANTENNA_X[i], A.BASE_Y],
                         "runtime_png": {"file": A.rel(p), "sha256": A.sha(crop), "hash_algorithm": "sha256-bytes"}})
    v05_flat = composite(v05_layers)
    manifest = {
        "project": "Worlds Between (rpg-2-star-ocean-the-second)",
        "scene": "Yonkers outskirts survey annex room 1 (天线走廊 / Antenna Walkway), scifi.outskirts room 1",
        "version": "v06 outdoor readability pass over v05 (4b9d66f1): calm shaded back wall with quiet zones behind the antennas, "
                   "utility boxes/cabinets/crate/trough/planter with top face, lit arris, turned edge, kick base and contact, "
                   "plinths and antenna cabinets with top face and foot (colour only), calmer deck, front parapet and piers",
        "status": "UNAPPROVED, NONRUNTIME, test-only. Not wired into the game: survey_annex.gd still loads v03, so v06 is off by "
                  "default. Scenes stay 3/12. No accepted flag, counter, ledger, Bible or Git index change.",
        "geography_note": "Fictional 2537 rooftop survey walkway in the Yonkers vicinity; generic Hudson-valley masonry and "
                          "utility hardware, not a reconstruction of any specific Yonkers landmark.",
        "base": {"author": A.rel(V05_AUTHOR), "v04_author": A.rel(Path(V4.__file__)), "v03_author": A.rel(V4.V03_AUTHOR),
                 "manifest": "outputs/yonkers-room1-v05_4b9d66f1/rpg-2-star-ocean-the-second_yonkers-antenna-room1_scene-quality-manifest_unapproved-v05_20261018-043851-4b9d66f1.json"},
        "quiet_zones_x": [[x0, x1, t] for x0, x1, t in QUIET],
        "detail_layer_edit_rects_xyxy": DETAIL_EDIT_RECTS,
        "safety_paint_boxes_x": PAINT_BOXES,
        "pixels_changed_vs_v05_flat": int((flat != v05_flat).any(axis=2).sum()),
        "pixels_changed_vs_v05_per_layer": {n: int((arrs[i] != v05_layers[i].a).any(axis=2).sum()) for i, n in enumerate(A.SCENE_LAYERS)},
        "authorship": "Native pixel art: hand-authored shapes, stamps and coordinate lists in this tool over the v05/v04/v03 layers, by "
                      "Claude (Claude Code). No generated, traced, resampled or palette-reduced image; declared palette only; binary alpha.",
        "canvas": [W, H], "palette_size": len(A.HEX), "palette": A.HEX, "palette_additions_vs_v05": EXTRA_HEX_V06,
        "native_palette_file": {"file": A.rel(gpl_p), "sha256": A.sha(gpl), "hash_algorithm": "sha256-bytes"},
        "layers_bottom_to_top": A.SCENE_LAYERS,
        "editable_sources": {k: {"file": A.rel(p), "sha256": A.sha(d), "hash_algorithm": "sha256-bytes"} for k, (p, d) in files.items()},
        "runtime_exports": {
            "note": "nonruntime exports in the v06 output folder only; nothing under game/ is written",
            "plate": {"from_layers": A.PLATE_LAYERS, "file": A.rel(plate_p), "sha256": A.sha(plate_b), "hash_algorithm": "sha256-bytes"},
            "antennas": antennas,
            "foreground": {"from_layers": ["foreground-occluder"], "file": A.rel(fg_p), "sha256": A.sha(fg_b), "hash_algorithm": "sha256-bytes"},
        },
        "source_tool": A.rel(Path(__file__)),
    }
    path = OUT / f"{PREFIX}_readability-manifest_unapproved-v06_{STAMP}.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(path)
    print("changed vs v05", manifest["pixels_changed_vs_v05_flat"], manifest["pixels_changed_vs_v05_per_layer"])
    return manifest


def V5_REF():
    """The v05 layers as the v05 author builds them (a fresh module, so the v06 palette registration cannot leak in)."""
    return load("yk1v05_author_ref", V05_AUTHOR).build_scene()


if __name__ == "__main__":
    build()
