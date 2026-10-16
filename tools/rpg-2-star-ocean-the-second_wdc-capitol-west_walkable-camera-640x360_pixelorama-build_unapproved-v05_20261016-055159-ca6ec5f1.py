"""UNAPPROVED, TEST-ONLY candidate v05: U.S. Capitol WEST GROUNDS as ONE 640x360 walkable gameplay camera (2537).

Deterministic Python tool authored and run by Claude (Claude Code, Opus 5.5, claude.ai Max subscription, firstParty;
no API key, no image model, no paid fallback). Worlds Between art workstream; disjoint from City Hall and Git QA.

What it writes: one 640x360 logical-pixel scene (exactly one gameplay camera: game/project.godot viewport 640x360,
window 1280x720, integer 2x) as an editable layer stack -- a native Pixelorama .pxo (pxo_version 7) and an .ora --
plus a palette (.gpl), a collision/walk mask PNG, a walkability + interaction JSON and a manifest. `check` adds the
Pixelorama 1.2.3 headless round-trip (APPDATA redirected), a Godot 4.7.2 headless texel/collision gate, and real
WINDOWED Godot renders at 1280x720 and at 640x360. Nothing is wired into the game runtime: no scene, script, data,
test, default or camera setting is touched; science scene art acceptance stays 0/11.

Why v05 (docs/qa/...wdc-capitol-west-v04-codex-visual-audit_unapproved-v01_20261016-013712-a9d83f26.md): v04's
entry view had no Capitol, its portico view cut the facade off with no dome, the paving/lawn were even and generic,
props repeated and the landmark was weak. v05 is a NEW single-screen composition: the West Front, the dome with the
Statue of Freedom and the Olmsted lower west terrace (twin stairs, central recess) are inside the same 640x360 camera
the heroine walks in. v04 (run wdc-capitol-west-v04_20261016-004457-a17af0a6) and the cinematic vista v02 (run
wdc-dome-west-v02_20261016-044903-cdb4ebdb) are READ-ONLY: `check` re-hashes them (LOCK). No v02 pixel is copied: the
vista is a 1280x720 telephoto from the Reflecting Pool; this camera is a different, nearer projection and every
cluster here is placed for this camera.

AUTHORING ROUTE (disclosed). NOT a Pixelorama GUI paint pass (no desktop/computer-use access to the GUI in this
session). Every architectural stage, bay state, damage item, tree lobe, rubble block, prop, collar, pin, exit and
interaction is an explicit hand-written table entry below; the tool rasterises those tables into named palette layers.
No continuous-colour or generated image is pasted anywhere. The .pxo opens in the Pixelorama GUI as editable layers.

Depth (documented so the landmark/heroine scale relation is checkable):
  * walkable plaza (rows ~205..359): game 3/4 projection at the approved heroine scale, 48 logical px = 1.7 m
    (28 px/m), i.e. the scale of the plaza's far edge in the backdrop camera below (d ~ 20 m); nearer ground is not
    enlarged (JRPG convention, stated, not hidden).
  * backdrop (everything north of the Olmsted seat wall): ONE pinhole camera, F = 552 logical px, eye 1.0 m above the
    plaza, horizon row HZ = 178.4; the West Lawn rises 7 m from the wall (d = 20 m) to the lower-terrace foot
    (d = 230 m). Ground at distance d projects to row HZ + (EYE - e(d)) * F / d.
      - Olmsted lower west terrace at d ~ 230 m -> 2.4 px/m (rows 137..163, foot row 164);
      - West Front facade at d ~ 310 m -> 1.78 px/m (rows 92..140; 228 m front = x 168..575);
      - dome at d ~ 366 m (it stands ~56 m behind the West Front) -> 1.51 px/m (stylobate row 92 .. Statue of
        Freedom tip row 6); the drum below the peristyle is hidden behind the central pavilion, as seen from the lawn.
      - mid trees 45..110 m, the distant patrol walker at 70 m (7.9 px/m, ~2.2 m tall = 17 px).
    The wall/steps band at d ~ 20 m (26-28 px/m) hides the seam between the two projections; rows are hand-set
    within +-10 % of this mapping (table DEPTH_TABLE is written to the manifest).
2537 story (game fiction, asymmetric, continuous with the v02 vista): breach in the south (right) dome shell, three
  missing south peristyle columns, collapsed House (south) wing corner, ivy over the Senate (north) wing, a collapsed
  bay of the Olmsted seat wall with a self-sown tree of heaven, a field survey station aimed at the West Front, an
  active patrol waypoint beacon with three-toed claw prints and laser scorch, and a patrol walker on the lawn.
Reference forms (text facts only, nothing copied): Architect of the Capitol dome page (cast-iron dome, peristyle,
  attic, tholos, Statue of Freedom) and Olmsted Terrace page (marble terraces, balustrades, grand stairs, bronze lamps).

Modes
  preview <dir>   render layers, flat, runtime stills, 2x views and guides into <dir> (outside the repo)
  build           write candidate files (never overwrites a different file)
  check           static gates + LOCK + Pixelorama headless round-trip (--no-pixelorama) + Godot gates in throwaway
                  temp projects (--no-godot); --write-report writes the JSON report and the Godot captures (1280x720
                  and 640x360) into outputs/<RUN>/.
Run: python -I -B <this file> preview <tempdir> | build | check [--write-report] [--no-pixelorama] [--no-godot]
"""
import argparse, hashlib, io, json, math, os, shutil, subprocess, sys, tempfile, time, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
AREA = "wdc-capitol-west"
VER = "unapproved-v05"
STAMP = "20261016-055159"
RUN_ID = "ca6ec5f1"
RUN = f"wdc-cw-v05_{STAMP}-{RUN_ID}"          # short run dir: keeps every candidate/output path under MAX_PATH (260)
CAND_REL = f"game/assets/environments/candidates/{RUN}"
OUT_REL = f"outputs/{RUN}"
TOOL_REL = "tools/" + os.path.basename(os.path.abspath(__file__))
AUDIT_REL = ("docs/qa/rpg-2-star-ocean-the-second_wdc-capitol-west-v04-codex-visual-audit_unapproved-v01_"
             "20261016-013712-a9d83f26.md")
HEROINE_REL = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_"
               "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
PIXELORAMA_DEFAULT = "C:/Users/hkzha/AppData/Local/Programs/Pixelorama-1.2.3/Pixelorama-Windows-64bit/Pixelorama.exe"
PIXELORAMA_VERSION = "v1.2.3-stable"
GODOT_REL = "work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe"      # gitignored local tooling
W, H = 640, 360                   # one gameplay camera (logical viewport)
VIEW = 2                          # window 1280x720 = integer 2x
WIN_LONG_PREFIX = "\\\\?\\"

# Read-only predecessors: digest of every file (text files CRLF->LF, others raw bytes), taken 2026-10-16 05:52
# before this tool existed. `check` recomputes them.
LOCK = {
    "game/assets/environments/candidates/wdc-capitol-west-v04_20261016-004457-a17af0a6":
        "b0b959f5054dd9ba5425091c6925619778dae2bf69cbd5e5ccd0596be0daf3c4",
    "outputs/wdc-capitol-west-v04_20261016-004457-a17af0a6":
        "d0bc92373354aa453d8e2b1be97acbaf32b34e6c7b4c711a887e2161d0282d8a",
    "tools/rpg-2-star-ocean-the-second_washington-capitol_west-grounds-scene-candidate_pixelorama-build_unapproved-v04_"
    "20261016-004457-a17af0a6.py": "t:a473df85717616c8a9bdb6c2b10ef5eb0a757085207a14279dc9e6bcc1bb0be5",
    "docs/qa/rpg-2-star-ocean-the-second_washington-capitol_west-grounds-scene-candidate_qa-note-unapproved-v04_"
    "20261016-004457-a17af0a6.md": "t:7f19c247cfd62537284a1dc9b549e3fbcfa969d70e4c784064d20444b66c6029",
    AUDIT_REL: "t:e1f3bca4747c994908e9ff27d02c01b9c1a96ee394a2968db3ec066fd34590c8",
    "game/assets/environments/candidates/wdc-dome-west-v02_20261016-044903-cdb4ebdb":
        "7cdf5545684608098da46d1cb34b2251daebec66cc01a9857247ac9a505ff25c",
    "outputs/wdc-dome-west-v02_20261016-044903-cdb4ebdb":
        "82bd167fa52bf843fa12585c6b4416b86b55a93ea3f59b46c51fd66922bbbd65",
    "tools/rpg-2-star-ocean-the-second_wdc-dome-west_cinematic-vista-candidate_pixelorama-build_unapproved-v02_"
    "20261016-044903-cdb4ebdb.py": "t:7e77d212cbed35e3865c63b241e3106a57d6105b404c6c08d4347b1cb7ad7b02",
    "docs/qa/rpg-2-star-ocean-the-second_wdc-dome-west_cinematic-vista_qa-note_unapproved-v02_20261016-044903-"
    "cdb4ebdb.md": "t:cc169996a72df3d2df8b46a1d366f7bf7f8c2e7c953e8f33e1766852fe13850f",
    "docs/qa/rpg-2-star-ocean-the-second_wdc-dome-west-v02-codex-visual-audit_unapproved-v01_20261016-054107-"
    "9117f501.md": "t:c97bb2b8ac27c7c0f5fcc2f4902e25752e61b1e0ea0c43d9e3789c4860029372",
    "game/assets/environments/candidates/nyc-chp-v01_20261016-044931-92357bf2":
        "baf62e443cb338508ec58d775d771633295c3be5ecb022e14a6b1ae480b79eac",
}
V04_FLAT = ("game/assets/environments/candidates/wdc-capitol-west-v04_20261016-004457-a17af0a6/rpg-2-star-ocean-the-"
            "second_wdc-capitol-west_scene-flat-art_unapproved-v04_20261016-004457-a17af0a6.png")


def fname(purpose, ext):
    """AGENTS naming: project slug, area, purpose, version, timestamp and run id are all in the file name."""
    return f"{SLUG}_{AREA}_{purpose}_{VER}_{STAMP}-{RUN_ID}.{ext}"


EXPORT_STEM = f"{SLUG}_{AREA}_pixelorama-export_{VER}_{STAMP}-{RUN_ID}"

LAYERS = ["sky", "clouds", "capitol-dome", "capitol-west-front", "capitol-ruin", "olmsted-terrace", "west-lawn",
          "grounds-trees", "lawn-edge-planting", "seat-wall-steps", "plaza-ground", "ground-detail", "cast-shadows",
          "rubble-collapse", "props-low", "survey-mast-ysort", "survey-tripod-ysort", "beacon-ysort", "elm-ysort",
          "fg-occlusion", "guides"]                                                     # bottom -> top
ART_LAYERS = LAYERS[:-1]
BASE_LAYERS = LAYERS[:15]                                                  # merged into one base at runtime
YSORT_LAYERS = LAYERS[15:19]

# ============================================================================ palette (all hand-picked for v05)
PALETTE = [
    ("ink", "14161b"),
    # late-afternoon sky, top -> horizon, and clouds (sun low in the south-west, behind the viewer's left)
    ("sk0", "3d5b84"), ("sk1", "4a6a93"), ("sk2", "5a7aa1"), ("sk3", "6e8cae"), ("sk4", "86a0ba"),
    ("sk5", "a2b5c3"), ("sk6", "c1cac6"), ("sk7", "ddd5bd"),
    ("cl0", "f5ead2"), ("cl1", "e2d8c3"), ("cl2", "c6c5bc"), ("cl3", "a5adb3"),
    # distant marble / painted cast iron (hazed blue shadows, warm sunlit planes)
    ("dm0", "56606d"), ("dm1", "6e7884"), ("dm2", "8b929a"), ("dm3", "a9aca9"), ("dm4", "c6c4b8"),
    ("dm5", "dfd8c6"), ("dm6", "f1e8d2"),
    ("dw0", "3b4350"), ("dw1", "4c5563"), ("br0", "33383f"), ("br1", "50565d"),
    ("ru0", "7d604c"), ("ru1", "9b7a5c"),
    # distant grounds foliage (~250 m), mid trees (45..110 m)
    ("vg0", "4a5d5a"), ("vg1", "5a6e64"), ("vg2", "6d806d"), ("vg3", "849277"), ("vg4", "9da585"),
    ("mg0", "253a30"), ("mg1", "33503b"), ("mg2", "466a46"), ("mg3", "5e8650"), ("mg4", "7fa25e"),
    # West Lawn meadow (far -> near warm), haze
    ("lw0", "4d6038"), ("lw1", "617443"), ("lw2", "7a8a4f"), ("lw3", "95a05d"), ("lw4", "b0b06c"),
    ("lw5", "c4bd83"), ("hz0", "a9b19c"), ("hz1", "bec2ae"),
    # near foliage and grass
    ("f0", "13221d"), ("f1", "1c3325"), ("f2", "28472b"), ("f3", "3a6132"), ("f4", "537c3c"), ("f5", "739b4a"),
    ("f6", "9bbb60"),
    ("g0", "1d331f"), ("g1", "2b4b27"), ("g2", "3b6430"), ("g3", "527f39"), ("g4", "6e9a44"), ("g5", "90b454"),
    ("g6", "b6c870"), ("d0", "86844a"), ("d1", "a89b5c"), ("d2", "c6b47a"),
    # bark, soil, moss
    ("b0", "271d18"), ("b1", "413128"), ("b2", "614c3b"), ("b3", "836c56"),
    ("s0", "2c221b"), ("s1", "47372b"), ("s2", "634e3b"), ("s3", "82664b"), ("s4", "a38764"),
    ("mo0", "45552a"), ("mo1", "667833"),
    # near granite (Olmsted walls) and marble (coping, balusters)
    ("gr0", "33323a"), ("gr1", "4d4b52"), ("gr2", "6a676b"), ("gr3", "88837f"), ("gr4", "a49d95"),
    ("gr5", "c0b8ac"),
    ("m3", "b8b0a3"), ("m4", "d2c9b9"), ("m5", "e6ddcb"), ("m6", "f6eedc"),
    # plaza paving (warm granite setts / flags)
    ("p0", "4a4540"), ("p1", "665e56"), ("p2", "837a6f"), ("p3", "9f9585"), ("p4", "b9ae9c"), ("p5", "d0c5b1"),
    # bronze lamps (verdigris)
    ("bz0", "23241f"), ("bz1", "383a30"), ("bz2", "4c6656"), ("bz3", "74a088"),
    # survey kit: graphite, teal light, muted safety orange, solar cells, olive tarp
    ("k0", "1b2129"), ("k1", "2b3440"), ("k2", "434f5c"), ("k3", "677685"), ("k4", "97a4b0"),
    ("t0", "1c6b70"), ("t1", "36b0aa"), ("t2", "9cefe0"),
    ("o0", "86421f"), ("o1", "c06a2b"), ("o2", "e3a449"),
    ("sp0", "1c2846"), ("sp1", "2d4574"), ("sp2", "6a8cc1"),
    ("tp0", "3b4733"), ("tp1", "566645"),
    # patrol machine light, rust, scorch, flowers
    ("r0", "6a1e22"), ("r1", "c03a32"), ("r2", "ff7b5b"),
    ("ru2", "6a3c26"), ("ru3", "925638"), ("sc0", "282321"), ("sc1", "3e3531"),
    ("fl0", "dcbf48"), ("fl1", "b38ad0"), ("fl2", "efeadb"), ("fl3", "cf613f"),
]
GUIDE_PALETTE = [("gd-walk", "3cdcff"), ("gd-block", "ff285a"), ("gd-pin", "ffe600"), ("gd-route", "ff00ff"),
                 ("gd-exit", "00ff6a"), ("gd-act", "ff9a00")]
ALL_PAL = PALETTE + GUIDE_PALETTE
I = {n: i for i, (n, _) in enumerate(ALL_PAL)}
RGB = np.array([[int(h[j:j + 2], 16) for j in (0, 2, 4)] for _, h in ALL_PAL], np.uint8)
N_ART = len(PALETTE)
LUMA = (RGB[:, :3].astype(np.int32) @ np.array([299, 587, 114])) // 1000


def R(*names):
    return [I[n] for n in names]


DOME = R("dm0", "dm1", "dm2", "dm3", "dm4", "dm5", "dm6")
VG = R("vg0", "vg1", "vg2", "vg3", "vg4")
MG = R("mg0", "mg1", "mg2", "mg3", "mg4")
LW = R("lw0", "lw1", "lw2", "lw3", "lw4", "lw5")
NEAR = R("f0", "f1", "f2", "f3", "f4", "f5", "f6")
GR = R("g0", "g1", "g2", "g3", "g4", "g5", "g6")
GRAN = R("gr0", "gr1", "gr2", "gr3", "gr4", "gr5")
PAVE = R("p0", "p1", "p2", "p3", "p4", "p5")
BARK = R("b0", "b1", "b2", "b3")

# opaque cast-shadow colour for whatever a shadow falls on (no semi-alpha anywhere)
SHADE = {"g6": "g4", "g5": "g3", "g4": "g2", "g3": "g1", "g2": "g1", "g1": "g0", "g0": "f0",
         "d2": "d0", "d1": "d0", "d0": "g1", "p5": "p3", "p4": "p2", "p3": "p2", "p2": "p1", "p1": "p0", "p0": "s0",
         "s4": "s2", "s3": "s1", "s2": "s1", "s1": "s0", "s0": "ink", "mo1": "mo0", "mo0": "g0",
         "gr5": "gr3", "gr4": "gr2", "gr3": "gr2", "gr2": "gr1", "gr1": "gr0", "m6": "m4", "m5": "m3", "m4": "gr3",
         "m3": "gr2", "f6": "f4", "f5": "f3", "f4": "f2", "f3": "f2", "f2": "f1", "f1": "f0",
         "fl0": "d0", "fl1": "g2", "fl2": "p3", "fl3": "ru3", "b3": "b1", "b2": "b1", "b1": "b0",
         "sc1": "sc0", "lw5": "lw3", "lw4": "lw2", "lw3": "lw1", "lw2": "lw1", "lw1": "lw0"}
SHADE_LUT = np.arange(len(ALL_PAL), dtype=np.int16)
for _a, _b in SHADE.items():
    SHADE_LUT[I[_a]] = I[_b]

# haze: one step toward the lawn/terrace-foot air (far lawn rows only)
HAZE = {"lw0": "lw1", "lw1": "lw2", "lw2": "vg3", "lw3": "vg4", "lw4": "hz0", "lw5": "hz1", "s3": "lw3",
        "s2": "lw2", "mg1": "vg1", "mg2": "vg2", "mg3": "vg3", "mg4": "vg4", "p3": "hz1", "p2": "hz0"}
HAZE_LUT = np.arange(len(ALL_PAL), dtype=np.int16)
for _a, _b in HAZE.items():
    HAZE_LUT[I[_a]] = I[_b]

# ============================================================================ camera + depth (see docstring)
CAPX = 371.5                      # Capitol / Mall axis between columns 371 and 372 (mirror: x' = 743 - x)
F = 552.0
EYE = 1.0
HZ = 178.4
D_TERRACE, D_FACADE, D_DOME = 230.0, 310.0, 366.0


def lawn_elev(d):
    return 7.0 * float(np.clip((d - 20.0) / 210.0, 0.0, 1.0))


def row_of(d, e=None):
    e = lawn_elev(d) if e is None else e
    return HZ + (EYE - e) * F / d


def d_of_row(y):
    """Inverse of row_of on the lawn (rows 164..206 -> d 230..20 m); nearer rows are the walkable plane."""
    if y >= row_of(20.0):
        return 20.0
    if y <= row_of(D_TERRACE):
        return D_TERRACE
    lo, hi = 20.0, D_TERRACE
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if row_of(mid) > y:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def proj(X, d):
    return CAPX + X * F / d, row_of(d)


DEPTH_TABLE = [  # element, assumed distance m, px per m, rows
    ("walkable plaza (game 3/4 plane)", "<= 20", 28.0, "205..359"),
    ("Olmsted seat wall, steps, cheek lanterns", 20, round(F / 20, 2), "192..238"),
    ("near lawn shrubs behind the wall", "20..30", "18..28", "170..236"),
    ("mid trees (left / right groups)", "45..110", "5..12", "24..181"),
    ("patrol walker on the lawn", 70, round(F / 70, 2), "157..174"),
    ("Olmsted lower west terrace (stairs, recess)", D_TERRACE, round(F / D_TERRACE, 2), "137..163"),
    ("West Front facade", D_FACADE, round(F / D_FACADE, 2), "92..140"),
    ("dome, peristyle .. Statue of Freedom", D_DOME, round(F / D_DOME, 2), "6..92"),
]

# ============================================================================ hand-authored geometry (logical px)
# --- dome stages (rows) and half widths, axis CAPX
TIP = 6
STATUE_TOP = 6
LANTERN = {"cap": (15, 17), "cornice": (18, 18), "cols": (19, 26), "base": (27, 30)}
SHELL = (31, 58)
SHELL_A, SHELL_B, SHELL_BASE = 23.0, 30.0, 59.0
ATTIC = (59, 67)
PERI_BAL = (68, 69)
PERI_ENT = (70, 73)
PERI_COLS = (74, 89)
STYLOBATE = (90, 92)
DOME_HW = {"attic": 26, "attic_cornice": 27, "peri_bal": 30, "peri_ent": 32, "peri_cols": 30, "stylobate": 33}
PERI_MISSING = (25, 35, 45)        # azimuth deg (+ = south / right): game fiction, three missing columns
BREACH = {38: (9, 11), 39: (8, 13), 40: (8, 14), 41: (9, 15), 42: (9, 16), 43: (10, 16), 44: (10, 15), 45: (11, 15),
          46: (12, 14)}            # row -> (X0, X1) relative to the axis: open hole in the south shell
BREACH_RIBS = ((11, 39, 45), (14, 40, 44))
RUST = ((10, 47, 52, "ru0"), (13, 47, 50, "ru1"), (15, 46, 49, "ru0"), (8, 47, 49, "ru1"))
# --- West Front (left half, absolute columns; the right half mirrors x' = 743 - x before asymmetric states)
SECTIONS_L = [("wing", 168, 247, 98), ("corridor", 248, 271, 102), ("center", 272, 327, 96),
              ("pavilion", 328, 371, 92)]
PROJECTION = {"pavilion": 3, "wing": 2, "center": 1, "corridor": 0}
FACADE_BOTTOM = 140
STRING = 122
GROUND_FLOOR = (124, 139)
PAV_COLS_L = [330, 338, 346, 354, 362]                 # 2-px colonnade columns (left x), mirror -> right half
WING_PORTICO_L = (186, 230)
WING_COLS_L = [187, 194, 201, 208, 215, 222, 229]
CENTER_BAYS_L = [274, 280, 286, 292, 298, 304, 310, 316, 322]
CORRIDOR_BAYS_L = [252, 258, 264]
WING_BAYS_L = [171, 177, 235, 241]
# window state per bay, hand-assigned (g glass, d dark, b broken, o boarded, v vine, s scorched)
STATE_CENTER = {"L": "gdgvgdbgd", "R": "dgbsgsbdg"}
STATE_CORR = {"L": "gvd", "R": "sbd"}
STATE_WING = {"L": "vvdv", "R": "gdsb"}
PAV_COL_MISSING_R = (0,)          # index into the mirrored right pavilion columns (nearest the axis is index 0)
WING_COL_TOPPLED_R = (2, 5)       # right (House) wing portico columns down
HOUSE_COLLAPSE = [(529, 98), (532, 97), (534, 103), (537, 102), (539, 108), (542, 106), (544, 111), (548, 110),
                  (550, 117), (553, 115), (556, 121), (559, 120), (561, 126), (565, 124), (568, 130), (571, 129),
                  (573, 134), (575, 136)]                   # jagged broken roofline of the House wing corner
IVY_WING_L = [(170, 99, 30, 3), (176, 101, 17, 2), (188, 104, 25, 4), (204, 101, 13, 2), (214, 104, 22, 3),
              (232, 99, 33, 3), (243, 100, 14, 2), (256, 104, 12, 2), (274, 98, 10, 2)]
ROOF_SHRUBS = [(178, 97, 4), (202, 96, 3), (240, 97, 5), (262, 101, 3), (553, 104, 4), (566, 118, 6)]
SOOT = [(420, 108, 9), (446, 106, 11), (452, 128, 8), (486, 108, 7), (510, 126, 9)]
# --- Olmsted lower west terrace (2.4 px/m), full width
T_RAIL, T_BAL, T_BASE = 137, (138, 140), 141
T_WALL = (142, 160)
T_FOOT = (161, 163)
STAIRS_T = ((300, 330), (413, 443))
CHEEKS_T = ((297, 299), (331, 333), (410, 412), (444, 446))
RECESS = (334, 409)
GROTTO = (364, 379, 147, 160)
FOUNTAIN_T = (352, 391, 157, 163)
T_PIERS = [26, 62, 98, 134, 170, 206, 242, 278, 465, 501, 537, 573, 609]
T_WINDOWS = [44, 80, 116, 152, 188, 224, 260, 483, 519, 591, 627]
T_BAL_GAPS = [(210, 221), (468, 477), (522, 549)]
T_IVY = [(150, 141, 14, 3), (156, 141, 9, 2), (334, 142, 12, 3), (339, 142, 7, 2), (401, 142, 15, 3),
         (406, 142, 9, 2), (66, 141, 11, 2), (612, 141, 8, 2)]
DECK_SHRUBS = [(120, 135, 6), (182, 134, 5), (268, 135, 4), (450, 134, 5), (600, 135, 7), (636, 133, 6)]
COLLAPSE_CONE = [(522, 133, 9, 6), (534, 136, 12, 7), (548, 137, 14, 7), (562, 138, 12, 6), (576, 139, 10, 5),
                 (588, 141, 8, 4)]
# --- lawn (world coordinates: X metres right of the axis, d metres from the camera)
TRAIL = ((0.0, 20.0), (0.0, 228.0), 2.4)
WALK_L = ((-60.0, 21.0), (-12.0, 228.0), 1.8)
WALK_R = ((60.0, 21.0), (12.0, 228.0), 1.8)
LAWN_SHRUBS = [(-30, 40, 2.2, "mg"), (-46, 70, 3.0, "mg"), (26, 52, 1.8, "mg"), (38, 95, 3.6, "mg"),
               (-16, 140, 3.0, "vg"), (52, 160, 5.0, "vg"), (-62, 120, 4.0, "vg"), (-8, 64, 1.3, "mg"),
               (12, 118, 2.0, "vg"), (-38, 190, 4.0, "vg"), (30, 205, 3.5, "vg"), (-20, 30, 1.4, "mg"),
               (18, 34, 1.6, "mg"), (44, 44, 2.0, "mg"), (-52, 52, 2.4, "mg"), (8, 88, 1.8, "mg"), (-30, 96, 2.6, "mg"),
               (60, 76, 3.0, "mg"), (-74, 90, 3.4, "mg"), (24, 150, 2.6, "vg"), (-46, 170, 3.2, "vg"),
               (70, 130, 4.0, "vg"), (-4, 180, 2.0, "vg"), (36, 26, 1.2, "mg"), (-40, 26, 1.3, "mg")]
LAWN_PATCHES = [(-24, 36, 5.0, 2.0), (30, 60, 7.0, 3.0), (-50, 84, 9.0, 4.0), (12, 110, 10.0, 5.0),
                (-14, 58, 4.0, 2.0), (48, 40, 5.0, 2.0)]                 # darker tall-grass swaths (X, d, half-w, half-d)
FALLEN_LOG = ((16.0, 42.0), (20.5, 46.0))
WALKER = (14.0, 70.0)
PATROL_TRAIL = [(6.5, 21.0), (9.0, 34.0), (12.0, 52.0), (14.0, 70.0), (19.0, 110.0), (26.0, 160.0)]   # X m, d m
OFFSCREEN_SHADE = [  # dappled canopy shadows of trees south of the frame (behind the camera), falling north
    [(-20, 352, 70, 16), (40, 362, 60, 12), (96, 366, 40, 9)],
    [(560, 360, 60, 12), (630, 350, 50, 18), (600, 340, 30, 8)]]
# --- grounds trees: (x, d m, height m, crown radius m, kind)
GROUNDS_TREES = [(92, 70, 14.0, 5.6, "mid"), (150, 112, 14.0, 4.6, "far"), (622, 66, 13.0, 5.2, "mid"),
                 (212, 205, 12.0, 4.0, "far"), (530, 196, 11.0, 3.8, "far"), (600, 150, 12.0, 4.2, "far")]
# Olmsted grounds groves beyond both terrace ends (~240 m, 2.3 px/m): hand-placed canopy masses (x, y, r)
FAR_MASSES = [
    [(-8, 132, 22), (22, 124, 20), (50, 130, 18), (78, 126, 17), (104, 134, 15), (130, 140, 12), (152, 146, 9),
     (10, 150, 18), (44, 152, 16), (80, 150, 14), (116, 154, 11), (140, 158, 8)],
    [(598, 128, 14), (620, 120, 18), (642, 126, 20), (586, 144, 10), (608, 146, 14), (634, 148, 16)],
]
TERRACE_FOOT_SHRUBS = [(8, 6), (30, 5), (64, 7), (98, 5), (160, 6), (196, 4), (236, 7), (266, 4), (286, 5),
                       (456, 5), (482, 7), (508, 4), (546, 6), (592, 7), (618, 5), (638, 6)]
SNAG = (586, 96, 14.0)
# --- Olmsted seat wall (a curved granite wall with a marble coping, d ~ 20 m)
ARC = (372.0, 420.0, 600.0, 214.0)               # centre x, centre y, rx, ry: coping top row = cy - ry*sqrt(...)
STEPS = (312, 432)
CHEEKS = ((296, 311), (433, 448))
CHEEK_TOP = 192
STEP_ROWS = [(203, 205, "landing"), (206, 207, "riser"), (208, 210, "tread"), (211, 212, "riser"),
             (213, 215, "tread"), (216, 217, "riser"), (218, 220, "tread"), (221, 222, "riser")]
PLAZA_TOP_AT_STEPS = 223
COLLAPSE = [(486, 0), (492, 5), (498, 9), (506, 14), (512, 17), (580, 17), (588, 11), (596, 6), (604, 0)]
WALL_SHRUBS = [  # behind the coping on the lawn side: (x, crown y above the coping, r, ramp)
    (8, 30, 22, "near"), (40, 22, 16, "near"), (70, 30, 20, "near"), (104, 18, 13, "near"), (132, 26, 17, "near"),
    (164, 16, 12, "near"), (190, 22, 14, "near"), (220, 12, 10, "near"), (246, 18, 12, "near"), (276, 10, 8, "near"),
    (458, 12, 9, "near"), (476, 18, 11, "near"), (612, 22, 15, "near"), (636, 30, 18, "near")]
YOUNG_TREE = (118, 58, 20)                       # sapling behind the wall: x, crown centre above coping, r
# --- plaza (walkable plane)
FORECOURT = (372.0, 222.0, 172.0, 62.0)
AXIS_WALK = (346, 397)
WEST_PATH = ([(-4, 318), (36, 313), (84, 305), (130, 302), (176, 305), (222, 299), (262, 287), (296, 275)], 10.0)
EAST_PATH = ([(644, 311), (604, 316), (566, 318), (536, 316), (508, 305), (486, 291), (462, 277), (446, 263)], 10.0)
WEST_SLABS = [(22, 312, 12), (40, 309, 10), (58, 306, 13), (78, 303, 9), (96, 301, 12)]
MISSING = [(268, 247, 9, 4), (432, 262, 12, 5), (470, 238, 7, 3), (330, 272, 6, 3), (372, 318, 7, 3)]
TURF_INVADE = [(222, 250, 24, 9), (512, 252, 26, 10), (392, 334, 14, 6), (300, 312, 20, 6), (600, 306, 18, 5),
               (364, 300, 10, 4), (384, 352, 12, 5), (352, 324, 6, 3),
               (120, 318, 16, 5), (446, 290, 10, 4), (352, 248, 8, 3)]
CRACKS = [[(352, 288), (358, 300), (355, 312), (361, 326)], [(396, 296), (388, 306), (392, 318)],
          [(250, 236), (262, 244), (270, 251)], [(450, 244), (462, 252), (470, 262), (486, 266)],
          [(416, 228), (424, 236), (438, 240)], [(330, 232), (322, 240), (316, 252)]]
ROOT_HEAVE = [(18, 300, 110, 322)]
PATROL_PRINTS = [(636, 336), (618, 330), (600, 326), (582, 322), (564, 318), (548, 316), (512, 300), (498, 292),
                 (484, 282), (470, 272), (458, 262), (448, 252), (440, 244), (432, 236), (424, 230)]
# --- props (bases are contact rows)
ELM = (28, 282)
LANTERN_L = (303, CHEEK_TOP)
LANTERN_R_STUB = (440, CHEEK_TOP)
LANTERN_HEAD_FALLEN = (466, 248)
TRIPOD = (238, 276)
MAST = (196, 256)
CRATE = (150, 286)
PANEL = (98, 272)
CASES = [(206, 296, "k"), (222, 297, "o")]
STAKES = [(118, 238), (152, 234), (186, 231), (220, 229), (254, 228), (284, 227)]
BEACON = (528, 306)
AILANTHUS = (572, 236)
YSORT_PIVOTS = {"survey-mast-ysort": MAST[1], "survey-tripod-ysort": TRIPOD[1], "beacon-ysort": BEACON[1],
                "elm-ysort": ELM[1]}
RUBBLE = [  # (x, base row, w, h, kind, tone): hand-placed on the mound, back (top) to toe, plus scattered chips
    (518, 228, 16, 11, "ashlar", "gr4"), (536, 226, 20, 12, "ashlar", "gr3"), (556, 230, 14, 10, "coping", "m4"),
    (502, 242, 14, 9, "ashlar", "gr3"), (526, 244, 18, 12, "cut", "gr4"), (548, 242, 16, 10, "ashlar", "gr2"),
    (568, 240, 14, 9, "ashlar", "gr3"), (584, 246, 12, 8, "coping", "m5"),
    (492, 256, 12, 7, "ashlar", "gr2"), (510, 258, 18, 10, "ashlar", "gr3"), (534, 260, 22, 11, "ashlar", "gr4"),
    (560, 258, 16, 9, "ashlar", "gr3"), (580, 260, 14, 8, "ashlar", "gr2"), (598, 258, 10, 6, "chip", "gr3"),
    (486, 268, 8, 4, "chip", "gr3"), (504, 270, 12, 6, "coping", "m4"), (530, 272, 10, 5, "chip", "gr2"),
    (548, 274, 18, 8, "ashlar", "gr3"), (574, 272, 12, 6, "coping", "m5"), (594, 268, 8, 4, "chip", "gr2"),
    (612, 270, 7, 4, "chip", "gr3"),
    (468, 266, 6, 3, "chip", "gr3"), (476, 277, 5, 3, "chip", "gr2"), (620, 277, 6, 3, "chip", "gr3"),
    (604, 281, 8, 4, "chip", "gr2"), (520, 283, 6, 3, "chip", "gr3"),
]
LYING_BALUSTERS = [(514, 251), (566, 266), (590, 253)]
HEAP = [(482, 262), (488, 252), (494, 244), (500, 238), (506, 231), (514, 226), (522, 219), (530, 216), (538, 218),
        (546, 214), (556, 217), (566, 222), (576, 226), (586, 232), (594, 240), (602, 248), (608, 256), (612, 264),
        (600, 268), (586, 270), (570, 272), (552, 274), (534, 273), (516, 271), (500, 268), (488, 266)]
FALLEN_LAMP = ((420, 347), (520, 329))          # Olmsted bronze lamp standard lying in the meadow: base -> head
MEADOW_PATCHES = [(206, 340, 46, 10), (548, 348, 34, 8), (84, 282, 22, 7), (300, 352, 30, 6), (616, 272, 20, 8),
                  (470, 302, 18, 5), (130, 258, 20, 6), (262, 316, 18, 5), (448, 330, 16, 5), (24, 340, 16, 6),
                  (600, 300, 14, 4)]
GROUND_SHRUBS = [(252, 344, 9), (494, 352, 8), (112, 336, 7), (610, 288, 8)]   # low shrubs on the turf (base, r)
FALLEN_LIMB = ((86, 330), (150, 342))
# --- foreground (drawn over actors)
FG_BALUSTRADE = (0, 359)
FG_BLOCK = (584, 359)
FG_FOOTPRINTS = {"fg_balustrade": (0, 340, 104, 359), "fg_block": (578, 333, 639, 359)}

PINS = {"spawn_south": (372, 350), "axis_mid": (372, 300), "vista_point": (372, 236), "steps_mid": (372, 214),
        "exit_north_steps": (372, 207), "survey_terminal": (164, 300), "tripod_behind": (238, 264),
        "tripod_front": (238, 290), "mast_behind": (196, 246), "elm_behind": (52, 272), "elm_front": (52, 296),
        "beacon_behind": (528, 294), "beacon_front": (528, 320), "collapse_inspect": (546, 288),
        "lantern_inspect": (466, 262), "olmsted_plaque": (304, 236), "exit_west": (3, 316), "exit_east": (636, 312),
        "exit_south": (372, 357)}
EXITS = {"exit_north_steps": {"rect": [330, 203, 414, 208], "to": "Olmsted lower west terrace (next room, north)"},
         "exit_west": {"rect": [0, 306, 9, 326], "to": "First Street walk toward Peace Circle (west)"},
         "exit_east": {"rect": [630, 300, 639, 322], "to": "Maryland Avenue walk toward Garfield Circle (east)"},
         "exit_south": {"rect": [344, 355, 400, 359], "to": "Union Square / Reflecting Pool (south)"}}
INTERACTIONS = {
    "vista_point": {"pin": "vista_point", "rect": [352, 228, 392, 244], "kind": "look",
                    "text_key": "wdc_cw_vista_west_front"},
    "survey_terminal": {"pin": "survey_terminal", "rect": [150, 292, 180, 306], "kind": "use",
                        "text_key": "wdc_cw_survey_terminal_scan_log"},
    "survey_scanner": {"pin": "tripod_front", "rect": [226, 282, 250, 296], "kind": "inspect",
                       "text_key": "wdc_cw_lidar_aimed_at_dome"},
    "patrol_beacon": {"pin": "beacon_front", "rect": [516, 312, 540, 326], "kind": "inspect",
                      "text_key": "wdc_cw_patrol_waypoint_active"},
    "collapse_cut_block": {"pin": "collapse_inspect", "rect": [532, 280, 560, 294], "kind": "inspect",
                           "text_key": "wdc_cw_laser_cut_granite"},
    "fallen_lantern": {"pin": "lantern_inspect", "rect": [456, 256, 478, 268], "kind": "inspect",
                       "text_key": "wdc_cw_olmsted_lantern_fallen"},
    "olmsted_plaque": {"pin": "olmsted_plaque", "rect": [294, 230, 314, 242], "kind": "read",
                       "text_key": "wdc_cw_olmsted_plaque"},
}
YSORT_CASES = [("tripod_behind", "survey-tripod-ysort", True), ("tripod_front", "survey-tripod-ysort", False),
               ("mast_behind", "survey-mast-ysort", True), ("beacon_behind", "beacon-ysort", True),
               ("beacon_front", "beacon-ysort", False), ("elm_behind", "elm-ysort", True),
               ("elm_front", "elm-ysort", False)]
ROUTE = ["spawn_south", "axis_mid", (372, 260), "vista_point", "steps_mid", "exit_north_steps", "steps_mid",
         "vista_point", (330, 246), "olmsted_plaque", (290, 250), (262, 264), "tripod_behind", (214, 266),
         (214, 246), "mast_behind", (150, 246), (150, 262), (120, 284), "survey_terminal", (200, 304),
         "tripod_front", (290, 290), (240, 306), (120, 304), "elm_front", "elm_behind", (64, 288), (24, 306),
         "exit_west", (60, 312), (200, 304), (300, 296), "axis_mid", (440, 296), (480, 300), "beacon_front",
         (548, 318), (552, 300), "beacon_behind", (500, 290), "collapse_inspect", (500, 290), "lantern_inspect", (440, 268), (440, 300), (600, 312), "exit_east", (560, 324), (420, 330),
         "spawn_south", "exit_south"]
COLLISION_PROBES = {  # points that must be blocked (not walkable) in the exported mask
    "seat_wall_face": (180, 224), "lawn_beyond_wall": (120, 200), "left_cheek": (304, 214),
    "right_cheek": (440, 214), "rubble_cone": (540, 254), "rubble_front_block": (550, 266),
    "elm_trunk": (28, 280), "survey_crate": (164, 284), "solar_panel": (110, 270), "tripod_feet": (238, 275),
    "mast_foot": (196, 255), "beacon_base": (528, 305), "fallen_lantern_head": (466, 247),
    "fg_balustrade": (30, 352), "fg_block": (610, 352), "terrace_backdrop": (372, 150), "dome": (372, 60),
}
CAPTURES = {"entry": "spawn_south", "vista": "vista_point", "survey-behind": "tripod_behind",
            "beacon-front": "beacon_front"}

# ============================================================================ helpers
YY, XX = np.mgrid[0:H, 0:W]
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16 + 1 / 32
BAY = BAYER[YY % 4, XX % 4]


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
    """Deterministic hash in [0, 1) (texture-level variation only: tones, leaf jitter; placement is in tables)."""
    return int.from_bytes(hashlib.sha256(repr(key).encode()).digest()[:4], "little") / 2 ** 32


_VN = {}


def vnoise(key, cell):
    """Smooth value noise in screen space (smoothstep-bilinear between hashed lattice values every `cell` px)."""
    if (key, cell) not in _VN:
        gw, gh = W // cell + 2, H // cell + 2
        seed = int.from_bytes(hashlib.sha256(repr((key, cell)).encode()).digest()[:8], "little")
        g = np.random.default_rng(seed).random((gh, gw)).astype(np.float32)
        fx, fy = (XX + 0.5) / cell, (YY + 0.5) / cell
        ix, iy = fx.astype(np.int32), fy.astype(np.int32)
        tx, ty = fx - ix, fy - iy
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        top = g[iy, ix] * (1 - tx) + g[iy, ix + 1] * tx
        bot = g[iy + 1, ix] * (1 - tx) + g[iy + 1, ix + 1] * tx
        _VN[(key, cell)] = (top * (1 - ty) + bot * ty).astype(np.float32)
    return _VN[(key, cell)]


_LAT = {}


def wnoise(key, u, v):
    """Smooth value noise at arbitrary world coordinates (wraps every 256 cells)."""
    if key not in _LAT:
        seed = int.from_bytes(hashlib.sha256(repr(key).encode()).digest()[:8], "little")
        _LAT[key] = np.random.default_rng(seed).random((256, 256)).astype(np.float32)
    g = _LAT[key]
    iu, iv = np.floor(u).astype(np.int64), np.floor(v).astype(np.int64)
    tu, tv = u - iu, v - iv
    tu, tv = tu * tu * (3 - 2 * tu), tv * tv * (3 - 2 * tv)
    a = g[iv % 256, iu % 256]; b = g[iv % 256, (iu + 1) % 256]
    c = g[(iv + 1) % 256, iu % 256]; d = g[(iv + 1) % 256, (iu + 1) % 256]
    return (a * (1 - tu) + b * tu) * (1 - tv) + (c * (1 - tu) + d * tu) * tv


def C(c):
    return I[c] if isinstance(c, str) else int(c)


def px(L, x, y, c, reg=None):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H:
        L[y, x] = C(c)
        if reg is not None:
            reg[y, x] = True


def rect(L, x0, y0, x1, y1, c, reg=None):
    x0, x1 = max(0, int(x0)), min(W - 1, int(x1))
    y0, y1 = max(0, int(y0)), min(H - 1, int(y1))
    if x0 <= x1 and y0 <= y1:
        L[y0:y1 + 1, x0:x1 + 1] = C(c)
        if reg is not None:
            reg[y0:y1 + 1, x0:x1 + 1] = True


def line(L, x0, y0, x1, y1, c, reg=None):
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for k in range(n):
        t = k / max(1, n - 1)
        px(L, round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), c, reg)


def stamp(L, x, y, rows, cmap, reg=None):
    """Paint a hand-authored sprite (top-left at x, y). '.' and ' ' are transparent; other chars map through cmap."""
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


def polyline_mask(pts, hw):
    m = np.zeros((H, W), bool)
    for p, q in zip(pts, pts[1:]):
        m |= seg(p, q, hw)
    return m


def dilate(m, r=1):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


def shift(ramp, idx, d):
    if idx in ramp:
        return ramp[max(0, min(len(ramp) - 1, ramp.index(idx) + d))]
    return idx


def tone(ramp, v, cuts):
    k = 0
    while k < len(cuts) and v >= cuts[k]:
        k += 1
    return ramp[k]


def quantize(ramp, v, cuts):
    out = np.full(v.shape, ramp[0], np.int16)
    for k, c in enumerate(cuts):
        out[v >= c] = ramp[k + 1]
    return out


def bezier2(p0, p1, p2, n=400):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * np.array(p0) + 2 * (1 - t) * t * np.array(p1) + t * t * np.array(p2)


# ============================================================================ foliage (leaf-cluster crowns)
LIGHT = np.array([-0.52, -0.46, 0.72])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
STD_LOBES = [(0.0, -0.52, 0.50), (-0.48, -0.30, 0.46), (0.48, -0.28, 0.46), (-0.66, 0.16, 0.40),
             (0.64, 0.18, 0.40), (-0.24, -0.02, 0.52), (0.26, 0.00, 0.52), (-0.36, 0.46, 0.42), (0.36, 0.46, 0.42),
             (0.0, 0.58, 0.40)]


def leaf_clump_shift(X, Y, union, key, size):
    """Leaf clumps: each texel belongs to its nearest jittered clump centre (Voronoi), the clump's upper-left part is
    lifted one tone and its lower-right rim dropped one tone, so a canopy reads as many small leaf clusters."""
    sx, sy = size
    best = np.full(X.shape, 1e9, np.float32)
    uu = np.zeros(X.shape, np.float32); vv = np.zeros(X.shape, np.float32)
    ci0, cj0 = np.floor(X / sx).astype(np.int64), np.floor(Y / sy).astype(np.int64)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            ci, cj = ci0 + di, cj0 + dj
            jx = wnoise((key, "cjx"), ci * 0.73 + 0.31, cj * 0.71 + 0.17)
            jy = wnoise((key, "cjy"), ci * 0.69 + 0.11, cj * 0.77 + 0.43)
            cx = (ci + 0.2 + 0.6 * jx) * sx
            cy = (cj + 0.2 + 0.6 * jy) * sy
            u, v = (X - cx) / sx, (Y - cy) / sy
            d = u * u + v * v
            upd = d < best
            best = np.where(upd, d, best); uu = np.where(upd, u, uu); vv = np.where(upd, v, vv)
    up = union & (uu + vv < -0.30)
    dn = union & (uu * 0.5 + vv * 0.86 > 0.30)
    return up, dn


def crown_lobes(L, lobes, ramp, cuts, key, reg=None, squash=0.9, gain=1.0, ctr=None, leaf=3, outline=True,
                holes=(), clumps=None):
    """Leaf canopy from hand-placed lobes (x, y, r). The lobes are z-buffered spheres (lower lobes sit nearer the
    viewer): the front-most sphere's normal is lit by the front-left sun; a metaball sum of the lobes gives ambient
    occlusion in the hollows between clusters and toward the rim, so the crown reads as one mass of leaf clusters;
    value noise at `leaf` px and optional Voronoi `clumps` add leaf texture; creases darken where a sphere passes
    behind its neighbour; only the outer shade side is outlined; `holes` (x, y, rx, ry) open sky gaps."""
    if not lobes:
        return np.zeros((H, W), bool)
    xs = [l[0] for l in lobes]; ys = [l[1] for l in lobes]
    cx, cy = ctr if ctr else (float(np.mean(xs)), float(np.mean(ys)))
    rr = max(1.0, max(math.hypot(x - cx, y - cy) + r for x, y, r in lobes))
    x0 = max(0, int(min(x - r for x, _, r in lobes)) - 3); x1 = min(W, int(max(x + r for x, _, r in lobes)) + 4)
    y0 = max(0, int(min(y - r * squash for _, y, r in lobes)) - 3)
    y1 = min(H, int(max(y + r * squash for _, y, r in lobes)) + 4)
    if x0 >= x1 or y0 >= y1:
        return np.zeros((H, W), bool)
    X, Y = XX[y0:y1, x0:x1] + 0.5, YY[y0:y1, x0:x1] + 0.5
    nz_field = vnoise((key, "leaf"), leaf)[y0:y1, x0:x1]
    fine = vnoise((key, "fine"), 2)[y0:y1, x0:x1]
    edge_n = vnoise((key, "edge"), 3)[y0:y1, x0:x1]
    zb = np.full(X.shape, -1e9, np.float32)
    lid = np.full(X.shape, -1, np.int32)
    nxs = np.zeros(X.shape, np.float32); nys = np.zeros(X.shape, np.float32); nzs = np.zeros(X.shape, np.float32)
    Fm = np.zeros(X.shape, np.float32)
    for k, (lx, ly, lr) in enumerate(lobes):
        nx, ny = (X - lx) / lr, (Y - ly) / (lr * squash)
        d2 = nx * nx + ny * ny
        Fm += np.clip(1 - d2, 0, None) ** 2
        m = d2 <= (1.0 + 0.34 * (edge_n - 0.5))
        if not m.any():
            continue
        nzv = np.sqrt(np.clip(1 - d2, 0, 1))
        z = nzv * lr + (ly - cy) * 0.55
        upd = m & (z > zb)
        zb[upd] = z[upd]; lid[upd] = k
        nxs[upd] = nx[upd]; nys[upd] = ny[upd]; nzs[upd] = nzv[upd]
    union = lid >= 0
    for (hx, hy, hrx, hry) in holes:
        union &= ((X - hx) / hrx) ** 2 + ((Y - hy) / hry) ** 2 > 1.0 + 0.6 * (edge_n - 0.5)
    inten = nxs * LIGHT[0] + nys * LIGHT[1] + nzs * LIGHT[2]
    glob = -0.30 * ((X - cx) / rr) - 0.42 * ((Y - cy) / rr)
    ao = np.clip(Fm / 0.9, 0, 1)
    v = (inten * 0.66 + glob * 0.60 + (ao - 0.55) * 0.42 + (nz_field - 0.5) * 0.60 + (fine - 0.5) * 0.16) * gain
    idx = quantize(ramp, v, cuts)
    crease = np.zeros(X.shape, bool)
    crease[:-1] |= union[:-1] & union[1:] & (lid[:-1] != lid[1:]) & (zb[:-1] < zb[1:] - 1.5)
    crease[:, :-1] |= union[:, :-1] & union[:, 1:] & (lid[:, :-1] != lid[:, 1:]) & (zb[:, :-1] < zb[:, 1:] - 1.5)
    crease &= fine > 0.35
    rim = union & (nxs * 0.5 + nys * 0.86 > 0.90)
    for i, n in enumerate(ramp):
        idx[(crease | rim) & (idx == n)] = ramp[max(0, i - 1)]
    if clumps:
        up, dn = leaf_clump_shift(X, Y, union, key, clumps)
        for i, n in reversed(list(enumerate(ramp))):
            idx[up & (idx == n) & (fine > 0.3)] = ramp[min(len(ramp) - 1, i + 1)]
        for i, n in enumerate(ramp):
            idx[dn & ~up & (idx == n)] = ramp[max(0, i - 1)]
    sub = np.where(union, idx, -1).astype(np.int16)
    if outline:
        edge = np.zeros_like(union)
        edge[:-1] |= union[:-1] & ~union[1:]
        edge[:, :-1] |= union[:, :-1] & ~union[:, 1:]
        sub[edge] = ramp[0]
    pocket = union & (nz_field < 0.13) & (Y > cy - 0.1 * rr)
    sub[pocket] = ramp[0]
    tgt = L[y0:y1, x0:x1]
    tgt[union] = sub[union]
    full = np.zeros((H, W), bool)
    full[y0:y1, x0:x1] = union
    if reg is not None:
        reg |= full
    return full


def cluster_lobes(lobes, key):
    """Split each big lobe into a cluster of five smaller ones (a core plus four jittered satellites), so a near
    crown reads as clusters of leaf clusters instead of a few large balls."""
    out = []
    for i, (x, y, r) in enumerate(lobes):
        out.append((x, y, r * 0.66))
        for k, (ox, oy) in enumerate(((-0.46, -0.30), (0.44, -0.34), (-0.40, 0.36), (0.42, 0.32))):
            jx, jy = (hval(key, i, k, "x") - 0.5) * 0.24, (hval(key, i, k, "y") - 0.5) * 0.24
            out.append((x + (ox + jx) * r, y + (oy + jy) * r, r * (0.46 + hval(key, i, k, "s") * 0.12)))
    return out


TREE_TEMPLATE = [(0.0, -0.56, 0.46), (-0.50, -0.38, 0.44), (0.48, -0.34, 0.44), (-0.78, 0.04, 0.38),
                 (0.76, 0.08, 0.38), (-0.30, -0.06, 0.50), (0.30, -0.02, 0.50), (0.0, 0.28, 0.48),
                 (-0.52, 0.40, 0.40), (0.54, 0.40, 0.40), (-0.12, -0.30, 0.42), (0.18, 0.56, 0.34),
                 (-0.30, 0.60, 0.30)]


def crown(L, cx, cy, r, ramp, cuts, key, reg=None, squash=0.9, gain=1.0, leaf=3, holes=(), clumps="auto"):
    """Generic broadleaf crown: 13 template lobes (two dropped per tree, all jittered per tree) z-buffered."""
    lobes = []
    drop = {int(hval(key, "drop", q) * len(TREE_TEMPLATE)) for q in range(2)} - {5, 6, 7}
    for k, (ox, oy, s) in enumerate(TREE_TEMPLATE):
        if k in drop:
            continue
        jx, jy = (hval(key, k, "x") - 0.5) * 0.22, (hval(key, k, "y") - 0.5) * 0.20
        js = 1 + (hval(key, k, "s") - 0.5) * 0.26
        lobes.append((cx + (ox + jx) * r, cy + (oy + jy) * r * squash, s * js * r))
    if clumps == "auto":
        clumps = None
    if r >= 22:
        lobes = cluster_lobes(lobes, key)
    return crown_lobes(L, lobes, ramp, cuts, key, reg, squash, gain, ctr=(cx, cy), leaf=leaf, holes=holes,
                       clumps=clumps)


MID_CUTS = (-0.24, 0.10, 0.40, 0.70)
VG_CUTS = (-0.20, 0.10, 0.36, 0.62)
NEAR_CUTS = (-0.42, -0.14, 0.12, 0.36, 0.60, 0.84)


# ============================================================================ 1-2 sky, clouds
SKY_BANDS = [(0, "sk0"), (18, "sk1"), (38, "sk2"), (60, "sk3"), (84, "sk4"), (108, "sk5"), (130, "sk6"),
             (150, "sk7")]
CLOUDS = [  # hand-placed lobes (cx, cy, rx, ry); each list is one cloud
    [(498, 44, 26, 5), (528, 40, 22, 6), (560, 45, 30, 5), (600, 41, 26, 6), (634, 46, 22, 4)],
    [(574, 96, 10, 4), (590, 91, 14, 7), (606, 87, 12, 8), (622, 92, 16, 6), (638, 96, 12, 4)],
    [(214, 31, 16, 3), (244, 27, 30, 4), (278, 24, 18, 4), (300, 28, 12, 2)],
    [(236, 117, 30, 3), (270, 120, 24, 2), (300, 118, 14, 2)],
    [(458, 124, 30, 3), (494, 121, 22, 3), (520, 125, 16, 2)],
    [(438, 64, 18, 3), (462, 61, 14, 3)],
]


def paint_sky():
    L = new()
    bands = SKY_BANDS + [(H, SKY_BANDS[-1][1])]
    for (y0, c), (y1, c2) in zip(bands, bands[1:]):
        for y in range(y0, min(y1, H)):
            row = np.full(W, I[c], np.int16)
            to_next = y1 - y
            if c2 != c and to_next <= 3:
                frac = (4 - to_next) / 4.0                      # 0.25, 0.5, 0.75 ordered dither into next band
                row[BAY[y] < frac * 0.999] = I[c2]
            L[y] = row
    return L


def paint_clouds():
    L = new()
    for ci, lobes in enumerate(CLOUDS):
        for (cx, cy, rx, ry) in sorted(lobes, key=lambda t: t[1]):
            n = vnoise(("cloud", ci), 3)
            m = (((XX + 0.5 - cx) / rx) ** 2 + ((YY + 0.5 - cy) / ry) ** 2) <= (1.0 + 0.35 * (n - 0.5))
            ny = (YY + 0.5 - cy) / ry
            nx = (XX + 0.5 - cx) / rx
            v = -ny * 0.8 - nx * 0.25 + (n - 0.5) * 0.4
            t = np.where(v > 0.45, I["cl0"], np.where(v > -0.15, I["cl1"], np.where(v > -0.6, I["cl2"], I["cl3"])))
            L[m] = t[m]
    return L


# ============================================================================ 3 dome
def cyl_v(u):
    u = np.clip(u, -1, 1)
    return 0.62 * np.sqrt(1 - u * u) - 0.42 * u


DOME_CUTS = (-0.10, 0.08, 0.24, 0.38, 0.50, 0.60)


def dome_band(L, y0, y1, hw, d=0, dith=0.05, key="b"):
    for y in range(y0, y1 + 1):
        xs = np.arange(int(math.ceil(CAPX - hw - 0.5)), int(math.floor(CAPX + hw - 0.5)) + 1)
        u = (xs + 0.5 - CAPX) / hw
        v = cyl_v(u) + (BAY[y, xs] - 0.5) * dith
        idx = quantize(DOME, v, DOME_CUTS)
        if d:
            idx = np.array([shift(DOME, int(c), d) for c in idx], np.int16)
        L[y, xs] = idx


def azimuth_cols(R, step_deg, offset_deg, min_cos):
    """x positions (float) of features evenly spaced in azimuth around a cylinder of radius R, front half only."""
    out = []
    a = -90 + offset_deg
    while a < 90:
        if math.cos(math.radians(a)) >= min_cos:
            out.append((a, CAPX + R * math.sin(math.radians(a))))
        a += step_deg
    return out


def statue(L):
    rows = ["..ab..",
            "..AB..",
            ".aABb.",
            ".AABb.",
            "..ABb.",
            ".aABBb",
            ".AABBb",
            "aAABBb",
            "cccccc"]
    stamp(L, 369, STATUE_TOP, rows, {"a": "br0", "A": "br1", "B": "br0", "b": "br0", "c": "dm2"})
    px(L, 370, STATUE_TOP + 3, "dm3")                 # sunlit shoulder catch-light


def paint_dome():
    L = new()
    statue(L)
    # lantern: cap dome, cornice, tholos colonnade, base ring
    for y, hw in ((15, 2), (16, 3), (17, 4)):
        dome_band(L, y, y, hw, d=1, dith=0.0)
    dome_band(L, 18, 18, 5, d=1, dith=0.0)
    for y in range(19, 27):
        dome_band(L, y, y, 6, d=-3, dith=0.0)
    for x in (366, 368, 370, 373, 375, 377):
        rect(L, x, 19, x, 26, "dm5" if x < 371 else "dm4")
    rect(L, 371, 20, 372, 25, "dw0")
    for y, hw, d in ((27, 9, 2), (28, 9, 1), (29, 10, 0), (30, 10, -1)):
        dome_band(L, y, y, hw, d=d, dith=0.0)
    # shell: ellipsoid lit from the front-left, cast-iron ribs, one tier of windows, the south breach
    lv = np.array([-0.55, 0.35, 0.76]); lv /= np.linalg.norm(lv)
    for y in range(SHELL[0], SHELL[1] + 1):
        Yh = SHELL_BASE - (y + 0.5)
        hw = SHELL_A * math.sqrt(max(0.0, 1 - (Yh / SHELL_B) ** 2))
        xs = np.arange(int(math.ceil(CAPX - hw - 0.5)), int(math.floor(CAPX + hw - 0.5)) + 1)
        X = xs + 0.5 - CAPX
        xh, yh = X / SHELL_A, Yh / SHELL_B
        zh = np.sqrt(np.clip(1 - xh * xh - yh * yh, 0, 1))
        n = np.stack([xh / SHELL_A, np.full_like(xh, yh / SHELL_B), zh / SHELL_A])
        n /= np.linalg.norm(n, axis=0)
        v = lv[0] * n[0] + lv[1] * n[1] + lv[2] * n[2]
        v = (v - 0.55) * 1.35 + (BAY[y, xs] - 0.5) * 0.06
        idx = quantize(DOME, v, (-0.55, -0.32, -0.12, 0.04, 0.17, 0.28))
        phi = np.degrees(np.arcsin(np.clip(X / max(hw, 1e-3), -1, 1)))
        cosp = np.cos(np.radians(phi))
        frac = ((phi + 5.0) / 10.0) % 1.0
        dpx = np.minimum(frac, 1 - frac) * math.radians(10.0) * hw * cosp
        rib = (dpx < 0.5) & (cosp > 0.42) & (Yh > 2)
        idx = np.where(rib, np.array([shift(DOME, int(c), -1) for c in idx]), idx)
        if y in (50, 51):
            wf = ((phi / 10.0) % 1.0)
            win = (np.abs(wf - 0.5) * math.radians(10.0) * hw * cosp < 0.5) & (cosp > 0.5)
            idx = np.where(win, I["dw0"], idx)
        if y == 41:
            wf = ((phi / 20.0) % 1.0)
            win = (np.abs(wf - 0.5) * math.radians(20.0) * hw * cosp < 0.5) & (cosp > 0.55)
            idx = np.where(win, I["dw1"], idx)
        if y == SHELL[1]:
            idx = np.array([shift(DOME, int(c), 1) for c in idx])
        L[y, xs] = idx
    for y, (a, b) in BREACH.items():
        for X in range(a, b + 1):
            px(L, math.floor(CAPX + X), y, "dw0")
        px(L, math.floor(CAPX + a) - 1, y, "dm5" if y < 42 else "dm3")
    for X, y0, y1 in BREACH_RIBS:
        rect(L, math.floor(CAPX + X), y0, math.floor(CAPX + X), y1, "dm2")
    for X, y0, y1, c in RUST:
        rect(L, math.floor(CAPX + X), y0, math.floor(CAPX + X), y1, c)
    # attic drum: cornice, wall with windows + pilasters, shadow line
    dome_band(L, ATTIC[0], ATTIC[0], DOME_HW["attic_cornice"], d=2, dith=0.0)
    dome_band(L, ATTIC[0] + 1, ATTIC[0] + 1, DOME_HW["attic_cornice"], d=-2, dith=0.0)
    dome_band(L, ATTIC[0] + 2, ATTIC[1] - 1, DOME_HW["attic"], d=0)
    for a, x in azimuth_cols(DOME_HW["attic"], 12, 6, 0.40):
        xi = math.floor(x)
        rect(L, xi, 62, xi, 65, "dw0")
        px(L, xi - 1, 62, "dm5" if a < 20 else "dm4")
    dome_band(L, ATTIC[1], ATTIC[1], DOME_HW["attic"], d=-3, dith=0.0)
    # peristyle balustrade + entablature
    dome_band(L, PERI_BAL[0], PERI_BAL[0], DOME_HW["peri_bal"], d=1, dith=0.0)
    for y in (PERI_BAL[1],):
        xs = np.arange(int(math.ceil(CAPX - 30 - 0.5)), int(math.floor(CAPX + 30 - 0.5)) + 1)
        for x in xs:
            px(L, x, y, "dm1" if x % 2 else "dm4")
    dome_band(L, 70, 70, DOME_HW["peri_ent"], d=2, dith=0.0)
    dome_band(L, 71, 72, DOME_HW["peri_ent"], d=0, dith=0.03)
    for x in range(int(CAPX - 32), int(CAPX + 32) + 1, 2):
        px(L, x, 72, "dm2")
    dome_band(L, 73, 73, DOME_HW["peri_ent"], d=-3, dith=0.0)
    # colonnade: dark wall with windows behind 36 columns (front half), three missing on the south side
    for y in range(PERI_COLS[0], PERI_COLS[1] + 1):
        dome_band(L, y, y, DOME_HW["peri_cols"], d=-4, dith=0.0)
    for a, x in azimuth_cols(DOME_HW["peri_cols"] - 3, 20, 10, 0.45):
        rect(L, math.floor(x), 78, math.floor(x), 85, "dw0")
    for a, x in azimuth_cols(DOME_HW["peri_cols"] - 1, 10, 5, 0.12):
        xi = math.floor(x)
        missing = any(abs(a - m) < 1 for m in PERI_MISSING)
        wide = math.cos(math.radians(a)) > 0.62
        lit = "dm6" if a < -20 else "dm5"
        if missing:
            if abs(a - 35) < 1:
                rect(L, xi, 86, xi + (1 if wide else 0), 89, "dm3")      # broken stump
            if abs(a - 45) < 1:
                rect(L, xi, 74, xi, 76, "dm3")                            # capital fragment still hanging
            continue
        rect(L, xi, PERI_COLS[0], xi, PERI_COLS[1], lit if wide else "dm4")
        if wide:
            rect(L, xi + 1, PERI_COLS[0], xi + 1, PERI_COLS[1], "dm3")
        rect(L, xi - (1 if wide else 0), PERI_COLS[0], xi + 1, PERI_COLS[0], "dm5")
    dome_band(L, 90, 90, DOME_HW["stylobate"], d=2, dith=0.0)
    dome_band(L, 91, 91, DOME_HW["stylobate"], d=0, dith=0.0)
    dome_band(L, 92, 92, DOME_HW["stylobate"], d=-2, dith=0.0)
    for x, c in ((390, "dm3"), (392, "dm2"), (395, "dm3")):          # fallen column drums on the stylobate
        px(L, x, 89, c)
    return L


# ============================================================================ 4 West Front
def section_at(x):
    xl = x if x <= 371 else 743 - x
    for name, x0, x1, roof in SECTIONS_L:
        if x0 <= xl <= x1:
            return name, x0, x1, roof
    return None


def window(L, x, y0, y1, state, cap=None):
    """2-px wide window with sill and head; `state` is the hand-assigned condition."""
    body = {"g": ("dw1", "dw0"), "d": ("dw0", "dw0"), "b": ("dw0", "dm1"), "o": ("ru0", "ru1"),
            "v": ("vg1", "vg2"), "s": ("dw0", "dw0")}[state]
    rect(L, x, y0, x, y1, body[0]); rect(L, x + 1, y0, x + 1, y1, body[1])
    if state == "g":
        px(L, x, y0 + 1, "dm3")                                         # sky reflection in the upper pane
    if state == "b":
        px(L, x + 1, y0 + (y1 - y0) // 2, "dm3")
    if state == "v":
        px(L, x, y0, "vg3"); px(L, x + 1, y1 + 1, "vg1")
    rect(L, x - 1, y1 + 1, x + 2, y1 + 1, "dm5")                        # sill
    if cap == "pediment":
        rect(L, x - 1, y0 - 2, x + 2, y0 - 2, "dm5"); rect(L, x, y0 - 3, x + 1, y0 - 3, "dm5")
        rect(L, x - 1, y0 - 1, x + 2, y0 - 1, "dm2")
    elif cap == "lintel":
        rect(L, x - 1, y0 - 1, x + 2, y0 - 1, "dm5")


def arch(L, x, y0, y1, w=3, c="dw0"):
    rect(L, x, y0 + 1, x + w - 1, y1, c)
    rect(L, x + 1 if w == 3 else x, y0, x + w - 2 if w == 3 else x + w - 1, y0, c)
    px(L, x - 1, y0, "dm5"); px(L, x + w, y0, "dm5")


def paint_west_front():
    L = new()
    half = new()
    # --- symmetric construction of the left half
    for name, x0, x1, roof in SECTIONS_L:
        r = roof
        rect(half, x0, r, x1, FACADE_BOTTOM, "dm4")
        rect(half, x0, r, x1, r, "dm5")                                  # balustrade rail
        for x in range(x0, x1 + 1):
            px(half, x, r + 1, "dm2" if x % 2 else "dm4")                # balusters
        rect(half, x0, r + 2, x1, r + 2, "dm4")
        rect(half, x0, r + 3, x1, r + 3, "dm6")                          # cornice lit edge
        rect(half, x0, r + 4, x1, r + 4, "dm2")                          # cornice shadow
        if name == "pavilion":
            rect(half, x0, 97, x1, 100, "dm4"); rect(half, x0, 98, x1, 98, "dm3")
            for x in range(x0, x1 + 1, 3):
                px(half, x, 99, "dm3")
            rect(half, x0 + 1, 101, x1, 121, "dm1")                      # shaded loggia wall behind the colonnade
            rect(half, x0 + 1, 101, x1, 102, "dw1")
            for x in range(x0 + 4, x1, 8):
                window(half, x, 106, 115, "d")
                rect(half, x, 103, x + 1, 103, "dw0")
            for x in PAV_COLS_L:
                rect(half, x, 101, x, 121, "dm6"); rect(half, x + 1, 101, x + 1, 121, "dm4")
                rect(half, x - 1, 101, x + 2, 101, "dm5"); rect(half, x - 1, 121, x + 2, 121, "dm5")
            rect(half, x0, 121, x1, 121, "dm5")
        elif name == "wing":
            rect(half, x0, r + 5, x1, r + 7, "dm4"); rect(half, x0, r + 6, x1, r + 6, "dm3")
            p0, p1 = WING_PORTICO_L
            rect(half, p0, r + 8, p1, 121, "dw1")
            for x in range(p0 + 3, p1 - 1, 7):
                window(half, x, 108, 116, "d")
            for x in WING_COLS_L:
                rect(half, x, r + 8, x, 121, "dm6"); rect(half, x + 1, r + 8, x + 1, 121, "dm4")
                rect(half, x - 1, r + 8, x + 2, r + 8, "dm5")
            for x in WING_BAYS_L:
                window(half, x, 108, 116, "g", cap="pediment")
                window(half, x, r + 6, r + 7, "d")
        elif name == "center":
            for x in CENTER_BAYS_L:
                window(half, x, 101, 103, "d")
                window(half, x, 110, 117, "g", cap="pediment" if (x // 6) % 2 else "lintel")
            rect(half, x0, 106, x1, 106, "dm3")
            for x in range(x0 + 2, x1, 6):
                rect(half, x + 3, 108, x + 3, 120, "dm5")                # pilasters between the bays
        elif name == "corridor":
            for x in CORRIDOR_BAYS_L:
                window(half, x, 110, 116, "g", cap="lintel")
        rect(half, x0, STRING, x1, STRING, "dm5"); rect(half, x0, STRING + 1, x1, STRING + 1, "dm2")
        # rusticated ground floor with an arcade
        for y in range(GROUND_FLOOR[0], GROUND_FLOOR[1] + 1, 3):
            rect(half, x0, y, x1, y, "dm3")
        for y0 in range(GROUND_FLOOR[0], GROUND_FLOOR[1], 3):
            off = 0 if (y0 // 3) % 2 else 3
            for x in range(x0 + off, x1 + 1, 6):
                px(half, x, y0 + 1, "dm3")
        pitch = 8 if name == "pavilion" else 6
        for x in range(x0 + 2, x1 - 2, pitch):
            arch(half, x, 129, 139, 3 if name == "pavilion" else 2)
        rect(half, x0, 139, x1, FACADE_BOTTOM, "dm2")
    # mirror to the right half
    for x in range(372, 576):
        half[:, x] = half[:, 743 - x]
    L[:] = half
    # --- asymmetric sunlight: projections lit on their left edge, cast shadow on a recessed neighbour's left edge
    names = []
    for x in range(168, 576):
        s = section_at(x)
        names.append(s[0] if s else None)
    for i in range(1, len(names)):
        a, b = names[i - 1], names[i]
        if a and b and a != b:
            x = 168 + i
            top = min(section_at(x - 1)[3], section_at(x)[3])
            if PROJECTION[b] > PROJECTION[a]:
                rect(L, x, section_at(x)[3] + 3, x, 121, "dm6")
            else:
                for y in range(section_at(x)[3] + 3, FACADE_BOTTOM + 1):
                    for dx in (0, 1):
                        if L[y, x + dx] in (I["dm4"], I["dm5"], I["dm6"]):
                            L[y, x + dx] = I["dm2"] if dx == 0 else I["dm3"]
    rect(L, 167, 98, 167, FACADE_BOTTOM, "dm6")                          # Senate wing end, lit
    # --- hand-assigned bay states (both halves differ)
    for side, bays in (("L", CENTER_BAYS_L), ("R", [743 - x - 1 for x in CENTER_BAYS_L])):
        for x, st in zip(bays, STATE_CENTER[side]):
            if st != "g":
                window(L, x, 110, 117, st)
    for side, bays in (("L", CORRIDOR_BAYS_L), ("R", [743 - x - 1 for x in CORRIDOR_BAYS_L])):
        for x, st in zip(bays, STATE_CORR[side]):
            if st != "g":
                window(L, x, 110, 116, st)
    for side, bays in (("L", WING_BAYS_L), ("R", [743 - x - 1 for x in WING_BAYS_L])):
        for x, st in zip(bays, STATE_WING[side]):
            if st != "g":
                window(L, x, 108, 116, st)
    pav_r = sorted([743 - x - 1 for x in PAV_COLS_L])
    for i in PAV_COL_MISSING_R:
        x = pav_r[i]
        rect(L, x, 102, x + 1, 120, "dw1")
        rect(L, x, 117, x + 1, 120, "dm3"); px(L, x, 116, "dm3")       # stump
        rect(L, x - 1, 101, x + 2, 101, "dm3")
    wing_r = sorted([743 - x - 1 for x in WING_COLS_L])
    for i in WING_COL_TOPPLED_R:
        x = wing_r[i]
        rect(L, x, 107, x + 1, 117, "dw1")
        rect(L, x - 3, 119, x + 4, 120, "dm3"); rect(L, x - 3, 121, x + 4, 121, "dm1")
    arch(L, 404, 129, 139, 3, "ru0")                                      # bricked arch, right pavilion
    arch(L, 338, 129, 139, 3, "dw1")
    return L


# ============================================================================ 5 Capitol ruin overlay
def paint_capitol_ruin(front):
    L = new()
    for (x, top, length, w) in IVY_WING_L:
        for k in range(w):
            ln = length - int(hval("ivy", x, k) * 6)
            for y in range(top, top + ln):
                if front[y, x + k] < 0:
                    continue
                c = "vg2" if k == 0 else ("vg1" if (y + k) % 3 else "vg0")
                if y > top + ln - 3 and hval("ivyt", x, k, y) < 0.5:
                    continue
                px(L, x + k, y, c)
        px(L, x - 1, top + 2, "vg3")
    for (x, y, r) in ROOF_SHRUBS:
        crown(L, x, y - r * 0.4, r, VG, VG_CUTS, ("roof", x), squash=0.8, leaf=2)
    # House (south) wing corner collapse: everything above the broken profile becomes sky-coloured void (removed),
    # the broken edge shows the dark interior and floor slabs
    prof = np.interp(np.arange(W), [p[0] for p in HOUSE_COLLAPSE], [p[1] for p in HOUSE_COLLAPSE], left=-1, right=-1)
    for x in range(HOUSE_COLLAPSE[0][0], 576):
        top = int(prof[x])
        depth = 3 + int(hval("hdepth", x // 2) * 3)
        for y in range(top, top + depth):
            px(L, x, y, "dw0" if y < top + depth - 1 else "dw1")
        px(L, x, top + depth, "dm2")
    for (y, x0, x1) in ((104, 528, 538), (112, 536, 549), (121, 546, 560), (129, 556, 569)):   # exposed floor slabs
        rect(L, x0, y, x1, y, "dm3"); rect(L, x0, y + 1, x1, y + 1, "dm1")
        px(L, x1 + 1, y, "dm2")
    for (x, y0, y1) in ((541, 96, 104), (552, 106, 112), (563, 116, 121)):                  # bent iron beams
        line(L, x, y1, x + 3, y0, "ru0"); px(L, x + 3, y0 - 1, "ru1")
    for (x, y) in ((534, 132), (546, 130), (558, 133), (570, 136)):                        # fallen blocks below
        rect(L, x, y, x + 4, y + 2, "dm3"); rect(L, x, y, x + 4, y, "dm5"); px(L, x + 4, y + 2, "dm1")
    for (x, y, w) in SOOT:
        for k in range(w):
            if hval("soot", x, k) < 0.7:
                px(L, x + (k % 3) - 1, y - k, "dm1" if k < w // 2 else "dm2")
    return L


def house_void():
    """Mask of facade texels removed by the House wing collapse (sky shows through)."""
    prof = np.interp(np.arange(W), [p[0] for p in HOUSE_COLLAPSE], [p[1] for p in HOUSE_COLLAPSE])
    return (XX >= HOUSE_COLLAPSE[0][0]) & (XX <= 575) & (YY < prof[None, :].repeat(H, 0))


# ============================================================================ 6 Olmsted lower west terrace
def paint_terrace():
    L = new()
    rect(L, 0, T_RAIL, W - 1, T_RAIL, "dm5")
    for x in range(W):
        px(L, x, T_BAL[0], "dm2")
        for y in (T_BAL[0] + 1, T_BAL[1]):
            px(L, x, y, "dm4" if x % 2 == 0 else "dm1")
    rect(L, 0, T_BASE, W - 1, T_BASE, "dm4")
    for (a, b) in T_BAL_GAPS:
        rect(L, a, T_RAIL, b, T_BAL[1], -1)
        px(L, a, T_RAIL, "dm3"); px(L, b, T_BAL[1], "dm3")
    for x in T_PIERS:
        rect(L, x, T_RAIL - 2, x + 3, T_BASE, "dm4"); rect(L, x, T_RAIL - 2, x + 3, T_RAIL - 2, "dm6")
        rect(L, x + 3, T_RAIL - 1, x + 3, T_BASE, "dm2")
        rect(L, x + 1, T_RAIL - 4, x + 2, T_RAIL - 3, "dm3")             # urn
    # wall face: ashlar courses
    for y in range(T_WALL[0], T_WALL[1] + 1):
        rel = y - T_WALL[0]
        row = np.full(W, I["dm4"], np.int16)
        if rel % 3 == 2:
            row[:] = I["dm3"]
        else:
            off = (y // 3) * 5
            row[((np.arange(W) + off) % 11) == 0] = I["dm3"]
        L[y] = row
    rect(L, 0, T_WALL[0], W - 1, T_WALL[0], "dm2")                       # shadow under the base rail
    for x in T_WINDOWS:
        arch(L, x, 149, 155, 3, "dw0")
        rect(L, x - 1, 156, x + 3, 156, "dm5")
    for y in range(T_FOOT[0], T_FOOT[1] + 1):
        rect(L, 0, y, W - 1, y, "dm2" if y > T_FOOT[0] else "dm3")
    # recess between the stairs (set back, in shade), grotto arch, dry fountain
    a, b = RECESS
    for y in range(T_WALL[0], T_WALL[1] + 1):
        for x in range(a, b + 1):
            c = L[y, x]
            L[y, x] = I["dm3"] if c == I["dm4"] else I["dm2"]
    gx0, gx1, gy0, gy1 = GROTTO
    rect(L, gx0, gy0 + 2, gx1, gy1, "dw0"); rect(L, gx0 + 2, gy0, gx1 - 2, gy0 + 1, "dw0")
    rect(L, gx0 - 1, gy0 + 1, gx0 - 1, gy1, "dm5"); rect(L, gx0 + 1, gy0 - 1, gx1 - 1, gy0 - 1, "dm5")
    for x in range(gx0 + 2, gx1 - 1, 3):
        rect(L, x, gy0 + 4, x, gy1 - 1, "dw1")
    fx0, fx1, fy0, fy1 = FOUNTAIN_T
    rect(L, fx0, fy0, fx1, fy1, "dm4"); rect(L, fx0, fy0, fx1, fy0, "dm6"); rect(L, fx0, fy1, fx1, fy1, "dm2")
    rect(L, fx0 + 2, fy0 + 1, fx1 - 2, fy0 + 2, "dw1")
    for x in range(fx0 + 3, fx1 - 2, 4):
        crown(L, x, fy0 - 1, 3, VG, VG_CUTS, ("basin", x), squash=0.7, leaf=2)
    # twin grand stairs with cheek walls
    for (x0, x1) in STAIRS_T:
        for y in range(T_RAIL - 1, T_FOOT[1] + 1):
            c = "dm5" if (y - T_RAIL) % 2 == 0 else "dm2"
            rect(L, x0, y, x1, y, c)
            if c == "dm5":
                for x in range(x0, x1 + 1):
                    if hval("tread", x // 5, y) < 0.18:
                        px(L, x, y, "dm4")
        rect(L, x0, T_FOOT[1] - 1, x1, T_FOOT[1], "dm3")
    for (x0, x1) in CHEEKS_T:
        rect(L, x0, T_RAIL - 3, x1, T_FOOT[1], "dm4"); rect(L, x0, T_RAIL - 3, x1, T_RAIL - 3, "dm6")
        rect(L, x1, T_RAIL - 2, x1, T_FOOT[1], "dm2")
        rect(L, x0, T_RAIL - 6, x1, T_RAIL - 4, "br0")                   # bronze lantern on each cheek pier
        px(L, x0 + 1, T_RAIL - 7, "br1")
    # damage on the right of the terrace: stains, rubble cone from the House wing collapse
    for x in (60, 126, 236, 488, 556, 618):
        for y in range(T_WALL[0] + 1, T_WALL[0] + 7 + int(hval("stain", x) * 6)):
            px(L, x, y, "dm3" if y % 2 else "dm2")
    for (cx, cy, rx, ry) in COLLAPSE_CONE:
        m = ell(cx, cy, rx, ry) & (YY <= T_FOOT[1])
        n = vnoise(("cone", cx), 2)
        t = np.where(n > 0.62, I["dm5"], np.where(n > 0.36, I["dm3"], np.where(n > 0.18, I["dm2"], I["dm0"])))
        L[m] = t[m]
    for (x, top, length, w) in T_IVY:
        for k in range(w):
            for y in range(top, top + length - int(hval("tivy", x, k) * 4)):
                px(L, x + k, y, "vg2" if k == 0 else "vg1")
    for (x, y, r) in DECK_SHRUBS:
        crown(L, x, y - r * 0.5, r, VG, VG_CUTS, ("deck", x), squash=0.75, leaf=2)
    return L


# ============================================================================ 7 West Lawn (perspective ground)
def lawn_world():
    """World coordinates (X m, d m) for every texel of the lawn rows (164..H); near rows clamp to d = 20 m."""
    drow = np.array([d_of_row(y + 0.5) for y in range(H)], np.float32)
    D = drow[:, None].repeat(W, 1)
    X = (XX + 0.5 - CAPX) * D / F
    return X, D


def world_strip(X, D, p, q, hw):
    (xa, da), (xb, db) = p, q
    t = np.clip((D - da) / (db - da), 0, 1)
    xc = xa + (xb - xa) * t
    return (np.abs(X - xc) <= hw) & (D >= da) & (D <= db)


def paint_west_lawn():
    L = new()
    X, D = lawn_world()
    lawn = YY >= T_FOOT[1] + 1
    n1 = wnoise("lawn-a", X / 9.0, D / 9.0)
    n2 = wnoise("lawn-b", X / 2.2, D / 2.2)
    n3 = wnoise("lawn-dry", X / 16.0, D / 20.0)
    v = 0.5 * n1 + 0.35 * n2 + 0.15 * BAY
    base = quantize(LW[:5], v + (n3 - 0.5) * 0.5, (0.30, 0.42, 0.55, 0.70))
    L[lawn] = base[lawn]
    # grass tufts in world space: spacing ~0.55 m and blade height ~0.22 m, both shrinking with distance; jittered
    # per cell so no row or column pattern forms
    spm = F / D
    for y in range(T_FOOT[1] + 2, H):
        s = spm[y, 0]
        step = max(3, int(round(0.55 * s)))
        hb = 1 if s < 5 else max(1, min(6, int(round(0.22 * s))))
        for cx in range(-1, W // step + 2):
            if hval("lt", cx, y) > (0.30 if s < 5 else 0.42):
                continue
            x0 = cx * step + int(hval("lx", cx, y) * step)
            if not (0 <= x0 < W):
                continue
            c = L[y, x0]
            if c < 0 or int(c) not in LW:
                continue
            up = shift(LW, int(c), 1 if hval("lu", cx, y) < 0.7 else 2)
            lean = 1 if hval("ll", cx, y) < 0.3 else 0
            for k in range(hb):
                if y - k > T_FOOT[1]:
                    px(L, x0 + (lean if k >= hb - 1 and hb > 2 else 0), y - k, up if k >= hb - 2 else c)
            px(L, x0 + 1, y, shift(LW, int(c), -1))
    for (x, r) in TERRACE_FOOT_SHRUBS:                                   # shrubs along the lower-terrace foot
        crown(L, x, T_FOOT[1] + 1 - r * 0.3, r, VG, VG_CUTS, ("tfoot", x), squash=0.6, leaf=2)
    # worn central trail and two diagonal walks (perspective strips), half-buried
    trail = world_strip(X, D, TRAIL[0], TRAIL[1], TRAIL[2] / 2) & lawn
    ov = wnoise("trail-ov", X / 0.8, D / 1.6)
    ov2 = wnoise("trail-ov2", X / 0.35, D / 0.7)
    L[trail & (ov > 0.32)] = I["s3"]
    L[trail & (ov > 0.32) & (ov2 > 0.62)] = I["lw4"]
    L[trail & (ov > 0.66)] = I["s4"]
    L[trail & (ov > 0.32) & (ov2 < 0.2)] = I["lw2"]
    for p, q, hw in (WALK_L, WALK_R):
        st = world_strip(X, D, p, q, hw / 2) & lawn
        bur = wnoise(("walk-ov", p), X / 1.0, D / 2.5)
        L[st & (bur > 0.42)] = I["p3"]
        L[st & (bur > 0.42) & (bur < 0.5)] = I["p2"]
        edge = st & ~np.roll(st, 1, 0)
        L[edge & (bur > 0.42)] = I["p4"]
    # darker tall-grass swaths (world-space ellipses with ragged edges)
    for i, (xm, d, hx, hd) in enumerate(LAWN_PATCHES):
        e = ((X - xm) / hx) ** 2 + ((D - d) / hd) ** 2 <= 1 + 0.6 * (wnoise(("lp", i), X / 0.8, D / 0.8) - 0.5)
        e &= lawn
        L[e] = np.array([shift(LW, int(c), -1) if int(c) in LW else c for c in L[e]], np.int16)
    # trampled patrol trail down the lawn (darker, flattened grass) from the walker toward the wall breach
    for (xa, da), (xb, db) in zip(PATROL_TRAIL, PATROL_TRAIL[1:]):
        st = world_strip(X, D, (xa, da), (xb, db), 0.9) & lawn
        tr = wnoise("ptrail", X / 0.5, D / 0.9)
        m = st & (tr > 0.30)
        L[m] = np.array([shift(LW, int(c), -2) if int(c) in LW else c for c in L[m]], np.int16)
    # haze toward the terrace foot
    hz = np.clip((D - 95.0) / 135.0, 0, 1)
    hm = lawn & (BAY < hz * 0.85)
    L[hm] = HAZE_LUT[L[hm]]
    # meadow shrubs, the fallen log
    for i, (xm, d, r, kind) in enumerate(LAWN_SHRUBS):
        sx, sy = proj(xm, d)
        rp_ = max(2.0, r * F / d)
        ramp, cuts = (MG, MID_CUTS) if kind == "mg" else (VG, VG_CUTS)
        crown(L, sx, sy - rp_ * 0.55, rp_, ramp, cuts, ("lshrub", i), squash=0.7, leaf=2 if rp_ < 10 else 3)
    (xa, da), (xb, db) = FALLEN_LOG
    ax, ay = proj(xa, da); bx, by = proj(xb, db)
    line(L, ax, ay - 1, bx, by - 1, "b2"); line(L, ax, ay, bx, by, "b1"); line(L, ax, ay + 1, bx, by + 1, "b0")
    rect(L, ax - 1, ay - 2, ax, ay + 1, "b3")
    paint_walker(L)
    return L


WALKER_SPRITE = ["......kk.........",
                 ".....kKKk........",
                 "....kKHHKk.......",
                 "...kKHHKKRk......",
                 "..kkKKKKKkk......",
                 ".kKKKKKKKKKkk....",
                 "kKKKHHHKKKKKKk...",
                 "kkKKKKKKKKKKKkk..",
                 ".kkkKKKKKKKKkk.k.",
                 "..k.k..kk.k..k..k",
                 "..k..k.k..k..k...",
                 ".k...k.k...k.k...",
                 ".k...k..k..k..k..",
                 "k....k..k...k.k..",
                 "k...k...k...k..k.",
                 "k...k....k..k..k.",
                 "kk.kk...kk.kk..kk"]


def paint_walker(L):
    """Distant quadruped patrol walker (game fiction) on the lawn at d = 70 m, red sensor facing the plaza."""
    sx, sy = proj(*WALKER)
    x0, y0 = int(round(sx)) - 8, int(round(sy)) - len(WALKER_SPRITE) + 1
    stamp(L, x0, y0, WALKER_SPRITE, {"k": "k1", "K": "k2", "H": "k3", "R": "r2"})


# ============================================================================ 8 grounds trees (mid / far)
def paint_grounds_trees():
    L = new()
    for i, lobes in enumerate(FAR_MASSES):
        crown_lobes(L, lobes, VG, VG_CUTS, ("farmass", i), squash=0.85, leaf=2)
    for i, (x, d, hm, rm, kind) in enumerate(GROUNDS_TREES):
        s = F / d
        base = row_of(d)
        r = rm * s
        top = base - hm * s
        cy = top + r * 0.82
        ramp, cuts = (MG, MID_CUTS) if kind == "mid" else (VG, VG_CUTS)
        tw = max(1, int(round(0.6 * s)))
        tcol = ("b1", "b0") if kind == "mid" else ("vg0", "vg0")
        for y in range(int(cy), int(base) + 1):
            flare = 1 if y > base - 3 and tw > 2 else 0
            rect(L, x - tw // 2 - flare, y, x - tw // 2 + tw - 1 + flare, y, tcol[0])
            px(L, x - tw // 2 + tw - 1 + flare, y, tcol[1])
        if kind == "mid":                                              # two limbs into the crown
            for dx in (-1, 1):
                for k in range(int(r * 0.6)):
                    px(L, x + dx * (1 + k // 2), int(cy + r * 0.25) - k, "b1")
        crown(L, x, cy, r, ramp, cuts, ("gtree", i), squash=0.80, leaf=3 if r > 20 else 2,
              holes=((x - r * 0.35, cy + r * 0.38, r * 0.12, r * 0.08),) if r > 30 else ())
        if kind == "far":
            m = (L >= 0) & box(int(x - r - 3), int(top) - 2, int(x + r + 3), int(base))
            L[m & (BAY < 0.25)] = HAZE_LUT[L[m & (BAY < 0.25)]]
    # storm-broken snag (bare, splintered) beside the House wing
    x, d, hm = SNAG
    s = F / d
    base = int(row_of(d)); top = int(base - hm * s)
    brk = top + 16
    for y in range(brk, base + 1):
        px(L, x, y, "b2"); px(L, x + 1, y, "b1"); px(L, x + 2, y, "b0") if y > base - 30 else None
    for (yy, c) in ((brk - 3, "b3"), (brk - 2, "b2"), (brk - 1, "b2")):
        px(L, x + (1 if yy % 2 else 0), yy, c)
    for (y0, dx, ln, dy) in ((brk + 10, -1, 16, 0.6), (brk + 18, 1, 14, 0.5), (brk + 30, -1, 10, 0.4),
                             (brk + 34, 1, 12, 0.7), (brk + 44, -1, 7, 0.3)):
        for k in range(ln):
            px(L, x + (0 if dx < 0 else 2) + dx * (k + 1), y0 - int(k * dy), "b1" if k < ln - 3 else "b2")
    return L


# ============================================================================ 9-10 seat wall, steps, cheeks, lanterns
def arc_top():
    cx, cy, rx, ry = ARC
    xs = np.arange(W) + 0.5
    return np.round(cy - ry * np.sqrt(np.clip(1 - ((xs - cx) / rx) ** 2, 0, 1))).astype(int)


YTOP = arc_top()


def collapse_drop():
    return np.round(np.interp(np.arange(W), [p[0] for p in COLLAPSE], [p[1] for p in COLLAPSE], left=0,
                              right=0)).astype(int)


DROP = collapse_drop()
WALL_FOOT = YTOP + 16                                   # first ground row in front of the wall


def paint_lawn_edge():
    L = new()
    for i, (x, up, r, kind) in enumerate(WALL_SHRUBS):
        base = YTOP[min(W - 1, max(0, x))] + 2
        crown(L, x, base - up * 0.5 - r * 0.25, r, NEAR[:6], NEAR_CUTS[:5], ("wshrub", i), squash=0.72, gain=0.92)
    x, up, r = YOUNG_TREE
    base = YTOP[x] + 2
    for y in range(int(base - up), base + 1):
        px(L, x, y, "b1"); px(L, x + 1, y, "b0")
    crown(L, x, base - up, r, NEAR[:6], NEAR_CUTS[:5], ("ytree",), squash=0.85)
    return L


def ashlar_face(L, x, y0, nrows, key):
    """Granite ashlar on the curved face, courses of 4 rows relative to the column's coping."""
    widths = (14, 9, 17, 11, 15, 8, 13, 19, 10, 16)
    for r in range(nrows):
        y = y0 + r
        c = r // 4
        rr = r % 4
        off = int(hval(key, "off", c) * 23)
        # which block in this course
        pos = x + off
        acc, k = 0, int(hval(key, "k", c) * 10)
        while acc + widths[k % 10] <= pos:
            acc += widths[k % 10]; k += 1
        bx = pos - acc
        t = ("gr3", "gr3", "gr4", "gr3", "gr2", "gr3", "gr4")[int(hval(key, c, k) * 7)]
        if rr == 3 or bx == 0:
            col = "gr1" if rr == 3 else "gr2"
        elif rr == 0:
            col = shift_name(t, 1)
        else:
            col = t
            if rr == 2 and bx >= widths[k % 10] - 2:
                col = shift_name(t, -1)
        px(L, x, y, col)


def shift_name(n, d):
    i = GRAN.index(I[n])
    return ALL_PAL[GRAN[max(0, min(len(GRAN) - 1, i + d))]][0]


def paint_seat_wall():
    L = new()
    s0, s1 = STEPS
    for x in range(W):
        if CHEEKS[0][0] <= x <= CHEEKS[1][1]:
            continue
        top = YTOP[x]
        dr = DROP[x]
        if dr == 0:
            px(L, x, top, "m5"); px(L, x, top + 1, "m6" if (x // 3) % 2 else "m5"); px(L, x, top + 2, "m4")
            px(L, x, top + 3, "gr1")
            ashlar_face(L, x, top + 4, 11, "seat")
        else:
            broken = top + 3 + dr
            if broken < top + 15:
                px(L, x, broken, "gr1"); px(L, x, broken + 1, "s1")
                if hval("brk", x) < 0.4:
                    px(L, x, broken - 1, "gr2")
                for y in range(broken + 2, top + 15):
                    ashlar_face(L, x, y, 1, ("seat-c", y - top - 4))
        px(L, x, top + 15, "gr0")
    # ivy over the left wall, moss on the coping
    for x0, l, w in ((22, 13, 5), (58, 9, 3), (86, 12, 6), (140, 8, 3), (230, 10, 4), (262, 7, 2), (600, 11, 4),
                     (622, 14, 6)):
        for k in range(w):
            for y in range(YTOP[x0 + k] + 1, YTOP[x0 + k] + 1 + l - int(hval("wivy", x0, k) * 5)):
                px(L, x0 + k, y, "f2" if (y + k) % 3 else "f3")
            px(L, x0 + k, YTOP[x0 + k], "f3" if k % 2 else "f4")
    for x in range(0, W, 1):
        if DROP[x] == 0 and not (CHEEKS[0][0] <= x <= CHEEKS[1][1]) and hval("cmoss", x // 4) < 0.22:
            px(L, x, YTOP[x], "mo1")
    # steps
    n_steps = sum(1 for r in STEP_ROWS if r[2] == "riser")
    k_up = n_steps
    for (y0, y1, kind) in STEP_ROWS:                 # top -> bottom; higher steps are farther: 2 px narrower each
        inset = 2 * k_up
        for y in range(y0, y1 + 1):
            for x in range(s0, s1 + 1):
                if x < s0 + inset or x > s1 - inset:
                    c = "gr3" if y % 3 else "gr2"                       # cheek wall return beside the flight
                elif kind == "riser":
                    c = "p1" if y == y0 else "p3"
                    if (x - s0 + 11 * (y0 // 5)) % 29 == 0:
                        c = "p2"
                elif kind == "landing":
                    c = "p4" if y < y1 else "p5"
                else:
                    c = "p5" if y == y1 else "p4"
                    if (x - s0 + 7 * (y0 // 5)) % 23 == 0 and y < y1:
                        c = "p3"
                    if abs(x - 372) < 18 and y < y1 and hval("wear", x // 2, y) < 0.45:
                        c = "p3"
                px(L, x, y, c)
        if kind == "riser":
            k_up -= 1
    # worn / broken treads, weeds in the joints
    rect(L, 412, 213, 431, 215, "p2"); rect(L, 414, 214, 429, 215, "s2"); rect(L, 416, 213, 424, 213, "p3")
    for (x, y) in ((318, 210), (330, 215), (402, 220), (426, 209), (346, 205), (392, 205)):
        px(L, x, y, "g3"); px(L, x + 1, y - 1, "g4"); px(L, x - 1, y, "g2")
    # cheek piers
    for i, (x0, x1) in enumerate(CHEEKS):
        rect(L, x0, CHEEK_TOP, x1, CHEEK_TOP + 1, "m5"); rect(L, x0, CHEEK_TOP + 2, x1, CHEEK_TOP + 2, "m6")
        rect(L, x0, CHEEK_TOP + 3, x1, CHEEK_TOP + 3, "m4"); rect(L, x0, CHEEK_TOP + 4, x1, CHEEK_TOP + 4, "gr1")
        for y in range(CHEEK_TOP + 5, 222):
            for x in range(x0, x1 + 1):
                r = y - CHEEK_TOP - 5
                if r % 6 == 5:
                    c = "gr2"
                elif r % 6 == 0:
                    c = "gr4"
                else:
                    c = "gr3"
                if x == x1:
                    c = "gr2"
                if x == x0:
                    c = "gr4" if r % 6 != 5 else "gr3"
                px(L, x, y, c)
        rect(L, x0, 222, x1, 222, "gr0")
    # bronze plaque on the left cheek, laser scorch on the right cheek
    rect(L, 299, 204, 308, 211, "bz1"); rect(L, 300, 205, 307, 210, "bz2")
    for y in (206, 208):
        rect(L, 301, y, 306, y, "bz3")
    for (x, y) in ((436, 201), (437, 202), (438, 203), (439, 204), (440, 205), (441, 206), (442, 207)):
        px(L, x, y, "sc0"); px(L, x + 1, y, "sc1")
    # lanterns: left intact (post, collar, cage with dark glass), right snapped
    x, b = LANTERN_L
    rect(L, x - 3, b - 4, x + 4, b - 1, "bz1"); rect(L, x - 3, b - 4, x - 3, b - 1, "bz2")
    rect(L, x, b - 34, x + 1, b - 5, "bz1"); rect(L, x, b - 34, x, b - 5, "bz2")
    rect(L, x - 1, b - 22, x + 2, b - 21, "bz2")
    stamp(L, x - 4, b - 46, ["...bb....", "..bBBb...", ".bbbbbbb.", ".bkKkkKb.", ".bkkkkkb.", ".bKkkkkb.",
                              ".bkkkKkb.", ".bbbbbbb.", "..bBBb...", "...bb...."],
          {"b": "bz1", "B": "bz3", "k": "k0", "K": "k2"})
    x, b = LANTERN_R_STUB
    rect(L, x - 3, b - 4, x + 4, b - 1, "bz1"); rect(L, x - 3, b - 4, x - 3, b - 1, "bz2")
    rect(L, x, b - 14, x + 1, b - 5, "bz1"); rect(L, x, b - 14, x, b - 5, "bz2")
    px(L, x + 1, b - 15, "bz1"); px(L, x, b - 16, "bz2")
    return L


# ============================================================================ 11 plaza ground (walkable plane)
def plaza_masks():
    m = {}
    ground = YY >= WALL_FOOT[None, :]
    stepzone = box(STEPS[0], 203, STEPS[1], 222)
    m["ground"] = ground & ~box(CHEEKS[0][0], 0, CHEEKS[1][1], 222)
    fx, fy, frx, fry = FORECOURT
    core = ell(fx, fy, frx, fry) & (YY >= fy)
    rim = ell(fx, fy, frx * 0.86, fry * 0.80)
    ragged = vnoise("fc-rim", 5) > 0.48
    m["forecourt"] = m["ground"] & core & (rim | ragged)
    m["axis"] = m["ground"] & box(AXIS_WALK[0], int(fy), AXIS_WALK[1], H - 1) & ~m["forecourt"]
    m["paving"] = m["forecourt"] | m["axis"]
    m["steps"] = stepzone
    paths = np.zeros((H, W), bool)
    for pts, hw in (WEST_PATH, EAST_PATH):
        for p, q in zip(pts, pts[1:]):
            paths |= seg(p, q, hw)
    m["paths"] = m["ground"] & paths & ~m["paving"]
    return m


def setts(L, mask, key):
    """Granite setts in courses concentric with the curved seat wall (centre = the wall's ellipse centre), sett
    lengths 9..13 px per course, staggered; joints mostly mid-tone so the forecourt reads as a flat floor."""
    cx, cy, rx, ry = ARC
    ratio = rx / ry
    ys, xs = np.nonzero(mask)
    dx, dy = xs + 0.5 - cx, (ys + 0.5 - cy) * ratio
    r = np.hypot(dx, dy)
    th = np.arctan2(dy, dx)
    cw = 11.0
    course = np.floor(r / cw).astype(int)
    fr = r / cw - course
    arc = th * r
    cl = np.clip(course, 0, 99)
    lens = np.array([9 + int(hval(key, "len", c) * 5) for c in range(100)])
    offs = np.array([hval(key, "off", c) * 13 for c in range(100)])
    sidx = np.floor((arc + offs[cl]) / lens[cl]).astype(int)
    sfr = (arc + offs[cl]) / lens[cl] - sidx
    pick = [2, 3, 3, 3, 4, 3, 2, 3, 4, 3]
    tones = np.array([PAVE[pick[int(hval(key, a, b) * 10)]] for a, b in zip(cl, sidx)], np.int16)
    out = tones.copy()
    along = sfr * lens[cl]
    joint_c = fr < 0.12
    joint_s = along < 1.0
    lit = (~joint_c) & (~joint_s) & (fr > 0.86)
    out = np.where(lit, np.array([shift(PAVE, int(t), 1) for t in tones]), out)
    shade = (~joint_c) & (~joint_s) & (along > lens[cl] - 1.2) & (fr < 0.5)
    out = np.where(shade, np.array([shift(PAVE, int(t), -1) for t in tones]), out)
    dark_j = np.array([hval(key, "jd", a, b) < 0.35 for a, b in zip(cl, sidx)])
    out = np.where(joint_c | joint_s, np.where(dark_j, I["p1"], I["p2"]), out)
    L[ys, xs] = out


def flags(L, mask, y0, course_h, key, widths):
    """Large granite flags in staggered courses (irregular slab lengths, mid-tone joints, a lit front lip only on
    some slabs) so the walk reads as a floor, not as a brick wall."""
    ys, xs = np.nonzero(mask)
    for y, x in zip(ys, xs):
        c = int(math.floor((y - y0) / course_h))
        rr = (y - y0) - c * course_h
        off = int(hval(key, "off", c) * 23)
        pos = x + off
        acc, k = 0, int(hval(key, "k", c) * len(widths))
        while acc + widths[k % len(widths)] <= pos:
            acc += widths[k % len(widths)]; k += 1
        bx = pos - acc
        wdt = widths[k % len(widths)]
        t = PAVE[[2, 3, 3, 2, 3, 4, 3, 2, 3, 3][int(hval(key, c, k) * 10)]]
        if rr == 0 or bx == 0:
            col = I["p2"] if hval(key, "j", c, k) < 0.6 else I["p1"]
        elif rr == course_h - 1 and hval(key, "lip", c, k) < 0.5:
            col = shift(PAVE, t, 1)
        elif bx >= wdt - 1 and rr > 1:
            col = shift(PAVE, t, -1)
        else:
            col = t
            if hval(key, "spk", x, y) < 0.03:
                col = shift(PAVE, t, -1 if t != PAVE[2] else 1)
        L[y, x] = col


GRASS_TUFT = ((0, 0, 1), (-1, 1, 1), (1, 1, 0), (0, 1, -1))
TALL_TUFT = ((0, 0, 2), (0, 1, 1), (-1, 2, 1), (1, 2, 0), (0, 2, -1))
CLOVER = ((0, 0, 1), (1, 0, 1), (0, 1, 0), (1, 1, 0), (-1, 1, 1))


def turf(L, mask, key, cell=(5, 4)):
    """Meadow turf: broad sunlit/damp zones with a 2x2 checker border, one blade tuft per jittered cell, each tuft
    one tone step from its ground (texture, never flecks)."""
    n = vnoise((key, "zone"), 48)
    n2 = vnoise((key, "zone2"), 14)
    chk = (XX // 2 + YY // 2) % 2 == 0
    base = np.full((H, W), I["g2"], np.int16)
    v = 0.65 * n + 0.35 * n2
    base[(v > 0.60) | ((v > 0.56) & chk)] = I["g3"]
    base[(v > 0.74) | ((v > 0.71) & chk)] = I["g4"]
    base[(v < 0.30) | ((v < 0.34) & chk)] = I["g1"]
    L[mask] = base[mask]
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return
    cw, ch = cell
    order = {c: i for i, c in enumerate(GR)}
    for gy in range(ys.min() // ch, ys.max() // ch + 1):
        for gx in range(xs.min() // cw, xs.max() // cw + 1):
            if hval(key, "s", gx, gy) > 0.80:
                continue
            x = gx * cw + int(hval(key, "x", gx, gy) * cw)
            y = gy * ch + int(hval(key, "y", gx, gy) * ch)
            if not (0 < x < W - 1 and y < H - 2) or not mask[y, x]:
                continue
            c0 = int(L[y, x])
            if c0 not in order:
                continue
            b = order[c0]
            hv = hval(key, "t", gx, gy)
            tuft = TALL_TUFT if hv < 0.22 else (CLOVER if hv > 0.93 else GRASS_TUFT)
            for dx, dy, d in tuft:
                if mask[y + dy, x + dx]:
                    L[y + dy, x + dx] = GR[max(0, min(6, b + d))]


def blob(cx, cy, rx, ry, key, amp=0.35):
    n = vnoise(("blob", key), 3)
    return (((XX + 0.5 - cx) / rx) ** 2 + ((YY + 0.5 - cy) / ry) ** 2) <= 1.0 + amp * (n - 0.5)


def paint_plaza_ground():
    L = new()
    m = plaza_masks()
    turf(L, m["ground"] & ~m["paving"], "turf")
    setts(L, m["forecourt"], "fan")
    flags(L, m["axis"], int(FORECOURT[1]) + 2, 12, "axis", (26, 18, 24, 15, 22, 28, 17, 20))
    # worn desire paths: packed soil with a paler centre, grass creeping over the edges
    for pi_, (pts, hw) in enumerate((WEST_PATH, EAST_PATH)):
        dist = np.full((H, W), 1e9, np.float32)
        for p, q in zip(pts, pts[1:]):
            dist = np.minimum(dist, seg_dist(p, q))
        wid = hw * (0.55 + 0.75 * vnoise(("pathw", pi_), 9))
        edge_n = vnoise(("pathedge", pi_), 2)
        rel = dist / wid
        soil = m["ground"] & ~m["paving"] & (rel < 0.75 + 0.45 * (edge_n - 0.5))
        tone_n = vnoise(("pathtone", pi_), 4)
        out = np.where(rel < 0.35, np.where(tone_n > 0.5, I["d1"], I["s4"]),
                       np.where(rel < 0.6, I["s3"], np.where(BAY < 0.5, I["s2"], I["d0"])))
        L[soil] = out[soil]
        tuft = soil & (vnoise(("pathgrass", pi_), 2) > 0.74)
        L[tuft] = I["g3"]
        L[soil & edge_above(soil) & (BAY < 0.4)] = I["s1"]
    # remnant flags of the First Street walk along the west path (root-heaved by the elm)
    for (x, y, w) in WEST_SLABS:
        rect(L, x, y - 3, x + w - 1, y + 1, "p3"); rect(L, x, y - 3, x + w - 1, y - 3, "p4")
        rect(L, x, y + 1, x + w - 1, y + 1, "p1"); px(L, x + w - 1, y - 2, "p2")
    for (x0, y0, x1, y1) in ROOT_HEAVE:
        for (a, b) in (((26, 307), (44, 312)), ((50, 302), (60, 314)), ((68, 304), (88, 300)), ((92, 298), (104, 304))):
            for (x, y) in zip(np.linspace(a[0], b[0], 24), np.linspace(a[1], b[1], 24)):
                px(L, round(x), round(y), "s0")
    # paving edges: lit kerb on the upper side, dark on the lower, grass lips over the edge
    pav, grs = m["paving"], m["ground"] & ~m["paving"]
    up = np.zeros_like(pav); up[1:] = pav[1:] & grs[:-1]
    dn = np.zeros_like(pav); dn[:-1] = pav[:-1] & grs[1:]
    L[up] = I["p3"]; L[dn] = I["p1"]
    lip = np.zeros_like(pav); lip[1:] = grs[1:] & pav[:-1]
    L[lip & (BAY < 0.5)] = I["g3"]
    # turf invading the paving, missing setts
    for i, (cx, cy, rx, ry) in enumerate(TURF_INVADE):
        b = blob(cx, cy, rx, ry, ("inv", i)) & pav
        tmp = new()
        turf(tmp, b, ("invturf", i))
        L[b] = tmp[b]
    for i, (cx, cy, rx, ry) in enumerate(MISSING):
        b = blob(cx, cy, rx, ry, ("miss", i), 0.5) & pav
        L[b] = I["s2"]
        L[b & (vnoise(("miss-n", i), 2) > 0.62)] = I["s3"]
        L[b & edge_above(b)] = I["s0"]
    return L


def seg_dist(p, q):
    (x0, y0), (x1, y1) = p, q
    dx, dy = x1 - x0, y1 - y0
    t = np.clip(((XX + 0.5 - x0) * dx + (YY + 0.5 - y0) * dy) / float(dx * dx + dy * dy), 0, 1)
    return np.hypot(XX + 0.5 - (x0 + t * dx), YY + 0.5 - (y0 + t * dy)).astype(np.float32)


def poly_mask(pts):
    """Even-odd point-in-polygon mask for a hand-drawn outline."""
    m = np.zeros((H, W), bool)
    xs, ys = XX + 0.5, YY + 0.5
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        cond = (y0 > ys) != (y1 > ys)
        xint = (x1 - x0) * (ys - y0) / (y1 - y0 if y1 != y0 else 1e-9) + x0
        m ^= cond & (xs < xint)
    return m


def edge_above(m):
    a = np.zeros_like(m)
    a[1:] = m[1:] & ~m[:-1]
    a[0] = m[0]
    return a


# ============================================================================ 12 ground detail
PRINT = ["x.x.x", ".xxx.", "..x.."]
FLOWER_DRIFTS = [(96, 300, ("fl0", "fl2"), 22, 6, 6), (250, 314, ("fl1", "fl2"), 16, 5, 4),
                 (470, 318, ("fl0", "fl3"), 18, 5, 5), (604, 290, ("fl1", "fl0"), 16, 6, 4),
                 (140, 340, ("fl2", "fl1"), 20, 5, 5), (444, 344, ("fl0", "fl2"), 18, 5, 5),
                 (300, 236, ("fl0", "fl1"), 10, 3, 3), (22, 250, ("fl2", "fl0"), 12, 4, 3)]


def paint_ground_detail():
    L = new()
    m = plaza_masks()
    pav = m["paving"]
    # cracks
    for i, pts in enumerate(CRACKS):
        for (a, b) in zip(pts, pts[1:]):
            n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
            for k in range(n):
                t = k / max(1, n - 1)
                x = round(a[0] + (b[0] - a[0]) * t + (hval("ck", i, k) - 0.5) * 1.2)
                y = round(a[1] + (b[1] - a[1]) * t)
                if 0 <= x < W and 0 <= y < H and pav[y, x]:
                    px(L, x, y, "p0")
                    if hval("ckw", i, k) < 0.3 and y + 1 < H:
                        px(L, x + 1, y, "g3")
    # moss in sett joints near the wall foot (shade side) and along the stair foot
    near_wall = m["forecourt"] & (YY < WALL_FOOT[None, :] + 10)
    ys, xs = np.nonzero(near_wall)
    for y, x in zip(ys, xs):
        if hval("moss", x, y) < 0.10:
            px(L, x, y, "mo0" if hval("moss2", x, y) < 0.5 else "mo1")
    # patrol: three-toed claw prints (mud on turf, scuff on paving), alternating feet
    for k, (x, y) in enumerate(PATROL_PRINTS):
        ox = 3 if k % 2 else -3
        on_pave = pav[min(H - 1, y), min(W - 1, max(0, x))]
        cmap = {"x": "p1" if on_pave else "s1"}
        stamp(L, x + ox - 2, y - 1, PRINT, cmap)
        if not on_pave:
            rect(L, x + ox - 2, y + 2, x + ox + 2, y + 2, "s2")
    # laser scorch ring around the beacon foot
    bx, by = BEACON
    ring = ell(bx, by - 1, 16, 6) & ~ell(bx, by - 1, 6, 2.5)
    n = vnoise("scorch", 2)
    L[ring & (n < 0.45)] = I["sc1"]
    L[ring & (n < 0.25)] = I["sc0"]
    for a in range(0, 360, 40):
        for k in range(8, 20):
            x = round(bx + math.cos(math.radians(a)) * k)
            y = round(by - 1 + math.sin(math.radians(a)) * k * 0.4)
            if hval("ray", a, k) < 0.5:
                px(L, x, y, "sc1")
    # flowers, clover, leaf litter, pebbles
    grs = m["ground"] & ~pav
    for i, (cx, cy, cols, rx, ry, n_) in enumerate(FLOWER_DRIFTS):
        for k in range(n_ * 6):
            a = hval("fd", i, k) * 2 * math.pi
            rr = math.sqrt(hval("fr", i, k))
            x = round(cx + math.cos(a) * rr * rx); y = round(cy + math.sin(a) * rr * ry)
            if 0 <= x < W - 1 and 0 <= y < H - 1 and grs[y, x]:
                c = cols[int(hval("fc", i, k) * len(cols))]
                px(L, x, y, c)
                if hval("fs", i, k) < 0.4:
                    px(L, x + 1, y, c)
                px(L, x, y + 1, "g1")
    for k in range(70):
        x = int(8 + hval("leaf", k) * 150); y = int(250 + hval("leafy", k) * 80)
        if 0 <= y < H and m["ground"][y, x]:
            px(L, x, y, ("b2", "d1", "ru3", "b3")[k % 4])
    for k in range(28):
        x = int(500 + hval("aleaf", k) * 110); y = int(276 + hval("aleafy", k) * 30)
        if m["ground"][y, x]:
            px(L, x, y, ("d1", "fl0", "b2")[k % 3])
    for k in range(40):
        x = int(hval("peb", k) * W); y = int(230 + hval("peby", k) * 126)
        if m["ground"][y, x] and not pav[y, x]:
            px(L, x, y, "gr4"); px(L, x, y + 1, "gr1") if y + 1 < H else None
    # tall meadow clumps with goldenrod / aster heads (ground texture the heroine walks through)
    for i, (cx, cy, rx, ry) in enumerate(MEADOW_PATCHES):
        for k in range(int(rx * ry * 0.9)):
            a = hval("mp", i, k) * 2 * math.pi
            rr = math.sqrt(hval("mpr", i, k))
            x = round(cx + math.cos(a) * rr * rx); y = round(cy + math.sin(a) * rr * ry)
            if not (1 <= x < W - 1 and 8 <= y < H) or not grs[y, x]:
                continue
            hgt = 3 + int(hval("mph", i, k) * 5 * (1 - rr * 0.5))
            lean = (1 if hval("mpl", i, k) < 0.5 else -1) if hgt > 4 else 0
            for j in range(hgt):
                c = "g1" if j == 0 else ("g4" if j < hgt - 1 else "g5")
                px(L, x + (lean if j > hgt * 0.6 else 0), y - j, c)
            if hval("mpf", i, k) < 0.16:
                px(L, x + lean, y - hgt, "fl0" if i % 2 == 0 else "fl1")
    # wall-foot grass lip and dark contact strip
    for x in range(W):
        y = WALL_FOOT[x]
        if 0 <= y < H and DROP[x] == 0 and not (CHEEKS[0][0] <= x <= CHEEKS[1][1]):
            if hval("wf", x // 2) < 0.6 and not pav[y, x]:
                px(L, x, y, "g1")
                if hval("wft", x) < 0.4:
                    px(L, x, y - 1, "g2")
    return L


# ============================================================================ 14 rubble (collapsed seat-wall bay)
def block(L, x, base, w, h, kind, t, reg, key):
    """Faceted block lit from the front-left: top face, front face with a course joint, dark right side, contact
    shadow. `cut` = clean laser-cut face with a scorched edge (patrol cue)."""
    top_h = max(2, h // 3)
    side = max(1, w // 6)
    if kind == "chip":
        rect(L, x, base - h + 1, x + w - 1, base, t, reg)
        rect(L, x, base - h + 1, x + w - 1, base - h + 1, "gr4" if t != "gr4" else "gr5", reg)
        rect(L, x + w - 1, base - h + 2, x + w - 1, base, "gr1", reg)
        rect(L, x, base, x + w - 1, base, "gr1", reg)
        return
    marble = kind == "coping"
    topc = "m5" if marble else shift_name(t, 1) if t in ("gr2", "gr3", "gr4") else "gr5"
    frontc = t
    sidec = "gr2" if marble else "gr1"
    skew = int(hval(key, "skew") * 3) - 1
    for j in range(top_h):
        rect(L, x + j // 2 + max(0, skew), base - h + 1 + j, x + w - 1 - side + j // 2, base - h + 1 + j, topc, reg)
    rect(L, x, base - h + 1 + top_h, x + w - 1 - side, base, frontc, reg)
    rect(L, x + w - side, base - h + 1 + top_h // 2, x + w - 1, base, sidec, reg)
    if not marble and h >= 9:
        jy = base - (h - top_h) // 2
        rect(L, x, jy, x + w - 1 - side, jy, "gr2", reg)
        px(L, x + int(hval(key, "vj") * (w - 4)) + 2, jy + 1, "gr2", reg)
    if kind == "cut":
        for j in range(h - top_h):
            px(L, x + 3 + j, base - j, "gr5", reg)
            px(L, x + 4 + j, base - j, "sc0", reg)
    rect(L, x, base, x + w - 1, base, "ink" if not marble else "gr1", reg)
    if hval(key, "moss") < 0.4:
        rect(L, x + 1, base - h + 1, x + 1 + int(w * 0.4), base - h + 1, "mo1", reg)


def baluster(L, x, base, reg, key):
    rows = [".mm.", "mMMm", "MMMm", "mMMm", ".mm.", ".Mm.", "mMMm", "mmmm"]
    for j, row in enumerate(rows):            # a lying baluster: drawn rotated (horizontal)
        for i, ch in enumerate(row):
            if ch != ".":
                px(L, x + j, base - 3 + i, "m5" if ch == "M" else "m3", reg)
    rect(L, x, base + 1, x + 7, base + 1, "gr1", reg)


def paint_rubble():
    L = new()
    items = {}
    # the heap: one hand-drawn silhouette filled with dark broken core, lit specks on its upper-left faces, weeds;
    # registered in 8-px column strips so every strip has its own contact row for the depth audit
    heap = poly_mask(HEAP)
    n = vnoise("core", 2)
    n3 = vnoise("core3", 4)
    L[heap] = np.where(n[heap] > 0.55, I["gr3"], np.where(n[heap] > 0.32, I["gr2"],
                                                          np.where(n[heap] > 0.16, I["gr1"], I["s1"])))
    lit = heap & (n3 > 0.66) & (vnoise("core-l", 2) > 0.55)
    L[lit] = I["gr4"]
    bottom = heap & ~np.roll(heap, -1, 0)
    L[bottom] = I["ink"]
    for x0 in range(480, 612, 8):
        strip = heap & (XX >= x0) & (XX < x0 + 8)
        if strip.any():
            items[f"heap_{x0}"] = {"mask": strip, "base": int(np.nonzero(strip.any(1))[0].max())}
    for i, (x, b, w, h, kind, t) in enumerate(sorted(RUBBLE, key=lambda r: r[1])):
        reg = np.zeros((H, W), bool)
        block(L, x, b, w, h, kind, t, reg, ("rb", i))
        items[f"rubble_{i:02d}"] = {"mask": reg, "base": b}
    for i, (x, b) in enumerate(LYING_BALUSTERS):
        reg = np.zeros((H, W), bool)
        baluster(L, x, b, reg, ("bal", i))
        items[f"baluster_{i}"] = {"mask": reg, "base": b + 1}
    for k in range(46):                                                   # weeds and grass rooted in the heap
        x = int(490 + hval("hw", k) * 114); y = int(226 + hval("hwy", k) * 52)
        if heap[min(H - 1, y), x] and hval("hw2", k) < 0.8:
            hgt = 2 + int(hval("hwh", k) * 4)
            for j in range(hgt):
                px(L, x + (j // 3 if k % 2 else 0), y - j, "g3" if j < hgt - 1 else "g5")
            px(L, x - 1, y, "g2"); px(L, x + 1, y, "g1")
    # tree of heaven (Ailanthus) self-sown in the rubble: slender trunk, light pinnate crown
    x, b = AILANTHUS
    reg = np.zeros((H, W), bool)
    for y in range(b - 52, b + 1):
        bend = int(round(math.sin((b - y) / 18.0) * 2))
        px(L, x + bend, y, "b2", reg); px(L, x + bend + 1, y, "b1", reg)
    lobes = [(x - 14, b - 66, 13), (x + 6, b - 74, 15), (x + 22, b - 60, 12), (x - 4, b - 54, 11),
             (x + 14, b - 48, 9), (x - 20, b - 50, 8)]
    crown_lobes(L, lobes, NEAR, NEAR_CUTS, "ailanthus", reg, squash=0.8, gain=1.1, leaf=2)
    items["ailanthus"] = {"mask": reg & (YY > b - 8), "base": b}
    # the fallen lantern head on the forecourt
    hx, hb = LANTERN_HEAD_FALLEN
    reg = np.zeros((H, W), bool)
    stamp(L, hx - 7, hb - 5, ["..bbbbbbbb.", ".bkkKkkkbBb", "bbkkkkKkbbB", ".bkKkkkkbBb", "..bbbbbbbb.",
                              "...........".replace(".", ".")], {"b": "bz1", "B": "bz3", "k": "k0", "K": "k2"}, reg)
    rect(L, hx + 4, hb - 2, hx + 14, hb - 1, "bz1", reg); rect(L, hx + 4, hb - 2, hx + 14, hb - 2, "bz2", reg)
    rect(L, hx - 7, hb, hx + 14, hb, "gr0", reg)
    items["lantern_head"] = {"mask": reg, "base": hb}
    return L, items


# ============================================================================ 15 props-low (survey kit)
def paint_props():
    L = new()
    items = {}
    # rugged crate with the field terminal on it
    x, b = CRATE
    reg = np.zeros((H, W), bool)
    rect(L, x, b - 12, x + 28, b, "tp0", reg); rect(L, x, b - 12, x + 28, b - 11, "tp1", reg)
    rect(L, x + 26, b - 10, x + 28, b, "k1", reg)
    for xx in (x + 4, x + 14, x + 22):
        rect(L, xx, b - 8, xx + 1, b - 6, "k3", reg)
    rect(L, x, b, x + 28, b, "ink", reg)
    stamp(L, x + 5, b - 21, ["kkkkkkkkkkkkk", "kt0000000000k", "kt0110120010k", "kt0000000000k",
                             "kt0101001100k", "kt000000000tk", "kkkkkkkkkkkkk", ".kKKKKKKKKKk.", "..kkkkkkkkk.."],
          {"k": "k0", "t": "t0", "0": "t0", "1": "t1", "2": "t2", "K": "k2"}, reg)
    items["survey_crate"] = {"mask": reg, "base": b}
    # solar panel on a folding stand
    x, b = PANEL
    reg = np.zeros((H, W), bool)
    for j in range(9):
        rect(L, x + j, b - 14 + j, x + 26 + j, b - 14 + j, "sp1", reg)
    for j in range(9):
        px(L, x + j, b - 14 + j, "sp0", reg); px(L, x + 26 + j, b - 14 + j, "sp0", reg)
    rect(L, x, b - 14, x + 26, b - 14, "sp2", reg)
    for k in range(1, 4):
        for j in range(9):
            px(L, x + j + k * 7, b - 14 + j, "sp0", reg)
    rect(L, x + 1, b - 10, x + 27, b - 10, "sp2", reg)
    rect(L, x + 6, b - 5, x + 6, b, "k2", reg); rect(L, x + 30, b - 5, x + 30, b, "k2", reg)
    rect(L, x + 4, b, x + 32, b, "ink", reg)
    items["solar_panel"] = {"mask": reg, "base": b}
    # hard cases
    for i, (cx, b, kind) in enumerate(CASES):
        reg = np.zeros((H, W), bool)
        w = 12 if kind == "k" else 9
        rect(L, cx, b - 6, cx + w, b, "k2" if kind == "k" else "o0", reg)
        rect(L, cx, b - 6, cx + w, b - 6, "k3" if kind == "k" else "o1", reg)
        rect(L, cx + w - 1, b - 5, cx + w, b, "k1" if kind == "k" else "ru2", reg)
        rect(L, cx + w // 2 - 1, b - 4, cx + w // 2, b - 4, "k4" if kind == "k" else "o2", reg)
        rect(L, cx, b, cx + w, b, "ink", reg)
        items[f"case_{i}"] = {"mask": reg, "base": b}
    # toppled Olmsted bronze lamp standard in the meadow (granite base uprooted), registered in 8-px strips
    (ax, ay), (bx, by) = FALLEN_LAMP
    reg = np.zeros((H, W), bool)
    n = int(max(abs(bx - ax), abs(by - ay)))
    for k in range(n + 1):
        t = k / n
        x = round(ax + (bx - ax) * t); y = round(ay + (by - ay) * t)
        px(L, x, y - 2, "bz2", reg); px(L, x, y - 1, "bz1", reg); px(L, x, y, "bz0", reg)
        if k % 22 == 6:
            rect(L, x - 1, y - 3, x + 1, y + 1, "bz1", reg); px(L, x - 1, y - 3, "bz3", reg)
    stamp(L, ax - 9, ay - 8, ["..gggggg..", ".gGGGGGgg.", "gGGgggGGgg", "gGgggggGgg", "gggggggggg", ".ssSsssSs.",
                              "..ssssss.."], {"g": "gr3", "G": "gr4", "s": "s1", "S": "s2"}, reg)
    stamp(L, bx - 2, by - 6, [".bbbbbbb.", "bkkKkbkkb", "bkkkkbKkb", "bbbbbbbbb", ".bBbbbBb.", "..b...b.."],
          {"b": "bz1", "B": "bz3", "k": "k0", "K": "k2"}, reg)
    for x0 in range(ax - 10, bx + 10, 8):
        strip = reg & (XX >= x0) & (XX < x0 + 8)
        if strip.any():
            items[f"fallen_lamp_{x0}"] = {"mask": strip, "base": int(np.nonzero(strip.any(1))[0].max())}
    # low shrubs on the turf and a fallen elm limb
    for i, (x, b, r) in enumerate(GROUND_SHRUBS):
        reg = np.zeros((H, W), bool)
        crown(L, x, b - r * 0.55, r, NEAR[:6], NEAR_CUTS[:5], ("gshrub", i), reg, squash=0.62, leaf=2)
        rect(L, x - r + 2, b, x + r - 2, b, "f0", reg)
        items[f"ground_shrub_{i}"] = {"mask": reg, "base": b}
    (ax, ay), (bx, by) = FALLEN_LIMB
    reg = np.zeros((H, W), bool)
    n = int(max(abs(bx - ax), abs(by - ay)))
    for k in range(n + 1):
        t = k / n
        x = round(ax + (bx - ax) * t); y = round(ay + (by - ay) * t)
        th = 3 if k < n * 0.6 else 2
        for j in range(th):
            px(L, x, y - j, ("b0", "b2", "b3")[j] if th == 3 else ("b0", "b2")[j], reg)
    for (k0, dx, dy) in ((14, 6, -5), (30, -4, -6), (44, 7, -4)):
        t = k0 / n
        x = round(ax + (bx - ax) * t); y = round(ay + (by - ay) * t)
        line(L, x, y - 1, x + dx, y - 1 + dy, "b1", reg)
    rect(L, ax - 2, ay - 3, ax, ay, "b3", reg); px(L, ax - 1, ay - 2, "b2", reg)
    for x0 in range(ax - 4, bx + 8, 8):
        strip = reg & (XX >= x0) & (XX < x0 + 8)
        if strip.any():
            items[f"fallen_limb_{x0}"] = {"mask": strip, "base": int(np.nonzero(strip.any(1))[0].max())}
    # cables (ground lines, not obstacles)
    for (a, b_, sag) in (((PANEL[0] + 30, PANEL[1] - 1), (CRATE[0], CRATE[1] - 2), 3),
                         ((CRATE[0] + 28, CRATE[1] - 3), (TRIPOD[0] - 6, TRIPOD[1] - 1), 4),
                         ((CRATE[0] + 20, CRATE[1] - 12), (MAST[0] - 2, MAST[1] - 1), 2)):
        n = int(max(abs(b_[0] - a[0]), abs(b_[1] - a[1]))) + 1
        for k in range(n):
            t = k / max(1, n - 1)
            px(L, round(a[0] + (b_[0] - a[0]) * t), round(a[1] + (b_[1] - a[1]) * t + sag * math.sin(math.pi * t)),
               "k0")
    # survey stakes with orange flagging and a string line along the wall foot
    for i, (x, b) in enumerate(STAKES):
        rect(L, x, b - 6, x, b, "s3"); rect(L, x + 1, b - 6, x + 2, b - 6, "o2"); rect(L, x + 1, b - 5, x + 2, b - 5, "o1")
        px(L, x, b + 1, "s0")
    for (a, b_) in zip(STAKES, STAKES[1:]):
        for k in range(0, b_[0] - a[0], 2):
            t = k / (b_[0] - a[0])
            px(L, a[0] + k, round(a[1] - 4 + (b_[1] - a[1]) * t + 1.5 * math.sin(math.pi * t)), "o1")
    return L, items


# ============================================================================ 16-19 Y-sorted sprites
def paint_mast():
    L = new()
    x, b = MAST
    rect(L, x - 4, b - 2, x + 5, b, "k1"); rect(L, x - 4, b - 2, x + 5, b - 2, "k3"); rect(L, x - 4, b, x + 5, b, "ink")
    rect(L, x, b - 66, x, b - 3, "k3"); rect(L, x + 1, b - 66, x + 1, b - 3, "k1")
    for y in range(b - 60, b - 3, 8):
        px(L, x - 1, y, "k2"); px(L, x + 2, y, "k2")
    rect(L, x - 6, b - 62, x + 7, b - 62, "k2"); rect(L, x - 4, b - 56, x + 5, b - 56, "k2")
    for dx in (-6, 7):
        rect(L, x + dx, b - 64, x + dx, b - 61, "k3")
    stamp(L, x + 2, b - 50, [".kk.", "kKKk", "kKHk", "kKKk", ".kk."], {"k": "k1", "K": "k3", "H": "k4"})
    rect(L, x - 1, b - 69, x + 2, b - 67, "k0"); rect(L, x, b - 69, x + 1, b - 68, "t2")
    px(L, x, b - 70, "t1")
    rect(L, x - 2, b - 30, x + 3, b - 26, "k2"); rect(L, x - 1, b - 29, x + 2, b - 28, "t1")
    for (gx, gy) in ((x - 18, b + 2), (x + 18, b - 2)):
        line(L, x, b - 58, gx, gy, "k3")
    return L


def paint_tripod():
    L = new()
    x, b = TRIPOD
    head_y = b - 40
    for (fx, fy) in ((x - 12, b), (x + 12, b), (x + 1, b - 4)):
        line(L, x, head_y + 10, fx, fy, "k2")
        line(L, x + (1 if fx > x else -1 if fx < x else 1), head_y + 10, fx + (1 if fx > x else 0), fy, "k3")
        rect(L, fx - 1, fy, fx + 1, fy, "ink")
    stamp(L, x - 6, head_y - 2, ["...kkkkkk...", "..kKKHHKKk..", ".kKHHHHHKKk.", "kKKKKKKKKKKk",
                                 "kKk.tTTt.kKk", "kKk.t22t.kKk", "kKKKKKKKKKKk", ".kkkkkkkkkk.",
                                 "....kKKk....", "....kKKk....", "...kkkkkk..."],
          {"k": "k0", "K": "k2", "H": "k3", "t": "t0", "T": "t1", "2": "t2"})
    px(L, x + 6, head_y + 1, "o1")
    return L


def paint_beacon():
    L = new()
    x, b = BEACON
    rect(L, x - 5, b - 3, x + 5, b, "k1"); rect(L, x - 5, b - 3, x + 5, b - 3, "k3"); rect(L, x - 5, b, x + 5, b, "ink")
    for xx in (x - 4, x + 4):
        px(L, xx, b - 2, "k4")
    for y in range(b - 34, b - 3):
        rect(L, x - 2, y, x - 2, y, "k3"); rect(L, x - 1, y, x + 1, y, "k2"); rect(L, x + 2, y, x + 2, y, "k1")
    for y in (b - 26, b - 18):
        rect(L, x - 2, y, x + 2, y + 1, "o1"); px(L, x - 2, y, "o2")
    rect(L, x - 3, b - 40, x + 3, b - 35, "k1")
    rect(L, x - 2, b - 39, x + 2, b - 36, "r1"); rect(L, x - 1, b - 38, x, b - 37, "r2")
    rect(L, x - 2, b - 42, x + 2, b - 41, "k3"); px(L, x, b - 43, "k4")
    return L


ELM_LOBES = [  # hand-placed, overlapping: back/top row, middle, lower, bottom fringe (z-buffered: lower = nearer)
    (10, -8, 30), (52, -12, 30), (98, -6, 28), (142, 6, 24), (182, 20, 18), (214, 34, 11),
    (-6, 26, 26), (32, 22, 28), (76, 26, 27), (120, 36, 22), (158, 48, 16), (192, 56, 10),
    (2, 64, 24), (40, 68, 23), (82, 66, 19), (116, 76, 13), (146, 82, 9),
    (-8, 100, 18), (22, 102, 15), (54, 96, 12), (84, 92, 8)]
ELM_HOLES = [(128, 24, 4, 2), (166, 40, 3, 2), (100, 86, 4, 2)]


def paint_elm():
    """Old American elm rooted in the plaza turf at the left edge (heroine scale): fissured trunk lit from the
    left, a limb reaching right into the frame, leaf-cluster crown framing the top-left sky and the Senate wing."""
    L = new()
    x, b = ELM
    for y in range(0, b + 1):
        t = y / b
        hw = 13 + int(5 * t * t)
        if y > b - 8:
            hw += (y - (b - 8)) * 2
        for xx in range(x - hw, x + hw + 1):
            u = (xx - (x - hw)) / (2 * hw)
            c = "b3" if u < 0.22 else ("b2" if u < 0.55 else ("b1" if u < 0.86 else "b0"))
            if hval("fiss", xx, y // 4) < 0.16 and 0.15 < u < 0.9:
                c = "b0" if u > 0.5 else "b1"
            if hval("lich", xx // 2, y // 3) < 0.05 and u < 0.6:
                c = "mo1"
            px(L, xx, y, c)
    for (rx, rl) in ((-30, 10), (30, 14), (-16, 6), (20, 9)):     # surface roots
        for k in range(rl):
            px(L, x + rx + (k if rx > 0 else -k), b - 1 + k // 4, "b2" if k % 3 else "b1")
            px(L, x + rx + (k if rx > 0 else -k), b + k // 4, "b0")
    for k in range(70):                                              # limb into the frame
        yy = 98 - int(k * 0.55) + int(3 * math.sin(k / 9))
        th = 5 if k < 30 else (4 if k < 50 else 3)
        for j in range(th):
            px(L, x + 12 + k, yy + j, "b2" if j == 0 else ("b1" if j < th - 1 else "b0"))
    for (a, b_) in (((118, 72), (198, 50)), ((150, 64), (214, 38)), ((104, 46), (184, 22)), ((136, 80), (176, 72))):
        line(L, a[0], a[1], b_[0], b_[1], "b1"); line(L, a[0], a[1] + 1, b_[0], b_[1] + 1, "b0")
    crown_lobes(L, cluster_lobes(ELM_LOBES, "elm"), NEAR, NEAR_CUTS, "elm", squash=0.85, gain=1.0, leaf=3,
                holes=ELM_HOLES, clumps=None)
    return L


# ============================================================================ 20 foreground (over actors)
def paint_fg():
    L = new()
    items = {}
    x0, b = FG_BALUSTRADE
    reg = np.zeros((H, W), bool)
    rect(L, x0, b - 15, x0 + 98, b, "m4", reg); rect(L, x0, b - 15, x0 + 98, b - 14, "m5", reg)
    rect(L, x0 + 95, b - 13, x0 + 98, b, "gr2", reg)
    for y in range(b - 10, b + 1, 4):
        rect(L, x0, y, x0 + 94, y, "m3", reg)
    for (cx_, cl_) in ((30, 6), (64, 9)):                                # cracks through the plinth
        for j in range(cl_):
            px(L, x0 + cx_ + (j % 3) - 1, b - 14 + j, "gr2", reg)
    bal = [".mmm.", "mMMMm", "MMMmm", ".mMm.", "..m..", ".mMm.", "mMMMm", "MMMMm", "MMMmm", "mMMmm", ".mMm.",
           "..m..", ".mmm.", "mmmmm"]
    for bx in (6, 22, 38, 54):
        stamp(L, x0 + bx, b - 29, bal, {"m": "m3", "M": "m5"}, reg)
    stamp(L, x0 + 70, b - 22, bal[7:], {"m": "m3", "M": "m5"}, reg)       # broken baluster stub
    rect(L, x0, b - 33, x0 + 60, b - 30, "m4", reg); rect(L, x0, b - 33, x0 + 60, b - 33, "m6", reg)
    rect(L, x0 + 58, b - 32, x0 + 60, b - 30, "gr2", reg); px(L, x0 + 61, b - 31, "m3", reg)
    stamp(L, x0 + 78, b - 20, ["..mm..", ".mMMm.", "mMMMm.", "mMMm..", ".mm..."], {"m": "m3", "M": "m4"}, reg)
    for k in range(30):                                                  # ivy over the plinth and rail
        xx = x0 + 2 + int(hval("fgivy", k) * 90); yy = b - 14 + int(hval("fgivyy", k) * 13)
        if k < 8:
            yy = b - 33 + int(hval("fgivyy", k) * 4); xx = x0 + int(hval("fgivy", k) * 40)
        rect(L, xx, yy, xx + 1, yy, "f3", reg); px(L, xx, yy + 1, "f2", reg); px(L, xx + 1, yy - 1, "f4", reg)
    items["fg_balustrade"] = {"mask": reg, "base": b}
    x0, b = FG_BLOCK
    reg = np.zeros((H, W), bool)
    rect(L, x0, b - 22, W - 1, b, "gr3", reg); rect(L, x0, b - 22, W - 1, b - 19, "gr4", reg)
    rect(L, x0, b - 22, W - 1, b - 22, "gr5", reg)
    rect(L, x0, b - 11, W - 1, b - 11, "gr2", reg)
    crown_lobes(L, [(x0 + 6, b - 24, 9), (x0 + 22, b - 30, 11), (x0 + 40, b - 26, 10), (x0 + 52, b - 16, 9),
                    (x0 + 14, b - 12, 7)], NEAR, NEAR_CUTS, "fgfern", reg, squash=0.7, leaf=2)
    items["fg_block"] = {"mask": reg, "base": b}
    for (cx, w_) in ((96, 34), (520, 30)):                            # tall edge grass at the bottom
        for k in range(w_):
            if hval("fgg", cx, k) < 0.55:
                xx = cx + k
                hgt = 4 + int(hval("fggh", cx, k) * 8)
                for j in range(hgt):
                    px(L, xx + (j // 4 if k % 2 else -(j // 5)), H - 1 - j, "g4" if j > hgt - 3 else "g2")
    return L, items


# ============================================================================ 13 cast shadows
SUN_DX, SUN_DY = 0.55, -0.30          # shadow offset per px of object height (sun behind the viewer's left)


def paint_shadows(below):
    sm = np.zeros((H, W), bool)
    x, b = ELM
    sm |= seg((x, b), (x + 0.55 * 70, b - 0.30 * 70), 14)
    dap = np.zeros((H, W), bool)
    for (cx, cy, rx, ry) in ((140, 240, 70, 14), (230, 236, 46, 10), (86, 262, 40, 10)):
        dap |= ell(cx, cy, rx, ry)
    sm |= dap & (vnoise("dapple", 6) > 0.45)
    x, b = MAST
    sm |= seg((x, b), (x + 66 * SUN_DX, b + 66 * SUN_DY), 0.8)
    x, b = TRIPOD
    sm |= seg((x, b), (x + 40 * SUN_DX, b + 40 * SUN_DY), 1.2)
    sm |= ell(x + 40 * SUN_DX, b + 40 * SUN_DY, 6, 3)
    x, b = BEACON
    sm |= seg((x, b), (x + 42 * SUN_DX, b + 42 * SUN_DY), 2.2)
    x, b = CRATE
    sm |= box(x + 6, b - 15, x + 36, b - 12) | box(x + 29, b - 12, x + 34, b)
    x, b = PANEL
    sm |= box(x + 10, b - 8, x + 40, b - 3)
    for (x0, x1) in CHEEKS:
        sm |= box(x1 + 1, 223, x1 + 8, 228)
    for (xr, br, w, h, kind, t) in RUBBLE:
        sm |= box(xr + w, br - int(h * 0.3), xr + w + int(h * 0.55), br)
    deep = np.zeros((H, W), bool)
    for grp in OFFSCREEN_SHADE:
        dm = np.zeros((H, W), bool)
        for (cx, cy, rx, ry) in grp:
            dm |= ell(cx, cy, rx, ry)
        dn = vnoise(("offshade", grp[0][0]), 5)
        sm |= dm & (dn > 0.36)
        deep |= dm & (dn > 0.52)
    sm &= (YY >= WALL_FOOT[None, :]) & ~box(CHEEKS[0][0], 0, CHEEKS[1][1], 222)
    deep &= sm
    L = new()
    L[sm] = SHADE_LUT[np.clip(below[sm], 0, None)]
    L[deep] = SHADE_LUT[L[deep]]
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
    m = plaza_masks()
    area = (m["ground"] | m["steps"]).copy()
    area &= ~box(CHEEKS[0][0], 0, CHEEKS[0][1], 222) & ~box(CHEEKS[1][0], 0, CHEEKS[1][1], 222)
    area &= (YY >= 203)
    # side margins: only the exit lanes reach the frame edge
    edge_ok = np.zeros((H, W), bool)
    for k, e in EXITS.items():
        x0, y0, x1, y1 = e["rect"]
        edge_ok |= box(x0, y0, x1, y1)
    area &= (XX >= 6) & (XX <= W - 7) | edge_ok
    area &= (YY <= H - 2) | edge_ok
    wk = erode(area | ~box(0, 0, W - 1, H - 1), 4, 2) & area
    wk |= area & edge_ok
    collars = {}
    for name, it in items.items():           # derived collar: feet north of the base whose sprite overlaps the item
        ov = overlap_feet(it["mask"], spr_alpha)
        col = ov & (YY < it["base"])
        ys, xs = np.nonzero(it["mask"])
        foot = box(xs.min() - 4, max(it["base"] - 5, ys.min()), xs.max() + 4, it["base"] + 3)
        collars[name] = col | foot
        wk &= ~collars[name]
    # Y-sorted objects: footprint collars only (the Y-sort resolves in front / behind)
    feet = {"mast_foot": (MAST, 6, 4), "tripod_feet": (TRIPOD, 14, 5), "beacon_foot": (BEACON, 7, 4),
            "elm_trunk": ((ELM[0], ELM[1]), 34, 6)}
    for name, ((x, b), half, up) in feet.items():
        c = box(x - half - 3, b - up, x + half + 3, b + 3)
        collars[name] = c
        wk &= ~c
    # elm trunk column: north of the base the trunk itself is solid
    collars["elm_trunk"] |= box(0, 0, ELM[0] + 20, ELM[1])
    wk &= ~collars["elm_trunk"]
    return wk, collars


def visibility(walk, rgba, spr_alpha, step=2):
    fg = rgba["fg-occlusion"][..., 3] == 255
    ys = {n: rgba[n][..., 3] == 255 for n in YSORT_LAYERS}
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
            if y0 < 0:
                continue
            xa, xb = max(0, x0), min(W, x0 + sw)
            vis_px = (o[y0:y0 + sh, xa:xb] & spr_alpha[:, xa - x0:xb - x0]).sum()
            vis = 1 - vis_px / tot
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


def _line_pts(a, b):
    (x0, y0), (x1, y1) = a, b
    n = max(abs(x1 - x0), abs(y1 - y0))
    return [(int(round(x0 + (x1 - x0) * k / n)), int(round(y0 + (y1 - y0) * k / n))) for k in range(1, n + 1)]


def _bfs(walk, a, b, pad=90):
    """8-connected shortest path on the walk mask inside a padded window around a..b (fallback only)."""
    from collections import deque
    x0, x1 = max(0, min(a[0], b[0]) - pad), min(W - 1, max(a[0], b[0]) + pad)
    y0, y1 = max(0, min(a[1], b[1]) - pad), min(H - 1, max(a[1], b[1]) + pad)
    prev = {a: None}
    q = deque([a])
    while q:
        c = q.popleft()
        if c == b:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = c[0] + dx, c[1] + dy
            if x0 <= nx <= x1 and y0 <= ny <= y1 and (nx, ny) not in prev and walk[ny, nx]:
                prev[(nx, ny)] = c
                q.append((nx, ny))
    if b not in prev:
        return None
    path, c = [], b
    while c != a:
        path.append(c); c = prev[c]
    return path[::-1]


ROUTE_INFO = {}


def route_points(walk=None):
    """Heroine route through the hand-picked ROUTE waypoints: straight 1-px steps; only where a straight segment
    would cross a blocked texel (and a mask is given) a local 8-connected shortest path is used instead. The number of
    such detours is reported."""
    pts = [PINS[p] if isinstance(p, str) else p for p in ROUTE]
    out = [pts[0]]
    detours = []
    for a, b in zip(pts, pts[1:]):
        seg_pts = _line_pts(a, b)
        if walk is not None and any(not walk[y, x] for (x, y) in seg_pts):
            alt = _bfs(walk, a, b)
            if alt is not None:
                detours.append([list(a), list(b)])
                seg_pts = alt
        out.extend(seg_pts)
    ROUTE_INFO["detours"] = detours
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
    layers = {"sky": paint_sky(), "clouds": paint_clouds(), "capitol-dome": paint_dome()}
    front = paint_west_front()
    void = house_void()
    front[void] = -1
    layers["capitol-west-front"] = front
    ruin = paint_capitol_ruin(front)
    ruin[void & (ruin >= 0) & (YY < np.interp(np.arange(W), [p[0] for p in HOUSE_COLLAPSE],
                                              [p[1] for p in HOUSE_COLLAPSE])[None, :].repeat(H, 0))] = -1
    layers["capitol-ruin"] = ruin
    layers["olmsted-terrace"] = paint_terrace()
    layers["west-lawn"] = paint_west_lawn()
    layers["grounds-trees"] = paint_grounds_trees()
    layers["lawn-edge-planting"] = paint_lawn_edge()
    layers["seat-wall-steps"] = paint_seat_wall()
    layers["plaza-ground"] = paint_plaza_ground()
    layers["ground-detail"] = paint_ground_detail()
    below = composite_idx(layers, list(layers))
    layers["cast-shadows"] = paint_shadows(below)
    layers["rubble-collapse"], items = paint_rubble()
    layers["props-low"], pitems = paint_props()
    items.update(pitems)
    layers["survey-mast-ysort"] = paint_mast()
    layers["survey-tripod-ysort"] = paint_tripod()
    layers["beacon-ysort"] = paint_beacon()
    layers["elm-ysort"] = paint_elm()
    layers["fg-occlusion"], fitems = paint_fg()
    for k, v in fitems.items():
        items[k] = {"mask": v["mask"], "base": H + 40, "fg": True}      # always over the actor: never wrong-order
    # base-layer architecture the actor must never stand behind (seat wall, cheek piers)
    wall = layers["seat-wall-steps"] >= 0
    for i, (x0, x1) in enumerate(CHEEKS):
        items[f"cheek_{i}"] = {"mask": wall & box(x0 - 1, 150, x1 + 1, 222), "base": 222}
    despeckled = despeckle_ground(layers)
    walk, collars = walkable({k: v for k, v in items.items() if not v.get("fg")}, spr_alpha)
    for k, v in fitems.items():                                       # fg footprints on the ground plane
        collars[k] = box(*FG_FOOTPRINTS[k])
        walk &= ~collars[k]
    layers["guides"] = paint_guides(walk, collars)
    return {"layers": layers, "items": items, "walk": walk, "collars": collars, "spr": spr, "spr_alpha": spr_alpha,
            "despeckled_ground_texels": despeckled}


def bbox_of(mask):
    ys, xs = np.nonzero(mask)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


GROUND_LAYERS = ("plaza-ground", "ground-detail", "cast-shadows")


def despeckle_ground(layers, passes=3):
    """A ground texel left brighter than all 8 neighbours by >= 40 luma takes its darkest neighbour's colour.
    Only the walkable-plane ground layers are edited; sprites and architecture are never touched."""
    fixed = 0
    for _ in range(passes):
        flat = composite_idx(layers, ART_LAYERS)
        l = LUMA[np.clip(flat, 0, None)]
        p = np.pad(l, 1, mode="edge")
        pi = np.pad(flat, 1, mode="edge")
        nbs = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0)]
        nb = np.stack([p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] for dy, dx in nbs])
        nbi = np.stack([pi[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] for dy, dx in nbs])
        iso = (l - nb.max(0) >= 40) & (YY >= 200)
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
            if y >= 196:
                L[y, x] = I["gd-walk"] if walk[y, x] else I["gd-block"]
    for k, e in EXITS.items():
        x0, y0, x1, y1 = e["rect"]
        for x in range(x0, x1 + 1):
            px(L, x, y0, "gd-exit"); px(L, x, y1, "gd-exit")
        for y in range(y0, y1 + 1):
            px(L, x0, y, "gd-exit"); px(L, x1, y, "gd-exit")
    for k, e in INTERACTIONS.items():
        x0, y0, x1, y1 = e["rect"]
        for x in range(x0, x1 + 1, 2):
            px(L, x, y0, "gd-act"); px(L, x, y1, "gd-act")
    for k, (x, y) in PINS.items():
        rect(L, x - 1, y - 1, x + 1, y + 1, "gd-pin")
    for (x, y) in route_points(walk)[::3]:
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


ACTOR_SHADOW = (3, -1, 9.0, 2.6)      # proposed actor contact shadow: offset (sun behind-left) and radii, px
_RGB_KEY = {int(r) << 16 | int(g) << 8 | int(b): i for i, (r, g, b) in enumerate(RGB[:N_ART].tolist())}


def shadow_patch(base, foot):
    """Opaque contact shadow under the actor: the ground texels inside a small ellipse take their SHADE colour (no
    semi-alpha). Returns (x0, y0, patch RGBA)."""
    dx, dy, rx, ry = ACTOR_SHADOW
    cx, cy = foot[0] + dx, foot[1] + dy
    x0, y0 = int(math.floor(cx - rx)), int(math.floor(cy - ry))
    w, h = int(2 * rx) + 2, int(2 * ry) + 2
    patch = np.zeros((h, w, 4), np.uint8)
    for j in range(h):
        for i in range(w):
            x, y = x0 + i, y0 + j
            if not (0 <= x < W and 0 <= y < H):
                continue
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 > 1.0:
                continue
            r_, g_, b_ = (int(v) for v in base[y, x, :3])
            k = _RGB_KEY.get(r_ << 16 | g_ << 8 | b_)
            if k is None:
                continue
            core = ((x + 0.5 - cx) / (rx * 0.62)) ** 2 + ((y + 0.5 - cy) / (ry * 0.62)) ** 2 <= 1.0
            patch[j, i, :3] = RGB[SHADE_LUT[SHADE_LUT[k]] if core else SHADE_LUT[k]]
            patch[j, i, 3] = 255
    return x0, y0, patch


def blit(dst, x0, y0, patch):
    h, w = patch.shape[:2]
    for j in range(h):
        for i in range(w):
            if patch[j, i, 3] and 0 <= x0 + i < W and 0 <= y0 + j < H:
                dst[y0 + j, x0 + i] = patch[j, i]


def runtime_stack_still(rgba, spr, foot, shadow=True):
    """Runtime draw order proposal: base (layers 1-15 merged) -> actor contact shadow (shaded ground texels, a
    proposal, not approved art) -> Y-sorted {4 sprite layers, actor} by pivot row (a sprite layer is drawn over the
    actor when the actor's foot row is north of its pivot) -> fg-occlusion."""
    out = composite_rgba(rgba, BASE_LAYERS)
    if shadow:
        blit(out, *shadow_patch(out, foot))
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
DT = (2026, 10, 16, 5, 51, 58)


def zput(z, name, payload, method=zipfile.ZIP_DEFLATED):
    zi = zipfile.ZipInfo(name, DT)
    zi.compress_type = method
    z.writestr(zi, payload)


def make_ora(rgba, comp_png, layers=None):
    layers = layers or LAYERS
    stack = ['<?xml version="1.0" encoding="UTF-8"?>',
             f'<image version="0.0.5" w="{W}" h="{H}" xres="72" yres="72">', "<stack>"]
    for n in reversed(layers):
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
        for n in layers:
            zput(z, f"data/{n}.png", png_bytes(rgba[n]) if isinstance(rgba[n], np.ndarray) else rgba[n])
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
    c = flat[..., 0].astype(np.int32) << 16 | flat[..., 1].astype(np.int32) << 8 | flat[..., 2]
    p = np.pad(c, 1, mode="edge")
    same = np.zeros((H, W), bool)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        same |= p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] == c
    iso = ~same & region
    return round(float(iso.sum()) / max(1, int(region.sum())), 4)


def flat_index(flat):
    key = flat[..., 0].astype(np.int64) << 16 | flat[..., 1].astype(np.int64) << 8 | flat[..., 2]
    pal = RGB[:, 0].astype(np.int64) << 16 | RGB[:, 1].astype(np.int64) << 8 | RGB[:, 2]
    lut = {int(k): i for i, k in enumerate(pal)}
    u, inv = np.unique(key, return_inverse=True)
    m = np.array([lut.get(int(k), 255) for k in u], np.int64)
    return m[inv].reshape(key.shape)


def repetition_stats(flat_idx, size=16, stride=2, min_colours=4):
    """Share of informative size x size windows whose exact content recurs >= size px away (same metric as the v04
    tool's repetition_stats, so the numbers are comparable)."""
    idx = (flat_idx + 1).astype(np.uint8)
    win = np.lib.stride_tricks.sliding_window_view(idx, (size, size))[::stride, ::stride]
    gy, gx = win.shape[:2]
    flatw = win.reshape(gy * gx, size * size)
    srt = np.sort(flatw, axis=1)
    ncol = 1 + (np.diff(srt.astype(np.int16), axis=1) != 0).sum(axis=1)
    inf = ncol >= min_colours
    rng = np.random.default_rng(12345)
    w1 = rng.random(size * size); w2 = rng.random(size * size)
    h1 = flatw @ w1; h2 = flatw @ w2
    keys = np.round(h1, 6) * 1e3 + np.round(h2, 6)
    pos_y = np.repeat(np.arange(gy) * stride, gx); pos_x = np.tile(np.arange(gx) * stride, gy)
    order = np.argsort(keys[inf], kind="stable")
    k_ = keys[inf][order]; py_ = pos_y[inf][order]; px_ = pos_x[inf][order]
    rep = np.zeros(len(k_), bool)
    start = 0
    for i in range(1, len(k_) + 1):
        if i == len(k_) or k_[i] != k_[start]:
            if i - start > 1:
                if np.ptp(py_[start:i]) >= size or np.ptp(px_[start:i]) >= size:
                    rep[start:i] = True
            start = i
    return {"windows": int(inf.sum()), "repeated_windows": int(rep.sum()),
            "repeated_share": round(float(rep.mean()) if len(rep) else 0.0, 4)}


def landmark_metrics(layers):
    cap = np.zeros((H, W), bool)
    for n in ("capitol-dome", "capitol-west-front", "capitol-ruin", "olmsted-terrace"):
        cap |= layers[n] >= 0
    flat = composite_idx(layers, ART_LAYERS)
    vis = np.zeros((H, W), bool)
    for n in ("capitol-dome", "capitol-west-front", "capitol-ruin", "olmsted-terrace"):
        vis |= (layers[n] >= 0) & (flat == layers[n])
    dome = layers["capitol-dome"] >= 0
    dome_vis = dome & (flat == layers["capitol-dome"])
    x0, y0, x1, y1 = bbox_of(cap & (YY < 164))
    dx0, dy0, dx1, dy1 = bbox_of(dome)
    return {"capitol_bbox_rows": [y0, y1], "capitol_bbox_cols": [x0, x1],
            "capitol_height_share_of_frame": round((y1 - y0 + 1) / H, 3),
            "capitol_visible_texels": int(vis.sum()), "capitol_visible_share_of_frame": round(vis.mean(), 3),
            "dome_bbox": [dx0, dy0, dx1, dy1], "dome_visible_share": round(dome_vis.sum() / max(1, dome.sum()), 3),
            "dome_texels_visible": int(dome_vis.sum()),
            "statue_tip_row": int(np.nonzero(dome.any(1))[0].min())}


def static_checks(sc, rgba, flat):
    layers, walk, spr = sc["layers"], sc["walk"], sc["spr"]
    v = {}
    v["canvas_640x360_all_layers"] = all(rgba[n].shape == (H, W, 4) for n in LAYERS)
    v["base_layer_opaque"] = bool((rgba["sky"][..., 3] == 255).all())
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
    da = depth_audit({k: it for k, it in sc["items"].items() if not it.get("fg")}, walk, sc["spr_alpha"])
    v["depth_audit_zero_wrong_order_feet"] = all(d["wrong_order_feet"] == 0 for d in da.values())
    v["walkable_never_in_backdrop"] = not bool(walk[:203].any())
    m = plaza_masks()
    v["walkable_only_on_plaza_ground_or_steps"] = not bool((walk & ~(m["ground"] | m["steps"])).any())
    ys_ok = {}
    for key, layer, behind in YSORT_CASES:
        foot = PINS[key]
        st = runtime_stack_still(rgba, spr, foot)
        sm = rgba[layer][..., 3] == 255
        hm = np.zeros((H, W), bool)
        sh, sw = spr.shape[:2]
        x0, y0 = foot[0] - sw // 2, foot[1] - sh + 1
        sub = spr[..., 3] == 255
        xa, xb = max(0, x0), min(W, x0 + sw)
        hm[y0:y0 + sh, xa:xb] = sub[:, xa - x0:xb - x0]
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
    rpts = route_points(walk)
    blocked = [p for p in rpts if not walk[p[1], p[0]]]
    v["heroine_route_fully_walkable"] = not blocked
    probes = {k: bool(walk[y, x]) for k, (x, y) in COLLISION_PROBES.items()}
    v["collision_probes_all_blocked"] = not any(probes.values())
    ex_ok = {}
    for k, e in EXITS.items():
        x0, y0, x1, y1 = e["rect"]
        z = box(x0, y0, x1, y1) & walk & reach
        ex_ok[k] = int(z.sum())
    v["every_exit_zone_reachable"] = all(n > 0 for n in ex_ok.values())
    act_ok = {}
    for k, a in INTERACTIONS.items():
        x0, y0, x1, y1 = a["rect"]
        px_, py_ = PINS[a["pin"]]
        act_ok[k] = bool(x0 <= px_ <= x1 and y0 <= py_ <= y1 and reach[py_, px_])
    v["every_interaction_pin_inside_its_zone_and_reachable"] = all(act_ok.values())
    top = np.full((H, W), -1, np.int16)
    for i, n in enumerate(ART_LAYERS):
        top[layers[n] >= 0] = i
    ground_top = np.isin(top, [ART_LAYERS.index(n) for n in GROUND_LAYERS])
    fl_walk, fl_ex = isolated_bright(flat, dilate(walk, 3) & ground_top)
    fl_props, fl_props_ex = isolated_bright(flat, dilate(walk, 3) & ~ground_top)
    fl_all, _ = isolated_bright(flat)
    v["no_isolated_bright_flecks_on_walkable_ground"] = fl_walk == 0
    lm = landmark_metrics(layers)
    v["capitol_landmark_in_camera_ge_40pct_height"] = lm["capitol_height_share_of_frame"] >= 0.40
    v["dome_and_statue_fully_in_frame"] = bool(lm["statue_tip_row"] >= 2 and lm["dome_visible_share"] >= 0.97)
    rep = repetition_stats(flat_index(flat))
    return {"verdicts": v, "visibility_worst": round(float(worst), 3), "visibility_worst_at": worst_at,
            "visibility_fail_count": len(fails), "visibility_fail_examples": fails[:10], "depth_audit": da,
            "ysort_cases": ys_ok, "pins_reachable": pins_ok, "route_points": len(rpts),
            "route_blocked_examples": blocked[:10], "route_detour_segments": ROUTE_INFO.get("detours"),
            "collision_probes_walkable": probes,
            "exit_zone_walkable_texels": ex_ok, "interaction_zones_ok": act_ok,
            "isolated_bright_flecks": {"ground_layers_near_walkable": fl_walk, "examples": fl_ex,
                                       "deliberate_prop_highlights_near_walkable": fl_props,
                                       "prop_highlight_examples": fl_props_ex,
                                       "whole_frame": fl_all},
            "single_texel_colour_islands_share": {"plane_rows_200_359": single_texel_islands(flat, YY >= 200),
                                                  "backdrop_rows_0_199": single_texel_islands(flat, YY < 200)},
            "repetition_16px_windows": rep, "landmark": lm,
            "palette": {"art_colours": N_ART, "used_in_flat": len(flat_cols)},
            "despeckled_ground_texels": sc["despeckled_ground_texels"],
            "walkable_texels": int(walk.sum())}


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
    nl = len(LAYERS)
    d = {"pxo": fname(f"scene-{nl}layer", "pxo"), "ora": fname(f"scene-{nl}layer", "ora"),
         "gpl": fname("scene-palette", "gpl"), "walk": fname("scene-walkability", "json"),
         "walkmask": fname("scene-walkmask", "png"), "flat": fname("scene-flat-640x360", "png"),
         "manifest": fname("scene-manifest", "json"), "report": fname("technical-check-report", "json")}
    for k in CAPTURES:
        d[f"cap1280_{k}"] = fname(f"godot-1280x720-{k}", "png")
        d[f"cap640_{k}"] = fname(f"godot-640x360-{k}", "png")
    return d


def walkability_json(sc):
    walk = sc["walk"]
    cells = []
    for cy in range(0, H, 8):
        row = ""
        for cx in range(0, W, 8):
            c = walk[cy:cy + 8, cx:cx + 8]
            row += "1" if c.all() else ("p" if c.any() else "0")
        cells.append(row)
    return {"candidate": RUN, "status": "UNAPPROVED test-only candidate; not wired to any runtime scene",
            "canvas": [W, H], "grid_px": 8,
            "cells_legend": {"1": "every foot texel walkable", "p": "partly walkable", "0": "not walkable"},
            "cells_rows_top_to_bottom": cells,
            "collision_mask_png": names()["walkmask"], "foot_rule": "a foot texel is walkable iff the mask is opaque",
            "pins": {k: list(v) for k, v in PINS.items()},
            "exits": EXITS, "interactions": INTERACTIONS,
            "ysort_pivots": YSORT_PIVOTS,
            "runtime_draw_order_proposal": "base (layers 1-15 merged) -> Y-sorted {4 *-ysort layers, actor} by pivot "
                                           "row (actor last on ties) -> fg-occlusion",
            "collars_blocked_texels": {k: int((v & ~walk).sum()) for k, v in sc["collars"].items()},
            "collision_probes_must_be_blocked": {k: list(v) for k, v in COLLISION_PROBES.items()},
            "heroine_route_waypoints": [PINS[p] if isinstance(p, str) else p for p in ROUTE],
            "heroine_route_rule": "1-px straight steps between waypoints; a local 8-connected shortest path only "
                                  "where a straight step would hit a blocked texel"}


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
    for key in set(CAPTURES.values()) | {"elm_behind", "mast_behind", "beacon_behind", "steps_mid"}:
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
        "project": SLUG, "area": AREA, "run": RUN, "version": "v05",
        "status": "UNAPPROVED test-only walkable candidate (one 640x360 camera composition). Not accepted art, not "
                  "runtime-integrated. Acceptance is creator review only; science scene art stays 0/11.",
        "art_approved": False, "runtime_integrated": False, "counters_changed": False,
        "authoring_route": {
            "method": "deterministic Python tool with hand-written placement tables, authored and run by Claude "
                      "(Claude Code, claude.ai Max subscription, firstParty; no API key, no image model, no paid "
                      "fallback); writes a native pxo_version 7 .pxo and an .ora with named layers",
            "pixelorama_gui_paint_pass": False,
            "disclosure": "no desktop/computer-use access to the Pixelorama GUI in this session",
            "references": "Architect of the Capitol dome and Olmsted Terrace pages (forms only, read as text facts "
                          "in prior QA); v02 vista and the nonruntime concept were looked at for composition only; "
                          "no pixel of either is used",
            "audit_reference": AUDIT_REL},
        "read_only_predecessors_lock": LOCK,
        "canvas": {"w": W, "h": H, "camera": "one 640x360 logical viewport (window 1280x720, integer 2x); top = "
                   "east (the Capitol), bottom = west (toward Union Square)",
                   "scale_reference": {"file": HEROINE_REL, "logical_height_px": int(sc["spr"].shape[0])},
                   "depth_model": {"backdrop_pinhole": {"F_px": F, "eye_m": EYE, "horizon_row": HZ,
                                                        "lawn_rise_m": 7.0},
                                   "walkable_plane": "game 3/4 at 28 px/m (scale of the backdrop at d = 20 m)",
                                   "table": DEPTH_TABLE}},
        "layers_bottom_to_top": [
            {"index": i + 1, "name": n, "visible": n != "guides", "locked": n == "guides",
             "runtime_export": ("merged into base" if n in BASE_LAYERS else
                                f"Y-sorted sprite layer, pivot row {YSORT_PIVOTS[n]}" if n in YSORT_PIVOTS else
                                "overlay above actors" if n == "fg-occlusion" else "never exported (hidden guides)"),
             "opaque_texels": int((rgba[n][..., 3] == 255).sum())} for i, n in enumerate(LAYERS)],
        "palette": [{"name": n, "hex": "#" + h} for n, h in PALETTE],
        "guide_palette": [{"name": n, "hex": "#" + h} for n, h in GUIDE_PALETTE],
        "pins": {k: list(v) for k, v in PINS.items()}, "exits": EXITS, "interactions": INTERACTIONS,
        "static_checks": rep,
        "files_sha256_bytes": {nm[k]: sha(v) for k, v in files.items()},
        "tool": {"file": TOOL_REL, "sha256_text_lf_v1": sha_text(read_bytes(os.path.abspath(__file__))),
                 "python": sys.version.split()[0], "pillow": Image.__version__, "numpy": np.__version__},
    }


def longest_path():
    nm = names()
    ps = [os.path.join(rp(CAND_REL), nm[k]) for k in ("pxo", "ora", "gpl", "walk", "walkmask", "flat", "manifest")]
    ps += [os.path.join(rp(OUT_REL), nm[k]) for k in nm if k.startswith("cap") or k == "report"]
    return max(len(os.path.abspath(p)) for p in ps)


def build():
    if longest_path() > 255:
        raise SystemExit(f"candidate path too long: {longest_path()}")
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


# ============================================================================ predecessor lock
TEXT_EXT = (".md", ".py", ".json", ".gpl", ".gd", ".txt")


def _file_digest(p):
    b = read_bytes(p)
    if p.lower().endswith(TEXT_EXT):
        return "t:" + sha_text(b)
    return "b:" + sha(b)


def lock_digest(rel):
    p = rp(rel)
    if os.path.isfile(_fs(p)):
        return _file_digest(p)
    items = []
    for d, _, fs in os.walk(_fs(p)):
        for f in fs:
            q = os.path.join(d, f)
            rel_q = os.path.relpath(q, _fs(p)).replace("\\", "/")
            items.append((rel_q, _file_digest(q.replace(WIN_LONG_PREFIX, "", 1) if q.startswith(WIN_LONG_PREFIX)
                                              else q)))
    items.sort()
    return hashlib.sha256("\n".join(f"{a} {b}" for a, b in items).encode()).hexdigest()


def lock_check():
    got = {rel: lock_digest(rel) for rel in LOCK}
    return {"entries": {rel: {"expected": LOCK[rel], "actual": got[rel], "ok": got[rel] == LOCK[rel]} for rel in LOCK},
            "all_ok": all(got[rel] == LOCK[rel] for rel in LOCK)}


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
    tmp = tempfile.mkdtemp(prefix="wb-cw5gate-")
    try:
        src = {}
        for k in ("pxo", "ora"):
            src[k] = os.path.join(tmp, f"src.{k}")
            with open(_fs(src[k]), "wb") as f:
                f.write(files[k])
        flats = []
        rt_layers = {}
        plan = (("pxo_flat_1", "pxo", False), ("pxo_flat_2", "pxo", False), ("pxo_split", "pxo", True),
                ("ora_flat", "ora", False), ("ora_split", "ora", True))
        for label, k, split in plan:
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
                    b = read_bytes(os.path.join(d, f))
                    a = decode(b)[2]
                    hit = [n for n in LAYERS if a.shape == rgba[n].shape and a.tobytes() == rgba[n].tobytes()]
                    got.append({"file": f, "exact_layer_match": hit,
                                "semi_alpha": int(((a[..., 3] > 0) & (a[..., 3] < 255)).sum())})
                    if k == "pxo" and hit:
                        rt_layers[hit[0]] = b
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
        # round trip: rebuild an .ora from Pixelorama's OWN split exports of the .pxo, export it again
        if all(n in rt_layers for n in ART_LAYERS):
            rt = dict(rt_layers)
            rt["guides"] = png_bytes(rgba["guides"])
            rt_ora = make_ora(rt, png_bytes(flat))
            p_rt = os.path.join(tmp, "roundtrip.ora")
            with open(_fs(p_rt), "wb") as f:
                f.write(rt_ora)
            d = os.path.join(tmp, "rt_flat"); os.makedirs(d)
            fake = os.path.join(tmp, "appdata_rt"); os.makedirs(fake)
            r = run_isolated(exe, ["--export", "-o", os.path.join(d, "f.png"), p_rt], fake, real_root)
            r["pngs"] = sorted(f for f in os.listdir(_fs(d)) if f.lower().endswith(".png"))
            if len(r["pngs"]) == 1:
                a = decode(read_bytes(os.path.join(d, r["pngs"][0])))[2]
                r["flat_equals_expected"] = a.shape == flat.shape and bool((a == flat).all())
            rep["steps"]["roundtrip_pxo_split_to_ora_to_flat"] = r
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
        "pixelorama_roundtrip_split_ora_flat_exact":
            st.get("roundtrip_pxo_split_to_ora_to_flat", {}).get("flat_equals_expected", False),
        "pixelorama_sources_unchanged": all(v.get("source_copy_unchanged", True) for v in st.values()),
        "pixelorama_split_does_not_export_hidden_guides": not any(st[k].get("guides_exported")
                                                                  for k in ("pxo_split", "ora_split")),
    }
    return rep


# ============================================================================ Godot gates (throwaway temp projects)
GODOT_TEXEL_SCRIPT = r'''extends SceneTree
# Test-only, nonruntime (headless): load the split layer PNGs from the .ora with Image.load_from_file, hash raw RGBA,
# walk the heroine route on the exported collision mask, probe collision points that must be blocked, check the exit
# and interaction pins, and composite a runtime-stack still (base -> Y-sorted {sprite layers, actor} by pivot row ->
# fg-occlusion) at every sampled foot; report SHA-256 per still.
func _init():
	var a = OS.get_cmdline_user_args()
	var dir: String = a[0]
	var cases = JSON.parse_string(FileAccess.get_file_as_string(dir + "/cases.json"))
	var out = {"layers": {}, "stills": {}, "probes": {}, "pins": {}}
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
	for k in cases["probes"].keys():
		var q = cases["probes"][k]
		out["probes"][k] = mask.get_pixel(int(q[0]), int(q[1])).a >= 0.5
	for k in cases["pins"].keys():
		var q = cases["pins"][k]
		out["pins"][k] = mask.get_pixel(int(q[0]), int(q[1])).a >= 0.5
	var base = imgs[cases["base_layers"][0]].duplicate()
	for i in range(1, cases["base_layers"].size()):
		base.blend_rect(imgs[cases["base_layers"][i]], Rect2i(0, 0, 640, 360), Vector2i(0, 0))
	for key in cases["feet"].keys():
		var foot = cases["feet"][key]
		var st = base.duplicate()
		var sh = Image.load_from_file(dir + "/shadow_" + key + ".png")
		sh.convert(Image.FORMAT_RGBA8)
		var so = cases["shadow_origin"][key]
		st.blend_rect(sh, Rect2i(0, 0, sh.get_width(), sh.get_height()), Vector2i(int(so[0]), int(so[1])))
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
# holding the Y-sorted layers (position.y = pivot, offset.y = -pivot) and the heroine (position = foot, added last so
# she wins ties), then the fg-occlusion overlay. Nearest filtering. Captures the root viewport at each foot.
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
	var shadow = Sprite2D.new()
	shadow.centered = false
	world.add_child(shadow)
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
		shadow.texture = ImageTexture.create_from_image(Image.load_from_file(dir + "/shadow_" + key + ".png"))
		var so = cases["shadow_origin"][key]
		shadow.position = Vector2(int(so[0]), int(so[1]))
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
window/size/window_width_override={ww}
window/size/window_height_override={wh}
window/stretch/mode="canvas_items"
window/stretch/scale_mode="integer"

[rendering]
renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
textures/canvas_textures/default_texture_filter=0
"""


def godot_inputs(data, files, spr):
    with zipfile.ZipFile(io.BytesIO(files["ora"])) as z:
        for n in ART_LAYERS:
            with open(os.path.join(data, f"{n}.png"), "wb") as f:
                f.write(z.read(f"data/{n}.png"))
    Image.fromarray(spr, "RGBA").save(os.path.join(data, "heroine48.png"))
    with open(os.path.join(data, "walkmask.png"), "wb") as f:
        f.write(files["walkmask"])


def write_shadows(data, rgba, feet):
    base = composite_rgba(rgba, BASE_LAYERS)
    so = {}
    for k, foot in feet.items():
        x0, y0, patch = shadow_patch(base, tuple(foot))
        Image.fromarray(patch, "RGBA").save(os.path.join(data, f"shadow_{k}.png"))
        so[k] = [x0, y0]
    return so


def godot_render(godot, tmp, files, spr, ysl, capfeet, tag, ww, wh, rgba):
    proj = os.path.join(tmp, f"p_{tag}"); os.makedirs(proj)
    data = os.path.join(tmp, f"d_{tag}"); os.makedirs(data)
    fake = os.path.join(tmp, f"ad_{tag}"); os.makedirs(fake)
    pname = f"cw5-render-{tag}-{RUN_ID}"
    with open(os.path.join(proj, "project.godot"), "w", newline="\n") as f:
        f.write(RENDER_PROJECT.format(name=pname, ww=ww, wh=wh))
    with open(os.path.join(proj, "gate.gd"), "w", newline="\n") as f:
        f.write(GODOT_RENDER_SCRIPT)
    godot_inputs(data, files, spr)
    so = write_shadows(data, rgba, capfeet)
    with open(os.path.join(data, "cases.json"), "w") as f:
        json.dump({"base_layers": BASE_LAYERS, "ysort_sprites": ysl, "captures": capfeet, "shadow_origin": so}, f)
    env = dict(os.environ); env["APPDATA"] = fake
    p = subprocess.run([godot, "--path", proj, "--script", "gate.gd", "--", data],
                       capture_output=True, text=True, timeout=300, env=env, encoding="utf-8", errors="replace")
    rr = json.load(open(os.path.join(data, "render_report.json")))
    caps = {k: read_bytes(os.path.join(data, f"render_{k}.png")) for k in capfeet}
    return p, rr, caps, pname


def godot_gates(godot, files, rgba, sc):
    spr = sc["spr"]
    rep = {"godot": GODOT_REL, "godot_sha256": sha(read_bytes(godot)), "texel_gate": {}, "render_gates": {}}
    caps_out = {}
    rpts = route_points(sc["walk"])
    feet = {f"r{i:04d}": list(p) for i, p in enumerate(rpts) if i % 6 == 0}
    feet.update({k: list(PINS[k]) for k in PINS})
    ysl = sorted(([n, YSORT_PIVOTS[n]] for n in YSORT_LAYERS), key=lambda t: t[1])
    tmp = tempfile.mkdtemp(prefix="wb-cw5godot-")
    pnames = [f"cw5-texel-{RUN_ID}"]
    try:
        proj = os.path.join(tmp, "p1"); os.makedirs(proj)
        data = os.path.join(tmp, "d1"); os.makedirs(data)
        fake = os.path.join(tmp, "ad1"); os.makedirs(fake)
        with open(os.path.join(proj, "project.godot"), "w", newline="\n") as f:
            f.write(f'config_version=5\n\n[application]\nconfig/name="cw5-texel-{RUN_ID}"\n')
        with open(os.path.join(proj, "gate.gd"), "w", newline="\n") as f:
            f.write(GODOT_TEXEL_SCRIPT)
        godot_inputs(data, files, spr)
        so = write_shadows(data, rgba, feet)
        with open(os.path.join(data, "cases.json"), "w") as f:
            json.dump({"art_layers": ART_LAYERS, "base_layers": BASE_LAYERS, "feet": feet, "route": rpts,
                       "shadow_origin": so,
                       "ysort_sprites": ysl, "probes": {k: list(v) for k, v in COLLISION_PROBES.items()},
                       "pins": {k: list(v) for k, v in PINS.items()}}, f)
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
                  "route_jumps_over_1px": gr["route_jumps"], "heroine_h": gr["heroine_h"],
                  "collision_probes_walkable_in_godot": gr["probes"], "pins_walkable_in_godot": gr["pins"]})
        capfeet = {k: list(PINS[v]) for k, v in CAPTURES.items()}
        for tag, ww, wh, scale in (("1280", 1280, 720, 2), ("640", 640, 360, 1)):
            p2, rr, caps, pname = godot_render(godot, tmp, files, spr, ysl, capfeet, tag, ww, wh, rgba)
            pnames.append(pname)
            r = {"exit_code": p2.returncode, "printed_done": "GODOT_RENDER_GATE_DONE" in p2.stdout,
                 "window_size": rr.get("window_size"), "captures": {}}
            for k, foot in capfeet.items():
                got = decode(caps[k])[2]
                st = runtime_stack_still(rgba, spr, tuple(foot))
                exp = x2(st) if scale == 2 else st
                same = got.shape == exp.shape
                diff = int((got[..., :3] != exp[..., :3]).any(axis=2).sum()) if same else None
                r["captures"][k] = {"foot": foot, "size": list(got.shape[1::-1]), "equals_python_stack": diff == 0,
                                    "differing_pixels": diff}
                caps_out[f"cap{tag}_{k}"] = caps[k]
            rep["render_gates"][tag] = r
        rep["godot_wrote_nothing_outside_temp"] = not any(os.path.isdir(os.path.join(
            os.environ.get("APPDATA", ""), "Godot", "app_userdata", n)) for n in pnames)
    finally:
        shutil.rmtree(_fs(tmp), ignore_errors=True)
    t, rg = rep["texel_gate"], rep["render_gates"]
    rep["verdicts"] = {
        "godot_loads_layers_exact": all(t["layers_exact"].values()) and t["exit_code"] == 0,
        "godot_route_walkable_on_exported_mask": t["route_blocked_on_exported_mask"] == 0
                                                 and t["route_jumps_over_1px"] == 0,
        "godot_collision_probes_blocked": not any(t["collision_probes_walkable_in_godot"].values()),
        "godot_pins_walkable": all(t["pins_walkable_in_godot"].values()),
        "godot_route_stills_match_ysort_and_occlusion": not t["stills_mismatched"],
        "godot_heroine_48_px": t["heroine_h"] == 48,
        "godot_render_1280x720_size": all(c["size"] == [1280, 720] for c in rg["1280"]["captures"].values()),
        "godot_render_1280x720_equals_python_2x": all(c["equals_python_stack"]
                                                      for c in rg["1280"]["captures"].values()),
        "godot_render_640x360_size": all(c["size"] == [640, 360] for c in rg["640"]["captures"].values()),
        "godot_render_640x360_equals_python_1x": all(c["equals_python_stack"] for c in rg["640"]["captures"].values()),
        "godot_wrote_nothing_outside_temp": rep["godot_wrote_nothing_outside_temp"],
    }
    return rep, caps_out


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
    gates["pxo_layer_stack_is_the_named_layers"] = [l["name"] for l in dj["layers"]] == LAYERS and \
        [l["visible"] for l in dj["layers"]] == [n != "guides" for n in LAYERS]
    gates["build_deterministic"] = build_all()[3] == files
    lk = lock_check()
    rep["lock"] = lk
    gates["v04_vista_v02_and_city_hall_untouched"] = lk["all_ok"]
    try:
        v04 = decode(read_bytes(rp(V04_FLAT)))[2]
        rep["v04_reference_repetition_16px_windows"] = repetition_stats(flat_index(v04[..., :4]) if v04.shape[:2] ==
                                                                        (H, W) else _v04_idx(v04))
    except Exception as e:                                               # reference metric only, not a gate
        rep["v04_reference_repetition_16px_windows"] = {"error": str(e)}
    gates["max_path_under_260"] = longest_path() < 260
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


def _v04_idx(img):
    """v04 is 1280x720 logical; its repetition metric uses its own palette, so compare by colour identity."""
    key = img[..., 0].astype(np.int64) << 16 | img[..., 1].astype(np.int64) << 8 | img[..., 2]
    _, inv = np.unique(key, return_inverse=True)
    return inv.reshape(key.shape).astype(np.int64) % 250


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
