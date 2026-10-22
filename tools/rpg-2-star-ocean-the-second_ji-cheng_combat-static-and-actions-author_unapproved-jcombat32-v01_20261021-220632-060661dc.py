"""Ji Cheng (纪澄, member_id ji-cheng) side-view combat static + eight source actions (jcombat32). UNAPPROVED, NOT A DEFAULT.

Reuses the lcombat29 / zcombat26 architecture (tools/...liang-xu_combat-static-and-actions-author_unapproved-lcombat29-v01...
efc98984.py, itself the mcombat22 method): every pose is a parameter row, a small rig (two-bone IK legs/arms, upper body rotated
about the pelvis, axis-aligned big Sea of Stars head) turns it into editable role layers, each part with a 1-texel near-black
outline and upper-left light / lower-right shadow planes. Raster primitives, ORA layout and the established PXO writer (female
south-run v06 make_pxo) are the same code; the body, costume, hair, props and fx below are Ji Cheng's own (not a Liang recolour,
no board, no gun, no blade; the old 32x48 Ji prototype is not read).

Identity (jexplore31 exploration identity; palette = the jexplore31 author PAL, i.e. the Ji Cheng south pilot named ramps, copied
literally and checked against the jexplore31 module at check time): records restorer, age 28, female. Straight blue-black
shoulder bob with jagged silver tips, shaved LEFT temple with razor lines and a rectangular brass drop earring, ink-green long open
coat with an uneven hem (long ragged point, cut-away front), cream uneven cloth panels, grey rolled sleeve lining, black high
collar, brown leather harness/belt with silver vials and a pouch, thigh strap, charcoal trousers, black buckled boots. Signature:
a brass folding magnifier in the near (right) hand and a small leather-bound book in the far (left) hand, as in the jexplore31
east view. Authored facing right, so her RIGHT side faces the viewer: the long silver-tipped curtain is the near side; the shaved
left temple is on the FAR side and only reads as the undercut wrap at the back of the head plus the drop-earring glint below it
(disclosed limitation, not a redesign of the identity).
Attack (attack_range 100, attack_damage 12): the magnifier is snapped forward at arm's length and focuses a lens flare into a
light lance toward the enemy (contact = flare on attack frame 0, tick 0, matching the existing immediate companion attack in
battle_arena _try_attack; no timer or damage change). Skill "Fault-Line Recall" (断层回读; battle_skill_ji: enemy windup/cooldown
+0.65*rank): book opens -> magnifier read over the page -> fault-line trace projected ahead -> recall brackets on the enemy line
as the book closes. Guard raises the closed book cover-out in front of the face. No victory poses. The combat static is the
idle-a pose exported as its own named package.

Contract = heroine hsc19 / lcombat29: schema worlds-between.combat-sprite-set/1, 136x144 cell, pivot (64,136), authored facing
right, logical scale 0.5, display proportion "0.65", 30 tick/s, 6-column sheet, actions idle/move/guard/attack/dodge/skill/hit/
defeat, per-action total ticks equal to the heroine set. Character is {"member_id": "ji-cheng"} with no appearance key; the
runtime index has only the "ji-cheng" key (no hero key).

    python -X utf8 -I <tool> build | check [--pixelorama EXE]
Writes only NEW files under outputs/jcombat32 and game/data/jcombat32.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, io, json, math, os, shutil, subprocess, sys, tempfile, zipfile
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/jcombat32"
PKG = ROOT / "game/data/jcombat32"
SLUG, SUBJECT, VER, STAMP, UID = "rpg-2-star-ocean-the-second", "ji-cheng-combat", "unapproved-jcombat32-v01", "20261021-220632", "060661dc"
MEMBER = "ji-cheng"
WRITER = ROOT / "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py"
HERO_MANIFEST = ROOT / "game/data/hsc19/rpg-2-star-ocean-the-second_heroine-sea-combat_pose-revision_spritesheet-manifest_20261021-034640-07587a3c.json"
HERO_SHEET = HERO_MANIFEST.with_name("rpg-2-star-ocean-the-second_heroine-sea-combat_pose-revision_spritesheet_20261021-034640-07587a3c.png")
MALE_SHEET = ROOT / "game/data/mcombat22/rpg-2-star-ocean-the-second_protagonist-male-combat_runtime-spritesheet_unapproved-v01_20261021-120000-a376c0d6.png"
ZHAO_SHEET = ROOT / "game/data/zcombat26/rpg-2-star-ocean-the-second_zhao-ling-combat_runtime-spritesheet_unapproved-zcombat26-v01_20261021-180157-340e10f5.png"
LIANG_SHEET = ROOT / "game/data/lcombat29/rpg-2-star-ocean-the-second_liang-xu-combat_runtime-spritesheet_unapproved-lcombat29-v01_20261021-201025-e7f7aac4.png"
LIANG_TOOL = "tools/rpg-2-star-ocean-the-second_liang-xu_combat-static-and-actions-author_unapproved-lcombat29-v01_20261021-201025-efc98984.py"
EXPLORE_TOOL = ROOT / "tools/rpg-2-star-ocean-the-second_ji-cheng_explore-source-author_unapproved-jexplore31-v01_20261021-210451-b2782add.py"
EXPLORE_EAST = "game/data/jexplore31/png/rpg-2-star-ocean-the-second_ji-cheng_explore-east-static_unapproved-jexplore31-v01_20261021-210451-1c39fa48.png"
SOUTH_PILOT_PNG = "game/assets/characters/ji-cheng-hd/rpg-2-star-ocean-the-second_ji-cheng_south-idle-static_unapproved-v01_20261018-132812-1920ff13.png"
CONCEPT = "outputs/rpg-2-star-ocean-the-second_ji-cheng_character-sheet_v01_20261013-190436-dcea1a37.png"
W, H = 136, 144
PIN = (64, 136)
COLS = 6
TICK = 30
ZIP_DT = (2026, 10, 21, 22, 6, 32)
LAYERS = ["coat-back", "arm-back", "leg-back", "leg-front", "torso", "head", "book", "arm-front", "magnifier", "fx"]

PAL_HEX = {   # literal copy of the jexplore31 Ji PAL (Ji Cheng south pilot named ramps, unchanged)
    "K": "#0c0a0e", "1": "#6c7482", "2": "#434852", "3": "#292c34", "4": "#111216", "5": "#e2e4e6", "6": "#b2b8c0",
    "7": "#7e848e", "F": "#f0d0bc", "f": "#d8aa94", "e": "#b47e6c", "n": "#c4aca2", "N": "#927e84", "y": "#2a2630",
    "R": "#b8706a", "G": "#5a7450", "g": "#3c5338", "H": "#223524", "J": "#0f1a11", "C": "#a9ada4", "c": "#787d76",
    "B": "#3c3c46", "b": "#1f1f26", "P": "#504e58", "p": "#32313a", "o": "#19181e", "O": "#54494a", "w": "#2e2629",
    "L": "#a2724a", "l": "#77513a", "m": "#4b3327", "M": "#e2c272", "X": "#a8844a", "Y": "#6c5432", "Z": "#d2e4e8",
    "z": "#7c98a2", "A": "#dcd0b2", "a": "#a89c84"}
PAL = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in PAL_HEX.items()}
R_HAIR, R_SILV, R_SKIN = ("1", "2", "3"), ("5", "6", "7"), ("F", "f", "e")
R_COAT, R_COATD, R_COATIN = ("G", "g", "H"), ("g", "H", "J"), ("H", "J", "J")
R_LINE, R_TOP, R_GLOVE = ("C", "c", "c"), ("B", "b", "o"), ("B", "b", "o")
R_TROU, R_TROUD, R_BOOT = ("P", "p", "o"), ("p", "o", "o"), ("O", "w", "o")
R_LEATH, R_BRASS, R_CREAM, R_LENS = ("L", "l", "m"), ("M", "X", "Y"), ("A", "a", "a"), ("Z", "z", "z")

NEUTRAL_PELVIS = (62.0, 92.0)
THIGH, SHIN = 21.0, 21.0
UPPER, FORE = 13.0, 12.0
HEM_DROP = 27.0   # long coat: ragged rear point to mid-calf, cut-away front higher

# Pose rows. pel: pelvis offset; lean: upper-body rotation (deg, + = toward the enemy); feet: ankle targets (sole row 135 when
# y=130); fh: near (right, magnifier) hand offset from the shoulder; mdeg: magnifier handle axis (0 = +x level, + = down);
# mag: open (lens ring out) | fold (ring folded into its brass case); bh: far (left, book) hand offset from the shoulder;
# kdeg: book axis; book: closed | open; hem: rear coat-tail follow-through (x); eyes: open|focus|read|shut|wince;
# fx: none|flare|sparks|glint|fault|recall; head: head offset.
D = dict(pel=(0, 0), lean=2.0, feet=((53, 130), (75, 130)), fh=(10, 3), mdeg=-62.0, mag="open", bh=(13, 16), kdeg=-8.0,
         book="closed", hem=0, eyes="open", fx="none", head=(0, 0))


def pose(**kw):
    p = dict(D)
    p.update(kw)
    return p


P = {
    "idle-a": pose(),
    "idle-b": pose(pel=(0, 1), lean=3.0, fh=(10, 4), mdeg=-58.0, bh=(13, 17), kdeg=-5.0, hem=-1),
    "move-a": pose(pel=(1, 1), lean=7.0, feet=((50, 130), (80, 130)), fh=(8, 5), mdeg=-50.0, bh=(12, 15), hem=-3),
    "move-b": pose(pel=(3, -2), lean=6.0, feet=((57, 126), (78, 130)), fh=(9, 4), mdeg=-54.0, bh=(12, 16), hem=-5),
    "move-c": pose(pel=(4, 1), lean=7.0, feet=((55, 130), (84, 128)), fh=(11, 5), mdeg=-50.0, bh=(11, 15), hem=-3),
    "move-d": pose(pel=(3, -1), lean=6.0, feet=((53, 130), (81, 130)), fh=(9, 4), mdeg=-54.0, bh=(12, 16), hem=-4),
    "guard-in": pose(pel=(-1, 2), lean=-1.0, fh=(5, 10), mdeg=-100.0, bh=(15, -2), kdeg=-90.0, hem=1, eyes="focus"),
    "guard-hold": pose(pel=(-2, 4), lean=-3.0, feet=((50, 130), (76, 130)), fh=(4, 11), mdeg=-105.0, bh=(16, -6), kdeg=-92.0,
                       hem=2, eyes="focus"),
    "attack-strike": pose(pel=(3, 2), lean=8.0, feet=((51, 130), (83, 130)), fh=(24, -1), mdeg=0.0, bh=(7, 18), kdeg=10.0, hem=-4,
                          eyes="focus", fx="flare"),
    "attack-follow": pose(pel=(3, 3), lean=9.0, feet=((51, 130), (83, 130)), fh=(22, 5), mdeg=12.0, bh=(8, 18), kdeg=8.0, hem=-2,
                          eyes="focus", fx="sparks"),
    "attack-fold": pose(pel=(1, 2), lean=5.0, feet=((52, 130), (80, 130)), fh=(15, 6), mdeg=-30.0, mag="fold", bh=(10, 17), hem=1,
                        eyes="focus"),
    "attack-recover": pose(pel=(0, 1), lean=3.0, feet=((53, 130), (77, 130)), fh=(11, 4), mdeg=-50.0, bh=(12, 16), hem=1),
    "dodge-hop": pose(pel=(-9, -6), lean=9.0, feet=((41, 122), (62, 124)), fh=(7, 8), mdeg=-70.0, bh=(10, 14), kdeg=-20.0, hem=7,
                      head=(0, 1)),
    "dodge-land": pose(pel=(-12, 9), lean=13.0, feet=((39, 130), (62, 130)), fh=(11, 9), mdeg=-45.0, bh=(13, 13), hem=5),
    "skill-open": pose(pel=(-1, 2), lean=4.0, feet=((52, 130), (76, 130)), fh=(9, 8), mdeg=-70.0, bh=(15, 7), kdeg=0.0, book="open",
                       eyes="read", head=(0, 1)),
    "skill-read": pose(pel=(0, 2), lean=6.0, feet=((52, 130), (77, 130)), fh=(15, 4), mdeg=40.0, bh=(15, 8), kdeg=0.0, book="open",
                       hem=-1, eyes="read", fx="glint", head=(0, 1)),
    "skill-fault": pose(pel=(0, 2), lean=3.0, feet=((52, 130), (78, 130)), fh=(17, -2), mdeg=-10.0, bh=(16, 6), kdeg=-6.0,
                        book="open", hem=1, eyes="focus", fx="fault"),
    "skill-recall": pose(pel=(1, 1), lean=4.0, feet=((52, 130), (78, 130)), fh=(23, -6), mdeg=-14.0, bh=(12, 15), kdeg=-6.0,
                         hem=0, eyes="focus", fx="recall"),
    "hit-recoil": pose(pel=(-6, 3), lean=-14.0, feet=((50, 130), (73, 130)), fh=(-3, 12), mdeg=-120.0, bh=(5, 15), kdeg=-40.0,
                       hem=7, eyes="wince", head=(-2, 0)),
    "hit-stagger": pose(pel=(-5, 6), lean=9.0, feet=((48, 130), (72, 130)), fh=(7, 14), mdeg=-80.0, bh=(10, 16), kdeg=20.0, hem=4,
                        eyes="wince"),
    "defeat-buckle": pose(pel=(-4, 10), lean=18.0, feet=((49, 130), (73, 130)), fh=(8, 18), mdeg=60.0, mag="fold", bh=(9, 19),
                          kdeg=50.0, hem=3, eyes="wince"),
    "defeat-knee": pose(pel=(-3, 22), lean=26.0, feet=((41, 130), (73, 130)), fh=(13, 20), mdeg=80.0, mag="fold", bh=(14, 20),
                        kdeg=80.0, hem=2, eyes="shut"),
    "defeat-down": pose(pel=(-2, 30), lean=40.0, feet=((37, 130), (65, 130)), fh=(17, 17), mdeg=170.0, mag="fold", bh=(18, 16),
                        kdeg=160.0, hem=2, eyes="shut", head=(0, 2)),
}
KNEELING = {"defeat-knee": "back", "defeat-down": "both"}
AIRBORNE = {"dodge-hop"}
CELLS = list(P)
# Runtime timing (30 tick/s). Totals equal the heroine hsc19 set; the lens-flare contact is attack frame 0 (tick 0).
ACTIONS = {
    "idle": {"loop": True, "loop_start": 0, "frames": [("idle-a", 14), ("idle-b", 14)]},
    "attack": {"loop": False, "frames": [("attack-strike", 2), ("attack-follow", 3), ("attack-fold", 3), ("attack-recover", 4), ("idle-a", 1)]},
    "move": {"loop": True, "loop_start": 0, "frames": [("move-a", 3), ("move-b", 3), ("move-c", 3), ("move-d", 3)]},
    "guard": {"loop": True, "loop_start": 1, "frames": [("guard-in", 2), ("guard-hold", 12)]},
    "dodge": {"loop": False, "frames": [("dodge-hop", 4), ("dodge-land", 4), ("idle-a", 1)]},
    "skill": {"loop": False, "frames": [("skill-open", 4), ("skill-read", 3), ("skill-fault", 3), ("skill-recall", 3), ("idle-a", 1)]},
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


# ---------------------------------------------------------------- raster primitives (same as lcombat29 / zcombat26 / mcombat22)
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
    hips = {"back": U(-3, 0), "front": U(2, 0)}
    J = {w: leg_joints(pid, hips[w], p["feet"][0 if w == "back" else 1], w) for w in ("back", "front")}
    hem_y = pel[1] + HEM_DROP
    h = p["hem"]
    bk, fk = J["back"][1], J["front"][1]

    # inside of the open long coat behind the legs + the long ragged rear point (swings with hem)
    tail = m_poly([U(-9, -2), U(-2, -2), (bk[0] - 1 + h * 0.4, hem_y - 2), (bk[0] - 6 + h * 0.8, hem_y + 3),
                   (bk[0] - 9 + h, hem_y - 1), (bk[0] - 12 + h, hem_y + 1), (U(-11, 6)[0] - 2 + h * 0.6, (U(-11, 6)[1] + hem_y) / 2)])
    part(L["coat-back"], tail, R_COATIN)
    put(L["coat-back"], m_cap((bk[0] - 11 + h, hem_y), (bk[0] - 6 + h * 0.8, hem_y + 2), 0.5), "X")     # worn brass hem trim glint

    # legs: slim charcoal trousers, black buckled boots to mid-calf with two brass buckles; thigh strap + pouch on the near thigh
    def leg(layer, which, dark):
        kneel, knee, ankle, stretch = J[which]
        hip = hips[which]
        tr = R_TROUD if dark else R_TROU
        part(layer, m_cap(hip, knee, 3.9) | m_cap(knee, add(knee, ((ankle[0] - knee[0]) * 0.45, (ankle[1] - knee[1]) * 0.45)), 3.4), tr)
        top = add(knee, ((ankle[0] - knee[0]) * 0.4, (ankle[1] - knee[1]) * 0.4))
        if kneel:
            foot = m_poly([(ankle[0] - 3, ankle[1] - 3), (ankle[0] + 1, ankle[1] - 3), (ankle[0] + 1, 135), (ankle[0] - 8, 135), (ankle[0] - 8, 132)])
            lift = 0
        else:
            lift = 0 if ankle[1] >= 130 else ankle[1] - 130
            foot = m_poly([(ankle[0] - 3, ankle[1] - 4), (ankle[0] + 3, ankle[1] - 3), (ankle[0] + 8, 132 + lift), (ankle[0] + 8, 135 + lift),
                           (ankle[0] - 3, 135 + lift)])
        part(layer, m_cap(top, ankle, 3.3) | foot, R_BOOT)
        if not kneel:
            put(layer, m_cap((ankle[0] - 3, 134 + lift), (ankle[0] + 7, 134 + lift), 0.5), "o")              # chunky sole
        for f in (0.3, 0.7):                                                                               # two boot straps + buckles
            sp = add(top, ((ankle[0] - top[0]) * f, (ankle[1] - top[1]) * f))
            put(layer, m_cap(add(sp, (-2, 0)), add(sp, (2, 0)), 0.5), "l")
            put(layer, m_cap(add(sp, (1, 0)), add(sp, (1, 0)), 0.5), "M" if not dark else "X")
        if not dark:                                                                                       # thigh strap + pouch
            ts = add(hip, ((knee[0] - hip[0]) * 0.45, (knee[1] - hip[1]) * 0.45))
            put(layer, m_cap(add(ts, (-3, 0)), add(ts, (3, 0)), 0.5), "l")
            part(layer, m_poly([add(ts, (1, 1)), add(ts, (5, 1)), add(ts, (5, 6)), add(ts, (1, 6))]), R_LEATH, band=1)
            put(layer, m_cap(add(ts, (3, 2)), add(ts, (3, 2)), 0.5), "X")
        info["joints"][which] = {"hip": [round(hip[0], 2), round(hip[1], 2)], "knee": [round(knee[0], 2), round(knee[1], 2)],
                                 "ankle": [round(ankle[0], 2), round(ankle[1], 2)], "stretch": round(stretch, 3)}

    leg(L["leg-back"], "back", True)
    leg(L["leg-front"], "front", False)

    # torso: ink-green open long coat (narrow waist), black high-collared top in the opening, brown harness straps crossing at a
    # brass ring, belt with brass buckle, two silver vials + pouch at the hip, cut-away front hem; long cream panel with a ragged
    # point at the knee hanging outside the near coat panel
    t = L["torso"]
    skirt = m_poly([U(-9, -1), U(8, -1), (max(fk[0] + 2, U(8, 0)[0] + 1), hem_y - 9), (fk[0] - 3, hem_y - 6),
                    (min(bk[0] - 2, fk[0] - 7), hem_y - 1), (U(-10, 4)[0], (U(-10, 4)[1] + hem_y) / 2)])
    body = m_poly([U(-9, -30), U(6, -31), U(9, -20), U(7, -10), U(8, 1), U(-9, 1), U(-10, -18)])
    part(t, skirt | body, R_COAT)
    put(t, m_poly([U(5, -29), U(8, -20), U(6, -10), U(7, 0), U(5, 0), U(4, -10), U(5, -20)]) & (skirt | body), "b")   # black top
    put(t, m_cap(U(4, -29), U(4, 0), 0.5), "X")                                                # brass lapel edge
    put(t, m_cap(U(-6, -27), U(-4, -6), 0.5), "G")                                             # shoulder-to-hip lit seam
    put(t, m_cap(U(-8, 5), (U(-8, 5)[0] + 1, hem_y - 6), 0.5), "H")                            # skirt fold
    put(t, m_cap(U(-7, -28), U(4, -6), 0.6), "l")                                              # harness strap (shoulder -> front waist)
    put(t, m_cap(U(-8, -10), U(2, -24), 0.6), "m")                                             # crossing strap
    put(t, m_cap(U(-2, -16), U(-2, -16), 0.9), "M")                                            # brass ring at the crossing
    part(t, m_poly([U(-9, -3), U(8, -3), U(8, 0), U(-9, 0)]), R_LEATH, band=1)                 # belt
    put(t, m_cap(U(3, -2), U(4, -2), 0.6), "M")                                                # brass buckle
    for vx in (-1, 2):                                                                          # silver vials with brass caps
        part(t, m_poly([U(vx, 1), U(vx + 1, 1), U(vx + 1, 7), U(vx, 7)]), R_SILV, band=1)
        put(t, m_cap(U(vx, 1), U(vx + 1, 1), 0.5), "M")
    part(t, m_poly([U(-8, 1), U(-4, 1), U(-4, 6), U(-8, 6)]), R_LEATH, band=1)                 # hip pouch
    panel = m_poly([U(0, 1), U(4, 1), (fk[0] - 1, hem_y - 9), (fk[0] - 2, hem_y - 3), (fk[0] - 4, hem_y - 6), (fk[0] - 5, hem_y - 1),
                    (U(0, 8)[0] - 1, (U(0, 8)[1] + hem_y - 6) / 2)])
    part(t, panel, R_CREAM, band=1)
    put(t, panel & ((xx + yy) % 5 == 0), "a")                                                  # woven pattern ticks
    part(t, m_poly([U(-5, -35), U(6, -35), U(7, -29), U(4, -27), U(-4, -28), U(-7, -31)]), R_TOP, band=1)   # black high collar
    put(t, m_cap(U(5, -32), U(5, -32), 0.6), "M")                                              # brass collar buckle

    # head: big Sea of Stars head, face toward the enemy. Straight blue-black bob: crown + forehead sweep toward the face, the
    # near (right) curtain straight to the shoulder over the ear ending in three jagged silver points. The shaved LEFT temple is
    # on the far side: it shows only as the pale undercut wrap with razor lines at the back of the head, with the rectangular
    # brass drop earring hanging below it behind the neck.
    hd = L["head"]
    part(hd, m_cap(U(0, -34), U(2, -34), 2.3), R_SKIN, band=1)                                 # neck
    head = m_ell(hc, 10, 11)
    part(hd, head, R_SKIN)
    under = head & (xx <= cx - 7) & (yy >= cy - 2) & (yy <= cy + 6)
    put(hd, under, "n")
    put(hd, under & (yy % 2 == 0) & (xx <= cx - 8), "N")                                       # razor lines
    ering = m_poly([(cx - 10, cy + 7), (cx - 8, cy + 7), (cx - 8, cy + 11), (cx - 10, cy + 11)])
    put(hd, dil4(ering) & ~ering & ~head, "K")
    put(hd, ering, "X")
    put(hd, ering & (yy <= cy + 8), "M")                                                       # brass drop earring
    crown = (head & (yy < cy - 3)) | m_ell((cx - 1, cy - 5), 10, 7)
    sweep = m_poly([(cx - 3, cy - 11), (cx + 6, cy - 10), (cx + 11, cy - 5), (cx + 10, cy - 3), (cx + 6, cy - 4), (cx + 2, cy - 3)])
    curtain = m_poly([(cx - 7, cy - 4), (cx + 1, cy - 5), (cx + 2, cy + 3), (cx + 1, cy + 13), (cx - 7, cy + 13)])
    hair = (crown | sweep | curtain) & ~under
    part(hd, hair, R_HAIR)
    put(hd, m_cap((cx - 6, cy - 9), (cx + 5, cy - 10), 0.5), "1")                              # crown sheen
    put(hd, m_cap((cx + 2, cy - 7), (cx + 9, cy - 4), 0.5), "2")                               # sweep strand
    put(hd, m_cap((cx - 3, cy - 3), (cx - 3, cy + 12), 0.5), "4")                               # curtain strand break
    tips = (m_poly([(cx - 7, cy + 12), (cx - 4, cy + 12), (cx - 6, cy + 17)]) | m_poly([(cx - 4, cy + 12), (cx - 1, cy + 12), (cx - 2, cy + 18)])
            | m_poly([(cx - 1, cy + 12), (cx + 2, cy + 12), (cx + 1, cy + 16)]))
    put(hd, dil4(tips) & ~tips & ~(hair | head), "K")
    put(hd, tips, "6")
    put(hd, tips & ~shift(tips, 1, 1), "5")
    put(hd, tips & ~shift(tips, -1, -1), "7")                                                  # jagged silver tips
    ex, ey = round(cx + 6), round(cy + 1)
    if p["eyes"] in ("open", "focus"):
        hd[ey:ey + 2, ex:ex + 2, :3] = PAL["y"]
        hd[ey - 1, ex - 1:ex + 3, :3] = PAL["3"]                                              # calm lowered lid
        if p["eyes"] == "focus":
            hd[ey, ex - 1, :3] = PAL["3"]
    elif p["eyes"] == "read":
        hd[ey + 1, ex:ex + 2, :3] = PAL["y"]                                                  # eyes lowered to the page
        hd[ey, ex - 1:ex + 3, :3] = PAL["3"]
    elif p["eyes"] == "shut":
        hd[ey + 1, ex - 1:ex + 3, :3] = PAL["3"]
    else:
        hd[ey, ex:ex + 3, :3] = PAL["3"]
        hd[ey + 1, ex - 1, :3] = PAL["3"]
        hd[ey + 1, ex + 3, :3] = PAL["3"]
    hd[ey + 3, round(cx + 9), :3] = PAL["f"]                                                  # nose shadow
    hd[round(cy + 6), round(cx + 6):round(cx + 8), :3] = PAL["R"]                             # muted lips

    # arms: ink-green sleeve -> wide grey rolled lining cuff at the elbow -> black forearm -> black glove
    def arm(layer, sh, off, front):
        hand = add(sh, off)
        el, stretch = ik(sh, hand, UPPER, FORE, -1)
        part(layer, m_cap(sh, el, 3.5), R_COAT if front else R_COATD)
        part(layer, m_cap(el, add(el, ((hand[0] - el[0]) * 0.7, (hand[1] - el[1]) * 0.7)), 2.8), R_TOP, band=1)
        part(layer, m_cap(add(el, ((sh[0] - el[0]) * 0.18, (sh[1] - el[1]) * 0.18)), add(el, ((hand[0] - el[0]) * 0.2, (hand[1] - el[1]) * 0.2)), 3.4),
             R_LINE, band=1)
        part(layer, m_ell(hand, 2.6, 2.6), R_GLOVE, band=1)
        info["joints"]["arm-front" if front else "arm-back"] = {"shoulder": [round(sh[0], 2), round(sh[1], 2)],
                                                               "elbow": [round(el[0], 2), round(el[1], 2)],
                                                               "hand": [round(hand[0], 2), round(hand[1], 2)], "stretch": round(stretch, 3)}
        return hand

    bhand = arm(L["arm-back"], U(-2, -27), p["bh"], False)
    hand = arm(L["arm-front"], U(3, -26), p["fh"], True)

    # small leather-bound book in the far (left) hand: closed = cover with cream page edge + brass clasp; open = two cream pages
    # with text lines inside the leather cover
    Bk = local(bhand, p["kdeg"])
    bo = L["book"]
    if p["book"] == "open":
        cover = m_poly([Bk(-9, -5), Bk(9, -5), Bk(9, 4), Bk(-9, 4)])
        part(bo, cover, R_LEATH, band=1)
        pages = m_poly([Bk(-8, -5), Bk(-1, -4), Bk(-1, 2), Bk(-8, 2)]) | m_poly([Bk(1, -4), Bk(8, -5), Bk(8, 2), Bk(1, 2)])
        put(bo, pages, "A")
        for ly in (-3, -1, 1):
            put(bo, m_cap(Bk(-7, ly), Bk(-2, ly), 0.5) | m_cap(Bk(2, ly), Bk(7, ly), 0.5), "a")    # text lines
        put(bo, m_cap(Bk(0, -4), Bk(0, 3), 0.5), "m")                                           # spine gutter
        page_c = Bk(4, -1)
    else:
        cover = m_poly([Bk(-4, -5), Bk(4, -5), Bk(4, 5), Bk(-4, 5)])
        part(bo, cover, R_LEATH, band=1)
        put(bo, m_cap(Bk(4, -4), Bk(4, 4), 0.5), "A")                                           # cream page edge
        put(bo, m_cap(Bk(-3, -4), Bk(-3, 4), 0.5), "m")                                         # spine
        put(bo, m_cap(Bk(3, 0), Bk(4, 0), 0.6), "M")                                            # brass clasp
        page_c = Bk(0, 0)
    put(bo, m_ell(bhand, 2.0, 2.0), "b")                                                       # gloved fingers over the cover
    info["book"] = {"grip": [round(bhand[0], 2), round(bhand[1], 2)], "deg": p["kdeg"], "open": p["book"] == "open",
                    "page": [round(page_c[0], 2), round(page_c[1], 2)]}

    # brass folding magnifier in the near (right) hand: brass handle + ring with pale lens, or folded into its brass case
    M = local(hand, p["mdeg"])
    mg = L["magnifier"]
    if p["mag"] == "open":
        part(mg, m_cap(M(1, 0), M(5, 0), 1.0), R_BRASS, band=1)
        ring = m_ell(M(9.5, 0), 4.2, 4.2)
        part(mg, ring, R_BRASS, band=1)
        lens = m_ell(M(9.5, 0), 2.6, 2.6)
        put(mg, lens, "z")
        put(mg, lens & ~shift(lens, 1, 1), "Z")                                                 # glass highlight
        lc = M(9.5, 0)
    else:
        case = m_poly([M(0, -2.5), M(8, -2.5), M(8, 2.5), M(0, 2.5)])
        part(mg, case, R_BRASS, band=1)
        put(mg, m_cap(M(2, 0), M(7, 0), 0.6), "z")
        put(mg, m_cap(M(2, -1), M(4, -1), 0.5), "Z")                                            # lens edge showing in the case
        lc = M(5, 0)
    put(mg, m_ell(hand, 2.0, 2.0), "b")                                                        # gloved grip over the handle
    info["magnifier"] = {"grip": [round(hand[0], 2), round(hand[1], 2)], "lens": [round(lc[0], 2), round(lc[1], 2)],
                         "deg": p["mdeg"], "open": p["mag"] == "open"}

    # fx (own layer, no outline): lens flare lance, sparks, reading glint, fault-line trace, recall brackets
    fx = L["fx"]
    if p["fx"] == "flare":
        lx, ly = lc
        beam = m_cap((lx + 5, ly), (W - 3, ly), 1.0)
        put(fx, beam, "z")
        put(fx, m_cap((lx + 5, ly), (W - 3, ly), 0.5), "Z")
        put(fx, m_cap((lx + 5, ly), (lx + 24, ly), 0.5), "5")                                   # hot core near the lens
        for a in (0, 45, 90, 135, 180, 225, 270, 315):
            r1 = 9 if a % 90 == 0 else 6
            put(fx, m_cap(add(lc, rot((5.5, 0), a)), add(lc, rot((r1 + 1.0, 0), a)), 0.5), "M" if a % 90 else "5")   # starburst
    elif p["fx"] == "sparks":
        lx, ly = lc
        put(fx, (np.abs(yy - ly) <= 0.5) & (xx > lx + 8) & (xx < W - 6) & (xx % 4 == 0), "Z")   # fading lance
        for c in ((lx + 16, ly - 5), (lx + 26, ly + 4), (lx + 34, ly - 3)):
            put(fx, m_cap(c, add(c, (1, 1)), 0.5), "M")
    elif p["fx"] == "glint":
        g = lc
        put(fx, m_cap(add(g, (-4, 0)), add(g, (4, 0)), 0.5) | m_cap(add(g, (0, -4)), add(g, (0, 4)), 0.5), "5")
        put(fx, m_cap(add(info["book"]["page"], (-3, -1)), add(info["book"]["page"], (3, -1)), 0.5), "Z")   # read line lit
    elif p["fx"] == "fault":
        sx, sy = add(bhand, (10, -12))
        pts = [(sx, sy), (sx + 8, sy - 4), (sx + 14, sy + 3), (sx + 22, sy - 3), (sx + 30, sy + 4), (sx + 38, sy - 2), (sx + 46, sy + 2)]
        line = np.zeros((H, W), bool)
        for a, b in zip(pts, pts[1:]):
            line |= m_cap(a, b, 0.5)
        put(fx, line, "A")
        for a, b in zip(pts, pts[1:]):                                                          # stratified strata lines below
            put(fx, m_cap((a[0], a[1] + 5), (b[0], b[1] + 5), 0.5) & (xx % 2 == 0), "a")
        for c in pts[1::2]:
            put(fx, m_cap(c, c, 0.8), "M")                                                      # recall nodes on the fault line
    elif p["fx"] == "recall":
        tx, ty = round(min(lc[0] + 24, W - 14)), round(lc[1])
        for s in (-1, 1):                                                                      # brackets [ ] on the enemy line
            bx = tx + s * 8
            put(fx, m_cap((bx, ty - 7), (bx, ty + 7), 0.5) | m_cap((bx, ty - 7), (bx - s * 3, ty - 7), 0.5)
                | m_cap((bx, ty + 7), (bx - s * 3, ty + 7), 0.5), "M")
        rr = np.hypot(xx - tx, yy - ty)
        aa = np.degrees(np.arctan2(yy - ty, xx - tx))
        put(fx, (np.abs(rr - 4.5) <= 0.6) & ~((aa > -100) & (aa < -40)), "Z")                  # paused clock ring
        put(fx, m_cap((tx, ty), (tx, ty - 3), 0.5), "5")
        put(fx, (np.abs(yy - ty) <= 0.5) & (xx > lc[0] + 6) & (xx < tx - 10) & (xx % 3 == 0), "z")   # sight line from the lens
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
        "schema": "worlds-between.combat-sprite-set/1", "set_id": "ji-cheng-combat-jcombat32-v01",
        "character": {"member_id": MEMBER},
        "art_status": "unapproved-ji-cheng-combat-source-poses-technical-only", "art_approved": False, "motion_approved": False,
        "default_adoption": False,
        "note": "Deterministic authored source set for Ji Cheng (brass folding magnifier + small book signature, Fault-Line Recall "
                "skill); not creator-approved art or motion, not a default, not wired. Loadable only through the explicit member-only "
                "jcombat32 index.",
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
        "status": "UNAPPROVED Ji Cheng combat static + eight-action source set; technical source only; runtime default unchanged.",
        "member_id": MEMBER, "architectureFrom": LIANG_TOOL, "paletteFrom": rel(EXPLORE_TOOL),
        "identityReference": {"conceptSheet": CONCEPT, "conceptIsUnapproved": True, "exploreEastStatic": EXPLORE_EAST,
                              "southPilotPng": SOUTH_PILOT_PNG, "old32x48PrototypeRead": False},
        "identity": "records restorer, female, age 28; straight blue-black shoulder bob with jagged silver tips, shaved LEFT temple "
                    "with razor lines + rectangular brass drop earring, ink-green long open coat with uneven hem, cream uneven panels, "
                    "grey rolled sleeve lining, black high collar, leather harness/belt with silver vials + pouch, thigh strap, "
                    "black buckled boots; brass folding magnifier (near/right hand) and small leather book (far/left hand)",
        "facingLimitation": "authored facing right shows her RIGHT side; the shaved left temple is on the far side and reads only as "
                            "the undercut wrap with razor lines at the back of the head and the drop-earring glint below it",
        "contractFrom": rel(HERO_MANIFEST), "layers": LAYERS, "cell": [W, H], "pivot": list(PIN), "tickRate": TICK,
        "signature": "brass folding magnifier focuses a lens-flare lance toward the enemy (attack_range 100); closed book raised "
                     "cover-out as the guard; no gun, no blade, no board",
        "skill": "Fault-Line Recall (断层回读): book opens -> magnifier read over the page -> fault-line trace ahead -> recall "
                 "brackets + paused ring on the enemy line as the book closes",
        "mechanicsRead": {"file": "game/scripts/app_state.gd MEMBER_DEFS ji-cheng + game/scripts/battle_arena.gd _try_attack/_use_skill",
                          "attack_damage": 12, "attack_range": 100.0, "attack_cooldown_s": 0.43, "skill_energy_cost": 14,
                          "skill_cooldown_s": 2.2, "skill_effect": "enemy_windup += 0.65*rank if winding up; enemy_cooldown += 0.65*rank",
                          "damage": "immediate on attack press"},
        "combatStatic": {"pose": "idle-a", "png": files["still.png"][1], "ora": files["still.ora"][1], "pxo": files["still.pxo"][1]},
        "runtimeActions": {a: {"frames": [[pid, t] for pid, t in s["frames"]], "loop": s["loop"], "totalTicks": sum(t for _, t in s["frames"])}
                           for a, s in ACTIONS.items()},
        "strikeCueTick": STRIKE_CUE_TICK,
        "strikeCueNote": "lens-flare contact is attack frame 0 (tick 0), matching the existing immediate companion attack; "
                         "no timer or damage change",
        "poses": {pid: {"params": {k: (list(map(list, v)) if k == "feet" else (list(v) if isinstance(v, tuple) else v)) for k, v in P[pid].items()},
                        "rig": built[pid][1], "runtimeCell": CELLS.index(pid)} for pid in P},
        "source": {"file": rel(Path(__file__).resolve()), "sha256TextLf": sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n")),
                   "textHashNormalization": "sha256-text-lf-v1 (CRLF->LF)"},
        "files": {role: {"path": rel(d / n), "sha256": sha(b)} for role, (d, n, b) in sorted(files.items())},
        "artApproved": False, "motionApproved": False, "runtimeDefaultChanged": False, "guiSaveAsVerified": False,
    }
    a_b = (json.dumps(author, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    files["author"] = (OUT, name("author-manifest", "json"), a_b)
    files["pkg.author"] = (PKG, name("author-manifest", "json"), a_b)
    return files, flats, built, manifest, index


def jexplore31_palette():
    spec = importlib.util.spec_from_file_location("wb_jexplore31_author", str(EXPLORE_TOOL))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return {k: tuple(v) for k, v in m.RGB.items()}


def gates(files, flats, built, manifest, index):
    res = []

    def gate(k, ok, info=None):
        res.append({"key": k, "pass": bool(ok), "info": info})
    jx_pal = jexplore31_palette()
    gate("palette == jexplore31 author PAL (same keys, same RGB)", jx_pal == PAL, sorted(set(jx_pal) ^ set(PAL)))
    pal = set(PAL.values())
    for pid, flat in flats.items():
        op = flat[..., 3] > 0
        ys, xs = np.nonzero(op)
        cols = {tuple(c) for c in flat[op][:, :3].tolist()}
        L, info = built[pid]
        gate(f"{pid}: binary alpha + declared Ji palette only", set(np.unique(flat[..., 3]).tolist()) <= {0, 255} and cols <= pal, len(cols))
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
                 (("blue-black hair", "1234"), ("silver tips/vials", "567"), ("ink-green coat", "GgHJ"), ("grey lining", "Cc"),
                  ("cream panel/pages", "Aa"), ("brass", "MXY"), ("leather harness/book", "Llm"), ("lens glass", "Zz"),
                  ("shaved scalp", "nN"), ("skin", "Ff"))}
        gate(f"{pid}: Ji identity cues present (hair/silver/coat/lining/cream/brass/leather/lens/shaved scalp/skin texels)",
             all(v >= 4 for v in ident.values()), ident)
        gate(f"{pid}: no board/gun/scarf copied (Liang board/copper/navy, Zhao gun/jacket, male scarf/coat RGB absent)",
             not ({(0x42, 0x45, 0x4f), (0xe0, 0x8c, 0x4c), (0x58, 0x74, 0xba), (0xa0, 0xea, 0xff), (0xd7, 0xdc, 0xe2), (0x8f, 0x98, 0xa8),
                   (0x66, 0x6a, 0x7d), (0x82, 0xc8, 0xb8), (0x8c, 0x76, 0x64), (0xb2, 0x7c, 0x4e)} & cols))
    gate("all pose images unique", len({sha(files[f'{p}.png'][2]) for p in P}) == len(P))
    for a, s in ACTIONS.items():
        ids = [pid for pid, _ in s["frames"]]
        diffs = [int((np.any(flats[x] != flats[y], -1)).sum()) for x, y in zip(ids, ids[1:])]
        gate(f"{a}: consecutive frames visibly different (>= 60 texels)", all(d >= 60 for d in diffs), diffs)
    hero = json.loads(HERO_MANIFEST.read_text(encoding="utf-8"))
    gate("manifest top-level keys == heroine hsc19 manifest", list(manifest) == list(hero), [k for k in hero if k not in manifest])
    gate("character is member-only ji-cheng (no appearance key)", manifest["character"] == {"member_id": MEMBER})
    gate("index has exactly the ji-cheng key, no hero key, names the manifest",
         list(index["sets"]) == [MEMBER] and not any(k.startswith("hero") for k in index["sets"]) and index["sets"][MEMBER] == files["pkg.manifest"][1])
    req = {"idle": True, "move": True, "guard": True, "attack": False, "dodge": False, "hit": False, "defeat": False}
    gate("eight canonical actions: required with loop flags + skill; no victory",
         all(manifest["actions"][a]["loop"] == l for a, l in req.items()) and set(manifest["actions"]) == set(req) | {"skill"}
         and not any(k.startswith("victory") for k in P))
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
    gate("strike cue (lens flare) on attack frame 0 = tick 0; no other attack frame has a flare",
         first == "attack-strike" and P[first]["fx"] == "flare" and STRIKE_CUE_TICK == 0 and manifest["actions"]["attack"]["frames"][0]["cell"] == CELLS.index(first)
         and all(P[pid]["fx"] != "flare" for pid, _ in ACTIONS["attack"]["frames"][1:]))
    sb = built["attack-strike"]
    fxm = sb[0]["fx"][..., 3] > 0
    gate("strike: open magnifier extended ahead (lens >= pelvis + 30 px) and the flare lance reaches x >= 128",
         sb[1]["magnifier"]["open"] and sb[1]["magnifier"]["lens"][0] >= sb[1]["pelvis"][0] + 30 and int(np.nonzero(fxm.any(0))[0].max()) >= 128,
         [sb[1]["magnifier"]["lens"], sb[1]["pelvis"], int(np.nonzero(fxm.any(0))[0].max())])
    gate("attack recovers: magnifier folds after the follow-through and reopens by recover",
         P["attack-fold"]["mag"] == "fold" and P["attack-recover"]["mag"] == "open" and P["attack-follow"]["fx"] == "sparks")
    gate("guard raises the closed book cover-out upright in front of the face (far hand above the shoulder)",
         all(P[x]["book"] == "closed" and P[x]["kdeg"] <= -80 and P[x]["bh"][1] <= 0 for x in ("guard-in", "guard-hold")))
    sr = built["skill-read"][1]
    gate("skill = Fault-Line Recall (book open, magnifier lens over the page, fault trace, recall brackets as the book closes)",
         P["skill-open"]["book"] == "open" and [P[x]["fx"] for x, _ in ACTIONS["skill"]["frames"][1:4]] == ["glint", "fault", "recall"]
         and P["skill-recall"]["book"] == "closed" and math.dist(sr["magnifier"]["lens"], sr["book"]["page"]) <= 12,
         round(math.dist(sr["magnifier"]["lens"], sr["book"]["page"]), 2))
    gate("defeat ends kneeling with eyes shut, magnifier folded and the book down", P["defeat-down"]["eyes"] == "shut"
         and KNEELING["defeat-down"] == "both" and P["defeat-down"]["mag"] == "fold" and abs(P["defeat-down"]["kdeg"]) > 150)
    sheet = decode(files["sheet"][2])
    gate("sheet is a cell multiple, 6 columns, each cell == its pose PNG; package copy == outputs copy",
         sheet.shape[1] == COLS * W and sheet.shape[0] % H == 0 and files["sheet"][2] == files["pkg.sheet"][2] and
         all(np.array_equal(sheet[(i // COLS) * H:(i // COLS + 1) * H, (i % COLS) * W:(i % COLS + 1) * W], flats[pid]) for i, pid in enumerate(CELLS)))
    mo = flats["idle-a"][..., 3] > 0
    for lab, path in (("heroine", HERO_SHEET), ("male mcombat22", MALE_SHEET), ("Zhao zcombat26", ZHAO_SHEET), ("Liang lcombat29", LIANG_SHEET)):
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
    split_ids = {"still", "attack-strike", "skill-fault", "guard-hold", "defeat-down"}
    for role in sorted(r for r in files if r.endswith(".pxo")):
        pid = role[:-4]
        pxo = str(long(OUT / files[role][1]))
        want = decode(files[f"{pid}.png"][2])
        layers = built["idle-a" if pid == "still" else pid][0]
        rec = {"pxo": files[role][1]}
        for split in ([False, True] if pid in split_ids else [False]):
            tmp = tempfile.mkdtemp(prefix="wb-jc32-")
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
        for r in res:
            if not r["pass"]:
                print("FAIL", r["key"], r["info"])
        print("BUILD REFUSED: source gates failed; nothing written")
        return 1
    elif a.mode == "build":
        for role, (d, n, b) in files.items():
            os.makedirs(long(d), exist_ok=True)
            p = long(d / n)
            if p.exists():
                assert p.read_bytes() == b, f"refusing to overwrite a different file: {n}"
            else:
                p.write_bytes(b)
        lst = {"schema": "jcombat32-file-list/1", "files": [{"role": r, "path": rel(d / n), "sha256": sha(b)} for r, (d, n, b) in sorted(files.items())]}
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
        res.append({"key": "Pixelorama native open/export equality (flat all PXOs; split layers still/attack-strike/skill-fault/guard-hold/defeat-down)",
                    "pass": not nf, "info": nf})
    fails = [r for r in res if not r["pass"]]
    for r in fails:
        print("FAIL", r["key"], r["info"])
    diags = sorted({d for r in (nat or []) for v in r.values() if isinstance(v, dict) for d in v["diagnostics"]})
    if diags:
        print("PIXELORAMA DIAGNOSTICS (disclosed):", len(diags), "unique lines")
        for d in diags[:10]:
            print("  ", d[:200])
    print("JCOMBAT32", a.mode.upper(), "PASS" if not fails else "FAIL", f"{len(res) - len(fails)}/{len(res)}")
    if a.mode == "check":
        rep = name("source-check-report-pixelorama" if a.pixelorama else "source-check-report", "json")
        os.makedirs(long(OUT), exist_ok=True)
        with open(long(OUT / rep), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"mode": "check", "pixelorama": a.pixelorama, "gates": res, "native": nat, "diagnostics": diags,
                                "passed": len(res) - len(fails), "total": len(res)}, indent=1, ensure_ascii=False) + "\n")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
