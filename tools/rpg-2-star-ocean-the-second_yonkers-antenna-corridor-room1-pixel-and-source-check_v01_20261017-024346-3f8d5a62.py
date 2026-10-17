"""Exact pixel and source checks for the Yonkers room 1 antenna fixture pilot.

Usage: python -I <this file> <before capture dir> <after capture dir> [--pixelorama <exe>]
Before captures come from HEAD survey_annex.gd, after captures from the fixture integration,
both made by ...yonkers-antenna-corridor-room1-capture-and-check...gd with the same hero poses.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import glob
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = ROOT / "tools/rpg-2-star-ocean-the-second_yonkers-antenna-corridor-room1-pixel-fixtures-author_v01_20261017-024000-9b3e6f21.py"
CLUES = [(163, 165), (320, 165), (477, 165)]
OFFSET = (-32, 2)
LABEL_RECTS = [(x - 48, y - 45, x + 48, y - 9) for x, y in CLUES]
LANE = (16, 236, 624, 290)


def load_author():
    spec = spec_from_file_location("yonkers_room1_author", AUTHOR)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rgba(path_or_bytes):
    src = io.BytesIO(path_or_bytes) if isinstance(path_or_bytes, bytes) else path_or_bytes
    return np.array(Image.open(src).convert("RGBA"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def one(folder, pattern):
    hits = glob.glob(os.path.join(folder, pattern))
    if len(hits) != 1:
        raise SystemExit(f"expected one {pattern} in {folder}, got {hits}")
    return hits[0]


def source_checks(author, manifest):
    rep = {}
    hexes = {tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for v in author.C.values()}
    for (slug, fn, clue, _), item in zip(author.FIXTURES, manifest["assets"]):
        layers = fn()
        flat = author.merged(layers)
        files = {ext: (ROOT / item["files"][ext]["file"]).read_bytes() for ext in ("png", "ora", "pxo")}
        runtime = (ROOT / item["runtime_png"]["file"]).read_bytes()
        r = {"hashes_match_manifest": all(sha(files[e]) == item["files"][e]["sha256"] for e in files) and sha(runtime) == item["runtime_png"]["sha256"],
             "runtime_png_equals_source_png": runtime == files["png"],
             "png_equals_rebuilt_layers": rgba(files["png"]).tobytes() == np.array(flat).tobytes(),
             "size": list(Image.open(io.BytesIO(files["png"])).size)}
        with zipfile.ZipFile(io.BytesIO(files["ora"])) as z:
            stack = ET.fromstring(z.read("stack.xml"))
            names = [el.get("name") for el in stack.iter("layer")]
            r["ora_mimetype_first_stored"] = z.infolist()[0].filename == "mimetype" and z.infolist()[0].compress_type == zipfile.ZIP_STORED
            r["ora_layers_top_to_bottom"] = names
            by_name = {el.get("name"): el.get("src") for el in stack.iter("layer")}
            r["ora_layers_exact"] = all(rgba(z.read(by_name[n])).tobytes() == np.array(img).tobytes() for n, img in zip(author.LAYERS, layers))
            r["ora_merged_exact"] = rgba(z.read("mergedimage.png")).tobytes() == np.array(flat).tobytes()
        with zipfile.ZipFile(io.BytesIO(files["pxo"])) as z:
            data = json.loads(z.read("data.json"))
            r["pxo_version"] = data["pxo_version"]
            r["pxo_layers_bottom_to_top"] = [l["name"] for l in data["layers"]]
            r["pxo_layers_exact"] = all(z.read(f"image_data/frames/1/layer_{i}") == img.tobytes() for i, img in enumerate(layers, start=1))
        a = np.array(flat)
        alpha_values = sorted(set(np.unique(a[..., 3]).tolist()))
        r["alpha_values"] = alpha_values
        shadow_alpha = np.array(layers[0])[..., 3]
        r["only_semi_alpha_is_contact_shadow"] = set(np.unique(shadow_alpha).tolist()) <= {0, 0xA8} and all(
            set(np.unique(np.array(l)[..., 3]).tolist()) <= {0, 255} for l in layers[1:])
        opaque_colours = {tuple(c) for c in a[a[..., 3] == 255][:, :3].tolist()}
        r["opaque_colours"] = len(opaque_colours)
        r["opaque_colours_all_in_palette"] = opaque_colours <= hexes
        rep[slug] = r
    second = {slug: author.merged(fn()).tobytes() for slug, fn, _, _ in author.FIXTURES}
    rep["rebuild_deterministic"] = all(second[s] == author.merged(f()).tobytes() for s, f, _, _ in author.FIXTURES)
    return rep


def capture_checks(before_dir, after_dir, fixtures):
    rep = {}
    rects = [(x + OFFSET[0], y + OFFSET[1], x + OFFSET[0] + 64, y + OFFSET[1] + 64) for x, y in CLUES]
    in_rect = np.zeros((360, 640), bool)
    fixture_alpha = np.zeros((360, 640), np.uint8)
    fixture_rgb = np.zeros((360, 640, 3), np.int16)
    for (x0, y0, x1, y1), f in zip(rects, fixtures):
        in_rect[y0:y1, x0:x1] = True
        fixture_alpha[y0:y1, x0:x1] = f[..., 3]
        fixture_rgb[y0:y1, x0:x1] = f[..., :3]
    yy, xx = np.mgrid[0:360, 0:640]
    marker = np.zeros((360, 640), bool)
    ring = np.zeros((360, 640), bool)
    for cx, cy in CLUES:
        dist = np.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
        marker |= dist <= 17.0
        ring |= (dist >= 13.2) & (dist <= 14.8)
    for shot in ("zh-start", "en-start", "zh-lane-b"):
        b = rgba(one(before_dir, f"*-{shot}-640x360_*.png")).astype(np.int16)
        a = rgba(one(after_dir, f"*-{shot}-640x360_*.png")).astype(np.int16)
        diff = (a != b).any(axis=2)
        r = {"size": [a.shape[1], a.shape[0]], "changed_pixels": int(diff.sum()),
             "changed_outside_fixture_rects": int((diff & ~in_rect).sum()),
             "changed_where_fixture_transparent": int((diff & (fixture_alpha == 0)).sum()),
             "marker_ring_pixels_changed": int((diff & ring).sum())}
        hero = np.zeros((360, 640), bool)
        if shot == "zh-lane-b":
            # Hero texels: where the lane-b pose differs from the start pose in the baseline.
            bs = rgba(one(before_dir, "*-zh-start-640x360_*.png")).astype(np.int16)
            hero = (b != bs).any(axis=2) & (yy > 150) & (yy < 250) & (xx > 290) & (xx < 350)
            r["hero_pixels"] = int(hero.sum())
            r["hero_pixels_changed_by_fixtures"] = int((diff & hero).sum())
        free = (fixture_alpha == 255) & ~marker & ~hero
        r["opaque_fixture_pixels_checked"] = int(free.sum())
        r["opaque_fixture_pixels_exact"] = int(((a[..., :3] == fixture_rgb).all(axis=2) & free).sum())
        semi = (fixture_alpha == 0xA8) & ~marker & ~hero
        expect = (b[..., :3] * (255 - 0xA8) + fixture_rgb * 0xA8) / 255.0
        r["shadow_pixels_checked"] = int(semi.sum())
        r["shadow_blend_max_channel_error"] = float(np.abs(a[..., :3] - expect)[semi].max()) if semi.any() else 0.0
        opaque_any = fixture_alpha > 0
        r["fixture_pixels_in_label_rects"] = int(sum(opaque_any[y0:y1, x0:x1].sum() for x0, y0, x1, y1 in LABEL_RECTS))
        r["fixture_pixels_in_walk_lane"] = int(opaque_any[LANE[1]:LANE[3], LANE[0]:LANE[2]].sum())
        r["fixture_rows_screen"] = [int(yy[opaque_any].min()), int(yy[opaque_any].max())]
        rep[shot] = r
    return rep


def run_pixelorama(exe, args, appdata):
    env = dict(os.environ)
    env["APPDATA"] = appdata
    return subprocess.run([exe, "--headless", "--quit", "--"] + args, capture_output=True, text=True, timeout=180, env=env)


def real_pixelorama_snapshot():
    root = os.path.join(os.environ.get("APPDATA", ""), "pixelorama")
    snap = {}
    if os.path.isdir(root):
        for d, _, files in os.walk(root):
            for f in files:
                rel = os.path.relpath(os.path.join(d, f), root).replace("\\", "/")
                if rel != ".running":
                    snap[rel] = sha(open(os.path.join(d, f), "rb").read())
    return snap


def pixelorama_checks(exe, author, manifest):
    rep = {}
    before = real_pixelorama_snapshot()
    tmp = tempfile.mkdtemp(prefix="wb-yk-r1-pxo-")
    try:
        for (slug, fn, _, _), item in zip(author.FIXTURES, manifest["assets"]):
            layers = fn()
            flat = np.array(author.merged(layers))
            for ext in ("pxo", "ora"):
                src = os.path.join(tmp, f"{slug}.{ext}")
                shutil.copyfile(ROOT / item["files"][ext]["file"], src)
                r = {}
                for mode in ("split", "flat"):
                    appdata = os.path.join(tmp, f"app-{slug}-{ext}-{mode}")
                    od = os.path.join(tmp, f"out-{slug}-{ext}-{mode}")
                    os.makedirs(appdata)
                    os.makedirs(od)
                    args = ["--export"] + (["--split-layers"] if mode == "split" else []) + ["-o", os.path.join(od, "f.png"), src]
                    p = run_pixelorama(exe, args, appdata)
                    outs = sorted(os.listdir(od))
                    if mode == "split":
                        exact = {}
                        for name, img in zip(author.LAYERS, layers):
                            hit = [o for o in outs if f"({name})" in o]
                            exact[name] = len(hit) == 1 and rgba(os.path.join(od, hit[0])).tobytes() == np.array(img).tobytes()
                        r["split"] = {"exit": p.returncode, "pngs": len(outs), "layers_exact": exact}
                    else:
                        got = rgba(os.path.join(od, outs[0])).astype(np.int16) if len(outs) == 1 else None
                        r["flat"] = {"exit": p.returncode, "pngs": len(outs),
                                     "exact": got is not None and got.tobytes() == flat.astype(np.int16).tobytes(),
                                     "differing_texels": int((got != flat).any(axis=2).sum()) if got is not None else None,
                                     "max_channel_delta": int(np.abs(got - flat).max()) if got is not None else None}
                r["source_unchanged_by_cli"] = open(src, "rb").read() == (ROOT / item["files"][ext]["file"]).read_bytes()
                rep[f"{slug}.{ext}"] = r
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    after = real_pixelorama_snapshot()
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    # An open Pixelorama GUI from another session autosaves its untitled backup about every 62 s;
    # headless --export runs never write untitled backups, so those are listed but not counted.
    gui = [k for k in changed if k.startswith("backups/") and "/(untitled backup)-" in k]
    rep["real_appdata_gui_autosave_changes_excluded"] = gui
    rep["real_appdata_pixelorama_changed"] = [k for k in changed if k not in gui]
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--pixelorama", default=str(ROOT / "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"))
    a = ap.parse_args()
    author = load_author()
    manifest_path = one(str(author.art.OUT), "*three-antenna-fixtures-manifest*.json")
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    fixtures = [rgba(ROOT / item["runtime_png"]["file"]) for item in manifest["assets"]]
    rep = {"sources": source_checks(author, manifest), "captures": capture_checks(a.before, a.after, fixtures)}
    if os.path.isfile(a.pixelorama):
        rep["pixelorama_cli"] = pixelorama_checks(a.pixelorama, author, manifest)
    s, c, p = rep["sources"], rep["captures"], rep.get("pixelorama_cli", {})
    gates = {
        "S1_sources_exact": all(v["hashes_match_manifest"] and v["runtime_png_equals_source_png"] and v["png_equals_rebuilt_layers"]
                                and v["ora_layers_exact"] and v["ora_merged_exact"] and v["pxo_layers_exact"] and v["ora_mimetype_first_stored"]
                                and v["size"] == [64, 64] and len(v["pxo_layers_bottom_to_top"]) == 4 for k, v in s.items() if isinstance(v, dict)),
        "S2_palette_and_alpha": all(v["opaque_colours_all_in_palette"] and v["only_semi_alpha_is_contact_shadow"] for k, v in s.items() if isinstance(v, dict)),
        "S3_rebuild_deterministic": s["rebuild_deterministic"],
        "C1_only_fixture_pixels_changed": all(v["changed_outside_fixture_rects"] == 0 and v["changed_where_fixture_transparent"] == 0 for v in c.values()),
        "C2_markers_labels_lane_clear": all(v["marker_ring_pixels_changed"] == 0 and v["fixture_pixels_in_label_rects"] == 0 and v["fixture_pixels_in_walk_lane"] == 0 for v in c.values()),
        "C3_fixture_pixels_native_exact": all(v["opaque_fixture_pixels_exact"] == v["opaque_fixture_pixels_checked"] and v["shadow_blend_max_channel_error"] <= 1.0 for v in c.values()),
        "C4_hero_not_hidden": c["zh-lane-b"]["hero_pixels"] > 300 and c["zh-lane-b"]["hero_pixels_changed_by_fixtures"] == 0,
        "P1_pixelorama_split_layers_exact": bool(p) and all(v["split"]["exit"] == 0 and all(v["split"]["layers_exact"].values()) and v["source_unchanged_by_cli"] for k, v in p.items() if isinstance(v, dict)),
        "P2_pixelorama_real_appdata_untouched": bool(p) and not p["real_appdata_pixelorama_changed"],
    }
    rep["gates"] = gates
    rep["report_only_pixelorama_flat_exact"] = {k: v["flat"]["exact"] for k, v in p.items() if isinstance(v, dict)}
    rep["result"] = "PASS" if all(gates.values()) else "FAIL"
    print(json.dumps(rep, indent=1, ensure_ascii=False))
    return 0 if rep["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
