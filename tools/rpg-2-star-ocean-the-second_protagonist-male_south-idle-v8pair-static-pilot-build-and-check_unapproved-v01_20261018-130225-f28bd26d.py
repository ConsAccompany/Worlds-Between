"""Male protagonist south-facing EXPLORATION IDLE static pilot paired to the approved female selout v8 (UNAPPROVED):
one hand-placed 80x112 cell (96-texel body -> 48 logical px at 0.5), editable Pixelorama .pxo + layered .ora with
13 role layers + hidden guides, declared palette, manifest and deterministic technical gates.

Scope: one direction (south), one static idle frame, male protagonist only. No animation, no other direction, no
runtime integration, no approval or counter change (runtime sprites stay 0/52, scene visuals 3/12, meter 40.8%,
plays 0/2). Identity source: the male character sheet (front view): tousled outward-pointing dark-brown short hair,
teal scarf, open grey-brown field coat with rolled sleeves, hand on the pack strap, teal sash, olive trousers with a
knee pad, tall cuffed boots, teal bedroll on a brown pack behind the viewer-right shoulder. The creator-approved female
selout v8 south static is the density / proportion / light benchmark (same cell, pin, 96-texel body, 0.5 scale,
1-texel near-black outer outline, upper-left light, 3-4 step material ramps); none of its texels or palette entries
are copied and none of its files are written. The rejected 32x48 male frame and the local v01/v02 high-density pilots
are not used as a base: every cluster here was placed fresh.

Source of truth: MAP (colour keys) and ROLE (role-layer keys) below, literal 56x96 grids placed at cell offset
(12, 8). They were placed by hand as shape spans, polygons, strokes and small stamps in a scratch authoring script,
judged on x5 previews over grey / dark-floor / bright-floor colours and at 1x / 2x next to v8, then frozen here.
No image generation, sampling of the concept sheet, resampling, filtering, quantization or dithering was used.

Modes (real Python, isolated):
  python -I -B <this file> build                   write PNG, .pxo, .ora, palette, manifest (never overwrites)
  python -I -B <this file> check --pixelorama X    gates + rebuild equality + Pixelorama CLI .pxo/.ora round trips
                                                   + female v8 source files unchanged
  python -I -B <this file> preview <out.png>       x4 nearest preview of the sprite alone
"""
import argparse, hashlib, io, json, os, shutil, subprocess, sys, tempfile, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
VISUAL_ID = "protagonist-male"
SUBJECT = "south-idle-v8pair"
VARIANT = "unapproved-v01"
STAMP = "20261018-130225"             # UTC
RUN_ID = "3617dbe6"
W, H = 80, 112
GRID_W, GRID_H = 56, 96
GRID_OFFSET = (12, 8)                 # grid (0,0) -> cell (12,8); body rows 8..103 like v8
PIN = (40, 104)
BODY_ROWS = (8, 103)
TEMPLATE_ROWS = {"head_top": 8, "shoulder": 34, "belt": 54, "knee": 76, "sole": 103}   # v8 south pose rows (guides)
DISPLAY_SCALE = 0.5                   # 96 texels -> 48 logical px; 1 texel = 1 window px at 1280x720
OUT_DIR_REL = "game/assets/characters/protagonist-male-v8pair"
PIXELORAMA_VERSION = "v1.2.3-stable"
GUIDE_RGB = (255, 0, 255)
ZIP_DT = (2026, 10, 18, 13, 2, 24)

V8_DIR = "game/assets/characters/pixelorama-pilots/"
V8_PNG = V8_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png"
# The approved female v8 source package must stay exactly as committed at 160b823.
V8_LOCKS = {
    V8_PNG: ("ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd", "bytes"),
    V8_PNG + ".import": ("f83fcbce68ae824fddc4dc784fdc7c3cb0f4392326608dbdb09fab932370840d", "text"),
    V8_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-manifest_m8-v08_20261015-021600-2d6c5eff.json": ("3ba35811bf4d55b061b7719c6451908bdbb1eb68425bdda2c2303cc669f310ed", "text"),
    V8_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-editable-manifest_m8-v08_20261015-080907-270b2256.json": ("d40059be868e50f6acbea509e14dd2e8ccd6cac3b1405f39399c9fbff17e73c3", "text"),
    V8_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-editable_m8-v08_20261015-080907-c8a1c140.pxo": ("cafa4998b107ae4b884cc877b80bbc695df267f37e09fb6e69701567f08a849e", "bytes"),
}
# Stable, tracked references (hash recorded in the manifest; volatile Bible/progress files are cited in the QA note).
REFS = {
    "identity_sheet_male": ("outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_male_20261013-153316-5b7c19e2.png", "bytes"),
    "benchmark_female_selout_v8_png": (V8_PNG, "bytes"),
    "benchmark_female_selout_v8_decision": ("docs/character-visuals/rpg-2-star-ocean-the-second_protagonist-female_south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md", "text"),
    "benchmark_female_selout_v8_visual_qa": ("docs/qa/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8_visual-qa-note_m8-v08_20261015-021600-c1694107.md", "text"),
    "rejected_male_32x48_south_frame": ("game/assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_protagonist-male_exploration-sprite-south_m8-draft_20261014-133644-a01be730.png", "bytes"),
    "prior_male_hd_v02_qa_note_not_used_as_base": ("docs/qa/rpg-2-star-ocean-the-second_protagonist-male_south-idle-high-density-static-pilot_qa-note_unapproved-nonruntime-v02_20261017-160419-ba29a498.md", "text"),
    "cast_identity_audit_48px": ("docs/qa/rpg-2-star-ocean-the-second_science-cast_hairstyle-and-identity-at-48px_unapproved-v01_20261016-183000-9234b6e1.md", "text"),
}

# Named ramps, light from the upper left. Hues follow the male sheet's swatches (dark-brown hair, warm grey-brown coat,
# cream shirt, olive-grey trousers, brown leather/boots, tea-green scarf; the bedroll is a darker, bluer teal).
RAMPS = {
    "outline": {"K": "0c0a0c"},
    "hair-dark-brown": {"1": "735442", "2": "4b362b", "3": "30231d", "4": "1f1614"},
    "skin": {"F": "f0c090", "f": "d49868", "e": "a86a48", "D": "7a4234"},
    "eye": {"y": "2a1a16"},
    "scarf-tea-green": {"S": "82c8b8", "s": "46988c", "Z": "2a6660"},
    "bedroll-teal": {"T": "5e9c9c", "t": "3c7678", "u": "28505a"},
    "coat-grey-brown": {"A": "8c7664", "B": "6a5b4e", "C": "4a3e36", "c": "2b2422"},
    "leather": {"L": "b27c4e", "l": "80523a", "m": "4e3224"},
    "shirt-cream": {"W": "efe6d2", "w": "c9bea6", "v": "978a76"},
    "trousers-olive-grey": {"P": "7e7a62", "p": "5c5a4a", "o": "3c3b30"},
    "boots-gloves": {"O": "8c5a3a", "b": "623d2a", "q": "3a2520"},
    "metal": {"M": "dcdad2", "X": "8e8c88"},
}
PAL = {k: v for ramp in RAMPS.values() for k, v in ramp.items()}

# Role layers, Pixelorama layer 1 = bottom. Outline texels belong to the part they outline.
ROLE_LAYERS = [("bedroll", "r"), ("pack", "b"), ("coat-skirt", "c"), ("sash", "a"), ("legs", "l"), ("boots", "o"),
               ("torso-coat", "t"), ("harness", "z"), ("arm-hanging", "m"), ("arm-grip", "n"), ("head-face", "f"),
               ("hair", "h"), ("scarf", "s")]
LAYERS = [n for n, _ in ROLE_LAYERS] + ["guides"]
LAYER_NOTES = {
    "bedroll": "teal bedroll on top of the pack behind the viewer-right shoulder: lit top band, shadow underside, leather strap with a steel buckle, spiral end",
    "pack": "brown leather pack body seen behind the viewer-right arm: lit top edge, side seam, strap with a steel buckle",
    "coat-skirt": "back of the open field coat flaring to the knee behind the legs: lit viewer-left panel, shadow viewer-right panel, fold lines, leather hem; dark yoke behind the hips",
    "sash": "teal sash hanging from the belt at the viewer-left hip behind the relaxed leg, lit edge and fold, forked end",
    "legs": "olive-grey trousers: weight on the straight viewer-right leg, relaxed viewer-left leg angled out with a cargo pocket and a leather knee pad; lit left edges, knee crease, bunching above the boots",
    "boots": "tall brown boots with folded lit cuffs, strap + buckle, lit toe caps; relaxed viewer-left foot turned out and set back (sole row 101), weight-bearing viewer-right foot forward (sole row 103)",
    "torso-coat": "popped coat collar framing the scarf, one lit chest plane on the left, shadow plane on the right, cream laced shirt in the opening, leather lapel piping, teal community-diamond emblem, belt with steel buckle, hip pouch, coat fronts over the hips",
    "harness": "2-texel leather pack straps from the shoulders down the chest, steel buckle on the right strap",
    "arm-hanging": "viewer-right arm hanging relaxed: coat sleeve in shadow, rolled cream cuff, bare forearm, fingerless-gloved fist",
    "arm-grip": "viewer-left arm: lit coat sleeve, elbow at the side, rolled cream cuff, bare forearm rising to a fingerless-gloved fist gripping the pack strap at the chest",
    "head-face": "13-wide face turned slightly to the viewer-left, chin on cell row 33: thick straight brows, 2x2 eyes with catch-lights, nose shadow, small closed smile, ear, jaw shadow on the right",
    "hair": "tousled dark-brown short hair: three uneven crown tufts, outward side flicks, fringe locks pointing down over the forehead, short nape behind the ear; small lit cap upper left, strand separations, shadow side on the right",
    "scarf": "tea-green scarf wrapped under the jaw inside the collar with a short point down the shirt; lit left folds, shadowed folds on the right",
    "guides": "hidden + locked #ff00ff: cell border, ticks on the v8 template rows (head top 8, shoulder 34, belt 54, knee 76, sole 103), pin (40,104); never exported",
}

MAP = [
    "........................K....KK...K.....................",  # 00 (cell row 8)
    ".......................K2K..K13K.K3K....................",  # 01 (cell row 9)
    ".....................KK222KK3223K323KK..................",  # 02 (cell row 10)
    "...................KK32212233323333333K.................",  # 03 (cell row 11)
    "..................K3442121234333243333KKK...............",  # 04 (cell row 12)
    "..................K4221222132432334333343K..............",  # 05 (cell row 13)
    "..................K32122333233433343343KK...............",  # 06 (cell row 14)
    "................KK3321334333334333342343K...............",  # 07 (cell row 15)
    "...............K322313333433333433343343K...............",  # 08 (cell row 16)
    "................K333333224333333433343343K..............",  # 09 (cell row 17)
    ".................K333323334333433333333344K.............",  # 10 (cell row 18)
    ".................K33434333433334333234443K..............",  # 11 (cell row 19)
    ".................K33434323ff23ff32333443K...............",  # 12 (cell row 20)
    "..................K334323FFFFFFff333344K................",  # 13 (cell row 21)
    "...................K34F344fFFF4444fK344K................",  # 14 (cell row 22)
    "...................K3KFFyyFFFFyyfffK444K................",  # 15 (cell row 23)
    "....................KKFFWyFFFFyWFffK44K.................",  # 16 (cell row 24)
    ".....................KFFFFFFFeFFFffe444K....KKK.........",  # 17 (cell row 25)
    ".....................KFFFFFFFeFFFfDe44KKKKKKtttK........",  # 18 (cell row 26)
    ".....................KFFFFFFDFFFffeTTTlmTTTtTTtuK.......",  # 19 (cell row 27)
    "......................KFFFeFFeFFfeTTTTlmTTTTtuTuK.......",  # 20 (cell row 28)
    "......................KFFFFDeFFfeKttttlmtttTuutuK.......",  # 21 (cell row 29)
    ".......................KFFFFFFfeKKttttMXtttTttTuK.......",  # 22 (cell row 30)
    "........................KFFFffeKKKttttlmttttTtuuK.......",  # 23 (cell row 31)
    ".....................KKKsKeeeeeeKsttttlmttttuuuuK.......",  # 24 (cell row 32)
    "....................KAAKSsKeeeeeKsKCCulmuuuuuuuuK.......",  # 25 (cell row 33)
    "...................KAAAKSSsKKKKKssKBCClmuuuuuuuK........",  # 26 (cell row 34)
    "...............KKKKBBlmBKSsSsssssKBlmBKKKKKKKKK.........",  # 27 (cell row 35)
    "..............KBBBKAAlmABKssSsssKBBlmBKBBKKlLLLK........",  # 28 (cell row 36)
    ".............KBAABKAAlmABcKssssKCBBlmBKAABKllllK........",  # 29 (cell row 37)
    ".............KAAABKAAlmABcvKssKlBCBlmCKABCKlllmK........",  # 30 (cell row 38)
    ".............KAAABKAAKKKKcvvKKwlBCBlmCKBBCKlllmK........",  # 31 (cell row 39)
    "............KBAABBKAKbOOKcvWvWwlBCSlmCcKBCKlllmK........",  # 32 (cell row 40)
    "............KBAABBCKqbbbKvWWWWWwlSslmCcKBCKlllmK........",  # 33 (cell row 41)
    "............KBAABBFFFFKKKvWWWWWwlBZlmCcKBCKlllmK........",  # 34 (cell row 42)
    "............KBAABFFFFKmAcvWWWWWwlBBlmCcKBBcKllmK........",  # 35 (cell row 43)
    "............KBAABFFFFKmAcvWwWWWwlBcClmcKBBCKmmmK........",  # 36 (cell row 44)
    "............KWWWWwFFKlmAcvWWWWwwlBcClmcKBBCKlMmK........",  # 37 (cell row 45)
    "............KWWWWWwfKlmBcvWWWWWwlBBClmcKBBCKlXmK........",  # 38 (cell row 46)
    "............KWWWWWwKAlmcvWWWWWWWwlBClmcKBBCKllmK........",  # 39 (cell row 47)
    ".............KvvvvKAAlmcvWWWwWWWwlBCMXcKWWwKllmK........",  # 40 (cell row 48)
    "..............KKKKBAAlmcvWWWWWWWwlBClmcKWWwKllmK........",  # 41 (cell row 49)
    "..................KBAlmcvWWWWWWWwlBClmKvvvvKllmK........",  # 42 (cell row 50)
    "..................KBBlmcvWWWWwWWwlBClmKFFFKlllmK........",  # 43 (cell row 51)
    "..................KBBlmcvWWWWWWWwlBClmKFFFKlllmK........",  # 44 (cell row 52)
    ".................KKLLLLLLLLMMMLLLLLLLLKFFFKmmmK.........",  # 45 (cell row 53)
    "................KssKllmllllMlXllllmlllKKFFeKKK..........",  # 46 (cell row 54)
    "................KsSKmmmmmmmXXXmmmmmmmmKbObbbK...........",  # 47 (cell row 55)
    "................KsSKBBBcBBBBBBBBBmlLmKKObbbbK...........",  # 48 (cell row 56)
    "................KSsKBBBcBpoopppBBmllKBKbbbbbK...........",  # 49 (cell row 57)
    "................KSsKBBBcBpoopppBBmmmKBKbqqqqK...........",  # 50 (cell row 58)
    "...............KsSsKBBBcBpooKppBBlBBKBKKFfeqK...........",  # 51 (cell row 59)
    "...............KsSsKBBBcBpoKcKPBBlBBKBBKKKKK............",  # 52 (cell row 60)
    "...............KSssKBBBcppoKcKPpBlBBKBBK................",  # 53 (cell row 61)
    "...............KSssKKBBpppoKcKPppBBKCCCBK...............",  # 54 (cell row 62)
    "...............KSsKBBKooppoKcKPppoKCCCCBK...............",  # 55 (cell row 63)
    "..............KsSsKBKPPoppoKcKPppoKCCCCCK...............",  # 56 (cell row 64)
    "..............KSssKBKXpoppoKcKPppoKCCCCCK...............",  # 57 (cell row 65)
    "..............KSssKBKpopppKccKPpppKCCCCBBK..............",  # 58 (cell row 66)
    ".............KSssZKBKpopppoKKpPpppKBCCCBBK..............",  # 59 (cell row 67)
    ".............KSssKcKoooppopK.KPpppKBCcCBBK..............",  # 60 (cell row 68)
    ".............KSssKcKPppppoK..KPpppKBCcCBCK..............",  # 61 (cell row 69)
    "............KSssZKcKpppppoK..KPPppoKCcCCBBK.............",  # 62 (cell row 70)
    "............KSssZKcKppppooK..KPPppoKCcCCBBK.............",  # 63 (cell row 71)
    "............KSssKBKPppppopK..KPPppoKCcCCBBK.............",  # 64 (cell row 72)
    "............KSssKcKmmpppoK...KpPopoKCcCCBBK.............",  # 65 (cell row 73)
    "............KSssKcKLlmpooK...KpPpooKCCcCBCBK............",  # 66 (cell row 74)
    "...........KsSsKBcKllmpooK...KpPppoKCCcCBCBK............",  # 67 (cell row 75)
    "...........KSssKBKmXmmpoK.....KPPppKBCcCBCBK............",  # 68 (cell row 76)
    "...........KSssKBKmmmppoK.....KPoppKBCcCCBBK............",  # 69 (cell row 77)
    "..........KBKKKKBKPppppoK.....KPPooKBCcCCBBBK...........",  # 70 (cell row 78)
    "..........KBBAABBKPpppooK.....KPPppKBCcCCBCBK...........",  # 71 (cell row 79)
    "..........KBBAABBKppppooK.....KPPppoKCcCCBCBK...........",  # 72 (cell row 80)
    "...........KlllllKopppooK.....KPPppoKllllllK............",  # 73 (cell row 81)
    "............KKKKKPpoopoK......KPoopooKKKKKK.............",  # 74 (cell row 82)
    "...............KpPppppoK......KpPpoooK..................",  # 75 (cell row 83)
    "...............KpPppppoK......KpPppooK..................",  # 76 (cell row 84)
    "...............KPPPPpooK......KpPppooKKK................",  # 77 (cell row 85)
    "..............KOKKKKKKKK......KKKKKKKOObK...............",  # 78 (cell row 86)
    "..............KbOOOOObbK......KbOOOOOObbK...............",  # 79 (cell row 87)
    "..............KqqqqqqqqK......KqqqqqqqqqK...............",  # 80 (cell row 88)
    "...............KObbbbqK........KObbbbbqK................",  # 81 (cell row 89)
    "...............KObbbbqK........KObbbbbqK................",  # 82 (cell row 90)
    "...............KObbbbqK........KObbbbbqK................",  # 83 (cell row 91)
    "...............KOmmMmqK........KOmmmMmqK................",  # 84 (cell row 92)
    "...............KObbbbqK........KObbbbbqK................",  # 85 (cell row 93)
    "...............KObbbbqK........KObbbbbqK................",  # 86 (cell row 94)
    "..............KbbbbbbqK........KObbbbbqK................",  # 87 (cell row 95)
    ".............KbbbbbbbqK........KObbbbbqK................",  # 88 (cell row 96)
    "............KbLOObbbbqK........KbbbbbbbqK...............",  # 89 (cell row 97)
    "...........KbOOOObbbbbK........KbbbOOLObqK..............",  # 90 (cell row 98)
    "...........KmmmmmmmmmmK........KbbbbOOOObbK.............",  # 91 (cell row 99)
    "...........KqqqqqqqqqqK........KbbbbbbbbbqqK............",  # 92 (cell row 100)
    "............KKKKKKKKKK.........KmmmmmmmmmmmK............",  # 93 (cell row 101)
    "...............................KqqqqqqqqqqqK............",  # 94 (cell row 102)
    "................................KKKKKKKKKKK.............",  # 95 (cell row 103)
]

ROLE = [
    "........................h....hh...h.....................",  # 00 (cell row 8)
    ".......................hhh..hhhh.hhh....................",  # 01 (cell row 9)
    ".....................hhhhhhhhhhhhhhhhh..................",  # 02 (cell row 10)
    "...................hhhhhhhhhhhhhhhhhhhh.................",  # 03 (cell row 11)
    "..................hhhhhhhhhhhhhhhhhhhhhhh...............",  # 04 (cell row 12)
    "..................hhhhhhhhhhhhhhhhhhhhhhhh..............",  # 05 (cell row 13)
    "..................hhhhhhhhhhhhhhhhhhhhhhh...............",  # 06 (cell row 14)
    "................hhhhhhhhhhhhhhhhhhhhhhhhh...............",  # 07 (cell row 15)
    "...............hhhhhhhhhhhhhhhhhhhhhhhhhh...............",  # 08 (cell row 16)
    "................hhhhhhhhhhhhhhhhhhhhhhhhhh..............",  # 09 (cell row 17)
    ".................hhhhhhhhhhhhhhhhhhhhhhhhhh.............",  # 10 (cell row 18)
    ".................hhhhhhhhhhhhhhhhhhhhhhhhh..............",  # 11 (cell row 19)
    ".................hhhhhhhhhffhhffhhhhhhhhh...............",  # 12 (cell row 20)
    "..................hhhhhhhffffffffhhhhhhh................",  # 13 (cell row 21)
    "...................hhhfhfffffffffffhhhhh................",  # 14 (cell row 22)
    "...................hhhfffffffffffffhhhhh................",  # 15 (cell row 23)
    "....................hffffffffffffffhhhh.................",  # 16 (cell row 24)
    ".....................fffffffffffffffhhhh....rrr.........",  # 17 (cell row 25)
    ".....................fffffffffffffffhhhrrrrrrrrr........",  # 18 (cell row 26)
    ".....................ffffffffffffffrrrrrrrrrrrrrr.......",  # 19 (cell row 27)
    "......................ffffffffffffrrrrrrrrrrrrrrr.......",  # 20 (cell row 28)
    "......................ffffffffffffrrrrrrrrrrrrrrr.......",  # 21 (cell row 29)
    ".......................ffffffffffrrrrrrrrrrrrrrrr.......",  # 22 (cell row 30)
    "........................sfffffffssrrrrrrrrrrrrrrr.......",  # 23 (cell row 31)
    ".....................ttsssffffffssrrrrrrrrrrrrrrr.......",  # 24 (cell row 32)
    "....................tttssssfffffsssttrrrrrrrrrrrr.......",  # 25 (cell row 33)
    "...................ttttsssssssssssstttrrrrrrrrrr........",  # 26 (cell row 34)
    "...............nnnnttzztsssssssssstzztmmmbbbbbb.........",  # 27 (cell row 35)
    "..............nnnnnttzzttssssssssttzztmmmmbbbbbb........",  # 28 (cell row 36)
    ".............nnnnnnttzztttsssssstttzztmmmmmbbbbb........",  # 29 (cell row 37)
    ".............nnnnnnttzzttttssssttttzztmmmmmbbbbb........",  # 30 (cell row 38)
    ".............nnnnnnttnnnntttsstttttzztmmmmmbbbbb........",  # 31 (cell row 39)
    "............nnnnnnntnnnnnttttttttttzzttmmmmbbbbb........",  # 32 (cell row 40)
    "............nnnnnnnnnnnnnttttttttttzzttmmmmbbbbb........",  # 33 (cell row 41)
    "............nnnnnnnnnnnnnttttttttttzzttmmmmbbbbb........",  # 34 (cell row 42)
    "............nnnnnnnnnnzttttttttttttzzttmmmmmbbbb........",  # 35 (cell row 43)
    "............nnnnnnnnnnztttttttttttttzztmmmmmbbbb........",  # 36 (cell row 44)
    "............nnnnnnnnnzztttttttttttttzztmmmmmbbbb........",  # 37 (cell row 45)
    "............nnnnnnnnnzztttttttttttttzztmmmmmbbbb........",  # 38 (cell row 46)
    "............nnnnnnnntzztttttttttttttzztmmmmmbbbb........",  # 39 (cell row 47)
    ".............nnnnnnttzztttttttttttttzztmmmmmbbbb........",  # 40 (cell row 48)
    "..............nnnntttzztttttttttttttzztmmmmmbbbb........",  # 41 (cell row 49)
    "..................tttzztttttttttttttzzmmmmmmbbbb........",  # 42 (cell row 50)
    "..................tttzztttttttttttttzzmmmmmbbbbb........",  # 43 (cell row 51)
    "..................tttzztttttttttttttzzmmmmmbbbbb........",  # 44 (cell row 52)
    ".................attttttttttttttttttttmmmmmbbbb.........",  # 45 (cell row 53)
    "................aaattttttttttttttttttttmmmmmbb..........",  # 46 (cell row 54)
    "................aaatttttttttttttttttttmmmmmmm...........",  # 47 (cell row 55)
    "................aaatttttttttttttttttttmmmmmmm...........",  # 48 (cell row 56)
    "................aaattttttllllllttttttcmmmmmmm...........",  # 49 (cell row 57)
    "................aaattttttllllllttttttcmmmmmmm...........",  # 50 (cell row 58)
    "...............aaaattttttllllllttttttccmmmmmm...........",  # 51 (cell row 59)
    "...............aaaattttttlllcllttttttcccmmmm............",  # 52 (cell row 60)
    "...............aaaatttttllllcllltttttccc................",  # 53 (cell row 61)
    "...............aaaaatttlllllclllltttccccc...............",  # 54 (cell row 62)
    "...............aaaacclllllllcllllllcccccc...............",  # 55 (cell row 63)
    "..............aaaaacllllllllcllllllcccccc...............",  # 56 (cell row 64)
    "..............aaaaacllllllllcllllllcccccc...............",  # 57 (cell row 65)
    "..............aaaaaclllllllccllllllccccccc..............",  # 58 (cell row 66)
    ".............aaaaaaclllllllllllllllccccccc..............",  # 59 (cell row 67)
    ".............aaaaaclllllllll.llllllccccccc..............",  # 60 (cell row 68)
    ".............aaaaacllllllll..llllllccccccc..............",  # 61 (cell row 69)
    "............aaaaaacllllllll..lllllllccccccc.............",  # 62 (cell row 70)
    "............aaaaaacllllllll..lllllllccccccc.............",  # 63 (cell row 71)
    "............aaaaaclllllllll..lllllllccccccc.............",  # 64 (cell row 72)
    "............aaaaacllllllll...lllllllccccccc.............",  # 65 (cell row 73)
    "............aaaaacllllllll...lllllllcccccccc............",  # 66 (cell row 74)
    "...........aaaaaccllllllll...lllllllcccccccc............",  # 67 (cell row 75)
    "...........aaaaacllllllll.....llllllcccccccc............",  # 68 (cell row 76)
    "...........aaaaacllllllll.....llllllcccccccc............",  # 69 (cell row 77)
    "..........ccaaaacllllllll.....llllllccccccccc...........",  # 70 (cell row 78)
    "..........cccccccllllllll.....llllllccccccccc...........",  # 71 (cell row 79)
    "..........cccccccllllllll.....lllllllcccccccc...........",  # 72 (cell row 80)
    "...........ccccccllllllll.....lllllllccccccc............",  # 73 (cell row 81)
    "............ccclllllllll......llllllllccccc.............",  # 74 (cell row 82)
    "...............lllllllll......llllllll..................",  # 75 (cell row 83)
    "...............lllllllll......llllllll..................",  # 76 (cell row 84)
    "...............ollllllll......lllllllooo................",  # 77 (cell row 85)
    "..............oooooooooo......ooooooooooo...............",  # 78 (cell row 86)
    "..............oooooooooo......ooooooooooo...............",  # 79 (cell row 87)
    "..............oooooooooo......ooooooooooo...............",  # 80 (cell row 88)
    "...............oooooooo........ooooooooo................",  # 81 (cell row 89)
    "...............oooooooo........ooooooooo................",  # 82 (cell row 90)
    "...............oooooooo........ooooooooo................",  # 83 (cell row 91)
    "...............oooooooo........ooooooooo................",  # 84 (cell row 92)
    "...............oooooooo........ooooooooo................",  # 85 (cell row 93)
    "...............oooooooo........ooooooooo................",  # 86 (cell row 94)
    "..............ooooooooo........ooooooooo................",  # 87 (cell row 95)
    ".............oooooooooo........ooooooooo................",  # 88 (cell row 96)
    "............ooooooooooo........oooooooooo...............",  # 89 (cell row 97)
    "...........oooooooooooo........ooooooooooo..............",  # 90 (cell row 98)
    "...........oooooooooooo........oooooooooooo.............",  # 91 (cell row 99)
    "...........oooooooooooo........ooooooooooooo............",  # 92 (cell row 100)
    "............oooooooooo.........ooooooooooooo............",  # 93 (cell row 101)
    "...............................ooooooooooooo............",  # 94 (cell row 102)
    "................................ooooooooooo.............",  # 95 (cell row 103)
]


def fid(role):
    return hashlib.sha256(f"{RUN_ID}:{role}".encode()).hexdigest()[:8]


NAMES = {
    "png": f"{SLUG}_{VISUAL_ID}_{SUBJECT}_{VARIANT}_{STAMP}-{fid('png')}.png",
    "pxo": f"{SLUG}_{VISUAL_ID}_{SUBJECT}-editable_{VARIANT}_{STAMP}-{fid('pxo')}.pxo",
    "ora": f"{SLUG}_{VISUAL_ID}_{SUBJECT}-layers_{VARIANT}_{STAMP}-{fid('ora')}.ora",
    "palette": f"{SLUG}_{VISUAL_ID}_{SUBJECT}-palette_{VARIANT}_{STAMP}-{fid('palette')}.json",
    "manifest": f"{SLUG}_{VISUAL_ID}_{SUBJECT}-manifest_{VARIANT}_{STAMP}-{fid('manifest')}.json",
}
TOOL_REL = "tools/" + os.path.basename(os.path.abspath(__file__))

# ============================================================================ paths / hashes
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


def text_sha256_lf(data):
    """sha256-text-lf-v1: SHA-256 after CRLF -> LF, nothing else normalized."""
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def ref_hash(rel, kind):
    data = read_bytes(repo_path(rel))
    return (sha256_bytes(data), "sha256-bytes") if kind == "bytes" else (text_sha256_lf(data), "sha256-text-lf-v1")


# ============================================================================ composition
def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def validate_maps():
    if len(MAP) != GRID_H or len(ROLE) != GRID_H:
        raise SystemExit("MAP/ROLE must have 96 rows")
    keys = {k for _, k in ROLE_LAYERS}
    for y, (m, r) in enumerate(zip(MAP, ROLE)):
        if len(m) != GRID_W or len(r) != GRID_W:
            raise SystemExit(f"row {y}: MAP/ROLE rows must be {GRID_W} wide")
        for x, (mk, rk) in enumerate(zip(m, r)):
            if (mk == ".") != (rk == "."):
                raise SystemExit(f"MAP/ROLE opacity differs at grid ({x},{y})")
            if mk != "." and mk not in PAL:
                raise SystemExit(f"undeclared colour key {mk!r} at grid ({x},{y})")
            if rk != "." and rk not in keys:
                raise SystemExit(f"unknown role key {rk!r} at grid ({x},{y})")


def compose(role_key=None):
    """RGBA cell; with role_key, only that role's texels."""
    a = np.zeros((H, W, 4), np.uint8)
    ox, oy = GRID_OFFSET
    for y in range(GRID_H):
        for x in range(GRID_W):
            k = MAP[y][x]
            if k == "." or (role_key is not None and ROLE[y][x] != role_key):
                continue
            a[oy + y, ox + x, :3] = hex_rgb(PAL[k])
            a[oy + y, ox + x, 3] = 255
    return a


def guides_rgba(full):
    g = np.zeros((H, W, 4), np.uint8)
    pts = set()
    pts.update((x, 0) for x in range(W)); pts.update((x, H - 1) for x in range(W))
    pts.update((0, y) for y in range(H)); pts.update((W - 1, y) for y in range(H))
    for y in TEMPLATE_ROWS.values():
        pts.update((x, y) for x in list(range(1, 4)) + list(range(W - 4, W - 1)))
    pts.add(PIN)
    for x, y in pts:
        g[y, x, :3] = GUIDE_RGB
        g[y, x, 3] = 255
    if (full[..., 3][g[..., 3] > 0] != 0).any():
        raise SystemExit("a guide texel overlaps an opaque sprite texel")
    return g


def png_bytes(a):
    buf = io.BytesIO()
    Image.fromarray(a, "RGBA").save(buf, "PNG", optimize=False, compress_level=9)
    return buf.getvalue()


def make_pxo(blobs, preview_png):
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": n == "guides", "metadata": {}, "name": n,
                   "new_cels_linked": False, "opacity": 1.0, "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": n != "guides"} for n in LAYERS]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0}
                             for _ in LAYERS], "duration": 1.0, "metadata": {}}]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": json.dumps("protagonist-male-south-idle-v8pair-v01"),
                      "frame_current_tag": "0", "include_tag_in_filename": "false", "interpolation": "0",
                      "lines_count": "1", "new_dir_for_each_frame_tag": "false", "number_of_digits": "4",
                      "number_of_frames": "1", "orientation": "0", "repeat_count": "0", "resize": "100",
                      "save_quality": "0.75", "separator_character": "\"_\"",
                      "sheet_layers_as_separate_files": "false", "split_layers": "false"}
    palette = {"name": "protagonist-male-south-v8pair-v01", "comment": "declared ramps", "width": 8, "height": 5,
               "colors": {str(i): {"color": "(%s, %s, %s, 1.0)" % tuple(round(c / 255, 6) for c in hex_rgb(v)), "index": i}
                          for i, v in enumerate(PAL.values())}}
    data = {"author_company": "", "author_contact": "", "author_display_name": "", "author_real_name": "",
            "brushes": [], "color_mode": 5, "current_frame": 0, "current_layer": len(LAYERS) - 2,
            "export_profile": export_profile, "fps": 6.0, "frames": frames_json, "guides": [], "layers": layer_json,
            "license": "", "metadata": {}, "next_keyframe_id": 0, "palettes": [],
            "pixelorama_version": PIXELORAMA_VERSION, "project_current_palette_name": "", "pxo_version": 7,
            "reference_images": [], "size_x": W, "size_y": H, "symmetry_points": [W - 1.0, H - 1.0], "tags": [],
            "tile_mode_x_basis_x": W, "tile_mode_x_basis_y": 0, "tile_mode_y_basis_x": 0, "tile_mode_y_basis_y": H,
            "tilesets": [], "user_data": json.dumps({"declared_palette": palette}), "vanishing_points": []}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        def put(name, payload):
            z.writestr(zipfile.ZipInfo(name, ZIP_DT), payload, zipfile.ZIP_DEFLATED)
        put("data.json", json.dumps(data, separators=(",", ":")))
        put("mimetype", "application/x-pixelorama")
        put("preview.png", preview_png)
        put("image_data/frames/1/", b"")
        for li, name in enumerate(LAYERS, start=1):
            put(f"image_data/frames/1/layer_{li}", blobs[name].tobytes())
            put(f"image_data/frames/1/indices_layer_{li}", b"\x00")
    return buf.getvalue()


def make_ora(blobs, png):
    stack = ['<?xml version="1.0" encoding="UTF-8"?>',
             f'<image version="0.0.3" w="{W}" h="{H}" xres="72" yres="72">', "<stack>"]
    for name in reversed(LAYERS):                          # ORA lists the top layer first
        vis = "hidden" if name == "guides" else "visible"
        stack.append(f'<layer name="{name}" src="data/{name}.png" x="0" y="0" opacity="1.0" '
                     f'visibility="{vis}" composite-op="svg:src-over"/>')
    stack += ["</stack>", "</image>"]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", ZIP_DT), "image/openraster", zipfile.ZIP_STORED)
        z.writestr(zipfile.ZipInfo("stack.xml", ZIP_DT), "\n".join(stack) + "\n", zipfile.ZIP_DEFLATED)
        for name in LAYERS:
            z.writestr(zipfile.ZipInfo(f"data/{name}.png", ZIP_DT), png_bytes(blobs[name]), zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("mergedimage.png", ZIP_DT), png, zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("Thumbnails/thumbnail.png", ZIP_DT), png, zipfile.ZIP_DEFLATED)
    return buf.getvalue()


def decode(png):
    return np.array(Image.open(io.BytesIO(png)).convert("RGBA"))


def read_ora_layers(ora):
    """Parse an .ora: layer RGBA by name (stack order top-first), hidden layer names, merged image."""
    import xml.etree.ElementTree as ET
    with zipfile.ZipFile(io.BytesIO(ora)) as z:
        root = ET.fromstring(z.read("stack.xml"))
        layers, hidden = [], []
        for el in root.iter("layer"):
            arr = decode(z.read(el.get("src")))
            layers.append((el.get("name"), arr, el.get("visibility", "visible")))
            if el.get("visibility") == "hidden":
                hidden.append(el.get("name"))
        merged = decode(z.read("mergedimage.png"))
        mimetype_first = z.infolist()[0].filename == "mimetype" and z.infolist()[0].compress_type == zipfile.ZIP_STORED
    return layers, hidden, merged, mimetype_first


def recompose(layers_bottom_up):
    comp = np.zeros((H, W, 4), np.uint8)
    for _, a in layers_bottom_up:
        m = a[..., 3] == 255
        comp[m] = a[m]
    return comp


# ============================================================================ gates and metrics
def lab(rgb):
    c = []
    for v in rgb:
        v = v / 255.0
        c.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    x = (0.4124 * c[0] + 0.3576 * c[1] + 0.1805 * c[2]) / 0.95047
    y = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    z = (0.0193 * c[0] + 0.1192 * c[1] + 0.9505 * c[2]) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return (116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z)))


def de76(a, b):
    return sum((p - q) ** 2 for p, q in zip(lab(a), lab(b))) ** 0.5


P4_EXEMPT = ("outline", "eye")        # outline and the single eye colour are not lit ramps


def v8_rgba():
    p = repo_path(V8_PNG)
    if os.path.isfile(_fs(p)) and sha256_bytes(read_bytes(p)) == V8_LOCKS[V8_PNG][0]:
        return decode(read_bytes(p))
    return None


def isolated_texels(full):
    """Opaque texels whose colour differs from all 8 neighbours (single-texel speckle; noise proxy)."""
    rgb = full[..., :3].astype(int); op = full[..., 3] > 0
    n = 0
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not op[y, x]:
                continue
            same = False
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if (dx or dy) and op[y + dy, x + dx] and (rgb[y + dy, x + dx] == rgb[y, x]).all():
                        same = True
            n += 0 if same else 1
    return n


def gates(full):
    alpha = full[..., 3]
    opaque = alpha > 0
    ys, xs = np.nonzero(opaque)
    colours = {tuple(int(c) for c in px) for px in full[opaque][:, :3]}
    declared = {hex_rgb(v) for v in PAL.values()}
    border = np.zeros_like(opaque); border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
    ramp_steps = {}
    for name, ramp in RAMPS.items():
        if name in P4_EXEMPT:
            continue
        ls = sorted((lab(hex_rgb(v))[0] for v in ramp.values()), reverse=True)
        ramp_steps[name] = [round(a - b, 2) for a, b in zip(ls, ls[1:])]
    v8_ramps = {"coat": ["5e6e8c", "3a4560", "222839"], "trousers": ["4a625c", "324542"]}
    v8_steps = []
    for r in v8_ramps.values():
        ls = sorted((lab(hex_rgb(v))[0] for v in r), reverse=True)
        v8_steps += [a - b for a, b in zip(ls, ls[1:])]
    all_steps = [s for v in ramp_steps.values() for s in v]
    body_h = int(ys.max() - ys.min() + 1)
    sole = int(ys.max())
    feet = xs[ys == sole]
    v8 = v8_rgba()
    bench = {}
    if v8 is not None:
        va = v8[..., 3] > 0
        vys, vxs = np.nonzero(va)
        bench = {"v8_visible_size": [int(vxs.max() - vxs.min() + 1), int(vys.max() - vys.min() + 1)],
                 "v8_body_rows": [int(vys.min()), int(vys.max())],
                 "v8_opaque_texels": int(va.sum()), "v8_colours": len({tuple(int(c) for c in px) for px in v8[va][:, :3]}),
                 "v8_isolated_single_texels": isolated_texels(v8)}
    return {
        "P1_binary_alpha": bool(set(np.unique(alpha).tolist()) <= {0, 255}),
        "P1_no_opaque_on_border": not bool((opaque & border).any()),
        "P2_colour_count": len(colours), "P2_cap": 48, "P2_pass": len(colours) <= 48,
        "P3_all_colours_declared": colours <= declared,
        "P3_declared_unused": sorted("#" + "%02x%02x%02x" % c for c in declared - colours),
        "P4_ramp_adjacent_Lstar_steps": ramp_steps, "P4_exempt": list(P4_EXEMPT), "P4_min_step": round(min(all_steps), 2),
        "P4_v8_reference_min_step": round(min(v8_steps), 2),
        "P4_pass_report_only": min(all_steps) >= min(v8_steps),
        "S1_body_height_texels": body_h, "S1_display_height_logical_px": body_h * DISPLAY_SCALE,
        "S1_pass": body_h == 96 and sole == PIN[1] - 1 and int(ys.min()) == BODY_ROWS[0],
        "S1_alpha_bounds_inclusive": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
        "S1_sole_row": sole, "S1_pin": list(PIN), "S1_sole_span_x": [int(feet.min()), int(feet.max())],
        "S1_pin_inside_feet_span": bool(int(xs[ys >= sole - 12].min()) <= PIN[0] <= int(xs[ys >= sole - 12].max())),
        "opaque_texels": int(opaque.sum()),
        "visible_size": [int(xs.max() - xs.min() + 1), body_h],
        "isolated_single_texels": isolated_texels(full),
        "benchmark_v8": bench,
    }


def legibility():
    """Report-only identity metrics at 1 texel = 1 screen px (grid rows; cell row = grid row + 8)."""
    ox, oy = GRID_OFFSET
    def span(y, keys=None, roles=None):
        xs_ = [x for x in range(GRID_W) if MAP[y][x] != "." and (keys is None or MAP[y][x] in keys)
               and (roles is None or ROLE[y][x] in roles)]
        return (min(xs_), max(xs_)) if xs_ else None
    hair_rows = [y for y in range(GRID_H) if any(ROLE[y][x] == "h" for x in range(GRID_W))]
    face_rows = [y for y in range(GRID_H) if any(MAP[y][x] in "Ff" and ROLE[y][x] == "f" for x in range(GRID_W))]
    hair_w = max(span(y, roles="h")[1] - span(y, roles="h")[0] + 1 for y in hair_rows)
    face_w = max(span(y, keys="Ff", roles="f")[1] - span(y, keys="Ff", roles="f")[0] + 1 for y in face_rows)
    top = []
    for x in range(GRID_W):
        ys_ = [y for y in range(GRID_H) if ROLE[y][x] == "h" and MAP[y][x] != "K"]
        top.append(min(ys_) if ys_ else None)
    peaks = []
    for x in range(1, GRID_W - 1):
        if top[x] is None:
            continue
        l = top[x - 1] if top[x - 1] is not None else 99
        r = top[x + 1] if top[x + 1] is not None else 99
        if top[x] < l and top[x] <= r and top[x] <= 6:
            peaks.append([x + ox, top[x] + oy])
    def contacts(ra, rb):
        n = 0
        for y in range(GRID_H):
            for x in range(GRID_W):
                if ROLE[y][x] != ra:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < GRID_W and 0 <= yy < GRID_H and ROLE[yy][xx] == rb:
                        n += 1
        return n
    def count(keys, roles=None):
        return sum(1 for y in range(GRID_H) for x in range(GRID_W) if MAP[y][x] in keys and (roles is None or ROLE[y][x] in roles))
    def mean_l(keys, roles):
        pts = [hex_rgb(PAL[MAP[y][x]]) for y in range(GRID_H) for x in range(GRID_W) if MAP[y][x] in keys and ROLE[y][x] in roles]
        return round(sum(lab(p)[0] for p in pts) / len(pts), 1)
    shoulder = span(36 - oy)
    return {
        "hair_max_width_px": hair_w, "face_max_width_px": face_w, "hair_wider_than_face_px": hair_w - face_w,
        "hair_crown_points_cell_xy": peaks, "hair_crown_point_count": len(peaks),
        "head_rows_cell": [min(hair_rows) + oy, max(face_rows) + oy],
        "shoulder_span_cell_x_row36": [shoulder[0] + ox, shoulder[1] + ox],
        "scarf_texels": count("SsZ", "s"), "bedroll_texels": count("TtuU", "r"), "sash_texels": count("SsZ", "a"),
        "teal_total_texels": count("SsZTtu"), "pack_texels": count("LlmMX", "b"),
        "scarf_bedroll_4_neighbour_contacts": contacts("s", "r"),
        "mean_Lstar": {"hair": mean_l("1234", "h"), "scarf": mean_l("SsZ", "s"), "coat": mean_l("ABCc", "tcnm"),
                       "bedroll": mean_l("Ttu", "r"), "shirt": mean_l("Wwv", "t"), "trousers": mean_l("Ppo", "l"),
                       "boots": mean_l("Obq", "o"), "skin": mean_l("FfeD", "f")},
        "scarf_s_vs_coat_B_dE76": round(de76(hex_rgb(PAL["s"]), hex_rgb(PAL["B"])), 1),
        "scarf_s_vs_bedroll_t_dE76": round(de76(hex_rgb(PAL["s"]), hex_rgb(PAL["t"])), 1),
        "hair_3_vs_skin_F_dE76": round(de76(hex_rgb(PAL["3"]), hex_rgb(PAL["F"])), 1),
    }


# ============================================================================ build
def artifacts():
    validate_maps()
    full = compose()
    union = np.zeros_like(full)
    blobs = {}
    for name, k in ROLE_LAYERS:
        part = compose(k)
        if ((union[..., 3] > 0) & (part[..., 3] > 0)).any():
            raise SystemExit("role layers overlap")
        union[part[..., 3] > 0] = part[part[..., 3] > 0]
        blobs[name] = part
    if union.tobytes() != full.tobytes():
        raise SystemExit("role layers do not reassemble the full sprite")
    blobs["guides"] = guides_rgba(full)
    png = png_bytes(full)
    pxo = make_pxo(blobs, png)
    ora = make_ora(blobs, png)
    return full, png, pxo, ora, blobs


def palette_json():
    p = {"project": "Worlds Between", "visual_id": VISUAL_ID, "purpose": "declared named ramps for the male "
         "protagonist south idle static pilot paired to female selout v8 (v01)", "art_approved": False,
         "ramps": {name: [{"key": k, "hex": "#" + v} for k, v in ramp.items()] for name, ramp in RAMPS.items()},
         "light": "upper left", "colour_count": len(PAL)}
    return (json.dumps(p, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def manifest_json(png, pxo, ora, pal, full):
    refs = {}
    for k, (rel, kind) in REFS.items():
        h, alg = ref_hash(rel, kind)
        refs[k] = {"file": rel, "sha256": h, "hash_algorithm": alg}
    layers = []
    for i, (n, k) in enumerate(ROLE_LAYERS, start=1):
        layers.append({"pixelorama_layer": i, "name": n, "visible": True, "locked": False,
                       "texels": int((compose(k)[..., 3] > 0).sum()), "note": LAYER_NOTES[n]})
    layers.append({"pixelorama_layer": len(LAYERS), "name": "guides", "visible": False, "locked": True,
                   "note": LAYER_NOTES["guides"]})
    m = {
        "project": "Worlds Between", "milestone": "M8", "visual_id": VISUAL_ID, "identity": "male protagonist (player-selectable hero)",
        "purpose": "South-facing exploration idle STATIC frame for the male protagonist at the approved 48 logical px, "
                   "authored fresh as clean hand-placed clusters paired to the approved female selout v8 rendering "
                   "density; editable Pixelorama role layers.",
        "status": "UNAPPROVED, NONRUNTIME pilot; technical gates only; not runtime-integrated; no animation; south only",
        "art_approved": False, "human_reviewed": False, "runtime_integrated": False, "variant": VARIANT, "run_id": RUN_ID,
        "acceptance_counters_unchanged": {"runtime_sprites_accepted": "0/52", "scene_visual_gates": "3/12",
                                          "overall_meter": "40.8%", "plays": "0/2"},
        "authorship": "Colour and role grids placed part by part by Claude (Claude Code, signed-in Claude Max, claude.ai "
                      "firstParty, no API key) as hand-chosen spans, polygons, strokes and small stamps, then frozen as "
                      "the literal grids in the tool. No image generation, no sampling of the concept sheet, no "
                      "resampling, filtering, quantization or dithering; no v8 texel or palette entry copied.",
        "not_used_as_base": ["rejected 32x48 male south frame (a01be730)", "local unapproved male high-density v01/v02 pilots"],
        "benchmark": {"female_selout_v8": "density/proportion/light benchmark only (same 80x112 cell, pin, 96-texel body, "
                      "0.5 scale, 1-texel near-black outline, upper-left light, 3-4 step material ramps); v8 files are "
                      "hash-locked and never written."},
        "identity_anchors_from_sheet": {
            "hair": "tousled dark-brown short hair with uneven outward tufts, wider than the face, fringe over the forehead (not a rounded cap, not a ponytail)",
            "face": "young adult male, thick straight brows, dark eyes, small closed smile, face turned slightly to the viewer-left",
            "scarf": "tea-green scarf wrapped at the neck with a short front point",
            "coat": "open warm grey-brown field coat to the knee with popped collar, leather piping and rolled sleeves showing cream cuffs and forearms",
            "pack_bedroll": "teal bedroll with a spiral end on top of a brown leather pack behind the viewer-right shoulder; harness straps on the chest",
            "other": "cream laced shirt, teal community-diamond emblem, belt with steel buckle, teal sash at the viewer-left hip, fingerless gloves, olive-grey trousers with a knee pad and cargo pocket, tall cuffed brown boots",
            "pose": "relaxed idle: viewer-left hand gripping the pack strap at the chest (as in the sheet), viewer-right arm hanging, weight on the viewer-right leg, relaxed leg angled out with the foot set back",
        },
        "cell": {"w": W, "h": H, "pin": list(PIN), "body_rows": list(BODY_ROWS), "display_scale": DISPLAY_SCALE,
                 "display_logical_height": 48, "filter": "nearest", "alpha": "binary", "grid_offset": list(GRID_OFFSET),
                 "template_rows_from_v8": TEMPLATE_ROWS},
        "files": {
            "png": {"file": f"{OUT_DIR_REL}/{NAMES['png']}", "sha256": sha256_bytes(png), "hash_algorithm": "sha256-bytes",
                    "role": "transparent runtime-CANDIDATE PNG (not wired into the game)"},
            "pxo": {"file": f"{OUT_DIR_REL}/{NAMES['pxo']}", "sha256": sha256_bytes(pxo), "hash_algorithm": "sha256-bytes",
                    "format": f"Pixelorama pxo_version 7 ({PIXELORAMA_VERSION}), color_mode 5, 1 frame x {len(LAYERS)} layers, fixed zip timestamps"},
            "ora": {"file": f"{OUT_DIR_REL}/{NAMES['ora']}", "sha256": sha256_bytes(ora), "hash_algorithm": "sha256-bytes",
                    "format": "OpenRaster 0.0.3, same layers as the .pxo (guides hidden), mergedimage = the PNG"},
            "palette": {"file": f"{OUT_DIR_REL}/{NAMES['palette']}", "sha256": text_sha256_lf(pal), "hash_algorithm": "sha256-text-lf-v1"},
            "gdignore": f"{OUT_DIR_REL}/.gdignore",
        },
        "layers_bottom_to_top": layers,
        "references": refs,
        "female_v8_source_locks": {rel: {"sha256": h, "hash_algorithm": "sha256-bytes" if k == "bytes" else "sha256-text-lf-v1"}
                                   for rel, (h, k) in V8_LOCKS.items()},
        "gates": gates(full),
        "legibility_metrics_report_only": legibility(),
        "pending_visual_decisions": [
            "Does the hair read as the sheet's tousled outward-pointing short hair at 1x, or as a crown of three spikes?",
            "Is the hand on the pack strap legible at 1x, or does it read as a dark knot on the chest?",
            "Is the warm grey-brown coat separated enough from the warm annex floor (it relies on the outline and the lit left plane)?",
            "Is the shirt opening too bright / too large compared with v8's chest?",
        ],
        "tool": {"file": TOOL_REL, "sha256": text_sha256_lf(read_bytes(os.path.abspath(__file__))),
                 "hash_algorithm": "sha256-text-lf-v1", "python": sys.version.split()[0], "pillow": Image.__version__,
                 "numpy": np.__version__, "run_flags": "-I -B"},
    }
    return (json.dumps(m, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write_new(path, data, text=False):
    if os.path.exists(_fs(path)):
        old = read_bytes(path)
        same = text_sha256_lf(old) == text_sha256_lf(data) if text else old == data
        if not same:
            raise SystemExit(f"refusing to overwrite a different existing file: {path}")
        return "unchanged"
    with open(_fs(path), "xb") as f:
        f.write(data)
    return "written"


HARD = ["P1_binary_alpha", "P1_no_opaque_on_border", "P2_pass", "P3_all_colours_declared", "S1_pass", "S1_pin_inside_feet_span"]


def v8_unchanged():
    return {rel.rsplit("/", 1)[-1]: ref_hash(rel, kind)[0] == h for rel, (h, kind) in V8_LOCKS.items()}


def build():
    if not all(v8_unchanged().values()):
        raise SystemExit("female v8 source files differ from their locks; refusing to build")
    full, png, pxo, ora, _ = artifacts()
    full2, png2, pxo2, ora2, _ = artifacts()
    if png != png2 or pxo != pxo2 or ora != ora2:
        raise SystemExit("build is not deterministic")
    g = gates(full)
    bad = [k for k in HARD if not g[k]]
    if bad:
        raise SystemExit(f"hard gates failed: {bad}")
    out = repo_path(OUT_DIR_REL)
    os.makedirs(_fs(out), exist_ok=True)
    print(write_new(os.path.join(out, ".gdignore"), b""), ".gdignore")
    pal = palette_json()
    for key, data in (("png", png), ("pxo", pxo), ("ora", ora)):
        print(write_new(os.path.join(out, NAMES[key]), data), NAMES[key], sha256_bytes(data))
    print(write_new(os.path.join(out, NAMES["palette"]), pal, text=True), NAMES["palette"])
    man = manifest_json(png, pxo, ora, pal, full)
    print(write_new(os.path.join(out, NAMES["manifest"]), man, text=True), NAMES["manifest"], text_sha256_lf(man), "(sha256-text-lf-v1)")


# ============================================================================ check
GUI_OWNED = (".running", "backups/")    # an open GUI's heartbeat and ~62 s autosaves; not written by our runs


def real_pixelorama_snapshot():
    root = os.path.join(os.environ.get("APPDATA", ""), "pixelorama")
    snap = {}
    if os.path.isdir(root):
        for d, _, files in os.walk(root):
            for f in files:
                p = os.path.join(d, f)
                rel = os.path.relpath(p, root).replace("\\", "/")
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
        shutil.rmtree(_fs(env["APPDATA"]), ignore_errors=True)
    files = sorted(f for f in os.listdir(_fs(out_dir)) if f.lower().endswith(".png"))
    return p.returncode, {f: read_bytes(os.path.join(out_dir, f)) for f in files}


def check(exe):
    full, png, pxo, ora, blobs = artifacts()
    out = repo_path(OUT_DIR_REL)
    disk = {k: read_bytes(os.path.join(out, NAMES[k])) for k in ("png", "pxo", "ora", "palette", "manifest")}
    man = json.loads(disk["manifest"])
    rep = {"files_equal_rebuild": {"png": disk["png"] == png, "pxo": disk["pxo"] == pxo, "ora": disk["ora"] == ora,
                                   "palette": text_sha256_lf(disk["palette"]) == text_sha256_lf(palette_json()),
                                   "manifest": text_sha256_lf(disk["manifest"]) == text_sha256_lf(manifest_json(png, pxo, ora, palette_json(), full))},
           "manifest_hashes_match": all(man["files"][k]["sha256"] == sha256_bytes(disk[k]) for k in ("png", "pxo", "ora")),
           "manifest_reference_hashes_current": {k: ref_hash(v["file"], "bytes" if v["hash_algorithm"] == "sha256-bytes" else "text")[0] == v["sha256"]
                                                 for k, v in man["references"].items()},
           "png_decodes_to_maps": decode(disk["png"]).tobytes() == full.tobytes(),
           "gates": gates(full), "legibility": legibility(), "pixelorama": {},
           "female_v8_source_unchanged": v8_unchanged()}
    layers, hidden, merged, mt = read_ora_layers(disk["ora"])
    bottom_up = [(n, a) for n, a, vis in reversed(layers) if vis != "hidden"]
    rep["ora_structure"] = {"mimetype_first_and_stored": mt, "hidden_layers": hidden,
                            "layer_names_bottom_up": [n for n, _ in bottom_up],
                            "visible_layers_recompose_to_png": recompose(bottom_up).tobytes() == full.tobytes(),
                            "each_layer_equals_role_blob": all(a.tobytes() == blobs[n].tobytes() for n, a in bottom_up),
                            "mergedimage_equals_png": merged.tobytes() == full.tobytes()}
    snap0 = real_pixelorama_snapshot()
    tmp = tempfile.mkdtemp(prefix="wb-malev8pair-")
    try:
        for kind in ("pxo", "ora"):
            src = os.path.join(tmp, f"cand.{kind}")
            with open(_fs(src), "wb") as f:
                f.write(disk[kind])
            flats = []
            for run, split in ((1, False), (2, False), (3, True)):
                od = os.path.join(tmp, f"{kind}-{run}")
                os.makedirs(_fs(od))
                rc, outs = pixelorama_export(exe, src, od, split)
                arrs = {f: decode(b) for f, b in outs.items()}
                if split:
                    want = {n: blobs[n].tobytes() for n, _ in ROLE_LAYERS}
                    matched = sorted(n for n, b in want.items() if any(o.tobytes() == b for o in arrs.values()))
                    guide_leak = any(o.tobytes() == blobs["guides"].tobytes() for o in arrs.values())
                    r = {"mode": "split-layers", "exit": rc, "pngs": len(outs), "visible_layers_matched": len(matched),
                         "visible_layers": len(want), "guides_exported": guide_leak,
                         "pass": rc == 0 and len(matched) == len(want) and len(outs) == len(want) and not guide_leak}
                else:
                    ok = rc == 0 and len(outs) == 1 and next(iter(arrs.values())).tobytes() == full.tobytes()
                    r = {"mode": "flattened", "run": run, "exit": rc, "pngs": len(outs), "rgba_equals_png": ok, "pass": ok}
                    if len(outs) == 1:
                        flats.append(next(iter(outs.values())))
                rep["pixelorama"][f"{kind}_{run}"] = r
            rep["pixelorama"][f"{kind}_flat_runs_byte_identical"] = len(flats) == 2 and flats[0] == flats[1]
            with open(_fs(src), "rb") as f:
                rep["pixelorama"][f"{kind}_input_unchanged_by_cli"] = f.read() == disk[kind]
    finally:
        shutil.rmtree(_fs(tmp), ignore_errors=True)
    snap1 = real_pixelorama_snapshot()
    changed = sorted(k for k in set(snap0) | set(snap1) if snap0.get(k) != snap1.get(k))
    rep["real_appdata_pixelorama_changed"] = {"ours": [k for k in changed if not k.startswith(GUI_OWNED)],
                                              "gui_owned_heartbeat_or_autosave": [k for k in changed if k.startswith(GUI_OWNED)]}
    g = rep["gates"]; px = rep["pixelorama"]; o = rep["ora_structure"]
    ok = (all(rep["files_equal_rebuild"].values()) and rep["manifest_hashes_match"] and all(rep["female_v8_source_unchanged"].values())
          and all(rep["manifest_reference_hashes_current"].values()) and rep["png_decodes_to_maps"]
          and all(g[k] for k in HARD)
          and o["mimetype_first_and_stored"] and o["hidden_layers"] == ["guides"] and o["visible_layers_recompose_to_png"]
          and o["each_layer_equals_role_blob"] and o["mergedimage_equals_png"]
          and all(v["pass"] for k, v in px.items() if isinstance(v, dict))
          and px["pxo_flat_runs_byte_identical"] and px["ora_flat_runs_byte_identical"]
          and px["pxo_input_unchanged_by_cli"] and px["ora_input_unchanged_by_cli"]
          and not rep["real_appdata_pixelorama_changed"]["ours"])
    rep["result"] = "PASS" if ok else "FAIL"
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    return 0 if ok else 1


def preview(path):
    full = artifacts()[0]
    Image.fromarray(full, "RGBA").resize((W * 4, H * 4), Image.NEAREST).save(_fs(path))
    print(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=["build", "check", "preview"])
    ap.add_argument("out", nargs="?")
    ap.add_argument("--pixelorama")
    a = ap.parse_args()
    if a.mode == "build":
        build(); return 0
    if a.mode == "preview":
        if not a.out:
            raise SystemExit("preview needs an output path")
        preview(a.out); return 0
    if not a.pixelorama or not os.path.isfile(a.pixelorama):
        raise SystemExit(f"Pixelorama 1.2.3 executable needed via --pixelorama (got {a.pixelorama!r})")
    return check(os.path.abspath(a.pixelorama))


if __name__ == "__main__":
    sys.exit(main())
