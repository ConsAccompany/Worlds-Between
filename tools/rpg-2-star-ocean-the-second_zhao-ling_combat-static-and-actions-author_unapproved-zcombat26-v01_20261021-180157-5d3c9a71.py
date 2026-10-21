"""Zhao Ling (赵铃, member_id zhao-ling) side-view combat static + eight source actions (zcombat26). UNAPPROVED, NOT A DEFAULT.

Reuses the proven mcombat22 method (tools/...protagonist-male_combat-static-and-actions-author...b7e2c4d1.py): every pose
is a parameter row, a small rig (two-bone IK legs/arms, upper body rotated about the pelvis, axis-aligned big Sea of Stars
head) turns it into editable role layers, each part with a 1-texel near-black outline and upper-left light / lower-right
shadow planes. Raster primitives, ORA layout and the established PXO writer (female south-run v06 make_pxo) are the same
code; the costume, body, weapon and fx below are Zhao's own, not the male coat/scarf/knife.

Identity (current zexplore25 exploration identity, Zhao palette copied literally from
tools/...zhao-ling_explore-source-author_unapproved-v01_20261021-172651-9f823054.py PAL): charcoal asymmetric chin-length
bob with teal tips (long side toward the viewer), teal headset with the near earcup visible and the far (left) earcup
antenna rising behind the head with a brass tip, oversized dark jacket with a grey collar and rolled grey cuffs over a
white tee, fingerless dark gloves, crossbody straps, portable radio on the LEFT hip (far side, peeking behind the back),
tablet in the far hand, baggy charcoal trousers with rolled cuffs, black boots. Signature: handgun (ranged firing with
recoil, no blade, no melee smear). Skill "Echo ranging": headset tune -> radio/antenna ping -> tablet ranging sweep.

Contract = heroine hsc19 / male mcombat22: schema worlds-between.combat-sprite-set/1, 136x144 cell, pivot (64,136),
authored facing right, logical scale 0.5, display proportion "0.65", 30 tick/s, 6-column sheet, actions idle/move/guard/
attack/dodge/skill/hit/defeat, per-action total ticks equal to the heroine set. Character is {"member_id": "zhao-ling"}
with no appearance key; the runtime index has only the "zhao-ling" key (no hero key). Attack: the firing cue (muzzle flash)
is the FIRST attack frame (tick 0), matching the existing immediate companion attack; no delayed damage is implied.
No victory poses. The combat static is the idle-a pose exported as its own named package.

    python -X utf8 -I <tool> build | check [--pixelorama EXE]
Writes only NEW files under outputs/zcombat26 and game/data/zcombat26.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, io, json, math, os, shutil, subprocess, sys, tempfile, zipfile
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/zcombat26"
PKG = ROOT / "game/data/zcombat26"
SLUG, SUBJECT, VER, STAMP, UID = "rpg-2-star-ocean-the-second", "zhao-ling-combat", "unapproved-zcombat26-v01", "20261021-180157", "5d3c9a71"
MEMBER = "zhao-ling"
WRITER = ROOT / "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py"
HERO_MANIFEST = ROOT / "game/data/hsc19/rpg-2-star-ocean-the-second_heroine-sea-combat_pose-revision_spritesheet-manifest_20261021-034640-07587a3c.json"
HERO_SHEET = HERO_MANIFEST.with_name("rpg-2-star-ocean-the-second_heroine-sea-combat_pose-revision_spritesheet_20261021-034640-07587a3c.png")
MALE_SHEET = ROOT / "game/data/mcombat22/rpg-2-star-ocean-the-second_protagonist-male-combat_runtime-spritesheet_unapproved-v01_20261021-120000-a376c0d6.png"
EXPLORE_TOOL = "tools/rpg-2-star-ocean-the-second_zhao-ling_explore-source-author_unapproved-v01_20261021-172651-9f823054.py"
PORTRAIT = "outputs/rpg-2-star-ocean-the-second_zhao-ling_character-sheet_v01_20261013-193120-54215370.png"
W, H = 136, 144
PIN = (64, 136)
COLS = 6
TICK = 30
ZIP_DT = (2026, 10, 21, 18, 1, 56)
LAYERS = ["far-gear", "arm-back", "leg-back", "leg-front", "jacket-back", "torso", "tablet", "head", "weapon", "arm-front", "fx"]

PAL_HEX = {   # literal copy of the zexplore25 Zhao PAL
    "K": "#0c0d12", "k": "#1f2029", "S": "#f4d8c6", "s": "#dcb09c", "z": "#b3806f", "H": "#525b76",
    "h": "#2f3348", "g": "#151722", "B": "#8fd3e6", "b": "#4f9dbf", "n": "#2c6585", "W": "#d7dce2",
    "w": "#8f98a8", "v": "#535b6b", "Y": "#e8c780", "y": "#b48c4d", "u": "#6c5133", "J": "#666a7d",
    "j": "#424556", "q": "#272935", "C": "#dfe0e5", "c": "#abaeb9", "x": "#777b8c", "T": "#f6f4ee",
    "L": "#7c5745", "l": "#4c342b", "P": "#74767f", "p": "#54565f", "D": "#5a5d6b", "d": "#2a2c36",
    "e": "#6f93ad", "E": "#1b2132", "m": "#b8706c"}
PAL = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in PAL_HEX.items()}
R_HAIR, R_TEAL, R_SKIN = ("H", "h", "g"), ("B", "b", "n"), ("S", "s", "z")
R_JACK, R_JACKD, R_COLL, R_TEE = ("J", "j", "q"), ("j", "q", "d"), ("C", "c", "x"), ("T", "C", "c")
R_TROU, R_TROUD, R_BOOT, R_GLOVE = ("P", "p", "d"), ("p", "d", "E"), ("v", "k", "E"), ("j", "k", "E")
R_BRASS, R_GUN, R_RADIO, R_STRAP = ("Y", "y", "u"), ("W", "w", "v"), ("D", "v", "d"), ("L", "l", "l")

NEUTRAL_PELVIS = (62.0, 92.0)
THIGH, SHIN = 21.0, 21.0
UPPER, FORE = 13.0, 12.0

# Pose rows. pel: pelvis offset; lean: upper-body rotation (deg, + = toward the enemy); feet: ankle targets (sole row 135 when
# y=130); fh/bh: front (gun) / back (tablet) hand offsets from the shoulder; aim: handgun barrel deg (0 = +x level, + = down);
# tab: tablet deg in the back hand; hem: jacket hem follow-through (x); ant: antenna sway (deg from vertical, - = back);
# eyes: open|shut|wince|aim; fx: none|flash|smoke|ping|sweep|lock; head: head offset.
D = dict(pel=(0, 0), lean=3.0, feet=((52, 130), (76, 130)), fh=(10, 13), bh=(7, 15), aim=55.0, tab=70.0, hem=0, ant=-12.0,
         eyes="open", fx="none", head=(0, 0))


def pose(**kw):
    p = dict(D)
    p.update(kw)
    return p


P = {
    "idle-a": pose(),
    "idle-b": pose(pel=(0, 1), lean=4.0, fh=(10, 14), bh=(7, 16), aim=58.0, tab=72.0, hem=-1, ant=-15.0),
    "move-a": pose(pel=(1, 1), lean=8.0, feet=((49, 130), (81, 130)), fh=(11, 12), bh=(4, 16), aim=48.0, tab=64.0, hem=-3, ant=-20.0),
    "move-b": pose(pel=(3, -2), lean=7.0, feet=((56, 126), (79, 130)), fh=(11, 11), bh=(5, 15), aim=46.0, tab=66.0, hem=-4, ant=-24.0),
    "move-c": pose(pel=(4, 1), lean=8.0, feet=((55, 130), (85, 128)), fh=(11, 12), bh=(4, 16), aim=48.0, tab=64.0, hem=-3, ant=-20.0),
    "move-d": pose(pel=(3, -1), lean=7.0, feet=((53, 130), (82, 130)), fh=(12, 11), bh=(5, 15), aim=46.0, tab=66.0, hem=-2, ant=-22.0),
    "guard-in": pose(pel=(-1, 2), lean=-1.0, fh=(9, 8), bh=(15, -2), aim=20.0, tab=-80.0, hem=1, ant=-8.0),
    "guard-hold": pose(pel=(-2, 4), lean=-4.0, feet=((49, 130), (77, 130)), fh=(9, 6), bh=(16, -5), aim=15.0, tab=-86.0, hem=2, ant=-6.0),
    "attack-fire": pose(pel=(2, 2), lean=2.0, feet=((51, 130), (82, 130)), fh=(21, -3), bh=(3, 17), aim=0.0, tab=80.0, hem=-1,
                        ant=-14.0, eyes="aim", fx="flash"),
    "attack-recoil": pose(pel=(-1, 2), lean=-4.0, feet=((51, 130), (82, 130)), fh=(18, -7), bh=(2, 17), aim=-16.0, tab=82.0, hem=2,
                          ant=-4.0, eyes="aim", fx="smoke", head=(-1, 0)),
    "attack-hold": pose(pel=(1, 2), lean=1.0, feet=((51, 130), (82, 130)), fh=(20, -4), bh=(3, 17), aim=-2.0, tab=80.0, hem=0,
                        ant=-10.0, eyes="aim"),
    "attack-recover": pose(pel=(0, 1), lean=2.0, feet=((52, 130), (79, 130)), fh=(13, 8), bh=(6, 16), aim=35.0, tab=74.0, hem=0, ant=-12.0),
    "dodge-hop": pose(pel=(-9, -6), lean=10.0, feet=((40, 122), (62, 124)), fh=(9, 14), bh=(-3, 16), aim=40.0, tab=60.0, hem=7,
                      ant=-30.0, head=(0, 1)),
    "dodge-land": pose(pel=(-12, 9), lean=14.0, feet=((38, 130), (62, 130)), fh=(13, 12), bh=(4, 17), aim=25.0, tab=70.0, hem=5, ant=-22.0),
    "skill-tune": pose(pel=(-1, 3), lean=6.0, feet=((51, 130), (76, 130)), fh=(7, 16), bh=(13, 3), aim=80.0, tab=-20.0, hem=0,
                       ant=-8.0, eyes="shut", head=(0, 1)),
    "skill-ping": pose(pel=(0, 2), lean=-3.0, feet=((51, 130), (77, 130)), fh=(7, 16), bh=(15, 0), aim=82.0, tab=-30.0, hem=-1,
                       ant=4.0, fx="ping"),
    "skill-sweep": pose(pel=(1, 2), lean=-2.0, feet=((51, 130), (78, 130)), fh=(8, 15), bh=(17, -2), aim=80.0, tab=-40.0, hem=-1,
                        ant=0.0, eyes="aim", fx="sweep"),
    "skill-lock": pose(pel=(1, 1), lean=1.0, feet=((51, 130), (78, 130)), fh=(18, -2), bh=(12, 6), aim=-1.0, tab=-10.0, hem=0,
                       ant=-8.0, eyes="aim", fx="lock"),
    "hit-recoil": pose(pel=(-6, 3), lean=-15.0, feet=((49, 130), (74, 130)), fh=(5, 15), bh=(-7, 12), aim=70.0, tab=95.0, hem=6,
                       ant=-34.0, eyes="wince", head=(-2, 0)),
    "hit-stagger": pose(pel=(-5, 6), lean=9.0, feet=((47, 130), (73, 130)), fh=(9, 16), bh=(2, 17), aim=62.0, tab=80.0, hem=4,
                        ant=-20.0, eyes="wince"),
    "defeat-buckle": pose(pel=(-4, 10), lean=18.0, feet=((48, 130), (74, 130)), fh=(6, 19), bh=(3, 19), aim=85.0, tab=95.0, hem=3,
                          ant=-26.0, eyes="wince"),
    "defeat-knee": pose(pel=(-3, 22), lean=26.0, feet=((40, 130), (74, 130)), fh=(12, 21), bh=(8, 20), aim=95.0, tab=110.0, hem=2,
                        ant=-30.0, eyes="shut"),
    "defeat-down": pose(pel=(-2, 30), lean=40.0, feet=((36, 130), (66, 130)), fh=(16, 18), bh=(12, 18), aim=170.0, tab=175.0, hem=2,
                        ant=-40.0, eyes="shut", head=(0, 2)),
}
KNEELING = {"defeat-knee": "back", "defeat-down": "both"}
AIRBORNE = {"dodge-hop"}
CELLS = list(P)
# Runtime timing (30 tick/s). Totals equal the heroine hsc19 set; the firing cue is attack frame 0 (tick 0).
ACTIONS = {
    "idle": {"loop": True, "loop_start": 0, "frames": [("idle-a", 14), ("idle-b", 14)]},
    "attack": {"loop": False, "frames": [("attack-fire", 2), ("attack-recoil", 3), ("attack-hold", 3), ("attack-recover", 4), ("idle-a", 1)]},
    "move": {"loop": True, "loop_start": 0, "frames": [("move-a", 3), ("move-b", 3), ("move-c", 3), ("move-d", 3)]},
    "guard": {"loop": True, "loop_start": 1, "frames": [("guard-in", 2), ("guard-hold", 12)]},
    "dodge": {"loop": False, "frames": [("dodge-hop", 4), ("dodge-land", 4), ("idle-a", 1)]},
    "skill": {"loop": False, "frames": [("skill-tune", 4), ("skill-ping", 3), ("skill-sweep", 3), ("skill-lock", 3), ("idle-a", 1)]},
    "hit": {"loop": False, "frames": [("hit-recoil", 3), ("hit-stagger", 4), ("idle-a", 1)]},
    "defeat": {"loop": False, "frames": [("defeat-buckle", 3), ("defeat-knee", 3), ("defeat-down", 3)]},
}
FIRING_CUE_TICK = 0


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


# ---------------------------------------------------------------- raster primitives (same as mcombat22)
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

    # far gear (behind everything): portable radio on her LEFT hip peeking behind the back, its whip antenna, and the
    # far (left) earcup antenna rising behind the head with a brass tip
    fg = L["far-gear"]
    part(fg, m_poly([U(-15, -9), U(-5, -9), U(-5, 6), U(-15, 6)]), R_RADIO)
    put(fg, m_poly([U(-14, -7), U(-10, -7), U(-10, -3), U(-14, -3)]), "b")                 # radio screen
    put(fg, m_cap(U(-14, 3), U(-12, 3), 0.6), "Y")                                           # brass knob
    put(fg, m_cap(U(-6, -8), U(-6, 5), 0.5), "y")                                            # brass edge
    put(fg, m_cap(U(-13, -9), U(-15, -16), 0.7), "k")                                        # radio stub antenna
    a_base = (cx - 3, cy - 2)
    a_tip = add(a_base, rot((0, -22), p["ant"]))
    put(fg, dil4(m_cap(a_base, a_tip, 0.6)) & ~m_cap(a_base, a_tip, 0.6), "K")
    put(fg, m_cap(a_base, a_tip, 0.6), "k")
    part(fg, m_ell(a_tip, 1.4, 1.4), R_BRASS, band=1)
    info["antennaTip"] = [round(a_tip[0], 2), round(a_tip[1], 2)]

    # legs: baggy charcoal trousers with a rolled lighter cuff, black boots
    def leg(layer, hip, ankle, dark, which):
        kneel = KNEELING.get(pid) in (which, "both")
        if kneel:
            dy = 131.0 - hip[1]
            stretch = max(0.0, abs(dy) - THIGH)
            knee = (hip[0] + math.sqrt(max(0.0, THIGH * THIGH - dy * dy)) * (0.35 if which == "back" else 0.8), 131.0)
            stretch = max(stretch, math.dist(hip, knee) - THIGH)
            ankle = (knee[0] - SHIN + 2, 131.0)
        else:
            knee, stretch = ik(hip, ankle, THIGH, SHIN, +1)
        tr = R_TROUD if dark else R_TROU
        roll = add(knee, ((ankle[0] - knee[0]) * 0.62, (ankle[1] - knee[1]) * 0.62))
        thigh = m_cap(hip, knee, 4.6)
        shin = m_cap(knee, roll, 4.3)
        cuff = m_cap(roll, add(roll, ((ankle[0] - knee[0]) * 0.1, (ankle[1] - knee[1]) * 0.1)), 4.0)
        if kneel:
            foot = m_poly([(ankle[0] - 3, ankle[1] - 3), (ankle[0] + 1, ankle[1] - 3), (ankle[0] + 1, 135), (ankle[0] - 9, 135), (ankle[0] - 9, 132)])
        else:
            lift = 0 if ankle[1] >= 130 else ankle[1] - 130
            foot = m_poly([(ankle[0] - 4, ankle[1] - 4), (ankle[0] + 3, ankle[1] - 3), (ankle[0] + 8, 132 + lift), (ankle[0] + 8, 135 + lift),
                           (ankle[0] - 4, 135 + lift)])
        boot = m_cap(add(roll, (0, 2)), ankle, 3.4) | foot
        part(layer, boot, R_BOOT)
        part(layer, thigh | shin, tr)
        part(layer, cuff, ("x", "p", "p") if dark else ("c", "x", "x"), band=1)
        if not kneel:
            put(layer, m_cap((ankle[0] - 4, 134 + (0 if ankle[1] >= 130 else ankle[1] - 130)),
                             (ankle[0] + 7, 134 + (0 if ankle[1] >= 130 else ankle[1] - 130)), 0.5), "q")   # lug sole line
        put(layer, m_cap(add(knee, (-1, 2)), add(knee, (2, 5)), 0.5), "d")                          # baggy fold
        info["joints"][which] = {"hip": [round(hip[0], 2), round(hip[1], 2)], "knee": [round(knee[0], 2), round(knee[1], 2)],
                                 "ankle": [round(ankle[0], 2), round(ankle[1], 2)], "stretch": round(stretch, 3)}

    leg(L["leg-back"], U(-3, 0), p["feet"][0], True, "back")
    leg(L["leg-front"], U(3, 0), p["feet"][1], False, "front")

    # oversized jacket: back hem drops over the seat behind the legs
    h = p["hem"]
    part(L["jacket-back"], m_poly([U(-10, -6), U(5, -6), U(4 + h * 0.3, 9), add(U(-12, 11), (h, 0))]), R_JACKD)

    # torso: boxy oversized jacket, white tee in the opening, grey collar, crossbody straps, belt
    t = L["torso"]
    part(t, m_poly([U(-10, -30), U(7, -31), U(10, -18), U(9, 8), U(-10, 9), U(-11, -18)]), R_JACK)
    part(t, m_poly([U(5, -28), U(9, -27), U(9, -6), U(6, -6)]), R_TEE, outline=False, band=1)
    put(t, m_cap(U(5, -27), U(5, 7), 0.5), "q")                                               # zip/placket edge
    part(t, m_poly([U(-8, -34), U(6, -34), U(9, -28), U(4, -25), U(-4, -26), U(-10, -29)]), R_COLL, band=1)   # grey collar
    put(t, m_cap(U(-8, -27), U(7, -5), 0.8), "l")                                             # crossbody strap
    put(t, m_cap(U(-8, -27), U(7, -5), 0.5), "L")
    put(t, m_cap(U(7, -26), U(-8, -2), 0.7), "q")                                             # second strap to the left-hip radio
    put(t, m_cap(U(1, -16), U(2, -16), 0.7), "Y")                                             # brass buckle
    part(t, m_poly([U(-10, -2), U(9, -2), U(9, 1), U(-10, 1)]), ("j", "q", "E"), band=1)      # belt
    put(t, m_cap(U(6, -1), U(7, -1), 0.6), "y")
    put(t, m_cap(U(-9, 4), U(-9, 9), 0.5), "q")                                               # jacket hem seam
    put(t, m_cap(U(-6, -20), U(-6, -12), 0.5), "c")                                           # sleeve-side reflective tab

    # head: big Sea of Stars head, asymmetric charcoal bob (long side toward the viewer) with teal tips, headset
    hd = L["head"]
    part(hd, m_cap(U(-1, -33), U(2, -33), 2.6), R_SKIN, band=1)                                # neck
    head = m_ell(hc, 10.5, 11.5)
    part(hd, head, R_SKIN)
    yy, xx = np.mgrid[0:H, 0:W]
    hair = (head & (yy < cy - 3)) | (head & (xx < cx + 1))
    hair |= m_ell((cx - 3, cy - 5), 10, 7)
    hair |= m_poly([(cx - 12, cy - 4), (cx - 10, cy + 9), (cx - 5, cy + 11), (cx + 1, cy + 9), (cx + 1, cy - 2)])   # bob mass to the chin
    hair |= m_poly([(cx + 1, cy - 11), (cx + 11, cy - 7), (cx + 9, cy - 1), (cx + 5, cy - 4)])                      # swept fringe
    hair |= m_poly([(cx - 1, cy + 3), (cx + 3, cy + 2), (cx + 2, cy + 12), (cx - 2, cy + 11)])                      # long side lock by the cheek
    part(hd, hair, R_HAIR)
    tips = hair & ~shift(hair, -2, 0) & (yy >= cy + 5)                                       # teal only on the lower ends
    put(hd, tips, "b")
    put(hd, tips & ~shift(hair, -1, 0) & (xx % 2 == 0), "B")
    put(hd, m_cap((cx - 9, cy - 9), (cx + 3, cy - 12), 0.6), "H")                             # crown highlight
    put(hd, m_cap((cx - 2, cy + 1), (cx - 1, cy + 9), 0.5), "g")                              # strand break
    ex, ey = round(cx + 6), round(cy + 1)
    if p["eyes"] in ("open", "aim"):
        hd[ey:ey + 3, ex:ex + 2, :3] = PAL["E"]
        hd[ey + 1, ex + 1, :3] = PAL["e"]
        if p["eyes"] == "aim":
            hd[ey - 1, ex - 1:ex + 3, :3] = PAL["g"]                                         # narrowed lid
    elif p["eyes"] == "shut":
        hd[ey + 1, ex - 1:ex + 3, :3] = PAL["g"]
    else:
        hd[ey, ex:ex + 3, :3] = PAL["g"]
        hd[ey + 1, ex - 1, :3] = PAL["g"]
        hd[ey + 1, ex + 3, :3] = PAL["g"]
    hd[ey - 2, ex - 1:ex + 3, :3] = PAL["h"]                                                  # brow
    hd[round(cy + 7), round(cx + 6):round(cx + 8), :3] = PAL["m"]                             # mouth
    # headset: band over the crown, near (right) earcup with a brass rim, mic boom
    band = m_cap((cx - 6, cy - 12), (cx - 2, cy - 2), 1.2)
    put(hd, dil4(band) & ~band & ~hair, "K")
    put(hd, band, "k")
    cup = m_ell((cx - 3, cy + 1), 3.6, 4.4)
    put(hd, dil4(cup) & ~cup, "K")
    part(hd, cup, R_TEAL, outline=False, band=1)
    put(hd, m_ell((cx - 3, cy + 1), 3.6, 4.4) & ~m_ell((cx - 3, cy + 1), 2.6, 3.4), "y")
    put(hd, m_ell((cx - 3, cy + 1), 1.4, 1.8), "n")
    put(hd, m_cap((cx - 1, cy + 4), (cx + 5, cy + 8), 0.5), "k")                              # mic boom

    # arms: oversized dark sleeve -> rolled grey cuff -> forearm -> fingerless glove (skin fingertips)
    def arm(layer, sh, off, front):
        hand = add(sh, off)
        el, stretch = ik(sh, hand, UPPER, FORE, -1)
        cuff = add(el, ((hand[0] - el[0]) * 0.3, (hand[1] - el[1]) * 0.3))
        part(layer, m_cap(sh, el, 4.0) | m_cap(el, cuff, 3.5), R_JACK if front else R_JACKD)
        part(layer, m_cap(cuff, add(cuff, ((hand[0] - cuff[0]) * 0.22, (hand[1] - cuff[1]) * 0.22)), 3.2), R_COLL, band=1)
        part(layer, m_cap(add(cuff, ((hand[0] - cuff[0]) * 0.3, (hand[1] - cuff[1]) * 0.3)), hand, 2.2), R_SKIN, band=1)
        part(layer, m_ell(hand, 3.0, 3.0), R_GLOVE, band=1)
        put(layer, m_ell(add(hand, (2, 1)), 0.8, 0.8), "s")                                    # bare fingertips
        info["joints"]["arm-front" if front else "arm-back"] = {"shoulder": [round(sh[0], 2), round(sh[1], 2)],
                                                               "elbow": [round(el[0], 2), round(el[1], 2)],
                                                               "hand": [round(hand[0], 2), round(hand[1], 2)], "stretch": round(stretch, 3)}
        return hand

    bhand = arm(L["arm-back"], U(-2, -27), p["bh"], False)
    hand = arm(L["arm-front"], U(3, -26), p["fh"], True)

    # tablet in the far hand (dark rugged frame, teal screen, brass corner)
    T = local(bhand, p["tab"])
    tb = L["tablet"]
    part(tb, m_poly([T(-2, -6), T(14, -6), T(14, 5), T(-2, 5)]), ("D", "k", "E"), band=1)
    put(tb, m_poly([T(0, -4), T(12, -4), T(12, 3), T(0, 3)]), "n")
    put(tb, m_cap(T(2, 0), T(10, -1), 0.5), "B")                                             # waveform trace
    put(tb, m_cap(T(13, -5), T(13, -5), 0.7), "Y")
    put(tb, m_ell(bhand, 2.4, 2.4), "k")                                                      # gripping fingers over the frame
    info["tablet"] = {"grip": [round(bhand[0], 2), round(bhand[1], 2)], "deg": p["tab"]}

    # handgun in the gun hand: grip down-back from the fist, slide + barrel along the aim
    G = local(hand, p["aim"])
    wp = L["weapon"]
    part(wp, m_poly([G(-2, -1), G(2, -1), G(0, 7), G(-4, 6)]), ("v", "k", "E"), band=1)      # grip
    part(wp, m_poly([G(-3, -5), G(12, -5), G(12, -1), G(-3, -1)]), R_GUN, band=1)            # slide
    put(wp, m_cap(G(0, -5), G(9, -5), 0.5), "W")
    put(wp, m_cap(G(10, -2), G(11, -2), 0.5), "v")                                           # muzzle
    put(wp, m_cap(G(1, 0), G(3, 1), 0.5), "k")                                               # trigger guard
    muzzle = G(13, -3)
    info["gun"] = {"grip": [round(hand[0], 2), round(hand[1], 2)], "muzzle": [round(muzzle[0], 2), round(muzzle[1], 2)], "deg": p["aim"]}

    # fx (own layer, no outline): muzzle flash, smoke + ejected brass, echo ping rings, ranging sweep, lock reticle
    fx = L["fx"]
    if p["fx"] == "flash":
        F = local(muzzle, p["aim"])
        put(fx, m_poly([F(0, -3), F(10, 0), F(0, 3)]), "Y")
        put(fx, m_poly([F(2, -6), F(6, 0), F(2, 6)]) | m_cap(F(0, 0), F(7, 0), 1.0), "T")
        put(fx, m_poly([F(1, -1), F(13, 0), F(1, 1)]), "T")
        put(fx, m_cap(F(0, 0), F(3, 0), 0.8), "Y")
    elif p["fx"] == "smoke":
        F = local(muzzle, p["aim"])
        for k, (dx, dy, r) in enumerate(((2, -2, 1.6), (5, -4, 2.0), (8, -7, 1.6))):
            put(fx, m_ell(F(dx, dy), r, r), "c" if k % 2 else "x")
        cas = G(-1, -9)
        put(fx, m_cap(cas, add(cas, (1, -1)), 0.6), "Y")                                         # ejected casing
    elif p["fx"] in ("ping", "sweep"):
        c0 = a_tip if p["fx"] == "ping" else T(14, 0)
        rr = np.hypot(xx - c0[0], yy - c0[1])
        aa = np.degrees(np.arctan2(yy - c0[1], xx - c0[0]))
        if p["fx"] == "ping":
            for r0, k in ((5, "B"), (10, "b"), (15, "B")):
                put(fx, (np.abs(rr - r0) <= 0.6) & ((aa > -170) & (aa < 10)), k)
        else:
            for r0, k in ((7, "B"), (14, "b"), (21, "B"), (28, "b")):
                put(fx, (np.abs(rr - r0) <= 0.6) & (np.abs(aa) <= 32), k)
    elif p["fx"] == "lock":
        rc = (124.0, cy + 8)
        ring = (np.abs(np.hypot(xx - rc[0], yy - rc[1]) - 6) <= 0.6)
        put(fx, ring, "B")
        for v in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            put(fx, m_cap(add(rc, (v[0] * 3, v[1] * 3)), add(rc, (v[0] * 9, v[1] * 9)), 0.5), "b")
        put(fx, m_ell(rc, 0.8, 0.8), "Y")
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
        "schema": "worlds-between.combat-sprite-set/1", "set_id": "zhao-ling-combat-zcombat26-v01",
        "character": {"member_id": MEMBER},
        "art_status": "unapproved-zhao-ling-combat-source-poses-technical-only", "art_approved": False, "motion_approved": False,
        "default_adoption": False,
        "note": "Deterministic authored source set for Zhao Ling (handgun signature, Echo ranging skill); not creator-approved art or "
                "motion, not a default, not wired. Loadable only through the explicit member-only zcombat26 index.",
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
        "status": "UNAPPROVED Zhao Ling combat static + eight-action source set; technical source only; runtime default unchanged.",
        "member_id": MEMBER, "methodFrom": "tools/rpg-2-star-ocean-the-second_protagonist-male_combat-static-and-actions-author_unapproved-v01_20261021-120000-b7e2c4d1.py",
        "paletteFrom": EXPLORE_TOOL, "identityReference": {"portraitConcept": PORTRAIT, "portraitIsConceptNotApproval": True,
                                                         "exploreEastStatic": "game/data/zexplore25/png/rpg-2-star-ocean-the-second_zhao-ling_explore-east-static_unapproved-zexplore25-v01_20261021-172651-7dd301f6.png"},
        "contractFrom": rel(HERO_MANIFEST), "layers": LAYERS, "cell": [W, H], "pivot": list(PIN), "tickRate": TICK,
        "signature": "handgun ranged fire with recoil (no blade, no melee smear)",
        "skill": "Echo ranging: headset tune -> antenna ping -> tablet ranging sweep -> target lock",
        "combatStatic": {"pose": "idle-a", "png": files["still.png"][1], "ora": files["still.ora"][1], "pxo": files["still.pxo"][1]},
        "runtimeActions": {a: {"frames": [[pid, t] for pid, t in s["frames"]], "loop": s["loop"], "totalTicks": sum(t for _, t in s["frames"])}
                           for a, s in ACTIONS.items()},
        "firingCueTick": FIRING_CUE_TICK,
        "firingCueNote": "muzzle flash is attack frame 0 (tick 0), matching the existing immediate companion attack; no delayed damage",
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


def gates(files, flats, built, manifest, index):
    res = []

    def gate(k, ok, info=None):
        res.append({"key": k, "pass": bool(ok), "info": info})
    pal = set(PAL.values())
    for pid, flat in flats.items():
        op = flat[..., 3] > 0
        ys, xs = np.nonzero(op)
        cols = {tuple(c) for c in flat[op][:, :3].tolist()}
        L, info = built[pid]
        gate(f"{pid}: binary alpha + declared Zhao palette only", set(np.unique(flat[..., 3]).tolist()) <= {0, 255} and cols <= pal, len(cols))
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
                 (("hair", "Hhg"), ("teal tips/headset", "Bbn"), ("jacket", "Jjq"), ("collar/cuffs", "Ccx"), ("brass", "Yy"),
                  ("handgun", "Ww"), ("radio", "D"))}
        gate(f"{pid}: Zhao identity cues present (hair/teal/jacket/collar/brass/gun/radio texels)", all(v >= 4 for v in ident.values()), ident)
        gate(f"{pid}: no blade/melee smear keys (male scarf/coat/leather palette absent)",
             not ({(0x82, 0xc8, 0xb8), (0x8c, 0x76, 0x64), (0xb2, 0x7c, 0x4e)} & cols))
    gate("all pose images unique", len({sha(files[f'{p}.png'][2]) for p in P}) == len(P))
    for a, s in ACTIONS.items():
        ids = [pid for pid, _ in s["frames"]]
        diffs = [int((np.any(flats[x] != flats[y], -1)).sum()) for x, y in zip(ids, ids[1:])]
        gate(f"{a}: consecutive frames visibly different (>= 60 texels)", all(d >= 60 for d in diffs), diffs)
    hero = json.loads(HERO_MANIFEST.read_text(encoding="utf-8"))
    gate("manifest top-level keys == heroine hsc19 manifest", list(manifest) == list(hero), [k for k in hero if k not in manifest])
    gate("character is member-only zhao-ling (no appearance key)", manifest["character"] == {"member_id": MEMBER})
    gate("index has exactly the zhao-ling key, no hero key, names the manifest",
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
    gate("firing cue (muzzle flash) on attack frame 0 = tick 0; no other attack frame flashes",
         first == "attack-fire" and P[first]["fx"] == "flash" and FIRING_CUE_TICK == 0
         and all(P[pid]["fx"] != "flash" for pid, _ in ACTIONS["attack"]["frames"][1:]))
    gate("recoil after the shot: muzzle rises and the hand pulls back on attack-recoil",
         P["attack-recoil"]["aim"] < P["attack-fire"]["aim"] and P["attack-recoil"]["fh"][0] < P["attack-fire"]["fh"][0])
    gate("skill = Echo ranging (ping from antenna, sweep from tablet, lock reticle)",
         [P[x]["fx"] for x, _ in ACTIONS["skill"]["frames"][1:4]] == ["ping", "sweep", "lock"])
    gate("defeat ends kneeling with eyes shut", P["defeat-down"]["eyes"] == "shut" and KNEELING["defeat-down"] == "both")
    sheet = decode(files["sheet"][2])
    gate("sheet is a cell multiple, 6 columns, each cell == its pose PNG; package copy == outputs copy",
         sheet.shape[1] == COLS * W and sheet.shape[0] % H == 0 and files["sheet"][2] == files["pkg.sheet"][2] and
         all(np.array_equal(sheet[(i // COLS) * H:(i // COLS + 1) * H, (i % COLS) * W:(i % COLS + 1) * W], flats[pid]) for i, pid in enumerate(CELLS)))
    mo = flats["idle-a"][..., 3] > 0
    for lab, path in (("heroine", HERO_SHEET), ("male mcombat22", MALE_SHEET)):
        o = np.array(Image.open(path).convert("RGBA"))[0:H, 0:W, 3] > 0
        iou = float((o & mo).sum() / (o | mo).sum())
        gate(f"idle silhouette distinct from {lab} idle (IoU < 0.85, not a recolour)", iou < 0.85, round(iou, 3))
    gate("still package pixels == idle-a", files["still.png"][2] == files["idle-a.png"][2])
    gate("all asset names <= 140 chars and in project/subject/purpose/variant/timestamp-id form",
         all(len(n) <= 140 and n.startswith(f"{SLUG}_{SUBJECT}_") and f"_{VER}_{STAMP}-" in n for _, n, _ in files.values()))
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
    split_ids = {"still", "attack-fire", "skill-sweep", "defeat-down"}
    for role in sorted(r for r in files if r.endswith(".pxo")):
        pid = role[:-4]
        pxo = str(long(OUT / files[role][1]))
        want = decode(files[f"{pid}.png"][2])
        layers = built["idle-a" if pid == "still" else pid][0]
        rec = {"pxo": files[role][1]}
        for split in ([False, True] if pid in split_ids else [False]):
            tmp = tempfile.mkdtemp(prefix="wb-zc26-")
            try:
                p, outs = pixelorama_export(exe, pxo, tmp, split)
                diag = [ln.strip() for ln in (p.stdout + p.stderr).splitlines() if any(t in ln for t in ("ERROR", "SCRIPT ERROR", "WARNING"))]
                names = sorted(outs)
                if split:
                    got = {n: decode(outs[n]) for n in names}
                    # match every exported layer PNG to the source layer with identical pixels (non-empty layers only)
                    src = [n for n in LAYERS if (layers[n][..., 3] > 0).any()]
                    matched = sum(1 for n in src if any(np.array_equal(g, layers[n]) for g in got.values()))
                    ok = p.returncode == 0 and matched == len(src)
                    rec["split"] = {"exit": p.returncode, "exported": len(names), "matched": f"{matched}/{len(src)}", "diagnostics": diag[:8]}
                else:
                    eq = len(names) == 1 and np.array_equal(decode(outs[names[0]]), want)
                    ok = p.returncode == 0 and eq
                    rec["flat"] = {"exit": p.returncode, "exported": len(names), "equal": bool(eq), "diagnostics": diag[:8]}
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
    if a.mode == "build":
        for role, (d, n, b) in files.items():
            os.makedirs(long(d), exist_ok=True)
            p = long(d / n)
            if p.exists():
                assert p.read_bytes() == b, f"refusing to overwrite a different file: {n}"
            else:
                p.write_bytes(b)
        lst = {"schema": "zcombat26-file-list/1", "files": [{"role": r, "path": rel(d / n), "sha256": sha(b)} for r, (d, n, b) in sorted(files.items())]}
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
        res.append({"key": "Pixelorama native open/export equality (flat all PXOs; split layers still/attack-fire/skill-sweep/defeat-down)",
                    "pass": not nf, "info": nf})
    fails = [r for r in res if not r["pass"]]
    for r in fails:
        print("FAIL", r["key"], r["info"])
    diags = sorted({d for r in (nat or []) for v in r.values() if isinstance(v, dict) for d in v["diagnostics"]})
    if diags:
        print("PIXELORAMA DIAGNOSTICS (disclosed):", len(diags), "unique lines")
        for d in diags[:10]:
            print("  ", d[:200])
    print("ZCOMBAT26", a.mode.upper(), "PASS" if not fails else "FAIL", f"{len(res) - len(fails)}/{len(res)}")
    if a.mode == "check":
        rep = name("source-check-report-pixelorama" if a.pixelorama else "source-check-report", "json")
        with open(long(OUT / rep), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"mode": "check", "pixelorama": a.pixelorama, "gates": res, "native": nat, "diagnostics": diags,
                                "passed": len(res) - len(fails), "total": len(res)}, indent=1, ensure_ascii=False) + "\n")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
