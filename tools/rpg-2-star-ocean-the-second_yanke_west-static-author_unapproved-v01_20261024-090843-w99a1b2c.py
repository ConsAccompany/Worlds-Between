"""Yanke WEST idle static, native 80x112 source package (UNAPPROVED v01).

content.char.yanke.static-west. Code-authored native pixels in the Sea of Stars direction (broad clusters,
upper-left light), 48 logical px at display scale 0.5. West = nose toward screen LEFT, so the character's LEFT
side faces the camera. Reauthored in forward coordinates with the Lin Que `P` pen (s = -1); it is not a
rotation, squash, recolour or mirror of south.

Identity anchors (Bible character-07, 37-year-old friendly heavy-tool craftsperson; concept sheet is an
UNAPPROVED identity reference, no pixels sampled): short curly dark-brown hair, thick beard, warm broad face with
a cheerful direct smile; broad leather shoulder straps over a cream rolled-sleeve work shirt and olive-green work
apron; brass harness buckles and belt buckle; dark-brown baggy work trousers with olive knee patches; heavy brown
leather boots; red work rag at the character's right hip; notched heavy steel tool head on a wooden handle slung
over the character's right shoulder. In west the right shoulder/hip are the far side: the steel head and notch read
above/behind the upper back at screen right, the handle end emerges over the near left shoulder at screen front,
and the red rag peeks behind the far hip.

Reuses the hash-pinned Yanke south v01 author in memory (and through it Lin Que v01 `P`/finish/gates, Jiang v01
gates and the male v8pair PNG/PXO/ORA serializers) with the same palette, layers, outline colours and HARD gates.
Only the direction label is rebound in memory; the south tool and committed south package stay byte-identical,
which this author verifies against the pinned south manifest and PNG.

  python -X utf8 -I <this> preview # content-named preview only (outputs/yanke-w99/author), no source files
  python -X utf8 -I <this> build   # writes the package into the fresh stage dir only (refuses different bytes)
  python -X utf8 -I <this> check   # rebuilds twice in memory and compares with files in the game tree
"""
import hashlib, importlib.util, io, json, os, sys, zipfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG, ACTOR, D = "rpg-2-star-ocean-the-second", "yanke", "west"
STAMP, RUN_ID = "20261024-090843", "w99a1b2c"
OUT_REL = "game/assets/characters/yanke-native-v01/west"
STAGE_REL = "outputs/yanke-w99/stage-r2"
QA_REL = "outputs/yanke-w99/author"
SOUTH_TOOL_REL = "tools/rpg-2-star-ocean-the-second_yanke_south-static-author_unapproved-v01_20261024-084428-b93c1a4e.py"
SOUTH_DIR_REL = "game/assets/characters/yanke-native-v01/south"
SOUTH_MANIFEST_REL = SOUTH_DIR_REL + "/rpg-2-star-ocean-the-second_yanke_south-manifest_unapproved-v01_20261024-084428-4305a59b.json"
SOUTH_PNG_REL = SOUTH_DIR_REL + "/rpg-2-star-ocean-the-second_yanke_south-static_unapproved-v01_20261024-084428-73949161.png"
PINS = {SOUTH_TOOL_REL: "cdc21721e7423a4df6696273be4271f0a564edfe7d91cd2b2beb13955459fd1c",
        SOUTH_MANIFEST_REL: "e57f5c93131daffff56bc75a47d9a2c1357f4c337797ea0d07c0c73918692e7e",
        SOUTH_PNG_REL: "4f6bcf937390e300e2829ac052bcb1047fdb6387de41561490c757246a32fef0"}
START_METERS = {"production_pct": 62.1, "content_done": 694, "content_total": 1881,
                "inspection_pct": 21.6, "creator_approval_pct": 7.8}


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
_spec = importlib.util.spec_from_file_location("yanke_south_v01_for_west", fs(SOUTH_TOOL_REL))
MS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MS)                                   # pins Lin/Jiang/male tools itself (MS.PIN_OK)
MS.D = D                                                      # rebind the direction label in memory only
M, S = MS.M, MS.S
PAL, LAYERS, FILE_KEYS = MS.PAL, MS.LAYERS, MS.FILE_KEYS
W, H, PIN, BODY_ROWS, L = MS.W, MS.H, MS.PIN, MS.BODY_ROWS, MS.L


# ------------------------------------------------------------------ west (profile, nose to screen left)
def draw_west(Ls):
    """Forward coordinates: f > 0 is the facing direction (screen x = 40 - f). Light stays upper-left on screen,
    so P.shaded puts the highlight on the front (screen-left) edge. Silhouette steps are >= 2 px."""
    p = {n: M.P(Ls[n], -1) for n in LAYERS}

    # ------------------------------------------------------------------ tool: steel head over the FAR (right) shoulder
    hm = p["hammer"]
    hm.rect(-24, 9, -13, 28, "k2")                                    # head block, above/behind the back of the skull
    hm.rect(-15, 10, -13, 28, "k1")                                   # lit front/left plane
    hm.rect(-24, 9, -22, 28, "k3")                                    # back shadow plane
    hm.rect(-24, 9, -13, 9, "k1"); hm.rect(-24, 28, -13, 28, "k3")    # top light, lower shadow
    for y in range(21, 25):                                            # square notch in the striking face
        a, b = hm.span(-24, -21)
        hm.l.a[y, a:b + 1] = 0
    hm.rect(-21, 11, -17, 12, "k1")                                    # worn steel face band
    hm.rect(-20, 17, -16, 18, "k1")
    for i in range(13):                                                # handle leaves the head down/forward
        f = -17 + i
        y = 29 + i // 2
        hm.rect(f, y, f + 1, y + 1, "w2")
        hm.rect(f, y, f, y, "w1"); hm.rect(f + 1, y, f + 1, y, "w3")
    hm.rect(-18, 28, -14, 30, "w2"); hm.rect(-18, 28, -14, 28, "w1")
    hm.rect(-13, 31, -9, 32, "w2"); hm.rect(-13, 31, -9, 31, "w1")    # handle crosses behind the shoulder

    # ------------------------------------------------------------------ boots: far darker/ahead, near in front
    b = p["boots"]
    b.shaded(-1, 91, 9, 101, "r2", "r2", "r3", 1, 1)                   # far boot, set slightly ahead
    b.rect(10, 97, 10, 101, "r2")
    b.rect(-1, 102, 10, 102, "r3")
    b.shaded(-7, 90, 6, 101, "r1", "r2", "r3", 2, 2)                   # near boot
    b.rect(-7, 90, 6, 91, "r2"); b.rect(-7, 90, 6, 90, "r1")           # folded cuff
    b.rect(-7, 92, 6, 92, "r3")
    b.rect(-7, 95, 6, 95, "r3"); b.rect(-7, 96, 6, 96, "r3")           # buckle strap
    b.rect(-1, 94, 2, 97, "y2"); b.rect(-1, 95, 2, 95, "y1")
    b.shaded(5, 97, 8, 101, "r1", "r1", "r2", 1, 1)                    # near toe
    b.rect(-8, 99, -8, 102, "r3")                                      # heel
    b.rect(-8, 102, 6, 102, "r3")
    b.rect(-8, 103, 10, 103, "r4")                                     # thick sole

    # ------------------------------------------------------------------ trousers: baggy dark brown, olive near knee patch
    t = p["trousers"]
    t.rect(-12, 66, 7, 72, "t2")                                       # seat
    t.shaded(-12, 72, -4, 90, "t2", "t2", "t3", 1, 2)                  # far leg, darker
    t.shaded(-4, 72, 7, 89, "t1", "t2", "t3", 2, 2)                    # near leg
    t.rect(-12, 72, -11, 89, "t3")
    t.rect(-2, 77, 4, 84, "a2"); t.rect(-2, 77, 4, 77, "a1")           # knee patch
    t.rect(-2, 84, 4, 84, "a3"); t.rect(-2, 78, -2, 80, "a3")
    t.rect(-4, 89, 6, 89, "t3"); t.rect(-4, 90, 6, 90, "t4")           # cuffs
    t.rect(-12, 89, -5, 89, "t3"); t.rect(-12, 90, -5, 90, "t4")

    # ------------------------------------------------------------------ shirt: cream, collar and near sleeve base
    sh = p["shirt"]
    sh.rows({33: (-1, 6), 34: (-1, 7), 35: (-2, 8), 36: (-2, 8)}, "c2")
    sh.rect(-1, 33, 6, 33, "c1")
    sh.rows({**{y: (-12, 9) for y in range(37, 62)}, 62: (-11, 8)}, "c2")
    sh.rect(7, 37, 9, 61, "c1"); sh.rect(-12, 37, -10, 61, "c3")       # lit front / shaded back
    sh.rect(-3, 62, 8, 64, "c2")
    sh.rect(-11, 36, 9, 36, "c3")                                      # shoulder seam

    # ------------------------------------------------------------------ apron: bib + skirt, pocket, worn hem
    ap = p["apron"]
    rows = {37: (-6, 5), 38: (-6, 6), 39: (-7, 6), **{y: (-7, 7) for y in range(40, 50)},
            **{y: (-8, 8) for y in range(50, 55)}, 55: (-10, 8),
            **{y: (-11, 9) for y in range(56, 70)}, 70: (-11, 8), 71: (-10, 8),
            72: (-10, 7), 73: (-9, 6), 74: (-7, 4)}
    ap.rows(rows, "a2")
    for y, (back, front) in rows.items():                              # front light / back shadow
        ap.rect(front - 1, y, front, y, "a1"); ap.rect(back, y, back + 1, y, "a3")
    ap.rect(-1, 56, 3, 63, "a3"); ap.rect(-1, 56, 3, 56, "a2"); ap.rect(-1, 56, -1, 63, "a4")  # stitched pocket
    ap.rect(-8, 73, 5, 73, "a3"); ap.rect(-7, 74, 3, 74, "a4")         # uneven worn hem

    # ------------------------------------------------------------------ harness: broad near-shoulder strap + brass buckle
    hr = p["harness"]
    hr.rect(-3, 34, 4, 38, "r2"); hr.rect(-3, 34, 4, 34, "r1")         # shoulder pad
    hr.rect(2, 39, 5, 63, "r2"); hr.rect(2, 39, 2, 63, "r1"); hr.rect(5, 39, 5, 63, "r3")   # front branch
    hr.rect(-10, 37, -7, 63, "r2"); hr.rect(-10, 37, -10, 63, "r1"); hr.rect(-7, 37, -7, 63, "r3")  # back branch
    hr.rect(-4, 35, 5, 38, "r1"); hr.rect(-4, 35, 5, 35, "r1")
    hr.rect(2, 43, 5, 47, "y2"); hr.rect(3, 44, 4, 46, "r3"); hr.rect(3, 44, 4, 44, "y1")      # brass buckle
    hr.rect(-12, 35, -11, 45, "r3")                                    # far strap edge peeks behind

    # ------------------------------------------------------------------ grip: far handle end over the near shoulder
    gr = p["grip"]
    gr.rect(8, 33, 11, 36, "w2"); gr.rect(8, 33, 11, 33, "w1"); gr.rect(8, 36, 11, 36, "w3")
    gr.rect(9, 37, 11, 37, "w2"); gr.rect(9, 37, 11, 37, "w3")
    gr.rect(8, 34, 9, 37, "r2"); gr.rect(8, 35, 9, 35, "r1")           # leather grip wrap
    gr.rect(11, 33, 12, 35, "y2"); gr.rect(11, 33, 12, 33, "y1")       # brass ferrule

    # ------------------------------------------------------------------ belt: broad leather, brass buckle, red rag far hip
    bl = p["belt"]
    bl.rect(-12, 63, 8, 67, "r2"); bl.rect(-12, 63, 8, 63, "r1"); bl.rect(-12, 67, 8, 67, "r3")
    bl.rect(3, 63, 7, 67, "y2"); bl.rect(4, 64, 6, 66, "r3"); bl.rect(4, 64, 6, 64, "y1")
    bl.rect(-2, 65, -2, 65, "r4"); bl.rect(-6, 65, -6, 65, "r4")
    bl.rows({**{y: (-15, -11) for y in range(64, 69)}, **{y: (-15, -12) for y in range(69, 72)},
             72: (-14, -12)}, "f1")
    bl.rect(-15, 64, -15, 71, "f2"); bl.rect(-14, 72, -12, 72, "f2")

    # ------------------------------------------------------------------ near (left) arm: rolled sleeve, bracer, fist
    a = p["arms"]
    a.rows({37: (1, 9), 38: (2, 11), **{y: (2, 12) for y in range(39, 48)}}, "c2")
    a.rect(2, 39, 3, 47, "c1"); a.rect(11, 39, 12, 47, "c3")
    a.rect(2, 48, 12, 50, "c3"); a.rect(2, 48, 12, 48, "c2"); a.rect(2, 50, 12, 50, "c4")
    a.shaded(3, 51, 11, 63, "s1", "s2", "s3", 2, 2)
    a.rect(3, 64, 11, 68, "r2"); a.rect(3, 64, 11, 64, "r1"); a.rect(3, 66, 11, 66, "r4"); a.rect(3, 68, 11, 68, "r3")
    a.shaded(3, 69, 11, 75, "s2", "s2", "s3", 1, 2)
    a.rect(4, 71, 10, 71, "s3"); a.rect(12, 72, 12, 73, "s2")

    # ------------------------------------------------------------------ face: strict profile, one eye, big nose, smile
    fc = p["face"]
    fc.rows({14: (-8, 4), 15: (-9, 5), 16: (-9, 6), **{y: (-10, 7) for y in range(17, 22)},
             22: (-10, 8), 23: (-10, 9), 24: (-10, 9), 25: (-10, 9), 26: (-10, 9), 27: (-9, 9),
             28: (-9, 8), 29: (-9, 8), 30: (-8, 8), 31: (-8, 7), 32: (-7, 6), 33: (-7, 5),
             34: (-6, 4), 35: (-5, 4), 36: (-4, 3)}, "s2")
    fc.rect(5, 16, 7, 27, "s1")                                        # lit front plane
    fc.rect(-10, 17, -9, 32, "s3")                                     # shaded back
    fc.rect(9, 24, 10, 27, "s2"); fc.rect(11, 26, 11, 27, "s2"); fc.rect(12, 27, 12, 27, "s3")
    fc.rect(10, 28, 11, 28, "s3")                                      # nose and nostril
    fc.rect(2, 22, 7, 22, "h2"); fc.rect(2, 23, 7, 23, "h3")           # thick brow
    fc.rect(3, 24, 6, 25, "e1"); fc.rect(4, 24, 6, 25, "e2"); fc.rect(4, 24, 5, 24, "h4")  # one eye
    fc.rect(4, 27, 6, 28, "s1")                                        # cheek plane
    fc.rect(6, 30, 9, 30, "m1"); fc.rect(7, 30, 8, 30, "e1"); fc.rect(6, 31, 9, 31, "m1")  # open smile + teeth
    fc.rect(5, 29, 5, 29, "m1")
    fc.rect(-7, 23, -5, 28, "s2"); fc.rect(-6, 24, -6, 27, "s3"); fc.rect(-7, 24, -7, 24, "s1")  # ear
    fc.rect(-3, 33, 3, 36, "s3"); fc.rect(-2, 33, 2, 35, "s2")         # neck

    # ------------------------------------------------------------------ hair: short dark-brown curls, back volume
    h = p["hair"]
    h.rows({8: (-8, 2), 9: (-11, 4), 10: (-13, 6), **{y: (-14, 7) for y in range(11, 14)}}, "h2")
    h.rows({14: (-14, 6), 15: (-14, 5), 16: (-14, 4), 17: (-14, 3), 18: (-14, 2), 19: (-14, 1),
            20: (-14, 0), 21: (-14, -1), **{y: (-14, -2) for y in range(22, 28)},
            28: (-13, -3), 29: (-12, -4)}, "h2")
    h.rows({14: (4, 8), 15: (4, 8), 16: (5, 8), 17: (5, 7), 18: (5, 7), 19: (6, 7)}, "h2")  # fringe
    h.rect(-15, 12, -14, 16, "h3"); h.rect(-15, 20, -14, 24, "h3")     # back curl lumps
    h.rect(-13, 8, -11, 9, "h2"); h.rect(-10, 8, -9, 9, "h2")          # crown curls
    h.rows({9: (-4, 0), 10: (-2, 3), 11: (0, 4), 12: (1, 5)}, "h1")    # upper-front sheen
    h.rect(-14, 15, -13, 26, "h3")                                     # dark back plane
    h.rect(-12, 10, -11, 12, "h1")

    # ------------------------------------------------------------------ beard: thick short beard, moustache, sideburn
    bd = p["beard"]
    bd.rows({21: (-9, -6), 22: (-10, -5), 23: (-10, -5), 24: (-10, -5), 25: (-10, -4),
             26: (-10, -4)}, "h2")
    bd.rows({27: (-9, 2), 28: (-9, 4), 29: (-9, 5), 30: (-9, 5), 31: (-9, 5), 32: (-8, 7),
             33: (-7, 7), 34: (-7, 6), 35: (-6, 6), 36: (-5, 6), 37: (-4, 5), 38: (-3, 4)}, "h2")
    bd.rows({28: (5, 9), 29: (6, 9)}, "h2")                            # moustache, mouth stays clear
    bd.rows({32: (0, 6), 33: (1, 6), 34: (1, 5), 35: (2, 5), 36: (2, 4), 37: (3, 5),
             38: (3, 5), 39: (4, 5)}, "h2")                            # chin beard and front tuft
    bd.rows({27: (-7, -3), 28: (-7, -4), 29: (-6, -3)}, "h1")          # lit front curls
    bd.rows({33: (-6, -3), 34: (-6, -3), 35: (-5, -3)}, "h3")          # shadow under the jaw
    bd.rect(4, 33, 5, 34, "h3")

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
    return {"files_match_manifest": all(files.values()), "palette_colors_identical": pal["colors"] == PAL,
            "png_matches_pin": sha(open(fs(SOUTH_PNG_REL), "rb").read()) == PINS[SOUTH_PNG_REL]}


def south_alpha():
    from PIL import Image
    import numpy as np
    return np.array(Image.open(fs(SOUTH_PNG_REL)).convert("RGBA"))[:, :, 3] > 0


def gates(r):
    g = MS.gates(r)
    from PIL import Image
    import numpy as np
    full = r[2]
    al = full[..., 3] > 0
    with zipfile.ZipFile(io.BytesIO(r[4])) as z:
        dj = z.read("data.json")
    g["pxo_labels_west"] = b"yanke-west" in dj and b"yanke-south" not in dj
    # Profile depth replaces the frontal-spread gate (declared in the view contract).
    chest = al[38:46]
    cols = np.nonzero(chest.any(axis=0))[0]
    g["profile_depth"] = int(cols.max() - cols.min() + 1) if len(cols) else 0
    g["stocky_profile_depth_ge_20"] = g["profile_depth"] >= 20
    sa = south_alpha()
    west_sil = al
    g["west_vs_south_alpha_diff"] = int(np.count_nonzero(west_sil != sa))
    g["west_vs_mirrored_south_alpha_diff"] = int(np.count_nonzero(west_sil != sa[:, ::-1]))
    g["west_not_south_or_mirror"] = (g["west_vs_south_alpha_diff"] >= 400
                                     and g["west_vs_mirrored_south_alpha_diff"] >= 400)
    # one eye in the profile face layer: the e1/e2 eye pixels form one contiguous column span
    face = r[1]["face"]; fm = face[..., 3] > 0
    eye = {S.rgb("e1"), S.rgb("e2")}
    cols = sorted({int(x) for y, x in zip(*np.nonzero(fm)) if tuple(face[y, x, :3]) in eye})
    spans = 0
    prev = None
    for x in cols:
        if prev is None or x > prev + 1:
            spans += 1
        prev = x
    g["profile_eye_column_spans"] = spans
    g["profile_one_eye"] = spans == 1
    return g


HARD = [k for k in MS.HARD if k != "stocky_shoulders_ge_34"] + [
    "stocky_profile_depth_ge_20", "pxo_labels_west", "west_not_south_or_mirror", "profile_one_eye"]


def manifest(files, g):
    m = {"actor_id": ACTOR, "content_id": f"content.char.{ACTOR}.static-{D}", "status": "UNAPPROVED",
         "direction": D, "pose": "idle-static", "canvas": [W, H], "pivot": list(PIN), "body_rows": list(BODY_ROWS),
         "display_scale": S.DISPLAY_SCALE, "logical_height_px": (BODY_ROWS[1] - BODY_ROWS[0] + 1) * S.DISPLAY_SCALE,
         "layers": [{"name": n, "visible": n != "guides"} for n in LAYERS],
         "face_layer_role": "strict profile face, one brown eye, thick brow, nose leading screen left, ear, "
                            "cheerful open smile with teeth, neck",
         "beard_layer_role": "thick short beard, moustache and sideburn wrapping the jaw; mouth kept clear for the "
                             "smile",
         "view_notes": "west profile (nose to screen left; the character's LEFT side faces the camera): short curly "
                       "dark-brown hair with upper-front sheen and full curl volume at the back of the skull; thick "
                       "beard, moustache and sideburn; cream rolled-sleeve work shirt at the collar and near sleeve; "
                       "olive-green work apron with bib, skirt, stitched pocket on the near/front face and uneven "
                       "worn hem; broad leather shoulder strap over the near (left) shoulder with front and back "
                       "branches and a brass buckle, far strap edge peeking behind; broad leather belt with front "
                       "brass buckle; red work rag at the character's RIGHT (far) hip peeking behind at the back hip; "
                       "dark-brown baggy work trousers, near leg in front, far leg darker and set slightly ahead, "
                       "olive knee patch on the near knee; heavy brown leather boots with cuff, brass buckle, broad "
                       "toe and thick sole; notched heavy steel tool head on a wooden handle slung over the "
                       "character's RIGHT (far) shoulder, steel head and notch above/behind the upper back at screen "
                       "right, far handle end emerging over the near (left) shoulder at screen front (screen left)",
         "authored_deviations_from_sheet": [
             "pose: neutral west profile idle with the near arm down; the sheet's 3/4 pose carries the hammer across "
             "both shoulders.",
             "hammer: the far-shoulder head and the near-shoulder handle end are kept as the profile-readable part "
             "of the across-back carry; the full across-shoulder pose is not copied.",
             "small belt tools, pouch and cloth tatters beyond the one red rag are omitted for 48 px readability."],
         "files": {k: {"file": fname(*FILE_KEYS[k]), "rawsha256": sha(b)} for k, b in files.items()},
         "colour_count": g["colour_count"], "genuine_visible_role_layers": g["genuine_visible_role_layers"],
         "isolated_texels": g["isolated_texels"], "profile_depth": g["profile_depth"],
         "west_vs_south_alpha_diff": g["west_vs_south_alpha_diff"],
         "west_vs_mirrored_south_alpha_diff": g["west_vs_mirrored_south_alpha_diff"],
         "portrait_ref": {"file": MS.PORTRAIT_REL, "expected_sha256": MS.PORTRAIT_SHA, "approval": "UNAPPROVED",
                          "use": "identity reference only; no pixels sampled"},
         "continuity_ref": {"file": SOUTH_MANIFEST_REL, "rawsha256": PINS[SOUTH_MANIFEST_REL],
                            "use": "Yanke south v01 palette/layers/outline/gates; no pixels copied"},
         "bible_ref": "character-07: 37yo friendly heavy-tool craftsperson; broad leather shoulder straps, "
                      "dark-brown work trousers, notched heavy tool head, sturdy build, cheerful direct; "
                      "identity/hair anchor short curls and thick beard",
         "style_contract": "docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md",
         "view_contract": "outputs/yanke-w99/rpg-2-star-ocean-the-second_yanke_west-style-source-contract_unapproved-v01_20261024-090843-w99a1b2c.md",
         "source_contract": "same as Yanke south v01: 80x112, pivot (40,104), body rows 8..103, display scale 0.5 = "
                            "48 logical px, binary alpha, transparent border, same declared palette, 24..48 used "
                            "colours, >=8 genuine role layers, hidden guides layer; frontal stocky-shoulder gate "
                            "replaced by profile depth >=20 (declared)",
         "replaces_placeholder": "does not modify the old 32x48 native-animation placeholder; it is not counted",
         "author_tool": "tools/" + os.path.basename(__file__),
         "author_revision": "r2 (steel head enlarged to meet the >=120 steel-mass gate; same filenames)",
         "reused_tool_pins": {**PINS, **MS.PINS},
         "serialization_helper": S.HELPER_REL,
         "task_start_meters": START_METERS,
         "base_revision": "234cfabeacd48a9ebc80b2608af448feb535af69",
         "pixel_source": "code-authored native pixels, declared palette",
         "limitations": "west static only; no runtime wiring, no east/north/south changes, no motion, no creator art "
                        "approval"}
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
    su = south_unchanged()
    bad = [k for k in HARD + ["deterministic_rebuild"] if not g[k]]
    bad += [f"tool_pin:{rel}" for rel, ok in {**PIN_OK, **MS.PIN_OK}.items() if not ok]
    bad += [f"south:{k}" for k, v in su.items() if not v]
    files = dict(zip(("png", "pxo", "ora", "palette"), r1[3:]))
    names = {fname(*FILE_KEYS[k]): b for k, b in files.items()}
    names[fname("manifest", "json")] = manifest(files, g)
    named = {f"{OUT_REL}/{n}": b for n, b in names.items()}
    if cmd in ("build", "stage", "preview"):                    # content-named preview: never reuses a name
        from PIL import Image
        buf = io.BytesIO()
        Image.fromarray(r1[2], "RGBA").resize((W * 6, H * 6), Image.NEAREST).save(buf, "PNG")
        prev = f"{QA_REL}/{SLUG}_{ACTOR}_{D}-preview-x6_unapproved-v01_{STAMP}-{sha(r1[3])[:8]}.png"
        write_new(prev, buf.getvalue())
        print("preview:", prev, sha(buf.getvalue()))
    if cmd in ("build", "stage"):                               # game tree untouched; install via wb_safe_replace
        if bad:
            raise SystemExit(f"hard gates failed: {bad}")
        for n, data in names.items():
            write_new(f"{STAGE_REL}/{n}", data)
        write_new(f"{STAGE_REL}/.gdignore", b"")
        listing = {"staged": {f"{STAGE_REL}/{n}": sha(b) for n, b in sorted(names.items())},
                   "gdignore": sha(b""),
                   "install_to": OUT_REL, "qa_preview_nonsource": {prev: sha(open(fs(prev), "rb").read())},
                   "hash": "sha256 of raw bytes"}
        listing_bytes = (json.dumps(listing, indent=2) + "\n").encode()
        write_new(f"{QA_REL}/{SLUG}_{ACTOR}_{D}-output-paths-rawhashes_unapproved-v01_{STAMP}-"
                  f"{uid('paths', sha(listing_bytes))}.json", listing_bytes)
    disk = {rel: (sha(open(fs(rel), "rb").read()) == sha(b)) if os.path.exists(fs(rel)) else None
            for rel, b in named.items()}
    report = {k: g[k] for k in ("body_rows", "colour_count", "genuine_visible_role_layers", "visible_role_texels",
                                "isolated_texels", "silhouette_width", "profile_depth",
                                "west_vs_south_alpha_diff", "west_vs_mirrored_south_alpha_diff",
                                "profile_one_eye", "identity_colours_visible", "binary_alpha", "no_opaque_border",
                                "pin_inside_feet_span", "all_colours_declared", "ora_hidden", "face_has_eye",
                                "deterministic_rebuild")}
    staged = {f"{STAGE_REL}/{n}": (sha(open(fs(f'{STAGE_REL}/{n}'), "rb").read()) == sha(b))
              if os.path.exists(fs(f"{STAGE_REL}/{n}")) else None for n, b in names.items()}
    staged[f"{STAGE_REL}/.gdignore"] = os.path.exists(fs(f"{STAGE_REL}/.gdignore"))
    report.update(tool_pins_ok={**PIN_OK, **MS.PIN_OK}, south_unchanged=su, disk_matches_rebuild=disk,
                  hard_failures=bad)
    if cmd in ("build", "stage"):
        report["stage_matches_rebuild"] = staged
    print(json.dumps(report, indent=1))
    ok = not bad and (all(v is True for v in staged.values()) if cmd in ("build", "stage")
                      else all(v is True for v in disk.values()))
    print("YANKE_WEST_V01_" + ("ALL_OK" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
