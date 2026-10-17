"""UNAPPROVED candidate v06: NYC City Hall Park (Lower Manhattan, 2537 science hub), one native 640x360 gameplay scene.

ONE bounded pass after Codex judged v05 (run nyc-chp-v05_20261017-015916-23a7984f, kept untouched as the audit
baseline) a flat, procedural park with a hero-height City Hall, generic skyline, regular paving, sparse props and a
near-invisible hero beneath the NE elm.

SOURCE HONESTY. Most visible pixels of this candidate come from an IMPORTED GENERATED SOURCE: the nonruntime,
AI-generated art-direction reference
  outputs/rpg-2-star-ocean-the-second_nyc-city-hall-park_style-alignment-reference_nonruntime-v01_20261016-225515-5ee8060c.png
(sha256 4a029b72..., 1672x941). This tool recomposes it for the real game frame (header rows 0-61 and footer rows
318+ are covered by the runtime UI, so the reference is box-recomposed in two bands: ref rows 0-425 -> rows 62-171,
ref rows 425-860 -> rows 172-317), palette-reduces it with deterministic k-means and a cluster (despeckle) pass, then
splits it into named Pixelorama/OpenRaster layers and adds NATIVE work on top: the walk network (promenade, fountain
links, terrace walk, report plaza, kiosk apron) with curbs, lawn/hedge in-painting where props were removed, a moved
east elm, a public-works survey kiosk, the ledger board, the gate-pier inspection panel, the double-numbered sign with
its teal/amber pavement lines, teal inlays, cupola patina, collision and Y-sort occluders. It is NOT wholly
hand-painted and must never be described that way. The manifest records the per-layer origin and pixel shares.

Modes:  preview <dir outside repo> | build | check [--no-pixelorama] [--write-report]
Run with: <python> -I -B <this file> <mode> ...
"""
import argparse, hashlib, io, json, math, os, shutil, subprocess, sys, tempfile, time, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG, AREA = "rpg-2-star-ocean-the-second", "nyc-city-hall-park"
VER, STAMP, RUN_ID = "unapproved-v06", "20261017-165253", "4519dffe"
RUN = f"nyc-chp-v06_{STAMP}-{RUN_ID}"
CAND_REL = f"game/assets/environments/candidates/{RUN}"
OUT_REL = f"outputs/{RUN}"
REF_REL = ("outputs/rpg-2-star-ocean-the-second_nyc-city-hall-park_style-alignment-reference_nonruntime-v01_"
           "20261016-225515-5ee8060c.png")
REF_SHA = "4a029b723174212db0ea2fd1dc02c6b3d0801c70479bbbab23067762c780e01c"
V05_DIR_REL = "game/assets/environments/candidates/nyc-chp-v05_20261017-015916-23a7984f"
HEROINE_REL = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_"
               "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
PIXELORAMA_DEFAULT = "C:/Users/hkzha/AppData/Local/Programs/Pixelorama-1.2.3/Pixelorama-Windows-64bit/Pixelorama.exe"
W, H = 640, 360
UI_TOP, UI_BOTTOM = 62, 318
WIN_LONG_PREFIX = "\\\\?\\"
YY, XX = np.mgrid[0:H, 0:W]


def fname(purpose, ext):
    return f"{SLUG}_{AREA}_{purpose}_{VER}_{STAMP}-{RUN_ID}.{ext}"


def _fs(path):
    path = os.path.abspath(path)
    if os.name == "nt" and len(path) > 247 and not path.startswith(WIN_LONG_PREFIX):
        return WIN_LONG_PREFIX + path
    return path


def rp(rel):
    return os.path.join(REPO, *rel.split("/"))


def read_bytes(p):
    with open(_fs(p), "rb") as f:
        return f.read()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_text(b):
    return hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()


def rng(*key):
    return np.random.Generator(np.random.PCG64(int.from_bytes(hashlib.sha256(repr(key).encode()).digest()[:8], "little")))


def new():
    return np.full((H, W), -1, np.int16)


def ell(cx, cy, rx, ry):
    return ((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2 <= 1.0


def box(x0, y0, x1, y1):
    """Half-open box: x0 <= x < x1, y0 <= y < y1."""
    return (XX >= x0) & (XX < x1) & (YY >= y0) & (YY < y1)


def poly_mask(pts):
    """Even-odd point-in-polygon on pixel centres (pure numpy, deterministic)."""
    px, py = XX + 0.5, YY + 0.5
    inside = np.zeros((H, W), bool)
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if y1 == y2:
            continue
        cond = (py >= min(y1, y2)) & (py < max(y1, y2))
        xint = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
        inside ^= cond & (px < xint)
    return inside


def shift(m, dx, dy, fill=False):
    out = np.full_like(m, fill)
    ys = slice(max(0, dy), H + min(0, dy)); yd = slice(max(0, -dy), H + min(0, -dy))
    xs = slice(max(0, dx), W + min(0, dx)); xd = slice(max(0, -dx), W + min(0, -dx))
    out[ys, xs] = m[yd, xd]
    return out


def dilate(m, r=1):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= shift(m, dx, dy)
    return out


def erode(m, r=1):
    return ~dilate(~m, r)


def edge(m):
    return m & ~erode(m, 1)


# ============================================================================ reference -> recomposed underpainting
REF_BANDS = [  # (ref y0, ref y1) -> (screen y0, rows)
    ((0, 425), (62, 110)),     # sky, skyline, City Hall, fence      sx 0.383 sy 0.259
    ((425, 860), (172, 146)),  # park                                 sx 0.383 sy 0.336
    ((860, 941), (318, 27)),   # bottom sidewalk (under the footer; also the paving texture source)
]


def load_reference():
    b = read_bytes(rp(REF_REL))
    if sha(b) != REF_SHA:
        raise SystemExit("reference hash mismatch")
    return Image.open(io.BytesIO(b)).convert("RGB")


def underpainting(ref):
    u = np.zeros((H, W, 3), np.float64)
    for (r0, r1), (s0, rows) in REF_BANDS:
        part = ref.crop((0, r0, ref.size[0], r1)).resize((W, rows), Image.LANCZOS)
        u[s0:s0 + rows] = np.asarray(part, np.float64)
    u[:UI_TOP] = u[UI_TOP]                          # under the header: repeat the first visible sky row
    u[345:] = u[318:333][::-1][:H - 345]            # under the footer: mirror the sidewalk courses
    return u


# ============================================================================ palette: k-means on the underpainting + native accents
K_REF = 72
ACCENTS = {  # hand-picked native colours (added after k-means; used only by native layers)
    "teal-glow": "6fe8e0", "teal-core": "c8fff6", "teal-deep": "1d6f74", "amber-line": "e8a640",
    "amber-deep": "9a5a24", "patina-hi": "a9c9b4", "patina-mid": "6f9a86", "patina-lo": "3f6559",
    "iron-dark": "1c2426", "iron-mid": "34403f", "glass-hi": "b8dcd8", "paper": "efe4c6",
    "paper-shade": "c9b994", "ink": "3a3a4a", "stamp": "b0443a", "curb-hi": "e6d6b4",
}


def kmeans_palette(u):
    a = u[UI_TOP:UI_BOTTOM].reshape(-1, 3).astype(np.float32)
    g = np.random.Generator(np.random.PCG64(2537))
    cent = a[g.choice(len(a), K_REF, replace=False)].copy()
    for _ in range(24):
        lab = nearest_idx(a, cent)
        sums = np.zeros_like(cent); cnt = np.zeros(K_REF)
        np.add.at(sums, lab, a); np.add.at(cnt, lab, 1)
        nz = cnt > 0
        cent[nz] = sums[nz] / cnt[nz, None]
    cent = np.round(cent).clip(0, 255).astype(np.int32)
    # deterministic order: dark -> light
    order = np.argsort(cent @ np.array([299, 587, 114]), kind="stable")
    return [tuple(int(v) for v in cent[i]) for i in order]


def nearest_idx(a, cent):
    out = np.empty(len(a), np.int32)
    c = np.asarray(cent, np.float32)
    for s in range(0, len(a), 65536):
        d = ((a[s:s + 65536, None, :] - c[None]) ** 2).sum(-1)
        out[s:s + 65536] = d.argmin(1)
    return out


def quantize(u, pal):
    return nearest_idx(u.reshape(-1, 3).astype(np.float32), np.array(pal, np.float32)).reshape(u.shape[:2]).astype(np.int16)


def despeckle(idx, pal, limit=46.0):
    """Cluster pass: a pixel with no same-index 4-neighbour takes its 8-neighbour majority when that colour is close.
    High-contrast singles (window lights, flower heads, lamp glints) are kept on purpose."""
    rgb = np.array(pal, np.float64)
    out = idx.copy()
    p = np.pad(idx, 1, mode="edge")
    n4 = [p[0:-2, 1:-1], p[2:, 1:-1], p[1:-1, 0:-2], p[1:-1, 2:]]
    lonely = np.ones(idx.shape, bool)
    for n in n4:
        lonely &= n != idx
    n8 = np.stack([p[dy:dy + H, dx:dx + W] for dy in range(3) for dx in range(3) if (dy, dx) != (1, 1)])
    ys, xs = np.nonzero(lonely)
    for y, x in zip(ys, xs):
        vals, cnts = np.unique(n8[:, y, x], return_counts=True)
        m = vals[np.argmax(cnts)]
        if cnts.max() >= 3 and np.linalg.norm(rgb[m] - rgb[idx[y, x]]) < limit:
            out[y, x] = m
    return out


class Pal:
    def __init__(self, ref_cols):
        self.cols = list(ref_cols) + [tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) for h in ACCENTS.values()]
        self.names = [f"ref{i:02d}" for i in range(len(ref_cols))] + list(ACCENTS)
        self.rgb = np.array(self.cols, np.float64)
        self.n_ref = len(ref_cols)
        self.I = {n: i for i, n in enumerate(self.names)}

    def near(self, hexcol, ref_only=True):
        c = np.array([int(hexcol[i:i + 2], 16) for i in (0, 2, 4)], np.float64)
        pool = self.rgb[:self.n_ref] if ref_only else self.rgb
        return int(((pool - c) ** 2).sum(1).argmin())

    def lum(self):
        return self.rgb @ np.array([0.299, 0.587, 0.114])

    def lut(self, scale, add=(0, 0, 0), ref_only=True):
        """Index -> index map of a colour transform (shadow / glow), restricted to reference colours."""
        tgt = (self.rgb * np.array(scale) + np.array(add)).clip(0, 255)
        pool = self.rgb[:self.n_ref] if ref_only else self.rgb
        return np.array([int(((pool - t) ** 2).sum(1).argmin()) for t in tgt], np.int16)


# ============================================================================ scene geometry (screen pixels; feet = actor foot anchor)
HOTSPOTS = {"spawn": (340, 253), "liang_xu": (282, 180), "trace_0": (285, 267), "trace_1": (378, 181),
            "assist": (120, 187), "survey": (558, 166), "report": (470, 247)}
INTERACT_RADIUS = {"liang_xu": 50, "trace_0": 34, "trace_1": 34, "assist": 40, "survey": 43, "report": 50}
LEGACY_SPAWN = (82, 260)          # pre-navigation generic SPAWN still found in old city saves
LEGACY_LANDING = (82, 203.5)      # where the old plate's recovery put it; kept standable on purpose (west apron)
FOUNT = (171, 265)
PLAZA_R = (477, 260)
ELM_SHIFT = (150, 21)             # east elm moved to the SE lower lawn: no hotspot, marker or fixture under its crown
ELM_PIVOT = 284 + 21              # trunk base row after the move
LAMPS_PROMENADE = [(212, 216), (420, 216)]
REVEAL = {"radius": [15, 27], "lift": 22, "max_hole": 0.85}


def walk_regions():
    r = {}
    r["promenade"] = box(58, 180, 597, 204)
    r["west-apron"] = box(58, 180, 101, 213)
    r["kiosk-apron"] = box(542, 152, 577, 180)
    r["fountain-link"] = box(152, 203, 189, 224)
    r["fountain-plaza"] = ell(170, 262, 80, 42) & ~ell(FOUNT[0], FOUNT[1], 52, 25)
    r["west-link"] = box(250, 244, 299, 273)
    r["axis"] = box(298, 204, 342, 307)
    r["terrace-walk"] = box(341, 249, 461, 269)
    r["report-link"] = box(452, 203, 489, 251)
    r["report-plaza"] = ell(PLAZA_R[0], PLAZA_R[1], 32, 15)
    return r


OBSTACLES = {   # solid bases inside paved areas (feet may not enter)
    "lamp-plaza-w": box(89, 264, 102, 275), "lamp-plaza-e": box(248, 263, 261, 275),
    "bollard-plaza": box(216, 221, 229, 231), "report-terminal": box(492, 252, 517, 268),
    "lamp-axis-e": box(337, 242, 348, 251),
    "bollard-tw-s": box(338, 265, 349, 275), "sign-trace-0": box(265, 239, 278, 248),
}


def walk_mask():
    r = walk_regions()
    m = np.zeros((H, W), bool)
    for v in r.values():
        m |= v
    for v in OBSTACLES.values():
        m &= ~v
    m[:UI_TOP + 48] = False
    m[UI_BOTTOM - 11:] = False
    return m


# visual paving footprints (feet regions grown by the shoe margin)
def paving_regions():
    p = {}
    p["promenade"] = box(52, 177, 603, 210)
    p["west-apron"] = box(48, 177, 106, 218)
    p["kiosk-apron"] = box(536, 148, 583, 180)
    p["fountain-link"] = box(146, 205, 195, 229)
    p["west-link"] = box(250, 239, 298, 277)
    p["terrace-walk"] = box(345, 244, 452, 274)
    p["report-link"] = box(446, 206, 495, 247)
    p["report-plaza"] = ell(PLAZA_R[0], PLAZA_R[1], 41, 21)
    return p


CITY_HALL_POLY = [(146, 86), (238, 86), (238, 80), (296, 80), (300, 62), (342, 62), (346, 80), (404, 80), (404, 86),
                  (494, 86), (494, 152), (146, 152)]


# ============================================================================ sprite masks cut from the quantized underpainting
def class_masks(ui, pal):
    """Palette-index votes: which reference colours occur in sampled crown interiors vs sampled open lawn."""
    crown_s = box(400, 176, 470, 214) | box(70, 92, 130, 150) | box(520, 110, 590, 170)
    lawn_s = box(350, 286, 392, 312) | box(110, 190, 150, 204) | box(560, 286, 584, 306)
    n = len(pal.cols)
    c = np.bincount(ui[crown_s].ravel(), minlength=n).astype(float)
    l = np.bincount(ui[lawn_s].ravel(), minlength=n).astype(float)
    crown_only = c > 3 * l + 2
    lawn_only = l > 3 * c + 2
    return crown_only, lawn_only


def smooth_vote(score, r=2):
    acc = np.zeros(score.shape)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            acc += shift(score, dx, dy, 0.0)
    return acc


def fill_holes(m):
    outside = np.zeros_like(m)
    stack = [(y, x) for y in (0, H - 1) for x in range(W) if not m[y, x]] + \
            [(y, x) for x in (0, W - 1) for y in range(H) if not m[y, x]]
    for y, x in stack:
        outside[y, x] = True
    while stack:
        y, x = stack.pop()
        for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= yy < H and 0 <= xx < W and not m[yy, xx] and not outside[yy, xx]:
                outside[yy, xx] = True
                stack.append((yy, xx))
    return ~outside


ELM_CROWN = [(366, 212), (366, 199), (371, 189), (379, 181), (391, 177), (404, 174), (420, 171), (436, 169),
             (452, 167), (468, 165), (484, 165), (498, 169), (507, 178), (509, 192), (506, 205), (499, 213),
             (487, 218), (470, 221), (455, 226), (444, 231), (432, 231), (420, 226), (407, 224), (395, 221),
             (382, 220), (372, 217)]
ELM_TRUNK = [(396, 219), (412, 222), (424, 224), (432, 232), (427, 244), (425, 262), (426, 278), (433, 287),
             (430, 291), (406, 291), (403, 286), (407, 276), (408, 256), (406, 238), (398, 228)]


def elm_mask(ui, pal):
    """Hand-traced crown (kept just inside the true leaf outline) + trunk with roots; bark pixels only in the trunk."""
    crown = erode(poly_mask(ELM_CROWN), 1)
    rgb = pal.rgb[ui]
    bark = (rgb[..., 0] > rgb[..., 2] + 14) & (rgb[..., 0] >= rgb[..., 1] - 10) & (rgb[..., 0] < 215)
    trunk = poly_mask(ELM_TRUNK) & (bark | (pal.lum()[ui] < 70))
    trunk = trunk | (poly_mask(ELM_TRUNK) & dilate(trunk, 1) & erode(dilate(trunk, 1), 1))
    return crown, trunk


PROP_MASKS = {
    # name: (polygon, pivot row, kind)
    "fountain-centre": ([(152, 214), (192, 214), (194, 252), (150, 252)], 262, "prop"),
    "lamp-plaza-w": ([(87, 212), (104, 212), (104, 273), (87, 273)], 273, "prop"),
    "lamp-plaza-e": ([(246, 216), (263, 216), (263, 273), (246, 273)], 273, "prop"),
    "bollard-plaza": ([(216, 204), (229, 204), (229, 229), (216, 229)], 229, "prop"),
    "lamp-axis-e": ([(337, 219), (348, 219), (348, 249), (337, 249)], 249, "prop"),
    "bollard-junction-se": ([(338, 260), (349, 260), (349, 276), (338, 276)], 275, "prop"),
}


def prop_mask(ui, pal, pts):
    """Prop pixels inside a hand polygon: everything that is not paving/lawn background (by local contrast to the
    polygon's own dominant ground colours)."""
    region = poly_mask(pts)
    vals, cnts = np.unique(ui[region], return_counts=True)
    rgb = pal.rgb[ui]
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    sat = rgb.max(-1) - rgb.min(-1)
    dark = lum < 70
    teal = (rgb[..., 2] > rgb[..., 0] + 40) & (rgb[..., 1] > rgb[..., 0] + 30)
    warm_glow = (rgb[..., 0] > 200) & (rgb[..., 1] > 150) & (rgb[..., 2] < 140)
    return region, dark | teal | warm_glow | (sat < 26) & (lum > 150)


# ============================================================================ native painters
def stone_ramp(ui, pal, region, min_share=0.015):
    vals, cnts = np.unique(ui[region], return_counts=True)
    lum = pal.lum()
    keep = [int(v) for v, c in zip(vals, cnts) if c / cnts.sum() >= min_share and 55 < lum[v] < 236]
    return sorted(keep, key=lambda k: (lum[k], k))


def flag_ids(key, course=6, wmin=8, wmax=19, y0=0):
    """Running-bond flag ids for the whole canvas (course index * 1000 + slab index)."""
    g = rng("flag-ids", key)
    ids = np.zeros((H, W), np.int32)
    tones = {}
    for c in range(-1, H // course + 2):
        bounds, x = [], -int(g.integers(0, wmax))
        while x < W:
            x += int(g.integers(wmin, wmax + 1))
            bounds.append(x)
        s = np.searchsorted(np.array(bounds), np.arange(W), side="right")
        ya, yb = max(0, y0 + c * course), min(H, y0 + (c + 1) * course)
        if ya < yb:
            ids[ya:yb] = (c + 1) * 1000 + s[None, :]
    return ids


def ring_ids(cx, cy, sy, ring=5, seg_px=11):
    dx, dy = XX - cx + 0.5, (YY - cy + 0.5) / sy
    r = np.hypot(dx, dy)
    ri = (r // ring).astype(np.int32)
    nseg = np.maximum(6, np.round(2 * np.pi * (ri + 0.5) * ring / seg_px)).astype(np.int32)
    th = (np.arctan2(dy, dx) + np.pi) / (2 * np.pi)
    si = np.floor(th * nseg).astype(np.int32) % nseg
    return ri * 1000 + si


def paint_ids(out, mask, ids, ramp, key, light=0.55, spread=0.24, grain=0.09):
    """Per-stone tone from a reference ramp, dark joint on bottom/right edges, lit lip on top/left edges,
    sparse grain and broad wear. Writes only inside `mask`."""
    g = rng("paint-ids", key)
    n = len(ramp)
    uniq = np.unique(ids[mask])
    tone = {}
    for u in uniq.tolist():
        tone[u] = int(np.clip(round(g.normal((n - 1) * light, (n - 1) * spread)), 1, n - 2))
    lut_keys = np.array(list(tone.keys()))
    lut_vals = np.array([tone[k] for k in lut_keys])
    order = np.argsort(lut_keys)
    k = lut_vals[order][np.searchsorted(lut_keys[order], np.where(mask, ids, lut_keys.min()))]
    rnd = rng("grain", key).random((H, W))
    wear = low_freq(("wear", key), 22) > 0.62
    k = np.where(rnd < grain, k - 1, np.where(rnd > 1 - grain * 0.5, k + 1, k))
    k = np.where(wear, k - 1, k)
    right = ids != shift(ids, -1, 0, -1)
    below = ids != shift(ids, 0, -1, -1)
    above = ids != shift(ids, 0, 1, -1)
    left = ids != shift(ids, 1, 0, -1)
    k = np.where((above | left) & (k <= n - 3), k + 1, k)
    k = np.where(right, k - 1, k)
    k = np.where(below, np.minimum(k - 2, 2), k)
    k = np.clip(k, 0, n - 1)
    rampa = np.array(ramp)
    out[mask] = rampa[k[mask]]


def low_freq(key, scale=24):
    g = rng("lowfreq", key)
    gh, gw = H // scale + 2, W // scale + 2
    coarse = g.random((gh, gw))
    yy, xx = YY / scale, XX / scale
    y0, x0 = yy.astype(int), xx.astype(int)
    fy, fx = yy - y0, xx - x0
    fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
    a = coarse[y0, x0] * (1 - fx) + coarse[y0, x0 + 1] * fx
    b = coarse[y0 + 1, x0] * (1 - fx) + coarse[y0 + 1, x0 + 1] * fx
    return a * (1 - fy) + b * fy


def not_green(ui, pal):
    rgb = pal.rgb[ui]
    return ~((rgb[..., 1] > rgb[..., 0] + 8) & (rgb[..., 1] > rgb[..., 2] + 8))


def tile(dst_mask, src, ox=0, oy=0, mirror=True):
    out = new()
    sh, sw = src.shape
    ys, xs = np.nonzero(dst_mask)
    ty, tx = (ys - oy), (xs - ox)
    by, bx = ty // sh, tx // sw
    iy, ix = ty % sh, tx % sw
    if mirror:
        iy = np.where(by % 2 == 1, sh - 1 - iy, iy)
        ix = np.where(bx % 2 == 1, sw - 1 - ix, ix)
    out[ys, xs] = src[iy, ix]
    return out


def move_into(dst, ui, m, dx, dy):
    sval = np.where(m, ui, -1).astype(np.int16)
    moved = shift(m, dx, dy)
    sv = shift(sval, dx, dy, -1)
    dst[moved] = sv[moved]
    return moved


# ============================================================================ build the scene
def scene():
    ref = load_reference()
    u = underpainting(ref)
    pal = Pal(kmeans_palette(u))
    ui = despeckle(quantize(u, pal.cols), pal.cols)
    P = pal.I
    near = pal.near
    lum = pal.lum()

    layers, order, ysort, origin = {}, [], {}, {}

    def add(name, arr, kind, pivot=None):
        layers[name] = arr; order.append(name); origin[name] = kind
        if pivot is not None:
            ysort[name] = pivot

    # ---------------------------------------------------------------- reference layers (imported generated source)
    ch = poly_mask(CITY_HALL_POLY)
    top = YY < 177
    L = new(); L[top & ~ch] = ui[top & ~ch]; add("ref-backdrop-skyline-treeline-fence", L, "imported-reference")
    L = new(); L[ch] = ui[ch]; add("ref-city-hall", L, "imported-reference")
    L = new(); L[~top] = ui[~top]; add("ref-park-ground", L, "imported-reference")

    # ---------------------------------------------------------------- cut sprites before any edit
    crown, trunk = elm_mask(ui, pal)
    props = {}
    for name, (pts, pivot, _) in PROP_MASKS.items():
        region, fg = prop_mask(ui, pal, pts)
        m = region & fg
        m = m | (region & dilate(m, 1) & ~fg & (lum[ui] < 120))
        props[name] = (m, pivot)
    ng = not_green(ui, pal)
    term_m = box(261, 270, 282, 302) & ng
    cart_m = poly_mask([(466, 272), (520, 272), (520, 318), (466, 318)]) & ng & (YY >= 272)
    bench_m = box(364, 240, 392, 252) & ng

    # ---------------------------------------------------------------- texture sources (quantized underpainting)
    lawn_src = ui[284:313, 348:392]
    hedge_src = ui[179:192, 206:288]
    cobble_src = ui[252:268, 350:450]
    flags = stone_ramp(ui, pal, box(300, 206, 338, 300))
    warm = stone_ramp(ui, pal, ell(171, 265, 88, 48) & ~ell(171, 265, 56, 29) & (YY > 285))

    # ---------------------------------------------------------------- in-painting where props / trunks are removed
    fill = new()
    hedge_zone = box(50, 168, 151, 177) | box(489, 152, 536, 177) | box(583, 152, 604, 177)
    f = tile(hedge_zone, hedge_src, 50, 164); fill[hedge_zone] = f[hedge_zone]
    lawn_zone = box(348, 209, 600, 244) | box(398, 283, 438, 300) | box(255, 277, 292, 303)
    f = tile(lawn_zone, lawn_src, 348, 209); fill[lawn_zone] = f[lawn_zone]
    # beds and a bench back onto the new lawns (moved clusters of the reference beds)
    for (sx0, sy0, sx1, sy1), (dx, dy) in [((488, 226, 540, 244), (56, -4)), ((230, 288, 256, 304), (30, -8)),
                                           ((440, 262, 470, 282), (-90, -50))]:
        src = ui[sy0:sy1, sx0:sx1]
        dst = fill[sy0 + dy:sy1 + dy, sx0 + dx:sx1 + dx]
        keep = not_green(src, pal) | (lum[src] > 150) | (lum[src] < 45)
        dst[keep] = src[keep]
    move_into(fill, ui, bench_m, 0, -9)
    add("inpaint-lawn-hedge", fill, "imported-reference-recomposed")

    # ---------------------------------------------------------------- native walk network
    walks = new()
    pv = paving_regions()
    curb_hi, lawn_shadow = P["curb-hi"], near("34501e")
    ids_a = flag_ids("promenade", course=6, wmin=10, wmax=24, y0=180)
    main = pv["promenade"] | pv["west-apron"] | pv["kiosk-apron"] | pv["fountain-link"] | pv["report-link"]
    paint_ids(walks, main, ids_a, flags, "promenade")
    border = (box(52, 177, 603, 180) | box(52, 206, 603, 210) | box(536, 148, 583, 151)) & main
    paint_ids(walks, border, flag_ids("border", course=3, wmin=5, wmax=9, y0=177), warm, "border", light=0.62,
              spread=0.16, grain=0.04)
    ids_b = flag_ids("links", course=5, wmin=8, wmax=15, y0=239)
    paint_ids(walks, pv["west-link"] | pv["terrace-walk"], ids_b, flags, "links")
    rp_m = pv["report-plaza"]
    paint_ids(walks, rp_m, ring_ids(PLAZA_R[0], PLAZA_R[1], 21 / 41, ring=5, seg_px=10), warm, "report-plaza",
              light=0.6, spread=0.2)
    walks[rp_m & ~ell(PLAZA_R[0], PLAZA_R[1], 39, 19)] = near("c7b08a")
    allpave = np.zeros((H, W), bool)
    for m in pv.values():
        allpave |= m
    # curbs: lit lip along south edges, dark grass shadow below; grass overhang on north edges
    south_lip = allpave & ~shift(allpave, 0, -1)
    walks[south_lip & (YY > 180)] = curb_hi
    below = shift(south_lip, 0, 1) & ~allpave & (YY > 180) & (YY < UI_BOTTOM)
    walks[below] = lawn_shadow
    north_edge = allpave & ~shift(allpave, 0, 1) & (YY > 200)
    tufts = north_edge & (rng("tufts").random((H, W)) < 0.45)
    walks[tufts] = near("4e7a2a")
    vert = allpave & (~shift(allpave, 1, 0) | ~shift(allpave, -1, 0)) & (YY > 147) & ~south_lip
    walks[vert] = flags[2]
    # cool shade under the fence base and the hedge line (light comes from the upper left)
    shade = pal.lut((0.74, 0.80, 0.88), (0, 4, 12))
    sh_m = box(52, 177, 603, 180) & allpave
    walks[sh_m] = shade[walks[sh_m]]
    # terrace retaining wall face under the terrace walk (reference cobble texture, re-laid)
    face = box(345, 274, 437, 283)
    t = tile(face, cobble_src, 345, 274); walks[face] = t[face]
    walks[box(345, 283, 437, 284)] = lawn_shadow
    add("native-walks", walks, "native")

    # ---------------------------------------------------------------- native ground detail
    det = new()
    teal, teal_core, teal_deep = P["teal-glow"], P["teal-core"], P["teal-deep"]
    amber, amber_deep = P["amber-line"], P["amber-deep"]
    for x in range(76, 600, 48):                      # promenade teal inlay studs (2537 lighting)
        if 280 <= x <= 356:
            continue
        det[184, x:x + 3] = teal_deep; det[184, x + 1] = teal; det[185, x:x + 3] = teal_deep
    for x in range(258, 299):                         # trace 0: repair line (teal) ...
        det[265, x] = teal_deep
        if x % 3 == 0:
            det[265, x] = teal
    for y in range(245, 277):                         # ... meets storage line (amber)
        det[y, 284] = amber_deep
        if y % 3 == 0:
            det[y, 284] = amber
    det[264:267, 282:287] = amber_deep; det[265, 283:286] = teal_core
    rp_ring = ell(PLAZA_R[0], PLAZA_R[1], 14, 7) & ~ell(PLAZA_R[0], PLAZA_R[1], 12.6, 5.9)
    det[rp_ring] = teal_deep
    det[rp_ring & (XX % 3 == 0)] = teal
    for x in (466, 476, 486):                         # guide studs from the plaza ring to the terminal
        pass
    dome = poly_mask([(300, 62), (342, 62), (340, 73), (302, 73)])
    rgb = pal.rgb[ui]
    gold = dome & (rgb[..., 0] > rgb[..., 2] + 40) & (rgb[..., 1] > 90)
    det[gold & (lum[ui] > 170)] = P["patina-hi"]
    det[gold & (lum[ui] <= 170) & (lum[ui] > 120)] = P["patina-mid"]
    det[gold & (lum[ui] <= 120)] = P["patina-lo"]
    base_now = composite_idx(layers, order)
    dapple = pv["promenade"] & box(512, 184, 603, 210) & (low_freq("dapple", 5) > 0.42)
    dapple |= pv["promenade"] & box(52, 180, 210, 196) & (low_freq("dapple-nw", 6) > 0.6)
    dapple |= pv["promenade"] & box(470, 180, 540, 192) & (low_freq("dapple-ne", 6) > 0.62)
    det[dapple] = shade[base_now[dapple]]
    add("native-ground-detail", det, "native")

    # ---------------------------------------------------------------- native fixtures (always behind the hero)
    fx = new()
    draw_ledger(fx, P, near, 108, 152)
    draw_kiosk(fx, P, near, 530, 102)
    draw_pier_panel(fx, P, near, 357, 156)
    draw_sign(fx, P, near, 271, 247)
    move_into(fx, ui, term_m, 495 - 261, 265 - 302)   # reference civic terminal moved to the report plaza
    fx[box(494, 264, 518, 266) & (fx < 0)] = near("4a4238")
    add("native-fixtures", fx, "native")

    # ---------------------------------------------------------------- Y-sort occluders
    base_idx = composite_idx(layers, order)
    elm_layer = new()
    mc = move_into(elm_layer, ui, crown, *ELM_SHIFT)
    move_into(elm_layer, ui, trunk, *ELM_SHIFT)
    rim = edge(mc) & ~shift(trunk, *ELM_SHIFT)
    elm_layer[rim] = near("1d3424")
    add("tree-east-elm", elm_layer, "imported-reference-moved", ELM_PIVOT)
    for name, (m, pivot) in props.items():
        L = new(); L[m] = ui[m]
        add(name, L, "imported-reference", pivot)
    L = new(); move_into(L, ui, cart_m, 0, 0)
    add("cart-se", L, "imported-reference", 316)
    lamp_src = props["lamp-plaza-w"][0]
    L = new()
    for x, base in LAMPS_PROMENADE:                   # reference lamp sprite repeated along the promenade's south edge
        move_into(L, ui, lamp_src, x - 95, base - 273)
    add("lamps-promenade-s", L, "imported-reference-recomposed", max(b for _, b in LAMPS_PROMENADE))
    order_base = list(order)
    wm = walk_mask()
    guides_l = new()
    guides_l[edge(wm)] = P["stamp"]
    for k, (x, y) in HOTSPOTS.items():
        guides_l[max(0, y - 1):y + 2, max(0, x - 1):x + 2] = P["teal-core"]
    layers["guides"] = guides_l; origin["guides"] = "guide"
    base_names = [n for n in order_base if n not in ysort]
    ys_names = sorted(ysort, key=lambda n: (ysort[n], n))
    final_order = base_names + ys_names + ["guides"]
    return dict(layers=layers, order=final_order, base=base_names, ysort=ysort, origin=origin, walk=wm, pal=pal,
                canopy=["tree-east-elm"])


def composite_idx(layers, names):
    out = new()
    for n in names:
        if n == "guides":
            continue
        m = layers[n] >= 0
        out[m] = layers[n][m]
    return out


# ---------------------------------------------------------------- native fixture drawings
def draw_ledger(L, P, near, x0, y0):
    """Allocation ledger board (Liang Xu assist): iron frame, teal header light, pinned sheets with duplicate IDs."""
    frame, frame_hi = P["iron-dark"], P["iron-mid"]
    paper, shade, ink = P["paper"], P["paper-shade"], P["ink"]
    w, h = 24, 18
    for x in (x0 + 2, x0 + w - 4):
        L[y0 + h:y0 + 25, x:x + 2] = frame
        L[y0 + h:y0 + 25, x + 1] = frame_hi
    L[y0:y0 + h, x0:x0 + w] = frame
    L[y0, x0 + 1:x0 + w - 1] = frame_hi
    L[y0 + 1, x0 + 1:x0 + w - 1] = P["teal-deep"]
    L[y0 + 1, x0 + 3:x0 + w - 3:3] = P["teal-glow"]
    L[y0 + 3:y0 + h - 1, x0 + 1:x0 + w - 1] = near("4f5a52")
    for (sx, sy, sw, sh) in ((x0 + 2, y0 + 3, 6, 8), (x0 + 9, y0 + 4, 6, 9), (x0 + 16, y0 + 3, 6, 7)):
        L[sy:sy + sh, sx:sx + sw] = paper
        L[sy + sh - 1, sx:sx + sw] = shade
        L[sy:sy + sh, sx + sw - 1] = shade
        for r in range(sy + 2, sy + sh - 1, 2):
            L[r, sx + 1:sx + sw - 2] = ink
    L[y0 + 5:y0 + 7, x0 + 11:x0 + 13] = P["stamp"]
    L[y0 + h - 1, x0:x0 + w] = frame_hi
    L[y0 + 25, x0 + 1:x0 + w - 1] = near("3a3428")


def draw_kiosk(L, P, near, x0, y0):
    """Cast-iron and glass public-works stair kiosk (52 x 50), stair mouth facing south onto the apron."""
    iron, iron_mid, glass = P["iron-dark"], P["iron-mid"], P["glass-hi"]
    teal, teal_core, teal_deep = P["teal-glow"], P["teal-core"], P["teal-deep"]
    stone_hi, stone, stone_lo = near("e8d8b4"), near("b8a17c"), near("6e604c")
    glass_mid, glass_lo = near("7fa7a6"), near("4f6f72")
    w = 52
    for r in range(0, 12):                            # hipped glass canopy on iron ribs
        inset = max(0, 11 - r) // 2
        col = iron if r in (0, 11) else (glass if r < 4 else (glass_mid if r < 8 else glass_lo))
        L[y0 + r, x0 + inset:x0 + w - inset] = col
        for x in range(x0 + inset + 3, x0 + w - inset, 6):
            L[y0 + r, x] = iron_mid
    L[y0 + 12, x0:x0 + w] = iron
    L[y0 + 13, x0:x0 + w] = teal_deep
    L[y0 + 13, x0 + 4:x0 + w - 4:4] = teal
    L[y0 + 14:y0 + 20, x0 + 2:x0 + w - 2] = iron_mid
    L[y0 + 15:y0 + 19, x0 + 18:x0 + 34] = teal_deep
    L[y0 + 16:y0 + 18, x0 + 20:x0 + 32] = teal
    L[y0 + 16, x0 + 25:x0 + 27] = teal_core
    for side in (0, 1):                               # side frames with glass panes
        sx = x0 + 2 if side == 0 else x0 + w - 12
        L[y0 + 20:y0 + 46, sx:sx + 10] = glass_lo
        L[y0 + 21:y0 + 45, sx + 2:sx + 8] = glass_mid
        L[y0 + 22:y0 + 31, sx + 3] = glass
        L[y0 + 22:y0 + 26, sx + 4] = glass
        L[y0 + 20:y0 + 46, sx] = iron; L[y0 + 20:y0 + 46, sx + 9] = iron
        L[y0 + 33, sx:sx + 10] = iron
    sx0, sx1 = x0 + 12, x0 + w - 12
    steps = [near("1f2a2a"), near("2a3434"), near("33403f"), near("3e4c4a"), near("4d5c58"), near("5f6e68"),
             near("75837a"), near("8e9b8e"), stone]
    for r in range(y0 + 20, y0 + 46):                 # stair well descending north, teal-lit landing
        k = min((r - (y0 + 20)) // 3, 8)
        L[r, sx0:sx1] = steps[k]
        if (r - (y0 + 20)) % 3 == 0 and k > 0:
            L[r, sx0:sx1] = stone_lo if k > 4 else near("27302f")
    L[y0 + 20:y0 + 24, sx0:sx1] = teal_deep
    L[y0 + 21, sx0 + 2:sx1 - 2] = teal
    L[y0 + 22, sx0 + 6:sx1 - 6] = teal_core
    L[y0 + 20:y0 + 46, sx0] = iron_mid; L[y0 + 20:y0 + 46, sx1 - 1] = iron_mid
    L[y0 + 46:y0 + 48, x0:x0 + w] = stone_hi
    L[y0 + 48, x0:x0 + w] = stone_lo
    for x in (x0 + 1, x0 + w - 2):
        L[y0 - 3:y0, x] = iron
        L[y0 - 4, x] = P["amber-line"]


def draw_pier_panel(L, P, near, x0, y0):
    """Inspection panel on the east gate pier: stamped quota sheet + teal scanner slot."""
    L[y0:y0 + 13, x0:x0 + 10] = P["iron-dark"]
    L[y0 + 1:y0 + 9, x0 + 1:x0 + 9] = P["paper"]
    L[y0 + 8, x0 + 1:x0 + 9] = P["paper-shade"]
    for r in (y0 + 2, y0 + 4, y0 + 6):
        L[r, x0 + 2:x0 + 7] = P["ink"]
    L[y0 + 3:y0 + 6, x0 + 5:x0 + 8] = P["stamp"]
    L[y0 + 4, x0 + 6] = P["paper"]
    L[y0 + 10, x0 + 2:x0 + 8] = P["teal-deep"]
    L[y0 + 10, x0 + 4:x0 + 6] = P["teal-glow"]


def draw_sign(L, P, near, x, base):
    """Old street sign: short iron post with two stacked blades carrying different numbers (teal / amber)."""
    iron, iron_mid = P["iron-dark"], P["iron-mid"]
    L[base - 24:base, x:x + 2] = iron
    L[base - 24:base, x + 1] = iron_mid
    L[base - 25, x:x + 2] = P["amber-deep"]
    L[base - 23:base - 18, x - 6:x + 8] = P["teal-deep"]
    L[base - 22:base - 19, x - 5:x + 7] = P["teal-glow"]
    for dx in (-3, -1, 3, 5):
        L[base - 21, x + dx] = P["teal-core"]
    L[base - 16:base - 11, x - 3:x + 10] = P["amber-deep"]
    L[base - 15:base - 12, x - 2:x + 9] = P["amber-line"]
    for dx in (0, 2, 5, 7):
        L[base - 14, x + dx] = P["amber-deep"]
    L[base, x - 2:x + 4] = near("3a3428")


# ============================================================================ rgba + containers
def to_rgba(idx, pal):
    a = np.zeros((H, W, 4), np.uint8)
    m = idx >= 0
    a[m, :3] = pal.rgb[idx[m]].astype(np.uint8)
    a[m, 3] = 255
    return a


def png_bytes(arr):
    buf = io.BytesIO()
    Image.fromarray(arr, "RGBA").save(buf, "PNG", optimize=False, compress_level=9)
    return buf.getvalue()


def decode(png):
    return np.array(Image.open(io.BytesIO(png)).convert("RGBA"))


def composite_rgba(rgba, names):
    out = rgba[names[0]].copy()
    for n in names[1:]:
        m = rgba[n][..., 3] == 255
        out[m] = rgba[n][m]
    return out


DT = (2026, 10, 17, 16, 52, 52)


def zput(z, name, payload, method=zipfile.ZIP_DEFLATED):
    zi = zipfile.ZipInfo(name, DT)
    zi.compress_type = method
    z.writestr(zi, payload)


def make_ora(order, rgba, comp_png):
    stack = ['<?xml version="1.0" encoding="UTF-8"?>',
             f'<image version="0.0.5" w="{W}" h="{H}" xres="72" yres="72">', "<stack>"]
    for n in reversed(order):
        vis = "hidden" if n == "guides" else "visible"
        stack.append(f'<layer name="{n}" src="data/{n}.png" x="0" y="0" opacity="1.000" '
                     f'visibility="{vis}" composite-op="svg:src-over"/>')
    stack += ["</stack>", "</image>", ""]
    thumb = Image.open(io.BytesIO(comp_png)).convert("RGBA").resize((256, 144), Image.NEAREST)
    tb = io.BytesIO(); thumb.save(tb, "PNG")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        zput(z, "mimetype", b"image/openraster", zipfile.ZIP_STORED)
        zput(z, "stack.xml", "\n".join(stack).encode())
        for n in order:
            zput(z, f"data/{n}.png", png_bytes(rgba[n]))
        zput(z, "mergedimage.png", comp_png)
        zput(z, "Thumbnails/thumbnail.png", tb.getvalue())
    return buf.getvalue()


def make_pxo(order, rgba, comp_png):
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": n == "guides", "metadata": {}, "name": n,
                   "new_cels_linked": False, "opacity": 1.0, "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": n != "guides"} for n in order]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0}
                             for _ in order], "duration": 1.0, "metadata": {}}]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": json.dumps(f"{SLUG}_{AREA}_export_{VER}_{STAMP}-{RUN_ID}"),
                      "frame_current_tag": "0", "include_tag_in_filename": "false", "interpolation": "0",
                      "lines_count": "1", "new_dir_for_each_frame_tag": "false", "number_of_digits": "4",
                      "number_of_frames": "1", "orientation": "0", "repeat_count": "0", "resize": "100",
                      "save_quality": "0.75", "separator_character": "\"_\"",
                      "sheet_layers_as_separate_files": "false", "split_layers": "false"}
    data = {"author_company": "", "author_contact": "", "author_display_name": "", "author_real_name": "",
            "brushes": [], "color_mode": 5, "current_frame": 0, "current_layer": 0, "export_profile": export_profile,
            "fps": 6.0, "frames": frames_json, "guides": [], "layers": layer_json, "license": "", "metadata": {},
            "next_keyframe_id": 0, "palettes": [], "pixelorama_version": "v1.2.3-stable",
            "project_current_palette_name": "", "pxo_version": 7, "reference_images": [], "size_x": W, "size_y": H,
            "symmetry_points": [W - 1.0, H - 1.0], "tags": [], "tile_mode_x_basis_x": W, "tile_mode_x_basis_y": 0,
            "tile_mode_y_basis_x": 0, "tile_mode_y_basis_y": H, "tilesets": [], "user_data": "",
            "vanishing_points": []}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        zput(z, "data.json", json.dumps(data, separators=(",", ":")))
        zput(z, "mimetype", "application/x-pixelorama")
        zput(z, "preview.png", comp_png)
        zput(z, "image_data/frames/1/", b"")
        for li, n in enumerate(order, start=1):
            zput(z, f"image_data/frames/1/layer_{li}", np.ascontiguousarray(rgba[n]).tobytes())
            zput(z, f"image_data/frames/1/indices_layer_{li}", b"\x00")
    return buf.getvalue()


def make_gpl(pal):
    lines = ["GIMP Palette", f"Name: {SLUG}_{AREA}_palette_{VER}", "Columns: 8", "#"]
    for n, (r, g, b) in zip(pal.names, pal.cols):
        lines.append(f"{r:3d} {g:3d} {b:3d}\t{n}")
    return ("\n".join(lines) + "\n").encode()


def write_new(path, data):
    if os.path.exists(_fs(path)):
        if read_bytes(path) != data:
            raise SystemExit(f"refusing to overwrite a different existing file: {path}")
        return "unchanged"
    with open(_fs(path), "xb") as f:
        f.write(data)
    return "written"


# ============================================================================ artefacts
RT_SHORT = {"tree-east-elm": "elm", "fountain-centre": "fount", "lamp-plaza-w": "lamp-pw", "lamp-plaza-e": "lamp-pe",
            "bollard-plaza": "bollard-p", "lamp-axis-e": "lamp-ae", "bollard-junction-se": "bollard-j",
            "cart-se": "cart", "lamps-promenade-s": "lamps-pr"}   # short: .import paths must stay under MAX_PATH


def rt_name(layer):
    return "rt-y-" + RT_SHORT[layer]


def scene_data(sc, nm):
    return {
        "run": RUN, "status": "UNAPPROVED candidate; scene art not accepted (science scenes stay 3/12)",
        "source": "palette-reduced recomposition of an imported AI-generated nonruntime reference plus native layers",
        "canvas": [W, H], "ui_rows": {"header_end": UI_TOP, "footer_start": UI_BOTTOM},
        "base": nm["rt-base"], "walkmask": nm["walkmask"],
        "ysort": [{"name": n, "png": nm[rt_name(n)], "pivot": int(sc["ysort"][n]), "canopy": n in sc["canopy"]}
                  for n in sorted(sc["ysort"], key=lambda n: (sc["ysort"][n], n))],
        "hotspots": {k: list(v) for k, v in HOTSPOTS.items()},
        "legacy_positions": [{"from": list(LEGACY_SPAWN), "to": list(LEGACY_LANDING),
                              "why": "pre-navigation generic area SPAWN in old city saves; the old plate recovered it "
                                     "onto the west road at (82,203.5); v06 keeps that exact spot as standable west "
                                     "apron paving, so old saves land where they always did"}],
        "canopy_reveal": REVEAL,
    }


def tres_bytes(sj):
    text = json.dumps(sj, separators=(",", ":"), sort_keys=True)
    esc = text.replace("\\", "\\\\").replace('"', '\\"')
    return ('[gd_resource type="Resource" format=3]\n\n[resource]\nmetadata/scene_json = "' + esc + '"\n').encode()


def names(sc):
    nm = {"pxo": fname("scene-layers", "pxo"), "ora": fname("scene-layers", "ora"), "flat": fname("flat", "png"),
          "gpl": fname("palette", "gpl"), "walkmask": fname("walkmask", "png"), "scene": fname("scene", "json"),
          "tres": fname("scene", "tres"), "rt-base": fname("rt-base", "png"),
          "manifest": fname("manifest", "json"), "report": fname("check-report", "json")}
    for n in sc["ysort"]:
        nm[rt_name(n)] = fname(rt_name(n), "png")
    return nm


def artefacts(sc):
    pal = sc["pal"]
    order = sc["order"]
    rgba = {n: to_rgba(sc["layers"][n], pal) for n in order}
    art = [n for n in order if n != "guides"]
    flat = composite_rgba(rgba, art)
    flat_png = png_bytes(flat)
    nm = names(sc)
    files = {"pxo": make_pxo(order, rgba, flat_png), "ora": make_ora(order, rgba, flat_png), "flat": flat_png,
             "gpl": make_gpl(pal)}
    wm = np.zeros((H, W, 4), np.uint8); wm[sc["walk"]] = 255
    files["walkmask"] = png_bytes(wm)
    files["rt-base"] = png_bytes(composite_rgba(rgba, sc["base"]))
    for n in sc["ysort"]:
        files[rt_name(n)] = png_bytes(rgba[n])
    sj = scene_data(sc, nm)
    files["scene"] = (json.dumps(sj, indent=2) + "\n").encode()
    files["tres"] = tres_bytes(sj)
    return rgba, flat, files, nm


# ============================================================================ walking simulation (mirrors the runtime)
def walkable_at(walk, x, y):
    xi, yi = int(math.floor(x + 0.5)), int(math.floor(y + 0.5))
    return 0 <= xi < W and 0 <= yi < H and bool(walk[yi, xi])


def slide(walk, frm, to):
    pos = list(frm)
    dx, dy = to[0] - frm[0], to[1] - frm[1]
    steps = max(1, math.ceil(math.hypot(dx, dy) / 2.0))
    sx, sy = dx / steps, dy / steps
    for _ in range(steps):
        cx, cy = pos[0] + sx, pos[1] + sy
        if walkable_at(walk, cx, cy):
            pos = [cx, cy]
        elif walkable_at(walk, cx, pos[1]):
            pos[0] = cx
        elif walkable_at(walk, pos[0], cy):
            pos[1] = cy
    return pos


def smoke_walk(walk, start, target, speed=140.0 / 60.0):
    pos = list(start)
    for step in range(600):
        if math.hypot(target[0] - pos[0], target[1] - pos[1]) < 2.5:
            return True, pos, step
        d = (target[0] - pos[0], target[1] - pos[1])
        n = math.hypot(*d)
        # Input.get_vector: per-axis strengths clamp to the unit circle (direction already unit)
        v = (d[0] / n, d[1] / n)
        pos = slide(walk, pos, (pos[0] + v[0] * speed, pos[1] + v[1] * speed))
    return False, pos, 600


def flood(mask, start):
    seen = np.zeros_like(mask)
    x, y = start
    if not mask[y, x]:
        return seen
    seen[y, x] = True
    st = [(y, x)]
    while st:
        cy, cx = st.pop()
        for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
            if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                st.append((ny, nx))
    return seen


def heroine_48():
    """Approved v8 south static at the runtime's 0.5 display scale (as v05): 48 logical px tall."""
    a = np.array(Image.open(_fs(rp(HEROINE_REL))).convert("RGBA"))
    small = a[1::2, 1::2]
    ys, xs = np.nonzero(small[..., 3] > 0)
    spr = small[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    spr[..., 3] = np.where(spr[..., 3] > 127, 255, 0)
    return spr


# ============================================================================ checks
def static_checks(sc, rgba, flat):
    v, m = {}, {}
    order, walk, pal = sc["order"], sc["walk"], sc["pal"]
    v["layers_are_640x360_binary_alpha"] = all(rgba[n].shape == (H, W, 4) and set(np.unique(rgba[n][..., 3])) <=
                                               {0, 255} for n in order)
    v["base_is_opaque"] = bool((composite_rgba(rgba, sc["base"])[..., 3] == 255).all())
    used = {tuple(c) for c in flat[..., :3].reshape(-1, 3).tolist()}
    v["flat_uses_palette_colours_only"] = used <= {tuple(int(x) for x in c) for c in pal.cols}
    m["palette_colours"] = len(pal.cols); m["palette_colours_used"] = len(used)
    reach = flood(walk, HOTSPOTS["spawn"])
    m["walkable_texels"] = int(walk.sum()); m["reachable_texels"] = int(reach.sum())
    v["walk_mask_single_component_from_spawn"] = int(reach.sum()) == int(walk.sum())
    hs = {}
    for k, (x, y) in HOTSPOTS.items():
        hs[k] = bool(walk[y, x])
    m["hotspot_standable"] = hs
    v["every_hotspot_exactly_standable"] = all(hs.values())
    v["walk_inside_visible_band"] = bool((~walk[:UI_TOP + 48]).all() and (~walk[UI_BOTTOM - 11:]).all())
    v["no_walkable_feet_in_fountain_basin"] = not bool((walk & ell(FOUNT[0], FOUNT[1], 44, 19)).any())
    lx, ly = LEGACY_SPAWN
    v["legacy_spawn_not_standable"] = not walk[ly, lx]
    v["legacy_landing_standable"] = walkable_at(walk, *LEGACY_LANDING) and bool(reach[204, 82])
    v["legacy_landing_below_assist_blocked_at_204"] = (not walkable_at(walk, 120, 204)) and walkable_at(walk, 120, 203)
    # every walkable foot sits on native or reference paving (never on lawn or water)
    pave = np.zeros((H, W), bool)
    for p in paving_regions().values():
        pave |= p
    pave |= ell(170, 262, 90, 50)            # reference fountain plaza ring
    pave |= box(292, 177, 346, 318)          # reference central walk
    v["walkable_feet_on_paving"] = not bool((walk & ~pave).any())
    # integration-smoke style straight walks between hotspots (mirrors game/tests/m8_city_integration_smoke.gd)
    seq = [HOTSPOTS["spawn"], (285, 267), (378, 181), (120, 187), (282, 180), (558, 166), (470, 247), (120, 187)]
    walks_ok, pos = [], seq[0]
    for t in seq[1:]:
        ok, pos, steps = smoke_walk(walk, pos, t)
        walks_ok.append({"to": t, "ok": ok, "steps": steps, "end": [round(pos[0], 1), round(pos[1], 1)]})
        if not ok:
            break
    m["integration_smoke_walks"] = walks_ok
    v["integration_smoke_straight_walks_succeed"] = all(w["ok"] for w in walks_ok) and len(walks_ok) == len(seq) - 1
    end = slide(walk, (120.0, 187.0), (120.0, 187.0 + 140.0))
    m["assist_down_block_y"] = round(end[1], 2)
    v["assist_down_blocked_before_204"] = end[1] < 204.0
    # markers stay clear of every Y-sort occluder (runtime markers draw beneath Y-sorted sprites)
    ys = np.zeros((H, W), bool)
    for n in sc["ysort"]:
        ys |= rgba[n][..., 3] == 255
    clear = {}
    for k, (x, y) in HOTSPOTS.items():
        if k in ("spawn", "liang_xu"):
            continue
        clear[k] = int((ys & ell(x, y, 11.5, 11.5)).sum())
    m["marker_pixels_under_ysort"] = clear
    v["hotspot_markers_not_under_ysort_layers"] = all(c == 0 for c in clear.values())
    spr = heroine_48()
    m["heroine_height_px"] = int(spr.shape[0])
    v["heroine_48px"] = spr.shape[0] == 48
    # occlusion behind-cases: each Y-sort layer has walkable feet just north of its pivot that it covers
    behind = {}
    for n, pv in sc["ysort"].items():
        a = rgba[n][..., 3] == 255
        best = None
        for y in range(pv - 1, max(UI_TOP + 48, pv - 130), -1):
            xs = np.nonzero(walk[y] & a[max(0, y - 30):y + 1].any(0))[0]
            for x in xs[::2]:
                cover = int(a[max(0, y - 44):y + 3, max(0, x - 7):x + 8].sum())
                if cover > 6 and (best is None or cover > best[2]):
                    best = (int(x), int(y), cover)
            if best:
                break
        behind[n] = best
    m["behind_case_per_ysort_layer"] = behind
    need = ["tree-east-elm", "fountain-centre", "lamp-plaza-w", "lamp-plaza-e", "lamp-axis-e", "lamps-promenade-s"]
    v["occluders_have_a_walkable_behind_case"] = all(behind.get(n) is not None for n in need)
    # source honesty: pixel shares by origin in the flat
    owner = np.full((H, W), "", object)
    for n in [x for x in order if x != "guides"]:
        owner[rgba[n][..., 3] == 255] = sc["origin"][n]
    vis = owner[UI_TOP:UI_BOTTOM]
    shares = {k: round(float((vis == k).mean()), 4) for k in sorted(set(vis.ravel().tolist()))}
    m["visible_pixel_share_by_origin"] = shares
    m["ysort_pivots"] = {n: int(p) for n, p in sc["ysort"].items()}
    m["layer_origin"] = sc["origin"]
    return v, m


BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def reveal_hole(foot, strength=1.0):
    """Mirror of the runtime canopy shader: a dithered hole around the hero's body (logical pixels)."""
    rx, ry = REVEAL["radius"]
    d = np.hypot((XX + 0.5 - foot[0]) / rx, (YY + 0.5 - (foot[1] - REVEAL["lift"])) / ry)
    t = strength * (1.0 - np.clip((d - 0.75) / 0.25, 0, 1))
    t = t * t * (3 - 2 * t) if False else t
    return BAYER4[YY % 4, XX % 4] < t * REVEAL["max_hole"]


def still(rgba, sc, spr, foot, reveal=True):
    out = composite_rgba(rgba, sc["base"])
    placed = False
    for n in sorted(sc["ysort"], key=lambda n: (sc["ysort"][n], n)):
        if not placed and foot[1] < sc["ysort"][n]:
            paste(out, spr, *foot); placed = True
        m = rgba[n][..., 3] == 255
        if reveal and n in sc["canopy"] and foot[1] < sc["ysort"][n]:
            m = m & ~reveal_hole(foot)
        out[m] = rgba[n][m]
    if not placed:
        paste(out, spr, *foot)
    return out


def paste(dst, spr, x, ybase):
    h, w = spr.shape[:2]
    x0, y0 = x - w // 2, ybase + 4 - h
    for j in range(h):
        for i in range(w):
            if spr[j, i, 3] and 0 <= x0 + i < W and 0 <= y0 + j < H:
                dst[y0 + j, x0 + i] = spr[j, i]


def preview(outdir):
    os.makedirs(outdir, exist_ok=True)
    sc = scene()
    rgba, flat, files, nm = artefacts(sc)
    spr = heroine_48()
    ui = flat.copy(); ui[:UI_TOP, :, :3] = (13, 23, 35); ui[UI_BOTTOM:, :, :3] = (13, 23, 35)
    Image.fromarray(ui).save(os.path.join(outdir, "flat.png"))
    Image.fromarray(ui).resize((W * 2, H * 2), Image.NEAREST).save(os.path.join(outdir, "flat-2x.png"))
    for k, foot in (("spawn", (340, 253)), ("elm", (560, 196)), ("ledger", (120, 187)), ("fount", (196, 238)),
                    ("report", (470, 247)), ("kiosk", (558, 166)), ("elm-lawn", (566, 236))):
        s = still(rgba, sc, spr, foot)
        s[:UI_TOP, :, :3] = (13, 23, 35); s[UI_BOTTOM:, :, :3] = (13, 23, 35)
        Image.fromarray(s).save(os.path.join(outdir, f"still-{k}.png"))
    g = composite_rgba(rgba, sc["order"])
    Image.fromarray(g).resize((W * 2, H * 2), Image.NEAREST).save(os.path.join(outdir, "guides-2x.png"))
    rt = os.path.join(outdir, "rt")
    os.makedirs(rt, exist_ok=True)
    for k, b in files.items():
        with open(_fs(os.path.join(rt, nm[k])), "wb") as f:
            f.write(b)
    v, m = static_checks(sc, rgba, flat)
    print(json.dumps({"verdicts": v, "metrics": m}, indent=1, default=str))


def manifest(sc, files, nm, metrics):
    return {
        "run": RUN, "status": "UNAPPROVED candidate (scene environment not accepted; science scenes stay 3/12)",
        "author": "Claude Code (Opus 5.5) on the signed-in claude.ai Max subscription; no API key, no image model",
        "tool": "tools/" + os.path.basename(os.path.abspath(__file__)),
        "imported_generated_source": {
            "path": REF_REL, "sha256": REF_SHA, "kind": "AI-generated nonruntime art-direction reference (Codex)",
            "use": "box-recomposed into the 640x360 game frame in two bands, k-means palette-reduced "
                   f"({K_REF} colours) and cluster-cleaned; split into named layers; most visible pixels derive "
                   "from it. Not hand-painted.",
            "bands": [{"ref_rows": list(r), "screen_row0": s0, "rows": n} for r, (s0, n) in REF_BANDS]},
        "native_work": ["walk network paving + curbs + terrace wall face", "lawn/hedge in-painting", "east elm moved "
                        "+25 px with crisp rim", "survey kiosk", "ledger board", "gate-pier inspection panel",
                        "double-numbered sign + teal/amber pavement lines", "teal inlays", "cupola patina",
                        "axis-top lamps lifted 9 rows", "report terminal relocated", "walk mask, obstacles, Y-sort "
                        "pivots, canopy reveal parameters"],
        "baseline_preserved": V05_DIR_REL,
        "canvas": [W, H], "runtime_ui_rows": [UI_TOP, UI_BOTTOM],
        "layers_bottom_to_top": sc["order"], "layer_origin": sc["origin"],
        "visible_pixel_share_by_origin": metrics.get("visible_pixel_share_by_origin"),
        "hotspots_unchanged_from_runtime": {k: list(v) for k, v in HOTSPOTS.items()},
        "files": {k: {"name": nm[k], "sha256": sha_text(b) if k in ("gpl", "scene", "tres") else sha(b),
                      "hash": "sha256-text-lf-v1" if k in ("gpl", "scene", "tres") else "sha256-bytes"}
                  for k, b in sorted(files.items())},
    }


def build():
    sc = scene()
    rgba, flat, files, nm = artefacts(sc)
    v, m = static_checks(sc, rgba, flat)
    if not all(v.values()):
        print(json.dumps(v, indent=1))
        raise SystemExit("static gates fail; not writing")
    cand = rp(CAND_REL)
    os.makedirs(_fs(cand), exist_ok=True)
    longest = 0
    for k, b in files.items():
        p = os.path.join(cand, nm[k])
        longest = max(longest, len(os.path.abspath(p)) + len(".import"))
        print(write_new(p, b), nm[k])
    mb = (json.dumps(manifest(sc, files, nm, m), indent=2) + "\n").encode()
    print(write_new(os.path.join(cand, nm["manifest"]), mb), nm["manifest"])
    print("longest path incl. .import:", longest)


def run_pixelorama(exe, args, fake_appdata):
    env = dict(os.environ)
    env["APPDATA"] = fake_appdata
    t0 = time.time()
    p = subprocess.run([exe, "--headless", "--quit", "--"] + args, env=env, capture_output=True, timeout=180)
    return {"rc": p.returncode, "seconds": round(time.time() - t0, 2)}


def snapshot(root):
    out = {}
    if os.path.isdir(root):
        for dp, _, fs in os.walk(root):
            for f in fs:
                q = os.path.join(dp, f)
                try:
                    out[os.path.relpath(q, root)] = os.path.getmtime(q)
                except OSError:
                    pass
    return out


def pixelorama_gate(exe, files, rgba, flat, order):
    real = os.path.join(os.environ.get("APPDATA", ""), "pixelorama")
    before = snapshot(real)
    tmp = tempfile.mkdtemp(prefix="wb-chp6-")
    rep = {"pixelorama_sha256": sha(read_bytes(exe)), "steps": {}}
    try:
        for k in ("pxo", "ora"):
            src = os.path.join(tmp, f"src.{k}")
            with open(src, "wb") as f:
                f.write(files[k])
            for split in (False, True):
                label = f"{k}_{'split' if split else 'flat'}"
                d = os.path.join(tmp, label); os.makedirs(d)
                fake = os.path.join(tmp, "appdata_" + label); os.makedirs(fake)
                r = run_pixelorama(exe, ["--export"] + (["--split-layers"] if split else []) +
                                   ["-o", os.path.join(d, "f.png"), src], fake)
                pngs = sorted(f for f in os.listdir(d) if f.lower().endswith(".png"))
                r["pngs"] = len(pngs)
                r["source_unchanged"] = read_bytes(src) == files[k]
                if not split:
                    a = decode(read_bytes(os.path.join(d, pngs[0]))) if pngs else None
                    r["flat_exact"] = a is not None and a.shape == flat.shape and bool((a == flat).all())
                else:
                    hits = set()
                    for f in pngs:
                        a = decode(read_bytes(os.path.join(d, f)))
                        hits |= {n for n in order if a.tobytes() == rgba[n].tobytes()}
                    r["art_layers_exact"] = all(n in hits for n in order if n != "guides")
                    r["guides_exported"] = "guides" in hits
                rep["steps"][label] = r
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    after = snapshot(real)
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k) and
                     not k.endswith(".running"))
    rep["real_appdata_changed_except_running"] = changed
    st = rep["steps"]
    rep["verdicts"] = {
        "pixelorama_pxo_flat_exact": st["pxo_flat"].get("flat_exact", False),
        "pixelorama_ora_flat_exact": st["ora_flat"].get("flat_exact", False),
        "pixelorama_pxo_split_layers_exact": st["pxo_split"].get("art_layers_exact", False),
        "pixelorama_ora_split_layers_exact": st["ora_split"].get("art_layers_exact", False),
        "pixelorama_hidden_guides_not_exported": not st["pxo_split"].get("guides_exported", True) and
                                                 not st["ora_split"].get("guides_exported", True),
        "pixelorama_sources_unchanged": all(v["source_unchanged"] for v in st.values()),
        "pixelorama_real_appdata_untouched": not changed,
    }
    return rep


def check(exe, write_report, use_pixelorama):
    sc = scene()
    rgba, flat, files, nm = artefacts(sc)
    cand = rp(CAND_REL)
    rep = {"run": RUN, "gates": {}, "metrics": {}}
    on_disk = {}
    for k, b in files.items():
        disk = read_bytes(os.path.join(cand, nm[k]))
        on_disk[k] = (sha_text(disk) == sha_text(b)) if k in ("gpl", "scene", "tres") else (disk == b)
    rep["gates"]["candidate_files_equal_fresh_rebuild"] = all(on_disk.values())
    rep["gates"]["build_deterministic"] = artefacts(scene())[2] == files
    rep["gates"]["reference_hash_pinned"] = sha(read_bytes(rp(REF_REL))) == REF_SHA
    v05 = rp(V05_DIR_REL)
    v05_man_path = os.path.join(v05, f"{SLUG}_{AREA}_manifest_unapproved-v05_20261017-015916-23a7984f.json")
    # v05 is a local-only audit baseline; a clean clone without it records the gate as skipped, never as passed.
    rep["metrics"]["v05_baseline_present"] = os.path.exists(_fs(v05_man_path))
    if rep["metrics"]["v05_baseline_present"]:
        v05_man = json.loads(read_bytes(v05_man_path))
        ok05 = True
        for k, e in v05_man["files"].items():
            b = read_bytes(os.path.join(v05, e["name"]))
            ok05 &= (sha_text(b) if e["hash"] == "sha256-text-lf-v1" else sha(b)) == e["sha256"]
        rep["gates"]["v05_baseline_files_unchanged"] = bool(ok05)
    v, m = static_checks(sc, rgba, flat)
    rep["gates"].update(v); rep["metrics"].update(m)
    with zipfile.ZipFile(io.BytesIO(files["pxo"])) as z:
        dj = json.loads(z.read("data.json"))
    rep["gates"]["pxo_lists_named_layers_guides_hidden"] = [l["name"] for l in dj["layers"]] == sc["order"] and \
        [l["visible"] for l in dj["layers"]] == [n != "guides" for n in sc["order"]]
    rep["gates"]["tres_matches_scene_json"] = json.loads(
        files["tres"].decode().split('metadata/scene_json = "', 1)[1].rsplit('"', 1)[0]
        .replace('\\"', '"').replace("\\\\", "\\")) == json.loads(files["scene"])
    rep["metrics"]["layer_count"] = len(sc["order"])
    if use_pixelorama:
        rep["pixelorama"] = pixelorama_gate(exe, files, rgba, flat, sc["order"])
        rep["gates"].update(rep["pixelorama"]["verdicts"])
    rep["result"] = "PASS" if all(rep["gates"].values()) else "FAIL"
    rep["note"] = "Technical gates only; passing them is not art acceptance."
    print(json.dumps({"result": rep["result"], "gates": rep["gates"]}, indent=1))
    if write_report:
        out = rp(OUT_REL)
        os.makedirs(_fs(out), exist_ok=True)
        print(write_new(os.path.join(out, nm["report"]), (json.dumps(rep, indent=2, default=str) + "\n").encode()))
    return 0 if rep["result"] == "PASS" else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["preview", "build", "check"])
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--write-report", action="store_true")
    ap.add_argument("--no-pixelorama", action="store_true")
    ap.add_argument("--pixelorama", default=PIXELORAMA_DEFAULT)
    a = ap.parse_args()
    if a.mode == "preview":
        if not a.dir or os.path.abspath(a.dir).startswith(REPO):
            raise SystemExit("preview needs a directory outside the repo")
        preview(a.dir)
    elif a.mode == "build":
        build()
    else:
        sys.exit(check(a.pixelorama, a.write_report, not a.no_pixelorama))


if __name__ == "__main__":
    main()
