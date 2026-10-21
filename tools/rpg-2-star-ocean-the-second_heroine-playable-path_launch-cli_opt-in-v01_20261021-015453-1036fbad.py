"""Launch the opt-in heroine playable path (motion and art UNAPPROVED) in the real game.

    python <this> play [--language en|zh] [--destination scifi.outskirts|scifi.city|scifi.ruins]
    python <this> play --dry-run        # JSON plan only, never starts the engine
    python <this> controls              # plain-language control list read from the game's input setup

The game runs with a separate local profile (work/hsea16-profile, ignored by Git): its settings and
saves never touch the player's normal saves. Uses the existing project Godot console runtime only.
Exit codes: 0 ok, 1 refused/engine failure, 2 invalid arguments.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import threading
from datetime import datetime, timezone
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GAME = REPO / "game"
ENTRY_RES = "res://scripts/hsea16/rpg-2-star-ocean-the-second_heroine-playable-path_entry_opt-in-v01_20261021-015453-1036fbad.gd"
CONFIG_FILE = GAME / "scripts/hsea16/rpg-2-star-ocean-the-second_heroine-playable-path_config_opt-in-v01_20261021-015453-1036fbad.gd"
PROFILE = REPO / "work" / "hsea16-profile"
GODOT_REL = Path("work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe")
LANGUAGES = ("en", "zh")
DESTINATIONS = ("scifi.outskirts", "scifi.city", "scifi.ruins")
READY_MARKER = "HSEA16_PLAYABLE_READY"
CONTROL_LABELS = {
    "move_up": "Move up", "move_down": "Move down", "move_left": "Move left", "move_right": "Move right",
    "interact": "Talk / examine", "battle_attack": "Attack", "battle_dodge": "Dodge", "battle_guard": "Guard",
    "battle_skill": "Skill", "battle_job_skill": "Job skill", "battle_switch": "Switch character",
    "battle_auto": "Auto battle", "battle_pause": "Battle orders (pause)",
}


def res_to_path(res: str) -> Path:
    return GAME / res.removeprefix("res://")


def pinned_paths() -> dict[str, str]:
    text = CONFIG_FILE.read_text(encoding="utf-8")
    found = dict(re.findall(r'const (REGISTRY_PATH|COMBAT_INDEX_PATH) := "([^"]+)"', text))
    return found


def find_godot(explicit: str | None) -> Path | None:
    if explicit:
        return Path(explicit)
    # Bounded walk up from this checkout only; no home-directory scanning.
    for ancestor in [REPO, *REPO.parents][:6]:
        candidate = ancestor / GODOT_REL
        if candidate.is_file():
            return candidate
    return None


def read_controls() -> list[dict[str, str]]:
    source = (GAME / "scripts/app_state.gd").read_text(encoding="utf-8")
    keys: dict[str, list[str]] = {}
    for action, key in re.findall(r'_add_key_action\("(\w+)", KEY_(\w+)\)', source):
        keys.setdefault(action, []).append(key.title() if len(key) > 1 else key)
    rows = [{"action": CONTROL_LABELS.get(a, a), "keys": " / ".join(k)} for a, k in keys.items()]
    rows.append({"action": "Back / cancel", "keys": "Escape"})
    return rows


def plan(args: argparse.Namespace) -> dict:
    godot = find_godot(args.godot)
    pins = pinned_paths()
    missing = [res for res in pins.values() if not res_to_path(res).is_file()]
    problems = []
    if godot is None or not godot.is_file():
        problems.append("Godot console runtime not found")
    if len(pins) != 2:
        problems.append("config pins unreadable")
    problems += ["pinned file missing: " + res for res in missing]
    command = [str(godot) if godot else "<missing>", "--path", str(GAME), "-s", ENTRY_RES, "--",
               f"--hsea16-language={args.language}", f"--hsea16-destination={args.destination}"]
    return {"ok": not problems, "problems": problems, "language": args.language,
            "destination": args.destination, "profile_dir": str(PROFILE), "command": command,
            "pinned": pins, "art_and_motion": "UNAPPROVED", "controls": read_controls()}


def play(args: argparse.Namespace) -> int:
    info = plan(args)
    if args.dry_run:
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return 0 if info["ok"] else 1
    if not info["ok"]:
        print("Cannot start: " + "; ".join(info["problems"]), file=sys.stderr)
        return 1
    PROFILE.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, APPDATA=str(PROFILE), LOCALAPPDATA=str(PROFILE))
    print("Preparing game assets...", flush=True)
    import_command = [info["command"][0], "--headless", "--path", str(GAME), "--editor", "--import", "--quit"]
    prepared = subprocess.run(import_command, env=env, capture_output=True, text=True, encoding="utf8", errors="replace", timeout=120)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    import_text = prepared.stdout + prepared.stderr
    (PROFILE / ("rpg-2-star-ocean-the-second_heroine-playable-path_asset-preparation_v01_" + stamp + ".log")).write_text(import_text, encoding="utf8")
    if prepared.returncode != 0 or "SCRIPT_ERROR" in import_text or any(line.lstrip().startswith("ERROR:") for line in import_text.splitlines()):
        print("Game assets could not be prepared. See the local preview log.", file=sys.stderr)
        return 1
    print_controls()
    proc = subprocess.Popen(info["command"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace")
    ready_event = threading.Event()
    failed_event = threading.Event()
    def stop_owned():
        if proc.poll() is None:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                proc.terminate()
    def startup_deadline():
        if not ready_event.is_set() and proc.poll() is None:
            failed_event.set()
            print("The game did not become ready within 20 seconds.", file=sys.stderr, flush=True)
            stop_owned()
    timer = threading.Timer(20.0, startup_deadline)
    timer.daemon = True
    timer.start()
    try:
        for line in proc.stdout:
            sys.stdout.write(line)
            if "SCRIPT_ERROR" in line or line.lstrip().startswith("ERROR:"):
                failed_event.set()
                stop_owned()
            if READY_MARKER in line and not ready_event.is_set():
                ready_event.set()
                timer.cancel()
                print("Game is ready. Close the game window to finish.", flush=True)
        code = proc.wait()
    finally:
        timer.cancel()
    return 0 if ready_event.is_set() and not failed_event.is_set() and code == 0 else 1


def print_controls() -> None:
    print("Controls:")
    for row in read_controls():
        print(f"  {row['action']:<24} {row['keys']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Play the heroine path (unapproved art and motion).")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("play", help="start the game at the heroine path")
    p.add_argument("--language", choices=LANGUAGES, default="en")
    p.add_argument("--destination", choices=DESTINATIONS, default="scifi.outskirts")
    p.add_argument("--dry-run", action="store_true", help="print the JSON launch plan; do not start the engine")
    p.add_argument("--godot", help="explicit Godot console executable")
    sub.add_parser("controls", help="list the game controls")
    args = parser.parse_args(argv)
    if args.cmd == "controls":
        print_controls()
        return 0
    return play(args)


if __name__ == "__main__":
    sys.exit(main())
