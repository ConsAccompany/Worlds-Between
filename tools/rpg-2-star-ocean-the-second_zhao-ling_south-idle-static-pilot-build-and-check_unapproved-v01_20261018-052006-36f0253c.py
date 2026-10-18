"""Zhao Ling (赵铃) south-facing EXPLORATION IDLE high-density STATIC pilot v01 (UNAPPROVED, NONRUNTIME): one
hand-placed 80x112 cell at the approved 48 logical px, editable Pixelorama .pxo + layered .ora (11 role layers +
hidden guides), named-ramp palette, manifest and technical gates.

Scope: one direction (south), one static idle frame, Zhao Ling only. No animation, no other direction, no runtime
integration, no approval or counter change (exploration sprites stay 0/52). The creator-approved female selout v8
south static is the density / proportion / value-separation benchmark (same cell, pin, 96-texel body, 0.5 display
scale, 1-texel outer ink); none of its texels, palette entries or design elements are copied. The rejected 2026-10-14
32x48 Zhao Ling runtime body and the premium concept are not reused or upscaled.

Identity source: the approved character sheet outputs/...zhao-ling_character-sheet_v01_20261013-193120-54215370.png
(front full-body view, head close-ups, chibi turnarounds, radio prop detail) and the character bible entry
31 赵铃 / Zhao Ling (female, 26, firearms; 湖蓝耳机、整齐的侧分短发和便携天线). See the manifest for the cue list,
the proposed pixel simplifications and the recorded open design questions.

Source of truth: MAP (colour keys) and ROLE (role-layer keys) below, literal 56x96 grids placed at cell offset (12, 8).
The masses were seeded in a scratch primitive script (not shipped, kept in %TEMP%), then the head, hair locks, blue
tips, earcup, chin/collar rows and body details were hand-typed and judged on x3/x6 previews over the city / annex
floor colours. No image generation, resampling, filtering, quantization or dithering was used.

Format helpers (pxo/ora writers, gates, isolated Pixelorama CLI) live in the shared module named in SHARED_REL; this
file carries only the Zhao-specific data, identity metrics and manifest.

Modes (real Python, isolated):
  python -I -B <this file> build                 write PNG, .pxo, .ora, palette, manifest, .gdignore (never overwrites)
  python -I -B <this file> check [--pixelorama X] gates + rebuild equality + reference locks + Pixelorama CLI round trips
  python -I -B <this file> preview <out.png>     x4 nearest preview of the sprite alone
"""
import argparse, hashlib, importlib.util, json, os, sys
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SHARED_REL = "tools/rpg-2-star-ocean-the-second_static-pilot-v8-format_shared-utils_unapproved-v01_20261018-052006-fcae68d3.py"
_spec = importlib.util.spec_from_file_location("v8fmt", os.path.join(REPO, *SHARED_REL.split("/")))
fmt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fmt)

SLUG = "rpg-2-star-ocean-the-second"
VISUAL_ID = "zhao-ling"
SUBJECT = "south-idle-static-pilot"
VARIANT = "unapproved-v01"
STAMP = "20261018-052006"            # local EDT
RUN_ID = "7027d25c"
OUT_DIR_REL = "game/assets/characters/zhao-ling/south-idle-static-pilot-unapproved-v01"
ZIP_DT = (2026, 10, 18, 5, 20, 6)

# Stable, tracked references (all clean at HEAD when this pilot was made).
REFS = {
    "identity_sheet_zhao_ling": ("outputs/rpg-2-star-ocean-the-second_zhao-ling_character-sheet_v01_20261013-193120-54215370.png", "bytes"),
    "character_bible_entry_31": ("outputs/rpg-2-star-ocean-the-second_remaining-companions_character-bible_v01_20261013-181920-6d2a4f8c.md", "text"),
    "codex_identity_transfer_audit_48px": ("docs/qa/rpg-2-star-ocean-the-second_science-companions_48px-identity-transfer-codex-audit_unapproved-v01_20261016-114641-a9e6c2d1.md", "text"),
    "codex_cast_hairstyle_identity_audit_48px": ("docs/qa/rpg-2-star-ocean-the-second_science-cast_hairstyle-and-identity-at-48px_unapproved-v01_20261016-183000-9234b6e1.md", "text"),
    "prior_native_32x48_review": ("docs/character-visuals/rpg-2-star-ocean-the-second_zhao-ling_native-exploration-review_m8-v01_20261014-142600-582df7a1.md", "text"),
    "prior_native_32x48_south_idle_not_reused": ("game/assets/characters/native-animation/rpg-2-star-ocean-the-second_zhao-ling_native-exploration-idle-south_m8-v01_20261014-142000-a9c9de72.png", "bytes"),
    "prior_premium_concept_not_reused": ("game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_zhao-ling_south-exploration-premium-pixel_m8-concept_20261014-160624-fe822f60.png", "bytes"),
    "benchmark_female_selout_v8_png": (fmt.V8_REL, "bytes"),
    "benchmark_female_selout_v8_decision": ("docs/character-visuals/rpg-2-star-ocean-the-second_protagonist-female_south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md", "text"),
    "confusion_pair_liang_xu_static_pilot_png": ("game/assets/characters/liang-xu/south-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot_unapproved-v01_20261016-140940-46a036ed.png", "bytes"),
}

# Named ramps, light from the upper left. Hues follow the sheet: blue-black hair, lake-blue (湖蓝) accent shared by
# hair tips / earcup / band / straps / cable / boot soles, near-black jacket with light-grey collar lining and rolled
# cuffs, white tee, charcoal trousers, brass hardware, pale skin with grey-blue eyes. The accent is pushed bluer and
# brighter than the sheet's muted steel-teal so it separates from v8's green-teal scarf and reads at 1 texel/px.
RAMPS = {
    "ink": {"K": "0c0d12", "k": "1f2029"},
    "skin": {"S": "f4d8c6", "s": "dcb09c", "z": "b3806f"},
    "hair": {"H": "525b76", "h": "2f3348", "g": "151722"},
    "lake_blue": {"B": "8fd3e6", "b": "4f9dbf", "n": "2c6585"},
    "steel": {"W": "d7dce2", "w": "8f98a8", "v": "535b6b"},
    "brass": {"Y": "e8c780", "y": "b48c4d", "u": "6c5133"},
    "jacket": {"J": "666a7d", "j": "424556", "q": "272935"},
    "lining_grey": {"C": "dfe0e5", "c": "abaeb9", "x": "777b8c"},
    "shirt": {"T": "f6f4ee"},
    "leather": {"L": "7c5745", "l": "4c342b"},
    "trousers": {"P": "74767f", "p": "54565f"},
    "boots": {"D": "5a5d6b", "d": "2a2c36"},
    "eye": {"e": "6f93ad", "E": "1b2132"},
    "mouth": {"m": "b8706c"},
}
P4_EXEMPT = ("ink", "eye", "mouth")    # outline pair and single-feature colours are not lit ramps (as in v8)

# Pixelorama layers bottom to top; they never overlap and their union is the PNG.
ROLE_LAYERS = [("hair-back", "b"), ("boots", "o"), ("legs", "l"), ("torso-jacket", "t"), ("straps-belt", "s"),
               ("radio-kit", "k"), ("arm-tablet", "a"), ("arm-near-radio", "r"), ("head-face", "f"),
               ("hair-front", "h"), ("headset-antenna", "e")]
LAYER_NOTES = {
    "hair-back": "short strand tucked behind the earcup (viewer-right side of the bob)",
    "boots": "black lace-up combat boots, lace zigzag, toe caps, lake-blue sole edge",
    "legs": "baggy charcoal trousers, knee and ankle folds, cargo pocket with brass snap, rolled light-grey cuffs",
    "torso-jacket": "oversized near-black jacket, popped light-grey collar and lapels, white tee, belt, uneven open hem, sleeve patch, snaps",
    "straps-belt": "dark leather crossbody strap with brass buckle (viewer-left shoulder to radio), lake-blue strap hanging on the viewer-left thigh",
    "radio-kit": "hip radio on the viewer-right hip: dark body, brass corners, lake-blue waveform screen, knob, grille; coiled lake-blue cable",
    "arm-tablet": "viewer-left sleeve, rolled cuff, fingerless glove holding a steel-framed tablet with an echo waveform",
    "arm-near-radio": "viewer-right sleeve hanging clear of the waist, rolled cuff, fingerless glove above the radio",
    "head-face": "face, grey-blue eyes, brow, neck",
    "hair-front": "blue-black asymmetric bob: side part, halo sheen, long fringe sweeping over the viewer-left eye, lake-blue under-tips",
    "headset-antenna": "lake-blue headband, one visible steel-rimmed lake-blue earcup (viewer-right), black antenna with brass collar and tip",
    "guides": "hidden + locked: 1-texel cell border, body rows 8/103 ticks, foot pin (40,104)",
}

MAP = [
    "....................................Y...................",  # 8
    "....................................y...................",  # 9
    "....................................k...................",  # 10
    ".........................KKKKKK.....k...................",  # 11
    "......................KhhHHHhBBbK...k...................",  # 12
    "....................KhHHHhhhhhghBbK.k...................",  # 13
    "..................KhHHHhhhhhhhghgbnKk...................",  # 14
    ".................KhHHhhhhhhhHHghhgbny...................",  # 15
    "................KhHHhhhhhhhHHhhghgbnk...................",  # 16
    "...............KhHHhhhhhhhHHhhghggbnk...................",  # 17
    "...............KhHhhhhhhhHHhhghhhgbnk...................",  # 18
    "..............KhHhhhhhhhHHhhhggzsgbnk...................",  # 19
    "..............KhHhhhhhhHHhhggzsSsWwwk...................",  # 20
    "..............KhHhhhhhHHhggzsSssWwwwwK..................",  # 21
    "..............KhHhhhhHHhggzshhhsWBbbwK..................",  # 22
    "..............KhhhhhHHhggzsssssswBbbwK..................",  # 23
    ".............KhhhhhHHhggzEEssEEswbbbwK..................",  # 24
    ".............KhhhhHHhhggzeEssEeswbbnwK..................",  # 25
    ".............KhhghHhhhggzssssssswbnnvK..................",  # 26
    ".............KhhghhhHhhgzSsszsszwwwvvK..................",  # 27
    ".............KhbghbhHhhgzsSsssszhwvvK...................",  # 28
    ".............KbBgbBghbhgzsssssszhKKK....................",  # 29
    ".............KbbgbbgbBhgzssmmszKgK......................",  # 30
    ".............KnbgnbgbbgggzssszK.K.......................",  # 31
    "..............KnKnbgbnbgKKzszK.KccK.....................",  # 32
    "...............K.KnKKnbccKzzzzKcccK.....................",  # 33
    "..................K.KKncccssssccccjKK...................",  # 34
    "................KKKKjCCLlcTsssTCcccxjKKK................",  # 35
    "...............KjjjjjCccLlTTsTTccccxjJJjK...............",  # 36
    ".............KKJjjjqJjCcLlTTTTccccxjjJjJqK..............",  # 37
    "............KJjjjjjqJjcccLlTTTccccxjqjJjjqK.............",  # 38
    "............KJjccjjqJjjCcLlTTTcccxjjqjjjjjqK............",  # 39
    "............KJjxxjjqJjjcccLlTTcccxjjqjjjjjqK............",  # 40
    "............KJjjjjjqJjjjccTLlTccxjjjqjjjjjqK............",  # 41
    "............KJjjqjjqJjjjccTLlTTcxjjjqKjjjjjqK...........",  # 42
    "............KJjjjjjqJjjjqTTTLlTcqqjjqKjjqjjqK...........",  # 43
    "............KJjjjjjqJjjjqTTTLlTcqqjjqKjjjqjqK...........",  # 44
    "............KJjqjjjqJjjjqTTTTYYcqqjjKKjqjjjqK...........",  # 45
    "....KKKKKKK..KJjqqjqJjjjqTTTTyulqqKK.KjjqjqK............",  # 46
    "...KvvvvvvvK.KJjjjjqJjjjqTTTTTLlqyK..KjjjjqK............",  # 47
    "..KvwwwwwwwvKKJjjjjqJjjjqTcTTTTLlqK..KjjjjqKK...........",  # 48
    "..KwqqqqqqqvCCCCCCCCJjjjqTTccTTLlqK..KCCCCCCCK..........",  # 49
    "..KwqqBqqqqvccccccxxJqqqqTTTTTTcLlK..KcccccxxK..........",  # 50
    "..KwqqbqqqqvsssszKKKJJjjqTTTTTTcLlK...KsssszK...........",  # 51
    "..KwqbqBqbqvsssszK.KJjjjqTcTTTTcqLlK..KkkkkkK...........",  # 52
    ".KwqbqqbqqkkkkkKK..KJjjjqTTcTTTcqqLlK.KDddddK...........",  # 53
    ".KwqbqqqbqDddddK...KJjjjkkkYYkkkkqLlK.KDddddK...........",  # 54
    ".KwqqqqqBqDddddK...KJjjjkkkyukkkkqKLlKKdddddK...........",  # 55
    ".KwqqqqqqqDddddK..KjjbnjjjjjjjjjqqpLlKKKsszKK...........",  # 56
    ".KvvvvvvvvvssKK...KjjbnjjjjjjjjjqqqpwwvvvvvvvK..........",  # 57
    "..KvvvvvvvKKK....KjjjbnjjjjjjjjjjjqYqqqqqqqqqyK.........",  # 58
    "...KKKKKKK.......KjjjbnjjjjjjjjjqqqjqnBnnqqWqkK.........",  # 59
    ".................KjjjbnjqqpppppppppjqbnnbqWwqkK.........",  # 60
    ".................KpqqbnqqppppppppppjqnnbnqqwqkK.........",  # 61
    ".................KpPpbnppppppppppppjqqqqqqqqqkK.........",  # 62
    ".................KpPpbnppppppppppppjvkqkqkqqqkK.........",  # 63
    ".................KpPpWwppppppppppppjqqkqkqkqqkK.........",  # 64
    ".................KpPpbnppppppppppppyqqqqqqqqqyK.........",  # 65
    ".................KpPpbnpppppppppppppkkkkkkkkkK..........",  # 66
    ".................KpPpbnppppqqpppppppppqKbnKKK...........",  # 67
    ".................KPppbnpppqKKPPpppppppqKKbnK............",  # 68
    ".................KPppbnpppqKKPPpppppppqKbnK.............",  # 69
    ".................KPppbnpppqKKPPpppqqqqqKKbnK............",  # 70
    "................KPpppbnpppqKKPPpppqPPPqqbnK.............",  # 71
    "................KPpqpbnpppqKKPPqppqpypqqKbnK............",  # 72
    "................KPppqbnpppqKKPPpqqqpppqqbnK.............",  # 73
    "................KPpppbnppqqKKPPpppqpppqqKbnK............",  # 74
    ".................KPppnnpqqK..KPPppqqqqqKbnK.............",  # 75
    ".................KPPPpqqqqK..KPPppppppqKnnK.............",  # 76
    ".................KPPppppqqK..KPPqqppppqKKK..............",  # 77
    "................KPppppppqqK..KPpppppppqK................",  # 78
    "................KPppppppqqK..KPpppppppqK................",  # 79
    "................KPpPPpppqqK..KPpPPppppqK................",  # 80
    "................KPqqppppqqK..KPqqpppppqK................",  # 81
    "...............KPpppppqqqK...KPppppqqqK.................",  # 82
    "...............KPqpppppqqK...KPppppppqK.................",  # 83
    "...............KPpppqqpqqK...KPppqqppqK.................",  # 84
    "...............KPppppppqqK...KPppppppqKK................",  # 85
    "..............KCCCCCCCCCCCK.KCCCCCCCCCCCK...............",  # 86
    "..............KccccccxcccxK.KcccccxccccxK...............",  # 87
    "..............KccccccccccxK.KccccccccccxK...............",  # 88
    "...............KxxxxxxxxxK...KxxxxxxxxxK................",  # 89
    "................KDddddddkK....KDddddddkK................",  # 90
    "................KDddxkddkK....KDddxkddkK................",  # 91
    "................KDddkxdddK....KDddkxdddK................",  # 92
    "................KDddxkdddK....KDddxkdddK................",  # 93
    "................KDddkxdddK....KDddkxdddK................",  # 94
    "................KDddxkdddK....KDddxkdddK................",  # 95
    "................KDddkxdddK....KDddkxdddK................",  # 96
    "...............KDdddddddddK..KDdddddddddK...............",  # 97
    "..............KDDDDdddddddK..KdDDDDdddddK...............",  # 98
    "..............KDDdddddddddK..KdDDdddddddK...............",  # 99
    "..............KdddddddddddK..KddddddddddK...............",  # 100
    "..............KkkkkkkkkkkkK..KkkkkkkkkkkK...............",  # 101
    ".............KbnnnnnnnnnnnK..KbnnnnnnnnnnK..............",  # 102
    "..............KKKKKKKKKKKK....KKKKKKKKKKK...............",  # 103
]

ROLE = [
    "....................................e...................",  # 8
    "....................................e...................",  # 9
    "....................................e...................",  # 10
    ".........................hhhhee.....e...................",  # 11
    "......................hhhhhhheeee...e...................",  # 12
    "....................hhhhhhhhhhhheee.e...................",  # 13
    "..................hhhhhhhhhhhhhhheeee...................",  # 14
    ".................hhhhhhhhhhhhhhhhheee...................",  # 15
    "................hhhhhhhhhhhhhhhhhheee...................",  # 16
    "...............hhhhhhhhhhhhhhhhhhheee...................",  # 17
    "...............hhhhhhhhhhhhhhhhhhheee...................",  # 18
    "..............hhhhhhhhhhhhhhhhhffheee...................",  # 19
    "..............hhhhhhhhhhhhhhhffffeeee...................",  # 20
    "..............hhhhhhhhhhhhhfffffeeeeee..................",  # 21
    "..............hhhhhhhhhhhhffffffeeeeee..................",  # 22
    "..............hhhhhhhhhhhfffffffeeeeee..................",  # 23
    ".............hhhhhhhhhhhffffffffeeeeee..................",  # 24
    ".............hhhhhhhhhhhffffffffeeeeee..................",  # 25
    ".............hhhhhhhhhhhffffffffeeeeee..................",  # 26
    ".............hhhhhhhhhhhffffffffeeeeee..................",  # 27
    ".............hhhhhhhhhhhffffffffbeeee...................",  # 28
    ".............hhhhhhhhhhhffffffffbbee....................",  # 29
    ".............hhhhhhhhhhhfffffffbbb......................",  # 30
    ".............hhhhhhhhhhhhffffff.t.......................",  # 31
    "..............hhhhhhhhhhhfffff.tttt.....................",  # 32
    "...............h.hhhhhhttfffffttttt.....................",  # 33
    "..................h.thhtttffffttttttt...................",  # 34
    "................aaattttssttfffttttttttrr................",  # 35
    "...............aaaaattttssttfttttttttrrrr...............",  # 36
    ".............aaaaaaattttsstttttttttttrrrrr..............",  # 37
    "............aaaaaaaatttttssttttttttttrrrrrr.............",  # 38
    "............aaaaaaaatttttssttttttttttrrrrrrr............",  # 39
    "............aaaaaaaattttttsstttttttttrrrrrrr............",  # 40
    "............aaaaaaaatttttttssttttttttrrrrrrr............",  # 41
    "............aaaaaaaatttttttssttttttttrrrrrrrr...........",  # 42
    "............aaaaaaaattttttttsstttttttrrrrrrrr...........",  # 43
    "............aaaaaaaattttttttsstttttttrrrrrrrr...........",  # 44
    "............aaaaaaaatttttttttssttttttrrrrrrrr...........",  # 45
    "....aaaaaaa..aaaaaaatttttttttssstttt.rrrrrrr............",  # 46
    "...aaaaaaaaa.aaaaaaattttttttttssttt..rrrrrrr............",  # 47
    "..aaaaaaaaaaaaaaaaaatttttttttttsstt..rrrrrrrr...........",  # 48
    "..aaaaaaaaaaaaaaaaaatttttttttttsstt..rrrrrrrrr..........",  # 49
    "..aaaaaaaaaaaaaaaaaattttttttttttsss..rrrrrrrrr..........",  # 50
    "..aaaaaaaaaaaaaaaaatttttttttttttsss...rrrrrrr...........",  # 51
    "..aaaaaaaaaaaaaaaa.ttttttttttttttsss..rrrrrrr...........",  # 52
    ".aaaaaaaaaaaaaaaa..tttttttttttttttsss.rrrrrrr...........",  # 53
    ".aaaaaaaaaaaaaaa...tttttttttttttttsss.rrrrrrr...........",  # 54
    ".aaaaaaaaaaaaaaa...tttttttttttttttssssrrrrrrr...........",  # 55
    ".aaaaaaaaaaaaaaa..tttsstttttttttttlssskrrrrrk...........",  # 56
    ".aaaaaaaaaaaaaa...tttssttttttttttttlkkkkkkkkkk..........",  # 57
    "..aaaaaaaaaaa....ttttssttttttttttttkkkkkkkkkkkk.........",  # 58
    "...aaaaaaa.......ttttssttttttttttttkkkkkkkkkkkk.........",  # 59
    ".................ttttsstttlllllllllkkkkkkkkkkkk.........",  # 60
    ".................llttssttllllllllllkkkkkkkkkkkk.........",  # 61
    ".................llllssllllllllllllkkkkkkkkkkkk.........",  # 62
    ".................llllssllllllllllllkkkkkkkkkkkk.........",  # 63
    ".................llllssllllllllllllkkkkkkkkkkkk.........",  # 64
    ".................llllssllllllllllllkkkkkkkkkkkk.........",  # 65
    ".................llllsslllllllllllllkkkkkkkkkk..........",  # 66
    ".................llllssllllllllllllllllkkkkkk...........",  # 67
    ".................llllsslllllllllllllllllkkkk............",  # 68
    ".................llllssllllllllllllllllkkkk.............",  # 69
    ".................llllsslllllllllllllllllkkkk............",  # 70
    "................lllllsslllllllllllllllllkkk.............",  # 71
    "................lllllsslllllllllllllllllkkkk............",  # 72
    "................lllllsslllllllllllllllllkkk.............",  # 73
    "................lllllsslllllllllllllllllkkkk............",  # 74
    ".................llllssllll..llllllllllkkkk.............",  # 75
    ".................llllllllll..llllllllllkkkk.............",  # 76
    ".................llllllllll..lllllllllllkk..............",  # 77
    "................lllllllllll..lllllllllll................",  # 78
    "................lllllllllll..lllllllllll................",  # 79
    "................lllllllllll..lllllllllll................",  # 80
    "................lllllllllll..lllllllllll................",  # 81
    "...............lllllllllll...llllllllll.................",  # 82
    "...............lllllllllll...llllllllll.................",  # 83
    "...............lllllllllll...llllllllll.................",  # 84
    "...............lllllllllll...lllllllllll................",  # 85
    "..............lllllllllllll.lllllllllllll...............",  # 86
    "..............lllllllllllll.lllllllllllll...............",  # 87
    "..............lllllllllllll.lllllllllllll...............",  # 88
    "...............lllllllllll...lllllllllll................",  # 89
    "................oooooooooo....oooooooooo................",  # 90
    "................oooooooooo....oooooooooo................",  # 91
    "................oooooooooo....oooooooooo................",  # 92
    "................oooooooooo....oooooooooo................",  # 93
    "................oooooooooo....oooooooooo................",  # 94
    "................oooooooooo....oooooooooo................",  # 95
    "................oooooooooo....oooooooooo................",  # 96
    "...............oooooooooooo..oooooooooooo...............",  # 97
    "..............ooooooooooooo..oooooooooooo...............",  # 98
    "..............ooooooooooooo..oooooooooooo...............",  # 99
    "..............ooooooooooooo..oooooooooooo...............",  # 100
    "..............ooooooooooooo..oooooooooooo...............",  # 101
    ".............oooooooooooooo..ooooooooooooo..............",  # 102
    "..............oooooooooooo....ooooooooooo...............",  # 103
]

SPEC = fmt.make_spec(REPO, MAP, ROLE, RAMPS, ROLE_LAYERS, "zhao-ling-south-idle-static-pilot-v01", ZIP_DT, P4_EXEMPT)
PAL = SPEC["PAL"]
W, H, GRID_W, GRID_H, OX, OY = fmt.W, fmt.H, fmt.GRID_W, fmt.GRID_H, fmt.GRID_OFFSET[0], fmt.GRID_OFFSET[1]


def fid(role):
    return hashlib.sha256(f"{RUN_ID}:{role}".encode()).hexdigest()[:8]


NAMES = {
    "png": f"{SLUG}_{VISUAL_ID}_{SUBJECT}_{VARIANT}_{STAMP}-{fid('png')}.png",
    "pxo": f"{SLUG}_{VISUAL_ID}_{SUBJECT}-editable_{VARIANT}_{STAMP}-{fid('pxo')}.pxo",
    "ora": f"{SLUG}_{VISUAL_ID}_{SUBJECT}-editable-layers_{VARIANT}_{STAMP}-{fid('ora')}.ora",
    "palette": f"{SLUG}_{VISUAL_ID}_{SUBJECT}-palette_{VARIANT}_{STAMP}-{fid('palette')}.json",
    "manifest": f"{SLUG}_{VISUAL_ID}_{SUBJECT}-manifest_{VARIANT}_{STAMP}-{fid('manifest')}.json",
}
TOOL_REL = "tools/" + os.path.basename(os.path.abspath(__file__))


def rp(rel):
    return fmt.repo_path(REPO, rel)


# ============================================================================ identity metrics (report only)
def cells(pred):
    return [(x + OX, y + OY) for y in range(GRID_H) for x in range(GRID_W)
            if MAP[y][x] != "." and pred(MAP[y][x], ROLE[y][x], x + OX, y + OY)]


def bbox(t):
    xs = [p[0] for p in t]; ys = [p[1] for p in t]
    return {"x": [min(xs), max(xs)], "y": [min(ys), max(ys)], "w": max(xs) - min(xs) + 1, "h": max(ys) - min(ys) + 1,
            "texels": len(t)}


def head_iou(other):
    """IoU of opaque texels in cell rows 8..35 (head + hair + headset) at the same pin; report only."""
    if other is None:
        return None
    a = fmt.compose(SPEC)[8:36, :, 3] > 0
    b = other[8:36, :, 3] > 0
    return round(float((a & b).sum()) / float((a | b).sum()), 3)


def legibility():
    hair = cells(lambda k, r, x, y: r in "hb" and k != "K")
    face = cells(lambda k, r, x, y: r == "f" and k in "sSz" and y <= 32)
    fx0 = min(p[0] for p in face); fx1 = max(p[0] for p in face); fc = (fx0 + fx1) / 2
    left_hair = [p for p in hair if p[0] < fc]; right_hair = [p for p in hair if p[0] > fc]
    crown = min(p[1] for p in hair)
    tips = cells(lambda k, r, x, y: r == "h" and k in "bBn")
    cup = cells(lambda k, r, x, y: r == "e" and 20 <= y <= 29 and x >= 44 and k != "K")
    band = cells(lambda k, r, x, y: r == "e" and k in "bBn" and y < 20)
    antenna = cells(lambda k, r, x, y: r == "e" and x == 48 and y <= 20)
    radio = cells(lambda k, r, x, y: r == "k" and y <= 66 and k != "K")
    cable = cells(lambda k, r, x, y: r == "k" and y >= 67 and k in "bBn")
    legs_right = max(p[0] for p in cells(lambda k, r, x, y: r == "l" and 58 <= y <= 66))
    tablet = cells(lambda k, r, x, y: r == "a" and x <= 23 and k != "K")
    sleeve_left = min(p[0] for p in cells(lambda k, r, x, y: r == "a" and x >= 24 and 38 <= y <= 50 and k != "K"))
    wave = [p for p in tablet if MAP[p[1] - OY][p[0] - OX] in "bB"]
    strap = cells(lambda k, r, x, y: r == "s" and k in "Ll")
    thigh_strap = cells(lambda k, r, x, y: r == "s" and x <= 35 and y >= 56 and k != "K")
    soles = cells(lambda k, r, x, y: r == "o" and k in "bn")

    def gap_rows(y0, y1, xa, xb):
        out = []
        for y in range(y0, y1 + 1):
            row = MAP[y - OY]
            if any(row[x - OX] == "." for x in range(xa, xb + 1)):
                out.append(y)
        return out
    arm_gap = gap_rows(44, 58, 47, 48)
    leg_gap = gap_rows(68, 103, 39, 40)
    lab = lambda k: fmt.hex_rgb(PAL[k])
    v8 = fmt.v8_rgba(REPO)
    liang_p = rp(REFS["confusion_pair_liang_xu_static_pilot_png"][0])
    liang = fmt.decode(fmt.read_bytes(liang_p)) if os.path.isfile(fmt.fs(liang_p)) else None
    return {
        "note": "cell coordinates; 1 texel = 1 window px at 1280x720 (0.5 scale on the 640x360 canvas)",
        "asymmetric_bob": {
            "face_x": [fx0, fx1], "crown_row": crown,
            "hair_extends_left_of_face_px": fx0 - min(p[0] for p in left_hair),
            "hair_extends_right_of_face_px": max(p[0] for p in right_hair) - fx1,
            "lowest_hair_row_fringe_side": max(p[1] for p in left_hair),
            "lowest_hair_row_tucked_side": max(p[1] for p in right_hair),
            "fringe_covers_face_columns_at_eye_row": "cells 26-35 hair, eyes at cells 37-38 and 41-42 (row 24-25)",
        },
        "blue_tips": {"texels": len(tips), "rows": [min(p[1] for p in tips), max(p[1] for p in tips)],
                      "dE76_tip_blue_vs_hair": round(fmt.de76(lab("b"), lab("h")), 1)},
        "earcup": {**bbox(cup), "lake_blue_texels": sum(1 for p in cup if MAP[p[1] - OY][p[0] - OX] in "bBn"),
                   "dE76_cup_blue_vs_hair": round(fmt.de76(lab("b"), lab("h")), 1)},
        "headband_texels_above_cup": len(band),
        "antenna": {"column": 48, "rows": [min(p[1] for p in antenna), max(p[1] for p in antenna)],
                    "rise_above_crown_px": crown - min(p[1] for p in antenna),
                    "brass_texels": sum(1 for p in antenna if MAP[p[1] - OY][p[0] - OX] in "Yy")},
        "hip_radio": {**bbox(radio), "protrudes_past_trousers_px": max(p[0] for p in radio) - legs_right,
                      "screen_texels": sum(1 for p in radio if MAP[p[1] - OY][p[0] - OX] in "bBn")},
        "coiled_cable": bbox(cable),
        "tablet": {**bbox(tablet), "protrudes_past_sleeve_px": sleeve_left - min(p[0] for p in tablet),
                   "waveform_texels": len(wave)},
        "crossbody_strap": bbox(strap),
        "thigh_strap_lake_blue": bbox(thigh_strap),
        "boot_sole_lake_blue_texels": len(soles),
        "viewer_right_arm_gap_rows": arm_gap,
        "leg_gap_rows": [leg_gap[0], leg_gap[-1]] if leg_gap else [],
        "accent_family": {"dE76_lake_blue_b_vs_v8_teal_249b98": round(fmt.de76(lab("b"), fmt.hex_rgb("249b98")), 1),
                          "dE76_lake_blue_b_vs_v8_teal_1a767b": round(fmt.de76(lab("b"), fmt.hex_rgb("1a767b")), 1)},
        "value_separation": {"dE76_hair_h_vs_jacket_j": round(fmt.de76(lab("h"), lab("j")), 1),
                             "dE76_jacket_j_vs_trousers_p": round(fmt.de76(lab("j"), lab("p")), 1)},
        "head_rows_8_35_iou_report_only": {"vs_female_v8": head_iou(v8), "vs_liang_xu_pilot": head_iou(liang)},
    }


# ============================================================================ outputs
def palette_json():
    p = {"project": "Worlds Between", "visual_id": VISUAL_ID,
         "purpose": "declared named ramps for the Zhao Ling south idle static pilot v01", "art_approved": False,
         "ramps": {name: [{"key": k, "hex": "#" + v} for k, v in ramp.items()] for name, ramp in RAMPS.items()},
         "p4_exempt": list(P4_EXEMPT), "light": "upper left", "colour_count": len(PAL)}
    return (json.dumps(p, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def manifest_json(png, pxo, ora, pal, full):
    refs = {}
    for k, (rel, kind) in REFS.items():
        h, alg = fmt.ref_hash(REPO, rel, kind)
        refs[k] = {"file": rel, "sha256": h, "hash_algorithm": alg}
    layers = [{"pixelorama_layer": i, "name": n, "visible": True, "locked": False,
               "texels": int((fmt.compose(SPEC, k)[..., 3] > 0).sum()), "note": LAYER_NOTES[n]}
              for i, (n, k) in enumerate(ROLE_LAYERS, start=1)]
    layers.append({"pixelorama_layer": len(SPEC["LAYERS"]), "name": "guides", "visible": False, "locked": True,
                   "note": LAYER_NOTES["guides"]})
    m = {
        "project": "Worlds Between", "milestone": "M8", "visual_id": VISUAL_ID,
        "identity": "Zhao Ling 赵铃, science-district companion (bible entry 31: female, 26, firearms job series, city radio repair technician)",
        "purpose": "First south-facing exploration idle STATIC identity pilot for Zhao Ling at the approved 48 logical px, "
                   "hand-placed in the female selout v8 format, before any animation or other direction.",
        "status": "UNAPPROVED, NONRUNTIME pilot; technical gates only; not runtime-integrated; no animation; south only",
        "art_approved": False, "human_reviewed": False, "runtime_integrated": False, "variant": VARIANT, "run_id": RUN_ID,
        "acceptance_counters_unchanged": {"runtime_sprites_accepted": "0/52"},
        "authorship": "Colour and role grids placed by Claude (Claude Code, signed-in Claude Max). Masses seeded by a "
                      "scratch primitive script (not shipped); head, hair locks, blue tips, earcup, chin/collar rows and "
                      "body details hand-typed; judged on x3/x6 previews over city / annex floor colours. The literal "
                      "grids in the tool are the only source. No image generation, resampling, filtering, quantization "
                      "or dithering. The 2026-10-14 32x48 runtime body and the premium concept were not reused.",
        "benchmark": {"female_selout_v8": "density / proportion / value-separation benchmark only (same 80x112 cell, "
                      "pin, 96-texel body, 0.5 scale, 1-texel outer ink); no v8 texel, palette entry or design element is copied."},
        "source_identity_references": {
            "sheet": REFS["identity_sheet_zhao_ling"][0] + " (1916x821)",
            "front_full_body_view": "sheet x~30-400: asymmetric bob, earcup + antenna on her left ear (viewer-right), oversized near-black jacket with light-grey collar and rolled cuffs, white tee, crossbody straps, hip radio on viewer-right hip with coiled cable, tablet in her right hand (viewer-left), fingerless gloves, baggy charcoal trousers with rolled grey cuffs and hanging blue straps, black lace-up boots with blue-grey soles",
            "head_close_ups": "sheet x~870-1580, y~0-370: side part, long fringe over her right eye (viewer-left), blue inner tips at the jaw, grey-blue eyes, steel-rimmed teal-blue earcups, black antenna with brass tip; hand raised to the earcup",
            "chibi_turnarounds": "sheet x~1380-1916, y~480-740: front view shows one visible earcup (viewer-right) with the antenna rising from it; back view shows a radio pack",
            "radio_prop_detail": "sheet x~830-1350, y~340-800: black/brass radio with waveform screen, knob, antenna, tool tray, strap",
            "bible": "outputs/...remaining-companions_character-bible...md entry 31: 湖蓝耳机、整齐的侧分短发和便携天线; city radio repair technician; personal skill 回声测距 (Echo Ranging)",
        },
        "identity_cues_kept": [
            "asymmetric chin-length blue-black bob: side part, long fringe swept over the viewer-left eye, wider fringe side, tucked side behind the earcup",
            "lake-blue inner tips at the jaw on the fringe side (three strands)",
            "one visible lake-blue earcup with steel rim on the viewer-right ear, headband over the crown",
            "narrow vertical black antenna with brass collar and tip rising from the earcup above the crown",
            "oversized near-black jacket with popped light-grey collar/lapels and rolled light-grey cuffs over a white tee",
            "dark crossbody strap with brass buckle from the viewer-left shoulder to a hip radio on the viewer-right hip",
            "hip radio with brass corners, lake-blue waveform screen and knob; coiled lake-blue cable",
            "tablet held in the viewer-left fingerless-gloved hand",
            "baggy charcoal trousers with rolled light-grey cuffs, a lake-blue strap hanging on the viewer-left thigh, cargo pocket",
            "black lace-up combat boots with lake-blue sole edge",
        ],
        "proposed_pixel_simplifications_vs_source": [
            "Pose: the sheet's hand-to-earcup gesture is replaced by a neutral idle (viewer-right arm hanging above the radio, viewer-left hand holding the tablet at the hip) so the earcup and antenna stay unoccluded and the frame can seed walk cycles.",
            "Tablet: shown as a steel-framed slate with a lake-blue echo waveform facing the viewer (the sheet shows its dark back); the waveform echoes the radio screen and Echo Ranging so it does not read as Liang Xu's copper board.",
            "Accent colour: the sheet's muted steel-teal is pushed to a brighter lake blue (湖蓝, bible wording) for 1 texel/px legibility and to separate it from v8's green-teal scarf.",
            "Jacket is lifted from near-black to a dark cool charcoal with lit planes so it separates from the blue-black hair and dark floors; trousers are one step lighter than the jacket.",
            "Gear reduced: multiple crossbody straps -> one leather strap; the viewer-left hip tool pouch with vials, the thigh holster pouches and the second hanging strap are omitted; one cargo pocket remains.",
            "Hip radio reduced to a 11x10 box (no tool tray, no prop antenna); cable shown as one 2-texel coil.",
            "Viewer-left earcup is hidden by the fringe, as in the sheet's front and chibi front views (one visible earcup).",
            "Face: 2-texel eyes, 1-texel nose shadow and 2-texel mouth; the sheet's eye shape and lashes are not representable at 48 px.",
        ],
        "name_note": "Canonical name is 赵铃 / Zhao Ling (character bible, Game Bible state, asset inventory, app strings). 赵羚 in the dispatch brief was a coordinator typo; it is not a creator question.",
        "decided_for_this_south_static": [
            "Weapon: the sheet shows no firearm, so none is drawn (the firearms job series does not require one in this exploration idle).",
        ],
        "pending_for_later_directions_only": [
            "Back radio pack vs hip radio construction (the sheet's back view shows a pack with its own antenna); needed for north/side facings, not for this south static.",
        ],
        "cell": {"w": W, "h": H, "pin": list(fmt.PIN), "body_rows": list(fmt.BODY_ROWS), "display_scale": fmt.DISPLAY_SCALE,
                 "display_logical_height": 48, "filter": "nearest", "alpha": "binary", "grid_offset": list(fmt.GRID_OFFSET),
                 "height_rule": "visible height 96 texels includes the antenna tip (row 8); hair crown at row 11, close to v8's crown"},
        "files": {
            "png": {"file": f"{OUT_DIR_REL}/{NAMES['png']}", "sha256": fmt.sha256_bytes(png), "hash_algorithm": "sha256-bytes",
                    "role": "transparent static PNG candidate (not wired into the game)"},
            "pxo": {"file": f"{OUT_DIR_REL}/{NAMES['pxo']}", "sha256": fmt.sha256_bytes(pxo), "hash_algorithm": "sha256-bytes",
                    "format": f"Pixelorama pxo_version 7 ({fmt.PIXELORAMA_VERSION}), color_mode 5, 1 frame x {len(SPEC['LAYERS'])} layers, fixed zip timestamps"},
            "ora": {"file": f"{OUT_DIR_REL}/{NAMES['ora']}", "sha256": fmt.sha256_bytes(ora), "hash_algorithm": "sha256-bytes",
                    "format": "OpenRaster 0.0.3, same layers as the .pxo (guides hidden), mergedimage = the PNG"},
            "palette": {"file": f"{OUT_DIR_REL}/{NAMES['palette']}", "sha256": fmt.text_sha256_lf(pal), "hash_algorithm": "sha256-text-lf-v1"},
            "gdignore": f"{OUT_DIR_REL}/.gdignore",
        },
        "layers_bottom_to_top": layers,
        "references": refs,
        "gates": fmt.gates(SPEC, full),
        "legibility_metrics_report_only": legibility(),
        "tool": {"file": TOOL_REL, "sha256": fmt.text_sha256_lf(fmt.read_bytes(os.path.abspath(__file__))),
                 "hash_algorithm": "sha256-text-lf-v1", "python": sys.version.split()[0], "pillow": Image.__version__,
                 "numpy": np.__version__, "run_flags": "-I -B"},
        "shared_format_module": {"file": SHARED_REL, "sha256": fmt.text_sha256_lf(fmt.read_bytes(rp(SHARED_REL))),
                                 "hash_algorithm": "sha256-text-lf-v1"},
    }
    return (json.dumps(m, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def build():
    full, png, pxo, ora, _ = fmt.artifacts(SPEC)
    if (png, pxo, ora) != fmt.artifacts(SPEC)[1:4]:
        raise SystemExit("build is not deterministic")
    g = fmt.gates(SPEC, full)
    bad = [k for k in fmt.HARD_GATES if not g[k]]
    if bad:
        raise SystemExit(f"hard gates failed: {bad} {g}")
    out = rp(OUT_DIR_REL)
    os.makedirs(fmt.fs(out), exist_ok=True)
    print(fmt.write_new(os.path.join(out, ".gdignore"), b""), ".gdignore")
    pal = palette_json()
    for key, data in (("png", png), ("pxo", pxo), ("ora", ora)):
        print(fmt.write_new(os.path.join(out, NAMES[key]), data), NAMES[key], fmt.sha256_bytes(data))
    print(fmt.write_new(os.path.join(out, NAMES["palette"]), pal, text=True), NAMES["palette"])
    man = manifest_json(png, pxo, ora, pal, full)
    print(fmt.write_new(os.path.join(out, NAMES["manifest"]), man, text=True), NAMES["manifest"],
          fmt.text_sha256_lf(man), "(sha256-text-lf-v1)")


def check(exe):
    full, png, pxo, ora, blobs = fmt.artifacts(SPEC)
    out = rp(OUT_DIR_REL)
    disk = {k: fmt.read_bytes(os.path.join(out, NAMES[k])) for k in ("png", "pxo", "ora", "palette", "manifest")}
    man = json.loads(disk["manifest"])
    v8_p = rp(fmt.V8_REL)
    rep = {"files_equal_rebuild": {"png": disk["png"] == png, "pxo": disk["pxo"] == pxo, "ora": disk["ora"] == ora,
                                   "palette": fmt.text_sha256_lf(disk["palette"]) == fmt.text_sha256_lf(palette_json()),
                                   "manifest": fmt.text_sha256_lf(disk["manifest"]) == fmt.text_sha256_lf(
                                       manifest_json(png, pxo, ora, palette_json(), full))},
           "manifest_file_hashes_match": all(man["files"][k]["sha256"] == fmt.sha256_bytes(disk[k]) for k in ("png", "pxo", "ora")),
           "manifest_reference_hashes_current": {k: fmt.ref_hash(REPO, v["file"], "bytes" if v["hash_algorithm"] == "sha256-bytes" else "text")[0] == v["sha256"]
                                                 for k, v in man["references"].items()},
           "v8_source_unchanged": fmt.sha256_bytes(fmt.read_bytes(v8_p)) == fmt.V8_SHA256,
           "png_decodes_to_maps": fmt.decode(disk["png"]).tobytes() == full.tobytes(),
           "gates": fmt.gates(SPEC, full), "legibility": legibility()}
    rep.update(fmt.container_checks(SPEC, exe, disk, full, blobs))
    g = rep["gates"]
    ok = (all(rep["files_equal_rebuild"].values()) and rep["manifest_file_hashes_match"]
          and all(rep["manifest_reference_hashes_current"].values()) and rep["v8_source_unchanged"]
          and rep["png_decodes_to_maps"] and all(g[k] for k in fmt.HARD_GATES) and rep["pass"])
    rep["result"] = "PASS" if ok else "FAIL"
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    return 0 if ok else 1


def preview(path):
    full = fmt.artifacts(SPEC)[0]
    Image.fromarray(full, "RGBA").resize((W * 4, H * 4), Image.NEAREST).save(fmt.fs(path))
    print(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=["build", "check", "preview"])
    ap.add_argument("out", nargs="?")
    ap.add_argument("--pixelorama", default=rp(fmt.PIXELORAMA_REL))
    a = ap.parse_args()
    if a.mode == "build":
        build(); return 0
    if a.mode == "preview":
        if not a.out:
            raise SystemExit("preview needs an output path")
        preview(a.out); return 0
    if not os.path.isfile(a.pixelorama):
        raise SystemExit(f"Pixelorama not found: {a.pixelorama}")
    return check(os.path.abspath(a.pixelorama))


if __name__ == "__main__":
    sys.exit(main())
