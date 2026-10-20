"""Sea of Stars heroine battle static v01: deterministic native conversion + curation of a GENERATED input.

Method change from v17/v17r2 (procedural texel authoring, rejected): the Codex-selected generated key pose is the
production input. It is high-resolution pixel-LOOKING art with an irregular generator grid (FFT pitch ~8.0-8.9 src px,
not a clean integer grid), so it is NOT native pixel art. This tool resamples it ONCE onto the existing native
136x144 battle cell (same logical 68x72 extent, pin 64,136 native = 32,68 logical) at the v17r2 occupied height
(rows 3..135 = 133 rows), then curates: fixed palette, cell-mode sampling, stray-alpha and speckle removal.
Nothing is hand-painted; the whole still is generated+curated. Layers are MASK SLICES of the one flattened still
(hair/head/body/scarf/weapon/legs); no part has hidden pixels painted behind another.

    build    write native PNG, PXO, ORA, x4 inspection view and manifest to outputs/hero-sea-v01
    check    rebuild in memory, require byte-identical files on disk + gates (default)
    native   Pixelorama 1.2.3 headless re-open + layer/flat export of the written PXO and ORA
"""
from pathlib import Path
import hashlib, importlib.util, io, json, os, subprocess, sys, tempfile, zipfile
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = Path(r"C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second")
OUT = ROOT / "outputs/hero-sea-v01"
SRC = OUT / "rpg-2-star-ocean-the-second_heroine_battle-keypose-generated-input_unapproved-v01_20261020-181640-a8fdf0f7.png"
WRITER = ROOT / "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py"
PIXELORAMA = PRIMARY / "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"
SLUG, SUBJECT, VER, STAMP, UID = "rpg-2-star-ocean-the-second", "heroine-battle", "sea-unapproved-v01", "20261020-181955", "5e1a7c02"
W, H = 136, 144
PIN = (64, 136)                 # native; logical (32, 68). Lowest sole row = 135, rows 136..143 transparent.
TOP_ROW = 3                     # v17r2 occupied rows 3..135 (h 133): same display proportion, no hidden scale change
PALETTE_COLORS = 30
METAL_COLORS = 4                # of the 30: separate median-cut over blade steel (see convert step 2)
ALPHA_ON = 128                  # generator alpha is ~250-254 on the figure, 1-31 haze around it
CENTER_FRAC = 0.6               # cell-mode sampling window (central fraction of each source cell)
FACE_SRC = (468, 228, 662, 444) # source box: eyes/brows/mouth/ear exempt from speckle removal
SWORD_SRC = (742, 410, 1022, 735)
BELT_SRC_Y = 742                # below this (source y) non-navy, non-teal texels are legs
HEAD_SRC_Y = 470                # above this (source y) brown connected to the hair mass is hair
LAYERS = ["legs", "body", "scarf", "weapon", "hair", "head"]   # bottom -> top; a partition of the flattened still


def long(p):
    return Path("\\\\?\\" + str(Path(p).resolve()))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_text(p):
    return sha(Path(p).read_bytes().replace(b"\r\n", b"\n"))


def fid(role):
    return sha(f"{UID}:{role}".encode())[:8]


def name(purpose, ext):
    return f"{SLUG}_{SUBJECT}_{purpose}_{VER}_{STAMP}-{fid(purpose)}.{ext}"


def module(path, label):
    spec = importlib.util.spec_from_file_location(label, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def png_bytes(a):
    buf = io.BytesIO()
    Image.fromarray(np.ascontiguousarray(a, np.uint8), "RGBA").save(buf, "PNG", optimize=False, compress_level=9)
    return buf.getvalue()


def decode(b):
    return np.array(Image.open(io.BytesIO(b)).convert("RGBA"))


def components(mask, conn8=True):
    lab = np.zeros(mask.shape, np.int32)
    n = 0
    sizes = [0]
    nb = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)] if conn8 else [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for y, x in zip(*np.nonzero(mask)):
        if lab[y, x]:
            continue
        n += 1
        lab[y, x] = n
        stack, size = [(y, x)], 0
        while stack:
            cy, cx = stack.pop()
            size += 1
            for dy, dx in nb:
                qy, qx = cy + dy, cx + dx
                if 0 <= qy < mask.shape[0] and 0 <= qx < mask.shape[1] and mask[qy, qx] and not lab[qy, qx]:
                    lab[qy, qx] = n
                    stack.append((qy, qx))
        sizes.append(size)
    return lab, np.array(sizes)


def hsv(rgb):
    r, g, b = [rgb[..., i] / 255.0 for i in range(3)]
    mx, mn = np.max(rgb / 255.0, axis=-1), np.min(rgb / 255.0, axis=-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rr = m & (mx == r)
    gg = m & (mx == g) & ~rr
    bb = m & ~rr & ~gg
    h[rr] = (60 * ((g - b)[rr] / d[rr])) % 360
    h[gg] = 60 * ((b - r)[gg] / d[gg]) + 120
    h[bb] = 60 * ((r - g)[bb] / d[bb]) + 240
    s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def convert():
    raw = long(SRC).read_bytes()
    src = np.array(Image.open(io.BytesIO(raw)).convert("RGBA"))
    sh, sw = src.shape[:2]
    rec = {"inputSize": [sw, sh]}
    # 1. source alpha: threshold, then drop disconnected generator haze/specks (< 400 src px)
    on = src[..., 3] >= ALPHA_ON
    lab, sizes = components(on[::2, ::2], conn8=True)          # half-res labelling for speed, exact rule recorded
    keep_lab = np.nonzero(sizes >= 100)[0]
    keep_lab = keep_lab[keep_lab > 0]
    keep_small = np.isin(lab, keep_lab)
    keep = np.repeat(np.repeat(keep_small, 2, 0), 2, 1)[:sh, :sw] & on
    rec["sourceAlpha"] = {"threshold": ALPHA_ON, "pxAboveThreshold": int(on.sum()), "pxKept": int(keep.sum()),
                          "componentsDropped": int((sizes[1:] < 100).sum()), "rule": "8-connected on 2x-decimated mask, keep >=100 (= ~400 src px)"}
    # 2. fixed palette: median-cut (no dither) over opaque source pixels only, deterministic
    # v01 correction after first preview: global median-cut merged the rare cool blade steel into the beige vest,
    # so METAL_COLORS entries are cut separately from low-saturation light pixels inside the sword box.
    def cut(pixels, n):
        q = Image.fromarray(pixels.reshape(1, -1, 3), "RGB").quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        return np.array(q.getpalette()[:n * 3], np.uint8).reshape(-1, 3)
    opaque_rgb = src[keep][:, :3]
    sbox = np.zeros(keep.shape, bool)
    sbox[SWORD_SRC[1]:SWORD_SRC[3], SWORD_SRC[0]:SWORD_SRC[2]] = True
    srgb = src[..., :3].astype(int)
    lowsat = (srgb.max(-1) - srgb.min(-1) < 0.18 * np.maximum(srgb.max(-1), 1)) & (srgb.max(-1) > 140)
    steel = src[keep & sbox & lowsat][:, :3]
    pal = np.concatenate([cut(opaque_rgb, PALETTE_COLORS - METAL_COLORS), cut(steel, METAL_COLORS)])
    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette(pal.flatten().tolist() + pal[0].tolist() * (256 - len(pal)))   # pad = entry 0 (ties map low)
    full = Image.fromarray(src[..., :3], "RGB").quantize(palette=pal_img, dither=Image.Dither.NONE)
    idx = np.array(full, np.int16)
    assert idx.max() < PALETTE_COLORS, "padding entries never selected"
    idx[~keep] = -1
    # 3. geometry: scale from occupied height, x from the midpoint between the two boots' lowest bands
    ys, xs = np.nonzero(keep)
    y0, y1 = ys.min(), ys.max()
    scale = (y1 + 1 - y0) / (PIN[1] - TOP_ROW)                   # src px per native texel
    band = keep[y1 - int(4 * scale):y1 + 1].any(axis=0)
    cols = np.nonzero(band)[0]
    gaps = np.nonzero(np.diff(cols) > 1)[0]
    assert len(gaps) >= 1, "two separate boots in the sole band"
    g = gaps[np.argmax(np.diff(cols)[gaps])]
    left_boot, right_boot = (cols[0], cols[g]), (cols[g + 1], cols[-1])
    mid = (left_boot[1] + right_boot[0]) / 2.0
    ox = mid - (PIN[0] + 0.5) * scale
    oy = y0 - TOP_ROW * scale
    rec["geometry"] = {"sourceOccupiedRows": [int(y0), int(y1)], "srcPxPerTexel": round(float(scale), 4),
                       "originSrc": [round(float(ox), 3), round(float(oy), 3)], "soleBandBootsSrcX": [list(map(int, left_boot)), list(map(int, right_boot))],
                       "pinColumnSrcX": round(float(mid), 2), "nativeTopRow": TOP_ROW, "nativeLowestRow": PIN[1] - 1}
    # 4. cell-mode resample (one resampling step): coverage >= 0.5 -> opaque; colour = mode in the central window
    grid = np.full((H, W), -1, np.int16)
    for ty in range(H):
        for tx in range(W):
            sx0, sy0 = ox + tx * scale, oy + ty * scale
            ax0, ay0, ax1, ay1 = int(round(sx0)), int(round(sy0)), int(round(sx0 + scale)), int(round(sy0 + scale))
            if ax1 <= 0 or ay1 <= 0 or ax0 >= sw or ay0 >= sh:
                continue
            cell = idx[max(ay0, 0):min(ay1, sh), max(ax0, 0):min(ax1, sw)]
            if cell.size == 0 or (cell >= 0).mean() < 0.5:
                continue
            m = (1 - CENTER_FRAC) / 2 * scale
            cx0, cy0, cx1, cy1 = int(round(sx0 + m)), int(round(sy0 + m)), int(round(sx0 + scale - m)), int(round(sy0 + scale - m))
            core = idx[max(cy0, 0):min(cy1, sh), max(cx0, 0):min(cx1, sw)]
            vals = core[core >= 0]
            if vals.size == 0:
                vals = cell[cell >= 0]
            grid[ty, tx] = np.bincount(vals, minlength=PALETTE_COLORS).argmax()
    assert (grid[:TOP_ROW] < 0).all() and (grid[PIN[1]:] < 0).all(), "occupied rows stay 3..135"
    assert (grid[:, 0] < 0).all() and (grid[:, -1] < 0).all(), "art fits inside transparent margins"
    resampled = grid.copy()

    def to_src(ty, tx):
        return ox + (tx + 0.5) * scale, oy + (ty + 0.5) * scale

    face = np.zeros((H, W), bool)
    for ty in range(H):
        for tx in range(W):
            sx, sy = to_src(ty, tx)
            face[ty, tx] = FACE_SRC[0] <= sx < FACE_SRC[2] and FACE_SRC[1] <= sy < FACE_SRC[3]
    # 5. curation (rules only, no painting): stray alpha, pinholes, speckle outside the face box
    op = grid >= 0
    lab, sizes = components(op)
    stray = op & (sizes[lab] < 6)
    grid[stray] = -1
    op = grid >= 0
    pin = np.zeros_like(op)
    pin[1:-1, 1:-1] = ~op[1:-1, 1:-1] & op[:-2, 1:-1] & op[2:, 1:-1] & op[1:-1, :-2] & op[1:-1, 2:]
    fills = 0
    for y, x in zip(*np.nonzero(pin)):
        n4 = [grid[y - 1, x], grid[y + 1, x], grid[y, x - 1], grid[y, x + 1]]
        grid[y, x] = max(set(n4), key=n4.count)
        fills += 1
    speck = 0
    g0 = grid.copy()
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            v = g0[y, x]
            if v < 0 or face[y, x]:
                continue
            nb = [g0[y + dy, x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
            if v in nb:
                continue
            opaque_nb = [n for n in nb if n >= 0]
            if len(opaque_nb) < 8:
                continue                      # silhouette edge texels are kept (shape boundary of the source)
            best = max(set(opaque_nb), key=opaque_nb.count)
            if opaque_nb.count(best) >= 5:
                grid[y, x] = best
                speck += 1
    rec["curation"] = {"strayAlphaTexelsRemoved": int(stray.sum()), "pinholesFilled": fills,
                       "interiorSpecklesMerged": speck, "faceBoxSrc": list(FACE_SRC), "faceTexelsExempt": int(face.sum()),
                       "rules": ["remove 8-connected opaque islands < 6 texels",
                                 "fill transparent texels with 4/4 opaque orthogonal neighbours (orth. majority colour)",
                                 "interior texel whose colour matches none of 8 opaque neighbours -> neighbour majority if >=5/8; face box exempt"],
                       "texelsChangedByCuration": int((grid != resampled).sum())}
    # 6. layer masks (explicit rules on palette class + source-mapped regions; outlines follow neighbours)
    rgb = pal[np.maximum(grid, 0)].astype(float)
    hue, sat, val = hsv(rgb)
    op = grid >= 0
    srcxy = np.array([[to_src(ty, tx) for tx in range(W)] for ty in range(H)])
    sx, sy = srcxy[..., 0], srcxy[..., 1]
    dark = op & (val < 0.22)
    teal = op & (hue >= 165) & (hue <= 200) & (sat > 0.35) & ~dark
    navy = op & (hue >= 205) & (hue <= 260) & (sat > 0.2) & ~dark
    metal = op & (sat < 0.18) & (val > 0.55)
    skin = op & (hue >= 10) & (hue <= 40) & (sat > 0.18) & (sat < 0.55) & (val > 0.72)
    brown = op & (hue < 45) & (sat > 0.3) & (val >= 0.22) & ~skin
    part = np.full((H, W), "", object)
    in_sword = (sx >= SWORD_SRC[0]) & (sx < SWORD_SRC[2]) & (sy >= SWORD_SRC[1]) & (sy < SWORD_SRC[3])
    part[in_sword & (metal | (op & (sat < 0.25) & ~skin & ~brown & ~navy))] = "weapon"
    part[teal & (part == "")] = "scarf"
    head_zone = op & (sy < HEAD_SRC_Y)
    hb = brown & head_zone & (part == "")
    lab, sizes = components(hb, conn8=False)
    hair_lab = np.argmax(sizes[1:]) + 1 if len(sizes) > 1 else 0
    part[hb & (lab == hair_lab)] = "hair"
    part[head_zone & (part == "") & ~dark & ~navy] = "head"           # skin, eyes, mouth, ear, small head colours
    legs_zone = op & (sy >= BELT_SRC_Y) & (part == "") & ~dark & ~navy
    part[legs_zone] = "legs"
    part[op & (part == "") & ~dark] = "body"
    # outlines/dark texels: neighbour-majority assignment, iterated until stable
    for _ in range(12):
        todo = list(zip(*np.nonzero(op & (part == ""))))
        if not todo:
            break
        upd = {}
        for y, x in todo:
            nb = [part[y + dy, x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                  if (dy or dx) and 0 <= y + dy < H and 0 <= x + dx < W and part[y + dy, x + dx] != ""]
            if nb:
                upd[(y, x)] = max(sorted(set(nb)), key=nb.count)
        for k, v in upd.items():
            part[k] = v
    part[op & (part == "")] = "body"
    rec["layerRule"] = {"method": "MASK SLICES of the single flattened curated still (partition, no overlap, nothing painted behind)",
                        "weapon": f"metal/low-saturation inside source box {list(SWORD_SRC)}",
                        "scarf": "teal hue 165-200, sat>0.35, anywhere (neck wrap + trailing tail)",
                        "hair": f"brown (hue<45,sat>0.3,non-skin) above source y {HEAD_SRC_Y}, largest 4-connected mass only",
                        "head": f"remaining non-dark, non-navy texels above source y {HEAD_SRC_Y} (skin, eyes, brows, mouth, ear)",
                        "legs": f"non-dark, non-navy texels below source y {BELT_SRC_Y} (trousers, knee pad, straps, boots)",
                        "body": "everything else (jacket, vest, belt, pouch, arms, gloves)",
                        "outlines": "dark texels (V<0.22) take the majority part of their 8 neighbours, iterated"}
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[op, :3] = pal[grid[op]]
    rgba[op, 3] = 255
    layers = {}
    for n in LAYERS:
        m = part == n
        L = np.zeros_like(rgba)
        L[m] = rgba[m]
        layers[n] = L
    rec["layerTexels"] = {n: int((part == n).sum()) for n in LAYERS}
    rec["palette"] = {"colors": PALETTE_COLORS, "method": "PIL median-cut, no dither: 26 over all kept opaque source pixels + 4 over low-saturation light pixels in the sword box; nearest mapping",
                      "used": int(len(np.unique(grid[op]))), "hex": ["#%02x%02x%02x" % tuple(c) for c in pal]}
    return raw, src, rgba, layers, rec


def ora_bytes(layers, flat):
    buf = io.BytesIO()
    dt = (2026, 10, 20, 18, 19, 54)
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", dt), "image/openraster", zipfile.ZIP_STORED)
        stack = ['<?xml version="1.0" encoding="UTF-8"?>', f'<image version="0.0.3" w="{W}" h="{H}">', "<stack>"]
        for i, n in reversed(list(enumerate(LAYERS))):          # ORA lists top layer first
            stack.append(f'<layer name="{n}" src="data/{i:02d}-{n}.png" x="0" y="0" opacity="1.0" visibility="visible" composite-op="svg:src-over"/>')
        stack += ["</stack>", "</image>"]
        z.writestr(zipfile.ZipInfo("stack.xml", dt), "\n".join(stack) + "\n", zipfile.ZIP_DEFLATED)
        for i, n in enumerate(LAYERS):
            z.writestr(zipfile.ZipInfo(f"data/{i:02d}-{n}.png", dt), png_bytes(layers[n]), zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("mergedimage.png", dt), png_bytes(flat), zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("Thumbnails/thumbnail.png", dt), png_bytes(flat), zipfile.ZIP_DEFLATED)
    return buf.getvalue()


def outputs():
    raw, src, flat, layers, rec = convert()
    writer = module(WRITER, "established_pxo_writer")
    writer.W, writer.H = W, H
    writer.to_rgba = lambda im: np.ascontiguousarray(im, np.uint8)
    png = png_bytes(flat)
    view = np.zeros((H * 4, W * 4, 4), np.uint8)
    bg = Image.new("RGBA", (W, H), (118, 128, 138, 255))
    bg.alpha_composite(Image.fromarray(flat, "RGBA"))
    view = np.array(bg.resize((W * 4, H * 4), Image.NEAREST))
    files = {
        "png": (name("still-native136", "png"), png),
        "ora": (name("still-layered", "ora"), ora_bytes(layers, flat)),
        "pxo": (name("still-editable", "pxo"), writer.make_pxo([layers], [1.0], png, name("still-source-export", "png"), 8,
                                                                order=LAYERS, dt=(2026, 10, 20, 18, 19, 54))),
        "inspect": (name("inspection-x4-grey", "png"), png_bytes(view)),
    }
    manifest = {
        "status": "UNAPPROVED technical static candidate. Generated input + deterministic resample/curation; not hand-pixel-authored, "
                  "not art approval, no animation, no runtime/default adoption, no game-source change.",
        "styleDirection": "docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md",
        "rejectedPredecessor": "v17r2 8759026a (procedural texel authoring) rejected by the creator",
        "provenance": {"input": SRC.name, "inputSha256": sha(raw), "inputKind": "generated image selected by Codex (generator output; "
                       "transparent, pixel-looking, irregular grid ~8.0-8.9 src px by FFT); production input, not native pixel art, not approved",
                       "generatorDetailsKnownToThisTool": False, "handPaintedTexels": 0,
                       "resamplingSteps": 1, "resampling": "palette-index cell mode (central 60% window), coverage>=0.5 alpha; no filtering/dither"},
        "cell": [W, H], "logicalExtent": [68, 72], "pinNative": list(PIN), "pinLogical": [32, 68],
        "displayRequirement": "draw_texture_rect(texture, Rect2(round(x)-32, 204, 68, 72)), nearest; same as v17/v17r2",
        "proportion": "occupied rows 3..135 (133 rows) = v17r2 occupied rows; no scale change hidden in cropping",
        "layers": LAYERS, "frameCount": 1, **rec,
        "source": {"file": str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"), "sha256TextLf": sha_text(__file__)},
        "inputs": {"pxoWriter": {"file": str(WRITER.relative_to(ROOT)).replace("\\", "/"), "sha256TextLf": sha_text(WRITER)}},
        "files": {role: {"name": n, "sha256": sha(b)} for role, (n, b) in files.items()},
        "inspectionNote": "inspection-x4-grey is nearest x4 on flat grey for viewing only; it is not runtime art",
        "artApproved": False, "animationMade": False, "runtimeDefaultChanged": False, "gameSourceChanged": False, "guiSaveAsVerified": False,
        "limits": ["640x360 native path samples 1 of 4 native texels (nearest) so 1-texel face features alias there",
                   "layers are slices of a flattened still; moving a part reveals holes (no painted occluded pixels)",
                   "outline continuity after resampling is not re-drawn; generator outline breaks are kept",
                   "automated gates are technical only; face quality needs visual judgement at actual size"],
    }
    files["manifest"] = (name("source-manifest", "json"), (json.dumps(manifest, indent=1) + "\n").encode())
    return files, flat, layers, manifest


def gates(files, flat, layers, manifest):
    res = []

    def gate(k, ok, info=None):
        res.append({"key": k, "pass": bool(ok), "info": info})
    op = flat[..., 3] > 0
    ys, xs = np.nonzero(op)
    gate("native cell 136x144 RGBA", flat.shape == (H, W, 4))
    gate("alpha binary 0/255", set(np.unique(flat[..., 3]).tolist()) <= {0, 255})
    gate("occupied rows 3..135 (v17r2 proportion)", ys.min() == TOP_ROW and ys.max() == PIN[1] - 1, [int(ys.min()), int(ys.max())])
    gate("transparent margins (cols 0/135, rows 136..143)", not op[:, 0].any() and not op[:, -1].any() and not op[PIN[1]:].any(),
         [int(xs.min()), int(xs.max())])
    r = np.nonzero(op[PIN[1] - 1])[0]
    gate("pin column 64 transparent on sole row 135 with a boot on the left", (r < 64).any() and not op[PIN[1] - 1, 64], r.tolist())
    feet = {}
    for side, sel in (("left", slice(0, 64)), ("right", slice(65, W))):
        rows = np.nonzero(op[100:PIN[1], sel].any(axis=1))[0]
        lo = [y for y in range(PIN[1] - 1, 99, -1) if op[y, sel].any()]
        feet[side] = int(lo[0]) if lo else None
    gate("record per-foot lowest row (right boot may sit higher in the source pose)", feet["left"] == PIN[1] - 1, feet)
    stack = np.zeros_like(flat)
    covered = np.zeros((H, W), int)
    for n in LAYERS:
        covered += layers[n][..., 3] > 0
        stack[layers[n][..., 3] > 0] = layers[n][layers[n][..., 3] > 0]
    gate("layers partition the still (each opaque texel in exactly one layer)", (covered[op] == 1).all() and (covered[~op] == 0).all())
    gate("layer stack equals native PNG", np.array_equal(stack, flat))
    gate("every layer non-empty", all((layers[n][..., 3] > 0).any() for n in LAYERS), manifest["layerTexels"])
    z = zipfile.ZipFile(io.BytesIO(files["ora"][1]))
    gate("ORA mimetype stored first", z.namelist()[0] == "mimetype" and z.getinfo("mimetype").compress_type == zipfile.ZIP_STORED)
    gate("ORA mergedimage equals PNG", np.array_equal(decode(z.read("mergedimage.png")), flat))
    zp = zipfile.ZipFile(io.BytesIO(files["pxo"][1]))
    d = json.loads(zp.read("data.json"))
    gate("PXO 136x144, 1 frame, layer names = ORA order", (d["size_x"], d["size_y"]) == (W, H) and len(d["frames"]) == 1
         and [l["name"] for l in d["layers"]] == LAYERS)
    cels = [np.frombuffer(zp.read(f"image_data/frames/1/layer_{i}"), np.uint8).reshape(H, W, 4) for i in range(1, len(LAYERS) + 1)]
    gate("PXO raw cels byte-equal ORA layers", all(np.array_equal(c, decode(z.read(f"data/{i:02d}-{n}.png")))
                                                   for i, (c, n) in enumerate(zip(cels, LAYERS))))
    gate("palette <= 30 colours used", manifest["palette"]["used"] <= PALETTE_COLORS, manifest["palette"]["used"])
    gate("input hash bound", manifest["provenance"]["inputSha256"] == sha(long(SRC).read_bytes()))
    return res


def native():
    files, flat, layers, manifest = outputs()
    for role in ("pxo", "ora", "png"):
        assert long(OUT / files[role][0]).read_bytes() == files[role][1], "build first; frozen files differ"
    exe = PIXELORAMA.resolve()
    tmp = Path(tempfile.mkdtemp(prefix="hsea01px-"))
    report = {"status": "Pixelorama 1.2.3 headless re-open + export of the written v01 sources; not a GUI Save As; not art approval",
              "executable": str(exe), "executableSha256": sha(exe.read_bytes()), "tempRoot": str(tmp), "runs": {},
              "diagnosticPolicy": "every stdout/stderr line containing ERROR, SCRIPT ERROR, WARNING or Shader is reported unfiltered"}
    for role in ("pxo", "ora"):
        for split in (True, False):
            key = f"{role}-{'split' if split else 'flat'}"
            folder = tmp / key
            for sub in ("app", "local", "exp"):
                (folder / sub).mkdir(parents=True)
            src = folder / files[role][0]
            src.write_bytes(files[role][1])
            env = dict(os.environ, APPDATA=str(folder / "app"), LOCALAPPDATA=str(folder / "local"))
            target = folder / "exp" / f"hsea-{role}.png"
            cmd = [str(exe), "--headless", "--quit", "--", "--export"] + (["--split-layers"] if split else []) + ["-o", str(target), str(src)]
            proc = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
                                  creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            exported = sorted((folder / "exp").glob("*.png"))
            if split:
                exact = {n: (lambda hits: len(hits) == 1 and np.array_equal(np.array(Image.open(hits[0]).convert("RGBA")), layers[n]))(
                    [q for q in exported if f"({n})" in q.name]) for n in LAYERS}
                ok = len(exported) == len(LAYERS) and all(exact.values())
            else:
                exact = {"flat": len(exported) == 1 and np.array_equal(np.array(Image.open(exported[0]).convert("RGBA")), flat)}
                ok = exact["flat"]
            text = proc.stdout + proc.stderr
            diag = [ln for ln in text.splitlines() if any(t in ln for t in ("ERROR", "SCRIPT ERROR", "WARNING", "Shader"))]
            report["runs"][key] = {"exit": proc.returncode, "cmd": cmd[1:], "exportedNames": [q.name for q in exported], "exact": exact,
                                   "allExact": ok, "sourceUnchanged": src.read_bytes() == files[role][1], "diagnosticLines": diag,
                                   "cleanApp": proc.returncode == 0 and not diag, "stdout": proc.stdout, "stderr": proc.stderr}
    report["nativeExactExport"] = all(r["exit"] == 0 and r["allExact"] and r["sourceUnchanged"] for r in report["runs"].values())
    report["cleanApp"] = all(r["cleanApp"] for r in report["runs"].values())
    path = long(OUT / name("pixelorama-native-report", "json"))
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(report, indent=1) + "\n")
    print({k: (v["exit"], v["allExact"], len(v["diagnosticLines"])) for k, v in report["runs"].items()})
    print("HSEA01_NATIVE", "EXACT" if report["nativeExactExport"] else "NOT_EXACT", "CLEAN" if report["cleanApp"] else "DIAGNOSTICS")
    return 0 if report["nativeExactExport"] else 1


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "native":
        sys.exit(native())
    files, flat, layers, manifest = outputs()
    again = outputs()[0]
    det = all(files[k][1] == again[k][1] for k in files)
    res = gates(files, flat, layers, manifest) + [{"key": "deterministic rebuild byte-identical", "pass": det, "info": None}]
    if mode == "build":
        for role, (n, b) in files.items():
            p = long(OUT / n)
            if p.exists():
                assert p.read_bytes() == b, f"refusing to overwrite differing {n}"
            else:
                p.write_bytes(b)
    else:
        for role, (n, b) in files.items():
            res.append({"key": f"on-disk {role} byte-identical", "pass": long(OUT / n).read_bytes() == b, "info": n})
        path = long(OUT / name("check-report", "json"))
        if not path.exists():
            path.write_text(json.dumps({"passed": sum(r["pass"] for r in res), "failed": sum(not r["pass"] for r in res),
                                        "gates": res, "source": manifest["source"]}, indent=1, default=str) + "\n", encoding="utf-8")
    failed = [r for r in res if not r["pass"]]
    for r in res:
        print("PASS" if r["pass"] else "FAIL", r["key"], r["info"] if r["info"] is not None else "")
    print(f"HSEA01_{mode.upper()}", f"{len(res) - len(failed)}/{len(res)}", "OK" if not failed else "FAILED")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
