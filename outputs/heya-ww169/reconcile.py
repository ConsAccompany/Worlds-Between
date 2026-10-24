"""Batch169 reconciliation for Heya west-walk (content.char.heya.walk-west).

Read-only over existing batch167 bytes and the fresh staging build. Verifies:
  1. fresh staged game package == installed game package (all bytes);
  2. fresh staged source outputs == existing batch167 source outputs, except the
     deliberately preserved pre-repair failed check-result, whose fixed PASS bytes
     are retained under the "-a6d5390a" suffix;
  3. all installed runtime JSON references resolve;
  4. the 41 manifest frame hashes match both output and installed PNGs;
  5. the protected Heya west static dependency still matches its pins.

Writes only outputs/heya-ww169/reconcile-summary.json.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STAGE = os.path.join(ROOT, "outputs/heya-ww169/stage")
OUT_EXIST = os.path.join(ROOT, "outputs/heya-ww167")
GAME_EXIST = os.path.join(ROOT, "game/assets/characters/heya-native-v01/west-walk")
MANIFEST = os.path.join(
    OUT_EXIST,
    "rpg-2-star-ocean-the-second_heya_walk-source-manifest_unapproved-hww167-v01_20261024-144500-85f7d9bf.json",
)
OLD_FAIL = os.path.join(
    OUT_EXIST,
    "rpg-2-star-ocean-the-second_heya_walk-check-result-check_unapproved-hww167-v01_20261024-144500-387414de.json",
)
FIXED_PASS = os.path.join(
    OUT_EXIST,
    "rpg-2-star-ocean-the-second_heya_walk-check-result-check_unapproved-hww167-v01_20261024-144500-387414de-a6d5390a.json",
)
STAGE_PASS = os.path.join(
    STAGE,
    "outputs/heya-ww167/rpg-2-star-ocean-the-second_heya_walk-check-result-check_unapproved-hww167-v01_20261024-144500-387414de.json",
)
OUT_ROOT_REL = "outputs/heya-ww167"
GAME_ROOT_REL = "game/assets/characters/heya-native-v01/west-walk"


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def tree(root):
    found = {}
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            found[os.path.relpath(p, root)] = p
    return found


def main():
    errors = []
    stage_out = tree(os.path.join(STAGE, OUT_ROOT_REL))
    exist_out = tree(OUT_EXIST)
    stage_game = tree(os.path.join(STAGE, GAME_ROOT_REL))
    exist_game = tree(GAME_EXIST)

    game_diff = [
        rel for rel in sorted(set(stage_game) & set(exist_game))
        if sha(stage_game[rel]) != sha(exist_game[rel])
    ]
    if set(stage_game) != set(exist_game):
        errors.append("game path set differs")
    if game_diff:
        errors.append("game bytes differ: " + ", ".join(game_diff))

    out_missing = sorted(set(stage_out) - set(exist_out))
    out_diff = [
        rel for rel in sorted(set(stage_out) & set(exist_out))
        if sha(stage_out[rel]) != sha(exist_out[rel])
    ]
    if out_missing:
        errors.append("staged outputs missing from existing: " + ", ".join(out_missing))

    old_fail_rel = os.path.relpath(OLD_FAIL, OUT_EXIST)
    fixed_pass_rel = os.path.relpath(FIXED_PASS, OUT_EXIST)
    stage_pass_rel = os.path.relpath(STAGE_PASS, os.path.join(STAGE, OUT_ROOT_REL))
    if out_diff != [old_fail_rel]:
        errors.append("unexpected staged/existing source-output differences: " + repr(out_diff))
    if sha(STAGE_PASS) != sha(FIXED_PASS):
        errors.append("fixed PASS bytes differ between staging and retained batch167 result")
    old_fail = json.load(open(OLD_FAIL, encoding="utf8"))
    fixed_pass = json.load(open(FIXED_PASS, encoding="utf8"))
    if old_fail.get("fails") == [] or old_fail.get("rebuild", {}).get("ok") != 0:
        errors.append("preserved old check-result is not the expected pre-repair failure")
    if fixed_pass.get("fails") != [] or fixed_pass.get("rebuild", {}).get("ok") != 91:
        errors.append("fixed check-result is not the expected PASS")

    manifest = json.load(open(MANIFEST, encoding="utf8"))
    frame_paths = [manifest["directions"]["west"]["static"]]
    frame_paths += manifest["directions"]["west"]["idle"]
    frame_paths += manifest["directions"]["west"]["walk"]
    for bridge in manifest["directions"]["west"]["stop_bridges"].values():
        frame_paths += [frame for frame in bridge if "file" in frame]
    unique_frames = {frame["file"]: frame["sha256"] for frame in frame_paths}
    if len(unique_frames) != 41:
        errors.append("manifest frame count != 41")
    installed_by_base = {os.path.basename(p): p for p in exist_game.values() if p.endswith(".png")}
    frame_bad = []
    for rel, want in unique_frames.items():
        out_p = os.path.join(ROOT, rel)
        base = os.path.basename(rel)
        if sha(out_p) != want:
            frame_bad.append("output " + base)
        if base not in installed_by_base or sha(installed_by_base[base]) != want:
            frame_bad.append("installed " + base)
    if frame_bad:
        errors.append("frame hash mismatches: " + ", ".join(frame_bad[:8]))

    runtime = json.load(open(os.path.join(GAME_EXIST, os.path.basename(manifest["package"]["sprite_set"])), encoding="utf8"))
    missing_refs = []
    for _action, dirs in runtime["actions"].items():
        for _direction, entries in dirs.items():
            for entry in entries:
                if not os.path.exists(os.path.join(GAME_EXIST, entry["file"])):
                    missing_refs.append(entry["file"])
    stop = json.load(open(os.path.join(GAME_EXIST, os.path.basename(manifest["package"]["stop_supplemental"])), encoding="utf8"))
    for bridge in stop["phase_bridges"]["west"].values():
        for entry in bridge:
            if "file" in entry and not os.path.exists(os.path.join(GAME_EXIST, entry["file"])):
                missing_refs.append(entry["file"])
    if missing_refs:
        errors.append("missing package references: " + ", ".join(missing_refs[:8]))

    static = {
        "game/assets/characters/heya-native-v01/west/rpg-2-star-ocean-the-second_heya_west-static_unapproved-v01_20261024-131500-22034c8f.png": "f8a167d8df2a554660c01b8cb88e461f878297c8d8da2456a566bdc0c2ed766e",
        "game/assets/characters/heya-native-v01/west/rpg-2-star-ocean-the-second_heya_west-edit_unapproved-v01_20261024-131500-4bc15dd4.pxo": "ee5bd72e1b1297c22909b1c952048acd092aeb146ee320dd7d1a8adb54fd6247",
        "game/assets/characters/heya-native-v01/west/rpg-2-star-ocean-the-second_heya_west-edit_unapproved-v01_20261024-131500-3346f283.ora": "fc3d332b0b263fba3d6f5be39f38c45b3ed872b76e706471e2671cb4bd4d424b",
        "game/assets/characters/heya-native-v01/west/rpg-2-star-ocean-the-second_heya_west-manifest_unapproved-v01_20261024-131500-164571cd.json": "75b0519c2b1282dc4441b38a90fa3bc64868a442f1779c436455928fd8897752",
        "game/assets/characters/heya-native-v01/west/rpg-2-star-ocean-the-second_heya_west-palette_unapproved-v01_20261024-131500-2b57e26b.json": "59491af00cb984ed840489de9e7bd427aea456152ef9f0b1423f0c3f26979d7c",
    }
    static_state = []
    for rel, want in static.items():
        got = sha(os.path.join(ROOT, rel))
        static_state.append({"path": rel, "sha256_expected": want, "sha256_now": got, "equal": got == want})
        if got != want:
            errors.append("static pin drift: " + rel)

    summary = {
        "stage_root": "outputs/heya-ww169/stage",
        "game_files": {"staged": len(stage_game), "installed": len(exist_game), "byte_equal": len(stage_game) - len(game_diff)},
        "source_output_files": {"staged": len(stage_out), "existing": len(exist_out),
                                "byte_equal": len(stage_out) - len(out_diff),
                                "preserved_old_failed_result": old_fail_rel,
                                "fixed_pass_result": fixed_pass_rel,
                                "stage_pass_equals_fixed_pass": sha(STAGE_PASS) == sha(FIXED_PASS)},
        "manifest_frames": len(unique_frames),
        "missing_package_references": missing_refs,
        "static_dependency": static_state,
        "errors": errors,
        "passed": not errors,
    }
    out = os.path.join(ROOT, "outputs/heya-ww169/reconcile-summary.json")
    with open(out, "w", encoding="utf8") as fh:
        fh.write(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
