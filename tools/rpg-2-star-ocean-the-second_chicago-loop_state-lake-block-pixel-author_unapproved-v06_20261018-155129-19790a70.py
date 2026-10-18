"""Chicago Loop arrival block, State St x Lake St: native 640x360 materials/depth pass v06 (UNAPPROVED, NONRUNTIME candidate).

v06 is one bounded native-pixel materials and depth pass over v05, after root's visual review (verdict
changes_requested, docs/qa/...codex-visual-review_six-verdicts_qa-receipt_v01_20261018-153526-67e353de.md):
"the upper facades and steel spans are still large flat repeated rectangles, and the repeated tree/planter
shapes and uniform paving have weaker depth and material craft than the ready interiors".

This tool does not copy the v05 author. It imports it unchanged
(tools/...pixel-author_unapproved-v05_20261017-234337-84862412.py) and replaces only the painters named
below, so every other pixel, the geometry, the blocks, the prop list, the pivots and the hero-visibility
model stay the v05 code. All changes are marked "v06".
  * backdrop-facade-north: per-building cast-shadow lines (one horizontal edge per facade, stepping down at
    the party walls) instead of the 36 px stair-step; a belt cornice with its shadow on the terracotta
    block; rounded terracotta piers (lit west face, shaded east face) and Chicago-window mullions in sun;
    stone lintels and a corbel band on the brick block plus one iron fire escape; limestone pilasters with
    a lit west face and a shaded east face, deeper window reveals, a belt course with its shadow.
  * station-platform-canopy: the windbreak is calm dark glass with one broad reflection band per bay
    (v05 showed the facade grid through it, which read as busy noise). Roof, posts, lamps, coping and the
    head house are unchanged.
  * backdrop-deck-l-girder: the plate girder gets an under-flange shadow and a grime band on the web,
    double-angle stiffeners with rivet columns and a cast shadow east of each, riveted splice plates at
    an irregular rhythm, two-pixel rivet heads (lit head, dark underside) along both flanges.
  * ground-street-plaza: random fleck grain on the slabs cut back; a few purposeful wear marks instead
    (chipped slab corners, two replaced slabs, root-heave cracks by the tree grates, spalled curb notches).
  * ground-contact-shadow (new static layer): short contact shadows to the lower right (south-east) of every
    prop footprint, consistent with the upper-left low sun, and an ambient-occlusion band where the
    storefront plinth meets the under-deck walk.
  * y-sort props, colour only inside the v05 alpha unless noted: foliage is drawn as lit leaf masses with a
    dark crevice on their lower-right edge (per-planting species: shrub, boxwood, honey locust, conifer,
    grass), knee braces read as round members with rivet pairs, planter boxes get distinct materials.
    All y-sort alpha silhouettes, prop regions, pivots, walk mask and occlusion
    reveal mask stay byte-identical to v05 (checked by the v06 source check).
Unchanged from v05: geometry, blocks, walk mask, reveal mask, prop regions and pivots, interaction anchors,
spawn, labels and the scene script. v06 runtime-candidate PNGs are written to outputs/ only: no file under
game/ is created or edited (the v05 scene is shown with v06 textures by a test-only Godot capture harness).
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import io
import json
import sys
import zipfile

import numpy as np
import PIL
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
V05_AUTHOR = ROOT / "tools" / "rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-author_unapproved-v05_20261017-234337-84862412.py"
V05_MANIFEST = ROOT / "outputs/chicago-loop-state-lake-v05/rpg-2-star-ocean-the-second_chicago-loop_state-lake_layer-manifest_unapproved-v05_20261017-234337-84862412.json"
STAMP = "20261018-155129-19790a70"
VARIANT = "unapproved-v06"
OUT = ROOT / "outputs" / "chicago-loop-state-lake-v06"
ZIP_TIME = (2026, 10, 18, 15, 51, 28)


def load_v05():
    spec = spec_from_file_location("chicago_author_v05_base", V05_AUTHOR)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


v5 = load_v05()
W, H = v5.W, v5.H
PREFIX = v5.PREFIX
hsh, shift, ellipse, poly, rmask, Layer = v5.hsh, v5.shift, v5.ellipse, v5.poly, v5.rmask, v5.Layer

# ---------------------------------------------------------------- v06 palette additions
# Blue-green conifer needles (darker and cooler than the broadleaf ramp, so the two conifers stop reading
# as the same green as the shrubs). Added to the v05 palette dict; the .gpl lists only colours in use.
V06_COLOURS = {"fb0": (14, 30, 28), "fb1": (24, 50, 42), "fb2": (38, 74, 58), "fb3": (62, 102, 72)}
v5.PAL.update(V06_COLOURS)
v5.RAMPS["fb"] = list(V06_COLOURS)
# Codex finish: granite's open-plane value changes are restrained so its joints no longer dominate the foreground.
GRANITE = {"pg0": (120, 108, 94), "pg1": (132, 118, 102), "pg2": (144, 129, 110), "pg3": (154, 138, 118), "pg4": (164, 147, 125), "pg5": (174, 157, 135)}
v5.PAL.update(GRANITE)
v5.RAMPS["pg"] = list(GRANITE)


# ---------------------------------------------------------------- v06 far facades
# One cast-shadow edge per facade (from a taller block west of State St, off camera): horizontal across each
# building, stepping down at the party walls, so it reads as a shadow on three facades at different depths.
SHADOW_ROW = [(96, 74), (280, 77), (424, 80), (W, 80)]   # (x_end, first shaded row); State St sidewalk uses the first
SHADOW_STEP = 3                                           # the step falls diagonally over 3 px east of each seam


def canyon_row(x):
    """v06: first shadowed row of the far facades and the corner sidewalk at column x."""
    prev = SHADOW_ROW[0][1] - 2
    for x_end, row in SHADOW_ROW:
        if x < x_end:
            break
        prev = row
    x0 = 0
    for x_end, row in SHADOW_ROW:
        if x < x_end:
            # diagonal step just east of the seam at x0 (from the previous facade's row to this one's)
            d = x - x0
            if x0 > 0 and d < SHADOW_STEP:
                return prev + (row - prev) * d // SHADOW_STEP
            return row
        x0 = x_end
    return SHADOW_ROW[-1][1]


def paint_terracotta(L, x0, x1, bay, fh, ft):
    """v06: Chicago-school block in buff terracotta: a belt cornice two floors up with its shadow, rounded piers
    (lit west face, mid, shaded east face), recessed spandrel panels, Chicago windows with mullions between
    the fixed pane and the sashes, an L of recess shadow (lintel and pier) on the glass, a lit sill with a
    shadow row under it, pale blinds now and then, lit interiors only on the shadow side."""
    for y in range(62, v5.DECK_TOP):
        fy = (y - ft) % fh
        fl = (y - ft) // fh
        for x in range(x0, x1):
            bx = (x - x0) % bay
            b = (x - x0) // bay
            sun = v5.in_sun(x, y)
            fixed = 8 <= bx < bay - 5
            if bx < 3:                                         # pier: lit west face, mid, shaded east face
                c = ("tc4", "tc3", "tc2")[bx] if sun else ("tc2", "tc1", "tc0")[bx]
            elif fy in (0, 1):                                 # recessed spandrel panel
                c = ("tc3" if fy == 0 else "tc2") if sun else ("tc1" if fy == 0 else "tc0")
            elif fy == 9:
                c = "tc4" if sun else "tc2"                    # lit sill
            elif fy == 10:
                c = "tc2" if sun else "tc1"                    # shadow under the sill
            elif fy == 2 or bx == 3:
                c = "gw0"                                      # lintel and pier shadow on the glass
            elif bx in (7, bay - 5):
                c = "tc2" if sun else "tc0"                    # mullions between fixed pane and sashes
            elif not sun and fixed and hsh(b, fl, 141) < 0.34:
                c = "lt0" if fy == 3 else "lt1"
            elif sun and fy - 3 < v5.blind(b, fl, 141):
                c = "gw3"
            else:
                c = "gw2" if sun else ("gw1" if fixed else "gw0")
            L.px(x, y, c)
    # belt cornice at rows 62..64 with its two-row shadow (a projecting band, lit top, dark soffit)
    for x in range(x0, x1):
        sun = v5.in_sun(x, 62)
        L.px(x, 62, "tc4" if sun else "tc2")
        L.px(x, 63, "tc3" if sun else "tc1")
        L.px(x, 64, "tc1" if sun else "tc0")
        if (x - x0) % 4 == 1:
            L.px(x, 64, "tc0")                                 # dentil shadows under the band
        wall = L.get(x, 65) in (v5.PAL["tc4"], v5.PAL["tc3"], v5.PAL["tc2"])
        L.px(x, 65, ("tc1" if wall else "gw0") if v5.in_sun(x, 65) else ("tc0" if wall else "gw0"))


def paint_brick(L, x0, x1, bay, fh, ft):
    """v06: recessive brick block: stone lintels over punched windows, shaded head and west jamb, a lit east
    reveal, a limestone sill and the shadow under it, one corbelled brick band at a floor line."""
    for y in range(62, v5.DECK_TOP):
        fy = (y - ft) % fh
        fl = (y - ft) // fh
        for x in range(x0, x1):
            bx = (x - x0) % bay
            b = (x - x0) // bay
            sun = v5.in_sun(x, y)
            if fy == 1 and 4 <= bx <= 12:
                c = "ls3" if sun else "ls1"                    # stone lintel
            elif 5 <= bx <= 11 and 2 <= fy <= 6:
                if fy == 2 or bx == 5:
                    c = "gw0"
                elif not sun and hsh(b, fl, 143) < v5.LIT_WINDOW_SHARE:
                    c = "lt0"
                elif sun and fy - 3 < v5.blind(b, fl, 143):
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
    for x in range(x0, x1):                                    # corbel band at the floor line of row 68
        sun = v5.in_sun(x, 68)
        L.px(x, 67, "bk3" if sun else "bk2")
        L.px(x, 68, ("bk3" if (x - x0) % 3 else "bk1") if sun else ("bk2" if (x - x0) % 3 else "bk0"))
    paint_fire_escape(L)


FIRE_ESCAPE = (378, 420)                                       # x range on the brick block, east of the head house


def paint_fire_escape(L):
    """v06: one black iron fire escape: two balconies at the sill lines with railings, a diagonal stair
    between them and the shadow they throw on the brick to the lower right."""
    x0, x1 = FIRE_ESCAPE
    for top in (66, 75):                                       # balcony decks at the sill lines (rows 66, 75)
        for x in range(x0, x1):
            if 62 <= top + 2 < v5.DECK_TOP:
                L.px(x + 1, top + 2, "bk0")                    # shadow of the deck on the wall
            L.px(x, top, "ir1")
            L.px(x, top + 1, "ir0")
            if (x - x0) % 4 == 0 and top - 3 >= 62:            # railing posts
                L.vline(x, top - 3, top, "ir1")
        if top - 3 >= 62:
            L.hline(x0, x1, top - 3, "ir2")                    # top rail, lit
    for k in range(9):                                         # stair from the upper to the lower balcony
        x = x0 + 4 + k * 2
        y = 67 + k
        if y < 75:
            L.rect(x, y, x + 2, y + 1, "ir1")
            L.px(x + 2, y + 1, "bk0")


def paint_limestone(L, x0, x1, bay, fh, ft):
    """v06: limestone block: pilasters with a lit west face and a shaded east face, deep paired-window reveals
    (lintel and jamb shadow, a lit east reveal), a lit sill with a shadow row under it, a belt course with
    its shadow every other floor, pale blinds now and then, lit interiors only on the shadow side."""
    for y in range(62, v5.DECK_TOP):
        fy = (y - ft) % fh
        fl = (y - ft) // fh
        for x in range(x0, x1):
            bx = (x - x0) % bay
            b = (x - x0) // bay
            sun = v5.in_sun(x, y)
            win = (8 <= bx <= 13 or 20 <= bx <= 25) and 3 <= fy <= 9
            near = 7 <= bx <= 14 or 19 <= bx <= 26
            if bx < 4:
                c = ("ls4", "ls4", "ls3", "ls1")[bx] if sun else ("ls2", "ls2", "ls1", "ls0")[bx]
            elif fl % 2 == 0 and fy in (0, 1):
                c = ("ls4" if fy == 0 else "ls1") if sun else ("ls2" if fy == 0 else "ls0")   # belt course, shadow
            elif win:
                if fy == 3 or bx in (8, 20):
                    c = "gw0"
                elif bx in (13, 25):
                    c = "ls3" if sun else "ls1"                # lit east reveal
                elif not sun and hsh(b * 2 + (bx > 16), fl, 145) < 0.3:
                    c = "lt0" if fy == 4 else "lt1"
                elif sun and fy - 4 < v5.blind(b * 2 + (bx > 16), fl, 145):
                    c = "gw3"
                else:
                    c = "gw2" if sun else "gw1"
            elif fy == 10 and near:
                c = "ls4" if sun else "ls2"
            elif fy == 11 and near:
                c = "ls1" if sun else "ls0"                    # shadow under the sill
            else:
                c = "ls3" if sun else "ls1"
            L.px(x, y, c)


v5.canyon_row = canyon_row
v5.paint_terracotta = paint_terracotta
v5.paint_brick = paint_brick
v5.paint_limestone = paint_limestone
v5.FACADE_PAINTERS.update({"terracotta": paint_terracotta, "brick": paint_brick, "limestone": paint_limestone})


def through_glass(n):
    """v06: unused facade sampling is replaced by calm glass (see windbreak below)."""
    return "gw0"


_V05_CANOPY = v5.draw_platform_canopy


def draw_platform_canopy(L, facade=None):
    """v06: the v05 canopy, then the windbreak rows 82..89 repainted as calm dark glass with one broad
    reflection band per bay between posts (posts and lamps are redrawn on top as in v05)."""
    _V05_CANOPY(L, None)
    x0, x1 = v5.CANOPY
    for y in range(82, 90):
        for x in range(x0 + 2, x1 - 2):
            px = L.get(x, y)
            if px in (v5.PAL["gl0"],):
                k = (x - x0 + (89 - y)) % 32
                L.px(x, y, "gw1" if 6 <= k < 10 else "gw0")
    _redraw_canopy_details(L)


def _redraw_canopy_details(L):
    for px_ in v5.CANOPY_POSTS:
        L.rect(px_, 81, px_ + 2, 90, "iw1")
        L.vline(px_, 81, 90, "iw3")
    for px_ in v5.CANOPY_POSTS[1::2]:
        L.rect(px_ + 13, 81, px_ + 18, 83, "lt2")
        L.hline(px_ + 14, px_ + 17, 81, "lt3")


v5.draw_platform_canopy = draw_platform_canopy


# ---------------------------------------------------------------- v06 deck girder (steel web)
SPLICES = (86, 182, 262, 374, 534, 614)                       # splice plates: irregular, clear of lamps, caps and the plate


def draw_deck(L):
    """v06: the v05 deck and plate girder with legible steel craft: an under-flange shadow and a grime band on
    the web, double-angle stiffeners (lit west leg, rivet column, shadow cast east on the web), riveted
    splice plates at an irregular rhythm, two-pixel rivet heads along both flanges."""
    y0 = v5.DECK_TOP
    L.rect(0, y0, W, y0 + 13, "iw0")
    for x in range(0, W):
        t = x % 6
        if t < 4:
            c = "ru0" if t in (0, 3) else ("ru1" if hsh(x // 6, 0, 121) < 0.7 else "wd0")
            L.vline(x, y0 + 1, y0 + 12, c)
            if t == 1 and hsh(x // 6, 1, 121) < 0.25:
                L.px(x, y0 + 6, "ru2")
    for ry, hi in ((y0 + 3, "iw4"), (y0 + 9, "iw4")):
        L.hline(0, W, ry, hi)
        L.hline(0, W, ry + 1, "iw2")
    L.hline(0, W, y0 + 6, "iw3")
    for x in range(2, W, 6):
        L.px(x, y0 + 5, "iw3")
        L.px(x, y0 + 11, "iw3")
    L.hline(0, W, y0, "iw2")
    L.hline(0, W, y0 + 12, "iw1")
    top = y0 + 13                                              # top flange: warm sun glint on the edge
    L.rect(0, top, W, top + 3, "iw3")
    L.hline(0, W, top, "ru2")
    for x in range(0, W, 9):
        L.px(x + int(hsh(x, 3, 122) * 6), top, "ru3")
    L.hline(0, W, top + 2, "iw1")                              # flange underside in shadow
    web0, web1 = top + 3, top + 21
    L.rect(0, web0, W, web1, "iw2")
    L.hline(0, W, web0, "iw1")                                 # v06: shadow of the flange on the web
    L.rect(0, web1 - 4, W, web1 - 1, "iw1")                    # v06: grime band on the lower web
    L.hline(0, W, web1 - 1, "iw0")
    for x in range(0, W, 4):                                   # v06: two-pixel rivet heads on both flange lines
        L.px(x + 1, web0 + 1, "iw4")
        L.px(x + 1, web0 + 2, "iw1")
        L.px(x + 3, web1 - 3, "iw3")
        L.px(x + 3, web1 - 2, "iw0")
    for sx in range(14, W, 32):                                # double-angle stiffeners
        L.vline(sx - 1, web0, web1, "iw1")                     # seam west of the angle
        L.vline(sx, web0, web1, "iw4")                         # lit west leg
        L.vline(sx + 1, web0, web1, "iw3")
        L.vline(sx + 2, web0, web1, "iw2")
        L.rect(sx + 3, web0 + 1, sx + 5, web1 - 1, "iw1")      # shadow cast east on the web
        for y in range(web0 + 2, web1 - 1, 3):
            L.px(sx + 1, y, "iw4")
            L.px(sx + 1, y + 1, "iw1")
        if hsh(sx, 0, 122) < 0.6:                              # rust runs under a rivet
            n = 2 + int(hsh(sx, 1, 122) * 5)
            rx = sx + 7 + int(hsh(sx, 2, 122) * 16)
            L.rect(rx, web0 + 3, rx + 1, min(web1 - 4, web0 + 3 + n), "ru1")
            L.px(rx, web0 + 3, "ru2")
    busy = [(lx - 8, lx + 8) for lx in v5.GIRDER_LAMPS] + [(cx - 15, cx + 15) for cx in v5.COLUMN_X] + \
        [(v5.PLATE[0] - 2, v5.PLATE[2] + 2)] + [(x - 1, x + 13) for x in SPLICES]
    for i, sx in enumerate(range(14, W, 32)):                  # weathering, one deliberate mark per panel at most
        h = hsh(i, 5, 123)
        px0 = sx + 9 + int(hsh(i, 6, 123) * 12)
        if any(a <= px0 + dx <= b for a, b in busy for dx in (-1, 7)):
            continue
        if h < 0.35:                                           # paint loss: lit bare-metal patch, rust lower edge
            py0 = web0 + 4 + int(hsh(i, 7, 123) * 5)
            for k, (o, n) in enumerate(((1, 3), (0, 5), (0, 6), (1, 4), (2, 2))):
                L.hline(px0 + o, px0 + o + n, py0 + k, "iw3")
                L.px(px0 + o + n - 1, py0 + k, "ru1" if k > 1 else "iw3")
            L.px(px0 + 1, py0, "iw4")
            L.hline(px0 + 2, px0 + 4, py0 + 5, "ru1")
        elif h < 0.65:                                         # grime streaks down from the upper rivet line
            for dx, n in ((0, 5 + int(hsh(i, 8, 123) * 4)), (3, 3 + int(hsh(i, 9, 123) * 3))):
                L.vline(px0 + dx, web0 + 3, web0 + 3 + n, "iw1")
    for x in SPLICES:                                          # riveted splice plates
        L.rect(x, web0 + 1, x + 11, web1 - 1, "iw3")
        L.vline(x, web0 + 1, web1 - 1, "iw4")
        L.hline(x, x + 11, web0 + 1, "iw4")
        L.vline(x + 10, web0 + 1, web1 - 1, "iw1")
        L.hline(x, x + 11, web1 - 2, "iw1")
        L.vline(x + 11, web0 + 2, web1, "iw0")                 # plate edge shadow on the web
        for ry in range(web0 + 3, web1 - 3, 3):
            for rx in (x + 2, x + 5, x + 8):
                L.px(rx, ry, "iw4")
                L.px(rx, ry + 1, "iw1")
    bot = web1
    L.rect(0, bot, W, bot + 3, "iw3")
    L.hline(0, W, bot, "iw4")
    L.hline(0, W, bot + 2, "iw1")
    L.rect(0, bot + 3, W, v5.DECK_BOTTOM + 1, "iw0")
    for x in range(0, W):
        for y in range(bot + 3, v5.DECK_BOTTOM + 1):
            k = y - bot - 3
            if (x + k) % 8 == 0 or (x - k) % 8 == 0:
                L.px(x, y, "iw2")
    for lx in v5.GIRDER_LAMPS:
        L.rect(lx - 6, web1 - 8, lx + 6, web1 - 1, "iw1")
        L.rect(lx - 5, web1 - 7, lx + 5, web1 - 2, "lt2")
        L.rect(lx - 3, web1 - 6, lx + 3, web1 - 3, "lt3")
        L.hline(lx - 1, lx + 1, web1 - 5, "lt4")
        L.hline(lx - 5, lx + 5, bot, "lt1")
        for y in range(bot + 3, v5.DECK_BOTTOM + 1):
            for x in range(lx - 7 - (y - bot), lx + 8 + (y - bot)):
                if L.get(x, y) == v5.PAL["iw2"]:
                    L.px(x, y, "ru2")
                elif L.get(x, y) == v5.PAL["iw0"] and (x + y) % 2 == 0 and abs(x - lx) < 4 + (y - bot) // 2:
                    L.px(x, y, "ru0")
    for cx in v5.COLUMN_X:
        L.rect(cx - 13, top, cx + 13, v5.DECK_BOTTOM + 1, "iw2")
        L.vline(cx - 13, top, v5.DECK_BOTTOM + 1, "iw4")
        L.vline(cx - 12, top, v5.DECK_BOTTOM + 1, "iw3")
        L.vline(cx + 12, top, v5.DECK_BOTTOM + 1, "iw0")
        L.vline(cx + 13, top + 1, v5.DECK_BOTTOM + 1, "iw0")   # cap shadow on the web
        L.hline(cx - 13, cx + 13, top, "iw4")
        for y in range(top + 2, v5.DECK_BOTTOM - 4, 3):
            for x in (cx - 10, cx - 6, cx + 5, cx + 9):
                L.px(x, y, "iw4")
                L.px(x, y + 1, "iw0")
        L.rect(cx - 8, v5.DECK_BOTTOM - 4, cx + 8, v5.DECK_BOTTOM + 1, "iw1")
        L.hline(cx - 8, cx + 8, v5.DECK_BOTTOM - 4, "iw3")


v5.draw_deck = draw_deck


# ---------------------------------------------------------------- v06 paving: fewer flecks, purposeful wear
FLECK_SHARE = 0.06      # v05: 0.45 of slabs carried a random fleck cluster


def paint_plaza(g):
    """v06: the v05 slab plaza, sett ribbons and guide strip, with the random fleck clusters cut back to a few
    and no random hairlines (wear is now placed by hand in paint_wear)."""
    PT, SW, SH = v5.PLAZA_TOP, v5.SLAB_W, v5.SLAB_H
    for y in range(PT, H):
        ry = y - PT
        row = ry // SH
        off = SW // 2 if row % 2 else 0
        for x in range(v5.CURB_X + 5, W):
            col = (x + off) // SW
            lx, ly = (x + off) % SW, ry % SH
            tone = {"pv3": "pg1", "pv4": "pg2", "pv5": "pg3", "ps0": "pg2", "ps1": "pg3", "ps2": "pg4"}[v5.slab_tone(col, row)]
            if ly == SH - 1 or lx == SW - 1:
                c = shift(tone, -1)  # shallow joints, one material value step, not near-black outlines
            elif ly == 0 and lx < 5:
                c = shift(tone, 1)   # short worn edge catches, not an all-row bright grid
            else:
                c = tone
            g.px(x, y, c)
    for row in range((H - PT) // SH + 1):
        off = SW // 2 if row % 2 else 0
        for col in range(W // SW + 2):
            if hsh(col, row, 33) >= FLECK_SHARE:
                continue
            x0 = col * SW - off + 3 + int(hsh(col, row, 34) * 20)
            y0 = PT + row * SH + 4 + int(hsh(col, row, 35) * 6)
            base = {"pv3": "pg1", "pv4": "pg2", "pv5": "pg3", "ps0": "pg2", "ps1": "pg3", "ps2": "pg4"}[v5.slab_tone(col, row)]
            c = shift(base, -1)
            w_ = 3 + int(hsh(col, row, 36) * 3)
            g.rect(max(x0, v5.CURB_X + 5), y0, x0 + w_, y0 + 1, c)
            g.rect(max(x0 + 1, v5.CURB_X + 5), y0 + 1, x0 + w_ - 1, y0 + 2, c)
    _V05_SETTS(g)


def _v05_setts_and_strip(g):
    """The v05 sett ribbons, sett band and teal guide strip, unchanged."""
    for x0, y0, x1, y1 in ((v5.CURB_X + 5, 276, 560, 280), (195, 248, 202, 298), (429, 248, 436, 298)):
        for y in range(y0, y1):
            for x in range(x0, x1):
                k = (x + (y // 2) * 3) % 6
                g.px(x, y, "pv1" if k == 5 or y % 2 == 1 and x % 6 == 2 else ("pv3" if hsh((x + (y // 2) * 3) // 6, y // 2, 38) < 0.5 else "pv2"))
    PT = v5.PLAZA_TOP
    for y in range(PT, PT + 4):
        for x in range(v5.CURB_X + 5, 540):
            joint = (x + ((y - PT) // 2) * 3) % 6 == 5 or (y - PT) % 2 == 1 and x % 6 == 5
            g.px(x, y, "pv1" if joint else ("pv3" if hsh((x + ((y - PT) // 2) * 3) // 6, y // 2, 37) < 0.5 else "pv2"))
    for x in range(96, 532):
        if (x - 96) % 24 < 18:
            g.px(x, PT + 4, "te3" if (x - 96) % 24 in (2, 8, 14) else "te2")
        g.px(x, PT + 5, "pv1")


_V05_SETTS = _v05_setts_and_strip

# Hand-placed wear on real slab corners: (row, col, corner). Slab row r starts at y = 206 + 16 r; odd rows are
# offset by half a slab (x = 32 col - 16). Kept off the medallion, the interaction rings, the labels and props.
CHIPS = [(1, 4, "nw"), (1, 13, "ne"), (2, 16, "sw"), (3, 17, "ne"), (4, 7, "nw"), (4, 14, "ne"), (2, 11, "se")]
PATCH_SLABS = [(1, 16), (4, 3)]              # two replaced slabs: plain granite, crisp dark joint, lit top edge
CRACKS = [(207, 283, 1), (423, 283, -1)]     # root heave from the honey locust grates (start, direction)
CURB_NOTCHES = (226, 241, 262)               # spalled curb-top notches on the State St curb
UNDERDECK_CHIPS = [(163, 179, "nw"), (343, 188, "ne"), (483, 197, "nw")]   # under-deck panel corners


def slab_corner(row, col, corner):
    x0 = col * v5.SLAB_W - (v5.SLAB_W // 2 if row % 2 else 0)
    y0 = v5.PLAZA_TOP + row * v5.SLAB_H
    return (x0 if corner[1] == "w" else x0 + v5.SLAB_W - 2), (y0 + 1 if corner[0] == "n" else y0 + v5.SLAB_H - 2)


def _tone(g, x, y, d):
    g.px(x, y, shift(v5.name_of(g.a[y, x, :3]), d))


def _chip(g, x, y, kind):
    """A chipped slab corner: a 4-step triangle two values darker (the broken face in shadow) whose diagonal
    edge catches the light one value up (the upper-left light hits the far side of the chip)."""
    dx = 1 if kind[1] == "w" else -1
    dy = 1 if kind[0] == "n" else -1
    for k, n in enumerate((4, 3, 2, 1)):
        for i in range(n):
            _tone(g, x + dx * i, y + dy * k, -2)
        _tone(g, x + dx * n, y + dy * k, 1)


def paint_wear(g):
    for row, col, kind in CHIPS:
        _chip(g, *slab_corner(row, col, kind), kind)
    for row, col in PATCH_SLABS:
        x0, y0 = slab_corner(row, col, "nw")
        y0 -= 1
        g.rect(x0, y0, x0 + v5.SLAB_W - 1, y0 + v5.SLAB_H - 1, "pv4")
        g.hline(x0, x0 + v5.SLAB_W - 1, y0, "pv5")
        g.vline(x0, y0, y0 + v5.SLAB_H - 1, "pv5")
        g.hline(x0 - 1, x0 + v5.SLAB_W, y0 + v5.SLAB_H - 1, "pv0")
        g.vline(x0 + v5.SLAB_W - 1, y0, y0 + v5.SLAB_H, "pv0")
        g.vline(x0 - 1, y0 - 1, y0 + v5.SLAB_H, "pv0")
        g.hline(x0 - 1, x0 + v5.SLAB_W, y0 - 1, "pv0")
    for x, y, d in CRACKS:
        for k in range(14):
            px, py = x + d * k, y - k // 2
            _tone(g, px, py, -2)
            _tone(g, px, py + 1, 1)
    for y in CURB_NOTCHES:
        for k in range(4):
            g.px(v5.CURB_X + 2, y + k, "pv3")
            if 0 < k < 3:
                g.px(v5.CURB_X + 3, y + k, "pv3")
        g.px(v5.CURB_X + 2, y + 4, "pv7")
    for x, y, kind in UNDERDECK_CHIPS:
        _chip(g, x, y, kind)


_V05_MARKERS = v5.paint_markers


def paint_markers(g):
    paint_wear(g)
    _V05_MARKERS(g)


v5.paint_plaza = paint_plaza
v5.paint_markers = paint_markers


# ---------------------------------------------------------------- v06 contact shadows (new static layer)
# Prop name -> contact shadow length in px along the low sun direction (to the lower right). The shadow is
# cast from the prop's own base outline (its lowest opaque pixels), so it shows just outside the art.
CONTACT = {"chicago-lamp": 3, "planter-stone-west": 4, "bench": 3, "planter-iron": 3, "planter-stone-east": 4,
           "litter-bin": 3, "civic-kiosk": 5, "conifer-planter": 4, "l-column-west": 5, "l-column-east": 5,
           "station-stair": 3, "east-terrace": 3, "fountain": 3, "planter-column-west": 3, "planter-column-east": 3,
           "wayfinding-pylon": 4, "granite-seat-west": 3, "granite-seat-east": 3, "honey-locust-west": 2,
           "honey-locust-east": 2, "bike-share-dock": 2, **{"bollard-%d" % y: 2 for y in v5.BOLLARD_ROWS}}
BASE_ROWS = 3                                 # the base outline: opaque pixels in the prop's lowest 3 rows
SUN_DX = 0.8                                  # the column cast shadows run 44 px east per 56 px south


def contact_masks(layers, props):
    """Core (first half) and tail (second half) of every prop's contact shadow, minus the prop's own pixels."""
    core = np.zeros((H, W), bool)
    tail = np.zeros((H, W), bool)
    for p in props:
        n = CONTACT.get(p["name"])
        if not n:
            continue
        x, y, w, h = p["region"]
        alpha = np.zeros((H, W), bool)
        alpha[y:y + h, x:x + w] = np.array(layers[p["layer"]])[y:y + h, x:x + w, 3] == 255
        rows = np.nonzero(alpha.any(axis=1))[0]
        base = alpha & rmask(0, rows.max() - BASE_ROWS + 1, W, rows.max() + 1)
        bys, bxs = np.nonzero(base)
        for k in range(1, n + 1):
            m = np.zeros((H, W), bool)
            sx = int(round(SUN_DX * k))
            ok = (bys + k < H) & (bxs + sx < W)
            m[bys[ok] + k, bxs[ok] + sx] = True
            m &= ~alpha
            if k <= (n + 1) // 2:
                core |= m
            else:
                tail |= m
    return core, tail & ~core


def contact_shadow(ground, shading, layers, props):
    """v06: a layer of ramp-shifted copies of the lit ground: two steps darker in the core of each prop's short
    contact shadow (lower right of its base outline), one step in its tail, and one step in an
    ambient-occlusion band where the storefront plinth meets the under-deck walk."""
    base = Layer()
    base.a[:] = ground.a
    op = shading.a[..., 3] == 255
    base.a[op] = shading.a[op]
    core, tail = contact_masks(layers, props)
    ao = rmask(v5.CURB_X + 5, 170, W, 172)
    walk = rmask(v5.CURB_X + 5, 170, W, H)
    layer = Layer()
    for m, d in ((tail & walk, -1), (ao & ~core, -1), (core & walk, -2)):
        for y, x in zip(*np.nonzero(m)):
            n = v5.name_of(base.a[y, x, :3])
            if n.startswith(("pv", "pg", "ps", "tl", "te", "ir", "as")):
                layer.px(x, y, shift(n, d))
    return layer


# ---------------------------------------------------------------- v06 foliage: lit leaf masses per species
_V05_FOLIAGE = v5.foliage
SPECIES = {
    # seed: (kind, mass spacing x, spacing y, ramp dark..light)
    41: ("shrub", 7, 5, ("fo1", "fo2", "fo3", "fo4", "fo5")),          # stone planter west, flowering
    43: ("box", 4, 3, ("fo0", "fo1", "fo2", "fo3", "fo4")),            # iron planter, clipped boxwood
    45: ("shrub", 6, 4, ("fo1", "fo2", "fo3", "fo4", "fo5")),          # stone planter east
    51: ("box", 5, 4, ("fo0", "fo1", "fo2", "fo3", "fo4")),            # column planter west, boxwood ball
    53: ("grass", 3, 9, ("fo2", "fo3", "fo4", "fo5", "fo6")),          # column planter east, ornamental grass
    61: ("conifer", 5, 4, ("fb0", "fb1", "fb2", "fb3", "fo4")),        # arborvitae by the stair
    81: ("shrub", 6, 5, ("fo1", "fo2", "fo3", "fo4", "fo5")),          # terrace shrubs
    83: ("conifer", 4, 3, ("fb0", "fb1", "fb2", "fb3", "fo4")),        # terrace conifer
    101: ("locust", 11, 8, ("fo2", "fo3", "fo4", "fo5", "fo6")),        # honey locust west: light, lacy
    103: ("locust", 14, 10, ("fo1", "fo2", "fo3", "fo4", "fo5")),        # honey locust east: deeper, larger masses
    97 + 96: ("box", 4, 3, ("fo1", "fo2", "fo3", "fo4", "fo5")),       # south hedge west: clipped boxwood run
    97 + 352: ("shrub", 7, 5, ("fo1", "fo2", "fo3", "fo4", "fo5")),    # south hedge east: mixed flowering planting
}
HEDGE_RAMP = ("fo0", "fo1", "fo2", "fo3", "fo4")
GLOBAL_WEIGHT = {"locust": 0.95}                    # open crowns: stronger light-to-shade across the whole crown
CREVICE = {"box": 2, "conifer": 2, "shrub": 1, "locust": 1, "grass": 1, "hedge": 1}   # value steps into a crevice


def kind_of(seed):
    return SPECIES.get(seed, ("hedge",))[0]


def foliage(layer, region, seed, flowers=(), holes=0.0, light=(-0.6, -0.8), base=True):
    """v06: leaf masses, not per-cell noise. The plant's pixels (exactly the v05 alpha of the same call, so
    sparkle and flower pixels at the rim are kept) are split into masses around jittered centres; each pixel is toned by the light across
    the whole plant (upper left) and across its own mass, the lower-right edge of every mass is a dark
    crevice, and the bottom edge of the plant is the darkest value. Flowers sit in small clusters on lit
    masses. Alpha equals the v05 alpha for the same call."""
    probe = Layer()                                             # exactly the v05 alpha for this call
    _V05_FOLIAGE(probe, region, seed, flowers, holes, light, base)
    region = probe.opaque()
    if kind_of(seed) in ("box", "grass", "conifer"):
        flowers = ()
    ys, xs = np.nonzero(region)
    if not len(xs):
        return
    kind, sx_, sy_, ramp = SPECIES.get(seed, ("hedge", 6, 4, HEDGE_RAMP))
    cx, cy = xs.mean(), ys.mean()
    rx, ry = max(1.0, (xs.max() - xs.min()) / 2), max(1.0, (ys.max() - ys.min()) / 2)
    centres = []
    for gy in range(ys.min() - sy_, ys.max() + sy_ + 1, sy_):
        for gx in range(xs.min() - sx_, xs.max() + sx_ + 1, sx_):
            ox = (sx_ // 2) if kind in ("conifer",) and (gy // sy_) % 2 else 0
            centres.append((gx + ox + (hsh(gx, gy, seed) - 0.5) * sx_ * 0.7, gy + (hsh(gx, gy, seed + 1) - 0.5) * sy_ * 0.6))
    c = np.array(centres)
    d = ((xs[:, None] - c[None, :, 0]) / sx_) ** 2 + ((ys[:, None] - c[None, :, 1]) / sy_) ** 2
    own = d.argmin(axis=1)
    owner = np.full((H, W), -1)
    owner[ys, xs] = own
    for k in range(len(xs)):
        x, y, o = xs[k], ys[k], own[k]
        gl = light[0] * (x - cx) / rx + light[1] * (y - cy) / ry
        lx, ly = (x - c[o, 0]) / sx_, (y - c[o, 1]) / sy_
        loc = -(lx + ly)
        v = GLOBAL_WEIGHT.get(kind, 0.72) * gl + 0.40 * loc + (hsh(o, 7, seed) - 0.5) * 0.22
        t = 0 if v < -0.75 else (1 if v < -0.15 else (2 if v < 0.35 else (3 if v < 0.85 else 4)))
        right = owner[y, min(W - 1, x + 1)]
        below = owner[min(H - 1, y + 1), x]
        if kind == "box" and owner[max(0, y - 1), x] == -1 and below != -1:
            t = max(t, 3)                                       # clipped top plane catches the light
        elif below == -1:
            t = 0                                               # underside of the plant
        elif gl < 0.1 and ly > 0.10 and ((right not in (-1, o)) or (below != o)):
            t = max(0, t - CREVICE[kind])                       # crevice on the lower-right edge of a mass
        if kind == "grass" and t >= 3 and (x + int(hsh(o, 9, seed) * 3)) % 3 == 0 and y < cy:
            t = 4
        layer.px(x, y, ramp[t])
    if kind == "grass":                                         # seed heads on the tallest blades
        for o in range(len(c)):
            m = own == o
            if m.any() and hsh(o, 11, seed) < 0.45:
                j = np.argmin(ys[m])
                layer.px(xs[m][j], ys[m][j], "wd2")
    for i, (fc, n) in enumerate(flowers):                       # flowers: small clusters on lit masses
        k = 0
        for o in sorted(set(own.tolist()), key=lambda o_: hsh(o_, 13 + i, seed)):
            if k >= n:
                break
            m = own == o
            if hsh(o, 17 + i, seed) < 0.5:
                continue
            j = np.argmin(xs[m] + ys[m])
            x, y = xs[m][j], ys[m][j]
            if region[y, x]:
                layer.px(x, y, fc)
                if region[y, min(W - 1, x + 1)]:
                    layer.px(x + 1, y, fc)
                k += 1


v5.foliage = foliage


# ---------------------------------------------------------------- v06 prop materials (colour inside v05 alpha)
def recolour(painter, mapping_fn):
    """Paint with the v05 painter, then recolour each opaque pixel by mapping_fn(x, y, name) (alpha kept)."""
    def paint(L):
        P = Layer()
        painter(P)
        op = P.opaque()
        for y, x in zip(*np.nonzero(op)):
            n = mapping_fn(x, y, v5.name_of(P.a[y, x, :3]), P)
            P.px(x, y, n)
        L.a[op] = P.a[op]
    return paint


def _column(L, cx):
    """v06: the v05 column, then knee braces as round members (lit top, mid, shade, dark underside) with rivet
    pairs, and rivet clusters on the gusset plates."""
    v5.draw_column(L, cx)
    for side in (-1, 1):
        for t in range(0, 31):
            x = cx + side * (8 + t)
            y = 160 - (t * 25) // 30
            for k, c in enumerate(("iw4", "iw2", "iw1", "iw1")):
                L.px(x, y + k, c)
            L.px(x, y + 4, "iw0")
            if t % 6 == 3:
                L.px(x, y + 2, "iw4")
                L.px(x, y + 3, "iw0")
        gx0 = cx + side * 8 - (3 if side < 0 else 0)
        L.rect(gx0, 156, gx0 + 3, 166, "iw2")
        L.vline(gx0, 156, 166, "iw3")
        for ry in (158, 161, 164):
            L.px(gx0 + 1, ry, "iw4")
            L.px(gx0 + 1, ry + 1, "iw0")


def _planter_box_material(kind):
    """Distinct planter materials: 'granite' (v05 stone), 'weathered' (warmer, darker granite with a stain
    line), 'iron-patina' (v05 iron with a teal-grey patina on the rim)."""
    def fn(x, y, n, P):
        if kind == "weathered" and n.startswith("st"):
            return shift(n, -1) if n != "st6" else "st5"
        if kind == "iron-patina" and n == "ir4":
            return "gl1"
        return n
    return fn


SPECIES.update({450: ("grass", 3, 9, ("fo2", "fo3", "fo4", "fo5", "fo6")),     # grass clumps in the east hedge
                451: ("box", 4, 3, ("fo0", "fo1", "fo2", "fo3", "fo4"))})      # low groundcover in the east hedge


def draw_foreground(L):
    """v06: the v05 south parapet, fence and lamp posts; the planting behind the fence is no longer one run of
    equal bumps repeated twice. West: a clipped boxwood hedge (flat top with gentle clipped waves, rounded
    ends). East: a mixed planting of flowering shrubs of three sizes, ornamental grass clumps and low
    groundcover. Rows 286..304 only, so the prop region and pivot are unchanged."""
    for x0, x1 in ((96, 300), (352, 560)):
        v5.stone_box(L, x0, 304, x1, 322, lip=3)
        if x0 == 96:
            hedge = rmask(x0 + 2, 292, x1 - 2, 305)
            for i, sx in enumerate(range(x0 + 2, x1 - 2, 22)):
                if hsh(i, 1, 191) < 0.55:
                    hedge |= rmask(sx + 2, 291, min(x1 - 2, sx + 20), 292)
            for cx_ in (x0 + 2, x1 - 3):
                hedge[292, cx_] = False
            foliage(L, hedge, 97 + x0, (("fl_w", 4),))
        else:
            shrubs = np.zeros((H, W), bool)
            grass = np.zeros((H, W), bool)
            cover = np.zeros((H, W), bool)
            x, i = x0 + 2, 0
            while x < x1 - 4:
                h = hsh(i, 2, 193)
                if h < 0.22:                                  # grass clump: tapered blades
                    w_ = 10
                    for dx in range(w_):
                        top = 287 + abs(dx - w_ // 2) + int(hsh(i, dx, 194) * 3)
                        grass[top:305, x + dx] = True
                elif h < 0.36:                                # low groundcover
                    w_ = 10 + int(hsh(i, 3, 193) * 5)
                    cover |= ellipse(x + w_ / 2, 300, w_ / 2 + 1, 5) & rmask(x, 295, x + w_, 305)
                else:                                         # flowering shrub, three sizes
                    big = hsh(i, 4, 193)
                    w_ = 18 if big < 0.35 else (14 if big < 0.75 else 11)
                    ry = 10 if big < 0.35 else (8 if big < 0.75 else 6)
                    shrubs |= ellipse(x + w_ / 2, 299, w_ / 2 + 1, ry)
                x += w_ - 1
                i += 1
            band = rmask(x0 + 1, 286, x1 - 1, 305)
            shrubs &= band
            grass &= band & ~shrubs
            cover &= band & ~shrubs & ~grass
            foliage(L, shrubs, 97 + x0, (("fl_w", 12), ("fl_r", 6), ("fl_y", 5), ("fl_p", 4)))
            foliage(L, grass, 450)
            foliage(L, cover, 451)
        L.hline(x0, x1, 296, "ir3")                        # v06: lit top rail and finials so the fence reads
        L.hline(x0, x1, 302, "ir1")                        # over the darker clipped hedge
        for x in range(x0 + 1, x1, 4):
            L.vline(x, 294, 304, "ir1")
            L.px(x, 293, "ir4")
    for lx in (150, 520):
        L.rect(lx - 1, 262, lx + 2, 305, "ir1")
        L.vline(lx - 1, 262, 305, "ir3")
        v5.lantern(L, lx, 252)
    # Preserve the exact v05 silhouette too: earlier partial v06 shrub species changed 656 alpha pixels.
    # Reuse the unchanged v05 code painter (not a raster reference) for any original rim pixels missing here.
    reference = Layer()
    v5.draw_foreground(reference)
    original_alpha = reference.opaque()
    missing = original_alpha & ~L.opaque()
    L.a[missing] = reference.a[missing]
    L.a[~original_alpha] = 0


PROP_GROUPS = [
    ("ysort-underdeck-props", [
        ("chicago-lamp", v5.draw_chicago_lamp, 182.5),
        ("planter-stone-west", lambda L: v5.draw_planter_stone(L, 214, 254, 154, 174, 41, (("fl_w", 8), ("fl_p", 3))), 185.5),
        ("bench", lambda L: v5.draw_bench(L, 258, 172, 42), 186.5),
        ("planter-iron", recolour(lambda L: v5.draw_planter_iron(L, 304, 318, 158, 174, 43, (("fl_r", 3),)), _planter_box_material("iron-patina")), 184.5),
        ("planter-stone-east", recolour(lambda L: v5.draw_planter_stone(L, 364, 386, 156, 173, 45, (("fl_w", 5),)), _planter_box_material("weathered")), 184.5),
        ("litter-bin", lambda L: v5.draw_bin(L, 397, 171), 190.5),
        ("civic-kiosk", v5.draw_kiosk, 200.5),
        ("conifer-planter", v5.draw_conifer_planter, 187.5),
    ]),
    ("ysort-l-columns", [
        ("l-column-west", lambda L: _column(L, v5.COLUMN_X[0]), 263.5),
        ("l-column-east", lambda L: _column(L, v5.COLUMN_X[1]), 263.5),
    ]),
    ("ysort-station-stair-east", [
        ("station-stair", v5.draw_stair, 206.5),
        ("east-terrace", v5.draw_east_terrace, 263.5),
    ]),
    ("ysort-plaza-props", [
        ("fountain", v5.muted(v5.draw_fountain, v5.MUTE_FOUNTAIN), 297.5),
        ("planter-column-west", recolour(lambda L: v5.draw_planter_iron(L, 100, 122, 236, 251, 51, (("fl_p", 4),)), _planter_box_material("iron")), 261.5),
        ("planter-column-east", recolour(lambda L: v5.draw_planter_iron(L, 488, 510, 236, 251, 53, (("fl_w", 4),)), _planter_box_material("iron-patina")), 261.5),
        *[("bollard-%d" % y, (lambda yy: lambda L: v5.draw_bollard(L, yy))(y), y + 0.5) for y in v5.BOLLARD_ROWS],
        ("wayfinding-pylon", v5.muted(v5.draw_pylon, v5.MUTE_PYLON), 232.5),
        ("granite-seat-west", lambda L: v5.draw_seat(L, 232), 265.5),
        ("granite-seat-east", lambda L: v5.draw_seat(L, 372), 265.5),
        ("honey-locust-west", lambda L: v5.draw_honey_locust(L, 198, 101), 293.5),
        ("honey-locust-east", lambda L: v5.draw_honey_locust(L, 432, 103), 293.5),
        ("bike-share-dock", v5.muted(v5.draw_bike_dock, v5.MUTE_DOCK), 297.5),
    ]),
    ("ysort-foreground", [
        ("south-parapet-fence", draw_foreground, 340.5),
    ]),
]
v5.PROP_GROUPS = PROP_GROUPS

STATIC = ["ground-street-plaza", "ground-shadow-light", "ground-contact-shadow", "backdrop-facade-north",
          "station-platform-canopy", "backdrop-deck-l-girder", "backdrop-underdeck-storefronts", "station-plate"]
v5.STATIC = STATIC
v5.LAYERS = STATIC + v5.YSORT
v5.ZIP_TIME = ZIP_TIME
LAYERS = v5.LAYERS
YSORT = v5.YSORT
GUIDE = v5.GUIDE
CHANGED_FROM_V05 = ("ground-street-plaza", "ground-contact-shadow", "backdrop-facade-north", "station-platform-canopy",
                    "backdrop-deck-l-girder", "ysort-underdeck-props", "ysort-l-columns", "ysort-station-stair-east",
                    "ysort-plaza-props", "ysort-foreground")

_V05_BUILD_LAYERS = v5.build_layers


def build_layers():
    """The v05 build (with the v06 painters above), plus the new contact-shadow layer."""
    layers, props = _V05_BUILD_LAYERS()
    g, s = Layer(), Layer()
    g.a[:] = np.array(layers["ground-street-plaza"])
    s.a[:] = np.array(layers["ground-shadow-light"])
    layers["ground-contact-shadow"] = Image.fromarray(contact_shadow(g, s, layers, props).a, "RGBA")
    return {k: layers[k] for k in LAYERS}, props


v5.build_layers = build_layers


def pxo_bytes(layers, guide, flat):
    """The v05 .pxo writer (pxo_version 7) with the v06 export name."""
    data = v5.pxo_bytes(layers, guide, flat)
    zin = zipfile.ZipFile(io.BytesIO(data))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for info in zin.infolist():
            payload = zin.read(info.filename)
            if info.filename == "data.json":
                payload = payload.replace(b"chicago-loop-state-lake-v05", b"chicago-loop-state-lake-v06")
            z.writestr(zipfile.ZipInfo(info.filename, ZIP_TIME), payload, zipfile.ZIP_DEFLATED)
    return buf.getvalue()


def rel(path):
    return v5.rel(path)


def build(out=OUT):
    out.mkdir(parents=True, exist_ok=True)
    layers, props = build_layers()
    guide = v5.walkmask()
    flat = v5.merged(layers)
    rt = v5.runtime_layers(layers)
    files = {}
    for name in ["ground-far"] + YSORT:
        data = v5.png_bytes(rt[name])
        path = out / f"{PREFIX}_{name}_{VARIANT}_{STAMP}.png"
        path.write_bytes(data)
        files[name] = {"file": rel(path), "sha256": v5.sha(data), "hash_algorithm": "sha256-bytes", "role": "runtime-candidate texture (not in game/)"}
    vis_report, low = v5.visibility_report(layers, props)
    data = v5.png_bytes(v5.reveal_mask_image(low))
    path = out / f"{PREFIX}_occlusion-reveal-mask_{VARIANT}_{STAMP}.png"
    path.write_bytes(data)
    files["occlusion-reveal-mask"] = {"file": rel(path), "sha256": v5.sha(data), "hash_algorithm": "sha256-bytes"}
    colours = v5.palette_colours(layers)
    pal_text = "GIMP Palette\nName: chicago-loop-state-lake-v06\nColumns: 16\n#\n" + "".join(
        f"{r:3d} {g:3d} {b:3d}\t{v5.name_of((r, g, b))}\n" for r, g, b in colours)
    extra = {
        "flat-source": (f"{PREFIX}_flat-source_{VARIANT}_{STAMP}.png", v5.png_bytes(flat)),
        "walkmask-guide": (f"{PREFIX}_{GUIDE}_{VARIANT}_{STAMP}.png", v5.png_bytes(guide)),
        "openraster": (f"{PREFIX}_layered-source_{VARIANT}_{STAMP}.ora", v5.ora_bytes(layers, guide, flat)),
        "pixelorama": (f"{PREFIX}_layered-source_{VARIANT}_{STAMP}.pxo", pxo_bytes(layers, guide, flat)),
        "palette-gpl": (f"{PREFIX}_palette_{VARIANT}_{STAMP}.gpl", pal_text.encode("utf-8")),
    }
    for key, (name, data) in extra.items():
        (out / name).write_bytes(data)
        text = name.endswith(".gpl")
        files[key] = {"file": rel(out / name), "sha256": v5.text_sha(data) if text else v5.sha(data),
                      "hash_algorithm": "sha256-text-lf-v1" if text else "sha256-bytes"}
    v05m = json.loads(V05_MANIFEST.read_text(encoding="utf-8"))
    manifest = {
        "project": "Worlds Between",
        "scene": "Chicago Loop arrival block: State St x Lake St under the Lake Street elevated (State/Lake)",
        "status": ("UNAPPROVED, NONRUNTIME candidate v06: one bounded native materials/depth pass over v05 after root's "
                   "changes_requested verdict. Not wired: no game/ file is created or edited; the v05 scene is shown with these "
                   "textures only by a test-only Godot capture harness. Not art approval; no counter, ledger or Site change."),
        "canon": v05m["canon"],
        "authorship": ("Every pixel is authored by code as explicit clusters with a fixed integer hash (no RNG, no generated image, "
                       "no underpainting, no reference read). This tool imports the v05 author unchanged and overrides the v06 painters. "
                       "Initial v06 implementation by Claude (signed-in Claude Max, firstParty); bounded ground/foliage finish and validation by Codex during creator-authorized quota gap."),
        "pass_of": {"base_author": rel(V05_AUTHOR), "base_author_sha256_text_lf": v5.text_sha(V05_AUTHOR.read_bytes()),
                    "base_manifest": rel(V05_MANIFEST), "base_manifest_sha256_text_lf": v5.text_sha(V05_MANIFEST.read_bytes()),
                    "changed_layers": list(CHANGED_FROM_V05),
                    "unchanged_layers": [n for n in LAYERS if n not in CHANGED_FROM_V05],
                    "new_layers": ["ground-contact-shadow"]},
        "toolchain": {"python": sys.version.split()[0], "pillow": PIL.__version__, "numpy": np.__version__},
        "provenance": v5.origin_counts(layers, props),
        "canvas": [W, H], "visible_art_rows": [62, 317], "palette_colours": len(colours),
        "layers_bottom_to_top": LAYERS + [GUIDE + " (hidden, locked)"],
        "runtime_layers": [{"name": "ground-far", "from": STATIC}] + [{"name": n} for n in YSORT],
        "ysort_props": props,
        "geometry": {"walk": v5.WALK, "blocks": v5.BLOCKS, "spawn": v5.SPAWN, "kiosk": v5.KIOSK, "stair": v5.STAIR, "pylon": v5.PYLON,
                     "interact_radius": v5.INTERACT_RADIUS, "deck_rows": [v5.DECK_TOP, v5.DECK_BOTTOM], "station_plate": v5.PLATE},
        "hero_visibility": vis_report,
        "pixelorama": f"pxo_version 7, color_mode 5, 1 frame x {len(LAYERS) + 1} layers (guides-walkmask hidden + locked); ORA lists the same layers",
        "files": files,
        "source": rel(Path(__file__).resolve()),
        "source_sha256_text_lf": v5.text_sha(Path(__file__).resolve().read_bytes()),
        "completed_by": "Codex, after interrupted Claude source; no inference or paid fallback",
    }
    path = out / f"{PREFIX}_layer-manifest_{VARIANT}_{STAMP}.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(path)
    return manifest


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":
        lay, pr = build_layers()
        v5.merged(lay).save(sys.argv[2])
        print(json.dumps(v5.visibility_report(lay, pr)[0]))
    else:
        build()
