"""Pixel, source, wiring and Pixelorama checks for the Chicago Loop State/Lake material-depth pass v05 (UNAPPROVED, opt-in).

Usage: python -I <this file> --capture-stamp <stamp> [--pixelorama <exe>] [--report <json path>]
Started from the v04 source check (S1-S4, G1, G2, H1, C1-C5, A1, K1, P1/P2 kept and retargeted at v05; C3 is
still the original v03 gate against v02). It reads the manifest written by the v05 author tool, the v05
scene script, the v05 opt-in selector, the runtime Loop scene, the real Godot captures in
outputs/chicago-loop-state-lake-v05/godot-runtime (including the visible-hero counts JSON) and, for the
actual-scale comparison, the untouched v02, v03r1 and v04 captures. Changed or new for v05, all thresholds
fixed before any v05 Godot capture was measured (they were set after measuring v04 and v05 merged
previews while the art was iterated; see the QA note):
  G3  opt-in wiring (r1 2026-10-18, independent of what HEAD already holds): the Loop .tscn is exactly the
      one-script Loop scene naming the v04 selector (never the v05 one, no other hook or node); the v04
      selector is the pinned file (its flag and its default-off fall-through to the v02 script); the v05
      selector extends the unchanged v02 script, targets v05 and keeps the v04, v03r1 and v03 routes; v02
      baseline unchanged.
  R1  bounded pass over v04: v04 manifest hashes unchanged and the base-author pin equals the v04 author;
      v03 and v03r1 tracked files clean against HEAD; only backdrop-facade-north,
      backdrop-underdeck-storefronts and station-platform-canopy differ from the v04 layers (the canopy only
      in its windbreak rows 82..89); y-sort layers, walk mask, reveal mask, geometry, props, pivots and hero
      visibility byte-identical to v04; the scene script is the v04 script except header and art path.
  C6  not noisier than v04 over the whole view (isolated share +0.01, edge density +0.05 at most).
  F1  near-black kept for recesses: facade near-black share at most v04 + 0.005 and no more small
      near-black specks than v04.
  N1  no busier than the v03r1 strip Codex called busy: edge density of both backdrop bands below v03r1's,
      and isolated-pixel share at most v04 + 0.002 in both bands (no speckle added).
  K1  plaza accents as quiet as v04 (same pixels: equal medallion, fountain and pylon figures).
  K2  station still focal: the 80 px window with the most warm lit pixels in rows 62..94 is centred within
      40 px of the plate, and beats the best window at least 80 px away by 25% or more.
  W1  warmer facade strip than v04 (mean r - b in rows 62..94).
  L1  lit storefronts not flat fills: the largest one-colour 4-connected warm-light region in rows 135..165
      at most 60% of v04's.
  H2  atmospheric hierarchy: the facade strip's luma spread (p95 - p5) at most v04's and below the plaza's.
Reported only (no gate): 8x8 coarse/fine luma ratio of both bands and the sun/shade plane means.
Pixelorama runs use a fresh temp APPDATA and the real %APPDATA%/pixelorama dir is snapshotted before and after.
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PRE = "rpg-2-star-ocean-the-second_chicago-loop_"
AUTHOR = ROOT / f"tools/{PRE}state-lake-block-pixel-author_unapproved-v05_20261017-234337-84862412.py"
SCENE_SCRIPT = ROOT / f"game/scripts/{PRE}state-lake-block-scene_unapproved-v05_20261017-234337-84862412.gd"
V05_SCENE = ROOT / f"game/scenes/{PRE}state-lake-block-scene_unapproved-v05_20261017-234337-84862412.tscn"
SELECTOR = ROOT / f"game/scripts/{PRE}state-lake-scene-opt-in-selector_unapproved-v05_20261017-234337-84862412.gd"
V04_SELECTOR_RES = f"{PRE}state-lake-scene-opt-in-selector_unapproved-v04_20261017-230650-c0d4b7f0.gd"
V04_MANIFEST = ROOT / f"outputs/chicago-loop-state-lake-v04/{PRE}state-lake_layer-manifest_unapproved-v04_20261017-230650-c0d4b7f0.json"
V04_CAPTURES = ROOT / "outputs/chicago-loop-state-lake-v04/godot-runtime"
V04_STAMP = "20261017-232210-1f83552b"
V04_SCENE_SCRIPT = ROOT / f"game/scripts/{PRE}state-lake-block-scene_unapproved-v04_20261017-230650-c0d4b7f0.gd"
CHANGED_LAYERS = ("backdrop-facade-north", "backdrop-underdeck-storefronts", "station-platform-canopy")
WINDBREAK_ROWS = (82, 90)
RUNTIME_SCENE = ROOT / f"game/scenes/{PRE}district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn"
# G3 r1: the only allowed Loop .tscn (LF), and the v04 selector it may name, pinned as sha256-text-lf.
LOOP_TSCN_EXPECTED = ('[gd_scene load_steps=2 format=3]\n\n[ext_resource type="Script" path="res://scripts/%s" id="1_loop"]\n\n'
                      '[node name="ChicagoLoopDistrict" type="Node2D"]\nscript = ExtResource("1_loop")\n')
V04_SELECTOR = ROOT / f"game/scripts/{PRE}state-lake-scene-opt-in-selector_unapproved-v04_20261017-230650-c0d4b7f0.gd"
V04_SELECTOR_SHA256_TEXT_LF = "6c288141cf4c0e54049554c68995d01d1be092fd61938f159bf877ee01ac3f80"
V02_SCRIPT = f"res://scripts/{PRE}state-lake-block-scene_unapproved-v02_20261017-160959-55667f46.gd"
V02_MANIFEST = ROOT / f"outputs/chicago-loop-state-lake-v02/{PRE}state-lake_layer-manifest_unapproved-v02_20261017-160959-55667f46.json"
V02_CAPTURES = ROOT / "outputs/chicago-loop-state-lake-v02/godot-runtime"
V02_STAMP = "20261017-162405-1bdb3cd5"
V03_MANIFEST = ROOT / f"outputs/chicago-loop-state-lake-v03/{PRE}state-lake_layer-manifest_unapproved-v03_20261017-174431-c223d3f7.json"
V03R1_MANIFEST = ROOT / f"outputs/chicago-loop-state-lake-v03r1/{PRE}state-lake_layer-manifest_unapproved-v03r1_20261017-183235-a00fabf3.json"
V03R1_CAPTURES = ROOT / "outputs/chicago-loop-state-lake-v03r1/godot-runtime"
V03R1_STAMP = "20261017-184340-44bc6d7f"
V03R1_SCENE_SCRIPT = ROOT / f"game/scripts/{PRE}state-lake-block-scene_unapproved-v03r1_20261017-183235-a00fabf3.gd"
V03R1_SELECTOR_RES = f"{PRE}state-lake-scene-opt-in-selector_unapproved-v03r1_20261017-183235-a00fabf3.gd"
V03R1_SCENE_RES = f"{PRE}state-lake-block-scene_unapproved-v03r1_20261017-183235-a00fabf3.tscn"
CAPTURES = ROOT / "outputs/chicago-loop-state-lake-v05/godot-runtime"
# v03 and v03r1 code, scenes, art and the committed captures/notes (git pathspecs; checked clean against HEAD).
BASELINE_PATHSPECS = ["tools/*state-lake*v03_*", "tools/*state-lake*v03r1_*", "game/scripts/*state-lake*v03_*",
                      "game/scripts/*state-lake*v03r1_*", "game/scenes/*state-lake*v03_*", "game/scenes/*state-lake*v03r1_*",
                      "game/assets/environments/chicago-loop-state-lake-v03", "game/assets/environments/chicago-loop-state-lake-v03r1",
                      "outputs/chicago-loop-state-lake-v03", "outputs/chicago-loop-state-lake-v03r1", "docs/qa/*state-lake*v03*"]
FACADE_ROWS = (62, 95)          # upper building strip, rows 62..94
STORE_ROWS = (135, 166)         # storefronts under the deck, rows 135..165
NOISE_TOLERANCE = {"isolated_pixel_share": 0.01, "edge_density": 0.05}   # C6: allowed rise over v04
MEDALLION_BOX = (266, 237, 367, 272)
FOUNTAIN_BOX = (566, 256, 640, 298)
PYLON_BOX = (235, 194, 245, 233)
MUTED_PROPS = ("fountain", "wayfinding-pylon", "bike-share-dock")
PLATE_CENTRE_X = 326            # PLATE 296..356
FOCAL_WINDOW, FOCAL_TOLERANCE, FOCAL_MARGIN = 80, 40, 1.25
# Runtime label boxes (with outline) and the arrival hero box, excluded from render parity.
LABEL_BOXES = [(146, 183, 240, 201), (0, 279, 102, 297), (305, 106, 364, 124)]
HERO_BOX = (320 - 17, 286 - 46, 320 + 17, 286 + 6)
EXPECTED_CAPTURES = ["en-default-off-v02-entry", "zh-entry", "en-entry", "zh-traverse-under-l-lane", "en-traverse-under-l-lane",
                     "en-traverse-crosswalk", "zh-traverse-crosswalk", "zh-traverse-stair-foot", "zh-occlusion-column-raw",
                     "en-occlusion-column-reveal", "zh-occlusion-honey-locust", "zh-interact-kiosk", "en-interact-kiosk",
                     "zh-interact-stair", "en-interact-stair", "zh-interact-pylon", "en-interact-pylon",
                     "zh-approved-heroine-ref", "en-approved-heroine-ref"]
REF_TAGS = ("zh-approved-heroine-ref", "en-approved-heroine-ref")


def load_author():
    spec = spec_from_file_location("chicago_author_v05", AUTHOR)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha(data):
    return hashlib.sha256(data).hexdigest()


def text_sha(data):
    return sha(data.replace(b"\r\n", b"\n"))


def loop_wiring_checks(loop, v04_selector_bytes):
    """G3 r1: holds whether or not HEAD already contains the v04 line (pure; loop is LF text)."""
    v04 = v04_selector_bytes.replace(b"\r\n", b"\n").decode("utf-8")
    return {
        "loop_tscn_is_exact_v04_hook": loop == LOOP_TSCN_EXPECTED % V04_SELECTOR_RES,
        "v04_selector_pinned": text_sha(v04_selector_bytes) == V04_SELECTOR_SHA256_TEXT_LF,
        "v04_selector_default_off_shape": (v04.startswith(f'extends "{V02_SCRIPT}"') and 'const V04_FLAG := "--chicago-state-lake-v04"' in v04
                                           and "static var v04_override := -1" in v04 and "return OS.get_cmdline_user_args().has(V04_FLAG)" in v04
                                           and V03R1_SELECTOR_RES in v04 and '\tif target == "":\n\t\tsuper()\n\t\treturn\n' in v04),
    }


def rgba(path_or_bytes):
    src = io.BytesIO(path_or_bytes) if isinstance(path_or_bytes, bytes) else path_or_bytes
    return np.array(Image.open(src).convert("RGBA"))


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True)


def gd_constants():
    """Parse the runtime constants that must match the author tool."""
    text = SCENE_SCRIPT.read_text(encoding="utf-8")
    num = r"([-\d.]+)"
    rect = rf"Rect2\({num}, {num}, {num}, {num}\)"

    def rects(block):
        return [tuple(int(float(v)) for v in m) for m in re.findall(rect, block)]
    vec = lambda name: tuple(int(float(v)) for v in re.search(rf"const {name} := Vector2\({num}, {num}\)", text).groups())
    scalar = lambda name: float(re.search(rf"const {name} := {num}", text).group(1))
    props = [(m[0], tuple(int(float(v)) for v in m[1:5]), float(m[5])) for m in
             re.findall(rf'\["(ysort-[a-z-]+)", {rect}, {num}\]', re.search(r"const YSORT_PROPS := \[(.*?)\n\]", text, re.S).group(1))]
    sites = [(m[0], (int(float(m[1])), int(float(m[2])))) for m in re.findall(rf'\["([a-z]+)", Vector2\({num}, {num}\)\]', re.search(r"const SITES := \[(.*?)\]\n", text, re.S).group(1))]
    shader = {k: float(re.search(rf"uniform float {k} = {num};", text).group(1)) for k in ("lift", "max_hole")}
    radius = tuple(float(v) for v in re.search(rf"uniform vec2 radius = vec2\({num}, {num}\);", text).groups())
    return {"walk": rects(re.search(r"const WALK := (Rect2\([^)]*\))", text).group(1))[0],
            "blocks": rects(re.search(r"const BLOCKS := \[(.*?)\n\]", text, re.S).group(1)),
            "spawn": vec("SPAWN"), "kiosk": vec("KIOSK"), "kiosk_radius": scalar("KIOSK_RADIUS"), "sites": sites,
            "props": props, "layers": re.findall(r'"(ysort-[a-z-]+)"', re.search(r"const YSORT_LAYERS := \[(.*?)\]", text).group(1)),
            "art": re.search(r'const ART := "([^"]+)"', text).group(1), "walk_top": scalar("WALK_TOP"),
            "deck_bottom": scalar("DECK_BOTTOM"), "shader": shader, "radius": radius}


def luma(v):
    v = v.astype(int)
    return (v[..., 0] * 299 + v[..., 1] * 587 + v[..., 2] * 114) // 1000


def isolated_share(rgb, rows=(62, 318)):
    """Share of pixels whose four neighbours all differ from them (speckle, not clusters)."""
    v = rgb[rows[0] - 1:rows[1] + 1].astype(np.int32)
    c = (v[..., 0] << 16) | (v[..., 1] << 8) | v[..., 2]
    p = np.pad(c, ((0, 0), (1, 1)), mode="edge")
    iso = (p[1:-1, :-2] != c[1:-1]) & (p[1:-1, 2:] != c[1:-1]) & (c[:-2] != c[1:-1]) & (c[2:] != c[1:-1])
    return round(float(iso[:, 1:-1].mean()), 4)


def edge_density(rgb, rows=(62, 318)):
    a = rgb[rows[0]:rows[1]]
    dx = (a[:, 1:] != a[:, :-1]).any(axis=2)[:-1, :]
    dy = (a[1:] != a[:-1]).any(axis=2)[:, :-1]
    return round(float((dx | dy).mean()), 4)


def material_shares(rgb):
    """Plaza-level (rows 178..317) shares of foliage, teal civic light and lit stone, by colour key."""
    v = rgb[178:318].astype(int)
    r, g, b = v[..., 0], v[..., 1], v[..., 2]
    foliage = (g > r + 6) & (g > b + 6)
    teal = (b > r + 30) & (g > r + 30) & (g + b > 140)
    lum = (r * 299 + g * 587 + b * 114) // 1000
    stone_lit = (lum > 120) & (np.abs(r - b) < 70) & ~foliage & ~teal
    return {"foliage": round(float(foliage.mean()), 4), "teal": round(float(teal.mean()), 4), "lit_stone": round(float(stone_lit.mean()), 4)}


def facade_speckle(rgb):
    """Upper facade strip: share of near-black pixels (luma < 40) and the number of near-black 4-connected
    specks of at most 14 px (the v03r1 F1 metric, unchanged), plus the warm-minus-blue mean (r - b)."""
    v = rgb[FACADE_ROWS[0]:FACADE_ROWS[1]].astype(int)
    dark = luma(v) < 40
    h, w = dark.shape
    seen = np.zeros_like(dark)
    specks = 0
    for y0, x0 in zip(*np.nonzero(dark)):
        if seen[y0, x0]:
            continue
        stack, n = [(y0, x0)], 0
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            n += 1
            for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= yy < h and 0 <= xx < w and dark[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
        specks += n <= 14
    return {"near_black_share": round(float(dark.mean()), 4), "near_black_specks_le_14px": int(specks),
            "mean_r_minus_b": round(float((v[..., 0] - v[..., 2]).mean()), 2)}


def band_stats(rgb):
    return {name: {"edge_density": edge_density(rgb, rows), "isolated_pixel_share": isolated_share(rgb, rows)}
            for name, rows in (("facade", FACADE_ROWS), ("storefronts", STORE_ROWS))}


def accent_stats(rgb):
    """Fictional plaza accents: medallion luma spread and high-chroma pixels; bright teal at fountain and pylon."""
    def box(b):
        return rgb[b[1]:b[3], b[0]:b[2]].astype(int)
    med = box(MEDALLION_BOX)
    chroma = med.max(axis=2) - med.min(axis=2)

    def bright_teal(v):
        return int(((v[..., 1] > 150) & (v[..., 2] > 140) & (v[..., 0] < 150)).sum())
    return {"medallion_luma_std": round(float(luma(med).std()), 2), "medallion_high_chroma_px": int((chroma > 90).sum()),
            "fountain_bright_teal_px": bright_teal(box(FOUNTAIN_BOX)), "pylon_bright_teal_px": bright_teal(box(PYLON_BOX))}


def focal_stats(rgb):
    """Warm lit pixels per column in the upper strip, summed over an 80 px window: where is the brightest place?"""
    v = rgb[FACADE_ROWS[0]:FACADE_ROWS[1]].astype(int)
    lit = (luma(v) > 150) & (v[..., 0] > v[..., 2] + 40)
    cols = lit.sum(axis=0)
    win = np.convolve(cols, np.ones(FOCAL_WINDOW, int), mode="valid")
    best = int(np.argmax(win))
    far = max(int(w) for i, w in enumerate(win) if abs(i - best) >= FOCAL_WINDOW)
    return {"focal_window_centre_x": best + FOCAL_WINDOW // 2, "focal_window_lit_px": int(win.max()), "plate_centre_x": PLATE_CENTRE_X,
            "best_far_window_lit_px": far, "focal_margin": round(float(win.max()) / max(1, far), 3)}


def largest_warm_light(rgb, rows=STORE_ROWS):
    """Largest one-colour 4-connected region of warm interior light (lamp ramp: r - b > 90, luma > 95)."""
    v = rgb[rows[0]:rows[1]].astype(int)
    lit = (luma(v) > 95) & (v[..., 0] - v[..., 2] > 90)
    c = (v[..., 0] << 16) | (v[..., 1] << 8) | v[..., 2]
    h, w = lit.shape
    seen = np.zeros_like(lit)
    best = [0, None]
    for y0, x0 in zip(*np.nonzero(lit)):
        if seen[y0, x0]:
            continue
        stack, pts = [(y0, x0)], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            pts.append((y, x))
            for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= yy < h and 0 <= xx < w and lit[yy, xx] and not seen[yy, xx] and c[yy, xx] == c[y0, x0]:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
        if len(pts) > best[0]:
            ys, xs = zip(*pts)
            best = [len(pts), [int(min(xs)), int(min(ys)) + rows[0], int(max(xs)), int(max(ys)) + rows[0]]]
    return {"largest_px": best[0], "box_x0_y0_x1_y1": best[1]}


def coarse_fine(rgb, rows, x0=83):
    """Reported only: std of 8x8 block mean luma over the mean within-block std (x >= 83)."""
    a = luma(rgb[rows[0]:rows[1], x0:]).astype(float)
    h, w = (a.shape[0] // 8) * 8, (a.shape[1] // 8) * 8
    b = a[:h, :w].reshape(h // 8, 8, w // 8, 8).swapaxes(1, 2).reshape(h // 8, w // 8, 64)
    coarse, fine = float(b.mean(axis=2).std()), float(b.std(axis=2).mean())
    return {"ratio": round(coarse / max(1e-6, fine), 3), "coarse": round(coarse, 2), "fine": round(fine, 2)}


def depth_stats(rgb):
    """W1 / H2 / reported figures for the far plane."""
    f = rgb[FACADE_ROWS[0]:FACADE_ROWS[1]].astype(int)
    pl = luma(rgb[206:318, 83:])
    fl = luma(f)
    return {"facade_mean_r_minus_b": round(float((f[..., 0] - f[..., 2]).mean()), 2),
            "facade_luma_spread_p95_p5": int(np.percentile(fl, 95) - np.percentile(fl, 5)),
            "plaza_luma_spread_p95_p5": int(np.percentile(pl, 95) - np.percentile(pl, 5)),
            "facade_mean_luma": round(float(fl.mean()), 1),
            "storefront_largest_warm_light": largest_warm_light(rgb),
            "coarse_fine_facade": coarse_fine(rgb, FACADE_ROWS), "coarse_fine_storefronts": coarse_fine(rgb, STORE_ROWS),
            # open facade columns (no canopy in front): sunlit top rows vs shadowed bottom rows
            "terracotta_open_sun_rows_62_69_mean_luma": round(float(luma(rgb[62:70, 96:150]).mean()), 1),
            "terracotta_open_shade_rows_80_94_mean_luma": round(float(luma(rgb[80:95, 96:150]).mean()), 1),
            "limestone_open_sun_rows_62_79_mean_luma": round(float(luma(rgb[62:80, 560:640]).mean()), 1),
            "limestone_open_shade_rows_86_94_mean_luma": round(float(luma(rgb[86:95, 560:640]).mean()), 1)}


def flat_stats(rgb):
    vis = rgb[62:318].reshape(-1, 3)
    colours, counts = np.unique(vis, axis=0, return_counts=True)
    return {"visible_colours": int(len(colours)), "largest_single_colour_share": round(float(counts.max() / counts.sum()), 4),
            "edge_density": edge_density(rgb), "isolated_pixel_share": isolated_share(rgb), **material_shares(rgb)}


_PROPS = None


def author_props(author):
    global _PROPS
    if _PROPS is None:
        _PROPS = author.build_layers()[1]
    return _PROPS


def ysorted_composite(author, runtime):
    """What Godot draws with no hero: ground, then every prop region in pivot order (ties in prop order)."""
    out = runtime["ground-far"].copy()
    props = sorted(enumerate(author_props(author)), key=lambda t: (t[1]["pivot"], t[0]))
    for _, p in props:
        x, y, w, h = p["region"]
        src = runtime[p["layer"]][y:y + h, x:x + w]
        a = src[..., 3:4] == 255
        out[y:y + h, x:x + w] = np.where(a, src, out[y:y + h, x:x + w])
    return out


def model_visible(author, runtime, hero, at, reveal):
    """Visible hero pixels that differ from the frame without her, using the scene's y-sort and reveal rules."""
    hx, hy = at
    x0, y0 = int(hx) - 16, int(hy) - 44
    props = sorted(enumerate(author_props(author)), key=lambda t: (t[1]["pivot"], t[0]))
    under = runtime["ground-far"][..., :3].copy()
    over = np.zeros((360, 640), bool)
    rx, ry = author.REVEAL["radius"]
    yy, xx = np.mgrid[0:360, 0:640]
    d = np.hypot((xx + 0.5 - hx) / rx, (yy + 0.5 - (hy - author.REVEAL["lift"])) / ry)
    t = 1.0 - np.clip((d - 0.75) / 0.25, 0.0, 1.0)
    hole = author.BAYER[yy % 4, xx % 4] < t * author.REVEAL["max_hole"] if reveal else np.zeros((360, 640), bool)
    for _, p in props:
        x, y, w, h = p["region"]
        a = np.zeros((360, 640), bool)
        a[y:y + h, x:x + w] = runtime[p["layer"]][y:y + h, x:x + w, 3] == 255
        if p["pivot"] < hy:
            under[a] = runtime[p["layer"]][..., :3][a]
        else:
            over |= a & ~hole
    count = 0
    for j in range(hero.shape[0]):
        for i in range(hero.shape[1]):
            x, y = x0 + i, y0 + j
            if hero[j, i, 3] == 255 and 0 <= x < 640 and 0 <= y < 360 and not over[y, x] and (hero[j, i, :3] != under[y, x]).any():
                count += 1
    return count


def git_clean(paths):
    out = subprocess.run(["git", "status", "--porcelain", "--"] + [str(p) for p in paths], cwd=ROOT, capture_output=True, text=True)
    return out.returncode == 0 and out.stdout.strip() == ""


def source_checks(author, manifest):
    r = {}
    files = manifest["files"]

    def locked(v):
        data = (ROOT / v["file"]).read_bytes()
        return text_sha(data) if v["hash_algorithm"] == "sha256-text-lf-v1" else sha(data)
    r["hashes_match_manifest"] = all(locked(v) == v["sha256"] for v in files.values())
    layers, props = author.build_layers()
    rt = author.runtime_layers(layers)
    guide = author.walkmask()
    names = author.LAYERS
    rnames = ["ground-far"] + author.YSORT
    runtime = {n: rgba(ROOT / files[n]["file"]) for n in rnames}
    r["runtime_layers_equal_rebuild"] = all(runtime[n].tobytes() == np.array(rt[n]).tobytes() for n in rnames)
    r["sizes_640x360"] = all(a.shape == (360, 640, 4) for a in runtime.values())
    # Runtime ground is opaque; in the source the ground layer owns the street and walk rows and the three
    # backdrop layers own the rows above, so together they cover the whole canvas (nothing transparent).
    cover = sum((np.array(layers[n])[:, :, 3] == 255).astype(int) for n in
                ("ground-street-plaza", "backdrop-facade-north", "backdrop-deck-l-girder", "backdrop-underdeck-storefronts"))
    r["ground_opaque"] = bool((runtime["ground-far"][:, :, 3] == 255).all()) and bool((cover >= 1).all())
    r["source_and_ysort_binary_alpha"] = all(set(np.unique(np.array(layers[n])[:, :, 3]).tolist()) <= {0, 255} for n in names)
    flat = runtime["ground-far"].copy()
    for n in rnames[1:]:
        a = runtime[n][:, :, 3:4] == 255
        flat = np.where(a, runtime[n], flat)
    r["merged_preview_equals_runtime_layers"] = rgba(ROOT / files["merged-preview"]["file"]).tobytes() == flat.tobytes()
    used = {tuple(p) for n in names for a in [np.array(layers[n])] for p in a[a[:, :, 3] == 255][:, :3].tolist()}
    gpl = (ROOT / files["palette-gpl"]["file"]).read_text(encoding="utf-8").splitlines()
    pal = {tuple(int(v) for v in line.split("\t")[0].split()) for line in gpl if line[:1].isdigit() or line[:1] == " "}
    r["colours_used"] = len(used)
    r["all_colours_in_gpl_and_curated_palette"] = used == pal and used <= set(author.PAL.values())
    mask = rgba(ROOT / files["walkmask-guide"]["file"])
    r["guide_equals_rebuild"] = mask.tobytes() == np.array(guide).tobytes()
    _, low = author.visibility_report(layers, props)
    reveal = np.array(Image.open(ROOT / files["occlusion-reveal-mask"]["file"]))
    r["reveal_mask_equals_rebuild"] = bool(((reveal > 127) == low).all())
    gd = gd_constants()
    r["gd_walk_blocks_match_author"] = gd["walk"] == tuple(author.WALK) and gd["blocks"] == [tuple(b) for b in author.BLOCKS]
    r["gd_spawn_sites_match_author"] = (gd["spawn"] == tuple(author.SPAWN) and gd["kiosk"] == tuple(author.KIOSK)
                                        and gd["sites"] == [("kiosk", tuple(author.KIOSK)), ("stair", tuple(author.STAIR)), ("pylon", tuple(author.PYLON))]
                                        and gd["kiosk_radius"] == author.INTERACT_RADIUS)
    r["gd_props_match_manifest"] = gd["props"] == [(p["layer"], tuple(p["region"]), p["pivot"]) for p in manifest["ysort_props"]] and gd["layers"] == author.YSORT
    r["gd_art_path_matches_runtime_files"] = all((ROOT / "game" / (gd["art"] % n).replace("res://", "")).resolve() == (ROOT / files[n]["file"]).resolve()
                                                 for n in rnames + ["occlusion-reveal-mask"])
    r["gd_reveal_shader_matches_model"] = (gd["radius"] == tuple(author.REVEAL["radius"]) and gd["shader"]["lift"] == author.REVEAL["lift"]
                                           and gd["shader"]["max_hole"] == author.REVEAL["max_hole"])
    r["legacy_pins"] = author.walkable(400, 180) and not author.walkable(440, 195) and not author.walkable(410, 190) and author.walkable(410, 180)
    r["spawn_walkable"] = author.walkable(*gd["spawn"]) and all(author.walkable(*s[1]) for s in gd["sites"])
    r["head_clear_of_deck"] = gd["walk_top"] - 44 >= gd["deck_bottom"] and gd["deck_bottom"] == author.DECK_BOTTOM
    r["pivots_fractional_and_on_footprints"] = all(p[2] % 1 == 0.5 for p in gd["props"])
    try:
        author.check_pivots(props)
    except SystemExit:
        r["pivots_fractional_and_on_footprints"] = False
    # Opt-in wiring: the v05 selector (extends the unchanged v02 script; keeps the v04, v03r1 and v03 routes
    # through the v04 selector's rules) -> v05 scene -> v05 script. The shared Loop .tscn is not touched.
    sel = SELECTOR.read_text(encoding="utf-8")
    loop = RUNTIME_SCENE.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    r["runtime_scene_not_wired_to_v05"] = SELECTOR.name not in loop and "unapproved-v05" not in loop
    r.update(loop_wiring_checks(loop, V04_SELECTOR.read_bytes()))
    r["selector_extends_v02_targets_v05_keeps_older_routes"] = (sel.startswith(f'extends "{V02_SCRIPT}"') and V05_SCENE.name in sel
                                                               and '"--chicago-state-lake-v05"' in sel and "static var v05_override := -1" in sel
                                                               and V04_SELECTOR_RES in sel and "V04Selector.v04_enabled()" in sel
                                                               and "V04Selector.V03R1Selector.v03r1_enabled()" in sel
                                                               and "V04Selector.V03R1Selector.V03Selector.v03_enabled()" in sel)
    r["v05_scene_uses_v05_script"] = SCENE_SCRIPT.name in V05_SCENE.read_text(encoding="utf-8")
    # Bounded pass over v04: v04 untouched; only the three backdrop layers change.
    v04 = json.loads(V04_MANIFEST.read_text(encoding="utf-8"))
    r["v04_manifest_hashes_unchanged"] = all(locked(v) == v["sha256"] for v in v04["files"].values())
    r["base_author_pin_equals_v04_author"] = (manifest["pass_of"]["base_author"] == v04["source"]
                                              and manifest["pass_of"]["base_author_sha256_text_lf"] == text_sha((ROOT / v04["source"]).read_bytes()))
    diff = git("diff", "--name-only", "HEAD", "--", *BASELINE_PATHSPECS)
    r["v03_and_v03r1_tracked_files_clean_vs_head"] = diff.returncode == 0 and diff.stdout.strip() == b""
    v4ora = zipfile.ZipFile(ROOT / v04["files"]["openraster"]["file"])
    v4stack = {e.get("name"): e.get("src") for e in ET.fromstring(v4ora.read("stack.xml")).find("stack").findall("layer")}
    v4layers = {n: rgba(v4ora.read(v4stack[n])) for n in names}
    changed = {n: int((v4layers[n] != np.array(layers[n])).any(axis=2).sum()) for n in names}
    r["layer_px_changed_vs_v04"] = changed
    r["only_backdrop_layers_changed"] = sorted(n for n, c in changed.items() if c) == sorted(CHANGED_LAYERS)
    canopy_diff = (v4layers["station-platform-canopy"] != np.array(layers["station-platform-canopy"])).any(axis=2)
    outside = canopy_diff.copy()
    outside[WINDBREAK_ROWS[0]:WINDBREAK_ROWS[1], :] = False
    r["canopy_changes_only_in_windbreak_rows"] = not outside.any()
    r["canopy_alpha_unchanged"] = bool((v4layers["station-platform-canopy"][..., 3] == np.array(layers["station-platform-canopy"])[..., 3]).all())
    v4f = v04["files"]
    r["ysort_walkmask_reveal_byte_identical_to_v04"] = all(files[n]["sha256"] == v4f[n]["sha256"]
                                                           for n in author.YSORT + ["occlusion-reveal-mask", "walkmask-guide"])
    r["geometry_props_visibility_equal_v04"] = (manifest["geometry"] == v04["geometry"] and manifest["ysort_props"] == v04["ysort_props"]
                                                and manifest["hero_visibility"] == v04["hero_visibility"])
    r["ground_changed_from_v04"] = files["ground-far"]["sha256"] != v4f["ground-far"]["sha256"]
    a = V04_SCENE_SCRIPT.read_text(encoding="utf-8").splitlines()
    b = SCENE_SCRIPT.read_text(encoding="utf-8").splitlines()
    code_a = [l for l in a if not l.startswith("#") and not l.startswith("const ART := ")]
    code_b = [l for l in b if not l.startswith("#") and not l.startswith("const ART := ")]
    r["scene_script_equals_v04_except_header_and_art_path"] = code_a == code_b and any(
        l.startswith("const ART := ") and "chicago-loop-state-lake-v05/" in l and author.STAMP in l for l in b)
    # Fully authored.
    src = AUTHOR.read_text(encoding="utf-8")
    r["provenance"] = manifest["provenance"]
    r["no_underpainted_pixels"] = manifest["provenance"]["underpainted_visible_px"] == 0 and manifest["reference"]["read"] is False
    r["author_never_names_style_reference"] = "style-alignment-reference" not in src and "4c6e2b91" not in src
    v02 = json.loads(V02_MANIFEST.read_text(encoding="utf-8"))
    v02_paths = [ROOT / v["file"] for v in v02["files"].values()]
    v02_code = [ROOT / "game/scripts" / V02_SCRIPT.rsplit("/", 1)[1],
                ROOT / f"tools/{PRE}state-lake-block-pixel-author_unapproved-v02_20261017-160959-55667f46.py",
                ROOT / f"tools/{PRE}state-lake-block-godot-capture-check_v02_20261017-160959-4c432d04.gd",
                ROOT / f"tools/{PRE}state-lake-block-pixel-source-check_v02_20261017-160959-7af12ce1.py"]
    r["v02_baseline_hashes_unchanged"] = all(sha(p.read_bytes()) == v["sha256"] for p, v in zip(v02_paths, v02["files"].values()))
    r["v02_baseline_git_clean"] = git_clean(v02_paths + v02_code + [V02_CAPTURES, V02_MANIFEST])
    # OpenRaster: source layers top-first, guide hidden, every layer pixel-exact.
    ora = zipfile.ZipFile(ROOT / files["openraster"]["file"])
    r["ora_mimetype_first_stored"] = ora.infolist()[0].filename == "mimetype" and ora.infolist()[0].compress_type == zipfile.ZIP_STORED
    stack = ET.fromstring(ora.read("stack.xml"))
    entries = list(reversed(stack.find("stack").findall("layer")))
    r["ora_layer_names"] = [e.get("name") for e in entries]
    expect = {**{n: np.array(layers[n]) for n in names}, author.GUIDE: np.array(guide)}
    r["ora_layers_exact"] = r["ora_layer_names"] == names + [author.GUIDE] and all(
        rgba(ora.read(e.get("src"))).tobytes() == expect[e.get("name")].tobytes() for e in entries)
    r["ora_guide_hidden"] = entries[-1].get("visibility") == "hidden"
    pxo = zipfile.ZipFile(ROOT / files["pixelorama"]["file"])
    data = json.loads(pxo.read("data.json"))
    r["pxo_version"] = data["pxo_version"]
    r["pxo_layer_names"] = [l["name"] for l in data["layers"]]
    r["pxo_layers_exact"] = r["pxo_layer_names"] == names + [author.GUIDE] and all(
        pxo.read(f"image_data/frames/1/layer_{i}") == expect[n].tobytes() for i, n in enumerate(r["pxo_layer_names"], start=1))
    r["pxo_guide_hidden_locked"] = data["layers"][-1]["visible"] is False and data["layers"][-1]["locked"] is True
    tmp = tempfile.mkdtemp(prefix="wb-chi5-")
    try:
        rebuilt = author.build(out=Path(tmp) / "o", runtime=Path(tmp) / "r")
        r["rebuild_deterministic"] = all(rebuilt["files"][k]["sha256"] == v["sha256"] for k, v in files.items())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    r["hero_visibility"] = manifest["hero_visibility"]
    return r, runtime, flat


def capture_checks(author, runtime, stamp):
    r = {}
    name = lambda folder, tag, variant, st: folder / f"rpg-2-star-ocean-the-second_chicago-loop_state-lake-godot-{tag}-640x360_{variant}_{st}.png"
    entry = rgba(name(CAPTURES, "zh-entry", "v05", stamp))
    composite = ysorted_composite(author, runtime)
    keep = np.zeros((360, 640), bool)
    keep[62:318, :] = True
    for x0, y0, x1, y1 in LABEL_BOXES + [HERO_BOX]:
        keep[y0:y1, x0:x1] = False
    diff = (entry[:, :, :3] != composite[:, :, :3]).any(axis=2) & keep
    r["godot_entry_matches_ysorted_layers_outside_hero_and_labels"] = int(diff.sum())
    r["godot_entry_pixels_compared"] = int(keep.sum())
    counts = json.loads((CAPTURES / f"rpg-2-star-ocean-the-second_chicago-loop_state-lake-godot-visible-hero-counts_v05_{stamp}.json").read_text(encoding="utf-8"))
    hero = rgba(author.HERO_IDLE)
    model = {}
    for key, c in counts["spots"].items():
        at = (int(c["at"][0]), int(c["at"][1]))
        model[key] = {"godot_raw": c["raw"], "model_raw": model_visible(author, runtime, hero, at, False),
                      "godot_reveal": c["reveal"], "model_reveal": model_visible(author, runtime, hero, at, c["needs_reveal"])}
    r["visible_hero_godot_vs_model"] = model
    r["visible_hero_raw_exact"] = all(m["godot_raw"] == m["model_raw"] for m in model.values())
    r["visible_hero_reveal_within_3px"] = all(abs(m["godot_reveal"] - m["model_reveal"]) <= 3 for m in model.values())
    r["v02_zh-approved-heroine-ref"] = flat_stats(rgba(name(V02_CAPTURES, "zh-approved-heroine-ref", "v02", V02_STAMP))[:, :, :3])
    r["v05_zh-entry"] = flat_stats(entry[:, :, :3])
    for tag in REF_TAGS:
        for ver, folder, st in (("v03r1", V03R1_CAPTURES, V03R1_STAMP), ("v04", V04_CAPTURES, V04_STAMP), ("v05", CAPTURES, stamp)):
            img = rgba(name(folder, tag, ver, st))[:, :, :3]
            r[f"{ver}_{tag}"] = flat_stats(img)
            r[f"{ver}_{tag}_facade"] = facade_speckle(img)
            r[f"{ver}_{tag}_bands"] = band_stats(img)
            r[f"{ver}_{tag}_accents"] = accent_stats(img)
            r[f"{ver}_{tag}_focal"] = focal_stats(img)
            r[f"{ver}_{tag}_depth"] = depth_stats(img)
    present = sorted(p.name for p in CAPTURES.glob(f"*_{stamp}.png"))
    r["captures_present"] = present
    r["captures_complete"] = all(name(CAPTURES, t, "v05", stamp).name in present for t in EXPECTED_CAPTURES) and len(present) == len(EXPECTED_CAPTURES)
    return r


def run_pixelorama(exe, args, appdata):
    env = dict(os.environ)
    env["APPDATA"] = appdata
    return subprocess.run([exe, "--headless", "--quit", "--"] + args, capture_output=True, text=True, timeout=300, env=env)


def real_pixelorama_snapshot():
    root = os.path.join(os.environ.get("APPDATA", ""), "pixelorama")
    snap = {}
    if os.path.isdir(root):
        for d, _, fs in os.walk(root):
            for f in fs:
                rel = os.path.relpath(os.path.join(d, f), root).replace("\\", "/")
                if rel != ".running":
                    snap[rel] = sha(open(os.path.join(d, f), "rb").read())
    return snap


def pixelorama_checks(exe, author, manifest):
    rep = {}
    before = real_pixelorama_snapshot()
    names = author.LAYERS
    tmp = tempfile.mkdtemp(prefix="wb-chi5-pxo-")
    try:
        layers, _ = author.build_layers()
        for ext, key in (("pxo", "pixelorama"), ("ora", "openraster")):
            src = os.path.join(tmp, f"chi.{ext}")
            shutil.copyfile(ROOT / manifest["files"][key]["file"], src)
            appdata = os.path.join(tmp, f"app-{ext}")
            od = os.path.join(tmp, f"out-{ext}")
            os.makedirs(appdata)
            os.makedirs(od)
            p = run_pixelorama(exe, ["--export", "--split-layers", "-o", os.path.join(od, "f.png"), src], appdata)
            outs = sorted(os.listdir(od))
            exact = {}
            for n in names:
                hit = [o for o in outs if f"({n})" in o]
                exact[n] = len(hit) == 1 and rgba(Path(od) / hit[0]).tobytes() == np.array(layers[n]).tobytes()
            rep[ext] = {"exit": p.returncode, "pngs": len(outs), "visible_layers_exact": exact,
                        "hidden_guide_not_exported": not any(f"({author.GUIDE})" in o for o in outs),
                        "source_unchanged_by_cli": open(src, "rb").read() == (ROOT / manifest["files"][key]["file"]).read_bytes()}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    after = real_pixelorama_snapshot()
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    gui = [k for k in changed if k.startswith("backups/") and "/(untitled backup)-" in k]
    rep["real_appdata_gui_autosave_changes_excluded"] = gui
    rep["real_appdata_pixelorama_changed"] = [k for k in changed if k not in gui]
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture-stamp", required=True)
    ap.add_argument("--pixelorama", default=str(ROOT / "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"))
    ap.add_argument("--report", default="")
    a = ap.parse_args()
    author = load_author()
    manifest = json.loads((author.OUT / f"{author.PREFIX}_layer-manifest_{author.VARIANT}_{author.STAMP}.json").read_text(encoding="utf-8"))
    s, runtime, flat = source_checks(author, manifest)
    c = capture_checks(author, runtime, a.capture_stamp)
    p = pixelorama_checks(a.pixelorama, author, manifest) if os.path.isfile(a.pixelorama) else None
    v2, v5 = c["v02_zh-approved-heroine-ref"], c["v05_zh-approved-heroine-ref"]
    hv = s["hero_visibility"]
    pairs = lambda key, base="v04": [(c[f"{base}_{t}_{key}"], c[f"v05_{t}_{key}"]) for t in REF_TAGS]
    gates = {
        "S1_hashes_and_rebuild_exact": s["hashes_match_manifest"] and s["runtime_layers_equal_rebuild"] and s["rebuild_deterministic"] and s["merged_preview_equals_runtime_layers"],
        "S2_canvas_alpha_palette": s["sizes_640x360"] and s["ground_opaque"] and s["source_and_ysort_binary_alpha"] and s["all_colours_in_gpl_and_curated_palette"],
        "S3_openraster_exact": s["ora_mimetype_first_stored"] and s["ora_layers_exact"] and s["ora_guide_hidden"],
        "S4_pxo_exact": s["pxo_version"] == 7 and s["pxo_layers_exact"] and s["pxo_guide_hidden_locked"],
        "G1_walk_reveal_and_runtime_constants_match": (s["guide_equals_rebuild"] and s["reveal_mask_equals_rebuild"] and s["gd_walk_blocks_match_author"]
                                                       and s["gd_spawn_sites_match_author"] and s["gd_props_match_manifest"] and s["gd_art_path_matches_runtime_files"]
                                                       and s["gd_reveal_shader_matches_model"]),
        "G2_pins_spawn_head_clearance_pivots": s["legacy_pins"] and s["spawn_walkable"] and s["head_clear_of_deck"] and s["pivots_fractional_and_on_footprints"],
        "G3_opt_in_wiring_exact_v04_hook_default_off_v02_unchanged": (s["runtime_scene_not_wired_to_v05"] and s["loop_tscn_is_exact_v04_hook"]
                                                                 and s["v04_selector_pinned"] and s["v04_selector_default_off_shape"]
                                                                 and s["selector_extends_v02_targets_v05_keeps_older_routes"] and s["v05_scene_uses_v05_script"]
                                                                 and s["v02_baseline_hashes_unchanged"] and s["v02_baseline_git_clean"]),
        "R1_bounded_pass_over_v04": (s["v04_manifest_hashes_unchanged"] and s["base_author_pin_equals_v04_author"] and s["v03_and_v03r1_tracked_files_clean_vs_head"]
                                     and s["only_backdrop_layers_changed"] and s["canopy_changes_only_in_windbreak_rows"] and s["canopy_alpha_unchanged"]
                                     and s["ysort_walkmask_reveal_byte_identical_to_v04"] and s["geometry_props_visibility_equal_v04"]
                                     and s["ground_changed_from_v04"] and s["scene_script_equals_v04_except_header_and_art_path"]),
        "A1_every_pixel_authored": s["no_underpainted_pixels"] and s["author_never_names_style_reference"],
        "H1_hero_at_least_half_visible_everywhere_with_reveal": hv["with_reveal_min_visible_fraction"] >= 0.5,
        "C1_godot_native_render_exact": c["godot_entry_matches_ysorted_layers_outside_hero_and_labels"] == 0 and c["godot_entry_pixels_compared"] > 150000,
        "C2_godot_visible_hero_matches_model": c["visible_hero_raw_exact"] and c["visible_hero_reveal_within_3px"],
        "C3_plaza_denser_in_foliage_teal_and_lit_stone_than_v02": v5["foliage"] > v2["foliage"] and v5["teal"] > v2["teal"] and v5["lit_stone"] > v2["lit_stone"],
        "C4_fewer_isolated_pixels_than_v02": v5["isolated_pixel_share"] < v2["isolated_pixel_share"],
        "C5_captures_complete": c["captures_complete"],
        "C6_not_noisier_than_v04": all(c[f"v05_{t}"][k] <= c[f"v04_{t}"][k] + tol for t in REF_TAGS for k, tol in NOISE_TOLERANCE.items()),
        "F1_near_black_kept_for_recesses": all(b["near_black_share"] <= a["near_black_share"] + 0.005 and b["near_black_specks_le_14px"] <= a["near_black_specks_le_14px"]
                                               for a, b in pairs("facade")),
        "N1_bands_no_busier_than_v03r1_no_added_speckle": all(b[band]["edge_density"] < r1_[band]["edge_density"] and b[band]["isolated_pixel_share"] <= a[band]["isolated_pixel_share"] + 0.002
                                                              for (a, b), (r1_, _) in zip(pairs("bands"), pairs("bands", "v03r1")) for band in ("facade", "storefronts")),
        "K1_plaza_accents_as_quiet_as_v04": all(a == b for a, b in pairs("accents")),
        "K2_station_still_focal_with_margin": all(abs(b["focal_window_centre_x"] - PLATE_CENTRE_X) <= FOCAL_TOLERANCE and b["focal_margin"] >= FOCAL_MARGIN for _, b in pairs("focal")),
        "W1_facade_warmer_than_v04": all(b["facade_mean_r_minus_b"] > a["facade_mean_r_minus_b"] for a, b in pairs("depth")),
        "L1_lit_storefronts_not_flat_fills": all(b["storefront_largest_warm_light"]["largest_px"] <= 0.6 * a["storefront_largest_warm_light"]["largest_px"] for a, b in pairs("depth")),
        "H2_far_plane_hazier_than_v04_and_plaza": all(b["facade_luma_spread_p95_p5"] <= a["facade_luma_spread_p95_p5"] and b["facade_luma_spread_p95_p5"] < b["plaza_luma_spread_p95_p5"]
                                                      for a, b in pairs("depth")),
    }
    if p is not None:
        gates["P1_pixelorama_cli_split_layers_exact"] = all(p[e]["exit"] == 0 and all(p[e]["visible_layers_exact"].values()) and p[e]["hidden_guide_not_exported"] and p[e]["source_unchanged_by_cli"] for e in ("pxo", "ora"))
        gates["P2_real_pixelorama_appdata_untouched"] = not p["real_appdata_pixelorama_changed"]
    report = {"gates": gates, "passed": sum(gates.values()), "total": len(gates), "sources": s, "captures": c, "pixelorama_cli": p}
    text = json.dumps(report, indent=2, ensure_ascii=False, default=str)
    if a.report:
        Path(a.report).write_text(text + "\n", encoding="utf-8")
    for k, v in gates.items():
        print(("PASS " if v else "FAIL ") + k)
    print("v02 zh approved-heroine-ref:", json.dumps(v2))
    print("v04 zh approved-heroine-ref:", json.dumps(c["v04_zh-approved-heroine-ref"]))
    print("v05 zh approved-heroine-ref:", json.dumps(v5))
    for key in ("facade", "bands", "accents", "focal", "depth"):
        print(f"{key} v04 -> v05 (zh, en):", json.dumps(pairs(key)))
    print("bands v03r1 (zh, en):", json.dumps([c[f"v03r1_{t}_bands"] for t in REF_TAGS]))
    print(f"CHICAGO_LOOP_V05_PIXEL_SOURCE_CHECK {report['passed']}/{report['total']}")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
