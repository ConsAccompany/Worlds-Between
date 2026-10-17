"""Chicago Loop arrival block, State St x Lake St, native 640x360 scene (UNAPPROVED candidate v03r1).

v03r1 is ONE bounded visual correction of v03 (this file started as a copy of the v03 author tool
tools/...pixel-author_unapproved-v03_20261017-174431-c223d3f7.py; v03 files stay untouched). Codex
found v03 too dark and flat on the plaza, with a busy upper building strip. Changes, all marked
"v03r1" below; geometry, props, pivots, walk mask and reveal mask are unchanged:
  * a warm sunlit paving ramp (ps0..ps3) that only the authored ground uses (never the underpainting);
  * slab tones lifted one step and sunlit slabs set as running clusters of warm slabs;
  * a lighter L cast shadow (-2 instead of -3) with warm sun in the tie slits, wider warm streaks;
  * under-deck concrete one step lighter, with larger storefront light pools;
  * upper facade strip: small near-black components merged into their surroundings and the cold iron
    blacks warmed to stone shadow, inside the same underpainted rows (share unchanged).

The text below describes the v03 base that v03r1 corrects.

v03 is one bounded composition pass after v02 (v02 files stay untouched as the runtime baseline).
Codex found v02's elevated L recognizable but the lower plaza too empty and the stone/foliage/teal
density too sparse next to the existing science city. v03 splits the work by material:

  * Underpainting (disclosed): only the backdrop bands come from the nonruntime style reference
    outputs/...chicago-state-lake_style-alignment-reference_nonruntime-v01_20261017-173900-4c6e2b91.png
    (hash pinned): the lit facade north of the L, the riveted deck girder and the storefront glass
    under the deck. They are area-averaged to 640x360 in numpy, row-recomposed for gameplay, mapped
    to the curated material palette below (no dither, no median cut) and cleaned into clusters
    (isolated pixels folded, components of 1-3 px merged into their surroundings).
  * Authored natively here, cluster by cluster with a fixed integer hash (no RNG streams): the whole
    walkable ground (granite slab plaza, under-deck concrete, Loop medallion with the five line
    colours and the Chicago star, sett bands, teal guide strip, tree and drain grates), State St
    with its continental crosswalk, curb ramps and tactile pads, the L cast shadow, the riveted L
    columns, knee braces and plinths, the station stair up to the platform, and every prop:
    Chicago lamp with flag banner and green street blade, planters, bench, litter bin, teal civic
    kiosk, wayfinding pylon, bike-share dock, bollards, granite seats, honey locusts, fountain,
    iron fence and foreground planting.
The image is split into purposeful editable layers (Pixelorama .pxo + OpenRaster .ora, same layers,
hidden locked walk-mask guide). Runtime gets the flattened static layers as one opaque PNG plus the
y-sort layer PNGs (binary alpha); each y-sort prop is a region of its layer with its own pivot row.
Geometry constants must match the v03 runtime scene script (checked in Godot and by the source check).
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import io
import json
import sys
import zipfile
import xml.etree.ElementTree as ET

import numpy as np
import PIL
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261017-183235-a00fabf3"
PREFIX = "rpg-2-star-ocean-the-second_chicago-loop_state-lake"
VARIANT = "unapproved-v03r1"
OUT = ROOT / "outputs" / "chicago-loop-state-lake-v03r1"
RUNTIME = ROOT / "game" / "assets" / "environments" / "chicago-loop-state-lake-v03r1"
BASE_AUTHOR = ROOT / "tools" / "rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-author_unapproved-v03_20261017-174431-c223d3f7.py"
REFERENCE = ROOT / "outputs" / "rpg-2-star-ocean-the-second_chicago-state-lake_style-alignment-reference_nonruntime-v01_20261017-173900-4c6e2b91.png"
REFERENCE_SHA256 = "7608a64f906bb93b326905b47cf51ed8e9645fe244541b393ffe4340d360fe5b"
W, H = 640, 360
PIXELORAMA_VERSION = "v1.2.3-stable"

# ---------------------------------------------------------------- curated material palette
# Every pixel of every layer uses one of these colours (the .gpl lists exactly the ones used).
PAL = {
    # night-blue UI field under the opaque header
    "ui": (13, 23, 35),
    # limestone facade (warm)
    "st0": (36, 31, 30), "st1": (58, 50, 46), "st2": (84, 74, 66), "st3": (114, 100, 87),
    "st4": (146, 129, 109), "st5": (178, 158, 128), "st6": (210, 190, 154),
    # granite paving (slightly cooler)
    "pv0": (47, 42, 41), "pv1": (66, 59, 55), "pv2": (88, 79, 71), "pv3": (112, 100, 88),
    "pv4": (136, 121, 104), "pv5": (160, 143, 121), "pv6": (184, 165, 139), "pv7": (208, 189, 160),
    # v03r1: the same granite in low warm sun (ps_k sits at the value of pv_(k+4), warmer; authored ground only)
    "ps0": (148, 127, 100), "ps1": (174, 149, 114), "ps2": (200, 172, 134), "ps3": (226, 200, 160),
    # asphalt
    "as0": (27, 29, 33), "as1": (39, 41, 46), "as2": (53, 55, 60), "as3": (69, 71, 75),
    # road paint
    "wp0": (150, 147, 136), "wp1": (196, 192, 177), "wp2": (226, 222, 205),
    # L iron (near-black green-grey) and rust/bronze
    "ir0": (10, 12, 12), "ir1": (22, 25, 25), "ir2": (35, 39, 38), "ir3": (52, 57, 54), "ir4": (78, 84, 77),
    # painted L structure steel (warm, weathered): separates the elevated from cold-black street iron
    "iw0": (24, 20, 18), "iw1": (40, 32, 27), "iw2": (58, 45, 36), "iw3": (84, 63, 46), "iw4": (116, 87, 60),
    "ru0": (52, 30, 17), "ru1": (86, 50, 25), "ru2": (122, 76, 35), "ru3": (160, 108, 50),
    # warm light (lamps, lit windows)
    "lt0": (150, 92, 34), "lt1": (200, 136, 58), "lt2": (236, 184, 98), "lt3": (252, 226, 160), "lt4": (255, 248, 222),
    # foliage
    "fo0": (13, 24, 16), "fo1": (22, 42, 25), "fo2": (34, 64, 32), "fo3": (54, 92, 38),
    "fo4": (88, 122, 44), "fo5": (138, 158, 58), "fo6": (190, 194, 88),
    # flowers
    "fl_w": (228, 222, 208), "fl_p": (210, 128, 148), "fl_r": (186, 62, 54), "fl_y": (232, 196, 80),
    # teal civic technology and water
    "te0": (8, 36, 40), "te1": (14, 66, 70), "te2": (26, 112, 112), "te3": (58, 176, 166),
    "te4": (138, 230, 214), "te5": (214, 255, 244),
    # granite lit by teal civic screens (glow pools on the paving)
    "tl0": (80, 118, 114), "tl1": (118, 162, 152),
    # brick / tactile pads
    "br0": (78, 34, 26), "br1": (116, 54, 38), "br2": (150, 80, 54),
    # awning green
    "aw0": (16, 46, 40), "aw1": (28, 72, 60), "aw2": (48, 104, 84),
    # bench wood
    "wd0": (96, 60, 35), "wd1": (134, 88, 50), "wd2": (166, 116, 66), "wd3": (194, 140, 82),
    # Loop line colours and the Chicago flag
    "loop_brown": (98, 54, 27), "loop_green": (0, 155, 58), "loop_orange": (249, 70, 28),
    "loop_pink": (226, 126, 166), "loop_purple": (82, 35, 152),
    "flag_white": (233, 238, 240), "flag_blue": (143, 208, 240), "flag_red": (216, 30, 44),
}
NAMES = list(PAL)
RGB = np.array([PAL[n] for n in NAMES], np.int32)
IDX = {n: i for i, n in enumerate(NAMES)}

# Colours the underpainting may map to (backdrop materials only; never Loop/flag/UI accents).
UNDERPAINT_SET = [n for n in NAMES if n[:2] in ("st", "pv", "as", "ir", "ru", "lt", "fo", "aw") and n != "lt4"]
ACCENTS = {"lt2", "lt3", "lt4", "te3", "te4", "te5", "fl_w", "fl_p", "fl_r", "fl_y"}

# ---------------------------------------------------------------- gameplay geometry (shared with the scene script)
WALK = (8, 178, 624, 120)          # rows 178..297
WALK_TOP = WALK[1]
DECK_TOP, DECK_BOTTOM = 95, 134    # the girder; a 44 px hero at the walk top keeps her head below it
SPAWN = (320, 286)
# (x, y, w, h); right/bottom edge exclusive.
BENCH = (258, 181, 42, 6)
KIOSK_BOX = (419, 189, 26, 12)
BIN = (397, 182, 14, 9)            # litter bin on the legacy (410,190) solid pin
BLOCKS = [
    BENCH, KIOSK_BOX, BIN,
    (83, 178, 11, 5),              # Chicago lamp base (State St curb)
    (214, 178, 40, 8),             # stone planter under the deck
    (304, 178, 14, 7),             # iron planter
    (364, 178, 22, 7),             # stone planter
    (498, 180, 26, 8),             # conifer planter by the stair
    (126, 250, 28, 14), (460, 250, 28, 14),   # L column plinths
    (100, 251, 22, 11), (488, 251, 22, 11),   # planters beside the plinths
    (236, 228, 8, 5),              # wayfinding pylon
    (232, 258, 28, 8), (372, 258, 28, 8),     # granite seats by the medallion
    (191, 285, 15, 9), (425, 285, 15, 9),     # honey locust grates
    (324, 288, 80, 10),            # bike-share dock
    (89, 212, 3, 2), (89, 224, 3, 2), (89, 252, 3, 2), (89, 264, 3, 2),   # bollards at the curb ramp
    (540, 178, 68, 29),            # station stair, newel posts
    (608, 178, 32, 86),            # east terrace wall and planters
    (566, 264, 74, 34),            # fountain basin
]
KIOSK = (432, 214)                 # interaction points just south of each site
STAIR = (574, 214)
PYLON = (240, 240)
INTERACT_RADIUS = 26


def walkable(x, y):
    def inside(r):
        return r[0] <= x < r[0] + r[2] and r[1] <= y < r[1] + r[3]
    return inside(WALK) and not any(inside(b) for b in BLOCKS)


# ---------------------------------------------------------------- tiny deterministic helpers
def hsh(x, y, s=0):
    """Integer hash in [0, 1): version-independent replacement for any random stream."""
    v = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xFFFFFFFF
    v = ((v ^ (v >> 13)) * 1274126177) & 0xFFFFFFFF
    v ^= v >> 16
    return (v & 0xFFFFFF) / float(1 << 24)


class Layer:
    """RGBA layer painted with palette names."""

    def __init__(self):
        self.a = np.zeros((H, W, 4), np.uint8)

    def px(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.a[y, x, :3] = PAL[c]
            self.a[y, x, 3] = 255

    def rect(self, x0, y0, x1, y1, c):
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        if x1 > x0 and y1 > y0:
            self.a[y0:y1, x0:x1, :3] = PAL[c]
            self.a[y0:y1, x0:x1, 3] = 255

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y + 1, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x + 1, y1, c)

    def mask(self, m, c):
        self.a[m, :3] = PAL[c]
        self.a[m, 3] = 255

    def get(self, x, y):
        return tuple(int(v) for v in self.a[y, x, :3])

    def opaque(self):
        return self.a[..., 3] == 255


def name_of(rgb):
    for n, c in PAL.items():
        if c == tuple(rgb):
            return n
    raise KeyError(rgb)


RAMPS = {k: [n for n in NAMES if n.startswith(k) and n[len(k):].isdigit()] for k in ("st", "pv", "as", "ir", "iw", "ru", "lt", "fo", "te", "br", "aw", "wd", "wp")}


def shift(n, d):
    """Move a palette colour d steps along its material ramp (clamped)."""
    if n[:2] == "ps" and n[2:].isdigit():
        # v03r1: sunlit granite brightens within the sun ramp; shadow takes it back to plain granite.
        k = int(n[2:])
        return "ps%d" % min(3, k + d) if d >= 0 else "pv%d" % max(0, k + 4 + d)
    for ramp in RAMPS.values():
        if n in ramp:
            return ramp[max(0, min(len(ramp) - 1, ramp.index(n) + d))]
    return n


def ellipse(cx, cy, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - cy) / ry) ** 2 <= 1.0


def poly(points):
    img = Image.new("L", (W, H), 0)
    ImageDraw.Draw(img).polygon(points, fill=255)
    return np.array(img) > 0


def rmask(x0, y0, x1, y1):
    m = np.zeros((H, W), bool)
    m[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True
    return m


# ---------------------------------------------------------------- underpainting (backdrop bands only)
def area_downscale(img):
    """Exact area average to W x H (numpy, independent of Pillow's resampler)."""
    a = np.asarray(img, np.float64)
    sh, sw = a.shape[:2]

    def weights(n_out, n_in):
        m = np.zeros((n_out, n_in))
        s = n_in / n_out
        for i in range(n_out):
            lo, hi = i * s, (i + 1) * s
            for j in range(int(np.floor(lo)), min(n_in, int(np.ceil(hi)))):
                m[i, j] = (min(hi, j + 1) - max(lo, j)) / s
        return m

    wy, wx = weights(H, sh), weights(W, sw)
    out = np.tensordot(np.tensordot(wy, a, axes=(1, 0)), wx, axes=(1, 1)).transpose(0, 2, 1)
    return np.floor(out + 0.5).clip(0, 255).astype(np.uint8)


DECK_DROP = (69, 70, 71, 72, 73)   # repeated tie rows removed so the 45-row reference deck fits rows 95..134


def row_map():
    """Native row -> reference row (reference area-averaged to 640x360)."""
    deck = [r for r in range(64, 109) if r not in DECK_DROP]
    rows = [max(0, y - 31) for y in range(DECK_TOP)] + deck + [y - 27 for y in range(DECK_BOTTOM + 1, H)]
    assert len(rows) == H and len(deck) == DECK_BOTTOM - DECK_TOP + 1
    return rows


def nearest_palette(rgb, names):
    pal = np.array([PAL[n] for n in names], np.int32)
    flat = rgb.reshape(-1, 3).astype(np.int32)
    wts = np.array([3, 4, 2], np.int32)
    best = np.zeros(len(flat), np.int64)
    best_d = np.full(len(flat), 1 << 60, np.int64)
    for i, c in enumerate(pal):
        d = (((flat - c) ** 2) * wts).sum(axis=1)
        m = d < best_d
        best[m] = i
        best_d[m] = d[m]
    return np.array([IDX[n] for n in names])[best].reshape(rgb.shape[:2])


def components(idx):
    """4-connected components of equal palette index: label array (min flat index per component)."""
    h, w = idx.shape
    lab = np.arange(h * w).reshape(h, w)
    while True:
        prev = lab
        for _ in range(8):
            p = np.pad(lab, 1, constant_values=h * w)
            q = np.pad(idx, 1, constant_values=-1)
            for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nb = p[1 + dy:h + 1 + dy, 1 + dx:w + 1 + dx]
                same = q[1 + dy:h + 1 + dy, 1 + dx:w + 1 + dx] == idx
                lab = np.where(same & (nb < lab), nb, lab)
            lab = lab.ravel()[lab.ravel()].reshape(h, w)   # pointer jumping
        if np.array_equal(lab, prev):
            return lab


def cluster_clean(idx, max_size=3, passes=3):
    """Merge every equal-colour component of <= max_size px (except accent lights and flowers) into the
    most frequent different colour on its 4-neighbour border: generator grain becomes clusters."""
    accent = np.array([IDX[n] for n in ACCENTS])
    h, w = idx.shape
    for _ in range(passes):
        lab = components(idx)
        sizes = np.bincount(lab.ravel(), minlength=h * w)
        small = (sizes[lab] <= max_size) & ~np.isin(idx, accent)
        if not small.any():
            break
        # Sequential (raster order) so two-colour checker dithers collapse instead of inverting.
        out = idx.copy()
        ys, xs = np.nonzero(small)
        for y, x in zip(ys, xs):
            cand = [int(out[y + dy, x + dx]) for dy, dx in ((0, -1), (0, 1), (-1, 0), (1, 0))
                    if 0 <= y + dy < h and 0 <= x + dx < w and out[y + dy, x + dx] != out[y, x]]
            if cand:
                out[y, x] = max(sorted(set(cand)), key=cand.count)
        idx = out
    return idx


def underpainting():
    data = REFERENCE.read_bytes()
    if hashlib.sha256(data).hexdigest() != REFERENCE_SHA256:
        raise SystemExit("reference image hash changed: " + str(REFERENCE))
    ref = area_downscale(Image.open(io.BytesIO(data)).convert("RGB"))
    u = ref[row_map()].copy()
    idx = nearest_palette(u, UNDERPAINT_SET)
    idx[62:170] = cluster_clean(idx[62:170])
    idx[62:DECK_TOP] = tame_facade_blacks(idx[62:DECK_TOP])
    return idx


# v03r1: the upper facade strip read as black speckle. Near-black components up to this size are
# folded into their surroundings; the cold iron blacks left (window recesses, doorways) become warm
# stone shadow (st0/st1), so the strip keeps its depth without cold pits. Same rows, same underpainted pixels.
FACADE_BLACKS = ("ir0", "ir1", "as0", "iw0", "st0", "fo0")
FACADE_BLACK_MAX = 14
FACADE_WARM = {"ir0": "st0", "ir1": "st1", "as0": "st0", "iw0": "st0", "ir2": "st1", "as1": "st1"}


def tame_facade_blacks(idx):
    h, w = idx.shape
    for _ in range(3):
        dark = np.isin(idx, [IDX[n] for n in FACADE_BLACKS])
        lab = components(np.where(dark, -2, idx))
        sizes = np.bincount(lab.ravel(), minlength=h * w)
        small = dark & (sizes[lab] <= FACADE_BLACK_MAX)
        if not small.any():
            break
        out = idx.copy()
        # Grow inward from the border: each pass fills dark pixels that touch a non-dark neighbour.
        todo = small.copy()
        while todo.any():
            filled = False
            for y, x in zip(*np.nonzero(todo)):
                cand = [int(out[y + dy, x + dx]) for dy, dx in ((0, -1), (0, 1), (-1, 0), (1, 0))
                        if 0 <= y + dy < h and 0 <= x + dx < w and not todo[y + dy, x + dx]
                        and not np.isin(out[y + dy, x + dx], [IDX[n] for n in FACADE_BLACKS])]
                if cand:
                    out[y, x] = max(sorted(set(cand)), key=cand.count)
                    todo[y, x] = False
                    filled = True
            if not filled:
                break
        idx = out
    for a, b in FACADE_WARM.items():
        idx = np.where(idx == IDX[a], IDX[b], idx)
    return idx


# ---------------------------------------------------------------- authored ground
CURB_X = 78                 # State St curb face columns 78-79, curb top 80-82, sidewalk from 83
XWALK = (206, 276)          # continental crosswalk rows across State St
RAMP = (210, 272)           # flush curb ramp rows
PLAZA_TOP = 206             # under-deck concrete above, granite slab plaza below
MEDALLION = (316, 254, 50, 17)


def paint_road(g):
    for y in range(DECK_BOTTOM + 1, H):
        for x in range(0, CURB_X):
            h = hsh(x // 2, y // 2, 11)
            g.px(x, y, "as1" if h < 0.78 else ("as2" if h < 0.95 else "as0"))
    # aggregate clusters (2x1 / 2x2), never single pixels
    for i in range(140):
        x, y = int(hsh(i, 1, 12) * (CURB_X - 3)), DECK_BOTTOM + 2 + int(hsh(i, 2, 12) * (H - DECK_BOTTOM - 4))
        c = "as3" if hsh(i, 3, 12) < 0.5 else "as0"
        g.rect(x, y, x + 2, y + (2 if hsh(i, 4, 12) < 0.5 else 1), c)
    # worn lane line (dashed) toward the far side
    for y in range(DECK_BOTTOM + 1, H):
        if (y // 9) % 2 == 0 and not (XWALK[0] - 6 <= y < XWALK[1] + 6):
            g.rect(14, y, 16, y + 1, "wp0")
    # stop bars and continental crosswalk (bars run with traffic, pedestrians cross east-west)
    g.rect(0, XWALK[0] - 5, CURB_X, XWALK[0] - 3, "wp1")
    g.rect(0, XWALK[1] + 3, CURB_X, XWALK[1] + 5, "wp1")
    for bx in range(3, CURB_X - 4, 13):
        g.rect(bx, XWALK[0], bx + 7, XWALK[1], "wp2")
        g.rect(bx + 6, XWALK[0], bx + 7, XWALK[1], "wp1")
        for j in range(5):   # worn patches where tyres run
            yy = XWALK[0] + 4 + int(hsh(bx, j, 13) * (XWALK[1] - XWALK[0] - 8))
            xo = bx + 1 + int(hsh(bx, j, 14) * 4)
            g.rect(xo, yy, xo + 2, yy + 2, "wp0")
    # manhole cover (rings and a hatched lid)
    m = ellipse(40, 300, 9, 5)
    inner = ellipse(40, 300, 6.5, 3.2)
    g.mask(m, "ir2")
    g.mask(m & ~ellipse(40, 300, 7.5, 3.8), "ir1")
    for y, x in zip(*np.nonzero(inner)):
        if (x + y) % 3 == 0:
            g.px(x, y, "ir3")
    # curb
    for y in range(DECK_BOTTOM + 1, H):
        flush = RAMP[0] <= y < RAMP[1]
        g.px(CURB_X, y, "pv2" if flush else "as0")
        g.px(CURB_X + 1, y, "pv3" if flush else "ir2")
        for x in (CURB_X + 2, CURB_X + 3, CURB_X + 4):
            g.px(x, y, "pv4" if flush else ("pv6" if x == CURB_X + 2 else "pv5"))
    # tactile warning pad at the foot of the ramp: truncated domes in 2x2 clusters
    g.rect(CURB_X + 2, RAMP[0] + 4, CURB_X + 9, RAMP[1] - 4, "br1")
    for y in range(RAMP[0] + 5, RAMP[1] - 5, 3):
        for x in range(CURB_X + 3, CURB_X + 9, 3):
            g.px(x, y, "br2")
            g.px(x, y + 1, "br0")


def paint_underdeck_walk(g):
    """Concrete sidewalk panels under the deck (rows 170..PLAZA_TOP): darker under the structure; the
    storefront light pools are added by the shading layer."""
    for y in range(170, PLAZA_TOP):
        for x in range(CURB_X + 5, W):
            px_, py_ = (x - CURB_X - 5) % 20, (y - 170) % 9
            tone = "pv4" if hsh((x - CURB_X - 5) // 20, (y - 170) // 9, 21) < 0.6 else "pv5"   # v03r1: one step lighter
            c = "pv1" if py_ == 8 else ("pv2" if px_ == 19 else tone)
            if py_ == 0 and px_ != 19:
                c = shift(tone, 1)
            g.px(x, y, c)
    # storefront base course: dark granite plinth under the glass
    g.rect(CURB_X + 5, 166, W, 168, "st2")
    g.rect(CURB_X + 5, 168, W, 170, "st1")
    for x in range(CURB_X + 5, W, 18):
        g.vline(x, 166, 170, "st0")


def slab_tone(cx, cy):
    """v03r1: one step lighter overall, and sunlit slabs come in running clusters (about 3 x 2 slabs)
    of warm granite, each slab one of three sun values, so the open plaza reads as patchy low sun."""
    h = hsh(cx, cy, 31)
    if hsh(cx // 3, cy // 2, 39) < SUN_CLUSTER_SHARE and h >= 0.12:
        return "ps0" if h < 0.35 else ("ps1" if h < 0.85 else "ps2")
    return "pv3" if h < 0.15 else ("pv4" if h < 0.6 else "pv5")


SUN_CLUSTER_SHARE = 0.4


SLAB_W, SLAB_H = 32, 16


def paint_plaza(g):
    """Large-format granite slabs 32x16 in running bond: one tone per slab, a lit top edge, dark bed
    joint, and at most one deliberate wear or fleck cluster; a sett band and teal guide strip edge it."""
    for y in range(PLAZA_TOP, H):
        ry = y - PLAZA_TOP
        row = ry // SLAB_H
        off = SLAB_W // 2 if row % 2 else 0
        for x in range(CURB_X + 5, W):
            col = (x + off) // SLAB_W
            lx, ly = (x + off) % SLAB_W, ry % SLAB_H
            tone = slab_tone(col, row)
            if ly == SLAB_H - 1:
                c = "pv1"
            elif lx == SLAB_W - 1:
                c = "pv2" if tone != "pv2" else "pv1"
            elif ly == 0:
                c = shift(tone, 1)
            else:
                c = tone
            g.px(x, y, c)
    for row in range((H - PLAZA_TOP) // SLAB_H + 1):
        off = SLAB_W // 2 if row % 2 else 0
        for col in range(W // SLAB_W + 2):
            h = hsh(col, row, 33)
            x0 = col * SLAB_W - off + 3 + int(hsh(col, row, 34) * 20)
            y0 = PLAZA_TOP + row * SLAB_H + 3 + int(hsh(col, row, 35) * 8)
            base = slab_tone(col, row)
            if h < 0.45:      # fleck cluster: 3-5 px, one ramp step off
                c = shift(base, -1 if h < 0.3 else 1)
                w_ = 2 + int(hsh(col, row, 36) * 3)
                g.rect(max(x0, CURB_X + 5), y0, x0 + w_, y0 + 1, c)
                g.rect(max(x0 + 1, CURB_X + 5), y0 + 1, x0 + w_ - 1, y0 + 2, c)
            elif h < 0.55:    # hairline crack: short stepped run
                for k in range(6):
                    g.px(x0 + k, y0 + k // 2, shift(base, -1))
    # sett ribbons: a cross band south of the medallion and the two tree lines
    for x0, y0, x1, y1 in ((CURB_X + 5, 276, 560, 280), (195, 248, 202, 298), (429, 248, 436, 298)):
        for y in range(y0, y1):
            for x in range(x0, x1):
                k = (x + (y // 2) * 3) % 6
                g.px(x, y, "pv1" if k == 5 or y % 2 == 1 and x % 6 == 2 else ("pv3" if hsh((x + (y // 2) * 3) // 6, y // 2, 38) < 0.5 else "pv2"))
    # sett band between the under-deck walk and the plaza, with the teal guide strip
    for y in range(PLAZA_TOP, PLAZA_TOP + 4):
        for x in range(CURB_X + 5, 540):
            joint = (x + ((y - PLAZA_TOP) // 2) * 3) % 6 == 5 or (y - PLAZA_TOP) % 2 == 1 and x % 6 == 5
            g.px(x, y, "pv1" if joint else ("pv3" if hsh((x + ((y - PLAZA_TOP) // 2) * 3) // 6, y // 2, 37) < 0.5 else "pv2"))
    for x in range(96, 532):
        if (x - 96) % 24 < 18:
            g.px(x, PLAZA_TOP + 4, "te3" if (x - 96) % 24 in (2, 8, 14) else "te2")
        g.px(x, PLAZA_TOP + 5, "pv1")


def paint_medallion(g):
    cx, cy, rx, ry = MEDALLION
    yy, xx = np.mgrid[0:H, 0:W]
    outer = ellipse(cx, cy, rx, ry)
    setts = outer & ~ellipse(cx, cy, rx - 4, ry - 2)
    for y, x in zip(*np.nonzero(setts)):
        g.px(x, y, "pv3" if (x // 4 + y // 2) % 2 else "pv1")
    bronze = ellipse(cx, cy, rx - 4, ry - 2) & ~ellipse(cx, cy, rx - 6, ry - 3)
    g.mask(bronze & (yy >= cy), "ru2")
    g.mask(bronze & (yy < cy), "ru3")
    g.mask(ellipse(cx, cy, rx - 6, ry - 3), "pv6")
    # the five Loop lines as concentric rings, broken at the south where the station sits
    ang = np.arctan2((yy + 0.5 - cy) * rx / ry, xx + 0.5 - cx)
    for i, c in enumerate(["loop_brown", "loop_green", "loop_orange", "loop_pink", "loop_purple"]):
        k = rx - 9 - i * 4
        ring = ellipse(cx, cy, k, k * ry / rx) & ~ellipse(cx, cy, k - 1.4, (k - 1.4) * ry / rx)
        g.mask(ring & ~((ang > 1.2) & (ang < 1.95)), c)
    g.mask(ellipse(cx, cy, 15, 5.4), "pv7")
    # six-pointed Chicago star (red) at the centre, flag-blue bars either side
    star = [(0, -4), (0, -3), (-1, -2), (0, -2), (1, -2), (-4, -2), (-3, -2), (3, -2), (4, -2), (-3, -1), (-2, -1), (-1, -1),
            (0, -1), (1, -1), (2, -1), (3, -1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (-3, 1), (-2, 1), (-1, 1), (0, 1),
            (1, 1), (2, 1), (3, 1), (-4, 2), (-3, 2), (3, 2), (4, 2), (-1, 2), (0, 2), (1, 2), (0, 3), (0, 4)]
    for dx, dy in star:
        g.px(cx + dx, cy + dy, "flag_red")
    g.rect(cx - 14, cy - 1, cx - 8, cy + 1, "flag_blue")
    g.rect(cx + 9, cy - 1, cx + 15, cy + 1, "flag_blue")


def paint_grates(g):
    for gx, gy in ((191, 285), (425, 285)):     # tree grates round the honey locust trunks
        g.rect(gx - 1, gy - 1, gx + 16, gy + 10, "pv2")
        g.rect(gx, gy, gx + 15, gy + 9, "ir2")
        for y in range(gy + 1, gy + 8, 2):
            g.hline(gx + 1, gx + 14, y, "ir1")
        for x in range(gx + 2, gx + 14, 3):
            g.vline(x, gy + 1, gy + 8, "ir3")
    for dx, dy in ((372, 230), (176, 278)):     # slot drains
        g.rect(dx, dy, dx + 10, dy + 4, "ir2")
        for x in range(dx + 1, dx + 10, 2):
            g.vline(x, dy + 1, dy + 3, "ir0")


def sun(n, d):
    """v03r1: granite pv_k in direct low sun becomes the warm ps ramp at the same value plus d steps."""
    if n[:2] == "pv" and int(n[2:]) - 4 + d >= 0:
        return "ps%d" % min(3, int(n[2:]) - 4 + d)
    return shift(n, d)


def shade_layer(base, regions):
    """A layer holding ramp-shifted copies of base pixels: [(mask, steps)], later entries win.
    v03r1: steps may be ("sun", d), warming granite to the sunlit ramp (see sun())."""
    layer = Layer()
    for m, d in regions:
        for y, x in zip(*np.nonzero(m & (base.a[..., 3] == 255))):
            n = name_of(base.a[y, x, :3])
            layer.px(x, y, sun(n, d[1]) if isinstance(d, tuple) else shift(n, d))
    return layer


LAMP_POOLS = [(88, 184, 12, 5), (140, 206, 14, 5), (474, 206, 14, 5), (544, 210, 10, 4), (604, 210, 10, 4),
              (150, 300, 12, 5), (520, 300, 12, 5), (240, 236, 8, 4)]


def ground_shading(g):
    """Cast shadow and light on the ground (hard edges, deliberate gaps): the deck dims the walk beneath
    it; the low west sun throws the deck across rows 206..247 with the tie gaps as lit slits, each column
    throws a long shadow south-east, warm streaks cross the open plaza, and lamps and storefronts pool light."""
    yy, xx = np.mgrid[0:H, 0:W]
    under = (yy >= 170) & (yy < 206) & (xx >= CURB_X + 5)
    deck = (yy >= 206) & (yy < 248) & (xx >= CURB_X + 5) & (xx < 540)
    slit = deck & (yy >= 212) & (yy < 242) & (((xx - (yy - 206) // 2) % 14) < 3)
    cols = poly([(140, 262), (152, 262), (196, 318), (178, 318)]) | poly([(474, 262), (486, 262), (530, 318), (512, 318)])
    streaks = (poly([(196, 248), (246, 248), (316, 318), (262, 318)]) | poly([(326, 248), (366, 248), (436, 318), (396, 318)])
               | poly([(470, 248), (500, 248), (556, 318), (530, 318)])) & (xx >= CURB_X + 5)
    pools = np.zeros((H, W), bool)
    for cx in (176, 288, 352, 470):
        pools |= ellipse(cx, 172, 22, 7) & (yy >= 170) & (yy < 182)
    lamps = np.zeros((H, W), bool)
    for cx, cy, rx, ry in LAMP_POOLS:
        lamps |= ellipse(cx, cy, rx, ry)
    road = xx < CURB_X
    # v03r1: lighter deck shadow (-2, was -3), warm sun in the tie slits (was -1), warm streaks (was +1)
    layer = shade_layer(g, [(under, -1), (deck & ~slit, -2), (slit, ("sun", 0)), (cols & ~deck, -2), (streaks & ~cols, ("sun", 1)),
                            (pools, 1), (lamps & ~road, 1), (lamps & road, 1)])
    # teal civic light pooling on the stone in front of the kiosk, the pylon, the dock rail and the stair canopy
    teal = np.zeros((H, W), bool)
    for cx, cy, rx, ry in TEAL_POOLS:
        teal |= ellipse(cx, cy, rx, ry)
    teal &= ~road
    for y, x in zip(*np.nonzero(teal)):
        n = name_of(g.a[y, x, :3])
        if n.startswith(("pv", "ps")):   # v03r1: sunlit slabs (ps_k = value of pv_(k+4)) glow too
            core = ((x - 0.5) % 2 == 0.5) or ((y + x) % 3 != 0)
            k = int(n[2:]) + (4 if n[:2] == "ps" else 0)
            layer.px(x, y, "tl1" if k >= 4 and core else "tl0")
    return layer


TEAL_POOLS = [(432, 205, 14, 4), (240, 236, 9, 3), (364, 300, 40, 3), (574, 210, 18, 4), (574, 214, 10, 3)]


def paint_markers(g):
    """Teal floor rings at the three interaction sites and fallen honey locust leaves."""
    for cx, cy in (KIOSK, STAIR, PYLON):
        ring = ellipse(cx, cy, 9, 4) & ~ellipse(cx, cy, 7.6, 2.8)
        for y, x in zip(*np.nonzero(ring)):
            g.px(x, y, "te3" if (x + y) % 4 else "te2")
    for tx in (198, 432):
        for i in range(26):
            x = tx - 26 + int(hsh(tx, i, 111) * 52)
            y = 270 + int(hsh(tx, i, 112) * 30)
            c = ("fo4", "fo5", "fl_y", "ru3")[int(hsh(tx, i, 113) * 4)]
            g.px(x, y, c)
            g.px(x + 1, y, c)


# ---------------------------------------------------------------- authored props
def foliage(layer, region, seed, flowers=(), holes=0.0, light=(-0.6, -0.8), base=True):
    """Leaf clusters, not noise: a plus-shaped 5 px blob per jittered grid cell, toned by its position
    against the light (upper left), each with a darker underside pixel; optional holes for lacy crowns."""
    ys, xs = np.nonzero(region)
    if not len(xs):
        return
    cx, cy = xs.mean(), ys.mean()
    rx, ry = max(1.0, (xs.max() - xs.min()) / 2), max(1.0, (ys.max() - ys.min()) / 2)
    if base:
        layer.mask(region, "fo1")
        layer.mask(region & ~np.roll(region, -1, axis=0), "fo0")
    cells = []
    for gy in range(ys.min() - 1, ys.max() + 2, 3):
        for gx in range(xs.min() - 1, xs.max() + 2, 3):
            jx = gx + int(hsh(gx, gy, seed) * 3) - 1
            jy = gy + int(hsh(gx, gy, seed + 1) * 3) - 1
            if 0 <= jx < W and 0 <= jy < H and region[jy, jx]:
                if holes and hsh(gx, gy, seed + 2) < holes:
                    continue
                cells.append((jy, jx))
    for jy, jx in sorted(cells):
        lv = light[0] * (jx - cx) / rx + light[1] * (jy - cy) / ry + (hsh(jx, jy, seed + 3) - 0.5) * 0.7
        tone = "fo5" if lv > 0.75 else ("fo4" if lv > 0.2 else ("fo3" if lv > -0.35 else "fo2"))
        for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
            if region[min(H - 1, jy + dy), min(W - 1, max(0, jx + dx))]:
                layer.px(jx + dx, jy + dy, tone)
        if jy + 2 < H and region[jy + 2, jx]:
            layer.px(jx, jy + 2, shift(tone, -2))
        if tone == "fo5" and hsh(jx, jy, seed + 4) < 0.35:
            layer.px(jx, jy - 1, "fo6")
    for i, (c, n) in enumerate(flowers):
        k = 0
        for jy, jx in cells:
            if k >= n:
                break
            if hsh(jx, jy, seed + 10 + i) < 0.3:
                layer.px(jx, jy, c)
                if hsh(jx, jy, seed + 20 + i) < 0.5:
                    layer.px(jx + 1, jy, c)
                k += 1


def stone_box(layer, x0, y0, x1, y1, lip=2):
    """Granite planter / plinth seen from the south-above: lit top lip, coursed front face, dark foot."""
    layer.rect(x0, y0, x1, y0 + lip, "st5")
    layer.hline(x0, x1, y0, "st6")
    layer.rect(x0, y0 + lip, x1, y1, "st3")
    layer.vline(x0, y0 + lip, y1, "st4")
    layer.vline(x1 - 1, y0 + lip, y1, "st2")
    for y in range(y0 + lip + 4, y1 - 1, 5):
        layer.hline(x0 + 1, x1 - 1, y, "st2")
    layer.hline(x0, x1, y1 - 1, "st1")


def iron_box(layer, x0, y0, x1, y1):
    layer.rect(x0, y0, x1, y1, "ir1")
    layer.hline(x0, x1, y0, "ir4")
    layer.hline(x0, x1, y0 + 1, "ir2")
    layer.vline(x0, y0 + 1, y1, "ir3")
    for x in range(x0 + 3, x1 - 1, 4):
        layer.vline(x, y0 + 3, y1 - 1, "ir2")
    layer.hline(x0, x1, y1 - 1, "ir0")


def lantern(layer, cx, top, glow=True):
    """Chicago-style acorn lantern: dark cap, amber glass, collar."""
    layer.rect(cx - 1, top, cx + 2, top + 1, "ir3")
    layer.rect(cx - 2, top + 1, cx + 3, top + 2, "ir1")
    layer.rect(cx - 3, top + 2, cx + 4, top + 8, "lt2")
    layer.rect(cx - 1, top + 3, cx + 2, top + 7, "lt3")
    layer.px(cx, top + 4, "lt4")
    layer.vline(cx - 3, top + 2, top + 8, "lt1")
    layer.vline(cx + 3, top + 2, top + 8, "lt0")
    layer.rect(cx - 2, top + 8, cx + 3, top + 9, "ir1")
    layer.rect(cx - 1, top + 9, cx + 2, top + 10, "ir2")


def draw_chicago_lamp(L):
    """State St curb lamp: twin-fluted iron post, acorn lantern, green street blade, Chicago flag banner."""
    cx = 88
    lantern(L, cx, 128)
    L.rect(cx - 1, 138, cx + 2, 176, "ir1")
    L.vline(cx - 1, 138, 176, "ir3")
    for y in range(142, 176, 6):
        L.px(cx + 1, y, "ir2")
    L.rect(cx - 2, 158, cx + 3, 160, "ir2")      # collar
    L.rect(cx - 3, 176, cx + 4, 180, "ir1")      # flared base
    L.hline(cx - 3, cx + 4, 176, "ir3")
    L.rect(cx - 4, 180, cx + 5, 183, "ir2")
    L.hline(cx - 4, cx + 5, 182, "ir0")
    L.vline(cx - 4, 180, 182, "ir4")
    # green street-name blade (Chicago street signs are green; the real names are runtime labels)
    L.rect(cx - 8, 141, cx + 9, 144, "aw1")
    L.hline(cx - 8, cx + 9, 141, "aw2")
    for x in range(cx - 6, cx + 7, 2):
        L.px(x, 142, "wp1")
    # flag banner on an arm: two light-blue stripes, red stars
    L.hline(cx + 2, cx + 11, 148, "ir2")
    for y in range(149, 162):
        L.hline(cx + 4, cx + 11, y, "flag_blue" if y in (151, 152, 157, 158) else "flag_white")
    for x in (cx + 5, cx + 8):
        L.px(x, 154, "flag_red")
        L.px(x, 155, "flag_red")
    L.px(cx + 4, 162, "flag_white")
    L.px(cx + 10, 162, "flag_white")


def draw_bench(L, x0, y0, w):
    """Cast-iron and slat bench seen from the south-above: backrest, gap, seat, legs, cast shadow."""
    for dy in range(13, 16):
        L.hline(x0 + 2 + (dy - 13), x0 + w + 1, y0 + dy, "pv2")
    for dy, c in ((0, "wd3"), (1, "wd1"), (2, "wd0"), (3, "ir1"), (4, "wd3"), (5, "wd2"), (6, "wd3"), (7, "wd2"), (8, "wd0")):
        L.hline(x0 + 1, x0 + w - 1, y0 + dy, c)
    L.hline(x0 + 1, x0 + w - 1, y0 + 9, "wd3")
    L.hline(x0 + 2, x0 + w - 2, y0 + 10, "ir1")
    for x in (x0, x0 + w // 2, x0 + w - 1):
        for dy in range(0, 11):
            L.px(x, y0 + dy, "ir3" if dy in (0, 4) else "ir1")
    for x in (x0 + 1, x0 + 2, x0 + w - 3, x0 + w - 2):
        for dy in range(11, 14):
            L.px(x, y0 + dy, "ir1")


def draw_bin(L, x0, y0):
    """Black steel litter bin: dome lid, dark mouth, vertical slats lit from the left."""
    w = 14
    L.rect(x0 + 3, y0, x0 + w - 3, y0 + 1, "ir3")
    L.rect(x0 + 1, y0 + 1, x0 + w - 1, y0 + 4, "ir2")
    L.hline(x0 + 2, x0 + 6, y0 + 1, "ir4")
    L.rect(x0 + 2, y0 + 4, x0 + w - 2, y0 + 5, "ir0")
    L.rect(x0 + 1, y0 + 5, x0 + w - 1, y0 + 19, "ir1")
    for x in range(x0 + 2, x0 + w - 1, 2):
        L.vline(x, y0 + 6, y0 + 18, "ir3" if x < x0 + 6 else "ir2")
    L.hline(x0 + 1, x0 + w - 1, y0 + 11, "ir2")
    L.rect(x0, y0 + 19, x0 + w, y0 + 20, "ir0")
    L.hline(x0 + 2, x0 + w + 2, y0 + 20, "pv2")


def draw_kiosk(L):
    """Teal civic kiosk on a granite pedestal: lit header bar, Loop map screen, five line colours."""
    x0, x1 = 421, 443
    stone_box(L, 419, 192, 445, 201)
    L.rect(x0, 150, x1, 192, "ir1")
    L.vline(x0, 150, 192, "ir3")
    L.vline(x1 - 1, 150, 192, "ir0")
    L.rect(x0 + 1, 147, x1 - 1, 150, "ir2")
    L.rect(x0 + 2, 150, x1 - 2, 153, "te3")
    L.hline(x0 + 3, x1 - 3, 151, "te4")
    L.rect(x0 + 3, 156, x1 - 3, 181, "te0")
    L.rect(x0 + 4, 157, x1 - 4, 180, "te1")
    # Loop map: the elevated rectangle in amber, stations as teal dots, "you are here" bright
    L.rect(x0 + 7, 161, x1 - 7, 162, "lt1")
    L.rect(x0 + 7, 172, x1 - 7, 173, "lt1")
    L.rect(x0 + 7, 161, x0 + 8, 173, "lt1")
    L.rect(x1 - 8, 161, x1 - 7, 173, "lt1")
    for x in (x0 + 10, x0 + 13):
        L.px(x, 161, "te3")
    L.rect(x1 - 10, 160, x1 - 8, 163, "te5")
    for i, c in enumerate(("loop_brown", "loop_green", "loop_orange", "loop_pink", "loop_purple")):
        L.rect(x0 + 5 + i * 3, 176, x0 + 7 + i * 3, 178, c)
    for y in (166, 168):
        L.hline(x0 + 10, x1 - 10, y, "te2")
    L.rect(x0 + 4, 184, x1 - 4, 186, "ir2")      # card slot / speaker grille
    L.hline(x0 + 6, x1 - 6, 185, "te2")


def draw_planter_stone(L, x0, x1, top, face, seed, flowers):
    stone_box(L, x0, face, x1, face + 12)
    region = ellipse((x0 + x1) / 2, face - 3, (x1 - x0) / 2 + 1, face - top) & rmask(x0, top, x1, face + 2)
    foliage(L, region, seed, flowers)


def draw_planter_iron(L, x0, x1, top, face, seed, flowers):
    iron_box(L, x0, face, x1, face + 10)
    region = ellipse((x0 + x1) / 2, face - 2, (x1 - x0) / 2, face - top) & rmask(x0, top, x1, face + 2)
    foliage(L, region, seed, flowers)


def draw_conifer_planter(L):
    stone_box(L, 498, 176, 524, 188)
    cone = poly([(511, 140), (522, 178), (500, 178)])
    foliage(L, cone, 61, light=(-0.9, -0.4))


def draw_column(L, cx):
    """Riveted L column: lit west flange, rivet rows, batten plates, lamp, flared shoe on a granite plinth,
    with knee braces up to the girder."""
    x0, x1 = cx - 8, cx + 8
    for side in (-1, 1):   # knee braces (4 px members, lit top edge, rivets)
        for t in range(0, 31):
            x = cx + side * (8 + t)
            y = 160 - (t * 25) // 30
            for k in range(4):
                L.px(x, y + k, "iw1" if k else "iw3")
            L.px(x, y + 4, "iw0")
            if t % 5 == 2:
                L.px(x, y + 2, "iw4")
        L.rect(cx + side * 8 - (3 if side < 0 else 0), 156, cx + side * 8 + (0 if side < 0 else 3), 166, "iw2")
    L.rect(x0, DECK_BOTTOM + 1, x1, 240, "iw1")
    L.vline(x0, DECK_BOTTOM + 1, 240, "iw0")
    L.vline(x1 - 1, DECK_BOTTOM + 1, 240, "iw0")
    L.rect(x0 + 1, DECK_BOTTOM + 1, x0 + 4, 240, "iw3")
    L.vline(x0 + 1, DECK_BOTTOM + 1, 240, "iw4")
    L.rect(x1 - 4, DECK_BOTTOM + 1, x1 - 1, 240, "iw2")
    L.vline(cx, DECK_BOTTOM + 1, 240, "iw0")
    for y in range(DECK_BOTTOM + 3, 238, 4):
        L.px(x0 + 2, y, "ru3" if hsh(cx, y, 71) < 0.15 else "iw4")
        L.px(x1 - 3, y, "iw3")
    for y in (150, 190, 222):   # batten plates
        L.rect(x0 - 1, y, x1 + 1, y + 3, "iw2")
        L.hline(x0 - 1, x1 + 1, y, "iw4")
        for x in range(x0 + 1, x1, 3):
            L.px(x, y + 1, "iw3")
    for y, n in ((200, 5), (214, 4), (230, 6)):   # rust streak clusters below the lamp
        L.rect(x0 + 5, y, x0 + 7, y + n, "ru1")
        L.px(x0 + 5, y, "ru2")
    # column lamp facing the plaza
    L.rect(cx - 3, 168, cx + 3, 178, "iw2")
    L.rect(cx - 2, 169, cx + 2, 177, "lt2")
    L.rect(cx - 1, 170, cx + 1, 176, "lt3")
    L.px(cx - 1, 172, "lt4")
    # flared shoe and bolted base plate
    for i, y in enumerate(range(240, 250)):
        L.rect(x0 - i // 3, y, x1 + i // 3, y + 1, "iw1")
        L.px(x0 - i // 3, y, "iw3")
    L.hline(x0 - 3, x1 + 3, 248, "iw2")
    for x in (x0 - 2, x0 + 3, x1 - 4, x1 + 1):
        L.px(x, 246, "iw4")
    stone_box(L, cx - 14, 249, cx + 14, 264, lip=3)
    for x, n in ((cx - 9, 6), (cx - 4, 4), (cx + 6, 7), (cx + 10, 3)):   # rust stains run down the plinth
        L.rect(x, 252, x + 1, 252 + n, "ru1")
        L.px(x, 252, "ru2")


def draw_pylon(L):
    """Teal civic wayfinding pylon: lit cap, map screen with the five line colours, granite foot."""
    x0, x1 = 236, 244
    L.rect(x0, 196, x1, 228, "ir1")
    L.vline(x0, 196, 228, "ir3")
    L.vline(x1 - 1, 196, 228, "ir0")
    L.rect(x0, 194, x1, 197, "te3")
    L.hline(x0 + 1, x1 - 1, 194, "te5")
    L.rect(x0 + 2, 200, x1 - 2, 214, "te1")
    L.vline(x0 + 3, 201, 213, "te3")
    for y in (203, 206, 209, 212):
        L.px(x0 + 5, y, "te4")
    for i, c in enumerate(("loop_brown", "loop_green", "loop_orange", "loop_pink", "loop_purple")):
        L.px(x0 + 2 + i if i < 4 else x1 - 2, 217, c)
        L.px(x0 + 2 + i if i < 4 else x1 - 2, 218, c)
    stone_box(L, x0 - 1, 227, x1 + 1, 233, lip=2)


def draw_seat(L, x0):
    """Backless granite seat block beside the medallion."""
    L.rect(x0, 252, x0 + 28, 258, "pv6")
    L.hline(x0, x0 + 28, 252, "pv7")
    L.rect(x0, 258, x0 + 28, 265, "pv4")
    L.hline(x0, x0 + 28, 258, "pv3")
    L.vline(x0, 252, 265, "pv5")
    L.vline(x0 + 27, 252, 265, "pv3")
    L.hline(x0, x0 + 28, 265, "pv1")
    L.hline(x0 + 2, x0 + 30, 266, "pv2")


def draw_honey_locust(L, tx, seed):
    """Street tree in a grate: forked trunk and a lacy, open crown (honey locust) with light gaps."""
    L.rect(tx - 2, 262, tx + 2, 292, "ru0")
    L.vline(tx - 2, 262, 292, "ru1")
    L.px(tx - 1, 270, "st2")
    L.px(tx, 281, "st2")
    for t in range(0, 14):   # two leaders
        L.px(tx - 2 - t // 2, 262 - t, "ru0")
        L.px(tx + 1 + t // 2, 262 - t, "ru0")
    crown = (ellipse(tx - 10, 244, 17, 13) | ellipse(tx + 11, 241, 16, 13) | ellipse(tx, 230, 16, 10)) & rmask(0, 0, W, 264)
    foliage(L, crown, seed, holes=0.18, base=False)
    for i in range(10):                                  # pale seed pods hanging in the crown
        x = tx - 20 + int(hsh(tx, i, 131) * 40)
        y = 228 + int(hsh(tx, i, 132) * 30)
        if crown[y, x] and crown[y + 1, x]:
            L.px(x, y, "fo6")
            L.px(x, y + 1, "ru3")


def draw_bike_dock(L):
    """Bike-share dock: teal-lit rail, five docked bikes in side view, payment terminal at the east end."""
    x0, x1 = 324, 404
    L.rect(x0, 293, x1, 297, "ir2")
    L.hline(x0, x1, 293, "ir4")
    L.hline(x0 + 1, x1 - 1, 295, "te2")
    for i in range(5):
        bx = x0 + 2 + i * 15
        for wx in (bx + 3, bx + 11):                    # wheels: dark tyre, lit upper rim, hub
            ring = ellipse(wx + 0.5, 289.5, 3.6, 3.6) & ~ellipse(wx + 0.5, 289.5, 2.2, 2.2)
            for y, x in zip(*np.nonzero(ring)):
                L.px(x, y, "ir3" if y < 288 else "ir0")
            L.px(wx, 289, "ir3")
        for k in range(9):                              # top tube and down tube (teal frame)
            L.px(bx + 4 + k, 285, "te3" if k < 7 else "te2")
        for k in range(4):
            L.px(bx + 4 + k, 286 + k, "te2")
            L.px(bx + 11 - k // 2, 286 + k, "te2")
        L.rect(bx + 2, 283, bx + 6, 284, "ir1")        # saddle
        L.rect(bx + 11, 282, bx + 14, 283, "ir2")      # bars
        L.vline(bx + 12, 283, 285, "ir2")
        L.rect(bx + 12, 285, bx + 15, 287, "te1")      # front basket
        L.vline(bx + 14, 286, 294, "ir1")             # dock post with its light
        L.px(bx + 14, 287, "te4")
    L.rect(x1 - 5, 272, x1, 297, "ir1")               # terminal
    L.vline(x1 - 5, 272, 297, "ir3")
    L.rect(x1 - 4, 274, x1 - 1, 282, "te3")
    L.px(x1 - 4, 275, "te5")
    L.rect(x1 - 4, 284, x1 - 1, 285, "te2")


BOLLARD_ROWS = (213, 225, 253, 265)


def draw_bollard(L, y):
    """Cast-iron bollard at the curb ramp with a small teal reflector."""
    L.rect(89, y - 6, 92, y + 1, "ir1")
    L.hline(89, 92, y - 7, "ir3")
    L.px(89, y - 6, "ir4")
    L.px(91, y - 3, "te3")
    L.hline(89, 92, y, "ir0")


def draw_stair(L):
    """Station stair up to the State/Lake platform: granite treads, iron stringers and handrails,
    stone newel posts with lanterns, a glass canopy where it meets the deck."""
    x0, x1 = 550, 598
    top, bottom = 140, 204
    steps = 12
    for i in range(steps):
        yb = bottom - (i * (bottom - top)) // steps
        yt = bottom - ((i + 1) * (bottom - top)) // steps
        L.rect(x0, yt, x1, yb, "st4" if i % 2 == 0 else "st5")
        L.hline(x0, x1, yt, "st6")
        L.hline(x0, x1, yb - 1, "st2")
        L.hline(x0, x1, yb - 2, "st3")
    for x in (x0 - 2, x1):   # stringers and handrails
        L.rect(x, top, x + 2, bottom, "ir1")
        L.vline(x + (0 if x < x0 else 1), top, bottom, "ir3")
        for y in range(top + 2, bottom, 6):
            L.px(x + 1, y, "ir4")
    L.rect(x0 - 6, 130, x1 + 6, 140, "ir2")        # canopy frame
    L.rect(x0 - 5, 132, x1 + 5, 138, "te1")
    for x in range(x0 - 4, x1 + 4, 6):
        L.vline(x, 132, 138, "ir1")
    L.hline(x0 - 5, x1 + 5, 132, "te3")
    L.hline(x0 - 6, x1 + 6, 139, "ir0")
    for i, c in enumerate(("loop_brown", "loop_green", "loop_orange", "loop_pink", "loop_purple")):
        L.rect(x0 + 13 + i * 4, 134, x0 + 16 + i * 4, 136, c)
    for nx in (540, 600):   # newel posts with lanterns
        stone_box(L, nx, 186, nx + 8, 207, lip=2)
        lantern(L, nx + 4, 175)


def draw_east_terrace(L):
    """Raised east terrace: coursed retaining wall, coping, conifer and flower planting, lantern."""
    stone_box(L, 608, 176, 640, 264, lip=4)
    for y in range(184, 262, 6):
        for x in range(610 + (3 if (y // 6) % 2 else 0), 640, 10):
            L.vline(x, y, y + 6, "st2")
    region = (ellipse(624, 166, 16, 14) | ellipse(612, 172, 6, 6)) & rmask(608, 140, 640, 178)
    foliage(L, region, 81, (("fl_w", 6), ("fl_p", 3)))
    cone = poly([(630, 128), (639, 172), (621, 172)])
    foliage(L, cone, 83, light=(-0.9, -0.4))
    lantern(L, 614, 196)


def draw_fountain(L):
    """Stone basin with a low jet: coping, teal water with ripple clusters, dark inner wall."""
    x0, x1, y0, y1 = 566, 640, 264, 298
    L.rect(x0, y0, x1, y1, "st3")
    L.rect(x0, y0, x1, y0 + 3, "st5")
    L.hline(x0, x1, y0, "st6")
    L.rect(x0 + 4, y0 + 4, x1, y1 - 6, "te1")
    L.hline(x0 + 4, x1, y0 + 4, "te0")
    for i in range(30):
        rx_ = x0 + 6 + int(hsh(i, 1, 91) * (x1 - x0 - 10))
        ry_ = y0 + 7 + int(hsh(i, 2, 91) * (y1 - y0 - 15))
        L.rect(rx_, ry_, rx_ + 3, ry_ + 1, "te2" if i % 3 else "te3")
    for y in range(y0 - 8, y0 + 12):
        L.px(604, y, "te4" if y % 3 else "te5")
    L.rect(602, y0 + 9, 607, y0 + 12, "te3")
    L.hline(x0, x1, y1 - 6, "st4")
    L.rect(x0, y1 - 5, x1, y1, "st3")
    L.hline(x0, x1, y1 - 1, "st1")
    L.vline(x0, y0, y1, "st4")


def draw_foreground(L):
    """South parapet with an iron picket fence, planting behind it and two lamp posts."""
    for x0, x1 in ((96, 300), (352, 560)):
        stone_box(L, x0, 304, x1, 322, lip=3)
        region = rmask(x0 + 2, 292, x1 - 2, 305) & ~ellipse((x0 + x1) / 2, 292, (x1 - x0) / 2 + 30, 6)
        hedge = np.zeros((H, W), bool)
        for i in range(0, x1 - x0, 12):
            hedge |= ellipse(x0 + 6 + i, 299 - 3 * hsh(i, x0, 96), 8 + 3 * hsh(i, x0, 95), 7)
        foliage(L, hedge & rmask(x0 + 1, 289, x1 - 1, 305), 97 + x0, (("fl_w", 16), ("fl_r", 8), ("fl_y", 6), ("fl_p", 5)))
        L.hline(x0, x1, 296, "ir2")
        L.hline(x0, x1, 302, "ir1")
        for x in range(x0 + 1, x1, 4):
            L.vline(x, 294, 304, "ir1")
            L.px(x, 293, "ir3")
    for lx in (150, 520):
        L.rect(lx - 1, 262, lx + 2, 305, "ir1")
        L.vline(lx - 1, 262, 305, "ir3")
        lantern(L, lx, 252)


# Y-sort groups: layer name -> list of (prop name, painter, pivot row). A prop is a region of its layer.
PROP_GROUPS = [
    ("ysort-underdeck-props", [
        ("chicago-lamp", draw_chicago_lamp, 182.5),
        ("planter-stone-west", lambda L: draw_planter_stone(L, 214, 254, 154, 174, 41, (("fl_w", 8), ("fl_p", 3))), 185.5),
        ("bench", lambda L: draw_bench(L, 258, 172, 42), 186.5),
        ("planter-iron", lambda L: draw_planter_iron(L, 304, 318, 158, 174, 43, (("fl_r", 3),)), 184.5),
        ("planter-stone-east", lambda L: draw_planter_stone(L, 364, 386, 156, 173, 45, (("fl_w", 5),)), 184.5),
        ("litter-bin", lambda L: draw_bin(L, 397, 171), 190.5),
        ("civic-kiosk", draw_kiosk, 200.5),
        ("conifer-planter", draw_conifer_planter, 187.5),
    ]),
    ("ysort-l-columns", [
        ("l-column-west", lambda L: draw_column(L, COLUMN_X[0]), 263.5),
        ("l-column-east", lambda L: draw_column(L, COLUMN_X[1]), 263.5),
    ]),
    ("ysort-station-stair-east", [
        ("station-stair", draw_stair, 206.5),
        ("east-terrace", draw_east_terrace, 263.5),
    ]),
    ("ysort-plaza-props", [
        ("fountain", draw_fountain, 297.5),
        ("planter-column-west", lambda L: draw_planter_iron(L, 100, 122, 236, 251, 51, (("fl_p", 4),)), 261.5),
        ("planter-column-east", lambda L: draw_planter_iron(L, 488, 510, 236, 251, 53, (("fl_w", 4),)), 261.5),
        *[("bollard-%d" % y, (lambda yy: lambda L: draw_bollard(L, yy))(y), y + 0.5) for y in BOLLARD_ROWS],
        ("wayfinding-pylon", draw_pylon, 232.5),
        ("granite-seat-west", lambda L: draw_seat(L, 232), 265.5),
        ("granite-seat-east", lambda L: draw_seat(L, 372), 265.5),
        ("honey-locust-west", lambda L: draw_honey_locust(L, 198, 101), 293.5),
        ("honey-locust-east", lambda L: draw_honey_locust(L, 432, 103), 293.5),
        ("bike-share-dock", draw_bike_dock, 297.5),
    ]),
    ("ysort-foreground", [
        ("south-parapet-fence", draw_foreground, 340.5),
    ]),
]

# ---------------------------------------------------------------- layers
STATIC = ["ground-street-plaza", "ground-shadow-light", "backdrop-facade-north", "backdrop-deck-l-girder",
          "backdrop-underdeck-storefronts", "station-plate"]
YSORT = [name for name, _ in PROP_GROUPS]
LAYERS = STATIC + YSORT
GUIDE = "guides-walkmask"
BAND = (DECK_BOTTOM + 1, 166)       # storefront glass rows taken from the underpainting
PLATE = (296, 112, 356, 123)        # State/Lake station plate on the girder web; text is a runtime label
COLUMN_X = (140, 474)
GIRDER_LAMPS = (60, 236, 396, 572)
# Underpainting repairs: (box x0, y0, x1, y1, dx) copies clean storefront from dx columns away, so no
# reference column, brace, kiosk or lamp survives behind the authored ones in the editable backdrop.
REPAIRS = [
    ((83, 135, 104, 166), 40),      # reference curb lamp and sign
    ((104, 135, 180, 166), 76),     # west column and braces
    ((410, 135, 450, 166), -40),    # reference kiosk
    ((438, 135, 512, 166), -74),    # east column and braces
]


def draw_deck(L):
    """The Lake Street elevated, authored: open track deck (ties over a dark gap, two running rails and a
    guard rail), a riveted plate girder with lit top flange, stiffeners every 32 px, rivet rows, sparse
    rust runs, amber girder lamps, the bottom flange and lattice bracing in the shadow under it, and
    bolted caps over the two columns."""
    y0 = DECK_TOP
    L.rect(0, y0, W, y0 + 13, "iw0")
    for x in range(0, W):
        t = x % 6
        if t < 4:                                      # timber ties seen from above
            c = "ru0" if t in (0, 3) else ("ru1" if hsh(x // 6, 0, 121) < 0.7 else "wd0")
            L.vline(x, y0 + 1, y0 + 12, c)
            if t == 1 and hsh(x // 6, 1, 121) < 0.25:
                L.px(x, y0 + 6, "ru2")
    for ry, hi in ((y0 + 3, "iw4"), (y0 + 9, "iw4")):  # running rails
        L.hline(0, W, ry, hi)
        L.hline(0, W, ry + 1, "iw2")
    L.hline(0, W, y0 + 6, "iw3")                     # guard rail
    for x in range(2, W, 6):                           # tie plates under the rails
        L.px(x, y0 + 5, "iw3")
        L.px(x, y0 + 11, "iw3")
    L.hline(0, W, y0, "iw2")
    L.hline(0, W, y0 + 12, "iw1")
    top = y0 + 13                                      # plate girder: top flange, warm sun glint
    L.rect(0, top, W, top + 3, "iw3")
    L.hline(0, W, top, "ru2")
    for x in range(0, W, 9):
        L.px(x + int(hsh(x, 3, 122) * 6), top, "ru3")
    L.hline(0, W, top + 2, "iw2")
    web0, web1 = top + 3, top + 21                     # web
    L.rect(0, web0, W, web1, "iw2")
    L.hline(0, W, web1 - 1, "iw1")
    for x in range(0, W, 4):                           # rivet rows along both flanges
        L.px(x + 1, web0, "iw4")
        L.px(x + 1, web0 + 1, "iw1")
        L.px(x + 3, web1 - 2, "iw4")
    for sx in range(14, W, 32):                        # stiffeners: lit left edge, shadowed right edge
        L.vline(sx, web0, web1, "iw3")
        L.vline(sx + 1, web0, web1, "iw2")
        L.vline(sx + 2, web0, web1, "iw1")
        for y in range(web0 + 3, web1 - 1, 3):
            L.px(sx + 1, y, "iw4")
        if hsh(sx, 0, 122) < 0.6:                      # rust runs under a rivet
            n = 2 + int(hsh(sx, 1, 122) * 5)
            rx = sx + 6 + int(hsh(sx, 2, 122) * 18)
            L.rect(rx, web0 + 2, rx + 1, web0 + 2 + n, "ru1")
            L.px(rx, web0 + 2, "ru2")
    bot = web1                                          # bottom flange
    L.rect(0, bot, W, bot + 3, "iw3")
    L.hline(0, W, bot, "iw4")
    L.hline(0, W, bot + 2, "iw1")
    L.rect(0, bot + 3, W, DECK_BOTTOM + 1, "iw0")       # lattice bracing in the shadow under the deck
    for x in range(0, W):
        for y in range(bot + 3, DECK_BOTTOM + 1):
            k = y - bot - 3
            if (x + k) % 8 == 0 or (x - k) % 8 == 0:
                L.px(x, y, "iw2")
    for lx in GIRDER_LAMPS:                             # amber lamps on the web, light spilling on the bracing
        L.rect(lx - 6, web1 - 8, lx + 6, web1 - 1, "iw1")
        L.rect(lx - 5, web1 - 7, lx + 5, web1 - 2, "lt2")
        L.rect(lx - 3, web1 - 6, lx + 3, web1 - 3, "lt3")
        L.hline(lx - 1, lx + 1, web1 - 5, "lt4")
        L.hline(lx - 5, lx + 5, bot, "lt1")
        for y in range(bot + 3, DECK_BOTTOM + 1):
            for x in range(lx - 7 - (y - bot), lx + 8 + (y - bot)):
                if L.get(x, y) == PAL["iw2"]:
                    L.px(x, y, "ru2")
                elif L.get(x, y) == PAL["iw0"] and (x + y) % 2 == 0 and abs(x - lx) < 4 + (y - bot) // 2:
                    L.px(x, y, "ru0")
    for cx in COLUMN_X:                                 # bolted column caps
        L.rect(cx - 13, top, cx + 13, DECK_BOTTOM + 1, "iw2")
        L.vline(cx - 13, top, DECK_BOTTOM + 1, "iw3")
        L.vline(cx + 12, top, DECK_BOTTOM + 1, "iw0")
        L.hline(cx - 13, cx + 13, top, "iw4")
        for y in range(top + 2, DECK_BOTTOM, 3):
            for x in (cx - 11, cx - 6, cx + 5, cx + 10):
                L.px(x, y, "iw4")
        L.rect(cx - 8, DECK_BOTTOM - 4, cx + 8, DECK_BOTTOM + 1, "iw1")


def draw_plate(L):
    x0, y0, x1, y1 = PLATE
    L.rect(x0, y0, x1, y1, "ir0")
    L.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, "ir2")
    L.hline(x0 + 1, x1 - 1, y0 + 1, "ir3")
    for i, c in enumerate(("loop_brown", "loop_green", "loop_orange", "loop_pink", "loop_purple")):
        L.rect(x0 + 2 + i * 2, y0 + 2, x0 + 4 + i * 2, y1 - 2, c)
    for x in (x0 + 6, x1 - 7):
        L.px(x, y0 - 1, "ir0")


def build_layers():
    idx = underpainting()
    up = RGB[idx].astype(np.uint8)
    for (x0, y0, x1, y1), dx in REPAIRS:
        up[y0:y1, x0:x1] = up[y0:y1, x0 + dx:x1 + dx].copy()
    g = Layer()
    paint_road(g)
    paint_underdeck_walk(g)
    paint_plaza(g)
    paint_medallion(g)
    paint_grates(g)
    paint_markers(g)
    g.rect(0, 0, W, 62, "ui")
    layers = {"ground-street-plaza": g, "ground-shadow-light": ground_shading(g)}
    facade, deck, band = Layer(), Layer(), Layer()
    facade.rect(0, 0, W, 62, "ui")
    facade.a[62:DECK_TOP, :, :3] = up[62:DECK_TOP]
    facade.a[62:DECK_TOP, :, 3] = 255
    draw_deck(deck)
    band.a[BAND[0]:BAND[1], CURB_X + 5:, :3] = up[BAND[0]:BAND[1], CURB_X + 5:]
    band.a[BAND[0]:BAND[1], CURB_X + 5:, 3] = 255
    layers.update({"backdrop-facade-north": facade, "backdrop-deck-l-girder": deck, "backdrop-underdeck-storefronts": band})
    plate = Layer()
    draw_plate(plate)
    layers["station-plate"] = plate
    props = []
    for group, entries in PROP_GROUPS:
        L = Layer()
        for name, painter, pivot in entries:
            P = Layer()
            painter(P)
            m = P.opaque()
            if (m & L.opaque()).any():
                raise SystemExit("y-sort props overlap inside %s: %s" % (group, name))
            L.a[m] = P.a[m]
            ys, xs = np.nonzero(m)
            props.append({"layer": group, "name": name, "region": [int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)], "pivot": pivot})
        layers[group] = L
    check_regions(layers, props)
    check_pivots(props)
    return {k: Image.fromarray(v.a, "RGBA") for k, v in layers.items()}, props


def check_regions(layers, props):
    """Each opaque y-sort pixel must lie in exactly one prop region of its layer (one pivot per pixel)."""
    for group in YSORT:
        count = np.zeros((H, W), int)
        for p in props:
            if p["layer"] == group:
                x, y, w, h = p["region"]
                count[y:y + h, x:x + w] += 1
        op = layers[group].opaque()
        if (op & (count != 1)).any():
            ys, xs = np.nonzero(op & (count != 1))
            raise SystemExit("%s: %d opaque px outside or in two regions, first at %s" % (group, len(xs), (int(xs[0]), int(ys[0]))))


def check_pivots(props):
    """A prop's pivot sits half a row above the bottom edge of the footprint block it stands on, so the
    hero draws in front as soon as she can stand south of it, and behind it whenever she is north."""
    for p in props:
        x, y, w, h = p["region"]
        feet = [b for b in BLOCKS if b[0] < x + w and x < b[0] + b[2] and b[1] < y + h and y < b[1] + b[3]
                and abs(b[1] + b[3] - 0.5 - p["pivot"]) < 0.01]
        if p["pivot"] < WALK[1] + WALK[3] and not feet:
            raise SystemExit("pivot %.1f of %s does not sit on a footprint block" % (p["pivot"], p["name"]))


def runtime_layers(layers):
    ground = Image.new("RGBA", (W, H))
    for name in STATIC:
        ground.alpha_composite(layers[name])
    out = {"ground-far": ground}
    for name in YSORT:
        out[name] = layers[name]
    return out


def merged(layers):
    out = Image.new("RGBA", (W, H))
    for name in LAYERS:
        out.alpha_composite(layers[name])
    return out


# ---------------------------------------------------------------- hero visibility (exact y-sort model)
HERO_IDLE = ROOT / "game/assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-female_native-idle-south_m8-prototype_20261014-135400-3bacea6e.png"


def cover_pivot(layers, props):
    """Per pixel: the highest pivot of any y-sort pixel there (the hero is hidden there when her feet
    are north of that pivot). Labels and static layers are always under her."""
    cov = np.full((H, W), -1.0)
    for p in props:
        x, y, w, h = p["region"]
        op = np.array(layers[p["layer"]])[y:y + h, x:x + w, 3] == 255
        sub = cov[y:y + h, x:x + w]
        sub[op] = np.maximum(sub[op], p["pivot"])
    return cov


REVEAL = {"radius": (15.0, 26.0), "lift": 21.0, "max_hole": 0.8, "threshold": 0.5}
BAYER = np.array([0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5]).reshape(4, 4) / 16.0


def hero_mask():
    return np.array(Image.open(HERO_IDLE).convert("RGBA"))[..., 3] > 0


def visibility_map(cov, hero, reveal=False):
    """Visible fraction of the south idle hero for feet at every pixel (sprite 32x48, centred, offset -20,
    so her top-left is feet + (-16, -44)). With reveal=True the y-sort pixels over her are dithered out
    exactly as the scene shader does at full strength."""
    yy, xx = np.mgrid[0:H, 0:W]
    vis = np.zeros((H, W))
    tot = np.zeros((H, W))
    rx, ry = REVEAL["radius"]
    for j, i in zip(*np.nonzero(hero)):
        dy, dx = j - 44, i - 16
        sy, sx = yy + dy, xx + dx
        valid = (sy >= 0) & (sy < H) & (sx >= 0) & (sx < W)
        c = np.where(valid, cov[np.clip(sy, 0, H - 1), np.clip(sx, 0, W - 1)], -1.0)
        seen = c <= yy
        if reveal:
            d = np.hypot((sx + 0.5 - xx) / rx, (sy + 0.5 - (yy - REVEAL["lift"])) / ry)
            t = 1.0 - np.clip((d - 0.75) / 0.25, 0.0, 1.0)
            seen |= BAYER[sy % 4, sx % 4] < t * REVEAL["max_hole"]
        tot += valid
        vis += valid & seen
    return vis / np.maximum(tot, 1)


def walk_grid():
    m = np.zeros((H, W), bool)
    for y in range(WALK[1], WALK[1] + WALK[3]):
        for x in range(WALK[0], WALK[0] + WALK[2]):
            m[y, x] = walkable(x, y)
    return m


def visibility_report(layers, props):
    hero = hero_mask()
    cov = cover_pivot(layers, props)
    walk = walk_grid()
    raw = visibility_map(cov, hero)
    low = walk & (raw < REVEAL["threshold"])
    eff = np.where(low, visibility_map(cov, hero, reveal=True), raw)

    def worst(a, n=6):
        ys, xs = np.nonzero(walk)
        order = np.argsort(a[ys, xs], kind="stable")[:n]
        return [[int(xs[k]), int(ys[k]), round(float(a[ys[k], xs[k]]), 3)] for k in order]
    return {"walkable_positions": int(walk.sum()), "raw_min_visible_fraction": round(float(raw[walk].min()), 4),
            "raw_worst": worst(raw), "reveal_positions": int(low.sum()),
            "with_reveal_min_visible_fraction": round(float(eff[walk].min()), 4), "with_reveal_worst": worst(eff),
            "reveal_params": REVEAL}, low


def reveal_mask_image(low):
    return Image.fromarray(np.where(low, 255, 0).astype(np.uint8), "L")


def gd_props(props):
    rows = ['\t["%s", Rect2(%d, %d, %d, %d), %s],' % (p["layer"], *p["region"], p["pivot"]) for p in props]
    return "const YSORT_PROPS := [\n" + "\n".join(rows) + "\n]"


# ---------------------------------------------------------------- guides, files
def walkmask():
    m = np.zeros((H, W, 4), np.uint8)
    m[..., 3] = 255
    for y in range(WALK[1], WALK[1] + WALK[3]):
        for x in range(WALK[0], WALK[0] + WALK[2]):
            if walkable(x, y):
                m[y, x, :3] = 255
    return Image.fromarray(m, "RGBA")


def png_bytes(img):
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=False, compress_level=9)
    return buf.getvalue()


ZIP_TIME = (2026, 10, 17, 18, 32, 34)


def ora_bytes(layers, guide, flat):
    root = ET.Element("image", {"w": str(W), "h": str(H), "name": PREFIX, "version": "0.0.3"})
    stack = ET.SubElement(root, "stack")
    buf = io.BytesIO()
    entries = [(name, layers[name], "visible") for name in LAYERS] + [(GUIDE, guide, "hidden")]
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", ZIP_TIME), "image/openraster", compress_type=zipfile.ZIP_STORED)
        z.writestr(zipfile.ZipInfo("mergedimage.png", ZIP_TIME), png_bytes(flat), compress_type=zipfile.ZIP_DEFLATED)
        for i, (name, img, vis) in reversed(list(enumerate(entries))):
            src = f"data/layer{i:02d}.png"
            z.writestr(zipfile.ZipInfo(src, ZIP_TIME), png_bytes(img), compress_type=zipfile.ZIP_DEFLATED)
            ET.SubElement(stack, "layer", {"name": name, "src": src, "x": "0", "y": "0", "opacity": "1.0", "visibility": vis, "composite-op": "svg:src-over"})
        z.writestr(zipfile.ZipInfo("stack.xml", ZIP_TIME), ET.tostring(root, encoding="utf-8", xml_declaration=True), compress_type=zipfile.ZIP_DEFLATED)
    return buf.getvalue()


def pxo_bytes(layers, guide, flat):
    entries = [(name, layers[name], True, False) for name in LAYERS] + [(GUIDE, guide, False, True)]
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": locked, "metadata": {}, "name": name,
                   "new_cels_linked": False, "opacity": 1.0, "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": visible} for name, _, visible, locked in entries]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0} for _ in entries],
                    "duration": 1.0, "metadata": {}}]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": json.dumps("chicago-loop-state-lake-v03r1"),
                      "frame_current_tag": "0", "include_tag_in_filename": "false", "interpolation": "0",
                      "lines_count": "1", "new_dir_for_each_frame_tag": "false", "number_of_digits": "4",
                      "number_of_frames": "1", "orientation": "0", "repeat_count": "0", "resize": "100",
                      "save_quality": "0.75", "separator_character": "\"_\"",
                      "sheet_layers_as_separate_files": "false", "split_layers": "false"}
    data = {"author_company": "", "author_contact": "", "author_display_name": "", "author_real_name": "",
            "brushes": [], "color_mode": 5, "current_frame": 0, "current_layer": len(LAYERS) - 1,
            "export_profile": export_profile, "fps": 6.0, "frames": frames_json, "guides": [], "layers": layer_json,
            "license": "", "metadata": {}, "next_keyframe_id": 0, "palettes": [],
            "pixelorama_version": PIXELORAMA_VERSION, "project_current_palette_name": "", "pxo_version": 7,
            "reference_images": [], "size_x": W, "size_y": H, "symmetry_points": [W - 1.0, H - 1.0], "tags": [],
            "tile_mode_x_basis_x": W, "tile_mode_x_basis_y": 0, "tile_mode_y_basis_x": 0, "tile_mode_y_basis_y": H,
            "tilesets": [], "user_data": "", "vanishing_points": []}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        def put_entry(name, payload):
            z.writestr(zipfile.ZipInfo(name, ZIP_TIME), payload, zipfile.ZIP_DEFLATED)
        put_entry("data.json", json.dumps(data, separators=(",", ":")))
        put_entry("mimetype", "application/x-pixelorama")
        put_entry("preview.png", png_bytes(flat))
        put_entry("image_data/frames/1/", b"")
        for i, (_, img, _, _) in enumerate(entries, start=1):
            put_entry(f"image_data/frames/1/layer_{i}", img.tobytes())
            put_entry(f"image_data/frames/1/indices_layer_{i}", b"\x00")
    return buf.getvalue()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def text_sha(data):
    """sha256-text-lf-v1: CRLF -> LF before hashing, so a checkout with autocrlf still matches."""
    return sha(data.replace(b"\r\n", b"\n"))


def rel(path):
    path = Path(path).resolve()
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path).replace("\\", "/")


def palette_colours(layers):
    return sorted({tuple(p) for img in layers.values() for p in np.array(img)[np.array(img)[..., 3] == 255][:, :3].tolist()})


def origin_counts(layers, props):
    """Visible-pixel provenance of the merged image: underpainted backdrop vs authored."""
    flat = np.array(merged(layers))
    under = np.zeros((H, W), bool)
    for name in ("backdrop-facade-north", "backdrop-underdeck-storefronts"):
        under |= np.array(layers[name])[..., 3] == 255
    covered = np.zeros((H, W), bool)
    for name in ["station-plate"] + YSORT:
        covered |= np.array(layers[name])[..., 3] == 255
    visible = np.zeros((H, W), bool)
    visible[62:318] = True
    u = int((under & ~covered & visible).sum())
    return {"visible_rows": [62, 317], "visible_px": int(visible.sum()), "underpainted_visible_px": u,
            "authored_visible_px": int(visible.sum()) - u, "underpainted_share": round(u / visible.sum(), 4)}


def build(out=OUT, runtime=RUNTIME):
    out.mkdir(parents=True, exist_ok=True)
    runtime.mkdir(parents=True, exist_ok=True)
    layers, props = build_layers()
    guide = walkmask()
    flat = merged(layers)
    rt = runtime_layers(layers)
    files = {}
    for name in ["ground-far"] + YSORT:
        data = png_bytes(rt[name])
        path = runtime / f"{PREFIX}_{name}_{VARIANT}_{STAMP}.png"
        path.write_bytes(data)
        files[name] = {"file": rel(path), "sha256": sha(data), "hash_algorithm": "sha256-bytes"}
    vis_report, low = visibility_report(layers, props)
    data = png_bytes(reveal_mask_image(low))
    path = runtime / f"{PREFIX}_occlusion-reveal-mask_{VARIANT}_{STAMP}.png"
    path.write_bytes(data)
    files["occlusion-reveal-mask"] = {"file": rel(path), "sha256": sha(data), "hash_algorithm": "sha256-bytes"}
    colours = palette_colours(layers)
    pal_text = "GIMP Palette\nName: chicago-loop-state-lake-v03r1\nColumns: 16\n#\n" + "".join(
        f"{r:3d} {g:3d} {b:3d}\t{name_of((r, g, b))}\n" for r, g, b in colours)
    extra = {
        "merged-preview": (f"{PREFIX}_merged-preview_{VARIANT}_{STAMP}.png", png_bytes(flat)),
        "walkmask-guide": (f"{PREFIX}_{GUIDE}_{VARIANT}_{STAMP}.png", png_bytes(guide)),
        "openraster": (f"{PREFIX}_layered-source_{VARIANT}_{STAMP}.ora", ora_bytes(layers, guide, flat)),
        "pixelorama": (f"{PREFIX}_layered-source_{VARIANT}_{STAMP}.pxo", pxo_bytes(layers, guide, flat)),
        "palette-gpl": (f"{PREFIX}_palette_{VARIANT}_{STAMP}.gpl", pal_text.encode("utf-8")),
    }
    for key, (name, data) in extra.items():
        (out / name).write_bytes(data)
        text = name.endswith(".gpl")
        files[key] = {"file": rel(out / name), "sha256": text_sha(data) if text else sha(data),
                      "hash_algorithm": "sha256-text-lf-v1" if text else "sha256-bytes"}
    manifest = {
        "project": "Worlds Between",
        "scene": "Chicago Loop arrival block: State St x Lake St under the Lake Street elevated (State/Lake)",
        "status": "UNAPPROVED candidate v03r1 (one bounded visual correction of v03), opt-in only (off by default) for Codex visual QA and creator review; counters unchanged (40.8%, M2 10/12, scenes 3/12, sprites 0/52, playtests 0/2)",
        "canon": "The exact intersection, the pedestrian Lake St plaza, the medallion, the stair position and the terrace are art-pilot choices, not creator-approved landmarks.",
        "authorship": ("Backdrop bands (facade north of the L, deck girder, storefront glass under the deck) are a disclosed "
                       "underpainting of the nonruntime style reference: numpy area average, row recomposition, nearest "
                       "colour in the curated palette, small-component cluster merge, storefront repairs. Everything at "
                       "plaza level, the L columns and braces, the stair and all props are authored in this tool as "
                       "explicit pixel clusters. Built by Claude (Claude Code, signed-in Claude Max, firstParty)."),
        "correction_of": {"base_author": rel(BASE_AUTHOR), "base_author_sha256_text_lf": text_sha(BASE_AUTHOR.read_bytes()),
                          "changes": ["warm sunlit paving ramp ps0..ps3 (authored ground only, never the underpainting)",
                                      "slab tones one step lighter; sunlit slabs in running clusters of about 3 x 2 slabs",
                                      "L cast shadow -2 (was -3); warm sun in the tie slits (was -1); warm streaks (was +1)",
                                      "under-deck concrete one step lighter",
                                      "facade strip rows 62..%d: near-black components <= %d px merged into their surroundings, "
                                      "remaining cold blacks warmed to stone shadow" % (DECK_TOP - 1, FACADE_BLACK_MAX)],
                          "unchanged": "geometry, walk mask, blocks, props, pivots, reveal mask, interactions, labels, underpainted rows"},
        "reference": {"file": rel(REFERENCE), "sha256": REFERENCE_SHA256, "git": "untracked at build time",
                      "use": "composition, palette and material guidance; never pasted into runtime; not finished pixel art"},
        "toolchain": {"pillow": PIL.__version__, "numpy": np.__version__,
                      "note": "no median cut, k-means or RNG streams; Pillow only decodes/encodes PNG and rasterizes polygons"},
        "row_recomposition": {"facade_rows": [62, DECK_TOP - 1, "reference rows 31..63"],
                              "deck_rows": [DECK_TOP, DECK_BOTTOM, "reference rows 64..108 minus %s" % list(DECK_DROP)],
                              "below_deck": "native row = reference row + 27"},
        "underpaint_repairs": [{"box": list(b), "copied_from_dx": dx} for b, dx in REPAIRS],
        "provenance": origin_counts(layers, props),
        "canvas": [W, H], "visible_art_rows": [62, 317], "palette_colours": len(colours),
        "layers_bottom_to_top": LAYERS + [GUIDE + " (hidden, locked)"],
        "runtime_layers": [{"name": "ground-far", "from": STATIC}] + [{"name": n} for n in YSORT],
        "ysort_props": props,
        "geometry": {"walk": WALK, "blocks": BLOCKS, "spawn": SPAWN, "kiosk": KIOSK, "stair": STAIR, "pylon": PYLON,
                     "interact_radius": INTERACT_RADIUS, "deck_rows": [DECK_TOP, DECK_BOTTOM], "station_plate": PLATE},
        "hero_visibility": vis_report,
        "pixelorama": f"pxo_version 7, color_mode 5, 1 frame x {len(LAYERS) + 1} layers (guides-walkmask hidden + locked); ORA lists the same layers",
        "files": files,
        "source": rel(Path(__file__).resolve()),
    }
    path = out / f"{PREFIX}_layer-manifest_{VARIANT}_{STAMP}.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(path)
    return manifest


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":
        # Iteration aid: write only a merged preview to the given path.
        lay, pr = build_layers()
        merged(lay).save(sys.argv[2])
        print(json.dumps(visibility_report(lay, pr)[0]))
        print(json.dumps(origin_counts(lay, pr)))
        print(gd_props(pr))
    else:
        build()
