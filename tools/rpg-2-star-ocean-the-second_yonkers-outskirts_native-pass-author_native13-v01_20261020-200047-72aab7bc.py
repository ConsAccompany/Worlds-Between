"""Yonkers outskirts exploration scene: native 640x360 service-route fixture pass (outskirts-native13, v01, UNAPPROVED).

Base: the committed 1672x941 outskirts m8 candidate, nearest-resampled to 640x360 and declared as a flattened
inherited plate (provenance only; not claimed as native work). Over it this tool authors eight hard-alpha native
layers in the accepted battle-env12 palette: paving transitions, a shallow cable raceway, the inset relay floor
panel (470,128), the flush survey threshold (558,277), a laid-out assist workpad (505,258), two distinct trace
plates (125,240 / 408,95), edge-mounted tech framing (only above y77 or right of x616) and low botanical ground
cover. Everything inside the legacy walk bounds is flush/walk-over; light comes from the upper left. UI strips
y0..62 and y328..359 stay base pixels.

Serialization (composite, ORA, Pixelorama gate) and the palette are reused from the battle-env12 author; the PXO
comes from the existing make_pxo writer with W/H set to 640/360. Output: outputs/outskirts-native13.

  python <tool> build | check [--pixelorama]
"""
import argparse, hashlib, importlib.util, json, os, sys
import numpy as np
from PIL import Image, ImageDraw

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
AUTHOR_REL = "tools/rpg-2-star-ocean-the-second_yonkers-outskirts_native-pass-author_native13-v01_20261020-200047-72aab7bc.py"
BATTLE_REL = "tools/rpg-2-star-ocean-the-second_battle-arena_native-pass-author_v01_20261020-230516-c4a9e217.py"
BASE_REL = ("game/assets/environments/rpg-2-star-ocean-the-second_scifi-outskirts_environment-background_"
            "m8-candidate_20261014-142557-58f0c3a1.png")
OUT_REL = "outputs/outskirts-native13"
STAMP = "20261020-200047"
SLUG, SUBJECT, VARIANT = "rpg-2-star-ocean-the-second", "yonkers-outskirts", "native13-v01"
W, H = 640, 360
ZIP_DT = (2026, 10, 20, 20, 0, 46)
UI_TOP, UI_BOTTOM = 62, 328          # rows 0..62 and 328..359 stay inherited
WALK = (24, 77, 616, 306)
PROTECTED = {"walkBounds": [24, 77, 616, 306], "spawn": [82, 260], "relay": [470, 128], "survey": [558, 277],
             "assist": [505, 258], "traces": [[125, 240], [408, 95]], "npc": [190, 150], "encounter": [355, 238]}
LAYERS = ["paving-transitions", "cable-raceway", "relay-floor-panel", "survey-threshold", "assist-workpad",
          "trace-plates", "edge-tech-framing", "botanical-integration"]
UPRIGHT = {"edge-tech-framing"}      # must sit entirely outside the walk bounds


def _load(rel, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REPO, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BA = _load(BATTLE_REL, "wb_battle_env12_author")
BA.W, BA.H, BA.ZIP_DT = W, H, ZIP_DT  # composite/make_ora/load_make_pxo read these module globals
col = BA.col


def uid(key):
    return hashlib.sha256(f"{STAMP}:{key}".encode("utf-8")).hexdigest()[:8]


def fname(purpose, ext):
    return f"{SLUG}_{SUBJECT}_{purpose}_{VARIANT}_{STAMP}-{uid(purpose + '.' + ext)}.{ext}"


def canvas():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def R(d, x0, y0, x1, y1, c):
    d.rectangle((x0, y0, x1, y1), fill=col(c))


def px(d, x, y, c):
    d.point((x, y), fill=col(c))


def inset(d, x0, y0, x1, y1, rim, face, shade="ink", lift="stone_hl"):
    """Flush recessed plate: rim, rim shadow on the inner top/left, lit inner bottom/right lip."""
    R(d, x0, y0, x1, y1, rim)
    R(d, x0 + 1, y0 + 1, x1 - 1, y1 - 1, face)
    R(d, x0 + 1, y0 + 1, x1 - 1, y0 + 1, shade)
    R(d, x0 + 1, y0 + 1, x0 + 1, y1 - 1, shade)
    R(d, x0 + 2, y1 - 1, x1 - 1, y1 - 1, lift)
    R(d, x1 - 1, y0 + 2, x1 - 1, y1 - 1, lift)


# ---------------------------------------------------------------------------------------------- inherited base

def base_layer():
    src = Image.open(os.path.join(REPO, BASE_REL)).convert("RGB")
    if src.size != (1672, 941):
        raise SystemExit(f"base plate size {src.size} != (1672, 941)")
    return src.resize((W, H), Image.NEAREST).convert("RGBA")


# ------------------------------------------------------------------------------------------------ native layers

def setts(d, x0, y0, x1, y1, bw=6, bh=4):
    """Dressed rectangular setts, running bond, mortar in stone, lit top row per sett."""
    R(d, x0, y0, x1, y1, "stone")
    for r, y in enumerate(range(y0, y1 + 1, bh)):
        off = (bw // 2) * (r % 2)
        for x in range(x0 - off, x1 + 1, bw):
            a, b = max(x, x0), min(x + bw - 2, x1)
            if a > b:
                continue
            yb = min(y + bh - 2, y1)
            R(d, a, y, b, yb, "stone_m" if (r + x // bw) % 3 else "stone_l")
            R(d, a, y, b, y, "stone_hl" if (r + x // bw) % 3 == 0 else "stone_l")


def paving_transitions():
    img, d = canvas()
    setts(d, 450, 112, 490, 144)          # relay apron
    setts(d, 534, 266, 582, 290)          # survey approach
    setts(d, 486, 246, 526, 272)          # workpad hardstanding
    for x0, y0, x1, y1 in ((450, 112, 490, 144), (534, 266, 582, 290), (486, 246, 526, 272)):
        R(d, x0 - 1, y0 - 1, x1 + 1, y0 - 1, "stone_d")     # kerb lip: upper-left edge catches no light
        R(d, x0 - 1, y0 - 1, x0 - 1, y1 + 1, "stone_d")
        R(d, x0, y1 + 1, x1 + 1, y1 + 1, "stone_hl")
        R(d, x1 + 1, y0, x1 + 1, y1 + 1, "stone_l")
    return img


RACEWAY = [  # (x0, y0, x1, y1) centre-line segments, axis aligned; routed east of the central approach
    (470, 77, 470, 112), (430, 134, 450, 134), (430, 134, 430, 249), (430, 249, 486, 249),
    (526, 268, 534, 268),
]


def cable_raceway():
    # Codex integration correction: a recessed three-pixel service groove, not a raised seven-pixel wall.
    img, d = canvas()
    for x0, y0, x1, y1 in RACEWAY:
        if x0 == x1:
            R(d, x0 - 1, y0, x0 + 1, y1, "stone_d")
            R(d, x0, y0, x0, y1, "slate")
            R(d, x0 + 1, y0, x0 + 1, y1, "stone")
            for y in range(y0 + 9, y1, 18):
                R(d, x0 - 1, y, x0 + 1, y, "brass_d")
                px(d, x0, y, "brass")
        else:
            R(d, x0, y0 - 1, x1, y0 + 1, "stone_d")
            R(d, x0, y0, x1, y0, "slate")
            R(d, x0, y0 + 1, x1, y0 + 1, "stone")
            for x in range(x0 + 9, x1, 18):
                R(d, x, y0 - 1, x, y0 + 1, "brass_d")
                px(d, x, y0, "brass")
    for cx, cy in ((430, 134), (430, 249)):
        R(d, cx - 1, cy - 1, cx + 1, cy + 1, "slate")
        px(d, cx, cy, "brass")
    return img



def relay_floor_panel():
    img, d = canvas()
    cx, cy = 470, 128
    inset(d, cx - 13, cy - 10, cx + 13, cy + 10, "brass_d", "slate", "ink", "brass_l")
    R(d, cx - 13, cy - 10, cx + 13, cy - 10, "brass_l")            # lit outer frame top/left
    R(d, cx - 13, cy - 10, cx - 13, cy + 10, "brass")
    R(d, cx, cy - 8, cx, cy + 8, "deep")                           # split cover seam
    for x in (cx - 9, cx + 4):                                      # cover plate faces
        R(d, x, cy - 7, x + 4, cy - 7, "steel_l")
    R(d, cx - 4, cy - 4, cx + 4, cy + 4, "brass_d")                # octagonal brass collar
    for x, y in ((cx - 4, cy - 4), (cx + 4, cy - 4), (cx - 4, cy + 4), (cx + 4, cy + 4)):
        px(d, x, y, "slate")
    R(d, cx - 3, cy - 3, cx + 3, cy + 3, "brass")
    R(d, cx - 3, cy - 3, cx + 2, cy - 3, "brass_hl")
    R(d, cx - 3, cy - 2, cx - 3, cy + 2, "brass_l")
    R(d, cx - 2, cy - 2, cx + 2, cy + 2, "teal_d")
    R(d, cx - 1, cy - 1, cx + 1, cy + 1, "teal")
    px(d, cx - 1, cy - 1, "glow"); px(d, cx, cy, "glow_hl")
    for y in (cy - 6, cy + 6):                                     # restrained teal status strips
        R(d, cx - 10, y, cx - 6, y, "teal_d"); R(d, cx + 6, y, cx + 10, y, "teal_d")
        px(d, cx - 8, y, "glow"); px(d, cx + 8, y, "teal")
    for x, y in ((cx - 11, cy - 8), (cx + 11, cy - 8), (cx - 11, cy + 8), (cx + 11, cy + 8)):
        px(d, x, y, "brass_hl")
    R(d, cx - 3, cy - 18, cx + 3, cy - 11, "brass_d")              # raceway connector clamp
    R(d, cx - 2, cy - 17, cx + 2, cy - 12, "brass")
    R(d, cx - 2, cy - 17, cx + 2, cy - 17, "brass_hl")
    R(d, cx - 2, cy - 14, cx + 2, cy - 14, "brass_d")
    R(d, cx - 21, cy + 4, cx - 14, cy + 8, "brass_d")              # west tap to the raceway elbow
    R(d, cx - 20, cy + 5, cx - 14, cy + 7, "brass")
    R(d, cx - 20, cy + 5, cx - 14, cy + 5, "brass_l")
    return img


def survey_threshold():
    img, d = canvas()
    cx, cy = 558, 277
    R(d, cx - 19, cy - 7, cx + 19, cy + 7, "stone_d")              # sill bed
    R(d, cx - 18, cy - 6, cx + 18, cy + 5, "stone_l")
    R(d, cx - 18, cy - 6, cx + 18, cy - 6, "stone_hl")
    R(d, cx - 18, cy + 4, cx + 18, cy + 5, "stone_m")              # flush nosing, front bevel
    R(d, cx - 18, cy + 6, cx + 18, cy + 6, "stone")
    for x in range(cx - 12, cx + 13, 8):                           # dressed joints
        R(d, x, cy - 5, x, cy + 5, "stone")
    R(d, cx - 15, cy - 2, cx + 15, cy - 2, "brass_d")              # grooved brass strip
    R(d, cx - 15, cy - 1, cx + 15, cy, "brass")
    R(d, cx - 15, cy - 1, cx + 15, cy - 1, "brass_hl")
    for x in (cx - 12, cx, cx + 12):                               # teal guide lights in the nosing
        R(d, x - 1, cy + 3, x + 1, cy + 3, "teal_d")
        px(d, x, cy + 3, "glow")
    for x in (cx - 21, cx + 20):                                   # flush steel jamb plates
        R(d, x, cy - 7, x + 1, cy + 7, "slate")
        R(d, x, cy - 7, x, cy + 7, "steel_l")
    return img


def assist_workpad():
    img, d = canvas()
    x0, y0, x1, y1 = 491, 251, 521, 266
    R(d, x0 + 1, y0 + 1, x1 + 1, y1 + 1, "stone_d")                # 1 px flat contact shadow
    R(d, x0, y0, x1, y1, "brass_d")                                 # canvas mat, bound edge
    R(d, x0 + 1, y0 + 1, x1 - 1, y1 - 1, "stone_m")
    R(d, x0 + 1, y0 + 1, x1 - 1, y0 + 1, "stone_l")
    for x in range(x0 + 3, x1 - 1, 5):                              # weave fold lines
        R(d, x, y0 + 2, x, y1 - 1, "stone")
    R(d, 494, 254, 501, 262, "ink")                                 # slate tablet
    R(d, 495, 255, 500, 260, "teal_d")
    R(d, 495, 255, 499, 255, "teal")
    R(d, 496, 257, 498, 257, "glow")
    px(d, 499, 259, "glow_hl")
    R(d, 495, 262, 500, 262, "deep")
    R(d, 504, 254, 504, 263, "brass_l")                             # calipers, laid flat
    R(d, 504, 254, 509, 254, "brass_hl")
    R(d, 505, 263, 505, 263, "brass_d")
    R(d, 507, 255, 509, 255, "brass")
    R(d, 512, 255, 518, 258, "cable_l")                             # coiled lead
    R(d, 513, 256, 517, 257, "cable")
    R(d, 514, 256, 516, 256, "stone_m")
    R(d, 511, 261, 519, 263, "brass_d")                             # tool roll
    for x in range(512, 519, 2):
        px(d, x, 262, "steel_l")
    R(d, 511, 261, 519, 261, "brass")
    return img


def trace_plates():
    img, d = canvas()
    cx, cy = 125, 240                                               # brass survey datum plate
    R(d, cx - 8, cy - 7, cx + 9, cy + 8, "stone_d")
    R(d, cx - 7, cy - 6, cx + 8, cy + 7, "brass_d")
    R(d, cx - 6, cy - 5, cx + 7, cy + 6, "brass")
    R(d, cx - 6, cy - 5, cx + 7, cy - 5, "brass_hl")
    R(d, cx - 6, cy - 4, cx - 6, cy + 6, "brass_l")
    R(d, cx, cy - 3, cx, cy - 1, "brass_d"); R(d, cx, cy + 1, cx, cy + 4, "brass_d")
    R(d, cx - 4, cy, cx - 2, cy, "brass_d"); R(d, cx + 2, cy, cx + 5, cy, "brass_d")
    px(d, cx, cy, "glow")
    for x, y in ((cx - 5, cy - 4), (cx + 6, cy - 4), (cx - 5, cy + 5), (cx + 6, cy + 5)):
        px(d, x, y, "brass_hl")
    cx, cy = 408, 95                                                # steel inspection hatch, hinged
    inset(d, cx - 12, cy - 5, cx + 12, cy + 5, "ink", "steel", "deep", "steel_l")
    for y in (cy - 3, cy, cy + 3):
        px(d, cx - 12, y, "steel_l"); px(d, cx - 11, y, "edge")
    R(d, cx - 4, cy - 1, cx + 3, cy + 1, "slate")                   # finger recess
    R(d, cx - 4, cy - 1, cx + 3, cy - 1, "ink")
    R(d, cx + 7, cy - 2, cx + 9, cy + 2, "teal_d")                  # indicator slot
    R(d, cx + 8, cy - 1, cx + 8, cy + 1, "glow")
    return img


def edge_tech_framing():
    img, d = canvas()
    # Codex correction: small separate wall-service modules preserve foliage gaps and edge depth.
    x0 = WALK[2] + 3
    R(d, x0, UI_TOP + 1, x0 + 1, UI_BOTTOM - 1, "slate")
    R(d, x0, UI_TOP + 1, x0, UI_BOTTOM - 1, "steel_l")
    for y in (83, 173, 271):
        R(d, x0 + 1, y - 2, W - 2, y + 29, "stone_d")
        R(d, x0 + 2, y - 3, W - 3, y + 26, "stone")
        R(d, x0 + 2, y - 3, W - 3, y - 2, "stone_hl")
        R(d, x0 + 2, y - 2, x0 + 3, y + 26, "stone_l")
        R(d, x0 + 5, y, W - 4, y + 24, "ink")
        R(d, x0 + 6, y + 1, W - 5, y + 22, "steel")
        R(d, x0 + 6, y + 1, W - 5, y + 1, "steel_l")
        R(d, x0 + 8, y + 5, x0 + 10, y + 12, "teal_d")
        R(d, x0 + 9, y + 6, x0 + 9, y + 11, "teal")
        px(d, x0 + 9, y + 6, "glow")
        for sy in (y + 16, y + 19):
            R(d, x0 + 8, sy, W - 6, sy, "deep")
        px(d, x0 + 6, y + 2, "brass_l")
        px(d, W - 5, y + 22, "brass")
    jx = PROTECTED["relay"][0]                                      # wall junction box above y77
    R(d, jx - 8, 64, jx + 8, 75, "ink")
    R(d, jx - 7, 65, jx + 7, 74, "steel")
    R(d, jx - 7, 65, jx + 7, 65, "edge")
    R(d, jx - 7, 65, jx - 7, 74, "steel_l")
    R(d, jx + 7, 66, jx + 7, 74, "slate")
    R(d, jx - 5, 67, jx + 5, 69, "brass_d")
    R(d, jx - 5, 67, jx + 5, 67, "brass_l")
    R(d, jx + 2, 71, jx + 4, 72, "teal_d"); px(d, jx + 3, 71, "glow")
    R(d, jx - 2, 75, jx + 2, 76, "brass")                          # gland down into the raceway
    return img


CLUMPS = [(427, 120, 7), (437, 160, 5), (424, 222, 6), (440, 256, 6), (486, 150, 5), (528, 278, 6),
          (114, 250, 6), (136, 231, 4), (395, 104, 5), (524, 252, 4), (586, 262, 5)]


def botanical_integration():
    img, d = canvas()
    for i, (cx, cy, r) in enumerate(CLUMPS):
        rng = np.random.default_rng(1300 + i)                       # fixed seeds, deterministic layout
        ry = max(2, (r * 2) // 3)                                   # rounder cluster, not a horizontal smear
        leaves = sorted(((cx + int(rng.integers(-r + 1, r)), cy + int(rng.integers(-ry, ry + 1)))
                         for _ in range(r + 3)), key=lambda p: p[1])
        for x, y in leaves:                                         # one-texel shade to the lower right only
            R(d, x, y + 1, x + 1, y + 1, "leaf_d")
            px(d, x + 2, y, "leaf_d")
        for j, (x, y) in enumerate(leaves):                         # 2x2 leaves, back to front
            R(d, x, y - 1, x + 1, y, "leaf" if j % 2 else "leaf_m")
            px(d, x, y - 1, "leaf_l" if j % 3 == 0 else "leaf_m")
        if i % 3 == 0:
            px(d, cx + 1, cy - 1, "bloom"); px(d, cx + 2, cy - 1, "bloom_l")
        elif i % 3 == 1:
            px(d, cx - 2, cy, "bloom_y")
    return img


DRAW = {"paving-transitions": paving_transitions, "cable-raceway": cable_raceway,
        "relay-floor-panel": relay_floor_panel, "survey-threshold": survey_threshold,
        "assist-workpad": assist_workpad, "trace-plates": trace_plates, "edge-tech-framing": edge_tech_framing,
        "botanical-integration": botanical_integration}


# ------------------------------------------------------------------------------------------------------- build

def build_all():
    imgs = {"inherited-base": base_layer()}
    imgs.update({n: DRAW[n]() for n in LAYERS})
    order = ["inherited-base"] + LAYERS
    arrays = {n: np.asarray(imgs[n]) for n in order}
    flat = BA.composite([imgs[n] for n in order])
    flat_img = Image.fromarray(flat, "RGBA")
    blobs, files = {}, []
    for i, n in enumerate(order):
        f = fname(f"layer{i:02d}-{n}", "png")
        blobs[f] = BA.png_bytes(imgs[n])
        files.append(f)
    flat_f = fname("merged-flat", "png")
    blobs[flat_f] = BA.png_bytes(flat_img)
    make_pxo = BA.load_make_pxo()
    pxo_f = fname("layered-source", "pxo")
    blobs[pxo_f] = make_pxo([arrays], [1.0], blobs[flat_f], os.path.splitext(flat_f)[0], 1, order=order, dt=ZIP_DT)
    ora_f = fname("layered-supplement", "ora")
    blobs[ora_f] = BA.make_ora(order, files, blobs, blobs[flat_f], BA.png_bytes(flat_img.resize((256, 144), Image.NEAREST)))
    with open(os.path.join(REPO, BASE_REL), "rb") as f:
        base_sha = BA.sha(f.read())
    manifest = {
        "schema": "worlds-between.outskirts-environment-source.v1",
        "canvas": [W, H],
        "base": {"file": BASE_REL, "sha256": base_sha,
                 "method": "nearest-resample 1672x941 -> 640x360; retained flattened inherited art (UNAPPROVED, not native)"},
        "layers": [{"name": n, "file": f, "sha256": BA.sha(blobs[f]),
                    "kind": "inherited-base" if n == "inherited-base" else "native-authored"}
                   for n, f in zip(order, files)],
        "flat": {"file": flat_f, "sha256": BA.sha(blobs[flat_f])},
        "pxo": {"file": pxo_f, "sha256": BA.sha(blobs[pxo_f])},
        "ora": {"file": ora_f, "sha256": BA.sha(blobs[ora_f])},
        "author": {"file": AUTHOR_REL, "sha256TextLf": BA.text_lf_sha(os.path.join(REPO, AUTHOR_REL))},
        "protected": PROTECTED,
        "artApproved": False,
        "defaultAdopted": False,
    }
    man_f = fname("source-manifest", "json")
    blobs[man_f] = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return order, files, arrays, flat, blobs, manifest, man_f


def checks(order, files, arrays, flat, blobs, manifest, man_f):
    import io, zipfile
    res = []

    def ok(name, cond, detail=""):
        res.append((name, bool(cond), detail))

    base = arrays["inherited-base"]
    ok("canvas 640x360", manifest["canvas"] == [640, 360] and all(a.shape == (H, W, 4) for a in arrays.values()))
    ok("base opaque", (base[..., 3] == 255).all())
    native = [n for n in order if n != "inherited-base"]
    ok("native layer count >= 6", len(native) >= 6, str(len(native)))
    x0, y0, x1, y1 = WALK
    for n in native:
        a = arrays[n][..., 3]
        ys, xs = np.nonzero(a)
        ok(f"{n}: hard alpha", set(np.unique(a)) <= {0, 255})
        ok(f"{n}: nonempty", len(xs) > 0, f"{len(xs)} px, x {xs.min()}..{xs.max()} y {ys.min()}..{ys.max()}")
        ok(f"{n}: UI strips transparent", not a[:UI_TOP + 1].any() and not a[UI_BOTTOM:].any())
        nc = len(np.unique(arrays[n][a == 255][:, :3], axis=0))
        ok(f"{n}: unique colours <= 32", nc <= 32, str(nc))
        ok(f"{n}: differs from base where drawn", (arrays[n][a == 255][:, :3] != base[a == 255][:, :3]).any(axis=1).mean() > 0.9)
        if n in UPRIGHT:
            ok(f"{n}: entirely above y77 or right of x616",
               not a[y0:y1 + 1, :x1 + 1].any(), "upright equipment outside walk bounds")
    ok("merged UI strips == base", np.array_equal(flat[:UI_TOP + 1], base[:UI_TOP + 1])
       and np.array_equal(flat[UI_BOTTOM:], base[UI_BOTTOM:]))
    for key in ("relay", "survey", "assist"):
        x, y = PROTECTED[key]
        ok(f"{key} fixture covers its point", any(arrays[n][y, x, 3] for n in native))
    for i, (x, y) in enumerate(PROTECTED["traces"]):
        ok(f"trace {i} plate covers its point", arrays["trace-plates"][y, x, 3] == 255)
    for key in ("spawn", "npc", "encounter"):                          # central lane / actors left inherited
        x, y = PROTECTED[key]
        ok(f"{key} 12 px radius untouched", np.array_equal(flat[y - 12:y + 13, x - 12:x + 13], base[y - 12:y + 13, x - 12:x + 13]))
    ok("merged opaque", (flat[..., 3] == 255).all())
    ok("merged == recomposite", np.array_equal(flat, BA.composite([Image.fromarray(arrays[n]) for n in order])))
    z = zipfile.ZipFile(io.BytesIO(blobs[manifest["pxo"]["file"]]))
    data = json.loads(z.read("data.json"))
    ok("pxo size/layers", data["size_x"] == W and data["size_y"] == H and [l["name"] for l in data["layers"]] == order)
    pxo = [np.frombuffer(z.read(f"image_data/frames/1/layer_{i}"), np.uint8).reshape(H, W, 4) for i in range(1, len(order) + 1)]
    ok("pxo layers == layer pngs", all(np.array_equal(p, arrays[n]) for p, n in zip(pxo, order)))
    ok("pxo reconstruct == merged", np.array_equal(BA.composite([Image.fromarray(p) for p in pxo]), flat))
    zo = zipfile.ZipFile(io.BytesIO(blobs[manifest["ora"]["file"]]))
    ok("ora mimetype first+stored", zo.infolist()[0].filename == "mimetype" and zo.infolist()[0].compress_type == zipfile.ZIP_STORED)
    ok("ora merged == merged bytes", zo.read("mergedimage.png") == blobs[manifest["flat"]["file"]])
    ok("ora layers == layer pngs", all(zo.read(f"data/{f}") == blobs[f] for f in files))
    ok("manifest keys", list(manifest) == ["schema", "canvas", "base", "layers", "flat", "pxo", "ora", "author",
                                           "protected", "artApproved", "defaultAdopted"])
    ok("manifest hashes", all(BA.sha(blobs[l["file"]]) == l["sha256"] for l in manifest["layers"]))
    ok("manifest kinds", [l["kind"] for l in manifest["layers"]] == ["inherited-base"] + ["native-authored"] * len(native))
    ok("unapproved/not default", manifest["artApproved"] is False and manifest["defaultAdopted"] is False)
    names = [man_f] + [manifest[k]["file"] for k in ("flat", "pxo", "ora")] + files
    ok("lowercase names", all(n == n.lower() for n in names))
    longest = max(len(os.path.join(REPO, OUT_REL, n)) for n in names)
    ok("path length <= 240", longest <= 240, str(longest))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["build", "check"])
    ap.add_argument("--pixelorama", action="store_true")
    a = ap.parse_args()
    order, files, arrays, flat, blobs, manifest, man_f = build_all()
    out = os.path.join(REPO, OUT_REL)
    res = []
    if a.mode == "build":
        os.makedirs(out, exist_ok=True)
        for n, b in blobs.items():
            p = os.path.join(out, n)
            if os.path.exists(p):
                with open(p, "rb") as f:
                    if f.read() != b:
                        raise SystemExit(f"refusing to overwrite different bytes: {p}")
            else:
                with open(p, "wb") as f:
                    f.write(b)
        print(f"wrote {len(blobs)} files to {OUT_REL}")
    else:
        for n, b in blobs.items():
            p = os.path.join(out, n)
            res.append((f"disk == rebuild: {n}", os.path.exists(p) and open(p, "rb").read() == b, ""))
        res.append(("no extra files in output dir", sorted(os.listdir(out)) == sorted(blobs), ""))
    res += checks(order, files, arrays, flat, blobs, manifest, man_f)
    if a.pixelorama:
        res += BA.pixelorama_gate(blobs, manifest, arrays, flat, order)
    fails = [r for r in res if not r[1]]
    for name, good, detail in res:
        print(("PASS " if good else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    print(f"{len(res) - len(fails)}/{len(res)} checks pass; manifest {man_f}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
