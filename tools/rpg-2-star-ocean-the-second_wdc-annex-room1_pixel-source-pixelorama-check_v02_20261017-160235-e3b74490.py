"""Exact pixel, source, provenance and Pixelorama checks for the Washington survey annex room 1 v02 pass.

Usage: python -I <this file> <v02 capture dir> [--pixelorama <exe>] [--report <json>]
v02 captures come from ...wdc-annex-room1_godot-capture-and-check_v02...gd. The v01 baseline captures and
sources (outputs/wdc-sr1-v01_65b9618f) are read only, as the unchanged comparison baseline.
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
AUTHOR = ROOT / "tools/rpg-2-star-ocean-the-second_wdc-annex-room1_capitol-interior-author_unapproved-v02_20261017-160235-71300729.py"
V01_DIR = ROOT / "outputs/wdc-sr1-v01_65b9618f"
V01_MANIFEST = V01_DIR / "rpg-2-star-ocean-the-second_wdc-annex-room1_scene-and-fixtures-manifest_unapproved-v01_20261017-030801-65b9618f.json"
CLUES = [(163, 165), (320, 165), (477, 165)]
EXIT, NEXT = (57, 257), (580, 257)
OFFSET = (-32, 2)
LABEL_RECTS = [(x - 48, y - 45, x + 48, y - 9) for x, y in CLUES]
DOOR_LABEL_RECTS = [(EXIT[0] - 41, EXIT[1] - 55, EXIT[0] + 72, EXIT[1] - 31), (NEXT[0] - 36, NEXT[1] - 55, NEXT[0] + 40, NEXT[1] - 31)]
LANE = (16, 236, 624, 290)
TEXT_GAP = (384, 4, 418, 32)  # header strip between the en title end (x 378) and the Save button


def hero_box(x, y):
    return (x - 27, y - 49, x + 28, y + 9)


def load_author():
    spec = spec_from_file_location("wdc_room1_author_v02", AUTHOR)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rgba(src):
    if isinstance(src, bytes):
        src = io.BytesIO(src)
    return np.array(Image.open(src).convert("RGBA"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def one(folder, pattern):
    hits = glob.glob(os.path.join(folder, pattern))
    if len(hits) != 1:
        raise SystemExit(f"expected one {pattern} in {folder}, got {hits}")
    return hits[0]


def check_asset(item, names, layers):
    flat = np.array(author_mod.merged(layers))
    files = {ext: (ROOT / item["files"][ext]["file"]).read_bytes() for ext in ("png", "ora", "pxo")}
    runtime = (ROOT / item["runtime_png"]["file"]).read_bytes()
    r = {"hashes_match_manifest": all(sha(files[e]) == item["files"][e]["sha256"] for e in files) and sha(runtime) == item["runtime_png"]["sha256"],
         "runtime_png_equals_source_png": runtime == files["png"],
         "png_equals_rebuilt_layers": rgba(files["png"]).tobytes() == flat.tobytes(),
         "size": list(Image.open(io.BytesIO(files["png"])).size)}
    with zipfile.ZipFile(io.BytesIO(files["ora"])) as z:
        stack = ET.fromstring(z.read("stack.xml"))
        r["ora_mimetype_first_stored"] = z.infolist()[0].filename == "mimetype" and z.infolist()[0].compress_type == zipfile.ZIP_STORED
        by_name = {el.get("name"): el.get("src") for el in stack.iter("layer")}
        r["ora_layers_top_to_bottom"] = [el.get("name") for el in stack.iter("layer")]
        r["ora_layers_exact"] = all(rgba(z.read(by_name[n])).tobytes() == np.array(img).tobytes() for n, img in zip(names, layers))
        r["ora_merged_exact"] = rgba(z.read("mergedimage.png")).tobytes() == flat.tobytes()
    with zipfile.ZipFile(io.BytesIO(files["pxo"])) as z:
        data = json.loads(z.read("data.json"))
        r["pxo_version"] = data["pxo_version"]
        r["pxo_size"] = [data["size_x"], data["size_y"]]
        r["pxo_layers_bottom_to_top"] = [l["name"] for l in data["layers"]]
        r["pxo_layers_exact"] = all(z.read(f"image_data/frames/1/layer_{i}") == img.tobytes() for i, img in enumerate(layers, start=1))
    r["exact"] = all([r["hashes_match_manifest"], r["runtime_png_equals_source_png"], r["png_equals_rebuilt_layers"], r["ora_mimetype_first_stored"],
                      r["ora_layers_exact"], r["ora_merged_exact"], r["pxo_layers_exact"], r["pxo_layers_bottom_to_top"] == names,
                      r["ora_layers_top_to_bottom"] == list(reversed(names))])
    return r, flat


def colours(arr, mask=None):
    px = arr[..., :3] if mask is None else arr[mask][:, :3]
    return {tuple(c) for c in px.reshape(-1, 3).tolist()}


def source_checks(manifest):
    A = author_mod
    hand = {tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for v in A.HP.values()}
    rep = {}
    scene_layers, names, stats, palette_hex, fg_layer, under = A.build_scene()
    r, flat = check_asset(manifest["scene_asset"], names, scene_layers)
    arrays = [np.array(l) for l in scene_layers]
    r["layer_alpha_binary"] = all(set(np.unique(l[..., 3]).tolist()) <= {0, 255} for l in arrays)
    r["merged_fully_opaque"] = bool((flat[..., 3] == 255).all())
    under_pal = colours(under)
    r["underpaint_palette_size"] = len(under_pal)
    under_idx = [i for i, n in enumerate(names) if n.endswith("-underpaint")]
    hand_idx = [i for i, n in enumerate(names) if n.startswith("hand-")]
    r["underpaint_layers_use_only_underpaint_palette"] = all(colours(arrays[i], arrays[i][..., 3] > 0) <= under_pal for i in under_idx)
    r["hand_layers_use_hand_or_underpaint_palette"] = all(colours(arrays[i], arrays[i][..., 3] > 0) <= (hand | under_pal) for i in hand_idx)
    r["merged_unique_colours"] = len(colours(flat))
    r["declared_palette_matches_merged"] = sorted("#%02x%02x%02x" % c for c in colours(flat)) == manifest["scene_palette_hex"]
    r["pixels_per_layer"] = {n: int((l[..., 3] > 0).sum()) for n, l in zip(names, arrays)}
    r["provenance"] = stats
    r["provenance_matches_manifest"] = stats == manifest["scene_asset"]["provenance"]
    rep["scene"] = r
    fg = np.array(fg_layer)
    fr, fflat = check_asset(manifest["foreground_asset"], ["foreground-stubs-occluder"], [Image.fromarray(fg)])
    fr["equals_scene_top_layer"] = fg.tobytes() == arrays[-1].tobytes()
    fr["opaque_pixels_equal_plate"] = bool((fg[fg[..., 3] > 0][:, :3] == flat[fg[..., 3] > 0][:, :3]).all())
    fr["alpha_binary"] = set(np.unique(fg[..., 3]).tolist()) <= {0, 255}
    rows = np.nonzero(fg[..., 3] > 0)[0]
    fr["rows"] = [int(rows.min()), int(rows.max())]
    rep["foreground"] = fr
    rep["fixtures"] = {}
    fixture_flats = []
    for (slug, fn, _, _), item in zip(A.FIXTURES, manifest["fixtures"]):
        layers = [Image.fromarray(l) for l in fn()]
        xr, xflat = check_asset(item, A.FIXTURE_LAYERS, layers)
        shadow_alpha = np.array(layers[0])[..., 3]
        xr["only_semi_alpha_is_contact_shadow"] = set(np.unique(shadow_alpha).tolist()) <= {0, A.SHADOW_RGBA[3]} and all(
            set(np.unique(np.array(l)[..., 3]).tolist()) <= {0, 255} for l in layers[1:])
        xr["opaque_colours_all_in_hand_palette"] = colours(xflat, xflat[..., 3] == 255) <= hand
        xr["opaque_colours"] = len(colours(xflat, xflat[..., 3] == 255))
        rows = np.nonzero(xflat[..., 3] > 0)[0]
        xr["rows_local"] = [int(rows.min()), int(rows.max())]
        rep["fixtures"][slug] = xr
        fixture_flats.append(xflat)
    again = A.build_scene()
    rep["rebuild_deterministic"] = A.merged(again[0]).tobytes() == Image.fromarray(flat).tobytes() and again[2] == stats and all(
        A.merged([Image.fromarray(l) for l in fn()]).tobytes() == Image.fromarray(ff).tobytes() for (_, fn, _, _), ff in zip(A.FIXTURES, fixture_flats))
    ref = (ROOT / manifest["underpainting_source"]["file"]).read_bytes()
    rep["underpainting_reference_hash_matches"] = sha(ref) == manifest["underpainting_source"]["sha256"]
    return rep, flat, fixture_flats, fg


def v01_baseline_checks():
    """The v01 sources, runtime copies and captures stay byte-identical to the v01 manifest."""
    m = json.loads(V01_MANIFEST.read_text(encoding="utf-8"))
    ok, checked = True, 0
    for item in [m["scene_asset"]] + m["fixtures"]:
        for f in list(item["files"].values()) + [item["runtime_png"]]:
            checked += 1
            ok &= sha((ROOT / f["file"]).read_bytes()) == f["sha256"]
    caps = sorted(glob.glob(str(V01_DIR / "before" / "*.png")) + glob.glob(str(V01_DIR / "after" / "*.png")))
    return {"v01_files_checked": checked, "v01_files_match_v01_manifest": bool(ok), "v01_captures_present": len(caps),
            "v01_capture_sha256": {os.path.basename(c): sha(open(c, "rb").read()) for c in caps}}


def rect_mask(rects, pad=0):
    m = np.zeros((360, 640), bool)
    for x0, y0, x1, y1 in rects:
        m[max(0, y0 - pad):min(360, y1 + pad), max(0, x0 - pad):min(640, x1 + pad)] = True
    return m


def capture_checks(cap, plate, fixtures, fg):
    rep = {}
    yy, xx = np.mgrid[0:360, 0:640]
    frects = [(x + OFFSET[0], y + OFFSET[1], x + OFFSET[0] + 64, y + OFFSET[1] + 64) for x, y in CLUES]
    falpha = np.zeros((360, 640), np.int32)
    frgb = np.zeros((360, 640, 3), np.int16)
    fid = np.full((360, 640), -1, np.int32)
    for i, ((x0, y0, x1, y1), f) in enumerate(zip(frects, fixtures)):
        falpha[y0:y1, x0:x1] = f[..., 3]
        frgb[y0:y1, x0:x1] = f[..., :3]
        fid[y0:y1, x0:x1] = np.where(f[..., 3] > 0, i, -1)
    ui = (yy < 62) | (yy >= 318)
    labels = rect_mask(LABEL_RECTS, 3) | rect_mask(DOOR_LABEL_RECTS, 3)
    markers = np.zeros((360, 640), bool)
    ring = np.zeros((360, 640), bool)
    for cx, cy in CLUES + [EXIT, NEXT]:
        d = np.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
        markers |= d <= 17.0
        ring |= (d >= 13.2) & (d <= 14.8)
    fgm = fg[..., 3] > 0
    poses = {"entry": (87, 261), "near-clue-0": (163, 238), "near-clue-1": (320, 238), "near-clue-2": (477, 238)}
    v01 = {"entry": "start", "near-clue-1": "lane-index"}
    for lang in ("zh", "en"):
        for pose, at in poses.items():
            shot = f"{lang}-{pose}"
            a = rgba(one(cap, f"*v02-godot-{shot}-640x360_*.png")).astype(np.int16)
            hero = rect_mask([hero_box(*at)])
            plain = ~ui & ~labels & ~markers & ~hero & (falpha == 0)
            r = {"size": [a.shape[1], a.shape[0]], "plate_pixels_checked": int(plain.sum()),
                 "plate_pixels_exact": int(((a[..., :3] == plate[..., :3]) & plain[..., None]).all(axis=2).sum())}
            free = (falpha == 255) & ~markers & ~hero
            r["opaque_fixture_pixels_checked"] = int(free.sum())
            r["opaque_fixture_pixels_exact"] = int(((a[..., :3] == frgb).all(axis=2) & free).sum())
            semi = (falpha > 0) & (falpha < 255) & ~markers & ~hero
            alpha = author_mod.SHADOW_RGBA[3]
            expect = (plate[..., :3].astype(float) * (255 - alpha) + np.array(author_mod.SHADOW_RGBA[:3]) * alpha) / 255.0
            r["shadow_pixels_checked"] = int(semi.sum())
            r["shadow_blend_max_channel_error"] = float(np.abs(a[..., :3] - expect)[semi].max()) if semi.any() else 0.0
            if pose in v01:
                b = rgba(one(str(V01_DIR / "after"), f"*pilot-godot-{lang}-{v01[pose]}-640x360_*.png")).astype(np.int16)
                other = "lane-index" if v01[pose] == "start" else "start"
                b_other = rgba(one(str(V01_DIR / "after"), f"*pilot-godot-{lang}-{other}-640x360_*.png")).astype(np.int16)
                texels = (b != b_other).any(axis=2) & hero
                r["hero_texels_v01"] = int(texels.sum())
                r["hero_texels_identical_to_v01"] = int(((a == b).all(axis=2) & texels).sum())
                r["marker_ring_pixels_changed_vs_v01"] = int(((a != b).any(axis=2) & ring & ~hero).sum())
                header = ui & (yy < 62)
                r["header_pixels_changed_vs_v01"] = int(((a != b).any(axis=2) & header).sum())
                r["footer_pixels_changed_vs_v01"] = int(((a != b).any(axis=2) & (yy >= 318)).sum())
            if lang == "en":
                gx0, gy0, gx1, gy1 = TEXT_GAP
                strip = a[gy0:gy1, gx0:gx1, :3]
                r["title_save_gap_is_plain_header"] = bool((strip == strip[0, 0]).all())
            rep[shot] = r
    # Occlusion: behind the index cabinet the fixture's opaque pixels cover the heroine, who stays visible around it.
    occ = rgba(one(cap, "*v02-godot-zh-occlusion-behind-index-640x360_*.png")).astype(np.int16)
    ref = rgba(one(cap, "*v02-godot-zh-entry-640x360_*.png")).astype(np.int16)
    box = rect_mask([hero_box(292, 204)])
    cover = box & (fid == 1) & (falpha == 255) & ~markers
    diff = (occ != ref).any(axis=2)
    rep["occlusion_behind_index"] = {"cabinet_pixels_over_hero_box": int(cover.sum()),
                                     "cabinet_pixels_exact": int(((occ[..., :3] == frgb).all(axis=2) & cover).sum()),
                                     "visible_hero_pixels_outside_cabinet": int((diff & box & ~cover).sum()),
                                     "changed_pixels_on_cabinet": int((diff & cover).sum()),
                                     "marker_disc_cabinet_pixels_reordered": int((diff & box & (fid == 1) & markers & ~ring).sum())}
    stub = rgba(one(cap, "*v02-godot-en-obstacle-west-stub-640x360_*.png")).astype(np.int16)
    sref = rgba(one(cap, "*v02-godot-en-entry-640x360_*.png")).astype(np.int16)
    sbox = rect_mask([hero_box(30, 258)])
    sdiff = (stub != sref).any(axis=2) & ~rect_mask([hero_box(87, 261)])
    # hero texels behind the stub: where the plain hero sprite (offset to this pose) would cover foreground pixels
    hero_img = np.array(Image.open(ROOT / "game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png").convert("RGBA"))
    small = hero_img[::2, ::2, 3] > 0
    hidden_by_fg = np.zeros((360, 640), bool)
    hy0, hx0 = 258 - 20 - small.shape[0] // 2, 30 - small.shape[1] // 2
    hidden_by_fg[hy0:hy0 + small.shape[0], hx0:hx0 + small.shape[1]] = small
    hidden_by_fg &= fgm
    rep["occlusion_west_stub"] = {"foreground_pixels_in_hero_box": int((sbox & fgm).sum()),
                                  "foreground_pixels_exact": int(((stub[..., :3] == plate[..., :3]).all(axis=2) & sbox & fgm).sum()),
                                  "visible_hero_pixels": int((sdiff & sbox & ~fgm).sum()),
                                  "hero_texels_hidden_by_foreground": int(hidden_by_fg.sum()),
                                  "changed_pixels_on_foreground": int((sdiff & sbox & fgm).sum())}
    fa = falpha > 0
    rep["fixture_rows_screen"] = [int(yy[fa].min()), int(yy[fa].max())]
    rep["fixture_pixels_in_label_rects"] = int((fa & rect_mask(LABEL_RECTS)).sum())
    rep["fixture_pixels_in_walk_lane"] = int(fa[LANE[1]:LANE[3], LANE[0]:LANE[2]].sum())
    rep["other_rooms_unchanged_vs_v01"] = {}
    for other in ("city-room1", "outskirts-room1", "ruins-room2"):
        a = rgba(one(cap, f"*v02-godot-zh-other-{other}-640x360_*.png"))
        b = rgba(one(str(V01_DIR / "after"), f"*pilot-godot-zh-other-{other}-640x360_*.png"))
        rep["other_rooms_unchanged_vs_v01"][other] = int((a != b).any(axis=2).sum())
    load = rgba(one(cap, "*v02-godot-en-after-load-640x360_*.png"))
    plain = ~ui & ~labels & ~markers & ~rect_mask([hero_box(402, 262)]) & (falpha == 0)
    rep["after_load_plate_exact"] = int(((load[..., :3] == plate[..., :3]).all(axis=2) & plain).sum()) == int(plain.sum())
    return rep


def run_pixelorama(exe, args, appdata):
    env = dict(os.environ)
    env["APPDATA"] = appdata
    return subprocess.run([exe, "--headless", "--quit", "--"] + args, capture_output=True, text=True, timeout=240, env=env)


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


def pixelorama_checks(exe, manifest):
    A = author_mod
    rep = {}
    before = real_pixelorama_snapshot()
    tmp = tempfile.mkdtemp(prefix="wb-wdc-r1v2-pxo-")
    scene_layers, names, _, _, fg_layer, _ = A.build_scene()
    assets = [("scene", names, scene_layers, manifest["scene_asset"]),
              ("foreground", ["foreground-stubs-occluder"], [Image.fromarray(fg_layer)], manifest["foreground_asset"])]
    for (slug, fn, _, _), item in zip(A.FIXTURES, manifest["fixtures"]):
        assets.append((slug, A.FIXTURE_LAYERS, [Image.fromarray(l) for l in fn()], item))
    try:
        for slug, lnames, layers, item in assets:
            flat = np.array(A.merged(layers)).astype(np.int16)
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
                        for n, img in zip(lnames, layers):
                            hit = [o for o in outs if f"({n})" in o]
                            if not hit and len(lnames) == 1 and len(outs) == 1:
                                hit = outs  # a one-layer project exports without the "(layer)" suffix
                            exact[n] = len(hit) == 1 and rgba(os.path.join(od, hit[0])).tobytes() == np.array(img).tobytes()
                        r["split"] = {"exit": p.returncode, "pngs": len(outs), "layers_exact": exact}
                    else:
                        got = rgba(os.path.join(od, outs[0])).astype(np.int16) if len(outs) == 1 else None
                        r["flat"] = {"exit": p.returncode, "pngs": len(outs),
                                     "exact": got is not None and got.tobytes() == flat.tobytes(),
                                     "differing_texels": int((got != flat).any(axis=2).sum()) if got is not None else None,
                                     "max_channel_delta": int(np.abs(got - flat).max()) if got is not None else None}
                r["source_unchanged_by_cli"] = open(src, "rb").read() == (ROOT / item["files"][ext]["file"]).read_bytes()
                rep[f"{slug}.{ext}"] = r
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    after = real_pixelorama_snapshot()
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    gui = [k for k in changed if k.startswith("backups/") and "/(untitled backup)-" in k]
    rep["real_appdata_gui_autosave_changes_excluded"] = gui
    rep["real_appdata_pixelorama_changed"] = [k for k in changed if k not in gui]
    return rep


def main():
    global author_mod
    ap = argparse.ArgumentParser()
    ap.add_argument("captures")
    ap.add_argument("--pixelorama", default=str(ROOT / "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"))
    ap.add_argument("--report")
    a = ap.parse_args()
    author_mod = load_author()
    manifest = json.loads(Path(one(str(author_mod.OUT), "*scene-and-fixtures-manifest*.json")).read_text(encoding="utf-8"))
    src, plate, fixtures, fg = source_checks(manifest)
    rep = {"sources": src, "v01_baseline": v01_baseline_checks(), "captures": capture_checks(a.captures, plate, fixtures, fg)}
    if os.path.isfile(a.pixelorama):
        rep["pixelorama_cli"] = pixelorama_checks(a.pixelorama, manifest)
    s, c, p, v = rep["sources"], rep["captures"], rep.get("pixelorama_cli", {}), rep["v01_baseline"]
    shots = [val for k, val in c.items() if k.startswith(("zh-", "en-"))]
    compared = [val for val in shots if "hero_texels_v01" in val]
    occ, stub = c["occlusion_behind_index"], c["occlusion_west_stub"]
    gates = {
        "S1_sources_exact": s["scene"]["exact"] and s["scene"]["size"] == [640, 360] and len(s["scene"]["pxo_layers_bottom_to_top"]) == 8
                            and s["foreground"]["exact"] and all(v2["exact"] and v2["size"] == [64, 64] and len(v2["pxo_layers_bottom_to_top"]) == 4
                                                                 for v2 in s["fixtures"].values()),
        "S2_palette_alpha_provenance": s["scene"]["layer_alpha_binary"] and s["scene"]["merged_fully_opaque"]
                                       and s["scene"]["underpaint_layers_use_only_underpaint_palette"] and s["scene"]["hand_layers_use_hand_or_underpaint_palette"]
                                       and s["scene"]["declared_palette_matches_merged"] and s["scene"]["merged_unique_colours"] <= 96
                                       and s["scene"]["provenance_matches_manifest"] and s["underpainting_reference_hash_matches"]
                                       and all(v2["opaque_colours_all_in_hand_palette"] and v2["only_semi_alpha_is_contact_shadow"] for v2 in s["fixtures"].values()),
        "S3_rebuild_deterministic": s["rebuild_deterministic"],
        "S4_foreground_is_plate_top_layer": s["foreground"]["equals_scene_top_layer"] and s["foreground"]["opaque_pixels_equal_plate"] and s["foreground"]["alpha_binary"],
        "S5_v01_baseline_untouched": v["v01_files_match_v01_manifest"] and v["v01_files_checked"] == 16 and v["v01_captures_present"] == 16,
        "C1_plate_renders_native_1to1": all(x["plate_pixels_exact"] == x["plate_pixels_checked"] > 110000 for x in shots) and c["after_load_plate_exact"],
        "C2_fixtures_native_exact": all(x["opaque_fixture_pixels_exact"] == x["opaque_fixture_pixels_checked"] and x["shadow_blend_max_channel_error"] <= 1.0 for x in shots),
        "C3_labels_lane_markers_clear": c["fixture_pixels_in_label_rects"] == 0 and c["fixture_pixels_in_walk_lane"] == 0
                                        and all(x["marker_ring_pixels_changed_vs_v01"] == 0 and x["footer_pixels_changed_vs_v01"] == 0 for x in compared),
        "C4_header_en_fixed_zh_unchanged": all(x["title_save_gap_is_plain_header"] for k, x in c.items() if k.startswith("en-"))
                                           and all(x["header_pixels_changed_vs_v01"] == 0 for k, x in c.items() if k.startswith("zh-") and "hero_texels_v01" in x),
        "C5_hero_in_front_unhidden": all(x["hero_texels_identical_to_v01"] == x["hero_texels_v01"] > 300 for x in compared),
        "C6_occlusion_behind_fixture_and_stub": occ["cabinet_pixels_over_hero_box"] > 100 and occ["cabinet_pixels_exact"] == occ["cabinet_pixels_over_hero_box"]
                                                and occ["changed_pixels_on_cabinet"] == 0 and occ["visible_hero_pixels_outside_cabinet"] > 150
                                                and stub["foreground_pixels_in_hero_box"] > 100 and stub["changed_pixels_on_foreground"] == 0
                                                and stub["foreground_pixels_exact"] == stub["foreground_pixels_in_hero_box"] and stub["visible_hero_pixels"] > 150
                                                and stub["hero_texels_hidden_by_foreground"] > 20,
        "C7_other_rooms_pixel_identical_to_v01": all(x == 0 for x in c["other_rooms_unchanged_vs_v01"].values()),
        "P1_pixelorama_split_layers_exact": bool(p) and all(x["split"]["exit"] == 0 and all(x["split"]["layers_exact"].values()) and x["source_unchanged_by_cli"]
                                                            for k, x in p.items() if isinstance(x, dict)),
        "P2_pixelorama_opaque_flat_exports_exact": bool(p) and all(p[f"{n}.{e}"]["flat"]["exact"] for n in ("scene", "foreground") for e in ("pxo", "ora")),
        "P3_pixelorama_real_appdata_untouched": bool(p) and not p["real_appdata_pixelorama_changed"],
    }
    rep["gates"] = gates
    rep["report_only_fixture_flat_export_exact"] = {k: x["flat"]["exact"] for k, x in p.items() if isinstance(x, dict) and not k.startswith(("scene.", "foreground."))}
    rep["result"] = "PASS" if all(gates.values()) else "FAIL"
    text = json.dumps(rep, indent=1, ensure_ascii=False)
    if a.report:
        Path(a.report).write_text(text + "\n", encoding="utf-8")
    print(text)
    print("GATES", sum(gates.values()), "/", len(gates), rep["result"])
    return 0 if rep["result"] == "PASS" else 1


author_mod = None

if __name__ == "__main__":
    sys.exit(main())
