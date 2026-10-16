"""UNAPPROVED, NONRUNTIME, TEST-ONLY candidate v08: U.S. Capitol WEST GROUNDS as ONE 640x360 walkable camera (2537),
ruin-state legibility pass over v07.

Deterministic Python tool authored and run by Claude (Claude Code, Opus 5.5, claude.ai Max subscription, firstParty;
no API key, no API billing, no image model, no paid fallback). Worlds Between art workstream B.

What it writes: one 640x360 logical-pixel scene (one gameplay camera: viewport 640x360, window 1280x720, integer 2x)
as an editable layer stack -- a native Pixelorama .pxo (pxo_version 7) and an .ora with 26 named layers -- plus a
palette (.gpl), a collision/walk mask PNG, a walkability + interaction JSON and a manifest. `check` adds the
Pixelorama 1.2.3 headless round-trip (APPDATA redirected), Godot 4.7.2 texel/collision gates, a Godot physics
collision probe (StaticBody2D rectangles, shape queries, CharacterBody2D sweeps) and real WINDOWED Godot renders at
1280x720 and 640x360. NONRUNTIME: nothing is wired into the game runtime; no scene, script, data, test, default,
camera setting, completion state or acceptance counter is touched. Science scene art acceptance stays 0/11.

Why v08. Codex judged v07 at 640x360: the dome and layout read and the ground improved, but the building still
feels overly intact and repetitive for the creator's direction (approved canon: the whole city is abandoned; the
Capitol grounds are recognisable, partially collapsed and overgrown; an active science survey outpost and patrol
automata operate there). v08 therefore:
  * BASE = v07. This file is a fork of the v07 builder (sha256-text-lf-v1 ddaf8213..., pinned in V07_TOOL_SHA_TEXT).
    Camera, sky, clouds, dome layer, West Lawn, patrol walker, every walkable-plane layer, pins, exits,
    interactions, Y-sort pivots, collision probes and the walk mask are v07's; `check` proves them byte-identical
    to the stored v07 files, and proves that the West Front and facade-weathering layers only LOSE texels inside
    the declared ruin voids (nothing repainted, nothing added).
  * Two specific, differently-told collapses (section 5b): A, the gutted south centre bays + south corridor with a
    standing pier, a fresh scorched rubble cone burying the arcade and terrace balustrade, the patrol walker on
    guard, a patrol relay, a dead walker in the cone and survey marks (spray X, pennants, prism, tape); B, the old
    fallen north corner of the Senate wing with a tree grown through the shell and a grassed-over spill. Neither
    mirrors the other or v07's House-wing bite. The dome and central pavilion stay untouched.
  * Two new editable layers: `breach-interiors` (back walls, slabs, party walls and trees seen through the breaches,
    below the West Front) and `breach-rubble` (both spill cones with fragments and the survey / patrol cues, over
    the terrace). Broken edges, blown windows, scorch, ivy, the X and the relay go into `capitol-ruin`.
  * Two grounds trees (broken oak, poplar) move right so they no longer hide breach A (backdrop only).

AUTHORING ROUTE (disclosed). NOT a Pixelorama GUI paint pass (no desktop/computer-use access to the GUI in this
session). Every placement is an explicit hand-written table entry; the tool rasterises those tables into named
palette layers (no continuous-colour image, no resize, no generated image anywhere). The .pxo opens in the
Pixelorama GUI as editable layers; the only Pixelorama step is the headless CLI export round-trip in `check`.
A GUI open/save/reopen has not been done.

Depth model: unchanged from v06/v07 (walkable plaza = game 3/4 plane at 28 px/m; backdrop = one pinhole, F 552 px,
eye 0.5 m, horizon row 192.2; DEPTH_TABLE is written to the manifest).

Modes
  preview <dir>   render layers, flat, runtime stills, 2x views and guides into <dir> (outside the repo); prints
                  the static gates and the v07 comparison
  build           write candidate files (never overwrites a different file)
  check           static gates + v07-relative gates + LOCK (v07, v06, v05t) + Pixelorama headless round-trip
                  (--no-pixelorama) + Godot gates in throwaway temp projects (--no-godot); --write-report writes the
                  JSON report, the Godot captures (1280x720 and 640x360) and zoom crops into outputs/<RUN>/.
Run: python -I -B <this file> preview <tempdir> | build | check [--write-report] [--no-pixelorama] [--no-godot]
     [--godot <exe>]
"""
import argparse, hashlib, io, json, math, os, shutil, subprocess, sys, tempfile, time, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
AREA = "wdc-capitol-west"
VER = "unapproved-v08"
STAMP = "20261016-155827"
RUN_ID = "6cf49486"
RUN = f"wdc-cw-v08_{STAMP}-{RUN_ID}"          # short run dir: keeps every candidate/output path under MAX_PATH (260)
CAND_REL = f"game/assets/environments/candidates/{RUN}"
OUT_REL = f"outputs/{RUN}"
TOOL_REL = "tools/" + os.path.basename(os.path.abspath(__file__))
REAL_SITE_AUDIT_REL = ("docs/qa/rpg-2-star-ocean-the-second_wdc-capitol-west_real-site-visual-reference-codex-audit_"
                       "unapproved-v01_20261016-114641-c720df4a.md")
# --- base composition: v06 (read-only). This tool is a fork of the v06 builder; the fork point is pinned below.
V06_RUN = "wdc-cw-v06_20261016-071733-18b9cea3"
V06_TOOL = ("tools/rpg-2-star-ocean-the-second_wdc-capitol-west_walkable-scale-depth_pixelorama-build_unapproved-"
            "v06_20261016-071733-18b9cea3.py")
V06_TOOL_SHA_TEXT = "aa7baec94e74f93f751c859b77c311f9c410dfa42d1f7aa3f584a65777a38e66"
V06_STEM = "unapproved-v06_20261016-071733-18b9cea3"
V06_CAND = f"game/assets/environments/candidates/{V06_RUN}"
V06_FLAT = f"{V06_CAND}/rpg-2-star-ocean-the-second_wdc-capitol-west_scene-flat-640x360_{V06_STEM}.png"
V06_ORA = f"{V06_CAND}/rpg-2-star-ocean-the-second_wdc-capitol-west_scene-22layer_{V06_STEM}.ora"
V06_WALKMASK = f"{V06_CAND}/rpg-2-star-ocean-the-second_wdc-capitol-west_scene-walkmask_{V06_STEM}.png"
V06_WALK_JSON = f"{V06_CAND}/rpg-2-star-ocean-the-second_wdc-capitol-west_scene-walkability_{V06_STEM}.json"
V06_AUDIT_REL = ("docs/qa/rpg-2-star-ocean-the-second_wdc-capitol-west_walkable-v06-codex-visual-audit_unapproved-v01_"
                 "20261016-134646-35af3a0d.md")
# --- texture donor: v05t (read-only, never imported or executed; its techniques are re-implemented here)
V05T_RUN = "wdc-cw-v05t_20261016-141453-0dd3075f"
V05T_TOOL = ("tools/rpg-2-star-ocean-the-second_wdc-capitol-west_authored-texture-hierarchy_pixelorama-build_unapproved-"
             "v05_20261016-141453-0dd3075f.py")
# --- v08 base: v07 (read-only). This tool is a fork of the v07 builder; the fork point is pinned below.
V07_RUN = "wdc-cw-v07_20261016-145408-0f854fbc"
V07_TOOL = ("tools/rpg-2-star-ocean-the-second_wdc-capitol-west_vista-texture-merge_pixelorama-build_unapproved-"
            "v07_20261016-145408-0f854fbc.py")
V07_TOOL_SHA_TEXT = "ddaf8213bd8ce59a27e1a4c04bea3ae777de220c4a867df4944c37d6dc210ee6"
V07_STEM = "unapproved-v07_20261016-145408-0f854fbc"
V07_CAND = f"game/assets/environments/candidates/{V07_RUN}"
V07_FLAT = f"{V07_CAND}/rpg-2-star-ocean-the-second_wdc-capitol-west_scene-flat-640x360_{V07_STEM}.png"
V07_ORA = f"{V07_CAND}/rpg-2-star-ocean-the-second_wdc-capitol-west_scene-24layer_{V07_STEM}.ora"
V07_WALKMASK = f"{V07_CAND}/rpg-2-star-ocean-the-second_wdc-capitol-west_scene-walkmask_{V07_STEM}.png"
V07_WALK_JSON = f"{V07_CAND}/rpg-2-star-ocean-the-second_wdc-capitol-west_scene-walkability_{V07_STEM}.json"
V07_QA_REL = ("docs/qa/rpg-2-star-ocean-the-second_wdc-capitol-west_vista-texture-merge_qa-note_unapproved-v07_"
              "20261016-145408-0f854fbc.md")
HEROINE_REL = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_"
               "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
PIXELORAMA_DEFAULT = "C:/Users/hkzha/AppData/Local/Programs/Pixelorama-1.2.3/Pixelorama-Windows-64bit/Pixelorama.exe"
PIXELORAMA_VERSION = "v1.2.3-stable"
GODOT_REL = "work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe"      # gitignored local tooling
W, H = 640, 360                   # one gameplay camera (logical viewport)
VIEW = 2                          # window 1280x720 = integer 2x
WIN_LONG_PREFIX = "\\\\?\\"

# Read-only predecessors: digest of every file (text files CRLF->LF, others raw bytes), taken 2026-10-16 14:55
# before this tool wrote anything. `check` recomputes them; v06 and v05t must stay byte-identical.
LOCK = {
    V06_CAND: "127d14ac0e651319456a3b3e58f758aa09eda0289338be50db65baaf32e9acda",
    f"outputs/{V06_RUN}": "3f0aba9a4a0a0ea858270caf732a6988370fb0c50c9ef9a82d66f75a94d2cb0d",
    V06_TOOL: "t:" + V06_TOOL_SHA_TEXT,
    "docs/qa/rpg-2-star-ocean-the-second_wdc-capitol-west_walkable-scale-depth_qa-note_unapproved-v06_"
    "20261016-071733-18b9cea3.md": "t:6f58afbbcebe0988432801c9fea72b87a6f1319deb6a5ddf01b51f448a214b41",
    V06_AUDIT_REL: "t:91bc78ab8428e67a5b2946fc9e29fb2feba9629eaf53fc44fe00c5550482dc76",
    "docs/qa/rpg-2-star-ocean-the-second_wdc-capitol-west_walkable-v06_clean-clone-check-closure-addendum_"
    "unapproved-v06_20261016-110135-03d32c38.md": "t:c814a44f547e7bd417f467d38aa5e2d0d29feb30dd1c81e8a9d02e99402e990b",
    REAL_SITE_AUDIT_REL: "t:f323bc4e7d361a282495b6e5b2c069b36ccaf64e818d9abc61e613c9bf42c119",
    f"game/assets/environments/candidates/{V05T_RUN}":
        "4eac90dfcb5a404237b4b1c5952e3752bf6345716a11db43a4a42d11477ca25d",
    f"outputs/{V05T_RUN}": "a6039830bbdfa76652ca985d71857b6af2ca9060dc30882f87f581046342a1ee",
    V05T_TOOL: "t:6452b4776c4aa901312cc7124bfa4b667b989c41b8f49142edb032bd4e97674e",
    "docs/qa/rpg-2-star-ocean-the-second_wdc-capitol-west_authored-texture-hierarchy_qa-note_unapproved-v05_"
    "20261016-141453-0dd3075f.md": "t:cee36beb67f6f9912008989a0c855194d6943ea7761e1a8ae425a02eaf8976b1",
    # v08: the direct base, v07 (digests taken 2026-10-16 15:58 before this tool wrote anything)
    V07_CAND: "ed788c57287eab78d99e896dbde8c05f06802cf4dcf4df664fd2b33773f6b699",
    f"outputs/{V07_RUN}": "09f98574bb1dda7095178a5e1ece51896404481f016709b54eba4ad2413f1f5e",
    V07_TOOL: "t:" + V07_TOOL_SHA_TEXT,
    V07_QA_REL: "t:3463f382df3345085a19c407a118de1fb570da3bd02907fc83d4650f0a315be5",
}
# v05t is untracked in git (absent from a clean clone). Its four entries are checked only when present; then they
# must match exactly. Every v06 entry is tracked and mandatory. v07 is untracked too, but it is v08's comparison
# base (V07_FLAT, V07_ORA, V07_WALKMASK are read), so its entries are mandatory: v08 `check` needs v07 on disk.
LOCK_OPTIONAL_IF_ABSENT = {
    f"game/assets/environments/candidates/{V05T_RUN}", f"outputs/{V05T_RUN}", V05T_TOOL,
    "docs/qa/rpg-2-star-ocean-the-second_wdc-capitol-west_authored-texture-hierarchy_qa-note_unapproved-v05_"
    "20261016-141453-0dd3075f.md",
}


def fname(purpose, ext):
    """AGENTS naming: project slug, area, purpose, version, timestamp and run id are all in the file name."""
    return f"{SLUG}_{AREA}_{purpose}_{VER}_{STAMP}-{RUN_ID}.{ext}"


EXPORT_STEM = f"{SLUG}_{AREA}_pixelorama-export_{VER}_{STAMP}-{RUN_ID}"

LAYERS = ["sky", "clouds", "capitol-dome", "breach-interiors", "capitol-west-front", "facade-weathering",
          "capitol-ruin", "olmsted-terrace", "breach-rubble", "west-lawn", "grounds-trees", "patrol-walker", "lawn-edge-planting", "seat-wall-steps",
          "plaza-ground", "terrain-patches", "ground-detail", "cast-shadows", "rubble-collapse", "props-low",
          "survey-mast-ysort", "survey-tripod-ysort", "beacon-ysort", "elm-ysort", "fg-occlusion",
          "guides"]                                  # bottom -> top; v07 added 2 editable layers, v08 adds 2 more
ART_LAYERS = LAYERS[:-1]
BASE_LAYERS = LAYERS[:LAYERS.index("props-low") + 1]                       # merged into one base at runtime
YSORT_LAYERS = [n for n in LAYERS if n.endswith("-ysort")]

# ============================================================================ palette (hand-picked; v06 adds haze glass, conifers)
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
    # v06: glass and voids seen through 150..260 m of air (hazed, never near-black), weathering streak
    ("hw0", "687384"), ("hw1", "7e8997"), ("hw2", "96a0aa"), ("ws0", "a39f97"),
    # v06: conifers (red cedar / spruce) and tulip-poplar yellow-green
    ("cn0", "1b2d2b"), ("cn1", "28413b"), ("cn2", "3a5a4b"), ("cn3", "557459"), ("cn4", "7a9470"),
    ("yg0", "4c6436"), ("yg1", "6c873f"), ("yg2", "92a952"), ("yg3", "b8c66d"),
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
CONIFER = R("cn0", "cn1", "cn2", "cn3", "cn4")
POPLAR = R("mg1", "yg0", "yg1", "yg2", "yg3")

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
        "s2": "lw2", "mg1": "vg1", "mg2": "vg2", "mg3": "vg3", "mg4": "vg4", "p3": "hz1", "p2": "hz0",
        "cn0": "cn1", "cn1": "vg0", "cn2": "vg1", "cn3": "vg2", "cn4": "vg3", "yg0": "vg1", "yg1": "vg2",
        "yg2": "vg3", "yg3": "vg4", "f1": "mg1", "f2": "mg1", "f3": "mg2", "f4": "mg3", "f5": "mg4", "b1": "vg0",
        "b2": "vg1"}
HAZE_LUT = np.arange(len(ALL_PAL), dtype=np.int16)
for _a, _b in HAZE.items():
    HAZE_LUT[I[_a]] = I[_b]

# ============================================================================ camera + depth (see docstring)
CAPX = 371.5                      # Capitol / Mall axis between columns 371 and 372 (mirror: x' = 743 - x)
F = 552.0
EYE = 0.5                         # v06: a low eye (seat-coping height) so the lawn foreshortens and the Capitol looms
HZ = 192.2
D_TERRACE, D_FACADE, D_DOME = 150.0, 207.0, 263.0
LAWN_RISE = 2.18


def lawn_elev(d):
    return LAWN_RISE * float(np.clip((d - 20.0) / (D_TERRACE - 20.0), 0.0, 1.0))


def row_of(d, e=None):
    e = lawn_elev(d) if e is None else e
    return HZ + (EYE - e) * F / d


def d_of_row(y):
    """Inverse of row_of on the lawn (rows 186..206 -> d 150..20 m); nearer rows are the walkable plane."""
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
    ("walkable plaza (game 3/4 plane)", "<= 20", 28.0, "203..359"),
    ("Olmsted seat wall, steps, cheek lanterns", 20, round(F / 20, 2), "146..252"),
    ("near planting behind the wall", "20..28", "20..28", "150..236"),
    ("patrol walker in the wall breach", 32, round(F / 32, 2), "153..197"),
    ("grounds trees flanking the lawn", "95..140", "3.9..5.8", "92..189"),
    ("Olmsted lower west terrace (stairs, recess, piers)", D_TERRACE, round(F / D_TERRACE, 2), "152..185"),
    ("West Front facade (wider than the frame)", D_FACADE, round(F / D_FACADE, 2), "100..169"),
    ("dome, peristyle .. Statue of Freedom", D_DOME, round(F / D_DOME, 2), "3..110"),
]

# ============================================================================ hand-authored geometry (logical px)
# --- dome stages (rows) and half widths, axis CAPX (2.1 px/m at 263 m)
STATUE_TOP = 3
SHELL = (35, 69)
SHELL_A, SHELL_B, SHELL_BASE = 29.0, 37.0, 70.0
ATTIC = (70, 80)
PERI_BAL = (81, 83)
PERI_ENT = (84, 88)
PERI_COLS = (89, 106)
STYLOBATE = (107, 110)
DOME_HW = {"attic": 33, "attic_cornice": 34, "peri_bal": 37, "peri_ent": 40, "peri_cols": 38, "stylobate": 41}
PERI_MISSING = (25, 35, 45)        # azimuth deg (+ = south / right): game fiction, three missing columns
BREACH = {44: (12, 14), 45: (11, 17), 46: (10, 18), 47: (10, 19), 48: (11, 20), 49: (11, 21), 50: (12, 21),
          51: (12, 20), 52: (13, 20), 53: (14, 19), 54: (15, 18), 55: (16, 17)}   # row -> (X0, X1) open hole, south
BREACH_RIBS = ((14, 45, 53), (18, 46, 51))
RUST = ((12, 56, 63, "ru0"), (16, 55, 61, "ru1"), (19, 54, 59, "ru0"), (10, 56, 60, "ru1"), (14, 57, 66, "ru0"))
# --- West Front (left half, absolute columns; the right half mirrors x' = 743 - x before asymmetric states)
#     2.67 px/m: the 229 m front spans x 66..677, so the House (south) wing runs out of the right frame edge
SECTIONS_L = [("wing", 66, 185, 109), ("corridor", 186, 221, 115), ("center", 222, 305, 106),
              ("pavilion", 306, 371, 100)]
PROJECTION = {"pavilion": 3, "wing": 2, "center": 1, "corridor": 0}
FACADE_BOTTOM = 169
STRING = 143
GROUND_FLOOR = (146, 168)
# (v07: the central pavilion's columns, PAV_COLS_L, moved to the explicit-variant tables of the West Front painter)
WING_PORTICO_L = (93, 152)        # v07: ends one texel past the last column (v06's 153..159 was an empty dark slot)
WING_COLS_L = [94, 105, 116, 127, 138, 149]
CENTER_BAYS_L = [226, 235, 244, 253, 262, 271, 280, 289, 298]
CORRIDOR_BAYS_L = [191, 200, 209]
WING_BAYS_L = [70, 78, 86, 163, 171, 179]
# window state per bay, hand-assigned (g glass, d dark, b broken, o boarded, v vine, s scorched)
STATE_CENTER = {"L": "gdgvgdbgd", "R": "dgbssobdg"}
STATE_CORR = {"L": "gvd", "R": "sbo"}
STATE_WING = {"L": "vvdvgv", "R": "gdsbdd"}
PAV_COL_MISSING_R = (0, 3)        # indices into the mirrored right pavilion columns (nearest the axis is index 0)
WING_COL_TOPPLED_R = (1, 4)       # right (House) wing portico columns down
#     v06 pass 2: a LOCALISED bite out of the House wing (not a diagonal shear): the roofline holds to x 566, a
#     ragged notch drops to the second floor over x 578..612, and a broken end pier survives at the frame edge
HOUSE_COLLAPSE = [(564, 109), (566, 110), (568, 113), (569, 112), (571, 118), (573, 117), (574, 123), (577, 126),
                  (578, 131), (581, 130), (583, 136), (586, 139), (588, 138), (591, 144), (594, 146), (597, 145),
                  (600, 149), (603, 148), (606, 146), (608, 141), (610, 142), (612, 135), (614, 131), (615, 132),
                  (617, 126), (619, 125), (621, 119), (623, 117), (625, 118), (627, 114), (630, 115), (633, 112),
                  (636, 113), (639, 111)]
HOUSE_SLABS = [(121, 568, 576), (133, 576, 585), (127, 615, 624), (139, 609, 617)]        # exposed floors: y, x0, x1
HOUSE_BEAMS = [(575, 113, 122), (586, 126, 134), (612, 124, 132), (604, 136, 146)]        # bent iron: x, y_top, y_bot
# ivy curtains hanging from the cornices: (x0, top row, max length, width) -- ragged lobed hems, tendrils
IVY_WING_L = [(66, 110, 40, 21), (93, 111, 24, 9), (108, 111, 44, 27), (150, 110, 30, 14), (170, 111, 20, 10),
              (192, 116, 15, 7), (229, 107, 11, 6), (247, 107, 7, 4)]
# roof scrub rooted on the parapets: (x centre, half width, height px) -- low mats, not floating balls
ROOF_SHRUBS = [(80, 9, 6), (115, 6, 4), (172, 11, 7), (200, 5, 4), (263, 4, 3), (436, 4, 3), (503, 6, 4),
               (546, 8, 5)]
ROOF_SAPLING = (205, 114, 16)      # self-sown tree on the north corridor roof: x, roof row, height px
SOOT = [(437, 130, 14), (452, 128, 11), (470, 136, 9), (486, 128, 12), (512, 140, 10), (528, 132, 8)]
FACADE_CRACKS = [[(392, 113), (394, 120), (392, 127), (395, 136), (393, 142)],
                 [(468, 107), (466, 113), (469, 119)], [(282, 111), (284, 117), (283, 121)]]
STREAKS = [(232, 111, 9), (258, 111, 6), (289, 111, 12), (318, 112, 7), (348, 112, 10), (401, 112, 8),
           (428, 112, 13), (455, 111, 6), (480, 111, 9), (507, 116, 5), (540, 110, 11), (90, 114, 8), (130, 114, 6)]
# --- Olmsted lower west terrace (~3.7 px/m at 150 m), full width
T_RAIL, T_BAL, T_BASE = 157, (158, 160), 161
T_WALL = (162, 181)
T_FOOT = (182, 185)
STAIRS_T = ((282, 319), (424, 461))
CHEEKS_T = ((278, 281), (320, 323), (420, 423), (462, 465))
RECESS = (324, 419)
GROTTO = (360, 383, 166, 181)
FOUNTAIN_T = (347, 396, 177, 185)
T_PIERS = [6, 46, 86, 126, 166, 206, 246, 497, 537, 577, 617]
T_WINDOWS = [24, 64, 104, 144, 184, 224, 515, 555, 595]
T_BAL_GAPS = [(194, 205), (478, 492), (550, 606)]
T_URNS = {6: "urn", 46: "urn", 86: "gone", 126: "urn", 166: "tilted", 206: "urn", 246: "stump", 497: "urn",
          537: "gone", 577: "urn", 617: "gone"}                 # v06: hand-assigned urn states (no repeated row)
TERRACE_BLOCKS = [  # v07: (x, course 0..6, length, tone) hand-placed replaced / weathered blocks on the wall face
    (12, 1, 9, "dark"), (40, 3, 12, "new"), (58, 5, 8, "ws"), (92, 2, 10, "ws"), (118, 4, 14, "dark"),
    (150, 1, 8, "new"), (176, 3, 11, "ws"), (210, 5, 9, "dark"), (232, 2, 13, "new"), (258, 4, 8, "ws"),
    (266, 0, 10, "dark"), (330, 4, 9, "ws"), (400, 2, 8, "dark"), (472, 1, 12, "ws"), (500, 3, 9, "new"),
    (520, 5, 11, "dark"), (560, 2, 8, "ws"), (590, 4, 13, "dark"), (612, 1, 9, "new"), (630, 3, 8, "ws")]
TERRACE_DAMP = [(0, 277, 6), (324, 346, 4), (397, 419, 4), (466, 639, 8)]   # (x0, x1, max rows) at the wall foot
T_IVY = [(146, 162, 16, 14), (324, 162, 14, 11), (404, 162, 18, 15), (62, 162, 12, 8), (234, 162, 9, 6),
         (518, 162, 12, 9)]
DECK_SHRUBS = [(116, 155, 6), (186, 154, 5), (262, 155, 4), (478, 154, 5), (530, 155, 7)]
COLLAPSE_CONE = [(548, 154, 12, 7), (564, 158, 15, 9), (582, 161, 16, 10), (600, 164, 15, 9), (618, 167, 13, 8),
                 (634, 170, 10, 7), (572, 172, 9, 5), (606, 176, 8, 4)]
T_SENTINEL = (300, 168)            # small parked patrol sentinel on the left terrace stair (scale figure, 9 px)
# --- lawn (world coordinates: X metres right of the axis, d metres from the camera)
TRAIL = ((0.0, 20.0), (0.0, 148.0), 2.6)
WALK_L = ((-48.0, 21.0), (-12.5, 148.0), 2.0)
WALK_R = ((48.0, 21.0), (12.5, 148.0), 2.0)
LAWN_SHRUBS = [(-14, 40, 0.9, "mg"), (11, 46, 0.8, "mg"), (-20, 70, 1.4, "vg"), (18, 64, 1.2, "mg"),
               (-6, 96, 1.6, "vg"), (24, 110, 2.0, "vg"), (-28, 120, 2.2, "vg"), (6, 128, 1.8, "vg"),
               (-34, 52, 1.0, "mg"), (30, 38, 0.8, "mg")]
LAWN_PATCHES = [(-12, 34, 4.0, 3.0), (16, 50, 6.0, 5.0), (-26, 80, 9.0, 8.0), (10, 104, 10.0, 9.0)]
WALKER_POS = (512, 197)            # near patrol walker standing in the seat-wall breach on the lawn (d ~ 32 m)
PATROL_TRAIL = [(5.0, 21.0), (8.0, 28.0), (8.6, 32.0), (11.0, 46.0), (16.0, 80.0), (22.0, 140.0)]  # X m, d m
OFFSCREEN_SHADE = [  # dappled canopy shadows of trees south of the frame (behind the camera), falling north
    [(-20, 352, 70, 16), (40, 362, 60, 12), (96, 366, 40, 9)],
    [(560, 360, 60, 12), (630, 350, 50, 18), (600, 340, 30, 8)]]
# --- grounds trees, each a distinct species with a hand-placed silhouette: (x, d m, height m, kind)
# v08: the broken oak (v07 x 548) and the poplar (v07 x 492) stood in front of the new south breach A and would
#      hide it at 640x360; they move right, in front of v07's House-wing bite (which they already half hid)
GROUNDS_TREES = [(196, 126, 16.0, "oak"), (252, 140, 15.0, "cedar"), (128, 96, 9.0, "magnolia"),
                 (588, 122, 15.0, "broken-oak"), (606, 104, 17.5, "spruce"), (568, 142, 11.0, "poplar")]
# Olmsted grounds groves beyond both terrace ends (~160 m): hand-placed canopy masses (x, y, r)
FAR_MASSES = [
    [(-6, 150, 18), (18, 142, 16), (40, 148, 14), (60, 152, 12), (8, 166, 14), (34, 170, 12), (56, 168, 10)],
    [(624, 150, 12), (640, 144, 14), (612, 166, 10), (634, 170, 12)],
]
TERRACE_FOOT_SHRUBS = [(14, 5), (36, 4), (70, 6), (100, 4), (162, 5), (222, 4), (248, 6), (268, 4),
                       (478, 4), (508, 6), (528, 4), (610, 5), (632, 6)]
# --- Olmsted seat wall (a curved granite wall with a marble coping, d ~ 20 m)
ARC = (372.0, 420.0, 600.0, 214.0)               # centre x, centre y, rx, ry: coping top row = cy - ry*sqrt(...)
STEPS = (312, 432)
CHEEKS = ((296, 311), (433, 448))
CHEEK_TOP = 192
STEP_ROWS = [(203, 205, "landing"), (206, 207, "riser"), (208, 210, "tread"), (211, 212, "riser"),
             (213, 215, "tread"), (216, 217, "riser"), (218, 220, "tread"), (221, 222, "riser")]
PLAZA_TOP_AT_STEPS = 223
COLLAPSE = [(486, 0), (492, 5), (498, 9), (506, 14), (512, 17), (580, 17), (588, 11), (596, 6), (604, 0)]
# near planting behind the coping (d 20..28 m), each a different plant, hand-placed: heights are px above the coping
NEAR_ROUND = [(8, 30, 22), (34, 20, 14)]                               # old yew masses behind the elm: x, up, r
HEDGE_LOBES = [(54, 22, 9), (68, 28, 11), (84, 25, 10), (98, 31, 12), (114, 27, 10), (130, 30, 11), (146, 22, 8),
               (76, 14, 9), (106, 16, 10), (138, 14, 8)]               # overgrown boxwood hedge remnant: x, up, r
GRASS_CLUMPS = [(160, 13, 16, 0.2), (184, 10, 21, 0.6), (270, 9, 13, 0.3), (282, 6, 9, 0.5), (454, 7, 12, 0.4),
                (604, 12, 17, 0.3), (622, 8, 11, 0.7)]                 # miscanthus / broomsedge: x, half-w, h, dry
CEDAR_SEEDLING = (232, 38)                                             # x, height px
SUMAC = (474, 13, 26)                                                  # staghorn sumac: x, half-w, height
VIBURNUM = (636, 30, 18)                                               # x, up, r (white flower heads)
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
    (518, 228, 16, 11, "ashlar", "gr4"), (536, 226, 20, 11, "drum", "m5"), (556, 230, 14, 10, "coping", "m4"),
    (502, 242, 14, 9, "ashlar", "gr3"), (526, 244, 18, 12, "cut", "gr4"), (548, 242, 16, 10, "ashlar", "gr2"),
    (568, 240, 14, 9, "ashlar", "gr3"), (584, 246, 12, 8, "coping", "m5"),
    (492, 256, 12, 7, "ashlar", "gr2"), (510, 258, 18, 10, "ashlar", "gr3"), (534, 260, 22, 9, "drum", "m5"),
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
CAPTURES = {"entry": "spawn_south", "vista": "vista_point", "interact": "beacon_front",
            "occlusion": "tripod_behind"}

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
SKY_BANDS = [(0, "sk0"), (14, "sk1"), (30, "sk2"), (48, "sk3"), (66, "sk4"), (84, "sk5"), (102, "sk6"),
             (120, "sk7")]
CLOUDS = [  # hand-placed lobes (cx, cy, rx, ry); each list is one cloud
    # cumulus bank behind the House wing (right); its flat base is hidden behind the facade. v07: lower and flatter
    # (tops at ~row 66 instead of ~58) and mostly in the grey-cream tones, so it no longer competes with the dome
    [(452, 99, 20, 7), (478, 91, 22, 10), (506, 85, 20, 11), (532, 79, 18, 10), (556, 83, 22, 11),
     (584, 77, 20, 11), (610, 81, 22, 10), (636, 87, 20, 10), (520, 96, 30, 8), (590, 96, 34, 9)],
    [(470, 80, 8, 5), (494, 76, 9, 5)],
    # wind-drawn streaks high on the left (partly behind the elm crown)
    [(150, 22, 34, 3), (196, 18, 28, 3), (236, 24, 22, 2)],
    [(214, 46, 26, 3), (250, 43, 20, 3), (282, 47, 12, 2)],
    [(272, 82, 22, 3), (300, 79, 14, 3)],
    [(444, 30, 18, 3), (470, 27, 14, 2)],
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
            if ci in (0, 1):                                    # v07: the bank keeps cl0 only on its sunlit crowns
                t = np.where(v > 0.72, I["cl0"], np.where(v > 0.0, I["cl1"], np.where(v > -0.5, I["cl2"], I["cl3"])))
            else:
                t = np.where(v > 0.45, I["cl0"], np.where(v > -0.15, I["cl1"], np.where(v > -0.6, I["cl2"],
                                                                                     I["cl3"])))
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
    """Statue of Freedom on its globe: crested helmet, sheathed sword hand, shield and wreath at her side."""
    rows = ["...a...",
            "..aAb..",
            "..AAb..",
            ".aABb..",
            ".AABBb.",
            "aAABBb.",
            ".AABBbb",
            ".AABBb.",
            "..ABBb.",
            ".aABBbb",
            "..cCcc.",
            ".cCCccc"]
    stamp(L, 368, STATUE_TOP, rows, {"a": "br0", "A": "br1", "B": "br0", "b": "br0", "c": "dm2", "C": "dm3"})
    px(L, 370, STATUE_TOP + 3, "dm3")                 # sunlit shoulder
    px(L, 369, STATUE_TOP + 5, "dm2")                 # shield rim


def paint_dome():
    L = new()
    statue(L)
    # tholos (lantern): cap dome, cornice, ring of columns before a shaded cella, stepped base ring
    for y, hw in ((15, 3), (16, 4), (17, 5), (18, 6)):
        dome_band(L, y, y, hw, d=1, dith=0.0)
    dome_band(L, 19, 19, 8, d=2, dith=0.0)
    for y in range(20, 30):
        dome_band(L, y, y, 7, d=-3, dith=0.0)
    for x in (365, 367, 369, 374, 376, 378):
        rect(L, x, 20, x, 29, "dm5" if x < 371 else "dm4")
    rect(L, 371, 21, 372, 28, "hw0")
    for y, hw, d in ((30, 10, 2), (31, 11, 1), (32, 12, 0), (33, 12, -1), (34, 13, -2)):
        dome_band(L, y, y, hw, d=d, dith=0.0)
    # shell: ellipsoid lit from the front-left, cast-iron ribs every 10 deg, two tiers of windows, the south breach
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
        idx = np.maximum(idx, I["dm1"])                                   # 263 m of air: no near-black on the shell
        phi = np.degrees(np.arcsin(np.clip(X / max(hw, 1e-3), -1, 1)))
        cosp = np.cos(np.radians(phi))
        frac = ((phi + 5.0) / 10.0) % 1.0
        dpx = np.minimum(frac, 1 - frac) * math.radians(10.0) * hw * cosp
        rib = (dpx < 0.5) & (cosp > 0.40) & (Yh > 2)
        idx = np.where(rib, np.array([shift(DOME, int(c), -1) for c in idx]), idx)
        if 59 <= y <= 61:
            wf = ((phi / 10.0) % 1.0)
            win = (np.abs(wf - 0.5) * math.radians(10.0) * hw * cosp < 0.6) & (cosp > 0.45)
            idx = np.where(win, I["hw0"] if y > 59 else I["hw1"], idx)
        if y in (47, 48):
            wf = ((phi / 20.0) % 1.0)
            win = (np.abs(wf - 0.5) * math.radians(20.0) * hw * cosp < 0.5) & (cosp > 0.55)
            idx = np.where(win, I["hw1"], idx)
        if y == SHELL[1]:
            idx = np.array([shift(DOME, int(c), 1) for c in idx])
        L[y, xs] = idx
    for y, (a, b) in BREACH.items():
        for X in range(a, b + 1):
            px(L, math.floor(CAPX + X), y, "dw1" if X < b - 1 else "hw0")
        px(L, math.floor(CAPX + a) - 1, y, "dm5" if y < 49 else "dm3")
    for X, y0, y1 in BREACH_RIBS:
        for y in range(y0, y1 + 1):
            px(L, math.floor(CAPX + X + (1 if y > (y0 + y1) // 2 + 1 else 0)), y, "dm2")
    for X, y0, y1, c in RUST:
        rect(L, math.floor(CAPX + X), y0, math.floor(CAPX + X), y1, c)
    # attic drum: cornice, wall with windows between pilasters, shadow line
    dome_band(L, ATTIC[0], ATTIC[0], DOME_HW["attic_cornice"], d=2, dith=0.0)
    dome_band(L, ATTIC[0] + 1, ATTIC[0] + 1, DOME_HW["attic_cornice"], d=-2, dith=0.0)
    dome_band(L, ATTIC[0] + 2, ATTIC[1] - 1, DOME_HW["attic"], d=0)
    for a, x in azimuth_cols(DOME_HW["attic"], 10, 5, 0.40):
        xi = math.floor(x)
        rect(L, xi, 74, xi, 77, "hw0")
        px(L, xi - 1, 74, "dm5" if a < 20 else "dm4")
    for a, x in azimuth_cols(DOME_HW["attic"], 10, 0, 0.55):
        px(L, math.floor(x), 72, "dm5" if a < 0 else "dm4")
    dome_band(L, ATTIC[1], ATTIC[1], DOME_HW["attic"], d=-3, dith=0.0)
    # peristyle balustrade + entablature (dentils)
    dome_band(L, PERI_BAL[0], PERI_BAL[0], DOME_HW["peri_bal"], d=1, dith=0.0)
    for x in range(int(CAPX - 37), int(CAPX + 37) + 1):
        px(L, x, PERI_BAL[0] + 1, "dm2" if x % 2 else "dm4")
    dome_band(L, PERI_BAL[1], PERI_BAL[1], DOME_HW["peri_bal"], d=0, dith=0.0)
    dome_band(L, 84, 84, DOME_HW["peri_ent"], d=2, dith=0.0)
    dome_band(L, 85, 86, DOME_HW["peri_ent"], d=0, dith=0.03)
    for x in range(int(CAPX - 40), int(CAPX + 40) + 1, 2):
        px(L, x, 87, "dm2")
    dome_band(L, 88, 88, DOME_HW["peri_ent"], d=-3, dith=0.0)
    # colonnade: shaded wall with windows behind 36 columns (front half), three missing on the south side
    for y in range(PERI_COLS[0], PERI_COLS[1] + 1):
        dome_band(L, y, y, DOME_HW["peri_cols"], d=-3, dith=0.0)
    for a, x in azimuth_cols(DOME_HW["peri_cols"] - 3, 20, 10, 0.45):
        rect(L, math.floor(x), 93, math.floor(x) + (1 if abs(a) < 40 else 0), 101, "hw0")
    for a, x in azimuth_cols(DOME_HW["peri_cols"] - 1, 10, 5, 0.12):
        xi = math.floor(x)
        missing = any(abs(a - m) < 1 for m in PERI_MISSING)
        wide = math.cos(math.radians(a)) > 0.62
        lit = "dm6" if a < -20 else "dm5"
        if missing:
            if abs(a - 35) < 1:
                rect(L, xi, 101, xi + (1 if wide else 0), 106, "dm3")    # broken stump
            if abs(a - 45) < 1:
                rect(L, xi, 89, xi, 92, "dm3")                            # capital fragment still hanging
            continue
        rect(L, xi, PERI_COLS[0], xi, PERI_COLS[1], lit if wide else "dm4")
        if wide:
            rect(L, xi + 1, PERI_COLS[0], xi + 1, PERI_COLS[1], "dm3")
        rect(L, xi - (1 if wide else 0), PERI_COLS[0], xi + 1, PERI_COLS[0], "dm5")
    for y, d in zip(range(STYLOBATE[0], STYLOBATE[1] + 1), (2, 1, 0, -2)):
        dome_band(L, y, y, DOME_HW["stylobate"], d=d, dith=0.0)
    for x, y, c in ((398, 105, "dm3"), (401, 106, "dm2"), (405, 105, "dm3"), (406, 106, "dm2")):
        px(L, x, y, c)                                                     # fallen column drums
    return L


# ============================================================================ 4 West Front
def mirror_x(x, w=1):
    """Start column of the mirror image of the span [x, x + w - 1] about the axis (x' = 743 - x)."""
    return 743 - x - (w - 1)


def section_at(x):
    xl = x if x <= 371 else 743 - x
    for name, x0, x1, roof in SECTIONS_L:
        if x0 <= xl <= x1:
            return name, x0, x1, roof
    return None


# --- v07: explicit architecture variants ------------------------------------------------------------------------------
# v06 drew every bay of a section with one rule (the same window and head, an even column pitch, an arcade at a fixed
# pitch across the whole width), so the West Front read as a generic repeated block. v07 replaces the rule with a SMALL
# CLOSED SET of hand-drawn variants assigned bay by bay in the tables below. Nothing in this painter is random.
#   principal-floor windows: T triangular pediment over a balustered apron, S segmental pediment, L cornice on two
#     consoles, A round head with a keystone, D the section's central door-window (taller, balcony slab)
#   attic lights: q square light, x blind relief panel, o oculus
#   columns: the central pavilion pairs its two outer columns (a coupled end, then an even run), as the real West
#     Front's central portico does; the wing porticoes keep an even run
#   ground-floor arcade: one arch under every bay or intercolumniation of the storey above (v06: a fixed 8/10 px
#     pitch unrelated to the bays)
# The building stays symmetric about the axis like the real Capitol; the kind strings are palindromic per section, the
# hand-assigned 2537 states (STATE_*) differ between the halves.
WINDOW_KINDS = ("T", "S", "L", "A", "D")
ATTIC_KINDS = ("q", "x", "o")
CENTER_KIND_L = "ATSTDTSTA"        # CENTER_BAYS_L, outer -> axis
CENTER_ATTIC_L = "xqqqoqqqx"       # blind panels over the end bays, an oculus over the door-window
CORR_KIND_L = "AAA"                # recessed link: a short round-headed arcade, contrasting with the pedimented centre
WING_KIND_L = "LTSSTL"             # WING_BAYS_L: three outer bays either side of the wing portico
WING_ATTIC_L = "qxqqxq"
WING_PORTICO_KIND_L = "LLDLL"      # windows between the six wing-portico columns, a central door-window
PAV_COLS_L = [308, 312, 324, 336, 348, 360]   # central pavilion columns (left x, 3 px): a coupled pair, then even
PAV_UPPER_KIND_L = "LALA"          # upper loggia lights in the four left intercolumniations (outer -> axis)
PAV_DOOR = (370, 4)                # the tall central opening on the axis under the dome (x, width), both tiers
ARCADE_STATE = {411: "ru0", 330: "dw1"}       # ground-floor arches: one bricked up (right), one broken open (left)
QUOINS_L = [66, 183]              # long-short quoin strips at the wing corners (left x of a 2-px strip; mirrored)


def _pav_bays():
    """Left-half intercolumniations of the central pavilion: x of a 3-px light centred in each gap."""
    out = []
    for a, b in zip(PAV_COLS_L, PAV_COLS_L[1:]):
        g0, g1 = a + 3, b - 1
        if g1 - g0 >= 4:
            out.append((g0 + g1) // 2 - 1)
    return out


def window(L, x, y0, y1, state, kind="L", w=3):
    """A window seen through ~200 m of haze (glass is blue-grey, never black). `state` is the hand-assigned 2537
    condition (g glass, d dark, b broken, o boarded, v vine, s scorched); `kind` is one of the v07 head variants."""
    body = {"g": ("hw1", "hw0", "hw0"), "d": ("hw0", "hw0", "hw0"), "b": ("hw0", "dw1", "hw0"),
            "o": ("ru1", "ru0", "ru0"), "v": ("vg2", "vg1", "vg1"), "s": ("dw1", "dw0", "dw1")}[state]
    cols = [body[0]] + [body[1]] * (w - 2) + [body[2]]
    for i in range(w):
        rect(L, x + i, y0, x + i, y1, cols[i])
    mid = x + w // 2 - (1 if w % 2 == 0 else 0)
    if kind == "A":                                                    # round head: top corners stay stone
        px(L, x, y0, "dm5"); px(L, x + w - 1, y0, "dm4")
        rect(L, x, y0 - 1, x + w - 1, y0 - 1, "dm5"); px(L, mid, y0 - 1, "dm6")       # archivolt + keystone
        px(L, x - 1, y0, "dm5"); px(L, x + w, y0, "dm3")
    if state in ("g", "d") and y1 - y0 >= 6:
        ty = y0 + (2 if kind == "A" else (y1 - y0) // 3)
        rect(L, x, ty, x + w - 1, ty, "dm3")                                        # transom / impost bar
    if state == "g":
        px(L, x, y0 + (2 if kind == "A" else 1), "hw2")
        if kind != "A":
            px(L, x + 1, y0 + 1, "hw2")                                             # sky in the upper pane
    if state == "b":
        px(L, x + 1, y0 + 2, "dm2"); px(L, x + w - 1, y0 + (y1 - y0) // 2, "dm3")  # glass shards
    if state == "v":
        px(L, x, y0 + 1, "vg3"); px(L, x + w - 1, y1 + 1, "vg1"); px(L, x + 1, y1 + 2, "vg1")
    if state == "s":
        rect(L, x - 1, y0 - 3, x + w, y0 - 2, "dm2"); px(L, mid, y0 - 4, "dm2")      # soot over the head
    if kind == "D":                                                    # door-window: balcony slab + balusters
        rect(L, x - 3, y1 + 1, x + w + 2, y1 + 1, "dm6")
        for k, xx in enumerate(range(x - 3, x + w + 3)):
            px(L, xx, y1 + 2, "dm3" if k % 2 == 0 else "dm5")
        rect(L, x - 3, y1 + 3, x + w + 2, y1 + 3, "dm2")
    else:
        rect(L, x - 1, y1 + 1, x + w, y1 + 1, "dm5")                                # sill
    if kind == "T":                                                    # triangular pediment, balustered apron
        rect(L, x - 1, y0 - 1, x + w, y0 - 1, "dm2")
        rect(L, x - 1, y0 - 2, x + w, y0 - 2, "dm5")
        rect(L, x, y0 - 3, x + w - 1, y0 - 3, "dm5")
        px(L, mid, y0 - 4, "dm6")
        for k, xx in enumerate(range(x - 1, x + w + 1)):
            px(L, xx, y1 + 2, "dm3" if k % 2 == 0 else "dm4")
    elif kind == "S":                                                  # segmental pediment (curved cap)
        rect(L, x - 1, y0 - 1, x + w, y0 - 1, "dm2")
        px(L, x - 1, y0 - 2, "dm5"); px(L, x + w, y0 - 2, "dm4")
        rect(L, x, y0 - 2, x + w - 1, y0 - 2, "dm4")
        rect(L, x, y0 - 3, x + w - 1, y0 - 3, "dm6")
    elif kind == "L":                                                  # cornice on two consoles
        rect(L, x - 2, y0 - 2, x + w + 1, y0 - 2, "dm6")
        rect(L, x - 1, y0 - 1, x + w, y0 - 1, "dm2")
        px(L, x - 2, y0 - 1, "dm5"); px(L, x + w + 1, y0 - 1, "dm4")
    elif kind == "D":                                                  # broad segmental head over the door-window
        rect(L, x - 1, y0 - 1, x + w, y0 - 1, "dm2")
        rect(L, x - 1, y0 - 2, x + w, y0 - 2, "dm5")
        rect(L, x, y0 - 3, x + w - 1, y0 - 3, "dm6")
        px(L, x - 2, y0 - 2, "dm5"); px(L, x + w + 1, y0 - 2, "dm4")


def attic_light(L, x, y0, y1, kind, state="d"):
    """Attic-storey opening variants: q square light, x blind relief panel (lit upper-left rim, shaded lower-right
    rim), o oculus (a rounded light with a lit ring)."""
    if kind == "x":
        rect(L, x - 1, y0, x + 3, y1, "dm4")
        rect(L, x - 1, y0, x + 3, y0, "dm5"); rect(L, x - 1, y0, x - 1, y1, "dm5")
        rect(L, x - 1, y1, x + 3, y1, "dm3"); rect(L, x + 3, y0 + 1, x + 3, y1, "dm3")
        return
    if kind == "o":
        c = "hw0" if state != "g" else "hw1"
        px(L, x + 1, y0, c); rect(L, x, y0 + 1, x + 2, y1 - 1, c); px(L, x + 1, y1, c)
        px(L, x, y0, "dm5"); px(L, x + 2, y0, "dm5"); px(L, x, y1, "dm3"); px(L, x + 2, y1, "dm3")
        px(L, x - 1, y0 + 1, "dm5"); px(L, x + 3, y1 - 1, "dm3")
        return
    window(L, x, y0, y1, state, "plain")


def arch(L, x, y0, y1, w=3, c="hw0"):
    rect(L, x, y0 + 1, x + w - 1, y1, c)
    rect(L, x + 1, y0, x + w - 2, y0, c)
    px(L, x - 1, y0, "dm5"); px(L, x + w, y0, "dm5")
    px(L, x, y0, "dm3"); px(L, x + w - 1, y0, "dm3")


def column(L, x, y0, y1, cap=True):
    """3-px column lit from the front-left: lit, mid and shade stripes, a capital and a base; the wall to its right
    takes a one-texel cast shadow."""
    rect(L, x, y0, x, y1, "dm6"); rect(L, x + 1, y0, x + 1, y1, "dm5"); rect(L, x + 2, y0, x + 2, y1, "dm3")
    if cap:
        rect(L, x - 1, y0, x + 3, y0, "dm5"); px(L, x + 3, y0, "dm3")
        rect(L, x - 1, y1, x + 3, y1, "dm5")
    for y in range(y0 + 1, y1):
        if x + 3 < W and L[y, x + 3] in (I["dm2"], I["dm3"], I["dm4"]):
            L[y, x + 3] = I["dm1"]


def quoin_strip(L, x, y0, y1):
    """Long-short quoins at a projecting corner: 3-row blocks 2 px wide alternating with 2-row blocks 1 px wide,
    lit top rows, mid-tone joints (corner punctuation instead of a flat sheet)."""
    y, k = y0, 0
    while y <= y1:
        hgt, wid = (3, 2) if k % 2 == 0 else (2, 1)
        for j in range(hgt):
            if y + j > y1:
                break
            for i in range(wid):
                if L[y + j, x + i] in (I["dm4"], I["dm5"]):
                    L[y + j, x + i] = I["dm5"] if j == 0 else I["dm4"] if i == 0 else I["dm3"]
        if y + hgt <= y1:
            rect(L, x, y + hgt, x + 1, y + hgt, "dm3")
        y += hgt + 1
        k += 1


def bay_layout():
    """Every opening of the West Front as one explicit record (x, row range, kind, state, width, half). Both halves:
    the right half mirrors the positions and kinds; the states come from the hand-assigned STATE_* strings."""
    recs = []
    for side in ("L", "R"):
        mx = (lambda x, w=3: x) if side == "L" else mirror_x
        for (bx, k, a, st) in zip(CENTER_BAYS_L, CENTER_KIND_L, CENTER_ATTIC_L, STATE_CENTER[side]):
            recs.append(("center-main", mx(bx, 3), 124, 136, k, st, 3, side))
            recs.append(("center-attic", mx(bx, 3), 113, 116, a, "d", 3, side))
        for (bx, k, st) in zip(CORRIDOR_BAYS_L, CORR_KIND_L, STATE_CORR[side]):
            recs.append(("corridor-main", mx(bx, 3), 125, 135, k, st, 3, side))
        r = SECTIONS_L[0][3]
        for (bx, k, a, st) in zip(WING_BAYS_L, WING_KIND_L, WING_ATTIC_L, STATE_WING[side]):
            recs.append(("wing-main", mx(bx, 3), 125, 136, k, st, 3, side))
            recs.append(("wing-attic", mx(bx, 3), r + 8, r + 9, a, "d", 3, side))
        for (cx, k) in zip(WING_COLS_L[:-1], WING_PORTICO_KIND_L):
            recs.append(("wing-portico", mx(cx + 5, 3), 126, 137, k, "d", 3, side))
            recs.append(("wing-portico-attic", mx(cx + 5, 3), r + 8, r + 9, "q", "d", 3, side))
        for (bx, k) in zip(_pav_bays(), PAV_UPPER_KIND_L):
            recs.append(("pavilion-upper", mx(bx, 3), 118, 126, k, "d", 3, side))
            recs.append(("pavilion-lower", mx(bx, 3), 131, 139, "L", "d", 3, side))
    return recs


def arcade_layout():
    """Ground-floor arch x positions: one under every bay / intercolumniation above, both halves (x, width)."""
    xs = []
    for side in ("L", "R"):
        mx = (lambda x, w=3: x) if side == "L" else mirror_x
        for bx in CENTER_BAYS_L + CORRIDOR_BAYS_L + WING_BAYS_L + [c + 5 for c in WING_COLS_L[:-1]]:
            xs.append((mx(bx, 3), 3))
        for bx in _pav_bays():
            xs.append((mx(bx, 3), 3))
    xs.append((PAV_DOOR[0], PAV_DOOR[1]))
    return sorted(set(xs))


def paint_west_front():
    L = new()
    spans = []
    for name, x0, x1, r in SECTIONS_L:
        spans.append((name, x0, x1, r))
        spans.append((name, mirror_x(x1), mirror_x(x0), r))
    # --- section bodies, roof balustrades, cornices (symmetric masses; unchanged from v06, so the silhouette is v06's)
    for name, x0, x1, r in spans:
        rect(L, x0, r, x1, FACADE_BOTTOM, "dm4")
        rect(L, x0, r, x1, r, "dm5")                                        # balustrade rail
        for x in range(x0, x1 + 1):
            c = "dm2" if x % 3 == 2 else "dm4"
            px(L, x, r + 1, c); px(L, x, r + 2, c)                          # balusters
        rect(L, x0, r + 3, x1, r + 3, "dm4")
        rect(L, x0, r + 4, x1, r + 4, "dm6")                                # cornice lit edge
        rect(L, x0, r + 5, x1, r + 5, "dm2")                                # soffit shadow
        for x in range(x0, x1 + 1, 2):
            px(L, x, r + 5, "dm3")                                          # modillions
        rect(L, x0, r + 6, x1, r + 6, "dm3")                                # frieze
        rect(L, x0, STRING, x1, STRING, "dm5"); rect(L, x0, STRING + 1, x1, STRING + 1, "dm2")
        for y in range(GROUND_FLOOR[0], GROUND_FLOOR[1] + 1, 3):           # rusticated ground floor (banded joints)
            rect(L, x0, y, x1, y, "dm3")
        for y0 in range(GROUND_FLOOR[0], GROUND_FLOOR[1], 3):
            off = 0 if (y0 // 3) % 2 else 4
            for x in range(x0 + off, x1 + 1, 8):
                px(L, x, y0 + 1, "dm3")
        rect(L, x0, FACADE_BOTTOM, x1, FACADE_BOTTOM, "dm2")
    # --- v07: ground-floor arcade aligned with the bays above (hand-assigned states for two arches)
    for (x, w) in arcade_layout():
        arch(L, x, 151, 168, w, ARCADE_STATE.get(x, "hw0"))
    # --- per-section walls, entablatures, colonnades (unchanged masses), then every opening from the bay table
    for name, x0, x1, r in SECTIONS_L:
        for side in ("L", "R"):
            mx = (lambda x, w=1: x) if side == "L" else mirror_x
            a, b = (x0, x1) if side == "L" else (mirror_x(x1), mirror_x(x0))
            if name == "pavilion":
                rect(L, a, r + 7, b, r + 11, "dm4"); rect(L, a, r + 9, b, r + 9, "dm3")    # attic over the colonnade
                rect(L, a, r + 12, b, r + 12, "dm5"); rect(L, a, r + 13, b, r + 13, "dm3")  # entablature
                rect(L, a, r + 14, b, 141, "dm2")                                          # loggia wall in shade
                for bx in _pav_bays():
                    ax = mx(bx, 3) if side == "R" else bx
                    rect(L, ax, r + 8, ax + 2, r + 10, "hw0")                              # attic lights
                    rect(L, ax + 1, r + 8, ax + 1, r + 10, "dm3")                          # attic mullion
                rect(L, a, 142, b, 142, "dm5")
            elif name == "center":
                rect(L, a, 119, b, 119, "dm5"); rect(L, a, 120, b, 120, "dm3")             # sill course of the attic
                for bx in CENTER_BAYS_L:
                    p = mirror_x(bx - 4, 2) if side == "R" else bx - 4                    # 2-px pilaster, lit left
                    rect(L, p, 121, p, 141, "dm5"); rect(L, p + 1, 121, p + 1, 141, "dm3")
            elif name == "wing":
                rect(L, a, r + 7, b, r + 10, "dm4"); rect(L, a, r + 9, b, r + 9, "dm3")
                p0, p1 = WING_PORTICO_L
                pa, pb = (p0, p1) if side == "L" else (mirror_x(p1), mirror_x(p0))
                rect(L, pa, r + 11, pb, 141, "dm2")                                       # portico wall in shade
    # the central door-window under the dome: one tall opening through both loggia tiers
    dx, dw = PAV_DOOR
    rect(L, dx, 117, dx + dw - 1, 139, "hw0"); rect(L, dx + 1, 116, dx + dw - 2, 116, "hw0")
    rect(L, dx, 128, dx + dw - 1, 128, "dm3")                                             # transom
    px(L, dx, 117, "dm3"); px(L, dx + dw - 1, 117, "dm3"); px(L, dx + 1, 115, "dm5"); px(L, dx + 2, 115, "dm5")
    rect(L, dx - 3, 140, dx + dw + 2, 140, "dm6")                                         # balcony slab
    for k, xx in enumerate(range(dx - 3, dx + dw + 3)):
        px(L, xx, 141, "dm3" if k % 2 == 0 else "dm5")
    for (kind, x, y0, y1, k, st, w, side) in bay_layout():
        if kind.endswith("attic"):
            if k == "q":
                window(L, x, y0, y1, st, "plain", w)
            else:
                attic_light(L, x, y0, y1, k, st)
        else:
            window(L, x, y0, y1, st, k, w)
    # columns over the openings (pavilion pairs, wing portico)
    for side in ("L", "R"):
        for cx in PAV_COLS_L:
            column(L, cx if side == "L" else mirror_x(cx, 3), SECTIONS_L[3][3] + 14, 141)
        for cx in WING_COLS_L:
            column(L, cx if side == "L" else mirror_x(cx, 3), SECTIONS_L[0][3] + 11, 141)
    # --- asymmetric sunlight on the projections: a projecting section's left return is lit, a recessed section
    #     right of a projection takes its cast shadow
    names_ = [section_at(x)[0] if section_at(x) else None for x in range(W)]
    for x in range(1, W):
        a, b = names_[x - 1], names_[x]
        if a and b and a != b:
            top = section_at(x)[3]
            if PROJECTION[b] > PROJECTION[a]:
                rect(L, x, top + 4, x, 141, "dm6")
            else:
                for y in range(top + 4, FACADE_BOTTOM + 1):
                    for dx_ in (0, 1, 2):
                        if 0 <= x + dx_ < W and L[y, x + dx_] in (I["dm4"], I["dm5"], I["dm6"]):
                            L[y, x + dx_] = I["dm2"] if dx_ == 0 else I["dm3"]
    rect(L, 65, 109, 65, FACADE_BOTTOM, "dm6")                             # Senate wing end, sunlit
    # v07: a shallow frontispiece round the centre section's door-window bay (a mid-section accent in each half)
    for side in ("L", "R"):
        bx = CENTER_BAYS_L[CENTER_KIND_L.index("D")]
        a, b = (bx - 4, bx + 6) if side == "L" else (mirror_x(bx + 6), mirror_x(bx - 4))
        for y in range(113, 142):
            for x in range(a, b + 1):
                if L[y, x] == I["dm4"]:
                    L[y, x] = I["dm5"]
        rect(L, a, 113, a, 141, "dm6")
        rect(L, b + 1, 113, b + 1, 141, "dm3")
    for x in QUOINS_L + [mirror_x(q, 2) for q in QUOINS_L]:              # v07: quoins at the wing corners
        sec = section_at(x)
        if sec and x + 1 < W:
            quoin_strip(L, x, sec[3] + 7, 141)
    # --- 2537 damage to the colonnades (hand-assigned, right half only)
    pav_r = sorted(mirror_x(x, 3) for x in PAV_COLS_L)
    for i in PAV_COL_MISSING_R:
        x = pav_r[i]
        rect(L, x, 115, x + 2, 141, "dm2")
        for wy0, wy1 in ((118, 126), (131, 139)):
            rect(L, x, wy0, x + 2, wy1, "hw0")
        rect(L, x, 136, x + 2, 141, "dm3"); px(L, x + 1, 135, "dm3")        # stump
        rect(L, x - 1, 114, x + 3, 114, "dm3")
        rect(L, x - 2, 141, x + 5, 141, "dm4"); px(L, x + 4, 140, "dm3")    # drum on the floor
    wing_r = sorted(mirror_x(x, 3) for x in WING_COLS_L)
    for i in WING_COL_TOPPLED_R:
        x = wing_r[i]
        if x + 2 < W:
            rect(L, x, 121, x + 2, 135, "dm2")
            rect(L, x - 4, 138, x + 6, 140, "dm4"); rect(L, x - 4, 138, x + 6, 138, "dm5")
            rect(L, x - 4, 141, x + 6, 141, "dm2")
    return L


def facade_variant_summary():
    """Closed-set audit of the bay table: kinds used per family and the number of openings (for the manifest)."""
    recs = bay_layout()
    main = [r for r in recs if not r[0].endswith("attic")]
    att = [r for r in recs if r[0].endswith("attic")]
    return {"openings": len(recs), "window_kinds_used": sorted({r[4] for r in main}),
            "attic_kinds_used": sorted({r[4] for r in att}), "window_kinds_allowed": list(WINDOW_KINDS),
            "attic_kinds_allowed": list(ATTIC_KINDS),
            "all_kinds_in_closed_set": all(r[4] in WINDOW_KINDS for r in main) and
            all(r[4] in ATTIC_KINDS for r in att),
            "pavilion_columns_left": PAV_COLS_L, "arcade_arches": len(arcade_layout()),
            "states_left_right_differ": STATE_CENTER["L"] != STATE_CENTER["R"]}


# ============================================================================ 4b facade weathering (v07, from v05t)
# v05t's lesson: weathering must be authored per feature (a run below THIS sill, a stain under THAT cornice), not a
# per-column rule. Every entry below is hand-placed against the v07 bay table; nothing is scattered at random.
# (kind, x, top row, length, width): rain = one value step down on the stone, broken toward its tail; soot = dark
# tongue rising above a burnt opening (length counts upward); rust = iron-stain run from a cramp or bent beam
FACADE_RUNS = [
    ("rain", 74, 117, 8, 1), ("rain", 89, 117, 5, 1), ("rain", 166, 117, 10, 2), ("rain", 181, 117, 6, 1),
    ("rain", 192, 123, 12, 1), ("rain", 204, 123, 7, 2), ("rain", 217, 123, 15, 1),
    ("rain", 233, 121, 3, 1), ("rain", 277, 121, 2, 1), ("rain", 246, 140, 3, 1), ("rain", 291, 140, 3, 1),
    ("rain", 316, 108, 4, 1), ("rain", 351, 108, 3, 1), ("rain", 427, 108, 5, 1),
    ("rain", 446, 121, 4, 1), ("rain", 489, 140, 3, 2), ("rain", 508, 121, 3, 1),
    ("rain", 530, 123, 14, 2), ("rain", 546, 117, 9, 1),
    ("soot", 462, 121, 7, 3), ("soot", 453, 121, 5, 2), ("soot", 523, 131, 8, 3),
    ("rust", 566, 122, 9, 1), ("rust", 552, 118, 6, 1), ("rust", 586, 136, 7, 1),
]
# (x, y, w, h, tone): new = a replaced, paler block; dark = weathered / dirt-stained block; green = algae on a damp
# course. Sizes are whole blocks at 2.67 px/m (about 1.5 x 0.75 m per 4 x 2 px).
FACADE_PATCHES = [
    (70, 116, 14, 1, "dark"), (154, 116, 10, 1, "dark"), (186, 121, 36, 2, "dark"), (68, 138, 22, 3, "green"),
    (160, 129, 5, 2, "new"), (89, 139, 6, 2, "new"), (230, 138, 8, 2, "dark"), (283, 122, 6, 2, "new"),
    (294, 139, 8, 2, "green"), (440, 138, 9, 2, "green"), (471, 122, 5, 2, "new"), (504, 137, 7, 3, "dark"),
    (522, 121, 14, 2, "dark"), (536, 132, 5, 2, "new"), (548, 125, 6, 3, "new"), (556, 136, 7, 2, "new"),
    (400, 112, 10, 2, "dark"), (330, 108, 7, 1, "new"),
]
FACADE_DAMP = [(66, 185, 5), (186, 221, 6), (222, 305, 4), (306, 437, 2), (438, 521, 5), (522, 563, 7)]
STONE_UP = {"dm2": "dm3", "dm3": "dm4", "dm4": "dm5", "dm5": "dm6"}
STONE_DN = {"dm6": "dm5", "dm5": "dm4", "dm4": "dm3", "dm3": "dm2", "dm2": "dm1"}


def paint_facade_weathering(front):
    """Authored weathering over the West Front (only on its stone texels; the House-wing void is cut later)."""
    L = new()
    name_of = {I[n]: n for n in ("dm1", "dm2", "dm3", "dm4", "dm5", "dm6")}

    def stone(x, y):
        return 0 <= x < W and 0 <= y < H and int(front[y, x]) in name_of

    for (kind, x, y0, ln, w) in FACADE_RUNS:
        for j in range(ln):
            y = y0 - j if kind == "soot" else y0 + j
            tail = j > ln * 0.6
            if tail and (j + x) % 3 == 0:
                continue
            ww = w - (1 if tail and w > 1 else 0)
            for i in range(ww):
                xi = x + i - (ww // 2 if kind == "soot" else 0)
                if not stone(xi, y):
                    continue
                c = name_of[int(front[y, xi])]
                if kind == "rain":
                    L[y, xi] = I[STONE_DN.get(c, c)]
                elif kind == "soot":
                    L[y, xi] = I["dw1"] if j < ln * 0.45 else I["dm2"]
                else:
                    L[y, xi] = I["ru0"] if j < ln * 0.4 else I["ru1"]
    for (x, y, w, h, tone) in FACADE_PATCHES:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if not stone(xx, yy) or L[yy, xx] >= 0:
                    continue
                c = name_of[int(front[yy, xx])]
                if tone == "new":
                    L[yy, xx] = I[STONE_UP.get(c, c)]
                elif tone == "dark":
                    L[yy, xx] = I[STONE_DN.get(c, c)]
                else:
                    L[yy, xx] = I["vg1"] if (xx + yy) % 3 == 0 else I[STONE_DN.get(c, c)]
    # rising damp at the facade foot, just above the terrace rail (irregular top, moss line in the last row)
    for k, (x0, x1, hmax) in enumerate(FACADE_DAMP):
        for x in range(x0, x1 + 1):
            hh = int(round(hmax * (0.45 + 0.55 * vn1(("fdamp", k), x / 5.0))))
            for j in range(hh):
                y = T_RAIL - 1 - j
                if not stone(x, y) or L[y, x] >= 0:
                    continue
                c = name_of[int(front[y, x])]
                if j == 0 and (x + k) % 4 != 1:
                    L[y, x] = I["vg0"]
                elif j < hh - 1 or x % 2 == 0:
                    L[y, x] = I[STONE_DN.get(c, c)]
    return L


# ============================================================================ 5 Capitol ruin overlay
def ivy_curtain(L, base, x0, top, length, width, key, ramp=("vg0", "vg1", "vg2", "vg3")):
    """Ivy hanging from a cornice: a leaf mass whose hem is a ragged lobed curve (two noise octaves along x, longest
    near the middle), a few tendrils running further down, and 2x2 leaf clumps lit on their upper-left -- no vertical
    stripes. Only drawn over texels of `base` (the wall it clings to)."""
    for k in range(width):
        x = x0 + k
        if not 0 <= x < W:
            continue
        u = (k + 0.5) / width
        env = math.sin(math.pi * min(1.0, 0.15 + 0.85 * u)) ** 0.6
        lobe = 0.55 + 0.30 * vn1(key, x / 5.0) + 0.15 * vn1((key, "f"), x / 1.7)
        ln = int(length * env * lobe)
        if hval(key, "tendril", k) < 0.10:
            ln = int(ln * 1.45) + 2
        for y in range(top, top + ln):
            if not 0 <= y < H or base[y, x] < 0:
                continue
            cx, cy = (x + (y // 2) % 2) // 2, y // 2
            v = hval(key, "clump", cx, cy)
            sub = (x + (y // 2) % 2) % 2 == 0 and y % 2 == 0                 # upper-left texel of the clump
            c = ramp[1] if v < 0.45 else ramp[2] if v < 0.85 else ramp[0]
            if sub and v >= 0.45:
                c = ramp[3] if v < 0.85 else ramp[2]
            if y >= top + ln - 2 and hval(key, "hem", x, y) < 0.45:
                continue                                                     # ragged hem
            if k in (0, width - 1) and hval(key, "edge", y) < 0.5:
                continue
            px(L, x, y, c)


def vn1(key, t):
    """Smooth 1-D value noise in [0, 1] (cosine interpolated lattice)."""
    i = math.floor(t)
    f = t - i
    a, b = hval(key, "vn1", i), hval(key, "vn1", i + 1)
    w = (1 - math.cos(math.pi * f)) * 0.5
    return a * (1 - w) + b * w


def roof_scrub(L, x, hw, hgt, key):
    """Scrub mat rooted on a section's parapet: a low irregular mound (base sunk one row into the balustrade), lit on
    its upper-left, with a few strands drooping over the cornice."""
    sec = section_at(x)
    if not sec:
        return
    r = sec[3]
    for xx in range(x - hw, x + hw + 1):
        if not 0 <= xx < W:
            continue
        u = (xx - x) / max(1, hw)
        h = hgt * max(0.0, 1 - u * u) ** 0.7 * (0.65 + 0.35 * vn1(key, xx / 2.3))
        h = max(1, int(round(h)))
        for j in range(h + 2):
            y = r + 1 - j
            t = j / max(1, h + 1)
            c = "vg0" if j == 0 else "vg1" if t < 0.45 else "vg2" if t < 0.85 or u > 0.2 else "vg3"
            if j == h + 1 and hval(key, "tip", xx) < 0.5:
                continue
            px(L, xx, y, c)
        if hval(key, "droop", xx) < 0.22:
            for j in range(2, 3 + int(hval(key, "dl", xx) * 4)):
                px(L, xx, r + j, "vg1" if j % 2 else "vg0")


def paint_capitol_ruin(front):
    L = new()
    for (x, top, length, w) in IVY_WING_L:
        ivy_curtain(L, front, x, top, length, w, ("ivy", x))
    for (x, hw, hgt) in ROOF_SHRUBS:
        roof_scrub(L, x, hw, hgt, ("roof", x))
    x, roof, hgt = ROOF_SAPLING                                            # self-sown tree on the corridor roof
    for y in range(roof - hgt + 8, roof + 1):
        px(L, x + (1 if y < roof - 8 else 0), y, "b1")
    crown_lobes(L, [(x - 3, roof - hgt + 6, 6), (x + 4, roof - hgt + 4, 6), (x + 1, roof - hgt + 10, 5)], VG,
                VG_CUTS, "roofsap", squash=0.85, leaf=2)
    # House (south) wing collapse: everything above the broken profile is removed (sky shows through); the broken
    # edge shows the hazed interior, three exposed floor slabs and bent iron
    prof = np.interp(np.arange(W), [p[0] for p in HOUSE_COLLAPSE], [p[1] for p in HOUSE_COLLAPSE], left=-1, right=-1)
    for x in range(HOUSE_COLLAPSE[0][0], W):
        top = int(prof[x])
        depth = 4 + int(hval("hdepth", x // 2) * 4)
        for y in range(top, top + depth):
            px(L, x, y, "dw1" if y < top + depth - 2 else "hw0")
        px(L, x, top + depth, "dm2")
    for (x, y, w) in SOOT:
        for k in range(w):
            if hval("soot", x, k) < 0.7:
                px(L, x + (k % 3) - 1, y - k, "dm2" if k < w // 2 else "dm3")
    for pts in FACADE_CRACKS:
        for (a, b) in zip(pts, pts[1:]):
            line(L, a[0], a[1], b[0], b[1], "dm2")
    for (x, y, ln) in STREAKS:                                             # rain streaks below the cornices
        for k in range(ln):
            if front[y + k, x] >= 0 and hval("streak", x, k) < 0.8:
                px(L, x, y + k, "ws0")
    # blast hole in the right pavilion attic, scorch fanning up from it
    rect(L, 397, 108, 404, 110, "dw1"); rect(L, 398, 107, 403, 107, "hw0"); px(L, 405, 109, "dm2")
    for (x, y) in ((396, 106), (399, 105), (402, 104), (405, 106), (407, 107)):
        px(L, x, y, "dm2")
    return L


def collapse_debris():
    """Pieces at the broken edge that stick out into the open air of the House wing bite (kept after the void is cut):
    exposed floor slabs with a sagging lip, bent iron beams, scrub rooted on two slabs."""
    L = new()
    for (y, x0, x1) in HOUSE_SLABS:
        rect(L, x0, y, x1, y, "dm4"); rect(L, x0, y + 1, x1, y + 1, "dm2")
        px(L, x0 + (x1 - x0) // 2, y + 2, "dm2")
    for (x, y0, y1) in HOUSE_BEAMS:
        line(L, x, y1, x + 3, y0, "ru0"); px(L, x + 3, y0 - 1, "ru1"); px(L, x + 4, y0, "ru0")
    for (x, hw, h, sy) in ((572, 4, 3, HOUSE_SLABS[0][0]), (619, 4, 3, HOUSE_SLABS[2][0])):
        for xx in range(x - hw, x + hw + 1):
            hh = max(1, int(h * (1 - ((xx - x) / (hw + 1)) ** 2) * (0.6 + 0.4 * hval("slabw", xx))))
            for j in range(hh):
                px(L, xx, sy - 1 - j, "vg1" if j < hh - 1 else "vg2")
    return L


def house_void():
    """Mask of facade texels removed by the House wing collapse (sky shows through)."""
    prof = np.interp(np.arange(W), [p[0] for p in HOUSE_COLLAPSE], [p[1] for p in HOUSE_COLLAPSE])
    return (XX >= HOUSE_COLLAPSE[0][0]) & (YY < prof[None, :].repeat(H, 0))


# ============================================================================ 5b v08 ruin state: two specific collapses
# Codex on v07 at 640x360: the dome and layout read, but the building feels overly intact and repetitive. v08 makes
# the 2537 ruin state legible at gameplay size with TWO specific, differently-told collapses, placed so neither is
# the mirror of the other or of v07's House-wing bite (mirror x' = 743 - x):
#   A "south breach" (x 466..562): the outer five bays of the south centre section and the whole south connecting
#     corridor are gutted -- roof and upper front wall gone down to the principal floor in stepped masonry breaks,
#     the back (east) wall of the range left standing in pieces with empty windows against the sky, broken floor
#     slabs, a self-sown Ailanthus inside, one section-end pier left standing as a tooth, and a fresh grey rubble cone
#     burying the ground-floor arcade and the terrace balustrade below. Story: the patrol walker stands guard in front,
#     a patrol relay (red light) is bolted to the tooth, the breach edges are scorched (blasted, not just decayed),
#     a long-dead walker lies half buried in the cone, and the survey team has marked it: an orange spray X on the
#     intact wall, two pennant stakes and a prism pole on the cone, safety tape along the terrace foot.
#   B "north end" (x 65..121): the outer corner of the Senate wing fell long ago -- a stepped break down to the
#     principal floor, a broken corner pier, a mature tree grown up through the shell above the roofline, ivy re-hung
#     from the broken lip, and an old spill over the terrace that is now grass and scrub.
#   Plus three small balustrade losses (sky notches) and one vine curtain on the north centre section, so the
#   roofline is no longer one continuous intact run.
# The dome and the central pavilion (x 306..437) are untouched, so the Capitol outline stays recognisable.
# Broken masonry is drawn as STEPPED courses (horizontal treads lit, left-facing risers lit, right-facing risers in
# shade): a smooth 1-px lit diagonal read as a garland in the first preview.
BREACH_A_KEYS = [(466, 106), (469, 107), (474, 113), (480, 119), (486, 126), (492, 131), (498, 136), (504, 138),
                 (509, 140), (513, 134), (516, 124)]                   # south centre bays, smooth guide
TOOTH_A = (517, 522, 109)                                               # section-end pier left standing (x0, x1, row)
BREACH_A_CORR_KEYS = [(523, 114), (527, 123), (533, 130), (538, 133), (544, 130), (550, 124), (555, 118),
                      (559, 112), (562, 109)]                           # south corridor, smooth guide
BREACH_B_KEYS = [(65, 126), (68, 126), (70, 133), (74, 140), (80, 141), (86, 137), (92, 131), (98, 126),
                 (104, 120), (110, 115), (116, 111), (121, 109)]
# back (east) wall of each gutted range: runs (x0, x1, top row) with gaps where it is gone too (sky down to the lip)
BACK_A = [(470, 476, 114), (477, 482, 117), (483, 489, 113), (497, 503, 119), (504, 509, 116), (510, 513, 121),
          (526, 531, 121), (532, 538, 118), (546, 552, 122)]
BACK_B = [(71, 77, 118), (88, 92, 126)]
BACK_HOLES = [(472, 117, 3, 5), (485, 116, 3, 5), (499, 122, 3, 5), (528, 124, 2, 5), (534, 121, 3, 6),
              (548, 125, 2, 4), (73, 121, 2, 4)]                        # empty windows in the back walls: the sky
CROSSWALLS_A = [(494, 496, 112), (539, 540, 120)]                      # party walls seen end-on (x0, x1, top)
SLABS_A = [(470, 489, 121), (497, 512, 130), (526, 537, 128)]          # floor slabs still spanning: x0, x1, row
AILANTHUS_A = [(491, 113, 6.0), (497, 109, 5.0), (486, 118, 5.0), (494, 119, 5.5), (500, 116, 4.5)]
AILANTHUS_A_TRUNK = (493, 120, 132)                                     # x, top row, root row
TREE_B = [(101, 106, 9.5), (110, 100, 7.0), (93, 111, 6.5), (104, 95, 6.5), (95, 100, 5.5), (112, 110, 5.5)]
TREE_B_TRUNK = (100, 114, 141)
ROOF_NOTCHES = [(148, 156, 109), (284, 292, 106), (446, 451, 106)]      # balustrade lost: x0, x1, roof row
CENTRE_VINE_L = (272, 107, 30, 15)                                      # ivy: x0, top, max length, width
# rubble cones over the terrace: (polyline of the top edge, left toe -> right toe); bottom = terrace foot row
CONE_A = [(462, 186), (466, 178), (470, 169), (474, 161), (479, 153), (485, 148), (491, 145), (497, 143),
          (503, 142), (509, 143), (515, 146), (520, 150), (525, 148), (530, 150), (536, 155), (543, 159),
          (550, 162), (556, 167), (561, 173), (565, 180), (568, 186)]
CONE_B = [(48, 186), (54, 177), (60, 168), (66, 160), (72, 154), (78, 151), (84, 151), (91, 154),
          (98, 159), (104, 165), (110, 172), (116, 179), (121, 186)]
CONE_A_FRAGMENTS = [  # hand-placed recognisable pieces: what fell from where
    ("cornice", 474, 159, 497, 151),            # a 9 m length of the main cornice, slid down the left flank
    ("wallpiece", 500, 147, 11, 8),             # a fallen piece of front wall with one window opening
    ("balustrade", 515, 157, 531, 162),         # a length of roof balustrade, balusters still in place
    ("drum", 536, 165, 5, 4), ("drum", 490, 172, 5, 4), ("drum", 549, 172, 4, 3),
    ("block", 470, 175, 6, 3), ("block", 521, 170, 7, 3), ("block", 557, 178, 5, 3), ("block", 505, 178, 6, 3),
    ("block", 482, 163, 5, 3), ("block", 528, 177, 5, 2),
]
CONE_A_GRASS = [(468, 182, 6, 4), (481, 179, 5, 3), (557, 182, 7, 4), (529, 183, 9, 3)]
CONE_A_SCRUB = [(474, 170, 4), (562, 173, 4)]
CONE_B_BLOCKS = [(76, 158, 6, 2), (92, 162, 5, 2), (84, 172, 7, 3), (104, 176, 5, 2)]
CONE_B_SCRUB = [(80, 156, 6), (97, 162, 5), (111, 176, 4), (66, 168, 5)]
SURVEY_X = (461, 145)              # orange spray X (5x5) on the intact wall at the breach's left edge
SURVEY_PENNANTS = [(478, 160), (543, 160)]          # stake foot (x, row): 7-px stake, 2x2 safety-orange flag
SURVEY_PRISM = (520, 152)          # prism pole foot on the cone (cyan reflector on top)
SURVEY_TAPE = [(458, 182), (497, 185), (533, 183), (571, 184)]   # posts along the terrace foot, tape sags between
PATROL_RELAY = (518, 109)          # relay box on the tooth (red light on an antenna)
SCORCH_A = [(468, 109, 6, 14), (465, 116, 4, 10), (523, 114, 4, 12), (560, 112, 4, 11), (516, 126, 3, 8)]
DORMANT_WALKER = (546, 177)        # a second, long-dead patrol walker half buried in the cone (dead grey eye)


def _steps(keys, key, w0=3, w1=6, q=2):
    """A stepped broken-masonry top: the smooth guide through `keys` cut into runs of 3..6 px, each at one row
    (rounded to the 2-row block course). The end runs keep the exact end rows so the break meets the roofline."""
    xs = [k[0] for k in keys]
    guide = np.interp(np.arange(W), xs, [k[1] for k in keys])
    out = {}
    x = xs[0]
    while x <= xs[-1]:
        w = w0 + int(hval(key, "w", x) * (w1 - w0 + 1))
        seg = list(range(x, min(x + w, xs[-1] + 1)))
        row = int(round(float(np.mean(guide[seg])) / q) * q)
        if x == xs[0]:
            row = keys[0][1]
        if seg[-1] == xs[-1]:
            row = keys[-1][1]
        for xx in seg:
            out[xx] = row
        x += w
    return out


def breach_tops():
    """Column -> first remaining front-wall row for every broken column (A, its tooth, its corridor, and B)."""
    tops = {}
    tops.update(_steps(BREACH_A_KEYS, "stA"))
    x0, x1, r = TOOTH_A
    for x in range(x0, x1 + 1):
        tops[x] = r
    tops.update(_steps(BREACH_A_CORR_KEYS, "stAc"))
    tb = _steps(BREACH_B_KEYS, "stB")
    return {"A": tops, "B": tb}


def _void_from(tops):
    m = np.zeros((H, W), bool)
    for x, r in tops.items():
        m[:r, x] = True
    return m


def notch_void():
    m = np.zeros((H, W), bool)
    for (x0, x1, r) in ROOF_NOTCHES:
        m |= box(x0, r, x1, r + 2)
    return m


def ruin_voids():
    """Every West Front texel removed in v08: v07's House-wing bite plus breach A, breach B and the notches."""
    t = breach_tops()
    return {"house_v07": house_void(), "breach_a": _void_from(t["A"]), "breach_b": _void_from(t["B"]),
            "roof_notches": notch_void()}


def paint_breach_interiors():
    """Seen through the two breaches, BEHIND the West Front layer: the standing pieces of the back walls of the gutted
    ranges (inner faces, soot-grimed and in the shade of the party walls: hazed mid-dark, lit top course) with empty windows
    that show the sky, party walls seen end-on, broken floor slabs with the shadow under them, and the trees that
    grew up inside the shells. Where the back wall is gone too, the sky shows down to the broken front lip."""
    L = new()
    for runs in (BACK_A, BACK_B):
        for (x0, x1, top) in runs:
            for x in range(x0, x1 + 1):
                t = top + (1 if hval("bwt", x) < 0.25 else 0)
                rect(L, x, t, x, 170, "dm1")
                px(L, x, t, "dm3"); px(L, x, t + 1, "dm2")
                if (x - x0) % 5 == 4:
                    rect(L, x, t + 4, x, t + 4, "dw1")                         # a joint here and there
            rect(L, x1, top + 1, x1, 170, "dw1")                                # shaded broken end
    for (x, y, w, h) in BACK_HOLES:                                             # empty windows: the sky shows
        rect(L, x, y, x + w - 1, y + h - 1, -1)
        rect(L, x, y + h, x + w - 1, y + h, "dw1")
    for (x0, x1, top) in CROSSWALLS_A:                                          # party walls end-on
        rect(L, x0, top, x1, 170, "dm2"); rect(L, x1, top + 1, x1, 170, "dw1"); px(L, x0, top, "dm4")
    for (x0, x1, y) in SLABS_A:                                                 # slabs + shadow below
        rect(L, x0, y, x1, y, "dm4")
        rect(L, x0, y + 1, x1, y + 2, "dw0")
        px(L, x1 + 1, y + 1, "dm3"); px(L, x1 + 1, y + 2, "dw0")              # sagging, cracked end
    tx, t0, t1 = AILANTHUS_A_TRUNK
    rect(L, tx, t0, tx, t1, "b1"); line(L, tx, t0 + 3, tx - 4, t0 - 1, "b1"); line(L, tx, t0 + 1, tx + 4, t0 - 4, "b1")
    crown_lobes(L, AILANTHUS_A, MG, MID_CUTS, "ailanthusA", squash=0.8, leaf=2)
    tx, t0, t1 = TREE_B_TRUNK
    rect(L, tx, t0, tx + 1, t1, "b1"); rect(L, tx + 1, t0, tx + 1, t1, "b0")
    line(L, tx, t0 + 4, tx - 8, t0 - 3, "b1"); line(L, tx + 1, t0 + 2, tx + 9, t0 - 9, "b1")
    crown_lobes(L, cluster_lobes(TREE_B, "treeB"), MG, MID_CUTS, "treeB", squash=0.85, leaf=2)
    _hazed(L, L >= 0, 0.18)
    return L


def paint_breach_edges(front):
    """Over the West Front (capitol-ruin layer): each stepped break gets lit treads, a lit left-facing riser or a
    shaded right-facing riser, the course below the tread one value down; windows cut by the break are blown out
    (interior shadow); scorch tongues round breach A; ivy re-hung from breach B's lip; the survey X; the relay."""
    L = new()
    for side, tops in breach_tops().items():
        xs = sorted(tops)
        for x in xs:
            y = tops[x]
            while y <= FACADE_BOTTOM and front[y, x] < 0:
                y += 1
            if y > FACADE_BOTTOM:
                continue
            l, r = tops.get(x - 1, y), tops.get(x + 1, y)
            px(L, x, y, "dm6" if hval("lip", side, x) < 0.8 else "dm5")                 # lit tread
            if r > y:                                                                    # step down to the right:
                rect(L, x, y + 1, x, min(r, FACADE_BOTTOM), "dm2")                       # right-facing riser, shade
            if l > y:
                rect(L, x, y + 1, x, min(l, FACADE_BOTTOM), "dm5")                       # left-facing riser, lit
            if front[y + 1, x] >= 0 and L[y + 1, x] < 0:
                px(L, x, y + 1, "dm3")
            for yy in range(y + 2, min(y + 12, FACADE_BOTTOM)):                          # blown windows
                if front[yy, x] in (I["hw0"], I["hw1"], I["hw2"]) and L[yy, x] < 0:
                    L[yy, x] = I["dw1"] if yy < y + 7 else I["dw0"]
    for (x, y, w, ln) in SCORCH_A:                                                         # blast scorch tongues
        for j in range(ln):
            for i in range(max(1, w - (j * w) // (ln + 1))):
                xx = x + i - (w // 2) + (1 if j % 3 == 1 else 0)
                yy = y + j
                if 0 <= xx < W and front[yy, xx] >= 0 and L[yy, xx] < 0 and hval("scA", xx, yy) < 0.85 - 0.4 * j / ln:
                    L[yy, xx] = I["dw1"] if j < ln * 0.4 else I["dm2"]
    tb = breach_tops()["B"]
    for (x0, w, ln, key) in ((95, 9, 14, 1), (82, 8, 10, 2), (106, 8, 12, 3), (115, 5, 9, 4)):
        top = min(tb.get(x, 109) for x in range(x0, x0 + w)) + 1
        ivy_curtain(L, front, x0, top, ln, w, ("ivyB", key))
    x0, top, ln, w = CENTRE_VINE_L
    ivy_curtain(L, front, x0, top, ln, w, ("vineC", x0))
    sx, sy = SURVEY_X                                                                      # orange spray X
    for k in range(5):
        px(L, sx + k, sy + k, "o1"); px(L, sx + 4 - k, sy + k, "o1")
    px(L, sx + 2, sy + 2, "o2")
    rx, ry = PATROL_RELAY                                                                  # patrol relay on the tooth
    rect(L, rx, ry - 3, rx + 2, ry - 1, "k1"); px(L, rx, ry - 3, "k3")
    rect(L, rx + 3, ry - 8, rx + 3, ry - 2, "k2")
    px(L, rx + 3, ry - 9, "r2"); px(L, rx + 2, ry - 9, "r1"); px(L, rx + 4, ry - 9, "r0")
    return L


def _cone_mask(edge):
    return poly_mask(edge + [(edge[-1][0], T_FOOT[1] + 1), (edge[0][0], T_FOOT[1] + 1)]) & (YY <= T_FOOT[1])


def _cone_tone(edge, m, ramp, key, gain=1.0):
    """Shade a spill cone as a soft mound: the top edge's slope gives the surface tilt near the crest (sun from the
    front-left: flanks rising to the right are lit), fading with depth below the crest, plus a gentle fall-off toward
    the toe and low-frequency swells; quantised into the 4-tone ramp (dark -> light). Bands follow the silhouette
    instead of running down whole columns (column-wise tones read as low-poly facets in the first preview)."""
    top = np.interp(np.arange(W), [p[0] for p in edge], [p[1] for p in edge])
    slope = np.convolve(np.gradient(top), np.ones(5) / 5.0, mode="same")
    nz = vnoise((key, "swell"), 5)
    out = np.full((H, W), -1, np.int16)
    hgt = max(1.0, T_FOOT[1] - float(top[edge[0][0]:edge[-1][0] + 1].min()))
    for y, x in zip(*np.nonzero(m)):
        depth = y - top[x]
        tilt = -slope[x] * math.exp(-depth / 7.0)
        v = 0.42 + gain * 0.55 * tilt + 0.22 * math.exp(-depth / 3.0) - 0.30 * depth / hgt + 0.22 * (nz[y, x] - 0.5)
        out[y, x] = I[ramp[0 if v < 0.18 else 1 if v < 0.42 else 2 if v < 0.66 else 3]]
    return out


def paint_breach_rubble():
    """Over the Olmsted terrace: cone A (fresh, grey, scorched; recognisable fallen pieces; survey + patrol cues) and
    cone B (old, grassed over; a few blocks still showing)."""
    L = new()
    m = _cone_mask(CONE_A)
    t = _cone_tone(CONE_A, m, ("dm1", "dm2", "dm3", "dm4"), "coneA")
    L[m] = t[m]
    for gy in range(144, 186, 5):                                               # sparse coarse stones
        for gx in range(462 + (gy % 2) * 4, 570, 9):
            if hval("stA", gx, gy) < 0.45:
                continue
            x = gx + int(hval("stAx", gx, gy) * 5); y = gy + int(hval("stAy", gx, gy) * 3)
            w = 3 + int(hval("stAw", gx, gy) * 3)
            if not (m[y, x] and m[min(H - 1, y + 2), min(W - 1, x + w)]):
                continue
            rect(L, x, y, x + w - 1, y, "dm4"); rect(L, x, y + 1, x + w - 1, y + 1, "dm3")
            px(L, x + w, y + 1, "dw0"); rect(L, x, y + 2, x + w - 1, y + 2, "dw1")
    for fr in CONE_A_FRAGMENTS:
        k = fr[0]
        if k == "cornice":
            _, xa, ya, xb, yb = fr
            for x in range(xa, xb + 1):
                y = int(round(ya + (yb - ya) * (x - xa) / (xb - xa)))
                px(L, x, y - 1, "dm6"); px(L, x, y, "dm5")
                px(L, x, y + 1, "dm2" if x % 2 else "dm4"); px(L, x, y + 2, "dw1"); px(L, x, y + 3, "dw1")
        elif k == "balustrade":
            _, xa, ya, xb, yb = fr
            for x in range(xa, xb + 1):
                y = int(round(ya + (yb - ya) * (x - xa) / (xb - xa)))
                px(L, x, y - 2, "dm6"); px(L, x, y - 1, "dm4" if x % 3 != 2 else "dw1")
                px(L, x, y, "dm4" if x % 3 != 2 else "dw1"); px(L, x, y + 1, "dm3"); px(L, x, y + 2, "dw1")
        elif k == "wallpiece":
            _, x, y, w, h = fr
            rect(L, x, y, x + w - 1, y + h - 1, "dm4"); rect(L, x, y, x + w - 1, y, "dm6")
            rect(L, x + w - 1, y + 1, x + w - 1, y + h - 1, "dm2"); rect(L, x, y + h, x + w, y + h, "dw1")
            rect(L, x + 4, y + 2, x + 6, y + 5, "hw0"); rect(L, x + 4, y + 2, x + 6, y + 2, "dw1")   # its window
            rect(L, x + 3, y + 6, x + 7, y + 6, "dm6")                                               # its sill
        elif k == "drum":
            _, x, y, w, h = fr
            rect(L, x, y, x + w - 1, y + h - 1, "dm4"); rect(L, x, y, x + 1, y + h - 1, "dm6")
            rect(L, x + w - 1, y, x + w - 1, y + h - 1, "dm2"); rect(L, x, y + h, x + w - 1, y + h, "dw1")
        else:
            _, x, y, w, h = fr
            rect(L, x, y, x + w - 1, y + h - 1, "dm4"); rect(L, x, y, x + w - 1, y, "dm6")
            rect(L, x + w - 1, y + 1, x + w - 1, y + h - 1, "dm2"); rect(L, x, y + h, x + w - 1, y + h, "dw1")
    for x in range(486, 520):                                                    # scorch on the cone's crest
        for j in range(3):
            y = int(np.interp(x, [p[0] for p in CONE_A], [p[1] for p in CONE_A])) + 1 + j
            if m[y, x] and hval("scc", x, j) < 0.55 - 0.15 * j and L[y, x] in (I["dm2"], I["dm3"], I["dm4"]):
                L[y, x] = I["dw1"] if j else I["dw0"]
    for (cx, cy, rx, ry) in CONE_A_GRASS:                                        # weeds in the lower slopes
        g = ell(cx, cy, rx, ry) & m
        top_g = g & ~np.roll(g, 1, 0)
        L[g] = I["lw2"]
        L[top_g] = I["lw3"]
    for (x, y, r) in CONE_A_SCRUB:
        crown(L, x, y - r * 0.4, r, VG, VG_CUTS, ("scrA", x), squash=0.75, leaf=2)
    dx, dy = DORMANT_WALKER                                                      # dead walker, half buried
    hull = poly_mask([(dx - 7, dy), (dx - 4, dy - 4), (dx + 5, dy - 5), (dx + 8, dy - 2), (dx + 6, dy)])
    L[hull] = I["k1"]
    rect(L, dx - 3, dy - 4, dx + 4, dy - 4, "k3"); px(L, dx - 5, dy - 2, "k3")             # lit edge, dead eye
    line(L, dx + 4, dy - 5, dx + 8, dy - 12, "k1"); line(L, dx + 8, dy - 12, dx + 11, dy - 9, "k1")
    rect(L, dx - 7, dy + 1, dx + 7, dy + 1, "dw1")
    px(L, dx + 1, dy - 2, "ru0")                                                 # rust bloom
    for (x, y) in SURVEY_PENNANTS:                                               # survey stakes, prism, tape
        rect(L, x, y - 7, x, y, "k1")
        rect(L, x + 1, y - 7, x + 3, y - 6, "o2"); rect(L, x + 1, y - 5, x + 2, y - 5, "o1")
    x, y = SURVEY_PRISM
    rect(L, x, y - 8, x, y, "k2"); px(L, x, y - 9, "t2"); px(L, x - 1, y - 9, "t1"); px(L, x, y - 10, "t1")
    for (a, b) in zip(SURVEY_TAPE, SURVEY_TAPE[1:]):
        (xa, ya), (xb, yb) = a, b
        for x in range(xa, xb + 1):
            tt = (x - xa) / (xb - xa)
            yy = int(round(ya - 3 + (yb - ya) * tt + 2.2 * math.sin(math.pi * tt)))
            px(L, x, yy, "o2" if (x // 3) % 2 else "o1")
    for (x, y) in SURVEY_TAPE:
        rect(L, x, y - 4, x, y, "k1"); px(L, x, y - 4, "k3")
    # --- cone B: an old spill grassed over in two calm masses, a few dressed blocks still showing, scrub
    m = _cone_mask(CONE_B)
    t = _cone_tone(CONE_B, m, ("vg0", "lw1", "lw2", "lw3"), "coneB")
    L[m] = t[m]
    topb = np.interp(np.arange(W), [p[0] for p in CONE_B], [p[1] for p in CONE_B])
    for x in range(CONE_B[0][0] + 2, CONE_B[-1][0] - 1):                      # grass blades on the skyline
        if hval("bladeB", x) < 0.45:
            y0 = int(math.ceil(topb[x]))
            for j in range(1, 2 + int(hval("bladeBh", x) * 2)):
                px(L, x, y0 - j, "lw3" if np.gradient(topb)[x] < 0 else "lw2")
    for (x, y, w, h) in CONE_B_BLOCKS:
        rect(L, x, y, x + w - 1, y + h - 1, "dm3"); rect(L, x, y, x + w - 1, y, "dm4")
        rect(L, x, y + h, x + w - 1, y + h, "vg0")
    for (x, y, r) in CONE_B_SCRUB:
        crown(L, x, y - r * 0.4, r, VG, VG_CUTS, ("scrB", x), squash=0.75, leaf=2)
    return L


# ============================================================================ 6 Olmsted lower west terrace
SENTINEL = ["..kk...",
            ".kKKk..",
            "kKRKKk.",
            ".kKKKkk",
            "..k.k..",
            ".k...k.",
            "k....k.",
            "k.....k",
            "kk...kk"]


def paint_terrace():
    L = new()
    rect(L, 0, T_RAIL, W - 1, T_RAIL, "dm5")
    for x in range(W):
        px(L, x, T_BAL[0], "dm2")
        for y in (T_BAL[0] + 1, T_BAL[1]):
            px(L, x, y, "dm4" if x % 3 != 2 else "dm2")
    rect(L, 0, T_BASE, W - 1, T_BASE, "dm4")
    for (a, b) in T_BAL_GAPS:
        rect(L, a, T_RAIL, b, T_BAL[1], -1)
        px(L, a, T_RAIL, "dm3"); px(L, b, T_BAL[1], "dm3"); px(L, a, T_BAL[1], "dm2")
    for x in T_PIERS:
        rect(L, x, T_RAIL - 3, x + 4, T_BASE, "dm4"); rect(L, x, T_RAIL - 3, x + 4, T_RAIL - 3, "dm6")
        rect(L, x + 4, T_RAIL - 2, x + 4, T_BASE, "dm2"); px(L, x, T_RAIL - 2, "dm5")
        st = T_URNS.get(x, "urn")
        if st == "urn":                                                    # bronze-patinated urn on a plinth
            rect(L, x + 1, T_RAIL - 6, x + 3, T_RAIL - 4, "dm3"); px(L, x + 1, T_RAIL - 6, "dm4")
            px(L, x + 2, T_RAIL - 7, "dm3")
        elif st == "tilted":                                               # urn knocked askew
            px(L, x + 1, T_RAIL - 4, "dm3"); px(L, x + 2, T_RAIL - 5, "dm4"); px(L, x + 3, T_RAIL - 5, "dm3")
            px(L, x + 3, T_RAIL - 6, "dm3"); px(L, x + 4, T_RAIL - 6, "dm2")
        elif st == "stump":                                                # broken foot of the urn only
            rect(L, x + 1, T_RAIL - 4, x + 3, T_RAIL - 4, "dm3"); px(L, x + 2, T_RAIL - 5, "dm2")
        # "gone": bare pier cap with a dark socket
        if st == "gone":
            px(L, x + 2, T_RAIL - 3, "dm2")
    # wall face: granite ashlar courses of 3 rows, irregular block lengths, mid-tone joints, weathered streaks
    for y in range(T_WALL[0], T_WALL[1] + 1):
        rel = y - T_WALL[0]
        c = rel // 3
        row = np.full(W, I["dm4"], np.int16)
        if rel % 3 == 2:
            row[:] = I["dm3"]
        else:
            acc = int(hval("tc", c) * 11)
            k = 0
            while acc < W:
                if 0 <= acc < W:
                    row[acc] = I["dm3"]
                acc += 7 + int(hval("tl", c, k) * 9)
                k += 1
        L[y] = row
    # v07 (v05t lesson): hand-placed replaced / weathered blocks instead of v06's hashed 14 % tone scatter
    for (x0, c, ln, tone) in TERRACE_BLOCKS:
        for y in range(T_WALL[0] + c * 3, min(T_WALL[1], T_WALL[0] + c * 3 + 1) + 1):
            for x in range(x0, min(W, x0 + ln)):
                if L[y, x] == I["dm4"]:
                    L[y, x] = I[{"new": "dm5", "dark": "dm3", "ws": "ws0"}[tone]]
    rect(L, 0, T_WALL[0], W - 1, T_WALL[0], "dm2")                       # shadow under the base rail
    for x in T_PIERS:                                                      # streaks under the urns
        for k in range(3 + int(hval("tstr", x) * 8)):
            px(L, x + 2, T_WALL[0] + 1 + k, "ws0")
    for x in T_WINDOWS:
        arch(L, x, 168, 176, 4, "hw0")
        rect(L, x - 1, 177, x + 4, 177, "dm5")
    # v07: rising damp at the wall foot, irregular top, a moss line on the last course
    for k, (x0, x1, hmax) in enumerate(TERRACE_DAMP):
        for x in range(x0, x1 + 1):
            hh = int(round(hmax * (0.4 + 0.6 * vn1(("tdamp", k), x / 6.0))))
            for j in range(hh):
                y = T_WALL[1] - j
                c = L[y, x]
                if c == I["dm4"] or c == I["ws0"] or c == I["dm5"]:
                    L[y, x] = I["vg1"] if j == 0 and (x + k) % 3 != 0 else I["dm3"]
                elif c == I["dm3"] and j < hh - 1:
                    L[y, x] = I["dm2"]
    for y in range(T_FOOT[0], T_FOOT[1] + 1):
        rect(L, 0, y, W - 1, y, "dm3" if y == T_FOOT[0] else "dm2")
    # recess between the stairs (set back, in shade), grotto arch, dry fountain planted with shrubs
    a, b = RECESS
    for y in range(T_WALL[0], T_WALL[1] + 1):
        for x in range(a, b + 1):
            c = L[y, x]
            L[y, x] = I["dm3"] if c == I["dm4"] else I["dm2"]
    gx0, gx1, gy0, gy1 = GROTTO
    rect(L, gx0, gy0 + 3, gx1, gy1, "hw0"); rect(L, gx0 + 3, gy0, gx1 - 3, gy0 + 2, "hw0")
    rect(L, gx0 + 1, gy0 + 1, gx1 - 1, gy0 + 2, "hw0")
    rect(L, gx0 - 1, gy0 + 2, gx0 - 1, gy1, "dm5"); rect(L, gx0 + 2, gy0 - 1, gx1 - 2, gy0 - 1, "dm5")
    for x in range(gx0 + 2, gx1 - 1, 4):
        rect(L, x, gy0 + 5, x, gy1 - 1, "dw1")
    fx0, fx1, fy0, fy1 = FOUNTAIN_T
    rect(L, fx0, fy0, fx1, fy1, "dm4"); rect(L, fx0, fy0, fx1, fy0, "dm6"); rect(L, fx0, fy1, fx1, fy1, "dm2")
    rect(L, fx0 + 2, fy0 + 1, fx1 - 2, fy0 + 2, "dw1")
    for x in (fx0 + 4, fx0 + 11, fx0 + 19, fx0 + 26, fx0 + 33, fx0 + 41):
        crown(L, x, fy0 - 2, 4 if x % 2 else 3, VG, VG_CUTS, ("basin", x), squash=0.7, leaf=2)
    # twin grand stairs with cheek walls and bronze lanterns
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
        rect(L, x0, T_RAIL - 7, x1, T_RAIL - 4, "br0")
        px(L, x0 + 1, T_RAIL - 8, "br1"); px(L, x0 + 1, T_RAIL - 6, "hw1")
    # stains, the rubble cone from the House wing collapse spilling over the right of the terrace
    for x in (60, 126, 236, 512, 586):
        for y in range(T_WALL[0] + 1, T_WALL[0] + 7 + int(hval("stain", x) * 7)):
            px(L, x, y, "dm3" if y % 2 else "dm2")
    for i, (cx, cy, rx, ry) in enumerate(COLLAPSE_CONE):
        m = ell(cx, cy, rx, ry) & (YY <= T_FOOT[1])
        n = vnoise(("cone", cx), 2)
        t = np.where(n > 0.64, I["dm5"], np.where(n > 0.40, I["dm4"], np.where(n > 0.22, I["dm2"], I["hw0"])))
        L[m] = t[m]
    for (x, y, w, h) in ((566, 168, 6, 3), (590, 172, 8, 4), (612, 175, 5, 3), (548, 165, 5, 2)):   # big blocks
        rect(L, x, y, x + w, y + h, "dm4"); rect(L, x, y, x + w, y, "dm6"); rect(L, x + w, y + 1, x + w, y + h, "dm2")
    for (x, top, length, w) in T_IVY:
        ivy_curtain(L, L.copy(), x, top, length, w, ("tivy", x))
    for (x, y, r) in DECK_SHRUBS:
        crown(L, x, y - r * 0.5, r, VG, VG_CUTS, ("deck", x), squash=0.75, leaf=2)
    sx, sb = T_SENTINEL                                                    # parked sentinel: a 9-px scale figure
    stamp(L, sx - 3, sb - len(SENTINEL) + 1, SENTINEL, {"k": "k1", "K": "k2", "R": "r2"})
    return L


# ============================================================================ 7 West Lawn (foreshortened ground)
def lawn_world():
    """World coordinates (X m, d m) for every texel of the lawn rows (186..H); near rows clamp to d = 20 m."""
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
    # grass tufts in world space: spacing ~0.55 m and blade height ~0.22 m, both shrinking with distance
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
    # worn central trail and two walks converging on the twin stairs (perspective strips), half-buried
    trail = world_strip(X, D, TRAIL[0], TRAIL[1], TRAIL[2] / 2) & lawn
    ov = wnoise("trail-ov", X / 0.8, D / 1.6)
    ov2 = wnoise("trail-ov2", X / 0.35, D / 0.7)
    L[trail & (ov > 0.30)] = I["s3"]
    L[trail & (ov > 0.30) & (ov2 > 0.62)] = I["lw4"]
    L[trail & (ov > 0.64)] = I["s4"]
    L[trail & (ov > 0.30) & (ov2 < 0.2)] = I["lw2"]
    for p, q, hw in (WALK_L, WALK_R):
        st = world_strip(X, D, p, q, hw / 2) & lawn
        bur = wnoise(("walk-ov", p), X / 1.0, D / 2.5)
        L[st & (bur > 0.40)] = I["p3"]
        L[st & (bur > 0.40) & (bur < 0.48)] = I["p2"]
        edge = st & ~np.roll(st, 1, 0)
        L[edge & (bur > 0.40)] = I["p4"]
    for i, (xm, d, hx, hd) in enumerate(LAWN_PATCHES):                  # darker tall-grass swaths
        e = ((X - xm) / hx) ** 2 + ((D - d) / hd) ** 2 <= 1 + 0.6 * (wnoise(("lp", i), X / 0.8, D / 0.8) - 0.5)
        e &= lawn
        L[e] = np.array([shift(LW, int(c), -1) if int(c) in LW else c for c in L[e]], np.int16)
    for (xa, da), (xb, db) in zip(PATROL_TRAIL, PATROL_TRAIL[1:]):        # trampled patrol trail to the breach
        st = world_strip(X, D, (xa, da), (xb, db), 1.0) & lawn
        tr = wnoise("ptrail", X / 0.5, D / 0.9)
        m = st & (tr > 0.30)
        L[m] = np.array([shift(LW, int(c), -2) if int(c) in LW else c for c in L[m]], np.int16)
    hz = np.clip((D - 55.0) / 95.0, 0, 1)                                  # haze toward the terrace foot
    hm = lawn & (BAY < hz * 0.85)
    L[hm] = HAZE_LUT[L[hm]]
    for i, (xm, d, r, kind) in enumerate(LAWN_SHRUBS):
        sx, sy = proj(xm, d)
        rp_ = max(2.0, r * F / d)
        ramp, cuts = (MG, MID_CUTS) if kind == "mg" else (VG, VG_CUTS)
        crown(L, sx, sy - rp_ * 0.55, rp_, ramp, cuts, ("lshrub", i), squash=0.7, leaf=2 if rp_ < 10 else 3)
    return L


# ============================================================================ 7b patrol walker (in the breach)
def paint_patrol_walker():
    """Quadruped patrol walker (game fiction, ~2.5 m) standing on the lawn in the seat-wall breach at d ~ 32 m,
    facing the plaza: hull, sensor head with a red eye, four digitigrade legs with three-toed feet, antenna, a
    dotted red scan line to the lawn and a contact shadow. Hand-placed vertices, front-left light."""
    L = new()
    x0, b = WALKER_POS
    P = lambda pts: [(x0 + x, b + y) for x, y in pts]
    # contact shadow on the lawn (opaque, darker grass)
    sh = ell(x0 + 3, b + 0.5, 22, 2.2)
    L[sh] = I["lw0"]
    L[sh & ell(x0 + 3, b + 0.5, 12, 1.4)] = I["f1"]
    # far legs (darker), then hull, head, then near legs
    def leg(hip, knee, foot, c_up, c_lo, w):
        for (a, q) in ((hip, knee), (knee, foot)):
            n = int(max(abs(q[0] - a[0]), abs(q[1] - a[1]))) + 1
            for k in range(n):
                t = k / max(1, n - 1)
                xx = round(x0 + a[0] + (q[0] - a[0]) * t); yy = round(b + a[1] + (q[1] - a[1]) * t)
                for j in range(w):
                    px(L, xx + j, yy, c_lo if j == w - 1 else c_up)
        kx, ky = x0 + knee[0], b + knee[1]
        rect(L, kx - 1, ky - 1, kx + 1, ky + 1, "k1"); px(L, kx - 1, ky - 1, "k3")
        fx, fy = x0 + foot[0], b + foot[1]
        for tx in (-3, 0, 3):                                              # three toes
            px(L, fx + tx, fy, "k0"); px(L, fx + tx + (1 if tx > 0 else 0), fy - 1, "k1")
        px(L, fx - 4, fy, "k0")
    leg((-8, -24), (-14, -15), (-11, 0), "k1", "k0", 2)
    leg((10, -24), (16, -14), (13, 0), "k1", "k0", 2)
    hull = poly_mask(P([(-17, -31), (-9, -36), (10, -36), (18, -32), (21, -27), (15, -22), (-12, -21),
                        (-19, -25)]))
    ys, xs = np.nonzero(hull)
    top = ys.min()
    for y, x in zip(ys, xs):
        r_ = y - top
        c = "k3" if r_ <= 2 else ("k2" if r_ <= 8 else "k1")
        if r_ <= 1 and x < x0 - 2:
            c = "k4"
        L[y, x] = I[c]
    edge = hull & ~(np.roll(hull, 1, 0) & np.roll(hull, -1, 0) & np.roll(hull, 1, 1) & np.roll(hull, -1, 1))
    L[edge] = I["k0"]
    for sx in (x0 - 4, x0 + 6):                                            # panel seams
        for y in range(b - 33, b - 22):
            if hull[y, sx] and not edge[y, sx]:
                px(L, sx, y, "k1")
    rect(L, x0 - 9, b - 26, x0 + 12, b - 26, "o1")                         # hazard stripe along the flank
    for xx in range(x0 - 9, x0 + 13, 4):
        px(L, xx, b - 26, "k1")
    head = poly_mask(P([(-27, -31), (-19, -34), (-14, -32), (-14, -25), (-20, -22), (-27, -26)]))
    hy, hx = np.nonzero(head)
    for y, x in zip(hy, hx):
        L[y, x] = I["k2" if y < b - 29 else "k1"]
    he = head & ~(np.roll(head, 1, 0) & np.roll(head, -1, 0) & np.roll(head, 1, 1) & np.roll(head, -1, 1))
    L[he] = I["k0"]
    rect(L, x0 - 25, b - 29, x0 - 21, b - 28, "r0")                        # sensor slit
    px(L, x0 - 24, b - 29, "r2"); px(L, x0 - 23, b - 29, "r2"); px(L, x0 - 22, b - 28, "r1")
    px(L, x0 - 19, b - 33, "k3")
    dome = ell(x0 + 4, b - 36.5, 5, 2.4) & (YY <= b - 36)
    L[dome] = I["k2"]; px(L, x0 + 2, b - 38, "k4")
    line(L, x0 + 9, b - 36, x0 + 12, b - 45, "k1"); px(L, x0 + 12, b - 46, "r2")       # antenna
    leg((-11, -23), (-22, -17), (-26, -6), "k2", "k1", 3)              # v07: near front leg raised mid-stride
    for (cx_, cy_, c_) in ((-27, -2, "s2"), (-24, -1, "s1"), (-29, 0, "s1"), (-25, 1, "lw0")):
        px(L, x0 + cx_, b + cy_, c_)                                    # clods falling from the lifted foot
    leg((13, -23), (22, -12), (20, 0), "k2", "k1", 3)
    for k in range(0, 15, 2):                                              # dotted scan line to the lawn
        px(L, x0 - 28 - k, b - 27 + int(k * 1.6), "r1")
    return L


# ============================================================================ 8 grounds trees (species, flanking)
def _hazed(L, m, share):
    """Aerial perspective: one haze step on an ordered-dither share of the texels in m."""
    hm = m & (L >= 0) & (BAY < share)
    L[hm] = HAZE_LUT[L[hm]]


def tree_trunk(L, x, y0, y1, w, cols=("b1", "b0"), flare=1):
    for y in range(int(y0), int(y1) + 1):
        f = flare if y > y1 - 3 else 0
        rect(L, x - w // 2 - f, y, x - w // 2 + w - 1 + f, y, cols[0])
        px(L, x - w // 2 + w - 1 + f, y, cols[1])


def conifer(L, x, base, hgt, half_w, ramp, key, tiers=6, droop=False):
    """Hand-shaped conifer: a jagged cone of stacked tiers (each tier lit on its upper-left, shaded below), tips
    drooping for a spruce; dark notches between tiers; a short trunk at the foot."""
    top = base - hgt
    for y in range(int(top), int(base) - 2):
        t = max(0.0, (y - top) / max(1.0, hgt - 3))
        tier = int(t * tiers)
        tt = t * tiers - tier
        hw = half_w * (0.12 + 0.88 * t ** 0.85) * (0.78 + 0.30 * tt)
        jag = (hval(key, "jag", y) - 0.5) * 2.2
        a, bnd = int(round(x - hw + jag * 0.5)), int(round(x + hw + jag * 0.5))
        for xx in range(a, bnd + 1):
            u = (xx - x) / max(1.0, hw)
            v = -0.55 * u + (0.45 - tt) * 0.9 + (hval(key, "lf", xx // 2, y) - 0.5) * 0.5
            c = ramp[0] if v < -0.55 else ramp[1] if v < -0.15 else ramp[2] if v < 0.25 else ramp[3] if v < 0.55 \
                else ramp[4]
            if tt > 0.86 and abs(u) < 0.7:
                c = ramp[0]                                               # notch under each tier
            px(L, xx, y, c)
        if droop and tt > 0.7:
            for side in (-1, 1):
                px(L, round(x + side * (hw + 1)), y + 1, ramp[1])
    px(L, x, int(top) - 1, ramp[2])
    tree_trunk(L, x, base - 3, base, 2, ("b1", "b0"), flare=0)


def broadleaf(L, x, base, lobes, trunk_top, trunk_w, ramp, cuts, key, limbs=(), holes=()):
    for (a, q) in limbs:
        line(L, x + a[0], base + a[1], x + q[0], base + q[1], "b1")
        line(L, x + a[0] + 1, base + a[1], x + q[0] + 1, base + q[1], "b0")
    tree_trunk(L, x, base - trunk_top, base, trunk_w)
    lb = [(x + lx, base + ly, r) for lx, ly, r in lobes]
    crown_lobes(L, cluster_lobes(lb, key) if max(r for _, _, r in lobes) >= 10 else lb, ramp, cuts, key,
                squash=0.86, leaf=2, holes=[(x + hx, base + hy, rx, ry) for hx, hy, rx, ry in holes])


def olmsted_lamp(L, side, d, state):
    """Olmsted bronze lamp standard (~3.4 m) beside a West Lawn walk, projected by the backdrop camera so the two rows
    shrink and converge on the terrace stairs (the depth ruler of the lawn). Plinth, post lit on its left, lantern
    head with a cap and finial; `leaning`, `headless` and `ok` are hand-assigned 2537 states."""
    (xa, da), (xb, db), hw = WALK_L if side < 0 else WALK_R
    t = (d - da) / (db - da)
    X = xa + (xb - xa) * t + side * (hw / 2 + 1.4)
    sx, gy = proj(X, d)
    s = F / d
    x, base = int(round(sx)), int(round(gy))
    hgt = int(round(3.4 * s))
    pw = 2 if s >= 6 else 1
    ph = max(1, int(round(0.35 * s)))
    lean = (0.22 if state == "leaning" else 0.0) * side
    top = base - hgt
    for j in range(hgt):
        y = base - j
        xx = x + int(round(lean * j))
        if j < ph:
            rect(L, xx - 1, y, xx + pw, y, "bz1"); px(L, xx - 1, y, "bz2")
            continue
        if state == "headless" and j > hgt - max(2, int(0.5 * s)):
            if j == hgt - max(2, int(0.5 * s)) + 1:
                px(L, xx, y, "bz2")                                        # snapped, ragged end
            continue
        px(L, xx, y, "bz2" if pw == 2 else "bz1")
        if pw == 2:
            px(L, xx + 1, y, "bz0")
    if state == "headless":
        return
    hx = x + int(round(lean * hgt))
    hw_ = max(1, int(round(0.22 * s)))
    hh = max(3, int(round(0.6 * s)))
    for j in range(hh):
        y = top - j
        rect(L, hx - hw_, y, hx + hw_ + pw - 1, y, "k1" if 0 < j < hh - 1 else "bz1")
        if 0 < j < hh - 1:
            px(L, hx - hw_, y, "bz1"); px(L, hx + hw_ + pw - 1, y, "bz0")
            if j == 1 and hw_ >= 2:
                px(L, hx - hw_ + 1, y, "hw1")                              # sky glint in the glass
    rect(L, hx - hw_ + 1, top - hh, hx + hw_ + pw - 2, top - hh, "bz2")    # cap
    px(L, hx + (pw - 1) // 2, top - hh - 1, "bz3")                        # finial


# v06 pass 2: Olmsted lamp standards along the two walks (side, d m, state) -- hand-assigned, asymmetric
OLMSTED_LAMPS = [(-1, 62, "ok"), (-1, 78, "ok"), (-1, 100, "headless"), (-1, 128, "ok"),
                 (1, 62, "ok"), (1, 78, "leaning"), (1, 100, "ok")]


def paint_grounds_trees():
    L = new()
    for i, lobes in enumerate(FAR_MASSES):
        crown_lobes(L, lobes, VG, VG_CUTS, ("farmass", i), squash=0.85, leaf=2)
    ops = [(d, "tree", e) for e in GROUNDS_TREES for d in (e[1],)] + \
          [(e[1], "lamp", e) for e in OLMSTED_LAMPS]
    for d, what, e in sorted(ops, key=lambda o: -o[0]):                 # painter's order: far first
        if what == "lamp":
            m0 = L >= 0
            olmsted_lamp(L, *e)
            _hazed(L, (L >= 0) & ~m0, float(np.clip((d - 60.0) / 160.0, 0.0, 0.30)))
            continue
        x, d, hm, kind = e
        s = F / d
        base = int(round(row_of(d)))
        hgt = hm * s
        m0 = L >= 0
        if kind == "oak":            # white oak: broad, irregular, low limbs, two sky gaps
            broadleaf(L, x, base, [(-22, -50, 12), (-6, -60, 13), (12, -56, 12), (26, -44, 10), (-28, -36, 9),
                                   (-4, -42, 14), (16, -36, 11), (-14, -30, 10), (30, -30, 6), (4, -26, 9)],
                      30, 3, MG, MID_CUTS, ("oak", x), limbs=[((0, -26), (-18, -40)), ((1, -24), (20, -38))])
        elif kind == "cedar":        # eastern red cedar: dense narrow column
            conifer(L, x, base, hgt, 7.5, CONIFER, ("cedar", x), tiers=9)
        elif kind == "magnolia":     # southern magnolia: dark glossy pyramid-oval with leaf glints
            broadleaf(L, x, base, [(0, -46, 8), (-8, -38, 10), (9, -38, 10), (-14, -26, 11), (12, -26, 11),
                                   (0, -30, 12), (-6, -16, 10), (8, -16, 10), (0, -12, 8)],
                      10, 3, NEAR[:5], NEAR_CUTS[:4], ("magnolia", x))
            for k in range(22):
                gx = int(x - 14 + hval("mglint", k) * 24); gy = int(base - 46 + hval("mglinty", k) * 34)
                if L[gy, gx] in (I["f3"], I["f4"]) and gx < x + 4:
                    px(L, gx, gy, "f5"); px(L, gx + 1, gy, "f4")
        elif kind == "broken-oak":   # storm-broken oak: half a crown, a snapped bare limb, splinters
            broadleaf(L, x, base, [(-20, -42, 11), (-8, -52, 12), (-24, -28, 9), (-8, -34, 12), (4, -42, 9),
                                   (-14, -20, 7)], 28, 3, MG, MID_CUTS, ("boak", x),
                      limbs=[((0, -24), (-16, -38))])
            for k in range(30):                                            # the snapped limb, bare
                xx = x + 2 + k; yy = base - 26 - int(k * 0.9)
                px(L, xx, yy, "b2"); px(L, xx, yy + 1, "b1"); px(L, xx + 1, yy + 1, "b0")
            for (sx_, sy_) in ((x + 31, base - 54), (x + 32, base - 56), (x + 30, base - 55), (x + 33, base - 53)):
                px(L, sx_, sy_, "b3")
            for (a, q) in (((x + 14, base - 38), (x + 22, base - 50)), ((x + 22, base - 46), (x + 30, base - 47))):
                line(L, a[0], a[1], q[0], q[1], "b1")
            rect(L, x - 2, base - 30, x - 2, base - 22, "b3")                # sunlit bark
        elif kind == "spruce":       # Norway spruce: tall cone, drooping tiers
            conifer(L, x, base, hgt, 17.0, CONIFER, ("spruce", x), tiers=8, droop=True)
        elif kind == "poplar":       # young tulip poplar: narrow oval, yellow-green
            broadleaf(L, x, base, [(0, -38, 6), (-5, -30, 7), (5, -30, 7), (-4, -20, 7), (4, -21, 6),
                                   (0, -26, 7)], 14, 2, POPLAR, MID_CUTS, ("poplar", x))
        new_m = (L >= 0) & ~m0
        _hazed(L, new_m, float(np.clip((d - 80.0) / 160.0, 0.0, 0.35)))
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


def grass_clump(L, x, base, hw, h, dry, key):
    """Ornamental-grass / broomsedge clump: individual arched blades from a tight crown, each blade darker at the
    base and lit at the tip; a `dry` share of blades is straw-coloured with a pale plume."""
    n = int(hw * 2.2)
    for k in range(n):
        ox = (hval(key, "o", k) - 0.5) * hw * 0.8
        lean = (hval(key, "l", k) - 0.5) * 2.0 + ox / max(1, hw) * 1.4
        hh = h * (0.55 + 0.45 * hval(key, "h", k))
        is_dry = hval(key, "d", k) < dry
        for j in range(int(hh)):
            t = j / max(1.0, hh)
            xx = round(x + ox + lean * hw * t * t)
            c = ("g1" if t < 0.3 else "g3" if t < 0.75 else "g5") if not is_dry else \
                ("d0" if t < 0.4 else "d1" if t < 0.85 else "d2")
            px(L, xx, base - j, c)
        if is_dry and hval(key, "p", k) < 0.5:
            px(L, round(x + ox + lean * hw), base - int(hh), "lw5")
    for j in range(-hw // 2, hw // 2 + 1):
        px(L, x + j, base, "g0")


def paint_lawn_edge():
    L = new()
    for i, (x, up, r) in enumerate(NEAR_ROUND):
        base = YTOP[x] + 2
        crown(L, x, base - up * 0.5 - r * 0.25, r, NEAR[:6], NEAR_CUTS[:5], ("yew", i), squash=0.72, gain=0.85)
    # boxwood hedge gone wild: one continuous body rooted on the lawn behind the coping (v06 pass 2: the v06 draft's
    # lobes floated free of the ground), with the overgrown lobes riding on its irregular top
    xs_ = [x for x, _, _ in HEDGE_LOBES]
    x0h, x1h = min(xs_) - 8, max(xs_) + 6
    tops = {}
    for x in range(x0h, x1h + 1):
        up = float(np.interp(x, sorted(xs_), [u for _, u, _ in sorted(HEDGE_LOBES)])) * 0.85
        u = (x - x0h) / max(1, x1h - x0h)
        up *= min(1.0, 4.0 * u, 4.0 * (1 - u)) ** 0.5
        tops[x] = int(round(YTOP[x] + 2 - up - 2 * vn1("hedge-top", x / 4.0)))
        for y in range(tops[x], YTOP[x] + 3):
            t = (y - tops[x]) / max(1, YTOP[x] + 2 - tops[x])
            c = "f3" if t < 0.18 else "f2" if t < 0.55 else "f1" if t < 0.85 else "f0"
            if t < 0.55 and hval("hedge-leaf", x // 2, y // 2) < 0.22:
                c = "f4" if t < 0.18 else "f3"
            px(L, x, y, c)
    lobes = [(x, YTOP[x] + 2 - up, r) for x, up, r in HEDGE_LOBES]
    crown_lobes(L, cluster_lobes(lobes, "hedge"), NEAR[:6], NEAR_CUTS[:5], "hedge", squash=0.62, gain=0.95, leaf=2)
    for x in (58, 92, 126):                                                # dead twigs poking out of the hedge
        line(L, x, YTOP[x] - 16, x - 3, YTOP[x] - 26, "b2"); px(L, x - 4, YTOP[x] - 27, "b3")
    x, hgt = CEDAR_SEEDLING
    conifer(L, x, YTOP[x] + 2, hgt, 7.0, CONIFER, "cedar-seedling", tiers=6)
    for i, (x, hw, h, dry) in enumerate(GRASS_CLUMPS):
        grass_clump(L, x, YTOP[x] + 2, hw, h, dry, ("grass", i))
    x, hw, h = SUMAC                                                       # staghorn sumac: forked stems, leaflets
    base = YTOP[x] + 2
    for (dx, top) in ((-6, h - 4), (0, h), (7, h - 7)):
        line(L, x, base, x + dx, base - top + 6, "b2")
    lobes = [(x - 8, base - h + 9, 6), (x + 1, base - h + 6, 7), (x + 9, base - h + 12, 6), (x - 3, base - 12, 6),
             (x + 6, base - 10, 5)]
    crown_lobes(L, lobes, NEAR[:6], NEAR_CUTS[:5], "sumac", squash=0.7, gain=1.0, leaf=2)
    for k in range(16):                                                    # first leaflets turning red, fruit cone
        lx = int(x - 12 + hval("sum", k) * 24); ly = int(base - h + 4 + hval("sumy", k) * (h - 8))
        if L[ly, lx] >= 0 and hval("sumr", k) < 0.6:
            px(L, lx, ly, "fl3"); px(L, lx + 1, ly, "ru3")
    rect(L, x, base - h + 1, x + 1, base - h + 3, "r0"); px(L, x, base - h + 1, "fl3")
    x, up, r = VIBURNUM
    base = YTOP[x] + 2
    crown(L, x, base - up * 0.5 - r * 0.25, r, NEAR[:6], NEAR_CUTS[:5], "viburnum", squash=0.7, gain=0.95)
    for k in range(14):
        fx = int(x - r + hval("vib", k) * r * 1.6); fy = int(base - up - r * 0.6 + hval("viby", k) * r * 1.1)
        if 0 <= fx < W - 1 and L[fy, fx] >= 0:
            rect(L, fx, fy, fx + 1, fy, "fl2"); px(L, fx, fy + 1, "p4")
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


SEAT_IVY = [(24, 6, 13, "down"), (60, 3, 9, "down"), (90, 7, 13, "down"), (142, 3, 8, "down"), (232, 4, 11, "down"),
            (264, 2, 7, "down"), (602, 4, 12, "down"), (626, 7, 14, "down"), (182, 4, 11, "up"), (470, 4, 10, "up")]


def ivy_leaf(L, ivy, face, x, y, rc, lit):
    """One ivy leaf cluster: a small squashed disc lit from the upper left (g4 only on the lit rim of upper
    clusters), body g2/g3, the shaded lower-right edge f1 (v05t)."""
    xi, yi = int(round(x)), int(round(y))
    R_ = int(math.ceil(rc)) + 1
    for j in range(-R_, R_ + 1):
        for i in range(-R_, R_ + 1):
            d = (i / (rc * 1.15)) ** 2 + (j / (rc * 0.85)) ** 2
            if d >= 1:
                continue
            x_, y_ = xi + i, yi + j
            if not (0 <= x_ < W and 0 <= y_ < H) or not (face[y_, x_] or face[min(H - 1, y_ + 2), x_]):
                continue
            v = -(i * 0.7 + j * 0.7) / (rc + 0.5)
            c = "g1" if v < -0.45 else "g2" if v < 0.15 else "g3"
            if v > 0.5 and lit > 0.5 and d > 0.25:
                c = "g4"
            if d > 0.72 and v < -0.2:
                c = "f1"
            L[y_, x_] = I[c]
            ivy[y_, x_] = True


def ivy_stem(L, ivy, face, x, y0, y1, dirn, rc0, key, lit=0.5):
    """A stem from y0 toward y1 (dirn +1 down / -1 up), wandering sideways, with leaf clusters set alternately left
    and right every 2-4 px; clusters shrink toward the growing tip (v05t)."""
    r = _rng("ivystem-v07", key)
    n = abs(int(y1) - int(y0))
    if n < 3:
        return
    dx, y, t_next = 0.0, float(y0), 0
    side = 1 if r.random() < 0.5 else -1
    for t in range(n):
        dx = max(-0.6, min(0.6, dx + float(r.normal(0, 0.18))))
        x += dx * 0.5
        y += dirn
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < W and 0 <= yi < H and face[yi, xi] and not ivy[yi, xi]:
            L[yi, xi] = I["s1"] if t % 5 else I["g1"]
            ivy[yi, xi] = True
        if t >= t_next:
            f = 1 - 0.6 * t / n
            ivy_leaf(L, ivy, face, x + side * float(r.uniform(1.0, 2.4)), y + float(r.uniform(-1, 1)),
                     max(1.2, rc0 * f * float(r.uniform(0.8, 1.2))), lit * (1.2 - t / n))
            side = -side
            t_next = t + int(r.integers(2, 5))


def ivy_mass(L, ivy, face, cx, anchor, hw, ln, limit, dirn, key):
    """Several stems from a shared foot (or coping), long in the middle and short at the flanks, so the outline is
    lobed and stone shows between the outer stems (v05t)."""
    r = _rng("ivymass-v07", key)
    ns = max(3, hw // 2 + 1)
    for s_ in range(ns):
        u = (s_ + 0.5) / ns * 2 - 1 + float(r.uniform(-0.12, 0.12))
        x = cx + u * hw
        ll = ln * (1 - u * u) ** 0.6 * float(r.uniform(0.55, 1.05))
        y1 = anchor + dirn * ll
        y1 = min(limit, y1) if dirn > 0 else max(limit, y1)
        ivy_stem(L, ivy, face, x, anchor - dirn * float(r.uniform(0, 2)), y1, dirn, 1.7 + 0.6 * (1 - abs(u)),
                 (key, s_), lit=0.7 - 0.3 * u)


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
    # v07 (v05t): ivy masses of wandering stems and lit leaf clusters with stone showing between the outer stems,
    # each throwing a 1-px shadow on the ashlar (v06 drew vertical f2/f3 stripes); moss on the coping as v06
    face = L >= 0
    ivy = np.zeros((H, W), bool)
    for k, (cx, hw, ln, grow) in enumerate(SEAT_IVY):
        top = YTOP[cx]
        if grow == "down":
            ivy_mass(L, ivy, face, cx, top, hw, ln, top + 15, +1, ("sivy", k))
        else:
            ivy_mass(L, ivy, face, cx, top + 15, hw, ln, top + 1, -1, ("sivy", k))
    sh = np.zeros((H, W), bool)
    sh[1:, 1:] = ivy[:-1, :-1]
    sh &= ~ivy & face
    L[sh] = SHADE_LUT[L[sh]]
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


# ---------------------------------------------------------------------------- v07 ground (v05t techniques, v06 plaza)
# v06's plaza turf was a checker-bordered noise zoning with one stamped tuft per jittered cell, its desire paths were
# flat soil bands and its meadow clumps were stamped blades. v07 re-implements v05t's authored ground on v06's
# unchanged walkable plaza: a hand-placed relief lit from the front-left key, quantised into calm tone bands whose
# edges are cut as grass-blade teeth (the nearer sward overlaps the farther one), materials (normal / damp / dry /
# shade), an authored long-grass weight that puts texture at edges and leaves the open sward calm, and a separate
# `terrain-patches` layer of story ground: worn desire lines, handcart ruts to the survey station, soil cores, leaf
# litter, a mossy wall-foot bed and a rush hollow. All placements are hand-written tables.
PLAZA_FORMS = [  # (cx, cy, rx, ry, height px, material): + rise, - hollow
    (40, 292, 46, 16, 6.0, "normal"),     # root swell round the old elm
    (150, 262, 64, 14, 3.0, "normal"),    # the survey station stands on a slight rise
    (250, 338, 58, 16, -4.5, "damp"),     # rain hollow between the west walk and the frame foot (rushes)
    (306, 300, 24, 9, -2.5, "damp"),      # puddle line beside the axis flags (west)
    (470, 340, 64, 16, 5.0, "dry"),       # sun-baked knoll round the fallen lamp
    (604, 298, 40, 12, 3.5, "dry"),       # east verge crown
    (488, 285, 24, 8, -3.0, "damp"),      # wet foot of the rubble spill
    (130, 336, 60, 16, 2.0, "normal"),    # low rise behind the foreground balustrade
    (566, 250, 36, 10, 2.5, "normal"),    # rise under the collapse
    (36, 336, 34, 14, 2.5, "shade"),      # under the elm's skirt of low limbs: dark sward
    (624, 330, 26, 22, 1.5, "shade"),     # under the foreground fern block
]
PLAZA_SWALES = [([(206, 318), (230, 330), (250, 338), (278, 354)], 9.0, 2.5)]   # (polyline, half width, depth)
LAWN_MATS = ["normal", "damp", "dry", "shade"]
LAWN_LUT_V7 = {"normal": ["g1", "g2", "g3", "g4", "g4"], "damp": ["f1", "g1", "g2", "g3", "g3"],
               "dry": ["g2", "g3", "g4", "g5", "d1"], "shade": ["f0", "g0", "g1", "g2", "g3"]}
# terrain-patches tables
DESIRE = [(WEST_PATH[0], 5.6, 1.0), (EAST_PATH[0], 5.0, 0.85),
          ([(232, 262), (226, 272), (224, 282)], 2.0, 0.45)]                           # forecourt -> tripod
RUTS_V7 = ([(338, 266), (300, 282), (256, 294), (214, 304)], 3.2)      # survey handcart: centre polyline, half gauge
RUT_MUD_V7 = (0.40, 0.62)                                              # dried puddle on this stretch of the ruts
SOIL_CORES_V7 = [(296, 318), (304, 320), (312, 322), (320, 324)]       # survey soil cores with lifted plugs
LITTER_V7 = [(70, 300, 40, 10), (28, 262, 20, 6), (112, 318, 22, 6)]      # only in the elm's shade (v07 1x read)
RUSH_V7 = [(250, 340, 34, 8), (304, 302, 12, 4)]
TUSSOCKS_V7 = [(206, 344, 40, 9), (548, 350, 30, 7), (84, 284, 20, 6), (616, 274, 18, 7), (130, 260, 16, 5),
               (24, 342, 14, 6), (604, 302, 12, 4)]
SEEDHEADS_V7 = [(470, 336, 40, 10), (446, 344, 16, 5), (300, 350, 26, 6)]
SLAB_STATES = [  # (x, y, w, h, tone) hand-placed wear on the axis flags and forecourt setts
    (348, 238, 22, 10, "dark"), (376, 262, 18, 10, "new"), (350, 286, 24, 10, "dark"), (380, 310, 16, 10, "new"),
    (362, 334, 20, 10, "dark"), (300, 238, 14, 8, "new"), (420, 244, 16, 8, "dark"), (458, 260, 14, 7, "new"),
    (280, 262, 14, 7, "dark")]


def _rng(*key):
    return np.random.default_rng(int.from_bytes(hashlib.sha256(repr(key).encode()).digest()[:8], "little"))


def below(a, k):
    """Array whose row y holds a's row y + k (edge rows repeat)."""
    out = np.empty_like(a)
    out[:H - k] = a[k:]
    out[H - k:] = a[H - 1:]
    return out


def dil1(m):
    """One-step 8-neighbour dilation without wrap-around at the frame edges."""
    p = np.pad(m, 1)
    out = m.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            out |= p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W]
    return out


def dist_to(mask, rmax):
    """Chessboard distance (px) to `mask`, saturated at rmax + 1."""
    d = np.full((H, W), float(rmax + 1), np.float32)
    cur = mask.copy()
    d[cur] = 0.0
    for k in range(1, rmax + 1):
        nxt = dil1(cur)
        d[nxt & ~cur] = k
        cur = nxt
    return d


def blob_e(cx, cy, rx, ry, key, wob=0.35):
    """Warped-ellipse field (< 1 inside): hand-placed forms get irregular edges."""
    n1 = vnoise(("blob7", key), 9)
    n2 = vnoise(("blob7b", key), 4)
    return (((XX + 0.5 - cx) / rx) ** 2 + ((YY + 0.5 - cy) / ry) ** 2 + (n1 - 0.5) * wob +
            (n2 - 0.5) * wob * 0.35)


def blade_teeth(key, maxlen, band=6):
    """Per-texel blade length for grass-edge teeth: runs of pointed clumps (2-5 px wide, peak 1..maxlen) with gaps;
    each 6-row band has its own run so stacked edges never repeat one pattern (v05t)."""
    r = _rng("teeth-v07", key, maxlen, band)
    nb = H // band + 2
    rows = []
    for _ in range(nb):
        out = np.zeros(W + 64, np.int16)
        x = int(r.integers(0, 3))
        while x < W + 64:
            w = int(r.integers(2, 6))
            peak = int(r.integers(max(1, maxlen // 2), maxlen + 1))
            c = (w - 1) / 2.0
            prof = [max(1, int(round(peak * (1 - abs(i - c) / (c + 1.0))))) for i in range(w)]
            out[x:x + w] = prof[:max(0, min(w, W + 64 - x))]
            x += w + int(r.integers(0, 3))
        rows.append(out)
    rows = np.stack(rows)
    shifts = r.integers(0, 64, nb)
    yb = np.arange(H) // band
    return rows[yb[:, None], np.arange(W)[None, :] + shifts[yb][:, None]]


def displace_up(a, teeth, valid):
    """a'(y, x) = a(y + t, x): the nearer (lower) sward's blades overlap the farther one along every boundary."""
    out = a.copy()
    for k in range(1, int(teeth.max()) + 1):
        m = (teeth == k) & valid & below(valid, k)
        out[m] = below(a, k)[m]
    return out


def despeckle_code(code, valid, passes=2):
    """A texel whose four neighbours all differ from it takes its upper (else left) neighbour's value."""
    for _ in range(passes):
        up = np.roll(code, 1, 0); dn = np.roll(code, -1, 0); lf = np.roll(code, 1, 1); rt = np.roll(code, -1, 1)
        vu = np.roll(valid, 1, 0); vl = np.roll(valid, 1, 1)
        iso = valid & (code != up) & (code != dn) & (code != lf) & (code != rt)
        code = np.where(iso & vu, up, np.where(iso & vl, lf, code))
    return code


def polyline_dist(pts, pad):
    """Distance (px) to a polyline and the arc-length parameter 0..1 of the nearest point, inside its bbox + pad."""
    d = np.full((H, W), np.inf, np.float32)
    t = np.zeros((H, W), np.float32)
    xs_ = [p[0] for p in pts]; ys_ = [p[1] for p in pts]
    x0, x1 = int(max(0, min(xs_) - pad)), int(min(W, max(xs_) + pad + 1))
    y0, y1 = int(max(0, min(ys_) - pad)), int(min(H, max(ys_) + pad + 1))
    if x0 >= x1 or y0 >= y1:
        return d, t
    X, Y = XX[y0:y1, x0:x1] + 0.5, YY[y0:y1, x0:x1] + 0.5
    seglen = [math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(pts, pts[1:])]
    tot = max(1e-6, sum(seglen))
    best = np.full(X.shape, np.inf, np.float32)
    bt = np.zeros(X.shape, np.float32)
    acc = 0.0
    for (p, q), sl in zip(zip(pts, pts[1:]), seglen):
        dx, dy = q[0] - p[0], q[1] - p[1]
        u = np.clip(((X - p[0]) * dx + (Y - p[1]) * dy) / max(1e-6, dx * dx + dy * dy), 0, 1)
        dd = np.hypot(X - (p[0] + u * dx), Y - (p[1] + u * dy))
        upd = dd < best
        best[upd] = dd[upd]
        bt[upd] = ((acc + u * sl) / tot)[upd]
        acc += sl
    d[y0:y1, x0:x1] = best
    t[y0:y1, x0:x1] = bt
    return d, t


def lawn_fields(m):
    """Relief (px), material map and long-grass weight of the plaza turf (v05t's model on v06's plaza)."""
    grass = m["ground"] & ~m["paving"]
    Hh = np.zeros((H, W), np.float32)
    mat = np.zeros((H, W), np.int8)
    for k, (cx, cy, rx, ry, ht, mt) in enumerate(PLAZA_FORMS):
        e = blob_e(cx, cy, rx, ry, ("form", k), wob=0.4)
        Hh += ht * np.clip(1 - e, 0, 1) ** 1.5
        if mt != "normal":
            mat[e < 0.75] = LAWN_MATS.index(mt)
    for k, (pts, hw, dep) in enumerate(PLAZA_SWALES):
        d, _ = polyline_dist(pts, hw + 4)
        Hh -= dep * np.clip(1 - d / hw, 0, 1) ** 1.3
    # long grass: the wall foot, along the paving edges, the frame edges, round the rubble and the kit; calm sward
    # elsewhere; dry knolls run long
    lg = 0.65 * np.clip(1 - (YY - WALL_FOOT[None, :]) / 14.0, 0, 1)
    lg = lg + 0.45 * np.clip(1 - dist_to(m["paving"], 6) / 6.0, 0, 1)
    lg = lg + 0.55 * np.clip(1 - np.minimum(XX, W - 1 - XX) / 34.0, 0, 1)
    lg = lg + 0.40 * np.clip((YY - 334) / 24.0, 0, 1)
    heap = poly_mask(HEAP)
    lg = lg + 0.55 * np.clip(1 - dist_to(heap, 10) / 10.0, 0, 1)
    lg = lg + 0.5 * (mat == LAWN_MATS.index("dry"))
    lg = np.clip(lg, 0, 1) * grass
    return grass, Hh, mat, lg


def paint_lawn_v7(L, m):
    grass, Hh, mat, lg = lawn_fields(m)
    gy_, gx_ = np.gradient(Hh)
    n = np.sqrt(gx_ ** 2 + gy_ ** 2 + 1)
    shade = (-gx_ * LIGHT[0] - gy_ * LIGHT[1] + LIGHT[2]) / n - LIGHT[2]
    f = 0.34 + 1.9 * shade
    # value hierarchy: the frame foot and the side edges sit lower, the turf round the forecourt and axis is lit, so
    # the eye runs up the axis to the stair and the Capitol (the open sward stays a calm mid-dark g2/g3)
    f -= 0.16 * np.clip((YY - 296) / 60.0, 0, 1)
    f -= 0.12 * np.clip(1 - XX / 150.0, 0, 1) + 0.12 * np.clip(1 - (W - 1 - XX) / 150.0, 0, 1)
    f += 0.08 * np.clip(1 - dist_to(m["paving"], 24) / 24.0, 0, 1)
    f += (vnoise("lawn-v07-broad", 90) - 0.5) * 0.10
    f += (vnoise("lawn-v07-clump", 16) - 0.5) * 0.16 + (vnoise("lawn-v07-clump2", 6) - 0.5) * 0.05
    B = np.digitize(f, [0.18, 0.37, 0.63, 0.80]).astype(np.int16)
    maxlen = np.choose(mat.astype(np.int64), [3, 3, 4, 2]).astype(np.int16)
    maxlen = np.maximum(maxlen, (lg * 4).astype(np.int16))
    teeth = np.minimum(blade_teeth("lawn", 5), maxlen).astype(np.int16)
    code = mat.astype(np.int16) * 8 + B
    code = displace_up(code, teeth, grass)
    code = despeckle_code(code, grass, 2)
    lut = np.zeros(len(LAWN_MATS) * 8, np.int16)
    for mi, mname in enumerate(LAWN_MATS):
        for b, cname in enumerate(LAWN_LUT_V7[mname]):
            lut[mi * 8 + b] = I[cname]
    col = lut[code]
    L[grass] = col[grass]
    return grass, lg


def paint_plaza_ground():
    L = new()
    m = plaza_masks()
    paint_lawn_v7(L, m)
    setts(L, m["forecourt"], "fan")
    flags(L, m["axis"], int(FORECOURT[1]) + 2, 12, "axis", (26, 18, 24, 15, 22, 28, 17, 20))
    # v07: hand-placed wear on the paving (stained, replaced and sunk slabs), never a scatter
    pave_dn = {k: shift(PAVE, k, -1) for k in PAVE}
    pave_up = {k: shift(PAVE, k, 1) for k in PAVE}
    for (x, y, w, h, tone) in SLAB_STATES:
        sub = m["paving"][y:y + h, x:x + w]
        tgt = L[y:y + h, x:x + w]
        for (j, i) in zip(*np.nonzero(sub)):
            c = int(tgt[j, i])
            if c not in PAVE:
                continue
            tgt[j, i] = (pave_up if tone == "new" else pave_dn)[c]
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


def paint_terrain_patches(base):
    """v07 `terrain-patches` layer (v05t painters on v06's plaza): story ground over the turf, never on paving."""
    L = new()
    m = plaza_masks()
    grass = m["ground"] & ~m["paving"]
    area = {}
    # mossy wall-foot bed: dark soil with moss cushions where the turf meets the seat wall (not at the steps / gap)
    bed_h = 3 + (vnoise("bed-v07", 7) * 4).astype(int)
    bed = grass & (YY < WALL_FOOT[None, :] + bed_h) & (DROP[None, :] == 0)
    bed &= ~box(CHEEKS[0][0] - 3, 0, CHEEKS[1][1] + 3, H - 1)
    L[bed] = np.where(vnoise("bedtone-v07", 4)[bed] < 0.45, I["s0"], I["s1"])
    moss = bed & (vnoise("bedmoss-v07", 3) > 0.58)
    L[moss] = I["mo0"]
    L[moss & ~np.roll(moss, 1, 0)] = I["mo1"]
    area["wall_foot_bed"] = int(bed.sum())
    # leaf-litter drifts: overlapping 2-px leaves in warm browns, thickening toward each drift's core
    lit_m = np.zeros((H, W), bool)
    for k, (cx, cy, rx, ry) in enumerate(LITTER_V7):
        lit_m |= (blob_e(cx, cy, rx, ry, ("litter", k), wob=0.6) < 1.2) & grass
    r = _rng("litter-v07")
    ys, xs = np.nonzero(lit_m)
    for i in r.permutation(len(ys))[: len(ys) // 9]:
        y, x = int(ys[i]), int(xs[i])
        a, b = (("s2", "s3"), ("b2", "s2"), ("s1", "s2"), ("d0", "s3"), ("s3", "b3"))[int(r.integers(0, 5))]
        L[y, x] = I[a]
        if x + 1 < W and lit_m[y, x + 1]:
            L[y, x + 1] = I[b]
        if y + 1 < H and lit_m[y + 1, x] and L[y + 1, x] < 0:
            L[y + 1, x] = SHADE_LUT[base[y + 1, x]]
    area["leaf_litter"] = int(lit_m.sum())
    # worn desire lines: soil with a lit crown, a shaded lower edge and a broken upper bank, pebbles with contact
    # shade, grass islands, a fringe of trampled straw-olive sward cut by blade teeth
    worn = np.zeros((H, W), bool); crown = np.zeros((H, W), bool); fringe = np.zeros((H, W), bool)
    wobble = vnoise("desire-w-v07", 7)
    for k, (pts, hw, wear) in enumerate(DESIRE):
        d, tt = polyline_dist(pts, hw + 8)
        # the two walks run off the frame and into the forecourt (no taper); the short tracks taper at both ends
        taper = 1.0 if k < 2 else np.clip(np.minimum(tt, 1 - tt) / 0.12, 0.4, 1)
        w_ = hw * taper * (0.78 + 0.45 * wobble)
        worn |= (d < w_) & grass
        crown |= (d < w_ * 0.42) & (wear > 0.55) & grass
        fringe |= (d >= w_) & (d < w_ + 2.0 + 2.0 * wear) & grass
    fringe &= ~worn
    fr = displace_up(fringe.astype(np.int8), blade_teeth("fringe", 3), grass).astype(bool) & ~worn
    L[fr] = np.where(((XX + YY // 2) % 5 == 0)[fr], I["d1"], I["d0"])
    L[worn] = I["s3"]
    L[worn & crown] = I["s4"]
    L[worn & ~below(worn, 1)] = I["s1"]
    L[worn & ~np.roll(worn, 1, 0) & (XX % 3 != 0)] = I["s2"]
    rr = _rng("pebbles-v07")
    for gy in range(0, H, 6):
        for gx in range(0, W, 6):
            x = gx + int(rr.integers(0, 6)); y = gy + int(rr.integers(0, 6))
            if x + 1 < W and y + 1 < H and worn[y, x] and worn[y, x + 1] and rr.random() < 0.45:
                L[y, x] = I["gr4"]; L[y, x + 1] = I["gr3"] if rr.random() < 0.6 else I["gr4"]
                L[y + 1, x] = I["s1"]; L[y + 1, x + 1] = I["s1"]
    for gy in range(0, H, 9):
        for gx in range(0, W, 9):
            x = gx + int(rr.integers(0, 9)); y = gy + int(rr.integers(0, 9))
            if worn[min(H - 1, y), min(W - 1, x)] and not crown[min(H - 1, y), min(W - 1, x)] and rr.random() < 0.35:
                for (i, j, c) in ((0, 0, "g3"), (1, 0, "g3"), (-1, 1, "g2"), (0, 1, "g2"), (1, 1, "g2"),
                                  (0, -1, "g4"), (2, 1, "s1")):
                    if 0 <= x + i < W and 0 <= y + j < H and worn[y + j, x + i]:
                        L[y + j, x + i] = I[c]
    area["worn_earth"] = int(worn.sum()); area["trampled_fringe"] = int(fr.sum())
    # remnant flags of the First Street walk along the west path (root-heaved by the elm), as in v06
    for (x, y, w) in WEST_SLABS:
        rect(L, x, y - 3, x + w - 1, y + 1, "p3"); rect(L, x, y - 3, x + w - 1, y - 3, "p4")
        rect(L, x, y + 1, x + w - 1, y + 1, "p1"); px(L, x + w - 1, y - 2, "p2")
    for (a, b) in (((26, 307), (44, 312)), ((50, 302), (60, 314)), ((68, 304), (88, 300)), ((92, 298), (104, 304))):
        for (x, y) in zip(np.linspace(a[0], b[0], 24), np.linspace(a[1], b[1], 24)):
            px(L, round(x), round(y), "s0")
    # handcart ruts from the forecourt to the survey station: twin compacted tracks, crushed sward between them,
    # a dried puddle with mud cracks where the ground dips
    pts, half = RUTS_V7
    d, tt = polyline_dist(pts, half + 6)
    between = (d < half - 1.0) & grass & ~worn
    L[between & ((XX * 3 + YY) % 4 != 0)] = I["d0"]
    rut = np.zeros((H, W), bool)
    for side in (-1, 1):
        off = []
        for p, q in zip(pts, pts[1:]):
            dx, dy = q[0] - p[0], q[1] - p[1]
            ln = math.hypot(dx, dy)
            nx, ny = -dy / ln * side * half, dx / ln * side * half
            off.append(((p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny)))
        for (a, b) in off:
            rut |= seg(a, b, 0.75)
    rut &= grass
    L[rut] = I["s1"]
    L[rut & ~below(rut, 1)] = I["s0"]
    L[rut & ~np.roll(rut, 1, 0)] = I["s2"]
    mud = (d < half + 2.5) & (tt > RUT_MUD_V7[0]) & (tt < RUT_MUD_V7[1]) & grass & ~worn
    mud &= blob_e(268, 291, 16, 5, "mud", wob=0.5) < 1
    L[mud] = I["s2"]
    crack = mud & ((np.abs((XX - YY * 2) % 9) < 1) | (np.abs((XX + YY) % 11) < 1))
    L[crack] = I["s1"]
    L[mud & ~np.roll(mud, 1, 0)] = I["s3"]
    area["handcart_ruts"] = int((rut | between).sum()); area["dried_puddle"] = int(mud.sum())
    # survey soil cores: a neat row of holes, each plug lifted out and laid beside it
    for (x, y) in SOIL_CORES_V7:
        for (i, j, c_) in ((0, 0, "ink"), (1, 0, "s0"), (0, 1, "s0"), (1, 1, "s0"), (-1, 0, "s1"), (2, 0, "s2"),
                           (3, -2, "s3"), (4, -2, "s2"), (3, -1, "s1"), (4, -1, "s1"), (3, -3, "g3"), (4, -3, "g4")):
            px(L, x + i, y + j, c_)
    area["soil_cores"] = 12 * len(SOIL_CORES_V7)
    L[~m["ground"] | m["paving"]] = -1
    return L, area


TUFT_SPEC = {"seed": (3, 5, 5, 8, ("g2", "g3", "g4", "g5"), "d1"),
             "rush": (4, 6, 5, 9, ("f1", "g1", "g2", "g3"), "d0"),
             "long": (3, 5, 4, 6, ("g2", "g3", "g4", "g5"), "lw5"),
             "short": (2, 4, 2, 3, ("g2", "g3", "g4", "g4"), "g5")}


def tuft_texels(r, kind):
    """One grass / rush tuft as (dx, dy, palette name) texels, base at dy = 0: blades fan out from the base and lean;
    the left (lit) blades are a step lighter; tips may carry the kind's head colour (v05t)."""
    nmin, nmax, hmin, hmax, ramp, tip = TUFT_SPEC[kind]
    n = int(r.integers(nmin, nmax + 1))
    out = []
    for i in range(n):
        bx = i - n // 2
        h = int(r.integers(hmin, hmax + 1))
        lean = (bx * 0.18 + float(r.uniform(-0.25, 0.25))) * (0.4 if kind == "rush" else 1.0)
        lit = 1 if bx < 0 else 0
        for j in range(h):
            x = bx + int(round(lean * (j ** 1.25) / max(1, h ** 0.25)))
            out.append((x, -j, ramp[min(3, (j * 4) // h + lit)]))
        if kind == "seed" and r.random() < 0.45:
            x = bx + int(round(lean * ((h - 1) ** 1.25) / max(1, h ** 0.25)))
            out += [(x, -h, tip), (x + 1, -h + 1, "lw5"), (x, -h + 1, tip)]
        elif r.random() < 0.3:
            x = bx + int(round(lean * ((h - 1) ** 1.25) / max(1, h ** 0.25)))
            out.append((x, -h, tip))
    return out, n


def paint_tufts(layer, comp, pts, kind, key, mask):
    """Tufts back to front (north first) so nearer tufts overlap farther ones, each with a 1-row contact shade."""
    r = _rng("tufts-v07", key, kind)
    for (x, y) in sorted(pts, key=lambda p: (p[1], p[0])):
        tex, n = tuft_texels(r, kind)
        for i in range(-(n // 2) - 1, n - n // 2 + 1):
            xx, yy = x + i, y + 1
            if 0 <= xx < W and 0 <= yy < H and mask[yy, xx] and comp[yy, xx] >= 0:
                layer[yy, xx] = SHADE_LUT[comp[yy, xx]]
        for dx, dy, c in tex:
            xx, yy = x + dx, y + dy
            if 0 <= xx < W and 0 <= yy < H and mask[yy, xx]:
                layer[yy, xx] = I[c]


def scatter_pts(mask, spacing, key, keep):
    """Jittered-grid points inside `mask`, kept with probability `keep` (a number or a full-frame field)."""
    r = _rng("scatter-v07", key, spacing)
    pts = []
    for gy in range(0, H, spacing):
        for gx in range(0, W, spacing):
            x = gx + int(r.integers(0, spacing)); y = gy + int(r.integers(0, spacing))
            if x < W and y < H and mask[y, x]:
                p = keep[y, x] if isinstance(keep, np.ndarray) else keep
                if r.random() < p:
                    pts.append((x, y))
    return pts


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


def paint_ground_detail(base, terrain):
    """Ground detail over the turf and paving. v06's cracks, joint moss, patrol claw prints, laser scorch, flower
    drifts and wall-foot lip are kept; v06's 98 randomly scattered leaves, 40 random pebbles and stamped meadow
    blades are replaced (v07) by litter drifts and path pebbles in `terrain-patches` and by generated tussocks, seed
    heads, rushes and long-grass tufts placed by the authored long-grass weight (none on the open sward)."""
    L = new()
    m = plaza_masks()
    pav = m["paving"]
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
    near_wall = m["forecourt"] & (YY < WALL_FOOT[None, :] + 10)
    ys, xs = np.nonzero(near_wall)
    for y, x in zip(ys, xs):
        if hval("moss", x, y) < 0.10:
            px(L, x, y, "mo0" if hval("moss2", x, y) < 0.5 else "mo1")
    for k, (x, y) in enumerate(PATROL_PRINTS):
        ox = 3 if k % 2 else -3
        on_pave = pav[min(H - 1, y), min(W - 1, max(0, x))]
        stamp(L, x + ox - 2, y - 1, PRINT, {"x": "p1" if on_pave else "s1"})
        if not on_pave:
            rect(L, x + ox - 2, y + 2, x + ox + 2, y + 2, "s2")
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
    grass = m["ground"] & ~pav
    free = grass & (terrain < 0)
    comp = base.copy()
    comp[terrain >= 0] = terrain[terrain >= 0]
    for i, (cx, cy, cols, rx, ry, n_) in enumerate(FLOWER_DRIFTS):
        for k in range(n_ * 6):
            a = hval("fd", i, k) * 2 * math.pi
            rr = math.sqrt(hval("fr", i, k))
            x = round(cx + math.cos(a) * rr * rx); y = round(cy + math.sin(a) * rr * ry)
            if 0 <= x < W - 1 and 0 <= y < H - 1 and free[y, x]:
                c = cols[int(hval("fc", i, k) * len(cols))]
                px(L, x, y, c)
                if hval("fs", i, k) < 0.4:
                    px(L, x + 1, y, c)
                px(L, x, y + 1, "g1")
    # tussock meadows: a dense standing clump with a shaded front band, seed tufts drawn back to front
    tus = np.zeros((H, W), bool)
    for k, (cx, cy, rx, ry) in enumerate(TUSSOCKS_V7):
        tus |= (blob_e(cx, cy, rx, ry, ("tus", k), wob=0.55) < 1) & free
    L[tus] = np.where(((XX * 7 + YY * 3) % 5 == 0)[tus], I["g2"], I["g3"])
    L[tus & ~below(tus, 2)] = I["g1"]
    paint_tufts(L, comp, scatter_pts(tus, 4, "tus-pts", 0.85), "seed", "tus", grass)
    # seed heads standing in the sward on the dry knoll (stalk + 2-3 px head, no clump)
    heads = np.zeros((H, W), bool)
    for k, (cx, cy, rx, ry) in enumerate(SEEDHEADS_V7):
        heads |= (blob_e(cx, cy, rx, ry, ("heads", k), wob=0.5) < 1) & free & ~tus
    r = _rng("seedheads-v07")
    for (x, y) in scatter_pts(heads, 5, "head-pts", 0.5):
        if y > 6:
            hh = int(r.integers(2, 6)); lean = int(r.integers(-1, 2))
            for j in range(1, hh):
                px(L, x + (lean if j > hh // 2 else 0), y - j, "g3" if j < hh - 1 else "d0")
            hx = min(W - 2, max(0, x + lean))
            px(L, hx, y - hh, "d1")
            if r.random() < 0.6:
                px(L, hx + 1, y - hh + int(r.integers(0, 2)), "lw5" if r.random() < 0.4 else "d1")
            L[y, x] = SHADE_LUT[comp[y, x]]
    # rush hollow (damp): sparse upright rushes, dark-green, never teal
    rush = np.zeros((H, W), bool)
    for k, (cx, cy, rx, ry) in enumerate(RUSH_V7):
        rush |= (blob_e(cx, cy, rx, ry, ("rush", k), wob=0.6) < 1) & free & ~tus
    paint_tufts(L, comp, scatter_pts(rush, 5, "rush-pts", 0.7), "rush", "rush", grass)
    # long-grass tufts where the authored weight is high (edges, wall foot, rubble, dry knoll); none on the open sward
    _, _, _, lg = lawn_fields(m)
    open_ = free & ~tus & ~rush & ~heads
    lpts = scatter_pts(open_, 5, "lg-pts", np.where(lg > 0.32, lg * 0.85, 0.0))
    paint_tufts(L, comp, [p for p in lpts if lg[p[1], p[0]] >= 0.55], "long", "lg-long", grass)
    paint_tufts(L, comp, [p for p in lpts if lg[p[1], p[0]] < 0.55], "short", "lg-short", grass)
    for x in range(W):                                        # wall-foot grass lip and dark contact strip (v06)
        y = WALL_FOOT[x]
        if 0 <= y < H and DROP[x] == 0 and not (CHEEKS[0][0] <= x <= CHEEKS[1][1]):
            if hval("wf", x // 2) < 0.6 and not pav[y, x]:
                px(L, x, y, "g1")
                if hval("wft", x) < 0.4:
                    px(L, x, y - 1, "g2")
    L[~m["ground"]] = -1
    return L


# ============================================================================ 14 rubble (collapsed seat-wall bay)
def poly_local(pts, x0, y0, x1, y1):
    """Texels (x, y) inside the polygon `pts` (vertex coordinates on texel corners), searched in a small box only."""
    ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    cx, cy = xs + 0.5, ys + 0.5
    m = np.zeros(xs.shape, bool)
    for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
        cond = (ay > cy) != (by > cy)
        xint = (bx - ax) * (cy - ay) / (by - ay if by != ay else 1e-9) + ax
        m ^= cond & (cx < xint)
    return [(int(a), int(b)) for a, b in zip(xs[m], ys[m])]


def block(L, x, base, w, h, kind, t, reg, key):
    """v06 pass 2: a broken masonry block as three irregular facets inside the v05 footprint (x .. x+w-1,
    base-h+1 .. base) -- a skewed, corner-chipped top face, a front face with a fracture and pitting, a dark right
    side -- lit from the front-left, with a dark contact edge. `cut` keeps the clean laser-cut face with a scorched
    edge (patrol cue); `chip` is a small five-sided shard."""
    j = lambda k, a: int(round((hval(key, k) - 0.5) * a))
    yt = base - h + 1
    if kind == "chip":
        pts = [(x, base + 1), (x + max(1, j("c0", 3) + 1), yt + max(0, j("c1", 2))),
               (x + w - 2 + j("c2", 2), yt), (x + w, yt + h // 2 + j("c3", 2)), (x + w - 1, base + 1)]
        for (a, b) in poly_local(pts, x, yt, x + w - 1, base):
            px(L, a, b, t, reg)
        for (a, b) in poly_local(pts, x, yt, x + w - 1, base):
            if b == yt or (b == yt + 1 and a < x + w // 2):
                px(L, a, b, "gr4" if t != "gr4" else "gr5", reg)
            elif a >= x + w - 2:
                px(L, a, b, "gr1", reg)
        rect(L, x + 1, base, x + w - 2, base, "gr1", reg)
        return
    if kind == "drum":                                                     # fallen marble column drum, end-on left
        r = (h - 1) / 2.0
        cy = base - r
        for a in range(x, x + w):
            for b in range(yt, base + 1):
                v = (b - cy) / r
                if abs(v) > 1.0:
                    continue
                c = "m6" if v < -0.55 else "m5" if v < -0.1 else "m4" if v < 0.45 else "m3" if v < 0.8 else "gr2"
                if (b - yt) % 3 == 1 and v > -0.6 and hval(key, "flute", a // 4) < 0.85:
                    c = shift_name("gr4", 0) if c in ("m4", "m3") else c          # flute shadow lines
                px(L, a, b, c, reg)
        ex = max(2, int(r * 0.55))                                         # elliptic broken end face
        for b in range(yt, base + 1):
            v = (b - cy) / r
            if abs(v) <= 1.0:
                half = int(round(ex * math.sqrt(max(0.0, 1 - v * v))))
                for a in range(x, x + half + 1):
                    px(L, a, b, "m5" if (a - x + b) % 5 else "m3", reg)
                px(L, x + half + 1, b, "gr2", reg)
        rect(L, x + 2, base, x + w - 2, base, "gr1", reg)
        return
    marble = kind == "coping"
    topc = "m5" if marble else shift_name(t, 1) if t in ("gr2", "gr3", "gr4") else "gr5"
    sidec = "gr2" if marble else "gr1"
    top_h = max(2, h // 3 + j("th", 2))
    side = max(1, w // 6 + (1 if hval(key, "sd") < 0.4 else 0))
    xr = x + w - 1 - side                                                  # front/side edge column
    tilt = j("tilt", max(3, w // 3))                                       # the block lies askew
    A = (x + 1 + max(0, j("ax", 4)), yt + max(0, tilt))
    B = (xr + 1 + j("bx", 2), yt + max(0, -tilt))
    Cp = (xr + 1, yt + top_h)
    D = (x, yt + top_h + max(0, j("dy", 2)))
    E = (x + max(0, j("ex", 3)), base + 1)
    Fp = (xr + 1, base + 1)
    G = (x + w, yt + top_h // 2 + max(0, -tilt) + j("gy", 2))
    Hp = (x + w, base + 1 - max(0, j("hy", 3)))
    box_ = (x - 1, yt - 1, x + w, base + 1)
    for (a, b) in poly_local([A, B, Cp, D], *box_):                        # top face
        px(L, a, b, topc, reg)
    front = poly_local([D, Cp, Fp, E], *box_)
    for (a, b) in front:                                                   # front face: pitted, slightly varied
        c = t
        if hval(key, "pit", a, b) < 0.10:
            c = shift_name(t, -1) if not marble else "m3"
        elif not marble and hval(key, "lit", a // 3, b // 2) < 0.12:
            c = shift_name(t, 1)
        px(L, a, b, c, reg)
    for (a, b) in poly_local([B, G, Hp, Fp, Cp], *box_):                   # shaded side
        px(L, a, b, sidec, reg)
    for (a, b) in poly_local([D, Cp, (Cp[0], Cp[1] + 1), (D[0], D[1] + 1)], *box_):
        px(L, a, b, "m6" if marble else "gr5", reg)                       # lit arris between top and front
    if not marble and h >= 8 and kind != "cut":                            # fracture across the front face
        fx = x + 2 + int(hval(key, "fx") * max(1, w - side - 6))
        y = yt + top_h + 1
        while y <= base - 1:
            px(L, fx, y, "gr1", reg)
            if hval(key, "fr", y) < 0.45:
                px(L, fx + 1, y, "gr2", reg)
            fx += 1 if hval(key, "fd", y) < 0.4 else (-1 if hval(key, "fd", y) > 0.8 else 0)
            y += 1
    if kind == "cut":
        for k in range(h - top_h):
            px(L, x + 3 + k, base - k, "gr5", reg)
            px(L, x + 4 + k, base - k, "sc0", reg)
    for (a, b) in front:
        if b == base:
            px(L, a, b, "ink" if not marble else "gr1", reg)
    if hval(key, "moss") < 0.4:
        for k in range(int(w * 0.4)):
            if hval(key, "mo", k) < 0.75:
                px(L, A[0] + k, A[1] + (1 if k % 3 == 2 else 0), "mo1", reg)


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
    # v07: the core is a bed of broken stones (Voronoi cells ~7 x 4 px), each lit on its upper-left and dark in the
    # crevice on its lower-right, darker toward the toe -- v06's 2-px value noise read as gravel static at 1x
    ys_, xs_ = np.nonzero(heap)
    y0h, y1h, x0h, x1h = ys_.min(), ys_.max() + 1, xs_.min(), xs_.max() + 1
    X, Y = XX[y0h:y1h, x0h:x1h] + 0.5, YY[y0h:y1h, x0h:x1h] + 0.5
    sxc, syc = 6.0, 5.0
    best = np.full(X.shape, 1e9, np.float32); second = np.full(X.shape, 1e9, np.float32)
    uu = np.zeros(X.shape, np.float32); vv = np.zeros(X.shape, np.float32); cid = np.zeros(X.shape, np.int64)
    ci0, cj0 = np.floor(X / sxc).astype(np.int64), np.floor(Y / syc).astype(np.int64)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            ci, cj = ci0 + di, cj0 + dj
            cx = (ci + 0.03 + 0.94 * wnoise(("stone", "x"), ci * 0.73 + 0.31, cj * 0.71 + 0.17)) * sxc
            cy = (cj + 0.03 + 0.94 * wnoise(("stone", "y"), ci * 0.69 + 0.11, cj * 0.77 + 0.43)) * syc
            u, v = (X - cx) / sxc, (Y - cy) / syc
            d = u * u + v * v
            upd = d < best
            second = np.where(upd, best, np.minimum(second, d))
            best = np.where(upd, d, best); uu = np.where(upd, u, uu); vv = np.where(upd, v, vv)
            cid = np.where(upd, ci * 7919 + cj, cid)
    tone = (wnoise(("stone", "t"), (cid % 7919) * 0.37, (cid // 7919) * 0.41) +
            0.35 * (Y - y0h) / max(1, y1h - y0h)).astype(np.float32)
    ramp = R("gr1", "gr2", "gr3", "gr4")
    k = np.clip((3.2 - tone * 3.2).astype(np.int64), 0, 3)
    sub = np.array(ramp, np.int16)[k]
    tilt = wnoise(("stone", "a"), (cid % 7919) * 0.53, (cid // 7919) * 0.47) * 2.4 - 0.2   # each stone lies askew
    lit_ = (uu * np.cos(tilt) + vv * np.sin(tilt) < -0.30) & (k < 3)
    sub = np.where(lit_, np.array(ramp, np.int16)[np.clip(k + 1, 0, 3)], sub)
    rim = (uu * np.cos(tilt) + vv * np.sin(tilt) > 0.46)
    sub = np.where(rim, I["gr1"], sub)
    joint = (second - best) < 0.07
    sub = np.where(joint, np.where(wnoise(("stone", "j"), X * 0.5, Y * 0.5) > 0.55, I["gr0"], I["gr1"]), sub)
    hm = heap[y0h:y1h, x0h:x1h]
    tgt = L[y0h:y1h, x0h:x1h]
    tgt[hm] = sub[hm]
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
    crown_lobes(L, cluster_lobes(lobes, "ailanthus"), NEAR, NEAR_CUTS, "ailanthus", reg, squash=0.8, gain=1.1,
                leaf=2)                                         # v07: clustered lobes (v06 read as bubble balls)
    items["ailanthus"] = {"mask": reg & (YY > b - 8), "base": b, "shadow_mask": reg.copy()}
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


def project_shadow(mask, g, out, core=None, contact=3):
    """v05t's forward projection: a texel of a standing object at screen (X, Y) above its contact row g stands
    z = g - Y high, and its shadow lands at (X + SUN_DX z, g + SUN_DY z). The lowest `contact` rows also mark `core`
    (the dark contact line under the object)."""
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return
    z = np.maximum(0.0, g - ys)
    for off in (0.0, 0.5):
        sx = np.round(xs + SUN_DX * z + off).astype(int)
        sy = np.round(g + SUN_DY * z).astype(int)
        ok = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)
        out[sy[ok], sx[ok]] = True
        if core is not None and off == 0.0:
            c = ok & (z < contact)
            core[sy[c], sx[c]] = True
            core[np.minimum(H - 1, sy[c] + 1), sx[c]] = True


def paint_shadows(below_, items, sprites):
    """v07 cast shadows: v06's shade pools (the elm's crown over the survey station, off-screen trees at the frame
    foot) plus every standing object's own silhouette projected from its contact row (v05t), with a darker contact
    core and grass-blade teeth on the shadow edge. Shadows fall on the plaza, the steps and the stair landing."""
    sm = np.zeros((H, W), bool)
    core = np.zeros((H, W), bool)
    dap = np.zeros((H, W), bool)
    for (cx, cy, rx, ry) in ((140, 240, 70, 14), (230, 236, 46, 10), (86, 262, 40, 10)):
        dap |= ell(cx, cy, rx, ry)
    sm |= dap & (vnoise("dapple", 6) > 0.45)
    deep = np.zeros((H, W), bool)
    for grp in OFFSCREEN_SHADE:
        dm = np.zeros((H, W), bool)
        for (cx, cy, rx, ry) in grp:
            dm |= ell(cx, cy, rx, ry)
        dn = vnoise(("offshade", grp[0][0]), 5)
        sm |= dm & (dn > 0.36)
        deep |= dm & (dn > 0.52)
    for name, it in items.items():
        g = FG_FOOTPRINTS[name][3] if it.get("fg") else it["base"]
        project_shadow(it.get("shadow_mask", it["mask"]), g, sm, core)
    for name, (lay, pivot) in sprites.items():
        msk = lay >= 0
        if name == "elm-ysort":
            msk &= (XX < ELM[0] + 26) & (YY > 120)                  # trunk and limb only; the crown is a shade pool
        project_shadow(msk, pivot, sm, core)
    allowed = (YY >= WALL_FOOT[None, :]) & ~box(CHEEKS[0][0], 0, CHEEKS[1][1], 222)
    allowed |= box(CHEEKS[0][1] + 1, 203, CHEEKS[1][0] - 1, 222)              # steps and landing between the cheeks
    m = plaza_masks()
    grass = m["ground"] & ~m["paving"]
    sm = np.where(grass, displace_up(sm.astype(np.int8), blade_teeth("shadow", 2), grass).astype(bool), sm)
    sm &= allowed
    core &= sm
    deep &= sm
    L = new()
    L[sm] = SHADE_LUT[np.clip(below_[sm], 0, None)]
    dd = core | deep
    L[dd] = SHADE_LUT[L[dd]]
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
    layers = {"sky": paint_sky(), "clouds": paint_clouds(), "capitol-dome": paint_dome(),
              "breach-interiors": paint_breach_interiors()}
    front = paint_west_front()
    voids = ruin_voids()
    void = np.zeros((H, W), bool)
    for v in voids.values():
        void |= v
    front[void] = -1
    layers["capitol-west-front"] = front
    fw = paint_facade_weathering(front)
    fw[void] = -1
    layers["facade-weathering"] = fw
    ruin = paint_capitol_ruin(front)
    ruin[void] = -1                                    # v07 cut its overlay only in the House bite; v08 in every void
    deb = collapse_debris()
    ruin[deb >= 0] = deb[deb >= 0]
    edges = paint_breach_edges(front)
    ruin[edges >= 0] = edges[edges >= 0]
    layers["capitol-ruin"] = ruin
    layers["olmsted-terrace"] = paint_terrace()
    layers["breach-rubble"] = paint_breach_rubble()
    layers["west-lawn"] = paint_west_lawn()
    layers["grounds-trees"] = paint_grounds_trees()
    layers["patrol-walker"] = paint_patrol_walker()
    layers["lawn-edge-planting"] = paint_lawn_edge()
    layers["seat-wall-steps"] = paint_seat_wall()
    layers["plaza-ground"] = paint_plaza_ground()
    layers["terrain-patches"], terrain_area = paint_terrain_patches(layers["plaza-ground"])
    layers["ground-detail"] = paint_ground_detail(layers["plaza-ground"], layers["terrain-patches"])
    below = composite_idx(layers, list(layers))
    rubble, items = paint_rubble()
    props, pitems = paint_props()
    items.update(pitems)
    fg, fitems = paint_fg()
    wall = layers["seat-wall-steps"] >= 0
    for i, (x0, x1) in enumerate(CHEEKS):
        items[f"cheek_{i}"] = {"mask": wall & box(x0 - 1, 150, x1 + 1, 222), "base": 222}
    sprites = {"survey-mast-ysort": paint_mast(), "survey-tripod-ysort": paint_tripod(),
               "beacon-ysort": paint_beacon(), "elm-ysort": paint_elm()}
    shadow_items = dict(items)
    for k, v in fitems.items():
        shadow_items[k] = {"mask": v["mask"], "base": H + 40, "fg": True}
    layers["cast-shadows"] = paint_shadows(below, shadow_items,
                                           {n: (sprites[n], YSORT_PIVOTS[n]) for n in sprites})
    layers["rubble-collapse"] = rubble
    layers["props-low"] = props
    for n in sprites:
        layers[n] = sprites[n]
    layers["fg-occlusion"] = fg
    for k, v in fitems.items():
        items[k] = {"mask": v["mask"], "base": H + 40, "fg": True}      # always over the actor: never wrong-order
    despeckled = despeckle_ground(layers)
    walk, collars = walkable({k: v for k, v in items.items() if not v.get("fg")}, spr_alpha)
    for k, v in fitems.items():                                       # fg footprints on the ground plane
        collars[k] = box(*FG_FOOTPRINTS[k])
        walk &= ~collars[k]
    layers["guides"] = paint_guides(walk, collars)
    assert list(layers) == LAYERS, list(layers)
    return {"layers": layers, "items": items, "walk": walk, "collars": collars, "spr": spr, "spr_alpha": spr_alpha,
            "despeckled_ground_texels": despeckled, "terrain_patch_area": terrain_area, "voids": voids}


def bbox_of(mask):
    ys, xs = np.nonzero(mask)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


GROUND_LAYERS = ("plaza-ground", "terrain-patches", "ground-detail", "cast-shadows")


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
DT = (2026, 10, 16, 7, 17, 32)


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
    for n in ("capitol-dome", "breach-interiors", "capitol-west-front", "capitol-ruin", "olmsted-terrace",
              "breach-rubble"):
        cap |= layers[n] >= 0
    flat = composite_idx(layers, ART_LAYERS)
    vis = np.zeros((H, W), bool)
    for n in ("capitol-dome", "breach-interiors", "capitol-west-front", "capitol-ruin", "olmsted-terrace",
              "breach-rubble"):
        vis |= (layers[n] >= 0) & (flat == layers[n])
    dome = layers["capitol-dome"] >= 0
    dome_vis = dome & (flat == layers["capitol-dome"])
    # v06: the low camera puts the stylobate and the foot of the peristyle behind the central pavilion's attic (as
    # seen from the lawn). "Fully in frame" is therefore measured on the dome ABOVE the West Front roofline in each
    # column; the raw share (including the deliberately hidden foot) is still reported.
    fr = layers["capitol-west-front"] >= 0
    roof = np.where(fr.any(0), fr.argmax(0), H)
    above = dome & (YY < roof[None, :])
    above_vis = above & (flat == layers["capitol-dome"])
    x0, y0, x1, y1 = bbox_of(cap & (YY < 186))
    dx0, dy0, dx1, dy1 = bbox_of(dome)
    return {"capitol_bbox_rows": [y0, y1], "capitol_bbox_cols": [x0, x1],
            "capitol_height_share_of_frame": round((y1 - y0 + 1) / H, 3),
            "capitol_visible_texels": int(vis.sum()), "capitol_visible_share_of_frame": round(vis.mean(), 3),
            "dome_bbox": [dx0, dy0, dx1, dy1], "dome_visible_share": round(dome_vis.sum() / max(1, dome.sum()), 3),
            "dome_above_roofline_visible_share": round(above_vis.sum() / max(1, above.sum()), 3),
            "dome_hidden_behind_west_front_texels": int((dome & ~above).sum()),
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
    v["dome_and_statue_in_frame_above_west_front_roofline"] = bool(
        lm["statue_tip_row"] >= 2 and lm["dome_above_roofline_visible_share"] >= 0.97)
    # v06 scale target (v05 Codex audit: "landmark only about three heroine heights tall"; facade = heroine height)
    lm["capitol_to_heroine_height_ratio"] = round((lm["capitol_bbox_rows"][1] - lm["capitol_bbox_rows"][0] + 1) / 48, 2)
    fr = layers["capitol-west-front"] >= 0
    lm["west_front_visible_height_px_at_axis"] = int(T_RAIL - np.nonzero(fr[:, int(CAPX)])[0].min())
    v["capitol_ge_3p5_heroine_heights_and_facade_taller_than_heroine"] = bool(
        lm["capitol_to_heroine_height_ratio"] >= 3.5 and lm["west_front_visible_height_px_at_axis"] > 48)
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
    for k in ZOOMS:
        d[f"zoom_{k}"] = fname(k, "png")
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
    return {"candidate": RUN, "status": "UNAPPROVED, NONRUNTIME test-only candidate; not wired to any runtime scene",
            "canvas": [W, H], "grid_px": 8,
            "cells_legend": {"1": "every foot texel walkable", "p": "partly walkable", "0": "not walkable"},
            "cells_rows_top_to_bottom": cells,
            "collision_mask_png": names()["walkmask"], "foot_rule": "a foot texel is walkable iff the mask is opaque",
            "pins": {k: list(v) for k, v in PINS.items()},
            "exits": EXITS, "interactions": INTERACTIONS,
            "ysort_pivots": YSORT_PIVOTS,
            "runtime_draw_order_proposal": f"base (layers 1-{len(BASE_LAYERS)} merged) -> Y-sorted "
                                           f"{{{len(YSORT_LAYERS)} *-ysort layers, actor}} by pivot row (actor last "
                                           "on ties) -> fg-occlusion",
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
    vg, vout = v07_comparison(sc, rgba, flat, v07_reference())
    rep["v07_gates"], rep["v07_comparison"] = vg, vout
    with open(os.path.join(outdir, "checks.json"), "w") as f:
        json.dump(rep, f, indent=1, default=str)
    print(json.dumps({"verdicts": rep["verdicts"], "v07_gates": vg,
                      "v07_comparison": vout}, indent=1,
                     default=str))


def manifest(sc, rgba, files, rep):
    nm = names()
    return {
        "project": SLUG, "area": AREA, "run": RUN, "version": "v08",
        "status": "UNAPPROVED, NONRUNTIME test-only walkable candidate v08 (v07 composition, walkability and plaza "
                  "unchanged; ruin-state legibility pass on the Capitol backdrop: two specific collapses, gutted "
                  "interiors, rubble, vegetation, survey-versus-patrol cues). Not accepted art, not "
                  "runtime-integrated. Acceptance is root + creator review only; science scene art stays 0/11.",
        "art_approved": False, "runtime_integrated": False, "nonruntime": True, "counters_changed": False,
        "predecessor": {"base": {"run": V07_RUN, "tool": V07_TOOL, "tool_sha256_text_lf_v1": V07_TOOL_SHA_TEXT,
                                 "qa_note": V07_QA_REL, "read_only": True, "relation": "fork of this tool"},
                        "v07_base": {"run": V06_RUN, "tool": V06_TOOL, "read_only": True},
                        "v07_texture_technique_donor": {"run": V05T_RUN, "tool": V05T_TOOL, "read_only": True}},
        "v08_ruin_tables": {
            "breach_a_south": {"front_top_guide": BREACH_A_KEYS, "tooth": TOOTH_A, "corridor_guide": BREACH_A_CORR_KEYS,
                               "back_wall_runs": BACK_A, "party_walls": CROSSWALLS_A, "slabs": SLABS_A,
                               "cone_top_edge": CONE_A, "fragments": CONE_A_FRAGMENTS,
                               "story": {"survey_x": SURVEY_X, "survey_pennants": SURVEY_PENNANTS,
                                         "survey_prism": SURVEY_PRISM, "survey_tape_posts": SURVEY_TAPE,
                                         "patrol_relay": PATROL_RELAY, "scorch": SCORCH_A,
                                         "dormant_walker": DORMANT_WALKER, "patrol_walker_v07": WALKER_POS}},
            "breach_b_north": {"front_top_guide": BREACH_B_KEYS, "back_wall_runs": BACK_B, "tree": TREE_B,
                               "cone_top_edge": CONE_B},
            "roof_notches": ROOF_NOTCHES, "centre_vine": CENTRE_VINE_L, "back_wall_windows": BACK_HOLES,
            "grounds_trees_moved": {"broken-oak": [548, 588], "poplar": [492, 568]},
            "void_texels": {k: int(v.sum()) for k, v in sc["voids"].items()}},
        "v07_tables_inherited": {"facade_variants": facade_variant_summary(), "facade_runs": len(FACADE_RUNS),
                       "facade_patches": len(FACADE_PATCHES), "terrace_blocks": len(TERRACE_BLOCKS),
                       "plaza_forms": len(PLAZA_FORMS), "slab_states": len(SLAB_STATES), "seat_ivy": len(SEAT_IVY),
                       "terrain_patch_area_texels": sc["terrain_patch_area"]},
        "authoring_route": {
            "method": "deterministic Python tool with hand-written placement tables, authored and run by Claude "
                      "(Claude Code, claude.ai Max subscription, firstParty; no API key, no image model, no paid "
                      "fallback); writes a native pxo_version 7 .pxo and an .ora with named layers",
            "pixelorama_gui_paint_pass": False,
            "pixelorama_use": "headless CLI export round-trip only (check mode): .pxo and .ora flat + split-layer "
                              "exports compared texel-exact; an .ora rebuilt from Pixelorama's own split exports "
                              "re-exports to the exact flat",
            "disclosure": "no desktop/computer-use access to the Pixelorama GUI in this session; authored by code "
                          "(hand-written tables) plus a Pixelorama round-trip, NOT painted in the GUI",
            "references": "Architect of the Capitol building, dome, grounds, Olmsted Terrace and Reflecting Pool pages "
                          "(forms only, read as text facts in prior QA); no reference pixel is used",
            "audit_reference": "Codex visual judgment of v07 at 640x360 (dispatch brief, 2026-10-16): dome and "
                               "layout read, ground improved, building still overly intact and repetitive",
            "v06_audit_reference": V06_AUDIT_REL,
            "real_site_reference_audit": REAL_SITE_AUDIT_REL},
        "read_only_predecessors_lock": LOCK,
        "canvas": {"w": W, "h": H, "camera": "one 640x360 logical viewport (window 1280x720, integer 2x); top = "
                   "east (the Capitol), bottom = west (toward Union Square)",
                   "scale_reference": {"file": HEROINE_REL, "logical_height_px": int(sc["spr"].shape[0])},
                   "depth_model": {"backdrop_pinhole": {"F_px": F, "eye_m": EYE, "horizon_row": HZ,
                                                        "lawn_rise_m": LAWN_RISE},
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
    ps += [os.path.join(rp(OUT_REL), nm[k]) for k in nm if k.startswith(("cap", "zoom")) or k == "report"]
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
    ent = {}
    for rel in LOCK:
        present = os.path.exists(_fs(rp(rel)))
        if not present and rel in LOCK_OPTIONAL_IF_ABSENT:
            ent[rel] = {"expected": LOCK[rel], "actual": None, "present": False, "ok": True,
                        "status": "absent: untracked historical sibling, not an input; checked only when present"}
            continue
        got = lock_digest(rel) if present else None
        ent[rel] = {"expected": LOCK[rel], "actual": got, "present": present, "ok": got == LOCK[rel],
                    "status": "match" if got == LOCK[rel] else ("MISSING" if not present else "MISMATCH")}
    return {"entries": ent, "all_ok": all(e["ok"] for e in ent.values()),
            "optional_absent": sorted(r for r, e in ent.items() if not e["present"] and e["ok"])}


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
        changed = {k for k in set(before) | set(now) if before.get(k) != now.get(k) and k != ".running"
                   and not k.startswith("backups/")}
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
                                                      if before.get(k) != after.get(k) and k != ".running"
                                                      and not k.startswith("backups/")),
            "real_dir_gui_own_changes": sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k)
                                               and (k == ".running" or k.startswith("backups/"))),
            "real_running_marker_present_after": (".running" in after) if ".running" in before else None,
            "output_tail": tail[-5:]}


def pixelorama_gate(exe, files, rgba, flat):
    real_root = os.path.join(os.environ.get("APPDATA", ""), "pixelorama")
    rep = {"pixelorama": exe, "pixelorama_sha256": sha(read_bytes(exe)),
           "isolation": "APPDATA redirected to a fresh temp dir per run; real %APPDATA%\\pixelorama polled every "
                        "10 ms with a kill-switch", "steps": {}}
    tmp = tempfile.mkdtemp(prefix="wb-cw8gate-")
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
    pname = f"cw8-render-{tag}-{RUN_ID}"
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
    tmp = tempfile.mkdtemp(prefix="wb-cw8godot-")
    pnames = [f"cw8-texel-{RUN_ID}"]
    try:
        proj = os.path.join(tmp, "p1"); os.makedirs(proj)
        data = os.path.join(tmp, "d1"); os.makedirs(data)
        fake = os.path.join(tmp, "ad1"); os.makedirs(fake)
        with open(os.path.join(proj, "project.godot"), "w", newline="\n") as f:
            f.write(f'config_version=5\n\n[application]\nconfig/name="cw8-texel-{RUN_ID}"\n')
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


# ============================================================================ v07 gates against the v06 base
FACADE_BAND = (95, 171, 60, 640)      # rows y0..y1, columns x0..x1 of the West Front band (both halves, to the edge)


def v06_reference():
    """The stored v06 candidate files (read-only): flat image, the 22 .ora layers, the walk mask and the JSON."""
    ref = {"flat": decode(read_bytes(rp(V06_FLAT)))[2]}
    with zipfile.ZipFile(io.BytesIO(read_bytes(rp(V06_ORA)))) as z:
        ref["layers"] = {n[5:-4]: decode(z.read(n))[2] for n in z.namelist()
                         if n.startswith("data/") and n.endswith(".png")}
    ref["walkmask"] = decode(read_bytes(rp(V06_WALKMASK)))[2][..., 3] == 255
    ref["walk_json"] = json.loads(read_bytes(rp(V06_WALK_JSON)))
    return ref


def facade_band(a):
    y0, y1, x0, x1 = FACADE_BAND
    return a[y0:y1, x0:x1]


def repetition_in(flat, sub):
    """repetition_stats() on a sub-rectangle (same metric as the whole-frame one)."""
    return repetition_stats(flat_index(sub(flat)))


def plaza_grass_mask():
    m = plaza_masks()
    return m["ground"] & ~m["paving"]


def luma_mean(flat, mask):
    l = flat[..., :3].astype(np.float64) @ np.array([0.2126, 0.7152, 0.0722]) / 255.0
    return float(l[mask].mean())


def hierarchy_metrics(flat):
    """Value hierarchy readout: the walk axis, forecourt and stair (focal) against the frame-foot corners, and the
    landmark (dome + West Front above the terrace) against its sky."""
    m = plaza_masks()
    focal = (m["paving"] | box(STEPS[0], 203, STEPS[1], 222)) & (YY < 330)
    foot = box(0, 320, 150, H - 1) | box(W - 151, 320, W - 1, H - 1)
    sky = box(150, 0, 640, 100) & (YY < 60)
    land = box(330, 10, 412, 100)
    return {"focal_minus_frame_foot": round(luma_mean(flat, focal) - luma_mean(flat, foot), 4),
            "dome_box_minus_sky": round(luma_mean(flat, land) - luma_mean(flat, sky), 4)}


def v06_comparison(sc, rgba, flat, ref):
    """Gates and indicators against the stored v06 base."""
    out, g = {}, {}
    g["capitol_dome_layer_identical_to_v06"] = bool((rgba["capitol-dome"] == ref["layers"]["capitol-dome"]).all())
    a7 = rgba["capitol-west-front"][..., 3] == 255
    a6 = ref["layers"]["capitol-west-front"][..., 3] == 255
    g["west_front_silhouette_identical_to_v06"] = bool((a7 == a6).all())
    out["west_front_texels_repainted_vs_v06"] = int((rgba["capitol-west-front"] != ref["layers"]["capitol-west-front"])
                                                    .any(axis=2).sum())
    wj = ref["walk_json"]
    same = {"pins": {k: list(v) for k, v in PINS.items()} == wj["pins"],
            "exits": json.loads(json.dumps(EXITS)) == wj["exits"],
            "interactions": json.loads(json.dumps(INTERACTIONS)) == wj["interactions"],
            "ysort_pivots": YSORT_PIVOTS == wj["ysort_pivots"],
            "collision_probes": {k: list(v) for k, v in COLLISION_PROBES.items()} ==
            wj["collision_probes_must_be_blocked"],
            "route_waypoints": [list(PINS[p]) if isinstance(p, str) else list(p) for p in ROUTE] ==
            [list(p) for p in wj["heroine_route_waypoints"]]}
    out["walk_contract_fields_equal_v06"] = same
    g["walk_contract_identical_to_v06"] = all(same.values())
    out["walkmask_texels_differing_from_v06"] = int((sc["walk"] != ref["walkmask"]).sum())
    g["walkmask_identical_to_v06"] = out["walkmask_texels_differing_from_v06"] == 0
    r7 = repetition_in(flat, facade_band); r6 = repetition_in(ref["flat"], facade_band)
    out["facade_band_repetition_16px"] = {"v06": r6, "v07": r7, "band_rows_cols": list(FACADE_BAND)}
    g["facade_band_repetition_below_v06"] = r7["repeated_share"] < r6["repeated_share"]
    fv = facade_variant_summary()
    out["facade_variants"] = fv
    g["facade_openings_from_closed_variant_table"] = bool(fv["all_kinds_in_closed_set"] and
                                                         len(fv["window_kinds_used"]) >= 4 and
                                                         len(fv["attic_kinds_used"]) >= 2)
    grass = plaza_grass_mask()
    i7 = single_texel_islands(flat, grass); i6 = single_texel_islands(ref["flat"], grass)
    out["plaza_turf_single_texel_islands"] = {"v06": i6, "v07": i7}
    g["plaza_turf_calmer_than_v06"] = i7 < i6
    h7, h6 = hierarchy_metrics(flat), hierarchy_metrics(ref["flat"])
    out["value_hierarchy"] = {"v06": h6, "v07": h7}
    g["focal_vs_frame_foot_contrast_not_below_v06"] = h7["focal_minus_frame_foot"] >= h6["focal_minus_frame_foot"]
    g["dome_vs_sky_contrast_not_below_v06"] = h7["dome_box_minus_sky"] >= h6["dome_box_minus_sky"] - 1e-9
    out["whole_frame_repetition_16px"] = {"v06": repetition_stats(flat_index(ref["flat"])),
                                          "v07": repetition_stats(flat_index(flat))}
    out["single_texel_colour_islands"] = {
        "v06": {"plane_rows_200_359": single_texel_islands(ref["flat"], YY >= 200),
                "backdrop_rows_0_199": single_texel_islands(ref["flat"], YY < 200)},
        "v07": {"plane_rows_200_359": single_texel_islands(flat, YY >= 200),
                "backdrop_rows_0_199": single_texel_islands(flat, YY < 200)}}
    out["texels_changed_vs_v06_flat"] = int((flat != ref["flat"]).any(axis=2).sum())
    out["texels_changed_share"] = round(out["texels_changed_vs_v06_flat"] / float(W * H), 4)
    per = {}
    for n in ART_LAYERS:
        if n in ref["layers"]:
            per[n] = int((rgba[n] != ref["layers"][n]).any(axis=2).sum())
        else:
            per[n] = "new in v07"
    out["texels_changed_per_layer_vs_v06"] = per
    return g, out


# ============================================================================ v08 gates against the v07 base
PAVILION_COLS = (306, 437)            # central pavilion under the dome: untouched, so the outline stays recognisable
UNCHANGED_LAYERS_VS_V07 = ["sky", "clouds", "capitol-dome", "west-lawn", "patrol-walker", "lawn-edge-planting",
                           "seat-wall-steps", "plaza-ground", "terrain-patches", "ground-detail", "cast-shadows",
                           "rubble-collapse", "props-low", "survey-mast-ysort", "survey-tripod-ysort",
                           "beacon-ysort", "elm-ysort", "fg-occlusion"]
VEG_NAMES = ("vg0", "vg1", "vg2", "vg3", "vg4", "mg0", "mg1", "mg2", "mg3", "mg4", "lw0", "lw1", "lw2", "lw3",
             "lw4", "yg0", "yg1", "yg2", "yg3", "cn0", "cn1", "cn2", "cn3", "cn4", "f0", "f1", "f2", "f3", "f4")
BACKDROP_BAND = (95, 186, 60, 640)    # rows y0..y1, cols x0..x1: West Front + terrace (the "building" read)


def v07_reference():
    """The stored v07 candidate files (read-only): flat image, the 24 .ora layers, the walk mask and the JSON."""
    ref = {"flat": decode(read_bytes(rp(V07_FLAT)))[2]}
    with zipfile.ZipFile(io.BytesIO(read_bytes(rp(V07_ORA)))) as z:
        ref["layers"] = {n[5:-4]: decode(z.read(n))[2] for n in z.namelist()
                         if n.startswith("data/") and n.endswith(".png")}
    ref["walkmask"] = decode(read_bytes(rp(V07_WALKMASK)))[2][..., 3] == 255
    ref["walk_json"] = json.loads(read_bytes(rp(V07_WALK_JSON)))
    return ref


def _cut_only(new_rgba, old_rgba, allowed):
    """A layer may only lose texels inside `allowed`; every texel it keeps must equal the old one."""
    a_new, a_old = new_rgba[..., 3] == 255, old_rgba[..., 3] == 255
    kept_equal = bool((new_rgba[a_new] == old_rgba[a_new]).all())
    no_new = not bool((a_new & ~a_old).any())
    removed = a_old & ~a_new
    return {"kept_texels_equal": kept_equal, "no_texel_added": no_new, "removed": int(removed.sum()),
            "removed_outside_allowed": int((removed & ~allowed).sum()),
            "ok": kept_equal and no_new and not bool((removed & ~allowed).any())}


def _visible_through(rgba_layers, order, after, mask):
    """Texels of `mask` where every layer stacked above `after` is transparent (seen straight through)."""
    clear = np.ones((H, W), bool)
    for n in order[order.index(after) + 1:]:
        if n in rgba_layers:
            clear &= rgba_layers[n][..., 3] != 255
    return clear & mask


def _roof_rows(front_rgba):
    a = front_rgba[..., 3] == 255
    return np.where(a.any(0), a.argmax(0), H)


def _longest_equal_run(r_new, r_old, x0, x1):
    """Longest run of columns whose roofline is the designed (v07) one; v07's House bite counts as broken."""
    best = cur = 0
    for x in range(x0, x1 + 1):
        cur = cur + 1 if (r_new[x] == r_old[x] and r_old[x] < H and x < HOUSE_COLLAPSE[0][0]) else 0
        best = max(best, cur)
    return best


def _mirror_share(flat):
    """Share of texels in the West Front + terrace band (left half, x 104..371: the mirror must be in frame) equal to
    their mirror (x' = 743 - x)."""
    y0, y1 = BACKDROP_BAND[0], BACKDROP_BAND[1]
    xs = np.arange(743 - (W - 1), 372)
    a = flat[y0:y1, xs, :3]; b = flat[y0:y1, 743 - xs, :3]
    return round(float((a == b).all(axis=2).mean()), 4)


def _band_mask():
    y0, y1, x0, x1 = BACKDROP_BAND
    return box(x0, y0, x1 - 1, y1 - 1)


def _share_of_palette(flat, mask, names_):
    keys = {tuple(RGB[I[n]].tolist()) for n in names_}
    pix = flat[mask][:, :3]
    hit = np.array([tuple(p) in keys for p in pix.tolist()])
    return round(float(hit.mean()), 4)


def _luma(flat):
    return flat[..., :3].astype(np.float64) @ np.array([0.2126, 0.7152, 0.0722]) / 255.0


def heroine_contrast(flat_base, spr, foot):
    """Mean |luma(heroine) - luma(backdrop behind her)| over her opaque texels (readability of the 48-px sprite)."""
    sh, sw = spr.shape[:2]
    x0, y0 = foot[0] - sw // 2, foot[1] - sh + 1
    a = spr[..., 3] == 255
    ls = _luma(spr)
    lb = _luma(flat_base)
    vals = []
    for j in range(sh):
        for i in range(sw):
            x, y = x0 + i, y0 + j
            if a[j, i] and 0 <= x < W and 0 <= y < H:
                vals.append(abs(ls[j, i] - lb[y, x]))
    return round(float(np.mean(vals)), 4)


def _notch_composition(rgba, notch):
    """What the viewer sees where the wall was: open sky/clouds, gutted shell stone (back walls, slabs, party walls),
    the trees grown inside the shell, or something nearer (lip, ivy, relay, cone, grounds trees, walker)."""
    top = np.full((H, W), -1, np.int16)
    for i, n in enumerate(ART_LAYERS):
        top[rgba[n][..., 3] == 255] = i
    bi = ART_LAYERS.index("breach-interiors")
    leaf = {tuple(RGB[I[n]].tolist()) for n in VEG_NAMES + ("b0", "b1", "b2", "b3")}
    tot = float(notch.sum())
    rgb = rgba["breach-interiors"][..., :3]
    is_leaf = np.array([[tuple(c) in leaf for c in row] for row in rgb.tolist()])
    sky = notch & (top < bi)
    shell = notch & (top == bi) & ~is_leaf
    tree = notch & (top == bi) & is_leaf
    near = notch & (top > bi)
    return {k: round(float(v.sum()) / tot, 3) for k, v in (("open_sky_or_clouds", sky), ("gutted_shell_stone", shell),
                                                         ("trees_grown_inside", tree),
                                                         ("nearer_layers_lip_ivy_cone_trees", near))}


def v07_comparison(sc, rgba, flat, ref):
    """Gates and indicators against the stored v07 base: what v08 was allowed to change (backdrop ruin state) and
    what it must not (dome, pavilion, walk contract, walk mask, every walkable-plane layer)."""
    out, g = {}, {}
    voids = sc["voids"]
    allv = np.zeros((H, W), bool)
    for v in voids.values():
        allv |= v
    g["capitol_dome_layer_identical_to_v07"] = bool((rgba["capitol-dome"] == ref["layers"]["capitol-dome"]).all())
    wf = _cut_only(rgba["capitol-west-front"], ref["layers"]["capitol-west-front"], allv)
    fw = _cut_only(rgba["facade-weathering"], ref["layers"]["facade-weathering"], allv)
    out["west_front_cut_vs_v07"], out["facade_weathering_cut_vs_v07"] = wf, fw
    g["west_front_only_cut_inside_declared_voids"] = wf["ok"]
    g["facade_weathering_only_cut_inside_declared_voids"] = fw["ok"]
    x0, x1 = PAVILION_COLS
    same = (flat[:200, x0:x1 + 1] == ref["flat"][:200, x0:x1 + 1]).all()
    g["central_pavilion_and_dome_columns_identical_to_v07"] = bool(same)
    unchanged = {n: bool((rgba[n] == ref["layers"][n]).all()) for n in UNCHANGED_LAYERS_VS_V07}
    out["layers_identical_to_v07"] = unchanged
    g["sky_dome_lawn_walker_and_every_walkable_plane_layer_identical_to_v07"] = all(unchanged.values())
    wj = ref["walk_json"]
    same_c = {"pins": {k: list(v) for k, v in PINS.items()} == wj["pins"],
              "exits": json.loads(json.dumps(EXITS)) == wj["exits"],
              "interactions": json.loads(json.dumps(INTERACTIONS)) == wj["interactions"],
              "ysort_pivots": YSORT_PIVOTS == wj["ysort_pivots"],
              "collision_probes": {k: list(v) for k, v in COLLISION_PROBES.items()} ==
              wj["collision_probes_must_be_blocked"],
              "route_waypoints": [list(PINS[p]) if isinstance(p, str) else list(p) for p in ROUTE] ==
              [list(p) for p in wj["heroine_route_waypoints"]],
              "cells_rows_top_to_bottom": walkability_json(sc)["cells_rows_top_to_bottom"] ==
              wj["cells_rows_top_to_bottom"],
              "collars_blocked_texels": walkability_json(sc)["collars_blocked_texels"] == wj["collars_blocked_texels"]}
    out["walk_contract_fields_equal_v07"] = same_c
    g["walk_contract_identical_to_v07"] = all(same_c.values())
    out["walkmask_texels_differing_from_v07"] = int((sc["walk"] != ref["walkmask"]).sum())
    g["walkmask_identical_to_v07"] = out["walkmask_texels_differing_from_v07"] == 0
    # --- ruin legibility at gameplay size (1x)
    intact = paint_west_front() >= 0                                   # the West Front before any 2537 bite
    v07_order = [n for n in LAYERS if n not in ("breach-interiors", "breach-rubble")]
    bre = {}
    for k in ("breach_a", "breach_b"):
        notch = voids[k] & intact                                     # wall that is really gone
        vis = _visible_through(rgba, LAYERS, "breach-interiors", notch)
        cols = np.nonzero(notch.any(0))[0]
        drop = int((_roof_rows(rgba["capitol-west-front"]) - _roof_rows(ref["layers"]["capitol-west-front"]))
                   [cols].max())
        bre[k] = {"removed_wall_texels": int(notch.sum()), "visible_share_at_1x": round(vis.sum() / notch.sum(), 3),
                  "width_px": int(cols.max() - cols.min() + 1), "max_roofline_drop_rows": drop,
                  "what_shows_in_the_removed_wall_area": _notch_composition(rgba, notch)}
    hv = voids["house_v07"] & intact
    v07_house_vis = _visible_through(ref["layers"], v07_order, "capitol-dome", hv)
    v08_house_vis = _visible_through(rgba, LAYERS, "breach-interiors", hv)
    bre["house_v07_bite"] = {"removed_wall_texels": int(hv.sum()),
                             "visible_share_at_1x_in_v07": round(v07_house_vis.sum() / hv.sum(), 3),
                             "visible_share_at_1x_in_v08": round(v08_house_vis.sum() / hv.sum(), 3)}
    out["breaches"] = bre
    g["two_specific_breaches_readable_at_640x360"] = all(
        bre[k]["visible_share_at_1x"] >= 0.6 and bre[k]["width_px"] >= 30 and bre[k]["max_roofline_drop_rows"] >= 20
        for k in ("breach_a", "breach_b"))
    r8, r7 = _roof_rows(rgba["capitol-west-front"]), _roof_rows(ref["layers"]["capitol-west-front"])
    run7 = _longest_equal_run(r7, r7, 60, 639)
    run8 = _longest_equal_run(r8, r7, 60, 639)
    out["roofline_longest_unbroken_run_px"] = {"v07": run7, "v08": run8}
    out["roofline_columns_lowered"] = int(((r8 - r7) > 0)[60:].sum())
    g["roofline_no_longer_one_continuous_run"] = run8 <= run7 // 2
    m7, m8 = _mirror_share(ref["flat"]), _mirror_share(flat)
    out["backdrop_band_mirror_equal_share"] = {"v07": m7, "v08": m8, "band_rows": list(BACKDROP_BAND[:2]),
                                               "cols": "104..371 vs 743-x"}
    g["backdrop_less_mirror_symmetric_than_v07"] = m8 <= m7 - 0.02
    sub = lambda a: a[BACKDROP_BAND[0]:BACKDROP_BAND[1], BACKDROP_BAND[2]:BACKDROP_BAND[3]]
    rp8, rp7 = repetition_in(flat, sub), repetition_in(ref["flat"], sub)
    out["backdrop_band_repetition_16px"] = {"v07": rp7, "v08": rp8}
    g["backdrop_band_repetition_not_above_v07"] = rp8["repeated_share"] <= rp7["repeated_share"]
    fb8, fb7 = repetition_in(flat, facade_band), repetition_in(ref["flat"], facade_band)
    out["facade_band_repetition_16px_v07_metric"] = {"v07": fb7, "v08": fb8, "band_rows_cols": list(FACADE_BAND)}
    bm = _band_mask()
    out["backdrop_band_vegetation_share"] = {"v07": _share_of_palette(ref["flat"], bm, VEG_NAMES),
                                             "v08": _share_of_palette(flat, bm, VEG_NAMES)}
    i7, i8 = single_texel_islands(ref["flat"], YY < 200), single_texel_islands(flat, YY < 200)
    out["backdrop_single_texel_islands"] = {"v07": i7, "v08": i8}
    g["no_added_pixel_noise_in_backdrop"] = i8 <= i7 * 1.10
    # --- value hierarchy
    h8, h7 = hierarchy_metrics(flat), hierarchy_metrics(ref["flat"])
    # the dome (its visible texels) must stay the brightest landmark mass; breach A is the new dark accent
    l8, l7 = _luma(flat), _luma(ref["flat"])
    dome_vis = _visible_through(rgba, LAYERS, "capitol-dome", rgba["capitol-dome"][..., 3] == 255)
    region_a = box(466, 104, 562, 185)
    for h, l in ((h8, l8), (h7, l7)):
        h["dome_visible_luma"] = round(float(l[dome_vis].mean()), 4)
        h["breach_a_region_luma"] = round(float(l[region_a].mean()), 4)
        h["breach_a_region_luma_std"] = round(float(l[region_a].std()), 4)
        h["dome_minus_breach_a_region"] = round(h["dome_visible_luma"] - h["breach_a_region_luma"], 4)
    out["value_hierarchy"] = {"v07": h7, "v08": h8}
    g["dome_vs_sky_contrast_not_below_v07"] = h8["dome_box_minus_sky"] >= h7["dome_box_minus_sky"] - 1e-9
    g["focal_vs_frame_foot_contrast_not_below_v07"] = h8["focal_minus_frame_foot"] >= h7["focal_minus_frame_foot"] - 1e-9
    g["dome_still_brighter_than_new_ruin_accent"] = h8["dome_minus_breach_a_region"] > 0.10
    spr = sc["spr"]
    base8 = composite_rgba(rgba, BASE_LAYERS)
    ref_base = composite_rgba({n: ref["layers"][n] for n in ref["layers"]},
                              [n for n in v07_order if n in BASE_LAYERS])
    hc = {k: {"v07": heroine_contrast(ref_base, spr, PINS[p]), "v08": heroine_contrast(base8, spr, PINS[p])}
          for k, p in CAPTURES.items()}
    out["heroine_vs_backdrop_luma_contrast_at_capture_pins"] = hc
    g["heroine_contrast_not_below_v07_at_every_capture_pin"] = all(v["v08"] >= v["v07"] - 1e-9 for v in hc.values())
    out["texels_changed_vs_v07_flat"] = int((flat != ref["flat"]).any(axis=2).sum())
    out["texels_changed_share"] = round(out["texels_changed_vs_v07_flat"] / float(W * H), 4)
    per = {}
    for n in ART_LAYERS:
        per[n] = int((rgba[n] != ref["layers"][n]).any(axis=2).sum()) if n in ref["layers"] else "new in v08"
    out["texels_changed_per_layer_vs_v07"] = per
    out["void_texels"] = {k: int(v.sum()) for k, v in voids.items()}
    return g, out

# ============================================================================ Godot physics collision probe (v05t)
GODOT_COLLISION_SCRIPT = r'''extends SceneTree
# Test-only, nonruntime: build a StaticBody2D from the exported blocked mask (one RectangleShape2D per merged
# rectangle of blocked texels, exact to the texel), then ask Godot's physics for (a) shape queries with an 11x3 px
# foot box at probe feet and (b) CharacterBody2D sweeps with move_and_collide (port of the v05t probe).
var dir: String
var frames := 0
var body: CharacterBody2D
func _initialize():
	dir = OS.get_cmdline_user_args()[0]
	var rects = JSON.parse_string(FileAccess.get_file_as_string(dir + "/rects.json"))
	var sb = StaticBody2D.new()
	root.add_child(sb)
	for r in rects:
		var cs = CollisionShape2D.new()
		var sh = RectangleShape2D.new()
		sh.size = Vector2(float(r[2]), float(r[3]))
		cs.shape = sh
		cs.position = Vector2(float(r[0]) + float(r[2]) / 2.0, float(r[1]) + float(r[3]) / 2.0)
		sb.add_child(cs)
	body = CharacterBody2D.new()
	var bcs = CollisionShape2D.new()
	var bsh = RectangleShape2D.new()
	bsh.size = Vector2(10.6, 2.6)
	bcs.shape = bsh
	body.add_child(bcs)
	root.add_child(body)
func _physics_process(_delta):
	frames += 1
	if frames < 4:
		return false
	var cases = JSON.parse_string(FileAccess.get_file_as_string(dir + "/probes.json"))
	var space = root.get_world_2d().direct_space_state
	var q = PhysicsShapeQueryParameters2D.new()
	var foot = RectangleShape2D.new()
	foot.size = Vector2(10.6, 2.6)
	q.shape = foot
	q.exclude = [body.get_rid()]
	var out = {"probes": {}, "sweeps": {}}
	for p in cases["probes"]:
		q.transform = Transform2D(0.0, Vector2(float(p[0]) + 0.5, float(p[1]) + 0.5))
		out["probes"][str(int(p[0])) + "," + str(int(p[1]))] = space.intersect_shape(q, 1).size() > 0
	for s in cases["sweeps"]:
		body.global_position = Vector2(float(s[0]) + 0.5, float(s[1]) + 0.5)
		body.force_update_transform()
		var col = body.move_and_collide(Vector2(float(s[2]), float(s[3])), true)
		var res = {"hit": col != null}
		if col != null:
			res["travel"] = [col.get_travel().x, col.get_travel().y]
		out["sweeps"][s[4]] = res
	var f = FileAccess.open(dir + "/collision_report.json", FileAccess.WRITE)
	f.store_string(JSON.stringify(out))
	f.close()
	print("GODOT_COLLISION_DONE")
	return true
'''


def blocked_rects(blocked):
    """Exact cover of the blocked mask by rectangles: horizontal runs per row, merged downward while identical."""
    rects, open_ = [], {}
    for y in range(H + 1):
        runs = set()
        if y < H:
            ch = np.nonzero(np.diff(np.r_[0, blocked[y].astype(np.int8), 0]))[0]
            runs = {(int(a), int(b)) for a, b in zip(ch[::2], ch[1::2])}
        nxt = {}
        for run, y0 in open_.items():
            if run in runs:
                nxt[run] = y0
            else:
                rects.append((run[0], y0, run[1] - run[0], y - y0))
        for run in runs:
            if run not in nxt:
                nxt[run] = y
        open_ = nxt
    return rects


def collision_cases(walk):
    blocked = ~walk
    pb = np.pad(blocked, ((1, 1), (5, 5)))
    foot_hit = np.zeros((H, W), bool)                      # python expectation for the 11x3 foot box (no wrap)
    for dy in (-1, 0, 1):
        for dx in range(-5, 6):
            foot_hit |= pb[1 + dy:1 + dy + H, 5 + dx:5 + dx + W]
    probes = [[int(x), int(min(H - 2, y))] for k, (x, y) in PINS.items() if 5 <= x < W - 5]
    rpts = route_points(walk)
    probes += [list(p) for p in rpts[::40] if 5 <= p[0] < W - 5]
    probes += [list(v) for v in COLLISION_PROBES.values()]
    expect = {f"{x},{y}": bool(foot_hit[y, x]) for x, y in probes}
    x0, y0 = PINS["spawn_south"]
    y = y0
    while y > 0 and not foot_hit[y - 1, x0]:
        y -= 1
    sweeps = [[x0, y0, 0, -(y0 - 150), "axis_north_from_spawn"], [x0, y0, 0, -(y0 - y - 3), "axis_north_short"]]
    xw, yw = PINS["axis_mid"]
    xe = xw
    while xe < W - 1 and not foot_hit[yw, xe + 1]:
        xe += 1
    sweeps.append([xw, yw, (W - 1) - xw, 0, "east_from_axis_mid"])
    sweep_expect = {"axis_north_from_spawn": {"hit": True, "travel": [0, -(y0 - y)]},
                    "axis_north_short": {"hit": False},
                    "east_from_axis_mid": {"hit": xe < W - 1, "travel": [xe - xw, 0]}}
    return blocked_rects(blocked), probes, expect, sweeps, sweep_expect


def godot_collision_gate(godot, walk):
    tmp = tempfile.mkdtemp(prefix="wb-cw8coll-")
    proj_name = f"cw8-collision-{RUN_ID}"
    rep = {"godot": GODOT_REL, "godot_sha256": sha(read_bytes(godot))}
    try:
        proj = os.path.join(tmp, "proj"); os.makedirs(proj)
        data = os.path.join(tmp, "data"); os.makedirs(data)
        fake = os.path.join(tmp, "appdata"); os.makedirs(fake)
        with open(os.path.join(proj, "project.godot"), "w", newline="\n") as f:
            f.write(f'config_version=5\n\n[application]\nconfig/name="{proj_name}"\n')
        with open(os.path.join(proj, "collide.gd"), "w", newline="\n") as f:
            f.write(GODOT_COLLISION_SCRIPT)
        rects, probes, expect, sweeps, sweep_expect = collision_cases(walk)
        with open(os.path.join(data, "rects.json"), "w") as f:
            json.dump(rects, f)
        with open(os.path.join(data, "probes.json"), "w") as f:
            json.dump({"probes": probes, "sweeps": sweeps}, f)
        env = dict(os.environ); env["APPDATA"] = fake
        p = subprocess.run([godot, "--headless", "--path", proj, "--script", "collide.gd", "--", data],
                           capture_output=True, text=True, timeout=600, env=env, encoding="utf-8", errors="replace")
        rep["exit_code"] = p.returncode
        rep["printed_done"] = "GODOT_COLLISION_DONE" in p.stdout
        gr = json.load(open(os.path.join(data, "collision_report.json")))
        mism = [k for k, v in expect.items() if gr["probes"].get(k) != v]
        rep.update({"rectangles": len(rects), "probes": len(expect), "probes_expected_blocked": sum(expect.values()),
                    "probe_mismatches": mism[:20]})
        sw = {}
        for k, e in sweep_expect.items():
            gg = gr["sweeps"].get(k, {})
            ok = gg.get("hit") == e["hit"]
            if e["hit"] and ok:
                ok = all(abs(gg["travel"][i] - e["travel"][i]) <= 1.0 for i in (0, 1))
            sw[k] = {"godot": gg, "python": e, "ok": ok}
        rep["sweeps"] = sw
        rep["verdicts"] = {"godot_physics_probes_match_mask": rep["exit_code"] == 0 and rep["printed_done"]
                           and not mism,
                           "godot_physics_sweeps_match_mask": all(v["ok"] for v in sw.values()),
                           "godot_physics_wrote_nothing_outside_temp": not os.path.isdir(os.path.join(
                               os.environ.get("APPDATA", ""), "Godot", "app_userdata", proj_name))}
    finally:
        shutil.rmtree(_fs(tmp), ignore_errors=True)
    return rep


ZOOMS = {"zoom3x-west-front-north-half": (60, 95, 372, 190, 3), "zoom3x-west-front-south-half": (372, 95, 640, 190, 3),
         "zoom4x-breach-a-south": (440, 92, 600, 192, 4), "zoom4x-breach-b-north": (40, 85, 200, 192, 4)}


def zoom_png(flat, spec):
    x0, y0, x1, y1, k = spec
    a = flat[y0:y1, x0:x1]
    return png_bytes(np.repeat(np.repeat(a, k, 0), k, 1))


# ============================================================================ check
def check(exe, write_report, use_pixelorama, godot=None):
    sc, rgba, flat, files = build_all()
    nm = names()
    cand = rp(CAND_REL)
    files["walk"] = (json.dumps(walkability_json(sc), indent=1) + "\n").encode()
    for k in ("pxo", "ora", "flat", "gpl", "walkmask", "walk"):
        b = read_bytes(os.path.join(cand, nm[k]))
        if k in ("gpl", "walk"):              # text: a Windows clone with core.autocrlf=true checks it out as CRLF
            b, want = b.replace(b"\r\n", b"\n"), files[k].replace(b"\r\n", b"\n")
        else:
            want = files[k]
        if b != want:
            raise SystemExit(f"{nm[k]} on disk differs from a fresh rebuild")
    st = static_checks(sc, rgba, flat)
    rep = {"run": RUN, "gates": dict(st["verdicts"]), "static": st}
    gates = rep["gates"]
    with zipfile.ZipFile(io.BytesIO(files["pxo"])) as z:
        dj = json.loads(z.read("data.json"))
    gates["pxo_layer_stack_is_the_named_layers"] = [l["name"] for l in dj["layers"]] == LAYERS and \
        [l["visible"] for l in dj["layers"]] == [n != "guides" for n in LAYERS]
    gates["build_deterministic"] = build_all()[3] == {k: v for k, v in files.items() if k != "walk"}
    lk = lock_check()
    rep["lock"] = lk
    gates["v07_v06_v05t_untouched"] = lk["all_ok"]
    gates["fork_point_is_the_pinned_v07_tool"] = lock_digest(V07_TOOL) == "t:" + V07_TOOL_SHA_TEXT
    vg, vout = v07_comparison(sc, rgba, flat, v07_reference())
    gates.update(vg)
    rep["v07_comparison"] = vout
    gates["max_path_under_260"] = longest_path() < 260
    caps = {}
    if use_pixelorama:
        rep["pixelorama"] = pixelorama_gate(exe, files, rgba, flat)
        gates.update(rep["pixelorama"]["verdicts"])
    if godot:
        rep["godot"], caps = godot_gates(godot, files, rgba, sc)
        gates.update(rep["godot"]["verdicts"])
        rep["godot_physics"] = godot_collision_gate(godot, sc["walk"])
        gates.update(rep["godot_physics"]["verdicts"])
    for k, spec in ZOOMS.items():
        caps[f"zoom_{k}"] = zoom_png(flat, spec)
    rep["result"] = "PASS" if all(gates.values()) else "FAIL"
    rep["evidence_sha256_bytes"] = {nm[k]: sha(v) for k, v in sorted(caps.items())}
    rep["note"] = ("Technical gates only. Passing them does not make the art accepted; acceptance is creator review. "
                   "Godot captures are real windowed renders; zoom files are nearest-neighbour crops of the Python "
                   "flat image (evidence only).")
    text = json.dumps(rep, indent=2, default=str) + "\n"
    print(json.dumps({"result": rep["result"], "gates_passed": f"{sum(gates.values())}/{len(gates)}",
                      "failed": [k for k, v in gates.items() if not v],
                      "lock_optional_absent": lk["optional_absent"]}, indent=1))
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
    ap.add_argument("--godot", default=None, help="Godot 4.7.2 console exe (default: the gitignored "
                                                    "work/tooling copy, absent from a clean clone)")
    a = ap.parse_args()
    if a.mode == "preview":
        if not a.dir or os.path.abspath(a.dir).startswith(REPO):
            raise SystemExit("preview needs a directory outside the repo")
        preview(a.dir)
    elif a.mode == "build":
        build()
    else:
        sys.exit(check(a.pixelorama, a.write_report, not a.no_pixelorama,
                       None if a.no_godot else (a.godot or rp(GODOT_REL))))


if __name__ == "__main__":
    main()
