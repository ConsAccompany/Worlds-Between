#!/usr/bin/env python3
"""Independent identity/runtime contract check for an exploration source package.

The input is the existing exploration source-bank manifest schema (the same
``directions`` bank consumed by the tracked native-bank checker).  This tool
does not recompose PXO/ORA pixels, does not run Godot, and does not approve art.

It checks, for the actor passed with ``--actor``:

* source actor, exact four directions, idle/walk durations, pivot and density;
* source frame hashes, unique/separate asset names and stop-bridge shape;
* the retained SOUTH original source PNG (``exact_source``) and source-author
  provenance (``tool``, ``reused_helpers``, ``source_inputs``);
* the package runtime set, registry and stop supplemental: schemas, exact
  single-actor registry, reference resolution and hashes against the source.

It then builds two isolated, preserved fixtures under ``--out-dir``:
wrong registry actor, and a changed runtime copied PNG while the original
source PNG stays unchanged.  Both must be refused.  Original files are only
read; the guard records their hashes before and after.

Usage (from the repository root):
  python -X utf8 -I <this> --manifest outputs/jexplore31/<source>.json \
      --actor ji-cheng --out-dir outputs/jexplore31-check
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import platform
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

PROJECT_SLUG = "rpg-2-star-ocean-the-second"
SUBJECT = "exploration-source"
PURPOSE = "identity-runtime-contract-check"
VARIANT = "test-only-v01"
DIRECTIONS = ("south", "west", "north", "east")
ACTIONS = ("idle", "walk")
SET_SCHEMA = "worlds-between.exploration-sprite-set.v1"
REGISTRY_SCHEMA = "worlds-between.exploration-sprite-set-registry.v1"
STOP_SCHEMA = "worlds-between.exploration-stop-transition.supplemental.v1"
PIVOT = [40, 104]
DENSITY = 2
FRAME_SIZE = [80, 112]
LOGICAL_HEIGHT = 48
MIN_DURATION_MS = 40
MAX_DURATION_MS = 2000
MIN_FRAMES = {"idle": 1, "walk": 2}
MAX_FRAMES = 16
MARKER = ".jexplore31-identity-runtime-fixture"
ROOT = Path(__file__).resolve().parent.parent
NATIVE_CHECKER = ROOT / "tools" / (
    "rpg-2-star-ocean-the-second_exploration-source_native-bank-check_"
    "test-only-v01_20261021-212850-493fd162.py"
)
ASSET_RE = re.compile(
    r"^rpg-2-star-ocean-the-second_[a-z0-9][a-z0-9-]*_[a-z0-9][a-z0-9-]*_"
    r"[a-z0-9][a-z0-9-]*_\d{8}-\d{6}-[a-z0-9]{4,32}\.png$"
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")


# ---------------------------------------------------------------------------
# Windows extended paths and explicit UTF-8 file helpers
# ---------------------------------------------------------------------------


def win_long(path):
    p = Path(path)
    if os.name != "nt":
        return p
    text = str(p)
    if text.startswith("\\\\?\\"):
        return p
    absolute = os.path.abspath(text)
    if absolute.startswith("\\\\"):
        return Path("\\\\?\\UNC\\" + absolute[2:])
    return Path("\\\\?\\" + absolute)


def ensure_dir(path):
    os.makedirs(str(win_long(path)), exist_ok=True)


def read_bytes(path):
    with open(str(win_long(path)), "rb") as handle:
        return handle.read()


def write_bytes(path, data):
    ensure_dir(Path(path).parent)
    with open(str(win_long(path)), "wb") as handle:
        handle.write(data)


def read_text(path):
    return read_bytes(path).decode("utf-8")


def write_text(path, text):
    write_bytes(path, text.encode("utf-8"))


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    with open(str(win_long(path)), "rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def text_lf_sha256(data):
    """sha256-text-lf-v1: CRLF->LF only; NUL/invalid UTF-8 refused."""
    if b"\x00" in data:
        raise ValueError("NUL byte in text file")
    data.decode("utf-8")
    return sha256_bytes(data.replace(b"\r\n", b"\n"))


def path_is_file(path):
    try:
        return os.path.isfile(str(win_long(path)))
    except OSError:
        return False


def path_exists(path):
    try:
        return os.path.exists(str(win_long(path)))
    except OSError:
        return False


def display_path(path, repo_root):
    try:
        return Path(path).resolve().relative_to(Path(repo_root).resolve()).as_posix()
    except (OSError, ValueError):
        return str(path)


def is_within(child, parent):
    child_abs = os.path.normcase(os.path.abspath(str(child)))
    parent_abs = os.path.normcase(os.path.abspath(str(parent)))
    return child_abs == parent_abs or child_abs.startswith(parent_abs + os.sep)


def resolve_manifest_arg(value):
    p = Path(value)
    if p.is_absolute():
        return p
    cwd_candidate = Path.cwd() / p
    if path_is_file(cwd_candidate):
        return cwd_candidate
    root_candidate = ROOT / p
    if path_is_file(root_candidate):
        return root_candidate
    return cwd_candidate


def infer_repo_root(manifest_path):
    manifest_abs = Path(os.path.abspath(str(manifest_path)))
    for ancestor in [manifest_abs.parent, *manifest_abs.parents]:
        if (ancestor / "game").is_dir() and (ancestor / "tools").is_dir():
            return ancestor
    return None


def resolve_source_ref(reference, repo_root, manifest_dir):
    p = Path(reference)
    if p.is_absolute():
        return p
    for base in (repo_root, manifest_dir):
        if base is None:
            continue
        candidate = Path(base) / p
        if path_exists(candidate):
            return candidate
    return Path(repo_root) / p if repo_root is not None else Path(manifest_dir) / p


def resolve_local_ref(reference, base_dir, repo_root):
    p = Path(reference)
    if p.is_absolute():
        return p
    base_candidate = Path(base_dir) / p
    if path_exists(base_candidate):
        return base_candidate
    if repo_root is not None:
        root_candidate = Path(repo_root) / p
        if path_exists(root_candidate):
            return root_candidate
    return base_candidate


def load_json(path):
    raw = read_bytes(path)
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("top-level JSON value is not an object")
    return data


# ---------------------------------------------------------------------------
# Checks and shared readers
# ---------------------------------------------------------------------------


class Checks:
    def __init__(self):
        self.items = []

    def ck(self, ok, label, detail=None):
        self.items.append({"check": label, "passed": bool(ok), "detail": detail})

    def failed(self):
        return [item["check"] for item in self.items if not item["passed"]]


def iter_file_refs(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ("file", "exact_source") and isinstance(child, str):
                yield child
            else:
                yield from iter_file_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_file_refs(child)


def direction_folder(source):
    directions = source.get("directions")
    return directions if isinstance(directions, dict) else {}


def iter_direction_entries(source):
    for direction in DIRECTIONS:
        bank = direction_folder(source).get(direction)
        if not isinstance(bank, dict):
            continue
        static = bank.get("static")
        if isinstance(static, dict):
            yield "static", direction, None, static
        for action in ACTIONS:
            frames = bank.get(action)
            if isinstance(frames, list):
                for index, entry in enumerate(frames):
                    if isinstance(entry, dict):
                        yield action, direction, index, entry
        bridges = bank.get("stop_bridges")
        if isinstance(bridges, dict):
            for phase, bridge in bridges.items():
                if isinstance(bridge, list):
                    for index, entry in enumerate(bridge):
                        if isinstance(entry, dict) and "file" in entry:
                            yield "stop", direction, f"{phase}[{index}]", entry
        for name in ("pxo", "ora"):
            entry = bank.get(name)
            if isinstance(entry, dict):
                yield name, direction, None, entry


def entry_label(kind, direction, index):
    if index is None:
        return f"{kind}.{direction}"
    return f"{kind}.{direction}[{index}]"


def check_file_entry(checks, kind, direction, index, entry, repo_root, manifest_dir, seen_paths, seen_names):
    label = entry_label(kind, direction, index)
    reference = entry.get("file")
    checks.ck(isinstance(reference, str) and bool(reference), f"source.file_path.{label}", reference)
    if not isinstance(reference, str) or not reference:
        return
    path = resolve_source_ref(reference, repo_root, manifest_dir)
    checks.ck(path_is_file(path), f"source.file_exists.{label}", display_path(path, repo_root))
    if not path_is_file(path):
        return
    actual = sha256_file(path)
    declared = entry.get("sha256")
    checks.ck(
        isinstance(declared, str) and HEX64.match(declared) is not None and declared == actual,
        f"source.file_hash.{label}",
        {"declared": declared, "actual": actual},
    )
    if kind in ("static", "idle", "walk", "stop"):
        name = path.name
        checks.ck(ASSET_RE.match(name) is not None, f"source.asset_name.{label}", name)
        checks.ck(name not in seen_names, f"source.asset_name_unique.{label}", seen_names.get(name))
        seen_names[name] = label
    key = os.path.normcase(os.path.abspath(str(path)))
    checks.ck(key not in seen_paths, f"source.file_distinct.{label}", seen_paths.get(key))
    seen_paths[key] = label


def check_hash_descriptor(checks, label, entry, repo_root, manifest_dir, require_text=False):
    reference = entry.get("file")
    checks.ck(isinstance(reference, str) and bool(reference), f"provenance.{label}.file", reference)
    if not isinstance(reference, str) or not reference:
        return None
    path = resolve_source_ref(reference, repo_root, manifest_dir)
    checks.ck(path_is_file(path), f"provenance.{label}.exists", display_path(path, repo_root))
    if not path_is_file(path):
        return path
    checked = False
    if "sha256" in entry:
        declared = entry.get("sha256")
        actual = sha256_file(path)
        checks.ck(
            isinstance(declared, str) and HEX64.match(declared) is not None and declared == actual,
            f"provenance.{label}.sha256_bytes",
            {"declared": declared, "actual": actual},
        )
        checked = True
    if "sha256_text_lf_v1" in entry or require_text:
        declared = entry.get("sha256_text_lf_v1")
        try:
            actual = text_lf_sha256(read_bytes(path))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            checks.ck(False, f"provenance.{label}.sha256_text_lf_v1", f"{type(exc).__name__}: {exc}")
        else:
            checks.ck(
                isinstance(declared, str) and HEX64.match(declared) is not None and declared == actual,
                f"provenance.{label}.sha256_text_lf_v1",
                {"declared": declared, "actual": actual},
            )
        checked = True
    if not checked:
        checks.ck(False, f"provenance.{label}.hash_declared", "no sha256/sha256_text_lf_v1")
    algorithm = entry.get("hash")
    if algorithm is not None:
        allowed = {"sha256-bytes", "sha256-text-lf-v1"}
        checks.ck(algorithm in allowed, f"provenance.{label}.hash_algorithm", algorithm)
    return path


def check_source(source, actor, repo_root, manifest_dir, checks):
    meta = {}
    source_actor = None
    if isinstance(source.get("visual_id"), str):
        source_actor = source["visual_id"]
    if isinstance(source.get("actor_id"), str):
        if source_actor is not None and source_actor != source["actor_id"]:
            checks.ck(False, "source.actor_fields_agree", {"visual_id": source_actor, "actor_id": source["actor_id"]})
        source_actor = source_actor if source_actor is not None else source["actor_id"]
    checks.ck(source_actor == actor, "source.actor_matches_argument", {"expected": actor, "actual": source_actor})
    meta["actor"] = source_actor

    contract = source.get("contract")
    checks.ck(isinstance(contract, dict), "source.contract_object")
    contract = contract if isinstance(contract, dict) else {}
    checks.ck(contract.get("pivot") == PIVOT, "source.pivot_40_104", contract.get("pivot"))
    density = contract.get("density")
    checks.ck(
        isinstance(density, int) and not isinstance(density, bool) and density == DENSITY,
        "source.density_2",
        density,
    )
    checks.ck(contract.get("cell") == FRAME_SIZE, "source.frame_size_80_112", contract.get("cell"))
    checks.ck(contract.get("logical_height") == LOGICAL_HEIGHT, "source.logical_height_48", contract.get("logical_height"))
    meta["contract"] = {
        "pivot": contract.get("pivot"),
        "density": density,
        "cell": contract.get("cell"),
        "logical_height": contract.get("logical_height"),
    }

    directions = direction_folder(source)
    checks.ck(isinstance(source.get("directions"), dict), "source.directions_object")
    checks.ck(set(directions) == set(DIRECTIONS), "source.exactly_four_directions", sorted(directions))
    required = ("static", "idle", "walk", "stop_bridges", "pxo", "ora")
    for direction in DIRECTIONS:
        bank = directions.get(direction)
        checks.ck(isinstance(bank, dict), f"source.direction.{direction}.object")
        if not isinstance(bank, dict):
            continue
        missing = [key for key in required if key not in bank]
        checks.ck(not missing, f"source.direction.{direction}.keys", missing)
        idle = bank.get("idle")
        walk = bank.get("walk")
        checks.ck(
            isinstance(idle, list) and MIN_FRAMES["idle"] <= len(idle) <= MAX_FRAMES,
            f"source.idle_count.{direction}",
            len(idle) if isinstance(idle, list) else None,
        )
        checks.ck(
            isinstance(walk, list) and MIN_FRAMES["walk"] <= len(walk) <= MAX_FRAMES,
            f"source.walk_count.{direction}",
            len(walk) if isinstance(walk, list) else None,
        )

    counts = {}
    for direction in DIRECTIONS:
        bank = directions.get(direction)
        if not isinstance(bank, dict):
            continue
        counts[direction] = {
            action: len(bank.get(action)) if isinstance(bank.get(action), list) else None
            for action in ACTIONS
        }
    checks.ck(len({json.dumps(value, sort_keys=True) for value in counts.values()}) == 1,
              "source.direction_counts_consistent", counts)
    meta["counts"] = counts

    idle_model = source.get("idle_model")
    idle_model = idle_model if isinstance(idle_model, dict) else {}
    model_idle_durations = idle_model.get("duration_ms")
    walk_model = source.get("walk_model")
    walk_model = walk_model if isinstance(walk_model, dict) else {}
    reference_frame_ms = walk_model.get("frame_ms_reference")
    for direction in DIRECTIONS:
        bank = directions.get(direction)
        if not isinstance(bank, dict):
            continue
        idle = bank.get("idle") if isinstance(bank.get("idle"), list) else []
        walk = bank.get("walk") if isinstance(bank.get("walk"), list) else []
        idle_durations = [entry.get("duration_ms") for entry in idle if isinstance(entry, dict)]
        walk_durations = [entry.get("duration_ms") for entry in walk if isinstance(entry, dict)]
        checks.ck(
            bool(idle_durations) and all(
                isinstance(value, int) and not isinstance(value, bool)
                and MIN_DURATION_MS <= value <= MAX_DURATION_MS
                for value in idle_durations
            ),
            f"source.idle_durations.{direction}",
            idle_durations,
        )
        checks.ck(
            bool(walk_durations) and all(
                isinstance(value, int) and not isinstance(value, bool)
                and MIN_DURATION_MS <= value <= MAX_DURATION_MS
                for value in walk_durations
            ),
            f"source.walk_durations.{direction}",
            walk_durations,
        )
        if isinstance(model_idle_durations, list):
            checks.ck(
                idle_durations == model_idle_durations,
                f"source.idle_durations_match_model.{direction}",
                {"actual": idle_durations, "model": model_idle_durations},
            )
        if isinstance(reference_frame_ms, int):
            checks.ck(
                all(value == reference_frame_ms for value in walk_durations),
                f"source.walk_durations_match_model.{direction}",
                {"actual": walk_durations, "model": reference_frame_ms},
            )

    seen_paths = {}
    seen_names = {}
    for kind, direction, index, entry in iter_direction_entries(source):
        check_file_entry(checks, kind, direction, index, entry, repo_root, manifest_dir, seen_paths, seen_names)

    for direction in DIRECTIONS:
        bank = directions.get(direction)
        if not isinstance(bank, dict):
            continue
        walk = bank.get("walk") if isinstance(bank.get("walk"), list) else []
        bridges = bank.get("stop_bridges")
        expected_phases = {f"phase{index}" for index in range(len(walk))}
        checks.ck(isinstance(bridges, dict), f"source.stop_bridges_object.{direction}")
        if not isinstance(bridges, dict):
            continue
        checks.ck(set(bridges) == expected_phases, f"source.stop_phases_exact.{direction}",
                  {"actual": sorted(bridges), "expected": sorted(expected_phases)})
        for phase, bridge in bridges.items():
            label = f"{direction}.{phase}"
            checks.ck(isinstance(bridge, list) and len(bridge) == 4, f"source.stop_length.{label}",
                      len(bridge) if isinstance(bridge, list) else None)
            if not isinstance(bridge, list) or len(bridge) != 4:
                continue
            try:
                phase_index = int(phase.removeprefix("phase"))
            except ValueError:
                checks.ck(False, f"source.stop_phase_name.{label}", phase)
                continue
            first = {"ref": "walk", "index": phase_index, "k": 0.0}
            last = {"ref": "idle", "index": 0, "k": 1.0}
            checks.ck(bridge[0] == first, f"source.stop_endpoint_first.{label}", bridge[0])
            checks.ck(bridge[-1] == last, f"source.stop_endpoint_last.{label}", bridge[-1])
            middle = [bridge[1], bridge[2]]
            checks.ck(
                all(isinstance(entry, dict) and isinstance(entry.get("k"), (int, float)) for entry in middle)
                and 0.0 < float(middle[0]["k"]) < float(middle[1]["k"]) < 1.0,
                f"source.stop_middle_k.{label}",
                [entry.get("k") if isinstance(entry, dict) else None for entry in middle],
            )
            for position in (1, 2):
                entry = bridge[position]
                if not isinstance(entry, dict):
                    checks.ck(False, f"source.stop_entry.{label}.{position}", entry)
                    continue
                reference = entry.get("file")
                path = resolve_source_ref(reference, repo_root, manifest_dir) if isinstance(reference, str) else None
                checks.ck(path is not None and path_is_file(path), f"source.stop_file_exists.{label}.{position}",
                          display_path(path, repo_root) if path is not None else None)
                if path is None or not path_is_file(path):
                    continue
                actual = sha256_file(path)
                declared = entry.get("sha256")
                checks.ck(declared == actual, f"source.stop_file_hash.{label}.{position}",
                          {"declared": declared, "actual": actual})
            if not (0 <= phase_index < len(walk)):
                checks.ck(False, f"source.stop_phase_index.{label}", phase_index)

    south = directions.get("south")
    south = south if isinstance(south, dict) else {}
    static = south.get("static")
    static = static if isinstance(static, dict) else {}
    exact_source = static.get("exact_source")
    checks.ck(isinstance(exact_source, str) and bool(exact_source), "south.exact_source_present", exact_source)
    exact_path = None
    if isinstance(exact_source, str) and exact_source:
        exact_path = resolve_source_ref(exact_source, repo_root, manifest_dir)
        checks.ck(path_is_file(exact_path), "south.exact_source_exists", display_path(exact_path, repo_root))
        if path_is_file(exact_path):
            actual = sha256_file(exact_path)
            checks.ck(actual == static.get("sha256"), "south.exact_source_matches_static_hash",
                      {"exactSource": actual, "static": static.get("sha256")})
    idle = south.get("idle") if isinstance(south.get("idle"), list) else []
    if idle and isinstance(idle[0], dict):
        checks.ck(idle[0].get("sha256") == static.get("sha256"), "south.idle_neutral_equals_static",
                  {"idle0": idle[0].get("sha256"), "static": static.get("sha256")})
    meta["south"] = {
        "staticFile": static.get("file"),
        "staticSha256": static.get("sha256"),
        "exactSource": exact_source,
    }

    source_inputs = source.get("source_inputs")
    checks.ck(isinstance(source_inputs, dict) and bool(source_inputs), "provenance.source_inputs_present")
    source_inputs = source_inputs if isinstance(source_inputs, dict) else {}
    input_paths = {}
    for name, entry in source_inputs.items():
        if not isinstance(entry, dict):
            checks.ck(False, f"provenance.source_inputs.{name}.object", entry)
            continue
        path = check_hash_descriptor(checks, f"source_inputs.{name}", entry, repo_root, manifest_dir)
        input_paths[name] = path
    if exact_path is not None:
        matches = [
            name for name, path in input_paths.items()
            if path is not None
            and os.path.normcase(os.path.abspath(str(path))) == os.path.normcase(os.path.abspath(str(exact_path)))
        ]
        matched_by = "path"
        if not matches:
            matches = [
                name for name, entry in source_inputs.items()
                if isinstance(entry, dict) and entry.get("sha256") == static.get("sha256")
            ]
            matched_by = "sha256"
        checks.ck(bool(matches), "south.exact_source_in_source_inputs",
                  {"matches": matches, "matchedBy": matched_by})
        if matches:
            declared = source_inputs.get(matches[0], {}).get("sha256")
            checks.ck(declared == static.get("sha256"), "south.exact_source_input_hash_matches_static",
                      {"input": declared, "static": static.get("sha256")})

    tool = source.get("tool")
    checks.ck(isinstance(tool, dict), "provenance.tool_present")
    if isinstance(tool, dict):
        check_hash_descriptor(checks, "tool", tool, repo_root, manifest_dir, require_text=True)
    reused = source.get("reused_helpers")
    if isinstance(reused, dict):
        check_hash_descriptor(checks, "reused_helpers", reused, repo_root, manifest_dir, require_text=True)

    package = source.get("package")
    checks.ck(isinstance(package, dict), "package.object")
    package = package if isinstance(package, dict) else {}
    paths = {}
    for key in ("sprite_set", "registry", "stop_supplemental"):
        reference = package.get(key)
        checks.ck(isinstance(reference, str) and bool(reference), f"package.{key}.path", reference)
        if isinstance(reference, str) and reference:
            path = resolve_source_ref(reference, repo_root, manifest_dir)
            paths[key] = path
            checks.ck(path_is_file(path), f"package.{key}.exists", display_path(path, repo_root))
    if "sprite_set" in paths and path_is_file(paths["sprite_set"]):
        actual = sha256_file(paths["sprite_set"])
        declared = package.get("sprite_set_sha256")
        checks.ck(declared == actual, "package.sprite_set_sha256", {"declared": declared, "actual": actual})
    if "stop_supplemental" in paths and path_is_file(paths["stop_supplemental"]):
        try:
            actual = text_lf_sha256(read_bytes(paths["stop_supplemental"]))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            checks.ck(False, "package.stop_supplemental_sha256_text_lf_v1", f"{type(exc).__name__}: {exc}")
        else:
            declared = package.get("stop_supplemental_sha256_text_lf_v1")
            checks.ck(declared == actual, "package.stop_supplemental_sha256_text_lf_v1",
                      {"declared": declared, "actual": actual})
    if "registry_sha256" in package and "registry" in paths and path_is_file(paths["registry"]):
        actual = sha256_file(paths["registry"])
        checks.ck(package.get("registry_sha256") == actual, "package.registry_sha256",
                  {"declared": package.get("registry_sha256"), "actual": actual})
    meta["package"] = {
        key: (display_path(value, repo_root) if value is not None else None)
        for key, value in paths.items()
    }
    return meta, paths, exact_path


def check_runtime_set(runtime, source, actor, repo_root, runtime_path, checks):
    meta = {}
    runtime_dir = runtime_path.parent
    checks.ck(runtime.get("schema") == SET_SCHEMA, "runtime.schema", runtime.get("schema"))
    checks.ck(runtime.get("actor_id") == actor, "runtime.actor_matches_argument",
              {"expected": actor, "actual": runtime.get("actor_id")})
    checks.ck(runtime.get("density") == DENSITY, "runtime.density_matches_source", runtime.get("density"))
    checks.ck(runtime.get("frame_size") == FRAME_SIZE, "runtime.frame_size_80_112", runtime.get("frame_size"))
    checks.ck(runtime.get("pivot") == PIVOT, "runtime.pivot_matches_source", runtime.get("pivot"))
    actions = runtime.get("actions")
    checks.ck(isinstance(actions, dict), "runtime.actions_object")
    actions = actions if isinstance(actions, dict) else {}
    checks.ck(set(actions) == set(ACTIONS), "runtime.actions_exact", sorted(actions))
    directions = direction_folder(source)
    seen_paths = {}
    seen_names = {}
    for action in ACTIONS:
        by_direction = actions.get(action)
        checks.ck(isinstance(by_direction, dict), f"runtime.actions.{action}.object")
        by_direction = by_direction if isinstance(by_direction, dict) else {}
        checks.ck(set(by_direction) == set(DIRECTIONS), f"runtime.actions.{action}.directions", sorted(by_direction))
        for direction in DIRECTIONS:
            runtime_frames = by_direction.get(direction)
            runtime_frames = runtime_frames if isinstance(runtime_frames, list) else []
            source_frames = directions.get(direction, {}).get(action) if isinstance(directions.get(direction), dict) else None
            source_frames = source_frames if isinstance(source_frames, list) else []
            checks.ck(len(runtime_frames) == len(source_frames), f"runtime.count.{action}.{direction}",
                      {"runtime": len(runtime_frames), "source": len(source_frames)})
            for index in range(min(len(runtime_frames), len(source_frames))):
                label = f"{action}.{direction}[{index}]"
                runtime_entry = runtime_frames[index]
                source_entry = source_frames[index]
                if not isinstance(runtime_entry, dict) or not isinstance(source_entry, dict):
                    checks.ck(False, f"runtime.entry.{label}", "entry is not an object")
                    continue
                reference = runtime_entry.get("file")
                path = resolve_local_ref(reference, runtime_dir, repo_root) if isinstance(reference, str) else None
                checks.ck(path is not None and path_is_file(path), f"runtime.frame_exists.{label}",
                          display_path(path, repo_root) if path is not None else None)
                if path is None or not path_is_file(path):
                    continue
                actual = sha256_file(path)
                checks.ck(actual == source_entry.get("sha256"), f"runtime.frame_hash.{label}",
                          {"runtime": actual, "source": source_entry.get("sha256"),
                           "file": display_path(path, repo_root)})
                source_name = Path(str(source_entry.get("file", ""))).name
                checks.ck(path.name == source_name, f"runtime.frame_name.{label}",
                          {"runtime": path.name, "source": source_name})
                checks.ck(ASSET_RE.match(path.name) is not None, f"runtime.asset_name.{label}", path.name)
                checks.ck(path.name not in seen_names, f"runtime.asset_name_unique.{label}", seen_names.get(path.name))
                seen_names[path.name] = label
                key = os.path.normcase(os.path.abspath(str(path)))
                checks.ck(key not in seen_paths, f"runtime.frame_distinct.{label}", seen_paths.get(key))
                seen_paths[key] = label
                checks.ck(runtime_entry.get("duration_ms") == source_entry.get("duration_ms"),
                          f"runtime.frame_duration.{label}",
                          {"runtime": runtime_entry.get("duration_ms"), "source": source_entry.get("duration_ms")})
    meta["actor"] = runtime.get("actor_id")
    meta["setId"] = runtime.get("set_id")
    meta["actions"] = {
        action: {
            direction: len(actions.get(action, {}).get(direction, []))
            for direction in DIRECTIONS
        }
        for action in ACTIONS
    }
    return meta


def check_registry(registry, actor, repo_root, runtime_path, registry_path, checks):
    meta = {}
    checks.ck(registry.get("schema") == REGISTRY_SCHEMA, "registry.schema", registry.get("schema"))
    actors = registry.get("actors")
    checks.ck(isinstance(actors, dict), "registry.actors_object")
    actors = actors if isinstance(actors, dict) else {}
    checks.ck(len(actors) == 1, "registry.exactly_one_actor", len(actors))
    if len(actors) == 1:
        key, value = next(iter(actors.items()))
        checks.ck(key == actor, "registry.actor_matches_argument", {"expected": actor, "actual": key})
        checks.ck(isinstance(value, str) and bool(value), "registry.set_reference_path", value)
        if isinstance(value, str) and value:
            resolved = resolve_local_ref(value, registry_path.parent, repo_root)
            checks.ck(path_is_file(resolved), "registry.set_reference_resolves", display_path(resolved, repo_root))
            checks.ck(os.path.normcase(os.path.abspath(str(resolved))) == os.path.normcase(os.path.abspath(str(runtime_path))),
                      "registry.set_reference_matches_package",
                      {"resolved": display_path(resolved, repo_root),
                       "package": display_path(runtime_path, repo_root)})
    checks.ck(registry_path.parent.name != "exploration-sprite-sets", "registry.not_default_registry",
              display_path(registry_path, repo_root))
    return meta


def check_stop(stop, source, actor, repo_root, stop_path, checks):
    meta = {}
    stop_dir = stop_path.parent
    checks.ck(stop.get("schema") == STOP_SCHEMA, "stop.schema", stop.get("schema"))
    checks.ck(stop.get("actor_id") == actor, "stop.actor_matches_argument",
              {"expected": actor, "actual": stop.get("actor_id")})
    checks.ck(stop.get("pivot") == PIVOT, "stop.pivot_matches_source", stop.get("pivot"))
    checks.ck(stop.get("logical_height") == LOGICAL_HEIGHT, "stop.logical_height_48", stop.get("logical_height"))
    checks.ck(stop.get("runtime_default") is False, "stop.runtime_default_false", stop.get("runtime_default"))
    frame_ms = stop.get("frame_ms")
    checks.ck(isinstance(frame_ms, int) and not isinstance(frame_ms, bool) and frame_ms > 0,
              "stop.frame_ms_positive", frame_ms)
    settle_ms = stop.get("settle_ms_inclusive")
    checks.ck(isinstance(settle_ms, int) and not isinstance(settle_ms, bool) and settle_ms > 0,
              "stop.settle_ms_positive", settle_ms)
    walk_model = source.get("walk_model") if isinstance(source.get("walk_model"), dict) else {}
    reference = walk_model.get("frame_ms_reference")
    if isinstance(reference, int):
        checks.ck(frame_ms == reference, "stop.frame_ms_matches_walk_model", {"stop": frame_ms, "walk": reference})
    phase_bridges = stop.get("phase_bridges")
    checks.ck(isinstance(phase_bridges, dict), "stop.phase_bridges_object")
    phase_bridges = phase_bridges if isinstance(phase_bridges, dict) else {}
    checks.ck(set(phase_bridges) == set(DIRECTIONS), "stop.exactly_four_directions", sorted(phase_bridges))
    directions = direction_folder(source)
    seen_paths = {}
    for direction in DIRECTIONS:
        runtime_bridges = phase_bridges.get(direction)
        runtime_bridges = runtime_bridges if isinstance(runtime_bridges, dict) else {}
        source_bridges = directions.get(direction, {}).get("stop_bridges") if isinstance(directions.get(direction), dict) else None
        source_bridges = source_bridges if isinstance(source_bridges, dict) else {}
        checks.ck(set(runtime_bridges) == set(source_bridges), f"stop.phases_exact.{direction}",
                  {"runtime": sorted(runtime_bridges), "source": sorted(source_bridges)})
        for phase, source_bridge in source_bridges.items():
            label = f"{direction}.{phase}"
            runtime_bridge = runtime_bridges.get(phase)
            checks.ck(isinstance(runtime_bridge, list) and len(runtime_bridge) == 4,
                      f"stop.length.{label}", len(runtime_bridge) if isinstance(runtime_bridge, list) else None)
            if not isinstance(runtime_bridge, list) or len(runtime_bridge) != 4:
                continue
            if isinstance(source_bridge, list) and len(source_bridge) == 4:
                checks.ck(runtime_bridge[0] == source_bridge[0], f"stop.endpoint_first.{label}", runtime_bridge[0])
                checks.ck(runtime_bridge[-1] == source_bridge[-1], f"stop.endpoint_last.{label}", runtime_bridge[-1])
            for position in (1, 2):
                runtime_entry = runtime_bridge[position]
                source_entry = source_bridge[position] if isinstance(source_bridge, list) and len(source_bridge) > position else {}
                if not isinstance(runtime_entry, dict):
                    checks.ck(False, f"stop.entry.{label}.{position}", runtime_entry)
                    continue
                checks.ck(runtime_entry.get("k") == source_entry.get("k"), f"stop.k.{label}.{position}",
                          {"runtime": runtime_entry.get("k"), "source": source_entry.get("k")})
                reference_value = runtime_entry.get("file")
                path = resolve_local_ref(reference_value, stop_dir, repo_root) if isinstance(reference_value, str) else None
                checks.ck(path is not None and path_is_file(path), f"stop.file_exists.{label}.{position}",
                          display_path(path, repo_root) if path is not None else None)
                if path is None or not path_is_file(path):
                    continue
                actual = sha256_file(path)
                checks.ck(actual == runtime_entry.get("sha256"), f"stop.file_hash.{label}.{position}",
                          {"declared": runtime_entry.get("sha256"), "actual": actual})
                checks.ck(runtime_entry.get("sha256") == source_entry.get("sha256"),
                          f"stop.source_hash_matches.{label}.{position}",
                          {"runtime": runtime_entry.get("sha256"), "source": source_entry.get("sha256")})
                key = os.path.normcase(os.path.abspath(str(path)))
                checks.ck(key not in seen_paths, f"stop.file_distinct.{label}.{position}", seen_paths.get(key))
                seen_paths[key] = f"{label}.{position}"
    meta["frameMs"] = frame_ms
    meta["settleMsInclusive"] = settle_ms
    return meta


def execute_check(manifest_path, actor, repo_root, out_dir, run_tag, label, write_result=True):
    started = datetime.now(timezone.utc)
    checks = Checks()
    result = {
        "project": PROJECT_SLUG,
        "subject": SUBJECT,
        "purpose": PURPOSE,
        "variant": VARIANT,
        "label": label,
        "runTag": run_tag,
        "actor": actor,
        "manifest": {"path": str(manifest_path), "sha256": None},
        "repoRoot": str(repo_root),
        "checker": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(__file__)},
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "nativePixelComposite": "not run by this wrapper; existing native-bank checker is separate",
        "godot": "not run",
        "checks": checks.items,
        "source": {},
        "runtime": {},
        "registry": {},
        "stop": {},
        "sourcePortraitStatus": "CONCEPT only; no approval inferred",
        "artApproved": False,
        "humanPlaytest": False,
        "startedUtc": started.isoformat(),
    }
    try:
        raw = read_bytes(manifest_path)
        result["manifest"]["sha256"] = sha256_bytes(raw)
        source = json.loads(raw.decode("utf-8"))
        if not isinstance(source, dict):
            raise ValueError("source manifest top-level JSON is not an object")
    except Exception as exc:  # noqa: BLE001 - reported as a contract failure
        checks.ck(False, "manifest.parse", f"{type(exc).__name__}: {exc}")
        source = None

    if source is not None:
        try:
            source_meta, package_paths, exact_path = check_source(
                source, actor, repo_root, Path(manifest_path).parent, checks
            )
            result["source"] = source_meta
        except Exception as exc:  # noqa: BLE001
            checks.ck(False, "source.section_exception", f"{type(exc).__name__}: {exc}")
            package_paths = {}
            exact_path = None
        try:
            runtime_path = package_paths.get("sprite_set")
            if runtime_path is not None and path_is_file(runtime_path):
                runtime = load_json(runtime_path)
                result["runtime"] = check_runtime_set(runtime, source, actor, repo_root, runtime_path, checks)
            else:
                checks.ck(False, "runtime.available", "sprite_set package file is missing")
        except Exception as exc:  # noqa: BLE001
            checks.ck(False, "runtime.section_exception", f"{type(exc).__name__}: {exc}")
        try:
            registry_path = package_paths.get("registry")
            if registry_path is not None and path_is_file(registry_path):
                registry = load_json(registry_path)
                result["registry"] = check_registry(
                    registry, actor, repo_root, package_paths.get("sprite_set"), registry_path, checks
                )
            else:
                checks.ck(False, "registry.available", "registry package file is missing")
        except Exception as exc:  # noqa: BLE001
            checks.ck(False, "registry.section_exception", f"{type(exc).__name__}: {exc}")
        try:
            stop_path = package_paths.get("stop_supplemental")
            if stop_path is not None and path_is_file(stop_path):
                stop = load_json(stop_path)
                result["stop"] = check_stop(stop, source, actor, repo_root, stop_path, checks)
            else:
                checks.ck(False, "stop.available", "stop supplemental package file is missing")
        except Exception as exc:  # noqa: BLE001
            checks.ck(False, "stop.section_exception", f"{type(exc).__name__}: {exc}")
        result["south"] = result.get("source", {}).get("south")
        result["exactSourcePath"] = display_path(exact_path, repo_root) if exact_path is not None else None

    result["finishedUtc"] = datetime.now(timezone.utc).isoformat()
    result["failedChecks"] = checks.failed()
    result["passed"] = not result["failedChecks"]
    result["scope"] = {
        "sourceContractOnly": True,
        "nativePixelComposite": False,
        "godot": False,
        "artApproved": False,
        "runtimeIntegrated": False,
        "defaultChanged": False,
        "ledgerOrGitChanged": False,
        "jiChengTested": actor == "ji-cheng",
        "note": (
            "Ji Cheng source was tested only if actor == ji-cheng; a different actor does not establish Ji."
        ),
    }
    if write_result:
        ensure_dir(out_dir)
        name = (
            f"{PROJECT_SLUG}_{SUBJECT}_identity-runtime-{label}_{VARIANT}_{run_tag}.json"
        )
        result["resultPath"] = str(out_dir / name)
        write_text(out_dir / name, json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result


# ---------------------------------------------------------------------------
# Isolated negative fixtures (copies only; originals are read-only)
# ---------------------------------------------------------------------------


def copy_exact(source, destination):
    data = read_bytes(source)
    write_bytes(destination, data)
    return sha256_bytes(data)


def clone_manifest_to_fixture(source_data, manifest_path, repo_root, fixture_root):
    data = copy.deepcopy(source_data)
    src_dir = fixture_root / "src"
    ensure_dir(src_dir)
    mapping = {}
    evidence = []
    missing = []

    def copy_ref(reference):
        original = resolve_source_ref(reference, repo_root, Path(manifest_path).parent)
        key = os.path.normcase(os.path.abspath(str(original)))
        if key in mapping:
            return mapping[key]
        if not path_is_file(original):
            missing.append(reference)
            destination = src_dir / ("missing-" + str(len(mapping)).zfill(4) + (Path(reference).suffix.lower() or ".bin"))
            mapping[key] = str(destination)
            return str(destination)
        destination = src_dir / original.name
        if path_exists(destination) and sha256_file(destination) != sha256_file(original):
            destination = src_dir / (str(len(mapping)).zfill(4) + "-" + original.name)
        digest = copy_exact(original, destination)
        mapping[key] = str(destination)
        evidence.append({
            "original": display_path(original, repo_root),
            "fixture": str(destination),
            "sha256": digest,
        })
        return str(destination)

    def rewrite(value):
        if isinstance(value, dict):
            for key, child in list(value.items()):
                if key in ("file", "exact_source") and isinstance(child, str):
                    value[key] = copy_ref(child)
                else:
                    rewrite(child)
        elif isinstance(value, list):
            for child in value:
                rewrite(child)

    rewrite(data)
    return data, {"mappingCount": len(mapping), "missing": missing, "files": evidence}


def clone_runtime_to_fixture(data, manifest_path, repo_root, fixture_root):
    runtime_dir = fixture_root / "runtime"
    ensure_dir(runtime_dir)
    package = data.get("package")
    if not isinstance(package, dict):
        raise ValueError("source manifest has no package object")
    evidence = []
    copied_names = {}
    for key in ("sprite_set", "registry", "stop_supplemental"):
        reference = package.get(key)
        if not isinstance(reference, str):
            raise ValueError(f"package.{key} is not a path")
        original = resolve_source_ref(reference, repo_root, Path(manifest_path).parent)
        if not path_is_file(original):
            raise FileNotFoundError(f"package.{key} missing: {original}")
        destination = runtime_dir / original.name
        if original.name in copied_names:
            raise ValueError(
                f"duplicate package file name: {original.name} ({copied_names[original.name]} and {key})"
            )
        copied_names[original.name] = key
        digest = copy_exact(original, destination)
        package[key] = str(destination)
        evidence.append({"key": key, "original": display_path(original, repo_root),
                         "fixture": str(destination), "sha256": digest})
    for key in ("sprite_set", "stop_supplemental"):
        document_path = Path(package[key])
        document = load_json(document_path)
        original_document = resolve_source_ref(
            next(item["original"] for item in evidence if item["key"] == key),
            repo_root,
            Path(manifest_path).parent,
        )
        original_dir = original_document.parent
        references = []
        if key == "sprite_set":
            actions = document.get("actions") if isinstance(document.get("actions"), dict) else {}
            for action in ACTIONS:
                by_direction = actions.get(action) if isinstance(actions.get(action), dict) else {}
                for direction in DIRECTIONS:
                    frames = by_direction.get(direction) if isinstance(by_direction.get(direction), list) else []
                    for entry in frames:
                        if isinstance(entry, dict) and isinstance(entry.get("file"), str):
                            references.append(entry["file"])
        else:
            bridges = document.get("phase_bridges") if isinstance(document.get("phase_bridges"), dict) else {}
            for direction in DIRECTIONS:
                phases = bridges.get(direction) if isinstance(bridges.get(direction), dict) else {}
                for bridge in phases.values():
                    if isinstance(bridge, list):
                        for entry in bridge:
                            if isinstance(entry, dict) and isinstance(entry.get("file"), str):
                                references.append(entry["file"])
        for reference in references:
            original = resolve_local_ref(reference, original_dir, repo_root)
            if not path_is_file(original):
                raise FileNotFoundError(f"runtime frame missing: {original}")
            destination = runtime_dir / Path(reference)
            if not is_within(destination, runtime_dir):
                raise ValueError(f"runtime frame escapes fixture: {reference}")
            ensure_dir(destination.parent)
            if path_is_file(destination):
                if sha256_file(destination) != sha256_file(original):
                    raise ValueError(f"runtime frame collision with different bytes: {reference}")
            else:
                copy_exact(original, destination)
    return evidence


def write_fixture(fixture_root, data, clone_evidence, runtime_evidence, run_tag):
    ensure_dir(fixture_root / "game")
    ensure_dir(fixture_root / "tools")
    manifest_path = fixture_root / "manifest.json"
    write_text(manifest_path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    write_text(fixture_root / MARKER, run_tag)
    write_text(
        fixture_root / "fixture-evidence.json",
        json.dumps({
            "marker": run_tag,
            "manifest": str(manifest_path),
            "manifestSha256": sha256_file(manifest_path),
            "sourceCopies": clone_evidence,
            "runtimeCopies": runtime_evidence,
        }, indent=2, ensure_ascii=False) + "\n",
    )
    return manifest_path


def mutate_registry_actor(fixture_root, data, source_data, actor, repo_root):
    registry_path = Path(data["package"]["registry"])
    if not is_within(registry_path, fixture_root):
        raise ValueError("registry fixture escaped its root")
    before = read_bytes(registry_path)
    registry = json.loads(before.decode("utf-8"))
    actors = registry.get("actors") if isinstance(registry.get("actors"), dict) else {}
    if len(actors) != 1:
        raise ValueError("source registry does not have exactly one actor to mutate")
    old_key, old_value = next(iter(actors.items()))
    wrong = "not-" + actor if actor != "not-" + actor else "unexpected-" + actor
    registry["actors"] = {wrong: old_value}
    after = (json.dumps(registry, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    write_bytes(registry_path, after)
    return {
        "type": "wrong-registry-actor",
        "registry": str(registry_path),
        "beforeActor": old_key,
        "afterActor": wrong,
        "setReferenceUnchanged": old_value,
        "beforeSha256": sha256_bytes(before),
        "afterSha256": sha256_bytes(after),
    }


def mutate_runtime_png(fixture_root, data, source_data, actor, repo_root):
    set_path = Path(data["package"]["sprite_set"])
    set_dir = set_path.parent
    runtime = json.loads(read_bytes(set_path).decode("utf-8"))
    actions = runtime.get("actions") if isinstance(runtime.get("actions"), dict) else {}
    chosen = None
    for action in ("walk", "idle"):
        direction_frames = actions.get(action, {}).get("south") if isinstance(actions.get(action), dict) else None
        if isinstance(direction_frames, list) and direction_frames:
            chosen = (action, 0, direction_frames[0])
            break
    if chosen is None:
        raise ValueError("no south runtime frame available to mutate")
    action, index, runtime_entry = chosen
    runtime_path = set_dir / runtime_entry["file"]
    if not is_within(runtime_path, fixture_root):
        raise ValueError("runtime frame escaped its fixture root")
    fixture_source_frames = data.get("directions", {}).get("south", {}).get(action, [])
    fixture_source_entry = (
        fixture_source_frames[index]
        if isinstance(fixture_source_frames, list) and len(fixture_source_frames) > index
        else {}
    )
    fixture_source_copy = (
        Path(fixture_source_entry.get("file"))
        if isinstance(fixture_source_entry.get("file"), str)
        else None
    )
    original_frames = source_data.get("directions", {}).get("south", {}).get(action, [])
    original_entry = original_frames[index] if isinstance(original_frames, list) and len(original_frames) > index else {}
    original_source = (
        resolve_source_ref(original_entry.get("file"), repo_root, Path(repo_root) / "outputs")
        if isinstance(original_entry.get("file"), str)
        else None
    )
    fixture_hash_before = (
        sha256_file(fixture_source_copy)
        if fixture_source_copy is not None and path_is_file(fixture_source_copy)
        else None
    )
    original_hash_before = (
        sha256_file(original_source) if original_source is not None and path_is_file(original_source) else None
    )
    before = read_bytes(runtime_path)
    after = before + b"\x00"
    write_bytes(runtime_path, after)
    fixture_hash_after = (
        sha256_file(fixture_source_copy)
        if fixture_source_copy is not None and path_is_file(fixture_source_copy)
        else None
    )
    original_hash_after = (
        sha256_file(original_source) if original_source is not None and path_is_file(original_source) else None
    )
    return {
        "type": "changed-runtime-copied-png",
        "runtimeFrame": str(runtime_path),
        "action": action,
        "direction": "south",
        "index": index,
        "bytesBefore": len(before),
        "bytesAfter": len(after),
        "runtimeSha256Before": sha256_bytes(before),
        "runtimeSha256After": sha256_bytes(after),
        "fixtureSourceCounterpart": str(fixture_source_copy) if fixture_source_copy is not None else None,
        "fixtureSourceSha256Before": fixture_hash_before,
        "fixtureSourceSha256After": fixture_hash_after,
        "originalSource": str(original_source) if original_source is not None else None,
        "originalSourceSha256Before": original_hash_before,
        "originalSourceSha256After": original_hash_after,
        "sourceUnchanged": (
            fixture_hash_before == fixture_hash_after
            and original_hash_before == original_hash_after
        ),
        "declaredSourceSha256": original_entry.get("sha256"),
    }


def run_negative_case(case_name, mutation, source_data, manifest_path, actor, repo_root, run_root, run_tag):
    short = uuid.uuid4().hex[:8]
    fixture_root = run_root / "fixtures" / f"{case_name}-{short}"
    ensure_dir(fixture_root)
    fixture_data, source_evidence = clone_manifest_to_fixture(source_data, manifest_path, repo_root, fixture_root)
    runtime_evidence = clone_runtime_to_fixture(fixture_data, manifest_path, repo_root, fixture_root)
    mutation_record = mutation(fixture_root, fixture_data, source_data, actor, repo_root)
    fixture_manifest = write_fixture(fixture_root, fixture_data, source_evidence, runtime_evidence, run_tag)
    check_out = fixture_root / "check-out"
    check_result = execute_check(
        fixture_manifest,
        actor,
        fixture_root,
        check_out,
        run_tag,
        f"negative-{case_name}",
        write_result=True,
    )
    expected_prefix = {
        "wrong-registry-actor": "registry.actor_matches_argument",
        "changed-runtime-copied-png": "runtime.frame_hash.",
    }[case_name]
    failed = check_result["failedChecks"]
    expected_hits = [name for name in failed if name.startswith(expected_prefix)]
    unexpected = [name for name in failed if not name.startswith(expected_prefix)]
    passed = (not check_result["passed"]) and bool(expected_hits) and not unexpected
    summary = {
        "case": case_name,
        "expected": "refuse",
        "passed": passed,
        "expectedFailurePrefix": expected_prefix,
        "expectedFailureHits": expected_hits,
        "unexpectedFailures": unexpected,
        "fixtureRoot": str(fixture_root),
        "fixtureManifest": str(fixture_manifest),
        "mutation": mutation_record,
        "checkResultPath": check_result.get("resultPath"),
        "checkPassed": check_result["passed"],
        "checkCount": len(check_result["checks"]),
        "failedCount": len(failed),
        "sourceCopies": source_evidence,
        "runtimeCopies": runtime_evidence,
    }
    write_text(
        fixture_root / "negative-summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    )
    return summary


def collect_guard_paths(source, manifest_path, repo_root):
    paths = [Path(manifest_path)]
    for reference in iter_file_refs(source):
        paths.append(resolve_source_ref(reference, repo_root, Path(manifest_path).parent))
    package = source.get("package") if isinstance(source.get("package"), dict) else {}
    for key, base_key in (("sprite_set", "sprite_set"), ("registry", "registry"),
                          ("stop_supplemental", "stop_supplemental")):
        reference = package.get(key)
        if not isinstance(reference, str):
            continue
        path = resolve_source_ref(reference, repo_root, Path(manifest_path).parent)
        paths.append(path)
        if not path_is_file(path):
            continue
        try:
            document = load_json(path)
        except Exception:  # noqa: BLE001 - guard records the package file itself
            continue
        if key == "sprite_set":
            actions = document.get("actions") if isinstance(document.get("actions"), dict) else {}
            for action in ACTIONS:
                by_direction = actions.get(action) if isinstance(actions.get(action), dict) else {}
                for direction in DIRECTIONS:
                    for entry in by_direction.get(direction, []) if isinstance(by_direction.get(direction), list) else []:
                        if isinstance(entry, dict) and isinstance(entry.get("file"), str):
                            paths.append(resolve_local_ref(entry["file"], path.parent, repo_root))
        elif key == "stop_supplemental":
            bridges = document.get("phase_bridges") if isinstance(document.get("phase_bridges"), dict) else {}
            for direction in DIRECTIONS:
                phases = bridges.get(direction) if isinstance(bridges.get(direction), dict) else {}
                for bridge in phases.values():
                    for entry in bridge if isinstance(bridge, list) else []:
                        if isinstance(entry, dict) and isinstance(entry.get("file"), str):
                            paths.append(resolve_local_ref(entry["file"], path.parent, repo_root))
        elif key == "registry":
            actors = document.get("actors") if isinstance(document.get("actors"), dict) else {}
            for value in actors.values():
                if isinstance(value, str):
                    paths.append(resolve_local_ref(value, path.parent, repo_root))
    unique = {}
    for path in paths:
        key = os.path.normcase(os.path.abspath(str(path)))
        unique[key] = path
    return [unique[key] for key in sorted(unique)]


def snapshot_guard(source, manifest_path, repo_root):
    files = {}
    for path in collect_guard_paths(source, manifest_path, repo_root):
        key = display_path(path, repo_root)
        files[key] = sha256_file(path) if path_is_file(path) else "MISSING"
    payload = "\n".join(f"{key}={files[key]}" for key in sorted(files)).encode("utf-8")
    return {
        "fileCount": len(files),
        "existingCount": sum(1 for value in files.values() if value != "MISSING"),
        "missing": [key for key, value in files.items() if value == "MISSING"],
        "aggregateSha256": sha256_bytes(payload),
        "files": files,
    }


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def make_note(result):
    positive = result["positive"]
    lines = [
        "# Exploration source identity/runtime contract check - short QA note",
        "",
        f"- Run tag: `{result['runTag']}`",
        f"- Actor argument: `{result['actor']}`",
        f"- Manifest: `{display_path(result['manifest']['path'], result['repoRoot'])}`",
        f"- Manifest SHA-256 (raw): `{result['manifest']['sha256']}`",
        f"- Repository root: `{result['repoRoot']}`",
        f"- Wrapper: `{display_path(result['checker']['path'], result['repoRoot'])}`",
        f"- Wrapper SHA-256 (raw): `{result['checker']['sha256']}`",
        f"- Python: `{result['python']['executable']}` ({result['python']['version']})",
        "",
        "## Actual checks",
        "",
        f"- Positive: **{positive['passed']}**; checks={positive['checkCount']}; failed={positive['failedCount']}.",
        f"- Runtime set: `{positive.get('runtime', {}).get('setId')}`; actor=`{positive.get('runtime', {}).get('actor')}`.",
        f"- Source counts: `{json.dumps(positive.get('source', {}).get('counts'), sort_keys=True)}`.",
        f"- SOUTH exact source: `{positive.get('source', {}).get('south', {}).get('exactSource')}`.",
        "",
        "| Negative case | Expected | Refused | Expected failure observed | Unexpected failures | Passed |",
        "|---|---|---:|---|---:|---|",
    ]
    for case in result["negatives"]:
        lines.append(
            f"| {case['case']} | {case['expected']} | {not case.get('checkPassed', False)} | "
            f"{', '.join(case.get('expectedFailureHits', [])) or 'none'} | "
            f"{len(case.get('unexpectedFailures', []))} | {case['passed']} |"
        )
    lines.extend([
        "",
        "## Safety guard",
        "",
        f"- Original references: {result['guard']['before']['fileCount']} "
        f"({result['guard']['before']['existingCount']} present, "
        f"{len(result['guard']['before']['missing'])} missing).",
        f"- Aggregate SHA-256 before: `{result['guard']['before']['aggregateSha256']}`",
        f"- Aggregate SHA-256 after: `{result['guard']['after']['aggregateSha256']}`",
        f"- Original files unchanged: **{result['guard']['unchanged']}**.",
        f"- Fixtures preserved under: `{display_path(result['runRoot'], result['repoRoot'])}/fixtures`.",
        "",
        "## Scope and limits",
        "",
        "- This is a source/package identity and hash contract check. It does not recompose PXO/ORA pixels; "
        "the existing tracked native-bank checker remains the pixel check.",
        "- No Godot gameplay, native game test, runtime integration, default adoption, ledger, Bible, "
        "operating registry, Git index/commit or account change was made by this wrapper.",
        "- Source portraits and source art remain CONCEPT/UNAPPROVED; this wrapper makes no art or approval claim.",
        "- Tests alone earn no production ledger points.",
        f"- Ji Cheng: **{'tested source contract only' if result['actor'] == 'ji-cheng' else 'NOT TESTED in this run'}**; "
        "a different actor result does not establish Ji Cheng.",
        f"- Overall result: **{result['summary']['passed']}**.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", required=True,
                        help="repo-relative (or absolute) exploration source manifest")
    parser.add_argument("--actor", required=True, help="expected source/runtime actor id; no built-in actor assertion")
    parser.add_argument("--out-dir", required=True, help="new or existing output directory for evidence")
    parser.add_argument("--repo-root", default=None, help="optional repository root; inferred from --manifest by default")
    args = parser.parse_args()

    manifest_path = resolve_manifest_arg(args.manifest)
    if not path_is_file(manifest_path):
        print("CHECK_ERROR manifest not found: " + str(manifest_path), file=sys.stderr)
        return 2
    repo_root = (
        Path(os.path.abspath(args.repo_root)) if args.repo_root else infer_repo_root(manifest_path)
    )
    if repo_root is None:
        repo_root = ROOT
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = Path.cwd() / out_dir
    try:
        ensure_dir(out_dir)
    except OSError as exc:
        print("CHECK_ERROR cannot create --out-dir: " + f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    started = datetime.now(timezone.utc)
    run_tag = started.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    run_root = out_dir / ("run-" + run_tag)
    ensure_dir(run_root)

    try:
        source = json.loads(read_bytes(manifest_path).decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print("CHECK_ERROR source manifest parse: " + f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    if not isinstance(source, dict):
        print("CHECK_ERROR source manifest is not an object", file=sys.stderr)
        return 2

    before = snapshot_guard(source, manifest_path, repo_root)
    positive = execute_check(
        manifest_path,
        args.actor,
        repo_root,
        run_root / "positive",
        run_tag,
        "positive-" + args.actor,
        write_result=True,
    )

    negatives = []
    for case_name, mutation in (
        ("wrong-registry-actor", mutate_registry_actor),
        ("changed-runtime-copied-png", mutate_runtime_png),
    ):
        try:
            negatives.append(run_negative_case(
                case_name, mutation, source, manifest_path, args.actor, repo_root, run_root, run_tag
            ))
        except Exception as exc:  # noqa: BLE001 - retain the harness failure as evidence
            negatives.append({
                "case": case_name,
                "expected": "refuse",
                "passed": False,
                "harnessError": f"{type(exc).__name__}: {exc}",
                "expectedFailureHits": [],
                "unexpectedFailures": [],
            })

    after = snapshot_guard(source, manifest_path, repo_root)
    changed = {
        key: {"before": before["files"].get(key), "after": after["files"].get(key)}
        for key in sorted(set(before["files"]) | set(after["files"]))
        if before["files"].get(key) != after["files"].get(key)
    }
    guard = {
        "before": before,
        "after": after,
        "changed": changed,
        "unchanged": (
            not changed
            and before["aggregateSha256"] == after["aggregateSha256"]
            and before["files"] == after["files"]
        ),
    }
    summary = {
        "passed": bool(
            positive["passed"]
            and all(case.get("passed") for case in negatives)
            and guard["unchanged"]
        ),
        "positivePassed": positive["passed"],
        "negativeCount": len(negatives),
        "negativesRefused": sum(1 for case in negatives if case.get("passed")),
        "originalsUnchanged": guard["unchanged"],
        "jiChengTested": args.actor == "ji-cheng",
        "artApproved": False,
        "ledgerPoints": 0,
    }
    result = {
        "project": PROJECT_SLUG,
        "subject": SUBJECT,
        "purpose": PURPOSE,
        "variant": VARIANT,
        "runTag": run_tag,
        "actor": args.actor,
        "manifest": {"path": str(manifest_path), "sha256": sha256_file(manifest_path)},
        "repoRoot": str(repo_root),
        "runRoot": str(run_root),
        "checker": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(__file__)},
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "nativeBankChecker": {
            "path": str(NATIVE_CHECKER),
            "exists": path_is_file(NATIVE_CHECKER),
            "sha256": sha256_file(NATIVE_CHECKER) if path_is_file(NATIVE_CHECKER) else None,
            "note": "separate pixel compositor; not invoked by this wrapper",
        },
        "positive": {
            "passed": positive["passed"],
            "checkCount": len(positive["checks"]),
            "failedCount": len(positive["failedChecks"]),
            "failedChecks": positive["failedChecks"],
            "checks": positive["checks"],
            "resultPath": positive.get("resultPath"),
            "source": positive.get("source"),
            "runtime": positive.get("runtime"),
            "registry": positive.get("registry"),
            "stop": positive.get("stop"),
        },
        "negatives": negatives,
        "guard": guard,
        "summary": summary,
        "scope": {
            "sourceContractOnly": True,
            "nativePixelComposite": False,
            "godot": False,
            "artApproved": False,
            "runtimeIntegrated": False,
            "defaultChanged": False,
            "ledgerBibleRegistryGitAccountChanged": False,
            "sourcePortraits": "CONCEPT only; no approval inferred",
            "jiChengNote": (
                "Ji Cheng source was tested only if --actor ji-cheng; this run: "
                + ("tested source contract only" if args.actor == "ji-cheng" else "NOT TESTED")
            ),
        },
        "startedUtc": started.isoformat(),
        "finishedUtc": datetime.now(timezone.utc).isoformat(),
    }
    result_path = run_root / (
        f"{PROJECT_SLUG}_{SUBJECT}_identity-runtime-contract-check_{VARIANT}_{run_tag}.json"
    )
    note_path = run_root / (
        f"{PROJECT_SLUG}_{SUBJECT}_identity-runtime-contract-check_qa-note_{VARIANT}_{run_tag}.md"
    )
    write_text(result_path, json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    write_text(note_path, make_note(result) + "\n")

    print(
        "IDENTITY_RUNTIME",
        summary["passed"],
        "positive=" + str(positive["passed"]),
        "negatives=" + str(summary["negativesRefused"]) + "/" + str(summary["negativeCount"]),
        "guard_unchanged=" + str(guard["unchanged"]),
        "actor=" + args.actor,
        display_path(result_path, repo_root),
    )
    for name in positive["failedChecks"]:
        print("POSITIVE_FAIL", name)
    for case in negatives:
        print(
            "CASE",
            case.get("case"),
            "passed=" + str(case.get("passed")),
            "expected_hits=" + str(case.get("expectedFailureHits")),
            "unexpected=" + str(case.get("unexpectedFailures")),
        )
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
