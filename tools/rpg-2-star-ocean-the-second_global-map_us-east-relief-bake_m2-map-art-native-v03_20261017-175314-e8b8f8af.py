"""Bake the v03 relief layers for the native global map (UNAPPROVED map-art candidate, 2026-10-17).

v03 is the legibility pass over v02 (dacc5102). The geometry of the two regional layers is unchanged (one cell is
exactly one screen pixel at each view's default zoom); what changes:
  - values: land lifted, lakes darker and bluer, brighter lake and sea shore rims, so land / lake / sea separate at
    640x360 (v02 measured land - lake 0.127 luma on the Great Lakes card);
  - route_inset is re-fitted to the compact route strip that now sits inside the route card (192 x 58 map area,
    margins 1.5 deg lon / 1.4 deg lat) instead of v02's 194 x 79 map inset left of the card.
  us_northeast   - the Northeast view (frame_px fit of its three places), standard parallel 40;
  us_great_lakes - the Great Lakes view (cover fit of its pan box), standard parallel 42;
  route_inset    - the NYC <-> Chicago route strip on the card (its own fit), area-averaged from the same tiles.
Every class comes from real data; nothing is invented:
  land  = hypsometric band (real elevation, ordered-dither transitions) x hillshade (NW light, 2 levels each way);
  sea   = shelf depth from real bathymetry (> -20 m, > -60 m, > -200 m; deeper stays transparent = COLOR_OCEAN)
          plus a shore band measured from the map's own Natural Earth coastline;
  lakes = a shore band from the same lake rings (no lake bathymetry is claimed);
  coast = one transparent cell on each side of every coast and lake shore, so the map's own polygons and coast
          line decide the exact edge and the texture never paints across it.

Elevation source: Tilezen / Mapzen "Terrarium" terrain tiles (AWS open data, zoom 7), the same 77 tiles v01 pinned.
v03 bakes offline: every cached tile must match the sha256 the v02 bake recorded, and the observed source families
are taken from the v02 JSON's per-tile `x-amz-meta-x-imagery-sources` records (SRTM, GMTED2010 and ETOPO1 only; the
bake fails on any other family). No network request is made, so a rerun is byte-identical.
Attribution guidance: https://github.com/tilezen/joerd/blob/master/docs/attribution.md

Usage (repo root; the real Python path is in the repo memory):
  python -I tools/<this file> --cache-dir <dir holding the 77 z7 tiles> [--out <json>] [--preview-dir <dir>]
"""
import argparse
import base64
import hashlib
import io
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw

TAG = "m2-map-art-native-v03_20261017-175314-e8b8f8af"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORLD_MAP = os.path.join(REPO, "game", "data", "world-map")
GEODATA = os.path.join(WORLD_MAP, "rpg-2-star-ocean-the-second_earth-map_runtime-geodata_m2-us-science-v02_20261015-175011-944d9635.json")
REGISTRY = os.path.join(WORLD_MAP, "rpg-2-star-ocean-the-second_earth-map_place-registry_m2-us-science-v02_20261015-175011-eeaa6baa.json")
TRAVEL = os.path.join(REPO, "game", "data", "world-travel",
    "rpg-2-star-ocean-the-second_global-earth-travel_locations-routes_m2-us-science-v02_20261015-175011-c454007b.json")
V02_RELIEF = os.path.join(WORLD_MAP, "rpg-2-star-ocean-the-second_earth-map_us-east-relief-layer_m2-map-art-native-v02_20261017-165006-dacc5102.json")
DEFAULT_OUT = os.path.join(WORLD_MAP, "rpg-2-star-ocean-the-second_earth-map_us-east-relief-layer_" + TAG + ".json")
TILE_URL = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
ZOOM = 7
ALLOWED_SOURCE_FAMILIES = {"srtm", "gmted", "etopo1"}

# Must match game/scripts/scifi_world_map.gd: MAP_RECT size, REGION_FRAME, REGION_ZOOM_RANGE, the route strip's map
# area (RouteInset STRIP_SIZE minus its 1 px border) and its frame margins (RouteInset MARGIN_DEG).
VIEWPORT = (640.0, 268.0)
REGION_FRAME = (150.0, 44.0, 230.0, 116.0)
REGION_ZOOM_RANGE = 6.0
INSET_AREA = (192.0, 58.0)
INSET_MARGIN_DEG = (1.5, 1.4)
INSET_PAIR = ("earth.us.ny.new-york-city", "earth.us.il.chicago")

BAND_LIMITS_M = [100.0, 200.0, 300.0, 450.0, 700.0, 1000.0]
# Fraction of a band's width on each side of a limit where the two bands dither (2x2 ordered pattern).
DITHER_MARGIN = 0.22
SHELF_LIMITS_M = [-20.0, -60.0, -200.0]
SUN_AZIMUTH_DEG = 315.0
SUN_ALTITUDE_DEG = 40.0

# v03 values (v02 in brackets): every land band lifted by about 0.045 luma [#627856 ...], so land sits clearly
# above the darker, bluer lakes; the step between bands and the hillshade inks are as in v02.
LAND_BASE = ["#6d855c", "#73895e", "#7a8d60", "#828f62", "#8b9165", "#959469", "#a09a70"]
SHADOW_INK = "#25342f"
LIGHT_INK = "#d3cf9c"
# Per hillshade level: (role suffix, ink, amount). Order matters: index = 1 + band * 5 + level.
SHADE_LEVELS = [("", None, 0.0), ("shadow", SHADOW_INK, 0.20), ("deep_shadow", SHADOW_INK, 0.36),
    ("lit", LIGHT_INK, 0.16), ("high_lit", LIGHT_INK, 0.30)]
# Shelf steps as v02; the shore rims are brighter and bluer [sea_shore #255868, lake_shore #35717f], so every
# shoreline reads as a lit edge of the water rather than as a value close to the land.
WATER = [
    ("sea_shelf_outer", "#133646"),
    ("sea_shelf_inner", "#183f4f"),
    ("sea_shallow", "#1e4858"),
    ("sea_shore", "#286479"),
    ("lake_shore", "#2f7290"),
]
# The map's flat polygon colours (scifi_world_map.gd COLOR_LAND / COLOR_OCEAN / COLOR_LAKE); used for previews only,
# and land_low_color must equal COLOR_LAND (the transparent coast band shows it).
LAND_LOW = LAND_BASE[0]
OCEAN = "#0f2b38"
LAKE = "#225873"

# Per layer: hillshade vertical exaggeration, shade thresholds (level 1, level 2), smoothing and supersampling.
LAYER_STYLE = {
    "us_northeast": {"z": 5.0, "t1": 0.07, "t2": 0.17, "smooth": 3, "ss": 2},
    "us_great_lakes": {"z": 9.0, "t1": 0.05, "t2": 0.13, "smooth": 3, "ss": 2},
    "route_inset": {"z": 14.0, "t1": 0.06, "t2": 0.16, "smooth": 1, "ss": 6},
}


def mix(a, b, t):
    pa = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    pb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join("%02x" % int(round(pa[i] + (pb[i] - pa[i]) * t)) for i in range(3))


def build_palette():
    palette = [("none", None)]
    for b, base in enumerate(LAND_BASE):
        for suffix, ink, amount in SHADE_LEVELS:
            palette.append(("land_b%d%s" % (b, "_" + suffix if suffix else ""), base if ink is None else mix(base, ink, amount)))
    palette += WATER
    return palette


PALETTE = build_palette()
INDEX = {role: i for i, (role, _) in enumerate(PALETTE)}


def tile_xy(lon, lat, z):
    n = 2 ** z
    x = (lon + 180.0) / 360.0 * n
    r = math.radians(lat)
    y = (1.0 - math.log(math.tan(r) + 1.0 / math.cos(r)) / math.pi) / 2.0 * n
    return x, y


def source_families(header):
    families = set()
    for item in (header or "").split(","):
        item = item.strip()
        if item:
            families.add(item.split("/")[0].lower())
    return sorted(families)


def load_tiles(bbox, cache_dir, recorded):
    """Offline: every cached tile must exist and match the sha256 the v02 bake recorded, whose observed source
    header families must stay within ALLOWED_SOURCE_FAMILIES."""
    west, south, east, north = bbox
    x0, y0 = tile_xy(west, north, ZOOM)
    x1, y1 = tile_xy(east, south, ZOOM)
    tiles = []
    for ty in range(int(y0), int(y1) + 1):
        for tx in range(int(x0), int(x1) + 1):
            key = (ZOOM, tx, ty)
            path = os.path.join(cache_dir, "terrarium_%d_%d_%d.png" % key)
            if key not in recorded:
                raise SystemExit("tile %s has no v02 record" % (key,))
            if not os.path.exists(path):
                raise SystemExit("tile %s missing from the cache %s (fetch it with the v02 bake)" % (key, cache_dir))
            with open(path, "rb") as f:
                digest = hashlib.sha256(f.read()).hexdigest()
            record = recorded[key]
            if record["sha256"] != digest or not record.get("v01_pin_match"):
                raise SystemExit("tile %s differs from the v02 / v01 sha256 pin" % (key,))
            families = list(record["imagery_source_families"])
            if not families or not set(families) <= ALLOWED_SOURCE_FAMILIES:
                raise SystemExit("tile %s lists source families %s, outside %s" % (key, families, sorted(ALLOWED_SOURCE_FAMILIES)))
            tiles.append({"z": ZOOM, "x": tx, "y": ty, "sha256": digest, "v01_pin_match": True, "v02_record_match": True,
                "imagery_source_families": families, "imagery_source_files": record["imagery_source_files"]})
    if len(tiles) != len(recorded):
        raise SystemExit("tile count %d differs from the v02 record (%d)" % (len(tiles), len(recorded)))
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
    """Bilinear elevation at the given cell centres (lons: 1-D, lats: 1-D)."""
    gx = (lons + 180.0) / 360.0 * 2 ** ZOOM
    gy = np.array([tile_xy(0.0, lat, ZOOM)[1] for lat in lats])
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


def sample_area(mosaic, tx0, ty0, bbox, width, height, ss):
    """Mean elevation per cell from ss x ss bilinear samples (area average, so small cells do not alias)."""
    west, _, _, north = bbox
    lon_step = (bbox[2] - west) / width
    lat_step = (north - bbox[1]) / height
    lons = west + (np.arange(width * ss) + 0.5) * lon_step / ss
    lats = north - (np.arange(height * ss) + 0.5) * lat_step / ss
    fine = sample(mosaic, tx0, ty0, lons, lats)
    return fine.reshape(height, ss, width, ss).mean(axis=(1, 3))


def ring_masks(rings, bbox, width, height):
    """Even-odd land mask (as world_map_data.is_on_land) and a lake mask (inside any hole ring), cell-centre rule."""
    west, south, east, north = bbox
    sx = width / (east - west)
    sy = height / (north - south)
    land = np.zeros((height, width), dtype=bool)
    lake = np.zeros((height, width), dtype=bool)
    for ring in rings:
        flat = ring["points"]
        # PIL fills pixel (i, j) when its centre (i + 0.5, j + 0.5) is inside; shift so cell centres match.
        pts = [((flat[i] - west) * sx - 0.5, (north - flat[i + 1]) * sy - 0.5) for i in range(0, len(flat), 2)]
        if len(pts) < 3:
            continue
        img = Image.new("1", (width, height), 0)
        ImageDraw.Draw(img).polygon(pts, fill=1)
        m = np.asarray(img, dtype=bool)
        land ^= m
        if ring["hole"]:
            lake |= m
    return land & ~lake, lake


def neighbours_differ(classes):
    """True where any 8-neighbour has another class (cells along a coast or lake shore)."""
    p = np.pad(classes, 1, mode="edge")
    h, w = classes.shape
    out = np.zeros((h, w), dtype=bool)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy or dx:
                out |= p[1 + dy:1 + dy + h, 1 + dx:1 + dx + w] != classes
    return out


def grow(mask, steps):
    out = mask.copy()
    for _ in range(steps):
        p = np.pad(out, 1)
        h, w = out.shape
        out = out | p[0:h, 1:w + 1] | p[2:h + 2, 1:w + 1] | p[1:h + 1, 0:w] | p[1:h + 1, 2:w + 2]
    return out


def smooth(values, cells):
    if cells <= 1:
        return values
    r = cells // 2
    p = np.pad(values, r, mode="edge")
    out = np.zeros_like(values)
    for dy in range(cells):
        for dx in range(cells):
            out += p[dy:dy + values.shape[0], dx:dx + values.shape[1]]
    return out / (cells * cells)


def hillshade(elev, bbox, width, height, z):
    lon_step = (bbox[2] - bbox[0]) / width
    lat_step = (bbox[3] - bbox[1]) / height
    lats = bbox[3] - (np.arange(height) + 0.5) * lat_step
    dy = lat_step * 111320.0
    dx = lon_step * 111320.0 * np.cos(np.radians(lats))[:, None]
    gy, gx = np.gradient(elev * z)
    dzdx = gx / dx
    dzdy = -gy / dy
    slope = np.arctan(np.hypot(dzdx, dzdy))
    aspect = np.arctan2(dzdy, -dzdx)
    az = math.radians(90.0 - SUN_AZIMUTH_DEG)
    alt = math.radians(SUN_ALTITUDE_DEG)
    shade = math.sin(alt) * np.cos(slope) + math.cos(alt) * np.sin(slope) * np.cos(az - aspect)
    return shade - math.sin(alt)


def keep_clusters(mask, need=3):
    """Drop cells with fewer than `need` same-class 8-neighbours (no lone specks)."""
    p = np.pad(mask, 1).astype(np.int8)
    n = sum(p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
    return mask & (n >= need)


def dithered_band(elev):
    """Band index per cell; within DITHER_MARGIN of a limit the 2x2 ordered pattern picks the lower or upper band."""
    band = np.digitize(elev, BAND_LIMITS_M)
    h, w = elev.shape
    bayer = np.array([[0.125, 0.625], [0.875, 0.375]])
    threshold = np.tile(bayer, (h // 2 + 1, w // 2 + 1))[:h, :w]
    limits = [0.0] + BAND_LIMITS_M + [BAND_LIMITS_M[-1] * 1.5]
    for i, limit in enumerate(BAND_LIMITS_M):
        below = limit - limits[i]
        above = limits[i + 2] - limit
        lo = limit - below * DITHER_MARGIN
        hi = limit + above * DITHER_MARGIN
        zone = (elev >= lo) & (elev < hi)
        t = np.clip((elev - lo) / (hi - lo), 0.0, 1.0)
        band = np.where(zone, np.where(t > threshold, i + 1, i), band)
    return band


def layer_grid(bbox_hint, x_factor, scale, cells_px=1.0):
    """Grid where one cell is `cells_px` screen pixels at `scale` (px per projected unit = per degree of latitude)."""
    lon_step = cells_px / (scale * x_factor)
    lat_step = cells_px / scale
    west, south, east, north = bbox_hint
    width = int(math.ceil((east - west) / lon_step))
    height = int(math.ceil((north - south) / lat_step))
    return [west, north - height * lat_step, west + width * lon_step, north], width, height, lon_step, lat_step


def fit_scale(box_wsen, x_factor, target, pan_wsen):
    """Replicates world_geo_projection.gd configure(cover) + frame_geo_box for one view."""
    min_scale = max(VIEWPORT[0] / ((pan_wsen[2] - pan_wsen[0]) * x_factor), VIEWPORT[1] / (pan_wsen[3] - pan_wsen[1]))
    fit = min(target[2] / max((box_wsen[2] - box_wsen[0]) * x_factor, 1e-4), target[3] / max(box_wsen[3] - box_wsen[1], 1e-4))
    return min(max(fit, min_scale), min_scale * REGION_ZOOM_RANGE)


def view_specs(registry, travel, clip):
    coords = {l["id"]: (l["coordinates"]["lon"], l["coordinates"]["lat"]) for l in travel["locations"]}
    specs = {}
    for region in registry["geo_regions"]:
        xf = math.cos(math.radians(region["standard_parallel"]))
        box = region.get("frame_bbox_wsen")
        if not box:
            pts = [coords[p["id"]] for p in registry["places"] if p["geo_region_id"] == region["id"] and p["id"] in coords]
            box = [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)]
        target = region.get("frame_px") or REGION_FRAME
        scale = fit_scale(box, xf, target, region["pan_bbox_wsen"])
        pan = region["pan_bbox_wsen"]
        hint = [pan[0] - 0.05, pan[1] - 0.05, pan[2] + 0.05, pan[3] + 0.05]
        specs[region["id"]] = {"scale": scale, "x_factor": xf, "standard_parallel": region["standard_parallel"], "bbox_hint": hint}
    a, b = coords[INSET_PAIR[0]], coords[INSET_PAIR[1]]
    mid_lat = (a[1] + b[1]) * 0.5
    xf = math.cos(math.radians(mid_lat))
    box = [min(a[0], b[0]) - INSET_MARGIN_DEG[0], min(a[1], b[1]) - INSET_MARGIN_DEG[1],
        max(a[0], b[0]) + INSET_MARGIN_DEG[0], max(a[1], b[1]) + INSET_MARGIN_DEG[1]]
    min_scale = max(INSET_AREA[0] / ((clip[2] - clip[0]) * xf), INSET_AREA[1] / (clip[3] - clip[1]))
    fit = min(INSET_AREA[0] / ((box[2] - box[0]) * xf), INSET_AREA[1] / (box[3] - box[1]))
    specs["route_inset"] = {"scale": min(max(fit, min_scale), min_scale * 60.0), "x_factor": xf, "standard_parallel": mid_lat,
        "bbox_hint": list(clip), "pair": list(INSET_PAIR)}
    return specs


def bake_layer(name, spec, mosaic, tx0, ty0, rings):
    style = LAYER_STYLE[name]
    bbox, width, height, lon_step, lat_step = layer_grid(spec["bbox_hint"], spec["x_factor"], spec["scale"])
    elev = sample_area(mosaic, tx0, ty0, bbox, width, height, style["ss"])
    land, lake = ring_masks(rings, bbox, width, height)
    sea = ~land & ~lake
    classes = np.where(land, 1, np.where(lake, 2, 0)).astype(np.int8)
    edge = neighbours_differ(classes)

    shade = hillshade(smooth(np.where(land, np.maximum(elev, 0.0), 0.0), style["smooth"]), bbox, width, height, style["z"])
    deep = keep_clusters(land & (shade < -style["t2"]))
    shadow = keep_clusters(land & (shade < -style["t1"])) & ~deep
    high = keep_clusters(land & (shade > style["t2"]))
    lit = keep_clusters(land & (shade > style["t1"])) & ~high & ~shadow & ~deep
    band = dithered_band(np.maximum(elev, 0.0))

    index = np.zeros((height, width), dtype=np.uint8)
    for b in range(len(LAND_BASE)):
        on = land & (band == b)
        index[on] = INDEX["land_b%d" % b]
        index[on & shadow] = INDEX["land_b%d_shadow" % b]
        index[on & deep] = INDEX["land_b%d_deep_shadow" % b]
        index[on & lit] = INDEX["land_b%d_lit" % b]
        index[on & high] = INDEX["land_b%d_high_lit" % b]
    near_land = grow(land | lake, 3) & sea
    index[sea & (elev > SHELF_LIMITS_M[2])] = INDEX["sea_shelf_outer"]
    index[sea & (elev > SHELF_LIMITS_M[1])] = INDEX["sea_shelf_inner"]
    index[sea & (elev > SHELF_LIMITS_M[0])] = INDEX["sea_shallow"]
    index[near_land] = INDEX["sea_shore"]
    index[lake & grow(land, 3)] = INDEX["lake_shore"]
    # One transparent cell each side of every coast and lake shore: the polygons and the coast line own the edge.
    index[edge] = 0

    image = Image.fromarray(index, mode="P")
    flat_palette = []
    for _, hexcolor in PALETTE:
        h = (hexcolor or "#000000").lstrip("#")
        flat_palette += [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    image.putpalette(flat_palette)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True, transparency=0)
    png = buffer.getvalue()
    counts = {PALETTE[i][0]: int((index == i).sum()) for i in range(len(PALETTE)) if int((index == i).sum())}
    layer = {
        "bbox_wsen": bbox,
        "grid": {"width": width, "height": height, "lon_step": lon_step, "lat_step": lat_step, "cell": "lon/lat, row 0 = north"},
        "view": {"default_scale_px_per_unit": spec["scale"], "x_factor": spec["x_factor"], "standard_parallel": spec["standard_parallel"],
            "cell_px_at_default_zoom": [lon_step * spec["scale"] * spec["x_factor"], lat_step * spec["scale"]]},
        "style": style,
        "class_counts": counts,
        "png_sha256": hashlib.sha256(png).hexdigest(),
        "png_base64": base64.b64encode(png).decode("ascii"),
    }
    if "pair" in spec:
        layer["view"]["pair"] = spec["pair"]
    preview = {"index": index, "land": land, "lake": lake}
    return layer, preview


def write_preview(path, index, land, lake, scale=2):
    rgb = np.zeros(index.shape + (3,), dtype=np.uint8)
    flat = {"land": LAND_LOW, "lake": LAKE, "sea": OCEAN}
    for kind, mask in (("sea", ~land & ~lake), ("land", land), ("lake", lake)):
        h = flat[kind]
        rgb[mask] = [int(h[i:i + 2], 16) for i in (1, 3, 5)]
    for i, (_, hexcolor) in enumerate(PALETTE):
        if hexcolor:
            rgb[index == i] = [int(hexcolor[k:k + 2], 16) for k in (1, 3, 5)]
    img = Image.fromarray(rgb, mode="RGB").resize((index.shape[1] * scale, index.shape[0] * scale), Image.NEAREST)
    img.save(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", required=True)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--preview-dir", default="")
    args = parser.parse_args()
    with open(GEODATA, encoding="utf-8") as f:
        geodata = json.load(f)
    with open(REGISTRY, encoding="utf-8") as f:
        registry = json.load(f)
    with open(TRAVEL, encoding="utf-8") as f:
        travel = json.load(f)
    with open(V02_RELIEF, encoding="utf-8") as f:
        v02_source = json.load(f)["sources"][0]
    recorded = {(t["z"], t["x"], t["y"]): t for t in v02_source["tiles"]}
    layer = geodata["layers"]["regions"]["us_east"]
    clip = layer["clip_bbox_wsen"]
    mosaic, tx0, ty0, tiles = load_tiles(clip, args.cache_dir, recorded)
    families = sorted({f for t in tiles for f in t["imagery_source_families"]})

    layers = {}
    for name, spec in view_specs(registry, travel, clip).items():
        layers[name], preview = bake_layer(name, spec, mosaic, tx0, ty0, layer["land"]["rings"])
        if args.preview_dir:
            os.makedirs(args.preview_dir, exist_ok=True)
            write_preview(os.path.join(args.preview_dir, "relief-v03-preview-%s.png" % name), preview["index"], preview["land"], preview["lake"],
                1 if name != "route_inset" else 3)
        print("LAYER %s %dx%d cell_px=%s png=%d bytes" % (name, layers[name]["grid"]["width"], layers[name]["grid"]["height"],
            [round(v, 4) for v in layers[name]["view"]["cell_px_at_default_zoom"]], len(base64.b64decode(layers[name]["png_base64"]))))

    out = {
        "schema": "worlds-between.world-map.relief-layer.v2",
        "status": "unapproved_map_art_candidate",
        "tag": TAG,
        "supersedes": os.path.relpath(V02_RELIEF, REPO).replace("\\", "/"),
        "changes_from_supersedes": [
            "palette: land bands lifted, lake flat and shore rims re-valued (see palette); band, shelf and hillshade classes unchanged",
            "route_inset re-fitted to the route strip on the card: map area %dx%d px, margins %s deg" % (INSET_AREA[0], INSET_AREA[1], list(INSET_MARGIN_DEG)),
            "offline: tile sha256 and observed source families taken from the superseded bake's records (no network request)",
        ],
        "generated_by": os.path.relpath(os.path.abspath(__file__), REPO).replace("\\", "/"),
        "geodata_key": "us_east",
        "mask": "Natural Earth land and lake rings of the map's own us_east geodata (even-odd, holes are lakes), cell-centre rule",
        "classes": {
            "elevation_bands_m": BAND_LIMITS_M,
            "band_dither": {"pattern": "2x2 ordered", "margin_fraction": DITHER_MARGIN},
            "sea_shelf_limits_m": SHELF_LIMITS_M,
            "shore_band_cells": 3,
            "coast_band": "one transparent cell on each side of every coast and lake shore",
            "hillshade": {"azimuth_deg": SUN_AZIMUTH_DEG, "altitude_deg": SUN_ALTITUDE_DEG, "levels": [s[0] or "flat" for s in SHADE_LEVELS],
                "cleanup": "shade cells need >= 3 same-class 8-neighbours"},
            "no_lake_bathymetry": "lake shading is a shore band from the lake rings only",
        },
        "palette": [{"index": i, "role": role, "color": color} for i, (role, color) in enumerate(PALETTE)],
        "land_low_color": LAND_LOW,
        "map_flat_colors": {"land": LAND_LOW, "ocean": OCEAN, "lake": LAKE},
        "layers": layers,
        "sources": [{
            "id": "tilezen_terrarium_z7",
            "url_template": TILE_URL,
            "observed_imagery_source_families": families,
            "observed_how": "x-amz-meta-x-imagery-sources response header of every tile, read by the v02 bake (2026-10-17) and re-checked here against its per-tile records",
            "attribution_guidance": "https://github.com/tilezen/joerd/blob/master/docs/attribution.md",
            "attribution_lines": [
                "Mapzen",
                "Global ETOPO1 terrain data U.S. National Oceanic and Atmospheric Administration",
                "Global GMTED2010 and SRTM terrain data courtesy of the U.S. Geological Survey.",
            ],
            "attribution_note": "Tilezen's example USGS line also names United States 3DEP (formerly NED); no tile used here lists a 3DEP/NED (or CDEM) file, so that clause is omitted.",
            "retrieved_on": "2026-10-17",
            "tiles": tiles,
        }, {"id": "natural_earth_us_east_rings", "path": os.path.relpath(GEODATA, REPO).replace("\\", "/")},
            {"id": "view_parameters", "paths": [os.path.relpath(REGISTRY, REPO).replace("\\", "/"), os.path.relpath(TRAVEL, REPO).replace("\\", "/")]}],
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print("RELIEF_BAKE_OK layers=%d families=%s json=%d bytes" % (len(layers), families, os.path.getsize(args.out)))


if __name__ == "__main__":
    main()
