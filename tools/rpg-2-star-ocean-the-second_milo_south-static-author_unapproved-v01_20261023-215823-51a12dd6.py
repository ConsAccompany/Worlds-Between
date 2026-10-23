"""Milo SOUTH idle static, native 80x112 source package (UNAPPROVED v01).

content.char.milo.static-south. Code-authored native pixels in the Sea of Stars direction (broad clusters,
upper-left light), 48 logical px at display scale 0.5. Identity anchors (Bible character 04 and the approved
hairstyle sheet; identity reference only, no pixels sampled): very short spiky dark-brown hair with a silver
temple patch on the character's right (screen left), light stubble, green eyes, navy high-collar zip shirt,
white/grey SHORT medical coat (Bible: short; the sheet's knee length is not used) with green cross, square
white medicine case with navy straps and green cross on the character's right hip, bright green wristband on
the character's left wrist (screen right), navy trousers with green piping, dark boots with pale bands and
green patches. The case strap is drawn cross-body (left shoulder -> right hip) for readability at 48 px; the
sheet carries it over the right shoulder. Recorded as an authored simplification in the manifest.

Reuses the Lin Que v01 author (L pen, outline/guide finish, extended gates) and through it the Jiang south v01
gates and the male v8pair PNG/PXO/ORA serializers. Their palette/layer globals are rebound in memory only; no
Lin, Jiang or male file is written. All three tool files are hash-pinned.

  python -X utf8 -I <this> build   # writes new files only (refuses to overwrite different bytes)
  python -X utf8 -I <this> check   # rebuilds twice in memory and compares with files on disk
"""
import hashlib, importlib.util, io, json, os, sys, zipfile
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG, ACTOR, D = "rpg-2-star-ocean-the-second", "milo", "south"
STAMP, RUN_ID = "20261023-215823", "51a12dd6"
OUT_REL = "game/assets/characters/milo-native-v01/south"
QA_REL = "outputs/milo-s01/author"
LIN_TOOL_REL = "tools/rpg-2-star-ocean-the-second_lin-que_four-direction-static-author_unapproved-v01_20261022-222500-3d61c74e.py"
PINS = {LIN_TOOL_REL: "0ddbea4591312c767b2ac46da6be29302b908cf311adb92eaf5ed26c300eff82",
        "tools/rpg-2-star-ocean-the-second_jiang-lan_south-static-author_unapproved-v01_20261021-235007-514b9771.py":
            "35005f3c904802251c773838d61068d4aea847c993f6e354676e88a599db69b4",
        "tools/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair-static-pilot-build-and-check_unapproved-v01_20261018-130225-f28bd26d.py":
            "fcd9d6e88e7401097e9c8afe8061df6dcdd9e2132892680522d7d722ac2abb79"}
PORTRAIT_REL = "outputs/rpg-2-star-ocean-the-second_milo_character-sheet_hairstyle-v02_20261013-161317-f1651dc0.png"
PORTRAIT_SHA = "79a02c532681042ec389cfb6eae0577e3f967652641be7b853461e6adc4c244f"
ZIP_DT = (2026, 10, 23, 21, 58, 22)

PAL = {  # declared palette, <=40 entries (male serializer palette grid is 8x5); upper-left light
    "s1": "f2c8a2", "s2": "d9a17b", "s3": "b07454", "s4": "754331", "j1": "a98670",   # skin, stubble
    "h1": "6e5848", "h2": "4b3b31", "h3": "30261f", "h4": "1a1411",                    # dark-brown hair
    "a1": "eef0f4", "a2": "b8bec8", "a3": "848b98",                                    # silver temple
    "e1": "f6f7f2", "e2": "3e8a3c", "m1": "9a5243",                                    # eye white, green iris, mouth
    "w1": "fcfcfa", "w2": "e0e3e8", "w3": "b2b9c4", "w4": "5b6373",                    # white/grey coat
    "n1": "4c5d8e", "n2": "334068", "n3": "232c4a", "n4": "131a2d",                    # navy
    "g1": "c6f76a", "g2": "74d93a", "g3": "3e9c2b", "g4": "22581b",                    # bright medical green
    "r1": "8a6248", "r2": "553a2b",                                                    # belt leather
    "b1": "6a6058", "b2": "443d37", "b3": "2a2521", "k1": "111113",                    # boots
    "x1": "dde1e7", "x2": "989fab",                                                    # metal buckle / zip
}
LAYERS = ["boots", "trousers", "undershirt", "coat", "belt", "case", "strap", "arms", "wristband", "face", "hair",
          "guides"]
OUTLINE = {"boots": "k1", "trousers": "n4", "undershirt": "n4", "coat": "w4", "belt": "r2", "case": "n4",
           "strap": "n4", "arms": "n4", "wristband": "g4", "face": "s4", "hair": "h4"}
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
M = load(LIN_TOOL_REL, "lin_que_v01_for_milo")                 # loads its own Jiang module instance as M.S
S = M.S
for mod in (M, S):                                            # rebind in memory only
    mod.PAL, mod.LAYERS, mod.OUTLINE, mod.ZIP_DT = PAL, LAYERS, OUTLINE, ZIP_DT
M.ACTOR = ACTOR
W, H, PIN, BODY_ROWS, L = S.W, S.H, S.PIN, S.BODY_ROWS, S.L


# ------------------------------------------------------------------ south (front)
def draw_south(Ls):
    # boots: chunky, pale band at the top, green patch, wide toes
    b = Ls["boots"]
    for x0, x1 in ((29, 39), (41, 51)):
        b.shaded(x0 + 1, 88, x1 - 1, 97, "b1", "b2", "b3", 2, 2)
        b.rect(x0 + 1, 88, x1 - 1, 90, "w3"); b.hline(x0 + 1, x1 - 1, 88, "w2"); b.rect(x1 - 3, 88, x1 - 1, 90, "w4")
        b.rect(x0 + 4, 92, x0 + 6, 94, "g3"); b.hline(x0 + 4, x0 + 5, 92, "g2")
        b.shaded(x0, 98, x1, 101, "b1", "b2", "b3", 3, 2)
        b.rect(x0 + 2, 98, x0 + 4, 99, "b1")                                        # toe highlight
        b.hline(x0, x1, 102, "b3"); b.hline(x0, x1, 103, "k1")
    b.rect(28, 100, 28, 103, "b3"); b.rect(52, 100, 52, 103, "b3")                 # wide soles

    # trousers: navy, green piping on the outer seams
    t = Ls["trousers"]
    t.rect(31, 63, 49, 69, "n2")
    t.shaded(30, 69, 39, 89, "n1", "n2", "n3", 2, 2)
    t.shaded(41, 69, 50, 89, "n1", "n2", "n3", 2, 2)
    t.vline(40, 66, 89, "n4")
    t.vline(30, 72, 88, "g3"); t.vline(50, 72, 88, "g3")
    t.rect(34, 80, 36, 80, "n3"); t.rect(45, 81, 47, 81, "n3")                     # knee folds

    # undershirt: navy high zip collar and the strip seen through the open coat
    u = Ls["undershirt"]
    u.rect(36, 33, 44, 37, "n2"); u.hline(37, 43, 33, "n1"); u.rect(43, 34, 44, 37, "n3")
    u.shaded(35, 38, 45, 64, "n1", "n2", "n3", 2, 2)
    u.vline(40, 34, 64, "x2")                                                      # zip

    # coat: white/grey SHORT medical coat, broad shoulders, open front, standing collar, hem at mid-thigh
    c = Ls["coat"]
    c.rows({37: (30, 50), 38: (27, 53), **{y: (26, 54) for y in range(39, 62)}}, "w2")
    for x0, x1 in ((26, 37), (43, 54)):                                             # skirt panels
        c.shaded(x0, 62, x1, 75, "w1", "w2", "w3", 2, 2)
    c.rows({76: (27, 37), 77: (27, 36)}, "w3"); c.rows({76: (43, 53), 77: (44, 53)}, "w3")
    c.rect(26, 39, 28, 61, "w1"); c.rect(52, 39, 54, 61, "w3")                     # side light/shadow planes
    c.rows({y: (35, 36) for y in range(38, 62)}, "w3"); c.rows({y: (44, 45) for y in range(38, 62)}, "w1")
    c.rows({32: (31, 35), 33: (30, 36), **{y: (30, 37) for y in range(34, 38)}}, "w1")  # standing collar
    c.rows({32: (45, 49), 33: (44, 50), **{y: (43, 50) for y in range(34, 38)}}, "w2")
    c.rect(49, 34, 50, 37, "w3"); c.vline(36, 34, 37, "w3"); c.vline(43, 34, 37, "w3")
    c.hline(27, 53, 38, "w3")                                                      # shoulder seam under collar
    c.rect(48, 43, 49, 48, "g2"); c.rect(46, 45, 51, 46, "g2"); c.rect(48, 45, 49, 46, "g1")  # green cross
    c.rect(28, 66, 33, 70, "w3"); c.hline(28, 33, 66, "w4"); c.rect(30, 66, 31, 67, "g2")   # pockets
    c.rect(47, 66, 52, 70, "w3"); c.hline(47, 52, 66, "w4"); c.rect(49, 66, 50, 67, "g2")
    c.rect(27, 73, 29, 75, "g3"); c.rect(51, 73, 53, 75, "g3")                     # hem accents

    # belt: visible in the open front only
    bl = Ls["belt"]
    bl.rect(35, 61, 45, 63, "r2"); bl.hline(35, 45, 61, "r1")
    bl.rect(38, 61, 42, 63, "x2"); bl.hline(38, 42, 61, "x1"); bl.rect(39, 62, 41, 62, "r2")

    # case: square white medicine case on the character's right hip (screen left)
    k = Ls["case"]
    k.shaded(13, 63, 27, 76, "w1", "w2", "w3", 2, 2)
    k.hline(13, 27, 66, "w3"); k.hline(14, 26, 63, "w1")                           # lid line
    k.rect(14, 63, 15, 76, "n2"); k.rect(25, 63, 26, 76, "n2"); k.vline(14, 63, 76, "n1")  # navy straps
    k.rect(14, 67, 15, 68, "x2"); k.rect(25, 67, 26, 68, "x2")                     # buckles
    k.rect(19, 68, 21, 73, "g2"); k.rect(18, 69, 22, 72, "g2")                     # green cross
    k.rect(19, 69, 20, 70, "g1"); k.rect(21, 69, 22, 72, "g3"); k.rect(19, 73, 21, 73, "g3")
    k.rect(17, 61, 23, 62, "n2"); k.hline(18, 22, 61, "n1")                        # handle

    # strap: cross-body, character's left shoulder -> right hip, with a green panel. One flat colour per row
    # band (3 px wide): per-pixel diagonal shade stripes read as noise at 48 px. Lighter n1 so it stays
    # distinct from the n2 shirt where it crosses the open coat front.
    s = Ls["strap"]
    for i in range(24):
        x, y = 49 - i, 37 + i
        s.hline(x - 2, x, y, "g2" if 9 <= i <= 12 else "n1")
    s.rect(24, 60, 27, 62, "n2")

    # arms: rolled white sleeves, navy cuffs, bare forearms, relaxed hands
    a = Ls["arms"]
    for x0, hi, dk in ((20, "w1", "w3"), (54, "w2", "w3")):
        a.rows({38: (x0 + 1, x0 + 5), 39: (x0, x0 + 6)}, "w2")
        a.shaded(x0, 40, x0 + 6, 53, hi, "w2", dk, 2, 2)
        a.rect(x0, 54, x0 + 6, 57, "n2"); a.hline(x0, x0 + 6, 54, "n1"); a.hline(x0, x0 + 6, 57, "n3")
        a.shaded(x0 + 1, 58, x0 + 5, 63, "s1", "s2", "s3", 2, 1)
        a.shaded(x0 + 1, 64, x0 + 5, 68, "s2", "s2", "s3", 1, 1); a.hline(x0 + 1, x0 + 5, 69, "s3")
        a.hline(x0 + 1, x0 + 5, 65, "s3")                                          # knuckle line
    a.rect(20, 41, 21, 52, "w1")

    # wristband: bright green band on the character's left wrist (screen right)
    wb = Ls["wristband"]
    wb.rect(54, 60, 60, 62, "g2"); wb.hline(54, 60, 60, "g1"); wb.rect(59, 60, 60, 62, "g3")
    wb.rect(56, 61, 57, 61, "g1")

    # face: square jaw, kind smile, light stubble, green eyes, ears
    f = Ls["face"]
    f.rows({**{y: (31, 49) for y in range(15, 28)}, 28: (32, 48), 29: (32, 48), 30: (32, 48), 31: (32, 48),
            32: (34, 46), 33: (36, 44)}, "s2")
    f.rect(31, 16, 33, 27, "s1"); f.rect(47, 16, 49, 30, "s3"); f.rect(46, 29, 46, 32, "s3")
    f.rect(29, 21, 30, 27, "s2"); f.rect(29, 21, 29, 24, "s1"); f.rect(30, 25, 30, 26, "s3")  # ears
    f.rect(50, 21, 51, 27, "s3"); f.px(50, 24, "s4")
    f.hline(33, 37, 21, "h3"); f.hline(43, 47, 21, "h3"); f.px(33, 22, "h3"); f.px(47, 22, "h3")  # brows
    for ex in (34, 43):                                                             # eyes
        f.hline(ex, ex + 3, 23, "h4")
        f.rect(ex, 24, ex + 3, 25, "e1"); f.rect(ex + 1, 24, ex + 2, 25, "e2"); f.px(ex + 2, 24, "h4")
    f.px(41, 25, "s3"); f.px(41, 26, "s3"); f.hline(39, 41, 27, "s3")               # nose
    f.hline(38, 42, 30, "m1"); f.px(37, 29, "m1"); f.px(43, 29, "m1")               # gentle smile
    f.rows({31: (36, 44), 32: (36, 44), 33: (38, 42)}, "j1")                        # stubble
    f.rect(33, 29, 34, 31, "j1"); f.rect(45, 29, 46, 32, "j1")

    # hair: very short spiky dark brown, silver patch on the character's right temple (screen left)
    h = Ls["hair"]
    # spike rows: each row-9 segment extends 2 px left of its tip and the gaps are 2 px, so outline runs join
    h.rows({8: (35, 36), 9: (33, 36), 10: (31, 49), **{y: (30, 50) for y in range(11, 15)},
            **{y: (29, 51) for y in range(15, 18)}}, "h2")
    h.rows({8: (41, 42), 9: (39, 42)}, "h2"); h.rows({8: (47, 48), 9: (45, 48)}, "h3")
    h.rows({18: (31, 34), 19: (32, 33)}, "h2"); h.rows({18: (37, 40), 19: (38, 39)}, "h2")   # short fringe tips
    h.rows({18: (43, 46), 19: (44, 45)}, "h2"); h.rows({18: (48, 51), 19: (49, 51)}, "h3")
    h.rect(49, 20, 51, 22, "h3")                                                   # cropped right sideburn
    h.rows({9: (34, 36), 10: (33, 38), 11: (33, 40), 12: (34, 38)}, "h1")          # upper-left sheen
    h.px(40, 9, "h1"); h.px(41, 8, "h1")
    h.rect(47, 10, 50, 17, "h3"); h.rows({13: (42, 43), 14: (43, 44)}, "h3")       # right plane, spike breaks
    h.rows({12: (31, 33), **{y: (29, 33) for y in range(13, 18)}, 18: (29, 30), 19: (29, 30), 20: (29, 30),
            21: (29, 30)}, "a2")                                                   # silver temple patch
    h.rows({13: (30, 31), 14: (29, 31), 15: (29, 30), 16: (29, 30)}, "a1"); h.rows({17: (32, 33)}, "a3")


def strip_coat_opening(Ls):
    """Open coat front: transparent wedge in the coat layer so the navy shirt/trousers show through."""
    a = Ls["coat"].a
    for y in range(38, 78):
        half = 3 if y < 62 else 2 + (y - 62) // 3
        a[y, 40 - half:40 + half + 1] = 0


def draw():
    Ls = {n: L() for n in LAYERS}
    draw_south(Ls)
    strip_coat_opening(Ls)
    return M.finish(Ls)


# ------------------------------------------------------------------ package
def fix_pxo_metadata(pxo):
    """Male helper hardcodes its export/palette names; rewrite for Milo south, keep entry order and dates."""
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
    g["pxo_no_lin_metadata"] = b"lin-que" not in dj
    g["palette_fits_pxo_grid_40"] = len(PAL) <= 40
    al = full[..., 3]
    g["isolated_texels"] = isolated(full)
    g["isolated_texels_le_24"] = g["isolated_texels"] <= 24
    cols = lambda keys: {S.rgb(k) for k in keys}
    used = {tuple(c) for c in full[al == 255][:, :3]}
    g["identity_colours_visible"] = {"green": bool(used & cols(("g1", "g2", "g3"))), "silver": bool(used & cols(("a1", "a2"))),
                                     "coat_white": bool(used & cols(("w1", "w2"))), "navy": bool(used & cols(("n1", "n2")))}
    g["identity_colours_all"] = all(g["identity_colours_visible"].values())
    vis = g["visible_role_texels"]
    g["anchor_layers_visible"] = all(vis[n] >= 12 for n in ("case", "wristband", "coat", "hair", "face"))
    ys, xs = np.nonzero(al)
    g["silhouette_width"] = int(xs.max() - xs.min() + 1)
    return g


HARD = M.HARD + ["pxo_no_lin_metadata", "palette_fits_pxo_grid_40", "isolated_texels_le_24", "identity_colours_all",
                 "anchor_layers_visible", "face_has_eye"]


def manifest(files, g):
    m = {"actor_id": ACTOR, "content_id": f"content.char.{ACTOR}.static-{D}", "status": "UNAPPROVED",
         "direction": D, "pose": "idle-static", "canvas": [W, H], "pivot": list(PIN), "body_rows": list(BODY_ROWS),
         "display_scale": S.DISPLAY_SCALE, "logical_height_px": (BODY_ROWS[1] - BODY_ROWS[0] + 1) * S.DISPLAY_SCALE,
         "layers": [{"name": n, "visible": n != "guides"} for n in LAYERS],
         "face_layer_role": "front face, two green eyes, brows, nose, smile, stubble, ears",
         "view_notes": "front: very short spiky dark-brown hair with silver patch on the character's right temple "
                       "(screen left); white/grey short coat to mid-thigh, open front over a navy zip high-collar "
                       "shirt, green cross on the character's left chest; square white case with navy straps and "
                       "green cross on the character's right hip (screen left); bright green wristband on the "
                       "character's left wrist (screen right); navy trousers with green piping; dark boots with "
                       "pale bands and green patches",
         "authored_deviations_from_sheet": [
             "coat length: Bible character-04 says SHORT coat; the sheet shows knee length. Mid-thigh hem used.",
             "case strap: drawn cross-body (character's left shoulder to right hip) for 48 px readability; the sheet "
             "shows the strap over the right shoulder."],
         "files": {k: {"file": fname(*FILE_KEYS[k]), "rawsha256": sha(b)} for k, b in files.items()},
         "colour_count": g["colour_count"], "genuine_visible_role_layers": g["genuine_visible_role_layers"],
         "isolated_texels": g["isolated_texels"],
         "portrait_ref": {"file": PORTRAIT_REL, "expected_sha256": PORTRAIT_SHA, "approval": "approved source portrait",
                          "use": "identity reference only (approved hairstyle sheet); no pixels sampled"},
         "style_contract": "docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md",
         "source_contract": "reuses the Jiang/Lin native static contract: 80x112, pivot (40,104), body rows 8..103, "
                            "display scale 0.5 = 48 logical px, binary alpha, transparent border, declared palette "
                            "24..48 used colours, >=8 genuine role layers, hidden guides layer",
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
    if cmd == "build":
        if bad:
            raise SystemExit(f"hard gates failed: {bad}")
        for rel, data in named.items():
            p = fs(rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            if os.path.exists(p) and open(p, "rb").read() != data:
                raise SystemExit(f"refusing to overwrite different file {rel}")
            open(p, "wb").write(data)
        open(fs("game/assets/characters/milo-native-v01/.gdignore"), "ab").close()
        from PIL import Image
        os.makedirs(fs(QA_REL), exist_ok=True)
        prev = f"{QA_REL}/{SLUG}_{ACTOR}_{D}-preview-x6_unapproved-v01_{STAMP}-{uid(D, 'preview')}.png"
        Image.fromarray(r1[2], "RGBA").resize((W * 6, H * 6), Image.NEAREST).save(fs(prev))
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
    print("MILO_SOUTH_V01_" + ("ALL_OK" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
