"""Launch the Zhao companion playable path using the existing isolated-profile launcher.

    python <this> play --language en
    python <this> play --dry-run
    python <this> controls

Starts a fresh demonstration run. Its saves/settings stay in work/zpath27-profile;
ordinary player saves and default asset selection are unchanged.
"""
import argparse
import importlib.util
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "tools/rpg-2-star-ocean-the-second_heroine-playable-path_launch-cli_opt-in-v01_20261021-015453-1036fbad.py"
DIRECTORY = "scripts/zpath27/"
STEM = "rpg-2-star-ocean-the-second_zhao-playable-path_"
SUFFIX = "_opt-in-v01_20261021-223218-3246d731.gd"


def configured_launcher():
    spec = importlib.util.spec_from_file_location("existing_playable_launcher", BASE)
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    base.CONFIG_FILE = ROOT / "game" / DIRECTORY / (STEM + "config" + SUFFIX)
    driver_file = ROOT / "game" / DIRECTORY / (STEM + "npc-driver" + SUFFIX)
    base.ENTRY_RES = "res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_entry_opt-in-v01_20261021-224100-c713ad29.gd"
    base.PROFILE = ROOT / "work/zpath27-profile"
    base.READY_MARKER = "ZPATH27_PLAYABLE_READY"

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
        result["command"] = [arg.replace("--hsea16-", "--zpath27-") for arg in result["command"]]
        if not base.res_to_path(base.ENTRY_RES).is_file():
            result["problems"].append("male entry missing")
        result["ok"] = not result["problems"]
        result["command"].append("--zpath27-appearance=" + args.appearance)
        result["starts_fresh_demo"] = True
        result["companion_identity_preserved"] = True
        result["ordinary_defaults_changed"] = False
        return result

    base.plan = male_plan
    # Preserve the existing bounded importer, but keep generated logs under this subject's unique name.
    original_prepare = base.prepare_assets
    def prepare(godot, env):
        before = set(base.PROFILE.glob("*asset-preparation*.log"))
        ok = original_prepare(godot, env)
        for old in set(base.PROFILE.glob("*asset-preparation*.log")) - before:
            old.rename(old.with_name(old.name.replace("heroine-playable-path", "zhao-playable-path")))
        return ok
    base.prepare_assets = prepare
    return base


def main():
    parser = argparse.ArgumentParser(description="Play the Zhao companion path in a separate local save profile.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    play = sub.add_parser("play")
    play.add_argument("--language", choices=("en", "zh"), default="en")
    play.add_argument("--destination", choices=("scifi.outskirts",), default="scifi.outskirts")
    play.add_argument("--appearance", choices=("male", "female"), default="male")
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
