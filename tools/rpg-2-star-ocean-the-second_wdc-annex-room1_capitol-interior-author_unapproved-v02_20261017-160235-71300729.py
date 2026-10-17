"""Washington, D.C. survey annex room 1 (遗址外环 / Ruin Outer Ring), UNAPPROVED v02 quality pass.

v01 (65b9618f, hand-placed primitives) stays untouched as the immutable baseline. v02 follows the
Codex nonruntime art-direction reference (a82fde43, generated with Codex's built-in image tool) for
composition and detail density, and is built like this:

1. Import: the reference is recomposed to 640x360 with a box filter in two bands, so the wall,
   window and Capitol dome sit below the 62 px UI header (wall band ref rows 0-300 -> y 58-152, floor
   ref rows 300-941 -> y 152-360; x scale 640/1672).
2. Grade: the floor is darkened toward the accepted NYC/Yonkers interiors' value range, with depth
   falloff toward the near edge and sides; sun shafts are compressed; the exterior keeps its light.
3. Palette reduction: median cut + k-means to UNDERPAINT_COLOURS colours, no dithering, then a
   cluster pass that folds isolated pixels into the nearest-coloured 4-neighbour cluster when the
   colour step is small (high-contrast single-pixel accents are kept).
4. Hand corrections in declared palette colours: a descending east stairwell for the "go deeper"
   door, cleared door thresholds, contact shadows, teal survey accents and a darker bench band
   behind the clue-label row.
5. Layers: the quantized underpainting is split by region into editable binary-alpha layers, hand
   layers sit above, and the foreground stubs are the top layer and a separate runtime overlay PNG
   that the room draws above the heroine.

The three 64x64 clue fixtures are redrawn by hand (no underpainting) in the shared ramps.
Writes merged PNG, layered .ora and Pixelorama .pxo (pxo_version 7) for every asset, a manifest
with sha256 hashes and provenance counts, and runtime copies. --preview DIR writes previews only.
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
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261017-160235-71300729"
PREFIX = "rpg-2-star-ocean-the-second_wdc-annex-room1"
OUT = ROOT / "outputs/wdc-sr1-v02_71300729"
RUNTIME_SCENE_DIR = ROOT / "game/assets/environments/wdc-survey-room1"
RUNTIME_PROP_DIR = ROOT / "game/assets/props/wdc-annex-room1"
REFERENCE = ROOT / "outputs/rpg-2-star-ocean-the-second_wdc-annex-room1_capitol-civic-interior-art-direction-reference_nonruntime-v01_20261017-032700-a82fde43.png"
REFERENCE_SHA256 = None  # recorded in the manifest at build time
PIXELORAMA_VERSION = "v1.2.3-stable"
W, H = 640, 360
FW = FH = 64
CLUES = [(163, 165), (320, 165), (477, 165)]
FIXTURE_OFFSET = (-32, 2)
UNDERPAINT_COLOURS = 64
WALL_REF_ROWS, WALL_Y = (0, 300), (58, 152)
FLOOR_REF_ROWS, FLOOR_Y = (300, 941), (152, 360)

# Hand palette shared by the corrections and the fixtures (light from the upper left).
HP = {
    "ink": "#1b1612",
    "stone_0": "#2f2a25", "stone_1": "#4a433b", "stone_2": "#675d51", "stone_3": "#857a6a",
    "stone_4": "#a39782", "stone_5": "#c2b59c", "stone_6": "#ddd0b5",
    "brick_0": "#4a2219", "brick_1": "#6e3324", "brick_2": "#8f4630", "brick_3": "#b0633f",
    "seal": "#2a2420",
    "wood_0": "#2b1a11", "wood_1": "#46291a", "wood_2": "#643b23", "wood_3": "#82512f", "wood_4": "#a46d40",
    "brass_0": "#3f2e12", "brass_1": "#6e521d", "brass_2": "#9c7a2c", "brass_3": "#c9a245", "brass_4": "#ecd07a",
    "verd_0": "#2e5a4c", "verd_1": "#4f8a72",
    "steel_0": "#1f2629", "steel_1": "#353f43", "steel_2": "#525e62", "steel_3": "#7a878a", "steel_4": "#aab6b6",
    "teal_0": "#0f2a2b", "teal_1": "#1b4847", "teal_2": "#2b6f6b", "teal_3": "#47a197", "teal_4": "#7fd4c6",
    "glow": "#d4fff3",
    "paper_0": "#9e9076", "paper_1": "#cbbd9c", "paper_2": "#ece0c3",
    "red": "#d4473a", "amber": "#e8a33a",
    "leaf_0": "#1f3016", "leaf_1": "#33501f", "leaf_2": "#52722b", "leaf_3": "#7c9a3c",
    "void": "#0e1214",
}
HRGB = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in HP.items()}
SHADOW_RGBA = (16, 13, 10, 0xA0)

SCENE_LAYERS = [
    "exterior-sky-dome-foliage-underpaint",
    "back-wall-columns-niches-underpaint",
    "floor-marble-inlay-underpaint",
    "rubble-ivy-midground-underpaint",
    "hand-floor-and-bench-corrections",
    "hand-east-stairwell-door",
    "hand-survey-teal-accents",
    "foreground-stubs-occluder",
]
FIXTURE_LAYERS = ["contact-shadow", "structure", "lit-edges", "clue-detail"]


# ---------------------------------------------------------------- pixel helpers (numpy RGBA)

def put(a, x, y, c):
    if 0 <= x < a.shape[1] and 0 <= y < a.shape[0]:
        a[y, x] = (*HRGB[c], 255)


def box(a, x0, y0, x1, y1, c):
    """Filled inclusive rectangle."""
    h, w = a.shape[:2]
    x0, x1 = max(0, min(x0, x1)), min(w - 1, max(x0, x1))
    y0, y1 = max(0, min(y0, y1)), min(h - 1, max(y0, y1))
    if x0 <= x1 and y0 <= y1:
        a[y0:y1 + 1, x0:x1 + 1] = (*HRGB[c], 255)


def seg(a, pts, c, width=1):
    img = Image.new("L", (a.shape[1], a.shape[0]), 0)
    ImageDraw.Draw(img).line(pts, fill=255, width=width)
    a[np.array(img) > 0] = (*HRGB[c], 255)


def poly_mask(pts, w=W, h=H):
    img = Image.new("L", (w, h), 0)
    ImageDraw.Draw(img).polygon(pts, fill=255)
    return np.array(img) > 0


def ellipse_mask(bb, w=W, h=H):
    img = Image.new("L", (w, h), 0)
    ImageDraw.Draw(img).ellipse(bb, fill=255)
    return np.array(img) > 0


def fill(a, mask, c):
    a[mask] = (*HRGB[c], 255)


def outline(a, mask, c):
    """1 px outline just outside mask."""
    grow = mask.copy()
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        grow |= np.roll(np.roll(mask, dy, 0), dx, 1)
    fill(a, grow & ~mask, c)


def checker(h=H, w=W, phase=0):
    yy, xx = np.mgrid[0:h, 0:w]
    return ((xx + yy + phase) % 2) == 0


def digit(a, x, y, ch, c):
    glyphs = {"4": ["1.1", "1.1", "111", "..1", "..1"], "7": ["111", "..1", "..1", ".1.", ".1."]}
    for j, row in enumerate(glyphs[ch]):
        for i, v in enumerate(row):
            if v == "1":
                put(a, x + i, y + j, c)


# ---------------------------------------------------------------- 1-3: import, grade, palette reduction

def underpaint_rgb():
    ref = Image.open(REFERENCE).convert("RGB")
    rw = ref.size[0]

    def band(rows, ys):
        return np.asarray(ref.resize((W, ys[1] - ys[0]), Image.Resampling.BOX, box=(0, rows[0], rw, rows[1])), np.float32)

    a = np.zeros((H, W, 3), np.float32)
    a[WALL_Y[0]:WALL_Y[1]] = band(WALL_REF_ROWS, WALL_Y)
    a[FLOOR_Y[0]:FLOOR_Y[1]] = band(FLOOR_REF_ROWS, FLOOR_Y)
    # rows hidden under the UI header: a dark continuation of the wall top
    for y in range(WALL_Y[0]):
        a[y] = a[WALL_Y[0]] * (0.35 + 0.4 * y / WALL_Y[0])
    return a


def grade(a):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    lum = (a @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    floor = yy >= WALL_Y[1] - 2
    exterior = exterior_mask(a)
    # floor: value range of the accepted interiors, falloff toward the near edge and the sides
    depth = ((yy - WALL_Y[1]) / (318 - WALL_Y[1])).clip(0, 1)
    side = (np.abs(xx - 320) / 320) ** 2
    k = np.where(floor, 0.80 - 0.12 * depth - 0.12 * side, 0.90)
    # compress the brightest sun-shaft highlights on the floor
    hi = np.clip((lum - 170) / 85, 0, 1)
    g = a * k[..., None] * np.where(floor[..., None], 1 - 0.22 * hi, 1)
    # cooler shadows, warmer lights
    l2 = (g @ np.array([0.299, 0.587, 0.114], np.float32))[..., None] / 255
    g = g + np.array([-5, -1, 5], np.float32) * (1 - l2) * 1.2 + np.array([4, 2, -3], np.float32) * l2
    # floor saturation pulled slightly toward neutral stone
    m = g.mean(axis=2, keepdims=True)
    g = np.where(floor[..., None], m + (g - m) * 0.88, g)
    # bench and wall base behind the clue-label row (y 118-156): a quieter, darker band
    ramp = np.clip((yy - 110) / 12, 0, 1) * np.clip((158 - yy) / 4, 0, 1)
    g = np.where(exterior[..., None], g, g * (1 - 0.26 * ramp)[..., None])
    g[exterior] = a[exterior] * 0.96
    img = Image.fromarray(g.clip(0, 255).astype(np.uint8))
    # floor local contrast (grout and slab edges), then crisp cluster edges before reduction
    contrast = np.asarray(img.filter(ImageFilter.UnsharpMask(radius=3, percent=45, threshold=2)))
    mixed = np.where(floor[..., None], contrast, np.asarray(img))
    img = Image.fromarray(mixed.astype(np.uint8))
    return img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=55, threshold=3))


def exterior_mask(a):
    """Sky, distant Capitol and far foliage seen through the window and the open sides."""
    yy, xx = np.mgrid[0:H, 0:W]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    sky = (b > r + 6) & (b > 120)
    regions = ((xx >= 287) & (xx <= 356) & (yy >= 62) & (yy <= 120)) | \
              ((xx <= 50) & (yy >= 58) & (yy <= 140)) | ((xx >= 604) & (yy >= 58) & (yy <= 128))
    foliage_far = regions & (g > r) & (yy < 140)
    return regions & (sky | foliage_far)


def reduce_palette(img):
    q = img.quantize(colors=UNDERPAINT_COLOURS, method=Image.Quantize.MEDIANCUT, kmeans=8, dither=Image.Dither.NONE)
    pal = np.array(q.getpalette()[:UNDERPAINT_COLOURS * 3], np.int32).reshape(-1, 3)
    idx = np.asarray(q).astype(np.int32)
    return idx, pal


def isolated(idx):
    same = np.zeros(idx.shape, np.int32)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        same += np.roll(np.roll(idx, dy, 0), dx, 1) == idx
    return same == 0


def cluster_pass(idx, pal, limit=34, passes=2):
    """Fold isolated pixels into the nearest-coloured neighbour cluster when the step is small."""
    idx = idx.copy()
    changed = 0
    for _ in range(passes):
        iso = isolated(idx)
        best = np.full(idx.shape, -1, np.int32)
        best_d = np.full(idx.shape, 1e9)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            n = np.roll(np.roll(idx, dy, 0), dx, 1)
            d = np.sqrt(((pal[n] - pal[idx]) ** 2).sum(-1))
            better = d < best_d
            best[better], best_d[better] = n[better], d[better]
        fold = iso & (best_d < limit)
        idx[fold] = best[fold]
        changed += int(fold.sum())
    return idx, changed


# ---------------------------------------------------------------- region masks for the layer split

def rubble_mask():
    left = poly_mask([(0, 132), (18, 128), (40, 134), (58, 146), (66, 160), (62, 178), (56, 192), (34, 198), (0, 200)])
    right = poly_mask([(548, 136), (570, 130), (600, 132), (628, 140), (640, 142), (640, 212), (612, 208),
                       (590, 200), (570, 188), (552, 170)])
    return left | right


def foreground_mask():
    """Corner stubs and ivy in front of the walk area; the room draws this layer above the heroine."""
    left = poly_mask([(0, 249), (30, 251), (40, 257), (40, 266), (57, 266), (57, 292), (66, 296), (82, 300),
                      (86, 318), (0, 318)])
    right = poly_mask([(556, 286), (572, 281), (584, 279), (584, 267), (603, 267), (603, 257), (616, 251),
                       (640, 247), (640, 318), (552, 318)])
    m = left | right
    m[318:] = False
    # keep the exit / next-room marker discs clear so the door markers always draw above the stubs
    yy, xx = np.mgrid[0:H, 0:W]
    for cx, cy in ((57, 257), (580, 257)):
        m &= np.hypot(xx + 0.5 - cx, yy + 0.5 - cy) > 17.5
    return m


# ---------------------------------------------------------------- 4: hand corrections

def shade(a, base, pal, mask, factor):
    """Re-tone base pixels under mask to the nearest underpaint-palette colour of base * factor."""
    ys, xs = np.nonzero(mask)
    if len(ys) == 0:
        return
    want = np.clip(base[ys, xs, :3].astype(np.float32) * factor, 0, 255)
    d = ((want[:, None, :] - pal[None, :, :].astype(np.float32)) ** 2).sum(-1)
    a[ys, xs, :3] = pal[d.argmin(1)].astype(np.uint8)
    a[ys, xs, 3] = 255


def hand_floor_and_bench(base, pal):
    """Palette-preserving re-toning: the bench foot shadow and contact shadows that seat the rubble
    piles and the corner stubs."""
    a = np.zeros((H, W, 4), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    shade(a, base, pal, (yy >= 152) & (yy <= 154) & (xx >= 70) & (xx <= 566), 0.62)
    shade(a, base, pal, (yy >= 155) & (yy <= 156) & (xx >= 70) & (xx <= 566), 0.80)
    for bb in [(-6, 188, 72, 206), (548, 196, 646, 216), (24, 292, 84, 310), (548, 290, 610, 308)]:
        core = ellipse_mask(bb)
        edge = ellipse_mask((bb[0] - 5, bb[1] - 3, bb[2] + 5, bb[3] + 3)) & ~core
        shade(a, base, pal, core, 0.70)
        shade(a, base, pal, edge, 0.84)
    return a


def hand_east_stairwell(base, pal):
    """A stair opening in the east floor, entered from the south and descending north to the records
    chamber, lit teal from below. The kerb is re-toned floor stone so the opening reads as cut into
    the same floor; each tread is lower and darker than the one in front of it."""
    a = np.zeros((H, W, 4), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    x0, x1, y0, y1 = 592, 632, 222, 251
    # kerb: lit north/west edges, shadowed east inner edge, open toward the south
    kerb = (xx >= x0 - 3) & (xx <= x1 + 2) & (yy >= y0 - 3) & (yy <= y1)
    shade(a, base, pal, kerb, 1.0)
    shade(a, base, pal, kerb & ((yy <= y0 - 2) | (xx <= x0 - 2)), 1.30)
    shade(a, base, pal, kerb & (xx >= x1 + 1), 0.72)
    # treads, front (south, highest and lit) to back (north, deepest); a worn nosing on each
    # tread's north edge and the drop's shadow behind it
    treads = [("stone_3", "stone_4"), ("stone_2", "stone_3"), ("stone_1", "stone_2"), ("stone_0", "stone_1"),
              ("ink", "stone_0"), ("void", "teal_0")]
    for k, (top, nose) in enumerate(treads):
        ty1 = y1 - k * 5
        ty0 = ty1 - 4
        box(a, x0, max(y0, ty0), x1, ty1, top)
        box(a, x0, max(y0, ty0), x1, max(y0, ty0), nose)
        if ty0 - 1 >= y0:
            box(a, x0, ty0 - 1, x1, ty0 - 1, "void")
    # inner side walls: the west face in light, the east face in shadow, both darker with depth
    for k in range(6):
        ty1 = y1 - k * 5
        ty0 = max(y0, ty1 - 4)
        box(a, x0, ty0, x0 + 1, ty1, ["stone_2", "stone_1", "stone_1", "stone_0", "ink", "void"][k])
        box(a, x1 - 1, ty0, x1, ty1, ["stone_1", "stone_0", "ink", "void", "void", "void"][k])
    # teal light rising from the chamber at the bottom of the flight
    box(a, x0 + 4, y0, x1 - 4, y0 + 2, "teal_1")
    box(a, x0 + 10, y0, x1 - 10, y0 + 1, "teal_2")
    for x in range(x0 + 3, x1 - 2, 3):
        put(a, x, y0 + 3, "teal_0")
    # bronze hand rails on the east and west kerbs, posts at the ends
    for rx in (x0 - 2, x1 + 1):
        box(a, rx, y0 - 2, rx, y1 - 1, "brass_2")
        box(a, rx, y0 - 3, rx, y0 - 2, "brass_3")
        box(a, rx, y1 - 2, rx, y1 - 1, "brass_1")
    # ivy creeping over the west kerb
    rng = random.Random(0x5A1E)
    for y in range(y0 - 3, y0 + 12):
        if rng.random() < 0.5:
            put(a, x0 - 4 + rng.choice((0, -1)), y, rng.choice(("leaf_1", "leaf_2", "leaf_3")))
    return a


def hand_survey_accents():
    """Teal survey accents: a beacon on the window sill and status lights on the brass survey posts."""
    a = np.zeros((H, W, 4), np.uint8)
    # beacon on the window sill: brass foot, teal lamp
    box(a, 296, 113, 299, 116, "brass_2")
    box(a, 297, 110, 298, 112, "teal_3")
    put(a, 297, 109, "glow")
    # status lights on the two brass survey posts flanking the centre bay
    for x, y in [(232, 130), (412, 130)]:
        put(a, x, y, "teal_4")
        put(a, x, y + 2, "red")
    return a


# ---------------------------------------------------------------- scene assembly

def build_scene(preview=None):
    rgb = underpaint_rgb()
    graded = grade(rgb)
    idx0, pal = reduce_palette(graded)
    iso_before = float(isolated(idx0).mean())
    idx, folded = cluster_pass(idx0, pal)
    iso_after = float(isolated(idx).mean())
    under = np.zeros((H, W, 4), np.uint8)
    under[..., :3] = pal[idx].astype(np.uint8)
    under[..., 3] = 255
    yy, xx = np.mgrid[0:H, 0:W]
    ext = exterior_mask(rgb)
    rub = rubble_mask()
    fg = foreground_mask()
    wall = (yy < WALL_Y[1]) & ~ext & ~rub & ~fg
    floor = (yy >= WALL_Y[1]) & ~ext & ~rub & ~fg

    def region(mask):
        l = np.zeros((H, W, 4), np.uint8)
        l[mask] = under[mask]
        return l

    hands = [hand_floor_and_bench(under, pal), hand_east_stairwell(under, pal), hand_survey_accents()]
    final = under.copy()
    for l in hands:
        m = l[..., 3] > 0
        final[m] = l[m]
    fg_layer = np.zeros((H, W, 4), np.uint8)
    fg_layer[fg] = final[fg]
    hands = [np.where(fg[..., None], 0, l).astype(np.uint8) for l in hands]
    layers = [region(ext), region(wall), region(floor), region(rub & ~fg)] + hands + [fg_layer]
    names = SCENE_LAYERS
    flat = np.zeros((H, W, 4), np.uint8)
    for l in layers:
        m = l[..., 3] > 0
        flat[m] = l[m]
    assert (flat == final).all() and (flat[..., 3] == 255).all()
    # provenance: which layer supplies each visible pixel
    owner = np.full((H, W), -1, np.int16)
    for i, l in enumerate(layers):
        owner[l[..., 3] > 0] = i
    vis = np.zeros((H, W), bool)
    vis[62:318] = True
    hand_ids = {4, 5, 6}
    hand_visible = int(np.isin(owner[vis], list(hand_ids)).sum())
    stats = {
        "underpaint_colours": UNDERPAINT_COLOURS,
        "isolated_pixel_fraction_before_cluster_pass": round(iso_before, 4),
        "isolated_pixel_fraction_after_cluster_pass": round(iso_after, 4),
        "pixels_folded_by_cluster_pass": folded,
        "visible_rows": "y 62-317 (between the UI header and footer)",
        "visible_pixels": int(vis.sum()),
        "visible_pixels_from_hand_layers": hand_visible,
        "visible_pixels_from_underpainting_layers": int(vis.sum()) - hand_visible,
        "foreground_overlay_pixels": int(fg.sum()),
        "unique_colours_merged": int(len(np.unique(final[..., :3].reshape(-1, 3), axis=0))),
    }
    if preview:
        Image.fromarray(final).save(Path(preview) / "scene.png")
        Image.fromarray(final).resize((1280, 720), Image.Resampling.NEAREST).save(Path(preview) / "scene2x.png")
        Image.fromarray(fg_layer).save(Path(preview) / "fg.png")
    palette_hex = sorted({"#%02x%02x%02x" % tuple(int(v) for v in p) for p in final[..., :3].reshape(-1, 3)})
    return [Image.fromarray(l) for l in layers], names, stats, palette_hex, fg_layer, under


# ---------------------------------------------------------------- clue fixtures (64x64, hand drawn)

def f_layer():
    return np.zeros((FH, FW, 4), np.uint8)


def f_shadow(bb):
    a = f_layer()
    a[ellipse_mask(bb, FW, FH)] = SHADOW_RGBA
    return a


def fmask(pts):
    return poly_mask(pts, FW, FH)


def fixture_layered_wall():
    """分层墙面 / Layered Wall: a cut wall specimen on a pallet. Dressed sandstone with a walkway
    moulding sits on a dark sealing course over older brick; the same teal age tag is fixed to both
    layers. A survey camera on a tripod photographs the original face."""
    shadow = f_shadow((2, 49, 62, 61))
    body = f_layer()
    # timber pallet
    box(body, 4, 52, 46, 53, "wood_3")
    box(body, 4, 54, 46, 54, "wood_1")
    for x0 in (5, 23, 41):
        box(body, x0, 55, x0 + 4, 57, "wood_2")
        box(body, x0, 57, x0 + 4, 57, "wood_1")
    for x in (15, 31):
        put(body, x, 52, "wood_1")
    # block silhouette: broken top profile over a front face
    tops = [19, 18, 17, 17, 16, 16, 17, 18, 18, 17, 15, 14, 14, 15, 16, 16, 15, 15, 16, 17, 17, 16, 15, 15, 16, 18,
            19, 19, 18, 17]
    face = np.zeros((FH, FW), bool)
    for i, t in enumerate(tops):
        face[t:52, 8 + i] = True
    outline(body, face, "ink")
    yy, xx = np.mgrid[0:FH, 0:FW]
    # top surface (broken, sunlit) then the front face courses
    fill(body, face & (yy < 21), "stone_5")
    fill(body, face & (yy >= 21) & (yy <= 33), "stone_4")
    fill(body, face & (yy >= 34) & (yy <= 35), "seal")
    fill(body, face & (yy >= 36), "brick_1")
    lit = f_layer()
    for i, t in enumerate(tops):
        put(lit, 8 + i, t, "stone_6")
        if i % 4 == 1:
            put(lit, 8 + i, t + 2, "stone_4")
    fill(lit, face & (yy == 21), "stone_3")
    # walkway moulding on the upper (later) layer
    box(lit, 8, 24, 37, 24, "stone_6")
    box(lit, 8, 25, 37, 25, "stone_5")
    box(lit, 8, 26, 37, 26, "stone_2")
    # ashlar joints and tooling
    for x in (17, 28):
        box(lit, x, 27, x, 33, "stone_2")
    box(lit, 8, 30, 16, 30, "stone_3")
    box(lit, 29, 30, 37, 30, "stone_3")
    for x, y in [(11, 28), (21, 31), (33, 28), (24, 22)]:
        put(lit, x, y, "stone_5")
    box(lit, 8, 33, 37, 33, "stone_2")
    # crumbling seal course
    for x in (12, 20, 31):
        put(lit, x, 34, "stone_1")
    # brick running bond: 2 px brick + 1 px mortar, alternating offsets
    for row, y in enumerate(range(36, 51, 3)):
        off = 0 if row % 2 else 3
        box(lit, 8, y + 2, 37, y + 2, "stone_2")
        for x in range(8 + off, 38, 6):
            box(lit, x, y, x, y + 1, "stone_2")
        for x in range(9 + off, 37, 6):
            put(lit, x, y, "brick_3" if (x + row) % 3 else "brick_2")
            if x + 3 < 38:
                put(lit, x + 3, y + 1, "brick_0")
    # left edge lit, right edge in shade
    box(lit, 8, 22, 8, 50, "stone_5")
    box(lit, 37, 22, 37, 33, "stone_2")
    box(lit, 37, 36, 37, 50, "brick_0")
    box(lit, 9, 51, 37, 51, "brick_0")
    # survey camera on a tripod aimed at the face
    for lx in (47, 54, 61):
        seg(body, [(54, 36), (lx, 58)], "steel_1")
    seg(lit, [(54, 37), (48, 57)], "steel_3")
    box(body, 53, 33, 55, 36, "steel_1")
    box(body, 46, 25, 61, 33, "ink")
    box(body, 47, 26, 60, 32, "steel_2")
    box(body, 43, 27, 46, 31, "ink")
    box(body, 44, 28, 46, 30, "steel_0")
    box(lit, 47, 26, 60, 26, "steel_4")
    box(lit, 47, 27, 47, 32, "steel_3")
    box(lit, 48, 32, 60, 32, "steel_1")
    detail = f_layer()
    # identical teal age tags on both layers
    for tx, ty in [(25, 28), (12, 41)]:
        box(detail, tx, ty, tx + 7, ty + 4, "teal_2")
        box(detail, tx + 1, ty + 1, tx + 6, ty + 3, "paper_2")
        box(detail, tx + 1, ty + 1, tx + 6, ty + 1, "teal_3")
        box(detail, tx + 2, ty + 3, tx + 5, ty + 3, "teal_1")
        put(detail, tx + 7, ty, "glow")
    # lens glass, record light, faint scan dots toward the face
    put(detail, 44, 29, "teal_4")
    put(detail, 45, 28, "glow")
    put(detail, 58, 28, "red")
    box(detail, 50, 28, 55, 29, "steel_0")
    for x in (39, 41):
        put(detail, x, 29, "teal_3")
    # ivy sprig over the broken top-left corner
    for x, y, c in [(9, 18, "leaf_2"), (10, 17, "leaf_3"), (8, 20, "leaf_1"), (9, 21, "leaf_2"), (8, 23, "leaf_1"),
                    (9, 24, "leaf_3"), (8, 26, "leaf_2"), (11, 18, "leaf_1"), (12, 17, "leaf_2")]:
        put(detail, x, y, c)
    return [shadow, body, lit, detail]


def fixture_broken_index():
    """残缺索引 / Broken Index: an oak card catalogue with one drawer slot empty and one drawer pulled
    out with gaps in its cards; a survey reader beside it lists the identifiers with a missing run."""
    shadow = f_shadow((3, 50, 62, 61))
    body = f_layer()
    # cabinet: top, front, plinth, feet
    box(body, 6, 9, 42, 57, "ink")
    box(body, 7, 10, 41, 13, "wood_4")
    box(body, 7, 14, 41, 53, "wood_2")
    box(body, 7, 54, 41, 55, "wood_1")
    box(body, 8, 56, 11, 58, "wood_1")
    box(body, 37, 56, 40, 58, "wood_1")
    lit = f_layer()
    box(lit, 7, 10, 41, 10, "paper_1")
    for x in (12, 21, 33):
        box(lit, x, 11, x + 4, 11, "wood_3")
    box(lit, 7, 13, 41, 13, "wood_1")
    box(lit, 7, 14, 7, 53, "wood_3")
    box(lit, 41, 14, 41, 53, "wood_1")
    detail = f_layer()
    for col in range(3):
        for row in range(4):
            x0, y0 = 9 + col * 11, 15 + row * 9
            if (col, row) == (2, 1):
                # the empty drawer slot
                box(body, x0, y0, x0 + 9, y0 + 7, "void")
                box(lit, x0, y0, x0 + 9, y0, "wood_0")
                box(lit, x0, y0 + 1, x0, y0 + 7, "wood_0")
                box(lit, x0 + 2, y0 + 6, x0 + 8, y0 + 7, "wood_1")
                continue
            if (col, row) == (1, 3):
                continue
            box(body, x0, y0, x0 + 9, y0 + 7, "wood_3")
            box(lit, x0, y0, x0 + 9, y0, "wood_4")
            box(lit, x0, y0 + 7, x0 + 9, y0 + 7, "wood_1")
            box(lit, x0 + 9, y0 + 1, x0 + 9, y0 + 6, "wood_2")
            # brass card holder with a paper label, and a cup pull
            box(detail, x0 + 3, y0 + 2, x0 + 6, y0 + 3, "brass_2")
            box(detail, x0 + 4, y0 + 2, x0 + 5, y0 + 2, "paper_2")
            put(detail, x0 + 4, y0 + 5, "brass_3")
            put(detail, x0 + 5, y0 + 5, "brass_1")
    # pulled-out drawer: slot dark above, drawer box projecting toward the viewer
    x0, y0 = 20, 42
    box(body, x0, y0, x0 + 9, y0 + 2, "void")
    box(body, x0 - 1, y0 + 3, x0 + 10, y0 + 13, "ink")
    box(body, x0, y0 + 3, x0 + 9, y0 + 7, "wood_1")
    box(body, x0, y0 + 8, x0 + 9, y0 + 12, "wood_3")
    box(lit, x0, y0 + 8, x0 + 9, y0 + 8, "wood_4")
    box(lit, x0, y0 + 12, x0 + 9, y0 + 12, "wood_1")
    box(detail, x0 + 3, y0 + 9, x0 + 6, y0 + 10, "brass_2")
    put(detail, x0 + 4, y0 + 9, "paper_2")
    # cards standing in the drawer with gaps
    for x in (x0 + 1, x0 + 2, x0 + 4, x0 + 7, x0 + 8):
        box(detail, x, y0 + 3, x, y0 + 6, "paper_2")
        put(detail, x, y0 + 6, "paper_0")
    # cards fallen on the floor
    for cx, cy in [(43, 55), (47, 58), (12, 60), (38, 61)]:
        box(detail, cx, cy, cx + 4, cy + 1, "paper_2")
        box(detail, cx, cy + 2, cx + 4, cy + 2, "paper_0")
    # survey reader on a fold-out stand
    seg(body, [(52, 46), (49, 58)], "steel_1")
    seg(body, [(56, 46), (58, 58)], "steel_1")
    box(body, 44, 22, 62, 46, "ink")
    box(body, 45, 23, 61, 45, "steel_2")
    box(body, 46, 25, 60, 43, "teal_0")
    box(lit, 45, 23, 61, 23, "steel_4")
    box(lit, 45, 24, 45, 45, "steel_3")
    box(lit, 46, 44, 60, 44, "steel_1")
    for i, y in enumerate(range(27, 42, 2)):
        if i in (3, 4):
            box(detail, 48, y, 51, y, "amber")
            put(detail, 53, y, "amber")
            continue
        box(detail, 48, y, 57 - (i % 3), y, "teal_3" if i % 2 else "teal_4")
    put(detail, 59, 26, "glow")
    put(detail, 59, 42, "red")
    return [shadow, body, lit, detail]


def fixture_code_47():
    """编号四七 / Code Forty-Seven: an old bronze junction box stamped 47 on a stone plinth beside a
    modern relay node whose display also reads 47; the node's cable lies unplugged by the old socket."""
    shadow = f_shadow((1, 49, 62, 61))
    body = f_layer()
    # stone plinth
    box(body, 3, 43, 32, 57, "ink")
    box(body, 4, 44, 31, 46, "stone_5")
    box(body, 4, 47, 31, 55, "stone_3")
    box(body, 4, 56, 31, 56, "stone_1")
    # bronze box
    box(body, 6, 14, 29, 43, "ink")
    box(body, 7, 15, 28, 17, "brass_3")
    box(body, 7, 18, 28, 42, "brass_2")
    lit = f_layer()
    box(lit, 4, 44, 31, 44, "stone_6")
    box(lit, 4, 46, 31, 46, "stone_4")
    for x in (12, 22):
        box(lit, x, 47, x, 55, "stone_2")
    box(lit, 4, 51, 11, 51, "stone_2")
    box(lit, 23, 51, 31, 51, "stone_2")
    box(lit, 7, 15, 28, 15, "brass_4")
    box(lit, 7, 17, 28, 17, "brass_1")
    box(lit, 7, 18, 7, 42, "brass_3")
    box(lit, 28, 18, 28, 42, "brass_1")
    box(lit, 8, 42, 27, 42, "brass_1")
    detail = f_layer()
    # stamped cream plate reading 47
    box(detail, 10, 21, 25, 30, "brass_1")
    box(detail, 11, 22, 24, 29, "paper_2")
    box(detail, 11, 29, 24, 29, "paper_1")
    digit(detail, 13, 23, "4", "ink")
    digit(detail, 19, 23, "7", "ink")
    # rivets and verdigris streaks
    for x, y in [(9, 19), (26, 19), (9, 40), (26, 40)]:
        put(detail, x, y, "brass_4")
        put(detail, x, y + 1, "verd_0")
    for x, y0, y1 in [(9, 21, 25), (26, 21, 27), (14, 31, 35), (21, 31, 34)]:
        box(detail, x, y0, x, y1, "verd_1" if x % 2 else "verd_0")
    # empty socket: the plug that should be here lies on the floor
    box(detail, 15, 34, 20, 39, "steel_1")
    box(detail, 16, 35, 19, 38, "ink")
    put(detail, 17, 36, "brass_1")
    put(detail, 18, 36, "brass_1")
    # relay node on a short tripod
    for lx in (40, 48, 57):
        seg(body, [(48, 44), (lx, 58)], "steel_1")
    seg(lit, [(48, 45), (41, 57)], "steel_3")
    box(body, 37, 14, 59, 44, "ink")
    box(body, 38, 15, 58, 43, "steel_2")
    box(body, 40, 18, 56, 31, "teal_0")
    box(body, 47, 5, 48, 13, "steel_1")
    box(lit, 38, 15, 58, 15, "steel_4")
    box(lit, 38, 16, 38, 43, "steel_3")
    box(lit, 58, 16, 58, 43, "steel_1")
    box(lit, 39, 43, 57, 43, "steel_1")
    box(lit, 40, 32, 56, 32, "steel_3")
    put(lit, 47, 5, "steel_3")
    digit(detail, 43, 21, "4", "glow")
    digit(detail, 49, 21, "7", "glow")
    box(detail, 41, 28, 55, 28, "teal_2")
    for x in range(41, 56, 3):
        put(detail, x, 30, "teal_1")
    put(detail, 42, 36, "teal_4")
    put(detail, 45, 36, "teal_3")
    put(detail, 54, 36, "red")
    box(detail, 41, 39, 55, 40, "steel_1")
    put(detail, 47, 4, "teal_4")
    # its cable, ending in a loose plug on the floor beside the old box
    seg(body, [(44, 44), (41, 50), (36, 55), (31, 58), (26, 59)], "teal_1", 2)
    seg(lit, [(44, 44), (41, 49), (36, 54), (31, 57)], "teal_2")
    box(body, 21, 57, 26, 61, "ink")
    box(body, 22, 58, 26, 60, "brass_2")
    box(lit, 22, 58, 26, 58, "brass_3")
    put(detail, 21, 58, "brass_4")
    put(detail, 21, 60, "brass_4")
    return [shadow, body, lit, detail]


FIXTURES = [
    ("layered-wall", fixture_layered_wall, 0,
     "分层墙面 / Layered Wall: cut wall specimen on a pallet, dressed sandstone with a walkway moulding over a dark sealing course and older brick, the same teal age tag on both layers, a survey camera photographing the original face"),
    ("broken-index", fixture_broken_index, 1,
     "残缺索引 / Broken Index: oak card catalogue with brass card holders, one drawer slot empty and one drawer pulled out with gaps in its cards, cards on the floor, a survey reader listing identifiers with an amber missing run"),
    ("code-47", fixture_code_47, 2,
     "编号四七 / Code Forty-Seven: old bronze junction box with verdigris and a stamped 47 plate on a stone plinth, next to a modern relay node whose display also reads 47; the node's cable and plug lie unplugged below the old box's empty socket"),
]
# Feet footprints (fixture-local rows/cols) used for the runtime blockers; see the manifest.
FIXTURE_FOOTPRINT_ROWS = {"layered-wall": (47, 58), "broken-index": (48, 58), "code-47": (45, 60)}


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


DT = (2026, 10, 17, 16, 2, 0)


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
    palette = [{"name": "wdc-annex-room1-v02", "colors": [{"color": c, "index": i} for i, c in enumerate(palette_hex)]}]
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


def write_asset(stem, export_name, names, layers, runtime_dir, palette_hex, runtime_image=None):
    flat = merged(layers)
    files = {"png": png_bytes(flat), "ora": ora_bytes(stem, names, layers, flat),
             "pxo": pxo_bytes(export_name, names, layers, flat, palette_hex)}
    for ext, data in files.items():
        (OUT / f"{stem}.{ext}").write_bytes(data)
    item = {
        "size": list(flat.size), "layers_bottom_to_top": names,
        "files": {ext: {"file": rel(OUT / f"{stem}.{ext}"), "sha256": sha(d), "hash_algorithm": "sha256-bytes"} for ext, d in files.items()},
    }
    if runtime_dir is not None:
        data = files["png"] if runtime_image is None else png_bytes(runtime_image)
        runtime = runtime_dir / f"{stem}.png"
        runtime.write_bytes(data)
        item["runtime_png"] = {"file": rel(runtime), "sha256": sha(data), "hash_algorithm": "sha256-bytes"}
    return item


def fixture_palette():
    return sorted(HP.values())


def build(preview=None):
    if preview:
        Path(preview).mkdir(parents=True, exist_ok=True)
        build_scene(preview)
        for slug, author, _, _ in FIXTURES:
            img = merged([Image.fromarray(l) for l in author()])
            img.save(Path(preview) / f"fx-{slug}.png")
            img.resize((256, 256), Image.Resampling.NEAREST).save(Path(preview) / f"fx-{slug}-4x.png")
        return None
    OUT.mkdir(parents=True, exist_ok=True)
    RUNTIME_SCENE_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_PROP_DIR.mkdir(parents=True, exist_ok=True)
    layers, names, stats, palette_hex, fg_layer, under = build_scene()
    scene = write_asset(f"{PREFIX}_capitol-interior-scene_unapproved-v02_{STAMP}", "wdc-annex-room1-v02-scene",
                        names, layers, RUNTIME_SCENE_DIR, palette_hex)
    scene["purpose"] = "room background, drawn at Rect2(0, 0, 640, 360) for scifi.ruins room 1"
    scene["provenance"] = stats
    fg_img = Image.fromarray(fg_layer)
    foreground = write_asset(f"{PREFIX}_foreground-occluder_unapproved-v02_{STAMP}", "wdc-annex-room1-v02-foreground",
                             ["foreground-stubs-occluder"], [fg_img], RUNTIME_SCENE_DIR, palette_hex)
    foreground["purpose"] = ("binary-alpha copy of the scene's top layer; the room draws it at Rect2(0, 0, 640, 360) "
                             "above the heroine so the corner stubs and ivy pass in front of her")
    fixtures = []
    for slug, author, clue_index, meaning in FIXTURES:
        flayers = [Image.fromarray(l) for l in author()]
        item = write_asset(f"{PREFIX}_{slug}-pixel-fixture_unapproved-v02_{STAMP}", f"wdc-annex-room1-v02-{slug}",
                           FIXTURE_LAYERS, flayers, RUNTIME_PROP_DIR, fixture_palette())
        r0, r1 = FIXTURE_FOOTPRINT_ROWS[slug]
        item.update({"purpose": slug, "clue": f"scifi.ruins:{clue_index}", "reads_as": meaning,
                     "screen_rect_640x360": f"CLUE_POSITIONS[{clue_index}] + (-32, 2), 64x64",
                     "footprint_rows_fixture_local": [r0, r1],
                     "footprint_rows_screen": [CLUES[clue_index][1] + FIXTURE_OFFSET[1] + r0,
                                               CLUES[clue_index][1] + FIXTURE_OFFSET[1] + r1]})
        fixtures.append(item)
    ref_bytes = REFERENCE.read_bytes()
    manifest = {
        "project": "rpg-2-star-ocean-the-second",
        "scene": "Washington, D.C. ruins survey annex room 1 (遗址外环 / Ruin Outer Ring), destination scifi.ruins",
        "variant": "v02 quality pass; v01 (outputs/wdc-sr1-v01_65b9618f, 65b9618f) is kept unchanged as the baseline",
        "status": "UNAPPROVED candidate; creator has not reviewed; counters unchanged (scenes 3/12, sprites 0/52, timed playtests 0/2, weighted 40.8%)",
        "authorship": {
            "scene": ("Imported underpainting, then hand corrections. The background layers marked '-underpaint' are a "
                      "box-filtered, graded, palette-reduced (median cut + k-means, no dither) and cluster-cleaned "
                      "conversion of the Codex-generated nonruntime art-direction reference below; they are NOT hand "
                      "painted. Layers marked 'hand-' are drawn pixel by pixel in this tool by Claude. The foreground "
                      "layer is the underpainting plus hand pixels inside the corner-stub silhouettes."),
            "fixtures": "Hand-drawn pixel by pixel in this tool by Claude; no underpainting, generation, resampling or filtering.",
            "tool_author": "Claude (Claude Code, signed-in Claude Max, firstParty)",
        },
        "underpainting_source": {
            "file": rel(REFERENCE), "sha256": sha(ref_bytes), "hash_algorithm": "sha256-bytes",
            "origin": "Codex built-in image generation (edit of the old m8-concept room-1 plate); see the "
                      "matching -prompt_ .md beside it. Nonruntime, unapproved art-direction reference.",
            "recomposition": {"wall_band": {"ref_rows": list(WALL_REF_ROWS), "screen_rows": list(WALL_Y)},
                              "floor_band": {"ref_rows": list(FLOOR_REF_ROWS), "screen_rows": list(FLOOR_Y)},
                              "x_scale": "640/1672", "filter": "box"},
            "grade": "floor x(0.80 - 0.12 depth - 0.12 side^2), sun-shaft highlight compression, cool shadows / warm lights, "
                     "floor saturation x0.88, bench band y 110-157 feathered down to x0.74, exterior kept at x0.96; "
                     "floor UnsharpMask(3, 45, 2) for grout contrast, then UnsharpMask(1.0, 55, 3) everywhere",
            "palette_reduction": f"PIL median cut + 8 k-means iterations to {UNDERPAINT_COLOURS} colours, no dither; "
                                 "isolated pixels folded into the nearest-coloured 4-neighbour cluster when the RGB step < 34 (2 passes)",
        },
        "scene_palette_hex": palette_hex,
        "fixture_palette": HP, "fixture_contact_shadow_rgba": list(SHADOW_RGBA),
        "pixelorama": f"pxo_version 7, color_mode 5, 1 frame; scene {len(names)} layers, fixtures {len(FIXTURE_LAYERS)} layers, foreground 1 layer; ORA lists the same layers",
        "scene_asset": scene, "foreground_asset": foreground, "fixtures": fixtures, "source": rel(Path(__file__)),
    }
    path = OUT / f"{PREFIX}_scene-and-fixtures-manifest_unapproved-v02_{STAMP}.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(rel(path))
    print(json.dumps(stats, indent=1))
    return manifest


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":
        build(sys.argv[2])
    else:
        build()
