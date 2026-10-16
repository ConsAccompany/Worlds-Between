"""UNAPPROVED, TEST-ONLY v02 candidate: U.S. Capitol West Front + Dome as a separate CINEMATIC VISTA (Washington, 2537).

Deterministic Python tool authored and run by Claude (Claude Code, Opus 5.5). It writes ONE 1280x720 logical-pixel
non-walkable vista from a fixed palette into a 15-layer editable stack, as a native Pixelorama .pxo (pxo_version 7) and
an .ora, plus a palette (.gpl) and a manifest. Nothing here is accepted art and nothing is wired into the game
runtime: no scene, data, test, default, camera setting, Game Bible, meter or docs/progress file is touched.

This is NOT a replacement of the walkable v04 west-grounds room and NOT an edit of the v01 establishing candidate.
v01 (run wdc-dome-west-v01_20261016-014650-feb222e8) is read-only: `check` re-hashes all of its files, its tool, its
QA note and the Codex audit, and also reads the v01 .pxo layers for the direct v01 -> v02 pixel comparison.

Why: the Codex v01 visual audit (docs/qa/...wdc-dome-west-v01-codex-visual-audit_unapproved-v01_20261016-044235-
74d1e7b0.md) found the 1280x720 frame dominated by a uniformly tiled foreground wall, a heroine nearly as tall as the
distant Capitol (scale conflict), the heroine and bright tripod on the central dome axis, and understated 2537 damage.

AUTHORING ROUTE (disclosed). NOT a Pixelorama GUI paint pass (no desktop/computer-use access to the GUI in this
session). Hand-written placement tables (every dome stage, facade bay, damage item, tree crown, rubble block and the
camera itself) are rasterised by this tool into named layers; Pixelorama 1.2.3 re-exports the .pxo/.ora headless and
the exports are compared texel by texel. The .pxo opens in the GUI as 15 editable layers for a GUI polish pass.

Camera (one consistent pinhole, documented so the heroine/building scale is checkable):
  viewpoint on the floor of the DRAINED Capitol Reflecting Pool near its west end, looking east along the Mall axis;
  focal length F = 2800 logical px (telephoto, ~25 deg horizontal FOV), eye EYE = 2.5 m above the pool floor,
  horizon row HZ = 430. Ground at distance d projects to row HZ + EYE*F/d.
  * Capitol West Front at ~900 m -> 3.11 px/m (2x v01). Terrace foot ~18 m above the pool floor -> row 380.
    Statue of Freedom tip row 76, so the Capitol spans rows 76..380 (42% of the frame height; v01: 21%).
  * heroine (approved v8 south idle, 48 logical px = 1.7 m) stands ON THE POOL FLOOR at d = 100 m: 28 px/m, feet row
    HZ + 2.5*2800/100 = 500, head row 452 (below the horizon and 72 rows below the Capitol's foot: no overlap, no
    scale conflict). She and the toned-down survey tripod stand in the LEFT third, >= 200 px off the dome axis.
Composition (asymmetric on purpose): a tall self-sown tree frames the left edge and the top-left sky; the right side
  stays low (rubble mound + toppled lamp), so the Capitol sits in open sky. A mist band at the hill foot separates
  the distant Capitol (cool hazed values) from the warm, full-contrast foreground. The pool floor is foreshortened
  9 m concrete panels, mostly buried in silt and meadow (heavier vegetation on the north/left side); a diagonal strip
  of exposed, cracked concrete leads from the bottom right to the survey pair, then the eye climbs to the dome.
2537 abandonment (game fiction), asymmetric but readable at 640x360: open hole with exposed ribs and rust in the south
  (right) dome shell; three missing south peristyle columns; a collapsed south-wing (House) roof corner with a tree
  growing from the breach and a debris cone; ivy curtains over the north wing (Senate); soot over broken windows; a
  breached south terrace balustrade; a drained, silted, self-seeded pool.
Reference forms: Architect of the Capitol dome and Olmsted terrace pages (text facts only; nothing copied).

Modes
  preview <dir>   render layers, flat image, Python runtime still and the 640x360 crop into <dir> (outside the repo)
  build           write the candidate files (.pxo/.ora/flat/.gpl/manifest; never overwrites a different file)
  check           technical gates + v01 lock + direct v01->v02 comparison; Pixelorama 1.2.3 headless round-trip
                  (APPDATA redirected to temp; --no-pixelorama to skip); Godot 4.7.2 throwaway temp project
                  (--no-godot to skip); --write-report writes the JSON report and the two Godot captures.
Run: python -I -B <this file> preview <tempdir> | build | check [--write-report] [--no-pixelorama] [--no-godot]
"""
import argparse, hashlib, io, json, math, os, shutil, subprocess, sys, tempfile, time, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
AREA = "wdc-dome-west"
VER = "unapproved-v02"
STAMP = "20261016-044903"
RUN_ID = "cdb4ebdb"
RUN = f"{AREA}-v02_{STAMP}-{RUN_ID}"
CAND_REL = f"game/assets/environments/candidates/{RUN}"
OUT_REL = f"outputs/{RUN}"
TOOL_REL = "tools/" + os.path.basename(os.path.abspath(__file__))
AUDIT_REL = ("docs/qa/rpg-2-star-ocean-the-second_wdc-dome-west-v01-codex-visual-audit_unapproved-v01_"
             "20261016-044235-74d1e7b0.md")
HEROINE_REL = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_"
               "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
V01_RUN = "wdc-dome-west-v01_20261016-014650-feb222e8"
_V01C = f"game/assets/environments/candidates/{V01_RUN}/rpg-2-star-ocean-the-second_wdc-dome-west_"
_V01O = f"outputs/{V01_RUN}/rpg-2-star-ocean-the-second_wdc-dome-west_"
_V01S = "_unapproved-v01_20261016-014650-feb222e8"
V01_PXO = f"{_V01C}scene-editable-15layer{_V01S}.pxo"
V01_CAPTURE = f"{_V01O}godot-establishing-1280x720-vista{_V01S}.png"
V01_LOCK = {  # sha256 (bytes) of every v01 file, taken before this tool existed (2026-10-16 04:49)
    f"{_V01C}scene-editable-15layer{_V01S}.ora": "bcd2d59582ee5a7ec91496b3d3b127367bf1d8522ce9890b3b54342403fa2c70",
    V01_PXO: "6ab72bda203d0a684f694f0005164f3256f9c60df6a857103d52f5ae1ec5d048",
    f"{_V01C}scene-flat-art{_V01S}.png": "819ff113f404d806441ff43bf5a95270c7f9f6acca153d5a03c8e10b94909902",
    f"{_V01C}scene-manifest{_V01S}.json": "587b9283dcc10e556d4aa434c50ac11b317774ce79991e1d4a5bba5adf4989c6",
    f"{_V01C}scene-palette{_V01S}.gpl": "2f41a9f24fa52daef5428309d8d1f3a93e5303126934463f747912441d6ddc6b",
    f"{_V01C}scene-walkability{_V01S}.json": "78a37d9aaa1324df9224f845ce9887c76f4431dade1ce6b0781f624a67ad0933",
    f"{_V01O}godot-cam640x360-tripod-behind{_V01S}.png":
        "1924f1fd2f8216ab1d4468b6b4920be035063bdb379e60bb11192d81690728b5",
    f"{_V01O}godot-cam640x360-vista-axis{_V01S}.png": "7385a8858b96e436046bdde38ba7bf00f773d06cbb5ecc0be154c605bc2fd47d",
    V01_CAPTURE: "868922fbcb890e5e7fbbc65886cbbca3e9e9c1d1065e2bcd00cbf4cb14ed8a66",
    f"{_V01O}technical-check-report{_V01S}.json": "7d1bc17a2ae2c13ed4c045c1a6f32b178181c9342f3fb6b1f159bd3e846d4e0a",
    "tools/rpg-2-star-ocean-the-second_wdc-capitol-dome-west_establishing-scene-candidate_pixelorama-build_"
    "unapproved-v01_20261016-014650-feb222e8.py": "9aef71e82486a9c062f1d8057a18fe7f4484e9ad5353d61efa09a307de692ce6",
    AUDIT_REL: "1db7057fa9c07ddb428b9c4a608aa98f54021e5365f45fd3d6ac13e06265e90f",
    "docs/qa/rpg-2-star-ocean-the-second_wdc-dome-west_establishing-composition_qa-note_unapproved-v01_"
    "20261016-014650-feb222e8.md": "3572e4287fa18575778b803bfe41bb6a500cc89a7b0880f347777da9932a776b",
}
PIXELORAMA_DEFAULT = "C:/Users/hkzha/AppData/Local/Programs/Pixelorama-1.2.3/Pixelorama-Windows-64bit/Pixelorama.exe"
PIXELORAMA_VERSION = "v1.2.3-stable"
GODOT_REL = "work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe"      # gitignored local tooling
W, H = 1280, 720
CAM_W, CAM_H = 640, 360           # game/project.godot logical viewport (window 1280x720, integer 2x)
WIN_LONG_PREFIX = "\\\\?\\"


def fname(purpose, ext):
    """AGENTS naming: project slug, area, purpose, version, timestamp and run id are all in the file name."""
    return f"{SLUG}_{AREA}_{purpose}_{VER}_{STAMP}-{RUN_ID}.{ext}"


EXPORT_STEM = f"{SLUG}_{AREA}_pixelorama-export_{VER}_{STAMP}-{RUN_ID}"

LAYERS = ["sky", "clouds", "dome", "west-front", "terrace-lawn", "capitol-damage", "capitol-grounds-trees",
          "hill-mist", "union-square-far", "pool-basin", "basin-vegetation", "foreground-debris", "survey-props",
          "fg-framing", "guides"]                                                       # bottom -> top
ART_LAYERS = LAYERS[:-1]                                                              # guides: hidden, locked
BASE_LAYERS = LAYERS[:13]                     # merged into one base at runtime; heroine above; fg-framing on top

# ============================================================================ palette (all new for the vista)
PALETTE = [
    ("ink", "15171c"),
    # sky (top -> horizon) and clouds
    ("sk0", "3f5268"), ("sk1", "4f6379"), ("sk2", "63778b"), ("sk3", "7a8d9d"), ("sk4", "94a4ae"),
    ("sk5", "afbabc"), ("sk6", "c8cbc2"), ("sk7", "d9d4c3"),
    ("cl0", "e6dfcc"), ("cl1", "c7c8bf"), ("cl2", "a3afb4"), ("cl3", "86959f"), ("cl4", "6c7d8c"),
    # distant marble / painted iron (900 m: shadows are hazed blue-grey, lights warm)
    ("dm0", "4f5a67"), ("dm1", "6a7480"), ("dm2", "8a929a"), ("dm3", "a9adab"), ("dm4", "c8c6bc"),
    ("dm5", "e2dccb"), ("dm6", "f3ecd9"),
    # bronze / iron, rust
    ("br0", "2e3540"), ("br1", "485261"), ("br2", "66717c"), ("ru0", "7a5642"), ("ru1", "9c6e4f"),
    # distant foliage (Capitol grounds, ~800 m), mid foliage (~300-600 m), mist
    ("vg0", "3f5550"), ("vg1", "52675d"), ("vg2", "67796a"), ("vg3", "7f8d78"), ("vg4", "9aa48c"),
    ("mg0", "2b3f36"), ("mg1", "3b5443"), ("mg2", "506b4f"), ("mg3", "6a855b"), ("mg4", "87a06a"),
    ("mi0", "b3bab6"), ("mi1", "c5c8c0"),
    # near foliage and grass
    ("f0", "16262a"), ("f1", "223d3a"), ("f2", "2f5644"),
    ("g0", "1f3324"), ("g1", "2c4a2c"), ("g2", "3d6234"), ("g3", "557a3c"), ("g4", "6f9145"), ("g5", "93ad55"),
    ("g6", "b9c26c"), ("d0", "7f7c45"), ("d1", "a99a5e"), ("d2", "c4b27a"),
    # pool concrete (near) and hazed far concrete
    ("p0", "4e4a45"), ("p1", "6b655c"), ("p2", "8a8274"), ("p3", "a69d8b"), ("p4", "c3b9a2"),
    ("q0", "9a9a92"), ("q1", "b0b1aa"),
    # silt / soil
    ("s0", "3a2c22"), ("s1", "5a4430"), ("s2", "7d6345"), ("s3", "a08458"), ("s4", "bfa478"),
    # granite / coping stone (near)
    ("m0", "45474f"), ("m1", "6a6b72"), ("m2", "8f8d8a"), ("m3", "b5b0a5"), ("m4", "d3ccbc"),
    # survey kit (toned down: no bright orange highlight), flowers
    ("o0", "7e3c1e"), ("o1", "b2602c"), ("k0", "232a36"), ("k1", "3a4656"), ("k2", "5a6a7c"), ("k3", "8d9cab"),
    ("c1", "4fb6bd"), ("fl", "b98fc2"), ("y0", "d9c25a"),
]
GUIDE_PALETTE = [("gd-axis", "ff285a"), ("gd-horizon", "3cdcff"), ("gd-third", "ffe600"), ("gd-pin", "ff78ff")]
ALL_PAL = PALETTE + GUIDE_PALETTE
I = {n: i for i, (n, _) in enumerate(ALL_PAL)}
RGB = np.array([[int(h[j:j + 2], 16) for j in (0, 2, 4)] for _, h in ALL_PAL], np.uint8)
N_ART = len(PALETTE)
LUMA = (RGB[:, :3].astype(np.int32) @ np.array([299, 587, 114])) // 1000


def R(*names):
    return [I[n] for n in names]


SKY = R("sk0", "sk1", "sk2", "sk3", "sk4", "sk5", "sk6", "sk7")
DOME = R("dm0", "dm1", "dm2", "dm3", "dm4", "dm5", "dm6")
VG = R("vg0", "vg1", "vg2", "vg3", "vg4")
MG = R("mg0", "mg1", "mg2", "mg3", "mg4")
NEAR = R("f0", "f1", "f2", "g2", "g3", "g4", "g5")
GR = R("g0", "g1", "g2", "g3", "g4", "g5", "g6")
CONC = R("p0", "p1", "p2", "p3", "p4")
SILT = R("s0", "s1", "s2", "s3", "s4")
STONE = R("m0", "m1", "m2", "m3", "m4")
WATER_OR_SKY = set(SKY + R("cl0", "cl1", "cl2", "cl3", "cl4", "c1"))

# haze recolouring (one step toward the mist), used by the hill-mist layer
HAZE = {"vg0": "vg2", "vg1": "vg3", "vg2": "vg3", "vg3": "vg4", "vg4": "mi0", "mg0": "vg1", "mg1": "vg2",
        "mg2": "vg3", "mg3": "vg4", "mg4": "mi0", "dm0": "dm2", "dm1": "dm3", "dm2": "dm3", "dm3": "dm4",
        "dm4": "mi1", "dm5": "mi1", "dm6": "dm5", "br0": "dm1", "br1": "dm2", "br2": "dm3", "ru0": "dm2",
        "ru1": "dm3", "mi0": "mi1", "mi1": "mi1", "s1": "vg2", "s2": "vg3", "s3": "vg4", "q0": "q1", "q1": "mi1",
        "p1": "q0", "p2": "q0", "p3": "q1", "m1": "dm2", "m2": "dm3", "m3": "dm4", "m4": "mi1", "d0": "vg3",
        "d1": "vg4", "sk5": "sk6", "sk6": "sk6", "sk7": "sk7", "k0": "dm0", "k1": "dm1", "o0": "ru0", "o1": "ru1"}
HAZE_LUT = np.arange(len(ALL_PAL), dtype=np.int16)
for _a, _b in HAZE.items():
    HAZE_LUT[I[_a]] = I[_b]

# cast-shadow colour for whatever a shadow falls on (opaque, no semi-alpha)
SHADE = {"p0": "s0", "p1": "p0", "p2": "p1", "p3": "p2", "p4": "p3", "q0": "p2", "q1": "q0",
         "s0": "ink", "s1": "s0", "s2": "s1", "s3": "s2", "s4": "s3", "g0": "f0", "g1": "g0", "g2": "g1",
         "g3": "g2", "g4": "g3", "g5": "g4", "g6": "g5", "d0": "g1", "d1": "d0", "d2": "d1",
         "mg0": "f1", "mg1": "mg0", "mg2": "mg1", "mg3": "mg2", "mg4": "mg3", "m0": "ink", "m1": "m0",
         "m2": "m1", "m3": "m2", "m4": "m3", "f0": "f0", "f1": "f0", "f2": "f1"}
SHADE_LUT = np.arange(len(ALL_PAL), dtype=np.int16)
for _a, _b in SHADE.items():
    SHADE_LUT[I[_a]] = I[_b]

# ============================================================================ camera + composition table (logical px)
CX = 640                          # Mall / Capitol axis (columns 0..1279 -> axis between 639 and 640)
F = 2800.0                        # focal length in logical px
EYE = 2.5                         # camera height above the pool floor, m
HZ = 430                          # horizon row
D_CAPITOL = 900.0                 # West Front distance, m -> 3.11 px/m
TERRACE_ELEV = 18.0               # terrace foot above the pool floor, m


def row_of(d, elev=0.0):
    return HZ + (EYE - elev) * F / d


def px_per_m(d):
    return F / d


# Capitol: every v01 table entry at 2x (v01 drew the Capitol at ~1.55 px/m, this vista at ~3.11 px/m)
TIP = 76
STATUE = (76, 95)
THOLOS_CAP = (96, 103)
THOLOS_COLS = (104, 119)
THOLOS_RING = (120, 125)
SHELL = (126, 181)
ATTIC = (182, 201)
PERI_BAL = (202, 205)
PERI_ENT = (206, 213)
PERI_COLS = (214, 247)
STYLOBATE = (248, 253)
DRUM = (254, 271)
HW = {"tholos_ring": 18, "tholos_cols": 12, "attic": 52, "peri_bal": 60, "peri_ent": 64, "peri_cols": 60,
      "stylobate": 66, "drum": 70}
SHELL_HW = (46, 14)               # shell half width at base / top
PERI_COLS_N = 36
PERI_MISSING = (4, 5, 6)          # game fiction: three missing columns on the south (right) side, index from centre
SECTIONS = [  # (name, x0, x1, roof row, kind, tone shift): West Front, symmetric about the axis (x0 + x1 = 1279)
    ("wingL", 286, 431, 270, "wing", 0), ("corrL", 432, 473, 274, "windows", -1),
    ("centerL", 474, 567, 266, "windows", 0), ("pavilion", 568, 711, 260, "loggia", 0),
    ("centerR", 712, 805, 266, "windows", 0), ("corrR", 806, 847, 274, "windows", -1),
    ("wingR", 848, 993, 270, "wing", 0),
]
FACADE_BOTTOM = 344
DECK = (346, 349)
TERRACE = (168, 1111)
TBAL = (350, 356)                 # rail 350-351, balusters 352-354, base rail 355-356
TWALL = (357, 374)
TGRANITE = (375, 380)
TERRACE_FOOT = 380
EXEDRA = (608, 671)
LANTERNS = (320, 524, 755, 959)
CAPITOL_BBOX_ROWS = (TIP, TERRACE_FOOT)

# figures on the pool floor (d = 100 m -> 28 px/m; 48 px heroine = 1.7 m)
D_FIGURES = 100.0
HEROINE_FOOT = (428, int(round(row_of(D_FIGURES))))          # (428, 500)
TRIPOD = (382, 498)                                          # pivot: front-feet contact row (2 m nearer than her)
TRIPOD_H = 44                                                # ~1.6 m at 28 px/m
CROP_640 = (320, 40)                                         # 640x360 landmark window: whole dome + West Front core

SHADOW_DIR = (-0.45, -0.30)       # late sun from the west-south-west behind the camera's right: shadows go up-left


# ============================================================================ helpers
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
    """Deterministic hash in [0, 1) for a key (texture-level variation only; placement comes from the tables)."""
    return int.from_bytes(hashlib.sha256(repr(key).encode()).digest()[:4], "little") / 2 ** 32


BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16 + 1 / 32
YY, XX = np.mgrid[0:H, 0:W]
BAY = BAYER[YY % 4, XX % 4]
_LAT = {}


def _lattice(key, n=256):
    if key not in _LAT:
        seed = int.from_bytes(hashlib.sha256(repr(key).encode()).digest()[:8], "little")
        _LAT[key] = np.random.default_rng(seed).random((n, n)).astype(np.float32)
    return _LAT[key]


def wnoise(key, u, v):
    """Smooth value noise at arbitrary (u, v) lattice coordinates (world space, wraps every 256 cells)."""
    g = _lattice(key)
    n = g.shape[0]
    iu, iv = np.floor(u).astype(np.int64), np.floor(v).astype(np.int64)
    tu, tv = u - iu, v - iv
    tu, tv = tu * tu * (3 - 2 * tu), tv * tv * (3 - 2 * tv)
    a = g[iv % n, iu % n]; b = g[iv % n, (iu + 1) % n]
    c = g[(iv + 1) % n, iu % n]; d = g[(iv + 1) % n, (iu + 1) % n]
    return (a * (1 - tu) + b * tu) * (1 - tv) + (c * (1 - tu) + d * tu) * tv


def fbm(key, u, v, octaves=3):
    s, amp, tot = 0.0, 1.0, 0.0
    for o in range(octaves):
        s = s + amp * wnoise((key, o), u * 2 ** o, v * 2 ** o)
        tot += amp
        amp *= 0.5
    return s / tot


def rect(L, x0, y0, x1, y1, c):
    x0, x1 = max(0, int(x0)), min(W - 1, int(x1))
    y0, y1 = max(0, int(y0)), min(H - 1, int(y1))
    if x0 <= x1 and y0 <= y1:
        L[y0:y1 + 1, x0:x1 + 1] = I[c] if isinstance(c, str) else c


def px(L, x, y, c):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H:
        L[y, x] = I[c] if isinstance(c, str) else c


def line(L, x0, y0, x1, y1, c, reg=None):
    n = int(max(abs(x1 - x0), abs(y1 - y0), 1))
    for k in range(n + 1):
        x, y = int(round(x0 + (x1 - x0) * k / n)), int(round(y0 + (y1 - y0) * k / n))
        px(L, x, y, c)
        if reg is not None and 0 <= x < W and 0 <= y < H:
            reg[y, x] = True


def stamp(L, x, y, rows, cmap, reg=None):
    """Paint a hand-authored sprite (top-left at x, y). '.' is transparent; other chars map through cmap."""
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in ". ":
                continue
            px(L, x + i, y + j, cmap.get(ch, ch))
            if reg is not None and 0 <= x + i < W and 0 <= y + j < H:
                reg[y + j, x + i] = True


def ellipse(cx, cy, rx, ry):
    return ((XX + 0.5 - cx) / rx) ** 2 + ((YY + 0.5 - cy) / ry) ** 2 <= 1.0


def ramp_at(ramp, l, cuts):
    k = 0
    while k < len(cuts) and l >= cuts[k]:
        k += 1
    return ramp[k]


def shift(ramp, idx, d):
    if idx in ramp:
        return ramp[max(0, min(len(ramp) - 1, ramp.index(idx) + d))]
    return idx


def cyl_light(u):
    """Light on a vertical cylinder seen from the front, late sun from the right-front. u in [-1, 1]."""
    u = max(-1.0, min(1.0, u))
    return 0.5 * math.sqrt(max(0.0, 1 - u * u)) + 0.5 * u + 0.1


DOME_CUTS = (-0.22, 0.08, 0.28, 0.44, 0.6, 0.74)


def dome_tone(u, d=0, dither=0.0):
    return shift(DOME, ramp_at(DOME, cyl_light(u) + dither, DOME_CUTS), d)


def band(L, y0, y1, hw, d=0, cx=CX, dith=True):
    """A horizontal cylindrical band (dome stage) shaded per column, ordered-dithered across tone borders."""
    for x in range(cx - hw, cx + hw):
        u = (x + 0.5 - cx) / hw
        for y in range(y0, y1 + 1):
            L[y, x] = dome_tone(u, d, (BAYER[y % 4, x % 4] - 0.5) * 0.07 if dith else 0.0)


def outline(mask):
    m = mask
    inner = m.copy()
    inner[1:] &= m[:-1]; inner[:-1] &= m[1:]; inner[:, 1:] &= m[:, :-1]; inner[:, :-1] &= m[:, 1:]
    return m & ~inner


def crown(L, cx, cy, r, ramp, base, seed, reg=None, flat=0.8, n_sub=None, light=(0.55, -0.85), contrast=1.6):
    """Clustered leaf-mass crown: 5-8 scalloped sub-masses (lit upper right, dark lower rim per cluster), shaded by
    smooth light with an ordered dither on the tone borders only (no per-texel random noise)."""
    sub = []
    n = n_sub or (5 + int(hval(seed, "n", cx, cy) * 4))
    for k in range(n):
        a = math.radians(-165 + 150 * k / max(1, n - 1) + 24 * (hval(seed, "a", cx, k) - 0.5))
        dd = r * (0.38 + 0.26 * hval(seed, "d", cx, k))
        sx, sy = cx + dd * math.cos(a), cy + dd * flat * math.sin(a) - r * 0.06
        sr = r * (0.40 + 0.22 * hval(seed, "r", cx, k))
        sub.append((sy, sx, sr, hval(seed, "ph", cx, k) * 6.283))
    sub.append((cy + r * 0.16, cx, r * 0.70, hval(seed, "ph0", cx) * 6.283))
    for k in range(2):                                                   # under-masses (lower-left / lower-right)
        sub.append((cy + r * 0.32, cx + (-0.42 if k == 0 else 0.4) * r, r * 0.5, hval(seed, "phu", cx, k) * 6.283))
    sub.sort()
    m = np.zeros((H, W), bool)
    y0b, y1b = max(0, int(cy - 1.5 * r)), min(H, int(cy + 1.4 * r) + 2)
    x0b, x1b = max(0, int(cx - 1.6 * r)), min(W, int(cx + 1.6 * r) + 2)
    if y0b >= y1b or x0b >= x1b:
        return m
    yy, xx = YY[y0b:y1b, x0b:x1b], XX[y0b:y1b, x0b:x1b]
    bay = BAY[y0b:y1b, x0b:x1b]
    sub_m = L[y0b:y1b, x0b:x1b]
    for sy, sx, sr, ph in sub:
        nx = (xx + 0.5 - sx) / sr
        ny = (yy + 0.5 - sy) / (sr * flat)
        th = np.arctan2(ny, nx)
        rr = 1.0 + 0.10 * np.sin(5 * th + ph) + 0.06 * np.sin(11 * th + 2 * ph)
        e = nx * nx + ny * ny <= rr * rr
        if not e.any():
            continue
        l = base + contrast * (light[0] * nx + light[1] * ny) * 0.75 + (bay - 0.5) * 0.9
        idx = np.clip(np.round(l), 0, len(ramp) - 1).astype(np.int64)
        sub_m[e] = np.array(ramp, np.int16)[idx[e]]
        dn = np.zeros_like(e); dn[:-1] = e[1:]
        sub_m[e & ~dn] = ramp[0]
        m[y0b:y1b, x0b:x1b] |= e
    if reg is not None:
        reg |= m
    return m


# ============================================================================ layer painters: sky
SKY_STOPS = [(0, "sk0"), (58, "sk1"), (128, "sk2"), (206, "sk3"), (282, "sk4"), (346, "sk5"), (392, "sk6"),
             (418, "sk7")]
CLOUDS = [  # (cx, cy, rx, ry, lit) cloud banks; hand placed clear of the dome (x 560..720 above row 260)
    (250, 40, 300, 30, 1), (1050, 62, 260, 30, 1), (1210, 30, 120, 18, 1),
    (450, 136, 110, 7, 0), (900, 166, 150, 8, 0), (1130, 234, 190, 10, 0),
    (220, 298, 200, 8, 0), (1120, 316, 170, 6, 0),
]


def paint_sky():
    L = new()
    for y in range(H):
        cur = 0
        for k, (y0, c) in enumerate(SKY_STOPS):
            if y >= y0:
                cur = k
        L[y, :] = I[SKY_STOPS[cur][1]]
        # 12-row ordered-dither transition into the next stop
        if cur + 1 < len(SKY_STOPS):
            y1, c1 = SKY_STOPS[cur + 1]
            if y1 - 12 <= y < y1:
                t = (y - (y1 - 12) + 0.5) / 12
                m = BAY[y] < t
                L[y, m] = I[c1]
    return L


def paint_clouds():
    """Cloud banks from noise inside a flattened envelope: puffy lit tops (late sun from behind the camera),
    darker flat undersides; the distant streaks are thin and low-contrast. Shading by depth below the local top."""
    L = new()
    ramp = np.array(R("cl4", "cl3", "cl2", "cl1", "cl0"), np.int16)
    for k, (cx, cy, rx, ry, lit) in enumerate(CLOUDS):
        if lit:                                           # cumulus bank: flat dark base body + lit puffs on top
            Lout, L = L, new()
            body = ((XX + 0.5 - cx) / rx) ** 2 + ((YY + 0.5 - cy - ry * 0.2) / (ry * 0.42)) ** 2 <= 1
            vb = 1.2 + (YY - cy) / ry * -1.2 + (BAY - 0.5) * 0.8
            L[body] = ramp[np.clip(np.round(vb), 0, 4).astype(int)][body]
            npuff = 17
            puffs = []
            for i in range(npuff):
                t = i / (npuff - 1)
                pxc = cx - rx * 0.86 + 1.72 * rx * t + 26 * (hval("pfx", k, i) - 0.5)
                r = ry * (0.22 + 0.62 * hval("pfr", k, i) ** 1.5) * (1 - 0.5 * abs(pxc - cx) / rx)
                pyc = cy + ry * 0.14 - r * 0.3 + 0.3 * ry * (hval("pfy", k, i) - 0.5)
                puffs.append((r, pxc, pyc))
            nz = fbm(("pfn", k), XX / 7.0, YY / 5.0)
            for r, pxc, pyc in sorted(puffs):            # small puffs first, big ones over them
                dd = np.sqrt(((XX + 0.5 - pxc) / (r * 1.6)) ** 2 + ((YY + 0.5 - pyc) / r) ** 2)
                e = dd <= 1 + 0.35 * (nz - 0.5)
                l = (-(YY + 0.5 - pyc) / r * 0.8 + (XX + 0.5 - pxc) / (r * 1.6) * 0.3)
                v = 1.9 + 1.3 * l + (nz - 0.5) * 1.2 + (BAY - 0.5) * 0.8
                L[e] = ramp[np.clip(np.round(v), 0, 4).astype(int)][e]
                dn = np.zeros_like(e); dn[:-1] = e[1:]
                L[e & ~dn & (YY < cy + ry * 0.3)] = I["cl3"]
            base = cy + ry * 0.42 + 2 * np.sin(XX / 29.0 + k)
            L[YY >= base] = -1                                               # flat underside
            Lout[L >= 0] = L[L >= 0]
            L = Lout
            continue
        env = 1 - ((XX + 0.5 - cx) / rx) ** 2 - ((YY + 0.5 - cy) / ry) ** 2
        n = fbm(("cloud", k), XX / (22.0 if lit else 40.0), YY / (12.0 if lit else 5.0), octaves=4)
        m = env + (n - 0.5) * (1.6 if lit else 1.2) > (0.22 if lit else 0.3)
        if lit:                                           # flatten the underside: clip below a wavy base line
            base = cy + ry * 0.35 + 3 * np.sin(XX / 37.0 + k)
            m &= YY < base
        if not m.any():
            continue
        # depth below the local top of the mask (per column)
        depth = np.zeros((H, W), np.int16)
        run = np.zeros(W, np.int16)
        for y in range(H):
            run = np.where(m[y], run + 1, 0)
            depth[y] = run
        dn = np.zeros_like(m); dn[:-1] = m[1:]
        if lit:
            v = 3.6 - depth * 0.28 + (n - 0.5) * 2.2 + (BAY - 0.5) * 0.8
            col = np.array(R("cl4", "cl3", "cl2", "cl1", "cl0"), np.int16)[np.clip(np.round(v), 0, 4).astype(int)]
            L[m] = col[m]
            L[m & (depth <= 1)] = I["cl0"]
            L[m & ~dn] = I["cl4"]
        else:
            v = 1.4 - depth * 0.35 + (n - 0.5) * 1.4 + (BAY - 0.5) * 0.6 + (0.6 if cy > 200 else 0)
            col = np.array(R("cl3", "cl2", "cl1"), np.int16)[np.clip(np.round(v), 0, 2).astype(int)]
            L[m] = col[m]
    return L


# ============================================================================ dome
def shell_hw(y):
    t = (SHELL[1] - y) / (SHELL[1] - SHELL[0])
    return SHELL_HW[1] + (SHELL_HW[0] - SHELL_HW[1]) * max(0.0, 1 - t ** 2.4) ** 0.55


STATUE_ROWS = [  # Statue of Freedom, 20 rows: feather crest, head, shoulders, shield (her right = screen left),
    "....b....",  # sword hand (screen right), robe widening to the hem, then the globe (iron, lit right)
    "...bkb...",
    "...kKk...",
    "...kKK...",
    "....kK...",
    "...kkK...",
    "..kkkKK..",
    ".kkkkKKk.",
    "kkkkkKKk.",
    "kkkkkKKkK",
    "kkkkkKKk.",
    ".kkkkKKk.",
    "..kkkKKk.",
    "..kkkKKK.",
    "..kkkKKKk",
    ".kkkkKKKk",
    ".kkkkKKKk",
    "..hhhHHH.",
    ".hhhHHHHh",
    "..hhhHH..",
]


def paint_dome():
    L = new()
    band(L, DRUM[0], DRUM[1], HW["drum"], -1)
    for x in range(CX - HW["drum"], CX + HW["drum"]):                     # drum windows
        if (x - (CX - HW["drum"])) % 12 in (5, 6):
            L[DRUM[0] + 3:DRUM[0] + 9, x] = shift(DOME, int(L[DRUM[0] + 3, x]), -2)
    band(L, STYLOBATE[0], STYLOBATE[1], HW["stylobate"], 0)
    band(L, STYLOBATE[0], STYLOBATE[0] + 1, HW["stylobate"], 1)
    band(L, STYLOBATE[1], STYLOBATE[1], HW["stylobate"], -1)
    # peristyle: dark interior (inner drum wall with windows), then 36 columns, front half visible
    hw = HW["peri_cols"]
    band(L, PERI_COLS[0], PERI_COLS[1], hw - 2, -3)
    for x in range(CX - hw + 4, CX + hw - 4):
        if (x - CX + 200) % 10 in (3, 4, 5):
            L[PERI_COLS[0] + 8:PERI_COLS[1] - 6, x] = I["dm0"]
    for k in range(PERI_COLS_N):
        th = math.radians(-180 + 5 + k * 10)
        if math.cos(th) <= 0:
            continue
        idx = int(round(math.degrees(th) - 5) // 10)
        if idx in PERI_MISSING:
            continue
        xc = CX - 0.5 + hw * math.sin(th)
        x0 = int(math.floor(xc - 1.5))
        for j, xx in enumerate(range(x0, x0 + 4)):
            u = (xx + 0.5 - CX) / hw
            c = dome_tone(u, (-1, 0, 1, 0)[j])
            L[PERI_COLS[0] + 2:PERI_COLS[1] - 1, xx] = c
        rect(L, x0 - 1, PERI_COLS[0], x0 + 4, PERI_COLS[0] + 1, dome_tone((xc - CX) / hw, 1))   # capital
        rect(L, x0 - 1, PERI_COLS[1] - 1, x0 + 4, PERI_COLS[1], dome_tone((xc - CX) / hw, 0))   # base
    # entablature: cornice lit, shadow below, frieze
    band(L, PERI_ENT[0], PERI_ENT[1], HW["peri_ent"], 0)
    band(L, PERI_ENT[0], PERI_ENT[0] + 1, HW["peri_ent"], 1, dith=False)
    band(L, PERI_ENT[0] + 2, PERI_ENT[0] + 2, HW["peri_ent"] - 1, -2, dith=False)
    band(L, PERI_ENT[1], PERI_ENT[1], HW["peri_ent"] - 2, -1, dith=False)
    # balustrade on the peristyle
    band(L, PERI_BAL[0], PERI_BAL[0], HW["peri_bal"], 1, dith=False)
    for x in range(CX - HW["peri_bal"], CX + HW["peri_bal"]):
        u = (x + 0.5 - CX) / HW["peri_bal"]
        L[PERI_BAL[0] + 1:PERI_BAL[1] + 1, x] = dome_tone(u, 0 if x % 3 else -2)
    # attic: cornice, shadow, pilasters and windows on a 10 degree grid
    hw = HW["attic"]
    band(L, ATTIC[0], ATTIC[1], hw, 0)
    band(L, ATTIC[0], ATTIC[0] + 1, hw, 1, dith=False)
    band(L, ATTIC[0] + 2, ATTIC[0] + 2, hw, -1, dith=False)
    band(L, ATTIC[1], ATTIC[1], hw, -1, dith=False)
    for k in range(-8, 9):
        th = math.radians(k * 10)
        x = int(round(CX - 0.5 + hw * math.sin(th)))
        if abs(k) <= 7:
            for xx in (x, x + 1):
                L[ATTIC[0] + 3:ATTIC[1], xx] = dome_tone((xx + 0.5 - CX) / hw, 1 if xx == x + 1 else 0)
        th2 = math.radians(k * 10 + 5)
        if abs(k * 10 + 5) < 65:
            x2 = int(round(CX - 0.5 + hw * math.sin(th2)))
            for xx in (x2 - 1, x2, x2 + 1):
                L[ATTIC[0] + 6:ATTIC[0] + 14, xx] = dome_tone((xx + 0.5 - CX) / hw, -3)
            L[ATTIC[0] + 5, x2 - 1:x2 + 2] = dome_tone((x2 + 0.5 - CX) / hw, 1)
    # ribbed shell (surface of revolution), light from the upper right-front, dithered on tone borders
    lv = np.array([0.55, 0.42, 0.72]); lv = lv / np.linalg.norm(lv)
    y0, y1 = SHELL
    for y in range(y0, y1 + 1):
        hwy = shell_hw(y)
        t = (y1 - y) / (y1 - y0)
        phi = math.radians(6 + 66 * t ** 1.6)
        for x in range(int(math.floor(CX - hwy)), int(math.ceil(CX + hwy))):
            u = (x + 0.5 - CX) / hwy
            if abs(u) > 1:
                continue
            n = np.array([u * math.cos(phi), math.sin(phi), math.sqrt(max(0, 1 - u * u)) * math.cos(phi)])
            l = float(n @ lv) * 0.95 + 0.02 + (BAYER[y % 4, x % 4] - 0.5) * 0.08
            L[y, x] = ramp_at(DOME, l, (-0.12, 0.1, 0.3, 0.48, 0.66, 0.82))
        if y > y0 + 2:                                               # ribs every 12 degrees: shade left, lit right
            for k in range(-7, 8):
                if abs(k * 12) > 80:
                    continue
                x = int(round(CX - 0.5 + hwy * math.sin(math.radians(k * 12))))
                if CX - hwy + 1 < x < CX + hwy - 2:
                    L[y, x] = shift(DOME, int(L[y, x]), -1)
                    if k % 2 == 0 and y < y1 - 3:
                        L[y, x + 1] = shift(DOME, int(L[y, x + 1]), 1)
    for x in range(CX - SHELL_HW[0], CX + SHELL_HW[0]):              # shell base ring
        u = (x + 0.5 - CX) / SHELL_HW[0]
        L[y1, x] = dome_tone(u, 1); L[y1 - 1, x] = dome_tone(u, 1); L[y1 - 2, x] = dome_tone(u, -1)
    for k in range(-5, 6):                                           # lunette windows near the base of the shell
        th = math.radians(k * 12 + 6)
        if abs(k * 12 + 6) > 64:
            continue
        hwy = shell_hw(y1 - 9)
        x = int(round(CX - 0.5 + hwy * math.sin(th)))
        for yy, w in ((y1 - 11, 1), (y1 - 10, 2), (y1 - 9, 2), (y1 - 8, 2), (y1 - 7, 2)):
            for xx in range(x - w // 2, x - w // 2 + w + 1):
                L[yy, xx] = I["dm0"] if yy > y1 - 11 else I["dm1"]
        L[y1 - 6, x - 1:x + 3] = dome_tone((x + 0.5 - CX) / hwy, 1)
    # tholos: ring, columns, cap
    band(L, THOLOS_RING[0], THOLOS_RING[1], HW["tholos_ring"], 0)
    band(L, THOLOS_RING[0], THOLOS_RING[0] + 1, HW["tholos_ring"], 1, dith=False)
    band(L, THOLOS_COLS[0], THOLOS_COLS[1], HW["tholos_cols"], -3, dith=False)
    for th in (-64, -30, 0, 30, 64):
        x = int(round(CX - 0.5 + HW["tholos_cols"] * math.sin(math.radians(th))))
        for xx in (x, x + 1):
            L[THOLOS_COLS[0]:THOLOS_COLS[1] + 1, xx] = dome_tone((xx + 0.5 - CX) / HW["tholos_cols"], 1 if xx > x else 0)
    band(L, THOLOS_COLS[0], THOLOS_COLS[0] + 1, HW["tholos_cols"] + 2, 0, dith=False)
    for y, hwc in zip(range(THOLOS_CAP[0], THOLOS_CAP[1] + 1), (3, 5, 7, 8, 9, 10, 11, 12)):
        band(L, y, y, hwc, 0)
    # Statue of Freedom (bronze) on its globe
    stamp(L, CX - 4, STATUE[0], STATUE_ROWS, {"k": "br0", "K": "br1", "b": "br1", "h": "dm1", "H": "dm3"})
    return L


# ============================================================================ West Front
FACADE_STATE = {  # hand-assigned window states by (section, bay): broken / boarded / dark (default) / glint
    ("wingL", 3): "boarded", ("wingL", 9): "broken", ("corrL", 1): "boarded", ("centerL", 2): "broken",
    ("centerL", 5): "glint", ("centerR", 1): "boarded", ("centerR", 4): "broken", ("corrR", 1): "broken",
    ("corrR", 2): "broken", ("wingR", 0): "broken", ("wingR", 2): "broken", ("wingR", 3): "boarded",
    ("wingR", 5): "broken", ("wingR", 7): "broken", ("wingR", 8): "broken",
}
WIN_ROWS = (288, 306)             # principal-storey window (dark) rows
BELT = (312, 315)
BASE_ROWS = (316, FACADE_BOTTOM)


def T(n, d):
    return shift(DOME, I[n], d)


def facade_section(L, name, x0, x1, top, kind, d):
    rect(L, x0, top, x1, FACADE_BOTTOM, T("dm4", d))
    # roof balustrade: top rail, balusters, base rail
    rect(L, x0, top, x1, top, T("dm5", d)); rect(L, x0, top + 1, x1, top + 1, T("dm4", d))
    for x in range(x0, x1 + 1):
        L[top + 2:top + 5, x] = T("dm4", d) if x % 3 else T("dm2", d)
    rect(L, x0, top + 5, x1, top + 5, T("dm5", d)); rect(L, x0, top + 6, x1, top + 6, T("dm3", d))
    # cornice (lit), deep shadow under it, frieze, architrave
    e = top + 7
    rect(L, x0, e, x1, e + 1, T("dm6", d) if d == 0 else T("dm5", d))
    rect(L, x0, e + 2, x1, e + 3, T("dm1", d))
    rect(L, x0, e + 4, x1, e + 7, T("dm4", d))
    rect(L, x0, e + 8, x1, e + 8, T("dm3", d))
    p0 = e + 9
    if kind == "loggia":                          # recessed colonnade: dark back wall with doors, paired columns
        rect(L, x0 + 2, p0, x1 - 2, BELT[0] - 1, T("dm1", d))
        rect(L, x0 + 2, p0, x1 - 2, p0 + 2, T("dm0", d))
        for x in range(x0 + 8, x1 - 6, 12):
            rect(L, x + 3, p0 + 12, x + 6, BELT[0] - 1, T("dm0", d))   # doors
        for x in range(x0 + 3, x1 - 3, 12):       # paired columns: shade, mid, lit, lit (light from the right)
            for j, tone in enumerate(("dm3", "dm4", "dm5", "dm6")):
                L[p0:BELT[0], x + j] = T(tone, d)
            for j, tone in enumerate(("dm3", "dm4", "dm5", "dm6")):
                L[p0:BELT[0], x + 5 + j] = T(tone, d)
            rect(L, x - 1, p0, x + 9, p0 + 1, T("dm6", d))           # capitals
        rect(L, x0, p0, x1, p0, T("dm5", d))
    else:
        bays = list(range(x0 + 5, x1 - 5, 12))
        for bay, x in enumerate(bays):
            st = FACADE_STATE.get((name, bay), "dark")
            rect(L, x - 2, WIN_ROWS[0] - 4, x + 5, WIN_ROWS[0] - 3, T("dm6", d))   # pediment / lintel cap
            rect(L, x - 1, WIN_ROWS[0] - 2, x + 4, WIN_ROWS[0] - 2, T("dm2", d))   # shadow under the cap
            c = {"dark": T("dm1", d), "broken": I["br0"], "boarded": I["s2"], "glint": T("dm3", d)}[st]
            rect(L, x, WIN_ROWS[0], x + 3, WIN_ROWS[1], c)
            if st == "dark":
                rect(L, x, WIN_ROWS[0], x + 3, WIN_ROWS[0] + 1, T("dm0", d))
            if st == "boarded":
                rect(L, x, WIN_ROWS[0] + 5, x + 3, WIN_ROWS[0] + 5, "s1")
                rect(L, x, WIN_ROWS[0] + 11, x + 3, WIN_ROWS[0] + 11, "s1")
            rect(L, x - 1, WIN_ROWS[1] + 1, x + 4, WIN_ROWS[1] + 1, T("dm6", d))   # sill
            rect(L, x, top + 17, x + 3, top + 19, T("dm1", d))                      # attic-storey window
            L[p0:BELT[0], x + 7] = T("dm5", d)                                       # pilaster: lit edge
            L[p0:BELT[0], x + 8] = T("dm3", d)
    # belt course and rusticated base with arched openings
    rect(L, x0, BELT[0], x1, BELT[0] + 1, T("dm6", d) if d == 0 else T("dm5", d))
    rect(L, x0, BELT[0] + 2, x1, BELT[1], T("dm2", d))
    for y in range(BASE_ROWS[0] + 3, FACADE_BOTTOM + 1, 4):
        rect(L, x0, y, x1, y, T("dm3", d))
    for x in range(x0 + 5, x1 - 5, 12):
        rect(L, x, 322, x + 3, 323, T("dm2", d)); rect(L, x + 1, 321, x + 2, 321, T("dm2", d))
        rect(L, x, 324, x + 3, 338, T("dm0", d))
    if kind == "wing":                                # projecting central portico of engaged columns on each wing
        c0 = (x0 + x1) // 2 - 36
        rect(L, c0 - 3, top - 2, c0 + 74, top - 1, T("dm5", d))                      # raised parapet
        rect(L, c0, p0, c0 + 71, BELT[0] - 1, T("dm2", d))                            # shaded recess
        for k in range(8):
            x = c0 + 2 + k * 9
            for j, tone in enumerate(("dm3", "dm5", "dm6", "dm5")):
                L[p0:BELT[0], x + j] = T(tone, d)
            rect(L, x - 1, p0, x + 4, p0 + 1, T("dm6", d))
            rect(L, x - 1, BELT[0] - 2, x + 4, BELT[0] - 1, T("dm4", d))
        for x in range(c0 - 3, c0):                                                   # its cast shadow (left)
            for y in range(p0, BELT[0]):
                L[y, x] = shift(DOME, int(L[y, x]), -1)


def paint_west_front():
    L = new()
    for name, x0, x1, top, kind, d in SECTIONS:
        facade_section(L, name, x0, x1, top, kind, d)
    # raised attic over the central pavilion
    p0, p1 = SECTIONS[3][1], SECTIONS[3][2]
    rect(L, p0, 254, p1, 259, "dm4"); rect(L, p0, 254, p1, 254, "dm6"); rect(L, p0, 255, p1, 255, "dm5")
    # shadow strips cast to the left by projecting blocks (light from the right)
    for xs in (SECTIONS[3][1] - 4, SECTIONS[2][1] - 4, SECTIONS[6][1] - 4):
        for x in range(xs, xs + 4):
            for y in range(256, FACADE_BOTTOM + 1):
                if L[y, x] >= 0:
                    L[y, x] = shift(DOME, int(L[y, x]), -1)
    # side returns: north end in shade, south end lit
    rect(L, 286, 270, 288, FACADE_BOTTOM, "dm2")
    rect(L, 991, 270, 993, FACADE_BOTTOM, "dm6")
    return L


# ============================================================================ Olmsted terrace + west lawn
LAWN_ROWS = (381, 437)


def paint_terrace_lawn():
    L = new()
    x0, x1 = TERRACE
    rect(L, x0, DECK[0], x1, DECK[1], "dm4"); rect(L, x0, DECK[0], x1, DECK[0], "dm3")
    # balustrade with piers every 40 px
    rect(L, x0, TBAL[0], x1, TBAL[0], "dm6"); rect(L, x0, TBAL[0] + 1, x1, TBAL[0] + 1, "dm4")
    for x in range(x0, x1 + 1):
        L[TBAL[0] + 2:TBAL[1] - 1, x] = I["dm5"] if x % 3 == 1 else (I["dm4"] if x % 3 == 2 else I["dm2"])
    rect(L, x0, TBAL[1] - 1, x1, TBAL[1] - 1, "dm5"); rect(L, x0, TBAL[1], x1, TBAL[1], "dm3")
    for x in range(x0 + 6, x1, 40):
        rect(L, x, TBAL[0] - 2, x + 4, TBAL[1], "dm4")
        rect(L, x + 3, TBAL[0] - 2, x + 4, TBAL[1], "dm6")
        rect(L, x, TBAL[0] - 2, x + 4, TBAL[0] - 2, "dm6")
        rect(L, x, TBAL[0] - 2, x, TBAL[1], "dm3")
    # wall face: marble courses, terrace-room windows, granite foundation
    rect(L, x0, TWALL[0], x1, TWALL[1], "dm4")
    rect(L, x0, TWALL[0], x1, TWALL[0] + 1, "dm2")                           # shadow under the rail
    for y in range(TWALL[0] + 4, TWALL[1] + 1, 4):
        rect(L, x0, y, x1, y, "dm3")
    rect(L, x0, TGRANITE[0], x1, TGRANITE[1], "dm2")
    for y in (TGRANITE[0] + 2, TGRANITE[0] + 4):
        for x in range(x0 + (y // 2) % 2 * 4, x1, 9):
            rect(L, x, y, x + 1, y, "dm1")
    for x in range(x0 + 18, x1 - 12, 30):
        if EXEDRA[0] - 70 < x < EXEDRA[1] + 70:
            continue
        rect(L, x, TWALL[0] + 5, x + 3, TWALL[0] + 12, "dm1")
        rect(L, x, TWALL[0] + 5, x + 3, TWALL[0] + 6, "dm0")
        rect(L, x - 1, TWALL[0] + 4, x + 4, TWALL[0] + 4, "dm6")
    # returns at both ends: north return in shade, south return lit
    for k in range(10):
        rect(L, x0 - 1 - k, TBAL[0] + k // 2, x0 - 1 - k, TGRANITE[1], "dm2" if k < 8 else "dm1")
        rect(L, x1 + 1 + k, TBAL[0] + k // 2, x1 + 1 + k, TGRANITE[1], "dm5" if k < 8 else "dm4")
    # four west lanterns on piers (bronze, unlit in 2537)
    for x in LANTERNS:
        rect(L, x, TBAL[0] - 12, x + 1, TBAL[0] - 3, "br1")
        rect(L, x - 2, TBAL[0] - 17, x + 3, TBAL[0] - 12, "br0")
        rect(L, x + 2, TBAL[0] - 16, x + 3, TBAL[0] - 13, "br2")
        px(L, x, TBAL[0] - 18, "br0"); px(L, x + 1, TBAL[0] - 18, "br0")
    # exedra: arched grotto under the landing with the dry fountain rim and dead planting
    e0, e1 = EXEDRA
    g0, g1 = e0 + 10, e1 - 10
    for x in range(g0, g1 + 1):
        u = (x + 0.5 - (g0 + g1 + 1) / 2) / ((g1 - g0 + 1) / 2)
        top = TWALL[0] + 3 + int(round(7 * (u * u)))
        rect(L, x, top, x, TGRANITE[1], "dm0" if abs(u) < 0.8 else "dm1")
    rect(L, g0 + 4, TGRANITE[0] - 2, g1 - 4, TGRANITE[0] - 1, "dm4")              # basin rim
    rect(L, g0 + 4, TGRANITE[0] - 2, g1 - 4, TGRANITE[0] - 2, "dm6")
    for x in range(g0 + 6, g1 - 5, 5):                                           # dry plants in the basin
        rect(L, x, TGRANITE[0] - 5, x + 1, TGRANITE[0] - 3, "vg1")
    # twin grand stairs: from a central landing over the exedra, two flights descend OUTWARD to the lawn
    # (inverted V). Each tread: lit top row, shaded riser row; outer cheek wall lit on the south (right) side.
    rect(L, e0 - 6, TBAL[0] - 1, e1 + 6, TBAL[0] + 1, "dm5")                      # landing
    rect(L, e0 - 6, TBAL[0] - 1, e1 + 6, TBAL[0] - 1, "dm6")
    for side in (-1, 1):
        inner0 = (e0 - 4) if side < 0 else (e1 + 4)
        for k in range(15):
            y = TBAL[0] + 2 + 2 * k
            xa = inner0 + side * (4 * k)                                         # inner edge moves outward
            xb = xa + side * 26
            lo, hi = min(xa, xb), max(xa, xb)
            rect(L, lo, y, hi, y, "dm6" if side > 0 else "dm5")
            rect(L, lo, y + 1, hi, y + 1, "dm3" if side > 0 else "dm2")
            ch = hi + 1 if side > 0 else lo - 2                                  # outer cheek wall
            rect(L, ch, y - 1, ch + 1, y + 1, "dm5" if side > 0 else "dm2")
            ic = lo - 1 if side > 0 else hi + 1                                  # inner edge shadow on the wall
            rect(L, ic, y, ic, y + 1, "dm1")
    # the west lawn below the terrace (hill face falling toward the viewer): hazed meadow, darker toward the foot
    for y in range(LAWN_ROWS[0], LAWN_ROWS[1] + 1):
        t = (y - LAWN_ROWS[0]) / (LAWN_ROWS[1] - LAWN_ROWS[0])
        n = wnoise("lawn", XX[y] / 14.0, np.full(W, y / 3.0))
        v = 2.6 - 1.4 * t + (n - 0.5) * 1.6 + (BAY[y] - 0.5) * 0.7
        idx = np.clip(np.round(v), 0, 4).astype(int)
        dry = wnoise("lawnd", XX[y] / 40.0, np.full(W, y / 8.0)) > 0.66
        row = np.array(VG, np.int16)[idx]
        row[dry & (idx >= 2)] = I["vg4"] if (y % 2 or y > 405) else I["vg3"]
        L[y, :] = row
    # central rubble apron below the stairs, and two curving walks (pale, broken)
    for side in (-1, 1):
        for k in range(26):
            t = k / 25
            x = CX + side * (90 + 260 * t ** 1.3)
            y = LAWN_ROWS[0] + 2 + 30 * t
            w = int(3 + 6 * t)
            if hval("walkgap", side, k) < 0.18:
                continue
            rect(L, x - w, y, x + w, y + 1, "dm3" if y < 400 else "mi0")
    return L


# ============================================================================ 2537 damage on the Capitol
IVY = [  # (x0, x1, top row, mean length, raggedness) ivy curtains: north wing (left), its corridor, the terrace
    (288, 316, 271, 50, 14), (317, 338, 273, 30, 10), (339, 366, 271, 44, 16), (384, 404, 274, 20, 8),
    (405, 431, 271, 56, 12), (432, 450, 275, 30, 10), (451, 462, 276, 14, 6),
    (170, 214, 350, 26, 6), (222, 256, 352, 18, 6), (266, 292, 354, 14, 5),
]
SOOT = [(860, 286, 14), (884, 285, 12), (908, 287, 16), (836, 288, 9), (722, 288, 8), (764, 288, 12),
        (490, 288, 9), (814, 288, 10)]
COLLAPSE = (914, 993, 270, 332)   # south-wing corner collapse: x0, x1, roof row, lowest broken row
SHELL_RINGS = (134, 142, 150, 158, 166, 174)
MISSING_PLATES = [  # (ring band index, rib gap index on the south side, "full" or "tri") missing cast-iron plates
    (0, 3, "tri"), (1, 2, "full"), (1, 3, "full"), (2, 2, "full"), (2, 3, "full"), (2, 4, "full"),
    (3, 3, "full"), (3, 4, "full"), (3, 5, "tri"), (4, 4, "tri"), (1, 4, "tri"),
]
DEBRIS_BLOCKS = [  # (x, y, w, h) larger marble blocks inside the debris cone below the collapse
    (944, 338, 9, 5), (968, 334, 11, 6), (930, 352, 8, 4), (986, 350, 10, 5), (956, 360, 12, 5), (1004, 366, 8, 4),
    (938, 372, 10, 4), (974, 374, 9, 4), (1016, 380, 7, 3),
]
BREACH_BAL = (1010, 1066)         # breached south terrace balustrade (x range)


def paint_capitol_damage(sky):
    L = new()
    # missing cast-iron plates on the dome's south shell: each missing plate is the cell between two ribs and two
    # ring members; the void is dark, the surviving ribs/rings stay as a thin lattice, lower plate edges catch light
    rib_x = lambda y, k: CX - 0.5 + shell_hw(y) * math.sin(math.radians(k * 12))
    hole = np.zeros((H, W), bool)
    for band_i, k, shape in MISSING_PLATES:
        ya, yb = SHELL_RINGS[band_i], SHELL_RINGS[band_i + 1]
        for y in range(ya + 1, yb):
            xa, xb = rib_x(y, k) + 1.5, rib_x(y, k + 1) - 0.5
            if shape == "tri":                                   # lower-left half of the plate torn away
                t = (y - ya) / (yb - ya)
                xb = xa + (xb - xa) * t
            for x in range(int(math.ceil(xa)), int(math.floor(xb)) + 1):
                hole[y, x] = True
    L[hole] = I["br0"]
    inner = hole & np.roll(hole, 1, 1) & np.roll(hole, -1, 1)
    L[inner & (BAY > 0.82)] = I["br1"]                            # glimpses of the inner truss
    up = hole & ~np.roll(hole, 1, 0)
    L[np.roll(up, -1, 0) & ~hole & (XX > CX)] = I["dm6"]           # torn upper plate edges catch the light
    rgt = hole & ~np.roll(hole, -1, 1)
    L[np.roll(rgt, 1, 1) & ~hole] = I["dm2"]
    # rust streaks run down from the hole and from the attic windows (mostly dark rust, a few lit drips)
    for x, y0s, y1s in ((654, 170, 190), (659, 168, 196), (664, 172, 184), (670, 166, 192), (648, 168, 178),
                        (676, 186, 200), (606, 186, 196), (686, 214, 232), (694, 216, 228)):
        for y in range(y0s, y1s + 1):
            px(L, x, y, "ru1" if (y - y0s) % 7 == 3 else "ru0")
    # missing peristyle columns leave a dark gap; one broken stump and a fallen drum on the stylobate
    hw = HW["peri_cols"]
    for k in PERI_MISSING:
        xc = int(round(CX - 0.5 + hw * math.sin(math.radians(k * 10 + 5))))
        rect(L, xc - 2, PERI_COLS[0] + 2, xc + 2, PERI_COLS[1] - 2, "dm0")
    xs = int(round(CX - 0.5 + hw * math.sin(math.radians(55))))
    rect(L, xs - 1, PERI_COLS[1] - 9, xs + 2, PERI_COLS[1] - 1, "dm4"); rect(L, xs + 1, PERI_COLS[1] - 9, xs + 2, PERI_COLS[1] - 1, "dm6")
    rect(L, xs - 2, PERI_COLS[1] - 10, xs, PERI_COLS[1] - 10, "dm3"); px(L, xs + 1, PERI_COLS[1] - 11, "dm4")
    # cracked entablature above the gap (sagging, dark crack)
    for i, x in enumerate(range(xs - 14, xs + 10)):
        px(L, x, PERI_ENT[0] + 3 + (i // 6) % 2, "dm0")
    # south-wing (House) corner collapse: above a ragged break line the wing is gone (sky shows through); just
    # under the break the facade has fallen away and the gutted interior is dark, crossed by broken floor slabs
    x0, x1, y0, y1 = COLLAPSE
    prof = {}
    for x in range(x0, x1 + 1):
        t = (x - x0) / (x1 - x0)
        base = y0 + (y1 - y0) * (t ** 1.35)
        jag = 4 * math.sin(x * 0.83) + 3 * math.sin(x * 0.37 + 1.3) + (5 if 948 <= x <= 955 else 0)
        prof[x] = int(max(y0 - 1, min(y1, base + jag * min(1.0, t * 4))))
    for x, yb in prof.items():
        if yb >= y0:
            L[y0 - 3:yb + 1, x] = sky[y0 - 3:yb + 1, x]                    # the wing above the break is gone
        t = (x - x0) / (x1 - x0)
        gut = int(4 + 18 * (1 - t) * min(1.0, t * 5))                     # depth of the gutted dark band
        rect(L, x, yb + 1, x, yb + gut, "br0")
        px(L, x, yb + 1, "dm3")                                           # broken wall edge (no bright chips)
    for yy in (294, 312):                                                 # floor slabs crossing the gutted band
        for x in range(x0, x1 + 1):
            if L[yy, x] == I["br0"] and hval("slab", x // 6, yy) < 0.8:
                L[yy, x] = I["dm3"]; px(L, x, yy + 1, "dm1")
    # a tree grown out of the gutted floor (hazed foliage), trunk rooted on the 312 slab
    rect(L, 940, 300, 941, 314, "vg0"); px(L, 942, 302, "vg0")
    for cx, cy, r in ((934, 292, 11), (948, 286, 12), (940, 280, 8)):
        crown(L, cx, cy, r, VG, 2.0, seed="breach", flat=0.85, contrast=1.4)
    # debris cone: fine rubble mass spilling from the break down the terrace onto the lawn, larger blocks in it
    cone = np.zeros((H, W), bool)
    for y in range(334, 388):
        t = (y - 334) / 54
        cxm = 968 + 10 * t
        hwm = 18 + 46 * t ** 0.8 + 3 * math.sin(y * 0.7)
        cone[y, int(cxm - hwm):int(cxm + hwm * 0.9)] = True
    n = wnoise("rubble", XX / 2.5, YY / 2.0)
    v = 2.6 + (n - 0.5) * 3.0 + (BAY - 0.5) * 0.8 - 0.8 * (YY - 334) / 54
    rub = np.array(R("dm1", "dm2", "dm3", "dm4", "dm5"), np.int16)[np.clip(np.round(v), 0, 4).astype(int)]
    L[cone] = rub[cone]
    ctop = cone & ~np.roll(cone, 1, 0)
    L[ctop] = I["dm5"]
    weeds = cone & (wnoise("rweed", XX / 4.0, YY / 3.0) > 0.68) & (YY > 360)
    L[weeds] = np.where(BAY[weeds] > 0.5, I["vg1"], I["vg2"])
    for x, y, w, h in DEBRIS_BLOCKS:
        rect(L, x, y, x + w - 1, y + h - 1, "dm4")
        rect(L, x, y, x + w - 2, y, "dm6")
        rect(L, x + w - 1, y + 1, x + w - 1, y + h - 1, "dm5")
        rect(L, x, y + h - 1, x + w - 1, y + h - 1, "dm1")
        rect(L, x - 1, y + 1, x - 1, y + h - 1, "dm2")
    # breached south terrace balustrade with a V notch in the wall face
    b0, b1 = BREACH_BAL
    L[TBAL[0] - 2:TBAL[1] + 1, b0:b1 + 1] = sky[TBAL[0] - 2:TBAL[1] + 1, b0:b1 + 1]
    for x in range(b0, b1 + 1):
        dep = 12 - abs(x - (b0 + b1) // 2) // 2
        if dep > 0:
            rect(L, x, TWALL[0], x, TWALL[0] + dep, "dm1")
        rect(L, x, TBAL[1] - 1, x, TBAL[1], "dm3")
    for x, y, w, h in ((b0 + 4, 372, 9, 4), (b0 + 16, 376, 12, 4), (b0 + 32, 374, 10, 5), (b0 + 44, 378, 8, 3),
                       (b0 + 24, 382, 10, 3)):
        rect(L, x, y, x + w - 1, y + h - 1, "dm4"); rect(L, x, y, x + w - 1, y, "dm6")
        rect(L, x, y + h - 1, x + w - 1, y + h - 1, "dm2")
    # weathering grime: short vertical streaks under cornices and sills, denser on the south (right) half, and a
    # settlement crack running down the south centre block
    for name, sx0, sx1, top, kind, d in SECTIONS:
        for x in range(sx0 + 2, sx1 - 1, 3):
            dens = 0.22 + (0.25 if x > CX else 0.0)
            if hval("grime", x) > dens:
                continue
            for yy, ln in ((top + 11, 3 + int(hval("gl", x) * 10)), (WIN_ROWS[1] + 2, 2 + int(hval("gs", x) * 6)),
                           (BELT[1] + 1, 2 + int(hval("gb", x) * 8))):
                rect(L, x, yy, x, yy + ln, "dm3" if hval("gc", x, yy) < 0.7 else "dm2")
    crack = [(772, 268), (768, 280), (774, 292), (770, 304), (776, 318), (771, 330), (775, 344)]
    for (xa, ya), (xb, yb) in zip(crack[:-1], crack[1:]):
        line(L, xa, ya, xb, yb, "dm1")
    # soot tongues above broken windows (darkest at the window, fading up)
    for x, y, h in SOOT:
        for j in range(h):
            w = max(1, 3 - j // 4)
            rect(L, x - w + 2, y - j, x + w + 1, y - j, "br0" if j < h // 2 else "dm1")
    # ivy curtains (north wing, its corridor, the north terrace): leaf-clump masses hanging from the cornices with
    # ragged, dripping lower edges; lit on the right, shaded under each clump
    ivy = np.zeros((H, W), bool)
    for xa, xb, top, ln, rag in IVY:
        for x in range(xa, xb + 1):
            t = (x - xa) / max(1, xb - xa)
            edge = min(1.0, 4 * min(t, 1 - t) + 0.25)
            length = ln * edge + rag * (wnoise(("ivy", xa), x / 3.0, 0.5) - 0.5) * 2
            if hval("drip", x) < 0.12:
                length += 4 + 10 * hval("dripl", x)
            ivy[top:top + max(2, int(length)), x] = True
    n = wnoise("ivyc", XX / 3.2, YY / 2.6)
    v = 1.3 + (n - 0.5) * 3.2 + (BAY - 0.5) * 0.7
    col = np.array(R("vg0", "vg1", "vg2", "vg3"), np.int16)[np.clip(np.round(v), 0, 3).astype(int)]
    L[ivy] = col[ivy]
    L[ivy & ~np.roll(ivy, -1, 1)] = I["vg2"]
    L[ivy & ~np.roll(ivy, -1, 0)] = I["vg0"]
    # roof shrubs on the north wing (left) and the centre (self-seeded)
    for cx, cy, r in ((312, 266, 8), (330, 264, 6), (376, 268, 5), (500, 262, 5), (790, 262, 4)):
        crown(L, cx, cy, r, VG, 2.0, seed="roof", flat=0.7, n_sub=4, contrast=1.3)
    return L


# ============================================================================ Capitol grounds trees (~750-900 m)
GROVE_L = [  # (cx, cy, r) drawn back to front within each list; left (north) grove heavier and taller
    (24, 318, 40), (92, 306, 42), (160, 316, 38), (222, 330, 34), (278, 344, 28), (322, 360, 22),
    (54, 362, 40), (126, 368, 38), (196, 374, 34), (258, 384, 28), (316, 392, 22), (364, 402, 16),
    (20, 404, 34), (90, 408, 34), (158, 410, 30), (226, 414, 24), (290, 418, 18),
]
GROVE_R = [  # right (south) grove: lower, gapped where the collapse and the breach stay visible
    (1258, 344, 34), (1196, 356, 30), (1140, 372, 24), (1100, 388, 16),
    (1230, 388, 32), (1166, 398, 26), (1112, 408, 18), (1060, 414, 12),
    (1250, 416, 26), (1190, 420, 20), (1130, 424, 14),
]
LAWN_TREES = [(470, 412, 10), (512, 420, 8), (792, 416, 9), (850, 410, 11), (900, 420, 8)]
SNAG = (1086, 334)                # dead tree in the south grove


def paint_grounds_trees():
    L = new()
    for grove, seed in ((GROVE_L, "gl"), (GROVE_R, "gr")):
        for cx, cy, r in grove:
            base = 1.4 + 0.9 * (cy - 300) / 120.0 * -1 + 0.9
            crown(L, cx, cy, r, VG, max(1.0, min(3.0, base)), seed=seed, flat=0.78, contrast=1.5)
            rect(L, cx - 1, cy + int(r * 0.55), cx + 1, min(437, cy + int(r * 1.0)), "vg0")
    for cx, cy, r in LAWN_TREES:
        crown(L, cx, cy, r, VG, 2.0, seed="lt", flat=0.8, n_sub=4, contrast=1.4)
        rect(L, cx, cy + int(r * 0.6), cx + 1, cy + r + 3, "vg0")
    x, y = SNAG                                                       # bare dead snag
    for j in range(0, 78):
        xx = x - int(j * 0.06)
        px(L, xx, y + j, "dm1"); px(L, xx + 1, y + j, "dm2" if j < 50 else "dm1")
    for dx, dy, ex, ey in ((0, 10, -14, -9), (1, 18, 12, -6), (0, 28, -10, 4), (1, 6, 7, -10), (0, 40, 9, -3)):
        line(L, x + dx, y + dy, x + dx + ex, y + dy + ey, "dm1")
    return L


# ============================================================================ hill-foot mist (baked, editable)
MIST = (352, 446)                  # rows affected; full strength around the horizon


def mist_strength(y):
    if y < MIST[0] or y > MIST[1]:
        return 0.0
    if y <= HZ - 2:
        t = (y - MIST[0]) / (HZ - 2 - MIST[0])
        return 0.9 * t ** 1.6
    return 0.9 * max(0.0, 1 - (y - (HZ - 2)) / (MIST[1] - HZ + 2)) ** 1.2


def paint_mist(below):
    """Recolour the composite underneath one haze step where a horizontal streak field exceeds the mist strength
    (long horizontal runs rather than a checker, so it reads as banks of mist). Sky and clouds are untouched."""
    L = new()
    for y in range(MIST[0], MIST[1] + 1):
        s = mist_strength(y)
        if s <= 0:
            continue
        n = wnoise("mist", XX[y] / 26.0, np.full(W, y / 2.2)) * 0.75 + BAY[y] * 0.25
        hit = n < s
        row = below[y]
        col = HAZE_LUT[row]
        ok = hit & (col != row) & ~np.isin(row, list(WATER_OR_SKY))
        L[y, ok] = col[ok]
    return L


# ============================================================================ far side of the pool (~300-640 m)
FAR_COPING = (439, 443)
MID_TREES_L = [(30, 408, 26), (84, 416, 24), (140, 420, 20), (196, 424, 16), (244, 428, 12)]
MID_TREES_R = [(1250, 404, 28), (1196, 414, 22), (1144, 420, 18), (1098, 426, 12), (1060, 430, 8)]
MEMORIAL = (446, 833, 428, 438)   # Grant Memorial platform (statues gone in 2537): low pale marble band


def paint_union_square():
    L = new()
    # memorial platform: long low marble band with plinth blocks at both ends and an empty central pedestal
    x0, x1, y0, y1 = MEMORIAL       # hazed (~650 m): low contrast, broken by shrubs and a slumped section
    rect(L, x0, y0, x1, y1, "dm3"); rect(L, x0, y0, x1, y0, "dm4"); rect(L, x0, y1 - 1, x1, y1, "dm2")
    for xb in (x0, x1 - 40):
        rect(L, xb, y0 - 6, xb + 40, y0, "dm3"); rect(L, xb, y0 - 6, xb + 40, y0 - 6, "dm4")
        rect(L, xb + 37, y0 - 5, xb + 40, y0, "dm4")
    rect(L, CX - 12, y0 - 10, CX + 11, y0, "dm2"); rect(L, CX - 12, y0 - 10, CX + 11, y0 - 10, "dm4")
    rect(L, CX + 6, y0 - 9, CX + 11, y0, "dm3")
    for x in range(700, 760):                                   # slumped section of the platform
        dip = int(4 * math.sin(math.pi * (x - 700) / 60))
        rect(L, x, y0, x, y0 + dip, "vg2")
    for cx, cy, r in ((520, 428, 7), (566, 430, 5), (742, 426, 8), (790, 430, 6), (612, 431, 4)):
        crown(L, cx, cy, r, VG, 2.0, seed="memshrub", flat=0.7, n_sub=4, contrast=1.3)
    # far east coping of the pool and the far basin wall
    rect(L, 0, FAR_COPING[0], W - 1, FAR_COPING[1], "q1")
    rect(L, 0, FAR_COPING[0], W - 1, FAR_COPING[0], "mi1")
    rect(L, 0, FAR_COPING[1], W - 1, FAR_COPING[1], "q0")
    for cx, cy, r in MID_TREES_L + MID_TREES_R:
        crown(L, cx, cy, r, MG, 2.1, seed="mid", flat=0.8, contrast=1.5)
        rect(L, cx - 1, cy + int(r * 0.5), cx, FAR_COPING[0] - 1, "mg0")
    return L


# ============================================================================ pool basin floor (d ~ 24 .. 640 m)
POOL_TOP = 444
PANEL = 9.0                         # concrete panel size, m (joints offset 4.5 m so none lies on the axis)
EXPOSED_PATH = [(16.0, 22.0), (11.0, 40.0), (2.0, 64.0), (-6.0, 92.0), (-9.0, 130.0)]   # (X m, d m) leading strip


def world():
    yy = np.maximum(YY - HZ, 0.5).astype(np.float64)
    d = EYE * F / yy
    X = (XX + 0.5 - CX) * d / F
    return d, X


def path_dist(X, d):
    """Distance (m) from the exposed leading strip polyline in world space."""
    best = np.full(X.shape, 1e9)
    for (xa, da), (xb, db) in zip(EXPOSED_PATH[:-1], EXPOSED_PATH[1:]):
        vx, vd = xb - xa, db - da
        t = np.clip(((X - xa) * vx + (d - da) * vd) / (vx * vx + vd * vd), 0, 1)
        dist = np.hypot(X - (xa + t * vx), d - (da + t * vd))
        best = np.minimum(best, dist)
    return best


def floor_fields():
    d, X = world()
    m = YY >= POOL_TOP
    silt = fbm("silt", X / 14.0, d / 14.0) + 0.18 * np.tanh(-X / 30.0) - 0.006 * (60 - np.minimum(d, 60))
    pdist = path_dist(X, d)
    path_w = 3.2 + 0.03 * d
    silt = silt - 0.45 * np.clip(1 - pdist / path_w, 0, 1)
    veg = fbm("veg", X / 10.0, d / 10.0) + 0.32 * np.tanh(-(X + 6) / 14.0) - 0.4 * np.clip(1 - pdist / (path_w * 1.6), 0, 1)
    return d, X, m, silt, veg, pdist


def conc_tone(v, d):
    """Concrete value v (0..1) -> palette, with contrast and value shifting toward the mist with distance."""
    c = np.clip(1.0 - (d - 30) / 400.0, 0.25, 1.0)
    v2 = 0.5 + (v - 0.5) * c + (1 - c) * 0.32
    near = np.array(CONC, np.int16)[np.clip((v2 * 4.99).astype(int), 0, 4)]
    farp = np.array(R("p2", "q0", "q1", "mi1"), np.int16)[np.clip(((v2 - 0.35) * 6.0).astype(int), 0, 3)]
    return np.where(d > 170 + 60 * BAY, farp, near)


def silt_tone(v, d):
    c = np.clip(1.0 - (d - 30) / 400.0, 0.3, 1.0)
    v2 = 0.5 + (v - 0.5) * c + (1 - c) * 0.25
    near = np.array(SILT, np.int16)[np.clip((v2 * 4.99).astype(int), 0, 4)]
    farp = np.array(R("s2", "d0", "vg3", "vg4"), np.int16)[np.clip(((v2 - 0.3) * 6.0).astype(int), 0, 3)]
    return np.where(d > 200 + 60 * BAY, farp, near)


def paint_pool(ff):
    d, X, m, silt, veg, pdist = ff
    L = new()
    i = np.floor((X + PANEL / 2) / PANEL).astype(int)
    j = np.floor(d / PANEL).astype(int)
    pan = _lattice("panel")[j % 256, (i + 128) % 256].astype(np.float64)        # one tone per 9 m panel
    stain = fbm("stain", X / 3.0, d / 3.0)
    v = 0.30 + 0.32 * pan + 0.38 * (stain - 0.5) + (BAY - 0.5) * 0.14
    conc = conc_tone(v, d)
    sv = 0.45 + 0.6 * (fbm("siltv", X / 4.0, d / 4.0) - 0.5) + (BAY - 0.5) * 0.18 + 0.08 * np.tanh((d - 60) / 60)
    silt_c = silt_tone(sv, d)
    exposed = silt < 0.5
    out = np.where(exposed, conc, silt_c)
    # expansion joints on exposed concrete only (silt buries them -> the grid is broken everywhere else)
    jx = np.abs(((X + PANEL / 2) / PANEL) - np.round((X + PANEL / 2) / PANEL)) * PANEL * F / d     # px from joint
    jl = (jx < 0.55) & (d < 260)
    for k in range(3, 72):
        yk = int(round(row_of(k * PANEL)))
        if yk <= POOL_TOP or yk >= H:
            continue
        gap = row_of((k - 1) * PANEL) - yk if k > 1 else 99
        if gap < 3.2:
            continue
        jl[yk] |= True
        if gap > 26:
            jl[yk + 1] |= True
    joint = jl & exposed & m
    jbreak = wnoise("jbreak", X / 2.5, d / 2.5) < 0.22                # chipped / missing joint sealant
    out = np.where(joint & ~jbreak, SHADE_LUT[out], out)
    # heaved / broken panels on the exposed strip (darker, with a lit broken edge)
    for (pi, pj) in ((1, 4), (2, 6), (0, 9), (-1, 12), (1, 3)):
        sel = (i == pi) & (j == pj) & exposed & m
        out[sel] = SHADE_LUT[out[sel]]
    # silt edges: a darker damp rim where silt meets exposed concrete
    em = exposed & m
    rim = m & ~exposed & (np.roll(em, -1, 0) | np.roll(em, 1, 1) | np.roll(em, -1, 1))
    out[rim] = np.where(d[rim] < 120, I["s1"], I["s2"])
    # damp dark patches and moss creeping out of the joints on the exposed concrete
    damp = em & (fbm("damp", X / 1.6, d / 1.6) > 0.64) & (d < 200)
    out[damp] = SHADE_LUT[out[damp]]
    moss = em & joint & (wnoise("moss", X / 1.2, d / 1.2) > 0.5) & (d < 90)
    out[moss] = np.where(BAY[moss] > 0.5, I["g1"], I["g2"])
    mossp = em & (fbm("mossp", X / 0.9, d / 0.9) > 0.7) & (d < 70)
    out[mossp] = np.where(BAY[mossp] > 0.35, I["g2"], I["g3"])
    # drying ripple marks in the silt (sinuous, foreshortened), and pebbles in the near silt
    sl = m & ~exposed & (d < 220)
    rip = np.sin(d * 1.15 + 0.35 * X + 5.0 * wnoise("ripw", X / 6.0, d / 6.0))
    rip_line = sl & (rip > 0.93) & ~rim
    out[rip_line] = np.where(d[rip_line] < 90, I["s1"], I["s2"])
    peb = sl & (d < 70) & (_lattice("peb")[YY % 256, XX % 256] < 0.012)
    ys, xs = np.nonzero(peb)
    for y, x in zip(ys, xs):
        r = max(1, int(0.05 * F / d[y, x]))
        out[y, x:x + r + 1] = I["s4"]
        if y + 1 < H:
            out[y + 1, x:x + r + 1] = I["s0"]
    L[m] = out[m]
    # dried mud polygons on the exposed silt fan right of the strip (Voronoi cracks in world space)
    cells = 1.6
    fu, fv = X / cells, d / cells
    iu, iv = np.floor(fu).astype(int), np.floor(fv).astype(int)
    best1 = np.full(X.shape, 9.0); best2 = np.full(X.shape, 9.0)
    for du in (-1, 0, 1):
        for dv in (-1, 0, 1):
            cu, cv = iu + du, iv + dv
            ox = _lattice("vx")[cv % 256, cu % 256]; oy = _lattice("vy")[cv % 256, cu % 256]
            dist = np.hypot(fu - (cu + ox), fv - (cv + oy))
            best2 = np.where(dist < best1, best1, np.minimum(best2, dist))
            best1 = np.minimum(best1, dist)
    fan = m & (X > 2) & (d < 70) & ~exposed & (silt < 0.62)
    crack = fan & ((best2 - best1) * cells * F / d < 1.0)
    L[crack] = I["s1"]
    L[fan & ~crack & (silt_c == I["s2"])] = I["s3"]
    return L


# ============================================================================ basin vegetation
SAPLINGS = [  # (x, foot row, height px, crown r) self-seeded trees in the north (left) half of the basin
    (64, 462, 96, 30), (150, 456, 70, 22), (218, 452, 52, 16), (1004, 452, 40, 12), (264, 449, 34, 11),
]
SHRUBS = [  # (cx, cy, r) dense shrubs on the basin floor, near (big) to far (small)
    (40, 612, 46), (120, 640, 40), (210, 676, 36), (20, 690, 40), (300, 560, 22), (360, 548, 16),
    (176, 520, 20), (100, 506, 16), (250, 498, 12), (330, 484, 9), (880, 486, 10), (980, 470, 8),
    (1120, 520, 18), (1200, 540, 24),
]


def grass_layer(ff, near_ramp=GR):
    d, X, m, silt, veg, pdist = ff
    L = new()
    thr = 0.52
    g = m & (veg > thr)
    v = 2.0 + 3.0 * (fbm("gv", X / 2.0, d / 2.0) - 0.5) * 1.4 + (veg - thr) * 4.0 + (BAY - 0.5) * 0.9
    near = np.array(near_ramp, np.int16)[np.clip(np.round(v), 0, len(near_ramp) - 1).astype(int)]
    mid = np.array(MG, np.int16)[np.clip(np.round(v * 0.75), 0, 4).astype(int)]
    far = np.array(VG, np.int16)[np.clip(np.round(1.5 + v * 0.5), 0, 4).astype(int)]
    col = np.where(d < 80, near, np.where(d < 220 + 40 * BAY, mid, far))
    dry = fbm("dry", X / 6.0, d / 6.0) > 0.62
    col = np.where(dry & (d < 160), np.where(BAY < 0.5, I["d1"], I["d0"]), col)
    L[g] = col[g]
    # grass blades on the upper edge of near grass regions and scattered inside near grass (height ~ 1/d, capped)
    top = g & ~np.roll(g, 1, 0)
    inside = g & (d < 45) & (_lattice("blade")[YY % 256, XX % 256] < 0.035)
    ys, xs = np.nonzero((top & (d < 90)) | inside)
    for y, x in zip(ys, xs):
        if top[y, x] and hval("bl", int(x), int(y)) < 0.45:
            continue
        h = int(min(16, 0.22 * F / d[y, x] * (0.4 + 0.8 * hval("blh", int(x), int(y)))))
        lean = 1 if hval("bll", int(x), int(y)) < 0.5 else -1
        c = int(L[y, x])
        dk = -1 if inside[y, x] else 0                           # blades inside a tuft read darker, tips lit
        for k in range(1, h + 1):
            xx = x + (lean if k > h * 0.6 else 0)
            if 0 <= y - k < H and 0 <= xx < W:
                L[y - k, xx] = shift(near_ramp, c, 1 if k > h - 2 else dk) if c in near_ramp else c
    return L


def paint_vegetation(ff):
    L = grass_layer(ff)
    for cx, cy, r in SHRUBS:
        d = EYE * F / max(1, cy - HZ)
        ramp = NEAR if d < 80 else MG
        crown(L, cx, cy - r * 0.5, r, ramp, 2.3 if d < 80 else 2.0, seed="shrub", flat=0.62, contrast=1.7)
    for x, foot, hgt, r in SAPLINGS:
        d = EYE * F / (foot - HZ)
        ramp = MG if d < 300 else VG
        for j in range(hgt - r):
            xx = x + int(2 * math.sin(j / 9.0))
            px(L, xx, foot - j, ramp[0]); px(L, xx + 1, foot - j, ramp[1])
            if hgt > 60:
                px(L, xx + 2, foot - j, ramp[1])
        crown(L, x + 3, foot - hgt + r * 0.6, r, ramp, 2.2, seed="sap", flat=0.85, contrast=1.6)
    return L


# ============================================================================ foreground debris (d < 60 m)
ROCKS = [  # (cx, base row, w, h) broken granite coping chunks, sized by distance (1 m ~ 70-115 px here)
    (1010, 716, 120, 46), (1112, 700, 84, 34), (906, 690, 64, 24), (1190, 676, 58, 22), (842, 650, 34, 13),
    (1034, 640, 40, 15), (784, 612, 22, 8), (950, 604, 26, 9), (716, 586, 13, 5), (862, 580, 15, 5),
    (604, 556, 8, 3), (742, 548, 9, 3), (560, 708, 40, 14), (470, 676, 26, 9),
]
LAMP = ((1290, 660), (980, 606))  # toppled cast-iron lamp post: base end (off frame), lantern end
LAMP_W = (15, 10)                 # post diameter in px at the base / lantern end (~0.2 m at ~35 m)
CRACKS = [  # world-space crack polylines (X m, d m) on the exposed strip
    [(14.0, 24.0), (12.5, 30.0), (13.6, 36.0), (11.0, 44.0)], [(8.0, 26.0), (6.0, 33.0), (7.2, 41.0)],
    [(4.0, 52.0), (1.6, 60.0), (2.8, 70.0), (0.2, 80.0)], [(-3.0, 88.0), (-5.0, 100.0), (-4.2, 114.0)],
    [(18.0, 34.0), (21.0, 40.0), (20.0, 48.0)],
]
PEBBLES = [(620, 640, 7), (560, 610, 5), (664, 600, 4), (700, 660, 9), (520, 690, 8), (600, 700, 6),
           (480, 560, 3), (540, 548, 3), (760, 640, 6), (448, 530, 3)]


def proj(Xm, dm):
    return CX - 0.5 + Xm * F / dm, row_of(dm)


def rock(L, cx, base, w, h, seed):
    """Irregular broken granite chunk sitting on the floor: faceted top lit from the right-back, darker front, a
    hard dark contact line, and a short cast shadow to the upper left."""
    y0, y1 = int(base - h * 1.2), int(base) + 1
    x0, x1 = int(cx - w * 0.62), int(cx + w * 0.62) + 1
    yy, xx = YY[y0:y1, x0:x1], XX[y0:y1, x0:x1]
    nx = (xx + 0.5 - cx) / (w / 2)
    ny = (base - (yy + 0.5)) / h                                       # 0 at the base, 1 at the top
    th = np.arctan2(ny, nx)
    ph = hval(seed, "ph") * 6.28
    prof = 1 - nx * nx * (0.55 + 0.25 * hval(seed, "sq")) + 0.10 * np.sin(3 * th + ph) + 0.07 * np.sin(7 * th + 2 * ph)
    m = (ny >= 0) & (ny <= prof) & (np.abs(nx) <= 1.05)
    facet = np.floor((nx + 1.2) * (2 + int(hval(seed, "f") * 2)) + 0.6 * np.sin(ny * 5 + ph))
    lit = (ny > prof - 0.22) & (nx > -0.5) | ((facet % 2 == 1) & (nx > 0.2) & (ny > 0.35))
    v = 1.0 + 0.8 * nx + 0.9 * (ny - 0.4) + np.where(lit, 0.9, 0) + (BAY[y0:y1, x0:x1] - 0.5) * 0.8
    col = np.array(STONE, np.int16)[np.clip(np.round(v), 0, 4).astype(int)]
    lich = wnoise(("lichen", seed), xx / 4.0, yy / 3.0) > 0.8
    col = np.where(lich & ~lit, I["d0"], col)
    sub = L[y0:y1, x0:x1]
    sub[m] = col[m]
    sub[m & (ny < 0.12)] = I["m0"]
    left = m & ~np.roll(m, 1, 1)
    sub[left] = I["m1"]
    full = np.zeros((H, W), bool)
    full[y0:y1, x0:x1] = m[:full[y0:y1, x0:x1].shape[0], :full[y0:y1, x0:x1].shape[1]]
    return full


def paint_debris():
    L = new()
    for cx, base, w, h in ROCKS:                                  # short cast shadows (up-left) in dark silt
        e = ellipse(cx - w * 0.25, base - h * 0.18, w * 0.62, max(2, h * 0.22))
        L[e] = I["s0"] if base > 600 else I["s1"]
    for poly in CRACKS:
        pts = [proj(a, b) for a, b in poly]
        for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
            line(L, xa, ya, xb, yb, "p0")
            if ya > 560:
                line(L, xa + 1, ya, xb + 1, yb, "p1")
    for x, y, r in PEBBLES:
        e = ellipse(x, y, r, r * 0.55)
        L[e] = I["m2"]
        L[e & ~np.roll(e, 1, 0)] = I["m3"]
        L[e & ~np.roll(e, -1, 0)] = I["m0"]
    # toppled cast-iron lamp post lying on the floor: fluted cylinder (lit top flutes), collars, broken lantern
    (xa, ya), (xb, yb) = LAMP
    n = int(max(abs(xb - xa), abs(yb - ya)))
    for s in range(n + 1):
        t = s / n
        x = xa + (xb - xa) * t; y = ya + (yb - ya) * t
        w = LAMP_W[0] + (LAMP_W[1] - LAMP_W[0]) * t
        for k in range(int(w) + 1):
            u = k / max(1, w)                                    # 0 = bottom (shade) .. 1 = top (lit)
            c = "k0" if u < 0.18 else ("k1" if u < 0.55 else ("k2" if u < 0.82 else "k3"))
            if 0.3 < u < 0.9 and int(k) % 3 == 0:
                c = "k1"                                         # fluting
            px(L, x, y - k, c)
        px(L, x, y + 1, "s0")                                    # contact shadow line
    for t, s in ((0.06, 7), (0.33, 5), (0.61, 4), (0.86, 4)):   # collars
        x = xa + (xb - xa) * t; y = ya + (yb - ya) * t
        w = LAMP_W[0] + (LAMP_W[1] - LAMP_W[0]) * t
        rect(L, x - 2, y - w - s // 2, x + 2, y + s // 2, "k0"); rect(L, x - 1, y - w - s // 2, x + 1, y - w, "k3")
    # broken lantern cage at the end, glass gone, lying on its side
    stamp(L, int(xb) - 16, int(yb) - 17, [
        "......kkkkkk......", "....kkKKKKKKkk....", "...kKk......kKk...", "..kK..........Kk..",
        ".kK............Kk.", ".kK.....kk.....Kk.", "kK.....kKKk.....Kk", "kK.....kKKk.....Kk",
        "kK......kk......Kk", ".kK............Kk.", ".kK............Kk.", "..kK..........Kk..",
        "...kKk......kKk...", "....kkKKKKKKkk....", "......kkkkkk......", ".......kkkk.......",
        "......kKKKKk......", "......kkkkkk......"], {"k": "k0", "K": "k2"})
    for k, (dx, dy) in enumerate(((-38, 4), (-44, 6), (-50, 3), (-30, 7))):           # glass shards (dull)
        rect(L, int(xb) + dx, int(yb) + dy, int(xb) + dx + 2, int(yb) + dy, "k3" if k % 2 else "q0")
    for k, (cx, base, w, h) in enumerate(sorted(ROCKS, key=lambda r: r[1])):
        m = rock(L, cx, base, w, h, ("rock", k))
        # weeds tufting along the rock base
        for i in range(int(cx - w * 0.6), int(cx + w * 0.6), 3):
            if hval("tuft", i, k) < 0.45:
                continue
            hh = 2 + int(hval("tufth", i, k) * 9 * (base - 520) / 200)
            for j in range(max(1, hh)):
                px(L, i + (j > hh // 2), base + 1 - j, "g2" if j < hh - 2 else "g4")
    return L


# ============================================================================ survey props (tripod, contact shadows)
def paint_survey(below):
    L = new()
    x, b = TRIPOD
    # contact shadows on the floor first (opaque shade of the floor colour underneath), falling up-left
    sh = np.zeros((H, W), bool)
    sh |= ellipse(HEROINE_FOOT[0] - 3, HEROINE_FOOT[1] - 1, 11, 2.6)
    for (fx, fy) in ((x - 13, b), (x + 13, b), (x + 1, b - 5)):
        line(L, fx, fy, fx - 9, fy - 5, -1, reg=sh)
    sh |= ellipse(x - 6, b - 4, 6, 2)
    L[sh] = SHADE_LUT[below[sh]]
    top = b - TRIPOD_H + 1
    hy = top + 12
    for ex, c1, c2 in ((x - 13, "o1", "o0"), (x + 13, "o1", "o0")):     # front legs (dull orange, no hot highlight)
        line(L, x - 2 if ex < x else x + 1, hy, ex, b - 1, c1)
        line(L, x - 1 if ex < x else x + 2, hy, ex + (1 if ex < x else -1), b - 1, c2)
        rect(L, ex - 1, b - 1, ex + 1, b, "k0")
    line(L, x, hy + 1, x + 1, b - 6, "o0")                              # rear leg
    rect(L, x - 5, hy, x + 5, hy + 2, "k1"); rect(L, x - 5, hy, x + 5, hy, "k2")
    rect(L, x - 1, hy - 3, x + 1, hy - 1, "k1")
    rect(L, x - 5, top + 1, x + 4, hy - 4, "k2")
    rect(L, x + 3, top + 1, x + 4, hy - 4, "k3")
    rect(L, x - 4, top + 3, x - 2, top + 5, "c1")
    rect(L, x - 2, top, x + 2, top, "k1")
    rect(L, x + 5, top + 2, x + 7, top + 4, "k1"); px(L, x + 7, top + 3, "k0")
    reg = (L >= 0) & ~sh
    ol = reg & ~(np.roll(reg, 1, 0) & np.roll(reg, -1, 0) & np.roll(reg, 1, 1) & np.roll(reg, -1, 1))
    L[ol & ~np.isin(L, R("o0", "o1"))] = I["k0"]
    # a hard case and a short ranging pole lying beside the pair
    rect(L, 456, 494, 471, 500, "k1"); rect(L, 456, 494, 471, 494, "k2"); rect(L, 456, 500, 471, 500, "k0")
    rect(L, 462, 496, 465, 497, "o0")
    line(L, 474, 501, 500, 497, "k2"); line(L, 474, 502, 500, 498, "k0")
    return L


# ============================================================================ foreground framing (asymmetric)
FG_TRUNK = [(40, 724, 46), (46, 640, 40), (54, 540, 34), (66, 430, 28), (80, 330, 23), (96, 240, 18),
            (112, 160, 14), (128, 96, 10)]                     # (x centre, row, width) bottom -> top, leaning right
FG_BOUGHS = [((84, 318), (206, 222), 12), ((100, 226), (250, 140), 10), ((74, 400), (168, 352), 8),
             ((114, 150), (36, 92), 8), ((96, 256), (320, 186), 6), ((180, 254), (236, 236), 4)]
FG_CANOPY = [  # (cx, cy, r) overhanging leaf masses, top-left only (the right side stays open sky)
    (20, 20, 70), (110, 10, 66), (210, 30, 56), (300, 52, 40), (60, 110, 60), (170, 108, 50), (262, 120, 36),
    (8, 190, 52), (120, 186, 40), (220, 196, 30), (330, 92, 26), (356, 132, 18),
]
FG_MOUND = [(1210, 738, 120, 64), (1276, 712, 70, 86)]       # low dark rubble/grass mound, bottom-right corner
FG_MOUND_ROCKS = [(1150, 700, 56, 26), (1228, 668, 50, 22), (1262, 690, 44, 30)]


def paint_fg():
    L = new()
    # trunk (lit right edge), roots flaring into the cracked slab
    pts = FG_TRUNK
    bark = wnoise("bark", XX / 2.0, YY / 9.0)                    # vertical bark furrows
    for (xa, ya, wa), (xb, yb, wb) in zip(pts[:-1], pts[1:]):
        for y in range(yb, ya + 1):
            t = (ya - y) / max(1, ya - yb)
            xc = xa + (xb - xa) * t + 2 * math.sin(y / 23.0); w = wa + (wb - wa) * t
            for x in range(int(xc - w / 2), int(xc + w / 2) + 1):
                u = min(1.0, max(0.0, (x + 0.5 - (xc - w / 2)) / max(1, w)))
                v = 0.4 + 2.6 * u ** 1.3 + (bark[min(y, H - 1), max(0, min(W - 1, x))] - 0.5) * 1.6
                c = ("f0", "s0", "s1", "s2", "s3")[int(max(0, min(4, round(v))))]
                if u < 0.12:
                    c = "f0"
                px(L, x, y, c)
    for dx, w in ((-40, 16), (34, 18), (-18, 10)):              # root flare into the cracked slab
        for j in range(w):
            for i in range(14 - j // 2):
                px(L, 40 + dx * (j / w) + i * (1 if dx > 0 else -1) * 0.35, 706 + j - i // 2,
                   "s1" if i > 8 and dx > 0 else ("s0" if i > 3 else "f0"))
    for (a, b, w) in FG_BOUGHS:                                   # tapered boughs, lit on their upper edge
        n = int(math.hypot(b[0] - a[0], b[1] - a[1]) * 1.5)
        for s in range(n + 1):
            t = s / n
            x = a[0] + (b[0] - a[0]) * t; y = a[1] + (b[1] - a[1]) * t - 16 * math.sin(math.pi * t)
            ww = max(2, int(round(w * (1 - 0.7 * t))))
            for k in range(ww):
                px(L, x, y + k, "s2" if k == 0 else ("s0" if k < ww - 1 else "f0"))
    for cx, cy, r in FG_CANOPY:
        crown(L, cx, cy, r, NEAR, 1.6, seed="fgc", flat=0.72, contrast=1.8)
    for x, y, n in ((150, 226, 26), (176, 214, 18), (232, 214, 22), (288, 150, 16), (60, 238, 30)):
        for j in range(n):
            px(L, x + (j // 6) % 2, y + j, "f2" if j % 3 else "g2")
            if j % 5 == 2:
                px(L, x + 1 + (j // 6) % 2, y + j, "g3")
    # bottom-right mound: low, dark (out-of-light) soil + grass with a few big stones (frames the right edge low)
    mound = np.zeros((H, W), bool)
    for cx, cy, rx, ry in FG_MOUND:
        mound |= ellipse(cx, cy, rx, ry)
    n = wnoise("mound", XX / 9.0, YY / 4.0)
    v = 1.0 + (n - 0.5) * 2.4 + (BAY - 0.5) * 0.35 + (YY - 650) / 80.0 * -0.6
    col = np.array(R("f0", "f1", "g0", "g1", "g2"), np.int16)[np.clip(np.round(v), 0, 4).astype(int)]
    L[mound] = col[mound]
    for k, (cx, base, w, h) in enumerate(FG_MOUND_ROCKS):
        m = rock(L, cx, base, w, h, ("mrock", k))
        L[m] = SHADE_LUT[L[m]]                                    # rocks in the mound sit in shade
    top = mound & ~np.roll(mound, 1, 0)
    for y, x in zip(*np.nonzero(top)):
        if hval("mbs", int(x)) < 0.4:
            continue
        h = 6 + int(hval("mb", int(x)) * 18)
        lean = -1 if hval("mbl", int(x)) < 0.6 else 1
        for k in range(h):
            px(L, x + (lean * (k - h // 2) // 4 if k > h // 2 else 0), y - k, "g1" if k < h - 3 else "g3")
    return L


# ============================================================================ guides (hidden, locked)
def paint_guides():
    L = new()
    L[:, CX - 1] = I["gd-axis"]
    L[HZ, :] = I["gd-horizon"]
    for x in (W // 3, 2 * W // 3):
        L[::3, x] = I["gd-third"]
    for y in (H // 3, 2 * H // 3):
        L[y, ::3] = I["gd-third"]
    x0, y0 = CROP_640
    rect(L, x0, y0, x0 + CAM_W - 1, y0, "gd-pin"); rect(L, x0, y0 + CAM_H - 1, x0 + CAM_W - 1, y0 + CAM_H - 1, "gd-pin")
    rect(L, x0, y0, x0, y0 + CAM_H - 1, "gd-pin"); rect(L, x0 + CAM_W - 1, y0, x0 + CAM_W - 1, y0 + CAM_H - 1, "gd-pin")
    hx, hy = HEROINE_FOOT
    rect(L, hx - 4, hy, hx + 4, hy, "gd-pin"); rect(L, hx, hy - 4, hx, hy + 4, "gd-pin")
    return L


# ============================================================================ scene assembly
def composite_idx(layers, names):
    out = new()
    for n in names:
        m = layers[n] >= 0
        out[m] = layers[n][m]
    return out


def neighbour_stack(L):
    p = np.pad(L, 1, mode="edge")
    return np.stack([p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                     if (dy, dx) != (0, 0)])


DESPECKLE_LAYERS = ("pool-basin", "basin-vegetation", "foreground-debris", "capitol-grounds-trees",
                    "union-square-far", "hill-mist", "terrace-lawn", "fg-framing", "clouds", "sky")


def despeckle(layers, passes=2):
    """Isolated single texels >= 40 luma brighter than all 8 composited neighbours (the 'pale fleck' defect of the
    v04/v01 audits) are recoloured, in their own layer, to the most common neighbouring colour. Architecture layers
    (dome, west-front, capitol-damage) and the survey props keep their deliberate highlights."""
    fixed = 0
    for _ in range(passes):
        comp = composite_idx(layers, ART_LAYERS)
        l = LUMA[comp]
        nb = neighbour_stack(comp)
        nl = LUMA[np.maximum(nb, 0)]
        iso = (l - nl.max(0) >= 40)
        for y, x in zip(*np.nonzero(iso)):
            owner = next(n for n in reversed(ART_LAYERS) if layers[n][y, x] >= 0)
            if owner not in DESPECKLE_LAYERS and not (owner == "capitol-damage" and y >= 330):
                continue
            layers[owner][y, x] = np.bincount(nb[:, y, x][nb[:, y, x] >= 0]).argmax()
            fixed += 1
    return fixed


def scene():
    layers = {}
    layers["sky"] = paint_sky()
    layers["clouds"] = paint_clouds()
    layers["dome"] = paint_dome()
    layers["west-front"] = paint_west_front()
    layers["terrace-lawn"] = paint_terrace_lawn()
    layers["capitol-damage"] = paint_capitol_damage(composite_idx(layers, ["sky", "clouds"]))
    layers["capitol-grounds-trees"] = paint_grounds_trees()
    layers["hill-mist"] = new()
    layers["union-square-far"] = paint_union_square()
    ff = floor_fields()
    layers["pool-basin"] = paint_pool(ff)
    layers["basin-vegetation"] = paint_vegetation(ff)
    layers["foreground-debris"] = paint_debris()
    layers["survey-props"] = new()
    layers["fg-framing"] = paint_fg()
    layers["guides"] = paint_guides()
    # mist is baked from what lies under it (layers 1..7): editable as its own layer
    layers["hill-mist"] = paint_mist(composite_idx(layers, LAYERS[:7]))
    # the far trees beyond the pool sit in lighter mist too (second pass over their own texels only)
    us = layers["union-square-far"]
    for y in range(400, 444):
        s = mist_strength(y) * 0.8
        n = wnoise("mist2", XX[y] / 20.0, np.full(W, y / 2.0)) * 0.7 + BAY[y] * 0.3
        hit = (us[y] >= 0) & (n < s)
        us[y, hit] = HAZE_LUT[us[y, hit]]
    layers["survey-props"] = paint_survey(composite_idx(layers, LAYERS[:12]))
    fixed = despeckle(layers)
    return {"layers": layers, "despeckled_texels": fixed, "spr": heroine_48()}


# ============================================================================ raster helpers / runtime stack
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


def heroine_48():
    """Approved v8 static south idle (96 texels = 48 logical px) sampled at 2:1 (same sampling as v01)."""
    a = np.array(Image.open(rp(HEROINE_REL)).convert("RGBA"))
    ys, xs = np.nonzero(a[..., 3])
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = a.shape[:2]
    small = np.array(Image.fromarray(a, "RGBA").resize((max(1, w // 2), h // 2), Image.NEAREST))
    small[..., 3] = np.where(small[..., 3] >= 128, 255, 0)
    return small


def paste(dst, spr, x, ybase):
    h, w = spr.shape[:2]
    x0, y0 = x - w // 2, ybase - h + 1
    for j in range(h):
        for i in range(w):
            if spr[j, i, 3] and 0 <= x0 + i < W and 0 <= y0 + j < H:
                dst[y0 + j, x0 + i] = spr[j, i]


def heroine_mask(spr):
    m = np.zeros((H, W), bool)
    sh, sw = spr.shape[:2]
    x0, y0 = HEROINE_FOOT[0] - sw // 2, HEROINE_FOOT[1] - sh + 1
    m[y0:y0 + sh, x0:x0 + sw] = spr[..., 3] == 255
    return m


def runtime_still(rgba, spr):
    """Proposed cinematic draw order: base (layers 1-13 merged) -> heroine sprite at her pin -> fg-framing."""
    out = composite_rgba(rgba, BASE_LAYERS)
    paste(out, spr, *HEROINE_FOOT)
    fm = rgba["fg-framing"][..., 3] == 255
    out[fm] = rgba["fg-framing"][fm]
    return out


def crop640(still):
    x0, y0 = CROP_640
    return still[y0:y0 + CAM_H, x0:x0 + CAM_W]


# ============================================================================ containers
DT = (2026, 10, 16, 4, 49, 4)


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
    lines = ["GIMP Palette", f"Name: {SLUG}_{AREA}_vista-palette_{VER}", "Columns: 8", "#"]
    for n, h in PALETTE:
        r, g, b = (int(h[j:j + 2], 16) for j in (0, 2, 4))
        lines.append(f"{r:3d} {g:3d} {b:3d}\t{n}")
    return ("\n".join(lines) + "\n").encode()


def artefacts(sc):
    rgba = {n: to_rgba(sc["layers"][n]) for n in LAYERS}
    flat = composite_rgba(rgba, ART_LAYERS)
    comp_png = png_bytes(flat)
    files = {"pxo": make_pxo(rgba, comp_png), "ora": make_ora(rgba, comp_png), "gpl": make_gpl()}
    return rgba, flat, files


def names():
    return {"pxo": fname("vista-15layer", "pxo"), "ora": fname("vista-15layer", "ora"),
            "gpl": fname("vista-palette", "gpl"), "flat": fname("vista-flat-art", "png"),
            "manifest": fname("vista-manifest", "json"),
            "still": fname("godot-vista-1280x720", "png"),
            "crop": fname("godot-cam640x360-landmark", "png"),
            "report": fname("technical-check-report", "json")}


# ============================================================================ metrics
def luma_img(a):
    return a[..., :3].astype(np.int32) @ np.array([299, 587, 114]) // 1000


def isolated_bright(img, rows, exclude=None):
    """Single texels >= 40 luma brighter than all 8 neighbours (the 'pale fleck' defect of the v04/v01 audits).
    `exclude` masks out the approved heroine sprite, whose own highlights are not scene art."""
    l = luma_img(img)
    p = np.pad(l, 1, mode="edge")
    nb = np.stack([p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                   if (dy, dx) != (0, 0)])
    iso = (l - nb.max(0) >= 40)
    m = np.zeros((H, W), bool); m[rows[0]:rows[1]] = True
    if exclude is not None:
        m &= ~exclude
    ys, xs = np.nonzero(iso & m)
    return int(len(ys)), [[int(x), int(y)] for y, x in zip(ys[:12], xs[:12])]


def block_repetition(img, rows, b=16):
    """Share of b x b blocks inside `rows` whose exact pixels occur at least twice (v04 repetition metric)."""
    seen = {}
    y0, y1 = rows
    tot = 0
    for y in range(y0, y1 - b + 1, b):
        for x in range(0, W - b + 1, b):
            k = img[y:y + b, x:x + b].tobytes()
            seen[k] = seen.get(k, 0) + 1
            tot += 1
    dup = sum(c for c in seen.values() if c > 1)
    return round(dup / max(1, tot), 4)


def row_periodicity(img, rows):
    """Strongest normalised autocorrelation of the DETRENDED per-row mean luma at lags 6..40 (a running-bond wall
    shows a strong peak at its course height; a foreshortened floor does not). Detrending (minus a 25-row moving
    mean) removes the slow top-to-bottom value gradient, which otherwise scores as 'periodic' at every lag."""
    l = luma_img(img)[rows[0]:rows[1]].astype(np.float64)
    prof = l.mean(1)
    k = 25
    pad = np.pad(prof, k // 2, mode="edge")
    prof = prof - np.convolve(pad, np.ones(k) / k, mode="valid")
    best = 0.0
    for lag in range(6, 41):
        a, b2 = prof[:-lag], prof[lag:]
        den = math.sqrt((a * a).sum() * (b2 * b2).sum()) or 1.0
        best = max(best, float((a * b2).sum() / den))
    return round(best, 3)


def bbox(mask):
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


def dome_metrics(layers):
    d = layers["dome"] >= 0
    bb = bbox(d)
    asym = []
    for y in range(bb[1], bb[3] + 1):
        xs = np.nonzero(d[y])[0]
        if len(xs) and abs((xs.min() + xs.max()) - (2 * CX - 1)) > 1:
            asym.append(int(y))
    return {"dome_bbox": bb, "statue_tip_row": bb[1], "silhouette_rows_asymmetric_over_1px": asym}


def v01_layers():
    """Read the v01 .pxo (read-only) and return its RGBA layers by name."""
    with zipfile.ZipFile(io.BytesIO(read_bytes(rp(V01_PXO)))) as z:
        dj = json.loads(z.read("data.json"))
        out = {}
        for li, l in enumerate(dj["layers"], start=1):
            raw = z.read(f"image_data/frames/1/layer_{li}")
            out[l["name"]] = np.frombuffer(raw, np.uint8).reshape(dj["size_y"], dj["size_x"], 4)
    return out


def v01_comparison(still, rgba):
    """Direct pixel comparison against v01 (its Godot 1280x720 capture and its .pxo layers)."""
    v1 = decode(read_bytes(rp(V01_CAPTURE)))[2]
    v1l = v01_layers()
    cap1 = (np.zeros((H, W), bool))
    for n in ("dome", "west-front", "olmsted-terrace"):
        cap1 |= v1l[n][..., 3] == 255
    cap2 = np.zeros((H, W), bool)
    for n in ("dome", "west-front", "terrace-lawn", "capitol-damage"):
        cap2 |= rgba[n][..., 3] == 255
    cap2[TERRACE_FOOT + 1:] = False
    b1, b2 = bbox(cap1), bbox(cap2)
    lower = (H // 2, H)
    # v01's walkable foreground wall = its plaza-ground layer (running-bond paving + lawn panels)
    wall1 = float((v1l["plaza-ground"][..., 3] == 255).mean())
    pool2 = np.zeros((H, W), bool); pool2[POOL_TOP:] = True
    exposed2 = (rgba["pool-basin"][..., 3] == 255) & np.isin(luma_img(rgba["pool-basin"]), [int(LUMA[c]) for c in CONC + R("q0", "q1")])
    exposed2 &= ~(rgba["basin-vegetation"][..., 3] == 255) & ~(rgba["foreground-debris"][..., 3] == 255)
    dmg1 = int((v1l["arch-ruin-survey"][..., 3] == 255)[:177].sum())
    dmg2 = int(((rgba["capitol-damage"][..., 3] == 255) & cap2).sum())
    veg = rgba["basin-vegetation"][..., 3] == 255
    sky_l = luma_img(rgba["sky"])
    def capitol_vs_sky(img, mask, bb):
        x0, y0, x1, y1 = bb
        ring = np.zeros((H, W), bool); ring[max(0, y0 - 20):y1, max(0, x0 - 40):min(W, x1 + 40)] = True
        return int(abs(luma_img(img)[mask].mean() - luma_img(img)[ring & ~mask].mean()))
    return {
        "v01_capture": V01_CAPTURE,
        "texels_differing_v01_vs_v02_1280x720": int((v1 != still).any(axis=2).sum()),
        "share_differing": round(float((v1 != still).any(axis=2).mean()), 4),
        "capitol_bbox": {"v01": b1, "v02": b2},
        "capitol_height_share_of_frame": {"v01": round((b1[3] - b1[1] + 1) / H, 3),
                                          "v02": round((b2[3] - b2[1] + 1) / H, 3)},
        "capitol_width_share_of_frame": {"v01": round((b1[2] - b1[0] + 1) / W, 3),
                                         "v02": round((b2[2] - b2[0] + 1) / W, 3)},
        "capitol_area_texels": {"v01": int(cap1.sum()), "v02": int(cap2.sum())},
        "capitol_vs_surround_luma_contrast": {"v01": capitol_vs_sky(v1, cap1, b1), "v02": capitol_vs_sky(still, cap2, b2)},
        "foreground_wall_or_paving_share_of_frame": {"v01_plaza_ground_layer": round(wall1, 3),
                                                     "v02_exposed_concrete": round(float(exposed2.mean()), 3)},
        "lower_half_16px_block_repetition": {"v01": block_repetition(v1, lower), "v02": block_repetition(still, lower)},
        "lower_half_row_periodicity_lag6_40": {"v01": row_periodicity(v1, lower), "v02": row_periodicity(still, lower)},
        "heroine_foot_offset_from_axis_px": {"v01": abs(640 - 640), "v02": abs(HEROINE_FOOT[0] - CX)},
        "tripod_offset_from_axis_px": {"v01": abs(548 - 640), "v02": abs(TRIPOD[0] - CX)},
        "heroine_height_vs_capitol_height": {"v01": round(48 / (b1[3] - b1[1] + 1), 3),
                                             "v02": round(48 / (b2[3] - b2[1] + 1), 3)},
        "damage_texels_on_capitol": {"v01_arch_ruin_survey_rows_0_176": dmg1, "v02_capitol_damage": dmg2},
        "basin_vegetation_left_vs_right_texels": {"left": int(veg[:, :CX].sum()), "right": int(veg[:, CX:].sum())},
        "distinct_colours_in_still": {"v01": int(len(np.unique(v1[..., :3].reshape(-1, 3), axis=0))),
                                      "v02": int(len(np.unique(still[..., :3].reshape(-1, 3), axis=0)))},
        "sky_rows_mean_luma_behind_dome": int(sky_l[TIP:PERI_COLS[1], CX - 80:CX + 80].mean()),
    }


def static_checks(sc, rgba, flat):
    layers, spr = sc["layers"], sc["spr"]
    v = {}
    v["canvas_1280x720_all_layers"] = all(rgba[n].shape == (H, W, 4) for n in LAYERS)
    v["base_layer_opaque"] = bool((rgba["sky"][..., 3] == 255).all())
    v["binary_alpha_all_layers"] = all(bool(np.isin(rgba[n][..., 3], (0, 255)).all()) for n in LAYERS)
    used = set()
    for n in ART_LAYERS:
        used |= set(np.unique(layers[n][layers[n] >= 0]).tolist())
    v["art_layers_palette_only"] = all(0 <= u < N_ART for u in used)
    flat_cols = {tuple(c) for c in np.unique(flat[..., :3].reshape(-1, 3), axis=0).tolist()}
    v["flat_colours_subset_of_palette"] = flat_cols <= {tuple(c) for c in RGB[:N_ART].tolist()}
    v["flat_opaque"] = bool((flat[..., 3] == 255).all())
    still = runtime_still(rgba, spr)
    # landmark prominence and framing
    cap = np.zeros((H, W), bool)
    for n in ("dome", "west-front", "terrace-lawn"):
        cap |= layers[n] >= 0
    cap[TERRACE_FOOT + 1:] = False
    cb = bbox(cap)
    v["capitol_band_at_least_40pct_of_frame_height"] = (cb[3] - cb[1] + 1) / H >= 0.40
    dm = dome_metrics(layers)
    x0, y0 = CROP_640
    db = dm["dome_bbox"]
    v["crop640_contains_whole_dome_with_8px_headroom"] = db[1] - y0 >= 8 and x0 <= db[0] and db[2] < x0 + CAM_W \
        and db[3] < y0 + CAM_H
    v["crop640_contains_capitol_tip_to_terrace_foot"] = y0 <= TIP - 8 and TERRACE_FOOT < y0 + CAM_H
    v["dome_silhouette_symmetric_below_statue"] = not [y for y in dm["silhouette_rows_asymmetric_over_1px"]
                                                       if y > STATUE[1]]
    # heroine: scale, perspective, placement
    hm = heroine_mask(spr)
    hb = bbox(hm)
    v["heroine_48_logical_px"] = spr.shape[0] == 48
    v["heroine_scale_matches_camera"] = abs(spr.shape[0] - 1.7 * px_per_m(D_FIGURES)) <= 1.0 and \
        HEROINE_FOOT[1] == int(round(row_of(D_FIGURES)))
    wf = layers["west-front"] >= 0
    wb = bbox(wf)
    west_front_m = (wb[2] - wb[0] + 1) / px_per_m(D_CAPITOL)
    v["capitol_scale_matches_camera"] = abs(west_front_m - 229.0) / 229.0 < 0.03
    v["heroine_and_tripod_off_dome_axis_by_160px"] = abs(HEROINE_FOOT[0] - CX) >= 160 and abs(TRIPOD[0] - CX) >= 160
    v["heroine_below_capitol_no_overlap"] = hb[1] > TERRACE_FOOT and not bool((hm & cap).any())
    v["heroine_not_covered_by_fg_framing"] = not bool((hm & (layers["fg-framing"] >= 0)).any())
    # drained pool: no water / sky colours on the basin floor
    floor = composite_idx(layers, ["pool-basin", "basin-vegetation", "foreground-debris"])
    pm = np.zeros((H, W), bool); pm[POOL_TOP:] = True
    v["drained_pool_no_water_or_sky_texels"] = not bool(np.isin(floor[pm & (floor >= 0)], list(WATER_OR_SKY)).any())
    hpad = hm | np.roll(hm, 1, 0) | np.roll(hm, -1, 0) | np.roll(hm, 1, 1) | np.roll(hm, -1, 1)
    fl_fg, fl_fg_where = isolated_bright(still, (TERRACE_FOOT, H), exclude=hpad)
    fl_bd, fl_bd_where = isolated_bright(still, (0, TERRACE_FOOT))
    v["no_isolated_bright_flecks_rows_380_719"] = fl_fg == 0
    comp = v01_comparison(still, rgba)
    v["capitol_taller_share_than_v01"] = comp["capitol_height_share_of_frame"]["v02"] > \
        comp["capitol_height_share_of_frame"]["v01"]
    v["lower_half_repetition_below_v01"] = comp["lower_half_16px_block_repetition"]["v02"] < \
        comp["lower_half_16px_block_repetition"]["v01"]
    v["lower_half_row_periodicity_below_v01"] = comp["lower_half_row_periodicity_lag6_40"]["v02"] < \
        comp["lower_half_row_periodicity_lag6_40"]["v01"]
    v["damage_on_capitol_more_than_v01"] = comp["damage_texels_on_capitol"]["v02_capitol_damage"] > \
        comp["damage_texels_on_capitol"]["v01_arch_ruin_survey_rows_0_176"]
    v["basin_vegetation_asymmetric_left_heavier"] = comp["basin_vegetation_left_vs_right_texels"]["left"] > \
        1.5 * comp["basin_vegetation_left_vs_right_texels"]["right"]
    return {"verdicts": v, "dome": dm, "capitol_bbox": cb, "west_front_width_m_at_camera": round(west_front_m, 1),
            "heroine_bbox": hb, "isolated_bright_flecks": {"rows_380_719": fl_fg, "rows_380_719_examples": fl_fg_where,
                                                           "rows_0_379": fl_bd, "rows_0_379_examples": fl_bd_where},
            "palette": {"art_colours": N_ART, "used_in_flat": len(flat_cols)},
            "despeckled_texels": sc["despeckled_texels"], "v01_comparison": comp,
            "camera": {"F_px": F, "eye_m": EYE, "horizon_row": HZ, "capitol_distance_m": D_CAPITOL,
                       "capitol_px_per_m": round(px_per_m(D_CAPITOL), 2), "figures_distance_m": D_FIGURES,
                       "figures_px_per_m": round(px_per_m(D_FIGURES), 2), "heroine_foot": list(HEROINE_FOOT),
                       "tripod_pivot": list(TRIPOD), "crop_640x360_xy": list(CROP_640)}}


# ============================================================================ preview / build / manifest
def preview(outdir):
    sc = scene()
    rgba, flat, files = artefacts(sc)
    os.makedirs(outdir, exist_ok=True)
    Image.fromarray(flat, "RGBA").save(os.path.join(outdir, "flat.png"))
    st = runtime_still(rgba, sc["spr"])
    Image.fromarray(st, "RGBA").save(os.path.join(outdir, "still.png"))
    Image.fromarray(crop640(st), "RGBA").save(os.path.join(outdir, "crop640.png"))
    for n in ART_LAYERS:
        Image.fromarray(rgba[n], "RGBA").save(os.path.join(outdir, f"layer_{LAYERS.index(n) + 1:02d}_{n}.png"))
    rep = static_checks(sc, rgba, flat)
    with open(os.path.join(outdir, "checks.json"), "w") as f:
        json.dump(rep, f, indent=1)
    print(json.dumps(rep["verdicts"], indent=1))
    print(json.dumps(rep["v01_comparison"], indent=1))
    print("flecks", rep["isolated_bright_flecks"], "despeckled", rep["despeckled_texels"])


def write_new(path, data):
    if os.path.exists(_fs(path)):
        if read_bytes(path) != data:
            raise SystemExit(f"refusing to overwrite a different existing file: {path}")
        return "unchanged"
    with open(_fs(path), "xb") as f:
        f.write(data)
    return "written"


AOC_REFS = {
    "dome": "https://www.aoc.gov/explore-capitol-campus/buildings-grounds/capitol-building/capitol-dome",
    "olmsted_terrace": "https://www.aoc.gov/explore-capitol-campus/buildings-grounds/capitol-grounds/olmsted-terrace",
}


def v01_untouched():
    return {rel: sha(read_bytes(rp(rel))) == h for rel, h in V01_LOCK.items()}


def manifest(sc, rgba, files, rep):
    nm = names()
    return {
        "project": SLUG, "area": "washington-capitol-dome-west-cinematic-vista", "run": RUN, "version": "v02",
        "status": "UNAPPROVED test-only cinematic vista candidate (non-walkable). Not accepted art, not "
                  "runtime-integrated. Acceptance is creator review only; science scene art stays 0/11.",
        "art_approved": False, "runtime_integrated": False, "counters_changed": False, "walkable": False,
        "relation_to_v01": f"separate candidate answering the Codex v01 audit; v01 ({V01_RUN}) is read-only and "
                           "re-hashed by `check`",
        "relation_to_v04_walkable_room": "not a replacement; the walkable v04 west-grounds room is untouched",
        "authoring_route": {
            "method": "deterministic Python tool with hand-written placement tables, authored and run by Claude "
                      "(Claude Code, claude.ai Max subscription, firstParty; no API key, no credits, no image model); "
                      "writes a native pxo_version 7 .pxo and an .ora with 15 named layers",
            "pixelorama_gui_paint_pass": False,
            "disclosure": "no desktop/computer-use access to the Pixelorama GUI in this session: hand-authored "
                          "tables -> .pxo/.ora -> Pixelorama 1.2.3 headless export, compared texel by texel",
            "no_reference_pixels_copied": True},
        "references": {"aoc_pages_text_only": AOC_REFS, "codex_v01_audit": AUDIT_REL},
        "canvas": {"w": W, "h": H, "camera": "pinhole, eye-level telephoto from the drained Capitol Reflecting Pool "
                                             "looking east along the Mall axis",
                   "camera_numbers": rep["camera"],
                   "gameplay_camera": "640x360 logical viewport (window 1280x720, integer 2x); the 640x360 "
                                      "capture is the landmark window at CROP_640",
                   "scale_reference": {"file": HEROINE_REL, "logical_height_px": int(sc["spr"].shape[0])}},
        "layers_bottom_to_top": [
            {"index": i + 1, "name": n, "visible": n != "guides", "locked": n == "guides",
             "runtime_export": ("merged into base" if n in BASE_LAYERS else
                                "overlay above the heroine" if n == "fg-framing" else "never exported"),
             "opaque_texels": int((rgba[n][..., 3] == 255).sum())} for i, n in enumerate(LAYERS)],
        "palette": [{"name": n, "hex": "#" + h} for n, h in PALETTE],
        "guide_palette": [{"name": n, "hex": "#" + h} for n, h in GUIDE_PALETTE],
        "static_checks": rep,
        "files_sha256_bytes": {nm[k]: sha(v) for k, v in files.items()},
        "tool": {"file": TOOL_REL, "sha256_text_lf_v1": sha_text(read_bytes(os.path.abspath(__file__))),
                 "python": sys.version.split()[0], "pillow": Image.__version__, "numpy": np.__version__},
    }


def build_all():
    _VN_RESET()
    sc = scene()
    rgba, flat, files = artefacts(sc)
    files["flat"] = png_bytes(flat)
    return sc, rgba, flat, files


def _VN_RESET():
    _LAT.clear()


def build():
    sc, rgba, flat, files = build_all()
    if build_all()[3] != files:
        raise SystemExit("build is not deterministic")
    if not all(v01_untouched().values()):
        raise SystemExit("v01 files changed; refusing to build")
    rep = static_checks(sc, rgba, flat)
    cand = rp(CAND_REL)
    os.makedirs(_fs(cand), exist_ok=True)
    nm = names()
    for k in ("pxo", "ora", "flat", "gpl"):
        print(write_new(os.path.join(cand, nm[k]), files[k]), nm[k])
    man = manifest(sc, rgba, files, rep)
    print(write_new(os.path.join(cand, nm["manifest"]), (json.dumps(man, indent=2) + "\n").encode()), nm["manifest"])
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
    tmp = tempfile.mkdtemp(prefix="wb-vista2gate-")
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


# ============================================================================ Godot gate (throwaway temp project)
GODOT_SCRIPT = r'''extends SceneTree
# Test-only, nonruntime: load the split layer PNGs from the .ora with Image.load_from_file, hash the raw RGBA,
# composite the cinematic still (base layers -> heroine at her pin -> fg-framing) with blend_rect, save the
# 1280x720 still and cut the native 640x360 landmark window.
func _init():
	var a = OS.get_cmdline_user_args()
	var dir: String = a[0]
	var cases = JSON.parse_string(FileAccess.get_file_as_string(dir + "/cases.json"))
	var out = {"layers": {}}
	var imgs = {}
	for n in cases["art_layers"]:
		var img = Image.load_from_file(dir + "/" + n + ".png")
		var fmt_in = img.get_format()
		if fmt_in != Image.FORMAT_RGBA8:
			img.convert(Image.FORMAT_RGBA8)
		var h = HashingContext.new()
		h.start(HashingContext.HASH_SHA256)
		h.update(img.get_data())
		out["layers"][n] = {"w": img.get_width(), "h": img.get_height(), "format_loaded": fmt_in, "sha256_rgba": h.finish().hex_encode()}
		imgs[n] = img
	var hero = Image.load_from_file(dir + "/heroine48.png")
	hero.convert(Image.FORMAT_RGBA8)
	out["heroine_h"] = hero.get_height()
	var foot = cases["foot"]
	var st = imgs[cases["base_layers"][0]].duplicate()
	for i in range(1, cases["base_layers"].size()):
		st.blend_rect(imgs[cases["base_layers"][i]], Rect2i(0, 0, 1280, 720), Vector2i(0, 0))
	var hp = Vector2i(int(foot[0]) - hero.get_width() / 2, int(foot[1]) - hero.get_height() + 1)
	st.blend_rect(hero, Rect2i(0, 0, hero.get_width(), hero.get_height()), hp)
	st.blend_rect(imgs["fg-framing"], Rect2i(0, 0, 1280, 720), Vector2i(0, 0))
	st.save_png(dir + "/still.png")
	var c = cases["crop"]
	var cam = st.get_region(Rect2i(int(c[0]), int(c[1]), 640, 360))
	cam.save_png(dir + "/crop.png")
	out["sizes"] = [st.get_width(), st.get_height(), cam.get_width(), cam.get_height()]
	var f = FileAccess.open(dir + "/godot_report.json", FileAccess.WRITE)
	f.store_string(JSON.stringify(out))
	f.close()
	print("GODOT_GATE_DONE")
	quit()
'''


def godot_gate(godot, files, rgba):
    """Throwaway Godot project under %TEMP% with APPDATA also redirected there: nothing touches game/ or the real
    Godot user dir. Returns the 1280x720 still and the 640x360 landmark window."""
    tmp = tempfile.mkdtemp(prefix="wb-vista2godot-")
    rep = {"godot": GODOT_REL, "godot_sha256": sha(read_bytes(godot)), "steps": {}}
    caps = {}
    proj_name = f"wdc-vista2-gate-{RUN_ID}"
    try:
        proj = os.path.join(tmp, "proj"); os.makedirs(proj)
        data = os.path.join(tmp, "data"); os.makedirs(data)
        fake = os.path.join(tmp, "appdata"); os.makedirs(fake)
        with open(os.path.join(proj, "project.godot"), "w", newline="\n") as f:
            f.write(f'config_version=5\n\n[application]\nconfig/name="{proj_name}"\n')
        with open(os.path.join(proj, "gate.gd"), "w", newline="\n") as f:
            f.write(GODOT_SCRIPT)
        with zipfile.ZipFile(io.BytesIO(files["ora"])) as z:
            for n in ART_LAYERS:
                with open(os.path.join(data, f"{n}.png"), "wb") as f:
                    f.write(z.read(f"data/{n}.png"))
        spr = heroine_48()
        Image.fromarray(spr, "RGBA").save(os.path.join(data, "heroine48.png"))
        with open(os.path.join(data, "cases.json"), "w") as f:
            json.dump({"art_layers": ART_LAYERS, "base_layers": BASE_LAYERS, "foot": list(HEROINE_FOOT),
                       "crop": list(CROP_640)}, f)
        env = dict(os.environ); env["APPDATA"] = fake
        p = subprocess.run([godot, "--headless", "--path", proj, "--script", "gate.gd", "--", data],
                           capture_output=True, text=True, timeout=600, env=env, encoding="utf-8", errors="replace")
        rep["exit_code"] = p.returncode
        rep["printed_done"] = "GODOT_GATE_DONE" in p.stdout
        gr = json.load(open(os.path.join(data, "godot_report.json")))
        lay_ok = {}
        for n in ART_LAYERS:
            g = gr["layers"][n]
            lay_ok[n] = g["w"] == W and g["h"] == H and g["sha256_rgba"] == sha(np.ascontiguousarray(rgba[n]).tobytes())
            rep["steps"][n] = {**g, "exact_texels_vs_source": lay_ok[n]}
        sb = read_bytes(os.path.join(data, "still.png"))
        got = decode(sb)[2]
        exp = runtime_still(rgba, spr)
        cbb = read_bytes(os.path.join(data, "crop.png"))
        cgot = decode(cbb)[2]
        cexp = crop640(exp)
        rep["steps"]["still"] = {"size": list(got.shape[1::-1]), "equals_python_runtime_still": bool(
            got.shape == exp.shape and (got == exp).all()), "differing_texels": int((got != exp).any(axis=2).sum())}
        rep["steps"]["crop"] = {"rect_xy": list(CROP_640), "size": list(cgot.shape[1::-1]),
                                "equals_python": bool(cgot.shape == (CAM_H, CAM_W, 4) and (cgot == cexp).all()),
                                "differing_texels": int((cgot != cexp).any(axis=2).sum()) if cgot.shape == cexp.shape else None}
        caps = {"still": sb, "crop": cbb}
        rep["heroine_h_in_godot"] = gr.get("heroine_h")
        rep["verdicts"] = {"godot_loads_layers_exact": all(lay_ok.values()) and rep["exit_code"] == 0,
                           "godot_still_1280x720_equals_python": rep["steps"]["still"]["equals_python_runtime_still"],
                           "godot_crop_640x360_equals_python": rep["steps"]["crop"]["equals_python"],
                           "godot_heroine_48_px": gr.get("heroine_h") == 48,
                           "godot_wrote_nothing_outside_temp": not os.path.isdir(
                               os.path.join(os.environ.get("APPDATA", ""), "Godot", "app_userdata", proj_name))}
    finally:
        shutil.rmtree(_fs(tmp), ignore_errors=True)
    return rep, caps


# ============================================================================ check
def check(exe, write_report, use_pixelorama, godot=None):
    sc, rgba, flat, files = build_all()
    nm = names()
    cand = rp(CAND_REL)
    for k in ("pxo", "ora", "flat", "gpl"):
        if read_bytes(os.path.join(cand, nm[k])) != files[k]:
            raise SystemExit(f"{nm[k]} on disk differs from a fresh rebuild")
    st = static_checks(sc, rgba, flat)
    rep = {"run": RUN, "gates": dict(st["verdicts"]), "static": st}
    gates = rep["gates"]
    v1 = v01_untouched()
    rep["v01_lock"] = v1
    gates["v01_untouched"] = all(v1.values())
    with zipfile.ZipFile(io.BytesIO(files["pxo"])) as z:
        dj = json.loads(z.read("data.json"))
    gates["pxo_layer_stack_is_15_named_layers_guides_hidden_locked"] = \
        [l["name"] for l in dj["layers"]] == LAYERS and len(LAYERS) == 15 and \
        [l["visible"] for l in dj["layers"]] == [n != "guides" for n in LAYERS] and \
        [l["locked"] for l in dj["layers"]] == [n == "guides" for n in LAYERS]
    gates["build_deterministic"] = build_all()[3] == files
    caps = {}
    if use_pixelorama:
        rep["pixelorama"] = pixelorama_gate(exe, files, rgba, flat)
        gates.update(rep["pixelorama"]["verdicts"])
    if godot:
        rep["godot"], caps = godot_gate(godot, files, rgba)
        gates.update(rep["godot"]["verdicts"])
        if caps:  # direct pixel comparison of the actual Godot capture against v01's Godot capture
            g = decode(caps["still"])[2]
            v1c = decode(read_bytes(rp(V01_CAPTURE)))[2]
            rep["godot_capture_vs_v01_capture"] = {"differing_texels": int((g != v1c).any(axis=2).sum()),
                                                   "share": round(float((g != v1c).any(axis=2).mean()), 4)}
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
