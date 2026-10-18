"""Yonkers outskirts survey annex room 1 (天线走廊 / Antenna Walkway): native pixel-art v05 scene-quality refinement.

v05 is one coherent pass over the v04 material-depth candidate (523bba3b). It imports the v04 author unchanged (which
imports the committed v03 author unchanged), rebuilds the same 13 layers, and then re-authors the surfaces Codex still
judged rigid in the official Pixelorama GUI view of v04: wall, deck and grating read as repeated bands with weak
relief and homogeneous slabs next to the accepted Yonkers maintenance room 2. Passes:
  1. coping: individual coping stones with their own top tone, open joints, chipped arrises and notches in the
     silhouette, a shaded front face and a varying drip shadow under each stone (back and front parapets share it);
  2. wall face: irregular ashlar per bay (unequal course heights, two-course jumper stones, crisp / eroded / spalled
     arrises, flush and raked joints instead of one continuous mortar line), repair stones, a stepped crack, lime
     bloom under two coping joints, biofilm where conduits shed water; pilasters toned down with chips and lichen;
  3. wall kit: contact occlusion under every box, cabinet, tray, pipe and ivy clump; the cable tray opens in two
     places with cables showing and one loop sagging out; rust weeps under brackets; fewer brass clamps;
  4. deck: flagstones re-laid with unequal widths, jogged joints, chipped corners, raised and sunken slabs with
     clear contact shadows, broken slabs, a weathering patch inside each slab, joint moss and lichen rosettes where
     nobody walks, oil and rust stains at the machinery, leaf litter in the corners;
  5. grating: bearing bars across the lane with cross rods (cells, not stripes), a darker recessed field, polish
     only along the walking line, glints only on lit bar tops of that line in a few clusters, grime and leaves in the
     panel corners, a duller brass nosing and railing with short worn highlights;
  6. side piers and the east block re-coursed the same way (stone pixels only; ivy, plates, door and lamp kept).
Geometry is preserved: the antenna layers keep v04 alpha exactly (colour-only plinth weathering), so sprite boxes,
anchors (163/320/477, 210), HUD clearance and clue ids are unchanged; props, doors, stair, lane, markers, collision and
transitions live where v04 put them (survey_annex.gd is not touched). Every pixel uses the declared palette (v03 colours
plus a few named additions); alpha is binary. No generated, traced, resampled or palette-reduced image is used; the
seeded rng only chooses layout among authored shapes (block widths, which arris variant), never per-pixel noise.

Outputs go to outputs/yonkers-room1-v05_4b9d66f1/ only. Nothing under game/ is written (runtime stays on v03).

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
STAMP = "20261018-043851-4b9d66f1"
V04_AUTHOR = ROOT / "tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_material-depth-author_unapproved-v04_20261018-052445-523bba3b.py"
OUT = ROOT / "outputs" / "yonkers-room1-v05_4b9d66f1"
EXPORTS = OUT / "nonruntime-exports"
PREFIX = "rpg-2-star-ocean-the-second_yonkers-antenna-room1"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V4 = load("yk1v04_author", V04_AUTHOR)
A = V4.A
W, H = A.W, A.H
Layer, composite = A.Layer, A.composite

# Named palette additions (the v03 colours stay unchanged and first).
EXTRA_HEX = {
    "st_cool": "#8a8b7f", "st_cool_dk": "#6b6d64",  # newer repair stone, cooler than the old warm ashlar
    "st_wet": "#555749",  # damp stone / biofilm where conduits shed water
    "lich_y": "#b1a65d", "lich_y_dk": "#8a8551",  # crustose lichen rosettes on stone that nobody walks on
    "soil": "#4a3f31", "leaf": "#7b5d35", "leaf_dk": "#57432a",  # bedding under a lost slab corner, leaf litter
    "stain": "#3c4037",  # oil / grime stain on the deck
    "gr_deep": "#2b3436",  # grating cell depth between the bars
}
for _k, _v in EXTRA_HEX.items():
    _rgb = tuple(int(_v[i:i + 2], 16) for i in (1, 3, 5))
    assert _rgb not in A.NAME_OF, _k
    A.HEX[_k], A.RGB[_k], A.RGBA[_k], A.NAME_OF[_rgb] = _v, _rgb, np.array(_rgb + (255,), np.uint8), _k
A.SHADE.update({"st_cool": "st_cool_dk", "st_cool_dk": "st_dk", "st_wet": "st_deep", "lich_y": "lich_y_dk", "lich_y_dk": "st_dk",
                "soil": "st_deep", "leaf": "leaf_dk", "leaf_dk": "soil", "stain": "dk_seam", "gr_deep": "gr_hole"})

DN = {"st_hi": "st", "st": "st_mid", "st_mid": "st_dk", "st_dk": "st_deep", "st_deep": "mortar", "mortar": "mortar", "lichen": "st_mid",
      "st_cool": "st_cool_dk", "st_cool_dk": "st_dk", "st_wet": "st_deep", "lich_y": "lich_y_dk", "lich_y_dk": "st_dk"}
UP = {"st_hi": "st_hi", "st": "st_hi", "st_mid": "st", "st_dk": "st_mid", "st_deep": "st_dk", "mortar": "st_deep", "lichen": "st_hi",
      "st_cool": "st_hi", "st_cool_dk": "st_cool", "st_wet": "st_dk", "lich_y": "lich_y", "lich_y_dk": "lich_y"}
STONE = set(DN)
DK_UP = {"dk_c": "dk_b", "dk_b": "dk_a", "dk_a": "dk_worn", "dk_worn": "dk_hi", "dk_hi": "dk_hi", "dk_sh": "dk_c"}
DK_DN = {"dk_hi": "dk_worn", "dk_worn": "dk_a", "dk_a": "dk_b", "dk_b": "dk_c", "dk_c": "dk_sh", "dk_sh": "dk_sh2", "dk_sh2": "dk_seam",
         "dk_wet": "dk_sh2", "dk_seam": "stain", "stain": "dk_seam"}
FOLIAGE = {"lf_dk", "lf", "lf_mid", "lf_hi", "moss", "moss_hi", "moss_dk", "flower"}
PILASTERS = A.PILASTERS
BAYS = [(0, PILASTERS[0] - 1)] + [(PILASTERS[i] + 16, PILASTERS[i + 1] - 1) for i in range(3)] + [(PILASTERS[3] + 16, W - 1)]


def dn(n, k=1):
    for _ in range(k):
        n = DN.get(n) or DK_DN.get(n) or A.shade_of(n)
    return n


def name(L, x, y):
    return L.name_at(x, y) if 0 <= x < W and 0 <= y < H else None


def mask_of(arr, names):
    m = np.zeros(arr.shape[:2], bool)
    for n in names:
        m |= (arr[..., :3] == A.RGB[n]).all(axis=2)
    return m & (arr[..., 3] == 255)


def copy_where(dst, src, m):
    m = m & (src.a[..., 3] == 255)
    dst.a[m] = src.a[m]


# ----------------------------------------------------------------------------- shared stone vocabulary
def coping(L, rng, x0, x1, top, face_rows, joints_min=18, joints_max=44, notch_p=0.35, sag_p=0.3, repair_at=(),
           tones=("st", "st", "st", "st_hi"), arris_p=0.45):
    """A run of coping stones: lit top (3 rows), a shaded front face, a drip row and an underside row.
    Each stone has its own top tone, a dark open joint, an optional chipped arris (silhouette notch) and an
    optional chip at the lower face edge; sagging stones push a deeper shadow onto the wall below. Returns the
    joint x positions and the per-stone shadow depth (for the wall pass)."""
    joints, depth = [], []
    x = x0 - rng.randint(0, 14)
    while x <= x1:
        w = rng.randint(joints_min, joints_max)
        sx0, sx1 = max(x, x0), min(x + w - 1, x1)
        repaired = any(sx0 <= rx <= sx1 for rx in repair_at)
        t = "st_cool" if repaired else rng.choice(tones)
        face = dn(t)
        L.rect(sx0, top, sx1, top + 2, t)
        if rng.random() < arris_p:  # only some stones still have a crisp, sunlit far arris
            L.hline(sx0, sx1 - 1, top, UP[t])
        L.rect(sx0, top + 3, sx1, top + 2 + face_rows, face)
        L.hline(sx0, sx1, top + 3, t)  # the face's upper arris still catches a little sky
        L.hline(sx0, sx1, top + 3 + face_rows, "st_deep")
        L.hline(sx0, sx1, top + 4 + face_rows, "mortar")
        if x + w - 1 <= x1:
            L.vline(sx1, top, top + 2 + face_rows, "st_deep")
            L.px(sx1, top + 1, "mortar")
            joints.append(sx1)
        # weathered top: a lichen or pitting cluster on about half the stones
        if sx1 - sx0 > 8 and rng.random() < 0.5:
            cx = rng.randint(sx0 + 2, sx1 - 4)
            for dx, dy in ((0, 1), (1, 1), (1, 2), (2, 1)):
                L.px(cx + dx, top + dy, rng.choice(("lich_y", "lichen", "lich_y_dk")))
        if sx1 - sx0 > 10 and rng.random() < notch_p:  # chipped far arris: sky shows through, the break is shaded
            cx, n = rng.randint(sx0 + 2, sx1 - 5), rng.randint(2, 4)
            L.a[top, cx:cx + n, 3] = 0
            L.hline(cx, cx + n - 1, top + 1, dn(t))
            L.px(cx + n, top + 1, dn(t, 2))
        if sx1 - sx0 > 10 and rng.random() < 0.45:  # chip off the lower front edge: dark recess, lit lower lip
            cx, n = rng.randint(sx0 + 2, sx1 - 6), rng.randint(2, 5)
            L.hline(cx, cx + n, top + 1 + face_rows, "st_deep")
            L.hline(cx + 1, cx + n, top + 2 + face_rows, dn(face))
            L.px(cx + n + 1, top + 2 + face_rows, t)
        sag = rng.random() < sag_p
        depth.append((sx0, sx1, 3 if sag else rng.choice((1, 2, 2))))
        x += w
    return joints, depth


def paint_block(T, rng, bx0, by0, bx1, by1, tone, close_right, kinds=(0.55, 0.3, 0.15)):
    T.rect(bx0, by0, bx1, by1, tone)
    T.hline(bx0, bx1, by1, "mortar")
    if close_right:
        T.vline(bx1, by0, by1, "mortar")
    fx1, fy1 = (bx1 - 1 if close_right else bx1), by1 - 1
    if fx1 - bx0 < 2 or fy1 - by0 < 1:
        return
    kind = rng.choices(("crisp", "eroded", "spall"), kinds)[0]
    if kind == "eroded":  # weathered arris: no catch-light, rounded corners, a dip worn into the top edge
        T.hline(bx0, fx1, fy1, dn(tone))
        for cx, cy in ((bx0, by0), (fx1, by0), (bx0, fy1), (fx1, fy1)):
            T.px(cx, cy, dn(tone, 2))
        ex = rng.randint(bx0, fx1)
        T.hline(ex, min(ex + rng.randint(1, 3), fx1), by0, dn(tone))
    else:
        T.hline(bx0, bx0 + int((fx1 - bx0) * rng.uniform(0.3, 0.85)), by0, UP[tone])
        T.hline(bx0 + 1, fx1, fy1, dn(tone))
        if kind == "spall" and fx1 - bx0 > 8 and fy1 - by0 > 3:
            sw, sh = rng.randint(3, min(6, fx1 - bx0 - 3)), rng.randint(2, min(3, fy1 - by0 - 1))
            sx, sy = rng.randint(bx0 + 1, fx1 - sw - 1), rng.randint(by0 + 1, fy1 - sh)
            T.rect(sx, sy, sx + sw, sy + sh, dn(tone))
            T.hline(sx, sx + sw, sy, dn(tone, 2))
            T.vline(sx, sy, sy + sh, dn(tone, 2))
            T.hline(sx + 1, sx + sw, sy + sh, UP[tone])
    for _ in range((fx1 - bx0) // 20):  # a few small wear clusters, never on the arrises
        if fy1 - by0 < 3 or rng.random() < 0.4:
            break
        cx, cy = rng.randint(bx0 + 1, max(bx0 + 1, fx1 - 2)), rng.randint(by0 + 1, max(by0 + 1, fy1 - 2))
        T.rect(cx, cy, cx + rng.randint(0, 2), cy + rng.randint(0, 1), dn(tone))


def ashlar(T, rng, x0, x1, y0, courses, tone_fn, jumper_p=0.12, kinds=(0.55, 0.3, 0.15)):
    """Irregular coursed ashlar into a scratch layer: unequal course heights, unequal block widths, jumper stones
    spanning two courses, three arris variants, and bed joints that are flush or raked in places instead of one
    unbroken mortar line. Returns the block list."""
    blocks, y = [], y0
    for ci, h in enumerate(courses):
        x = x0 - rng.randint(0, 22)
        while x <= x1:
            w = rng.randint(13, 38)
            b = (max(x, x0), y, min(x + w - 1, x1), y + h - 1, x + w - 1 <= x1, ci)
            blocks.append(b)
            paint_block(T, rng, b[0], b[1], b[2], b[3], tone_fn(b), b[4], kinds)
            x += w
        y += h
    for b in [b for b in blocks if b[5] < len(courses) - 1 and b[2] - b[0] > 10 and rng.random() < jumper_p]:
        nb = (b[0], b[1], b[2], b[3] + courses[b[5] + 1], True, b[5])
        paint_block(T, rng, nb[0], nb[1], nb[2], nb[3], tone_fn(nb), True, kinds)
    yb = y0
    for h in courses[:-1]:  # bed joints: flush pointing (lighter) or raked out (deeper, shades the arris above)
        yb += h
        x = x0
        while x <= x1:
            n = rng.randint(3, 11)
            r = rng.random()
            for xx in range(x, min(x + n, x1 + 1)):
                if T.name_at(xx, yb - 1) != "mortar":
                    continue
                if r < 0.22:
                    T.px(xx, yb - 1, "st_dk")
                elif r < 0.34 and name(T, xx, yb - 2) in STONE:
                    T.px(xx, yb - 2, dn(T.name_at(xx, yb - 2)))
            x += n
    return blocks


def stamp(L, x, y, rows, palette, only=None):
    """Hand-drawn pixel cluster: rows of characters, '.' transparent, other characters index `palette`."""
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch == "." or not (0 <= x + dx < W and 0 <= y + dy < H):
                continue
            if only is not None and name(L, x + dx, y + dy) not in only:
                continue
            L.px(x + dx, y + dy, palette[ch])


def streak(L, x, y0, n, width=1):
    """A weep stain one tone darker than the stone it runs over, breaking up toward its tail."""
    for i in range(n):
        if i > n * 0.6 and (i + x) % 2:
            continue
        for dx in range(width):
            c = name(L, x + dx, y0 + i)
            if c in STONE and c != "mortar":
                L.px(x + dx, y0 + i, dn(c))


# ----------------------------------------------------------------------------- 1 back parapet
REPAIRS = [(150, 1), (472, 2), (523, 0)]  # (x, course) newer cooler stones set into the old wall
DAMP_X = [x + 8 for x in A.JUNCTION_X] + [p + 8 for p in PILASTERS] + [59, 586]  # where water is shed down the face
CRACKS_WALL = [[(122, 109), (122, 117), (116, 117), (116, 126), (111, 126), (111, 134)],
               [(503, 109), (503, 118), (497, 118), (497, 127), (490, 127), (490, 137), (486, 137), (486, 146)]]
BLOOM = [(231, 109, 7), (441, 109, 6), (346, 109, 5)]  # lime bloom under a leaking coping joint (x, y, length)
WASH = [(127, 170), (456, 190), (531, 110), (297, 120), (20, 90)]  # darker rain-wash run below ivy and leaking joints


def parapet_pass(L):
    rng = random.Random(5051)
    joints_all, depth_all = [], []
    for bx0, bx1 in BAYS:
        T = Layer()
        courses = rng.choice(([8, 10, 9, 7, 10], [9, 8, 11, 8, 8], [10, 7, 9, 10, 8], [7, 11, 8, 9, 9]))

        def tone(b, bx0=bx0):
            cx, ci = (b[0] + b[2]) / 2, b[5]
            for rx, rc in REPAIRS:
                if b[0] <= rx <= b[2] and ci == rc:
                    return "st_cool"
            if ci == 0:
                return rng.choice(("st_dk", "st_dk", "st_mid"))
            if ci == 4 and any(abs(cx - d) < 12 for d in DAMP_X):
                return "st_wet"
            return rng.choice(("st_mid", "st_mid", "st_mid", "st_mid", "st_dk", "st_dk", "st_dk", "st"))
        ashlar(T, rng, bx0, bx1, 108, courses, tone)
        m = np.zeros((H, W), bool)
        m[108:152, bx0:bx1 + 1] = True
        copy_where(L, T, m)
        C = Layer()
        joints, depth = coping(C, rng, bx0, bx1, 99, 4, repair_at=[r[0] for r in REPAIRS if r[1] == 0])
        m = np.zeros((H, W), bool)
        m[99:108, bx0:bx1 + 1] = True
        L.a[m] = C.a[m]
        joints_all += joints
        depth_all += depth
    for k, (cx, n) in enumerate(WASH):  # one broad, irregular darker run per leak, longer than it is wide
        for x, y in blob(random.Random(600 + k), cx, 109, n, cx - 14, 108, cx + 14, 146, dirs=((0, 1), (0, 1), (1, 0), (-1, 0), (0, -1))):
            c = name(L, x, y)
            if c in STONE and c != "mortar":
                L.px(x, y, dn(c))
    # shadow under each coping stone: deeper where it sags
    for sx0, sx1, d in depth_all:
        for x in range(sx0, sx1 + 1):
            for y in range(108, 108 + d):
                c = name(L, x, y)
                if c in STONE:
                    L.px(x, y, dn(c) if y > 108 or d < 3 else "mortar")
    # weeps below the coping joints, lime bloom under three of them, a stepped crack in two bays
    for i, jx in enumerate(joints_all):
        if not any(p - 3 <= jx <= p + 19 for p in PILASTERS):
            streak(L, jx + (i % 2), 110, 10 + (i * 7) % 14, 1 + (i % 3 == 0))
    for x, y, n in BLOOM:
        for i in range(n):
            for dx in ((0, 1) if i < n - 2 else (0,)):
                if name(L, x + dx, y + i) in STONE:
                    L.px(x + dx, y + i, "st_hi" if i % 3 != 2 else "lichen")
    for path in CRACKS_WALL:
        for (xa, ya), (xb, yb) in zip(path, path[1:]):
            L.line(xa, ya, xb, yb, "st_deep")
            if xa == xb:
                for y in range(min(ya, yb), max(ya, yb) + 1):
                    if name(L, xa + 1, y) in STONE:
                        L.px(xa + 1, y, UP[L.name_at(xa + 1, y)])
    # wall foot: damp course with biofilm only where water comes down, a dry line elsewhere
    for x in range(W):
        wet = any(abs(x - d) < 9 - (d % 3) for d in DAMP_X)
        for y in range(146 if wet else 151, 156):
            c = name(L, x, y)
            if c in STONE:
                if wet and y >= 149 + (x * 5) % 3:
                    L.px(x, y, "st_wet" if y < 155 else "moss_dk")
                elif wet:
                    L.px(x, y, dn(c))
    pilaster_pass(L, rng)
    return joints_all


def pilaster_pass(L, rng):
    """Tone the four pilasters down (they were the brightest stone), re-joint them unevenly, chip and lichen them."""
    for k, p in enumerate(PILASTERS):
        for y in range(99, 150):
            for x in range(p, p + 16):
                c = name(L, x, y)
                if c == "st_hi":
                    L.px(x, y, "st" if (y // 4) % 3 else "st_hi")
                elif c == "st" and x > p + 1:
                    L.px(x, y, "st" if x <= p + 2 + (y // 11 + k) % 2 else "st_mid")
        y = 100 + k * 3
        while y < 148:  # unequal drums with a shaded bed and a broken lit upper arris
            L.hline(p, p + 15, y, "st_deep")
            for x in range(p, p + 16):
                if (x * 3 + y) % 7 == 0:
                    L.px(x, y, "st_dk")
            L.hline(p + 1, p + 3 + (y % 5), y + 1, "st")
            y += rng.choice((8, 10, 11, 12))
        for cx, cy in ((p + 12, 112 + k * 7), (p + 1, 131 - k * 4)):  # corner chips
            stamp(L, cx, cy, ["dd.", "dm.", ".ml"][: 3], {"d": "st_deep", "m": "st_dk", "l": "st"})
        if k in (1, 3):  # lichen rosettes on the two pilasters in the open
            for cx, cy in ((p + 6, 104 + k * 5), (p + 9, 137 - k * 2)):
                stamp(L, cx, cy, [".y.", "yYy", ".y."], {"y": "lich_y_dk", "Y": "lich_y"})
        L.hline(p, p + 15, 99, "st_deep")
    # caps: darker face, lit far arris only, chipped
    for k, p in enumerate(PILASTERS):
        L.rect(p - 2, 92, p + 17, 92, "st")
        L.hline(p - 1, p + 12 - k, 92, "st_hi")
        L.rect(p - 2, 94, p + 17, 96, "st_mid")
        L.hline(p - 2, p + 17, 94, "st")
        L.px(p + 4 + k * 3, 92, "st_dk")
        L.a[92, p + 14 - k:p + 16 - k, 3] = 0


# ----------------------------------------------------------------------------- 2 wall kit
TRAY_OPEN = [(140, 152), (452, 466)]  # lid gone: cables show
TRAY_SAG = (300, 318)  # a cable loop slipping out of the tray


def kit_pass(K, P):
    """Contact occlusion of every wall fitting onto the stone face (layer P), plus tray/clamp/drip detail on K."""
    occ = np.zeros((H, W), bool)
    ys, xs = np.nonzero(K.a[..., 3] == 255)
    for x, y in zip(xs, ys):
        if y < 104 or y > 155:
            continue
        foliage = K.name_at(x, y) in FOLIAGE
        for dx, dy in (((1, 1),) if foliage else ((1, 1), (2, 2), (1, 2))):
            if 0 <= x + dx < W and 0 <= y + dy < H:
                occ[y + dy, x + dx] = True
    occ &= K.a[..., 3] != 255
    for y, x in zip(*np.nonzero(occ)):
        c = name(P, x, y)
        if c in STONE:
            P.px(x, y, dn(c))
    for x0, x1 in TRAY_OPEN:  # open tray: dark well, a teal signal line and a brass power line
        K.rect(x0, 116, x1, 119, "ink")
        K.hline(x0, x1, 117, "teal_dk")
        K.hline(x0 + 1, x1 - 2, 118, "br_dk")
        K.px(x0 + 3, 117, "teal")
        K.hline(x0 - 1, x0 + 1, 115, "edge")
        K.px(x1, 115, "steel")
    x0, x1 = TRAY_SAG
    for i in range(x1 - x0 + 1):
        y = 121 + int(round(4 * math.sin(math.pi * i / (x1 - x0))))
        K.px(x0 + i, y, "ink")
        if 0 < i < x1 - x0:
            K.px(x0 + i, y - 1, "teal_dk" if i % 5 else "teal")
    for i, x in enumerate(range(105 + 6, 556, 30)):  # rust weeping from most tray brackets, unevenly
        if any(p - 2 <= x <= p + 18 for p in PILASTERS) or i % 3 == 1:
            continue
        for i in range(3 + (x % 4)):
            if name(P, x, 125 + i) in STONE and (i < 3 or i % 2 == 0):
                P.px(x, 125 + i, "rust" if i < 2 else "br_dk")
    for x0, x1 in [(105, 240), (415, 555)]:  # brass service pipe: working finish, short glints, verdigris by the flanges
        for x in range(x0, x1 + 1):
            if K.name_at(x, 139) == "br_hi" and (x // 4) % 6:
                K.px(x, 139, "br")
        for fx in range(x0 + 10, x1, 34):
            for dx, dy in ((3, 141), (4, 141), (-1, 141), (5, 140)):
                if K.name_at(fx + dx, dy) in ("br", "br_dk"):
                    K.px(fx + dx, dy, "teal_dk")
    for jx in A.JUNCTION_X:  # brass hinge, darker foot, grime under the gland
        K.vline(jx + 1, 128, 130, "br")
        K.px(jx + 1, 128, "br_hi")
        K.hline(jx + 1, jx + 15, 143, "deep")
        for i in range(4):
            if name(P, jx + 4, 147 + i) in STONE:
                P.px(jx + 4, 147 + i, "st_wet")


# ----------------------------------------------------------------------------- 4 deck re-laid
ROW_EDGES = A.ROW_EDGES
TRAFFIC = A.TRAFFIC
# hand-placed: raised slab (r, x), sunken slab, broken slab, lost corner with soil and grass
RAISED = [(1, 120), (3, 260), (4, 520), (2, 410), (5, 90)]
SUNKEN = [(2, 205), (4, 360), (3, 560), (5, 300)]
BROKEN = [(3, 140), (4, 250), (2, 470), (5, 545), (1, 330)]
LOST = [(4, 110), (3, 395), (5, 205), (2, 585), (1, 270)]
LICHEN = [(60, 199), (112, 186), (206, 172), (268, 189), (378, 192), (430, 176), (556, 182), (585, 214), (402, 214), (250, 226),
          (84, 232), (540, 230)]
OIL = [(230, 191, 0), (392, 186, 1), (334, 216, 2)]  # under the drum, the crate, beside the dish plinth
LEAVES = [(44, 200), (41, 226), (590, 205), (594, 231), (104, 162), (520, 161), (275, 160)]


def slab_at(r, x, slabs):
    for s in slabs:
        if s[0] == r and s[1] <= x <= s[2]:
            return s
    return None


def blob(rng, cx, cy, n, x0, y0, x1, y1, dirs=((1, 0), (-1, 0), (0, 1), (0, -1), (1, 0), (-1, 0))):
    """A compact cluster grown cell by cell from a seed (a stain or patch shape, not scattered noise)."""
    cells, out = [(cx, cy)], {(cx, cy)}
    while len(out) < n and cells:
        x, y = rng.choice(cells)
        dx, dy = rng.choice(dirs)
        nx, ny = x + dx, y + dy
        if x0 <= nx <= x1 and y0 <= ny <= y1 and (nx, ny) not in out:
            out.add((nx, ny))
            cells.append((nx, ny))
    return out


def deck_layer(rng):
    L = Layer()
    slabs = []
    for r in range(len(ROW_EDGES) - 1):
        y0, y1 = ROW_EDGES[r], ROW_EDGES[r + 1] - 1
        h = y1 - y0 + 1
        base = h * 2.3
        x = -rng.randint(0, int(base))
        while x < W:
            w = max(14, int(base * rng.choice((0.65, 0.8, 1.0, 1.0, 1.15, 1.3, 1.6))))
            cx = x + w / 2
            f = math.sin(cx / 61.0 + r * 0.7) + 0.6 * math.sin(cx / 27.0 - r * 1.3) + rng.uniform(-0.5, 0.5)
            tone = "dk_a" if f > 0.8 else ("dk_b" if f > -0.4 else "dk_c")
            if any(((cx - tx) / rx) ** 2 + (((y0 + y1) / 2 - ty) / ry) ** 2 < 1.3 for tx, ty, rx, ry in TRAFFIC):
                tone = DK_UP[tone]  # boots polish whole slabs along the approaches
            slabs.append((r, x, x + w - 1, y0, y1, tone))
            x += w
    for r, x0, x1, y0, y1, tone in slabs:
        jog = rng.choice((0, 0, 0, 1, -1))  # the head joint steps by a pixel halfway down on some slabs
        mid = (y0 + y1) // 2
        L.rect(x0, y0, x1, y1, tone)
        L.hline(x0, x1, y1, "dk_seam")
        L.vline(x1, y0, mid, "dk_seam")
        L.vline(x1 + jog, mid, y1, "dk_seam")
        L.hline(x0, x1 - 1, y1 - 1, DK_DN[tone])  # front face of the slab, turned from the light
        lit_to = x0 + int((x1 - x0) * rng.uniform(0.35, 0.9))
        for x in range(x0, lit_to):  # lit back arris, broken where it is chipped
            if (x - x0) % 9 not in (5, 6):
                L.px(x, y0, DK_UP[tone])
        L.vline(x0, y0 + 1, y1 - 3, DK_UP[tone] if rng.random() < 0.7 else tone)
        for cx, cy in ((x0, y0), (x1 - 1, y1 - 1)):  # rounded / chipped corners
            if rng.random() < 0.6:
                L.px(cx, cy, "dk_seam")
        # a weathering patch inside the slab: darker where water stands, worn lighter where boots go
        if x1 - x0 > 10:
            n = int((x1 - x0) * (y1 - y0) * rng.uniform(0.12, 0.3))
            worn = tone in ("dk_worn", "dk_hi")
            for px, py in blob(rng, rng.randint(x0 + 3, x1 - 4), rng.randint(y0 + 2, y1 - 3), n, x0 + 1, y0 + 1, x1 - 2, y1 - 3):
                L.px(px, py, DK_UP[tone] if worn else DK_DN[tone])
    for r, xx in RAISED:  # proud slab: deeper front face and a cast shadow on the slab in front / to the east
        s = slab_at(r, xx, slabs)
        if s:
            _, x0, x1, y0, y1, tone = s
            L.hline(x0, x1 - 1, y1 - 2, DK_DN[tone])
            L.hline(x0, x1 - 1, y1 - 1, "dk_sh2")
            for x in range(x0 + 2, x1 + 3):
                c = name(L, x, y1 + 1)
                if c in DK_DN:
                    L.px(x, y1 + 1, DK_DN[c])
            for y in range(y0 + 2, y1 + 1):
                c = name(L, x1 + 1, y)
                if c in DK_DN:
                    L.px(x1 + 1, y, DK_DN[c])
    for r, xx in SUNKEN:  # settled slab: darker, shadowed under its back and west edges
        s = slab_at(r, xx, slabs)
        if s:
            _, x0, x1, y0, y1, tone = s
            for y in range(y0, y1 - 1):
                for x in range(x0, x1):
                    c = L.name_at(x, y)
                    if c in DK_DN and c != "dk_seam":
                        L.px(x, y, DK_DN[c])
            L.hline(x0, x1 - 1, y0, "dk_sh2")
            L.hline(x0, x1 - 1, y0 + 1, "dk_sh")
            L.vline(x0, y0, y1 - 2, "dk_sh2")
    for r, xx in BROKEN:  # broken slab: a crack across it, one piece settled darker
        s = slab_at(r, xx, slabs)
        if s:
            _, x0, x1, y0, y1, tone = s
            cxp = (x0 + x1) // 2 + rng.randint(-4, 4)
            y = y0
            x = cxp
            while y < y1:
                L.px(x, y, "dk_seam")
                for xr in range(x + 1, x1):
                    c = L.name_at(xr, y)
                    if c in DK_DN and c not in ("dk_seam", "dk_sh2"):
                        L.px(xr, y, DK_DN[c])
                y += 1
                x += rng.choice((0, 0, 1, -1))
    for r, xx in LOST:  # a lost corner: bedding soil, a grass tuft, a shaded break edge
        s = slab_at(r, xx, slabs)
        if s:
            _, x0, x1, y0, y1, tone = s
            stamp(L, x1 - 7, y1 - 5, ["....kk.", "..kssk.", ".ksssgk", "kssgsGs", "ssgGsss"],
                  {"k": "dk_seam", "s": "soil", "g": "moss", "G": "moss_hi"})
    for x, y in LICHEN:  # crustose lichen rosettes on slabs nobody walks on
        stamp(L, x, y, [".yY.", "yYyy", ".yy."], {"y": "lich_y_dk", "Y": "lich_y"}, only=set(DK_DN) - {"dk_seam"})
    for x, y, k in OIL:  # oil and grime where machinery stands
        for px, py in blob(random.Random(91 + k), x, y, 26 + 8 * k, x - 9, y - 3, x + 9, y + 3):
            c = name(L, px, py)
            if c in DK_DN:
                L.px(px, py, "stain" if (px + py) % 5 else "dk_sh2")
    # joint moss: in joints near the wall foot, the plinths and the piers, in short runs, never in the traffic ellipses
    ys, xs = np.nonzero(mask_of(L.a, ("dk_seam",)))
    for x, y in zip(xs, ys):
        if any(((x - tx) / rx) ** 2 + ((y - ty) / ry) ** 2 < 1.1 for tx, ty, rx, ry in TRAFFIC):
            continue
        near = y < 172 or x < 58 or x > 582 or any(abs(x - ax) < 40 and 184 < y < 216 for ax in A.ANTENNA_X)
        if near and (x * 7 + y * 3) % 11 < 4:
            L.px(x, y, "moss" if (x + y) % 3 else "moss_dk")
            if (x * 5 + y) % 13 == 0 and name(L, x, y - 1) in DK_DN:
                L.px(x, y - 1, "moss_hi")
    for x, y in LEAVES:
        stamp(L, x, y, [".l..", "lLd.", ".dl."], {"l": "leaf", "L": "wood_hi", "d": "leaf_dk"})
    # damp at the wall foot only below the water lines
    for d in DAMP_X:
        for px, py in blob(random.Random(d), d, 158, 40, d - 8, 156, d + 8, 164):
            c = name(L, px, py)
            if c in DK_DN:
                L.px(px, py, "dk_wet" if py < 162 else "dk_sh2")
    return L


# ----------------------------------------------------------------------------- 5 grating re-authored
WALK_Y0, WALK_Y1 = A.WALK_Y0, A.WALK_Y1
LANE_LINE = (255, 267)  # where boots actually go (the heroine's feet are at y 261)
GLINT_CLUSTERS = [(96, 258, 3), (201, 262, 2), (247, 256, 3), (391, 260, 2), (438, 264, 3), (566, 257, 2)]
CORNER_LITTER = [(33, 248), (176, 274), (270, 248), (352, 273), (498, 249), (603, 274)]


def walkway_pass(L):
    rng = random.Random(7070)
    gy0, gy1 = WALK_Y0 + 3, WALK_Y1 - 3
    px0 = 30
    for k, (pw, kind, rod, bright) in enumerate(A.PANELS):
        pxe = px0 + pw - 1
        pitch = 4 if kind != "old" else 5
        bar = "gr" if bright > -0.2 else "gr_mid"  # each panel has its own age: older panels are duller
        for y in range(gy0, gy1 + 1):
            ry = (y - gy0) % 3
            on_line = LANE_LINE[0] <= y <= LANE_LINE[1]
            for x in range(px0 + 1, pxe):
                cx = (x - px0) % pitch
                if kind == "plate":
                    row, shift = (y - gy0) % 4, ((y - gy0) // 4 % 2) * 3
                    lug = row == 0 and (x + shift) % 6 == 0
                    c = ("gr" if not on_line or (x + y) % 3 else "gr_mid") if lug else ("gr_dk" if row == 1 and (x + shift) % 6 == 0 else "gr_mid")
                    if on_line and not lug and (x * 3 + y) % 7 == 0:
                        c = "gr"  # lugs worn flat where boots go
                elif cx == 0:  # bearing bar top, polished in short runs on the walking line only
                    c = "gr_hi" if on_line and ry and ((x // pitch) * 7 + k * 3) % 5 < 2 else bar
                elif ry == 0:  # cross rod, set lower than the bearing bars
                    c = "gr_mid"
                elif cx == 1 and ry == 1:  # cell corner under bar and rod
                    c = "gr_deep" if bright > -0.2 else "gr_hole"
                else:  # open cell
                    c = "gr_dk" if bright > -0.2 else "gr_deep"
                L.px(x, y, c)
        if kind == "old":  # rust blooms around the old panel's cross rods
            for bx in range(px0 + 6, pxe - 4, 13):
                by = gy0 + 6 * rng.randint(1, 4)
                for x, y in blob(rng, bx, by, 9, px0 + 2, gy0 + 1, pxe - 2, gy1 - 1):
                    if L.name_at(x, y) in ("gr", "gr_mid"):
                        L.px(x, y, "dk_rust" if L.name_at(x, y) == "gr" else "rust")
        L.vline(px0, gy0, gy1, "gr_hole")
        L.vline(px0 + 1, gy0, gy1, "gr_dk")
        L.vline(pxe, gy0, gy1, "gr_mid")
        for ry in (gy0 + 1, gy1 - 1):
            L.px(px0 + 3, ry, "edge")
            L.px(pxe - 2, ry, "edge")
        px0 += pw
    for y in range(gy0, gy0 + 3):  # the first rows sit in the shadow of the trench lip
        for x in range(30, 610):
            n = L.name_at(x, y)
            L.px(x, y, {"gr_hi": "gr", "gr": "gr_mid", "gr_mid": "gr_dk", "gr_dk": "gr_deep", "plate": "gr", "edge": "steel"}.get(n, n))
    for x in range(30, 610):  # the last row before the nosing: dirt collects against it
        if name(L, x, gy1) in ("gr_mid", "gr_dk", "gr_deep", "gr"):
            L.px(x, gy1, "gr_deep" if (x // 7) % 3 else "soil")
    for gx, gy, n in GLINT_CLUSTERS:  # sun glints only on lit bar tops on the walking line
        for i in range(n):
            x = gx + 4 * i - (gx - 30) % 4
            for y in (gy, gy + 1):
                if L.name_at(x, y) in ("gr_hi", "gr", "plate"):
                    L.px(x, y, "gr_glint" if i == n // 2 and y == gy else "gr_hi")
    for x, y in CORNER_LITTER:  # leaves and grit caught in the panel corners
        stamp(L, x, y, ["ld.", "dls", ".s."], {"l": "leaf", "d": "leaf_dk", "s": "soil"})
    # nosing: brass dulled to a working finish, bright only in short worn runs where boots cross it
    for x in range(30, 610):
        if L.name_at(x, WALK_Y0 + 1) == "br_hi":
            L.px(x, WALK_Y0 + 1, "br")
        if L.name_at(x, WALK_Y0) == "gr_hi" and (x // 11) % 4 == 3:
            L.px(x, WALK_Y0, "gr")
    for cx in (A.ANTENNA_X[0], A.ANTENNA_X[1], A.ANTENNA_X[2], 52, 588):
        for x in range(cx - 5, cx + 6):
            if L.name_at(x, WALK_Y0 + 1) == "br" and x % 3:
                L.px(x, WALK_Y0 + 1, "br_hi")
    # trench covers: each lid has its own age (two older, darker lids; a newer one whose lip catches the light)
    joints = [x for x in range(A.TRENCH_X0 + 1, 601) if L.name_at(x, A.TRENCH_Y0 + 4) == "deep"]
    for i, (xa, xb) in enumerate(zip([A.TRENCH_X0] + joints, joints + [601])):
        kind = (i * 5) % 7
        for x in range(xa + 1, xb):
            for y in range(A.TRENCH_Y0 + 2, A.TRENCH_Y1 - 1):
                if L.name_at(x, y) == "steel":
                    if kind in (1, 4):
                        L.px(x, y, "slate")
                    elif kind == 3 and y == A.TRENCH_Y0 + 2:
                        L.px(x, y, "edge")
    # trench lid: grime in the cover joints, the lip shades the lane's first row
    for x in range(A.TRENCH_X0, 602):
        if L.name_at(x, A.TRENCH_Y1) == "deep" and (x // 5) % 4 == 0:
            L.px(x, A.TRENCH_Y1, "ink")
        if L.name_at(x, A.TRENCH_Y0 + 2) == "steel" and (x * 7) % 19 == 0:
            L.px(x, A.TRENCH_Y0 + 2, "slate")


# ----------------------------------------------------------------------------- 6 deck detail
def detail_pass(L):
    """Fewer, duller brass clamps on the floor conduits; rust blooms at the riser feet and anchor plates."""
    jx = [x + 8 for x in A.JUNCTION_X]
    for x, y0, y1 in [(jx[0], 157, 199), (jx[1], 157, 199), (jx[2], 157, 199), (186, 211, A.TRENCH_Y0), (343, 211, A.TRENCH_Y0),
                      (489, 211, A.TRENCH_Y0)]:
        for i, y in enumerate(range(y0 + 6, y1, 11)):
            if i % 2:
                for dx, c in ((-1, "edge"), (0, "steel"), (1, "deep")):
                    L.px(x + dx, y, c)
                    L.px(x + dx, y + 1, c)
                for dx in (-2, 2):
                    L.a[y:y + 2, x + dx, 3] = 0
            else:
                L.hline(x - 2, x + 2, y, "br")
                L.hline(x - 2, x + 2, y + 1, "br_dk")
    for x, y in [(186, A.TRENCH_Y0 - 1), (343, A.TRENCH_Y0 - 1), (489, A.TRENCH_Y0 - 1), (435, 208), (531, 208)]:
        stamp(L, x - 3, y - 1, [".r..r.", "rRrrRr"], {"r": "dk_rust", "R": "rust"}, only=None)


# ----------------------------------------------------------------------------- 8 doors and side walls
def piers_pass(L):
    """Re-course the west pier and the east maintenance block (stone pixels only)."""
    rng = random.Random(8080)
    for (x0, x1, y0, y1, tones) in [(1, 27, 95, 235, ("st_mid", "st_mid", "st_dk", "st")), (1, 27, 291, 317, ("st_mid", "st_dk")),
                                    (611, 639, 92, 225, ("st_dk", "st_dk", "st_mid", "st_deep")), (611, 639, 291, 317, ("st_dk", "st_deep"))]:
        T = Layer()
        courses, y = [], y0
        while y <= y1:
            h = rng.choice((9, 10, 11, 12, 10))
            courses.append(min(h, y1 - y + 1))
            y += h
        ashlar(T, rng, x0, x1, y0, courses, lambda b, tones=tones: rng.choice(tones), jumper_p=0.18, kinds=(0.45, 0.4, 0.15))
        m = np.zeros((H, W), bool)
        m[y0:y1 + 1, x0:x1 + 1] = True
        m &= mask_of(L.a, ("st_mid", "st_dk", "st", "st_deep"))
        copy_where(L, T, m)
    for x, y in ((8, 186), (20, 150), (616, 140), (630, 200)):  # biofilm runs on the piers
        streak(L, x, y, 14, 2)


# ----------------------------------------------------------------------------- 9 front parapet
def front_pass(L):
    rng = random.Random(9090)
    C = Layer()
    coping(C, rng, 0, W - 1, 292, 2, joints_min=22, joints_max=46, notch_p=0.0, sag_p=0.25, tones=("st", "st_mid", "st_mid", "st"), arris_p=0.35)
    m = np.zeros((H, W), bool)
    m[292:299] = True
    L.a[m] = C.a[m]
    T = Layer()
    ashlar(T, rng, 0, W - 1, 299, [7, 6, 6], lambda b: "st_dk" if b[5] == 0 else rng.choice(("st_mid", "st_dk", "st_dk")),
           jumper_p=0.1, kinds=(0.4, 0.45, 0.15))
    m = np.zeros((H, W), bool)
    m[299:318] = True
    copy_where(L, T, m)
    for x in range(0, W, 1):  # under the drip: a broken shadow line
        if name(L, x, 299) in STONE and (x // 6) % 4 != 1:
            L.px(x, 299, dn(L.name_at(x, 299)))
    for x in range(14, W, 37):
        streak(L, x + (x % 5), 300, 8 + x % 9)
    # railing: a working brass finish with short worn highlights, a shadow line on the coping behind the posts
    for x in range(38, 602):
        if L.name_at(x, 286) == "br_hi":
            L.px(x, 286, "br_hi" if (x // 5) % 9 == 0 or (x // 3) % 23 == 7 else "br")
    for x in range(44, 600, 40):
        L.px(x + 2, 288, "br_dk")
        L.px(x + 2, 289, "dk_seam")
        stamp(L, x - 1, 290, ["bbbb"], {"b": "br_dk"})
    for x in range(38, 602):
        if (x * 11) % 17 < 3 and name(L, x, 291) not in ("moss", "lf"):
            L.px(x, 291, "moss_dk")


# ----------------------------------------------------------------------------- 10-12 plinth weathering (colour only)
def plinth_pass(layers):
    """Chipped arrises, rust weeps under the brass bolts and moss at the foot; alpha is never touched."""
    for i, (x0, x1, top) in enumerate(V4.PLINTHS):
        L = layers[9 + i]
        before = L.a[..., 3].copy()
        for cx in (x0 + 5 + 7 * i, x1 - 9):
            stamp(L, cx, top, ["ddm", ".dl"], {"d": "st_deep", "m": "st_dk", "l": "st"}, only=STONE)
        for bx in ((x0 + 4, x1 - 6) if i != 2 else (x0 + 4, x1 - 5)):
            for k in range(4):
                if name(L, bx, top + 5 + k) in STONE and k != 2:
                    L.px(bx, top + 5 + k, "dk_rust" if k else "rust")
        for x in range(x0 + 1, x1):
            if (x * 5 + i) % 9 < 3 and name(L, x, A.BASE_Y - 2) in STONE:
                L.px(x, A.BASE_Y - 2, "moss_dk" if x % 2 else "moss")
        assert (L.a[..., 3] == before).all()


# ----------------------------------------------------------------------------- build
def build_scene():
    layers, _v4stats = V4.build_scene()
    sky, parapet, kit, _deck_v04, walk, detail, _shadow_v04, doors, front, a, b, c, fg = layers
    parapet_pass(parapet)
    kit_pass(kit, parapet)
    deck = deck_layer(random.Random(4040))
    walkway_pass(walk)
    detail_pass(detail)
    under = composite([sky, parapet, kit, deck, walk, detail])
    X = A.ANTENNA_X
    contact = [(X[0] - 37, A.BASE_Y, X[0] + 28, A.BASE_Y + 1), (X[1] - 28, A.BASE_Y, X[1] + 38, A.BASE_Y + 1),
               (X[2] - 33, A.BASE_Y, X[2] + 45, A.BASE_Y + 1), (224, 185, 258, 186), (380, 181, 413, 182),
               (38, 157, 597, 160), (38, 157, 45, 243), (590, 157, 597, 243),
               (45, 185, 100, 187), (290, 186, 363, 187)]  # v05: planter and dish trough also sit on the deck
    shadows = A.shadow_layer(under, [a, b, c], contact, (parapet, kit))
    V4.contact_pass(shadows, under)
    piers_pass(doors)
    front_pass(front)
    plinth_pass(layers)
    return [sky, parapet, kit, deck, walk, detail, shadows, doors, front, a, b, c, fg]


def write_gpl(path):
    lines = ["GIMP Palette", "Name: yonkers-antenna-room1-v05", "Columns: 8", "#"]
    for k, v in A.HEX.items():
        r, g, b_ = (int(v[i:i + 2], 16) for i in (1, 3, 5))
        lines.append(f"{r:3d} {g:3d} {b_:3d}\t{k}")
    data = ("\n".join(lines) + "\n").encode("utf-8")
    path.write_bytes(data)
    return data


def build():
    layers = build_scene()
    v04_layers, _ = V4.build_scene()
    arrs = [l.a for l in layers]
    for a_ in arrs:
        assert set(np.unique(a_[..., 3]).tolist()) <= {0, 255}, "binary alpha only"
    for i in range(9, 13):
        assert (arrs[i][..., 3] == v04_layers[i].a[..., 3]).all(), "antenna and foreground alpha equal v04: " + A.SCENE_LAYERS[i]
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
    stem = f"{PREFIX}_scene-quality-layers_unapproved-v05_{STAMP}"
    files = {"ora": (OUT / f"{stem}.ora", A.ora_bytes(stem, A.SCENE_LAYERS, imgs, flat_img)),
             "pxo": (OUT / f"{stem}.pxo", A.pxo_bytes("yonkers-room1-v05", A.SCENE_LAYERS, imgs, flat_img)),
             "png": (OUT / f"{PREFIX}_scene-quality-native-640x360-flat_unapproved-v05_{STAMP}.png", A.png_bytes(flat_img))}
    for p, data in files.values():
        p.write_bytes(data)
    gpl_p = OUT / f"{PREFIX}_native-palette_unapproved-v05_{STAMP}.gpl"
    gpl = write_gpl(gpl_p)
    plate_p = EXPORTS / f"{PREFIX}_corridor-plate-scene-quality_unapproved-v05_{STAMP}.png"
    fg_p = EXPORTS / f"{PREFIX}_foreground-occluder_unapproved-v05_{STAMP}.png"
    plate_b, fg_b = A.png_bytes(A.to_img(plate)), A.png_bytes(A.to_img(arrs[12]))
    plate_p.write_bytes(plate_b)
    fg_p.write_bytes(fg_b)
    antennas = []
    for i, slug in enumerate(A.ANTENNA_SLUGS):
        x0, y0, x1, y1 = A.sprite_box(i)
        crop = A.png_bytes(A.to_img(np.ascontiguousarray(arrs[9 + i][y0:y1, x0:x1])))
        p = EXPORTS / f"{PREFIX}_{slug}_unapproved-v05_{STAMP}.png"
        p.write_bytes(crop)
        antennas.append({"layer": A.ANTENNA_LAYERS[i], "clue": f"scifi.outskirts:{i}", "reads_as": A.ANTENNA_READS[i],
                         "crop_from_layer_xywh": [x0, y0, A.SPRITE_W, A.SPRITE_H], "anchor": [A.ANTENNA_X[i], A.BASE_Y],
                         "runtime_png": {"file": A.rel(p), "sha256": A.sha(crop), "hash_algorithm": "sha256-bytes"}})
    v04_flat = composite(v04_layers)
    manifest = {
        "project": "Worlds Between (rpg-2-star-ocean-the-second)",
        "scene": "Yonkers outskirts survey annex room 1 (天线走廊 / Antenna Walkway), scifi.outskirts room 1",
        "version": "v05 scene-quality refinement over v04 (523bba3b): coping stones, irregular ashlar, wall-fitting occlusion, "
                   "re-laid flagstones with contact shadows and localized stains, grating cells with walking-line polish and "
                   "clustered glints, duller brass, re-coursed piers; geometry, antennas (alpha) and foreground equal v04",
        "status": "UNAPPROVED, NONRUNTIME. Not wired into the game: survey_annex.gd still loads v03, so v05 is off by default. "
                  "Scenes stay 3/12. No accepted flag, counter, ledger, Bible or Git index change.",
        "geography_note": "Fictional 2537 rooftop survey walkway in the Yonkers vicinity; generic Hudson-valley masonry and "
                          "utility hardware, not a reconstruction of any specific Yonkers landmark.",
        "base": {"author": A.rel(V04_AUTHOR), "v03_author": A.rel(V4.V03_AUTHOR),
                 "manifest": "outputs/yonkers-room1-v04_523bba3b/rpg-2-star-ocean-the-second_yonkers-antenna-room1_material-depth-scene-manifest_unapproved-v04_20261018-052445-523bba3b.json"},
        "pixels_changed_vs_v04_flat": int((flat != v04_flat).any(axis=2).sum()),
        "pixels_changed_vs_v04_per_layer": {n: int((arrs[i] != v04_layers[i].a).any(axis=2).sum()) for i, n in enumerate(A.SCENE_LAYERS)},
        "authorship": "Native pixel art: hand-authored shapes, stamps and coordinate lists in this tool over the v04/v03 layers, by "
                      "Claude (Claude Code). No generated, traced, resampled or palette-reduced image; declared palette only; binary alpha.",
        "canvas": [W, H], "palette_size": len(A.HEX), "palette": A.HEX, "palette_additions_vs_v03": EXTRA_HEX,
        "native_palette_file": {"file": A.rel(gpl_p), "sha256": A.sha(gpl), "hash_algorithm": "sha256-bytes"},
        "layers_bottom_to_top": A.SCENE_LAYERS,
        "editable_sources": {k: {"file": A.rel(p), "sha256": A.sha(d), "hash_algorithm": "sha256-bytes"} for k, (p, d) in files.items()},
        "runtime_exports": {
            "note": "nonruntime exports in the v05 output folder only; nothing under game/ is written",
            "plate": {"from_layers": A.PLATE_LAYERS, "file": A.rel(plate_p), "sha256": A.sha(plate_b), "hash_algorithm": "sha256-bytes"},
            "antennas": antennas,
            "foreground": {"from_layers": ["foreground-occluder"], "file": A.rel(fg_p), "sha256": A.sha(fg_b), "hash_algorithm": "sha256-bytes"},
        },
        "source_tool": A.rel(Path(__file__)),
    }
    path = OUT / f"{PREFIX}_scene-quality-manifest_unapproved-v05_{STAMP}.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(path)
    print("changed vs v04", manifest["pixels_changed_vs_v04_flat"], manifest["pixels_changed_vs_v04_per_layer"])
    return manifest


if __name__ == "__main__":
    build()
