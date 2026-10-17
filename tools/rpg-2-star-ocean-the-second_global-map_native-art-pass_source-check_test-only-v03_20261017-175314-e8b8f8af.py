"""Deterministic native-art / source check for the global map legibility pass v03 (TEST-ONLY, UNAPPROVED, 2026-10-17).

Checks, without Godot:
  1. the v03 relief JSON: schema, supersedes v02, palette roles as v02, flat colours equal to scifi_world_map.gd's
     COLOR_LAND / COLOR_LAKE / COLOR_OCEAN, every layer PNG decodes to its recorded sha256, size and palette;
  2. the regional layers keep v02's exact grids; the route-strip layer matches the strip constants in the map script
     (RouteInset map area = INSET_SIZE - 2, MARGIN_DEG = the bake's INSET_MARGIN_DEG);
  3. relief sources: the 77 tiles keep the v01 / v02 sha256 pins, observed families only SRTM / GMTED2010 / ETOPO1, no
     3DEP / NED / CDEM claim;
  4. with --cache-dir, a rebake into a temp file is identical to the JSON on disk under sha256-text-lf-v1 (CRLF -> LF,
     so an autocrlf=true checkout passes too);
  5. source facts: the route strip is built into the card (not the map frame), MapData reads the v03 JSON, map text
     names no airport or schedule component, and the route core and travel data are unchanged from git HEAD;
  6. hashes of every v03 file (sha256-text-lf-v1 for text, sha256-bytes for PNG) and of the capture manifest's files.

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

from PIL import Image

TAG = "v03_20261017-175314-e8b8f8af"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORLD_MAP = os.path.join(REPO, "game", "data", "world-map")
V03_JSON = os.path.join(WORLD_MAP, "rpg-2-star-ocean-the-second_earth-map_us-east-relief-layer_m2-map-art-native-" + TAG + ".json")
V02_JSON = os.path.join(WORLD_MAP, "rpg-2-star-ocean-the-second_earth-map_us-east-relief-layer_m2-map-art-native-v02_20261017-165006-dacc5102.json")
BAKE = os.path.join(REPO, "tools", "rpg-2-star-ocean-the-second_global-map_us-east-relief-bake_m2-map-art-native-" + TAG + ".py")
CAPTURE_TOOL = os.path.join(REPO, "tools", "rpg-2-star-ocean-the-second_global-map_native-art-pass_capture-check_test-only-" + TAG + ".gd")
MAP_SCRIPT = os.path.join(REPO, "game", "scripts", "scifi_world_map.gd")
MAP_DATA = os.path.join(REPO, "game", "scripts", "world_map_data.gd")
MAP_TEXT = os.path.join(REPO, "game", "scripts", "world_map_text.gd")
OUTPUTS = os.path.join(REPO, "outputs")
MANIFEST = os.path.join(OUTPUTS, "rpg-2-star-ocean-the-second_global-map_native-art_capture-manifest_test-only-" + TAG + ".json")
DEFAULT_OUT = os.path.join(OUTPUTS, "rpg-2-star-ocean-the-second_global-map_native-art_source-check_test-only-" + TAG + ".json")
ALLOWED = {"srtm", "gmted", "etopo1"}
# Route core and travel data: v03 is map art only, so these must equal git HEAD.
TRAVEL_CORE = ["game/data/world-travel", "game/scripts/app_state.gd", "game/scripts/travel_calendar.gd",
    "game/scripts/world_route_registry.gd", "game/scripts/world_map_route_adapter.gd"]
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


def py_const(source, name):
    m = re.search(r"^%s = \(([-0-9.]+), ([-0-9.]+)\)" % name, source, re.M)
    return (float(m.group(1)), float(m.group(2))) if m else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", default="")
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args()
    with open(V03_JSON, encoding="utf-8") as f:
        v03 = json.load(f)
    with open(V02_JSON, encoding="utf-8") as f:
        v02 = json.load(f)
    with open(MAP_SCRIPT, encoding="utf-8") as f:
        gd = f.read()
    with open(BAKE, encoding="utf-8") as f:
        bake = f.read()
    facts = {}

    # 1. JSON, palette and flat colours.
    check(v03["schema"] == "worlds-between.world-map.relief-layer.v2" and v03["status"] == "unapproved_map_art_candidate", "v03 relief JSON: schema v2, unapproved candidate")
    check(v03["supersedes"].endswith(os.path.basename(V02_JSON)), "v03 relief JSON supersedes the v02 layer")
    roles03 = [p["role"] for p in v03["palette"]]
    roles02 = [p["role"] for p in v02["palette"]]
    check(roles03 == roles02, "palette keeps v02's %d roles in the same order" % len(roles02))
    changed = [p["role"] for p, q in zip(v03["palette"], v02["palette"]) if p["color"] != q["color"]]
    facts["palette_roles_changed_from_v02"] = changed
    check(len(changed) > 0 and all(r.startswith("land_") or r in ("sea_shore", "lake_shore") for r in changed),
        "%d roles re-valued, all land bands or shore rims (shelf depth steps unchanged)" % len(changed))
    flat = v03["map_flat_colors"]
    for key, const in (("land", "COLOR_LAND"), ("lake", "COLOR_LAKE"), ("ocean", "COLOR_OCEAN")):
        check(flat[key].lower() == gd_color(gd, const), "flat %s %s equals scifi_world_map.gd %s %s" % (key, flat[key], const, gd_color(gd, const)))
    check(v03["land_low_color"].lower() == gd_color(gd, "COLOR_LAND"), "land_low_color equals COLOR_LAND")
    for layer_id, layer in v03["layers"].items():
        png = base64.b64decode(layer["png_base64"])
        check(hashlib.sha256(png).hexdigest() == layer["png_sha256"], "%s PNG matches its recorded sha256 %s" % (layer_id, layer["png_sha256"][:16]))
        image = Image.open(io.BytesIO(png))
        check(image.mode == "P" and image.size == (layer["grid"]["width"], layer["grid"]["height"]), "%s PNG is a %dx%d palette image" % (layer_id, image.size[0], image.size[1]))
        used = image.getextrema()[1]
        check(used < len(v03["palette"]), "%s PNG uses only palette indices 0..%d" % (layer_id, len(v03["palette"]) - 1))
        cell = layer["view"]["cell_px_at_default_zoom"]
        check(abs(cell[0] - 1.0) < 1e-6 and abs(cell[1] - 1.0) < 1e-6, "%s: one cell is one screen pixel at its default zoom %s" % (layer_id, cell))
        facts["layer " + layer_id] = {"grid": [layer["grid"]["width"], layer["grid"]["height"]], "png_sha256": layer["png_sha256"]}

    # 2. Grids: regional layers as v02; route strip layer matches the map script.
    for layer_id in ("us_northeast", "us_great_lakes"):
        a, b = v03["layers"][layer_id], v02["layers"][layer_id]
        check(a["bbox_wsen"] == b["bbox_wsen"] and a["grid"] == b["grid"], "%s keeps v02's grid and lon/lat box" % layer_id)
    m = re.search(r"^const INSET_SIZE := Vector2\((\d+), (\d+)\)", gd, re.M)
    strip = (float(m.group(1)) - 2.0, float(m.group(2)) - 2.0) if m else None
    check(strip is not None and py_const(bake, "INSET_AREA") == strip, "bake INSET_AREA %s = map INSET_SIZE - 2 border %s" % (py_const(bake, "INSET_AREA"), strip))
    m = re.search(r"const MARGIN_DEG := Vector2\(([-0-9.]+), ([-0-9.]+)\)", gd)
    margin = (float(m.group(1)), float(m.group(2))) if m else None
    check(margin is not None and py_const(bake, "INSET_MARGIN_DEG") == margin, "bake INSET_MARGIN_DEG %s = RouteInset MARGIN_DEG %s" % (py_const(bake, "INSET_MARGIN_DEG"), margin))
    check(v03["layers"]["route_inset"]["view"]["pair"] == ["earth.us.ny.new-york-city", "earth.us.il.chicago"], "route strip layer is baked for the New York City <-> Chicago pair")

    # 3. Sources.
    source = v03["sources"][0]
    tiles02 = {(t["z"], t["x"], t["y"]): t for t in v02["sources"][0]["tiles"]}
    check(len(source["tiles"]) == 77 == len(tiles02), "77 z7 tiles, as v01 / v02")
    check(all(t["sha256"] == tiles02[(t["z"], t["x"], t["y"])]["sha256"] and t["v01_pin_match"] and t["v02_record_match"] for t in source["tiles"]), "every tile sha256 equals the v02 record and the v01 pin")
    families = set(source["observed_imagery_source_families"])
    check(families and families <= ALLOWED and all(set(t["imagery_source_families"]) <= ALLOWED for t in source["tiles"]), "observed source families %s only SRTM / GMTED2010 / ETOPO1" % sorted(families))
    claims = json.dumps(source["attribution_lines"]) + json.dumps(v03["classes"])
    for word in ("3DEP", "(formerly NED)", "NED/", "CDEM"):
        check(word not in claims, "attribution lines and classes do not claim '%s'" % word)

    # 4. Rebake.
    if args.cache_dir:
        with tempfile.TemporaryDirectory(prefix="wb-relief-v03-") as tmp:
            out = os.path.join(tmp, "rebake.json")
            run = subprocess.run([sys.executable, "-I", BAKE, "--cache-dir", args.cache_dir, "--out", out], capture_output=True, text=True)
            same = run.returncode == 0 and text_hash(out) == text_hash(V03_JSON)
            check(same, "rebake from the pinned tile cache is identical to the v03 JSON, sha256-text-lf-v1 (%s)" % run.stdout.strip().splitlines()[-1] if run.stdout.strip() else run.stderr[-200:])
    else:
        print("SKIP rebake (no --cache-dir)")

    # 5. Source facts.
    check("box.add_child(route_inset)" in gd and "map_frame.add_child(route_inset)" not in gd, "the route strip is built into the route card, not the map frame")
    check("_route_inset_slot" not in gd and "caption" not in gd and "inset_title" not in gd, "the strip has no map slot, caption or header (no mode / time breakdown)")
    check(re.search(r"^const PLATE_FONT := 12$", gd, re.M) and re.search(r"^const PLATE_SUB_FONT := 10$", gd, re.M), "map label plates 12 / 10 px")
    with open(MAP_DATA, encoding="utf-8") as f:
        data_src = f.read()
    check(os.path.basename(V03_JSON) in data_src and os.path.basename(V02_JSON) not in data_src.split("const RELIEF_PATH")[1].split("\n")[0], "MapData.RELIEF_PATH reads the v03 JSON")
    with open(MAP_TEXT, encoding="utf-8") as f:
        text_src = f.read()
    strings = text_src.split("const STRINGS")[1].split("\nstatic func")[0]
    found = [w for w in FORBIDDEN_TEXT if w in strings]
    check(not found, "map text names no airport, terminal or trip component (%s)" % found)
    diff = subprocess.run(["git", "-C", REPO, "diff", "--quiet", "HEAD", "--"] + TRAVEL_CORE)
    untracked = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--"] + TRAVEL_CORE, capture_output=True, text=True).stdout.strip()
    check(diff.returncode == 0 and untracked == "", "route core and travel data equal git HEAD (%s)" % ", ".join(TRAVEL_CORE))

    # 6. Hashes.
    hashes = {}
    for path in (MAP_SCRIPT, MAP_DATA, MAP_TEXT, V03_JSON, BAKE, CAPTURE_TOOL, os.path.abspath(__file__)):
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
        check(ok and len(manifest["captures"]) == 12, "capture manifest lists %d captures, each matching its file bytes" % len(manifest["captures"]))
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
