"""Female protagonist NORTH-facing exploration idle STATIC pilot (UNAPPROVED, NONRUNTIME): one hand-placed 80x112
back-view cell matched to the creator-approved south idle selout v8 at 48 logical px, with an editable Pixelorama
.pxo + layered .ora (13 role layers + hidden guides) and a manifest. One missing direction toward the four-direction
set; not a new south iteration, not battle, not motion, not a sprite-set or runtime approval.

Matched to v8 (read only, SHA-256 locked): same 80x112 cell, foot pin (40,104), sole row 103, 96-texel body (rows
8..103 -> 48 logical px at scale 0.5), binary alpha, 1-texel outer ink with v8's selout colours (legs C, boots F,
teal S, else A), light from the screen's upper left, and only colours taken from v8's own 32-colour palette (the
gate decodes v8 and requires the north colours to be a subset). No v8 texel is copied, mirrored or resampled.

Back view, built from the 21:9 identity sheet's back view plus v8 (see EVIDENCE): ponytail tied at the crown,
rising and falling clear of the head on the viewer right (the character's right, the side v8's plume falls on);
coat collar at the nape; teal bedroll across the shoulders with its long end past the character's left shoulder (as
in v8); warm pack with the community diamond and two leather straps with steel buckles; steel canister on the pack's
character-left side (v8's side; the sheet's back view shows it on the other side, see EVIDENCE); storm-slate sleeves
with rolled cream cuffs, bare forearms, fingerless gloves; teal scarf tail hanging on the character's right (v8 and
the sheet's back view agree); storm-slate coat skirt with a centre back vent; spruce trousers with a knee strap on
the character's right leg; warm leather boots seen from the heel. Arms hang relaxed as in the sheet's back view
(v8's hand-on-hip is a front-only pose here; recorded as an identity decision in the QA note).

Source of truth: MAP (v8 colour keys) and ROLE (role-layer keys) below, literal 56x96 grids placed at cell offset
(12, 8). They were placed in a scratch layer script judged on x2/x5 previews next to v8 over city / annex /
outskirts floor colours; only these literal grids ship. No image generation, resampling, filtering, quantization or
dithering was used.

Helpers (paths, hashes, v8 source gate, Pixelorama path/version) are imported from the tracked v8 .pxo round-trip
tool, which is hash-locked here and only read.

Modes (real Python, isolated):
  python -I -B <this file> build                  write PNG, .pxo, .ora, manifest (never overwrites)
  python -I -B <this file> check [--pixelorama X]  gates + rebuild equality + Pixelorama CLI .pxo/.ora round trips
                                                  (APPDATA redirected to a temp dir) + v8 files unchanged
"""
import argparse, hashlib, importlib.util, io, json, os, shutil, subprocess, sys, tempfile, zipfile
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
V8_TOOL_REL = "tools/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-pxo-source-roundtrip_m8-v08_20261015-080907-05c22e55.py"
V8_TOOL_SHA256 = "53d492fb9e4a7cbd9cdc8991a105140cd8a23aa507040d888993310323754f73"   # sha256-text-lf-v1


def _load_v8_tool():
    path = os.path.join(REPO, *V8_TOOL_REL.split("/"))
    with open(path, "rb") as f:
        if hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest() != V8_TOOL_SHA256:
            raise SystemExit("v8 round-trip tool changed; refusing to import it")
    spec = importlib.util.spec_from_file_location("v8_pxo_roundtrip", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


v8t = _load_v8_tool()
_fs, repo_path, read_bytes = v8t._fs, v8t.repo_path, v8t.read_bytes
sha256_bytes, text_sha256_lf, write_new = v8t.sha256_bytes, v8t.text_sha256_lf, v8t.write_new
W, H, PIN, BODY_ROWS = v8t.W, v8t.H, v8t.PIN, v8t.BODY_ROWS
PIXELORAMA_REL, PIXELORAMA_VERSION = v8t.PIXELORAMA_REL, v8t.PIXELORAMA_VERSION

SLUG = "rpg-2-star-ocean-the-second"
VISUAL_ID = "protagonist-female"
SUBJECT = "north-idle-static-pilot"
VARIANT = "unapproved-v01"
STAMP = "20261018-090713"
RUN_ID = "97156e89"
GRID_W, GRID_H = 56, 96
GRID_OFFSET = (12, 8)
DISPLAY_SCALE = 0.5
OUT_DIR_REL = "game/assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01"
GUIDE_RGB = (255, 0, 255)
ZIP_DT = (2026, 10, 18, 9, 7, 12)
GUI_OWNED = (".running", "backups/")     # an open GUI's heartbeat / autosaves; never written by these CLI runs

# Read-only references; check requires them unchanged (v8 files are also the approval lock).
REFS = {
    "v8_png": (v8t.V8_REL, "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd", "bytes"),
    "v8_manifest": ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-manifest_m8-v08_20261015-021600-2d6c5eff.json",
                    "3ba35811bf4d55b061b7719c6451908bdbb1eb68425bdda2c2303cc669f310ed", "text"),
    "v8_pxo": ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-editable_m8-v08_20261015-080907-c8a1c140.pxo",
               "cafa4998b107ae4b884cc877b80bbc695df267f37e09fb6e69701567f08a849e", "bytes"),
    "v8_pxo_manifest": ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-editable-manifest_m8-v08_20261015-080907-270b2256.json",
                        "d40059be868e50f6acbea509e14dd2e8ccd6cac3b1405f39399c9fbff17e73c3", "text"),
    "v8_qa_note": ("docs/qa/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8_visual-qa-note_m8-v08_20261015-021600-c1694107.md",
                   "ff922d31e23557774c85102b3bbc1ff4818236b45b51f99f88ef19e2fa7d8d04", "text"),
    "v8_decision": ("docs/character-visuals/rpg-2-star-ocean-the-second_protagonist-female_south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md",
                    "f7ea59b73de35a9c71a7d6dc4968ebbd4b2ce28458fa926877222d85591d7c37", "text"),
    "v8_pxo_roundtrip_qa_note": ("docs/qa/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-pxo-source_headless-roundtrip_qa-note_m8-v08_20261015-080907-599b83ff.md",
                                 "d73777b1171107f9d534485975dcf1086ef513e37d8189789f770a655d126aa3", "text"),
    "v8_pxo_roundtrip_tool": (V8_TOOL_REL, V8_TOOL_SHA256, "text"),
    "identity_sheet_female": ("outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_female_20261013-153316-8fa4d0c3.png",
                              "3d876c4f666913d6110fe8a058b79a55ce82ac225577d87f1f02624affeea58d", "bytes"),
}

# v8's own palette entries (keys as in the v8 QA dump); the gate also proves each is a v8 colour.
PAL = {"A": "0a0a0e", "B": "533b32", "C": "222839", "D": "3a4560", "E": "324542", "F": "302526", "G": "1a767b",
       "H": "41302b", "I": "b09986", "J": "714730", "K": "845436", "L": "634739", "M": "11525b", "N": "d7c0a8",
       "O": "4a625c", "P": "5e6e8c", "Q": "201c20", "R": "fbc38d", "S": "0a323b", "T": "e39664", "U": "cfc8bd",
       "V": "a16f4b", "W": "bb7c50", "X": "faead4", "Y": "7e5f4a", "Z": "23252b", "b": "474b54", "c": "249b98",
       "d": "30333a", "e": "626873"}
MATERIAL = {"ink": "AQZ", "brown hair / leather / pack": "BFHJKLVY", "storm-slate coat": "PDC", "spruce trousers": "OE",
            "teal (bedroll, scarf tail, emblem)": "cGMS", "cream cuffs / emblem frame": "XNIU", "skin": "RTW",
            "steel (canister, buckles)": "bde"}

# Role layers, Pixelorama layer 1 = bottom. Outer-ink texels belong to the part they outline.
ROLE_LAYERS = [("legs", "l"), ("boots", "o"), ("coat", "c"), ("scarf-tail", "s"), ("arm-left", "m"),
               ("arm-right", "n"), ("pack", "p"), ("canister", "k"), ("straps", "z"), ("bedroll", "r"),
               ("collar", "q"), ("hair", "h"), ("ponytail", "t")]
LAYERS = [n for n, _ in ROLE_LAYERS] + ["guides"]

# Which back details are direct evidence and which are proposed (the sheet's back view = sheet-back).
EVIDENCE = {
    "ponytail": ("sheet-back + v8", "high ponytail tied at the crown (sheet back view); plume rising then falling on the "
                 "character's right with wisp tips, mirrored in screen space from v8's plume. The exact arc, the clear gap "
                 "beside the head and the wisp tips are proposed 48 px construction"),
    "hair": ("sheet-back + v8", "dark-brown back of the head with loose locks reaching the collar (sheet back view), v8's "
             "hair ramp; lock clusters, sheen and crown tie placement are proposed"),
    "collar": ("sheet-back", "bunched collar / hood at the nape (sheet back view), drawn in v8's storm-slate coat colours "
               "because v8 recoloured the coat; the sheet's grey-brown hood colour is not used"),
    "bedroll": ("sheet-back + v8", "teal roll across the top of the pack (sheet back view); long end past the character's "
                "left shoulder (v8 shows that end); spiral end cap is proposed"),
    "pack": ("sheet-back", "warm pack body with flap, teal community diamond and lower pocket (sheet back view and pack "
             "detail panel); v8 shows only the bedroll and strap edges, so pack proportions at 48 px are proposed"),
    "straps": ("sheet-back + v8", "two leather straps with steel buckles (sheet back view); v8 shows the shoulder straps"),
    "canister": ("v8 (conflicts with sheet-back)", "steel canister on the character's LEFT, as in v8 (viewer right in the "
                 "south frame); the sheet's back view puts it on the character's right. v8 is the approved baseline, so "
                 "v8's side is kept for turn consistency"),
    "arm-left": ("sheet-back + v8", "storm-slate sleeve, rolled cream cuff, bare forearm, fingerless glove (sheet; v8 "
                 "colours); arms hang relaxed as in the sheet's back view, not v8's hand-on-hip"),
    "arm-right": ("sheet-back + v8", "as arm-left, on the shadow side"),
    "scarf-tail": ("sheet-back + v8", "teal scarf tail hanging on the character's right below the pack, flaring under the "
                   "hand (sheet back view and v8's teal tail on the same side)"),
    "coat": ("sheet-back + v8", "storm-slate coat skirt to mid-thigh with a centre back vent (sheet back view); colours "
             "from v8. Belt stubs either side of the pack at v8's belt rows are inferred from v8's front belt; folds are proposed"),
    "legs": ("sheet-back + v8", "spruce trousers (v8 colours) with a strap at the character's right knee (sheet back "
             "view shows a knee strap; v8's knee pad is on the same leg's front)"),
    "boots": ("sheet-back + v8", "warm leather boots with a turned cuff and an ankle strap with a steel buckle seen from "
              "the heel (sheet back view; v8 boot ramp). Heel blocks and slight toe-out are proposed"),
    "not_present": ("—", "no face, eyes, shirt front, laces, knee pad, chest emblem or lapel trims: these are front-only "
                    "in the sheet and v8. No new gear, outfit piece or marking was added"),
}

MAP = [
    "............................AAAAA.......................",  # 00
    "...........................AKVVKLA......................",  # 01
    "..........................AKVVKKLBA.....................",  # 02
    ".........................AKVKKLBBLHAA...................",  # 03
    ".......................AAAFQKLBBLBHHFAAA................",  # 04
    ".....................AAKVKLQQQBHFKLBBHHFAA..............",  # 05
    "....................AKVVKLBFQFBBLHFKLBBHHFAA............",  # 06
    "...................AVVVKLBLBFBLBBHHFFKLBHHHFA...........",  # 07
    "..................AKVVVKKBLBHFBLBBHHFAFKLBHHFA..........",  # 08
    ".................ALKVVKLHKLBBHFBLBHHFAAAKLBBHFA.........",  # 09
    ".................AKVKKLBHKLBBHFBBLHHFA.AKKLBHFA.........",  # 10
    ".................ALKKLLBHKLLBHFBBLBHFA..AKLBHBFA........",  # 11
    "..................AKLLBBHVLBBHFLBBHHFA..ALKBHBFA........",  # 12
    "..................AKLBBHFKLBBHFLBBHFQA..ALKBHHFA........",  # 13
    "..................ALLBBHFLBBHFFBLHHFQA..ALBKHHFA........",  # 14
    "..................ALBBHHFLBBHFHBBHHFQA..ABLBHHFA........",  # 15
    "..................ALBBHFFBBHHFHBHHFFQA..ABLBHHFA........",  # 16
    "..................ABBHHFHBBHFFHBHFFQQA...ALBHHFA........",  # 17
    "..................ABBHFFHBHHFHHHFFFQQA...ABLHFFA........",  # 18
    "..................ABHHFHHHHFFHHFFFQQQA....ABHHFA........",  # 19
    "..................AHHFHHFHFFHHFFFQQQQA....AHBHFA........",  # 20
    "...................AHFHFFHFFHFFQFFQQA....AFAHFAFA.......",  # 21
    "...................ABHFQFFQFFQFQFQQFA....AFAAFAAFA......",  # 22
    "..................ABHPDPDDDDDDDDCDFFA.....A.AFA.A.......",  # 23
    ".............AAAAAAHDPDDDCDDDCDDDCCFAA.......A..........",  # 24
    "............AGcccccccccccccccGGGGGGGGMAAAA..............",  # 25
    "...........AcGcccccccccccccGGGGGGGGGMMDDDCA.............",  # 26
    "..........AGMSGGGGGGGGGGGGGGGGGGGGGGMMMMDCCA............",  # 27
    "..........AMSGMGGGGGGGGGGGGGGGGGGGGMMMMMDCCA............",  # 28
    "..........AMGSMGGGGGMMMMMMMMMMMMMMMMMMSSDCCA............",  # 29
    "...........AMSSMMMMMMMMMMMMMMMMMMMMSSSSDDCCA............",  # 30
    "............ASSSSSSSSSSSSSSSSSSSSSSSSSADDCCA............",  # 31
    "............APPDDCPPPHKJHHHHHHHHHKJHCCADDCCA............",  # 32
    "............APPDDCPPFYKJYYYYUYYYYKJYFCADDCCA............",  # 33
    "............APPDDebdFYKJLLLUcULLLKJHFCADDCCA............",  # 34
    "............APPDDbddFYKJLLUcGGILLKJHFCADDCCA............",  # 35
    "............APPDDUebFYKJLLLUGILLLKJHFCADDCCA............",  # 36
    "............APPDCUebFYKJLLLLILLLLKJHFCADCCCA............",  # 37
    "............APDDDUebFYKJLLLLLLLLLKJHFCADDCCA............",  # 38
    "............APPDDJJFFQUeQQQQQQQQQUeQFCADDCCA............",  # 39
    "............APPDDUebFLebBBBBBBBBBebHFCADDCCA............",  # 40
    "............APPDDUebFLKJBBBBBBBBBKJHFCADDCCA............",  # 41
    "............APDDDUebFLKJBBBBBBBBBKJHFCADDCCA............",  # 42
    "...........AXXNNIebdFFKJFFFFFFFFFKJFFCANNNIHA...........",  # 43
    "...........AXNNNIddZFLKJBBBBBBBBBKJHFCANNIIHA...........",  # 44
    "...........ANNNIIAPPFLKJBBBBBBBBBKJHFCANIIIHA...........",  # 45
    "...........AIIIIHAPPFLKJBBBBBBBBBKJHFCAIIHHHA...........",  # 46
    "............ARRTTAJJFLKJBBBBBBBBBKJHFJATTWWA............",  # 47
    "............ARRTTAFFFLLHHHHHHHHHHHHHFFATTWWA............",  # 48
    "............ARRTWAPPFFFFFFFFFFFFFFFFFcGTTWWA............",  # 49
    "...........AKKJJAACCCCCCCCCCCCCCCCCCCcGLLBBHA...........",  # 50
    "...........AKVJJBPPPDDDDDDDDDDDDDDDDCcGLKBBHA...........",  # 51
    "...........AKKJJBPPPDDDDDDDDDDDDDDDDCcGLLBBHA...........",  # 52
    "...........AKJJBHPPPDCDDDDDDCDDDDDCDCcGLBBHHA...........",  # 53
    "...........AHJBBHPPPPCDDDDDDCDDDDDCDCcMHBBHFA...........",  # 54
    "............ARTTWPPPDDCDDDDDCDDDDCDDCcMTTWWA............",  # 55
    "............ARTWPPPPDPCDDDDDCDDDDCDDCcGMTWWA............",  # 56
    ".............AAAPPPPDDDCDDDDCDDDCDDDCcGMMAA.............",  # 57
    "...............APPPPDDPCDDDDCDDDCDDDCcGMMS..............",  # 58
    "..............APPPPDDDDDDDDCCCDDDDDDDcGMMS..............",  # 59
    "..............APPPPDDDDDDDCCCCCDDDDDDccMMS..............",  # 60
    "..............APPPPDDDDDDDCCCCCDDDDDDcGGMMS.............",  # 61
    "..............APPPPDDDDDDCCCCCOCDDDDDcGMMMS.............",  # 62
    ".............APPPPDDDDDDDCCCCCOCDDDDDcGMMMS.............",  # 63
    ".............APPPPPPPPPPCCCCCCCOCDDDDcGGMMS.............",  # 64
    ".............ACCCCCCCCCCCCCCCCCOCCCCCcGGMMS.............",  # 65
    "..............AAAAAOOEEECCCCCCCOOEEECCcGGMMS............",  # 66
    "..................COOEEECCC...COOEEECCScGMMS............",  # 67
    "..................COOEEECCC...COOEEECCCScGMS............",  # 68
    "..................COOEEECCC...CKKJJJUeC.ScMS............",  # 69
    ".................COOEEECCC....CFFFFFFFCC.SS.............",  # 70
    ".................COOCCECCC.....COOECECCC................",  # 71
    ".................COOEECCCC.....COCCEECCC................",  # 72
    ".................COOEEECCC.....COOEEECCC................",  # 73
    ".................COOEEECCC.....COOEEECCC................",  # 74
    ".................COOEEECCC.....COOEEECCC................",  # 75
    "................COOEEECCFF....FFFOOEEECCC...............",  # 76
    ".................FVVVKKJJHF..FKKKJJJHHFC................",  # 77
    ".................FKKKJJJHFF..FKJJJBHHFF.................",  # 78
    "..................FHFFJFFFF...FFFJFFFFF.................",  # 79
    "..................FVKJJBBHF...FKJBBBHFF.................",  # 80
    "..................FKKJJBBHF...FJJBBHHFF.................",  # 81
    "..................FKJJBBBHF...FJJBBHHFF.................",  # 82
    "..................FKJJBBHFF...FJBBBHHFF.................",  # 83
    "..................FKJBBBHFF...FJBBHHFFF.................",  # 84
    "..................FKJBBHFF...FFFFJFFeFF.................",  # 85
    "..................FKJBBHFF....FFJBBHHFF.................",  # 86
    ".................FUeFJFFFFF....FJBBHHFF.................",  # 87
    "..................FKJBBBHFF...FKJBBHHFF.................",  # 88
    ".................FVKJJBBHFF...FKJBBHHFFF................",  # 89
    ".................FKKJBBBHFF...FJJBBHHFFF................",  # 90
    "................AKKJJBBHHFA...AJBBHHFFFQA...............",  # 91
    "................AJJJBBHHFQA...AHFFFFQQQQA...............",  # 92
    "................AHHFFFFQQQA....AQQQQQQQA................",  # 93
    ".................AQQQQQQQA......AAAAAAA.................",  # 94
    "..................AAAAAAA...............................",  # 95
]
ROLE = [
    "............................ttttt.......................",  # 00
    "...........................ttttttt......................",  # 01
    "..........................ttttttttt.....................",  # 02
    ".........................tttttttttttt...................",  # 03
    ".......................hhttttttttttttttt................",  # 04
    ".....................hhhhhhhhhhhtttttttttt..............",  # 05
    "....................hhhhhhhhhhhhhhtttttttttt............",  # 06
    "...................hhhhhhhhhhhhhhhhhttttttttt...........",  # 07
    "..................hhhhhhhhhhhhhhhhhhhttttttttt..........",  # 08
    ".................hhhhhhhhhhhhhhhhhhhhhttttttttt.........",  # 09
    ".................hhhhhhhhhhhhhhhhhhhhh.tttttttt.........",  # 10
    ".................hhhhhhhhhhhhhhhhhhhhh..tttttttt........",  # 11
    "..................hhhhhhhhhhhhhhhhhhhh..tttttttt........",  # 12
    "..................hhhhhhhhhhhhhhhhhhhh..tttttttt........",  # 13
    "..................hhhhhhhhhhhhhhhhhhhh..tttttttt........",  # 14
    "..................hhhhhhhhhhhhhhhhhhhh..tttttttt........",  # 15
    "..................hhhhhhhhhhhhhhhhhhhh..tttttttt........",  # 16
    "..................hhhhhhhhhhhhhhhhhhhh...ttttttt........",  # 17
    "..................hhhhhhhhhhhhhhhhhhhh...ttttttt........",  # 18
    "..................hhhhhhhhhhhhhhhhhhhh....tttttt........",  # 19
    "..................hhhhhhhhhhhhhhhhhhhh....tttttt........",  # 20
    "...................hhhhhhhhhhhhhhhhhh....tttttttt.......",  # 21
    "...................hhhhhhhhhhhhhhhhhh....ttttttttt......",  # 22
    "..................hhhqqqqqqqqqqqqqhhh.....t.ttt.t.......",  # 23
    ".............rrrrrhhqqqqqqqqqqqqqqqhhr.......t..........",  # 24
    "............rrrrrrrrrrrrrrrrrrrrrrrrrrrnnn..............",  # 25
    "...........rrrrrrrrrrrrrrrrrrrrrrrrrrrnnnnn.............",  # 26
    "..........rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrnnnn............",  # 27
    "..........rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrnnnn............",  # 28
    "..........rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrnnnn............",  # 29
    "...........rrrrrrrrrrrrrrrrrrrrrrrrrrrrnnnnn............",  # 30
    "............rrrrrrrrrrrrrrrrrrrrrrrrrrrnnnnn............",  # 31
    "............mmmmmmcccpzzpppppppppzzpccnnnnnn............",  # 32
    "............mmmmmmccppzzpppppppppzzppcnnnnnn............",  # 33
    "............mmmmmkkkppzzpppppppppzzppcnnnnnn............",  # 34
    "............mmmmmkkkppzzpppppppppzzppcnnnnnn............",  # 35
    "............mmmmmkkkppzzpppppppppzzppcnnnnnn............",  # 36
    "............mmmmmkkkppzzpppppppppzzppcnnnnnn............",  # 37
    "............mmmmmkkkppzzpppppppppzzppcnnnnnn............",  # 38
    "............mmmmmkkkppzzpppppppppzzppcnnnnnn............",  # 39
    "............mmmmmkkkppzzpppppppppzzppcnnnnnn............",  # 40
    "............mmmmmkkkppzzpppppppppzzppcnnnnnn............",  # 41
    "............mmmmmkkkppzzpppppppppzzppcnnnnnn............",  # 42
    "...........mmmmmmkkkppzzpppppppppzzppcnnnnnnn...........",  # 43
    "...........mmmmmmkkkppzzpppppppppzzppcnnnnnnn...........",  # 44
    "...........mmmmmmkccppzzpppppppppzzppcnnnnnnn...........",  # 45
    "...........mmmmmmmccppzzpppppppppzzppcnnnnnnn...........",  # 46
    "............mmmmmmccppzzpppppppppzzppcnnnnnn............",  # 47
    "............mmmmmmccpppppppppppppppppcnnnnnn............",  # 48
    "............mmmmmmccpppppppppppppppppssnnnnn............",  # 49
    "...........mmmmmmccccccccccccccccccccssnnnnnn...........",  # 50
    "...........mmmmmmccccccccccccccccccccssnnnnnn...........",  # 51
    "...........mmmmmmccccccccccccccccccccssnnnnnn...........",  # 52
    "...........mmmmmmccccccccccccccccccccssnnnnnn...........",  # 53
    "...........mmmmmmccccccccccccccccccccssnnnnnn...........",  # 54
    "............mmmmmccccccccccccccccccccssnnnnn............",  # 55
    "............mmmmcccccccccccccccccccccsssnnnn............",  # 56
    ".............mmmcccccccccccccccccccccssssnn.............",  # 57
    "...............ccccccccccccccccccccccsssss..............",  # 58
    "..............cccccccccccccclccccccccsssss..............",  # 59
    "..............ccccccccccccclllcccccccsssss..............",  # 60
    "..............ccccccccccccclllcccccccssssss.............",  # 61
    "..............cccccccccccclllllccccccssssss.............",  # 62
    ".............ccccccccccccclllllccccccssssss.............",  # 63
    ".............cccccccccccclllllllcccccssssss.............",  # 64
    ".............cccccccccccclllllllcccccssssss.............",  # 65
    "..............ccccclllllllllllllllllllssssss............",  # 66
    "..................lllllllll...llllllllssssss............",  # 67
    "..................lllllllll...lllllllllsssss............",  # 68
    "..................lllllllll...lllllllll.ssss............",  # 69
    ".................lllllllll....llllllllll.ss.............",  # 70
    ".................lllllllll.....lllllllll................",  # 71
    ".................lllllllll.....lllllllll................",  # 72
    ".................lllllllll.....lllllllll................",  # 73
    ".................lllllllll.....lllllllll................",  # 74
    ".................lllllllll.....lllllllll................",  # 75
    "................lllllllloo....ooollllllll...............",  # 76
    ".................oooooooooo..ooooooooool................",  # 77
    ".................oooooooooo..oooooooooo.................",  # 78
    "..................ooooooooo...ooooooooo.................",  # 79
    "..................ooooooooo...ooooooooo.................",  # 80
    "..................ooooooooo...ooooooooo.................",  # 81
    "..................ooooooooo...ooooooooo.................",  # 82
    "..................ooooooooo...ooooooooo.................",  # 83
    "..................ooooooooo...ooooooooo.................",  # 84
    "..................oooooooo...oooooooooo.................",  # 85
    "..................oooooooo....ooooooooo.................",  # 86
    ".................oooooooooo....oooooooo.................",  # 87
    "..................ooooooooo...ooooooooo.................",  # 88
    ".................oooooooooo...oooooooooo................",  # 89
    ".................oooooooooo...oooooooooo................",  # 90
    "................ooooooooooo...ooooooooooo...............",  # 91
    "................ooooooooooo...ooooooooooo...............",  # 92
    "................ooooooooooo....ooooooooo................",  # 93
    ".................ooooooooo......ooooooo.................",  # 94
    "..................ooooooo...............................",  # 95
]


def fid(role):
    return hashlib.sha256(f"{RUN_ID}:{role}".encode()).hexdigest()[:8]


NAMES = {
    "png": f"{SLUG}_{VISUAL_ID}_{SUBJECT}_{VARIANT}_{STAMP}-{fid('png')}.png",
    "pxo": f"{SLUG}_{VISUAL_ID}_{SUBJECT}-editable_{VARIANT}_{STAMP}-{fid('pxo')}.pxo",
    "ora": f"{SLUG}_{VISUAL_ID}_{SUBJECT}-editable-layers_{VARIANT}_{STAMP}-{fid('ora')}.ora",
    "manifest": f"{SLUG}_{VISUAL_ID}_{SUBJECT}-manifest_{VARIANT}_{STAMP}-{fid('manifest')}.json",
}
TOOL_REL = "tools/" + os.path.basename(os.path.abspath(__file__))


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def ref_ok(rel, want, kind):
    data = read_bytes(repo_path(rel))
    return (sha256_bytes(data) if kind == "bytes" else text_sha256_lf(data)) == want


def refs_checked():
    bad = [k for k, (rel, h, kind) in REFS.items() if not ref_ok(rel, h, kind)]
    if bad:
        raise SystemExit(f"reference files changed: {bad}; refusing to run")


# ============================================================================ composition
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


def png_bytes(a):
    buf = io.BytesIO()
    Image.fromarray(a, "RGBA").save(buf, "PNG", optimize=False, compress_level=9)
    return buf.getvalue()


def decode(png):
    return np.array(Image.open(io.BytesIO(png)).convert("RGBA"))


def make_pxo(blobs, preview_png):
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": n == "guides", "metadata": {}, "name": n,
                   "new_cels_linked": False, "opacity": 1.0, "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": n != "guides"} for n in LAYERS]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0}
                             for _ in LAYERS], "duration": 1.0, "metadata": {}}]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": json.dumps("protagonist-female-north-idle-static-pilot-v01"),
                      "frame_current_tag": "0", "include_tag_in_filename": "false", "interpolation": "0",
                      "lines_count": "1", "new_dir_for_each_frame_tag": "false", "number_of_digits": "4",
                      "number_of_frames": "1", "orientation": "0", "repeat_count": "0", "resize": "100",
                      "save_quality": "0.75", "separator_character": "\"_\"",
                      "sheet_layers_as_separate_files": "false", "split_layers": "false"}
    palette = {"name": "protagonist-female-v8-subset", "comment": "v8 palette entries used by the north pilot",
               "width": 8, "height": 4,
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


def artifacts():
    validate_maps()
    full = compose()
    blobs = {n: compose(k) for n, k in ROLE_LAYERS}
    blobs["guides"] = v8t.guides_rgba(full)        # same guide layout as the v8 .pxo; refuses any overlap
    png = png_bytes(full)
    return full, png, make_pxo(blobs, png), make_ora(blobs, png), blobs


# ============================================================================ gates
def gates(full):
    _, v8 = v8t.v8_checked()
    alpha = full[..., 3]
    op = alpha > 0
    ys, xs = np.nonzero(op)
    cols = {tuple(int(c) for c in px) for px in full[op][:, :3]}
    v8op = v8[..., 3] > 0
    v8cols = {tuple(int(c) for c in px) for px in v8[v8op][:, :3]}
    vys, vxs = np.nonzero(v8op)
    border = np.zeros_like(op); border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
    sole = int(ys.max())
    low = ys >= sole - 12
    # Not a mirrored front: north opaque texels whose RGBA equals v8 at the same position, or v8 mirrored left-right
    # (best of shifts -3..+3 around the pin axis).
    same_plain = int(((full == v8).all(axis=2) & op).sum())
    same_mirror = max(int(((full == np.roll(v8[:, ::-1], s, axis=1)).all(axis=2) & op).sum()) for s in range(-3, 4))
    skin = {hex_rgb(PAL[k]) for k in "RTW"}
    head_skin = sum(1 for y, x in zip(ys, xs) if y <= 33 and tuple(int(c) for c in full[y, x, :3]) in skin)
    return {
        "P1_binary_alpha": bool(set(np.unique(alpha).tolist()) <= {0, 255}),
        "P1_no_opaque_on_border": not bool((op & border).any()),
        "P2_colour_count": len(cols), "P2_v8_colour_count": len(v8cols),
        "P3_colours_subset_of_v8_palette": cols <= v8cols,
        "P3_v8_colours_unused": sorted("#%02x%02x%02x" % c for c in v8cols - cols),
        "S1_body_rows": [int(ys.min()), sole], "S1_v8_body_rows": [int(vys.min()), int(vys.max())],
        "S1_pass": int(ys.min()) == BODY_ROWS[0] and sole == BODY_ROWS[1] and sole == PIN[1] - 1
                   and int(vys.min()) == BODY_ROWS[0] and int(vys.max()) == BODY_ROWS[1],
        "S1_logical_height_px": (sole - int(ys.min()) + 1) * DISPLAY_SCALE,
        "S1_pin": list(PIN), "S1_pin_inside_feet_span": bool(int(xs[low].min()) <= PIN[0] <= int(xs[low].max())),
        "S1_alpha_bounds_inclusive": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
        "S1_v8_alpha_bounds_inclusive": [int(vxs.min()), int(vys.min()), int(vxs.max()), int(vys.max())],
        "opaque_texels": int(op.sum()), "v8_opaque_texels": int(v8op.sum()),
        "N1_texels_equal_v8_same_position": same_plain,
        "N1_texels_equal_v8_mirrored_about_pin": same_mirror,
        "N1_share_mirrored_match": round(same_mirror / int(op.sum()), 4),
        "N2_skin_texels_in_head_rows_le_33": head_skin,
        "N3_texels_per_material": {m: int(sum(np.sum((full[..., :3] == hex_rgb(PAL[k])).all(axis=2) & op) for k in ks))
                                    for m, ks in MATERIAL.items()},
    }


HARD = ["P1_binary_alpha", "P1_no_opaque_on_border", "P3_colours_subset_of_v8_palette", "S1_pass",
        "S1_pin_inside_feet_span"]


# ============================================================================ build
def manifest_json(png, pxo, ora, full):
    g = gates(full)
    m = {
        "project": "Worlds Between", "milestone": "M8", "visual_id": VISUAL_ID,
        "purpose": "Female protagonist north-facing exploration idle STATIC pilot (back view) matched to the approved "
                   "south idle selout v8 at 48 logical px; one missing direction toward the four-direction set.",
        "status": "UNAPPROVED technical candidate; NONRUNTIME (not wired into any scene); no animation; no other direction",
        "art_approved": False, "human_reviewed": False, "runtime_integrated": False,
        "acceptance_counters_unchanged": {"exploration_sprites": "0/52"},
        "authorship": "Texels hand-placed by Claude (Claude Code) as literal grids in the tool; no generated pixels.",
        "cell": {"w": W, "h": H, "pin": list(PIN), "body_rows": list(BODY_ROWS), "display_scale": DISPLAY_SCALE,
                 "logical_height_px": 48, "filter": "nearest", "alpha": "binary"},
        "files": {
            "png": {"file": f"{OUT_DIR_REL}/{NAMES['png']}", "sha256": sha256_bytes(png), "hash_algorithm": "sha256-bytes"},
            "pxo": {"file": f"{OUT_DIR_REL}/{NAMES['pxo']}", "sha256": sha256_bytes(pxo), "hash_algorithm": "sha256-bytes",
                    "format": f"Pixelorama pxo_version 7 ({PIXELORAMA_VERSION}), color_mode 5, 1 frame x {len(LAYERS)} layers"},
            "ora": {"file": f"{OUT_DIR_REL}/{NAMES['ora']}", "sha256": sha256_bytes(ora), "hash_algorithm": "sha256-bytes",
                    "format": "OpenRaster 0.0.3, mimetype stored first, one PNG per layer, mergedimage = PNG"},
        },
        "layers_bottom_to_top": [{"name": n, "evidence": EVIDENCE[n][0], "content": EVIDENCE[n][1]} for n, _ in ROLE_LAYERS]
                                + [{"name": "guides", "visible": False, "locked": True,
                                    "content": "#ff00ff cell border, ticks on rows 8 and 103, pin (40,104); never exported"}],
        "not_present": EVIDENCE["not_present"][1],
        "palette": {"source": "subset of v8's 32 colours (exact RGB)", "keys": PAL},
        "references": {k: {"file": rel, "sha256": h, "hash_algorithm": "sha256-bytes" if kind == "bytes" else "sha256-text-lf-v1"}
                       for k, (rel, h, kind) in REFS.items()},
        "gates": g,
        "tool": {"file": TOOL_REL, "sha256": text_sha256_lf(read_bytes(os.path.abspath(__file__))),
                 "hash_algorithm": "sha256-text-lf-v1", "python": sys.version.split()[0], "pillow": Image.__version__,
                 "numpy": np.__version__, "run_flags": "-I -B"},
    }
    return (json.dumps(m, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def build():
    refs_checked()
    full, png, pxo, ora, _ = artifacts()
    _, png2, pxo2, ora2, _ = artifacts()
    if (png, pxo, ora) != (png2, pxo2, ora2):
        raise SystemExit("build is not deterministic")
    g = gates(full)
    if not all(g[k] for k in HARD):
        raise SystemExit("hard gate failed: " + json.dumps({k: g[k] for k in HARD}))
    out = repo_path(OUT_DIR_REL)
    os.makedirs(_fs(out), exist_ok=True)
    for key, data in (("png", png), ("pxo", pxo), ("ora", ora), ("manifest", manifest_json(png, pxo, ora, full))):
        print(write_new(os.path.join(out, NAMES[key]), data), NAMES[key], sha256_bytes(data))
    refs_checked()


# ============================================================================ check
def read_ora_layers(ora):
    with zipfile.ZipFile(io.BytesIO(ora)) as z:
        root = ET.fromstring(z.read("stack.xml"))
        layers = [(el.get("name"), decode(z.read(el.get("src"))), el.get("visibility", "visible")) for el in root.iter("layer")]
        merged = decode(z.read("mergedimage.png"))
        first = z.infolist()[0]
        mt = first.filename == "mimetype" and first.compress_type == zipfile.ZIP_STORED
    return layers, merged, mt


def appdata_snapshot():
    root = os.path.join(os.environ.get("APPDATA", ""), "pixelorama")
    snap = {}
    if os.path.isdir(root):
        for d, _, files in os.walk(root):
            for f in files:
                p = os.path.join(d, f)
                try:
                    snap[os.path.relpath(p, root).replace("\\", "/")] = sha256_bytes(read_bytes(p))
                except OSError:
                    snap[os.path.relpath(p, root).replace("\\", "/")] = "unreadable"
    return snap


def pixelorama_export(exe, src, out_dir, split):
    """Headless export with APPDATA redirected to a fresh temp dir (never touches the real config)."""
    env = dict(os.environ)
    env["APPDATA"] = tempfile.mkdtemp(prefix="wb-fnorth-appdata-")
    args = [exe, "--headless", "--quit", "--", "--export"] + (["--split-layers"] if split else []) + \
           ["-o", os.path.join(out_dir, "f.png"), src]
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=240, env=env)
    finally:
        shutil.rmtree(_fs(env["APPDATA"]), ignore_errors=True)
    files = sorted(f for f in os.listdir(_fs(out_dir)) if f.lower().endswith(".png"))
    return p.returncode, {f: read_bytes(os.path.join(out_dir, f)) for f in files}


def check(exe):
    refs_checked()
    full, png, pxo, ora, blobs = artifacts()
    out = repo_path(OUT_DIR_REL)
    disk = {k: read_bytes(os.path.join(out, NAMES[k])) for k in NAMES}
    man = json.loads(disk["manifest"])
    rep = {"files_equal_rebuild": {"png": disk["png"] == png, "pxo": disk["pxo"] == pxo, "ora": disk["ora"] == ora,
                                   "manifest": text_sha256_lf(disk["manifest"]) == text_sha256_lf(manifest_json(png, pxo, ora, full))},
           "manifest_file_hashes_match": all(man["files"][k]["sha256"] == sha256_bytes(disk[k]) for k in ("png", "pxo", "ora")),
           "png_decodes_to_maps": decode(disk["png"]).tobytes() == full.tobytes(),
           "gates": gates(full), "pixelorama": {}}
    layers, merged, mt = read_ora_layers(disk["ora"])
    bottom_up = [(n, a) for n, a, vis in reversed(layers) if vis != "hidden"]
    comp = np.zeros((H, W, 4), np.uint8)
    overlap = 0
    for _, a in bottom_up:
        m = a[..., 3] == 255
        overlap += int((m & (comp[..., 3] == 255)).sum())
        comp[m] = a[m]
    rep["ora_structure"] = {"mimetype_first_and_stored": mt,
                            "hidden_layers": [n for n, _, vis in layers if vis == "hidden"],
                            "layer_names_bottom_up": [n for n, _ in bottom_up],
                            "role_layers_overlap_texels": overlap,
                            "visible_layers_recompose_to_png": comp.tobytes() == full.tobytes(),
                            "each_layer_equals_role_blob": all(a.tobytes() == blobs[n].tobytes() for n, a in bottom_up),
                            "mergedimage_equals_png": merged.tobytes() == full.tobytes()}
    snap0 = appdata_snapshot()
    tmp = tempfile.mkdtemp(prefix="wb-fnorth-")
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
                    leak = any(o.tobytes() == blobs["guides"].tobytes() for o in arrs.values())
                    r = {"mode": "split-layers", "exit": rc, "pngs": len(outs), "visible_layers_matched": len(matched),
                         "visible_layers": len(want), "guides_exported": leak,
                         "pass": rc == 0 and len(matched) == len(want) and len(outs) == len(want) and not leak}
                else:
                    a = next(iter(arrs.values())) if len(arrs) == 1 else None
                    ok = rc == 0 and a is not None and a.tobytes() == full.tobytes()
                    r = {"mode": "flattened", "run": run, "exit": rc, "pngs": len(outs), "rgba_equals_png": ok,
                         "binary_alpha": a is not None and set(np.unique(a[..., 3]).tolist()) <= {0, 255}, "pass": ok}
                    if len(outs) == 1:
                        flats.append(next(iter(outs.values())))
                rep["pixelorama"][f"{kind}_{run}"] = r
            rep["pixelorama"][f"{kind}_flat_runs_byte_identical"] = len(flats) == 2 and flats[0] == flats[1]
            rep["pixelorama"][f"{kind}_input_unchanged_by_cli"] = read_bytes(src) == disk[kind]
    finally:
        shutil.rmtree(_fs(tmp), ignore_errors=True)
    snap1 = appdata_snapshot()
    changed = sorted(k for k in set(snap0) | set(snap1) if snap0.get(k) != snap1.get(k))
    rep["real_appdata_pixelorama_changed"] = {"ours": [k for k in changed if not k.startswith(GUI_OWNED)],
                                              "gui_owned": [k for k in changed if k.startswith(GUI_OWNED)]}
    rep["references_unchanged_after"] = {k: ref_ok(rel, h, kind) for k, (rel, h, kind) in REFS.items()}
    g, px, o = rep["gates"], rep["pixelorama"], rep["ora_structure"]
    ok = (all(rep["files_equal_rebuild"].values()) and rep["manifest_file_hashes_match"] and rep["png_decodes_to_maps"]
          and all(g[k] for k in HARD)
          and o["mimetype_first_and_stored"] and o["hidden_layers"] == ["guides"] and o["role_layers_overlap_texels"] == 0
          and o["visible_layers_recompose_to_png"] and o["each_layer_equals_role_blob"] and o["mergedimage_equals_png"]
          and all(v["pass"] for v in px.values() if isinstance(v, dict))
          and px["pxo_flat_runs_byte_identical"] and px["ora_flat_runs_byte_identical"]
          and px["pxo_input_unchanged_by_cli"] and px["ora_input_unchanged_by_cli"]
          and not rep["real_appdata_pixelorama_changed"]["ours"] and all(rep["references_unchanged_after"].values()))
    rep["result"] = "PASS" if ok else "FAIL"
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=["build", "check"])
    ap.add_argument("--pixelorama", default=repo_path(PIXELORAMA_REL))
    a = ap.parse_args()
    if a.mode == "build":
        build()
        return 0
    if not os.path.isfile(a.pixelorama):
        raise SystemExit(f"Pixelorama not found: {a.pixelorama}")
    return check(os.path.abspath(a.pixelorama))


if __name__ == "__main__":
    sys.exit(main())
