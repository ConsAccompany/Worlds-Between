"""Deterministic source check for the global map v03r2 bounded visual gate (TEST-ONLY, UNAPPROVED, 2026-10-17).

Checks, without Godot:
  1. the v03r2 relief JSON: schema, supersedes v03, palette roles as v03 with only land bands and sea shelf steps
     re-valued, flat colours equal to scifi_world_map.gd's COLOR_LAND / COLOR_LAKE / COLOR_OCEAN, every layer PNG
     decodes to its recorded sha256, size and palette;
  2. geometry unchanged: all three layers keep v03's exact grids and lon/lat boxes; the route-strip layer still
     matches the strip constants in the map script;
  3. relief sources: the same 77 tiles and sha256 pins as v03, observed families only SRTM / GMTED2010 / ETOPO1;
  4. texture: on each regional layer, land cells whose right or lower land neighbour has another class (relief
     speckle), v03 vs v03r2 (must fall);
  5. with --cache-dir, a rebake into a temp file is identical to the JSON on disk under sha256-text-lf-v1;
  6. source facts: MapData reads the v03r2 JSON; the map text, route core and travel data equal git HEAD; roads are
     not drawn in the trip line's gold;
  7. hashes of every v03r2 file (sha256-text-lf-v1 for text, sha256-bytes for PNG) and of the capture manifest's files.

Usage (repo root; the real Python path is in the repo memory):
  python -I tools/<this file> [--cache-dir <dir holding the 77 z7 tiles>] [--out <json>]
"""
import argparse
import base64
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

TAG = "v03r2_20261017-224631-9875b9e2"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORLD_MAP = os.path.join(REPO, "game", "data", "world-map")
NEW_JSON = os.path.join(WORLD_MAP, "rpg-2-star-ocean-the-second_earth-map_us-east-relief-layer_m2-map-art-native-" + TAG + ".json")
V03_JSON = os.path.join(WORLD_MAP, "rpg-2-star-ocean-the-second_earth-map_us-east-relief-layer_m2-map-art-native-v03_20261017-175314-e8b8f8af.json")
BAKE = os.path.join(REPO, "tools", "rpg-2-star-ocean-the-second_global-map_us-east-relief-bake_m2-map-art-native-" + TAG + ".py")
CAPTURE_TOOL = os.path.join(REPO, "tools", "rpg-2-star-ocean-the-second_global-map_v03r2-visual-gate_capture-check_test-only-" + TAG + ".gd")
MAP_SCRIPT = os.path.join(REPO, "game", "scripts", "scifi_world_map.gd")
MAP_DATA = os.path.join(REPO, "game", "scripts", "world_map_data.gd")
MAP_TEXT = os.path.join(REPO, "game", "scripts", "world_map_text.gd")
OUTPUTS = os.path.join(REPO, "outputs")
MANIFEST = os.path.join(OUTPUTS, "rpg-2-star-ocean-the-second_global-map_v03r2_capture-manifest_test-only-" + TAG + ".json")
DEFAULT_OUT = os.path.join(OUTPUTS, "rpg-2-star-ocean-the-second_global-map_v03r2_source-check_test-only-" + TAG + ".json")
CAPTURES = 10
ALLOWED = {"srtm", "gmted", "etopo1"}
# Route core, travel data and map text: v03r2 is map art only, so these must equal git HEAD.
UNCHANGED = ["game/data/world-travel", "game/scripts/app_state.gd", "game/scripts/travel_calendar.gd",
    "game/scripts/world_route_registry.gd", "game/scripts/world_map_route_adapter.gd", "game/scripts/world_map_text.gd"]
FORBIDDEN_TEXT = ["LGA", "ORD", "JFK", "EWR", "MDW", "LaGuardia", "O'Hare", "Midway", "airport", "Airport", "terminal",
    "check-in", "boarding", "layover", "机场", "航站", "值机", "登机", "中转", "拉瓜迪亚", "奥黑尔"]

checks = []


def check(ok, what):
    checks.append({"ok": bool(ok), "check": what})
    print(("PASS " if ok else "FAIL ") + what)


def text_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def bytes_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def gd_color(source, name):
    m = re.search(r'^const %s := Color\("(#[0-9a-fA-F]{6})"\)' % name, source, re.M)
    return m.group(1).lower() if m else None


def gd_rgba(source, name):
    m = re.search(r"^const %s := Color\(([-0-9.]+), ([-0-9.]+), ([-0-9.]+), ([-0-9.]+)\)" % name, source, re.M)
    return tuple(float(m.group(i)) for i in range(1, 5)) if m else None


def py_const(source, name):
    m = re.search(r"^%s = \(([-0-9.]+), ([-0-9.]+)\)" % name, source, re.M)
    return (float(m.group(1)), float(m.group(2))) if m else None


def layer_index(layer):
    return np.asarray(Image.open(io.BytesIO(base64.b64decode(layer["png_base64"]))))


def speckle(layer, palette):
    """Share of land cells whose right or lower neighbour is land of another palette class."""
    land_ids = np.array([p["index"] for p in palette if p["role"].startswith("land_")])
    index = layer_index(layer)
    land = np.isin(index, land_ids)
    right = land[:, :-1] & land[:, 1:] & (index[:, :-1] != index[:, 1:])
    down = land[:-1, :] & land[1:, :] & (index[:-1, :] != index[1:, :])
    edges = np.zeros_like(land)
    edges[:, :-1] |= right
    edges[:-1, :] |= down
    return float(edges.sum()) / max(1, int(land.sum()))


def saturation(r, g, b):
    hi, lo = max(r, g, b), min(r, g, b)
    return 0.0 if hi <= 0 else (hi - lo) / hi


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", default="")
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args()
    with open(NEW_JSON, encoding="utf-8") as f:
        new = json.load(f)
    with open(V03_JSON, encoding="utf-8") as f:
        v03 = json.load(f)
    with open(MAP_SCRIPT, encoding="utf-8") as f:
        gd = f.read()
    with open(BAKE, encoding="utf-8") as f:
        bake = f.read()
    facts = {}

    # 1. JSON, palette and flat colours.
    check(new["schema"] == "worlds-between.world-map.relief-layer.v2" and new["status"] == "unapproved_map_art_candidate", "v03r2 relief JSON: schema v2, unapproved candidate")
    check(new["supersedes"].endswith(os.path.basename(V03_JSON)), "v03r2 relief JSON supersedes the v03 layer")
    roles_new = [p["role"] for p in new["palette"]]
    roles_v03 = [p["role"] for p in v03["palette"]]
    check(roles_new == roles_v03, "palette keeps v03's %d roles in the same order" % len(roles_v03))
    changed = [p["role"] for p, q in zip(new["palette"], v03["palette"]) if p["color"] != q["color"]]
    facts["palette_roles_changed_from_v03"] = changed
    check(len(changed) > 0 and all(r.startswith("land_") or r.startswith("sea_shelf") or r == "sea_shallow" for r in changed),
        "%d roles re-valued, all land bands or sea shelf steps (shore rims and lake unchanged)" % len(changed))
    flat = new["map_flat_colors"]
    for key, const in (("land", "COLOR_LAND"), ("lake", "COLOR_LAKE"), ("ocean", "COLOR_OCEAN")):
        check(flat[key].lower() == gd_color(gd, const), "flat %s %s equals scifi_world_map.gd %s %s" % (key, flat[key], const, gd_color(gd, const)))
    check(new["land_low_color"].lower() == gd_color(gd, "COLOR_LAND"), "land_low_color equals COLOR_LAND")
    for layer_id, layer in new["layers"].items():
        png = base64.b64decode(layer["png_base64"])
        check(hashlib.sha256(png).hexdigest() == layer["png_sha256"], "%s PNG matches its recorded sha256 %s" % (layer_id, layer["png_sha256"][:16]))
        image = Image.open(io.BytesIO(png))
        check(image.mode == "P" and image.size == (layer["grid"]["width"], layer["grid"]["height"]), "%s PNG is a %dx%d palette image" % (layer_id, image.size[0], image.size[1]))
        used = image.getextrema()[1]
        check(used < len(new["palette"]), "%s PNG uses only palette indices 0..%d" % (layer_id, len(new["palette"]) - 1))
        cell = layer["view"]["cell_px_at_default_zoom"]
        check(abs(cell[0] - 1.0) < 1e-6 and abs(cell[1] - 1.0) < 1e-6, "%s: one cell is one screen pixel at its default zoom %s" % (layer_id, cell))
        facts["layer " + layer_id] = {"grid": [layer["grid"]["width"], layer["grid"]["height"]], "png_sha256": layer["png_sha256"]}

    # 2. Geometry unchanged from v03; route strip layer matches the map script.
    for layer_id in ("us_northeast", "us_great_lakes", "route_inset"):
        a, b = new["layers"][layer_id], v03["layers"][layer_id]
        check(a["bbox_wsen"] == b["bbox_wsen"] and a["grid"] == b["grid"] and a["view"] == b["view"], "%s keeps v03's grid, lon/lat box and view fit" % layer_id)
        # The land / lake / sea footprint is the same: only colours and shade classes move.
        ia, ib = layer_index(a), layer_index(b)
        kind = lambda idx, pal: np.where(np.isin(idx, [p["index"] for p in pal if p["role"].startswith("land_")]), 1, np.where(idx == 0, 0, 2))
        check(np.array_equal(kind(ia, new["palette"]), kind(ib, v03["palette"])), "%s: land / water / coast-band cells identical to v03" % layer_id)
    m = re.search(r"^const INSET_SIZE := Vector2\((\d+), (\d+)\)", gd, re.M)
    strip = (float(m.group(1)) - 2.0, float(m.group(2)) - 2.0) if m else None
    check(strip is not None and py_const(bake, "INSET_AREA") == strip, "bake INSET_AREA %s = map INSET_SIZE - 2 border %s" % (py_const(bake, "INSET_AREA"), strip))
    m = re.search(r"const MARGIN_DEG := Vector2\(([-0-9.]+), ([-0-9.]+)\)", gd)
    margin = (float(m.group(1)), float(m.group(2))) if m else None
    check(margin is not None and py_const(bake, "INSET_MARGIN_DEG") == margin, "bake INSET_MARGIN_DEG %s = RouteInset MARGIN_DEG %s" % (py_const(bake, "INSET_MARGIN_DEG"), margin))

    # 3. Sources.
    source = new["sources"][0]
    tiles_v03 = {(t["z"], t["x"], t["y"]): t for t in v03["sources"][0]["tiles"]}
    check(len(source["tiles"]) == 77 == len(tiles_v03), "77 z7 tiles, as v01 / v02 / v03")
    check(all(t["sha256"] == tiles_v03[(t["z"], t["x"], t["y"])]["sha256"] and t["v01_pin_match"] and t["v02_record_match"] for t in source["tiles"]), "every tile sha256 equals the v03 record (v01 pin, v02 record)")
    families = set(source["observed_imagery_source_families"])
    check(families and families <= ALLOWED and all(set(t["imagery_source_families"]) <= ALLOWED for t in source["tiles"]), "observed source families %s only SRTM / GMTED2010 / ETOPO1" % sorted(families))
    check(source["attribution_lines"] == v03["sources"][0]["attribution_lines"], "attribution lines unchanged from v03")

    # 4. Relief speckle on the regional layers.
    for layer_id in ("us_northeast", "us_great_lakes"):
        before = speckle(v03["layers"][layer_id], v03["palette"])
        after = speckle(new["layers"][layer_id], new["palette"])
        facts["speckle " + layer_id] = {"v03": round(before, 4), "v03r2": round(after, 4), "change": round(after / before - 1.0, 3)}
        check(after < before, "%s: relief speckle %.4f -> %.4f of land cells (class change to a land neighbour)" % (layer_id, before, after))

    # 5. Rebake.
    if args.cache_dir:
        with tempfile.TemporaryDirectory(prefix="wb-relief-v03r2-") as tmp:
            out = os.path.join(tmp, "rebake.json")
            run = subprocess.run([sys.executable, "-I", BAKE, "--cache-dir", args.cache_dir, "--out", out], capture_output=True, text=True)
            same = run.returncode == 0 and text_hash(out) == text_hash(NEW_JSON)
            check(same, "rebake from the pinned tile cache is identical to the v03r2 JSON, sha256-text-lf-v1 (%s)" % run.stdout.strip().splitlines()[-1] if run.stdout.strip() else run.stderr[-200:])
    else:
        print("SKIP rebake (no --cache-dir)")

    # 6. Source facts.
    with open(MAP_DATA, encoding="utf-8") as f:
        data_src = f.read()
    check(os.path.basename(NEW_JSON) in data_src.split("const RELIEF_PATH")[1].split("\n")[0], "MapData.RELIEF_PATH reads the v03r2 JSON")
    with open(MAP_TEXT, encoding="utf-8") as f:
        text_src = f.read()
    strings = text_src.split("const STRINGS")[1].split("\nstatic func")[0]
    found = [w for w in FORBIDDEN_TEXT if w in strings]
    check(not found, "map text names no airport, terminal or trip component (%s)" % found)
    diff = subprocess.run(["git", "-C", REPO, "diff", "--quiet", "HEAD", "--"] + UNCHANGED)
    untracked = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--"] + UNCHANGED, capture_output=True, text=True).stdout.strip()
    check(diff.returncode == 0 and untracked == "", "route core, travel data and map text equal git HEAD (%s)" % ", ".join(UNCHANGED))
    road = gd_rgba(gd, "COLOR_ROAD")
    line = gd_color(gd, "COLOR_ROUTE_LINE")
    line_rgb = [int(line[i:i + 2], 16) / 255.0 for i in (1, 3, 5)] if line else [0, 0, 0]
    check(road is not None and saturation(*road[:3]) < 0.25 < saturation(*line_rgb) and road[3] <= 0.4,
        "roads are pale stone (s %.2f, a %.2f), the trip line alone is gold (s %.2f)" % (saturation(*road[:3]) if road else -1, road[3] if road else -1, saturation(*line_rgb)))

    # 7. Hashes.
    hashes = {}
    for path in (MAP_SCRIPT, MAP_DATA, MAP_TEXT, NEW_JSON, BAKE, CAPTURE_TOOL, os.path.abspath(__file__)):
        hashes[os.path.relpath(path, REPO).replace("\\", "/")] = {"sha256-text-lf-v1": text_hash(path)}
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            manifest = json.load(f)
        ok = True
        for entry in manifest["captures"]:
            path = os.path.join(OUTPUTS, entry["file"])
            digest = bytes_hash(path) if os.path.exists(path) else ""
            ok = ok and digest == entry["sha256"]
            hashes["outputs/" + entry["file"]] = {"sha256-bytes": digest}
        check(ok and len(manifest["captures"]) == CAPTURES, "capture manifest lists %d captures, each matching its file bytes" % len(manifest["captures"]))
    else:
        check(False, "capture manifest present: " + MANIFEST)
    failures = [c["check"] for c in checks if not c["ok"]]
    report = {"tag": TAG, "status": "UNAPPROVED test-only source check; map-art gate open; no counter changed",
        "checks_total": len(checks), "failures": failures, "checks": checks, "facts": facts, "hashes": hashes}
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print("REPORT " + args.out)
    if failures:
        print("SOURCE_CHECK_FAIL %d/%d" % (len(failures), len(checks)))
        sys.exit(1)
    print("SOURCE_CHECK_OK %d checks" % len(checks))


if __name__ == "__main__":
    main()
