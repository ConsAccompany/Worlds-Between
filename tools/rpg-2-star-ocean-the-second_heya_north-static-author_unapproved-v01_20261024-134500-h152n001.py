"""Heya NORTH idle static draft (development only)."""
import hashlib, importlib.util, io, json, os, subprocess, sys, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.environ.get("WB_REPO") or os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
WEST_REL = "tools/rpg-2-star-ocean-the-second_heya_west-static-author_unapproved-v01_20261024-131500-h150w001.py"
WEST_PIN = "75467c614e38cfedf21c9f27f644ce2df88a518234398c40cff0752a14f8c070"
SLUG, ACTOR, D = "rpg-2-star-ocean-the-second", "heya", "north"
STAMP, RUN_ID = "20261024-134500", "h152n001"
OUT_REL = "game/assets/characters/heya-native-v01/north"
STAGE_REL = "outputs/heya-n152/staging/north"
QA_REL = "outputs/heya-n152/author"
CONTRACT_REL = "outputs/heya-n152/rpg-2-star-ocean-the-second_heya_north-style-source-contract_unapproved-v01_20261024-134500-h152n001.md"


def fs(rel):
    p = os.path.join(REPO, *rel.split("/"))
    return "\\\\?\\" + p if os.name == "nt" and len(p) > 240 and not p.startswith("\\\\?\\") else p


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, fs(rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


WEST = load(WEST_REL, "heya_west_v01_for_north")
PIN_OK = {WEST_REL: sha(open(fs(WEST_REL), "rb").read()) == WEST_PIN}
WEST.D, WEST.STAMP, WEST.RUN_ID = D, STAMP, RUN_ID
WEST.OUT_REL, WEST.STAGE_REL, WEST.QA_REL, WEST.CONTRACT_REL = OUT_REL, STAGE_REL, QA_REL, CONTRACT_REL
WEST.MS.D = D
M, S = WEST.M, WEST.S
PAL, LAYERS, FILE_KEYS = WEST.PAL, WEST.LAYERS, WEST.FILE_KEYS
W, H, PIN, BODY_ROWS, L = WEST.W, WEST.H, WEST.PIN, WEST.BODY_ROWS, WEST.L
SOUTH_MANIFEST_REL = WEST.SOUTH_MANIFEST_REL
WEST_MANIFEST_REL = "game/assets/characters/heya-native-v01/west/rpg-2-star-ocean-the-second_heya_west-manifest_unapproved-v01_20261024-131500-164571cd.json"
WEST_MANIFEST_SHA = "75b0519c2b1282dc4441b38a90fa3bc64868a442f1779c436455928fd8897752"


def draw_north(Ls):
    """Back view: nose away from camera. Character's LEFT is SCREEN LEFT."""
    # boots: rear view shafts, folded cuffs, stacked heels, soles
    b = Ls["boots"]
    for x0, x1 in ((28, 38), (42, 52)):
        b.shaded(x0, 89, x1, 99, "r1", "r2", "r3", 2, 2)
        b.hline(x0, x1, 88, "r2"); b.hline(x0, x1, 89, "r1")                     # folded cuff
        b.rect(x0 + 1, 92, x1 - 1, 93, "r3"); b.rect(x0 + 2, 92, x0 + 3, 92, "y2")  # back strap + brass eyelet
        b.rect(x0 + 1, 100, x1 - 1, 102, "r2"); b.rect(x0 + 2, 100, x1 - 2, 101, "r1")
        b.rect(x0, 102, x1, 103, "r3")                                           # heel / sole
        b.rect(x0 + 2, 103, x1 - 2, 103, "r3")
    b.rect(30, 100, 31, 103, "r3"); b.rect(49, 100, 50, 103, "r3")

    # dress: charcoal back panel, standing collar, centre seam, lower vent visible in the coat
    d = Ls["dress"]
    d.rows({32: (36, 44), 33: (34, 46), **{y: (33, 47) for y in range(34, 40)},
            **{y: (31, 49) for y in range(40, 52)}, **{y: (30, 50) for y in range(52, 60)}},
           "c2")
    d.rows({**{y: (29, 51) for y in range(60, 72)}, **{y: (28, 52) for y in range(72, 82)},
            **{y: (27, 53) for y in range(82, 89)}}, "c2")
    d.rect(33, 32, 35, 38, "c1"); d.rect(45, 32, 47, 38, "c3")
    d.vline(40, 34, 88, "c3"); d.vline(39, 34, 88, "c1")                        # centre back seam
    d.rect(37, 74, 43, 88, "c1"); d.vline(40, 74, 88, "c3")                     # lower vent
    d.hline(27, 53, 88, "c4")

    # coat: ivory closed back, yoke seam, centre seam, side shadows, worn hem, vent cut-out
    c = Ls["coat"]
    c.rows({33: (34, 46), 34: (31, 49), 35: (29, 51), **{y: (28, 52) for y in range(36, 41)},
            **{y: (27, 53) for y in range(41, 60)}, **{y: (28, 52) for y in range(60, 66)},
            **{y: (27, 53) for y in range(66, 89)}}, "w2")
    c.hline(29, 51, 35, "w3"); c.hline(28, 52, 36, "w2")                        # shoulder yoke
    c.vline(40, 36, 88, "w3"); c.vline(39, 36, 88, "w2")                        # centre back seam
    for y in range(41, 89):
        x0, x1 = (27, 53) if y < 60 else ((28, 52) if y < 66 else (27, 53))
        c.px(x0, y, "w1"); c.px(x0 + 1, y, "w1"); c.px(x1, y, "w3"); c.px(x1 - 1, y, "w3")
    c.rect(31, 42, 35, 48, "w3"); c.hline(31, 35, 42, "w2")                     # back yoke shadow
    c.rect(44, 42, 48, 48, "w3")
    c.a[76:87, 38:43] = 0                                                       # back vent reveals dress
    c.hline(27, 37, 87, "w3"); c.hline(43, 53, 87, "w3")
    c.hline(27, 37, 88, "w4"); c.hline(43, 53, 88, "w4")

    # apron: ties and bow at the back (apron is worn in front), side wrap edges
    ap = Ls["apron"]
    ap.rect(32, 60, 48, 62, "v2"); ap.hline(32, 48, 60, "v1"); ap.hline(32, 48, 62, "v3")
    ap.rect(35, 61, 39, 65, "v2"); ap.rect(41, 61, 45, 65, "v2")                 # bow loops
    ap.rect(35, 61, 35, 65, "v1"); ap.rect(45, 61, 45, 65, "v3")
    ap.rect(39, 61, 41, 66, "v1"); ap.hline(39, 41, 66, "v3")                   # knot
    ap.rect(37, 66, 38, 76, "v2"); ap.rect(42, 66, 43, 76, "v2")                 # bow tails
    ap.vline(36, 66, 76, "v3"); ap.vline(44, 66, 76, "v3")
    ap.rect(27, 68, 28, 84, "v2"); ap.rect(52, 68, 53, 84, "v2")                 # side wrap edges
    ap.vline(27, 68, 84, "v1"); ap.vline(53, 68, 84, "v3")

    # belt: slim leather belt across the back, small medicine pouch char-right (screen right)
    bl = Ls["belt"]
    bl.rect(28, 59, 52, 62, "r2"); bl.hline(28, 52, 59, "r1"); bl.hline(28, 52, 62, "r3")
    bl.rect(46, 63, 50, 69, "r2"); bl.hline(46, 50, 63, "r1"); bl.hline(46, 50, 69, "r3")
    bl.rect(47, 65, 48, 66, "y2")

    # strap: over the back from char-right shoulder to the char-left hip bag
    st = Ls["strap"]
    for i in range(28):
        y = 35 + i
        x = 50 - (23 * i) // 27
        col = "r1" if i % 5 == 0 else ("r3" if i % 7 == 0 else "r2")
        st.rect(x, y, x + 2, y, col)
    st.rect(35, 47, 38, 49, "y2"); st.rect(36, 48, 37, 49, "y1")                 # brass adjuster

    # bag: dark-red emergency bag on the character's LEFT hip (screen LEFT), brass clasps
    bg = Ls["bag"]
    bg.rect(15, 62, 27, 80, "b2")
    bg.rect(15, 62, 27, 68, "b1"); bg.hline(15, 27, 62, "b1"); bg.hline(15, 27, 68, "b3")
    bg.rect(25, 69, 27, 80, "b3"); bg.hline(15, 27, 80, "b3"); bg.hline(16, 26, 81, "b3")
    bg.rect(17, 64, 18, 66, "y2"); bg.rect(17, 64, 18, 65, "y1")
    bg.rect(23, 64, 24, 66, "y2"); bg.rect(23, 64, 24, 65, "y1")
    bg.rect(15, 59, 17, 61, "r2"); bg.rect(25, 59, 27, 61, "r2")
    bg.rect(18, 58, 24, 59, "r2"); bg.hline(18, 24, 58, "r1")                    # handle
    bg.rect(25, 70, 26, 77, "v2"); bg.hline(25, 26, 70, "v1"); bg.vline(26, 71, 76, "v3")  # bandage
    bg.rect(16, 70, 17, 78, "b1"); bg.rect(16, 70, 17, 71, "b2")

    # arms: both ivory sleeves visible from behind, pale cuffs, dark gloves
    a = Ls["arms"]
    a.shaded(24, 37, 30, 57, "w1", "w2", "w3", 2, 2); a.rect(24, 58, 30, 61, "w3")
    a.hline(24, 30, 58, "w2"); a.hline(24, 30, 61, "w4")
    a.shaded(23, 62, 29, 66, "k2", "k1", "k1", 1, 2)
    a.rect(21, 67, 28, 74, "k1"); a.rect(21, 67, 22, 69, "k2"); a.rect(27, 72, 28, 74, "k2")
    a.shaded(50, 37, 56, 60, "w1", "w2", "w3", 2, 2); a.rect(50, 61, 56, 64, "w3")
    a.hline(50, 56, 61, "w2"); a.hline(50, 56, 64, "w4")
    a.shaded(51, 65, 56, 69, "k2", "k1", "k1", 1, 2)
    a.rect(50, 70, 56, 76, "k1"); a.rect(50, 70, 51, 72, "k2"); a.rect(55, 74, 56, 76, "k2")

    # herb: sprig tucked at the char-right back waist (screen right), tips past the sleeve
    hb = Ls["herb"]
    hb.rect(46, 54, 46, 62, "n2")
    hb.rect(44, 55, 46, 56, "n1"); hb.rect(46, 57, 48, 58, "n1")
    hb.rect(44, 59, 46, 60, "n2"); hb.rect(46, 61, 48, 62, "n2")

    # face: rear head only, ears both sides + nape/neck under the scarf; no eyes/nose/mouth
    f = Ls["face"]
    f.rect(36, 28, 44, 36, "s2"); f.rect(37, 28, 43, 35, "s1"); f.rect(38, 34, 44, 36, "s3")
    for x0, x1, lit in ((25, 28, 26), (51, 54, 53)):
        f.rect(x0, 21, x1, 28, "s2"); f.vline(lit, 22, 27, "s1"); f.px(x1 if x0 == 25 else x0, 28, "s3")
    f.rect(33, 29, 35, 36, "s3"); f.rect(45, 29, 47, 36, "s3")

    # hair: crown seen from behind, upper-left sheen, swept-back strand lines into the nape
    h = Ls["hair"]
    h.rows({8: (34, 45), 9: (31, 48), 10: (29, 50), **{y: (28, 51) for y in range(11, 17)},
            **{y: (27, 52) for y in range(17, 24)}, **{y: (28, 51) for y in range(24, 28)},
            28: (31, 48), 29: (34, 45), 30: (36, 43)}, "h2")
    h.rows({8: (36, 41), 9: (33, 39), 10: (30, 36), 11: (29, 34), 12: (28, 32),
            13: (28, 31), 14: (28, 31), 15: (28, 32)}, "h1")                     # upper-left sheen
    h.rows({11: (45, 50), 12: (47, 51), **{y: (48, 52) for y in range(13, 24)}}, "h3")
    for x, y1 in ((33, 22), (40, 20), (47, 23)):
        h.rect(x, y1, x, 27, "h3" if x > 40 else "h1")                           # few broad strands
    h.rect(28, 22, 29, 27, "h3"); h.rect(50, 22, 51, 27, "h4")                   # side locks
    h.rect(36, 28, 43, 30, "h3"); h.rect(37, 29, 42, 30, "h2")                   # nape hair

    # braid: auburn braided coil LOW at the nape, centred on the back, banded plaits
    br = Ls["braid"]
    br.rows({24: (37, 43), 25: (35, 45), 26: (34, 46), 27: (33, 47),
             **{y: (33, 47) for y in range(28, 31)}, 31: (34, 46), 32: (35, 45),
             33: (36, 44), 34: (38, 42), 35: (39, 41)}, "h2")
    for y, (x0, x1) in ((26, (35, 45)), (28, (34, 46)), (30, (35, 45)), (32, (36, 44))):
        br.hline(x0, x1, y, "h1")
    for y, (x0, x1) in ((27, (34, 46)), (29, (34, 46)), (31, (35, 45)), (33, (37, 43))):
        br.hline(x0, x1, y, "h3")
    br.rect(37, 34, 43, 35, "h4"); br.hline(38, 42, 34, "h1")                   # braid tie

    # scarf: cool grey-white wrap at the neck, long tail down the char-left (screen-left) back
    sc = Ls["scarf"]
    sc.rows({34: (32, 48), 35: (31, 49), 36: (31, 49), 37: (32, 48), 38: (33, 47),
             39: (33, 47), 40: (34, 46), 41: (35, 45)}, "f1")
    sc.rect(44, 35, 48, 41, "f2"); sc.rect(45, 36, 47, 40, "f1")
    sc.rect(31, 35, 35, 41, "f2"); sc.rect(32, 36, 34, 39, "f1")
    sc.rect(37, 37, 38, 37, "f3"); sc.rect(42, 38, 43, 38, "f3"); sc.rect(46, 39, 47, 39, "f2")  # wrap folds
    sc.rows({**{y: (24, 32) for y in range(42, 50)}, **{y: (25, 32) for y in range(50, 58)},
             58: (26, 31), 59: (26, 31), 60: (27, 30)}, "f1")                   # long back tail
    sc.rect(25, 42, 26, 57, "f2"); sc.rect(31, 43, 32, 56, "f3")
    sc.hline(26, 31, 61, "f3"); sc.rect(27, 62, 28, 62, "f3"); sc.rect(29, 62, 30, 62, "f3")  # fringed end


def draw():
    Ls = {n: L() for n in LAYERS}
    draw_north(Ls)
    return M.finish(Ls)


WEST.draw = draw


def south_unchanged():
    return WEST.south_unchanged()


def west_unchanged():
    m = json.loads(open(fs(WEST_MANIFEST_REL), "rb").read())
    files = {v["file"]: sha(open(fs("game/assets/characters/heya-native-v01/west/" + v["file"]), "rb").read())
             == v["rawsha256"] for v in m["files"].values()}
    return {"manifest_sha_matches_pin": sha(open(fs(WEST_MANIFEST_REL), "rb").read()) == WEST_MANIFEST_SHA,
            "files_match_manifest": all(files.values()),
            "palette_colors_identical": json.loads(open(fs(
                "game/assets/characters/heya-native-v01/west/" + m["files"]["palette"]["file"]), "rb").read())
            ["colors"] == PAL}


def gates(r):
    hp, blobs, full, png, pxo, ora, pal = r
    g = M.gates(D, r)
    with zipfile.ZipFile(io.BytesIO(pxo)) as z:
        dj = z.read("data.json")
    g["pxo_labels_north"] = b"heya-north" in dj and b"heya-south" not in dj and b"heya-west" not in dj
    g["pxo_no_foreign_metadata"] = all(s not in dj for s in (b"milo", b"jiang", b"lin-que", b"muxiu", b"yanke"))
    g["palette_fits_pxo_grid_40"] = len(PAL) <= 40
    al = full[..., 3]
    g["isolated_texels"] = WEST.isolated(full)
    g["isolated_texels_le_24"] = g["isolated_texels"] <= 24
    cols = lambda keys: {S.rgb(k) for k in keys}
    used = {tuple(c) for c in full[al == 255][:, :3]}
    g["identity_colours_visible"] = {"auburn_hair": bool(used & cols(("h1", "h2"))),
                                     "grey_white_scarf": bool(used & cols(("f1", "f2"))),
                                     "dark_red_bag": bool(used & cols(("b1", "b2"))),
                                     "ivory_coat": bool(used & cols(("w1", "w2"))),
                                     "pale_apron": bool(used & cols(("v1", "v2"))),
                                     "charcoal_dress": bool(used & cols(("c1", "c2"))),
                                     "leather": bool(used & cols(("r1", "r2"))),
                                     "brass": bool(used & cols(("y1", "y2"))),
                                     "herb_green": bool(used & cols(("n1", "n2")))}
    g["identity_colours_all"] = all(g["identity_colours_visible"].values())
    vis = g["visible_role_texels"]
    g["anchor_layers_visible"] = all(vis[n] >= 12 for n in ("braid", "scarf", "bag", "apron", "coat", "hair",
                                                           "face", "herb"))
    ys, xs = np.nonzero(al)
    g["silhouette_width"] = int(xs.max() - xs.min() + 1)
    g["silhouette_width_28_56"] = 28 <= g["silhouette_width"] <= 56
    chest = al[38:47].any(axis=0)
    g["chest_width"] = int(np.count_nonzero(chest))
    g["slim_female_chest_28_38"] = 28 <= g["chest_width"] <= 38
    # rear head: both ears visible, broad crown, no facial features in the face layer
    fm = blobs["face"][..., 3] == 255; fy, fx = np.nonzero(fm)
    g["rear_ears_both_visible"] = int((fx < 32).sum()) >= 8 and int((fx > 48).sum()) >= 8
    hm = blobs["hair"][..., 3] == 255; hy, hx = np.nonzero(hm)
    g["rear_head_broad"] = int(hx.max() - hx.min() + 1) >= 20 and abs(float(hx.mean()) - 39.5) <= 2.0
    g["rear_head_detail"] = {"width": int(hx.max() - hx.min() + 1), "mean_x": round(float(hx.mean()), 2)}
    # genuine pixel check: the face layer must not contain eye-white, iris or mouth palette texels
    fcols = {tuple(c) for c in blobs["face"][fm][:, :3]}
    face_eye_mouth = {S.rgb(k) for k in ("e1", "e2", "m1")}
    g["north_face_no_eyes_or_mouth"] = not (fcols & face_eye_mouth)
    g["north_face_palette_detail"] = {"eye_mouth_colours_present": sorted(
        "#" + "".join(f"{v:02x}" for v in c) for c in fcols & face_eye_mouth)}
    # low centred braided coil at the nape
    bm = blobs["braid"][..., 3] == 255; by, bx = np.nonzero(bm)
    g["coil_low_at_nape_north"] = (int(bm.sum()) >= 80 and by.min() >= 24 and by.max() <= 44
                                   and 35.0 <= float(bx.mean()) <= 45.0
                                   and int(bx.max() - bx.min() + 1) >= 10)
    g["coil_detail_north"] = {"texels": int(bm.sum()), "rows": [int(by.min()), int(by.max())],
                              "mean_x": round(float(bx.mean()), 2), "width": int(bx.max() - bx.min() + 1)}
    g["hair_not_high_bun_north"] = int(hy.max()) <= 32 and int(hy.min()) >= 8
    # scarf: neck wrap plus a long tail down the back; only cool grey-white colours
    sm = blobs["scarf"][..., 3] == 255; sy, sx = np.nonzero(sm)
    scols = {tuple(c) for c in blobs["scarf"][sm][:, :3]}
    g["scarf_back_wrap_and_tail"] = (int(sm.sum()) >= 160 and int(sy.max()) >= 50 and int(sy.min()) <= 34
                                     and scols <= cols(("f1", "f2", "f3")))
    g["scarf_detail_north"] = {"texels": int(sm.sum()), "rows": [int(sy.min()), int(sy.max())]}
    # bag on the character's LEFT hip = screen LEFT in rear view
    gm = blobs["bag"][..., 3] == 255; gy, gx = np.nonzero(gm)
    gcols = {tuple(c) for c in blobs["bag"][gm][:, :3]}
    brass = cols(("y1", "y2"))
    g["bag_left_hip_north"] = (int(gm.sum()) >= 120 and float(gx.mean()) <= 28.0
                               and bool(gcols & cols(("b1", "b2"))) and sum(tuple(c) in brass for c in gcols) >= 1
                               and int(gy.max() - gy.min() + 1) >= 12)
    g["bag_detail_north"] = {"texels": int(gm.sum()), "mean_x": round(float(gx.mean()), 2),
                             "rows": [int(gy.min()), int(gy.max())]}
    # apron tied in a bow at the back, pale grey-white, centred
    am = blobs["apron"][..., 3] == 255; ay, ax = np.nonzero(am)
    acols = {tuple(c) for c in blobs["apron"][am][:, :3]}
    g["apron_tied_at_back"] = (int(am.sum()) >= 80 and 60 <= int(ay.max()) <= 90
                               and abs(float(ax.mean()) - 40.0) <= 6.0
                               and acols <= cols(("v1", "v2", "v3")))
    g["apron_detail_north"] = {"texels": int(am.sum()), "mean_x": round(float(ax.mean()), 2),
                               "rows": [int(ay.min()), int(ay.max())]}
    dress_cols = cols(("c1", "c2", "c3", "c4"))
    dress_mask = np.zeros(al.shape, bool)
    for c in dress_cols:
        dress_mask |= np.all(full[:, :, :3] == c, axis=2)
    g["charcoal_dress_visible"] = int((dress_mask & (al == 255)).sum()) >= 12
    g["charcoal_detail"] = int((dress_mask & (al == 255)).sum())
    g["herb_visible_north"] = int((blobs["herb"][..., 3] == 255).sum()) >= 12
    # own rear silhouette, not a flip/recolour of south or west
    def alpha_diff(rel):
        import glob
        f = sorted(glob.glob(os.path.join(REPO, rel, "*static*.png")))
        im = np.array(Image.open(f[0]).convert("RGBA"))
        return int(np.count_nonzero((im[:, :, 3] > 0) != (al > 0)))
    diffs = {k: alpha_diff(v) for k, v in (("south", "game/assets/characters/heya-native-v01/south"),
                                           ("west", "game/assets/characters/heya-native-v01/west"))}
    g["own_silhouette_not_flip"] = all(v >= 400 for v in diffs.values())
    g["silhouette_diff_detail"] = diffs
    g["profile_depth"] = g["silhouette_width"]
    return g


HARD = M.HARD + ["pxo_labels_north", "pxo_no_foreign_metadata", "palette_fits_pxo_grid_40",
                 "isolated_texels_le_24", "identity_colours_all", "anchor_layers_visible",
                 "silhouette_width_28_56", "slim_female_chest_28_38", "rear_ears_both_visible",
                 "rear_head_broad", "north_face_no_eyes_or_mouth", "coil_low_at_nape_north",
                 "hair_not_high_bun_north", "scarf_back_wrap_and_tail", "bag_left_hip_north",
                 "apron_tied_at_back", "charcoal_dress_visible", "herb_visible_north",
                 "own_silhouette_not_flip"]


def manifest(files, g):
    m = json.loads(WEST.manifest(files, g))
    m.pop("profile_depth", None)
    m.update({
        "face_layer_role": "rear head: both ears and the nape/neck only; no eyes, nose or mouth (no facial "
                           "features in the back view)",
        "braid_layer_role": "auburn braided coil LOW at the nape: one centred, banded plaited mass below the "
                            "crown at rows 24..35, never a high bun",
        "view_notes": "north rear view (nose away from camera; the character's LEFT is screen LEFT): back of the "
                      "auburn head with upper-left sheen and swept-back strand lines; low centred braided coil at "
                      "the nape; cool grey-white medical scarf wrapped at the neck with the long tail down the "
                      "char-left back; ivory clinician coat closed over the back with shoulder yoke, centre seam "
                      "and lower vent revealing the charcoal underdress; pale grey-white apron tied in a bow at "
                      "the back with side wrap edges; slim leather belt with a small medicine pouch at the "
                      "char-right back; dark-red emergency bag with brass clasps, leather handle and rolled "
                      "bandage on the character's LEFT hip (screen LEFT), hung from a leather cross-body strap "
                      "with a brass adjuster; small green herb sprig tucked at the char-right back waist; both "
                      "ivory sleeves, pale cuffs and dark gloves visible from behind, char-left hand on the bag; "
                      "brown leather boots seen from behind with folded cuffs, brass eyelets, stacked heels and "
                      "soles",
        "authored_deviations_from_sheet": [
            "North is a true rear view re-authored from the same identity contract, not a horizontal flip, "
            "recolour or upscale of the south or west static.",
            "The concept sheet is front-facing; the north view deliberately shows no eyes, nose or mouth. The "
            "canonical restrained patient smile remains part of the character identity and is carried by the "
            "south/west views, not invented on the back of the head.",
            "The white head-veil is omitted so the Bible's low auburn braided coil remains readable; the "
            "grey-white medical scarf is wrapped at the neck with its tail down the back.",
            "The sheet's long dark-red shawl is reduced to the canonical dark-red emergency bag on the "
            "character's left hip (screen left in rear view).",
            "The apron is worn in front, so from behind only its waist ties, bow, tails and side wrap edges are "
            "shown; this is an explicit rear-view readability choice, not a second apron.",
            "The herb sprig is at the char-right chest in front views; in the rear view it is tucked at the "
            "char-right back waist so the identity colour remains present without a floating prop.",
            "Fine embroidery, bag contents, tassels and multiple belt charms beyond the botanical hem motif, "
            "brass clasps and rolled bandage are omitted for 48 px readability."],
        "view_contract": CONTRACT_REL,
        "source_contract": "same as Heya south/west v01: 80x112, pivot (40,104), body rows 8..103, display scale "
                           "0.5 = 48 logical px, binary alpha, transparent border, 24..48 used colours, >=8 "
                           "genuine role layers, hidden guides layer; north rear-view gates replace the "
                           "front/profile face, coil, scarf, bag and apron gates",
        "author_tool": "tools/" + os.path.basename(__file__),
        "reused_tool_pins": {**WEST.PINS, **WEST.MS.PINS, WEST_REL: WEST_PIN},
        "west_continuity_ref": {"file": WEST_MANIFEST_REL, "rawsha256": WEST_MANIFEST_SHA,
                                "use": "Heya west v01 palette/layers/outline/gates and profile wording; no pixels copied"},
        "limitations": "north static only; no runtime wiring/defaults, no other directions, no motion, no GUI "
                       "save/reopen proof and no creator art approval"})
    return (json.dumps(m, indent=2) + "\n").encode()


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    r1, r2 = WEST.artifacts(), WEST.artifacts()
    g = gates(r1)
    g["deterministic_rebuild"] = WEST.check_r2(r1, r2)
    su, wu = south_unchanged(), west_unchanged()
    bad = [k for k in HARD + ["deterministic_rebuild"] if not g[k]]
    bad += [f"tool_pin:{rel}" for rel, ok in {**PIN_OK, **WEST.PIN_OK, **WEST.MS.PIN_OK}.items() if not ok]
    bad += [f"south:{k}" for k, v in su.items() if not v]
    bad += [f"west:{k}" for k, v in wu.items() if not v]
    files = dict(zip(("png", "pxo", "ora", "palette"), r1[3:]))
    named = {f"{STAGE_REL}/{WEST.fname(*FILE_KEYS[k])}": b for k, b in files.items()}
    named[f"{STAGE_REL}/{WEST.fname('manifest', 'json')}"] = manifest(files, g)
    from PIL import Image
    previews = {}
    if cmd in ("build", "preview"):
        os.makedirs(fs(QA_REL), exist_ok=True)
        previews[f"{QA_REL}/{SLUG}_{ACTOR}_{D}-preview-x6_unapproved-v01_{STAMP}-{sha(r1[3])[:8]}.png"] = (
            Image.fromarray(r1[2], "RGBA").resize((W * 6, H * 6), Image.NEAREST))
        previews[f"{QA_REL}/{SLUG}_{ACTOR}_{D}-preview-x12_unapproved-v01_{STAMP}-{sha(r1[3])[:8]}.png"] = (
            Image.fromarray(r1[2], "RGBA").resize((W * 12, H * 12), Image.NEAREST))
        for rel, im in previews.items():
            im.save(fs(rel)); print("preview:", rel)
    if cmd == "build":
        if bad:
            raise SystemExit(f"hard gates failed: {bad}")
        written = WEST.write_stage(named)
        listing = {"staged": written,
                   "qa_preview_nonsource": {rel: sha(open(fs(rel), "rb").read()) for rel in previews},
                   "hash": "sha256 of raw bytes, no normalization"}
        lp = f"{QA_REL}/{SLUG}_{ACTOR}_{D}-staging-output-paths-rawhashes_unapproved-v01_{STAMP}-{WEST.uid('paths')}.json"
        open(fs(lp), "wb").write((json.dumps(listing, indent=2) + "\n").encode())
    if cmd == "install":
        if bad:
            raise SystemExit(f"hard gates failed: {bad}")
        for rel, data in named.items():
            sp = fs(rel)
            if not os.path.exists(sp) or open(sp, "rb").read() != data:
                raise SystemExit(f"staging missing or stale: {rel}; run build first")
        os.makedirs(fs(OUT_REL), exist_ok=True)
        for rel, data in named.items():
            dst = f"{OUT_REL}/{os.path.basename(rel)}"; dp = fs(dst)
            if os.path.exists(dp):
                if open(dp, "rb").read() != data:
                    subprocess.run([sys.executable, "tools/wb_safe_replace.py", rel, dst], cwd=REPO, check=True)
            else:
                open(dp, "wb").write(data)
        for extra, extra_bytes in (("/.gdignore", b""), ("/.gitattributes", b"* -text -eol\n")):
            er = OUT_REL + extra; ep = fs(er)
            if not os.path.exists(ep):
                open(ep, "wb").write(extra_bytes)
            elif open(ep, "rb").read() != extra_bytes:
                subprocess.run([sys.executable, "tools/wb_safe_replace.py", er, er], cwd=REPO, check=True)
    disk = {}
    for rel, data in named.items():
        sr = f"{STAGE_REL}/{os.path.basename(rel)}"
        ir = f"{OUT_REL}/{os.path.basename(rel)}"
        disk["stage:" + sr] = (sha(open(fs(sr), "rb").read()) == sha(data)) if os.path.exists(fs(sr)) else None
        disk["install:" + ir] = (sha(open(fs(ir), "rb").read()) == sha(data)) if os.path.exists(fs(ir)) else None
    report = {k: g[k] for k in ("body_rows", "colour_count", "genuine_visible_role_layers", "visible_role_texels",
                                "isolated_texels", "identity_colours_visible", "binary_alpha", "no_opaque_border",
                                "pin_inside_feet_span", "all_colours_declared", "ora_hidden",
                                "deterministic_rebuild")}
    report.update({k: g[k] for k in ("silhouette_width", "chest_width", "rear_ears_both_visible",
                                     "rear_head_broad", "rear_head_detail", "north_face_no_eyes_or_mouth",
                                     "coil_low_at_nape_north", "coil_detail_north", "hair_not_high_bun_north",
                                     "scarf_back_wrap_and_tail", "scarf_detail_north", "bag_left_hip_north",
                                     "bag_detail_north", "apron_tied_at_back", "apron_detail_north",
                                     "charcoal_dress_visible", "charcoal_detail", "herb_visible_north",
                                     "own_silhouette_not_flip", "silhouette_diff_detail")})
    report.update(tool_pins_ok={**PIN_OK, **WEST.PIN_OK, **WEST.MS.PIN_OK}, south_unchanged=su,
                  west_unchanged=wu, disk_matches_rebuild=disk, hard_failures=bad)
    print(json.dumps(report, indent=1))
    stage_ok = all(v is True for k, v in disk.items() if k.startswith("stage:"))
    ok = not bad and stage_ok and all(v is not False for v in disk.values())
    print("HEYA_NORTH_V01_" + ("ALL_OK" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
