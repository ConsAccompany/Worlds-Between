"""Washington, D.C. survey annex room 2 (记录内室 / Records Chamber), UNAPPROVED v01 physical fixtures.

Three clue fixtures at the existing room-2 clue sites (scifi.ruins:3/4/5) and one analysis table at the
unchanged research-terminal site, drawn pixel by pixel in this tool: no generated image, no underpainting,
no resampling, no filtering. The room background (the m8-concept plate) is NOT repainted or touched.

- 机器译文 / Machine Translation (clue 3): a broken sandstone fragment with incised glyph rows rests in a
  felt-lined timber cradle; a field translator on a tripod scans one worn glyph group, which it boxes
  in teal on the stone and in amber on its screen beside a mostly empty (low) confidence bar.
- 平行铭文 / Parallel Inscription (clue 4): a dark basalt tablet with two parallel incised registers,
  braced by timber props and bronze edge brackets on a sandstone plinth; one glyph group in each
  register is marked by a teal bracket and a clip tag for comparison.
- 擦除标题 / Erased Heading (clue 5): a broken patinated bronze plaque on a sandstone pedestal; its heading
  band is scraped through the patina to raw metal with criss-cross abrasion and only stray stroke
  stubs, the body rows below are intact; the broken corner lies on the floor.
- 研判终端 / Analysis console (unchanged terminal site): a low field light-table at the near floor edge
  with a specimen shard, a brass magnifier arm, a small readout and a power case.

No glyph is a real character or word: glyph marks are abstract 3x3 stroke cells from a fixed set.
Writes merged PNG, layered .ora and Pixelorama .pxo (pxo_version 7) for every asset, a manifest with
sha256 hashes, placement and feet footprints, and runtime copies. --preview DIR writes previews only.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import io
import json
import random
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261018-001157-151fb8d0"
PREFIX = "rpg-2-star-ocean-the-second_wdc-annex-room2"
OUT = ROOT / "outputs/wdc-rc2-v01_151fb8d0"
RUNTIME_PROP_DIR = ROOT / "game/assets/props/wdc-annex-room2"
BACKGROUND = ROOT / "game/assets/environments/rpg-2-star-ocean-the-second_scifi-ruins-survey-annex-room-02_environment-background_m8-concept_20261014-143300-042ae336.png"
PIXELORAMA_VERSION = "v1.2.3-stable"

# Placement (screen px, 640x360). Clue sites and the terminal site are the room's existing constants.
CLUES = [(163, 165), (320, 165), (477, 165)]
TERMINAL = (320, 263)
CW, CH = 96, 72            # clue fixture canvas
CLUE_ORIGIN_Y = 164        # canvas row 0 on screen; the marker disc (y 149-181) floats over the fixture tops
CLUE_SORT_ROW = 54         # y-sort line (screen y 218) inside the feet footprint
TW, TH = 96, 40            # terminal canvas
TERMINAL_ORIGIN = (272, 278)

P = {
    "ink": "#1e1712",
    "ss0": "#3b2c1f", "ss1": "#5a4430", "ss2": "#7a5e42", "ss3": "#9a7a56", "ss4": "#b9976c", "ss5": "#d4b689", "ss6": "#ead2a6",
    "bs0": "#161a19", "bs1": "#262c2a", "bs2": "#37403c", "bs3": "#4c5751", "bs4": "#677369", "bs5": "#8b978b",
    "br0": "#2e2210", "br1": "#4f3a1a", "br2": "#755527", "br3": "#9c7535", "br4": "#c49a4e", "br5": "#e6c47a", "br6": "#fbe6ac",
    "vd0": "#24473e", "vd1": "#386b5c", "vd2": "#56927c", "vd3": "#80b8a0",
    "wd0": "#25170e", "wd1": "#3e2817", "wd2": "#5c3c22", "wd3": "#7d5531", "wd4": "#a07043",
    "fe0": "#3a2422", "fe1": "#57352e",
    "st0": "#1a1f22", "st1": "#2f383d", "st2": "#4a565c", "st3": "#6e7c82", "st4": "#9fadb0", "st5": "#cdd7d6",
    "tl0": "#0d2628", "tl1": "#174443", "tl2": "#236863", "tl3": "#3c968c", "tl4": "#72cbbd", "glow": "#c9fbee",
    "am": "#e0a03a", "am0": "#8a5a1c", "rd": "#c44a3a",
    "pp0": "#8f8068", "pp1": "#c6b693", "pp2": "#e9ddbf",
}
RGB = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in P.items()}
SHADOW_CORE = (26, 17, 10, 0xA8)
SHADOW_EDGE = (26, 17, 10, 0x5C)

CLUE_LAYERS = ["contact-shadow", "structure", "form-and-light", "inscription-and-wear", "survey-equipment", "teal-light"]
TERMINAL_LAYERS = ["contact-shadow", "structure", "form-and-light", "specimen-and-cables", "teal-light"]

# Abstract glyph cells (3x3 strokes). They are not characters of any script and spell nothing.
GLYPHS = ["111/1../111", "1.1/111/1.1", "11./.1./.11", "1../111/..1", "111/.1./1.1", "1.1/.1./111",
          "11./1.1/.11", ".1./111/.1.", "1.1/1.1/111", "111/..1/11."]


# ---------------------------------------------------------------- pixel helpers (numpy RGBA)

def layer(w, h):
    return np.zeros((h, w, 4), np.uint8)


def put(a, x, y, c):
    if 0 <= x < a.shape[1] and 0 <= y < a.shape[0]:
        a[y, x] = (*RGB[c], 255)


def box(a, x0, y0, x1, y1, c):
    """Filled inclusive rectangle."""
    h, w = a.shape[:2]
    x0, x1 = max(0, min(x0, x1)), min(w - 1, max(x0, x1))
    y0, y1 = max(0, min(y0, y1)), min(h - 1, max(y0, y1))
    if x0 <= x1 and y0 <= y1:
        a[y0:y1 + 1, x0:x1 + 1] = (*RGB[c], 255)


def seg(a, pts, c, width=1):
    img = Image.new("L", (a.shape[1], a.shape[0]), 0)
    ImageDraw.Draw(img).line(pts, fill=255, width=width)
    a[np.array(img) > 0] = (*RGB[c], 255)


def poly_mask(pts, w, h):
    img = Image.new("L", (w, h), 0)
    ImageDraw.Draw(img).polygon(pts, fill=255)
    return np.array(img) > 0


def ellipse_mask(bb, w, h):
    img = Image.new("L", (w, h), 0)
    ImageDraw.Draw(img).ellipse(bb, fill=255)
    return np.array(img) > 0


def fill(a, mask, c):
    a[mask] = (*RGB[c], 255)


def ring(mask):
    """Pixels just outside mask (4-neighbourhood)."""
    grow = mask.copy()
    grow[1:] |= mask[:-1]
    grow[:-1] |= mask[1:]
    grow[:, 1:] |= mask[:, :-1]
    grow[:, :-1] |= mask[:, 1:]
    return grow & ~mask


def top_edge(mask):
    m = mask.copy()
    m[1:] &= ~mask[:-1]
    return m


def left_edge(mask):
    m = mask.copy()
    m[:, 1:] &= ~mask[:, :-1]
    return m


def right_edge(mask):
    m = mask.copy()
    m[:, :-1] &= ~mask[:, 1:]
    return m


def bottom_edge(mask):
    m = mask.copy()
    m[:-1] &= ~mask[1:]
    return m


def shadow(a, core_bb, pad=(3, 2)):
    h, w = a.shape[:2]
    core = ellipse_mask(core_bb, w, h)
    edge = ellipse_mask((core_bb[0] - pad[0], core_bb[1] - pad[1], core_bb[2] + pad[0], core_bb[3] + pad[1]), w, h) & ~core
    a[edge] = SHADOW_EDGE
    a[core] = SHADOW_CORE


def glyph(a, x, y, index, groove, lip=None, keep=None, rng=None, wear=0.0):
    """An incised abstract glyph cell: groove pixels, with an optional lip under each stroke. With wear > 0
    some stroke pixels are left out so the marks read as cut, weathered stone rather than print."""
    rows = GLYPHS[index % len(GLYPHS)].split("/")
    for j, row in enumerate(rows):
        for i, v in enumerate(row):
            if v != "1" or (keep is not None and not keep(x + i, y + j)):
                continue
            if rng is not None and rng.random() < wear:
                continue
            put(a, x + i, y + j, groove)
            if lip and (j == 2 or rows[j + 1][i] != "1"):
                put(a, x + i, y + j + 1, lip)


def glyph_row(a, x0, x1, y, rng, groove, lip=None, keep=None, wear=0.0):
    """A row of abstract glyph cells separated by 1 px, with occasional 2 px gaps."""
    x = x0
    while x + 2 <= x1:
        glyph(a, x, y, rng.randrange(len(GLYPHS)), groove, lip, keep, rng, wear)
        x += 4 + (1 if rng.random() < 0.28 else 0)


def bracket(a, x0, y0, x1, y1, c, arm=2):
    """Corner brackets (survey marks) around a rectangle."""
    for cx, cy, dx, dy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        for k in range(arm + 1):
            put(a, cx + dx * k, cy, c)
            put(a, cx, cy + dy * k, c)


# ---------------------------------------------------------------- 机器译文 / Machine Translation

def fixture_machine_translation():
    w, h = CW, CH
    sh, st, fo, ins, eq, tl = (layer(w, h) for _ in range(6))
    shadow(sh, (5, 55, 56, 64))
    shadow(sh, (57, 58, 92, 65))
    yy, xx = np.mgrid[0:h, 0:w]

    # felt-lined timber cradle: back rim and felt seen from above, a two-plank front, brass corners, feet
    box(st, 7, 42, 52, 60, "ink")
    box(st, 8, 43, 51, 44, "wd3")
    box(st, 8, 45, 51, 47, "fe0")
    box(st, 8, 48, 51, 58, "wd3")
    box(st, 8, 54, 51, 58, "wd2")
    box(st, 9, 59, 12, 61, "wd1")
    box(st, 47, 59, 50, 61, "wd1")
    box(st, 8, 61, 12, 61, "ink")
    box(st, 46, 61, 51, 61, "ink")
    box(fo, 8, 43, 51, 43, "wd4")
    box(fo, 8, 45, 51, 45, "fe1")
    box(fo, 8, 48, 51, 48, "wd4")
    box(fo, 8, 53, 51, 53, "wd1")
    box(fo, 8, 58, 51, 58, "wd1")
    box(fo, 8, 49, 8, 57, "wd4")
    box(fo, 51, 49, 51, 58, "wd1")
    for x in (19, 33, 44):
        put(fo, x, 50, "wd2")
        put(fo, x + 3, 56, "wd1")
    for x0 in (8, 48):
        box(eq, x0, 48, x0 + 3, 50, "br3")
        put(eq, x0 + (0 if x0 == 8 else 3), 48, "br5")
        put(eq, x0 + 1, 49, "br1")

    # the original fragment: a broken sandstone slab leaning back in the cradle (its foot hidden by the front plank)
    frag = poly_mask([(12, 26), (15, 21), (20, 22), (24, 17), (30, 18), (34, 14), (40, 16), (45, 21), (47, 27),
                      (46, 33), (48, 39), (47, 47), (12, 47), (11, 39), (13, 32)], w, h)
    frag &= yy <= 47
    fill(st, ring(frag) & (yy <= 47) & (yy >= 12), "ink")
    fill(st, frag, "ss4")
    # stone thickness: the broken top edge reads as a 2 px lit top surface, the right edge as the shaded side
    top1 = top_edge(frag)
    top2 = top_edge(frag & ~top1)
    fill(fo, top1, "ss6")
    fill(fo, top2, "ss5")
    re1 = right_edge(frag) & ~top1
    re2 = right_edge(frag & ~right_edge(frag)) & ~top1 & ~top2
    fill(fo, re1, "ss1")
    fill(fo, re2, "ss2")
    fill(fo, left_edge(frag) & ~top1 & ~top2, "ss5")
    # weathering: the face darkens toward the cradle, a shadow under the broken top, pits and a crack
    face = frag & ~top1 & ~top2 & ~re1 & ~re2
    fill(fo, face & (yy >= 40), "ss3")
    fill(fo, face & (yy >= 45), "ss2")
    fill(fo, top_edge(frag & ~top1 & ~top2) & ~re1 & ~re2, "ss3")
    rng = random.Random(0xF4A6)
    for _ in range(34):
        x, y = rng.randrange(13, 46), rng.randrange(20, 44)
        if face[y, x]:
            put(fo, x, y, rng.choice(("ss3", "ss3", "ss5")))
    seg(fo, [(41, 17), (39, 22), (41, 26)], "ss1")
    seg(fo, [(42, 18), (40, 22)], "ss5")
    # incised glyph rows; the worn group (row 2, centre) is left as faint, broken strokes
    worn = (24, 31, 34, 36)  # x0, y0, x1, y1 of the blurred word

    def on_face(x, y):
        return bool(frag[y, x]) and not (top1[y, x] or top2[y, x] or re1[y, x] or re2[y, x])

    def legible(x, y):
        return on_face(x, y) and not (worn[0] <= x <= worn[2] and worn[1] <= y <= worn[3])

    for y, x0, x1 in ((24, 16, 43), (30, 14, 44), (36, 14, 45), (41, 14, 44)):
        glyph_row(ins, x0, x1, y, rng, "ss1" if y < 40 else "ss0", None, legible, wear=0.22)
    # the blurred word: shallow, pitted, partly missing strokes
    for x, y in [(25, 32), (26, 32), (27, 33), (29, 32), (29, 34), (30, 33), (32, 32), (32, 34), (33, 33), (26, 35)]:
        put(ins, x, y, "ss2")
    for x, y in [(24, 34), (28, 35), (31, 35), (34, 32), (27, 31)]:
        put(ins, x, y, "ss3")
    # a chip broken off the lower left corner, lying in the felt
    box(ins, 14, 46, 16, 47, "ss3")
    put(ins, 14, 46, "ss5")

    # field translator on a short tripod: lens head aimed at the worn group, screen toward the viewer
    for foot in ((60, 62), (71, 63), (80, 60)):
        seg(eq, [(71, 39), foot], "st1")
    seg(fo, [(71, 40), (61, 61)], "st3")
    seg(fo, [(72, 40), (72, 62)], "st2")
    for fx, fy in ((60, 62), (71, 63), (80, 60)):
        put(eq, fx, fy, "ink")
    box(eq, 69, 36, 73, 39, "st1")
    put(fo, 69, 36, "st3")
    # body: top face, front face, darker right side, carry handle
    box(st, 59, 19, 85, 36, "ink")
    box(st, 60, 20, 84, 21, "st4")
    box(st, 60, 22, 84, 35, "st2")
    box(st, 83, 22, 84, 35, "st1")
    seg(eq, [(64, 19), (65, 16), (78, 16), (79, 19)], "st1")
    seg(fo, [(65, 16), (78, 16)], "st3")
    box(fo, 60, 20, 84, 20, "st5")
    box(fo, 60, 22, 60, 35, "st3")
    box(fo, 61, 35, 84, 35, "st1")
    # scanner head on the left side
    box(st, 52, 25, 59, 31, "ink")
    box(st, 53, 26, 59, 30, "st2")
    box(fo, 53, 26, 59, 26, "st4")
    box(fo, 53, 30, 59, 30, "st1")
    box(eq, 52, 27, 53, 29, "st0")
    # screen: two rows of glyph marks, the worn group boxed in amber, a confidence bar with two of twelve lit
    box(st, 63, 23, 81, 33, "st0")
    box(tl, 64, 24, 80, 32, "tl0")
    for x in range(65, 80, 2):
        put(tl, x, 25, "tl2" if x % 4 else "tl3")
    for x in (65, 67, 68, 77, 79):
        put(tl, x, 28, "tl2")
    bracket(tl, 70, 27, 75, 29, "am", 1)
    put(tl, 72, 28, "am0")
    put(tl, 73, 28, "am0")
    box(tl, 65, 31, 76, 31, "tl1")
    box(tl, 65, 31, 66, 31, "am")
    put(tl, 79, 31, "tl1")
    # status lights and lens
    put(tl, 82, 23, "tl4")
    put(eq, 82, 25, "am")
    put(tl, 52, 28, "tl4")
    put(tl, 52, 27, "glow")
    # faint scan rays and a teal reticle projected on the stone around the worn group
    for x, y in [(50, 29), (48, 30), (46, 31), (50, 27), (48, 26), (46, 26)]:
        put(tl, x, y, "tl3")
    bracket(tl, worn[0] - 1, worn[1] - 1, worn[2] + 1, worn[3], "tl4", 1)
    # cable to a small power case on the floor
    seg(eq, [(84, 34), (88, 42), (89, 52)], "st1")
    box(st, 83, 52, 93, 60, "ink")
    box(st, 84, 53, 92, 54, "st3")
    box(st, 84, 55, 92, 59, "st2")
    box(fo, 84, 53, 92, 53, "st4")
    box(fo, 92, 55, 92, 59, "st1")
    put(tl, 86, 57, "tl4")
    put(eq, 88, 57, "am")
    return [sh, st, fo, ins, eq, tl]


# ---------------------------------------------------------------- 平行铭文 / Parallel Inscription

def fixture_parallel_inscription():
    w, h = CW, CH
    sh, st, fo, ins, eq, tl = (layer(w, h) for _ in range(6))
    shadow(sh, (12, 55, 84, 65))
    yy, xx = np.mgrid[0:h, 0:w]

    # timber braces behind the tablet, feet on the floor at both sides
    seg(st, [(30, 20), (15, 60)], "wd2", 3)
    seg(st, [(66, 20), (81, 60)], "wd2", 3)
    seg(fo, [(29, 20), (14, 59)], "wd4")
    seg(fo, [(67, 21), (82, 60)], "wd1")
    for fx in (13, 80):
        box(st, fx, 59, fx + 3, 61, "wd1")
        box(st, fx, 62, fx + 3, 62, "ink")

    # sandstone plinth: an overhanging moulded cap (lit top, shadow line under it) on a dressed block
    box(st, 19, 46, 77, 52, "ink")
    box(st, 22, 52, 74, 62, "ink")
    box(st, 20, 47, 76, 49, "ss5")
    box(st, 20, 50, 76, 51, "ss4")
    box(st, 23, 52, 73, 61, "ss3")
    box(fo, 20, 47, 76, 47, "ss6")
    box(fo, 20, 51, 76, 51, "ss2")
    box(fo, 23, 52, 73, 52, "ss1")
    box(fo, 23, 53, 23, 61, "ss4")
    box(fo, 72, 53, 73, 61, "ss2")
    box(fo, 24, 61, 71, 61, "ss2")
    box(fo, 48, 53, 48, 60, "ss2")
    for x, y in [(30, 56), (31, 56), (45, 58), (58, 55), (64, 58), (66, 58), (38, 54), (76, 49), (20, 50)]:
        put(fo, x, y, "ss2")
    for x, y in [(27, 55), (52, 57), (61, 54), (49, 55)]:
        put(fo, x, y, "ss4")
    # grit and chips around the foot
    for x, y in [(18, 61), (21, 62), (75, 62), (78, 61), (25, 63), (70, 63)]:
        put(eq, x, y, "ss4" if (x + y) % 2 else "ss2")

    # basalt tablet with a broken upper-right corner; 2 px top surface and a 3 px shaded right side
    slab = poly_mask([(28, 11), (31, 8), (56, 8), (60, 11), (63, 9), (66, 14), (66, 50), (28, 50)], w, h)
    fill(st, ring(slab) & (yy <= 50), "ink")
    fill(st, slab, "bs3")
    t1 = top_edge(slab)
    t2 = top_edge(slab & ~t1)
    fill(fo, t1, "bs5")
    fill(fo, t2, "bs4")
    side = slab & (xx >= 64)
    fill(fo, side & ~t1, "bs1")
    fill(fo, slab & (xx == 63) & ~t1 & ~t2, "bs2")
    fill(fo, left_edge(slab) & ~t1, "bs4")
    # broken corner: raw paler stone in the break
    for x, y in [(60, 11), (61, 10), (62, 10), (61, 11), (63, 11), (64, 12)]:
        put(fo, x, y, "bs5")
    # the tablet sits in a slot in the plinth top
    box(fo, 27, 49, 67, 50, "ink")
    box(fo, 27, 51, 67, 51, "ss2")
    # face: inner field slightly darker, two parallel registers with a divider
    box(fo, 31, 13, 61, 47, "bs2")
    box(ins, 46, 13, 46, 47, "bs0")
    box(ins, 47, 13, 47, 47, "bs4")
    rng = random.Random(0x7AB1)
    rows = list(range(15, 46, 5))
    for i, y in enumerate(rows):
        glyph_row(ins, 32, 45, y, rng, "bs0", "bs3", wear=0.12)
        glyph_row(ins, 49, 62, y, rng, "bs0", "bs3", wear=0.12)
    # the compared pair: similar but not identical groups on the same row in each register
    y = rows[3]
    box(ins, 32, y, 45, y + 3, "bs2")
    box(ins, 49, y, 62, y + 3, "bs2")
    for x, gi in ((34, 1), (38, 6), (41, 3)):
        glyph(ins, x, y, gi, "bs0", "bs5")
    for x, gi in ((51, 1), (55, 6), (58, 9)):
        glyph(ins, x, y, gi, "bs0", "bs5")
    bracket(tl, 33, y - 1, 44, y + 3, "tl4", 1)
    bracket(tl, 50, y - 1, 61, y + 3, "tl4", 1)
    # chipped and weathered spots
    for x, y2 in [(33, 41), (60, 18), (40, 22), (53, 38), (36, 12)]:
        put(ins, x, y2, "bs4")
    # bronze edge brackets bolting the tablet to the braces
    for bx, by in ((26, 18), (26, 38), (65, 18), (65, 38)):
        box(eq, bx, by, bx + 3, by + 4, "br2")
        box(eq, bx, by, bx + 3, by, "br4")
        put(eq, bx + 1, by + 2, "br5")
        put(eq, bx + 2, by + 4, "br1")
    for bx, by in ((26, 22), (65, 42)):
        put(eq, bx + 1, by, "vd2")
    # teal clip tags hanging from the edge brackets beside the compared row
    for tx in (24, 69):
        box(eq, tx, y - 2, tx + 2, y + 3, "st1")
        box(tl, tx, y - 1, tx + 2, y + 2, "tl3")
        put(tl, tx + 1, y, "glow")
    return [sh, st, fo, ins, eq, tl]


# ---------------------------------------------------------------- 擦除标题 / Erased Heading

def fixture_erased_heading():
    w, h = CW, CH
    sh, st, fo, ins, eq, tl = (layer(w, h) for _ in range(6))
    shadow(sh, (14, 54, 78, 64))
    shadow(sh, (74, 58, 92, 64), pad=(2, 1))
    yy, xx = np.mgrid[0:h, 0:w]

    # sandstone pedestal: an overhanging moulded cap with a slot, a dressed block below
    box(st, 18, 42, 74, 48, "ink")
    box(st, 21, 48, 71, 62, "ink")
    box(st, 19, 43, 73, 45, "ss5")
    box(st, 19, 46, 73, 47, "ss4")
    box(st, 22, 48, 70, 61, "ss3")
    box(fo, 19, 43, 73, 43, "ss6")
    box(fo, 19, 47, 73, 47, "ss2")
    box(fo, 22, 48, 70, 48, "ss1")
    box(fo, 22, 49, 22, 61, "ss4")
    box(fo, 69, 49, 70, 61, "ss2")
    box(fo, 23, 61, 68, 61, "ss2")
    box(fo, 23, 55, 68, 55, "ss2")
    for x, y in [(29, 52), (41, 58), (57, 52), (63, 58), (35, 57), (73, 46), (19, 46)]:
        put(fo, x, y, "ss2")
    for x, y in [(33, 51), (52, 58), (60, 51)]:
        put(fo, x, y, "ss4")

    # bronze plaque standing in the slot; the upper-right corner is broken away along a jagged line
    plaque = poly_mask([(23, 10), (57, 10), (59, 12), (62, 12), (63, 15), (66, 16), (66, 19), (69, 20), (70, 23),
                        (73, 24), (73, 45), (23, 45)], w, h)
    fill(st, ring(plaque) & (yy <= 45), "ink")
    fill(st, plaque, "br2")
    # cast frame and plate thickness: a 2 px lit top surface, a 2 px shaded right side
    inner = (xx >= 26) & (xx <= 69) & (yy >= 13) & (yy <= 42)
    fill(fo, plaque & ~inner, "br3")
    t1 = top_edge(plaque)
    t2 = top_edge(plaque & ~t1)
    r1 = right_edge(plaque)
    r2 = right_edge(plaque & ~r1)
    fill(fo, t2 & ~r1, "br4")
    fill(fo, t1, "br5")
    fill(fo, (r2 & ~t1 & ~t2) | bottom_edge(plaque), "br1")
    fill(fo, r1 & ~t1, "br0")
    fill(fo, left_edge(plaque) & ~t1, "br4")
    box(fo, 26, 13, 69, 13, "br1")
    box(fo, 26, 13, 26, 42, "br1")
    box(fo, 27, 42, 69, 42, "br4")
    # raw metal along the fresh fracture
    fracture = (t1 | r1) & (xx >= 57) & (yy <= 25)
    fill(fo, fracture, "br6")
    fill(fo, (t2 | r2) & (xx >= 58) & (yy <= 25) & ~fracture, "br4")
    # patina over the field: verdigris mottling with darker pooling low and along the frame
    rng = random.Random(0xE5A3)
    field = plaque & inner & (yy >= 14) & (xx >= 27)
    fill(fo, field, "vd1")
    fill(fo, field & ((yy >= 40) | (xx <= 28)), "vd0")
    for _ in range(190):
        x, y = rng.randrange(27, 70), rng.randrange(14, 42)
        if field[y, x]:
            put(fo, x, y, rng.choice(("vd0", "vd2", "vd2", "br2")))
    # the crack running down-left from the break into the field
    seg(ins, [(63, 17), (61, 22), (62, 27), (58, 33), (59, 38)], "br0")
    seg(ins, [(64, 17), (62, 22), (63, 26)], "br4")

    # the erased heading band: patina scraped through to raw metal, criss-cross abrasion that overshoots
    # the band's edges, and only stray stroke stubs left
    hx0, hy0, hx1, hy1 = 29, 15, 60, 22
    band = (xx >= hx0) & (xx <= hx1) & (yy >= hy0) & (yy <= hy1) & plaque
    reach = (xx >= hx0 - 2) & (xx <= hx1 + 2) & (yy >= hy0 - 1) & (yy <= hy1 + 2) & field
    scrape = layer(w, h)
    fill(scrape, band, "br4")
    for k in range(-10, 42, 3):
        seg(scrape, [(hx0 + k, hy1 + 2), (hx0 + k + 7, hy0 - 1)], "br5")
    for k in range(-6, 42, 5):
        seg(scrape, [(hx0 + k, hy0 - 1), (hx0 + k + 6, hy1 + 2)], "br3")
    for k in range(0, 34, 6):
        seg(scrape, [(hx0 + k, hy0 + 1 + k % 3), (hx0 + k + 9, hy0 + 2 + k % 4)], "br6")
    keep_scrape = band | (reach & (scrape[..., 0] > 0) & (((xx * 7 + yy * 3) % 5) < 2))
    ins[keep_scrape] = scrape[keep_scrape]
    for x, y in [(33, 17), (33, 18), (34, 18), (41, 16), (49, 20), (49, 21), (55, 17), (56, 17), (45, 22)]:
        put(ins, x, y, "vd0")

    # intact body rows below: cast marks catching light, with a patina shadow under each stroke
    keep = lambda x, y: bool(field[y, x]) and abs(x - (63 - (y - 17) * 0.25)) > 1.2 and y >= 25
    for y in (26, 31, 36):
        glyph_row(ins, 29, 67, y, rng, "br3", "vd0", keep, wear=0.12)
    # rivets at the corners
    for x, y in [(24, 11), (24, 44), (71, 44)]:
        put(eq, x, y, "br6")
    # the broken corner lying on the floor, patina up, a few chips
    piece = poly_mask([(76, 56), (86, 53), (91, 57), (85, 61), (77, 60)], w, h)
    fill(st, ring(piece), "ink")
    fill(st, piece, "br2")
    fill(fo, top_edge(piece), "br5")
    for x, y in [(81, 57), (84, 56), (86, 58), (79, 58)]:
        put(fo, x, y, "vd1")
    put(fo, 82, 58, "vd2")
    for x, y in [(73, 62), (90, 62), (17, 61), (75, 50)]:
        put(eq, x, y, "br4" if x > 50 else "ss4")
    # survey marks: a teal reticle on the scraped band and a clip tag on the left frame edge
    bracket(tl, hx0 - 1, hy0 - 1, hx1 + 1, hy1 + 1, "tl4", 2)
    box(eq, 19, 15, 22, 21, "st1")
    box(tl, 19, 16, 21, 20, "tl3")
    put(tl, 20, 17, "glow")
    return [sh, st, fo, ins, eq, tl]


# ---------------------------------------------------------------- 研判终端 / Analysis console

def terminal_light_table():
    w, h = TW, TH
    sh, st, fo, sp, tl = (layer(w, h) for _ in range(5))
    shadow(sh, (10, 28, 86, 37))
    shadow(sh, (0, 31, 16, 37), pad=(2, 1))
    # table top in 3/4 view: timber frame around a light panel, apron, folding legs
    box(st, 13, 5, 83, 22, "ink")
    box(st, 14, 6, 82, 16, "wd3")
    box(st, 14, 17, 82, 21, "wd2")
    box(fo, 14, 6, 82, 6, "wd4")
    box(fo, 14, 7, 15, 16, "wd4")
    box(fo, 81, 7, 82, 16, "wd2")
    box(fo, 14, 17, 82, 17, "wd4")
    box(fo, 14, 21, 82, 21, "wd1")
    box(fo, 82, 18, 82, 21, "wd1")
    for x in (30, 52, 70):
        put(fo, x, 19, "wd1")
    for lx, rx in ((18, 26), (70, 78)):
        seg(st, [(lx, 22), (rx, 34)], "wd1", 2)
        seg(st, [(rx, 22), (lx, 34)], "wd2", 2)
        seg(fo, [(lx, 22), (rx, 33)], "wd3")
    for fx in (17, 25, 69, 77):
        box(st, fx, 34, fx + 2, 35, "ink")
    # brass corner fittings
    for x in (14, 80):
        box(sp, x, 17, x + 2, 19, "br3")
        put(sp, x + (0 if x == 14 else 2), 17, "br5")
    # light panel: dim teal glass with a faint grid
    box(st, 18, 8, 78, 15, "st0")
    box(tl, 19, 9, 77, 14, "tl1")
    for x in range(21, 77, 6):
        box(tl, x, 9, x, 14, "tl2")
    box(tl, 19, 11, 77, 11, "tl2")
    box(tl, 36, 10, 58, 13, "tl2")
    # specimen shard on the glass, with its outline glowing through
    shard = poly_mask([(40, 10), (45, 9), (52, 10), (54, 12), (49, 14), (41, 14)], w, h)
    fill(sp, ring(shard) & (np.mgrid[0:h, 0:w][0] >= 9), "tl3")
    fill(sp, shard, "ss4")
    fill(sp, top_edge(shard), "ss6")
    fill(sp, right_edge(shard), "ss2")
    for x, y in [(44, 12), (46, 11), (48, 12), (50, 11)]:
        put(sp, x, y, "ss1")
    # brass magnifier arm from a post at the back left, lens over the shard
    box(st, 24, 0, 26, 9, "ink")
    box(st, 25, 1, 25, 8, "br3")
    seg(sp, [(25, 1), (34, 2), (42, 5)], "br3")
    seg(fo, [(25, 0), (34, 1)], "br5")
    box(sp, 41, 4, 47, 8, "br2")
    box(tl, 42, 5, 46, 7, "tl3")
    put(tl, 43, 5, "glow")
    # small readout at the back right, face toward the viewer
    box(st, 63, 0, 79, 9, "ink")
    box(st, 64, 1, 78, 8, "st2")
    box(fo, 64, 1, 78, 1, "st4")
    box(tl, 65, 2, 77, 7, "tl0")
    for x in range(66, 76, 2):
        put(tl, x, 3, "tl3")
    for x in (66, 67, 70, 73):
        put(tl, x, 5, "tl2")
    box(tl, 66, 6, 68, 6, "am")
    put(tl, 77, 2, "tl4")
    # cable down to a power case on the floor at the left
    seg(sp, [(14, 14), (9, 20), (8, 27)], "st1")
    box(st, 1, 26, 15, 34, "ink")
    box(st, 2, 27, 14, 28, "st3")
    box(st, 2, 29, 14, 33, "st2")
    box(fo, 2, 27, 14, 27, "st4")
    box(fo, 14, 29, 14, 33, "st1")
    put(tl, 4, 31, "tl4")
    put(sp, 6, 31, "am")
    put(sp, 9, 31, "rd")
    return [sh, st, fo, sp, tl]


FIXTURES = [
    ("machine-translation", fixture_machine_translation, 3,
     "机器译文 / Machine Translation: a broken sandstone fragment with abstract incised glyph rows rests in a felt-lined timber cradle; one glyph group is worn shallow and partly missing. A field translator on a tripod aims its scanner at that group (teal reticle on the stone) and shows it boxed in amber on its screen beside a confidence bar with only two of twelve segments lit. No recovered word or recipient is shown."),
    ("parallel-inscription", fixture_parallel_inscription, 4,
     "平行铭文 / Parallel Inscription: a dark basalt tablet with two parallel incised registers, held upright by timber braces and bronze edge brackets on a sandstone plinth. One similar-but-not-identical glyph group in each register is marked with a teal bracket and a clip tag for comparison. No word is shown."),
    ("erased-heading", fixture_erased_heading, 5,
     "擦除标题 / Erased Heading: a patinated bronze plaque on a sandstone pedestal, cracked with its upper-right corner broken off and lying on the floor. Its heading band is scraped through the patina to raw metal with criss-cross abrasion and only stray stroke stubs; the cast body rows below are intact. A teal reticle and clip tag mark the scraped band. Nothing of the heading is restored."),
]
TERMINAL_ITEM = ("analysis-light-table", terminal_light_table,
                 "研判终端 / Analysis console: a low timber field light-table at the near floor edge, a specimen shard on dim teal glass under a brass magnifier arm, a small readout at the back right and a power case on the floor.")


# ---------------------------------------------------------------- placement, footprints, sorting

def opaque(layers):
    a = np.zeros(layers[0].shape[:2], bool)
    for l in layers[1:]:  # contact shadow excluded
        a |= l[..., 3] > 0
    return a


def footprint(layers, rows, pad=6):
    """Feet blocker: the opaque columns across the given canvas rows, padded by about half the heroine's width."""
    m = opaque(layers)[rows[0]:rows[1] + 1]
    cols = np.nonzero(m.any(axis=0))[0]
    return int(cols.min()) - pad, int(cols.max()) + pad


def placements():
    items = []
    for (slug, fn, clue, _), (cx, cy) in zip(FIXTURES, CLUES):
        layers = fn()
        x0 = cx - CW // 2
        c0, c1 = footprint(layers, (48, 61))
        items.append({"slug": slug, "clue": clue, "origin": [x0, CLUE_ORIGIN_Y], "size": [CW, CH],
                      "sort_y": CLUE_ORIGIN_Y + CLUE_SORT_ROW,
                      "blocker": [x0 + c0, CLUE_ORIGIN_Y + 48, c1 - c0 + 1, 14]})
    layers = TERMINAL_ITEM[1]()
    # the heroine's sprite reaches ~14 px left, ~8 px right and 4 px below her feet: fence the table so
    # she can never overlap it (it draws before her)
    c0, c1 = footprint(layers, (0, 35), pad=15)
    top = TERMINAL_ORIGIN[1] - 6
    items.append({"slug": TERMINAL_ITEM[0], "origin": list(TERMINAL_ORIGIN), "size": [TW, TH],
                  "blocker": [TERMINAL_ORIGIN[0] + c0, top, c1 - c0 + 1, 306 - top]})
    return items


# ---------------------------------------------------------------- source writers

def merged(layers):
    w, h = layers[0].size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for img in layers:
        out.alpha_composite(img)
    return out


def png_bytes(img):
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=False)
    return buf.getvalue()


DT = (2026, 10, 18, 0, 11, 56)


def ora_bytes(name, names, layers, flat):
    w, h = flat.size
    root = ET.Element("image", {"w": str(w), "h": str(h), "name": name, "version": "0.0.3"})
    stack = ET.SubElement(root, "stack")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", DT), "image/openraster", compress_type=zipfile.ZIP_STORED)
        z.writestr(zipfile.ZipInfo("mergedimage.png", DT), png_bytes(flat), compress_type=zipfile.ZIP_DEFLATED)
        for i, (ln, img) in reversed(list(enumerate(zip(names, layers)))):  # ORA lists top layer first
            src = f"data/layer{i:02d}.png"
            z.writestr(zipfile.ZipInfo(src, DT), png_bytes(img), compress_type=zipfile.ZIP_DEFLATED)
            ET.SubElement(stack, "layer", {"name": ln, "src": src, "x": "0", "y": "0", "opacity": "1.0",
                                           "visibility": "visible", "composite-op": "svg:src-over"})
        z.writestr(zipfile.ZipInfo("stack.xml", DT), ET.tostring(root, encoding="utf-8", xml_declaration=True),
                   compress_type=zipfile.ZIP_DEFLATED)
    return buf.getvalue()


def pxo_bytes(export_name, names, layers, flat, palette_hex):
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
    palette = [{"name": "wdc-annex-room2-v01", "colors": [{"color": c, "index": i} for i, c in enumerate(palette_hex)]}]
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
        for i, img in enumerate(layers, start=1):
            add(f"image_data/frames/1/layer_{i}", img.tobytes())
            add(f"image_data/frames/1/indices_layer_{i}", b"\x00")
    return buf.getvalue()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rel(p):
    return str(p.relative_to(ROOT)).replace("\\", "/")


def palette_hex():
    return sorted(P.values())


def write_asset(stem, export_name, names, layers):
    flat = merged(layers)
    files = {"png": png_bytes(flat), "ora": ora_bytes(stem, names, layers, flat),
             "pxo": pxo_bytes(export_name, names, layers, flat, palette_hex())}
    for ext, data in files.items():
        (OUT / f"{stem}.{ext}").write_bytes(data)
    runtime = RUNTIME_PROP_DIR / f"{stem}.png"
    runtime.write_bytes(files["png"])
    return {
        "size": list(flat.size), "layers_bottom_to_top": names,
        "files": {ext: {"file": rel(OUT / f"{stem}.{ext}"), "sha256": sha(d), "hash_algorithm": "sha256-bytes"} for ext, d in files.items()},
        "runtime_png": {"file": rel(runtime), "sha256": sha(files["png"]), "hash_algorithm": "sha256-bytes"},
        "opaque_colours": int(len({tuple(p) for p in np.array(flat).reshape(-1, 4) if p[3] == 255})),
    }


def all_assets():
    """(slug, layer names, layer arrays) for every asset, clue fixtures first."""
    out = [(slug, CLUE_LAYERS, fn()) for slug, fn, _, _ in FIXTURES]
    out.append((TERMINAL_ITEM[0], TERMINAL_LAYERS, TERMINAL_ITEM[1]()))
    return out


def preview(folder):
    """Fixtures alone at 4x, and composited over a bilinear 640x360 approximation of the room plate at 2x."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    bg = Image.open(BACKGROUND).convert("RGBA").resize((640, 360), Image.Resampling.BILINEAR)
    for (slug, names, layers), place in zip(all_assets(), placements()):
        img = merged([Image.fromarray(l) for l in layers])
        img.resize((img.width * 4, img.height * 4), Image.Resampling.NEAREST).save(folder / f"fx-{slug}-4x.png")
        bg.alpha_composite(img, tuple(place["origin"]))
    bg.save(folder / "room.png")
    bg.resize((1280, 720), Image.Resampling.NEAREST).save(folder / "room-2x.png")
    print(json.dumps(placements(), indent=1))


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    RUNTIME_PROP_DIR.mkdir(parents=True, exist_ok=True)
    place = {p["slug"]: p for p in placements()}
    fixtures = []
    for slug, fn, clue, meaning in FIXTURES:
        item = write_asset(f"{PREFIX}_{slug}-pixel-fixture_unapproved-v01_{STAMP}", f"wdc-annex-room2-v01-{slug}",
                           CLUE_LAYERS, [Image.fromarray(l) for l in fn()])
        item.update({"clue": f"scifi.ruins:{clue}", "reads_as": meaning, "placement": place[slug]})
        fixtures.append(item)
    slug, fn, meaning = TERMINAL_ITEM
    terminal = write_asset(f"{PREFIX}_{slug}-pixel-fixture_unapproved-v01_{STAMP}", f"wdc-annex-room2-v01-{slug}",
                           TERMINAL_LAYERS, [Image.fromarray(l) for l in fn()])
    terminal.update({"interaction": "existing research terminal at TERMINAL_POSITION (320, 263), unchanged",
                     "reads_as": meaning, "placement": place[slug]})
    manifest = {
        "project": "rpg-2-star-ocean-the-second",
        "scene": "Washington, D.C. ruins survey annex room 2 (记录内室 / Records Chamber), destination scifi.ruins",
        "variant": "v01 physical investigation fixtures; test-only opt-in `-- --wdc-records-chamber-v01`, default room 2 unchanged",
        "status": "UNAPPROVED candidate; the creator has not reviewed it; counters unchanged",
        "authorship": {
            "fixtures": "Hand-placed pixel by pixel in this tool by Claude (Claude Code, signed-in Claude Max, firstParty); "
                        "no generated image, underpainting, resampling or filtering. Glyph marks are abstract 3x3 stroke cells "
                        "that are not characters of any script.",
            "background": "Not touched. Room 2 keeps the existing m8-concept plate "
                          f"({rel(BACKGROUND)}), a generated concept image drawn scaled to 640x360; these fixtures sit on it.",
        },
        "background_sha256": sha(BACKGROUND.read_bytes()),
        "palette_hex": P, "contact_shadow_rgba": {"core": list(SHADOW_CORE), "edge": list(SHADOW_EDGE)},
        "pixelorama": f"pxo_version 7, color_mode 5, 1 frame; clue fixtures {len(CLUE_LAYERS)} layers, terminal {len(TERMINAL_LAYERS)} layers; ORA lists the same layers",
        "runtime": {
            "clue_canvas": [CW, CH], "clue_origin": "(clue.x - 48, %d)" % CLUE_ORIGIN_Y,
            "clue_sort_y": CLUE_ORIGIN_Y + CLUE_SORT_ROW,
            "terminal_canvas": [TW, TH], "terminal_origin": list(TERMINAL_ORIGIN),
            "notes": "clue fixtures are y-sorted Sprite2D children with their clue marker as a child (marker always above its "
                     "fixture); the terminal table draws before the heroine and is fenced by its blocker so she never overlaps it",
        },
        "fixtures": fixtures, "terminal": terminal, "source": rel(Path(__file__)),
    }
    path = OUT / f"{PREFIX}_records-chamber-fixtures-manifest_unapproved-v01_{STAMP}.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(rel(path))
    print(json.dumps([p for p in placements()], indent=1))
    return manifest


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":
        preview(sys.argv[2])
    else:
        build()
