"""Bake the globe's sphere-tint layer for the native global map (UNAPPROVED map-art candidate, 2026-10-17).

The globe shows each Earth civilization sphere in its own restrained land colour. This tool turns Natural
Earth 50m countries into a small palette PNG on a 0.25 deg lon/lat grid (row 0 = 90N, column 0 = 180W),
one palette index per sphere, and records for every ring of the map's own global land layer
(ne_110m_land, in geodata order) whether one sphere covers it (flat fill) or several do (the map clips the
texture to that ring's polygon). The map's coasts, borders, regions, markers and routes are untouched:
only the fill colour inside the existing land polygons changes.

Sphere rule (the same as the v02 map-art candidate, ab9459d4; canon: five Earth spheres, creator decision
2026-10-15):
  science    = ADM0_A3 USA or CAN
  borderland = other North America (Mexico, Central America, Caribbean incl. Puerto Rico / US Virgin Is.)
  magic      = CONTINENT South America
  wuxia      = CONTINENT Asia (except Turkey)
  nature     = CONTINENT Oceania
  culture    = CONTINENT Europe or Africa (except Russia)
  dlc        = CONTINENT Antarctica
  unassigned = Russia, Turkey, Greenland, Bermuda, St. Pierre and Miquelon, open-ocean islands
A European country's polygons in the Western Hemisphere (e.g. French Guiana, Guadeloupe) follow geography:
south of 13N -> magic, else borderland.

All tints sit in the land value family (sRGB luma 0.43-0.54), above lakes (#2f6476, 0.35) and sea
(#102f3d, 0.16), so the land / lake / sea hierarchy of the native pass is kept.

Usage (repo root; the real Python is noted in the repo memory):
  python -I tools/<this file> --cache-dir <temp dir> [--out <json path>]
"""
import argparse
import base64
import hashlib
import io
import json
import os
import urllib.request

import numpy as np
from PIL import Image, ImageDraw

TAG = "m2-map-art-native-v01r1_20261017-022144-f9b0d28b"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEODATA = os.path.join(REPO, "game", "data", "world-map",
    "rpg-2-star-ocean-the-second_earth-map_runtime-geodata_m2-us-science-v02_20261015-175011-944d9635.json")
DEFAULT_OUT = os.path.join(REPO, "game", "data", "world-map",
    "rpg-2-star-ocean-the-second_earth-map_globe-sphere-tint-layer_" + TAG + ".json")
COUNTRIES_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_50m_admin_0_countries.geojson"
COUNTRIES_SHA256 = "3e458fc036ad0a66411f2c1e6cac49c5d7bfb81cb1123bc513b22511a2b7fdeb"
CELLS_PER_DEG = 4
WIDTH = 360 * CELLS_PER_DEG
HEIGHT = 180 * CELLS_PER_DEG
# Empty cells next to a country take its sphere, so cells that straddle a 110m coast are never left blank.
DILATE_STEPS = 6
# A ring is "one sphere" when that sphere holds at least this share of its cells.
SINGLE_SHARE = 0.97
PALETTE = [
    ("none", None),
    ("science", "#5f8f76"),
    ("magic", "#7e6d96"),
    ("wuxia", "#97695a"),
    ("nature", "#86904c"),
    ("culture", "#a08b63"),
    ("borderland", "#777267"),
    ("dlc_antarctica", "#68747d"),
    ("unassigned", "#6b716c"),
]
INDEX = {role: i for i, (role, _) in enumerate(PALETTE)}


def sphere_of(props):
    a3 = props.get("ADM0_A3")
    continent = props.get("CONTINENT")
    if a3 in ("USA", "CAN"):
        return "science"
    if a3 in ("RUS", "TUR", "GRL", "BMU", "SPM"):
        return "unassigned"
    return {
        "North America": "borderland",
        "South America": "magic",
        "Asia": "wuxia",
        "Oceania": "nature",
        "Europe": "culture",
        "Africa": "culture",
        "Antarctica": "dlc_antarctica",
    }.get(continent, "unassigned")


def polygon_sphere(sphere, props, ring):
    """Overseas polygons of European countries follow their geography (French Guiana, Antilles)."""
    if props.get("CONTINENT") != "Europe":
        return sphere
    lons = [p[0] for p in ring]
    lats = [p[1] for p in ring]
    lon = sum(lons) / len(lons)
    lat = sum(lats) / len(lats)
    if lon < -25.0 and lon > -100.0:
        return "magic" if lat < 13.0 else "borderland"
    return sphere


def to_px(lon, lat):
    return ((lon + 180.0) * CELLS_PER_DEG, (90.0 - lat) * CELLS_PER_DEG)


def load_countries(cache_dir):
    path = os.path.join(cache_dir, "ne_50m_admin_0_countries_v5.1.2.geojson")
    if not os.path.exists(path):
        with urllib.request.urlopen(COUNTRIES_URL, timeout=120) as response:
            data = response.read()
        with open(path, "wb") as f:
            f.write(data)
    with open(path, "rb") as f:
        raw = f.read()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != COUNTRIES_SHA256:
        raise SystemExit("ne_50m_admin_0_countries sha256 mismatch: " + digest)
    return json.loads(raw.decode("utf-8"))


def rasterize(countries):
    image = Image.new("L", (WIDTH, HEIGHT), 0)
    draw = ImageDraw.Draw(image)
    members = {}
    # Outer rings only: enclaves (Lesotho, San Marino, ...) share their host's sphere.
    for feature in countries["features"]:
        props = feature["properties"]
        sphere = sphere_of(props)
        geometry = feature["geometry"]
        polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
        for polygon in polygons:
            outer = polygon[0]
            role = polygon_sphere(sphere, props, outer)
            members.setdefault(role, set()).add(props.get("ADM0_A3"))
            draw.polygon([to_px(p[0], p[1]) for p in outer], fill=INDEX[role])
    return np.array(image, dtype=np.uint8), {k: sorted(v) for k, v in members.items()}


def dilate(index):
    out = index.copy()
    for _ in range(DILATE_STEPS):
        empty = out == 0
        if not empty.any():
            break
        p = np.pad(out, 1)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            neighbour = p[1 + dy:1 + dy + HEIGHT, 1 + dx:1 + dx + WIDTH]
            take = empty & (out == 0) & (neighbour != 0)
            out[take] = neighbour[take]
    return out


def ring_spheres(rings, index):
    """Per global land ring: a single palette index, or -1 when several spheres share it. Holes get 0."""
    out = []
    for ring in rings:
        if ring["hole"]:
            out.append(0)
            continue
        flat = ring["points"]
        pts = [to_px(flat[i], flat[i + 1]) for i in range(0, len(flat), 2)]
        mask_img = Image.new("1", (WIDTH, HEIGHT), 0)
        ImageDraw.Draw(mask_img).polygon(pts, fill=1, outline=1)
        mask = np.array(mask_img, dtype=bool)
        values = index[mask]
        values = values[values != 0]
        if values.size == 0:
            # A speck no country raster reaches: the nearest labelled cell to its first point.
            x, y = pts[0]
            ys, xs = np.nonzero(index)
            k = int(np.argmin((xs - x) ** 2 + (ys - y) ** 2))
            out.append(int(index[ys[k], xs[k]]))
            continue
        counts = np.bincount(values, minlength=len(PALETTE))
        top = int(np.argmax(counts))
        out.append(top if counts[top] >= SINGLE_SHARE * values.size else -1)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", required=True)
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args()
    os.makedirs(args.cache_dir, exist_ok=True)
    with open(GEODATA, "rb") as f:
        geodata_raw = f.read()
    geodata = json.loads(geodata_raw.decode("utf-8"))
    rings = geodata["layers"]["global_land"]["rings"]

    raw_index, members = rasterize(load_countries(args.cache_dir))
    index = dilate(raw_index)
    per_ring = ring_spheres(rings, index)

    image = Image.fromarray(index, mode="P")
    flat_palette = []
    for _, hexcolor in PALETTE:
        h = (hexcolor or "#000000").lstrip("#")
        flat_palette += [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    image.putpalette(flat_palette)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True, transparency=0)
    png = buffer.getvalue()

    geodata_lf = geodata_raw.replace(b"\r\n", b"\n")
    out = {
        "schema": "worlds-between.world-map.sphere-tint-layer.v1",
        "status": "unapproved_map_art_candidate",
        "tag": TAG,
        "generated_by": os.path.relpath(os.path.abspath(__file__), REPO).replace("\\", "/"),
        "bbox_wsen": [-180.0, -90.0, 180.0, 90.0],
        "grid": {"width": WIDTH, "height": HEIGHT, "cells_per_degree": CELLS_PER_DEG, "cell": "lon/lat (plate carree), row 0 = north", "dilate_steps": DILATE_STEPS},
        "sphere_rule": {
            "science": "ADM0_A3 USA or CAN",
            "borderland": "other North America (Mexico, Central America, Caribbean incl. Puerto Rico and US Virgin Islands)",
            "magic": "CONTINENT South America",
            "wuxia": "CONTINENT Asia (except Turkey)",
            "nature": "CONTINENT Oceania",
            "culture": "CONTINENT Europe or Africa (except Russia)",
            "dlc_antarctica": "CONTINENT Antarctica",
            "unassigned": "Russia, Turkey, Greenland, Bermuda, St. Pierre and Miquelon, open-ocean islands (no creator decision)",
            "overseas": "European countries' Western-Hemisphere polygons: south of 13N magic, else borderland",
        },
        "palette": [{"index": i, "role": role, "color": color} for i, (role, color) in enumerate(PALETTE)],
        "members": members,
        "global_ring_count": len(rings),
        "ring_spheres": per_ring,
        "ring_spheres_note": "per ring of geodata layers.global_land (order kept): palette index of the one sphere covering >= %.0f%% of it, -1 = several (clip the texture), 0 = hole" % (SINGLE_SHARE * 100),
        "class_counts": {PALETTE[i][0]: int((index == i).sum()) for i in range(len(PALETTE))},
        "sources": [
            {"id": "ne_50m_admin_0_countries", "url": COUNTRIES_URL, "sha256": COUNTRIES_SHA256, "hash_algorithm": "sha256-bytes",
             "license": "Natural Earth vector data is public domain: https://www.naturalearthdata.com/about/terms-of-use/"},
            {"id": "natural_earth_global_land_rings", "path": os.path.relpath(GEODATA, REPO).replace("\\", "/"),
             "sha256": hashlib.sha256(geodata_lf).hexdigest(), "hash_algorithm": "sha256-text-lf-v1"},
        ],
        "png_sha256": hashlib.sha256(png).hexdigest(),
        "png_base64": base64.b64encode(png).decode("ascii"),
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    mixed = sum(1 for v in per_ring if v == -1)
    print("SPHERE_TINT_BAKE_OK %dx%d png=%d bytes json=%d bytes rings=%d mixed=%d" % (WIDTH, HEIGHT, len(png), os.path.getsize(args.out), len(rings), mixed))
    print(json.dumps(out["class_counts"]))


if __name__ == "__main__":
    main()
