"""Pixel, source, wiring and Pixelorama checks for the Chicago Loop State/Lake candidate v03 (UNAPPROVED, opt-in).

Usage: python -I <this file> --capture-stamp <stamp> [--pixelorama <exe>] [--report <json path>]
Reads the manifest written by the v03 author tool, the v03 scene script, the opt-in selector, the runtime
Loop scene, the real Godot captures in outputs/chicago-loop-state-lake-v03/godot-runtime (including the
visible-hero counts JSON), and for the actual-scale comparison the untouched v02 captures. Pixelorama runs
use a fresh temp APPDATA and the real %APPDATA%/pixelorama dir is snapshotted before and after.
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
AUTHOR = ROOT / "tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-author_unapproved-v03_20261017-174431-c223d3f7.py"
SCENE_SCRIPT = ROOT / "game/scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v03_20261017-174431-c223d3f7.gd"
V03_SCENE = ROOT / "game/scenes/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v03_20261017-174431-c223d3f7.tscn"
SELECTOR = ROOT / "game/scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v03_20261017-174431-c223d3f7.gd"
RUNTIME_SCENE = ROOT / "game/scenes/rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn"
V02_SCRIPT = "res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v02_20261017-160959-55667f46.gd"
V02_MANIFEST = ROOT / "outputs/chicago-loop-state-lake-v02/rpg-2-star-ocean-the-second_chicago-loop_state-lake_layer-manifest_unapproved-v02_20261017-160959-55667f46.json"
CAPTURES = ROOT / "outputs/chicago-loop-state-lake-v03/godot-runtime"
V02_CAPTURES = ROOT / "outputs/chicago-loop-state-lake-v02/godot-runtime"
V02_STAMP = "20261017-162405-1bdb3cd5"
# Runtime label boxes (with outline) and the arrival hero box, excluded from render parity.
LABEL_BOXES = [(146, 183, 240, 201), (0, 279, 102, 297), (305, 106, 364, 124)]
HERO_BOX = (320 - 17, 286 - 46, 320 + 17, 286 + 6)
EXPECTED_CAPTURES = ["en-default-off-v02-entry", "zh-entry", "en-entry", "zh-traverse-under-l-lane", "en-traverse-crosswalk",
                     "zh-traverse-stair-foot", "zh-occlusion-column-raw", "en-occlusion-column-reveal", "zh-occlusion-honey-locust",
                     "zh-interact-kiosk", "en-interact-kiosk", "zh-interact-stair", "en-interact-stair", "zh-interact-pylon",
                     "en-interact-pylon", "zh-approved-heroine-ref", "en-approved-heroine-ref"]


def load_author():
    spec = spec_from_file_location("chicago_author_v03", AUTHOR)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rgba(path_or_bytes):
    src = io.BytesIO(path_or_bytes) if isinstance(path_or_bytes, bytes) else path_or_bytes
    return np.array(Image.open(src).convert("RGBA"))


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


def isolated_share(rgb):
    """Share of visible-art pixels whose four neighbours all differ from them (speckle, not clusters)."""
    v = rgb[62:318].astype(np.int32)
    c = (v[..., 0] << 16) | (v[..., 1] << 8) | v[..., 2]
    p = np.pad(c, 1, mode="edge")
    iso = (p[1:-1, :-2] != c) & (p[1:-1, 2:] != c) & (p[:-2, 1:-1] != c) & (p[2:, 1:-1] != c)
    return round(float(iso[1:-1, 1:-1].mean()), 4)


def material_shares(rgb):
    """Plaza-level (rows 178..317) shares of foliage, teal civic light and lit stone, by colour key."""
    v = rgb[178:318].astype(int)
    r, g, b = v[..., 0], v[..., 1], v[..., 2]
    foliage = (g > r + 6) & (g > b + 6)
    teal = (b > r + 30) & (g > r + 30) & (g + b > 140)
    lum = (r * 299 + g * 587 + b * 114) // 1000
    stone_lit = (lum > 120) & (np.abs(r - b) < 70) & ~foliage & ~teal
    return {"foliage": round(float(foliage.mean()), 4), "teal": round(float(teal.mean()), 4), "lit_stone": round(float(stone_lit.mean()), 4)}


def flat_stats(rgb):
    vis = rgb[62:318].reshape(-1, 3)
    colours, counts = np.unique(vis, axis=0, return_counts=True)
    dx = (rgb[62:318, 1:] != rgb[62:318, :-1]).any(axis=2)[:-1, :]
    dy = (rgb[63:318] != rgb[62:317]).any(axis=2)[:, :-1]
    return {"visible_colours": int(len(colours)), "largest_single_colour_share": round(float(counts.max() / counts.sum()), 4),
            "edge_density": round(float((dx | dy).mean()), 4), "isolated_pixel_share": isolated_share(rgb), **material_shares(rgb)}


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


_PROPS = None


def author_props(author):
    global _PROPS
    if _PROPS is None:
        _PROPS = author.build_layers()[1]
    return _PROPS


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
        return sha(data.replace(b"\r\n", b"\n") if v["hash_algorithm"] == "sha256-text-lf-v1" else data)
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
    # Opt-in wiring: Loop scene -> selector (extends the unchanged v02 script) -> v03 scene -> v03 script.
    sel = SELECTOR.read_text(encoding="utf-8")
    # The Loop scene names this selector, or a later selector that extends v02 and delegates the v03 flag
    # to this selector's own rule (v03_enabled() -> V03_SCENE). Godot proves the v03 route end to end.
    m = re.search(r'\[ext_resource type="Script" path="res://scripts/([^"]+)"', RUNTIME_SCENE.read_text(encoding="utf-8"))
    loop_script = m.group(1) if m else ""
    loop_src = (ROOT / "game/scripts" / loop_script).read_text(encoding="utf-8") if loop_script else ""
    r["runtime_scene_script"] = loop_script
    r["runtime_scene_uses_selector"] = loop_script == SELECTOR.name or (
        loop_src.startswith(f'extends "{V02_SCRIPT}"') and f'preload("res://scripts/{SELECTOR.name}")' in loop_src
        and ".v03_enabled()" in loop_src and ".V03_SCENE" in loop_src and "\t\tsuper()" in loop_src)
    r["selector_extends_v02_and_targets_v03"] = (sel.startswith(f'extends "{V02_SCRIPT}"') and V03_SCENE.name in sel
                                                 and '"--chicago-state-lake-v03"' in sel and "static var enabled_override := -1" in sel)
    r["v03_scene_uses_v03_script"] = SCENE_SCRIPT.name in V03_SCENE.read_text(encoding="utf-8")
    v02 = json.loads(V02_MANIFEST.read_text(encoding="utf-8"))
    v02_paths = [ROOT / v["file"] for v in v02["files"].values()]
    v02_code = [ROOT / "game/scripts" / V02_SCRIPT.rsplit("/", 1)[1],
                ROOT / "tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-author_unapproved-v02_20261017-160959-55667f46.py",
                ROOT / "tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-godot-capture-check_v02_20261017-160959-4c432d04.gd",
                ROOT / "tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-source-check_v02_20261017-160959-7af12ce1.py"]
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
    tmp = tempfile.mkdtemp(prefix="wb-chi3-")
    try:
        rebuilt = author.build(out=Path(tmp) / "o", runtime=Path(tmp) / "r")
        r["rebuild_deterministic"] = all(rebuilt["files"][k]["sha256"] == v["sha256"] for k, v in files.items())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    r["provenance"] = manifest["provenance"]
    r["hero_visibility"] = manifest["hero_visibility"]
    return r, runtime, flat


def capture_checks(author, runtime, stamp):
    r = {}
    name = lambda folder, tag, variant, st: folder / f"rpg-2-star-ocean-the-second_chicago-loop_state-lake-godot-{tag}-640x360_{variant}_{st}.png"
    entry = rgba(name(CAPTURES, "zh-entry", "v03", stamp))
    composite = ysorted_composite(author, runtime)
    keep = np.zeros((360, 640), bool)
    keep[62:318, :] = True
    for x0, y0, x1, y1 in LABEL_BOXES + [HERO_BOX]:
        keep[y0:y1, x0:x1] = False
    diff = (entry[:, :, :3] != composite[:, :, :3]).any(axis=2) & keep
    r["godot_entry_matches_ysorted_layers_outside_hero_and_labels"] = int(diff.sum())
    r["godot_entry_pixels_compared"] = int(keep.sum())
    counts = json.loads((CAPTURES / f"rpg-2-star-ocean-the-second_chicago-loop_state-lake-godot-visible-hero-counts_v03_{stamp}.json").read_text(encoding="utf-8"))
    hero = rgba(author.HERO_IDLE)
    model = {}
    for key, c in counts["spots"].items():
        at = (int(c["at"][0]), int(c["at"][1]))
        model[key] = {"godot_raw": c["raw"], "model_raw": model_visible(author, runtime, hero, at, False),
                      "godot_reveal": c["reveal"], "model_reveal": model_visible(author, runtime, hero, at, c["needs_reveal"])}
    r["visible_hero_godot_vs_model"] = model
    r["visible_hero_raw_exact"] = all(m["godot_raw"] == m["model_raw"] for m in model.values())
    r["visible_hero_reveal_within_3px"] = all(abs(m["godot_reveal"] - m["model_reveal"]) <= 3 for m in model.values())
    for tag in ("zh-arrival", "zh-approved-heroine-ref", "en-approved-heroine-ref"):
        r[f"v02_{tag}"] = flat_stats(rgba(name(V02_CAPTURES, tag, "v02", V02_STAMP))[:, :, :3])
    r["v03_zh-entry"] = flat_stats(entry[:, :, :3])
    for tag in ("zh-approved-heroine-ref", "en-approved-heroine-ref"):
        r[f"v03_{tag}"] = flat_stats(rgba(name(CAPTURES, tag, "v03", stamp))[:, :, :3])
    present = sorted(p.name for p in CAPTURES.glob(f"*_{stamp}.png"))
    r["captures_present"] = present
    r["captures_complete"] = all(name(CAPTURES, t, "v03", stamp).name in present for t in EXPECTED_CAPTURES) and len(present) == len(EXPECTED_CAPTURES)
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
    tmp = tempfile.mkdtemp(prefix="wb-chi3-pxo-")
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
    v2, v3 = c["v02_zh-approved-heroine-ref"], c["v03_zh-approved-heroine-ref"]
    hv = s["hero_visibility"]
    gates = {
        "S1_hashes_and_rebuild_exact": s["hashes_match_manifest"] and s["runtime_layers_equal_rebuild"] and s["rebuild_deterministic"] and s["merged_preview_equals_runtime_layers"],
        "S2_canvas_alpha_palette": s["sizes_640x360"] and s["ground_opaque"] and s["source_and_ysort_binary_alpha"] and s["all_colours_in_gpl_and_curated_palette"],
        "S3_openraster_exact": s["ora_mimetype_first_stored"] and s["ora_layers_exact"] and s["ora_guide_hidden"],
        "S4_pxo_exact": s["pxo_version"] == 7 and s["pxo_layers_exact"] and s["pxo_guide_hidden_locked"],
        "G1_walk_reveal_and_runtime_constants_match": (s["guide_equals_rebuild"] and s["reveal_mask_equals_rebuild"] and s["gd_walk_blocks_match_author"]
                                                       and s["gd_spawn_sites_match_author"] and s["gd_props_match_manifest"] and s["gd_art_path_matches_runtime_files"]
                                                       and s["gd_reveal_shader_matches_model"]),
        "G2_pins_spawn_head_clearance_pivots": s["legacy_pins"] and s["spawn_walkable"] and s["head_clear_of_deck"] and s["pivots_fractional_and_on_footprints"],
        "G3_opt_in_wiring_and_v02_baseline_unchanged": (s["runtime_scene_uses_selector"] and s["selector_extends_v02_and_targets_v03"] and s["v03_scene_uses_v03_script"]
                                                        and s["v02_baseline_hashes_unchanged"] and s["v02_baseline_git_clean"]),
        "H1_hero_at_least_half_visible_everywhere_with_reveal": hv["with_reveal_min_visible_fraction"] >= 0.5,
        "C1_godot_native_render_exact": c["godot_entry_matches_ysorted_layers_outside_hero_and_labels"] == 0 and c["godot_entry_pixels_compared"] > 150000,
        "C2_godot_visible_hero_matches_model": c["visible_hero_raw_exact"] and c["visible_hero_reveal_within_3px"],
        "C3_plaza_denser_in_foliage_teal_and_lit_stone_than_v02": v3["foliage"] > v2["foliage"] and v3["teal"] > v2["teal"] and v3["lit_stone"] > v2["lit_stone"],
        "C4_fewer_isolated_pixels_than_v02": v3["isolated_pixel_share"] < v2["isolated_pixel_share"],
        "C5_captures_complete": c["captures_complete"],
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
    print("v03 zh approved-heroine-ref:", json.dumps(v3))
    print(f"CHICAGO_LOOP_V03_PIXEL_SOURCE_CHECK {report['passed']}/{report['total']}")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
