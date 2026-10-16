"""UNAPPROVED, test-only pilot v09: female protagonist side-view battle idle, facing right, ONE static frame.

Static-frame refinement of v08 (no motion, no batch, no runtime swap). Same cell (68x72), same pin (32, 68), same sole
row 67, same crown row 7, same 18 layers + guides in the same order and the same 30-key palette, so the owner-approved
0.65 battle display proportion (crown-to-sole 61 logical px at node scale 1.0) and the foot baseline are unchanged.
v08's files are read (hash-gated) and never written.

Targets only the three issues the Codex v08 visual audit (docs/qa/...battle-static-v08-codex-visual-audit_unapproved-
v01_20261016-145125-5e1b7d6c.md) still names at 1x in the real 1280x720 four-person captures:
  dark far leg / boots blend    -> value-grouped against the measured floor, not outlined: the far trouser leg is the
  into both floors                 v8 trouser deep (C, the slate v8 itself shades its trousers with) with one spruce (T)
                                   front edge, so it sits ~40 L under the paving; the parts of both boots that stand in
                                   the contact shadow (rows 62-65, floor L ~45-58) are mid leather (b) with a lit (B)
                                   instep edge instead of the shadow-valued l; shafts above the shadow stay dark (L/l)
  roll nearly joins the scarf;  -> the roll is drawn end-on as a 7x7 coil (outer ring lit top-right, one dark spiral
  reads as a shoulder block        turn, shadowed base) sitting on the back half of the pack; its right edge ends at
                                   x21, so two fully transparent columns (x22-23) separate it from the coat/scarf
  narrow hip drape              -> v8's back-hip fabric widened (5-7 texels) and lengthened to row 54: it flares back
                                   past the coat tail, one diagonal fold line (Q) runs down it and becomes the split
                                   between two hem tails; lit front edge (G), shadowed back edge (q); it stays left of
                                   the far leg's back edge, so no stance texel is covered
Unchanged layers (byte-identical to v08's .ora layers): pack, ponytail, coat, coat-skirt, shirt-lapel, near-arm,
sword-blade, sword-guard, fist, head, hair-tie, collar, scarf-neck, collar-front. near-leg changes only in the boot's
rows 62-65. So v08's fist/belt and sword continuity fixes are kept exactly.

Hand-authored pixel art: each layer is an ASCII block typed below ('.' = transparent). The blade is placed by a 1:1
pixel-line helper (the texels a line tool lays). No resampling, filtering, gradients, dithering, quantizing, image
generation or upscaling. Binary alpha. Fixed palette (<= 32 colours).

Editable source: a layered Pixelorama .pxo (pxo_version 7) and an .ora with the same layers plus a hidden, locked
'guides' layer. The candidate PNG is the Pixelorama 1.2.3 headless flat export of the .pxo (byte-compared to this
tool's render); Pixelorama runs with APPDATA redirected to a fresh temp dir so the real config is never touched.

Modes
  preview <dir> [ruins-nosprite.png outskirts-nosprite.png]
                  inspection PNGs in <dir> (outside the repo); with no-sprite captures, also the exact game-scale
                  composite (2x nearest at texture origin 536, 408, as the Godot capture draws it)
  build           export via Pixelorama, write PNG + .pxo + .ora + manifest (never overwrites a different file)
  check           technical gates on the built files incl. Pixelorama flat + split-layer round-trips, palette identity
                  with v08, per-layer identity with v08's .ora, changed texels only inside the intended regions, and
                  layer-stack recomposition of the .pxo and .ora; writes nothing

Run with the real Python in isolated mode:  python -I -B <this file> preview <dir> | build | check
"""
import argparse, hashlib, io, json, os, shutil, subprocess, sys, tempfile, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
VER = "unapproved-v09"
STAMP = "20261016-135202"
RUN_ID = "43cf7e01"
W, H = 68, 72
PIN = (32, 68)            # same as v03-v08: first transparent row under the soles, between the feet
CROWN_ROW = 7             # same as v03-v08: head crown row; soles end on row 67 -> crown-to-sole 61 rows
SOLE_ROW = 67
OUT_DIR_REL = "game/assets/characters/combat-sideview-pilots"
_V08 = "rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_"
V08_LOCKS = {             # v08 (committed in 15c9b73) is read-only for this tool: checked before and after every build/check
    OUT_DIR_REL + "/" + _V08 + "unapproved-v08_20261016-095054-a06775a0.png":
        "edee2924e1058fa2058f04ea2d507f744e97c93999c6183bf7b7730c51d0adc5",
    OUT_DIR_REL + "/" + _V08 + "editable-layers_unapproved-v08_20261016-095054-2574ce1c.pxo":
        "bf7111a24953699ca966fc5f68bc5f8512456f64a4c0578e99f64df2d04544cb",
    OUT_DIR_REL + "/" + _V08 + "editable-layers_unapproved-v08_20261016-095054-314d939f.ora":
        "818e4bd4e0618a42d8680033a3d92b8a28ad660cee4cda3e488c0598e6048e34",
    OUT_DIR_REL + "/" + _V08 + "manifest_unapproved-v08_20261016-095054-ab653c87.json":
        "8ec39ef6ac086507c4061d9976100ce4954fc9856a6bfabce9e6a926a903814b",
}
V08_PNG_REL, V08_PXO_REL, V08_ORA_REL, V08_MANIFEST_REL = list(V08_LOCKS)
# The only places v09 may differ from v08 (inclusive texel boxes x0, y0, x1, y1), and the layers each one belongs to.
# check fails if any composite or layer texel changes outside them, or if one of them is left unchanged.
INTENDED_REGIONS = {
    "far leg trouser + far boot": {"box": (16, 42, 33, 67), "layers": ["far-leg"]},
    "near boot instep (in the contact shadow)": {"box": (37, 62, 48, 65), "layers": ["near-leg"]},
    "bedroll (end-on coil, gap to scarf)": {"box": (14, 21, 24, 28), "layers": ["bedroll"]},
    "hip drape (wider, split hem)": {"box": (14, 40, 30, 55), "layers": ["hip-drape"]},
}
CHANGED_LAYERS = sorted({n for r in INTENDED_REGIONS.values() for n in r["layers"]})
V8_SOUTH_REL = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_"
                "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
PIXELORAMA_REL = "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"
PIXELORAMA_VERSION = "v1.2.3-stable"
GUIDE_RGB = (255, 0, 255)
CAPTURE_ORIGIN = (536, 408)   # screen px of texel (0, 0) in the 1280x720 party capture (hero x 300, floor 272, 2x)


def fid(role):
    return hashlib.sha256(f"{RUN_ID}:{role}".encode()).hexdigest()[:8]


SUBJECT = "protagonist-female_sideview-idle-right-static-native0p65"
PNG_NAME = f"{SLUG}_{SUBJECT}_{VER}_{STAMP}-{fid('png')}.png"
PXO_NAME = f"{SLUG}_{SUBJECT}_editable-layers_{VER}_{STAMP}-{fid('pxo')}.pxo"
ORA_NAME = f"{SLUG}_{SUBJECT}_editable-layers_{VER}_{STAMP}-{fid('ora')}.ora"
MANIFEST_NAME = f"{SLUG}_{SUBJECT}_manifest_{VER}_{STAMP}-{fid('manifest')}.json"
TOOL_REL = "tools/" + os.path.basename(os.path.abspath(__file__))

PALETTE = {
    "K": "#16141a",                                                                  # outline
    "1": "#231816", "2": "#3d2a22", "3": "#5c3e2c", "4": "#82593b", "h": "#a8794f",  # hair dark -> sheen
    "S": "#fbd5b0", "s": "#e7a67c", "x": "#b36f50", "E": "#1d1214",                  # skin light/mid/shadow, eye/brow
    "C": "#222839", "c": "#3a4560", "o": "#5e6e8c",                                  # v8 storm-slate coat C3/C2/C1
    "T": "#324542", "t": "#4a625c",                                                  # v8 spruce trousers T2/T1
    "W": "#f3ead9", "w": "#c6b59d",                                                  # shirt / shadowed white
    "P": "#d7c0a8", "p": "#b09986",                                                  # v8 pale beige: cuff, buckle
    "L": "#2e1c14", "l": "#533626", "b": "#845436", "B": "#bb7c50",                  # leather (v8 warm ramp)
    "Q": "#0a323b", "q": "#1a767b", "g": "#249b98", "G": "#6cc9bc",                  # teal (v8 scarf + one light)
    "m": "#5a6470", "M": "#a9b5bd", "Z": "#eef4f5",                                  # steel
}

LAYERS = []


def tr(text, mapping):
    """Re-point keys in one simultaneous pass (shape untouched)."""
    return text.translate(str.maketrans(mapping))


def block(name, x0, y0, text):
    """One layer from an ASCII block: row i of text is canvas row y0+i, column j is canvas x0+j."""
    rows = [r for r in text.strip("\n").split("\n")]
    LAYERS.append((name, [(x0 + j, y0 + i, ch) for i, r in enumerate(rows) for j, ch in enumerate(r.strip())
                          if ch != "."]))


def block_px(name, texels):
    LAYERS.append((name, list(texels)))


# ===================================================================================================== layers
# bottom -> top.  Column rulers in comments are absolute canvas x.

# far (back) leg angled back onto the ball of the foot, shape unchanged from v08. v09 values, chosen against the
# measured floor behind each row (paving L ~70-100 down to row 61, contact shadow L ~45-58 on rows 62-67):
#   trouser: v8 trouser deep (C, L 40) body + one spruce (T) front edge, instead of v08's T body + t edge (L 65 / 92,
#            both within ~20 L of the paving); interior value only, the outline is the same K
#   boot:    shaft (rows 60-61) stays dark leather over the paving; the cuff's back end is l, not the floor-valued b;
#            the foot in the shadow (rows 62-65) is mid leather b with a lit B instep edge instead of the shadow-valued l;
#            heel back and sole band stay L
#                x16       x26       x36
block("far-leg", 16, 42, """
...........KCCCTK.
...........KCCCTK.
..........KCCCTK..
..........KCCCTK..
.........KCCCTK...
.........KCCCTK...
........KCCCTK....
........KCCCTK....
.......KCCCTK.....
.......KCCTK......
.......KCCTK......
......KCCTK.......
......KCCTK.......
......KCCTK.......
.....KCCTK........
.....KCCTK........
....KKKKKKK.......
....KlBBBBK.......
...KLLLLLlK.......
...KLllllllK......
..KLbbbbbbbBK.....
..KLbbbbbbbbBK....
.KLLbbbbbbbbbBK...
.KKLLbbbbbbbbbBK..
...KKLLLLLLLLLLLK.
.....KKKKKKKKKKKK.
""")

# tan leather pack on the upper back: plain lit block (B) with a shadowed flap edge, one pale-beige buckle, darker base;
# v07's diamond emblem is gone (it read only at zoom). The coat draws over its right edge.
block("pack", 16, 28, """
KKKKKKKKK
KBBBBBBBK
KBBBBBBbK
KbbbbbbbK
KBBBPBBbK
KBBBpBBbK
KBBBBBBbK
KbBBBBbbK
KlbbbbblK
.KKKKKKK.
""")

# teal blanket roll on top of the pack, seen end-on (it lies across the back, as v8 south carries it): a 7x7 coil with
# the outer ring lit top-right (G), body (g), shadowed base (q) and one dark spiral turn (Q) curling round a lit core.
# It sits on the back half of the pack and ends at x21, so columns x22-23 stay transparent between it and the coat's
# back/scarf (v08's capsule ran to x23 and read as one teal shoulder block with the scarf at 1x)
#               x15   x21
block("bedroll", 15, 22, """
..KKK..
.KgGGK.
KgQQQGK
KqQgQgK
KqQggqK
.KqqqK.
..KKK..
""")

# single tapering ponytail (v07 shape): tall asymmetric plume, one clean tail ending on row 20 above the roll
block("ponytail", 14, 1, """
..........KK...
........KK4K...
......KK344hK..
.....K23344hhK.
....K123344h4K.
...K1223344334K
..K1223344433K.
..K12223343KK..
.K1122233K.....
.K112223K......
.K11223K.......
.K11223K.......
.K1122K........
.K1122K........
..K112K........
..K112K........
..K11K.........
...K11K........
...K1K.........
....KK.........
""")

# near (front) leg: thigh forward to a bent knee with the leather knee pad, shin down to a flat strapped boot; deep
# slate back edge (C), spruce body (T), lit front edge (t)
#                x32       x42
block("near-leg", 32, 41, """
.KCTTtK..........
.KCTTtK..........
..KCTTtK.........
..KCTTtK.........
...KCTTtK........
...KCTTttK.......
....KCTTtK.......
....KCTTttK......
.....KCTTtK......
.....KLLlbBK.....
.....KLLlbBK.....
......KLlbK......
......KCTtK......
......KCTtK......
......KCTtK......
......KCTtK......
.....KCTTtK......
.....KCTTtK......
.....KKKKKKKK....
.....KLbBBBbK....
.....KLLLLLLK....
.....KLbbbbBBK...
.....KLbbbbbBBK..
.....KLbbbbbbbBK.
.....KLLbbbbbbBK.
.....KLLLLLLLLLK.
......KKKKKKKKKK.
""")

# coat torso + belt, value-grouped: deep back half (C), a thin mid band (c), lit front plane (o); the belt's top row is
# lit leather (B) so the waist reads as one warm line between jacket and hip
block("coat", 24, 22, """
...KKKKK.......
.KKCcoooK......
KCCCcoooo......
KCCCCcoooo.....
KCCCCCcoooo....
KCCCCCcooooo...
KCCCCCCcooooo..
KCCCCCCcoooooo.
KCCCCCCcoooooo.
KCCCCCCcoooooo.
KCCCCCCcoooooo.
KCCCCCCcoooooo.
KCCCCCCcoooooo.
KCCCCCCcooooooo
KCCCCCCcooooooo
KCCCCCCcooooooo
KBBBBBBBBBBBBBBB
KLLLLLLLLLLLLLLL
""")

# coat skirt: deep back tail (C) over the far thigh, one-texel mid band (c), lit front panel (o) over the near thigh,
# lit leather hem trim (B) along both hems
#                  x17       x27       x37
block("coat-skirt", 17, 40, """
......KCCCCCCcoooooooooooK.
.....KCCCCCCcoCoooooooooooK
.....KCCCCCCcoCKooooooooooK
....KCCCCCCcoCCKoooooooooBK
....KCCCCCCcoCCKooooooooBK.
...KCCCCCCcoCCCKoooooBBBK..
...KCCCCCCcoCCK.KBBBBKKK...
...KCCCCCcoCCK...KKKK......
..KCCCCCCcoBK..............
..KCCCCCcBBK...............
..KCCCcBBK.................
.KCCBBBK...................
.KBBKK.....................
.KKK.......................
""")

# v8's teal back-hip fabric, wider and longer than v08's sash: it hangs from the belt over the coat's deep back tail
# and flares back past it to x15. Plain mid body (g) with a lit front edge (G) at the top; from row 45 one diagonal fold
# line (Q) runs parallel to the front edge and opens into the split between two hem tails (rows 52-54), echoing v8's
# ragged drape hem; the flared underside at the back is shadowed (q/Q). Its front edge stays left of the far leg's
# back edge on every row, so the stance is not covered.
#                   x15       x25
block("hip-drape", 15, 40, """
........KggggGK
........KggggGK
.......KggggGK.
.......KggggGK.
......KggggGK..
.....KgggQgGK..
.....KggQgGK...
....KgggQgGK...
...KgggQgGK....
..KqgggQgGK....
..KqggQgGK.....
.KQqgQgGK......
KQqgKgGK.......
KQqK.KK........
.KK............
""")

# open coat front over the white shirt, lit lapel edge (v07 shape)
block("shirt-lapel", 32, 23, """
ooKWWK..
oooKWWK.
.ooKWWWK
.ooKwWWK
..oKwWWWK
..oKwWWWK
..oKwWWWK
...KwWWWK
...KwWWWK
...KwWWWK
...KwWWK.
...KwWWK.
...KwWWK.
...KwWWK.
...KwWWK.
""")

# near arm bent at the elbow: lit slate sleeve top over a deep underside, forearm carried forward across the white shirt
# (top o, mid c, underside C), rolled pale-beige cuff; the fist is its own layer above the sword grip
#               x25       x35
block("near-arm", 25, 23, """
..KKKKK.......
.KooooooK.....
.KCoooooK.....
.KCoooooK.....
.KCCooooK.....
.KCCooooK.....
.KCCooooKKKKK.
.KCCoooooooPPK
..KCCcccccPpK.
...KCCCCCCppK.
....KKKKKKKK..
""")


# ordinary short sword raised forward at 45 degrees: each row is outline, edge light (Z), steel (M), outline, one texel
# further forward per row up, so the light core stays connected (no stair notches); short tapered tip
def blade_segments(y0=26, y1=18):
    segs = []
    for y in range(y1, y0 + 1):
        x = 70 - y                       # edge-light column on row y
        segs += [(x - 1, y, "K"), (x, y, "Z"), (x + 1, y, "M"), (x + 2, y, "K")]
    x = 70 - (y1 - 1)
    segs += [(x - 1, y1 - 1, "K"), (x, y1 - 1, "Z"), (x + 1, y1 - 1, "K"), (x, y1 - 2, "K")]
    return segs


block_px("sword-blade", blade_segments())

# small steel crossguard square to the blade, at the top-front of the fist
block("sword-guard", 41, 25, """
KK...
KMK..
.KMK.
..KMK
...KK
""")

# light tan glove closed round the grip, held at chest height in front of the shirt (four rows above the belt); the
# grip's leather end shows under the little finger
block("fist", 37, 27, """
.KKKK..
KBBBBK.
KBBBbbK
KbBbbbK
KbbbblK
.KLKKK.
..K....
""")

# head: v05 shape unchanged
block("head", 24, 7, """
.....KKKKKKK.......
...KK2334hh43KK....
..K22334hh4433KK...
.K1223344h44333K...
.K12233443443333K..
.K1223343321SSS3K..
.K122332232SSSEESK.
.K1223222sSSSSESSK.
.K1122221xssSSESSSK
.K1122211ssSSSSSSK.
.K1122111sSSSSSxSK.
.K112111KxssSSSSK..
..K1111K.KxssKKK...
""")

# leather hair tie knotted on the crown-back, where the ponytail leaves the head (v05 shape)
block("hair-tie", 24, 7, """
.KK.
KbBK
KLbK
.KK.
""")

# raised coat collar standing behind the nape (v06 shape)
block("collar", 24, 16, """
.KK..
KooK.
KoooK
KoooK
KCooK
KCcoK
""")

# scarf at the neck: thick wrap, knot and short front tail (v05 shape)
block("scarf-neck", 25, 20, """
.KqggGGggggGgK.
KQqqgggqqggGGgK
KQQqqqqQqqggGgK
KQQQqqQQqqggqK.
.KKKKKKKQqgGqK.
........KqgGK..
........KQqgK..
.........KqK...
..........K....
""")

# front half of the raised collar over the scarf's front edge (v07 shape)
block("collar-front", 38, 20, """
.KK.
KooK
KooK
KcoK
KcoK
.KK.
""")

LAYER_NAMES = [n for n, _ in LAYERS] + ["guides"]



# ===================================================================================================== raster
def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def guides_rgba(comp):
    g = np.zeros((H, W, 4), np.uint8)
    pts = set()
    pts.update((x, 0) for x in range(W)); pts.update((x, H - 1) for x in range(W))
    pts.update((0, y) for y in range(H)); pts.update((W - 1, y) for y in range(H))
    for y in (CROWN_ROW, SOLE_ROW):
        pts.update((x, y) for x in list(range(1, 4)) + list(range(W - 4, W - 1)))
    pts.add(PIN)
    for x, y in pts:
        g[y, x, :3] = GUIDE_RGB
        g[y, x, 3] = 255
    if (comp[..., 3][g[..., 3] > 0] != 0).any():
        raise SystemExit("a guide texel overlaps an opaque art texel")
    return g


def render():
    """Returns ({layer name: RGBA}, composite RGBA). Alpha is binary, so 'over' is a plain copy."""
    blobs = {}
    comp = np.zeros((H, W, 4), np.uint8)
    for name, texels in LAYERS:
        a = np.zeros((H, W, 4), np.uint8)
        for x, y, ch in texels:
            if ch not in PALETTE:
                raise SystemExit(f"{name}: unknown key {ch!r} at x{x} y{y}")
            if not (0 <= x < W and 0 <= y < H):
                raise SystemExit(f"{name}: texel ({x},{y}) outside the {W}x{H} cell")
            a[y, x, :3] = hex_rgb(PALETTE[ch])
            a[y, x, 3] = 255
        blobs[name] = a
        m = a[..., 3] == 255
        comp[m] = a[m]
    blobs["guides"] = guides_rgba(comp)
    return blobs, comp


def png_bytes(rgba):
    buf = io.BytesIO()
    Image.fromarray(rgba, "RGBA").save(buf, "PNG", optimize=False, compress_level=9)
    return buf.getvalue()


# ===================================================================================================== paths / hashes
WIN_MAX_PATH = 259
WIN_LONG_PREFIX = "\\\\?\\"


def _fs(path):
    path = os.path.abspath(path)
    if os.name == "nt" and len(path) > WIN_MAX_PATH - 12 and not path.startswith(WIN_LONG_PREFIX):
        return WIN_LONG_PREFIX + path
    return path


def repo_path(rel):
    return os.path.join(REPO, *rel.split("/"))


def read_bytes(path):
    with open(_fs(path), "rb") as f:
        return f.read()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def lock_hash(rel):
    """sha256-bytes for binaries; sha256-text-lf-v1 (CRLF -> LF) for the .json lock, so a core.autocrlf=true clone of
    the LF blob still matches. The committed v08 manifest is LF, so both algorithms give the same locked value."""
    data = read_bytes(repo_path(rel))
    return sha256_bytes(data.replace(b"\r\n", b"\n") if rel.endswith(".json") else data)


def v08_lock():
    files = {rel: lock_hash(rel) for rel in V08_LOCKS}
    return {"files": files, "unchanged": all(files[rel] == want for rel, want in V08_LOCKS.items())}


# ===================================================================================================== v08 comparison
def v08_reference():
    """v08's flat PNG, its per-layer RGBA from the locked .ora, and its manifest palette (all read-only)."""
    png = decode(read_bytes(repo_path(V08_PNG_REL)))[2]
    with zipfile.ZipFile(io.BytesIO(read_bytes(repo_path(V08_ORA_REL)))) as z:
        names = [n[len("data/"):-len(".png")] for n in z.namelist() if n.startswith("data/") and n.endswith(".png")]
        layers = {n: decode(z.read(f"data/{n}.png"))[2] for n in names}
    man = json.loads(read_bytes(repo_path(V08_MANIFEST_REL)))
    order = [l["name"] for l in man["layers_bottom_to_top"]]
    return png, layers, order, man["palette"]


def in_box(x, y, box):
    return box[0] <= x <= box[2] and box[1] <= y <= box[3]


def diff_texels(a, b):
    """(x, y) of texels whose RGBA differs."""
    ys, xs = np.nonzero((a != b).any(-1))
    return list(zip(xs.tolist(), ys.tolist()))


def scope_report(comp, blobs):
    """Where v09 differs from v08: composite and per layer, against INTENDED_REGIONS."""
    v08_png, v08_layers, v08_order, v08_pal = v08_reference()
    boxes = [r["box"] for r in INTENDED_REGIONS.values()]
    comp_diff = diff_texels(comp, v08_png)
    outside = [p for p in comp_diff if not any(in_box(*p, b) for b in boxes)]
    per_region = {k: sum(1 for p in comp_diff if in_box(*p, r["box"])) for k, r in INTENDED_REGIONS.items()}
    layers = {}
    for name in LAYER_NAMES:
        d = diff_texels(blobs[name], v08_layers[name]) if name in v08_layers else None
        allowed = [r["box"] for r in INTENDED_REGIONS.values() if name in r["layers"]]
        layers[name] = {"changed_texels": None if d is None else len(d),
                        "changed_outside_its_regions": None if d is None else
                        sum(1 for p in d if not any(in_box(*p, b) for b in allowed))}
    return {
        "composite_changed_texels": len(comp_diff),
        "composite_changed_outside_intended_regions": len(outside),
        "composite_changed_per_intended_region": per_region,
        "layers": layers,
        "unchanged_layers": [n for n in LAYER_NAMES if layers[n]["changed_texels"] == 0],
        "layer_order_same_as_v08": LAYER_NAMES == v08_order + (["guides"] if v08_order[-1] != "guides" else []),
        "palette_same_as_v08": {k: v.lower() for k, v in PALETTE.items()} == {k: v.lower() for k, v in v08_pal.items()},
    }


def scope_ok(s):
    return (s["composite_changed_outside_intended_regions"] == 0
            and all(n > 0 for n in s["composite_changed_per_intended_region"].values())
            and all(v["changed_texels"] is not None for v in s["layers"].values())
            and all(v["changed_outside_its_regions"] == 0 for v in s["layers"].values())
            and sorted(n for n in LAYER_NAMES if s["layers"][n]["changed_texels"]) == CHANGED_LAYERS
            and s["layer_order_same_as_v08"] and s["palette_same_as_v08"])


def roll_gap(comp):
    """Transparent columns between the roll's right edge and the next opaque texel, per roll row (rows 22-27)."""
    op = comp[..., 3] > 0
    out = {}
    for y in range(22, 28):
        xs = [x for x in range(14, 24) if op[y, x]]
        right = max(x for x in xs if x <= 21) if any(x <= 21 for x in xs) else None
        nxt = next((x for x in range(right + 1, W) if op[y, x]), None) if right is not None else None
        out[y] = None if nxt is None else nxt - right - 1
    return out


def recompose(layer_rgba):
    """Plain 'over' of binary-alpha layers in order (guides are hidden and skipped)."""
    comp = np.zeros((H, W, 4), np.uint8)
    for name in LAYER_NAMES[:-1]:
        a = layer_rgba[name]
        m = a[..., 3] == 255
        comp[m] = a[m]
    return comp


def decode(png):
    im = Image.open(io.BytesIO(png))
    return im.mode, im.size, np.array(im.convert("RGBA"))


# ===================================================================================================== metrics
def lum(rgb):
    rgb = np.asarray(rgb, float)
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def isolated_texels(comp):
    rgb = comp[..., :3].astype(np.int32)
    key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    op = comp[..., 3] > 0
    line = key == int(PALETTE["K"][1:], 16)
    n = 0
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not op[y, x] or line[y, x]:
                continue
            if not any(op[y + dy, x + dx] and key[y + dy, x + dx] == key[y, x]
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                n += 1
    return n


def stats(comp):
    m = comp[..., 3] > 0
    ys, xs = np.nonzero(m)
    cols = {"#%02x%02x%02x" % tuple(int(c) for c in px) for px in comp[m][:, :3]}
    pal = {v.lower() for v in PALETTE.values()}
    crown_cols = [x for x in range(24, 42) if m[CROWN_ROW, x] and not m[:CROWN_ROW, x].any()]
    head_top = min(int(np.nonzero(m[:, x])[0].min()) for x in range(24, 42) if m[:, x].any() and x in crown_cols) \
        if crown_cols else None
    return {
        "size": [W, H], "pin": list(PIN), "opaque_texels": int(m.sum()), "colours": len(cols),
        "colours_outside_palette": sorted(cols - pal),
        "alpha_values": sorted({int(v) for v in np.unique(comp[..., 3])}),
        "alpha_bounds_inclusive": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
        "top_row": int(ys.min()), "sole_row": int(ys.max()), "crown_row_measured": head_top,
        "crown_columns": crown_cols, "crown_to_sole_rows": SOLE_ROW - CROWN_ROW + 1,
        "with_ponytail_rows": int(ys.max() - ys.min() + 1),
        "pin_row_clear": bool(not m[PIN[1]:, :].any()),
        "isolated_single_texels": isolated_texels(comp),
    }


def region_counts(comp):
    """Texel counts per material group (for the QA note: v07 vs v08 areas per material)."""
    groups = {"teal": "QqgG", "steel": "mMZ", "skin": "Ssx", "eye-brow": "E", "hair": "1234h",
              "slate (coat, sleeve, near-leg back edge)": "Cco", "shirt": "Ww", "pale beige (cuff, buckle)": "Pp", "trousers": "Tt", "leather": "LlbB"}
    rgb = comp[..., :3]
    m = comp[..., 3] > 0
    out = {}
    for g, keys in groups.items():
        n = 0
        for k in keys:
            n += int((m & (rgb == np.array(hex_rgb(PALETTE[k]), np.uint8)).all(-1)).sum())
        out[g] = n
    return out


# ===================================================================================================== preview
def on_bg(rgba, bg, zoom):
    im = Image.new("RGBA", (rgba.shape[1], rgba.shape[0]), tuple(bg) + (255,))
    im.alpha_composite(Image.fromarray(rgba, "RGBA"))
    return im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)


def game_scale(rgba, nosprite):
    """The 1280x720 capture as Godot draws it: each texel a 2x2 block at CAPTURE_ORIGIN over the no-sprite frame."""
    im = Image.open(nosprite).convert("RGBA")
    big = Image.fromarray(rgba, "RGBA").resize((W * 2, H * 2), Image.NEAREST)
    im.alpha_composite(big, CAPTURE_ORIGIN)
    return im


def preview(out_dir, nosprites=()):
    """Separate inspection images (one subject each, no sheets), written outside the repo."""
    blobs, comp = render()
    os.makedirs(out_dir, exist_ok=True)
    for tag, bg in (("floor-mid", (88, 84, 80)), ("floor-light", (150, 140, 124)), ("dark", (40, 42, 48))):
        on_bg(comp, bg, 8).save(os.path.join(out_dir, f"v09_x8_{tag}.png"))
    for path in nosprites:
        tag = "ruins" if "ruins" in os.path.basename(path) else "outskirts"
        full = game_scale(comp, path)
        full.save(os.path.join(out_dir, f"v09_game-scale_{tag}.png"))
        full.crop((240, 360, 720, 600)).save(os.path.join(out_dir, f"v09_game-scale-crop-1x_{tag}.png"))
        crop = full.crop((480, 380, 680, 560))
        crop.resize((crop.width * 4, crop.height * 4), Image.NEAREST).save(
            os.path.join(out_dir, f"v09_game-scale-crop-x4_{tag}.png"))
    print(json.dumps({**stats(comp), "material_texels_v09": region_counts(comp), "roll_gap_columns": roll_gap(comp),
                      "scope_vs_v08": scope_report(comp, blobs)}))


# ===================================================================================================== editable files
def make_pxo(png, blobs):
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": n == "guides", "metadata": {}, "name": n,
                   "new_cels_linked": False, "opacity": 1.0, "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": n != "guides"} for n in LAYER_NAMES]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0}
                             for _ in LAYER_NAMES], "duration": 1.0, "metadata": {}}]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": json.dumps("sideview-idle-right-static-unapproved-v09"),
                      "frame_current_tag": "0", "include_tag_in_filename": "false", "interpolation": "0",
                      "lines_count": "1", "new_dir_for_each_frame_tag": "false", "number_of_digits": "4",
                      "number_of_frames": "1", "orientation": "0", "repeat_count": "0", "resize": "100",
                      "save_quality": "0.75", "separator_character": "\"_\"",
                      "sheet_layers_as_separate_files": "false", "split_layers": "false"}
    data = {"author_company": "", "author_contact": "", "author_display_name": "", "author_real_name": "",
            "brushes": [], "color_mode": 5, "current_frame": 0, "current_layer": len(LAYER_NAMES) - 2,
            "export_profile": export_profile, "fps": 6.0, "frames": frames_json, "guides": [],
            "layers": layer_json, "license": "", "metadata": {}, "next_keyframe_id": 0, "palettes": [],
            "pixelorama_version": PIXELORAMA_VERSION, "project_current_palette_name": "", "pxo_version": 7,
            "reference_images": [], "size_x": W, "size_y": H, "symmetry_points": [W - 1.0, H - 1.0], "tags": [],
            "tile_mode_x_basis_x": W, "tile_mode_x_basis_y": 0, "tile_mode_y_basis_x": 0,
            "tile_mode_y_basis_y": H, "tilesets": [], "user_data": "", "vanishing_points": []}
    buf = io.BytesIO()
    dt = (2026, 10, 16, 13, 52, 2)     # fixed (zip needs even seconds) -> byte-identical rebuilds
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        def put(name, payload):
            z.writestr(zipfile.ZipInfo(name, dt), payload, zipfile.ZIP_DEFLATED)
        put("data.json", json.dumps(data, separators=(",", ":")))
        put("mimetype", "application/x-pixelorama")
        put("preview.png", png)
        put("image_data/frames/1/", b"")
        for li, name in enumerate(LAYER_NAMES, start=1):
            put(f"image_data/frames/1/layer_{li}", np.ascontiguousarray(blobs[name]).tobytes())
            put(f"image_data/frames/1/indices_layer_{li}", b"\x00")
    return buf.getvalue()


def make_ora(png, blobs):
    stack = ['<?xml version="1.0" encoding="UTF-8"?>',
             f'<image version="0.0.3" w="{W}" h="{H}" xres="72" yres="72">', "<stack>"]
    for name in reversed(LAYER_NAMES):                      # ORA lists the top layer first
        vis = "hidden" if name == "guides" else "visible"
        stack.append(f'<layer name="{name}" src="data/{name}.png" x="0" y="0" opacity="1.0" '
                     f'visibility="{vis}" composite-op="svg:src-over"/>')
    stack += ["</stack>", "</image>"]
    buf = io.BytesIO()
    dt = (2026, 10, 16, 13, 52, 2)
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", dt), "image/openraster", zipfile.ZIP_STORED)
        z.writestr(zipfile.ZipInfo("stack.xml", dt), "\n".join(stack) + "\n", zipfile.ZIP_DEFLATED)
        for name in LAYER_NAMES:
            z.writestr(zipfile.ZipInfo(f"data/{name}.png", dt), png_bytes(blobs[name]), zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("mergedimage.png", dt), png, zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("Thumbnails/thumbnail.png", dt), png, zipfile.ZIP_DEFLATED)
    return buf.getvalue()


# ===================================================================================================== Pixelorama
def appdata_snapshot():
    root = os.path.join(os.environ.get("APPDATA", ""), "pixelorama")
    snap = {}
    if os.path.isdir(root):
        for d, _, files in os.walk(root):
            for f in files:
                p = os.path.join(d, f)
                rel = os.path.relpath(p, root).replace("\\", "/")
                if rel == ".running":          # an open GUI's 15 s heartbeat; not ours
                    continue
                try:
                    snap[rel] = sha256_bytes(read_bytes(p))
                except OSError:
                    snap[rel] = "unreadable"
    return snap


def pixelorama_export(exe, src, out_dir, split):
    """Headless export with APPDATA redirected to a fresh temp dir (never touches the real config)."""
    env = dict(os.environ)
    env["APPDATA"] = tempfile.mkdtemp(prefix="wb-pxappdata-")
    args = [exe, "--headless", "--quit", "--", "--export"] + (["--split-layers"] if split else []) + \
           ["-o", os.path.join(out_dir, "f.png"), src]
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=240, env=env)
    finally:
        shutil.rmtree(env["APPDATA"], ignore_errors=True)
    files = sorted(f for f in os.listdir(out_dir) if f.lower().endswith(".png"))
    return p.returncode, {f: read_bytes(os.path.join(out_dir, f)) for f in files}


def pixelorama_roundtrips(exe, pxo, ora, blobs, comp):
    snap0 = appdata_snapshot()
    tmp = tempfile.mkdtemp(prefix="wb-fv09-")
    px, flat_png = {}, None
    try:
        for kind, data_ in (("pxo", pxo), ("ora", ora)):
            src = os.path.join(tmp, f"cand.{kind}")
            with open(src, "wb") as f:
                f.write(data_)
            for split in (False, True):
                od = os.path.join(tmp, f"{kind}-{'split' if split else 'flat'}")
                os.makedirs(od)
                rc, outs = pixelorama_export(exe, src, od, split)
                key = f"{kind}_{'split' if split else 'flat'}"
                arrs = {f: decode(b)[2] for f, b in outs.items()}
                if split:
                    want = {n: blobs[n].tobytes() for n in LAYER_NAMES[:-1]}
                    matched = {n for n, b in want.items() if any(o.tobytes() == b for o in arrs.values())}
                    guide_leak = any(o.tobytes() == blobs["guides"].tobytes() for o in arrs.values())
                    px[key] = {"exit": rc, "pngs": len(outs), "visible_layers_matched": len(matched),
                               "visible_layers": len(want), "guides_exported": guide_leak,
                               "pass": rc == 0 and len(matched) == len(want) and not guide_leak
                               and len(outs) == len(want)}
                else:
                    ok = rc == 0 and len(outs) == 1 and next(iter(arrs.values())).tobytes() == comp.tobytes()
                    px[key] = {"exit": rc, "pngs": len(outs), "rgba_equals_tool_render": ok, "pass": ok}
                    if kind == "pxo" and ok:
                        flat_png = next(iter(outs.values()))
                with open(src, "rb") as f:
                    px[key]["input_copy_unchanged"] = f.read() == data_
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    px["real_appdata_pixelorama_untouched_except_heartbeat"] = snap0 == appdata_snapshot()
    return px, flat_png


# ===================================================================================================== build / check
LAYER_NOTES = {
    "far-leg": "far leg angled back (v08 shape): v8 trouser deep (C) with a spruce (T) front edge, dark boot shaft over the paving, mid-leather (b) foot with a lit (B) instep edge in the contact shadow, dark heel and sole band",
    "pack": "tan leather pack on the upper back: plain lit block, shadowed flap edge, one pale-beige buckle, darker base",
    "bedroll": "teal blanket roll seen end-on on the back half of the pack: 7x7 coil, lit outer ring, one dark spiral turn, shadowed base; two transparent columns to the coat/scarf",
    "ponytail": "high ponytail: v07's tall plume up and back from the tie, one clean tapering tail ending above the roll",
    "near-leg": "near leg forward (v08): thigh to a bent knee with leather knee pad, shin in v8 spruce, flat strapped boot; v09 relights only the instep rows 62-65 (b body, B edge) where the boot stands in the contact shadow",
    "coat": "v8 storm-slate coat torso value-grouped: deep back half, thin mid band, lit front plane; belt with a lit top row",
    "coat-skirt": "split coat skirt: deep back tail over the far thigh, one-texel mid band, lit front panel, lit leather hem trim",
    "hip-drape": "v8 teal back-hip fabric: hangs from the belt over the coat's back tail and flares back past it, lit front edge, shadowed back edge, one diagonal fold that opens into a split two-tail hem; clear of the far leg",
    "shirt-lapel": "white shirt under the open coat front, lit slate lapel edge",
    "near-arm": "near arm bent at the elbow: lit slate sleeve over a deep underside, forearm forward across the shirt, pale-beige cuff",
    "sword-blade": "ordinary short sword blade raised forward at 45 degrees: edge light + steel core one texel step per row, tapered tip",
    "sword-guard": "small steel crossguard square to the blade",
    "fist": "light tan glove closed round the grip at chest height, leather grip end under the little finger",
    "head": "hair mass with crown sheen, pulled-back fringe, wide skin plane, brow + 1x2 eye, nose step, mouth, jaw shadow",
    "hair-tie": "leather hair tie knotted on the crown-back",
    "collar": "raised coat collar standing behind the nape (lit slate face, deep inner edge)",
    "scarf-neck": "teal scarf neck wrap, knot and short front tail",
    "collar-front": "front point of the raised coat collar, standing up under the jaw over the scarf's front edge",
    "guides": f"hidden + locked #ff00ff: cell border, ticks on crown row {CROWN_ROW} and sole row {SOLE_ROW}, pin {list(PIN)}",
}


def make_manifest(png, pxo, ora, comp, flat_from_pixelorama):
    st = stats(comp)
    m = {
        "project": SLUG,
        "subject": "female protagonist side-view battle idle, facing right, ONE static frame (native 0.65 on-screen size)",
        "version": VER, "status": "UNAPPROVED test-only candidate", "art_approved": False,
        "runtime_integrated": False, "game_bible_or_acceptance_counters_changed": False, "animation": False,
        "node_scale_intended": 1.0, "display_proportion_equivalent": 0.65,
        "refines": {"files": V08_LOCKS,
                    "hash_algorithm": "sha256-bytes for .png/.pxo/.ora; sha256-text-lf-v1 for the .json manifest",
                    "relationship": "same cell/pin/sole/crown rows, layer stack and palette as v08; only the intended "
                                    "regions below differ; v08 left untouched",
                    "intended_regions": INTENDED_REGIONS,
                    "changed_layers": CHANGED_LAYERS,
                    "scope_vs_v08": scope_report(comp, render()[0])},
        "coat_reference": {"file": V8_SOUTH_REL, "note": "owner-approved v8 south exploration idle; coat/trouser "
                           "ramps copied from it (C1/C2/C3, T1/T2); v8 also shades its trousers with C, the far-leg "
                           "deep used here; its wide teal hip drape and roll are the references for the drape/roll"},
        "codex_audit_addressed": "docs/qa/rpg-2-star-ocean-the-second_protagonist-female_battle-static-v08-codex-"
                                 "visual-audit_unapproved-v01_20261016-145125-5e1b7d6c.md",
        "author_tool": TOOL_REL,
        "png_source": ("Pixelorama 1.2.3 headless flat export of the .pxo (byte-compared to the tool render)"
                       if flat_from_pixelorama else "tool render"),
        "files": {
            "png": {"file": f"{OUT_DIR_REL}/{PNG_NAME}", "sha256": sha256_bytes(png), "hash_algorithm": "sha256-bytes"},
            "pxo": {"file": f"{OUT_DIR_REL}/{PXO_NAME}", "sha256": sha256_bytes(pxo), "hash_algorithm": "sha256-bytes",
                    "format": f"Pixelorama pxo_version 7 ({PIXELORAMA_VERSION}), color_mode 5 (RGBA8), 1 frame x "
                              f"{len(LAYER_NAMES)} layers"},
            "ora": {"file": f"{OUT_DIR_REL}/{ORA_NAME}", "sha256": sha256_bytes(ora), "hash_algorithm": "sha256-bytes"},
        },
        "layers_bottom_to_top": [{"name": n, "note": LAYER_NOTES.get(n, "")} for n in LAYER_NAMES],
        "palette": PALETTE,
        "metrics": {**st, "material_texels": region_counts(comp)},
    }
    return (json.dumps(m, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write_new(path, data):
    if os.path.exists(_fs(path)):
        if read_bytes(path) != data:
            raise SystemExit(f"refusing to overwrite a different existing file: {path}")
        return "unchanged"
    with open(_fs(path), "xb") as f:
        f.write(data)
    return "written"


def build(exe):
    lock = v08_lock()
    if not lock["unchanged"]:
        raise SystemExit(f"v08 changed: {lock}")
    blobs, comp = render()
    st = stats(comp)
    if st["colours_outside_palette"] or st["alpha_values"] != [0, 255] or st["colours"] > 32:
        raise SystemExit(f"palette/alpha gate failed: {st}")
    scope = scope_report(comp, blobs)
    if not scope_ok(scope):
        raise SystemExit(f"scope gate failed (v09 differs from v08 outside the intended regions): {json.dumps(scope)}")
    tool_png = png_bytes(comp)
    pxo, ora = make_pxo(tool_png, blobs), make_ora(tool_png, blobs)
    if make_pxo(tool_png, blobs) != pxo or make_ora(tool_png, blobs) != ora:
        raise SystemExit("editable build is not deterministic")
    px, flat = pixelorama_roundtrips(exe, pxo, ora, blobs, comp)
    if flat is None or not all(v["pass"] for v in px.values() if isinstance(v, dict)):
        raise SystemExit(f"Pixelorama round-trip failed: {json.dumps(px)}")
    png = flat                         # the delivered PNG is Pixelorama's export of the layered .pxo
    out = repo_path(OUT_DIR_REL)
    for name, data in ((PNG_NAME, png), (PXO_NAME, pxo), (ORA_NAME, ora),
                       (MANIFEST_NAME, make_manifest(png, pxo, ora, comp, True))):
        print(write_new(os.path.join(out, name), data), f"{OUT_DIR_REL}/{name}", sha256_bytes(data))
    print(json.dumps({"pixelorama": px}))
    if not v08_lock()["unchanged"]:
        raise SystemExit("v08 changed during build")


def check(exe):
    report = {"status": "UNAPPROVED test-only candidate", "v08_lock_before": v08_lock()}
    blobs, comp = render()
    out = repo_path(OUT_DIR_REL)
    png = read_bytes(os.path.join(out, PNG_NAME))
    pxo = read_bytes(os.path.join(out, PXO_NAME))
    ora = read_bytes(os.path.join(out, ORA_NAME))
    man = json.loads(read_bytes(os.path.join(out, MANIFEST_NAME)))
    mode, size, a = decode(png)
    st = stats(a)
    g = {
        "png_rgba_68x72": mode == "RGBA" and size == (W, H),
        "png_equals_tool_render": a.tobytes() == comp.tobytes(),
        "binary_alpha": st["alpha_values"] == [0, 255],
        "no_off_palette_colour": not st["colours_outside_palette"],
        "colours_le_32": st["colours"] <= 32,
        "sole_on_row_67_same_as_v08": st["sole_row"] == SOLE_ROW,
        "crown_on_row_7_same_as_v08": st["crown_row_measured"] == CROWN_ROW,
        "leftmost_texel_x15_same_as_v08": st["alpha_bounds_inclusive"][0] == 15,
        "nothing_at_or_below_pin_row": st["pin_row_clear"],
        "both_boots_touch_sole_row": bool((a[SOLE_ROW, 20:PIN[0], 3] > 0).any() and (a[SOLE_ROW, PIN[0]:, 3] > 0).any()),
        "transparent_border": bool(not a[0, :, 3].any() and not a[-1, :, 3].any()
                                   and not a[:, 0, 3].any() and not a[:, -1, 3].any()),
        "manifest_hashes_match": (man["files"]["png"]["sha256"] == sha256_bytes(png)
                                  and man["files"]["pxo"]["sha256"] == sha256_bytes(pxo)
                                  and man["files"]["ora"]["sha256"] == sha256_bytes(ora)),
        "manifest_unapproved_flags": (man["art_approved"] is False and man["runtime_integrated"] is False
                                      and man["game_bible_or_acceptance_counters_changed"] is False),
        "rebuild_editables_byte_identical": make_pxo(png_bytes(comp), blobs) == pxo
                                            and make_ora(png_bytes(comp), blobs) == ora,
    }
    with zipfile.ZipFile(io.BytesIO(pxo)) as z:
        data = json.loads(z.read("data.json"))
        names = [l["name"] for l in data["layers"]]
        g["pxo_layers_match"] = names == LAYER_NAMES and all(
            z.read(f"image_data/frames/1/layer_{i + 1}") == blobs[n].tobytes() for i, n in enumerate(names))
        pxo_layers = {n: np.frombuffer(z.read(f"image_data/frames/1/layer_{i + 1}"), np.uint8).reshape(H, W, 4)
                      for i, n in enumerate(names)}
        g["pxo_layer_stack_recomposes_png"] = recompose(pxo_layers).tobytes() == a.tobytes()
        g["pxo_guides_hidden_locked"] = [(l["visible"], l["locked"]) for l in data["layers"]][-1] == (False, True)
    with zipfile.ZipFile(io.BytesIO(ora)) as z:
        g["ora_mimetype_first_stored"] = z.infolist()[0].filename == "mimetype" and z.infolist()[0].compress_type == 0
        ora_layers = {n: decode(z.read(f"data/{n}.png"))[2] for n in LAYER_NAMES}
        g["ora_layers_match"] = all(ora_layers[n].tobytes() == blobs[n].tobytes() for n in LAYER_NAMES)
        g["ora_layer_stack_recomposes_png"] = recompose(ora_layers).tobytes() == a.tobytes()
        g["ora_mergedimage_equals_png"] = decode(z.read("mergedimage.png"))[2].tobytes() == a.tobytes()
    scope = scope_report(a, blobs)
    report["scope_vs_v08"] = scope
    g["palette_same_as_v08"] = scope["palette_same_as_v08"]
    g["layer_order_same_as_v08"] = scope["layer_order_same_as_v08"]
    g["changes_only_in_intended_regions_and_layers"] = scope_ok(scope)
    g["manifest_scope_matches_fresh_scope"] = man["refines"]["scope_vs_v08"] == json.loads(json.dumps(scope))
    gaps = roll_gap(a)
    report["roll_gap_transparent_columns_by_row"] = gaps
    g["roll_scarf_gap_ge_2_transparent_columns"] = all(v is not None and v >= 2 for v in gaps.values())
    if exe:
        px, flat = pixelorama_roundtrips(exe, pxo, ora, blobs, comp)
        report["pixelorama_1_2_3_headless"] = px
        g["pixelorama_roundtrips"] = all(v["pass"] for v in px.values() if isinstance(v, dict)) and \
            px["real_appdata_pixelorama_untouched_except_heartbeat"]
        g["png_equals_fresh_pixelorama_flat_export"] = flat == png
    report["metrics"] = {**st, "material_texels": region_counts(a)}
    report["v08_lock_after"] = v08_lock()
    g["v08_unchanged"] = report["v08_lock_before"]["unchanged"] and report["v08_lock_after"]["unchanged"]
    report["gates"] = g
    report["result"] = "PASS" if all(g.values()) else "FAIL"
    print(json.dumps(report, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    return 0 if report["result"] == "PASS" else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=["preview", "build", "check"])
    ap.add_argument("out", nargs="?")
    ap.add_argument("nosprite", nargs="*", help="preview only: no-sprite party captures (ruins, outskirts)")
    ap.add_argument("--no-pixelorama", action="store_true")
    ap.add_argument("--pixelorama", default=repo_path(PIXELORAMA_REL))
    args = ap.parse_args()
    if args.mode == "preview":
        if not args.out:
            raise SystemExit("preview needs an output dir outside the repo")
        preview(args.out, args.nosprite)
        return 0
    exe = None if args.no_pixelorama else os.path.abspath(args.pixelorama)
    if args.mode == "build":
        if not exe or not os.path.isfile(exe):
            raise SystemExit("build needs Pixelorama (the PNG is its export)")
        build(exe)
        return 0
    if exe and not os.path.isfile(exe):
        raise SystemExit(f"Pixelorama not found: {exe}")
    return check(exe)


if __name__ == "__main__":
    sys.exit(main())
