#!/usr/bin/env python3
"""Targeted tests for the reusable exploration PNG-source packager.

All source images are synthetic 80x112 RGBA test fixtures built in this test process; they are
not art and nothing is approved or made default. The suite exercises a full four-direction
idle+walk package plus missing/invalid schema, counts, durations, paths, filenames, alpha,
size, pivot, floor, body and atomic no-overwrite behavior. If --godot is supplied, one valid
synthetic package is imported into a temporary minimal Godot project and probed with the
existing game/scripts/exploration_sprite_set_pilot.gd loader, followed by an invalid-package
fallback check.

Usage:
  python -I <this> [--work-root <dir>] [--report <json>] [--godot <console exe>] [--keep]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "rpg-2-star-ocean-the-second_exploration-source-package_packager_v01_20261020-171611-e359539c.py"
CHECKED_RUNNER = ROOT / "tools" / "rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py"
PILOT = ROOT / "game" / "scripts" / "exploration_sprite_set_pilot.gd"
DRIVER = ROOT / "game" / "scripts" / "fexp" / "rpg-2-star-ocean-the-second_female-complete-explore_driver_pilot-v01_20261019-184900-f2c0a7e1.gd"
GUARD = ROOT / "game" / "scripts" / "fexp" / "rpg-2-star-ocean-the-second_female-complete-explore_input-guard_v01_20261019-190507-a7d3e9b1.gd"
GODOT_DEFAULT = ROOT.parents[1] / "tooling" / "godot-4-7-2" / "Godot_v4.7.2-stable_win64_console.exe"
ACTOR = "protagonist-female"
DIRECTIONS = ("south", "west", "north", "east")
ACTIONS = ("idle", "walk")
STAMP = "20261020-171611"
NAME_RE = re.compile(
    r"^[a-z0-9][a-z0-9-]*_[a-z0-9][a-z0-9-]*_[a-z0-9][a-z0-9-]*_[a-z0-9][a-z0-9-]*_\d{8}-\d{6}-[a-z0-9]{4,32}\.png$"
)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_text_lf(path):
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def unique(prefix="exp"):
    return f"{prefix}-{secrets.token_hex(4)}"


def png_name(action, direction, index):
    return (
        f"rpg-2-star-ocean-the-second_hero-female_"
        f"{action}-{direction}-pose_v{index + 1:02d}_{STAMP}-{secrets.token_hex(4)}.png"
    )


def draw(path, *, mode="RGBA", size=(80, 112), top=8, bottom=103, x0=24, x1=56,
         color=None, partial=False, border=False, floor=False, empty=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if mode == "RGBA":
        image = Image.new("RGBA", size, (0, 0, 0, 0))
    elif mode == "RGB":
        image = Image.new("RGB", size, (0, 0, 0))
    else:
        raise ValueError(mode)
    pixels = image.load()
    color = color or (54, 96, 150)
    if not empty:
        for y in range(max(0, top), min(size[1] - 1, bottom) + 1):
            for x in range(max(1, x0), min(size[0] - 1, x1)):
                pixels[x, y] = color if mode == "RGB" else (*color, 255)
    if partial:
        pixels[40, 60] = (*color, 128) if mode == "RGBA" else color
    if border:
        pixels[0, 60] = (*color, 255) if mode == "RGBA" else color
    if floor:
        pixels[40, 104] = (*color, 255) if mode == "RGBA" else color
    image.save(path, format="PNG")


def write_manifest(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")


def build_source(root, *, counts=None, nested=False, source_files=False):
    root = Path(root)
    root.mkdir(parents=True)
    counts = counts or {"idle": 2, "walk": 2}
    payload = {}
    for action in ACTIONS:
        payload[action] = {}
        for direction in DIRECTIONS:
            payload[action][direction] = []
            for index in range(counts[action]):
                name = png_name(action, direction, index)
                relative = f"art/{name}" if nested else name
                target = root / relative
                top = 8 if action == "idle" else 40
                draw(target, top=top, bottom=103, color=(30 + index * 11, 80 + len(direction) * 3, 120))
                payload[action][direction].append({"file": relative, "duration_ms": 200 + index * 10})
    data = {
        "schema": "worlds-between.exploration-source.v1",
        "actor_id": ACTOR,
        "density": 2,
        "frame_size": [80, 112],
        "pivot": [40, 104],
        "actions": payload,
    }
    if source_files:
        native = root / "native-source.pxo"
        native.write_bytes(b"SYNTHETIC-NATIVE-SOURCE-NOT-ART\n")
        data["source_files"] = [native.name]
    manifest = root / "source-manifest_test-only.json"
    write_manifest(manifest, data)
    return {"root": root, "manifest": manifest, "data": data}


def clone_source(source, destination):
    destination = Path(destination)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source["root"], destination)
    return {"root": destination, "manifest": destination / source["manifest"].name, "data": json.loads(
        (destination / source["manifest"].name).read_text(encoding="utf-8"))}


def mutate(source, callback):
    data = json.loads(source["manifest"].read_text(encoding="utf-8"))
    callback(data, source["root"])
    write_manifest(source["manifest"], data)
    source["data"] = data
    return source


def redraw(source, action, direction, index, **kwargs):
    entry = json.loads(source["manifest"].read_text(encoding="utf-8"))["actions"][action][direction][index]
    draw(source["root"] / entry["file"], **kwargs)


def run_tool(source, out, repo_root=None, timeout=90):
    command = [sys.executable, "-I", str(TOOL), "--source", str(source), "--out", str(out)]
    if repo_root is not None:
        command.extend(["--repo-root", str(repo_root)])
    started = time.monotonic()
    proc = subprocess.run(
        command,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    payload = None
    try:
        payload = json.loads(proc.stdout)
    except Exception:
        pass
    return proc, payload, round((time.monotonic() - started) * 1000, 1)


def out_empty(path):
    if not Path(path).exists():
        return True
    try:
        return not any(True for _ in Path(path).iterdir())
    except OSError:
        return False


def case(name, source, out, *, expect="ok", contains=None, repo_root=None, out_prepared=False, allow_nonempty=False):
    proc, payload, elapsed = run_tool(source["manifest"], out, repo_root=repo_root)
    errors = payload.get("errors", []) if isinstance(payload, dict) else [proc.stderr.strip() or proc.stdout.strip()]
    error_text = " | ".join(str(item) for item in errors)
    record = {
        "name": name,
        "expect": expect,
        "exit_code": proc.returncode,
        "elapsed_ms": elapsed,
        "errors": errors,
        "stderr_tail": proc.stderr[-2000:],
    }
    if expect == "ok":
        ok = proc.returncode == 0 and isinstance(payload, dict) and payload.get("ok") is True
        if ok:
            summary = verify_package(source, Path(out), payload)
            record.update(summary)
            ok = summary["verified"]
        record["passed"] = bool(ok)
    else:
        ok = proc.returncode != 0 and isinstance(payload, dict) and payload.get("ok") is False
        if not allow_nonempty:
            ok = ok and out_empty(out)
        if contains and contains.lower() not in error_text.lower():
            record["missing_expected_error"] = contains
            ok = False
        record["passed"] = bool(ok)
    if not record["passed"]:
        record["stdout_tail"] = proc.stdout[-4000:]
    return record


def verify_package(source, out, payload):
    errors = []
    try:
        set_path = out / payload["package"]["set"]["file"]
        registry_path = out / payload["package"]["registry"]["file"]
        provenance_path = out / payload["package"]["provenance"]["file"]
        set_data = json.loads(set_path.read_text(encoding="utf-8"))
        registry_data = json.loads(registry_path.read_text(encoding="utf-8"))
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"verified": False, "verify_errors": [f"manifest read failed: {exc}"]}
    if set_data.get("schema") != "worlds-between.exploration-sprite-set.v1":
        errors.append("set schema")
    if set_data.get("actor_id") != ACTOR:
        errors.append("set actor_id")
    if set_data.get("density") != 2 or set_data.get("frame_size") != [80, 112] or set_data.get("pivot") != [40, 104]:
        errors.append("set density/frame_size/pivot")
    if registry_data.get("schema") != "worlds-between.exploration-sprite-set-registry.v1":
        errors.append("registry schema")
    if registry_data.get("actors", {}).get(ACTOR) != set_path.name:
        errors.append("registry target")
    if provenance.get("schema") != "worlds-between.exploration-source-package-provenance.v1":
        errors.append("provenance schema")
    if provenance.get("copy", {}).get("network_used") is not False:
        errors.append("provenance network flag")
    if provenance.get("copy", {}).get("image_editing") != "none":
        errors.append("provenance image editing")
    if provenance.get("copy", {}).get("import_metadata_copied") is not False:
        errors.append("provenance import metadata flag")
    source_files = source["data"].get("source_files") or []
    provenance_sources = provenance.get("source_files") or []
    if len(provenance_sources) != len(source_files):
        errors.append("provenance source_files count")
    else:
        for relative, entry in zip(source_files, provenance_sources):
            path = source["root"] / relative
            if not path.is_file() or entry.get("sha256") != sha256_bytes(path.read_bytes()):
                errors.append(f"provenance source_files hash {relative}")
    frame_total = 0
    byte_equal = 0
    for action in ACTIONS:
        for direction in DIRECTIONS:
            source_frames = source["data"]["actions"][action][direction]
            runtime_frames = set_data.get("actions", {}).get(action, {}).get(direction)
            if not isinstance(runtime_frames, list) or len(runtime_frames) != len(source_frames):
                errors.append(f"count {action}/{direction}")
                continue
            for source_frame, runtime_frame in zip(source_frames, runtime_frames):
                frame_total += 1
                source_bytes = (source["root"] / source_frame["file"]).read_bytes()
                output_file = out / runtime_frame["file"]
                if not output_file.is_file():
                    errors.append(f"missing output {runtime_frame['file']}")
                    continue
                output_bytes = output_file.read_bytes()
                if output_bytes == source_bytes:
                    byte_equal += 1
                else:
                    errors.append(f"byte mismatch {runtime_frame['file']}")
                if runtime_frame.get("duration_ms") != source_frame.get("duration_ms"):
                    errors.append(f"duration mismatch {action}/{direction}")
                if not NAME_RE.match(output_file.name):
                    errors.append(f"output name rule {output_file.name}")
    if frame_total != payload.get("package", {}).get("png_count"):
        errors.append("payload png_count")
    if byte_equal != frame_total:
        errors.append("byte-equal count")
    files = sorted(str(path.relative_to(out)).replace("\\", "/") for path in out.rglob("*") if path.is_file())
    if any(name.endswith(".import") for name in files):
        errors.append("import metadata was copied into package")
    if len(files) != frame_total + 3:
        errors.append(f"unexpected output file count {len(files)}")
    if provenance.get("source_manifest", {}).get("sha256") != sha256_bytes(source["manifest"].read_bytes()):
        errors.append("source manifest hash")
    return {
        "verified": not errors,
        "verify_errors": errors,
        "package_files": len(files),
        "frame_total": frame_total,
        "byte_equal": byte_equal,
        "set_file": set_path.name,
        "set_sha256": sha256_bytes(set_path.read_bytes()),
        "registry_file": registry_path.name,
        "registry_sha256": sha256_bytes(registry_path.read_bytes()),
        "provenance_file": provenance_path.name,
        "provenance_sha256": sha256_bytes(provenance_path.read_bytes()),
    }


def try_junction(link, target):
    link = Path(link)
    target = Path(target)
    try:
        proc = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return proc.returncode == 0 and link.exists()
    except Exception:
        return False


def create_godot_project(package_summary, package_dir, work):
    project = work / "godot-probe"
    project.mkdir(parents=True)
    (project / "project.godot").write_text(
        '; synthetic packager loader probe project\nconfig_version=5\n\n[application]\nconfig/name="exp-pack08-probe"\n',
        encoding="utf-8",
        newline="\n",
    )
    (project / "scripts" / "fexp").mkdir(parents=True)
    shutil.copyfile(PILOT, project / "scripts" / "exploration_sprite_set_pilot.gd")
    shutil.copyfile(DRIVER, project / "scripts" / "fexp" / DRIVER.name)
    shutil.copyfile(GUARD, project / "scripts" / "fexp" / GUARD.name)
    shutil.copytree(package_dir, project / "pkg")
    bad = project / "bad"
    shutil.copytree(package_dir, bad)
    set_name = package_summary["set_file"]
    registry_name = package_summary["registry_file"]
    bad_set = json.loads((bad / set_name).read_text(encoding="utf-8"))
    bad_set["actions"]["idle"]["south"][0]["duration_ms"] = 39
    write_manifest(bad / set_name, bad_set)
    probe = f'''extends SceneTree

const Pilot := preload("res://scripts/exploration_sprite_set_pilot.gd")
const ACTOR := "protagonist-female"
const DIRS := ["south", "west", "north", "east"]

func _fail(message: String) -> void:
	print("EXP_PACK_PROBE_FAIL ", message)
	quit(1)

func _init() -> void:
	var registry_path := "res://pkg/{registry_name}"
	var listed := Pilot.load_registry(registry_path)
	if not listed["ok"]:
		_fail("registry: " + "; ".join(listed["errors"]))
		return
	var set_path: String = listed["actors"].get(ACTOR, "")
	if set_path == "":
		_fail("protagonist-female missing from registry")
		return
	var loaded := Pilot.load_set(set_path, ACTOR)
	if not loaded["ok"]:
		_fail("set: " + "; ".join(loaded["errors"]))
		return
	var clips: Dictionary = loaded["set"]["clips"]
	var frame_count := 0
	for action in ["idle", "walk"]:
		for direction in DIRS:
			var clip: Dictionary = clips[action][direction]
			var minimum := 1 if action == "idle" else 2
			if clip["textures"].size() < minimum:
				_fail("count " + action + "/" + direction)
				return
			for texture in clip["textures"]:
				if texture == null or Vector2i(texture.get_size()) != Vector2i(80, 112):
					_fail("texture size")
					return
				frame_count += 1
	Pilot.clear_cache()
	Pilot.enabled_override = 1
	Pilot.registry_override = registry_path
	var host := Sprite2D.new()
	var driver = Pilot.attach(host, ACTOR, "south")
	if driver == null:
		_fail("attach returned null for valid package")
		return
	if host.texture == null or host.scale != Vector2(0.5, 0.5):
		_fail("host not configured")
		return
	var before_texture := host.texture
	var before_scale := host.scale
	var before_offset := host.offset
	Pilot.clear_cache()
	Pilot.registry_override = "res://bad/{registry_name}"
	var bad_driver = Pilot.attach(host, ACTOR, "south")
	if bad_driver != null:
		_fail("invalid package was accepted")
		return
	if host.texture != before_texture or host.scale != before_scale or host.offset != before_offset:
		_fail("invalid package mutated the host")
		return
	print("EXP_PACK_PROBE_OK frames=", frame_count)
	quit(0)
'''
    (project / "probe.gd").write_text(probe, encoding="utf-8", newline="\n")
    return project


def run_godot_probe(godot, package_summary, package_dir, work):
    if not godot or not Path(godot).is_file():
        return {"ran": False, "skipped": True, "reason": f"Godot not found: {godot}"}
    if not CHECKED_RUNNER.is_file():
        return {"ran": False, "skipped": True, "reason": f"checked runner not found: {CHECKED_RUNNER}"}
    project = create_godot_project(package_summary, package_dir, work)
    profiles = work / "profiles"
    (profiles / "a").mkdir(parents=True)
    (profiles / "l").mkdir(parents=True)
    env = dict(os.environ)
    env["APPDATA"] = str(profiles / "a")
    env["LOCALAPPDATA"] = str(profiles / "l")
    log_import = work / "godot-import_test-only.log"
    log_probe = work / "godot-probe_test-only.log"
    commands = [
        ("import", [godot, "--headless", "--path", str(project), "--import"], None, log_import),
        ("loader_probe", [godot, "--headless", "--path", str(project), "-s", "res://probe.gd"], "EXP_PACK_PROBE_OK", log_probe),
    ]
    results = []
    for name, godot_command, expect, log in commands:
        command = [sys.executable, "-I", str(CHECKED_RUNNER), "--timeout", "180", "--log", str(log)]
        if expect:
            command.extend(["--expect", expect])
        command.extend(["--"] + godot_command)
        proc = subprocess.run(
            command,
            cwd=str(work),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=240,
        )
        log_text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
        results.append(
            {
                "stage": name,
                "exit_code": proc.returncode,
                "passed": proc.returncode == 0 and "CHECKED_RUN PASS" in proc.stdout,
                "expect": expect,
                "log": str(log),
                "log_tail": log_text[-5000:],
            }
        )
    passed = all(item["passed"] for item in results)
    probe_text = results[1]["log_tail"] if len(results) > 1 else ""
    return {
        "ran": True,
        "skipped": False,
        "passed": passed,
        "process_gate": "checked runner rejects any engine ERROR/SCRIPT ERROR diagnostic even with exit 0",
        "project": str(project),
        "stages": results,
        "marker": "EXP_PACK_PROBE_OK" in probe_text,
        "invalid_fallback_observed": "rejected for protagonist-female" in probe_text,
        "loader_observed": "EXP_PACK_PROBE_OK" in probe_text and "rejected for protagonist-female" in probe_text,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", default=None, help="workspace-local short temporary root")
    parser.add_argument("--report", default=None, help="write the test report JSON here")
    parser.add_argument("--godot", default=str(GODOT_DEFAULT) if GODOT_DEFAULT.is_file() else "")
    parser.add_argument("--skip-godot", action="store_true")
    parser.add_argument("--keep", action="store_true", help="keep the temporary work root")
    args = parser.parse_args()

    started = time.monotonic()
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if args.work_root:
        work = Path(args.work_root)
        if work.exists():
            shutil.rmtree(work)
        work.mkdir(parents=True)
    else:
        base = ROOT / "tmp"
        base.mkdir(exist_ok=True)
        work = base / ("e8-" + secrets.token_hex(4))
        work.mkdir()
    records = []
    skipped = []
    valid_package = None
    valid_source = None
    try:
        base = build_source(work / "valid", source_files=True)
        valid_source = base
        out = work / "valid-package"
        record = case("valid_full_four_direction_with_source_files", base, out, expect="ok")
        records.append(record)
        if record.get("passed"):
            valid_package = {
                "out": out,
                "payload": json.loads(json.dumps({"package": {
                    "set": {"file": record["set_file"]},
                    "registry": {"file": record["registry_file"]},
                    "provenance": {"file": record["provenance_file"]},
                    "png_count": record["frame_total"],
                }})),
                "summary": record,
            }

        valid_nested = build_source(work / "valid-nested", nested=True)
        records.append(case("valid_nested_source_paths", valid_nested, work / "nested-package", expect="ok"))

        prepared = work / "prepared-empty-out"
        prepared.mkdir()
        records.append(case("valid_existing_empty_out", base, prepared, expect="ok", out_prepared=True))

        # No-overwrite: a second publication to the same non-empty directory must fail.
        before = {p.name: sha256_bytes(p.read_bytes()) for p in out.rglob("*") if p.is_file()}
        records.append(case("no_overwrite_existing_nonempty_out", base, out, expect="refusal", contains="not empty", allow_nonempty=True))
        after = {p.name: sha256_bytes(p.read_bytes()) for p in out.rglob("*") if p.is_file()}
        records[-1]["package_unchanged"] = before == after
        records[-1]["passed"] = records[-1]["passed"] and before == after

        # Each invalid case gets a fresh clone of the synthetic full input.
        cases = []

        def add(name, mutator, contains, **kwargs):
            cases.append((name, mutator, contains, kwargs))

        add("missing_schema", lambda s: s["data"].pop("schema"), "schema")
        add("missing_actor_id", lambda s: s["data"].pop("actor_id"), "actor_id")
        add("wrong_density", lambda s: s["data"].__setitem__("density", 3), "density")
        add("wrong_frame_size", lambda s: s["data"].__setitem__("frame_size", [80, 111]), "frame_size")
        add("wrong_pivot", lambda s: s["data"].__setitem__("pivot", [41, 104]), "pivot")
        add("missing_actions", lambda s: s["data"].pop("actions"), "actions")
        add("missing_walk_direction", lambda s: s["data"]["actions"]["walk"].pop("north"), "missing direction")
        add("extra_walk_direction", lambda s: s["data"]["actions"]["walk"].__setitem__("up", []), "non-contract direction")
        add("idle_zero_poses", lambda s: s["data"]["actions"]["idle"].__setitem__("south", []), "needs 1..16")
        add("walk_one_pose", lambda s: s["data"]["actions"]["walk"].__setitem__("south", s["data"]["actions"]["walk"]["south"][:1]), "needs 2..16")
        add("duration_low", lambda s: s["data"]["actions"]["idle"]["south"][0].__setitem__("duration_ms", 39), "duration_ms")
        add("duration_high", lambda s: s["data"]["actions"]["idle"]["south"][0].__setitem__("duration_ms", 2001), "duration_ms")
        add("duration_float", lambda s: s["data"]["actions"]["idle"]["south"][0].__setitem__("duration_ms", 200.0), "duration_ms")
        add("duration_bool", lambda s: s["data"]["actions"]["idle"]["south"][0].__setitem__("duration_ms", True), "duration_ms")

        def missing_file(s):
            s["data"]["actions"]["idle"]["south"][0]["file"] = (
                f"rpg-2-star-ocean-the-second_hero-female_idle-south-pose_v01_{STAMP}-{secrets.token_hex(4)}.png"
            )
        add("missing_frame_file", missing_file, "does not exist")

        def absolute_path(s):
            s["data"]["actions"]["idle"]["south"][0]["file"] = str(s["root"] / s["data"]["actions"]["idle"]["south"][0]["file"]).replace("\\", "/")
        add("absolute_path", absolute_path, "absolute")

        def traversal(s):
            outside = work / "outside-frame.png"
            shutil.copyfile(s["root"] / s["data"]["actions"]["idle"]["south"][0]["file"], outside)
            s["data"]["actions"]["idle"]["south"][0]["file"] = "../outside-frame.png"
        add("traversal_path", traversal, "traversal")

        def bad_filename(s):
            old = s["root"] / s["data"]["actions"]["idle"]["south"][0]["file"]
            new_name = "BAD-UPPER_hero-female_idle-south-pose_v01_" + STAMP + "-" + secrets.token_hex(4) + ".png"
            old.rename(s["root"] / new_name)
            s["data"]["actions"]["idle"]["south"][0]["file"] = new_name
        add("bad_filename_rule", bad_filename, "lowercase")

        def duplicate(s):
            first = s["data"]["actions"]["walk"]["south"][0]["file"]
            s["data"]["actions"]["walk"]["south"][1]["file"] = first
        add("duplicate_filename", duplicate, "reuses")

        def wrong_size(s):
            entry = s["data"]["actions"]["idle"]["east"][0]["file"]
            draw(s["root"] / entry, size=(81, 112), top=8, bottom=103)
        add("wrong_png_size", wrong_size, "not 80x112")

        def partial_alpha(s):
            entry = s["data"]["actions"]["idle"]["west"][0]["file"]
            draw(s["root"] / entry, top=8, bottom=103, partial=True)
        add("partial_alpha", partial_alpha, "partial-alpha")

        def alpha_border(s):
            entry = s["data"]["actions"]["walk"]["east"][0]["file"]
            draw(s["root"] / entry, top=40, bottom=103, border=True)
        add("opaque_border", alpha_border, "border")

        def floor(s):
            entry = s["data"]["actions"]["walk"]["north"][0]["file"]
            draw(s["root"] / entry, top=40, bottom=103, floor=True)
        add("opaque_below_floor", floor, "y >= 104")

        def idle_short(s):
            entry = s["data"]["actions"]["idle"]["north"][0]["file"]
            draw(s["root"] / entry, top=9, bottom=103)
        add("idle_body_short", idle_short, "idle body")

        def idle_soles(s):
            entry = s["data"]["actions"]["idle"]["east"][1]["file"]
            draw(s["root"] / entry, top=7, bottom=102)
        add("idle_soles_not_103", idle_soles, "soles")

        def walk_tall(s):
            entry = s["data"]["actions"]["walk"]["west"][0]["file"]
            draw(s["root"] / entry, top=6, bottom=103)
        add("walk_body_too_tall", walk_tall, "taller")

        def rgb(s):
            entry = s["data"]["actions"]["idle"]["south"][1]["file"]
            draw(s["root"] / entry, mode="RGB", top=8, bottom=103)
        add("non_rgba_png", rgb, "color type")

        def source_files_missing(s):
            s["data"]["source_files"] = ["missing-native.pxo"]
        add("missing_source_file_provenance", source_files_missing, "does not exist")

        def junction_escape(s):
            outside = work / "junction-outside"
            outside.mkdir(exist_ok=True)
            name = Path(s["data"]["actions"]["idle"]["south"][0]["file"]).name
            shutil.copyfile(s["root"] / s["data"]["actions"]["idle"]["south"][0]["file"], outside / name)
            link = s["root"] / "linked-outside"
            if not try_junction(link, outside):
                raise RuntimeError("junction unsupported")
            s["data"]["actions"]["idle"]["south"][0]["file"] = f"linked-outside/{name}"
        add("junction_outside_manifest_folder", junction_escape, "junction")

        for name, mutator, contains, _kwargs in cases:
            clone = clone_source(base, work / ("case-" + name))
            view = {"data": clone["data"], "root": clone["root"], "manifest": clone["manifest"]}
            try:
                mutator(view)
            except RuntimeError as exc:
                skipped.append({"name": name, "reason": str(exc)})
                continue
            write_manifest(clone["manifest"], clone["data"])
            records.append(case(name, clone, work / ("out-" + name), expect="refusal", contains=contains))

        # Invalid input must not create a package or disturb a pre-created empty destination.
        clone = clone_source(base, work / "case-atomic")
        draw(clone["root"] / clone["data"]["actions"]["idle"]["south"][0]["file"], top=8, bottom=103, partial=True)
        empty_out = work / "atomic-empty-out"
        empty_out.mkdir()
        atomic = case("invalid_atomic_preserves_empty_out", clone, empty_out, expect="refusal", contains="partial-alpha", out_prepared=True)
        atomic["out_still_empty"] = out_empty(empty_out)
        atomic["passed"] = atomic["passed"] and atomic["out_still_empty"]
        records.append(atomic)

        # --repo-root containment: valid inside, refused outside.
        repo = work / "repo-root"
        repo.mkdir()
        inside = clone_source(base, repo / "src")
        records.append(case("repo_root_contains_valid_source_and_out", inside, repo / "pkg", expect="ok", repo_root=repo))
        outside_repo = work / "outside-repo"
        outside_repo.mkdir()
        different_repo = work / "different-repo"
        different_repo.mkdir()
        records.append(case("repo_root_refuses_source_outside", inside, outside_repo / "pkg", expect="refusal", contains="outside", repo_root=different_repo))

        # Duplicate JSON keys are not silently accepted.
        duplicate_root = work / "case-duplicate-key"
        clone = clone_source(base, duplicate_root)
        text = clone["manifest"].read_text(encoding="utf-8")
        text = text.replace('"actions": {', '"actions": {', 1)
        text = text.replace('"idle": {', '"idle": {', 1)
        # Add a second "idle" key before the closing of actions by duplicating the actual object text is
        # brittle; construct it from the parsed data instead.
        data = json.loads(text)
        raw = json.dumps(data, indent=2)
        raw = raw.replace('"actions": {', '"actions": {\n    "idle": {"south": [], "west": [], "north": [], "east": []},', 1)
        clone["manifest"].write_text(raw, encoding="utf-8", newline="\n")
        records.append(case("duplicate_json_key", clone, work / "out-duplicate-key", expect="refusal", contains="duplicate"))

        if not args.skip_godot:
            if valid_package is not None:
                probe = run_godot_probe(args.godot, valid_package["summary"], valid_package["out"], work)
            else:
                probe = {"ran": False, "skipped": True, "reason": "valid package was not produced"}
        else:
            probe = {"ran": False, "skipped": True, "reason": "--skip-godot"}
    finally:
        if args.keep:
            keep_note = f"kept work root: {work}"
        else:
            keep_note = ""
            try:
                shutil.rmtree(work)
            except OSError:
                keep_note = f"work root cleanup failed: {work}"

    failed = [record for record in records if not record.get("passed")]
    report = {
        "schema": "worlds-between.exploration-source-package.tests-report.v1",
        "status": "synthetic test-only; not art; no approval; packager capability checks",
        "started_utc": started_utc,
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_seconds": round(time.monotonic() - started, 2),
        "python": sys.version,
        "pillow": Image.__version__,
        "paths": {
            "tool": str(TOOL),
            "tests": str(Path(__file__).resolve()),
            "checked_runner": str(CHECKED_RUNNER),
            "godot": args.godot,
        },
        "hashes": {
            "tool": {"algorithm": "sha256-text-lf-v1", "sha256": sha256_text_lf(TOOL)},
            "tests": {"algorithm": "sha256-text-lf-v1", "sha256": sha256_text_lf(__file__)},
        },
        "summary": {
            "total": len(records),
            "passed": len(records) - len(failed),
            "failed": len(failed),
            "skipped": len(skipped),
        },
        "skipped": skipped,
        "cases": records,
        "godot_loader_probe": probe,
        "keep_note": keep_note,
    }
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        report["report_path"] = str(report_path)
    print(json.dumps({key: report[key] for key in ("summary", "godot_loader_probe", "report_path") if key in report}, indent=2, ensure_ascii=False))
    for record in records:
        print(("PASS " if record.get("passed") else "FAIL ") + record["name"] + (" SKIP" if record["name"] in {s["name"] for s in skipped} else ""))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
