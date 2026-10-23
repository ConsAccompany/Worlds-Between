"""Lin Que SOUTH / WEST / NORTH / EAST idle statics, native 80x112 source packages (UNAPPROVED v01).

Code-authored native pixels in the Sea of Stars direction (broad clusters, upper-left light). Identity anchors
from the concept sheet (identity reference only, no pixels sampled): dark navy layered short hair, goggles
above the forehead, white scarf, navy short cape/coat with pale geometric trim, dark trousers and boots,
technical belt/holster and a compact silver/black firearm. Holster sits on the character's RIGHT hip, the
scarf tail hangs/streams on the character's LEFT side, so east/west are authored, not mirrored.

Reuses the Jiang south v01 author (L primitives, compose, gates) and through it the male v8pair serializers
(png/pxo/ora); the Jiang module's palette/layer globals are rebound in memory to Lin Que's (no Jiang file is
written). Jiang files are only read.

  python -X utf8 -I <this> build   # writes new files only (refuses to overwrite different bytes)
  python -X utf8 -I <this> check   # rebuilds twice in memory and compares with files on disk
"""
import hashlib, importlib.util, io, json, os, sys, zipfile
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG, ACTOR = "rpg-2-star-ocean-the-second", "lin-que"
STAMP, RUN_ID = "20261022-222500", "3d61c74e"
OUT_REL = "game/assets/characters/lin-que-native-v01"
QA_REL = "outputs/lin58d/claude"
JIANG_TOOL_REL = "tools/rpg-2-star-ocean-the-second_jiang-lan_south-static-author_unapproved-v01_20261021-235007-514b9771.py"
JIANG_TOOL_SHA = "35005f3c904802251c773838d61068d4aea847c993f6e354676e88a599db69b4"
PORTRAIT_REL = "outputs/rpg-2-star-ocean-the-second_lin-que_character-sheet_v01_20261013-153556-88b92720.png"
PORTRAIT_SHA = "24007e147c9dd67b330af4a84ac13054f65989cddb9bdf2702dc5c80de7fb352"
DIRS = ("south", "west", "north", "east")
ZIP_DT = (2026, 10, 22, 22, 25, 0)
MIN_VISIBLE = 12  # texels a role layer must show in the composite to count as genuine

PAL = {  # declared palette; upper-left light
    "s1": "f6d8bf", "s2": "e2b796", "s3": "bf8c6e", "s4": "855543",          # skin
    "n1": "4f6596", "n2": "33436c", "n3": "212c4a", "n4": "11182b",          # navy hair
    "e1": "f4f6ff", "e2": "34507e", "m1": "a2584a",                          # eye white, iris, mouth
    "c1": "586894", "c2": "3c496f", "c3": "2a3352", "c4": "171d31",          # navy coat / cape
    "t1": "eef2f6", "t2": "b9c4d2", "t3": "8292a8",                          # pale geometric trim
    "w1": "fbfbf7", "w2": "dcdfe3", "w3": "aab2be",                          # white scarf
    "g1": "6c7482", "g2": "2c3039", "l1": "c4ecff", "l2": "5a9ec8",          # goggles frame/strap, lens
    "d1": "4a4a58", "d2": "33333f", "d3": "222229",                          # dark trousers
    "b1": "5a4a44", "b2": "3a2e2a", "k1": "121216",                          # boots / black
    "r1": "8c5c3c", "r2": "5e3c26",                                          # belt / holster leather
    "x1": "e4e8ee", "x2": "a0a8b4", "x3": "5c6270",                          # silver firearm / buckle
}
LAYERS = ["cape", "boots", "trousers", "coat", "belt", "arms", "firearm", "face", "scarf", "hair", "goggles", "guides"]
OUTLINE = {"cape": "c4", "boots": "k1", "trousers": "d3", "coat": "c4", "belt": "r2", "arms": "c4",
           "firearm": "k1", "face": "s4", "scarf": "w3", "hair": "n4", "goggles": "g2"}


def fs(rel):
    p = os.path.join(REPO, *rel.split("/"))
    return "\\\\?\\" + p if os.name == "nt" and len(p) > 240 and not p.startswith("\\\\?\\") else p


def sha(b):
    return hashlib.sha256(b).hexdigest()


def uid(*parts):
    return sha(":".join((RUN_ID,) + parts).encode())[:8]


def fname(d, purpose, ext):
    return f"{SLUG}_{ACTOR}_{d}-{purpose}_unapproved-v01_{STAMP}-{uid(d, purpose, ext)}.{ext}"


def load(rel, modname):
    spec = importlib.util.spec_from_file_location(modname, fs(rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


S = load(JIANG_TOOL_REL, "jiang_south_v01_for_lin")
S.PAL, S.LAYERS, S.OUTLINE, S.ZIP_DT = PAL, LAYERS, OUTLINE, ZIP_DT   # rebind in memory only
W, H, PIN, BODY_ROWS, L = S.W, S.H, S.PIN, S.BODY_ROWS, S.L


def trim_row(l, x0, x1, y, phase=0):
    """pale geometric trim: t1 diamonds every 3rd texel on t2."""
    for x in range(x0, x1 + 1):
        l.px(x, y, "t1" if (x + phase) % 3 == 0 else "t2")


# ------------------------------------------------------------------ south (front)
def draw_south(Ls):
    cp = Ls["cape"]                                                           # cape flare behind arms
    cp.rows({**{y: (28, 52) for y in range(37, 42)}, **{y: (25, 55) for y in range(42, 48)},
             **{y: (24, 56) for y in range(48, 54)}, **{y: (23, 57) for y in range(54, 58)}}, "c2")
    cp.rect(23, 44, 24, 57, "c1"); cp.rect(55, 44, 57, 57, "c3")
    trim_row(cp, 23, 57, 58)

    b = Ls["boots"]
    for x0 in (31, 42):
        b.shaded(x0, 89, x0 + 7, 102, "b1", "b2", "k1", 2, 2)
        b.hline(x0, x0 + 7, 89, "b1"); b.hline(x0 + 1, x0 + 6, 94, "x3"); b.px(x0 + 2, 94, "x2")
        b.rect(x0 + 1, 99, x0 + 3, 100, "b1")                                # toe cap highlight
        b.hline(x0, x0 + 7, 103, "k1")

    t = Ls["trousers"]
    t.rect(31, 66, 49, 72, "d2")
    for x0 in (32, 42):
        t.shaded(x0, 72, x0 + 6, 92, "d1", "d2", "d3", 2, 2)
        t.px(x0 + 3, 80, "d3"); t.px(x0 + 2, 81, "d1")                       # knee crease

    c = Ls["coat"]
    c.rows({37: (32, 48), 38: (30, 50), 39: (28, 52), **{y: (27, 53) for y in range(40, 46)}}, "c2")
    c.rect(27, 40, 31, 45, "c1"); c.rect(49, 40, 53, 45, "c3")               # capelet shoulders
    trim_row(c, 27, 53, 46); c.hline(28, 52, 47, "c3")
    c.shaded(30, 48, 50, 66, "c1", "c2", "c3", 2, 3)
    for x0, x1 in ((30, 38), (42, 50)):                                       # split tails
        c.shaded(x0, 67, x1, 73, "c1", "c2", "c3", 1, 2)
    c.rect(29, 70, 29, 73, "c1"); c.rect(51, 70, 51, 73, "c3")
    trim_row(c, 29, 38, 74); trim_row(c, 42, 51, 74, 1)
    c.vline(40, 47, 66, "c4")
    for y in range(47, 74):                                                   # front-edge trim
        k = "t1" if y % 3 == 0 else "t2"
        c.px(39, y, k); c.px(41, y, "t3" if y % 3 else "t2")
    c.rect(33, 52, 36, 55, "c3"); c.hline(33, 36, 52, "c1")                  # chest pocket (char right)

    bl = Ls["belt"]
    bl.rect(30, 62, 50, 64, "r2"); bl.hline(30, 50, 62, "r1")
    bl.rect(38, 62, 42, 64, "x2"); bl.px(38, 62, "x1"); bl.rect(39, 63, 41, 63, "x3")
    bl.rect(46, 64, 48, 68, "r2"); bl.hline(46, 48, 64, "r1")                # pouch (char left)
    bl.rect(27, 64, 31, 73, "r2"); bl.vline(27, 64, 73, "r1"); bl.hline(27, 31, 67, "r1")  # holster

    a = Ls["arms"]
    for x0, hx in ((25, 25), (51, 52)):
        a.shaded(x0, 41, x0 + 4, 59, "c1", "c2", "c3", 1, 1)
        trim_row(a, x0, x0 + 4, 60); a.hline(x0, x0 + 4, 61, "t3")
        a.shaded(hx, 62, hx + 3, 65, "s1", "s2", "s3", 1, 1)

    f = Ls["firearm"]
    f.rect(29, 59, 32, 63, "k1"); f.vline(29, 59, 63, "x3"); f.hline(30, 32, 61, "x3")  # grip
    f.rect(28, 64, 30, 71, "x2"); f.vline(28, 64, 71, "x1"); f.vline(30, 64, 71, "x3")  # slide in holster

    fc = Ls["face"]
    fc.rows({**{y: (31, 48) for y in range(18, 31)}, 31: (32, 47), 32: (34, 45), 33: (36, 43)}, "s2")
    fc.rect(31, 18, 33, 28, "s1"); fc.rect(46, 18, 48, 31, "s3"); fc.hline(31, 48, 23, "s3")
    fc.rect(37, 33, 42, 36, "s3")
    for ex in (35, 43):
        fc.rect(ex, 25, ex + 1, 27, "e2"); fc.px(ex, 25, "e1")
    fc.px(40, 28, "s3"); fc.hline(39, 40, 30, "m1")

    sc = Ls["scarf"]
    sc.rows({34: (34, 46), **{y: (32, 48) for y in range(35, 41)}, 41: (33, 47)}, "w1")
    sc.rect(45, 35, 48, 41, "w2"); sc.vline(48, 35, 41, "w3")
    for x in range(34, 44, 2):
        sc.px(x, 38, "w2")
    sc.rect(44, 36, 46, 39, "w2"); sc.px(45, 37, "w3")                       # knot
    sc.rows({y: (45, 49) for y in range(42, 53)}, "w1")                       # tail on char left
    sc.vline(48, 42, 52, "w2"); sc.vline(49, 42, 52, "w3"); sc.hline(45, 47, 47, "w2")

    h = Ls["hair"]
    h.rows({8: (35, 45), 9: (32, 48), 10: (30, 50), 11: (29, 51), **{y: (28, 52) for y in range(12, 18)},
            **{y: (27, 53) for y in range(18, 21)}}, "n2")
    h.rows({21: (31, 34), 22: (32, 33)}, "n2"); h.rows({21: (37, 41), 22: (38, 40), 23: (39, 39)}, "n2")
    h.rows({21: (44, 48), 22: (45, 47)}, "n2")
    h.rect(27, 21, 31, 27, "n2"); h.rect(48, 21, 53, 27, "n2")
    h.rows({28: (28, 30), 29: (28, 30), 30: (29, 30), 31: (29, 29)}, "n2")
    h.rows({28: (49, 52), 29: (50, 52), 30: (50, 51), 31: (51, 51)}, "n2")
    h.rows({9: (33, 38), 10: (31, 37), 11: (30, 35), 12: (29, 33)}, "n1")    # upper-left sheen
    h.rect(28, 18, 29, 26, "n1"); h.rows({19: (32, 35), 20: (33, 34)}, "n1")
    h.rect(51, 12, 52, 27, "n3"); h.rows({18: (47, 50), 19: (46, 49), 20: (45, 48)}, "n3")
    for x in (36, 42, 47):                                                     # layer separations
        h.vline(x, 18, 20, "n3")

    g = Ls["goggles"]
    g.hline(28, 52, 15, "g2"); g.hline(28, 52, 16, "g2")
    for x0 in (31, 43):
        g.rect(x0, 12, x0 + 6, 17, "g1"); g.rect(x0 + 1, 13, x0 + 5, 16, "l2")
        g.rect(x0 + 1, 13, x0 + 2, 14, "l1"); g.hline(x0 + 1, x0 + 6, 17, "g2")
    g.rect(38, 14, 42, 15, "g1")


# ------------------------------------------------------------------ north (back)
def draw_north(Ls):
    cp = Ls["cape"]                                                           # cape covers the back
    cp.rows({**{y: (29, 51) for y in range(37, 41)}, **{y: (26, 54) for y in range(41, 48)},
             **{y: (25, 55) for y in range(48, 55)}, **{y: (24, 56) for y in range(55, 60)}}, "c2")
    cp.rect(24, 41, 28, 59, "c1"); cp.rect(52, 41, 56, 59, "c3")
    for i, y in enumerate(range(47, 54)):                                     # back diamond motif
        r = 3 - abs(i - 3)
        cp.hline(40 - r, 40 + r - 1 if r else 40, y, "t2")
    cp.px(40, 50, "t1"); cp.px(39, 50, "t1")
    trim_row(cp, 24, 56, 60, 2)

    b = Ls["boots"]
    for x0 in (31, 42):
        b.shaded(x0, 89, x0 + 7, 102, "b1", "b2", "k1", 2, 2)
        b.hline(x0, x0 + 7, 89, "b1"); b.rect(x0 + 2, 98, x0 + 5, 102, "b2")   # heel counter
        b.hline(x0, x0 + 7, 103, "k1")

    t = Ls["trousers"]
    t.rect(31, 66, 49, 72, "d2")
    for x0 in (32, 42):
        t.shaded(x0, 72, x0 + 6, 92, "d1", "d2", "d3", 2, 2)
        t.hline(x0 + 1, x0 + 5, 84, "d3")                                     # back-knee fold

    c = Ls["coat"]
    for x0, x1 in ((30, 39), (41, 50)):                                       # tails below the cape
        c.shaded(x0, 61, x1, 73, "c1", "c2", "c3", 1, 2)
    c.rect(29, 70, 29, 73, "c1"); c.rect(51, 70, 51, 73, "c3"); c.vline(40, 61, 73, "c4")
    trim_row(c, 29, 39, 74); trim_row(c, 41, 51, 74, 2)

    bl = Ls["belt"]
    bl.rect(30, 62, 50, 64, "r2"); bl.hline(30, 50, 62, "r1"); bl.rect(39, 62, 41, 64, "r1")
    bl.rect(49, 64, 53, 73, "r2"); bl.vline(49, 64, 73, "r1"); bl.hline(49, 53, 67, "r1")  # holster (char right)
    bl.rect(32, 64, 34, 68, "r2"); bl.hline(32, 34, 64, "r1")                # pouch (char left)

    a = Ls["arms"]
    for x0, hx in ((25, 25), (51, 52)):
        a.shaded(x0, 41, x0 + 4, 59, "c1", "c2", "c3", 1, 1)
        trim_row(a, x0, x0 + 4, 60); a.hline(x0, x0 + 4, 61, "t3")
        a.shaded(hx, 62, hx + 3, 65, "s2", "s2", "s3", 1, 1)

    f = Ls["firearm"]
    f.rect(48, 59, 51, 63, "k1"); f.vline(48, 59, 63, "x3"); f.hline(49, 51, 61, "x3")  # grip back

    fc = Ls["face"]                                                           # ears + nape only
    fc.rect(26, 21, 27, 26, "s2"); fc.vline(26, 21, 26, "s1"); fc.px(27, 24, "s3")
    fc.rect(53, 21, 54, 26, "s3"); fc.px(53, 24, "s4")
    fc.rect(37, 33, 43, 35, "s3")

    sc = Ls["scarf"]
    sc.rows({**{y: (32, 48) for y in range(35, 41)}, 41: (33, 47)}, "w1")
    sc.rect(45, 35, 48, 41, "w2"); sc.vline(48, 35, 41, "w3")
    for x in range(35, 45, 2):
        sc.px(x, 37, "w2")
    sc.rows({y: (31, 35) for y in range(42, 54)}, "w1")                       # tail on char left = screen left
    sc.vline(34, 42, 53, "w2"); sc.vline(35, 42, 53, "w3"); sc.hline(31, 33, 48, "w2")

    h = Ls["hair"]
    h.rows({8: (35, 45), 9: (32, 48), 10: (30, 50), **{y: (28, 52) for y in range(11, 29)},
            29: (29, 51), 30: (29, 51), 31: (30, 50), 32: (31, 49)}, "n2")
    for x0 in (31, 36, 41, 46):                                               # layered nape spikes
        h.rows({33: (x0, x0 + 2), 34: (x0 + 1, x0 + 1)}, "n2")
    h.rows({9: (33, 38), 10: (31, 37), 11: (30, 35), 12: (29, 33)}, "n1")
    h.rect(28, 18, 29, 28, "n1")
    h.rect(50, 11, 52, 30, "n3")
    for x0, y0 in ((34, 20), (40, 18), (45, 21)):                             # layer tiers
        h.vline(x0, y0, y0 + 9, "n3"); h.px(x0 - 1, y0 + 9, "n1")
    h.hline(31, 49, 26, "n3"); h.rows({27: (32, 36)}, "n1")

    g = Ls["goggles"]
    g.hline(28, 52, 15, "g2"); g.hline(28, 52, 16, "g2")
    g.rect(37, 14, 42, 17, "g1"); g.rect(38, 15, 41, 16, "x2"); g.px(38, 15, "x1")   # strap buckle
    g.rect(28, 12, 30, 15, "g1"); g.rect(50, 12, 52, 15, "g1")              # lens-rim backs


# ------------------------------------------------------------------ profiles (west / east)
class P:
    """Forward-coordinate pen over an L: f>0 is the facing direction; light stays upper-left on screen."""
    def __init__(self, lay, s):
        self.l, self.s = lay, s

    def x(self, f):
        return 40 + self.s * f

    def span(self, f0, f1):
        a, b = self.x(f0), self.x(f1)
        return min(a, b), max(a, b)

    def px(self, f, y, k):
        self.l.px(self.x(f), y, k)

    def rect(self, f0, y0, f1, y1, k):
        a, b = self.span(f0, f1); self.l.rect(a, y0, b, y1, k)

    def shaded(self, f0, y0, f1, y1, lo, mid, dk, hi_w=1, dk_w=1):
        a, b = self.span(f0, f1); self.l.shaded(a, y0, b, y1, lo, mid, dk, hi_w, dk_w)

    def rows(self, spans, k):
        for y, (f0, f1) in spans.items():
            self.rect(f0, y, f1, y, k)

    def trim(self, f0, f1, y, phase=0):
        a, b = self.span(f0, f1); trim_row(self.l, a, b, y, phase)


def draw_side(Ls, d):
    s = 1 if d == "east" else -1
    right = d == "east"                  # east shows the character's right side (holster), west the left (scarf tail)
    p = {n: P(Ls[n], s) for n in LAYERS}

    cp = p["cape"]                                                            # cape sweeps back
    cp.rows({**{y: (-8, 2) for y in range(37, 45)}, **{y: (-10, 0) for y in range(45, 53)},
             **{y: (-12, -1) for y in range(53, 59)}}, "c2")
    cp.shaded(-12, 45, -6, 58, "c1", "c2", "c3", 1, 1)
    cp.trim(-12, -1, 59)

    b = p["boots"]
    b.shaded(-2, 92, 6, 102, "b2", "b2", "k1"); b.rect(6, 98, 8, 102, "b2")   # far boot, darker, ahead
    b.rect(-2, 103, 8, 103, "k1")
    b.shaded(-4, 90, 4, 102, "b1", "b2", "k1", 2, 1); b.rect(5, 98, 6, 102, "b1")
    b.rect(1, 98, 4, 99, "b1"); b.rect(-4, 94, 3, 94, "x3"); b.px(-3, 94, "x2")
    b.rect(-5, 103, 6, 103, "k1"); b.rect(-5, 101, -4, 102, "b2")             # heel

    t = p["trousers"]
    t.rect(-6, 66, 5, 72, "d2")
    t.rect(-1, 72, 4, 92, "d3"); t.rect(4, 72, 4, 92, "d3")                   # far leg
    t.shaded(-4, 72, 1, 91, "d1", "d2", "d3", 2, 1)
    t.px(1, 80, "d1"); t.px(0, 81, "d3")
    if right:
        t.rect(-4, 70, 0, 70, "r1")                                           # holster thigh strap

    c = p["coat"]
    c.rows({37: (-5, 4), 38: (-7, 5), **{y: (-8, 6) for y in range(39, 46)}}, "c2")
    c.rect(-8, 39, -6, 45, "c1"); c.rect(5, 40, 6, 45, "c3")
    c.trim(-8, 6, 46); c.rect(-7, 47, 5, 47, "c3")
    c.shaded(-6, 48, 5, 66, "c1", "c2", "c3", 2, 2)
    c.shaded(-8, 67, -1, 76, "c1", "c2", "c3", 1, 1); c.trim(-8, -1, 77)      # back tail
    c.shaded(1, 67, 5, 72, "c2", "c2", "c3"); c.trim(1, 5, 73, 1)             # front tail
    for y in range(47, 73):
        c.px(5, y, "t1" if y % 3 == 0 else "t2")                              # front-edge trim
    if right:
        c.rect(1, 52, 3, 55, "c3"); c.rect(1, 52, 3, 52, "c1")                # chest pocket (char right)

    bl = p["belt"]
    bl.rect(-6, 62, 5, 64, "r2"); bl.rect(-6, 62, 5, 62, "r1"); bl.rect(3, 62, 5, 64, "x2"); bl.px(3, 62, "x1")
    if right:
        bl.rect(-5, 64, -1, 73, "r2"); bl.rect(-5, 64, -5, 73, "r1"); bl.rect(-5, 67, -1, 67, "r1")
    else:
        bl.rect(-4, 64, 0, 68, "r2"); bl.rect(-4, 64, 0, 64, "r1"); bl.px(-2, 66, "x3")  # pouch

    a = p["arms"]
    a.shaded(-3, 40, 2, 59, "c1", "c2", "c3", 2, 1)
    a.trim(-3, 2, 60); a.rect(-3, 61, 2, 61, "t3")
    a.shaded(-2, 62, 2, 66, "s1", "s2", "s3", 1, 1); a.px(3, 64, "s2")

    f = p["firearm"]
    if right:
        f.rect(-4, 58, -1, 63, "k1"); f.rect(-4, 58, -4, 63, "x3"); f.rect(-3, 60, -1, 60, "x3")
        f.rect(-4, 64, -2, 72, "x2"); f.rect(-4, 64, -4, 72, "x1"); f.rect(-2, 64, -2, 72, "x3")
        f.rect(-1, 69, -1, 71, "k1")                                           # trigger guard
    else:
        f.rect(-9, 60, -7, 64, "k1"); f.rect(-9, 60, -9, 64, "x3"); f.px(-8, 62, "x3")  # grip peeks behind

    fc = p["face"]
    fc.rows({**{y: (-1, 7) for y in range(18, 23)}, **{y: (-1, 8) for y in range(23, 28)},
             **{y: (-1, 7) for y in range(28, 31)}, 31: (0, 6), 32: (1, 5), 33: (2, 4)}, "s2")
    fc.px(9, 26, "s2"); fc.px(9, 27, "s3")                                    # nose
    fc.rect(-1, 18, 1, 23, "s3"); fc.rect(0, 24, 1, 27, "s3"); fc.px(0, 25, "s4")  # ear
    fc.rect(-2, 33, 3, 37, "s3")
    fc.rect(5, 24, 6, 26, "e2"); fc.px(6, 24, "e1"); fc.rect(6, 30, 7, 30, "m1")

    sc = p["scarf"]
    sc.rows({34: (-3, 5), **{y: (-5, 6) for y in range(35, 41)}, 41: (-4, 5)}, "w1")
    sc.shaded(-5, 35, 6, 41, "w1", "w1", "w3", 1, 1)
    for ff in range(-4, 6, 2):
        sc.px(ff, 38, "w2")
    if right:
        sc.rows({y: (-9, -6) for y in range(37, 43)}, "w2"); sc.rect(-9, 42, -6, 42, "w3")
    else:                                                                     # long tail streams back
        sc.rows({**{y: (-10, -6) for y in range(36, 42)}, **{y: (-13, -7) for y in range(42, 47)},
                 **{y: (-14, -9) for y in range(47, 52)}}, "w1")
        sc.rect(-14, 47, -9, 47, "w2"); sc.rect(-13, 44, -7, 44, "w2"); sc.rect(-14, 51, -9, 51, "w3")

    h = p["hair"]
    h.rows({8: (-4, 3), 9: (-7, 5), 10: (-8, 6), **{y: (-9, 7) for y in range(11, 17)},
            **{y: (-10, 8) for y in range(17, 21)}, 21: (-10, 1), **{y: (-10, 0) for y in range(22, 26)},
            **{y: (-10, -1) for y in range(26, 31)}, 31: (-9, -4), 32: (-8, -5), 33: (-7, -6)}, "n2")
    h.rows({21: (5, 7), 22: (6, 7)}, "n2")                                     # bang spike
    h.rows({9: (-5, 1), 10: (-6, 0), 11: (-7, -2), 12: (-8, -4)}, "n1")
    h.rect(-10, 17, -9, 30, "n3" if right else "n1")
    h.rows({17: (2, 8), 18: (3, 7)}, "n3" if right else "n1")
    for ff in (-6, -3):
        h.rect(ff, 20, ff, 29, "n3")
    if right:
        h.rows({23: (1, 1), 24: (1, 1)}, "n2")                                # sideburn (char right)
    else:
        h.rows({31: (-3, -2), 32: (-3, -3)}, "n2")                            # longer layered nape (char left)

    g = p["goggles"]
    g.rect(-9, 15, 7, 16, "g2")
    g.rect(2, 12, 8, 17, "g1"); g.rect(3, 13, 7, 16, "l2"); g.rect(3, 13, 4, 14, "l1")
    g.rect(-8, 14, -6, 17, "g1")                                              # strap clip


def finish(Ls):
    """Jiang v01 outline rule (outer silhouette, layer's darkest colour) + hidden guides."""
    comp = S.compose_layers(Ls)
    opaque = comp[..., 3] == 255
    for n, k in OUTLINE.items():
        m = Ls[n].a[..., 3] == 255
        top = S.compose_layers(Ls, above=n)[..., 3] == 255
        for y, x in zip(*np.nonzero(m & ~top)):
            if any(not (0 <= y + dy < H and 0 <= x + dx < W) or not opaque[y + dy, x + dx]
                   for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                Ls[n].px(x, y, k)
    gd = Ls["guides"].a
    gd[0, :] = gd[H - 1, :] = gd[:, 0] = gd[:, W - 1] = (*S.GUIDE_RGB, 255)
    for y in BODY_ROWS:
        for x in (1, 2, 3, W - 4, W - 3, W - 2):
            gd[y, x] = (*S.GUIDE_RGB, 255)
    gd[PIN[1], PIN[0]] = (*S.GUIDE_RGB, 255)
    return {n: Ls[n].a for n in LAYERS}


def draw(d):
    Ls = {n: L() for n in LAYERS}
    {"south": draw_south, "north": draw_north}.get(d, lambda x: draw_side(x, d))(Ls)
    return finish(Ls)


# ------------------------------------------------------------------ package
def fix_pxo_metadata(pxo, d):
    """Male helper hardcodes its export/palette names; rewrite for Lin Que <d>, keep entry order and dates."""
    src = zipfile.ZipFile(io.BytesIO(pxo))
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename == "data.json":
                j = json.loads(data)
                j["export_profile"]["file_name"] = json.dumps(f"lin-que-{d}-idle-static-v01")
                pal = json.loads(j["user_data"])["declared_palette"]
                pal.update(name=f"lin-que-{d}-v01", comment=f"declared palette (lin-que native {d} v01)")
                j["user_data"] = json.dumps({"declared_palette": pal, "actor_id": ACTOR, "direction": d,
                                             "status": "UNAPPROVED"})
                j["current_layer"] = LAYERS.index("hair")
                data = json.dumps(j, separators=(",", ":")).encode()
            z.writestr(zipfile.ZipInfo(info.filename, ZIP_DT), data, zipfile.ZIP_DEFLATED)
    return out.getvalue()


def artifacts(d):
    hp = S.load_helper()
    hp.ZIP_DT, hp.LAYERS, hp.PAL = ZIP_DT, LAYERS, PAL
    blobs = draw(d)
    full = S.compose_layers(blobs)
    png = hp.png_bytes(full)
    pxo = fix_pxo_metadata(hp.make_pxo(blobs, png), d)
    ora = hp.make_ora(blobs, png)
    pal = (json.dumps({"actor_id": ACTOR, "name": f"lin-que-{d}-v01", "colors": PAL}, indent=2) + "\n").encode()
    return hp, blobs, full, png, pxo, ora, pal


def visible_texels(blobs):
    owner = np.full((H, W), -1)
    roles = [n for n in LAYERS if n != "guides"]
    for i, n in enumerate(roles):
        owner[blobs[n][..., 3] == 255] = i
    return {n: int((owner == i).sum()) for i, n in enumerate(roles)}


def gates(d, r):
    hp, blobs, full, png, pxo, ora, pal = r
    g = S.gates(hp, blobs, full, png, pxo, ora)
    with zipfile.ZipFile(io.BytesIO(pxo)) as z:
        dj = z.read("data.json")
    g["pxo_no_jiang_metadata"] = b"jiang" not in dj
    vis = visible_texels(blobs)
    g["visible_role_texels"] = vis
    g["genuine_visible_role_layers"] = sum(v >= MIN_VISIBLE for v in vis.values())
    g["genuine_visible_role_layers_ge_8"] = g["genuine_visible_role_layers"] >= 8
    g["guides_hidden_in_pxo_ora"] = "guides" in g["ora_hidden"]
    face = blobs["face"]; fm = face[..., 3] == 255
    fcols = {tuple(c) for c in face[fm][:, :3]}
    eye = {S.rgb("e1"), S.rgb("e2"), S.rgb("m1")}
    g["north_face_no_eyes_or_mouth"] = (not (fcols & eye)) if d == "north" else None
    g["face_has_eye"] = bool(fcols & eye) if d != "north" else None
    return g


HARD = S.HARD + ["genuine_visible_role_layers_ge_8", "guides_hidden_in_pxo_ora", "pxo_no_jiang_metadata"]


def manifest(d, files, g):
    m = {"actor_id": ACTOR, "content_id": f"content.char.lin-que.static-{d}", "status": "UNAPPROVED",
         "direction": d, "pose": "idle-static", "canvas": [W, H], "pivot": list(PIN), "body_rows": list(BODY_ROWS),
         "display_scale": S.DISPLAY_SCALE, "logical_height_px": (BODY_ROWS[1] - BODY_ROWS[0] + 1) * S.DISPLAY_SCALE,
         "layers": [{"name": n, "visible": n != "guides"} for n in LAYERS],
         "face_layer_role": "ears and nape only (no eyes)" if d == "north" else
                            ("front face, two eyes, nose, mouth, neck" if d == "south" else "profile head, one eye, nose, mouth, ear"),
         "view_notes": {"south": "front: goggles above forehead, layered bangs, white scarf with knot and tail on "
                                 "char-left (screen right), capelet with trim row, split coat tails, holster + "
                                 "compact firearm on char-right hip (screen left), pouch on char-left",
                        "west": "character's LEFT side: long scarf tail streaming back, belt pouch, firearm grip "
                                "only peeking behind the back, longer layered nape",
                        "east": "character's RIGHT side: holster with silver slide and black grip, thigh strap, "
                                "chest pocket, sideburn, short far-side scarf tail",
                        "north": "back: cape over the back with pale diamond motif and trim hem, goggle strap "
                                 "buckle, layered nape spikes, scarf tail on screen left, holster on screen right"}[d],
         "files": {k: {"file": fname(d, *FILE_KEYS[k]), "rawsha256": sha(b)} for k, b in files.items()},
         "colour_count": g["colour_count"], "genuine_visible_role_layers": g["genuine_visible_role_layers"],
         "portrait_ref": {"file": PORTRAIT_REL, "expected_sha256": PORTRAIT_SHA,
                          "use": "identity reference only (concept); no pixels sampled"},
         "south_baseline": {"author_tool": "tools/" + os.path.basename(__file__), "preserved_byte_exact": None,
                            "note": "first Lin Que native set; south authored in this same tool"},
         "author_tool": "tools/" + os.path.basename(__file__), "serialization_helper": S.HELPER_REL,
         "pixel_source": "code-authored native pixels, declared palette (shared by all four directions)",
         "limitations": "technical source only; no runtime wiring, no motion, no creator art approval"}
    return (json.dumps(m, indent=2) + "\n").encode()


FILE_KEYS = {"png": ("static", "png"), "pxo": ("edit", "pxo"), "ora": ("edit", "ora"), "palette": ("palette", "json")}


def build_all():
    res = {}
    for d in DIRS:
        r1, r2 = artifacts(d), artifacts(d)
        g = gates(d, r1)
        g["deterministic_rebuild"] = all(a == b for a, b in zip(r1[3:], r2[3:]))
        files = dict(zip(("png", "pxo", "ora", "palette"), r1[3:]))
        man = manifest(d, files, g)
        named = {f"{OUT_REL}/{d}/{fname(d, *FILE_KEYS[k])}": b for k, b in files.items()}
        named[f"{OUT_REL}/{d}/{fname(d, 'manifest', 'json')}"] = man
        res[d] = (r1, g, named)
    west, east = res["west"][0][2], res["east"][0][2]
    diff = int((east != west[:, ::-1]).any(-1).sum())
    batch = {"actor_id": ACTOR, "status": "UNAPPROVED", "run": f"{STAMP}-{RUN_ID}", "directions": list(DIRS),
             "packages": {d: {rel: sha(b) for rel, b in res[d][2].items()} for d in DIRS},
             "east_vs_mirrored_west_differing_texels": diff,
             "reused_tool_pins": {JIANG_TOOL_REL: JIANG_TOOL_SHA},
             "author_tool": "tools/" + os.path.basename(__file__)}
    batch_rel = f"{OUT_REL}/{SLUG}_{ACTOR}_four-direction-batch-manifest_unapproved-v01_{STAMP}-{uid('batch')}.json"
    return res, diff, {batch_rel: (json.dumps(batch, indent=2) + "\n").encode()}


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    jiang_ok = sha(open(fs(JIANG_TOOL_REL), "rb").read()) == JIANG_TOOL_SHA
    res, diff, batch = build_all()
    report, bad = {}, [] if jiang_ok else ["jiang_tool_pin"]
    for d in DIRS:
        g = res[d][1]
        fails = [k for k in HARD + ["deterministic_rebuild"] if not g[k]]
        if d == "north" and not g["north_face_no_eyes_or_mouth"]:
            fails.append("north_face_no_eyes_or_mouth")
        if d != "north" and not g["face_has_eye"]:
            fails.append("face_has_eye")
        bad += [f"{d}:{k}" for k in fails]
        report[d] = {k: g[k] for k in ("body_rows", "colour_count", "genuine_visible_role_layers", "visible_role_texels",
                                       "binary_alpha", "no_opaque_border", "pin_inside_feet_span",
                                       "all_colours_declared", "pxo_no_male_metadata", "pxo_no_jiang_metadata",
                                       "ora_hidden", "deterministic_rebuild")}
        report[d]["hard_failures"] = fails
    if diff < 200:
        bad.append(f"east_not_blind_mirror ({diff} texels)")
    files = {rel: b for d in DIRS for rel, b in res[d][2].items()}
    files.update(batch)
    if cmd == "build":
        if bad:
            raise SystemExit(f"hard gates failed: {bad}")
        for rel, data in files.items():
            p = fs(rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            if os.path.exists(p) and open(p, "rb").read() != data:
                raise SystemExit(f"refusing to overwrite different file {rel}")
            open(p, "wb").write(data)
        open(fs(OUT_REL + "/.gdignore"), "ab").close()
        from PIL import Image
        qa = {}
        os.makedirs(fs(QA_REL), exist_ok=True)
        for d in DIRS:
            rel = f"{QA_REL}/{SLUG}_{ACTOR}_{d}-preview-x6_unapproved-v01_{STAMP}-{uid(d, 'preview')}.png"
            Image.fromarray(res[d][0][2], "RGBA").resize((W * 6, H * 6), Image.NEAREST).save(fs(rel))
            qa[rel] = sha(open(fs(rel), "rb").read())
        listing = {"outputs": {rel: sha(b) for rel, b in sorted(files.items())}, "qa_previews_nonsource": qa,
                   "hash": "sha256 of raw bytes"}
        lp = f"{QA_REL}/{SLUG}_{ACTOR}_four-direction-output-paths-rawhashes_unapproved-v01_{STAMP}-{uid('paths')}.json"
        open(fs(lp), "wb").write((json.dumps(listing, indent=2) + "\n").encode())
    disk = {rel: (sha(open(fs(rel), "rb").read()) == sha(b)) if os.path.exists(fs(rel)) else None
            for rel, b in files.items()}
    report["east_vs_mirrored_west_differing_texels"] = diff
    report["jiang_tool_pin_ok"] = jiang_ok
    report["disk_matches_rebuild"] = disk
    report["hard_failures"] = bad
    print(json.dumps(report, indent=1))
    ok = not bad and all(v is True for v in disk.values())
    print("LIN_QUE_FOUR_DIRECTION_V01_" + ("ALL_OK" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
