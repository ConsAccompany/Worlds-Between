"""Patrol automaton battle static (content.enemy.patrol.static) -- UNAPPROVED technical candidate.

Native 64x64, faces LEFT toward the party, display 1x, pivot (32,56); both boot soles on row 55.
Every pixel is placed from integer polygons/rects/points below (Pillow ImageDraw, no antialias,
no fonts, no randomness). Output is byte-identical on rebuild.

Usage: python <this file> --out-dir PATH
"""
import argparse
import hashlib
import importlib.util
import io
import json
import os

from PIL import Image, ImageDraw

W, H = 64, 64
PIVOT = (32, 56)
SOLE_ROW = 55
PREFIX = "rpg-2-star-ocean-the-second_patrol_"
SUFFIX = "_bench-v01_20261018-234437-8dfccbf6"
HERE = os.path.dirname(os.path.abspath(__file__))
HELPER = os.path.join(HERE, "..", "inputs",
                      "rpg-2-star-ocean-the-second_benchmark_native-format-helper_v01_20261018-234437-8dfccbf6.py")

# Palette: warm sandstone plating, cool steel joints, one amber warning, teal tech accent.
OUT = (36, 30, 34, 255)        # shared outline
STEEL_D = (66, 64, 72, 255)    # joints / far side
STEEL_M = (104, 104, 110, 255)
STEEL_L = (150, 150, 150, 255)
FAR_M = (84, 78, 82, 255)      # far leg mid (pushed back in value)
PLATE_D = (112, 82, 60, 255)   # warm masonry plating ramp
PLATE_M = (156, 118, 82, 255)
PLATE_L = (196, 158, 108, 255)
PLATE_H = (226, 200, 150, 255)
MOSS = (86, 102, 60, 255)      # foliage-tinted joint covers
MOSS_L = (122, 140, 78, 255)
AMBER = (236, 168, 56, 255)
AMBER_D = (170, 96, 34, 255)
TEAL_D = (26, 98, 104, 255)
TEAL = (48, 168, 166, 255)
TEAL_L = (156, 236, 218, 255)
VISOR = (24, 34, 44, 255)


def layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def poly(d, pts, fill, outline=OUT):
    d.polygon(pts, fill=fill, outline=outline)


def px(d, pts, color):
    for p in pts:
        d.point(p, fill=color)


def draw_leg(d, hip, knee, ankle, toe_x, heel_x, mid, dark, light):
    """Reverse-knee (digitigrade) leg: thigh forward, shin back, flat boot whose sole sits on row 55."""
    hx, hy = hip
    kx, ky = knee
    ax, ay = ankle
    # thigh
    poly(d, [(hx - 3, hy - 1), (hx + 3, hy + 1), (kx + 2, ky + 1), (kx - 2, ky - 1)], mid)
    d.line([(hx - 2, hy + 1), (kx - 1, ky)], fill=light)
    # shin (thinner strut)
    poly(d, [(kx - 1, ky), (kx + 2, ky - 1), (ax + 2, ay), (ax - 1, ay + 1)], dark)
    d.line([(kx + 1, ky), (ax + 1, ay)], fill=mid)
    # knee joint
    d.ellipse([kx - 2, ky - 2, kx + 2, ky + 2], fill=dark, outline=OUT)
    px(d, [(kx - 1, ky - 1)], light)
    # boot: wedge toe forward (left), heel spur back, sole row 55
    poly(d, [(toe_x, SOLE_ROW), (toe_x + 2, ay + 1), (heel_x - 2, ay + 1), (heel_x, SOLE_ROW)], mid)
    d.line([(toe_x + 3, ay + 2), (heel_x - 3, ay + 2)], fill=light)
    d.line([(toe_x + 1, SOLE_ROW - 1), (heel_x - 1, SOLE_ROW - 1)], fill=dark)


def build_layers():
    layers = {}

    # 1. far leg (behind hull, value pushed down)
    im = layer(); d = ImageDraw.Draw(im)
    draw_leg(d, hip=(38, 38), knee=(35, 45), ankle=(41, 51), toe_x=35, heel_x=47,
             mid=FAR_M, dark=STEEL_D, light=STEEL_M)
    layers["far-leg"] = im

    # 2. hull: compact armoured egg + backpack + antenna shaft, warm plate planes
    im = layer(); d = ImageDraw.Draw(im)
    poly(d, [(45, 24), (51, 25), (51, 35), (45, 36)], STEEL_M)                 # backpack
    d.line([(46, 34), (50, 34)], fill=STEEL_D)
    d.line([(43, 22), (45, 12)], fill=OUT)                                     # antenna shaft
    d.line([(44, 22), (46, 12)], fill=STEEL_L)
    poly(d, [(27, 24), (40, 21), (46, 25), (48, 33), (43, 39), (29, 39), (25, 34)], PLATE_M)
    poly(d, [(28, 25), (40, 22), (45, 26), (29, 28)], PLATE_L, outline=PLATE_L)  # top plane (lit)
    d.line([(31, 24), (39, 22)], fill=PLATE_H)                                 # rim highlight
    poly(d, [(26, 34), (47, 34), (43, 38), (29, 38)], PLATE_D, outline=PLATE_D)  # belly plane (shade)
    d.line([(27, 31), (46, 31)], fill=PLATE_D)                                 # plate seam
    px(d, [(30, 29), (42, 29), (30, 36), (42, 36)], PLATE_H)                   # rivets
    # hip cover (moss-tinted) over both hips
    d.ellipse([28, 36, 35, 42], fill=MOSS, outline=OUT)
    px(d, [(30, 37), (31, 37), (29, 38)], MOSS_L)
    layers["hull"] = im

    # 3. head + left-facing sensor visor
    im = layer(); d = ImageDraw.Draw(im)
    poly(d, [(25, 23), (30, 23), (30, 29), (25, 29)], STEEL_D)                 # neck collar
    poly(d, [(13, 20), (25, 16), (30, 19), (30, 27), (24, 30), (15, 29), (11, 25)], STEEL_M)
    poly(d, [(14, 20), (25, 17), (29, 20), (16, 22)], STEEL_L, outline=STEEL_L)  # brow plane
    d.line([(16, 28), (24, 29)], fill=STEEL_D)                                 # jaw shade
    poly(d, [(11, 23), (22, 22), (22, 26), (12, 26)], VISOR, outline=OUT)      # visor slot
    layers["head-sensor"] = im

    # 4. near leg (in front of hull, full value)
    im = layer(); d = ImageDraw.Draw(im)
    draw_leg(d, hip=(31, 39), knee=(25, 46), ankle=(30, 52), toe_x=20, heel_x=34,
             mid=STEEL_L, dark=STEEL_M, light=PLATE_H)
    d.ellipse([29, 37, 33, 41], fill=MOSS, outline=OUT)                        # near hip bolt
    px(d, [(30, 38)], MOSS_L)
    layers["near-leg"] = im

    # 5. restrained amber warning mark on the flank plate
    im = layer(); d = ImageDraw.Draw(im)
    d.rectangle([35, 27, 41, 30], fill=AMBER)
    px(d, [(36, 30), (37, 29), (38, 28), (39, 27), (39, 30), (40, 29), (41, 28)], AMBER_D)
    layers["warning-mark"] = im

    # 6. teal technology accent: sensor lens, backpack vent, antenna beacon
    im = layer(); d = ImageDraw.Draw(im)
    d.rectangle([12, 23, 15, 25], fill=TEAL)
    px(d, [(12, 24), (13, 24)], TEAL_L)
    px(d, [(16, 24), (17, 24), (19, 24)], TEAL_D)                              # scan trace in slot
    d.rectangle([47, 27, 48, 32], fill=TEAL_D)
    px(d, [(47, 28), (47, 30)], TEAL)
    d.rectangle([45, 10, 47, 12], fill=TEAL)
    px(d, [(46, 10)], TEAL_L)
    layers["tech-accent"] = im
    return layers


def pixels(im):
    """Row-major RGBA tuples (avoids the deprecated Image.getdata)."""
    raw = im.tobytes()
    return [tuple(raw[i:i + 4]) for i in range(0, len(raw), 4)]


def composite(layers):
    out = layer()
    for im in layers.values():
        out.alpha_composite(im)
    return out


def check(layers, comp):
    px_ = comp.load()
    for y in range(H):
        for x in range(W):
            a = px_[x, y][3]
            assert a in (0, 255), "alpha must be 0/255"
            if a and (x < 2 or x >= W - 2 or y < 2 or y >= SOLE_ROW + 1):
                raise AssertionError(f"pixel outside allowed area at {(x, y)}")
    colors = {c for c in pixels(comp) if c[3]}
    assert len(colors) <= 24, f"{len(colors)} opaque colors > 24"
    sole = [x for x in range(W) if px_[x, SOLE_ROW][3]]
    assert any(x < PIVOT[0] for x in sole) and any(x > PIVOT[0] + 2 for x in sole), "both soles on row 55"
    for name, im in layers.items():
        n = sum(1 for c in pixels(im) if c[3])
        assert n >= 6, f"layer {name} has only {n} opaque pixels"
        visible = sum(1 for a, b in zip(pixels(im), pixels(comp)) if a[3] and a == b)
        assert visible >= 6, f"layer {name} is not meaningfully visible"
    return len(colors)


def long_path(p):
    p = os.path.abspath(p)
    if os.name == "nt" and not p.startswith("\\\\?\\"):
        p = "\\\\?\\" + p
    return p


def png_bytes(im):
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out_dir = long_path(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    spec = importlib.util.spec_from_file_location("native_helper", long_path(HELPER))
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)

    layers = build_layers()
    comp = composite(layers)
    ncolors = check(layers, comp)

    files = {}
    comp_name = PREFIX + "battle-static-composite" + SUFFIX + ".png"
    files[comp_name] = png_bytes(comp)
    layer_files = {}
    for role, im in layers.items():
        name = PREFIX + "layer-" + role + SUFFIX + ".png"
        layer_files[role] = name
        files[name] = png_bytes(im)
    pxo_name = PREFIX + "battle-static" + SUFFIX + ".pxo"
    ora_name = PREFIX + "battle-static" + SUFFIX + ".ora"
    files[pxo_name] = helper.pxo_bytes([layers], [1.0], files[comp_name], pxo_name[:-4])
    files[ora_name] = helper.ora_bytes(layers)

    for name, data in files.items():
        with open(os.path.join(out_dir, name), "wb") as f:
            f.write(data)

    src_path = os.path.abspath(__file__)
    src_rel = os.path.relpath(src_path, os.path.abspath(args.out_dir)).replace("\\", "/")
    sha = {n: hashlib.sha256(b).hexdigest() for n, b in sorted(files.items())}
    with open(long_path(src_path), "rb") as f:
        sha[src_rel] = hashlib.sha256(f.read()).hexdigest()
    manifest = {
        "schemaVersion": 1, "width": W, "height": H, "pivot": list(PIVOT),
        "composite": comp_name, "pxo": pxo_name, "ora": ora_name,
        "layerOrder": list(layers), "layers": layer_files,
        "source": src_rel, "sha256": sha,
    }
    man_name = PREFIX + "asset-manifest" + SUFFIX + ".json"
    with open(os.path.join(out_dir, man_name), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2, sort_keys=False)
        f.write("\n")
    print(f"OK patrol static: {len(layers)} layers, {ncolors} opaque colors, {len(files) + 1} files -> {args.out_dir}")


if __name__ == "__main__":
    main()
