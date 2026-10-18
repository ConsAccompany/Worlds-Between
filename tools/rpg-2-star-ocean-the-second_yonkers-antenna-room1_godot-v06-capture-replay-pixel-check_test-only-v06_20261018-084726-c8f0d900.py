"""Pixel and log check of the actual Godot v06 test-only captures (Yonkers antenna corridor room 1), adapted from the v05
capture/replay pixel check (same five gates; the comparison baseline moves from v04 to v05).

1. Plate pixels: for each zh/en entry capture, the plate pixels v06 changed against v05 (and against the runtime v03
   plate), minus those under an opaque antenna or foreground texel, must show v06 and never v05 or v03. Pixels under UI
   or the heroine match neither plate and are not counted.
2. The 30 captures are 640x360, 15 per language, with every review kind (entry, three approaches, B from the lane,
   A/C occlusion, beside B, west stair, three interactions, traversal, runtime heroine, return from room 2).
3. The harness log has YK1_V06_ALL_OK and YK1_V06_TEXTURES_IN_USE, no FAIL or SCRIPT ERROR, all six clues, the three
   transitions, 14 collision cases, lane walk, reachability and isolation.
4. Behaviour parity with the v05 run: HUD, header, caption, depth, interaction, reachability, clue, transition,
   isolation and antenna lines are identical (tag renamed); collision, slide and escape stops within 0.05 px; lane walk
   within 1 px.
5. Accepted rooms: the 8 replay captures taken under the v06 in-memory override equal the acceptance captures (0 px),
   and the replay log has ACCEPTED_REPLAY_V06_OVERRIDE textures=5, three interaction lines and ACCEPTED_REPLAY_ALL_OK.

Usage: python -I <this file>
"""
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261018-084726-c8f0d900"
OUT = ROOT / "outputs/yonkers-room1-v06_c8f0d900"
CAP = OUT / "cap"
ACC = OUT / "acc"
LOG = OUT / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-v06-test-only-check-log_{STAMP}.txt"
REPLAY_LOG = OUT / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-v06-accepted-rooms-replay-log_{STAMP}.txt"
V05_LOG = ROOT / "outputs/yonkers-room1-v05_4b9d66f1/rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-v05-test-only-check-log_20261018-043851-4b9d66f1.txt"
V03 = ROOT / "game/assets/environments/yonkers-antenna-room1/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-plate_unapproved-v03_20261017-224447-15709be4.png"
V05 = ROOT / "outputs/yonkers-room1-v05_4b9d66f1/nonruntime-exports/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-plate-scene-quality_unapproved-v05_20261018-043851-4b9d66f1.png"
EXPORTS = OUT / "exp"
V06 = EXPORTS / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-plate-readability_unapproved-v06_{STAMP}.png"
ACCEPTED = [(ROOT / "outputs/room1-visual-review", "011400-d3590c0a"), (ROOT / "outputs/room2-fixtures-pilot", "010418-6b3138d8"),
            (ROOT / "outputs/yonkers-room2-visual-review", "011814-94cebca4")]
KINDS = ["entry", "approach-a", "approach-b", "approach-c", "b-dish-from-lane", "occlusion-behind-a", "occlusion-behind-c", "beside-b",
         "west-stair", "interact-a", "interact-b", "interact-c", "traversal", "entry-runtime-heroine", "returned-from-room2"]
SAME_TAGS = ("HUD_CLEAR", "HEADER_", "CAPTION_", "DEPTH", "ROOM1_INTERACTIONS_OK", "REACHABILITY_OK", "ALL_SIX_CLUES_OK", "TRANSITION_",
             "ISOLATION_OK", "ANTENNA ")
TIMED_TAGS = ("COLLISION ", "SLIDE_OK", "ESCAPE_OK")  # held-input stop points: frame timing, compared within 0.05 px


def long(p):
    """Windows extended-length path: the accepted-replay names exceed MAX_PATH in the primary checkout."""
    s = str(Path(p).resolve())
    return "\\\\?\\" + s if len(s) > 240 and not s.startswith("\\\\?\\") else s


def rgb(p):
    return np.array(Image.open(long(p)).convert("RGB")).astype(np.int16)


def tagged(text, version):
    out = []
    for line in text.splitlines():
        if line.startswith(f"YK1_{version}_"):
            out.append(line[len(f"YK1_{version}_"):].strip())
    return out


def nums(s):
    return [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", s)]


def main():
    p3, p5, p6 = rgb(V03), rgb(V05), rgb(V06)
    covered = np.array(Image.open(next(EXPORTS.glob("*_foreground-occluder_*.png"))).convert("RGBA"))[..., 3] > 0
    for x, slug in zip((163, 320, 477), ("antenna-a-lattice-yagi", "antenna-b-dish", "antenna-c-guyed-whip")):
        alpha = np.array(Image.open(next(EXPORTS.glob(f"*_{slug}_*.png"))).convert("RGBA"))[..., 3] > 0
        covered[58:210, x - 64:x + 64] |= alpha
    changed = (p6 != p5).any(axis=2) & (p6 != p3).any(axis=2) & ~covered
    rep = {"status": "UNAPPROVED, NONRUNTIME test-only evidence", "changed_plate_px_vs_v05_and_v03": int(changed.sum()), "captures": {}}
    for lang in ("zh", "en"):
        cap = rgb(CAP / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_v06-test-only-godot-{lang}-entry-640x360_{STAMP}.png")
        rep["captures"][lang] = {"visible_changed_px_matching_v06": int(((cap == p6).all(axis=2) & changed).sum()),
                                 "matching_v05": int(((cap == p5).all(axis=2) & changed).sum()),
                                 "matching_v03": int(((cap == p3).all(axis=2) & changed).sum())}
    names = sorted(p.name for p in CAP.glob("*.png"))
    rep["capture_count"] = len(names)
    rep["all_640x360"] = all(Image.open(long(CAP / n)).size == (640, 360) for n in names)
    rep["kinds_per_language"] = {lang: sorted(k for k in KINDS if f"-godot-{lang}-{k}-640x360_{STAMP}.png" in "|".join(names)) for lang in ("zh", "en")}
    log = LOG.read_text(encoding="utf-8", errors="replace")
    v6 = tagged(log, "V06")
    need = ["ALL_OK", "TEXTURES_IN_USE", "ROOM1_INTERACTIONS_OK", "ALL_SIX_CLUES_OK 6/6", "TRANSITION_NEXT_OK", "TRANSITION_BACK_OK",
            "TRANSITION_EXIT_OK", "LANE_WALK_OK", "REACHABILITY_OK", "ISOLATION_OK", "SLIDE_OK", "ESCAPE_OK"]
    rep["log"] = {"required_present": {k: any(l.startswith(k) for l in v6) for k in need},
                  "collision_cases": sum(1 for l in v6 if l.startswith("COLLISION ")),
                  "fail_or_script_errors": log.count("YK1_V06_FAIL") + log.count("SCRIPT ERROR")}
    v5 = tagged(V05_LOG.read_text(encoding="utf-8", errors="replace"), "V05")
    same6 = [l for l in v6 if l.startswith(SAME_TAGS)]
    same5 = [l for l in v5 if l.startswith(SAME_TAGS)]
    coll6 = [l for l in v6 if l.startswith(TIMED_TAGS)]
    coll5 = [l for l in v5 if l.startswith(TIMED_TAGS)]
    coll_dev = max((max(abs(a - b) for a, b in zip(nums(x.split("->")[1]), nums(y.split("->")[1]))) for x, y in zip(coll6, coll5)), default=None)
    lane6 = [nums(l.split("x=")[1])[0] for l in v6 if l.startswith("LANE_WALK_OK")]
    lane5 = [nums(l.split("x=")[1])[0] for l in v5 if l.startswith("LANE_WALK_OK")]
    rep["parity_vs_v05"] = {"identical_lines": sum(1 for a, b in zip(same6, same5) if a == b), "compared_lines": len(same5),
                            "differing": [[a, b] for a, b in zip(same6, same5) if a != b],
                            "collision_case_names_equal": [x.split("->")[0] for x in coll6] == [y.split("->")[0] for y in coll5],
                            "collision_max_deviation_px": coll_dev, "lane_walk_x": [lane6, lane5]}
    acc = {}
    for folder, tag in ACCEPTED:
        for ref in sorted(folder.glob(f"*_20261017-{tag}.png")):
            stem = ref.name[: -len(f"_20261017-{tag}.png")]
            got = ACC / f"{stem}_{STAMP}.png"
            acc[ref.name] = int((rgb(ref) != rgb(got)).any(axis=2).sum()) if Path(long(got)).exists() else "missing replay"
    rlog = REPLAY_LOG.read_text(encoding="utf-8", errors="replace")
    rep["accepted_rooms"] = {"differing_px": acc, "override_installed": "ACCEPTED_REPLAY_V06_OVERRIDE in-memory textures=5" in rlog,
                             "interactions_ok": sum(rlog.count(k) for k in ("NYC_ROOM1_INTERACTIONS_OK 3", "NYC_ROOM2_INTERACTIONS_OK 3", "YONKERS_ROOM2_INTERACTIONS_OK 3")),
                             "all_ok": "ACCEPTED_REPLAY_ALL_OK" in rlog, "fail_or_script_errors": rlog.count("ACCEPTED_REPLAY_FAIL") + rlog.count("SCRIPT ERROR")}
    par, ar = rep["parity_vs_v05"], rep["accepted_rooms"]
    gates = {
        "C1_v06_pixels_on_screen": all(c["visible_changed_px_matching_v06"] > 10000 and c["matching_v05"] == 0 and c["matching_v03"] == 0 for c in rep["captures"].values()),
        "C2_thirty_native_captures_all_kinds": rep["capture_count"] == 30 and rep["all_640x360"] and all(len(v) == len(KINDS) for v in rep["kinds_per_language"].values()),
        "C3_six_clues_three_transitions_collision_log": all(rep["log"]["required_present"].values()) and rep["log"]["collision_cases"] == 14 and rep["log"]["fail_or_script_errors"] == 0,
        "C4_behaviour_parity_with_v05": par["identical_lines"] == par["compared_lines"] > 20 and par["collision_case_names_equal"] and par["collision_max_deviation_px"] is not None
            and par["collision_max_deviation_px"] <= 0.05 and len(par["lane_walk_x"][0]) == 1 and abs(par["lane_walk_x"][0][0] - par["lane_walk_x"][1][0]) <= 1.0,
        "C5_accepted_rooms_0px_under_override": len(acc) == 8 and all(v == 0 for v in acc.values()) and ar["override_installed"] and ar["interactions_ok"] == 3
            and ar["all_ok"] and ar["fail_or_script_errors"] == 0,
    }
    rep["gates"] = gates
    rep["result"] = "PASS" if all(gates.values()) else "FAIL"
    path = OUT / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-v06-capture-replay-pixel-check-report_test-only_{STAMP}.json"
    path.write_text(json.dumps(rep, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for k, v in gates.items():
        print(("PASS " if v else "FAIL ") + k)
    print("V06_CAPTURE_REPLAY_PIXEL_CHECK " + rep["result"])


if __name__ == "__main__":
    main()
