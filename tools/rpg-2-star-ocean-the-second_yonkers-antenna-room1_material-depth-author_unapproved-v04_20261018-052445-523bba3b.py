"""Yonkers outskirts survey annex room 1 (天线走廊 / Antenna Walkway): native pixel-art v04 material-depth pass.

v04 is a bounded recolour pass over the committed v03 scene. It imports the v03 author unchanged, rebuilds its
13 layers, and then only changes the colours of pixels that are already opaque. No alpha, layer, sprite box, clue,
marker, device, collision or walk-lane coordinate moves. Codex judged the v03 640x360 entry; v04 answers four defects:
  1. mechanically repeated flat wall blocks -> each masonry block gets an upper-left catch-light and a
     lower-right recess edge, and its value follows one upper-left light falloff (with damp at the wall foot);
  2. dead-even slab value -> each deck slab steps lighter/darker with the same light, with lit back edges
     and shaded front seams;
  3. sparse contact depth at the device plinths -> deeper occlusion at the three plinth feet, falling to the
     lower right (away from the light);
  4. little material separation at the dish mount -> plinth B is shaded as a drum (lit left, core shadow
     right, rounded foot), with a dark stone seat under the steel turntable and a lit steel rim.
Wear is placed in a few named clusters (pilaster feet, junction-box drips, door-side chips), not as noise.
Every pixel stays in the v03 palette. No generated, traced or resampled image is used.

Outputs go to outputs/yonkers-room1-v04_523bba3b/ only. Nothing under game/ is written and survey_annex.gd is
not touched, so the default and accepted rooms keep loading v03 (runtime stays off by default).

Usage: python -I <this file>
"""

from __future__ import annotations

import importlib.util
import json
from collections import deque
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261018-052445-523bba3b"
V03_AUTHOR = ROOT / "tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-scene-author_unapproved-v03_20261017-224447-15709be4.py"
OUT = ROOT / "outputs" / "yonkers-room1-v04_523bba3b"
EXPORTS = OUT / "nonruntime-exports"
PREFIX = "rpg-2-star-ocean-the-second_yonkers-antenna-room1"


def load_v03():
    spec = importlib.util.spec_from_file_location("yk1v03_author", V03_AUTHOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A = load_v03()
W, H = A.W, A.H
SCENE_LAYERS = A.SCENE_LAYERS
RGB, RGBA, HEX, NAME_OF = A.RGB, A.RGBA, A.HEX, A.NAME_OF
composite, sprite_box = A.composite, A.sprite_box
STONE = ("st_hi", "st", "st_mid", "st_dk")
LIT = {"st_hi": "st_hi", "st": "st_hi", "st_mid": "st", "st_dk": "st_mid", "st_deep": "st_dk"}
DIM = {"st_hi": "st", "st": "st_mid", "st_mid": "st_dk", "st_dk": "st_deep", "st_deep": "st_deep"}
DECK_BASE = ("dk_a", "dk_b", "dk_c")
DK_LIT = {"dk_c": "dk_b", "dk_b": "dk_a", "dk_a": "dk_worn"}
DK_DIM = {"dk_a": "dk_b", "dk_b": "dk_c", "dk_c": "dk_sh"}
WALL_Y = (108, 155)  # masonry face under the coping drip line, above the deck
# Plinths as drawn by the v03 antenna functions: (x0, x1, top); the foot row is BASE_Y - 1.
PLINTHS = [(A.ANTENNA_X[0] - 22, A.ANTENNA_X[0] + 26, 192), (A.ANTENNA_X[1] - 28, A.ANTENNA_X[1] + 28, 192),
           (A.ANTENNA_X[2] - 16, A.ANTENNA_X[2] + 16, 194)]
# Purposeful wear clusters: rising damp at pilaster feet and below the junction boxes; chips beside the doors.
DAMP = [(px, 155, 15, 9) for px in A.PILASTERS] + [(jx + 4, 155, 10, 6) for jx in A.JUNCTION_X]
CHIPS = [(52, 121), (58, 139), (582, 117), (575, 134), (230, 128), (452, 124)]


def names(a):
    """Palette name per pixel (None where transparent)."""
    out = np.full((H, W), None, object)
    ys, xs = np.nonzero(a[..., 3] == 255)
    for y, x in zip(ys, xs):
        out[y, x] = NAME_OF[tuple(int(v) for v in a[y, x, :3])]
    return out


def components(mask):
    """4-connected components of a boolean mask (no scipy); returns a label array, -1 outside."""
    lab = np.full(mask.shape, -1, np.int32)
    n = 0
    for y0, x0 in zip(*np.nonzero(mask)):
        if lab[y0, x0] >= 0:
            continue
        lab[y0, x0] = n
        q = deque([(y0, x0)])
        while q:
            y, x = q.popleft()
            for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and lab[yy, xx] < 0:
                    lab[yy, xx] = n
                    q.append((yy, xx))
        n += 1
    return lab, n


def light(cx, cy):
    """One upper-left light: 1 at the top-left of the wall/deck, about -1 at the lower right."""
    return 1.0 - 1.6 * (cx / W) - 0.6 * ((cy - 100) / 180)


def in_damp(x, y):
    for cx, cy, rx, ry in DAMP:
        # irregular top contour: the stain rises higher at its centre and frays with a fixed ripple
        top = cy - ry * (1 - ((x - cx) / rx) ** 2) - (1 if (x * 7) % 5 == 0 else 0)
        if abs(x - cx) <= rx and top <= y <= cy:
            return True
    return False


def wall_pass(layer):
    a = layer.a
    nm = names(a)
    rows = slice(WALL_Y[0], WALL_Y[1] + 1)
    stone = np.zeros((H, W), bool)
    stone[rows] = np.isin(nm[rows], STONE)
    lab, n = components(stone)
    new = nm.copy()
    for k in range(n):
        ys, xs = np.nonzero(lab == k)
        if len(ys) < 6 or len(ys) > 900:  # tiny specks and unbounded runs keep their v03 values
            continue
        v = light(xs.mean(), ys.mean()) + 0.35 * (((k * 37) % 7) / 6 - 0.5)  # small per-block variance
        step = LIT if v > 0.55 else (DIM if v < -0.45 else None)
        y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
        for y, x in zip(ys, xs):
            c = nm[y, x]
            c = step[c] if step else c
            if y == y0 or x == x0:
                c = LIT[c]  # upper-left catch-light on the block arris
            elif y == y1 or x == x1:
                c = DIM[c]  # recess edge on the lower right, into the mortar joint
            new[y, x] = c
    for y in range(*WALL_Y):
        for x in range(W):
            if new[y, x] in STONE and in_damp(x, y):
                new[y, x] = DIM[new[y, x]]
    for cx, cy in CHIPS:  # spall: shaded upper-left inner edge, lit lower-right lip
        for x, y, c in ((cx, cy, "st_deep"), (cx + 1, cy, "st_deep"), (cx, cy + 1, "st_dk"), (cx + 2, cy + 1, "st_hi"), (cx + 1, cy + 2, "st_hi")):
            if new[y, x] in STONE + ("st_deep",):
                new[y, x] = c
    return apply(layer, nm, new)


def deck_pass(layer):
    a = layer.a
    nm = names(a)
    slab = np.isin(nm, DECK_BASE + ("dk_hi", "dk_worn"))
    slab[:157] = False
    lab, n = components(slab)
    new = nm.copy()
    for k in range(n):
        ys, xs = np.nonzero(lab == k)
        if len(ys) < 20:
            continue
        v = light(xs.mean(), ys.mean()) + 0.5 * (((k * 53) % 5) / 4 - 0.5)
        step = DK_LIT if v > 0.25 else (DK_DIM if v < -0.55 else None)
        y0, y1 = ys.min(), ys.max()
        for y, x in zip(ys, xs):
            c = nm[y, x]
            if c in DECK_BASE:
                if step:
                    c = step.get(c, c)
                if y == y0 and x % 3:
                    c = "dk_worn" if c != "dk_sh" else "dk_c"  # lit back arris, broken every third pixel
                elif y == y1:
                    c = DK_DIM.get(c, c)  # front seam shade
            new[y, x] = c
    return apply(layer, nm, new)


def contact_pass(shadow_layer, under):
    """Deepen the plinth feet: two dark rows under each plinth, then a cast tail to the lower right."""
    sh = shadow_layer.a
    for x0, x1, _top in PLINTHS:
        for y, xa, xb, depth in ((A.BASE_Y, x0 - 1, x1 + 2, 3), (A.BASE_Y + 1, x0, x1 + 3, 2),
                                 (A.BASE_Y + 2, x0 + 2, x1 + 4, 2), (A.BASE_Y + 3, x0 + 6, x1 + 5, 1),
                                 (A.BASE_Y + 4, x0 + 12, x1 + 5, 1)):
            for x in range(xa, xb + 1):
                if y == A.BASE_Y + 4 and x % 2:
                    continue  # the tail breaks up as it leaves the plinth
                if under[y, x, 3] != 255:
                    continue
                c = NAME_OF[tuple(int(v) for v in under[y, x, :3])]
                for _ in range(depth):
                    c = A.shade_of(c)
                sh[y, x] = RGBA[c]


def dish_plinth_pass(layer):
    """Plinth B as a stone drum under a steel turntable."""
    a = layer.a
    nm = names(a)
    new = nm.copy()
    x0, x1, top = PLINTHS[1]
    span = x1 - x0
    for y in range(top, A.BASE_Y):
        for x in range(x0, x1 + 1):
            if nm[y, x] not in STONE + ("st_deep",):
                continue
            t = (x - x0) / span
            c = "st" if t < 0.06 else "st_hi" if t < 0.3 else "st" if t < 0.5 else "st_mid" if t < 0.7 else "st_dk" if t < 0.92 else "st_deep"
            if y >= A.BASE_Y - 3:
                c = DIM[c] if c in DIM else c  # foot in shade
            if y == A.BASE_Y - 1 and (t < 0.06 or t > 0.94):
                c = "st_deep"  # rounded foot corners
            if y == top and t < 0.55:
                c = "st_hi"
            new[y, x] = c
    cx = A.ANTENNA_X[1]
    # stone seat under the turntable: dark on the shaded right, mid on the lit left; lit steel rim upper-left
    for x in range(cx - 14, cx + 17):
        y = 196
        if new[y, x] in STONE + ("st_deep",):
            new[y, x] = "st_deep" if x > cx - 4 else "st_mid"
    for x in range(cx - 14, cx - 3):
        if nm[186, x] in ("steel", "slate"):
            new[186, x] = "edge"
    for x in range(cx + 4, cx + 15):
        if nm[192, x] == "steel":
            new[192, x] = "slate"
    for bx in (cx - 24, cx + 22):  # bolts stay brass
        new[195, bx], new[195, bx + 1], new[196, bx] = "br_hi", "br_dk", "br_dk"
    return apply(layer, nm, new)


def apply(layer, nm, new):
    changed = 0
    for y, x in zip(*np.nonzero(nm != new)):
        layer.a[y, x] = RGBA[new[y, x]]
        changed += 1
    return changed


def build_scene():
    layers = A.build_scene()
    stats = {}
    stats["back-parapet-masonry"] = wall_pass(layers[1])
    stats["wall-kit-and-ivy"] = wall_pass(layers[2])
    stats["deck-slabs"] = deck_pass(layers[3])
    under = composite(layers[:6])
    before = layers[6].a.copy()
    contact_pass(layers[6], under)
    stats["cast-shadows_contact_px"] = int((layers[6].a != before).any(axis=2).sum())
    stats["antenna-b-dish"] = dish_plinth_pass(layers[10])
    return layers, stats


def sha(data):
    return A.sha(data)


def rel(p):
    return A.rel(p)


def build():
    layers, stats = build_scene()
    v03 = A.build_scene()
    arrs = [l.a for l in layers]
    for i, (a, b) in enumerate(zip(arrs, (l.a for l in v03))):
        if i == 6:
            assert ((b[..., 3] == 255) <= (a[..., 3] == 255)).all(), "shadow layer only grows"
        else:
            assert (a[..., 3] == b[..., 3]).all(), "alpha unchanged: " + SCENE_LAYERS[i]
    plate = composite(layers[:9])
    assert (plate[..., 3] == 255).all()
    flat = composite(layers)
    used = {tuple(int(v) for v in c) for c in flat[..., :3].reshape(-1, 3)}
    assert used <= set(RGB.values()), "v03 palette only"
    OUT.mkdir(parents=True, exist_ok=True)
    EXPORTS.mkdir(parents=True, exist_ok=True)
    imgs = [A.to_img(a) for a in arrs]
    flat_img = A.to_img(flat)
    stem = f"{PREFIX}_material-depth-scene-layers_unapproved-v04_{STAMP}"
    files = {"ora": (OUT / f"{stem}.ora", A.ora_bytes(stem, SCENE_LAYERS, imgs, flat_img)),
             "pxo": (OUT / f"{stem}.pxo", A.pxo_bytes("yonkers-room1-v04", SCENE_LAYERS, imgs, flat_img)),
             "png": (OUT / f"{PREFIX}_material-depth-native-640x360-flat_unapproved-v04_{STAMP}.png", A.png_bytes(flat_img))}
    for p, data in files.values():
        p.write_bytes(data)
    plate_p = EXPORTS / f"{PREFIX}_corridor-plate-material-depth_unapproved-v04_{STAMP}.png"
    fg_p = EXPORTS / f"{PREFIX}_foreground-occluder_unapproved-v04_{STAMP}.png"
    plate_b, fg_b = A.png_bytes(A.to_img(plate)), A.png_bytes(A.to_img(arrs[12]))
    plate_p.write_bytes(plate_b)
    fg_p.write_bytes(fg_b)
    antennas = []
    for i, slug in enumerate(A.ANTENNA_SLUGS):
        x0, y0, x1, y1 = sprite_box(i)
        crop = A.png_bytes(A.to_img(np.ascontiguousarray(arrs[9 + i][y0:y1, x0:x1])))
        p = EXPORTS / f"{PREFIX}_{slug}_unapproved-v04_{STAMP}.png"
        p.write_bytes(crop)
        antennas.append({"layer": A.ANTENNA_LAYERS[i], "clue": f"scifi.outskirts:{i}", "crop_from_layer_xywh": [x0, y0, A.SPRITE_W, A.SPRITE_H],
                         "anchor": [A.ANTENNA_X[i], A.BASE_Y], "runtime_png": {"file": rel(p), "sha256": sha(crop), "hash_algorithm": "sha256-bytes"}})
    v03_flat = composite(v03)
    manifest = {
        "project": "Worlds Between (rpg-2-star-ocean-the-second)",
        "scene": "Yonkers outskirts survey annex room 1 (天线走廊 / Antenna Walkway), scifi.outskirts room 1",
        "version": "v04 bounded material-depth recolour over committed v03 (15709be4): wall-block light and recess edges, deck slab "
                   "values, plinth contact shadows, drum-shaded dish plinth with a stone seat under the steel turntable",
        "status": "UNAPPROVED. Not wired into the game: survey_annex.gd still loads v03, so v04 is off by default. Scenes stay 3/12.",
        "base": {"author": rel(V03_AUTHOR), "manifest": "outputs/yonkers-room1-v03_15709be4/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-scene-manifest_unapproved-v03_20261017-224447-15709be4.json"},
        "pixels_changed_vs_v03_flat": int((flat != v03_flat).any(axis=2).sum()),
        "pixels_changed_per_layer": stats,
        "alpha_unchanged_except_shadow_growth": True,
        "authorship": "Native pixel art: rule-based recolouring of the hand-placed v03 layers in this tool, by Claude (Claude Code). "
                      "No generated, traced, resampled or palette-reduced image; v03 palette only; binary alpha.",
        "canvas": [W, H], "palette_size": len(HEX), "palette": HEX, "layers_bottom_to_top": SCENE_LAYERS,
        "editable_sources": {k: {"file": rel(p), "sha256": sha(d), "hash_algorithm": "sha256-bytes"} for k, (p, d) in files.items()},
        "runtime_exports": {
            "note": "nonruntime exports in the v04 output folder only; nothing under game/ is written",
            "plate": {"from_layers": A.PLATE_LAYERS, "file": rel(plate_p), "sha256": sha(plate_b), "hash_algorithm": "sha256-bytes"},
            "antennas": antennas,
            "foreground": {"from_layers": ["foreground-occluder"], "file": rel(fg_p), "sha256": sha(fg_b), "hash_algorithm": "sha256-bytes"},
        },
        "source_tool": rel(Path(__file__)),
    }
    path = OUT / f"{PREFIX}_material-depth-scene-manifest_unapproved-v04_{STAMP}.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(path)
    print("changed", manifest["pixels_changed_vs_v03_flat"], stats)
    return manifest


if __name__ == "__main__":
    build()
