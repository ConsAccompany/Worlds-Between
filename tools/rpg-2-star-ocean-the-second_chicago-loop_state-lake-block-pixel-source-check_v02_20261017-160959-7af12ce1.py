"""Pixel, source and Pixelorama checks for the Chicago Loop State/Lake block candidate v02 (UNAPPROVED).

Usage: python -I <this file> --capture-stamp <stamp> [--pixelorama <exe>] [--report <json path>]
Reads the manifest written by the v02 author tool, the v02 scene script, the real Godot captures in
outputs/chicago-loop-state-lake-v02/godot-runtime and, for the actual-scale comparison, the untouched
v01 captures in outputs/chicago-loop-state-lake-v01/after. Pixelorama runs use a fresh temp APPDATA
and the real %APPDATA%/pixelorama dir is snapshotted before and after.
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
AUTHOR = ROOT / "tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-author_unapproved-v02_20261017-160959-55667f46.py"
SCENE_SCRIPT = ROOT / "game/scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v02_20261017-160959-55667f46.gd"
RUNTIME_SCENE = ROOT / "game/scenes/rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn"
CAPTURES = ROOT / "outputs/chicago-loop-state-lake-v02/godot-runtime"
V01_CAPTURES = ROOT / "outputs/chicago-loop-state-lake-v01/after"
V01_STAMP = "20261017-031308-509a5e64"
# Runtime label boxes (with outline) and the arrival hero box, excluded from render parity.
LABEL_BOXES = [(262, 155, 350, 176), (0, 261, 96, 282), (324, 114, 392, 135)]
HERO_BOX = (320 - 17, 286 - 46, 320 + 17, 286 + 6)


def load_author():
    spec = spec_from_file_location("chicago_author_v02", AUTHOR)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rgba(path_or_bytes):
    src = io.BytesIO(path_or_bytes) if isinstance(path_or_bytes, bytes) else path_or_bytes
    return np.array(Image.open(src).convert("RGBA"))


def gd_geometry():
    """Parse the runtime constants that must match the author tool."""
    text = SCENE_SCRIPT.read_text(encoding="utf-8")
    def rects(block):
        return [tuple(int(float(v)) for v in m) for m in re.findall(r"Rect2\(([-\d.]+), ([-\d.]+), ([-\d.]+), ([-\d.]+)\)", block)]
    walk = rects(re.search(r"const WALK := (Rect2\([^)]*\))", text).group(1))[0]
    blocks = rects(re.search(r"const BLOCKS := \[(.*?)\n\]", text, re.S).group(1))
    vec = lambda name: tuple(int(float(v)) for v in re.search(rf"const {name} := Vector2\(([-\d.]+), ([-\d.]+)\)", text).groups())
    pivots = [float(v) for v in re.findall(r"\.png\"\), ([\d.]+)\]", text)]
    layer_files = re.findall(r"state-lake_(ysort-[a-z-]+)_unapproved-v02", text)
    ground = re.findall(r"state-lake_(ground-far)_unapproved-v02", text)
    scalar = lambda name: float(re.search(rf"const {name} := ([\d.]+)", text).group(1))
    return {"walk": walk, "blocks": blocks, "kiosk": vec("KIOSK"), "spawn": vec("SPAWN"), "pivots": pivots,
            "layer_files": layer_files, "ground": ground, "walk_top": scalar("WALK_TOP"), "deck_bottom": scalar("DECK_BOTTOM")}


def runtime_script_chain():
    """The Loop scene's script, then each `extends "res://..."` parent in turn (opt-in selectors sit above v02)."""
    m = re.search(r'\[ext_resource type="Script" path="(res://[^"]+)"', RUNTIME_SCENE.read_text(encoding="utf-8"))
    chain, res = [], m.group(1) if m else None
    while res and res not in chain and len(chain) < 8:
        chain.append(res)
        path = ROOT / "game" / res.replace("res://", "")
        e = re.match(r'extends "(res://[^"]+)"', path.read_text(encoding="utf-8")) if path.exists() else None
        res = e.group(1) if e else None
    return chain


def repetition(rgb):
    """Share of distinct 16x16 blocks in the visible art rows (1.0 = no block repeats exactly)."""
    vis = rgb[64:320]
    blocks = {vis[y:y + 16, x:x + 16].tobytes() for y in range(0, 256, 16) for x in range(0, 640, 16)}
    return round(len(blocks) / (16 * 40), 4)


def edge_density(rgb):
    """Share of visible pixels whose right or lower neighbour has a different colour (detail density)."""
    vis = rgb[62:318].astype(int)
    dx = (vis[:, 1:] != vis[:, :-1]).any(axis=2)[:-1, :]
    dy = (vis[1:, :] != vis[:-1, :]).any(axis=2)[:, :-1]
    return round(float((dx | dy).mean()), 4)


def flat_stats(rgb):
    vis = rgb[62:318].reshape(-1, 3)
    colours, counts = np.unique(vis, axis=0, return_counts=True)
    return {"visible_colours": int(len(colours)), "largest_single_colour_share": round(float(counts.max() / counts.sum()), 4),
            "distinct_16px_block_share": repetition(rgb), "edge_density": edge_density(rgb)}


def source_checks(author, manifest):
    r = {}
    files = manifest["files"]
    r["hashes_match_manifest"] = all(sha((ROOT / v["file"]).read_bytes()) == v["sha256"] for v in files.values())
    layers = author.build_layers()
    rt = author.runtime_layers(layers)
    guide = author.walkmask()
    names = [n for n, _ in author.LAYERS]
    rnames = [n for n, _ in author.RUNTIME_LAYERS]
    runtime = {n: rgba(ROOT / files[n]["file"]) for n in rnames}
    r["runtime_layers_equal_rebuild"] = all(runtime[n].tobytes() == np.array(rt[n]).tobytes() for n in rnames)
    r["sizes_640x360"] = all(a.shape == (360, 640, 4) for a in runtime.values())
    r["ground_opaque"] = bool((runtime["ground-far"][:, :, 3] == 255).all())
    r["source_and_ysort_binary_alpha"] = all(set(np.unique(np.array(layers[n])[:, :, 3]).tolist()) <= {0, 255} for n in names)
    flat = runtime["ground-far"].copy()
    for n in rnames[1:]:
        a = runtime[n][:, :, 3:4] == 255
        flat = np.where(a, runtime[n], flat)
    r["merged_preview_equals_runtime_layers"] = rgba(ROOT / files["merged-preview"]["file"]).tobytes() == flat.tobytes()
    used = {tuple(p) for a in runtime.values() for p in a[a[:, :, 3] == 255][:, :3].tolist()}
    gpl = (ROOT / files["palette-gpl"]["file"]).read_text(encoding="utf-8").splitlines()
    pal = {tuple(int(v) for v in line.split("\t")[0].split()) for line in gpl if line[:1].isdigit() or line[:1] == " "}
    r["colours_used"] = len(used)
    r["colour_budget"] = author.PALETTE_SIZE + len(author.HAND)
    r["all_colours_in_gpl_palette"] = used <= pal and len(used) <= r["colour_budget"]
    r["static_layers_partition_canvas"] = bool((sum((np.array(layers[n])[:, :, 3] == 255).astype(int) for n in author.STATIC[:3]) == 1).all())
    mask = rgba(ROOT / files["walkmask-guide"]["file"])
    r["guide_equals_rebuild"] = mask.tobytes() == np.array(guide).tobytes()
    gd = gd_geometry()
    r["gd_walk_blocks_match_author"] = gd["walk"] == tuple(author.WALK) and sorted(gd["blocks"]) == sorted(tuple(b) for b in author.BLOCKS)
    r["gd_kiosk_matches_author"] = gd["kiosk"] == tuple(author.KIOSK)
    r["gd_pivots_match_author"] = gd["pivots"] == [p for _, p in author.YSORT] and gd["layer_files"] == [n for n, _ in author.YSORT] and gd["ground"] == ["ground-far"]
    r["legacy_pins"] = author.walkable(400, 180) and not author.walkable(440, 195) and not author.walkable(410, 190) and author.walkable(410, 180)
    r["spawn_walkable"] = author.walkable(*gd["spawn"])
    r["head_clear_of_deck"] = gd["walk_top"] - 44 >= gd["deck_bottom"] and gd["deck_bottom"] == author.DECK_BOTTOM
    r["pivots_fractional"] = all(p % 1 == 0.5 for p in gd["pivots"])
    # The Loop scene runs this v02 script directly or through opt-in selectors that extend it; each
    # selector must fall through to super() (v02) when its flag is off. Godot proves the default render.
    chain = runtime_script_chain()
    v02_res = "res://scripts/" + SCENE_SCRIPT.name
    r["runtime_scene_script_chain"] = [c.rsplit("/", 1)[1] for c in chain]
    r["runtime_scene_uses_v02_script"] = v02_res in chain and all(
        "\t\tsuper()" in (ROOT / "game" / c.replace("res://", "")).read_text(encoding="utf-8") for c in chain[:chain.index(v02_res)])
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
    tmp = tempfile.mkdtemp(prefix="wb-chi-v02-")
    try:
        rebuilt = author.build(out=Path(tmp) / "o", runtime=Path(tmp) / "r")
        r["rebuild_deterministic"] = all(rebuilt["files"][k]["sha256"] == v["sha256"] for k, v in files.items())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    r["merged_flat_stats"] = flat_stats(flat[:, :, :3])
    return r, flat


def capture_checks(flat, stamp):
    r = {}
    name = lambda folder, tag, variant, st: folder / f"rpg-2-star-ocean-the-second_chicago-loop_state-lake-godot-{tag}-640x360_{variant}_{st}.png"
    arrival = rgba(name(CAPTURES, "zh-arrival", "v02", stamp))
    keep = np.zeros((360, 640), bool)
    keep[62:318, :] = True
    for x0, y0, x1, y1 in LABEL_BOXES + [HERO_BOX]:
        keep[y0:y1, x0:x1] = False
    diff = (arrival[:, :, :3] != flat[:, :, :3]).any(axis=2) & keep
    r["godot_arrival_matches_layers_outside_hero_and_labels"] = int(diff.sum())
    r["godot_arrival_pixels_compared"] = int(keep.sum())
    for tag in ("zh-arrival", "en-arrival", "zh-approved-heroine-ref"):
        r[f"v01_{tag}"] = flat_stats(rgba(name(V01_CAPTURES, tag, "v01", V01_STAMP))[:, :, :3])
        r[f"v02_{tag}"] = flat_stats(rgba(name(CAPTURES, tag, "v02", stamp))[:, :, :3])
    r["captures_present"] = sorted(p.name for p in CAPTURES.glob(f"*_{stamp}.png"))
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
    names = [n for n, _ in author.LAYERS]
    tmp = tempfile.mkdtemp(prefix="wb-chi2-pxo-")
    try:
        layers = author.build_layers()
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
    s, flat = source_checks(author, manifest)
    c = capture_checks(flat, a.capture_stamp)
    p = pixelorama_checks(a.pixelorama, author, manifest) if os.path.isfile(a.pixelorama) else None
    v1, v2 = c["v01_zh-arrival"], c["v02_zh-arrival"]
    gates = {
        "S1_hashes_and_rebuild_exact": s["hashes_match_manifest"] and s["runtime_layers_equal_rebuild"] and s["rebuild_deterministic"] and s["merged_preview_equals_runtime_layers"],
        "S2_canvas_alpha_palette": s["sizes_640x360"] and s["ground_opaque"] and s["source_and_ysort_binary_alpha"] and s["all_colours_in_gpl_palette"] and s["static_layers_partition_canvas"],
        "S3_openraster_exact": s["ora_mimetype_first_stored"] and s["ora_layers_exact"] and s["ora_guide_hidden"],
        "S4_pxo_exact": s["pxo_version"] == 7 and s["pxo_layers_exact"] and s["pxo_guide_hidden_locked"],
        "G1_walk_guide_and_runtime_geometry_match": s["guide_equals_rebuild"] and s["gd_walk_blocks_match_author"] and s["gd_kiosk_matches_author"] and s["gd_pivots_match_author"],
        "G2_pins_spawn_head_clearance_pivots": s["legacy_pins"] and s["spawn_walkable"] and s["head_clear_of_deck"] and s["pivots_fractional"],
        "G3_runtime_scene_wired_to_v02": s["runtime_scene_uses_v02_script"],
        "A1_no_large_flat_fill": s["merged_flat_stats"]["largest_single_colour_share"] < 0.05,
        "C1_godot_native_render_exact": c["godot_arrival_matches_layers_outside_hero_and_labels"] == 0 and c["godot_arrival_pixels_compared"] > 150000,
        "C2_v02_denser_and_less_repetitive_than_v01": (v2["edge_density"] > v1["edge_density"] and v2["distinct_16px_block_share"] > v1["distinct_16px_block_share"]
                                                       and v2["largest_single_colour_share"] < v1["largest_single_colour_share"]),
        "C3_captures_present": len(c["captures_present"]) == 8,
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
    print("v01 zh arrival:", json.dumps(v1))
    print("v02 zh arrival:", json.dumps(v2))
    print(f"CHICAGO_LOOP_V02_PIXEL_SOURCE_CHECK {report['passed']}/{report['total']}")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
