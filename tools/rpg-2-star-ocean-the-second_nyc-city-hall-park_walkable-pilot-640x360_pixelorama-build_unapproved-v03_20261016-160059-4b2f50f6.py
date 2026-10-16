"""UNAPPROVED, NONRUNTIME pilot v03: NYC City Hall Park (2537 science hub), ONE 640x360 walkable camera composition.

A NEW, separate candidate forked from the pilot v02 tool (run nyc-chp-v02_20261016-055120-59848a60, whose files are
left untouched) after the Codex v02 visual audit docs/qa/...nyc-city-hall-park_walkable-v02-codex-visual-audit_
unapproved-v01_20261016-064422-216b6bc3.md. Deterministic Python tool authored and run by Claude (Claude Code, Opus
5.5, claude.ai Max subscription, firstParty; no API key, no image model, no paid fallback).

v03 changes against the v02 audit (defect -> response; each change is commented "v03" where it is made):
  * facade: per-window state table (blinds, curtains, lit, sky reflections), weathering streaks, cornice shadow band,
    deep window reveals, roof urns, Justice figure on the cupola; the whole building is hazed one aerial-perspective
    step (own hazed-marble ramp) so it no longer shares values with the hero-scale gate piers -> reads distant;
    door-scaled visitors on the stair give the facade a human yardstick.
  * skyline: a sky band and broken rooflines; three hazed depth planes in warm brick, limestone, terracotta and glass
    (Woolworth-like terracotta piers at the left, Municipal-Building-like limestone colonnade at the right, water
    tanks, one slim 2537 garden tower in the far plane with a faint teal seam) instead of grey blocks.
  * lawns / trees: shrub borders on lawn edges, a picnic, a bench reader and a gardener occupy the lawns; flower beds
    get stone edging and grouped bloom drifts; hero crowns get hand-cut gaps that show limbs, edge spill and
    asymmetric lobes; back-grove crowns are hazed and mirrored per instance.
  * fountain: the tall 2-px jet is gone; a solid two-tier centrepiece (pedestal, wide upper bowl with falling sheets,
    a low foam crown) hides the lower body of anyone directly behind it instead of slicing through her.
  * behind-tree: the SE plane forks low (no lollipop) and the capture foot is moved so the trunk covers one side of
    the heroine while her far foot and contact shadow stay visible.

What it writes: one 640x360 logical-pixel scene (exactly one gameplay camera: game/project.godot viewport 640x360,
window 1280x720, integer 2x) as a 24-layer editable stack -- a native Pixelorama .pxo (pxo_version 7) and an .ora --
plus a palette (.gpl), the actor contact-shadow sprite, a walk mask PNG, a walkability JSON and a manifest. `check`
adds the Pixelorama 1.2.3 headless export round-trip and two Godot 4.7.2 gates (headless texel gate along a heroine
route, and real windowed renders at 1280x720 and at native 640x360). Nothing is wired into the game runtime;
science scene art stays 0/11.

AUTHORING ROUTE (disclosed). NOT a Pixelorama GUI paint pass (no desktop/computer-use access to the GUI in this
session). Landmarks, trees (one hand-written lobe list per tree), wear marks, stains, cracks, leaf litter, worn turf,
beds, props, lawn occupants and window states are explicit table entries below; textures are hand-drawn motifs (leaf clumps, grass tufts) placed on
fixed lattices with hand-written offset tables. No value-noise thresholds and no hashed pixel scatter are used for
texture; the only hash use left is choosing a granite slab's tone from a short hand-written tone table.

Reference use. City Hall follows the published description of the building (NYC DCAS City Hall page cited in the v01
audit; the Justice figure on the cupola is part of that published description of the tower): a central pavilion, two projecting wings, a columned entrance portico and a domed tower. Bay counts, column
counts and proportions are an interpretation at backdrop scale, NOT measured from LPC elevations, and no reference
pixel is copied. Lower Manhattan context beyond Chambers Street (Woolworth-like terracotta piers on Broadway, a
Municipal-Building-like limestone colonnade, the Tweed Courthouse roof, brick and limestone blocks with water tanks,
one invented slim 2537 garden tower) is generic massing in hazed colours, not traced. The v03 visual-direction
reference image (outputs/...visual-direction-reference_nonruntime-v03_20261016-124945-33aa88e9.png, Codex, generated,
UNAPPROVED) was looked at for density ideas only; none of its pixels or colours are sampled.

v02 composition (kept in v03):

  * dollhouse join: the walk now ends at hero-scale granite gate piers with lanterns and hero-scale railings; the
    forecourt beyond them recedes (paving courses thin to 2 rows, stair risers graded 4 -> 2 rows); lawns flow from
    the park up to the building with tufts that shrink with distance; trees recede in three sizes.
  * horizontal bands: no full-width grove, hedge or picket belt; skyline, tree clumps and lawns break irregularly.
  * City Hall: projecting wings (+9 rows), central pavilion (+3), projecting entrance portico (+7) with a stair;
    wing shadows fall on the recessed links (sun from the south-west); invented green banners removed.
  * foliage: four species with their own clump size, ramp and crown lobes (London plane, American elm, honey
    locust, flowering dogwood); leaning / forked trunks; plane-tree bark mottling.
  * paving: wear layer (cracks, stains, patched slabs, polished lane, moss joints, sunken pavers, worn turf, litter);
    the continuous teal centre seam is replaced by two wayfinding medallions; lamp shadows are short stubby shapes.
  * fountain: low inner tier and arching jets in the base layer; only a slim column, bowl and jet are Y-sorted; a
    readability gate blocks feet where an occluder would hide only the feet ("standing on" read).
  * actor contact shadow: a two-step alpha ellipse (sun south-west, nudged north-east), drawn under the actor.

Modes
  preview <dir>   render layers, flat, runtime stills, 2x views and guides into <dir> (outside the repo)
  build           write candidate files (never overwrites a different file)
  check           static gates + Pixelorama headless round-trip (APPDATA redirected to temp; --no-pixelorama) +
                  Godot gates in throwaway temp projects (--no-godot); --write-report writes the JSON report and the
                  three 1280x720 and three 640x360 Godot render captures into outputs/<RUN>/.
Run: python -I -B <this file> preview <tempdir> | build | check [--write-report] [--no-pixelorama] [--no-godot]
"""
import argparse, hashlib, io, json, math, os, shutil, subprocess, sys, tempfile, time, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
AREA = "nyc-city-hall-park"
VER = "unapproved-v03"
STAMP = "20261016-160059"
RUN_ID = "4b2f50f6"
RUN = f"nyc-chp-v03_{STAMP}-{RUN_ID}"       # short run dir: keeps candidate paths well under MAX_PATH (260)
CAND_REL = f"game/assets/environments/candidates/{RUN}"
OUT_REL = f"outputs/{RUN}"
TOOL_REL = "tools/" + os.path.basename(os.path.abspath(__file__))
V02_RUN = "nyc-chp-v02_20261016-055120-59848a60"
V02_TOOL_REL = ("tools/rpg-2-star-ocean-the-second_nyc-city-hall-park_walkable-pilot-640x360_pixelorama-build_"
                "unapproved-v02_20261016-055120-59848a60.py")
AUDIT_REL = ("docs/qa/rpg-2-star-ocean-the-second_nyc-city-hall-park_walkable-v02-codex-visual-audit_"
             "unapproved-v01_20261016-064422-216b6bc3.md")
VISUAL_REF_REL = ("outputs/rpg-2-star-ocean-the-second_nyc-city-hall-park_visual-direction-reference_nonruntime-v03_"
                  "20261016-124945-33aa88e9.png")
V03_CHANGES = [
    "skyline: sky band, broken rooflines, three hazed planes in brick / limestone / terracotta / glass; "
    "Woolworth-like piers (left), Municipal-Building-like colonnade (right), water tanks, one faint 2537 garden tower",
    "City Hall: per-window state table (blinds, curtains, lit, three reflection shapes), cornice shadow band, splash "
    "grime, 17 hand-placed rain streaks, deep-reveal shadows, Justice figure on the cupola, whole building and far "
    "stair hazed one aerial-perspective step; four door-scaled visitors on the stair",
    "trees: hand-cut crown gaps showing limbs, asymmetric lobe lists, SE plane forks low (V) with a low east bough, "
    "elm in vase form, back groves mirrored per instance with a spill lobe and hazed north of row 80",
    "lawns: new lawn-life layer (seated reader, picnic pair on a gingham blanket, bench reader, kneeling gardener, a "
    "small 2537 garden drone, three mounded shrub borders); seven mown patches break the tuft lattice",
    "flower beds: granite edging, mulch line, solid bloom drifts with lit caps and bloom ticks (v02 dots read dark)",
    "fountain: the tall 2-px jet is removed; two-tier centrepiece with a wide upper bowl, overflow veil (every 2nd "
    "column) and a low foam crown; the behind-fountain capture moves to stand directly behind it",
    "behind-tree capture moved 5 px west: trunk covers her east side, far foot and contact shadow visible",
    "gates: standing-on rule now counts a row against the heroine's own texels in that row (v02 counter could never "
    "exceed 0); contact-shadow gate accepts a behind capture whose front sprite covers >= 50 % of the footprint; "
    "native 640x360 windowed Godot render added beside 1280x720",
]
REFERENCE_URL = "https://www.nyc.gov/site/dcas/business/dcasmanagedbuildings/city-hall.page"
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

LAYERS = ["skyline", "forecourt", "back-groves", "streets", "city-hall", "park-ground", "ground-wear",
          "ground-detail", "fountain-basin", "cast-shadows", "props-low", "lawn-life", "forecourt-near",
          "tree-nw-ysort", "lamp-w-ysort", "trees-ne-ysort", "statue-ysort", "fountain-ysort", "lamp-e-ysort",
          "tree-se-ysort", "tree-sw-ysort", "cart-ysort", "fg-occlusion", "guides"]          # bottom -> top
ART_LAYERS = LAYERS[:-1]
BASE_LAYERS = LAYERS[:13]                                                 # merged into one base at runtime
YSORT_LAYERS = LAYERS[13:22]

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
    # v02 additions: hazed Lower Manhattan context, earth / worn turf, honey-locust yellow-greens, dogwood bloom,
    # plane-tree bark, vendor umbrella
    ("h0", "4f5866"), ("h1", "65707c"), ("h2", "7d8792"), ("h3", "98a0a8"), ("h4", "b3b8bb"), ("hw", "8a7d68"),
    ("e0", "4e4030"), ("e1", "6e5b43"), ("e2", "917b5c"),
    ("y0", "26361d"), ("y1", "3f5726"), ("y2", "5f7a2f"), ("y3", "86a03f"), ("y4", "b2c565"),
    ("pk0", "a85b7a"), ("pk1", "dc9db3"), ("pk2", "f3d7de"),
    ("bk0", "8a8670"), ("bk1", "b5b096"), ("bk2", "625e4f"),
    ("ub0", "2d5a92"), ("ub1", "e3c24e"),
    # v03 additions. Sky band; far plane (closest to the sky); hazed brick, limestone, terracotta, glass, patina and
    # roof-garden greens for Lower Manhattan; one faint 2537 teal; hazed-marble / roof / window ramps that put City
    # Hall one aerial-perspective step behind the hero-scale gate (each = the v02 colour mixed 18 % toward fa2);
    # hazed grove greens; skin, curtain and picnic-cloth colours for the lawn occupants.
    ("sy0", "a9c3cf"), ("sy1", "c4d6dc"), ("sy2", "dde6e2"),
    ("fa0", "8d9ea8"), ("fa1", "a3b2b9"), ("fa2", "b8c4c7"),
    ("hb0", "6f5f5e"), ("hb1", "8a7470"), ("hb2", "a48d84"),
    ("hl0", "8c8a85"), ("hl1", "a9a59b"), ("hl2", "c4beb0"), ("hl3", "d6d0c0"),
    ("tc0", "9a8c74"), ("tc1", "b8a888"), ("tc2", "d2c4a2"),
    ("hg0", "5d7584"), ("hg1", "7f97a3"), ("hg2", "a7bcc4"),
    ("cu0", "5e8a7e"), ("cu1", "86ae9e"), ("tq", "7fc6c0"), ("gr0", "6b8466"), ("gr1", "86a07a"),
    ("hm0", "54555c"), ("hm1", "6f6f74"), ("hm2", "8e8b8a"), ("hm3", "aba79f"), ("hm4", "c4c0b4"), ("hm5", "d8d4c8"),
    ("hm6", "e7e6db"),
    ("hr0", "4f5b5d"), ("hr1", "606f70"), ("hr2", "758688"),
    ("hw0", "3a4650"), ("hw1", "4b5c6a"), ("hw2", "698292"), ("hwl", "debf83"), ("hwl2", "ebdaac"), ("hcu", "b9a37c"),
    ("q0", "2f4a3a"), ("q1", "3f5e45"), ("q2", "537653"), ("q3", "6b8e62"), ("q4", "88a777"),
    ("hu0", "8d5a3f"), ("hu1", "c58b66"), ("hu2", "e6b58f"), ("fr0", "7d2530"),
]
GUIDE_PALETTE = [("gd-walk", "3cdcff"), ("gd-block", "ff285a"), ("gd-pin", "ffe600"), ("gd-route", "ff00ff")]
ALL_PAL = PALETTE + GUIDE_PALETTE
I = {n: i for i, (n, _) in enumerate(ALL_PAL)}
RGB = np.array([[int(h[j:j + 2], 16) for j in (0, 2, 4)] for _, h in ALL_PAL], np.uint8)
N_ART = len(PALETTE)
LUMA_IDX = (RGB.astype(np.int32) @ np.array([299, 587, 114])) // 1000

SHADE = {  # opaque cast-shadow colour for each ground colour (no semi-alpha anywhere in the scene layers)
    "g4": "g2", "g3": "g1", "g2": "g1", "g1": "g0", "g0": "f1",
    "p5": "p3", "p4": "p2", "p3": "p2", "p2": "p1", "p1": "p0", "p0": "p0",
    "x3": "x1", "x2": "x1", "x1": "x0", "x0": "a1", "a3": "a1", "a2": "a1", "a1": "a0",
    "f6": "f4", "f5": "f3", "f4": "f3", "f3": "f2", "f2": "f1", "f1": "f0",
    "fl0": "f2", "fl1": "fl0", "fl2": "au0", "fl3": "p3", "fl4": "f2", "fl5": "br1",
    "m6": "m4", "m5": "m3", "m4": "m3", "m3": "m2", "m2": "m1",
    "c3": "c1", "c2": "c1", "c1": "c0", "lw": "p2", "t1": "t0", "t2": "t1", "k3": "k2", "k2": "k1",
    "s1": "s0", "wd2": "wd1", "wd1": "wd0", "au1": "au0", "au2": "au1",
    "e2": "e1", "e1": "e0", "e0": "b1", "y4": "y2", "y3": "y1", "y2": "y1", "y1": "y0",
    "pk2": "pk0", "pk1": "pk0", "bk1": "bk0", "bk0": "bk2", "bk2": "b1",
    "w2": "w1", "w1": "w0", "wl": "au1", "wl2": "wl", "m1": "m0", "r2": "r1", "r1": "r0",
    "h4": "h3", "h3": "h2", "h2": "h1", "h1": "h0", "b2": "b1", "b1": "b0",
}
SHADE_LUT = np.arange(len(ALL_PAL), dtype=np.int16)
for _a, _b in SHADE.items():
    SHADE_LUT[I[_a]] = I[_b]

# ============================================================================ hand-authored geometry (logical px)
CX = 320                            # City Hall / central walk axis lies between columns 319 and 320 (mirror: 639-x)
# City Hall elevation rows for a section at depth 0 (the recessed links); deeper sections shift down by `d` rows
ROOF = (48, 57)
BAL = (58, 63)
CORN = (64, 67)
UP = (68, 95)
STRING = (96, 98)
LOW = (99, 126)
PLINTH = (127, 131)
# (kind, x0, x1, depth rows): projecting wings +9, central pavilion +3, links recessed
SECTIONS = [("wing", 150, 207, 9), ("link", 208, 275, 0), ("centre", 276, 363, 3), ("link", 364, 431, 0),
            ("wing", 432, 489, 9)]
PORTICO = (282, 357, 7)                                         # x0, x1, depth rows of the entrance portico
PORT_COLS = [284, 298, 312, 324, 338, 352]                      # lower-tier column left x (4 px wide), symmetric
# per-window state, keyed (section, side 0 = west / 1 = east, storey, bay); unlisted windows are dark glass with one
# of three sky-reflection shapes. Deliberately asymmetric: the east and west halves never share a pattern.
WINDOW_STATE = {
    ("wing", 0, "up", 0): "blind", ("wing", 0, "up", 2): "curtain", ("wing", 0, "low", 1): "lit",
    ("wing", 0, "low", 2): "blind-low",
    ("link", 0, "up", 0): "blind", ("link", 0, "up", 2): "lit", ("link", 0, "up", 3): "blind",
    ("link", 0, "low", 0): "curtain", ("link", 0, "low", 3): "blind",
    ("centre", 0, "up", 0): "curtain", ("centre", 0, "up", 3): "lit", ("centre", 0, "up", 4): "blind",
    ("link", 1, "up", 1): "blind-low", ("link", 1, "up", 3): "lit", ("link", 1, "low", 0): "lit",
    ("link", 1, "low", 2): "curtain",
    ("wing", 1, "up", 0): "lit", ("wing", 1, "up", 1): "blind", ("wing", 1, "low", 0): "curtain",
    ("wing", 1, "low", 2): "blind"}
# weathering: 1-px rain streaks (x, y0, y1) washing down from sills and cornice ends, darkened one SHADE step on
# the wall only; hand placed, not mirrored
STREAKS = [(153, 68, 79), (161, 98, 106), (176, 118, 124), (203, 73, 84), (214, 96, 103), (233, 88, 95),
           (258, 66, 72), (271, 112, 121), (283, 74, 79), (360, 70, 80), (371, 89, 97), (395, 110, 118),
           (413, 66, 73), (436, 99, 107), (452, 80, 87), (470, 117, 125), (486, 70, 82)]
HAZE = {"m0": "hm0", "m1": "hm1", "m2": "hm2", "m3": "hm3", "m4": "hm4", "m5": "hm5", "m6": "hm6",
        "r0": "hr0", "r1": "hr1", "r2": "hr2", "w0": "hw0", "w1": "hw1", "w2": "hw2", "wl": "hwl", "wl2": "hwl2",
        "k0": "w0", "k1": "w1", "c3": "hg2"}
VISITORS = [(300, 151, "ub0", "b0"), (329, 133, "fr0", "b1"), (334, 133, "m1", "k1"), (351, 156, "f2", "b2")]
FLAGS = [(242, "us"), (396, "nyc")]                              # flagpole x, flag (forecourt, behind the railing)
FLAG_BASE, FLAG_TOP = 137, 60
STAIR_TOP = 139                                                  # first tread row under the portico podium
STAIR_RISERS = (2, 2, 2, 3, 3, 3, 4)                             # graded: thin far steps, thick near steps
GATE_PIERS = [(266, 279), (360, 373)]                            # hero-scale piers x0, x1 (rows 124..171)
PIER_TOP = 124
RAILS = [(214, 265), (374, 425)]                                 # hero-scale railings x0, x1 (rows 143..171)
SUN = (0.30, 0.17)                                               # ground shadow offset per row of height (+x, -y)
WALK_TOP = 172
# park paths (masks built in park_masks()) -- network kept from v01, fountain plaza re-proportioned
AXIS = (292, 347)                                               # granite central walk x range
SOUTH_PLAZA = (44, 639, 338, 359)
FOUNTAIN = (172, 272)                                           # basin centre
PLAZA_R = (92, 62)
BASIN_R = (44, 24)
BASIN_IN = (40, 21)
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
LAMPS = {"lamp-w-ysort": [(295, 226)], "lamp-e-ysort": [(344, 292)]}    # staggered, not mirrored pairs
FOUNTAIN_LAMPS = [(104, 272), (240, 272)]                        # candelabra on the plaza (fountain-ysort)
STATUE = (470, 268)
CART = (470, 344)                                               # vendor cart: left x of the body, wheel base row
YSORT_PIVOTS = {"tree-nw-ysort": 204, "lamp-w-ysort": 226, "trees-ne-ysort": 240, "statue-ysort": 268,
                "fountain-ysort": 272, "lamp-e-ysort": 292, "tree-se-ysort": 300, "tree-sw-ysort": 330,
                "cart-ysort": 344}
FENCES = [(350, 368, 253), (394, 436, 253), (504, 570, 253), (350, 436, 281), (504, 570, 281),  # (x0, x1, base)
          (66, 84, 336), (108, 148, 336), (196, 289, 336), (350, 426, 336), (452, 569, 336)]
BENCHES = [(372, 252), (86, 336), (429, 336)]                    # left x, base row (benches sit in fence gaps)
BINS = [(342, 256), (560, 342)]
BOLLARDS = [(50, 342), (50, 352)]
PYLON = (214, 230)                                              # info pylon base centre
PINS = {"spawn_south": (320, 350), "city_hall_gate": (320, 178), "axis_mid": (320, 292),
        "fountain_south": (172, 318), "fountain_behind": (172, 240), "info_pylon": (214, 244),
        "statue_plaque": (470, 284), "statue_behind": (470, 250), "tree_se_behind": (398, 268),
        "lamp_w_behind": (300, 216), "lamp_w_front": (300, 234), "fountain_lamp_front": (110, 284),
        "exit_broadway_gate": (70, 270), "exit_park_row": (596, 350)}
YSORT_CASES = [("fountain_behind", "fountain-ysort", True), ("fountain_lamp_front", "fountain-ysort", False),
               ("statue_behind", "statue-ysort", True), ("statue_plaque", "statue-ysort", False),
               ("tree_se_behind", "tree-se-ysort", True), ("lamp_w_behind", "lamp-w-ysort", True),
               ("lamp_w_front", "lamp-w-ysort", False)]
ROUTE = ["spawn_south", (320, 300), (320, 270), (262, 270), (232, 244), "info_pylon", (200, 236), "fountain_behind",
         (130, 236), (112, 250), "exit_broadway_gate", (112, 292), "fountain_south", (172, 348), (320, 348),
         "axis_mid", (320, 266), (440, 266), (452, 250), "statue_behind", (486, 252), (500, 266), (588, 266),
         (588, 348), "exit_park_row", (420, 348), (320, 348), "lamp_w_front", (314, 234), (314, 216), "lamp_w_behind",
         "city_hall_gate"]
CAPTURES = {"axis": "axis_mid", "behind-fountain": "fountain_behind", "behind-tree": "tree_se_behind"}
# actor contact shadow: rows of a 17x5 two-step alpha ellipse ('X' core, 'x' rim), centred 1 px east of the foot
# and 1 row north of it (sun from the south-west pushes the contact shadow slightly north-east)
SHADOW_ROWS = ["....xxxxxxxxx....",
               "..xxXXXXXXXXXxx..",
               ".xXXXXXXXXXXXXXx.",
               "..xxXXXXXXXXXxx..",
               "....xxxxxxxxx...."]
SHADOW_ALPHA = {"X": 118, "x": 64}
SHADOW_OFF = (1, -1)                                             # (dx, dy) of the shadow centre from the foot
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
    """Deterministic hash in [0, 1): only picks a slab / hex-block tone or a course offset from a short hand table."""
    return int.from_bytes(hashlib.sha256(repr(key).encode()).digest()[:4], "little") / 2 ** 32


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


def poly(L, pts, c, mask=None):
    """1-px polyline through hand-written points (cracks, tar seams); optionally clipped to a mask."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for k in range(n + 1):
            x, y = int(round(x0 + (x1 - x0) * k / n)), int(round(y0 + (y1 - y0) * k / n))
            if 0 <= x < W and 0 <= y < H and (mask is None or mask[y, x]):
                L[y, x] = I[c]


def shade_region(L, mask):
    """Darken already painted texels of L inside mask by one SHADE step (opaque, palette only)."""
    sel = mask & (L >= 0)
    L[sel] = SHADE_LUT[L[sel]]


def mirror(x, w=1):
    return W - 1 - x - (w - 1)


def merge_orphans(L, region, passes=2):
    """Cluster cleanup inside `region`: a texel whose four neighbours (inside the region) all differ from it takes
    the most common neighbour colour (ties -> the darker one), so clusters stay intentional, never lone texels."""
    for _ in range(passes):
        ys, xs = np.nonzero(region)
        changed = 0
        for y, x in zip(ys, xs):
            c = L[y, x]
            nb = [L[y + dy, x + dx] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))
                  if 0 <= y + dy < H and 0 <= x + dx < W and region[y + dy, x + dx]]
            if len(nb) < 3 or c in nb:
                continue
            cnt = {}
            for n in nb:
                cnt[n] = cnt.get(n, 0) + 1
            best = max(cnt.items(), key=lambda kv: (kv[1], -LUMA_IDX[kv[0]]))[0]
            L[y, x] = best
            changed += 1
        if not changed:
            break


# ============================================================================ foliage: hand-written lobes, leaf clumps
LIGHT = np.array([-0.55, -0.62, 0.56])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
OFF7 = ((0, 0), (1, -1), (-1, 1), (1, 1), (0, -1), (-1, 0), (1, 0))       # fixed clump offset table (cycled)
SIZE5 = (1.0, 0.84, 1.14, 0.92, 1.06)                                      # fixed clump size cycle
SPECIES = {   # ramp dark -> light, tone cuts, leaf-clump spacing (px), optional gaps / bloom, bark style
    "plane": {"ramp": ("f0", "f1", "f2", "f3", "f4", "f5", "f6"), "cuts": (-0.40, -0.14, 0.12, 0.36, 0.60, 0.84),
              "clump": 5.2, "bark": "plane"},
    "elm": {"ramp": ("f0", "f1", "f2", "f3", "f4", "f5"), "cuts": (-0.34, -0.06, 0.22, 0.50, 0.76), "clump": 4.4,
            "bark": "dark"},
    "locust": {"ramp": ("y0", "y1", "y2", "y3", "y4"), "cuts": (-0.28, 0.02, 0.32, 0.64), "clump": 3.4,
               "holes": 9, "bark": "dark"},
    "dogwood": {"ramp": ("f1", "f2", "f3", "f4", "f5"), "cuts": (-0.30, 0.0, 0.30, 0.60), "clump": 3.8,
                "bloom": True, "bark": "dark"},
    "mid": {"ramp": ("f0", "f1", "f2", "f3", "f4", "f5"), "cuts": (-0.36, -0.06, 0.24, 0.52, 0.80), "clump": 3.6,
            "bark": "dark"},
    "back": {"ramp": ("f0", "f1", "f2", "f3", "f4"), "cuts": (-0.26, 0.06, 0.38, 0.70), "clump": 3.2,
             "bark": "dark"},
    "backhaze": {"ramp": ("q0", "q1", "q2", "q3", "q4"), "cuts": (-0.26, 0.06, 0.38, 0.70), "clump": 3.2,
                 "bark": "dark"},
    "box": {"ramp": ("f1", "f2", "f3", "f4", "f5"), "cuts": (-0.30, 0.0, 0.30, 0.62), "clump": 2.8, "bark": "dark"},
}


def crown(L, cx, cy, lobes, sp, reg=None, squash=0.86, gain=1.0, gaps=()):
    """Canopy from a hand-written lobe list (dx, dy, r px). Each lobe is lit as a sphere from the south-west; its
    area is filled with leaf clumps on a fixed staggered lattice (OFF7 / SIZE5 tables, no random jitter). Every clump
    is a small disc with a lit upper-left crescent and a shaded lower-right rim, drawn top to bottom so nearer clumps
    overlap farther ones; the canopy silhouette is the union of the clumps (lumpy, never a smooth ellipse).
    v03: `gaps` is a hand-written list of (dx, dy, rx, ry) sky holes -- clumps centred inside one are skipped, so
    limbs painted before the crown show through and the silhouette is no longer a closed round mass."""
    S = SPECIES[sp]
    ramp, cuts, s = S["ramp"], S["cuts"], S["clump"]
    lob = sorted(((cx + dx, cy + dy, r) for dx, dy, r in lobes), key=lambda t: t[1])
    R = max(math.hypot(dx, dy) + r for dx, dy, r in lobes)
    bx0 = int(min(lx - r for lx, _, r in lob)) - 1
    bx1 = int(max(lx + r for lx, _, r in lob)) + 1
    by0 = int(min(ly - r * squash for _, ly, r in lob)) - 1
    by1 = int(max(ly + r * squash for _, ly, r in lob)) + 1
    clumps = []
    j, y = 0, float(by0)
    while y <= by1:
        i, x = 0, bx0 + (s / 2 if j % 2 else 0.0)
        while x <= bx1:
            ox, oy = OFF7[(i * 3 + j * 5) % 7]
            qx, qy = x + ox, y + oy
            hit = None
            for lb in lob:
                if ((qx - lb[0]) / lb[2]) ** 2 + ((qy - lb[1]) / (lb[2] * squash)) ** 2 <= 1.0:
                    hit = lb
            if hit is not None and any(((qx - cx - gx) / gr) ** 2 + ((qy - cy - gy) / gq) ** 2 <= 1.0
                                       for gx, gy, gr, gq in gaps):
                hit = None
            if hit is not None and not (S.get("holes") and (i * 7 + j * 3) % S["holes"] == 0):
                clumps.append((qy, qx, hit, SIZE5[(i + 2 * j) % 5], i, j))
            x += s
            i += 1
        y += s * 0.74
        j += 1
    clumps.sort(key=lambda t: (t[0], t[1]))
    union = np.zeros((H, W), bool)
    top = len(ramp) - 1
    for (qy, qx, (lx, ly, r), sz, i, j) in clumps:
        nx, ny = (qx - lx) / r, (qy - ly) / (r * squash)
        nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
        v = ((nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]) * 0.78
             + (-0.30 * (qx - cx) / R - 0.42 * (qy - cy) / R) * 0.55) * gain
        k = sum(1 for c in cuts if v >= c)
        rr = s * 0.62 * sz
        for yy in range(max(0, int(math.floor(qy - rr))), min(H, int(math.ceil(qy + rr)) + 1)):
            for xx in range(max(0, int(math.floor(qx - rr))), min(W, int(math.ceil(qx + rr)) + 1)):
                u, w = (xx + 0.5 - qx) / rr, (yy + 0.5 - qy) / rr
                d2 = u * u + w * w
                if d2 > 1.0:
                    continue
                if rr >= 2.3 and -u * 0.6 - w * 0.8 > 0.40 and d2 < 0.85:
                    kk = k + 1
                elif u * 0.55 + w * 0.85 > (0.52 if rr >= 2.3 else 0.70):
                    kk = k - 1
                else:
                    kk = k
                L[yy, xx] = I[ramp[max(0, min(top, kk))]]
                union[yy, xx] = True
        if S.get("bloom") and (i + 2 * j) % 3 == 0 and k >= 1:              # dogwood bracts: 2x2 / 2x1 clusters
            bx, by = int(round(qx)) - 1, int(round(qy)) - 1
            if k >= 3:
                stamp(L, bx, by, ["PP", "pq"], {"P": "pk2", "p": "pk1", "q": "pk0"})
            else:
                stamp(L, bx, by, ["pp", "q."], {"p": "pk1", "q": "pk0"})
    hole = ~union & ((np.roll(union, 1, 0) & np.roll(union, -1, 0)) | (np.roll(union, 1, 1) & np.roll(union, -1, 1)))
    L[hole] = I[ramp[0]]                                              # close 1-px pinholes between clumps
    union |= hole
    u8 = sum(np.roll(np.roll(union, dy, 0), dx, 1).astype(np.int8) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
             if (dy, dx) != (0, 0))
    nook = ~union & (u8 >= 6)                                         # v03: also close 1-px nooks a gap leaves
    L[nook] = I[ramp[0]]
    union |= nook
    edge = np.zeros_like(union)
    edge[:-1] |= union[:-1] & ~union[1:]
    edge[:, :-1] |= union[:, :-1] & ~union[:, 1:]
    L[edge] = I[ramp[0]]
    merge_orphans(L, union)
    if reg is not None:
        reg |= union
    return union


def limb(L, p, q, w0, w1, bark, reg=None, mottle=False):
    """Tapered bark segment p -> q, lit from the west. 'plane': pale bark with olive / cream patches at fixed
    fractions of the main stem; 'dark': furrowed bark with a dashed furrow down the middle."""
    (x0, y0), (x1, y1) = p, q
    n = max(1, int(round(max(abs(x1 - x0), abs(y1 - y0)))))
    for k in range(n + 1):
        t = k / n
        xc, yc = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        w = max(1, int(round(w0 + (w1 - w0) * t)))
        flare = 1 if (k <= 1 and w0 >= 5) else 0
        xa = int(math.floor(xc - w / 2.0 + 0.5)) - flare
        xb = xa + w - 1 + 2 * flare
        yy = int(round(yc))
        for xx in range(xa, xb + 1):
            u = (xx - xa + 0.5) / (xb - xa + 1)
            if bark == "plane":
                c = "bk0" if u < 0.36 else ("bk2" if u < 0.76 else "b1")
            else:
                c = "b2" if u < 0.34 else ("b1" if u < 0.78 else "b0")
                if xb - xa >= 3 and xx == xa + (xb - xa + 1) // 2 and (yy // 3) % 2 == 0:
                    c = "b0"
            px(L, xx, yy, c, reg)
    if mottle:
        for f, side in ((0.10, 1), (0.22, 0), (0.40, 1), (0.55, 0), (0.70, 1)):
            xc, yc = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
            xx = int(round(xc)) - 2 if side == 0 else int(round(xc)) + 1
            rect(L, xx, int(round(yc)), xx + 1, int(round(yc)) + 2, "bk1" if side == 0 else "bk0", reg)


def paint_tree(L, t, reg=None):
    bark = SPECIES[t["sp"]]["bark"]
    for n, (p, q, w0, w1) in enumerate(t.get("limbs", ())):
        limb(L, p, q, w0, w1, bark, reg, mottle=(bark == "plane" and n == 0))
    return crown(L, t["c"][0], t["c"][1], t["lobes"], t["sp"], reg, gain=t.get("gain", 1.0), gaps=t.get("gaps", ()))


TREES = {   # hero-scale Y-sorted trees; each has its own trunk polylines, lobe list and hand-cut crown gaps (v03)
    "tree-nw-ysort": [dict(sp="plane", base=(96, 204), c=(100, 148),
                           limbs=[((96, 204), (98, 178), 9, 7), ((97, 186), (84, 166), 5, 3),
                                  ((99, 184), (114, 162), 5, 3), ((114, 163), (108, 138), 3, 2),
                                  ((84, 167), (77, 150), 3, 2), ((113, 164), (125, 150), 2, 2)],
                           lobes=[(-24, -12, 14), (-6, -26, 13), (14, -22, 12), (30, -10, 11), (-34, 4, 11),
                                  (-12, -6, 17), (12, -4, 15), (34, 10, 8), (-22, 16, 12), (2, 14, 13),
                                  (20, 18, 9), (-40, -4, 7), (40, -2, 6), (6, -36, 7)],
                           gaps=[(8, -10, 6, 4), (-21, 6, 5, 4), (24, 4, 4, 3)])],
    "trees-ne-ysort": [dict(sp="locust", base=(462, 240), c=(464, 196),
                            limbs=[((462, 240), (465, 214), 5, 4), ((465, 216), (456, 203), 3, 2),
                                   ((465, 215), (475, 204), 3, 2)],
                            lobes=[(-14, -8, 11), (3, -14, 12), (17, -6, 10), (-8, 6, 11), (12, 8, 10),
                                   (-21, 7, 7), (24, -14, 6)],
                            gaps=[(4, 0, 4, 3)]),
                       dict(sp="elm", base=(540, 240), c=(542, 184),
                            limbs=[((540, 240), (541, 214), 8, 6), ((540, 216), (522, 190), 4, 3),
                                   ((541, 214), (543, 182), 4, 3), ((542, 216), (561, 190), 4, 3),
                                   ((523, 192), (514, 178), 2, 2), ((560, 192), (570, 180), 2, 2)],
                            lobes=[(-32, -10, 12), (-16, -20, 13), (2, -24, 12), (18, -20, 13), (32, -8, 11),
                                   (-22, 2, 10), (22, 2, 10), (0, -6, 11), (-40, -2, 6), (40, 4, 6)],
                            gaps=[(-10, -2, 5, 4), (12, -4, 5, 4)])],
    "tree-se-ysort": [dict(sp="plane", base=(410, 300), c=(412, 194),
                           limbs=[((410, 300), (411, 266), 10, 8), ((411, 268), (400, 226), 6, 4),
                                  ((412, 268), (424, 222), 6, 4), ((400, 228), (388, 206), 4, 2),
                                  ((424, 224), (440, 208), 4, 2), ((413, 252), (434, 236), 4, 3),
                                  ((401, 232), (405, 206), 3, 2)],
                           lobes=[(-26, -6, 12), (-12, -14, 12), (4, -22, 11), (18, -14, 12), (30, -4, 10),
                                  (-18, 4, 11), (14, 4, 12), (-4, -4, 10), (30, 32, 8), (38, 26, 7),
                                  (22, 36, 6), (-36, 2, 6)],
                           gaps=[(-2, 6, 5, 4), (8, -6, 4, 3), (24, 14, 5, 4)])],
    "tree-sw-ysort": [dict(sp="dogwood", base=(262, 330), c=(262, 304),
                           limbs=[((260, 330), (256, 312), 3, 2), ((263, 330), (265, 310), 3, 2),
                                  ((265, 329), (272, 314), 2, 2)],
                           lobes=[(-10, -4, 9), (2, -8, 10), (12, -2, 8), (-4, 5, 9), (9, 6, 8), (-15, 3, 5)])],
}
MID_TREES = [   # backdrop scale (forecourt-near), overlapping the wing corners
    dict(sp="mid", base=(134, 160), c=(136, 128), limbs=[((134, 160), (135, 140), 4, 3)],
         lobes=[(-14, -6, 11), (2, -12, 12), (15, -4, 10), (-6, 6, 11), (10, 7, 9)]),
    dict(sp="mid", base=(494, 158), c=(496, 128), limbs=[((494, 158), (495, 140), 4, 3)],
         lobes=[(-13, -5, 10), (1, -11, 11), (14, -4, 10), (-5, 6, 10), (11, 6, 9)])]
SHRUBS = [dict(sp="box", base=(196, 171), c=(196, 161), lobes=[(-12, 2, 9), (0, -3, 11), (12, 2, 8)]),
          dict(sp="box", base=(444, 171), c=(444, 161), lobes=[(-13, 2, 8), (0, -3, 11), (12, 2, 9)])]
BACK_TPL = {"A": [(-8, -4, 7), (4, -7, 8), (10, 1, 6), (-3, 4, 8)],
            "B": [(-9, 0, 7), (0, -8, 8), (9, -2, 7), (2, 5, 7)],
            "C": [(-6, -6, 6), (5, -6, 7), (-9, 3, 6), (7, 4, 6), (0, 1, 8)]}
BACK_TREES = [  # (x, y, scale, lobe template, trunk base row or None); listed back (north) to front
    (116, 34, 1.0, "B", None), (82, 44, 1.3, "A", None), (140, 56, 0.9, "C", None), (106, 68, 1.2, "A", None),
    (70, 76, 1.4, "C", None), (128, 96, 1.1, "C", None), (90, 104, 1.3, "B", None), (74, 132, 1.2, "A", 150),
    (286, 46, 0.8, "B", None), (354, 46, 0.8, "A", None), (228, 44, 0.9, "C", None), (262, 46, 0.7, "A", None),
    (384, 44, 0.8, "B", None), (414, 42, 1.0, "C", None), (174, 46, 0.9, "A", None), (466, 46, 0.9, "B", None),
    (526, 64, 1.0, "B", None), (594, 62, 1.2, "C", None), (560, 76, 1.3, "A", None), (536, 100, 1.2, "C", None),
    (600, 96, 1.1, "A", None), (574, 108, 1.4, "B", None), (520, 124, 1.0, "A", 140), (592, 134, 1.2, "C", 152),
    (60, 52, 1.2, "C", None), (148, 84, 1.0, "B", None), (150, 116, 1.0, "A", 132), (100, 128, 1.1, "B", 146),
    (506, 70, 1.0, "A", None), (492, 98, 0.9, "C", None), (604, 40, 1.1, "A", None), (500, 112, 1.1, "B", 128),
    (548, 128, 1.2, "A", 146), (126, 40, 1.0, "C", None), (548, 46, 1.0, "B", None),
]
FG_TREES = [dict(sp="mid", c=(-4, 366), lobes=[(-6, -16, 16), (16, -10, 15), (2, 4, 20), (26, 6, 12)]),
            dict(sp="mid", c=(646, 368), lobes=[(-18, -12, 15), (2, -18, 14), (-4, 2, 19), (-26, 8, 11)])]


# ============================================================================ skyline: restrained Lower Manhattan
WATER_TANK = ["...a...", "..aAa..", ".aAAAa.", "LWWWWdd", "lwwwwdd", "LWWWWdd", "lwwwwdd", "LWWWWdd", ".k...k.",
              ".kk.kk.", "kkkkkkk"]
TANK_MAP = {"a": "h1", "A": "h2", "L": "e2", "l": "e1", "W": "hw", "w": "e1", "d": "e0", "k": "h0"}


def paint_skyline():
    """Opaque base: the sky band and hazed Lower Manhattan north of Chambers Street seen over City Hall, in three
    aerial-perspective planes (far towers nearly sky-coloured; a warmer mid plane of brick, limestone and terracotta
    blocks with broken rooflines and water tanks; the nearest Tweed Courthouse roof). Left: Woolworth-like
    terracotta piers; right: Municipal-Building-like limestone colonnade; far plane: one slim 2537 garden tower with a
    faint teal seam. Generic massing, an interpretation, not traced."""
    L = new()
    L[:, :] = I["sy2"]
    rect(L, 0, 0, W - 1, 3, "sy0"); rect(L, 0, 4, W - 1, 10, "sy1")
    for (x0, x1, top, prof) in FAR_TOWERS:                           # far plane: pier shadows only, no window grid
        rect(L, x0, top, x1, 60, "fa1")
        rect(L, x0, top, x0, 60, "fa2")
        if prof == "stepped":
            rect(L, x0, top, x0 + 4, top + 5, "sy1"); rect(L, x1 - 3, top, x1, top + 3, "sy1")
            rect(L, x0 + 5, top, x0 + 5, top + 5, "fa2"); rect(L, x0, top + 6, x0 + 4, top + 6, "fa2")
        if prof == "ribbed":
            for x in range(x0 + 3, x1 - 1, 4):
                rect(L, x, top + 2, x, 60, "fa0")
        rect(L, x0, top, x1, top, "fa2")
    gx0, gx1 = GARDEN_TOWER                                         # 2537 garden tower: terraces + teal seam
    rect(L, gx0, 0, gx1, 60, "fa1"); rect(L, gx0, 0, gx0 + 1, 60, "fa2"); rect(L, gx1, 0, gx1, 60, "fa0")
    for y in range(3, 40, 7):
        rect(L, gx0 - 1, y, gx1 + 1, y, "gr1"); rect(L, gx0 - 1, y + 1, gx1 + 1, y + 1, "gr0")
        rect(L, gx0 + 2, y - 1, gx0 + 4, y - 1, "gr1"); rect(L, gx1 - 5, y - 1, gx1 - 4, y - 1, "gr1")
        rect(L, (gx0 + gx1) // 2, y + 2, (gx0 + gx1) // 2, y + 5, "tq")
    for (x0, x1, top, mat, win, tank) in MID_BLOCKS:                 # mid plane: material, cornice, own rhythm
        face, lit, shade, glass, trim = SKY_MAT[mat]
        rect(L, x0, top, x1, 60, face)
        rect(L, x0, top, x0, 60, lit)
        rect(L, x1, top, x1, 60, shade)
        rect(L, x0, top, x1, top, trim); rect(L, x0, top + 1, x1, top + 1, shade)
        dx, dy, ox, oy, skip = win
        for r, y in enumerate(range(top + 3 + oy, 60, dy)):
            for c, x in enumerate(range(x0 + 1 + ox, x1 - 1, dx)):
                if (r + c * 2) % skip == skip - 1:
                    continue
                rect(L, x, y, x + (1 if mat in ("brick", "terra") else 0), y + 1, glass)
                if mat == "brick":
                    rect(L, x, y - 1, x + 1, y - 1, trim)
        if tank is not None:
            stamp(L, tank, top - len(WATER_TANK) + 1, WATER_TANK, TANK_MAP)
    for (x, y) in SKY_LIT_WINDOWS:                                    # a few warm windows (late afternoon)
        rect(L, x, y, x + 1, y + 1, "hwl")
    # Woolworth-like terracotta tower at the left (Broadway): piers, recessed spandrels, pointed heads; rises out of
    # the frame, so only its pier rhythm and Gothic heads show
    rect(L, 64, 0, 150, 60, "tc1")
    for x in range(64, 151, 6):
        rect(L, x, 0, x, 60, "tc2"); rect(L, x + 1, 0, x + 1, 60, "tc1"); rect(L, x + 5, 0, x + 5, 60, "tc0")
        for y in range(4, 60, 9):
            rect(L, x + 2, y, x + 4, y + 5, "hg0"); px(L, x + 3, y - 1, "hg0")
            rect(L, x + 2, y + 6, x + 4, y + 6, "tc0")
            px(L, x + 2, y, "tc1"); px(L, x + 4, y, "tc1")
    for y in (21, 22, 46, 47):                                        # belt courses
        rect(L, 64, y, 150, y, "tc2" if y in (21, 46) else "tc0")
    rect(L, 150, 0, 150, 60, "tc0")
    # lower neighbour with a copper mansard (x 151..177)
    rect(L, 151, 12, 177, 60, "hb1"); rect(L, 151, 9, 177, 13, "cu0"); rect(L, 151, 9, 177, 9, "cu1")
    for x in range(154, 176, 6):
        rect(L, x, 10, x + 1, 12, "cu1"); rect(L, x, 17, x + 1, 19, "hb0"); rect(L, x, 25, x + 1, 27, "hb0")
    # Tweed Courthouse roof directly behind City Hall: hazed slate hip, ridge, two limestone chimneys
    for y in range(24, 48):
        inset = max(0, 36 - (y - 24) * 36 // 23)
        rect(L, 200 + inset, y, 440 - inset, y, "hr0" if (y - 24) % 3 == 2 else "hr1")
        px(L, 200 + inset, y, "hr2"); px(L, 440 - inset, y, "hr0")
    rect(L, 236, 24, 404, 24, "hr2")
    for cxx in (250, 384):
        rect(L, cxx, 15, cxx + 5, 24, "hl1"); rect(L, cxx + 5, 16, cxx + 5, 24, "hl0"); rect(L, cxx - 1, 15, cxx + 6, 15, "hl3")
    # Municipal-Building-like limestone block (right): colonnade base, grouped window bays, setback central tower
    rect(L, 462, 6, 603, 60, "hl1")
    for b, x in enumerate(range(466, 600, 12)):
        rect(L, x - 2, 6, x - 1, 60, "hl2")
        for xx in (x + 1, x + 4, x + 7):
            for y in range(12, 33, 4):
                rect(L, xx, y, xx + 1, y + 2, "hg0" if (b + y // 4) % 5 else "hg1")
    rect(L, 462, 33, 603, 33, "hl3"); rect(L, 462, 34, 603, 35, "hl0")
    for x in range(464, 602, 5):                                      # colonnade
        rect(L, x, 36, x + 1, 60, "hl2"); rect(L, x + 2, 36, x + 4, 60, "hl0")
    rect(L, 524, 38, 542, 60, "hl0"); rect(L, 526, 40, 540, 60, "hg0")    # central arch (shadowed passage)
    for y in range(38, 42):
        px(L, 524 + (41 - y), y, "hl2"); px(L, 542 - (41 - y), y, "hl2")
    rect(L, 462, 6, 603, 6, "hl3"); rect(L, 462, 7, 603, 7, "hl0")
    rect(L, 590, 0, 603, 6, "sy1")                                    # east end steps down
    rect(L, 514, 0, 552, 6, "hl2")                                    # central tower rises out of the frame
    for x in range(516, 551, 5):
        rect(L, x, 0, x + 1, 5, "hl3"); rect(L, x + 2, 0, x + 2, 5, "hl0")
    rect(L, 462, 6, 462, 60, "hl2"); rect(L, 603, 6, 603, 60, "hl0")
    return L


FAR_TOWERS = [(176, 205, 6, "ribbed"), (206, 229, 11, "flat"), (252, 284, 3, "stepped"), (285, 300, 9, "flat"),
              (338, 366, 4, "ribbed"), (367, 384, 13, "flat"), (408, 436, 7, "stepped"), (437, 461, 2, "ribbed")]
GARDEN_TOWER = (234, 247)
SKY_MAT = {"brick": ("hb1", "hb2", "hb0", "hb0", "hl2"), "lime": ("hl1", "hl2", "hl0", "hg0", "hl3"),
           "terra": ("tc1", "tc2", "tc0", "hg0", "tc2"), "glass": ("hg1", "hg2", "hg0", "hg0", "hg2")}
MID_BLOCKS = [  # (x0, x1, roof row, material, (dx, dy, x off, y off, skip every n-th), water-tank x or None)
    (178, 203, 17, "lime", (3, 5, 1, 1, 7), 186), (204, 233, 21, "brick", (5, 4, 2, 0, 4), None),
    (250, 279, 15, "terra", (4, 4, 1, 1, 6), 266), (280, 299, 19, "brick", (4, 5, 0, 0, 3), None),
    (340, 362, 18, "glass", (3, 4, 0, 0, 99), None), (363, 389, 14, "brick", (5, 4, 1, 1, 5), 372),
    (390, 411, 20, "lime", (3, 5, 1, 0, 4), None), (412, 440, 16, "brick", (4, 4, 2, 1, 6), 428),
    (441, 461, 12, "terra", (4, 5, 1, 1, 5), None)]
SKY_LIT_WINDOWS = [(207, 25), (217, 29), (369, 18), (387, 22), (420, 21), (452, 30), (186, 31), (494, 16)]


BACK_EXTRA = ((-12, 3, 4), (11, -5, 4), (3, 7, 5), (-6, -9, 4), (13, 4, 3))    # one spill lobe per tree (cycled)


def paint_back_groves():
    """Mid-distance groves. v03: every second tree mirrors its template and each gets one extra spill lobe from a
    short hand table, so no two neighbours share a silhouette; trees north of row 80 use the hazed q ramp."""
    L = new()
    for k, (x, y, s, tpl, tb) in enumerate(BACK_TREES):
        sgn = -1 if k % 2 else 1
        lobes = [(sgn * dx * s, dy * s, r * s) for dx, dy, r in BACK_TPL[tpl]]
        ex, ey, er = BACK_EXTRA[k % len(BACK_EXTRA)]
        lobes.append((sgn * ex * s, ey * s, er * s))
        if tb is not None:
            limb(L, (x, tb), (x, y + int(6 * s)), 3, 2, "dark")
        crown(L, x, y, lobes, "backhaze" if y < 80 else "back", gain=0.9)
    return L


# ============================================================================ streets (Broadway, Park Row)
def lamp_sprite(L, x, base, reg=None):
    """Cast-iron park lantern (about 3.3 m at the heroine scale) with a 2537 teal sensor ring under the lantern."""
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


ASPHALT_PATCHES = [(1, 64, 6, 90), (34, 150, 40, 171), (1, 236, 6, 249), (34, 296, 40, 318)]
TAR_SEAMS = [[(2, 120), (4, 126), (3, 133)], [(36, 210), (38, 216), (37, 224)], [(4, 300), (6, 305), (5, 311)],
             [(35, 30), (37, 36)]]
SIDEWALK_STAINS = [(52, 124, 3, 5), (49, 262, 2, 4), (56, 318, 3, 2), (616, 70, 4, 3), (630, 250, 3, 5),
                   (612, 330, 4, 2)]
STREET_TREE = dict(sp="mid", base=(622, 149), c=(622, 112), limbs=[((622, 149), (622, 122), 4, 3)],
                   lobes=[(-8, -4, 8), (4, -8, 9), (10, 0, 7), (-2, 5, 9)])


def paint_streets():
    L = new()
    road = box(BROADWAY[0], 0, BROADWAY[1], H - 1)
    L[road] = I["a1"]
    for (x0, y0, x1, y1) in ASPHALT_PATCHES:                        # repaired asphalt, hand placed
        rect(L, x0, y0, x1, y1, "a2"); rect(L, x0, y1, x1, y1, "a0"); rect(L, x1, y0, x1, y1, "a0")
    for pts in TAR_SEAMS:
        poly(L, pts, "a0")
    for (mx, my) in ((37, 270), (3, 180)):                          # manhole covers
        m = ell(mx, my, 3, 2)
        L[m] = I["k1"]; L[m & edge_above(m)] = I["a3"]
    # maglev guideway (2537): concrete slab with expansion joints, two grooves, teal centre strip
    gw = box(8, 0, 32, H - 1)
    L[gw] = I["a2"]
    for y in range(10, H, 24):
        rect(L, 8, y, 32, y, "a1")
    rect(L, 8, 0, 8, H - 1, "a3"); rect(L, 32, 0, 32, H - 1, "a0")
    rect(L, 12, 0, 12, H - 1, "a0"); rect(L, 28, 0, 28, H - 1, "a0")
    rect(L, 19, 0, 20, H - 1, "t0")
    for y in range(4, H, 12):
        rect(L, 19, y, 20, y + 3, "t1")
    rect(L, 36, 0, 37, H - 1, "a1")
    for y in range(6, 330, 22):                                     # lane dashes (one-way southbound lane)
        rect(L, 37, y, 37, y + 9, "lw")
    for x in range(2, 41, 8):                                       # crosswalk at the south plaza
        rect(L, x, 341, x + 3, 357, "lw")
    rect(L, 42, 0, 42, H - 1, "p4"); rect(L, 43, 0, 43, H - 1, "p2")
    sw = box(44, 0, 61, H - 1)
    L[sw] = I["p3"]
    for y in range(5, H, 14):
        rect(L, 44, y, 61, y, "p2")
    rect(L, 53, 0, 53, H - 1, "p2")
    pr = box(606, 0, W - 1, H - 1)
    L[pr] = I["p3"]
    for y in range(9, H, 14):
        rect(L, 606, y, W - 1, y, "p2")
    rect(L, 622, 0, 622, H - 1, "p2")
    for (sx, sy, rx, ry) in SIDEWALK_STAINS:
        L[ell(sx, sy, rx, ry) & (sw | pr)] = I["p2"]
    # tall park fences (Broadway side with gate gap, Park Row side): pickets, lit tops
    for x0 in (BW_FENCE, PARK_ROW):
        for y in range(0, 338):
            if x0 == BW_FENCE and 256 <= y <= 283:
                continue
            px(L, x0, y, "k1"); px(L, x0 + 1, y, "k0")
            if y % 4 in (0, 1):
                px(L, x0, y, "k2")
    for (y0, y1) in ((250, 257), (282, 289)):                       # Broadway gate piers (registered as items)
        rect(L, 60, y0, 65, y1, "m3"); rect(L, 60, y0, 61, y1, "m4"); rect(L, 65, y0, 65, y1, "m2")
        rect(L, 59, y0, 66, y0 + 1, "m5")
    # maglev tram on the guideway: brushed-steel roof (toned down so it no longer competes with City Hall)
    rect(L, 7, 34, 33, 110, "m2")
    rect(L, 7, 34, 7, 110, "m3"); rect(L, 33, 34, 33, 110, "k1"); rect(L, 32, 34, 32, 110, "m1")
    rect(L, 7, 34, 33, 35, "m3")
    for (a, b) in ((46, 55), (88, 97)):
        rect(L, 12, a, 28, b, "k1"); rect(L, 12, a, 28, a, "k2"); rect(L, 13, a + 2, 27, b - 2, "m1")
    for y in range(38, 108, 6):
        rect(L, 19, y, 20, y + 3, "t0")
    for y in (64, 72, 80):
        rect(L, 19, y, 20, y + 1, "t1")
    rect(L, 7, 111, 33, 120, "k1")
    rect(L, 9, 112, 31, 115, "w1"); rect(L, 9, 112, 14, 113, "w2")
    rect(L, 8, 117, 10, 118, "t1"); rect(L, 30, 117, 32, 118, "t1")
    rect(L, 12, 117, 28, 118, "k2"); rect(L, 7, 120, 33, 120, "k0")
    rect(L, 34, 36, 35, 120, "a0")
    # glass tram shelter on the Broadway sidewalk (roof from above, posts, map screen)
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
    # NYC subway stair entrance on the Park Row sidewalk: descending stair, railings, green globe lamps, sign plate
    for y in range(194, 227):
        depth = (226 - y) // 8
        rect(L, 612, y, 630, y, ("a3", "a2", "a1", "a0", "a0")[depth])
        if (226 - y) % 3 == 0:
            rect(L, 612, y, 630, y, ("p3", "a3", "a2", "a1", "a1")[depth])
    for xr in (610, 631):
        rect(L, xr, 192, xr + 1, 226, "k1"); rect(L, xr, 192, xr, 226, "k2")
        rect(L, xr - 1 if xr == 610 else xr + 2, 192, xr - 1 if xr == 610 else xr + 2, 227, "p4")
    rect(L, 610, 192, 632, 193, "k1"); rect(L, 610, 192, 632, 192, "k2"); rect(L, 609, 191, 633, 191, "p4")
    rect(L, 614, 188, 628, 190, "k1"); rect(L, 615, 189, 627, 189, "lw"); rect(L, 615, 189, 617, 189, "f4")
    for gx in (611, 631):
        rect(L, gx, 206, gx, 226, "k1"); rect(L, gx - 1, 225, gx + 1, 226, "k0")
        stamp(L, gx - 2, 198, [".lg.", "lggf", "gggf", ".ff."], {"l": "f6", "g": "f4", "f": "f3"})
        rect(L, gx - 1, 202, gx + 1, 202, "k1")
    lamp_sprite(L, 624, 300)                                         # classic lamp on Park Row (never reachable)
    rect(L, 614, 147, 630, 151, "k1"); rect(L, 615, 148, 629, 150, "s1"); rect(L, 615, 148, 629, 148, "s0")
    paint_tree(L, STREET_TREE)                                       # NYC street tree in an iron-guarded pit
    return L


# ============================================================================ City Hall
def facade_window(L, x, top, h, arched, key, front):
    """One window. Its state comes from the hand-written WINDOW_STATE table (blind / low blind / curtains / lit /
    dark) and dark panes take one of three sky-reflection shapes, so no two neighbouring windows repeat. Deep reveal:
    the lintel and west jamb throw a 1-px shadow into the opening (sun from the south-west)."""
    state = WINDOW_STATE.get(key, "dark")
    lit = state == "lit"
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
    mid = top + h // 3 if arched else top + h // 2
    if state in ("blind", "blind-low"):                                    # cream roller blind, hem, dark below
        yb = top + (h * 2) // 5 if state == "blind" else top + h - 4
        rect(L, x, top + (1 if arched else 0), x + 5, yb, "tc2"); rect(L, x, yb, x + 5, yb, "m2")
        rect(L, x + 5, top + 1, x + 5, yb - 1, "tc1")
    elif state == "curtain":                                               # tied-back curtains framing dark glass
        for cx_ in (x, x + 5):
            rect(L, cx_, top + 1, cx_, top + h - 1, "hcu")
        px(L, x + 1, mid + 1, "hcu"); px(L, x + 4, mid + 1, "hcu")
    rect(L, x, mid, x + 5, mid, mull)
    rect(L, x + 2, top + 1, x + 2, top + h - 1, mull)
    if state in ("dark", "curtain"):
        v = key[1] * 1 + {"up": 0, "low": 1}[key[2]] + 2 * key[3]
        v = (v + {"wing": 0, "link": 1, "centre": 2}[key[0]]) % 3
        if v == 0:
            rect(L, x + (1 if state == "curtain" else 0), top + 1 if arched else top, x + 1, top + 2, refl)
        elif v == 1:
            px(L, x + 3, top + 2, refl); px(L, x + 4, top + 1, refl); px(L, x + 3, mid + 2, refl)
        else:
            rect(L, x + 3, top + h - 3, x + 4, top + h - 2, "w1"); px(L, x + 1, top + 1, refl)
    elif lit:
        rect(L, x, top + 1 if arched else top, x + 1, top + 2, refl)
    rect(L, x, top + (1 if arched else 0), x + 5, top + (1 if arched else 0), "w0" if not lit else "au0")
    rect(L, x, top + 1, x, top + h - 1, "w0" if not lit else "au0")      # west-jamb reveal shadow
    rect(L, x - 2, top + h + 1, x + 7, top + h + 1, "m6" if front else "m5")    # sill
    rect(L, x - 1, top + h + 2, x + 6, top + h + 2, "m2")


def hood(L, x, top, pediment, front):
    """Cornice hood over an upper-storey window (6 px wide); wings carry a small pediment."""
    hi = "m6" if front else "m5"
    rect(L, x - 2, top - 3, x + 7, top - 3, hi)
    rect(L, x - 1, top - 2, x + 6, top - 2, "m2")
    if pediment:
        rect(L, x, top - 4, x + 5, top - 4, hi); rect(L, x + 2, top - 5, x + 3, top - 5, hi)


def section_rows(kind, d):
    return {"roof": (ROOF[0], BAL[0] + d - 1), "bal": (BAL[0] + d, BAL[1] + d), "corn": (CORN[0] + d, CORN[1] + d),
            "up": (UP[0] + d, UP[1] + d), "string": (STRING[0] + d, STRING[1] + d), "low": (LOW[0] + d, LOW[1] + d),
            "plinth": (PLINTH[0] + d, PLINTH[1] + d + (3 if kind == "wing" else 0))}


WEST_X0 = {"wing": 150, "link": 208}
WING_BAYS = (8, 26, 43)            # window left-x offsets inside the west wing (east wing mirrored)
WING_PILS = (1, 19, 36, 54)        # 3-px pilasters
LINK_BAYS = (7, 23, 39, 55)
CENTRE_BAYS = (290, 304, 317, 330, 344)


def paint_section(L, kind, x0, x1, d, side):
    r = section_rows(kind, d)
    front = kind != "link"
    wall, joint = ("m4", "m3") if front else ("m3", "m2")

    def X(o, w):
        xw = WEST_X0[kind] + o
        return xw if side == 0 else mirror(xw, w)

    for y in range(r["roof"][0], r["roof"][1] + 1):                    # roof from above, hipped at wing ends
        inset = max(0, ROOF[0] + 7 - y) if kind == "wing" else 0
        xa, xb = (x0 + inset, x1) if side == 0 else (x0, x1 - inset)
        rect(L, xa, y, xb, y, "r1" if (y - ROOF[0]) % 3 else "r0")
        for x in range(x0 + 3, x1 + 1, 7):
            if xa <= x <= xb and y >= r["roof"][0] + 2 and L[y, x] == I["r1"]:
                L[y, x] = I["r0"]
    rect(L, x0, r["roof"][1], x1, r["roof"][1], "r2")
    rect(L, x0, r["corn"][0], x1, r["plinth"][0] - 1, wall)
    for y in range(r["low"][0] + 3, r["low"][1], 4):
        rect(L, x0, y, x1, y, joint)
    rect(L, x0, r["plinth"][0], x1, r["plinth"][1], "m2")
    rect(L, x0, r["plinth"][0], x1, r["plinth"][0], "m4" if front else "m3")
    if kind == "wing":
        rect(L, x0, r["plinth"][0] + 2, x1, r["plinth"][0] + 2, "m3")
    rect(L, x0, r["string"][0], x1, r["string"][0], "m5"); rect(L, x0, r["string"][0] + 1, x1, r["string"][0] + 1, "m4")
    rect(L, x0, r["string"][1], x1, r["string"][1], "m2")
    rect(L, x0, r["corn"][0], x1, r["corn"][0], "m6"); rect(L, x0, r["corn"][0] + 1, x1, r["corn"][0] + 1, "m4")
    rect(L, x0, r["corn"][0] + 2, x1, r["corn"][0] + 2, "m1")
    for x in range(x0, x1 + 1):
        px(L, x, r["corn"][1], "m4" if x % 2 == 0 else "m2")
    rect(L, x0, r["bal"][0], x1, r["bal"][0], "m6"); rect(L, x0, r["bal"][0] + 1, x1, r["bal"][0] + 1, "m3")
    for x in range(x0, x1 + 1):
        rect(L, x, r["bal"][0] + 2, x, r["bal"][1] - 1, ("m5", "m3", "m0")[x % 3])
    rect(L, x0, r["bal"][1], x1, r["bal"][1], "m4")
    if kind == "wing":
        for o in WING_PILS:
            x = X(o, 3)
            rect(L, x, r["up"][0], x + 1, r["low"][1], "m5"); rect(L, x + 2, r["up"][0], x + 2, r["low"][1], "m3")
            rect(L, x - 1, r["up"][0], x + 3, r["up"][0], "m6"); rect(L, x - 1, r["up"][0] + 1, x + 3, r["up"][0] + 1, "m4")
            rect(L, x - 1, r["low"][0], x + 3, r["low"][0], "m5")
            rect(L, x, r["bal"][0] - 1, x + 2, r["bal"][1], "m4"); rect(L, x, r["bal"][0] - 1, x + 2, r["bal"][0] - 1, "m6")
            rect(L, x + 2, r["bal"][0], x + 2, r["bal"][1], "m2")
        cx0 = X(12, 5)                                               # chimney stack on the wing roof
        rect(L, cx0, ROOF[0] - 6, cx0 + 4, ROOF[0] + 3, "m2"); rect(L, cx0, ROOF[0] - 6, cx0 + 1, ROOF[0] + 3, "m3")
        rect(L, cx0 - 1, ROOF[0] - 7, cx0 + 5, ROOF[0] - 6, "m4")
        bays, ped = WING_BAYS, True
    else:
        sx = X(22, 16)                                               # skylight on the link roof
        rect(L, sx, 51, sx + 15, 55, "k1"); rect(L, sx + 1, 52, sx + 14, 54, "c3"); rect(L, sx + 8, 52, sx + 14, 54, "w2")
        bays, ped = LINK_BAYS, False
    for bi, o in enumerate(bays):
        x = X(o, 6)
        facade_window(L, x, r["up"][0] + 7, 13, False, (kind, side, "up", bi), front)
        hood(L, x, r["up"][0] + 7, ped, front)
        facade_window(L, x, r["low"][0] + 6, 16, True, (kind, side, "low", bi), front)


def paint_centre(L):
    kind, x0, x1, d = SECTIONS[2]
    r = section_rows(kind, d)
    for y in range(r["roof"][0], r["roof"][1] + 1):
        rect(L, x0, y, x1, y, "r1" if (y - ROOF[0]) % 3 else "r0")
    rect(L, x0, r["roof"][1], x1, r["roof"][1], "r2")
    rect(L, x0, r["corn"][0], x1, r["plinth"][1], "m4")
    for y in range(r["low"][0] + 3, r["low"][1], 4):
        rect(L, x0, y, x1, y, "m3")
    rect(L, x0, r["plinth"][0], x1, r["plinth"][1], "m2"); rect(L, x0, r["plinth"][0], x1, r["plinth"][0], "m4")
    rect(L, x0, r["corn"][0], x1, r["corn"][0], "m6"); rect(L, x0, r["corn"][0] + 1, x1, r["corn"][0] + 1, "m4")
    rect(L, x0, r["corn"][0] + 2, x1, r["corn"][0] + 2, "m1")
    for x in range(x0, x1 + 1):
        px(L, x, r["corn"][1], "m4" if x % 2 == 0 else "m2")
    rect(L, x0, r["bal"][0], x1, r["bal"][0], "m6"); rect(L, x0, r["bal"][0] + 1, x1, r["bal"][0] + 1, "m3")
    for x in range(x0, x1 + 1):
        rect(L, x, r["bal"][0] + 2, x, r["bal"][1] - 1, ("m5", "m3", "m0")[x % 3])
    rect(L, x0, r["bal"][1], x1, r["bal"][1], "m4")
    for qx, lit in ((x0, True), (x1 - 2, False)):                     # pavilion quoins
        for y in range(r["corn"][1] + 1, r["plinth"][0], 3):
            rect(L, qx, y, qx + 2, min(y + 1, r["plinth"][0] - 1), ("m5" if lit else "m3") if (y // 3) % 2 else "m4")
    for x in PORT_COLS:                                               # upper-storey Corinthian pilasters
        rect(L, x, r["up"][0], x + 1, r["up"][1], "m5"); rect(L, x + 2, r["up"][0], x + 2, r["up"][1], "m3")
        rect(L, x - 1, r["up"][0], x + 3, r["up"][0], "m6"); rect(L, x - 1, r["up"][0] + 1, x + 3, r["up"][0] + 1, "m4")
        px(L, x - 1, r["up"][0] + 1, "m6"); px(L, x + 3, r["up"][0] + 1, "m3")
    for bi, x in enumerate(CENTRE_BAYS):
        if x == 317:
            facade_window(L, x, r["up"][0] + 6, 15, True, ("centre", 0, "up", bi), True)
        else:
            facade_window(L, x, r["up"][0] + 7, 13, False, ("centre", 0, "up", bi), True)
            hood(L, x, r["up"][0] + 7, False, True)


def paint_portico(L):
    """Columned entrance portico (+7 rows): terrace balustrade, entablature, dark loggia with arched openings and the
    lit door, six Ionic columns with their shadows on the loggia wall, porch podium."""
    xa, xb = PORTICO[0] - 2, PORTICO[1] + 2
    rect(L, xa, 98, xb, 98, "m6")
    for x in range(xa, xb + 1):
        rect(L, x, 99, x, 101, ("m5", "m3", "m0")[x % 3])
    rect(L, xa, 102, xb, 102, "m4")
    for x in PORT_COLS:
        rect(L, x, 97, x + 3, 102, "m5"); rect(L, x, 97, x + 3, 97, "m6"); rect(L, x + 3, 98, x + 3, 102, "m3")
    rect(L, xa, 103, xb, 103, "m6"); rect(L, xa, 104, xb, 104, "m4"); rect(L, xa, 105, xb, 105, "m2")
    rect(L, xa, 106, xb, 133, "m1")
    for y in range(110, 134, 5):
        rect(L, xa, y, xb, y, "m0")
    for (a, b) in ((288, 297), (302, 311), (316, 323), (328, 337), (342, 351)):
        if a == 316:
            rect(L, 317, 112, 322, 131, "wl"); rect(L, 318, 110, 321, 111, "wl"); rect(L, 318, 108, 321, 109, "wl2")
            rect(L, 317, 112, 318, 131, "wl2"); rect(L, 320, 113, 320, 131, "au0")
        else:
            c = (a + b) // 2
            rect(L, c - 2, 113, c + 2, 131, "w0"); rect(L, c - 1, 112, c + 1, 112, "w0"); rect(L, c - 2, 114, c - 1, 116, "w2")
    for x in PORT_COLS:
        for i, c in enumerate(("m5", "m6", "m4", "m2")):
            rect(L, x + i, 108, x + i, 131, c)
        rect(L, x - 1, 106, x + 4, 106, "m6"); rect(L, x - 1, 107, x + 4, 107, "m4")
        px(L, x - 1, 107, "m5"); px(L, x + 4, 107, "m2")
        rect(L, x - 1, 132, x + 4, 133, "m4"); rect(L, x - 1, 133, x + 4, 133, "m2")
        rect(L, x + 4, 108, x + 5, 131, "m0")
    rect(L, xa - 2, 134, xb + 2, 134, "m5"); rect(L, xa - 2, 135, xb + 2, 135, "m4")
    rect(L, xa - 2, 136, xb + 2, 137, "m3"); rect(L, xa - 2, 138, xb + 2, 138, "m2")


def paint_cupola(L):
    c = 319.5
    rect(L, 300, 38, 339, 57, "m4"); rect(L, 300, 38, 302, 57, "m5"); rect(L, 337, 38, 339, 57, "m2")
    rect(L, 298, 36, 341, 36, "m6"); rect(L, 298, 37, 341, 37, "m3"); rect(L, 300, 38, 339, 38, "m2")
    rect(L, 314, 43, 325, 56, "m1"); rect(L, 315, 42, 324, 42, "m1"); rect(L, 317, 41, 322, 41, "m1")
    for y in range(44, 56, 2):
        rect(L, 315, y, 324, y, "m2")
    rect(L, 313, 41, 313, 56, "m5"); rect(L, 326, 41, 326, 56, "m3")
    for wx in (305, 331):
        rect(L, wx, 46, wx + 2, 48, "w0"); px(L, wx, 46, "w2")
    for x in range(306, 334):
        u = (x + 0.5 - c) / 14
        v = cyl(u)
        col = tone(["m1", "m2", "m3", "m4", "m5", "m6"], v, (0.05, 0.22, 0.38, 0.52, 0.66))
        rect(L, x, 24, x, 35, col)
        if int(round((x + 0.5 - c) / 4.6)) % 2 == 0 and abs(u) < 0.95 and abs(x + 0.5 - c) > 6:
            rect(L, x, 26, x, 34, shift_of(["m0", "m1", "m2", "m3", "m4", "m5", "m6"], col, -2))
    for y in range(25, 35):
        for x in range(314, 326):
            d = math.hypot(x + 0.5 - c, (y + 0.5 - 29.5) * 1.05)
            if d <= 4.6:
                px(L, x, y, "m6")
            elif d <= 5.6:
                px(L, x, y, "au1" if x < c else "au0")
    rect(L, 319, 26, 320, 29, "k0"); rect(L, 320, 29, 322, 30, "k0")
    rect(L, 304, 22, 335, 22, "m6"); rect(L, 304, 23, 335, 23, "m2")
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
    # Justice figure on the cupola (scales west, sword east), cut by the frame top like the towers behind it
    stamp(L, 316, 0, ["b.AA.s", "baAAas", "..AA..", ".aAAa.", "aaAAaa"], {"A": "au2", "a": "au1", "b": "au0",
                                                                        "s": "m6"})
    for y in range(0, 48):                                           # shade-side outline against the city behind
        row = np.nonzero(np.isin(L[y, 296:344], [I[n] for n in ("m1", "m2", "m3", "m4", "m5", "m6")]))[0]
        if len(row):
            px(L, 296 + row.max() + 1, y, "m0")


def paint_city_hall():
    """Central pavilion (+3 rows), two projecting wings (+9), recessed links, columned entrance portico (+7), domed
    clock tower. Drawn back to front; wing / pavilion shadows fall on the recessed walls east of them."""
    L = new()
    for kind, x0, x1, d in SECTIONS:
        if kind == "link":
            paint_section(L, kind, x0, x1, d, 0 if x0 < CX else 1)
    paint_centre(L)
    for kind, x0, x1, d in SECTIONS:
        if kind == "wing":
            paint_section(L, kind, x0, x1, d, 0 if x0 < CX else 1)
    shade_region(L, box(208, BAL[0], 216, PLINTH[1]) & ((XX - 208) < 4 + (YY - BAL[0])))   # west wing's shadow
    shade_region(L, box(364, BAL[0], 366, PLINTH[1]))                                       # pavilion's shadow
    shade_region(L, box(360, 102, 363, PLINTH[1] + 3))                                      # portico's shadow
    for kind, x0, x1, d in SECTIONS:                                 # cornice shadow band on the upper wall
        r = section_rows(kind, d)
        wall = I["m4"] if kind != "link" else I["m3"]
        shade_region(L, box(x0, r["up"][0] + 1, x1, r["up"][0] + 2) & (L == wall))
        shade_region(L, box(x0, r["plinth"][0] - 2, x1, r["plinth"][0] - 1) & (L == wall))   # splash grime
    for (x, y0, y1) in STREAKS:
        shade_region(L, box(x, y0, x, y1) & np.isin(L, [I["m4"], I["m3"]]))
    paint_portico(L)
    paint_cupola(L)
    haze(L)
    return L


def haze(L, mask=None):
    """Aerial perspective: remap the backdrop's marble / roof / glass colours to their hazed twins (HAZE table)."""
    lut = np.arange(len(ALL_PAL), dtype=np.int16)
    for a, b in HAZE.items():
        lut[I[a]] = I[b]
    sel = (L >= 0) if mask is None else (mask & (L >= 0))
    L[sel] = lut[L[sel]]


# ============================================================================ forecourt (backdrop scale) and gate
LAWN_LIGHT = [(178, 196, 44, 12), (468, 204, 50, 14), (520, 306, 40, 12), (372, 318, 22, 7), (250, 304, 20, 7),
              (184, 152, 40, 9), (452, 152, 36, 9)]
LAWN_DAMP = [(136, 186, 30, 9), (580, 226, 24, 8), (80, 318, 18, 8), (420, 162, 18, 5)]
TUFT = {"near": ((0, 0, 1), (-1, 1, 1), (0, 1, 1), (0, 2, -1), (1, 2, -1)),
        "mid": ((0, 0, 1), (1, 0, 1), (1, 1, -1), (2, 1, -1)),
        "far": ((0, 0, 1), (1, 0, 1))}
TUFT_LAT = {"near": (6, 4), "mid": (5, 3), "far": (4, 3)}
TUFT_ROWS = {"far": (0, 149), "mid": (150, 199), "near": (200, H - 1)}
JIT = ((0, 2), (3, 1), (1, 3), (4, 0), (2, 2), (5, 1))             # fixed lattice offsets, cycled per cell
MOWN = [(452, 196, 44, 9), (570, 228, 26, 7), (104, 186, 34, 8), (520, 326, 34, 6), (112, 312, 22, 6),
        (236, 192, 22, 5), (400, 296, 26, 6)]                         # v03: hand-placed tuft-free (mown) patches


def grass(L, mask, key):
    """Lawn: hand-placed sunlit and damp zones (2x2 checker borders) and a hand-drawn tuft motif on a fixed staggered
    lattice. Tufts shrink with distance (3-row near tufts, 2-row mid, 2-px far ticks) so lawns recede toward City
    Hall instead of ending in a band."""
    chk = (XX // 2 + YY // 2) % 2 == 0
    base = np.full((H, W), I["g2"], np.int16)
    for (zx, zy, rx, ry) in LAWN_LIGHT:
        e = ((XX + 0.5 - zx) / rx) ** 2 + ((YY + 0.5 - zy) / ry) ** 2
        base[(e <= 0.8) | ((e <= 1.0) & chk)] = I["g3"]
    for (zx, zy, rx, ry) in LAWN_DAMP:
        e = ((XX + 0.5 - zx) / rx) ** 2 + ((YY + 0.5 - zy) / ry) ** 2
        base[(e <= 0.8) | ((e <= 1.0) & chk)] = I["g1"]
    L[mask] = base[mask]
    ramp = [I[c] for c in ("g0", "g1", "g2", "g3", "g4")]
    order = {c: i for i, c in enumerate(ramp)}
    for kind, (r0, r1) in TUFT_ROWS.items():
        cw, ch = TUFT_LAT[kind]
        for gy in range(r0 // ch, r1 // ch + 1):
            for gx in range(0, W // cw + 1):
                if (gx * 5 + gy * 3) % 7 == 0:
                    continue
                if any(((gx * cw + 0.5 - mx) / mrx) ** 2 + ((gy * ch + 0.5 - my) / mry) ** 2 <= 1.0
                       for mx, my, mrx, mry in MOWN):
                    continue                                          # v03: freshly mown patches break the lattice
                jx, jy = JIT[(gx + 2 * gy) % 6]
                x, y = gx * cw + jx % cw, gy * ch + jy % ch
                if not (r0 <= y <= r1) or not (0 < x < W - 1) or y + 2 >= H or not mask[y, x]:
                    continue
                b = order.get(int(L[y, x]), 2)
                for dx, dy, d in TUFT[kind]:
                    if mask[y + dy, x + dx]:
                        L[y + dy, x + dx] = ramp[max(0, min(4, b + d))]


def hedge_strip(L, xa, xb, y0, y1):
    """Clipped box border at the building base: lit top row with 2-px sprigs every 7 px, notches every 16 px."""
    rect(L, xa, y0, xb, y1, "f3")
    rect(L, xa, y0, xb, y0, "f4")
    for x in range(xa + 2, xb, 7):
        rect(L, x, y0, x + 1, y0, "f5")
    rect(L, xa, y1, xb, y1, "f1")
    for x in range(xa + 8, xb - 2, 16):
        rect(L, x, y0 + 1, x, y1 - 1, "f2")


BORDER_BLOOMS = [(160, 145, "fl1"), (163, 146, "fl3"), (181, 145, "fl2"), (199, 145, "fl1"), (444, 145, "fl4"),
                 (461, 146, "fl3"), (478, 145, "fl1"), (220, 133, "fl2"), (253, 133, "fl1"), (384, 133, "fl1"),
                 (414, 133, "fl2")]
LANDING_COURSES = [((158, 159), (5, 4, 6, 5, 4, 6)), ((160, 162), (7, 6, 8, 6, 7)), ((163, 166), (9, 11, 8, 10)),
                   ((167, 171), (13, 11, 15, 12, 14))]


def lobe_shadow_mask(t, clip=None):
    """Ground shadow of a tree: every lobe projected along the sun (+x, -y per row of height), flattened."""
    bx, b = t["base"]
    sm = np.zeros((H, W), bool)
    cx, cy = t["c"]
    for dx, dy, r in t["lobes"]:
        z = b - (cy + dy)
        sm |= ell(cx + dx + SUN[0] * z, b - SUN[1] * z, r * 0.95, r * 0.45)
    zt = b - cy
    sm |= seg((bx, b), (bx + SUN[0] * zt, b - SUN[1] * zt), 2.5)
    return sm if clip is None else sm & clip


def paint_forecourt():
    L = new()
    lawn = box(64, 40, PARK_ROW - 1, WALK_TOP - 1)
    grass(L, lawn, "forecourt")
    for (xa, xb, y0, y1) in ((152, 205, 144, 147), (434, 487, 144, 147), (210, 273, 132, 135), (366, 429, 132, 135)):
        hedge_strip(L, xa, xb, y0, y1)
        shade_region(L, box(xa - 1, y1 + 1, xb + 1, y1 + 1))                # contact shade under the border
    for (x, y, c) in BORDER_BLOOMS:
        rect(L, x, y, x + 1, y, c); px(L, x, y + 1, c); px(L, x + 1, y + 1, "f2")
    shade_region(L, box(208, 132, 216, 143) & (L >= 0))                      # west wing's ground shadow
    # grand stair: graded risers (2-row far steps at the portico, 4-row near steps), splaying toward the gate
    y = STAIR_TOP
    for k, h in enumerate(STAIR_RISERS):
        xa, xb = 276 - 2 * k, 363 + 2 * k
        rect(L, xa, y, xb, y, "m5")
        if h >= 2:
            rect(L, xa, y + 1, xb, y + 1, "m2")
        if h >= 3:
            rect(L, xa, y + 2, xb, y + h - 1, "m3")
        px(L, xa, y, "m6")
        y += h
    for (a, b, lit) in ((256, 263, True), (376, 383, False)):               # cheek blocks
        rect(L, a, 139, b, 157, "m4" if lit else "m3"); rect(L, a, 139, b, 140, "m6" if lit else "m5")
        rect(L, a, 157, b, 157, "m2"); rect(L, b, 141, b, 156, "m3" if lit else "m2")
    # landing and forecourt walk inside the gate: courses thin with distance (5 -> 2 rows), slabs shorten
    for ci, ((ya, yb), widths) in enumerate(LANDING_COURSES):
        x, k = 256 - (ci * 3) % 7, 0
        while x <= 383:
            w = widths[k % len(widths)]
            t = ("p4", "p3", "p4", "p4", "p3")[(k + ci) % 5]
            rect(L, max(256, x + 1), ya + 1, min(383, x + w - 1), yb, t)
            if yb - ya >= 2:
                rect(L, max(256, x + 1), ya + 1, min(383, x + 2), ya + 1, "p5" if t == "p4" else "p4")
            rect(L, max(256, x), ya, min(383, x + w - 1), ya, "p2")
            if 256 <= x <= 383:
                rect(L, x, ya, x, yb, "p2")
            x += w
            k += 1
    rect(L, 280, 170, 359, 170, "t0")                                        # access light line (2537)
    for x in range(282, 358, 6):
        rect(L, x, 170, x + 1, 170, "t1")
    # shadows on the forecourt ground: gate piers, railing top rails, mid-distance trees
    sh = np.zeros((H, W), bool)
    for (a, b) in GATE_PIERS:
        for yy in range(162, WALK_TOP):
            s = (WALK_TOP - 1 - yy) * SUN[0] / SUN[1]
            sh |= box(int(a + s), yy, int(b + s), yy)
        sh |= ell((a + b) / 2 + SUN[0] * 56, WALK_TOP - 1 - SUN[1] * 56, 4, 1.5)
    for (a, b) in RAILS:
        sh |= box(a + 7, 166, b + 7, 166)
    for t in MID_TREES:
        sh |= lobe_shadow_mask(t)
    shade_region(L, sh & lawn & (YY >= 136))
    haze(L, YY < 146)                                                # far treads and cheek tops share the building's haze
    return L


def visitor(L, x, b, coat, hair):
    """Door-scaled visitor (10 rows: the lit door is 20 rows tall) on the City Hall stair -- a human yardstick that
    makes the facade read large and far instead of model-sized."""
    rows = [".hh.", ".ff.", "cCCc", "cCCc", "cCCc", ".CC.", ".CC.", ".LL.", ".LL.", ".L.L"]
    stamp(L, x - 2, b - len(rows) + 1, rows, {"h": hair, "f": "hu1", "c": coat, "C": coat, "L": "w1"})
    px(L, x - 2, b - 7, "hm5" if coat != "m1" else "hm3")             # sunlit west shoulder


def paint_forecourt_near():
    L = new()
    for (x, b, coat, hair) in VISITORS:
        visitor(L, x, b, coat, hair)
    for t in MID_TREES:
        paint_tree(L, t)
    for x, kind in FLAGS:                                            # flagpoles with the U.S. and NYC flags
        rect(L, x, FLAG_TOP, x, FLAG_BASE, "m5"); rect(L, x + 1, FLAG_TOP, x + 1, FLAG_BASE, "m3")
        rect(L, x - 1, FLAG_BASE - 1, x + 2, FLAG_BASE, "m2"); px(L, x, FLAG_TOP - 1, "au2")
        fx0, fy0, fw, fh = x + 2, FLAG_TOP + 2, 17, 11
        for i in range(fw):
            dy = 1 if 5 <= i <= 10 else 0
            for j in range(fh):
                if kind == "us":
                    col = "fr" if j % 2 == 0 else "m6"
                    if i < 7 and j < 6:
                        col = "fb" if (i + j) % 3 else "m6"
                else:
                    col = "fb" if i < 6 else ("m6" if i < 12 else "fo")
                    if (i, j) in ((8, 4), (9, 5), (8, 6), (9, 4)):
                        col = "fb"
                px(L, fx0 + i, fy0 + j + dy, col)
            px(L, fx0 + i, fy0 + fh + dy, "m2" if i % 3 else "m1")
    for ex in (RAILS[0][0] - 4, RAILS[1][1] + 1):                    # granite end posts with ball finials
        rect(L, ex, 138, ex + 3, 171, "m4"); rect(L, ex, 138, ex, 171, "m5"); rect(L, ex + 3, 138, ex + 3, 171, "m2")
        rect(L, ex - 1, 136, ex + 4, 137, "m6"); rect(L, ex - 1, 137, ex + 4, 137, "m3")
        stamp(L, ex, 133, [".ab.", "abbc", ".cc."], {"a": "m6", "b": "m4", "c": "m2"})
    for (xa, xb) in RAILS:                                           # hero-scale iron railings on a granite curb
        rect(L, xa, 167, xb, 171, "m3"); rect(L, xa, 167, xb, 167, "m5"); rect(L, xa, 171, xb, 171, "m2")
        rect(L, xa, 164, xb, 164, "k2"); rect(L, xa, 165, xb, 165, "k1")
        for x in range(xa + 1, xb, 4):
            rect(L, x, 145, x, 166, "k1"); rect(L, x - 1, 145, x + 1, 145, "k1"); px(L, x, 143, "k2"); px(L, x, 144, "k2")
        rect(L, xa, 147, xb, 147, "k3"); rect(L, xa, 148, xb, 148, "k1")
    for t in SHRUBS:
        paint_tree(L, t)
    for (a, b) in GATE_PIERS:                                        # hero-scale granite gate piers with lanterns
        rect(L, a - 1, 164, b + 1, 171, "m3"); rect(L, a - 1, 164, b + 1, 164, "m5"); rect(L, a - 1, 171, b + 1, 171, "m2")
        rect(L, a - 1, 165, a - 1, 170, "m4")
        rect(L, a, 134, b, 163, "m4"); rect(L, a, 134, a + 1, 163, "m5"); rect(L, b, 134, b, 163, "m2")
        rect(L, a + 3, 138, b - 3, 159, "m3")
        rect(L, a + 3, 138, b - 3, 138, "m2"); rect(L, a + 3, 139, a + 3, 159, "m2")
        rect(L, a + 4, 159, b - 3, 159, "m5"); rect(L, b - 3, 139, b - 3, 158, "m5")
        mid = (a + b) // 2
        rect(L, mid, 141, mid, 156, "t0"); px(L, mid, 141, "t2"); px(L, mid, 146, "t1"); px(L, mid, 151, "t1")
        rect(L, a - 2, 128, b + 2, 128, "m6"); rect(L, a - 2, 129, b + 2, 130, "m4"); rect(L, a - 2, 129, a - 1, 130, "m5")
        rect(L, a - 1, 131, b + 1, 131, "m2"); rect(L, a, 132, b, 133, "m4"); rect(L, b, 132, b, 133, "m2")
        lc = mid
        rect(L, lc - 2, 126, lc + 3, 127, "k1"); rect(L, lc, 122, lc + 1, 125, "k2")
        rect(L, lc - 3, 113, lc + 4, 121, "k1")
        rect(L, lc - 2, 114, lc + 3, 120, "wl"); rect(L, lc - 2, 114, lc - 1, 117, "wl2"); rect(L, lc + 1, 114, lc + 1, 120, "au0")
        rect(L, lc - 4, 112, lc + 5, 112, "k2"); rect(L, lc - 3, 111, lc + 4, 111, "k1"); rect(L, lc, 109, lc + 1, 110, "k2")
    return L


# ============================================================================ park ground (hero scale)
def park_masks():
    m = {}
    m["axis"] = box(AXIS[0], WALK_TOP, AXIS[1], H - 1)
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
    park = box(64, WALK_TOP, PARK_ROW - 1, H - 1) | m["south"]
    m["granite"] = (m["axis"] | m["south"] | m["plaza"] | m["statue_c"]) & ~m["basin"]
    m["hex"] = (m["diag"] | m["east_conn"] | m["s_conn"] | m["w_gate"] | m["statue_walk"] | m["e_walk"]) & \
        ~m["granite"] & ~m["basin"]
    m["path"] = (m["granite"] | m["hex"]) & (YY >= WALK_TOP)
    m["lawn"] = park & ~m["path"] & ~m["basin"] & (YY >= WALK_TOP)
    return m


SLAB_TONES = ("p3", "p3", "p4", "p3", "p2", "p3", "p4", "p3")
WIDTHS = (14, 10, 18, 12, 16, 9, 13, 15, 11, 17)
LIT_STEP = {"p2": "p3", "p3": "p4", "p4": "p5"}


def flags(L, mask, y0, y1, course_h, key, widths=WIDTHS, tones=SLAB_TONES, joint="p2"):
    """Granite flag courses with irregular slab lengths; each slab's tone is picked from a short hand table, and it
    gets one 4-px L-shaped bevel highlight at its north-west corner (no per-texel speckle)."""
    for c, ya in enumerate(range(y0, y1 + 1, course_h)):
        off = int(hval(key, "off", c) * 23)
        k = int(hval(key, "ph", c) * len(widths))
        x = -off
        while x < W:
            w = widths[k % len(widths)]
            t = tones[int(hval(key, c, k) * len(tones))]
            L[mask & box(x + 1, ya + 1, x + w - 1, ya + course_h - 1)] = I[t]
            L[mask & (box(x + 1, ya + 1, x + 3, ya + 1) | box(x + 1, ya + 2, x + 1, ya + 2))] = I[LIT_STEP[t]]
            L[mask & (box(x, ya, x, ya + course_h - 1) | box(x, ya, x + w - 1, ya))] = I[joint]
            x += w
            k += 1


def hex_pavers(L, mask, key="hex", sx=10, sy=6):
    """NYC park hexagonal pavers: Voronoi cells of a hex lattice squashed for the 3/4 view, mortar on cell borders,
    a lit upper lip on each block; block tone picked per cell from a short hand table."""
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


def paint_park_ground():
    L = new()
    m = park_masks()
    grass(L, m["lawn"], "lawn")
    gm = m["granite"] & (YY >= WALK_TOP)
    axis_s = (m["axis"] | m["south"]) & ~m["plaza"] & gm
    flags(L, axis_s & m["axis"] & ~m["south"], WALK_TOP, 337, 8, "axis")
    flags(L, axis_s & m["south"], 338, 359, 11, "south", widths=(22, 16, 28, 19, 25, 17, 24))
    cx, cy = FOUNTAIN                                                # fountain plaza: radial granite rings
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
    hi = (~ring_joint) & (~rad_joint) & (frac < 0.32) & (rr <= 0.95) & (out == I["p3"]) & ((k + seg_id) % 3 == 0)
    out = np.where(hi, I["p4"], out)
    L[ys, xs] = out
    sc = m["statue_c"] & ~m["plaza"]                                 # statue circle with a compass ring
    flags(L, sc, 240, 292, 7, "statue", widths=(9, 12, 8, 11, 10))
    sx0, sy0, srx, sry = STATUE_C
    ring = sc & ~ell(sx0, sy0, srx - 2, sry - 1.5)
    L[ring] = I["p2"]
    L[ring & edge_above(sc)] = I["p4"]
    hex_pavers(L, m["hex"] & (YY >= WALK_TOP))
    lawn, path = m["lawn"], m["path"]                                # granite curbs, lit on the north side
    up = np.zeros_like(path); up[1:] = path[1:] & lawn[:-1]
    dn = np.zeros_like(path); dn[:-1] = path[:-1] & lawn[1:]
    lf = np.zeros_like(path); lf[:, 1:] = path[:, 1:] & lawn[:, :-1]
    rt = np.zeros_like(path); rt[:, :-1] = path[:, :-1] & lawn[:, 1:]
    L[up | lf] = I["p5"]
    L[dn | rt] = I["p2"]
    gl = np.zeros_like(lawn); gl[:-1] = lawn[:-1] & path[1:]
    L[gl] = I["g1"]
    return L


# ============================================================================ wear (every mark hand placed)
CRACKS = [[(298, 186), (301, 189), (301, 193), (304, 196)], [(340, 206), (337, 210), (338, 215)],
          [(308, 248), (312, 250), (317, 250), (319, 253)], [(330, 318), (333, 315), (338, 315)],
          [(196, 232), (200, 229), (205, 229)], [(128, 298), (131, 302), (131, 305)],
          [(452, 350), (456, 347), (462, 347), (465, 344)], [(560, 352), (563, 355), (568, 355)],
          [(470, 286), (474, 289)], [(306, 340), (309, 344), (309, 349)]]
STAINS = [(382, 259, 9, 2), (342, 262, 4, 2), (488, 350, 10, 2), (322, 175, 9, 2), (566, 347, 4, 2),
          (596, 300, 3, 6), (186, 330, 6, 2), (240, 352, 6, 2)]
PATCHES = [(300, 254, 313, 261), (326, 186, 339, 192), (500, 344, 522, 353)]
MOSS_BOXES = [(292, 172, 300, 250), (64, 236, 150, 262), (346, 300, 347, 337)]
SUNKEN = [(270, 216), (522, 266), (588, 314), (79, 270)]
TURF = [("ell", 100, 207, 13, 4), ("line", [(88, 252), (95, 257), (104, 258)], 2), ("ell", 262, 331, 8, 2),
        ("ell", 540, 241, 9, 2), ("ell", 462, 241, 6, 2), ("ell", 410, 301, 7, 2), ("line", [(286, 176), (282, 184),
                                                                                              (283, 192)], 2)]
LEAF = {"a": ["a.", ".b"], "b": [".a", "ab"], "c": ["ab"], "d": ["a", "b"]}
LITTER = [(118, 240, "a", "au0", "s1"), (104, 252, "b", "fl5", "au0"), (126, 246, "c", "e2", "s1"),
          (418, 262, "a", "au0", "s1"), (430, 271, "d", "fl5", "au0"), (396, 276, "b", "e2", "s1"),
          (560, 262, "c", "au0", "s1"), (548, 270, "a", "fl5", "au0"), (296, 318, "c", "pk1", "pk0"),
          (294, 326, "d", "pk1", "pk0"), (300, 331, "a", "pk2", "pk1"), (452, 262, "b", "y3", "y1"),
          (474, 270, "c", "y3", "y1"), (86, 296, "a", "au0", "s1")]


def paint_ground_wear():
    """Wear layer (separate so a painter can edit or hide it): hairline cracks, oil / damp stains, replaced slabs,
    moss in shaded joints, sunken hex pavers, trampled turf and mulch rings, small leaf / petal litter."""
    L = new()
    m = park_masks()
    pave = m["path"]
    g = paint_park_ground()                                         # read-only reference for joint detection
    for (x0, y0, x1, y1) in PATCHES:
        msk = box(x0, y0, x1, y1) & m["granite"]
        L[msk] = I["p4"]
        L[msk & ~box(x0 + 1, y0 + 1, x1 - 1, y1 - 1)] = I["p2"]
        L[msk & box(x0 + 1, y0 + 1, x0 + 3, y0 + 1)] = I["p5"]
    for (sx, sy, rx, ry) in STAINS:
        e = ((XX + 0.5 - sx) / rx) ** 2 + ((YY + 0.5 - sy) / ry) ** 2
        chk = (XX // 2 + YY // 2) % 2 == 0
        msk = ((e <= 0.7) | ((e <= 1.0) & chk)) & pave
        L[msk] = SHADE_LUT[np.clip(np.where(L[msk] >= 0, L[msk], g[msk]), 0, None)]
    for pts in CRACKS:
        poly(L, pts, "p1", m["granite"])
    near_lawn = dilate(m["lawn"], 2)
    for (x0, y0, x1, y1) in MOSS_BOXES:
        msk = box(x0, y0, x1, y1) & pave & near_lawn & np.isin(g, [I["p2"], I["x0"]])
        L[msk] = I["g1"]
    for (sx, sy) in SUNKEN:
        msk = ell(sx, sy, 4, 2.2) & m["hex"]
        L[msk] = I["x1"]
        L[msk & (edge_above(msk) | edge_below(msk))] = I["x0"]
    for t in TURF:
        if t[0] == "ell":
            _, sx, sy, rx, ry = t
            e = ((XX + 0.5 - sx) / rx) ** 2 + ((YY + 0.5 - sy) / ry) ** 2
            core = (e <= 0.55) & m["lawn"]
            rim = (e <= 1.0) & ~core & m["lawn"] & ((XX // 2 + YY // 2) % 2 == 0)
            L[core] = I["s1"] if rx <= 9 else I["e1"]
            L[core & edge_above(core)] = I["e2"]
            L[rim] = I["e2"] if rx > 9 else I["e1"]
        else:
            _, pts, hw = t
            msk = np.zeros((H, W), bool)
            for p, q in zip(pts, pts[1:]):
                msk |= seg(p, q, hw)
            msk &= m["lawn"]
            L[msk] = I["e1"]
            L[msk & edge_above(msk)] = I["e2"]
    for (x, y, shape, ca, cb) in LITTER:
        stamp(L, x, y, LEAF[shape], {"a": ca, "b": cb})
    return L


# ============================================================================ ground detail: beds, drains, wayfinding
PIGEON = {0: [".kg..", "kmmmx", "..mx."], 1: ["..gk.", "xmmmk", ".xm.."]}
PIGEONS = [(232, 349, 0), (241, 352, 1), (248, 347, 0), (146, 322, 1), (152, 325, 0)]


BEDS = [  # (ellipse parts, bloom drifts (cx, cy, rx, ry, lit colour, shade colour)); v03: grouped drifts, stone edge
    ([(186, 190, 22, 6), (210, 194, 14, 5)],
     [(176, 189, 9, 3.2, "pk2", "pk0"), (194, 191, 6, 3.0, "fl3", "p3"), (212, 195, 9, 3.0, "fl1", "fl0")]),
    ([(500, 232, 16, 5.5)], [(492, 231, 7, 3.0, "fl2", "au1"), (507, 233, 7, 3.0, "fl1", "fl0")]),
    ([(520, 306, 26, 7), (548, 302, 12, 5)],
     [(508, 305, 10, 3.6, "fl4", "fb"), (529, 308, 7, 3.2, "fl3", "p3"), (549, 302, 7, 2.8, "pk1", "pk0")]),
    ([(278, 300, 9, 4)], [])]


def bed(L, parts, drifts):
    """Planted bed that reads at 640x360: a 1-px granite edging (lit north / west), a thin mulch line, foliage
    clumps on a fixed 4x3 lattice, then solid bloom drifts -- each a shade-colour mass with a lit cap shifted up-left
    -- instead of v02's scattered bloom dots that averaged to a dark blob."""
    m = np.zeros((H, W), bool)
    inner = np.zeros((H, W), bool)
    soil = np.zeros((H, W), bool)
    for (cx, cy, rx, ry) in parts:
        m |= ell(cx, cy, rx, ry)
        soil |= ell(cx, cy, rx - 1, ry - 1)
        inner |= ell(cx, cy, rx - 2, ry - 1.6)
    edge = m & ~soil
    L[edge] = I["p2"]
    L[edge & (edge_above(m) | (XX < np.array([p[0] for p in parts]).mean()))] = I["p4"]
    L[soil & ~inner] = I["e1"]
    L[inner] = I["f3"]
    ys, xs = np.nonzero(inner)
    for y in range(ys.min(), ys.max() + 1, 3):                       # leaf clumps on a fixed 4x3 lattice
        for x in range(xs.min() + (2 if (y // 3) % 2 else 0), xs.max() + 1, 4):
            if inner[y, x] and y + 1 < H and inner[y + 1, x + 1]:
                stamp(L, x, y, ["ab", "bc"], {"a": "f5", "b": "f4", "c": "f2"})
    merge_orphans(L, inner)
    for (cx, cy, rx, ry, hi, lo) in drifts:
        d = ell(cx, cy, rx, ry) & inner
        L[d] = I[lo]
        L[d & ell(cx - 1, cy - 0.8, rx - 1.5, ry - 1.0)] = I[hi]
        L[d & edge_below(d)] = I["f2"]                                # foliage reads under each drift
        for y in range(int(cy - ry) + 1, int(cy + ry), 2):            # single blooms: shade ticks on a fixed
            for x in range(int(cx - rx) + 1 + (y % 4) // 2 * 2, int(cx + rx), 4):   # 4x2 staggered lattice
                if d[y, x] and d[y, x + 1] and L[y, x] == I[hi]:
                    L[y, x + 1] = I[lo]


def paint_ground_detail():
    L = new()
    m = park_masks()
    for parts, drifts in BEDS:
        bed(L, parts, drifts)
    for (x, y) in ((320, 266), (320, 338)):                          # teal wayfinding medallions (2537), not a seam
        stamp(L, x - 3, y - 2, [".ttt.", "tTsTt", ".ttt."], {"t": "t0", "T": "t1", "s": "t2"})
    for (x, y) in ((320, 324), (172, 332), (588, 300)):              # cast-iron drain grates
        rect(L, x - 4, y - 2, x + 3, y + 1, "k1"); rect(L, x - 4, y - 2, x + 3, y - 2, "k2")
        for xx in range(x - 3, x + 3, 2):
            rect(L, xx, y - 1, xx, y, "k0")
    for (x, y, f) in PIGEONS:
        stamp(L, x, y, PIGEON[f], {"k": "x0", "g": "bz2", "m": "m2", "x": "m1"})
    return L


# ============================================================================ fountain
def paint_fountain_basin():
    """Basin (base layer): granite coping lit from the south-west, outer wall face, water with a shaded north band,
    broken ripple arcs, a low inner tier and eight arching jets -- all low enough never to rise above the back rim."""
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
    wall = np.zeros((H, W), bool)
    for x in range(cx - BASIN_R[0], cx + BASIN_R[0] + 1):
        col = np.nonzero(out[:, x])[0]
        if len(col) and col.max() >= cy:
            for k in range(1, 4):
                wall[col.max() + k, x] = True
    L[wall] = I["m3"]
    L[wall & edge_below(wall)] = I["m2"]
    L[wall & ((XX % 9) == 0)] = I["m2"]
    L[inn] = I["c1"]
    L[inn & ~ell(cx, cy + 3, BASIN_IN[0] - 1, BASIN_IN[1] - 2) & (YY < cy)] = I["c0"]       # shade under north coping
    L[inn & edge_below(inn)] = I["c2"]
    ang = np.arctan2(YY + 0.5 - cy, XX + 0.5 - cx)
    for (rx, ry) in ((24, 11), (32, 16)):                            # broken ripple arcs (fixed 8-step pattern)
        ring = ell(cx, cy + 1, rx, ry) & ~ell(cx, cy + 1, rx - 1.2, ry - 1)
        L[inn & ring & (np.floor((ang + math.pi) / (math.pi / 8)) % 2 == 0)] = I["c2"]
    tier = ell(cx, cy + 1, 15, 7)
    tin = ell(cx, cy + 1, 12, 5)
    L[tier & ~tin] = I["m4"]
    L[tier & ~tin & (XX < cx) & (YY < cy + 1)] = I["m5"]
    L[tier & edge_above(tier)] = I["m6"]
    L[tier & edge_below(tier)] = I["m2"]
    L[tin] = I["c2"]
    L[tin & ell(cx - 3, cy - 1, 6, 2)] = I["c3"]
    for kk in range(8):                                              # arching jets, inner tier -> outer pool
        a = kk * math.pi / 4 + math.pi / 8
        sx, sy = cx + 15 * math.cos(a), cy + 1 + 7 * math.sin(a)
        ex, ey = cx + 29 * math.cos(a), cy + 1 + 14 * math.sin(a)
        for s in range(0, 11):
            t = s / 10
            x = sx + (ex - sx) * t
            y = sy + (ey - sy) * t - 5 * math.sin(math.pi * t)
            px(L, int(round(x)), int(round(y)), "c3")
            px(L, int(round(x)), int(round(y)) + 1, "c2")
        rect(L, int(round(ex)) - 1, int(round(ey)), int(round(ex)) + 1, int(round(ey)), "c3")
    return L


FOAM = ["...WWWW...",               # low foam crown bubbling on the upper bowl (hand drawn, 10 x 8): white core lit from
        ".WWWCCWC..",               # the south-west, blue body, shaded east side; wider than tall so it never reads
        "WWCCCCCCc.",               # as a staff or a jet crossing an actor
        "WCCCCCCCcc",
        "CCCCCCCccc",
        "cCCcCCcCcc",
        ".c.cCc.cc.",
        "..c..c..c."]
BOWL_TOP = 226                      # upper-bowl rim row (the solid tier an actor behind the fountain stands behind)


def fountain_sprite(L, reg=None):
    """Y-sorted two-tier centrepiece (v03): pedestal with mouldings rising from the inner tier, a wide upper bowl seen
    from above (rim, water surface, shaded body), overflow streams falling all round its front into the inner tier,
    and a low foam crown. A heroine directly behind it is hidden from the hips down by solid stone and falling water
    -- a readable 'behind' -- instead of being crossed by a thin vertical jet (v02 audit)."""
    cx, cy = FOUNTAIN
    for y in range(BOWL_TOP + 10, cy - 1):                           # pedestal with collar and base flare
        hw = 5 if y >= cy - 5 else (5 if y in (250, 251) else 4)
        for x in range(cx - hw, cx + hw):
            px(L, x, y, tone(["m2", "m3", "m4", "m5", "m6"], cyl((x + 0.5 - cx) / hw), (0.1, 0.3, 0.48, 0.62)), reg)
    rect(L, cx - 5, 250, cx + 4, 251, "m6", reg); rect(L, cx - 5, 252, cx + 4, 252, "m2", reg)
    rect(L, cx - 6, cy - 5, cx + 5, cy - 5, "m6", reg)
    for i, y in enumerate(range(BOWL_TOP + 4, BOWL_TOP + 11)):       # bowl body below the rim, tapering
        hw = (14, 13, 12, 10, 8, 6, 5)[i]
        for x in range(cx - hw, cx + hw):
            px(L, x, y, tone(["m2", "m3", "m4", "m5"], cyl((x + 0.5 - cx) / hw), (0.15, 0.36, 0.55)), reg)
        if i in (1, 4):
            rect(L, cx - hw, y, cx + hw - 1, y, "m2" if i == 4 else "m5", reg)
    rim = ell(cx, BOWL_TOP + 2, 15, 3.2)                              # rim ellipse seen from above, water inside
    water = ell(cx, BOWL_TOP + 2, 12.5, 1.9)
    for y, x in zip(*np.nonzero(rim)):
        px(L, x, y, "m6" if (y <= BOWL_TOP + 1 or x < cx - 8) else ("m4" if x > cx + 8 else "m5"), reg)
    for y, x in zip(*np.nonzero(water)):
        px(L, x, y, "c3" if x < cx - 4 and y <= BOWL_TOP + 2 else "c2", reg)
    for k, x in enumerate(range(cx - 12, cx + 12, 2)):                # overflow veil: a stream on every 2nd column
        y0 = BOWL_TOP + 6                                             # from under the rim (the rim projects past
        y1 = cy - 7 + (k % 3)                                         # it), so whatever stands behind shows half
        u = (x + 0.5 - cx) / 12                                       # through falling water
        col = "lw" if u < -0.6 else ("c3" if u < 0.0 else ("c2" if u < 0.6 else "c1"))
        for y in range(y0, y1 + 1):                                   # continuous streams (gaps made walk holes)
            px(L, x, y, col if (col != "lw" or (y + k) % 5) else "c3", reg)
        rect(L, x - 1, y1 + 1, x + 1, y1 + 1, "c3", reg)              # splash on the inner tier
    rect(L, cx - 13, BOWL_TOP + 5, cx + 12, BOWL_TOP + 5, "c3", reg)  # where the water leaves the bowl
    stamp(L, cx - 5, BOWL_TOP - 6, FOAM, {"C": "c3", "c": "c2", "W": "lw"}, reg)


def candelabra(L, x, base, reg=None):
    """Fountain-plaza candelabra: cast-iron post, two arms and three white globes (unlike the walk lanterns)."""
    rect(L, x - 3, base - 3, x + 3, base, "k1", reg); rect(L, x - 3, base - 3, x - 3, base, "k3", reg)
    rect(L, x - 4, base, x + 4, base, "k0", reg); rect(L, x - 2, base - 6, x + 2, base - 4, "k2", reg)
    rect(L, x - 1, base - 49, x, base - 7, "k2", reg); rect(L, x, base - 49, x, base - 7, "k0", reg)
    px(L, x - 1, base - 20, "k3", reg); rect(L, x - 2, base - 26, x + 1, base - 25, "k3", reg)
    rect(L, x - 8, base - 40, x + 7, base - 40, "k1", reg); rect(L, x - 7, base - 41, x + 6, base - 41, "k2", reg)
    for gx, gy in ((x - 8, base - 46), (x + 7, base - 46), (x, base - 52)):
        rect(L, gx - 1, gy + 2, gx, gy + 5, "k1", reg)
        stamp(L, gx - 2, gy - 2, [".lw.", "lwwm", "wwmm", ".mm."], {"l": "m6", "w": "lw", "m": "m4"}, reg)


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
    for j in range(len(fig)):
        row = fig[j]
        k = next((i for i, ch in enumerate(row) if ch not in ". "), None)
        if k is not None:
            px(L, x - 5 + k + 1, b - 17 - len(fig) + j, "bz3" if j % 3 else "bz2", reg)


def cart_sprite(L, reg=None):
    """Street-vendor cart on the south plaza: steel body, blue / yellow umbrella, two wheels (no brand marks)."""
    x0, b = CART
    x1 = x0 + 35
    cxu = x0 + 17
    for i, hw in enumerate((6, 11, 15, 18, 20, 21, 21, 21)):         # umbrella dome, alternating panels
        y = b - 58 + i
        for x in range(cxu - hw, cxu + hw + 1):
            pan = int(math.floor((x - cxu) / 6.0 + 0.5)) % 2
            c = ("ub0", "ub1")[pan]
            if i == 7:
                c = ("k2", "au1")[pan]
            px(L, x, y, c, reg)
    for x in range(cxu - 21, cxu + 22, 6):
        rect(L, x, b - 50, x + 1, b - 50, "k2", reg)
    rect(L, cxu, b - 50, cxu + 1, b - 22, "k2", reg); rect(L, cxu + 1, b - 50, cxu + 1, b - 22, "k1", reg)
    rect(L, x0 - 1, b - 21, x1 + 1, b - 21, "m6", reg)
    rect(L, x0, b - 20, x1, b - 5, "m4", reg); rect(L, x0, b - 20, x0 + 1, b - 5, "m5", reg)
    rect(L, x1, b - 20, x1, b - 5, "m2", reg); rect(L, x0, b - 5, x1, b - 5, "m2", reg)
    rect(L, x0 + 2, b - 14, x1 - 1, b - 12, "ub1", reg); rect(L, x0 + 2, b - 11, x1 - 1, b - 10, "ub0", reg)
    rect(L, x0 + 4, b - 18, x0 + 12, b - 16, "m2", reg); rect(L, x0 + 5, b - 17, x0 + 11, b - 17, "k1", reg)
    rect(L, x0 + 24, b - 23, x0 + 24, b - 22, "fr", reg); rect(L, x0 + 26, b - 23, x0 + 26, b - 22, "ub1", reg)
    rect(L, x0 + 28, b - 24, x0 + 29, b - 22, "m5", reg)
    for wx in (x0 + 3, x0 + 27):
        stamp(L, wx, b - 4, [".kk.", "kmmk", "kmmk", ".kk."], {"k": "k0", "m": "k2"}, reg)


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

    def item(name, fn, base):
        reg = np.zeros((H, W), bool)
        fn(reg)
        items[name] = {"mask": reg, "base": base}

    for i, (x0, x1, b) in enumerate(FENCES):                         # low NYC park hoop fences
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
    for i, (y0, y1) in enumerate(((250, 257), (282, 289))):           # Broadway gate piers (drawn in streets)
        items[f"broadway_pier_{i}"] = {"mask": box(59, y0, 66, y1), "base": y1}
    return L, items


# ============================================================================ lawn life (v03): occupants + shrub borders
# Hand-drawn hero-scale occupants (seated adults are about half the 48-px heroine). Letters: h hair, H hair light,
# F skin, f skin shade, k dark (eyes, shoes), S/s/d shirt lit / mid / shade, P/p/q trousers lit / mid / shade,
# W/w page or paper light / shade, c cap. Sun from the south-west: west (left) sides are the lit ones.
SEATED_READER = ["......hhhh......",      # cross-legged, open book in the lap
                 "....hhhhhhhh....",
                 "...hhhhhhhhhh...",
                 "...hHHhhhhhhh...",
                 "..hhHFFFFFFhhh..",
                 "..hhFFFFFFFFhh..",
                 "..hhFkFFFFkFhh..",
                 "...hFFFFFFFfh...",
                 "....FFFFFFff....",
                 ".....fFFFff.....",
                 "......ffff......",
                 "...SSSSsssssd...",
                 "..SSSSssssssdd..",
                 "..SSSsssssssdd..",
                 ".SSSssssssssddd.",
                 ".SSssssssssssdd.",
                 ".FSsWWWWWWwsdf..",
                 "..FfWWWWwwwwdf..",
                 "..PPPPppppppqq..",
                 ".PPPPpppppppqqq.",
                 "PPPPppppppppqqqq",
                 "PPPpppppppppqqqq",
                 ".kkkpppppppqkkk.",
                 "..kkk......kkk.."]
KNEES_UP = ["....hhhh......",           # sitting with knees drawn up, hands on knees
            "..hhhhhhhh....",
            ".hhhhhhhhhh...",
            ".hHHhhhhhhhh..",
            ".hhFFFFFFFhh..",
            "hhFFFFFFFFFhh.",
            "hhFkFFFFFkFhh.",
            ".hFFFFFFFFfh..",
            "..FFFFFFFff...",
            "...fFFFFff....",
            "....ffff......",
            "..SSSssssdd...",
            ".SSSssssssdd..",
            ".SSPPPpppqddd.",
            ".SFPPPppppfdd.",
            ".SSPPPpppppqd.",
            "..SPPpppppqd..",
            "..sPPpppppqq..",
            "...PPppppqq...",
            "...PPpp.pqq...",
            "...PPp..pqq...",
            "..kkkk..kkkk..",
            "..kkkk..kkkk.."]
BENCH_READER = SEATED_READER[:18] + ["..PPPPpppppqq...",   # on a bench: thighs toward the viewer, shins down
                                     "..PPPPppppppqq..",
                                     "...PPp....pqq...",
                                     "...PPp....pqq...",
                                     "...PPp....pqq...",
                                     "..kkkk...kkkk..."]
GARDENER = [".....cccc.....",           # kneeling at a bed, cap and gloves, trowel in the west hand
            "...cccccccc...",
            "..cccccccccc..",
            ".ccccccccccc..",
            "...hFFFFFFh...",
            "...FFkFFkFf...",
            "...FFFFFFff...",
            "....fFFFff....",
            "...SSSsssdd...",
            "..SSSSssssdd..",
            ".SSSSsssssddd.",
            "kSSSssssssdddk",
            "kkSSssssssddkk",
            "w.SPPPppppqd..",
            "w.PPPPppppqq..",
            "..PPPPpppqqq..",
            ".kkPPPppppqkk.",
            ".kkkk....kkkk."]
DRONE = [".kk...kk.",                 # 2537 garden drone: twin rotors, teal status light, misting nozzle
         "kmmmmmmmk",
         ".kTTtmmk.",
         "..k...k.."]
FIGURE_MAPS = {
    "reader_nw": {"h": "b0", "H": "b1", "F": "hu2", "f": "hu1", "k": "k0", "S": "c2", "s": "c1", "d": "c0",
                  "P": "k3", "p": "k2", "q": "k1", "W": "m6", "w": "m4"},
    "picnic_a": {"h": "au0", "H": "au1", "F": "hu1", "f": "hu0", "k": "k0", "S": "fl1", "s": "fl0", "d": "pk0",
                 "P": "m5", "p": "m4", "q": "m3", "W": "m6", "w": "m4"},
    "picnic_b": {"h": "k0", "H": "k1", "F": "hu1", "f": "hu0", "k": "k0", "S": "f5", "s": "f4", "d": "f3",
                 "P": "w2", "p": "w1", "q": "w0"},
    "bench_reader": {"h": "m3", "H": "m5", "F": "hu2", "f": "hu1", "k": "k0", "S": "br1", "s": "br0", "d": "b0",
                     "P": "x3", "p": "x2", "q": "x1", "W": "m6", "w": "m4"},
    "gardener": {"c": "f4", "h": "b1", "F": "hu1", "f": "hu0", "k": "k1", "S": "f3", "s": "f2", "d": "f1",
                 "P": "wd2", "p": "wd1", "q": "wd0", "w": "k3"},
}
# (name, sprite, top-left x, base row): bases sit on lawn far enough from walkable paving that no foot can stand
# north of an occupant while overlapping it (the depth audit and collars below prove it)
OCCUPANTS = [("reader_nw", "SEATED_READER", 104, 210), ("picnic_a", "SEATED_READER", 374, 318),
             ("picnic_b", "KNEES_UP", 392, 316), ("bench_reader", "BENCH_READER", 88, 337),
             ("gardener", "GARDENER", 516, 238)]
PICNIC = (370, 314, 406, 324)                                    # blanket x0, y0, x1, y1 (gingham, 3/4 view)
DRONE_AT = (473, 218)
SHRUB_BORDERS = [  # (sp, (x0, x1), base row, lobe radius, bloom colours or None): mounded beds on lawn edges only
    ("hydrangea", (146, 198), 208, 6, ("fl3", "c3", "c2")),     # north rim of the fountain plaza
    ("hydrangea", (396, 434), 250, 5, ("fl4", "pk1", "fl0")),   # behind the NE hoop fence
    ("box", (66, 82), 333, 5, None)]                            # SW fence corner, beside the bench reader


def shrub_border(L, sp, x0, x1, base, r, bloom, reg):
    """A mounded border as one hand-spaced lobe row (lobes alternate 2 rows up / down and grow toward the middle),
    lit like the hero crowns; hydrangea heads are 2x2 clusters in three hand-picked tones."""
    n = max(2, (x1 - x0) // (r + 1))
    lobes = []
    for k in range(n + 1):
        lx = x0 + r + (x1 - x0 - 2 * r) * k / n
        lobes.append((lx - (x0 + x1) / 2, (-2 if k % 2 else 0) - (1 if 0 < k < n else 0), r + (1 if k % 3 == 1 else 0)))
    cx, cy = (x0 + x1) / 2, base - r * 0.7
    u = crown(L, cx, cy, lobes, "box", reg, squash=0.7)
    if bloom:
        hi, mid, lo = bloom
        ys, _ = np.nonzero(u)
        for j, y in enumerate(range(int(ys.min()) + 2, base - 2, 3)):     # flower heads on a fixed 5x3 lattice
            for k, x in enumerate(range(x0 + 2 + (j % 2) * 2, x1 - 1, 5)):
                if u[y + 1, x + 1] and u[y - 1, x]:
                    stamp(L, x - 1, y - 1, ["ab", "bc"], {"a": hi, "b": mid if (j + k) % 3 else hi, "c": lo}, reg)
    return u


def paint_lawn_life():
    L = new()
    items = {}
    for (sp, (x0, x1), base, r, bloom) in SHRUB_BORDERS:
        reg = np.zeros((H, W), bool)
        shrub_border(L, sp, x0, x1, base, r, bloom, reg)
        items[f"shrub_border_{x0}"] = {"mask": reg, "base": base}
    reg = np.zeros((H, W), bool)                                     # picnic blanket, basket, bottle
    x0, y0, x1, y1 = PICNIC
    for y in range(y0, y1 + 1):
        for x in range(x0 + (y1 - y) // 3, x1 + 1 - (y - y0) // 4):
            band = ((x - x0) // 3 + (y - y0) // 2) % 2
            c = ("fr", "m5")[band] if y < y1 else "fr0"
            if x >= x1 - (y - y0) // 4 - 1 and y < y1:
                c = "fr0" if band == 0 else "m3"
            px(L, x, y, c, reg)
    stamp(L, x1 - 9, y0 + 1, [".kkkk.", "k....k", "WWWWWW", "wWWWWd", "wwwwdd"],
          {"k": "wd0", "W": "wd2", "w": "wd1", "d": "wd0"}, reg)
    stamp(L, x0 + 16, y0 + 2, ["g", "G", "G"], {"g": "f5", "G": "f3"}, reg)
    items["picnic_blanket"] = {"mask": reg, "base": y1}
    for (name, spr, x, base) in OCCUPANTS:
        rows = globals()[spr]
        reg = np.zeros((H, W), bool)
        stamp(L, x, base - len(rows) + 1, rows, FIGURE_MAPS[name], reg)
        items[f"occupant_{name}"] = {"mask": reg, "base": base}
    reg = np.zeros((H, W), bool)
    dx, dy = DRONE_AT
    stamp(L, dx, dy, DRONE, {"k": "k1", "m": "m3", "T": "t2", "t": "t1"}, reg)
    items["garden_drone"] = {"mask": reg, "base": dy + 16}
    return L, items


def life_shadow_mask():
    """Ground contact shadows of the occupants (short, north-east of their seats) and the drone's hover shadow."""
    sm = np.zeros((H, W), bool)
    for (name, spr, x, base) in OCCUPANTS:
        w = len(globals()[spr][0])
        sm |= ell(x + w / 2 + 4, base - 1, w * 0.62, 2.6)
    sm |= ell(DRONE_AT[0] + 7, DRONE_AT[1] + 15, 4, 1.4)
    x0, y0, x1, y1 = PICNIC
    sm |= box(x0 + 4, y0 - 2, x1 + 2, y0 - 1)
    for (sp, (a, b), base, r, bloom) in SHRUB_BORDERS:
        sm |= box(a + 3, base - 2 * r, b + 3, base) & ~box(a, base - 2 * r, b, base)
    return sm


def paint_ysort(layer):
    L = new()
    for t in TREES.get(layer, ()):
        paint_tree(L, t)
    for x, b in LAMPS.get(layer, ()):
        lamp_sprite(L, x, b)
    if layer == "statue-ysort":
        statue_sprite(L)
    if layer == "fountain-ysort":
        fountain_sprite(L)
        for x, b in FOUNTAIN_LAMPS:
            candelabra(L, x, b)
    if layer == "cart-ysort":
        cart_sprite(L)
    return L


def paint_fg():
    L = new()
    for t in FG_TREES:
        crown(L, t["c"][0], t["c"][1], t["lobes"], t["sp"], gain=0.8)
    return L


def paint_shadows(below_idx):
    """Opaque cast shadows on the park (sun from the south-west -> shadows fall north-east, up-right on screen).
    Lamp shadows are 2 px wide and end in a lantern blob, so they no longer read as hairline cracks."""
    sm = np.zeros((H, W), bool)
    for trees in TREES.values():
        for t in trees:
            sm |= lobe_shadow_mask(t)
    for lamps in LAMPS.values():
        for (x, b) in lamps:
            sm |= seg((x, b), (x + SUN[0] * 52, b - SUN[1] * 52), 1.0)
            sm |= ell(x + SUN[0] * 60, b - SUN[1] * 60, 3, 1.6)
    for (x, b) in FOUNTAIN_LAMPS:
        sm |= seg((x, b), (x + SUN[0] * 44, b - SUN[1] * 44), 1.0)
        sm |= ell(x + SUN[0] * 50, b - SUN[1] * 50, 5, 1.8)
    sx, sb = STATUE
    sm |= ell(sx + 11, sb - 6, 12, 5)
    fx, fy = FOUNTAIN
    sm |= ell(fx + SUN[0] * 40, fy - 2 - SUN[1] * 40, 13, 3.5) & ell(fx, fy, *BASIN_IN)      # upper bowl on water
    for (x, b) in BENCHES:
        sm |= box(x + 2, b - 10, x + 21, b - 9)
    for (x0, x1, b) in FENCES:
        sm |= box(x0 + 2, b - 5, x1 + 2, b - 5) & ((XX % 6) < 3)
    sm |= seg((PYLON[0], PYLON[1]), (PYLON[0] + 6, PYLON[1] - 4), 1.5)
    cx0, cb = CART
    sm |= box(cx0 + 4, cb - 8, cx0 + 41, cb - 2) | ell(cx0 + 17 + SUN[0] * 54, cb - SUN[1] * 54, 20, 3)
    sm |= life_shadow_mask()
    m = park_masks()
    sm &= ((YY >= WALK_TOP) & (XX >= 64) & (XX < PARK_ROW)) | m["south"]
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
    # Y-sorted objects: footprint collars only (the Y-sort handles in front / behind); (x0, x1, base row)
    feet = {f"candelabra_{i}": (x - 4, x + 4, b) for i, (x, b) in enumerate(FOUNTAIN_LAMPS)}
    feet["statue_pedestal"] = (STATUE[0] - 11, STATUE[0] + 11, STATUE[1])
    feet["vendor_cart"] = (CART[0], CART[0] + 35, CART[1])
    for layer, lamps in LAMPS.items():
        for i, (x, b) in enumerate(lamps):
            feet[f"{layer}_{i}"] = (x - 4, x + 4, b)
    for name, (x0, x1, b) in feet.items():
        c = box(x0 - 4, b - (8 if name == "vendor_cart" else 6), x1 + 4, b + 3)
        collars[name] = c
        wk &= ~c
    return wk, collars


def standing_on_risk(walk, rgba, spr_alpha, run_max=10):
    """Readability gate. A foot is risky when the sprites drawn over the actor there (Y-sort layers whose pivot is
    south of her foot row, plus fg-occlusion) hide >= 50 % of her bottom three opaque rows across >= 6 columns (a
    wide occluder, not a pole or jet) while covering <= run_max rows upward from her feet (v03: a row counts when
    >= 40 % of HER OWN texels in that row are hidden; the v02 rule measured against the widest lower-body row, which
    her 2-texel bottom row can never reach, so its run was always 0 and every foot-hiding occluder was flagged however
    tall): the occluder's top edge then sits at her feet and she reads as standing ON it (the v01 fountain / tree
    captures). Risky feet are removed from the walk mask."""
    fg, ys = occluder_masks(rgba)
    sh, sw = spr_alpha.shape
    rows_px = spr_alpha.sum(1)
    bottom = int(np.nonzero(rows_px)[0].max())
    band = np.zeros_like(spr_alpha)
    band[bottom - 2:bottom + 1] = spr_alpha[bottom - 2:bottom + 1]
    nband = int(band.sum())
    body_w = int(spr_alpha[max(0, bottom - 11):bottom + 1].sum(1).max())
    risky = np.zeros((H, W), bool)
    cache = {}
    for y, x in zip(*np.nonzero(walk)):
        if y not in cache:
            o = fg.copy()
            for n, pv in YSORT_PIVOTS.items():
                if y < pv:
                    o |= ys[n]
            cache[y] = o
        o = cache[y]
        x0, y0 = x - sw // 2, y - sh + 1
        if x0 < 0 or y0 < 0 or x0 + sw > W or not o[y0 + bottom - 2:y0 + bottom + 1, x0:x0 + sw].any():
            continue
        win = o[y0:y0 + sh, x0:x0 + sw] & spr_alpha
        hb = win & band
        if int(hb.sum()) * 2 < nband or int(hb.any(0).sum()) < 6:
            continue
        cov = win.sum(1)
        run = 0
        for r in range(bottom, -1, -1):
            if rows_px[r] == 0:
                continue
            if cov[r] * 10 >= rows_px[r] * 4:
                run += 1
            else:
                break
        if run <= run_max:
            risky[y, x] = True
    return risky


def contact_shadow():
    """Actor contact shadow sprite (RGBA, black with two alpha steps), from the hand-written SHADOW_ROWS."""
    a = np.zeros((len(SHADOW_ROWS), len(SHADOW_ROWS[0]), 4), np.uint8)
    for j, row in enumerate(SHADOW_ROWS):
        for i, ch in enumerate(row):
            if ch in SHADOW_ALPHA:
                a[j, i, 3] = SHADOW_ALPHA[ch]
    return a


def shadow_offset():
    """Top-left of the shadow sprite relative to the foot texel."""
    return SHADOW_OFF[0] - len(SHADOW_ROWS[0]) // 2, SHADOW_OFF[1] - len(SHADOW_ROWS) // 2


def apply_shadow(dst, foot):
    """Runtime blend of a black texel with alpha A: c' = round(c * (255 - A) / 255), integer, half up. The Godot
    texel gate applies the same integer formula; the windowed GPU render is compared against it with tolerance."""
    sh = contact_shadow()
    ox, oy = shadow_offset()
    x0, y0 = foot[0] + ox, foot[1] + oy
    for j in range(sh.shape[0]):
        for i in range(sh.shape[1]):
            A = int(sh[j, i, 3])
            if A and 0 <= x0 + i < W and 0 <= y0 + j < H:
                c = dst[y0 + j, x0 + i, :3].astype(np.int32)
                dst[y0 + j, x0 + i, :3] = ((c * (255 - A) + 127) // 255).astype(np.uint8)


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
    layers = {"skyline": paint_skyline(), "forecourt": paint_forecourt(), "back-groves": paint_back_groves(),
              "streets": paint_streets(), "city-hall": paint_city_hall(), "park-ground": paint_park_ground(),
              "ground-wear": paint_ground_wear(), "ground-detail": paint_ground_detail(),
              "fountain-basin": paint_fountain_basin()}
    assert list(layers) == LAYERS[:9]
    below = composite_idx(layers, list(layers))
    layers["cast-shadows"] = paint_shadows(below)
    props, items = paint_props()
    layers["props-low"] = props
    layers["lawn-life"], life_items = paint_lawn_life()
    items.update(life_items)
    layers["forecourt-near"] = paint_forecourt_near()
    for n in YSORT_LAYERS:
        layers[n] = paint_ysort(n)
    layers["fg-occlusion"] = paint_fg()
    despeckled = despeckle_ground(layers)
    walk, collars = walkable(items, spr_alpha)
    occ = {n: to_rgba(layers[n]) for n in YSORT_LAYERS + ["fg-occlusion"]}
    risky = standing_on_risk(walk, occ, spr_alpha)
    collars["standing_on_readability"] = risky
    walk = walk & ~risky
    layers["guides"] = paint_guides(walk, collars)
    return {"layers": layers, "items": items, "walk": walk, "collars": collars, "spr": spr, "spr_alpha": spr_alpha,
            "despeckled_ground_texels": despeckled, "standing_on_blocked_feet": int(risky.sum())}


GROUND_LAYERS = ("forecourt", "park-ground", "ground-wear", "ground-detail", "cast-shadows", "fountain-basin")
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
        iso = (l - nb.max(0) >= 40) & (YY >= 130)
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


def runtime_stack_still(rgba, spr, foot, shadow=True):
    """Runtime draw order proposal: base (layers 1-13 merged) -> Y-sorted {9 sprite layers, actor} by pivot row (a
    sprite layer is drawn over the actor when the actor's foot row is north of its pivot); the actor's contact
    shadow is drawn immediately before the actor -> fg-occlusion."""
    out = composite_rgba(rgba, BASE_LAYERS)
    placed = False
    for name in sorted(YSORT_LAYERS, key=lambda n: YSORT_PIVOTS[n]):
        if not placed and foot[1] < YSORT_PIVOTS[name]:
            if shadow:
                apply_shadow(out, foot)
            paste(out, spr, foot[0], foot[1]); placed = True
        m = rgba[name][..., 3] == 255
        out[m] = rgba[name][m]
    if not placed:
        if shadow:
            apply_shadow(out, foot)
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


def occlusion_profile(rgba, spr_alpha, foot):
    """For one foot: share of the actor's opaque texels hidden, share of her bottom 3 rows hidden, and the run of
    rows (from the feet upward) at least 40 % covered -- the numbers behind the standing-on readability gate."""
    fg, ys = occluder_masks(rgba)
    o = fg.copy()
    for n, pv in YSORT_PIVOTS.items():
        if foot[1] < pv:
            o |= ys[n]
    sh, sw = spr_alpha.shape
    x0, y0 = foot[0] - sw // 2, foot[1] - sh + 1
    win = o[y0:y0 + sh, x0:x0 + sw] & spr_alpha
    rows_px = spr_alpha.sum(1)
    bottom = int(np.nonzero(rows_px)[0].max())
    band = spr_alpha[bottom - 2:bottom + 1]
    body_w = int(spr_alpha[max(0, bottom - 11):bottom + 1].sum(1).max())
    cov = win.sum(1)
    run = 0
    for r in range(bottom, -1, -1):
        if rows_px[r] and cov[r] * 10 >= rows_px[r] * 4:
            run += 1
        elif rows_px[r]:
            break
    return {"hidden_share": round(float(win.sum()) / int(spr_alpha.sum()), 3),
            "foot_band_hidden_share": round(float(win[bottom - 2:bottom + 1].sum()) / int(band.sum()), 3),
            "covered_rows_from_feet": run}


def static_checks(sc, rgba, flat):
    layers, walk, spr = sc["layers"], sc["walk"], sc["spr"]
    v = {}
    v["canvas_640x360_all_layers"] = all(rgba[n].shape == (H, W, 4) for n in LAYERS)
    v["base_layer_opaque"] = bool((rgba["skyline"][..., 3] == 255).all())
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
    v["no_standing_on_ambiguity_at_walkable_feet"] = not bool(standing_on_risk(walk, rgba, sc["spr_alpha"]).any())
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
                      "walkable": bool(walk[foot[1], foot[0]]),
                      "occlusion": occlusion_profile(rgba, sc["spr_alpha"], foot)}
    v["ysort_behind_front_correct"] = all(c["ok"] and c["walkable"] for c in ys_ok.values())
    sh_spr = contact_shadow()
    v["contact_shadow_two_alpha_steps"] = set(np.unique(sh_spr[..., 3]).tolist()) == {0} | set(SHADOW_ALPHA.values())
    cap_shadow, cap_shadow_occ = {}, {}
    fgm, ysm = occluder_masks(rgba)
    for cap, key in CAPTURES.items():
        foot = PINS[key]
        a = runtime_stack_still(rgba, spr, foot, shadow=True)
        b = runtime_stack_still(rgba, spr, foot, shadow=False)
        cap_shadow[cap] = int((a != b).any(axis=2).sum())
        fp = np.zeros((H, W), bool)                                   # shadow footprint at this foot
        ox, oy = shadow_offset()
        shs = sh_spr[..., 3] > 0
        fp[foot[1] + oy:foot[1] + oy + shs.shape[0], foot[0] + ox:foot[0] + ox + shs.shape[1]] = shs
        over = fgm.copy()
        for n, pv in YSORT_PIVOTS.items():
            if foot[1] < pv:
                over |= ysm[n]
        cap_shadow_occ[cap] = round(float((fp & over).sum()) / int(fp.sum()), 3)
    # v03: the shadow must show (>= 12 texels) unless the capture is a behind case whose over-actor sprite covers at
    # least half of the shadow footprint (behind the fountain veil the shadow is correctly mostly hidden)
    v["contact_shadow_visible_or_occluded_by_front_sprite"] = all(
        cap_shadow[c] >= 12 or (cap_shadow_occ[c] >= 0.5 and cap_shadow[c] >= 1) for c in CAPTURES)
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
    islands = {"park_rows_150_359": single_texel_islands(flat, YY >= 150),
               "backdrop_rows_0_149": single_texel_islands(flat, YY < 150)}
    return {"verdicts": v, "visibility_worst": round(float(worst), 3), "visibility_worst_at": worst_at,
            "visibility_fail_count": len(fails), "visibility_fail_examples": fails[:10], "depth_audit": da,
            "ysort_cases": ys_ok, "pins_reachable": pins_ok, "route_points": len(rpts),
            "route_blocked_examples": blocked[:10],
            "isolated_bright_flecks": {"park_rows_150_359": fl_walk, "examples": fl_ex, "whole_frame": fl_all},
            "single_texel_colour_islands_share": islands,
            "palette": {"art_colours": N_ART, "used_in_flat": len(flat_cols)},
            "despeckled_ground_texels": sc["despeckled_ground_texels"],
            "standing_on_blocked_feet": sc["standing_on_blocked_feet"],
            "contact_shadow_visible_texels_per_capture": cap_shadow,
            "contact_shadow_footprint_share_under_front_sprites": cap_shadow_occ,
            "capture_occlusion": {cap: occlusion_profile(rgba, sc["spr_alpha"], PINS[key])
                                  for cap, key in CAPTURES.items()},
            "walkable_texels": int(walk.sum()), "walkable_share_of_park_rows": round(
                float(walk[WALK_TOP:].sum()) / ((H - WALK_TOP) * W), 3)}


# ============================================================================ build
def artefacts(sc):
    layers = sc["layers"]
    rgba = {n: to_rgba(layers[n]) for n in LAYERS}
    flat = composite_rgba(rgba, ART_LAYERS)
    comp_png = png_bytes(flat)
    files = {"pxo": make_pxo(rgba, comp_png), "ora": make_ora(rgba, comp_png), "gpl": make_gpl(),
             "flat": comp_png, "walkmask": walkmask_png(sc["walk"]), "shadow": png_bytes(contact_shadow())}
    return rgba, flat, files


def names():
    return {"pxo": fname("scene-24layer", "pxo"), "ora": fname("scene-24layer", "ora"),
            "shadow": fname("contact-shadow", "png"),
            "gpl": fname("scene-palette", "gpl"), "walk": fname("scene-walkability", "json"),
            "walkmask": fname("scene-walkmask", "png"), "flat": fname("scene-flat-640x360", "png"),
            "manifest": fname("scene-manifest", "json"),
            "cap_axis": fname("godot-render-1280x720-axis", "png"),
            "cap_behind-fountain": fname("godot-render-1280x720-behind-fountain", "png"),
            "cap_behind-tree": fname("godot-render-1280x720-behind-tree", "png"),
            "cap640_axis": fname("godot-render-640x360-axis", "png"),
            "cap640_behind-fountain": fname("godot-render-640x360-behind-fountain", "png"),
            "cap640_behind-tree": fname("godot-render-640x360-behind-tree", "png"),
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
            "runtime_draw_order_proposal": "base (layers 1-13 merged) -> Y-sorted {9 *-ysort layers, actor} by "
                                           "pivot row (actor last on ties; the actor's contact shadow is drawn just "
                                           "before the actor) -> fg-occlusion",
            "actor_contact_shadow": {"png": names()["shadow"], "offset_from_foot": list(shadow_offset()),
                                     "blend": "black, alpha 118 core / 64 rim, normal alpha blend"},
            "standing_on_readability_blocked_feet": sc["standing_on_blocked_feet"],
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
    for key in set(CAPTURES.values()) | {"spawn_south", "city_hall_gate", "statue_behind", "lamp_w_behind"}:
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
        "project": SLUG, "area": AREA, "run": RUN, "version": "v03",
        "derived_from": {"run": V02_RUN, "tool": V02_TOOL_REL,
                         "note": "v02 files untouched; v03 is a new separate candidate forked from the v02 tool"},
        "status": "UNAPPROVED / NONRUNTIME test-only walkable pilot (one 640x360 camera composition). Not accepted "
                  "art, not runtime-integrated. Acceptance is creator review only; science scene art stays 0/11.",
        "art_approved": False, "runtime_integrated": False, "counters_changed": False, "human_reviewed": False,
        "v03_changes_vs_v02": V03_CHANGES,
        "capture_pins_vs_v02": {"axis": {"v02": [320, 292], "v03": list(PINS["axis_mid"])},
                                "behind-fountain": {"v02": [186, 226], "v03": list(PINS["fountain_behind"]),
                                                    "why": "v02 overlap was 6 texels of a thin jet across her arm; "
                                                           "v03 stands her directly behind the new veil so stone and "
                                                           "falling water hide her from the hips down"},
                                "behind-tree": {"v02": [403, 268], "v03": list(PINS["tree_se_behind"]),
                                                "why": "5 px west so the trunk covers one side and her far foot and "
                                                       "contact shadow stay visible; the west leader crosses her "
                                                       "torso"}},
        "authoring_route": {
            "method": "deterministic Python tool with hand-written placement tables, authored and run by Claude "
                      "(Claude Code, claude.ai Max subscription, firstParty; no API key, no image model, no paid "
                      "fallback); writes a native pxo_version 7 .pxo and an .ora with 24 named layers",
            "pixelorama_gui_paint_pass": False,
            "disclosure": "no desktop/computer-use access to the Pixelorama GUI in this session",
            "texture_policy": "hand-drawn motifs (leaf clumps, grass tufts, bed clumps) on fixed lattices with "
                              "hand-written offset tables; wear marks, stains, cracks, litter, beds, trees and "
                              "props are explicit table entries; no value-noise thresholds, no hashed pixel scatter "
                              "(a hash only picks a granite slab / hex block tone from a short hand table)",
            "reference_usage": "City Hall massing follows the published description (central pavilion, two "
                               "projecting wings, columned entrance portico, domed tower); bay / column counts are "
                               "an interpretation, not measured from LPC elevations; no reference pixel copied; "
                               "Lower Manhattan context is generic hazed massing",
            "reference_url": REFERENCE_URL, "audit_reference": AUDIT_REL,
            "density_idea_reference": {"file": VISUAL_REF_REL, "use": "looked at for density ideas only (canopy "
                                       "variation, planted borders, lawn occupation, warmer city blocks); no pixel "
                                       "or colour sampled; it is itself an UNAPPROVED generated concept"}},
        "canvas": {"w": W, "h": H, "camera": "top-down 3/4; top = north (City Hall), bottom = south",
                   "gameplay_camera": "exactly one 640x360 logical viewport (window 1280x720, integer 2x; also "
                                      "captured in a native 640x360 window)",
                   "scale_reference": {"file": HEROINE_REL, "logical_height_px": int(sc["spr"].shape[0])},
                   "forced_perspective": "backdrop rows 0..171 (city beyond Chambers St, City Hall at reduced "
                                         "scale, forecourt) is not walkable; walkable park rows 172..359 at heroine "
                                         "scale; the walk ends at hero-scale gate piers and railings, the forecourt "
                                         "beyond them recedes (graded stair risers, thinning paving courses, smaller "
                                         "tufts and trees)"},
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
    for k in ("pxo", "ora", "flat", "gpl", "walkmask", "shadow"):
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
# {sprite layers, contact shadow + actor} by pivot row -> fg-occlusion) at every sampled route foot; report SHA-256
# per still. The contact shadow uses the runtime integer formula c' = (c * (255 - A) + 127) / 255 on raw bytes.
func _shadow(st: Image, sh: Image, foot, soff) -> void:
	var d = st.get_data()
	var sd = sh.get_data()
	var sw = sh.get_width()
	var x0 = int(foot[0]) + int(soff[0])
	var y0 = int(foot[1]) + int(soff[1])
	for j in range(sh.get_height()):
		for i in range(sw):
			var al = sd[(j * sw + i) * 4 + 3]
			var x = x0 + i
			var y = y0 + j
			if al == 0 or x < 0 or y < 0 or x >= 640 or y >= 360:
				continue
			var o = (y * 640 + x) * 4
			for c in range(3):
				d[o + c] = int((d[o + c] * (255 - al) + 127) / 255)
	st.set_data(640, 360, false, Image.FORMAT_RGBA8, d)

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
	var shadow = Image.load_from_file(dir + "/shadow.png")
	shadow.convert(Image.FORMAT_RGBA8)
	var soff = cases["shadow_offset"]
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
				_shadow(st, shadow, foot, soff)
				st.blend_rect(hero, Rect2i(0, 0, hero.get_width(), hero.get_height()), hp)
				placed = true
			st.blend_rect(imgs[sp[0]], Rect2i(0, 0, 640, 360), Vector2i(0, 0))
		if not placed:
			_shadow(st, shadow, foot, soff)
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
# holding the nine Y-sorted layers (position.y = pivot, offset.y = -pivot) and the heroine (position = foot, added
# last so she wins ties) whose child is the alpha contact shadow (show_behind_parent), then the fg-occlusion
# overlay. 640x360 viewport, window from the project (1280x720 or 640x360), integer canvas_items stretch, nearest
# filtering. Captures the root
# viewport at each requested foot.
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
	var shadow = Sprite2D.new()
	shadow.centered = false
	shadow.texture = ImageTexture.create_from_image(Image.load_from_file(dir + "/shadow.png"))
	shadow.offset = Vector2(int(cases["shadow_offset"][0]), int(cases["shadow_offset"][1]))
	shadow.show_behind_parent = true
	hero.add_child(shadow)
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
window/size/window_width_override={ww}
window/size/window_height_override={wh}
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
    with open(os.path.join(data, "shadow.png"), "wb") as f:
        f.write(files["shadow"])


def godot_gates(godot, files, rgba, sc):
    spr, walk = sc["spr"], sc["walk"]
    rep = {"godot": GODOT_REL, "godot_sha256": sha(read_bytes(godot)), "texel_gate": {}, "render_gate": {}}
    caps = {}
    rpts = route_points()
    feet = {f"r{i:04d}": list(p) for i, p in enumerate(rpts) if i % 6 == 0}
    feet.update({k: list(PINS[k]) for k in PINS})
    ysl = sorted(([n, YSORT_PIVOTS[n]] for n in YSORT_LAYERS), key=lambda t: t[1])
    tmp = tempfile.mkdtemp(prefix="wb-chpgodot-")
    pnames = []
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
                       "ysort_sprites": ysl, "shadow_offset": list(shadow_offset())}, f)
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
        # ---- windowed render gates (real renderer): 1280x720 (integer 2x) and native 640x360 (1x)
        capfeet = {k: list(PINS[v]) for k, v in CAPTURES.items()}
        for scale, (ww, wh) in ((2, (W * 2, H * 2)), (1, (W, H))):
            tag = f"{ww}x{wh}"
            proj2 = os.path.join(tmp, f"p2_{tag}"); os.makedirs(proj2)
            data2 = os.path.join(tmp, f"d2_{tag}"); os.makedirs(data2)
            fake2 = os.path.join(tmp, f"ad2_{tag}"); os.makedirs(fake2)
            pname = f"chp-render-{RUN_ID}-{tag}"
            pnames.append(pname)
            with open(os.path.join(proj2, "project.godot"), "w", newline="\n") as f:
                f.write(RENDER_PROJECT.format(name=pname, ww=ww, wh=wh))
            with open(os.path.join(proj2, "gate.gd"), "w", newline="\n") as f:
                f.write(GODOT_RENDER_SCRIPT)
            godot_inputs(data2, files, spr, walk)
            with open(os.path.join(data2, "cases.json"), "w") as f:
                json.dump({"base_layers": BASE_LAYERS, "ysort_sprites": ysl, "captures": capfeet,
                           "shadow_offset": list(shadow_offset())}, f)
            env2 = dict(os.environ); env2["APPDATA"] = fake2
            p2 = subprocess.run([godot, "--path", proj2, "--script", "gate.gd", "--", data2],
                                capture_output=True, text=True, timeout=300, env=env2, encoding="utf-8",
                                errors="replace")
            r = rep["render_gate"].setdefault(tag, {})
            r["exit_code"] = p2.returncode
            r["printed_done"] = "GODOT_RENDER_GATE_DONE" in p2.stdout
            r["script_errors"] = [l for l in (p2.stdout + p2.stderr).splitlines() if "SCRIPT ERROR" in l][:5]
            rr = json.load(open(os.path.join(data2, "render_report.json")))
            r["window_size"] = rr.get("window_size")
            r["captures"] = {}
            for k, foot in capfeet.items():
                b = read_bytes(os.path.join(data2, f"render_{k}.png"))
                got = decode(b)[2]
                one = runtime_stack_still(rgba, spr, tuple(foot))
                exp = x2(one) if scale == 2 else one
                same_shape = got.shape == exp.shape
                sm = np.zeros((H, W), bool)                           # 1x footprint of the alpha contact shadow
                ox, oy = shadow_offset()
                shs = contact_shadow()[..., 3] > 0
                sm[foot[1] + oy:foot[1] + oy + shs.shape[0], foot[0] + ox:foot[0] + ox + shs.shape[1]] = shs
                sm2 = x2(sm) if scale == 2 else sm
                if same_shape:
                    dif = (got[..., :3].astype(np.int16) - exp[..., :3].astype(np.int16))
                    dmask = (dif != 0).any(axis=2)
                    diff = int(dmask.sum())
                    out_sh = int((dmask & ~sm2).sum())
                    max_in = int(np.abs(dif[sm2]).max()) if sm2.any() else 0
                else:
                    diff = out_sh = max_in = None
                r["captures"][k] = {"foot": foot, "size": list(got.shape[1::-1]), "differing_pixels": diff,
                                    "differing_outside_contact_shadow": out_sh,
                                    "max_channel_diff_inside_contact_shadow": max_in,
                                    "equals_python_stack": out_sh == 0 and max_in is not None and max_in <= 1}
                caps[("cap_" if scale == 2 else "cap640_") + k] = b
        rep["render_gate"]["godot_wrote_nothing_outside_temp"] = not any(os.path.isdir(os.path.join(
            os.environ.get("APPDATA", ""), "Godot", "app_userdata", n)) for n in pnames + [f"chp-texel-{RUN_ID}"])
    finally:
        shutil.rmtree(_fs(tmp), ignore_errors=True)
    t, rg = rep["texel_gate"], rep["render_gate"]
    r720, r360 = rg["1280x720"], rg["640x360"]
    rep["verdicts"] = {
        "godot_loads_layers_exact": all(t["layers_exact"].values()) and t["exit_code"] == 0,
        "godot_route_walkable_on_exported_mask": t["route_blocked_on_exported_mask"] == 0
                                                 and t["route_jumps_over_1px"] == 0,
        "godot_route_stills_match_ysort_and_occlusion": not t["stills_mismatched"],
        "godot_heroine_48_px": t["heroine_h"] == 48,
        "godot_render_1280x720": all(c["size"] == [W * VIEW, H * VIEW] for c in r720["captures"].values())
                                 and r720["window_size"] == [W * VIEW, H * VIEW],
        "godot_render_1280x720_equals_python_2x_exact_outside_shadow_le1_inside": all(
            c["equals_python_stack"] for c in r720["captures"].values()),
        "godot_render_640x360": all(c["size"] == [W, H] for c in r360["captures"].values())
                                and r360["window_size"] == [W, H],
        "godot_render_640x360_equals_python_1x_exact_outside_shadow_le1_inside": all(
            c["equals_python_stack"] for c in r360["captures"].values()),
        "godot_render_no_script_errors": not r720["script_errors"] and not r360["script_errors"]
                                         and r720["printed_done"] and r360["printed_done"],
        "godot_wrote_nothing_outside_temp": rg["godot_wrote_nothing_outside_temp"],
    }
    return rep, caps


# ============================================================================ check
def check(exe, write_report, use_pixelorama, godot=None):
    sc, rgba, flat, files = build_all()
    nm = names()
    cand = rp(CAND_REL)
    for k in ("pxo", "ora", "flat", "gpl", "walkmask", "shadow"):
        if read_bytes(os.path.join(cand, nm[k])) != files[k]:
            raise SystemExit(f"{nm[k]} on disk differs from a fresh rebuild")
    st = static_checks(sc, rgba, flat)
    rep = {"run": RUN, "gates": dict(st["verdicts"]), "static": st}
    gates = rep["gates"]
    with zipfile.ZipFile(io.BytesIO(files["pxo"])) as z:
        dj = json.loads(z.read("data.json"))
    gates["pxo_layer_stack_is_24_named_layers"] = [l["name"] for l in dj["layers"]] == LAYERS and \
        [l["visible"] for l in dj["layers"]] == [n != "guides" for n in LAYERS] and len(LAYERS) == 24
    with zipfile.ZipFile(io.BytesIO(files["ora"])) as z:
        stack = z.read("stack.xml").decode()
        ora_names = [part.split('"')[0] for part in stack.split('<layer name="')[1:]]
        ora_pngs_exact = all(decode(z.read(f"data/{n}.png"))[2].tobytes() == rgba[n].tobytes() for n in LAYERS)
    gates["ora_stack_is_24_named_layers_guides_hidden"] = ora_names == LAYERS[::-1] and \
        stack.count('visibility="hidden"') == 1 and '<layer name="guides" src="data/guides.png" x="0" y="0" ' \
        'opacity="1.000" visibility="hidden"' in stack
    gates["ora_layer_pngs_exact"] = ora_pngs_exact
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
