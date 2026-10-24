"""Muxiu SOUTH idle static, native 80x112 source package (UNAPPROVED v01).

content.char.muxiu.static-south. Code-authored native pixels in the Sea of Stars direction (broad clusters,
upper-left light), 48 logical px at display scale 0.5. Identity anchors (Bible character-06, 24-year-old animal
carer; unapproved character sheet used as identity reference only, no pixels sampled into the art): messy wavy
dark-brown hair with a long braid over the character's right shoulder (screen left), warm skin, brown-green eyes,
gentle smile; moss-green SHORT hooded cloak (capelet) with cream tree motif and fringed hem, closed by a round
brass clasp; cream rolled-sleeve shirt; small wooden whistle on a cord at the chest; knotted green/tan rope
bracelet on the character's left wrist (screen right); brown belt with buckle and hip pouches; olive-brown
trousers with darker knee patches; green crossed leg wraps; brown boots. Palette hues were chosen by eye from
point samples of the sheet; pixels are authored, not resampled.

Reuses the Lin Que v01 author (L pen, outline/guide finish, extended gates) and through it the Jiang south v01
gates and the male v8pair PNG/PXO/ORA serializers, exactly as the Milo south v01 author does. Their palette/layer
globals are rebound in memory only; no Lin, Jiang, Milo or male file is written. All reused tool files are
hash-pinned.

  python -X utf8 -I <this> build   # writes new files only (refuses to overwrite different bytes)
  python -X utf8 -I <this> check   # rebuilds twice in memory and compares with files on disk
"""
import hashlib, importlib.util, io, json, os, sys, zipfile
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG, ACTOR, D = "rpg-2-star-ocean-the-second", "muxiu", "south"
STAMP, RUN_ID = "20261024-071500", "6d3e9a51"
OUT_REL = "game/assets/characters/muxiu-native-v01/south"
QA_REL = "outputs/muxiu-s01/author"
LIN_TOOL_REL = "tools/rpg-2-star-ocean-the-second_lin-que_four-direction-static-author_unapproved-v01_20261022-222500-3d61c74e.py"
PINS = {LIN_TOOL_REL: "0ddbea4591312c767b2ac46da6be29302b908cf311adb92eaf5ed26c300eff82",
        "tools/rpg-2-star-ocean-the-second_jiang-lan_south-static-author_unapproved-v01_20261021-235007-514b9771.py":
            "35005f3c904802251c773838d61068d4aea847c993f6e354676e88a599db69b4",
        "tools/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair-static-pilot-build-and-check_unapproved-v01_20261018-130225-f28bd26d.py":
            "fcd9d6e88e7401097e9c8afe8061df6dcdd9e2132892680522d7d722ac2abb79",
        "tools/rpg-2-star-ocean-the-second_milo_south-static-author_unapproved-v01_20261023-215823-51a12dd6.py":
            "138a78d5a8ec32a4cbef7037c5eb5bda8740821f5868cf0a277ad4eda613cb6d"}   # structural template only
PORTRAIT_REL = "outputs/rpg-2-star-ocean-the-second_muxiu_character-sheet_v01_20261013-153818-25247999.png"
PORTRAIT_SHA = "9d80d2d7fc26ea10edd36948e620fbb5a5557db143eacb99fcb202347c22d606"
ZIP_DT = (2026, 10, 24, 7, 15, 0)

PAL = {  # declared palette, <=40 entries (male serializer palette grid is 8x5); upper-left light
    "s1": "f4c9a0", "s2": "dca480", "s3": "b07a58", "s4": "6e4430",                    # warm skin
    "h1": "7a5a44", "h2": "533c30", "h3": "3a2a22", "h4": "1e1612",                    # dark-brown hair / braid
    "e1": "f4efe4", "e2": "6a5a2c", "m1": "9a5243",                                    # eye white, brown-green iris, mouth
    "c1": "8c9a52", "c2": "6b7a3e", "c3": "4d5a2c", "c4": "2c3519",                    # moss-green cloak
    "w1": "f1e8d2", "w2": "d8c9a8", "w3": "ab9a7c", "w4": "6e624e",                    # cream shirt / motif
    "t1": "6f6a4e", "t2": "524f38", "t3": "3a3828", "t4": "222016",                    # olive-brown trousers
    "r1": "9a6a44", "r2": "6e4a30", "r3": "4a3020", "r4": "2a1a10",                    # leather / boots
    "q1": "c8a86a", "q2": "8f7444",                                                    # tan rope
    "x1": "dcbc8c", "x2": "a07e58",                                                    # whistle wood
    "y1": "d8b060", "k1": "140e0a",                                                    # brass clasp, sole
}
LAYERS = ["boots", "legwraps", "trousers", "shirt", "belt", "pouches", "cloak", "arms", "bracelet", "whistle",
          "face", "hair", "braid", "guides"]
OUTLINE = {"boots": "k1", "legwraps": "c4", "trousers": "t4", "shirt": "w4", "belt": "r4", "pouches": "r4",
           "cloak": "c4", "arms": "s4", "bracelet": "r3", "whistle": "r3", "face": "s4", "hair": "h4", "braid": "h4"}
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
M = load(LIN_TOOL_REL, "lin_que_v01_for_muxiu")               # loads its own Jiang module instance as M.S
S = M.S
for mod in (M, S):                                            # rebind in memory only
    mod.PAL, mod.LAYERS, mod.OUTLINE, mod.ZIP_DT = PAL, LAYERS, OUTLINE, ZIP_DT
M.ACTOR = ACTOR
W, H, PIN, BODY_ROWS, L = S.W, S.H, S.PIN, S.BODY_ROWS, S.L


# ------------------------------------------------------------------ south (front)
def draw_south(Ls):
    # boots: brown leather, folded cuff, laces, rounded toes
    b = Ls["boots"]
    for x0, x1 in ((29, 39), (41, 51)):
        b.shaded(x0 + 1, 92, x1 - 1, 98, "r1", "r2", "r3", 2, 2)
        b.rect(x0 + 1, 92, x1 - 1, 93, "r2"); b.hline(x0 + 1, x1 - 1, 92, "r1")   # cuff
        b.rect(x0 + 4, 95, x0 + 6, 97, "q2")                                        # laces
        b.shaded(x0, 99, x1, 101, "r1", "r2", "r3", 3, 2)
        b.hline(x0, x1, 102, "r3"); b.hline(x0, x1, 103, "k1")
    b.rect(28, 99, 28, 103, "r3"); b.rect(52, 99, 52, 103, "r3")

    # leg wraps: green cloth bound with broad tan cord bands (a per-pixel X cross reads as noise at 48 px)
    lw = Ls["legwraps"]
    for x0, x1 in ((30, 38), (42, 50)):
        lw.shaded(x0, 82, x1, 91, "c2", "c2", "c3", 2, 2)
        lw.hline(x0, x1, 82, "w2"); lw.hline(x0, x1, 83, "w3")                      # cream top band
        lw.hline(x0, x1, 85, "q2"); lw.hline(x0, x1, 88, "q2")                      # cord bands
        lw.rect(x0 + 3, 86, x0 + 5, 87, "q1")                                        # cord knot

    # trousers: olive-brown, loose, darker knee patches
    t = Ls["trousers"]
    t.rect(31, 64, 49, 70, "t2")
    t.shaded(29, 70, 39, 83, "t1", "t2", "t3", 2, 2)
    t.shaded(41, 70, 51, 83, "t1", "t2", "t3", 2, 2)
    t.vline(40, 67, 83, "t4")
    t.rect(32, 75, 36, 79, "t3"); t.hline(32, 36, 75, "t4")                         # knee patches
    t.rect(44, 76, 48, 80, "t3"); t.hline(44, 48, 76, "t4")

    # shirt: cream, open collar; visible at the neck V and between capelet hem and belt
    sh = Ls["shirt"]
    sh.rows({33: (36, 44), 34: (35, 45), 35: (35, 45)}, "w1")
    sh.shaded(31, 36, 49, 61, "w1", "w2", "w3", 3, 3)
    sh.rows({33: (39, 41), 34: (39, 41), 35: (40, 40)}, "s2")                       # collarbone V
    sh.rect(36, 56, 37, 61, "w3"); sh.rect(43, 57, 44, 61, "w3")                    # cloth folds

    # belt: brown leather with brass buckle
    bl = Ls["belt"]
    bl.rect(30, 61, 50, 64, "r2"); bl.hline(30, 50, 61, "r1"); bl.hline(30, 50, 64, "r3")
    bl.rect(38, 61, 42, 64, "y1"); bl.rect(39, 62, 41, 63, "r3")

    # pouches: two leather hip pouches, larger on the character's right (screen left)
    p = Ls["pouches"]
    p.shaded(24, 62, 31, 71, "r1", "r2", "r3", 2, 2); p.rect(24, 62, 31, 65, "r3"); p.hline(24, 31, 62, "r2")
    p.rect(27, 66, 28, 67, "y1")
    p.shaded(49, 62, 55, 69, "r1", "r2", "r3", 2, 2); p.rect(49, 62, 55, 64, "r3")
    p.rect(51, 65, 52, 66, "y1")

    # cloak: moss-green short hooded capelet, bunched hood at the neck, tree motif band, fringed hem
    c = Ls["cloak"]
    rows = {}
    for y in range(31, 59):
        k = y - 31
        half = 13 + min(k, 16) // 2 + max(0, k - 16) // 3      # shoulders slope 1px per 2 rows, A-line hem
        rows[y] = (40 - half, 40 + half - 1)
    c.rows(rows, "c2")
    for y, (x0, x1) in rows.items():                            # light plane left, shadow plane right
        c.hline(x0, x0 + 4, y, "c1"); c.hline(x1 - 4, x1, y, "c3")
    c.rows({29: (30, 50), 30: (28, 52), 31: (27, 53), 32: (27, 53)}, "c3")           # hood roll behind the neck
    c.rows({29: (31, 37), 30: (29, 36), 31: (28, 35)}, "c2")
    c.rows({32: (28, 34), 33: (27, 33)}, "c1")
    for y in range(50, 54):                                     # cream tree motif band
        c.hline(rows[y][0] + 2, rows[y][1] - 2, y, "c3")
    for mx in (31, 49, 58):                                     # left motif sits behind the braid
        c.vline(mx, 49, 54, "w2"); c.hline(mx - 1, mx + 1, 50, "w2"); c.hline(mx - 2, mx + 2, 52, "w2")
    for y in range(55, 59):                                     # fringe: alternating 2px tassels
        x0, x1 = rows[y]
        c.hline(x0, x1, y, "c3")
    for x in range(rows[58][0], rows[58][1] + 1, 4):
        c.rect(x, 59, x + 1, 61, "q2"); c.hline(x, x + 1, 59, "c3")

    # arms: forearms below the capelet, cream rolled sleeves, relaxed hands
    a = Ls["arms"]
    for x0 in (16, 59):
        a.shaded(x0, 59, x0 + 5, 63, "w1", "w2", "w3", 2, 2)                        # rolled sleeve
        a.hline(x0, x0 + 5, 63, "w3")
        a.shaded(x0 + 1, 64, x0 + 5, 70, "s1", "s2", "s3", 2, 1)
        a.shaded(x0 + 1, 71, x0 + 5, 75, "s2", "s2", "s3", 1, 1); a.hline(x0 + 1, x0 + 5, 76, "s3")
        a.hline(x0 + 1, x0 + 5, 72, "s3")                                           # knuckle line

    # bracelet: knotted green/tan rope on the character's left wrist (screen right)
    q = Ls["bracelet"]
    q.rect(59, 68, 65, 70, "c2")
    for x in range(59, 66, 2):
        q.rect(x, 68, x, 70, "q1")
    q.rect(62, 71, 63, 72, "c3")                                                    # dangling knot

    # whistle: small wooden whistle on a tan cord at the chest, in the capelet's neck V
    wh = Ls["whistle"]
    wh.rows({34: (37, 37), 35: (37, 37), 36: (38, 38), 37: (38, 38)}, "q2")
    wh.rows({34: (43, 43), 35: (43, 43), 36: (42, 42), 37: (42, 42)}, "q2")
    wh.rect(38, 38, 42, 39, "y1")                                                   # brass clasp
    wh.rect(39, 40, 41, 46, "x1"); wh.vline(41, 40, 46, "x2"); wh.hline(39, 41, 46, "x2")
    wh.rect(39, 42, 41, 42, "q2")

    # face: oval, gentle closed smile, warm brown-green eyes
    f = Ls["face"]
    f.rows({**{y: (31, 49) for y in range(15, 27)}, 27: (32, 48), 28: (32, 48), 29: (33, 47), 30: (34, 46),
            31: (36, 44), 32: (38, 42)}, "s2")
    f.rect(31, 16, 33, 26, "s1"); f.rect(47, 16, 49, 28, "s3"); f.rect(46, 28, 46, 30, "s3")
    f.rect(36, 33, 44, 35, "s3"); f.rect(37, 33, 43, 34, "s2")                      # neck
    f.hline(33, 37, 20, "h3"); f.hline(43, 47, 20, "h3")                            # soft brows
    for ex in (34, 43):                                                             # eyes
        f.hline(ex, ex + 3, 22, "h4")
        f.rect(ex, 23, ex + 3, 24, "e1"); f.rect(ex + 1, 23, ex + 2, 24, "e2"); f.px(ex + 2, 23, "h4")
    f.px(41, 24, "s3"); f.px(41, 25, "s3"); f.hline(39, 41, 26, "s3")               # nose
    f.hline(37, 43, 28, "m1"); f.hline(35, 36, 27, "m1"); f.hline(44, 45, 27, "m1")  # wide easy smile
    f.rect(33, 25, 34, 26, "s1"); f.px(47, 29, "s3")                                # cheek plane, jaw shade

    # hair: messy wavy dark brown; tufted crown, swept fringe locks with forehead gaps, side locks to the jaw.
    # Silhouette steps are >=2 px so outline runs join (1 px stairs leave isolated outline texels).
    h = Ls["hair"]
    h.rows({8: (32, 35), 9: (30, 48), 10: (28, 50), **{y: (26, 53) for y in range(11, 16)}}, "h2")
    h.rows({8: (44, 47)}, "h3")
    h.rows({16: (26, 34), 17: (26, 33), 18: (26, 32)}, "h2")                        # fringe locks, gaps show brow
    h.rows({16: (36, 41), 17: (37, 40), 18: (38, 39)}, "h2")
    h.rows({16: (44, 53), 17: (45, 53), 18: (46, 53)}, "h3")
    h.rows({y: (26, 31) for y in range(19, 30)}, "h2"); h.rows({30: (28, 29)}, "h2")
    h.rows({y: (50, 53) for y in range(19, 31)}, "h3"); h.rows({31: (52, 53)}, "h3")
    h.rows({9: (32, 37), 10: (30, 39), 11: (29, 36), 12: (29, 33)}, "h1")          # upper-left sheen
    h.rows({13: (37, 41), 14: (39, 42)}, "h1"); h.rows({y: (27, 28) for y in range(19, 24)}, "h1")
    h.rect(48, 10, 53, 15, "h3"); h.rows({12: (43, 44), 13: (44, 45), 14: (45, 46)}, "h3")  # right plane, wave breaks

    # braid: long plait from behind the character's right ear over the shoulder (screen left), tan tie, tuft
    br = Ls["braid"]
    for i, y in enumerate(range(28, 60)):
        x = 27 - min(i, 6) // 2                                 # drifts outward over the shoulder, then hangs
        seg = (i // 3) % 2
        br.hline(x - 2, x + 1, y, "h2" if seg == 0 else "h3")
        br.px(x - 2 + (seg * 3), y, "h1" if seg == 0 else "h4")
    br.rect(22, 60, 26, 61, "q1"); br.hline(22, 26, 61, "q2")                       # tan tie
    br.rows({62: (22, 26), 63: (21, 26), 64: (21, 27), 65: (21, 26), 66: (22, 25)}, "h2")  # tuft
    br.rows({63: (22, 23), 64: (22, 23)}, "h1"); br.rows({65: (25, 26), 66: (24, 25)}, "h3")


def open_neck(Ls):
    """Capelet neck V: transparent wedge in the cloak layer so the shirt collar and whistle show through."""
    a = Ls["cloak"].a
    for y in range(33, 48):
        half = max(0, 4 - (y - 33) // 4)
        a[y, 40 - half:40 + half + 1] = 0


def draw():
    Ls = {n: L() for n in LAYERS}
    draw_south(Ls)
    open_neck(Ls)
    return M.finish(Ls)


# ------------------------------------------------------------------ package
def fix_pxo_metadata(pxo):
    """Male helper hardcodes its export/palette names; rewrite for Muxiu south, keep entry order and dates."""
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
    g["pxo_no_foreign_metadata"] = all(s not in dj for s in (b"lin-que", b"milo", b"jiang"))
    g["palette_fits_pxo_grid_40"] = len(PAL) <= 40
    al = full[..., 3]
    g["isolated_texels"] = isolated(full)
    g["isolated_texels_le_24"] = g["isolated_texels"] <= 24
    cols = lambda keys: {S.rgb(k) for k in keys}
    used = {tuple(c) for c in full[al == 255][:, :3]}
    g["identity_colours_visible"] = {"moss_cloak": bool(used & cols(("c1", "c2"))),
                                     "brown_hair": bool(used & cols(("h1", "h2"))),
                                     "cream_shirt": bool(used & cols(("w1", "w2"))),
                                     "tan_rope": bool(used & cols(("q1", "q2"))),
                                     "olive_trousers": bool(used & cols(("t1", "t2")))}
    g["identity_colours_all"] = all(g["identity_colours_visible"].values())
    vis = g["visible_role_texels"]
    g["anchor_layers_visible"] = all(vis[n] >= 12 for n in ("cloak", "braid", "bracelet", "whistle", "hair", "face"))
    ys, xs = np.nonzero(al)
    g["silhouette_width"] = int(xs.max() - xs.min() + 1)
    return g


HARD = M.HARD + ["pxo_no_foreign_metadata", "palette_fits_pxo_grid_40", "isolated_texels_le_24",
                 "identity_colours_all", "anchor_layers_visible", "face_has_eye"]


def manifest(files, g):
    m = {"actor_id": ACTOR, "content_id": f"content.char.{ACTOR}.static-{D}", "status": "UNAPPROVED",
         "direction": D, "pose": "idle-static", "canvas": [W, H], "pivot": list(PIN), "body_rows": list(BODY_ROWS),
         "display_scale": S.DISPLAY_SCALE, "logical_height_px": (BODY_ROWS[1] - BODY_ROWS[0] + 1) * S.DISPLAY_SCALE,
         "layers": [{"name": n, "visible": n != "guides"} for n in LAYERS],
         "face_layer_role": "front face, two brown-green eyes, soft brows, nose, wide easy smile, neck",
         "view_notes": "front: messy wavy dark-brown hair with swept fringe and side locks; long braid over the "
                       "character's right shoulder (screen left) with tan tie and tuft; moss-green short hooded "
                       "capelet with hood roll, cream tree motif band and fringed hem, brass clasp; cream shirt "
                       "with open collar and rolled sleeves; small wooden whistle on a tan cord in the neck V; "
                       "knotted green/tan rope bracelet on the character's left wrist (screen right); brown belt, "
                       "two leather hip pouches; olive-brown trousers with knee patches; green leg wraps with "
                       "crossed tan cord; brown boots",
         "authored_deviations_from_sheet": [
             "pose: neutral front idle with both arms down; the sheet's 3/4 pose has the right hand at the clasp.",
             "chest straps and extra belt charms/cloth tatters omitted for 48 px readability.",
             "whistle moved from the strap to a neck cord in the capelet V so it reads at 48 px."],
         "files": {k: {"file": fname(*FILE_KEYS[k]), "rawsha256": sha(b)} for k, b in files.items()},
         "colour_count": g["colour_count"], "genuine_visible_role_layers": g["genuine_visible_role_layers"],
         "isolated_texels": g["isolated_texels"],
         "portrait_ref": {"file": PORTRAIT_REL, "expected_sha256": PORTRAIT_SHA, "approval": "UNAPPROVED",
                          "use": "identity reference only; hues chosen by eye from point samples, no pixels copied"},
         "bible_ref": "character-06: 24yo animal carer; moss-green short cloak, knotted rope bracelet, small whistle, "
                      "swaying braid",
         "style_contract": "docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md",
         "source_contract": "reuses the Jiang/Lin/Milo native static contract: 80x112, pivot (40,104), body rows "
                            "8..103, display scale 0.5 = 48 logical px, binary alpha, transparent border, declared "
                            "palette 24..48 used colours, >=8 genuine role layers, hidden guides layer",
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
        prev = f"{QA_REL}/{SLUG}_{ACTOR}_{D}-preview-x6_unapproved-v01_{STAMP}-{sha(r1[3])[:8]}.png"  # content-named
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
        open(fs("game/assets/characters/muxiu-native-v01/.gdignore"), "ab").close()
        listing = {"outputs": {rel: sha(b) for rel, b in sorted(named.items())},
                   "qa_preview_nonsource": {prev: sha(open(fs(prev), "rb").read())}, "hash": "sha256 of raw bytes"}
        lp = f"{QA_REL}/{SLUG}_{ACTOR}_{D}-output-paths-rawhashes_unapproved-v01_{STAMP}-{uid('paths')}.json"
        open(fs(lp), "wb").write((json.dumps(listing, indent=2) + "\n").encode())
    disk = {rel: (sha(open(fs(rel), "rb").read()) == sha(b)) if os.path.exists(fs(rel)) else None
            for rel, b in named.items()}
    report = {k: g[k] for k in ("body_rows", "colour_count", "genuine_visible_role_layers", "visible_role_texels",
                                "isolated_texels", "silhouette_width", "identity_colours_visible", "binary_alpha",
                                "no_opaque_border", "pin_inside_feet_span", "all_colours_declared", "ora_hidden",
                                "deterministic_rebuild")}
    report.update(tool_pins_ok=PIN_OK, disk_matches_rebuild=disk, hard_failures=bad)
    print(json.dumps(report, indent=1))
    ok = not bad and all(v is True for v in disk.values())
    print("MUXIU_SOUTH_V01_" + ("ALL_OK" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
