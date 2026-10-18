"""Pixel, source, Pixelorama and regression gates for the Yonkers antenna corridor room 1 v03 candidate.

Usage: python -I <this file> [--pixelorama <exe>] [--wdc-captures <dir>] [--report <json>]
Reads the v03 manifest/sources/runtime PNGs, the v03 Godot captures and Godot check log, the accepted-room
replay captures, and (optionally) a fresh WDC v02 capture run. Pixelorama runs with APPDATA pointed at a
fresh temp dir; the real %APPDATA%/pixelorama is snapshotted before and after.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261017-224447-15709be4"
OUT = ROOT / "outputs" / "yonkers-room1-v03_15709be4"
CAP = OUT / "captures"
REPLAY = OUT / "acc"  # short: replay names are ~138 chars and outputs/ paths hit MAX_PATH
AUTHOR = ROOT / f"tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-scene-author_unapproved-v03_{STAMP}.py"
MANIFEST = OUT / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-scene-manifest_unapproved-v03_{STAMP}.json"
LOG = OUT / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-check-log_unapproved-v03_{STAMP}.txt"
V01_EN = ROOT / "outputs/yonkers-room1-antenna-pilot/after/rpg-2-star-ocean-the-second_yonkers-antenna-room1_three-antenna-fixtures-godot-en-start-640x360_v01_20261017-024526-d6f2a815.png"
ACCEPTED = [
    ROOT / "outputs/room1-visual-review", "011400-d3590c0a",
    ROOT / "outputs/room2-fixtures-pilot", "010418-6b3138d8",
    ROOT / "outputs/yonkers-room2-visual-review", "011814-94cebca4",
]
WDC_STORED = ROOT / "outputs/wdc-sr1-v02_71300729/captures"
MARKERS = [(163, 228), (320, 228), (477, 228)]
EXIT, NEXT = (57, 257), (580, 257)
# v03 must keep v02's layout and behaviour exactly: compare against v02's Godot log and runtime constants.
V02_LOG = ROOT / "outputs/yonkers-room1-v02_c1f6a38e/rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-check-log_unapproved-v02_20261017-184816-c1f6a38e.txt"
V02_MANIFEST = ROOT / "outputs/yonkers-room1-v02_c1f6a38e/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-scene-manifest_unapproved-v02_20261017-184816-c1f6a38e.json"
SURVEY = ROOT / "game/scripts/survey_annex.gd"
LAYOUT_LITERALS = [
    "const YONKERS_ANTENNA_BASE_Y := 210.0",
    "const YONKERS_ROOM_ONE_MARKERS := [Vector2(163, 228), Vector2(320, 228), Vector2(477, 228)]",
    "\tRect2(0, 0, 640, 166), Rect2(0, 166, 38, 70), Rect2(602, 166, 38, 70), Rect2(0, 281, 640, 79),",
    "\tRect2(42, 160, 58, 26), Rect2(124, 186, 68, 26), Rect2(290, 166, 72, 46), Rect2(443, 186, 80, 26),",
    "\tRect2(428, 199, 14, 12), Rect2(524, 199, 14, 12), Rect2(494, 166, 14, 8), Rect2(224, 166, 34, 20), Rect2(380, 166, 34, 16),",
    "const CLUE_POSITIONS := [Vector2(163, 165), Vector2(320, 165), Vector2(477, 165)]",
    "const EXIT_POSITION := Vector2(57, 257)",
    "const NEXT_POSITION := Vector2(580, 257)",
    "\t\tantenna.offset = Vector2(-64, -YONKERS_ANTENNA_BASE_Y + 58)",
    "\thero.offset = Vector2(0, -20)",
    "\thero.position = Vector2(87, 261)",
    "(yonkers_room_one and hero.position.distance_to(YONKERS_ROOM_ONE_MARKERS[index]) < 42.0)",
]
# Accepted interiors (NYC rooms 1 and 2, Yonkers room 2): their art must be byte-identical to HEAD.
ACCEPTED_ASSET_PATHS = [
    "game/assets/props/nyc-public-facilities-room1", "game/assets/props/nyc-public-facilities-room2",
    "game/assets/props/yonkers-maintenance-room2",
    "game/assets/environments/rpg-2-star-ocean-the-second_scifi-survey-annex-room-01_environment-background_m8-concept_20261014-142350-f2ab83d1.png",
    "game/assets/environments/rpg-2-star-ocean-the-second_scifi-survey-annex-room-02_environment-background_m8-concept_20261014-142926-e2e661fc.png",
    "game/assets/environments/rpg-2-star-ocean-the-second_scifi-outskirts-survey-annex-room-02_environment-background_m8-concept_20261014-143030-3784c1e2.png",
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rgba(path):
    return np.array(Image.open(path).convert("RGBA"))


def load_author():
    spec = importlib.util.spec_from_file_location("yk1v03_author", AUTHOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cap(lang, label):
    return CAP / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_v03-godot-{lang}-{label}-640x360_{STAMP}.png"


# ----------------------------------------------------------------------------- S: sources and runtime exports
def source_checks(A, manifest):
    rep = {}
    layers = A.build_scene()
    arrs = [l.a for l in layers]
    rep["layer_count"] = len(arrs)
    rep["binary_alpha"] = all(set(np.unique(a[..., 3]).tolist()) <= {0, 255} for a in arrs)
    pal = set(A.RGB.values())
    rep["palette_size"] = len(pal)
    rep["all_pixels_in_palette"] = all({tuple(int(v) for v in c) for c in a[a[..., 3] == 255][:, :3]} <= pal for a in arrs)
    hashes = {}
    for key, item in manifest["editable_sources"].items():
        hashes[key] = sha((ROOT / item["file"]).read_bytes()) == item["sha256"]
    rt = manifest["runtime_exports"]
    for key in ("plate", "foreground"):
        hashes[key] = sha((ROOT / rt[key]["file"]).read_bytes()) == rt[key]["sha256"]
    for item in rt["antennas"]:
        hashes[item["layer"]] = sha((ROOT / item["runtime_png"]["file"]).read_bytes()) == item["runtime_png"]["sha256"]
    rep["manifest_hashes_match"] = hashes
    plate = A.composite(layers[:9])
    exports = {"plate": rgba(ROOT / rt["plate"]["file"]).tobytes() == plate.tobytes(),
               "foreground": rgba(ROOT / rt["foreground"]["file"]).tobytes() == arrs[12].tobytes()}
    for i, item in enumerate(rt["antennas"]):
        x, y, w, h = item["crop_from_layer_xywh"]
        exports[item["layer"]] = rgba(ROOT / item["runtime_png"]["file"]).tobytes() == np.ascontiguousarray(arrs[9 + i][y:y + h, x:x + w]).tobytes()
        outside = arrs[9 + i].copy()
        outside[y:y + h, x:x + w] = 0
        exports[item["layer"] + "_nothing_outside_crop"] = not outside[..., 3].any()
    rep["runtime_exports_equal_layers"] = exports
    rep["plate_opaque"] = bool((plate[..., 3] == 255).all())
    # ORA stack order and merged image
    import zipfile
    with zipfile.ZipFile(ROOT / manifest["editable_sources"]["ora"]["file"]) as z:
        stack = z.read("stack.xml").decode()
        names = re.findall(r'name="([^"]+)" src=', stack)
        merged = np.array(Image.open(__import__("io").BytesIO(z.read("mergedimage.png"))).convert("RGBA"))
    rep["ora_layers_top_first"] = names == list(reversed(A.SCENE_LAYERS))
    rep["ora_merged_equals_composite"] = merged.tobytes() == A.composite(layers).tobytes()
    with zipfile.ZipFile(ROOT / manifest["editable_sources"]["pxo"]["file"]) as z:
        data = json.loads(z.read("data.json"))
        rep["pxo_layers_bottom_first"] = [l["name"] for l in data["layers"]] == A.SCENE_LAYERS
        rep["pxo_size"] = [data["size_x"], data["size_y"]]
        rep["pxo_layer_bytes_exact"] = all(z.read(f"image_data/frames/1/layer_{i + 1}") == arrs[i].tobytes() for i in range(len(arrs)))
    return rep, layers


# ----------------------------------------------------------------------------- P: Pixelorama CLI
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


def pixelorama_checks(exe, A, layers, manifest):
    rep = {}
    before = real_pixelorama_snapshot()
    tmp = tempfile.mkdtemp(prefix="wb-yk1v03-pxo-")
    flat = A.composite(layers).astype(np.int16)
    try:
        for ext in ("pxo", "ora"):
            src = os.path.join(tmp, f"scene.{ext}")
            shutil.copyfile(ROOT / manifest["editable_sources"][ext]["file"], src)
            r = {}
            for mode in ("split", "flat"):
                appdata = os.path.join(tmp, f"app-{ext}-{mode}")
                od = os.path.join(tmp, f"out-{ext}-{mode}")
                os.makedirs(appdata)
                os.makedirs(od)
                args = ["--export"] + (["--split-layers"] if mode == "split" else []) + ["-o", os.path.join(od, "f.png"), src]
                p = run_pixelorama(exe, args, appdata)
                outs = sorted(os.listdir(od))
                if mode == "split":
                    exact = {}
                    for n, lay in zip(A.SCENE_LAYERS, layers):
                        hit = [o for o in outs if f"({n})" in o]
                        exact[n] = len(hit) == 1 and rgba(os.path.join(od, hit[0])).tobytes() == lay.a.tobytes()
                    r["split"] = {"exit": p.returncode, "pngs": len(outs), "layers_exact": exact}
                else:
                    got = rgba(os.path.join(od, outs[0])).astype(np.int16) if len(outs) == 1 else None
                    r["flat"] = {"exit": p.returncode, "pngs": len(outs), "exact": got is not None and got.tobytes() == flat.tobytes(),
                                 "differing_texels": int((got != flat).any(axis=2).sum()) if got is not None else None}
            r["source_unchanged_by_cli"] = open(src, "rb").read() == (ROOT / manifest["editable_sources"][ext]["file"]).read_bytes()
            rep[ext] = r
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    after = real_pixelorama_snapshot()
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    gui = [k for k in changed if k.startswith("backups/") and "/(untitled backup)-" in k]
    rep["real_appdata_gui_autosave_changes_excluded"] = gui
    rep["real_appdata_pixelorama_changed"] = [k for k in changed if k not in gui]
    return rep


# ----------------------------------------------------------------------------- C: captures
def disc(mask, c, r):
    yy, xx = np.ogrid[:360, :640]
    mask |= (xx - c[0]) ** 2 + (yy - c[1]) ** 2 <= r * r


def box(mask, x0, y0, x1, y1):
    mask[max(y0, 0):min(y1, 360), max(x0, 0):min(x1, 640)] = True


def caption_rects(log_text, lang):
    rects = []
    for m in re.finditer(rf"YK1_V03_CAPTION_{lang} \d '[^']*' rect=\[P: \(([\d.]+), ([\d.]+)\), S: \(([\d.]+), ([\d.]+)\)\]", log_text):
        x, y, w, h = (float(v) for v in m.groups())
        rects.append((int(x) - 3, int(y) - 3, int(x + w) + 3, int(y + h) + 3))
    return rects


def capture_checks(A, layers, log_text):
    rep = {}
    flat = A.composite(layers)
    for lang in ("zh", "en"):
        img = rgba(cap(lang, "entry"))
        ui = np.zeros((360, 640), bool)
        box(ui, 0, 0, 640, 62)
        box(ui, 0, 318, 640, 360)
        for c in MARKERS + [EXIT, NEXT]:
            disc(ui, c, 17)
        for r in caption_rects(log_text, lang):
            box(ui, *r)
        box(ui, 10, 200, 112, 224)   # exit caption
        box(ui, 538, 200, 628, 224)  # next caption
        box(ui, 87 - 22, 261 - 56, 87 + 22, 261 + 8)  # reference heroine
        cmp = ~ui
        same = (img[..., :3] == flat[..., :3]).all(axis=2)
        antenna_px = np.zeros((360, 640), bool)
        for i in range(3):
            antenna_px |= layers[9 + i].a[..., 3] == 255
        rep[f"{lang}_entry_scene_exact_outside_ui"] = {"compared": int(cmp.sum()), "differing": int((cmp & ~same).sum()),
                                                      "antenna_texels_compared": int((cmp & antenna_px).sum()),
                                                      "antenna_texels_differing": int((cmp & antenna_px & ~same).sum())}
    # English header: nothing bright reaches the right viewport edge (v01 had text at x=639).
    def right_text_x(path):
        a = rgba(path)[8:54, :, :3].astype(int)
        bright = a.sum(axis=2) > 450
        xs = np.nonzero(bright.any(axis=0))[0]
        return int(xs.max()) if len(xs) else -1
    rep["en_header_rightmost_bright_x_v03"] = right_text_x(cap("en", "entry"))
    rep["en_header_rightmost_bright_x_v01"] = right_text_x(V01_EN) if V01_EN.exists() else None
    # All capture files present and 640x360.
    names = sorted(p.name for p in CAP.glob("*.png"))
    rep["capture_count"] = len(names)
    rep["captures_640x360"] = all(Image.open(CAP / n).size == (640, 360) for n in names)
    langs = {"zh": [n for n in names if "-godot-zh-" in n], "en": [n for n in names if "-godot-en-" in n]}
    kinds = ["entry", "approach-a", "approach-b", "approach-c", "interact", "b-dish-from-lane", "occlusion-behind-a",
             "occlusion-behind-c", "returned-from-room2", "traversal"]
    rep["kinds_by_language"] = {lang: {k: sum(1 for n in v if f"-{k}" in n) for k in kinds} for lang, v in langs.items()}
    return rep


# ----------------------------------------------------------------------------- R: regressions
def accepted_replay():
    rep = {}
    for folder, tag in zip(ACCEPTED[0::2], ACCEPTED[1::2]):
        for ref in sorted(folder.glob(f"*_20261017-{tag}.png")):
            stem = ref.name[: -len(f"_20261017-{tag}.png")]
            got = REPLAY / f"{stem}_{STAMP}.png"
            if not got.exists():
                rep[ref.name] = "missing replay"
                continue
            a, b = rgba(ref), rgba(got)
            rep[ref.name] = int((a != b).any(axis=2).sum())
    return rep


def wdc_replay(folder):
    rep = {}
    if folder is None or not Path(folder).is_dir():
        return {"skipped": True}
    for ref in sorted(WDC_STORED.glob("*.png")):
        label = re.sub(r"_20261017-160235-[0-9a-f]+\.png$", "", ref.name)
        hit = [p for p in Path(folder).glob("*.png") if re.sub(r"_20261017-160235-[0-9a-f]+\.png$", "", p.name) == label]
        if not hit:
            rep[label] = "missing"
            continue
        rep[label] = int((rgba(ref) != rgba(hit[0])).any(axis=2).sum())
    return rep


def log_checks(text):
    want = ["YK1_V03_ROOM1_INTERACTIONS_OK", "YK1_V03_LANE_WALK_OK", "YK1_V03_SLIDE_OK", "YK1_V03_ESCAPE_OK", "YK1_V03_REACHABILITY_OK",
            "YK1_V03_TRANSITION_NEXT_OK", "YK1_V03_ALL_SIX_CLUES_OK 6/6", "YK1_V03_TRANSITION_BACK_OK", "YK1_V03_TRANSITION_EXIT_OK",
            "YK1_V03_ISOLATION_OK", "YK1_V03_ALL_OK"]
    rep = {w: w in text for w in want}
    rep["collision_cases"] = len(re.findall(r"YK1_V03_COLLISION ", text))
    rep["depth_lines"] = re.findall(r"YK1_V03_DEPTH .*", text)
    rep["script_errors"] = text.count("SCRIPT ERROR")
    rep["fail_lines"] = text.count("YK1_V03_FAIL")
    return rep


def hud_checks(manifest, log_text):
    rows = manifest["hud_clearance"]["top_texel_row"]
    lines = re.findall(r"YK1_V03_HUD_CLEAR antenna=(\d) top_screen_y=(\d+) texels_under_header=(\d+)", log_text)
    return {"manifest_top_texel_rows": rows, "godot_top_screen_y": {i: int(y) for i, y, _ in lines},
            "godot_texels_under_header": {i: int(n) for i, _, n in lines},
            "ok": len(lines) == 3 and all(int(y) >= 66 and int(n) == 0 for _, y, n in lines) and all(v >= 66 for v in rows.values())}


def layout_checks(log_text):
    """v03 is an art pass only: runtime layout constants unchanged, and every v02 behaviour number reproduced."""
    src = SURVEY.read_text(encoding="utf-8")
    rep = {"layout_literals_present": {lit.strip()[:60]: lit in src for lit in LAYOUT_LITERALS}}
    v02 = V02_LOG.read_text(encoding="utf-8", errors="replace")

    def coll(text, tag):
        return {m.group(1): (float(m.group(2)), float(m.group(3))) for m in re.finditer(rf"{tag}_COLLISION (\S+) -> \(([\d.]+), ([\d.]+)\)", text)}
    c2, c3 = coll(v02, "YK1_V02"), coll(log_text, "YK1_V03")
    rep["collision_cases_v02_v03"] = [len(c2), len(c3)]
    rep["collision_max_abs_delta_px"] = max(max(abs(c2[k][0] - c3[k][0]), abs(c2[k][1] - c3[k][1])) for k in c2) if c2.keys() == c3.keys() else None

    def cells(text, tag):
        m = re.search(rf"{tag}_REACHABILITY_OK cells=(\d+)", text)
        return int(m.group(1)) if m else None
    rep["reachable_cells_v02_v03"] = [cells(v02, "YK1_V02"), cells(log_text, "YK1_V03")]
    v02m = json.loads(V02_MANIFEST.read_text(encoding="utf-8"))
    rep["runtime_layout_text_equal_v02"] = None  # filled by caller with the v03 manifest
    rep["_v02_runtime_layout"] = v02m["runtime_layout"]
    rep["_v02_antenna_boxes"] = [(a["crop_from_layer_xywh"], a["anchor"]) for a in v02m["runtime_exports"]["antennas"]]
    return rep


def accepted_assets_unchanged():
    p = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--"] + ACCEPTED_ASSET_PATHS, capture_output=True, text=True)
    return {"exit": p.returncode, "changed": [l for l in p.stdout.splitlines() if l.strip()]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pixelorama", default=str(ROOT / "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"))
    ap.add_argument("--wdc-captures", default=None)
    ap.add_argument("--report", default=str(OUT / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_pixel-source-pixelorama-check-report_unapproved-v03_{STAMP}.json"))
    a = ap.parse_args()
    A = load_author()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    log_text = LOG.read_text(encoding="utf-8", errors="replace")
    rep = {"tool": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), "status": "UNAPPROVED candidate"}
    rep["sources"], layers = source_checks(A, manifest)
    rep["pixelorama_cli"] = pixelorama_checks(a.pixelorama, A, layers, manifest) if os.path.isfile(a.pixelorama) else {"skipped": True}
    rep["captures"] = capture_checks(A, layers, log_text)
    rep["godot_log"] = log_checks(log_text)
    rep["accepted_rooms_replay_differing_px"] = accepted_replay()
    rep["wdc_room1_v02_replay_differing_px"] = wdc_replay(a.wdc_captures)
    rep["hud"] = hud_checks(manifest, log_text)
    lay = layout_checks(log_text)
    lay["runtime_layout_text_equal_v02"] = manifest["runtime_layout"] == lay.pop("_v02_runtime_layout")
    lay["antenna_boxes_equal_v02"] = [(a_["crop_from_layer_xywh"], a_["anchor"]) for a_ in manifest["runtime_exports"]["antennas"]] == lay.pop("_v02_antenna_boxes")
    rep["layout_vs_v02"] = lay
    rep["accepted_assets_vs_head"] = accepted_assets_unchanged()
    s, p, c, g = rep["sources"], rep["pixelorama_cli"], rep["captures"], rep["godot_log"]
    acc = rep["accepted_rooms_replay_differing_px"]
    wdc = rep["wdc_room1_v02_replay_differing_px"]
    gates = {
        "S1_binary_alpha_palette_13_layers": s["binary_alpha"] and s["all_pixels_in_palette"] and s["layer_count"] == 13,
        "S2_manifest_hashes": all(s["manifest_hashes_match"].values()),
        "S3_runtime_exports_equal_layers": all(s["runtime_exports_equal_layers"].values()) and s["plate_opaque"],
        "S4_ora_pxo_structure": s["ora_layers_top_first"] and s["ora_merged_equals_composite"] and s["pxo_layers_bottom_first"] and s["pxo_layer_bytes_exact"],
        "P1_pixelorama_split_layers_exact": not p.get("skipped") and all(p[e]["split"]["exit"] == 0 and all(p[e]["split"]["layers_exact"].values()) and p[e]["source_unchanged_by_cli"] for e in ("pxo", "ora")),
        "P2_pixelorama_flat_exact": not p.get("skipped") and all(p[e]["flat"]["exact"] for e in ("pxo", "ora")),
        "P3_real_appdata_untouched": not p.get("skipped") and not p["real_appdata_pixelorama_changed"],
        "C1_entry_scene_exact_outside_ui": all(c[f"{l}_entry_scene_exact_outside_ui"]["differing"] == 0 and c[f"{l}_entry_scene_exact_outside_ui"]["antenna_texels_compared"] > 5000 for l in ("zh", "en")),
        "C2_en_header_not_clipped": 0 <= c["en_header_rightmost_bright_x_v03"] <= 630,
        "C3_capture_set_zh_en": c["captures_640x360"] and all(all(v > 0 for v in kinds.values()) for kinds in c["kinds_by_language"].values()),
        "G1_godot_checks": all(v for k, v in g.items() if k.startswith("YK1_V03_")) and g["collision_cases"] >= 14 and g["script_errors"] == 0 and g["fail_lines"] == 0,
        "R1_accepted_rooms_0px": len(acc) == 8 and all(v == 0 for v in acc.values()),
        "R2_wdc_room1_v02_unchanged_except_outskirts_room1": not wdc.get("skipped") and all(v == 0 for k, v in wdc.items() if "other-outskirts-room1" not in k),
        "R3_accepted_room_assets_equal_head": rep["accepted_assets_vs_head"]["exit"] == 0 and not rep["accepted_assets_vs_head"]["changed"],
        "H1_antenna_tips_below_hud": rep["hud"]["ok"],
        "L1_layout_and_behaviour_equal_v02": all(lay["layout_literals_present"].values()) and lay["runtime_layout_text_equal_v02"]
            and lay["antenna_boxes_equal_v02"] and lay["collision_cases_v02_v03"] == [14, 14]
            and lay["collision_max_abs_delta_px"] is not None and lay["collision_max_abs_delta_px"] < 0.05
            and lay["reachable_cells_v02_v03"][0] == lay["reachable_cells_v02_v03"][1] is not None,
    }
    rep["gates"] = gates
    rep["gates_passed"] = f"{sum(gates.values())}/{len(gates)}"
    Path(a.report).write_text(json.dumps(rep, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for k, v in gates.items():
        print(("PASS " if v else "FAIL ") + k)
    print("GATES", rep["gates_passed"], a.report)


if __name__ == "__main__":
    main()
