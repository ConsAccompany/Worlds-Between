"""UNAPPROVED, TEST-ONLY pilot v01: NYC City Hall Park (2537 science hub), ONE 640x360 walkable camera composition.

Deterministic Python tool authored and run by Claude (Claude Code, Opus 5.5, claude.ai Max subscription, firstParty;
no API key, no image model, no paid fallback). Workstream C of the independent art implementation pass.

What it writes: one 640x360 logical-pixel scene (exactly one gameplay camera: game/project.godot viewport 640x360,
window 1280x720, integer 2x) as an 18-layer editable stack -- a native Pixelorama .pxo (pxo_version 7) and an .ora --
plus a palette (.gpl), a collision/walk mask PNG, a walkability JSON and a manifest. `check` adds the Pixelorama 1.2.3
headless export round-trip and two Godot 4.7.2 gates (headless texel gate along a heroine route, and a real windowed
render at 1280x720 of the same slice). Nothing is wired into the game runtime: no scene, script, data, test, default
or camera setting is touched; science scene art acceptance stays 0/11.

AUTHORING ROUTE (disclosed). NOT a Pixelorama GUI paint pass (no desktop/computer-use access to the GUI in this
session). Every landmark, path, lawn, tree, lamp, prop and pin is an explicit hand-written table entry below; the tool
rasterises those tables into named palette-indexed layers. The .pxo opens in the Pixelorama GUI as 18 editable layers
so a GUI polish pass can start from it.

Reference use. The nonruntime concept (outputs/...nyc-city-hall-park_walkable-art-direction-nonruntime-v03_
20261015-221543-c74a12e0.png) and its audit (docs/qa/...walkable-art-direction-visual-audit_unapproved-v03_...md)
were LOOKED AT for geography / path / zone cues only: City Hall + cupola at the north, fountain plaza to the
south-west, central north-south walk, lawn panels with low fences, a statue lawn to the east, Broadway on the west
edge, discreet science fixtures. This tool never opens that image; no continuous-colour pixel and no generated figure
is used. The only character pixels are the approved v8 female south idle frame, used as the 48-logical-px scale and
layering actor.

Composition (top of frame = north). Forced perspective, documented as such:
  * backdrop, rows 0..169 (NOT walkable): north grove band, City Hall (two storeys, portico, end pavilions, roof
    balustrade, cupola with clock and gilded Justice), forecourt with flagpoles, flank trees, the hedge/fence belt and
    the gated forecourt entry with two scanner piers (the science-hub access line).
  * walkable park, rows 172..359, at the approved heroine scale (48 logical px): granite central walk, the fountain
    plaza (radial granite rings, two-tier fountain), NYC hexagonal-paver side walks, the statue circle (bronze patriot
    statue on a granite pedestal), fenced lawns with flower beds, the south plaza; Broadway (maglev tram on a teal
    guideway, glass shelter, crosswalk) on the west edge and the Park Row sidewalk on the east edge (not walkable).
  Selective 2537 technology: tram + guideway, glass tram shelter with a map screen, scanner piers + light line at the
  City Hall gate, sensor rings on the cast-iron lamps, an info pylon, tech bollards, a teal wayfinding inlay. The
  historic fabric (City Hall, fountain, lamps, fences, hex pavers) stays classic.

Modes
  preview <dir>   render layers, flat, runtime stills, 2x views and guides into <dir> (outside the repo)
  build           write candidate files (never overwrites a different file)
  check           static gates + Pixelorama headless round-trip (APPDATA redirected to temp; --no-pixelorama) +
                  Godot gates in throwaway temp projects (--no-godot); --write-report writes the JSON report and the
                  three 1280x720 Godot render captures into outputs/<RUN>/.
Run: python -I -B <this file> preview <tempdir> | build | check [--write-report] [--no-pixelorama] [--no-godot]
"""
import argparse, hashlib, io, json, math, os, shutil, subprocess, sys, tempfile, time, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
AREA = "nyc-city-hall-park"
VER = "unapproved-v01"
STAMP = "20261016-044931"
RUN_ID = "92357bf2"
RUN = f"nyc-chp-v01_{STAMP}-{RUN_ID}"       # short run dir: keeps candidate paths well under MAX_PATH (260)
CAND_REL = f"game/assets/environments/candidates/{RUN}"
OUT_REL = f"outputs/{RUN}"
TOOL_REL = "tools/" + os.path.basename(os.path.abspath(__file__))
AUDIT_REL = ("docs/qa/rpg-2-star-ocean-the-second_nyc-city-hall-park_walkable-art-direction-visual-audit_"
             "unapproved-v03_20261015-221543-c74a12e0.md")
CONCEPT_REL = ("outputs/rpg-2-star-ocean-the-second_nyc-city-hall-park_walkable-art-direction-nonruntime-v03_"
               "20261015-221543-c74a12e0.png")
HEROINE_REL = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_"
               "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
PIXELORAMA_DEFAULT = "C:/Users/hkzha/AppData/Local/Programs/Pixelorama-1.2.3/Pixelorama-Windows-64bit/Pixelorama.exe"
PIXELORAMA_VERSION = "v1.2.3-stable"
GODOT_REL = "work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe"      # gitignored local tooling
W, H = 640, 360                   # one gameplay camera (logical viewport)
VIEW = 2                          # window 1280x720 = integer 2x
WIN_LONG_PREFIX = "\\\\?\\"


def fname(purpose, ext):
    """AGENTS naming: project slug, area, purpose, version, timestamp and run id are all in the file name."""
    return f"{SLUG}_{AREA}_{purpose}_{VER}_{STAMP}-{RUN_ID}.{ext}"


EXPORT_STEM = f"{SLUG}_{AREA}_pixelorama-export_{VER}_{STAMP}-{RUN_ID}"

LAYERS = ["north-groves", "streets", "city-hall", "forecourt-flank", "park-ground", "ground-detail",
          "fountain-basin", "cast-shadows", "props-low", "tree-nw-ysort", "lamps-n-ysort", "trees-ne-ysort",
          "statue-ysort", "fountain-ysort", "lamps-s-ysort", "tree-se-ysort", "fg-occlusion", "guides"]  # bottom->top
ART_LAYERS = LAYERS[:-1]
BASE_LAYERS = LAYERS[:9]                                                  # merged into one base at runtime
YSORT_LAYERS = LAYERS[9:16]

# ============================================================================ palette (all hand-picked)
PALETTE = [
    ("ink", "15171d"),
    ("m0", "3e3d45"), ("m1", "5f5c62"), ("m2", "857f7c"), ("m3", "a8a196"), ("m4", "c7bfb0"), ("m5", "dfd8c8"),
    ("m6", "f2ede0"),
    ("w0", "1f2a36"), ("w1", "334556"), ("w2", "587486"), ("wl", "e6be74"), ("wl2", "f6dfa6"),
    ("r0", "384446"), ("r1", "4d5c5d"), ("r2", "66787a"),
    ("au0", "7e5f27"), ("au1", "bd9238"), ("au2", "ecd07c"),
    ("f0", "14241c"), ("f1", "1f3a27"), ("f2", "2d5530"), ("f3", "437539"), ("f4", "5f9444"), ("f5", "86b558"),
    ("f6", "b0d27a"),
    ("g0", "2a4627"), ("g1", "375c2f"), ("g2", "477437"), ("g3", "5f8d41"), ("g4", "7da650"),
    ("b0", "2a201b"), ("b1", "463427"), ("b2", "67503d"),
    ("p0", "4d4a47"), ("p1", "6c675f"), ("p2", "8b847a"), ("p3", "aaa294"), ("p4", "c6beae"), ("p5", "dcd5c6"),
    ("x0", "3f4045"), ("x1", "55575c"), ("x2", "6c6e71"), ("x3", "848583"),
    ("a0", "25282d"), ("a1", "33373d"), ("a2", "434850"), ("a3", "596068"),
    ("lw", "d6d6cc"),
    ("k0", "1b2128"), ("k1", "2c3540"), ("k2", "435160"), ("k3", "66798a"),
    ("c0", "26566c"), ("c1", "377e98"), ("c2", "63adc2"), ("c3", "aee1e8"),
    ("t0", "186a70"), ("t1", "33b2ae"), ("t2", "8aeedd"),
    ("fl0", "b84a7c"), ("fl1", "e39ab4"), ("fl2", "e6c95a"), ("fl3", "efece0"), ("fl4", "7f66bd"), ("fl5", "d9663f"),
    ("br0", "553026"), ("br1", "774533"),
    ("wd0", "45301f"), ("wd1", "6b482c"), ("wd2", "916740"),
    ("s0", "3b2d23"), ("s1", "574131"),
    ("fr", "a33139"), ("fb", "2b3c6c"), ("fo", "d9782e"),
    ("bz0", "2b2a24"), ("bz1", "4a4a3a"), ("bz2", "5f7b66"), ("bz3", "8fb39a"),
]
GUIDE_PALETTE = [("gd-walk", "3cdcff"), ("gd-block", "ff285a"), ("gd-pin", "ffe600"), ("gd-route", "ff00ff")]
ALL_PAL = PALETTE + GUIDE_PALETTE
I = {n: i for i, (n, _) in enumerate(ALL_PAL)}
RGB = np.array([[int(h[j:j + 2], 16) for j in (0, 2, 4)] for _, h in ALL_PAL], np.uint8)
N_ART = len(PALETTE)

SHADE = {  # opaque cast-shadow colour for each ground colour (no semi-alpha anywhere)
    "g4": "g2", "g3": "g1", "g2": "g1", "g1": "g0", "g0": "f1",
    "p5": "p3", "p4": "p2", "p3": "p2", "p2": "p1", "p1": "p0", "p0": "p0",
    "x3": "x1", "x2": "x1", "x1": "x0", "x0": "a1", "a3": "a1", "a2": "a1", "a1": "a0",
    "f6": "f4", "f5": "f3", "f4": "f3", "f3": "f2", "f2": "f1", "f1": "f0",
    "fl0": "f2", "fl1": "fl0", "fl2": "au0", "fl3": "p3", "fl4": "f2", "fl5": "br1",
    "m6": "m4", "m5": "m3", "m4": "m3", "m3": "m2", "m2": "m1",
    "c3": "c1", "c2": "c1", "c1": "c0", "lw": "p2", "t1": "t0", "t2": "t1", "k3": "k2", "k2": "k1",
    "s1": "s0", "wd2": "wd1", "wd1": "wd0", "au1": "au0", "au2": "au1",
}
SHADE_LUT = np.arange(len(ALL_PAL), dtype=np.int16)
for _a, _b in SHADE.items():
    SHADE_LUT[I[_a]] = I[_b]

# ============================================================================ hand-authored geometry (logical px)
CX = 320                            # City Hall / central walk axis lies between columns 319 and 320 (mirror: 639-x)
# City Hall elevation rows
CUP_TIP = 0
ROOF = (48, 57)
BAL = (58, 63)
CORN = (64, 67)
UP = (68, 95)
STRING = (96, 98)
LOW = (99, 126)
PLINTH = (127, 131)
SECTIONS = [("pav", 150, 197), ("wing", 198, 275), ("center", 276, 363), ("wing", 364, 441), ("pav", 442, 489)]
PORTICO = (282, 357)
COLS = [286, 298, 310, 326, 338, 350]                          # portico column left x (4 px wide), symmetric
LIT_WINDOWS = {("up", 0), ("up", 5), ("low", 3), ("low", 8), ("up", 9), ("low", 12)}   # warm-lit bays (by index)
FLAGS = [(236, "us"), (403, "nyc")]                             # flagpole x, flag
FLAG_BASE, FLAG_TOP = 146, 60
GATE_PIERS = [(284, 291), (348, 355)]                            # x0, x1 (rows 140..169)
HEDGE = (150, 167)
WALK_TOP = 172
# park paths (masks built in park_masks())
AXIS = (292, 347)                                               # granite central walk x range
SOUTH_PLAZA = (44, 639, 338, 359)
FOUNTAIN = (172, 270)                                           # basin centre
PLAZA_R = (92, 58)
BASIN_R = (46, 26)
BASIN_IN = (41, 22)
DIAG = ((226, 240), (298, 200), 12)                             # NE diagonal hex walk: p, q, half width
EAST_CONN = (250, 258, 292, 281)
S_CONN = (150, 300, 193, 338)
W_GATE = (62, 258, 92, 281)
STATUE_WALK = (348, 255, 450, 277)
STATUE_C = (470, 266, 34, 23)
E_WALK_H = (490, 255, 603, 277)
E_WALK_V = (572, 255, 603, 338)
BROADWAY = (0, 41)                                              # road x range; curb 42..43; sidewalk 44..61
BW_FENCE = 62                                                   # fence columns 62..63, gate gap rows 258..281
PARK_ROW = 604                                                  # fence 604..605, sidewalk 606..639
# heroine-scale trees: trunk x, base row, canopy radius
TREES = {"tree-nw-ysort": [(106, 214, 29)], "trees-ne-ysort": [(404, 244, 25), (516, 244, 24)],
         "tree-se-ysort": [(410, 322, 27)]}
LAMPS = {"lamps-n-ysort": [(295, 230), (344, 230)], "lamps-s-ysort": [(295, 312), (344, 312)]}   # on the walk edges
FOUNTAIN_LAMPS = [(106, 272), (238, 272)]
STATUE = (470, 268)
YSORT_PIVOTS = {"tree-nw-ysort": 214, "lamps-n-ysort": 230, "trees-ne-ysort": 244, "statue-ysort": 268,
                "fountain-ysort": 272, "lamps-s-ysort": 312, "tree-se-ysort": 322}
FENCES = [(350, 436, 253), (504, 570, 253), (350, 436, 281), (504, 570, 281),       # (x0, x1, base row)
          (66, 148, 336), (196, 289, 336), (350, 569, 336)]
BEDS = [(190, 190, 30, 8), (106, 318, 30, 8), (246, 316, 24, 8), (460, 222, 26, 8), (522, 306, 32, 9)]
BENCHES = [(372, 252), (90, 336), (420, 336)]                    # left x, base row (benches face south)
BINS = [(342, 256), (196, 336)]
BOLLARDS = [(50, 342), (50, 352)]
PYLON = (214, 230)                                              # info pylon base centre
PINS = {"spawn_south": (320, 350), "city_hall_gate": (320, 178), "axis_mid": (320, 292),
        "fountain_south": (172, 318), "fountain_behind": (172, 236), "info_pylon": (214, 244),
        "statue_plaque": (470, 284), "statue_behind": (470, 250), "tree_se_behind": (410, 274),
        "lamp_n_behind": (300, 222), "lamp_n_front": (300, 238), "fountain_lamp_front": (112, 284),
        "exit_broadway_gate": (70, 270), "exit_park_row": (596, 350)}
YSORT_CASES = [("fountain_behind", "fountain-ysort", True), ("fountain_lamp_front", "fountain-ysort", False),
               ("statue_behind", "statue-ysort", True), ("statue_plaque", "statue-ysort", False),
               ("tree_se_behind", "tree-se-ysort", True), ("lamp_n_behind", "lamps-n-ysort", True),
               ("lamp_n_front", "lamps-n-ysort", False)]
ROUTE = ["spawn_south", (320, 300), (320, 270), (262, 270), (232, 244), "fountain_behind", (130, 236), (112, 250),
         "exit_broadway_gate", (112, 292), "fountain_south", (172, 348), (320, 348), "axis_mid", (320, 266),
         (440, 266), "statue_behind", (500, 266), (588, 266), (588, 348), "exit_park_row", (420, 348),
         (320, 348), "lamp_n_front", (314, 238), (314, 222), "lamp_n_behind", "city_hall_gate"]
CAPTURES = {"axis": "axis_mid", "behind-fountain": "fountain_behind", "behind-tree": "tree_se_behind"}

# ============================================================================ helpers
YY, XX = np.mgrid[0:H, 0:W]


def _fs(path):
    path = os.path.abspath(path)
    if os.name == "nt" and len(path) > 247 and not path.startswith(WIN_LONG_PREFIX):
        return WIN_LONG_PREFIX + path
    return path


def rp(rel):
    return os.path.join(REPO, *rel.split("/"))


def read_bytes(p):
    with open(_fs(p), "rb") as f:
        return f.read()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_text(b):
    return hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()


def new():
    return np.full((H, W), -1, np.int16)


def hval(*key):
    """Deterministic hash in [0, 1) (texture variation only: slab tones, leaf jitter; never placement)."""
    return int.from_bytes(hashlib.sha256(repr(key).encode()).digest()[:4], "little") / 2 ** 32


_VN = {}


def vnoise(key, cell):
    """Smooth value noise (smoothstep-bilinear between hashed lattice values every `cell` px)."""
    if (key, cell) not in _VN:
        gw, gh = W // cell + 2, H // cell + 2
        g = np.array([[hval(key, "vn", i, j) for i in range(gw)] for j in range(gh)], np.float32)
        fx, fy = XX / cell, YY / cell
        ix, iy = fx.astype(np.int32), fy.astype(np.int32)
        tx, ty = fx - ix, fy - iy
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        top = g[iy, ix] * (1 - tx) + g[iy, ix + 1] * tx
        bot = g[iy + 1, ix] * (1 - tx) + g[iy + 1, ix + 1] * tx
        _VN[(key, cell)] = (top * (1 - ty) + bot * ty).astype(np.float32)
    return _VN[(key, cell)]


def C(c):
    return I[c] if isinstance(c, str) else c


def rect(L, x0, y0, x1, y1, c, reg=None):
    x0, x1 = max(0, x0), min(W - 1, x1)
    y0, y1 = max(0, y0), min(H - 1, y1)
    if x0 <= x1 and y0 <= y1:
        L[y0:y1 + 1, x0:x1 + 1] = C(c)
        if reg is not None:
            reg[y0:y1 + 1, x0:x1 + 1] = True


def px(L, x, y, c, reg=None):
    if 0 <= x < W and 0 <= y < H:
        L[y, x] = C(c)
        if reg is not None:
            reg[y, x] = True


def stamp(L, x, y, rows, cmap, reg=None):
    """Paint a hand-authored sprite (top-left at x, y). '.' is transparent; other chars map through cmap."""
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in ". ":
                continue
            px(L, x + i, y + j, cmap[ch], reg)


def ell(cx, cy, rx, ry):
    return ((XX + 0.5 - cx) / rx) ** 2 + ((YY + 0.5 - cy) / ry) ** 2 <= 1.0


def box(x0, y0, x1, y1):
    return (XX >= x0) & (XX <= x1) & (YY >= y0) & (YY <= y1)


def seg(p, q, hw):
    (x0, y0), (x1, y1) = p, q
    dx, dy = x1 - x0, y1 - y0
    t = np.clip(((XX + 0.5 - x0) * dx + (YY + 0.5 - y0) * dy) / float(dx * dx + dy * dy), 0, 1)
    return np.hypot(XX + 0.5 - (x0 + t * dx), YY + 0.5 - (y0 + t * dy)) <= hw


def shift_of(names, c, d):
    i = names.index(c)
    return names[max(0, min(len(names) - 1, i + d))]


def dilate(m, r=1):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


def edge_below(m):
    """True where m and the texel below is not m (bottom edges)."""
    b = np.zeros_like(m)
    b[:-1] = m[:-1] & ~m[1:]
    return b


def edge_above(m):
    a = np.zeros_like(m)
    a[1:] = m[1:] & ~m[:-1]
    return a


def cyl(u):
    """Light across a vertical cylinder (u in -1..1), sun from the front-left (south-west)."""
    u = max(-1.0, min(1.0, u))
    return 0.55 * math.sqrt(max(0.0, 1 - u * u)) - 0.45 * u + 0.05


def tone(ramp, v, cuts):
    k = 0
    while k < len(cuts) and v >= cuts[k]:
        k += 1
    return ramp[k]


# ============================================================================ foliage (leaf-cluster crowns)
LIGHT = np.array([-0.55, -0.62, 0.56])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
LOBES = [(0.0, -0.52, 0.50), (-0.48, -0.30, 0.46), (0.48, -0.28, 0.46), (-0.66, 0.16, 0.40), (0.64, 0.18, 0.40),
         (-0.24, -0.02, 0.52), (0.26, 0.00, 0.52), (-0.36, 0.46, 0.42), (0.36, 0.46, 0.42), (0.0, 0.58, 0.40)]
TREE_RAMP = ["f0", "f1", "f2", "f3", "f4", "f5", "f6"]
TREE_CUTS = (-0.42, -0.12, 0.14, 0.38, 0.62, 0.86)
BACK_RAMP = ["f0", "f1", "f2", "f3", "f4"]
BACK_CUTS = (-0.30, 0.02, 0.34, 0.66)


def crown(L, cx, cy, r, key, ramp=TREE_RAMP, cuts=TREE_CUTS, reg=None, squash=0.86, gain=1.0):
    """Leaf-cluster canopy: hand-ordered lobes (back to front), each lit as a sphere from the south-west, value
    noise at 3 px makes leaf clumps, lower-right lobe rims separate the clusters, dark outline on the shade side."""
    lobes = []
    drop = {int(hval(key, "drop", q) * len(LOBES)) for q in range(2)} - {0, 5, 6}   # per-tree silhouette variety
    for k, (ox, oy, s) in enumerate(LOBES):
        if k in drop:
            continue
        jx, jy = (hval(key, k, "x") - 0.5) * 0.16, (hval(key, k, "y") - 0.5) * 0.16
        js = 1 + (hval(key, k, "s") - 0.5) * 0.18
        lobes.append((cx + (ox + jx) * r, cy + (oy + jy) * r * squash, s * js * r * 0.66))
    lobes.sort(key=lambda t: t[1])
    x0, x1 = int(cx - 1.25 * r), int(cx + 1.25 * r) + 1
    y0, y1 = int(cy - 1.15 * r * squash), int(cy + 1.15 * r * squash) + 1
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x0 >= x1 or y0 >= y1:
        return np.zeros((H, W), bool)
    X, Y = XX[y0:y1, x0:x1] + 0.5, YY[y0:y1, x0:x1] + 0.5
    nz_field = vnoise("leaf", 3)[y0:y1, x0:x1]
    fine = vnoise("leaf-fine", 2)[y0:y1, x0:x1]
    sub = np.full(X.shape, -1, np.int16)
    union = np.zeros(X.shape, bool)
    for (lx, ly, lr) in lobes:
        nx, ny = (X - lx) / lr, (Y - ly) / (lr * squash)
        d2 = nx * nx + ny * ny
        m = d2 <= 1.0
        if not m.any():
            continue
        nzv = np.sqrt(np.clip(1 - d2, 0, 1))
        inten = nx * LIGHT[0] + ny * LIGHT[1] + nzv * LIGHT[2]
        glob = -0.30 * ((lx - cx) / r) - 0.42 * ((ly - cy) / r)
        v = (inten * 0.78 + glob * 0.55 + (nz_field - 0.5) * 0.55 + (fine - 0.5) * 0.18) * gain
        rim = m & (d2 > 0.72) & ((nx * 0.55 + ny * 0.85) > 0.30)
        idx = np.zeros(X.shape, np.int16)
        for ki in range(len(ramp)):
            lo = -9 if ki == 0 else cuts[ki - 1]
            hi = 9 if ki == len(ramp) - 1 else cuts[ki]
            idx[(v >= lo) & (v < hi)] = I[ramp[ki]]
        rim_idx = np.array([I[ramp[max(0, ramp.index(n) - 1)]] for n in ramp], np.int16)
        lut = {I[n]: rim_idx[i] for i, n in enumerate(ramp)}
        for a, b in lut.items():
            idx[rim & (idx == a)] = b
        sub[m] = idx[m]
        union |= m
    # outline on the shade side (bottom and right edges of the union)
    edge = np.zeros_like(union)
    edge[:-1] |= union[:-1] & ~union[1:]
    edge[:, :-1] |= union[:, :-1] & ~union[:, 1:]
    sub[edge] = I[ramp[0]]
    # dark leaf pockets in the lower half (crowns read as clumps, not balls)
    pocket = union & (nz_field < 0.16) & (Y > cy + 0.15 * r)
    sub[pocket] = I[ramp[0]]
    tgt = L[y0:y1, x0:x1]
    tgt[union] = sub[union]
    full = np.zeros((H, W), bool)
    full[y0:y1, x0:x1] = union
    if reg is not None:
        reg |= full
    return full


def trunk(L, x, base, top, w=6, reg=None):
    """Bark column, lit from the left, with a root flare and two branch forks into the crown."""
    for y in range(top, base + 1):
        flare = 1 if y >= base - 2 else 0
        for i in range(-flare, w + flare):
            xx = x - w // 2 + i
            u = (i + 0.5) / w
            c = "b2" if u < 0.34 else ("b1" if u < 0.8 else "b0")
            if hval("bark", xx, y // 3) < 0.12 and 0.2 < u < 0.8:
                c = "b0"
            px(L, xx, y, c, reg)
    for dx in (-1, 1):                       # forks
        for k in range(6):
            px(L, x + dx * (2 + k // 2) - (1 if dx < 0 else 0), top - k, "b1", reg)


# ============================================================================ layer painters
GROVE_BAND = [  # backdrop crowns behind City Hall (x, y, r), hand placed back row first; the pale cupola
    # silhouette reads against the dark canopy. Second row overlaps the roof line at the flanks only.
    (34, -6, 24), (92, -4, 22), (150, -8, 24), (206, -2, 22), (262, -6, 22), (376, -6, 22), (432, -2, 22),
    (488, -8, 24), (546, -4, 22), (604, -6, 24),
    (8, 20, 22), (66, 18, 24), (124, 22, 22), (182, 16, 24), (238, 22, 22), (286, 14, 16), (354, 14, 16),
    (400, 22, 22), (456, 16, 24), (514, 22, 22), (572, 18, 24), (630, 22, 20),
    (40, 46, 20), (98, 48, 18), (544, 48, 18), (600, 46, 20), (176, 40, 18), (464, 40, 18),
]


def paint_north_groves():
    L = new()
    L[:, :] = I["g1"]                                    # opaque base under everything
    g = vnoise("grove-under", 4)
    under = YY < 170
    L[under] = I["f1"]
    L[under & (g < 0.36)] = I["f0"]
    L[under & (g > 0.74)] = I["f2"]
    for i, (x, y, r) in enumerate(GROVE_BAND):
        crown(L, x, y, r, ("band", i), BACK_RAMP, BACK_CUTS, gain=0.85)
    return L


def paint_streets():
    L = new()
    road = box(BROADWAY[0], 0, BROADWAY[1], H - 1)
    L[road] = I["a1"]
    n = vnoise("asphalt", 2)
    L[road & (n < 0.22)] = I["a0"]
    L[road & (n > 0.80)] = I["a2"]
    # maglev guideway (2537): concrete slab, two grooves, teal centre strip
    gw = box(8, 0, 32, H - 1)
    L[gw] = I["a2"]
    L[gw & (vnoise("guideway", 3) > 0.74)] = I["a3"]
    rect(L, 8, 0, 8, H - 1, "a3"); rect(L, 32, 0, 32, H - 1, "a0")
    rect(L, 12, 0, 12, H - 1, "a0"); rect(L, 28, 0, 28, H - 1, "a0")
    rect(L, 19, 0, 20, H - 1, "t0")
    for y in range(4, H, 12):
        rect(L, 19, y, 20, y + 3, "t1")
    rect(L, 36, 0, 37, H - 1, "a1")
    for y in range(6, 330, 22):                          # lane dashes (one-way southbound lane)
        rect(L, 37, y, 37, y + 9, "lw")
    for x in range(2, 41, 8):                            # crosswalk at the south plaza
        rect(L, x, 341, x + 3, 357, "lw")
    rect(L, 42, 0, 42, H - 1, "p4"); rect(L, 43, 0, 43, H - 1, "p2")
    sw = box(44, 0, 61, H - 1)
    L[sw] = I["p3"]
    for y in range(5, H, 14):
        rect(L, 44, y, 61, y, "p2")
    rect(L, 53, 0, 53, H - 1, "p2")
    L[sw & (vnoise("sidewalk", 3) < 0.12)] = I["p2"]
    # Park Row sidewalk (east)
    pr = box(606, 0, W - 1, H - 1)
    L[pr] = I["p3"]
    for y in range(9, H, 14):
        rect(L, 606, y, W - 1, y, "p2")
    rect(L, 622, 0, 622, H - 1, "p2")
    L[pr & (vnoise("sidewalk-e", 3) < 0.12)] = I["p2"]
    # tall park fences (Broadway side with gate gap, Park Row side): pickets every 3 px, lit tops
    for x0 in (BW_FENCE, PARK_ROW):
        for y in range(0, 338):
            if x0 == BW_FENCE and 256 <= y <= 283:
                continue
            px(L, x0, y, "k1"); px(L, x0 + 1, y, "k0")
            if y % 4 in (0, 1):
                px(L, x0, y, "k2")
    for (y0, y1) in ((250, 257), (282, 289)):             # Broadway gate piers (registered as items)
        rect(L, 60, y0, 65, y1, "m3"); rect(L, 60, y0, 61, y1, "m4"); rect(L, 65, y0, 65, y1, "m2")
        rect(L, 59, y0, 66, y0 + 1, "m5")
    # tram (maglev) on the guideway, seen from above with its south end face
    tr = box(7, 22, 33, 118)
    L[tr] = I["m4"]
    rect(L, 7, 22, 7, 118, "m5"); rect(L, 33, 22, 33, 118, "k2"); rect(L, 32, 22, 32, 118, "m3")
    rect(L, 7, 22, 33, 23, "m5")
    for (a, b) in ((38, 48), (90, 100)):                 # roof equipment pods
        rect(L, 12, a, 28, b, "k2"); rect(L, 12, a, 28, a, "k3"); rect(L, 12, b, 28, b, "k1")
        rect(L, 13, a + 2, 27, b - 2, "m2")
    for y in range(26, 116, 6):                          # teal roof light strip
        rect(L, 19, y, 20, y + 3, "t1")
    rect(L, 19, 52, 20, 86, "t0")
    for y in (60, 70, 80):
        rect(L, 19, y, 20, y + 1, "t2")
    rect(L, 7, 119, 33, 130, "k1")                       # south end face
    rect(L, 9, 120, 31, 124, "w1"); rect(L, 9, 120, 15, 121, "w2")
    rect(L, 8, 126, 10, 127, "t2"); rect(L, 30, 126, 32, 127, "t2")
    rect(L, 12, 126, 28, 127, "k2"); rect(L, 7, 130, 33, 130, "k0")
    rect(L, 34, 24, 36, 130, "a0")                       # cast shadow to the north-east side
    # glass tram shelter on the Broadway sidewalk (roof seen from above, posts, map screen)
    rect(L, 39, 182, 61, 190, "k1")
    rect(L, 40, 183, 60, 189, "c3")
    rect(L, 40, 186, 60, 189, "w2")
    for x in range(44, 60, 5):
        rect(L, x, 183, x, 189, "k2")
    rect(L, 40, 183, 46, 184, "lw")
    rect(L, 44, 191, 45, 214, "k1"); rect(L, 58, 191, 59, 214, "k1")
    rect(L, 46, 192, 57, 205, "w2")
    rect(L, 49, 194, 54, 201, "t0"); rect(L, 50, 195, 53, 197, "t1"); rect(L, 50, 199, 51, 200, "t2")
    rect(L, 46, 207, 57, 208, "k2"); rect(L, 46, 209, 57, 209, "k0")
    # NYC subway stair entrance on the Park Row sidewalk: descending stair, iron railing, green globe lamps
    for y in range(194, 227):
        depth = (226 - y) // 8
        rect(L, 612, y, 630, y, ("a3", "a2", "a1", "a0", "a0")[depth])
        if (226 - y) % 3 == 0:
            rect(L, 612, y, 630, y, ("p3", "a3", "a2", "a1", "a1")[depth])
    for xr in (610, 631):
        rect(L, xr, 192, xr + 1, 226, "k1"); rect(L, xr, 192, xr, 226, "k2")
        rect(L, xr - 1 if xr == 610 else xr + 2, 192, xr - 1 if xr == 610 else xr + 2, 227, "p4")
    rect(L, 610, 192, 632, 193, "k1"); rect(L, 610, 192, 632, 192, "k2"); rect(L, 609, 191, 633, 191, "p4")
    for y in range(196, 226, 6):
        rect(L, 610, y, 611, y + 1, "k0"); rect(L, 631, y, 632, y + 1, "k0")
    for gx in (611, 631):
        rect(L, gx, 206, gx, 226, "k1"); rect(L, gx - 1, 225, gx + 1, 226, "k0")
        rect(L, gx - 2, 199, gx + 2, 204, "f4"); rect(L, gx - 2, 199, gx - 1, 200, "f6")
        rect(L, gx + 1, 202, gx + 2, 204, "f3"); rect(L, gx - 1, 198, gx + 1, 198, "k1")
        rect(L, gx - 1, 205, gx + 1, 205, "k1")
    # classic lamp on the Park Row sidewalk (never reachable by the heroine)
    lamp_sprite(L, 624, 300)
    return L


def facade_window(L, x, top, h, arched, lit, front):
    glass, mull, refl = ("wl", "au0", "wl2") if lit else ("w0", "w1", "w2")
    frame_l, frame_r = ("m6", "m3") if front else ("m5", "m2")
    rect(L, x - 1, top - 1, x + 6, top + h, frame_l)
    rect(L, x + 6, top - 1, x + 6, top + h, frame_r)
    rect(L, x, top, x + 5, top + h - 1, glass)
    if arched:
        px(L, x - 1, top - 1, "m4" if front else "m3")
        px(L, x + 6, top - 1, "m4" if front else "m3")
        px(L, x, top, frame_l); px(L, x + 5, top, frame_l)
        rect(L, x + 2, top - 3, x + 3, top - 2, "m6" if front else "m5")       # keystone
    rect(L, x, top + h // 2, x + 5, top + h // 2, mull)
    rect(L, x + 2, top + 1, x + 2, top + h - 1, mull)
    rect(L, x, top + 1 if arched else top, x + 1, top + 2, refl)
    rect(L, x - 2, top + h + 1, x + 7, top + h + 1, "m6" if front else "m5")    # sill
    rect(L, x - 1, top + h + 2, x + 6, top + h + 2, "m2")


def paint_city_hall():
    L = new()
    # roof (seen from above behind the balustrade), hipped ends, chimneys, two discreet skylights
    for y in range(ROOF[0], ROOF[1] + 1):
        inset = max(0, ROOF[0] + 6 - y)
        rect(L, 152 + inset, y, 487 - inset, y, "r1" if (y - ROOF[0]) % 3 else "r0")
    for x in range(152, 488, 7):
        rect(L, x, ROOF[0] + 2, x, ROOF[1], "r0")
    rect(L, 152, ROOF[1], 487, ROOF[1], "r2")
    for cx0 in (196, 440):
        rect(L, cx0, 42, cx0 + 4, 51, "m2"); rect(L, cx0, 42, cx0 + 1, 51, "m3"); rect(L, cx0 - 1, 41, cx0 + 5, 42, "m4")
    for sx in (214, 410):
        rect(L, sx, 51, sx + 15, 55, "k1"); rect(L, sx + 1, 52, sx + 14, 54, "c3"); rect(L, sx + 8, 52, sx + 14, 54, "w2")
    # walls: back planes (wings / centre) m3-ish, front planes (pavilions / portico) m4-ish
    for kind, x0, x1 in SECTIONS:
        front = kind == "pav"
        wall = "m4" if front else "m3"
        rect(L, x0, CORN[1], x1, PLINTH[0] - 1, wall)
        # ground-floor rustication joints
        for y in range(LOW[0] + 3, LOW[1], 4):
            rect(L, x0, y, x1, y, "m3" if front else "m2")
        # plinth
        rect(L, x0, PLINTH[0], x1, PLINTH[1] + (3 if front else 0), "m2")
        rect(L, x0, PLINTH[0], x1, PLINTH[0], "m4" if front else "m3")
    # pavilion pilasters
    for kind, x0, x1 in SECTIONS:
        if kind != "pav":
            continue
        for pxx in (x0 + 1, x0 + 22, x0 + 44):
            rect(L, pxx, UP[0], pxx + 2, LOW[1], "m5"); rect(L, pxx + 2, UP[0], pxx + 2, LOW[1], "m3")
            rect(L, pxx - 1, UP[0], pxx + 3, UP[0] + 1, "m6")          # capitals
            rect(L, pxx - 1, LOW[0], pxx + 3, LOW[0] + 1, "m5")
    # windows: bays per section, symmetric about the axis
    bays = []
    lx = SECTIONS[0][1]
    bays += [lx + 10, lx + 32]                                         # left pavilion
    wx = SECTIONS[1][1]
    bays += [wx + 7, wx + 26, wx + 46, wx + 65]                        # left wing
    bays += [639 - b - 5 for b in reversed(bays)]                       # mirror (window is 6 wide)
    for i, bx in enumerate(bays):
        front = bx < 198 or bx > 441
        facade_window(L, bx, 74, 15, True, ("up", i) in LIT_WINDOWS, front)
        facade_window(L, bx, 104, 13, False, ("low", i) in LIT_WINDOWS, front)
        rect(L, bx - 2, 101, bx + 7, 101, "m6" if front else "m5")      # lower hood
        rect(L, bx - 1, 102, bx + 6, 102, "m2")
    # entablature bands (continuous)
    rect(L, 150, STRING[0], 489, STRING[0], "m5"); rect(L, 150, STRING[0] + 1, 489, STRING[0] + 1, "m4")
    rect(L, 150, STRING[1], 489, STRING[1], "m2")
    rect(L, 150, CORN[0], 489, CORN[0], "m6"); rect(L, 150, CORN[0] + 1, 489, CORN[0] + 1, "m4")
    rect(L, 150, CORN[0] + 2, 489, CORN[0] + 2, "m1")
    for x in range(150, 490):
        px(L, x, CORN[1], "m4" if x % 2 == 0 else "m2")                 # dentils
    # cast shadows on the back walls right of each front plane (sun from the south-west)
    for x0 in (198, 358):
        for x in range(x0, x0 + 3):
            for y in range(CORN[0] + 3, PLINTH[1] + 1):
                if L[y, x] == I["m3"]:
                    L[y, x] = I["m2"]
                elif L[y, x] == I["m4"]:
                    L[y, x] = I["m3"]
    # portico: dark loggia, openings, two-tier colonnade, banners, steps
    rect(L, PORTICO[0], UP[0], PORTICO[1], LOW[1], "m1")
    for y in range(UP[0], LOW[1] + 1, 5):
        rect(L, PORTICO[0], y, PORTICO[1], y, "m0")
    gaps = [(290, 297), (302, 309), (314, 325), (330, 337), (342, 349)]
    for (a, b) in gaps:
        c = (a + b) // 2
        if a == 314:
            rect(L, 316, 104, 323, LOW[1], "wl"); rect(L, 317, 102, 322, 103, "wl")
            rect(L, 316, 104, 317, LOW[1], "wl2"); rect(L, 319, 104, 320, LOW[1], "au0")
            rect(L, 316, 74, 323, 89, "w0"); rect(L, 317, 72, 322, 73, "w0"); rect(L, 316, 75, 317, 77, "w2")
        else:
            rect(L, c - 2, 106, c + 2, 119, "w0"); rect(L, c - 2, 106, c - 1, 108, "w2")
            rect(L, c - 2, 76, c + 2, 89, "w0"); rect(L, c - 1, 75, c + 1, 75, "w0"); rect(L, c - 2, 77, c - 1, 79, "w2")
    for x in COLS:
        for (y0, y1) in ((UP[0] + 2, UP[1] - 2), (LOW[0] + 2, LOW[1] - 2)):
            for i, c in enumerate(("m5", "m6", "m4", "m2")):
                rect(L, x + i, y0, x + i, y1, c)
            rect(L, x + 1, y0, x + 1, y1, "m6")
        rect(L, x - 1, UP[0], x + 4, UP[0], "m6"); rect(L, x - 1, UP[0] + 1, x + 4, UP[0] + 1, "m4")   # capitals
        for i in range(-1, 5, 2):
            px(L, x + i, UP[0] + 1, "m3")
        rect(L, x - 1, LOW[0], x + 4, LOW[0], "m6"); rect(L, x - 1, LOW[0] + 1, x + 4, LOW[0] + 1, "m3")
        px(L, x - 1, LOW[0] + 1, "m5"); px(L, x + 4, LOW[0] + 1, "m2")
        for (b0, b1) in ((UP[1] - 1, UP[1]), (LOW[1] - 1, LOW[1])):                                   # bases
            rect(L, x - 1, b0, x + 4, b1, "m4"); rect(L, x - 1, b1, x + 4, b1, "m2")
    for bx in (291, 343):                                                 # science-hub banners (green, gold, teal)
        rect(L, bx, 71, bx + 5, 91, "f2"); rect(L, bx, 71, bx + 1, 91, "f3"); rect(L, bx - 1, 70, bx + 6, 70, "au1")
        rect(L, bx + 2, 78, bx + 3, 79, "t1"); px(L, bx + 2, 78, "t2")
        rect(L, bx + 1, 81, bx + 4, 81, "au1")
        for i in range(0, 6, 2):
            px(L, bx + i, 92, "au1")
    rect(L, PORTICO[0] - 1, UP[0], PORTICO[0] - 1, PLINTH[1], "m5")    # portico edges
    rect(L, PORTICO[1] + 1, UP[0], PORTICO[1] + 1, PLINTH[1], "m1")
    rect(L, PORTICO[0] - 1, PLINTH[0], PORTICO[1] + 1, PLINTH[1] + 3, "m2")
    rect(L, PORTICO[0] - 1, PLINTH[0], PORTICO[1] + 1, PLINTH[0], "m4")
    for k in range(7):                                                    # grand stair, splaying toward the viewer
        y = PLINTH[1] + 4 + 2 * k
        rect(L, 280 - k, y, 359 + k, y, "m5"); rect(L, 280 - k, y + 1, 359 + k, y + 1, "m3")
        px(L, 280 - k, y, "m4"); px(L, 359 + k, y + 1, "m2")
    for (a, b, lit) in ((272, 279, True), (360, 367, False)):          # stair cheek blocks
        rect(L, a, 134, b, 149, "m4" if lit else "m3"); rect(L, a, 134, b, 135, "m6" if lit else "m5")
        rect(L, a, 149, b, 149, "m2")
    # balustrade over everything
    rect(L, 150, BAL[0], 489, BAL[0], "m6"); rect(L, 150, BAL[0] + 1, 489, BAL[0] + 1, "m3")
    for x in range(150, 490):
        c = ("m5", "m3", "m0")[x % 3]
        rect(L, x, BAL[0] + 2, x, BAL[1] - 1, c)
    for x0 in list(range(150, 320, 24)) + [639 - x - 3 for x in range(150, 320, 24)]:
        rect(L, x0, BAL[0] - 1, x0 + 3, BAL[1], "m4"); rect(L, x0, BAL[0] - 1, x0 + 3, BAL[0] - 1, "m6")
        rect(L, x0 + 3, BAL[0], x0 + 3, BAL[1], "m2")
    rect(L, 150, BAL[1], 489, BAL[1], "m4")
    paint_cupola(L)
    return L


def paint_cupola(L):
    c = 319.5
    # square base stage on the roof
    rect(L, 300, 38, 339, 57, "m4"); rect(L, 300, 38, 302, 57, "m5"); rect(L, 337, 38, 339, 57, "m2")
    rect(L, 298, 36, 341, 36, "m6"); rect(L, 298, 37, 341, 37, "m3"); rect(L, 300, 38, 339, 38, "m2")
    rect(L, 314, 43, 325, 56, "m1"); rect(L, 315, 42, 324, 42, "m1"); rect(L, 317, 41, 322, 41, "m1")
    for y in range(44, 56, 2):
        rect(L, 315, y, 324, y, "m2")
    rect(L, 313, 41, 313, 56, "m5"); rect(L, 326, 41, 326, 56, "m3")
    for wx in (305, 331):                                               # oculi
        rect(L, wx, 46, wx + 2, 48, "w0"); px(L, wx, 46, "w2")
    # clock drum (cylinder shading per column, recessed bays between six columns)
    for x in range(306, 334):
        u = (x + 0.5 - c) / 14
        v = cyl(u)
        col = tone(["m1", "m2", "m3", "m4", "m5", "m6"], v, (0.05, 0.22, 0.38, 0.52, 0.66))
        rect(L, x, 24, x, 35, col)
        if int(round((x + 0.5 - c) / 4.6)) % 2 == 0 and abs(u) < 0.95 and abs(x + 0.5 - c) > 6:
            rect(L, x, 26, x, 34, shift_of(["m0", "m1", "m2", "m3", "m4", "m5", "m6"], col, -2))
    for y in range(25, 35):                                             # clock face
        for x in range(314, 326):
            d = math.hypot(x + 0.5 - c, (y + 0.5 - 29.5) * 1.05)
            if d <= 4.6:
                px(L, x, y, "m6")
            elif d <= 5.6:
                px(L, x, y, "au1" if x < c else "au0")
    rect(L, 319, 26, 320, 29, "k0"); rect(L, 320, 29, 322, 30, "k0")
    rect(L, 304, 22, 335, 22, "m6"); rect(L, 304, 23, 335, 23, "m2")
    # dome (pale, ribbed), lantern, gilded Justice
    for y in range(11, 22):
        t = (21.5 - y) / 11.0
        hw = 13.5 * math.sqrt(max(0.0, 1 - t * t))
        for x in range(int(c - hw), int(c + hw) + 1):
            u = (x + 0.5 - c) / max(hw, 1)
            v = cyl(u) + 0.12 * (1 - t)
            col = tone(["m1", "m2", "m3", "m4", "m5", "m6"], v, (0.02, 0.2, 0.36, 0.5, 0.64))
            if abs(x + 0.5 - c) > 1 and int(x + 0.5 - c) % 4 == 0:
                col = shift_of(["m1", "m2", "m3", "m4", "m5", "m6"], col, -1)
            px(L, x, y, col)
    rect(L, 316, 6, 323, 10, "m4"); rect(L, 316, 6, 317, 10, "m5"); rect(L, 322, 6, 323, 10, "m2")
    rect(L, 319, 7, 320, 9, "m0"); rect(L, 315, 5, 324, 5, "m5")
    stamp(L, 317, 0, ["..A..", ".BAa.", "..Aa.", ".aAa.", "aaAAa"], {"A": "au2", "a": "au1", "B": "au0"})
    # shade-side outline so the pale cupola reads against the dark grove
    for y in range(0, 58):
        row = np.nonzero((L[y, 296:344] >= 0) & np.isin(L[y, 296:344], [I[n] for n in
                                                                          ("m3", "m4", "m5", "m6", "m2", "m1")]))[0]
        if len(row) and y < 48:
            px(L, 296 + row.max() + 1, y, "m0")


def lamp_sprite(L, x, base, reg=None):
    """Cast-iron park lamp (about 3.3 m at the heroine scale) with a 2537 teal sensor ring under the lantern."""
    rect(L, x - 2, base - 5, x + 2, base, "k1", reg); rect(L, x - 2, base - 5, x - 2, base, "k3", reg)
    rect(L, x - 3, base, x + 3, base, "k0", reg); rect(L, x - 2, base - 6, x + 2, base - 6, "k2", reg)
    rect(L, x - 1, base - 50, x, base - 7, "k2", reg); rect(L, x, base - 50, x, base - 7, "k0", reg)
    px(L, x - 1, base - 40, "k3", reg); px(L, x - 1, base - 20, "k3", reg)
    rect(L, x - 2, base - 30, x + 1, base - 29, "k3", reg); rect(L, x + 1, base - 30, x + 1, base - 29, "k1", reg)
    rect(L, x - 2, base - 52, x + 1, base - 51, "t1", reg); rect(L, x - 2, base - 52, x - 1, base - 52, "t2", reg)
    rect(L, x - 3, base - 54, x + 2, base - 53, "k1", reg)
    rect(L, x - 3, base - 62, x + 2, base - 55, "k1", reg)
    rect(L, x - 2, base - 61, x + 1, base - 56, "wl", reg); rect(L, x - 2, base - 61, x - 1, base - 59, "wl2", reg)
    rect(L, x - 4, base - 63, x + 3, base - 63, "k2", reg); rect(L, x - 2, base - 64, x + 1, base - 64, "k1", reg)
    px(L, x - 1, base - 65, "k1", reg); px(L, x - 1, base - 66, "k3", reg)


FLANK_TREES = [  # backdrop flank trees beside City Hall: (x, y_crown, r, trunk base)
    (128, 70, 21, 100), (90, 108, 26, 140),
    (512, 70, 21, 100), (550, 108, 26, 140),
]


def paint_forecourt_flank():
    L = new()
    # forecourt: lawn panels at the backdrop scale, a granite apron along the plinth, borders of bloom
    fc = box(64, 128, 603, 149) & ~box(272, 128, 367, 149)
    grass(L, fc, "forecourt", cell=(4, 3), big=40)
    apron = box(146, 132, 493, 137) & ~box(272, 132, 367, 137)
    L[apron] = I["p4"]
    for x in range(146, 494, 6):
        rect(L, x, 132, x, 137, "p3")
    rect(L, 146, 137, 493, 137, "p2")
    border = box(148, 138, 491, 142) & ~box(270, 138, 369, 142)      # shrub border with bloom clusters
    bn = vnoise("border", 2)
    L[border] = I["f3"]
    L[border & (bn < 0.4)] = I["f2"]
    L[border & (YY == 138) & (bn > 0.5)] = I["f4"]
    L[border & (YY == 142)] = I["f1"]
    for x in range(149, 490, 5):
        if 268 <= x <= 369:
            continue
        c = ("fl1", "fl3", "fl2", "fl1", "fl4")[int(hval("border", x) * 5)]
        y = 139 + int(hval("border-y", x) * 2)
        rect(L, x, y, x + 1, y, c); px(L, x, y + 1, c)
    # forecourt walk from the gate to the steps (granite)
    rect(L, 294, 150, 345, 169, "p4")
    for y in range(152, 170, 5):
        rect(L, 294, y, 345, y, "p3")
    for y0 in range(150, 170, 10):
        for x in range(298 + (y0 // 10 % 2) * 6, 345, 12):
            rect(L, x, y0, x, min(169, y0 + 9), "p3")
    rect(L, 294, 168, 345, 169, "t0")                                 # access light line (2537)
    for x in range(296, 345, 6):
        rect(L, x, 168, x + 1, 168, "t1")
    # flank trees (trunks then crowns), drawn back to front
    for i, (x, y, r, b) in enumerate(sorted(FLANK_TREES, key=lambda t: t[3])):
        trunk(L, x, b, y + int(r * 0.4), w=4)
        crown(L, x, y, r, ("flank", i), TREE_RAMP[:6], TREE_CUTS[:5], gain=0.92)
    # flagpoles with the U.S. and NYC flags
    for x, kind in FLAGS:
        rect(L, x, FLAG_TOP, x, FLAG_BASE, "m5"); rect(L, x + 1, FLAG_TOP, x + 1, FLAG_BASE, "m3")
        rect(L, x - 1, FLAG_BASE - 1, x + 2, FLAG_BASE, "m2"); px(L, x, FLAG_TOP - 1, "au2")
        fx0, fy0, fw, fh = x + 2, FLAG_TOP + 2, 17, 11
        for i in range(fw):
            dy = 1 if 5 <= i <= 10 else 0
            for j in range(fh):
                if kind == "us":
                    col = "fr" if (j // 1) % 2 == 0 else "m6"
                    if i < 7 and j < 6:
                        col = "fb" if (i + j) % 3 else "m6"
                else:
                    col = "fb" if i < 6 else ("m6" if i < 12 else "fo")
                    if 6 <= i < 12 and 3 <= j <= 7 and (i, j) in ((8, 4), (9, 5), (8, 6), (9, 4)):
                        col = "fb"
                px(L, fx0 + i, fy0 + j + dy, col)
            px(L, fx0 + i, fy0 + fh + dy, "m2" if i % 3 else "m1")
    # hedge belt with an iron picket fence on its south face; gate opening on the axis
    # clipped boxwood: rounded 22-28 px segments (bumped top edge), lit top, shaded face, dark foot
    hb = np.zeros((H, W), bool)
    x = 64
    while x < 604:
        w = (24, 22, 28, 26, 23, 27)[int(hval("hedge-seg", x) * 6)]
        x1 = min(603, x + w - 1)
        if not (x1 < 284 or x > 355):
            x = 356
            continue
        for xx in range(x, x1 + 1):
            u = (xx - x + 0.5) / (x1 - x + 1)
            top = HEDGE[0] + 3 - int(round(3 * math.sqrt(max(0.0, 1 - (2 * u - 1) ** 2))))
            hb[top:HEDGE[1] + 1, xx] = True
        x = x1 + 1
    h = vnoise("hedge", 3)
    L[hb] = I["f3"]
    L[hb & (h < 0.38)] = I["f2"]
    L[hb & (h > 0.68)] = I["f4"]
    topm = edge_above(hb) | np.roll(edge_above(hb), 1, 0) & hb
    L[topm] = I["f4"]
    L[edge_above(hb) & (h > 0.5)] = I["f5"]
    L[hb & (YY >= HEDGE[1] - 5)] = I["f2"]
    L[hb & (YY >= HEDGE[1] - 5) & (h < 0.4)] = I["f1"]
    gaps = edge_below(hb.T).T | edge_below(hb[:, ::-1].T).T[:, ::-1]
    L[gaps & hb & (YY > HEDGE[0] + 3)] = I["f1"]
    for x in range(62, 604):
        if 284 <= x <= 355:
            continue
        px(L, x, HEDGE[1] - 1, "k2"); px(L, x, HEDGE[1], "k0")
        if x % 4 == 0:
            rect(L, x, HEDGE[1] - 9, x, HEDGE[1], "k1"); px(L, x, HEDGE[1] - 10, "k2")
    for (a, b) in GATE_PIERS:                                          # granite gate piers with scanner strips
        rect(L, a, 140, b, 169, "m4"); rect(L, a, 140, a + 1, 169, "m5"); rect(L, b, 140, b, 169, "m2")
        rect(L, a - 1, 138, b + 1, 140, "m6"); rect(L, a - 1, 141, b + 1, 141, "m2")
        rect(L, a + 2, 132, b - 2, 137, "wl"); rect(L, a + 2, 132, a + 3, 134, "wl2"); rect(L, a + 2, 137, b - 2, 137, "k1")
        sx = b - 1 if a < CX else a + 1
        rect(L, sx, 148, sx, 161, "t1"); px(L, sx, 148, "t2"); px(L, sx, 152, "t2")
        rect(L, a, 168, b, 169, "m2")
    return L


def park_masks():
    m = {}
    m["axis"] = box(AXIS[0], 168, AXIS[1], H - 1)
    x0, x1, y0, y1 = SOUTH_PLAZA
    m["south"] = box(x0, y0, x1, y1)
    m["plaza"] = ell(*FOUNTAIN, *PLAZA_R)
    m["basin"] = ell(*FOUNTAIN, *BASIN_R)
    m["diag"] = seg(*DIAG)
    m["east_conn"] = box(*EAST_CONN)
    m["s_conn"] = box(*S_CONN)
    m["w_gate"] = box(*W_GATE)
    m["statue_walk"] = box(*STATUE_WALK)
    m["statue_c"] = ell(*STATUE_C)
    m["e_walk"] = box(*E_WALK_H) | box(*E_WALK_V)
    park = box(64, 168, PARK_ROW - 1, H - 1) | m["south"]
    m["granite"] = (m["axis"] | m["south"] | m["plaza"] | m["statue_c"]) & ~m["basin"]
    m["hex"] = (m["diag"] | m["east_conn"] | m["s_conn"] | m["w_gate"] | m["statue_walk"] | m["e_walk"]) & \
        ~m["granite"] & ~m["basin"]
    m["path"] = (m["granite"] | m["hex"]) & (YY >= 168)
    m["lawn"] = park & ~m["path"] & ~m["basin"] & (YY >= 168)
    return m


SLAB_TONES = ("p3", "p3", "p4", "p3", "p2", "p3", "p4", "p3")
WIDTHS = (14, 10, 18, 12, 16, 9, 13, 15, 11, 17)


def flags(L, mask, y0, y1, course_h, key, widths=WIDTHS, tones=SLAB_TONES, joint="p2"):
    """Granite flag courses with irregular slab lengths (joints never line up into a brick or grid pattern)."""
    for c, ya in enumerate(range(y0, y1 + 1, course_h)):
        off = int(hval(key, "off", c) * 23)
        k = int(hval(key, "ph", c) * len(widths))
        x = -off
        while x < W:
            w = widths[k % len(widths)]
            t = tones[int(hval(key, c, k) * len(tones))]
            sl = mask & box(x + 1, ya + 1, x + w - 1, ya + course_h - 1)
            L[sl] = I[t]
            hi = mask & box(x + 1, ya + 1, x + 2, ya + 1)
            if t != "p4":
                L[hi] = I["p4"]
            lo = mask & box(x + w - 2, ya + course_h - 1, x + w - 1, ya + course_h - 1)
            L[lo] = I["p2"]
            j = mask & (box(x, ya, x, ya + course_h - 1) | box(x, ya, x + w - 1, ya))
            L[j] = I[joint]
            x += w
            k += 1


def hex_pavers(L, mask, key="hex", sx=10, sy=6):
    """NYC park hexagonal pavers: Voronoi cells of a hex lattice squashed for the 3/4 view, mortar on cell borders,
    a lit upper lip on each block."""
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return
    fx, fy = xs + 0.5, ys + 0.5
    j0 = np.floor(fy / sy).astype(int)
    best = np.full(len(xs), 1e9); second = np.full(len(xs), 1e9)
    bid = np.zeros((len(xs), 2), int)
    by = np.zeros(len(xs))
    for dj in (-1, 0, 1, 2):
        j = j0 + dj
        off = (j % 2) * (sx / 2)
        i0 = np.floor((fx - off) / sx).astype(int)
        for di in (-1, 0, 1):
            i = i0 + di
            cxs, cys = i * sx + off, j * sy
            d = np.hypot(fx - cxs, (fy - cys) * (sx / sy) * 0.866)
            upd = d < best
            second = np.where(upd, best, np.minimum(second, d))
            bid[upd] = np.stack([i[upd], j[upd]], 1)
            by = np.where(upd, cys, by)
            best = np.where(upd, d, best)
    joint = (second - best) < 1.25
    tones = np.array([I[("x2", "x2", "x1", "x2", "x3", "x2")[int(hval(key, a, b) * 6)]] for a, b in bid])
    out = np.where(joint, I["x0"], tones)
    lip = (~joint) & (fy - by < -sy * 0.32)
    out = np.where(lip & (tones == I["x2"]), I["x3"], out)
    out = np.where(lip & (tones == I["x1"]), I["x2"], out)
    L[ys, xs] = out


TUFT = ((0, 0, 1), (-1, 1, 1), (1, 1, 0), (0, 1, -1))                 # blade pair over a dark root (dx, dy, step)


def grass(L, mask, key, cell=(5, 4), big=56):
    """Lawn: two broad light zones (sunlit swaths / damp hollows, no stripes, no grid) and one blade tuft per
    jittered cell, every tuft one tone step from its ground so it reads as texture, never as flecks."""
    n = vnoise(key, big)
    chk = (XX // 2 + YY // 2) % 2 == 0            # a 2x2 cluster checker softens each zone border (no hard edge)
    base = np.full((H, W), I["g2"], np.int16)
    base[(n > 0.72) | ((n > 0.68) & chk)] = I["g3"]
    base[(n < 0.18) | ((n < 0.22) & chk)] = I["g1"]
    L[mask] = base[mask]
    ramp = [I[c] for c in ("g0", "g1", "g2", "g3", "g4")]
    order = {c: i for i, c in enumerate(ramp)}
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return
    cw, ch = cell
    for gy in range(ys.min() // ch, ys.max() // ch + 1):
        for gx in range(xs.min() // cw, xs.max() // cw + 1):
            if hval(key, "s", gx, gy) > 0.78:
                continue
            x = gx * cw + int(hval(key, "x", gx, gy) * cw)
            y = gy * ch + int(hval(key, "y", gx, gy) * ch)
            if not (0 < x < W - 1 and y < H - 1) or not mask[y, x]:
                continue
            b = order.get(int(L[y, x]), 2)
            for dx, dy, d in TUFT:
                if mask[y + dy, x + dx]:
                    L[y + dy, x + dx] = ramp[max(0, min(4, b + d))]


def paint_park_ground():
    L = new()
    m = park_masks()
    grass(L, m["lawn"], "lawn")
    gm = m["granite"] & (YY >= 168)
    axis_s = (m["axis"] | m["south"]) & ~m["plaza"] & gm
    flags(L, axis_s & m["axis"] & ~m["south"], 168, 337, 8, "axis")
    flags(L, axis_s & m["south"], 338, 359, 11, "south", widths=(22, 16, 28, 19, 25, 17, 24))
    # fountain plaza: radial granite rings with staggered radial joints
    cx, cy = FOUNTAIN
    pl = m["plaza"] & ~m["basin"]
    ys, xs = np.nonzero(pl)
    rr = np.hypot((xs + 0.5 - cx) / PLAZA_R[0], (ys + 0.5 - cy) / PLAZA_R[1])
    th = np.arctan2((ys + 0.5 - cy) / PLAZA_R[1], (xs + 0.5 - cx) / PLAZA_R[0])
    k = np.floor((rr - 0.5) / 0.1).astype(int)
    frac = (rr - 0.5) / 0.1 - k
    ring_tone = np.array([I[t] for t in ("p3", "p4", "p3", "p3", "p2", "p2")])
    out = ring_tone[np.clip(k, 0, 5)]
    nseg = 22 + 7 * np.clip(k, 0, 5)
    a = (th / (2 * np.pi) + 0.5) * nseg + 0.5 * (k % 2)
    af = a - np.floor(a)
    rad_joint = (af < 0.9 / (2 * np.pi * rr * PLAZA_R[0] / nseg))
    ring_joint = frac < 0.12
    out = np.where(ring_joint | rad_joint, I["p2"], out)
    out = np.where((rr > 0.95), I["p1"], out)
    out = np.where((rr > 0.95) & (np.floor(a * 2) % 2 == 0), I["p2"], out)
    seg_id = np.floor(a).astype(int)
    hi = (~ring_joint) & (~rad_joint) & (frac < 0.32) & (rr <= 0.95) & (out == I["p3"])
    out = np.where(hi & (np.array([hval("ring", int(kk), int(s)) for kk, s in zip(k, seg_id)]) < 0.35), I["p4"], out)
    L[ys, xs] = out
    # statue circle: granite with a compass ring
    sc = m["statue_c"] & ~m["plaza"]
    flags(L, sc, 240, 292, 7, "statue", widths=(9, 12, 8, 11, 10))
    sx0, sy0, srx, sry = STATUE_C
    ring = sc & ~ell(sx0, sy0, srx - 2, sry - 1.5)
    L[ring] = I["p2"]
    L[ring & edge_above(sc)] = I["p4"]
    hex_pavers(L, m["hex"] & (YY >= 168))
    # granite curbs where paths meet lawn (lit on the north side of each path)
    lawn = m["lawn"]
    path = m["path"]
    up = np.zeros_like(path); up[1:] = path[1:] & lawn[:-1]
    dn = np.zeros_like(path); dn[:-1] = path[:-1] & lawn[1:]
    lf = np.zeros_like(path); lf[:, 1:] = path[:, 1:] & lawn[:, :-1]
    rt = np.zeros_like(path); rt[:, :-1] = path[:, :-1] & lawn[:, 1:]
    L[up | lf] = I["p5"]
    L[dn | rt] = I["p2"]
    gl = np.zeros_like(lawn); gl[:-1] = lawn[:-1] & path[1:]
    L[gl] = I["g1"]
    return L


def bed(L, cx, cy, rx, ry, key):
    m = ell(cx, cy, rx, ry)
    inner = ell(cx, cy, rx - 2, ry - 1.5)
    L[m & ~inner] = I["s1"]
    L[m & ~inner & edge_below(m)] = I["s0"]
    n = vnoise("bed-" + key, 2)
    L[inner] = I["f3"]
    L[inner & (n < 0.38)] = I["f2"]
    L[inner & (n > 0.75)] = I["f4"]
    cols = ("fl0", "fl1", "fl2", "fl3", "fl4", "fl5")
    pal = [cols[int(hval(key, "c", q) * 6)] for q in range(3)]
    for y in range(int(cy - ry), int(cy + ry) + 1, 2):
        for x in range(int(cx - rx), int(cx + rx) + 1, 3):
            xx = x + (1 if (y // 2) % 2 else 0)
            if y + 1 < H and inner[y, xx] and inner[y + 1, xx] and hval(key, xx, y) < 0.62:
                c = pal[int(hval(key, "p", xx, y) * 3)]
                rect(L, xx, y, xx + 1, y, c)
                px(L, xx, y + 1, c)
                px(L, xx + 1, y + 1, "f2")


def paint_ground_detail():
    L = new()
    for i, (cx, cy, rx, ry) in enumerate(BEDS):
        bed(L, cx, cy, rx, ry, f"bed{i}")
    # teal wayfinding inlay down the central walk (2537), interrupted at the slab joints
    for y in range(172, 338):
        px(L, 319, y, "t0"); px(L, 320, y, "t0")
    for y in range(176, 338, 16):
        rect(L, 319, y, 320, y + 1, "t1")
    # cast-iron drain grates and a few fallen-leaf clusters on the paths
    for (x, y) in ((320, 324), (172, 334), (588, 300)):
        rect(L, x - 4, y - 2, x + 3, y + 1, "k1"); rect(L, x - 4, y - 2, x + 3, y - 2, "k2")
        for xx in range(x - 3, x + 3, 2):
            rect(L, xx, y - 1, xx, y, "k0")
    for i, (x, y) in enumerate(((300, 214), (340, 262), (226, 300), (152, 242), (560, 264), (470, 284),
                                (110, 296), (604, 344), (380, 346), (262, 264))):
        c = ("au0", "s1", "fl5")[i % 3]
        rect(L, x, y, x + 1, y, c); px(L, x + 1, y + 1, "s1" if c != "s1" else "au0")
    return L


def paint_fountain_basin():
    L = new()
    cx, cy = FOUNTAIN
    out = ell(cx, cy, *BASIN_R)
    inn = ell(cx, cy, *BASIN_IN)
    rim = out & ~inn
    ys, xs = np.nonzero(rim)
    for x, y in zip(xs, ys):
        ang = math.atan2(y + 0.5 - cy, x + 0.5 - cx)
        lit = -math.cos(ang) * 0.5 - math.sin(ang) * 0.3
        L[y, x] = I["m5"] if lit > 0.2 else (I["m4"] if lit > -0.25 else I["m3"])
    L[rim & edge_above(out)] = I["m6"]
    wall = np.zeros((H, W), bool)                     # outer face of the basin wall on the near (south) half
    for x in range(cx - BASIN_R[0], cx + BASIN_R[0] + 1):
        col = np.nonzero(out[:, x])[0]
        if len(col):
            yb = col.max()
            if yb >= cy:
                for k in range(1, 4):
                    wall[yb + k, x] = True
    L[wall] = I["m3"]
    L[wall & edge_below(wall)] = I["m2"]
    L[wall & ((XX % 9) == 0)] = I["m2"]
    water = inn
    wn = vnoise("water", 3)
    L[water] = I["c1"]
    L[water & (YY < cy - 6) & (wn > 0.45)] = I["c2"]
    L[water & ~ell(cx, cy, BASIN_IN[0] - 3, BASIN_IN[1] - 2)] = I["c0"]
    for (rx, ry) in ((14, 6), (24, 11), (33, 16)):     # ripple rings around the centrepiece
        ring = ell(cx, cy + 1, rx, ry) & ~ell(cx, cy + 1, rx - 1.2, ry - 1)
        L[water & ring & (wn > 0.3)] = I["c2"]
    for (x, y) in ((150, 262), (192, 280), (160, 284), (186, 258), (140, 274), (204, 268)):
        rect(L, x, y, x + 1, y, "c3")
    return L


def fountain_sprite(L, reg=None):
    cx, cy = FOUNTAIN
    x0 = cx - 5
    for y in range(cy - 10, cy + 3):                                  # pedestal
        for i in range(10):
            px(L, x0 + i, y, ("m5", "m5", "m4", "m4", "m4", "m3", "m3", "m3", "m2", "m2")[i], reg)
    rect(L, x0 - 1, cy - 11, x0 + 10, cy - 11, "m6", reg)
    for y in range(cy + 1, cy + 3):                                   # splash ring at the waterline
        for x in range(x0 - 4, x0 + 14):
            if (x + y) % 3:
                px(L, x, y, "c3" if (x + y) % 2 else "c2", reg)
    for y in range(252, 259):                                          # lower bowl
        t = (y - 252) / 6
        hw = int(round(16 - 9 * t * t))
        for x in range(cx - hw, cx + hw):
            u = (x + 0.5 - cx) / hw
            v = cyl(u)
            px(L, x, y, tone(["m2", "m3", "m4", "m5"], v, (0.15, 0.36, 0.55)), reg)
    rect(L, cx - 16, 251, cx + 15, 251, "m6", reg)
    rect(L, cx - 14, 252, cx + 13, 253, "c2", reg); rect(L, cx - 12, 252, cx - 6, 252, "c3", reg)
    for x in list(range(cx - 16, cx - 12)) + list(range(cx + 12, cx + 16)):   # falling sheets
        for y in range(256, 268):
            if (x + y) % 2 == 0 or y < 258:
                px(L, x, y, "c3" if (y + x) % 3 else "c2", reg)
    for y in range(238, 251):                                          # column
        for i, c in enumerate(("m5", "m4", "m3", "m2")):
            px(L, cx - 2 + i, y, c, reg)
    rect(L, cx - 3, 244, cx + 2, 244, "m5", reg)
    for y in range(234, 239):                                          # upper bowl
        hw = int(round(9 - 4 * ((y - 234) / 4) ** 2))
        for x in range(cx - hw, cx + hw):
            px(L, x, y, tone(["m2", "m3", "m4", "m5"], cyl((x + 0.5 - cx) / hw), (0.15, 0.36, 0.55)), reg)
    rect(L, cx - 9, 233, cx + 8, 233, "m6", reg); rect(L, cx - 7, 234, cx + 6, 234, "c2", reg)
    for x in (cx - 9, cx - 8, cx + 7, cx + 8):
        for y in range(236, 251, 2):
            px(L, x, y, "c3", reg)
    stamp(L, cx - 2, 226, [".bb.", "bBBb", "bBBb", ".bb.", "bBBb", ".bb.", "..b."],
          {"b": "bz1", "B": "bz2"}, reg)                                  # bronze finial
    px(L, cx - 1, 227, "bz3", reg)
    for y in range(218, 226):                                          # jet and its crown of spray
        px(L, cx - 1, y, "c3", reg); px(L, cx, y, "c2" if y % 2 else "c3", reg)
    for (dx, dy) in ((-4, 218), (2, 218), (-5, 220), (3, 220)):          # spray crown (2 px clusters)
        rect(L, cx + dx, dy, cx + dx + 1, dy, "c3", reg)
    rect(L, cx - 2, 216, cx + 1, 216, "c2", reg); rect(L, cx - 1, 216, cx, 216, "c3", reg)


def statue_sprite(L, reg=None):
    x, b = STATUE
    rect(L, x - 10, b - 2, x + 9, b, "m3", reg); rect(L, x - 10, b, x + 9, b, "m2", reg)
    rect(L, x - 10, b - 2, x + 9, b - 2, "m5", reg)
    rect(L, x - 8, b - 14, x + 7, b - 3, "m4", reg); rect(L, x - 8, b - 14, x - 6, b - 3, "m5", reg)
    rect(L, x + 6, b - 14, x + 7, b - 3, "m2", reg)
    rect(L, x - 4, b - 10, x + 3, b - 6, "bz1", reg); rect(L, x - 3, b - 9, x + 2, b - 9, "bz2", reg)
    rect(L, x - 3, b - 7, x + 1, b - 7, "bz2", reg)
    rect(L, x - 9, b - 16, x + 8, b - 15, "m6", reg); rect(L, x - 9, b - 15, x + 8, b - 15, "m3", reg)
    fig = ["...hh....", "..hHHh...", "..hHHh...", "...hh....", "..cCCc...", ".cCCCCc..", ".cCCCCcc.", ".cCCCCcc.",
           ".cCcCCc..", "..cCCCc..", "..cCCCcc.", "..cCCCCc.", "..cCCCCc.", ".ccCCCCcc", ".ccCCCCcc", "..cc.cc..",
           "..cc.cc..", "..cC.Cc..", "..cC.Cc..", "..cc.cc..", ".ccc.ccc."]
    stamp(L, x - 5, b - 17 - len(fig), fig, {"h": "bz1", "H": "bz2", "c": "bz0", "C": "bz1"}, reg)
    for j in range(len(fig)):                                          # verdigris light on the west (left) edge
        row = fig[j]
        k = next((i for i, ch in enumerate(row) if ch not in ". "), None)
        if k is not None:
            px(L, x - 5 + k + 1, b - 17 - len(fig) + j, "bz3" if j % 3 else "bz2", reg)


def bench(L, x, b, reg):
    rows = ["k..................k",
            "kWWWWWWWWWWWWWWWWWWk",
            "kddddddddddddddddddk",
            "kWWWWWWWWWWWWWWWWWWk",
            "k..................k",
            "kSSSSSSSSSSSSSSSSSSk",
            "kDDDDDDDDDDDDDDDDDDk",
            "k.k..............k.k",
            "k.k..............k.k"]
    stamp(L, x, b - len(rows) + 1, rows, {"k": "k1", "W": "wd2", "d": "wd1", "S": "wd2", "D": "wd0"}, reg)


def bin_sprite(L, x, b, reg):
    rows = [".KKKK.", "KkKkKK", "KkkkkK", "KkKkKK", "KkkkkK", "KkKkKK", ".KKKK."]
    stamp(L, x - 3, b - len(rows) + 1, rows, {"K": "k1", "k": "f1"}, reg)
    px(L, x - 2, b - len(rows) + 1, "k3", reg)


def paint_props():
    L = new()
    items = {}

    def item(name, fn, base, pivot_only=False):
        reg = np.zeros((H, W), bool)
        fn(reg)
        items[name] = {"mask": reg, "base": base}

    for i, (x0, x1, b) in enumerate(FENCES):                           # low NYC park hoop fences
        def f(reg, x0=x0, x1=x1, b=b):
            for x in range(x0, x1 + 1):
                ph = (x - x0) % 6
                px(L, x, b - 3, "k3" if ph < 3 else "k2", reg)
                if ph in (0, 1, 5):
                    px(L, x, b - 2, "k1", reg)
                if ph in (0, 3):
                    px(L, x, b - 1, "k1", reg); px(L, x, b, "k0", reg)
                    px(L, x, b - 2, "k1", reg)
            rect(L, x0, b - 4, x0, b, "k1", reg); rect(L, x1, b - 4, x1, b, "k1", reg)
        item(f"fence_{i}", f, b)
    for i, (x, b) in enumerate(BENCHES):
        item(f"bench_{i}", lambda reg, x=x, b=b: bench(L, x, b, reg), b)
    for i, (x, b) in enumerate(BINS):
        item(f"bin_{i}", lambda reg, x=x, b=b: bin_sprite(L, x, b, reg), b)
    for i, (x, b) in enumerate(BOLLARDS):
        def bo(reg, x=x, b=b):
            rect(L, x - 2, b - 6, x + 1, b, "k1", reg); rect(L, x - 2, b - 6, x - 2, b, "k3", reg)
            rect(L, x - 2, b - 4, x + 1, b - 4, "t1", reg); rect(L, x - 2, b - 7, x + 1, b - 7, "k2", reg)
        item(f"bollard_{i}", bo, b)

    def pylon(reg):
        x, b = PYLON
        rect(L, x - 3, b - 1, x + 3, b, "k0", reg)
        rect(L, x - 2, b - 17, x + 2, b - 2, "k1", reg); rect(L, x - 2, b - 17, x - 2, b - 2, "k2", reg)
        rect(L, x - 1, b - 15, x + 1, b - 7, "t0", reg); rect(L, x - 1, b - 14, x + 1, b - 13, "t1", reg)
        rect(L, x - 1, b - 11, x, b - 11, "t2", reg); rect(L, x - 1, b - 9, x + 1, b - 9, "t1", reg)
        rect(L, x - 2, b - 19, x + 2, b - 18, "t1", reg); rect(L, x - 2, b - 19, x - 1, b - 19, "t2", reg)
    item("info_pylon", pylon, PYLON[1])
    # registered base items drawn in other layers (gate piers on the Broadway fence)
    for i, (y0, y1) in enumerate(((250, 257), (282, 289))):
        reg = box(59, y0, 66, y1)
        items[f"broadway_pier_{i}"] = {"mask": reg, "base": y1}
    return L, items


def paint_trees(layer):
    L = new()
    for i, (x, b, r) in enumerate(TREES[layer]):
        cy = b - 16 - int(r * 0.78)
        trunk(L, x, b, cy + int(r * 0.3), w=6)
        crown(L, x, cy, r, (layer, i))
    return L


def paint_lamps(layer):
    L = new()
    for x, b in LAMPS[layer]:
        lamp_sprite(L, x, b)
    return L


def paint_fountain_ysort():
    L = new()
    fountain_sprite(L)
    for x, b in FOUNTAIN_LAMPS:
        lamp_sprite(L, x, b)
    return L


def paint_statue():
    L = new()
    statue_sprite(L)
    return L


FG_CROWNS = [(-2, 366, 40), (650, 372, 38)]                            # canopies of trees south of the frame


def paint_fg():
    L = new()
    for i, (x, y, r) in enumerate(FG_CROWNS):
        crown(L, x, y, r, ("fg", i), TREE_RAMP[:6], TREE_CUTS[:5], gain=0.8)
    return L


def tree_canopy_y(b, r):
    return b - 16 - int(r * 0.78)


def paint_shadows(below_idx):
    """Opaque cast shadows (sun from the south-west -> shadows fall north-east, up-right on screen)."""
    sm = np.zeros((H, W), bool)
    for layer, trees in TREES.items():
        for (x, b, r) in trees:
            sm |= ell(x + 0.55 * r, b - 0.30 * r, 0.95 * r, 0.42 * r)
            sm |= seg((x, b), (x + 0.55 * r, b - 0.30 * r), 3)
    for lamps in list(LAMPS.values()) + [FOUNTAIN_LAMPS]:
        for (x, b) in lamps:
            sm |= seg((x, b), (x + 26, b - 15), 0.8)
            sm |= ell(x + 28, b - 16, 4, 2)
    sx, sb = STATUE
    sm |= ell(sx + 12, sb - 6, 13, 6)
    fx, fy = FOUNTAIN
    sm |= ell(fx + 14, fy - 8, 18, 7) & ~ell(fx, fy, *BASIN_R)
    for (x, b) in BENCHES:
        sm |= box(x + 2, b - 10, x + 21, b - 9)
    for (x0, x1, b) in FENCES:
        sm |= box(x0 + 2, b - 5, x1 + 2, b - 5) & ((XX % 6) < 3)
    sm |= seg((PYLON[0], PYLON[1]), (PYLON[0] + 10, PYLON[1] - 6), 1.5)
    sm &= (YY >= 168) & (XX >= 64) & (XX < PARK_ROW)
    L = new()
    L[sm] = SHADE_LUT[np.clip(below_idx[sm], 0, None)]
    return L


# ============================================================================ actor, walkability, audits
def heroine_48():
    """Approved v8 static south idle (96 texels = 48 logical px) sampled 2:1 for the logical scene."""
    a = np.array(Image.open(rp(HEROINE_REL)).convert("RGBA"))
    ys, xs = np.nonzero(a[..., 3])
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = a.shape[:2]
    small = np.array(Image.fromarray(a, "RGBA").resize((max(1, w // 2), h // 2), Image.NEAREST))
    small[..., 3] = np.where(small[..., 3] >= 128, 255, 0)
    return small


def overlap_feet(mask, spr_alpha):
    """Boolean map of foot positions (x, y) at which the actor sprite would overlap any texel of `mask`."""
    sh, sw = spr_alpha.shape
    out = np.zeros((H, W), bool)
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return out
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    sub = mask[y0:y1 + 1, x0:x1 + 1]
    oy, ox = np.nonzero(spr_alpha)
    for j, i in zip(oy, ox):
        fy0 = y0 + sh - 1 - j
        fx0 = x0 + sw // 2 - i
        ya, xa = max(0, fy0), max(0, fx0)
        yb, xb = min(H, fy0 + sub.shape[0]), min(W, fx0 + sub.shape[1])
        if ya < yb and xa < xb:
            out[ya:yb, xa:xb] |= sub[ya - fy0:yb - fy0, xa - fx0:xb - fx0]
    return out


def erode(mask, rx, ry):
    m = np.pad(mask.astype(np.int32), ((ry + 1, ry), (rx + 1, rx)))
    s = m.cumsum(0).cumsum(1)
    k = (2 * ry + 1) * (2 * rx + 1)
    tot = s[2 * ry + 1:, 2 * rx + 1:] - s[:-2 * ry - 1, 2 * rx + 1:] - s[2 * ry + 1:, :-2 * rx - 1] + \
        s[:-2 * ry - 1, :-2 * rx - 1]
    return tot[:H, :W] == k


def walkable(items, spr_alpha):
    m = park_masks()
    area = m["path"] & (YY >= WALK_TOP) & (XX >= 64) & (XX <= 634)
    area &= ~dilate(m["basin"], 3)
    wk = erode(area | ~box(0, 0, W - 1, H - 1), 4, 2) & area
    wk[H - 1, :] = False
    collars = {}
    for name, it in items.items():           # derived collar: feet north of the base whose sprite overlaps the item
        ov = overlap_feet(it["mask"], spr_alpha)
        col = ov & (YY < it["base"])
        ys, xs = np.nonzero(it["mask"])
        foot = box(xs.min() - 5, it["base"] - 4, xs.max() + 5, it["base"] + 3)
        collars[name] = col | foot
        wk &= ~collars[name]
    # Y-sorted objects: footprint collars only (the Y-sort handles in front / behind)
    feet = {"fountain_lamp_0": (FOUNTAIN_LAMPS[0], 4), "fountain_lamp_1": (FOUNTAIN_LAMPS[1], 4),
            "statue_pedestal": (STATUE, 11)}
    for layer, lamps in LAMPS.items():
        for i, p in enumerate(lamps):
            feet[f"{layer}_{i}"] = (p, 4)
    for name, ((x, b), half) in feet.items():
        c = box(x - half - 4, b - 6, x + half + 4, b + 3)
        collars[name] = c
        wk &= ~c
    return wk, collars


def occluder_masks(rgba):
    """For each Y-sort pivot, the mask of everything drawn over an actor whose foot row is north of the pivot."""
    fg = rgba["fg-occlusion"][..., 3] == 255
    ys = {n: rgba[n][..., 3] == 255 for n in YSORT_LAYERS}
    return fg, ys


def visibility(walk, rgba, spr_alpha, step=2):
    fg, ys = occluder_masks(rgba)
    sh, sw = spr_alpha.shape
    tot = spr_alpha.sum()
    fails, worst, worst_at = [], 1.0, None
    for y in range(0, H, step):
        o = fg.copy()
        for n, pv in YSORT_PIVOTS.items():
            if y < pv:
                o |= ys[n]
        for x in range(0, W, step):
            if not walk[y, x]:
                continue
            x0, y0 = x - sw // 2, y - sh + 1
            if x0 < 0 or y0 < 0 or x0 + sw > W:
                continue
            vis = 1 - (o[y0:y0 + sh, x0:x0 + sw] & spr_alpha).sum() / tot
            if vis < worst:
                worst, worst_at = vis, (x, y)
            if vis < 1 / 3:
                fails.append((x, y))
    return fails, worst, worst_at


def depth_audit(items, walk, spr_alpha):
    res = {}
    for name, it in items.items():
        ov = overlap_feet(it["mask"], spr_alpha) & walk
        res[name] = {"overlapping_walkable_feet": int(ov.sum()),
                     "wrong_order_feet": int((ov & (YY < it["base"])).sum()), "base_row": it["base"]}
    return res


def flood(mask, start):
    seen = np.zeros_like(mask)
    if not mask[start[1], start[0]]:
        return seen
    stack = [start]
    seen[start[1], start[0]] = True
    while stack:
        x, y = stack.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and mask[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                stack.append((nx, ny))
    return seen


def route_points():
    pts = [PINS[p] if isinstance(p, str) else p for p in ROUTE]
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0))
        for k in range(1, n + 1):
            out.append((int(round(x0 + (x1 - x0) * k / n)), int(round(y0 + (y1 - y0) * k / n))))
    return out


# ============================================================================ scene assembly
def composite_idx(layers, names):
    out = layers[names[0]].copy()
    for n in names[1:]:
        m = layers[n] >= 0
        out[m] = layers[n][m]
    return out


def scene():
    spr = heroine_48()
    spr_alpha = spr[..., 3] == 255
    layers = {"north-groves": paint_north_groves(), "streets": paint_streets(), "city-hall": paint_city_hall(),
              "forecourt-flank": paint_forecourt_flank(), "park-ground": paint_park_ground(),
              "ground-detail": paint_ground_detail(), "fountain-basin": paint_fountain_basin()}
    below = composite_idx(layers, list(layers))
    layers["cast-shadows"] = paint_shadows(below)
    props, items = paint_props()
    layers["props-low"] = props
    for n in ("tree-nw-ysort", "trees-ne-ysort", "tree-se-ysort"):
        layers[n] = paint_trees(n)
    for n in ("lamps-n-ysort", "lamps-s-ysort"):
        layers[n] = paint_lamps(n)
    layers["statue-ysort"] = paint_statue()
    layers["fountain-ysort"] = paint_fountain_ysort()
    layers["fg-occlusion"] = paint_fg()
    despeckled = despeckle_ground(layers)
    walk, collars = walkable(items, spr_alpha)
    layers["guides"] = paint_guides(walk, collars)
    return {"layers": layers, "items": items, "walk": walk, "collars": collars, "spr": spr, "spr_alpha": spr_alpha,
            "despeckled_ground_texels": despeckled}


GROUND_LAYERS = ("park-ground", "ground-detail", "cast-shadows", "fountain-basin", "forecourt-flank")
LUMA = (RGB[:, :3].astype(np.int32) @ np.array([299, 587, 114])) // 1000


def despeckle_ground(layers, passes=3):
    """A ground texel left brighter than all 8 neighbours by >= 40 luma (usually a 2 px slab highlight half
    covered by a lamp post or fence) takes its darkest neighbour's colour. Sprite layers are never edited."""
    fixed = 0
    for _ in range(passes):
        flat = composite_idx(layers, ART_LAYERS)
        l = LUMA[np.clip(flat, 0, None)]
        p = np.pad(l, 1, mode="edge")
        pi = np.pad(flat, 1, mode="edge")
        nbs = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0)]
        nb = np.stack([p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] for dy, dx in nbs])
        nbi = np.stack([pi[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] for dy, dx in nbs])
        iso = (l - nb.max(0) >= 40) & (YY >= 150)
        darkest = np.take_along_axis(nbi, nb.argmin(0)[None], 0)[0]
        n = 0
        for y, x in zip(*np.nonzero(iso)):
            for name in reversed(ART_LAYERS):
                if layers[name][y, x] >= 0:
                    if name in GROUND_LAYERS:
                        layers[name][y, x] = darkest[y, x]
                        n += 1
                    break
        fixed += n
        if not n:
            break
    return fixed


def paint_guides(walk, collars):
    L = new()
    for y in range(2, H, 4):
        for x in range(2, W, 4):
            if y >= 150:
                L[y, x] = I["gd-walk"] if walk[y, x] else I["gd-block"]
    for k, (x, y) in PINS.items():
        rect(L, x - 1, y - 1, x + 1, y + 1, "gd-pin")
    for (x, y) in route_points()[::3]:
        px(L, x, y, "gd-route")
    return L


# ============================================================================ raster output
def to_rgba(idx):
    a = np.zeros((H, W, 4), np.uint8)
    m = idx >= 0
    a[m, :3] = RGB[idx[m]]
    a[m, 3] = 255
    return a


def png_bytes(arr):
    buf = io.BytesIO()
    Image.fromarray(arr, "RGBA").save(buf, "PNG", optimize=False, compress_level=9)
    return buf.getvalue()


def decode(png):
    im = Image.open(io.BytesIO(png))
    return im.mode, im.size, np.array(im.convert("RGBA"))


def composite_rgba(rgba_layers, names):
    out = rgba_layers[names[0]].copy()
    for n in names[1:]:
        m = rgba_layers[n][..., 3] == 255
        out[m] = rgba_layers[n][m]
    return out


def paste(dst, spr, x, ybase):
    h, w = spr.shape[:2]
    x0, y0 = x - w // 2, ybase - h + 1
    for j in range(h):
        for i in range(w):
            if spr[j, i, 3] and 0 <= x0 + i < W and 0 <= y0 + j < H:
                dst[y0 + j, x0 + i] = spr[j, i]


def runtime_stack_still(rgba, spr, foot):
    """Runtime draw order proposal: base (layers 1-9 merged) -> Y-sorted {7 sprite layers, actor} by pivot row (a
    sprite layer is drawn over the actor when the actor's foot row is north of its pivot) -> fg-occlusion."""
    out = composite_rgba(rgba, BASE_LAYERS)
    placed = False
    for name in sorted(YSORT_LAYERS, key=lambda n: YSORT_PIVOTS[n]):
        if not placed and foot[1] < YSORT_PIVOTS[name]:
            paste(out, spr, foot[0], foot[1]); placed = True
        m = rgba[name][..., 3] == 255
        out[m] = rgba[name][m]
    if not placed:
        paste(out, spr, foot[0], foot[1])
    fm = rgba["fg-occlusion"][..., 3] == 255
    out[fm] = rgba["fg-occlusion"][fm]
    return out


def x2(a):
    return np.repeat(np.repeat(a, VIEW, 0), VIEW, 1)


# ============================================================================ containers
DT = (2026, 10, 16, 4, 49, 30)


def zput(z, name, payload, method=zipfile.ZIP_DEFLATED):
    zi = zipfile.ZipInfo(name, DT)
    zi.compress_type = method
    z.writestr(zi, payload)


def make_ora(rgba, comp_png):
    stack = ['<?xml version="1.0" encoding="UTF-8"?>',
             f'<image version="0.0.5" w="{W}" h="{H}" xres="72" yres="72">', "<stack>"]
    for n in reversed(LAYERS):
        vis = "hidden" if n == "guides" else "visible"
        stack.append(f'<layer name="{n}" src="data/{n}.png" x="0" y="0" opacity="1.000" '
                     f'visibility="{vis}" composite-op="svg:src-over"/>')
    stack += ["</stack>", "</image>", ""]
    thumb = Image.open(io.BytesIO(comp_png)).convert("RGBA").resize((256, 144), Image.NEAREST)
    tb = io.BytesIO(); thumb.save(tb, "PNG")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        zput(z, "mimetype", b"image/openraster", zipfile.ZIP_STORED)
        zput(z, "stack.xml", "\n".join(stack).encode())
        for n in LAYERS:
            zput(z, f"data/{n}.png", png_bytes(rgba[n]))
        zput(z, "mergedimage.png", comp_png)
        zput(z, "Thumbnails/thumbnail.png", tb.getvalue())
    return buf.getvalue()


def make_pxo(rgba, comp_png):
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": n == "guides", "metadata": {}, "name": n,
                   "new_cels_linked": False, "opacity": 1.0, "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": n != "guides"} for n in LAYERS]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0}
                             for _ in LAYERS], "duration": 1.0, "metadata": {}}]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": json.dumps(EXPORT_STEM), "frame_current_tag": "0",
                      "include_tag_in_filename": "false", "interpolation": "0", "lines_count": "1",
                      "new_dir_for_each_frame_tag": "false", "number_of_digits": "4", "number_of_frames": "1",
                      "orientation": "0", "repeat_count": "0", "resize": "100", "save_quality": "0.75",
                      "separator_character": "\"_\"", "sheet_layers_as_separate_files": "false",
                      "split_layers": "false"}
    data = {"author_company": "", "author_contact": "", "author_display_name": "", "author_real_name": "",
            "brushes": [], "color_mode": 5, "current_frame": 0, "current_layer": 0, "export_profile": export_profile,
            "fps": 6.0, "frames": frames_json, "guides": [], "layers": layer_json, "license": "", "metadata": {},
            "next_keyframe_id": 0, "palettes": [], "pixelorama_version": PIXELORAMA_VERSION,
            "project_current_palette_name": "", "pxo_version": 7, "reference_images": [], "size_x": W, "size_y": H,
            "symmetry_points": [W - 1.0, H - 1.0], "tags": [], "tile_mode_x_basis_x": W, "tile_mode_x_basis_y": 0,
            "tile_mode_y_basis_x": 0, "tile_mode_y_basis_y": H, "tilesets": [], "user_data": "",
            "vanishing_points": []}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        zput(z, "data.json", json.dumps(data, separators=(",", ":")))
        zput(z, "mimetype", "application/x-pixelorama")
        zput(z, "preview.png", comp_png)
        zput(z, "image_data/frames/1/", b"")
        for li, n in enumerate(LAYERS, start=1):
            zput(z, f"image_data/frames/1/layer_{li}", np.ascontiguousarray(rgba[n]).tobytes())
            zput(z, f"image_data/frames/1/indices_layer_{li}", b"\x00")
    return buf.getvalue()


def make_gpl():
    lines = ["GIMP Palette", f"Name: {SLUG}_{AREA}_scene-palette_{VER}", "Columns: 8", "#"]
    for n, h in PALETTE:
        r, g, b = (int(h[j:j + 2], 16) for j in (0, 2, 4))
        lines.append(f"{r:3d} {g:3d} {b:3d}\t{n}")
    return ("\n".join(lines) + "\n").encode()


def walkmask_png(walk):
    a = np.zeros((H, W, 4), np.uint8)
    a[walk] = (255, 255, 255, 255)
    return png_bytes(a)


# ============================================================================ metrics
def isolated_bright(flat, region=None):
    """Single texels brighter than all 8 neighbours by luma >= 40 (the 'pale fleck' defect)."""
    l = flat[..., :3].astype(np.int32) @ np.array([299, 587, 114]) // 1000
    p = np.pad(l, 1, mode="edge")
    nb = np.stack([p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                   if (dy, dx) != (0, 0)])
    iso = (l - nb.max(0) >= 40)
    if region is not None:
        iso &= region
    ys, xs = np.nonzero(iso)
    return int(len(ys)), [[int(x), int(y)] for y, x in zip(ys[:12], xs[:12])]


def single_texel_islands(flat, region):
    """Share of texels with no 4-neighbour of the same colour (noise, as opposed to intentional clusters)."""
    c = flat[..., 0].astype(np.int32) << 16 | flat[..., 1].astype(np.int32) << 8 | flat[..., 2]
    p = np.pad(c, 1, mode="edge")
    same = np.zeros((H, W), bool)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        same |= p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] == c
    iso = ~same & region
    return round(float(iso.sum()) / max(1, int(region.sum())), 4)


def static_checks(sc, rgba, flat):
    layers, walk, spr = sc["layers"], sc["walk"], sc["spr"]
    v = {}
    v["canvas_640x360_all_layers"] = all(rgba[n].shape == (H, W, 4) for n in LAYERS)
    v["base_layer_opaque"] = bool((rgba["north-groves"][..., 3] == 255).all())
    v["binary_alpha_all_layers"] = all(bool(np.isin(rgba[n][..., 3], (0, 255)).all()) for n in LAYERS)
    used = set()
    for n in ART_LAYERS:
        used |= set(np.unique(layers[n][layers[n] >= 0]).tolist())
    v["art_layers_palette_only"] = all(0 <= u < N_ART for u in used)
    flat_cols = {tuple(c) for c in np.unique(flat[..., :3].reshape(-1, 3), axis=0).tolist()}
    v["flat_colours_subset_of_palette"] = flat_cols <= {tuple(c) for c in RGB[:N_ART].tolist()}
    v["flat_opaque"] = bool((flat[..., 3] == 255).all())
    v["heroine_48_logical_px"] = spr.shape[0] == 48
    fails, worst, worst_at = visibility(walk, rgba, sc["spr_alpha"])
    v["every_walkable_foot_keeps_one_third_visible"] = not fails
    da = depth_audit(sc["items"], walk, sc["spr_alpha"])
    v["depth_audit_zero_wrong_order_feet"] = all(d["wrong_order_feet"] == 0 for d in da.values())
    v["walkable_never_in_backdrop"] = not bool(walk[:WALK_TOP].any())
    m = park_masks()
    v["walkable_only_on_paving"] = not bool((walk & ~m["path"]).any())
    v["walkable_never_in_fountain_basin"] = not bool((walk & m["basin"]).any())
    ys_ok = {}
    for key, layer, behind in YSORT_CASES:
        foot = PINS[key]
        st = runtime_stack_still(rgba, spr, foot)
        sm = rgba[layer][..., 3] == 255
        hm = np.zeros((H, W), bool)
        sh, sw = spr.shape[:2]
        x0, y0 = foot[0] - sw // 2, foot[1] - sh + 1
        hm[y0:y0 + sh, x0:x0 + sw] = spr[..., 3] == 255
        both = sm & hm
        n = int(both.sum())
        on_top = int((st[both] == rgba[layer][both]).all(axis=1).sum())
        ys_ok[key] = {"layer": layer, "behind": behind, "overlap_texels": n, "sprite_on_top_texels": on_top,
                      "ok": n > 0 and ((on_top == n) if behind else (on_top < n)),
                      "walkable": bool(walk[foot[1], foot[0]])}
    v["ysort_behind_front_correct"] = all(c["ok"] and c["walkable"] for c in ys_ok.values())
    reach = flood(walk, PINS["spawn_south"])
    pins_ok = {k: bool(reach[y, x]) for k, (x, y) in PINS.items()}
    v["all_pins_reachable_from_spawn"] = all(pins_ok.values())
    v["pins_on_walkable_texels"] = all(bool(walk[y, x]) for (x, y) in PINS.values())
    rpts = route_points()
    blocked = [p for p in rpts if not walk[p[1], p[0]]]
    v["heroine_route_fully_walkable"] = not blocked
    fl_walk, fl_ex = isolated_bright(flat, YY >= 150)
    fl_all, _ = isolated_bright(flat)
    v["no_isolated_bright_flecks_in_walkable_park"] = fl_walk == 0
    walk_area = (YY >= 150)
    islands = {"park_rows_150_359": single_texel_islands(flat, walk_area),
               "backdrop_rows_0_149": single_texel_islands(flat, YY < 150)}
    return {"verdicts": v, "visibility_worst": round(float(worst), 3), "visibility_worst_at": worst_at,
            "visibility_fail_count": len(fails), "visibility_fail_examples": fails[:10], "depth_audit": da,
            "ysort_cases": ys_ok, "pins_reachable": pins_ok, "route_points": len(rpts),
            "route_blocked_examples": blocked[:10],
            "isolated_bright_flecks": {"park_rows_150_359": fl_walk, "examples": fl_ex, "whole_frame": fl_all},
            "single_texel_colour_islands_share": islands,
            "palette": {"art_colours": N_ART, "used_in_flat": len(flat_cols)},
            "despeckled_ground_texels": sc["despeckled_ground_texels"],
            "walkable_texels": int(walk.sum()), "walkable_share_of_park_rows": round(
                float(walk[WALK_TOP:].sum()) / ((H - WALK_TOP) * W), 3)}


# ============================================================================ build
def artefacts(sc):
    layers = sc["layers"]
    rgba = {n: to_rgba(layers[n]) for n in LAYERS}
    flat = composite_rgba(rgba, ART_LAYERS)
    comp_png = png_bytes(flat)
    files = {"pxo": make_pxo(rgba, comp_png), "ora": make_ora(rgba, comp_png), "gpl": make_gpl(),
             "flat": comp_png, "walkmask": walkmask_png(sc["walk"])}
    return rgba, flat, files


def names():
    return {"pxo": fname("scene-18layer", "pxo"), "ora": fname("scene-18layer", "ora"),
            "gpl": fname("scene-palette", "gpl"), "walk": fname("scene-walkability", "json"),
            "walkmask": fname("scene-walkmask", "png"), "flat": fname("scene-flat-640x360", "png"),
            "manifest": fname("scene-manifest", "json"),
            "cap_axis": fname("godot-render-1280x720-axis", "png"),
            "cap_behind-fountain": fname("godot-render-1280x720-behind-fountain", "png"),
            "cap_behind-tree": fname("godot-render-1280x720-behind-tree", "png"),
            "report": fname("technical-check-report", "json")}


def walkability_json(sc):
    walk = sc["walk"]
    cells = []
    for cy in range(0, H, 8):
        row = ""
        for cx in range(0, W, 8):
            c = walk[cy:cy + 8, cx:cx + 8]
            row += "1" if c.all() else ("p" if c.any() else "0")
        cells.append(row)
    return {"candidate": RUN, "status": "UNAPPROVED test-only pilot; not wired to any runtime scene",
            "canvas": [W, H], "grid_px": 8,
            "cells_legend": {"1": "every foot texel walkable", "p": "partly walkable", "0": "not walkable"},
            "cells_rows_top_to_bottom": cells, "walk_top_row": WALK_TOP,
            "collision_mask_png": names()["walkmask"], "foot_rule": "a foot texel is walkable iff the mask is opaque",
            "pins": {k: list(v) for k, v in PINS.items()},
            "ysort_pivots": YSORT_PIVOTS,
            "runtime_draw_order_proposal": "base (layers 1-9 merged) -> Y-sorted {7 *-ysort layers, actor} by pivot "
                                           "row (actor last on ties) -> fg-occlusion",
            "collars_blocked_texels": {k: int((v & ~walk).sum()) for k, v in sc["collars"].items()},
            "exits": {"exit_broadway_gate": "west park gate onto the Broadway sidewalk (transition trigger)",
                      "exit_park_row": "south plaza east end toward Park Row (transition trigger)",
                      "city_hall_gate": "scanner piers on the axis; interaction, the forecourt is not walkable"},
            "heroine_route": [PINS[p] if isinstance(p, str) else p for p in ROUTE]}


def write_new(path, data):
    if os.path.exists(_fs(path)):
        if read_bytes(path) != data:
            raise SystemExit(f"refusing to overwrite a different existing file: {path}")
        return "unchanged"
    with open(_fs(path), "xb") as f:
        f.write(data)
    return "written"


def build_all():
    sc = scene()
    rgba, flat, files = artefacts(sc)
    return sc, rgba, flat, files


def preview(outdir):
    sc, rgba, flat, files = build_all()
    os.makedirs(outdir, exist_ok=True)
    Image.fromarray(flat, "RGBA").save(os.path.join(outdir, "flat.png"))
    Image.fromarray(x2(flat), "RGBA").save(os.path.join(outdir, "flat_x2.png"))
    spr = sc["spr"]
    for key in set(CAPTURES.values()) | {"spawn_south", "city_hall_gate", "statue_behind", "lamp_n_behind"}:
        st = runtime_stack_still(rgba, spr, PINS[key])
        Image.fromarray(x2(st), "RGBA").save(os.path.join(outdir, f"still_{key}_x2.png"))
    g = composite_rgba(rgba, ART_LAYERS + ["guides"])
    Image.fromarray(x2(g), "RGBA").save(os.path.join(outdir, "guides_x2.png"))
    for n in LAYERS:
        Image.fromarray(rgba[n], "RGBA").save(os.path.join(outdir, f"layer_{n}.png"))
    rep = static_checks(sc, rgba, flat)
    with open(os.path.join(outdir, "checks.json"), "w") as f:
        json.dump(rep, f, indent=1, default=str)
    print(json.dumps({k: v for k, v in rep.items() if k not in ("depth_audit",)}, indent=1, default=str))


def manifest(sc, rgba, files, rep):
    nm = names()
    return {
        "project": SLUG, "area": AREA, "run": RUN, "version": "v01",
        "status": "UNAPPROVED test-only walkable pilot (one 640x360 camera composition). Not accepted art, not "
                  "runtime-integrated. Acceptance is creator review only; science scene art stays 0/11.",
        "art_approved": False, "runtime_integrated": False, "counters_changed": False,
        "authoring_route": {
            "method": "deterministic Python tool with hand-written placement tables, authored and run by Claude "
                      "(Claude Code, claude.ai Max subscription, firstParty; no API key, no image model, no paid "
                      "fallback); writes a native pxo_version 7 .pxo and an .ora with 18 named layers",
            "pixelorama_gui_paint_pass": False,
            "disclosure": "no desktop/computer-use access to the Pixelorama GUI in this session",
            "concept_usage": "geography / path / zone cues only, read by eye; the tool never opens the concept "
                             "image, no continuous-colour pixels or generated figures are used",
            "concept_reference": CONCEPT_REL, "audit_reference": AUDIT_REL},
        "canvas": {"w": W, "h": H, "camera": "top-down 3/4; top = north (City Hall), bottom = south",
                   "gameplay_camera": "exactly one 640x360 logical viewport (window 1280x720, integer 2x)",
                   "scale_reference": {"file": HEROINE_REL, "logical_height_px": int(sc["spr"].shape[0])},
                   "forced_perspective": "backdrop rows 0..169 (City Hall at reduced scale, forecourt, flank trees) "
                                         "is not walkable; walkable park rows 172..359 at heroine scale"},
        "layers_bottom_to_top": [
            {"index": i + 1, "name": n, "visible": n != "guides", "locked": n == "guides",
             "runtime_export": ("merged into base" if n in BASE_LAYERS else
                                f"Y-sorted sprite layer, pivot row {YSORT_PIVOTS[n]}" if n in YSORT_PIVOTS else
                                "overlay above actors" if n == "fg-occlusion" else "never exported (hidden guides)"),
             "opaque_texels": int((rgba[n][..., 3] == 255).sum())} for i, n in enumerate(LAYERS)],
        "palette": [{"name": n, "hex": "#" + h} for n, h in PALETTE],
        "guide_palette": [{"name": n, "hex": "#" + h} for n, h in GUIDE_PALETTE],
        "pins": {k: list(v) for k, v in PINS.items()},
        "static_checks": rep,
        "files_sha256_bytes": {nm[k]: sha(v) for k, v in files.items()},
        "tool": {"file": TOOL_REL, "sha256_text_lf_v1": sha_text(read_bytes(os.path.abspath(__file__))),
                 "python": sys.version.split()[0], "pillow": Image.__version__, "numpy": np.__version__},
    }


def build():
    sc, rgba, flat, files = build_all()
    if build_all()[3] != files:
        raise SystemExit("build is not deterministic")
    rep = static_checks(sc, rgba, flat)
    cand = rp(CAND_REL)
    os.makedirs(_fs(cand), exist_ok=True)
    nm = names()
    for k in ("pxo", "ora", "flat", "gpl", "walkmask"):
        print(write_new(os.path.join(cand, nm[k]), files[k]), nm[k])
    files["walk"] = (json.dumps(walkability_json(sc), indent=1) + "\n").encode()
    print(write_new(os.path.join(cand, nm["walk"]), files["walk"]), nm["walk"])
    man = manifest(sc, rgba, files, rep)
    print(write_new(os.path.join(cand, nm["manifest"]), (json.dumps(man, indent=2, default=str) + "\n").encode()),
          nm["manifest"])
    print(json.dumps(rep["verdicts"], indent=1))
    return 0


# ============================================================================ Pixelorama gate (isolated APPDATA)
def snapshot_dir(root):
    snap = {}
    if root and os.path.isdir(root):
        for d, _, fs in os.walk(root):
            for f in fs:
                p = os.path.join(d, f)
                try:
                    st = os.stat(p)
                    snap[os.path.relpath(p, root).replace("\\", "/")] = (st.st_size, st.st_mtime_ns)
                except OSError:
                    snap[os.path.relpath(p, root).replace("\\", "/")] = None
    return snap


def run_isolated(exe, args, fake_appdata, real_root):
    """Pixelorama headless with APPDATA pointed at a temp dir. Kill-switch: if anything in the real
    %APPDATA%\\pixelorama other than the GUI's own .running heartbeat changes, or .running disappears."""
    env = dict(os.environ)
    env["APPDATA"] = fake_appdata
    before = snapshot_dir(real_root)
    t0 = time.time()
    p = subprocess.Popen([exe, "--headless", "--quit", "--"] + args, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    killed, marker_missing = False, False
    while p.poll() is None:
        now = snapshot_dir(real_root)
        changed = {k for k in set(before) | set(now) if before.get(k) != now.get(k) and k != ".running"}
        if ".running" in before and ".running" not in now:
            marker_missing = True
        if changed or marker_missing or time.time() - t0 > 240:
            p.kill(); killed = True
            break
        time.sleep(0.01)
    so, se = p.communicate()
    after = snapshot_dir(real_root)
    noise = ("shader_compiler", "custom_samplers", "Condition \"!actions")
    tail = [l for l in so.splitlines() + se.splitlines() if l.strip() and not any(s in l for s in noise)]
    return {"args": [os.path.basename(a) if os.path.isabs(a) else a for a in args], "exit_code": p.returncode,
            "seconds": round(time.time() - t0, 1), "killed_by_guard": killed,
            "fake_user_dir_created": os.path.isdir(os.path.join(fake_appdata, "pixelorama")),
            "real_dir_changed_except_running": sorted(k for k in set(before) | set(after)
                                                      if before.get(k) != after.get(k) and k != ".running"),
            "real_running_marker_present_after": (".running" in after) if ".running" in before else None,
            "output_tail": tail[-5:]}


def pixelorama_gate(exe, files, rgba, flat):
    real_root = os.path.join(os.environ.get("APPDATA", ""), "pixelorama")
    rep = {"pixelorama": exe, "pixelorama_sha256": sha(read_bytes(exe)),
           "isolation": "APPDATA redirected to a fresh temp dir per run; real %APPDATA%\\pixelorama polled every "
                        "10 ms with a kill-switch", "steps": {}}
    tmp = tempfile.mkdtemp(prefix="wb-chpgate-")
    try:
        src = {}
        for k in ("pxo", "ora"):
            src[k] = os.path.join(tmp, f"src.{k}")
            with open(_fs(src[k]), "wb") as f:
                f.write(files[k])
        flats = []
        for label, k, split in (("pxo_flat_1", "pxo", False), ("pxo_flat_2", "pxo", False),
                                ("pxo_split", "pxo", True), ("ora_flat", "ora", False), ("ora_split", "ora", True)):
            d = os.path.join(tmp, label); os.makedirs(d)
            fake = os.path.join(tmp, "appdata_" + label); os.makedirs(fake)
            args = ["--export"] + (["--split-layers"] if split else []) + ["-o", os.path.join(d, "f.png"), src[k]]
            r = run_isolated(exe, args, fake, real_root)
            r["pngs"] = sorted(f for f in os.listdir(_fs(d)) if f.lower().endswith(".png"))
            r["source_copy_unchanged"] = read_bytes(src[k]) == files[k]
            if not split and len(r["pngs"]) == 1:
                b = read_bytes(os.path.join(d, r["pngs"][0]))
                a = decode(b)[2]
                r["png_sha256"] = sha(b)
                r["flat_equals_expected"] = a.shape == flat.shape and bool((a == flat).all())
                r["differing_texels"] = int((a != flat).any(axis=2).sum()) if a.shape == flat.shape else None
                if k == "pxo":
                    flats.append(b)
            if split:
                got = []
                for f in r["pngs"]:
                    a = decode(read_bytes(os.path.join(d, f)))[2]
                    hit = [n for n in LAYERS if a.shape == rgba[n].shape and a.tobytes() == rgba[n].tobytes()]
                    got.append({"file": f, "exact_layer_match": hit,
                                "semi_alpha": int(((a[..., 3] > 0) & (a[..., 3] < 255)).sum())})
                r["split"] = got
                matched = [h for g in got for h in g["exact_layer_match"]]
                r["art_layers_all_exact"] = all(n in matched for n in ART_LAYERS)
                r["guides_exported"] = "guides" in matched or any("guides" in g["file"] for g in got)
                order = {n: i for i, n in enumerate(LAYERS)}
                stack = sorted((order[g["exact_layer_match"][0]], g["file"]) for g in got
                               if g["exact_layer_match"] and g["exact_layer_match"][0] != "guides")
                if stack:
                    comp = decode(read_bytes(os.path.join(d, stack[0][1])))[2].copy()
                    for _, f in stack[1:]:
                        a = decode(read_bytes(os.path.join(d, f)))[2]
                        m = a[..., 3] == 255
                        comp[m] = a[m]
                    r["split_composite_equals_flat"] = bool((comp == flat).all())
            rep["steps"][label] = r
        rep["pxo_flat_runs_identical"] = len(flats) == 2 and flats[0] == flats[1]
    finally:
        shutil.rmtree(_fs(tmp), ignore_errors=True)
    st = rep["steps"]
    rep["verdicts"] = {
        "pixelorama_isolation_held": all(not v["killed_by_guard"] and not v["real_dir_changed_except_running"]
                                         and v["real_running_marker_present_after"] is not False
                                         for v in st.values()),
        "pixelorama_pxo_flat_exact": all(st[k].get("flat_equals_expected") for k in ("pxo_flat_1", "pxo_flat_2")),
        "pixelorama_pxo_flat_deterministic": rep["pxo_flat_runs_identical"],
        "pixelorama_pxo_split_layers_exact": st["pxo_split"].get("art_layers_all_exact", False),
        "pixelorama_pxo_split_composite_equals_flat": st["pxo_split"].get("split_composite_equals_flat", False),
        "pixelorama_ora_flat_exact": st["ora_flat"].get("flat_equals_expected", False),
        "pixelorama_ora_split_layers_exact": st["ora_split"].get("art_layers_all_exact", False),
        "pixelorama_sources_unchanged": all(v["source_copy_unchanged"] for v in st.values()),
        "pixelorama_split_does_not_export_hidden_guides": not any(st[k].get("guides_exported")
                                                                  for k in ("pxo_split", "ora_split")),
    }
    return rep


# ============================================================================ Godot gates (throwaway temp projects)
GODOT_TEXEL_SCRIPT = r'''extends SceneTree
# Test-only, nonruntime (headless): load the split layer PNGs from the .ora with Image.load_from_file, hash raw RGBA,
# walk the heroine route on the exported collision mask, and composite a runtime-stack still (base -> Y-sorted
# {sprite layers, actor} by pivot row -> fg-occlusion) at every sampled route foot; report SHA-256 per still.
func _init():
	var a = OS.get_cmdline_user_args()
	var dir: String = a[0]
	var cases = JSON.parse_string(FileAccess.get_file_as_string(dir + "/cases.json"))
	var out = {"layers": {}, "stills": {}}
	var imgs = {}
	for n in cases["art_layers"]:
		var img = Image.load_from_file(dir + "/" + n + ".png")
		if img.get_format() != Image.FORMAT_RGBA8:
			img.convert(Image.FORMAT_RGBA8)
		var h = HashingContext.new()
		h.start(HashingContext.HASH_SHA256)
		h.update(img.get_data())
		out["layers"][n] = {"w": img.get_width(), "h": img.get_height(), "sha256_rgba": h.finish().hex_encode()}
		imgs[n] = img
	var hero = Image.load_from_file(dir + "/heroine48.png")
	hero.convert(Image.FORMAT_RGBA8)
	out["heroine_h"] = hero.get_height()
	var mask = Image.load_from_file(dir + "/walkmask.png")
	var blocked = 0
	var jumps = 0
	var prev = null
	for p in cases["route"]:
		if mask.get_pixel(int(p[0]), int(p[1])).a < 0.5:
			blocked += 1
		if prev != null and (absi(int(p[0]) - int(prev[0])) > 1 or absi(int(p[1]) - int(prev[1])) > 1):
			jumps += 1
		prev = p
	out["route_points"] = cases["route"].size()
	out["route_blocked"] = blocked
	out["route_jumps"] = jumps
	var base = imgs[cases["base_layers"][0]].duplicate()
	for i in range(1, cases["base_layers"].size()):
		base.blend_rect(imgs[cases["base_layers"][i]], Rect2i(0, 0, 640, 360), Vector2i(0, 0))
	for key in cases["feet"].keys():
		var foot = cases["feet"][key]
		var st = base.duplicate()
		var hp = Vector2i(int(foot[0]) - hero.get_width() / 2, int(foot[1]) - hero.get_height() + 1)
		var placed = false
		for sp in cases["ysort_sprites"]:
			if not placed and int(foot[1]) < int(sp[1]):
				st.blend_rect(hero, Rect2i(0, 0, hero.get_width(), hero.get_height()), hp)
				placed = true
			st.blend_rect(imgs[sp[0]], Rect2i(0, 0, 640, 360), Vector2i(0, 0))
		if not placed:
			st.blend_rect(hero, Rect2i(0, 0, hero.get_width(), hero.get_height()), hp)
		st.blend_rect(imgs["fg-occlusion"], Rect2i(0, 0, 640, 360), Vector2i(0, 0))
		var hs = HashingContext.new()
		hs.start(HashingContext.HASH_SHA256)
		hs.update(st.get_data())
		out["stills"][key] = hs.finish().hex_encode()
	var f = FileAccess.open(dir + "/godot_report.json", FileAccess.WRITE)
	f.store_string(JSON.stringify(out))
	f.close()
	print("GODOT_TEXEL_GATE_DONE")
	quit()
'''

GODOT_RENDER_SCRIPT = r'''extends SceneTree
# Test-only, nonruntime (WINDOWED, real GL Compatibility renderer): Sprite2D per base layer, a y_sort_enabled Node2D
# holding the seven Y-sorted layers (position.y = pivot, offset.y = -pivot) and the heroine (position = foot, added
# last so she wins ties), then the fg-occlusion overlay. 640x360 viewport, 1280x720 window, integer canvas_items
# stretch, nearest filtering. Captures the root viewport at each requested foot.
func _initialize():
	_run()

func _spr(path: String) -> Sprite2D:
	var s = Sprite2D.new()
	s.centered = false
	s.texture = ImageTexture.create_from_image(Image.load_from_file(path))
	return s

func _run():
	var a = OS.get_cmdline_user_args()
	var dir: String = a[0]
	var cases = JSON.parse_string(FileAccess.get_file_as_string(dir + "/cases.json"))
	var world = Node2D.new()
	world.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	root.add_child(world)
	for n in cases["base_layers"]:
		world.add_child(_spr(dir + "/" + n + ".png"))
	var ys = Node2D.new()
	ys.y_sort_enabled = true
	world.add_child(ys)
	for sp in cases["ysort_sprites"]:
		var s = _spr(dir + "/" + sp[0] + ".png")
		s.position = Vector2(0, int(sp[1]))
		s.offset = Vector2(0, -int(sp[1]))
		ys.add_child(s)
	var himg = Image.load_from_file(dir + "/heroine48.png")
	var hero = Sprite2D.new()
	hero.centered = false
	hero.texture = ImageTexture.create_from_image(himg)
	hero.offset = Vector2(-(himg.get_width() / 2), -himg.get_height() + 1)
	ys.add_child(hero)
	world.add_child(_spr(dir + "/fg-occlusion.png"))
	var out = {"captures": {}}
	for key in cases["captures"].keys():
		var foot = cases["captures"][key]
		hero.position = Vector2(int(foot[0]), int(foot[1]))
		for i in range(4):
			await process_frame
		await RenderingServer.frame_post_draw
		var img = root.get_texture().get_image()
		img.convert(Image.FORMAT_RGBA8)
		img.save_png(dir + "/render_" + key + ".png")
		out["captures"][key] = [img.get_width(), img.get_height()]
	out["window_size"] = [root.size.x, root.size.y]
	var f = FileAccess.open(dir + "/render_report.json", FileAccess.WRITE)
	f.store_string(JSON.stringify(out))
	f.close()
	print("GODOT_RENDER_GATE_DONE")
	quit()
'''

RENDER_PROJECT = """config_version=5

[application]
config/name="{name}"

[display]
window/size/viewport_width=640
window/size/viewport_height=360
window/size/window_width_override=1280
window/size/window_height_override=720
window/stretch/mode="canvas_items"
window/stretch/scale_mode="integer"

[rendering]
renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
textures/canvas_textures/default_texture_filter=0
"""


def godot_inputs(data, files, spr, walk):
    with zipfile.ZipFile(io.BytesIO(files["ora"])) as z:
        for n in ART_LAYERS:
            with open(os.path.join(data, f"{n}.png"), "wb") as f:
                f.write(z.read(f"data/{n}.png"))
    Image.fromarray(spr, "RGBA").save(os.path.join(data, "heroine48.png"))
    with open(os.path.join(data, "walkmask.png"), "wb") as f:
        f.write(files["walkmask"])


def godot_gates(godot, files, rgba, sc):
    spr, walk = sc["spr"], sc["walk"]
    rep = {"godot": GODOT_REL, "godot_sha256": sha(read_bytes(godot)), "texel_gate": {}, "render_gate": {}}
    caps = {}
    rpts = route_points()
    feet = {f"r{i:04d}": list(p) for i, p in enumerate(rpts) if i % 6 == 0}
    feet.update({k: list(PINS[k]) for k in PINS})
    ysl = sorted(([n, YSORT_PIVOTS[n]] for n in YSORT_LAYERS), key=lambda t: t[1])
    tmp = tempfile.mkdtemp(prefix="wb-chpgodot-")
    try:
        # ---- headless texel gate
        proj = os.path.join(tmp, "p1"); os.makedirs(proj)
        data = os.path.join(tmp, "d1"); os.makedirs(data)
        fake = os.path.join(tmp, "ad1"); os.makedirs(fake)
        with open(os.path.join(proj, "project.godot"), "w", newline="\n") as f:
            f.write(f'config_version=5\n\n[application]\nconfig/name="chp-texel-{RUN_ID}"\n')
        with open(os.path.join(proj, "gate.gd"), "w", newline="\n") as f:
            f.write(GODOT_TEXEL_SCRIPT)
        godot_inputs(data, files, spr, walk)
        with open(os.path.join(data, "cases.json"), "w") as f:
            json.dump({"art_layers": ART_LAYERS, "base_layers": BASE_LAYERS, "feet": feet, "route": rpts,
                       "ysort_sprites": ysl}, f)
        env = dict(os.environ); env["APPDATA"] = fake
        p = subprocess.run([godot, "--headless", "--path", proj, "--script", "gate.gd", "--", data],
                           capture_output=True, text=True, timeout=900, env=env, encoding="utf-8", errors="replace")
        t = rep["texel_gate"]
        t["exit_code"] = p.returncode
        t["printed_done"] = "GODOT_TEXEL_GATE_DONE" in p.stdout
        gr = json.load(open(os.path.join(data, "godot_report.json")))
        lay_ok = {n: gr["layers"][n]["w"] == W and gr["layers"][n]["h"] == H and
                  gr["layers"][n]["sha256_rgba"] == sha(np.ascontiguousarray(rgba[n]).tobytes()) for n in ART_LAYERS}
        st_bad = []
        for k, foot in feet.items():
            exp = runtime_stack_still(rgba, spr, tuple(foot))
            if gr["stills"].get(k) != sha(np.ascontiguousarray(exp).tobytes()):
                st_bad.append(k)
        t.update({"layers_exact": lay_ok, "stills_compared": len(feet), "stills_mismatched": st_bad[:20],
                  "route_points": gr["route_points"], "route_blocked_on_exported_mask": gr["route_blocked"],
                  "route_jumps_over_1px": gr["route_jumps"], "heroine_h": gr["heroine_h"]})
        # ---- windowed render gate (real renderer)
        proj2 = os.path.join(tmp, "p2"); os.makedirs(proj2)
        data2 = os.path.join(tmp, "d2"); os.makedirs(data2)
        fake2 = os.path.join(tmp, "ad2"); os.makedirs(fake2)
        pname = f"chp-render-{RUN_ID}"
        with open(os.path.join(proj2, "project.godot"), "w", newline="\n") as f:
            f.write(RENDER_PROJECT.format(name=pname))
        with open(os.path.join(proj2, "gate.gd"), "w", newline="\n") as f:
            f.write(GODOT_RENDER_SCRIPT)
        godot_inputs(data2, files, spr, walk)
        capfeet = {k: list(PINS[v]) for k, v in CAPTURES.items()}
        with open(os.path.join(data2, "cases.json"), "w") as f:
            json.dump({"base_layers": BASE_LAYERS, "ysort_sprites": ysl, "captures": capfeet}, f)
        env2 = dict(os.environ); env2["APPDATA"] = fake2
        p2 = subprocess.run([godot, "--path", proj2, "--script", "gate.gd", "--", data2],
                            capture_output=True, text=True, timeout=300, env=env2, encoding="utf-8", errors="replace")
        r = rep["render_gate"]
        r["exit_code"] = p2.returncode
        r["printed_done"] = "GODOT_RENDER_GATE_DONE" in p2.stdout
        rr = json.load(open(os.path.join(data2, "render_report.json")))
        r["window_size"] = rr.get("window_size")
        r["captures"] = {}
        for k, foot in capfeet.items():
            b = read_bytes(os.path.join(data2, f"render_{k}.png"))
            got = decode(b)[2]
            exp = x2(runtime_stack_still(rgba, spr, tuple(foot)))
            same_shape = got.shape == exp.shape
            diff = int((got[..., :3] != exp[..., :3]).any(axis=2).sum()) if same_shape else None
            r["captures"][k] = {"foot": foot, "size": list(got.shape[1::-1]), "equals_python_2x_stack": diff == 0,
                                "differing_pixels": diff}
            caps["cap_" + k] = b
        r["godot_wrote_nothing_outside_temp"] = not any(os.path.isdir(os.path.join(
            os.environ.get("APPDATA", ""), "Godot", "app_userdata", n)) for n in (pname, f"chp-texel-{RUN_ID}"))
    finally:
        shutil.rmtree(_fs(tmp), ignore_errors=True)
    t, r = rep["texel_gate"], rep["render_gate"]
    rep["verdicts"] = {
        "godot_loads_layers_exact": all(t["layers_exact"].values()) and t["exit_code"] == 0,
        "godot_route_walkable_on_exported_mask": t["route_blocked_on_exported_mask"] == 0
                                                 and t["route_jumps_over_1px"] == 0,
        "godot_route_stills_match_ysort_and_occlusion": not t["stills_mismatched"],
        "godot_heroine_48_px": t["heroine_h"] == 48,
        "godot_render_1280x720": all(c["size"] == [W * VIEW, H * VIEW] for c in r["captures"].values()),
        "godot_render_equals_python_2x": all(c["equals_python_2x_stack"] for c in r["captures"].values()),
        "godot_wrote_nothing_outside_temp": r["godot_wrote_nothing_outside_temp"],
    }
    return rep, caps


# ============================================================================ check
def check(exe, write_report, use_pixelorama, godot=None):
    sc, rgba, flat, files = build_all()
    nm = names()
    cand = rp(CAND_REL)
    for k in ("pxo", "ora", "flat", "gpl", "walkmask"):
        if read_bytes(os.path.join(cand, nm[k])) != files[k]:
            raise SystemExit(f"{nm[k]} on disk differs from a fresh rebuild")
    st = static_checks(sc, rgba, flat)
    rep = {"run": RUN, "gates": dict(st["verdicts"]), "static": st}
    gates = rep["gates"]
    with zipfile.ZipFile(io.BytesIO(files["pxo"])) as z:
        dj = json.loads(z.read("data.json"))
    gates["pxo_layer_stack_is_18_named_layers"] = [l["name"] for l in dj["layers"]] == LAYERS and \
        [l["visible"] for l in dj["layers"]] == [n != "guides" for n in LAYERS] and len(LAYERS) == 18
    gates["build_deterministic"] = build_all()[3] == files
    caps = {}
    if use_pixelorama:
        rep["pixelorama"] = pixelorama_gate(exe, files, rgba, flat)
        gates.update(rep["pixelorama"]["verdicts"])
    if godot:
        rep["godot"], caps = godot_gates(godot, files, rgba, sc)
        gates.update(rep["godot"]["verdicts"])
    rep["result"] = "PASS" if all(gates.values()) else "FAIL"
    rep["note"] = "Technical gates only. Passing them does not make the art accepted; acceptance is creator review."
    text = json.dumps(rep, indent=2, default=str) + "\n"
    print(json.dumps({"result": rep["result"], "gates": gates}, indent=1))
    if write_report:
        out = rp(OUT_REL)
        os.makedirs(_fs(out), exist_ok=True)
        print(write_new(os.path.join(out, nm["report"]), text.encode()), nm["report"])
        for k, b in caps.items():
            print(write_new(os.path.join(out, nm[k]), b), nm[k])
    return 0 if rep["result"] == "PASS" else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["preview", "build", "check"])
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--write-report", action="store_true")
    ap.add_argument("--no-pixelorama", action="store_true")
    ap.add_argument("--no-godot", action="store_true")
    ap.add_argument("--pixelorama", default=PIXELORAMA_DEFAULT)
    a = ap.parse_args()
    if a.mode == "preview":
        if not a.dir or os.path.abspath(a.dir).startswith(REPO):
            raise SystemExit("preview needs a directory outside the repo")
        preview(a.dir)
    elif a.mode == "build":
        build()
    else:
        sys.exit(check(a.pixelorama, a.write_report, not a.no_pixelorama, None if a.no_godot else rp(GODOT_REL)))


if __name__ == "__main__":
    main()
