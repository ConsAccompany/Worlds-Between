"""Bake the US-east relief layer for the native global map (UNAPPROVED map-art candidate, 2026-10-17).

Turns real elevation and sea depth into a small palette PNG on a lon/lat grid over the map's `us_east`
geodata clip box, masked by the map's own Natural Earth land and lake rings, so relief never crosses a
coast the map does not draw. Classes (no invented terrain):
  land  = elevation band (< 120 m, < 230 m, < 450 m, higher) x hillshade (flat, shadow, lit; NW light);
  sea   = inner shelf (> -60 m), outer shelf (> -200 m); deeper water and every lake stay transparent.
The map script draws the PNG over its land polygons with nearest filtering (one texture per region view).

Elevation source: Tilezen/Mapzen "Terrarium" terrain tiles (AWS open data, zoom 7), which merge SRTM,
USGS NED/3DEP, GMTED2010 and ETOPO1 for this area. Attribution:
https://github.com/tilezen/joerd/blob/master/docs/attribution.md

Usage (repo root; the real Python is noted in the repo memory):
  python -I tools/<this file> --cache-dir <empty temp dir for tiles> [--out <json path>]
"""
import argparse
import base64
import hashlib
import io
import json
import math
import os
import urllib.request

import numpy as np
from PIL import Image, ImageDraw

TAG = "m2-map-art-native-v01_20261017-015515-7bf04753"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEODATA = os.path.join(REPO, "game", "data", "world-map",
    "rpg-2-star-ocean-the-second_earth-map_runtime-geodata_m2-us-science-v02_20261015-175011-944d9635.json")
DEFAULT_OUT = os.path.join(REPO, "game", "data", "world-map",
    "rpg-2-star-ocean-the-second_earth-map_us-east-relief-layer_" + TAG + ".json")
TILE_URL = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
ZOOM = 7
# Grid steps: 64 cells per degree of longitude; latitude cells ~cos(41 deg) as tall, so cells are near-square
# at the regional views' standard parallels (40 and 42 deg).
LON_STEP = 1.0 / 64.0
LAT_STEP = 1.0 / 84.0
BAND_LIMITS_M = [120.0, 230.0, 450.0]
SHELF_LIMITS_M = [-60.0, -200.0]
SUN_AZIMUTH_DEG = 315.0
SUN_ALTITUDE_DEG = 40.0
Z_FACTOR = 4.0
SHADE_THRESHOLD = 0.08
# Elevation is box-smoothed over this many cells before shading, so only coherent ridges and valleys survive.
SMOOTH_CELLS = 3
# Palette: index -> (role, hex). Index 0 is transparent. Land "low/flat" is the map's own COLOR_LAND and stays
# transparent so the land polygons show through; the map script keeps that constant equal to land_low.
PALETTE = [
    ("none", None),
    ("land_b0_shadow", "#57694f"),
    ("land_b0_lit", "#74865f"),
    ("land_b1", "#6c7d5a"),
    ("land_b1_shadow", "#5b6b4f"),
    ("land_b1_lit", "#7a8a62"),
    ("land_b2", "#72805c"),
    ("land_b2_shadow", "#5f6c50"),
    ("land_b2_lit", "#818d65"),
    ("land_b3", "#7b8461"),
    ("land_b3_shadow", "#656b51"),
    ("land_b3_lit", "#8d946c"),
    ("sea_inner_shelf", "#1d4656"),
    ("sea_outer_shelf", "#173b4b"),
]
LAND_LOW = "#677a59"


def tile_xy(lon, lat, z):
    n = 2 ** z
    x = (lon + 180.0) / 360.0 * n
    r = math.radians(lat)
    y = (1.0 - math.log(math.tan(r) + 1.0 / math.cos(r)) / math.pi) / 2.0 * n
    return x, y


def fetch_tiles(bbox, cache_dir):
    west, south, east, north = bbox
    x0, y0 = tile_xy(west, north, ZOOM)
    x1, y1 = tile_xy(east, south, ZOOM)
    tiles = []
    for ty in range(int(y0), int(y1) + 1):
        for tx in range(int(x0), int(x1) + 1):
            path = os.path.join(cache_dir, "terrarium_%d_%d_%d.png" % (ZOOM, tx, ty))
            if not os.path.exists(path):
                with urllib.request.urlopen(TILE_URL.format(z=ZOOM, x=tx, y=ty), timeout=60) as response:
                    data = response.read()
                with open(path, "wb") as f:
                    f.write(data)
            with open(path, "rb") as f:
                digest = hashlib.sha256(f.read()).hexdigest()
            tiles.append({"z": ZOOM, "x": tx, "y": ty, "sha256": digest})
    xs = sorted({t["x"] for t in tiles})
    ys = sorted({t["y"] for t in tiles})
    mosaic = np.zeros((len(ys) * 256, len(xs) * 256), dtype=np.float32)
    for t in tiles:
        rgb = np.asarray(Image.open(os.path.join(cache_dir, "terrarium_%d_%d_%d.png" % (ZOOM, t["x"], t["y"]))).convert("RGB"), dtype=np.float32)
        elev = rgb[:, :, 0] * 256.0 + rgb[:, :, 1] + rgb[:, :, 2] / 256.0 - 32768.0
        r, c = ys.index(t["y"]), xs.index(t["x"])
        mosaic[r * 256:(r + 1) * 256, c * 256:(c + 1) * 256] = elev
    return mosaic, xs[0], ys[0], tiles


def sample(mosaic, tx0, ty0, lons, lats):
    """Bilinear elevation at cell centres (lons: 1-D, lats: 1-D)."""
    gx = (lons + 180.0) / 360.0 * 2 ** ZOOM
    gy =np.array([tile_xy(0.0, lat, ZOOM)[1] for lat in lats])
    px = (gx - tx0) * 256.0 - 0.5
    py = (gy - ty0) * 256.0 - 0.5
    X, Y = np.meshgrid(px, py)
    x0 = np.clip(np.floor(X).astype(int), 0, mosaic.shape[1] - 2)
    y0 = np.clip(np.floor(Y).astype(int), 0, mosaic.shape[0] - 2)
    fx = np.clip(X - x0, 0.0, 1.0)
    fy = np.clip(Y - y0, 0.0, 1.0)
    a = mosaic[y0, x0] * (1 - fx) + mosaic[y0, x0 + 1] * fx
    b = mosaic[y0 + 1, x0] * (1 - fx) + mosaic[y0 + 1, x0 + 1] * fx
    return a * (1 - fy) + b * fy


def ring_masks(rings, bbox, width, height):
    """Even-odd land mask (as world_map_data.is_on_land) and a lake mask (inside any hole ring)."""
    west, _, _, north = bbox
    land = np.zeros((height, width), dtype=bool)
    lake = np.zeros((height, width), dtype=bool)
    for ring in rings:
        flat = ring["points"]
        pts = [((flat[i] - west) / LON_STEP, (north - flat[i + 1]) / LAT_STEP) for i in range(0, len(flat), 2)]
        if len(pts) < 3:
            continue
        img = Image.new("1", (width, height), 0)
        ImageDraw.Draw(img).polygon(pts, fill=1)
        m = np.asarray(img, dtype=bool)
        land ^= m
        if ring["hole"]:
            lake |= m
    return land & ~lake, lake


def hillshade(elev, lat_centres):
    dy = LAT_STEP * 111320.0
    dx = LON_STEP * 111320.0 * np.cos(np.radians(lat_centres))[:, None]
    gy, gx = np.gradient(elev * Z_FACTOR)
    # Row index grows southward: north-facing gradient is -gy.
    dzdx = gx / dx
    dzdy = -gy / dy
    slope = np.arctan(np.hypot(dzdx, dzdy))
    aspect = np.arctan2(dzdy, -dzdx)
    az = math.radians(90.0 - SUN_AZIMUTH_DEG)
    alt = math.radians(SUN_ALTITUDE_DEG)
    shade = math.sin(alt) * np.cos(slope) + math.cos(alt) * np.sin(slope) * np.cos(az - aspect)
    return shade - math.sin(alt)


def smooth(values, cells):
    """Box mean over cells x cells (edge-padded)."""
    r = cells // 2
    p = np.pad(values, r, mode="edge")
    out = np.zeros_like(values)
    for dy in range(cells):
        for dx in range(cells):
            out += p[dy:dy + values.shape[0], dx:dx + values.shape[1]]
    return out / (cells * cells)


def keep_clusters(mask):
    """Drop shade pixels with fewer than three same-class 8-neighbours (no lone specks)."""
    p = np.pad(mask, 1).astype(np.int8)
    n = sum(p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
    return mask & (n >= 3)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", required=True)
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args()
    os.makedirs(args.cache_dir, exist_ok=True)
    with open(GEODATA, encoding="utf-8") as f:
        geodata = json.load(f)
    layer = geodata["layers"]["regions"]["us_east"]
    bbox = layer["clip_bbox_wsen"]
    west, south, east, north = bbox
    width = int(round((east - west) / LON_STEP))
    height = int(round((north - south) / LAT_STEP))
    lons = west + (np.arange(width) + 0.5) * LON_STEP
    lats = north - (np.arange(height) + 0.5) * LAT_STEP

    mosaic, tx0, ty0, tiles = fetch_tiles(bbox, args.cache_dir)
    elev = sample(mosaic, tx0, ty0, lons, lats)
    land, lake = ring_masks(layer["land"]["rings"], bbox, width, height)
    sea = ~land & ~lake

    shade = hillshade(smooth(np.where(land, np.maximum(elev, 0.0), 0.0), SMOOTH_CELLS), lats)
    shadow = keep_clusters(land & (shade < -SHADE_THRESHOLD))
    lit = keep_clusters(land & (shade > SHADE_THRESHOLD) & ~shadow)
    band = np.digitize(elev, BAND_LIMITS_M)

    index = np.zeros((height, width), dtype=np.uint8)
    for b in range(len(BAND_LIMITS_M) + 1):
        on = land & (band == b)
        if b > 0:
            index[on] = 3 * b
        index[on & shadow] = 3 * b + 1
        index[on & lit] = 3 * b + 2
    shelf = 3 * (len(BAND_LIMITS_M) + 1)
    index[sea & (elev > SHELF_LIMITS_M[1])] = shelf + 1
    index[sea & (elev > SHELF_LIMITS_M[0])] = shelf

    image = Image.fromarray(index, mode="P")
    flat_palette = []
    for _, hexcolor in PALETTE:
        h = (hexcolor or "#000000").lstrip("#")
        flat_palette += [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    image.putpalette(flat_palette)
    image.info["transparency"] = 0
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True, transparency=0)
    png = buffer.getvalue()

    counts = {PALETTE[i][0]: int((index == i).sum()) for i in range(len(PALETTE))}
    out = {
        "schema": "worlds-between.world-map.relief-layer.v1",
        "status": "unapproved_map_art_candidate",
        "tag": TAG,
        "generated_by": os.path.relpath(os.path.abspath(__file__), REPO).replace("\\", "/"),
        "geodata_key": "us_east",
        "bbox_wsen": bbox,
        "grid": {"width": width, "height": height, "lon_step": LON_STEP, "lat_step": LAT_STEP, "cell": "lon/lat (plate carree), row 0 = north"},
        "mask": "Natural Earth land and lake rings of the map's own us_east geodata (even-odd, holes are lakes)",
        "classes": {
            "elevation_bands_m": BAND_LIMITS_M,
            "sea_shelf_limits_m": SHELF_LIMITS_M,
            "hillshade": {"azimuth_deg": SUN_AZIMUTH_DEG, "altitude_deg": SUN_ALTITUDE_DEG, "z_factor": Z_FACTOR, "threshold": SHADE_THRESHOLD, "smooth_cells": SMOOTH_CELLS,
                "cleanup": "shade pixels need >= 3 same-class 8-neighbours"},
        },
        "palette": [{"index": i, "role": role, "color": color} for i, (role, color) in enumerate(PALETTE)],
        "land_low_color": LAND_LOW,
        "class_counts": counts,
        "sources": [{
            "id": "tilezen_terrarium_z7",
            "url_template": TILE_URL,
            "attribution": "https://github.com/tilezen/joerd/blob/master/docs/attribution.md (SRTM, USGS NED/3DEP, GMTED2010, ETOPO1)",
            "retrieved_on": "2026-10-17",
            "tiles": tiles,
        }, {"id": "natural_earth_us_east_rings", "path": os.path.relpath(GEODATA, REPO).replace("\\", "/")}],
        "png_sha256": hashlib.sha256(png).hexdigest(),
        "png_base64": base64.b64encode(png).decode("ascii"),
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print("RELIEF_BAKE_OK %dx%d png=%d bytes json=%d bytes" % (width, height, len(png), os.path.getsize(args.out)))
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
