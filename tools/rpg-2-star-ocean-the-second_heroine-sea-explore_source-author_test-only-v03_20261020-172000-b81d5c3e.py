"""Heroine Sea-of-Stars exploration idle+walk source, v03 method (generated-base adaptation + articulated layers).

UNAPPROVED, test-only. Writes only outputs/hsea-exp02/src-v03-<tag>/. Supersedes the rejected v02 primitive
redraw method (outputs/hsea-exp02/src-20261020-171600 kept untouched as rejected evidence).
- south idle f00 = approved static bytes verbatim; south walk articulates the approved static's own legs.
- east/north bases = Codex built-in imagegen directional sources (outputs/hse-dir08, unapproved), adapted like the
  existing exploration-native-build: alpha bbox crop, nearest scale to 96 px body, 80x112 canvas, pivot (40,104),
  hard alpha (>=128), colours mapped to the approved south static's 32-colour palette.
- walk: upper body bobs; each leg is split into thigh and shin+boot segments and rotated about hip/knee
  (side view) or foreshortened (front/back view); a painted trouser under-layer fills the crotch/joint gap.
- west = east mirrored (disclosed; asymmetric straps/scarf tail flip sides).
Usage: python -I <this> [--out-tag YYYYMMDD-HHMMSS]
"""
import hashlib, importlib.util, io, json, sys, zipfile, datetime, math
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOUTH = "outputs/hero-sea-exp-v01/rpg-2-star-ocean-the-second_heroine-sea_exploration-native80x112_unapproved-v01_20261020-181941-4449ed55.png"
SOUTH_SHA = "6bf1d688487bd3fcc71eeb2e7c9b7c74f1fe6b6cd6362860b7fa0d42e009e429"
GEN = {"east": "outputs/hse-dir08/rpg-2-star-ocean-the-second_heroine-sea_east-direction-generated-source_unapproved-v01_20261020-211734-ddf94004.png",
       "north": "outputs/hse-dir08/rpg-2-star-ocean-the-second_heroine-sea_north-direction-generated-source_unapproved-v01_20261020-211734-ddf94004.png"}
WRITER = "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py"
W, H, PIV, SOLE, BODY = 80, 112, (40, 104), 103, 96
WALK_MS, IDLE_MS = 60, 600          # 8 x 60 ms = 480 ms / 2 steps = 4.167 steps/s
DT = (2026, 10, 20, 0, 0, 0)

# Planned footfall plan (8 phases, two steps). Near leg contact at p0, far leg contact at p4.
# side view: (thigh deg, knee bend deg, lift px); +deg swings the foot forward (toward facing).
SIDE = [(20, 4, 0), (10, 2, 0), (0, 0, 0), (-12, 4, 0), (-20, 14, 1), (-6, 34, 4), (10, 28, 4), (20, 10, 1)]
# front/back views: (foreshortened lift px, inward x)
FRONT = [(0, 0), (0, 0), (0, 0), (1, 0), (3, 0), (6, 1), (5, 1), (2, 0)]
BOB = [1, 0, -1, 0, 1, 0, -1, 0]


def sha(b): return hashlib.sha256(b).hexdigest()
def png(a):
    b = io.BytesIO(); Image.fromarray(a).save(b, "PNG"); return b.getvalue()
def blank(): return np.zeros((H, W, 4), np.uint8)


def palette_of(a):
    m = a[..., 3] > 0
    return np.unique(a[m][:, :3], axis=0).astype(np.int32)


def adapt(path, pal):
    im = Image.open(ROOT / path).convert("RGBA")
    bb = Image.fromarray((np.array(im)[..., 3] >= 128).astype(np.uint8) * 255).getbbox()
    crop = im.crop(bb); w = max(1, round(crop.width * BODY / crop.height))
    sm = np.array(crop.resize((w, BODY), Image.NEAREST))
    out = blank(); x0 = PIV[0] - w // 2; y0 = SOLE + 1 - BODY
    keep = sm[..., 3] >= 128
    rgb = sm[..., :3].astype(np.int32)
    idx = ((rgb[:, :, None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
    q = pal[idx].astype(np.uint8)
    region = out[y0:y0 + BODY, x0:x0 + w]
    region[keep, :3] = q[keep]; region[keep, 3] = 255
    return out, {"sourceBBox": list(bb), "scaledWidth": w, "x0": x0}


def rows(a):
    ys = np.nonzero((a[..., 3] > 0).any(1))[0]; return ys[0], ys[-1]


def rot_paste(dst, seg, pivot, angle, to):
    """Rotate RGBA segment about pivot (nearest, hard alpha) and paste so pivot lands at `to` (src-over)."""
    if not (seg[..., 3] > 0).any() and True: return
    ys, xs = np.nonzero(seg[..., 3] > 0)
    out = np.zeros_like(seg)
    t = math.radians(angle); c, s = math.cos(t), math.sin(t)
    # inverse mapping over destination bbox
    r = int(max(np.hypot(xs - pivot[0], ys - pivot[1]).max(), 1)) + 2
    for y in range(max(0, int(to[1]) - r), min(H, int(to[1]) + r + 1)):
        for x in range(max(0, int(to[0]) - r), min(W, int(to[0]) + r + 1)):
            dx, dy = x - to[0], y - to[1]
            sx = round(pivot[0] + c * dx + s * dy); sy = round(pivot[1] - s * dx + c * dy)
            if 0 <= sx < W and 0 <= sy < H and seg[sy, sx, 3]:
                out[y, x] = seg[sy, sx]
    m = out[..., 3] > 0; dst[m] = out[m]


def mask_split(a, hip, xsplit, band, extra):
    """Upper body = rows < hip plus hands/coat tails outside the leg band for `extra` rows below hip;
    the remaining lower body splits into two legs at column xsplit."""
    upm = np.zeros((H, W), bool); upm[:hip] = True
    upm[hip:hip + extra, :band[0]] = True; upm[hip:hip + extra, band[1] + 1:] = True
    up = np.where(upm[..., None], a, 0).astype(np.uint8)
    low = np.where(upm[..., None], 0, a).astype(np.uint8)
    left = low.copy(); left[:, xsplit:] = 0
    right = low.copy(); right[:, :xsplit] = 0
    return up, left, right


def underpaint(a, hip, band, depth=10):
    """Painted trouser under-layer behind the hip joint: each row spans the base leg extent in darkest trouser."""
    lay = blank(); pant = darkest(a, hip, hip + depth)
    for y in range(hip - 2, hip + depth):
        xs = np.nonzero(a[y, band[0]:band[1] + 1, 3] > 0)[0] + band[0]
        if len(xs): lay[y, xs.min() + 1:xs.max()] = (*pant, 255)
    lay[a[..., 3] == 0] = 0          # only under already-opaque body: hidden at rest, fills joints when legs move
    return lay


def darkest(a, y0, y1):
    px = a[y0:y1][a[y0:y1, :, 3] > 0][:, :3].astype(int)
    vals, cnt = np.unique(px, axis=0, return_counts=True)
    cand = vals[cnt >= max(2, cnt.max() // 6)]
    return tuple(int(v) for v in cand[cand.sum(1).argmin()])


def leg_side(seg, hip_pt, knee_y, thigh, knee, lift, sx):
    """Two-segment leg articulation for a side view. sx=+1 facing right."""
    th = seg.copy(); th[knee_y:] = 0
    sh = seg.copy(); sh[:knee_y] = 0
    out = blank()
    a1 = -thigh * sx                      # screen rotation: forward swing for a right-facing body = CCW
    t = math.radians(a1)
    kdx, kdy = 0, knee_y - hip_pt[1]
    c, s = math.cos(t), math.sin(t)
    knee_to = (hip_pt[0] + c * kdx - s * kdy, hip_pt[1] - lift + s * kdx + c * kdy)
    rot_paste(out, sh, (hip_pt[0], knee_y), a1 + knee * sx, knee_to)
    rot_paste(out, th, hip_pt, a1, (hip_pt[0], hip_pt[1] - lift))
    return out


def leg_front(seg, hip, lift, inward, sx):
    """Front/back view: foreshorten the leg (hip..sole) by `lift` px with nearest row resampling; foot rises."""
    out = blank()
    if lift == 0 and inward == 0:
        return seg.copy()
    y0, y1 = hip, SOLE
    n_src = y1 - y0 + 1; n_dst = n_src - lift
    for i in range(n_dst):
        sy = y0 + min(n_src - 1, round(i * (n_src - 1) / max(1, n_dst - 1)))
        out[y0 + i] = np.roll(seg[sy], inward * sx * (i > n_dst // 2), 0)
    return out


def compose(layers, order):
    out = blank()
    for k in order:
        m = layers[k][..., 3] > 0; out[m] = layers[k][m]
    out[SOLE + 1:] = 0
    return out


def build_dir(base, kind, hip, xsplit, knee_rel, band, extra, facing=1):
    up, left, right = mask_split(base, hip, xsplit, band, extra)
    under = underpaint(base, hip, band)
    idle = {"under-trouser-paint": under, "far-leg": left if facing > 0 else right,
            "near-leg": right if facing > 0 else left, "upper-body": up}
    order = ["under-trouser-paint", "far-leg", "near-leg", "upper-body"]
    assert np.array_equal(compose(idle, order), base)
    frames = [(compose(idle, order), idle)]
    walk = []
    near, far = idle["near-leg"], idle["far-leg"]
    nh = (int(np.nonzero(near[hip].any(-1) if False else near[hip:, :, 3].any(0))[0].mean()), hip)
    fh = (int(np.nonzero(far[hip:, :, 3].any(0))[0].mean()), hip)
    for p in range(8):
        b = BOB[p]
        L = {"under-trouser-paint": np.roll(under, b, 0), "upper-body": np.roll(up, b, 0)}
        if kind == "side":
            q = SIDE[p]; r = SIDE[(p + 4) % 8]
            L["near-leg"] = leg_side(near, (nh[0], hip), hip + knee_rel, q[0], q[1], q[2], facing)
            L["far-leg"] = leg_side(far, (fh[0], hip), hip + knee_rel, r[0], r[1], r[2], facing)
            L["near-leg"] = np.roll(L["near-leg"], b if q[2] == 0 else min(b, 0), 0)
            L["far-leg"] = np.roll(L["far-leg"], b if r[2] == 0 else min(b, 0), 0)
        else:
            q = FRONT[p]; r = FRONT[(p + 4) % 8]
            L["near-leg"] = leg_front(near, hip, q[0], q[1], 1 if facing > 0 else -1)
            L["far-leg"] = leg_front(far, hip, r[0], r[1], -1 if facing > 0 else 1)
            # stance leg absorbs the bob (knee flex) so planted soles stay on row SOLE
            for key, st in (("near-leg", q[0]), ("far-leg", r[0])):
                if b > 0 and st == 0: L[key] = leg_front(L[key], hip, 0, 0, 1)
        if b < 0:   # body rises 1 px: extend each planted leg's top row upward (thigh stretch) to close the waist seam
            L["under-trouser-paint"] = under.copy()
            for key in ("near-leg", "far-leg"):
                lg = L[key]; top = lg[hip]; gap = (lg[hip - 1, :, 3] == 0) & (top[:, 3] > 0)
                lg[hip - 1][gap] = top[gap]
        walk.append((compose(L, order), L))
    return frames, walk, order


def main():
    tag = sys.argv[sys.argv.index("--out-tag") + 1] if "--out-tag" in sys.argv else datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    uid = sha(("v03" + tag).encode())[:8]
    run = ROOT / "outputs" / "hsea-exp02" / f"src-v03-{tag}"; run.mkdir(parents=True, exist_ok=True)
    raw = (ROOT / SOUTH).read_bytes(); assert sha(raw) == SOUTH_SHA
    south = np.array(Image.open(io.BytesIO(raw)).convert("RGBA")); pal = palette_of(south)
    bases, adapt_info = {"south": south}, {}
    for d, p in GEN.items():
        bases[d], adapt_info[d] = adapt(p, pal)
        adapt_info[d].update(file=p, sha256=sha((ROOT / p).read_bytes()))
    # per-direction articulation landmarks (rows in the 80x112 frame) chosen from inspected adapted bases
    # (kind, hip row, leg split x, knee rows below hip, leg band x0..x1, rows below hip kept with upper body)
    spec_dirs = {"south": ("front", 68, 41, 14, (27, 55), 12), "north": ("front", 71, 41, 14, (29, 52), 3),
                 "east": ("side", 73, 44, 13, (29, 57), 0)}
    out = {}
    for d, (kind, hip, xs, knee, band, extra) in spec_dirs.items():
        out[d] = build_dir(bases[d], kind, hip, xs, knee, band, extra)
    ef, ew, eo = out["east"]
    mir = lambda L: {k: v[:, ::-1].copy() for k, v in L.items()}
    out["west"] = ([(a[:, ::-1].copy(), mir(L)) for a, L in ef], [(a[:, ::-1].copy(), mir(L)) for a, L in ew], eo)
    spec = importlib.util.spec_from_file_location("pxo_writer", ROOT / WRITER)
    wr = importlib.util.module_from_spec(spec); spec.loader.exec_module(wr)
    wr.W, wr.H = W, H; wr.to_rgba = lambda a: np.ascontiguousarray(a, np.uint8)
    pre = "rpg-2-star-ocean-the-second_heroine-sea"
    actions = {"idle": {}, "walk": {}}; src = []
    for d in ("south", "west", "north", "east"):
        idle, walk, order = out[d]
        allf = []
        for act, fr in (("idle", idle), ("walk", walk)):
            actions[act][d] = []
            for i, (arr, L) in enumerate(fr):
                b = raw if (d == "south" and act == "idle" and i == 0) else png(arr)
                if d == "south" and act == "idle" and i == 0: assert np.array_equal(arr, south)
                fn = f"{pre}_explore-{d}-{act}-f{i:02d}_unapproved-v03_{tag}-{uid}.png"
                (run / fn).write_bytes(b)
                actions[act][d].append({"file": fn, "duration_ms": IDLE_MS if act == "idle" else WALK_MS})
                allf.append((L, (IDLE_MS if act == "idle" else WALK_MS) / 1000))
        per = [{k: L[k] for k in order} for L, _ in allf]
        pxo = f"{pre}_explore-{d}-layers_unapproved-v03_{tag}-{uid}.pxo"
        (run / pxo).write_bytes(wr.make_pxo(per, [t for _, t in allf], png(compose(per[0], order)), pxo[:-4] + ".png", 16, order=order, dt=DT))
        ora = f"{pre}_explore-{d}-idle0-layers_unapproved-v03_{tag}-{uid}.ora"
        with zipfile.ZipFile(run / ora, "w") as z:
            z.writestr(zipfile.ZipInfo("mimetype", DT), "image/openraster")
            z.writestr(zipfile.ZipInfo("mergedimage.png", DT), png(compose(per[0], order)))
            root = ET.Element("image", {"w": str(W), "h": str(H)}); st = ET.SubElement(root, "stack")
            for i, k in enumerate(order[::-1]):
                z.writestr(zipfile.ZipInfo(f"data/l{i}.png", DT), png(per[0][k]))
                ET.SubElement(st, "layer", {"name": k, "src": f"data/l{i}.png", "x": "0", "y": "0"})
            z.writestr(zipfile.ZipInfo("stack.xml", DT), ET.tostring(root, encoding="utf8"))
        src += [{"direction": d, "file": pxo, "format": "pixelorama-pxo", "sha256": sha((run / pxo).read_bytes())},
                {"direction": d, "file": ora, "format": "openraster-supplemental-idle0", "sha256": sha((run / ora).read_bytes())}]
    man = {"schema": "worlds-between.exploration-source.v1", "actor_id": "protagonist-female", "density": 2,
           "frame_size": [W, H], "pivot": list(PIV), "actions": actions, "source_files": src,
           "status": "UNAPPROVED test-only candidate; generated-base adaptation; no runtime/default change",
           "actor_id_note": "Coordinator correction 2026-10-20: actor_id is the SpriteSetPilot.attach host key 'protagonist-female'; the earlier 'hero:female' in the v02 brief was a contract error.",
           "author_tool": {"file": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"),
                           "sha256TextLf": sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n"))},
           "generated_bases": adapt_info, "approved_south": {"file": SOUTH, "sha256": SOUTH_SHA},
           "landmarks": {d: {"kind": k, "hipRow": h, "legSplitX": x, "kneeRel": kr, "legBand": list(bd), "upperExtraRows": ex}
                     for d, (k, h, x, kr, bd, ex) in spec_dirs.items()},
           "gait": {"walk_frames": 8, "frame_ms": WALK_MS, "steps_per_second": round(2000 / (8 * WALK_MS), 3),
                    "side_plan": SIDE, "front_plan": FRONT, "bob": BOB},
           "disclosure": ["west = east mirrored; asymmetric straps/scarf tail flip sides",
                          "east/north are nearest-scaled, palette-mapped Codex imagegen sources (unapproved generated source, not hand-authored)",
                          "arms, scarf and ponytail are not articulated: no arm counter-swing yet",
                          "one idle pose per direction (breath frame would break exact 96 px idle height)"]}
    mp = run / f"{pre}_explore-source-manifest_unapproved-v03_{tag}-{uid}.json"
    mp.write_text(json.dumps(man, indent=1), encoding="utf-8", newline="\n")
    print(mp)


if __name__ == "__main__":
    main()
