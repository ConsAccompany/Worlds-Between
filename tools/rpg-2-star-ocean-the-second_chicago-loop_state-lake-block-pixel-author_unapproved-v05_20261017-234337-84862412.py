"""Chicago Loop arrival block, State St x Lake St, native 640x360 scene (UNAPPROVED candidate v05).

v05 is one bounded material-depth pass over v04 (this file started as a copy of the v04 author tool
tools/...pixel-author_unapproved-v04_20261017-230650-c0d4b7f0.py; v04 files stay untouched).
Brief: v04 reads clear but diagrammatic and cool at 1x. Only three static backdrop layers change,
all marked "v05" below:
  * backdrop-facade-north: the far facades in warm evening haze (own terracotta, brick, limestone and
    glass ramps, none as bright as the lit station hall), sunlit upper floors over one stepped cast-shadow
    plane from a taller block west of State St, window recesses (an L of lintel and jamb shadow on the
    glass, a lit sill, a shadow row under the terracotta sills in sun, a lit east reveal on the brick),
    warm-neutral glass with pale blinds drawn in some sunlit windows, lit interiors only on the shadow
    side; State St north is one asphalt value lighter in its far half and its far crosswalk is dimmer.
  * backdrop-underdeck-storefronts: two soffit shadow rows over the fascias, back-lit letter blocks on
    lit shops (one plain plate on some dark ones), piers lit on the west face that shade the glass east
    of them, lit interiors with a dim ceiling and pendant lamps, a lit back wall brightest in the middle
    of each pane, a shelf in shadow, a counter and now and then a figure instead of one flat warm fill,
    a door rail, dark shops with one broad diagonal reflection band, two shallow awnings (green, brick
    red) with their shadow on the glass.
  * station-platform-canopy: the windbreak shows the facade behind it through its glass (two dark
    warm-neutral values by brightness) instead of one flat dark band. The roof, posts, lamps, coping and
    the head house with its lit hall and teal lintel are unchanged, so the station stays the focal point.
  Everything else (ground, light and shadow layer, deck girder, plate, every y-sort layer, walk mask,
  reveal mask, geometry, props, pivots, hero visibility) is byte-identical to v04.

v04 was one bounded scene-art pass over v03r1 (this file started as a copy of the v03r1 author tool
tools/...pixel-author_unapproved-v03r1_20261017-183235-a00fabf3.py; v03 and v03r1 files stay untouched).
Brief: Codex found the upper facade strip muddy (generator-derived) and the medallion, fountain and pylon
competing with the station. Changes, all marked "v04" below:
  * Both backdrop bands are now authored here as explicit pixel clusters; the generated style reference
    is no longer read at all (underpainted share 0). North of the L: State St continues north past the
    intersection (asphalt, lane line, far crosswalk, corner sidewalk), then three buildings with one
    regular rhythm each: a terracotta Chicago-school block with Chicago windows, a recessive brick block
    and a pale limestone block with paired windows, lit from the west like the rest of the scene.
    Under the L: the same three buildings' storefronts in the deck shadow, shop by shop, lit windows
    over the existing ground light pools.
  * The elevated station is focal: a new static layer holds the north platform canopy along the deck
    (glass roof, posts on the girder stiffener rhythm, lamps, platform edge) with a glazed head house
    and the one teal lintel straight above the State/Lake girder plate.
  * Lower competing contrast at plaza level: the Loop medallion becomes a low-contrast granite and
    bronze inlay (one segmented ring of the five line colours, bronze star, no flag-blue bars); the
    fountain, pylon and dock lose their brightest teal values (recoloured in place, same alpha); the
    pylon and dock teal ground pools are removed or smaller.
  * Unchanged and byte-identical to v03r1: geometry, blocks, walk mask, every y-sort prop region, pivot
    and alpha, the occlusion reveal mask, the deck girder, the station plate, the stair, kiosk and the
    three read-only sites. A Chicago Theatre vertical-sign cue was considered and not added: the Theatre
    (175 N State, east side, south of Lake) stands behind this north-facing camera.

The text below describes the v03 base, as corrected by v03r1 and v04.

v03 is one bounded composition pass after v02 (v02 files stay untouched as the runtime baseline).
Authored natively here, cluster by cluster with a fixed integer hash (no RNG streams): the whole
walkable ground (granite slab plaza, under-deck concrete, Loop medallion, sett bands, teal guide strip,
tree and drain grates), State St with its continental crosswalk, curb ramps and tactile pads, the L
cast shadow, the riveted deck girder, L columns, knee braces and plinths, the station stair up to the
platform, and every prop: Chicago lamp with flag banner and green street blade, planters, bench,
litter bin, teal civic kiosk, wayfinding pylon, bike-share dock, bollards, granite seats, honey
locusts, fountain, iron fence and foreground planting.
The image is split into purposeful editable layers (Pixelorama .pxo + OpenRaster .ora, same layers,
hidden locked walk-mask guide). Runtime gets the flattened static layers as one opaque PNG plus the
y-sort layer PNGs (binary alpha); each y-sort prop is a region of its layer with its own pivot row.
Geometry constants must match the v04 runtime scene script (checked in Godot and by the source check).
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
STAMP = "20261017-234337-84862412"
PREFIX = "rpg-2-star-ocean-the-second_chicago-loop_state-lake"
VARIANT = "unapproved-v05"
OUT = ROOT / "outputs" / "chicago-loop-state-lake-v05"
RUNTIME = ROOT / "game" / "assets" / "environments" / "chicago-loop-state-lake-v05"
BASE_AUTHOR = ROOT / "tools" / "rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-author_unapproved-v04_20261017-230650-c0d4b7f0.py"
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
    # v04: window and canopy glass (teal-grey, never near-black)
    "gl0": (34, 50, 54), "gl1": (58, 80, 82), "gl2": (92, 118, 116),
    # v05: far facades in warm evening haze (no value reaches the lit station hall: luma < 150 or r - b <= 40)
    # buff terracotta: recess, shadow plane, shade, sunlit body, sunlit west face
    "tc0": (74, 58, 50), "tc1": (102, 80, 66), "tc2": (130, 102, 80), "tc3": (156, 122, 92), "tc4": (176, 138, 100),
    # brick
    "bk0": (64, 42, 36), "bk1": (88, 56, 44), "bk2": (114, 74, 56), "bk3": (136, 92, 68),
    # limestone (greyer)
    "ls0": (80, 74, 68), "ls1": (106, 98, 88), "ls2": (130, 120, 106), "ls3": (152, 140, 122), "ls4": (170, 158, 138),
    # window glass in evening haze, warm-neutral: recess shadow, glass in shade, glass in sun, blind / sky glint
    "gw0": (50, 42, 42), "gw1": (72, 60, 56), "gw2": (102, 86, 74), "gw3": (134, 112, 90),
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


RAMPS = {k: [n for n in NAMES if n.startswith(k) and n[len(k):].isdigit()] for k in ("st", "pv", "as", "ir", "iw", "ru", "lt", "fo", "te", "br", "aw", "wd", "wp", "gl", "tc", "bk", "ls", "gw")}


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


# ---------------------------------------------------------------- v04: authored backdrop bands
# Rows 62..94 (north of the L) and 135..165 (under it) are painted here as explicit clusters; the
# generated style reference is not read any more. The low west sun lights west faces (piers, jambs
# facing west) and the pier throws its shadow on the recess east of it. Each building keeps one bay
# width and one floor height, so the strip reads as three facades instead of texture.
SIDEWALK_N = (83, 96)               # corner sidewalk north of Lake St, east side of State St
XWALK_N = (82, 95)                  # far crosswalk of the intersection, cut by the deck at row 95
# (name, x0, x1, bay width, floor height, row of a floor top); storefront shop width below the L
BUILDINGS = [
    ("terracotta", 96, 280, 24, 11, 52, 48),
    ("brick", 280, 424, 16, 9, 59, 48),
    ("limestone", 424, W, 32, 12, 54, 64),
]
LIT_WINDOW_SHARE = 0.22             # whole panes lit from inside, chosen per (bay, floor)


# v05: one cast-shadow line across the far plane. A taller block west of State St (off camera) shades
# the lower floors in the low west sun; the hard edge steps down one row every 36 px eastward, so the
# strip has one broad sunlit plane over one shadow plane instead of an even grid. The lit station hall
# (rows 72..80) sits inside the shadow side of that line, which keeps it the brightest place.
def canyon_row(x):
    """First shadowed row of the far facades and the corner sidewalk at column x."""
    return 70 + max(0, x - 83) // 36


def in_sun(x, y):
    return y < canyon_row(x)


def paint_state_street_north(L):
    """v05: State St north of the intersection seen through haze: the far half one asphalt value lighter,
    the far stop bar one row and the far crosswalk bars in the dim paint value with a worn top row (they
    read as the far side, not a second near crosswalk); the corner sidewalk takes the cast shadow line."""
    for y in range(62, DECK_TOP):
        far = y < 74
        for x in range(0, CURB_X):
            h = hsh(x // 2, y // 2, 11)
            L.px(x, y, ("as2" if h < 0.9 else "as3") if far else ("as1" if h < 0.9 else "as2"))
        if (y // 9) % 2 == 0 and y < XWALK_N[0] - 6:
            L.rect(14, y, 16, y + 1, "wp0")
    L.rect(0, XWALK_N[0] - 4, CURB_X, XWALK_N[0] - 3, "wp0")
    for bx in range(3, CURB_X - 4, 13):
        L.rect(bx, XWALK_N[0], bx + 7, XWALK_N[1], "wp0")
        L.hline(bx, bx + 6, XWALK_N[0], "wp1")
        L.rect(bx + 6, XWALK_N[0], bx + 7, XWALK_N[1], "as3")
    for y in range(62, DECK_TOP):
        L.px(CURB_X, y, "as1")
        L.px(CURB_X + 1, y, "ir2")
        L.px(CURB_X + 2, y, "pv6" if in_sun(CURB_X + 2, y) else "pv4")
        L.px(CURB_X + 3, y, "pv5" if in_sun(CURB_X + 3, y) else "pv3")
        L.px(CURB_X + 4, y, "pv5" if in_sun(CURB_X + 4, y) else "pv3")
        for x in range(SIDEWALK_N[0], SIDEWALK_N[1]):
            tone = "pv5" if in_sun(x, y) else "pv3"
            L.px(x, y, shift(tone, -1) if (y - 62) % 9 == 8 else tone)


# v05: each facade keeps v04's bays and floors, now with recess depth: the lintel and the pier west of a
# window shade its top row and first column, the sill is lit with a shadow row under it, and the glass
# mirrors the warm sky in its upper rows and the street below them (two broad values, no mullion lines).
def blind(b, fl, seed):
    """v05: rows of a pale blind drawn down from the head of a sunlit window (0 for most windows), so the
    grid varies in broad shapes, never per pixel."""
    h = hsh(b, fl, seed + 1)
    return 0 if h < 0.7 else (2 if h < 0.85 else 3)


def paint_terracotta(L, x0, x1, bay, fh, ft):
    """Chicago-school block in buff terracotta: one pier and spandrel value per light plane, a Chicago
    window per bay (sashes darker than the wide fixed pane in shade), a lit sill with a shadow row under it
    in sun, an L of recess shadow (lintel and pier) on the glass, now and then a pale blind."""
    for y in range(62, DECK_TOP):
        fy = (y - ft) % fh
        fl = (y - ft) // fh
        for x in range(x0, x1):
            bx = (x - x0) % bay
            b = (x - x0) // bay
            sun = in_sun(x, y)
            fixed = 8 <= bx < bay - 5
            if bx < 3 or fy in (0, 1) or fy == 10 and not sun:
                c = "tc3" if sun else "tc1"
            elif fy == 9:
                c = "tc4" if sun else "tc2"
            elif fy == 10:
                c = "tc2"
            elif fy == 2 or bx == 3:
                c = "gw0"
            elif not sun and fixed and hsh(b, fl, 141) < 0.34:
                c = "lt0" if fy == 3 else "lt1"
            elif sun and fy - 3 < blind(b, fl, 141):
                c = "gw3"
            else:
                c = "gw2" if sun else ("gw1" if fixed else "gw0")
            L.px(x, y, c)


def paint_brick(L, x0, x1, bay, fh, ft):
    """Recessive brick block behind the head house: punched windows with a shaded head and west jamb, a lit
    east reveal, a limestone sill and the shadow under it."""
    for y in range(62, DECK_TOP):
        fy = (y - ft) % fh
        fl = (y - ft) // fh
        for x in range(x0, x1):
            bx = (x - x0) % bay
            b = (x - x0) // bay
            sun = in_sun(x, y)
            if 5 <= bx <= 11 and 2 <= fy <= 6:
                if fy == 2 or bx == 5:
                    c = "gw0"
                elif not sun and hsh(b, fl, 143) < LIT_WINDOW_SHARE:
                    c = "lt0"
                elif sun and fy - 3 < blind(b, fl, 143):
                    c = "gw3"
                else:
                    c = "gw2" if sun else "gw1"
            elif fy == 7 and 4 <= bx <= 12:
                c = "ls4" if sun else "ls2"
            elif fy == 8 and 5 <= bx <= 12:
                c = "bk1" if sun else "bk0"
            elif bx == 12 and 2 <= fy <= 6:
                c = "bk3" if sun else "bk2"
            else:
                c = "bk2" if sun else "bk1"
            L.px(x, y, c)


def paint_limestone(L, x0, x1, bay, fh, ft):
    """Limestone block: pilasters lit on the west face and shaded on the east, recessed paired windows
    (lintel and jamb shadow, pale blinds now and then), a lit sill."""
    for y in range(62, DECK_TOP):
        fy = (y - ft) % fh
        fl = (y - ft) // fh
        for x in range(x0, x1):
            bx = (x - x0) % bay
            b = (x - x0) // bay
            sun = in_sun(x, y)
            win = (8 <= bx <= 13 or 20 <= bx <= 25) and 3 <= fy <= 9
            near = 7 <= bx <= 14 or 19 <= bx <= 26
            if bx < 4:
                c = ("ls4" if bx < 3 else "ls2") if sun else ("ls2" if bx < 3 else "ls0")
            elif win:
                if fy == 3 or bx in (8, 20):
                    c = "gw0"
                elif not sun and hsh(b * 2 + (bx > 16), fl, 145) < 0.3:
                    c = "lt0" if fy == 4 else "lt1"
                elif sun and fy - 4 < blind(b * 2 + (bx > 16), fl, 145):
                    c = "gw3"
                else:
                    c = "gw2" if sun else "gw1"
            elif fy == 10 and near:
                c = "ls4" if sun else "ls2"
            else:
                c = "ls3" if sun else "ls1"
            L.px(x, y, c)


FACADE_PAINTERS = {"terracotta": paint_terracotta, "brick": paint_brick, "limestone": paint_limestone}


def paint_facade_north(L):
    paint_state_street_north(L)
    for name, x0, x1, bay, fh, ft, _ in BUILDINGS:
        FACADE_PAINTERS[name](L, x0, x1, bay, fh, ft)
    for name, x0, *_ in BUILDINGS[1:]:   # party-wall seams: the taller west neighbour's shadow
        L.rect(x0, 62, x0 + 2, DECK_TOP, "tc0")
        L.vline(x0 + 2, 62, DECK_TOP, "tc1")


SHOP_SIGNS = ("aw1", "st2", "ru1", "aw0", "st3", "ru2", "iw2")
SHOP_LIT_X = (176, 288, 352, 470, 560, 616)    # over the storefront light pools on the under-deck walk
SHOP_AWNINGS = {2: ("aw2", "aw1", "aw0"), 8: ("br2", "br1", "br0")}   # v05: shop index -> canvas values


def paint_storefronts(L):
    """v05: the three buildings' shopfronts under the deck, in its shadow. Two soffit shadow rows sit over
    the fascias; lit shops carry back-lit letter blocks (some dark ones one plain plate); piers are lit on
    the west face and shade the glass east of them; lit shops show a dim ceiling with pendant lamps, a lit
    back wall, a shelf in shadow, a counter and now and then a figure instead of a flat warm fill; dark
    shops mirror one broad diagonal band; two shallow awnings shade the glass under them."""
    y0, y1 = BAND
    for y in range(y0, y1):              # corner pier at Lake St
        for x in range(CURB_X + 5, SIDEWALK_N[1]):
            L.px(x, y, "st2" if x < CURB_X + 7 else "st1")
    L.rect(SIDEWALK_N[1], y0, W, y0 + 1, "st0")
    L.rect(SIDEWALK_N[1], y0 + 1, W, y0 + 2, "st1")
    shops = []
    for name, x0, x1, *_, shop in BUILDINGS:
        for sx in range(x0, x1, shop):
            shops.append((sx, min(x1, sx + shop)))
    g0, g1 = y0 + 7, y1 - 6              # glass rows 142..159
    for i, (sx, ex) in enumerate(shops):
        lit = any(sx <= lx < ex for lx in SHOP_LIT_X)
        sign = SHOP_SIGNS[int(hsh(i, 0, 151) * len(SHOP_SIGNS))]
        L.rect(sx, y0 + 2, ex, y0 + 6, sign)               # fascia: body under the soffit shadow rows
        if lit or hsh(i, 1, 151) < 0.5:   # letter blocks: lit shops two or three back-lit words, dark shops one plate
            words = [4 + int(hsh(i, 10 + k, 151) * 6) for k in range(2 + int(hsh(i, 2, 151) * 2))] if lit else [(ex - sx) // 3]
            span = sum(words) + 2 * (len(words) - 1)
            wx = sx + (ex - sx - span) // 2
            for wlen in words:
                if wx >= sx + 3 and wx + wlen <= ex - 1:
                    L.rect(wx, y0 + 3, wx + wlen, y0 + 5, "lt2" if lit else "st4")
                wx += wlen + 2
        L.hline(sx, ex, y0 + 6, "st1")
        door = (ex - 12, ex - 4)
        glass = (sx + 3, door[0])
        panes = max(1, round((glass[1] - glass[0]) / 16))
        mulls = {glass[0] + k * (glass[1] - glass[0]) // panes for k in range(1, panes)}
        bounds = [glass[0]] + sorted(mulls) + [glass[1]]
        cores = [(a + (b_ - a) // 3, b_ - (b_ - a) // 3) for a, b_ in zip(bounds, bounds[1:])]
        lamps = [(a + b_) // 2 for a, b_ in zip(bounds, bounds[1:])]
        figure = glass[0] + 5 + int(hsh(i, 3, 151) * max(1, glass[1] - glass[0] - 12)) if lit and hsh(i, 4, 151) < 0.7 else -99
        for y in range(g0, g1):
            for x in range(sx, ex):
                lx = x - sx
                if lx < 3:
                    c = "st3" if lx == 0 else "st2"
                elif x == door[0]:
                    c = "st1"
                elif y < g0 + 2:
                    c = "gl0" if lit else "gw0"            # transom mirrors the dark deck
                elif y == g0 + 2:
                    c = "st1"                              # transom bar
                elif door[0] < x < door[1]:
                    c = "st1" if y == g0 + 10 else (("lt0" if y >= g0 + 4 else "gl0") if lit else "gw1")   # door with its rail
                elif x in mulls or lx == 3:
                    c = "st1" if x in mulls else ("wd0" if lit else "gw0")   # pier shadow on the glass
                elif lit:
                    if y >= g1 - 5:
                        c = "wd1" if y == g1 - 5 else "wd0"   # counter
                    elif figure <= x < figure + 3 and y >= g0 + 7 or figure < x < figure + 2 and g0 + 5 <= y < g0 + 7:
                        c = "iw1"                          # a figure behind the counter
                    elif y < g0 + 5:                       # dim ceiling with pendant lamps
                        c = ("lt3" if y == g0 + 3 else "lt2") if any(abs(x - lp) <= (0 if y == g0 + 3 else 1) for lp in lamps) else "lt0"
                    elif y < g0 + 10:                      # lit back wall, brightest in the middle of each pane
                        c = "lt2" if g0 + 6 <= y < g0 + 9 and any(a <= x < b_ for a, b_ in cores) else "lt1"
                    else:
                        c = "lt0"                          # display shelf in shadow above the counter
                else:
                    if y >= g1 - 5:
                        c = "gw0"
                    elif (lx + (g1 - y)) % 30 < 4:
                        c = "gw2"                          # one broad reflection band
                    else:
                        c = "gw1"
                L.px(x, y, c)
        if i in SHOP_AWNINGS:                              # shallow awning and its shadow on the glass
            top, mid, low = SHOP_AWNINGS[i]
            L.hline(sx + 3, ex, g0, top)
            L.rect(sx + 3, g0 + 1, ex, g0 + 3, mid)
            for x in range(sx + 3, ex):
                L.px(x, g0 + 3, low if (x - sx) % 4 < 3 else mid)
            for y in (g0 + 4, g0 + 5):
                for x in range(sx + 3, ex):
                    if x != door[0] and L.get(x, y) != PAL["st1"]:
                        L.px(x, y, "gw0")
        L.rect(sx, y1 - 6, ex, y1, "st2")                  # bulkhead as v04
        L.hline(sx, ex, y1 - 6, "st3")
        L.hline(sx, ex, y1 - 1, "st1")
        L.vline(sx, y1 - 6, y1, "st3")


CANOPY = (150, 540)                 # north platform canopy along the deck
HEAD = (286, 366)                   # glazed head house centred over the State/Lake plate (PLATE 296..356)
CANOPY_POSTS = [x for x in range(14, W, 32) if CANOPY[0] < x < CANOPY[1] - 2]   # girder stiffener rhythm


def through_glass(n):
    """v05: a facade colour seen through the dark windbreak glass: two glass values by brightness."""
    r, g, b = PAL[n]
    return "gw1" if (r * 299 + g * 587 + b * 114) // 1000 >= 112 else "gw0"


def draw_platform_canopy(L, facade=None):
    """The State/Lake north platform: a lit coping right above the track deck, a windbreak (v05: the
    facade behind shows through its dark glass, under one roof-shadow row), posts on the girder stiffener
    rhythm, a teal glass roof with a warm fascia and lamps, and a glazed head house whose lit hall and
    teal lintel are the brightest place of the strip (unchanged from v04)."""
    x0, x1 = CANOPY
    L.rect(x0, 76, x1, 80, "te1")                     # glass roof, glazing bars on the posts
    L.hline(x0, x1, 76, "iw4")
    L.hline(x0, x1, 80, "ru2")                        # sunlit fascia
    L.rect(x0, 81, x1, 90, "gl0")                     # windbreak glass under the roof
    if facade is not None:
        for y in range(82, 90):
            for x in range(x0, x1):
                L.px(x, y, through_glass(name_of(facade.get(x, y))))
    L.hline(x0, x1, 90, "st5")                        # platform coping and face
    L.rect(x0, 91, x1, DECK_TOP, "st3")
    for px_ in CANOPY_POSTS:
        L.vline(px_, 77, 80, "iw2")
        L.rect(px_, 81, px_ + 2, 90, "iw1")
        L.vline(px_, 81, 90, "iw3")
    for px_ in CANOPY_POSTS[1::2]:                    # lamps under the fascia
        L.rect(px_ + 13, 81, px_ + 18, 83, "lt2")
        L.hline(px_ + 14, px_ + 17, 81, "lt3")
    for x in (x0, x1 - 2):                            # end frames
        L.rect(x, 76, x + 2, 91, "iw2")
        L.vline(x, 76, 91, "iw3")
    h0, h1 = HEAD
    L.rect(h0, 64, h1, 72, "gl1")                     # head house: sky in the upper glass,
    L.rect(h0, 72, h1, 80, "lt2")                     # the lit station hall below the transom
    for x in range(h0 + 15, h1 - 10, 20):             # hall lamps
        L.rect(x, 73, x + 6, 75, "lt3")
    L.hline(h0, h1, 64, "iw4")
    L.rect(h0, 65, h1, 68, "te2")                     # teal lintel
    L.hline(h0 + 2, h1 - 2, 66, "te3")
    L.hline(h0, h1, 72, "iw2")
    for x in range(h0 + 20, h1 - 4, 20):
        L.vline(x, 68, 80, "iw2")
    L.rect(h0, 64, h0 + 2, 81, "iw3")
    L.rect(h1 - 2, 64, h1, 81, "iw1")
    L.hline(h0, h1, 80, "ru2")


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
    """v04: a low-contrast inlay instead of a bright target. Setts one step apart (was three), a darker
    bronze ring, a mid granite field, one ring of five short line-colour segments broken at the south,
    and a bronze star on a slightly lighter disc; no flag-blue bars."""
    cx, cy, rx, ry = MEDALLION
    yy, xx = np.mgrid[0:H, 0:W]
    outer = ellipse(cx, cy, rx, ry)
    setts = outer & ~ellipse(cx, cy, rx - 4, ry - 2)
    for y, x in zip(*np.nonzero(setts)):
        g.px(x, y, "pv3" if (x // 4 + y // 2) % 2 else "pv2")
    bronze = ellipse(cx, cy, rx - 4, ry - 2) & ~ellipse(cx, cy, rx - 6, ry - 3)
    g.mask(bronze & (yy >= cy), "ru1")
    g.mask(bronze & (yy < cy), "ru2")
    g.mask(ellipse(cx, cy, rx - 6, ry - 3), "pv4")
    ang = np.arctan2((yy + 0.5 - cy) * rx / ry, xx + 0.5 - cx)
    k = rx - 13
    ring = ellipse(cx, cy, k, k * ry / rx) & ~ellipse(cx, cy, k - 1.4, (k - 1.4) * ry / rx)
    ring &= ~((ang > 1.2) & (ang < 1.95))
    seg = ((ang + np.pi) / (2 * np.pi) * 10).astype(int) % 10    # ten arcs: five colours, five gaps
    for i, c in enumerate(["loop_brown", "loop_green", "loop_orange", "loop_pink", "loop_purple"]):
        g.mask(ring & (seg == i * 2), c)
    g.mask(ring & (seg % 2 == 1), "ru1")
    g.mask(ellipse(cx, cy, 12, 4.4), "pv5")
    star = [(0, -3), (-1, -2), (0, -2), (1, -2), (-3, -1), (-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1), (3, -1),
            (-1, 0), (0, 0), (1, 0), (-3, 1), (-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1), (3, 1), (-1, 2), (0, 2), (1, 2), (0, 3)]
    for dx, dy in star:
        g.px(cx + dx, cy + dy, "ru3" if dy < 0 else "ru2")


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


TEAL_POOLS = [(432, 205, 14, 4), (364, 300, 24, 2), (574, 210, 18, 4), (574, 214, 10, 3)]   # v04: no pylon pool, smaller dock pool


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


# v04: quieter teal on the fictional plaza props. Each map recolours a painted prop in place (same
# opaque pixels, so regions, pivots, occlusion and the reveal mask stay byte-identical to v03r1).
MUTE_FOUNTAIN = {"te5": "te3", "te4": "te2", "te3": "te2"}
MUTE_PYLON = {"te5": "te3", "te4": "te2", "te3": "te2"}
MUTE_DOCK = {"te5": "te3", "te4": "te3"}


def muted(painter, mapping):
    def paint(L):
        P = Layer()
        painter(P)
        op = P.opaque()
        for y, x in zip(*np.nonzero(op)):
            n = name_of(P.a[y, x, :3])
            if n in mapping:
                P.px(x, y, mapping[n])
        L.a[op] = P.a[op]
    return paint


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
        ("fountain", muted(draw_fountain, MUTE_FOUNTAIN), 297.5),
        ("planter-column-west", lambda L: draw_planter_iron(L, 100, 122, 236, 251, 51, (("fl_p", 4),)), 261.5),
        ("planter-column-east", lambda L: draw_planter_iron(L, 488, 510, 236, 251, 53, (("fl_w", 4),)), 261.5),
        *[("bollard-%d" % y, (lambda yy: lambda L: draw_bollard(L, yy))(y), y + 0.5) for y in BOLLARD_ROWS],
        ("wayfinding-pylon", muted(draw_pylon, MUTE_PYLON), 232.5),
        ("granite-seat-west", lambda L: draw_seat(L, 232), 265.5),
        ("granite-seat-east", lambda L: draw_seat(L, 372), 265.5),
        ("honey-locust-west", lambda L: draw_honey_locust(L, 198, 101), 293.5),
        ("honey-locust-east", lambda L: draw_honey_locust(L, 432, 103), 293.5),
        ("bike-share-dock", muted(draw_bike_dock, MUTE_DOCK), 297.5),
    ]),
    ("ysort-foreground", [
        ("south-parapet-fence", draw_foreground, 340.5),
    ]),
]

# ---------------------------------------------------------------- layers
STATIC = ["ground-street-plaza", "ground-shadow-light", "backdrop-facade-north", "station-platform-canopy",
          "backdrop-deck-l-girder", "backdrop-underdeck-storefronts", "station-plate"]
YSORT = [name for name, _ in PROP_GROUPS]
LAYERS = STATIC + YSORT
GUIDE = "guides-walkmask"
BAND = (DECK_BOTTOM + 1, 166)       # storefront rows under the deck (v04: authored, see paint_storefronts)
PLATE = (296, 112, 356, 123)        # State/Lake station plate on the girder web; text is a runtime label
COLUMN_X = (140, 474)
GIRDER_LAMPS = (60, 236, 396, 572)

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
    g = Layer()
    paint_road(g)
    paint_underdeck_walk(g)
    paint_plaza(g)
    paint_medallion(g)
    paint_grates(g)
    paint_markers(g)
    g.rect(0, 0, W, 62, "ui")
    layers = {"ground-street-plaza": g, "ground-shadow-light": ground_shading(g)}
    facade, canopy, deck, band = Layer(), Layer(), Layer(), Layer()
    facade.rect(0, 0, W, 62, "ui")
    paint_facade_north(facade)          # v04: authored, no underpainting
    draw_platform_canopy(canopy, facade)   # v05: the windbreak shows the facade through its glass
    draw_deck(deck)
    paint_storefronts(band)
    layers.update({"backdrop-facade-north": facade, "station-platform-canopy": canopy, "backdrop-deck-l-girder": deck,
                   "backdrop-underdeck-storefronts": band})
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


ZIP_TIME = (2026, 10, 17, 23, 43, 36)


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
                      "file_format": "0", "file_name": json.dumps("chicago-loop-state-lake-v05"),
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


UNDERPAINTED_LAYERS = ()   # v04: none (v03/v03r1 underpainted the facade and storefront bands)


def origin_counts(layers, props):
    """Visible-pixel provenance of the merged image: underpainted backdrop vs authored."""
    under = np.zeros((H, W), bool)
    for name in UNDERPAINTED_LAYERS:
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
    pal_text = "GIMP Palette\nName: chicago-loop-state-lake-v05\nColumns: 16\n#\n" + "".join(
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
        "status": "UNAPPROVED candidate v05 (one bounded material-depth pass over v04), test-harness opt-in only (the runtime Loop .tscn is not wired to it; default stays v02) for Codex visual QA and creator review; counters unchanged (40.8%, M2 10/12, scenes 3/12, sprites 0/52, playtests 0/2)",
        "canon": ("The exact intersection, the pedestrian Lake St plaza, the medallion, the stair position, the terrace, the three "
                  "north-side buildings and the platform canopy are art-pilot choices, not creator-approved landmarks or a claim "
                  "about the 2537 station. The medallion, fountain, kiosk and pylon are fictional scene design."),
        "authorship": ("Every pixel is authored in this tool as explicit clusters with a fixed integer hash: the ground, the deck girder, "
                       "both backdrop bands (State St north, three facades, storefronts), the platform canopy, columns, stair and props. "
                       "The generated style reference used by v03/v03r1 is not read. Built by Claude (Claude Code, signed-in Claude Max, firstParty)."),
        "pass_of": {"base_author": rel(BASE_AUTHOR), "base_author_sha256_text_lf": text_sha(BASE_AUTHOR.read_bytes()),
                    "changes": ["backdrop-facade-north: warm haze ramps (terracotta, brick, limestone, warm-neutral glass), sunlit upper floors "
                                "over one stepped cast-shadow plane, window recesses (lintel and jamb shadow, lit sills), pale blinds in some "
                                "sunlit windows, lit interiors only on the shadow side, hazier State St north and a dimmer far crosswalk",
                                "backdrop-underdeck-storefronts: soffit shadow rows, back-lit letter blocks, lit interiors in several values "
                                "(dim ceiling and pendant lamps, lit back wall, shelf in shadow, counter, figures), door rails, one diagonal "
                                "reflection band on dark shops, two shallow awnings with their shadow",
                                "station-platform-canopy: the windbreak shows the facade through its glass (two dark warm-neutral values); "
                                "roof, posts, lamps, coping and head house unchanged"],
                    "unchanged": ("ground and its light and shadow layer, deck girder, plate, every y-sort layer (regions, pivots, alpha "
                                  "and colour), walk mask, reveal mask, geometry, interactions, labels: byte-identical to v04")},
        "reference": {"read": False, "note": "v05, like v04, does not open the nonruntime style reference that v03/v03r1 underpainted from"},
        "theatre_cue": ("Considered, not added: the Chicago Theatre (175 N State St, east side of State, south of Lake St) stands behind "
                        "this north-facing camera; a vertical sign north of the L would invert the geography."),
        "toolchain": {"pillow": PIL.__version__, "numpy": np.__version__,
                      "note": "no median cut, k-means or RNG streams; Pillow only decodes/encodes PNG and rasterizes polygons"},
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
