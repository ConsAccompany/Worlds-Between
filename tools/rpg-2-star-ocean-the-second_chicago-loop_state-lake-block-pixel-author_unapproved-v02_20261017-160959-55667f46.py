"""Chicago Loop arrival block, State St x Lake St, native 640x360 scene (UNAPPROVED candidate v02).

v02 is one visual-density pass over v01 (v01 files stay untouched as the audit baseline). The base
is a quantized underpainting of the nonruntime art-direction reference
outputs/...elevated-rail-walkable-block-art-direction-nonruntime-v02_20261016-195030-8c456a73.png:
  1. area-average (box) downscale of the whole reference to 640x360, no other resampling;
  2. row recomposition for gameplay: the facade rows above the L move under the header edge, the
     open-tie deck is shortened from 51 to 40 rows (deck bottom row 134, so a 44 px hero at the walk
     top 178 stays clear of the girder), and everything below the deck shifts up by 30 rows;
  3. repairs of visible generator defects (white splotches on the far road, a noisy block where the
     crosswalk meets the plaza) by copying clean neighbouring texture;
  4. gameplay moves: the info kiosk is lifted 32 rows and shortened 17 rows (it now stands under the
     deck edge on the legacy smoke-test pin instead of v01's mid-lane car);
  5. light unsharp mask, then one 128-colour median-cut palette with k-means refinement, no dither;
  6. two passes that fold isolated low-contrast pixels into their neighbours, so remaining single
     pixels are deliberate (rivets, highlights, flowers);
  7. hand-placed native pixel art on top: a bench, the State/Lake station plate with the five Loop
     line colours, a Chicago-flag banner on the curb lamp.
The image is then split into editable layers: static ground / facade / deck / station plate, and
y-sort occluders cut with explicit rectangles, brace polygons and colour keys. Ground under each
occluder is filled from a nearby clean offset so the editable ground is complete. Runtime gets the
flattened static layers as one opaque PNG plus the y-sort PNGs (binary alpha).
Geometry constants must match the v02 runtime scene script (checked in Godot and by the source check).
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
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261017-160959-55667f46"
PREFIX = "rpg-2-star-ocean-the-second_chicago-loop_state-lake"
VARIANT = "unapproved-v02"
OUT = ROOT / "outputs" / "chicago-loop-state-lake-v02"
RUNTIME = ROOT / "game" / "assets" / "environments" / "chicago-loop-state-lake-v02"
REFERENCE = ROOT / "outputs" / "rpg-2-star-ocean-the-second_chicago-loop_elevated-rail-walkable-block-art-direction-nonruntime-v02_20261016-195030-8c456a73.png"
REFERENCE_SHA256 = "73b57deb1532fcd6be419b96ec7b33aea894458f39a7f3d42c8842f778761be4"
W, H = 640, 360
PIXELORAMA_VERSION = "v1.2.3-stable"
PALETTE_SIZE = 128

# --- Geometry shared with the runtime scene script (x, y, w, h; right/bottom edge exclusive). ---
WALK = (8, 178, 624, 120)
BENCH = (392, 188, 26, 12)
KIOSK_BOX = (419, 189, 26, 12)
KIOSK = (432, 214)            # interaction point, just south of the kiosk
BLOCKS = [
    BENCH, KIOSK_BOX,
    (79, 178, 14, 5),          # curb lamp base
    (143, 246, 38, 17), (460, 246, 38, 18),   # L column plinths
    (180, 250, 15, 8), (453, 250, 8, 8),      # iron racks
    (120, 250, 23, 13), (497, 250, 22, 14),   # planters
    (518, 178, 122, 20),       # raised terrace, steps and terrace planter
    (520, 288, 26, 10),        # forecourt lamp pedestal
    (574, 218, 66, 80),        # cypress, fountain court and railing
    (86, 276, 44, 22),         # foreground tree
]
DECK_TOP, DECK_BOTTOM = 95, 134   # deck rows 95..134; the walk top leaves a 44 px figure below it
WALK_TOP = WALK[1]

# Source layers bottom to top: name, role, y-sort pivot row (None = static, flattened into ground-far).
LAYERS = [
    ("ground-plaza-street", None),
    ("facade-north", None),
    ("deck-l-girder", None),
    ("station-plate", None),
    ("ysort-curb-lamp", 180.5),
    ("ysort-kiosk-bench", 195.5),
    ("ysort-l-columns", 254.5),
    ("ysort-planters", 256.5),
    ("ysort-forecourt", 300.5),
    ("ysort-foreground-tree", 330.5),
]
STATIC = [n for n, p in LAYERS if p is None]
YSORT = [(n, p) for n, p in LAYERS if p is not None]
RUNTIME_LAYERS = [("ground-far", None)] + YSORT
GUIDE = "guides-walkmask"

# Hand-placed colours (everything else comes from the 128-colour underpainting palette).
HAND = {
    "iron": (31, 40, 42), "iron_hi": (58, 70, 72), "wood_dk": (106, 67, 39), "wood": (141, 93, 54),
    "wood_hi": (168, 119, 69), "wood_edge": (192, 138, 82), "bench_shadow": (74, 70, 67),
    "plate_edge": (14, 18, 20), "plate": (28, 35, 40), "plate_hi": (58, 69, 76),
    "loop_brown": (98, 54, 27), "loop_green": (0, 155, 58), "loop_orange": (249, 70, 28),
    "loop_pink": (226, 126, 166), "loop_purple": (82, 35, 152),
    "flag_white": (233, 238, 240), "flag_blue": (143, 208, 240), "flag_red": (216, 30, 44),
}


# ---------------------------------------------------------------- underpainting
def reference_box():
    data = REFERENCE.read_bytes()
    if hashlib.sha256(data).hexdigest() != REFERENCE_SHA256:
        raise SystemExit("reference image hash changed: " + str(REFERENCE))
    return np.array(Image.open(io.BytesIO(data)).convert("RGB").resize((W, H), Image.BOX))


def row_map():
    """Native row -> reference-box row."""
    deck = list(range(54, 65)) + list(range(74, 85)) + list(range(87, 105))
    rows = [max(0, y - 41) for y in range(DECK_TOP)] + deck + [y - 30 for y in range(DECK_BOTTOM + 1, H)]
    assert len(rows) == H and len(deck) == DECK_BOTTOM - DECK_TOP + 1
    return rows


def copy_patch(a, box, dx, dy):
    x0, y0, x1, y1 = box
    a[y0:y1, x0:x1] = a[y0 + dy:y1 + dy, x0 + dx:x1 + dx].copy()


KIOSK_SRC = (430, 170, 456, 253)      # kiosk in the recomposed underpainting (x0, y0, x1, y1)
KIOSK_CUT_ROWS = range(199, 216)       # screen rows removed to fit under the deck edge
KIOSK_DST = (KIOSK_BOX[0], DECK_BOTTOM + 1)
REPAIRS = [  # (box, dx, dy): visible generator defects replaced by clean neighbouring texture
    ((0, 62, 58, 95), 0, 78),          # white splotches on the far State St roadway
    ((92, 186, 122, 264), 110, 0),     # noisy block where the crosswalk meets the plaza
]


def underpainting():
    r = reference_box()
    u = r[row_map()].copy()
    u[:41] = (13, 23, 35)                            # under the opaque header: no reference above row 0
    for box, dx, dy in REPAIRS:
        copy_patch(u, box, dx, dy)
    x0, y0, x1, y1 = KIOSK_SRC
    keep = [y for y in range(y0, y1) if y not in KIOSK_CUT_ROWS]
    kiosk = u[keep, x0:x1].copy()
    copy_patch(u, KIOSK_SRC, -32, 0)                 # plaza and deck shadow where the kiosk stood
    kx, ky = KIOSK_DST
    kiosk_rows = (ky, ky + kiosk.shape[0])
    u[ky:ky + kiosk.shape[0], kx:kx + kiosk.shape[1]] = kiosk
    img = Image.fromarray(u).filter(ImageFilter.UnsharpMask(radius=1, percent=60, threshold=2))
    q = img.quantize(colors=PALETTE_SIZE, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE, kmeans=4)
    pal = np.array(q.getpalette()[:PALETTE_SIZE * 3], np.uint8).reshape(-1, 3)
    idx = clean_isolated(np.array(q), pal)
    return pal[idx], kiosk_rows


def clean_isolated(idx, pal, passes=2, max_luma=28):
    luma = pal.astype(int) @ np.array([299, 587, 114]) // 1000
    for _ in range(passes):
        p = np.pad(idx, 1, mode="edge")
        n = np.stack([p[1:-1, :-2], p[1:-1, 2:], p[:-2, 1:-1], p[2:, 1:-1]])
        isolated = (n != idx).all(axis=0)
        best = n[0].copy()
        votes = np.zeros(idx.shape, int)
        for i in range(4):
            c = sum((n[j] == n[i]).astype(int) for j in range(4))
            m = c > votes
            best[m] = n[i][m]
            votes[m] = c[m]
        soft = np.abs(luma[idx] - luma[best]) < max_luma
        idx = np.where(isolated & soft, best, idx)
    return idx


# ---------------------------------------------------------------- masks
def rect_mask(x0, y0, x1, y1):
    m = np.zeros((H, W), bool)
    m[y0:y1, x0:x1] = True
    return m


def poly_mask(points):
    img = Image.new("L", (W, H), 0)
    ImageDraw.Draw(img).polygon(points, fill=255)
    return np.array(img) > 0


def luma(a):
    return (a[..., 0].astype(int) * 299 + a[..., 1].astype(int) * 587 + a[..., 2].astype(int) * 114) // 1000


def key_object(a):
    """Dark iron, foliage or lamp glow: pixels that are clearly not plaza paving."""
    r, g, b = (a[..., i].astype(int) for i in range(3))
    return (luma(a) < 78) | ((g > r + 6) & (g > b + 6)) | ((r > 200) & (r - b > 50)) | ((b > r + 30) & (g > r + 20))


def scan_fill(m, box):
    """Fill each row of the box between its first and last key pixel (solid silhouettes)."""
    x0, y0, x1, y1 = box
    out = np.zeros_like(m)
    for y in range(y0, y1):
        xs = np.nonzero(m[y, x0:x1])[0]
        if len(xs):
            out[y, x0 + xs[0]:x0 + xs[-1] + 1] = True
    return out


def key_foliage(a):
    r, g, b = (a[..., i].astype(int) for i in range(3))
    return (g > r + 6) & (g > b + 6)


def despeckle(m):
    """Drop key pixels with fewer than two 4-neighbours (stray background darks along edges)."""
    p = np.pad(m, 1)
    n = p[1:-1, :-2].astype(int) + p[1:-1, 2:] + p[:-2, 1:-1] + p[2:, 1:-1]
    return m & (n >= 2)


def keyed(a, box, fill=True, key=key_object):
    m = despeckle(key(a) & rect_mask(*box))
    return scan_fill(m, box) if fill else m


def light_stone(a):
    """Pale, low-saturation paving or parapet stone caught inside a row-filled foliage silhouette."""
    return (luma(a) > 105) & (a.max(axis=-1).astype(int) - a.min(axis=-1) < 40)


def brace(a, points):
    return despeckle(poly_mask(points) & (luma(a) < 100))


def object_masks(a, kiosk_rows):
    m = {}
    cols = np.zeros((H, W), bool)
    for dx in (0, 317):   # left column at x 151..172, right column at x 468..489
        cols |= rect_mask(151 + dx, DECK_BOTTOM + 1, 173 + dx, 210)
        cols |= brace(a, [(121 + dx, 130), (136 + dx, 130), (153 + dx, 149), (153 + dx, 160), (146 + dx, 160)])
        cols |= brace(a, [(202 + dx, 130), (187 + dx, 130), (170 + dx, 149), (170 + dx, 160), (177 + dx, 160)])
    cols |= rect_mask(143, 208, 181, 263) | rect_mask(460, 208, 498, 264)
    cols |= keyed(a, (180, 224, 195, 259), fill=False) | keyed(a, (453, 224, 461, 259), fill=False)
    cols[:DECK_BOTTOM + 1] = False
    m["ysort-l-columns"] = cols
    kx, ky = KIOSK_DST
    kw = KIOSK_SRC[2] - KIOSK_SRC[0]
    base_top = kiosk_rows[1] - 15
    m["ysort-kiosk-bench"] = keyed(a, (kx, ky, kx + kw, base_top)) | rect_mask(kx, base_top, kx + kw, kiosk_rows[1])
    m["ysort-curb-lamp"] = scan_fill(despeckle(key_object(a) & rect_mask(78, DECK_BOTTOM + 1, 94, 187)), (78, DECK_BOTTOM + 1, 94, 187))
    m["ysort-planters"] = (keyed(a, (120, 224, 144, 250), key=key_foliage) | rect_mask(120, 249, 143, 263)
                           | keyed(a, (497, 224, 520, 250), key=key_foliage) | rect_mask(497, 249, 519, 264))
    m["ysort-forecourt"] = (keyed(a, (522, 254, 548, 283)) | rect_mask(520, 282, 546, H)
                            | (keyed(a, (574, 222, 598, 301), key=key_foliage) & ~light_stone(a)) | rect_mask(575, 300, 600, H))
    m["ysort-foreground-tree"] = keyed(a, (78, 262, 140, H), key=key_foliage) & ~light_stone(a)
    return m


# Ground fill under each occluder (editable source only; the runtime always draws the occluder).
FILL_OFFSETS = {"ysort-l-columns": [((100, 135, 240, H), 75), ((420, 135, 540, H), -75)],
                "ysort-kiosk-bench": [((380, 135, 470, 215), -60)],
                "ysort-curb-lamp": [((70, 135, 100, 190), 20)],
                "ysort-planters": [((100, 200, 160, 270), 90), ((480, 200, 530, 270), -87)],
                "ysort-forecourt": [((515, 250, 560, H), 28), ((560, 210, 610, H), -32)],
                "ysort-foreground-tree": [((70, 255, 150, H), 70)]}


def fill_under(base, masks):
    out = base.copy()
    for name, regions in FILL_OFFSETS.items():
        for (x0, y0, x1, y1), dx in regions:
            sel = masks[name] & rect_mask(x0, y0, x1, y1)
            ys, xs = np.nonzero(sel)
            out[ys, xs] = base[ys, np.clip(xs + dx, 0, W - 1)]
    return out


# ---------------------------------------------------------------- hand-placed pixel art
def put(layer, x, y, colour):
    layer[y, x, :3] = HAND[colour]
    layer[y, x, 3] = 255


def hline(layer, x0, x1, y, colour):
    for x in range(x0, x1):
        put(layer, x, y, colour)


def draw_bench(layer):
    """Cast-iron and slat park bench seen from the south-above: backrest, dark gap, seat, legs, shadow."""
    x0, y0 = BENCH[0] - 1, BENCH[1] - 5          # 28 x 17 sprite, seat over the footprint
    w = BENCH[2] + 2
    for dy in range(14, 17):                     # cast shadow on the paving, offset east
        hline(layer, x0 + 2 + (dy - 14), x0 + w + 1, y0 + dy, "bench_shadow")
    hline(layer, x0 + 1, x0 + w - 1, y0, "wood_hi")         # backrest slats
    hline(layer, x0 + 1, x0 + w - 1, y0 + 1, "wood")
    hline(layer, x0 + 1, x0 + w - 1, y0 + 2, "wood_dk")
    hline(layer, x0 + 1, x0 + w - 1, y0 + 3, "iron")        # gap under the backrest
    for dy, c in ((4, "wood_hi"), (5, "wood"), (6, "wood_hi"), (7, "wood"), (8, "wood_dk")):
        hline(layer, x0 + 1, x0 + w - 1, y0 + dy, c)        # seat slats
    hline(layer, x0 + 1, x0 + w - 1, y0 + 9, "wood_edge")   # front edge catches the light
    hline(layer, x0 + 2, x0 + w - 2, y0 + 10, "iron")       # apron
    for x in (x0, x0 + w // 2, x0 + w - 1):                 # cast-iron standards
        for dy in range(0, 11):
            put(layer, x, y0 + dy, "iron_hi" if dy in (0, 4) else "iron")
    for x in (x0 + 1, x0 + 2, x0 + w - 3, x0 + w - 2):      # legs
        for dy in range(11, 14):
            put(layer, x, y0 + dy, "iron")
    for x in (x0 + 1, x0 + w - 3):
        put(layer, x, y0 + 11, "iron_hi")


PLATE = (318, 120, 382, 132)   # State/Lake station plate on the girder fascia; text is a runtime label


def draw_plate(layer):
    x0, y0, x1, y1 = PLATE
    for y in range(y0, y1):
        for x in range(x0, x1):
            edge = y in (y0, y1 - 1) or x in (x0, x1 - 1)
            put(layer, x, y, "plate_edge" if edge else ("plate_hi" if y == y0 + 1 else "plate"))
    for i, c in enumerate(("loop_brown", "loop_green", "loop_orange", "loop_pink", "loop_purple")):
        for y in (y0 + 1 + 2 * i, y0 + 2 + 2 * i):
            if y < y1 - 1:
                for x in (x0 + 2, x0 + 3, x0 + 4):
                    put(layer, x, y, c)
    for x in (x0 + 8, x1 - 9):                   # hanger bolts
        put(layer, x, y0 - 1, "plate_edge")


def draw_banner(layer):
    hline(layer, 89, 98, 140, "iron")
    for y in range(141, 153):
        c = "flag_blue" if y in (143, 144, 149, 150) else "flag_white"
        hline(layer, 92, 98, y, c)
    for x in (93, 96):
        put(layer, x, 146, "flag_red")
        put(layer, x, 147, "flag_red")
    put(layer, 92, 153, "flag_white")
    put(layer, 97, 153, "flag_white")


# ---------------------------------------------------------------- layers
def rgba_layer(src, mask):
    out = np.zeros((H, W, 4), np.uint8)
    out[mask, :3] = src[mask]
    out[mask, 3] = 255
    return out


def build_layers():
    a, kiosk_rows = underpainting()
    masks = object_masks(a, kiosk_rows)
    ground = fill_under(a, masks)
    rows = np.arange(H)[:, None] * np.ones((1, W), int)
    facade = (rows < DECK_TOP) | ((rows > DECK_BOTTOM) & (rows < 152) & (np.arange(W)[None, :] >= 100))
    deck = (rows >= DECK_TOP) & (rows <= DECK_BOTTOM)
    layers = {
        "ground-plaza-street": rgba_layer(ground, ~facade & ~deck),
        "facade-north": rgba_layer(ground, facade),
        "deck-l-girder": rgba_layer(ground, deck),
        "station-plate": np.zeros((H, W, 4), np.uint8),
    }
    draw_plate(layers["station-plate"])
    for name, _ in YSORT:
        layers[name] = rgba_layer(a, masks[name])
    draw_banner(layers["ysort-curb-lamp"])
    draw_bench(layers["ysort-kiosk-bench"])
    return {k: Image.fromarray(v, "RGBA") for k, v in layers.items()}


def runtime_layers(layers):
    ground = Image.new("RGBA", (W, H))
    for name in STATIC:
        ground.alpha_composite(layers[name])
    out = {"ground-far": ground}
    for name, _ in YSORT:
        out[name] = layers[name]
    return out


# ---------------------------------------------------------------- guides, files
def walkable(x, y):
    def inside(r):
        return r[0] <= x < r[0] + r[2] and r[1] <= y < r[1] + r[3]
    return inside(WALK) and not any(inside(b) for b in BLOCKS)


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


def merged(layers):
    out = Image.new("RGBA", (W, H))
    for name, _ in LAYERS:
        out.alpha_composite(layers[name])
    return out


ZIP_TIME = (2026, 10, 17, 16, 9, 58)


def ora_bytes(layers, guide, flat):
    root = ET.Element("image", {"w": str(W), "h": str(H), "name": PREFIX, "version": "0.0.3"})
    stack = ET.SubElement(root, "stack")
    buf = io.BytesIO()
    entries = [(name, layers[name], "visible") for name, _ in LAYERS] + [(GUIDE, guide, "hidden")]
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
    entries = [(name, layers[name], True, False) for name, _ in LAYERS] + [(GUIDE, guide, False, True)]
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": locked, "metadata": {}, "name": name,
                   "new_cels_linked": False, "opacity": 1.0, "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": visible} for name, _, visible, locked in entries]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0} for _ in entries],
                    "duration": 1.0, "metadata": {}}]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": json.dumps("chicago-loop-state-lake-v02"),
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


def rel(path):
    path = Path(path).resolve()
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path).replace("\\", "/")


def palette_colours(layers):
    return sorted({tuple(p) for img in layers.values() for p in np.array(img)[np.array(img)[..., 3] == 255][:, :3].tolist()})


def build(out=OUT, runtime=RUNTIME):
    out.mkdir(parents=True, exist_ok=True)
    runtime.mkdir(parents=True, exist_ok=True)
    layers = build_layers()
    guide = walkmask()
    flat = merged(layers)
    rt = runtime_layers(layers)
    files = {}
    for name, pivot in RUNTIME_LAYERS:
        data = png_bytes(rt[name])
        path = runtime / f"{PREFIX}_{name}_{VARIANT}_{STAMP}.png"
        path.write_bytes(data)
        files[name] = {"file": rel(path), "sha256": sha(data), "hash_algorithm": "sha256-bytes", "ysort_pivot_row": pivot}
    colours = palette_colours(layers)
    pal_text = "GIMP Palette\nName: chicago-loop-state-lake-v02\nColumns: 16\n#\n" + "".join(f"{r:3d} {g:3d} {b:3d}\tc{i:03d}\n" for i, (r, g, b) in enumerate(colours))
    extra = {
        "merged-preview": (f"{PREFIX}_merged-preview_{VARIANT}_{STAMP}.png", png_bytes(flat)),
        "walkmask-guide": (f"{PREFIX}_{GUIDE}_{VARIANT}_{STAMP}.png", png_bytes(guide)),
        "openraster": (f"{PREFIX}_layered-source_{VARIANT}_{STAMP}.ora", ora_bytes(layers, guide, flat)),
        "pixelorama": (f"{PREFIX}_layered-source_{VARIANT}_{STAMP}.pxo", pxo_bytes(layers, guide, flat)),
        "palette-gpl": (f"{PREFIX}_palette_{VARIANT}_{STAMP}.gpl", pal_text.encode("utf-8")),
    }
    for key, (name, data) in extra.items():
        (out / name).write_bytes(data)
        files[key] = {"file": rel(out / name), "sha256": sha(data),
                      "hash_algorithm": "sha256-bytes" if not name.endswith(".gpl") else "sha256-bytes (LF, written by this tool)"}
    manifest = {
        "project": "Worlds Between",
        "scene": "Chicago Loop arrival block: State St x Lake St under the Lake Street elevated (State/Lake)",
        "status": "UNAPPROVED candidate v02 for Codex visual review; creator has not reviewed; counters unchanged (3/12 scenes, 0/52 sprites, 0/2 playtests, 40.8%)",
        "canon": "The exact intersection, the pedestrianised Lake St plaza and the terrace are art-pilot choices, not creator-approved landmarks.",
        "authorship": ("Quantized underpainting of the nonruntime art-direction reference (box downscale, row recomposition, "
                       "defect repair, kiosk move, unsharp, 128-colour median cut + k-means, isolated-pixel cleanup), "
                       "split into editable layers, plus hand-placed bench, station plate and flag banner; "
                       "built by Claude (Claude Code, signed-in Claude Max, firstParty)."),
        "reference": {"file": rel(REFERENCE), "sha256": REFERENCE_SHA256, "git": "untracked at build time"},
        "toolchain": {"pillow": PIL.__version__, "numpy": np.__version__,
                      "note": "median-cut/k-means output can change with Pillow versions; the hash lock is for this toolchain"},
        "row_recomposition": {"facade_rows": [62, DECK_TOP - 1], "deck_rows": [DECK_TOP, DECK_BOTTOM],
                              "reference_box_rows_for_deck": "54-64, 74-84, 87-104", "below_deck_shift": -30},
        "repairs": [{"box": list(b), "copied_from_offset": [dx, dy]} for b, dx, dy in REPAIRS],
        "kiosk_move": {"source_box": list(KIOSK_SRC), "rows_removed": [KIOSK_CUT_ROWS.start, KIOSK_CUT_ROWS.stop - 1], "placed_at": list(KIOSK_DST)},
        "canvas": [W, H], "visible_art_rows": [62, 317], "palette_colours": len(colours),
        "layers_bottom_to_top": [{"name": n, "ysort_pivot_row": p} for n, p in LAYERS] + [{"name": GUIDE, "hidden": True, "locked": True}],
        "runtime_layers": [{"name": n, "ysort_pivot_row": p, "from": STATIC if p is None else [n]} for n, p in RUNTIME_LAYERS],
        "geometry": {"walk": WALK, "blocks": BLOCKS, "bench": BENCH, "kiosk_box": KIOSK_BOX, "kiosk": KIOSK,
                     "deck_rows": [DECK_TOP, DECK_BOTTOM], "station_plate": PLATE},
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
        merged(build_layers()).save(sys.argv[2])
    else:
        build()
