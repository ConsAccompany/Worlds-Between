"""Reuse the checked runner and inherited normal-input flow for the male path.

Runs EN/ZH victory and natural defeat/retry, each with an isolated temporary save
profile. Reports are automated evidence, not human playtests or artistic approval.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parent.parent
HARNESS = ROOT / "tools/rpg-2-star-ocean-the-second_male-playable-path_combined-flow-adapter_test-only-v01_20261021-170200-5e1c24a7.gd"
CHECKED = ROOT / "tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py"


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--language", choices=("en", "zh"), action="append")
    args.add_argument("--scenario", choices=("victory", "defeat"), action="append")
    opts = args.parse_args()
    spec = importlib.util.spec_from_file_location("existing_checked_runner", CHECKED)
    checked = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checked)
    godot = next((p / "work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe"
                  for p in [ROOT, *ROOT.parents][:6]
                  if (p / "work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe").is_file()), None)
    if godot is None:
        raise SystemExit("Godot runtime missing")
    tag = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    out = ROOT / "outputs/mpath24" / tag
    out.mkdir(parents=True)
    pins = [HARNESS, Path(__file__), ROOT / "game/scripts/battle_arena.gd", ROOT / "game/scripts/exploration_sprite_set_pilot.gd",
            *sorted((ROOT / "game/scripts/mpath24").glob("*.gd"))]
    result = {"base": "bbbfbde84cdc2d07556eded68eeb618522cc183b", "startedAt": datetime.now(timezone.utc).isoformat(),
              "sourceSha256Raw": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in pins},
              "runs": [], "humanPlaytest": False, "artApproved": False, "ordinaryMaleDefaultAdopted": False}
    manifest = out / ("rpg-2-star-ocean-the-second_male-playable-path_root-proof_test-only-v01_" + tag + ".json")
    for language in opts.language or ("en", "zh"):
        for scenario in opts.scenario or ("victory", "defeat"):
            stem = "rpg-2-star-ocean-the-second_male-playable-path_" + language + "-" + scenario + "_test-only-v01_" + tag
            run_dir = out / (language + "-" + scenario)
            run_dir.mkdir()
            with tempfile.TemporaryDirectory(prefix="worlds-between-male-") as profile:
                # This dedicated runner process has no other workers; children inherit this isolated profile.
                os.environ.update(APPDATA=profile, LOCALAPPDATA=profile)
                command = [str(godot), "--resolution", "1280x720", "--position", "40,40", "--audio-driver", "Dummy", "--fixed-fps", "30",
                           "--path", str(ROOT / "game"), "--script", str(HARNESS), "--", str(run_dir), language, tag, profile, scenario]
                r = checked.run_checked(command, 120, expected=["PATH16_ALL_PASS language=" + language], log_path=run_dir / (stem + ".log"))
            result["runs"].append({"language": language, "scenario": scenario, "command": command,
                                   **{k: v for k, v in r.items() if k != "log"}})
            result["finishedAt"] = datetime.now(timezone.utc).isoformat()
            manifest.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf8"))
            print(language, scenario, "PASS" if r["passed"] else "FAIL", r.get("reason"), flush=True)
            if not r["passed"]:
                print(r.get("log", "")[-3500:])
                return 1
    print(manifest.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
