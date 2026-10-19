"""UNAPPROVED, NONRUNTIME test-only pilot v15: female protagonist side-view battle idle, facing right, ONE static frame.

Material-value pass over v14 (bounded fork of the v14 author tool; no motion, no new direction, no batch, no runtime
swap). The alpha silhouette, pose, head, face, hair, scarf, coat torso, shirt, arm, hand, blade and every outline are
v14's; only interior palette-plane choices change, plus one removed accent layer (the v14 canister). v14's files
(tracked at HEAD) are read (hash-gated) and never written.

Root review of the v14 actual 640x360 four-person archive capture, one named defect list:
  coat / feet merge with the dark floor  -> the lower body is moved out of the floors' value band (outskirts paving
                                            L ~76-86, archive ~103 warm brown): the back coat tail body takes a new
                                            deep-mid slate (e, between C and c); the far leg sits in shadow (C/T, no lit
                                            front stripe); boot shafts and foot sides become dark leather (L) with mid
                                            leather (d) between, the lit vamp/toe plane and the two-row lit base (D)
                                            are v14's; the warm grey (u) planes return to spruce (t) or leather (D)
  back / pack details are busy           -> broad pack planes: one lit flap (D), one deep body (d), a shaded back side
                                            (L/l); no buckle, no strap, no canister; the roll's bright top (G) drops to
                                            the scarf's mid teal (g); the hip drape is deep teal (Q) with one q edge
Protected (production constraints, not art approval): 68x72 cell, pin (32, 68), crown row 7, sole row 67, display
proportion 0.65, v14 silhouette alpha, blade reach, face/hair/scarf/slate-coat identity, adult head read; no rim, halo,
glow or neon (every silhouette edge texel stays as v14's).

v14 header follows (its targets are kept unless changed above).
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
v15: Pixelorama's own console diagnostics (ERROR / WARNING / SCRIPT ERROR / shader lines) are recorded per export and
reported SEPARATELY from pixel equality, next to the same export of the unchanged v14 .pxo as a control. A diagnostic
does not fail the pixel gate and an exact export does not make the application run clean.

Modes
  preview <dir> [nosprite.png ...]
                  inspection PNGs in <dir> (outside the repo), one subject per file; with no-sprite captures (1280x720
                  or 640x360), also the exact game-scale composite (texture origin 536,408 at 2x / 268,204 at 1x)
  build           export via Pixelorama, write PNG + .pxo + .ora + manifest to outputs/battle-static-v15 (never
                  overwrites a different file)
  check           technical gates on the built files incl. Pixelorama flat + split-layer round-trips, layer names and
                  palette diff vs v14, silhouette report vs v14, preservation / value-plane / edge / back-accent gates
                  (manifest pose_gates), layer-stack recomposition of the .pxo and .ora, v14 + protected-path locks;
                  writes nothing

Run with the real Python in isolated mode:  python -I -B <this file> preview <dir> | build | check
"""
import argparse, colorsys, hashlib, io, json, os, shutil, subprocess, sys, tempfile, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
VER = "unapproved-v15"
STAMP = "20261018-210446"
RUN_ID = "2c0b5777"
W, H = 68, 72
PIN = (32, 68)            # same as v03-v14: first transparent row under the soles, between the feet
CROWN_ROW = 7             # same as v03-v14: head crown row; soles end on row 67 -> crown-to-sole 61 rows
SOLE_ROW = 67
HEAD_COLS = (24, 47)      # crown columns are searched here (same as v10-v14)
OUT_DIR_REL = "outputs/battle-static-v15"          # v15 writes nothing under game/
V14_DIR_REL = "game/assets/characters/combat-sideview-pilots"
_V14 = "rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_"
V14_LOCKS = {             # v14 (tracked at HEAD) is the comparison base and is read-only for this tool
    V14_DIR_REL + "/" + _V14 + "unapproved-v14_20261018-084553-336f663b.png":
        "86286082c59d923e27fdf572a616467e9acfb2912d55c7b639167c8789ae43dc",
    V14_DIR_REL + "/" + _V14 + "editable-layers_unapproved-v14_20261018-084553-8a0ff314.pxo":
        "8a424e58178cb770e76604262f2f0cce9634f1aa4a2cc933689460e456e4e6e3",
    V14_DIR_REL + "/" + _V14 + "editable-layers_unapproved-v14_20261018-084553-90f4f22b.ora":
        "d0688be291b79d24ad14a8f81bf7c59e65e9199f01f53765baa37708cb307fe5",
    V14_DIR_REL + "/" + _V14 + "manifest_unapproved-v14_20261018-084553-5bf8c74a.json":
        "38d044ac79e41320eea55fc78f2be6be1891f0bc85488208488459c6d214a219",
}
V14_PNG_REL, V14_PXO_REL, V14_ORA_REL, V14_MANIFEST_REL = list(V14_LOCKS)
# protected paths this tool must leave untouched (checked before and after build / check); text = sha256-text-lf-v1
PROTECTED_LOCKS = {
    "game/scripts/battle_arena.gd": "5b69823ff3acca2f1ab6241c4de9c3f2be2c0c94b78d366249f51fe3955173d2",
    "game/assets/environments/rpg-2-star-ocean-the-second_scifi-archive-battle-arena_runtime-band_m8-candidate_"
    "20261014-213622-14315e18.png": "c840e071e126510cf301e8deafde2d085c759415c00c57ba88140da12c916f4b",
    "game/assets/environments/rpg-2-star-ocean-the-second_scifi-outskirts-battle-arena_runtime-band_m8-candidate_"
    "20261014-213622-14315e18.png": "feea6297f1e859c64daffe0771e1ac5beadaffb0595066944b3b473cff82a4aa",
    # v14 author tool, capture probe and the six v14 captures the root reviewed
    "tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-idle-right-native-0p65-author_unapproved-"
    "v14_20261018-084553-8e0b84ca.py": "603fb65f79fd9943ad71c3c038623c5bdc1bde7258a7d7a07a8e71a1d14d9c81",
    "tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-idle-right-native-0p65-party-capture-probe_"
    "unapproved-v14_20261018-084553-2c7e5a90.gd": "720c8377794ac65458ab203fa664b483ffc76ec1022ef31419c676359f2457a3",
    "outputs/" + _V14 + "party-capture-archive-640-probe-zh_unapproved-v14_20261018-084553-5a0ec9d0.png":
        "775803bfb013097db6450605548018f7e56c8bcc601f17849ff993518f92b414",
    "outputs/" + _V14 + "party-capture-archive-640-probe-en_unapproved-v14_20261018-084553-7c83e367.png":
        "1ddd41235a53f345b6ff9ea41cfe9bd89fd482900cdedaf6077b9046c75970c1",
    "outputs/" + _V14 + "party-capture-outskirts-640-probe-zh_unapproved-v14_20261018-084553-f1b7abb6.png":
        "cd750d835665b98477efd89a73a3d2d1faf2416d7b80e65d7fe0a78599631d6b",
    "outputs/" + _V14 + "party-capture-outskirts-640-probe-en_unapproved-v14_20261018-084553-cb540bbe.png":
        "b2595418166a3bb72423005eeb9900fe4d2a78441bb9ea7ba537a95f8df0fafc",
    "outputs/" + _V14 + "party-capture-head-geometric-640-probe-zh_unapproved-v14_20261018-084553-a1d47b82.png":
        "6a782be4da2fa9e965416707b1b0fc3d06f239c2001748a856f780a83a907b9e",
    "outputs/" + _V14 + "party-capture-head-geometric-640-probe-en_unapproved-v14_20261018-084553-0de3077a.png":
        "a17fa97e625b0ce5c229f165d631c83a01b8e49946bd06efa063a1061ba316b0",
}
TEXT_EXT = (".json", ".gd", ".tscn", ".godot", ".py", ".md")
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


SUBJECT = "female-battle-idle-right"                # short: outputs/battle-static-v15 paths stay well under MAX_PATH
PNG_NAME = f"{SLUG}_{SUBJECT}_static-native0p65_{VER}_{STAMP}-{fid('png')}.png"
PXO_NAME = f"{SLUG}_{SUBJECT}_editable-layers_{VER}_{STAMP}-{fid('pxo')}.pxo"
ORA_NAME = f"{SLUG}_{SUBJECT}_editable-layers_{VER}_{STAMP}-{fid('ora')}.ora"
MANIFEST_NAME = f"{SLUG}_{SUBJECT}_manifest_{VER}_{STAMP}-{fid('manifest')}.json"
TOOL_REL = "tools/" + os.path.basename(os.path.abspath(__file__))

PALETTE = {               # v14's 31 keys + ONE disclosed extension (e, deep-mid storm slate between C and c)
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
    "e": "#2e364d",   # v15 extension: storm slate between C (L ~40) and c (L ~69), L ~54, same hue as the v8 ramp
}
REMOVED_KEYS_VS_V14 = []                          # sorted() order
ADDED_KEYS_VS_V14 = ["e"]

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
#
# v15 (material values only; every row keeps v14's start column and length, so the alpha is v14's): the far leg is in
# the body's shadow as one receding plane (deep slate back C, spruce T; v14's lit spruce front stripe t matched the dark
# floor). Boots: the shaft and the heel / foot side away from the light are dark leather (L, L ~31: clear of both floors'
# paving), mid leather (d) between, the vamp slope and toe plane lit (D) as in v14, and v14's two-row lit base (D) where
# the foot stands in the contact shadow; the warm-grey toe texel (u) becomes D
rows("far-leg", [
    (46, 28, "KCCTTK"),
    (47, 28, "KCCTTK"),
    (48, 27, "KCCTTTK"),
    (49, 27, "KCCTTTK"),
    (50, 26, "KCCTTTK"),
    (51, 26, "KCCTTTK"),
    (52, 25, "KCCTTKK"),
    (53, 25, "KCCTTK"),
    (54, 24, "KCCTTK"),
    (55, 24, "KCCTTK"),
    (56, 23, "KCCTTK"),
    (57, 22, "KLLLLLK"),
    (58, 22, "KLLLddK"),
    (59, 22, "KLLLddK"),
    (60, 21, "KLLLddDK"),
    (61, 20, "KLLLLddDDK"),
    (62, 20, "KLLLLLddDDK"),
    (63, 20, "KLLLLLdddDDK"),
    (64, 20, "KLLLLLddddDK"),
    (65, 20, "KDDDDDDDDDDK"),
    (66, 20, "KDDDDDDDDDK"),
    (67, 21, "KKKKKKKKK"),
])

# v8's teal back-hip cloth hung BEHIND the coat skirt. v14: tucked under the pack and hanging from the belt, it fills the
# notch between the pack bottom and the back tail (v13: a tab sticking out of the silhouette at the hip), so the back
# contour runs pack -> drape -> tail in one line. v15: it hangs in the pack's shadow, so it is deep teal (Q) with one
# mid-teal (q) texel where it leaves the pack (v14: a lit g edge and q body, a fourth bright accent on the back)
rows("hip-drape", [
    (38, 18, "KqQQQK"),
    (39, 19, "KQQQQK"),
    (40, 20, "KQQQK"),
    (41, 21, "KQQK"),
    (42, 22, "KK"),
])

# v14 pack outline (v13's slumped sack) kept. v15 face in broad planes only: the lit flap (D, rows 27-29, as v14), one
# deep brown body (d) under it, the side turned away from the light shaded (l, then L at the bottom) and the dark
# underside row (L). v14's pale buckle (P), strap line (l) and flap-edge marks are gone, and so is the canister layer
rows("pack", [
    (26, 19, "KKKKKKKK"),
    (27, 18, "KDDDDDDDdK"),
    (28, 17, "KdDDDDDDDdK"),
    (29, 16, "KldDDDDDDDdK"),
    (30, 15, "KLldddddddddK"),
    (31, 15, "KLldddddddddK"),
    (32, 15, "KLldddddddddK"),
    (33, 15, "KLldddddddddK"),
    (34, 15, "KLLddddddddK"),
    (35, 16, "KLLLdddddK"),
    (36, 17, "KLLLLLLLK"),
    (37, 18, "KKKKKKK"),
])

# v13 teal bedroll cylinder (end cap ring round a dark core, bowing binding), v14: the top edge is outlined in deep teal
# (Q) instead of black so the lit top reads as a rounded surface, not a hard box lid. v15: the top plane is the scarf's
# mid teal (g) instead of the pale teal light (G, L ~180), so the roll is one calm teal mass under the ponytail
rows("bedroll", [
    (20, 17, "KQQQQQQK"),
    (21, 16, "KqQgggglgK"),
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
# v15 (values only, v14 alpha): the warm-grey u planes on the thigh top and shin front return to lit spruce (t), the
# shin turns from a deep back (C C) through spruce (T) to one lit front plane (t) facing the light; boot as the far one
# but on the lit side: the shaft's front plane is lit leather (D), the heel side dark (L)
rows("near-leg", [
    (42, 33, "KCTTTtK"),
    (43, 34, "KCTTTtK"),
    (44, 34, "KCTTTTtK"),
    (45, 35, "KCTTTTtK"),
    (46, 36, "KCTTTTtK"),
    (47, 36, "KCTTTTttK"),
    (48, 37, "KCTTTTttK"),
    (49, 38, "KCTTTtmmK"),
    (50, 38, "KCTTTLmMK"),
    (51, 38, "KCCTTLmMK"),
    (52, 38, "KCTTTLmK"),
    (53, 38, "KCCTTtK"),
    (54, 38, "KCCTTtK"),
    (55, 38, "KCCTTtK"),
    (56, 38, "KCCTTtK"),
    (57, 38, "KLLLLLK"),
    (58, 38, "KLLddDK"),
    (59, 38, "KLLddDK"),
    (60, 38, "KLLddDK"),
    (61, 37, "KLLLddDDK"),
    (62, 37, "KLLLLddDDK"),
    (63, 37, "KLLLLdddDDK"),
    (64, 37, "KLLLLLdddDDK"),
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
# v15 (values only, v14 alpha and v14 fold drawing): the back tail's body moves from mid slate c (L ~69, inside the
# dark floor's band) to the new deep-mid slate e (L ~54); the shadowed back edge and fold flank (C), the fold's lit
# ridge and the lit split edge (o) and the leather hem (l) are v14's, and the lit front panel is v14's unchanged
rows("coat-skirt", [
    (40, 23, "KCCCCCCe" + "o" * 14 + "K"),
    (41, 22, "KCeeCoeeooK" + "ooooocooooooK"),
    (42, 22, "KCeeCoeeoCK" + "ooooocooooooK"),
    (43, 21, "KCeeeCoeeoCK" + "ooooocoooocK"),
    (44, 21, "KCeeCoeeeoCK" + "ooooocoocllK"),
    (45, 20, "KCeeeCoeeeoCK" + "ooooccllKK"),
    (46, 20, "KCeeeCoeeeoCK" + "ccccllK"),
    (47, 20, "KCeeCoeeeoCK" + "lllK"),
    (48, 19, "KCeeeCoeeeoe"),
    (48, 31, "KKKK"),
    (49, 19, "KCeeeCoeeeelK"),
    (50, 18, "KCeeeCoeeellK"),
    (51, 18, "KCeeCoelllKK"),
    (52, 17, "KCeeClllKKK"),
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
V14_LAYERS_REMOVED = ["canister"]             # v15 = v14's 21 layer names minus the canister (+ guides)
V14_UNCHANGED_LAYERS = ["ponytail", "loose-lock", "coat", "shirt-lapel", "near-arm", "insignia", "sword-blade",
                        "sword-guard", "fist", "head", "hair-tie", "collar", "scarf-neck",
                        "collar-front"]       # declared byte-identical to v14's .ora layers (checked)
V15_CHANGED_LAYERS = ["far-leg", "hip-drape", "pack", "bedroll", "near-leg", "coat-skirt"]   # recoloured, alpha = v14
BACK_REGION = (0, 31, 20, 56)                 # x0, x1, y0, y1 inclusive: pack, roll, back tail, behind the body
LOWER_REGION_ROWS = (38, 67)                  # belt row to sole row
ACCENT_KEYS = "GPpMZu"                        # pale / bright accent keys (L >= ~113) counted in the back region
V15_TARGETS = [
    "back coat tail body in the new deep-mid slate e (L ~54) instead of mid slate c (L ~69, inside the dark floor's "
    "value band); v14's fold drawing, C flank, o ridge, lit split edge and leather hem kept",
    "far leg one receding shadow plane (C back, T body; v14's lit spruce front stripe t removed)",
    "boots: shafts and the heel / foot side away from the light in dark leather L, mid leather d between, the vamp/toe "
    "plane lit D and v14's two-row lit base D in the contact shadow kept; near shaft front lit (D); warm-grey u toe "
    "texels -> D",
    "near leg: warm-grey u planes -> lit spruce t; shin C C T T t",
    "pack face in broad planes: v14's lit flap (D), one deep body (d), shaded back side (l / L); buckle, strap, flap "
    "marks and the canister layer removed",
    "roll top plane g instead of pale G; hip drape deep teal Q with one q texel",
    "unchanged: alpha silhouette (v14's), head/face/hair, scarf, coat torso, shirt, arm, hand, blade, guard, insignia, "
    "collars, ponytail, loose lock, hair band (byte-identical layers); no rim, halo, glow or neon",
]
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
    """sha256-bytes for binaries; sha256-text-lf-v1 (CRLF -> LF only) for text, so a core.autocrlf=true checkout still
    matches the LF blob."""
    data = read_bytes(repo_path(rel))
    return sha256_bytes(data.replace(b"\r\n", b"\n") if rel.endswith(TEXT_EXT) else data)


def locks():
    """v14 comparison files + protected paths: {rel: sha} and whether each equals its declared hash."""
    want = {**V14_LOCKS, **PROTECTED_LOCKS}
    files = {rel: lock_hash(rel) for rel in want}
    return {"files": files, "mismatched": sorted(rel for rel in want if files[rel] != want[rel]),
            "unchanged": all(files[rel] == want[rel] for rel in want),
            "hash_algorithm": "sha256-bytes for .png/.pxo/.ora; sha256-text-lf-v1 (CRLF -> LF only) for text"}


def decode(png):
    im = Image.open(io.BytesIO(png))
    return im.mode, im.size, np.array(im.convert("RGBA"))


# ===================================================================================================== v14 comparison
def v14_reference():
    """v14's flat PNG, its per-layer RGBA from the locked .ora, and its manifest palette (all read-only)."""
    png = decode(read_bytes(repo_path(V14_PNG_REL)))[2]
    with zipfile.ZipFile(io.BytesIO(read_bytes(repo_path(V14_ORA_REL)))) as z:
        names = [n[len("data/"):-len(".png")] for n in z.namelist() if n.startswith("data/") and n.endswith(".png")]
        layers = {n: decode(z.read(f"data/{n}.png"))[2] for n in names}
    man = json.loads(read_bytes(repo_path(V14_MANIFEST_REL)))
    order = [l["name"] for l in man["layers_bottom_to_top"]]
    return png, layers, order, man["palette"]


def bbox(alpha):
    ys, xs = np.nonzero(alpha)
    return None if len(xs) == 0 else [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


def visible_masks(blobs, names=None):
    """Per layer: texels where that layer is the top-most opaque layer (what the viewer actually sees of it). `names`
    is the bottom-to-top order (default: this tool's layers); v14's .ora layers are passed with v14's own order."""
    names = [n for n in (names or LAYER_NAMES) if n != "guides"]
    owner = np.full((H, W), -1, np.int16)
    for i, name in enumerate(names):
        owner[blobs[name][..., 3] == 255] = i
    return {name: owner == i for i, name in enumerate(names)}


def silhouette_report(comp, blobs):
    """How v15 differs from v14: whole-sprite alpha silhouette, composite texels, per layer, palette and layer names."""
    v14_png, v14_layers, v14_order, v14_pal = v14_reference()
    a15, a14 = comp[..., 3] > 0, v14_png[..., 3] > 0
    inter, union = int((a15 & a14).sum()), int((a15 | a14).sum())
    layers = {}
    for name in LAYER_NAMES[:-1]:
        mine = blobs[name][..., 3] > 0
        theirs = v14_layers[name][..., 3] > 0 if name in v14_layers else None
        same_px = theirs is not None and np.array_equal(blobs[name], v14_layers[name])
        layers[name] = {"texels_v14": None if theirs is None else int(theirs.sum()), "texels_v15": int(mine.sum()),
                        "alpha_identical_to_v14": None if theirs is None else bool(np.array_equal(mine, theirs)),
                        "byte_identical_to_v14": bool(same_px),
                        "changed_texels": None if theirs is None else int((blobs[name] != v14_layers[name]).any(-1).sum())}
    v14_names = [n for n in v14_order if n != "guides"]
    pal14 = {k: v.lower() for k, v in v14_pal.items()}
    pal15 = {k: v.lower() for k, v in PALETTE.items()}
    return {
        "silhouette_texels_v14": int(a14.sum()), "silhouette_texels_v15": int(a15.sum()),
        "silhouette_iou": round(inter / union, 4), "silhouette_alpha_identical_to_v14": bool(np.array_equal(a15, a14)),
        "silhouette_bbox_v14": bbox(a14), "silhouette_bbox_v15": bbox(a15),
        "composite_changed_texels": int((comp != v14_png).any(-1).sum()),
        "layers": layers,
        "byte_identical_layers": [n for n in LAYER_NAMES[:-1] if layers[n]["byte_identical_to_v14"]],
        "layers_added_vs_v14": [n for n in LAYER_NAMES[:-1] if n not in v14_names],
        "layers_removed_vs_v14": [n for n in v14_names if n not in LAYER_NAMES],
        "layer_order_v14": v14_order,
        "palette_keys_removed_vs_v14": sorted(set(pal14) - set(pal15)),
        "palette_keys_added_vs_v14": sorted(set(pal15) - set(pal14)),
        "palette_shared_keys_same_colour": all(pal14[k] == pal15[k] for k in set(pal14) & set(pal15)),
    }


# ===================================================================================================== value planes
def lum(rgb):
    rgb = np.asarray(rgb, float)
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def keycount(rgba, mask, keys):
    rgb = rgba[..., :3]
    return int(sum((mask & (rgb == np.array(hex_rgb(PALETTE[k]), np.uint8)).all(-1)).sum() for k in keys if k in PALETTE))


def key_histogram(rgba, mask):
    inv = {hex_rgb(v): k for k, v in PALETTE.items()}
    out = {}
    for y, x in zip(*np.nonzero(mask & (rgba[..., 3] > 0))):
        k = inv.get(tuple(int(c) for c in rgba[y, x, :3]), "?")
        out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items()))


def runtime_shadow_mask():
    """Texels whose screen-pixel centre lies inside the runtime contact shadow ellipse (pin on screen (300, 272), texel
    (tx, ty) on screen (268 + tx, 204 + ty), radius 18, y scale 0.28)."""
    ty, tx = np.mgrid[0:H, 0:W]
    dx = (268 + tx + 0.5 - 300.0) / RUNTIME_SHADOW_RADIUS
    dy = (204 + ty + 0.5 - 272.0) / (RUNTIME_SHADOW_RADIUS * RUNTIME_SHADOW_SCALE_Y)
    return dx * dx + dy * dy <= 1.0


def edge_report(comp):
    """Silhouette edge: opaque texels with a transparent 4-neighbour. Keys found there (a lit key = a rim/outline)."""
    op = comp[..., 3] > 0
    pad = np.pad(op, 1)
    edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    inv = {hex_rgb(v): k_ for k_, v in PALETTE.items()}
    keys, non_k = {}, []
    for y, x in zip(*np.nonzero(edge)):
        key = inv[tuple(int(c) for c in comp[y, x, :3])]
        keys[key] = keys.get(key, 0) + 1
        if key != "K":
            non_k.append([int(x), int(y), key])
    return {"edge_texels": int(edge.sum()), "edge_keys": dict(sorted(keys.items())), "non_outline_edge_texels": non_k}


def value_report(comp, blobs, names=None):
    """Descriptive (not gated): per region, the visible key histogram and mean luminance (outline excluded), plus the
    back region's accent count. The same function is run on v14's locked layers for comparison."""
    vis = visible_masks(blobs, names)
    k = (comp[..., :3] == np.array(hex_rgb(PALETTE["K"]), np.uint8)).all(-1)
    op = comp[..., 3] > 0
    x0, x1, y0, y1 = BACK_REGION
    back = np.zeros((H, W), bool)
    back[y0:y1 + 1, x0:x1 + 1] = True
    lower = np.zeros((H, W), bool)
    lower[LOWER_REGION_ROWS[0]:LOWER_REGION_ROWS[1] + 1] = True
    boots = np.zeros((H, W), bool)
    boots[57:67] = True
    tail = vis["coat-skirt"].copy()
    tail[:, 32:] = False
    regions = {"back_region": back & op, "lower_body_38_67": lower & op, "boots_57_66": boots & (vis["far-leg"] | vis["near-leg"]),
               "boots_in_contact_shadow": boots & (vis["far-leg"] | vis["near-leg"]) & runtime_shadow_mask(),
               "boots_on_paving": boots & (vis["far-leg"] | vis["near-leg"]) & ~runtime_shadow_mask(),
               "back_coat_tail": tail, "far_leg_above_boot": vis["far-leg"] & (np.arange(H)[:, None] < 57),
               "near_leg_above_boot": vis["near-leg"] & (np.arange(H)[:, None] < 57),
               "pack_visible": vis["pack"], "bedroll_visible": vis["bedroll"], "hip_drape_visible": vis["hip-drape"]}
    out = {}
    for name, m in regions.items():
        mm = m & ~k
        out[name] = {"texels_excl_outline": int(mm.sum()),
                     "mean_L_excl_outline": round(float(lum(comp[mm][:, :3]).mean()), 1) if mm.any() else None,
                     "keys": key_histogram(comp, mm)}
    out["back_region_accent_texels_" + ACCENT_KEYS] = keycount(comp, back & op, ACCENT_KEYS)
    return out


def pose_report(comp, blobs):
    v14_png, v14_layers, v14_order, _ = v14_reference()
    return {"values_v15": value_report(comp, blobs), "values_v14": value_report(v14_png, v14_layers, v14_order),
            "edge_v15": edge_report(comp), "edge_v14": edge_report(v14_png),
            "declared_unchanged_layers_identical_to_v14": {n: bool(np.array_equal(blobs[n], v14_layers[n]))
                                                           for n in V14_UNCHANGED_LAYERS},
            "changed_layers_alpha_identical_to_v14": {n: bool(np.array_equal(blobs[n][..., 3], v14_layers[n][..., 3]))
                                                      for n in V15_CHANGED_LAYERS},
            "canister_alpha_inside_v14_pack": bool(((v14_layers["canister"][..., 3] > 0)
                                                    & ~(v14_layers["pack"][..., 3] > 0)).sum() == 0),
            "new_key_e_luminance_between_C_and_c": [round(float(lum(hex_rgb(PALETTE[q]))), 1) for q in "Cec"],
            "silhouette_texels_v14": int((v14_png[..., 3] > 0).sum()),
            "silhouette_texels_v15": int((comp[..., 3] > 0).sum())}


def pose_gates(p):
    """Preservation and structural gates only. No contrast threshold is gated (the value numbers are descriptive)."""
    v15, v14 = p["values_v15"], p["values_v14"]
    lc, le, lcc = p["new_key_e_luminance_between_C_and_c"]
    acc = "back_region_accent_texels_" + ACCENT_KEYS
    return {
        "declared_unchanged_layers_byte_identical_to_v14": all(p["declared_unchanged_layers_identical_to_v14"].values()),
        "changed_layers_keep_v14_alpha": all(p["changed_layers_alpha_identical_to_v14"].values()),
        "removed_canister_was_inside_v14_pack_alpha": p["canister_alpha_inside_v14_pack"],
        "silhouette_texel_count_equals_v14": p["silhouette_texels_v15"] == p["silhouette_texels_v14"],
        "silhouette_edge_keys_identical_to_v14_no_new_rim": p["edge_v15"] == p["edge_v14"],
        "palette_extension_e_is_between_C_and_c": lc < le < lcc,
        "back_region_has_fewer_pale_accent_texels_than_v14": v15[acc] < v14[acc],
        "pack_face_has_no_pale_buckle_or_steel": all(q not in v15["pack_visible"]["keys"] for q in "PpmMZ"),
        "lower_body_no_warm_grey_u_planes": "u" not in v15["lower_body_38_67"]["keys"],
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
        on_bg(comp, bg, 8).save(os.path.join(out_dir, f"v15_x8_{tag}.png"))
    for path in nosprites:
        tag = os.path.splitext(os.path.basename(path))[0]
        full = game_scale(comp, path)
        k = full.width // 640
        full.save(os.path.join(out_dir, f"v15_game-scale_{tag}.png"))
        full.crop((120 * k, 180 * k, 360 * k, 300 * k)).save(os.path.join(out_dir, f"v15_game-scale-crop-1x_{tag}.png"))
        crop = full.crop((240 * k, 190 * k, 340 * k, 280 * k))
        z = 8 // k
        crop.resize((crop.width * z, crop.height * z), Image.NEAREST).save(
            os.path.join(out_dir, f"v15_game-scale-crop-x{z}_{tag}.png"))
    p = pose_report(comp, blobs)
    print(json.dumps({**stats(comp), "material_texels_v15": region_counts(comp), "pose": p,
                      "pose_gates": pose_gates(p), "silhouette_vs_v14": silhouette_report(comp, blobs)}))


# ===================================================================================================== editable files
ZIP_DT = (2026, 10, 18, 21, 4, 46)      # fixed (zip needs even seconds) -> byte-identical rebuilds


def make_pxo(png, blobs):
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": n == "guides", "metadata": {}, "name": n,
                   "new_cels_linked": False, "opacity": 1.0, "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": n != "guides"} for n in LAYER_NAMES]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0}
                             for _ in LAYER_NAMES], "duration": 1.0, "metadata": {}}]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": json.dumps("female-battle-idle-right-static-unapproved-v15"),
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
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        def put(name, payload):
            z.writestr(zipfile.ZipInfo(name, ZIP_DT), payload, zipfile.ZIP_DEFLATED)
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
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", ZIP_DT), "image/openraster", zipfile.ZIP_STORED)
        z.writestr(zipfile.ZipInfo("stack.xml", ZIP_DT), "\n".join(stack) + "\n", zipfile.ZIP_DEFLATED)
        for name in LAYER_NAMES:
            z.writestr(zipfile.ZipInfo(f"data/{name}.png", ZIP_DT), png_bytes(blobs[name]), zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("mergedimage.png", ZIP_DT), png, zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("Thumbnails/thumbnail.png", ZIP_DT), png, zipfile.ZIP_DEFLATED)
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
DIAG_MARKERS = ("ERROR", "WARNING", "SCRIPT ERROR", "Shader", "shader", "Parse Error", "Traceback")


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


def diagnostics(text):
    """Pixelorama console lines carrying an error / warning / shader marker, with repeat counts (order kept)."""
    out = {}
    for line in (text or "").replace("\r\n", "\n").split("\n"):
        s = line.strip()
        if s and any(m in s for m in DIAG_MARKERS):
            out[s] = out.get(s, 0) + 1
    return [{"line": k, "count": v} for k, v in out.items()]


def pixelorama_export(exe, src, out_dir, split):
    """Headless export with APPDATA redirected to a fresh temp dir (never touches the real config). Returns the exit
    code, the exported PNGs and the application's own diagnostic lines (reported, not gated)."""
    env = dict(os.environ)
    env["APPDATA"] = tempfile.mkdtemp(prefix="wb-pxappdata-")
    args = [exe, "--headless", "--quit", "--", "--export"] + (["--split-layers"] if split else []) + \
           ["-o", os.path.join(out_dir, "f.png"), src]
    try:
        p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240,
                           env=env)
    finally:
        shutil.rmtree(env["APPDATA"], ignore_errors=True)
    files = sorted(f for f in os.listdir(out_dir) if f.lower().endswith(".png"))
    return p.returncode, {f: read_bytes(os.path.join(out_dir, f)) for f in files}, \
        diagnostics((p.stdout or "") + "\n" + (p.stderr or ""))


def pixelorama_roundtrips(exe, pxo, ora, blobs, comp):
    """Native pixel equality (gated) and application diagnostics (recorded separately), plus the same flat export of the
    unchanged v14 .pxo as a control for the diagnostics."""
    snap0 = appdata_snapshot()
    tmp = tempfile.mkdtemp(prefix="wb-fv15-")
    px, diags, flat_png = {}, {}, None
    try:
        for kind, data_ in (("pxo", pxo), ("ora", ora)):
            src = os.path.join(tmp, f"cand.{kind}")
            with open(src, "wb") as f:
                f.write(data_)
            for split in (False, True):
                od = os.path.join(tmp, f"{kind}-{'split' if split else 'flat'}")
                os.makedirs(od)
                rc, outs, dg = pixelorama_export(exe, src, od, split)
                key = f"{kind}_{'split' if split else 'flat'}"
                diags[key] = dg
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
        # controls: the unchanged, locked v14 .pxo and .ora through the same flat export
        control = {}
        v14_rgba = decode(read_bytes(repo_path(V14_PNG_REL)))[2]
        for kind, rel in (("pxo", V14_PXO_REL), ("ora", V14_ORA_REL)):
            src = os.path.join(tmp, f"v14-control.{kind}")
            with open(src, "wb") as f:
                f.write(read_bytes(repo_path(rel)))
            od = os.path.join(tmp, f"v14-control-{kind}-flat")
            os.makedirs(od)
            rc, outs, dg = pixelorama_export(exe, src, od, False)
            diags[f"v14_control_{kind}_flat"] = dg
            control[f"{kind}_flat"] = {"exit": rc, "pngs": len(outs), "flat_rgba_equals_v14_png":
                                       len(outs) == 1 and decode(next(iter(outs.values())))[2].tobytes()
                                       == v14_rgba.tobytes()}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    px["real_appdata_pixelorama_untouched_except_heartbeat"] = snap0 == appdata_snapshot()
    is_ctrl = lambda k: k.startswith("v14_control_")
    unexplained = {}
    for k, v in diags.items():          # candidate lines absent from the same-format v14 control
        if not is_ctrl(k):
            ctrl = {d["line"] for d in diags[f"v14_control_{k.split('_')[0]}_flat"]}
            unexplained[k] = sorted(d["line"] for d in v if d["line"] not in ctrl)
    app = {"per_export": diags, "v14_controls": control,
           "candidate_exports_with_diagnostics": sorted(k for k, v in diags.items() if not is_ctrl(k) and v),
           "v14_controls_with_diagnostics": sorted(k for k, v in diags.items() if is_ctrl(k) and v),
           "candidate_lines_not_in_same_format_v14_control": unexplained,
           "application_run_clean": not any(diags.values()),
           "note": "pixel equality is gated; application diagnostics are reported, not gated, and are compared with "
                   "the unchanged v14 control. No GUI Save As / reopen was run."}
    return px, flat_png, app


# ===================================================================================================== build / check
LAYER_NOTES = {
    "far-leg": "v14 far leg drawing (braced back, small knee bend); v15 values: one receding shadow plane (deep slate back C, spruce T; v14's lit front stripe t removed); boot: dark cuff band (L), shaft and heel side dark leather (L), mid leather (d), lit vamp/toe plane (D), lowest foot row and welt lit leather (D) in the contact shadow; v14's warm-grey toe texel u -> D",
    "hip-drape": "v8 teal back-hip cloth tucked under the pack (v14 drawing); v15: in the pack's shadow, deep teal Q with one q texel where it leaves the pack (v14: lit g edge + q body)",
    "pack": "v14/v13 slumped-sack outline; v15 face in broad planes: lit flap (D, as v14), one deep body (d), shaded back side (l / L), dark underside (L); v14's pale buckle, strap line and flap marks removed",
    "bedroll": "v13 teal bedroll cylinder with v14's deep-teal top edge; v15 top plane mid teal g (v14 pale G)",
    "ponytail": "high tied ponytail with a single tapered tip (v14, unchanged)",
    "loose-lock": "separate loose lock falling from the hook tip at the nape (v14, unchanged)",
    "near-leg": "v14 near leg drawing (knee juts forward, pad on a strap, shin drops back); v15 values: v14's warm-grey u planes -> lit spruce t, shin C C T T t; boot: shaft front lit (D), heel side dark (L), mid (d), lit vamp/toe (D), two-row lit base (D)",
    "coat": "v8 storm-slate coat torso and belt (v14, unchanged)",
    "coat-skirt": "split coat skirt, v14 drawing and lit front panel; v15: back-tail body in the new deep-mid slate e (v14 c), v14's C back edge / fold flank, o fold ridge and split edge and l hem kept",
    "shirt-lapel": "white shirt wedge framed by lit lapel texels and a dark lapel line (v14, unchanged)",
    "near-arm": "sword arm reaching forward with the sleeve rolled to the elbow (v14, unchanged)",
    "insignia": "teal 3x3 diamond on the upper sleeve (v14, unchanged)",
    "sword-blade": "ordinary short sword blade raised forward at 45 degrees (v14, unchanged; same reach)",
    "sword-guard": "small steel crossguard square to the blade (v14, unchanged)",
    "fist": "fingerless dark glove with bare skin knuckles and thumb round the grip (v14, unchanged)",
    "head": "v14 head and face (v14's brow recolour kept), byte-identical to v14",
    "hair-tie": "dark leather hair band where the ponytail leaves the head (v14, unchanged)",
    "collar": "raised coat collar standing behind the nape (v14, unchanged)",
    "scarf-neck": "compact teal scarf (v14, unchanged)",
    "collar-front": "front point of the raised coat collar over the scarf's front edge (v14, unchanged)",
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
        "sprite_acceptance_count": "0/52 (unchanged)", "production_points_earned_by_this_version": 0,
        "node_scale_intended": 1.0, "display_proportion_equivalent": 0.65,
        "refines": {"files": V14_LOCKS,
                    "hash_algorithm": "sha256-bytes for .png/.pxo/.ora; sha256-text-lf-v1 for the .json manifest",
                    "relationship": "same cell/pin/sole/crown rows, alpha silhouette and every outline as v14; "
                                    "v15 is a material-value pass: " + "; ".join(V15_TARGETS) + "; v14 left untouched",
                    "silhouette_vs_v14": silhouette_report(comp, blobs)},
        "pose": pose,
        "pose_gates": pose_gates(pose),
        "palette_extension": {"key": "e", "hex": PALETTE["e"],
                              "note": "one deep-mid storm slate between v8's C and c (same hue family), used only "
                                      "for the back coat tail body"},
        "removed": {"layer": "canister", "why": "named defect 'back / pack details are busy': at 1x the v14 canister "
                                                "read as a pale grey mark, not a bottle"},
        "identity_references": {"character_sheet": CHARACTER_SHEET_REL, "v8_south_static": V8_SOUTH_REL},
        "feedback_addressed": "root review of the v14 actual 640x360 four-person archive capture (2026-10-18): coat / "
                              "feet merge with the dark floor; back / pack details are busy. v14's cloth volume and "
                              "slimmer boot shape are preserved (same alpha). Creator's standing request on v11: "
                              "'继续精修静止帧' (keep refining the still), not an approval",
        "v15_targets": V15_TARGETS,
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
        "sole_on_row_67_same_as_v14": st["sole_row"] == SOLE_ROW,
        "crown_on_row_7_same_as_v14_0p65_proportion": st["crown_row_measured"] == CROWN_ROW,
        "leftmost_texel_ge_x15_liang_gap_kept": st["alpha_bounds_inclusive"][0] >= 15,
        "rightmost_texel_le_62_sentry_gap_and_blade_reach_kept": st["alpha_bounds_inclusive"][2] <= 62,
        "nothing_at_or_below_pin_row": st["pin_row_clear"],
        "both_boots_touch_sole_row": bool((a[SOLE_ROW, 20:PIN[0], 3] > 0).any() and (a[SOLE_ROW, PIN[0]:, 3] > 0).any()),
        "transparent_border": bool(not a[0, :, 3].any() and not a[-1, :, 3].any()
                                   and not a[:, 0, 3].any() and not a[:, -1, 3].any()),
    }


def structure_ok(sil):
    return (sil["layers_added_vs_v14"] == [] and sil["layers_removed_vs_v14"] == V14_LAYERS_REMOVED
            and sil["palette_keys_removed_vs_v14"] == REMOVED_KEYS_VS_V14
            and sil["palette_keys_added_vs_v14"] == ADDED_KEYS_VS_V14 and sil["palette_shared_keys_same_colour"]
            and sil["silhouette_alpha_identical_to_v14"]
            and sil["silhouette_bbox_v15"] == sil["silhouette_bbox_v14"])


def build(exe):
    lock = locks()
    if not lock["unchanged"]:
        raise SystemExit(f"v14 / protected lock mismatch: {lock['mismatched']}")
    blobs, comp = render()
    st = stats(comp)
    sg = static_gates(comp, st)
    pg = pose_gates(pose_report(comp, blobs))
    sil = silhouette_report(comp, blobs)
    if not all(sg.values()) or not all(pg.values()) or not structure_ok(sil):
        raise SystemExit(f"static/preservation gate failed: {json.dumps({'static': sg, 'pose': pg})}")
    tool_png = png_bytes(comp)
    pxo, ora = make_pxo(tool_png, blobs), make_ora(tool_png, blobs)
    if make_pxo(tool_png, blobs) != pxo or make_ora(tool_png, blobs) != ora:
        raise SystemExit("editable build is not deterministic")
    px, flat, app = pixelorama_roundtrips(exe, pxo, ora, blobs, comp)
    if flat is None or not all(v["pass"] for v in px.values() if isinstance(v, dict)):
        raise SystemExit(f"Pixelorama round-trip failed: {json.dumps(px)}")
    png = flat                         # the delivered PNG is Pixelorama's export of the layered .pxo
    out = repo_path(OUT_DIR_REL)
    os.makedirs(_fs(out), exist_ok=True)
    for name, data in ((PNG_NAME, png), (PXO_NAME, pxo), (ORA_NAME, ora),
                       (MANIFEST_NAME, make_manifest(png, pxo, ora, comp, True))):
        print(write_new(os.path.join(out, name), data), f"{OUT_DIR_REL}/{name}", sha256_bytes(data))
    print(json.dumps({"pixelorama_native": px, "pixelorama_application_diagnostics": app}))
    if not locks()["unchanged"]:
        raise SystemExit("v14 / protected lock changed during build")


def check(exe):
    report = {"status": "UNAPPROVED, NONRUNTIME test-only candidate", "locks_before": locks()}
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
                                      and man["game_bible_or_acceptance_counters_changed"] is False
                                      and man["production_points_earned_by_this_version"] == 0),
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
    report["silhouette_vs_v14"] = sil
    g["layers_palette_alpha_vs_v14_as_declared"] = structure_ok(sil)
    g["manifest_silhouette_matches_fresh"] = man["refines"]["silhouette_vs_v14"] == json.loads(json.dumps(sil))
    pose = pose_report(a, blobs)
    report["pose"] = pose
    pg = pose_gates(pose)
    g.update(pg)
    g["manifest_pose_matches_fresh"] = man["pose"] == json.loads(json.dumps(pose)) and man["pose_gates"] == pg
    if exe:
        px, flat, app = pixelorama_roundtrips(exe, pxo, ora, blobs, comp)
        report["pixelorama_1_2_3_headless_native"] = px
        report["pixelorama_1_2_3_application_diagnostics_not_gated"] = app
        g["pixelorama_native_roundtrips_pixel_exact"] = all(v["pass"] for v in px.values() if isinstance(v, dict)) \
            and px["real_appdata_pixelorama_untouched_except_heartbeat"]
        g["png_equals_fresh_pixelorama_flat_export"] = flat == png
    report["metrics"] = {**st, "material_texels": region_counts(a)}
    report["locks_after"] = locks()
    g["v14_and_protected_paths_unchanged"] = report["locks_before"]["unchanged"] and report["locks_after"]["unchanged"]
    report["gates"] = g
    report["gates_passed"] = f"{sum(bool(v) for v in g.values())}/{len(g)}"
    report["result"] = "PASS" if all(g.values()) else "FAIL"
    print(json.dumps(report, indent=1, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
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
