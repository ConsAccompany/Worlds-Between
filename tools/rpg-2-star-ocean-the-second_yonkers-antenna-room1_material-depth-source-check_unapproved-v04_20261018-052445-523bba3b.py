"""Source and Pixelorama gates for the Yonkers antenna corridor room 1 v04 material-depth candidate.

Reuses the committed v03 checker's source_checks (layers, palette, binary alpha, manifest hashes, nonruntime exports,
ORA/PXO structure) and pixelorama_checks (headless split/flat round trip; skipped when no Pixelorama binary is given).
Adds v04 gates: alpha and sprite boxes equal v03 (no coordinate moves), v03 files and runtime wiring unchanged, and
every changed pixel in the wall, deck, cast-shadow or dish layers, below the coping drip line (y 108). Godot capture is not part of this tool.

Usage: python -I <this file> [--pixelorama <exe>] [--report <json>]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261018-052445-523bba3b"
V03_CHECK = ROOT / "tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_pixel-source-pixelorama-check_unapproved-v03_20261017-224447-15709be4.py"
AUTHOR = ROOT / f"tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_material-depth-author_unapproved-v04_{STAMP}.py"
OUT = ROOT / "outputs" / "yonkers-room1-v04_523bba3b"
MANIFEST = OUT / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_material-depth-scene-manifest_unapproved-v04_{STAMP}.json"
V03_MANIFEST = ROOT / "outputs/yonkers-room1-v03_15709be4/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-scene-manifest_unapproved-v03_20261017-224447-15709be4.json"
SURVEY = "game/scripts/survey_annex.gd"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT)] + list(args), capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pixelorama", default=str(ROOT / "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"))
    ap.add_argument("--report", default=str(OUT / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_material-depth-source-check-report_unapproved-v04_{STAMP}.json"))
    a = ap.parse_args()
    C = load("yk1v03_check", V03_CHECK)
    V4 = load("yk1v04_author", AUTHOR)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rep = {"tool": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), "status": "UNAPPROVED candidate"}
    # v03 source_checks calls A.build_scene() and expects the layer list; the v04 author also returns stats.
    shim = type("A", (), {k: getattr(V4, k) for k in ("composite", "RGB", "SCENE_LAYERS")})
    shim.build_scene = staticmethod(lambda: V4.build_scene()[0])
    rep["sources"], layers = C.source_checks(shim, manifest)
    rep["pixelorama_cli"] = C.pixelorama_checks(a.pixelorama, shim, layers, manifest) if os.path.isfile(a.pixelorama) else {"skipped": True, "reason": "no Pixelorama binary in this environment"}

    v03 = V4.A.build_scene()
    alpha = {}
    for i, name in enumerate(V4.SCENE_LAYERS):
        new, old = layers[i].a[..., 3] == 255, v03[i].a[..., 3] == 255
        alpha[name] = bool((new == old).all()) if i != 6 else bool((old <= new).all())
    rep["alpha_equal_v03"] = alpha
    m3 = json.loads(V03_MANIFEST.read_text(encoding="utf-8"))
    boxes = lambda m: [(x["crop_from_layer_xywh"], x["anchor"], x["clue"]) for x in m["runtime_exports"]["antennas"]]
    rep["sprite_boxes_anchors_clues_equal_v03"] = boxes(manifest) == boxes(m3)
    rep["palette_equal_v03"] = manifest["palette"] == m3["palette"]
    # v03 originals: the manifest-pinned files still hash as recorded and are unmodified against HEAD
    v03_files = [m3["editable_sources"][k] for k in m3["editable_sources"]] + [m3["runtime_exports"]["plate"], m3["runtime_exports"]["foreground"]] + [x["runtime_png"] for x in m3["runtime_exports"]["antennas"]]
    rep["v03_files_hash_as_recorded"] = all(C.sha((ROOT / f["file"]).read_bytes()) == f["sha256"] for f in v03_files)
    st = git("status", "--porcelain", "--", SURVEY, "game/assets", "outputs/yonkers-room1-v03_15709be4", str(V4.V03_AUTHOR.relative_to(ROOT)))
    rep["runtime_and_v03_paths_clean_vs_head"] = {"exit": st.returncode, "changed": st.stdout.splitlines()}
    survey = (ROOT / SURVEY).read_text(encoding="utf-8")
    rep["survey_annex_still_loads_v03_not_v04"] = "corridor-plate_unapproved-v03_20261017-224447-15709be4.png" in survey and STAMP not in survey
    rep["nothing_written_under_game"] = not any(STAMP in p for p in git("ls-files", "--others", "--exclude-standard", "game").stdout.splitlines())
    # where the change landed: only the wall, deck, cast-shadow and dish layers, and nothing above the coping drip line
    allowed = {"back-parapet-masonry", "wall-kit-and-ivy", "deck-slabs", "cast-shadows", "antenna-b-dish"}
    rep["changed_px_per_layer"] = {n: int((layers[i].a != v03[i].a).any(axis=2).sum()) for i, n in enumerate(V4.SCENE_LAYERS)}
    flat_new, flat_old = V4.composite(layers), V4.composite(v03)
    ys, xs = np.nonzero((flat_new != flat_old).any(axis=2))
    rep["changed_px"] = int(len(ys))
    rep["changed_bbox_y"] = [int(ys.min()), int(ys.max())] if len(ys) else None
    rep["changed_above_y108"] = int((ys < 108).sum())
    rep["changed_in_other_layers"] = {n: v for n, v in rep["changed_px_per_layer"].items() if v and n not in allowed}

    s, p = rep["sources"], rep["pixelorama_cli"]
    gates = {
        "S1_binary_alpha_palette_13_layers": s["binary_alpha"] and s["all_pixels_in_palette"] and s["layer_count"] == 13,
        "S2_manifest_hashes": all(s["manifest_hashes_match"].values()),
        "S3_exports_equal_layers": all(s["runtime_exports_equal_layers"].values()) and s["plate_opaque"],
        "S4_ora_pxo_structure": s["ora_layers_top_first"] and s["ora_merged_equals_composite"] and s["pxo_layers_bottom_first"] and s["pxo_layer_bytes_exact"],
        "V1_alpha_and_coordinates_equal_v03": all(alpha.values()) and rep["sprite_boxes_anchors_clues_equal_v03"] and rep["palette_equal_v03"],
        "V2_v03_originals_and_runtime_untouched": rep["v03_files_hash_as_recorded"] and st.returncode == 0 and not st.stdout.strip()
            and rep["survey_annex_still_loads_v03_not_v04"] and rep["nothing_written_under_game"],
        "V3_change_bounded_to_wall_deck_plinths": rep["changed_px"] > 0 and rep["changed_above_y108"] == 0 and not rep["changed_in_other_layers"],
    }
    pending = {"P_pixelorama_cli_round_trip": "skipped (no binary here); pending locally" if p.get("skipped") else
               all(p[e]["split"]["exit"] == 0 and all(p[e]["split"]["layers_exact"].values()) and p[e]["flat"]["exact"] for e in ("pxo", "ora")),
               "G_godot_capture": "not run: no Godot binary here; pending locally"}
    rep["gates"], rep["pending"] = gates, pending
    rep["gates_passed"] = f"{sum(gates.values())}/{len(gates)}"
    Path(a.report).write_text(json.dumps(rep, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for k, v in gates.items():
        print(("PASS " if v else "FAIL ") + k)
    for k, v in pending.items():
        print("PENDING " + k + ": " + str(v))
    print("GATES", rep["gates_passed"], Path(a.report).relative_to(ROOT))


if __name__ == "__main__":
    main()
