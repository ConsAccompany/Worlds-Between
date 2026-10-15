"""Female protagonist - SOUTH walk pilot w01 - source-locked build and checker (M8).

Builds an isolated 8-frame south-facing walk loop for the female protagonist from the
user-approved STATIC selout v8 idle (approved as a 48-logical-px static visual baseline only).

Method (no generative redraw, no resampling, no filtering, no flips/mirrors):
  1. v8 is split into five layers by explicit texel ownership rules (torso, right forearm,
     left fist, viewer-left leg "vl" with the knee guard, viewer-right leg "vr").  A gate
     checks that re-stacking the untouched layers reproduces v8 texel-for-texel.
  2. A few HIDDEN fill texels are authored under the forearm/fist/hand.  They are covered in the
     idle stack (the gate above proves it) and only show when a limb swings away.
  3. Each walk frame re-stacks the layers with integer, hand-chosen placements:
       - torso (head, face, hair, coat, scarf, teal flask, belt ...) moves only by the body bob;
       - each leg keeps its thigh on the hip (moves with the bob) while the knee/shin/boot are
         ground-relative: the knee lifts over the thigh (foreshortening), thigh/shin rows are
         repeated or overlapped by whole rows, and the swing knee tucks 1 texel inward;
       - boots use hand-authored texel variants (forward, flat, heel-up, lifted) written below
         as palette-letter text, all in v8 colours;
       - forearm and fist swing in opposition to the legs; the cape tip lags as cloth.
  4. Frames are written as separate 80x112 PNGs, plus a manifest and an editable Pixelorama
     1.2.3 .pxo (pxo_version 7: one frame per walk phase, five layers).

Every texel colour comes from the v8 palette.  Nothing here edits v8, its manifest, the Game
Bible, progress files, the readiness checklist, the battle arena or any runtime file.

Usage (repository root, Codex-runtime Python 3.12 + Pillow + NumPy):
  python -I tools/<this file> --out-dir <dir>      # build into a scratch dir (determinism check)
  python -I tools/<this file> --write              # build into game/assets/characters/walk-pilots/
  python -I tools/<this file> --check <dir>        # independent PNG-level checks -> stdout JSON
"""
import argparse, hashlib, io, json, os, sys, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
V8_REL = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_"
          "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
V8_SHA256 = "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
OUT_REL = "game/assets/characters/walk-pilots"
STAMP = "20261015-024345"
RUN_ID = "ab7891d4"
VARIANT = "m8-w01"
SLUG = "rpg-2-star-ocean-the-second"
W, H = 80, 112
PIN = (40, 104)          # cell ground pin shared by every frame (v8: lowest row 103, feet mid x 40)

# v8 palette (manifest roles_v8), letter -> sRGB hex
ROLES = {"K": "#0a0a0e", "k": "#201c20", "O": "#23252b", "T": "#0a323b", "q": "#302526", "G": "#30333a",
         "b": "#41302b", "t": "#11525b", "n": "#533b32", "g": "#474b54", "m": "#634739", "L": "#714730",
         "u": "#1a767b", "l": "#845436", "w": "#7e5f4a", "z": "#626873", "v": "#249b98", "r": "#a16f4b",
         "D": "#bb7c50", "c": "#b09986", "s": "#e39664", "C": "#d7c0a8", "B": "#cfc8bd", "S": "#fbc38d",
         "W": "#faead4", "M": "#9a4634", "1": "#5e6e8c", "2": "#3a4560", "3": "#222839", "4": "#c07a40",
         "5": "#4a625c", "6": "#324542"}
RGB = {k: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for k, h in ROLES.items()}
INV = {v: k for k, v in RGB.items()}


def fid(role):
    """Short unique, reproducible file id per output role."""
    return hashlib.sha256(f"{RUN_ID}:{role}".encode()).hexdigest()[:8]


# ----------------------------------------------------------------------------- layer split
def owner(x, y, ch):
    """Ownership of a v8 texel.  Rows <= 60 are torso except the two forearms."""
    if y <= 60:
        if 47 <= y <= 53 and 18 <= x <= {47: 24, 52: 24, 53: 24}.get(y, 25):
            return "fist"
        if 53 <= y <= 56 and 46 <= x <= 53 and not (y == 53 and x >= 52):
            return "armr"
        if 57 <= y <= 60 and x >= 47:
            return "armr"
        return "torso"
    hand_left = {61: 47, 62: 47, 63: 47, 64: 47, 65: 47, 66: 47, 67: 47, 68: 48, 69: 49, 70: 50}
    if y in hand_left and x >= hand_left[y]:
        return "armr"
    coat_left = {61: 29, 62: 28, 63: 27}.get(y, 26 if y <= 70 else (25 if y <= 74 else -1))
    if x <= coat_left:                                  # left coat panel + teal cape
        return "torso"
    if y in (61, 62) and ch in "cC" and 30 <= x <= 40:  # shirt tails
        return "torso"
    flap = {61: (43, 46), 62: (43, 46), 63: (43, 46), 64: (43, 46), 65: (43, 46), 66: (44, 46), 67: (44, 46),
            68: (44, 46), 69: (45, 47), 70: (45, 47), 71: (45, 48), 72: (45, 48), 73: (47, 48), 74: (47, 51),
            75: (48, 50)}
    if y in flap and flap[y][0] <= x <= flap[y][1]:     # right coat flap over the vr thigh
        return "torso"
    if y <= 70:
        return "legvl" if x <= 35 else "legvr"
    return "legvl" if x <= 36 else "legvr"


# Hidden texels: covered in the idle stack, revealed only when a forearm/fist swings away.
TORSO_FILL = {(18, 47): "K", (19, 47): "2", (20, 47): "2", (21, 47): "2", (22, 47): "2", (23, 47): "3", (24, 47): "K",
              (19, 52): "K", (20, 53): "K", (21, 53): "K", (22, 53): "T", (23, 53): "t", (24, 53): "t",
              (46, 53): "2", (47, 53): "2", (48, 53): "2", (49, 53): "2", (50, 53): "2", (51, 53): "K", (50, 52): "2",
              (53, 54): "K", (46, 54): "3", (46, 55): "3", (46, 56): "3"}
LEGVR_FILL = {(47, 66): "6", (47, 67): "6", (48, 67): "6", (48, 68): "6", (49, 68): "6", (50, 68): "3", (51, 68): "K",
              (49, 69): "6", (50, 69): "3", (51, 69): "K", (50, 70): "K"}

# Hand-authored boots.  Row 0 = boot cuff row; x0 = cell column of string index 0; '.' = empty.
# vl_flat and vr_fwd are v8's own boots; the others are redrawn foot poses (no flip, no mirror).
BOOTS = {
    "vl_flat": (25, [
        "...qLLLLbq.", "...qLnLnbK.", "....kqbbk..", "....qbbbk..", "....qbbbk..", "...KsCbqLK.", "...KBBCLbK.",
        "...KCCqnqK.", "..KqnnbbbK.", "..nLLLbbbq.", ".nllLLqqbk.", "qLllLLqqkK.", "qbnnbqqK...", "qbqqbqK....",
        "KqbqqK.....", ".KKK......."]),
    "vl_fwd": (24, [
        "....qLLLLbq.", "....qLnLnbK.", ".....kqbbk..", ".....qbbbk..", ".....qbbbk..", "....KsCbqLK.",
        "....KBBCLbK.", "....KCCqnqK.", "...KqnnbbbK.", "...nLLLbbbq.", "..nllLLqqbk.", ".qLllLLqqkK.",
        ".qLllLLLqK..", "qLllrLLqqK..", "qbLlLLnqK...", "qbnnbbqqK...", "Kqbqqqqk....", ".qqqqqqK....",
        "..KKKKK....."]),
    "vl_heelup": (25, [
        "...qLLLLbq.", "...qLnLnbK.", "....kqbbk..", "....qbbbk..", "....qbbbk..", "...KsCbqLK.", "...KBBCLbK.",
        "...KCCqnqK.", "..KqnnbbbK.", "..nLLLbbbq.", "..qlLLqqbK.", "..qbnbqqK..", "..KqbqqK...", "...KKKK...."]),
    "vr_fwd": (43, [
        "KbbnbLbK....", "qqLLLLbK....", "KqnnLLbK....", ".KnnLbqK....", "..kbbbqK....", "..Kqbbbn....",
        "..KqbCCqK...", "..KbCbqLK...", "..KbBBCKK...", "...KqCbbK...", "...KbLLLq...", "...KbLnnqK..",
        "...kqLLLLq..", "...kbLllLLK.", "...KqbllLLbK", "....KqnLrnbK", "....KbbqqqbK", ".....qqqqqqK",
        "......KKKKK."]),
    "vr_back": (43, [
        "KbbnbLbK....", "qqLLLLbK....", "KqnnLLbK....", ".KnnLbqK....", "..kbbbqK....", "..Kqbbbn....",
        "..KqbCCqK...", "..KbCbqLK...", "..KbBBCKK...", "...KqCbbK...", "...KbLLLq...", "...KbllLLK..",
        "...kqllLLq..", "...KqbLLbK..", "....KqqqK...", ".....KKK...."]),
    "vr_heelup": (43, [
        "KbbnbLbK....", "qqLLLLbK....", "KqnnLLbK....", ".KnnLbqK....", "..kbbbqK....", "..Kqbbbn....",
        "..KqbCCqK...", "..KbCbqLK...", "..KbBBCKK...", "...KqCbbK...", "...KbLLLq...", "...KblLLK...",
        "...KqbbqK...", "....KKKK...."]),
}
LEG = {  # v8 source-row segments per leg; fill_row is repeated when the thigh must lengthen
    "vl": {"thigh": (61, 70), "knee": (71, 79), "fill_row": 70, "fill_extra": {26: "K"}},
    "vr": {"thigh": (61, 73), "knee": (74, 79), "fill_row": 72, "fill_extra": {}},
}
SHIN_ROWS = (80, 84)

# The loop.  bob = torso dy; per leg: kdy = knee/shin dy (ground-relative), sd = shin rows added
# (+) or overlapped (-), boot = variant, dx = inward tuck; armr/fist = (dx, dy) on top of the bob;
# cape = lagging cape-tip dx.  vl = viewer-left leg (character's right, knee guard).
FRAMES = [
    ("f01-contact-vr", "vr forward heel-strike, vl pushes off behind; right forearm back, fist forward",
     {"bob": 1, "vr": {"kdy": 2, "sd": -1, "boot": "vr_fwd"}, "vl": {"kdy": 0, "sd": 1, "boot": "vl_heelup"},
      "fist": (0, 1), "armr": (0, -2), "cape": 0}),
    ("f02-down-vr", "weight on vr (body lowest), vl toe-off with knee starting to bend and tuck",
     {"bob": 1, "vr": {"kdy": 1, "sd": -1, "boot": "vr_fwd"}, "vl": {"kdy": -1, "sd": 1, "boot": "vl_heelup", "dx": 1},
      "fist": (0, 1), "armr": (0, -1), "cape": -1}),
    ("f03-passing-vr", "vr straight under the body, vl knee lifted and tucked, foot clear of the ground",
     {"bob": 0, "vr": {"kdy": 0, "sd": 0, "boot": "vr_fwd"}, "vl": {"kdy": -2, "sd": 1, "boot": "vl_flat", "dx": 1},
      "fist": (0, 0), "armr": (0, 0), "cape": -1}),
    ("f04-up-vr", "vr late stance (foot 1 row up in cell), vl reaching forward to land",
     {"bob": 0, "vr": {"kdy": -1, "sd": 0, "boot": "vr_fwd"}, "vl": {"kdy": 1, "sd": -1, "boot": "vl_fwd"},
      "fist": (0, -1), "armr": (-1, 1), "cape": 0}),
    ("f05-contact-vl", "vl forward heel-strike, vr pushes off behind; right forearm forward, fist back",
     {"bob": 1, "vl": {"kdy": 2, "sd": -1, "boot": "vl_fwd"}, "vr": {"kdy": 0, "sd": 0, "boot": "vr_heelup"},
      "fist": (0, -1), "armr": (-1, 1), "cape": 0}),
    ("f06-down-vl", "weight on vl (body lowest), vr toe-off with knee starting to bend and tuck",
     {"bob": 1, "vl": {"kdy": 1, "sd": -1, "boot": "vl_fwd"}, "vr": {"kdy": -1, "sd": 1, "boot": "vr_heelup", "dx": -1},
      "fist": (0, -1), "armr": (-1, 1), "cape": 1}),
    ("f07-passing-vl", "vl straight under the body, vr knee lifted and tucked, foot clear of the ground",
     {"bob": 0, "vl": {"kdy": 0, "sd": 0, "boot": "vl_fwd"}, "vr": {"kdy": -2, "sd": 1, "boot": "vr_back", "dx": -1},
      "fist": (0, 0), "armr": (0, 0), "cape": 1}),
    ("f08-up-vl", "vl late stance (foot 1 row up in cell), vr reaching forward to land",
     {"bob": 0, "vl": {"kdy": -1, "sd": 0, "boot": "vl_fwd"}, "vr": {"kdy": 1, "sd": -1, "boot": "vr_fwd"},
      "fist": (0, 1), "armr": (0, -1), "cape": 0}),
]
IDLE = {"bob": 0, "vl": {"kdy": 0, "sd": 0, "boot": "vl_flat"}, "vr": {"kdy": 0, "sd": 0, "boot": "vr_fwd"}}
LAYER_ORDER = ["leg-vl", "leg-vr", "torso", "arm-right-forearm", "arm-left-fist"]  # back to front


# ----------------------------------------------------------------------------- helpers
def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_grid(path):
    a = np.array(Image.open(path).convert("RGBA"))
    return {(x, y): INV[tuple(int(c) for c in a[y, x, :3])] for y in range(H) for x in range(W) if a[y, x, 3]}


def shift(d, dx, dy):
    return {(x + dx, y + dy): c for (x, y), c in d.items()}


def rows_of(d, y0, y1):
    return {(x, y): c for (x, y), c in d.items() if y0 <= y <= y1}


def art(rows, x0, y0):
    return {(x0 + i, y0 + j): ch for j, row in enumerate(rows) for i, ch in enumerate(row) if ch != "."}


def split_layers(v8):
    L = {"torso": {}, "fist": {}, "armr": {}, "legvl": {}, "legvr": {}}
    for (x, y), ch in v8.items():
        L[owner(x, y, ch)][(x, y)] = ch
    L["armr"][(50, 52)] = L["torso"].pop((50, 52))     # cuff-top texel travels with the forearm
    t = dict(TORSO_FILL); t.update(L["torso"]); L["torso"] = t
    r = dict(LEGVR_FILL); r.update(L["legvr"]); L["legvr"] = r
    return L


def shin_rows(sd):
    rows = [80, 81, 82, 83, 84]
    if sd > 0:
        rows = [80, 81] + [82] * (1 + sd) + [83, 84]
    if sd < 0:
        rows = [r for r in rows if r not in [83, 82, 81][:-sd]]
    return rows


def build_leg(L, side, bob, kdy, sd, boot, dx=0):
    spec, src, out = LEG[side], L["leg" + side], {}
    t0, t1 = spec["thigh"]
    k0, k1 = spec["knee"]
    out.update(shift(rows_of(src, t0, t1), 0, bob))
    for yy in range(t1 + bob + 1, k0 + kdy):           # thigh lengthens when the knee drops
        for (x, y), c in src.items():
            if y == spec["fill_row"]:
                out[(x, yy)] = c
        for x, c in spec["fill_extra"].items():
            out[(x, yy)] = c
    rows = shin_rows(sd)
    for i, sy in enumerate(rows):
        for (x, y), c in src.items():
            if y == sy:
                out[(x + dx, SHIN_ROWS[0] + kdy + i)] = c
    out.update(shift(rows_of(src, k0, k1), dx, kdy))   # knee drawn over the thigh when lifted
    x0, art_rows = BOOTS[boot]
    top = SHIN_ROWS[0] + kdy + len(rows)
    out.update(art(art_rows, x0 + dx, top))
    return out, top + len(art_rows) - 1


def frame_layers(L, fr):
    bob = fr["bob"]
    legs, soles = {}, {}
    for side in ("vl", "vr"):
        p = fr[side]
        legs[side], soles[side] = build_leg(L, side, bob, p["kdy"], p["sd"], p["boot"], p.get("dx", 0))
    torso = dict(L["torso"])
    cdx = fr.get("cape", 0)
    if cdx:
        tip = {(x, y): c for (x, y), c in torso.items() if 67 <= y <= 74 and x <= 20}
        for p in tip:
            del torso[p]
        moved = shift(tip, cdx, 0)
        if cdx < 0:   # keep the cape's inner edge closed: repeat each row's rightmost texel
            for y in range(67, 75):
                xs = [x for (x, yy) in tip if yy == y]
                if xs:
                    moved[(max(xs), y)] = tip[(max(xs), y)]
        torso.update(moved)
    adx, ady = fr.get("armr", (0, 0))
    fdx, fdy = fr.get("fist", (0, 0))
    layers = {"leg-vl": legs["vl"], "leg-vr": legs["vr"], "torso": shift(torso, 0, bob),
              "arm-right-forearm": shift(L["armr"], adx, bob + ady), "arm-left-fist": shift(L["fist"], fdx, bob + fdy)}
    return layers, soles


def stack(layers):
    g = {}
    for name in LAYER_ORDER:
        g.update(layers[name])
    return g


def to_rgba(grid):
    a = np.zeros((H, W, 4), np.uint8)
    for (x, y), c in grid.items():
        if not (0 <= x < W and 0 <= y < H):
            raise SystemExit(f"texel outside cell: {(x, y)}")
        a[y, x, :3] = RGB[c]
        a[y, x, 3] = 255
    return a


def png_bytes(a):
    buf = io.BytesIO()
    Image.fromarray(a, "RGBA").save(buf, format="PNG")
    return buf.getvalue()


def frame_name(key):
    return f"{SLUG}_protagonist-female_south-walk-pilot-{key}_{VARIANT}_{STAMP}-{fid(key)}.png"


MANIFEST_NAME = f"{SLUG}_protagonist-female_south-walk-pilot-manifest_{VARIANT}_{STAMP}-{fid('manifest')}.json"
PXO_NAME = f"{SLUG}_protagonist-female_south-walk-pilot-editable_{VARIANT}_{STAMP}-{fid('pxo')}.pxo"


def make_pxo(per_frame_layers, preview_png):
    """Pixelorama 1.2.3 project (pxo_version 7), mirroring the structure of the team's existing .pxo files."""
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": False, "metadata": {}, "name": n,
                   "new_cels_linked": False, "opacity": 1.0, "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": True} for n in LAYER_ORDER]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0}
                             for _ in LAYER_ORDER], "duration": 1.0, "metadata": {}} for _ in per_frame_layers]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": "\"protagonist-female-south-walk-pilot\"",
                      "frame_current_tag": "0", "include_tag_in_filename": "false", "interpolation": "0",
                      "lines_count": "1", "new_dir_for_each_frame_tag": "false", "number_of_digits": "4",
                      "number_of_frames": "1", "orientation": "0", "repeat_count": "0", "resize": "100",
                      "save_quality": "0.75", "separator_character": "\"_\"",
                      "sheet_layers_as_separate_files": "false", "split_layers": "false"}
    data = {"author_company": "", "author_contact": "", "author_display_name": "", "author_real_name": "",
            "brushes": [], "color_mode": 5, "current_frame": 0, "current_layer": 2, "export_profile": export_profile,
            "fps": 10.0, "frames": frames_json, "guides": [], "layers": layer_json, "license": "", "metadata": {},
            "next_keyframe_id": 0, "palettes": [], "pixelorama_version": "v1.2.3-stable",
            "project_current_palette_name": "", "pxo_version": 7, "reference_images": [], "size_x": W, "size_y": H,
            "symmetry_points": [W - 1.0, H - 1.0], "tags": [], "tile_mode_x_basis_x": W, "tile_mode_x_basis_y": 0,
            "tile_mode_y_basis_x": 0, "tile_mode_y_basis_y": H, "tilesets": [], "user_data": "",
            "vanishing_points": []}
    buf = io.BytesIO()
    dt = (2026, 10, 15, 2, 43, 44)
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        def put(name, payload):
            z.writestr(zipfile.ZipInfo(name, dt), payload, zipfile.ZIP_DEFLATED)
        put("data.json", json.dumps(data, separators=(",", ":")))
        put("mimetype", "application/x-pixelorama")
        put("preview.png", preview_png)
        for fi, layers in enumerate(per_frame_layers, start=1):
            put(f"image_data/frames/{fi}/", b"")
            for li, name in enumerate(LAYER_ORDER, start=1):
                put(f"image_data/frames/{fi}/layer_{li}", to_rgba(layers[name]).tobytes())
                put(f"image_data/frames/{fi}/indices_layer_{li}", b"\x00")
    return buf.getvalue()


# ----------------------------------------------------------------------------- build
def build(out_dir):
    v8_path = os.path.join(REPO, V8_REL)
    if sha256_file(v8_path) != V8_SHA256:
        raise SystemExit("v8 source SHA-256 mismatch; refusing to build")
    v8 = load_grid(v8_path)
    L = split_layers(v8)
    if stack(frame_layers(L, IDLE)[0]) != v8:
        raise SystemExit("layer split is not lossless: idle re-stack differs from v8")
    os.makedirs(out_dir, exist_ok=True)
    written, frames_meta, per_frame_layers, previews = [], [], [], []
    for order, (key, intent, fr) in enumerate(FRAMES, start=1):
        layers, soles = frame_layers(L, fr)
        overlap = len(set(layers["leg-vl"]) & set(layers["leg-vr"]))
        if overlap:
            raise SystemExit(f"{key}: leg layers overlap ({overlap}); fixed .pxo layer order would not reproduce PNG")
        a = to_rgba(stack(layers))
        data = png_bytes(a)
        name = frame_name(key)
        written.append(_write(out_dir, name, data))
        per_frame_layers.append(layers)
        previews.append(data)
        frames_meta.append({"order": order, "key": key, "intent": intent, "file": name,
                            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
                            "duration_s_at_review_rate": 0.1, "pose": {k: (list(v) if isinstance(v, tuple) else v)
                                                                         for k, v in fr.items()},
                            "declared_sole_row": soles, "front_leg_for_review": "vr" if soles["vr"] > soles["vl"] else "vl"})
    pxo = make_pxo(per_frame_layers, previews[0])
    written.append(_write(out_dir, PXO_NAME, pxo))
    manifest = {
        "project": "Worlds Between", "milestone": "M8", "variant": VARIANT,
        "purpose": "Isolated south-facing walk pilot for the female protagonist, built from the approved static selout v8 idle.",
        "status": "technical pilot for human review; unapproved; not runtime-integrated",
        "art_approved": False, "human_reviewed": False, "runtime_integrated": False,
        "gates_changed": "none (0/52 exploration sprites, 0/11 scene gates unchanged)",
        "source": {"file": V8_REL, "sha256": V8_SHA256, "role": "read-only, source-locked; v8 approved as STATIC 48 px baseline only"},
        "builder": {"script": os.path.relpath(os.path.abspath(__file__), REPO).replace("\\", "/"),
                    "python": sys.version.split()[0], "pillow": Image.__version__, "numpy": np.__version__,
                    "method": "explicit texel layer split of v8 (lossless gate) + hand-authored integer placements, row repeats/overlaps and palette-letter boot redraws; no resampling, filtering, generative redraw, flip or mirror"},
        "cell": [W, H], "ground_pin_cell": list(PIN), "ground_line_row": 103,
        "display": {"logical_height_px": 48, "scale": 0.5, "texel_to_screen_px_at_1280x720": 1, "filter": "nearest"},
        "frame_counts": {"idle": {"south": 1, "file": "v8 unchanged (not copied)"}, "walk": {"south": len(FRAMES)}},
        "loop": [f["key"] for f in frames_meta], "review_fps": 10,
        "layer_order_back_to_front": LAYER_ORDER,
        "hidden_fill_texels": {"torso": len(TORSO_FILL), "leg-vr": len(LEGVR_FILL),
                               "note": "covered in the idle stack (lossless gate); exposed only by limb swings"},
        "boot_variants": {k: {"x0": v[0], "rows": len(v[1]), "source": "v8 texels" if k in ("vl_flat", "vr_fwd") else "hand-authored texel redraw"}
                          for k, v in BOOTS.items()},
        "frames": frames_meta,
        "editable": {"file": PXO_NAME, "sha256": hashlib.sha256(pxo).hexdigest(), "format": "Pixelorama pxo_version 7 (v1.2.3), 8 frames x 5 layers"},
        "files_added": [os.path.basename(p) for p in written] + [MANIFEST_NAME],
    }
    mbytes = (json.dumps(manifest, indent=1) + "\n").encode()
    written.append(_write(out_dir, MANIFEST_NAME, mbytes))
    for p in written:
        print("WROTE", p, sha256_file(p))


def _write(out_dir, name, data):
    path = os.path.join(out_dir, name)
    if os.path.exists(path):
        with open(path, "rb") as f:
            if f.read() != data:
                raise SystemExit(f"refusing to overwrite different bytes: {path}")
    else:
        with open(path, "wb") as f:
            f.write(data)
    return path


# ----------------------------------------------------------------------------- independent checks
KNEE_GUARD = set("OGzgv")


def check(frame_dir):
    """Reads only PNGs on disk (frames + v8).  Independent of the build bookkeeping except file names."""
    v8a = np.array(Image.open(os.path.join(REPO, V8_REL)).convert("RGBA"))
    v8_cols = {tuple(c) for c in v8a[v8a[..., 3] > 0][:, :3].tolist()}
    res = {"frames": []}
    head = (slice(8, 34), slice(0, W))
    prev = None
    for key, _, _ in FRAMES:
        p = os.path.join(frame_dir, frame_name(key))
        im = Image.open(p)
        a = np.array(im.convert("RGBA"))
        op = a[..., 3] > 0
        ys, xs = np.nonzero(op)
        r = {"key": key, "size": list(im.size), "mode": im.mode,
             "alpha_values": sorted(set(np.unique(a[..., 3]).tolist())),
             "border_opaque": int(op[0].sum() + op[-1].sum() + op[:, 0].sum() + op[:, -1].sum()),
             "colours": len({tuple(c) for c in a[op][:, :3].tolist()}),
             "colours_outside_v8": len({tuple(c) for c in a[op][:, :3].tolist()} - v8_cols),
             "bbox_xyxy": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
             "visible_height": int(ys.max() - ys.min() + 1), "lowest_row": int(ys.max())}
        # bob found by exact search of the head/face/hair rows (8-33) against v8
        bob = None
        for dy in range(-3, 4):
            if np.array_equal(np.roll(v8a, dy, axis=0)[8 + dy:34 + dy], a[8 + dy:34 + dy]):
                bob = dy
                break
        r["bob_found_by_head_search"] = bob
        # locked upper body: v8 rows 8-52 shifted by bob, excluding the swinging forearm/fist boxes
        mism = 0
        if bob is not None:
            sh = np.roll(v8a, bob, axis=0)
            for y in range(8 + bob, 53 + bob):
                for x in range(W):
                    if 16 <= x <= 26 and 45 + bob <= y <= 56 + bob:
                        continue
                    if 44 <= x <= 55 and 50 + bob <= y:
                        continue
                    if not np.array_equal(sh[y, x], a[y, x]):
                        mism += 1
        r["locked_upper_body_mismatch_texels"] = mism
        # soles per leg (opaque rows >= 85, viewer-left x<38 vs viewer-right x>=38)
        r["sole_row_vl"] = int(max(y for y, x in zip(ys, xs) if y >= 85 and x < 38))
        r["sole_row_vr"] = int(max(y for y, x in zip(ys, xs) if y >= 85 and x >= 38))
        r["stride_separation_rows"] = abs(r["sole_row_vl"] - r["sole_row_vr"])
        # knee-guard ownership (guard colours in the leg region, x<40)
        kg = [(x, y) for y, x in zip(ys, xs) if 66 <= y <= 86 and x < 40 and INV.get(tuple(int(c) for c in a[y, x, :3])) in KNEE_GUARD]
        r["knee_guard_texels"] = len(kg)
        r["knee_guard_centroid"] = [round(float(np.mean([p[0] for p in kg])), 2), round(float(np.mean([p[1] for p in kg])), 2)] if kg else None
        r["knee_guard_on_viewer_left"] = bool(kg) and r["knee_guard_centroid"][0] < PIN[0]
        # cape / scarf tail (teal u/t/T, x<23, rows 52-80) stays viewer-left
        cape = [x for y, x in zip(ys, xs) if 52 <= y <= 80 and x < 23 and INV.get(tuple(int(c) for c in a[y, x, :3])) in ("u", "t", "T")]
        r["cape_centroid_x"] = round(float(np.mean(cape)), 2)
        # knee band motion vs bob-shifted idle (rows 73-83 + bob, x 23-60, forearm zone excluded)
        if bob is not None:
            sh = np.roll(v8a, bob, axis=0)
            kb = 0
            for y in range(73 + bob, 84 + bob):
                for x in range(23, 61):
                    if x >= 44 and y <= 71 + bob:
                        continue
                    if not np.array_equal(sh[y, x], a[y, x]):
                        kb += 1
            r["knee_band_changed_texels"] = kb
        # leg separation: rows 80-100 with a transparent texel between the legs (x 36-44)
        r["leg_gap_rows_80_100"] = int(sum(1 for y in range(80, 101) if (~op[y, 36:45]).any()))
        r["identical_to_v8"] = bool(np.array_equal(a, v8a))
        r["identical_to_previous_frame"] = bool(prev is not None and np.array_equal(a, prev))
        prev = a
        res["frames"].append(r)
    hashes = [sha256_file(os.path.join(frame_dir, frame_name(k))) for k, _, _ in FRAMES]
    res["all_frames_unique"] = len(set(hashes)) == len(hashes)
    res["v8_sha256_still"] = sha256_file(os.path.join(REPO, V8_REL))
    res["v8_unchanged"] = res["v8_sha256_still"] == V8_SHA256
    # .pxo layers re-stack to the frame PNGs
    with zipfile.ZipFile(os.path.join(frame_dir, PXO_NAME)) as z:
        d = json.loads(z.read("data.json"))
        ok = []
        for fi, (key, _, _) in enumerate(FRAMES, start=1):
            comp = np.zeros((H, W, 4), np.uint8)
            for li in range(1, len(d["layers"]) + 1):
                cel = np.frombuffer(z.read(f"image_data/frames/{fi}/layer_{li}"), np.uint8).reshape(H, W, 4)
                m = cel[..., 3] > 0
                comp[m] = cel[m]
            ok.append(bool(np.array_equal(comp, np.array(Image.open(os.path.join(frame_dir, frame_name(key))).convert("RGBA")))))
        res["pxo"] = {"frames": len(d["frames"]), "layers": [l["name"] for l in d["layers"]],
                      "pxo_version": d["pxo_version"], "restack_equals_png_per_frame": ok}
    return res


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--out-dir")
    g.add_argument("--write", action="store_true")
    g.add_argument("--check")
    args = ap.parse_args()
    if args.check:
        print(json.dumps(check(args.check), indent=1))
        return
    out = args.out_dir or os.path.join(REPO, OUT_REL)
    build(out)


if __name__ == "__main__":
    main()
