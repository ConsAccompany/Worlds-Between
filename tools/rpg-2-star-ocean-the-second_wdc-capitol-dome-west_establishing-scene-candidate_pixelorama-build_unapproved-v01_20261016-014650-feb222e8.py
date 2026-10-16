"""UNAPPROVED, TEST-ONLY v01 candidate: distant U.S. Capitol West Front + Dome establishing composition (Washington).

Deterministic Python tool authored and run by Claude (Claude Code, Opus 5.5). It writes ONE 1280x720 logical-pixel
establishing scene from a fixed palette into a 15-layer editable stack, as a native Pixelorama .pxo (pxo_version 7) and
an .ora, plus a palette (.gpl), a walkability JSON and a manifest. Nothing here is accepted art, and nothing is wired
into the game runtime: no scene, data, test, default or camera setting is touched.

AUTHORING ROUTE (disclosed). This is NOT a Pixelorama GUI paint pass. The session had no desktop/computer-use access to
the Pixelorama GUI, so it uses the route the v01-v04 west-grounds candidates used: hand-written placement tables (every
dome stage, facade bay state, grove crown, ruin item and survey prop is an explicit table entry) are rasterised by this
tool into named layers, then Pixelorama 1.2.3 itself re-exports the .pxo/.ora headless and the exports are compared
texel by texel. The .pxo opens in the GUI as 15 editable layers, so a GUI polish pass can start from it.

Why this candidate exists: the Codex v04 visual audit (docs/qa/...wdc-capitol-west-v04-codex-visual-audit_unapproved-
v01_20261016-013712-a9d83f26.md) found that the v04 walkable west-grounds scene never shows the dome, so it reads as a
generic neoclassical ruin. It asked for a separate distant dome / West Front establishing composition. v04 itself is
read-only here (`check` re-hashes its candidate files and its tool).

Composition (top of frame = east). Forced perspective, documented as such:
  * backdrop, rows 0..213 (NOT walkable): sky; the Capitol at ~1.55 px/m (dome, statue tip at row 24; West Front;
    Olmsted terrace with twin stairs and a dry exedra); the lower west lawn; flanking Olmsted tree groves; the DRAINED
    Capitol Reflecting Pool (no water texels; game fiction for 2537).
  * walkable foreground, rows 218..719, at the approved heroine scale (48 logical px): Union Square paving with a survey
    staging camp, two lawn panels (one mown camp panel, one overgrown meadow), a stair down to the Grant Memorial
    platform (off-frame west) as the entry, and two side walks around the drained pool as exits toward the v04 scene.
  The whole Capitol stack is 194 rows tall, so a 640x360 camera window centred on the heroine's body shows the ENTIRE
  dome (statue included) whenever her feet are at the overlook coping (foot row <= ~228).
Reference forms (from the Architect of the Capitol's dome and Olmsted terrace pages, text facts only, nothing copied):
  cast-iron dome on a columned peristyle, attic, ribbed shell, tholos and the Statue of Freedom; terrace walls of marble
  on a granite foundation with balustrades wrapping north, west and south; four west-side lanterns.
2537 abandonment (game fiction): missing cast-iron plates and rust on the dome's south shell, two missing peristyle
  columns, a gutted south-wing roof corner with a self-sown tree, soot over broken windows, ivy on the north wing and
  the terrace, a breached south balustrade with a rubble cone, the drained and weedy pool.
Survey context (game fiction): a scaffold tower with a beacon beside the dome, cordon and flags at the breach, a lawn
  tent, a total-station tripod at the overlook (Y-sorted), a telescoping survey mast (Y-sorted), stake lines, paint
  ticks and the camp.

Resume (2026-10-16): the session that wrote this tool hit the Claude Max session limit before `build`/`check` existed
  and before anything was written. The resumed session kept the run id (nothing had been built under it), added
  build/check and the Pixelorama/Godot gates (adapted from the v04 tool), and fixed defects seen in the first preview:
  per-tile hashes left axis-aligned stain rectangles on the paving and a 12x8 grid in the grass (now smooth value
  noise, stains decided per slab); a long 1-px cable read as a crack (removed; the mast cable is k1); 18 pale
  flecks in the walkable foreground (leaf colours, stranded paving texels in grass, a rope pinhole, despeckle pass).

Modes
  preview <dir>   render the layers, flat image, runtime stills and camera windows into <dir> (outside the repo)
  build           write the candidate files (.pxo/.ora/flat/.gpl/walkability/manifest; never overwrites a different
                  file). No captures: the only captures are the three Godot ones written by `check --write-report`.
  check           technical gates; Pixelorama 1.2.3 headless round-trip with APPDATA redirected to temp
                  (--no-pixelorama to skip); Godot 4.7.2 throwaway temp project (--no-godot to skip);
                  --write-report writes the JSON report (and the Godot captures on first run) into outputs/<RUN>/.
Run: python -I -B <this file> preview <tempdir> | build | check [--write-report] [--no-pixelorama] [--no-godot]
"""
import argparse, hashlib, io, json, math, os, shutil, subprocess, sys, tempfile, time, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
AREA = "wdc-dome-west"           # short: with "wdc-capitol-dome-west" the candidate paths reached 264-273 chars (> MAX_PATH)
VER = "unapproved-v01"
STAMP = "20261016-014650"
RUN_ID = "feb222e8"
RUN = f"{AREA}-v01_{STAMP}-{RUN_ID}"
CAND_REL = f"game/assets/environments/candidates/{RUN}"
OUT_REL = f"outputs/{RUN}"
TOOL_REL = "tools/" + os.path.basename(os.path.abspath(__file__))
AUDIT_REL = ("docs/qa/rpg-2-star-ocean-the-second_wdc-capitol-west-v04-codex-visual-audit_unapproved-v01_"
             "20261016-013712-a9d83f26.md")
HEROINE_REL = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_"
               "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
V04_RUN = "wdc-capitol-west-v04_20261016-004457-a17af0a6"
V04_LOCK = {  # sha256 of the read-only v04 walkable-scene candidate files and tool (taken before this tool existed)
    f"game/assets/environments/candidates/{V04_RUN}/rpg-2-star-ocean-the-second_wdc-capitol-west_scene-editable-"
    "11layer_unapproved-v04_20261016-004457-a17af0a6.ora": "640225cbfc5e51d13e257d3f0315227411b375c4118f903a38dc36565d1ab0a2",
    f"game/assets/environments/candidates/{V04_RUN}/rpg-2-star-ocean-the-second_wdc-capitol-west_scene-editable-"
    "11layer_unapproved-v04_20261016-004457-a17af0a6.pxo": "d440328c701e793818900dd933afeb091332a0f4bc2b82552e2a3ff0bcf87c2e",
    f"game/assets/environments/candidates/{V04_RUN}/rpg-2-star-ocean-the-second_wdc-capitol-west_scene-flat-art_"
    "unapproved-v04_20261016-004457-a17af0a6.png": "3dd46a8422a97a8dfc4f0e905770b1ba24e526c312042917f166a693a742ab91",
    f"game/assets/environments/candidates/{V04_RUN}/rpg-2-star-ocean-the-second_wdc-capitol-west_scene-manifest_"
    "unapproved-v04_20261016-004457-a17af0a6.json": "5a2e557d14425f382352c5295e9a84a0dc8f412abc9a138faca314a9c25bbabc",
    f"game/assets/environments/candidates/{V04_RUN}/rpg-2-star-ocean-the-second_wdc-capitol-west_scene-palette_"
    "unapproved-v04_20261016-004457-a17af0a6.gpl": "16679b800d34703365601f4795cc8248b34769267dacecbebe683fac2df9e12f",
    f"game/assets/environments/candidates/{V04_RUN}/rpg-2-star-ocean-the-second_wdc-capitol-west_scene-walkability_"
    "unapproved-v04_20261016-004457-a17af0a6.json": "3eba0e326cdbab16955152fb48d0a88c26bcfc5254cb0d0b9e6908b8d74d7dc5",
    "tools/rpg-2-star-ocean-the-second_washington-capitol_west-grounds-scene-candidate_pixelorama-build_unapproved-"
    "v04_20261016-004457-a17af0a6.py": "a473df85717616c8a9bdb6c2b10ef5eb0a757085207a14279dc9e6bcc1bb0be5",
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

LAYERS = ["sky", "dome", "west-front", "olmsted-terrace", "arch-ruin-survey", "far-lawn-basin", "groves",
          "plaza-ground", "ground-detail", "cast-shadows", "props-low", "survey-tripod-ysort", "survey-mast-ysort",
          "fg-occlusion", "guides"]                                                    # bottom -> top
ART_LAYERS = LAYERS[:-1]                                                              # guides: hidden, locked
BASE_LAYERS = LAYERS[:11]                                                             # merged into one base at runtime
YSORT_LAYERS = ["survey-tripod-ysort", "survey-mast-ysort"]

# ============================================================================ palette
# The 47 v04 colours (unchanged, same names) + 15 new atmospheric colours for sky, distant stone and distant foliage.
PALETTE = [
    ("ink", "1a1c22"),
    ("g0", "1f3324"), ("g1", "2c4a2c"), ("g2", "3d6234"), ("g3", "557a3c"), ("g4", "6f9145"),
    ("g5", "93ad55"), ("g6", "b9c26c"), ("g7", "d3d98a"),
    ("d0", "7f7c45"), ("d1", "a99a5e"),
    ("f0", "16262a"), ("f1", "223d3a"), ("f2", "2f5644"),
    ("e2", "2a5a52"), ("e3", "40806c"), ("e4", "6aa58a"),
    ("s0", "3a2c22"), ("s1", "5a4430"), ("s2", "7d6345"), ("s3", "a08458"), ("s4", "c6aa76"),
    ("m0", "4a4c58"), ("m1", "6e6f78"), ("m2", "93918f"), ("m3", "b8b3a8"), ("m4", "d6d0c2"), ("m5", "ece6d6"),
    ("p0", "6b5f52"), ("p1", "8d7f6c"), ("p2", "ab9d86"), ("p3", "c6b99e"),
    ("k0", "232a36"), ("k1", "3a4656"), ("k2", "5a6a7c"), ("k3", "8d9cab"),
    ("c0", "1f6f78"), ("c1", "49c6cf"), ("c2", "b4f4f0"),
    ("o0", "a34a1e"), ("o1", "e07a2e"), ("o2", "f4b860"),
    ("fl", "c79ad0"), ("bl", "eda7b6"), ("y0", "e8cf58"),
    ("r0", "9a3b34"), ("n0", "2e3f66"),
    # new in this candidate: sky / cloud
    ("sk0", "6b8092"), ("sk1", "8b9fae"), ("sk2", "aab8c0"), ("sk3", "c9d0cd"), ("cl0", "e4e2d8"), ("cl1", "b9c1c2"),
    # distant stone in shade (cool haze greys)
    ("hz0", "5d6670"), ("hz1", "7d868e"), ("hz2", "9da3a5"), ("hz3", "bdbdb5"),
    # distant foliage (haze greens)
    ("vg0", "34493f"), ("vg1", "4b6151"), ("vg2", "677b63"), ("vg3", "879474"), ("vg4", "a7ad8a"),
]
NEW_COLOURS = ["sk0", "sk1", "sk2", "sk3", "cl0", "cl1", "hz0", "hz1", "hz2", "hz3", "vg0", "vg1", "vg2", "vg3", "vg4"]
GUIDE_PALETTE = [("gd-walk", "3cdcff"), ("gd-block", "ff285a"), ("gd-pin", "ffe600"), ("gd-tick", "ffffff"),
                 ("gd-route", "ff78ff")]
ALL_PAL = PALETTE + GUIDE_PALETTE
I = {n: i for i, (n, _) in enumerate(ALL_PAL)}
RGB = np.array([[int(h[j:j + 2], 16) for j in (0, 2, 4)] for _, h in ALL_PAL], np.uint8)
N_ART = len(PALETTE)
WATER_OR_SKY = {I[n] for n in ("c0", "c1", "c2", "sk0", "sk1", "sk2", "sk3", "cl0", "cl1", "n0")}

DOME = [I[n] for n in ("hz0", "hz1", "hz2", "hz3", "m4", "m5")]          # distant lit marble / white-painted iron
VG = [I[n] for n in ("vg0", "vg1", "vg2", "vg3", "vg4")]                  # distant foliage
FOL = [I[n] for n in ("f0", "f1", "f2", "g2", "g3", "g4", "g5")]          # near foliage
GR = [I[n] for n in ("g0", "g1", "g2", "g3", "g4", "g5", "g6", "g7")]     # near grass
PAVE = [I[n] for n in ("p0", "p1", "p2", "p3")]
SOIL = [I[n] for n in ("s0", "s1", "s2", "s3")]

SHADE = {  # opaque cast-shadow colour for each art colour underneath (no semi-alpha anywhere)
    "ink": "ink", "g0": "f0", "g1": "g0", "g2": "g1", "g3": "g1", "g4": "g2", "g5": "g3", "g6": "g4", "g7": "g5",
    "d0": "g1", "d1": "d0", "f0": "f0", "f1": "f0", "f2": "f1", "e2": "f1", "e3": "e2", "e4": "e3",
    "s0": "ink", "s1": "s0", "s2": "s1", "s3": "s1", "s4": "s2",
    "m0": "ink", "m1": "m0", "m2": "m1", "m3": "m1", "m4": "m2", "m5": "m3",
    "p0": "m0", "p1": "p0", "p2": "p0", "p3": "p1",
    "k0": "ink", "k1": "k0", "k2": "k1", "k3": "k2", "c0": "k0", "c1": "c0", "c2": "c0",
    "o0": "s0", "o1": "o0", "o2": "o1", "fl": "s1", "bl": "fl", "y0": "d1", "r0": "s0", "n0": "k0",
    "sk0": "hz0", "sk1": "hz1", "sk2": "hz2", "sk3": "hz3", "cl0": "hz3", "cl1": "hz2",
    "hz0": "k1", "hz1": "hz0", "hz2": "hz1", "hz3": "hz2", "vg0": "f0", "vg1": "vg0", "vg2": "vg1", "vg3": "vg2",
    "vg4": "vg3",
}
SHADE_LUT = np.arange(len(ALL_PAL), dtype=np.int16)
for _a, _b in SHADE.items():
    SHADE_LUT[I[_a]] = I[_b]

# ============================================================================ composition table (logical px)
CX = 640                         # Capitol axis (columns 0..1279 -> axis between 639 and 640)
TIP = 24                         # Statue of Freedom tip row
# dome stages (rows inclusive) and half widths: about 1.55 px per metre (dome ~38 m peristyle, ~58 m above the roof)
STATUE = (24, 33)
THOLOS_CAP = (34, 37)
THOLOS_COLS = (38, 45)
THOLOS_RING = (46, 48)
SHELL = (49, 76)
ATTIC = (77, 86)
PERI_BAL = (87, 88)
PERI_ENT = (89, 92)
PERI_COLS = (93, 109)
STYLOBATE = (110, 112)
DRUM = (113, 121)
HW = {"tholos_ring": 9, "tholos_cols": 6, "attic": 26, "peri_bal": 30, "peri_ent": 32, "peri_cols": 30,
      "stylobate": 33, "drum": 35}
SHELL_HW = (23, 7)               # shell half width at its base / top
PERI_COLS_N = 36                 # peristyle ring: 36 columns, 10 degrees apart
PERI_MISSING = (5, 6)            # game fiction: two missing columns on the south (right) side (index from centre)
SHELL_RIBS = 30
# West Front sections (x inclusive) and roof rows: ~229 m long -> 355 px
WINGS = ((463, 535), (744, 816))           # Senate (north, left) and House (south, right) extensions
CORRIDORS = ((536, 556), (723, 743))       # connecting corridors (recessed)
CENTER = (557, 722)                        # Bulfinch central building
PAVILION = (604, 675)                      # projecting central west front with its loggia
ROOF = {"wing": 121, "corridor": 123, "center": 119, "pavilion": 116}
FACADE_BOTTOM = 158
DECK = (159, 160)
TERRACE = (404, 875)                       # west terrace wall (returns east at both ends)
TBAL = (161, 164)                          # balustrade: rail 161, balusters 162-163, base rail 164
TWALL = (165, 173)                         # marble face
TGRANITE = (174, 176)                      # granite rubble foundation
EXEDRA = (624, 655)                        # dry fountain grotto between the twin stairs
STAIR_L = 598                              # left flight foot (outer) x; right mirrored about the axis
LAWN = (177, 190)
FAR_COPING = (191, 194)                    # far coping top (191-192) + inner wall face (193-194)
BASIN = (195, 208)
NEAR_COPING = (209, 213)
BASIN_FAR_X = (470, 809)
BASIN_NEAR_X = (372, 907)
PLAZA_TOP = 214
WALK_TOP = 218
LEFT_PANEL = (236, 312, 556, 632)          # x0, y0, x1, y1 (curbed lawn, survey camp, mown)
RIGHT_PANEL = (723, 312, 1043, 632)        # overgrown meadow
BEDS = ((0, 180), (1099, 1279))            # side planting beds (non-walkable), x ranges
STEPS = (416, 684, 863, 719)               # stair down to the Grant Memorial platform (off-frame west)
SIDE_WALKS = (((300, 216), (352, 200), (420, 190), (452, 184)),         # around the drained pool, toward v04
              ((979, 216), (927, 200), (859, 190), (827, 184)))
PINS = {"spawn_entry_steps": (640, 712), "vista_axis_coping": (640, 220), "tripod_behind": (548, 223),
        "tripod_front": (548, 244), "mast_behind": (906, 236), "mast_front": (906, 262),
        "exit_north_pool_walk": (318, 222), "exit_south_pool_walk": (961, 222), "camp_tent": (430, 512),
        "meadow_sapling": (880, 470), "canopy_left_edge": (206, 236)}
TRIPOD = (548, 232)              # pivot: base centre x, contact row
MAST = (906, 248)
GODOT_VIEWS = {"vista-axis": "vista_axis_coping", "tripod-behind": "tripod_behind"}
ESTABLISHING_PIN = "vista_axis_coping"

# lighting: late afternoon sun from the south-west, behind the viewer's right shoulder -> lit from screen right;
# cast shadows fall up and to the left (north-east).
SHADOW_DIR = (-0.55, -0.35)


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
    """Deterministic hash in [0, 1) for a key (used only to vary slab tones and leaf bumps, never for placement)."""
    return int.from_bytes(hashlib.sha256(repr(key).encode()).digest()[:4], "little") / 2 ** 32


BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16 + 1 / 32
_VN = {}


def vnoise(key, cell):
    """Smooth value noise over the canvas (smoothstep-bilinear between hashed lattice values every `cell` px).
    Replaces the per-tile hashes that left axis-aligned rectangles in the paving stains and a grid in the grass."""
    if (key, cell) not in _VN:
        gw, gh = W // cell + 2, H // cell + 2
        g = np.array([[hval(key, "vn", i, j) for i in range(gw)] for j in range(gh)], np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        fx, fy = xx / cell, yy / cell
        ix, iy = fx.astype(np.int32), fy.astype(np.int32)
        tx, ty = fx - ix, fy - iy
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        top = g[iy, ix] * (1 - tx) + g[iy, ix + 1] * tx
        bot = g[iy + 1, ix] * (1 - tx) + g[iy + 1, ix + 1] * tx
        _VN[(key, cell)] = top * (1 - ty) + bot * ty
    return _VN[(key, cell)]


def quantile_cut(field, frac):
    return float(np.quantile(field, frac)) if frac > 0 else -1.0


def rect(L, x0, y0, x1, y1, c):
    x0, x1 = max(0, x0), min(W - 1, x1)
    y0, y1 = max(0, y0), min(H - 1, y1)
    if x0 <= x1 and y0 <= y1:
        L[y0:y1 + 1, x0:x1 + 1] = I[c] if isinstance(c, str) else c


def px(L, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        L[y, x] = I[c] if isinstance(c, str) else c


def line(L, x0, y0, x1, y1, c):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for k in range(n + 1):
        px(L, int(round(x0 + (x1 - x0) * k / n)), int(round(y0 + (y1 - y0) * k / n)), c)


def stamp(L, x, y, rows, cmap, reg=None):
    """Paint a hand-authored sprite (top-left at x, y). '.' is transparent; other chars map through cmap."""
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "." or ch == " ":
                continue
            px(L, x + i, y + j, cmap.get(ch, ch))
            if reg is not None and 0 <= x + i < W and 0 <= y + j < H:
                reg[y + j, x + i] = True


def ellipse(cx, cy, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W]
    return ((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - cy) / ry) ** 2 <= 1.0


def ramp_at(ramp, l, cuts):
    """Pick a ramp entry for light value l given ascending cut points (len(cuts) == len(ramp) - 1)."""
    k = 0
    while k < len(cuts) and l >= cuts[k]:
        k += 1
    return ramp[k]


def shift(ramp, idx, d):
    if idx in ramp:
        return ramp[max(0, min(len(ramp) - 1, ramp.index(idx) + d))]
    return idx


def cyl_light(u):
    """Light on a vertical cylinder seen from the front, sun from the right-front. u in [-1, 1]."""
    u = max(-1.0, min(1.0, u))
    return 0.5 * math.sqrt(max(0.0, 1 - u * u)) + 0.5 * u + 0.1


DOME_CUTS = (-0.05, 0.22, 0.42, 0.58, 0.72)


def dome_tone(u, d=0):
    return shift(DOME, ramp_at(DOME, cyl_light(u), DOME_CUTS), d)


def band(L, y0, y1, hw, d=0, cx=CX):
    """A horizontal cylindrical band (dome stage) shaded per column."""
    for x in range(cx - hw, cx + hw):
        u = (x + 0.5 - cx) / hw
        c = dome_tone(u, d)
        L[y0:y1 + 1, x] = c


# ============================================================================ layer painters
CLOUDS = [  # (cx, cy, rx, ry) unions per bank; hand placed clear of the dome silhouette (x 600..680)
    [(250, 52, 118, 8), (318, 45, 62, 7), (180, 58, 80, 5), (390, 56, 46, 4)],
    [(1010, 40, 150, 9), (1088, 32, 74, 7), (936, 48, 70, 5), (1170, 46, 60, 5)],
    [(120, 120, 150, 6), (60, 114, 70, 5), (420, 134, 110, 4), (330, 128, 60, 4)],
    [(1150, 112, 140, 7), (1230, 104, 60, 5), (880, 130, 110, 4), (960, 126, 60, 4)],
    [(520, 96, 50, 3), (780, 88, 58, 3)],
]
SKY_STOPS = [(0, "sk0"), (78, "sk1"), (128, "sk2"), (168, "sk3")]


def paint_sky():
    L = new()
    for y in range(H):
        cur = SKY_STOPS[0][1]
        for k, (y0, c) in enumerate(SKY_STOPS):
            if y >= y0:
                cur = c
        L[y, :] = I[cur]
        for k in range(1, len(SKY_STOPS)):
            y0, c = SKY_STOPS[k]
            if y0 - 14 <= y < y0:                      # 14-row transition of horizontal streak runs (painterly)
                t = (y - (y0 - 14) + 0.5) / 14
                x = 0
                while x < W:
                    run = 10 + int(hval("srun", y, x) * 40)
                    if hval("sc", y, x) < t:
                        L[y, x:x + run] = I[c]
                    x += run
    for bank in CLOUDS:
        m = np.zeros((H, W), bool)
        for cx, cy, rx, ry in bank:
            m |= ellipse(cx, cy, rx, ry)
        up = np.zeros_like(m); up[1:] = m[:-1]
        dn = np.zeros_like(m); dn[:-1] = m[1:]
        L[m] = I["sk3"]
        L[m & ~dn] = I["cl1"]                         # under-side shade (bottom edge)
        top = m & ~up
        L[top] = I["cl0"]                             # lit cap
        top2 = m & np.roll(top, 1, axis=0) & (np.arange(W)[None, :] % 3 != 0)
        L[top2] = I["cl0"]
    return L


def shell_hw(y):
    t = (SHELL[1] - y) / (SHELL[1] - SHELL[0])
    return SHELL_HW[1] + (SHELL_HW[0] - SHELL_HW[1]) * max(0.0, 1 - t ** 2.4) ** 0.55


def paint_dome():
    L = new()
    # drum base (mostly hidden behind the central roof), stylobate, peristyle, entablature, balustrade, attic
    band(L, DRUM[0], DRUM[1], HW["drum"], -1)
    for x in range(CX - HW["drum"], CX + HW["drum"]):              # small drum windows
        if (x - (CX - HW["drum"])) % 7 == 3:
            L[DRUM[0] + 2:DRUM[0] + 5, x] = shift(DOME, int(L[DRUM[0] + 2, x]), -2)
    band(L, STYLOBATE[0], STYLOBATE[1], HW["stylobate"], 0)
    band(L, STYLOBATE[0], STYLOBATE[0], HW["stylobate"], 1)
    # peristyle: dark interior, then 36 columns at 10 degree steps (front half visible)
    hw = HW["peri_cols"]
    band(L, PERI_COLS[0], PERI_COLS[1], hw - 1, -3)
    for k in range(PERI_COLS_N):
        th = math.radians(-180 + 5 + k * 10)
        if math.cos(th) <= 0:
            continue
        idx = int(round(math.degrees(th) - 5) // 10)                # ..., -1, 0, 1, ... centre-relative index
        if idx in PERI_MISSING:
            continue
        xc = CX - 0.5 + hw * math.sin(th)
        x0 = int(math.floor(xc - 0.5))
        for xx in (x0, x0 + 1):
            u = (xx + 0.5 - CX) / hw
            c = dome_tone(u, 0 if xx == x0 + 1 else -1)
            L[PERI_COLS[0]:PERI_COLS[1] + 1, xx] = c
    band(L, PERI_COLS[0], PERI_COLS[0], hw, 1)                      # capitals
    band(L, PERI_COLS[1], PERI_COLS[1], hw, 0)                      # bases
    # entablature: cornice lit, shadow below, frieze
    band(L, PERI_ENT[0], PERI_ENT[1], HW["peri_ent"], 0)
    band(L, PERI_ENT[0], PERI_ENT[0], HW["peri_ent"], 1)
    band(L, PERI_ENT[0] + 1, PERI_ENT[0] + 1, HW["peri_ent"] - 1, -1)
    # balustrade on top of the peristyle: rail + alternating balusters
    band(L, PERI_BAL[0], PERI_BAL[0], HW["peri_bal"], 1)
    for x in range(CX - HW["peri_bal"], CX + HW["peri_bal"]):
        u = (x + 0.5 - CX) / HW["peri_bal"]
        L[PERI_BAL[1], x] = dome_tone(u, 0 if x % 2 else -2)
    # attic: cornice, shadow, pilasters and windows on a 10 degree grid
    hw = HW["attic"]
    band(L, ATTIC[0], ATTIC[1], hw, 0)
    band(L, ATTIC[0], ATTIC[0], hw, 1)
    band(L, ATTIC[0] + 1, ATTIC[0] + 1, hw, -1)
    for k in range(-8, 9):
        th = math.radians(k * 10)
        x = int(round(CX - 0.5 + hw * math.sin(th)))
        if abs(k) <= 7:
            L[ATTIC[0] + 2:ATTIC[1] + 1, x] = dome_tone((x + 0.5 - CX) / hw, 1)
        th2 = math.radians(k * 10 + 5)
        if abs(k * 10 + 5) < 65:
            x2 = int(round(CX - 0.5 + hw * math.sin(th2)))
            L[ATTIC[0] + 3:ATTIC[0] + 7, x2] = dome_tone((x2 + 0.5 - CX) / hw, -2)
    # ribbed shell (surface of revolution), light from the upper right-front
    lv = np.array([0.55, 0.45, 0.70]); lv = lv / np.linalg.norm(lv)
    y0, y1 = SHELL
    for y in range(y0, y1 + 1):
        hwy = shell_hw(y)
        t = (y1 - y) / (y1 - y0)
        phi = math.radians(8 + 62 * t ** 1.6)
        for x in range(int(math.floor(CX - hwy)), int(math.ceil(CX + hwy))):
            u = (x + 0.5 - CX) / hwy
            if abs(u) > 1:
                continue
            n = np.array([u * math.cos(phi), math.sin(phi), math.sqrt(max(0, 1 - u * u)) * math.cos(phi)])
            l = float(n @ lv) * 0.95 + 0.02
            L[y, x] = ramp_at(DOME, l, (-0.05, 0.2, 0.42, 0.62, 0.8))
        # rib lines: shadow pixel on the left of each rib (light from right), every rib 12 degrees
        if y > y0 + 1:
            for k in range(-7, 8):
                th = math.radians(k * 12)
                if abs(k * 12) > 78:
                    continue
                x = int(round(CX - 0.5 + hwy * math.sin(th)))
                if CX - hwy < x < CX + hwy - 1 and k % 2 == 0:
                    L[y, x] = shift(DOME, int(L[y, x]), -1)
    # shell base ring and lunette windows
    for x in range(CX - SHELL_HW[0], CX + SHELL_HW[0]):
        u = (x + 0.5 - CX) / SHELL_HW[0]
        L[y1, x] = dome_tone(u, 1)
        L[y1 - 1, x] = dome_tone(u, -1)
    for k in range(-5, 6):
        th = math.radians(k * 12 + 6)
        if abs(k * 12 + 6) > 62:
            continue
        hwy = shell_hw(y1 - 5)
        x = int(round(CX - 0.5 + hwy * math.sin(th)))
        for yy in (y1 - 6, y1 - 5, y1 - 4):
            L[yy, x] = shift(DOME, int(L[yy, x]), -3)
    # tholos: ring, columns, cap
    band(L, THOLOS_RING[0], THOLOS_RING[1], HW["tholos_ring"], 0)
    band(L, THOLOS_RING[0], THOLOS_RING[0], HW["tholos_ring"], 1)
    band(L, THOLOS_COLS[0], THOLOS_COLS[1], HW["tholos_cols"], -3)
    for th in (-62, -22, 18, 58):
        x = int(round(CX - 0.5 + HW["tholos_cols"] * math.sin(math.radians(th))))
        L[THOLOS_COLS[0]:THOLOS_COLS[1] + 1, x] = dome_tone((x + 0.5 - CX) / HW["tholos_cols"], 1)
    band(L, THOLOS_COLS[0], THOLOS_COLS[0], HW["tholos_cols"] + 1, 0)
    for y, hwc in zip(range(THOLOS_CAP[0], THOLOS_CAP[1] + 1), (2, 4, 5, 6)):
        band(L, y, y, hwc, 0)
    # Statue of Freedom: dark bronze figure on a globe (10 rows)
    stamp(L, CX - 3, STATUE[0], ["..k...", "..kk..", "..kK..", ".kkKk.", "..kKk.", ".kkKKk", "..kKk.", ".kkKKk",
                                 "kkkKKk", ".hhHh."], {"k": "k0", "K": "k1", "h": "hz1", "H": "hz3"})
    return L


FACADE_STATE = {  # hand-assigned window states by (section, bay index): broken / boarded / dark (default) / lit glass
    ("wingL", 2): "boarded", ("wingL", 7): "broken", ("wingL", 9): "glass", ("corrL", 1): "boarded",
    ("centerL", 3): "broken", ("centerL", 6): "glass", ("centerR", 2): "boarded", ("centerR", 5): "broken",
    ("corrR", 2): "broken", ("wingR", 1): "broken", ("wingR", 3): "broken", ("wingR", 4): "boarded",
    ("wingR", 6): "broken", ("wingR", 8): "broken",
}
SOUTH_WING_GUTTED = (797, 816, 121, 135)   # x0, x1, y0, y1 roof corner collapse (game fiction), drawn as a notch


def facade_section(L, x0, x1, top, kind, name, d=0):
    """One facade section in elevation. kind: 'windows' or 'loggia'. d: tone shift (recessed sections darker)."""
    T = lambda n: shift(DOME, I[n], d)
    rect(L, x0, top, x1, FACADE_BOTTOM, T("m4"))
    # roof balustrade
    rect(L, x0, top, x1, top, T("m5"))
    for x in range(x0, x1 + 1):
        L[top + 1:top + 3, x] = T("m4") if x % 2 == 0 else T("hz2")
    rect(L, x0, top + 3, x1, top + 3, T("m3"))
    # entablature: cornice, shadow, frieze
    e = top + 4
    rect(L, x0, e, x1, e, T("m5"))
    rect(L, x0, e + 1, x1, e + 1, T("hz2"))
    rect(L, x0, e + 2, x1, e + 3, T("m4"))
    p0, p1 = e + 4, 144                         # principal storey
    if kind == "loggia":
        rect(L, x0 + 1, p0, x1 - 1, p1, T("hz0"))
        rect(L, x0 + 1, p0 + 12, x1 - 1, p1, T("hz1"))   # back wall with doors, lit low
        for x in range(x0 + 2, x1 - 1, 7):               # paired columns
            for xx, tone in ((x, "hz3"), (x + 1, "m5"), (x + 3, "hz3"), (x + 4, "m5")):
                if xx < x1:
                    L[p0:p1 + 1, xx] = T(tone)
        rect(L, x0, p0, x1, p0, T("m5"))
    else:
        bay = 0
        for x in range(x0 + 3, x1 - 2, 6):
            st = FACADE_STATE.get((name, bay), "dark")
            rect(L, x - 1, p0 + 1, x + 2, p0 + 1, T("m5"))      # pediment / lintel
            c = {"dark": "hz0", "broken": "k0", "boarded": "s2", "glass": "hz1"}[st]
            rect(L, x, p0 + 3, x + 1, p0 + 9, c if st in ("broken", "boarded") else T(c))
            if st == "boarded":
                rect(L, x, p0 + 5, x + 1, p0 + 5, "s1")
            rect(L, x - 1, p0 + 10, x + 2, p0 + 10, T("m5"))    # sill
            rect(L, x, p0 + 13, x + 1, p0 + 14, T("hz1"))       # mezzanine window
            L[p0 + 2:p1 + 1, x + 3] = T("m5")                    # pilaster (lit edge)
            bay += 1
    # belt course and rusticated base with arched openings
    rect(L, x0, 145, x1, 145, T("m5"))
    rect(L, x0, 146, x1, 146, T("hz2"))
    for y in range(149, FACADE_BOTTOM + 1, 3):
        rect(L, x0, y, x1, y, T("m3"))
    for x in range(x0 + 3, x1 - 2, 6):
        rect(L, x, 150, x + 1, 150, T("hz2"))
        rect(L, x, 151, x + 1, 157, T("hz0"))


def paint_west_front():
    L = new()
    facade_section(L, *WINGS[0], ROOF["wing"], "windows", "wingL")
    facade_section(L, *WINGS[1], ROOF["wing"], "windows", "wingR")
    facade_section(L, *CORRIDORS[0], ROOF["corridor"], "windows", "corrL", d=-1)
    facade_section(L, *CORRIDORS[1], ROOF["corridor"], "windows", "corrR", d=-1)
    facade_section(L, CENTER[0], PAVILION[0] - 1, ROOF["center"], "windows", "centerL")
    facade_section(L, PAVILION[1] + 1, CENTER[1], ROOF["center"], "windows", "centerR")
    facade_section(L, PAVILION[0], PAVILION[1], ROOF["pavilion"] + 3, "loggia", "pavilion")
    # raised attic over the central pavilion (rows 116..118), plus the shadow strips cast by projections (light right)
    rect(L, PAVILION[0], ROOF["pavilion"], PAVILION[1], ROOF["pavilion"] + 2, "m4")
    rect(L, PAVILION[0], ROOF["pavilion"], PAVILION[1], ROOF["pavilion"], "m5")
    for x0 in (PAVILION[0] - 3, CENTER[0] - 3, WINGS[1][0] - 3):
        for x in range(x0, x0 + 3):
            for y in range(H):
                if L[y, x] >= 0 and y > 118:
                    L[y, x] = shift(DOME, int(L[y, x]), -1)
    # side returns: north end in shade, south end lit
    rect(L, WINGS[0][0], ROOF["wing"], WINGS[0][0] + 1, FACADE_BOTTOM, "hz2")
    rect(L, WINGS[1][1] - 1, ROOF["wing"], WINGS[1][1], FACADE_BOTTOM, "m5")
    # gutted south-wing roof corner: notch (the ruin layer paints the broken edge and the tree)
    x0, x1, y0, y1 = SOUTH_WING_GUTTED
    for y in range(y0, y1 + 1):
        depth = int((x1 - x0) * (1 - (y - y0) / (y1 - y0 + 1)) ** 0.7)
        L[y, x1 - depth:x1 + 1] = -1
    return L


def paint_terrace():
    L = new()
    x0, x1 = TERRACE
    rect(L, x0, DECK[0], x1, DECK[1], "hz3")
    rect(L, x0, DECK[0], x1, DECK[0], "m3")
    # balustrade with piers every 34 px
    rect(L, x0, TBAL[0], x1, TBAL[0], "m5")
    for x in range(x0, x1 + 1):
        L[TBAL[0] + 1:TBAL[1], x] = I["m4"] if x % 3 else I["hz2"]
    rect(L, x0, TBAL[1], x1, TBAL[1], "m3")
    for x in range(x0 + 4, x1, 34):
        rect(L, x, TBAL[0] - 1, x + 2, TBAL[1], "m4")
        rect(L, x + 2, TBAL[0] - 1, x + 2, TBAL[1], "m5")
        rect(L, x, TBAL[0] - 1, x + 2, TBAL[0] - 1, "m5")
    # wall face: marble courses, terrace-room windows, granite foundation
    rect(L, x0, TWALL[0], x1, TWALL[1], "m4")
    for y in range(TWALL[0] + 2, TWALL[1] + 1, 3):
        rect(L, x0, y, x1, y, "m3")
    rect(L, x0, TWALL[0], x1, TWALL[0], "hz2")                 # shadow under the balustrade rail
    rect(L, x0, TGRANITE[0], x1, TGRANITE[1], "m2")
    for x in range(x0, x1 + 1, 5):
        px(L, x, TGRANITE[0] + 1, "m1")
    for x in range(x0 + 12, x1 - 8, 15):
        if EXEDRA[0] - 30 < x < EXEDRA[1] + 30:
            continue
        rect(L, x, TWALL[0] + 3, x + 1, TWALL[0] + 5, "hz0")
        rect(L, x, TWALL[0] + 2, x + 1, TWALL[0] + 2, "m5")
    # returns at both ends (the terrace wraps north and south): north return in shade, south return lit
    for k in range(6):
        rect(L, x0 - 1 - k, TBAL[0] + k // 2, x0 - 1 - k, TGRANITE[1], "hz2" if k < 5 else "hz1")
        rect(L, x1 + 1 + k, TBAL[0] + k // 2, x1 + 1 + k, TGRANITE[1], "m5" if k < 5 else "m4")
    # four west lanterns on piers (bronze posts with dark lamps; unlit in 2537)
    for x in (480, 582, 696, 798):
        rect(L, x, TBAL[0] - 6, x, TBAL[0] - 2, "k1")
        rect(L, x - 1, TBAL[0] - 8, x + 1, TBAL[0] - 6, "k2")
        px(L, x, TBAL[0] - 9, "k1")
    # exedra: dark arched grotto with the dry fountain rim and planting
    e0, e1 = EXEDRA
    for x in range(e0, e1 + 1):
        u = (x + 0.5 - (e0 + e1 + 1) / 2) / ((e1 - e0 + 1) / 2)
        top = TWALL[0] + int(round(3 * (u * u)))
        rect(L, x, top, x, TGRANITE[1], "hz0")
    rect(L, e0, TWALL[0] - 1, e1, TWALL[0] - 1, "m5")
    rect(L, e0 + 3, TGRANITE[0] - 1, e1 - 3, TGRANITE[0] - 1, "m3")       # basin rim
    rect(L, e0 + 3, TGRANITE[0], e1 - 3, TGRANITE[0] + 1, "hz1")
    # twin grand stairs: flights descend outward from the central landing; treads 2 rows (lit top, riser)
    for side in (-1, 1):
        for k in range(8):
            y = TBAL[0] + 1 + 2 * k
            inner = (e0 - 2) if side < 0 else (e1 + 2)
            xa = inner - side * (2 * k)                                 # inner edge steps outward
            xb = xa - side * 22
            lo, hi = min(xa, xb), max(xa, xb)
            rect(L, lo, y, hi, y, "m5" if side > 0 else "m4")
            rect(L, lo, y + 1, hi, y + 1, "hz3" if side > 0 else "hz2")
            # cheek wall on the outer side
            ch = hi + 1 if side > 0 else lo - 1
            rect(L, ch, y, ch, y + 1, "m5" if side > 0 else "hz1")
    return L


RUBBLE_CONE = [  # (x, y, w, h) chunky blocks at the breached south balustrade (no single-texel chips)
    (820, 172, 4, 2), (826, 170, 5, 3), (833, 168, 4, 3), (839, 171, 5, 2), (845, 173, 4, 2), (824, 175, 6, 2),
    (831, 174, 5, 3), (838, 175, 4, 2), (816, 176, 4, 2), (843, 176, 5, 2), (828, 178, 4, 2), (835, 178, 6, 2),
]
VINES = [  # (x, y_top, length, width) ivy curtains, north (left) half and the terrace
    (466, 128, 22, 2), (470, 134, 16, 3), (476, 140, 12, 2), (489, 146, 10, 2), (500, 150, 8, 2),
    (420, 162, 12, 3), (430, 161, 9, 2), (446, 163, 10, 3), (508, 162, 8, 2), (540, 163, 7, 2),
    (612, 163, 9, 2), (668, 163, 6, 2), (760, 162, 5, 2), (866, 162, 11, 3),
]
SOOT = [(746, 129, 6), (758, 127, 5), (782, 130, 7), (794, 126, 6), (731, 128, 4)]


def paint_ruin_survey():
    L = new()
    # missing cast-iron plates on the dome's south shell: dark interior with surviving ribs
    spans = {53: (0.38, 0.58), 54: (0.34, 0.64), 55: (0.32, 0.68), 56: (0.30, 0.70), 57: (0.30, 0.71),
             58: (0.31, 0.70), 59: (0.33, 0.69), 60: (0.36, 0.67), 61: (0.40, 0.63), 62: (0.45, 0.58)}
    for y, (u0, u1) in spans.items():
        hwy = shell_hw(y)
        xa, xb = int(round(CX - 0.5 + u0 * hwy)), int(round(CX - 0.5 + u1 * hwy))
        rect(L, xa, y, xb, y, "hz0")
        for xr in range(xa + 1, xb, 3):
            px(L, xr, y, "hz2")
        px(L, xa, y, "k1")
    # rust streaks below the opening and from attic windows
    for x, y0, y1 in ((648, 63, 70), (652, 63, 74), (645, 64, 68), (657, 79, 86), (623, 79, 84), (662, 93, 100)):
        for y in range(y0, y1 + 1):
            px(L, x, y, "s2" if (y - y0) % 4 else "s1")
    # two missing peristyle columns are left as gaps by the dome painter; a stump of one stands in the gap
    xc = int(round(CX - 0.5 + HW["peri_cols"] * math.sin(math.radians(55))))
    rect(L, xc, PERI_COLS[1] - 4, xc + 1, PERI_COLS[1], "hz3")
    px(L, xc + 1, PERI_COLS[1] - 4, "m4")
    # survey scaffold tower beside the dome on the south roof, with a beacon (2537 survey; game fiction)
    sx0, sx1, sy0, sy1 = 678, 686, 76, 118
    rect(L, sx0, sy0, sx0, sy1, "k1")
    rect(L, sx1, sy0, sx1, sy1, "k1")
    for y in range(sy0, sy1 + 1, 7):
        rect(L, sx0, y, sx1, y, "k1")
        if y + 7 <= sy1:
            line(L, sx0 + 1, y + 1, sx1 - 1, y + 6, "k2")
    rect(L, sx0 - 1, sy0 - 1, sx1 + 1, sy0 - 1, "k2")
    rect(L, sx0 + 3, sy0 - 4, sx0 + 5, sy0 - 2, "k0")
    rect(L, sx0 + 4, sy0 - 3, sx0 + 4, sy0 - 3, "c1")
    px(L, sx0 + 4, sy0 - 5, "k1")
    # gutted south-wing corner: broken edge, dark gutted interior, self-sown tree
    x0, x1, y0, y1 = SOUTH_WING_GUTTED
    for y in range(y0, y1 + 1):
        depth = int((x1 - x0) * (1 - (y - y0) / (y1 - y0 + 1)) ** 0.7)
        if depth > 0:
            px(L, x1 - depth - 1, y, "hz2")
            rect(L, x1 - depth, y, x1, y, "hz0" if y > y0 + 3 else "k1")
    for cx, cy, r, lt in ((806, 118, 7, 2), (812, 122, 6, 1), (801, 124, 5, 1)):
        m = ellipse(cx, cy, r, r * 0.8)
        ys, xs = np.nonzero(m)
        for y, x in zip(ys, xs):
            l = ((x - cx) * 0.6 - (y - cy) * 0.7) / r + 0.3 * (hval("sw", x // 2, y // 2) - 0.5)
            L[y, x] = VG[max(0, min(4, int(1 + lt * 0.5 + l * 1.6)))]
    rect(L, 806, 126, 806, 134, "s1")
    # soot tongues above south-wing windows (k1 core, hz0 rim)
    for x, y, h in SOOT:
        for j in range(h):
            w = max(1, 2 - j // 3)
            rect(L, x - w + 1, y - j, x + w - 1, y - j, "k1" if j < h - 2 else "hz0")
    # ivy curtains
    for x, y, n, w in VINES:
        for j in range(n):
            for i in range(w):
                if j > n - 3 and i == w - 1:
                    continue
                px(L, x + i, y + j, "vg0" if (i + j) % 3 else "vg1")
    # breached south balustrade: gap with broken stubs and the rubble cone on the lawn
    rect(L, 822, TBAL[0], 846, TBAL[1], "hz3")
    rect(L, 822, TBAL[0], 846, TBAL[0], "m3")
    for x0b, y0b, w, h in RUBBLE_CONE:
        rect(L, x0b, y0b, x0b + w - 1, y0b + h - 1, "m4")
        rect(L, x0b, y0b, x0b + w - 1, y0b, "m5")
        rect(L, x0b, y0b + h - 1, x0b + w - 1, y0b + h - 1, "hz2")
    for x in range(826, 844):                                       # V notch in the wall face
        dep = 6 - abs(x - 835) // 2
        if dep > 0:
            rect(L, x, TWALL[0], x, TWALL[0] + dep, "hz0")
    # survey cordon and flags round the breach; a survey tent on the north lawn
    for x in range(806, 862, 3):
        rect(L, x, 181, x + 1, 181, "o1")
    for x in (806, 834, 862):
        rect(L, x, 179, x, 183, "k1")
        px(L, x + 1, 179, "o1")
    stamp(L, 520, 178, ["...o...", "..ooO..", ".ooOOO.", "oOOOkOO"], {"o": "o1", "O": "o0", "k": "k0"})
    for x, y in ((560, 183), (600, 187), (680, 187), (720, 183)):
        rect(L, x, y - 3, x, y, "k1")
        px(L, x + 1, y - 3, "o1")
    return L


GROVE_CROWNS = [  # (cx, cy, r, haze) hand placed; drawn back to front; haze +1 = farther (lighter)
    # left grove
    (210, 120, 26, 1), (262, 126, 24, 1), (312, 122, 26, 1), (362, 128, 22, 1), (408, 134, 20, 1), (448, 140, 16, 1),
    (176, 146, 26, 0), (228, 152, 26, 0), (284, 150, 28, 0), (338, 154, 24, 0), (388, 158, 22, 0), (434, 160, 18, 0),
    (476, 158, 14, 0), (500, 166, 10, 0),
    (196, 178, 22, -1), (248, 182, 22, -1), (300, 180, 20, -1), (348, 186, 18, -1), (460, 182, 14, -1),
    # right grove (different rhythm, a gap where the south walk enters)
    (1074, 118, 28, 1), (1018, 124, 24, 1), (968, 130, 24, 1), (920, 136, 20, 1), (876, 142, 16, 1),
    (1110, 148, 26, 0), (1052, 152, 28, 0), (996, 156, 24, 0), (946, 160, 22, 0), (900, 158, 18, 0), (856, 164, 12, 0),
    (812, 170, 9, 0),
    (1092, 182, 22, -1), (1036, 184, 20, -1), (982, 182, 18, -1), (930, 188, 16, -1), (822, 186, 12, -1),
]
SNAGS = [(392, 112, 1), (934, 104, -1)]      # bare dead trees among the groves (x, top y, lean)
GROVE_TRUNKS = [(306, 203), (466, 199), (976, 203), (822, 201)]


def crown(L, cx, cy, r, ramp, base, reg=None, seed="c"):
    """Leaf-mass crown built from 4-7 sub-masses (each lit from the upper right, shaded underneath), so crowns read
    as clumped foliage rather than single balls. Sub-mass offsets are hashed per crown (texture-level variation);
    crown position and size come from the hand-written tables."""
    yy, xx = np.mgrid[0:H, 0:W]
    y0b, y1b = max(0, int(cy - 1.3 * r)), min(H, int(cy + 1.1 * r) + 1)
    x0b, x1b = max(0, int(cx - 1.4 * r)), min(W, int(cx + 1.4 * r) + 1)
    sub = []
    n = 4 + int(hval(seed, "n", cx, cy) * 4)
    for k in range(n):
        a = math.radians(-160 + 140 * k / max(1, n - 1) + 20 * (hval(seed, "a", cx, k) - 0.5))
        d = r * (0.35 + 0.25 * hval(seed, "d", cx, k))
        sx, sy = cx + d * math.cos(a), cy + d * 0.8 * math.sin(a) - r * 0.05
        sr = r * (0.42 + 0.22 * hval(seed, "r", cx, k))
        sub.append((sy, sx, sr))
    sub.append((cy + r * 0.12, cx, r * 0.72))
    sub.sort()                                                 # upper masses first, lower (nearer) masses over them
    m = np.zeros((H, W), bool)
    for sy, sx, sr in sub:
        e = np.zeros((H, W), bool)
        e[y0b:y1b, x0b:x1b] = ((xx[y0b:y1b, x0b:x1b] + 0.5 - sx) / sr) ** 2 + \
                              ((yy[y0b:y1b, x0b:x1b] + 0.5 - sy) / (sr * 0.82)) ** 2 <= 1
        ys, xs = np.nonzero(e)
        for y, x in zip(ys, xs):
            l = ((x - sx) * 0.55 - (y - sy) * 0.8) / sr
            cl = hval(seed, "cl", (x + (y // 3) % 2 * 2) // 3, y // 3) - 0.5
            v = base + l * 1.7 + cl * 0.8
            L[y, x] = ramp[max(0, min(len(ramp) - 1, int(round(v))))]
        dn = np.zeros_like(e); dn[:-1] = e[1:]
        rim = e & ~dn
        L[rim] = ramp[0]
        m |= e
    if reg is not None:
        reg |= m
    return m


GROVE_MASS = [(196, 492, 180, 200), (788, 1096, 182, 202)]   # x0, x1, top row, bottom row of the shaded under-mass


def paint_groves():
    L = new()
    for x0, x1, y0, y1 in GROVE_MASS:
        for x in range(x0, x1 + 1):
            u = (x - x0) / (x1 - x0)
            top = y0 + int(round(5 * math.sin(x / 9.0 + hval("gm", x0)) + 3 * hval("gm", x // 6)))
            for y in range(top, y1 + 1):
                L[y, x] = VG[0] if y > y1 - 3 or hval("gmt", x // 3, y // 3) < 0.3 else VG[1]
    for x, y in GROVE_TRUNKS:
        rect(L, x, y - 8, x + 1, y, "hz0")
        px(L, x + 1, y - 8, "hz1")
    for cx, cy, r, hz in GROVE_CROWNS:
        crown(L, cx, cy, r, VG, 1.6 + hz * 0.7, seed="grove")
    for x, y, lean in SNAGS:
        for j in range(0, 34):
            xx = x + int(lean * j * 0.12)
            px(L, xx, y + j, "hz0")
            if j < 20:
                px(L, xx + 1, y + j, "hz1")
        for (dx, dy, ex, ey) in ((0, 6, -8, -4), (0, 10, 7, 3), (0, 16, -6, 9), (1, 4, 5, -6)):
            line(L, x + dx, y + dy, x + dx + ex * (1 if lean > 0 else -1), y + dy + ey, "hz0")
    return L


def bez(pts, n=400):
    p = np.array(pts, float)
    t = np.linspace(0, 1, n)[:, None]
    return ((1 - t) ** 3 * p[0] + 3 * (1 - t) ** 2 * t * p[1] + 3 * (1 - t) * t ** 2 * p[2] + t ** 3 * p[3])


def paint_far_lawn_basin():
    L = new()
    # lawn rows behind and beside the pool (distant meadow with dry patches)
    for y in range(LAWN[0], NEAR_COPING[1] + 1):      # horizontal streak runs, longer with distance
        x = 0
        t = (y - LAWN[0]) / (NEAR_COPING[1] - LAWN[0])
        while x < W:
            run = int(14 + 30 * (1 - t) + hval("lrun", y, x) * 30)
            v = hval("lawn", y, x)
            c = "vg3" if v < 0.6 else ("vg2" if v < 0.86 else ("d1" if v < 0.95 else "vg4"))
            if y < LAWN[0] + 3:
                c = "vg2" if v < 0.7 else "vg3"
            L[y, x:x + run] = I[c]
            x += run
    # mown survey strip on the axis and the two curved Olmsted walks from the stair feet
    rect(L, CX - 6, LAWN[0], CX + 5, LAWN[1], "vg4")
    for side in (-1, 1):
        pts = [(CX + side * 40, LAWN[0]), (CX + side * 70, LAWN[0] + 4), (CX + side * 120, LAWN[1] - 2),
               (CX + side * 170, LAWN[1] + 1)]
        for x, y in bez(pts):
            rect(L, int(x), int(y), int(x) + 1, int(y), "m3")
    # side walks around the pool (to v04 / exits): pale bands narrowing with distance
    for pts in SIDE_WALKS:
        for k, (x, y) in enumerate(bez(pts)):
            t = k / 399
            hw = 9 - 6 * t
            rect(L, int(x - hw), int(y), int(x + hw), int(y), "p2" if t < 0.5 else "m3")
    # drained Capitol Reflecting Pool (game fiction: no water texels at all)
    def edge_x(y, side):
        t = (y - FAR_COPING[0]) / (NEAR_COPING[1] - FAR_COPING[0])
        far = BASIN_FAR_X[0] if side < 0 else BASIN_FAR_X[1]
        near = BASIN_NEAR_X[0] if side < 0 else BASIN_NEAR_X[1]
        return int(round(far + (near - far) * t))
    for y in range(FAR_COPING[0], NEAR_COPING[1] + 1):
        xa, xb = edge_x(y, -1), edge_x(y, 1)
        if y <= FAR_COPING[0] + 1:
            rect(L, xa, y, xb, y, "m4" if y == FAR_COPING[0] else "m3")
        elif y <= FAR_COPING[1]:
            rect(L, xa, y, xb, y, "hz3")                                  # far inner wall face (lit)
        elif y <= BASIN[1]:
            rect(L, xa + 3, y, xb - 3, y, "s1")
            rect(L, xa, y, xa + 2, y, "hz1")                              # left inner wall (shade)
            rect(L, xb - 2, y, xb, y, "m3")                               # right inner wall (lit)
        else:
            rect(L, xa - 2, y, xb + 2, y, "m4" if y < NEAR_COPING[0] + 2 else "m3")
            if y == NEAR_COPING[1]:
                rect(L, xa - 2, y, xb + 2, y, "m2")
    # basin floor: cracked silt plates (bigger near), drainage channel, weed beds at the margins
    for y in range(BASIN[0], BASIN[1] + 1):
        t = (y - BASIN[0]) / (BASIN[1] - BASIN[0])
        cw = int(8 + 14 * t)
        for x in range(edge_x(y, -1) + 3, edge_x(y, 1) - 2):
            if (x + (y // 3) * 5) % cw == 0 or (y - BASIN[0]) % max(3, int(3 + 3 * t)) == 0 and hval("crk", x // 3, y) < 0.5:
                L[y, x] = I["s0"]
            elif hval("silt", (x + (y // 3) * 5) // cw, (y - BASIN[0]) // 3) < 0.62:
                L[y, x] = I["s2"]
    rect(L, CX - 1, BASIN[0], CX, BASIN[1], "s0")
    WEEDS = [(492, 197, 34, 3), (540, 205, 26, 3), (742, 199, 40, 4), (806, 206, 30, 3), (590, 201, 14, 2),
             (690, 196, 18, 2), (430, 206, 34, 3), (846, 203, 30, 3)]
    for x0, y0, w, h in WEEDS:
        for j in range(h):
            for i in range(w):
                if hval("wd", x0 + i, y0 + j) < 0.75 - 0.25 * abs(i - w / 2) / (w / 2):
                    L[y0 + j, x0 + i] = I["d0" if (i + j) % 4 == 0 else ("g3" if hval("w2", i, j) < 0.5 else "g2")]
    # survey transect tape across the drained pool
    for k, (x, y) in enumerate(bez([(520, 207), (580, 203), (690, 199), (762, 196)], 260)):
        if (k // 6) % 2 == 0:
            px(L, int(x), int(y), "o1")
    return L


SLAB_TONES = ("p2", "p2", "p2", "p2", "p2", "p3", "p1", "p2", "p3", "p2")
# reclaimed meadow (selective vegetation): hand-placed ellipses, minus the cleared survey corridor
MEADOW = [(930, 420, 150, 112), (1010, 560, 120, 104), (840, 612, 84, 52), (990, 330, 80, 46), (300, 650, 150, 56),
          (214, 570, 56, 84), (470, 300, 36, 12), (790, 292, 44, 14), (1070, 250, 40, 30)]
CORRIDOR = (572, 708)                     # cleared survey corridor on the axis (kept paved)
VERGE_SHRUBS = [  # (cx, cy, r) dense shrubs on the side verges (non-walkable), lit from the right
    (60, 330, 26), (150, 372, 24), (40, 430, 22), (160, 470, 20), (70, 600, 28), (150, 640, 22), (30, 700, 24),
    (1230, 360, 26), (1130, 400, 22), (1250, 470, 24), (1140, 620, 26), (1230, 650, 28), (1120, 700, 20),
]


STAIN_FRAC = 0.2                           # share of slabs darkened by weathering (whole slabs, organic zones)


def paving(L, x0, y0, x1, y1, sw, sh, key, tones=SLAB_TONES, joint="p1"):
    field = 0.65 * vnoise(key + "-st", 72) + 0.35 * vnoise(key + "-st2", 28)
    cut = quantile_cut(field[y0:y1 + 1, x0:x1 + 1], STAIN_FRAC)
    for y in range(y0, y1 + 1):
        r = (y - y0) // sh
        off = (sw // 2) * (r % 2)
        sy = min(H - 1, y0 + r * sh + sh // 2)
        for x in range(x0, x1 + 1):
            c = (x - x0 + off) // sw
            t = I[tones[int(hval(key, r, c) * len(tones))]]
            sx = max(0, min(W - 1, x0 + c * sw - off + sw // 2))
            stained = field[sy, sx] < cut                              # decided per slab: zones follow joints
            if stained:
                t = shift(PAVE, t, -1)                                 # weathered, darker slabs
            if (y - y0) % sh == sh - 1 or (x - x0 + off) % sw == 0:
                L[y, x] = I["p0"] if stained or field[y, x] < cut else I[joint]
            else:
                L[y, x] = t
                if (y - y0) % sh == 0 and hval(key, "lip", r, c) < 0.35:
                    L[y, x] = shift(PAVE, t, 1)                    # lit top edge on some slabs


def blob(cx, cy, rx, ry, seed):
    """Ellipse whose radius wobbles with angle (two hashed harmonics): an organic patch outline."""
    yy, xx = np.mgrid[0:H, 0:W]
    dx, dy = (xx + 0.5 - cx) / rx, (yy + 0.5 - cy) / ry
    th = np.arctan2(dy, dx)
    p1, p2, p3 = (hval(seed, cx, cy, k) * 6.283 for k in range(3))
    rr = 1 + 0.16 * np.sin(3 * th + p1) + 0.09 * np.sin(5 * th + p2) + 0.05 * np.sin(11 * th + p3)
    return dx * dx + dy * dy <= rr * rr


def meadow_mask():
    m = np.zeros((H, W), bool)
    for cx, cy, rx, ry in MEADOW:
        m |= blob(cx, cy, rx, ry, "mead")
    m[:, CORRIDOR[0]:CORRIDOR[1] + 1] = False
    m[:PLAZA_TOP + 6] = False
    m[STEPS[1] - 4:, STEPS[0] - 4:STEPS[2] + 5] = False
    return m


_DRY_CUT = {}


def grass_px(key, x, y, base, dry=0.0):
    # smooth tonal field (organic patches, no tile grid) + ordered dither on the thresholds for soft transitions
    pv = 0.6 * vnoise(key, 22)[y, x] + 0.4 * vnoise(key + "-f", 7)[y, x] + (BAYER[y % 4, x % 4] - 0.5) * 0.06
    tone = base + (1 if pv > 0.6 else (-1 if pv < 0.4 else 0))
    blade = hval(key, "b", x, (y + (x * 7) % 3) // 3) < 0.3
    c = GR[max(0, min(7, tone + (1 if blade else 0)))]
    if dry:
        df = vnoise(key + "-dry", 16)
        if (key, dry) not in _DRY_CUT:
            _DRY_CUT[(key, dry)] = quantile_cut(df, dry)
        if df[y, x] + (BAYER[y % 4, x % 4] - 0.5) * 0.04 < _DRY_CUT[(key, dry)]:
            c = I["d1"] if blade else I["d0"]
    return c


def paint_plaza():
    L = new()
    paving(L, 0, PLAZA_TOP, W - 1, H - 1, 24, 12, "plaza")
    rect(L, 0, PLAZA_TOP, W - 1, PLAZA_TOP + 1, "m3")                           # coping curb lip
    rect(L, 0, PLAZA_TOP + 2, W - 1, PLAZA_TOP + 2, "p0")
    # cleared survey corridor: larger, lighter axis slabs
    paving(L, CORRIDOR[0], 300, CORRIDOR[1], 683, 34, 16, "axis", tones=("p2", "p3", "p3", "p2", "p3"))
    rect(L, CORRIDOR[0], 300, CORRIDOR[0] + 1, 683, "p1"); rect(L, CORRIDOR[1] - 1, 300, CORRIDOR[1], 683, "p1")
    # reclaimed meadow: grass over the paving, with a joint-grass transition band round it
    mm = meadow_mask()
    near = mm.copy()
    for d in (3, 6, 9):
        near |= np.roll(mm, d, 0) | np.roll(mm, -d, 0) | np.roll(mm, d, 1) | np.roll(mm, -d, 1)
    ys, xs = np.nonzero(near & ~mm)
    for y, x in zip(ys, xs):
        if y > PLAZA_TOP + 3 and L[y, x] == I["p1"]:
            L[y, x] = I["g3"] if hval("jg", x, y) < 0.6 else I["g2"]
        elif y > PLAZA_TOP + 3 and hval("moss", x // 3, y // 2) < 0.12:
            L[y, x] = I["d0"]
    ys, xs = np.nonzero(mm)
    for y, x in zip(ys, xs):
        L[y, x] = grass_px("mead", x, y, 3, 0.26 if x > CX else 0.12)
    # ragged boundary: grass tongues into the paving joints and paving islands left in the grass
    edge = mm & ~(np.roll(mm, 1, 0) & np.roll(mm, -1, 0) & np.roll(mm, 1, 1) & np.roll(mm, -1, 1))
    ys, xs = np.nonzero(edge)
    for y, x in zip(ys[::5], xs[::5]):
        if PLAZA_TOP + 6 < y < H - 6 and not (CORRIDOR[0] - 4 <= x <= CORRIDOR[1] + 4):
            for j in range(int(2 + hval("tng", x, y) * 4)):
                px(L, x + (1 if hval("tdx", x, y) < 0.5 else -1) * j, y + j % 2, "g3" if j % 2 else "g2")
    # paving texels stranded inside grass by the tongues read as pale flecks: grass them over
    nb = neighbour_stack(L)
    stranded = np.isin(L, PAVE) & (np.isin(nb, GR).sum(0) >= 5)
    stranded[:PLAZA_TOP + 4] = False
    L[stranded] = I["g2"]
    # side verges (non-walkable): shaded grass under the tree rows, leaf litter, dense shrubs
    for x0, x1 in BEDS:
        for y in range(PLAZA_TOP + 3, H):
            for x in range(x0, x1 + 1):
                L[y, x] = grass_px("verge", x, y, 1)
                if hval("lit", x // 2, y) < 0.06:
                    L[y, x] = I["s1"]   # s1, not s2: s2 flecked on the shaded verge grass
        edge = x1 if x0 == 0 else x0
        rect(L, edge - 1, PLAZA_TOP + 3, edge + 1, H - 1, "p1")
        rect(L, edge - 1 + (1 if x0 == 0 else 0), PLAZA_TOP + 3, edge - 1 + (1 if x0 == 0 else 0), H - 1, "p3")
    for cx, cy, r in VERGE_SHRUBS:
        crown(L, cx, cy, r, FOL, 2.4, seed="verge")
    # steps down to the Grant Memorial platform (entry): treads lit, risers face the viewer
    x0, y0, x1, y1 = STEPS
    for k in range(3):
        ty = y0 + 12 * k
        a, b = x0 + 8 * k, x1 - 8 * k
        rect(L, a, ty, b, ty + 3, "m4")
        rect(L, a, ty, b, ty, "m5")
        rect(L, a, ty + 4, b, min(ty + 11, H - 1), "m3")
        rect(L, a, min(ty + 10, H - 1), b, min(ty + 11, H - 1), "m2")
        rect(L, a, ty, a + 1, min(ty + 11, H - 1), "m2")
        rect(L, b - 1, ty, b, min(ty + 11, H - 1), "m5")
    return L


CRACKS = [((600, 236), (628, 244), (650, 241)), ((980, 300), (1010, 318), (1040, 322)),
          ((260, 600), (300, 610), (330, 604)), ((720, 240), (744, 236), (770, 246)),
          ((470, 280), (492, 290), (520, 286)), ((640, 560), (652, 574), (648, 590)), ((600, 400), (590, 420))]
MISSING_SLABS = [(744, 652, 24, 12), (216, 262, 24, 12), (1040, 286, 24, 12), (528, 600, 24, 12)]
HEAVED = [(900, 250, 48, 12), (520, 660, 24, 12)]
LEAF_DRIFTS = [(196, 250, 30, 10), (196, 330, 16, 30), (1060, 300, 24, 30), (1070, 470, 18, 30), (330, 700, 30, 8),
               (1000, 700, 34, 8), (560, 230, 60, 6)]
STAKE_LINES = [(CORRIDOR[0] + 8, range(320, 680, 72)), (CORRIDOR[1] - 8, range(352, 680, 72))]
PAINT_TICKS = [(640, 300), (640, 372), (640, 444), (640, 516), (640, 588), (640, 660), (520, 262), (760, 262)]
FLOWER_CLUMPS = [(820, 380, "fl"), (880, 520, "y0"), (990, 400, "bl"), (1040, 560, "y0"), (800, 600, "fl"),
                 (300, 640, "y0"), (240, 600, "fl"), (960, 470, "o2")]
TUSSOCKS = 90


def paint_ground_detail():
    L = new()
    for pts in CRACKS:
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            line(L, xa, ya, xb, yb, "p0")
            line(L, xa + 1, ya, xb + 1, yb, "p1")
    for x, y, w, h in MISSING_SLABS:
        rect(L, x + 1, y, x + w - 1, y + h - 2, "s1")
        rect(L, x + 1, y, x + w - 1, y + 1, "s0")
        for i in range(2, w - 2, 3):
            rect(L, x + i, y + h - 5, x + i + 1, y + h - 3, "g3")
            rect(L, x + i, y + h - 6, x + i + 1, y + h - 6, "g4")
    for x, y, w, h in HEAVED:          # heaved slab: tilted, lit lip and dark gap below
        rect(L, x + 1, y - 2, x + w - 1, y - 2, "p3")
        rect(L, x + 1, y - 1, x + w - 1, y + h - 3, "p2")
        rect(L, x + 1, y + h - 2, x + w - 1, y + h - 1, "s0")
    for x0, y0, w, h in LEAF_DRIFTS:   # leaf litter as 2x1 clusters (no single texels)
        for k in range(w * h // 9):
            x = x0 + int(hval("lf", x0, k) * w)
            y = y0 + int(hval("lfy", y0, k) * h)
            rect(L, x, y, x + 1, y, ("o0", "s2", "s1", "s2")[k % 4])   # no d1: it flecked on stained slabs
    for x, y in PAINT_TICKS:           # survey paint crosses on the paving
        rect(L, x - 4, y, x + 4, y, "o1")
        rect(L, x, y - 3, x, y + 3, "o1")
    for x, ys in STAKE_LINES:          # stake lines bounding the survey corridor (12 px stakes, orange flagging)
        for y in ys:
            stamp(L, x - 2, y - 11, ["..ooo", "..oOO", "..oO.", "..w..", "..wW.", "..wW.", "..wW.", "..wW.",
                                     "..wW.", "..wW.", ".ww..", "..s.."],
                  {"o": "o1", "O": "o0", "w": "s3", "W": "s2", "s": "s0"})
    mm = meadow_mask()
    for x, y, c in FLOWER_CLUMPS:      # sparse wildflower clusters in the meadow (2x1 heads on green stems)
        for dx, dy in ((0, 0), (4, 1), (2, 3), (-3, 2), (6, -2), (-5, -1)):
            if mm[y + dy, x + dx]:
                rect(L, x + dx, y + dy, x + dx + 1, y + dy, c)
                px(L, x + dx, y + dy + 1, "g2")
    k = 0
    n = 0
    while n < TUSSOCKS and k < 4000:   # tall-grass tussocks only inside the meadow
        x = 160 + int(hval("tus", k) * 960)
        y = PLAZA_TOP + 20 + int(hval("tusy", k) * (H - PLAZA_TOP - 40))
        k += 1
        if not (mm[y, x] and mm[y - 6, x - 4] and mm[y, x + 5]):
            continue
        stamp(L, x - 4, y - 7, ["...d..c..", "..bd..c..", "..bd.cc..", ".bbd.c.c.", ".bb.cc...", "abbbcc...",
                                 "aabbbcc..", ".aabb...."],
              {"a": "g1", "b": "g3", "c": "g5", "d": "g6"} if x < CX else {"a": "g2", "b": "g4", "c": "g6", "d": "d1"})
        n += 1
    # cable: generator -> light mast only, in k1 so it reads as a cable lying on the slabs, not a scratch
    # (the long generator -> tripod run read as a crack across the plaza; a total station needs no mains feed)
    for pts in ([(262, 452), (300, 420), (420, 380), (494, 384)],):
        for x, y in bez(pts, 700):
            px(L, int(x), int(y), "k1")
    return L


def neighbour_stack(L):
    p = np.pad(L, 1, constant_values=-1)
    return np.stack([p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                     if (dy, dx) != (0, 0)])


def fill_pinholes(L, min_nb=6):
    """Transparent texels enclosed by >= min_nb opaque neighbours (e.g. between a guy rope and a tent outline) take
    the most common neighbour colour, so no single ground texel shows through a sprite as a pale fleck."""
    nb = neighbour_stack(L)
    holes = (L < 0) & ((nb >= 0).sum(0) >= min_nb)
    for y, x in zip(*np.nonzero(holes)):
        v = nb[:, y, x]
        v = v[v >= 0]
        L[y, x] = np.bincount(v).argmax()
    return L


def outline_mask(L, reg, c="k0"):
    """1-px outline round a registered sprite mask (pixel-art silhouette), drawn into L."""
    up = np.zeros_like(reg); up[1:] = reg[:-1]
    dn = np.zeros_like(reg); dn[:-1] = reg[1:]
    lf = np.zeros_like(reg); lf[:, 1:] = reg[:, :-1]
    rt = np.zeros_like(reg); rt[:, :-1] = reg[:, 1:]
    edge = reg & ~(up & dn & lf & rt)
    L[edge] = I[c]


def box3q(L, reg, x0, base, w, d, h, top, front, hi, lo, edge="k0"):
    """A 3/4 top-down box: top face (d rows) directly above the front face (h rows); light from the right."""
    yf = base - h + 1
    yt = yf - d
    rect(L, x0, yt, x0 + w - 1, yf - 1, top)
    rect(L, x0, yf, x0 + w - 1, base, front)
    rect(L, x0 + w - 2, yt, x0 + w - 2, base, hi)
    rect(L, x0, base - 1, x0 + w - 1, base - 1, lo)
    rect(L, x0, yf, x0 + w - 1, yf, hi)
    m = np.zeros((H, W), bool)
    m[max(0, yt):base + 1, max(0, x0):x0 + w] = True
    reg |= m
    outline_mask(L, m, edge)
    return yt, yf


def crate(L, reg, x0, base, w=24, h=16, d=8):
    yt, yf = box3q(L, reg, x0, base, w, d, h, "s3", "s2", "s4", "s1")
    for y in range(yf + 3, base - 1, 4):
        rect(L, x0 + 1, y, x0 + w - 3, y, "s1")
    rect(L, x0 + 3, yf + 5, x0 + 8, yf + 7, "o1")                       # survey stencil
    rect(L, x0 + 4, yt + 2, x0 + w - 4, yt + 2, "s2")


def tent(L, reg, x0, base, w, h, body=("k3", "k2", "k1", "k0"), trim="o1"):
    """Ridge tent, ridge parallel to the screen: the front (south) slope is a trapezoid (hipped ends), lit; a low
    front wall with an open door flap; guy lines to pegs."""
    hi, mid, lo, dk = body
    eave = base - 8
    ridge = base - h
    m = np.zeros((H, W), bool)
    i0 = int(w * 0.18)
    for y in range(ridge, eave + 1):
        t = (y - ridge) / max(1, eave - ridge)
        inset = int(round(i0 * (1 - t)))
        a, b = x0 + inset, x0 + w - 1 - inset
        rect(L, a, y, b, y, hi if t < 0.5 else mid)
        rect(L, a, y, min(b, a + 3), y, lo)                              # left hip in shade
        rect(L, max(a, b - 2), y, b, y, hi)                              # right hip lit
        for xx in range(a + 14, b - 6, 14):                              # seams on the slope
            px(L, xx, y, mid if t < 0.5 else lo)
        m[y, a:b + 1] = True
    rect(L, x0, eave + 1, x0 + w - 1, base, mid)                          # low front wall
    rect(L, x0, eave + 1, x0 + w - 1, eave + 1, trim)
    dx = x0 + w // 2
    rect(L, dx - 7, eave - 6, dx + 6, base, dk)                           # open door flap
    rect(L, dx + 7, eave - 6, dx + 9, base, hi)
    rect(L, x0, base, x0 + w - 1, base, dk)
    m[eave + 1:base + 1, x0:x0 + w] = True
    reg |= m
    outline_mask(L, m, "k0")
    for sx, ex in ((x0 + i0, x0 - 10), (x0 + w - 1 - i0, x0 + w + 9)):  # guy lines to pegs
        line(L, sx, ridge + 1, ex, base - 2, "k1")
        rect(L, ex, base - 2, ex + 1, base - 1, "s1")


def rover(L, reg, x0, base):
    """Survey ground-effect sled: low chassis, raised cab at the left, cyan light bar, orange flank stripe."""
    box3q(L, reg, x0, base - 6, 104, 18, 20, "k3", "k2", "k3", "k1")
    rect(L, x0 + 2, base - 18, x0 + 100, base - 16, "o1")
    rect(L, x0 + 2, base - 15, x0 + 100, base - 15, "o0")
    box3q(L, reg, x0 + 8, base - 30, 40, 10, 16, "k2", "k1", "k3", "k0")
    rect(L, x0 + 12, base - 42, x0 + 44, base - 37, "k0")               # windscreen
    rect(L, x0 + 13, base - 41, x0 + 30, base - 41, "k2")
    rect(L, x0 + 14, base - 55, x0 + 40, base - 54, "c0"); rect(L, x0 + 16, base - 55, x0 + 38, base - 55, "c1")
    m = np.zeros((H, W), bool)
    for wx in (x0 + 10, x0 + 78):                                         # skids
        rect(L, wx, base - 6, wx + 18, base, "k0"); rect(L, wx + 1, base - 5, wx + 17, base - 4, "k1")
        m[base - 6:base + 1, wx:wx + 19] = True
    reg |= m
    rect(L, x0 + 60, base - 32, x0 + 96, base - 31, "k1")                # cargo rail
    crate(L, reg, x0 + 62, base - 27, 18, 10, 6)


def generator(L, reg, x0, base):
    yt, yf = box3q(L, reg, x0, base, 36, 10, 18, "k3", "k2", "k3", "k1")
    for x in range(x0 + 3, x0 + 20, 3):
        rect(L, x, yf + 4, x, base - 4, "k1")
    rect(L, x0 + 23, yf + 4, x0 + 31, yf + 9, "o1"); rect(L, x0 + 24, yf + 5, x0 + 26, yf + 6, "c1")
    rect(L, x0 + 4, yt + 3, x0 + 12, yt + 5, "k1")


def table(L, reg, x0, base):
    m = np.zeros((H, W), bool)
    for lx in (x0 + 2, x0 + 39):
        rect(L, lx, base - 12, lx + 1, base, "k1"); m[base - 12:base + 1, lx:lx + 2] = True
    reg |= m
    yt, yf = box3q(L, reg, x0, base - 12, 42, 12, 3, "k3", "k2", "m4", "k1")
    rect(L, x0 + 6, yt + 3, x0 + 17, yt + 8, "k0"); rect(L, x0 + 7, yt + 4, x0 + 16, yt + 7, "c1")
    rect(L, x0 + 8, yt + 5, x0 + 12, yt + 5, "c2")
    rect(L, x0 + 24, yt + 4, x0 + 35, yt + 9, "m5"); rect(L, x0 + 25, yt + 6, x0 + 33, yt + 6, "m2")   # map sheet


def light_mast(L, reg, x, base, hgt=84):
    m = np.zeros((H, W), bool)
    top = base - hgt
    for dx, ex in ((-1, -12), (1, 12)):                                   # splayed feet
        line(L, x + dx, base - 14, x + ex, base, "k1")
        line(L, x + dx, base - 13, x + ex, base, "k1")
    rect(L, x - 1, top + 10, x + 1, base - 10, "k2"); rect(L, x + 1, top + 10, x + 1, base - 10, "k3")
    rect(L, x - 1, top + 10, x - 1, base - 10, "k1")
    for lx in (x - 13, x + 2):                                            # two lamp heads (unlit, daytime)
        box3q(L, m, lx, top + 9, 12, 3, 8, "k2", "k0", "k3", "k0")
        rect(L, lx + 2, top + 3, lx + 9, top + 6, "m4")
    rect(L, x - 13, top + 10, x + 13, top + 10, "k1")
    m[top:base + 1, x - 13:x + 14] |= (L[top:base + 1, x - 13:x + 14] >= 0)
    reg |= m


def lamp_post(L, reg, x, base, hgt=88, broken=None):
    """Union Square style cast-iron lamp: plinth, ringed column, lantern; broken='stump' keeps the lower third."""
    m = np.zeros((H, W), bool)
    top = base - hgt
    rect(L, x - 6, base - 9, x + 5, base, "k1"); rect(L, x + 3, base - 9, x + 4, base, "k2")
    rect(L, x - 6, base - 9, x + 5, base - 9, "k2"); rect(L, x - 7, base - 2, x + 6, base, "k0")
    col_top = top + 16 if broken is None else base - 30
    for y in range(col_top, base - 9):
        rect(L, x - 2, y, x + 1, y, "k1"); px(L, x + 1, y, "k2"); px(L, x - 2, y, "k0")
        if (y - col_top) % 18 == 6:
            rect(L, x - 3, y, x + 2, y + 1, "k2"); px(L, x + 2, y, "k3")
    if broken == "stump":
        for i in range(4):                                                # jagged break
            for j in range(int(hval("stump", x, i) * 4)):
                px(L, x - 2 + i, col_top - 1 - j, "k1")
    else:
        rect(L, x - 5, top + 13, x + 4, top + 15, "k1")                   # lantern
        rect(L, x - 4, top + 4, x + 3, top + 12, "k0")
        rect(L, x - 3, top + 5, x + 2, top + 11, "k2")
        rect(L, x - 1, top + 5, x - 1, top + 11, "k0")
        rect(L, x + 1, top + 6, x + 2, top + 9, "hz2")                    # one surviving pane
        rect(L, x - 5, top + 2, x + 4, top + 3, "k1"); rect(L, x - 3, top, x + 2, top + 1, "k1")
        px(L, x - 1, top - 2, "k1"); px(L, x - 1, top - 1, "k2")
    reg_box = (L[max(0, top - 3):base + 1, x - 7:x + 7] >= 0)
    m[max(0, top - 3):base + 1, x - 7:x + 7] = reg_box
    reg |= m


def lamp_toppled(L, x0, base):
    rect(L, x0, base - 4, x0 + 70, base - 2, "k1"); rect(L, x0, base - 4, x0 + 70, base - 4, "k2")
    rect(L, x0, base - 1, x0 + 70, base - 1, "k0")
    for k in range(x0 + 10, x0 + 70, 18):
        rect(L, k, base - 5, k + 1, base - 1, "k2")
    rect(L, x0 + 70, base - 8, x0 + 80, base, "k0"); rect(L, x0 + 71, base - 7, x0 + 79, base - 1, "k2")
    rect(L, x0 + 74, base - 6, x0 + 75, base - 3, "hz2")
    rect(L, x0 - 10, base - 6, x0 - 1, base, "k1"); rect(L, x0 - 10, base - 6, x0 - 1, base - 6, "k2")


def bench_broken(L, reg, x0, base):
    m = np.zeros((H, W), bool)
    rect(L, x0, base - 14, x0 + 22, base - 12, "s3"); rect(L, x0, base - 11, x0 + 22, base - 10, "s2")   # left half seat
    rect(L, x0, base - 20, x0 + 22, base - 18, "s3")                                                   # back rail
    line(L, x0 + 24, base - 12, x0 + 46, base - 2, "s2"); line(L, x0 + 24, base - 13, x0 + 46, base - 3, "s3")  # snapped
    for lx in (x0 + 1, x0 + 20, x0 + 44):
        rect(L, lx, base - 12, lx + 1, base, "k0")
    m[base - 21:base + 1, x0 - 1:x0 + 48] = L[base - 21:base + 1, x0 - 1:x0 + 48] >= 0
    reg |= m
    outline_mask(L, m, "k0")


def sapling(L, reg, x, base, hgt, r, base_tone=3.2):
    m = np.zeros((H, W), bool)
    for y in range(base - hgt, base + 1):
        rect(L, x - 1, y, x, y, "s1"); px(L, x + 1, y, "s2")
        m[y, x - 1:x + 2] = True
    rect(L, x - 3, base - 1, x + 3, base, "s1")
    m[base - 1:base + 1, x - 3:x + 4] = True
    crown(L, x, base - hgt - r * 0.4, r, FOL, base_tone, reg=m, seed=f"sap{x}")
    reg |= m


BIG_TREES = [(96, 452, 22, 290), (1188, 480, 24, 300)]     # foreground trunks: x, base row, width, top row
CAMP = {"tent_a": (300, 496, 96, 50), "tent_b": (420, 430, 70, 40), "rover": (226, 600), "generator": (226, 452),
        "table": (450, 520), "light_mast": (494, 392), "crates": [(420, 560), (446, 566), (432, 548), (360, 548)]}
YOUNG_TREES = [(930, 440, 58, 26), (1030, 560, 66, 30), (850, 628, 34, 16), (1000, 352, 40, 18)]
LAMPS = [(556, 430, None), (724, 430, "stump"), (556, 650, None)]
TOPPLED = (762, 470)
BENCH = (960, 660)
SNAG_FG = (238, 690)


def paint_props():
    L = new()
    items = {}

    def reg_new(name, base):
        items[name] = {"mask": np.zeros((H, W), bool), "base": base}
        return items[name]["mask"]

    tx, tb, tw, th = CAMP["tent_a"]; tent(L, reg_new("tent-a", tb), tx, tb, tw, th)
    tx, tb, tw, th = CAMP["tent_b"]
    tent(L, reg_new("tent-b", tb), tx, tb, tw, th, body=("o2", "o1", "o0", "s0"), trim="k1")
    rx, rb = CAMP["rover"]; rover(L, reg_new("rover", rb), rx, rb)
    gx, gb = CAMP["generator"]; generator(L, reg_new("generator", gb), gx, gb)
    tx, tb = CAMP["table"]; table(L, reg_new("survey-table", tb), tx, tb)
    mx, mb = CAMP["light_mast"]; light_mast(L, reg_new("light-mast", mb), mx, mb)
    for k, (cx, cb) in enumerate(CAMP["crates"]):
        crate(L, reg_new(f"crate-{k}", cb), cx, cb)
    for k, (x, b, br) in enumerate(LAMPS):
        lamp_post(L, reg_new(f"lamp-{k}", b), x, b, broken=br)
    lamp_toppled(L, *TOPPLED)
    bench_broken(L, reg_new("bench-broken", BENCH[1]), *BENCH)
    for k, (x, b, hg, r) in enumerate(YOUNG_TREES):
        sapling(L, reg_new(f"young-tree-{k}", b), x, b, hg, r)
    # big foreground tree trunks (canopies are in fg-occlusion): bark lit on the right, root flare
    for k, (x, base, w, top) in enumerate(BIG_TREES):
        reg = reg_new(f"tree-trunk-{k}", base)
        for y in range(top, base + 1):
            flare = int(max(0, (y - (base - 16))) * 0.7)
            ww = w + 2 * flare
            for i in range(ww):
                xx = x - ww // 2 + i
                u = i / (ww - 1)
                c = "s0" if u < 0.22 else ("s1" if u < 0.58 else ("s2" if u < 0.86 else "s3"))
                if hval("bark", xx // 2, y // 5) < 0.2 and 0.2 < u < 0.8:
                    c = "s0" if u < 0.5 else "s1"
                px(L, xx, y, c); reg[y, xx] = True
    # broken dead snag (foreground, lower left verge edge)
    reg = reg_new("snag-fg", SNAG_FG[1])
    fx, fb = SNAG_FG
    for y in range(fb - 52, fb + 1):
        ww = 10 if y > fb - 30 else 8
        for i in range(ww):
            c = "s0" if i < 3 else ("s1" if i < 6 else "s2")
            px(L, fx - ww // 2 + i, y, c); reg[y, fx - ww // 2 + i] = True
    for i in range(8):
        for j in range(int(hval("snag", i) * 7)):
            px(L, fx - 4 + i, fb - 52 - j, "s2" if i > 4 else "s1"); reg[fb - 52 - j, fx - 4 + i] = True
    return L, items


TRIPOD_H = 44                    # total-station tripod: ~1.6 m at the 48 px heroine scale


def paint_tripod():
    """Survey total station on a tripod (Y-sorted sprite). Two front legs reach the pivot row; the rear leg stops
    6 rows short of it, so the sprite's ground contact (pivot) is the front feet."""
    L = new()
    x, b = TRIPOD
    top = b - TRIPOD_H + 1
    hy = top + 12                                                         # leg head plate row
    for ex, c1, c2 in ((x - 13, "o1", "o0"), (x + 13, "o2", "o1")):     # front legs (right leg lit)
        line(L, x - 2 if ex < x else x + 1, hy, ex, b - 1, c1)
        line(L, x - 1 if ex < x else x + 2, hy, ex + (1 if ex < x else -1), b - 1, c2)
        rect(L, ex - 1, b - 1, ex + 1, b, "k0")                           # shoes
    line(L, x, hy + 1, x + 1, b - 7, "o0")                                # rear leg (behind)
    rect(L, x - 5, hy, x + 5, hy + 2, "k1"); rect(L, x - 5, hy, x + 5, hy, "k2")
    rect(L, x - 1, hy - 3, x + 1, hy - 1, "k1")                           # tribrach
    rect(L, x - 5, top + 1, x + 4, hy - 4, "k2")                          # instrument body
    rect(L, x + 3, top + 1, x + 4, hy - 4, "k3")
    rect(L, x - 4, top + 3, x - 1, top + 5, "c1"); px(L, x - 3, top + 3, "c2")   # screen
    rect(L, x - 2, top, x + 2, top, "k1")                                 # telescope housing
    rect(L, x + 5, top + 2, x + 8, top + 4, "k1"); px(L, x + 8, top + 3, "k0")   # lens
    reg = L >= 0
    outline = reg & ~(np.roll(reg, 1, 0) & np.roll(reg, -1, 0) & np.roll(reg, 1, 1) & np.roll(reg, -1, 1))
    L[outline & (L != I["o1"]) & (L != I["o2"]) & (L != I["o0"])] = I["k0"]
    return L


def paint_mast():
    L = new()
    x, b = MAST
    top = b - 92
    rect(L, x - 5, b - 3, x + 5, b, "k0"); rect(L, x - 4, b - 3, x + 4, b - 2, "k2")      # weighted base plate
    for y in range(top, b - 3):
        seg = (y - top) // 30                                                            # telescoping sections
        w = 1 + (seg >= 1) + (seg >= 2)
        for i in range(w + 1):
            px(L, x - w // 2 + i, y, "k1" if i == 0 else ("k3" if i == w else "k2"))
        if (y - top) % 30 == 0 and y > top:
            rect(L, x - 2, y, x + 2, y, "k0")
    # pennant and beacon
    stamp(L, x + 1, top + 4, ["ooooooo", "oOOOOo.", "oOOo...", "oo....."], {"o": "o1", "O": "o2"})
    rect(L, x - 1, top - 3, x + 1, top - 1, "k0"); px(L, x, top - 2, "c1")
    # instrument box half way up
    stamp(L, x - 4, b - 40, ["kkkkkkk", "kHHHHHk", "kHCCHMk", "kMMMMMk", "kkkkkkk"],
          {"k": "k0", "H": "k3", "M": "k2", "C": "c1"})
    return L


FG_CANOPIES = [  # (cx, cy, rx, ry) big foreground canopies framing the vista (fg-occlusion)
    (40, 40, 160, 120), (170, 120, 96, 66), (50, 230, 110, 92), (108, 268, 70, 50), (230, 26, 90, 48),
    (1250, 40, 170, 130), (1132, 128, 90, 64), (1236, 256, 92, 100), (1160, 296, 70, 46), (1060, 22, 100, 50),
]


def paint_fg():
    L = new()
    m = np.zeros((H, W), bool)
    for cx, cy, rx, ry in FG_CANOPIES:
        m |= ellipse(cx, cy, rx, ry)
    # leafy edge: carve and add bumps along the outline on a 6 px lattice (hand-hashed)
    edge = m & ~(np.roll(m, 6, 0) & np.roll(m, -6, 0) & np.roll(m, 6, 1) & np.roll(m, -6, 1))
    ys, xs = np.nonzero(edge)
    for y, x in zip(ys[::23], xs[::23]):
        r = 3 + int(hval("fgb", x, y) * 6)
        if hval("fgc", x, y) < 0.5:
            m |= ellipse(x, y, r, r * 0.8)
        else:
            m &= ~ellipse(x, y, r * 0.8, r * 0.7)
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        side = 1 if x > CX else -1
        cxr = 1280 if side > 0 else 0
        l = (0.6 if side > 0 else -0.1) - (y / 360) * 0.5 + 0.9 * (hval("fgl", (x + (y // 4) % 2 * 3) // 6, y // 4) - 0.5)
        l += 0.6 * (1 - min(1, abs(x - cxr) / 260)) * (-0.6)
        L[y, x] = FOL[max(0, min(4, int(round(1.6 + l * 2.2))))]
    dn = np.zeros_like(m); dn[:-1] = m[1:]
    L[m & ~dn] = I["f0"]
    # a few hanging leaf sprays below the canopies
    for x, y, n in ((150, 196, 18), (176, 190, 12), (1120, 214, 16), (1146, 210, 22), (1098, 200, 10)):
        for j in range(n):
            px(L, x + (j // 5) % 2, y + j, "f2" if j % 3 else "g2")
    return L


def paint_shadows(layers, items):
    """Opaque cast shadows (shade LUT over the composite underneath), falling up and to the left."""
    base = composite_idx(layers, ["sky", "dome", "west-front", "olmsted-terrace", "arch-ruin-survey",
                                  "far-lawn-basin", "groves", "plaza-ground", "ground-detail"])
    S = np.zeros((H, W), bool)
    for name, it in items.items():
        ys, xs = np.nonzero(it["mask"])
        if not len(ys):
            continue
        b = it["base"]
        hgt = b - ys.min() + 1
        if name.startswith("tree-trunk"):
            continue
        for y, x in zip(ys, xs):
            h = b - y
            sx = int(round(x + SHADOW_DIR[0] * h * 0.6))
            sy = int(round(b + SHADOW_DIR[1] * h * 0.45))
            if 0 <= sx < W and 0 <= sy < H:
                S[sy, sx] = True
    for x, b in (TRIPOD, MAST):
        top = b - (TRIPOD_H if x == TRIPOD[0] else 92)
        for y in range(top, b):
            h = b - y
            for dx in (-2, -1, 0, 1, 2) if x == TRIPOD[0] and h < 20 else (0, 1):
                sx = int(round(x + dx + SHADOW_DIR[0] * h * 0.6)); sy = int(round(b + SHADOW_DIR[1] * h * 0.45))
                if 0 <= sx < W and 0 <= sy < H:
                    S[sy, sx] = True
    # canopy shade pools near the big trunks (dappled by a 4 px lattice) and short trunk shadows
    for cx, cy, r in VERGE_SHRUBS:                          # shrub shadows on the verge
        e = ellipse(cx - r * 0.35, cy + r * 0.45, r * 0.95, r * 0.45)
        S |= e
    S[:PLAZA_TOP + 3] = False
    out = new()
    out[S] = SHADE_LUT[base[S]]
    return out


def composite_idx(layers, names):
    out = new()
    for n in names:
        m = layers[n] >= 0
        out[m] = layers[n][m]
    return out


GROUND_LAYERS = ("plaza-ground", "ground-detail", "cast-shadows")
LUMA = (RGB[:, :3].astype(np.int32) @ np.array([299, 587, 114])) // 1000


def despeckle_ground(layers, passes=2):
    """Final ground clean-up (the v04 audit's 'pale chips read as noise'): a walkable-foreground texel that is
    >= 40 luma brighter than all 8 composited neighbours AND belongs to a ground layer is recoloured, in its own
    layer, to the most common neighbouring composite colour. Sprite highlights on props/Y-sort layers are kept."""
    fixed = 0
    for _ in range(passes):
        comp = composite_idx(layers, ART_LAYERS)
        l = LUMA[comp]
        nb = neighbour_stack(comp)
        nl = np.where(nb >= 0, LUMA[np.maximum(nb, 0)], 0)
        iso = (l - nl.max(0) >= 40)
        iso[:PLAZA_TOP] = False
        for y, x in zip(*np.nonzero(iso)):
            owner = next(n for n in reversed(ART_LAYERS) if layers[n][y, x] >= 0)
            if owner not in GROUND_LAYERS:
                continue
            layers[owner][y, x] = np.bincount(nb[:, y, x][nb[:, y, x] >= 0]).argmax()
            fixed += 1
    return fixed


# ============================================================================ walkability
def heroine_48():
    """Approved v8 static south idle (96 texels = 48 logical px) sampled at 2:1 for scale overlays only."""
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
    # foot (fx, fy) places sprite texel (j, i) at (fy - sh + 1 + j, fx - sw//2 + i)
    oy, ox = np.nonzero(spr_alpha)
    for j, i in zip(oy, ox):
        fy0 = y0 + sh - 1 - j
        fx0 = x0 + sw // 2 - i
        ya, xa = max(0, fy0), max(0, fx0)
        yb, xb = min(H, fy0 + sub.shape[0]), min(W, fx0 + sub.shape[1])
        if ya < yb and xa < xb:
            out[ya:yb, xa:xb] |= sub[ya - fy0:yb - fy0, xa - fx0:xb - fx0]
    return out


def walkable(layers, items, spr_alpha):
    wk = np.zeros((H, W), bool)
    wk[WALK_TOP:H - 2, 6:W - 6] = True
    for x0, x1 in BEDS:
        wk[:, max(0, x0 - (0 if x0 == 0 else 6)):x1 + 1 + (6 if x0 == 0 else 0)] = False
    collars = {}
    for name, it in items.items():           # derived collar: feet north of the base whose sprite overlaps the item
        ov = overlap_feet(it["mask"], spr_alpha)
        yy = np.arange(H)[:, None]
        col = ov & (yy < it["base"])
        ys, xs = np.nonzero(it["mask"])
        foot = np.zeros((H, W), bool)        # footprint collar: feet on the item's own ground rows
        foot[max(0, it["base"] - 6):it["base"] + 4, max(0, xs.min() - 6):xs.max() + 7] = True
        collars[name] = col | foot
        wk &= ~collars[name]
    for name, (x, b), half in (("survey-tripod-ysort", TRIPOD, 12), ("survey-mast-ysort", MAST, 7)):
        c = np.zeros((H, W), bool)
        c[b - 5:b + 5, x - half:x + half + 1] = True
        collars[name] = c
        wk &= ~c
    for (x0, y0, x1, y1) in (LEFT_PANEL, RIGHT_PANEL):   # the tussock meadow stays walkable; curbs are low
        pass
    return wk, collars


def visibility_fails(fg, walk, spr, step=2):
    sh, sw = spr.shape
    tot = spr.sum()
    out = []
    worst = 1.0
    for y in range(0, H, step):
        for x in range(0, W, step):
            if not walk[y, x]:
                continue
            x0, y0 = x - sw // 2, y - sh + 1
            if x0 < 0 or y0 < 0 or x0 + sw > W:
                continue
            vis = 1 - (fg[y0:y0 + sh, x0:x0 + sw] & spr).sum() / tot
            worst = min(worst, vis)
            if vis < 1 / 3:
                out.append((x, y))
    return out, worst


def depth_audit(items, walk, spr_alpha):
    """Every walkable foot (1 px steps): the actor (drawn over the merged base) must never overlap a registered
    tall base item from behind (foot row < item base row)."""
    res = {}
    for name, it in items.items():
        ov = overlap_feet(it["mask"], spr_alpha) & walk
        yy = np.arange(H)[:, None]
        res[name] = {"overlapping_walkable_feet": int(ov.sum()),
                     "wrong_order_feet": int((ov & (yy < it["base"])).sum()), "base_row": it["base"]}
    return res


def erode(mask, rx, ry):
    """Box erosion via summed-area table: True where the (2rx+1)x(2ry+1) box is entirely inside mask."""
    m = np.pad(mask.astype(np.int32), ((ry + 1, ry), (rx + 1, rx)))
    s = m.cumsum(0).cumsum(1)
    k = (2 * ry + 1) * (2 * rx + 1)
    tot = s[2 * ry + 1:, 2 * rx + 1:] - s[:-2 * ry - 1, 2 * rx + 1:] - s[2 * ry + 1:, :-2 * rx - 1] + s[:-2 * ry - 1, :-2 * rx - 1]
    return tot[:H, :W] == k


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


# ============================================================================ scene assembly
def scene():
    spr = heroine_48()
    spr_alpha = spr[..., 3] == 255
    layers = {"sky": paint_sky(), "dome": paint_dome(), "west-front": paint_west_front(),
              "olmsted-terrace": paint_terrace(), "arch-ruin-survey": paint_ruin_survey(),
              "far-lawn-basin": paint_far_lawn_basin(), "groves": paint_groves(), "plaza-ground": paint_plaza(),
              "ground-detail": paint_ground_detail()}
    props, items = paint_props()
    layers["props-low"] = fill_pinholes(props)
    layers["cast-shadows"] = paint_shadows({**layers, "props-low": props}, items)
    layers["survey-tripod-ysort"] = paint_tripod()
    layers["survey-mast-ysort"] = paint_mast()
    layers["fg-occlusion"] = paint_fg()
    despeckled = despeckle_ground(layers)
    walk, collars = walkable(layers, items, spr_alpha)
    layers["guides"] = paint_guides(walk, collars)
    sc = {"layers": layers, "items": items, "walk": walk, "collars": collars, "spr": spr, "spr_alpha": spr_alpha,
          "despeckled_ground_texels": despeckled}
    return sc


def paint_guides(walk, collars):
    L = new()
    for y in range(4, H, 8):                           # 8 px grid: one texel per walkable / blocked cell centre
        for x in range(4, W, 8):
            if y >= PLAZA_TOP:
                L[y, x] = I["gd-walk"] if walk[y, x] else I["gd-block"]
    for c in collars.values():
        ys, xs = np.nonzero(c & ~walk)
        L[ys[::7], xs[::7]] = I["gd-block"]
    for k, (x, y) in PINS.items():
        rect(L, x - 1, y - 1, x + 1, y + 1, "gd-pin")
    for key in GODOT_VIEWS.values():                   # the two Godot camera windows
        x0, y0 = camera_rect(PINS[key])
        rect(L, x0, y0, x0 + CAM_W - 1, y0, "gd-tick"); rect(L, x0, y0 + CAM_H - 1, x0 + CAM_W - 1, y0 + CAM_H - 1, "gd-tick")
        rect(L, x0, y0, x0, y0 + CAM_H - 1, "gd-tick"); rect(L, x0 + CAM_W - 1, y0, x0 + CAM_W - 1, y0 + CAM_H - 1, "gd-tick")
    for x, y in bez([PINS["spawn_entry_steps"], (640, 520), (640, 360), PINS["vista_axis_coping"]], 300):
        px(L, int(x), int(y), "gd-route")
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


YSORT_PIVOTS = {"survey-tripod-ysort": TRIPOD[1], "survey-mast-ysort": MAST[1]}


def runtime_stack_still(rgba, spr, foot):
    """Runtime draw order proposal: base (layers 1-11 merged) -> Y-sorted {tripod, mast, actor} by pivot row (a
    sprite is drawn over the actor when the actor's foot row is north of the sprite's pivot) -> fg-occlusion."""
    out = composite_rgba(rgba, BASE_LAYERS)
    placed = False
    for name, pivot in sorted(YSORT_PIVOTS.items(), key=lambda kv: kv[1]):
        if not placed and foot[1] < pivot:
            paste(out, spr, foot[0], foot[1]); placed = True
        m = rgba[name][..., 3] == 255
        out[m] = rgba[name][m]
    if not placed:
        paste(out, spr, foot[0], foot[1])
    fg = rgba["fg-occlusion"]
    fm = fg[..., 3] == 255
    out[fm] = fg[fm]
    return out


def camera_rect(foot):
    """640x360 logical camera window centred on the actor's body (foot - 24 rows), clamped to the scene (as v04)."""
    cx = min(max(int(foot[0]), CAM_W // 2), W - CAM_W // 2)
    cy = min(max(int(foot[1]) - 24, CAM_H // 2), H - CAM_H // 2)
    return cx - CAM_W // 2, cy - CAM_H // 2


def camera_view(still, foot):
    x0, y0 = camera_rect(foot)
    return still[y0:y0 + CAM_H, x0:x0 + CAM_W]


# ============================================================================ containers
DT = (2026, 10, 16, 1, 46, 50)


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


# ============================================================================ metrics
def isolated_bright(flat, region):
    """Single texels clearly brighter than all 8 neighbours (luma +40): the 'pale fleck' defect from the v04 audit."""
    l = flat[..., :3].astype(np.int32) @ np.array([299, 587, 114]) // 1000
    p = np.pad(l, 1, mode="edge")
    nb = np.stack([p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                   if (dy, dx) != (0, 0)])
    iso = (l - nb.max(0) >= 40)
    m = np.zeros((H, W), bool)
    y0, y1 = region
    m[y0:y1] = True
    ys, xs = np.nonzero(iso & m)
    return int(len(ys)), [[int(x), int(y)] for y, x in zip(ys[:12], xs[:12])]


def dome_metrics(layers):
    d = layers["dome"] >= 0
    ys, xs = np.nonzero(d)
    rows = {}
    for y in range(STATUE[0], DRUM[0]):
        r = np.nonzero(d[y])[0]
        if len(r):
            rows[y] = (int(r.min()), int(r.max()))
    asym = [y for y, (a, b) in rows.items() if abs((CX - a) - (b + 1 - CX)) > 1]
    return {"dome_bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
            "statue_tip_row": int(ys.min()), "silhouette_rows_asymmetric_over_1px": asym,
            "peristyle_width_px": HW["peri_cols"] * 2, "west_front_width_px": WINGS[1][1] - WINGS[0][0] + 1,
            "dome_to_front_width_ratio": round(HW["peri_cols"] * 2 / (WINGS[1][1] - WINGS[0][0] + 1), 3),
            "dome_height_above_roof_px": ROOF["center"] - int(ys.min())}


# ============================================================================ build
def artefacts(sc):
    layers = sc["layers"]
    rgba = {n: to_rgba(layers[n]) for n in LAYERS}
    flat = composite_rgba(rgba, ART_LAYERS)
    comp_png = png_bytes(flat)
    files = {"pxo": make_pxo(rgba, comp_png), "ora": make_ora(rgba, comp_png), "gpl": make_gpl()}
    return rgba, flat, files


def names():
    return {"pxo": fname("scene-editable-15layer", "pxo"), "ora": fname("scene-editable-15layer", "ora"),
            "gpl": fname("scene-palette", "gpl"), "walk": fname("scene-walkability", "json"),
            "flat": fname("scene-flat-art", "png"),
            "manifest": fname("scene-manifest", "json"),
            "establishing": fname("godot-establishing-1280x720-vista", "png"),
            "view_vista-axis": fname("godot-cam640x360-vista-axis", "png"),
            "view_tripod-behind": fname("godot-cam640x360-tripod-behind", "png"),
            "report": fname("technical-check-report", "json")}


def walkability_json(sc):
    walk = sc["walk"]
    cells = []
    for cy in range(0, H, 8):
        row = ""
        for cx in range(0, W, 8):
            row += "1" if walk[cy:cy + 8, cx:cx + 8].all() else ("p" if walk[cy:cy + 8, cx:cx + 8].any() else "0")
        cells.append(row)
    return {"candidate": RUN, "status": "UNAPPROVED test-only candidate; not wired to any runtime scene",
            "grid_px": 8, "cells_legend": {"1": "every foot texel in the cell walkable", "p": "partly walkable",
                                           "0": "not walkable"},
            "cells_rows_top_to_bottom": cells, "walk_top_row": WALK_TOP,
            "backdrop_rows_not_walkable": [0, PLAZA_TOP - 1],
            "pins": {k: list(v) for k, v in PINS.items()},
            "ysort_pivots": {k: [TRIPOD[0] if k.startswith("survey-tripod") else MAST[0], v]
                             for k, v in YSORT_PIVOTS.items()},
            "runtime_draw_order_proposal": "base (layers 1-11 merged) -> Y-sorted {survey-tripod-ysort, "
                                           "survey-mast-ysort, actor} by pivot row -> fg-occlusion",
            "collars": {k: int((v & ~walk).sum()) for k, v in sc["collars"].items()},
            "exits": {"exit_north_pool_walk": "side walk round the drained pool toward the v04 west-grounds scene",
                      "exit_south_pool_walk": "side walk round the drained pool toward the v04 west-grounds scene"}}


def write_new(path, data):
    if os.path.exists(_fs(path)):
        if read_bytes(path) != data:
            raise SystemExit(f"refusing to overwrite a different existing file: {path}")
        return "unchanged"
    with open(_fs(path), "xb") as f:
        f.write(data)
    return "written"


def preview(outdir):
    sc = scene()
    rgba, flat, files = artefacts(sc)
    os.makedirs(outdir, exist_ok=True)
    Image.fromarray(flat, "RGBA").save(os.path.join(outdir, "flat.png"))
    spr = sc["spr"]
    for key in list(GODOT_VIEWS.values()) + ["tripod_front", "mast_behind", "spawn_entry_steps", "canopy_left_edge"]:
        st = runtime_stack_still(rgba, spr, PINS[key])
        if key == ESTABLISHING_PIN:
            Image.fromarray(st, "RGBA").save(os.path.join(outdir, "establishing.png"))
        Image.fromarray(camera_view(st, PINS[key]), "RGBA").save(os.path.join(outdir, f"cam_{key}.png"))
    g = composite_rgba(rgba, ART_LAYERS + ["guides"])
    Image.fromarray(g, "RGBA").save(os.path.join(outdir, "guides.png"))
    rep = static_checks(sc, rgba, flat)
    with open(os.path.join(outdir, "checks.json"), "w") as f:
        json.dump(rep, f, indent=1)
    print(json.dumps(rep["verdicts"], indent=1))


def static_checks(sc, rgba, flat):
    layers, walk, spr = sc["layers"], sc["walk"], sc["spr"]
    v = {}
    v["canvas_1280x720_all_layers"] = all(rgba[n].shape == (H, W, 4) for n in LAYERS)
    v["base_layer_opaque"] = bool((rgba["sky"][..., 3] == 255).all())
    v["binary_alpha_all_layers"] = all(bool(np.isin(rgba[n][..., 3], (0, 255)).all()) for n in LAYERS)
    used = set()
    for n in ART_LAYERS:
        used |= set(np.unique(layers[n][layers[n] >= 0]).tolist())
    v["art_layers_palette_only"] = all(0 <= u < N_ART for u in used)
    flat_cols = {tuple(c) for c in np.unique(flat[..., :3].reshape(-1, 3), axis=0).tolist()}
    pal_cols = {tuple(c) for c in RGB[:N_ART].tolist()}
    v["flat_colours_subset_of_palette"] = flat_cols <= pal_cols
    v["flat_opaque"] = bool((flat[..., 3] == 255).all())
    # drained pool: no water or sky colours inside the basin floor
    basin = np.zeros((H, W), bool); basin[BASIN[0]:BASIN[1] + 1, BASIN_NEAR_X[0]:BASIN_NEAR_X[1] + 1] = True
    fl_idx = composite_idx(layers, ["sky", "dome", "west-front", "olmsted-terrace", "arch-ruin-survey", "far-lawn-basin", "groves"])
    v["drained_pool_no_water_or_sky_texels"] = not bool(np.isin(fl_idx[basin], list(WATER_OR_SKY)).any())
    # dome: whole dome and statue visible inside both Godot windows; silhouette symmetric
    dm = dome_metrics(layers)
    tip = dm["statue_tip_row"]
    views = {}
    for vname, key in GODOT_VIEWS.items():
        x0, y0 = camera_rect(PINS[key])
        views[vname] = {"foot": list(PINS[key]), "camera_xy": [x0, y0], "statue_tip_margin_rows": tip - y0,
                        "dome_fully_inside": bool(tip - y0 >= 0 and x0 <= dm["dome_bbox"][0]
                                                  and dm["dome_bbox"][2] < x0 + CAM_W)}
    v["vista_view_whole_dome_with_8px_sky_margin"] = views["vista-axis"]["statue_tip_margin_rows"] >= 8 and \
        views["vista-axis"]["dome_fully_inside"]
    v["tripod_view_whole_dome_inside"] = views["tripod-behind"]["dome_fully_inside"]
    v["dome_silhouette_symmetric"] = not dm["silhouette_rows_asymmetric_over_1px"]
    # heroine scale and layering
    v["heroine_48_logical_px"] = spr.shape[0] == 48
    fg = layers["fg-occlusion"] >= 0
    fails, worst = visibility_fails(fg, walk, sc["spr_alpha"])
    v["every_walkable_foot_keeps_one_third_visible"] = not fails
    da = depth_audit(sc["items"], walk, sc["spr_alpha"])
    v["depth_audit_zero_wrong_order_feet"] = all(d["wrong_order_feet"] == 0 for d in da.values())
    v["walkable_never_in_backdrop"] = not bool(walk[:WALK_TOP].any())
    # Y-sort cases: behind -> sprite over actor; front -> actor over sprite
    ys_ok = {}
    for key, layer, behind in (("tripod_behind", "survey-tripod-ysort", True), ("tripod_front", "survey-tripod-ysort", False),
                               ("mast_behind", "survey-mast-ysort", True), ("mast_front", "survey-mast-ysort", False)):
        foot = PINS[key]
        st = runtime_stack_still(rgba, spr, foot)
        sm = rgba[layer][..., 3] == 255
        hm = np.zeros((H, W), bool)
        sh, sw = spr.shape[:2]
        x0, y0 = foot[0] - sw // 2, foot[1] - sh + 1
        hm[y0:y0 + sh, x0:x0 + sw] = spr[..., 3] == 255
        both = sm & hm
        n = int(both.sum())
        sprite_on_top = int((st[both] == rgba[layer][both]).all(axis=1).sum())
        ys_ok[key] = {"overlap_texels": n, "sprite_on_top_texels": sprite_on_top,
                      "ok": n > 0 and ((sprite_on_top == n) if behind else (sprite_on_top < n)),
                      "walkable": bool(walk[foot[1], foot[0]])}
    v["ysort_behind_front_correct"] = all(c["ok"] and c["walkable"] for c in ys_ok.values())
    # paths: eroded 11 px foot reaches every pin from the entry
    er = erode(walk, 5, 2)
    reach = flood(er, PINS["spawn_entry_steps"])
    pins_ok = {k: bool(reach[y, x]) for k, (x, y) in PINS.items()}
    v["all_pins_reachable_from_entry"] = all(pins_ok.values())
    # pale flecks
    fleck_fg, fleck_fg_where = isolated_bright(flat, (PLAZA_TOP, H))
    fleck_bd, _ = isolated_bright(flat, (0, PLAZA_TOP))
    v["no_isolated_bright_flecks_in_walkable_foreground"] = fleck_fg == 0
    # 8 px grid: pins on walkable texels; walk mask consistent with guides
    v["pins_on_walkable_texels"] = all(bool(walk[y, x]) for k, (x, y) in PINS.items())
    return {"verdicts": v, "dome": dm, "views": views, "visibility_worst": round(float(worst), 3),
            "visibility_fail_count": len(fails), "depth_audit": da, "ysort_cases": ys_ok, "pins_reachable": pins_ok,
            "isolated_bright_flecks": {"foreground_rows_214_719": fleck_fg, "foreground_examples": fleck_fg_where,
                                       "backdrop_rows_0_213": fleck_bd},
            "palette": {"art_colours": N_ART, "new_colours": NEW_COLOURS, "used_in_flat": len(flat_cols)},
            "walkable_texels": int(walk.sum()), "despeckled_ground_texels": sc["despeckled_ground_texels"]}


# ============================================================================ build / manifest
AOC_REFS = {
    "dome": "https://www.aoc.gov/explore-capitol-campus/buildings-grounds/capitol-building/capitol-dome",
    "olmsted_terrace": "https://www.aoc.gov/explore-capitol-campus/buildings-grounds/capitol-grounds/olmsted-terrace",
}


def v04_untouched():
    return {rel: sha(read_bytes(rp(rel))) == h for rel, h in V04_LOCK.items()}


def manifest(sc, rgba, files, rep):
    nm = names()
    return {
        "project": SLUG, "area": "washington-capitol-dome-west-establishing", "run": RUN, "version": "v01",
        "status": "UNAPPROVED test-only establishing-composition candidate. Not accepted art, not runtime-integrated. "
                  "Acceptance is creator review only; science scene art stays 0/11.",
        "art_approved": False, "runtime_integrated": False, "counters_changed": False,
        "relation_to_v04": f"separate composition; v04 ({V04_RUN}) is read-only and re-hashed by `check`",
        "authoring_route": {
            "method": "deterministic Python tool with hand-written placement tables, authored and run by Claude "
                      "(Claude Code, claude.ai Max subscription, firstParty; no API key, no image model); writes a "
                      "native pxo_version 7 .pxo and an .ora with 15 named layers",
            "pixelorama_gui_paint_pass": False,
            "disclosure": "no desktop/computer-use access to the Pixelorama GUI in this session: hand-authored "
                          "pixels -> .pxo/.ora -> Pixelorama 1.2.3 headless export, compared texel by texel",
            "resumed_from": "partial tool written by the session held at the Claude Max limit (same run id); never "
                            "built before; finished and fixed in the resumed session",
            "no_reference_pixels_copied": True},
        "references": {"aoc_pages_text_only": AOC_REFS, "v04_codex_audit": AUDIT_REL},
        "canvas": {"w": W, "h": H, "camera": "top-down 3/4; top = east (Capitol), bottom = west",
                   "gameplay_camera": "640x360 logical viewport (window 1280x720, integer 2x)",
                   "scale_reference": {"file": HEROINE_REL, "logical_height_px": int(sc["spr"].shape[0])},
                   "forced_perspective": "backdrop rows 0..213 at ~1.55 px/m (Capitol, terrace, lawn, drained "
                                         "pool); walkable foreground rows 218..719 at heroine scale"},
        "layers_bottom_to_top": [
            {"index": i + 1, "name": n, "visible": n != "guides", "locked": n == "guides",
             "runtime_export": ("merged into base" if n in BASE_LAYERS else
                                f"separate Y-sorted sprite, pivot row {YSORT_PIVOTS[n]}" if n in YSORT_PIVOTS else
                                "overlay above actors" if n == "fg-occlusion" else "never exported"),
             "opaque_texels": int((rgba[n][..., 3] == 255).sum())} for i, n in enumerate(LAYERS)],
        "palette": [{"name": n, "hex": "#" + h} for n, h in PALETTE],
        "guide_palette": [{"name": n, "hex": "#" + h} for n, h in GUIDE_PALETTE],
        "pins": {k: list(v) for k, v in PINS.items()},
        "godot_views": {"establishing_1280x720": ESTABLISHING_PIN, **{f"cam640x360_{k}": v
                                                                     for k, v in GODOT_VIEWS.items()}},
        "static_checks": rep,
        "files_sha256_bytes": {nm[k]: sha(v) for k, v in files.items()},
        "tool": {"file": TOOL_REL, "sha256_text_lf_v1": sha_text(read_bytes(os.path.abspath(__file__))),
                 "python": sys.version.split()[0], "pillow": Image.__version__, "numpy": np.__version__},
    }


def build_all():
    sc = scene()
    rgba, flat, files = artefacts(sc)
    files["flat"] = png_bytes(flat)
    return sc, rgba, flat, files


def build():
    sc, rgba, flat, files = build_all()
    if build_all()[3] != files:
        raise SystemExit("build is not deterministic")
    if not all(v04_untouched().values()):
        raise SystemExit("v04 candidate files changed; refusing to build")
    rep = static_checks(sc, rgba, flat)
    cand = rp(CAND_REL)
    os.makedirs(_fs(cand), exist_ok=True)
    nm = names()
    for k in ("pxo", "ora", "flat", "gpl"):
        print(write_new(os.path.join(cand, nm[k]), files[k]), nm[k])
    files["walk"] = (json.dumps(walkability_json(sc), indent=1) + "\n").encode()
    print(write_new(os.path.join(cand, nm["walk"]), files["walk"]), nm["walk"])
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
    tmp = tempfile.mkdtemp(prefix="wb-domegate-")
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
# composite runtime-stack stills (base -> Y-sorted {sprites, actor} by pivot row -> fg-occlusion) with blend_rect,
# save the 1280x720 establishing still and cut the native 640x360 logical camera windows round the actor.
func _init():
	var a = OS.get_cmdline_user_args()
	var dir: String = a[0]
	var cases = JSON.parse_string(FileAccess.get_file_as_string(dir + "/cases.json"))
	var out = {"layers": {}, "stills": {}}
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
	for key in cases["feet"].keys():
		var foot = cases["feet"][key]
		var st = imgs[cases["base_layers"][0]].duplicate()
		for i in range(1, cases["base_layers"].size()):
			st.blend_rect(imgs[cases["base_layers"][i]], Rect2i(0, 0, 1280, 720), Vector2i(0, 0))
		var hp = Vector2i(int(foot[0]) - hero.get_width() / 2, int(foot[1]) - hero.get_height() + 1)
		var placed = false
		for sp in cases["ysort_sprites"]:
			if not placed and int(foot[1]) < int(sp[1]):
				st.blend_rect(hero, Rect2i(0, 0, hero.get_width(), hero.get_height()), hp)
				placed = true
			st.blend_rect(imgs[sp[0]], Rect2i(0, 0, 1280, 720), Vector2i(0, 0))
		if not placed:
			st.blend_rect(hero, Rect2i(0, 0, hero.get_width(), hero.get_height()), hp)
		st.blend_rect(imgs["fg-occlusion"], Rect2i(0, 0, 1280, 720), Vector2i(0, 0))
		st.save_png(dir + "/still_" + key + ".png")
		var cx = clampi(int(foot[0]), 320, 1280 - 320)
		var cy = clampi(int(foot[1]) - 24, 180, 720 - 180)
		var cam = st.get_region(Rect2i(cx - 320, cy - 180, 640, 360))
		cam.save_png(dir + "/cam_" + key + ".png")
		out["stills"][key] = [st.get_width(), st.get_height(), cam.get_width(), cam.get_height()]
	var f = FileAccess.open(dir + "/godot_report.json", FileAccess.WRITE)
	f.store_string(JSON.stringify(out))
	f.close()
	print("GODOT_GATE_DONE")
	quit()
'''


def godot_gate(godot, files, rgba):
    """Throwaway Godot project under %TEMP% with APPDATA also redirected there: nothing touches game/ or the real
    Godot user dir. Returns the establishing still (1280x720) and the two 640x360 camera windows."""
    tmp = tempfile.mkdtemp(prefix="wb-domegodot-")
    rep = {"godot": GODOT_REL, "godot_sha256": sha(read_bytes(godot)), "steps": {}}
    caps = {}
    proj_name = f"wdc-dome-gate-{RUN_ID}"
    feet = {k: list(PINS[k]) for k in sorted(set(GODOT_VIEWS.values()) | {ESTABLISHING_PIN})}
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
            json.dump({"art_layers": ART_LAYERS, "base_layers": BASE_LAYERS, "feet": feet,
                       "ysort_sprites": sorted(([k, v] for k, v in YSORT_PIVOTS.items()), key=lambda kv: kv[1])}, f)
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
        st_ok, cam_ok = {}, {}
        for k, foot in feet.items():
            b = read_bytes(os.path.join(data, f"still_{k}.png"))
            got = decode(b)[2]
            exp = runtime_stack_still(rgba, spr, tuple(foot))
            st_ok[k] = bool(got.shape == exp.shape and (got == exp).all())
            cb = read_bytes(os.path.join(data, f"cam_{k}.png"))
            cgot = decode(cb)[2]
            cexp = camera_view(exp, tuple(foot))
            cam_ok[k] = bool(cgot.shape == (CAM_H, CAM_W, 4) and cgot.shape == cexp.shape and (cgot == cexp).all())
            rep["steps"]["still_" + k] = {"foot": foot, "still_size": list(got.shape[1::-1]),
                                          "equals_python_runtime_stack": st_ok[k],
                                          "differing_texels": int((got != exp).any(axis=2).sum()),
                                          "camera_rect_xy": list(camera_rect(foot)), "camera_size": list(cgot.shape[1::-1]),
                                          "camera_equals_python": cam_ok[k]}
            if k == ESTABLISHING_PIN:
                caps["establishing"] = b
            for vname, key in GODOT_VIEWS.items():
                if key == k:
                    caps["view_" + vname] = cb
        rep["heroine_h_in_godot"] = gr.get("heroine_h")
        rep["verdicts"] = {"godot_loads_layers_exact": all(lay_ok.values()) and rep["exit_code"] == 0,
                           "godot_stills_match_ysort_and_occlusion": all(st_ok.values()),
                           "godot_camera_640x360_match": all(cam_ok.values()),
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
    v4 = v04_untouched()
    rep["v04_lock"] = v4
    gates["v04_untouched"] = all(v4.values())
    with zipfile.ZipFile(io.BytesIO(files["pxo"])) as z:
        dj = json.loads(z.read("data.json"))
    gates["pxo_layer_stack_is_15_named_layers"] = [l["name"] for l in dj["layers"]] == LAYERS and \
        [l["visible"] for l in dj["layers"]] == [n != "guides" for n in LAYERS] and len(LAYERS) == 15
    gates["build_deterministic"] = build_all()[3] == files
    caps = {}
    if use_pixelorama:
        rep["pixelorama"] = pixelorama_gate(exe, files, rgba, flat)
        gates.update(rep["pixelorama"]["verdicts"])
    if godot:
        rep["godot"], caps = godot_gate(godot, files, rgba)
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
