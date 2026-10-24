"""Yanke SOUTH idle static, native 80x112 source package (UNAPPROVED v01).

content.char.yanke.static-south. Code-authored native pixels in the Sea of Stars direction (broad coherent
clusters, upper-left light), 48 logical px at display scale 0.5. Identity anchors (Bible character-07, 37-year-old
friendly heavy-tool craftsperson; concept sheet is an UNAPPROVED identity reference, no pixels sampled): short
curly dark-brown hair, thick beard, warm broad face with a cheerful direct smile; broad leather shoulder straps
over a cream rolled-sleeve work shirt and olive-green work apron; brass harness buckles and belt buckle; dark-brown
baggy work trousers with olive knee patches; heavy brown leather boots; red work rag at the character's right hip
(screen left); notched heavy steel tool head on a wooden handle slung over the character's right shoulder (screen
left). Sturdy, wide silhouette. Palette hues were chosen by eye from point samples of the concept; pixels are
authored, not resampled.

Reuses the Lin Que v01 author (L pen, outline/guide finish, extended gates) and through it the Jiang south v01
gates and the male v8pair PNG/PXO/ORA serializers, exactly as the Milo and Muxiu south v01 authors do. Their
palette/layer globals are rebound in memory only; no Lin, Jiang, Milo, Muxiu or male file is written. All reused
tool files are hash-pinned.

  python -X utf8 -I <this> build   # writes new files only (refuses to overwrite different bytes)
  python -X utf8 -I <this> check   # rebuilds twice in memory and compares with files on disk
  python -X utf8 -I <this> preview # preview only, no package writes
"""
import hashlib, importlib.util, io, json, os, sys, zipfile
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG, ACTOR, D = "rpg-2-star-ocean-the-second", "yanke", "south"
STAMP, RUN_ID = "20261024-084428", "b93c1a4e"
OUT_REL = "game/assets/characters/yanke-native-v01/south"
QA_REL = "outputs/yanke-s93/author"
LIN_TOOL_REL = "tools/rpg-2-star-ocean-the-second_lin-que_four-direction-static-author_unapproved-v01_20261022-222500-3d61c74e.py"
PINS = {LIN_TOOL_REL: "0ddbea4591312c767b2ac46da6be29302b908cf311adb92eaf5ed26c300eff82",
        "tools/rpg-2-star-ocean-the-second_jiang-lan_south-static-author_unapproved-v01_20261021-235007-514b9771.py":
            "35005f3c904802251c773838d61068d4aea847c993f6e354676e88a599db69b4",
        "tools/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair-static-pilot-build-and-check_unapproved-v01_20261018-130225-f28bd26d.py":
            "fcd9d6e88e7401097e9c8afe8061df6dcdd9e2132892680522d7d722ac2abb79",
        "tools/rpg-2-star-ocean-the-second_muxiu_south-static-author_unapproved-v01_20261024-071500-6d3e9a51.py":
            "f329ac7aa595f003ba741ed8de6cf5aade1d912acfa65a1720ce731eb24737f1"}   # structural template only
PORTRAIT_REL = "outputs/rpg-2-star-ocean-the-second_yanke_character-sheet_v01_20261013-153818-244380f3.png"
PORTRAIT_SHA = "65ded437ee36afd47f2bbd17cefc72a2ec0afe5914d54bcb6f46f17855b8b23f"
ZIP_DT = (2026, 10, 24, 8, 44, 28)

PAL = {  # declared palette, <=40 entries (male serializer palette grid is 8x5); upper-left light
    "s1": "f6d0a8", "s2": "dfa87e", "s3": "b87a54", "s4": "7a4630",                    # warm skin
    "h1": "7a583e", "h2": "523824", "h3": "332116", "h4": "1c120b",                    # hair / beard
    "e1": "f7f1e3", "e2": "5a3a1e", "m1": "8f4036",                                    # eye white, iris, mouth
    "c1": "f2e8d2", "c2": "dacbac", "c3": "b3a184", "c4": "6e604c",                    # cream work shirt
    "a1": "7f804a", "a2": "5e6034", "a3": "3f4222", "a4": "252713",                    # olive work apron
    "t1": "604834", "t2": "44311f", "t3": "2c1f13", "t4": "19110a",                    # dark-brown trousers
    "r1": "9a6638", "r2": "6e4724", "r3": "4a2c15", "r4": "2a190c",                    # leather straps/boots
    "k1": "969aa1", "k2": "626770", "k3": "393c43", "k4": "1a1c20",                    # steel tool head
    "w1": "b08450", "w2": "7d5a32", "w3": "4f371d",                                    # wooden handle
    "y1": "d0a24e", "y2": "8e6a2c",                                                    # brass buckles
    "f1": "a84838", "f2": "722c22",                                                    # red work rag
}
LAYERS = ["hammer", "boots", "trousers", "shirt", "apron", "harness", "grip", "belt", "arms", "face", "hair",
          "beard", "guides"]
OUTLINE = {"hammer": "k4", "boots": "r4", "trousers": "t4", "apron": "a4", "shirt": "c4", "harness": "r4",
           "grip": "w3", "belt": "r4", "arms": "s4", "face": "s4", "hair": "h4", "beard": "h4"}
FILE_KEYS = {"png": ("static", "png"), "pxo": ("edit", "pxo"), "ora": ("edit", "ora"), "palette": ("palette", "json")}


def fs(rel):
    p = os.path.join(REPO, *rel.split("/"))
    return "\\\\?\\" + p if os.name == "nt" and len(p) > 240 and not p.startswith("\\\\?\\") else p


def sha(b):
    return hashlib.sha256(b).hexdigest()


def uid(*parts):
    return sha(":".join((RUN_ID,) + parts).encode())[:8]


def fname(purpose, ext):
    return f"{SLUG}_{ACTOR}_{D}-{purpose}_unapproved-v01_{STAMP}-{uid(D, purpose, ext)}.{ext}"


def load(rel, modname):
    spec = importlib.util.spec_from_file_location(modname, fs(rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


PIN_OK = {rel: sha(open(fs(rel), "rb").read()) == want for rel, want in PINS.items()}
M = load(LIN_TOOL_REL, "lin_que_v01_for_yanke")                # loads its own Jiang module instance as M.S
S = M.S
for mod in (M, S):                                            # rebind in memory only
    mod.PAL, mod.LAYERS, mod.OUTLINE, mod.ZIP_DT = PAL, LAYERS, OUTLINE, ZIP_DT
M.ACTOR = ACTOR
W, H, PIN, BODY_ROWS, L = S.W, S.H, S.PIN, S.BODY_ROWS, S.L


# ------------------------------------------------------------------ south (front)
def draw_south(Ls):
    # hammer: notched heavy steel head slung over the character's right shoulder (screen left), wooden handle
    hm = Ls["hammer"]
    hm.rect(7, 14, 30, 31, "k2")                                                # head block
    hm.hline(8, 29, 14, "k1"); hm.rect(7, 15, 9, 30, "k1")                      # upper-left light plane
    hm.rect(26, 16, 30, 31, "k3"); hm.hline(10, 30, 30, "k3"); hm.hline(9, 30, 31, "k4")
    hm.vline(27, 16, 30, "k2"); hm.vline(28, 16, 30, "k3")                      # eye band around the handle
    for y in range(21, 25):                                                     # square chip in the striking face
        hm.a[y, 7:11] = 0
    hm.rect(27, 31, 30, 38, "w2"); hm.vline(27, 31, 38, "w1"); hm.vline(30, 31, 38, "w3")
    for i in range(4):                                                          # handle disappears behind shoulder
        y = 35 + i
        x = 30 + i
        hm.rect(x, y, x + 2, y, "w2"); hm.px(x, y, "w1"); hm.px(x + 2, y, "w3")

    # boots: heavy brown leather, folded cuff, brass buckle, broad toe and thick sole
    b = Ls["boots"]
    for x0, x1 in ((25, 38), (42, 55)):
        b.rect(x0, 90, x1, 93, "r2"); b.hline(x0, x1, 90, "r1"); b.hline(x0, x1, 93, "r3")
        b.shaded(x0 + 1, 94, x1 - 1, 99, "r1", "r2", "r3", 2, 2)
        b.hline(x0 + 2, x1 - 2, 96, "r3"); b.hline(x0 + 2, x1 - 2, 97, "r3")    # buckle strap
        b.rect(x0 + 4, 95, x0 + 6, 97, "y2"); b.rect(x0 + 4, 96, x0 + 5, 96, "y1")
        b.shaded(x0 - 1, 100, x1 + 1, 102, "r1", "r2", "r3", 2, 2)
        b.rect(x0 + 2, 100, x0 + 7, 100, "r1")                                   # toe highlight
        b.hline(x0 - 1, x1 + 1, 103, "r4"); b.hline(x0 - 1, x1 + 1, 102, "r3")

    # trousers: dark-brown baggy work trousers, olive knee patches, cuffed hems
    t = Ls["trousers"]
    t.rect(27, 63, 53, 72, "t2")
    t.shaded(27, 63, 53, 72, "t1", "t2", "t3", 2, 2)
    t.shaded(26, 72, 39, 90, "t1", "t2", "t3", 2, 2)
    t.shaded(41, 72, 54, 90, "t1", "t2", "t3", 2, 2)
    t.rect(40, 70, 40, 89, "t4")                                                 # inseam
    for x0, x1 in ((28, 35), (45, 52)):                                          # knee patches
        t.rect(x0, 79, x1, 85, "a2"); t.hline(x0, x1, 79, "a1"); t.hline(x0, x1, 85, "a3")
        t.vline(x0, 80, 81, "a3"); t.vline(x1, 80, 81, "a3")
    t.hline(27, 38, 89, "t3"); t.hline(42, 53, 89, "t3"); t.hline(27, 38, 90, "t4")
    t.hline(42, 53, 90, "t4")

    # apron: olive-green work apron, bib + skirt, stitched pocket, slightly uneven worn hem
    ap = Ls["apron"]
    ap.rows({35: (33, 47), 36: (31, 49), **{y: (30, 50) for y in range(37, 41)},
             **{y: (29, 51) for y in range(41, 50)}, **{y: (28, 52) for y in range(50, 54)},
             **{y: (27, 53) for y in range(54, 61)}, **{y: (26, 54) for y in range(61, 69)},
             **{y: (27, 53) for y in range(69, 72)}, 72: (28, 52)}, "a2")
    for y in range(36, 72):                                                      # light/shadow planes
        half = 11 if y < 54 else (12 if y < 61 else 13)
        if y < 41: half = 10 if y < 37 else 11
        ap.hline(40 - half, 40 - half + 1, y, "a1"); ap.hline(40 + half - 1, 40 + half, y, "a3")
    ap.rect(33, 56, 41, 64, "a3"); ap.hline(33, 41, 56, "a2"); ap.vline(33, 56, 64, "a4")
    ap.rect(43, 44, 49, 49, "a3"); ap.hline(43, 49, 44, "a2")

    # shirt: cream rolled-sleeve work shirt under the apron; broad shoulders and collar
    sh = Ls["shirt"]
    sh.rows({33: (34, 46), 34: (31, 49), 35: (26, 54), **{y: (22, 58) for y in range(36, 46)},
             **{y: (23, 57) for y in range(46, 62)}, **{y: (25, 55) for y in range(62, 65)}}, "c2")
    sh.rect(22, 36, 25, 60, "c1"); sh.rect(55, 36, 58, 60, "c3")
    sh.hline(24, 56, 35, "c3")                                                   # shoulder seam
    sh.rows({33: (36, 44), 34: (35, 45), 35: (34, 46), 36: (33, 47), 37: (33, 47)}, "c1")  # open collar
    sh.vline(34, 37, 44, "c3"); sh.vline(47, 37, 44, "c3")

    # harness: broad leather shoulder straps with brass buckles, over shirt and apron
    hr = Ls["harness"]
    for y in range(32, 67):
        if y < 38:
            lx, rx = 27, 49
        elif y < 65:
            lx, rx = 29, 47
        else:
            lx, rx = 30, 46
        for x0 in (lx, rx):
            hr.rect(x0, y, x0 + 4, y, "r2")
            hr.px(x0, y, "r1"); hr.px(x0 + 4, y, "r3")
    hr.rect(26, 32, 32, 34, "r1"); hr.rect(48, 32, 54, 34, "r2")                 # shoulder pads
    for bx in (29, 47):                                                          # brass buckles
        hr.rect(bx, 42, bx + 4, 46, "y2"); hr.rect(bx + 1, 43, bx + 3, 45, "r3")
        hr.rect(bx + 1, 43, bx + 3, 43, "y1")

    # grip: far end of the hammer handle emerging over the character's left shoulder (screen right)
    gr = Ls["grip"]
    for i in range(9):
        y = 35 + i
        x = 52 + i // 2
        gr.rect(x, y, x + 2, y, "w2"); gr.px(x, y, "w1"); gr.px(x + 2, y, "w3")
    gr.rect(53, 34, 56, 37, "r2"); gr.hline(53, 56, 34, "r1"); gr.hline(53, 56, 37, "r3")

    # belt: broad leather belt with a brass buckle and a red work rag at the character's right hip
    bl = Ls["belt"]
    bl.rect(26, 64, 54, 68, "r2"); bl.hline(26, 54, 64, "r1"); bl.hline(26, 54, 68, "r3")
    bl.rect(36, 63, 44, 69, "y2"); bl.rect(38, 65, 42, 67, "r3"); bl.hline(38, 42, 65, "y1")
    bl.vline(46, 66, 67, "r4"); bl.vline(49, 66, 67, "r4"); bl.vline(52, 66, 67, "r4")
    bl.rows({**{y: (24, 29) for y in range(64, 70)}, **{y: (25, 29) for y in range(70, 74)},
             74: (26, 28)}, "f1")
    bl.rect(29, 64, 29, 73, "f2"); bl.hline(25, 28, 74, "f2")

    # arms: thick arms, cream rolled sleeves, bare forearms, leather bracers, relaxed fists
    a = Ls["arms"]
    for x0, hi in ((14, "c1"), (57, "c2")):
        a.rows({36: (x0 + 2, x0 + 8), 37: (x0, x0 + 9), **{y: (x0, x0 + 9) for y in range(38, 49)}}, "c2")
        a.rect(x0, 38, x0 + 1, 48, hi); a.rect(x0 + 8, 38, x0 + 9, 48, "c3")
        a.rect(x0, 49, x0 + 9, 51, "c3"); a.hline(x0, x0 + 9, 49, "c2"); a.hline(x0, x0 + 9, 51, "c4")
        a.shaded(x0 + 1, 52, x0 + 8, 64, "s1", "s2", "s3", 2, 2)
        a.rect(x0 + 1, 65, x0 + 8, 69, "r2"); a.hline(x0 + 1, x0 + 8, 65, "r1")
        a.hline(x0 + 1, x0 + 8, 67, "r4"); a.hline(x0 + 1, x0 + 8, 69, "r3")
        a.shaded(x0 + 1, 70, x0 + 8, 76, "s2", "s2", "s3", 1, 2)
        a.hline(x0 + 2, x0 + 7, 72, "s3")                                        # knuckle line
        a.px(x0 + 9, 71, "s2"); a.px(x0 + 9, 72, "s3")

    # face: broad warm face, thick brows, brown eyes, nose, cheerful open smile; ears
    f = Ls["face"]
    f.rows({17: (32, 48), **{y: (30, 50) for y in range(18, 21)},
            **{y: (29, 51) for y in range(21, 28)}, **{y: (30, 50) for y in range(28, 33)},
            **{y: (31, 49) for y in range(33, 36)}, 36: (33, 47), 37: (35, 45),
            **{y: (37, 43) for y in range(38, 45)}}, "s2")
    f.rect(30, 19, 32, 33, "s1"); f.rect(49, 19, 51, 34, "s3")
    f.rect(27, 25, 29, 31, "s2"); f.vline(28, 27, 28, "s3")                      # ears
    f.rect(51, 25, 53, 31, "s3"); f.vline(52, 27, 28, "s2")
    f.hline(32, 37, 22, "h2"); f.hline(32, 37, 23, "h3")                         # thick brows
    f.hline(43, 48, 22, "h2"); f.hline(43, 48, 23, "h3")
    for ex in (32, 44):                                                          # eyes
        f.hline(ex, ex + 4, 25, "h4")
        f.rect(ex, 26, ex + 4, 27, "e1"); f.rect(ex + 1, 26, ex + 3, 27, "e2")
        f.px(ex + 2, 26, "h4")
    f.rect(40, 27, 41, 30, "s3"); f.hline(39, 42, 30, "s3")                      # nose
    f.hline(38, 42, 34, "m1"); f.hline(39, 41, 34, "e1")                         # open smile + teeth
    f.hline(38, 42, 35, "m1"); f.px(37, 33, "m1"); f.px(43, 33, "m1")            # smile corners
    f.rect(33, 28, 34, 30, "s1"); f.rect(46, 31, 47, 31, "s3")                   # cheek plane, jaw shade
    f.rect(37, 40, 43, 44, "s3"); f.rect(38, 40, 42, 43, "s2")                   # neck

    # hair: short dark-brown curls, upper-left sheen, side locks framing the face
    h = Ls["hair"]
    h.rows({8: (31, 36), 9: (29, 39), 10: (27, 53), **{y: (25, 55) for y in range(11, 14)},
            **{y: (24, 56) for y in range(14, 17)}}, "h2")
    h.rows({8: (43, 48), 9: (42, 51), 10: (45, 53), 11: (48, 55), 12: (49, 56)}, "h3")
    h.rows({17: (24, 35), 18: (24, 33), 19: (24, 31), 20: (24, 29), 21: (24, 28)}, "h2")   # fringe left
    h.rows({17: (42, 56), 18: (44, 56), 19: (46, 56), 20: (48, 56), 21: (50, 56)}, "h2")   # fringe right
    h.rows({22: (24, 27), 23: (24, 27), **{y: (24, 27) for y in range(24, 30)}}, "h2")
    h.rows({22: (53, 56), 23: (53, 56), **{y: (53, 56) for y in range(24, 30)}}, "h3")
    h.rows({8: (32, 34), 9: (30, 34), 10: (29, 36), 11: (27, 34), 12: (26, 32), 13: (26, 31)}, "h1")
    h.rows({14: (26, 30), 15: (27, 29)}, "h1")
    h.rows({9: (37, 38), 12: (35, 38), 15: (32, 35)}, "h1")                      # curl highlights
    h.rect(54, 13, 56, 19, "h3"); h.rect(52, 15, 53, 15, "h3")

    # beard: full short beard and moustache, leaving the mouth and smile visible
    bd = Ls["beard"]
    bd.rows({28: (28, 31), 29: (27, 33), 30: (27, 35), 31: (27, 36), 32: (28, 52), 33: (28, 52),
             **{y: (28, 34) for y in range(34, 36)}, **{y: (46, 53) for y in range(34, 36)},
             36: (29, 51), 37: (30, 50), 38: (32, 48), 39: (34, 46), 40: (35, 45), 41: (36, 44),
             42: (37, 43)}, "h2")
    bd.rows({29: (28, 31), 30: (28, 32), 31: (28, 33), 32: (29, 33), 36: (30, 34), 37: (31, 34)}, "h1")
    bd.rows({32: (34, 46), 33: (34, 46)}, "h3")                                  # moustache
    bd.hline(35, 46, 32, "h1")
    bd.rows({38: (45, 48), 39: (42, 46), 40: (41, 45), 41: (42, 44)}, "h3")      # right/bottom shadow
    bd.rows({34: (28, 33), 35: (28, 33)}, "h3")


def draw():
    Ls = {n: L() for n in LAYERS}
    draw_south(Ls)
    return M.finish(Ls)


# ------------------------------------------------------------------ package
def fix_pxo_metadata(pxo):
    """Male helper hardcodes its export/palette names; rewrite for Yanke south, keep entry order and dates."""
    src = zipfile.ZipFile(io.BytesIO(pxo))
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename == "data.json":
                j = json.loads(data)
                j["export_profile"]["file_name"] = json.dumps(f"{ACTOR}-{D}-idle-static-v01")
                pal = json.loads(j["user_data"])["declared_palette"]
                pal.update(name=f"{ACTOR}-{D}-v01", comment=f"declared palette ({ACTOR} native {D} v01)")
                j["user_data"] = json.dumps({"declared_palette": pal, "actor_id": ACTOR, "direction": D,
                                             "status": "UNAPPROVED"})
                j["current_layer"] = LAYERS.index("hair")
                data = json.dumps(j, separators=(",", ":")).encode()
            z.writestr(zipfile.ZipInfo(info.filename, ZIP_DT), data, zipfile.ZIP_DEFLATED)
    return out.getvalue()


def artifacts():
    hp = S.load_helper()
    hp.ZIP_DT, hp.LAYERS, hp.PAL = ZIP_DT, LAYERS, PAL
    blobs = draw()
    full = S.compose_layers(blobs)
    png = hp.png_bytes(full)
    pxo = fix_pxo_metadata(hp.make_pxo(blobs, png))
    ora = hp.make_ora(blobs, png)
    pal = (json.dumps({"actor_id": ACTOR, "name": f"{ACTOR}-{D}-v01", "colors": PAL}, indent=2) + "\n").encode()
    return hp, blobs, full, png, pxo, ora, pal


def isolated(full):
    """Opaque texels whose 4-neighbours are all a different colour (noise metric for broad clusters)."""
    rgb = full[..., :3].astype(int); op = full[..., 3] == 255; n = 0
    for y, x in zip(*np.nonzero(op)):
        same = 0
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and op[yy, xx] and (rgb[yy, xx] == rgb[y, x]).all():
                same += 1
        n += same == 0
    return int(n)


def gates(r):
    hp, blobs, full, png, pxo, ora, pal = r
    g = M.gates(D, r)
    with zipfile.ZipFile(io.BytesIO(pxo)) as z:
        dj = z.read("data.json")
    g["pxo_no_foreign_metadata"] = all(s not in dj for s in (b"lin-que", b"milo", b"jiang", b"muxiu"))
    g["palette_fits_pxo_grid_40"] = len(PAL) <= 40
    al = full[..., 3]
    g["isolated_texels"] = isolated(full)
    g["isolated_texels_le_24"] = g["isolated_texels"] <= 24
    cols = lambda keys: {S.rgb(k) for k in keys}
    used = {tuple(c) for c in full[al == 255][:, :3]}
    g["identity_colours_visible"] = {"leather": bool(used & cols(("r1", "r2"))),
                                     "dark_brown_trousers": bool(used & cols(("t1", "t2"))),
                                     "steel_tool": bool(used & cols(("k1", "k2"))),
                                     "olive_apron": bool(used & cols(("a1", "a2"))),
                                     "cream_shirt": bool(used & cols(("c1", "c2"))),
                                     "red_rag": bool(used & cols(("f1", "f2")))}
    g["identity_colours_all"] = all(g["identity_colours_visible"].values())
    vis = g["visible_role_texels"]
    g["anchor_layers_visible"] = all(vis[n] >= 12 for n in ("hammer", "grip", "harness", "trousers", "apron",
                                                           "hair", "beard", "face"))
    ys, xs = np.nonzero(al)
    g["silhouette_width"] = int(xs.max() - xs.min() + 1)
    # stocky: torso/shoulder span is at least 34 source px at chest rows
    chest = al[38:46].any(axis=0)
    g["stocky_shoulders_ge_34"] = int(np.count_nonzero(chest)) >= 34
    return g


HARD = M.HARD + ["pxo_no_foreign_metadata", "palette_fits_pxo_grid_40", "isolated_texels_le_24",
                 "identity_colours_all", "anchor_layers_visible", "face_has_eye", "stocky_shoulders_ge_34"]


def manifest(files, g):
    m = {"actor_id": ACTOR, "content_id": f"content.char.{ACTOR}.static-{D}", "status": "UNAPPROVED",
         "direction": D, "pose": "idle-static", "canvas": [W, H], "pivot": list(PIN), "body_rows": list(BODY_ROWS),
         "display_scale": S.DISPLAY_SCALE, "logical_height_px": (BODY_ROWS[1] - BODY_ROWS[0] + 1) * S.DISPLAY_SCALE,
         "layers": [{"name": n, "visible": n != "guides"} for n in LAYERS],
         "face_layer_role": "broad front face, two brown eyes, thick brows, nose, cheerful open smile, ears, neck",
         "beard_layer_role": "thick short beard, moustache and sideburns; mouth kept clear for the smile",
         "view_notes": "front: short curly dark-brown hair with upper-left sheen; thick beard and moustache; cream "
                       "rolled-sleeve work shirt; olive-green work apron with stitched pocket and worn hem; broad "
                       "leather shoulder straps with brass buckles over shirt and apron; broad leather belt with "
                       "brass buckle and red work rag at the character's right hip (screen left); dark-brown baggy "
                       "work trousers with olive knee patches; heavy brown leather boots with cuffs and brass "
                       "buckles; notched heavy steel tool head on a wooden handle slung over the character's right "
                       "shoulder (screen left), with the far end of the handle emerging over the character's left "
                       "shoulder (screen right). Sturdy, wide silhouette.",
         "authored_deviations_from_sheet": [
             "pose: neutral front idle with both arms relaxed; the sheet's 3/4 pose carries the hammer across both "
             "shoulders.",
             "hammer: the head is slung over the right shoulder with the far end of the wooden handle emerging "
             "over the left shoulder, so the notch and steel mass read at 48 px; the full across-shoulder pose is "
             "not copied.",
             "small belt tools, pouch and cloth tatters beyond the one red rag are omitted for 48 px readability."],
         "files": {k: {"file": fname(*FILE_KEYS[k]), "rawsha256": sha(b)} for k, b in files.items()},
         "colour_count": g["colour_count"], "genuine_visible_role_layers": g["genuine_visible_role_layers"],
         "isolated_texels": g["isolated_texels"],
         "portrait_ref": {"file": PORTRAIT_REL, "expected_sha256": PORTRAIT_SHA, "approval": "UNAPPROVED",
                          "use": "concept identity reference only; hues chosen by eye, no pixels copied"},
         "bible_ref": "character-07: 37yo friendly heavy-tool craftsperson; broad leather shoulder straps, "
                      "dark-brown work trousers, notched heavy tool head, sturdy build, cheerful direct; "
                      "identity/hair anchor short curls and thick beard",
         "style_contract": "docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md",
         "source_contract": "reuses the Jiang/Lin/Milo/Muxiu native static contract: 80x112, pivot (40,104), body "
                            "rows 8..103, display scale 0.5 = 48 logical px, binary alpha, transparent border, "
                            "declared palette 24..48 used colours, >=8 genuine role layers, hidden guides layer",
         "replaces_placeholder": "does not modify the old 32x48 native-animation placeholder; it is not counted",
         "author_tool": "tools/" + os.path.basename(__file__), "reused_tool_pins": PINS,
         "serialization_helper": S.HELPER_REL,
         "pixel_source": "code-authored native pixels, declared palette",
         "limitations": "south static only; no runtime wiring, no other directions, no motion, no creator art approval"}
    return (json.dumps(m, indent=2) + "\n").encode()


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    r1, r2 = artifacts(), artifacts()
    g = gates(r1)
    g["deterministic_rebuild"] = all(a == b for a, b in zip(r1[3:], r2[3:]))
    bad = [k for k in HARD + ["deterministic_rebuild"] if not g[k]]
    bad += [f"tool_pin:{rel}" for rel, ok in PIN_OK.items() if not ok]
    files = dict(zip(("png", "pxo", "ora", "palette"), r1[3:]))
    named = {f"{OUT_REL}/{fname(*FILE_KEYS[k])}": b for k, b in files.items()}
    named[f"{OUT_REL}/{fname('manifest', 'json')}"] = manifest(files, g)
    from PIL import Image
    if cmd in ("build", "preview"):
        os.makedirs(fs(QA_REL), exist_ok=True)
        prev = f"{QA_REL}/{SLUG}_{ACTOR}_{D}-preview-x6_unapproved-v01_{STAMP}-{sha(r1[3])[:8]}.png"
        Image.fromarray(r1[2], "RGBA").resize((W * 6, H * 6), Image.NEAREST).save(fs(prev))
        print("preview:", prev)
    if cmd == "build":
        if bad:
            raise SystemExit(f"hard gates failed: {bad}")
        for rel, data in named.items():
            p = fs(rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            if os.path.exists(p) and open(p, "rb").read() != data:
                raise SystemExit(f"refusing to overwrite different file {rel}")
            open(p, "wb").write(data)
        open(fs(OUT_REL + "/.gdignore"), "ab").close()
        listing = {"outputs": {rel: sha(b) for rel, b in sorted(named.items())},
                   "qa_preview_nonsource": {prev: sha(open(fs(prev), "rb").read())}, "hash": "sha256 of raw bytes"}
        lp = f"{QA_REL}/{SLUG}_{ACTOR}_{D}-output-paths-rawhashes_unapproved-v01_{STAMP}-{uid('paths')}.json"
        open(fs(lp), "wb").write((json.dumps(listing, indent=2) + "\n").encode())
    disk = {rel: (sha(open(fs(rel), "rb").read()) == sha(b)) if os.path.exists(fs(rel)) else None
            for rel, b in named.items()}
    report = {k: g[k] for k in ("body_rows", "colour_count", "genuine_visible_role_layers", "visible_role_texels",
                                "isolated_texels", "silhouette_width", "identity_colours_visible",
                                "stocky_shoulders_ge_34", "binary_alpha", "no_opaque_border", "pin_inside_feet_span",
                                "all_colours_declared", "ora_hidden", "deterministic_rebuild")}
    report.update(tool_pins_ok=PIN_OK, disk_matches_rebuild=disk, hard_failures=bad)
    print(json.dumps(report, indent=1))
    ok = not bad and all(v is True for v in disk.values())
    print("YANKE_SOUTH_V01_" + ("ALL_OK" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
