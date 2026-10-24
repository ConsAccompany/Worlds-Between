"""Yanke NORTH idle static, native 80x112 source package (UNAPPROVED v01).

content.char.yanke.static-north. Code-authored native pixels in the Sea of Stars direction (broad clusters,
upper-left light), 48 logical px at display scale 0.5. North is a true BACK view: the camera sees the back of the
head and hair, ears, nape, back of the shirt/harness, trousers seat, boot heels and the tool carried across the
back. It paints no front face (no eyes, nose or mouth) and is not a horizontal mirror of south or west.

Identity anchors (Bible character-07, 37-year-old friendly heavy-tool craftsperson; concept sheet is an
UNAPPROVED identity reference, no pixels sampled): short curly dark-brown hair, thick beard; cream work shirt;
olive-green work apron with ties; broad leather shoulder straps and brass buckles; dark-brown baggy work trousers;
heavy brown leather boots; red work rag at the character's right hip (screen right from behind); notched heavy steel
tool head on a wooden handle slung over the character's right shoulder, the handle running diagonally across the
back to the left hip. In a back view the character's right side is screen right.

Reuses the hash-pinned Yanke south v01 author in memory (and through it Lin Que v01 finish/gates, Jiang v01 gates
and the male v8pair PNG/PXO/ORA serializers) with the same palette, layers and outline colours. Only the direction
label is rebound in memory; the south and west packages and all reused tools stay byte-identical.

  python -X utf8 -I <this> preview # content-named preview only (outputs/yanke-n101/north/author)
  python -X utf8 -I <this> build   # writes the package into the fresh stage dir only
  python -X utf8 -I <this> install # writes new package bytes into the game tree (refuses different bytes)
  python -X utf8 -I <this> check   # rebuilds twice in memory and compares with files in the game tree
"""
import hashlib, importlib.util, io, json, os, sys, zipfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG, ACTOR, D = "rpg-2-star-ocean-the-second", "yanke", "north"
STAMP, RUN_ID = "20261024-092500", "n101north"
OUT_REL = "game/assets/characters/yanke-native-v01/north"
STAGE_REL = "outputs/yanke-n101/north/stage"
QA_REL = "outputs/yanke-n101/north/author"
SOUTH_TOOL_REL = "tools/rpg-2-star-ocean-the-second_yanke_south-static-author_unapproved-v01_20261024-084428-b93c1a4e.py"
SOUTH_DIR_REL = "game/assets/characters/yanke-native-v01/south"
SOUTH_MANIFEST_REL = SOUTH_DIR_REL + "/rpg-2-star-ocean-the-second_yanke_south-manifest_unapproved-v01_20261024-084428-4305a59b.json"
SOUTH_PNG_REL = SOUTH_DIR_REL + "/rpg-2-star-ocean-the-second_yanke_south-static_unapproved-v01_20261024-084428-73949161.png"
WEST_DIR_REL = "game/assets/characters/yanke-native-v01/west"
WEST_MANIFEST_REL = WEST_DIR_REL + "/rpg-2-star-ocean-the-second_yanke_west-manifest_unapproved-v01_20261024-090843-e4019ea8.json"
WEST_PNG_REL = WEST_DIR_REL + "/rpg-2-star-ocean-the-second_yanke_west-static_unapproved-v01_20261024-090843-c7b9c800.png"
PINS = {SOUTH_TOOL_REL: "cdc21721e7423a4df6696273be4271f0a564edfe7d91cd2b2beb13955459fd1c",
        SOUTH_MANIFEST_REL: "e57f5c93131daffff56bc75a47d9a2c1357f4c337797ea0d07c0c73918692e7e",
        SOUTH_PNG_REL: "4f6bcf937390e300e2829ac052bcb1047fdb6387de41561490c757246a32fef0",
        WEST_MANIFEST_REL: "2741ec94a1779077f6771b2bafcbe59f07bc9a8e449b62659683118aa1191df6",
        WEST_PNG_REL: "7fce1fe9dec54ebcc60143adf75c4fd2cc3c50f37668d110df5ea4ce5dceabd3"}
START_NOTE = "task-map 2 points (frozen); canonical meters coordinator-owned, not read or changed"


def fs(rel):
    p = os.path.join(REPO, *rel.split("/"))
    return "\\\\?\\" + p if os.name == "nt" and len(p) > 240 and not p.startswith("\\\\?\\") else p


def sha(b):
    return hashlib.sha256(b).hexdigest()


def uid(*parts):
    return sha(":".join((RUN_ID,) + parts).encode())[:8]


def fname(purpose, ext):
    return f"{SLUG}_{ACTOR}_{D}-{purpose}_unapproved-v01_{STAMP}-{uid(D, purpose, ext)}.{ext}"


PIN_OK = {rel: sha(open(fs(rel), "rb").read()) == want for rel, want in PINS.items()}
_spec = importlib.util.spec_from_file_location("yanke_south_v01_for_north", fs(SOUTH_TOOL_REL))
MS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MS)                                   # pins Lin/Jiang/male tools itself (MS.PIN_OK)
MS.D = D                                                      # rebind the direction label in memory only
M, S = MS.M, MS.S
PAL, LAYERS, FILE_KEYS = MS.PAL, MS.LAYERS, MS.FILE_KEYS
W, H, PIN, BODY_ROWS, L = MS.W, MS.H, MS.PIN, MS.BODY_ROWS, MS.L


# ------------------------------------------------------------------ north (back view)
def draw_north(Ls):
    """Back view. Screen-left light on every form; no face pixels. Character right is screen right."""
    # ------------------------------------------------------------------ tool: steel head above the RIGHT shoulder
    hm = Ls["hammer"]
    hm.rect(57, 11, 71, 29, "k2")                                      # head block above/behind right shoulder
    hm.rect(57, 11, 59, 29, "k1")                                      # lit left plane
    hm.rect(57, 11, 71, 11, "k1")                                      # top light
    hm.rect(57, 29, 71, 29, "k3")                                      # lower shadow
    hm.rect(69, 12, 71, 28, "k3")                                      # back/right shadow plane
    for y in range(18, 23):                                            # square notch in the striking face
        hm.a[y, 67:72] = 0
    hm.rect(61, 15, 68, 16, "k1")                                      # worn steel face bands
    hm.rect(61, 24, 68, 25, "k1")
    hm.rect(60, 12, 62, 13, "k1")

    # ------------------------------------------------------------------ boots: heels, cuffs, soles
    b = Ls["boots"]
    for x0 in (26, 42):
        b.rect(x0, 90, x0 + 12, 92, "r2")
        b.hline(x0, x0 + 12, 90, "r1"); b.hline(x0, x0 + 12, 92, "r3")
        b.shaded(x0, 93, x0 + 12, 101, "r1", "r2", "r3", 2, 2)
        b.rect(x0 + 3, 95, x0 + 8, 100, "r3")                          # heel counter
        b.rect(x0 + 4, 96, x0 + 7, 97, "r3")
        bx = x0 + 1 if x0 == 26 else x0 + 9                            # brass buckle on the outer ankle
        b.rect(bx, 96, bx + 3, 98, "y2"); b.rect(bx + 1, 97, bx + 2, 97, "y1")
        b.hline(x0 - 1, x0 + 13, 102, "r3")
    b.hline(25, 55, 103, "r4")                                        # thick joined sole row
    b.px(40, 102, "r3")

    # ------------------------------------------------------------------ trousers: seat, back pockets, legs
    t = Ls["trousers"]
    t.rect(26, 63, 54, 73, "t2")
    t.shaded(26, 66, 54, 73, "t1", "t2", "t3", 2, 2)
    t.vline(40, 66, 73, "t4")                                          # centre seat seam
    t.shaded(26, 73, 38, 90, "t1", "t2", "t3", 2, 2)
    t.shaded(42, 73, 54, 90, "t1", "t2", "t3", 2, 2)
    t.vline(39, 73, 89, "t4"); t.vline(41, 73, 89, "t4")               # inseams
    for x0 in (28, 46):                                                # two back patch pockets
        t.rect(x0, 76, x0 + 7, 83, "t3")
        t.rect(x0 + 1, 77, x0 + 6, 82, "t2")
        t.hline(x0 + 1, x0 + 6, 77, "t1")
    t.rect(25, 80, 27, 85, "a2"); t.rect(25, 80, 25, 85, "a1"); t.rect(27, 80, 27, 85, "a3")
    t.rect(53, 80, 55, 85, "a2"); t.rect(53, 80, 53, 85, "a3"); t.rect(55, 80, 55, 85, "a2")
    t.hline(26, 38, 89, "t3"); t.hline(42, 54, 89, "t3")
    t.hline(26, 38, 90, "t4"); t.hline(42, 54, 90, "t4")

    # ------------------------------------------------------------------ shirt: broad back, collar, seams
    sh = Ls["shirt"]
    sh.rows({33: (33, 47), 34: (30, 50), 35: (26, 54), 36: (22, 58), 37: (20, 60)}, "c2")
    sh.rows({**{y: (20, 60) for y in range(38, 46)},
             **{y: (22, 58) for y in range(46, 62)},
             62: (24, 56), 63: (25, 55), 64: (25, 55), 65: (26, 54)}, "c2")
    sh.rect(20, 37, 23, 61, "c1"); sh.rect(57, 37, 60, 61, "c3")
    sh.hline(22, 58, 36, "c3")                                         # shoulder seam
    sh.rect(36, 33, 44, 35, "c1"); sh.hline(35, 45, 35, "c3")          # back collar
    sh.vline(40, 46, 62, "c3")                                         # centre back seam
    sh.rect(35, 38, 36, 45, "c3"); sh.rect(44, 38, 45, 45, "c3")       # shoulder-blade shading

    # ------------------------------------------------------------------ apron: side skirts, tied bow
    ap = Ls["apron"]
    ap.shaded(21, 55, 27, 73, "a1", "a2", "a3", 1, 2)
    ap.shaded(53, 55, 59, 73, "a1", "a2", "a3", 1, 2)
    ap.hline(21, 27, 55, "a1"); ap.hline(53, 59, 55, "a1")
    ap.rect(33, 67, 38, 71, "a2"); ap.rect(42, 67, 47, 71, "a2")       # bow loops (top under belt)
    ap.rect(38, 68, 42, 74, "a1"); ap.rect(40, 68, 42, 74, "a2")       # knot
    ap.rect(35, 72, 38, 77, "a2"); ap.rect(43, 72, 46, 77, "a2")       # tails
    ap.hline(35, 38, 77, "a3"); ap.hline(43, 46, 77, "a3")
    ap.hline(39, 41, 69, "a3")

    # ------------------------------------------------------------------ harness: back straps, ring, buckles
    hr = Ls["harness"]
    for y in range(34, 67):
        if y < 38:
            lx, rx = 27, 47
        elif y < 65:
            lx, rx = 29, 45
        else:
            lx, rx = 30, 44
        for x0 in (lx, rx):
            hr.rect(x0, y, x0 + 5, y, "r2")
            hr.px(x0, y, "r1"); hr.px(x0 + 5, y, "r3")
    hr.rect(26, 34, 33, 37, "r1"); hr.rect(47, 34, 54, 37, "r2")       # shoulder pads
    hr.hline(29, 51, 40, "r2"); hr.hline(29, 51, 41, "r2")
    hr.hline(29, 51, 39, "r1"); hr.hline(29, 51, 42, "r3")             # horizontal back strap
    hr.rect(37, 38, 43, 42, "y2"); hr.rect(38, 39, 42, 41, "r3"); hr.hline(38, 39, 39, "y1")  # central ring
    for bx in (30, 46):                                                # brass strap buckles
        hr.rect(bx, 46, bx + 4, 50, "y2"); hr.rect(bx + 1, 47, bx + 3, 49, "r3")
        hr.hline(bx + 1, bx + 3, 47, "y1")

    # ------------------------------------------------------------------ grip: diagonal handle across the back
    gr = Ls["grip"]
    for y in range(30, 83):                                            # solid 3-px staircase band
        x = 62 - round((y - 30) * 40 / 52)
        gr.rect(x, y, x + 4, y, "w2")
    for y in (34, 42, 50, 58, 66):                                     # 2x2 lit clusters, upper-left edge
        x = 62 - round((y - 30) * 40 / 52)
        gr.rect(x, y, x, y + 1, "w1")
    for y in (38, 46, 54, 62, 70):                                     # 2x2 shadow clusters, lower-right edge
        x = 62 - round((y - 30) * 40 / 52)
        gr.rect(x + 4, y, x + 4, y + 1, "w3")
    for y in range(69, 73):                                            # leather grip wrap
        x = 62 - round((y - 30) * 40 / 52)
        gr.rect(x, y, x + 4, y, "r2")
    gr.rect(32, 69, 33, 70, "r1")
    for y in range(78, 83):                                            # brass ferrule at the butt
        x = 62 - round((y - 30) * 40 / 52)
        gr.rect(x, y, x + 4, y, "y2")
    gr.rect(26, 79, 27, 80, "y1")

    # ------------------------------------------------------------------ belt: loops, side fitting, red rag
    bl = Ls["belt"]
    bl.rect(25, 63, 55, 68, "r2"); bl.hline(25, 55, 63, "r1"); bl.hline(25, 55, 68, "r3")
    for x in (32, 40, 48):
        bl.rect(x, 63, x + 1, 68, "r4")
    bl.rect(51, 64, 55, 67, "y2"); bl.rect(52, 65, 54, 66, "r3"); bl.rect(52, 65, 53, 65, "y1")
    bl.rows({**{y: (56, 61) for y in range(64, 69)}, **{y: (55, 60) for y in range(69, 72)},
             72: (56, 59), 73: (56, 59), 74: (57, 58)}, "f1")
    bl.vline(60, 64, 70, "f2"); bl.hline(56, 59, 72, "f2"); bl.hline(56, 59, 73, "f2")

    # ------------------------------------------------------------------ arms: sleeves, bracers, fists
    a = Ls["arms"]
    for x0, hi in ((14, "c1"), (60, "c2")):
        a.rows({36: (x0 + 2, x0 + 7), 37: (x0, x0 + 8),
                **{y: (x0, x0 + 8) for y in range(38, 49)}}, "c2")
        a.rect(x0, 38, x0 + 1, 48, hi); a.rect(x0 + 7, 38, x0 + 8, 48, "c3")
        a.rect(x0, 49, x0 + 8, 51, "c3"); a.hline(x0, x0 + 8, 49, "c2"); a.hline(x0, x0 + 8, 51, "c4")
        a.shaded(x0 + 1, 52, x0 + 7, 64, "s1", "s2", "s3", 1, 2)
        a.rect(x0 + 1, 65, x0 + 7, 69, "r2"); a.hline(x0 + 1, x0 + 7, 65, "r1")
        a.hline(x0 + 1, x0 + 7, 67, "r4"); a.hline(x0 + 1, x0 + 7, 69, "r3")
        a.shaded(x0 + 1, 70, x0 + 7, 77, "s2", "s2", "s3", 1, 2)
        a.hline(x0 + 2, x0 + 6, 72, "s3")

    # ------------------------------------------------------------------ face: ears + nape only, no front face
    fc = Ls["face"]
    fc.rect(20, 21, 23, 27, "s2"); fc.vline(20, 21, 27, "s1")
    fc.px(23, 24, "s3"); fc.px(23, 25, "s3")
    fc.rect(56, 21, 59, 27, "s3"); fc.vline(59, 21, 27, "s4"); fc.rect(56, 24, 57, 25, "s2")
    fc.rect(35, 30, 45, 37, "s3"); fc.rect(36, 31, 44, 36, "s2"); fc.rect(36, 31, 38, 35, "s1")

    # ------------------------------------------------------------------ hair: full back-of-head curl mass
    h = Ls["hair"]
    h.rows({8: (35, 44), 9: (32, 47), 10: (30, 49), 11: (28, 51), 12: (27, 52), 13: (27, 52),
            14: (25, 54), 15: (25, 54), 16: (25, 54), **{y: (24, 55) for y in range(17, 28)},
            28: (25, 54), 29: (27, 52), 30: (29, 50), 31: (31, 48), 32: (33, 46)}, "h2")
    h.rows({9: (32, 36), 10: (30, 36), 11: (28, 34), 12: (27, 33), 13: (27, 33),
            14: (25, 31), 15: (25, 30)}, "h1")                          # upper-left sheen
    h.rect(24, 17, 25, 27, "h1")                                        # lit left edge
    h.rect(53, 13, 55, 30, "h3"); h.rect(51, 10, 54, 12, "h3")          # right shadow plane
    for x0, y0 in ((29, 20), (37, 17), (45, 23)):
        h.rect(x0, y0, x0 + 2, y0 + 2, "h1")                            # curl lumps
    for x0, y0 in ((34, 24), (42, 19), (30, 27)):
        h.rect(x0, y0, x0 + 2, y0 + 2, "h3")
    h.rect(48, 8, 50, 9, "h1")

    # ------------------------------------------------------------------ beard: jaw-edge tufts only
    bd = Ls["beard"]
    bd.rows({27: (20, 25), 28: (20, 25), 29: (20, 26), 30: (20, 26), 31: (21, 26),
             32: (21, 25), 33: (22, 25), 34: (22, 24)}, "h2")
    bd.rows({27: (20, 22), 28: (20, 22), 29: (20, 22), 30: (21, 23)}, "h1")
    bd.rows({31: (24, 26), 32: (23, 25), 33: (23, 25), 34: (23, 24)}, "h3")
    bd.rows({28: (54, 59), 29: (54, 59), 30: (54, 59), 31: (54, 58),
             32: (55, 58), 33: (55, 58), 34: (56, 57)}, "h2")
    bd.rows({28: (57, 59), 29: (57, 59), 30: (57, 59), 31: (56, 58)}, "h3")
    bd.rows({31: (54, 55), 32: (54, 55), 33: (54, 55)}, "h1")


def despeckle(blobs, rounds=3):
    """Deterministic broad-cluster cleanup: absorb any opaque texel with no same-colour 4-neighbour into the most
    common visible neighbour colour. Alpha, layer ownership, silhouette and all role counts are unchanged."""
    import numpy as np
    names = [n for n in LAYERS if n != "guides"]
    for _ in range(rounds):
        full = S.compose_layers(blobs)
        rgb = full[..., :3].astype(int); op = full[..., 3] == 255
        owner = np.full((H, W), -1, int)
        for i, n in enumerate(names):
            owner[blobs[n][..., 3] == 255] = i
        changed = 0
        for y, x in zip(*np.nonzero(op)):
            same = 0
            counts = {}
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and op[yy, xx]:
                    c = tuple(int(v) for v in rgb[yy, xx])
                    counts[c] = counts.get(c, 0) + 1
                    if c == tuple(int(v) for v in rgb[y, x]):
                        same += 1
            if same or not counts:
                continue
            new = max(counts.items(), key=lambda kv: (kv[1], kv[0]))[0]
            i = owner[y, x]
            if i >= 0:
                blobs[names[i]][y, x, :3] = new
                changed += 1
        if not changed:
            break
    return blobs


def draw():
    Ls = {n: L() for n in LAYERS}
    draw_north(Ls)
    return despeckle(M.finish(Ls))


# ------------------------------------------------------------------ package
def artifacts():
    hp = S.load_helper()
    hp.ZIP_DT, hp.LAYERS, hp.PAL = MS.ZIP_DT, LAYERS, PAL
    blobs = draw()
    full = S.compose_layers(blobs)
    png = hp.png_bytes(full)
    pxo = MS.fix_pxo_metadata(hp.make_pxo(blobs, png))           # labels use the rebound direction (north)
    ora = hp.make_ora(blobs, png)
    pal = (json.dumps({"actor_id": ACTOR, "name": f"{ACTOR}-{D}-v01", "colors": PAL}, indent=2) + "\n").encode()
    return hp, blobs, full, png, pxo, ora, pal


def package_unchanged(dir_rel, manifest_rel):
    m = json.loads(open(fs(manifest_rel), "rb").read())
    files = {v["file"]: sha(open(fs(f"{dir_rel}/{v['file']}"), "rb").read()) == v["rawsha256"]
             for v in m["files"].values()}
    return {"files_match_manifest": all(files.values())}


def alpha_of(rel):
    from PIL import Image
    import numpy as np
    return np.array(Image.open(fs(rel)).convert("RGBA"))[:, :, 3] > 0


def gates(r):
    g = MS.gates(r)
    from PIL import Image
    import numpy as np
    full = r[2]
    al = full[..., 3] > 0
    used = {tuple(c) for c in full[al][:, :3]}
    with zipfile.ZipFile(io.BytesIO(r[4])) as z:
        dj = z.read("data.json")
    g["pxo_labels_north"] = (b"yanke-north" in dj
                             and all(s not in dj for s in (b"yanke-south", b"yanke-west")))
    # A back view must not paint any front-face feature colour anywhere, and the face layer stays skin only.
    face_colours = {S.rgb(k) for k in ("e1", "e2", "m1")}
    g["back_view_no_eye_or_mouth_colour"] = not (used & face_colours)
    face = r[1]["face"]; fm = face[..., 3] == 255
    fcols = {tuple(c) for c in face[fm][:, :3]}
    g["face_layer_skin_only"] = fcols <= {S.rgb(k) for k in ("s1", "s2", "s3", "s4")}
    g["back_hair_mass"] = int(np.count_nonzero(r[1]["hair"][..., 3] == 255)) >= 350
    g["back_ears_and_nape_visible"] = int(np.count_nonzero(fm)) >= 12
    gr = r[1]["grip"]; gy, gx = np.nonzero(gr[..., 3] == 255)
    g["handle_spans_back"] = bool(len(gy) and gy.max() - gy.min() >= 30 and gx.max() - gx.min() >= 25)
    hm = r[1]["hammer"]; hy, hx = np.nonzero(hm[..., 3] == 255)
    g["tool_head_above_shoulder"] = bool(len(hy) and hy.min() <= 14 and hx.max() >= 65)
    sa = alpha_of(SOUTH_PNG_REL); wa = alpha_of(WEST_PNG_REL)
    g["north_vs_south_alpha_diff"] = int(np.count_nonzero(al != sa))
    g["north_vs_mirrored_south_alpha_diff"] = int(np.count_nonzero(al != sa[:, ::-1]))
    g["north_vs_west_alpha_diff"] = int(np.count_nonzero(al != wa))
    g["north_vs_mirrored_west_alpha_diff"] = int(np.count_nonzero(al != wa[:, ::-1]))
    g["north_not_south_or_mirror"] = (g["north_vs_south_alpha_diff"] >= 400
                                      and g["north_vs_mirrored_south_alpha_diff"] >= 400)
    g["north_not_west_or_mirror"] = (g["north_vs_west_alpha_diff"] >= 400
                                     and g["north_vs_mirrored_west_alpha_diff"] >= 400)
    g["north_back_view"] = bool(g["north_face_no_eyes_or_mouth"] and g["back_view_no_eye_or_mouth_colour"]
                                and g["face_layer_skin_only"])
    return g


HARD = [k for k in MS.HARD if k != "face_has_eye"] + [
    "pxo_labels_north", "north_face_no_eyes_or_mouth", "back_view_no_eye_or_mouth_colour",
    "face_layer_skin_only", "back_hair_mass", "back_ears_and_nape_visible", "handle_spans_back",
    "tool_head_above_shoulder", "north_not_south_or_mirror", "north_not_west_or_mirror", "north_back_view"]


def manifest(files, g):
    m = {"actor_id": ACTOR, "content_id": f"content.char.{ACTOR}.static-{D}", "status": "UNAPPROVED",
         "direction": D, "pose": "idle-static", "canvas": [W, H], "pivot": list(PIN), "body_rows": list(BODY_ROWS),
         "display_scale": S.DISPLAY_SCALE, "logical_height_px": (BODY_ROWS[1] - BODY_ROWS[0] + 1) * S.DISPLAY_SCALE,
         "layers": [{"name": n, "visible": n != "guides"} for n in LAYERS],
         "face_layer_role": "ears and nape only (no eyes, nose or mouth); back-view skin",
         "beard_layer_role": "short thick beard tufts peeking at both jaw edges below the ears; no moustache or "
                             "mouth is painted",
         "view_notes": "back: camera sees the back of the head and the full short curly dark-brown hair mass with "
                       "upper-left sheen and right-side shadow, ears and nape skin, no front face; cream work shirt "
                       "across the broad back with shoulder seam and centre back seam; olive-green work apron side "
                       "skirts peeking beyond the hips and a tied bow with tails at the centre back below the belt; "
                       "two broad leather shoulder straps down the back joined by a horizontal back strap, central "
                       "brass ring and brass strap buckles; broad leather belt with loops, side brass fitting and the "
                       "red work rag at the character's RIGHT hip (screen right); dark-brown baggy work trousers with "
                       "seat, centre seat seam, two back patch pockets, olive side-knee patch edges and cuffed hems; "
                       "heavy brown leather boots from behind with cuffs, heel counters, brass outer buckles and thick "
                       "soles; notched heavy steel tool head above the character's RIGHT shoulder (screen right) with "
                       "the wooden handle running diagonally across the back to the character's LEFT hip (screen lower "
                       "left), leather wrap and brass ferrule at the butt; both arms down with cream rolled sleeves, "
                       "bare forearms, leather bracers and relaxed fists",
         "authored_deviations_from_sheet": [
             "pose: neutral back-view idle with both arms relaxed; the sheet's 3/4 pose carries the hammer across "
             "both shoulders.",
             "apron: seen from behind only as side skirts plus the tied bow and tails; the front bib/pocket are not "
             "painted on the back.",
             "face/beard: no front face or moustache is visible from behind; only ears, nape and jaw-edge beard tufts.",
             "small belt tools, pouch and cloth tatters beyond the one red rag are omitted for 48 px readability."],
         "files": {k: {"file": fname(*FILE_KEYS[k]), "rawsha256": sha(b)} for k, b in files.items()},
         "colour_count": g["colour_count"], "genuine_visible_role_layers": g["genuine_visible_role_layers"],
         "isolated_texels": g["isolated_texels"], "silhouette_width": g["silhouette_width"],
         "north_vs_south_alpha_diff": g["north_vs_south_alpha_diff"],
         "north_vs_mirrored_south_alpha_diff": g["north_vs_mirrored_south_alpha_diff"],
         "north_vs_west_alpha_diff": g["north_vs_west_alpha_diff"],
         "north_vs_mirrored_west_alpha_diff": g["north_vs_mirrored_west_alpha_diff"],
         "portrait_ref": {"file": MS.PORTRAIT_REL, "expected_sha256": MS.PORTRAIT_SHA, "approval": "UNAPPROVED",
                          "use": "identity reference only; no pixels sampled"},
         "continuity_ref": {"file": SOUTH_MANIFEST_REL, "rawsha256": PINS[SOUTH_MANIFEST_REL],
                            "use": "Yanke south v01 palette/layers/outline/gates; no pixels copied",
                            "west_ref": WEST_MANIFEST_REL},
         "bible_ref": "character-07: 37yo friendly heavy-tool craftsperson; broad leather shoulder straps, "
                      "dark-brown work trousers, notched heavy tool head, sturdy build, cheerful direct; "
                      "identity/hair anchor short curls and thick beard",
         "style_contract": "docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md",
         "view_contract": "outputs/yanke-n101/rpg-2-star-ocean-the-second_yanke_north-style-source-contract_unapproved-v01_20261024-092500-n101north.md",
         "source_contract": "same as Yanke south v01: 80x112, pivot (40,104), body rows 8..103, display scale 0.5 = "
                            "48 logical px, binary alpha, transparent border, same declared palette, 24..48 used "
                            "colours, >=8 genuine role layers, hidden guides layer; south face_has_eye replaced by "
                            "north_face_no_eyes_or_mouth (declared back-view rule)",
         "replaces_placeholder": "does not modify or count the old 32x48 native-animation placeholder",
         "author_tool": "tools/" + os.path.basename(__file__),
         "author_revision": "r1 (new north back view; no source replacement)",
         "broad_cluster_cleanup": "deterministic 4-neighbour despeckle after the outline pass; alpha, layer "
                                  "ownership and silhouette unchanged",
         "reused_tool_pins": {**PINS, **MS.PINS},
         "serialization_helper": S.HELPER_REL,
         "task_points": 2,
         "task_start_meters": START_NOTE,
         "base_revision": "f8e628c6e568cd6c1f724038432472df1dc34f46",
         "pixel_source": "code-authored native pixels, declared palette",
         "limitations": "north static only; no runtime wiring, no south/west/east changes, no motion, no GUI "
                        "SaveAs/reopen, no creator art approval"}
    return (json.dumps(m, indent=2) + "\n").encode()


def write_new(rel, data):
    """Write new bytes only; identical existing bytes are left untouched, different bytes are refused."""
    p = fs(rel)
    if os.path.exists(p):
        if open(p, "rb").read() != data:
            raise SystemExit(f"refusing to overwrite different file {rel}")
        return
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "xb") as fh:
        fh.write(data)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    r1, r2 = artifacts(), artifacts()
    g = gates(r1)
    g["deterministic_rebuild"] = all(a == b for a, b in zip(r1[3:], r2[3:]))
    su = package_unchanged(SOUTH_DIR_REL, SOUTH_MANIFEST_REL)
    wu = package_unchanged(WEST_DIR_REL, WEST_MANIFEST_REL)
    bad = [k for k in HARD + ["deterministic_rebuild"] if not g[k]]
    bad += [f"tool_pin:{rel}" for rel, ok in {**PIN_OK, **MS.PIN_OK}.items() if not ok]
    bad += [f"south:{k}" for k, v in su.items() if not v]
    bad += [f"west:{k}" for k, v in wu.items() if not v]
    files = dict(zip(("png", "pxo", "ora", "palette"), r1[3:]))
    names = {fname(*FILE_KEYS[k]): b for k, b in files.items()}
    names[fname("manifest", "json")] = manifest(files, g)
    named = {f"{OUT_REL}/{n}": b for n, b in names.items()}
    prev = None
    if cmd in ("build", "install", "preview"):                  # content-named preview: never reuses a name
        from PIL import Image
        buf = io.BytesIO()
        Image.fromarray(r1[2], "RGBA").resize((W * 6, H * 6), Image.NEAREST).save(buf, "PNG")
        prev = f"{QA_REL}/{SLUG}_{ACTOR}_{D}-preview-x6_unapproved-v01_{STAMP}-{sha(r1[3])[:8]}.png"
        write_new(prev, buf.getvalue())
        print("preview:", prev, sha(buf.getvalue()))
    if cmd in ("build", "install"):
        if bad:
            raise SystemExit(f"hard gates failed: {bad}")
        for n, data in names.items():
            write_new(f"{STAGE_REL}/{n}", data)
        write_new(f"{STAGE_REL}/.gdignore", b"")
        listing = {"staged": {f"{STAGE_REL}/{n}": sha(b) for n, b in sorted(names.items())},
                   "stage_gdignore": sha(b""), "install_to": OUT_REL,
                   "qa_preview_nonsource": {prev: sha(open(fs(prev), "rb").read())},
                   "hash": "sha256 of raw bytes"}
        listing_bytes = (json.dumps(listing, indent=2) + "\n").encode()
        write_new(f"{QA_REL}/{SLUG}_{ACTOR}_{D}-output-paths-rawhashes_unapproved-v01_{STAMP}-"
                  f"{uid('paths', sha(listing_bytes))}.json", listing_bytes)
        if cmd == "install":
            for n, data in names.items():
                write_new(f"{OUT_REL}/{n}", data)
            write_new(f"{OUT_REL}/.gdignore", b"")
            print("installed:", OUT_REL)
    disk = {rel: (sha(open(fs(rel), "rb").read()) == sha(b)) if os.path.exists(fs(rel)) else None
            for rel, b in named.items()}
    report = {k: g[k] for k in ("body_rows", "colour_count", "genuine_visible_role_layers", "visible_role_texels",
                                "isolated_texels", "silhouette_width", "stocky_shoulders_ge_34",
                                "north_vs_south_alpha_diff", "north_vs_mirrored_south_alpha_diff",
                                "north_vs_west_alpha_diff", "north_vs_mirrored_west_alpha_diff",
                                "north_face_no_eyes_or_mouth", "back_view_no_eye_or_mouth_colour",
                                "face_layer_skin_only", "back_hair_mass", "handle_spans_back",
                                "identity_colours_visible", "binary_alpha", "no_opaque_border",
                                "pin_inside_feet_span", "all_colours_declared", "ora_hidden",
                                "deterministic_rebuild")}
    staged = {f"{STAGE_REL}/{n}": (sha(open(fs(f'{STAGE_REL}/{n}'), "rb").read()) == sha(b))
              if os.path.exists(fs(f"{STAGE_REL}/{n}")) else None for n, b in names.items()}
    staged[f"{STAGE_REL}/.gdignore"] = os.path.exists(fs(f"{STAGE_REL}/.gdignore"))
    report.update(tool_pins_ok={**PIN_OK, **MS.PIN_OK}, south_unchanged=su, west_unchanged=wu,
                  disk_matches_rebuild=disk, hard_failures=bad)
    if cmd in ("build", "install"):
        report["stage_matches_rebuild"] = staged
    print(json.dumps(report, indent=1))
    ok = not bad and (all(v is True for v in staged.values()) if cmd in ("build", "install")
                      else all(v is True for v in disk.values()))
    print("YANKE_NORTH_V01_" + ("ALL_OK" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
