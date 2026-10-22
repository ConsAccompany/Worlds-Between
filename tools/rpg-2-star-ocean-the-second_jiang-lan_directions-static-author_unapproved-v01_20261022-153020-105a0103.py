"""Jiang Lan WEST / NORTH / EAST idle statics, native 80x112 source packages (UNAPPROVED v01).

Reuses the south v01 author (L primitives, palette, layer roles, compose, gates) and, through it, the male
v8pair serializers (png/pxo/ora). Authored geometry per view: one profile builder drawn in forward
coordinates with side-specific details (east = character's right: long vest panel, rectangular case,
swept hair, trouser panel; west = character's left: short vest + diagonal strap, round device, hanging
strap, cropped temple, back strap edge), and a separate back view (vest back panel, orange vertical strap,
rear neck/ears in the face layer, no eyes). Lighting stays upper-left in every view. South files are only
read and hash-pinned, never written.

  python -X utf8 -I <this> build   # writes new files only (refuses to overwrite different bytes)
  python -X utf8 -I <this> check   # rebuilds twice in memory and compares with files on disk
"""
import hashlib, importlib.util, io, json, os, sys, zipfile
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG, ACTOR = "rpg-2-star-ocean-the-second", "jiang-lan"
STAMP, RUN_ID = "20261022-153020", "105a0103"
OUT_REL = "game/assets/characters/jiang-lan-native-directions-v01"
QA_REL = "outputs/jiang38/claude"
SOUTH_TOOL_REL = "tools/rpg-2-star-ocean-the-second_jiang-lan_south-static-author_unapproved-v01_20261021-235007-514b9771.py"
SOUTH_DIR = "game/assets/characters/jiang-lan-native-south-v01/"
SOUTH_PINS = {  # raw sha256; south v01 must stay byte-exact
    SOUTH_TOOL_REL: "35005f3c904802251c773838d61068d4aea847c993f6e354676e88a599db69b4",
    SOUTH_DIR + "rpg-2-star-ocean-the-second_jiang-lan_south-idle-static_unapproved-v01_20261021-235007-5f1c2a90.png": "fb7de93bbfb9dd9e50fde752588b82e3baa5070cbf46b7003f051ac9a7433092",
    SOUTH_DIR + "rpg-2-star-ocean-the-second_jiang-lan_south-idle-static-editable_unapproved-v01_20261021-235007-a3e07b14.pxo": "530ca642dbc4a0189de008e1b71a6912c547b72fa9a3bb8e2833e0c7f5d82d7e",
    SOUTH_DIR + "rpg-2-star-ocean-the-second_jiang-lan_south-idle-static-editable_unapproved-v01_20261021-235007-c81d4e62.ora": "6cba6e8b01c34b96b949f698165707b56e3a379e9cc75dae121aaee2c22c775c",
    SOUTH_DIR + "rpg-2-star-ocean-the-second_jiang-lan_south-idle-palette_unapproved-v01_20261021-235007-2b9f6d07.json": "c095f79ab6788fa1a656105b15185ae4794fdc0f3fddee32dbec411937a3ec75",
    SOUTH_DIR + "rpg-2-star-ocean-the-second_jiang-lan_south-idle-manifest_unapproved-v01_20261021-235007-e4a7c3d9.json": "1438eb5df00373f2a3f3af8fa8a234cd9f325239ae30411a4644f3bba93aae77",
}
DIRS = ("west", "north", "east")
ZIP_DT = (2026, 10, 22, 15, 30, 20)
MIN_VISIBLE = 12  # texels a role layer must show in the composite to count as genuine


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


S = load(SOUTH_TOOL_REL, "jiang_south_v01")
W, H, PIN, BODY_ROWS, LAYERS, L = S.W, S.H, S.PIN, S.BODY_ROWS, S.LAYERS, S.L


# ------------------------------------------------------------------ profile (west/east)
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


def draw_side(Ls, d):
    s = 1 if d == "east" else -1
    right = d == "east"                  # east shows the character's right side, west the left side
    p = {n: P(Ls[n], s) for n in LAYERS}

    # boots: far foot peeks ahead (darker), near boot with orange strap, toe panel, sole and heel
    b = p["boots"]
    b.rect(5, 97, 7, 101, "c4"); b.rect(5, 102, 7, 102, "o3"); b.rect(5, 103, 7, 103, "o3")
    b.shaded(-4, 89, 1, 99, "c2", "c3", "k1")
    b.shaded(-5, 96, 5, 101, "c2", "c3", "k1")
    b.rect(-4, 92, 1, 92, "o2"); b.px(-4, 92, "o1")
    b.rect(1, 97, 4, 98, "g1")
    b.rect(-5, 102, 5, 102, "o2"); b.rect(-5, 103, 5, 103, "o3")
    b.rect(-5, 100, -4, 101, "o2")

    # trousers: hips, far leg (darker, slightly forward), near leg
    t = p["trousers"]
    t.rect(-6, 61, 5, 68, "c2")
    t.rect(1, 66, 4, 90, "c3"); t.rect(1, 69, 1, 90, "c4")
    t.shaded(-5, 66, 1, 90, "c1", "c2", "c3")
    t.rect(-4, 86, 0, 87, "c3")                                                   # cuff gather
    t.px(1, 76, "c1"); t.px(0, 77, "c3")                                          # knee crease
    if right:                                                                     # off-white outer panel
        t.rect(-4, 72, -2, 88, "v2"); t.rect(-4, 72, -4, 88, "v1"); t.rect(-2, 72, -2, 88, "v3")
    else:                                                                         # cargo pocket
        t.rect(-3, 76, 0, 81, "c3"); t.rect(-3, 76, 0, 76, "c1")

    # shirt: torso profile, high collar with orange inner edge at the front
    sh = p["shirt"]
    sh.shaded(-6, 38, 5, 63, "c1", "c2", "c3")
    sh.rect(-3, 35, 2, 39, "c3"); sh.rect(-2, 35, 1, 35, "c2")
    sh.rect(2, 36, 2, 39, "o2" if right else "o3")

    # vest: right side long panel with pockets; left side short panel, tab, diagonal strap, back strap edge
    v = p["vest"]
    if right:
        v.shaded(-6, 39, 4, 63, "v1", "v2", "v3")
        v.rect(4, 41, 4, 63, "v4"); v.rect(-4, 40, -4, 63, "v3")
        v.rect(0, 46, 3, 50, "v3"); v.rect(0, 46, 3, 46, "v4"); v.px(2, 48, "o2")
        v.rect(0, 53, 2, 57, "v3"); v.rect(0, 53, 2, 53, "v4")
    else:
        v.shaded(-6, 40, 4, 56, "v1", "v2", "v3")
        v.rect(4, 41, 4, 56, "v4"); v.rect(-4, 41, -4, 56, "v3")
        v.rect(1, 44, 3, 47, "c3"); v.px(2, 45, "o1")
        for i in range(10):
            v.px(3 - (i * 6) // 10, 47 + i, "c3")
        v.rect(-6, 40, -6, 63, "o2"); v.rect(-6, 63, -6, 63, "o3"); v.px(-6, 40, "o1")
        v.rect(3, 61, 4, 72, "o2"); v.rect(3, 61, 3, 72, "o1"); v.rect(3, 72, 4, 72, "o3")
    v.rect(-6, 58, 5, 60, "c4"); v.rect(-6, 58, 5, 58, "c3")                     # belt

    # near arm: sleeve, orange rolled cuff, forearm, fingerless glove, fingertips
    a = p["arms"]
    a.rect(-3, 37, 2, 39, "c2")
    a.shaded(-3, 40, 1, 49, "c1", "c2", "c3")
    a.rect(-3, 50, 1, 53, "o2"); a.rect(-3, 50, 1, 50, "o1"); a.rect(-3, 53, 1, 53, "o3")
    a.shaded(-2, 54, 1, 58, "s1", "s2", "s3")
    a.rect(-3, 59, 2, 64, "k1"); a.rect(-2, 59, 1, 59, "c3"); a.rect(-2, 61, 1, 61, "c3")
    a.rect(-2, 65, 1, 66, "s2"); a.px(1, 66, "s3")

    # devices: right hip rectangular folding case, left hip round hinged mechanism
    dv = p["devices"]
    if right:
        dv.shaded(2, 61, 6, 70, "v2", "g1", "c3")
        dv.rect(4, 61, 4, 70, "o2"); dv.rect(2, 65, 6, 65, "c4"); dv.px(5, 62, "o1")
    else:
        cf, cy = 5, 65
        for y in range(cy - 4, cy + 5):
            for f in range(cf - 3, cf + 4):
                e = (f - cf) ** 2 * 2 + (y - cy) ** 2                              # seen edge-on: narrower ellipse
                if e <= 18:
                    dv.px(f, y, "o2" if e >= 11 else ("c3" if e <= 2 else ("v2" if y < cy else "g1")))
        dv.px(cf, cy, "o1"); dv.rect(cf - 1, cy + 4, cf, cy + 5, "c3")              # hinge knuckle

    # face: head profile, ear, one visible eye, nose, smile, neck
    fc = p["face"]
    fc.rect(-3, 33, 1, 37, "s3"); fc.rect(0, 33, 1, 35, "s2")
    head = {17: (-6, 5), 18: (-6, 6), 19: (-6, 6), 20: (-6, 6), 21: (-6, 6), 22: (-6, 6), 23: (-6, 6), 24: (-6, 6),
            25: (-6, 6), 26: (-6, 6), 27: (-5, 7), 28: (-5, 7), 29: (-5, 6), 30: (-4, 6), 31: (-3, 6), 32: (-2, 6),
            33: (-1, 5), 34: (0, 4)}
    fc.rows(head, "s2")
    for y, (f0, f1) in head.items():
        lo, hi = fc.span(f0, f1)
        if y < 30:
            fc.l.px(lo, y, "s1"); fc.l.px(lo + 1, y, "s1")
        fc.l.px(hi, y, "s3")
    fc.rows({31: (0, 3), 32: (1, 3), 33: (1, 2)}, "s3")                         # jaw shade
    fc.rect(-2, 22, 0, 27, "s3"); fc.rect(-1, 23, 0, 26, "s2"); fc.px(-1, 25, "s4")  # ear
    fc.rect(2, 24, 5, 24, "h4"); fc.rect(2, 23, 5, 23, "h3")                     # lash + brow
    fc.rect(3, 25, 5, 26, "e1"); fc.rect(3, 25, 4, 26, "e2"); fc.px(3, 25, "h4")  # eye
    fc.px(6, 29, "s3"); fc.px(7, 27, "s1")                                        # nostril, nose tip light
    fc.rect(4, 32, 6, 32, "m1"); fc.px(3, 31, "m1")                               # smile

    # hair: swept-back spikes; right side keeps the swept mass + sideburn, left side shows the cropped temple
    h = p["hair"]
    h.rect(-8, 12, 6, 19, "h2"); h.rect(-7, 11, 4, 11, "h2")
    h.rows({10: (-6, -3), 9: (-5, -4), 8: (-5, -5)}, "h2")
    h.rows({10: (0, 3), 9: (1, 2)}, "h2")
    h.rows({12: (-10, -8), 13: (-11, -8), 14: (-10, -8), 11: (-11, -9)}, "h3")     # trailing tips
    h.rows({20: (-8, -2), 21: (-8, -2), 22: (-8, -3), 23: (-8, -3), 24: (-7, -3), 25: (-7, -3), 26: (-6, -4)}, "h2")
    h.rect(-8, 18, -7, 25, "h3"); h.rows({12: (-4, 1), 11: (-3, 0)}, "h1"); h.px(-4, 9, "h1")
    if right:
        h.rows({19: (3, 7), 20: (4, 7), 21: (5, 7), 22: (6, 7)}, "h2"); h.px(5, 20, "h1")  # forelock
        h.rect(1, 19, 2, 25, "h2"); h.rect(1, 24, 1, 25, "h3")                     # sideburn
        h.rows({14: (-12, -9), 15: (-11, -9)}, "h2")                               # fuller sweep
    else:
        h.rows({19: (4, 7), 20: (5, 6)}, "h2")
        h.rect(-2, 18, 1, 21, "h3"); h.rect(1, 22, 1, 23, "h3"); h.px(0, 19, "h4"); h.px(-1, 21, "h4")  # cropped temple

    # goggles: strap round the head, one lens cup at the forehead front
    g = p["goggles"]
    g.rect(-8, 16, 2, 16, "g2"); g.rect(-8, 17, 2, 17, "g1")
    g.rect(2, 13, 7, 18, "o2"); g.rect(2, 13, 7, 13, "o1"); g.rect(2, 18, 7, 18, "o3")
    g.rect(6, 14, 7, 17, "l2"); g.rect(6, 14, 6, 15, "l1")
    g.rect(-7, 15, -6, 18, "o3")                                                  # strap buckle


# ------------------------------------------------------------------ back (north)
def draw_north(Ls):
    b = Ls["boots"]
    for x0, x1 in ((28, 38), (42, 52)):
        b.shaded(x0 + 1, 89, x1 - 1, 99, "c2", "c3", "k1")
        b.rect(x0, 96, x1, 101, "c3"); b.rect(x0, 96, x0 + 1, 99, "c2")
        b.hline(x0 + 1, x1 - 1, 92, "o2"); b.px(x0 + 1, 92, "o1")
        b.rect(x0 + 3, 97, x1 - 3, 99, "g1"); b.hline(x0 + 3, x1 - 3, 97, "v3")    # heel counter
        b.rect((x0 + x1) // 2 - 1, 89, (x0 + x1) // 2, 90, "o2")                    # pull tab
        b.hline(x0, x1, 102, "o2"); b.hline(x0, x1, 103, "o3"); b.px(x0, 102, "o1")
    b.rect(28, 100, 30, 101, "o2"); b.rect(50, 100, 52, 101, "o2")

    t = Ls["trousers"]
    t.rect(30, 61, 50, 68, "c2")
    t.shaded(29, 66, 39, 90, "c1", "c2", "c3")
    t.shaded(41, 66, 51, 90, "c1", "c2", "c3")
    t.rect(48, 72, 51, 88, "v2"); t.vline(48, 72, 88, "v1"); t.vline(51, 72, 88, "v3")  # char-right outer panel
    t.vline(40, 61, 90, "c4")                                                       # seat seam / inseam
    t.rect(32, 63, 37, 66, "c3"); t.hline(32, 37, 63, "c1")                        # back pockets
    t.rect(43, 63, 47, 66, "c3"); t.hline(43, 47, 63, "c1")
    t.rows({86: (30, 38), 87: (30, 38)}, "c3"); t.rows({86: (42, 50), 87: (42, 50)}, "c3")

    s = Ls["shirt"]
    s.shaded(30, 38, 50, 63, "c1", "c2", "c3")
    s.rect(36, 35, 44, 38, "c3"); s.hline(36, 44, 35, "o3"); s.hline(37, 43, 36, "c2")

    v = Ls["vest"]
    v.shaded(29, 39, 51, 56, "v1", "v2", "v3")
    v.shaded(41, 57, 51, 63, "v1", "v2", "v3")                                      # longer char-right tail
    v.hline(30, 50, 44, "v3"); v.hline(30, 50, 45, "v4")                           # yoke seam
    v.vline(40, 46, 63, "v3")
    v.rect(35, 39, 36, 63, "o2"); v.vline(35, 39, 63, "o1"); v.hline(35, 36, 63, "o3")  # orange vertical strap
    v.rect(43, 49, 48, 52, "v3"); v.hline(43, 48, 49, "v4"); v.px(47, 50, "o2")    # back tool loop
    v.rect(29, 58, 51, 60, "c4"); v.hline(29, 51, 58, "c3"); v.rect(39, 58, 41, 60, "c3")  # belt + loop

    a = Ls["arms"]
    for x0, x1, hi, dk in ((23, 28, "c1", "c3"), (52, 57, "c2", "c3")):
        a.rect(x0 + 1, 38, x1, 40, "c2")
        a.shaded(x0, 40, x1, 49, hi, "c2", dk)
        a.hline(x0 + 1, x1 - 1, 46, "c3")                                           # elbow crease
        a.rect(x0, 50, x1, 53, "o2"); a.hline(x0, x1, 50, "o1"); a.hline(x0, x1, 53, "o3")
        a.shaded(x0 + 1, 54, x1 - 1, 58, "s1", "s2", "s3", 1, 1)
        a.rect(x0, 59, x1, 64, "k1"); a.hline(x0 + 1, x1 - 1, 62, "c3")
        a.rect(x0 + 1, 65, x1 - 1, 65, "s3")

    d = Ls["devices"]
    d.shaded(45, 61, 50, 70, "v2", "g1", "c3"); d.vline(47, 61, 70, "o2"); d.hline(45, 50, 65, "c4")  # case back
    cx, cy = 33, 65
    for y in range(cy - 4, cy + 5):
        for x in range(cx - 4, cx + 5):
            r2 = (x - cx) ** 2 + (y - cy) ** 2
            if r2 <= 18:
                d.px(x, y, "o2" if r2 >= 11 else ("g1" if r2 > 2 else "c3"))         # back plate, no lens
    d.rect(cx - 5, cy - 1, cx - 4, cy + 1, "c3")
    d.rect(cx - 1, cy - 2, cx, cy - 1, "l2"); d.px(cx - 1, cy - 2, "l1")              # amber status lamp
    d.rect(46, 67, 49, 68, "e1"); d.hline(46, 49, 69, "v3")                         # reflective case label

    f = Ls["face"]                                                                  # rear neck + ears only
    f.rect(36, 28, 44, 37, "s3"); f.rect(37, 28, 39, 34, "s2"); f.hline(36, 44, 30, "s4")
    f.rect(28, 22, 29, 27, "s2"); f.px(28, 22, "s1"); f.px(29, 26, "s3")
    f.rect(51, 22, 52, 27, "s3"); f.px(51, 24, "s4")

    h = Ls["hair"]
    h.rect(30, 12, 50, 27, "h2")
    h.rows({11: (31, 49), 10: (32, 36), 9: (33, 35), 8: (34, 34)}, "h2")
    h.rows({10: (39, 43), 9: (40, 42), 8: (41, 41)}, "h2")
    h.rows({11: (45, 49), 10: (46, 49), 9: (47, 48)}, "h3")
    h.rows({13: (50, 54), 14: (50, 53), 12: (52, 55), 11: (53, 55)}, "h2")          # sweep to char-right
    h.rect(49, 15, 51, 25, "h2"); h.vline(51, 15, 25, "h3")
    h.rows({28: (35, 45), 29: (37, 43)}, "h3")                                      # nape taper
    h.rows({12: (32, 38), 11: (33, 36)}, "h1"); h.px(34, 9, "h1"); h.px(41, 9, "h1")
    h.rows({20: (32, 36), 22: (34, 38), 24: (32, 35)}, "h1")                         # back spike lights
    h.rows({19: (42, 48), 21: (44, 49), 23: (43, 48), 25: (44, 49)}, "h3")
    h.rect(29, 18, 31, 23, "h3"); h.px(30, 20, "h4"); h.px(31, 22, "h4")            # cropped char-left temple
    h.rect(29, 12, 30, 17, "h3")

    g = Ls["goggles"]
    g.hline(28, 52, 16, "g2"); g.hline(28, 52, 17, "g1")
    g.rect(39, 15, 42, 18, "o2"); g.hline(39, 42, 15, "o1"); g.rect(40, 16, 41, 17, "g2")  # strap buckle


def finish(Ls):
    """South v01 outline rule (outer silhouette, layer's darkest colour) + hidden guides."""
    comp = S.compose_layers(Ls)
    opaque = comp[..., 3] == 255
    for n, k in S.OUTLINE.items():
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
    draw_north(Ls) if d == "north" else draw_side(Ls, d)
    return finish(Ls)


# ------------------------------------------------------------------ package
def fix_pxo_metadata(pxo, d):
    """Male helper hardcodes its export/palette names; rewrite for Jiang <d>, keep entry order and dates."""
    src = zipfile.ZipFile(io.BytesIO(pxo))
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename == "data.json":
                j = json.loads(data)
                j["export_profile"]["file_name"] = json.dumps(f"jiang-lan-{d}-idle-static-v01")
                pal = json.loads(j["user_data"])["declared_palette"]
                pal.update(name=f"jiang-lan-{d}-v01", comment=f"declared palette (jiang-lan native {d} v01)")
                j["user_data"] = json.dumps({"declared_palette": pal, "actor_id": ACTOR, "direction": d,
                                             "status": "UNAPPROVED"})
                j["current_layer"] = LAYERS.index("hair")
                data = json.dumps(j, separators=(",", ":")).encode()
            z.writestr(zipfile.ZipInfo(info.filename, ZIP_DT), data, zipfile.ZIP_DEFLATED)
    return out.getvalue()


def artifacts(d):
    hp = S.load_helper()
    hp.ZIP_DT = ZIP_DT
    blobs = draw(d)
    full = S.compose_layers(blobs)
    png = hp.png_bytes(full)
    pxo = fix_pxo_metadata(hp.make_pxo(blobs, png), d)
    ora = hp.make_ora(blobs, png)
    pal = (json.dumps({"actor_id": ACTOR, "name": f"jiang-lan-{d}-v01", "colors": S.PAL}, indent=2) + "\n").encode()
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
    vis = visible_texels(blobs)
    g["visible_role_texels"] = vis
    g["genuine_visible_role_layers"] = sum(v >= MIN_VISIBLE for v in vis.values())
    g["genuine_visible_role_layers_ge_8"] = g["genuine_visible_role_layers"] >= 8
    g["guides_hidden_in_pxo_ora"] = "guides" in g["ora_hidden"]
    face = blobs["face"]; fm = face[..., 3] == 255
    fcols = {tuple(c) for c in face[fm][:, :3]}
    eye = {S.rgb("e1"), S.rgb("e2"), S.rgb("m1")}
    g["north_face_no_eyes_or_mouth"] = (not (fcols & eye)) if d == "north" else None
    g["side_face_has_eye"] = bool(fcols & eye) if d != "north" else None
    return g


HARD = S.HARD + ["genuine_visible_role_layers_ge_8", "guides_hidden_in_pxo_ora"]


def south_pin_state():
    out = {}
    for rel, want in SOUTH_PINS.items():
        p = fs(rel)
        out[rel] = os.path.exists(p) and sha(open(p, "rb").read()) == want
    return out


def manifest(d, files, g):
    m = {"actor_id": ACTOR, "content_id": f"content.char.jiang-lan.static-{d}", "status": "UNAPPROVED",
         "direction": d, "pose": "idle-static", "canvas": [W, H], "pivot": list(PIN), "body_rows": list(BODY_ROWS),
         "display_scale": S.DISPLAY_SCALE, "logical_height_px": (BODY_ROWS[1] - BODY_ROWS[0] + 1) * S.DISPLAY_SCALE,
         "layers": [{"name": n, "visible": n != "guides"} for n in LAYERS],
         "face_layer_role": "rear neck and ears only (no eyes)" if d == "north" else "profile head, one eye, nose, mouth",
         "view_notes": {"west": "character's LEFT side: short vest panel + diagonal strap, round hinged device, hanging "
                                "orange strap, cropped temple, back strap edge, cargo pocket",
                        "east": "character's RIGHT side: long vest panel + pockets, rectangular folding case, swept "
                                "hair mass + sideburn + forelock, off-white trouser panel",
                        "north": "back: vest back panel with longer char-right tail, orange vertical strap, strap "
                                 "buckle, case/device backs at hips, cropped char-left temple"}[d],
         "files": {k: {"file": fname(d, *FILE_KEYS[k]), "rawsha256": sha(b)} for k, b in files.items()},
         "colour_count": g["colour_count"], "genuine_visible_role_layers": g["genuine_visible_role_layers"],
         "portrait_ref": {"file": S.PORTRAIT_REL, "expected_sha256": S.PORTRAIT_SHA,
                          "use": "identity reference only; no pixels sampled"},
         "south_baseline": {"author_tool": SOUTH_TOOL_REL, "preserved_byte_exact": True},
         "author_tool": "tools/" + os.path.basename(__file__), "serialization_helper": S.HELPER_REL,
         "pixel_source": "code-authored native pixels, declared palette (shared with south v01)",
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
             "south_pins": SOUTH_PINS, "author_tool": "tools/" + os.path.basename(__file__)}
    batch_rel = f"{OUT_REL}/{SLUG}_{ACTOR}_directions-batch-manifest_unapproved-v01_{STAMP}-{uid('batch')}.json"
    return res, diff, {batch_rel: (json.dumps(batch, indent=2) + "\n").encode()}


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    pins_before = south_pin_state()
    res, diff, batch = build_all()
    report, bad = {}, []
    for d in DIRS:
        g = res[d][1]
        fails = [k for k in HARD + ["deterministic_rebuild"] if not g[k]]
        if d == "north" and not g["north_face_no_eyes_or_mouth"]:
            fails.append("north_face_no_eyes_or_mouth")
        if d != "north" and not g["side_face_has_eye"]:
            fails.append("side_face_has_eye")
        bad += [f"{d}:{k}" for k in fails]
        report[d] = {k: g[k] for k in ("body_rows", "colour_count", "genuine_visible_role_layers", "visible_role_texels",
                                       "binary_alpha", "pin_inside_feet_span", "all_colours_declared",
                                       "pxo_no_male_metadata", "ora_hidden", "north_face_no_eyes_or_mouth")}
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
        for d in DIRS:
            rel = f"{QA_REL}/{SLUG}_{ACTOR}_{d}-preview-x6_unapproved-v01_{STAMP}-{uid(d, 'preview')}.png"
            os.makedirs(os.path.dirname(fs(rel)), exist_ok=True)
            Image.fromarray(res[d][0][2], "RGBA").resize((W * 6, H * 6), Image.NEAREST).save(fs(rel))
            qa[rel] = sha(open(fs(rel), "rb").read())
        listing = {"outputs": {rel: sha(b) for rel, b in sorted(files.items())}, "qa_previews_nonsource": qa,
                   "hash": "sha256 of raw bytes", "south_pins_before": pins_before}
        lp = f"{QA_REL}/{SLUG}_{ACTOR}_directions-output-paths-rawhashes_unapproved-v01_{STAMP}-{uid('paths')}.json"
        open(fs(lp), "wb").write((json.dumps(listing, indent=2) + "\n").encode())
    disk = {rel: (sha(open(fs(rel), "rb").read()) == sha(b)) if os.path.exists(fs(rel)) else None
            for rel, b in files.items()}
    pins_after = south_pin_state()
    report["east_vs_mirrored_west_differing_texels"] = diff
    report["south_pins_exact_before_after"] = all(pins_before.values()) and all(pins_after.values())
    report["disk_matches_rebuild"] = disk
    report["hard_failures"] = bad
    print(json.dumps(report, indent=1))
    ok = not bad and all(v is True for v in disk.values()) and report["south_pins_exact_before_after"]
    print("JIANG_DIRECTIONS_V01_" + ("ALL_OK" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
