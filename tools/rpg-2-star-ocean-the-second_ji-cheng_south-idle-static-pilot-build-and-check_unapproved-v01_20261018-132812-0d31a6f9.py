"""Ji Cheng (纪澄) south-facing EXPLORATION IDLE static pilot at the approved female selout v8 density (UNAPPROVED):
one hand-placed 80x112 cell (96-texel body -> 48 logical px at 0.5), editable Pixelorama .pxo + layered .ora with
13 role layers + hidden guides, declared palette, manifest and deterministic technical gates.

Scope: one direction (south), one static idle frame, Ji Cheng only. No animation, no other direction, no runtime
integration, no approval or counter change (runtime sprites stay 0/52, scene visuals 3/12, meter 40.8%, plays 0/2).
Identity source: Ji Cheng's character sheet (registry approval "concept"; front, back, three head studies, chibi
turnaround, magnifier close-up) and the registry anchor "quiet old-records restorer ... shaved short behind the ear,
shoulder-length straight silver-black hair on top; ink-green jacket and folding magnifier". She is a 28-year-old
woman. Read from the sheet: her LEFT temple (viewer-right in a south view) is shaved with razor lines, a rectangular
drop earring on that ear; the black bob is swept from a side part across the forehead toward the viewer-left and
falls to the shoulder there, ending in silver-white tips; a shorter silver-tipped lock hangs behind the shaved side;
dark forest-green long coat, open, with an uneven pointed hem, grey rolled sleeve linings, worn brass trim; black
high-collared top with a small collar buckle; brown leather chest harness, belt, hip vials/pouch and thigh strap;
cream patterned sheer cloth panels hanging below the coat; black gloves; black trousers; black buckled boots; brass
folding magnifier raised in her right hand (viewer-left), a small book held in her left hand. The creator-approved
female selout v8 south static is the density / proportion / light benchmark (same cell, pin, 96-texel body, 0.5
scale, 1-texel near-black outer outline, upper-left light, 3-4 step material ramps); none of its texels or palette
entries are copied and none of its files are written. The old 32x48 Ji Cheng prototype frames are read for history
only and are not a base: every cluster here was placed fresh, nothing was recoloured.

Source of truth: MAP (colour keys) and ROLE (role-layer keys) below, literal 56x96 grids placed at cell offset
(12, 8). They were placed by hand as row spans, strokes and small stamps in a scratch authoring script (four bounded
passes), judged on x5 previews over grey / dark-floor / bright-floor colours and at 1x / 2x next to v8, then frozen
here. No image generation, sampling of the concept sheet, resampling, filtering, quantization or dithering was used.

Modes (real Python, isolated):
  python -I -B <this file> build                   write PNG, .pxo, .ora, palette, manifest (never overwrites)
  python -I -B <this file> check --pixelorama X    gates + rebuild equality + Pixelorama CLI .pxo/.ora round trips
                                                   + female v8 and old Ji Cheng 32x48 source files unchanged
  python -I -B <this file> preview <out.png>       x4 nearest preview of the sprite alone
"""
import argparse, hashlib, io, json, os, shutil, subprocess, sys, tempfile, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
VISUAL_ID = "ji-cheng"
SUBJECT = "south-idle-static"
VARIANT = "unapproved-v01"
STAMP = "20261018-132812"             # UTC
RUN_ID = "04cd6a26"
W, H = 80, 112
GRID_W, GRID_H = 56, 96
GRID_OFFSET = (12, 8)                 # grid (0,0) -> cell (12,8); body rows 8..103 like v8
PIN = (40, 104)
BODY_ROWS = (8, 103)
TEMPLATE_ROWS = {"head_top": 8, "shoulder": 34, "belt": 54, "knee": 76, "sole": 103}   # v8 south pose rows (guides)
DISPLAY_SCALE = 0.5                   # 96 texels -> 48 logical px; 1 texel = 1 window px at 1280x720
OUT_DIR_REL = "game/assets/characters/ji-cheng-hd"
PIXELORAMA_VERSION = "v1.2.3-stable"
GUIDE_RGB = (255, 0, 255)
ZIP_DT = (2026, 10, 18, 13, 28, 12)

V8_DIR = "game/assets/characters/pixelorama-pilots/"
V8_PNG = V8_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png"
OLD_DIR = "game/assets/characters/native-animation/"
OLD_SOUTH = OLD_DIR + "rpg-2-star-ocean-the-second_ji-cheng_native-idle-south-phase-00_m8-prototype_20261014-142157-13372e64.png"
# The approved female v8 source package and the old runtime Ji Cheng frame must stay exactly as committed at 160b823.
V8_LOCKS = {
    V8_PNG: ("ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd", "bytes"),
    V8_PNG + ".import": ("f83fcbce68ae824fddc4dc784fdc7c3cb0f4392326608dbdb09fab932370840d", "text"),
    V8_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-manifest_m8-v08_20261015-021600-2d6c5eff.json": ("3ba35811bf4d55b061b7719c6451908bdbb1eb68425bdda2c2303cc669f310ed", "text"),
    V8_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-editable-manifest_m8-v08_20261015-080907-270b2256.json": ("d40059be868e50f6acbea509e14dd2e8ccd6cac3b1405f39399c9fbff17e73c3", "text"),
    V8_DIR + "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-editable_m8-v08_20261015-080907-c8a1c140.pxo": ("cafa4998b107ae4b884cc877b80bbc695df267f37e09fb6e69701567f08a849e", "bytes"),
    OLD_SOUTH: ("a8319fe8da1c07c4d1caf405fa620141825f3b3f431384ae589a1a051b2fccea", "bytes"),
}
# Stable, tracked references (hash recorded in the manifest; volatile Bible/progress files are cited in the QA note).
REFS = {
    "identity_sheet_ji_cheng": ("outputs/rpg-2-star-ocean-the-second_ji-cheng_character-sheet_v01_20261013-190436-dcea1a37.png", "bytes"),
    "character_visual_registry": ("game/data/character-visuals/rpg-2-star-ocean-the-second_character-visual-registry_m8-v01_20261014-134810-2a5d1b3c.json", "text"),
    "benchmark_female_selout_v8_png": (V8_PNG, "bytes"),
    "benchmark_female_selout_v8_decision": ("docs/character-visuals/rpg-2-star-ocean-the-second_protagonist-female_south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md", "text"),
    "benchmark_female_selout_v8_visual_qa": ("docs/qa/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8_visual-qa-note_m8-v08_20261015-021600-c1694107.md", "text"),
    "old_ji_cheng_32x48_south_frame_not_used_as_base": (OLD_SOUTH, "bytes"),
    "old_ji_cheng_32x48_review": ("docs/character-visuals/rpg-2-star-ocean-the-second_ji-cheng_native-exploration-review_m8-prototype_20261014-142230-f1c8e5a4.md", "text"),
    "cast_identity_audit_48px": ("docs/qa/rpg-2-star-ocean-the-second_science-cast_hairstyle-and-identity-at-48px_unapproved-v01_20261016-183000-9234b6e1.md", "text"),
    "science_companions_identity_transfer_audit": ("docs/qa/rpg-2-star-ocean-the-second_science-companions_48px-identity-transfer-codex-audit_unapproved-v01_20261016-114641-a9e6c2d1.md", "text"),
    "roster_hairstyles_audit": ("docs/qa/rpg-2-star-ocean-the-second_roster-hairstyles_51-sheet-visual-audit_unapproved-v01_20261016-200329-7e7f62a9.md", "text"),
}

# Named ramps, light from the upper left. Hues follow Ji Cheng's sheet: cool blue-black hair with silver-white ends,
# fair skin, pale shaved scalp, dark forest-green coat with grey sleeve lining, near-black top/gloves/trousers/boots,
# brown leather harness, worn brass fittings, pale lens glass and cream patterned cloth.
RAMPS = {
    "outline": {"K": "0c0a0e"},
    "hair-blue-black": {"1": "6c7482", "2": "434852", "3": "292c34", "4": "111216"},
    "hair-silver-tips": {"5": "e2e4e6", "6": "b2b8c0", "7": "7e848e"},
    "skin": {"F": "f0d0bc", "f": "d8aa94", "e": "b47e6c"},
    "shaved-scalp": {"n": "c4aca2", "N": "927e84"},
    "eye": {"y": "2a2630"},
    "lip": {"R": "b8706a"},
    "coat-forest-green": {"G": "5a7450", "g": "3c5338", "H": "223524", "J": "0f1a11"},
    "coat-lining-grey": {"C": "a9ada4", "c": "787d76"},
    "top-gloves-black": {"B": "3c3c46", "b": "1f1f26"},
    "trousers-charcoal": {"P": "504e58", "p": "32313a", "o": "19181e"},
    "boots-black-leather": {"O": "54494a", "w": "2e2629"},
    "leather-brown": {"L": "a2724a", "l": "77513a", "m": "4b3327"},
    "brass": {"M": "e2c272", "X": "a8844a", "Y": "6c5432"},
    "lens-glass": {"Z": "d2e4e8", "z": "7c98a2"},
    "cloth-cream": {"A": "dcd0b2", "a": "a89c84"},
}
PAL = {k: v for ramp in RAMPS.values() for k, v in ramp.items()}

# Role layers, Pixelorama layer 1 = bottom. Outline texels belong to the part they outline (internal K separation
# rings belong to the part drawn on top). Kept as separate parts so a later animation pass can move them.
ROLE_LAYERS = [("coat-back", "c"), ("cloth-panels", "q"), ("legs", "l"), ("boots", "o"), ("coat-front", "t"),
               ("inner-top", "i"), ("harness-belt", "z"), ("arm-hanging", "m"), ("book", "k"), ("arm-raised", "n"),
               ("magnifier", "x"), ("head-face", "f"), ("hair", "h")]
LAYERS = [n for n, _ in ROLE_LAYERS] + ["guides"]
LAYER_NOTES = {
    "coat-back": "inside/back of the long coat seen between the legs down to mid-calf, deep shadow greens",
    "cloth-panels": "cream sheer patterned cloth: a long panel from the belt outside the viewer-left coat panel ending in a ragged point at the knee, a short panel peeking under the cut-away viewer-right hem; woven pattern ticks",
    "legs": "black/charcoal fitted trousers, lit left edges, knee creases, bunching over the boots; leather thigh strap with a brass buckle and a small pouch on the viewer-left thigh",
    "boots": "black buckled boots to mid-calf: lit cuff tops, two leather straps with brass buckles each, lit toe caps, chunky dark soles on cell rows 101 (viewer-left foot, set slightly back) and 102 (viewer-right foot); bottom outline rows 102 / 103",
    "coat-front": "dark forest-green long open coat: lit shoulders and viewer-left plane, shadow viewer-right plane, lapels with brass edge, breast pocket flap + button, side seam, brass toggles, worn texture texels, uneven hem (long ragged point on the viewer-left, cut-away on the viewer-right) with worn brass trim glints",
    "inner-top": "black high-collared top with a small brass collar buckle, visible in the open coat",
    "harness-belt": "two brown leather chest straps crossing at a brass ring, brown belt with brass buckle, two silver vials with brass caps and a leather pouch at the viewer-left hip",
    "arm-hanging": "viewer-right (her left) arm hanging: green sleeve in shadow, grey rolled lining cuff, black glove",
    "book": "small brown leather-bound book held against the viewer-right hip: cream page edge, brass clasp, gloved fingers over the cover",
    "arm-raised": "viewer-left (her right) arm: green sleeve angled from the shoulder to the elbow, wide grey rolled cuff at the elbow, black-gloved forearm raised, fist at head height (as in the sheet's front view)",
    "magnifier": "brass folding magnifier held up beside the hair: 7x6 brass ring with a lit upper-left rim, pale glass with a highlight, hinge into the glove",
    "head-face": "13-wide fair face, chin on cell row 32: calm lowered lids, grey-dark eyes, brow on the open side, nose shadow, muted lips, right-side shadow; shaved LEFT temple (viewer-right) as a 3-4 x 9 pale stubble patch with razor lines, ear, rectangular brass drop earring",
    "hair": "blue-black bob swept from the side part above the shaved temple across the forehead toward the viewer-left; lit cap and sheen along the sweep; long viewer-left curtain to the shoulder with jagged silver-white tips (three points); short lock behind the shaved side with silver ends",
    "guides": "hidden + locked #ff00ff: cell border, ticks on the v8 template rows (head top 8, shoulder 34, belt 54, knee 76, sole 103), pin (40,104); never exported",
}

MAP = [
    "......................KKKKKKKKK.........................",  # 00 (cell row 8)
    "....................KK221113334KK.......................",  # 01 (cell row 9)
    "..................KK2211133333334K......................",  # 02 (cell row 10)
    ".................K2211333333211334K.....................",  # 03 (cell row 11)
    "................K221133333113233334K....................",  # 04 (cell row 12)
    "................K2133333133433234nnNK...................",  # 05 (cell row 13)
    "...............K22333313334333324nnnNK..................",  # 06 (cell row 14)
    "...............K22333133343332334nNnNK..................",  # 07 (cell row 15)
    "...............K22333333433323334nnNNK..................",  # 08 (cell row 16)
    "...............K2233333433323334KKnnNK..................",  # 09 (cell row 17)
    "...............K223333433323334KKKNnNK..................",  # 10 (cell row 18)
    "...............K223333333234FFFFfenNNK..................",  # 11 (cell row 19)
    "...............K2233333334FFFFFFfeKnNK..................",  # 12 (cell row 20)
    "...............K22333334FFFFF3333fenNK..................",  # 13 (cell row 21)
    "...............K2333334FeeeFFeeeefefe4K.................",  # 14 (cell row 22)
    "...............K2333334FyyFFFFyyFfefe44K................",  # 15 (cell row 23)
    "...............K2333334Fy6FFFFy6Ffefe44K................",  # 16 (cell row 24)
    "...............K233334FFFFFFFFFFFfefe44K................",  # 17 (cell row 25)
    "......KKKKK...K2334334FfFFFFfFFFFfeKM44K................",  # 18 (cell row 26)
    ".....KMMMMMK..K2334334FFFFFFeFFFfeKKM44K................",  # 19 (cell row 27)
    "....KMMZzzzXK.K2134334KFFFFFFFFFfeKKM44K................",  # 20 (cell row 28)
    "....KMZZzzzXK.K2133334KFFFFRRRFFfeKKX44K................",  # 21 (cell row 29)
    "....KMzzzzzXK.K2133334KKFFFFfFFfeK44444K................",  # 22 (cell row 30)
    "....KMzzzzYXK.K2333434K.KFFFFFfeKK33333K................",  # 23 (cell row 31)
    ".....KXXXYXK..K3333433K.KbffFffbKK77777K................",  # 24 (cell row 32)
    "......KKKKK...K3333333K.KBeeeeebKK77777K................",  # 25 (cell row 33)
    "......KBBBbK..K7737777K.KBBBMBbbKK66667K................",  # 26 (cell row 34)
    ".....KBBBBbK..K7777737KKKBBBXBbbKK55557K................",  # 27 (cell row 35)
    ".....KBBBBbK..K6663667GGXXGGgggYHJH5557K................",  # 28 (cell row 36)
    "......KBBBbK..K6666667GGXGBBbbbgYJH6J6KKKKK.............",  # 29 (cell row 37)
    "......KBbbbK..K5556557GGGGBBbbbgHJgHH6gHHJJK............",  # 30 (cell row 38)
    "......KBbbbK.KG655H55ggGGgLBbblgHJggJKgHHJJK............",  # 31 (cell row 39)
    "......KBbbbK.KGG56H56ggGGgLBbblgHJggJKgHHJJK............",  # 32 (cell row 40)
    "......KBbbbKKGGg6HG6GggGGBLbbblbHJggJKgHHJJK............",  # 33 (cell row 41)
    "......KBbbbKGGggHKG6GggGGBLbbblbHJggJKgHHJJK............",  # 34 (cell row 42)
    ".....KKCCCcKKgggHKGGGggGGBLbbblbHJggHKgHHJJK............",  # 35 (cell row 43)
    "....KCCCCCCccKgHKKGGGgggGBBLblbbHJggHKgHHJJK............",  # 36 (cell row 44)
    "....KCCCCCCCccKHKKGHHHHgGBBLblbbHJggHKgHHJJK............",  # 37 (cell row 45)
    ".....KCCCCCCccKK.KGGXgggGBBLMlbbHJggHHKgHHJJK...........",  # 38 (cell row 46)
    "......KCCCCccKK..KGGGgggGBBLblbbHJggHHKgHHJJK...........",  # 39 (cell row 47)
    ".......KKKKKK....KGGGggggBBLblbbggggHHKgHHJJK...........",  # 40 (cell row 48)
    ".................KGgGggggBBblbbbgggJHHKgHHJJK...........",  # 41 (cell row 49)
    ".................KGGgggggBBblbbbgggJHHKgHHJJK...........",  # 42 (cell row 50)
    ".................KGGGggggBBblbbbgggJHHKgHHJJK...........",  # 43 (cell row 51)
    ".................KGGGggggBBblbbbgggJHHKCCCCcKK..........",  # 44 (cell row 52)
    ".................KGGGggggBBblbbbggggHHCKKKKKcK..........",  # 45 (cell row 53)
    "................KLLLLLLLLLLMMLlllllllllCCCCccK..........",  # 46 (cell row 54)
    "................KllllllllllMXlmmmmmmmmmBbbbbK...........",  # 47 (cell row 55)
    "...........KKK..KXXXXLllmHHHHHHHJgHHHHKKKKKKK...........",  # 48 (cell row 56)
    "..........KAAaKKG5767LMlmHHHHHHHJgHHHKALLLLLLK..........",  # 49 (cell row 57)
    "..........KAAaKKG5767LllmHHHHHHHJgHHHKAlbbblmK..........",  # 50 (cell row 58)
    "..........KAAaKKG5767LllmHHHHHHHJgHHHKAlllllmK..........",  # 51 (cell row 59)
    "..........KAaaKKG5767LllmHHHHHHHJgHHHKAllMXlmK..........",  # 52 (cell row 60)
    "..........KAAaKKG57HgggHHHHHHHHHJgHHHKAlllllmK..........",  # 53 (cell row 61)
    "..........KAAaKKGGgggggHHHHHHHHHHgHHHKAlllllmK..........",  # 54 (cell row 62)
    "..........KaAaKGGgggggHHHHHHHHHHHgHHHKAlllllmK..........",  # 55 (cell row 63)
    "..........KAAaKGGgggggXppppoopppppgHHKAlllllmK..........",  # 56 (cell row 64)
    "..........KAAaKGGgggggHppppoopppppgHHJKKKKKKK...........",  # 57 (cell row 65)
    "..........KAaaKHGgggggHmpppoopppppgHHHHHJJK.............",  # 58 (cell row 66)
    "..........KAAaKHGgggggHmpppoopppppgHHHHHJJK.............",  # 59 (cell row 67)
    "..........KAAaGGggggggHmllllopppppHHHHHHJJK.............",  # 60 (cell row 68)
    ".........KAaAaGGggggggHmmmmmopppppgHHHHHJJK.............",  # 61 (cell row 69)
    ".........KAAAaGGHgggggXmppooHpppppgHHHHHJJK.............",  # 62 (cell row 70)
    ".........KAAaKGGgHggggHmppooHpppppgHHHHHHJJK............",  # 63 (cell row 71)
    ".........KAaaKGGggggggHpppooHpppppgHHHJHHJJK............",  # 64 (cell row 72)
    ".........KAAaKGGggggggHpppooHpppppgHHHJHHJJK............",  # 65 (cell row 73)
    ".........KAAaGHgggggggHpopooHpppppgHHHHHHJJK............",  # 66 (cell row 74)
    ".........KaAaGHgggggggHppoooHppoppgHHHHHHJJK............",  # 67 (cell row 75)
    ".........KAAaGGgggggggHpppooHpppopgHHHHHHJJK............",  # 68 (cell row 76)
    ".........KAAaGGgggggHgHpppooHpppppgHHHHHHJJK............",  # 69 (cell row 77)
    ".........KAaaGGggggggHHpppooHpppppgHHHHHHHJJK...........",  # 70 (cell row 78)
    ".........KAAGGggggggggHpppooHpppppgHHHHHHHJJK...........",  # 71 (cell row 79)
    ".........KAAGGgggggggHPpppooHpppppgHHHHHHHJJK...........",  # 72 (cell row 80)
    "........KAaAGGgggggggHPpppooHpppppoogHHHHHJJK...........",  # 73 (cell row 81)
    "........KAAAGGgHgggggHPpppooHpppppooaXgHHHJJK...........",  # 74 (cell row 82)
    ".........KAAGGgggggggHPpppooHpppppooXAAagHJJK...........",  # 75 (cell row 83)
    ".........KAaaGGggggggHPoppooHpppppooAAaaKKgJJK..........",  # 76 (cell row 84)
    "..........KKKKGGgggggHPpopooHppoppooAAaaK.KKJK..........",  # 77 (cell row 85)
    "..............KGGggggHPpppooHpppopooaaaK....K...........",  # 78 (cell row 86)
    "...............KGGggXPPpppooHpppppooAaaK................",  # 79 (cell row 87)
    "................KGGXOOOOOOOOHOOOOOOOOaK.................",  # 80 (cell row 88)
    ".................KHKOOwwwwwwKOwwwwwwwaK.................",  # 81 (cell row 89)
    "..................KKOOwwwwwwKOwwwwwwwK..................",  # 82 (cell row 90)
    "...................KmMmmmmmmKmmmmmmXmK..................",  # 83 (cell row 91)
    "...................KOOwwwwwwKOwwwwwwwK..................",  # 84 (cell row 92)
    "...................KOOwwwwwwKOwwwwwwwK..................",  # 85 (cell row 93)
    "...................KOOwwwwwwKOwwwwwwwK..................",  # 86 (cell row 94)
    "...................KmMmmmmmmKmmmmmmXmK..................",  # 87 (cell row 95)
    "...................KOOwwwwwwKOwwwwwwwK..................",  # 88 (cell row 96)
    "...................KOOwwwwwwKOwwwwwwwK..................",  # 89 (cell row 97)
    "..................KOOwwwwwwwKOwwwwwwwK..................",  # 90 (cell row 98)
    ".................KOOOwwwwwwwKOwwwwwwwwK.................",  # 91 (cell row 99)
    ".................KwwwwwwwwwwKOOOwwwwwwwK................",  # 92 (cell row 100)
    ".................KKKKKKKKKKKKOwwwwwwwwwK................",  # 93 (cell row 101)
    "..................KKKKKKKKKKKKKKKKKKKKKK................",  # 94 (cell row 102)
    ".............................KKKKKKKKKK.................",  # 95 (cell row 103)
]

ROLE = [
    "......................hhhhhhhhh.........................",  # 00 (cell row 8)
    "....................hhhhhhhhhhhhh.......................",  # 01 (cell row 9)
    "..................hhhhhhhhhhhhhhhh......................",  # 02 (cell row 10)
    ".................hhhhhhhhhhhhhhhhhh.....................",  # 03 (cell row 11)
    "................hhhhhhhhhhhhhhhhhhhh....................",  # 04 (cell row 12)
    "................hhhhhhhhhhhhhhhhhffff...................",  # 05 (cell row 13)
    "...............hhhhhhhhhhhhhhhhhhfffff..................",  # 06 (cell row 14)
    "...............hhhhhhhhhhhhhhhhhhfffff..................",  # 07 (cell row 15)
    "...............hhhhhhhhhhhhhhhhhhfffff..................",  # 08 (cell row 16)
    "...............hhhhhhhhhhhhhhhhhhfffff..................",  # 09 (cell row 17)
    "...............hhhhhhhhhhhhhhhhhffffff..................",  # 10 (cell row 18)
    "...............hhhhhhhhhhhhhffffffffff..................",  # 11 (cell row 19)
    "...............hhhhhhhhhhhffffffffffff..................",  # 12 (cell row 20)
    "...............hhhhhhhhhffffffffffffff..................",  # 13 (cell row 21)
    "...............hhhhhhhhffffffffffffffhh.................",  # 14 (cell row 22)
    "...............hhhhhhhhffffffffffffffhhh................",  # 15 (cell row 23)
    "...............hhhhhhhhffffffffffffffhhh................",  # 16 (cell row 24)
    "...............hhhhhhhfffffffffffffffhhh................",  # 17 (cell row 25)
    "......xxxxx...hhhhhhhhfffffffffffffffhhh................",  # 18 (cell row 26)
    ".....xxxxxxx..hhhhhhhhfffffffffffffffhhh................",  # 19 (cell row 27)
    "....xxxxxxxxx.hhhhhhhhfffffffffffffffhhh................",  # 20 (cell row 28)
    "....xxxxxxxxx.hhhhhhhhhffffffffffffffhhh................",  # 21 (cell row 29)
    "....xxxxxxxxx.hhhhhhhhhfffffffffffhhhhhh................",  # 22 (cell row 30)
    "....xxxxxxxxx.hhhhhhhhh.fffffffffhhhhhhh................",  # 23 (cell row 31)
    ".....xxxxxxx..hhhhhhhhh.iifffffiihhhhhhh................",  # 24 (cell row 32)
    "......xxxxx...hhhhhhhhh.iifffffiihhhhhhh................",  # 25 (cell row 33)
    "......nnnnnn..hhhhhhhhh.iiiiiiiiihhhhhhh................",  # 26 (cell row 34)
    ".....nnnnnnn..hhhhhhhhhtiiiiiiiiihhhhhhh................",  # 27 (cell row 35)
    ".....nnnnnnn..hhhhhhhhttttttttttttthhhhh................",  # 28 (cell row 36)
    "......nnnnnn..hhhhhhhhttttiiiiitttththhmmmm.............",  # 29 (cell row 37)
    "......nnnnnn..hhhhhhhhttttiiiiitttttthmmmmmm............",  # 30 (cell row 38)
    "......nnnnnn.nnhhhnhhtttttziiizttttttmmmmmmm............",  # 31 (cell row 39)
    "......nnnnnn.nnnhhnhhtttttziiizttttttmmmmmmm............",  # 32 (cell row 40)
    "......nnnnnnnnnnhnthtttttiziiizitttttmmmmmmm............",  # 33 (cell row 41)
    "......nnnnnnnnnnnnthtttttiziiizitttttmmmmmmm............",  # 34 (cell row 42)
    ".....nnnnnnnnnnnnntttttttiziiizitttttmmmmmmm............",  # 35 (cell row 43)
    "....nnnnnnnnnnnnnttttttttiiziziitttttmmmmmmm............",  # 36 (cell row 44)
    "....nnnnnnnnnnnnnttttttttiiziziitttttmmmmmmm............",  # 37 (cell row 45)
    ".....nnnnnnnnnnn.ttttttttiizzziittttttmmmmmmm...........",  # 38 (cell row 46)
    "......nnnnnnnnn..ttttttttiiziziittttttmmmmmmm...........",  # 39 (cell row 47)
    ".......nnnnnn....ttttttttiiziziittttttmmmmmmm...........",  # 40 (cell row 48)
    ".................ttttttttiiiziiittttttmmmmmmm...........",  # 41 (cell row 49)
    ".................ttttttttiiiziiittttttmmmmmmm...........",  # 42 (cell row 50)
    ".................ttttttttiiiziiittttttmmmmmmm...........",  # 43 (cell row 51)
    ".................ttttttttiiiziiittttttmmmmmmmm..........",  # 44 (cell row 52)
    ".................ttttttttiiiziiittttttmmmmmmmm..........",  # 45 (cell row 53)
    "................zzzzzzzzzzzzzzzzzzzzzzzmmmmmmm..........",  # 46 (cell row 54)
    "................zzzzzzzzzzzzzzzzzzzzzzzmmmmmm...........",  # 47 (cell row 55)
    "...........qqq..zzzzzzzzzcccccccctttttkkkkkkk...........",  # 48 (cell row 56)
    "..........qqqqqttzzzzzzzzccccccccttttkkkkkkkkk..........",  # 49 (cell row 57)
    "..........qqqqqttzzzzzzzzccccccccttttkkkkkkkkk..........",  # 50 (cell row 58)
    "..........qqqqqttzzzzzzzzccccccccttttkkkkkkkkk..........",  # 51 (cell row 59)
    "..........qqqqqttzzzzzzzzccccccccttttkkkkkkkkk..........",  # 52 (cell row 60)
    "..........qqqqqttzztttttcccccccccttttkkkkkkkkk..........",  # 53 (cell row 61)
    "..........qqqqqtttttttttcccccccccttttkkkkkkkkk..........",  # 54 (cell row 62)
    "..........qqqqqttttttttccccccccccttttkkkkkkkkk..........",  # 55 (cell row 63)
    "..........qqqqqttttttttllllllllllltttkkkkkkkkk..........",  # 56 (cell row 64)
    "..........qqqqqttttttttlllllllllllttttkkkkkkk...........",  # 57 (cell row 65)
    "..........qqqqqttttttttlllllllllllttttttttt.............",  # 58 (cell row 66)
    "..........qqqqqttttttttlllllllllllttttttttt.............",  # 59 (cell row 67)
    "..........qqqqtttttttttlllllllllllttttttttt.............",  # 60 (cell row 68)
    ".........qqqqqtttttttttlllllllllllttttttttt.............",  # 61 (cell row 69)
    ".........qqqqqtttttttttlllllclllllttttttttt.............",  # 62 (cell row 70)
    ".........qqqqqtttttttttlllllcllllltttttttttt............",  # 63 (cell row 71)
    ".........qqqqqtttttttttlllllcllllltttttttttt............",  # 64 (cell row 72)
    ".........qqqqqtttttttttlllllcllllltttttttttt............",  # 65 (cell row 73)
    ".........qqqqttttttttttlllllcllllltttttttttt............",  # 66 (cell row 74)
    ".........qqqqttttttttttlllllcllllltttttttttt............",  # 67 (cell row 75)
    ".........qqqqttttttttttlllllcllllltttttttttt............",  # 68 (cell row 76)
    ".........qqqqttttttttttlllllcllllltttttttttt............",  # 69 (cell row 77)
    ".........qqqqttttttttttlllllclllllttttttttttt...........",  # 70 (cell row 78)
    ".........qqqtttttttttttlllllclllllttttttttttt...........",  # 71 (cell row 79)
    ".........qqqttttttttttllllllclllllttttttttttt...........",  # 72 (cell row 80)
    "........qqqqttttttttttllllllclllllllttttttttt...........",  # 73 (cell row 81)
    "........qqqqttttttttttllllllclllllllqtttttttt...........",  # 74 (cell row 82)
    ".........qqqttttttttttllllllcllllllltqqqttttt...........",  # 75 (cell row 83)
    ".........qqqqtttttttttllllllclllllllqqqqtttttt..........",  # 76 (cell row 84)
    "..........qqqtttttttttllllllclllllllqqqqq.tttt..........",  # 77 (cell row 85)
    "..............ttttttttllllllclllllllqqqq....t...........",  # 78 (cell row 86)
    "...............ttttttlllllllclllllllqqqq................",  # 79 (cell row 87)
    "................ttttoooooooocooooooooqq.................",  # 80 (cell row 88)
    ".................tttoooooooocooooooooqq.................",  # 81 (cell row 89)
    "..................tooooooooooooooooooq..................",  # 82 (cell row 90)
    "...................ooooooooooooooooooo..................",  # 83 (cell row 91)
    "...................ooooooooooooooooooo..................",  # 84 (cell row 92)
    "...................ooooooooooooooooooo..................",  # 85 (cell row 93)
    "...................ooooooooooooooooooo..................",  # 86 (cell row 94)
    "...................ooooooooooooooooooo..................",  # 87 (cell row 95)
    "...................ooooooooooooooooooo..................",  # 88 (cell row 96)
    "...................ooooooooooooooooooo..................",  # 89 (cell row 97)
    "..................oooooooooooooooooooo..................",  # 90 (cell row 98)
    ".................oooooooooooooooooooooo.................",  # 91 (cell row 99)
    ".................ooooooooooooooooooooooo................",  # 92 (cell row 100)
    ".................ooooooooooooooooooooooo................",  # 93 (cell row 101)
    "..................oooooooooooooooooooooo................",  # 94 (cell row 102)
    ".............................oooooooooo.................",  # 95 (cell row 103)
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
                      "file_format": "0", "file_name": json.dumps("ji-cheng-south-idle-static-v01"),
                      "frame_current_tag": "0", "include_tag_in_filename": "false", "interpolation": "0",
                      "lines_count": "1", "new_dir_for_each_frame_tag": "false", "number_of_digits": "4",
                      "number_of_frames": "1", "orientation": "0", "repeat_count": "0", "resize": "100",
                      "save_quality": "0.75", "separator_character": "\"_\"",
                      "sheet_layers_as_separate_files": "false", "split_layers": "false"}
    palette = {"name": "ji-cheng-south-idle-static-v01", "comment": "declared ramps", "width": 8, "height": 5,
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


P4_EXEMPT = ("outline", "eye", "lip")   # outline and the single eye / lip colours are not lit ramps


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
    def cells(keys, roles=None):
        return [(x, y) for y in range(GRID_H) for x in range(GRID_W)
                if MAP[y][x] in keys and (roles is None or ROLE[y][x] in roles)]
    def bbox(pts):
        xs_ = [p[0] for p in pts]; ys_ = [p[1] for p in pts]
        return [min(xs_) + ox, min(ys_) + oy, max(xs_) + ox, max(ys_) + oy]
    def mean_l(keys, roles):
        pts = [hex_rgb(PAL[MAP[y][x]]) for x, y in cells(keys, roles)]
        return round(sum(lab(p)[0] for p in pts) / len(pts), 1)
    hair_rows = [y for y in range(GRID_H) if any(ROLE[y][x] == "h" for x in range(GRID_W))]
    face_rows = [y for y in range(GRID_H) if any(MAP[y][x] in "Ff" and ROLE[y][x] == "f" for x in range(GRID_W))]
    face_w = max(span(y, keys="Ff", roles="f")[1] - span(y, keys="Ff", roles="f")[0] + 1 for y in face_rows)
    # head asymmetry: hair extent left of the face vs right of the face on the face rows
    face_mid = 28                                          # grid column of the pin / face centre
    left_ext = max(face_mid - span(y, roles="h")[0] for y in face_rows if span(y, roles="h"))
    right_ext = max(span(y, roles="hf")[1] - face_mid for y in face_rows if span(y, roles="hf"))
    shaved = cells("nN", "f")
    silver = cells("567", "h")
    lens = cells("MXYZz", "x")
    # clear background columns between the raised forearm/magnifier and the hair curtain, per row
    gaps = {}
    for y in range(GRID_H):
        xs_n = [x for x in range(GRID_W) if ROLE[y][x] in "nx" and MAP[y][x] != "K"]
        xs_h = [x for x in range(GRID_W) if ROLE[y][x] == "h" and MAP[y][x] != "K"]
        if xs_n and xs_h and max(xs_n) < min(xs_h):
            gaps[y + oy] = sum(1 for x in range(max(xs_n) + 1, min(xs_h)) if MAP[y][x] == ".")
    shoulder = span(36 - oy)
    return {
        "face_max_width_px": face_w,
        "head_rows_cell": [min(hair_rows) + oy, max(face_rows) + oy],
        "hair_extent_left_of_face_centre_px": left_ext, "head_extent_right_of_face_centre_px": right_ext,
        "shaved_temple_texels": len(shaved), "shaved_temple_bbox_cell": bbox(shaved),
        "silver_tip_texels": len(silver), "silver_tip_bbox_cell": bbox(silver),
        "magnifier_texels": len(lens), "magnifier_bbox_cell": bbox(lens),
        "background_px_between_raised_arm_and_hair_by_cell_row": gaps,
        "coat_green_texels": len(cells("GgHJ")), "cream_cloth_texels": len(cells("Aa", "q")),
        "shoulder_span_cell_x_row36": [shoulder[0] + ox, shoulder[1] + ox],
        "mean_Lstar": {"hair_black": mean_l("1234", "h"), "silver_tips": mean_l("567", "h"),
                       "shaved_scalp": mean_l("nN", "f"), "skin": mean_l("Ffe", "f"),
                       "coat": mean_l("GgHJ", "tmnc"), "top_gloves": mean_l("Bb", "imn"),
                       "trousers": mean_l("Ppo", "l"), "boots": mean_l("Ow", "o"), "cloth": mean_l("Aa", "q")},
        "shaved_n_vs_hair_3_dE76": round(de76(hex_rgb(PAL["n"]), hex_rgb(PAL["3"])), 1),
        "shaved_n_vs_skin_F_dE76": round(de76(hex_rgb(PAL["n"]), hex_rgb(PAL["F"])), 1),
        "silver_5_vs_coat_G_dE76": round(de76(hex_rgb(PAL["5"]), hex_rgb(PAL["G"])), 1),
        "coat_g_vs_trousers_p_dE76": round(de76(hex_rgb(PAL["g"]), hex_rgb(PAL["p"])), 1),
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
    p = {"project": "Worlds Between", "visual_id": VISUAL_ID, "purpose": "declared named ramps for the Ji Cheng "
         "south idle static pilot at the female selout v8 density (v01)", "art_approved": False,
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
        "project": "Worlds Between", "milestone": "M8", "visual_id": VISUAL_ID, "display_name_zh": "纪澄",
        "identity": "Ji Cheng, science-region side companion (companion 16), 28-year-old woman, old-records restorer",
        "purpose": "South-facing exploration idle STATIC frame for Ji Cheng at the approved 48 logical px, authored "
                   "fresh as clean hand-placed clusters at the approved female selout v8 rendering density; editable "
                   "Pixelorama role layers kept as separable parts for a later animation pass.",
        "status": "UNAPPROVED, NONRUNTIME pilot; technical gates only; not runtime-integrated; no animation; south only",
        "art_approved": False, "human_reviewed": False, "runtime_integrated": False, "variant": VARIANT, "run_id": RUN_ID,
        "acceptance_counters_unchanged": {"runtime_sprites_accepted": "0/52", "scene_visual_gates": "3/12",
                                          "overall_meter": "40.8%", "plays": "0/2"},
        "authorship": "Colour and role grids placed part by part by Claude (Claude Code, signed-in Claude Max, claude.ai "
                      "firstParty, no API key) as hand-chosen row spans, strokes and small stamps, then frozen as the "
                      "literal grids in the tool. No image generation, no sampling of the concept sheet, no "
                      "resampling, filtering, quantization or dithering; no v8 or old-prototype texel or palette entry "
                      "copied or recoloured.",
        "not_used_as_base": ["old 32x48 Ji Cheng native idle/walk prototype (13372e64 and siblings; read for history only)",
                             "old Ji Cheng side-view combat prototype"],
        "benchmark": {"female_selout_v8": "density/proportion/light benchmark only (same 80x112 cell, pin, 96-texel body, "
                      "0.5 scale, 1-texel near-black outline, upper-left light, 3-4 step material ramps); v8 files are "
                      "hash-locked and never written."},
        "identity_anchors_from_sheet": {
            "hair": "blue-black straight bob swept from a side part above the shaved temple across the forehead toward the viewer-left, falling to the shoulder there with silver-white tips; a shorter silver-tipped lock behind the shaved side (not a rounded grey cap, not a centre part, not a headset)",
            "shaved_temple": "her LEFT temple (viewer-right in a south view) shaved, shown as a large pale stubble patch with razor lines on the head outline, ear and rectangular brass drop earring",
            "face": "28-year-old woman, fair skin, calm lowered lids, grey-dark eyes, muted lips",
            "coat": "dark forest-green long open coat with an uneven pointed hem (long ragged point viewer-left, cut-away viewer-right), grey rolled sleeve linings, worn brass trim",
            "tools": "brass folding magnifier raised in her right hand (viewer-left) beside the hair, as in the sheet's front view; small leather book held in her left hand",
            "other": "black high-collared top with a brass collar buckle, crossing brown chest straps, belt with brass buckle, silver vials and a pouch at the viewer-left hip, leather thigh strap, cream patterned sheer cloth panels below the coat, black gloves, black trousers, black buckled boots",
            "pose": "quiet frontal idle: right forearm raised holding the magnifier, left arm hanging with the book at the hip, feet planted slightly apart",
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
        "locked_source_files": {rel: {"sha256": h, "hash_algorithm": "sha256-bytes" if k == "bytes" else "sha256-text-lf-v1"}
                                for rel, (h, k) in V8_LOCKS.items()},
        "gates": gates(full),
        "legibility_metrics_report_only": legibility(),
        "pending_visual_decisions": [
            "Does the pale shaved patch read as shaved scalp at 1x, or as a grey/white hair streak?",
            "Do the silver tips read as hair ends, or as shoulder pads on the coat?",
            "Is the raised magnifier legible as a held tool at 1x against busy city paving?",
            "Is the frontal, symmetric stance too stiff next to v8's weight shift?",
            "Is the cream cloth panel on the viewer-left too plank-like / too bright?",
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
        raise SystemExit("female v8 or old Ji Cheng source files differ from their locks; refusing to build")
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
           "locked_sources_unchanged": v8_unchanged()}
    layers, hidden, merged, mt = read_ora_layers(disk["ora"])
    bottom_up = [(n, a) for n, a, vis in reversed(layers) if vis != "hidden"]
    rep["ora_structure"] = {"mimetype_first_and_stored": mt, "hidden_layers": hidden,
                            "layer_names_bottom_up": [n for n, _ in bottom_up],
                            "visible_layers_recompose_to_png": recompose(bottom_up).tobytes() == full.tobytes(),
                            "each_layer_equals_role_blob": all(a.tobytes() == blobs[n].tobytes() for n, a in bottom_up),
                            "mergedimage_equals_png": merged.tobytes() == full.tobytes()}
    snap0 = real_pixelorama_snapshot()
    tmp = tempfile.mkdtemp(prefix="wb-jicheng-v01-")
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
    ok = (all(rep["files_equal_rebuild"].values()) and rep["manifest_hashes_match"] and all(rep["locked_sources_unchanged"].values())
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
