"""Source and Pixelorama gates for the Yonkers antenna corridor room 1 v05 scene-quality candidate.

Like the v04 source check, it reuses the committed v03 checker's source_checks (layers, palette, binary alpha, manifest
hashes, nonruntime exports, ORA/PXO structure) and pixelorama_checks (headless split/flat round trip with an isolated
temporary APPDATA; the real %APPDATA%/pixelorama is snapshotted before and after). v05 gates:
  G1 geometry: antenna and foreground alpha equal v04, sprite boxes/anchors/clue ids equal the v04 manifest, no antenna
     texel above y 66 (HUD), the sky and everything above y 92 unchanged (open skyline);
  G2 transitions and props: the doors layer changed only stone pixels (door opening, threshold, lamp, stair, exit plate
     and ivy are v04 pixels); the deck-detail layer changed only the conduit clamps and the rust blooms;
  G3 originals and runtime: the v04 and v03 files hash as their manifests record; survey_annex.gd still loads v03 and
     names no v04/v05 file; nothing with the v05 stamp exists under game/;
  G4 palette: the 65 v03 colours unchanged and first, additions named; the .gpl palette matches the manifest.
Godot runtime evidence is checked separately by the v05 capture/replay pixel check.

Usage: python -I <this file> [--pixelorama <exe>] [--report <json>]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261018-043851-4b9d66f1"
V03_CHECK = ROOT / "tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_pixel-source-pixelorama-check_unapproved-v03_20261017-224447-15709be4.py"
AUTHOR = ROOT / f"tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_scene-quality-refinement-author_unapproved-v05_{STAMP}.py"
OUT = ROOT / "outputs" / "yonkers-room1-v05_4b9d66f1"
MANIFEST = OUT / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_scene-quality-manifest_unapproved-v05_{STAMP}.json"
V04_MANIFEST = ROOT / "outputs/yonkers-room1-v04_523bba3b/rpg-2-star-ocean-the-second_yonkers-antenna-room1_material-depth-scene-manifest_unapproved-v04_20261018-052445-523bba3b.json"
V03_MANIFEST = ROOT / "outputs/yonkers-room1-v03_15709be4/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-scene-manifest_unapproved-v03_20261017-224447-15709be4.json"
SURVEY = ROOT / "game/scripts/survey_annex.gd"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pinned_files(m):
    files = [m["editable_sources"][k] for k in m["editable_sources"]] + [m["runtime_exports"]["plate"], m["runtime_exports"]["foreground"]]
    return files + [x["runtime_png"] for x in m["runtime_exports"]["antennas"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pixelorama", default=str(ROOT / "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"))
    ap.add_argument("--report", default=str(OUT / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_scene-quality-source-check-report_unapproved-v05_{STAMP}.json"))
    a = ap.parse_args()
    C = load("yk1v03_check", V03_CHECK)
    V5 = load("yk1v05_author", AUTHOR)
    A, V4 = V5.A, V5.V4
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rep = {"tool": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), "status": "UNAPPROVED, NONRUNTIME candidate"}
    shim = type("A", (), {"composite": A.composite, "RGB": A.RGB, "SCENE_LAYERS": A.SCENE_LAYERS})
    shim.build_scene = staticmethod(V5.build_scene)
    rep["sources"], layers = C.source_checks(shim, manifest)
    rep["pixelorama_cli"] = C.pixelorama_checks(a.pixelorama, shim, layers, manifest) if os.path.isfile(a.pixelorama) else {"skipped": True, "reason": "no Pixelorama binary given"}

    v04, _ = V4.build_scene()
    names = A.SCENE_LAYERS
    alpha = {names[i]: bool((layers[i].a[..., 3] == v04[i].a[..., 3]).all()) for i in range(9, 13)}
    m4 = json.loads(V04_MANIFEST.read_text(encoding="utf-8"))
    boxes = lambda m: [(x["crop_from_layer_xywh"], x["anchor"], x["clue"]) for x in m["runtime_exports"]["antennas"]]
    tops = {names[9 + i]: int(np.nonzero(layers[9 + i].a[..., 3].any(axis=1))[0][0]) for i in range(3)}
    flat5, flat4 = A.composite(layers), A.composite(v04)
    diff = (flat5 != flat4).any(axis=2)
    rep["geometry"] = {"antenna_and_foreground_alpha_equal_v04": alpha, "sprite_boxes_anchors_clues_equal_v04": boxes(manifest) == boxes(m4),
                       "antenna_top_rows": tops, "sky_layer_unchanged": bool((layers[0].a == v04[0].a).all()),
                       "changed_px_above_y92": int(diff[:92].sum())}
    # props and transitions: what may change in the doors and deck-detail layers
    stone = [A.RGB[n] for n in ("st_hi", "st", "st_mid", "st_dk", "st_deep", "mortar", "lichen", "st_cool", "st_cool_dk", "st_wet")]
    def is_stone(arr):
        m = np.zeros(arr.shape[:2], bool)
        for c in stone:
            m |= (arr[..., :3] == c).all(axis=2)
        return m & (arr[..., 3] == 255)
    d_old, d_new = v04[7].a, layers[7].a
    changed = (d_old != d_new).any(axis=2)
    rep["doors_layer"] = {"changed_px": int(changed.sum()), "changed_non_stone_px": int((changed & ~(is_stone(d_old) & is_stone(d_new))).sum())}
    det_changed = (v04[5].a != layers[5].a).any(axis=2)
    ys, xs = np.nonzero(det_changed)
    conduit_x = [x + 8 for x in A.JUNCTION_X] + [186, 343, 489, 435, 531]
    rep["detail_layer"] = {"changed_px": int(len(ys)), "changed_outside_conduits_and_blooms": int(sum(1 for x in xs if min(abs(x - c) for c in conduit_x) > 3))}
    # originals and runtime
    m3 = json.loads(V03_MANIFEST.read_text(encoding="utf-8"))
    rep["v04_files_hash_as_recorded"] = all(C.sha((ROOT / f["file"]).read_bytes()) == f["sha256"] for f in pinned_files(m4))
    rep["v03_files_hash_as_recorded"] = all(C.sha((ROOT / f["file"]).read_bytes()) == f["sha256"] for f in pinned_files(m3))
    survey = SURVEY.read_text(encoding="utf-8")
    rep["survey_annex"] = {"sha256": C.sha(SURVEY.read_bytes()), "loads_v03": "corridor-plate_unapproved-v03_20261017-224447-15709be4.png" in survey,
                           "names_v04_or_v05": "523bba3b" in survey or STAMP in survey or "4b9d66f1" in survey}
    rep["files_with_v05_stamp_under_game"] = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "game").rglob(f"*4b9d66f1*"))
    # palette
    pal = manifest["palette"]
    gpl = (ROOT / manifest["native_palette_file"]["file"]).read_bytes()
    rep["palette"] = {"size": len(pal), "v03_colours_unchanged_and_first": list(pal.items())[:len(m3["palette"])] == list(m3["palette"].items()),
                      "additions": manifest["palette_additions_vs_v03"],
                      "gpl_hash_as_recorded": C.sha(gpl) == manifest["native_palette_file"]["sha256"],
                      "gpl_lists_palette": [l.split("\t")[1] for l in gpl.decode().splitlines()[4:]] == list(pal)}
    rep["changed_px_vs_v04"] = int(diff.sum())
    rep["changed_px_per_layer_vs_v04"] = {n: int((layers[i].a != v04[i].a).any(axis=2).sum()) for i, n in enumerate(names)}

    s, p, g = rep["sources"], rep["pixelorama_cli"], rep["geometry"]
    gates = {
        "S1_binary_alpha_palette_13_layers": s["binary_alpha"] and s["all_pixels_in_palette"] and s["layer_count"] == 13,
        "S2_manifest_hashes": all(s["manifest_hashes_match"].values()),
        "S3_exports_equal_layers": all(s["runtime_exports_equal_layers"].values()) and s["plate_opaque"],
        "S4_ora_pxo_structure": s["ora_layers_top_first"] and s["ora_merged_equals_composite"] and s["pxo_layers_bottom_first"] and s["pxo_layer_bytes_exact"],
        "G1_geometry_hud_skyline": all(alpha.values()) and g["sprite_boxes_anchors_clues_equal_v04"] and min(tops.values()) >= A.ART_TOP
            and g["sky_layer_unchanged"] and g["changed_px_above_y92"] == 0,
        "G2_transitions_and_props_kept": rep["doors_layer"]["changed_non_stone_px"] == 0 and rep["detail_layer"]["changed_outside_conduits_and_blooms"] == 0,
        "G3_originals_and_runtime_untouched": rep["v04_files_hash_as_recorded"] and rep["v03_files_hash_as_recorded"] and rep["survey_annex"]["loads_v03"]
            and not rep["survey_annex"]["names_v04_or_v05"] and not rep["files_with_v05_stamp_under_game"],
        "G4_native_palette": all(v for k, v in rep["palette"].items() if k not in ("size", "additions")),
        "G5_real_change": rep["changed_px_vs_v04"] > 20000,
    }
    if not p.get("skipped"):
        gates["P_pixelorama_cli_round_trip"] = all(p[e]["split"]["exit"] == 0 and all(p[e]["split"]["layers_exact"].values()) and p[e]["flat"]["exact"]
                                                   and p[e]["source_unchanged_by_cli"] for e in ("pxo", "ora")) and not p["real_appdata_pixelorama_changed"]
    rep["gates"] = gates
    rep["gates_passed"] = f"{sum(gates.values())}/{len(gates)}"
    report = Path(a.report).resolve()
    report.write_text(json.dumps(rep, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for k, v in gates.items():
        print(("PASS " if v else "FAIL ") + k)
    if p.get("skipped"):
        print("SKIPPED P_pixelorama_cli_round_trip: " + p["reason"])
    print("GATES", rep["gates_passed"], report)


if __name__ == "__main__":
    main()
