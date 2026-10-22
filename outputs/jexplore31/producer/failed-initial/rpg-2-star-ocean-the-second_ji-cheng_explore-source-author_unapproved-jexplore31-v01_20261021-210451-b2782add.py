"""Ji Cheng (纪澄) four-direction EXPLORATION SOURCE author (jexplore31, UNAPPROVED technical source).

Statics, 4-frame idle loops, 12-phase walk cycles (40 ms reference) and phase-aware stop bridges for
south/west/north/east at the existing Ji Cheng contract (80x112 cell, density 2, pivot 40/104, 96-texel body,
48 logical px at 0.5).

- south: the Ji Cheng south pilot MAP/ROLE grids (v01 04cd6a26) are the exact neutral 13 role layers; static and
  idle f00 are the source PNG bytes. idle/walk/stop = role-layer offsets, a per-leg column split at x=40 (rows
  >= 84 rise: shin + buckled boot), a 1-texel coat-hem sway; the raised magnifier arm moves at half the arm
  offset; the book settles 1 texel. No repaint.
- north: back view from the south role silhouettes mirrored x'=80-x (shaved LEFT temple + earring stay on her
  left = viewer-left from behind, the silver-tipped curtain stays on her right, magnifier in her right hand,
  book in her left) refilled as back surfaces: closed long-coat back with centre seam + vent, crossed back
  harness straps, belt, satchel with a brass buckle and a rolled cream scroll (concept sheet back view), black
  high collar, back-of-head hair with the shaved scalp/ear/earring kept from source texels, nape.
- west: authored side puppet, her LEFT side to the viewer: shaved temple with razor lines, ear and rectangular
  brass drop earring, short silver-tipped lock behind the ear, far curtain behind the neck; book in the near
  (left) hand; magnifier raised forward in the far (right) hand; short cream panel under the cut-away hem.
- east: authored side puppet with her RIGHT side to the viewer (long silver-tipped curtain over the ear,
  magnifier raised forward in the near hand, hip vials, thigh strap + pouch, long cream panel, long ragged
  hem point, book in the far hand), then mirrored x'=80-x. NOT a mirror of west; light becomes upper-right
  (limitation).

Character-agnostic helpers (raster primitives, pose tables, PXO/ORA writers, guides, contact/stop reports,
Pixelorama export) are imported from the mexplore23 author; the generic structure follows the Liang lexplore28
author. Neither tool, nor the Ji Cheng south pilot tool, is modified. The old 32x48 Ji Cheng prototype is not
read. The character sheet is a CONCEPT identity reference only (not approved art) and is not sampled.

Usage:  python -X utf8 -I <tool> build|check [--pixelorama EXE] | preview <dir outside the repo>
Writes only NEW files under outputs/jexplore31 and game/data/jexplore31.
"""
import argparse, importlib.util, json, math, os, shutil, sys, tempfile, zipfile, io
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_MX = os.path.join(_HERE, "rpg-2-star-ocean-the-second_protagonist-male_explore-4dir-source-author_unapproved-mexplore23-v01_20261021-162551-6e3b1a7d.py")
_spec = importlib.util.spec_from_file_location("wb_mexplore23_helpers", _MX)
mx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mx)
_JX = os.path.join(_HERE, "rpg-2-star-ocean-the-second_ji-cheng_south-idle-static-pilot-build-and-check_unapproved-v01_20261018-132812-0d31a6f9.py")
_spec = importlib.util.spec_from_file_location("wb_ji_south_v01", _JX)
jx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(jx)
_LX28 = os.path.join(_HERE, "rpg-2-star-ocean-the-second_liang-xu_explore-source-author_unapproved-lexplore28-v01_20261021-194350-3acdbd6e.py")
_fs, rp, rb, sha, sha_text, png_bytes, decode, blank = mx._fs, mx.rp, mx.rb, mx.sha, mx.sha_text, mx.png_bytes, mx.decode, mx.blank
shift, mirror, over, lerp_pose = mx.shift, mx.mirror, mx.over, mx.lerp_pose

SRC_DIR = "game/assets/characters/ji-cheng-hd"
SRC_PNG = SRC_DIR + "/rpg-2-star-ocean-the-second_ji-cheng_south-idle-static_unapproved-v01_20261018-132812-1920ff13.png"
SRC_PXO = SRC_DIR + "/rpg-2-star-ocean-the-second_ji-cheng_south-idle-static-editable_unapproved-v01_20261018-132812-d4b5aa5e.pxo"
SRC_PNG_SHA = "58c92f51959aa7b34dfc9d37c953665579fe75b5629e6d8c807180cba4a32a1d"
SRC_PXO_SHA = "ce9c1fab360c04b7412142a14dca5cd211b91d7e3b14e840a0cc0b4de6b8b69c"
CONCEPT_SHEET = "outputs/rpg-2-star-ocean-the-second_ji-cheng_character-sheet_v01_20261013-190436-dcea1a37.png"
STAMP = "20261021-210451"
RUN = "b2782add"
OUT_REL = "outputs/jexplore31"
PKG_REL = "game/data/jexplore31"
PFX = "rpg-2-star-ocean-the-second_ji-cheng_explore"
VAR = "unapproved-jexplore31-v01"
ACTOR = "ji-cheng"
W, H, PIN, SOLE = mx.W, mx.H, mx.PIN, mx.SOLE
ZIP_DT = (2026, 10, 21, 21, 4, 50)
mx.ZIP_DT = ZIP_DT          # in-process only: zip entry dates for this run's PXO/ORA
DIRS, NPH, FRAME_MS, STOP_K, IDLE_MS, D_PHASE = mx.DIRS, mx.NPH, mx.FRAME_MS, mx.STOP_K, mx.IDLE_MS, mx.D_PHASE
NORMAL_SPEED_LOGICAL = 140.0

PAL = {k: "#" + v for k, v in jx.PAL.items()}       # Ji Cheng named ramps, unchanged
RGB = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in PAL.items()}
INV = {v: k for k, v in RGB.items()}
assert len(INV) == len(RGB), "Ji palette colours must be unique"
YY, XX = np.arange(H)[:, None], np.arange(W)[None, :]
GREEN = set("GgHJ")


class JCanvas(mx.Canvas):
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


def jshade(mask, base, lit, dark, rim=None, litfrac=0.3, darkfrac=0.25):
    c = JCanvas()
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


def keys_of(a):
    k = np.full((H, W), "", dtype="<U1")
    for y, x in zip(*np.nonzero(a[..., 3] == 255)):
        k[y, x] = INV[tuple(int(v) for v in a[y, x, :3])]
    return k


def reshade(a, groups):
    """Re-light the texels of each material group with an upper-left ramp; other texels (outline, fittings) stay."""
    k = keys_of(a)
    out = a.copy()
    for keyset, base, lit, dark in groups:
        m = np.isin(k, list(keyset))
        if m.any():
            out[m] = jshade(m, base, lit, dark).a[m]
    return out


def interior(mask, k):
    """Non-outline texels of a mask plus internal K texels whose 4 neighbours are all inside it."""
    nb = np.zeros_like(mask)
    nb[1:-1, 1:-1] = mask[:-2, 1:-1] & mask[2:, 1:-1] & mask[1:-1, :-2] & mask[1:-1, 2:]
    return (mask & (k != "K")) | (mask & (k == "K") & nb)


def dilate(m, r):
    o = m.copy()
    for _ in range(r):
        n = o.copy()
        n[1:] |= o[:-1]; n[:-1] |= o[1:]; n[:, 1:] |= o[:, :-1]; n[:, :-1] |= o[:, 1:]
        o = n
    return o


# ----------------------------------------------------------------------------- source (exact)
SOUTH_LAYERS = [n for n, _ in jx.ROLE_LAYERS]


def load_src():
    png, pxo = rb(rp(SRC_PNG)), rb(rp(SRC_PXO))
    assert sha(png) == SRC_PNG_SHA and sha(pxo) == SRC_PXO_SHA, "Ji Cheng south source hash drift"
    jx.validate_maps()
    lay = {name: jx.compose(key) for name, key in jx.ROLE_LAYERS}
    src = decode(png)
    assert np.array_equal(over([lay[n] for n in SOUTH_LAYERS]), src), "role layers != source PNG"
    return lay, src, png


LIFT_ROW = 84       # front/back step: shin + buckled boot rise; thigh, knee and coat stay
HEM_ROW = 74        # coat rows >= 74 sway by the 'skirt' pose value
HEAD = ("head-face", "hair", "head-back")


def lift_legs(a, pose):
    parts = []
    for sl, key in ((slice(0, 40), "ll"), (slice(40, W), "rl")):
        leg = blank(); leg[:, sl] = a[:, sl]
        upper = leg.copy(); upper[LIFT_ROW:] = 0
        lower = leg.copy(); lower[:LIFT_ROW] = 0
        parts += [upper, shift(lower, 0, -int(pose.get(key, 0)))]
    return over(parts)


def sway_hem(a, dx):
    if not dx:
        return a
    top, hem = a.copy(), a.copy()
    top[HEM_ROW:] = 0; hem[:HEM_ROW] = 0
    return over([top, shift(hem, dx, 0)])


def render_fb(base, names, pose, raised, hanging, swaying):
    up, hd = int(pose.get("bob", 0)), int(pose.get("head", 0))
    out = []
    for n in names:
        a = base[n]
        if n in ("legs", "boots"):
            a = lift_legs(a, pose)
        elif n in HEAD:
            a = shift(a, 0, hd)
        elif n in raised:          # magnifier arm held up: half the walk arm offset
            a = shift(a, 0, up + int(round(pose.get("arm_l", 0) * 0.5)))
        elif n in hanging:
            a = shift(a, 0, up + int(pose.get("arm_r", 0)) + (int(pose.get("pack", 0)) if n.startswith("book") else 0))
        elif n in swaying:
            a = sway_hem(shift(a, 0, up), int(pose.get("skirt", 0)))
        else:
            a = shift(a, 0, up)
        out.append((n, clip_floor(a)))
    return out


def render_south(src, pose):
    return render_fb(src, SOUTH_LAYERS, pose, ("arm-raised", "magnifier"), ("arm-hanging", "book"), ("coat-front",))


# ----------------------------------------------------------------------------- north (back view)
NORTH_LAYERS = ["cloth-panels", "legs", "boots", "coat-back", "collar-back", "arm-left", "book-back", "arm-right",
                "magnifier-back", "head-back", "hair"]


def north_base(src):
    M = {n: mirror(src[n]) for n in src}
    K = {n: keys_of(M[n]) for n in M}
    al = lambda n: M[n][..., 3] == 255
    base = {"cloth-panels": M["cloth-panels"]}                                   # sheer patterned cloth, same from behind
    base["legs"] = reshade(M["legs"], [(set("Ppo"), "p", "P", "o")])            # thigh strap/pouch texels kept
    base["boots"] = reshade(M["boots"], [(set("Ow"), "w", "O", "w")])           # straps, brass buckles, soles kept
    body = al("coat-front") | al("coat-back") | al("inner-top") | al("harness-belt")
    kb = np.where(al("coat-front"), K["coat-front"], np.where(al("coat-back"), K["coat-back"],
                  np.where(al("inner-top"), K["inner-top"], K["harness-belt"])))
    cm = interior(body, kb) & (YY >= 36)
    hem = np.zeros((H, W), bool)
    for x in range(W):
        hem[:80 + max(0, x - 34) // 3, x] = True                               # closed back over the legs, longer on her right
    cm |= al("legs") & hem & (YY >= 56) & (XX >= 33) & (XX <= 47)
    c = jshade(cm, "g", "G", "H")
    for y in range(38, 71):                                                     # centre back seam
        if cm[y, 40]:
            c.px(40, y, "H")
    for y in range(71, H):                                                      # back vent
        if cm[y, 40]:
            c.px(40, y, "J"); c.px(41, y, "H") if cm[y, 41] else None
    for x in np.nonzero(cm[54])[0]:
        c.px(x, 54, "L")
    for x in np.nonzero(cm[55])[0]:
        c.px(x, 55, "l")
    for (x1, y1, x2, y2) in ((35, 37, 37, 53), (45, 37, 43, 53)):               # crossed back harness straps
        for t in np.linspace(0, 1, 40):
            x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            c.px(x, y, "l"); c.px(x + 1, y, "m")
    for x in range(37, 44):
        c.px(x, 44, "l")
    c.px(36, 44, "M"); c.px(44, 44, "M"); c.px(36, 45, "X"); c.px(44, 45, "X")
    for y in range(56, 64):                                                     # satchel on the belt
        for x in range(33, 48):
            c.px(x, y, "L" if y < 58 else ("m" if y == 63 else "l"))
    c.px(40, 58, "M"); c.px(40, 59, "X"); c.px(39, 58, "Y"); c.px(41, 58, "Y")
    for y in range(64, 67):                                                     # rolled cream scroll under it
        for x in range(32, 49):
            c.px(x, y, "a" if y == 66 else "A")
        c.px(31, y, "X"); c.px(49, y, "X")
    base["coat-back"] = c.outline().a
    col = interior(al("inner-top"), K["inner-top"]) & (YY <= 36)
    base["collar-back"] = jshade(col, "B", "B", "b").outline().a
    base["arm-left"] = reshade(M["arm-hanging"], [(GREEN, "g", "G", "H")])
    base["arm-right"] = reshade(M["arm-raised"], [(GREEN, "g", "G", "H")])
    base["book-back"] = reshade(M["book"], [(set("LlmAa"), "l", "L", "m")])
    base["magnifier-back"] = reshade(M["magnifier"], [(set("Zz"), "z", "z", "z"), (set("MXY"), "X", "M", "Y")])
    hm = al("head-face") | al("hair")
    kk = np.where(al("hair"), K["hair"], K["head-face"])
    hfill = interior(hm, kk)
    scalp = np.isin(kk, list("nN"))
    brass = np.isin(kk, list("MXY"))
    silver = al("hair") & np.isin(K["hair"], list("567"))
    skin = np.isin(kk, list("FfeyR")) | (al("head-face") & np.isin(K["head-face"], list("567")))
    ear = skin & dilate(scalp | brass, 2)
    hb = JCanvas()
    for y, x in zip(*np.nonzero(scalp | brass)):
        hb.px(x, y, kk[y, x])
    for y, x in zip(*np.nonzero(ear)):
        hb.px(x, y, "f" if y < 28 else "e")
    base["head-back"] = hb.outline().a
    hairm = hfill & ~scalp & ~brass & ~ear                                    # the bob covers the nape
    hc = jshade(hairm & ~silver, "3", "2", "4", litfrac=0.25)
    for y, x in zip(*np.nonzero(hairm & silver)):
        hc.px(x, y, K["hair"][y, x])
    for i in range(7):                                                          # crown sheen
        x, y = 34 + i, 11 + abs(i - 3) // 2
        if hairm[y, x]:
            hc.px(x, y, "1")
    base["hair"] = hc.outline().a
    return base


def render_north(base, pose):
    return render_fb(base, NORTH_LAYERS, pose, ("arm-right", "magnifier-back"), ("arm-left", "book-back"), ("coat-back",))


# ----------------------------------------------------------------------------- side puppet (drawn facing -x)
ANKLE_UP = 5
LEG = 17.6      # thigh = shin (source texels); hip row 62 to ankle row 97
HIP_Y = 62
IK_LOG = []


def ik(hx, hy, ax, ay, l1=LEG, l2=LEG):
    dx, dy = ax - hx, ay - hy
    IK_LOG.append(math.hypot(dx, dy) - (l1 + l2))
    d = min(math.hypot(dx, dy), l1 + l2 - 1e-6)
    a = math.atan2(dy, dx)
    b = math.acos((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))
    return hx + l1 * math.cos(a + b), hy + l1 * math.sin(a + b)


def draw_leg(ax_, lift, hip, near, strap=False):
    c = JCanvas()
    hx, hy = hip
    ay = SOLE - 1 - ANKLE_UP - lift
    kx, ky = ik(hx, hy, ax_, ay)
    tr, trs = ("P", "p") if near else ("p", "o")
    c.seg(hx, hy, kx, ky, 8, trs)                               # fitted black trousers
    c.seg(hx - 0.6, hy, kx - 0.6, ky, 5, tr)
    c.seg(kx, ky, ax_, ay, 7, trs)
    c.seg(kx - 0.5, ky, ax_ - 0.5, ay, 4, tr)
    if strap:                                                   # her right thigh: leather strap, brass buckle, pouch
        tx, ty = hx + (kx - hx) * 0.5, hy + (ky - hy) * 0.5
        for dx in range(-4, 4):
            c.px(tx + dx, ty, "l")
        c.px(tx - 2, ty, "M")
        c.poly([(tx, ty + 1), (tx + 3.99, ty + 1), (tx + 3.99, ty + 5.99), (tx, ty + 5.99)], "l")
        c.px(tx, ty + 1, "L"); c.px(tx + 1, ty + 1, "L"); c.px(tx + 2, ty + 3, "X")
    t = 9 / max(math.hypot(kx - ax_, ky - ay), 1)
    bx, by = ax_ + (kx - ax_) * t, ay + (ky - ay) * t
    c.seg(bx, by, ax_, ay, 7, "w")                              # black buckled boot shaft
    c.seg(bx - 0.5, by, ax_ - 0.5, ay, 3, "O" if near else "w")
    c.seg(bx - 0.5, by, bx + 0.5, by, 7, "O" if near else "w")  # lit cuff top
    for f in (0.35, 0.75):                                      # two straps, brass buckles on the near boot
        sx, sy = bx + (ax_ - bx) * f, by + (ay - by) * f
        for dx in range(-3, 4):
            c.px(sx + dx, sy, "m")
        if near:
            c.px(sx - 2, sy, "M")
    sole = ay + ANKLE_UP
    c.poly([(ax_ + 4, ay - 1), (ax_ - 3, ay - 1), (ax_ - 7, sole - 2), (ax_ - 7, sole + 0.99), (ax_ + 4, sole + 0.99)], "w")
    if near:
        c.px(ax_ - 5, sole - 2, "O"); c.px(ax_ - 6, sole - 1, "O"); c.px(ax_ - 1, ay, "O")
    for x in range(int(ax_ - 7), int(ax_ + 4) + 1):             # chunky dark sole
        c.px(x, sole, "K")
    return c.outline().a


def draw_arm(sh, ang, near):
    """Hanging book arm: green sleeve, grey rolled lining cuff, black glove."""
    c = JCanvas()
    sx, sy = sh
    ex, ey = sx + 12 * math.sin(-ang), sy + 12 * math.cos(ang)
    fa = ang - 0.35 if ang < 0 else ang - 0.15
    hx, hy = ex + 9 * math.sin(-fa), ey + 9 * math.cos(fa)
    sl, sd = ("G", "g") if near else ("g", "H")
    c.seg(sx, sy, ex, ey, 7, sd)
    c.seg(sx - 0.6, sy, ex - 0.6, ey, 4, sl)
    c.seg(ex, ey, hx, hy, 6, sd)
    c.seg(ex - 0.5, ey, hx - 0.5, hy, 3, sl)
    cx, cy = ex + (hx - ex) * 0.7, ey + (hy - ey) * 0.7
    c.ell(cx, cy, 3.4, 1.9, "C" if near else "c")
    c.ell(hx, hy + 2, 2.4, 2.4, "B" if near else "b")
    return c.outline().a, (hx, hy + 2)


def draw_raised(sh, near):
    """Magnifier arm: green sleeve to the elbow, wide grey rolled cuff, black-gloved forearm raised forward."""
    c = JCanvas()
    sx, sy = sh
    ex, ey = sx - 5, sy + 9
    hx, hy = sx - 15, sy - 4
    sl, sd = ("G", "g") if near else ("g", "H")
    gl, gd = ("B", "b") if near else ("b", "b")
    c.seg(sx, sy, ex, ey, 7, sd)
    c.seg(sx - 0.6, sy, ex - 0.6, ey, 4, sl)
    c.seg(ex, ey, hx, hy, 5, gd)
    c.seg(ex - 0.6, ey, hx - 0.6, hy, 2, gl)
    c.ell(ex, ey, 3.6, 2.6, "C" if near else "c")
    c.px(ex - 2, ey - 1, "C" if near else "c"); c.px(ex + 2, ey + 1, "c")
    c.ell(hx, hy, 2.6, 2.6, gd)
    c.px(hx - 1, hy - 1, gl)
    return c.outline().a, (hx, hy)


def draw_magnifier(hand):
    """Brass folding magnifier held up, lens turned three-quarters: oval brass ring, pale glass, hinge arm."""
    c = JCanvas()
    hx, hy = hand
    cx, cy = hx - 2, hy - 8
    c.seg(hx - 0.5, hy - 1.5, cx + 0.5, cy + 3.5, 2, "Y")
    c.ell(cx, cy, 2.8, 4.4, "X")
    c.ell(cx, cy, 1.4, 3.0, "z")
    c.px(cx - 1, cy - 2, "Z"); c.px(cx - 1, cy - 1, "Z")
    c.px(cx - 2, cy - 3, "M"); c.px(cx - 1, cy - 4, "M"); c.px(cx - 3, cy - 1, "M"); c.px(cx - 3, cy, "M")
    return c.outline().a


def draw_book(hand, near):
    c = JCanvas()
    hx, hy = hand
    c.poly([(hx - 3, hy - 3), (hx + 2.99, hy - 3), (hx + 2.99, hy + 5.99), (hx - 3, hy + 5.99)], "l" if near else "m")
    c.poly([(hx - 3, hy - 3), (hx - 2.01, hy - 3), (hx - 2.01, hy + 5.99), (hx - 3, hy + 5.99)], "L" if near else "l")
    c.poly([(hx + 2, hy - 2), (hx + 2.99, hy - 2), (hx + 2.99, hy + 4.99), (hx + 2, hy + 4.99)], "A" if near else "a")
    c.px(hx - 3, hy + 2, "M"); c.px(hx - 2, hy + 2, "X")       # brass clasp
    c.ell(hx, hy, 1.8, 1.8, "B" if near else "b")               # gloved fingers over the cover
    return c.outline().a


def draw_head(hd, west):
    """Profile face toward -x; west shows her shaved LEFT temple, east (pre-mirror) her curtain side."""
    c = JCanvas()
    c.poly([(34, 13 + hd), (43, 13 + hd), (44, 30 + hd), (41, 33.5 + hd), (36, 33.5 + hd), (33.5, 31 + hd), (33, 29 + hd),
            (32, 27.5 + hd), (31.2, 25.5 + hd), (33, 23.5 + hd), (33.5, 20 + hd), (34, 16 + hd)], "F")
    c.poly([(40, 13 + hd), (44, 13 + hd), (44, 30 + hd), (41, 33 + hd), (40, 31 + hd)], "f")
    for x in range(37, 41):
        c.px(x, 33 + hd, "e")                                   # jaw shade
    for x in (34, 35, 36):
        c.px(x, 22 + hd, "e")                                   # calm lowered lid
    c.px(34, 23 + hd, "y"); c.px(35, 23 + hd, "y"); c.px(34, 24 + hd, "y"); c.px(35, 24 + hd, "6")
    c.px(33, 27 + hd, "f")                                      # nose shade
    c.px(32, 28 + hd, "R"); c.px(33, 28 + hd, "R"); c.px(33, 29 + hd, "e")
    show = np.zeros((H, W), bool)
    if west:                                                    # shaved left temple, ear, rectangular drop earring
        sc = JCanvas()
        sc.poly([(38, 16 + hd), (45, 14.5 + hd), (47.5, 19 + hd), (47.5, 27 + hd), (45, 31 + hd), (42, 30 + hd), (40, 25 + hd), (38, 21 + hd)], "n")
        sm = sc.a[..., 3] == 255
        c.a[sm] = sc.a[sm]
        for x0, y0 in ((40, 18), (41, 22), (43, 16)):           # razor lines
            for i in range(4):
                c.px(x0 + i, y0 + hd + i // 2, "N")
        for y in range(15, 31):
            if sm[y + hd, 47]:
                c.px(47, y + hd, "N")
        c.ell(44, 24.5 + hd, 1.6, 2.6, "f")
        c.px(44, 24 + hd, "e"); c.px(44, 25 + hd, "e")
        c.px(44, 27 + hd, "X")
        for y, k in ((28, "M"), (29, "X"), (30, "X"), (31, "Y")):
            c.px(43, y + hd, k); c.px(44, y + hd, k if k != "M" else "X")
        show |= sm
        show[27 + hd:32 + hd, 43:45] = True
    face = c.a[..., 3] == 255
    show |= face & (YY >= 21 + hd) & (XX <= (41 if west else 38))
    return c.a, show


def draw_hair(hd, west, face, show):
    c = JCanvas()
    c.ell(42, 20 + hd, 10, 11, "3")                             # cranium: top texel row 9, outline row 8
    c.ell(40, 15 + hd, 7, 5, "2")
    c.poly([(32, 14 + hd), (40, 11 + hd), (42.5, 17 + hd), (37, 20 + hd), (33.5, 21.5 + hd), (32.5, 19 + hd)], "2")   # side-part sweep
    for i in range(6):
        c.px(35 + i, 13 + hd - i // 3, "1")
    c.px(34, 17 + hd, "1"); c.px(35, 16 + hd, "1")
    if west:
        c.poly([(46, 19 + hd), (52.5, 20 + hd), (52, 33 + hd), (47, 34 + hd)], "3")        # back of the bob
        c.poly([(49, 22 + hd), (52.5, 22 + hd), (52, 33 + hd), (50, 33 + hd)], "4")
        c.poly([(46, 28 + hd), (52, 28 + hd), (51.5, 40 + hd), (47.5, 41 + hd)], "4")     # far curtain behind the neck
        for x, y in ((48, 38), (49, 38), (50, 38), (48, 39), (49, 39), (50, 39), (49, 40), (48, 40)):
            c.px(x, y + hd, "6" if y < 40 else "5")
        c.px(51, 38 + hd, "7"); c.px(51, 39 + hd, "7")
        c.poly([(45.5, 27 + hd), (48, 27 + hd), (48, 35 + hd), (46, 33 + hd)], "3")        # short lock behind the shaved side
        for x, y, k in ((46, 32, "6"), (47, 32, "6"), (46, 33, "5"), (47, 33, "6"), (47, 34, "5")):
            c.px(x, y + hd, k)
    else:
        c.poly([(32, 14 + hd), (40, 11 + hd), (43, 18 + hd), (38, 21.5 + hd), (34, 22 + hd), (32.5, 20 + hd)], "2")
        curtain = [(38.5, 17 + hd), (50, 16 + hd), (52.5, 30 + hd), (51.5, 41 + hd), (49.5, 43.5 + hd), (47.5, 41 + hd),
                   (45.5, 43.5 + hd), (43.5, 41 + hd), (41.5, 43 + hd), (40, 39 + hd), (39, 30 + hd)]
        c.poly(curtain, "3")
        cm = JCanvas(); cm.poly(curtain, "3"); cmask = cm.a[..., 3] == 255
        for y in range(18, 40):                                 # lit strands along the front edge
            row = np.nonzero(cmask[y + hd])[0]
            if len(row):
                c.px(row.min(), y + hd, "2"); c.px(row.min() + 1, y + hd, "2" if y % 4 else "1")
                c.px(row.max(), y + hd, "4")
        for y in range(36, 45):                                 # jagged silver-white tips
            for x in np.nonzero(cmask[min(y + hd, H - 1)])[0]:
                c.px(x, y + hd, "5" if (x + y) % 5 == 0 or y >= 40 and x < 46 else ("6" if x < 49 else "7"))
    c.a[show] = 0
    c.outline()
    keep = show & (c.a[..., 3] == 255)
    c.a[keep] = face[keep]
    return c.a


def render_side(pose, near):
    """near='left': her left side to the viewer (west). near='right': her right side (east, pre-mirror)."""
    west = near == "left"
    b, hd, sk, fl = int(pose.get("bob", 0)), int(pose.get("head", 0)), int(pose.get("skirt", 0)), int(pose.get("flap", 0))
    hip = (40.5, HIP_Y + b)
    o = {}
    o["leg-near"] = draw_leg(pose["ax"], pose["al"], hip, True, strap=not west)
    o["leg-far"] = draw_leg(pose["bx"] + 1, pose["bl"], (hip[0] + 1, hip[1]), False)
    book_ang = (pose["arm_n"] if west else pose["arm_f"]) * 0.6
    if west:
        o["arm-near"], hand_b = draw_arm((41, 40 + b), book_ang, True)
        o["arm-far"], hand_m = draw_raised((43, 40 + b), False)
    else:
        o["arm-far"], hand_b = draw_arm((43, 40 + b), book_ang, False)
        o["arm-near"], hand_m = draw_raised((41, 40 + b), True)
    o["book"] = draw_book((hand_b[0], hand_b[1] + fl), west)
    o["magnifier"] = draw_magnifier(hand_m)
    c = JCanvas()                                               # long coat: back tail
    c.poly([(42, 62 + b), (50, 62 + b), (53 + sk, 86), (44 + sk, 86)], "H")
    c.poly([(49, 62 + b), (50, 62 + b), (53 + sk, 86), (51 + sk, 86)], "J")
    c.px(46 + sk, 86, "Y"); c.px(49 + sk, 86, "Y")
    o["coat-back-tail"] = c.outline().a
    hem = 84 if west else 88                                    # her left: cut-away; her right: long ragged point
    c = JCanvas()
    c.poly([(34, 62 + b), (42, 62 + b), (41 - sk, hem - 3), (36 - sk, hem), (32 - sk, hem - 1)], "g")
    c.poly([(34, 62 + b), (36, 62 + b), (34 - sk, hem - 1), (32 - sk, hem - 1)], "G")
    c.px(35 - sk, hem - 1, "X"); c.px(38 - sk, hem - 2, "X"); c.px(36 - sk, hem - 1, "Y")
    o["coat-front-tail"] = c.outline().a
    c = JCanvas()
    if west:                                                    # short cream panel under the cut-away hem
        c.poly([(35 - sk, 78), (41 - sk, 78), (40 - sk, 89), (38 - sk, 87), (36 - sk, 89)], "A")
        for y in range(80, 89):
            c.px(40 - sk, y, "a")
        for y in range(81, 89, 3):
            c.px(37 - sk, y, "a")
    else:                                                       # long patterned cream panel outside the coat
        c.poly([(39, 57 + b), (43, 57 + b), (43 - sk, 83), (41.5 - sk, 87), (40 - sk, 84), (39 - sk, 86)], "A")
        for y in range(58 + b, 86):
            c.px(42 - (sk if y > 70 else 0), y, "a")
        for y in range(60 + b, 84, 3):
            c.px(40 - (sk if y > 70 else 0), y, "a"); c.px(41 - (sk if y > 70 else 0), y + 1, "a")
    o["cloth-panel"] = c.outline().a
    tc = JCanvas()
    tc.poly([(36, 36 + b), (46, 36 + b), (49, 42 + b), (50, 62 + b), (34, 62 + b), (34, 43 + b)], "g")
    tc.poly([(36, 36 + b), (39, 36 + b), (38, 62 + b), (34, 62 + b), (34, 43 + b)], "G")
    tc.poly([(47, 39 + b), (49, 42 + b), (50, 62 + b), (47, 62 + b)], "H")
    for y in range(39, 53):
        tc.px(34 if y > 43 else 35, y + b, "B")                 # black top in the open front
        tc.px(35 if y > 43 else 36, y + b, "M" if y % 5 == 0 else "X")   # worn brass lapel trim
    for t in np.linspace(0, 1, 30):                             # chest harness strap + brass ring
        tc.px(44 - 7 * t, 38 + 14 * t + b, "l"); tc.px(45 - 7 * t, 38 + 14 * t + b, "m")
    tc.px(40, 45 + b, "M"); tc.px(41, 45 + b, "X")
    for x in range(34, 51):
        tc.px(x, 54 + b, "L"); tc.px(x, 55 + b, "l")
    tc.px(34, 54 + b, "M"); tc.px(35, 54 + b, "X"); tc.px(34, 55 + b, "X"); tc.px(35, 55 + b, "Y")
    if not west:                                                # her right hip: two silver vials with brass caps
        for vx in (38, 41):
            tc.px(vx, 57 + b, "X")
            for y in range(58, 62):
                tc.px(vx, y + b, "5" if y == 58 else "6")
            tc.px(vx + 1, 58 + b, "6"); tc.px(vx + 1, 59 + b, "7")
    o["torso-coat"] = tc.outline().a
    c = JCanvas()                                               # black high collar + green lapel behind
    c.poly([(43, 33 + b), (48, 35 + b), (48, 40 + b), (44, 40 + b)], "g")
    c.poly([(36, 31 + hd), (44, 31 + hd), (45, 37 + b), (36, 37 + b)], "B")
    c.poly([(42, 31 + hd), (44, 31 + hd), (45, 37 + b), (42, 37 + b)], "b")
    c.px(36, 35 + b, "M")
    o["collar"] = c.outline().a
    face, show = draw_head(hd, west)
    c = JCanvas(); c.a = face.copy()
    o["head-face"] = c.outline().a
    o["hair"] = draw_hair(hd, west, o["head-face"], show)
    if west:
        order = ["magnifier", "arm-far", "coat-back-tail", "leg-far", "leg-near", "cloth-panel", "torso-coat",
                 "coat-front-tail", "collar", "head-face", "hair", "arm-near", "book"]
    else:
        order = ["book", "arm-far", "coat-back-tail", "leg-far", "leg-near", "torso-coat", "coat-front-tail",
                 "cloth-panel", "collar", "head-face", "arm-near", "hair", "magnifier"]
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
                    "Front/back cycles are in place (not world-locked). No fluidity claim."}


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
            "notes": ["side stance span 24 source texels exceeds the 35.2-texel leg reach at the extremes; the knee "
                      "solve clamps and the shin segment stretches by the listed overreach (straight-leg look at contact)",
                      "front/back walk is an in-place shin/boot lift (no foreshortened stride); coat hem sways 1 texel",
                      "side views and the north refill are new puppet/refill geometry, not the hand-placed south texel "
                      "quality; face/hair/props at 48 px not inspected in-game in this batch",
                      "east light direction becomes upper-right after the mirror",
                      "magnifier lens is a 3/4 oval in side views and stays raised (no swing) while walking",
                      "north back details (harness straps, satchel, scroll) follow the CONCEPT sheet, which is not approved art",
                      "south cosmetic revision bucket and visual audit remain open (deferred, not waived)"]}
    source = {"project": "Worlds Between", "visual_id": ACTOR, "run_id": RUN, "variant": VAR,
              "status": "UNAPPROVED technical source; art not approved; not runtime-integrated; no default changed",
              "task_ids": ["content.char.ji-cheng.static-west", "content.char.ji-cheng.static-north",
                           "content.char.ji-cheng.static-east", "content.char.ji-cheng.idle-anim",
                           "content.char.ji-cheng.walk-south", "content.char.ji-cheng.walk-west",
                           "content.char.ji-cheng.walk-north", "content.char.ji-cheng.walk-east"],
              "contract": {"cell": [W, H], "pivot": list(PIN), "density": 2, "body_texels": 96, "logical_height": 48,
                           "sole_row": SOLE, "alpha": "binary", "filter": "nearest"},
              "source_inputs": {"ji_cheng_south_png": {"file": SRC_PNG, "sha256": SRC_PNG_SHA, "hash": "sha256-bytes"},
                                "ji_cheng_south_pxo": {"file": SRC_PXO, "sha256": SRC_PXO_SHA, "hash": "sha256-bytes"},
                                "ji_cheng_south_build_tool_maps": {"file": "tools/" + os.path.basename(_JX), "sha256_text_lf_v1": sha_text(rb(_JX))}},
              "identity_reference_not_sampled": {"file": CONCEPT_SHEET, "approval": "CONCEPT (not approved art)",
                                                 "use": "read for side/back identity cues only; no texel sampled; historical output omitted in this sparse checkout"},
              "methods": {"south": "exact Ji Cheng south MAP/ROLE 13 role layers; static and idle f00 are the source PNG bytes; idle/walk/stop = role-layer offsets + per-leg column split at x=40 (rows>=84 rise) + 1-texel hem sway; raised magnifier arm at half the arm offset",
                          "north": "back view: south role silhouettes mirrored x'=80-x refilled as back surfaces (closed coat back, seam, vent, crossed harness straps, belt, satchel + rolled scroll, black collar, back-of-head hair; shaved scalp/ear/earring and silver tip texels kept from source)",
                          "west": "authored side puppet, her left side to viewer: shaved temple + razor lines, ear, rectangular brass drop earring, short silver-tipped lock, far curtain behind the neck; book in the near (left) hand; magnifier raised forward in the far (right) hand; short cream panel",
                          "east": "authored side puppet, her right side to viewer (long silver-tipped curtain, magnifier raised in the near hand, hip vials, thigh strap + pouch, long cream panel, long hem point, book in the far hand), mirrored x'=80-x; light becomes upper-right (limitation)"},
              "reused_helpers": {"file": "tools/" + os.path.basename(_MX), "sha256_text_lf_v1": sha_text(rb(_MX))},
              "architecture_reference": {"file": "tools/" + os.path.basename(_LX28), "sha256_text_lf_v1": sha_text(rb(_LX28)),
                                         "use": "generic structure (frame set, emit, package, checks) followed; not imported"},
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
    ck("original south PXO unchanged", sha(rb(rp(SRC_PXO))) == SRC_PXO_SHA)
    ck("four statics pairwise distinct", len({st[d].tobytes() for d in DIRS}) == 4)
    ck("east is not a mirror of west (handedness authored)", not np.array_equal(st["east"], mirror(st["west"])))
    ck("north is not a mirror of south", not np.array_equal(st["north"], mirror(st["south"])))
    sets = {"brass": {RGB[k] for k in "MXY"}, "silver": {RGB[k] for k in "567"}, "scalp": {RGB[k] for k in "nN"},
            "glass": {RGB[k] for k in "Zz"}, "cream": {RGB[k] for k in "Aa"}, "green": {RGB[k] for k in "GgHJ"}}
    for d in DIRS:
        a = st[d]
        cnt = lambda ks, y0=0, y1=H: int(sum(1 for y in range(y0, y1) for x in range(W) if a[y, x, 3] and tuple(a[y, x, :3]) in ks))
        got = {"brass": cnt(sets["brass"]), "silver_head_rows": cnt(sets["silver"], 8, 50), "scalp_head_rows": cnt(sets["scalp"], 8, 40),
               "glass": cnt(sets["glass"]), "cream": cnt(sets["cream"]), "green": cnt(sets["green"])}
        need_scalp = d != "east"                                # east shows her curtain side; the shaved side faces away
        ok = got["brass"] >= 8 and got["silver_head_rows"] >= 4 and got["glass"] >= 2 and got["cream"] >= 4 and \
            got["green"] >= 200 and (got["scalp_head_rows"] >= 4 if need_scalp else True)
        ck(f"{d} identity cues: brass, silver tips, magnifier glass, cream panel, green coat, shaved scalp (not east)", ok, got)
    lm = {d: (st[d][8:40, :, 3] == 255) for d in DIRS}
    scalp_x = {d: [int(x) for x in np.nonzero(np.isin(keys_of(st[d])[8:40], list("nN")).any(0))[0]] for d in ("south", "north")}
    ck("shaved temple side: south viewer-right, north viewer-left (her left both)",
       scalp_x["south"] and min(scalp_x["south"]) > 40 and scalp_x["north"] and max(scalp_x["north"]) < 40, scalp_x)
    pk = json.loads(files[source["package"]["sprite_set"]])
    ok = pk["schema"] == "worlds-between.exploration-sprite-set.v1" and pk["actor_id"] == ACTOR and \
        set(pk["actions"]) == {"idle", "walk"} and all(set(pk["actions"][a]) == set(DIRS) for a in pk["actions"])
    durs = [f["duration_ms"] for a in pk["actions"].values() for v in a.values() for f in v]
    ok &= all(isinstance(x, int) and 40 <= x <= 2000 for x in durs)
    paths = [f["file"] for a in pk["actions"].values() for v in a.values() for f in v]
    ok &= all(not p.startswith("/") and ".." not in p and (PKG_REL + "/" + p) in files for p in paths)
    ok &= all(files[PKG_REL + "/png/" + p.rsplit("/", 1)[-1]] == files[OUT_REL + "/png/" + p.rsplit("/", 1)[-1]] for p in paths)
    ck("runtime package schema/actor/actions/durations/relative lossless PNG copies", ok, len(paths))
    stp = json.loads(files[source["package"]["stop_supplemental"]])
    sp = [s["file"] for d in DIRS for v in stp["phase_bridges"][d].values() for s in v if "file" in s]
    ck("stop supplemental actor/48 bridges per... 24 per direction, files present and byte-equal",
       stp["actor_id"] == ACTOR and len(sp) == 96 and all(files[PKG_REL + "/" + p] == files[OUT_REL + "/" + p] for p in sp), len(sp))
    reg = json.loads(files[source["package"]["registry"]])
    ck("registry schema + ONLY ji-cheng -> set manifest", reg["schema"] == "worlds-between.exploration-sprite-set-registry.v1" and
       list(reg["actors"]) == [ACTOR] and (PKG_REL + "/" + reg["actors"][ACTOR]) == source["package"]["sprite_set"])
    ck("no .gdignore in runtime package", not os.path.exists(_fs(rp(PKG_REL + "/.gdignore"))) and not os.path.exists(_fs(rp(PKG_REL + "/png/.gdignore"))))
    ck("no 32x48 placeholder input", all("32x48" not in v["file"] and "native-animation" not in v["file"] for v in source["source_inputs"].values()))
    for d in ("west", "east"):
        c = source["contact_check"][d]
        ck(f"{d} sole rows grounded on planted pairs (slip disclosed, not gated)", all(SOLE in r["sole_rows"] or SOLE + 1 in r["sole_rows"] for r in c["pairs"]),
           {"max_abs_slip_source": c["max_abs_slip_source"]})
    return res


def preview(out_dir):
    from PIL import Image
    if os.path.abspath(out_dir).lower().startswith(mx.ROOT.lower()):
        raise SystemExit("preview dir must be outside the repo")
    fs, files, source = build_all()
    os.makedirs(out_dir, exist_ok=True)
    for bgname, bg in (("grey", (120, 120, 130)), ("bright", (214, 206, 186)), ("dark", (38, 40, 46))):
        for d in DIRS:
            e = source["directions"][d]
            fr = [e["static"]] + e["walk"]
            sheet = Image.new("RGBA", (W * len(fr), H), bg + (255,))
            for i, x in enumerate(fr):
                sheet.alpha_composite(Image.fromarray(decode(files[x["file"]])), (i * W, 0))
            sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(os.path.join(out_dir, f"jx31_{d}_{bgname}.png"))
    print("PREVIEW", out_dir)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["build", "check", "preview"])
    ap.add_argument("out", nargs="?")
    ap.add_argument("--pixelorama")
    a = ap.parse_args()
    if a.mode == "preview":
        return preview(a.out)
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
            tmp = tempfile.mkdtemp(prefix="wb-jx31-")
            try:
                p, outs = mx.pixelorama_export(a.pixelorama, rp(e["pxo"]["file"]), tmp, False)
                diag = [ln for ln in (p.stdout + p.stderr).splitlines() if any(t in ln for t in ("ERROR", "SCRIPT ERROR", "WARNING"))]
                names = sorted(outs)
                eqn = sum(1 for i in range(min(len(names), len(order))) if np.array_equal(decode(outs[names[i]]), decode(files[order[i]["file"]])))
                r = {"dir": d, "exit": p.returncode, "frames_exported": len(names), "frames_expected": len(order),
                     "all_frames_equal": f"{eqn}/{len(order)}", "script_error": any("SCRIPT ERROR" in ln for ln in diag),
                     "diagnostics_reported_separately": diag[:12], "diagnostic_lines": len(diag)}
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
