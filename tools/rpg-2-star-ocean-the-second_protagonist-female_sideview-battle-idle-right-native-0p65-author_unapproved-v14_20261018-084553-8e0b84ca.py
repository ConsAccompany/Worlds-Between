"""UNAPPROVED, NONRUNTIME test-only pilot v14: female protagonist side-view battle idle, facing right, ONE static frame.

Cloth-volume and leg-anatomy pass over v13 (bounded fork of the v13 author tool; no motion, no batch, no runtime swap).
Same cell (68x72), pin (32, 68), sole row 67, crown row 7, head outline, coat torso, shirt, scarf, arm, hand, blade,
insignia, collar, ponytail, loose lock and hair band as v13, so the approved 0.65 battle display proportion, the foot pin,
the blade reach and the v8 storm-slate coat identity are unchanged. v13's files (tracked at 160b823) are read
(hash-gated) and never written.

Targets the root review of v13 (overly busy hard-edged silhouette, thick boot masses, dark-floor lower-body merging, v12's
full coat partly lost) and the creator's standing request to keep refining the static frame ("继续精修静止帧"):
  V14_TARGETS below lists each change; the v13 header follows (its targets are kept unless changed).

v13 header:
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
                  palette diff vs v13, silhouette report vs v13, identity / form / leg-anatomy / silhouette-edge / pack
                  gates (manifest pose_gates), layer-stack recomposition of the .pxo and .ora; writes nothing

Run with the real Python in isolated mode:  python -I -B <this file> preview <dir> | build | check
"""
import argparse, colorsys, hashlib, io, json, os, shutil, subprocess, sys, tempfile, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
VER = "unapproved-v14"
STAMP = "20261018-084553"
RUN_ID = "8e0b84ca"
W, H = 68, 72
PIN = (32, 68)            # same as v03-v12: first transparent row under the soles, between the feet
CROWN_ROW = 7             # same as v03-v12: head crown row; soles end on row 67 -> crown-to-sole 61 rows
SOLE_ROW = 67
HEAD_COLS = (24, 47)      # crown columns are searched here (same as v10-v12)
OUT_DIR_REL = "game/assets/characters/combat-sideview-pilots"
_V13 = "rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_"
V13_LOCKS = {             # v13 (tracked since 7553581) is the comparison base and is read-only for this tool
    OUT_DIR_REL + "/" + _V13 + "unapproved-v13_20261017-235615-1195f40e.png":
        "5b295aa1d19dcceb69b740e983eb2695d966701a4ead4ad8bbb72f13af6ebdb2",
    OUT_DIR_REL + "/" + _V13 + "editable-layers_unapproved-v13_20261017-235615-24e9a137.pxo":
        "4e707496f3e27fb374600d944398e43d81209a3227dff27079d10715f955a6bc",
    OUT_DIR_REL + "/" + _V13 + "editable-layers_unapproved-v13_20261017-235615-3fffbeeb.ora":
        "0fb1eda94deb9721446e543883779975bbb2983a516b0acb1017d83373088fb7",
    OUT_DIR_REL + "/" + _V13 + "manifest_unapproved-v13_20261017-235615-96c04b57.json":
        "2e262894f802c0d61b1c1c93edf105db141f8bc82e63956d8525599900e65d75",
}
V13_PNG_REL, V13_PXO_REL, V13_ORA_REL, V13_MANIFEST_REL = list(V13_LOCKS)
# v12 (tracked at c20118d) is read only for the coat-fullness comparison (the root review says v12's full coat was
# partly lost in v13); same hashes as the v13 tool's locks
_V12_ORA_REL = OUT_DIR_REL + "/" + _V13 + "editable-layers_unapproved-v12_20261017-224530-2ae3fe34.ora"
_V12_ORA_SHA = "4fde9395cab3cf66377f12f6f4b0c309308cc56fd43857e7eda12ca5f3c8772d"
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

PALETTE = {               # v13's (= v12's) 31 keys, unchanged; v14 reuses the warm grey u for restrained lit planes
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
REMOVED_KEYS_VS_V13 = []                          # sorted() order; v14 keeps v13's palette exactly
ADDED_KEYS_VS_V13 = []

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

# v14 legs and boots (v13: straight tubes into 13-15 texel boot blocks with a full-width warm-grey welt and a 3-4 row lit
# band). Runtime contact shadow (radius 18, y scale 0.28, centred on the pin), texel columns inside per row: row 63
# x24-39, row 64 x19-44, row 65 x16-47, row 66 x15-48, row 67 x14-49; rows 57-62 stand on paving (archive L ~110,
# outskirts ~76). v14 boot anatomy: a dark cuff band (L) where the trouser tucks in, a shaft only as wide as the shin
# (5 colour texels, v13 8), an ankle, a heel that steps back one texel, a vamp that slopes down to a rounded toe, a thin
# lit-leather welt. Values: shaft, upper foot and toe on the paving deep (d); the vamp slope and toe cap lit (D, one
# warm-grey u texel); inside the shadow ellipse the foot's lowest side row and the welt are lit leather (D), two rows (v13:
# three to four lit rows plus a full-width warm-grey welt), so the foot base does not sink into the contact shadow.
# far (back) leg in the body's shadow: a straighter brace with a small knee bend (v13: one diagonal tube), deep slate back
# edge (C), spruce body (T) and a lit spruce front edge (t) toward the gap between the legs
rows("far-leg", [
    (46, 28, "KCTTTK"),
    (47, 28, "KCTTTK"),
    (48, 27, "KCTTTtK"),
    (49, 27, "KCTTTtK"),
    (50, 26, "KCTTTtK"),
    (51, 26, "KCTTTtK"),
    (52, 25, "KCCTtKK"),
    (53, 25, "KCCTtK"),
    (54, 24, "KCCTtK"),
    (55, 24, "KCCTtK"),
    (56, 23, "KCCTtK"),
    (57, 22, "KLLLLLK"),
    (58, 22, "KdddddK"),
    (59, 22, "KdddddK"),
    (60, 21, "KdddddDK"),
    (61, 20, "KddddddDDK"),
    (62, 20, "KdddddddDDK"),
    (63, 20, "KddddddddDuK"),
    (64, 20, "KdddddddddDK"),
    (65, 20, "KDDDDDDDDDDK"),
    (66, 20, "KDDDDDDDDDK"),
    (67, 21, "KKKKKKKKK"),
])

# v8's teal back-hip cloth hung BEHIND the coat skirt. v14: tucked under the pack and hanging from the belt, it fills the
# notch between the pack bottom and the back tail (v13: a tab sticking out of the silhouette at the hip), so the back
# contour runs pack -> drape -> tail in one line
rows("hip-drape", [
    (38, 18, "KgqqqK"),
    (39, 19, "KgqqQK"),
    (40, 20, "KgqQK"),
    (41, 21, "KqQK"),
    (42, 22, "KK"),
])

# v14 pack: the v13 slumped sack outline kept, the inside calmed (v13: six dark L/l marks across the face): one lit flap
# (D) whose edge (l) dips in a curve to a pale buckle (P), one strap (l) down from it, a body in one deep brown (d), a
# shadowed back edge (l, L) away from the light and a dark underside row (L)
rows("pack", [
    (26, 19, "KKKKKKKK"),
    (27, 18, "KDDDDDDDdK"),
    (28, 17, "KdDDDDDDDdK"),
    (29, 16, "KldDDDDDDDdK"),
    (30, 15, "KlddlDDDldddK"),
    (31, 15, "KldddlPlddddK"),
    (32, 15, "KlddddldddddK"),
    (33, 15, "KlddddldddddK"),
    (34, 15, "KLldddlddddK"),
    (35, 16, "KLlddldddK"),
    (36, 17, "KLLLLLLLK"),
    (37, 18, "KKKKKKK"),
])

# small steel canister hung on the pack's visible side (character sheet + v8 identity item; v05-v13 had none): two steel
# texels wide, lit on the right toward the light (M), subordinate to the pack at 1x; inside the pack's outline, so the
# silhouette does not change
rows("canister", [
    (32, 17, "KK"),
    (33, 16, "KmMK"),
    (34, 16, "KmMK"),
    (35, 16, "KmmK"),
    (36, 17, "KK"),
])

# v13 teal bedroll cylinder (end cap ring round a dark core, bowing binding), v14: the top edge is outlined in deep teal
# (Q) instead of black so the lit top reads as a rounded surface, not a hard box lid
rows("bedroll", [
    (20, 17, "KQQQQQQK"),
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

# v14 near (front) leg: the thigh runs down and forward from under the front panel to a knee that juts forward of the
# shin (v13: thigh and shin one straight column), the cool grey knee pad (m/M) on the knee's front on a dark strap (L),
# the shin drops back to the ankle; spruce body (T), deep slate back edge (C), lit spruce top/front plane (t) facing
# the light; boot as the far one with the vamp slope lit (D) and the foot's lower side lit only inside the shadow
rows("near-leg", [
    (42, 33, "KCTTTtK"),
    (43, 34, "KCTTTtK"),
    (44, 34, "KCTTTTtK"),
    (45, 35, "KCTTTTtK"),
    (46, 36, "KCTTTTuK"),
    (47, 36, "KCTTTTtuK"),
    (48, 37, "KCTTTTtuK"),
    (49, 38, "KCTTTtmmK"),
    (50, 38, "KCTTTLmMK"),
    (51, 38, "KCCTTLmMK"),
    (52, 38, "KCTTTLmK"),
    (53, 38, "KCTTtuK"),
    (54, 38, "KCTTtuK"),
    (55, 38, "KCTTtuK"),
    (56, 38, "KCTTtuK"),
    (57, 38, "KLLLLLK"),
    (58, 38, "KdddddK"),
    (59, 38, "KdddddK"),
    (60, 38, "KddddDK"),
    (61, 37, "KdddddDDK"),
    (62, 37, "KddddddDDK"),
    (63, 37, "KdddddddDuK"),
    (64, 37, "KddddddddDuK"),
    (65, 37, "KDDDDDDDDDdK"),
    (66, 37, "KDDDDDDDDDK"),
    (67, 38, "KKKKKKKKK"),
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
# v14: the v12/v13 front panel is kept; the back tail gets v12's fullness back (flares to x17, hem outline on row 54;
# v13 x18 / row 53, v12 x16 / row 56) as cloth with volume instead of v12's deep wedge or v13's two dark fold lines: a shadowed
# back edge turning away from the light (C), a mid slate body (c), ONE broad fold running from the belt toward the back
# corner (its shadowed flank C, its lit ridge o), the lit split edge (o, C), and a dark-leather hem (l) that rises in one
# smooth diagonal toward the split so the far leg shows under it
rows("coat-skirt", [
    (40, 23, "KCCCCCCc" + "o" * 14 + "K"),
    (41, 22, "KCccCoccooK" + "ooooocooooooK"),
    (42, 22, "KCccCoccoCK" + "ooooocooooooK"),
    (43, 21, "KCcccCoccoCK" + "ooooocoooocK"),
    (44, 21, "KCccCocccoCK" + "ooooocoocllK"),
    (45, 20, "KCcccCocccoCK" + "ooooccllKK"),
    (46, 20, "KCcccCocccoCK" + "ccccllK"),
    (47, 20, "KCccCocccoCK" + "lllK"),
    (48, 19, "KCcccCocccoc"),
    (48, 31, "KKKK"),
    (49, 19, "KCcccCocccclK"),
    (50, 18, "KCcccCocccllK"),
    (51, 18, "KCccCoclllKK"),
    (52, 17, "KCccClllKKK"),
    (53, 17, "KllllKKK"),
    (54, 17, "KKKKK"),
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
.K111122212SS21SSK.
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
V13_LAYER_NAMES_PLUS = ["canister"]           # v14 = v13's 20 layer names + the canister over the pack (+ guides)
V13_UNCHANGED_LAYERS = ["ponytail", "loose-lock", "coat", "shirt-lapel", "near-arm", "insignia", "sword-blade",
                        "sword-guard", "fist", "hair-tie", "collar", "scarf-neck",
                        "collar-front"]       # declared byte-identical to v13's .ora layers (checked)
V14_CHANGED_LAYERS = ["far-leg", "hip-drape", "pack", "bedroll", "near-leg", "coat-skirt", "head"]
FACE_CHANGED_TEXELS = [(41, 13), (42, 13), (43, 13)]   # the only head texels v14 recolours (brow row; alpha unchanged)
BACK_REGION = (0, 31, 20, 56)                 # x0, x1, y0, y1 inclusive: pack, roll, back tail, behind the body
V14_TARGETS = [
    "back coat tail: v12's fullness back (to x17 / row 54) as cloth with one broad fold, not v12's deep wedge or v13's "
    "two dark fold lines",
    "legs: near knee juts forward of the shin, shin drops back to the ankle; far leg braced back with a small knee bend "
    "in the body's shadow (deep slate body, spruce front edge)",
    "boots: shaft as wide as the shin (5 colour texels, v13 8), heel steps back, vamp slopes to a rounded toe; dark "
    "leather with a lit vamp/toe cap and a two-row lit-leather base (lowest foot row + welt) where the foot stands in "
    "the contact shadow (v13: a 3-4 row lit band and a full-width warm-grey welt)",
    "restrained warm edge planes: the existing warm grey (u) only on light-facing planes (near thigh top, near shin "
    "front, toe caps); the silhouette edge stays black (no rim light)",
    "pack calmed to one flap, one strap, one buckle; small steel canister on its visible side (identity item); teal "
    "drape tucked under the pack so the back contour runs pack -> drape -> tail",
    "roll: v13 cylinder kept, top edge outlined in deep teal instead of black",
    "face: brow drawn in hair brown and separated from a smaller lash line (more mature read); head outline unchanged",
]


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
    still matches (the v13 manifest blob is LF; a core.autocrlf=true checkout writes it with CRLF)."""
    data = read_bytes(repo_path(rel))
    return sha256_bytes(data.replace(b"\r\n", b"\n") if rel.endswith(".json") else data)


def v13_lock():
    files = {rel: lock_hash(rel) for rel in V13_LOCKS}
    return {"files": files, "unchanged": all(files[rel] == want for rel, want in V13_LOCKS.items())}


def decode(png):
    im = Image.open(io.BytesIO(png))
    return im.mode, im.size, np.array(im.convert("RGBA"))


# ===================================================================================================== v13 comparison
def v13_reference():
    """v13's flat PNG, its per-layer RGBA from the locked .ora, and its manifest palette (all read-only)."""
    png = decode(read_bytes(repo_path(V13_PNG_REL)))[2]
    with zipfile.ZipFile(io.BytesIO(read_bytes(repo_path(V13_ORA_REL)))) as z:
        names = [n[len("data/"):-len(".png")] for n in z.namelist() if n.startswith("data/") and n.endswith(".png")]
        layers = {n: decode(z.read(f"data/{n}.png"))[2] for n in names}
    man = json.loads(read_bytes(repo_path(V13_MANIFEST_REL)))
    order = [l["name"] for l in man["layers_bottom_to_top"]]
    return png, layers, order, man["palette"]


def v12_tail_reference():
    """v12's coat-skirt layer from its tracked .ora (sha256-gated, read-only): the coat fullness the root review says
    v13 partly lost. Returns the back tail (left of the split, x <= 31) bbox and texel count."""
    data = read_bytes(repo_path(_V12_ORA_REL))
    if sha256_bytes(data) != _V12_ORA_SHA:
        raise SystemExit("v12 .ora changed")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        stack = z.read("stack.xml").decode("utf-8")
        order = [seg.split('"')[0] for seg in stack.split('layer name="')[1:]][::-1]      # ORA lists top first
        layers = {n: decode(z.read(f"data/{n}.png"))[2] for n in order}
        merged = decode(z.read("mergedimage.png"))[2]
    skirt = layers["coat-skirt"][..., 3] > 0
    skirt[:, 32:] = False
    vis = visible_masks(layers, order)
    return {"back_tail_bbox_v12": bbox(skirt), "back_tail_texels_v12": int(skirt.sum()),
            "back_tail_visible_C_v12": keycount(merged, vis["coat-skirt"] & skirt, "C")}


def bbox(alpha):
    ys, xs = np.nonzero(alpha)
    return None if len(xs) == 0 else [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


def visible_masks(blobs, names=None):
    """Per layer: texels where that layer is the top-most opaque layer (what the viewer actually sees of it). `names`
    is the bottom-to-top order (default: this tool's layers); v13's .ora layers are passed with v13's own order."""
    names = [n for n in (names or LAYER_NAMES) if n != "guides"]
    owner = np.full((H, W), -1, np.int16)
    for i, name in enumerate(names):
        owner[blobs[name][..., 3] == 255] = i
    return {name: owner == i for i, name in enumerate(names)}


def silhouette_report(comp, blobs):
    """How v14 differs from v13: whole-sprite alpha silhouette, composite texels, per layer, palette and layer names."""
    v13_png, v13_layers, v13_order, v13_pal = v13_reference()
    a11, a10 = comp[..., 3] > 0, v13_png[..., 3] > 0
    inter, union = int((a11 & a10).sum()), int((a11 | a10).sum())
    layers = {}
    for name in LAYER_NAMES[:-1]:
        mine = blobs[name][..., 3] > 0
        theirs = v13_layers[name][..., 3] > 0 if name in v13_layers else None
        same_px = theirs is not None and np.array_equal(blobs[name], v13_layers[name])
        layers[name] = {"texels_v13": None if theirs is None else int(theirs.sum()), "texels_v14": int(mine.sum()),
                        "bbox_v13": None if theirs is None else bbox(theirs), "bbox_v14": bbox(mine),
                        "byte_identical_to_v13": bool(same_px),
                        "changed_texels": None if theirs is None else int((blobs[name] != v13_layers[name]).any(-1).sum())}
    v13_names = [n for n in v13_order if n != "guides"]
    pal10 = {k: v.lower() for k, v in v13_pal.items()}
    pal11 = {k: v.lower() for k, v in PALETTE.items()}
    return {
        "silhouette_texels_v13": int(a10.sum()), "silhouette_texels_v14": int(a11.sum()),
        "silhouette_iou": round(inter / union, 4), "silhouette_added_texels": int((a11 & ~a10).sum()),
        "silhouette_removed_texels": int((a10 & ~a11).sum()),
        "silhouette_bbox_v13": bbox(a10), "silhouette_bbox_v14": bbox(a11),
        "composite_changed_texels": int((comp != v13_png).any(-1).sum()),
        "layers": layers,
        "byte_identical_layers": [n for n in LAYER_NAMES[:-1] if layers[n]["byte_identical_to_v13"]],
        "layers_added_vs_v13": [n for n in LAYER_NAMES[:-1] if n not in v13_names],
        "layers_removed_vs_v13": [n for n in v13_names if n not in LAYER_NAMES],
        "layer_order_v13": v13_order,
        "palette_keys_removed_vs_v13": sorted(set(pal10) - set(pal11)),
        "palette_keys_added_vs_v13": sorted(set(pal11) - set(pal10)),
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
    """Identity and mass numbers for one version: v14 (this render) or v13 (its locked .ora layers and order)."""
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
    (tx, ty) on screen (268 + tx, 204 + ty), radius 18, y scale 0.28). The v14 captures measure the real pixels too."""
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
    """Material form of the roll, pack, back tail and ponytail tip for one version (v14 render or v13's locked layers)."""
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
        "back_tail_visible_o": keycount(comp, vis["coat-skirt"] & tail, "o"),
        "hip_drape_bbox": bbox(blobs["hip-drape"][..., 3] > 0),
        "hip_drape_visible_teal": keycount(comp, vis["hip-drape"], "QqgG"),
        "ponytail_bottom_row": last, "ponytail_bottom_row_opaque": int(pt[last].sum()),
        "ponytail_row_above_bottom_opaque": int(pt[last - 1].sum()),
    }


def leg_report(comp, blobs, names=None):
    """Leg and boot anatomy for one version (v14 render or v13's locked layers): colour widths come from each leg
    layer's own texels (outline excluded), gaps and edges from the composite."""
    k = np.array(hex_rgb(PALETTE["K"]), np.uint8)
    op = comp[..., 3] > 0
    out = {}
    for leg in ("far-leg", "near-leg"):
        lay = blobs[leg]
        a = lay[..., 3] > 0
        col = a & ~(lay[..., :3] == k).all(-1)
        ext = row_extents(col)
        widths = {y: int(col[y].sum()) for y in range(57, 67)}
        foot_min = min(ext[y][0] for y in range(61, 67))
        shaft_min = min(ext[y][0] for y in (58, 59))
        u_planes = col & (lay[..., :3] == np.array(hex_rgb(PALETTE["u"]), np.uint8)).all(-1)
        u_planes[SOLE_WELT_ROW:] = False
        out[leg] = {
            "shaft_colour_width_rows_58_59": [widths[58], widths[59]],
            "boot_max_colour_width_rows_57_66": max(widths.values()),
            "boot_colour_texels_rows_57_66": int(col[57:67].sum()),
            "heel_steps_back_of_shaft": bool(foot_min < shaft_min),
            "toe_rounded_welt_shorter_than_foot": bool(ext[SOLE_WELT_ROW][1] < max(ext[64][1], ext[65][1])),
            "welt_row_66_keys": sorted({k_ for k_, v in PALETTE.items() for x in range(W)
                                        if col[SOLE_WELT_ROW, x]
                                        and tuple(lay[SOLE_WELT_ROW, x, :3]) == hex_rgb(v)}),
            "warm_plane_u_texels_above_welt": int(u_planes.sum()),
            "rows_65_66_in_shadow_lit_D_share": round(
                int((col[65:67] & runtime_shadow_mask()[65:67]
                     & (lay[65:67, :, :3] == np.array(hex_rgb(PALETTE["D"]), np.uint8)).all(-1)).sum())
                / max(1, int((col[65:67] & runtime_shadow_mask()[65:67]).sum())), 3),
            "row_right_edge_49_56": {str(y): ext[y][1] for y in range(49, 57) if y in ext},
        }
    near = out["near-leg"]["row_right_edge_49_56"]
    knee = max(near.get(str(y), -1) for y in range(49, 53))
    shin = max(near.get(str(y), -1) for y in range(53, 57))
    gaps = {}
    for name, (y0, y1) in (("shins_53_56", (53, 56)), ("boots_57_67", (57, 67))):
        fx = max(np.nonzero(blobs["far-leg"][y, :, 3])[0].max() for y in range(y0, y1 + 1))
        nx = min(np.nonzero(blobs["near-leg"][y, :, 3])[0].min() for y in range(y0, y1 + 1))
        gaps[name] = int(sum(not op[y0:y1 + 1, x].any() for x in range(fx + 1, nx)))
    return {"legs": out, "near_knee_forward_of_shin_texels": int(knee - shin),
            "transparent_columns_between_far_and_near_leg": gaps}


def edge_report(comp):
    """Silhouette edge: opaque texels with a transparent 4-neighbour. Keys found there (a lit key = a rim/outline)."""
    op = comp[..., 3] > 0
    pad = np.pad(op, 1)
    edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    inv = {hex_rgb(v): k_ for k_, v in PALETTE.items()}
    keys = {}
    non_k = []
    for y, x in zip(*np.nonzero(edge)):
        key = inv[tuple(int(c) for c in comp[y, x, :3])]
        keys[key] = keys.get(key, 0) + 1
        if key != "K":
            non_k.append([int(x), int(y), key])
    return {"edge_texels": int(edge.sum()), "edge_keys": dict(sorted(keys.items())), "non_outline_edge_texels": non_k}


def pack_report(comp, blobs, names=None):
    """Dark marks inside the pack face (L/l texels not on the pack's own outline ring) and the canister."""
    vis = visible_masks(blobs, names)
    pa = blobs["pack"][..., 3] > 0
    inner = pa & np.roll(pa, 1, 0) & np.roll(pa, -1, 0) & np.roll(pa, 1, 1) & np.roll(pa, -1, 1)
    inner = inner & ~(blobs["pack"][..., :3] == np.array(hex_rgb(PALETTE["K"]), np.uint8)).all(-1)
    rep = {"pack_face_dark_marks_L_l_visible": keycount(comp, vis["pack"] & inner, "Ll")}
    if "canister" in blobs:
        ca = blobs["canister"][..., 3] > 0
        rep.update({"canister_bbox": bbox(ca), "canister_steel_texels_visible": keycount(comp, vis["canister"], "mMZ"),
                    "canister_inside_pack_alpha": bool((ca & ~pa).sum() == 0)})
    return rep


def pose_report(comp, blobs):
    v13_png, v13_layers, v13_order, _ = v13_reference()
    head_diff = (blobs["head"] != v13_layers["head"]).any(-1)
    return {"identity_v14": identity_report(comp, blobs), "identity_v13": identity_report(v13_png, v13_layers, v13_order),
            "form_v14": form_report(comp, blobs), "form_v13": form_report(v13_png, v13_layers, v13_order),
            "back_tail_v12": v12_tail_reference(),
            "legs_v14": leg_report(comp, blobs), "legs_v13": leg_report(v13_png, v13_layers, v13_order),
            "pack_v14": pack_report(comp, blobs), "pack_v13": pack_report(v13_png, v13_layers, v13_order),
            "edge_v14": edge_report(comp), "edge_v13": edge_report(v13_png),
            "boots_runtime_shadow_v14": shadow_boot_report(comp, blobs),
            "boots_runtime_shadow_v13": shadow_boot_report(v13_png, v13_layers, v13_order),
            "boots_v14": boot_report(comp, blobs), "boots_v13": boot_report(v13_png, v13_layers, v13_order),
            "lower_body_v14": lower_body_report(comp), "lower_body_v13": lower_body_report(v13_png),
            "head_alpha_identical_to_v13": bool(np.array_equal(blobs["head"][..., 3], v13_layers["head"][..., 3])),
            "head_texels_changed_vs_v13": [[int(x), int(y)] for y, x in zip(*np.nonzero(head_diff))],
            "eye_brow_texels_E_v13_v14": [keycount(v13_png, v13_layers["head"][..., 3] > 0, "E"),
                                          keycount(comp, blobs["head"][..., 3] > 0, "E")],
            "declared_unchanged_layers_identical_to_v13": {n: bool(np.array_equal(blobs[n], v13_layers[n]))
                                                           for n in V13_UNCHANGED_LAYERS},
            "silhouette_texels_v13": int((v13_png[..., 3] > 0).sum()),
            "silhouette_texels_v14": int((comp[..., 3] > 0).sum())}


def pose_gates(p):
    i14, i13, f14, f13 = p["identity_v14"], p["identity_v13"], p["form_v14"], p["form_v13"]
    l14, l13 = p["legs_v14"], p["legs_v13"]
    t12 = p["back_tail_v12"]
    lock = i14["loose_lock"]
    roll_top = [[x, 20, "Q"] for x in range(18, 24)]          # the declared deep-teal top edge of the roll
    return {
        # kept: proportion, head outline, identity masses (the figure does not grow or shrink by more than 5 %)
        "silhouette_texels_within_5pct_of_v13": 0.95 * p["silhouette_texels_v13"] <= p["silhouette_texels_v14"]
        <= 1.05 * p["silhouette_texels_v13"],
        "head_outline_identical_to_v13": p["head_alpha_identical_to_v13"],
        "face_change_only_the_declared_brow_texels": sorted(map(tuple, p["head_texels_changed_vs_v13"]))
        == sorted(FACE_CHANGED_TEXELS),
        "eye_mass_smaller_than_v13": p["eye_brow_texels_E_v13_v14"][1] < p["eye_brow_texels_E_v13_v14"][0],
        "declared_unchanged_layers_identical": all(p["declared_unchanged_layers_identical_to_v13"].values()),
        "loose_lock_separated_both_sides": lock is not None and all(
            (r["clear_cols_to_tail"] or 0) >= 1 and (r["clear_cols_to_head"] or 0) >= 1 for r in lock["rows"]),
        "hair_tie_not_a_pale_bead": i14["hair_tie_visible_pale_texels"] == 0,
        "tail_and_lock_clear_of_roll": i14["tail_or_lock_to_roll_min_vertical_gap_rows"] is not None
        and i14["tail_or_lock_to_roll_min_vertical_gap_rows"] >= 2,
        "shirt_wedge_same_as_v13": i14["shirt_visible_W_w_per_row_23_37"] == i13["shirt_visible_W_w_per_row_23_37"],
        "scarf_compact_ends_row_26": i14["scarf_bbox"][3] <= 26,
        "teal_scarf_and_roll_present": i14["teal_texels_visible"]["scarf-neck"] >= 40
        and i14["teal_texels_visible"]["bedroll"] >= 40,
        "hand_shows_skin_and_glove": i14["fist_skin_texels"] >= 6 and i14["fist_glove_texels"] >= 4,
        "bare_forearm_and_rolled_cuff": i14["forearm_skin_texels"] >= 8 and i14["sleeve_rolled_cuff_texels_P_p"] >= 6,
        "roll_end_cap_ringed_core": len(f14["roll_ringed_core_texels"]) >= 1,
        "roll_rounded_corners": f14["roll_bbox_corners_transparent"],
        "roll_binding_bows_toward_cap": f14["roll_binding_bows_toward_cap"],
        "roll_not_larger_than_v13": f14["roll_texels"] <= f13["roll_texels"],
        # coat: v12's fullness back without v12's black wedge
        "back_tail_fuller_than_v13": f14["back_tail_texels"] > f13["back_tail_texels"]
        and f14["back_tail_bbox"][0] < f13["back_tail_bbox"][0] and f14["back_tail_bbox"][3] > f13["back_tail_bbox"][3],
        "back_tail_texels_ge_v12": f14["back_tail_texels"] >= t12["back_tail_texels_v12"],
        "back_tail_deep_slate_C_le_half_of_v12": f14["back_tail_visible_C"] * 2 <= t12["back_tail_visible_C_v12"],
        "back_tail_mid_and_lit_slate_ge_twice_deep": f14["back_tail_visible_c"] + f14["back_tail_visible_o"]
        >= 2 * f14["back_tail_visible_C"],
        # legs and boots: anatomy, slimmer boots, separated near / far forms
        "boot_shafts_as_wide_as_the_shin": all(max(l14["legs"][g]["shaft_colour_width_rows_58_59"]) <= 5
                                               for g in ("far-leg", "near-leg")),
        "boots_narrower_than_v13": all(l14["legs"][g]["boot_max_colour_width_rows_57_66"]
                                       < l13["legs"][g]["boot_max_colour_width_rows_57_66"]
                                       and l14["legs"][g]["boot_colour_texels_rows_57_66"]
                                       < l13["legs"][g]["boot_colour_texels_rows_57_66"]
                                       for g in ("far-leg", "near-leg")),
        "heels_step_back_of_shafts": all(l14["legs"][g]["heel_steps_back_of_shaft"] for g in ("far-leg", "near-leg")),
        "toes_rounded": all(l14["legs"][g]["toe_rounded_welt_shorter_than_foot"] for g in ("far-leg", "near-leg")),
        "welts_lit_leather_D_only": all(l14["legs"][g]["welt_row_66_keys"] == ["D"] for g in ("far-leg", "near-leg")),
        "foot_base_rows_65_66_in_shadow_lit_ge_90pct": all(l14["legs"][g]["rows_65_66_in_shadow_lit_D_share"] >= 0.9
                                                           for g in ("far-leg", "near-leg")),
        "near_knee_juts_ge_2_forward_of_shin": l14["near_knee_forward_of_shin_texels"] >= 2,
        "near_and_far_legs_separated_ge_5_columns": all(v >= 5 for v in
                                                        l14["transparent_columns_between_far_and_near_leg"].values()),
        # restrained warm edge planes, no rim light: every new silhouette-edge texel is black; the only non-black edge
        # texels are v13's own (hair strand tips, scarf, guard and hem notches in unchanged art) and the declared
        # deep-teal roll top
        "warm_planes_u_restrained_4_to_16": 4 <= sum(l14["legs"][g]["warm_plane_u_texels_above_welt"]
                                                     for g in ("far-leg", "near-leg")) <= 16,
        "silhouette_edge_black_except_v13_and_roll_top": set(map(tuple, p["edge_v14"]["non_outline_edge_texels"]))
        <= set(map(tuple, p["edge_v13"]["non_outline_edge_texels"])) | set(map(tuple, roll_top)),
        "lower_body_no_orange": p["lower_body_v14"]["warm_orange_texels"] == 0,
        # pack, canister, drape
        "pack_face_calmer_than_v13": p["pack_v14"]["pack_face_dark_marks_L_l_visible"]
        < p["pack_v13"]["pack_face_dark_marks_L_l_visible"],
        "canister_present_inside_pack_silhouette": p["pack_v14"]["canister_steel_texels_visible"] >= 6
        and p["pack_v14"]["canister_inside_pack_alpha"],
        "drape_tucked_under_pack_not_larger_than_v13": f14["hip_drape_visible_teal"] <= f13["hip_drape_visible_teal"]
        and f14["hip_drape_bbox"][1] == f14["pack_bbox"][3] + 1,
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
        on_bg(comp, bg, 8).save(os.path.join(out_dir, f"v14_x8_{tag}.png"))
    for path in nosprites:
        tag = os.path.splitext(os.path.basename(path))[0]
        full = game_scale(comp, path)
        k = full.width // 640
        full.save(os.path.join(out_dir, f"v14_game-scale_{tag}.png"))
        full.crop((120 * k, 180 * k, 360 * k, 300 * k)).save(os.path.join(out_dir, f"v14_game-scale-crop-1x_{tag}.png"))
        crop = full.crop((240 * k, 190 * k, 340 * k, 280 * k))
        z = 8 // k
        crop.resize((crop.width * z, crop.height * z), Image.NEAREST).save(
            os.path.join(out_dir, f"v14_game-scale-crop-x{z}_{tag}.png"))
    p = pose_report(comp, blobs)
    print(json.dumps({**stats(comp), "material_texels_v14": region_counts(comp), "pose": p,
                      "pose_gates": pose_gates(p), "silhouette_vs_v13": silhouette_report(comp, blobs)}))


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
                      "file_format": "0", "file_name": json.dumps("sideview-idle-right-static-unapproved-v14"),
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
    dt = (2026, 10, 18, 8, 45, 52)      # fixed (zip needs even seconds) -> byte-identical rebuilds
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
    dt = (2026, 10, 18, 8, 45, 52)
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
    tmp = tempfile.mkdtemp(prefix="wb-fv14-")
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
    "far-leg": "v14 far leg braced back with a small knee bend, in the body's shadow: deep slate back and body (C), spruce (T) and a lit spruce front edge (t); boot: dark cuff band (L), shaft as wide as the shin (d), heel stepping back, vamp sloping to a rounded toe with a lit plane (D) and one warm-grey toe-cap texel (u), lowest foot row and welt lit leather (D)",
    "hip-drape": "v8 teal back-hip cloth, v14: tucked under the pack bottom from the belt, filling the notch between pack and back tail (v13: a tab sticking out at the hip)",
    "pack": "v14 pack: v13's slumped-sack outline, face calmed to one lit flap (D) whose edge (l) dips to a pale buckle (P), one strap (l), deep brown body (d), shadowed back edge (l/L) and underside (L)",
    "canister": "v14: small steel canister (m, lit side M) on the pack's visible side, inside the pack outline (character-sheet / v8 identity item; v05-v13 had none)",
    "bedroll": "v13 teal bedroll cylinder (end cap ring round a dark core, bowing binding); v14 outlines its top edge in deep teal (Q) instead of black",
    "ponytail": "high tied ponytail with a single tapered tip (v13, unchanged)",
    "loose-lock": "separate loose lock falling from the hook tip at the nape, one transparent column to the tail and to the head on every row (v13, unchanged)",
    "near-leg": "v14 near leg: thigh runs down and forward from under the front panel to a knee that juts two texels forward of the shin, cool grey knee pad (m/M) on a dark strap (L), shin drops back to the ankle; spruce body (T), deep slate back edge (C), lit spruce (t) and warm-grey (u) planes on the light-facing thigh top and shin front; boot as the far one",
    "coat": "v8 storm-slate coat torso and belt (v13, unchanged)",
    "coat-skirt": "split coat skirt: v13 lit front panel; v14 back tail flares to x17 and hangs to row 54 (v13 x18 / row 53, v12 x16 / row 56) as cloth: shadowed back edge (C), mid slate body (c), one broad fold (C flank, o ridge) from the belt toward the back corner, lit split edge (o, C), dark-leather hem (l) rising in one diagonal toward the split",
    "shirt-lapel": "white shirt wedge framed by lit lapel texels and a dark lapel line (v13, unchanged)",
    "near-arm": "sword arm reaching forward with the sleeve rolled to the elbow (v13, unchanged)",
    "insignia": "teal 3x3 diamond on the upper sleeve (v13, unchanged; a colour placement at 1x)",
    "sword-blade": "ordinary short sword blade raised forward at 45 degrees (v10-v13, unchanged; same reach)",
    "sword-guard": "small steel crossguard square to the blade (v10-v13, unchanged)",
    "fist": "fingerless dark glove with bare skin knuckles and thumb round the grip (v13, unchanged)",
    "head": "v13 head outline and face; v14 recolours three brow-row texels only: the brow is hair brown (2, 1) and ends one texel before the eye's front, so the eye reads as a smaller lash line over the pupil and eye-white (more mature)",
    "hair-tie": "dark leather hair band where the ponytail leaves the head (v13, unchanged)",
    "collar": "raised coat collar standing behind the nape (v13, unchanged)",
    "scarf-neck": "compact teal scarf (v13, unchanged)",
    "collar-front": "front point of the raised coat collar over the scarf's front edge (v13, unchanged)",
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
        "refines": {"files": V13_LOCKS,
                    "hash_algorithm": "sha256-bytes for .png/.pxo/.ora; sha256-text-lf-v1 for the .json manifest",
                    "relationship": "same cell/pin/sole/crown rows and bbox; head outline, coat torso, shirt, scarf, "
                                    "arm, hand, blade, insignia, collar, ponytail, loose lock and hair band "
                                    "byte-identical to v13; v14 changes: " + "; ".join(V14_TARGETS) + "; v13 left "
                                    "untouched",
                    "silhouette_vs_v13": silhouette_report(comp, blobs)},
        "pose": pose,
        "pose_gates": pose_gates(pose),
        "identity_references": {"character_sheet": CHARACTER_SHEET_REL, "v8_south_static": V8_SOUTH_REL},
        "feedback_addressed": "root review of v13 (v14 task brief, 2026-10-18): pack/roll form modestly improved "
                              "but an overly busy hard-edged silhouette, thick boot masses and dark-floor lower-body "
                              "merging remain; v12's full coat partly lost. Earlier: Codex v12 review in the v13 "
                              "dispatch " + DISPATCH_REL + "; creator answer on v11 '继续精修静止帧' (a request for "
                              "further static refinement, not acceptance)",
        "v14_targets": V14_TARGETS,
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
        "sole_on_row_67_same_as_v13": st["sole_row"] == SOLE_ROW,
        "crown_on_row_7_same_as_v13_0p65_proportion": st["crown_row_measured"] == CROWN_ROW,
        "leftmost_texel_ge_x15_liang_gap_kept": st["alpha_bounds_inclusive"][0] >= 15,
        "rightmost_texel_le_v13_sentry_gap_kept": st["alpha_bounds_inclusive"][2] <= 62,
        "nothing_at_or_below_pin_row": st["pin_row_clear"],
        "both_boots_touch_sole_row": bool((a[SOLE_ROW, 20:PIN[0], 3] > 0).any() and (a[SOLE_ROW, PIN[0]:, 3] > 0).any()),
        "transparent_border": bool(not a[0, :, 3].any() and not a[-1, :, 3].any()
                                   and not a[:, 0, 3].any() and not a[:, -1, 3].any()),
    }


def structure_ok(sil):
    return (sil["layers_added_vs_v13"] == V13_LAYER_NAMES_PLUS and sil["layers_removed_vs_v13"] == []
            and sil["palette_keys_removed_vs_v13"] == REMOVED_KEYS_VS_V13
            and sil["palette_keys_added_vs_v13"] == ADDED_KEYS_VS_V13 and sil["palette_shared_keys_same_colour"])


def build(exe):
    lock = v13_lock()
    if not lock["unchanged"]:
        raise SystemExit(f"v13 changed: {lock}")
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
    if not v13_lock()["unchanged"]:
        raise SystemExit("v13 changed during build")


def check(exe):
    report = {"status": "UNAPPROVED, NONRUNTIME test-only candidate", "v13_lock_before": v13_lock()}
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
    report["silhouette_vs_v13"] = sil
    g["layers_and_palette_vs_v13_as_declared"] = structure_ok(sil)
    g["manifest_silhouette_matches_fresh"] = man["refines"]["silhouette_vs_v13"] == json.loads(json.dumps(sil))
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
    report["v13_lock_after"] = v13_lock()
    g["v13_unchanged"] = report["v13_lock_before"]["unchanged"] and report["v13_lock_after"]["unchanged"]
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
