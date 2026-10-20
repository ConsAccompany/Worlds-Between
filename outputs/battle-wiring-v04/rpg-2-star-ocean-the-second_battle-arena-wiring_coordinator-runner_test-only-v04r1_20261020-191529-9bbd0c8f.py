#!/usr/bin/env python3
"""Minimal coordinator runner for content.scene.battle-arena.wiring v04.

v04r1 fixes the v04 runner's raw-hash comparison: the fixture deliberately adds
the --self test source to both hash maps, so the runner must compare the seven
game paths (and allow exactly the self-test extra key), not the full map.

The producer did NOT run Godot: the v03 sandbox attempt had an unfiltered Windows
root-certificate diagnostic. This runner is the single execution path for the
coordinator's ordinary (canonical) context. It:

* invokes the original checked runner by exact absolute path, with an argv list
  (never a shell string), and no diagnostic filtering or trust/validation change;
* creates fresh APPDATA/LOCALAPPDATA/TEMP dirs under this task worktree;
* optionally performs a bounded headless import preflight only when the game
  checkout has no populated .godot/imported cache;
* runs the normal windowed 640x360 EN/ZH fixture with a 90 s Godot limit;
* enforces a finite whole-run deadline and a clean Git game tree;
* verifies the report, exact save/reward/return checks, 27 actual 640x360
  captures, raw+LF 99bf35a source hashes, and the expected marker;
* writes a uniquely named run manifest and prints BATTLE_WIRING_V04_RUN_PASS.

No network, credentials, billing, game, ledger, registry or index writes.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone

PROJECT = "rpg-2-star-ocean-the-second"
SUBJECT = "battle-arena-wiring"
VARIANT = "test-only-v04"
EXPECTED_MARKER = "BATTLE_WIRING_OK"
BASE_COMMIT = "99bf35affa8fd332802c3922a1c632e9ea22695e"
GODOT_LIMIT_SECONDS = 90
WHOLE_RUN_SECONDS = 240

WORKTREE = Path(r"C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\dual05\ds-wiring")
PYTHON = Path(r"C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
CHECKED_RUNNER = WORKTREE / "tools" / "rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py"
GODOT = Path(r"C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\tooling\godot-4-7-2\Godot_v4.7.2-stable_win64_console.exe")
GAME = WORKTREE / "game"
OUTPUTS = WORKTREE / "outputs" / "battle-wiring-v04"
FIXTURE = OUTPUTS / "rpg-2-star-ocean-the-second_battle-arena-wiring_natural-victory-check_test-only-v04_20261020-190935-51fe4e36.gd"
GIT = Path(r"C:\Program Files\Git\bin\git.exe")

EXPECTED_RAW = {
    "res://scripts/battle_arena.gd": "d7c4fb46bbdff55596aac443d7eafc470be51728f00a78f2cc45b1a2301dec95",
    "res://scripts/scifi_exploration_area.gd": "13f89322c328598fcaeac94536182aef2e936bbf33a61a1bf89f741f9806b4b3",
    "res://scripts/app_state.gd": "e3a162ef3d70aafbb97f4a668b69813dc8aed3e327ee6a87b398aba29fdbc33f",
    "res://scripts/save_store.gd": "88c2d71d1f9faa0c7a840b2098a146808e0a1ef6d1f7315f2951a00eacdd7a0a",
    "res://scripts/battle_rules.gd": "e95400251485fce27d496c0a100ec9fe1a1f2e2430bb5f9c6899497370a3263c",
    "res://scenes/battle_arena.tscn": "dfd2ed1ce9642a4519926e3aa45dae5bd2b6bad11dfa0f3152d5cf80de9d4310",
    "res://scenes/scifi_exploration_area.tscn": "b3be08cde8a8d9c4fa0edaa49c3ef30965291691d1b3c30184776ec3553b8ae8",
}
EXPECTED_LF = {
    "res://scripts/battle_arena.gd": "d7c4fb46bbdff55596aac443d7eafc470be51728f00a78f2cc45b1a2301dec95",
    "res://scripts/scifi_exploration_area.gd": "13f89322c328598fcaeac94536182aef2e936bbf33a61a1bf89f741f9806b4b3",
    "res://scripts/app_state.gd": "60f3622f1dfcaa554861391b552442636a7870c7d250de4c4122da9245c4f2ee",
    "res://scripts/save_store.gd": "0980b722686e05a227bee8c71bfe6a04ee71c84826937a552b0248e5ebeff6d1",
    "res://scripts/battle_rules.gd": "98d0ed2e9b723859cdd42782f57e222c66e2b61b3f9772fa2cd72f44c09cca7b",
    "res://scenes/battle_arena.tscn": "a41247599f910aabd35bfd8e4015a2ff3e4ab22dafe19a73b11044ba3743e322",
    "res://scenes/scifi_exploration_area.tscn": "b60cf71490b5aacb0163c3336cefefac7b7ed16de6940924f875d23499a5cdc7",
}


def die(message: str) -> "NoReturn":
    print("BATTLE_WIRING_V04_RUN_FAIL", message)
    raise SystemExit(1)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def game_path(res_path: str) -> Path:
    if not res_path.startswith("res://"):
        raise ValueError(res_path)
    return GAME / res_path[len("res://"):].replace("/", os.sep)


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("not a PNG with IHDR")
    return struct.unpack(">II", header[16:24])


def write_log(path: Path, text: str) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def append_log(path: Path, text: str) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def git(args: list[str]) -> dict:
    command = [str(GIT), "-C", str(WORKTREE), *args]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=30)
    return {"command": command, "exitCode": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}


def kill_tree(pid: int) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    else:
        try:
            os.killpg(pid, 9)
        except ProcessLookupError:
            pass


def run_bounded(command: list[str], timeout: float, env: dict) -> tuple[int | None, str, bool]:
    if timeout <= 1:
        return None, "", True
    flags = 0
    if os.name == "nt":
        flags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, encoding="utf-8", errors="replace",
                               cwd=str(WORKTREE), env=env, creationflags=flags)
    try:
        output, _ = process.communicate(timeout=timeout)
        return process.returncode, output, False
    except subprocess.TimeoutExpired:
        kill_tree(process.pid)
        try:
            output, _ = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            output = ""
        return None, output, True


def main() -> None:
    started = time.monotonic()
    deadline = started + WHOLE_RUN_SECONDS
    if "--plan" in sys.argv[1:]:
        plan = {
            "status": "PENDING_COORDINATOR_RUN",
            "wholeRunDeadlineSeconds": WHOLE_RUN_SECONDS,
            "godotLimitSecondsPerProcess": GODOT_LIMIT_SECONDS,
            "python": str(PYTHON),
            "checkedRunner": str(CHECKED_RUNNER),
            "godot": str(GODOT),
            "game": str(GAME),
            "fixture": str(FIXTURE),
            "expectedMarker": EXPECTED_MARKER,
            "baseCommit": BASE_COMMIT,
            "note": "Import preflight runs only when game/.godot/imported is missing or empty.",
        }
        print(json.dumps(plan, indent=2))
        return

    for path in (PYTHON, CHECKED_RUNNER, GODOT, FIXTURE, GAME, GIT):
        if not path.exists():
            die(f"required path missing: {path}")

    head = git(["rev-parse", "HEAD"])
    if head["exitCode"] != 0 or head["stdout"].strip() != BASE_COMMIT:
        die(f"HEAD is not the declared {BASE_COMMIT}: {head}")
    status_before = git(["status", "--porcelain", "--", "game"])
    if status_before["exitCode"] != 0 or status_before["stdout"].strip():
        die(f"game tree is not clean before run: {status_before}")

    uid = uuid.uuid4().hex
    uid8 = uid[:8]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_dir = OUTPUTS / f"run-{uid8}"
    captures_dir = OUTPUTS / f"caps-{uid8}"
    appdata = run_dir / "appdata"
    localappdata = run_dir / "localappdata"
    temp = run_dir / "temp"
    for directory in (run_dir, captures_dir, appdata, localappdata, temp):
        directory.mkdir(parents=True, exist_ok=False)

    prefix = f"{PROJECT}_{SUBJECT}"
    report_path = OUTPUTS / f"{prefix}_natural-victory-report_{VARIANT}_{stamp}-{uid8}.json"
    raw_log = OUTPUTS / f"{prefix}_natural-victory-raw_{VARIANT}_{stamp}-{uid8}.log"
    import_log = OUTPUTS / f"{prefix}_import-raw_{VARIANT}_{stamp}-{uid8}.log"
    checked_stdout_log = OUTPUTS / f"{prefix}_checked-run-stdout_{VARIANT}_{stamp}-{uid8}.log"
    manifest_path = OUTPUTS / f"{prefix}_run-manifest_{VARIANT}_{stamp}-{uid8}.json"

    for path in (report_path, raw_log, import_log, checked_stdout_log, manifest_path):
        if path.exists():
            die(f"refusing to overwrite existing evidence: {path}")

    env = os.environ.copy()
    env["APPDATA"] = str(appdata)
    env["LOCALAPPDATA"] = str(localappdata)
    env["TEMP"] = str(temp)
    env["TMP"] = str(temp)
    trust_env = {key: env.get(key) for key in ("SSL_CERT_FILE", "SSL_CERT_DIR") if key in env}

    manifest: dict = {
        "project": PROJECT,
        "subject": SUBJECT,
        "purpose": "coordinator-run-manifest",
        "variant": VARIANT,
        "timestampUtc": now_iso(),
        "uuid": uid,
        "status": "FAIL",
        "expectedMarker": EXPECTED_MARKER,
        "testedCommit": BASE_COMMIT,
        "worktree": str(WORKTREE),
        "resolution": "640x360",
        "runMode": "windowed",
        "freshDirs": {"run": str(run_dir), "captures": str(captures_dir),
                      "appdata": str(appdata), "localappdata": str(localappdata),
                      "temp": str(temp)},
        "paths": {"report": str(report_path), "rawLog": str(raw_log),
                  "importLog": str(import_log), "checkedStdoutLog": str(checked_stdout_log),
                  "manifest": str(manifest_path), "fixture": str(FIXTURE)},
        "trustEnvUnchanged": trust_env,
        "gameStatusBefore": status_before,
        "wholeRunDeadlineSeconds": WHOLE_RUN_SECONDS,
        "godotLimitSecondsPerProcess": GODOT_LIMIT_SECONDS,
    }

    stdout_parts: list[str] = []

    def finish(status: str, reason: str | None = None, extra: dict | None = None) -> None:
        manifest["status"] = status
        manifest["finishedUtc"] = now_iso()
        manifest["elapsedSeconds"] = round(time.monotonic() - started, 3)
        if reason:
            manifest["failure"] = reason
        if extra:
            manifest.update(extra)
        try:
            write_log(checked_stdout_log, "".join(stdout_parts))
        except FileExistsError:
            pass
        write_log(manifest_path, json.dumps(manifest, indent=2) + "\n")
        print("MANIFEST", manifest_path)
        if status == "PASS":
            print("EXPECTED_MARKER", EXPECTED_MARKER)
            print("BATTLE_WIRING_V04_RUN_PASS")
            print("REPORT", report_path)
            print("CAPTURES", captures_dir)
        else:
            print("BATTLE_WIRING_V04_RUN_FAIL", reason)
            print("RAW_LOG", raw_log)
        raise SystemExit(0 if status == "PASS" else 1)

    imported_cache = GAME / ".godot" / "imported"
    needs_import = not imported_cache.is_dir() or not any(imported_cache.iterdir())
    import_result = {"skipped": not needs_import}
    if needs_import:
        remaining = deadline - time.monotonic()
        if remaining <= 5:
            finish("FAIL", "whole-run deadline exhausted before import")
        import_command = [str(PYTHON), str(CHECKED_RUNNER), "--timeout", str(GODOT_LIMIT_SECONDS),
                          "--log", str(import_log), "--", str(GODOT), "--headless",
                          "--path", str(GAME), "--import"]
        code, output, timed_out = run_bounded(import_command, min(GODOT_LIMIT_SECONDS + 10, remaining), env)
        stdout_parts.append("=== IMPORT PREFLIGHT ===\n")
        stdout_parts.append(output)
        import_result = {"skipped": False, "exitCode": code, "timedOut": timed_out,
                         "command": import_command, "rawLog": str(import_log)}
        if timed_out or code != 0:
            finish("FAIL", "import preflight did not pass; see import raw log", {"import": import_result})
    manifest["import"] = import_result

    remaining = deadline - time.monotonic()
    if remaining <= 5:
        finish("FAIL", "whole-run deadline exhausted before Godot test", {"import": import_result})
    godot_args = [str(GODOT), "--windowed", "--path", str(GAME), "--resolution", "640x360",
                  "-s", str(FIXTURE), "--", f"--report={report_path}",
                  f"--captures={captures_dir}", f"--base={BASE_COMMIT}", f"--self={FIXTURE}",
                  f"--uuid={uid}"]
    checked_command = [str(PYTHON), str(CHECKED_RUNNER), "--timeout", str(GODOT_LIMIT_SECONDS),
                       "--expect", EXPECTED_MARKER, "--log", str(raw_log), "--", *godot_args]
    code, output, timed_out = run_bounded(checked_command, min(GODOT_LIMIT_SECONDS + 10, remaining), env)
    stdout_parts.append("=== CHECKED GODOT RUN ===\n")
    stdout_parts.append(output)
    manifest["checkedRunner"] = {"exitCode": code, "timedOut": timed_out,
                                 "command": checked_command, "rawLog": str(raw_log)}
    if timed_out or code != 0:
        finish("FAIL", "checked runner did not pass; no result is claimed", {"import": import_result})

    if not raw_log.exists():
        finish("FAIL", "checked runner passed but raw log is missing", {"import": import_result})
    raw_text = raw_log.read_text(encoding="utf-8", errors="replace")
    if EXPECTED_MARKER not in raw_text:
        finish("FAIL", "raw log lacks the expected marker", {"import": import_result})
    if "ERROR:" in raw_text or "SCRIPT ERROR:" in raw_text or "Parse Error:" in raw_text:
        finish("FAIL", "raw log contains a diagnostic despite runner exit 0", {"import": import_result})

    case_lines = [line for line in raw_text.splitlines() if line.startswith("BATTLE_WIRING_CASE ")]
    expected_hits = {"patrol": 4, "sentry": 6}
    if len(case_lines) != 4:
        finish("FAIL", f"expected 4 natural-victory case lines, got {len(case_lines)}", {"import": import_result})
    case_evidence = []
    for line in case_lines:
        match = re.match(r"BATTLE_WIRING_CASE\s+(\w+)\s+(en|zh)\s+(\{.*\})\s*$", line)
        if not match:
            finish("FAIL", f"unparseable case line: {line[:160]}", {"import": import_result})
        enemy, language, payload_text = match.group(1), match.group(2), match.group(3)
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            finish("FAIL", f"case JSON invalid: {exc}", {"import": import_result})
        hits = expected_hits.get(enemy)
        if hits is None:
            finish("FAIL", f"unexpected enemy in case line: {enemy}", {"import": import_result})
        setup_x = payload.get("setupX")
        positions = payload.get("positionsAtHit", [])
        cooldowns = payload.get("cooldownsAtHit", [])
        if setup_x is None or not isinstance(positions, list) or not isinstance(cooldowns, list):
            finish("FAIL", f"case line lacks single-setup evidence: {enemy} {language}", {"import": import_result})
        valid = (
            payload.get("category") == "victory"
            and payload.get("expectedHits") == hits
            and payload.get("attacks") == hits
            and len(payload.get("hitSteps", [])) == hits
            and len(payload.get("hpTrace", [])) == hits
            and len(positions) == hits
            and len(cooldowns) == hits
            and all(abs(float(value) - float(setup_x)) <= 1e-9 for value in positions)
            and all(float(value) == 0.0 for value in cooldowns)
            and int(payload.get("enemyAttacks", 0)) >= 1
            and str(payload.get("save", "")).startswith("auto-")
            and len(payload.get("return", [])) == 2
        )
        if not valid:
            finish("FAIL", f"natural-victory case evidence invalid: {enemy} {language}", {"import": import_result})
        case_evidence.append({"enemy": enemy, "language": language, "hits": hits,
                              "steps": payload.get("steps"), "save": payload.get("save"),
                              "setupX": setup_x, "enemyAttacks": payload.get("enemyAttacks")})

    defeat_lines = [line for line in raw_text.splitlines() if line.startswith("BATTLE_WIRING_DEFEAT_CASE ")]
    if len(defeat_lines) != 1:
        finish("FAIL", f"expected one labeled defeat case, got {len(defeat_lines)}", {"import": import_result})
    defeat_match = re.match(r"BATTLE_WIRING_DEFEAT_CASE\s+(\w+)\s+(en|zh)\s+(\{.*\})\s*$", defeat_lines[0])
    if not defeat_match or json.loads(defeat_match.group(3)).get("category") != "defeat":
        finish("FAIL", "labeled defeat case evidence invalid", {"import": import_result})
    defeat_payload = json.loads(defeat_match.group(3))
    if int(defeat_payload.get("enemyAttacks", 0)) < 1 or int(defeat_payload.get("hp", -1)) != 0:
        finish("FAIL", "labeled defeat case did not reach 0 HP from real contacts", {"import": import_result})

    if not report_path.exists():
        finish("FAIL", "report JSON missing", {"import": import_result})
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report every parse failure
        finish("FAIL", f"report JSON unreadable: {exc}", {"import": import_result})

    report_checks = {
        "variant": report.get("variant") == "natural-victory-v04",
        "baseCommit": report.get("baseCommit") == BASE_COMMIT,
        "testedCommit": report.get("testedCommit") == BASE_COMMIT,
        "failedZero": report.get("failed") == 0,
        "passedEqualsTotal": isinstance(report.get("total"), int)
        and report.get("passed") == report.get("total") and report.get("total", 0) > 0,
        "victoryCategory": report.get("categorySummary", {}).get("victory", {}).get("failed") == 0
        and report.get("categorySummary", {}).get("victory", {}).get("total", 0) > 0,
        "defeatCategory": report.get("categorySummary", {}).get("defeat", {}).get("failed") == 0
        and report.get("categorySummary", {}).get("defeat", {}).get("total", 0) > 0,
        "naturalCases": report.get("naturalVictory", {}).get("cases") == 4
        and report.get("naturalVictory", {}).get("countedAsVictory") is True,
        "defeatCase": report.get("defeat", {}).get("executed") is True
        and report.get("defeat", {}).get("countedAsVictory") is False
        and report.get("defeat", {}).get("label") == "DEFEAT-ONLY"
        and report.get("defeat", {}).get("result", {}).get("category") == "defeat",
        "protectedStats": report.get("protectedStats", {}).get("patrol", {}).get("max_hp") == 64
        and report.get("protectedStats", {}).get("patrol", {}).get("damage") == 12
        and report.get("protectedStats", {}).get("sentry", {}).get("max_hp") == 96
        and report.get("protectedStats", {}).get("sentry", {}).get("damage") == 18
        and report.get("protectedStats", {}).get("heroAttackDamage") == 19
        and report.get("protectedStats", {}).get("heroAttackRange") == 61.0,
    }
    for name, passed in report_checks.items():
        if not passed:
            finish("FAIL", f"report predicate failed: {name}", {"import": import_result, "report": str(report_path)})

    computed_raw = {path: sha256_file(game_path(path)) for path in EXPECTED_RAW}
    computed_lf = {path: sha256_lf(game_path(path)) for path in EXPECTED_LF}
    if computed_raw != EXPECTED_RAW or computed_lf != EXPECTED_LF:
        finish("FAIL", "current game source bytes no longer match the 99bf35a hashes", {"import": import_result})
    report_raw = report.get("sourceHashesSha256RawV1", {})
    report_lf = report.get("sourceHashesSha256TextLfV1", {})
    for path, value in computed_raw.items():
        if report_raw.get(path) != value:
            finish("FAIL", f"report raw hash mismatch: {path}", {"import": import_result})
    for path, value in computed_lf.items():
        if report_lf.get(path) != value:
            finish("FAIL", f"report LF hash mismatch: {path}", {"import": import_result})
    allowed_extra = {str(FIXTURE)}
    if set(report_raw) - set(computed_raw) != allowed_extra:
        finish("FAIL", "report raw hash map has an unexpected extra key", {"import": import_result})
    if set(report_lf) - set(computed_lf) != allowed_extra:
        finish("FAIL", "report LF hash map has an unexpected extra key", {"import": import_result})

    capture_rows = report.get("captures", [])
    if not isinstance(capture_rows, list) or len(capture_rows) != 27:
        finish("FAIL", f"expected 27 capture records, got {len(capture_rows)}", {"import": import_result})
    actual_pngs = sorted(captures_dir.glob("*.png"))
    if len(actual_pngs) != 27:
        finish("FAIL", f"expected 27 capture files, got {len(actual_pngs)}", {"import": import_result})
    capture_evidence = []
    for row in capture_rows:
        name = str(row.get("file", ""))
        path = captures_dir / name
        if not name or not path.is_file():
            finish("FAIL", f"capture missing: {name}", {"import": import_result})
        if f"-{uid8}.png" not in name or f"_{VARIANT}_" not in name:
            finish("FAIL", f"capture is not uniquely bound to this run: {name}", {"import": import_result})
        width, height = png_size(path)
        digest = sha256_file(path)
        if (width, height) != (640, 360) or digest != row.get("sha256"):
            finish("FAIL", f"capture mismatch: {name}", {"import": import_result})
        if str(row.get("display", "")).lower() == "headless":
            finish("FAIL", f"capture was taken headless: {name}", {"import": import_result})
        capture_evidence.append({"file": name, "sha256": digest, "width": width, "height": height})

    status_after = git(["status", "--porcelain", "--", "game"])
    if status_after["exitCode"] != 0 or status_after["stdout"].strip():
        finish("FAIL", f"game tree is not clean after run: {status_after}", {"import": import_result})
    if status_after["stdout"] != status_before["stdout"]:
        finish("FAIL", "game tree status changed during run", {"import": import_result})

    finish("PASS", None, {
        "import": import_result,
        "reportSummary": {
            "variant": report.get("variant"),
            "testedCommit": report.get("testedCommit"),
            "passed": report.get("passed"),
            "total": report.get("total"),
            "failed": report.get("failed"),
            "categorySummary": report.get("categorySummary"),
            "naturalVictory": report.get("naturalVictory"),
            "defeat": {k: v for k, v in report.get("defeat", {}).items() if k != "result"},
            "saveIds": [row.get("save") for row in report.get("checks", [])
                        if isinstance(row, dict) and row.get("category") == "victory"
                        and isinstance(row.get("detail"), dict) and row["detail"].get("saveId")],
        },
        "captures": capture_evidence,
        "sourceHashesSha256RawV1": computed_raw,
        "sourceHashesSha256TextLfV1": computed_lf,
        "gameStatusAfter": status_after,
    })


if __name__ == "__main__":
    main()
