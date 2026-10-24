"""Muxiu NORTH idle static, native 80x112 source package (UNAPPROVED v01, author revision r2).

content.char.muxiu.static-north. Code-authored native pixels in the Sea of Stars direction (broad clusters,
upper-left light), 48 logical px at display scale 0.5. North = back view: the character's RIGHT side is on screen
RIGHT. Newly drawn in screen coordinates; it is not a rotation, squash, recolour or mirror of south or west.

Revision history (earlier tool files are retained byte-identical, never edited):
- draft tools/...muxiu_north-static-author_unapproved-v01_20261024-080000-4e7d2c19.py: preview rc1, hard failures
  all_role_layers_nonempty (whistle layer empty) and isolated_texels_le_24 (28). Never built source files.
- r1 tools/...muxiu_north-static-author_unapproved-v01r1_20261024-080000-4e7d2c19.py: preview rc1, only hard
  failure isolated_texels_le_24 (25; coords at nape locks and plait stairs). Never built source files. r1 added: the whistle layer carries only the tan cord loop crossing the back of the neck over the hood rim
  (the whistle itself stays at the front, no wood colours drawn); braid plait and hood taper use 2 px stair steps,
  no per-row single-pixel braid highlights; isolated texel coordinates printed in the report.
- r2 (this file): nape locks drop their single-row tips; the plait steps 3 px every 2 rows with its colour
  bands aligned to the steps. Same gates and thresholds.

Identity (Bible character-06 via the Muxiu south v01 manifest; unapproved character sheet as identity reference
only, no pixels sampled): messy wavy dark-brown hair covering the back of the head with stick-out wave locks; the
long braid is gathered in a knot at the nape and runs over the character's RIGHT shoulder (screen right) to the
front, so from behind it shows as the nape knot plus the plait crossing the shoulder; moss-green short hooded
capelet with the hood lying on the upper back, cream tree motif band and a larger cream tree on the back, fringed
hem; cream shirt below the hem; knotted green/tan rope bracelet on the character's LEFT wrist (screen left);
brown belt back with the larger pouch on the character's right hip (screen right); olive-brown trousers with a
seat seam (knee patches are front-only); green leg wraps with cream band and tan cords; brown boots with heels.

Reuses the hash-pinned Muxiu south v01 author in memory (and through it Lin Que v01 pens/finish/gates, Jiang v01
gates and the male v8pair PNG/PXO/ORA serializers) with the same palette, layers, outline colours and HARD gates,
with two direction swaps (documented in the manifest, no threshold changed):
- south `face_has_eye` -> the reused Lin author's own `north_face_no_eyes_or_mouth` (as Milo north v01 did);
- south `anchor_layers_visible` (cloak, braid, bracelet, whistle, hair, face >= 12 texels) ->
  `anchor_layers_visible_north`: same 12-texel threshold on cloak, braid, bracelet, hair, face, plus
  `whistle_body_not_drawn_through_back` (no whistle-wood x1/x2 texels; the cord loop alone is visible).

  python -X utf8 -I <this> preview # content-named preview only (outputs/muxiu-n01/author), no source files
  python -X utf8 -I <this> stage   # writes the package into the fresh stage dir only (refuses different bytes)
  python -X utf8 -I <this> install # copies staged bytes into the (new) game-tree north dir; refuses different bytes
  python -X utf8 -I <this> check   # rebuilds twice in memory and compares with files in the game tree
"""
import hashlib, importlib.util, io, json, os, sys, zipfile
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG, ACTOR, D = "rpg-2-star-ocean-the-second", "muxiu", "north"
STAMP, RUN_ID = "20261024-080000", "4e7d2c19"
OUT_REL = "game/assets/characters/muxiu-native-v01/north"
STAGE_REL = "outputs/muxiu-n01/stage-r2"
QA_REL = "outputs/muxiu-n01/author"
SOUTH_TOOL_REL = "tools/rpg-2-star-ocean-the-second_muxiu_south-static-author_unapproved-v01_20261024-071500-6d3e9a51.py"
SOUTH_DIR_REL = "game/assets/characters/muxiu-native-v01/south"
SOUTH_MANIFEST_REL = SOUTH_DIR_REL + "/rpg-2-star-ocean-the-second_muxiu_south-manifest_unapproved-v01_20261024-071500-dd478113.json"
WEST_MANIFEST_REL = ("game/assets/characters/muxiu-native-v01/west/"
                     "rpg-2-star-ocean-the-second_muxiu_west-manifest_unapproved-v01_20261024-055724-a2f2ac0f.json")
PINS = {SOUTH_TOOL_REL: "f329ac7aa595f003ba741ed8de6cf5aade1d912acfa65a1720ce731eb24737f1",   # committed f556e74e
        SOUTH_MANIFEST_REL: "24c751575fe02a4857628dbfb8b379cd1d42344167062ae8ddbb033024e114de",
        WEST_MANIFEST_REL: "c92fb90c2f6a54b778856329f1c60b6db269070244e38c897bee5f7a13dc4772"}  # committed 322f88f3


def fs(rel):
    return os.path.join(REPO, *rel.split("/"))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def uid(*parts):
    return sha(":".join((RUN_ID,) + parts).encode())[:8]


def fname(purpose, ext):
    return f"{SLUG}_{ACTOR}_{D}-{purpose}_unapproved-v01_{STAMP}-{uid(D, purpose, ext)}.{ext}"


PIN_OK = {rel: sha(open(fs(rel), "rb").read()) == want for rel, want in PINS.items()}
_spec = importlib.util.spec_from_file_location("muxiu_south_v01_for_north", fs(SOUTH_TOOL_REL))
MS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MS)                                   # pins Lin/Jiang/male/Milo tools itself (MS.PIN_OK)
MS.D = D                                                      # rebind the direction label in memory only
M, S = MS.M, MS.S
PAL, LAYERS, FILE_KEYS = MS.PAL, MS.LAYERS, MS.FILE_KEYS
W, H, PIN, BODY_ROWS, L = MS.W, MS.H, MS.PIN, MS.BODY_ROWS, MS.L


# ------------------------------------------------------------------ north (back view)
def draw_north(Ls):
    """Screen coordinates. Character's right = screen right. Light stays upper-left on screen.
    Silhouette steps are >= 2 px (1 px stairs leave isolated outline texels)."""
    # boots: backs of the boots, folded cuff, raised heel counter, heels
    b = Ls["boots"]
    for x0, x1 in ((29, 39), (41, 51)):
        b.shaded(x0 + 1, 92, x1 - 1, 101, "r1", "r2", "r3", 2, 2)
        b.rect(x0 + 1, 92, x1 - 1, 93, "r2"); b.hline(x0 + 1, x1 - 1, 92, "r1")   # cuff
        b.rect(x0 + 3, 96, x1 - 3, 100, "r1"); b.hline(x0 + 3, x1 - 3, 100, "r3")  # heel counter
        b.hline(x0 + 1, x1 - 1, 102, "r3"); b.hline(x0 + 1, x1 - 1, 103, "k1")     # heel block

    # leg wraps: green cloth, cream top band, tan cord bands with the knots tied at the back
    lw = Ls["legwraps"]
    for x0, x1 in ((30, 38), (42, 50)):
        lw.shaded(x0, 82, x1, 91, "c2", "c2", "c3", 2, 2)
        lw.hline(x0, x1, 82, "w2"); lw.hline(x0, x1, 83, "w3")
        lw.hline(x0, x1, 85, "q2"); lw.hline(x0, x1, 88, "q2")
        lw.rect(x0 + 3, 85, x0 + 5, 87, "q1")                                        # back knot

    # trousers: olive-brown seat and legs, centre seam, back-knee fold (no knee patches from behind)
    t = Ls["trousers"]
    t.rect(31, 64, 49, 70, "t2")
    t.shaded(29, 70, 39, 83, "t1", "t2", "t3", 2, 2)
    t.shaded(41, 70, 51, 83, "t1", "t2", "t3", 2, 2)
    t.vline(40, 64, 83, "t4")
    t.rect(32, 66, 38, 67, "t3"); t.rect(42, 66, 48, 67, "t3")                     # seat fold
    t.rect(32, 77, 37, 77, "t3"); t.rect(43, 77, 48, 77, "t3")                     # back-knee fold

    # shirt: cream back, visible between the capelet hem and the belt
    sh = Ls["shirt"]
    sh.shaded(31, 55, 49, 61, "w1", "w2", "w3", 3, 3)
    sh.rect(39, 57, 40, 61, "w3")                                                   # back pleat

    # belt: back of the brown belt (buckle is at the front), two belt loops
    bl = Ls["belt"]
    bl.rect(30, 61, 50, 64, "r2"); bl.hline(30, 50, 61, "r1"); bl.hline(30, 50, 64, "r3")
    bl.rect(34, 61, 35, 64, "r3"); bl.rect(45, 61, 46, 64, "r3")

    # pouches: larger pouch on the character's right hip (screen right), smaller on the left (screen left)
    p = Ls["pouches"]
    p.shaded(49, 62, 56, 71, "r1", "r2", "r3", 2, 2); p.rect(49, 62, 56, 65, "r3"); p.hline(49, 56, 62, "r2")
    p.rect(52, 66, 53, 67, "y1")
    p.shaded(25, 62, 31, 69, "r1", "r2", "r3", 2, 2); p.rect(25, 62, 31, 64, "r3")

    # cloak: closed moss-green capelet back, A-line, hood lying on the upper back, motif band, back tree, fringe
    c = Ls["cloak"]
    rows = {}
    for y in range(31, 59):
        k = y - 31
        half = 13 + min(k, 16) // 2 + max(0, k - 16) // 3
        rows[y] = (40 - half, 40 + half - 1)
    c.rows(rows, "c2")
    for y, (x0, x1) in rows.items():                            # light plane left, shadow plane right
        c.hline(x0, x0 + 4, y, "c1"); c.hline(x1 - 4, x1, y, "c3")
    c.rows({29: (30, 50), 30: (28, 52)}, "c3")                  # hood rim rising behind the neck
    c.rows({29: (31, 37), 30: (29, 36)}, "c2")
    hood = {y: (31 + 2 * (max(0, y - 37) // 2), 49 - 2 * (max(0, y - 37) // 2)) for y in range(31, 46)}  # 2px stairs
    c.rows(hood, "c3")                                          # hood back lying on the shoulders
    c.rows({y: (x0 + 2, x1 - 2) for y, (x0, x1) in hood.items() if y <= 43}, "c2")
    c.rows({y: (x0 + 2, x0 + 4) for y, (x0, x1) in hood.items() if y <= 43}, "c1")
    c.rect(38, 44, 42, 46, "c3")                                # hood point
    for y in range(50, 54):                                     # cream tree motif band
        c.hline(rows[y][0] + 2, rows[y][1] - 2, y, "c3")
    for mx in (27, 53):
        c.vline(mx, 49, 54, "w2"); c.hline(mx - 1, mx + 1, 50, "w2"); c.hline(mx - 2, mx + 2, 52, "w2")
    c.rect(39, 47, 41, 54, "w2"); c.rect(37, 48, 43, 49, "w2"); c.rect(35, 51, 45, 52, "w2")  # back tree
    c.rect(41, 47, 41, 54, "w3")
    for y in range(55, 59):                                     # fringe
        x0, x1 = rows[y]
        c.hline(x0, x1, y, "c3")
    for x in range(rows[58][0], rows[58][1] + 1, 4):
        c.rect(x, 59, x + 1, 61, "q2"); c.hline(x, x + 1, 59, "c3")

    # arms: backs of the forearms below the capelet, cream rolled sleeves, backs of the hands
    a = Ls["arms"]
    for x0 in (16, 59):
        a.shaded(x0, 59, x0 + 5, 63, "w1", "w2", "w3", 2, 2)
        a.hline(x0, x0 + 5, 63, "w3")
        a.shaded(x0 + 1, 64, x0 + 5, 70, "s2", "s2", "s3", 2, 1)
        a.shaded(x0 + 1, 71, x0 + 5, 75, "s2", "s3", "s3", 1, 1); a.hline(x0 + 1, x0 + 5, 76, "s3")

    # bracelet: knotted green/tan rope on the character's LEFT wrist (screen left); knot tail at the back
    q = Ls["bracelet"]
    q.rect(16, 68, 22, 70, "c2")
    for x in range(16, 23, 2):
        q.rect(x, 68, x, 70, "q1")
    q.rect(18, 71, 19, 72, "c3")

    # whistle layer: only the tan cord loop around the back of the neck, over the hood rim; the wooden whistle
    # itself hangs at the chest and is not drawn through the back
    wh = Ls["whistle"]
    wh.rect(32, 29, 36, 30, "q2"); wh.rect(44, 29, 48, 30, "q2")

    # face layer: ears and a sliver of nape only (no eyes, brows or mouth from behind)
    f = Ls["face"]
    f.rect(29, 20, 30, 26, "s2"); f.rect(29, 20, 29, 23, "s1")                  # left ear (lit)
    f.rect(50, 20, 51, 26, "s3")                                                # right ear (shade)
    f.rows({29: (37, 43), 30: (37, 43)}, "s3")                                  # nape under the knot

    # hair: messy wavy dark brown covering the back of the head; tufted crown, stick-out wave locks, nape locks
    h = Ls["hair"]
    h.rows({8: (34, 41), 9: (30, 48), 10: (28, 50), **{y: (27, 53) for y in range(11, 20)},
            **{y: (31, 49) for y in range(20, 27)}, 27: (33, 47), 28: (35, 45)}, "h2")
    h.rows({8: (44, 47), 9: (44, 48)}, "h3")                                    # crown tuft
    h.rows({y: (25, 26) for y in range(13, 17)}, "h3"); h.rows({y: (54, 55) for y in range(15, 19)}, "h3")  # locks
    h.rows({20: (27, 30), 21: (27, 30), 22: (28, 30)}, "h2")                    # left lock over the ear top
    h.rows({20: (50, 53), 21: (50, 53), 22: (50, 52)}, "h3")
    h.rows({9: (32, 37), 10: (30, 39), 11: (29, 36), 12: (29, 33)}, "h1")      # upper-left sheen
    h.rows({14: (35, 39), 15: (36, 40)}, "h1"); h.rect(27, 13, 28, 19, "h1")
    h.rect(48, 10, 53, 19, "h3"); h.rect(46, 20, 49, 26, "h3")                  # right (shadow) plane
    h.rows({13: (41, 42), 14: (42, 43), 15: (43, 44)}, "h3")                    # wave breaks
    h.rows({18: (33, 34), 19: (34, 35), 20: (35, 36)}, "h3"); h.rows({17: (42, 43), 18: (43, 44)}, "h3")
    for x0 in (32, 44):                                                         # nape locks either side of the knot
        h.rows({26: (x0, x0 + 3), 27: (x0, x0 + 3)}, "h3")

    # braid: gathered knot at the nape, plait runs over the character's right shoulder (screen right) to the front
    br = Ls["braid"]
    br.rows({26: (38, 42), 27: (37, 43), 28: (37, 43), 29: (38, 42), 30: (38, 42)}, "h2")
    br.rect(38, 26, 39, 28, "h1"); br.rect(42, 28, 43, 30, "h3")
    br.rect(37, 31, 43, 31, "q1"); br.rect(37, 32, 43, 32, "q2")                # tan tie under the knot
    for i, y in enumerate(range(31, 39)):
        x = 44 + 3 * (i // 2)                                                   # 3 px stair every 2 rows
        br.hline(x, x + 3, y, "h2" if (i // 2) % 2 == 0 else "h3")
    br.rect(54, 39, 57, 41, "h2"); br.rect(54, 39, 55, 40, "h1")                # plait turning over the shoulder


def draw():
    Ls = {n: L() for n in LAYERS}
    draw_north(Ls)
    return M.finish(Ls)


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


def isolated_coords(full):
    rgb = full[..., :3].astype(int); op = full[..., 3] == 255; out = []
    for y, x in zip(*np.nonzero(op)):
        if not any(0 <= y + dy < H and 0 <= x + dx < W and op[y + dy, x + dx] and (rgb[y + dy, x + dx] == rgb[y, x]).all()
                   for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            out.append([int(x), int(y)])
    return out


def unchanged(manifest_rel):
    d = manifest_rel.rsplit("/", 1)[0]
    m = json.loads(open(fs(manifest_rel), "rb").read())
    pal = json.loads(open(fs(f"{d}/{m['files']['palette']['file']}"), "rb").read())
    files = {v["file"]: sha(open(fs(f"{d}/{v['file']}"), "rb").read()) == v["rawsha256"] for v in m["files"].values()}
    return {"files_match_manifest": all(files.values()), "palette_colors_identical": pal["colors"] == PAL}


def gates(r):
    g = MS.gates(r)                                               # Lin gates run with d == "north"
    with zipfile.ZipFile(io.BytesIO(r[4])) as z:
        dj = z.read("data.json")
    g["pxo_labels_north"] = b"muxiu-north" in dj and b"muxiu-south" not in dj
    vis = g["visible_role_texels"]
    g["anchor_layers_visible_north"] = all(vis[n] >= 12 for n in ("cloak", "braid", "bracelet", "hair", "face"))
    full = r[2]; op = full[..., 3] == 255
    wood = {S.rgb("x1"), S.rgb("x2")}
    g["whistle_body_not_drawn_through_back"] = not any(tuple(int(v) for v in c) in wood for c in full[op][:, :3])
    g["isolated_texel_coords"] = isolated_coords(full)
    return g


HARD = [k for k in MS.HARD if k not in ("face_has_eye", "anchor_layers_visible")] + [
    "north_face_no_eyes_or_mouth", "pxo_labels_north", "anchor_layers_visible_north",
    "whistle_body_not_drawn_through_back"]


def manifest(files, g):
    m = {"actor_id": ACTOR, "content_id": f"content.char.{ACTOR}.static-{D}", "status": "UNAPPROVED",
         "direction": D, "pose": "idle-static", "canvas": [W, H], "pivot": list(PIN), "body_rows": list(BODY_ROWS),
         "display_scale": S.DISPLAY_SCALE, "logical_height_px": (BODY_ROWS[1] - BODY_ROWS[0] + 1) * S.DISPLAY_SCALE,
         "layers": [{"name": n, "visible": n != "guides"} for n in LAYERS],
         "face_layer_role": "ears and nape only (no eyes, brows or mouth)",
         "view_notes": "north back view (character's right = screen right): messy wavy dark-brown hair covering the "
                       "back of the head with crown tuft, stick-out wave locks and nape locks; braid gathered in a "
                       "knot at the nape with tan tie, plait running over the character's right shoulder (screen "
                       "right) to the front; moss-green closed short capelet back with the hood lying on the upper "
                       "back, cream tree motif band, larger cream back tree and fringed hem; tan whistle cord loop "
                       "crossing the back of the neck (whistle itself at the front, not visible); cream shirt below "
                       "the hem; knotted green/tan rope bracelet on the character's left wrist (screen left); belt "
                       "back with loops; larger pouch on the right hip (screen right), smaller on the left; "
                       "olive-brown trousers with seat seam and back-knee folds; green leg wraps with back cord "
                       "knots; brown boot backs with heel counters.",
         "authored_deviations_from_sheet": [
             "braid: from behind only the nape knot and the plait crossing the right shoulder are drawn; the hanging "
             "length is at the front (continuous with south/west v01).",
             "whistle: front-worn; only its cord loop is drawn at the back of the neck.",
             "chest straps and extra belt charms/cloth tatters omitted for 48 px readability."],
         "gate_swaps": {"face_has_eye": "replaced by the reused Lin author's north_face_no_eyes_or_mouth",
                        "anchor_layers_visible": "replaced by anchor_layers_visible_north (same 12-texel threshold, "
                                                 "whistle excluded) plus whistle_body_not_drawn_through_back"},
         "files": {k: {"file": fname(*FILE_KEYS[k]), "rawsha256": sha(b)} for k, b in files.items()},
         "colour_count": g["colour_count"], "genuine_visible_role_layers": g["genuine_visible_role_layers"],
         "isolated_texels": g["isolated_texels"],
         "portrait_ref": {"file": MS.PORTRAIT_REL, "expected_sha256": MS.PORTRAIT_SHA, "approval": "UNAPPROVED",
                          "use": "identity reference only; no pixels sampled"},
         "continuity_refs": {SOUTH_MANIFEST_REL: PINS[SOUTH_MANIFEST_REL], WEST_MANIFEST_REL: PINS[WEST_MANIFEST_REL]},
         "bible_ref": "character-06: 24yo animal carer; moss-green short cloak, knotted rope bracelet, small whistle, "
                      "swaying braid",
         "style_contract": "docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md",
         "source_contract": "same as Muxiu south v01: 80x112, pivot (40,104), body rows 8..103, display scale 0.5 = "
                            "48 logical px, binary alpha, transparent border, same declared palette, 24..48 used "
                            "colours, >=8 genuine role layers, hidden guides layer",
         "replaces_placeholder": "does not modify the old 32x48 native-animation placeholder; it is not counted",
         "author_tool": "tools/" + os.path.basename(__file__), "author_revision": "r2 (supersedes failed draft and r1; neither built source files)",
         "reused_tool_pins": {**PINS, **MS.PINS},
         "serialization_helper": S.HELPER_REL,
         "pixel_source": "code-authored native pixels, declared palette",
         "limitations": "north static only; no runtime wiring, no east, no motion, no creator art approval"}
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
    su = {"south": unchanged(SOUTH_MANIFEST_REL), "west": unchanged(WEST_MANIFEST_REL)}
    bad = [k for k in HARD + ["deterministic_rebuild"] if not g[k]]
    bad += [f"tool_pin:{rel}" for rel, ok in {**PIN_OK, **MS.PIN_OK}.items() if not ok]
    bad += [f"{d}:{k}" for d, v in su.items() for k, ok in v.items() if not ok]
    files = dict(zip(("png", "pxo", "ora", "palette"), r1[3:]))
    names = {fname(*FILE_KEYS[k]): b for k, b in files.items()}
    names[fname("manifest", "json")] = manifest(files, g)
    named = {f"{OUT_REL}/{n}": b for n, b in names.items()}
    if cmd in ("stage", "preview"):                            # content-named preview: never reuses a name
        from PIL import Image
        buf = io.BytesIO()
        Image.fromarray(r1[2], "RGBA").resize((W * 6, H * 6), Image.NEAREST).save(buf, "PNG")
        prev = f"{QA_REL}/{SLUG}_{ACTOR}_{D}-preview-x6_unapproved-v01r2_{STAMP}-{sha(r1[3])[:8]}.png"
        write_new(prev, buf.getvalue())
        print("preview:", prev, sha(buf.getvalue()))
    if cmd in ("stage", "install") and bad:
        raise SystemExit(f"hard gates failed: {bad}")
    if cmd == "stage":
        for n, data in names.items():
            write_new(f"{STAGE_REL}/{n}", data)
    if cmd == "install":                                       # fresh north dir; staged bytes must match rebuild
        for n, data in names.items():
            if open(fs(f"{STAGE_REL}/{n}"), "rb").read() != data:
                raise SystemExit(f"staged file differs from rebuild: {n}")
            write_new(f"{OUT_REL}/{n}", data)
    disk = {rel: (sha(open(fs(rel), "rb").read()) == sha(b)) if os.path.exists(fs(rel)) else None
            for rel, b in named.items()}
    report = {k: g[k] for k in ("body_rows", "colour_count", "genuine_visible_role_layers", "visible_role_texels",
                                "isolated_texels", "isolated_texel_coords", "silhouette_width",
                                "identity_colours_visible", "binary_alpha", "no_opaque_border",
                                "pin_inside_feet_span", "all_colours_declared", "ora_hidden",
                                "north_face_no_eyes_or_mouth", "anchor_layers_visible_north",
                                "whistle_body_not_drawn_through_back", "deterministic_rebuild")}
    report.update(tool_pins_ok={**PIN_OK, **MS.PIN_OK}, siblings_unchanged=su, disk_matches_rebuild=disk,
                  staged_names=sorted(names), hard_failures=bad)
    print(json.dumps(report, indent=1))
    ok = not bad and all(v is True for v in disk.values())
    print("MUXIU_NORTH_V01R2_" + ("ALL_OK" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
