"""Male protagonist side-view combat static + all combat action source poses (mcombat22). UNAPPROVED, NOT A DEFAULT.

Deterministic author: every pose is a parameter row (pelvis offset, upper-body lean about the waist, ankle targets,
hand targets, blade angle, coat/scarf follow-through, eyes, fx). A small rig turns each row into 11 editable role layers
(two-bone IK legs and arms, upper body rotated about the pelvis, axis-aligned big Sea of Stars head), each part with its
own 1-texel near-black outline and upper-left light / lower-right shadow planes from the male identity ramps
(tools/...protagonist-male_south-idle-v8pair...f28bd26d.py RAMPS, copied literally below). Identity cues: tousled
outward-pointing dark-brown short hair (no ponytail), tea-green scarf with a trailing tail, open grey-brown field coat
with a flaring split skirt, cream shirt, olive trousers, tall brown boots, brown pack with a teal bedroll on the back.

Contract reused from the heroine Sea combat set (game/data/hsc19): schema worlds-between.combat-sprite-set/1, 136x144
cell, pivot (64,136), authored facing right, logical scale 0.5, display proportion 0.65, 30 tick/s, 6-column sheet,
canonical runtime actions idle/move/guard/attack/dodge/hit/defeat (+ optional skill). Per-action total ticks and the
attack contact start tick equal the heroine set so combat timing is unchanged. "victory" is not a runtime action in the
loader (unknown actions reject a set), so its two poses are supplemental sources listed only in the author manifest.
The battle still (combat static) is the idle-a pose, exported as its own named package.

    build | check (default)
"""
from pathlib import Path
import hashlib, importlib.util, io, json, math, os, sys, zipfile
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/mcombat22"
SLUG, SUBJECT, VER, STAMP, UID = "rpg-2-star-ocean-the-second", "protagonist-male-combat", "unapproved-v01", "20261021-120000", "b7e2c4d1"
WRITER = ROOT / "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py"
HERO_MANIFEST = ROOT / "game/data/hsc19/rpg-2-star-ocean-the-second_heroine-sea-combat_pose-revision_spritesheet-manifest_20261021-034640-07587a3c.json"
HERO_SHEET = HERO_MANIFEST.with_name("rpg-2-star-ocean-the-second_heroine-sea-combat_pose-revision_spritesheet_20261021-034640-07587a3c.png")
W, H = 136, 144
PIN = (64, 136)
COLS = 6
TICK = 30
LAYERS = ["scarf-tail", "pack", "arm-back", "coat-back", "leg-back", "leg-front", "torso", "head", "weapon", "arm-front", "fx"]

RAMPS = {   # literal copy of the male v8pair identity ramps (light upper left)
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
PAL = {k: tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) for r in RAMPS.values() for k, v in r.items()}
R_HAIR, R_SKIN, R_SCARF, R_ROLL = ("1", "2", "3"), ("F", "f", "e"), ("S", "s", "Z"), ("T", "t", "u")
R_COAT, R_COATD, R_LEATH, R_SHIRT = ("A", "B", "C"), ("B", "C", "c"), ("L", "l", "m"), ("W", "w", "v")
R_TROU, R_TROUD, R_BOOT, R_METAL = ("P", "p", "o"), ("p", "o", "o"), ("O", "b", "q"), ("M", "M", "X")

NEUTRAL_PELVIS = (62.0, 92.0)
THIGH, SHIN = 21.0, 21.0
UPPER, FORE = 13.0, 12.0

# Pose rows. pel: pelvis offset; lean: upper-body rotation (deg, + = toward the enemy); feet: ankle targets (world,
# sole row 135 when y=130); fh/bh: front/back hand offsets from the shoulder; blade: deg (0 = +x, -90 = up);
# coat: skirt hem follow-through (x); scarf: tail direction (deg); eyes: open|shut|wince; fx: none|smear|flare.
D = dict(pel=(0, 0), lean=4.0, feet=((51, 130), (77, 130)), fh=(9, 14), bh=(6, 15), blade=-38.0, coat=0, scarf=168.0,
         eyes="open", fx="none", head=(0, 0))


def pose(**kw):
    p = dict(D)
    p.update(kw)
    return p


P = {
    "idle-a": pose(),
    "idle-b": pose(pel=(0, 1), lean=5.0, fh=(9, 15), bh=(6, 16), blade=-36.0, scarf=172.0, coat=-1),
    "move-a": pose(pel=(1, 1), lean=9.0, feet=((49, 130), (81, 130)), fh=(10, 13), bh=(4, 16), blade=-30.0, coat=-3, scarf=176.0),
    "move-b": pose(pel=(3, -2), lean=8.0, feet=((56, 126), (79, 130)), fh=(10, 12), bh=(5, 15), blade=-32.0, coat=-4, scarf=180.0),
    "move-c": pose(pel=(4, 1), lean=9.0, feet=((55, 130), (85, 128)), fh=(10, 13), bh=(4, 16), blade=-30.0, coat=-3, scarf=176.0),
    "move-d": pose(pel=(3, -1), lean=8.0, feet=((53, 130), (82, 130)), fh=(11, 12), bh=(5, 15), blade=-33.0, coat=-2, scarf=178.0),
    "guard-in": pose(pel=(-1, 2), lean=0.0, fh=(12, 4), bh=(12, 8), blade=-80.0, coat=1, scarf=165.0),
    "guard-hold": pose(pel=(-2, 4), lean=-3.0, feet=((49, 130), (77, 130)), fh=(13, 2), bh=(13, 6), blade=-88.0, coat=2, scarf=160.0),
    "attack-windup": pose(pel=(-4, 3), lean=-10.0, feet=((50, 130), (78, 130)), fh=(-12, -4), bh=(8, 12), blade=-150.0, coat=3, scarf=150.0),
    "attack-strike": pose(pel=(6, 4), lean=14.0, feet=((51, 130), (88, 130)), fh=(14, -2), bh=(-6, 14), blade=-40.0, coat=-5, scarf=185.0, fx="smear"),
    "attack-contact": pose(pel=(10, 6), lean=20.0, feet=((53, 130), (93, 130)), fh=(17, 8), bh=(-8, 12), blade=10.0, coat=-7, scarf=190.0, fx="smear"),
    "attack-follow": pose(pel=(9, 6), lean=18.0, feet=((54, 130), (93, 130)), fh=(13, 16), bh=(-7, 10), blade=40.0, coat=-5, scarf=186.0),
    "attack-recover": pose(pel=(4, 3), lean=9.0, feet=((52, 130), (84, 130)), fh=(10, 14), bh=(3, 14), blade=-20.0, coat=-2, scarf=176.0),
    "dodge-hop": pose(pel=(-9, -6), lean=12.0, feet=((40, 122), (62, 124)), fh=(8, 16), bh=(-3, 16), blade=-30.0, coat=7, scarf=205.0, head=(0, 1)),
    "dodge-land": pose(pel=(-12, 9), lean=16.0, feet=((38, 130), (62, 130)), fh=(11, 15), bh=(4, 17), blade=-18.0, coat=5, scarf=196.0),
    "skill-coil": pose(pel=(-2, 7), lean=14.0, feet=((50, 130), (76, 130)), fh=(-4, 17), bh=(7, 9), blade=168.0, coat=1, scarf=178.0, eyes="shut"),
    "skill-raise": pose(pel=(0, 2), lean=-8.0, feet=((51, 130), (78, 130)), fh=(9, -6), bh=(10, 2), blade=-86.0, coat=-1, scarf=150.0),
    "skill-flare": pose(pel=(1, 1), lean=-12.0, feet=((51, 130), (79, 130)), fh=(10, -9), bh=(13, -2), blade=-90.0, coat=-2, scarf=140.0, fx="flare"),
    "skill-settle": pose(pel=(0, 2), lean=-2.0, fh=(10, 10), bh=(8, 12), blade=-55.0, coat=0, scarf=162.0),
    "hit-recoil": pose(pel=(-6, 3), lean=-16.0, feet=((49, 130), (74, 130)), fh=(4, 16), bh=(-8, 12), blade=-10.0, coat=6, scarf=200.0, eyes="wince", head=(-2, 0)),
    "hit-stagger": pose(pel=(-5, 6), lean=10.0, feet=((47, 130), (73, 130)), fh=(8, 17), bh=(2, 18), blade=-12.0, coat=4, scarf=192.0, eyes="wince"),
    "defeat-buckle": pose(pel=(-4, 10), lean=18.0, feet=((48, 130), (74, 130)), fh=(6, 20), bh=(3, 20), blade=60.0, coat=3, scarf=188.0, eyes="wince"),
    "defeat-knee": pose(pel=(-3, 22), lean=26.0, feet=((40, 130), (74, 130)), fh=(12, 22), bh=(8, 20), blade=80.0, coat=2, scarf=186.0, eyes="shut"),
    "defeat-down": pose(pel=(-2, 30), lean=40.0, feet=((36, 130), (66, 130)), fh=(16, 18), bh=(12, 18), blade=6.0, coat=2, scarf=184.0, eyes="shut", head=(0, 2)),
    "victory-flourish": pose(pel=(0, -1), lean=-4.0, fh=(8, -12), bh=(-2, 18), blade=-70.0, coat=-1, scarf=150.0, fx="flare"),
    "victory-hold": pose(pel=(0, 0), lean=-2.0, feet=((53, 130), (75, 130)), fh=(-1, -4), bh=(4, 14), blade=-150.0, coat=0, scarf=158.0),
}
KNEELING = {"defeat-knee": "back", "defeat-down": "both"}
AIRBORNE = {"dodge-hop"}
SUPPLEMENTAL = ["victory-flourish", "victory-hold"]
CELLS = [k for k in P if k not in SUPPLEMENTAL]
# Runtime timing (30 tick/s). Totals and the attack contact start tick equal the heroine hsc19 set.
ACTIONS = {
    "idle": {"loop": True, "loop_start": 0, "frames": [("idle-a", 14), ("idle-b", 14)]},
    "attack": {"loop": False, "frames": [("attack-windup", 3), ("attack-strike", 1), ("attack-contact", 2), ("attack-follow", 3),
                                         ("attack-recover", 3), ("idle-a", 1)]},
    "move": {"loop": True, "loop_start": 0, "frames": [("move-a", 3), ("move-b", 3), ("move-c", 3), ("move-d", 3)]},
    "guard": {"loop": True, "loop_start": 1, "frames": [("guard-in", 2), ("guard-hold", 12)]},
    "dodge": {"loop": False, "frames": [("dodge-hop", 4), ("dodge-land", 4), ("idle-a", 1)]},
    "skill": {"loop": False, "frames": [("skill-coil", 4), ("skill-raise", 3), ("skill-flare", 3), ("skill-settle", 3), ("idle-a", 1)]},
    "hit": {"loop": False, "frames": [("hit-recoil", 3), ("hit-stagger", 4), ("idle-a", 1)]},
    "defeat": {"loop": False, "frames": [("defeat-buckle", 3), ("defeat-knee", 3), ("defeat-down", 3)]},
}
ATTACK_CONTACT_TICK = 4
SUPPLEMENTAL_TIMING = {"victory": {"loop": False, "frames": [("victory-flourish", 6), ("victory-hold", 30)], "runtime": False}}


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


# ---------------------------------------------------------------- raster primitives (PIL, deterministic integer output)
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
    """Outline first (so the part separates from earlier parts in the same layer), then mid/shadow/light planes."""
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
    """Two-bone IK; bend=+1 puts the joint toward +x (knees), -1 toward +y-ish/back (elbows). Returns joint, stretch."""
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


# ---------------------------------------------------------------- the rig
def build(pid):
    p = P[pid]
    L = {n: blank() for n in LAYERS}
    pel = add(NEUTRAL_PELVIS, p["pel"])
    lean = p["lean"]

    def U(x, y):
        return add(pel, rot((x, y), lean))

    info = {"pelvis": [round(pel[0], 2), round(pel[1], 2)], "joints": {}}

    # scarf tail (behind everything): from the back of the neck, tapering, direction p["scarf"]
    nb = U(-3, -31)
    tip = add(nb, rot((20, 0), p["scarf"]))
    mid = add(nb, rot((11, 2), p["scarf"]))
    part(L["scarf-tail"], m_cap(nb, mid, 3.0) | m_cap(mid, tip, 2.0), R_SCARF)

    # pack + teal bedroll on the back
    part(L["pack"], m_poly([U(-16, -29), U(-7, -29), U(-7, -8), U(-15, -9)]), R_LEATH)
    put(L["pack"], m_cap(U(-12, -24), U(-12, -12), 0.5), "m")
    part(L["pack"], m_cap(U(-17, -32), U(-6, -32), 3.6), R_ROLL)
    put(L["pack"], m_cap(U(-11, -35), U(-11, -29), 0.5), "l")

    # legs (two-bone IK, knees toward the enemy); kneeling poses put the knee on the floor
    def leg(layer, hip, ankle, dark, which):
        kneel = KNEELING.get(pid) in (which, "both")
        if kneel:
            # knee rests on the floor (row 131 centre) one thigh length from the hip; shin lies back along the floor
            dy = 131.0 - hip[1]
            stretch = max(0.0, abs(dy) - THIGH)
            knee = (hip[0] + math.sqrt(max(0.0, THIGH * THIGH - dy * dy)) * (0.35 if which == "back" else 0.8), 131.0)
            stretch = max(stretch, math.dist(hip, knee) - THIGH)
            ankle = (knee[0] - SHIN + 2, 131.0)
        else:
            knee, stretch = ik(hip, ankle, THIGH, SHIN, +1)
            s2 = 0.0
        tr, bo = (R_TROUD, R_BOOT) if dark else (R_TROU, R_BOOT)
        bt = add(knee, ((ankle[0] - knee[0]) * 0.45, (ankle[1] - knee[1]) * 0.45))
        thigh = m_cap(hip, knee, 4.0)
        shin = m_cap(knee, bt, 3.4)
        boot = m_cap(bt, ankle, 3.6)
        sole_y = 135 if not kneel else 135
        if kneel:
            foot = m_poly([(ankle[0] - 3, ankle[1] - 3), (ankle[0] + 1, ankle[1] - 3), (ankle[0] + 1, sole_y), (ankle[0] - 9, sole_y), (ankle[0] - 9, sole_y - 3)])
        else:
            lift = 0 if ankle[1] >= 130 else ankle[1] - 130
            foot = m_poly([(ankle[0] - 4, ankle[1] - 3), (ankle[0] + 4, ankle[1] - 2), (ankle[0] + 8, 133 + lift), (ankle[0] + 8, 135 + lift),
                           (ankle[0] - 4, 135 + lift)])
        part(layer, thigh | shin, tr)
        part(layer, boot | foot, bo)
        put(layer, m_cap(add(bt, (-3, 0)), add(bt, (3, 0)), 0.6), "L")      # cuffed boot top
        if not dark:
            put(layer, m_cap(add(knee, (0, -1)), add(knee, (1, 2)), 1.2), "o")  # knee pad
        info["joints"][which] = {"hip": [round(hip[0], 2), round(hip[1], 2)], "knee": [round(knee[0], 2), round(knee[1], 2)],
                                 "ankle": [round(ankle[0], 2), round(ankle[1], 2)], "stretch": round(stretch, 3)}

    leg(L["leg-back"], U(-3, 0), p["feet"][0], True, "back")
    leg(L["leg-front"], U(3, 0), p["feet"][1], False, "front")

    # coat skirt: back flap behind the legs, open front flap over the front thigh
    c = p["coat"]
    part(L["coat-back"], m_poly([U(-8, -4), U(4, -4), U(2 + c * 0.4, 20), add(U(-13, 23), (c, 0))]), R_COATD)
    put(L["coat-back"], m_cap(add(U(-12, 22), (c, 0)), U(1 + c * 0.4, 20), 0.6), "m")

    # torso: coat body, cream shirt in the opening, belt, harness strap, scarf wrap
    t = L["torso"]
    part(t, m_poly([U(-8, -31), U(8, -32), U(9, -16), U(7, 0), U(-8, 0), U(-9, -16)]), R_COAT)
    part(t, m_poly([U(4, -29), U(8, -29), U(8, -6), U(5, -4)]), R_SHIRT, outline=False, band=1)
    put(t, m_cap(U(4, -29), U(4, -5), 0.5), "c")                           # lapel edge
    part(t, m_poly([U(3, -3), U(8, -3), U(11 + c * 0.3, 17), U(4 + c * 0.3, 18)]), R_COAT)    # open front flap
    part(t, m_poly([U(-8, -4), U(8, -4), U(8, 0), U(-8, 0)]), R_LEATH, band=1)                # belt
    put(t, m_cap(U(5, -2), U(6, -2), 0.6), "M")
    put(t, m_cap(U(-7, -29), U(6, -9), 0.7), "l")                           # pack strap across the chest
    put(t, m_cap(U(-3, -2), U(-3, 6), 1.0), "S")                            # teal sash at the hip

    # head: scarf wrap, face, tousled outward-pointing hair, eye, ear
    hd = L["head"]
    neck = U(1, -31)
    hc = add(add(neck, rot((2, -12), lean * 0.6)), p["head"])
    part(hd, m_cap(U(-5, -31), U(6, -31), 3.2), R_SCARF)
    head = m_ell(hc, 10.5, 11.5)
    part(hd, head, R_SKIN)
    cx, cy = hc
    hair = (head & (np.arange(H)[:, None] < cy - 4)) | (head & (np.arange(W)[None, :] < cx - 1))
    spikes = [[(cx - 11, cy - 4), (cx - 18, cy - 9), (cx - 9, cy - 9)], [(cx - 8, cy - 9), (cx - 14, cy - 17), (cx - 3, cy - 11)],
              [(cx - 4, cy - 11), (cx - 4, cy - 19), (cx + 3, cy - 11)], [(cx + 1, cy - 11), (cx + 8, cy - 18), (cx + 8, cy - 8)],
              [(cx + 6, cy - 8), (cx + 14, cy - 10), (cx + 10, cy - 3)], [(cx - 10, cy + 1), (cx - 15, cy + 6), (cx - 8, cy + 6)],
              [(cx + 1, cy - 5), (cx + 3, cy + 1), (cx + 6, cy - 5)]]
    for s in spikes:
        hair |= m_poly(s)
    hair |= m_ell((cx - 3, cy - 5), 9, 7)
    part(hd, hair, R_HAIR)
    put(hd, m_cap((cx - 6, cy - 8), (cx + 2, cy - 9), 0.6), "1")
    ex, ey = round(cx + 6), round(cy + 1)
    if p["eyes"] == "open":
        hd[ey:ey + 3, ex:ex + 2, :3] = PAL["y"]
        hd[ey:ey + 1, ex + 1, :3] = PAL["M"]
    elif p["eyes"] == "shut":
        hd[ey + 1, ex - 1:ex + 3, :3] = PAL["y"]
    else:
        hd[ey, ex:ex + 3, :3] = PAL["y"]
        hd[ey + 1, ex - 1, :3] = PAL["y"]
        hd[ey + 1, ex + 3, :3] = PAL["y"]
    hd[ey - 2, ex - 1:ex + 3, :3] = PAL["3"]                                 # brow
    hd[round(cy + 7), round(cx + 6):round(cx + 9), :3] = PAL["e"]             # mouth
    put(hd, m_ell((cx - 1, cy + 2), 1.6, 2.4), "f")                          # ear

    # arms: shoulder -> elbow (down/back) -> hand; sleeve, rolled cream cuff, forearm, fingerless-gloved fist
    def arm(layer, sh, off, front):
        hand = add(sh, off)
        el, stretch = ik(sh, hand, UPPER, FORE, -1)
        cuff = add(el, ((hand[0] - el[0]) * 0.35, (hand[1] - el[1]) * 0.35))
        part(layer, m_cap(sh, el, 3.6) | m_cap(el, cuff, 3.0), R_COAT if front else R_COATD)
        part(layer, m_cap(cuff, add(cuff, ((hand[0] - cuff[0]) * 0.2, (hand[1] - cuff[1]) * 0.2)), 2.8), R_SHIRT, band=1)
        part(layer, m_cap(add(cuff, ((hand[0] - cuff[0]) * 0.3, (hand[1] - cuff[1]) * 0.3)), hand, 2.2), R_SKIN, band=1)
        part(layer, m_ell(hand, 3.0, 3.0), R_BOOT, band=1)
        info["joints"]["arm-front" if front else "arm-back"] = {"shoulder": [round(sh[0], 2), round(sh[1], 2)],
                                                               "elbow": [round(el[0], 2), round(el[1], 2)],
                                                               "hand": [round(hand[0], 2), round(hand[1], 2)], "stretch": round(stretch, 3)}
        return hand

    arm(L["arm-back"], U(-2, -27), p["bh"], False)
    hand = arm(L["arm-front"], U(3, -26), p["fh"], True)

    # weapon: short straight field blade, leather grip, steel guard
    bdir = rot((1, 0), p["blade"])
    nrm = (-bdir[1], bdir[0])
    g0 = add(hand, (-bdir[0] * 5, -bdir[1] * 5))
    g1 = add(hand, (bdir[0] * 3, bdir[1] * 3))
    tipb = add(hand, (bdir[0] * 30, bdir[1] * 30))
    wpn = L["weapon"]
    part(wpn, m_cap(g0, g1, 1.3), R_LEATH, band=1)
    part(wpn, m_cap(add(g1, (nrm[0] * 4, nrm[1] * 4)), add(g1, (-nrm[0] * 4, -nrm[1] * 4)), 1.2), R_METAL, band=1)
    base = add(g1, (bdir[0] * 1.5, bdir[1] * 1.5))
    part(wpn, m_poly([add(base, (nrm[0] * 2, nrm[1] * 2)), add(tipb, (nrm[0] * 0.6, nrm[1] * 0.6)), add(tipb, (bdir[0] * 3, bdir[1] * 3)),
                      add(tipb, (-nrm[0] * 1.2, -nrm[1] * 1.2)), add(base, (-nrm[0] * 2, -nrm[1] * 2))]), R_METAL, band=1)
    info["blade"] = {"grip": [round(hand[0], 2), round(hand[1], 2)], "tip": [round(tipb[0], 2), round(tipb[1], 2)], "deg": p["blade"]}

    # fx (drawn into its own layer, no outline): attack smear arc, skill/victory teal flare
    fx = L["fx"]
    if p["fx"] == "smear":
        a1 = p["blade"]
        a0 = a1 - 70
        band = np.zeros((H, W), bool)
        yy, xx = np.mgrid[0:H, 0:W]
        rr = np.hypot(xx - hand[0], yy - hand[1])
        aa = np.degrees(np.arctan2(yy - hand[1], xx - hand[0]))
        rel_a = (aa - a0) % 360
        band = (rr >= 22) & (rr <= 31) & (rel_a <= 70)
        put(fx, band, "W")
        put(fx, band & (rr <= 25), "S")
    elif p["fx"] == "flare":
        cxf, cyf = tipb
        for k in range(8):
            v = rot((1, 0), k * 45)
            r0, r1 = (4, 9) if k % 2 == 0 else (4, 6)
            put(fx, m_cap(add((cxf, cyf), (v[0] * r0, v[1] * r0)), add((cxf, cyf), (v[0] * r1, v[1] * r1)), 0.6), "S" if k % 2 else "W")
        put(fx, m_ell((cxf, cyf), 1.5, 1.5), "W")
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
    dt = (2026, 10, 21, 12, 0, 0)
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", dt), "image/openraster", zipfile.ZIP_STORED)
        st = ['<?xml version="1.0" encoding="UTF-8"?>', f'<image version="0.0.3" w="{W}" h="{H}">', "<stack>"]
        for i, n in reversed(list(enumerate(LAYERS))):
            st.append(f'<layer name="{n}" src="data/{i:02d}-{n}.png" x="0" y="0" opacity="1.0" visibility="visible" composite-op="svg:src-over"/>')
        st += ["</stack>", "</image>"]
        z.writestr(zipfile.ZipInfo("stack.xml", dt), "\n".join(st) + "\n", zipfile.ZIP_DEFLATED)
        for i, n in enumerate(LAYERS):
            z.writestr(zipfile.ZipInfo(f"data/{i:02d}-{n}.png", dt), png_bytes(L[n]), zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("mergedimage.png", dt), png_bytes(flat), zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("Thumbnails/thumbnail.png", dt), png_bytes(flat), zipfile.ZIP_DEFLATED)
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
        files[f"{pid}.png"] = (name(f"{pid}-native136", "png"), png)
        files[f"{pid}.ora"] = (name(f"{pid}-layered", "ora"), ora_bytes(L, flat))
        files[f"{pid}.pxo"] = (name(f"{pid}-editable", "pxo"), wr.make_pxo([L], [1.0], png, name(f"{pid}-pxo-export", "png"), TICK,
                                                                        order=LAYERS, dt=(2026, 10, 21, 12, 0, 0)))
    # combat static = idle-a pose, its own named package
    L0 = built["idle-a"][0]
    files["still.png"] = (name("battle-still-native136", "png"), png_bytes(flats["idle-a"]))
    files["still.ora"] = (name("battle-still-layered", "ora"), ora_bytes(L0, flats["idle-a"]))
    files["still.pxo"] = (name("battle-still-editable", "pxo"), wr.make_pxo([L0], [1.0], files["still.png"][1], name("battle-still-pxo-export", "png"),
                                                                            TICK, order=LAYERS, dt=(2026, 10, 21, 12, 0, 0)))
    rows = math.ceil(len(CELLS) / COLS)
    sheet = np.zeros((rows * H, COLS * W, 4), np.uint8)
    for i, pid in enumerate(CELLS):
        sheet[(i // COLS) * H:(i // COLS + 1) * H, (i % COLS) * W:(i % COLS + 1) * W] = flats[pid]
    files["sheet"] = (name("runtime-spritesheet", "png"), png_bytes(sheet))
    manifest = {
        "schema": "worlds-between.combat-sprite-set/1", "set_id": "protagonist-male-combat-mcombat22-v01",
        "character": {"member_id": "hero", "appearance": "male"},
        "art_status": "unapproved-male-combat-source-poses-technical-only", "art_approved": False, "motion_approved": False,
        "default_adoption": False,
        "note": "Deterministic authored source set for the male protagonist; not creator-approved art or motion, not a default, not "
                "wired. Sheet must be placed under game/ and imported before the loader can resolve it.",
        "source_provenance": name("author-manifest", "json"), "sheet": files["sheet"][0], "cell_size": [W, H], "pivot": list(PIN),
        "authored_facing": "right", "logical_scale": 0.5, "display_proportion": "0.65",
        "actions": {a: ({"loop": True, "loop_start": s["loop_start"]} if s["loop"] else {"loop": False}) | {"tick_rate": TICK, "frames": frames_json(s)}
                    for a, s in ACTIONS.items()},
    }
    files["manifest"] = (name("runtime-spritesheet-manifest", "json"), (json.dumps(manifest, indent=2) + "\n").encode())
    author = {
        "status": "UNAPPROVED male combat static + action source set; technical source only; runtime default unchanged.",
        "identityRampsFrom": "tools/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair-static-pilot-build-and-check_unapproved-v01_20261018-130225-f28bd26d.py",
        "contractFrom": rel(HERO_MANIFEST), "layers": LAYERS, "cell": [W, H], "pivot": list(PIN), "tickRate": TICK,
        "combatStatic": {"pose": "idle-a", "png": files["still.png"][0], "ora": files["still.ora"][0], "pxo": files["still.pxo"][0]},
        "runtimeActions": {a: {"frames": [[pid, t] for pid, t in s["frames"]], "loop": s["loop"], "totalTicks": sum(t for _, t in s["frames"])}
                           for a, s in ACTIONS.items()},
        "attackContactStartTick": ATTACK_CONTACT_TICK,
        "supplementalActions": {"victory": {"frames": [[pid, t] for pid, t in SUPPLEMENTAL_TIMING["victory"]["frames"]],
                                            "reason": "loader REQUIRED/OPTIONAL_ACTIONS has no victory; unknown actions reject a set"}},
        "poses": {pid: {"params": {k: (list(map(list, v)) if k == "feet" else (list(v) if isinstance(v, tuple) else v)) for k, v in P[pid].items()},
                        "rig": built[pid][1], "runtimeCell": CELLS.index(pid) if pid in CELLS else None} for pid in P},
        "source": {"file": rel(Path(__file__).resolve()), "sha256TextLf": sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n")),
                   "textHashNormalization": "sha256-text-lf-v1 (CRLF->LF)"},
        "files": {role: {"name": n, "sha256": sha(b)} for role, (n, b) in sorted(files.items())},
        "artApproved": False, "motionApproved": False, "runtimeDefaultChanged": False, "guiSaveAsVerified": False,
    }
    files["author"] = (name("author-manifest", "json"), (json.dumps(author, indent=1) + "\n").encode())
    return files, flats, built, manifest


def gates(files, flats, built, manifest):
    res = []

    def gate(k, ok, info=None):
        res.append({"key": k, "pass": bool(ok), "info": info})
    pal = set(PAL.values())
    for pid, flat in flats.items():
        op = flat[..., 3] > 0
        ys, xs = np.nonzero(op)
        cols = {tuple(c) for c in flat[op][:, :3].tolist()}
        L, info = built[pid]
        gate(f"{pid}: binary alpha + declared male palette only", set(np.unique(flat[..., 3]).tolist()) <= {0, 255} and cols <= pal, len(cols))
        gate(f"{pid}: margins clear, nothing below sole row", ys.min() >= 2 and xs.min() >= 1 and xs.max() <= W - 2 and ys.max() <= PIN[1] - 1,
             [int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())])
        if pid in AIRBORNE:
            gate(f"{pid}: airborne (lowest row 120..133)", 120 <= ys.max() <= 133, int(ys.max()))
        else:
            gate(f"{pid}: grounded (lowest row 135)", ys.max() == PIN[1] - 1, int(ys.max()))
        st = max(j["stretch"] for j in info["joints"].values())
        gate(f"{pid}: no limb stretch beyond 0.6 texel", st <= 0.6, st)
        filled = [n for n in LAYERS if (L[n][..., 3] > 0).any()]
        gate(f"{pid}: real editable layers (>= 10 non-empty role layers)", len(filled) >= 10, len(filled))
        z = zipfile.ZipFile(io.BytesIO(files[f"{pid}.ora"][1]))
        zp = zipfile.ZipFile(io.BytesIO(files[f"{pid}.pxo"][1]))
        cels = [np.frombuffer(zp.read(f"image_data/frames/1/layer_{i}"), np.uint8).reshape(H, W, 4) for i in range(1, len(LAYERS) + 1)]
        pxo_flat = blank()
        for c in cels:
            pxo_flat[c[..., 3] > 0] = c[c[..., 3] > 0]
        gate(f"{pid}: PNG == layer composite == ORA merged; ORA layers == PXO cels == source layers",
             np.array_equal(decode(files[f"{pid}.png"][1]), flat) and np.array_equal(decode(z.read("mergedimage.png")), flat)
             and np.array_equal(pxo_flat, flat)
             and all(np.array_equal(c, L[n]) and np.array_equal(decode(z.read(f"data/{i:02d}-{n}.png")), L[n]) for i, (c, n) in enumerate(zip(cels, LAYERS))))
        ident = {k: int(sum(np.all(flat[..., :3] == PAL[c], -1)[op].sum() for c in r)) for k, r in
                 (("scarf", "SsZ"), ("hair", "123"), ("bedroll", "Ttu"), ("coat", "ABC"))}
        gate(f"{pid}: male identity cues present (scarf/hair/bedroll/coat texels)", all(v >= 20 for v in ident.values()), ident)
    gate("all pose images unique", len({sha(files[f'{p}.png'][1]) for p in P}) == len(P))
    for a, s in ACTIONS.items():
        ids = [pid for pid, _ in s["frames"]]
        diffs = [int((np.any(flats[x] != flats[y], -1)).sum()) for x, y in zip(ids, ids[1:])]
        gate(f"{a}: consecutive frames visibly different (>= 60 texels)", all(d >= 60 for d in diffs), diffs)
    hero = json.loads(HERO_MANIFEST.read_text(encoding="utf-8"))
    gate("manifest top-level keys == heroine hsc19 manifest", list(manifest) == list(hero), [k for k in hero if k not in manifest])
    req = {"idle": True, "move": True, "guard": True, "attack": False, "dodge": False, "hit": False, "defeat": False}
    gate("canonical loader actions: required present with loop flags, only optional extra = skill",
         all(manifest["actions"][a]["loop"] == l for a, l in req.items()) and set(manifest["actions"]) == set(req) | {"skill"})
    gate("action key set == heroine action key set", set(manifest["actions"]) == set(hero["actions"]))
    gate("contract fields == heroine (cell, pivot, facing, scale, proportion)",
         all(manifest[k] == hero[k] for k in ("cell_size", "pivot", "authored_facing", "logical_scale", "display_proportion")))
    tot = lambda m, a: sum(f["ticks"] for f in m["actions"][a]["frames"])
    gate("one-shot action durations == heroine (attack/dodge/skill/hit/defeat ticks)",
         all(tot(manifest, a) == tot(hero, a) for a in ("attack", "dodge", "skill", "hit", "defeat")),
         {a: [tot(manifest, a), tot(hero, a)] for a in ("attack", "dodge", "skill", "hit", "defeat")})
    start = 0
    for f in ACTIONS["attack"]["frames"]:
        if f[0] == "attack-contact":
            break
        start += f[1]
    hs = 0
    for f in hero["actions"]["attack"]["frames"]:
        if f["cell"] == 5:
            break
        hs += f["ticks"]
    gate("attack contact pose starts at the heroine contact tick (4)", start == hs == ATTACK_CONTACT_TICK, [start, hs])
    gate("attack has anticipation (lean back, blade behind) -> contact (lunge) -> recovery",
         P["attack-windup"]["lean"] < 0 and P["attack-windup"]["blade"] < -90 and P["attack-contact"]["pel"][0] >= 8
         and 0 < P["attack-recover"]["lean"] < P["attack-contact"]["lean"])
    gate("defeat ends kneeling with eyes shut; victory poses distinct from idle",
         P["defeat-down"]["eyes"] == "shut" and KNEELING["defeat-down"] == "both"
         and all(int(np.any(flats[v] != flats["idle-a"], -1).sum()) >= 150 for v in SUPPLEMENTAL))
    sheet = decode(files["sheet"][1])
    gate("sheet is a cell multiple, 6 columns, each cell == its pose PNG",
         sheet.shape[1] == COLS * W and sheet.shape[0] % H == 0 and
         all(np.array_equal(sheet[(i // COLS) * H:(i // COLS + 1) * H, (i % COLS) * W:(i % COLS + 1) * W], flats[pid]) for i, pid in enumerate(CELLS)))
    hs_img = np.array(Image.open(HERO_SHEET).convert("RGBA"))
    ho = hs_img[0:H, 0:W, 3] > 0
    mo = flats["idle-a"][..., 3] > 0
    iou = float((ho & mo).sum() / (ho | mo).sum())
    gate("idle silhouette distinct from heroine idle (IoU < 0.8, not a recolour)", iou < 0.8, round(iou, 3))
    gate("still package pixels == idle-a", files["still.png"][1] == files["idle-a.png"][1])
    gate("all asset names <= 140 chars and in project/subject/purpose/variant/timestamp-id form",
         all(len(n) <= 140 and n.startswith(f"{SLUG}_{SUBJECT}_") and f"_{VER}_{STAMP}-" in n for n, _ in files.values()))
    return res


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    files, flats, built, manifest = outputs()
    det = all(files[k][1] == b for k, (n, b) in outputs()[0].items())
    res = [{"key": "deterministic rebuild", "pass": det, "info": None}] + gates(files, flats, built, manifest)
    if mode == "build":
        os.makedirs(long(OUT), exist_ok=True)
        for role, (n, b) in files.items():
            p = long(OUT / n)
            if p.exists():
                assert p.read_bytes() == b, f"refusing to overwrite a different file: {n}"
            else:
                p.write_bytes(b)
        lst = {"schema": "mcombat22-file-list/1", "files": [{"role": r, "path": rel(OUT / n), "sha256": sha(b)} for r, (n, b) in sorted(files.items())]}
        lp = long(OUT / name("file-list", "json"))
        data = (json.dumps(lst, indent=1) + "\n").encode()
        if not lp.exists() or lp.read_bytes() != data:
            lp.write_bytes(data)
    else:
        for role, (n, b) in files.items():
            p = long(OUT / n)
            res.append({"key": f"on-disk bytes equal rebuild: {role}", "pass": p.exists() and p.read_bytes() == b, "info": None})
    fails = [r for r in res if not r["pass"]]
    for r in fails:
        print("FAIL", r["key"], r["info"])
    print("MCOMBAT22", mode.upper(), "PASS" if not fails else "FAIL", f"{len(res) - len(fails)}/{len(res)}")
    if mode == "check":
        with open(long(OUT / name("source-check-report", "json")), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"mode": "check", "gates": res, "passed": len(res) - len(fails), "total": len(res)}, indent=1) + "\n")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
