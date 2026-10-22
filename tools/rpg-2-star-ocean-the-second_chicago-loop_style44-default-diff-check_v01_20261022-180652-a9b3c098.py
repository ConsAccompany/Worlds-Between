#!/usr/bin/env python3
"""Static LF source-integrity diff check for the authorized style42 Chicago default."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

BASE = "b92f3f4f98b0a71c53893ea689f51c8165275139"
SELECTOR = "game/scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v05_20261017-234337-84862412.gd"
POLICY = "game/scripts/sdef35/rpg-2-star-ocean-the-second_mvp-scene-defaults_policy_prepared-v01_20261021-231349-a83c4bae.gd"
MANIFEST = "outputs/style42/rpg-2-star-ocean-the-second_chicago-loop-style42_native-manifest_unapproved-v01_20261022-161615-69eb4eee.json"
SCENE = "game/scenes/style42/rpg-2-star-ocean-the-second_chicago-loop-style42_state-lake-scene_unapproved-v01_20261022-161615-69eb4eee.tscn"
TARGET, CHICAGO_OLD, CHICAGO_NEW = b"target = V05_SCENE", b"const CHICAGO_V05_DEFAULT := false", b"const CHICAGO_V05_DEFAULT := true"
OTHER_BITS = ("CITY_V06_DEFAULT", "RUINS_V13_DEFAULT", "RECORDS_ROOM2_DEFAULT")
EXPLICIT = (TARGET, b"target = V04Selector.V04_SCENE", b"target = V04Selector.V03R1Selector.V03R1_SCENE",
            b"target = V04Selector.V03R1Selector.V03Selector.V03_SCENE")

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def git_show(root, path):
    proc = subprocess.run(["git", "show", f"{BASE}:{path}"], cwd=root, timeout=10,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"git show failed for {path}: {proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout

def evaluate(selector, policy, old_selector, old_policy, scene):
    """Pure byte check. Returns (ok, errors); negative fixtures must return False."""
    errs = []
    if not scene or not scene.startswith("res://") or not scene.endswith(".tscn"):
        errs.append("manifest_scene_not_resource_tscn")
    if b"\r" in old_selector or b"\r" in old_policy:
        errs.append("baseline_not_lf")
    if b"\r" in selector or b"\r" in policy:
        errs.append("actual_not_lf")
    count, idx = old_selector.count(TARGET), old_selector.rfind(TARGET)
    if count != 2 or idx < 0:
        errs.append("baseline_selector_target_count")
    else:
        prefix = old_selector[:idx]
        for line in EXPLICIT:
            if prefix.count(line) != 1:
                errs.append("baseline_explicit_target_missing")
        expected_selector = prefix + b'target = "' + scene.encode("utf-8") + b'"' + old_selector[idx + len(TARGET):]
        if selector != expected_selector:
            errs.append("selector_not_exact_one_default_target_replacement")
        if selector[:idx] != prefix:
            errs.append("earlier_explicit_targets_changed")
    if old_policy.count(CHICAGO_OLD) != 1:
        errs.append("baseline_chicago_bit_marker")
    elif policy != old_policy.replace(CHICAGO_OLD, CHICAGO_NEW, 1):
        errs.append("policy_not_exact_chicago_false_to_true")
    if policy.count(CHICAGO_NEW) != 1:
        errs.append("chicago_bit_not_exactly_true")
    for key in OTHER_BITS:
        if policy.count(f"const {key} := false".encode("ascii")) != 1:
            errs.append(f"{key}_not_exactly_false")
    for marker in (b"if v05_enabled():", b"elif v05_override != 0 and SceneDefaults35.default_on(SceneDefaults35.CHICAGO):"):
        if selector.count(marker) != 1:
            errs.append("selector_marker_missing_or_duplicated")
    return not errs, errs

def fixture_results(old_selector, old_policy, res_scene):
    idx=old_selector.rfind(TARGET)
    valid_selector=old_selector[:idx]+b'target = "'+res_scene.encode('utf8')+b'"'+old_selector[idx+len(TARGET):]
    valid_policy=old_policy.replace(CHICAGO_OLD,CHICAGO_NEW,1)
    positive=evaluate(valid_selector,valid_policy,old_selector,old_policy,res_scene)
    if not positive[0]:raise AssertionError("positive fixture fails before mutation")
    fixtures = {
        "other_bit_true": evaluate(valid_selector,valid_policy.replace(b"CITY_V06_DEFAULT := false",b"CITY_V06_DEFAULT := true",1),old_selector,old_policy,res_scene),
        "explicit_flag_target_changed": evaluate(valid_selector.replace(TARGET,b"target = V04Selector.V04_SCENE",1),valid_policy,old_selector,old_policy,res_scene),
        "unexpected_extra_code": evaluate(valid_selector+b"\nvar forbidden_extra = true\n",valid_policy,old_selector,old_policy,res_scene),
    }
    return {name:{"ok":ok,"errors":errs,"valid_control_passed":positive[0]} for name,(ok,errs) in fixtures.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    root, out_dir = Path(args.root).resolve(), Path(args.out).resolve()
    report = {"tool": "style44-default-diff-check", "scope": "source-integrity only", "base_commit": BASE,
              "status": "ERROR", "checks": {}, "baseline_sha256": {}, "actual_sha256": {}, "errors": [],
              "limitations": ["No runtime, rendering, Godot, packaging, or gameplay claim; unrelated dirty sources/imports outside the two targets are ignored."]}
    try:
        old_selector, old_policy = git_show(root, SELECTOR), git_show(root, POLICY)
        manifest_scene = json.loads((root / MANIFEST).read_text(encoding="utf-8"))["scene"]["tscn"]
        if manifest_scene != SCENE:
            raise RuntimeError(f"manifest scene mismatch: {manifest_scene}")
        res_scene = "res://" + manifest_scene.removeprefix("game/")
        actual_selector, actual_policy = (root / SELECTOR).read_bytes(), (root / POLICY).read_bytes()
        ok, errs = evaluate(actual_selector, actual_policy, old_selector, old_policy, res_scene)
        fixtures = fixture_results(old_selector, old_policy, res_scene)
        fixtures_ok = all(not item["ok"] for item in fixtures.values())
        report.update({"selector": SELECTOR, "policy": POLICY, "manifest": MANIFEST, "scene": res_scene,
                       "baseline_sha256": {"selector": sha256(old_selector), "policy": sha256(old_policy)},
                       "actual_sha256": {"selector": sha256(actual_selector), "policy": sha256(actual_policy)},
                       "checks": {"two_file_exact": ok, "negative_fixtures_return_false": fixtures_ok, "negative_fixtures": fixtures},
                       "errors": errs})
        if ok and fixtures_ok:
            report["status"] = "PASS"
        elif actual_selector == old_selector or actual_policy == old_policy:
            report["status"] = "PENDING"
        else:
            report["status"] = "FAIL"
    except Exception as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "rpg-2-star-ocean-the-second_chicago-loop_style44-default-diff-check_v01_20261022-180652-a9b3c098.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "errors": report["errors"], "report": str(report_path)}))
    return {"PASS": 0, "FAIL": 1, "PENDING": 2}.get(report["status"], 1)


if __name__ == "__main__":
    sys.exit(main())
