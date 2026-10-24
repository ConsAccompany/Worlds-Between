"""Heya SOUTH idle static, native 80x112 source package (UNAPPROVED v01).

content.char.heya.static-south. Code-authored native pixels in the Sea of Stars direction (broad coherent
clusters, upper-left light), 48 logical px at display scale 0.5. Identity anchors (Bible character-26 /
companion #26, 44-year-old clinician who respects a patient's bodily autonomy; concept sheet is an UNAPPROVED
identity reference, no pixels sampled): restrained patient closed-lip smile, warm mature face; auburn hair
gathered into a braided coil LOW at the nape (visible as two plaited masses below the ears, never a high bun);
cool grey-white medical scarf wound at the neck with a long tail on the character's left (screen RIGHT); ivory
open clinician coat over a pale grey-white apron and charcoal underdress; dark-red emergency bag with brass
clasps at the character's left hip (screen RIGHT), on a leather cross-body strap; small herb sprig at the
character's right chest (screen LEFT); dark gloves and brown leather boots.

The concept sheet shows a white head-veil and a long dark-red shawl; the Bible source identity overrides those
inconsistencies, so the veil is omitted to keep the low braided coil readable and the shawl is reduced to the
canonical dark-red emergency bag. Hues were chosen by eye from the sheet; pixels are authored, not resampled.

Reuses the Lin Que v01 author (L pen, outline/guide finish, extended gates) and through it the Jiang south v01
gates and the male v8pair PNG/PXO/ORA serializers, exactly as the Muxiu/Yanke south v01 authors do. Their
palette/layer globals are rebound in memory only; no Lin, Jiang, Muxiu, Yanke or male file is written. All
reused tool files are hash-pinned.

  python -X utf8 -I <this> preview  # previews only, no package writes
  python -X utf8 -I <this> build    # fresh staging package under outputs/heya-s148/staging/south
  python -X utf8 -I <this> install  # copies the verified staging package into the game tree
  python -X utf8 -I <this> check    # rebuilds twice in memory and compares staging + installed files
"""
import hashlib, importlib.util, io, json, os, shutil, subprocess, sys, zipfile
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG, ACTOR, D = "rpg-2-star-ocean-the-second", "heya", "south"
STAMP, RUN_ID = "20261024-125310", "h148s001"
OUT_REL = "game/assets/characters/heya-native-v01/south"
STAGE_REL = "outputs/heya-s148/staging/south"
QA_REL = "outputs/heya-s148/author"
LIN_TOOL_REL = "tools/rpg-2-star-ocean-the-second_lin-que_four-direction-static-author_unapproved-v01_20261022-222500-3d61c74e.py"
PINS = {LIN_TOOL_REL: "0ddbea4591312c767b2ac46da6be29302b908cf311adb92eaf5ed26c300eff82",
        "tools/rpg-2-star-ocean-the-second_jiang-lan_south-static-author_unapproved-v01_20261021-235007-514b9771.py":
            "35005f3c904802251c773838d61068d4aea847c993f6e354676e88a599db69b4",
        "tools/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair-static-pilot-build-and-check_unapproved-v01_20261018-130225-f28bd26d.py":
            "fcd9d6e88e7401097e9c8afe8061df6dcdd9e2132892680522d7d722ac2abb79",
        "tools/rpg-2-star-ocean-the-second_muxiu_south-static-author_unapproved-v01_20261024-071500-6d3e9a51.py":
            "f329ac7aa595f003ba741ed8de6cf5aade1d912acfa65a1720ce731eb24737f1"}   # structural template
PORTRAIT_REL = "outputs/rpg-2-star-ocean-the-second_heya_character-sheet_v01_20261013-192811-6cbcb12e.png"
PORTRAIT_SHA = "918e8a17ea297a1eece49b4240712b19c08fab09eadc29eb7620d77b9a68e3e0"
ZIP_DT = (2026, 10, 24, 12, 53, 10)
HELPER = "python3 tools/wb_safe_replace.py"

PAL = {  # declared palette, 35 entries (<=40 male serializer grid); upper-left light
    "s1": "f0c8a8", "s2": "d9a684", "s3": "b57a5c",                                   # warm mature skin
    "h1": "a85a34", "h2": "7d3f24", "h3": "552716", "h4": "2e140b",                   # auburn hair / braid
    "e1": "f5efe4", "e2": "5c4a2e", "m1": "9a5048",                                   # eye white, hazel iris, mouth
    "w1": "f1e9d8", "w2": "d9cdb8", "w3": "b3a58c", "w4": "6e6352",                   # ivory clinician coat
    "v1": "e2e5dd", "v2": "c3c8bf", "v3": "949a90",                                   # pale grey-white apron
    "f1": "e8ecec", "f2": "c2cacb", "f3": "909b9e",                                   # cool grey-white scarf
    "c1": "5a5c60", "c2": "3f4146", "c3": "2b2d31", "c4": "181a1d",                   # charcoal underdress
    "b1": "8e3b36", "b2": "642523", "b3": "401615",                                   # dark-red emergency bag
    "r1": "8a5c3e", "r2": "5e3a26", "r3": "3b2316",                                   # leather / boots
    "y1": "d8b060", "y2": "96702e",                                                   # brass
    "k1": "15120f", "k2": "2a2520",                                                   # gloves
    "n1": "7f8f52", "n2": "556338",                                                   # herb sprig
}
LAYERS = ["boots", "dress", "coat", "apron", "belt", "strap", "bag", "arms", "herb", "face", "hair", "braid",
          "scarf", "guides"]
OUTLINE = {"boots": "r3", "dress": "c4", "coat": "w4", "apron": "v3", "belt": "r3", "bag": "b3",
           "strap": "r3", "arms": "r3", "herb": "n2", "face": "s3", "hair": "h4", "scarf": "f3"}
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
M = load(LIN_TOOL_REL, "lin_que_v01_for_heya")               # loads its own Jiang module instance as M.S
S = M.S
for mod in (M, S):                                            # rebind in memory only
    mod.PAL, mod.LAYERS, mod.OUTLINE, mod.ZIP_DT = PAL, LAYERS, OUTLINE, ZIP_DT
M.ACTOR = ACTOR
W, H, PIN, BODY_ROWS, L = S.W, S.H, S.PIN, S.BODY_ROWS, S.L


# ------------------------------------------------------------------ south (front)
def draw_south(Ls):
    # boots: dark-brown leather, folded cuff, brass buckle strap, low stacked heel, broad toe
    b = Ls["boots"]
    for x0, x1 in ((29, 38), (42, 51)):
        b.shaded(x0 + 1, 88, x1 - 1, 96, "r1", "r2", "r3", 2, 2)
        b.hline(x0 + 1, x1 - 1, 88, "r1"); b.hline(x0 + 1, x1 - 1, 89, "r2")          # folded cuff
        b.rect(x0 + 3, 92, x0 + 5, 93, "y2"); b.hline(x0 + 3, x0 + 5, 92, "y1")      # buckle strap
        b.shaded(x0, 97, x1, 101, "r1", "r2", "r3", 3, 2)                             # foot
        b.rect(x0 + 1, 97, x0 + 4, 98, "r1")                                          # toe plane
        b.hline(x0, x1, 102, "r3")
        b.hline(x0 + 1, x1 - 1, 103, "r3")                                            # sole
    b.rect(29, 101, 31, 103, "r3"); b.rect(49, 101, 51, 103, "r3")                    # stacked heels

    # dress: charcoal underdress, high collar, open front placket, A-line skirt to the boot tops
    d = Ls["dress"]
    d.rows({33: (36, 44), 34: (35, 45), **{y: (34, 46) for y in range(35, 39)},
            **{y: (33, 47) for y in range(39, 45)}, **{y: (32, 48) for y in range(45, 54)},
            **{y: (31, 49) for y in range(54, 60)}}, "c2")
    d.rect(33, 33, 34, 42, "c1"); d.rect(46, 33, 48, 54, "c3")
    d.rect(39, 39, 40, 58, "c1"); d.vline(41, 39, 58, "c2")                            # placket seen in coat gap
    d.rows({**{y: (30, 50) for y in range(60, 65)}, **{y: (29, 51) for y in range(65, 71)},
            **{y: (28, 52) for y in range(71, 79)}, **{y: (27, 53) for y in range(79, 89)}}, "c2")
    for y in range(60, 89):                                                           # broad light/shadow planes
        x0, x1 = (30, 50) if y < 65 else ((29, 51) if y < 71 else ((28, 52) if y < 79 else (27, 53)))
        d.px(x0, y, "c1"); d.px(x0 + 1, y, "c1")
        d.px(x1, y, "c3"); d.px(x1 - 1, y, "c3")
    d.hline(27, 53, 87, "c3"); d.hline(27, 53, 88, "c4")                              # hem shadow

    # coat: ivory open clinician coat, narrow shoulders, long panels, worn hem
    c = Ls["coat"]
    c.rows({33: (34, 46), 34: (31, 49), 35: (29, 51), **{y: (29, 51) for y in range(36, 41)},
            **{y: (30, 50) for y in range(41, 51)}, **{y: (30, 50) for y in range(51, 59)},
            **{y: (28, 52) for y in range(59, 65)}, **{y: (27, 53) for y in range(65, 89)}}, "w2")
    c.rect(29, 35, 32, 58, "w1"); c.rect(48, 35, 51, 58, "w3")
    c.hline(31, 49, 34, "w3"); c.hline(30, 50, 35, "w2")                              # shoulder seam
    for y in range(59, 89):
        x0, x1 = (28, 52) if y < 65 else (27, 53)
        c.px(x0, y, "w1"); c.px(x0 + 1, y, "w1"); c.px(x1, y, "w3"); c.px(x1 - 1, y, "w3")
    c.rect(31, 42, 33, 47, "w3"); c.hline(31, 33, 42, "w2")                           # char-right chest pocket
    c.a[39:87, 39:42, 3] = 0                                                          # open front reveals dress
    c.hline(27, 38, 87, "w3"); c.hline(42, 53, 87, "w3"); c.hline(27, 38, 88, "w4"); c.hline(42, 53, 88, "w4")

    # apron: pale grey-white half-apron from the waist, restrained botanical hem motif and ties
    ap = Ls["apron"]
    ap.rows({59: (33, 47), 60: (32, 48), **{y: (32, 48) for y in range(61, 72)},
             **{y: (31, 49) for y in range(72, 86)}}, "v2")
    for y in range(60, 86):
        x0, x1 = (32, 48) if y < 72 else (31, 49)
        ap.px(x0, y, "v1"); ap.px(x0 + 1, y, "v1"); ap.px(x1, y, "v3"); ap.px(x1 - 1, y, "v3")
    ap.hline(31, 49, 85, "v3"); ap.hline(31, 49, 86, "v3")
    ap.vline(40, 73, 82, "v3")                                                        # stem
    ap.rect(37, 76, 38, 77, "v3"); ap.rect(42, 78, 43, 79, "v3")                      # leaves
    ap.rect(38, 80, 39, 81, "v3"); ap.rect(41, 74, 42, 75, "v3")
    ap.rect(31, 59, 33, 60, "v3"); ap.rect(47, 59, 49, 60, "v3")                      # waist ties

    # belt: slim leather belt, brass buckle, small char-right medicine pouch
    bl = Ls["belt"]
    bl.rect(31, 59, 49, 62, "r2"); bl.hline(31, 49, 59, "r1"); bl.hline(31, 49, 62, "r3")
    bl.rect(38, 59, 42, 62, "y2"); bl.rect(39, 60, 41, 61, "r3"); bl.rect(39, 60, 40, 60, "y1")
    bl.rect(30, 63, 34, 68, "r2"); bl.hline(30, 34, 63, "r1"); bl.hline(30, 34, 68, "r3")
    bl.rect(31, 65, 32, 66, "y1")

    # bag: dark-red emergency bag at the character's LEFT hip (screen RIGHT), brass clasps and rolled bandage
    bg = Ls["bag"]
    bg.rect(53, 62, 64, 78, "b2")
    bg.rect(53, 62, 64, 67, "b1"); bg.hline(53, 64, 62, "b1"); bg.hline(53, 64, 67, "b3")
    bg.rect(62, 68, 64, 78, "b3"); bg.hline(53, 64, 78, "b3"); bg.hline(54, 63, 79, "b3")
    bg.rect(56, 64, 57, 65, "y2"); bg.rect(56, 64, 57, 65, "y1")                      # flap clasps
    bg.rect(61, 64, 62, 65, "y2"); bg.rect(61, 64, 62, 65, "y1")
    bg.rect(53, 59, 55, 61, "r2"); bg.rect(62, 59, 64, 61, "r2")                      # handle mounts
    bg.rect(56, 58, 61, 59, "r2"); bg.hline(56, 61, 58, "r1")                         # handle
    bg.rect(62, 70, 63, 75, "v2"); bg.hline(62, 63, 70, "v1"); bg.hline(62, 63, 71, "v3")
    bg.vline(63, 72, 74, "v3")                                                        # rolled bandage

    # strap: leather cross-body strap from char-right shoulder to the bag, brass adjuster
    st = Ls["strap"]
    for i in range(26):
        y = 35 + i
        x = 33 + (i * 22) // 25
        colour = "r1" if i % 5 == 0 else ("r3" if i % 7 == 0 else "r2")
        st.rect(x, y, x + 2, y, colour)
    st.rect(44, 48, 46, 50, "y2"); st.rect(45, 49, 46, 50, "y1")

    # arms: ivory coat sleeves, pale cuffs, dark gloves; char-left hand rests on the bag
    a = Ls["arms"]
    a.shaded(24, 37, 29, 49, "w1", "w2", "w3", 2, 2)
    a.rect(24, 50, 29, 53, "w3"); a.hline(24, 29, 50, "w2"); a.hline(24, 29, 53, "w4")
    a.shaded(25, 54, 29, 65, "k2", "k1", "k1", 1, 2)
    a.rect(26, 66, 30, 73, "k1"); a.rect(26, 66, 27, 68, "k2"); a.rect(29, 71, 30, 72, "k2")
    a.shaded(51, 38, 56, 49, "w1", "w2", "w3", 2, 2)
    a.rect(51, 50, 56, 53, "w3"); a.hline(51, 56, 50, "w2"); a.hline(51, 56, 53, "w4")
    a.shaded(51, 54, 55, 67, "k2", "k1", "k1", 1, 2)
    a.rect(52, 68, 57, 74, "k1"); a.rect(52, 68, 53, 70, "k2"); a.rect(56, 71, 57, 73, "k2")

    # herb: small green sprig at the character's right chest (screen LEFT), from the concept sheet
    hb = Ls["herb"]
    hb.vline(33, 45, 51, "n2")
    hb.rect(33, 44, 34, 45, "n1"); hb.rect(31, 46, 32, 47, "n1")
    hb.rect(34, 48, 35, 49, "n2"); hb.rect(31, 50, 32, 51, "n2")

    # face: mature oval, calm level brows, hazel eyes, nose, restrained closed-lip smile
    f = Ls["face"]
    f.rows({16: (32, 48), 17: (31, 49), **{y: (30, 50) for y in range(18, 26)},
            26: (31, 49), 27: (31, 49), 28: (32, 48), 29: (33, 47), 30: (34, 46), 31: (36, 44), 32: (37, 43)}, "s2")
    f.rect(30, 18, 32, 27, "s1"); f.rect(49, 18, 50, 28, "s3")
    f.rect(28, 21, 29, 26, "s2"); f.rect(28, 22, 28, 23, "s1"); f.rect(29, 24, 29, 25, "s3")   # ears
    f.rect(50, 21, 51, 26, "s2"); f.rect(51, 22, 51, 23, "s3"); f.rect(50, 24, 50, 25, "s3")
    f.hline(33, 37, 20, "h3"); f.hline(43, 47, 20, "h3")                              # level patient brows
    for ex in (34, 43):                                                               # calm eyes
        f.hline(ex, ex + 3, 21, "h3")
        f.rect(ex, 22, ex + 3, 23, "e1"); f.rect(ex + 1, 22, ex + 2, 23, "e2")
        f.rect(ex + 1, 22, ex + 1, 23, "h4"); f.hline(ex, ex + 3, 24, "s3")
    f.rect(40, 25, 41, 26, "s3"); f.hline(39, 41, 27, "s3")                           # nose
    f.hline(37, 42, 29, "m1"); f.px(37, 28, "m1"); f.px(42, 28, "m1")                 # restrained closed smile
    f.hline(38, 41, 30, "s3")                                                         # lower lip
    f.rect(35, 27, 35, 28, "s3"); f.rect(44, 27, 44, 28, "s3")                        # soft mature cheek lines
    f.rect(37, 31, 43, 31, "s3"); f.rect(38, 32, 42, 32, "s3")                        # chin plane
    f.rect(37, 33, 43, 36, "s3"); f.rect(38, 33, 42, 35, "s2")                        # neck under scarf

    # hair: auburn crown with upper-left sheen, side-swept fringe, loose face-framing strands
    h = Ls["hair"]
    h.rows({8: (33, 46), 9: (31, 48), 10: (29, 50), **{y: (28, 51) for y in range(11, 16)},
            16: (29, 50)}, "h2")
    h.rows({8: (35, 40), 9: (32, 38), 10: (30, 35), 11: (29, 33), 12: (29, 32)}, "h1")  # sheen
    h.rows({9: (44, 48), 10: (46, 50), **{y: (48, 51) for y in range(11, 16)}}, "h3")
    h.rows({17: (29, 36), 18: (29, 34), 19: (29, 32), 20: (29, 31)}, "h2")             # fringe, screen left
    h.rows({17: (44, 50), 18: (45, 50), 19: (46, 50), 20: (46, 49)}, "h3")             # fringe, screen right
    h.rows({21: (27, 30), 22: (27, 29), 23: (27, 30), 24: (28, 29), 25: (28, 29)}, "h2")  # loose left lock
    h.rows({21: (51, 53), 22: (51, 52), 23: (51, 52), 24: (51, 52), 25: (51, 52)}, "h3")  # loose right lock

    # braid: auburn braided coil LOW at the nape, two plaited masses below the ears with alternating bands
    br = Ls["braid"]
    left = {25: (29, 30), 26: (27, 31), 27: (26, 32), 28: (25, 33), 29: (25, 33), 30: (26, 33),
            31: (26, 33), 32: (27, 32), 33: (27, 32), 34: (28, 31), 35: (29, 31)}
    right = {25: (50, 51), 26: (49, 53), 27: (48, 54), 28: (47, 55), 29: (47, 55), 30: (48, 55),
             31: (48, 55), 32: (49, 54), 33: (49, 54), 34: (50, 53), 35: (50, 52)}
    br.rows(left, "h2"); br.rows(right, "h3")
    br.hline(27, 29, 27, "h1"); br.hline(27, 29, 31, "h1")                             # left plait bands
    br.hline(26, 28, 29, "h3"); br.hline(28, 30, 33, "h3")
    br.hline(49, 51, 27, "h2"); br.hline(49, 51, 31, "h2")                             # right plait bands
    br.hline(48, 50, 29, "h4"); br.hline(50, 52, 33, "h4")

    # scarf: cool grey-white medical scarf wound at the neck, knot char-right, long tail char-left (screen RIGHT)
    sc = Ls["scarf"]
    sc.rows({33: (34, 46), 34: (32, 48), 35: (30, 50), 36: (30, 50), 37: (32, 48), 38: (33, 47),
             39: (34, 46)}, "f1")
    sc.rect(45, 34, 48, 38, "f2"); sc.rect(47, 35, 48, 37, "f3")                      # shadow folds
    sc.rect(32, 35, 36, 38, "f2"); sc.rect(33, 35, 35, 36, "f1")                      # knot (screen LEFT)
    sc.rect(32, 39, 35, 43, "f1"); sc.rect(34, 39, 35, 43, "f2"); sc.hline(32, 35, 43, "f3")
    sc.rows({**{y: (47, 52) for y in range(38, 45)}, **{y: (48, 52) for y in range(45, 55)},
             55: (49, 52), 56: (49, 52), 57: (50, 52), 58: (50, 52), 59: (49, 51), 60: (49, 51)}, "f1")
    sc.rect(49, 39, 50, 58, "f2"); sc.rect(51, 40, 52, 57, "f3")
    sc.hline(49, 52, 61, "f3"); sc.hline(49, 52, 62, "f3")                            # fringe


def draw():
    Ls = {n: L() for n in LAYERS}
    draw_south(Ls)
    return M.finish(Ls)


# ------------------------------------------------------------------ package
def fix_pxo_metadata(pxo):
    """Male helper hardcodes its export/palette names; rewrite for Heya south, keep entry order and dates."""
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


def isolated_list(full, blobs):
    rgb = full[..., :3].astype(int); op = full[..., 3] == 255; out = []
    owner = np.full((H, W), "none", dtype=object)
    for n in LAYERS:
        if n == "guides":
            continue
        m = blobs[n][..., 3] == 255
        owner[m] = n
    for y, x in zip(*np.nonzero(op)):
        same = 0
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W and op[yy, xx] and (rgb[yy, xx] == rgb[y, x]).all():
                same += 1
        if same == 0:
            out.append({"x": int(x), "y": int(y), "owner": str(owner[y, x]),
                        "rgb": "%02x%02x%02x" % tuple(int(v) for v in full[y, x, :3])})
    counts = {}
    for row in out:
        counts[row["owner"]] = counts.get(row["owner"], 0) + 1
    return out, counts


def gates(r):
    hp, blobs, full, png, pxo, ora, pal = r
    g = M.gates(D, r)
    with zipfile.ZipFile(io.BytesIO(pxo)) as z:
        dj = z.read("data.json")
    g["pxo_no_foreign_metadata"] = all(s not in dj for s in (b"lin-que", b"milo", b"jiang", b"muxiu", b"yanke"))
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
    ys, xs = np.nonzero(al)
    g["silhouette_width"] = int(xs.max() - xs.min() + 1)
    g["silhouette_width_28_56"] = 28 <= g["silhouette_width"] <= 56
    chest = al[38:47].any(axis=0)
    g["chest_width"] = int(np.count_nonzero(chest))
    g["slim_female_chest_28_38"] = 28 <= g["chest_width"] <= 38
    # low braided coil: visible below the ears, both sides of the neck, not a high bun
    bm = blobs["braid"][..., 3] == 255
    by, bx = np.nonzero(bm)
    g["coil_low_at_nape"] = (int(bm.sum()) >= 80 and by.min() >= 24 and by.max() <= 40
                             and int((bx < 36).sum()) >= 8 and int((bx > 44).sum()) >= 8)
    g["coil_detail"] = {"texels": int(bm.sum()), "rows": [int(by.min()), int(by.max())],
                        "left": int((bx < 36).sum()), "right": int((bx > 44).sum())}
    hm = blobs["hair"][..., 3] == 255; hy, _ = np.nonzero(hm)
    g["hair_not_high_bun"] = int(hy.max()) <= 30 and int(hy.min()) >= 8
    # scarf: a real wrap plus a tail passing below the waist; only cool grey-white colours
    sm = blobs["scarf"][..., 3] == 255; sy, sx = np.nonzero(sm)
    scols = {tuple(c) for c in blobs["scarf"][sm][:, :3]}
    g["scarf_wrap_and_tail"] = (int(sm.sum()) >= 140 and int(sy.max()) >= 58 and int(sy.min()) <= 34
                                and scols <= cols(("f1", "f2", "f3")))
    g["scarf_detail"] = {"texels": int(sm.sum()), "rows": [int(sy.min()), int(sy.max())]}
    # emergency bag: dark-red mass on the character's LEFT hip (screen right), with brass hardware
    gm = blobs["bag"][..., 3] == 255; gy, gx = np.nonzero(gm)
    gcols = {tuple(c) for c in blobs["bag"][gm][:, :3]}
    brass = cols(("y1", "y2"))
    g["bag_left_hip"] = (int(gm.sum()) >= 120 and float(gx.mean()) >= 52.0
                         and bool(gcols & cols(("b1", "b2"))) and sum(tuple(c) in brass for c in gcols) >= 1)
    g["bag_detail"] = {"texels": int(gm.sum()), "mean_x": round(float(gx.mean()), 2)}
    # restrained closed-lip smile: narrow mouth, upturned corners, no teeth
    fm = blobs["face"][..., 3] == 255
    mouth = np.zeros_like(fm)
    for yy in range(27, 32):
        for xx in range(34, 46):
            if fm[yy, xx]:
                mouth[yy, xx] = bool((blobs["face"][yy, xx, :3] == S.rgb("m1")).all())
    my, mx = np.nonzero(mouth)
    teeth = any((blobs["face"][yy, xx, :3] == S.rgb("e1")).all()
                for yy in range(28, 31) for xx in range(35, 45) if fm[yy, xx])
    g["restrained_closed_smile"] = (3 <= int(mouth.sum()) <= 8 and not teeth
                                    and int(mx.max() - mx.min() + 1) <= 8)
    g["mouth_detail"] = {"texels": int(mouth.sum()), "width": int(mx.max() - mx.min() + 1),
                         "teeth_visible": bool(teeth)}
    return g


HARD = M.HARD + ["pxo_no_foreign_metadata", "palette_fits_pxo_grid_40", "isolated_texels_le_24",
                 "identity_colours_all", "anchor_layers_visible", "face_has_eye", "silhouette_width_28_56",
                 "slim_female_chest_28_38", "coil_low_at_nape", "hair_not_high_bun", "scarf_wrap_and_tail",
                 "bag_left_hip", "restrained_closed_smile"]


def manifest(files, g):
    m = {"actor_id": ACTOR, "content_id": f"content.char.{ACTOR}.static-{D}", "status": "UNAPPROVED",
         "direction": D, "pose": "idle-static", "canvas": [W, H], "pivot": list(PIN), "body_rows": list(BODY_ROWS),
         "display_scale": S.DISPLAY_SCALE, "logical_height_px": (BODY_ROWS[1] - BODY_ROWS[0] + 1) * S.DISPLAY_SCALE,
         "layers": [{"name": n, "visible": n != "guides"} for n in LAYERS],
         "face_layer_role": "mature front face, calm level brows, two hazel eyes, nose, restrained closed-lip "
                            "smile, soft cheek lines, ears, neck",
         "braid_layer_role": "auburn braided coil LOW at the nape: two plaited masses below the ears with "
                             "alternating light/dark segments; never a high bun",
         "view_notes": "front: auburn hair with upper-left sheen, side-swept fringe and loose face-framing "
                       "strands; low braided coil at the nape; cool grey-white medical scarf wound at the neck "
                       "with a knot on the character's right (screen left) and a long tail on the character's "
                       "left (screen right); ivory open clinician coat over a pale grey-white apron with a "
                       "restrained botanical hem motif and a charcoal underdress; slim leather belt with brass "
                       "buckle and small medicine pouch; dark-red emergency bag with brass clasps, leather "
                       "handle and a rolled bandage at the character's left hip (screen right), hung from a "
                       "leather cross-body strap with a brass adjuster; small green herb sprig at the "
                       "character's right chest (screen left); dark gloves; dark-brown leather boots with "
                       "folded cuffs, brass eyelets and low stacked heels",
         "authored_deviations_from_sheet": [
             "The concept sheet's white head-veil/veil is omitted because the Bible identity requires the "
             "auburn braided coil LOW at the nape to stay readable; the canonical grey-white medical scarf is "
             "worn at the neck instead.",
             "The sheet's long dark-red shawl is reduced to the canonical dark-red emergency bag on the "
             "character's left hip; the shawl silhouette is not copied.",
             "Pose: neutral front idle with both arms down; the sheet's 3/4 pose holds an herb sprig. The "
             "sprig is kept as a small chest accent.",
             "Fine embroidery, bag contents, tassels and multiple belt charms beyond the botanical hem motif, "
             "brass clasps and rolled bandage are omitted for 48 px readability."],
         "files": {k: {"file": fname(*FILE_KEYS[k]), "rawsha256": sha(b)} for k, b in files.items()},
         "colour_count": g["colour_count"], "genuine_visible_role_layers": g["genuine_visible_role_layers"],
         "isolated_texels": g["isolated_texels"], "silhouette_width": g["silhouette_width"],
         "portrait_ref": {"file": PORTRAIT_REL, "expected_sha256": PORTRAIT_SHA, "approval": "UNAPPROVED",
                          "use": "identity reference only; hues chosen by eye from point samples, no pixels copied"},
         "bible_ref": "character-26 / companion #26 Heya (赫娅), 44-year-old clinician who respects patient "
                      "bodily autonomy; restrained patient smile, auburn braided coil low at the nape, "
                      "grey-white medical scarf, dark-red emergency bag",
         "style_contract": "docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md",
         "source_contract": "reuses the Jiang/Lin/Muxiu native static contract: 80x112, pivot (40,104), body "
                            "rows 8..103, display scale 0.5 = 48 logical px, binary alpha, transparent border, "
                            "declared palette 24..48 used colours, >=8 genuine role layers, hidden guides layer",
         "replaces_placeholder": "does not modify the old 32x48 native-animation placeholder; it is not counted",
         "author_tool": "tools/" + os.path.basename(__file__), "reused_tool_pins": PINS,
         "serialization_helper": S.HELPER_REL,
         "pixel_source": "code-authored native pixels, declared palette",
         "limitations": "south static only; no runtime wiring, no other directions, no motion, no GUI "
                        "save/reopen proof and no creator art approval"}
    return (json.dumps(m, indent=2) + "\n").encode()


def check_r2(r1, r2):
    return all(a == b for a, b in zip(r1[3:], r2[3:]))


def write_files(root_rel, named):
    written = {}
    for rel, data in named.items():
        p = fs(f"{root_rel}/{os.path.basename(rel)}")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if os.path.exists(p) and open(p, "rb").read() != data:
            raise SystemExit(f"refusing to overwrite different bytes: {root_rel}/{os.path.basename(rel)}")
        open(p, "wb").write(data)
        written[f"{root_rel}/{os.path.basename(rel)}"] = sha(data)
    open(fs(root_rel + "/.gdignore"), "ab").close()
    return written


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    r1, r2 = artifacts(), artifacts()
    g = gates(r1)
    g["deterministic_rebuild"] = check_r2(r1, r2)
    bad = [k for k in HARD + ["deterministic_rebuild"] if not g[k]]
    bad += [f"tool_pin:{rel}" for rel, ok in PIN_OK.items() if not ok]
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
        written = write_files(STAGE_REL, named)
        listing = {"staged": written,
                   "qa_preview_nonsource": {rel: sha(open(fs(rel), "rb").read()) for rel in previews},
                   "hash": "sha256 of raw bytes, no normalization"}
        lp = f"{QA_REL}/{SLUG}_{ACTOR}_{D}-staging-output-paths-rawhashes_unapproved-v01_{STAMP}-{uid('paths')}.json"
        open(fs(lp), "wb").write((json.dumps(listing, indent=2) + "\n").encode())
    if cmd == "install":
        if bad:
            raise SystemExit(f"hard gates failed: {bad}")
        # staging must already exist and match the freshly rebuilt bytes exactly
        for rel, data in named.items():
            sp = fs(rel)
            if not os.path.exists(sp) or open(sp, "rb").read() != data:
                raise SystemExit(f"staging missing or stale: {rel}; run build first")
        os.makedirs(fs(OUT_REL), exist_ok=True)
        for rel, data in named.items():
            dst = f"{OUT_REL}/{os.path.basename(rel)}"; dp = fs(dst)
            if os.path.exists(dp) and open(dp, "rb").read() != data:
                subprocess.run([sys.executable, "tools/wb_safe_replace.py", rel, dst], cwd=REPO, check=True)
            else:
                open(dp, "wb").write(data)
        open(fs(OUT_REL + "/.gdignore"), "ab").close()
    disk = {}
    for rel, data in named.items():
        sr = f"{STAGE_REL}/{os.path.basename(rel)}"
        ir = f"{OUT_REL}/{os.path.basename(rel)}"
        disk["stage:" + sr] = (sha(open(fs(sr), "rb").read()) == sha(data)) if os.path.exists(fs(sr)) else None
        disk["install:" + ir] = (sha(open(fs(ir), "rb").read()) == sha(data)) if os.path.exists(fs(ir)) else None
    report = {k: g[k] for k in ("body_rows", "colour_count", "genuine_visible_role_layers", "visible_role_texels",
                                "isolated_texels", "silhouette_width", "chest_width", "identity_colours_visible",
                                "coil_detail", "scarf_detail", "bag_detail", "mouth_detail", "binary_alpha",
                                "no_opaque_border", "pin_inside_feet_span", "all_colours_declared", "ora_hidden",
                                "deterministic_rebuild")}
    report.update({k: g[k] for k in ("coil_low_at_nape", "hair_not_high_bun", "scarf_wrap_and_tail",
                                     "bag_left_hip", "restrained_closed_smile", "slim_female_chest_28_38",
                                     "silhouette_width_28_56")})
    report.update(tool_pins_ok=PIN_OK, disk_matches_rebuild=disk, hard_failures=bad)
    if not g["isolated_texels_le_24"]:
        report["isolated_positions"], report["isolated_by_layer"] = isolated_list(r1[2], r1[1])
    print(json.dumps(report, indent=1))
    stage_ok = all(v is True for k, v in disk.items() if k.startswith("stage:"))
    ok = not bad and stage_ok and all(v is not False for v in disk.values())
    print("HEYA_SOUTH_V01_" + ("ALL_OK" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
