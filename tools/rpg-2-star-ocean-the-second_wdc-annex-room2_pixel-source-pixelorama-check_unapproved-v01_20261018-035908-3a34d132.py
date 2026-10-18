"""Exact source, pixel, occlusion, default-off, accepted-room and Pixelorama checks for the UNAPPROVED v01
Washington survey annex room 2 (records chamber) fixture integration (`-- --wdc-records-chamber-v01`).

Usage: python -I <this file> --captures <dir> --probes <dir> --parity <dir> --replay <dir>
                                 [--pixelorama <exe>] [--report <json>] [--deps <json>]
- captures/probes: output of tools/...wdc-annex-room2_godot-capture-and-check_unapproved-v01_20261018-001157-151fb8d0.gd
  run WITH the opt-in flag (probes are the same frames with the heroine hidden);
- parity: output of the same tool run WITHOUT the flag in `--default-off-parity` mode (D1 r1, 2026-10-18: zh 0 px,
  en may differ from HEAD only in the 62-row header, the intentional c3ff819c default layout fix);
- replay: output of tools/...wdc-annex-room1_v02-review-gate-accepted-rooms-replay_check-v01_20261017-172907-03286bf3.gd.
Pixelorama runs headless with a temporary APPDATA per call; the real Pixelorama APPDATA is snapshotted before and
after. This only exercises the CLI loader/exporter: it is NOT a GUI Save As / reopen check. A missing executable
fails the Pixelorama gates rather than skipping them.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import glob
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = ROOT / "tools/rpg-2-star-ocean-the-second_wdc-annex-room2_records-chamber-fixtures-author_unapproved-v01_20261018-001157-151fb8d0.py"
GODOT_TOOL = ROOT / "tools/rpg-2-star-ocean-the-second_wdc-annex-room2_godot-capture-and-check_unapproved-v01_20261018-001157-151fb8d0.gd"
REPLAY_TOOL = ROOT / "tools/rpg-2-star-ocean-the-second_wdc-annex-room1_v02-review-gate-accepted-rooms-replay_check-v01_20261017-172907-03286bf3.gd"
SCRIPT = ROOT / "game/scripts/survey_annex.gd"
CONTENT = ROOT / "game/scripts/survey_content.gd"
SCENE = ROOT / "game/scenes/survey_annex.tscn"
HERO_REF = ROOT / "game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png"
CLUES = [(163, 165), (320, 165), (477, 165)]
TERMINAL = (320, 263)
# Acceptance-record images of the three accepted rooms (NYC room 1, NYC room 2, Yonkers room 2).
ACCEPTED = {
    "nyc-public-facilities-room1_existing-scene-godot-%s-640x360-review-v01": ("outputs/room1-visual-review", "20261017-011400-d3590c0a", ("zh", "en")),
    "nyc-public-facilities-room2_three-pixel-fixtures-godot-%s-640x360_unapproved-v01": ("outputs/room2-fixtures-pilot", "20261017-010418-6b3138d8", ("zh", "en")),
    "nyc-public-facilities-room2_repair-manual-approach-godot-%s-640x360_unapproved-v01": ("outputs/room2-fixtures-pilot", "20261017-010418-6b3138d8", ("zh",)),
    "nyc-public-facilities-room2_repair-manual-interaction-godot-%s-640x360_unapproved-v01": ("outputs/room2-fixtures-pilot", "20261017-010418-6b3138d8", ("zh",)),
    "yonkers-maintenance-room2_four-pixel-fixtures-godot-%s-640x360-review-v01": ("outputs/yonkers-room2-visual-review", "20261017-011814-94cebca4", ("zh", "en")),
}


def load_author():
    spec = spec_from_file_location("wdc_room2_author_v01", AUTHOR)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rgba(src):
    if isinstance(src, bytes):
        src = io.BytesIO(src)
    return np.array(Image.open(src).convert("RGBA"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sha_text(path):
    return sha(Path(path).read_bytes().replace(b"\r\n", b"\n"))


def one(folder, pattern):
    hits = glob.glob(os.path.join(folder, pattern))
    if len(hits) != 1:
        raise SystemExit(f"expected one {pattern} in {folder}, got {hits}")
    return hits[0]


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT)] + list(args), capture_output=True, text=True).stdout.strip()


def rel(p):
    return str(Path(p).resolve().relative_to(ROOT)).replace("\\", "/")


# ---------------------------------------------------------------- sources

def check_asset(item, names, layers):
    flat_img = author_mod.merged(layers)
    flat = np.array(flat_img)
    files = {ext: (ROOT / item["files"][ext]["file"]).read_bytes() for ext in ("png", "ora", "pxo")}
    runtime = (ROOT / item["runtime_png"]["file"]).read_bytes()
    stem = Path(item["files"]["png"]["file"]).stem
    export_name = "wdc-annex-room2-v01-" + stem.split("_wdc-annex-room2_")[1].split("-pixel-fixture")[0]
    rebuilt = {"png": author_mod.png_bytes(flat_img), "ora": author_mod.ora_bytes(stem, names, layers, flat_img),
               "pxo": author_mod.pxo_bytes(export_name, names, layers, flat_img, author_mod.palette_hex())}
    r = {"hashes_match_manifest": all(sha(files[e]) == item["files"][e]["sha256"] for e in files) and sha(runtime) == item["runtime_png"]["sha256"],
         "runtime_png_equals_source_png": runtime == files["png"],
         "rebuild_byte_identical": {e: rebuilt[e] == files[e] for e in files},
         "png_equals_rebuilt_layers": rgba(files["png"]).tobytes() == flat.tobytes(),
         "size": list(flat_img.size)}
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
        r["pxo_layers_bottom_to_top"] = [l["name"] for l in data["layers"]]
        r["pxo_layers_exact"] = all(z.read(f"image_data/frames/1/layer_{i}") == img.tobytes() for i, img in enumerate(layers, start=1))
    alpha = flat[..., 3]
    shadow = np.array(layers[0])[..., 3] > 0
    r["opaque_texels"] = int((alpha == 255).sum())
    r["only_semi_alpha_is_contact_shadow"] = bool((((alpha > 0) & (alpha < 255)) <= shadow).all())
    r["exact"] = all([r["hashes_match_manifest"], r["runtime_png_equals_source_png"], all(r["rebuild_byte_identical"].values()),
                      r["png_equals_rebuilt_layers"], r["ora_mimetype_first_stored"], r["ora_layers_exact"], r["ora_merged_exact"],
                      r["pxo_layers_exact"], r["pxo_layers_bottom_to_top"] == names, r["ora_layers_top_to_bottom"] == list(reversed(names)),
                      r["pxo_version"] == 7])
    return r, flat


def runtime_constants():
    text = SCRIPT.read_text(encoding="utf-8")
    block = re.search(r"const WDC_ROOM_TWO_BLOCKERS := \[(.*?)\n\]", text, re.S).group(1)
    rects = [[int(float(v)) for v in m.split(",")] for m in re.findall(r"Rect2\(([^)]*)\)", block)]
    num = lambda name: float(re.search(rf"const {name} := ([0-9.]+)", text).group(1))
    origin = [int(v) for v in re.search(r"const WDC_ROOM_TWO_TERMINAL_ORIGIN := Vector2\((\d+), (\d+)\)", text).groups()]
    preloads = re.findall(r'preload\("res://(assets/props/wdc-annex-room2/[^"]+)"\)', text)
    return {"blockers": rects, "fixture_top": num("WDC_ROOM_TWO_FIXTURE_TOP"), "sort_y": num("WDC_ROOM_TWO_SORT_Y"),
            "terminal_origin": origin, "preloads": preloads, "flag_gate": 'OS.get_cmdline_user_args().has(WDC_ROOM_TWO_FLAG)' in text}


def source_checks(manifest):
    A = author_mod
    rep = {"fixtures": {}}
    arrays = {}
    for (slug, fn, _, _), item in zip(A.FIXTURES, manifest["fixtures"]):
        r, flat = check_asset(item, A.CLUE_LAYERS, [Image.fromarray(l) for l in fn()])
        rep["fixtures"][slug] = r
        arrays[slug] = (flat, tuple(item["placement"]["origin"]))
    slug, fn, _ = A.TERMINAL_ITEM
    r, flat = check_asset(manifest["terminal"], A.TERMINAL_LAYERS, [Image.fromarray(l) for l in fn()])
    rep["fixtures"][slug] = r
    arrays[slug] = (flat, tuple(manifest["terminal"]["placement"]["origin"]))
    rt = runtime_constants()
    man_blockers = [f["placement"]["blocker"] for f in manifest["fixtures"]] + [manifest["terminal"]["placement"]["blocker"]]
    rep["runtime_constants"] = rt
    rep["runtime_matches_manifest"] = (rt["blockers"][1:5] == man_blockers and rt["blockers"][0] == [0, 0, 640, 114]
                                       and rt["fixture_top"] == 164 and rt["sort_y"] == manifest["runtime"]["clue_sort_y"]
                                       and rt["terminal_origin"] == manifest["terminal"]["placement"]["origin"]
                                       and sorted(Path(p).name for p in rt["preloads"]) == sorted(Path(item["runtime_png"]["file"]).name for item in manifest["fixtures"] + [manifest["terminal"]]))
    rep["placements_rebuild_equal_manifest"] = A.placements() == [f["placement"] for f in manifest["fixtures"]] + [manifest["terminal"]["placement"]]
    rep["background_hash_matches_manifest"] = sha((ROOT / A.BACKGROUND).read_bytes()) == manifest["background_sha256"]
    head_content = subprocess.run(["git", "-C", str(ROOT), "show", "HEAD:game/scripts/survey_content.gd"], capture_output=True).stdout
    rep["clue_text_file_identical_to_head"] = head_content.replace(b"\r\n", b"\n") == CONTENT.read_bytes().replace(b"\r\n", b"\n")
    return rep, arrays


# ---------------------------------------------------------------- captures

def fixture_mask(arrays, which, opaque_only=True):
    m = np.zeros((360, 640), bool)
    for slug in which:
        flat, (ox, oy) = arrays[slug]
        a = flat[..., 3] == 255 if opaque_only else flat[..., 3] > 0
        h, w = a.shape
        m[oy:oy + h, ox:ox + w] |= a
    return m


def disc_mask(center, radius=17):
    yy, xx = np.mgrid[0:360, 0:640]
    return (xx - center[0]) ** 2 + (yy - center[1]) ** 2 <= radius ** 2


def box_mask(x, y):
    m = np.zeros((360, 640), bool)
    m[max(0, y - 50):y + 11, max(0, x - 28):x + 29] = True
    return m


def expected_fixture_canvas(arrays):
    exp = np.zeros((360, 640, 4), np.uint8)
    for flat, (ox, oy) in arrays.values():
        h, w = flat.shape[:2]
        exp[oy:oy + h, ox:ox + w][flat[..., 3] == 255] = flat[flat[..., 3] == 255]
    return exp


def capture_checks(cap, probes, arrays):
    slugs = list(arrays)
    opaque = fixture_mask(arrays, slugs)
    opaque_checked = opaque & ~disc_mask(TERMINAL)  # the terminal disc overlaps the table's top two rows
    exp = expected_fixture_canvas(arrays)
    shots = {}
    files = sorted(glob.glob(os.path.join(cap, "*_v01-godot-*-640x360_*.png")))
    rep = {"capture_count": len(files), "all_640x360": all(Image.open(f).size == (640, 360) for f in files)}
    with open(os.path.join(probes, "godot-check-results.json"), encoding="utf-8") as fh:
        godot = json.load(fh)
    rep["godot_results_ok"] = godot.get("ok") is True and "failed" not in godot
    positions = {"entry": (87, 261), "terminal-approach": (320, 268)}
    for i in range(3):
        positions[f"front-clue-{i + 3}"] = (CLUES[i][0], 230)
        positions[f"occlusion-behind-clue-{i + 3}"] = (CLUES[i][0] - 28, 196)
    for path in glob.glob(os.path.join(probes, "probe-hidden-hero_*.png")):
        lang, label = Path(path).stem[len("probe-hidden-hero_"):].split("_", 1)
        shot = rgba(one(cap, f"*_v01-godot-{lang}-{label}-640x360_*.png"))
        hidden = rgba(path)
        diff = (shot != hidden).any(axis=2)
        hx, hy = positions[label]
        r = {"opaque_fixture_texels_checked": int(opaque_checked.sum()),
             "opaque_fixture_texels_exact_in_hidden_frame": int(((hidden == exp).all(axis=2) & opaque_checked).sum()),
             "hero_changed_pixels": int(diff.sum()),
             "changes_outside_hero_box": int((diff & ~box_mask(hx, hy)).sum())}
        if label.startswith(("front-clue-", "occlusion-behind-clue-")):
            idx = int(label[-1]) - 3
            own = fixture_mask(arrays, [slugs[idx]])
            r["hero_pixels_over_own_fixture"] = int((diff & own).sum())
            r["own_fixture_texels_in_hero_box"] = int((own & box_mask(hx, hy)).sum())
            if label.startswith("occlusion"):
                r["fixture_texels_exact_over_hero"] = int(((shot == exp).all(axis=2) & own & box_mask(hx, hy)).sum())
        if label == "terminal-approach":
            r["hero_pixels_over_table"] = int((diff & fixture_mask(arrays, [slugs[3]], opaque_only=False)).sum())
        shots[f"{lang}-{label}"] = r
    rep["shots"] = shots
    needed = ["entry", "front-clue-3", "front-clue-4", "front-clue-5", "occlusion-behind-clue-3", "occlusion-behind-clue-4",
              "occlusion-behind-clue-5", "interaction-clue-3", "interaction-clue-4", "interaction-clue-5",
              "interaction-terminal-locked", "door-entry-from-room1", "after-load"]
    rep["bilingual_set_missing"] = [f"{l}-{n}" for n in needed for l in ("zh", "en") if not glob.glob(os.path.join(cap, f"*_v01-godot-{l}-{n}-640x360_*.png"))]
    rep["return_captures"] = [Path(p).name for p in sorted(glob.glob(os.path.join(cap, "*_v01-godot-*-return-room1-*.png")))]
    return rep, godot


HEADER_ROWS = 62   # r1 (2026-10-18): the c3ff819c default fix changes the Washington English header on purpose


def parity_checks(folder):
    rep = {}
    for room in (1, 2):
        for lang in ("zh", "en"):
            a = rgba(one(folder, f"*default-off-working-tree-room{room}-{lang}-640x360_*.png"))
            b = rgba(one(folder, f"*default-off-head-room{room}-{lang}-640x360_*.png"))
            diff = (a != b).any(axis=2)
            rep[f"room{room}_{lang}"] = {"pixels": int(diff.sum()), "below_header": int(diff[HEADER_ROWS:].sum())}
    return rep


def replay_checks(folder):
    rep = {}
    for name, (subdir, stamp, langs) in ACCEPTED.items():
        for lang in langs:
            n = name % lang
            ref = ROOT / subdir / f"rpg-2-star-ocean-the-second_{n}_{stamp}.png"
            got = one(folder, f"rpg-2-star-ocean-the-second_{n}_*.png")
            rep[n] = int((rgba(got) != rgba(str(ref))).any(axis=2).sum()) if ref.is_file() else "reference missing"
    return rep


# ---------------------------------------------------------------- Pixelorama CLI (load + export only)

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
                key = os.path.relpath(os.path.join(d, f), root).replace("\\", "/")
                if key != ".running":
                    snap[key] = sha(open(os.path.join(d, f), "rb").read())
    return snap


def pixelorama_checks(exe, manifest):
    A = author_mod
    rep = {}
    before = real_pixelorama_snapshot()
    tmp = tempfile.mkdtemp(prefix="wb-wdc-r2v1-pxo-")
    assets = [(slug, A.CLUE_LAYERS, [Image.fromarray(l) for l in fn()], item) for (slug, fn, _, _), item in zip(A.FIXTURES, manifest["fixtures"])]
    assets.append((A.TERMINAL_ITEM[0], A.TERMINAL_LAYERS, [Image.fromarray(l) for l in A.TERMINAL_ITEM[1]()], manifest["terminal"]))
    try:
        for slug, names, layers, item in assets:
            flat = np.array(A.merged(layers)).astype(np.int16)
            semi = (flat[..., 3] > 0) & (flat[..., 3] < 255)
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
                        for n, img in zip(names, layers):
                            hit = [o for o in outs if f"({n})" in o]
                            exact[n] = len(hit) == 1 and rgba(os.path.join(od, hit[0])).tobytes() == np.array(img).tobytes()
                        r["split"] = {"exit": p.returncode, "pngs": len(outs), "layers_exact": exact}
                    else:
                        got = rgba(os.path.join(od, outs[0])).astype(np.int16) if len(outs) == 1 else None
                        d = (got != flat).any(axis=2) if got is not None else None
                        r["flat"] = {"exit": p.returncode, "pngs": len(outs),
                                     "exact": got is not None and got.tobytes() == flat.tobytes(),
                                     "differing_texels": int(d.sum()) if d is not None else None,
                                     "differing_texels_outside_semi_alpha_shadow": int((d & ~semi).sum()) if d is not None else None,
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


# ---------------------------------------------------------------- dependency manifest

def dependency_manifest(manifest, report_path):
    tracked = set(git("ls-files").splitlines())
    modified = set(git("diff", "--name-only", "HEAD", "--").splitlines())
    entries = []

    def add(path, role, kind=None):
        p = ROOT / path
        kind = kind or ("sha256-bytes" if p.suffix in (".png", ".pxo", ".ora") else "sha256-text-lf-v1")
        digest = sha(p.read_bytes()) if kind == "sha256-bytes" else sha_text(p)
        state = "untracked" if path not in tracked else ("modified-vs-HEAD" if path in modified else "tracked-unchanged")
        entries.append({"file": path, "role": role, "hash_algorithm": kind, "sha256": digest, "git_state": state})

    add("game/scripts/survey_annex.gd", "runtime script: opt-in `--wdc-records-chamber-v01` branch (the whole working-tree diff vs HEAD is this branch)")
    add("game/scenes/survey_annex.tscn", "runtime scene (unchanged)")
    add("game/scripts/survey_content.gd", "clue text (unchanged; must equal HEAD)")
    add(rel(ROOT / author_mod.BACKGROUND), "room 2 background plate (unchanged m8-concept)")
    for item in manifest["fixtures"] + [manifest["terminal"]]:
        add(item["runtime_png"]["file"], "runtime fixture PNG (preloaded)")
        add(item["runtime_png"]["file"] + ".import", "Godot import settings for the runtime PNG")
        for ext in ("png", "ora", "pxo"):
            add(item["files"][ext]["file"], f"layered/flat source ({ext})")
    add(rel(next(Path(author_mod.OUT).glob("*records-chamber-fixtures-manifest*.json"))), "author manifest (hashes, placements, blockers)")
    add(rel(AUTHOR), "author tool (pixel-by-pixel fixtures)")
    add(rel(GODOT_TOOL), "Godot capture/check tool (real input, collision, save/load, default-off parity)")
    add(rel(REPLAY_TOOL), "accepted rooms replay (read-only use)")
    add(rel(Path(__file__)), "this check")
    add(rel(HERO_REF), "capture-only heroine reference (approved selout v8 idle; not wired by this branch)")
    dep = {"scope": "Washington survey annex room 2 records-chamber v01 (UNAPPROVED, off by default)",
           "head": git("rev-parse", "HEAD"), "upstream_main_checked": git("rev-parse", "origin/main"),
           "survey_annex_gd_head_blob": git("rev-parse", "HEAD:game/scripts/survey_annex.gd"),
           "entries": entries, "report": report_path}
    return dep


def main():
    global author_mod
    ap = argparse.ArgumentParser()
    ap.add_argument("--captures", required=True)
    ap.add_argument("--probes", required=True)
    ap.add_argument("--parity", required=True)
    ap.add_argument("--replay", required=True)
    ap.add_argument("--pixelorama", default=str(ROOT / "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"))
    ap.add_argument("--report")
    ap.add_argument("--deps")
    a = ap.parse_args()
    author_mod = load_author()
    manifest = json.loads(Path(one(str(author_mod.OUT), "*records-chamber-fixtures-manifest*.json")).read_text(encoding="utf-8"))
    src, arrays = source_checks(manifest)
    cap, godot = capture_checks(a.captures, a.probes, arrays)
    rep = {"sources": src, "captures": cap, "default_off_parity_differing_pixels": parity_checks(a.parity),
           "accepted_rooms_replay_differing_pixels": replay_checks(a.replay),
           "pixelorama_cli": pixelorama_checks(a.pixelorama, manifest) if os.path.isfile(a.pixelorama) else {"missing_executable": a.pixelorama}}
    s, c, p = rep["sources"], rep["captures"], rep["pixelorama_cli"]
    shots = c["shots"]
    front = [v for k, v in shots.items() if "-front-clue-" in k]
    occl = [v for k, v in shots.items() if "-occlusion-behind-clue-" in k]
    pxo_items = {k: v for k, v in p.items() if isinstance(v, dict)}
    gates = {
        "S1_sources_hash_rebuild_layers_exact": len(s["fixtures"]) == 4 and all(v["exact"] for v in s["fixtures"].values()),
        "S2_only_contact_shadow_is_semi_alpha": all(v["only_semi_alpha_is_contact_shadow"] for v in s["fixtures"].values()),
        "S3_runtime_constants_match_manifest": s["runtime_matches_manifest"] and s["placements_rebuild_equal_manifest"] and s["runtime_constants"]["flag_gate"],
        "S4_background_and_clue_text_unchanged": s["background_hash_matches_manifest"] and s["clue_text_file_identical_to_head"],
        "G1_godot_real_input_check_all_ok": c["godot_results_ok"],
        "C1_bilingual_640_captures_complete": c["all_640x360"] and not c["bilingual_set_missing"] and len(c["return_captures"]) == 2,
        "C2_fixtures_render_native_1to1": len(shots) == 16 and all(v["opaque_fixture_texels_exact_in_hidden_frame"] == v["opaque_fixture_texels_checked"] > 9000 for v in shots.values()),
        "C3_only_the_heroine_changes": all(v["changes_outside_hero_box"] == 0 and v["hero_changed_pixels"] > 150 for v in shots.values()),
        "C4_hero_in_front_draws_over_fixture": len(front) == 6 and all(v["hero_pixels_over_own_fixture"] > 100 for v in front),
        "C5_fixture_occludes_hero_behind": len(occl) == 6 and all(v["hero_pixels_over_own_fixture"] == 0 and v["own_fixture_texels_in_hero_box"] > 300
                                                                  and v["fixture_texels_exact_over_hero"] == v["own_fixture_texels_in_hero_box"]
                                                                  and v["hero_changed_pixels"] > 150 for v in occl),
        "C6_heroine_never_overlaps_table": all(v["hero_pixels_over_table"] == 0 for k, v in shots.items() if k.endswith("terminal-approach")),
        "D1_default_off_zh_identical_en_header_only": len(rep["default_off_parity_differing_pixels"]) == 4
            and all(v["below_header"] == 0 and (v["pixels"] == 0 or k.endswith("_en")) for k, v in rep["default_off_parity_differing_pixels"].items()),
        "D2_accepted_rooms_pixel_identical": len(rep["accepted_rooms_replay_differing_pixels"]) == 8 and all(v == 0 for v in rep["accepted_rooms_replay_differing_pixels"].values()),
        "P1_pixelorama_cli_split_layers_exact": len(pxo_items) == 8 and all(x["split"]["exit"] == 0 and all(x["split"]["layers_exact"].values()) and x["source_unchanged_by_cli"] for x in pxo_items.values()),
        "P2_pixelorama_cli_flat_exact_except_shadow_rounding": len(pxo_items) == 8 and all(x["flat"]["exit"] == 0 and x["flat"]["differing_texels_outside_semi_alpha_shadow"] == 0
                                                                                           and x["flat"]["max_channel_delta"] <= 1 for x in pxo_items.values()),
        "P3_pixelorama_real_appdata_untouched": len(pxo_items) == 8 and not p["real_appdata_pixelorama_changed"],
    }
    rep["gates"] = gates
    rep["not_checked_here"] = ["Pixelorama GUI Save As / reopen of the .pxo (CLI load+export only)", "creator visual approval"]
    rep["result"] = "PASS" if all(gates.values()) else "FAIL"
    text = json.dumps(rep, indent=1, ensure_ascii=False)
    if a.report:
        Path(a.report).write_text(text + "\n", encoding="utf-8")
    if a.deps:
        Path(a.deps).write_text(json.dumps(dependency_manifest(manifest, a.report and rel(a.report)), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)
    print("GATES", sum(gates.values()), "/", len(gates), rep["result"])
    return 0 if rep["result"] == "PASS" else 1


author_mod = None

if __name__ == "__main__":
    sys.exit(main())
