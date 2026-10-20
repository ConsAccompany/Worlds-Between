"""Science/outskirts battle arena: native 640x212 fixture-and-layer pass (battle-env12, v01, UNAPPROVED).

Base: the committed 1280x424 courtyard runtime band, nearest-resampled to 640x212 and declared as a flattened
inherited plate (provenance only; not claimed as native work). Over it this tool authors seven hard-alpha native
layers: cable trough, cast shadows, stone/metal framing, power/conduit hardware, inset control console,
signal/light structure and botanical depth. Light comes from the upper left, so every cast shadow falls to the
lower right on the rear paving. Nothing native is drawn at band-local y >= 150 (open fighting lane 150..211).

Writes layer PNGs, one merged PNG, a layered PXO (reused make_pxo writer), a supplementary ORA and the
worlds-between.battle-environment-source.v1 manifest into outputs/battle-env12. Deterministic: a rebuild reproduces
identical bytes and the writer refuses to overwrite different bytes.

  python <tool> build            write the candidate
  python <tool> check            rebuild in memory, compare with disk, run structural checks
  python <tool> check --pixelorama   also run the installed Pixelorama CLI export gate (not GUI Save As)
"""
from pathlib import Path
import argparse, hashlib, importlib.util, io, json, os, shutil, subprocess, sys, tempfile, zipfile
import numpy as np
from PIL import Image, ImageDraw

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
AUTHOR_REL = "tools/rpg-2-star-ocean-the-second_battle-arena_native-pass-author_v01_20261020-230516-c4a9e217.py"
BASE_REL = ("game/assets/environments/rpg-2-star-ocean-the-second_scifi-outskirts-battle-arena_runtime-band_"
            "m8-candidate_20261014-213622-14315e18.png")
PXO_TOOL_REL = "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py"
PIXELORAMA_REL = "../../tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"
OUT_REL = "outputs/battle-env12"
STAMP = "20261020-230516"
SLUG = "rpg-2-star-ocean-the-second"
SUBJECT = "outskirts-arena"
VARIANT = "env12-v01"
W, H = 640, 212
LANE = (150, 211)
ZIP_DT = (2026, 10, 20, 23, 5, 16)

C = {
    "ink": "#161b1e", "deep": "#252e33", "slate": "#36434a", "steel": "#53636a", "steel_l": "#7d8b8c",
    "edge": "#a7b0a6",
    "stone_d": "#584d40", "stone": "#7f705a", "stone_m": "#9d8b6e", "stone_l": "#bfad88", "stone_hl": "#dccca3",
    "brass_d": "#5c411f", "brass": "#987035", "brass_l": "#c99e56", "brass_hl": "#ebc77c",
    "teal_d": "#164b54", "teal": "#3a8885", "glow": "#86dcc8", "glow_hl": "#d2f7ea",
    "cable": "#1f2528", "cable_l": "#46535a",
    "soil": "#33281d", "leaf_d": "#203419", "leaf": "#365325", "leaf_m": "#567434", "leaf_l": "#87a246",
    "bloom": "#a98ac4", "bloom_l": "#d6c0e6", "bloom_y": "#d9bf56",
}
SHADOW_TONES = [(60, (33, 33, 39)), (92, (49, 49, 56)), (125, (62, 61, 67)), (999, (78, 76, 81))]

LAYERS = [  # bottom to top after the inherited base
    "cable-trough", "cast-shadows", "stone-metal-framing", "power-conduit", "control-console",
    "signal-light-structure", "botanical-depth",
]


def uid(key):
    return hashlib.sha256(f"{STAMP}:{key}".encode("utf-8")).hexdigest()[:8]


def fname(purpose, ext):
    return f"{SLUG}_{SUBJECT}_{purpose}_{VARIANT}_{STAMP}-{uid(purpose + '.' + ext)}.{ext}"


def canvas():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def col(name):
    h = C[name]
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 255)


def R(d, x0, y0, x1, y1, fill, outline=None):
    d.rectangle((x0, y0, x1, y1), fill=col(fill), outline=col(outline) if outline else None)


def L(d, pts, fill, width=1):
    d.line(pts, fill=col(fill), width=width)


def P(d, pts, fill, outline=None):
    d.polygon(pts, fill=col(fill), outline=col(outline) if outline else None)


def E(d, box, fill, outline=None):
    d.ellipse(box, fill=col(fill), outline=col(outline) if outline else None)


def dot(d, x, y, fill):
    d.point((x, y), fill=col(fill))


# ---------------------------------------------------------------------------------------------- inherited base

def base_layer():
    src = Image.open(os.path.join(REPO, BASE_REL)).convert("RGB")
    if src.size != (1280, 424):
        raise SystemExit(f"base plate size {src.size} != (1280, 424)")
    return src.resize((W, H), Image.NEAREST).convert("RGBA")


# ------------------------------------------------------------------------------------------------ native layers

def cable_trough():
    img, d = canvas()
    x0, x1, y0, y1 = 48, 592, 122, 131
    R(d, x0, y0, x1, y1, "ink")                       # recessed channel
    L(d, [(x0, y0), (x1, y0)], "stone_l")             # far curb lip catches the light
    L(d, [(x0, y0 + 1), (x1, y0 + 1)], "stone_d")
    L(d, [(x0, y1), (x1, y1)], "stone_m")             # near curb
    L(d, [(x0, y1 - 1), (x1, y1 - 1)], "deep")
    L(d, [(x0, y0), (x0, y1)], "stone_hl")
    L(d, [(x1, y0), (x1, y1)], "stone_d")
    # bundled cables visible in the open channel: two dark runs and one restrained teal-sheathed signal line
    L(d, [(x0 + 1, 125), (x1 - 1, 125)], "cable_l")
    L(d, [(x0 + 1, 126), (x1 - 1, 126)], "cable")
    L(d, [(x0 + 1, 128), (x1 - 1, 128)], "teal_d")
    L(d, [(x0 + 1, 127), (x1 - 1, 127)], "cable")
    # steel grate covers, 26 px sections with 6 px open gaps; slots every 3 px, brass corner bolts
    x = x0 + 4
    while x + 26 <= x1 - 2:
        R(d, x, y0 + 2, x + 25, y1 - 2, "steel")
        L(d, [(x, y0 + 2), (x + 25, y0 + 2)], "steel_l")
        L(d, [(x, y1 - 2), (x + 25, y1 - 2)], "slate")
        for sx in range(x + 3, x + 23, 3):
            L(d, [(sx, y0 + 4), (sx, y1 - 4)], "deep")
        for bx in (x + 1, x + 24):
            dot(d, bx, y0 + 3, "brass_l")
            dot(d, bx, y1 - 3, "brass")
        x += 32
    return img


def shadow_mask():
    m = Image.new("1", (W, H), 0)
    d = ImageDraw.Draw(m)
    polys = [
        # console + plinth: right side throw and a ground strip along the plinth foot
        [(182, 101), (197, 107), (199, 121), (182, 121)],
        [(78, 120), (184, 120), (187, 123), (81, 123)],
        # signal mast: long thin throw with the lamp head at the end
        [(212, 119), (218, 119), (253, 129), (248, 130)],
        # bollards
        [(271, 117), (274, 117), (283, 121), (280, 122)],
        [(371, 117), (374, 117), (383, 121), (380, 122)],
        # cabinet niche frame
        [(574, 50), (592, 110), (594, 121), (574, 121)],
        [(456, 120), (576, 120), (579, 123), (459, 123)],
        # junction box + drop conduit beside the niche
        [(453, 70), (457, 72), (457, 121), (453, 121)],
        # planters
        [(74, 128), (85, 132), (85, 147), (74, 147)],
        [(36, 146), (76, 146), (78, 148), (38, 148)],
        [(204, 130), (212, 133), (212, 147), (204, 147)],
        [(184, 146), (206, 146), (208, 148), (186, 148)],
        [(612, 128), (622, 132), (622, 147), (612, 147)],
        [(576, 146), (614, 146), (616, 148), (578, 148)],
    ]
    for p in polys:
        d.polygon(p, fill=1)
    d.ellipse((246, 126, 258, 131), fill=1)
    return np.array(m, dtype=bool)


def cast_shadows(below):
    """Hard-alpha shadow texels; each tone is chosen from the luminance of the art underneath (base + trough), so
    paving joints stay legible as a four-tone cluster instead of a translucent overlay."""
    mask = shadow_mask()
    a = np.zeros((H, W, 4), np.uint8)
    lum = (below[..., 0].astype(int) * 299 + below[..., 1].astype(int) * 587 + below[..., 2].astype(int) * 114) // 1000
    for y, x in zip(*np.nonzero(mask)):
        for lim, rgb in SHADOW_TONES:
            if lum[y, x] < lim:
                a[y, x, :3] = rgb
                break
        a[y, x, 3] = 255
    return Image.fromarray(a, "RGBA")


def stone_block_face(d, x0, y0, x1, y1, course=7, block=16):
    """Warm ashlar face: lit top lip, mortar courses, staggered joints, light left edge, shaded right edge."""
    R(d, x0, y0, x1, y1, "stone_m")
    y, row = y0 + course, 0
    while y < y1:
        L(d, [(x0, y), (x1, y)], "stone_d")
        y += course
    for r, yy in enumerate(range(y0, y1, course)):
        off = (block // 2) * (r % 2)
        for jx in range(x0 + off + block, x1, block):
            L(d, [(jx, yy + 1), (jx, min(yy + course - 1, y1))], "stone_d")
            dot(d, jx + 1, yy + 1, "stone_l")
    L(d, [(x0, y0), (x0, y1)], "stone_l")
    L(d, [(x1, y0), (x1, y1)], "stone")
    L(d, [(x0, y1), (x1, y1)], "stone_d")


def framing():
    img, d = canvas()
    # console plinth
    R(d, 78, 101, 182, 104, "stone_l")
    L(d, [(78, 101), (182, 101)], "stone_hl")
    stone_block_face(d, 78, 105, 182, 120)
    for cx in (78, 179):
        R(d, cx, 102, cx + 3, 104, "brass", "brass_d")
        dot(d, cx + 1, 102, "brass_hl")
    # mast footing
    R(d, 200, 104, 226, 107, "stone_l")
    L(d, [(200, 104), (226, 104)], "stone_hl")
    stone_block_face(d, 200, 108, 226, 120, course=6, block=13)
    R(d, 208, 105, 218, 107, "steel", "slate")          # steel base flange
    for bx in (209, 217):
        dot(d, bx, 106, "brass_l")
    # cabinet niche: dark inset back, two pilasters, lintel with brass emblem, plinth
    R(d, 468, 54, 562, 112, "deep")
    L(d, [(468, 54), (562, 54)], "ink")
    L(d, [(468, 54), (468, 112)], "ink")
    for px in (458, 563):
        R(d, px, 50, px + 9, 112, "stone_m")
        L(d, [(px, 50), (px, 112)], "stone_l")
        L(d, [(px + 1, 50), (px + 1, 112)], "stone_hl" if px == 458 else "stone_l")
        L(d, [(px + 9, 50), (px + 9, 112)], "stone")
        for yy in range(57, 112, 8):
            L(d, [(px, yy), (px + 9, yy)], "stone_d")
        R(d, px - 1, 52, px + 10, 54, "brass", "brass_d")   # capital band
        L(d, [(px, 52), (px + 9, 52)], "brass_hl")
    R(d, 455, 40, 575, 49, "stone_m")
    L(d, [(455, 40), (575, 40)], "stone_hl")
    L(d, [(455, 41), (575, 41)], "stone_l")
    L(d, [(455, 49), (575, 49)], "stone_d")
    L(d, [(455, 40), (455, 49)], "stone_l")
    L(d, [(575, 40), (575, 49)], "stone")
    for jx in (478, 500, 530, 552):
        L(d, [(jx, 42), (jx, 48)], "stone_d")
    P(d, [(509, 41), (521, 41), (518, 49), (512, 49)], "brass", "brass_d")   # keystone plate
    L(d, [(510, 42), (520, 42)], "brass_hl")
    R(d, 513, 44, 517, 46, "teal_d")
    dot(d, 514, 44, "glow")
    R(d, 455, 112, 575, 114, "stone_l")
    L(d, [(455, 112), (575, 112)], "stone_hl")
    stone_block_face(d, 455, 115, 575, 120, course=6, block=15)
    return img


def power_conduit():
    img, d = canvas()
    # cabinet body in the niche
    R(d, 474, 58, 556, 111, "slate", "ink")
    L(d, [(475, 59), (555, 59)], "steel_l")
    L(d, [(475, 59), (475, 110)], "steel")
    L(d, [(555, 60), (555, 110)], "deep")
    R(d, 474, 108, 556, 111, "deep", "ink")              # kick plate
    L(d, [(515, 60), (515, 107)], "ink")                  # door split
    for x0 in (478, 518):                                 # recessed door panels
        R(d, x0, 63, x0 + 33, 104, "steel", "deep")
        L(d, [(x0 + 1, 64), (x0 + 32, 64)], "steel_l")
        L(d, [(x0 + 1, 64), (x0 + 1, 103)], "steel_l")
    for yy in range(67, 80, 3):                           # louvres, upper right door
        L(d, [(522, yy), (547, yy)], "deep")
        L(d, [(522, yy + 1), (547, yy + 1)], "edge")
    R(d, 482, 67, 506, 82, "ink")                         # breaker window, left door
    for i, bx in enumerate(range(484, 505, 4)):
        R(d, bx, 69, bx + 2, 80, "deep")
        R(d, bx, 72 + (i % 2) * 3, bx + 2, 74 + (i % 2) * 3, "brass_l" if i % 3 else "teal")
    R(d, 486, 88, 502, 94, "brass", "brass_d")            # rating plate
    L(d, [(488, 90), (500, 90)], "brass_d")
    L(d, [(488, 92), (497, 92)], "brass_d")
    dot(d, 487, 89, "brass_hl")
    for hy in (84, 96):                                   # door handles, brass, either side of the split
        R(d, 512, hy, 513, hy + 4, "brass_l")
        R(d, 517, hy, 518, hy + 4, "brass")
    for i, lx in enumerate((524, 530, 536)):              # status lamps, restrained teal
        R(d, lx, 86, lx + 2, 88, "teal_d")
        dot(d, lx + 1, 87, "glow" if i != 2 else "teal")
    R(d, 523, 94, 547, 100, "deep")
    L(d, [(524, 97), (546, 97)], "teal_d")
    # junction box left of the niche, feed through the pilaster, drop conduit into the trough
    R(d, 440, 58, 454, 72, "steel", "ink")
    L(d, [(441, 59), (453, 59)], "steel_l")
    L(d, [(441, 59), (441, 71)], "steel_l")
    R(d, 444, 62, 450, 68, "slate")
    for bx, by in ((442, 60), (452, 60), (442, 70), (452, 70)):
        dot(d, bx, by, "brass_l")
    for yy, tone in ((63, "steel_l"), (64, "steel"), (65, "slate")):   # horizontal feed into the cabinet
        L(d, [(455, yy), (474, yy)], tone)
    R(d, 461, 62, 463, 66, "brass", "brass_d")            # clamp over the pilaster
    for xx, tone in ((445, "steel_l"), (446, "steel"), (447, "steel"), (448, "slate")):
        L(d, [(xx, 73), (xx, 124)], tone)
    for cy in range(80, 122, 13):
        R(d, 444, cy, 449, cy + 2, "brass", "brass_d")
        dot(d, 445, cy, "brass_hl")
    R(d, 442, 121, 451, 124, "deep", "ink")               # trough entry gland
    # console feed: short conduit from the console back down into the trough
    for xx, tone in ((185, "steel_l"), (186, "steel"), (187, "slate")):
        L(d, [(xx, 88), (xx, 124)], tone)
    L(d, [(173, 88), (185, 88)], "steel_l")
    L(d, [(173, 89), (185, 89)], "slate")
    for cy in (96, 110):
        R(d, 184, cy, 188, cy + 1, "brass", "brass_d")
    R(d, 183, 121, 189, 124, "deep", "ink")
    return img


def control_console():
    img, d = canvas()
    # upright back panel with hood
    R(d, 90, 62, 170, 63, "steel_l")
    R(d, 92, 64, 168, 87, "slate", "ink")
    L(d, [(93, 64), (93, 86)], "steel_l")
    L(d, [(167, 65), (167, 86)], "deep")
    # inset screen: brass bezel, teal glass, calm trace + grid ticks
    R(d, 98, 67, 142, 83, "brass_d")
    L(d, [(98, 67), (142, 67)], "brass_l")
    R(d, 100, 69, 140, 81, "teal_d")
    for gx in range(104, 140, 8):
        dot(d, gx, 75, "teal")
    trace = [(101, 76), (108, 76), (111, 72), (114, 79), (117, 75), (126, 75), (129, 73), (132, 77), (139, 77)]
    L(d, trace, "glow")
    dot(d, 111, 72, "glow_hl")
    L(d, [(101, 70), (110, 70)], "teal")
    # gauge cluster: two brass-rimmed dials with needles
    for gx in (146, 157):
        E(d, (gx, 69, gx + 8, 77), "deep", "brass")
        dot(d, gx + 2, 70, "brass_hl")
        L(d, [(gx + 4, 73), (gx + 6, 71)], "glow" if gx == 146 else "brass_l")
    R(d, 146, 79, 164, 83, "ink")
    for i, sx in enumerate(range(147, 164, 4)):
        R(d, sx, 80, sx + 2, 82, "teal" if i == 1 else "brass_d")
    # sloped desk with key rows
    P(d, [(88, 88), (172, 88), (177, 100), (83, 100)], "steel", "ink")
    L(d, [(89, 89), (171, 89)], "steel_l")
    L(d, [(88, 89), (84, 99)], "edge")
    for r, ky in enumerate((91, 94, 97)):
        inset = 3 - r
        for i, kx in enumerate(range(93 - r * 2 + inset, 166 + r * 2, 5)):
            tone = "teal" if (i + r) % 7 == 3 else ("brass_l" if (i + r) % 5 == 0 else "slate")
            R(d, kx, ky, kx + 2, ky + 1, tone)
    R(d, 124, 92, 136, 97, "deep")                        # trackball well
    E(d, (127, 93, 132, 97), "brass", "brass_d")
    dot(d, 128, 94, "brass_hl")
    # front apron with brass trim and side cheeks
    R(d, 83, 100, 177, 103, "deep", "ink")
    L(d, [(84, 101), (176, 101)], "brass")
    L(d, [(84, 100), (176, 100)], "brass_l")
    P(d, [(86, 87), (90, 87), (85, 101), (82, 101)], "slate", "ink")
    P(d, [(170, 87), (174, 87), (179, 101), (176, 101)], "deep", "ink")
    # desk shadow on the plinth top (light from upper left)
    L(d, [(84, 104), (180, 104)], "stone_d")
    return img


def signal_light():
    img, d = canvas()
    # main signal mast on its footing
    R(d, 210, 20, 215, 105, "steel")
    L(d, [(210, 20), (210, 105)], "steel_l")
    L(d, [(211, 20), (211, 105)], "edge")
    L(d, [(215, 20), (215, 105)], "slate")
    for by in range(30, 104, 17):
        R(d, 209, by, 216, by + 2, "brass", "brass_d")
        L(d, [(210, by), (215, by)], "brass_hl")
    # lamp head: brass housing, teal lens, cap
    P(d, [(205, 9), (220, 9), (223, 19), (202, 19)], "brass", "brass_d")
    L(d, [(206, 10), (219, 10)], "brass_hl")
    L(d, [(205, 10), (203, 18)], "brass_l")
    R(d, 205, 13, 220, 16, "teal_d")
    L(d, [(206, 14), (219, 14)], "glow")
    dot(d, 207, 14, "glow_hl")
    R(d, 208, 6, 217, 8, "slate", "ink")
    dot(d, 212, 5, "brass_l")
    # cantilever arm with a hanging signal lantern
    L(d, [(216, 26), (236, 26)], "steel_l")
    L(d, [(216, 27), (236, 27)], "slate")
    L(d, [(216, 32), (226, 27)], "steel")                 # strut
    L(d, [(233, 28), (233, 30)], "brass_d")
    R(d, 230, 31, 236, 41, "brass_d", "ink")
    R(d, 231, 33, 235, 39, "teal_d")
    L(d, [(232, 34), (232, 38)], "glow")
    L(d, [(233, 34), (234, 34)], "glow_hl")
    R(d, 230, 30, 236, 31, "brass_l")
    # small beacon on the niche lintel
    R(d, 510, 34, 520, 39, "brass", "brass_d")
    L(d, [(511, 35), (519, 35)], "brass_hl")
    R(d, 512, 31, 518, 33, "teal_d")
    L(d, [(513, 32), (517, 32)], "glow")
    # paired bollard lights framing the open centre (low, behind the fighters)
    for bx in (266, 366):
        R(d, bx, 103, bx + 5, 118, "stone_m", "stone_d")
        L(d, [(bx + 1, 104), (bx + 1, 117)], "stone_hl")
        R(d, bx - 1, 100, bx + 6, 102, "brass", "brass_d")
        L(d, [(bx, 100), (bx + 5, 100)], "brass_hl")
        R(d, bx + 2, 105, bx + 3, 110, "teal_d")
        dot(d, bx + 2, 106, "glow")
        L(d, [(bx, 118), (bx + 5, 118)], "stone_d")
    return img


def planter(d, x0, y0, x1, y1):
    R(d, x0, y0, x1, y0 + 2, "stone_l")
    L(d, [(x0, y0), (x1, y0)], "stone_hl")
    R(d, x0 + 2, y0 + 1, x1 - 2, y0 + 2, "soil")
    stone_block_face(d, x0, y0 + 3, x1, y1, course=6, block=12)
    L(d, [(x0, y0 + 8), (x1, y0 + 8)], "brass")
    L(d, [(x0, y0 + 9), (x1, y0 + 9)], "brass_d")


def leaf_clump(d, cx, cy, r):
    """Lobed three-tone clump: three overlapping leaf lobes (dark mass, mid body offset up-left, light crown) with
    pointed leaf tips on the silhouette; clean clusters, no noise."""
    lobes = [(cx - r // 2, cy, r * 2 // 3), (cx + r // 2, cy + 1, r * 2 // 3), (cx, cy - r // 3, r * 2 // 3)]
    for lx, ly, lr in lobes:
        E(d, (lx - lr, ly - lr + 1, lx + lr, ly + lr), "leaf_d")
    for lx, ly, lr in lobes:
        E(d, (lx - lr + 1, ly - lr, lx + lr - 1, ly + lr - 2), "leaf")
    for lx, ly, lr in lobes:
        E(d, (lx - lr + 1, ly - lr, lx + lr - 2, ly + lr - 3), "leaf_m")
    for lx, ly, lr in lobes[1:]:
        L(d, [(lx - lr + 2, ly - 1), (lx - 1, ly - lr + 1)], "leaf_l")   # lit leaf edge, upper left
    for tx, ty, tone in ((cx - r - 1, cy - 1, "leaf"), (cx + r, cy - 2, "leaf_d"), (cx - 1, cy - r - 1, "leaf_m"),
                         (cx + r // 2 + 1, cy - r + 1, "leaf_m"), (cx - r + 1, cy - r // 2 - 1, "leaf_l")):
        dot(d, tx, ty, tone)
        dot(d, tx + (1 if tx < cx else -1), ty + 1, tone)


def fern(d, x, y, dx, n):
    L(d, [(x, y), (x + dx * n, y - n)], "leaf")
    for i in range(1, n, 2):
        dot(d, x + dx * i, y - i - 1, "leaf_m")
        dot(d, x + dx * i + dx, y - i + 1, "leaf_d")


def botanical():
    img, d = canvas()
    beds = [  # planter box (x0, y0, x1, y1) and clump centres (cx, cy, r) and flower dots
        ((36, 132, 76, 146), [(42, 128, 6), (52, 124, 7), (63, 127, 6), (71, 130, 4)],
         [(50, 120, "bloom"), (55, 121, "bloom_l"), (64, 123, "bloom_y"), (44, 125, "bloom")]),
        ((184, 134, 206, 146), [(190, 130, 5), (199, 129, 5)], [(194, 126, "bloom_y"), (200, 126, "bloom")]),
        ((576, 132, 614, 146), [(582, 128, 5), (592, 124, 7), (604, 127, 6)],
         [(589, 120, "bloom_l"), (594, 121, "bloom"), (606, 123, "bloom_y"), (600, 122, "bloom")]),
    ]
    for (x0, y0, x1, y1), clumps, flowers in beds:
        for cx, cy, r in clumps:
            leaf_clump(d, cx, cy, r)
        for fx, fy, tone in flowers:   # small plus-shaped blossoms with a darker heart
            for px, py in ((fx, fy - 1), (fx - 1, fy), (fx + 1, fy), (fx, fy + 1)):
                dot(d, px, py, tone)
            dot(d, fx, fy, "brass_d" if tone == "bloom_y" else "bloom")
        fern(d, x0 + 1, y0 + 1, -1, 5)
        fern(d, x1 - 1, y0 + 1, 1, 5)
        planter(d, x0, y0, x1, y1)
        L(d, [(x0 + 3, y0 + 3), (x0 + 6, y0 + 6)], "leaf")     # trailing stem over the rim
        dot(d, x0 + 6, y0 + 7, "leaf_m")
    # ivy climbing the left niche pilaster (stays on the stone face)
    vine = [(459, 111), (461, 104), (459, 97), (462, 90), (460, 83), (463, 76), (461, 70)]
    L(d, vine, "leaf_d")
    for i, (vx, vy) in enumerate(vine[:-1]):
        side = 1 if i % 2 else -1
        R(d, vx + side, vy - 1, vx + side + 1, vy, "leaf_m")
        dot(d, vx + side * 2, vy - 2, "leaf_l" if i % 3 == 0 else "leaf")
    return img


# ---------------------------------------------------------------------------------------------- assembly/export

def composite(stack):
    out = np.zeros((H, W, 4), np.uint8)
    for im in stack:
        a = np.asarray(im)
        on = a[..., 3] == 255
        out[on] = a[on]
    return out


def png_bytes(img):
    b = io.BytesIO()
    img.save(b, "PNG", optimize=False, compress_level=9)
    return b.getvalue()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def text_lf_sha(path):
    with open(path, "rb") as f:
        return sha(f.read().replace(b"\r\n", b"\n"))


def load_make_pxo():
    spec = importlib.util.spec_from_file_location("wb_pxo_writer", os.path.join(REPO, PXO_TOOL_REL))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.W, mod.H = W, H
    mod.to_rgba = lambda a: np.ascontiguousarray(a, dtype=np.uint8)
    return mod.make_pxo


def make_ora(names, files, blobs, merged_png, thumb_png):
    stack = ['<?xml version="1.0" encoding="UTF-8"?>',
             f'<image version="0.0.3" w="{W}" h="{H}">', "<stack>"]
    for n, f in reversed(list(zip(names, files))):   # ORA lists top first
        stack.append(f'<layer name="{n}" src="data/{f}" x="0" y="0" opacity="1.0" visibility="visible" '
                     f'composite-op="svg:src-over"/>')
    stack += ["</stack>", "</image>", ""]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", ZIP_DT), "image/openraster", zipfile.ZIP_STORED)
        z.writestr(zipfile.ZipInfo("stack.xml", ZIP_DT), "\n".join(stack), zipfile.ZIP_DEFLATED)
        for f in files:
            z.writestr(zipfile.ZipInfo(f"data/{f}", ZIP_DT), blobs[f], zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("mergedimage.png", ZIP_DT), merged_png, zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("Thumbnails/thumbnail.png", ZIP_DT), thumb_png, zipfile.ZIP_DEFLATED)
    return buf.getvalue()


def build_all():
    base = base_layer()
    trough = cable_trough()
    below = composite([base, trough])
    imgs = {"inherited-base": base, "cable-trough": trough, "cast-shadows": cast_shadows(below),
            "stone-metal-framing": framing(), "power-conduit": power_conduit(),
            "control-console": control_console(), "signal-light-structure": signal_light(),
            "botanical-depth": botanical()}
    order = ["inherited-base"] + LAYERS
    arrays = {n: np.asarray(imgs[n]) for n in order}
    flat = composite([imgs[n] for n in order])
    flat_img = Image.fromarray(flat, "RGBA")
    blobs, files = {}, []
    for i, n in enumerate(order):
        f = fname(f"layer{i:02d}-{n}", "png")
        blobs[f] = png_bytes(imgs[n])
        files.append(f)
    flat_f = fname("merged-flat", "png")
    blobs[flat_f] = png_bytes(flat_img)
    thumb = flat_img.resize((256, 85), Image.NEAREST)
    make_pxo = load_make_pxo()
    pxo_f = fname("layered-source", "pxo")
    blobs[pxo_f] = make_pxo([arrays], [1.0], blobs[flat_f], os.path.splitext(flat_f)[0], 1, order=order, dt=ZIP_DT)
    ora_f = fname("layered-supplement", "ora")
    blobs[ora_f] = make_ora(order, files, blobs, blobs[flat_f], png_bytes(thumb))
    with open(os.path.join(REPO, BASE_REL), "rb") as f:
        base_sha = sha(f.read())
    manifest = {
        "schema": "worlds-between.battle-environment-source.v1",
        "canvas": [W, H],
        "base": {"file": BASE_REL, "sha256": base_sha,
                 "method": "nearest-resample 1280x424 -> 640x212; retained flattened inherited art (not native)"},
        "layers": [{"name": n, "file": f, "sha256": sha(blobs[f]),
                    "kind": "inherited-base" if n == "inherited-base" else "native-authored"}
                   for n, f in zip(order, files)],
        "flat": {"file": flat_f, "sha256": sha(blobs[flat_f])},
        "pxo": {"file": pxo_f, "sha256": sha(blobs[pxo_f])},
        "ora": {"file": ora_f, "sha256": sha(blobs[ora_f])},
        "author": {"file": AUTHOR_REL, "sha256TextLf": text_lf_sha(os.path.join(REPO, AUTHOR_REL))},
        "protected": {"arenaFloorScreenY": 272, "playBand": [0, 90, 640, 212], "openLaneLocalY": [150, 211]},
        "artApproved": False,
        "defaultAdopted": False,
    }
    man_f = fname("source-manifest", "json")
    blobs[man_f] = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return order, files, arrays, flat, blobs, manifest, man_f


# ------------------------------------------------------------------------------------------------------- checks

def structural_checks(order, files, arrays, flat, blobs, manifest, man_f):
    res = []

    def ok(name, cond, detail=""):
        res.append((name, bool(cond), detail))

    ok("canvas", manifest["canvas"] == [640, 212] and all(a.shape == (H, W, 4) for a in arrays.values()))
    ok("base opaque", (arrays["inherited-base"][..., 3] == 255).all())
    native = [n for n in order if n != "inherited-base"]
    ok("native layer count >= 6", len(native) >= 6, str(len(native)))
    for n in native:
        a = arrays[n][..., 3]
        ys, xs = np.nonzero(a)
        ok(f"{n}: hard alpha", set(np.unique(a)) <= {0, 255})
        ok(f"{n}: nonempty", len(xs) > 0, f"{len(xs)} px")
        if len(xs):
            ok(f"{n}: alpha bounds", ys.max() < LANE[0],
               f"x {xs.min()}..{xs.max()} y {ys.min()}..{ys.max()}")
        ok(f"{n}: open lane transparent", not a[LANE[0]:LANE[1] + 1].any())
        ok(f"{n}: unique colours <= 32", len(np.unique(arrays[n][a == 255][:, :3], axis=0)) <= 32,
           str(len(np.unique(arrays[n][a == 255][:, :3], axis=0))))
    ok("merged lane == base lane (no foreground over fighters)",
       np.array_equal(flat[LANE[0]:], arrays["inherited-base"][LANE[0]:]))
    ok("merged opaque", (flat[..., 3] == 255).all())
    ok("merged == recomposite", np.array_equal(flat, composite([Image.fromarray(arrays[n]) for n in order])))
    # PXO reconstruct
    z = zipfile.ZipFile(io.BytesIO(blobs[manifest["pxo"]["file"]]))
    data = json.loads(z.read("data.json"))
    ok("pxo size/layers", data["size_x"] == W and data["size_y"] == H and [l["name"] for l in data["layers"]] == order)
    pxo_stack = [np.frombuffer(z.read(f"image_data/frames/1/layer_{i}"), np.uint8).reshape(H, W, 4)
                 for i in range(1, len(order) + 1)]
    ok("pxo layers == layer pngs", all(np.array_equal(p, arrays[n]) for p, n in zip(pxo_stack, order)))
    ok("pxo reconstruct == merged", np.array_equal(composite([Image.fromarray(p) for p in pxo_stack]), flat))
    ok("pxo preview == merged bytes", z.read("preview.png") == blobs[manifest["flat"]["file"]])
    # ORA
    zo = zipfile.ZipFile(io.BytesIO(blobs[manifest["ora"]["file"]]))
    ok("ora mimetype first+stored", zo.infolist()[0].filename == "mimetype"
       and zo.infolist()[0].compress_type == zipfile.ZIP_STORED)
    ok("ora merged == merged bytes", zo.read("mergedimage.png") == blobs[manifest["flat"]["file"]])
    ok("ora layers == layer pngs", all(zo.read(f"data/{f}") == blobs[f] for f in files))
    # manifest
    ok("manifest keys", list(manifest) == ["schema", "canvas", "base", "layers", "flat", "pxo", "ora", "author",
                                           "protected", "artApproved", "defaultAdopted"])
    ok("manifest hashes", all(sha(blobs[l["file"]]) == l["sha256"] for l in manifest["layers"]))
    ok("manifest kinds", [l["kind"] for l in manifest["layers"]] ==
       ["inherited-base"] + ["native-authored"] * len(native))
    ok("unapproved/not default", manifest["artApproved"] is False and manifest["defaultAdopted"] is False)
    names = [man_f] + [manifest[k]["file"] for k in ("flat", "pxo", "ora")] + files
    ok("lowercase names", all(n == n.lower() for n in names))
    ok("path length <= 240", all(len(os.path.join(REPO, OUT_REL, n)) <= 240 for n in names),
       str(max(len(os.path.join(REPO, OUT_REL, n)) for n in names)))
    return res


def pixelorama_gate(blobs, manifest, arrays, flat, order):
    exe = next((str(a / "tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe") for a in Path(REPO).parents if (a / "tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe").is_file()), "")
    if not os.path.exists(exe):
        return [("pixelorama available", False, exe)]
    res = []
    work = tempfile.mkdtemp(prefix="wb-env12-px-")
    try:
        src = os.path.join(work, "src.pxo")
        with open(src, "wb") as f:
            f.write(blobs[manifest["pxo"]["file"]])
        for split in (False, True):
            od = os.path.join(work, "split" if split else "merged")
            os.makedirs(od)
            env = dict(os.environ)
            env["APPDATA"] = tempfile.mkdtemp(prefix="wb-pxappdata-")
            args = [exe, "--headless", "--quit", "--", "--export"] + (["--split-layers"] if split else []) + \
                   ["-o", os.path.join(od, "f.png"), src]
            try:
                p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                   timeout=240, env=env)
            finally:
                shutil.rmtree(env["APPDATA"], ignore_errors=True)
            log = (p.stdout or "") + "\n" + (p.stderr or "")
            diag = [ln.strip() for ln in log.splitlines() if "ERROR" in ln or "SCRIPT_ERROR" in ln]
            tag = "split" if split else "merged"
            res.append((f"pixelorama {tag}: exit 0", p.returncode == 0, str(p.returncode)))
            res.append((f"pixelorama {tag}: no ERROR/SCRIPT_ERROR lines", not diag,
                        "; ".join(sorted(set(diag)))[:400]))
            pngs = sorted(f for f in os.listdir(od) if f.lower().endswith(".png"))
            got = [np.asarray(Image.open(os.path.join(od, f)).convert("RGBA")) for f in pngs]
            if split:   # Pixelorama names split files "<export name>(<layer name>) _0001.png"; match by layer name
                by_name = {n: [g for f, g in zip(pngs, got) if f"({n})" in f] for n in order}
                exact = len(got) == len(order) and all(len(v) == 1 and np.array_equal(v[0], arrays[n])
                                                       for n, v in by_name.items())
                res.append(("pixelorama split == layer pngs", exact, f"{len(got)} files"))
            else:
                exact = len(got) == 1 and np.array_equal(got[0], flat)
                diff = int(np.abs(got[0].astype(int) - flat.astype(int)).max()) if len(got) == 1 else -1
                res.append(("pixelorama merged == merged png", exact, f"{len(got)} files, max diff {diff}"))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["build", "check"])
    ap.add_argument("--pixelorama", action="store_true")
    a = ap.parse_args()
    order, files, arrays, flat, blobs, manifest, man_f = build_all()
    out = os.path.join(REPO, OUT_REL)
    res = []
    if a.mode == "build":
        os.makedirs(out, exist_ok=True)
        for n, b in blobs.items():
            p = os.path.join(out, n)
            if os.path.exists(p):
                with open(p, "rb") as f:
                    if f.read() != b:
                        raise SystemExit(f"refusing to overwrite different bytes: {p}")
            else:
                with open(p, "wb") as f:
                    f.write(b)
        print(f"wrote {len(blobs)} files to {OUT_REL}")
    else:
        for n, b in blobs.items():
            p = os.path.join(out, n)
            same = os.path.exists(p) and open(p, "rb").read() == b
            res.append((f"disk == rebuild: {n}", same, ""))
        res.append(("no extra files in output dir", sorted(os.listdir(out)) == sorted(blobs), ""))
    res += structural_checks(order, files, arrays, flat, blobs, manifest, man_f)
    if a.pixelorama:
        res += pixelorama_gate(blobs, manifest, arrays, flat, order)
    fails = [r for r in res if not r[1]]
    for name, good, detail in res:
        print(("PASS " if good else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    print(f"{len(res) - len(fails)}/{len(res)} checks pass; manifest {man_f}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
