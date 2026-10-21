"""Male protagonist four-direction EXPLORATION SOURCE author (mexplore23, UNAPPROVED technical source).

Builds statics, idle loops, 12-phase walk cycles and phase-aware stop bridges for south/west/north/east at
the male v8pair contract (80x112 cell, pivot 40/104, 96-texel body, display scale 0.5).

- south: the existing male v8pair role layers (ORA) are the exact neutral; idle/walk/stop are role-layer
  offsets and per-leg column splits of those exact texels (no repaint).
- north: back view built from the male south role silhouettes mirrored about the pivot column and refilled
  as back surfaces (hair mass, coat back with vent) plus an authored large pack and bedroll.
- west: authored side puppet (IK two-bone legs, swinging arms, pack + bedroll spiral, scarf tail).
- east: west role layers mirrored with x' = 80 - x (pivot column preserved); lighting becomes upper-right.

Usage:  python -X utf8 -I <tool> build|check [--pixelorama EXE]
Writes only NEW files under outputs/mexplore23 and game/data/mexplore23.
"""
import argparse, hashlib, io, json, math, os, shutil, subprocess, sys, tempfile, zipfile
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SRC_DIR = "game/assets/characters/protagonist-male-v8pair"
SRC_ORA = SRC_DIR + "/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair-layers_unapproved-v01_20261018-130225-587897cb.ora"
SRC_PNG = SRC_DIR + "/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair_unapproved-v01_20261018-130225-79ed5d37.png"
SRC_PNG_SHA = "e4b2db368f65e158724dff4c8844fe2dcabf9f9b7f7a9aa3807d76bd72409af2"
SRC_ORA_SHA = "bba61903b962cb38a2ccd24bc203a4ed1ca778bf2e9c680a35398350bbf0b9f3"
STAMP = "20261021-162551"
RUN = "6e3b1a7d"
OUT_REL = "outputs/mexplore23"
PKG_REL = "game/data/mexplore23"
PFX = "rpg-2-star-ocean-the-second_protagonist-male_explore"
VAR = "unapproved-mexplore23-v01"
W, H, PIN = 80, 112, (40, 104)
SOLE = 103
ZIP_DT = (2026, 10, 21, 16, 25, 50)
PIXELORAMA_VERSION = "v1.2.3-stable"
DIRS = ("south", "west", "north", "east")
NPH = 12
D_PHASE = 4            # declared logical movement per walk phase, SOURCE texels (= 2 logical px)
STEP = 24              # side stance travel per step, source texels (6 phases x 4)
FRAME_MS = 40
STOP_K = (0.0, 1 / 3, 2 / 3, 1.0)

PAL = {"K": "#0c0a0c", "1": "#735442", "2": "#4b362b", "3": "#30231d", "4": "#1f1614",
       "F": "#f0c090", "f": "#d49868", "e": "#a86a48", "D": "#7a4234", "y": "#2a1a16",
       "S": "#82c8b8", "s": "#46988c", "Z": "#2a6660", "T": "#5e9c9c", "t": "#3c7678", "u": "#28505a",
       "A": "#8c7664", "B": "#6a5b4e", "C": "#4a3e36", "c": "#2b2422", "L": "#b27c4e", "l": "#80523a",
       "m": "#4e3224", "W": "#efe6d2", "w": "#c9bea6", "v": "#978a76", "P": "#7e7a62", "p": "#5c5a4a",
       "o": "#3c3b30", "O": "#8c5a3a", "b": "#623d2a", "q": "#3a2520", "M": "#dcdad2", "X": "#8e8c88"}
RGB = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in PAL.items()}


def _fs(p):
    p = os.path.abspath(p)
    return "\\\\?\\" + p if os.name == "nt" and not p.startswith("\\\\?\\") else p


def rp(rel):
    return os.path.join(ROOT, rel.replace("/", os.sep))


def rb(p):
    with open(_fs(p), "rb") as f:
        return f.read()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_text(b):
    return sha(b.replace(b"\r\n", b"\n"))


def png_bytes(a):
    buf = io.BytesIO()
    Image.fromarray(a, "RGBA").save(buf, "PNG", optimize=False, compress_level=9)
    return buf.getvalue()


def decode(b):
    return np.array(Image.open(io.BytesIO(b)).convert("RGBA"))


def blank():
    return np.zeros((H, W, 4), np.uint8)


# ----------------------------------------------------------------------------- raster primitives
class Canvas:
    def __init__(self):
        self.a = blank()

    def px(self, x, y, k):
        x, y = int(x), int(y)
        if 0 <= x < W and 0 <= y < H:
            self.a[y, x, :3] = RGB[k]
            self.a[y, x, 3] = 255

    def poly(self, pts, k):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        for y in range(int(math.floor(min(ys))), int(math.ceil(max(ys))) + 1):
            yc = y + 0.5
            hits = []
            for i in range(len(pts)):
                (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
                if (y1 <= yc < y2) or (y2 <= yc < y1):
                    hits.append(x1 + (yc - y1) * (x2 - x1) / (y2 - y1))
            hits.sort()
            for j in range(0, len(hits) - 1, 2):
                for x in range(int(math.ceil(hits[j] - 0.5)), int(math.floor(hits[j + 1] - 0.5)) + 1):
                    self.px(x, y, k)

    def ell(self, cx, cy, rx, ry, k):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                    self.px(x, y, k)

    def seg(self, x1, y1, x2, y2, wdt, k):
        """Thick segment as a quad + round caps."""
        dx, dy = x2 - x1, y2 - y1
        n = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / n * wdt / 2, dx / n * wdt / 2
        self.poly([(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)], k)
        self.ell(x1, y1, wdt / 2, wdt / 2, k)
        self.ell(x2, y2, wdt / 2, wdt / 2, k)

    def outline(self):
        m = self.a[..., 3] == 255
        o = np.zeros_like(m)
        o[1:] |= m[:-1]; o[:-1] |= m[1:]; o[:, 1:] |= m[:, :-1]; o[:, :-1] |= m[:, 1:]
        o &= ~m
        self.a[o, :3] = RGB["K"]; self.a[o, 3] = 255
        return self


def shade_mask(mask, base, lit, dark, rim=None, litfrac=0.3, darkfrac=0.25):
    """Fill a boolean mask with an upper-left lit ramp (column bands inside the mask's span per row)."""
    c = Canvas()
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return c
    top = ys.min()
    for y in range(H):
        row = np.nonzero(mask[y])[0]
        if not len(row):
            continue
        x0, x1 = row.min(), row.max()
        span = x1 - x0 + 1
        for x in row:
            f = (x - x0) / max(span - 1, 1)
            k = lit if f < litfrac else (dark if f > 1 - darkfrac else base)
            if y - top < 2 and rim:
                k = rim
            c.px(x, y, k)
    return c


def shift(a, dx, dy):
    o = blank()
    ys, xs = np.nonzero(a[..., 3])
    nx, ny = xs + dx, ys + dy
    ok = (nx >= 0) & (nx < W) & (ny >= 0) & (ny < H)
    o[ny[ok], nx[ok]] = a[ys[ok], xs[ok]]
    return o


def mirror(a):
    """x' = 80 - x : keeps pivot column 40 fixed; column 0 must be empty."""
    assert not a[:, 0, 3].any(), "column 0 occupied; mirror would drop texels"
    o = blank()
    o[:, 1:] = a[:, 1:][:, ::-1]
    return o


def over(layers):
    comp = blank()
    for a in layers:
        m = a[..., 3] == 255
        comp[m] = a[m]
    return comp


# ----------------------------------------------------------------------------- source layers (exact)
SOUTH_LAYERS = ["bedroll", "pack", "coat-skirt", "sash", "legs", "boots", "torso-coat", "harness",
                "arm-hanging", "arm-grip", "head-face", "hair", "scarf"]


def load_src():
    ora = rb(rp(SRC_ORA)); png = rb(rp(SRC_PNG))
    assert sha(png) == SRC_PNG_SHA and sha(ora) == SRC_ORA_SHA, "male v8pair source hash drift"
    with zipfile.ZipFile(io.BytesIO(ora)) as z:
        lay = {n: decode(z.read(f"data/{n}.png")) for n in SOUTH_LAYERS}
    assert np.array_equal(over([lay[n] for n in SOUTH_LAYERS]), decode(png)), "ORA layers != source PNG"
    return lay, decode(png)


# ----------------------------------------------------------------------------- pose models
def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)


def side_walk_pose(p):
    """West-facing (forward = -x). Foot A planted phases 0..5, foot B planted 6..11.
    Planted ankle x = 40 - 12 + 4*k (k = phase within stance) -> sprite moves +4/phase = world-fixed."""
    def foot(ph):
        if ph < 6:   # stance
            return (40 - STEP / 2 + D_PHASE * ph, 0.0, True)
        t = (ph - 6 + 1) / 7.0   # swing 6 phases, from back (+12) to front (-12)
        return (40 + STEP / 2 + D_PHASE - (STEP + D_PHASE) * ease(t), 6.0 * math.sin(math.pi * t), False)
    ax, al, ap = foot(p)
    bx, bl, bp = foot((p + 6) % NPH)
    bob = -1 if p % 6 in (2, 3, 4) else 0
    ang = 0.55 * math.cos(2 * math.pi * p / NPH)   # near arm swings opposite the near (A) leg
    return {"ax": ax, "al": al, "bx": bx, "bl": bl, "bob": bob, "head": bob, "arm_n": ang, "arm_f": -ang,
            "skirt": round(1.5 * math.cos(2 * math.pi * p / NPH)), "flap": p % 4 // 2, "planted": "A" if ap else "B"}


SIDE_IDLE = [  # 4-frame breathing loop; f0 = neutral
    {"bob": 0, "head": 0, "flap": 0}, {"bob": 1, "head": 1, "flap": 0},
    {"bob": 1, "head": 1, "flap": 1}, {"bob": 1, "head": 1, "flap": 1}]
IDLE_MS = [700, 200, 400, 200]
SIDE_NEUTRAL = {"ax": 39.0, "al": 0.0, "bx": 43.0, "bl": 0.0, "bob": 0, "head": 0, "arm_n": 0.1, "arm_f": -0.1,
                "skirt": 0, "flap": 0}


def fb_walk_pose(p):
    """Front/back in-place cycle: leg L lifted phases 1..5, leg R lifted 7..11, both down at 0 and 6."""
    def lift(ph):
        return round(4 * math.sin(math.pi * ph / 6)) if 0 < ph < 6 else 0
    l, r = lift(p), lift((p + 6) % NPH)
    bob = 0 if p % 6 in (2, 3, 4) else 1      # settle DOWN at contact (never up: an upward torso shift opens a waist gap)
    sw = round(2 * math.sin(2 * math.pi * p / NPH))
    return {"ll": l, "rl": r, "bob": bob, "head": bob, "arm_l": -sw, "arm_r": sw,
            "skirt": round(math.sin(2 * math.pi * p / NPH)), "pack": (-1 if p % 6 in (3, 4, 5) else 0),
            "planted": "R" if l and not r else ("L" if r and not l else "both")}


FB_NEUTRAL = {"ll": 0, "rl": 0, "bob": 0, "head": 0, "arm_l": 0, "arm_r": 0, "skirt": 0, "pack": 0}
FB_IDLE = [{"bob": 0, "head": 0, "pack": 0}, {"bob": 1, "head": 1, "pack": 0},
           {"bob": 1, "head": 1, "pack": 1}, {"bob": 1, "head": 1, "pack": 1}]


def lerp_pose(a, b, k):
    o = {}
    for key, va in a.items():
        if key == "planted":
            continue
        vb = b.get(key, va)
        v = va + (vb - va) * k
        o[key] = round(v) if isinstance(va, int) and isinstance(vb, int) else v
    return o


# ----------------------------------------------------------------------------- south renderer (exact layers)
LIFT_ROW = 70   # front/back step: only the shin + boot (rows >= 70) of a column-split leg rises; thigh stays


def lift_legs(a, pose):
    parts = []
    for sl, key in ((slice(0, 40), "ll"), (slice(40, W), "rl")):
        leg = blank(); leg[:, sl] = a[:, sl]
        upper = leg.copy(); upper[LIFT_ROW:] = 0
        lower = leg.copy(); lower[:LIFT_ROW] = 0
        parts += [upper, shift(lower, 0, -pose.get(key, 0))]
    return over(parts)


def render_south(src, pose):
    L = {}
    up = pose.get("bob", 0)
    hd = pose.get("head", 0)
    for n in SOUTH_LAYERS:
        a = src[n]
        if n in ("legs", "boots"):
            a = lift_legs(a, pose)
        elif n == "coat-skirt":
            a = shift(a, pose.get("skirt", 0), 0)
        elif n in ("head-face", "hair"):
            a = shift(a, 0, hd)
        elif n == "arm-hanging":
            a = shift(a, 0, up + pose.get("arm_r", 0))
        elif n in ("pack", "bedroll"):
            a = shift(a, 0, up + pose.get("pack", 0))
        elif n in ("torso-coat", "harness", "scarf", "arm-grip", "sash"):
            a = shift(a, 0, up if n != "sash" else 0)
        L[n] = a
    return [(n, L[n]) for n in SOUTH_LAYERS]


# ----------------------------------------------------------------------------- north renderer (back view)
NORTH_LAYERS = ["coat-skirt", "legs", "boots", "arm-left", "arm-right", "torso-coat", "head-back", "hair",
                "scarf", "pack", "bedroll"]


def north_base(src):
    m = lambda n: mirror(src[n])[..., 3] == 255
    base = {}
    sk = m("coat-skirt") | m("sash")
    sk &= ~m("torso-coat")
    c = shade_mask(sk, "B", "A", "C")
    for y in range(60, 84):                       # centre vent + hem leather
        if sk[y, 40]:
            c.px(40, y, "c")
    for x in range(W):
        col = np.nonzero(sk[:, x])[0]
        if len(col):
            c.px(x, col.max(), "m")
    base["coat-skirt"] = c.outline().a
    for n in ("legs", "boots"):
        mm = m(n)
        if n == "legs":
            c = shade_mask(mm, "p", "P", "o")
            c.a[mm & (np.arange(H)[:, None] >= 76) & (np.arange(H)[:, None] <= 77)] = (*RGB["o"], 255)  # knee crease
        else:
            c = shade_mask(mm, "b", "O", "q", rim="O")
            for x in range(W):
                col = np.nonzero(mm[:, x])[0]
                if len(col):
                    c.px(x, col.max(), "q")             # heel/sole band seen from behind
                    c.px(x, col.max() - 1, "m")
        base[n] = c.outline().a
    arm = m("arm-hanging") | m("arm-grip")
    lmask = arm.copy(); lmask[:, 40:] = False
    rmask = arm.copy(); rmask[:, :40] = False
    for name, mm in (("arm-left", lmask), ("arm-right", rmask)):
        c = shade_mask(mm, "B", "A", "C")
        ys = np.nonzero(mm.any(1))[0]
        if len(ys):
            for y in range(ys.max() - 3, ys.max() + 1):
                for x in np.nonzero(mm[y])[0]:
                    c.px(x, y, "b" if y > ys.max() - 2 else "w")   # cream cuff then glove
        base[name] = c.outline().a
    tm = m("torso-coat") | m("harness")
    c = shade_mask(tm, "B", "A", "C", rim="A")
    for y in range(52, 56):
        for x in np.nonzero(tm[y])[0]:
            if y in (53, 54):
                c.px(x, y, "l")                       # belt across the back
    base["torso-coat"] = c.outline().a
    hm = m("head-face")
    c = Canvas()
    for y, x in zip(*np.nonzero(hm)):
        c.px(x, y, "e" if y > 28 else "f")            # nape / ears
    base["head-back"] = c.outline().a
    hr = m("hair") | (hm & (np.arange(H)[:, None] <= 29))
    c = shade_mask(hr, "2", "1", "3", litfrac=0.25)
    ys, xs = np.nonzero(hr)
    for y, x in zip(ys, xs):                          # tousled strand marks, deterministic
        if (x * 7 + y * 3) % 11 == 0 and y < 27:
            c.px(x, y, "3")
        if (x * 5 + y * 13) % 17 == 0 and y < 20:
            c.px(x, y, "1")
    base["hair"] = c.outline().a
    c = Canvas()
    c.poly([(33, 29), (47, 29), (48, 33), (32, 33)], "s")
    for x in range(33, 47):
        c.px(x, 29, "S")
    c.poly([(42, 33), (46, 33), (45, 40), (42, 38)], "Z")   # knot tail down the back
    base["scarf"] = c.outline().a
    c = Canvas()                                      # big pack centred on the back
    c.poly([(30, 36), (50, 36), (51, 60), (29, 60)], "l")
    c.poly([(30, 36), (34, 36), (33, 60), (29, 60)], "L")
    c.poly([(47, 36), (50, 36), (51, 60), (48, 60)], "m")
    c.poly([(31, 36), (49, 36), (49, 43), (31, 43)], "L")   # flap
    for x in range(31, 50):
        c.px(x, 43, "m")
    for y in (47, 48):
        for x in range(32, 49):
            c.px(x, y, "m")                           # lower strap
    c.px(36, 47, "M"); c.px(44, 47, "M"); c.px(40, 43, "M"); c.px(40, 44, "X")
    base["pack"] = c.outline().a
    c = Canvas()                                      # bedroll across the top, spiral ends both sides
    c.poly([(27, 27), (53, 27), (53, 36), (27, 36)], "t")
    for x in range(27, 54):
        c.px(x, 28, "T"); c.px(x, 29, "T"); c.px(x, 35, "u")
    for cx in (27, 53):
        c.ell(cx, 31.5, 3.2, 4.6, "T")
        c.px(cx, 31, "u"); c.px(cx + 1, 32, "u"); c.px(cx - 1, 30, "t")
    for x in (34, 46):
        for y in range(27, 37):
            c.px(x, y, "m")                           # straps
    base["bedroll"] = c.outline().a
    return base


def render_north(base, pose):
    up, hd = pose.get("bob", 0), pose.get("head", 0)
    out = []
    for n in NORTH_LAYERS:
        a = base[n]
        if n in ("legs", "boots"):
            a = lift_legs(a, pose)
        elif n == "coat-skirt":
            a = shift(a, pose.get("skirt", 0), 0)
        elif n in ("head-back", "hair", "scarf"):
            a = shift(a, 0, hd)
        elif n == "arm-left":
            a = shift(a, 0, up + pose.get("arm_l", 0))
        elif n == "arm-right":
            a = shift(a, 0, up + pose.get("arm_r", 0))
        elif n in ("pack", "bedroll"):
            a = shift(a, 0, up + pose.get("pack", 0))
        elif n == "torso-coat":
            a = shift(a, 0, up)
        out.append((n, a))
    return [(n, np.concatenate((a[:PIN[1]], np.zeros_like(a[PIN[1]:])), axis=0)) for n, a in out]  # Clip added back-view outline to unchanged sole line.


# ----------------------------------------------------------------------------- west puppet
WEST_LAYERS = ["arm-far", "leg-far", "coat-skirt-back", "leg-near", "pack", "torso-coat", "coat-skirt-front",
               "bedroll", "scarf", "head-face", "hair", "arm-near"]
L1 = L2 = 20.0
ANKLE_UP = 5     # ankle sits 5 texels above the sole row


def ik(hx, hy, ax, ay):
    dx, dy = ax - hx, ay - hy
    d = min(math.hypot(dx, dy), L1 + L2 - 1e-6)
    a = math.atan2(dy, dx)
    b = math.acos((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))
    ka = a + b                      # knee bends forward (-x) for a west-facing figure
    return hx + L1 * math.cos(ka), hy + L1 * math.sin(ka)


def draw_leg(ax_, lift, hip, near):
    c = Canvas()
    hx, hy = hip
    ay = SOLE - 1 - ANKLE_UP - lift          # fill sole on row 102; outline lands on the contract sole row 103
    kx, ky = ik(hx, hy, ax_, ay)
    tr, trs = ("P", "p") if near else ("p", "o")
    c.seg(hx, hy, kx, ky, 7, tr)
    c.seg(kx, ky, ax_, ay, 6, trs if not near else tr)
    if near:                                       # knee pad / front-lit stripe
        c.ell(kx - 1, ky, 2, 2, "p")
    # boot shaft from ankle up 11 texels along the shin + cuff
    t = 11 / max(math.hypot(kx - ax_, ky - ay), 1)
    bx, by = ax_ + (kx - ax_) * t, ay + (ky - ay) * t
    bo, bs = ("O", "b") if near else ("b", "q")
    c.seg(bx, by, ax_, ay, 7, bs)
    c.seg(bx, by, ax_, ay, 5, bo)
    c.seg(bx - 0.5, by, bx + 0.5, by, 8, "b" if near else "q")   # cuff
    # foot: heel behind (+x), toe forward (-x), sole on row ay+5
    sole = ay + ANKLE_UP
    c.poly([(ax_ + 4, ay - 1), (ax_ - 3, ay - 1), (ax_ - 7, sole - 2), (ax_ - 7, sole + 0.99), (ax_ + 4, sole + 0.99)], bo)
    for x in range(int(ax_ - 7), int(ax_ + 4) + 1):
        c.px(x, sole, "q")
    if near:
        c.px(ax_ - 4, sole - 2, "L")
    return c.outline().a, (kx, ky)


def draw_arm(sh, ang, near):
    c = Canvas()
    sx, sy = sh
    ex, ey = sx + 11 * math.sin(-ang) , sy + 11 * math.cos(ang)
    fa = ang - 0.35 if ang < 0 else ang - 0.15      # slight elbow flex, more on the back swing
    hx, hy = ex + 10 * math.sin(-fa), ey + 10 * math.cos(fa)
    sl, sd = ("B", "C") if near else ("C", "c")
    c.seg(sx, sy, ex, ey, 6, sd)
    c.seg(sx, sy, ex, ey, 4, sl)
    c.seg(ex, ey, hx, hy, 5, sl)
    mx, my = ex + (hx - ex) * 0.55, ey + (hy - ey) * 0.55
    c.seg(mx, my, mx + (hx - ex) * 0.15, my + (hy - ey) * 0.15, 5, "w" if near else "v")   # rolled cream cuff
    c.ell(hx, hy + 1, 2.4, 2.4, "b" if near else "q")                                     # fingerless glove
    if near:
        c.px(hx - 1, hy + 2, "f")
    return c.outline().a


def render_west(pose):
    bob, hd = pose.get("bob", 0), pose.get("head", 0)
    hd += 3  # Existing48logical source contract: neutral hair begins atrow8, walk atrow7minimum.
    hip = (40.5, 61 + bob)
    out = {}
    out["leg-near"], _ = draw_leg(pose["ax"], pose["al"], hip, True)
    out["leg-far"], _ = draw_leg(pose["bx"] + 1, pose["bl"], (hip[0] + 1, hip[1]), False)
    sh = (40.5, 38 + bob)
    out["arm-near"] = draw_arm(sh, pose["arm_n"], True)
    out["arm-far"] = draw_arm((sh[0] + 2, sh[1]), pose["arm_f"], False)
    sw = pose.get("skirt", 0)
    c = Canvas()                                   # coat back panel flaring behind
    c.poly([(40, 55 + bob), (48, 55 + bob), (53 - sw, 80), (41, 81)], "C")
    c.poly([(47, 56 + bob), (48, 56 + bob), (53 - sw, 80), (51 - sw, 80)], "c")
    for x in range(41, 54 - sw):
        c.px(x, 81 if x < 47 else 80, "m")
    out["coat-skirt-back"] = c.outline().a
    c = Canvas()                                   # front coat panel (open, swings with the stride)
    c.poly([(34, 55 + bob), (40, 55 + bob), (40, 79), (31 - sw, 78)], "B")
    c.poly([(34, 55 + bob), (35.5, 55 + bob), (32.5 - sw, 78), (31 - sw, 78)], "A")
    for x in range(int(31 - sw), 41):
        c.px(x, 78, "m")
    out["coat-skirt-front"] = c.outline().a
    c = Canvas()                                   # torso: open coat, cream shirt front, belt
    c.poly([(35, 34 + bob), (46, 34 + bob), (48, 41 + bob), (47, 57 + bob), (34, 57 + bob), (33, 41 + bob)], "B")
    c.poly([(35, 34 + bob), (38, 34 + bob), (37, 57 + bob), (34, 57 + bob), (33, 41 + bob)], "A")
    c.poly([(45, 35 + bob), (46, 34 + bob), (48, 41 + bob), (47, 57 + bob), (45, 57 + bob)], "C")
    c.poly([(33, 38 + bob), (35, 38 + bob), (35, 54 + bob), (33, 54 + bob)], "W")
    for y in range(40, 54, 3):
        c.px(34, y + bob, "w")
    for x in range(33, 48):
        c.px(x, 54 + bob, "l"); c.px(x, 55 + bob, "m")
    c.px(34, 54 + bob, "M"); c.px(34, 55 + bob, "X")
    c.poly([(41, 35 + bob), (43, 35 + bob), (44, 54 + bob), (42, 54 + bob)], "m")   # pack strap
    out["torso-coat"] = c.outline().a
    c = Canvas()                                   # leather pack on the back (+x)
    c.poly([(46, 37 + bob), (55, 38 + bob), (56, 57 + bob), (46, 57 + bob)], "l")
    c.poly([(46, 37 + bob), (55, 38 + bob), (55, 41 + bob), (46, 41 + bob)], "L")
    c.poly([(53, 41 + bob), (55, 41 + bob), (56, 57 + bob), (54, 57 + bob)], "m")
    for y in (47, 48):
        for x in range(47, 56):
            c.px(x, y + bob, "m")
    c.px(51, 47 + bob, "M")
    out["pack"] = c.outline().a
    c = Canvas()                                   # bedroll seen end-on: teal spiral disc on the pack top
    c.ell(51, 32 + bob, 5.6, 5.0, "t")
    c.ell(50.5, 31.4 + bob, 4.2, 3.6, "T")
    for (x, y, k) in ((51, 32, "u"), (52, 32, "u"), (52, 31, "u"), (51, 30, "u"), (50, 30, "u"), (49, 31, "u"),
                      (49, 32, "u"), (49, 33, "t"), (50, 34, "u"), (51, 34, "u"), (52, 34, "u"), (53, 33, "u")):
        c.px(x, y + bob, k)
    for y in range(27, 38):
        c.px(47, y + bob, "m")
    out["bedroll"] = c.outline().a
    c = Canvas()                                   # scarf wrap + trailing tail (flaps)
    fl = pose.get("flap", 0)
    c.poly([(34, 31 + hd), (44, 31 + hd), (45, 36 + bob), (35, 37 + bob)], "s")
    c.poly([(34, 31 + hd), (38, 31 + hd), (37, 37 + bob), (35, 37 + bob)], "S")
    c.poly([(43, 33 + bob), (46, 33 + bob), (51, 39 + bob - fl), (48, 41 + bob + fl)], "Z")
    c.poly([(44, 33 + bob), (45, 33 + bob), (49, 38 + bob - fl), (48, 39 + bob)], "s")
    out["scarf"] = c.outline().a
    c = Canvas()                                   # face profile facing -x
    c.poly([(34, 14 + hd), (41, 14 + hd), (42, 30 + hd), (37, 32 + hd), (34, 30 + hd), (33, 27 + hd),
            (32, 25 + hd), (30.5, 23 + hd), (32, 21 + hd), (33, 17 + hd)], "F")
    c.poly([(39, 14 + hd), (42, 14 + hd), (42, 30 + hd), (39, 31 + hd)], "f")
    c.poly([(34, 28 + hd), (37, 28 + hd), (37, 32 + hd), (35, 31 + hd)], "f")
    c.px(33, 21 + hd, "y"); c.px(34, 21 + hd, "y"); c.px(34, 22 + hd, "y")
    c.px(31, 23 + hd, "e"); c.px(34, 27 + hd, "D"); c.px(35, 27 + hd, "e")
    c.ell(41.5, 23.5 + hd, 1.6, 2.4, "f"); c.px(41, 24 + hd, "D")
    out["head-face"] = c.outline().a
    c = Canvas()                                   # tousled outward hair, wider than the face
    c.ell(42, 18 + hd, 11.5, 9.5, "2")
    c.ell(40.5, 15.5 + hd, 8.5, 6.0, "1")
    for (x1, y1, x2, y2) in ((50, 12, 54, 10), (52, 18, 55, 19), (50, 24, 53, 26), (45, 9, 46, 7), (37, 10, 35, 8),
                             (32, 13, 30, 12), (47, 27, 48, 29)):
        c.seg(x1, y1 + hd, x2, y2 + hd, 2.6, "2")
    c.poly([(29, 15 + hd), (36, 13 + hd), (37, 19 + hd), (33, 18 + hd), (31, 19 + hd)], "2")   # fringe
    c.poly([(42, 21 + hd), (51, 21 + hd), (49, 29 + hd), (43, 28 + hd)], "3")                  # back/nape mass
    for (x, y, k) in ((38, 11, "1"), (42, 10, "1"), (36, 13, "1"), (46, 14, "3"), (48, 17, "3"), (44, 16, "3"),
                      (33, 16, "3"), (50, 22, "4"), (47, 25, "4"), (35, 17, "1")):
        c.px(x, y + hd, k)
    m = c.a[..., 3] == 255                        # keep the face visible: hair stays above the brow/back
    face = out["head-face"][..., 3] == 255
    yy = np.arange(H)[:, None]; xx = np.arange(W)[None, :]
    cut = face & (yy >= 19 + hd) & (xx <= 40)
    c.a[cut] = 0
    c.outline()
    fo = out["head-face"]
    c.a[cut & (c.a[..., 3] == 255)] = fo[cut & (c.a[..., 3] == 255)]
    out["hair"] = c.a
    return [(n, out[n]) for n in WEST_LAYERS]


def render_east(pose):
    return [(n, mirror(a)) for n, a in render_west(pose)]


# ----------------------------------------------------------------------------- frame set
def frame_set(src, nbase):
    """Returns {dir: {"idle":[(layers,pose)], "walk":[...], "stop":{p:[...]}}} plus pose tables."""
    out = {}
    for d in DIRS:
        side = d in ("west", "east")
        neutral = SIDE_NEUTRAL if side else FB_NEUTRAL
        walkp = [side_walk_pose(p) if side else fb_walk_pose(p) for p in range(NPH)]
        idlep = [dict(neutral, **i) for i in (SIDE_IDLE if side else FB_IDLE)]
        rend = {"south": lambda q: render_south(src, q), "north": lambda q: render_north(nbase, q),
                "west": render_west, "east": render_east}[d]
        idle = [(rend(q), q) for q in idlep]
        walk = [(rend(q), q) for q in walkp]
        stop = {}
        for p in range(NPH):
            seq = []
            for k in STOP_K:
                if k == 0.0:
                    seq.append(walk[p])
                elif k == 1.0:
                    seq.append(idle[0])
                else:
                    q = lerp_pose(walkp[p], neutral, k)
                    seq.append((rend(q), q))
            stop[p] = seq
        out[d] = {"idle": idle, "walk": walk, "stop": stop, "walk_poses": walkp, "idle_poses": idlep}
    return out


# ----------------------------------------------------------------------------- measurements
def sole_points(layers, d):
    """Grounded-foot coordinates measured from the rendered boot/leg layers (source texels)."""
    res = {}
    if d in ("west", "east"):
        for n in ("leg-near", "leg-far"):
            a = dict(layers)[n]
            al = a[..., 3] == 255
            rows = np.nonzero(al.any(1))[0]
            bottom = int(rows.max())
            xs = np.nonzero(al[bottom])[0]
            res[n] = {"sole_row": bottom, "toe_x": int(xs.min()) if d == "west" else int(xs.max()),
                      "heel_x": int(xs.max()) if d == "west" else int(xs.min()), "grounded": bottom == SOLE + 1 or bottom == SOLE}
    else:
        name = "boots"
        a = dict(layers)[name]
        for side, sl in (("L", slice(0, 40)), ("R", slice(40, W))):
            al = a[..., 3] == 255
            al2 = np.zeros_like(al); al2[:, sl] = al[:, sl]
            rows = np.nonzero(al2.any(1))[0]
            bottom = int(rows.max())
            xs = np.nonzero(al2[bottom])[0]
            res[side] = {"sole_row": bottom, "x_min": int(xs.min()), "x_max": int(xs.max()),
                         "grounded": bottom >= SOLE}
    return res


# ----------------------------------------------------------------------------- native writers
def make_pxo(layer_names, frames, preview_png, fps_ms):
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": n == "guides", "metadata": {}, "name": n,
                   "new_cels_linked": False, "opacity": 1.0, "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": n != "guides"} for n in layer_names]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0}
                             for _ in layer_names], "duration": float(ms) / FRAME_MS, "metadata": {}}
                   for (_, ms) in frames]
    data = {"author_company": "", "author_contact": "", "author_display_name": "", "author_real_name": "",
            "brushes": [], "color_mode": 5, "current_frame": 0, "current_layer": 0, "export_profile": {},
            "fps": 1000.0 / FRAME_MS, "frames": frames_json, "guides": [], "layers": layer_json, "license": "",
            "metadata": {}, "next_keyframe_id": 0, "palettes": [], "pixelorama_version": PIXELORAMA_VERSION,
            "project_current_palette_name": "", "pxo_version": 7, "reference_images": [], "size_x": W, "size_y": H,
            "symmetry_points": [W - 1.0, H - 1.0], "tags": fps_ms, "tile_mode_x_basis_x": W, "tile_mode_x_basis_y": 0,
            "tile_mode_y_basis_x": 0, "tile_mode_y_basis_y": H, "tilesets": [], "user_data": "", "vanishing_points": []}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        def put(name, payload):
            z.writestr(zipfile.ZipInfo(name, ZIP_DT), payload, zipfile.ZIP_DEFLATED)
        put("data.json", json.dumps(data, separators=(",", ":")))
        put("mimetype", "application/x-pixelorama")
        put("preview.png", preview_png)
        for fi, (layers, _) in enumerate(frames, start=1):
            put(f"image_data/frames/{fi}/", b"")
            for li, (_, a) in enumerate(layers, start=1):
                put(f"image_data/frames/{fi}/layer_{li}", a.tobytes())
                put(f"image_data/frames/{fi}/indices_layer_{li}", b"\x00")
    return buf.getvalue()


def make_ora(layers, png):
    stack = ['<?xml version="1.0" encoding="UTF-8"?>', f'<image version="0.0.3" w="{W}" h="{H}" xres="72" yres="72">', "<stack>"]
    for name, _ in reversed(layers):
        vis = "hidden" if name == "guides" else "visible"
        stack.append(f'<layer name="{name}" src="data/{name}.png" x="0" y="0" opacity="1.0" visibility="{vis}" composite-op="svg:src-over"/>')
    stack += ["</stack>", "</image>"]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", ZIP_DT), "image/openraster", zipfile.ZIP_STORED)
        z.writestr(zipfile.ZipInfo("stack.xml", ZIP_DT), "\n".join(stack) + "\n", zipfile.ZIP_DEFLATED)
        for name, a in layers:
            z.writestr(zipfile.ZipInfo(f"data/{name}.png", ZIP_DT), png_bytes(a), zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("mergedimage.png", ZIP_DT), png, zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("Thumbnails/thumbnail.png", ZIP_DT), png, zipfile.ZIP_DEFLATED)
    return buf.getvalue()


def guides():
    g = blank()
    for x in range(W):
        g[0, x] = g[H - 1, x] = (255, 0, 255, 255)
    for y in range(H):
        g[y, 0] = g[y, W - 1] = (255, 0, 255, 255)
    for y in (8, 34, 54, 76, 103):
        g[y, 1:4] = (255, 0, 255, 255)
    g[PIN[1], PIN[0]] = (255, 0, 255, 255)
    return g


def fname(subject, ext):
    tag = sha(f"{RUN}:{subject}".encode())[:8]
    return f"{PFX}-{subject}_{VAR}_{STAMP}-{tag}.{ext}"


# ----------------------------------------------------------------------------- build
def artifacts():
    src, src_png = load_src()
    nbase = north_base(src)
    fs = frame_set(src, nbase)
    files = {}          # rel path -> bytes
    man_dirs = {}
    G = guides()
    for d in DIRS:
        f = fs[d]
        entry = {"static": None, "idle": [], "walk": [], "stop_bridges": {}, "contact": [], "layers": None}
        native_frames, tags, fi = [], [], 1

        def emit(subject, layers, pose, ms, role):
            comp = over([a for _, a in layers])
            png = png_bytes(comp)
            rel = f"{OUT_REL}/png/{fname(subject, 'png')}"
            files[rel] = png
            native_frames.append((list(layers) + [("guides", G)], ms))
            return {"file": rel, "sha256": sha(png), "duration_ms": ms, "role": role,
                    "pose": {k: (round(v, 3) if isinstance(v, float) else v) for k, v in pose.items()}}, comp

        e, neutral = emit(f"{d}-static", *f["idle"][0], 600, "static neutral")   # 600 ms only as the native frame duration
        e["duration_ms"] = None
        entry["static"] = e
        if d == "south":
            assert np.array_equal(neutral, src_png), "south neutral must equal the male v8pair source texels"
            entry["static"]["exact_source"] = SRC_PNG
        start = len(native_frames)
        for i, (lay, q) in enumerate(f["idle"]):
            e, comp = emit(f"{d}-idle-f{i:02d}", lay, q, IDLE_MS[i], "idle loop")
            if i == 0:
                assert np.array_equal(comp, neutral)
            entry["idle"].append(e)
        tags.append({"name": f"{d}-idle", "from": start + 1, "to": len(native_frames)})
        start = len(native_frames)
        for p, (lay, q) in enumerate(f["walk"]):
            e, _ = emit(f"{d}-walk-p{p:02d}", lay, q, FRAME_MS, "walk phase")
            e["phase"] = p
            e["grounded_feet_source"] = sole_points(lay, d)
            entry["walk"].append(e)
        tags.append({"name": f"{d}-walk", "from": start + 1, "to": len(native_frames)})
        for p in range(NPH):
            seq = []
            start = len(native_frames)
            for s, (lay, q) in enumerate(f["stop"][p]):
                if s in (0, len(STOP_K) - 1):     # exact references, not duplicated as PNGs
                    seq.append({"ref": "walk" if s == 0 else "idle", "index": p if s == 0 else 0, "k": STOP_K[s]})
                    continue
                e, _ = emit(f"{d}-stop-p{p:02d}-s{s}", lay, q, FRAME_MS, "phase-aware stop bridge")
                e["k"] = round(STOP_K[s], 4)
                e["grounded_feet_source"] = sole_points(lay, d)
                seq.append(e)
            tags.append({"name": f"{d}-stop-p{p:02d}", "from": start + 1, "to": len(native_frames)})
            entry["stop_bridges"][f"phase{p}"] = seq
        # native sources
        lnames = [n for n, _ in f["idle"][0][0]] + ["guides"]
        pxo = make_pxo(lnames, native_frames, png_bytes(neutral), tags)
        ora = make_ora(list(f["idle"][0][0]) + [("guides", G)], png_bytes(neutral))
        files[f"{OUT_REL}/{fname(d + '-editable', 'pxo')}"] = pxo
        files[f"{OUT_REL}/{fname(d + '-static-layers', 'ora')}"] = ora
        entry["pxo"] = {"file": f"{OUT_REL}/{fname(d + '-editable', 'pxo')}", "sha256": sha(pxo),
                        "frames": len(native_frames), "layers_bottom_to_top": lnames,
                        "frame_order": "static, idle f00-f03, walk p00-p11, stop p00..p11 x (s1,s2)"}
        entry["ora"] = {"file": f"{OUT_REL}/{fname(d + '-static-layers', 'ora')}", "sha256": sha(ora),
                        "content": "static neutral role layers"}
        entry["layers"] = lnames
        man_dirs[d] = entry
    return fs, files, man_dirs


def contact_report(man):
    rep = {}
    for d in DIRS:
        walk = man[d]["walk"]
        if d in ("west", "east"):
            sgn = 1 if d == "west" else -1          # sprite-space drift of a world-fixed foot per phase
            rows = []
            for p in range(NPH):
                pl = "leg-near" if walk[p]["pose"]["planted"] == "A" else "leg-far"
                q = (p + 1) % NPH
                if walk[q]["pose"]["planted"] != walk[p]["pose"]["planted"]:
                    continue
                a = walk[p]["grounded_feet_source"][pl]; b = walk[q]["grounded_feet_source"][pl]
                dx = b["heel_x"] - a["heel_x"]
                rows.append({"from": p, "to": q, "planted": pl, "heel_dx": dx, "declared": sgn * D_PHASE,
                             "slip_source_texels": dx - sgn * D_PHASE, "sole_rows": [a["sole_row"], b["sole_row"]]})
            rep[d] = {"model": "world-locked planted heel against declared movement", "pairs": rows,
                      "max_abs_slip_source": max(abs(r["slip_source_texels"]) for r in rows),
                      "max_abs_slip_logical": max(abs(r["slip_source_texels"]) for r in rows) / 2}
        else:
            rows = []
            for p in range(NPH):
                g = walk[p]["grounded_feet_source"]
                rows.append({"phase": p, "L_sole": g["L"]["sole_row"], "R_sole": g["R"]["sole_row"]})
            rep[d] = {"model": "IN-PLACE front/back cycle; grounded foot stays at its sprite column/row, so it slips "
                               "in the world by the declared per-phase movement along screen y (NOT world-locked)",
                      "declared_world_slip_per_phase_source": D_PHASE, "sole_rows": rows}
    return rep


def stop_report(man, fs):
    rep = {}
    for d in DIRS:
        side = d in ("west", "east")
        rows = []
        for p in range(NPH):
            seq = man[d]["stop_bridges"][f"phase{p}"]
            pts = [man[d]["walk"][p]["grounded_feet_source"]] + [s["grounded_feet_source"] for s in seq[1:-1]] + \
                  [sole_points(fs[d]["idle"][0][0], d)]
            if side:
                key = "leg-near" if man[d]["walk"][p]["pose"]["planted"] == "A" else "leg-far"
                xs = [q[key]["heel_x"] for q in pts]
            else:
                xs = [q["L"]["x_min"] for q in pts]
            steps = [abs(xs[i + 1] - xs[i]) for i in range(len(xs) - 1)]
            rows.append({"phase": p, "planted_heel_x_seq": xs, "max_step_source": max(steps),
                         "total_drift_source": abs(xs[-1] - xs[0])})
        rep[d] = {"host_position_moves": False, "frames": "walk p (exact) -> s1 -> s2 -> idle f00 (exact)",
                  "frame_ms": FRAME_MS, "settle_ms_inclusive": FRAME_MS * 3, "phases": rows,
                  "max_planted_drift_source": max(r["total_drift_source"] for r in rows)}
    return rep


def manifests(fs, man):
    def rel_pkg(f):
        return "../../" + f if False else f
    sprite_set = {"schema": "worlds-between.exploration-sprite-set.v1", "set_id": f"hero-male-exploration-source-{STAMP}-{RUN}",
                  "actor_id": "protagonist-male", "density": 2, "frame_size": [W, H], "pivot": list(PIN),
                  "status": "UNAPPROVED technical source; not wired into any default; package file paths are repo-relative",
                  "actions": {"idle": {d: [{"file": "png/" + e["file"].rsplit("/", 1)[-1], "duration_ms": e["duration_ms"]} for e in man[d]["idle"]] for d in DIRS},
                              "walk": {d: [{"file": "png/" + e["file"].rsplit("/", 1)[-1], "duration_ms": e["duration_ms"]} for e in man[d]["walk"]] for d in DIRS}}}
    stop = {"schema": "worlds-between.exploration-stop-transition.supplemental.v1", "actor_id": "protagonist-male",
            "rule": "phase-aware stop: on release at walk phase p the host position stops immediately; play bridge "
                    "[walk p exact, s1, s2, idle f00 exact] at frame_ms each; settle 120 ms inclusive",
            "frame_ms": FRAME_MS, "settle_ms_inclusive": FRAME_MS * 3, "pivot": list(PIN), "logical_height": 48,
            "phase_bridges": {d: {k: [s if "ref" in s else {"file": "png/" + s["file"].rsplit("/", 1)[-1], "k": s["k"], "sha256": s["sha256"]} for s in v]
                                  for k, v in man[d]["stop_bridges"].items()} for d in DIRS}}
    return sprite_set, stop


def build_all():
    fs, files, man = artifacts()
    contact = contact_report(man)
    stops = stop_report(man, fs)
    sprite_set, stop = manifests(fs, man)
    ss_b = (json.dumps(sprite_set, indent=2, ensure_ascii=False) + "\n").encode()
    st_b = (json.dumps(stop, indent=2, ensure_ascii=False) + "\n").encode()
    files[f"{PKG_REL}/{fname('sprite-set-runtime', 'json')}"] = ss_b
    files[f"{PKG_REL}/{fname('stop-transition-supplemental', 'json')}"] = st_b
    # Lossless runtime package: existing generic loader resolves paths relative to this JSON.
    for source_rel, payload in list(files.items()):
        if source_rel.startswith(OUT_REL + "/png/") and source_rel.endswith(".png"):
            files[PKG_REL + "/png/" + source_rel.rsplit("/", 1)[-1]] = payload
    registry = {"schema": "worlds-between.exploration-sprite-set-registry.v1", "actors": {"protagonist-male": fname("sprite-set-runtime", "json")}}
    files[PKG_REL + "/" + fname("sprite-set-registry", "json")] = (json.dumps(registry, indent=2) + "\n").encode()
    source = {"project": "Worlds Between", "visual_id": "protagonist-male", "run_id": RUN, "variant": VAR,
              "status": "UNAPPROVED technical source; art not approved; not runtime-integrated; no default changed",
              "contract": {"cell": [W, H], "pivot": list(PIN), "body_texels": 96, "display_scale": 0.5,
                           "logical_height": 48, "sole_row": SOLE, "alpha": "binary", "filter": "nearest"},
              "source_inputs": {"male_v8pair_png": {"file": SRC_PNG, "sha256": SRC_PNG_SHA, "hash": "sha256-bytes"},
                                "male_v8pair_ora": {"file": SRC_ORA, "sha256": SRC_ORA_SHA, "hash": "sha256-bytes"}},
              "methods": {"south": "exact v8pair role layers; idle/walk/stop = role-layer offsets + per-leg column split at x=40",
                          "north": "back view: male south role silhouettes mirrored x'=80-x and refilled as back surfaces; authored pack/bedroll",
                          "west": "authored side puppet: 2-bone IK legs (L1=L2=20 src), arms, pack, bedroll spiral, scarf tail",
                          "east": "west role layers mirrored x'=80-x (pivot preserved); light becomes upper-right (limitation)"},
              "walk_model": {"phases": NPH, "frame_ms_reference": FRAME_MS, "declared_move_per_phase_source": D_PHASE,
                             "declared_move_per_phase_logical": D_PHASE / 2, "cycle_distance_logical": NPH * D_PHASE / 2,
                             "contacts": "side: foot A planted p0-p5, foot B planted p6-p11; front/back: L lifted p1-p5, R lifted p7-p11",
                             "pure_distance_driver": "phase = floor(distance_logical / 2) mod 12"},
              "idle_model": {"frames": 4, "duration_ms": IDLE_MS, "neutral_endpoint": "f00 == static (exact)"},
              "directions": man, "contact_check": contact, "stop_check": stops,
              "package": {"sprite_set": f"{PKG_REL}/{fname('sprite-set-runtime', 'json')}", "sprite_set_sha256": sha(ss_b),
                          "stop_supplemental": f"{PKG_REL}/{fname('stop-transition-supplemental', 'json')}",
                          "stop_supplemental_sha256_text_lf_v1": sha_text(st_b)},
              "tool": {"file": "tools/" + os.path.basename(__file__), "sha256_text_lf_v1": sha_text(rb(os.path.abspath(__file__)))}}
    files[f"{OUT_REL}/{fname('source-manifest', 'json')}"] = (json.dumps(source, indent=2, ensure_ascii=False) + "\n").encode()
    return files, source


def write_all(files):
    for rel, b in files.items():
        p = rp(rel)
        os.makedirs(_fs(os.path.dirname(p)), exist_ok=True)
        with open(_fs(p), "wb") as f:
            f.write(b)


def pixelorama_export(exe, src, out_dir, split):
    env = dict(os.environ)
    env["APPDATA"] = tempfile.mkdtemp(prefix="wb-pxappdata-")
    args = [exe, "--headless", "--quit", "--", "--export"] + (["--split-layers"] if split else []) + ["-o", os.path.join(out_dir, "f.png"), src]
    try:
        p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300, env=env)
    finally:
        shutil.rmtree(env["APPDATA"], ignore_errors=True)
    outs = sorted(f for f in os.listdir(out_dir) if f.lower().endswith(".png"))
    return p, {f: rb(os.path.join(out_dir, f)) for f in outs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["build", "check"])
    ap.add_argument("--pixelorama")
    a = ap.parse_args()
    files, source = build_all()
    if a.mode == "build":
        write_all(files)
        print(f"WROTE {len(files)} files")
        return 0
    # check: rebuild determinism vs disk + native equality
    fails, checks = [], 0
    for rel, b in files.items():
        checks += 1
        try:
            disk = rb(rp(rel))
        except OSError:
            fails.append(f"missing {rel}"); continue
        if disk != b:
            fails.append(f"rebuild differs {rel}")
    print(f"REBUILD {checks - len(fails)}/{checks}")
    res = {"rebuild": {"checked": checks, "fails": list(fails)}, "native": []}
    if a.pixelorama:
        for d in DIRS:
            pxo = rp(source["directions"][d]["pxo"]["file"])
            tmp = tempfile.mkdtemp(prefix="wb-mx23-")
            try:
                p, outs = pixelorama_export(a.pixelorama, pxo, tmp, False)
                diag = [ln for ln in (p.stdout + p.stderr).splitlines() if any(t in ln for t in ("ERROR", "SCRIPT ERROR", "WARNING"))]
                order = ([source["directions"][d]["static"]] + source["directions"][d]["idle"] + source["directions"][d]["walk"])
                stops = [s for p_ in range(NPH) for s in source["directions"][d]["stop_bridges"][f"phase{p_}"] if "file" in s]
                order += stops
                names = sorted(outs)
                ok = len(names) == len(order)
                picks = {0: "static", 1 + 0: "idle f00", 5 + 3: "walk p03", 5 + 9: "walk p09", 17 + 7: "stop p03 s2"}
                eq = {}
                for idx, lab in picks.items():
                    if idx < len(names):
                        got = decode(outs[names[idx]]); want = decode(rb(rp(order[idx]["file"])))
                        eq[lab] = bool(np.array_equal(got, want))
                    else:
                        eq[lab] = False
                allf = sum(1 for i in range(min(len(names), len(order))) if np.array_equal(decode(outs[names[i]]), decode(rb(rp(order[i]["file"])))))
                r = {"dir": d, "exit": p.returncode, "frames_exported": len(names), "frames_expected": len(order),
                     "representative_equal": eq, "all_frames_equal": f"{allf}/{len(order)}", "diagnostics": diag[:12]}
                res["native"].append(r)
                print(json.dumps(r))
                if p.returncode != 0 or not ok or not all(eq.values()) or allf != len(order):
                    fails.append(f"native {d}")
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
    res["fails"] = fails
    print("RESULT", "PASS" if not fails else "FAIL", json.dumps(fails[:10]))
    out = rp(f"{OUT_REL}/{fname('check-result', 'json')}")
    with open(_fs(out), "wb") as f:
        f.write((json.dumps(res, indent=2) + "\n").encode())
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
