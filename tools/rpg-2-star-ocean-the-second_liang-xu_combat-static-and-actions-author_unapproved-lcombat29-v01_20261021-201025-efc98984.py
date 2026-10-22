"""Liang Xu (梁序, member_id liang-xu) side-view combat static + eight source actions (lcombat29). UNAPPROVED, NOT A DEFAULT.

Reuses the zcombat26 architecture (tools/...zhao-ling_combat-static-and-actions-author_unapproved-zcombat26-v01...5d3c9a71.py,
itself the mcombat22 method): every pose is a parameter row, a small rig (two-bone IK legs/arms, upper body rotated about the
pelvis, axis-aligned big Sea of Stars head) turns it into editable role layers, each part with a 1-texel near-black outline and
upper-left light / lower-right shadow planes. Raster primitives, ORA layout and the established PXO writer (female south-run v06
make_pxo) are the same code; the costume, body, signature tool and fx below are Liang's own (no handgun, no knife, no tablet copy).

Identity (lexplore28 exploration identity; palette = the lexplore28 author PAL, i.e. the Liang south pilot named ramps, copied
literally and checked against the lexplore28 module at check time): tactical mentor, age 46. Dark hair pinned up into a top-knot
with a copper pin, a silver streak sweeping back over the near (right) temple, a navy high collar, a copper placket line down the
coat front, a split graphite long coat (side panel to the shin + rear vent tail that swings), dark trousers, boots and gloves.
Signature: a folding tactical board carried in the far (left) hand as in the lexplore28 east view. It strikes edge-first at close
range (attack_range 65), opens into a two-panel shield for guard, and unfolds into a calibration display for the skill.
Skill "Tactical Calibration" (battle_skill_liang: allies set to focus + boost): board opens -> projected calibration grid ->
near-hand signal back toward the allies -> copper link ticks as the board folds shut.

Contract = heroine hsc19 / zcombat26: schema worlds-between.combat-sprite-set/1, 136x144 cell, pivot (64,136), authored facing
right, logical scale 0.5, display proportion "0.65", 30 tick/s, 6-column sheet, actions idle/move/guard/attack/dodge/skill/hit/
defeat, per-action total ticks equal to the heroine set. Character is {"member_id": "liang-xu"} with no appearance key; the
runtime index has only the "liang-xu" key (no hero key). Attack: the board strike contact (impact burst) is the FIRST attack frame
(tick 0), matching the existing immediate companion attack in battle_arena _try_attack; no timer or damage change is implied.
No victory poses. The combat static is the idle-a pose exported as its own named package.

    python -X utf8 -I <tool> build | check [--pixelorama EXE]
Writes only NEW files under outputs/lcombat29 and game/data/lcombat29.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, io, json, math, os, shutil, subprocess, sys, tempfile, zipfile
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/lcombat29"
PKG = ROOT / "game/data/lcombat29"
SLUG, SUBJECT, VER, STAMP, UID = "rpg-2-star-ocean-the-second", "liang-xu-combat", "unapproved-lcombat29-v01", "20261021-201025", "efc98984"
MEMBER = "liang-xu"
WRITER = ROOT / "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py"
HERO_MANIFEST = ROOT / "game/data/hsc19/rpg-2-star-ocean-the-second_heroine-sea-combat_pose-revision_spritesheet-manifest_20261021-034640-07587a3c.json"
HERO_SHEET = HERO_MANIFEST.with_name("rpg-2-star-ocean-the-second_heroine-sea-combat_pose-revision_spritesheet_20261021-034640-07587a3c.png")
MALE_SHEET = ROOT / "game/data/mcombat22/rpg-2-star-ocean-the-second_protagonist-male-combat_runtime-spritesheet_unapproved-v01_20261021-120000-a376c0d6.png"
ZHAO_SHEET = ROOT / "game/data/zcombat26/rpg-2-star-ocean-the-second_zhao-ling-combat_runtime-spritesheet_unapproved-zcombat26-v01_20261021-180157-340e10f5.png"
ZHAO_TOOL = "tools/rpg-2-star-ocean-the-second_zhao-ling_combat-static-and-actions-author_unapproved-zcombat26-v01_20261021-180157-5d3c9a71.py"
EXPLORE_TOOL = ROOT / "tools/rpg-2-star-ocean-the-second_liang-xu_explore-source-author_unapproved-lexplore28-v01_20261021-194350-3acdbd6e.py"
EXPLORE_EAST = "game/data/lexplore28/png/rpg-2-star-ocean-the-second_liang-xu_explore-east-static_unapproved-lexplore28-v01_20261021-194350-6d681674.png"
PORTRAIT = "outputs/rpg-2-star-ocean-the-second_liang-xu_character-sheet_v01_20261013-153556-c7630671.png"
W, H = 136, 144
PIN = (64, 136)
COLS = 6
TICK = 30
ZIP_DT = (2026, 10, 21, 20, 10, 24)
LAYERS = ["coat-back", "arm-back", "leg-back", "leg-front", "torso", "board", "head", "arm-front", "fx"]

PAL_HEX = {   # literal copy of the lexplore28 Liang PAL (Liang south pilot named ramps, unchanged)
    "K": "#0a0a0e", "k": "#1c1b24", "1": "#6a5654", "2": "#45383b", "3": "#251d20", "W": "#f6f4f0", "S": "#d2cfd6",
    "s": "#a09eac", "z": "#6e6c7e", "F": "#f2c49c", "f": "#d89c72", "e": "#ab6c4c", "d": "#7c4838", "y": "#3b2622",
    "L": "#b9bdc8", "A": "#8d92a0", "B": "#616574", "C": "#42454f", "D": "#272932", "N": "#5874ba", "n": "#3a4e88",
    "m": "#25305a", "T": "#555564", "t": "#34343f", "O": "#6e6064", "o": "#42373a", "q": "#221c20", "Q": "#ffc68a",
    "R": "#e08c4c", "r": "#a95b2f", "u": "#6b3521", "G": "#a0eaff", "g": "#3ba8e2"}
PAL = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in PAL_HEX.items()}
R_HAIR, R_SILV, R_SKIN = ("1", "2", "3"), ("W", "S", "s"), ("F", "f", "e")
R_COAT, R_COATD, R_COLL = ("A", "B", "C"), ("B", "C", "D"), ("N", "n", "m")
R_TROU, R_TROUD, R_BOOT, R_GLOVE = ("T", "t", "D"), ("t", "D", "q"), ("O", "o", "q"), ("o", "q", "k")
R_COPPER, R_BOARD, R_SCREEN = ("Q", "R", "r"), ("C", "D", "q"), ("G", "g", "m")

NEUTRAL_PELVIS = (62.0, 92.0)
THIGH, SHIN = 21.0, 21.0
UPPER, FORE = 13.0, 12.0
HEM_DROP = 24.0   # long coat hem below the pelvis (to the upper shin)

# Pose rows. pel: pelvis offset; lean: upper-body rotation (deg, + = toward the enemy); feet: ankle targets (sole row 135 when
# y=130); fh: near (right, free) hand offset from the shoulder; bh: far (left, board) hand offset from the shoulder;
# bdeg: board long-axis deg in the board hand (0 = +x level, + = down, -90 = up); fold: 0 folded slab | 1 opened two panels;
# hem: rear coat-tail follow-through (x); eyes: open|focus|read|shut|wince; fx: none|impact|trail|grid|signal|link;
# head: head offset.
D = dict(pel=(0, 0), lean=2.0, feet=((52, 130), (76, 130)), fh=(9, 16), bh=(10, 12), bdeg=-70.0, fold=0, hem=0,
         eyes="open", fx="none", head=(0, 0))


def pose(**kw):
    p = dict(D)
    p.update(kw)
    return p


P = {
    "idle-a": pose(),
    "idle-b": pose(pel=(0, 1), lean=3.0, fh=(9, 17), bh=(10, 13), bdeg=-66.0, hem=-1),
    "move-a": pose(pel=(1, 1), lean=7.0, feet=((49, 130), (81, 130)), fh=(5, 16), bh=(12, 11), bdeg=-60.0, hem=-3),
    "move-b": pose(pel=(3, -2), lean=6.0, feet=((56, 126), (79, 130)), fh=(7, 15), bh=(11, 12), bdeg=-64.0, hem=-5),
    "move-c": pose(pel=(4, 1), lean=7.0, feet=((55, 130), (85, 128)), fh=(11, 15), bh=(9, 12), bdeg=-60.0, hem=-3),
    "move-d": pose(pel=(3, -1), lean=6.0, feet=((53, 130), (82, 130)), fh=(8, 15), bh=(11, 11), bdeg=-64.0, hem=-4),
    "guard-in": pose(pel=(-1, 2), lean=-1.0, fh=(12, 4), bh=(15, 0), bdeg=-95.0, fold=1, hem=1, eyes="focus"),
    "guard-hold": pose(pel=(-2, 4), lean=-3.0, feet=((49, 130), (77, 130)), fh=(13, 0), bh=(16, -3), bdeg=-92.0, fold=1, hem=2,
                       eyes="focus"),
    "attack-strike": pose(pel=(3, 2), lean=9.0, feet=((50, 130), (84, 130)), fh=(-6, 14), bh=(22, -3), bdeg=12.0, hem=-4,
                          eyes="focus", fx="impact"),
    "attack-follow": pose(pel=(3, 3), lean=11.0, feet=((50, 130), (84, 130)), fh=(-5, 15), bh=(19, 7), bdeg=48.0, hem=-2,
                          eyes="focus", fx="trail"),
    "attack-fold": pose(pel=(1, 2), lean=5.0, feet=((51, 130), (81, 130)), fh=(3, 16), bh=(14, 6), bdeg=-25.0, hem=1, eyes="focus"),
    "attack-recover": pose(pel=(0, 1), lean=3.0, feet=((52, 130), (78, 130)), fh=(7, 16), bh=(11, 10), bdeg=-55.0, hem=1),
    "dodge-hop": pose(pel=(-9, -6), lean=9.0, feet=((40, 122), (62, 124)), fh=(4, 14), bh=(9, 12), bdeg=-50.0, hem=7, head=(0, 1)),
    "dodge-land": pose(pel=(-12, 9), lean=13.0, feet=((38, 130), (62, 130)), fh=(10, 13), bh=(13, 10), bdeg=-40.0, hem=5),
    "skill-open": pose(pel=(-1, 2), lean=4.0, feet=((51, 130), (76, 130)), fh=(13, 6), bh=(14, 4), bdeg=-8.0, fold=1, hem=0,
                       eyes="read", head=(0, 1)),
    "skill-grid": pose(pel=(0, 2), lean=1.0, feet=((51, 130), (77, 130)), fh=(14, 3), bh=(15, 3), bdeg=-14.0, fold=1, hem=-1,
                       eyes="read", fx="grid"),
    "skill-signal": pose(pel=(0, 2), lean=-4.0, feet=((51, 130), (78, 130)), fh=(-12, -6), bh=(15, 4), bdeg=-10.0, fold=1, hem=2,
                         eyes="focus", fx="signal", head=(-1, 0)),
    "skill-set": pose(pel=(1, 1), lean=2.0, feet=((51, 130), (78, 130)), fh=(9, 14), bh=(12, 9), bdeg=-60.0, fold=0, hem=0,
                      eyes="focus", fx="link"),
    "hit-recoil": pose(pel=(-6, 3), lean=-14.0, feet=((49, 130), (74, 130)), fh=(-4, 14), bh=(4, 14), bdeg=-110.0, hem=7,
                       eyes="wince", head=(-2, 0)),
    "hit-stagger": pose(pel=(-5, 6), lean=9.0, feet=((47, 130), (73, 130)), fh=(6, 17), bh=(10, 14), bdeg=-80.0, hem=4, eyes="wince"),
    "defeat-buckle": pose(pel=(-4, 10), lean=18.0, feet=((48, 130), (74, 130)), fh=(6, 19), bh=(9, 18), bdeg=70.0, hem=3, eyes="wince"),
    "defeat-knee": pose(pel=(-3, 22), lean=26.0, feet=((40, 130), (74, 130)), fh=(12, 21), bh=(14, 20), bdeg=95.0, hem=2, eyes="shut"),
    "defeat-down": pose(pel=(-2, 30), lean=40.0, feet=((36, 130), (66, 130)), fh=(16, 18), bh=(18, 17), bdeg=158.0, hem=2,
                        eyes="shut", head=(0, 2)),
}
KNEELING = {"defeat-knee": "back", "defeat-down": "both"}
AIRBORNE = {"dodge-hop"}
CELLS = list(P)
# Runtime timing (30 tick/s). Totals equal the heroine hsc19 set; the strike contact is attack frame 0 (tick 0).
ACTIONS = {
    "idle": {"loop": True, "loop_start": 0, "frames": [("idle-a", 14), ("idle-b", 14)]},
    "attack": {"loop": False, "frames": [("attack-strike", 2), ("attack-follow", 3), ("attack-fold", 3), ("attack-recover", 4), ("idle-a", 1)]},
    "move": {"loop": True, "loop_start": 0, "frames": [("move-a", 3), ("move-b", 3), ("move-c", 3), ("move-d", 3)]},
    "guard": {"loop": True, "loop_start": 1, "frames": [("guard-in", 2), ("guard-hold", 12)]},
    "dodge": {"loop": False, "frames": [("dodge-hop", 4), ("dodge-land", 4), ("idle-a", 1)]},
    "skill": {"loop": False, "frames": [("skill-open", 4), ("skill-grid", 3), ("skill-signal", 3), ("skill-set", 3), ("idle-a", 1)]},
    "hit": {"loop": False, "frames": [("hit-recoil", 3), ("hit-stagger", 4), ("idle-a", 1)]},
    "defeat": {"loop": False, "frames": [("defeat-buckle", 3), ("defeat-knee", 3), ("defeat-down", 3)]},
}
STRIKE_CUE_TICK = 0


def sha(b):
    return hashlib.sha256(b).hexdigest()


def long(p):
    return Path("\\\\?\\" + str(Path(p).resolve()))


def fid(role):
    return sha(f"{UID}:{role}".encode())[:8]


def name(purpose, ext):
    return f"{SLUG}_{SUBJECT}_{purpose}_{VER}_{STAMP}-{fid(purpose)}.{ext}"


def rel(p):
    return str(Path(p).relative_to(ROOT)).replace("\\", "/")


def png_bytes(a):
    buf = io.BytesIO()
    Image.fromarray(np.ascontiguousarray(a, np.uint8), "RGBA").save(buf, "PNG", optimize=False, compress_level=9)
    return buf.getvalue()


def decode(b):
    return np.array(Image.open(io.BytesIO(b)).convert("RGBA"))


def blank():
    return np.zeros((H, W, 4), np.uint8)


# ---------------------------------------------------------------- raster primitives (same as zcombat26 / mcombat22)
def _canvas():
    im = Image.new("L", (W, H), 0)
    return im, ImageDraw.Draw(im)


def m_poly(pts):
    im, d = _canvas()
    d.polygon([(round(x), round(y)) for x, y in pts], fill=1)
    return np.array(im, bool)


def m_cap(a, b, r):
    im, d = _canvas()
    d.line([(round(a[0]), round(a[1])), (round(b[0]), round(b[1]))], fill=1, width=max(1, round(2 * r)))
    for c in (a, b):
        d.ellipse([round(c[0] - r + 0.5), round(c[1] - r + 0.5), round(c[0] + r - 0.5), round(c[1] + r - 0.5)], fill=1)
    return np.array(im, bool)


def m_ell(c, rx, ry):
    im, d = _canvas()
    d.ellipse([round(c[0] - rx), round(c[1] - ry), round(c[0] + rx), round(c[1] + ry)], fill=1)
    return np.array(im, bool)


def shift(m, dy, dx):
    o = np.zeros_like(m)
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    o[yd, xd] = m[ys, xs]
    return o


def dil4(m):
    return m | shift(m, 1, 0) | shift(m, -1, 0) | shift(m, 0, 1) | shift(m, 0, -1)


def put(layer, mask, key):
    layer[mask, :3] = PAL[key]
    layer[mask, 3] = 255


def part(layer, mask, ramp, outline=True, band=2):
    if not mask.any():
        return
    if outline:
        put(layer, dil4(mask) & ~mask, "K")
    put(layer, mask, ramp[1])
    put(layer, mask & ~shift(mask, -band, -band), ramp[2])
    put(layer, mask & ~shift(mask, band, band), ramp[0])


def rot(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def ik(root, target, a, b, bend):
    dx, dy = target[0] - root[0], target[1] - root[1]
    d = math.hypot(dx, dy)
    stretch = max(0.0, d - (a + b))
    dd = min(max(d, 1e-6), a + b - 1e-6)
    ca = (a * a + dd * dd - b * b) / (2 * a * dd)
    ang = math.atan2(dy, dx)
    off = math.acos(max(-1.0, min(1.0, ca)))
    j1 = (root[0] + a * math.cos(ang - off), root[1] + a * math.sin(ang - off))
    j2 = (root[0] + a * math.cos(ang + off), root[1] + a * math.sin(ang + off))
    if bend > 0:
        j = j1 if j1[0] >= j2[0] else j2
    else:
        j = j1 if j1[1] >= j2[1] else j2
    return j, stretch


def local(origin, deg):
    """Map a point in an object's own frame (x along deg) to world."""
    return lambda x, y: add(origin, rot((x, y), deg))


def leg_joints(pid, hip, ankle, which):
    kneel = KNEELING.get(pid) in (which, "both")
    if kneel:
        dy = 131.0 - hip[1]
        stretch = max(0.0, abs(dy) - THIGH)
        knee = (hip[0] + math.sqrt(max(0.0, THIGH * THIGH - dy * dy)) * (0.35 if which == "back" else 0.8), 131.0)
        stretch = max(stretch, math.dist(hip, knee) - THIGH)
        ankle = (knee[0] - SHIN + 2, 131.0)
    else:
        knee, stretch = ik(hip, ankle, THIGH, SHIN, +1)
    return kneel, knee, ankle, stretch


# ---------------------------------------------------------------- the rig
def build(pid):
    p = P[pid]
    L = {n: blank() for n in LAYERS}
    pel = add(NEUTRAL_PELVIS, p["pel"])
    lean = p["lean"]

    def U(x, y):
        return add(pel, rot((x, y), lean))

    info = {"pelvis": [round(pel[0], 2), round(pel[1], 2)], "joints": {}}
    neck = U(1, -31)
    hc = add(add(neck, rot((2, -12), lean * 0.6)), p["head"])
    cx, cy = hc
    yy, xx = np.mgrid[0:H, 0:W]
    hips = {"back": U(-3, 0), "front": U(3, 0)}
    J = {w: leg_joints(pid, hips[w], p["feet"][0 if w == "back" else 1], w) for w in ("back", "front")}
    hem_y = pel[1] + HEM_DROP

    # rear vent tail of the split long coat (behind the legs), swings with hem
    h = p["hem"]
    bk = J["back"][1]
    part(L["coat-back"], m_poly([U(-10, -2), U(-3, -2), (bk[0] - 2 + h * 0.4, hem_y + 1), (bk[0] - 10 + h, hem_y + 2),
                                 (U(-11, 6)[0] - 2 + h * 0.6, (U(-11, 6)[1] + hem_y) / 2)]), R_COATD)
    put(L["coat-back"], m_cap((bk[0] - 9 + h, hem_y + 1), (bk[0] - 3 + h * 0.4, hem_y), 0.5), "D")       # tail hem line

    # legs: dark trousers, dark boots with a heel block
    def leg(layer, which, dark):
        kneel, knee, ankle, stretch = J[which]
        hip = hips[which]
        tr = R_TROUD if dark else R_TROU
        part(layer, m_cap(hip, knee, 4.4) | m_cap(knee, add(knee, ((ankle[0] - knee[0]) * 0.55, (ankle[1] - knee[1]) * 0.55)), 4.0), tr)
        top = add(knee, ((ankle[0] - knee[0]) * 0.5, (ankle[1] - knee[1]) * 0.5))
        if kneel:
            foot = m_poly([(ankle[0] - 3, ankle[1] - 3), (ankle[0] + 1, ankle[1] - 3), (ankle[0] + 1, 135), (ankle[0] - 9, 135), (ankle[0] - 9, 132)])
            lift = 0
        else:
            lift = 0 if ankle[1] >= 130 else ankle[1] - 130
            foot = m_poly([(ankle[0] - 4, ankle[1] - 4), (ankle[0] + 3, ankle[1] - 3), (ankle[0] + 9, 132 + lift), (ankle[0] + 9, 135 + lift),
                           (ankle[0] - 4, 135 + lift)])
        part(layer, m_cap(top, ankle, 3.6) | foot, R_BOOT)
        if not kneel:
            put(layer, m_cap((ankle[0] - 4, 134 + lift), (ankle[0] + 8, 134 + lift), 0.5), "q")              # sole line
            put(layer, m_cap((ankle[0] - 3, 133 + lift), (ankle[0] - 1, 133 + lift), 0.5), "k")              # heel block
        put(layer, m_cap(add(top, (-2, 1)), add(top, (2, 1)), 0.5), "o")                                     # boot top seam
        info["joints"][which] = {"hip": [round(hip[0], 2), round(hip[1], 2)], "knee": [round(knee[0], 2), round(knee[1], 2)],
                                 "ankle": [round(ankle[0], 2), round(ankle[1], 2)], "stretch": round(stretch, 3)}

    leg(L["leg-back"], "back", True)
    leg(L["leg-front"], "front", False)

    # torso: long graphite coat with navy high collar and copper placket; side skirt panel to the shin covers both thighs and
    # follows the knees (the split to the rear vent tail shows behind it)
    t = L["torso"]
    fk = J["front"][1]
    skirt = m_poly([U(-10, -1), U(9, -1), (max(fk[0] + 5, U(9, 0)[0] + 2), hem_y - 1), (min(bk[0] - 4, fk[0] - 8), hem_y),
                    (U(-11, 4)[0], (U(-11, 4)[1] + hem_y) / 2)])
    body = m_poly([U(-10, -30), U(7, -31), U(10, -18), U(9, 2), U(-10, 2), U(-11, -18)])
    part(t, skirt | body, R_COAT)
    put(t, m_cap((min(bk[0] - 3, fk[0] - 7), hem_y - 1), (min(bk[0] - 1, fk[0] - 4), (pel[1] + hem_y) / 2 + 2), 0.5), "D")  # vent split
    put(t, m_cap(U(8, -27), U(8, 1), 0.5), "R")                                              # copper placket line
    put(t, m_cap(U(8, 1), (max(fk[0] + 4, U(9, 0)[0] + 1), hem_y - 2), 0.5), "r")             # placket continues down the front edge
    for yy0 in (-22, -14, -6):
        put(t, m_cap(U(7, yy0), U(7, yy0), 0.6), "Q")                                         # copper studs
    part(t, m_poly([U(-10, -2), U(9, -2), U(9, 1), U(-10, 1)]), ("C", "D", "q"), band=1)      # belt
    put(t, m_cap(U(2, -1), U(3, -1), 0.6), "R")                                               # copper buckle
    put(t, m_cap(U(-7, -26), U(-5, -6), 0.5), "L")                                            # shoulder-to-hip light seam
    put(t, m_cap(U(-9, 6), (U(-9, 6)[0] + 1, hem_y - 4), 0.5), "C")                           # skirt fold
    part(t, m_poly([U(-6, -35), U(7, -35), U(9, -28), U(5, -26), U(-5, -27), U(-8, -30)]), R_COLL, band=1)   # navy high collar
    put(t, m_cap(U(7, -34), U(8, -28), 0.5), "R")                                             # copper collar edge

    # head: big Sea of Stars head, face toward the enemy; dark hair pinned up into a top-knot with a copper pin; silver streak
    # sweeping back over the near (right) temple; age cues: brow weight and a cheek line
    hd = L["head"]
    part(hd, m_cap(U(0, -34), U(3, -34), 2.6), R_SKIN, band=1)                                 # neck
    head = m_ell(hc, 10.5, 11.5)
    part(hd, head, R_SKIN)
    hair = (head & (yy < cy - 4)) | (head & (xx < cx - 1))
    hair |= m_ell((cx - 3, cy - 5), 10, 7)
    hair |= m_poly([(cx - 11, cy - 2), (cx - 10, cy + 6), (cx - 5, cy + 7), (cx - 2, cy + 2), (cx - 2, cy - 3)])   # nape, pulled back
    hair |= m_poly([(cx + 1, cy - 11), (cx + 10, cy - 8), (cx + 9, cy - 3), (cx + 4, cy - 6)])                      # short front line
    knot_c = (cx - 7, cy - 14)
    knot = m_ell(knot_c, 4.6, 4.0)
    part(hd, hair | knot, R_HAIR)
    put(hd, m_cap(add(knot_c, (-3, 1)), add(knot_c, (2, -2)), 0.5), "1")                       # knot highlight
    pin_a, pin_b = add(knot_c, (-8, 3)), add(knot_c, (7, -3))
    put(hd, dil4(m_cap(pin_a, pin_b, 0.6)) & ~m_cap(pin_a, pin_b, 0.6) & ~(hair | knot), "K")
    put(hd, m_cap(pin_a, pin_b, 0.6), "R")                                                    # copper hair pin through the knot
    put(hd, m_cap(pin_b, pin_b, 0.7), "Q")
    streak = m_poly([(cx + 4, cy - 8), (cx - 3, cy - 10), (cx - 8, cy - 8), (cx - 7, cy - 6), (cx - 2, cy - 7), (cx + 3, cy - 6)]) & hair
    put(hd, streak, "S")
    put(hd, streak & ~shift(streak, 1, 1), "W")
    put(hd, streak & ~shift(streak, -1, -1), "s")
    put(hd, m_cap((cx - 6, cy - 1), (cx - 4, cy + 4), 0.5), "3")                               # strand break over the ear
    part(hd, m_ell((cx - 1, cy + 1), 1.6, 2.4), R_SKIN, outline=False, band=1)                 # ear
    put(hd, m_cap((cx - 1, cy + 1), (cx - 1, cy + 2), 0.5), "e")
    ex, ey = round(cx + 6), round(cy + 1)
    if p["eyes"] in ("open", "focus"):
        hd[ey:ey + 3, ex:ex + 2, :3] = PAL["y"]
        hd[ey + 1, ex + 1, :3] = PAL["n"]
        if p["eyes"] == "focus":
            hd[ey - 1, ex - 1:ex + 3, :3] = PAL["3"]                                          # narrowed lid
    elif p["eyes"] == "read":
        hd[ey + 1:ey + 3, ex:ex + 2, :3] = PAL["y"]                                           # eyes lowered to the board
        hd[ey, ex - 1:ex + 3, :3] = PAL["3"]
    elif p["eyes"] == "shut":
        hd[ey + 1, ex - 1:ex + 3, :3] = PAL["3"]
    else:
        hd[ey, ex:ex + 3, :3] = PAL["3"]
        hd[ey + 1, ex - 1, :3] = PAL["3"]
        hd[ey + 1, ex + 3, :3] = PAL["3"]
    hd[ey - 2, ex - 1:ex + 4, :3] = PAL["y"]                                                  # heavy brow
    hd[ey + 4, ex - 1, :3] = PAL["e"]                                                         # cheek line (age cue)
    hd[ey + 5, ex, :3] = PAL["e"]
    hd[round(cy + 7), round(cx + 6):round(cx + 9), :3] = PAL["d"]                             # mouth

    # arms: graphite sleeve -> navy cuff -> dark glove
    def arm(layer, sh, off, front):
        hand = add(sh, off)
        el, stretch = ik(sh, hand, UPPER, FORE, -1)
        cuff = add(el, ((hand[0] - el[0]) * 0.62, (hand[1] - el[1]) * 0.62))
        part(layer, m_cap(sh, el, 3.9) | m_cap(el, cuff, 3.4), R_COAT if front else R_COATD)
        part(layer, m_cap(cuff, add(cuff, ((hand[0] - cuff[0]) * 0.3, (hand[1] - cuff[1]) * 0.3)), 3.0), R_COLL, band=1)
        part(layer, m_ell(hand, 2.9, 2.9), R_GLOVE, band=1)
        info["joints"]["arm-front" if front else "arm-back"] = {"shoulder": [round(sh[0], 2), round(sh[1], 2)],
                                                               "elbow": [round(el[0], 2), round(el[1], 2)],
                                                               "hand": [round(hand[0], 2), round(hand[1], 2)], "stretch": round(stretch, 3)}
        return hand

    bhand = arm(L["arm-back"], U(-2, -27), p["bh"], False)
    hand = arm(L["arm-front"], U(3, -26), p["fh"], True)

    # folding tactical board in the far (left) hand: folded = a thick graphite slab with a copper hinge edge; opened = two panels
    # with a copper frame, centre hinge and a cyan display face
    B = local(bhand, p["bdeg"])
    bd = L["board"]
    if p["fold"]:
        face = m_poly([B(-3, -10), B(19, -10), B(19, 10), B(-3, 10)])
        part(bd, face, R_BOARD, band=1)
        put(bd, m_poly([B(-1, -8), B(17, -8), B(17, -1), B(-1, -1)]) | m_poly([B(-1, 1), B(17, 1), B(17, 8), B(-1, 8)]), "g")
        put(bd, m_poly([B(0, -7), B(9, -7), B(9, -4), B(0, -4)]), "G")
        put(bd, m_cap(B(1, 4), B(15, 4), 0.5), "G")                                         # display trace
        put(bd, m_cap(B(-2, 0), B(18, 0), 0.6), "R")                                         # centre hinge
        for c in (B(-2, -9), B(18, -9), B(-2, 9), B(18, 9)):
            put(bd, m_cap(c, c, 0.7), "Q")                                                   # copper corners
        tip = B(19, 0)
    else:
        slab = m_poly([B(-3, -3), B(19, -3), B(19, 3), B(-3, 3)])
        part(bd, slab, R_BOARD, band=1)
        put(bd, m_cap(B(-2, -2), B(18, -2), 0.5), "R")                                       # copper hinge edge
        put(bd, m_cap(B(0, 1), B(16, 1), 0.5), "g")                                          # display seam peeking at the fold
        put(bd, m_cap(B(18, -2), B(18, 2), 0.6), "Q")                                        # copper end cap
        tip = B(19, 0)
    put(bd, m_ell(bhand, 2.4, 2.4), "q")                                                      # gripping fingers over the frame
    info["board"] = {"grip": [round(bhand[0], 2), round(bhand[1], 2)], "tip": [round(tip[0], 2), round(tip[1], 2)],
                     "deg": p["bdeg"], "open": bool(p["fold"])}

    # fx (own layer, no outline): strike impact, follow-through trail, calibration grid, ally signal, copper link ticks
    fx = L["fx"]
    if p["fx"] == "impact":
        F = local(tip, p["bdeg"])
        put(fx, m_poly([F(0, -6), F(9, 0), F(0, 6), F(4, 0)]), "R")
        put(fx, m_poly([F(1, -3), F(13, 0), F(1, 3)]), "Q")
        put(fx, m_cap(F(2, -9), F(6, -12), 0.5) | m_cap(F(2, 9), F(6, 12), 0.5) | m_cap(F(6, 0), F(10, 0), 0.5), "W")
    elif p["fx"] == "trail":
        rr = np.hypot(xx - bhand[0], yy - bhand[1])
        aa = np.degrees(np.arctan2(yy - bhand[1], xx - bhand[0]))
        for r0, k in ((17, "g"), (20, "G")):
            put(fx, (np.abs(rr - r0) <= 0.6) & (aa > -6) & (aa < 40), k)
    elif p["fx"] == "grid":
        g0 = B(8, -14)
        gx0, gy0 = round(g0[0]) - 10, round(g0[1]) - 18
        grid = np.zeros((H, W), bool)
        for i in range(0, 21, 5):
            grid |= m_cap((gx0 + i, gy0), (gx0 + i, gy0 + 14), 0.5)
        for j in range(0, 15, 7):
            grid |= m_cap((gx0, gy0 + j), (gx0 + 20, gy0 + j), 0.5)
        put(fx, grid & (xx % 2 == (yy % 2)), "g")
        put(fx, m_cap((gx0 + 10, gy0 + 7), (gx0 + 10, gy0 + 7), 0.8), "Q")                     # calibrated point
        put(fx, m_cap((gx0 + 5, gy0 + 14), (gx0 + 15, gy0 + 0), 0.5), "G")                      # vector line
    elif p["fx"] == "signal":
        for k, dx in enumerate((-4, -9, -14)):
            c = add(hand, (dx, 0))
            put(fx, m_cap(add(c, (2, -3)), c, 0.5) | m_cap(c, add(c, (2, 3)), 0.5), "Q" if k == 0 else "R")   # chevrons back to allies
    elif p["fx"] == "link":
        for c in (add(bhand, (-14, -16)), add(bhand, (-22, -10)), add(bhand, (-6, -22))):
            put(fx, m_cap(c, add(c, (2, 0)), 0.5) | m_cap(add(c, (1, -1)), add(c, (1, 1)), 0.5), "R")
    for n in LAYERS:   # nothing below the sole row or outside the 1-texel margin
        L[n][PIN[1]:] = 0
        L[n][:, :1] = 0
        L[n][:, -1:] = 0
        L[n][:2] = 0
    return L, info


def flatten(L):
    flat = blank()
    for n in LAYERS:
        m = L[n][..., 3] > 0
        flat[m] = L[n][m]
    return flat


def ora_bytes(L, flat):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", ZIP_DT), "image/openraster", zipfile.ZIP_STORED)
        st = ['<?xml version="1.0" encoding="UTF-8"?>', f'<image version="0.0.3" w="{W}" h="{H}">', "<stack>"]
        for i, n in reversed(list(enumerate(LAYERS))):
            st.append(f'<layer name="{n}" src="data/{i:02d}-{n}.png" x="0" y="0" opacity="1.0" visibility="visible" composite-op="svg:src-over"/>')
        st += ["</stack>", "</image>"]
        z.writestr(zipfile.ZipInfo("stack.xml", ZIP_DT), "\n".join(st) + "\n", zipfile.ZIP_DEFLATED)
        for i, n in enumerate(LAYERS):
            z.writestr(zipfile.ZipInfo(f"data/{i:02d}-{n}.png", ZIP_DT), png_bytes(L[n]), zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("mergedimage.png", ZIP_DT), png_bytes(flat), zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("Thumbnails/thumbnail.png", ZIP_DT), png_bytes(flat), zipfile.ZIP_DEFLATED)
    return buf.getvalue()


def writer():
    spec = importlib.util.spec_from_file_location("established_pxo_writer", str(WRITER))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.W, m.H = W, H
    m.to_rgba = lambda im: np.ascontiguousarray(im, np.uint8)
    return m


def frames_json(spec):
    return [{"cell": CELLS.index(pid), "ticks": t} for pid, t in spec["frames"]]


def outputs():
    wr = writer()
    built = {pid: build(pid) for pid in P}
    files, flats = {}, {}
    for pid, (L, info) in built.items():
        flat = flatten(L)
        flats[pid] = flat
        png = png_bytes(flat)
        files[f"{pid}.png"] = (OUT, name(f"{pid}-native136", "png"), png)
        files[f"{pid}.ora"] = (OUT, name(f"{pid}-layered", "ora"), ora_bytes(L, flat))
        files[f"{pid}.pxo"] = (OUT, name(f"{pid}-editable", "pxo"), wr.make_pxo([L], [1.0], png, name(f"{pid}-pxo-export", "png"), TICK,
                                                                             order=LAYERS, dt=ZIP_DT))
    L0 = built["idle-a"][0]
    files["still.png"] = (OUT, name("battle-still-native136", "png"), png_bytes(flats["idle-a"]))
    files["still.ora"] = (OUT, name("battle-still-layered", "ora"), ora_bytes(L0, flats["idle-a"]))
    files["still.pxo"] = (OUT, name("battle-still-editable", "pxo"), wr.make_pxo([L0], [1.0], files["still.png"][2],
                                                                                 name("battle-still-pxo-export", "png"), TICK, order=LAYERS, dt=ZIP_DT))
    rows = math.ceil(len(CELLS) / COLS)
    sheet = np.zeros((rows * H, COLS * W, 4), np.uint8)
    for i, pid in enumerate(CELLS):
        sheet[(i // COLS) * H:(i // COLS + 1) * H, (i % COLS) * W:(i % COLS + 1) * W] = flats[pid]
    sheet_b = png_bytes(sheet)
    sheet_n = name("runtime-spritesheet", "png")
    files["sheet"] = (OUT, sheet_n, sheet_b)
    files["pkg.sheet"] = (PKG, sheet_n, sheet_b)
    manifest = {
        "schema": "worlds-between.combat-sprite-set/1", "set_id": "liang-xu-combat-lcombat29-v01",
        "character": {"member_id": MEMBER},
        "art_status": "unapproved-liang-xu-combat-source-poses-technical-only", "art_approved": False, "motion_approved": False,
        "default_adoption": False,
        "note": "Deterministic authored source set for Liang Xu (folding tactical board signature, Tactical Calibration skill); not "
                "creator-approved art or motion, not a default, not wired. Loadable only through the explicit member-only lcombat29 index.",
        "source_provenance": name("author-manifest", "json"), "sheet": sheet_n, "cell_size": [W, H], "pivot": list(PIN),
        "authored_facing": "right", "logical_scale": 0.5, "display_proportion": "0.65",
        "actions": {a: ({"loop": True, "loop_start": s["loop_start"]} if s["loop"] else {"loop": False}) | {"tick_rate": TICK, "frames": frames_json(s)}
                    for a, s in ACTIONS.items()},
    }
    man_b = (json.dumps(manifest, indent=2) + "\n").encode()
    man_n = name("runtime-spritesheet-manifest", "json")
    files["manifest"] = (OUT, man_n, man_b)
    files["pkg.manifest"] = (PKG, man_n, man_b)
    index = {"schema": "worlds-between.combat-sprite-set-index/1", "sets": {MEMBER: man_n}}
    idx_b = (json.dumps(index, indent=2) + "\n").encode()
    files["pkg.index"] = (PKG, name("runtime-index", "json"), idx_b)
    author = {
        "status": "UNAPPROVED Liang Xu combat static + eight-action source set; technical source only; runtime default unchanged.",
        "member_id": MEMBER, "architectureFrom": ZHAO_TOOL, "paletteFrom": rel(EXPLORE_TOOL),
        "identityReference": {"portraitConcept": PORTRAIT, "portraitIsConceptNotApproval": True, "exploreEastStatic": EXPLORE_EAST},
        "identity": "tactical mentor, age 46; pinned dark hair with copper pin, silver temple streak, navy high collar, copper placket, "
                    "split graphite long coat, folding tactical board in the far (left) hand",
        "contractFrom": rel(HERO_MANIFEST), "layers": LAYERS, "cell": [W, H], "pivot": list(PIN), "tickRate": TICK,
        "signature": "folding tactical board: edge-first close-range strike (attack_range 65), opened two-panel guard; no gun, no blade",
        "skill": "Tactical Calibration: board opens -> calibration grid -> signal to allies -> link ticks as the board folds",
        "mechanicsRead": {"file": "game/scripts/app_state.gd MEMBER_DEFS liang-xu + game/scripts/battle_arena.gd _try_attack/_use_skill",
                          "attack_damage": 16, "attack_range": 65.0, "attack_cooldown_s": 0.43, "skill_energy_cost": 16,
                          "skill_cooldown_s": 2.2, "skill_effect": "allies command=focus, boost += 4*rank", "damage": "immediate on attack press"},
        "combatStatic": {"pose": "idle-a", "png": files["still.png"][1], "ora": files["still.ora"][1], "pxo": files["still.pxo"][1]},
        "runtimeActions": {a: {"frames": [[pid, t] for pid, t in s["frames"]], "loop": s["loop"], "totalTicks": sum(t for _, t in s["frames"])}
                           for a, s in ACTIONS.items()},
        "strikeCueTick": STRIKE_CUE_TICK,
        "strikeCueNote": "board strike contact (impact burst) is attack frame 0 (tick 0), matching the existing immediate companion attack; "
                         "no timer or damage change",
        "poses": {pid: {"params": {k: (list(map(list, v)) if k == "feet" else (list(v) if isinstance(v, tuple) else v)) for k, v in P[pid].items()},
                        "rig": built[pid][1], "runtimeCell": CELLS.index(pid)} for pid in P},
        "source": {"file": rel(Path(__file__).resolve()), "sha256TextLf": sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n")),
                   "textHashNormalization": "sha256-text-lf-v1 (CRLF->LF)"},
        "files": {role: {"path": rel(d / n), "sha256": sha(b)} for role, (d, n, b) in sorted(files.items())},
        "artApproved": False, "motionApproved": False, "runtimeDefaultChanged": False, "guiSaveAsVerified": False,
    }
    a_b = (json.dumps(author, indent=1) + "\n").encode()
    files["author"] = (OUT, name("author-manifest", "json"), a_b)
    files["pkg.author"] = (PKG, name("author-manifest", "json"), a_b)
    return files, flats, built, manifest, index


def lexplore28_palette():
    spec = importlib.util.spec_from_file_location("wb_lexplore28_author", str(EXPLORE_TOOL))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return {k: tuple(v) for k, v in m.RGB.items()}


def gates(files, flats, built, manifest, index):
    res = []

    def gate(k, ok, info=None):
        res.append({"key": k, "pass": bool(ok), "info": info})
    lx_pal = lexplore28_palette()
    gate("palette == lexplore28 author PAL (same keys, same RGB)", lx_pal == PAL, sorted(set(lx_pal) ^ set(PAL)))
    pal = set(PAL.values())
    for pid, flat in flats.items():
        op = flat[..., 3] > 0
        ys, xs = np.nonzero(op)
        cols = {tuple(c) for c in flat[op][:, :3].tolist()}
        L, info = built[pid]
        gate(f"{pid}: binary alpha + declared Liang palette only", set(np.unique(flat[..., 3]).tolist()) <= {0, 255} and cols <= pal, len(cols))
        gate(f"{pid}: margins clear, nothing below sole row", ys.min() >= 2 and xs.min() >= 1 and xs.max() <= W - 2 and ys.max() <= PIN[1] - 1,
             [int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())])
        if pid in AIRBORNE:
            gate(f"{pid}: airborne (lowest row 120..133)", 120 <= ys.max() <= 133, int(ys.max()))
        else:
            gate(f"{pid}: grounded (lowest row 135)", ys.max() == PIN[1] - 1, int(ys.max()))
        st = max(j["stretch"] for j in info["joints"].values())
        gate(f"{pid}: no limb stretch beyond 0.6 texel", st <= 0.6, st)
        filled = [n for n in LAYERS if (L[n][..., 3] > 0).any()]
        need = len(LAYERS) - (0 if P[pid]["fx"] != "none" else 1)
        gate(f"{pid}: real editable layers (all role layers non-empty, fx only when used)", len(filled) == need, len(filled))
        z = zipfile.ZipFile(io.BytesIO(files[f"{pid}.ora"][2]))
        zp = zipfile.ZipFile(io.BytesIO(files[f"{pid}.pxo"][2]))
        cels = [np.frombuffer(zp.read(f"image_data/frames/1/layer_{i}"), np.uint8).reshape(H, W, 4) for i in range(1, len(LAYERS) + 1)]
        pxo_flat = blank()
        for c in cels:
            pxo_flat[c[..., 3] > 0] = c[c[..., 3] > 0]
        gate(f"{pid}: PNG == layer composite == ORA merged; ORA layers == PXO cels == source layers",
             np.array_equal(decode(files[f"{pid}.png"][2]), flat) and np.array_equal(decode(z.read("mergedimage.png")), flat)
             and np.array_equal(pxo_flat, flat)
             and all(np.array_equal(c, L[n]) and np.array_equal(decode(z.read(f"data/{i:02d}-{n}.png")), L[n]) for i, (c, n) in enumerate(zip(cels, LAYERS))))
        ident = {k: int(sum(np.all(flat[..., :3] == PAL[c], -1)[op].sum() for c in r)) for k, r in
                 (("dark hair", "123"), ("silver streak", "WSs"), ("graphite coat", "ABC"), ("navy collar/cuffs", "Nnm"),
                  ("copper pin/placket", "QRr"), ("board display", "Gg"), ("skin", "Ff"))}
        gate(f"{pid}: Liang identity cues present (hair/silver/coat/collar/copper/board/skin texels)", all(v >= 4 for v in ident.values()), ident)
        gate(f"{pid}: no handgun/knife/tablet copied (Zhao gun/jacket and male scarf/coat/leather RGB absent)",
             not ({(0xd7, 0xdc, 0xe2), (0x8f, 0x98, 0xa8), (0x66, 0x6a, 0x7d), (0x82, 0xc8, 0xb8), (0x8c, 0x76, 0x64), (0xb2, 0x7c, 0x4e)} & cols))
    gate("all pose images unique", len({sha(files[f'{p}.png'][2]) for p in P}) == len(P))
    for a, s in ACTIONS.items():
        ids = [pid for pid, _ in s["frames"]]
        diffs = [int((np.any(flats[x] != flats[y], -1)).sum()) for x, y in zip(ids, ids[1:])]
        gate(f"{a}: consecutive frames visibly different (>= 60 texels)", all(d >= 60 for d in diffs), diffs)
    hero = json.loads(HERO_MANIFEST.read_text(encoding="utf-8"))
    gate("manifest top-level keys == heroine hsc19 manifest", list(manifest) == list(hero), [k for k in hero if k not in manifest])
    gate("character is member-only liang-xu (no appearance key)", manifest["character"] == {"member_id": MEMBER})
    gate("index has exactly the liang-xu key, no hero key, names the manifest",
         list(index["sets"]) == [MEMBER] and not any(k.startswith("hero") for k in index["sets"]) and index["sets"][MEMBER] == files["pkg.manifest"][1])
    req = {"idle": True, "move": True, "guard": True, "attack": False, "dodge": False, "hit": False, "defeat": False}
    gate("eight canonical actions: required with loop flags + skill",
         all(manifest["actions"][a]["loop"] == l for a, l in req.items()) and set(manifest["actions"]) == set(req) | {"skill"})
    gate("contract fields == heroine (cell, pivot, facing, scale, proportion)",
         all(manifest[k] == hero[k] for k in ("cell_size", "pivot", "authored_facing", "logical_scale", "display_proportion")))
    gate("cell and pivot even (logical scale 0.5)", W % 2 == 0 and H % 2 == 0 and PIN[0] % 2 == 0 and PIN[1] % 2 == 0)
    tot = lambda m, a: sum(f["ticks"] for f in m["actions"][a]["frames"])
    gate("every action duration == heroine (ticks)", all(tot(manifest, a) == tot(hero, a) for a in hero["actions"]),
         {a: [tot(manifest, a), tot(hero, a)] for a in hero["actions"]})
    gate("tick schema: every action tick_rate 30, frames use ticks only, loop_start only on loops",
         all(v["tick_rate"] == TICK and all(set(f) == {"cell", "ticks"} and f["ticks"] > 0 for f in v["frames"])
             and (("loop_start" in v) == v["loop"]) for v in manifest["actions"].values()))
    first = ACTIONS["attack"]["frames"][0][0]
    gate("strike cue (impact burst) on attack frame 0 = tick 0; no other attack frame has an impact",
         first == "attack-strike" and P[first]["fx"] == "impact" and STRIKE_CUE_TICK == 0 and manifest["actions"]["attack"]["frames"][0]["cell"] == CELLS.index(first)
         and all(P[pid]["fx"] != "impact" for pid, _ in ACTIONS["attack"]["frames"][1:]))
    sb = built["attack-strike"][1]
    gate("strike: folded board extended edge-first ahead of the body (tip >= pelvis + 30 px)",
         not sb["board"]["open"] and sb["board"]["tip"][0] >= sb["pelvis"][0] + 30, [sb["board"]["tip"], sb["pelvis"]])
    gate("follow-through: board swings down after the strike (deg increases), then folds back up",
         P["attack-follow"]["bdeg"] > P["attack-strike"]["bdeg"] > P["attack-fold"]["bdeg"])
    gate("guard opens the board into a two-panel shield held upright in front",
         all(P[x]["fold"] == 1 and P[x]["bdeg"] <= -80 for x in ("guard-in", "guard-hold")))
    gate("skill = Tactical Calibration (board open, grid, ally signal, link ticks as the board folds)",
         P["skill-open"]["fold"] == 1 and [P[x]["fx"] for x, _ in ACTIONS["skill"]["frames"][1:4]] == ["grid", "signal", "link"]
         and P["skill-set"]["fold"] == 0 and P["skill-signal"]["fh"][0] < 0)
    gate("defeat ends kneeling with eyes shut and the board down", P["defeat-down"]["eyes"] == "shut" and KNEELING["defeat-down"] == "both"
         and abs(P["defeat-down"]["bdeg"]) > 150)
    sheet = decode(files["sheet"][2])
    gate("sheet is a cell multiple, 6 columns, each cell == its pose PNG; package copy == outputs copy",
         sheet.shape[1] == COLS * W and sheet.shape[0] % H == 0 and files["sheet"][2] == files["pkg.sheet"][2] and
         all(np.array_equal(sheet[(i // COLS) * H:(i // COLS + 1) * H, (i % COLS) * W:(i % COLS + 1) * W], flats[pid]) for i, pid in enumerate(CELLS)))
    mo = flats["idle-a"][..., 3] > 0
    for lab, path in (("heroine", HERO_SHEET), ("male mcombat22", MALE_SHEET), ("Zhao zcombat26", ZHAO_SHEET)):
        o = np.array(Image.open(path).convert("RGBA"))[0:H, 0:W, 3] > 0
        iou = float((o & mo).sum() / (o | mo).sum())
        gate(f"idle silhouette distinct from {lab} idle (IoU < 0.85, not a recolour)", iou < 0.85, round(iou, 3))
    gate("still package pixels == idle-a", files["still.png"][2] == files["idle-a.png"][2])
    gate("all asset names <= 140 chars and in project/subject/purpose/variant/timestamp-id form",
         all(len(n) <= 140 and n.startswith(f"{SLUG}_{SUBJECT}_") and f"_{VER}_{STAMP}-" in n for _, n, _ in files.values()))
    gate("unique names (no two roles share a file name in the same directory)",
         len({(str(d), n) for d, n, _ in files.values()}) == len({(str(d), n, sha(b)) for d, n, b in files.values()}))
    return res


def pixelorama_export(exe, src, out_dir, split):
    env = dict(os.environ)
    env["APPDATA"] = tempfile.mkdtemp(prefix="wb-pxappdata-")
    args = [exe, "--headless", "--quit", "--", "--export"] + (["--split-layers"] if split else []) + ["-o", os.path.join(out_dir, "f.png"), src]
    try:
        p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300, env=env)
    finally:
        shutil.rmtree(env["APPDATA"], ignore_errors=True)
    outs = sorted(f for f in os.listdir(out_dir) if f.lower().endswith(".png"))
    return p, {f: Path(os.path.join(out_dir, f)).read_bytes() for f in outs}


def native(exe, files, built):
    """Open every PXO in installed Pixelorama headless, export flat (all) and split layers (still + representative poses)."""
    out, fails = [], []
    split_ids = {"still", "attack-strike", "skill-grid", "guard-hold", "defeat-down"}
    for role in sorted(r for r in files if r.endswith(".pxo")):
        pid = role[:-4]
        pxo = str(long(OUT / files[role][1]))
        want = decode(files[f"{pid}.png"][2])
        layers = built["idle-a" if pid == "still" else pid][0]
        rec = {"pxo": files[role][1]}
        for split in ([False, True] if pid in split_ids else [False]):
            tmp = tempfile.mkdtemp(prefix="wb-lc29-")
            try:
                p, outs = pixelorama_export(exe, pxo, tmp, split)
                diag = [ln.strip() for ln in (p.stdout + p.stderr).splitlines() if any(t in ln for t in ("ERROR", "SCRIPT ERROR", "WARNING"))]
                names = sorted(outs)
                if split:
                    got = {n: decode(outs[n]) for n in names}
                    src = [n for n in LAYERS if (layers[n][..., 3] > 0).any()]
                    matched = sum(1 for n in src if any(np.array_equal(g, layers[n]) for g in got.values()))
                    ok = p.returncode == 0 and matched == len(src)
                    rec["split"] = {"exit": p.returncode, "exported": len(names), "matched": f"{matched}/{len(src)}", "diagnostics": diag[:8]}
                else:
                    eq = len(names) == 1 and np.array_equal(decode(outs[names[0]]), want)
                    ok = p.returncode == 0 and eq
                    rec["flat"] = {"exit": p.returncode, "exported": len(names), "equal": bool(eq), "diagnostics": diag[:8]}
                if any("SCRIPT ERROR" in d for d in diag):
                    ok = False
                if not ok:
                    fails.append(f"native {pid} {'split' if split else 'flat'}")
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
        out.append(rec)
    return out, fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["build", "check"])
    ap.add_argument("--pixelorama")
    a = ap.parse_args()
    files, flats, built, manifest, index = outputs()
    det = all(files[k][2] == b for k, (_, n, b) in outputs()[0].items())
    res = [{"key": "deterministic rebuild", "pass": det, "info": None}] + gates(files, flats, built, manifest, index)
    if a.mode == "build" and any(not r["pass"] for r in res):
        print("BUILD REFUSED: source gates failed; nothing written")
    elif a.mode == "build":
        for role, (d, n, b) in files.items():
            os.makedirs(long(d), exist_ok=True)
            p = long(d / n)
            if p.exists():
                assert p.read_bytes() == b, f"refusing to overwrite a different file: {n}"
            else:
                p.write_bytes(b)
        lst = {"schema": "lcombat29-file-list/1", "files": [{"role": r, "path": rel(d / n), "sha256": sha(b)} for r, (d, n, b) in sorted(files.items())]}
        lp = long(OUT / name("file-list", "json"))
        data = (json.dumps(lst, indent=1) + "\n").encode()
        if not lp.exists() or lp.read_bytes() != data:
            lp.write_bytes(data)
    else:
        for role, (d, n, b) in files.items():
            p = long(d / n)
            res.append({"key": f"on-disk bytes equal rebuild: {role}", "pass": p.exists() and p.read_bytes() == b, "info": None})
    nat = None
    if a.mode == "check" and a.pixelorama:
        nat, nf = native(a.pixelorama, files, built)
        res.append({"key": "Pixelorama native open/export equality (flat all PXOs; split layers still/attack-strike/skill-grid/guard-hold/defeat-down)",
                    "pass": not nf, "info": nf})
    fails = [r for r in res if not r["pass"]]
    for r in fails:
        print("FAIL", r["key"], r["info"])
    diags = sorted({d for r in (nat or []) for v in r.values() if isinstance(v, dict) for d in v["diagnostics"]})
    if diags:
        print("PIXELORAMA DIAGNOSTICS (disclosed):", len(diags), "unique lines")
        for d in diags[:10]:
            print("  ", d[:200])
    print("LCOMBAT29", a.mode.upper(), "PASS" if not fails else "FAIL", f"{len(res) - len(fails)}/{len(res)}")
    if a.mode == "check":
        rep = name("source-check-report-pixelorama" if a.pixelorama else "source-check-report", "json")
        os.makedirs(long(OUT), exist_ok=True)
        with open(long(OUT / rep), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"mode": "check", "pixelorama": a.pixelorama, "gates": res, "native": nat, "diagnostics": diags,
                                "passed": len(res) - len(fails), "total": len(res)}, indent=1, ensure_ascii=False) + "\n")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
