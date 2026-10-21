"""Zhao Ling four-direction EXPLORATION SOURCE author (zexplore25, UNAPPROVED technical source).

Statics, 4-frame idle loops, 12-phase walk cycles (40 ms reference) and phase-aware stop bridges for
south/west/north/east at the existing Zhao contract (80x112 cell, density 2, pivot 40/104, 96-texel body).

- south: the Zhao south ORA role layers are the exact neutral (static + idle f00 are the source PNG bytes);
  idle/walk/stop are role-layer offsets and a per-leg column split at x=40 (shin/cuff/boot rise), no repaint.
- north: back view from the south role silhouettes mirrored x'=80-x (her left radio/earcup stay on her left)
  refilled as back surfaces: bob hair with teal inner tips, headset band, jacket back + collar, crossbody strap.
- west: authored side puppet, her LEFT side to the viewer: earcup + antenna near, radio on the near hip,
  tablet in the far (right) hand.
- east: authored side puppet with her RIGHT side to the viewer (long hair side, tablet in the near hand,
  radio on the far hip peeking behind, earcup hidden, antenna behind the head), then mirrored x'=80-x.
  It is NOT a mirror of west; light becomes upper-right (limitation).

Character-agnostic helpers (raster primitives, IK, pose tables, PXO/ORA writers, guides, contact/stop
reports, Pixelorama export) are imported from the mexplore23 author, which this tool does not modify.

Usage:  python -X utf8 -I <tool> build|check [--pixelorama EXE]
Writes only NEW files under outputs/zexplore25 and game/data/zexplore25.
"""
import argparse, importlib.util, io, json, math, os, shutil, sys, tempfile, zipfile
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_MX = os.path.join(_HERE, "rpg-2-star-ocean-the-second_protagonist-male_explore-4dir-source-author_unapproved-mexplore23-v01_20261021-162551-6e3b1a7d.py")
_spec = importlib.util.spec_from_file_location("wb_mexplore23_helpers", _MX)
mx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mx)
_fs, rp, rb, sha, sha_text, png_bytes, decode, blank = mx._fs, mx.rp, mx.rb, mx.sha, mx.sha_text, mx.png_bytes, mx.decode, mx.blank
shift, mirror, over, lerp_pose = mx.shift, mx.mirror, mx.over, mx.lerp_pose

SRC_DIR = "game/assets/characters/zhao-ling/south-idle-static-pilot-unapproved-v01"
SRC_ORA = SRC_DIR + "/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-editable-layers_unapproved-v01_20261018-052006-2e77e99e.ora"
SRC_PNG = SRC_DIR + "/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot_unapproved-v01_20261018-052006-73f1d603.png"
SRC_PNG_SHA = "069acee4ba3c25c55cd381e19ab3a7453bb9ddd7fe27ff69eca7068c038859f7"
SRC_ORA_SHA = "180f86a94456a5a13f92288b5c7d286530af953e20c9a9b31e84c3bfa14c6fb4"
STAMP = "20261021-172651"
RUN = "9f823054"
OUT_REL = "outputs/zexplore25"
PKG_REL = "game/data/zexplore25"
PFX = "rpg-2-star-ocean-the-second_zhao-ling_explore"
VAR = "unapproved-zexplore25-v01"
W, H, PIN, SOLE = mx.W, mx.H, mx.PIN, mx.SOLE
ZIP_DT = (2026, 10, 21, 17, 26, 50)
mx.ZIP_DT = ZIP_DT          # in-process only: zip entry dates for this run's PXO/ORA
DIRS, NPH, FRAME_MS, STOP_K, IDLE_MS, D_PHASE = mx.DIRS, mx.NPH, mx.FRAME_MS, mx.STOP_K, mx.IDLE_MS, mx.D_PHASE
NORMAL_SPEED_LOGICAL = 140.0

PAL = {"K": "#0c0d12", "k": "#1f2029", "S": "#f4d8c6", "s": "#dcb09c", "z": "#b3806f", "H": "#525b76",
       "h": "#2f3348", "g": "#151722", "B": "#8fd3e6", "b": "#4f9dbf", "n": "#2c6585", "W": "#d7dce2",
       "w": "#8f98a8", "v": "#535b6b", "Y": "#e8c780", "y": "#b48c4d", "u": "#6c5133", "J": "#666a7d",
       "j": "#424556", "q": "#272935", "C": "#dfe0e5", "c": "#abaeb9", "x": "#777b8c", "T": "#f6f4ee",
       "L": "#7c5745", "l": "#4c342b", "P": "#74767f", "p": "#54565f", "D": "#5a5d6b", "d": "#2a2c36",
       "e": "#6f93ad", "E": "#1b2132", "m": "#b8706c"}
RGB = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in PAL.items()}
YY, XX = np.arange(H)[:, None], np.arange(W)[None, :]


class ZCanvas(mx.Canvas):
    def px(self, x, y, k):
        x, y = int(x), int(y)
        if 0 <= x < W and 0 <= y < H:
            self.a[y, x, :3] = RGB[k]
            self.a[y, x, 3] = 255

    def outline(self):
        m = self.a[..., 3] == 255
        o = np.zeros_like(m)
        o[1:] |= m[:-1]; o[:-1] |= m[1:]; o[:, 1:] |= m[:, :-1]; o[:, :-1] |= m[:, 1:]
        o &= ~m
        self.a[o, :3] = RGB["K"]; self.a[o, 3] = 255
        return self


def zshade(mask, base, lit, dark, rim=None, litfrac=0.3, darkfrac=0.25):
    c = ZCanvas()
    ys = np.nonzero(mask.any(1))[0]
    if not len(ys):
        return c
    for y in ys:
        row = np.nonzero(mask[y])[0]
        x0, span = row.min(), row.max() - row.min() + 1
        for x in row:
            f = (x - x0) / max(span - 1, 1)
            c.px(x, y, rim if (rim and y - ys.min() < 2) else (lit if f < litfrac else (dark if f > 1 - darkfrac else base)))
    return c


def clip_floor(a):
    a = a.copy(); a[SOLE + 1:] = 0
    return a


# ----------------------------------------------------------------------------- source (exact)
SOUTH_LAYERS = ["hair-back", "boots", "legs", "torso-jacket", "straps-belt", "radio-kit", "arm-tablet",
                "arm-near-radio", "head-face", "hair-front", "headset-antenna"]


def load_src():
    ora, png = rb(rp(SRC_ORA)), rb(rp(SRC_PNG))
    assert sha(png) == SRC_PNG_SHA and sha(ora) == SRC_ORA_SHA, "Zhao south source hash drift"
    with zipfile.ZipFile(io.BytesIO(ora)) as z:
        lay = {n: decode(z.read(f"data/{n}.png")) for n in SOUTH_LAYERS}
    assert np.array_equal(over([lay[n] for n in SOUTH_LAYERS]), decode(png)), "ORA layers != source PNG"
    return lay, decode(png), png


LIFT_ROW = 82   # front/back step: shin, rolled cuff and boot rise; thigh stays


def lift_legs(a, pose):
    parts = []
    for sl, key in ((slice(0, 40), "ll"), (slice(40, W), "rl")):
        leg = blank(); leg[:, sl] = a[:, sl]
        upper = leg.copy(); upper[LIFT_ROW:] = 0
        lower = leg.copy(); lower[:LIFT_ROW] = 0
        parts += [upper, shift(lower, 0, -pose.get(key, 0))]
    return over(parts)


def render_south(src, pose):
    up, hd = pose.get("bob", 0), pose.get("head", 0)
    out = []
    for n in SOUTH_LAYERS:
        a = src[n]
        if n in ("legs", "boots"):
            a = lift_legs(a, pose)
        elif n in ("hair-back", "head-face", "hair-front", "headset-antenna"):
            a = shift(a, 0, hd)
        elif n == "arm-tablet":
            a = shift(a, 0, up + pose.get("arm_l", 0))
        elif n == "arm-near-radio":
            a = shift(a, 0, up + pose.get("arm_r", 0))
        elif n == "radio-kit":
            a = shift(a, 0, up + pose.get("pack", 0))
        else:
            a = shift(a, 0, up)
        out.append((n, a))
    return out


# ----------------------------------------------------------------------------- north (back view)
NORTH_LAYERS = ["legs", "boots", "torso-jacket", "strap-back", "radio-kit", "arm-radio", "arm-tablet",
                "head-back", "hair", "headset-antenna"]


def north_base(src):
    m = lambda n: mirror(src[n])[..., 3] == 255
    base = {}
    mm = m("legs")
    c = zshade(mm, "p", "P", "q")
    keep = mm & (YY >= 86)                                   # rolled cuffs read the same from behind
    c.a[keep] = mirror(src["legs"])[keep]
    c.a[mm & ((YY == 77) | (YY == 78)) & (c.a[..., 3] == 255) & (YY < 86)] = (*RGB["q"], 255)   # knee crease
    base["legs"] = clip_floor(c.outline().a)
    mm = m("boots")
    c = zshade(mm, "d", "D", "k", rim="D")
    for x in range(W):
        col = np.nonzero(mm[:, x])[0]
        if len(col):
            c.px(x, col.max(), "k"); c.px(x, col.max() - 1, "d")
    base["boots"] = clip_floor(c.outline().a)
    tm = m("torso-jacket") | m("straps-belt")
    c = zshade(tm, "j", "J", "q")
    for y in range(31, 37):
        for x in np.nonzero(tm[y])[0]:
            if 32 <= x <= 48:
                c.px(x, y, "C" if y < 35 else "c")               # light collar band across the back
    for y in range(40, 61):
        if tm[y, 40]:
            c.px(40, y, "q")                                     # centre back seam
    base["torso-jacket"] = c.outline().a
    c = ZCanvas()                                                # crossbody strap: her right shoulder -> left hip
    c.seg(47, 36, 34, 57, 2.4, "L")
    c.seg(47.6, 36.6, 34.6, 57.6, 0.9, "l")
    base["strap-back"] = c.outline().a
    rm = m("radio-kit")
    c = zshade(rm, "v", "w", "q")
    ys = np.nonzero(rm.any(1))[0]
    for x in np.nonzero(rm[ys.min() + 2])[0]:
        c.px(x, ys.min() + 2, "y")                               # strap clip band
    for y in range(ys.min() + 6, ys.max() - 3, 3):
        for x in np.nonzero(rm[y])[0][1:-1:2]:
            c.px(x, y, "x")                                      # back vents
    base["radio-kit"] = c.outline().a
    am = m("arm-near-radio")
    c = zshade(am, "j", "J", "q")
    ys = np.nonzero(am.any(1))[0]
    for y in range(ys.max() - 1, ys.max() + 1):
        for x in np.nonzero(am[y])[0]:
            c.px(x, y, "s")
    for x in np.nonzero(am[ys.max() - 3])[0]:
        c.px(x, ys.max() - 3, "C")
    base["arm-radio"] = c.outline().a
    am = m("arm-tablet")
    tab = am & (XX >= 80 - 23) & (YY >= 46)
    sleeve = am & ~tab
    c = zshade(sleeve, "j", "J", "q")
    c2 = zshade(tab, "v", "w", "k")
    c.a[tab] = c2.a[tab]
    ys = np.nonzero(tab.any(1))[0]
    xs = np.nonzero(tab.any(0))[0]
    c.px((xs.min() + xs.max()) // 2, (ys.min() + ys.max()) // 2, "b")   # case logo dot
    base["arm-tablet"] = c.outline().a
    hm = m("head-face")
    c = ZCanvas()
    for y, x in zip(*np.nonzero(hm)):
        c.px(x, y, "z" if y > 31 else "s")
    base["head-back"] = c.outline().a
    hr = m("hair-front") | m("hair-back") | (hm & (YY <= 31))
    c = zshade(hr, "h", "H", "g", litfrac=0.25)
    for x in (32, 37, 43, 48):                                   # a few vertical strand partings, no dot grid
        col = np.nonzero(hr[:, x])[0]
        for y in col[3:-3]:
            if y >= 16:
                c.px(x, y, "g")
    for x in range(W):                                          # teal inner tips at the bob hem
        col = np.nonzero(hr[:, x])[0]
        if len(col) and col.max() >= 27:
            c.px(x, col.max(), "n"); c.px(x, col.max() - 1, "b")
    base["hair"] = c.outline().a
    c = ZCanvas()
    c.a = mirror(src["headset-antenna"]).copy()                 # earcup on her left = viewer left from behind
    c.seg(36, 19, 39, 12.5, 1.6, "k")
    c.seg(39, 12.5, 47, 13, 1.6, "k")
    c.seg(47, 13, 50, 18, 1.6, "k")
    base["headset-antenna"] = c.a
    return base


def render_north(base, pose):
    up, hd = pose.get("bob", 0), pose.get("head", 0)
    out = []
    for n in NORTH_LAYERS:
        a = base[n]
        if n in ("legs", "boots"):
            a = lift_legs(a, pose)
        elif n in ("head-back", "hair", "headset-antenna"):
            a = shift(a, 0, hd)
        elif n == "arm-radio":
            a = shift(a, 0, up + pose.get("arm_l", 0))
        elif n == "arm-tablet":
            a = shift(a, 0, up + pose.get("arm_r", 0))
        elif n == "radio-kit":
            a = shift(a, 0, up + pose.get("pack", 0))
        else:
            a = shift(a, 0, up)
        out.append((n, clip_floor(a)))
    return out


# ----------------------------------------------------------------------------- side puppet (drawn facing -x)
ANKLE_UP = 5
LEG = 18.6      # Zhao thigh = shin (source texels): hip row 60 to ankle row 97 is near-straight at neutral
HIP_Y = 60


def ik(hx, hy, ax, ay, l1=LEG, l2=LEG):
    dx, dy = ax - hx, ay - hy
    d = min(math.hypot(dx, dy), l1 + l2 - 1e-6)
    a = math.atan2(dy, dx)
    b = math.acos((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))
    return hx + l1 * math.cos(a + b), hy + l1 * math.sin(a + b)


def draw_leg(ax_, lift, hip, near):
    c = ZCanvas()
    hx, hy = hip
    ay = SOLE - 1 - ANKLE_UP - lift
    kx, ky = ik(hx, hy, ax_, ay)
    tr, trs = ("P", "p") if near else ("p", "q")
    c.seg(hx, hy, kx, ky, 9, trs)                                # baggy trousers
    c.seg(hx - 0.6, hy, kx - 0.6, ky, 6, tr)
    c.seg(kx, ky, ax_, ay, 8, trs)
    c.seg(kx - 0.5, ky, ax_ - 0.5, ay, 5, tr)
    t = 8 / max(math.hypot(kx - ax_, ky - ay), 1)
    bx, by = ax_ + (kx - ax_) * t, ay + (ky - ay) * t
    c.seg(bx, by, ax_, ay, 7, "d")
    c.seg(bx - 0.5, by - 1, bx + 0.5, by - 1, 9, "C" if near else "c")   # rolled cuff
    c.seg(bx - 0.5, by + 0.6, bx + 0.5, by + 0.6, 9, "c" if near else "x")
    sole = ay + ANKLE_UP
    c.poly([(ax_ + 4, ay - 1), (ax_ - 3, ay - 1), (ax_ - 7, sole - 2), (ax_ - 7, sole + 0.99), (ax_ + 4, sole + 0.99)], "d")
    if near:
        c.px(ax_ - 4, sole - 2, "D"); c.px(ax_ - 5, sole - 1, "D"); c.px(ax_ - 1, ay, "D")
    for x in range(int(ax_ - 7), int(ax_ + 4) + 1):
        c.px(x, sole, "k")
    return c.outline().a


def draw_arm(sh, ang, near):
    c = ZCanvas()
    sx, sy = sh
    ex, ey = sx + 11 * math.sin(-ang), sy + 11 * math.cos(ang)
    fa = ang - 0.35 if ang < 0 else ang - 0.15
    hx, hy = ex + 9 * math.sin(-fa), ey + 9 * math.cos(fa)
    sl, sd = ("J", "j") if near else ("j", "q")
    c.seg(sx, sy, ex, ey, 8, sd)                                 # oversized sleeve
    c.seg(sx - 0.6, sy, ex - 0.6, ey, 5, sl)
    c.seg(ex, ey, hx, hy, 7, sd)
    c.seg(ex - 0.5, ey, hx - 0.5, hy, 4, sl)
    c.seg(hx - (hx - ex) * 0.12, hy - (hy - ey) * 0.12, hx, hy, 7, "C" if near else "c")
    c.ell(hx, hy + 2, 2.2, 2.2, "s" if near else "z")
    return c.outline().a, (hx, hy + 2)


def draw_tablet(hand):
    c = ZCanvas()
    hx, hy = hand
    c.poly([(hx - 3, hy - 3), (hx + 1.99, hy - 3), (hx + 1.99, hy + 8.99), (hx - 3, hy + 8.99)], "v")
    c.poly([(hx - 3, hy - 3), (hx - 1.01, hy - 3), (hx - 1.01, hy + 8.99), (hx - 3, hy + 8.99)], "n")
    c.px(hx - 3, hy - 2, "B"); c.px(hx - 2, hy - 1, "b"); c.px(hx + 1, hy - 2, "w")
    c.ell(hx, hy + 1, 1.8, 1.8, "s")                             # gripping fingers over the case
    return c.outline().a


def draw_radio(x0, y0):
    c = ZCanvas()
    c.poly([(x0, y0), (x0 + 8.99, y0), (x0 + 8.99, y0 + 15.99), (x0, y0 + 15.99)], "v")
    c.poly([(x0 + 1, y0 + 2), (x0 + 7.99, y0 + 2), (x0 + 7.99, y0 + 14.99), (x0 + 1, y0 + 14.99)], "q")
    c.ell(x0 + 3.5, y0 + 6.5, 2.0, 2.0, "b"); c.px(x0 + 3, y0 + 5, "B")
    for y in (y0 + 10, y0 + 12):
        for x in range(x0 + 2, x0 + 8, 2):
            c.px(x, y, "w")
    for x in range(x0, x0 + 9):
        c.px(x, y0, "W" if x < x0 + 4 else "w")
    c.px(x0 + 7, y0 + 4, "Y"); c.px(x0 + 6, y0 + 4, "y")
    for y in range(y0 - 4, y0):
        c.px(x0 + 8, y, "w")                                     # stub antenna
    return c.outline().a


def render_side(pose, near):
    """near='left': her left side to the viewer (west). near='right': her right side (east, pre-mirror)."""
    b, hd = pose.get("bob", 0), pose.get("head", 0)
    hip = (40.5, HIP_Y + b)
    o = {}
    o["leg-near"] = draw_leg(pose["ax"], pose["al"], hip, True)
    o["leg-far"] = draw_leg(pose["bx"] + 1, pose["bl"], (hip[0] + 1, hip[1]), False)
    o["arm-near"], hand_n = draw_arm((40.5, 39 + b), pose["arm_n"], True)
    o["arm-far"], hand_f = draw_arm((43, 39 + b), pose["arm_f"], False)
    c = ZCanvas()                                                # oversized jacket, open front, white tee
    c.poly([(34, 34 + b), (46, 34 + b), (50, 40 + b), (51, 63 + b), (31, 63 + b), (31, 42 + b)], "j")
    c.poly([(34, 34 + b), (38, 34 + b), (37, 63 + b), (31, 63 + b), (31, 42 + b)], "J")
    c.poly([(48, 38 + b), (50, 40 + b), (51, 63 + b), (48, 63 + b)], "q")
    c.poly([(31, 40 + b), (33.9, 38 + b), (33.9, 58 + b), (31, 58 + b)], "T")
    for x in range(31, 52):
        c.px(x, 63 + b, "q")
    c.px(36, 52 + b, "q"); c.px(37, 52 + b, "q")                 # pocket
    o["torso-jacket"] = c.outline().a
    c = ZCanvas()
    c.poly([(35, 32 + b), (45, 32 + b), (46, 36 + b), (35, 37 + b)], "C")   # light collar
    for x in range(35, 46):
        c.px(x, 36 + b, "c")
    o["collar"] = c.outline().a
    c = ZCanvas()                                                # crossbody strap
    if near == "left":
        c.seg(45, 36 + b, 36, 57 + b, 2.2, "L")
    else:
        c.seg(36, 37 + b, 45, 56 + b, 2.2, "L")
    o["strap"] = c.outline().a
    radio = draw_radio(42 if near == "left" else 46, 56 + b + pose.get("flap", 0))
    tablet = draw_tablet(hand_f if near == "left" else hand_n)
    c = ZCanvas()                                                # profile face toward -x
    c.poly([(34, 15 + hd), (41, 15 + hd), (42, 31 + hd), (37, 33 + hd), (34, 31 + hd), (33, 28 + hd),
            (32, 26 + hd), (30.5, 24 + hd), (32, 22 + hd), (33, 18 + hd)], "S")
    c.poly([(39, 15 + hd), (42, 15 + hd), (42, 31 + hd), (39, 32 + hd)], "s")
    c.poly([(34, 29 + hd), (37, 29 + hd), (37, 33 + hd), (35, 32 + hd)], "s")
    c.px(33, 22 + hd, "E"); c.px(34, 22 + hd, "E"); c.px(34, 23 + hd, "e")
    c.px(31, 24 + hd, "z"); c.px(34, 28 + hd, "m")
    o["head-face"] = c.outline().a
    hem = 30 if near == "left" else 34                            # asymmetric bob: short left, long right
    c = ZCanvas()
    c.ell(42, 20 + hd, 10, 8.6, "h")
    c.ell(40, 17 + hd, 8, 5.6, "H")
    c.poly([(30, 16 + hd), (37, 12.5 + hd), (38, 20 + hd), (33, 19 + hd), (31, 20 + hd)], "h")
    c.poly([(41, 21 + hd), (51, 21 + hd), (50, hem + hd), (42, hem + 1 + hd)], "h")
    for x in range(42, 51):
        c.px(x, hem + hd, "n"); c.px(x, hem - 1 + hd, "b")
    for (x, y, k) in ((38, 13, "H"), (44, 14, "g"), (47, 18, "g"), (45, 24, "g"), (36, 15, "H"), (49, 26, "g")):
        c.px(x, y + hd, k)
    face = o["head-face"][..., 3] == 255
    cut = face & (YY >= 19 + hd) & (XX <= 40)
    c.a[cut] = 0
    c.outline()
    c.a[cut & (c.a[..., 3] == 255)] = o["head-face"][cut & (c.a[..., 3] == 255)]
    o["hair"] = c.a
    c = ZCanvas()
    if near == "left":                                           # near earcup + band
        c.seg(43, 20 + hd, 42, 12 + hd, 1.6, "k")
        c.seg(42, 12 + hd, 37, 11.5 + hd, 1.6, "k")
        c.ell(43, 24 + hd, 3.0, 3.8, "w")
        c.ell(43, 24 + hd, 2.0, 2.8, "b")
        c.px(42, 23 + hd, "B")
        c.outline()
    else:                                                        # far earcup hidden; band crosses the crown
        c.seg(43, 11.5 + hd, 36, 12 + hd, 1.4, "k")
    o["headset"] = c.a
    c = ZCanvas()                                                # vertical brass-tipped antenna (no outline)
    for y in range(10, 21):
        c.px(45, y + hd, "v")
    c.px(45, 8 + hd, "Y"); c.px(45, 9 + hd, "y")
    o["antenna"] = c.a
    if near == "left":
        order = ["arm-far", "leg-far", "leg-near", "torso-jacket", "tablet", "collar", "strap", "radio",
                 "head-face", "hair", "headset", "antenna", "arm-near"]
        o["tablet"], o["radio"] = tablet, radio
    else:
        order = ["antenna", "radio", "arm-far", "leg-far", "leg-near", "torso-jacket", "collar", "strap",
                 "head-face", "hair", "headset", "arm-near", "tablet"]
        o["tablet"], o["radio"] = tablet, radio
    return [(n, o[n]) for n in order]


def render_west(pose):
    return render_side(pose, "left")


def render_east(pose):
    return [(n, mirror(a)) for n, a in render_side(pose, "right")]


# ----------------------------------------------------------------------------- frame set + build
def frame_set(src, nbase):
    out = {}
    for d in DIRS:
        side = d in ("west", "east")
        neutral = mx.SIDE_NEUTRAL if side else mx.FB_NEUTRAL
        walkp = [mx.side_walk_pose(p) if side else mx.fb_walk_pose(p) for p in range(NPH)]
        idlep = [dict(neutral, **i) for i in (mx.SIDE_IDLE if side else mx.FB_IDLE)]
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
        out[d] = {"idle": idle, "walk": walk, "stop": stop}
    return out


def sole_points(layers, d):
    if d in ("west", "east"):
        return mx.sole_points(layers, d)
    return mx.sole_points(layers, d)


def fname(subject, ext):
    tag = sha(f"{RUN}:{subject}".encode())[:8]
    return f"{PFX}-{subject}_{VAR}_{STAMP}-{tag}.{ext}"


def artifacts():
    src, src_arr, src_png = load_src()
    nbase = north_base(src)
    fs = frame_set(src, nbase)
    files, man_dirs, G = {}, {}, mx.guides()
    for d in DIRS:
        f = fs[d]
        entry = {"static": None, "idle": [], "walk": [], "stop_bridges": {}}
        native, tags = [], []

        def emit(subject, layers, pose, ms, role):
            comp = over([a for _, a in layers])
            png = src_png if (d == "south" and np.array_equal(comp, src_arr)) else png_bytes(comp)
            rel = f"{OUT_REL}/png/{fname(subject, 'png')}"
            files[rel] = png
            native.append((list(layers) + [("guides", G)], ms))
            return {"file": rel, "sha256": sha(png), "duration_ms": ms, "role": role,
                    "pose": {k: (round(v, 3) if isinstance(v, float) else v) for k, v in pose.items()}}, comp

        e, neutral = emit(f"{d}-static", *f["idle"][0], 600, "static neutral")
        e["duration_ms"] = None
        entry["static"] = e
        if d == "south":
            assert np.array_equal(neutral, src_arr) and e["sha256"] == SRC_PNG_SHA
            e["exact_source"] = SRC_PNG
        start = len(native)
        for i, (lay, q) in enumerate(f["idle"]):
            e, comp = emit(f"{d}-idle-f{i:02d}", lay, q, IDLE_MS[i], "idle loop")
            assert i or np.array_equal(comp, neutral)
            entry["idle"].append(e)
        tags.append({"name": f"{d}-idle", "from": start + 1, "to": len(native)})
        start = len(native)
        for p, (lay, q) in enumerate(f["walk"]):
            e, _ = emit(f"{d}-walk-p{p:02d}", lay, q, FRAME_MS, "walk phase")
            e["phase"] = p
            e["grounded_feet_source"] = sole_points(lay, d)
            entry["walk"].append(e)
        tags.append({"name": f"{d}-walk", "from": start + 1, "to": len(native)})
        for p in range(NPH):
            seq, start = [], len(native)
            for s, (lay, q) in enumerate(f["stop"][p]):
                if s in (0, len(STOP_K) - 1):
                    seq.append({"ref": "walk" if s == 0 else "idle", "index": p if s == 0 else 0, "k": STOP_K[s]})
                    continue
                e, _ = emit(f"{d}-stop-p{p:02d}-s{s}", lay, q, FRAME_MS, "phase-aware stop bridge")
                e["k"] = round(STOP_K[s], 4)
                e["grounded_feet_source"] = sole_points(lay, d)
                seq.append(e)
            tags.append({"name": f"{d}-stop-p{p:02d}", "from": start + 1, "to": len(native)})
            entry["stop_bridges"][f"phase{p}"] = seq
        lnames = [n for n, _ in f["idle"][0][0]] + ["guides"]
        pxo = mx.make_pxo(lnames, native, png_bytes(neutral), tags)
        ora = mx.make_ora(list(f["idle"][0][0]) + [("guides", G)], files[entry["static"]["file"]])
        files[f"{OUT_REL}/{fname(d + '-editable', 'pxo')}"] = pxo
        files[f"{OUT_REL}/{fname(d + '-static-layers', 'ora')}"] = ora
        entry["pxo"] = {"file": f"{OUT_REL}/{fname(d + '-editable', 'pxo')}", "sha256": sha(pxo), "frames": len(native),
                        "layers_bottom_to_top": lnames, "frame_order": "static, idle f00-f03, walk p00-p11, stop p00..p11 x (s1,s2)"}
        entry["ora"] = {"file": f"{OUT_REL}/{fname(d + '-static-layers', 'ora')}", "sha256": sha(ora),
                        "content": "static neutral role layers + hidden guides"}
        man_dirs[d] = entry
    return fs, files, man_dirs


def speed_disclosure(contact):
    per_phase_world_src = NORMAL_SPEED_LOGICAL * FRAME_MS / 1000.0 * 2
    return {"normal_speed_logical_px_s": NORMAL_SPEED_LOGICAL,
            "declared_cycle_speed_logical_px_s_at_40ms": D_PHASE / 2 / (FRAME_MS / 1000.0),
            "world_advance_per_40ms_phase_source_at_normal_speed": per_phase_world_src,
            "side_planted_foot_world_drift_per_phase_source_if_phase_clock_40ms": round(per_phase_world_src - D_PHASE, 3),
            "side_planted_foot_world_drift_per_phase_logical_if_phase_clock_40ms": round((per_phase_world_src - D_PHASE) / 2, 3),
            "distance_driver_phase_rate_hz_at_normal_speed": NORMAL_SPEED_LOGICAL / (D_PHASE / 2),
            "front_back_in_place_world_drift_per_40ms_source": per_phase_world_src,
            "note": "No foot lock is claimed at normal speed. With a fixed 40 ms phase clock the planted side foot "
                    "slides by the listed amount per phase; with the pure distance driver (phase=floor(dist/2) mod 12) "
                    "the source cycle is footlocked but advances 70 phases/s, so 60 fps playback skips phases. "
                    "Front/back cycles are in place (not world-locked)."}


def build_all():
    fs, files, man = artifacts()
    contact = mx.contact_report(man)
    stops = mx.stop_report(man, {d: {"idle": fs[d]["idle"]} for d in DIRS})
    entry = lambda e: {"file": "png/" + e["file"].rsplit("/", 1)[-1], "duration_ms": e["duration_ms"]}
    set_name = fname("sprite-set-runtime", "json")
    sprite_set = {"schema": "worlds-between.exploration-sprite-set.v1", "set_id": f"zhao-ling-exploration-source-{STAMP}-{RUN}",
                  "actor_id": "zhao-ling", "density": 2, "frame_size": [W, H], "pivot": list(PIN),
                  "status": "UNAPPROVED technical source; not wired into any default; frame paths are relative to this JSON",
                  "actions": {"idle": {d: [entry(e) for e in man[d]["idle"]] for d in DIRS},
                              "walk": {d: [entry(e) for e in man[d]["walk"]] for d in DIRS}}}
    stop = {"schema": "worlds-between.exploration-stop-transition.supplemental.v1", "actor_id": "zhao-ling",
            "rule": "phase-aware stop: on release at walk phase p the host position stops immediately; play bridge "
                    "[walk p exact, s1, s2, idle f00 exact] at frame_ms each; settle 120 ms inclusive",
            "frame_ms": FRAME_MS, "settle_ms_inclusive": FRAME_MS * 3, "pivot": list(PIN), "logical_height": 48,
            "runtime_default": False,
            "phase_bridges": {d: {k: [s if "ref" in s else {"file": "png/" + s["file"].rsplit("/", 1)[-1], "k": s["k"], "sha256": s["sha256"]} for s in v]
                                  for k, v in man[d]["stop_bridges"].items()} for d in DIRS}}
    ss_b = (json.dumps(sprite_set, indent=2, ensure_ascii=False) + "\n").encode()
    st_b = (json.dumps(stop, indent=2, ensure_ascii=False) + "\n").encode()
    files[f"{PKG_REL}/{set_name}"] = ss_b
    files[f"{PKG_REL}/{fname('stop-transition-supplemental', 'json')}"] = st_b
    for rel, payload in list(files.items()):
        if rel.startswith(OUT_REL + "/png/"):
            files[PKG_REL + "/png/" + rel.rsplit("/", 1)[-1]] = payload
    reg_rel = PKG_REL + "/" + fname("sprite-set-registry", "json")
    registry = {"schema": "worlds-between.exploration-sprite-set-registry.v1", "actors": {"zhao-ling": set_name}}
    files[reg_rel] = (json.dumps(registry, indent=2) + "\n").encode()
    files[f"{OUT_REL}/{fname('loader-ready', 'json')}"] = (json.dumps(
        {"actor_id": "zhao-ling", "registry": reg_rel, "sprite_set": f"{PKG_REL}/{set_name}",
         "registry_sha256": sha(files[reg_rel]), "sprite_set_sha256": sha(ss_b),
         "status": "UNAPPROVED technical source; not runtime default"}, indent=2) + "\n").encode()
    source = {"project": "Worlds Between", "visual_id": "zhao-ling", "run_id": RUN, "variant": VAR,
              "status": "UNAPPROVED technical source; art not approved; not runtime-integrated; no default changed",
              "contract": {"cell": [W, H], "pivot": list(PIN), "density": 2, "body_texels": 96, "logical_height": 48,
                           "sole_row": SOLE, "alpha": "binary", "filter": "nearest"},
              "source_inputs": {"zhao_south_png": {"file": SRC_PNG, "sha256": SRC_PNG_SHA, "hash": "sha256-bytes"},
                                "zhao_south_ora": {"file": SRC_ORA, "sha256": SRC_ORA_SHA, "hash": "sha256-bytes"}},
              "methods": {"south": "exact Zhao south role layers; static and idle f00 are the source PNG bytes; idle/walk/stop = role-layer offsets + per-leg column split at x=40 (rows>=82 rise)",
                          "north": "back view: south role silhouettes mirrored x'=80-x and refilled as back surfaces (bob hair + teal tips, headset band, collar, strap, radio back, tablet case back)",
                          "west": "authored side puppet, her left side to viewer: near earcup + antenna, near-hip radio, tablet in far right hand",
                          "east": "authored side puppet, her right side to viewer (long bob side, near-hand tablet, far-hip radio, hidden earcup), mirrored x'=80-x; light becomes upper-right (limitation)"},
              "reused_helpers": {"file": "tools/" + os.path.basename(_MX), "sha256_text_lf_v1": sha_text(rb(_MX))},
              "walk_model": {"phases": NPH, "frame_ms_reference": FRAME_MS, "declared_move_per_phase_source": D_PHASE,
                             "contacts": "side: foot A planted p0-p5, foot B planted p6-p11; front/back: L lifted p1-p5, R lifted p7-p11",
                             "pure_distance_driver": "phase = floor(distance_logical / 2) mod 12"},
              "idle_model": {"frames": 4, "duration_ms": IDLE_MS, "neutral_endpoint": "f00 == static (exact)"},
              "directions": man, "contact_check": contact, "normal_speed_drift": speed_disclosure(contact), "stop_check": stops,
              "package": {"sprite_set": f"{PKG_REL}/{set_name}", "sprite_set_sha256": sha(ss_b), "registry": reg_rel,
                          "stop_supplemental": f"{PKG_REL}/{fname('stop-transition-supplemental', 'json')}",
                          "stop_supplemental_sha256_text_lf_v1": sha_text(st_b)},
              "tool": {"file": "tools/" + os.path.basename(__file__), "sha256_text_lf_v1": sha_text(rb(os.path.abspath(__file__)))}}
    files[f"{OUT_REL}/{fname('source-manifest', 'json')}"] = (json.dumps(source, indent=2, ensure_ascii=False) + "\n").encode()
    return fs, files, source


# ----------------------------------------------------------------------------- checks
def source_checks(fs, files, source):
    res = []

    def ck(name, ok, detail=""):
        res.append({"check": name, "pass": bool(ok), "detail": detail})

    pal = set(RGB.values())
    for d in DIRS:
        e = source["directions"][d]
        allf = [("static", e["static"])] + [("idle", x) for x in e["idle"]] + [("walk", x) for x in e["walk"]] + \
               [("stop", s) for p in range(NPH) for s in e["stop_bridges"][f"phase{p}"] if "file" in s]
        bad, hts = [], {"static": [], "idle": [], "walk": [], "stop": []}
        for kind, x in allf:
            a = decode(files[x["file"]])
            al = a[..., 3]
            rows = np.nonzero(al.any(1))[0]
            if a.shape != (H, W, 4) or set(np.unique(al)) - {0, 255} or al[0].any() or al[-1].any() or al[:, 0].any() or al[:, -1].any():
                bad.append(x["file"])
            if rows.max() != SOLE or {tuple(c) for c in a[al == 255][:, :3]} - pal:
                bad.append(x["file"] + " floor/palette")
            hts[kind].append(int(rows.max() - rows.min() + 1))
        ck(f"{d} frames 80x112 binary alpha transparent border sole 103 palette", not bad, bad[:3])
        ck(f"{d} static/idle body 96+-1", all(95 <= h <= 97 for h in hts["static"] + hts["idle"]), hts["static"] + hts["idle"])
        ck(f"{d} walk/stop height <= 97", max(hts["walk"] + hts["stop"]) <= 97, [min(hts["walk"] + hts["stop"]), max(hts["walk"] + hts["stop"])])
        ck(f"{d} counts idle 4 walk 12 stop 24", (len(e["idle"]), len(e["walk"]), len(hts["stop"])) == (4, 12, 24))
        low = [decode(files[x["file"]])[78:104] for x in e["walk"]]
        ck(f"{d} walk lower body changes across phases (not bob-only)", len({b.tobytes() for b in low}) >= 6, len({b.tobytes() for b in low}))
        ora = rb(rp(e["ora"]["file"])) if False else files[e["ora"]["file"]]
        with zipfile.ZipFile(io.BytesIO(ora)) as z:
            names = [n for n in e["pxo"]["layers_bottom_to_top"] if n != "guides"]
            comp = over([decode(z.read(f"data/{n}.png")) for n in names])
            ck(f"{d} ORA role layers recompose to static PNG", np.array_equal(comp, decode(files[e["static"]["file"]])) and
               np.array_equal(decode(z.read("mergedimage.png")), comp), len(names))
        with zipfile.ZipFile(io.BytesIO(files[e["pxo"]["file"]])) as z:
            nl = len(e["pxo"]["layers_bottom_to_top"])
            order = [x for _, x in allf]
            okp = len(order) == e["pxo"]["frames"]
            for fi, x in enumerate(order, start=1):
                lays = [np.frombuffer(z.read(f"image_data/frames/{fi}/layer_{li}"), np.uint8).reshape(H, W, 4) for li in range(1, nl)]
                okp &= np.array_equal(over(lays), decode(files[x["file"]]))
            ck(f"{d} PXO layer cels recompose to every frame PNG", okp, e["pxo"]["frames"])
    st = {d: decode(files[source["directions"][d]["static"]["file"]]) for d in DIRS}
    ck("south static is the exact source PNG bytes", sha(files[source["directions"]["south"]["static"]["file"]]) == SRC_PNG_SHA and
       sha(rb(rp(SRC_PNG))) == SRC_PNG_SHA)
    ck("four statics pairwise distinct", len({st[d].tobytes() for d in DIRS}) == 4)
    ck("east is not a mirror of west (handedness authored)", not np.array_equal(st["east"], mirror(st["west"])))
    ck("north is not a mirror of south", not np.array_equal(st["north"], mirror(st["south"])))
    teal, brass = {RGB["B"], RGB["b"], RGB["n"]}, RGB["Y"]
    for d in DIRS:
        a = st[d]; cols = [tuple(c) for c in a[..., :3].reshape(-1, 3)]
        top = a[8, :, 3] == 255
        head_teal = sum(1 for y in range(8, 36) for x in range(W) if a[y, x, 3] and tuple(a[y, x, :3]) in teal)
        ck(f"{d} identity cues: brass antenna tip on row 8, teal in head band, radio/tablet steel", top.any() and
           tuple(a[8, np.nonzero(top)[0][0], :3]) == brass and head_teal >= 6 and
           sum(1 for c in cols if c in (RGB["v"], RGB["w"])) >= 20, head_teal)
    pk = json.loads(files[source["package"]["sprite_set"]])
    ok = pk["schema"] == "worlds-between.exploration-sprite-set.v1" and pk["actor_id"] == "zhao-ling" and \
        set(pk["actions"]) == {"idle", "walk"} and all(set(pk["actions"][a]) == set(DIRS) for a in pk["actions"])
    durs = [f["duration_ms"] for a in pk["actions"].values() for v in a.values() for f in v]
    ok &= all(isinstance(x, int) and 40 <= x <= 2000 for x in durs)
    paths = [f["file"] for a in pk["actions"].values() for v in a.values() for f in v]
    ok &= all(not p.startswith("/") and ".." not in p and (PKG_REL + "/" + p) in files for p in paths)
    ok &= all(files[PKG_REL + "/png/" + p.rsplit("/", 1)[-1]] == files[OUT_REL + "/png/" + p.rsplit("/", 1)[-1]] for p in paths)
    ck("runtime package schema/actor/actions/durations/relative lossless PNG copies", ok, len(paths))
    reg = json.loads(files[source["package"]["registry"]])
    ck("registry schema + zhao-ling -> set manifest", reg["schema"] == "worlds-between.exploration-sprite-set-registry.v1" and
       (PKG_REL + "/" + reg["actors"]["zhao-ling"]) == source["package"]["sprite_set"])
    ck("no .gdignore in runtime package", not os.path.exists(_fs(rp(PKG_REL + "/.gdignore"))) and not os.path.exists(_fs(rp(PKG_REL + "/png/.gdignore"))))
    for d in ("west", "east"):
        c = source["contact_check"][d]
        ck(f"{d} sole rows grounded on planted pairs (slip disclosed, not gated)", all(SOLE in r["sole_rows"] or SOLE + 1 in r["sole_rows"] for r in c["pairs"]),
           {"max_abs_slip_source": c["max_abs_slip_source"]})
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["build", "check"])
    ap.add_argument("--pixelorama")
    a = ap.parse_args()
    fs, files, source = build_all()
    if a.mode == "build":
        mx.write_all(files)
        print(f"WROTE {len(files)} files")
        return 0
    fails, n = [], 0
    for rel, b in files.items():
        n += 1
        try:
            if rb(rp(rel)) != b:
                fails.append(f"rebuild differs {rel}")
        except OSError:
            fails.append(f"missing {rel}")
    print(f"REBUILD {n - len(fails)}/{n}")
    res = {"tool_sha256_text_lf_v1": source["tool"]["sha256_text_lf_v1"], "rebuild": {"checked": n, "fails": list(fails)}}
    sc = source_checks(fs, files, source)
    res["source_checks"] = sc
    for c in sc:
        if not c["pass"]:
            fails.append("source " + c["check"])
    print(f"SOURCE {sum(c['pass'] for c in sc)}/{len(sc)}")
    res["native"] = []
    if a.pixelorama:
        for d in DIRS:
            e = source["directions"][d]
            order = [e["static"]] + e["idle"] + e["walk"] + [s for p in range(NPH) for s in e["stop_bridges"][f"phase{p}"] if "file" in s]
            tmp = tempfile.mkdtemp(prefix="wb-zx25-")
            try:
                p, outs = mx.pixelorama_export(a.pixelorama, rp(e["pxo"]["file"]), tmp, False)
                diag = [ln for ln in (p.stdout + p.stderr).splitlines() if any(t in ln for t in ("ERROR", "SCRIPT ERROR", "WARNING"))]
                names = sorted(outs)
                eqn = sum(1 for i in range(min(len(names), len(order))) if np.array_equal(decode(outs[names[i]]), decode(files[order[i]["file"]])))
                r = {"dir": d, "exit": p.returncode, "frames_exported": len(names), "frames_expected": len(order),
                     "all_frames_equal": f"{eqn}/{len(order)}", "script_error": any("SCRIPT ERROR" in ln for ln in diag),
                     "diagnostics": diag[:12]}
                res["native"].append(r)
                print(json.dumps(r))
                if p.returncode != 0 or len(names) != len(order) or eqn != len(order) or r["script_error"]:
                    fails.append(f"native {d}")
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
    else:
        fails.append("native Pixelorama export not run")
    res["fails"] = fails
    print("RESULT", "PASS" if not fails else "FAIL", json.dumps(fails[:12]))
    out = rp(f"{OUT_REL}/{fname('check-result', 'json')}")
    with open(_fs(out), "wb") as f:
        f.write((json.dumps(res, indent=2) + "\n").encode())
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
