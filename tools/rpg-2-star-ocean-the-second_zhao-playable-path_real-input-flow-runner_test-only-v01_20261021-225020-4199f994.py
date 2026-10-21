"""Run the Zhao real-input flow (windowed, 640x360, real-time) under the checked runner with isolated APPDATA/LOCALAPPDATA.

    python <this> --language en --scenario victory
Each run gets a fresh profile under ignored work/zpath27-rif-profiles/<tag>; logs/report/captures go to outputs/zpath27/rif-<tag>.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import time

ROOT = Path(__file__).resolve().parent.parent
GODOT = next((a / "work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe" for a in [ROOT, *ROOT.parents][:6] if (a / "work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe").is_file()), None)
RUNNER = ROOT / "tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py"
HARNESS = ROOT / "tools/rpg-2-star-ocean-the-second_zhao-playable-path_real-input-flow_test-only-v01_20261021-225020-4199f994.gd"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--language", choices=("en", "zh"), required=True)
    p.add_argument("--scenario", choices=("victory", "defeat", "defeat-boundary"), required=True)
    p.add_argument("--timeout", type=float, default=200.0)
    a = p.parse_args()
    spec = importlib.util.spec_from_file_location("checked_runner", RUNNER)
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    tag = time.strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(4)
    out = ROOT / "outputs/zpath27" / ("rif-" + tag)
    prof = ROOT / "work/zpath27-rif-profiles" / tag
    for d in (out, prof / "appdata", prof / "localappdata"):
        d.mkdir(parents=True, exist_ok=False)
    os.environ["APPDATA"] = str(prof / "appdata")
    os.environ["LOCALAPPDATA"] = str(prof / "localappdata")
    os.environ.pop("ANTHROPIC_API_KEY", None)
    cmd = [str(GODOT), "--path", str(ROOT / "game"), "--resolution", "640x360", "--fixed-fps", "-1",
           "-s", str(HARNESS), "--", str(out).replace("\\", "/"), a.language, tag, str(prof).replace("\\", "/"), a.scenario]
    log = out / f"rpg-2-star-ocean-the-second_zhao-rif_{a.language}-{a.scenario}_godot-log_{tag}.log"
    r = runner.run_checked(cmd, a.timeout, ["ZRIF_ALL_PASS"], str(log))
    receipt = {"tag": tag, "language": a.language, "scenario": a.scenario, "passed": r["passed"], "reason": r["reason"],
               "exitCode": r["exitCode"], "elapsedSeconds": r["elapsedSeconds"], "missingMarkers": r["missingMarkers"],
               "command": cmd, "harnessSha256Raw": hashlib.sha256(HARNESS.read_bytes()).hexdigest(),
               "runnerSha256Raw": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "profile": str(prof)}
    (out / f"rpg-2-star-ocean-the-second_zhao-rif_{a.language}-{a.scenario}_receipt_{tag}.json").write_text(
        json.dumps(receipt, indent=1), encoding="utf-8")
    for line in r["log"].splitlines():
        if line.startswith("ZRIF") or "ERROR" in line:
            print(line)
    print("RIF_RUN", "PASS" if r["passed"] else "FAIL", r["reason"], tag, r["elapsedSeconds"])
    return 0 if r["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
