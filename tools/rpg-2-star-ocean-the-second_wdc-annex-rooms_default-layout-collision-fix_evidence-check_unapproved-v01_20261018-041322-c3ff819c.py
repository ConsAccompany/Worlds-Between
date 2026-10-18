"""UNAPPROVED Washington survey annex rooms layout/collision fix: evidence gates, accepted-room 0 px replay and a
dependency manifest (sha256-text-lf-v1 for text, sha256-bytes for binaries).

Usage: python -I <this file> --out outputs/wdc-rooms-fix_c3ff819c
Reads <out>/probe/godot-check-results-{default,optin}.json, <out>/v01-rerun/probe/godot-check-results.json,
<out>/replay/ (accepted-rooms replay frames) and writes <out>/<report>.json and <out>/<manifest>.json.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261018-041322-c3ff819c"
BASE = "7370739"
# Acceptance-record images of the three accepted rooms (same list as the room-2 v01 check, gate D2).
ACCEPTED = {
    "nyc-public-facilities-room1_existing-scene-godot-%s-640x360-review-v01": ("outputs/room1-visual-review", "20261017-011400-d3590c0a", ("zh", "en")),
    "nyc-public-facilities-room2_three-pixel-fixtures-godot-%s-640x360_unapproved-v01": ("outputs/room2-fixtures-pilot", "20261017-010418-6b3138d8", ("zh", "en")),
    "nyc-public-facilities-room2_repair-manual-approach-godot-%s-640x360_unapproved-v01": ("outputs/room2-fixtures-pilot", "20261017-010418-6b3138d8", ("zh",)),
    "nyc-public-facilities-room2_repair-manual-interaction-godot-%s-640x360_unapproved-v01": ("outputs/room2-fixtures-pilot", "20261017-010418-6b3138d8", ("zh",)),
    "yonkers-maintenance-room2_four-pixel-fixtures-godot-%s-640x360-review-v01": ("outputs/yonkers-room2-visual-review", "20261017-011814-94cebca4", ("zh", "en")),
}
UNCHANGED_VS_BASE = [
    "game/scripts/survey_content.gd",
    "game/scenes/survey_annex.tscn",
    "game/scripts/app_state.gd",
    "game/assets/environments/rpg-2-star-ocean-the-second_scifi-ruins-survey-annex-room-02_environment-background_m8-concept_20261014-143300-042ae336.png",
    "game/assets/environments/wdc-survey-room1/rpg-2-star-ocean-the-second_wdc-annex-room1_capitol-interior-scene_unapproved-v02_20261017-160235-71300729.png",
]
DEPENDENCIES = [
    ("game/scripts/survey_annex.gd", "runtime script (only modified tracked file of this fix)"),
    *[(p, "unchanged vs " + BASE) for p in UNCHANGED_VS_BASE],
    ("tools/rpg-2-star-ocean-the-second_wdc-annex-rooms_default-layout-collision-fix_godot-check_unapproved-v01_20261018-041322-c3ff819c.gd", "new focused Godot check"),
    ("tools/rpg-2-star-ocean-the-second_wdc-annex-rooms_default-layout-collision-fix_evidence-check_unapproved-v01_20261018-041322-c3ff819c.py", "this evidence check"),
    ("tools/rpg-2-star-ocean-the-second_wdc-annex-room2_godot-capture-and-check_unapproved-v01_20261018-001157-151fb8d0.gd", "room-2 v01 opt-in check (rerun, unmodified)"),
    ("tools/rpg-2-star-ocean-the-second_wdc-annex-room1_v02-review-gate-accepted-rooms-replay_check-v01_20261017-172907-03286bf3.gd", "accepted rooms replay (rerun, unmodified)"),
    ("docs/qa/rpg-2-star-ocean-the-second_wdc-annex-room2_records-chamber-playable-integration_qa-note_unapproved-v01_20261018-035908-3a34d132.md", "prior room-2 QA (retained, unmodified)"),
]
TEXT_SUFFIXES = {".gd", ".py", ".md", ".json", ".tscn", ".patch", ".txt", ".log"}


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, check=False).stdout


def digest(data, path):
    if Path(path).suffix in TEXT_SUFFIXES:
        return "sha256-text-lf-v1", hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()
    return "sha256-bytes", hashlib.sha256(data).hexdigest()


def rgba(path):
    return np.array(Image.open(path).convert("RGBA"))


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    out = ROOT / ap.parse_args().out
    default = load(out / "probe/godot-check-results-default.json")
    optin = load(out / "probe/godot-check-results-optin.json")
    v01 = load(out / "v01-rerun/probe/godot-check-results.json")

    replay = {}
    for name, (subdir, stamp, langs) in ACCEPTED.items():
        for lang in langs:
            n = name % lang
            ref = ROOT / subdir / f"rpg-2-star-ocean-the-second_{n}_{stamp}.png"
            got = sorted((out / "replay").glob(f"rpg-2-star-ocean-the-second_{n}_*.png"))
            replay[n] = int((rgba(got[0]) != rgba(ref)).any(axis=2).sum()) if ref.is_file() and len(got) == 1 else "missing"

    unchanged = {}
    for p in UNCHANGED_VS_BASE:
        base = git("show", f"{BASE}:{p}")
        unchanged[p] = digest(base, p) == digest((ROOT / p).read_bytes(), p)

    parity = default["parity_vs_head"]
    gates = {
        "G1_default_mode_ok": default.get("ok") is True and default.get("test_saves_removed") is True,
        "G2_optin_mode_ok": optin.get("ok") is True and optin.get("test_saves_removed") is True,
        "G3_room2_v01_optin_rerun_ok": v01.get("ok") is True,
        "H1_header_bounds_after": all(not v["after"]["problems"] for r in (default, optin) for v in r["header"].values()),
        "H2_head_bugs_reproduced": bool(default["header"]["room1_en"]["before"]["problems"]) and bool(default["header"]["room2_en"]["before"]["problems"]),
        "W1_walls_stop_after": all(not v["in_wall"] for k, v in default["collision"].items() if k.startswith("after_"))
            and all(not v["in_wall"] for v in optin["collision"].values()),
        "W2_head_walk_through_reproduced": default["head_cases_inside_walls"] == 7,
        "R1_reachable_clues_terminal_exit": all(all(r["reachability"]["targets"].values()) for r in (default, optin)),
        "P1_zh_frames_identical_to_head": parity["room1_zh"]["pixels"] == 0 and parity["room2_zh"]["pixels"] == 0
            and optin["parity_vs_head"]["room1_zh"]["pixels"] == 0,
        "P2_en_changes_header_only": all(parity[k]["bbox"][3] < 62 for k in ("room1_en", "room2_en")),
        "D2_accepted_rooms_pixel_identical": len(replay) == 8 and all(v == 0 for v in replay.values()),
        "S1_content_scene_backgrounds_unchanged": all(unchanged.values()),
    }
    report = {
        "stamp": STAMP, "base": BASE, "status": "UNAPPROVED technical fix; nothing staged/committed/pushed; meters unchanged",
        "gates": gates, "passed": sum(gates.values()), "total": len(gates),
        "parity_vs_head_default": parity, "parity_vs_head_optin_room1": optin["parity_vs_head"],
        "header": {"default": default["header"], "optin": optin["header"]},
        "collision": {"default": default["collision"], "optin": optin["collision"]},
        "reachability": {"default": default["reachability"], "optin": optin["reachability"]},
        "interactions_default": default.get("interactions"),
        "accepted_rooms_replay_differing_pixels": replay, "unchanged_vs_base": unchanged,
        "v01_parity_gate_rerun": ("c3ff819c run (2026-10-18): the old 0 px v01 parity FAILED by design (room 1 en 1377 px, Back button). "
                                  "Since r1 (2026-10-18) the v01 parity mode and D1 expect zh 0 px and en changes only in the 62-row header."),
    }
    (out / f"rpg-2-star-ocean-the-second_wdc-annex-rooms_fix-check-report_{STAMP}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    entries = []
    paths = list(DEPENDENCIES) + [(str(p.relative_to(ROOT)).replace("\\", "/"), "evidence") for p in sorted(out.rglob("*"))
                                  if p.is_file() and "manifest" not in p.name and "check-report" not in p.name]
    for rel, role in paths:
        data = (ROOT / rel).read_bytes()
        algo, h = digest(data, rel)
        tracked = bool(git("ls-files", "--", rel).strip())
        state = ("modified" if git("status", "--porcelain", "--", rel).strip() else "unchanged") if tracked else "untracked"
        entries.append({"path": rel, "role": role, "hash_algorithm": algo, "sha256": h, "git_state": state})
    (out / f"rpg-2-star-ocean-the-second_wdc-annex-rooms_fix-dependency-manifest_{STAMP}.json").write_text(
        json.dumps({"stamp": STAMP, "base": BASE, "entries": entries}, indent=2), encoding="utf-8")

    for k, v in gates.items():
        print(("PASS " if v else "FAIL ") + k)
    print(f"GATES {report['passed']}/{report['total']}")
    print("REPLAY", json.dumps(replay))
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
