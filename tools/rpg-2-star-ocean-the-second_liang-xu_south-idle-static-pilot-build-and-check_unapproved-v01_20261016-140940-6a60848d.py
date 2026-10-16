"""Liang Xu south-facing exploration idle STATIC pilot (UNAPPROVED v01): hand-placed 80x112 cell,
editable Pixelorama source with role layers, palette, manifest, and technical gates.

Scope: one direction (south), one static idle frame, Liang Xu only. No animation, no runtime
integration, no other character, no approval or counter change. The female selout v8 south static is
used only as the quality/scale benchmark (same cell, pin, 96-texel body, 0.5 display scale); none of
its texels are copied.

Source of truth: MAP (colour keys) and ROLE (role-layer keys) below. Both are literal 56x96 grids
placed at cell offset (12, 8). They were hand-edited texel by texel; a scratch primitive blocking pass
(not shipped) only seeded the large masses before the hand passes.

Modes (real Python, isolated):
  python -I -B <this file> build                 write PNG, .pxo, palette, manifest (never overwrites)
  python -I -B <this file> check [--pixelorama X] gates + rebuild equality + Pixelorama CLI round trip
  python -I -B <this file> preview <out.png>     x4 nearest preview of the sprite alone (for outputs/)
"""
import argparse, hashlib, io, json, os, shutil, subprocess, sys, tempfile, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
VISUAL_ID = "liang-xu"
VARIANT = "unapproved-v01"
STAMP = "20261016-140940"
RUN_ID = "baa30d44"
W, H = 80, 112
GRID_W, GRID_H = 56, 96
GRID_OFFSET = (12, 8)                 # grid (0,0) -> cell (12,8); body rows 8..103 like v8
PIN = (40, 104)
BODY_ROWS = (8, 103)
DISPLAY_SCALE = 0.5                   # 96 texels -> 48 logical px; 1 texel = 1 window px at 1280x720
OUT_DIR_REL = "game/assets/characters/liang-xu/south-idle-static-pilot-unapproved-v01"
PIXELORAMA_REL = "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"
PIXELORAMA_VERSION = "v1.2.3-stable"
GUIDE_RGB = (255, 0, 255)

REFS = {
    "identity_sheet": ("outputs/rpg-2-star-ocean-the-second_liang-xu_character-sheet_v01_20261013-153556-c7630671.png", "bytes"),
    "game_bible_state": ("outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json", "text"),
    "identity_transfer_audit": ("docs/qa/rpg-2-star-ocean-the-second_science-companions_48px-identity-transfer-codex-audit_unapproved-v01_20261016-114641-a9e6c2d1.md", "text"),
    "prior_liang_premium_south_concept": ("game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_liang-xu_south-exploration-premium-pixel_m8-concept_20261014-153531-4c6e2bcd.png", "bytes"),
    "prior_liang_city_capture_48px": ("outputs/rpg-2-star-ocean-the-second_scifi-city_liang-xu-character-quality-h48-canvas-items_m8-v02_20261014-153547-1ca1259c.png", "bytes"),
    "benchmark_female_selout_v8_png": ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png", "bytes"),
    "benchmark_female_selout_v8_decision": ("docs/character-visuals/rpg-2-star-ocean-the-second_protagonist-female_south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md", "text"),
    "pipeline_doc": ("docs/design/rpg-2-star-ocean-the-second_character-sprites_pixel-art-production-pipeline_unapproved-v01_20261015-040155-ffd3391d.md", "text"),
}
V8_SHA256 = "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"

# Named ramps (pipeline P3). key -> hex. Light comes from the upper left.
RAMPS = {
    "selout": {"K": "0a0a0e", "k": "1c1b24"},
    "hair-dark": {"1": "6a5654", "2": "45383b", "3": "251d20"},
    "hair-silver": {"W": "f6f4f0", "S": "d2cfd6", "s": "a09eac", "z": "6e6c7e"},
    "skin": {"F": "f2c49c", "f": "d89c72", "e": "ab6c4c", "d": "7c4838"},
    "brow-iris": {"y": "3b2622"},
    "coat-graphite": {"L": "b9bdc8", "A": "8d92a0", "B": "616574", "C": "42454f", "D": "272932"},
    "tunic-lining-navy": {"N": "5874ba", "n": "3a4e88", "m": "25305a"},
    "trousers": {"T": "555564", "t": "34343f"},
    "boots-glove-belt": {"O": "6e6064", "o": "42373a", "q": "221c20"},
    "copper": {"Q": "ffc68a", "R": "e08c4c", "r": "a95b2f", "u": "6b3521"},
    "tablet-screen": {"G": "a0eaff", "g": "3ba8e2"},
}
PAL = {k: v for ramp in RAMPS.values() for k, v in ramp.items()}

# Role layers, Pixelorama layer 1 = bottom (pipeline section 1.3 order, read bottom-up).
# arm-near = the tablet arm (viewer's right), arm-far = the pocket arm (viewer's left); in a south view
# both are at similar depth, the names follow the pipeline's fixed stack.
ROLE_LAYERS = [("hair-back", "b"), ("arm-far", "r"), ("boots", "o"), ("legs", "l"), ("accessory", "a"),
               ("torso-coat", "t"), ("arm-near", "n"), ("head-face", "f"), ("hair-front", "h")]
LAYERS = [n for n, _ in ROLE_LAYERS] + ["guides"]

MAP = [
    ".......................KKKKKKKK.........................",  # 00
    ".....................KK1zsz1222KK.......................",  # 01
    "....................K1z2333221233K......................",  # 02
    "....................Kz2321z332223K......................",  # 03
    "....................K132112232323K......................",  # 04
    "....................K232123322323K......................",  # 05
    "....................K233223223333K......................",  # 06
    ".....................K2333223333K.......................",  # 07
    ".......................K3333333K........................",  # 08
    ".........................K3223K.........................",  # 09
    "........................K211223K........................",  # 10
    "......................K21WSSSs322K......................",  # 11
    ".....................K1WWSSSSs3122K.....................",  # 12
    "....................KWWSSSsSsz32112K....................",  # 13
    "...................KWSSSsSszFFf32122K...................",  # 14
    "...................KWSSsSszFFFFf3212K...................",  # 15
    "...................KSWSsszFFFFFff322K...................",  # 16
    "...................KSWSszFFFFFFffe32K...................",  # 17
    "...................KSWSsyyFFFfyyye32K...................",  # 18
    "...................KSWSzFFFFFffffe32K...................",  # 19
    "...................KSSszKKFFFfKKfeFeK...................",  # 20
    "...................KSSszyKFFFfyKfeFeK...................",  # 21
    "...................KSsszFFFFeffffee3K...................",  # 22
    "...................KSszFFFFfefffeeK3K...................",  # 23
    "...................KSszFFffedfffeeK3K...................",  # 24
    "...................KSszfFefffffeeKKK....................",  # 25
    "...................KsszffffedefeeK......................",  # 26
    "...................KszAKfffFffeeKCK.....................",  # 27
    "...................KzKABKfFffeeKCDK.....................",  # 28
    "....................KABBCnddddmCCDDK....................",  # 29
    "....................KABCCnrQRrmCCDDK....................",  # 30
    ".................KAABBCCnnRmmrmmCCDDDDK.................",  # 31
    "...............KALABBBCANnRmmunmBCCDDDDDK...............",  # 32
    "..............KALAABDALANnurrunmBABkDDDDDK..............",  # 33
    ".............KAAABBBDALANnnrmnnmBABkCDDDDKKKKKKK........",  # 34
    ".............KALABBBDALANnnrmnnmBABkDCDDKQRRRRRrK.......",  # 35
    "............KAABBBCkDALANnnrnnmmBBBCkCDDKRGkkkDrK.......",  # 36
    "............KABBBBCkBDAANnnrnnmmBCCCkCDDKRgkDkkrK.......",  # 37
    "...........KAABBBCCkBCAANnnRnnmmBCCDkCDDKRkkQRkrK.......",  # 38
    "...........KABBBCCDkBCAANnnrnnmmBCCDkCDDKRkRkkRrK.......",  # 39
    "...........KABBBCDKKBCAANnnrnnmmBCCDkCDDKRkRkkRrK.......",  # 40
    "...........KABBCCK.KBCAANnnrnnmmBCCDkCDDKRkkrrkrK.......",  # 41
    "...........KABBCK..KBCAANnnrnnmmBCCDkCDDKRkDkkkrK.......",  # 42
    "..........KABBCK...KCCAANnnRnnmmBCCDkCDDKRkkkDkrK.......",  # 43
    "..........KABBCK...KCCAANnnrnnmmBCCDkCCAKRkkkkDrK.......",  # 44
    "..........KABBCCK..KCCAANnnrnnmmBCCDkDDBooOFkkkrK.......",  # 45
    "..........KABBBCCK.KCCAANnnrnnmmBCCDkDDDooOfkDkrK.......",  # 46
    "..........KABBBBCCDKCCAANnnrnnmmBCCDkKKKqoofkkkrK.......",  # 47
    "..........KAABBBBCCKCCAANnrQRrmmBCCDDK..KRekkkDrK.......",  # 48
    "...........KABBBCCCKooOOooRqqrooooqqqK..KRkkkkkrK.......",  # 49
    "...........KCABBBCCKqqqqqqRqquqqqqqqqK..KRkDkkkrK.......",  # 50
    "............KCABBCDDKAAnnnurrummmBCDDK..KrrrrruuK.......",  # 51
    ".............KDALLADKAAnNnnnnnmmmBKBDkK.KKKKKKKKK.......",  # 52
    "..............KDABBRKAAnNnnmnnmmmBKBDkK.................",  # 53
    "...............KDDDDKAAnnnnmnnmmmBKBDDkK................",  # 54
    "..............KBkkkkkAArnnnmnmmrmBKBDDkK................",  # 55
    "..............KBCDCBAAKurRrrrruKKBKBDCkK................",  # 56
    "..............KBCBDCAKtttDKkkKTTttKBDDCDkK..............",  # 57
    "..............KBCBDCAKtttDKkkKTTttDKBDCDkK..............",  # 58
    ".............KBCBDCAKTtttDK..KTTttDKBDDCDkK.............",  # 59
    ".............KBCBDCAKTtttDK..KTTttDDKBDCDkK.............",  # 60
    ".............KBCBDAKTTtttDK..KTTttDDKBDCDkK.............",  # 61
    "............KBCBDCAKTTtttDK..KTTttDDKKCDCDkK............",  # 62
    "............KBCBDAKKTTtttDK..KTTtkDDKKCDCCkK............",  # 63
    "............KBCBDAKKTTttDDK..KTTtkDDKKCDCCkK............",  # 64
    "...........KBCBDCAKKTTtDtDK..KTTtkDDK.KCDCCkK...........",  # 65
    "...........KBCBDBK.KTTtttDK..KTTktDDK.KCDCCkK...........",  # 66
    "...........KBCBDBK.KTTtttDK..KTkttDDK.KCDCCkK...........",  # 67
    "..........KBCBDCBK.KTTtttDK..KTTttDDK.KCDDCCkK..........",  # 68
    "..........KBCBDCBK.KTTTttDK..KTTTtDDK..KCDCCkK..........",  # 69
    "..........KBCBDCNK.KTTTttDK..KTTTtDDK..KnDCCkK..........",  # 70
    "..........KBBDCNK..KTTTttDK..KTTTtDDK..KnDCCkK..........",  # 71
    ".........KBCBDCNK..KTTtDtDK..KTTttDDK..KnDDCCkK.........",  # 72
    ".........KCCBDCNK..KTTDDtDK..KTTttDDK..KnDDCCkK.........",  # 73
    ".........KCBDCCNK..KTTtDtDK..KTTttDDK..KnDDCCkK.........",  # 74
    "........KCCBDCNnK..KTTDttDK..KTTktDDK...KmnCCkK.........",  # 75
    "........KCCCDCNnK..KTTDttDK..KTTktDDK...KmnDCCkK........",  # 76
    "........KCCDCNnK..KOOOOOOOK..KOOOOOOOK..KmnDCCkK........",  # 77
    ".......KCCCDCNnK..KqqqqqqqK..KqqqqqqqK..KmnDCCkK........",  # 78
    ".......KCCCCCNnK...KoOOooqK..KoOooqqK...KmnDDCDkK.......",  # 79
    ".......KCCCCNnnK...KoOOooqK..KoOooqqK...KmmnDCDkK.......",  # 80
    "......KCCCCCNnnK...KRrqqqqK..KqqqqrRK....KmmnCDkK.......",  # 81
    "......KCCCCCNnmK...KruoooqK..KoooourK....KmmnDCDkK......",  # 82
    "......KCCCCCNnmK...KoOooqqK..KoOooqqK....KmmnDCDkK......",  # 83
    "......KCCCCNnmK....KoOooqqK..KoOooqqK....KmmnDCDkK......",  # 84
    ".....KCCCCCNnmK....KoOooqqK..KoOooqqK....KmmnDDDDkK.....",  # 85
    ".....KDDDDDDDmK....KoOooqqK..KoOooqqK....KmDDDDDDkK.....",  # 86
    ".....KBDKKKKKKK....KoOooqqK..KoOooqqK....KKKKKKKkDK.....",  # 87
    ".....KKK...........KqrqqqqK..KqqqqrqK...........KKK.....",  # 88
    "...................KoOoooqK..KoOooqqK...................",  # 89
    "..................KooOoooqK..KoOoooqqK..................",  # 90
    "..................KoOOooqqK..KoOOooqqK..................",  # 91
    "..................KOOooqqqK..KoOOoqqqK..................",  # 92
    "..................KoooqqqqK..KooooqqqK..................",  # 93
    "..................KqqqqqqqK..KqqqqqqqK..................",  # 94
    "..................KKKKKKKKK..KKKKKKKKK..................",  # 95
]

ROLE = [
    ".......................bbbbbbbb.........................",  # 00
    ".....................bbbbbbbbbbbb.......................",  # 01
    "....................bbbbbbbbbbbbbb......................",  # 02
    "....................bbbbbbbbbbbbbb......................",  # 03
    "....................bbbbbbbbbbbbbb......................",  # 04
    "....................bbbbbbbbbbbbbb......................",  # 05
    "....................bbbbbbbbbbbbbb......................",  # 06
    ".....................bbbbbbbbbbbb.......................",  # 07
    ".......................bbbbbbbbb........................",  # 08
    ".........................bbbbbb.........................",  # 09
    "........................hhhhhhhh........................",  # 10
    "......................hhhhhhhhhhhh......................",  # 11
    ".....................hhhhhhhhhhhhhh.....................",  # 12
    "....................hhhhhhhhhhhhhhhh....................",  # 13
    "...................hhhhhhhhhfffhhhhhh...................",  # 14
    "...................hhhhhhhhfffffhhhhh...................",  # 15
    "...................hhhhhhhfffffffhhhh...................",  # 16
    "...................hhhhhhfffffffffhhh...................",  # 17
    "...................hhhhhffffffffffhhh...................",  # 18
    "...................hhhhhffffffffffhhh...................",  # 19
    "...................hhhhhhfffffffffffh...................",  # 20
    "...................hhhhhfffffffffffff...................",  # 21
    "...................hhhhhfffffffffffhf...................",  # 22
    "...................hhhhffffffffffffhh...................",  # 23
    "...................hhhhffffffffffffhh...................",  # 24
    "...................hhhhfffffffffffff....................",  # 25
    "...................hhhhfffffffffff......................",  # 26
    "...................hhhtfffffffffftt.....................",  # 27
    "...................hhtttffffffffttt.....................",  # 28
    "....................ttttttfffftttttt....................",  # 29
    "....................ttttttaaaatttttt....................",  # 30
    ".................tttttttttattattttttttt.................",  # 31
    "...............tttttttttttattattttttttttt...............",  # 32
    "..............ttttttttttttaaaatttttttttttt..............",  # 33
    ".............ttttttttttttttttttttttttttttaaaaaaa........",  # 34
    ".............ttttttttttttttttttttttttnnnaaaaaaaaa.......",  # 35
    "............rrrrrrrttttttttttttttttttnnnaaaaaaaaa.......",  # 36
    "............rrrrrrrttttttttttttttttttnnnaaaaaaaaa.......",  # 37
    "...........rrrrrrrrttttttttttttttttttnnnaaaaaaaaa.......",  # 38
    "...........rrrrrrrrttttttttttttttttttnnnaaaaaaaaa.......",  # 39
    "...........rrrrrrrrttttttttttttttttttnnnaaaaaaaaa.......",  # 40
    "...........rrrrrrr.ttttttttttttttttttnnnaaaaaaaaa.......",  # 41
    "...........rrrrrr..ttttttttttttttttttnnnaaaaaaaaa.......",  # 42
    "..........rrrrrr...ttttttttttttttttttnnnaaaaaaaaa.......",  # 43
    "..........rrrrrr...ttttttttttttttttttnnnaaaaaaaaa.......",  # 44
    "..........rrrrrrr..ttttttttttttttttttnnnnnnnaaaaa.......",  # 45
    "..........rrrrrrrr.ttttttttttttttttttnnnnnnnaaaaa.......",  # 46
    "..........rrrrrrrrrttttttttttttttttttnnnnnnnaaaaa.......",  # 47
    "..........rrrrrrrrrrttttttaaaatttttttt..aanaaaaaa.......",  # 48
    "...........rrrrrrrrraaaaaaaaaaaaaaaaat..aaaaaaaaa.......",  # 49
    "...........rrrrrrrrraaaaaaaaaaaaaaaaaa..aaaaaaaaa.......",  # 50
    "............rrrrrrrrrtttttaaaatttttttt..aaaaaaaaa.......",  # 51
    ".............rrrrrrrrtttttttttttttttttt.aaaaaaaaa.......",  # 52
    "..............rrrrrrrtttttttttttttttttt.................",  # 53
    "...............rrrrrrttttttttttttttttttt................",  # 54
    "..............tttttttttttttttttttttttttt................",  # 55
    "..............tttttttttttttttttttttttttt................",  # 56
    "..............ttttttttlllllllllllltttttttt..............",  # 57
    "..............tttttttllllllllllllllttttttt..............",  # 58
    ".............ttttttttllllll..lllllllttttttt.............",  # 59
    ".............tttttttlllllll..lllllllttttttt.............",  # 60
    ".............tttttttlllllll..lllllllltttttt.............",  # 61
    "............ttttttttlllllll..llllllllttttttt............",  # 62
    "............ttttttttlllllll..llllllllttttttt............",  # 63
    "............ttttttttlllllll..llllllllttttttt............",  # 64
    "...........tttttttttlllllll..llllllll.ttttttt...........",  # 65
    "...........ttttttt.llllllll..llllllll.ttttttt...........",  # 66
    "...........ttttttt.llllllll..llllllll.ttttttt...........",  # 67
    "..........tttttttt.llllllll..llllllll.tttttttt..........",  # 68
    "..........tttttttt.llllllll..llllllll..ttttttt..........",  # 69
    "..........tttttttt.llllllll..llllllll..ttttttt..........",  # 70
    "..........ttttttt..llllllll..llllllll..ttttttt..........",  # 71
    ".........tttttttt..llllllll..llllllll..tttttttt.........",  # 72
    ".........tttttttt..llllllll..llllllll..tttttttt.........",  # 73
    ".........tttttttt..llllllll..llllllll..tttttttt.........",  # 74
    "........ttttttttt..llllllll..llllllll...ttttttt.........",  # 75
    "........ttttttttt..llllllll..llllllll...tttttttt........",  # 76
    "........tttttttt..ooooooooo..ooooooooo..tttttttt........",  # 77
    ".......ttttttttt..ooooooooo..ooooooooo..tttttttt........",  # 78
    ".......ttttttttt...oooooooo..oooooooo...ttttttttt.......",  # 79
    ".......ttttttttt...oooooooo..oooooooo...ttttttttt.......",  # 80
    "......tttttttttt...oooooooo..oooooooo....tttttttt.......",  # 81
    "......tttttttttt...oooooooo..oooooooo....ttttttttt......",  # 82
    "......tttttttttt...oooooooo..oooooooo....ttttttttt......",  # 83
    "......ttttttttt....oooooooo..oooooooo....ttttttttt......",  # 84
    ".....tttttttttt....oooooooo..oooooooo....tttttttttt.....",  # 85
    ".....tttttttttt....oooooooo..oooooooo....tttttttttt.....",  # 86
    ".....tttttttttt....oooooooo..oooooooo....tttttttttt.....",  # 87
    ".....ttt...........oooooooo..oooooooo...........ttt.....",  # 88
    "...................oooooooo..oooooooo...................",  # 89
    "..................ooooooooo..ooooooooo..................",  # 90
    "..................ooooooooo..ooooooooo..................",  # 91
    "..................ooooooooo..ooooooooo..................",  # 92
    "..................ooooooooo..ooooooooo..................",  # 93
    "..................ooooooooo..ooooooooo..................",  # 94
    "..................ooooooooo..ooooooooo..................",  # 95
]


def fid(role):
    return hashlib.sha256(f"{RUN_ID}:{role}".encode()).hexdigest()[:8]


NAMES = {
    "png": f"{SLUG}_{VISUAL_ID}_south-idle-static-pilot_{VARIANT}_{STAMP}-{fid('png')}.png",
    "pxo": f"{SLUG}_{VISUAL_ID}_south-idle-static-pilot-editable_{VARIANT}_{STAMP}-{fid('pxo')}.pxo",
    "palette": f"{SLUG}_{VISUAL_ID}_south-idle-static-pilot-palette_{VARIANT}_{STAMP}-{fid('palette')}.json",
    "manifest": f"{SLUG}_{VISUAL_ID}_south-idle-static-pilot-manifest_{VARIANT}_{STAMP}-{fid('manifest')}.json",
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
    for y, (m, r) in enumerate(zip(MAP, ROLE)):
        if len(m) != GRID_W or len(r) != GRID_W:
            raise SystemExit(f"row {y}: MAP/ROLE rows must be {GRID_W} wide")
        for x, (mk, rk) in enumerate(zip(m, r)):
            if (mk == ".") != (rk == "."):
                raise SystemExit(f"MAP/ROLE opacity differs at grid ({x},{y})")
            if mk != "." and mk not in PAL:
                raise SystemExit(f"undeclared colour key {mk!r} at grid ({x},{y})")
            if rk != "." and rk not in dict((v, k) for k, v in ROLE_LAYERS):
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
    for y in BODY_ROWS:
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


def make_pxo(full, preview_png):
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": n == "guides", "metadata": {}, "name": n,
                   "new_cels_linked": False, "opacity": 1.0, "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": n != "guides"} for n in LAYERS]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0}
                             for _ in LAYERS], "duration": 1.0, "metadata": {}}]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": json.dumps("liang-xu-south-idle-static-pilot-v01"),
                      "frame_current_tag": "0", "include_tag_in_filename": "false", "interpolation": "0",
                      "lines_count": "1", "new_dir_for_each_frame_tag": "false", "number_of_digits": "4",
                      "number_of_frames": "1", "orientation": "0", "repeat_count": "0", "resize": "100",
                      "save_quality": "0.75", "separator_character": "\"_\"",
                      "sheet_layers_as_separate_files": "false", "split_layers": "false"}
    palette = {"name": "liang-xu-v01", "comment": "declared ramps", "width": 8, "height": 6,
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
    blobs = {n: compose(k).tobytes() for n, k in ROLE_LAYERS}
    blobs["guides"] = guides_rgba(full).tobytes()
    buf = io.BytesIO()
    dt = (2026, 10, 16, 14, 9, 40)
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        def put(name, payload):
            z.writestr(zipfile.ZipInfo(name, dt), payload, zipfile.ZIP_DEFLATED)
        put("data.json", json.dumps(data, separators=(",", ":")))
        put("mimetype", "application/x-pixelorama")
        put("preview.png", preview_png)
        put("image_data/frames/1/", b"")
        for li, name in enumerate(LAYERS, start=1):
            put(f"image_data/frames/1/layer_{li}", blobs[name])
            put(f"image_data/frames/1/indices_layer_{li}", b"\x00")
    return buf.getvalue(), blobs


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


# Not lit ramps: the two selout inks (outer ink + interior line, the same 2-ink structure v8 uses) and the
# single brow/iris colour. They are reported in the palette but excluded from the P4 step check.
P4_EXEMPT = ("selout", "brow-iris")


def gates(full):
    alpha = full[..., 3]
    opaque = alpha > 0
    ys, xs = np.nonzero(opaque)
    colours = {tuple(int(c) for c in px) for px in full[opaque][:, :3]}
    declared = {hex_rgb(v) for v in PAL.values()}
    border = np.zeros_like(opaque); border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
    # P4: adjacent ramp steps in L*, reference = v8's declared cloth ramps from its QA note
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
    v8_min = round(min(v8_steps), 2)
    all_steps = [s for v in ramp_steps.values() for s in v]
    # S1
    body_h = int(ys.max() - ys.min() + 1)
    sole = int(ys.max())
    feet = xs[ys == sole]
    # S4: head+hair IoU vs the v8 benchmark, rows 8..40, same pin (both x=40)
    hh = np.zeros_like(opaque)
    ox, oy = GRID_OFFSET
    for y in range(GRID_H):
        for x in range(GRID_W):
            if ROLE[y][x] in "bhf":
                hh[oy + y, ox + x] = True
    s4 = {}
    v8_path = repo_path(REFS["benchmark_female_selout_v8_png"][0])
    if os.path.isfile(_fs(v8_path)) and sha256_bytes(read_bytes(v8_path)) == V8_SHA256:
        v8 = np.array(Image.open(io.BytesIO(read_bytes(v8_path))).convert("RGBA"))[..., 3] > 0
        band = slice(8, 41)
        v8hh = np.zeros_like(v8); v8hh[band] = v8[band]
        # v8 has no role split: its head+hair band is rows 8..33 (shoulders start at row 34)
        v8hh[34:41] = False
        ours = hh.copy(); ours[41:] = False
        inter = int((ours & v8hh).sum()); union = int((ours | v8hh).sum())
        s4 = {"pair": "liang-xu vs protagonist-female selout v8 (benchmark)", "rows": "8-40 (v8 head band 8-33)",
              "iou": round(inter / union, 4), "liang_texels": int(ours.sum()), "v8_texels": int(v8hh.sum()),
              "note": "reported only; pipeline S4 sets no threshold until a pair is user-judged"}
    return {
        "P1_binary_alpha": bool(set(np.unique(alpha).tolist()) <= {0, 255}),
        "P1_no_opaque_on_border": not bool((opaque & border).any()),
        "P2_colour_count": len(colours), "P2_cap": 48, "P2_pass": len(colours) <= 48,
        "P3_all_colours_declared": colours <= declared, "P3_declared_unused": sorted("#" + "%02x%02x%02x" % c for c in declared - colours),
        "P4_ramp_adjacent_Lstar_steps": ramp_steps, "P4_exempt": list(P4_EXEMPT), "P4_min_step": round(min(all_steps), 2),
        "P4_v8_reference_min_step": v8_min,
        "P4_v8_reference_source": "v8 QA note declared cloth ramps (coat C1-C3, trousers T1-T2)",
        "P4_pass": min(all_steps) >= v8_min,
        "S1_body_height": body_h, "S1_pass": abs(body_h - 96) <= 1 and sole == PIN[1] - 1,
        "S1_alpha_bounds_inclusive": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
        "S1_sole_row": sole, "S1_pin": list(PIN), "S1_sole_span_x": [int(feet.min()), int(feet.max())],
        "S1_feet_centre_x": round((int(feet.min()) + int(feet.max())) / 2, 1),
        "S4_head_hair_iou": s4,
        "opaque_texels": int(opaque.sum()),
        "visible_size": [int(xs.max() - xs.min() + 1), body_h],
    }


def legibility(full):
    """Report-only counts for the identity cues the audit asked for, all at 1 texel = 1 screen px."""
    def keys(y):
        return MAP[y]
    # bun: grid rows 0..9 are the bun + pinch; crown starts at row 10
    widths = []
    for y in range(0, 14):
        r = keys(y)
        xs_ = [x for x, k in enumerate(r) if k != "."]
        widths.append(max(xs_) - min(xs_) + 1 if xs_ else 0)
    bun_w = max(widths[0:9]); pinch_w = min(widths[7:11]); crown_w = widths[13]
    silver = [(x, y) for y in range(10, GRID_H) for x, k in enumerate(keys(y)) if k in "WSsz"]
    dark = [(x, y) for y in range(0, 29) for x, k in enumerate(keys(y)) if k in "123"]
    def mean_l(pts):
        return sum(lab(hex_rgb(PAL[MAP[y][x]]))[0] for x, y in pts) / len(pts)
    run = max(sum(1 for k in keys(y) if k in "WSsz") for y in range(10, GRID_H))
    # coat-tail negative space: transparent texels strictly between each tail and the legs/boots
    gaps = {}
    for y in range(57, 87):
        r = keys(y)
        mid = 27
        left = r[:mid]; right = r[mid + 1:]
        # left: last run of '.' before the leg/boot ink, after the tail ink
        lx = [x for x in range(0, mid) if r[x] != "."]
        segs_l = "".join("." if k == "." else "#" for k in r[:mid]).strip(".")
        segs_r = "".join("." if k == "." else "#" for k in r[mid + 1:]).strip(".")
        gl = max((len(s) for s in segs_l.split("#") if s), default=0)
        gr = max((len(s) for s in segs_r.split("#") if s), default=0)
        gaps[y] = [gl, gr]
    gap_rows_l = [y for y, (a, b) in gaps.items() if a > 0]
    gap_rows_r = [y for y, (a, b) in gaps.items() if b > 0]
    # tablet: grid columns 40..48, grid rows 34..52 (cell 52..60 x 42..60); body right edge left of it
    tab = [(x, y) for y in range(34, 53) for x in range(40, 49) if ROLE[y][x] == "a"]
    tx = [x for x, _ in tab]; ty = [y for _, y in tab]
    body_right = max(x for y in range(34, 53) for x in range(0, 40) if ROLE[y][x] in "trn" and MAP[y][x] != ".")
    copper = sum(1 for x, y in tab if MAP[y][x] in "QRru")
    return {
        "bun": {"max_width": bun_w, "pinch_width": pinch_w, "crown_width_row13": crown_w,
                "notch_depth_each_side_approx": round((min(bun_w, crown_w) - pinch_w) / 2, 1),
                "rows_above_crown": 10, "grey_strand_texels": sum(1 for y in range(0, 10) for k in keys(y) if k in "zs")},
        "silver_forelock": {"texels": len(silver), "max_row_run": run,
                            "rows": [min(y for _, y in silver), max(y for _, y in silver)],
                            "mean_Lstar_silver": round(mean_l(silver), 1), "mean_Lstar_dark_hair": round(mean_l(dark), 1),
                            "delta_Lstar": round(mean_l(silver) - mean_l(dark), 1)},
        "coat_tail_negative_space": {"rows_with_left_gap": [min(gap_rows_l), max(gap_rows_l)] if gap_rows_l else None,
                                     "rows_with_right_gap": [min(gap_rows_r), max(gap_rows_r)] if gap_rows_r else None,
                                     "max_gap_px": [max(a for a, _ in gaps.values()), max(b for _, b in gaps.values())],
                                     "between_legs_gap_px": 2, "per_row_left_right_px": {str(k + GRID_OFFSET[1]): v for k, v in gaps.items()}},
        "tablet": {"cell_bbox": [min(tx) + GRID_OFFSET[0], min(ty) + GRID_OFFSET[1], max(tx) + GRID_OFFSET[0], max(ty) + GRID_OFFSET[1]],
                   "size_px": [max(tx) - min(tx) + 1, max(ty) - min(ty) + 1],
                   "protrudes_beyond_body_px": max(tx) - body_right, "copper_frame_and_emblem_texels": copper,
                   "copper_R_vs_coat_C_dE76": round(de76(hex_rgb(PAL["R"]), hex_rgb(PAL["C"])), 1),
                   "screen_glow_texels": sum(1 for x, y in tab if MAP[y][x] in "Gg")},
    }


# ============================================================================ build
def artifacts():
    validate_maps()
    full = compose()
    union = np.zeros_like(full)
    for _, k in ROLE_LAYERS:
        part = compose(k)
        if ((union[..., 3] > 0) & (part[..., 3] > 0)).any():
            raise SystemExit("role layers overlap")
        union[part[..., 3] > 0] = part[part[..., 3] > 0]
    if union.tobytes() != full.tobytes():
        raise SystemExit("role layers do not reassemble the full sprite")
    png = png_bytes(full)
    pxo, blobs = make_pxo(full, png)
    return full, png, pxo, blobs


def palette_json():
    p = {"project": "Worlds Between", "visual_id": VISUAL_ID, "purpose": "declared named ramps (pipeline P3) for the "
         "Liang Xu south idle static pilot v01", "art_approved": False,
         "ramps": {name: [{"key": k, "hex": "#" + v} for k, v in ramp.items()] for name, ramp in RAMPS.items()},
         "light": "upper left", "colour_count": len(PAL)}
    return (json.dumps(p, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def manifest_json(png, pxo, pal, full):
    refs = {}
    for k, (rel, kind) in REFS.items():
        h, alg = ref_hash(rel, kind)
        refs[k] = {"file": rel, "sha256": h, "hash_algorithm": alg}
    layers = []
    for i, (n, k) in enumerate(ROLE_LAYERS, start=1):
        layers.append({"pixelorama_layer": i, "name": n, "visible": True, "locked": False,
                       "texels": int((compose(k)[..., 3] > 0).sum())})
    layers.append({"pixelorama_layer": len(LAYERS), "name": "guides", "visible": False, "locked": True,
                   "content": "#ff00ff cell border, ticks on rows 8 and 103, pin (40,104); never exported"})
    m = {
        "project": "Worlds Between", "milestone": "M8", "visual_id": VISUAL_ID, "identity_id": "character-01 梁序 Liang Xu",
        "purpose": "Task G pilot: one south-facing exploration idle STATIC frame for Liang Xu at the approved 48 logical px, "
                   "hand-placed clusters, editable Pixelorama role layers. Identity cues targeted at ordinary game size: "
                   "high bun with a visible pinch, broad silver forelock, two split long coat tails with negative space, "
                   "copper-framed folding tactical board held clear of the body.",
        "status": "UNAPPROVED pilot; technical gates only; not runtime-integrated; no animation; south only",
        "art_approved": False, "human_reviewed": False, "runtime_integrated": False,
        "acceptance_counters_unchanged": {"runtime_exploration_sprites_accepted": "0/52",
                                          "scene_quality_gates_passed": "0/11", "human_timed_playtests": "0/2"},
        "authorship": "Colour and role maps hand-edited texel by texel by Claude (Claude Code, signed-in Claude Max, "
                      "firstParty). A scratch primitive blocking pass seeded the large masses; it is not shipped and the "
                      "literal maps in the tool are the only source. No image generation, resampling, filtering, "
                      "quantization or dithering was used.",
        "benchmark": {"female_selout_v8": "quality/scale benchmark only (same 80x112 cell, pin, 96-texel body, 0.5 scale, "
                      "1-texel ink selout); no v8 texel, palette entry or design element is copied."},
        "identity_anchors": {
            "game_bible": "46 岁导师; 石墨灰长外套、铜色领扣、束起的灰白发、折叠式战术板",
            "hair_silhouette": "high round bun on the crown (14 px wide, 9 rows) above a 6 px pinch, so both sides show a notch "
                               "before the crown; broad silver forelock swept from a right-of-centre part across the "
                               "forehead and down the viewer-left cheek; one grey strand through the bun",
            "second_silhouette_mass": "open graphite coat whose two tails flare from the belt to mid-calf hems with "
                                      "pointed outer tips; transparent slots between each tail and the boots from row "
                                      "~73, navy lining wedges on the inner faces of the lower tails",
            "property": "folding tactical board, 9x19 px, copper frame + copper ring emblem + 2 px screen glow, held by "
                        "a fingerless glove at chest height on the viewer's right; it sticks out 9 px past the sleeve",
            "distinct_from": {"protagonist": "brown high ponytail with fringe; teal scarf/cape; brown leathers",
                              "zhao_ling": "asymmetric chin-length bob, teal tips, round teal earcup, vertical antenna; "
                                           "crossbody gear"},
            "pose": "hand in coat pocket with elbow out (triangle of background between arm and waist), eyes toward the board",
        },
        "cell": {"w": W, "h": H, "pin": list(PIN), "body_rows": list(BODY_ROWS), "display_scale": DISPLAY_SCALE,
                 "display_logical_height": 48, "filter": "nearest", "alpha": "binary", "grid_offset": list(GRID_OFFSET)},
        "files": {
            "png": {"file": f"{OUT_DIR_REL}/{NAMES['png']}", "sha256": sha256_bytes(png), "hash_algorithm": "sha256-bytes"},
            "pxo": {"file": f"{OUT_DIR_REL}/{NAMES['pxo']}", "sha256": sha256_bytes(pxo), "hash_algorithm": "sha256-bytes",
                    "format": f"Pixelorama pxo_version 7 ({PIXELORAMA_VERSION}), color_mode 5, 1 frame x {len(LAYERS)} layers, "
                              "fixed zip timestamps", "layers_bottom_to_top": layers,
                    "preview_png": "the pilot PNG bytes"},
            "palette": {"file": f"{OUT_DIR_REL}/{NAMES['palette']}", "sha256": text_sha256_lf(pal),
                        "hash_algorithm": "sha256-text-lf-v1"},
            "gdignore": f"{OUT_DIR_REL}/.gdignore",
        },
        "references": refs,
        "gates": gates(full),
        "legibility_metrics_report_only": legibility(full),
        "pending_visual_decisions": [
            "Does the bun + silver forelock read as Liang (not Heya / not the protagonist) at 1280x720 without a nameplate?",
            "Are the coat-tail slots and lining wedges enough, or should the tails flare further (figure is 46 px wide vs v8 43)?",
            "Does the board read as a folding tactical board rather than a phone/book? (9x19 px, copper frame)",
            "Face age: one nasolabial texel and narrowed eyes; does Liang read 46 and composed next to the protagonists?",
            "Graphite coat value in the dark annex: the left tail and torso separate by the ink selout more than by value.",
        ],
        "tool": {"file": TOOL_REL, "sha256": text_sha256_lf(read_bytes(os.path.abspath(__file__))),
                 "hash_algorithm": "sha256-text-lf-v1", "python": sys.version.split()[0], "pillow": Image.__version__,
                 "numpy": np.__version__, "run_flags": "-I -B"},
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


def build():
    full, png, pxo, _ = artifacts()
    full2, png2, pxo2, _ = artifacts()
    if png != png2 or pxo != pxo2:
        raise SystemExit("build is not deterministic")
    g = gates(full)
    hard = ["P1_binary_alpha", "P1_no_opaque_on_border", "P2_pass", "P3_all_colours_declared", "S1_pass"]
    bad = [k for k in hard if not g[k]]
    if bad:
        raise SystemExit(f"hard gates failed: {bad}")
    out = repo_path(OUT_DIR_REL)
    os.makedirs(_fs(out), exist_ok=True)
    print(write_new(os.path.join(out, ".gdignore"), b""), ".gdignore")
    pal = palette_json()
    for key, data in (("png", png), ("pxo", pxo), ("palette", pal)):
        print(write_new(os.path.join(out, NAMES[key]), data), NAMES[key])
    man = manifest_json(png, pxo, pal, full)
    print(write_new(os.path.join(out, NAMES["manifest"]), man), NAMES["manifest"], text_sha256_lf(man), "(sha256-text-lf-v1)")
    print("png sha256-bytes", sha256_bytes(png))
    print("pxo sha256-bytes", sha256_bytes(pxo))


# ============================================================================ check
def run_pixelorama(exe, args, appdata):
    env = dict(os.environ)
    env["APPDATA"] = appdata                 # isolate config.ini/.running from any open GUI session
    return subprocess.run([exe, "--headless", "--quit", "--"] + args, capture_output=True, text=True,
                          timeout=180, env=env)


def real_pixelorama_snapshot():
    root = os.path.join(os.environ.get("APPDATA", ""), "pixelorama")
    snap = {}
    if os.path.isdir(root):
        for d, _, files in os.walk(root):
            for f in files:
                p = os.path.join(d, f)
                rel = os.path.relpath(p, root).replace("\\", "/")
                if rel == ".running":
                    continue                 # GUI heartbeat, rewritten every ~15 s by an open GUI
                try:
                    snap[rel] = sha256_bytes(read_bytes(p))
                except OSError:
                    snap[rel] = "unreadable"
    return snap


def check(exe):
    full, png, pxo, blobs = artifacts()
    out = repo_path(OUT_DIR_REL)
    disk = {k: read_bytes(os.path.join(out, NAMES[k])) for k in ("png", "pxo", "palette", "manifest")}
    man = json.loads(disk["manifest"])
    rep = {"files_equal_rebuild": {"png": disk["png"] == png, "pxo": disk["pxo"] == pxo,
                                   "palette": text_sha256_lf(disk["palette"]) == text_sha256_lf(palette_json())},
           "manifest_hashes_match": man["files"]["png"]["sha256"] == sha256_bytes(disk["png"])
           and man["files"]["pxo"]["sha256"] == sha256_bytes(disk["pxo"]),
           "png_decodes_to_maps": np.array(Image.open(io.BytesIO(disk["png"])).convert("RGBA")).tobytes() == full.tobytes(),
           "gates": gates(full), "runs": []}
    before = real_pixelorama_snapshot()
    tmp = tempfile.mkdtemp(prefix="wb-liangpxo-")
    try:
        src = os.path.join(tmp, "liang.pxo")
        with open(src, "wb") as f:
            f.write(disk["pxo"])
        flat_pngs = []
        for i in (1, 2):
            appdata = os.path.join(tmp, f"appdata{i}"); os.makedirs(appdata)
            od = os.path.join(tmp, f"flat{i}"); os.makedirs(od)
            p = run_pixelorama(exe, ["--export", "-o", os.path.join(od, "f.png"), src], appdata)
            files = sorted(os.listdir(od))
            r = {"run": i, "mode": "flattened", "exit_code": p.returncode, "pngs": files}
            if len(files) == 1:
                b = read_bytes(os.path.join(od, files[0]))
                a = np.array(Image.open(io.BytesIO(b)).convert("RGBA"))
                r["rgba_equal_pilot"] = a.shape == full.shape and a.tobytes() == full.tobytes()
                r["differing_texels"] = int((a != full).any(axis=2).sum()) if a.shape == full.shape else None
                flat_pngs.append(b)
            rep["runs"].append(r)
        rep["flattened_runs_byte_identical"] = len(flat_pngs) == 2 and flat_pngs[0] == flat_pngs[1]
        appdata = os.path.join(tmp, "appdata3"); os.makedirs(appdata)
        od = os.path.join(tmp, "split"); os.makedirs(od)
        p = run_pixelorama(exe, ["--export", "--split-layers", "-o", os.path.join(od, "f.png"), src], appdata)
        files = sorted(os.listdir(od))
        split = {"mode": "split-layers", "exit_code": p.returncode, "pngs": len(files), "layers": {}}
        for n, k in ROLE_LAYERS:
            hit = [f for f in files if f"({n})" in f]
            ok = None
            if len(hit) == 1:
                a = np.array(Image.open(io.BytesIO(read_bytes(os.path.join(od, hit[0])))).convert("RGBA"))
                ok = a.tobytes() == blobs[n]
            split["layers"][n] = ok
        split["guides_exported"] = any("(guides)" in f for f in files)
        rep["runs"].append(split)
        rep["source_pxo_unchanged_by_cli"] = read_bytes(src) == disk["pxo"]
    finally:
        shutil.rmtree(_fs(tmp), ignore_errors=True)
    after = real_pixelorama_snapshot()
    rep["real_appdata_pixelorama_changed"] = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    g = rep["gates"]
    ok = (all(rep["files_equal_rebuild"].values()) and rep["manifest_hashes_match"] and rep["png_decodes_to_maps"]
          and all(r.get("rgba_equal_pilot") and r["exit_code"] == 0 for r in rep["runs"] if r.get("mode") == "flattened")
          and rep["flattened_runs_byte_identical"] and split["exit_code"] == 0
          and all(v is True for v in split["layers"].values()) and not split["guides_exported"]
          and rep["source_pxo_unchanged_by_cli"] and not rep["real_appdata_pixelorama_changed"]
          and g["P1_binary_alpha"] and g["P1_no_opaque_on_border"] and g["P2_pass"] and g["P3_all_colours_declared"]
          and g["S1_pass"])
    rep["result"] = "PASS" if ok else "FAIL"
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    return 0 if ok else 1


def preview(path):
    full, png, _, _ = artifacts()
    Image.fromarray(full, "RGBA").resize((W * 4, H * 4), Image.NEAREST).save(path)
    print(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=["build", "check", "preview"])
    ap.add_argument("out", nargs="?")
    ap.add_argument("--pixelorama", default=repo_path(PIXELORAMA_REL))
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
