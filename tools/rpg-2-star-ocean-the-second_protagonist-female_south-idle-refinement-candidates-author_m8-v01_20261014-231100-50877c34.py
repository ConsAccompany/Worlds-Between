"""Female protagonist south-idle refinement candidates (M8 v01), single static frame.

Technical candidates only. Output is unapproved and not used by the game runtime.
Input is the read-only imagegen refinement reference (a concept, not a production sprite).
Two standalone 80x112 RGBA PNGs are written, each a 96-texel-tall body (48 logical px in
game at 0.5 scale), binary alpha 0/255, no shadow or background:

  inkline  material-group sampling with dark-line priority (ink kept where it covers
           >= 42 % of a texel), black silhouette outline, raw 40-cluster palette,
           hand-specified anime face (lashes, sclera, iris), knee guard, belt and buckles.
  selout   material-group sampling with line suppression (ink only where it covers
           >= 62 %), 1-texel spur removal, ramp-reduced palette, selective (coloured)
           outline, hand-specified soft face (brown lashes, blush), knee guard, belt and buckles.

Neither candidate reuses the rejected BOX/LANCZOS area-average + median-cut pipeline:
texel colours are picked from OKLab k-means clusters of the reference (no blending of
unrelated materials), then cleaned and locally corrected from fixed texel maps below.

Run with the Codex-runtime Python (Pillow 12.3.0, NumPy 2.3.5), isolated mode:
  python -I <this script>                  # write PNGs + manifest (refuses to change existing PNG bytes)
  python -I <this script> --out-dir <tmp>  # determinism re-check into another folder
"""

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import PIL
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PILOT_DIR = ROOT / "game/assets/characters/pixelorama-pilots"
SOURCE = PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-refinement-reference_m8-v01_20261014-230012-9b6c4a31.png"
SOURCE_SHA256 = "20c471b64b649c3de52c6e93a70b08f93e00598b73d4c361f9367d058144672c"
RUN = "m8-v01_20261014-231100"
OUTPUTS = {
    "inkline": f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-refine-inkline-candidate_{RUN}-fb830d80.png",
    "selout": f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-refine-selout-candidate_{RUN}-4d141ad5.png",
}
MANIFEST = f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-refinement-candidates-manifest_{RUN}-08c301fd.json"
REJECTED = {
    "boxquant": "rpg-2-star-ocean-the-second_protagonist-female_south-idle-boxquant-pilot_m8-v01_20261014-212322-7c30d48c.png",
    "lanczosquant": "rpg-2-star-ocean-the-second_protagonist-female_south-idle-lanczosquant-pilot_m8-v01_20261014-212322-b9fd58f7.png",
}

ALPHA_THRESHOLD = 128
BODY_H = 96
CELL = (80, 112)
PIN = (40, 104)
FEET_ROWS = 6
K = 40
SEED = 20261014
SIGMA_FRAC = 0.5
INK_THRESH = {"inkline": 0.42, "selout": 0.62}
MAX_COLOURS = 48

# Material groups over the 40 OKLab clusters, assigned once by inspecting cluster
# lightness/chroma/hue (cluster ids are stable for this source, seed and K).
GROUPS = {
    "ink": [24, 28, 11, 22, 25, 13, 1, 17],
    "dkn": [20, 3, 12],
    "brown": [19, 2, 36, 7, 30, 0, 16, 32],
    "leather": [33, 29, 37, 5],
    "skin": [21, 9, 15, 27],
    "cream": [34, 14, 4, 8, 35, 31],
    "teal": [23, 10, 26, 6, 39, 38],
    "grey": [18],
}
GROUP_NAMES = list(GROUPS)
# selout: number of shades kept per group (1-D weighted k-means on OKLab L).
RAMP_SHADES = {"ink": 1, "dkn": 2, "brown": 4, "leather": 3, "skin": 3, "cream": 3, "teal": 4, "grey": 1}

# Hand-specified colours not present as clusters (knee guard slate, buckle metal).
CUSTOM = {
    "slate_outline": (35, 37, 43),
    "slate_dark": (48, 51, 58),
    "slate_mid": (71, 75, 84),
    "slate_light": (98, 104, 115),
    "metal": (207, 200, 189),
}

# Local corrections. Each map is (left_col, top_row, rows); '.' keeps the sampled texel.
# Body-block coordinates (43 x 96 block before placement in the cell).
FACE_INKLINE = (17, 15, [
    ".......S...",
    "......SS...",
    "......SSs..",
    "......SHHs.",
    ".....SSSSs.",
    "..HH.SSKKK.",
    ".KKKSSSEWsK",
    ".SWESSdSSsK",
    ".sSSSSSSSdK",
    ".dSSSMMSsdK",
    ".KdsSSSsdK.",
    "..KKDDDKK..",
    "....DDD....",
])
FACE_SELOUT = (17, 15, [
    ".......S...",
    "......SS...",
    "......SSs..",
    "......SHHs.",
    ".....SSSSs.",
    "..HH.SSkks.",
    ".skkSSSEWsk",
    ".SWESSdSSsk",
    ".sdSSSSSdsk",
    ".dSSSMSSsdk",
    ".kdsSSSsdk.",
    "..kkDDDkk..",
    "....DDD....",
])
KNEE = (13, 66, [
    ".OOOOO.",
    "OGllgGO",
    "OGgttGO",
    "OGgtgBO",
    "OGggGBO",
    ".OGGGO.",
])

# Belt band with a 3x3 ring buckle and a small metal loop (reference waist, rows 46-48).
BELT = (18, 46, [
    "LBBBLLLLLL",
    "LBKBLLLBLL",
    "LBBBLLLLLL",
])

ROLE_CLUSTER = {"L": 2, "H": 12, "h": 36, "S": 27, "s": 15, "d": 9, "D": 21, "W": 35, "E": 33, "M": 37, "K": 22, "k": 3, "t": 38}
ROLE_CUSTOM = {"G": "slate_dark", "g": "slate_mid", "l": "slate_light", "B": "metal"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def to_oklab(rgb01):
    c = np.where(rgb01 <= 0.04045, rgb01 / 12.92, ((rgb01 + 0.055) / 1.055) ** 2.4)
    l = 0.4122214708 * c[..., 0] + 0.5363325363 * c[..., 1] + 0.0514459929 * c[..., 2]
    m = 0.2119034982 * c[..., 0] + 0.6806995451 * c[..., 1] + 0.1073969566 * c[..., 2]
    s = 0.0883024619 * c[..., 0] + 0.2817188376 * c[..., 1] + 0.6299787005 * c[..., 2]
    l, m, s = np.cbrt(l), np.cbrt(m), np.cbrt(s)
    return np.stack([
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    ], -1)


def cluster_source(rgba):
    """Deterministic k-means++ (K=40, 25 Lloyd iterations) on every 3rd opaque texel in OKLab."""
    mask = rgba[..., 3] >= ALPHA_THRESHOLD
    lab = to_oklab(rgba[..., :3] / 255.0)
    pts = lab[mask]
    sub = pts[::3]
    rng = np.random.default_rng(SEED)
    cent = [sub[rng.integers(len(sub))]]
    for _ in range(K - 1):
        d = np.min(((sub[:, None, :] - np.array(cent)[None]) ** 2).sum(-1), 1)
        cent.append(sub[rng.choice(len(sub), p=d / d.sum())])
    cent = np.array(cent)
    for _ in range(25):
        idx = np.argmin(((sub[:, None, :] - cent[None]) ** 2).sum(-1), 1)
        cent = np.array([sub[idx == k].mean(0) if (idx == k).any() else cent[k] for k in range(K)])
    labels = np.full(mask.shape, -1)
    idx = np.argmin(((pts[:, None, :] - cent[None]) ** 2).sum(-1), 1)
    labels[mask] = idx
    rgb = rgba[..., :3][mask]
    pal = np.array([rgb[idx == k].mean(0) for k in range(K)])
    counts = np.bincount(idx, minlength=K)
    return labels, cent, np.round(pal).astype(int), counts


def grid(rgba):
    mask = rgba[..., 3] >= ALPHA_THRESHOLD
    ys, xs = np.where(mask)
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    step = (y1 - y0) / BODY_H
    width = int(np.ceil((x1 - x0) / step))
    bx0 = (x0 + x1) / 2 - width * step / 2
    return {"bounds": [x0, y0, x1, y1], "step": step, "width": width, "bx0": bx0, "y0": y0}


def sample(labels, cent, g, ink_thresh):
    """Per texel: Gaussian-weighted material-group histogram; ink wins only above ink_thresh,
    otherwise the heaviest non-ink group; colour = that group's cluster nearest (OKLab) to the
    weighted mean of the group's pixels in the texel. Opaque if weighted coverage >= 0.5."""
    g_of = np.zeros(K, int)
    for gi, name in enumerate(GROUP_NAMES):
        for k in GROUPS[name]:
            g_of[k] = gi
    ink = GROUP_NAMES.index("ink")
    s, width, bx0, y0 = g["step"], g["width"], g["bx0"], g["y0"]
    out = np.full((BODY_H, width), -1)
    for i in range(BODY_H):
        for j in range(width):
            ya, yb = y0 + i * s, y0 + (i + 1) * s
            xa, xb = bx0 + j * s, bx0 + (j + 1) * s
            ys = np.arange(int(np.floor(ya)), int(np.ceil(yb)))
            xs = np.arange(int(np.floor(xa)), int(np.ceil(xb)))
            ys = ys[(ys + 0.5 >= ya) & (ys + 0.5 < yb) & (ys >= 0) & (ys < labels.shape[0])]
            xs = xs[(xs + 0.5 >= xa) & (xs + 0.5 < xb) & (xs >= 0) & (xs < labels.shape[1])]
            blk = labels[np.ix_(ys, xs)]
            wy = np.exp(-((ys + 0.5 - (ya + yb) / 2) ** 2) / (2 * (SIGMA_FRAC * s) ** 2))
            wx = np.exp(-((xs + 0.5 - (xa + xb) / 2) ** 2) / (2 * (SIGMA_FRAC * s) ** 2))
            w = wy[:, None] * wx[None]
            op = blk >= 0
            if w[op].sum() / w.sum() < 0.5:
                continue
            kl, ww = blk[op], w[op]
            gl = g_of[kl]
            gh = np.bincount(gl, weights=ww, minlength=len(GROUP_NAMES))
            if gh[ink] / gh.sum() >= ink_thresh:
                grp = ink
            else:
                gh[ink] = 0
                grp = int(np.argmax(gh))
            sel = gl == grp
            mean = (cent[kl[sel]] * ww[sel, None]).sum(0) / ww[sel].sum()
            cand = np.array(GROUPS[GROUP_NAMES[grp]])
            out[i, j] = int(cand[np.argmin(((cent[cand] - mean) ** 2).sum(-1))])
    return out, g_of


N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def neighbours(lab, i, j, offs):
    h, w = lab.shape
    return [lab[i + dy, j + dx] if 0 <= i + dy < h and 0 <= j + dx < w else -1 for dy, dx in offs]


def components(op):
    h, w = op.shape
    seen = np.zeros_like(op, bool)
    comps = []
    for i in range(h):
        for j in range(w):
            if op[i, j] and not seen[i, j]:
                stack, comp = [(i, j)], []
                seen[i, j] = True
                while stack:
                    y, x = stack.pop()
                    comp.append((y, x))
                    for dy, dx in N8:
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < h and 0 <= xx < w and op[yy, xx] and not seen[yy, xx]:
                            seen[yy, xx] = True
                            stack.append((yy, xx))
                comps.append(comp)
    return comps


def drop_orphans(lab, log, min_size=3):
    for comp in components(lab >= 0):
        if len(comp) < min_size:
            for y, x in comp:
                lab[y, x] = -1
            log.append({"op": "drop_orphan_component", "texels": [[x, y] for y, x in comp]})


def fill_pinholes(lab, log):
    for i in range(lab.shape[0]):
        for j in range(lab.shape[1]):
            if lab[i, j] < 0:
                n = neighbours(lab, i, j, N4)
                if all(v >= 0 for v in n):
                    vals, cnt = np.unique(n, return_counts=True)
                    lab[i, j] = int(vals[np.argmax(cnt)])
                    log.append({"op": "fill_pinhole", "texel": [j, i], "label": int(lab[i, j])})


def majority_clean(lab, g_of, protect, log, passes):
    """A texel whose material group has no 8-neighbour of the same group, while >= 5 of its
    8 neighbours share one other group, takes that group's most common neighbour cluster."""
    for p in range(passes):
        src = lab.copy()
        for i in range(lab.shape[0]):
            for j in range(lab.shape[1]):
                if src[i, j] < 0 or protect[i, j]:
                    continue
                n = [v for v in neighbours(src, i, j, N8) if v >= 0]
                if len(n) < 6:
                    continue
                me = g_of[src[i, j]]
                ng = [g_of[v] for v in n]
                if me in ng:
                    continue
                vals, cnt = np.unique(ng, return_counts=True)
                if cnt.max() >= 5:
                    gwin = vals[np.argmax(cnt)]
                    cands = [v for v in n if g_of[v] == gwin]
                    cv, cc = np.unique(cands, return_counts=True)
                    lab[i, j] = int(cv[np.argmax(cc)])
                    log.append({"op": "majority_clean", "pass": p, "texel": [j, i], "from": int(src[i, j]), "to": int(lab[i, j])})


def remove_spurs(lab, protect, log, passes):
    """selout only: opaque texels with <= 1 opaque 4-neighbour (1-texel strand tips) are cleared,
    except protected texels and the top/bottom body rows (keeps the 96-texel height)."""
    for p in range(passes):
        src = lab.copy()
        for i in range(1, lab.shape[0] - 1):
            for j in range(lab.shape[1]):
                if src[i, j] >= 0 and not protect[i, j]:
                    if sum(v >= 0 for v in neighbours(src, i, j, N4)) <= 1:
                        lab[i, j] = -1
                        log.append({"op": "remove_spur", "pass": p, "texel": [j, i], "from": int(src[i, j])})


def fill_notches(lab, log):
    """selout only: transparent texels with >= 3 opaque 4-neighbours take the most common
    neighbour cluster (rounds the silhouette mass; cannot extend the body height)."""
    src = lab.copy()
    for i in range(1, lab.shape[0] - 1):
        for j in range(lab.shape[1]):
            if src[i, j] < 0:
                n = [v for v in neighbours(src, i, j, N4) if v >= 0]
                if len(n) >= 3:
                    vals, cnt = np.unique(n, return_counts=True)
                    lab[i, j] = int(vals[np.argmax(cnt)])
                    log.append({"op": "fill_notch", "texel": [j, i], "label": int(lab[i, j])})


def ink_despeckle(lab, g_of, protect, log, max_ink_neighbours):
    """Interior ink texels with <= max_ink_neighbours ink 8-neighbours are line noise, not line
    intent: they take the most common non-ink 8-neighbour cluster."""
    ink = GROUP_NAMES.index("ink")
    src = lab.copy()
    edge = boundary(src >= 0)
    for i in range(lab.shape[0]):
        for j in range(lab.shape[1]):
            if src[i, j] < 0 or protect[i, j] or edge[i, j] or g_of[src[i, j]] != ink:
                continue
            n = [v for v in neighbours(src, i, j, N8) if v >= 0]
            if sum(g_of[v] == ink for v in n) <= max_ink_neighbours:
                other = [v for v in n if g_of[v] != ink]
                if other:
                    vals, cnt = np.unique(other, return_counts=True)
                    lab[i, j] = int(vals[np.argmax(cnt)])
                    log.append({"op": "ink_despeckle", "texel": [j, i], "from": int(src[i, j]), "to": int(lab[i, j])})


def shade_smooth(lab, g_of, protect, log, passes):
    """A texel whose exact cluster appears in none of its 4-neighbours, while one same-group
    cluster fills >= 3 of them, takes that cluster (flatter shade clusters, same material)."""
    for p in range(passes):
        src = lab.copy()
        for i in range(lab.shape[0]):
            for j in range(lab.shape[1]):
                if src[i, j] < 0 or protect[i, j]:
                    continue
                n = [v for v in neighbours(src, i, j, N4) if v >= 0]
                if src[i, j] in n:
                    continue
                vals, cnt = np.unique(n, return_counts=True) if n else (np.array([]), np.array([]))
                if len(cnt) and cnt.max() >= 3 and g_of[vals[np.argmax(cnt)]] == g_of[src[i, j]]:
                    lab[i, j] = int(vals[np.argmax(cnt)])
                    log.append({"op": "shade_smooth", "pass": p, "texel": [j, i], "from": int(src[i, j]), "to": int(lab[i, j])})


def boundary(op):
    h, w = op.shape
    b = np.zeros_like(op)
    for i in range(h):
        for j in range(w):
            if op[i, j]:
                for dy, dx in N4:
                    yy, xx = i + dy, j + dx
                    if not (0 <= yy < h and 0 <= xx < w) or not op[yy, xx]:
                        b[i, j] = True
                        break
    return b


def ramp_reduce(pal, cent, counts):
    """Per group, 1-D count-weighted k-means on OKLab L into RAMP_SHADES[g] shades; each
    cluster maps to its shade, shade colour = count-weighted mean sRGB of its clusters."""
    mapping, shades = {}, {}
    for name, ks in GROUPS.items():
        ks = sorted(ks, key=lambda k: cent[k, 0])
        n = min(RAMP_SHADES[name], len(ks))
        L = np.array([cent[k, 0] for k in ks])
        wts = np.array([counts[k] for k in ks], float)
        centres = np.quantile(L, np.linspace(0, 1, n)) if n > 1 else np.array([np.average(L, weights=wts)])
        for _ in range(50):
            a = np.argmin(np.abs(L[:, None] - centres[None]), 1)
            centres = np.array([np.average(L[a == c], weights=wts[a == c]) if (a == c).any() else centres[c] for c in range(n)])
        a = np.argmin(np.abs(L[:, None] - centres[None]), 1)
        shade_rgb = []
        for c in range(n):
            mem = [ks[t] for t in range(len(ks)) if a[t] == c]
            col = np.round(np.average(pal[mem], axis=0, weights=[counts[k] for k in mem])).astype(int)
            shade_rgb.append(tuple(int(v) for v in col))
            for k in mem:
                mapping[k] = tuple(int(v) for v in col)
        shades[name] = shade_rgb  # dark -> light
    return mapping, shades


def apply_map(rgb, op, spec, role_rgb, log, tag):
    left, top, rows = spec
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            y, x = top + r, left + c
            rgb[y, x] = role_rgb[ch]
            op[y, x] = True
            log.append({"op": tag, "texel": [x, y], "role": ch, "rgb": list(role_rgb[ch])})


def map_mask(shape, spec):
    m = np.zeros(shape, bool)
    left, top, rows = spec
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch != ".":
                m[top + r, left + c] = True
    return m


def place(rgb, op):
    """Lowest opaque row -> y = PIN_y - 1; x = PIN_x at the integer midpoint of the opaque span
    in the lowest FEET_ROWS body rows (same rule as the prior pilots, for harness parity)."""
    rows = np.where(op.any(1))[0]
    bottom = int(rows.max())
    feet = op[bottom - FEET_ROWS + 1: bottom + 1]
    cols = np.where(feet.any(0))[0]
    mid = (int(cols.min()) + int(cols.max()) + 1) // 2
    ox, oy = PIN[0] - mid, PIN[1] - 1 - bottom
    cell = np.zeros((CELL[1], CELL[0], 4), np.uint8)
    h, w = op.shape
    assert 0 <= ox and ox + w <= CELL[0] and 0 <= oy and oy + h <= CELL[1], "body block does not fit cell"
    cell[oy:oy + h, ox:ox + w, :3] = np.where(op[..., None], rgb, 0)
    cell[oy:oy + h, ox:ox + w, 3] = np.where(op, 255, 0)
    return cell, {"body_block_size": [w, h], "body_block_offset_in_cell": [ox, oy],
                  "feet_rows_used": FEET_ROWS, "feet_span_x_in_block": [int(cols.min()), int(cols.max())]}


def measure(cell):
    a = cell[..., 3]
    op = a == 255
    ys, xs = np.where(op)
    colours = sorted({tuple(int(v) for v in c) for c in cell[op][:, :3]})
    border = int(op[0].sum() + op[-1].sum() + op[:, 0].sum() + op[:, -1].sum())
    return {
        "size": [cell.shape[1], cell.shape[0]],
        "alpha_values_present": sorted(int(v) for v in np.unique(a)),
        "partial_alpha_texels": int(((a > 0) & (a < 255)).sum()),
        "transparent_texels_with_nonzero_rgb": int(((a == 0) & (cell[..., :3].any(-1))).sum()),
        "opaque_texels": int(op.sum()),
        "unique_opaque_rgb_colours": len(colours),
        "palette_hex": ["#%02x%02x%02x" % c for c in colours],
        "alpha_bounds_inclusive_xyxy": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
        "visible_body_height_texels": int(ys.max() - ys.min() + 1),
        "visible_body_width_texels": int(xs.max() - xs.min() + 1),
        "opaque_texels_on_cell_border": border,
        "lowest_opaque_row": int(ys.max()),
        "ground_pin": list(PIN),
        "isolated_opaque_texels_8n": int(sum(
            1 for y, x in zip(ys, xs)
            if not any(0 <= y + dy < cell.shape[0] and 0 <= x + dx < cell.shape[1] and op[y + dy, x + dx] for dy, dx in N8))),
    }


def build(variant, labels, cent, pal, counts, g):
    log = []
    lab, g_of = sample(labels, cent, g, INK_THRESH[variant])
    face = FACE_INKLINE if variant == "inkline" else FACE_SELOUT
    protect = map_mask(lab.shape, face) | map_mask(lab.shape, KNEE) | map_mask(lab.shape, BELT)
    drop_orphans(lab, log)
    fill_pinholes(lab, log)
    if variant == "selout":
        remove_spurs(lab, protect, log, passes=2)
        drop_orphans(lab, log)
        fill_notches(lab, log)
    majority_clean(lab, g_of, protect, log, passes=1 if variant == "inkline" else 2)
    ink_despeckle(lab, g_of, protect, log, max_ink_neighbours=0 if variant == "inkline" else 1)
    shade_smooth(lab, g_of, protect, log, passes=1 if variant == "inkline" else 2)
    op = lab >= 0
    if variant == "inkline":
        colour = {k: tuple(int(v) for v in pal[k]) for k in range(K)}
    else:
        colour, shades = ramp_reduce(pal, cent, counts)
    rgb = np.zeros(lab.shape + (3,), int)
    for (i, j), k in np.ndenumerate(lab):
        if k >= 0:
            rgb[i, j] = colour[k]
    # Silhouette outline on boundary texels (recolour inside the silhouette; height unchanged).
    edge = boundary(op) & ~protect
    ink_dark = tuple(int(v) for v in pal[22])
    for i, j in zip(*np.where(edge)):
        if variant == "inkline":
            new = ink_dark
        else:
            grp = GROUP_NAMES[g_of[lab[i, j]]]
            new = shades[grp][0]
        if tuple(rgb[i, j]) != new:
            log.append({"op": "outline", "texel": [int(j), int(i)], "from": [int(v) for v in rgb[i, j]], "to": list(new)})
            rgb[i, j] = new
    roles = {ch: colour[k] for ch, k in ROLE_CLUSTER.items()}
    roles.update({ch: CUSTOM[name] for ch, name in ROLE_CUSTOM.items()})
    roles["O"] = ink_dark if variant == "inkline" else CUSTOM["slate_outline"]
    if variant == "selout":
        roles["k"] = shades["dkn"][0]
    apply_map(rgb, op, face, roles, log, "face_map")
    apply_map(rgb, op, KNEE, roles, log, "knee_guard_map")
    apply_map(rgb, op, BELT, roles, log, "belt_map")
    for x, y in BUCKLES:
        log.append({"op": "buckle", "texel": [x, y], "from": [int(v) for v in rgb[y, x]], "to": list(roles["B"])})
        rgb[y, x] = roles["B"]
        op[y, x] = True
    cell, placement = place(rgb, op)
    summary = {}
    for entry in log:
        summary[entry["op"]] = summary.get(entry["op"], 0) + 1
    return cell, placement, log, summary


# Boot buckles (body-block texels), set to the metal colour in both candidates.
BUCKLES = [(16, 83), (17, 83), (34, 85), (35, 85)]


def cluster_metrics(cell):
    """Objective, method-independent texel statistics (same code for new and rejected PNGs).
    speckle: opaque texels whose RGB matches none of their opaque 8-neighbours.
    same_rgb_4adjacency: share of opaque-opaque 4-adjacent pairs with identical RGB.
    components: 4-connected same-RGB regions; mean size = opaque texels / components.
    silhouette_dark_share: boundary texels with OKLab L < 0.30 (edge separation from ground).
    face: largest skin component (OKLab L > 0.62, C > 0.06, hue 35-80 deg) in the top 32 body
    rows; inside its bbox, count dark feature texels (L < 0.35) and sclera-like texels
    (L > 0.85, C < 0.06), and report median skin L minus darkest feature L."""
    op = cell[..., 3] == 255
    rgb = cell[..., :3].astype(int)
    h, w = op.shape
    key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    key = np.where(op, key, -1)
    speckle = 0
    for y, x in zip(*np.where(op)):
        n = [key[y + dy, x + dx] for dy, dx in N8 if 0 <= y + dy < h and 0 <= x + dx < w and op[y + dy, x + dx]]
        if n and key[y, x] not in n:
            speckle += 1
    pairs = same = 0
    for a, b in ((key[:, :-1], key[:, 1:]), (key[:-1, :], key[1:, :])):
        both = (a >= 0) & (b >= 0)
        pairs += int(both.sum())
        same += int((both & (a == b)).sum())
    seen = np.zeros_like(op)
    comps = 0
    for y, x in zip(*np.where(op)):
        if seen[y, x]:
            continue
        comps += 1
        stack = [(y, x)]
        seen[y, x] = True
        while stack:
            cy, cx = stack.pop()
            for dy, dx in N4:
                yy, xx = cy + dy, cx + dx
                if 0 <= yy < h and 0 <= xx < w and not seen[yy, xx] and key[yy, xx] == key[cy, cx]:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
    lab = to_oklab(rgb / 255.0)
    L, C = lab[..., 0], np.hypot(lab[..., 1], lab[..., 2])
    hue = np.degrees(np.arctan2(lab[..., 2], lab[..., 1]))
    edge = boundary(op)
    top = int(np.where(op.any(1))[0].min())
    skin = op & (L > 0.62) & (C > 0.06) & (hue > 35) & (hue < 80)
    skin[top + 32:] = False
    face = {}
    best = max(components(skin), key=len, default=[])
    if best:
        ys, xs = zip(*best)
        y0, y1, x0, x1 = min(ys), max(ys), min(xs), max(xs)
        box = np.zeros_like(op)
        box[y0:y1 + 1, x0:x1 + 1] = True
        feat = box & op & (L < 0.35)
        sclera = box & op & (L > 0.85) & (C < 0.06)
        face = {"skin_bbox_xyxy": [int(x0), int(y0), int(x1), int(y1)], "skin_texels": len(best),
                "dark_feature_texels_in_bbox": int(feat.sum()), "sclera_like_texels_in_bbox": int(sclera.sum()),
                "skin_median_L": round(float(np.median(L[skin])), 3),
                "skin_minus_darkest_feature_L": round(float(np.median(L[skin]) - L[feat].min()), 3) if feat.any() else None}
    return {"opaque_texels": int(op.sum()), "unique_opaque_rgb_colours": int(len(np.unique(key[op]))),
            "speckle_texels": speckle, "speckle_share": round(speckle / int(op.sum()), 4),
            "same_rgb_4adjacency_share": round(same / pairs, 4), "same_rgb_components": comps,
            "mean_component_size": round(int(op.sum()) / comps, 3),
            "silhouette_boundary_texels": int(edge.sum()),
            "silhouette_dark_share": round(float((L[edge] < 0.30).mean()), 4), "face": face}


LIMITATIONS = [
    "Static south idle only (one frame per candidate); no walk, turn or other facings were made.",
    "The source is an imagegen concept with a soft, irregular ~8 px art grid (about 1.7 reference art pixels per output texel), so automated sampling still carries some reference noise; hand maps cover only the face, knee guard, belt and boot buckles.",
    "Material groups were assigned once by inspecting the 40 OKLab clusters; they are specific to this source, seed and K and would need re-assignment for any other source.",
    "The reference pose is a relaxed 3/4 stance with a head tilt and a backpack; that pose is kept, not re-drawn as a strict frontal south view.",
    "Face texel maps are a manual interpretation at 96 texels tall (eyes are 2x2 texels); they are a readability choice, not a measurement of the reference.",
    "selout removes 1-2 texel strand tips and fills notches, so its hair silhouette deliberately departs from the reference's loose strands.",
    "Body height is 96 texels shown at 0.5 scale (48 logical px, 96 window px at 1280x720); nothing was checked at other zoom levels.",
    "Not art-approved, not runtime-integrated, no registry/inventory/acceptance/progress/Game Bible change.",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=PILOT_DIR)
    ap.add_argument("--qa-report", type=Path, help="Godot capture report JSON to embed (path + SHA-256 per capture)")
    args = ap.parse_args()
    if sha256(SOURCE) != SOURCE_SHA256:
        sys.exit("source SHA-256 mismatch")
    rgba = np.array(Image.open(SOURCE).convert("RGBA")).astype(np.float64)
    labels, cent, pal, counts = cluster_source(rgba)
    g = grid(rgba)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    candidates = []
    for variant, name in OUTPUTS.items():
        cell, placement, log, summary = build(variant, labels, cent, pal, counts, g)
        path = args.out_dir / name
        im = Image.fromarray(cell, "RGBA")
        tmp = path.with_suffix(".tmp.png")
        im.save(tmp, optimize=False, compress_level=9)
        if path.exists() and path.read_bytes() != tmp.read_bytes():
            tmp.unlink()
            sys.exit(f"refusing to change existing bytes of {path.name}")
        tmp.replace(path)
        m = measure(cell)
        assert m["partial_alpha_texels"] == 0 and m["visible_body_height_texels"] == BODY_H
        assert m["unique_opaque_rgb_colours"] <= MAX_COLOURS and m["opaque_texels_on_cell_border"] == 0
        cm = cluster_metrics(cell)
        candidates.append({"variant": variant, "file": name, "format": "PNG RGBA 8-bit, single image, no metadata chunks",
                           "bytes": path.stat().st_size, "sha256": sha256(path), "placement": placement,
                           "measured": m, "cluster_metrics": cm, "edit_summary": summary,
                           "status": "technical candidate; unapproved; not runtime-integrated", "edits": log})
        print(f"{variant}: {name} {m['size']} h={m['visible_body_height_texels']} w={m['visible_body_width_texels']} "
              f"colours={m['unique_opaque_rgb_colours']} partial={m['partial_alpha_texels']} "
              f"isolated={m['isolated_opaque_texels_8n']} sha256={sha256(path)}")
        print(f"  edits={summary}")
        print(f"  metrics={json.dumps({k: v for k, v in cm.items()})}")
    rejected = []
    for variant, name in REJECTED.items():
        p = PILOT_DIR / name
        cm = cluster_metrics(np.array(Image.open(p).convert("RGBA")))
        rejected.append({"variant": variant, "file": name, "sha256": sha256(p), "cluster_metrics": cm,
                         "relationship": "read-only comparison baseline (user-rejected); not used as input"})
        print(f"rejected {variant}: metrics={json.dumps(cm)}")
    qa = None
    if args.qa_report:
        rep = json.loads(args.qa_report.read_text(encoding="utf-8"))
        qa = {"report": args.qa_report.name, "report_sha256": sha256(args.qa_report),
              "captures": [{k: c[k] for k in ("scene", "variant", "capture", "capture_sha256", "capture_size",
                                              "pilot_visible_logical", "pilot_window_diff_bounds_measured")}
                           for c in rep["captures"]]}
    manifest = {
        "project": "Worlds Between",
        "milestone": "M8",
        "purpose": "Two distinct single-frame female south-idle refinement candidates derived from the new imagegen refinement reference, after the user rejected both BOX/LANCZOS quantized pilots. Static frame only.",
        "status": "technical candidates only; unapproved; not integrated; idle frame only, no walk frames",
        "art_approved": False,
        "runtime_integrated": False,
        "walk_frames": 0,
        "unchanged": ["runtime art", "character registry", "inventory", "acceptance flags (0/52 sprites, 0/11 scene gates)",
                      "progress", "Game Bible", "git"],
        "source": {"role": "read-only input; imagegen concept, not a production sprite",
                   "file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"), "sha256": SOURCE_SHA256,
                   "size": [int(rgba.shape[1]), int(rgba.shape[0])], "bytes": SOURCE.stat().st_size,
                   "alpha_note": "Body alpha is mostly 250-254 with soft low-alpha haze; thresholded at alpha >= 128."},
        "generator": {"script": "tools/" + Path(__file__).name, "script_sha256": sha256(__file__),
                      "python": platform.python_version(), "pillow": PIL.__version__, "numpy": np.__version__,
                      "run_flags": "-I (isolated)", "deterministic": "fixed seed; re-run with --out-dir reproduces PNG bytes"},
        "identity_kept": ["female face with lashes", "high ponytail", "teal scarf + scarf tail", "boots with buckles",
                          "asymmetric knee guard on the viewer-left knee (slate, teal mark, metal buckle)",
                          "long brown coat, cream shirt, belt with ring buckle, teal bedroll"],
        "method": {
            "shared_steps": [
                "1. Verify source SHA-256; load RGBA; mask = alpha >= 128.",
                f"2. OKLab k-means (K={K}, k-means++ seed {SEED}, 25 Lloyd iterations, fit on every 3rd masked pixel) -> per-pixel cluster ids; cluster colour = mean sRGB of its pixels.",
                "3. Clusters grouped into 8 material groups (ink, dark-neutral, brown, leather, skin, cream, teal, grey) - fixed table GROUPS.",
                f"4. Texel grid: mask bounds height mapped to exactly {BODY_H} texels; width widened symmetrically to a whole texel count at the same step.",
                f"5. Per texel: Gaussian-weighted (sigma = {SIGMA_FRAC} x step) material histogram; opaque if weighted coverage >= 0.5; ink wins only if its weight share >= the candidate's ink threshold, else the heaviest non-ink group; colour = that group's cluster nearest (OKLab) to the weighted mean of the group's pixels. No colour blending across materials.",
                "6. Cleanup: drop opaque 8-components < 3 texels; fill single-texel pinholes; majority clean (texel with no same-group 8-neighbour and >= 5 neighbours of one other group); ink despeckle (interior ink with too few ink neighbours); shade smoothing (texel whose cluster is absent from its 4-neighbours while one same-group cluster fills >= 3).",
                "7. Silhouette outline: opaque boundary texels recoloured inside the silhouette (height unchanged).",
                "8. Hand-specified texel maps (FACE_*, KNEE, BELT, BUCKLES in the script) written last; these texels are protected from steps 6-7.",
                f"9. Placement on an {CELL[0]}x{CELL[1]} transparent cell: lowest opaque row at y={PIN[1] - 1}, feet-span midpoint at x={PIN[0]} (same rule as the rejected pilots). Transparent texels are RGBA 0,0,0,0.",
                "10. Save PNG RGBA (optimize=False, compress_level=9); refuse to change existing bytes.",
            ],
            "inkline": {"ink_threshold": INK_THRESH["inkline"], "majority_passes": 1, "ink_despeckle_max_ink_neighbours": 0,
                        "shade_smooth_passes": 1, "outline": "near-black cluster 22 on every silhouette boundary texel",
                        "palette": "raw OKLab clusters actually used + custom slate/metal", "face": "black lashes with outer flicks, 2x2 eyes with sclera + brown iris, brow, nose shadow, 2-texel mouth"},
            "selout": {"ink_threshold": INK_THRESH["selout"], "spur_removal_passes": 2, "notch_fill": True, "majority_passes": 2,
                       "ink_despeckle_max_ink_neighbours": 1, "shade_smooth_passes": 2,
                       "outline": "selective: each boundary texel takes the darkest shade of its own material ramp",
                       "palette": "ramp-reduced: per-group 1-D weighted k-means on OKLab L, shades " + json.dumps(RAMP_SHADES),
                       "face": "dark-brown lashes without flicks, 2x2 eyes with sclera + iris, cheek blush texels, 1-texel mouth"},
            "custom_colours": {k: "#%02x%02x%02x" % v for k, v in CUSTOM.items()},
            "not_used": "No Pillow BOX/LANCZOS resize, no median-cut quantize, no AI image editing, no dithering.",
        },
        "grid": {k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in g.items()},
        "source_clusters_hex": ["#%02x%02x%02x" % tuple(c) for c in pal],
        "source_cluster_pixel_counts": [int(c) for c in counts],
        "candidates": candidates,
        "rejected_baselines": rejected,
        "qa_captures": qa,
        "limitations": LIMITATIONS,
        "review": {"user_or_codex_review": "not done", "assessment": "Technical measurements only; visual judgement is Codex's/the user's."},
    }
    (args.out_dir / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("MANIFEST " + str(args.out_dir / MANIFEST))


if __name__ == "__main__":
    main()
