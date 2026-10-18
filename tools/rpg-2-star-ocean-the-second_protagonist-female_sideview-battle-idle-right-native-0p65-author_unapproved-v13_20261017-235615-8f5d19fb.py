"""UNAPPROVED, NONRUNTIME test-only pilot v13: female protagonist side-view battle idle, facing right, ONE static frame.

Material-form pass over v12 (bounded fork of the v12 author tool; no motion, no batch, no runtime swap). Same cell (68x72),
pin (32, 68), sole row 67, crown row 7, head outline and face, arm, hand, blade and insignia as v12, so the approved 0.65
battle display proportion, the foot pin, the blade reach and the v8 storm-slate coat identity are unchanged. v12's files are
read (hash-gated) and never written.

Targets the Codex visual review of v12 (2026-10-17, v13 dispatch ...v13-material-and-real-shadow-dispatch...-dfdc7f83.md):
  pack + bedroll read as two stacked boxes   -> bedroll becomes a cylinder: an elliptical end cap with a rolled ring at the
                                                back end, a rounded front end and two bindings that bow round the body;
                                                the pack becomes a slumped canvas sack: a soft flap with a curved edge, a
                                                bulging body that narrows to a rounded bottom, a narrow shadowed side panel
                                                toward the coat (perspective) and one fold crease. Both are SMALLER than v12
  large black tail/roll bundle on the back    -> the back coat tail is shorter and narrower and is cloth-valued: mid slate
                                                (c) body with deep (C) fold lines instead of one deep wedge; the hip drape
                                                follows the shorter tail; the ponytail tip tapers to one point
  weak bright-floor foot separation           -> boot keys follow the REAL runtime contact shadow (radius 18, scale y 0.28,
                                                centred on the pin): texels standing on bright paving are deep (d / l / L),
                                                texels inside the shadow ellipse carry the lit top plane (D) and the
                                                warm-grey welt (u)

v12 header follows (its targets are kept unless changed above).
Mass-and-identity pass over v11. Targets the creator's answer on the v11 four-person captures (2026-10-17, "继续精修静止帧")
and the Codex v12 visual-target note (...creator-feedback-and-v12-visual-target_unapproved-v01_20261017-193755-c7a93e12.md):
  silhouette mass at 1x        -> larger grey-brown pack (13x13, was 10x11) under a larger teal bedroll (13x7, was 10x7);
                                  fuller split coat skirt (back tail to row 56, front panel to x45); near thigh 5 colour
                                  texels wide (was 4); far trouser 5 wide; chunkier boots (15 wide). Head outline and
                                  height untouched; leftmost texel stays x15 (Liang gap kept), blade unchanged
  three identity masses        -> darker high ponytail (body hair-1, strands hair-2, one sheen arc) with a separated loose
                                  lock (own layer, a transparent column on each side); a light shirt wedge (W/w) framed
                                  by a dark lapel line and widening down to the belt under the sword arm; a compact teal
                                  scarf (lit top, short knot) and a compact teal bedroll on the brown pack
  planted feet on dark floors  -> lit low-saturation brown feet (D) over the contact shadow with a warm-grey outsole welt
                                  (new key u, L ~113, saturation 0.15) between the foot and the outline; dark shafts over
                                  the paving; no orange
  micro detail subordinate     -> the pale hair tie becomes a dark leather band (it read as a bead); insignia, face, hand,
                                  forearm, blade unchanged from v11

Hand-authored pixel art: each layer is an ASCII block or explicit rows of keys typed below ('.' = transparent). The blade
is placed by a 1:1 pixel-line helper (the texels a line tool lays). No resampling, filtering, gradients, dithering,
quantizing, image generation or upscaling. Binary alpha. Fixed palette (<= 32 colours).

Editable source: a layered Pixelorama .pxo (pxo_version 7) and an .ora with the same layers plus a hidden, locked
'guides' layer. The candidate PNG is the Pixelorama 1.2.3 headless flat export of the .pxo (byte-compared to this
tool's render); Pixelorama runs with APPDATA redirected to a fresh temp dir so the real config is never touched.

Modes
  preview <dir> [nosprite.png ...]
                  inspection PNGs in <dir> (outside the repo), one subject per file; with no-sprite captures (1280x720
                  or 640x360), also the exact game-scale composite (texture origin 536,408 at 2x / 268,204 at 1x)
  build           export via Pixelorama, write PNG + .pxo + .ora + manifest (never overwrites a different file)
  check           technical gates on the built files incl. Pixelorama flat + split-layer round-trips, layer names and
                  palette diff vs v12, silhouette report vs v12, identity / form / runtime-shadow boot gates, layer-stack recomposition
                  of the .pxo and .ora; writes nothing

Run with the real Python in isolated mode:  python -I -B <this file> preview <dir> | build | check
"""
import argparse, colorsys, hashlib, io, json, os, shutil, subprocess, sys, tempfile, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
VER = "unapproved-v13"
STAMP = "20261017-235615"
RUN_ID = "8f5d19fb"
W, H = 68, 72
PIN = (32, 68)            # same as v03-v12: first transparent row under the soles, between the feet
CROWN_ROW = 7             # same as v03-v12: head crown row; soles end on row 67 -> crown-to-sole 61 rows
SOLE_ROW = 67
HEAD_COLS = (24, 47)      # crown columns are searched here (same as v10-v12)
OUT_DIR_REL = "game/assets/characters/combat-sideview-pilots"
_V12 = "rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_"
V12_LOCKS = {             # v12 (tracked at c20118d) is the comparison base and is read-only for this tool
    OUT_DIR_REL + "/" + _V12 + "unapproved-v12_20261017-224530-fbd81525.png":
        "27f0f79e25dd7587386c5e20df865322aea3a6de024bcf8e745fe02b97c3a079",
    OUT_DIR_REL + "/" + _V12 + "editable-layers_unapproved-v12_20261017-224530-b3da5b53.pxo":
        "a362b607647c1f3781d4b23ce40c62aa91a9fa2361e86e081a015f4f4bc8a64c",
    OUT_DIR_REL + "/" + _V12 + "editable-layers_unapproved-v12_20261017-224530-2ae3fe34.ora":
        "4fde9395cab3cf66377f12f6f4b0c309308cc56fd43857e7eda12ca5f3c8772d",
    OUT_DIR_REL + "/" + _V12 + "manifest_unapproved-v12_20261017-224530-cd2b6299.json":
        "8b4fa592fc60d1e37e9d9333b11d96ac2d501b161ec77828945a4206311117ec",
}
V12_PNG_REL, V12_PXO_REL, V12_ORA_REL, V12_MANIFEST_REL = list(V12_LOCKS)
# Real runtime contact shadow (battle_arena _draw_contact_shadows in the working tree, re-drawn by the v13 capture probe):
# draw_set_transform((round(x), 272), 0, (1, 0.28)); draw_circle(0, 18, rgba(0.02, 0.03, 0.05, 0.42)). In texel space the
# pin (32, 68) sits on screen (300, 272), so texel (tx, ty) covers screen x 268+tx, y 204+ty.
RUNTIME_SHADOW_RADIUS = 18.0
RUNTIME_SHADOW_SCALE_Y = 0.28
V8_SOUTH_REL = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_"
                "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
CHARACTER_SHEET_REL = "outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_female_20261013-153316-8fa4d0c3.png"
DISPATCH_REL = ("docs/coordination/rpg-2-star-ocean-the-second_female-battle-static-v13-material-and-real-shadow-"
                "dispatch_unapproved-v01_20261017-235000-dfdc7f83.md")
VISUAL_TARGET_REL = ("docs/qa/rpg-2-star-ocean-the-second_protagonist-female_battle-static-v11-creator-feedback-and-"
                     "v12-visual-target_unapproved-v01_20261017-193755-c7a93e12.md")
PIXELORAMA_REL = "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"
PIXELORAMA_VERSION = "v1.2.3-stable"
GUIDE_RGB = (255, 0, 255)
CAPTURE_ORIGIN = {1280: (536, 408), 640: (268, 204)}   # screen px of texel (0, 0): hero x 300, floor 272, k = W / 640
BOOT_CONTACT_ROWS = (62, 65)                           # rows standing in the arena's contact shadow
LOWER_BODY_ROW = 38                                    # belt and everything below it
SOLE_WELT_ROW = 66                                     # the outsole welt row above the outline row 67


def fid(role):
    return hashlib.sha256(f"{RUN_ID}:{role}".encode()).hexdigest()[:8]


SUBJECT = "protagonist-female_sideview-idle-right-static-native0p65"
PNG_NAME = f"{SLUG}_{SUBJECT}_{VER}_{STAMP}-{fid('png')}.png"
PXO_NAME = f"{SLUG}_{SUBJECT}_editable-layers_{VER}_{STAMP}-{fid('pxo')}.pxo"
ORA_NAME = f"{SLUG}_{SUBJECT}_editable-layers_{VER}_{STAMP}-{fid('ora')}.ora"
MANIFEST_NAME = f"{SLUG}_{SUBJECT}_manifest_{VER}_{STAMP}-{fid('manifest')}.json"
TOOL_REL = "tools/" + os.path.basename(os.path.abspath(__file__))

PALETTE = {               # v12's 31 keys, unchanged (v12 = v11's 30 keys plus the warm-grey outsole welt u)
    "K": "#16141a",                                                                  # outline
    "1": "#231816", "2": "#3d2a22", "3": "#5c3e2c", "4": "#82593b", "h": "#a8794f",  # hair dark -> sheen
    "S": "#fbd5b0", "s": "#e7a67c", "x": "#b36f50", "E": "#1d1214",                  # skin light/mid/shadow, eye/brow
    "C": "#222839", "c": "#3a4560", "o": "#5e6e8c",                                  # v8 storm-slate coat C3/C2/C1
    "T": "#324542", "t": "#4a625c",                                                  # v8 spruce trousers T2/T1
    "W": "#f3ead9", "w": "#c6b59d",                                                  # shirt / shadowed white
    "P": "#d7c0a8", "p": "#b09986",                                                  # v8 pale beige: cuff, buckle, strap
    "L": "#2e1c14", "l": "#533626",                                                  # v8 dark leather
    "d": "#45342e", "D": "#6f5a4c",                                                  # deep boot / pack brown (v11)
    "Q": "#0a323b", "q": "#1a767b", "g": "#249b98", "G": "#6cc9bc",                  # teal (v8 scarf + one light)
    "m": "#5a6470", "M": "#a9b5bd", "Z": "#eef4f5",                                  # steel / grey knee pad
    "u": "#7a6f68",                                                                  # outsole welt (new, L ~113)
}
REMOVED_KEYS_VS_V12 = []                          # sorted() order
ADDED_KEYS_VS_V12 = []

LAYERS = []


def block(name, x0, y0, text):
    """One layer from an ASCII block: row i of text is canvas row y0+i, column j is canvas x0+j."""
    rows = [r for r in text.strip("\n").split("\n")]
    LAYERS.append((name, [(x0 + j, y0 + i, ch) for i, r in enumerate(rows) for j, ch in enumerate(r.strip())
                          if ch != "."]))


def rows(name, spec):
    """One layer from explicit rows: (canvas row y, first canvas column x, keys); key j lands on column x+j."""
    LAYERS.append((name, [(x + j, y, ch) for y, x, keys in spec for j, ch in enumerate(keys) if ch != "."]))


def block_px(name, texels):
    LAYERS.append((name, list(texels)))


# ===================================================================================================== layers
# bottom -> top.  In rows() specs the second number is the absolute canvas column of the first key.

# v13 boots: same outline as v12, re-keyed by the REAL runtime contact shadow (radius 18, y scale 0.28, centred on the
# pin). Ellipse spans per row (texel columns whose screen-pixel centre is inside): row 63 x24-39, row 64 x19-44, row 65
# x16-47, row 66 x15-48, row 67 x14-49; rows 57-62 are all on paving. On paving the boot is deep (d, dark cuff l): archive
# paving L ~110, outskirts ~80. Inside the shadow (archive L ~66, outskirts ~46) the foot's top plane is lit (D, L ~94)
# and the outsole welt warm grey (u, L ~113). The far heel and the near toe stick out of the ellipse, so they stay deep.
# far (back) leg braced back, 5 colour texels wide: deep slate trouser (C) with a spruce crease (T)
rows("far-leg", [
    (42, 26, "KCCCCCK"),
    (43, 26, "KCCCTCK"),
    (44, 25, "KCCCTCK"),
    (45, 25, "KCCCTCK"),
    (46, 24, "KCCCTCK"),
    (47, 24, "KCCCTCK"),
    (48, 23, "KCCCTCK"),
    (49, 23, "KCCCTCK"),
    (50, 22, "KCCCTCK"),
    (51, 22, "KCCCTCK"),
    (52, 21, "KCCCTCK"),
    (53, 21, "KCCCTCK"),
    (54, 21, "KCCCTCK"),
    (55, 21, "KCCCTCK"),
    (56, 21, "KCCCTCK"),
    (57, 20, "KKKKKKKKK"),
    (58, 20, "KlllllldK"),
    (59, 19, "KddddddddK"),
    (60, 19, "KdpppddddK"),
    (61, 18, "KddddddddddK"),
    (62, 18, "KdddddddddlK"),
    (63, 17, "KddddddDDDDDDK"),
    (64, 17, "KdDDDDDDDDDDpDK"),
    (65, 17, "KdDDDDDDDDDDDDK"),
    (66, 18, "KuuuuuuuuuuuuK"),
    (67, 19, "KKKKKKKKKKKK"),
])

# v8's teal back-hip cloth hung BEHIND the coat skirt. v13: a short tab from the belt (rows 39-47) that shows two or three
# texels left of the narrower back tail, under the pack; v12's long drape ran down the whole tail edge as a stripe
#                   x18
block("hip-drape", 18, 39, """
...KK.
..KgqK
.KgqqK
.KgqQK
KgqQK.
KgQqK.
KgqK..
KqK...
.K....
""")

# v13 slumped canvas pack (v12: a 13x13 box): narrow at the top (x19, so the roll overhangs it by two texels) and
# widening down to the bulge, like a loaded sack; the bedroll sits in its open top; a soft lit flap top plane (D), a flap
# front (d) whose dark edge (L) curves down to the middle like a hanging flap, a body that bulges out to x15 and narrows
# to a rounded, slumped bottom ending on row 37 (two rows above the coat tail, v12: touching it), a soft highlight on the
# upper bulge (D), one fold crease (l) and a dark-leather strap (l) with a pale buckle (P) from under the flap; the coat
# covers its right edge. Smaller than v12
rows("pack", [
    (26, 19, "KKKKKKKKK"),
    (27, 18, "KDDDDDDDdK"),
    (28, 17, "KdDDDDDDddK"),
    (29, 16, "KLdDDDDDddLK"),
    (30, 15, "KdLLddddLLLdK"),
    (31, 15, "KddDLLPLLdddK"),
    (32, 15, "KdDDddlddddLK"),
    (33, 15, "KdDdddlddddLK"),
    (34, 15, "KddddlldddLLK"),
    (35, 16, "KddlddddLLLK"),
    (36, 16, "KLdddddLLK"),
    (37, 17, "KKKKKKKK"),
])

# v13 teal bedroll as a cylinder (v12: a 13x7 box), 12x7, resting in the pack top: an elliptical end cap at the back end
# (x16-18: deep ring q with lit turns g round a dark core Q, closed by a seam Q that curves like the cap's far rim), a lit
# top (G), mid body (g), deep underside (q, Q), a rounded front end, and one leather binding (l, darker L on the
# underside) that bows toward the cap the way a band round a cylinder does
rows("bedroll", [
    (20, 17, "KKKKKKKK"),
    (21, 16, "KqQGGGGlGK"),
    (22, 15, "KqgqQgglggqK"),
    (23, 15, "KgQgQgglggqK"),
    (24, 15, "KqqqQqqlqqqK"),
    (25, 16, "KqQQQQQLQK"),
    (26, 17, "KKKKKKKK"),
])

# high tied ponytail, v12 hook and strands; v13 replaces the forked tip (two prongs on rows 15-17) with one clean taper
#               x16
block("ponytail", 16, 1, """
........KKKKK...
.......K11223K..
.....K1112234hK.
....K111122332K.
...K1111122321K.
..K1111122221K..
..K11112K.K11K..
.K11112K..K1....
.K11122K..KK....
.K11121K........
K11112K.........
K11121K.........
K11211K.........
K1112K..........
K112K...........
.K1K............
..K.............
""")

# loose lock falling from the hook tip at the nape, between the tail and the head: one hair texel wide inside its
# outline, with at least one transparent column to the tail and to the head on every row (reads as a separate strand)
rows("loose-lock", [
    (9, 25, "K1K"),
    (10, 25, "K2K"),
    (11, 25, "K1K"),
    (12, 24, "K1K"),
    (13, 24, "K2K"),
    (14, 24, "K1K"),
    (15, 24, "K1K"),
    (16, 25, "K"),
])

# near (front) leg, 5 colour texels wide (v11: 4): spruce thigh (T body, t front edge, C back) to a bent knee with a
# cool grey knee pad (m/M over C) on a dark strap (L/l), spruce shin, boot as the far one (dark cuff/shaft over the
# paving, long lit foot in the contact shadow, pale toe glint, warm-grey outsole welt) with the light pale strap (P)
rows("near-leg", [
    (41, 33, "KCTTTtK"),
    (42, 33, "KCTTTttK"),
    (43, 34, "KCTTTtK"),
    (44, 34, "KCTTTttK"),
    (45, 35, "KCTTTtK"),
    (46, 35, "KCTTTttK"),
    (47, 36, "KCTTTtK"),
    (48, 36, "KCTTTttK"),
    (49, 37, "KCTTTtK"),
    (50, 37, "KCTTTttK"),
    (51, 37, "KCmmmMMK"),
    (52, 37, "KCCmmmmK"),
    (53, 38, "KLllllK"),
    (54, 38, "KCTTTtK"),
    (55, 38, "KCTTTtK"),
    (56, 38, "KCTTTtK"),
    (57, 37, "KKKKKKKKK"),
    (58, 37, "KlllllldK"),
    (59, 37, "KddddddddK"),
    (60, 37, "KdPPPddddK"),
    (61, 37, "KdddddddddK"),
    (62, 37, "KddddddddllK"),
    (63, 37, "KDDdddddddddlK"),
    (64, 37, "KDDDDDDDddddldK"),
    (65, 37, "KDDDDDDDDDDdldK"),
    (66, 37, "KuuuuuuuuuuuddK"),
    (67, 38, "KKKKKKKKKKKKK"),
])

# coat torso + belt, leaning (v11 outline and value planes: deep back C, mid seam c, lit front o), front carried one to
# three texels further forward on rows 30-37 so the open front can show a wider shirt; belt dark leather (l over L)
# with the pale buckle (P/p), now running to the front edge
#                x24       x34
block("coat", 24, 22, """
.......KKKKK.........
.....KKCcoooK........
....KCCCcoooo........
....KCCCCcoooo.......
...KCCCCCcoooo.......
...KCCCCCcooooo......
...KCCCCCCcooooo.....
...KCCCCCCcoooooo....
..KCCCCCCcooooooo....
..KCCCCCCcoooooooo...
..KCCCCCCcoooooooo...
..KCCCCCCcooooooooo..
.KCCCCCCcoooooooooo..
.KCCCCCCcoooooooooo..
.KCCCCCCcooooooooooo.
KCCCCCCcoooooooooooo.
KlllllllllPPllllllllK
KLLLLLLLLLLppLLLLLLLK
""")

# split coat skirt, fuller: deep back tail (C, mid band c, lit split edge o) flaring to x16 and hanging to row 56 with a
# dark-leather hem (l) that rises toward the split so the far shin shows under it; lit front panel (o, fold c) from the
# split K at x32 to x45, mid hem band (c) and dark-leather trim (l) closing at row 48
# v13: the front panel is v12's; the back tail is shorter (ends on row 53, v12 row 56) and narrower (to x18, v12 x16),
# cloth-valued: mid slate body (c) with two deep fold lines (C) running down toward the back, deep only under the belt,
# the lit split edge (o) kept, and a dark-leather hem (l) that rises toward the split
rows("coat-skirt", [
    (40, 23, "KCCCCCCc" + "o" * 14 + "K"),
    (41, 22, "KccCcccccoK" + "ooooocooooooK"),
    (42, 22, "KcCcccCccoK" + "ooooocooooooK"),
    (43, 21, "KcCccccCcoCK" + "ooooocoooocK"),
    (44, 21, "KcCcccCccoCK" + "ooooocoocllK"),
    (45, 21, "KccccCcccoCK" + "ooooccllKK"),
    (46, 20, "KcccccCcccoCK" + "ccccllK"),
    (47, 20, "KccccCcccoK" + "K" + "lllK"),
    (48, 20, "KccccCccoK"),
    (48, 31, "KKKK"),
    (49, 19, "KccccCcclK"),
    (50, 19, "KcccCcllK"),
    (51, 18, "KcccCllK"),
    (52, 18, "KllllK"),
    (53, 19, "KKKK"),
])

# white shirt wedge in the open coat front: two lit lapel texels (o), a dark lapel line (K), the shirt's shadow column
# (w) and the shirt (W) to the front edge; it widens from 3 texels at the neck to 7 at the belt (v11: 2-3 everywhere)
rows("shirt-lapel", [
    (23, 39, "ooKWWK"),
    (24, 39, "ooKwWWK"),
    (25, 38, "ooKwWWWK"),
    (26, 38, "ooKwWWWK"),
    (27, 37, "ooKwWWWWK"),
    (28, 37, "ooKwWWWWK"),
    (29, 37, "ooKwWWWK"),
    (30, 37, "ooKwWWWK"),
    (31, 36, "ooKwWWWWK"),
    (32, 36, "ooKwWWWWK"),
    (33, 35, "ooKwWWWWWK"),
    (34, 35, "ooKwWWWWWK"),
    (35, 34, "ooKwWWWWWWK"),
    (36, 34, "ooKwWWWWWWK"),
    (37, 34, "ooKwWWWWWWK"),
])

# near arm reaching forward, sleeve rolled to the elbow (v11 drawing, unchanged)
#                 x28       x38
block("near-arm", 28, 23, """
...KKKKK........
..KooooooK......
..KCoooooK......
...KCoooooK.....
...KCCooooK.....
....KCCooooK....
....KCCoooPKKKKK
....KCCcoPPPSSSK
.....KCCpPpsSssK
......KCKppxxxxK
.......KKKKKKKKK
""")

# teal insignia patch on the upper sleeve (v11, unchanged; a colour placement at 1x)
#                 x33
block("insignia", 33, 24, """
.g.
gGg
.g.
""")


# ordinary short sword raised forward at 45 degrees (v10/v11 blade, unchanged)
def blade_segments(y0=26, y1=18):
    segs = []
    for y in range(y1, y0 + 1):
        x = 76 - y                       # edge-light column on row y
        segs += [(x - 1, y, "K"), (x, y, "Z"), (x + 1, y, "M"), (x + 2, y, "K")]
    x = 76 - (y1 - 1)
    segs += [(x - 1, y1 - 1, "K"), (x, y1 - 1, "Z"), (x + 1, y1 - 1, "K"), (x, y1 - 2, "K")]
    return segs


block_px("sword-blade", blade_segments())

# small steel crossguard square to the blade (v10/v11, unchanged)
block("sword-guard", 47, 25, """
KK...
KMK..
.KMK.
..KMK
...KK
""")

# fingerless dark glove closed round the grip (v11, unchanged)
block("fist", 43, 27, """
.KKKK..
KlSSSK.
KllSSsK
KLlsSsK
KLlssxK
.KLKKK.
..K....
""")

# head: v11 outline and face texel-for-texel (crown row 7, same size); hair re-keyed darker (body hair-1, strands
# hair-2, one sheen arc 3/h), fringe strands over the brow and the side lock kept
#            x28
block("head", 28, 7, """
.....KKKKKKK.......
...KK11112223KK....
..K11111222332KK...
.K111112222h322K...
.K11111222223322K..
.K1111122212S2S2K..
.K111122212SSEEESK.
.K111122121SSSEESK.
.K111122121sSSEWSSK
.K111121121sssSSSK.
.K111211112ssSSxSK.
.K111111K1xssSSSK..
..K1111K.K1xsKKK...
""")

# dark leather hair band where the ponytail leaves the head (v11's pale tie read as a separate bead at 1x)
block("hair-tie", 28, 7, """
.KK.
KDdK
KdDK
.KK.
""")

# raised coat collar standing behind the nape (v10/v11, unchanged)
block("collar", 28, 16, """
.KK..
KooK.
KoooK
KoooK
KCooK
KCcoK
""")

# compact teal scarf: lit top row (G), mid wrap (g, q), deep under-fold (Q), short knot ending on row 26 (v11 tail ran to
# row 28 over the shirt)
block("scarf-neck", 29, 20, """
.KgGGGGggggGGK.
KqgggGGGgggGGgK
KQqggggggqggGgK
KQQqqqqQqqqggqK
.KKKKKKKQqgGgK.
........KqgGgK.
.........KKKK..
""")

# front half of the raised collar over the scarf's front edge (v10/v11, unchanged)
block("collar-front", 42, 20, """
.KK.
KooK
KooK
KcoK
KcoK
.KK.
""")

LAYER_NAMES = [n for n, _ in LAYERS] + ["guides"]
V12_LAYER_NAMES_PLUS = []                     # v13 = v12's 20 layer names, same order (+ guides)
V12_UNCHANGED_LAYERS = ["loose-lock", "coat", "shirt-lapel", "near-arm", "insignia", "sword-blade", "sword-guard",
                        "fist", "head", "hair-tie", "collar", "scarf-neck",
                        "collar-front"]       # declared byte-identical to v12's .ora layers (checked)
V13_CHANGED_LAYERS = ["far-leg", "hip-drape", "pack", "bedroll", "ponytail", "near-leg", "coat-skirt"]
BACK_REGION = (0, 31, 20, 56)                 # x0, x1, y0, y1 inclusive: pack, roll, back tail, behind the body


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
    """sha256-bytes for binaries; sha256-text-lf-v1 (CRLF -> LF) for the .json lock, so a core.autocrlf=true checkout
    still matches. The v12 manifest is LF on disk, so both algorithms give the same locked value."""
    data = read_bytes(repo_path(rel))
    return sha256_bytes(data.replace(b"\r\n", b"\n") if rel.endswith(".json") else data)


def v12_lock():
    files = {rel: lock_hash(rel) for rel in V12_LOCKS}
    return {"files": files, "unchanged": all(files[rel] == want for rel, want in V12_LOCKS.items())}


def decode(png):
    im = Image.open(io.BytesIO(png))
    return im.mode, im.size, np.array(im.convert("RGBA"))


# ===================================================================================================== v12 comparison
def v12_reference():
    """v12's flat PNG, its per-layer RGBA from the locked .ora, and its manifest palette (all read-only)."""
    png = decode(read_bytes(repo_path(V12_PNG_REL)))[2]
    with zipfile.ZipFile(io.BytesIO(read_bytes(repo_path(V12_ORA_REL)))) as z:
        names = [n[len("data/"):-len(".png")] for n in z.namelist() if n.startswith("data/") and n.endswith(".png")]
        layers = {n: decode(z.read(f"data/{n}.png"))[2] for n in names}
    man = json.loads(read_bytes(repo_path(V12_MANIFEST_REL)))
    order = [l["name"] for l in man["layers_bottom_to_top"]]
    return png, layers, order, man["palette"]


def bbox(alpha):
    ys, xs = np.nonzero(alpha)
    return None if len(xs) == 0 else [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


def visible_masks(blobs, names=None):
    """Per layer: texels where that layer is the top-most opaque layer (what the viewer actually sees of it). `names`
    is the bottom-to-top order (default: this tool's layers); v12's .ora layers are passed with v12's own order."""
    names = [n for n in (names or LAYER_NAMES) if n != "guides"]
    owner = np.full((H, W), -1, np.int16)
    for i, name in enumerate(names):
        owner[blobs[name][..., 3] == 255] = i
    return {name: owner == i for i, name in enumerate(names)}


def silhouette_report(comp, blobs):
    """How v13 differs from v12: whole-sprite alpha silhouette, composite texels, per layer, palette and layer names."""
    v12_png, v12_layers, v12_order, v12_pal = v12_reference()
    a11, a10 = comp[..., 3] > 0, v12_png[..., 3] > 0
    inter, union = int((a11 & a10).sum()), int((a11 | a10).sum())
    layers = {}
    for name in LAYER_NAMES[:-1]:
        mine = blobs[name][..., 3] > 0
        theirs = v12_layers[name][..., 3] > 0 if name in v12_layers else None
        same_px = theirs is not None and np.array_equal(blobs[name], v12_layers[name])
        layers[name] = {"texels_v12": None if theirs is None else int(theirs.sum()), "texels_v13": int(mine.sum()),
                        "bbox_v12": None if theirs is None else bbox(theirs), "bbox_v13": bbox(mine),
                        "byte_identical_to_v12": bool(same_px),
                        "changed_texels": None if theirs is None else int((blobs[name] != v12_layers[name]).any(-1).sum())}
    v12_names = [n for n in v12_order if n != "guides"]
    pal10 = {k: v.lower() for k, v in v12_pal.items()}
    pal11 = {k: v.lower() for k, v in PALETTE.items()}
    return {
        "silhouette_texels_v12": int(a10.sum()), "silhouette_texels_v13": int(a11.sum()),
        "silhouette_iou": round(inter / union, 4), "silhouette_added_texels": int((a11 & ~a10).sum()),
        "silhouette_removed_texels": int((a10 & ~a11).sum()),
        "silhouette_bbox_v12": bbox(a10), "silhouette_bbox_v13": bbox(a11),
        "composite_changed_texels": int((comp != v12_png).any(-1).sum()),
        "layers": layers,
        "byte_identical_layers": [n for n in LAYER_NAMES[:-1] if layers[n]["byte_identical_to_v12"]],
        "layers_added_vs_v12": [n for n in LAYER_NAMES[:-1] if n not in v12_names],
        "layers_removed_vs_v12": [n for n in v12_names if n not in LAYER_NAMES],
        "layer_order_v12": v12_order,
        "palette_keys_removed_vs_v12": sorted(set(pal10) - set(pal11)),
        "palette_keys_added_vs_v12": sorted(set(pal11) - set(pal10)),
        "palette_shared_keys_same_colour": all(pal10[k] == pal11[k] for k in set(pal10) & set(pal11)),
    }


# ===================================================================================================== identity gates
def lum(rgb):
    rgb = np.asarray(rgb, float)
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def warm_orange_mask(rgba):
    """Opaque texels whose colour is a saturated orange/tan: hue 10-50 deg, HSV saturation >= 0.45, value >= 0.40."""
    m = np.zeros(rgba.shape[:2], bool)
    for y, x in zip(*np.nonzero(rgba[..., 3] > 0)):
        r, g, b = (int(v) / 255 for v in rgba[y, x, :3])
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        m[y, x] = 10 / 360 <= h <= 50 / 360 and s >= 0.45 and v >= 0.40
    return m


def lower_body_report(rgba):
    """Belt row and everything below it: share of saturated orange texels and of cool (blue/green/teal-ish) texels."""
    op = rgba[..., 3] > 0
    op[:LOWER_BODY_ROW] = False
    warm = warm_orange_mask(rgba) & op
    rgb = rgba[..., :3].astype(int)
    cool = op & (rgb[..., 2] >= rgb[..., 0]) & ~(rgb == np.array(hex_rgb(PALETTE["K"]))).all(-1)
    n = int(op.sum())
    return {"opaque_texels": n, "warm_orange_texels": int(warm.sum()),
            "warm_orange_share": round(int(warm.sum()) / max(1, n), 4),
            "cool_texels_blue_ge_red_excl_outline": int(cool.sum()),
            "cool_share": round(int(cool.sum()) / max(1, n), 4),
            "mean_L_excl_outline": round(float(lum(rgba[op & ~(rgb == np.array(hex_rgb(PALETTE["K"]))).all(-1)][:, :3])
                                               .mean()), 1)}


def keycount(rgba, mask, keys):
    rgb = rgba[..., :3]
    return int(sum((mask & (rgb == np.array(hex_rgb(PALETTE[k]), np.uint8)).all(-1)).sum() for k in keys))


def boot_report(comp, blobs, names=None):
    """Each boot: lit top-plane texels (D, P, p) on the contact-shadow rows, deep texels (d, L) on the shaft rows, and
    the warm-grey outsole welt (u) on the welt row."""
    vis = visible_masks(blobs, names)
    out = {}
    for leg in ("far-leg", "near-leg"):
        contact = vis[leg].copy()
        contact[:BOOT_CONTACT_ROWS[0]] = False
        contact[BOOT_CONTACT_ROWS[1] + 1:] = False
        shaft = vis[leg].copy()
        shaft[:58] = False
        shaft[BOOT_CONTACT_ROWS[0]:] = False
        welt = vis[leg].copy()
        welt[:SOLE_WELT_ROW] = False
        welt[SOLE_WELT_ROW + 1:] = False
        out[leg] = {"contact_rows_lit_top_plane_D_P_p": keycount(comp, contact, "DPp"),
                    "contact_rows_deep_d_L": keycount(comp, contact, "dL"),
                    "shaft_rows_deep_d_L": keycount(comp, shaft, "dL"),
                    "shaft_rows_light_anchor_D_P_p": keycount(comp, shaft, "DPp"),
                    "welt_row_u": keycount(comp, welt, "u") if "u" in PALETTE else 0,
                    "welt_row_dark_L_d": keycount(comp, welt, "Ld"),
                    "boot_bbox": bbox(vis[leg] & (np.arange(H)[:, None] >= 57)),
                    "orange_texels": int((warm_orange_mask(comp) & vis[leg]).sum())}
    return out


def row_colour_widths(layer_rgba, y0, y1):
    """Non-outline texels per row of one layer (its own pixels, not visibility) on rows y0..y1."""
    k = np.array(hex_rgb(PALETTE["K"]), np.uint8)
    op = (layer_rgba[..., 3] > 0) & ~(layer_rgba[..., :3] == k).all(-1)
    return [int(op[y].sum()) for y in range(y0, y1 + 1)]


def identity_report(comp, blobs, names=None):
    """Identity and mass numbers for one version: v13 (this render) or v12 (its locked .ora layers and order)."""
    names = [n for n in (names or LAYER_NAMES) if n != "guides"]
    vis = visible_masks(blobs, names)
    head, fist, arm = vis["head"], vis["fist"], vis["near-arm"]
    hair_mask = head | vis["ponytail"] | (vis["loose-lock"] if "loose-lock" in vis else False)
    tails = blobs["ponytail"][..., 3] > 0
    if "loose-lock" in blobs:
        tails = tails | (blobs["loose-lock"][..., 3] > 0)
    roll = blobs["bedroll"][..., 3] > 0
    pack = blobs["pack"][..., 3] > 0
    gap = None                    # transparent rows between the lowest hair (tail or lock) and the roll, per column
    for x in range(W):
        py, ry = np.nonzero(tails[:, x])[0], np.nonzero(roll[:, x])[0]
        if len(py) and len(ry):
            g = int(ry.min() - py.max() - 1)
            gap = g if gap is None else min(gap, g)
    lock = None
    if "loose-lock" in blobs:     # per lock row: transparent texels of the composite between lock, tail and head
        la = blobs["loose-lock"][..., 3] > 0
        op = comp[..., 3] > 0
        rows_ok = []
        for y in range(10, 16):
            xs = np.nonzero(la[y])[0]
            left = [x for x in range(xs.min() - 1, -1, -1) if op[y, x]]
            right = [x for x in range(xs.max() + 1, W) if op[y, x]]
            rows_ok.append({"row": y, "clear_cols_to_tail": int(xs.min() - 1 - left[0]) if left else None,
                            "clear_cols_to_head": int(right[0] - xs.max() - 1) if right else None})
        lock = {"texels": int(la.sum()), "hair_texels_visible": keycount(comp, vis["loose-lock"], "1234h"),
                "rows": rows_ok}
    shirt = vis["shirt-lapel"]
    shirt_w = shirt.copy()
    mass_layers = ("coat", "coat-skirt", "pack", "bedroll")
    near_thigh = row_colour_widths(blobs["near-leg"], 41, 50)
    far_shin = row_colour_widths(blobs["far-leg"], 50, 56)
    return {
        "face_skin_texels_S_s_x": keycount(comp, head, "Ssx"),
        "eye_brow_texels_E": keycount(comp, head, "E"),
        "eye_catch_texels_W": keycount(comp, head, "W"),
        "head_layer_alpha_bbox": bbox(blobs["head"][..., 3] > 0),
        "hair_texels_by_key": {k: keycount(comp, hair_mask, k) for k in "1234h"},
        "hair_darkest_share_1": round(keycount(comp, hair_mask, "1") / max(1, keycount(comp, hair_mask, "1234h")), 3),
        "hair_dark_share_1_2": round(keycount(comp, hair_mask, "12") / max(1, keycount(comp, hair_mask, "1234h")), 3),
        "hair_tie_visible_pale_texels": keycount(comp, vis["hair-tie"], "Pp"),
        "loose_lock": lock,
        "tail_or_lock_to_roll_min_vertical_gap_rows": gap,
        "fist_skin_texels": keycount(comp, fist, "Ssx"),
        "fist_glove_texels": keycount(comp, fist, "lL"),
        "forearm_skin_texels": keycount(comp, arm, "Ssx"),
        "sleeve_rolled_cuff_texels_P_p": keycount(comp, arm, "Pp"),
        "shirt_visible_W_w": keycount(comp, shirt_w, "Ww"),
        "shirt_visible_W_w_per_row_23_37": [keycount(comp, shirt_w & (np.arange(H)[:, None] == y), "Ww")
                                            for y in range(23, 38)],
        "teal_texels_visible": {n: keycount(comp, vis[n], "QqgG") for n in ("scarf-neck", "bedroll", "insignia",
                                                                            "hip-drape")},
        "scarf_bbox": bbox(blobs["scarf-neck"][..., 3] > 0),
        "roll_bbox": bbox(roll), "pack_bbox": bbox(pack),
        "roll_sits_on_pack_top": bool(bbox(roll)[3] + 1 == bbox(pack)[1]),
        "pack_visible_texels": int(vis["pack"].sum()),
        "pack_visible_brown_d_D": keycount(comp, vis["pack"], "dD"),
        "coat_pack_roll_visible_texels": {n: int(vis[n].sum()) for n in mass_layers},
        "coat_pack_roll_visible_total": int(sum(vis[n].sum() for n in mass_layers)),
        "near_thigh_colour_texels_per_row_41_50": near_thigh,
        "far_shin_colour_texels_per_row_50_56": far_shin,
    }


def face_mask(head_rgba):
    """Skin, eye/brow and eye-catch texels of a head layer (the face; hair is excluded)."""
    rgb = head_rgba[..., :3]
    m = np.zeros((H, W), bool)
    for k in "SsxEW":
        m |= (head_rgba[..., 3] > 0) & (rgb == np.array(hex_rgb(PALETTE[k]), np.uint8)).all(-1)
    return m


def runtime_shadow_mask():
    """Texels whose screen-pixel centre lies inside the runtime contact shadow ellipse (pin on screen (300, 272), texel
    (tx, ty) on screen (268 + tx, 204 + ty), radius 18, y scale 0.28). The v13 captures measure the real pixels too."""
    ty, tx = np.mgrid[0:H, 0:W]
    dx = (268 + tx + 0.5 - 300.0) / RUNTIME_SHADOW_RADIUS
    dy = (204 + ty + 0.5 - 272.0) / (RUNTIME_SHADOW_RADIUS * RUNTIME_SHADOW_SCALE_Y)
    return dx * dx + dy * dy <= 1.0


def shadow_boot_report(comp, blobs, names=None):
    """Each boot's foot rows 62-66 (outline excluded), split by the runtime contact-shadow ellipse: texels on paving
    should be deep (d, l, L), texels in the shadow lit (D top plane, u welt, p/P glint)."""
    vis = visible_masks(blobs, names)
    sh = runtime_shadow_mask()
    rows_ = np.zeros((H, W), bool)
    rows_[62:67] = True
    out = {}
    for leg in ("far-leg", "near-leg"):
        foot = vis[leg] & rows_
        lit_in = keycount(comp, foot & sh, "DupP")
        out[leg] = {"in_shadow_texels": int((foot & sh & ~(comp[..., :3] == np.array(hex_rgb(PALETTE["K"]),
                                                                                       np.uint8)).all(-1)).sum()),
                    "in_shadow_lit_D_u_p_P": lit_in, "in_shadow_deep_d_l_L": keycount(comp, foot & sh, "dlL"),
                    "on_paving_lit_D_u_p_P": keycount(comp, foot & ~sh, "DupP"),
                    "on_paving_deep_d_l_L": keycount(comp, foot & ~sh, "dlL"),
                    "rows_64_66_in_shadow_lit_share": round(keycount(comp, foot & sh & (np.arange(H)[:, None] >= 64),
                                                                     "DupP")
                                                            / max(1, keycount(comp, foot & sh & (np.arange(H)[:, None]
                                                                                                  >= 64), "DupPdlL")), 3)}
    return out


def row_extents(alpha):
    """{row: (first x, last x)} of a layer's opaque texels."""
    return {int(y): (int(np.nonzero(alpha[y])[0].min()), int(np.nonzero(alpha[y])[0].max()))
            for y in range(H) if alpha[y].any()}


def form_report(comp, blobs, names=None):
    """Material form of the roll, pack, back tail and ponytail tip for one version (v13 render or v12's locked layers)."""
    vis = visible_masks(blobs, names)
    roll = blobs["bedroll"]
    ra = roll[..., 3] > 0
    rb = bbox(ra)
    teal = {hex_rgb(PALETTE[k]) for k in "gqG"}
    deep_q = hex_rgb(PALETTE["Q"])
    cores = []                    # deep Q texels whose four neighbours are all lighter teal: the rolled end's core
    for y in range(rb[1] + 1, rb[3]):
        for x in range(rb[0] + 1, rb[2]):
            if ra[y, x] and tuple(roll[y, x, :3]) == deep_q and all(
                    ra[y + dy, x + dx] and tuple(roll[y + dy, x + dx, :3]) in teal
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                cores.append([x, y])
    corners_clear = all(not ra[y, x] for x in (rb[0], rb[2]) for y in (rb[1], rb[3]))
    leather = {hex_rgb(PALETTE[k]) for k in "lL"}
    bind = {}                     # binding texels per row
    for y in range(rb[1], rb[3] + 1):
        xs = [x for x in range(rb[0], rb[2] + 1) if ra[y, x] and tuple(roll[y, x, :3]) in leather]
        if xs:
            bind[y] = xs
    inner = [y for y in range(rb[1] + 2, rb[3] - 1)]
    bows = bool(bind) and all(y in bind and len(bind[y]) == 1 for y in [rb[1] + 1] + inner + [rb[3] - 1]) and \
        len({bind[y][0] for y in inner}) == 1 and bind[rb[1] + 1][0] == bind[rb[3] - 1][0] == bind[inner[0]][0] + 1
    pa = blobs["pack"][..., 3] > 0
    pe = row_extents(pa)
    pw = {y: b - a + 1 for y, (a, b) in pe.items()}
    widest = max(pw.values())
    pack_rows = sorted(pe)
    flap_rows = sorted({y for y in pack_rows if y <= pack_rows[0] + 6 and any(
        tuple(blobs["pack"][y, x, :3]) == hex_rgb(PALETTE["L"]) for x in range(W) if pa[y, x])})
    below = (blobs["coat-skirt"][..., 3] > 0) | (blobs["hip-drape"][..., 3] > 0)
    pack_gap = None               # transparent rows between the pack bottom and the coat skirt / drape, per column
    for x in range(W):
        py, by = np.nonzero(pa[:, x])[0], np.nonzero(below[:, x])[0]
        by = by[by > (py.max() if len(py) else H)] if len(py) else by
        if len(py) and len(by):
            g = int(by.min() - py.max() - 1)
            pack_gap = g if pack_gap is None else min(pack_gap, g)
    x0, x1, y0, y1 = BACK_REGION
    back = np.zeros((H, W), bool)
    back[y0:y1 + 1, x0:x1 + 1] = True
    skirt = blobs["coat-skirt"][..., 3] > 0
    tail = skirt.copy()
    tail[:, 32:] = False          # the back tail: everything left of the split
    pt = blobs["ponytail"][..., 3] > 0
    pt_rows = row_extents(pt)
    last = max(pt_rows)
    return {
        "roll_bbox": rb, "roll_texels": int(ra.sum()), "roll_visible_texels": int(vis["bedroll"].sum()),
        "roll_ringed_core_texels": cores, "roll_bbox_corners_transparent": corners_clear,
        "roll_binding_columns_by_row": {str(y): v for y, v in bind.items()}, "roll_binding_bows_toward_cap": bows,
        "pack_bbox": bbox(pa), "pack_texels": int(pa.sum()), "pack_visible_texels": int(vis["pack"].sum()),
        "pack_row_widths": {str(y): w for y, w in pw.items()}, "pack_widest_row_width": widest,
        "pack_top_row_width": pw[pack_rows[0]], "pack_bottom_row_width": pw[pack_rows[-1]],
        "pack_flap_edge_rows_with_L": flap_rows,
        "pack_bottom_to_skirt_or_drape_min_gap_rows": pack_gap,
        "back_region_xywh": [x0, y0, x1 - x0 + 1, y1 - y0 + 1],
        "back_region_visible_deep_slate_C": keycount(comp, back, "C"),
        "back_region_visible_mid_slate_c": keycount(comp, back, "c"),
        "back_region_visible_dark_C_d_l_L_1_excl_outline": keycount(comp, back, "CdlL1"),
        "back_tail_bbox": bbox(tail), "back_tail_texels": int(tail.sum()),
        "back_tail_visible_C": keycount(comp, vis["coat-skirt"] & tail, "C"),
        "back_tail_visible_c": keycount(comp, vis["coat-skirt"] & tail, "c"),
        "hip_drape_visible_teal": keycount(comp, vis["hip-drape"], "QqgG"),
        "ponytail_bottom_row": last, "ponytail_bottom_row_opaque": int(pt[last].sum()),
        "ponytail_row_above_bottom_opaque": int(pt[last - 1].sum()),
    }


def pose_report(comp, blobs):
    v12_png, v12_layers, v12_order, _ = v12_reference()
    return {"identity_v13": identity_report(comp, blobs), "identity_v12": identity_report(v12_png, v12_layers, v12_order),
            "form_v13": form_report(comp, blobs), "form_v12": form_report(v12_png, v12_layers, v12_order),
            "boots_runtime_shadow_v13": shadow_boot_report(comp, blobs),
            "boots_runtime_shadow_v12": shadow_boot_report(v12_png, v12_layers, v12_order),
            "boots_v13": boot_report(comp, blobs), "boots_v12": boot_report(v12_png, v12_layers, v12_order),
            "lower_body_v13": lower_body_report(comp), "lower_body_v12": lower_body_report(v12_png),
            "head_alpha_identical_to_v12": bool(np.array_equal(blobs["head"][..., 3], v12_layers["head"][..., 3])),
            "head_face_texels_identical_to_v12": bool(np.array_equal(face_mask(blobs["head"]),
                                                                     face_mask(v12_layers["head"]))
                                                      and np.array_equal(blobs["head"][face_mask(blobs["head"])],
                                                                         v12_layers["head"][face_mask(blobs["head"])])),
            "declared_unchanged_layers_identical_to_v12": {n: bool(np.array_equal(blobs[n], v12_layers[n]))
                                                           for n in V12_UNCHANGED_LAYERS},
            "silhouette_texels_v12": int((v12_png[..., 3] > 0).sum()),
            "silhouette_texels_v13": int((comp[..., 3] > 0).sum())}


def pose_gates(p):
    i13, i12, f13, f12 = p["identity_v13"], p["identity_v12"], p["form_v13"], p["form_v12"]
    s13 = p["boots_runtime_shadow_v13"]
    lock = i13["loose_lock"]
    return {
        # kept from v12: proportion, head, face, identity masses (the size of the figure does not grow)
        "silhouette_texels_95_to_100pct_of_v12": 0.95 * p["silhouette_texels_v12"] <= p["silhouette_texels_v13"]
        <= p["silhouette_texels_v12"],
        "near_thigh_5_colour_texels_rows_41_50": min(i13["near_thigh_colour_texels_per_row_41_50"]) >= 5,
        "head_outline_identical_to_v12": p["head_alpha_identical_to_v12"],
        "face_texels_identical_to_v12": p["head_face_texels_identical_to_v12"],
        "declared_unchanged_layers_identical": all(p["declared_unchanged_layers_identical_to_v12"].values()),
        "loose_lock_separated_both_sides": lock is not None and all(
            (r["clear_cols_to_tail"] or 0) >= 1 and (r["clear_cols_to_head"] or 0) >= 1 for r in lock["rows"]),
        "hair_tie_not_a_pale_bead": i13["hair_tie_visible_pale_texels"] == 0,
        "tail_and_lock_clear_of_roll": i13["tail_or_lock_to_roll_min_vertical_gap_rows"] is not None
        and i13["tail_or_lock_to_roll_min_vertical_gap_rows"] >= 2,
        "shirt_wedge_same_as_v12": i13["shirt_visible_W_w_per_row_23_37"] == i12["shirt_visible_W_w_per_row_23_37"],
        "scarf_compact_ends_row_26": i13["scarf_bbox"][3] <= 26,
        "teal_scarf_and_roll_present": i13["teal_texels_visible"]["scarf-neck"] >= 40
        and i13["teal_texels_visible"]["bedroll"] >= 40,
        "hand_shows_skin_and_glove": i13["fist_skin_texels"] >= 6 and i13["fist_glove_texels"] >= 4,
        "bare_forearm_and_rolled_cuff": i13["forearm_skin_texels"] >= 8 and i13["sleeve_rolled_cuff_texels_P_p"] >= 6,
        # roll and pack: material form, not bigger than v12
        "roll_and_pack_not_larger_than_v12": f13["roll_texels"] <= f12["roll_texels"]
        and f13["pack_texels"] < f12["pack_texels"] and f13["pack_visible_texels"] < f12["pack_visible_texels"],
        "roll_end_cap_ringed_core": len(f13["roll_ringed_core_texels"]) >= 1,
        "roll_rounded_corners": f13["roll_bbox_corners_transparent"],
        "roll_binding_bows_toward_cap": f13["roll_binding_bows_toward_cap"],
        "pack_tapers_to_top_and_bottom": f13["pack_top_row_width"] <= f13["pack_widest_row_width"] - 3
        and f13["pack_bottom_row_width"] <= f13["pack_widest_row_width"] - 4,
        "pack_flap_edge_curves_over_3_rows": len(f13["pack_flap_edge_rows_with_L"]) >= 3,
        "pack_clear_of_coat_tail_and_drape": (f13["pack_bottom_to_skirt_or_drape_min_gap_rows"] or 0) >= 1,
        # the back stops reading as one black bundle
        # the tail is what changed; the coat torso back and the far trouser keep v12's deep slate on purpose, so the
        # whole back region only drops by about two fifths (reported in form_v12/form_v13, not gated)
        "back_tail_deep_slate_C_le_third_of_v12": f13["back_tail_visible_C"] <= f12["back_tail_visible_C"] / 3,
        "back_tail_shorter_and_narrower_than_v12": f13["back_tail_bbox"][3] < f12["back_tail_bbox"][3]
        and f13["back_tail_bbox"][0] > f12["back_tail_bbox"][0],
        "back_tail_mostly_mid_slate": f13["back_tail_visible_c"] > 2 * f13["back_tail_visible_C"],
        "ponytail_tip_one_point": f13["ponytail_bottom_row_opaque"] == 1
        and f13["ponytail_row_above_bottom_opaque"] <= 3,
        # planted feet against the REAL runtime contact shadow
        "lower_body_no_orange": p["lower_body_v13"]["warm_orange_texels"] == 0,
        "feet_on_paving_all_deep": all(b["on_paving_lit_D_u_p_P"] == 0 for b in s13.values()),
        "feet_in_shadow_rows_64_66_lit_ge_80pct": all(b["rows_64_66_in_shadow_lit_share"] >= 0.8 for b in s13.values()),
    }


# ===================================================================================================== metrics
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
    crown_cols = [x for x in range(HEAD_COLS[0], HEAD_COLS[1] + 1) if m[CROWN_ROW, x] and not m[:CROWN_ROW, x].any()]
    head_top = min(int(np.nonzero(m[:, x])[0].min()) for x in crown_cols) if crown_cols else None
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
    """Texel counts per material group."""
    groups = {"teal": "QqgG", "steel": "mMZ", "skin": "Ssx", "eye-brow": "E", "hair": "1234h",
              "slate (coat, sleeve, far trouser, leg back edges)": "Cco", "shirt": "Ww",
              "pale beige (cuff, buckle, strap, hair tie)": "Pp", "trousers": "Tt", "dark leather": "Ll",
              "deep brown (boots, pack)": "dD", "outsole welt": "u"}
    rgb = comp[..., :3]
    m = comp[..., 3] > 0
    out = {}
    for g, keys in groups.items():
        out[g] = sum(int((m & (rgb == np.array(hex_rgb(PALETTE[k]), np.uint8)).all(-1)).sum()) for k in keys)
    return out


# ===================================================================================================== preview
def on_bg(rgba, bg, zoom):
    im = Image.new("RGBA", (rgba.shape[1], rgba.shape[0]), tuple(bg) + (255,))
    im.alpha_composite(Image.fromarray(rgba, "RGBA"))
    return im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)


def game_scale(rgba, nosprite):
    """The party capture as Godot draws it: each texel a k x k block at the texture origin over the no-sprite frame."""
    im = Image.open(nosprite).convert("RGBA")
    k = im.width // 640
    big = Image.fromarray(rgba, "RGBA").resize((W * k, H * k), Image.NEAREST)
    im.alpha_composite(big, CAPTURE_ORIGIN[im.width])
    return im


def preview(out_dir, nosprites=()):
    """Separate inspection images (one subject each, no sheets), written outside the repo."""
    blobs, comp = render()
    os.makedirs(out_dir, exist_ok=True)
    for tag, bg in (("floor-mid", (88, 84, 80)), ("floor-light", (150, 140, 124)), ("dark", (40, 42, 48))):
        on_bg(comp, bg, 8).save(os.path.join(out_dir, f"v13_x8_{tag}.png"))
    for path in nosprites:
        tag = os.path.splitext(os.path.basename(path))[0]
        full = game_scale(comp, path)
        k = full.width // 640
        full.save(os.path.join(out_dir, f"v13_game-scale_{tag}.png"))
        full.crop((120 * k, 180 * k, 360 * k, 300 * k)).save(os.path.join(out_dir, f"v13_game-scale-crop-1x_{tag}.png"))
        crop = full.crop((240 * k, 190 * k, 340 * k, 280 * k))
        z = 8 // k
        crop.resize((crop.width * z, crop.height * z), Image.NEAREST).save(
            os.path.join(out_dir, f"v13_game-scale-crop-x{z}_{tag}.png"))
    p = pose_report(comp, blobs)
    print(json.dumps({**stats(comp), "material_texels_v13": region_counts(comp), "pose": p,
                      "pose_gates": pose_gates(p), "silhouette_vs_v12": silhouette_report(comp, blobs)}))


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
                      "file_format": "0", "file_name": json.dumps("sideview-idle-right-static-unapproved-v13"),
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
    dt = (2026, 10, 17, 23, 56, 14)     # fixed (zip needs even seconds) -> byte-identical rebuilds
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
    dt = (2026, 10, 17, 23, 56, 14)
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", dt), "image/openraster", zipfile.ZIP_STORED)
        z.writestr(zipfile.ZipInfo("stack.xml", dt), "\n".join(stack) + "\n", zipfile.ZIP_DEFLATED)
        for name in LAYER_NAMES:
            z.writestr(zipfile.ZipInfo(f"data/{name}.png", dt), png_bytes(blobs[name]), zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("mergedimage.png", dt), png, zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("Thumbnails/thumbnail.png", dt), png, zipfile.ZIP_DEFLATED)
    return buf.getvalue()


def recompose(layer_rgba):
    """Plain 'over' of binary-alpha layers in order (guides are hidden and skipped)."""
    comp = np.zeros((H, W, 4), np.uint8)
    for name in LAYER_NAMES[:-1]:
        a = layer_rgba[name]
        m = a[..., 3] == 255
        comp[m] = a[m]
    return comp


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
    tmp = tempfile.mkdtemp(prefix="wb-fv13-")
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
    "far-leg": "far leg braced back, trouser 5 colour texels wide (deep slate C, spruce crease T); boot (v12 outline) re-keyed by the runtime contact shadow: dark cuff (l), deep shaft (d) with a pale strap (p) and a deep heel on the paving, lit top plane (D), pale toe glint (p) and warm-grey welt (u) inside the shadow ellipse, heel lifted",
    "hip-drape": "v8 teal back-hip cloth behind the coat skirt, v13: a short tab from the belt (rows 39-47) showing two or three texels left of the narrower back tail (v12: a long stripe down the whole tail edge)",
    "pack": "slumped canvas pack (v13; v12 a 13x13 box): narrow top under the overhanging roll, lit flap top plane (D), flap edge (L) curving down to the middle with a pale buckle (P), body bulging to x15 with a soft highlight (D), strap/crease (l), rounded bottom on row 37 clear of the coat tail",
    "bedroll": "teal bedroll as a cylinder (v13; v12 a 13x7 box), 12x7: elliptical end cap (ring q/g round a dark core Q, curved seam Q), lit top (G), mid (g), deep underside (q/Q), rounded front end, one leather binding (l/L) bowing toward the cap",
    "ponytail": "high tied ponytail, v12 hook and strands; the forked tip is now one clean taper",
    "loose-lock": "separate loose lock falling from the hook tip at the nape, one transparent column to the tail and to the head on every row (v12, unchanged)",
    "near-leg": "near leg forward, thigh 5 colour texels wide (T body, t edge, C back), cool grey knee pad (m/M) on a dark strap, spruce shin; boot (v12 outline) re-keyed by the runtime contact shadow: dark cuff/shaft with the pale strap (P) and a deep toe on the paving, lit top plane (D) and warm-grey welt (u) inside the shadow ellipse",
    "coat": "v8 storm-slate coat torso and belt (v12, unchanged)",
    "coat-skirt": "split coat skirt: v12 lit front panel; back tail shorter (to row 53, v12 56) and narrower (to x18, v12 x16), mid slate (c) with two deep fold lines (C), deep only under the belt, lit split edge (o), dark-leather hem (l) rising toward the split",
    "shirt-lapel": "white shirt wedge framed by lit lapel texels and a dark lapel line (v12, unchanged)",
    "near-arm": "sword arm reaching forward with the sleeve rolled to the elbow (v12, unchanged)",
    "insignia": "teal 3x3 diamond on the upper sleeve (v12, unchanged; a colour placement at 1x)",
    "sword-blade": "ordinary short sword blade raised forward at 45 degrees (v10-v12, unchanged; same reach)",
    "sword-guard": "small steel crossguard square to the blade (v10-v12, unchanged)",
    "fist": "fingerless dark glove with bare skin knuckles and thumb round the grip (v12, unchanged)",
    "head": "v12 head and face texel-for-texel (unchanged)",
    "hair-tie": "dark leather hair band where the ponytail leaves the head (v12, unchanged)",
    "collar": "raised coat collar standing behind the nape (v12, unchanged)",
    "scarf-neck": "compact teal scarf (v12, unchanged)",
    "collar-front": "front point of the raised coat collar over the scarf's front edge (v12, unchanged)",
    "guides": f"hidden + locked #ff00ff: cell border, ticks on crown row {CROWN_ROW} and sole row {SOLE_ROW}, pin {list(PIN)}",
}


def make_manifest(png, pxo, ora, comp, flat_from_pixelorama):
    blobs = render()[0]
    st = stats(comp)
    pose = pose_report(comp, blobs)
    m = {
        "project": SLUG,
        "subject": "female protagonist side-view battle idle, facing right, ONE static frame (native 0.65 on-screen size)",
        "version": VER, "status": "UNAPPROVED, NONRUNTIME test-only candidate", "art_approved": False,
        "runtime_integrated": False, "game_bible_or_acceptance_counters_changed": False, "animation": False,
        "sprite_acceptance_count": "0/52 (unchanged)",
        "node_scale_intended": 1.0, "display_proportion_equivalent": 0.65,
        "refines": {"files": V12_LOCKS,
                    "hash_algorithm": "sha256-bytes for .png/.pxo/.ora; sha256-text-lf-v1 for the .json manifest",
                    "relationship": "same cell/pin/sole/crown rows, head, face, coat torso, shirt, scarf, arm, hand, "
                                    "blade, insignia, collar, loose lock and hair band byte-identical to v12; the "
                                    "bedroll becomes a cylinder with an end cap and a bowing binding, the pack a "
                                    "slumped sack with a curved flap (both smaller), the back coat tail shorter, "
                                    "narrower and mid-slate, the hip drape a short tab, the ponytail tip one taper, "
                                    "and the boot keys follow the runtime contact shadow; v12 left untouched",
                    "silhouette_vs_v12": silhouette_report(comp, blobs)},
        "pose": pose,
        "pose_gates": pose_gates(pose),
        "identity_references": {"character_sheet": CHARACTER_SHEET_REL, "v8_south_static": V8_SOUTH_REL},
        "feedback_addressed": "Codex visual review of v12 in the v13 dispatch " + DISPATCH_REL + ": pack and "
                              "bedroll read as two stacked boxes; a large black tail/roll bundle dominates the back; "
                              "bright-floor foot separation still weak; the v12 review overlay drew a 23.4 shadow "
                              "while the game draws 18. Earlier: creator answer on v11 '继续精修静止帧' (not accepted)",
        "coat_colour_note": "the coat keeps the approved v8 storm-slate ramp (C/c/o); the v13 dispatch confirms no new "
                            "creator colour decision is needed to follow the approved v8 static identity",
        "runtime_contact_shadow": {"radius": RUNTIME_SHADOW_RADIUS, "scale_y": RUNTIME_SHADOW_SCALE_Y,
                                   "centre_screen": [300, 272], "texel_origin_screen": [268, 204],
                                   "colour_rgba": [0.02, 0.03, 0.05, 0.42]},
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


def static_gates(a, st):
    return {
        "binary_alpha": st["alpha_values"] == [0, 255],
        "no_off_palette_colour": not st["colours_outside_palette"],
        "colours_le_32": st["colours"] <= 32,
        "sole_on_row_67_same_as_v12": st["sole_row"] == SOLE_ROW,
        "crown_on_row_7_same_as_v12_0p65_proportion": st["crown_row_measured"] == CROWN_ROW,
        "leftmost_texel_ge_x15_liang_gap_kept": st["alpha_bounds_inclusive"][0] >= 15,
        "rightmost_texel_le_v12_sentry_gap_kept": st["alpha_bounds_inclusive"][2] <= 62,
        "nothing_at_or_below_pin_row": st["pin_row_clear"],
        "both_boots_touch_sole_row": bool((a[SOLE_ROW, 20:PIN[0], 3] > 0).any() and (a[SOLE_ROW, PIN[0]:, 3] > 0).any()),
        "transparent_border": bool(not a[0, :, 3].any() and not a[-1, :, 3].any()
                                   and not a[:, 0, 3].any() and not a[:, -1, 3].any()),
    }


def structure_ok(sil):
    return (sil["layers_added_vs_v12"] == V12_LAYER_NAMES_PLUS and sil["layers_removed_vs_v12"] == []
            and sil["palette_keys_removed_vs_v12"] == REMOVED_KEYS_VS_V12
            and sil["palette_keys_added_vs_v12"] == ADDED_KEYS_VS_V12 and sil["palette_shared_keys_same_colour"])


def build(exe):
    lock = v12_lock()
    if not lock["unchanged"]:
        raise SystemExit(f"v12 changed: {lock}")
    blobs, comp = render()
    st = stats(comp)
    sg = static_gates(comp, st)
    pg = pose_gates(pose_report(comp, blobs))
    sil = silhouette_report(comp, blobs)
    if not all(sg.values()) or not all(pg.values()) or not structure_ok(sil):
        raise SystemExit(f"static/identity gate failed: {json.dumps({'static': sg, 'identity': pg})}")
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
    if not v12_lock()["unchanged"]:
        raise SystemExit("v12 changed during build")


def check(exe):
    report = {"status": "UNAPPROVED, NONRUNTIME test-only candidate", "v12_lock_before": v12_lock()}
    blobs, comp = render()
    out = repo_path(OUT_DIR_REL)
    png = read_bytes(os.path.join(out, PNG_NAME))
    pxo = read_bytes(os.path.join(out, PXO_NAME))
    ora = read_bytes(os.path.join(out, ORA_NAME))
    man = json.loads(read_bytes(os.path.join(out, MANIFEST_NAME)))
    mode, size, a = decode(png)
    st = stats(a)
    g = {"png_rgba_68x72": mode == "RGBA" and size == (W, H), "png_equals_tool_render": a.tobytes() == comp.tobytes()}
    g.update(static_gates(a, st))
    g.update({
        "manifest_hashes_match": (man["files"]["png"]["sha256"] == sha256_bytes(png)
                                  and man["files"]["pxo"]["sha256"] == sha256_bytes(pxo)
                                  and man["files"]["ora"]["sha256"] == sha256_bytes(ora)),
        "manifest_unapproved_flags": (man["art_approved"] is False and man["runtime_integrated"] is False
                                      and man["game_bible_or_acceptance_counters_changed"] is False),
        "rebuild_editables_byte_identical": make_pxo(png_bytes(comp), blobs) == pxo
                                            and make_ora(png_bytes(comp), blobs) == ora,
    })
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
    sil = silhouette_report(a, blobs)
    report["silhouette_vs_v12"] = sil
    g["layers_and_palette_vs_v12_as_declared"] = structure_ok(sil)
    g["manifest_silhouette_matches_fresh"] = man["refines"]["silhouette_vs_v12"] == json.loads(json.dumps(sil))
    pose = pose_report(a, blobs)
    report["pose"] = pose
    pg = pose_gates(pose)
    g.update(pg)
    g["manifest_pose_matches_fresh"] = man["pose"] == json.loads(json.dumps(pose)) and man["pose_gates"] == pg
    if exe:
        px, flat = pixelorama_roundtrips(exe, pxo, ora, blobs, comp)
        report["pixelorama_1_2_3_headless"] = px
        g["pixelorama_roundtrips"] = all(v["pass"] for v in px.values() if isinstance(v, dict)) and \
            px["real_appdata_pixelorama_untouched_except_heartbeat"]
        g["png_equals_fresh_pixelorama_flat_export"] = flat == png
    report["metrics"] = {**st, "material_texels": region_counts(a)}
    report["v12_lock_after"] = v12_lock()
    g["v12_unchanged"] = report["v12_lock_before"]["unchanged"] and report["v12_lock_after"]["unchanged"]
    report["gates"] = g
    report["gates_passed"] = f"{sum(bool(v) for v in g.values())}/{len(g)}"
    report["result"] = "PASS" if all(g.values()) else "FAIL"
    print(json.dumps(report, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    return 0 if report["result"] == "PASS" else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=["preview", "build", "check"])
    ap.add_argument("out", nargs="?")
    ap.add_argument("nosprite", nargs="*", help="preview only: no-sprite party captures (1280x720 and/or 640x360)")
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
