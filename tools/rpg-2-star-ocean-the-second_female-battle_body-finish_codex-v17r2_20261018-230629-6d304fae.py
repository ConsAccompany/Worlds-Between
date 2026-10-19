"""UNAPPROVED v17r2: one static still - body finishing over the frozen v17r1 face.

One deliberate authoring pass on the body: coat lapel / shoulder / underarm /
waist / skirt / tail planes with a few coherent folds, boot cuff / ankle / strap
/ heel / toe cap / welt, glove knuckles, thumb and finger creases, quieter pack
and canister. Frozen and gated: the v17r1 face and hair (composite rows 0-44 and
the head / ponytail / loose-lock / hair-tie layers), soles + pin + padding
(rows 132-143), blade and guard layers, cell, pin, logical extent, palette keys
and figure bounds. One frame only; no animation; no game source or default.

Reuses the v17r1 author (layers, raster, outline pass, ORA writer) and the
established south-run v06 .pxo writer. No resampling, filtering, dithering,
noise or image generation. The x4 inspection PNG is for viewing only; actual
1280 game captures are separate evidence.

Modes (python -I -B <this> ...):
  preview <dir>            write the package to a scratch folder outside the repo
  build                    write outputs/battle-static-v17r2 (refuses to replace different bytes)
  check [--write-report]   technical gates, evaluated on the built files' bytes
  native                   Pixelorama 1.2.3 headless re-open + layer export of the .pxo and .ora
                           under a fresh APPDATA/LOCALAPPDATA (never the user's editor); one report
"""
from pathlib import Path
import hashlib, importlib.util, io, json, os, subprocess, sys, tempfile, zipfile
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = "tools/rpg-2-star-ocean-the-second_female-battle-static_dense-author_unapproved-v17r1_20261018-224310-2fa4fe00.py"
WRITER = "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py"
R1_DIR = "outputs/battle-static-v17r1/"
BASE_PNG = R1_DIR + "rpg-2-star-ocean-the-second_female-battle-idle-right_dense-native136_unapproved-v17r1_20261018-224310-6e037d3b.png"
BASE_SHA = "06c2927fb170d48b5da794c23cbeab87772010960272d7f4b15f87908016815e"
R1_ORA = R1_DIR + "rpg-2-star-ocean-the-second_female-battle-idle-right_dense-layers_unapproved-v17r1_20261018-224310-46ab885c.ora"
R1_ORA_SHA = "ab731ba413342a76c17e759c742f12af44197ac28047b80c942ea27ed1f67bfc"
R1_HEAD = R1_DIR + "rpg-2-star-ocean-the-second_female-battle-idle-right_dense-head-native_unapproved-v17r1_20261018-224310-881b8d93.png"
R1_HEAD_SHA = "83b046192a0dbbfaf12da45f6f1fc7655a0c4ca9e05b9bd91726677961860acd"
PIXELORAMA = ROOT / "../tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"
STAMP, UID = "20261018-230629", "6d304fae"
PREFIX = "rpg-2-star-ocean-the-second_female-battle"
OUT = ROOT / "outputs/battle-static-v17r2"
W, H = 136, 144
PIN = (64, 136)
PROTECTED_ROWS = 45                      # composite rows 0-44: v17r1 face, hair, ponytail, tie
SOLE_ROW = 132                           # composite rows 132-143: soles, pin, padding
FACE_CROP = (52, 12, 96, 45)             # = the v17r1 head PNG box (52,12,96,48) minus its 3 body rows
HAIR_LAYERS = ("head", "ponytail", "loose-lock", "hair-tie")
FROZEN_LAYERS = HAIR_LAYERS + ("hip-drape", "bedroll", "far-leg", "belt", "collar", "scarf-lower-wrap",
                               "scarf-upper-wrap", "scarf-knot", "sword-blade", "sword-guard")
SILHOUETTE_ZONES = [(40, 112, 101, 132), (84, 51, 98, 65)]   # boots, hands: the only places opacity may change


def long(p):
    return Path("\\\\?\\" + str(Path(p).resolve()))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_text(p):
    return sha(long(p).read_bytes().replace(b"\r\n", b"\n"))


def module(rel, name):
    spec = importlib.util.spec_from_file_location(name, long(ROOT / rel))
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def name(role, suffix):
    key = sha((UID + ":" + role).encode())[:8]
    return f"{PREFIX}_{role}_unapproved-v17r2_{STAMP}-{key}.{suffix}"


def decode(data):
    return np.array(Image.open(io.BytesIO(data)).convert("RGBA"))


def fold(layer, key, pts, width=1):
    """A fold/seam/hem line that only recolours texels the cloth layer already owns (no new silhouette)."""
    for p in layer._mask(lambda d: d.line(pts, fill=1, width=width)):
        if p in layer.px:
            layer.px[p] = key


def author():
    a = module(BASE, "frozen_face_source")
    before_layers, before = a.render()
    assert sha(a.png_bytes(before)) == BASE_SHA
    layers = {x.name: x for x in a.LAYERS}
    # One deliberate body pass. Light stays upper-right (front/top lit, back and
    # underside in shadow). Only existing palette keys; planes, a few coherent
    # folds and seams, no texture speckle. Rows 0-44 (face, hair, ponytail, tie)
    # and rows 132+ (soles, floor, pin) are frozen and asserted below.

    # ---- coat torso: the sleeve must separate from the body behind it.
    coat = layers["coat"]
    coat.shade("e", [(61, 67), (77, 67), (77, 70), (61, 71)])      # underarm cast shadow
    fold(coat, "C", [(61, 68), (66, 68)])
    coat.shade("c", [(56, 45), (61, 45), (61, 53), (58, 56), (56, 52)])   # shoulder blade
    coat.shade("C", [(53, 66), (57, 66), (57, 78), (53, 78)])             # waist turns away
    coat.shade("o", [(73, 67), (76, 67), (76, 78), (73, 78)])      # lapel face toward the light
    fold(coat, "e", [(72, 68), (72, 78)])                           # lapel shadow on the coat
    fold(coat, "O", [(76, 67), (76, 78)])                           # lapel rim
    fold(coat, "e", [(64, 71), (66, 75)])                           # two waist gathers into the belt
    fold(coat, "e", [(68, 71), (69, 75)])
    fold(coat, "o", [(69, 71), (70, 74)])
    # ---- front skirt: shadow side, two flaring folds, lit leading panel.
    coat.shade("e", [(64, 79), (67, 79), (67, 96), (64, 96)])
    for pt in [p for p in coat.px if p[1] >= 79 and coat.px[p] == "e" and p[0] > 67]:
        coat.px[pt] = "c"                                          # drop the old ruler-straight fold lines
    fold(coat, "e", [(71, 80), (70, 86), (69, 95)])
    fold(coat, "o", [(72, 84), (71, 93)])
    fold(coat, "e", [(79, 81), (79, 88), (78, 96)])
    fold(coat, "o", [(80, 86), (80, 94)])
    coat.shade("o", [(85, 80), (91, 79), (93, 85), (93, 92), (87, 94), (86, 86)])
    fold(coat, "O", [(91, 80), (93, 86), (93, 91)])
    fold(coat, "c", [(86, 86), (86, 93)])
    fold(coat, "C", [(74, 95), (85, 94)])                           # hem turns under
    fold(coat, "l", [(65, 95), (73, 97), (86, 96), (93, 92)])       # v17r1 leather binding path
    # ---- back tail: upper surface catches light, one long ridge, deep valley.
    tail = layers["coat-tail"]
    tail.shade("e", [(36, 78), (65, 78), (65, 112), (36, 112)])
    tail.shade("c", [(53, 78), (65, 78), (65, 91), (61, 101), (57, 101), (60, 89), (56, 80)])
    fold(tail, "o", [(61, 80), (63, 86)])
    fold(tail, "c", [(54, 84), (49, 95), (44, 105)], width=2)
    fold(tail, "C", [(52, 82), (46, 95), (41, 104), (40, 107)])
    fold(tail, "C", [(58, 92), (54, 103)])
    tail.shade("C", [(36, 100), (41, 96), (39, 104), (36, 109)])
    fold(tail, "l", [(36, 109), (44, 111), (52, 108), (59, 104)])
    fold(tail, "c", [(45, 110), (51, 108)])
    # ---- shirt: forearm/hand cast shadow, side plane, blouse over the belt.
    shirt = layers["shirt"]
    for pt in [p for p in shirt.px if p[1] >= 64 and shirt.px[p] in "fw" and p[0] > 80]:
        shirt.px[pt] = "W"
    shirt.shade("w", [(78, 64), (90, 64), (90, 65), (78, 66)])
    shirt.shade("w", [(78, 66), (80, 66), (80, 76), (78, 76)])
    fold(shirt, "w", [(84, 67), (83, 74)])
    fold(shirt, "f", [(83, 72), (83, 74)])
    fold(shirt, "w", [(87, 71), (87, 74)])
    fold(shirt, "w", [(81, 73), (89, 74)])
    # ---- sleeve: lit top-right plane, two elbow creases, underside, calmer cuff.
    arm = layers["near-arm"]
    arm.shade("c", [(66, 56), (74, 56), (74, 64), (66, 64)])
    arm.shade("o", [(71, 52), (75, 52), (75, 58), (73, 60), (71, 57)])
    fold(arm, "e", [(66, 59), (71, 62)])
    fold(arm, "e", [(66, 63), (70, 65)])
    arm.shade("e", [(64, 65), (75, 65), (75, 66), (64, 66)])
    arm.shade("P", [(75, 57), (82, 56), (82, 60), (75, 60)])
    arm.shade("p", [(75, 61), (82, 61), (82, 67), (75, 67)])
    layers["near-leg"].shade("v", [(89, 102), (90, 102), (89, 110), (88, 110)])
    # ---- boots: rolled cuff, Achilles/ankle, strap, heel counter, toe cap,
    # lit vamp and welt bevel. Rows 132-135 (soles) stay exactly as they were.
    boots = {
        "near-boot": [
            (112, 77, "KlnnDDDDNNNDdK"),
            (113, 77, "KLdnnnnnnDDDdK"),
            (114, 77, "KLdnnnnnnnDDdK"),
            (115, 77, "KLLddddddnnndK"),
            (116, 77, "_KLLLLLLLLLLK_"),
            (117, 78, "KLdddddnnnDK"),
            (118, 78, "KLLLLLLMmLLK"),
            (119, 78, "KLddnnnnnDDK"),
            (120, 78, "KLddnnnnnDDK"),
            (121, 77, "KLLddnnnnnDDNK"),
            (122, 77, "KLLddnnnnnnDDDNK"),
            (123, 77, "KLLdddnnnnnnDDDNK"),
            (124, 76, "KLLddd" + "n" * 10 + "lDNK"),
            (125, 76, "KLLddd" + "n" * 9 + "lDDNNK"),
            (126, 75, "KLLdddd" + "n" * 8 + "lDDDDNNK"),
            (127, 75, "KLLdddd" + "n" * 8 + "lDDDDDNNK"),
            (128, 74, "KLLLdddd" + "n" * 9 + "lDDDDDNK"),
            (129, 74, "KLLLddddd" + "n" * 9 + "lDDDDDNK"),
            (130, 74, "KLLL" + "d" * 19 + "nDK"),
            (131, 74, "KLLL" + "n" * 20 + "DK"),
        ],
        "far-boot": [
            (112, 47, "KldnnnnnnnDDdK"),
            (113, 47, "KLddnnnnnnnDdK"),
            (114, 47, "KLdddnnnnnnndK"),
            (115, 47, "KLLddddddddddK"),
            (116, 47, "_KLLLLLLLLLLK_"),
            (117, 48, "KLddddddnnnK"),
            (118, 48, "KLLLLLLmzLLK"),
            (119, 48, "KLdddddnnnnK"),
            (120, 48, "KLdddddnnnnK"),
            (121, 47, "KLLddddddnnnK"),
            (122, 46, "KLLdddddddnnnDK"),
            (123, 45, "KLLddddddddnnnDK"),
            (124, 44, "KLLLddddddddnnlDNK"),
            (125, 43, "KLLLddddddddnnlDDNK"),
            (126, 43, "KLLLdddddddnnlDDDDNK"),
            (127, 42, "KLLLLdddddddnnlDDDDNK"),
            (128, 42, "KLLLLddddddddnnlDDDDK"),
            (129, 41, "KLLLLddddddddddnnlDDDDK"),
            (130, 41, "KLLL" + "d" * 17 + "nK"),
            (131, 41, "KLLL" + "l" * 17 + "nK"),
        ],
    }
    for key, rows in boots.items():
        boot = layers[key]
        for pt in [p for p in boot.px if 112 <= p[1] <= 131]:
            del boot.px[pt]
        boot.rows(rows)
    # ---- gloves: back-of-hand leather with a knuckle crest, a thumb pressed
    # along the grip toward the guard, two finger creases per fist.
    hands = layers["hands"]
    hands.px.clear()
    hands.paint(85, 52, """
..KKKKKK....
.KldDNNSK...
KLlDDDNjSSK.
KLllDDlxsSSK
KLLllllsSSxK
.KLLLlxxxxK.
KLlDDNlsSsK.
KLlDDDlsSxK.
KLLlllxxxK..
KLLLllsSsK..
.KLLLlsxsK..
..KKKKKKK...
""")
    # ---- quiet carried gear so the face and chest lead.
    pack = layers["pack"]
    for pt, color in list(pack.px.items()):
        if color == "P":
            pack.px[pt] = "p"
        elif color == "N" and pt[1] >= 55:
            pack.px[pt] = "D"
    can = layers["canister"]
    for pt, color in list(can.px.items()):
        if color == "Z":
            can.px[pt] = "M"
        elif color == "M" and pt[1] > 61:
            can.px[pt] = "z"
    grids, comp = a.compose()
    return a, grids, comp, a.to_rgba(comp), before_layers, before


def outputs():
    a, grids, comp, full, before_layers, before = author()
    rgba = {k: a.to_rgba(v) for k, v in grids.items()}
    rgba["outline"] = a.to_rgba(a.outline_layer(grids, comp))
    order = [x.name for x in a.LAYERS] + ["outline"]
    writer = module(WRITER, "established_pxo_writer")
    writer.W, writer.H = W, H
    writer.to_rgba = lambda im: np.ascontiguousarray(im, np.uint8)
    png = a.png_bytes(full)
    x0, y0, x1, y1 = FACE_CROP
    files = {
        "png": (name("still-native136", "png"), png),
        "face": (name("face-hair-native", "png"), a.png_bytes(np.ascontiguousarray(full[y0:y1, x0:x1]))),
        "ora": (name("still-layered", "ora"), a.ora_bytes(grids, comp)),
        "pxo": (name("still-editable", "pxo"), writer.make_pxo(
            [rgba], [1.0], png, name("still-source-export", "png"), 8, order=order, dt=(2026, 10, 18, 23, 6, 28))),
    }
    buf = io.BytesIO()
    a.on_bg(full, (120, 130, 140), 4).save(buf, "PNG")
    files["inspect"] = (name("body-inspection-x4", "png"), buf.getvalue())
    changed = (full != before).any(axis=2)
    yy, xx = np.nonzero(changed)
    manifest = {
        "status": "UNAPPROVED one static still: body finishing over the frozen v17r1 face/hair. Not art approval, "
                  "not runtime adoption, no animation, no default or game-source change.",
        "standingCreatorRejection": "way too coarse, face not even recognizable (v16, 2026-10-18)",
        "cell": [W, H], "logicalExtent": [68, 72], "pinNative": list(PIN), "pinLogical": [32, 68],
        "displayRequirement": "draw_texture_rect(texture, Rect2(round(x)-32, 204, 68, 72)), nearest; identical to v17/v17r1",
        "frozen": {"compositeRows": [0, PROTECTED_ROWS - 1], "soleRows": [SOLE_ROW, H - 1],
                   "layersByteIdenticalToV17r1": list(FROZEN_LAYERS), "faceHairCrop": list(FACE_CROP)},
        "layers": order, "frameCount": 1,
        "changedTexelsVsV17r1": int(changed.sum()),
        "changedNativeBounds": [int(xx.min()), int(yy.min()), int(xx.max()), int(yy.max())],
        "inputs": {BASE: {"sha256TextLf": sha_text(ROOT / BASE)}, BASE_PNG: {"sha256": BASE_SHA},
                   R1_ORA: {"sha256": R1_ORA_SHA}, R1_HEAD: {"sha256": R1_HEAD_SHA},
                   WRITER: {"sha256TextLf": sha_text(ROOT / WRITER)}},
        "source": {"file": str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"),
                   "sha256TextLf": sha_text(__file__)},
        "files": {role: {"name": n, "sha256": sha(b)} for role, (n, b) in files.items()},
        "inspectionNote": "body-inspection-x4 is a nearest x4 view on flat grey for viewing only; it is not runtime art",
        "artApproved": False, "animationMade": False, "runtimeDefaultChanged": False, "gameSourceChanged": False,
        "pxoWriter": "established south-run v06 make_pxo (Pixelorama v1.2.3 pxo_version 7 layout); raw cels are gated",
        "guiSaveAsVerified": False,
        "limits": ["native 640x360 path samples 1 of 4 native texels; thin lines and sub-logical planes break up",
                   "normal four-person layout: companion draws still cover part of the blade/hands area (later-draw "
                   "matte measured separately)",
                   "technical equality and gates are not artistic acceptance"],
    }
    files["manifest"] = (name("source-manifest", "json"), (json.dumps(manifest, indent=1) + "\n").encode())
    return files, order


def largest_flat(keys, mask):
    """Largest 4-connected run of one palette colour inside mask (coarseness indicator, reported only)."""
    seen = np.zeros(mask.shape, bool)
    best = (0, "")
    for y, x in zip(*np.nonzero(mask)):
        if seen[y, x]:
            continue
        k, stack, n = keys[y, x], [(y, x)], 0
        seen[y, x] = True
        while stack:
            cy, cx = stack.pop()
            n += 1
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx] and keys[ny, nx] == k:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        best = max(best, (n, k))
    return {"texels": best[0], "key": best[1]}


def gates(files, order):
    """Every gate is evaluated on file bytes (built or on disk), independent of the authoring path."""
    out = []

    def gate(label, ok, detail=None):
        out.append({"gate": label, "pass": bool(ok), "detail": detail})

    a = module(BASE, "frozen_face_reference")
    pal = {tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)): k for k, v in a.PALETTE.items()}
    r1_png_b, r1_ora_b, r1_head_b = (long(ROOT / p).read_bytes() for p in (BASE_PNG, R1_ORA, R1_HEAD))
    gate("v17r1 inputs present and sha-pinned (native PNG, layered ORA, head PNG)",
         (sha(r1_png_b), sha(r1_ora_b), sha(r1_head_b)) == (BASE_SHA, R1_ORA_SHA, R1_HEAD_SHA))
    r1, png = decode(r1_png_b), decode(files["png"][1])
    op, op1 = png[..., 3] == 255, r1[..., 3] == 255

    def keys_of(img):
        k = np.full((H, W), "", "<U1")
        for c, key in pal.items():
            k[(img[..., 3] == 255) & (img[..., :3] == c).all(axis=2)] = key
        return k
    k2, k1 = keys_of(png), keys_of(r1)
    gate("cell 136x144, binary alpha", png.shape == (H, W, 4) and set(np.unique(png[..., 3]).tolist()) <= {0, 255},
         list(png.shape))
    off = sorted({tuple(c) for c in png[op][:, :3].tolist()} - set(pal))
    used = sorted(set(k2[op].tolist()))
    gate("every opaque texel is a v17r1 palette colour (no new colour), <= 48 used", not off and len(used) <= 48,
         {"used": len(used), "keys": "".join(used), "offPalette": off[:5],
          "v17r1Used": len(set(k1[op1].tolist()))})
    pad = np.pad(op, 1, constant_values=False)
    edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    gate("silhouette edge is outline K or deep skin profile k only (no rim/neon/halo)",
         set(k2[edge].tolist()) <= {"K", "k"}, sorted(set(k2[edge].tolist())))
    p = PROTECTED_ROWS
    gate(f"face/hair protected rows 0-{p - 1}: composite byte-identical to v17r1 (incl. outline pass)",
         np.array_equal(png[:p], r1[:p]), int((png[:p] != r1[:p]).any(axis=2).sum()))
    x0, y0, x1, y1 = FACE_CROP
    face = decode(files["face"][1])
    gate("separate face/hair PNG = composite crop and = the v17r1 head PNG minus its 3 body rows",
         np.array_equal(face, png[y0:y1, x0:x1]) and np.array_equal(face, decode(r1_head_b)[:y1 - y0]),
         list(FACE_CROP))
    gate(f"soles, pin and padding rows {SOLE_ROW}-{H - 1} byte-identical to v17r1",
         np.array_equal(png[SOLE_ROW:], r1[SOLE_ROW:]), int((png[SOLE_ROW:] != r1[SOLE_ROW:]).any(axis=2).sum()))
    xs135 = np.nonzero(op[135])[0]
    gate("pin (64,136) transparent; rows 136+ clear; feet either side of x64 on row 135",
         not op[136:].any() and not op[135, 64] and (xs135 < 64).any() and (xs135 > 64).any())
    ys, xs = np.nonzero(op)
    ys1, xs1 = np.nonzero(op1)
    bb2 = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    bb1 = [int(xs1.min()), int(ys1.min()), int(xs1.max()), int(ys1.max())]
    gate("figure bounds identical to v17r1 (logical extent, blade endpoint, apparent proportion)", bb2 == bb1,
         {"v17r2": bb2, "v17r1": bb1})
    sil = op != op1
    allowed = np.zeros((H, W), bool)
    for zx0, zy0, zx1, zy1 in SILHOUETTE_ZONES:
        allowed[zy0:zy1, zx0:zx1] = True
    gate("opacity changes only inside the boot and glove zones (no new silhouette clutter elsewhere)",
         not (sil & ~allowed).any(), {"opacityChanged": int(sil.sum()), "outsideZones": int((sil & ~allowed).sum()),
                                      "opaqueTexels": [int(op1.sum()), int(op.sum())], "zones": SILHOUETTE_ZONES})
    blocks = png.reshape(H // 2, 2, W // 2, 2, 4).transpose(0, 2, 1, 3, 4).reshape(H // 2, W // 2, 4, 4)
    full2 = (blocks[..., 3] == 255).all(axis=2)
    non = (blocks[..., :3] != blocks[:, :, :1, :3]).any(axis=(2, 3))
    gate("native density kept: >= 25% of fully opaque 2x2 blocks carry sub-logical detail",
         (full2 & non).sum() >= 0.25 * full2.sum(), {"blocks": int(full2.sum()), "nonUniform": int((full2 & non).sum())})
    # ORA: same layer names/order as v17r1, frozen layers byte-identical, stack and merged image = PNG.
    z, z1 = zipfile.ZipFile(io.BytesIO(files["ora"][1])), zipfile.ZipFile(io.BytesIO(r1_ora_b))
    lf = sorted(n for n in z.namelist() if n.startswith("data/"))
    lf1 = sorted(n for n in z1.namelist() if n.startswith("data/"))
    gate("ORA mimetype first; layer files, names and order identical to v17r1",
         z.namelist()[0] == "mimetype" and z.read("mimetype") == b"image/openraster" and lf == lf1
         and [f.split("-", 1)[1][:-4] for f in lf] == order, len(lf))
    stack = np.zeros((H, W, 4), np.uint8)
    for n in lf:
        layer = decode(z.read(n))
        stack[layer[..., 3] == 255] = layer[layer[..., 3] == 255]
    gate("ORA layers stacked bottom->top and ORA mergedimage both equal the native PNG",
         np.array_equal(stack, png) and np.array_equal(decode(z.read("mergedimage.png")), png))
    changed_layers = {f.split("-", 1)[1][:-4]: int((decode(z.read(f)) != decode(z1.read(f))).any(axis=2).sum())
                      for f in lf}
    frozen_bad = {k: changed_layers[k] for k in FROZEN_LAYERS if changed_layers[k]}
    gate("frozen layers (hair, face, tie, drape, bedroll, far leg, belt, collar, scarf, blade, guard) identical "
         "to v17r1 layers", not frozen_bad, frozen_bad)
    o = next(f for f in lf if f.endswith("-outline.png"))
    od = (decode(z.read(o)) != decode(z1.read(o))).any(axis=2)
    gate(f"outline reconciliation only outside the protected face/hair rows (0-{p - 1})", not od[:p].any(),
         {"outlineTexelsChanged": int(od.sum()), "insideProtectedRows": int(od[:p].sum())})
    # PXO: one frame, same layers, raw cels equal the ORA layers, cel stack and preview equal the PNG.
    zp = zipfile.ZipFile(io.BytesIO(files["pxo"][1]))
    doc = json.loads(zp.read("data.json"))
    cels_ok, pstack = True, Image.new("RGBA", (W, H))
    for i, n in enumerate(lf, 1):
        raw = zp.read(f"image_data/frames/1/layer_{i}")
        cels_ok &= raw == decode(z.read(n)).tobytes()
        pstack.alpha_composite(Image.frombytes("RGBA", (W, H), raw))
    gate("PXO: pixelorama mimetype, 136x144, exactly 1 frame, layer names/order = ORA",
         zp.read("mimetype") == b"application/x-pixelorama" and (doc["size_x"], doc["size_y"]) == (W, H)
         and len(doc["frames"]) == 1 and [l["name"] for l in doc["layers"]] == order)
    gate("PXO raw cels byte-equal the ORA layer pixels; cel stack and preview.png equal the native PNG",
         cels_ok and np.array_equal(np.array(pstack), png) and np.array_equal(decode(zp.read("preview.png")), png))
    body = np.zeros((H, W), bool)
    body[p:SOLE_ROW] = True
    info = {"largestFlatBodyRun": {"v17r1": largest_flat(k1, op1 & body), "v17r2": largest_flat(k2, op & body)},
            "bodyDistinctKeys": {"v17r1": len(set(k1[op1 & body].tolist())), "v17r2": len(set(k2[op & body].tolist()))},
            "changedLayersTexels": {k: v for k, v in changed_layers.items() if v},
            "changedTexels": int((png != r1).any(axis=2).sum())}
    return out, info


def native():
    """Pixelorama's own re-open + layer export (distinct from a GUI Save As, which is not done here)."""
    files, order = outputs()
    for role in ("pxo", "ora"):
        assert long(OUT / files[role][0]).read_bytes() == files[role][1], "build first; check the frozen files"
    exe = PIXELORAMA.resolve()
    tmp = Path(tempfile.mkdtemp(prefix="v17r2px-"))
    za = zipfile.ZipFile(io.BytesIO(files["ora"][1]))
    expect = {f.split("-", 1)[1][:-4]: decode(za.read(f)) for f in sorted(n for n in za.namelist() if n.startswith("data/"))}
    report = {"status": "Pixelorama native re-open/export of the frozen v17r2 sources; not a GUI Save As; "
                        "not art approval", "executable": str(exe), "executableSha256": sha(exe.read_bytes()),
              "tempRoot": str(tmp), "runs": {}}
    for role in ("pxo", "ora"):
        folder = tmp / role
        (folder / "app").mkdir(parents=True)
        (folder / "local").mkdir()
        (folder / "exp").mkdir()
        src = folder / files[role][0]
        src.write_bytes(files[role][1])
        env = dict(os.environ, APPDATA=str(folder / "app"), LOCALAPPDATA=str(folder / "local"))
        target = folder / "exp" / f"v17r2-{role}.png"
        cmd = [str(exe), "--headless", "--quit", "--", "--export", "--split-layers", "-o", str(target), str(src)]
        proc = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=120, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        exported = sorted((folder / "exp").glob("*.png"))
        layers = {}
        for lname, want in expect.items():
            hits = [q for q in exported if f"({lname})" in q.name]
            layers[lname] = len(hits) == 1 and np.array_equal(np.array(Image.open(hits[0]).convert("RGBA")), want)
        text = proc.stdout + proc.stderr
        diag = [ln for ln in text.splitlines() if any(t in ln for t in ("ERROR", "SCRIPT ERROR", "WARNING", "Shader"))]
        report["runs"][role] = {
            "exit": proc.returncode, "exportedPngs": len(exported), "exportedNames": [q.name for q in exported],
            "layersExact": layers, "allLayersExact": len(exported) == len(expect) and all(layers.values()),
            "sourceUnchanged": src.read_bytes() == files[role][1], "diagnosticLines": diag,
            "cleanApp": proc.returncode == 0 and not diag, "stdout": proc.stdout, "stderr": proc.stderr}
    report["nativeExactExport"] = all(r["exit"] == 0 and r["allLayersExact"] and r["sourceUnchanged"]
                                      for r in report["runs"].values())
    report["cleanApp"] = all(r["cleanApp"] for r in report["runs"].values())
    path = long(OUT / name("pixelorama-native-report", "json"))
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(report, indent=1) + "\n")
    print(json.dumps({k: report[k] for k in ("nativeExactExport", "cleanApp")}),
          {r: (v["exit"], v["exportedPngs"], len(v["diagnosticLines"])) for r, v in report["runs"].items()})
    print("BATTLE_BODY_R2_NATIVE", "EXACT" if report["nativeExactExport"] else "NOT_EXACT",
          "CLEAN" if report["cleanApp"] else "DIAGNOSTICS")
    return 0 if report["nativeExactExport"] else 1


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "native":
        sys.exit(native())
    files, order = outputs()
    again, _ = outputs()
    deterministic = {r: v[1] for r, v in files.items()} == {r: v[1] for r, v in again.items()}
    results, info = gates(files, order)
    results.insert(0, {"gate": "deterministic rebuild (two independent authoring passes, identical bytes)",
                       "pass": deterministic, "detail": None})
    ok = all(g["pass"] for g in results)
    if mode in ("preview", "build"):
        if not ok:
            print(json.dumps([g for g in results if not g["pass"]], indent=1))
            sys.exit("GATES FAIL: nothing written")
        target = Path(sys.argv[2]) if mode == "preview" else OUT
        long(target).mkdir(parents=True, exist_ok=True)
        for fname, data in files.values():
            fp = long(target / fname)
            if fp.exists():
                assert fp.read_bytes() == data, f"refuse to replace a frozen output {fname}"
            else:
                fp.write_bytes(data)
        print("WROTE", target, len(files), "files")
    elif mode == "check":
        disk = {r: (n, long(OUT / n).read_bytes() if long(OUT / n).exists() else None) for r, (n, _) in files.items()}
        same = {r: disk[r][1] == files[r][1] for r in files}
        results.insert(1, {"gate": "every built file on disk equals this tool's deterministic output", "pass": all(same.values()),
                           "detail": same})
        if all(same.values()):
            disk_results, _ = gates(disk, order)
            results.insert(2, {"gate": "all content gates re-evaluated on the on-disk bytes", "pass":
                               all(g["pass"] for g in disk_results), "detail": len(disk_results)})
        ok = all(g["pass"] for g in results)
    report = {"status": "UNAPPROVED v17r2 still technical check; not art approval", "pass": ok,
              "passed": sum(g["pass"] for g in results), "total": len(results), "gates": results, "info": info,
              "files": {r: {"name": n, "sha256": sha(b)} for r, (n, b) in files.items()},
              "tool": {"file": str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"),
                       "sha256TextLf": sha_text(__file__)}}
    print(json.dumps(report, indent=1))
    if mode == "check" and "--write-report" in sys.argv:
        data = (json.dumps(report, indent=1) + "\n").encode()
        fp = long(OUT / name("check-report", "json"))
        if fp.exists():
            assert fp.read_bytes() == data, "refuse to replace a different check report"
        else:
            fp.write_bytes(data)
    print("BATTLE_BODY_R2", mode.upper(), "PASS" if ok else "FAIL", f"{report['passed']}/{report['total']}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
