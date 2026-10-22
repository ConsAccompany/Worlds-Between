"""Liang Xu four-direction EXPLORATION SOURCE author (lexplore28, UNAPPROVED technical source).

Statics, 4-frame idle loops, 12-phase walk cycles (40 ms reference) and phase-aware stop bridges for
south/west/north/east at the existing Liang contract (80x112 cell, density 2, pivot 40/104, 96-texel body).

- south: the Liang south pilot MAP/ROLE grids (v01 baa30d44) are the exact neutral role layers; static and
  idle f00 are the source PNG bytes. The source 'accessory' role is split into 'belt-placket' and 'board'
  (adjacent in the stack, composite unchanged). idle/walk/stop = role-layer offsets, a per-leg column split
  at x=40 (rows >= 82 rise) and a 1-texel coat-hem sway; no repaint.
- north: back view from the south role silhouettes mirrored x'=80-x (silver streak stays on their right, the
  board stays in their left hand) refilled as back surfaces: dark hair + pinned top-knot with a copper pin,
  high collar band, split long-coat back vent, board back panel with copper frame.
- west: authored side puppet, their LEFT side to the viewer: board held edge-on in the near hand, copper
  placket at the front edge, split coat tail behind; the silver streak shows only where it crosses the crown.
- east: authored side puppet with their RIGHT side to the viewer (silver temple streak, board in the far hand
  peeking past the coat front), then mirrored x'=80-x. NOT a mirror of west; light becomes upper-right
  (limitation).

Character-agnostic helpers (raster primitives, pose tables, PXO/ORA writers, guides, contact/stop reports,
Pixelorama export) are imported from the mexplore23 author, which this tool does not modify.

Usage:  python -X utf8 -I <tool> build|check [--pixelorama EXE]
Writes only NEW files under outputs/lexplore28 and game/data/lexplore28.
"""
import argparse, importlib.util, json, math, os, shutil, sys, tempfile, zipfile, io
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_MX = os.path.join(_HERE, "rpg-2-star-ocean-the-second_protagonist-male_explore-4dir-source-author_unapproved-mexplore23-v01_20261021-162551-6e3b1a7d.py")
_spec = importlib.util.spec_from_file_location("wb_mexplore23_helpers", _MX)
mx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mx)
_LX = os.path.join(_HERE, "rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-build-and-check_unapproved-v01_20261016-140940-6a60848d.py")
_spec = importlib.util.spec_from_file_location("wb_liang_south_v01", _LX)
lx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lx)
_fs, rp, rb, sha, sha_text, png_bytes, decode, blank = mx._fs, mx.rp, mx.rb, mx.sha, mx.sha_text, mx.png_bytes, mx.decode, mx.blank
shift, mirror, over, lerp_pose = mx.shift, mx.mirror, mx.over, mx.lerp_pose

SRC_DIR = "game/assets/characters/liang-xu/south-idle-static-pilot-unapproved-v01"
SRC_PNG = SRC_DIR + "/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot_unapproved-v01_20261016-140940-46a036ed.png"
SRC_PXO = SRC_DIR + "/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-editable_unapproved-v01_20261016-140940-65edcfd2.pxo"
SRC_PNG_SHA = "9fee901809d33128839779cc1e926fc314f4d92fd11baa3b857d4cffebfe38ab"
SRC_PXO_SHA = "26024bdd2c2d16b29c6a0e5df63a17038d29829506f505f0ca37f13a73ff09ee"
STAMP = "20261021-194350"
RUN = "3acdbd6e"
OUT_REL = "outputs/lexplore28"
PKG_REL = "game/data/lexplore28"
PFX = "rpg-2-star-ocean-the-second_liang-xu_explore"
VAR = "unapproved-lexplore28-v01"
ACTOR = "liang-xu"
W, H, PIN, SOLE = mx.W, mx.H, mx.PIN, mx.SOLE
ZIP_DT = (2026, 10, 21, 19, 43, 50)
mx.ZIP_DT = ZIP_DT          # in-process only: zip entry dates for this run's PXO/ORA
DIRS, NPH, FRAME_MS, STOP_K, IDLE_MS, D_PHASE = mx.DIRS, mx.NPH, mx.FRAME_MS, mx.STOP_K, mx.IDLE_MS, mx.D_PHASE
NORMAL_SPEED_LOGICAL = 140.0

PAL = {k: "#" + v for k, v in lx.PAL.items()}       # Liang named ramps, unchanged
RGB = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in PAL.items()}
YY, XX = np.arange(H)[:, None], np.arange(W)[None, :]


class LCanvas(mx.Canvas):
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


def lshade(mask, base, lit, dark, rim=None, litfrac=0.3, darkfrac=0.25):
    c = LCanvas()
    ys = np.nonzero(mask.any(1))[0]
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
SOUTH_LAYERS = ["hair-back", "arm-far", "boots", "legs", "belt-placket", "board", "torso-coat", "arm-near",
                "head-face", "hair-front"]
BOARD_X = 51        # accessory texels at cell x >= 51 are the folding board; the rest is belt/placket


def load_src():
    png, pxo = rb(rp(SRC_PNG)), rb(rp(SRC_PXO))
    assert sha(png) == SRC_PNG_SHA and sha(pxo) == SRC_PXO_SHA, "Liang south source hash drift"
    lx.validate_maps()
    ox, oy = lx.GRID_OFFSET
    lay = {}
    for name, key in lx.ROLE_LAYERS:
        a = blank()
        for gy, (mrow, rrow) in enumerate(zip(lx.MAP, lx.ROLE)):
            for gx, (mk, rk) in enumerate(zip(mrow, rrow)):
                if rk == key and mk != ".":
                    a[gy + oy, gx + ox, :3] = RGB[mk]; a[gy + oy, gx + ox, 3] = 255
        lay[name] = a
    acc = lay.pop("accessory")
    lay["board"] = acc.copy(); lay["board"][:, :BOARD_X] = 0
    lay["belt-placket"] = acc.copy(); lay["belt-placket"][:, BOARD_X:] = 0
    src = decode(png)
    assert np.array_equal(over([lay[n] for n in SOUTH_LAYERS]), src), "role layers != source PNG"
    return lay, src, png


LIFT_ROW = 82       # front/back step: shin + boot rise; thigh and coat stay
HEM_ROW = 74        # coat rows >= 74 sway by the 'skirt' pose value


def lift_legs(a, pose):
    parts = []
    for sl, key in ((slice(0, 40), "ll"), (slice(40, W), "rl")):
        leg = blank(); leg[:, sl] = a[:, sl]
        upper = leg.copy(); upper[LIFT_ROW:] = 0
        lower = leg.copy(); lower[:LIFT_ROW] = 0
        parts += [upper, shift(lower, 0, -pose.get(key, 0))]
    return over(parts)


def sway_hem(a, dx):
    if not dx:
        return a
    top, hem = a.copy(), a.copy()
    top[HEM_ROW:] = 0; hem[:HEM_ROW] = 0
    return over([top, shift(hem, dx, 0)])


def render_fb(base, names, pose, arm_l, arm_r):
    up, hd = pose.get("bob", 0), pose.get("head", 0)
    out = []
    for n in names:
        a = base[n]
        if n in ("legs", "boots"):
            a = lift_legs(a, pose)
        elif n in ("hair-back", "head-face", "hair-front", "head-back", "hair", "collar-back"):
            a = shift(a, 0, hd)
        elif n == arm_l:
            a = shift(a, 0, up + pose.get("arm_l", 0))
        elif n in arm_r:
            a = shift(a, 0, up + pose.get("arm_r", 0) + (pose.get("pack", 0) if n.startswith("board") else 0))
        elif n in ("torso-coat", "coat-back"):
            a = sway_hem(shift(a, 0, up), pose.get("skirt", 0))
        else:
            a = shift(a, 0, up)
        out.append((n, clip_floor(a)))
    return out


def render_south(src, pose):
    return render_fb(src, SOUTH_LAYERS, pose, "arm-far", ("arm-near", "board"))


# ----------------------------------------------------------------------------- north (back view)
NORTH_LAYERS = ["legs", "boots", "coat-back", "board-back", "arm-left", "arm-right", "head-back", "hair",
                "collar-back"]


def north_base(src):
    m = lambda n: mirror(src[n])[..., 3] == 255
    base = {}
    mm = m("legs")
    c = lshade(mm, "T", "T", "t")
    base["legs"] = clip_floor(c.outline().a)
    mm = m("boots")
    c = lshade(mm, "o", "O", "q", rim="O")
    for x in range(W):
        col = np.nonzero(mm[:, x])[0]
        if len(col):
            c.px(x, col.max(), "q")
    base["boots"] = clip_floor(c.outline().a)
    tm = m("torso-coat") | m("belt-placket")
    c = lshade(tm, "B", "A", "D")
    for y in range(56, 59):                                     # half-belt across the back
        for x in np.nonzero(tm[y])[0][2:-2]:
            c.px(x, y, "C" if y < 58 else "D")
    c.px(36, 57, "R"); c.px(43, 57, "R")                        # copper belt studs
    for y in range(44, 72):                                     # centre back seam
        if tm[y, 40]:
            c.px(40, y, "C")
    vent = tm & (YY >= 72) & (XX >= 39) & (XX <= 41)            # split long-coat back vent
    c.a[vent] = 0
    for y in range(72, 98):
        for x in (38, 42):
            if tm[y, x]:
                c.px(x, y, "D")
    base["coat-back"] = c.outline().a
    bm = m("board")
    c = lshade(bm, "u", "r", "u")
    ys, xs = np.nonzero(bm.any(1))[0], np.nonzero(bm.any(0))[0]
    for y in ys:                                                # copper frame round the back panel
        for x in np.nonzero(bm[y])[0]:
            if y in (ys.min(), ys.max()) or x in (xs.min(), xs.max()):
                c.px(x, y, "R")
    c.px((xs.min() + xs.max()) // 2, (ys.min() + ys.max()) // 2, "Q")   # hinge pin
    for x in range(xs.min() + 1, xs.max()):
        c.px(x, (ys.min() + ys.max()) // 2 + 1, "r")            # fold line
    base["board-back"] = c.outline().a
    for src_n, out_n in (("arm-far", "arm-right"), ("arm-near", "arm-left")):
        am = m(src_n)
        c = lshade(am, "B", "A", "D")
        ys = np.nonzero(am.any(1))[0]
        for y in range(ys.max() - 3, ys.max() + 1):
            for x in np.nonzero(am[y])[0]:
                c.px(x, y, "O" if y < ys.max() else "o")       # gloves
        base[out_n] = c.outline().a
    hm = m("head-face")
    c = LCanvas()
    for y, x in zip(*np.nonzero(hm)):
        c.px(x, y, "e" if y > 33 else "f")
    base["head-back"] = c.outline().a
    hr = m("hair-front") | m("hair-back") | (hm & (YY <= 31))
    c = lshade(hr, "2", "1", "3", litfrac=0.25)
    for y, x in zip(*np.nonzero(hr & (XX >= 45) & (YY >= 19) & (YY <= 33))):
        c.px(x, y, "S" if x < 48 else "s")                     # silver streak: their right = viewer right from behind
    for y, x in zip(*np.nonzero(hr & (XX >= 44) & (XX <= 46) & (YY >= 17) & (YY <= 18))):
        c.px(x, y, "W")
    for x in range(36, 45):                                     # copper pin through the top-knot
        c.px(x, 13, "R")
    c.px(35, 13, "Q"); c.px(45, 13, "r")
    base["hair"] = c.outline().a
    c = LCanvas()                                               # high collar band over the nape
    c.poly([(32, 35), (48, 35), (49, 39.99), (31, 39.99)], "C")
    for x in range(32, 49):
        c.px(x, 35, "B"); c.px(x, 39, "D")
    base["collar-back"] = c.outline().a
    return base


def render_north(base, pose):
    return render_fb(base, NORTH_LAYERS, pose, "arm-right", ("arm-left", "board-back"))


# ----------------------------------------------------------------------------- side puppet (drawn facing -x)
ANKLE_UP = 5
LEG = 17.4      # Liang thigh = shin (source texels); hip row 63 to ankle row 97
HIP_Y = 63
IK_LOG = []


def ik(hx, hy, ax, ay, l1=LEG, l2=LEG):
    dx, dy = ax - hx, ay - hy
    IK_LOG.append(math.hypot(dx, dy) - (l1 + l2))
    d = min(math.hypot(dx, dy), l1 + l2 - 1e-6)
    a = math.atan2(dy, dx)
    b = math.acos((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))
    return hx + l1 * math.cos(a + b), hy + l1 * math.sin(a + b)


def draw_leg(ax_, lift, hip, near):
    c = LCanvas()
    hx, hy = hip
    ay = SOLE - 1 - ANKLE_UP - lift
    kx, ky = ik(hx, hy, ax_, ay)
    tr, trs = ("T", "t") if near else ("t", "D")
    c.seg(hx, hy, kx, ky, 8, trs)                               # straight trousers
    c.seg(hx - 0.6, hy, kx - 0.6, ky, 5, tr)
    c.seg(kx, ky, ax_, ay, 7, trs)
    c.seg(kx - 0.5, ky, ax_ - 0.5, ay, 4, tr)
    t = 9 / max(math.hypot(kx - ax_, ky - ay), 1)
    bx, by = ax_ + (kx - ax_) * t, ay + (ky - ay) * t
    c.seg(bx, by, ax_, ay, 7, "o")                              # tall boot shaft
    c.seg(bx - 0.5, by, bx + 0.5, by, 7, "O" if near else "o")  # boot cuff
    sole = ay + ANKLE_UP
    c.poly([(ax_ + 4, ay - 1), (ax_ - 3, ay - 1), (ax_ - 7, sole - 2), (ax_ - 7, sole + 0.99), (ax_ + 4, sole + 0.99)], "o")
    if near:
        c.px(ax_ - 4, sole - 2, "O"); c.px(ax_ - 5, sole - 1, "O"); c.px(ax_ - 1, ay, "O")
    for x in range(int(ax_ - 7), int(ax_ + 4) + 1):
        c.px(x, sole, "q")
    return c.outline().a


def draw_arm(sh, ang, near):
    c = LCanvas()
    sx, sy = sh
    ex, ey = sx + 12 * math.sin(-ang), sy + 12 * math.cos(ang)
    fa = ang - 0.35 if ang < 0 else ang - 0.15
    hx, hy = ex + 10 * math.sin(-fa), ey + 10 * math.cos(fa)
    sl, sd = ("A", "C") if near else ("C", "D")
    c.seg(sx, sy, ex, ey, 7, sd)                                # coat sleeve
    c.seg(sx - 0.6, sy, ex - 0.6, ey, 4, sl)
    c.seg(ex, ey, hx, hy, 6, sd)
    c.seg(ex - 0.5, ey, hx - 0.5, hy, 3, sl)
    c.ell(hx, hy + 2, 2.4, 2.4, "O" if near else "o")           # glove
    return c.outline().a, (hx, hy + 2)


def draw_board(hand, near):
    """Folding tactical board held edge-on: copper frame edge + a sliver of the screen face."""
    c = LCanvas()
    hx, hy = hand
    c.poly([(hx - 2, hy - 9), (hx + 2.99, hy - 9), (hx + 2.99, hy + 8.99), (hx - 2, hy + 8.99)], "R" if near else "r")
    c.poly([(hx + 1, hy - 8), (hx + 2.99, hy - 8), (hx + 2.99, hy + 7.99), (hx + 1, hy + 7.99)], "u")
    c.poly([(hx - 4, hy - 8), (hx - 2.01, hy - 8), (hx - 2.01, hy + 7.99), (hx - 4, hy + 7.99)], "g")
    c.px(hx - 4, hy - 7, "G"); c.px(hx - 3, hy - 6, "G")
    c.px(hx - 2, hy, "Q"); c.px(hx - 1, hy, "Q")                 # hinge
    c.ell(hx, hy + 1, 2.0, 2.0, "O" if near else "o")           # gripping glove over the frame
    return c.outline().a


def render_side(pose, near):
    """near='left': their left side to the viewer (west). near='right': their right side (east, pre-mirror)."""
    b, hd, sk = pose.get("bob", 0), pose.get("head", 0), pose.get("skirt", 0)
    hip = (40.5, HIP_Y + b)
    o = {}
    o["leg-near"] = draw_leg(pose["ax"], pose["al"], hip, True)
    o["leg-far"] = draw_leg(pose["bx"] + 1, pose["bl"], (hip[0] + 1, hip[1]), False)
    board_arm = "arm-near" if near == "left" else "arm-far"
    an = pose["arm_n"] * (0.45 if board_arm == "arm-near" else 1.0)
    af = pose["arm_f"] * (0.45 if board_arm == "arm-far" else 1.0)
    o["arm-near"], hand_n = draw_arm((41, 41 + b), an, True)
    o["arm-far"], hand_f = draw_arm((43, 41 + b), af, False)
    c = LCanvas()                                               # long coat: split tail behind
    c.poly([(42, 62 + b), (50, 62 + b), (53 + sk, 95), (44 + sk, 95)], "C")      # back tail
    c.poly([(50, 62 + b), (51, 62 + b), (54 + sk, 95), (52 + sk, 95)], "D")
    for x in range(int(44 + sk), int(54 + sk)):
        c.px(x, 95, "D")
    o["coat-back-tail"] = c.outline().a
    c = LCanvas()
    c.poly([(34, 62 + b), (42, 62 + b), (40 - sk, 93), (32 - sk, 93)], "B")     # front tail
    c.poly([(34, 62 + b), (36, 62 + b), (34 - sk, 93), (32 - sk, 93)], "A")
    for x in range(int(32 - sk), int(41 - sk)):
        c.px(x, 93, "C")
    o["coat-front-tail"] = c.outline().a
    tc = LCanvas()
    tc.poly([(36, 37 + b), (46, 37 + b), (49, 44 + b), (50, 63 + b), (34, 63 + b), (34, 44 + b)], "B")
    tc.poly([(36, 37 + b), (39, 37 + b), (38, 63 + b), (34, 63 + b), (34, 44 + b)], "A")
    tc.poly([(47, 40 + b), (49, 44 + b), (50, 63 + b), (47, 63 + b)], "C")
    for y in range(39, 56):                                     # copper placket at the front edge
        tc.px(34 if y > 43 else 35, y + b, "R")
    tc.px(35, 45 + b, "Q"); tc.px(35, 50 + b, "Q")
    for x in range(34, 51):                                     # belt
        tc.px(x, 57 + b, "o"); tc.px(x, 58 + b, "q")
    tc.px(35, 57 + b, "R"); tc.px(36, 57 + b, "Q")
    o["torso-coat"] = tc.outline().a
    c = LCanvas()                                               # high navy collar with copper edge
    c.poly([(36, 33 + hd), (45, 33 + hd), (46, 39 + b), (36, 39 + b)], "n")
    c.poly([(36, 33 + hd), (38, 33 + hd), (38, 39 + b), (36, 39 + b)], "N")
    for x in range(36, 46):
        c.px(x, 33 + hd, "R")
    o["collar"] = c.outline().a
    fl = pose.get("flap", 0)                                    # idle/walk: board settles 1 texel in the grip
    board = draw_board((hand_n[0], hand_n[1] + fl) if near == "left" else (hand_f[0] - 11, hand_f[1] - 2 + fl), near == "left")
    c = LCanvas()                                               # profile face toward -x
    c.poly([(34, 18 + hd), (42, 18 + hd), (43, 34 + hd), (38, 36 + hd), (35, 34 + hd), (34, 31 + hd),
            (33, 29 + hd), (31.5, 27 + hd), (33, 25 + hd), (34, 21 + hd)], "F")
    c.poly([(40, 18 + hd), (43, 18 + hd), (43, 34 + hd), (40, 35 + hd)], "f")
    c.poly([(35, 32 + hd), (38, 32 + hd), (38, 36 + hd), (36, 35 + hd)], "e")
    c.px(34, 24 + hd, "y"); c.px(35, 24 + hd, "y"); c.px(36, 23 + hd, "y")   # brow
    c.px(34, 25 + hd, "K"); c.px(35, 25 + hd, "y")                           # eye
    c.px(32, 27 + hd, "e"); c.px(34, 31 + hd, "d"); c.px(35, 31 + hd, "d")   # nose shade, mouth
    c.px(38, 28 + hd, "e"); c.px(37, 29 + hd, "e")                           # cheek line (age)
    o["head-face"] = c.outline().a
    c = LCanvas()                                               # pinned dark hair swept back to a top-knot
    c.ell(42, 23 + hd, 9.5, 8.5, "2")
    c.ell(40, 20 + hd, 7.5, 5.5, "1")
    c.poly([(32, 20 + hd), (38, 15.5 + hd), (40, 22 + hd), (35, 21 + hd), (33, 22 + hd)], "2")
    c.poly([(42, 24 + hd), (51, 24 + hd), (50, 33 + hd), (43, 33 + hd)], "3")
    c.ell(46, 13 + hd, 4.5, 3.6, "2")                           # top-knot
    c.ell(45, 12 + hd, 2.6, 1.8, "1")
    for x in range(40, 52):
        c.px(x, 13 + hd, "R")                                   # copper pin
    c.px(39, 13 + hd, "Q")
    streak = [(37, 16), (38, 16), (39, 16), (40, 17), (41, 17), (42, 17), (43, 18)]   # crosses the crown
    if near == "right":                                         # right temple: full silver sweep
        streak += [(x, y) for y in range(19, 31) for x in range(41, 46) if (x - 41) <= (y - 17) // 3 + 2]
        streak += [(42, 31), (43, 31), (43, 32)]
    for x, y in streak:
        c.px(x, y + hd, "S" if (x + y) % 4 else "W")
    face = o["head-face"][..., 3] == 255
    cut = face & (YY >= 22 + hd) & (XX <= 41)
    c.a[cut] = 0
    c.outline()
    c.a[cut & (c.a[..., 3] == 255)] = o["head-face"][cut & (c.a[..., 3] == 255)]
    o["hair"] = c.a
    o["board"] = board
    if near == "left":
        order = ["arm-far", "coat-back-tail", "leg-far", "leg-near", "torso-coat", "coat-front-tail", "collar",
                 "head-face", "hair", "arm-near", "board"]
    else:
        order = ["board", "arm-far", "coat-back-tail", "leg-far", "leg-near", "torso-coat", "coat-front-tail",
                 "collar", "head-face", "hair", "arm-near"]
    return [(n, clip_floor(o[n])) for n in order]


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
        IK_LOG.clear()
        idle = [(rend(q), q) for q in idlep]
        walk = [(rend(q), q) for q in walkp]
        stretch = list(IK_LOG)
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
        out[d] = {"idle": idle, "walk": walk, "stop": stop,
                  "ik_overreach_max_source": round(max(stretch), 3) if stretch else None}
    return out


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
            e["grounded_feet_source"] = mx.sole_points(lay, d)
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
                e["grounded_feet_source"] = mx.sole_points(lay, d)
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


def speed_disclosure():
    per_phase_world_src = NORMAL_SPEED_LOGICAL * FRAME_MS / 1000.0 * 2
    return {"normal_speed_logical_px_s": NORMAL_SPEED_LOGICAL,
            "declared_cycle_speed_logical_px_s_at_40ms": D_PHASE / 2 / (FRAME_MS / 1000.0),
            "world_advance_per_40ms_phase_source_at_normal_speed": per_phase_world_src,
            "side_planted_foot_world_drift_per_phase_source_if_phase_clock_40ms": round(per_phase_world_src - D_PHASE, 3),
            "side_planted_foot_world_drift_per_phase_logical_if_phase_clock_40ms": round((per_phase_world_src - D_PHASE) / 2, 3),
            "side_planted_foot_world_drift_per_stance_logical_if_phase_clock_40ms": round((per_phase_world_src - D_PHASE) / 2 * 6, 3),
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
    sprite_set = {"schema": "worlds-between.exploration-sprite-set.v1", "set_id": f"{ACTOR}-exploration-source-{STAMP}-{RUN}",
                  "actor_id": ACTOR, "density": 2, "frame_size": [W, H], "pivot": list(PIN),
                  "status": "UNAPPROVED technical source; not wired into any default; frame paths are relative to this JSON",
                  "actions": {"idle": {d: [entry(e) for e in man[d]["idle"]] for d in DIRS},
                              "walk": {d: [entry(e) for e in man[d]["walk"]] for d in DIRS}}}
    stop = {"schema": "worlds-between.exploration-stop-transition.supplemental.v1", "actor_id": ACTOR,
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
    registry = {"schema": "worlds-between.exploration-sprite-set-registry.v1", "actors": {ACTOR: set_name}}
    files[reg_rel] = (json.dumps(registry, indent=2) + "\n").encode()
    files[f"{OUT_REL}/{fname('loader-ready', 'json')}"] = (json.dumps(
        {"actor_id": ACTOR, "registry": reg_rel, "sprite_set": f"{PKG_REL}/{set_name}",
         "registry_sha256": sha(files[reg_rel]), "sprite_set_sha256": sha(ss_b),
         "status": "UNAPPROVED technical source; not runtime default"}, indent=2) + "\n").encode()
    weak = {"side_ik_overreach_max_source": {d: fs[d]["ik_overreach_max_source"] for d in ("west", "east")},
            "notes": ["side stance span 24 source texels exceeds the 34.8-texel leg reach at the extremes; the knee "
                      "solve clamps and the shin segment stretches by the listed overreach (straight-leg look at contact)",
                      "front/back walk is an in-place shin/boot lift (no foreshortened stride); coat hem sways 1 texel",
                      "side views are new puppet geometry, not the hand-placed south texel quality; face/hair at 48 px "
                      "not inspected in-game in this batch",
                      "east light direction becomes upper-right after the mirror",
                      "board is edge-on in side views (thin 5-7 texel copper slab), only the south/north show its face/back",
                      "south cosmetic revision bucket and visual audit remain open (deferred, not waived)"]}
    source = {"project": "Worlds Between", "visual_id": ACTOR, "run_id": RUN, "variant": VAR,
              "status": "UNAPPROVED technical source; art not approved; not runtime-integrated; no default changed",
              "task_ids": ["content.char.liang-xu.static-west", "content.char.liang-xu.static-north",
                           "content.char.liang-xu.static-east", "content.char.liang-xu.idle-anim",
                           "content.char.liang-xu.walk-south", "content.char.liang-xu.walk-west",
                           "content.char.liang-xu.walk-north", "content.char.liang-xu.walk-east"],
              "contract": {"cell": [W, H], "pivot": list(PIN), "density": 2, "body_texels": 96, "logical_height": 48,
                           "sole_row": SOLE, "alpha": "binary", "filter": "nearest"},
              "source_inputs": {"liang_south_png": {"file": SRC_PNG, "sha256": SRC_PNG_SHA, "hash": "sha256-bytes"},
                                "liang_south_pxo": {"file": SRC_PXO, "sha256": SRC_PXO_SHA, "hash": "sha256-bytes"},
                                "liang_south_build_tool_maps": {"file": "tools/" + os.path.basename(_LX), "sha256_text_lf_v1": sha_text(rb(_LX))}},
              "methods": {"south": "exact Liang south MAP/ROLE role layers (accessory split into belt-placket + board); static and idle f00 are the source PNG bytes; idle/walk/stop = role-layer offsets + per-leg column split at x=40 (rows>=82 rise) + 1-texel hem sway",
                          "north": "back view: south role silhouettes mirrored x'=80-x refilled as back surfaces (pinned top-knot + copper pin, silver streak on their right, high collar band, split-coat vent, board back panel)",
                          "west": "authored side puppet, their left side to viewer: board edge-on in the near (left) hand, copper placket front edge, split coat tails",
                          "east": "authored side puppet, their right side to viewer (silver temple sweep, board in the far left hand behind the coat front), mirrored x'=80-x; light becomes upper-right (limitation)"},
              "reused_helpers": {"file": "tools/" + os.path.basename(_MX), "sha256_text_lf_v1": sha_text(rb(_MX))},
              "walk_model": {"phases": NPH, "frame_ms_reference": FRAME_MS, "declared_move_per_phase_source": D_PHASE,
                             "contacts": "side: foot A planted p0-p5, foot B planted p6-p11; front/back: L lifted p1-p5, R lifted p7-p11",
                             "pure_distance_driver": "phase = floor(distance_logical / 2) mod 12"},
              "idle_model": {"frames": 4, "duration_ms": IDLE_MS, "neutral_endpoint": "f00 == static (exact)"},
              "directions": man, "contact_check": contact, "normal_speed_drift": speed_disclosure(), "stop_check": stops,
              "measured_weaknesses": weak,
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
        idl = {decode(files[x["file"]]).tobytes() for x in e["idle"]}
        ck(f"{d} idle frames are not duplicate stills", len(idl) >= 3, len(idl))
        low = [decode(files[x["file"]])[78:104] for x in e["walk"]]
        ck(f"{d} walk lower body changes across phases (not bob-only)", len({b.tobytes() for b in low}) >= 6, len({b.tobytes() for b in low}))
        ora = files[e["ora"]["file"]]
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
    ck("south idle f00 is the exact source PNG bytes", source["directions"]["south"]["idle"][0]["sha256"] == SRC_PNG_SHA)
    ck("four statics pairwise distinct", len({st[d].tobytes() for d in DIRS}) == 4)
    ck("east is not a mirror of west (handedness authored)", not np.array_equal(st["east"], mirror(st["west"])))
    ck("north is not a mirror of south", not np.array_equal(st["north"], mirror(st["south"])))
    copper, silver, screen = {RGB[k] for k in "QRru"}, {RGB[k] for k in "WSs"}, {RGB[k] for k in "Gg"}
    for d in DIRS:
        a = st[d]
        cnt = lambda ks, y0=0, y1=H: int(sum(1 for y in range(y0, y1) for x in range(W) if a[y, x, 3] and tuple(a[y, x, :3]) in ks))
        need_screen = d != "north"
        ok = cnt(copper) >= 12 and cnt(silver, 8, 40) >= 5 and (cnt(screen) >= 2 if need_screen else True)
        ck(f"{d} identity cues: copper placket/board, silver streak in head rows, board screen (not north)", ok,
           {"copper": cnt(copper), "silver_head": cnt(silver, 8, 40), "screen": cnt(screen)})
    pk = json.loads(files[source["package"]["sprite_set"]])
    ok = pk["schema"] == "worlds-between.exploration-sprite-set.v1" and pk["actor_id"] == ACTOR and \
        set(pk["actions"]) == {"idle", "walk"} and all(set(pk["actions"][a]) == set(DIRS) for a in pk["actions"])
    durs = [f["duration_ms"] for a in pk["actions"].values() for v in a.values() for f in v]
    ok &= all(isinstance(x, int) and 40 <= x <= 2000 for x in durs)
    paths = [f["file"] for a in pk["actions"].values() for v in a.values() for f in v]
    ok &= all(not p.startswith("/") and ".." not in p and (PKG_REL + "/" + p) in files for p in paths)
    ok &= all(files[PKG_REL + "/png/" + p.rsplit("/", 1)[-1]] == files[OUT_REL + "/png/" + p.rsplit("/", 1)[-1]] for p in paths)
    ck("runtime package schema/actor/actions/durations/relative lossless PNG copies", ok, len(paths))
    reg = json.loads(files[source["package"]["registry"]])
    ck("registry schema + liang-xu -> set manifest", reg["schema"] == "worlds-between.exploration-sprite-set-registry.v1" and
       (PKG_REL + "/" + reg["actors"][ACTOR]) == source["package"]["sprite_set"])
    ck("no .gdignore in runtime package", not os.path.exists(_fs(rp(PKG_REL + "/.gdignore"))) and not os.path.exists(_fs(rp(PKG_REL + "/png/.gdignore"))))
    ck("no 32x48 placeholder input", all("32x48" not in v["file"] for v in source["source_inputs"].values()))
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
            tmp = tempfile.mkdtemp(prefix="wb-lx28-")
            try:
                p, outs = mx.pixelorama_export(a.pixelorama, rp(e["pxo"]["file"]), tmp, False)
                diag = [ln for ln in (p.stdout + p.stderr).splitlines() if any(t in ln for t in ("ERROR", "SCRIPT ERROR", "WARNING"))]
                names = sorted(outs)
                eqn = sum(1 for i in range(min(len(names), len(order))) if np.array_equal(decode(outs[names[i]]), decode(files[order[i]["file"]])))
                r = {"dir": d, "exit": p.returncode, "frames_exported": len(names), "frames_expected": len(order),
                     "all_frames_equal": f"{eqn}/{len(order)}", "script_error": any("SCRIPT ERROR" in ln for ln in diag),
                     "diagnostics_reported_separately": diag[:12]}
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
    os.makedirs(_fs(os.path.dirname(out)), exist_ok=True)
    with open(_fs(out), "wb") as f:
        f.write((json.dumps(res, indent=2) + "\n").encode())
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
