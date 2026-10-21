"""Launch the male playable path using the existing isolated-profile launcher.

    python <this> play --language en
    python <this> play --dry-run
    python <this> controls

Starts a fresh demonstration run. Its saves/settings stay in work/mpath24-profile;
ordinary player saves and default asset selection are unchanged.
"""
import argparse
import importlib.util
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "tools/rpg-2-star-ocean-the-second_heroine-playable-path_launch-cli_opt-in-v01_20261021-015453-1036fbad.py"
DIRECTORY = "scripts/mpath24/"
STEM = "rpg-2-star-ocean-the-second_male-playable-path_"
SUFFIX = "_opt-in-v01_20261021-170200-5e1c24a7.gd"


def configured_launcher():
    spec = importlib.util.spec_from_file_location("existing_playable_launcher", BASE)
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    base.CONFIG_FILE = ROOT / "game" / DIRECTORY / (STEM + "config" + SUFFIX)
    driver_file = ROOT / "game" / DIRECTORY / (STEM + "explore-driver" + SUFFIX)
    base.ENTRY_RES = "res://" + DIRECTORY + STEM + "entry" + SUFFIX
    base.PROFILE = ROOT / "work/mpath24-profile"
    base.READY_MARKER = "MPATH24_PLAYABLE_READY"

    def pins():
        pairs = {}
        for path, key in [(driver_file, "REGISTRY_PATH"), (base.CONFIG_FILE, "COMBAT_INDEX_PATH")]:
            if path.is_file():
                found = re.search(r'const ' + key + r' := "([^"]+)"', path.read_text(encoding="utf8"))
                if found:
                    pairs[key] = found.group(1)
        return pairs

    base.pinned_paths = pins
    original_plan = base.plan

    def male_plan(args):
        result = original_plan(args)
        result["command"] = [arg.replace("--hsea16-", "--mpath24-") for arg in result["command"]]
        if not base.res_to_path(base.ENTRY_RES).is_file():
            result["problems"].append("male entry missing")
        result["ok"] = not result["problems"]
        result["starts_fresh_demo"] = True
        result["ordinary_defaults_changed"] = False
        return result

    base.plan = male_plan
    return base


def main():
    parser = argparse.ArgumentParser(description="Play the male path in a separate local save profile.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    play = sub.add_parser("play")
    play.add_argument("--language", choices=("en", "zh"), default="en")
    play.add_argument("--destination", choices=("scifi.city", "scifi.outskirts", "scifi.ruins"), default="scifi.outskirts")
    play.add_argument("--dry-run", action="store_true")
    play.add_argument("--godot")
    sub.add_parser("controls")
    args = parser.parse_args()
    base = configured_launcher()
    if args.cmd == "controls":
        base.print_controls()
        return 0
    return base.play(args)


if __name__ == "__main__":
    sys.exit(main())
