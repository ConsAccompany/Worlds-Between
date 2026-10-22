"""Jiang Lan SOUTH idle static, native 80x112 source package (UNAPPROVED v01).

Draws native pixels per role layer with a declared palette (no portrait resample, no generated pixels),
then writes PNG + layered PXO + ORA + palette JSON + manifest. Serialization (make_pxo/make_ora/png_bytes)
is reused from the male v8pair pilot tool via dynamic import; Jiang layer names, palette and export
metadata are set explicitly here.

  python -X utf8 -I <this> build   # writes new files only (refuses to overwrite different bytes)
  python -X utf8 -I <this> check   # rebuilds in memory and compares with files on disk
"""
import hashlib, importlib.util, io, json, os, sys, zipfile
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
ACTOR = "jiang-lan"
STAMP, RUN_ID = "20261021-235007", "514b9771"
W, H = 80, 112
PIN = (40, 104)
BODY_ROWS = (8, 103)
DISPLAY_SCALE = 0.5
OUT_DIR_REL = "game/assets/characters/jiang-lan-native-south-v01"
QA_DIR_REL = "outputs/jiang37/claude"
HELPER_REL = ("tools/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair-static-pilot-build-and-check_"
              "unapproved-v01_20261018-130225-f28bd26d.py")
PORTRAIT_REL = "outputs/rpg-2-star-ocean-the-second_jiang-lan_character-sheet_hairstyle-v02_20261013-161317-c21bd255.png"
PORTRAIT_SHA = "bbddf46f3c1370742c86d1934e36adf7969e5f43a4e6d67ddbf9ba8d44902e4a"
ZIP_DT = (2026, 10, 21, 23, 50, 6)

PAL = {  # declared palette; upper-left light
    "s1": "f4c9a0", "s2": "dca277", "s3": "b47652", "s4": "7c4a31",          # skin
    "h1": "7a5238", "h2": "513424", "h3": "33211a", "h4": "1c120d",          # hair
    "e1": "fff6e8", "e2": "6a4022", "m1": "8c4636",                          # eye white, iris, mouth
    "o1": "ffb050", "o2": "f07d1e", "o3": "b0520f",                          # orange accents
    "l1": "ffe0a0", "l2": "d08a3c",                                          # goggle lens
    "g1": "5c5c66", "g2": "2a2a32",                                          # goggle frame / strap
    "v1": "f2eee4", "v2": "d2cdc2", "v3": "a9a398", "v4": "6f6a63",          # off-white vest
    "c1": "62626a", "c2": "48484f", "c3": "33333a", "c4": "1e1e24",          # charcoal cloth
    "k1": "121216",                                                          # glove/boot black
}
LAYERS = ["boots", "trousers", "shirt", "vest", "arms", "devices", "face", "hair", "goggles", "guides"]
OUTLINE = {"boots": "k1", "trousers": "c4", "shirt": "c4", "vest": "v4", "arms": "c4", "devices": "c4",
           "face": "s4", "hair": "h4", "goggles": "g2"}
GUIDE_RGB = (255, 0, 255)


def name(purpose, ext, uid):
    return f"{SLUG}_{ACTOR}_{purpose}_unapproved-v01_{STAMP}-{uid}.{ext}"


NAMES = {"png": name("south-idle-static", "png", "5f1c2a90"), "pxo": name("south-idle-static-editable", "pxo", "a3e07b14"),
         "ora": name("south-idle-static-editable", "ora", "c81d4e62"), "palette": name("south-idle-palette", "json", "2b9f6d07"),
         "manifest": name("south-idle-manifest", "json", "e4a7c3d9")}


def rgb(k):
    h = PAL[k]
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load_helper():
    spec = importlib.util.spec_from_file_location("male_v8pair_helper", os.path.join(REPO, *HELPER_REL.split("/")))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.W, m.H, m.LAYERS, m.ZIP_DT = W, H, LAYERS, ZIP_DT
    m.PAL = PAL
    return m


# ------------------------------------------------------------------ drawing primitives
class L:
    def __init__(self):
        self.a = np.zeros((H, W, 4), np.uint8)

    def px(self, x, y, k):
        self.a[y, x, :3] = rgb(k); self.a[y, x, 3] = 255

    def rect(self, x0, y0, x1, y1, k):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, k)

    def hline(self, x0, x1, y, k):
        self.rect(x0, y, x1, y, k)

    def vline(self, x, y0, y1, k):
        self.rect(x, y0, x, y1, k)

    def shaded(self, x0, y0, x1, y1, lo, mid, dk, hi_w=1, dk_w=2):
        """mid fill, left highlight column(s), right shadow column(s)."""
        self.rect(x0, y0, x1, y1, mid)
        self.rect(x0, y0, x0 + hi_w - 1, y1, lo)
        self.rect(x1 - dk_w + 1, y0, x1, y1, dk)

    def rows(self, spans, k):
        """spans: {y: (x0, x1)}"""
        for y, (x0, x1) in spans.items():
            self.hline(x0, x1, y, k)


def draw():
    Ls = {n: L() for n in LAYERS}

    # boots (rows 89..103), orange heel/sole accents
    b = Ls["boots"]
    for x0, x1 in ((28, 38), (42, 52)):
        b.shaded(x0 + 1, 89, x1 - 1, 99, "c2", "c3", "k1")
        b.rect(x0, 96, x1, 101, "c3"); b.rect(x0, 96, x0 + 1, 99, "c2")
        b.hline(x0 + 1, x1 - 1, 92, "o2"); b.px(x0 + 1, 92, "o1")              # orange strap
        b.rect(x0 + 2, 97, x1 - 3, 98, "g1")                                    # grey toe panel
        b.hline(x0, x1, 102, "o2"); b.hline(x0, x1, 103, "o3"); b.px(x0, 102, "o1")  # sole
    b.rect(28, 100, 30, 101, "o2"); b.rect(50, 100, 52, 101, "o2")            # outer heel accents

    # trousers: baggy charcoal, off-white outer panel on viewer-left leg
    t = Ls["trousers"]
    t.rect(30, 61, 50, 68, "c2")
    t.shaded(29, 66, 39, 90, "c1", "c2", "c3")
    t.shaded(41, 66, 51, 90, "c1", "c2", "c3")
    t.rect(29, 72, 31, 88, "v2"); t.vline(29, 72, 88, "v1"); t.vline(32, 72, 88, "v3")
    t.vline(40, 69, 90, "c4")                                                   # inseam gap line
    t.rows({86: (30, 38), 87: (30, 38)}, "c3")                                  # cuff gather
    t.rows({86: (42, 50), 87: (42, 50)}, "c3")
    t.rect(45, 76, 49, 81, "c3"); t.hline(45, 49, 76, "c1")                     # cargo pocket

    # shirt: charcoal, high collar with orange inner collar
    s = Ls["shirt"]
    s.shaded(30, 38, 50, 63, "c1", "c2", "c3")
    s.rect(36, 36, 44, 39, "c3"); s.hline(37, 43, 36, "c2")
    s.rect(35, 37, 35, 40, "o2"); s.rect(45, 37, 45, 40, "o3")                  # inner collar
    s.vline(40, 41, 58, "c3")                                                   # placket

    # vest: asymmetric off-white tool vest (long left panel, short right panel)
    v = Ls["vest"]
    v.shaded(29, 39, 38, 63, "v1", "v2", "v3")
    v.shaded(43, 40, 51, 56, "v1", "v2", "v3")
    v.vline(38, 41, 63, "v4"); v.vline(43, 41, 56, "v4")                        # opening edges
    v.rect(31, 46, 35, 50, "v3"); v.hline(31, 35, 46, "v4"); v.px(33, 48, "o2")  # chest pocket
    v.rect(31, 53, 34, 57, "v3"); v.hline(31, 34, 53, "v4")                     # lower pocket
    v.rect(45, 44, 49, 47, "c3"); v.px(47, 45, "o1")                            # small dark tab
    for i in range(10):                                                         # diagonal strap
        v.px(44 + (i * 7) // 10, 47 + i, "c3")
    v.rect(29, 58, 51, 60, "c4"); v.hline(29, 51, 58, "c3")                     # belt
    v.rect(39, 58, 41, 60, "v3"); v.px(40, 59, "c4")                            # buckle
    v.rect(46, 61, 47, 72, "o2"); v.vline(46, 61, 72, "o1"); v.hline(46, 47, 72, "o3")  # hanging strap

    # arms: charcoal sleeves, bright orange rolled cuffs, skin forearms, black fingerless gloves
    a = Ls["arms"]
    for x0, x1, hi, dk in ((23, 28, "c1", "c3"), (52, 57, "c2", "c3")):
        a.rect(x0 + 1, 38, x1, 40, "c2")
        a.shaded(x0, 40, x1, 49, hi, "c2", dk)
        a.rect(x0, 50, x1, 53, "o2"); a.hline(x0, x1, 50, "o1"); a.hline(x0, x1, 53, "o3")
        a.shaded(x0 + 1, 54, x1 - 1, 58, "s1", "s2", "s3", 1, 1)
        a.rect(x0, 59, x1, 64, "k1"); a.hline(x0 + 1, x1 - 1, 59, "c3")
        a.rect(x0 + 1, 65, x1 - 1, 66, "s2"); a.px(x1 - 1, 66, "s3")           # bare fingertips
    a.hline(24, 27, 61, "c3"); a.hline(53, 56, 61, "c3")                        # glove knuckle seam

    # devices: rectangular folding case (viewer-left hip) + round hinged mechanism (viewer-right hip)
    d = Ls["devices"]
    d.shaded(31, 61, 36, 70, "v2", "g1", "c3")
    d.vline(33, 61, 70, "o2"); d.hline(31, 36, 65, "c4"); d.px(35, 62, "o1")
    cx, cy = 47, 65
    for y in range(cy - 4, cy + 5):
        for x in range(cx - 4, cx + 5):
            r2 = (x - cx) ** 2 + (y - cy) ** 2
            if r2 <= 18:
                d.px(x, y, "o2" if 7 <= r2 <= 10 else ("c3" if r2 <= 2 else ("v2" if x + y < cx + cy - 2 else "g1")))
    d.px(cx, cy, "o1")
    d.rect(cx + 4, cy - 1, cx + 5, cy + 1, "c3")                                # hinge knuckle

    # face/head: skin, ears, neck, eyes, brows, nose, mouth
    f = Ls["face"]
    f.rect(37, 34, 43, 37, "s3")                                                # neck
    head = {17: (30, 50), 18: (30, 50), 19: (30, 50), 20: (30, 50), 21: (30, 50), 22: (30, 50), 23: (30, 50),
            24: (30, 50), 25: (30, 50), 26: (30, 50), 27: (30, 50), 28: (31, 49), 29: (31, 49), 30: (32, 48),
            31: (33, 47), 32: (34, 46), 33: (36, 44), 34: (38, 42)}
    f.rows(head, "s2")
    for y, (x0, x1) in head.items():
        f.hline(x0 + 1, min(x0 + 6, x1), y, "s1") if y < 31 else None
        f.px(x1, y, "s3"); f.px(x1 - 1, y, "s3") if y > 27 else None
    f.rect(28, 24, 29, 28, "s2"); f.px(28, 24, "s1"); f.rect(51, 24, 52, 28, "s3")   # ears
    for x0 in (33, 44):                                                         # eyes: lash, white, iris
        f.hline(x0, x0 + 3, 24, "h3")
        f.hline(x0, x0 + 3, 25, "h4")
        f.rect(x0, 26, x0 + 3, 27, "e1")
        f.rect(x0 + 1, 26, x0 + 2, 27, "e2"); f.px(x0 + 1, 26, "h4")
    f.hline(33, 36, 22, "h3"); f.hline(44, 47, 22, "h3"); f.px(32, 23, "h3")   # brows (confident tilt)
    f.px(41, 29, "s3"); f.px(41, 30, "s3"); f.px(40, 31, "s3")                  # nose
    f.hline(39, 41, 33, "m1"); f.px(38, 32, "m1"); f.px(42, 32, "m1"); f.hline(39, 41, 34, "s3")           # smiling mouth

    # hair: spiky dark brown, swept to viewer-left; close-cropped temple on viewer-right
    h = Ls["hair"]
    h.rect(30, 12, 50, 19, "h2")
    h.rows({11: (31, 49), 10: (32, 36), 9: (33, 35), 8: (34, 34)}, "h2")       # spikes
    h.rows({10: (39, 43), 9: (40, 42), 8: (41, 41)}, "h2")
    h.rows({11: (45, 49), 10: (46, 49), 9: (47, 48)}, "h3")
    h.rows({13: (26, 30), 14: (27, 30), 12: (25, 28), 11: (25, 27)}, "h2")     # left sweep tips
    h.rect(28, 15, 30, 25, "h2"); h.vline(28, 15, 25, "h3"); h.px(29, 26, "h3")  # left sideburn mass
    h.rows({19: (30, 39), 20: (30, 37), 21: (30, 35), 22: (30, 33), 23: (30, 31)}, "h2")                    # fringe falling to viewer-left
    h.px(37, 20, "h3"); h.px(38, 20, "h3")
    h.rows({12: (32, 38), 11: (33, 36)}, "h1"); h.px(41, 9, "h1"); h.px(34, 9, "h1")  # highlights
    h.hline(31, 33, 20, "h1")
    h.rect(49, 18, 51, 23, "h3"); h.px(50, 20, "h4"); h.px(49, 22, "h4")        # cropped temple stubble
    h.rect(50, 12, 51, 17, "h3")

    # goggles resting on forehead: strap, orange rims, warm lenses
    g = Ls["goggles"]
    g.hline(28, 52, 16, "g2"); g.hline(28, 52, 17, "g1")
    for x0 in (31, 42):
        g.rect(x0, 13, x0 + 7, 18, "o2"); g.hline(x0, x0 + 7, 13, "o1"); g.hline(x0, x0 + 7, 18, "o3")
        g.rect(x0 + 1, 14, x0 + 6, 17, "l2"); g.rect(x0 + 1, 14, x0 + 3, 15, "l1")
    g.rect(39, 14, 41, 16, "g2")                                                 # bridge

    # auto outline on the outer silhouette, per layer, in that layer's darkest colour
    comp = compose_layers(Ls)
    opaque = comp[..., 3] == 255
    for n, k in OUTLINE.items():
        m = Ls[n].a[..., 3] == 255
        top = compose_layers(Ls, above=n)[..., 3] == 255
        for y, x in zip(*np.nonzero(m & ~top)):
            if any(not (0 <= y + dy < H and 0 <= x + dx < W) or not opaque[y + dy, x + dx]
                   for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                Ls[n].px(x, y, k)

    # guides (hidden): canvas border, pin, body-row ticks
    gd = Ls["guides"].a
    for x in range(W):
        gd[0, x] = gd[H - 1, x] = (*GUIDE_RGB, 255)
    for y in range(H):
        gd[y, 0] = gd[y, W - 1] = (*GUIDE_RGB, 255)
    for y in BODY_ROWS:
        for x in (1, 2, 3, W - 4, W - 3, W - 2):
            gd[y, x] = (*GUIDE_RGB, 255)
    gd[PIN[1], PIN[0]] = (*GUIDE_RGB, 255)
    return {n: Ls[n].a for n in LAYERS}


def compose_layers(Ls, above=None):
    names = [n for n in LAYERS if n != "guides"]
    if above is not None:
        names = names[names.index(above) + 1:]
    comp = np.zeros((H, W, 4), np.uint8)
    for n in names:
        a = Ls[n].a if isinstance(Ls[n], L) else Ls[n]
        m = a[..., 3] == 255
        comp[m] = a[m]
    return comp


# ------------------------------------------------------------------ package
def sha(b):
    return hashlib.sha256(b).hexdigest()


def fix_pxo_metadata(pxo):
    """Helper hardcodes male export/palette names; rewrite them for Jiang, keep entry order and dates."""
    src = zipfile.ZipFile(io.BytesIO(pxo))
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename == "data.json":
                j = json.loads(data)
                j["export_profile"]["file_name"] = json.dumps("jiang-lan-south-idle-static-v01")
                pal = json.loads(j["user_data"])["declared_palette"]
                pal.update(name="jiang-lan-south-v01", comment="declared palette (jiang-lan native south v01)")
                j["user_data"] = json.dumps({"declared_palette": pal, "actor_id": ACTOR, "status": "UNAPPROVED"})
                j["current_layer"] = LAYERS.index("hair")
                data = json.dumps(j, separators=(",", ":")).encode()
            z.writestr(zipfile.ZipInfo(info.filename, ZIP_DT), data, zipfile.ZIP_DEFLATED)
    return out.getvalue()


def artifacts():
    hp = load_helper()
    blobs = draw()
    full = compose_layers(blobs)
    png = hp.png_bytes(full)
    pxo = fix_pxo_metadata(hp.make_pxo(blobs, png))
    ora = hp.make_ora(blobs, png)
    pal = (json.dumps({"actor_id": ACTOR, "name": "jiang-lan-south-v01", "colors": PAL}, indent=2) + "\n").encode()
    return hp, blobs, full, png, pxo, ora, pal


def gates(hp, blobs, full, png, pxo, ora):
    g = {}
    al = full[..., 3]
    g["binary_alpha"] = bool(np.isin(al, (0, 255)).all())
    g["no_opaque_border"] = not (al[0].any() or al[-1].any() or al[:, 0].any() or al[:, -1].any())
    ys, xs = np.nonzero(al)
    g["body_rows"] = [int(ys.min()), int(ys.max())]
    g["body_rows_ok"] = g["body_rows"] == list(BODY_ROWS)
    feet = xs[ys == BODY_ROWS[1]]
    g["pin_inside_feet_span"] = bool(feet.min() <= PIN[0] <= feet.max())
    cols = {tuple(c) for c in full[al == 255][:, :3]}
    declared = {rgb(k) for k in PAL}
    g["colour_count"] = len(cols)
    g["colour_count_24_48"] = 24 <= len(cols) <= 48
    g["all_colours_declared"] = cols <= declared
    g["png_decode_equals_compose"] = bool((hp.decode(png) == full).all())
    layers, hidden, merged, mfirst = hp.read_ora_layers(ora)
    g["ora_hidden"] = hidden
    g["ora_mimetype_first_stored"] = mfirst
    g["ora_recompose_equals_png"] = bool((hp.recompose([(n, a) for n, a, vis in reversed(layers) if vis != "hidden"]) == full).all())
    with zipfile.ZipFile(io.BytesIO(pxo)) as z:
        dj = json.loads(z.read("data.json"))
        g["pxo_layer_names"] = [l["name"] for l in dj["layers"]] == LAYERS
        stack = [np.frombuffer(z.read(f"image_data/frames/1/layer_{i}"), np.uint8).reshape(H, W, 4)
                 for i in range(1, len(LAYERS) + 1)]
        g["pxo_no_male_metadata"] = b"protagonist-male" not in z.read("data.json")
    g["pxo_recompose_equals_png"] = bool((hp.recompose([(LAYERS[i], s) for i, s in enumerate(stack)
                                                        if LAYERS[i] != "guides"]) == full).all())
    nonempty = {n: int((blobs[n][..., 3] == 255).sum()) for n in LAYERS}
    g["layer_texels"] = nonempty
    g["all_role_layers_nonempty"] = all(v > 0 for v in nonempty.values())
    g["guides_hidden_no_overlap"] = not ((blobs["guides"][..., 3] > 0) & (al > 0)).any()
    return g


HARD = ["binary_alpha", "no_opaque_border", "body_rows_ok", "pin_inside_feet_span", "colour_count_24_48",
        "all_colours_declared", "png_decode_equals_compose", "ora_mimetype_first_stored", "ora_recompose_equals_png",
        "pxo_layer_names", "pxo_no_male_metadata", "pxo_recompose_equals_png", "all_role_layers_nonempty",
        "guides_hidden_no_overlap"]


def manifest(png, pxo, ora, pal, g):
    port = os.path.join(REPO, *PORTRAIT_REL.split("/"))
    psha = sha(open(port, "rb").read()) if os.path.exists(port) else None
    m = {"actor_id": ACTOR, "content_id": "content.char.jiang-lan.static-south", "status": "UNAPPROVED",
         "direction": "south", "pose": "idle-static", "canvas": [W, H], "pivot": list(PIN), "body_rows": list(BODY_ROWS),
         "display_scale": DISPLAY_SCALE, "logical_height_px": (BODY_ROWS[1] - BODY_ROWS[0] + 1) * DISPLAY_SCALE,
         "layers": [{"name": n, "visible": n != "guides"} for n in LAYERS],
         "files": {k: {"file": NAMES[k], "rawsha256": sha(b)} for k, b in
                   (("png", png), ("pxo", pxo), ("ora", ora), ("palette", pal))},
         "portrait_ref": {"file": PORTRAIT_REL, "sha256": psha, "expected_sha256": PORTRAIT_SHA,
                          "use": "identity reference only; no pixels sampled"},
         "colour_count": g["colour_count"], "author_tool": "tools/" + os.path.basename(__file__),
         "serialization_helper": HELPER_REL, "pixel_source": "code-authored native pixels, declared palette"}
    return (json.dumps(m, indent=2) + "\n").encode()


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    r1 = artifacts(); r2 = artifacts()
    hp, blobs, full, png, pxo, ora, pal = r1
    det = all(a == b for a, b in zip(r1[3:], r2[3:]))
    g = gates(hp, blobs, full, png, pxo, ora)
    g["deterministic_rebuild"] = det
    bad = [k for k in HARD + ["deterministic_rebuild"] if not g[k]]
    man = manifest(png, pxo, ora, pal, g)
    out = os.path.join(REPO, *OUT_DIR_REL.split("/"))
    files = {"png": png, "pxo": pxo, "ora": ora, "palette": pal, "manifest": man}
    if cmd == "build":
        if bad:
            raise SystemExit(f"hard gates failed: {bad}")
        os.makedirs(out, exist_ok=True)
        for k, data in files.items():
            p = os.path.join(out, NAMES[k])
            if os.path.exists(p) and open(p, "rb").read() != data:
                raise SystemExit(f"refusing to overwrite different file {p}")
            open(p, "wb").write(data)
        open(os.path.join(out, ".gdignore"), "ab").close()
        qa = os.path.join(REPO, *QA_DIR_REL.split("/")); os.makedirs(qa, exist_ok=True)
        from PIL import Image
        Image.fromarray(full, "RGBA").resize((W * 6, H * 6), Image.NEAREST).save(
            os.path.join(qa, name("south-idle-preview-x6", "png", "7d2e9a41")))
    disk = {k: (sha(open(os.path.join(out, NAMES[k]), "rb").read()) == sha(v)) if os.path.exists(os.path.join(out, NAMES[k])) else None
            for k, v in files.items()}
    g["disk_matches_rebuild"] = disk
    g["hard_failures"] = bad
    print(json.dumps(g, indent=1))
    print("JIANG_SOUTH_V01_" + ("ALL_OK" if not bad and all(disk.values()) else "FAIL"))
    return 0 if not bad and all(v is not False for v in disk.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
