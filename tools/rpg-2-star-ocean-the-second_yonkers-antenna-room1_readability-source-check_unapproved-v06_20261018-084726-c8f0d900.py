"""Source and Pixelorama gates for the Yonkers antenna corridor room 1 v06 outdoor readability candidate.

Like the v05 source check, it reuses the committed v03 checker's source_checks (layers, palette, binary alpha, manifest
hashes, nonruntime exports, ORA/PXO structure) and pixelorama_checks (official Pixelorama headless split/flat export with
an isolated temporary APPDATA; the real %APPDATA%/pixelorama is snapshotted before and after). v06 gates, against the
v05 layers rebuilt by the v05 author:
  G1 geometry: antenna and foreground alpha equal v05, sprite boxes/anchors/clue ids equal the v05 manifest, no antenna
     texel above y 66 (HUD), the sky and everything above y 92 unchanged (open skyline);
  G2 transitions, lane and props: the walkway (lane/grating/trench) layer is unchanged; the doors layer changed only
     stone pixels to stone; deck-detail changes stay inside the declared crate/trough/planter rects or on the
     safety-paint lines; wall-kit changes stay inside the five wall boxes plus their new top faces;
  G3 originals and runtime: v05, v04 and v03 files hash as their manifests record; survey_annex.gd still loads v03 and
     names no v04/v05/v06 file; nothing with the v06 stamp exists under game/;
  G4 palette: the 75 v05 colours unchanged and first, two named additions; the .gpl palette matches the manifest;
  G5 real change against v05;
  G6 calmer wall: on the plate (layers 1-9, no antenna sprites) over visible back-wall pixels (rows 108-155, not under
     the wall kit) the mean luminance step between horizontal neighbours is lower than v05, and lowest inside the three
     quiet zones behind the antennas;
  G7 fixture volume: for each named fixture the top face is lighter than its front face by at least 12 luma levels
     (wall boxes, cabinets, crate and trough: all pixels of the face; plinths: stone pixels only, because the lattice
     legs, the dish turntable and the whip mast stand on their top faces).
Godot runtime evidence is checked separately by the v06 capture/replay pixel check.

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
STAMP = "20261018-084726-c8f0d900"
V03_CHECK = ROOT / "tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_pixel-source-pixelorama-check_unapproved-v03_20261017-224447-15709be4.py"
AUTHOR = ROOT / f"tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_outdoor-readability-author_unapproved-v06_{STAMP}.py"
OUT = ROOT / "outputs" / "yonkers-room1-v06_c8f0d900"
MANIFEST = OUT / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_readability-manifest_unapproved-v06_{STAMP}.json"
V05_MANIFEST = ROOT / "outputs/yonkers-room1-v05_4b9d66f1/rpg-2-star-ocean-the-second_yonkers-antenna-room1_scene-quality-manifest_unapproved-v05_20261018-043851-4b9d66f1.json"
V04_MANIFEST = ROOT / "outputs/yonkers-room1-v04_523bba3b/rpg-2-star-ocean-the-second_yonkers-antenna-room1_material-depth-scene-manifest_unapproved-v04_20261018-052445-523bba3b.json"
V03_MANIFEST = ROOT / "outputs/yonkers-room1-v03_15709be4/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-scene-manifest_unapproved-v03_20261017-224447-15709be4.json"
SURVEY = ROOT / "game/scripts/survey_annex.gd"
# fixture: (layer index, top-face rect, front-face rect) as x0, y0, x1, y1 inclusive
FIXTURES = {
    "junction-box-a": (2, (199, 122, 213, 122), (200, 125, 213, 142)),
    "junction-box-b": (2, (361, 122, 375, 122), (362, 125, 375, 142)),
    "junction-box-c": (2, (421, 122, 435, 122), (422, 125, 435, 142)),
    "west-patch-cabinet": (2, (47, 110, 71, 110), (48, 113, 70, 151)),
    "east-switch-cabinet": (2, (575, 109, 597, 109), (576, 111, 596, 152)),
    "crate": (5, (403, 158, 411, 163), (382, 166, 410, 178)),  # lid east of the cable coil
    "dish-cable-trough": (5, (291, 161, 360, 166), (291, 168, 359, 181)),
    "plinth-a": (9, (142, 193, 188, 195), (142, 198, 187, 206)),
    "plinth-b-dish-base": (10, (293, 193, 347, 195), (293, 198, 347, 206)),
    "plinth-c": (11, (462, 195, 492, 197), (462, 200, 491, 206)),
}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pinned_files(m):
    files = [m["editable_sources"][k] for k in m["editable_sources"]] + [m["runtime_exports"]["plate"], m["runtime_exports"]["foreground"]]
    return files + [x["runtime_png"] for x in m["runtime_exports"]["antennas"]]


def read_pinned(rel):
    """Bytes of a manifest-pinned file; the v05 export names exceed MAX_PATH in the primary checkout, so use the
    Windows extended-length form for long paths."""
    s = str((ROOT / rel).resolve())
    if os.name == "nt" and len(s) > 240:
        s = "\\\\?\\" + s
    with open(s, "rb") as fh:
        return fh.read()


def luma(arr):
    rgb = arr[..., :3].astype(np.float64)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def wall_step(flat, kit_alpha, x0=0, x1=639):
    """Mean |luma(x+1) - luma(x)| over visible back-wall stone pairs (rows 108-155) between x0 and x1."""
    lum = luma(flat)
    vis = kit_alpha != 255
    rows = slice(108, 156)
    d = np.abs(lum[rows, x0 + 1:x1 + 1] - lum[rows, x0:x1])
    m = vis[rows, x0 + 1:x1 + 1] & vis[rows, x0:x1]
    return round(float(d[m].mean()), 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pixelorama", default=str(ROOT / "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"))
    ap.add_argument("--report", default=str(OUT / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_readability-source-check-report_unapproved-v06_{STAMP}.json"))
    a = ap.parse_args()
    C = load("yk1v03_check", V03_CHECK)
    V6 = load("yk1v06_author", AUTHOR)
    A = V6.A
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rep = {"tool": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), "status": "UNAPPROVED, NONRUNTIME candidate"}
    shim = type("A", (), {"composite": A.composite, "RGB": A.RGB, "SCENE_LAYERS": A.SCENE_LAYERS})
    shim.build_scene = staticmethod(V6.build_scene)
    rep["sources"], layers = C.source_checks(shim, manifest)
    rep["pixelorama_cli"] = C.pixelorama_checks(a.pixelorama, shim, layers, manifest) if os.path.isfile(a.pixelorama) else {"skipped": True, "reason": "no Pixelorama binary given"}
    rep["pixelorama_exe"] = a.pixelorama

    v05 = V6.V5_REF()
    names = A.SCENE_LAYERS
    alpha = {names[i]: bool((layers[i].a[..., 3] == v05[i].a[..., 3]).all()) for i in range(9, 13)}
    m5 = json.loads(V05_MANIFEST.read_text(encoding="utf-8"))
    boxes = lambda m: [(x["crop_from_layer_xywh"], x["anchor"], x["clue"]) for x in m["runtime_exports"]["antennas"]]
    tops = {names[9 + i]: int(np.nonzero(layers[9 + i].a[..., 3].any(axis=1))[0][0]) for i in range(3)}
    flat6, flat5 = A.composite(layers), A.composite(v05)
    plate6, plate5 = A.composite(layers[:9]), A.composite(v05[:9])
    diff = (flat6 != flat5).any(axis=2)
    rep["geometry"] = {"antenna_and_foreground_alpha_equal_v05": alpha, "sprite_boxes_anchors_clues_equal_v05": boxes(manifest) == boxes(m5),
                       "antenna_top_rows": tops, "sky_layer_unchanged": bool((layers[0].a == v05[0].a).all()),
                       "changed_px_above_y92": int(diff[:92].sum())}
    # lane, doors, props
    stone = [A.RGB[n] for n in sorted(V6.STONE)]
    def is_stone(arr):
        m = np.zeros(arr.shape[:2], bool)
        for c in stone:
            m |= (arr[..., :3] == c).all(axis=2)
        return m & (arr[..., 3] == 255)
    rep["walkway_layer_unchanged"] = bool((layers[4].a == v05[4].a).all())
    changed = (v05[7].a != layers[7].a).any(axis=2)
    rep["doors_layer"] = {"changed_px": int(changed.sum()), "changed_non_stone_px": int((changed & ~(is_stone(v05[7].a) & is_stone(layers[7].a))).sum())}
    allowed = np.zeros((A.H, A.W), bool)
    for x0, y0, x1, y1 in V6.DETAIL_EDIT_RECTS:
        allowed[y0:y1 + 1, x0:x1 + 1] = True
    for x0, x1 in V6.PAINT_BOXES:
        allowed[184:214, x0] = allowed[184:214, x1] = True
        allowed[213, x0:x1 + 1] = True
    det = (v05[5].a != layers[5].a).any(axis=2)
    rep["detail_layer"] = {"changed_px": int(det.sum()), "changed_outside_declared_fixtures_and_paint": int((det & ~allowed).sum())}
    kit_ok = np.zeros((A.H, A.W), bool)
    for x0, y0, x1, y1 in V6.WALL_BOXES:
        kit_ok[y0 - V6.BOX_TOP_H:y1 + 3, x0 - 1:x1 + 2] = True
    kit = (v05[2].a != layers[2].a).any(axis=2)
    rep["wall_kit_layer"] = {"changed_px": int(kit.sum()), "changed_outside_wall_boxes": int((kit & ~kit_ok).sum())}
    # originals and runtime
    m4 = json.loads(V04_MANIFEST.read_text(encoding="utf-8"))
    m3 = json.loads(V03_MANIFEST.read_text(encoding="utf-8"))
    rep["v05_files_hash_as_recorded"] = all(C.sha(read_pinned(f["file"])) == f["sha256"] for f in pinned_files(m5))
    rep["v04_files_hash_as_recorded"] = all(C.sha(read_pinned(f["file"])) == f["sha256"] for f in pinned_files(m4))
    rep["v03_files_hash_as_recorded"] = all(C.sha(read_pinned(f["file"])) == f["sha256"] for f in pinned_files(m3))
    survey = SURVEY.read_text(encoding="utf-8")
    rep["survey_annex"] = {"sha256": C.sha(SURVEY.read_bytes()), "loads_v03": "corridor-plate_unapproved-v03_20261017-224447-15709be4.png" in survey,
                           "names_v04_v05_or_v06": any(t in survey for t in ("523bba3b", "4b9d66f1", "c8f0d900"))}
    rep["files_with_v06_stamp_under_game"] = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "game").rglob("*c8f0d900*"))
    # palette
    pal = manifest["palette"]
    gpl = (ROOT / manifest["native_palette_file"]["file"]).read_bytes()
    rep["palette"] = {"size": len(pal), "v05_colours_unchanged_and_first": list(pal.items())[:len(m5["palette"])] == list(m5["palette"].items()),
                      "additions": manifest["palette_additions_vs_v05"],
                      "additions_are_the_rest": list(pal)[len(m5["palette"]):] == list(manifest["palette_additions_vs_v05"]),
                      "gpl_hash_as_recorded": C.sha(gpl) == manifest["native_palette_file"]["sha256"],
                      "gpl_lists_palette": [l.split("\t")[1] for l in gpl.decode().splitlines()[4:]] == list(pal)}
    rep["changed_px_vs_v05"] = int(diff.sum())
    rep["changed_px_per_layer_vs_v05"] = {n: int((layers[i].a != v05[i].a).any(axis=2).sum()) for i, n in enumerate(names)}
    # calmer wall (descriptive numbers plus the gate)
    zones = {f"quiet_{x0}_{x1}": (x0, x1) for x0, x1, _t in V6.QUIET}
    rep["wall_luma_step"] = {
        "whole_wall": {"v05": wall_step(plate5, v05[2].a[..., 3]), "v06": wall_step(plate6, layers[2].a[..., 3])},
        **{k: {"v05": wall_step(plate5, v05[2].a[..., 3], x0, x1), "v06": wall_step(plate6, layers[2].a[..., 3], x0, x1)} for k, (x0, x1) in zones.items()},
    }
    # fixture volume: top face lighter than front face, measured on the fixture's own layer
    vol = {}
    for k, (li, (tx0, ty0, tx1, ty1), (fx0, fy0, fx1, fy1)) in FIXTURES.items():
        arr = layers[li].a
        lum = luma(arr)
        keep = arr[..., 3] == 255
        if k.startswith("plinth"):
            keep = keep & np.isin(V6.V4.names(arr), sorted(V6.STONE))
        top = lum[ty0:ty1 + 1, tx0:tx1 + 1][keep[ty0:ty1 + 1, tx0:tx1 + 1]]
        front = lum[fy0:fy1 + 1, fx0:fx1 + 1][keep[fy0:fy1 + 1, fx0:fx1 + 1]]
        vol[k] = {"top_luma": round(float(top.mean()), 1), "front_luma": round(float(front.mean()), 1),
                  "top_minus_front": round(float(top.mean() - front.mean()), 1)}
    rep["fixture_volume"] = vol

    s, p, g, wl = rep["sources"], rep["pixelorama_cli"], rep["geometry"], rep["wall_luma_step"]
    gates = {
        "S1_binary_alpha_palette_13_layers": s["binary_alpha"] and s["all_pixels_in_palette"] and s["layer_count"] == 13,
        "S2_manifest_hashes": all(s["manifest_hashes_match"].values()),
        "S3_exports_equal_layers": all(s["runtime_exports_equal_layers"].values()) and s["plate_opaque"],
        "S4_ora_pxo_structure": s["ora_layers_top_first"] and s["ora_merged_equals_composite"] and s["pxo_layers_bottom_first"] and s["pxo_layer_bytes_exact"],
        "G1_geometry_hud_skyline": all(alpha.values()) and g["sprite_boxes_anchors_clues_equal_v05"] and min(tops.values()) >= A.ART_TOP
            and g["sky_layer_unchanged"] and g["changed_px_above_y92"] == 0,
        "G2_lane_transitions_props_kept": rep["walkway_layer_unchanged"] and rep["doors_layer"]["changed_non_stone_px"] == 0
            and rep["detail_layer"]["changed_outside_declared_fixtures_and_paint"] == 0 and rep["wall_kit_layer"]["changed_outside_wall_boxes"] == 0,
        "G3_originals_and_runtime_untouched": rep["v05_files_hash_as_recorded"] and rep["v04_files_hash_as_recorded"] and rep["v03_files_hash_as_recorded"]
            and rep["survey_annex"]["loads_v03"] and not rep["survey_annex"]["names_v04_v05_or_v06"] and not rep["files_with_v06_stamp_under_game"],
        "G4_native_palette": all(v for k, v in rep["palette"].items() if k not in ("size", "additions")),
        "G5_real_change": rep["changed_px_vs_v05"] > 20000,
        "G6_calmer_wall_quietest_behind_antennas": wl["whole_wall"]["v06"] < wl["whole_wall"]["v05"]
            and all(wl[k]["v06"] < wl[k]["v05"] and wl[k]["v06"] <= wl["whole_wall"]["v06"] for k in zones),
        "G7_fixture_top_lighter_than_front": all(v["top_minus_front"] >= 12 for v in vol.values()),
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
    print("wall_luma_step", json.dumps(wl))
    print("fixture_volume", json.dumps({k: v["top_minus_front"] for k, v in vol.items()}))
    print("GATES", rep["gates_passed"], report)


if __name__ == "__main__":
    main()
