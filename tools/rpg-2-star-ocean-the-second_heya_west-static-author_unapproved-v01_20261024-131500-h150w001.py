"""Heya WEST idle static, native 80x112 source package (UNAPPROVED v01).

content.char.heya.static-west. Code-authored native pixels in the Sea of Stars direction (broad clusters,
upper-left light), 48 logical px at display scale 0.5. West = nose toward screen LEFT, so the character's
LEFT side faces the camera. Reauthored in forward coordinates with the Lin Que `P` pen (s = -1); it is not a
rotation, squash, recolour or mirror of south. Style/source contract (recorded before the verified build):
outputs/heya-w150/rpg-2-star-ocean-the-second_heya_west-style-source-contract_unapproved-v01_20261024-131500-h150w001.md

Identity (Bible character-26 / companion #26, 44-year-old clinician; unapproved character sheet is an identity
reference only, no pixels sampled): warm mature face with restrained closed-lip smile; auburn hair gathered into
a braided coil LOW at the nape (in profile a plaited mass behind/below the ear, never a high bun); cool grey-white
medical scarf wound at the neck with the long tail down the near front; ivory open clinician coat over a pale
grey-white apron and charcoal underdress; dark-red emergency bag with brass clasps on the character's LEFT hip
(the near hip in a west-facing profile); dark gloves; brown leather boots; small herb sprig.

Reuses the hash-pinned Heya south v01 author in memory (and through it the Lin Que v01 P/finish/gates, the
Jiang v01 gates and the male v8pair PNG/PXO/ORA serializers) with the same palette, layers, outline colours and
serialization contract. Only the direction label is rebound in memory; the south tool and committed south package
stay byte-identical and are verified against their pinned hashes.

  python -X utf8 -I <this> preview  # previews only, no package writes
  python -X utf8 -I <this> build    # fresh staging package under outputs/heya-w150/staging/west
  python -X utf8 -I <this> install  # installs verified staging bytes; helper on differing destination
  python -X utf8 -I <this> check    # rebuilds twice in memory and compares staging + installed files
"""
import hashlib, importlib.util, io, json, os, subprocess, sys, zipfile
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG, ACTOR, D = "rpg-2-star-ocean-the-second", "heya", "west"
STAMP, RUN_ID = "20261024-131500", "h150w001"
OUT_REL = "game/assets/characters/heya-native-v01/west"
STAGE_REL = "outputs/heya-w150/staging/west"
QA_REL = "outputs/heya-w150/author"
SOUTH_TOOL_REL = "tools/rpg-2-star-ocean-the-second_heya_south-static-author_unapproved-v01_20261024-125310-h148s001.py"
SOUTH_DIR_REL = "game/assets/characters/heya-native-v01/south"
SOUTH_MANIFEST_REL = SOUTH_DIR_REL + "/rpg-2-star-ocean-the-second_heya_south-manifest_unapproved-v01_20261024-125310-a9210ea1.json"
CONTRACT_REL = "outputs/heya-w150/rpg-2-star-ocean-the-second_heya_west-style-source-contract_unapproved-v01_20261024-131500-h150w001.md"
PINS = {SOUTH_TOOL_REL: "3bccc473faba713b7ea096ffa9154dd7b59f91fcc303b393e421ccd2bca1b31e",
        SOUTH_MANIFEST_REL: "d6ddec7e38d74083e6a774d96e7235c9b64fe5ba7b7ec3664f5067f82217d80c"}


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
_spec = importlib.util.spec_from_file_location("heya_south_v01_for_west", fs(SOUTH_TOOL_REL))
MS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MS)                                   # pins Lin/Jiang/male/Muxiu tools itself
MS.D = D                                                       # rebind the direction label in memory only
M, S = MS.M, MS.S
PAL, LAYERS, FILE_KEYS = MS.PAL, MS.LAYERS, MS.FILE_KEYS
W, H, PIN, BODY_ROWS, L = MS.W, MS.H, MS.PIN, MS.BODY_ROWS, MS.L


# ------------------------------------------------------------------ west (profile, nose to screen left)
def draw_west(Ls):
    """Forward coordinates: f > 0 is the facing direction (screen x = 40 - f). Light stays upper-left on screen,
    so P.shaded puts the highlight on the front (screen-left) edge. Silhouette steps are >= 2 px."""
    p = {n: M.P(Ls[n], -1) for n in LAYERS}

    # boots: far (right) boot darker and set a little ahead; near (left) boot brown, folded cuff, world/heel
    b = p["boots"]
    b.shaded(-2, 91, 7, 102, "r2", "r2", "r3", 1, 1); b.rect(6, 97, 8, 102, "r2")     # far boot + toe
    b.rect(-2, 102, 8, 102, "r3")
    b.shaded(-6, 88, 3, 102, "r1", "r2", "r3", 2, 2)
    b.rect(-6, 88, 3, 90, "r1"); b.rect(-6, 88, 3, 88, "r2")                           # folded cuff
    b.rect(-4, 92, 1, 93, "r2"); b.px(-2, 92, "y2")                                    # strap + brass eyelet
    b.shaded(2, 97, 4, 102, "r1", "r1", "r2", 1, 1)                                    # near toe
    b.rect(-7, 99, -6, 102, "r3"); b.rect(-7, 102, 8, 102, "r3")                       # heel, welt
    b.rect(-7, 103, 8, 103, "r3")                                                      # sole

    # dress: charcoal underdress, high collar, open front strip seen in the coat gap, A-line skirt
    d = p["dress"]
    d.rows({34: (-2, 3), 35: (-3, 4), **{y: (-4, 5) for y in range(36, 41)},
            **{y: (-5, 6) for y in range(41, 60)}, **{y: (-6, 6) for y in range(60, 66)},
            **{y: (-7, 7) for y in range(66, 80)}, **{y: (-8, 7) for y in range(80, 89)}}, "c2")
    d.rect(-4, 36, -3, 58, "c1"); d.rect(5, 36, 6, 58, "c3")
    d.rect(3, 36, 5, 58, "c1"); d.rect(6, 36, 6, 58, "c2")                             # front placket in coat gap
    d.rect(-8, 88, 7, 88, "c4")

    # coat: ivory open clinician coat, standing collar behind the neck, long back panel flaring behind
    c = p["coat"]
    c.rows({33: (-4, 3), 34: (-5, 5), 35: (-7, 5), **{y: (-8, 6) for y in range(36, 41)},
            **{y: (-8, 2) for y in range(41, 60)}, **{y: (-9, 4) for y in range(60, 66)},
            **{y: (-10, 5) for y in range(66, 76)}, **{y: (-11, 6) for y in range(76, 88)}}, "w2")
    c.rect(2, 36, 3, 58, "w1"); c.rect(-8, 36, -7, 59, "w3")
    c.rect(-9, 60, -8, 65, "w3"); c.rect(-10, 66, -9, 75, "w3"); c.rect(-11, 76, -10, 87, "w3")
    c.rect(-7, 34, 5, 34, "w3"); c.rect(-8, 35, 6, 35, "w2")                                 # shoulder seam
    c.rows({32: (-4, -1), 33: (-5, 0), **{y: (-6, 0) for y in range(34, 38)}}, "w2")   # standing collar
    c.rect(-1, 32, 0, 37, "w1"); c.rect(-5, 33, -4, 37, "w3")
    c.rect(-6, 45, -3, 50, "w3"); c.rect(-6, 45, -3, 45, "w2"); c.px(-5, 47, "w4")        # side pocket
    c.rect(-11, 87, -7, 87, "w3"); c.rect(-10, 87, 6, 87, "w3"); c.rect(-10, 88, 6, 88, "w4")   # worn hem
    c.rect(-9, 62, -6, 70, "w3")                                                       # back fold shadow

    # apron: pale grey-white half-apron over the near front of the skirt, waist tie, botanical hem motif
    ap = p["apron"]
    ap.rows({59: (-1, 6), 60: (-2, 7), **{y: (-2, 7) for y in range(61, 72)},
             **{y: (-3, 7) for y in range(72, 86)}}, "v2")
    for y in range(60, 86):
        x0, x1 = (-2, 7) if y < 72 else (-3, 7)
        ap.px(x0, y, "v1"); ap.px(x0 + 1, y, "v1"); ap.px(x1, y, "v3"); ap.px(x1 - 1, y, "v3")
    ap.rect(-3, 85, 7, 85, "v3"); ap.rect(-3, 86, 7, 86, "v3")
    ap.rect(2, 72, 2, 81, "v3"); ap.rect(0, 76, 1, 77, "v3"); ap.rect(4, 78, 5, 79, "v3")
    ap.rect(1, 80, 2, 81, "v3"); ap.rect(3, 74, 4, 75, "v3")                           # botanical sprig
    ap.rect(-2, 58, 1, 59, "v3"); ap.px(-4, 59, "v3"); ap.px(5, 59, "v3")              # waist ties

    # belt: slim leather belt, brass buckle at the front, small medicine pouch at the back
    bl = p["belt"]
    bl.rect(-7, 59, 5, 62, "r2"); bl.rect(-7, 59, 5, 59, "r1"); bl.rect(-7, 62, 5, 62, "r3")
    bl.rect(2, 59, 4, 62, "y2"); bl.rect(3, 60, 4, 61, "r3"); bl.rect(3, 60, 3, 60, "y1")
    bl.rect(-10, 63, -7, 67, "r2"); bl.rect(-10, 63, -7, 63, "r1"); bl.rect(-10, 67, -7, 67, "r3")
    bl.rect(-9, 64, -8, 65, "y1")

    # strap: cross-body from the far (right) shoulder over the near chest to the near (left) hip bag
    st = p["strap"]
    for i in range(26):
        y = 36 + i
        f = -6 + (11 * i) // 25
        colour = "r1" if i % 5 == 0 else ("r3" if i % 7 == 0 else "r2")
        st.rect(f, y, f + 2, y, colour)
    st.rect(0, 47, 2, 49, "y2"); st.rect(1, 48, 2, 49, "y1")                           # brass adjuster

    # bag: dark-red emergency bag on the character's LEFT (near) hip, brass clasps, handle, rolled bandage
    bg = p["bag"]
    bg.rect(-5, 61, 7, 80, "b2")
    bg.rect(-5, 61, 7, 66, "b1"); bg.rect(-5, 61, 7, 61, "b1"); bg.rect(-5, 66, 7, 66, "b3")
    bg.rect(6, 67, 7, 80, "b3"); bg.rect(-5, 80, 7, 80, "b3"); bg.rect(-4, 81, 6, 81, "b3")
    bg.rect(-2, 63, 0, 65, "y2"); bg.rect(-2, 63, 0, 64, "y1")                         # flap clasps
    bg.rect(3, 63, 5, 65, "y2"); bg.rect(3, 63, 5, 64, "y1")
    bg.rect(-5, 58, -2, 60, "r2"); bg.rect(4, 58, 7, 60, "r2")                         # handle mounts
    bg.rect(-1, 57, 3, 58, "r2"); bg.rect(-1, 57, 3, 57, "r1")                            # handle
    bg.rect(6, 68, 7, 76, "v2"); bg.rect(6, 68, 7, 68, "v1"); bg.rect(6, 69, 7, 69, "v3")
    bg.rect(7, 70, 7, 75, "v3")                                                          # rolled bandage

    # arms: near (left) ivory sleeve with pale cuff, dark glove; near hand rests on the bag
    a = p["arms"]
    a.rows({36: (-3, 0), 37: (-4, 1)}, "w2")
    a.shaded(-4, 38, 1, 53, "w1", "w2", "w3", 2, 1)
    a.rect(-4, 54, 1, 57, "w3"); a.rect(-4, 54, 1, 54, "w2"); a.rect(-4, 57, 1, 57, "w4")    # pale cuff
    a.shaded(-3, 58, 1, 65, "k2", "k1", "k1", 1, 2)                                    # glove
    a.rect(-2, 66, 3, 73, "k1"); a.rect(-2, 66, -1, 68, "k2"); a.rect(2, 71, 3, 72, "k2")
    a.px(4, 68, "k2")                                                                  # thumb on the bag

    # herb: small green sprig at the character's right chest, tips protruding past the near front edge
    hb = p["herb"]
    hb.rect(8, 43, 8, 50, "n2")
    hb.rect(7, 44, 8, 45, "n1"); hb.rect(8, 46, 9, 47, "n1")
    hb.rect(6, 48, 7, 49, "n2"); hb.rect(7, 50, 8, 51, "n2")

    # face: mature profile, one hazel eye, level brow, nose leading left, ear, restrained closed-lip smile
    f = p["face"]
    f.rows({15: (-2, 4), 16: (-4, 5), **{y: (-5, 6) for y in range(17, 21)},
            **{y: (-6, 6) for y in range(21, 24)}, **{y: (-6, 7) for y in range(24, 27)},
            27: (-6, 8), 28: (-6, 7), 29: (-6, 7), 30: (-6, 6), 31: (-5, 5),
            32: (-4, 4), 33: (-3, 3)}, "s2")
    f.rect(7, 17, 8, 28, "s1"); f.rect(-6, 18, -5, 28, "s3")                            # lit front / shaded back
    f.rect(-4, 21, -2, 26, "s3"); f.rect(-3, 22, -2, 25, "s2"); f.px(-3, 23, "s1")      # ear
    f.rect(2, 21, 6, 21, "h3")                                                         # level brow
    f.rect(4, 23, 6, 23, "h4"); f.rect(4, 24, 4, 24, "e1"); f.rect(5, 24, 6, 25, "e2")
    f.px(6, 24, "h4")                                                                  # hazel eye
    f.rect(8, 25, 9, 26, "s2"); f.px(8, 27, "s3")                                      # nose tip / nostril
    f.rect(4, 29, 5, 29, "m1"); f.px(5, 28, "m1")                                      # restrained smile corner
    f.px(0, 27, "s3"); f.rect(2, 31, 6, 31, "s3"); f.rect(3, 32, 5, 32, "s2")          # cheek line / jaw / chin
    f.rect(-3, 33, 2, 37, "s3"); f.rect(-2, 33, 1, 36, "s2")                           # neck under scarf

    # hair: auburn crown with front sheen, side-swept fringe, loose near lock, layered nape
    h = p["hair"]
    h.rows({8: (-2, 2), 9: (-5, 4), 10: (-7, 5), **{y: (-8, 6) for y in range(11, 16)},
            16: (-8, 5), **{y: (-8, -6) for y in range(17, 24)}}, "h2")
    h.rows({9: (1, 3), 10: (2, 4), 11: (3, 5), 12: (3, 5)}, "h1")                      # upper-front sheen
    h.rows({10: (-7, -5), 11: (-8, -6), **{y: (-8, -7) for y in range(12, 18)}}, "h3")  # back plane
    h.rows({16: (4, 6), 17: (5, 6), 18: (6, 7), 19: (6, 7), 20: (6, 7), 21: (6, 7)}, "h2")  # near fringe lock
    h.rows({17: (2, 4), 18: (1, 3), 19: (0, 2)}, "h1")                                 # fringe sheen
    h.rows({22: (-7, -5), 23: (-7, -5), 24: (-6, -4), 25: (-6, -4), 26: (-6, -4)}, "h3")  # layered nape

    # braid: auburn braided coil LOW at the nape, a plaited mass behind/below the ear with alternating bands
    br = p["braid"]
    left = {24: (-7, -5), 25: (-9, -5), 26: (-10, -5), **{y: (-11, -5) for y in range(27, 32)},
            32: (-11, -6), 33: (-10, -6), 34: (-10, -6), 35: (-9, -6), 36: (-9, -6),
            37: (-8, -6), 38: (-8, -6), 39: (-8, -7), 40: (-8, -7)}
    br.rows(left, "h2")
    br.rect(-10, 26, -6, 26, "h1"); br.rect(-10, 30, -6, 30, "h1"); br.rect(-9, 34, -6, 34, "h1")
    br.rect(-10, 28, -6, 28, "h3"); br.rect(-9, 32, -6, 32, "h3"); br.rect(-9, 36, -6, 36, "h3")
    br.rect(-6, 25, -5, 39, "h3"); br.px(-11, 29, "h4"); br.px(-11, 31, "h4")          # braid shadow / gaps

    # scarf: cool grey-white medical scarf wound at the neck, knot at the near front, long tail down the front
    sc = p["scarf"]
    sc.rows({33: (-4, 4), 34: (-5, 6), **{y: (-7, 6) for y in range(35, 40)},
            40: (-6, 6), 41: (-5, 5)}, "f1")
    sc.rect(4, 34, 6, 39, "f2"); sc.rect(5, 35, 6, 38, "f1"); sc.px(6, 36, "f3")      # knot
    sc.rect(-7, 36, -6, 40, "f2"); sc.rect(-5, 38, -4, 40, "f3")                      # wrap folds
    sc.rows({**{y: (-9, -6) for y in range(41, 48)}, **{y: (-10, -7) for y in range(48, 54)},
             54: (-10, -8), 55: (-9, -8)}, "f1")                                       # long tail streaming back
    sc.rect(-9, 41, -8, 54, "f2"); sc.rect(-10, 48, -9, 53, "f3")
    sc.rect(-9, 55, -8, 55, "f3")                                                      # tail fringe


def draw():
    Ls = {n: L() for n in LAYERS}
    draw_west(Ls)
    return M.finish(Ls)


# ------------------------------------------------------------------ package
def artifacts():
    hp = S.load_helper()
    hp.ZIP_DT, hp.LAYERS, hp.PAL = MS.ZIP_DT, LAYERS, PAL
    blobs = draw()
    full = S.compose_layers(blobs)
    png = hp.png_bytes(full)
    pxo = MS.fix_pxo_metadata(hp.make_pxo(blobs, png))           # labels use the rebound direction (west)
    ora = hp.make_ora(blobs, png)
    pal = (json.dumps({"actor_id": ACTOR, "name": f"{ACTOR}-{D}-v01", "colors": PAL}, indent=2) + "\n").encode()
    return hp, blobs, full, png, pxo, ora, pal


def south_unchanged():
    m = json.loads(open(fs(SOUTH_MANIFEST_REL), "rb").read())
    pal = json.loads(open(fs(f"{SOUTH_DIR_REL}/{m['files']['palette']['file']}"), "rb").read())
    files = {v["file"]: sha(open(fs(f"{SOUTH_DIR_REL}/{v['file']}"), "rb").read()) == v["rawsha256"]
             for v in m["files"].values()}
    return {"manifest_sha_matches_pin": sha(open(fs(SOUTH_MANIFEST_REL), "rb").read()) == PINS[SOUTH_MANIFEST_REL],
            "files_match_manifest": all(files.values()), "palette_colors_identical": pal["colors"] == PAL}


def isolated(full):
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
    g["pxo_labels_west"] = b"heya-west" in dj and b"heya-south" not in dj
    g["pxo_no_foreign_metadata"] = all(s not in dj for s in (b"milo", b"jiang", b"lin-que", b"muxiu", b"yanke"))
    g["palette_fits_pxo_grid_40"] = len(PAL) <= 40
    al = full[..., 3]
    g["isolated_texels"] = isolated(full)
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

    # --- west profile direction -------------------------------------------------
    face = blobs["face"]; fm = face[..., 3] == 255
    fy, fx = np.nonzero(fm)
    # nose leads screen LEFT: front-most face texel at rows 24..27, back of head further right at rows 17..21
    nose_rows = fm[24:28].any(axis=0); nose_x = int(np.nonzero(nose_rows)[0].min())
    back_rows = fm[17:22].any(axis=0); back_x = int(np.nonzero(back_rows)[0].max())
    g["profile_west_facing"] = nose_x <= 32 and back_x >= 45 and int(fx.max()) >= 45
    g["profile_west_facing_detail"] = {"nose_x": nose_x, "back_x": back_x}
    g["profile_face_narrow"] = int(fx.max() - fx.min() + 1) <= 20
    g["profile_depth"] = int(np.nonzero(al)[1].max() - np.nonzero(al)[1].min() + 1)
    g["profile_depth_20_34"] = 20 <= g["profile_depth"] <= 34
    # one visible eye: eye-white texels in a small cluster on the front of the face
    eye_white = np.zeros_like(fm)
    for yy in range(22, 27):
        for xx in range(30, 40):
            if fm[yy, xx] and (blobs["face"][yy, xx, :3] == S.rgb("e1")).all():
                eye_white[yy, xx] = True
    g["profile_one_eye"] = 1 <= int(eye_white.sum()) <= 8

    # low braided coil at the nape: behind/below the ear, back half of the head, never a high bun
    bm = blobs["braid"][..., 3] == 255; by, bx = np.nonzero(bm)
    g["coil_low_at_nape_west"] = (int(bm.sum()) >= 80 and by.min() >= 23 and by.max() <= 40
                                  and float(bx.mean()) >= 44.0 and int(bx.max()) >= 49)
    g["coil_detail_west"] = {"texels": int(bm.sum()), "rows": [int(by.min()), int(by.max())],
                             "mean_x": round(float(bx.mean()), 2), "max_x": int(bx.max())}
    hm = blobs["hair"][..., 3] == 255; hy, _ = np.nonzero(hm)
    g["hair_not_high_bun_west"] = int(hy.max()) <= 30 and int(hy.min()) >= 8

    # scarf: wrap at the neck plus a long near-front tail; only cool grey-white colours
    sm = blobs["scarf"][..., 3] == 255; sy, sx = np.nonzero(sm)
    scols = {tuple(c) for c in blobs["scarf"][sm][:, :3]}
    g["scarf_west"] = (int(sm.sum()) >= 160 and int(sy.max()) >= 52 and int(sy.min()) <= 34
                       and scols <= cols(("f1", "f2", "f3")))
    g["scarf_detail_west"] = {"texels": int(sm.sum()), "rows": [int(sy.min()), int(sy.max())]}

    # bag: dark-red mass on the character's LEFT (near) hip, no further back than mid-hip
    gm = blobs["bag"][..., 3] == 255; gy, gx = np.nonzero(gm)
    gcols = {tuple(c) for c in blobs["bag"][gm][:, :3]}
    brass = cols(("y1", "y2"))
    g["bag_left_hip_west"] = (int(gm.sum()) >= 120 and 32.0 <= float(gx.mean()) <= 44.0
                              and bool(gcols & cols(("b1", "b2"))) and sum(tuple(c) in brass for c in gcols) >= 1
                              and int(gy.max() - gy.min() + 1) >= 12)
    g["bag_detail_west"] = {"texels": int(gm.sum()), "mean_x": round(float(gx.mean()), 2),
                            "rows": [int(gy.min()), int(gy.max())]}

    # restrained closed-lip smile: short mouth at the front of the profile, no teeth
    mouth = np.zeros_like(fm)
    for yy in range(27, 32):
        for xx in range(28, 37):
            if fm[yy, xx] and (blobs["face"][yy, xx, :3] == S.rgb("m1")).all():
                mouth[yy, xx] = True
    my, mx = np.nonzero(mouth)
    teeth = any((blobs["face"][yy, xx, :3] == S.rgb("e1")).all()
                for yy in range(28, 31) for xx in range(28, 37) if fm[yy, xx])
    width = int(mx.max() - mx.min() + 1) if len(mx) else 0
    g["restrained_smile_west"] = (3 <= int(mouth.sum()) <= 6 and not teeth and width <= 4)
    g["mouth_detail_west"] = {"texels": int(mouth.sum()), "width": width, "teeth_visible": bool(teeth)}
    g["herb_visible_west"] = int((blobs["herb"][..., 3] == 255).sum()) >= 12
    return g


HARD = M.HARD + ["pxo_labels_west", "pxo_no_foreign_metadata", "palette_fits_pxo_grid_40",
                 "isolated_texels_le_24", "identity_colours_all", "anchor_layers_visible", "face_has_eye",
                 "profile_west_facing", "profile_face_narrow", "profile_depth_20_34", "profile_one_eye",
                 "coil_low_at_nape_west", "hair_not_high_bun_west", "scarf_west", "bag_left_hip_west",
                 "restrained_smile_west", "herb_visible_west"]


def manifest(files, g):
    m = {"actor_id": ACTOR, "content_id": f"content.char.{ACTOR}.static-{D}", "status": "UNAPPROVED",
         "direction": D, "pose": "idle-static", "canvas": [W, H], "pivot": list(PIN), "body_rows": list(BODY_ROWS),
         "display_scale": S.DISPLAY_SCALE, "logical_height_px": (BODY_ROWS[1] - BODY_ROWS[0] + 1) * S.DISPLAY_SCALE,
         "layers": [{"name": n, "visible": n != "guides"} for n in LAYERS],
         "face_layer_role": "mature west profile: one hazel eye, level brow, nose leading screen left, ear, "
                            "restrained closed-lip smile, jaw/chin, neck",
         "braid_layer_role": "auburn braided coil LOW at the nape: one plaited mass behind and below the near ear "
                             "at the back of the head, alternating light/dark bands; never a high bun",
         "view_notes": "west profile (nose to screen left; the character's LEFT side faces the camera): auburn "
                       "hair with front sheen, side-swept fringe and a loose near lock; low braided coil at the "
                       "nape behind the head; cool grey-white medical scarf wound at the neck with the knot at the "
                       "near front and a long tail down the front; ivory open clinician coat with the charcoal "
                       "underdress placket in the front gap, pale grey-white apron with botanical hem motif, slim "
                       "leather belt with brass buckle and back medicine pouch; dark-red emergency bag with brass "
                       "clasps, leather handle and rolled bandage on the character's LEFT (near) hip, hung from a "
                       "leather cross-body strap with a brass adjuster; small green herb sprig at the far right "
                       "chest with tips past the near front edge; near left arm in an ivory sleeve, pale cuff and "
                       "dark glove resting on the bag; far arm occluded; brown leather boots with folded cuff and "
                       "brass eyelet, far boot darker and set slightly ahead",
         "authored_deviations_from_sheet": [
             "West profile re-authors the front-view south design in forward coordinates; it is not a rotation, "
             "squash, recolour or mirror of the south package.",
             "The concept sheet's white head-veil is omitted so the Bible's low auburn braided coil remains "
             "readable; the canonical grey-white medical scarf is worn at the neck with its tail down the front.",
             "The sheet's long dark-red shawl is reduced to the canonical dark-red emergency bag on the "
             "character's left (near) hip; the shawl silhouette is not copied.",
             "In strict west profile the character's right chest is far/occluded; the herb sprig is kept at that "
             "far lapel with only its tips protruding past the near front edge, an explicit readability choice.",
             "The far arm is fully occluded by the torso in profile; the near left hand rests on the bag.",
             "Fine embroidery, bag contents, tassels and multiple belt charms beyond the botanical hem motif, "
             "brass clasps and rolled bandage are omitted for 48 px readability."],
         "files": {k: {"file": fname(*FILE_KEYS[k]), "rawsha256": sha(b)} for k, b in files.items()},
         "colour_count": g["colour_count"], "genuine_visible_role_layers": g["genuine_visible_role_layers"],
         "isolated_texels": g["isolated_texels"], "profile_depth": g["profile_depth"],
         "portrait_ref": {"file": MS.PORTRAIT_REL, "expected_sha256": MS.PORTRAIT_SHA, "approval": "UNAPPROVED",
                          "use": "identity reference only; hues chosen by eye, no pixels sampled"},
         "continuity_ref": {"file": SOUTH_MANIFEST_REL, "rawsha256": PINS[SOUTH_MANIFEST_REL],
                            "use": "Heya south v01 palette/layers/outline/gates and identity wording; no pixels copied"},
         "bible_ref": "character-26 / companion #26 Heya (赫娅), 44-year-old clinician who respects patient "
                      "bodily autonomy; restrained patient smile, auburn braided coil low at the nape, "
                      "grey-white medical scarf, dark-red emergency bag on the character's left",
         "style_contract": "docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md",
         "view_contract": CONTRACT_REL,
         "source_contract": "same as Heya south v01: 80x112, pivot (40,104), body rows 8..103, display scale 0.5 = "
                            "48 logical px, binary alpha, transparent border, declared 24..48 used colours, >=8 "
                            "genuine role layers, hidden guides layer; west profile gates replace the front-view "
                            "coil/scarf/bag/chest gates",
         "replaces_placeholder": "does not modify the old 32x48 native-animation placeholder; it is not counted",
         "author_tool": "tools/" + os.path.basename(__file__), "reused_tool_pins": {**PINS, **MS.PINS},
         "serialization_helper": S.HELPER_REL,
         "pixel_source": "code-authored native pixels, declared palette",
         "limitations": "west static only; no runtime wiring, no south/north/east rewrites, no motion, no GUI "
                        "save/reopen proof and no creator art approval"}
    return (json.dumps(m, indent=2) + "\n").encode()


def check_r2(r1, r2):
    return all(a == b for a, b in zip(r1[3:], r2[3:]))


def write_stage(named):
    written = {}
    for rel, data in named.items():
        p = fs(rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if os.path.exists(p) and open(p, "rb").read() != data:
            raise SystemExit(f"refusing to overwrite different staging file {rel}")
        open(p, "wb").write(data)
        written[rel] = sha(data)
    open(fs(STAGE_REL + "/.gdignore"), "ab").close()
    return written


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    r1, r2 = artifacts(), artifacts()
    g = gates(r1)
    g["deterministic_rebuild"] = check_r2(r1, r2)
    su = south_unchanged()
    bad = [k for k in HARD + ["deterministic_rebuild"] if not g[k]]
    bad += [f"tool_pin:{rel}" for rel, ok in {**PIN_OK, **MS.PIN_OK}.items() if not ok]
    bad += [f"south:{k}" for k, v in su.items() if not v]
    files = dict(zip(("png", "pxo", "ora", "palette"), r1[3:]))
    named = {f"{STAGE_REL}/{fname(*FILE_KEYS[k])}": b for k, b in files.items()}
    named[f"{STAGE_REL}/{fname('manifest', 'json')}"] = manifest(files, g)
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
        written = write_stage(named)
        listing = {"staged": written,
                   "qa_preview_nonsource": {rel: sha(open(fs(rel), "rb").read()) for rel in previews},
                   "hash": "sha256 of raw bytes, no normalization"}
        lp = f"{QA_REL}/{SLUG}_{ACTOR}_{D}-staging-output-paths-rawhashes_unapproved-v01_{STAMP}-{uid('paths')}.json"
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
                                "pin_inside_feet_span", "all_colours_declared", "ora_hidden", "deterministic_rebuild")}
    report.update({k: g[k] for k in ("profile_west_facing", "profile_west_facing_detail", "profile_face_narrow",
                                     "profile_depth", "profile_one_eye", "coil_low_at_nape_west",
                                     "coil_detail_west", "hair_not_high_bun_west", "scarf_west",
                                     "scarf_detail_west", "bag_left_hip_west", "bag_detail_west",
                                     "restrained_smile_west", "mouth_detail_west", "herb_visible_west")})
    report.update(tool_pins_ok={**PIN_OK, **MS.PIN_OK}, south_unchanged=su, disk_matches_rebuild=disk,
                  hard_failures=bad)
    if not g["isolated_texels_le_24"]:
        report["isolated_positions"] = [
            {"x": int(x), "y": int(y)} for y, x in zip(*np.nonzero(r1[2][..., 3] == 255))
            if not any(0 <= y + dy < H and 0 <= x + dx < W and r1[2][y + dy, x + dx, 3] == 255
                       and (r1[2][y + dy, x + dx, :3] == r1[2][y, x, :3]).all()
                       for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    print(json.dumps(report, indent=1))
    stage_ok = all(v is True for k, v in disk.items() if k.startswith("stage:"))
    ok = not bad and stage_ok and all(v is not False for v in disk.values())
    print("HEYA_WEST_V01_" + ("ALL_OK" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
