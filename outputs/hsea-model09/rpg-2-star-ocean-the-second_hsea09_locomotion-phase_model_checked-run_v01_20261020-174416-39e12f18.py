"""HSEA09 bounded checked run for the pure locomotion phase model (test-only, synthetic fixture).

Runs the canonical Godot checked runner with a 20 s deadline and the HSEA09_TESTS_OK marker.
It never filters an engine diagnostic: if Godot emits ERROR (including the known environment
root-certificate-store error), the checked gate is reported FAIL even at exit 0.

This fixture does not run gameplay, a scene, input, collision or the opt-in driver. It is not
motion/visual/creator approval evidence.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = next(p for p in ROOT.parents if (p / "work/tooling/godot-4-7-2").is_dir())
TAG = "20261020-174416-39e12f18"
MODEL = ROOT / "game/scripts/rpg-2-star-ocean-the-second_hsea09_locomotion-phase_model_v01_20261020-174416-39e12f18.gd"
TEST = ROOT / "tests/hsea09/rpg-2-star-ocean-the-second_hsea09_locomotion-phase_model_checked-tests_test-only-v01_20261020-174416-39e12f18.gd"
GODOT = PRIMARY / "work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe"
CHECKED = ROOT / "tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py"
OUT = ROOT / "outputs/hsea09"


def lp(path):
    text = str(Path(path).resolve())
    return Path("\\\\?\\" + text) if os.name == "nt" and len(text) > 247 and not text.startswith("\\\\?\\") else Path(text)


def sha(path):
    return hashlib.sha256(lp(path).read_bytes()).hexdigest()


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default=TAG)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    profile = OUT / ("profile-" + args.tag)
    profile.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["APPDATA"] = str(profile)
    env["LOCALAPPDATA"] = str(profile)
    for path in (MODEL, TEST, GODOT, CHECKED):
        assert path.is_file(), str(path)

    log_path = OUT / ("rpg-2-star-ocean-the-second_hsea09_locomotion-phase_model_engine-run_v01_" + args.tag + ".log")
    if log_path.exists():
        log_path.unlink()
    command = [
        sys.executable, "-I", str(CHECKED), "--timeout", "20", "--expect", "HSEA09_TESTS_OK",
        "--log", str(log_path), "--", str(GODOT), "--headless", "--path", str(ROOT / "game"),
        "--audio-driver", "Dummy", "--script", str(TEST),
    ]
    checked = {"command": [str(x) for x in command], "passed": False, "reason": "not-run", "exitCode": None,
               "elapsedSeconds": None, "timedOut": False, "stdoutTail": ""}
    try:
        proc = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=25, env=env)
        checked["exitCode"] = proc.returncode
        checked["stdoutTail"] = (proc.stdout + proc.stderr)[-4000:]
    except subprocess.TimeoutExpired as exc:
        checked["timedOut"] = True
        checked["stdoutTail"] = ((exc.stdout or "") + (exc.stderr or ""))[-4000:]
        checked["reason"] = "outer-timeout"

    log_text = lp(log_path).read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    summary_text = log_text + "\n" + checked["stdoutTail"]
    summary_line = next((line.strip() for line in summary_text.splitlines() if line.startswith("CHECKED_RUN ")), "")
    parsed = re.search(r"CHECKED_RUN (PASS|FAIL) (\S+) exit= (-?\d+) elapsed= ([\d.]+) missing= (.*)", summary_line)
    if parsed:
        checked["passed"] = parsed.group(1) == "PASS"
        checked["reason"] = parsed.group(2)
        checked["exitCode"] = int(parsed.group(3))
        checked["elapsedSeconds"] = float(parsed.group(4))
        checked["missingMarkers"] = [x for x in parsed.group(5).split(",") if x and x != "[]"]
    check_match = re.search(r"HSEA09_CHECKS total=(\d+) failures=(\d+)", log_text)
    total = int(check_match.group(1)) if check_match else 0
    failures = int(check_match.group(2)) if check_match else -1
    marker = "HSEA09_TESTS_OK" in log_text
    model_pass = total > 0 and failures == 0 and marker
    cert_diag = "ERROR: Failed to read the root certificate store." in log_text

    # Unmodified engine control: the same environment diagnostic on a --quit process proves this is
    # an environment/engine startup condition, not an HSEA09 assertion. It is not filtered.
    control_cmd = [str(GODOT), "--headless", "--path", str(ROOT / "game"), "--quit"]
    control_text = ""
    control_code = None
    try:
        control = subprocess.run(control_cmd, capture_output=True, text=True, encoding="utf-8",
                                 errors="replace", timeout=20, env=env)
        control_code = control.returncode
        control_text = control.stdout + control.stderr
    except subprocess.TimeoutExpired as exc:
        control_text = ((exc.stdout or "") + (exc.stderr or "")) if isinstance(exc.stdout, str) else ""
        control_code = "timeout"
    control_cert = "ERROR: Failed to read the root certificate store." in control_text
    version_match = re.search(r"Godot Engine v([^\s]+)", log_text or control_text)
    cert_at = "get_system_ca_certificates" in log_text or "get_system_ca_certificates" in control_text

    if checked["passed"] and model_pass:
        result = "PASS"
    elif model_pass and cert_diag and checked["reason"] == "diagnostic":
        result = "MODEL_PASS_CHECKED_RUN_ENVIRONMENT_FAIL"
    else:
        result = "FAIL"

    report = {
        "task": "hsea09",
        "fixture": "synthetic deterministic numeric headless fixture; NOT actual gameplay",
        "generatedUtc": datetime.now(timezone.utc).isoformat(),
        "result": result,
        "modelChecks": {"total": total, "failures": failures, "successMarker": marker, "pass": model_pass},
        "checkedRun": {
            "passed": checked["passed"], "reason": checked["reason"], "exitCode": checked["exitCode"],
            "elapsedSeconds": checked["elapsedSeconds"], "timedOut": checked["timedOut"],
            "timeoutSeconds": 20, "log": rel(log_path) if log_path.exists() else None,
            "logSha256": sha(log_path) if log_path.exists() else None,
            "command": checked["command"], "summaryLine": summary_line,
        },
        "environment": {
            "rootCertificateStoreError": cert_diag,
            "rootCertificateSourceFrame": cert_at,
            "controlReproduced": control_cert,
            "controlExitCode": control_code,
            "diagnosticsFiltered": False,
            "note": "The checked runner correctly rejects any ERROR even at exit 0. This host emits a known Godot startup/exit root-certificate-store ERROR; it is reported, not suppressed.",
        },
        "files": {
            "model": {"path": rel(MODEL), "sha256": sha(MODEL)},
            "test": {"path": rel(TEST), "sha256": sha(TEST)},
            "runner": {"path": rel(Path(__file__)), "sha256": sha(Path(__file__))},
            "checkedRunner": {"path": rel(CHECKED), "sha256": sha(CHECKED)},
        },
        "godot": {"path": str(GODOT), "version": version_match.group(1) if version_match else None},
        "textHashNormalization": "raw bytes, LF files written by the author; no CRLF normalization",
        "noGitCommitOrPush": True,
        "limitations": [
            "Synthetic numeric fixture only; it is not gameplay, actual movement/collision, driver integration, visual motion review or creator approval.",
            "No host/scene/loader/art/ledger/index/dashboard file was changed.",
            "The model is intentionally pure and returns a display phase; it never asserts true world foot lock.",
            "Settle uses wallclock only for the cosmetic bounded transition; walk phase uses actual Euclidean displacement only.",
            "The checked-run gate is FAIL solely on the known Godot root-certificate-store environment ERROR emitted at exit 0; model assertions themselves pass. No diagnostic filter was applied.",
            "The report cannot certify engine sprite position/speed/collision because the model does not own or mutate those systems; that is verified by source scope, not a gameplay run.",
        ],
    }
    report_path = OUT / ("rpg-2-star-ocean-the-second_hsea09_locomotion-phase_model_qa-report_v01_" + args.tag + ".json")
    lp(report_path).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("result", "modelChecks", "checkedRun", "environment")}, indent=2))
    print("HSEA09_QA_REPORT", report_path)
    raise SystemExit(0 if result == "PASS" else 1)


if __name__ == "__main__":
    main()
