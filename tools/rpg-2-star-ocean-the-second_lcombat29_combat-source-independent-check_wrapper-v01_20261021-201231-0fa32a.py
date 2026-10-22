#!/usr/bin/env python3
"""Independent combat-source check for Worlds Between production set manifests.

One concise wrapper, no second validation framework:
  * runs the existing runtime-spritesheet validator on the member manifest;
  * binds the exact member-only runtime index entry to that manifest;
  * checks all eight actions and their source pose/ticks/loop mapping;
  * runs the existing PXO/ORA composition reader for source PNG hashes,
    native-layer exports and source-cell-to-runtime-atlas equality.

Reads a SOURCE author manifest (the one with member_id, runtimeActions, poses
and files). Writes only --out, its two companion reports, and temporary
self-test fixtures under --out's directory. Never imports or edits gameplay.

CLI:
  python -X utf8 -I <this-file> --manifest SOURCE.json --out REPORT.json
  python -X utf8 -I <this-file> --manifest SOURCE.json --out REPORT.json --self-test

--self-test adds the positive control and two adversarial mutations (extra index
member; source/action drift that the runtime validator alone accepts).
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # importing the existing readers must not create __pycache__

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path

TOOL = "worlds-between-lcombat29-combat-source-independent-check"
SET_SCHEMA = "worlds-between.combat-sprite-set/1"
INDEX_SCHEMA = "worlds-between.combat-sprite-set-index/1"
ACTIONS = ["attack", "defeat", "dodge", "guard", "hit", "idle", "move", "skill"]
LIMITATIONS = [
    "Static source/export/index validation only; no Godot import/load, playback, motion, art quality, default adoption, save or creator approval is claimed.",
    "Native PXO/ORA composition and source-to-atlas checks are delegated to the existing composition reader; GUI save/reopen is not established.",
    "All hashes bind raw file bytes with no newline normalization; text/JSON normalization is not applied.",
    "The existing composition reader resolves files[*].path from the repository root, so the source manifest and its referenced files must stay inside that root (absolute paths are also accepted by the reader).",
    "Index path resolution mirrors the loader's base-directory join; res:// is mapped to the repository root only for inspection.",
    "Self-test mutations are temporary generated fixtures derived from the target source manifest, not production art or approval evidence.",
]

_MODULES: dict[tuple[str, str], object] = {}


def lp(path: Path) -> Path:
    """Extended-length path for Windows file I/O."""
    path = path.resolve()
    return Path("\\\\?\\" + str(path)) if os.name == "nt" else path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_exists(path: Path | None) -> bool:
    """Existence test through the extended-length Windows path."""
    return path is not None and lp(path).is_file()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with lp(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_bytes(path: Path) -> bytes:
    return lp(path).read_bytes()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lp(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict:
    data = json.loads(read_bytes(path).decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("top-level JSON is not an object")
    return data


def load_module(path: Path, name: str):
    key = (str(path.resolve()), name)
    if key not in _MODULES:
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load module {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _MODULES[key] = module
    return _MODULES[key]


def first_existing(root: Path, patterns: list[str]) -> Path | None:
    for pattern in patterns:
        found = sorted((root / "tools").glob(pattern))
        if found:
            return found[0]
    return None


class Checks:
    def __init__(self) -> None:
        self.items: list[dict] = []
        self.failed: list[str] = []

    def add(self, check_id: str, ok: bool, detail: str) -> bool:
        self.items.append({"id": check_id, "ok": bool(ok), "detail": detail})
        if not ok:
            self.failed.append(f"{check_id}: {detail}")
        return bool(ok)

    def fail(self, check_id: str, detail: str) -> None:
        self.add(check_id, False, detail)


def source_identity(source: dict) -> tuple[str | None, str | None]:
    member = source.get("member_id")
    appearance = source.get("appearance")
    character = source.get("character")
    if isinstance(character, dict):
        member = member if isinstance(member, str) and member else character.get("member_id")
        appearance = appearance if isinstance(appearance, str) and appearance else character.get("appearance")
    return (member if isinstance(member, str) and member else None,
            appearance if isinstance(appearance, str) and appearance else None)


def expected_key(member: str, appearance: str | None) -> str:
    return f"hero:{appearance}" if member == "hero" and appearance else member


def resolve_entry(entry: object, root: Path) -> Path | None:
    if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not entry["path"]:
        return None
    candidate = Path(entry["path"])
    return candidate if candidate.is_absolute() else root / candidate


def resolve_index_value(index_path: Path, value: str, root: Path) -> Path | None:
    if value.startswith("res://"):
        return root / value[len("res://"):]
    if "://" in value:
        return None
    candidate = Path(value)
    return candidate if candidate.is_absolute() else index_path.parent / candidate


def resolve_sheet(manifest_path: Path, sheet: str, root: Path) -> Path | None:
    if sheet.startswith("res://"):
        return root / sheet[len("res://"):]
    candidate = Path(sheet)
    return candidate if candidate.is_absolute() else manifest_path.parent / candidate


def same_path(left: Path | None, right: Path | None) -> bool:
    if left is None or right is None:
        return False
    return os.path.normcase(str(left.resolve())) == os.path.normcase(str(right.resolve()))


def run_existing_validator(validator_path: Path, manifest_path: Path, report_path: Path):
    module = load_module(validator_path, "wb_existing_runtime_validator")
    return module.validate(manifest_path, report_path)


def run_existing_reader(reader_path: Path, source_path: Path, report_path: Path, root: Path):
    module = load_module(reader_path, "wb_existing_native_reader")
    saved = sys.argv
    sys.argv = [
        str(reader_path),
        "--manifest", str(source_path.resolve()),
        "--out", str(report_path.resolve()),
    ]
    try:
        code = module.main()
    finally:
        sys.argv = saved
    report = read_json(report_path)
    return code, report


def check_actions(source: dict, target: dict, validator_result: dict, checks: Checks) -> dict:
    src_actions = source.get("runtimeActions")
    rt_actions = target.get("actions")
    checks.add("actions.all_eight", isinstance(rt_actions, dict) and sorted(rt_actions) == ACTIONS,
               f"runtime action keys={sorted(rt_actions) if isinstance(rt_actions, dict) else rt_actions!r}")
    checks.add("actions.source_all_eight", isinstance(src_actions, dict) and sorted(src_actions) == ACTIONS,
               f"source action keys={sorted(src_actions) if isinstance(src_actions, dict) else src_actions!r}")
    if not isinstance(src_actions, dict) or not isinstance(rt_actions, dict):
        return {"ok": False, "detail": "action objects missing"}

    source_rate = source.get("tickRate")
    rt_rates = {name: entry.get("tick_rate") for name, entry in rt_actions.items() if isinstance(entry, dict)}
    checks.add("actions.tick_rate", type(source_rate) is int and source_rate > 0
               and all(rate == source_rate for rate in rt_rates.values()),
               f"source tickRate={source_rate!r}; runtime rates={rt_rates!r}")

    poses = source.get("poses") if isinstance(source.get("poses"), dict) else {}
    cell_count = validator_result.get("sheet", {}).get("cell_count")
    expected_cells: list[int] = []
    pose_cells: dict[str, int] = {}
    summary: dict = {}
    all_match = True
    for name in ACTIONS:
        src = src_actions.get(name)
        rt = rt_actions.get(name)
        detail: list[str] = []
        if not isinstance(src, dict) or not isinstance(rt, dict):
            checks.add(f"actions.{name}.source_match", False, "source/runtime action missing or not an object")
            all_match = False
            continue
        if src.get("loop") is not rt.get("loop"):
            detail.append(f"loop source={src.get('loop')!r} runtime={rt.get('loop')!r}")
        if rt.get("tick_rate") != source_rate:
            detail.append(f"tick_rate runtime={rt.get('tick_rate')!r} source={source_rate!r}")
        src_frames = src.get("frames")
        rt_frames = rt.get("frames")
        if not isinstance(src_frames, list) or not isinstance(rt_frames, list):
            detail.append("frames must be arrays")
            src_frames = src_frames if isinstance(src_frames, list) else []
            rt_frames = rt_frames if isinstance(rt_frames, list) else []
        if len(src_frames) != len(rt_frames):
            detail.append(f"frame count source={len(src_frames)} runtime={len(rt_frames)}")
        total = 0
        for index, src_frame in enumerate(src_frames):
            if not isinstance(src_frame, list) or len(src_frame) != 2:
                detail.append(f"source frame[{index}] is not [pose,ticks]")
                continue
            pose, ticks = src_frame[0], src_frame[1]
            pose_entry = poses.get(pose) if isinstance(poses, dict) else None
            cell = pose_entry.get("runtimeCell") if isinstance(pose_entry, dict) else None
            if type(ticks) is not int or ticks <= 0:
                detail.append(f"source frame[{index}] ticks invalid: {ticks!r}")
            else:
                total += ticks
            if type(cell) is not int or cell < 0:
                detail.append(f"source pose {pose!r} has invalid runtimeCell={cell!r}")
                continue
            expected_cells.append(cell)
            pose_cells[str(pose)] = cell
            if cell_count is not None and cell >= cell_count:
                detail.append(f"source pose {pose!r} cell {cell} outside runtime cell_count {cell_count}")
            if index >= len(rt_frames) or not isinstance(rt_frames[index], dict):
                detail.append(f"runtime frame[{index}] missing")
                continue
            rt_frame = rt_frames[index]
            if rt_frame.get("cell") != cell:
                detail.append(f"frame[{index}] cell runtime={rt_frame.get('cell')!r} source pose {pose!r}={cell}")
            if rt_frame.get("ticks") != ticks:
                detail.append(f"frame[{index}] ticks runtime={rt_frame.get('ticks')!r} source={ticks!r}")
        if "totalTicks" in src and src.get("totalTicks") != total:
            detail.append(f"source totalTicks={src.get('totalTicks')!r} frame sum={total}")
        ok = not detail
        all_match = all_match and ok
        checks.add(f"actions.{name}.source_match", ok, "; ".join(detail) if detail else "loop/ticks/cells match source")
        summary[name] = {"frame_count": len(src_frames), "total_ticks": total, "ok": ok}

    cell_owners: dict[int, str] = {}
    collisions: list[str] = []
    for pose, cell in pose_cells.items():
        if cell in cell_owners and cell_owners[cell] != pose:
            collisions.append(f"cell {cell}: {cell_owners[cell]!r} and {pose!r}")
        cell_owners.setdefault(cell, pose)
    checks.add("actions.source_cells_unique", not collisions,
               "; ".join(collisions) if collisions else f"{len(pose_cells)} distinct poses map to {len(cell_owners)} distinct cells")
    checks.add("actions.cells_in_bounds", cell_count is not None and all(cell < cell_count for cell in expected_cells),
               f"cell_count={cell_count!r}; referenced cells={expected_cells}")
    return {"ok": all_match, "actions": summary}


def check_index(source: dict, source_path: Path, root: Path, checks: Checks) -> dict:
    files = source.get("files") if isinstance(source.get("files"), dict) else {}
    member, appearance = source_identity(source)
    if member is None:
        checks.fail("source.member", "source manifest has no non-empty member_id")
        member = ""
    if member == "hero" and not appearance:
        pkg_entry = files.get("pkg.manifest") if isinstance(files, dict) else None
        pkg_path = resolve_entry(pkg_entry, root)
        if file_exists(pkg_path):
            try:
                appearance = read_json(pkg_path).get("character", {}).get("appearance")
            except Exception:
                appearance = None
    key = expected_key(member, appearance)
    index_entry = files.get("pkg.index") if isinstance(files, dict) else None
    if not isinstance(index_entry, dict):
        index_entry = files.get("index") if isinstance(files, dict) else None
    index_path = resolve_entry(index_entry, root)
    checks.add("index.entry", index_path is not None,
               f"files.pkg.index path={index_entry!r}" if index_entry else "files has no pkg.index entry")
    if index_path is None:
        return {"key": key, "path": None, "entry": index_entry}
    checks.add("index.file_exists", file_exists(index_path), str(index_path))
    if not file_exists(index_path):
        return {"key": key, "path": index_path, "entry": index_entry}
    actual = sha256_file(index_path)
    declared = index_entry.get("sha256")
    checks.add("index.sha256_matches", declared == actual, f"declared={declared!r} actual={actual}")
    try:
        index = read_json(index_path)
    except Exception as exc:
        checks.fail("index.json", str(exc))
        return {"key": key, "path": index_path, "entry": index_entry, "sha256": actual}
    checks.add("index.schema", index.get("schema") == INDEX_SCHEMA,
               f"expected {INDEX_SCHEMA!r}; got {index.get('schema')!r}")
    sets = index.get("sets")
    checks.add("index.sets_object", isinstance(sets, dict), f"sets must be an object; got {type(sets).__name__}")
    if not isinstance(sets, dict):
        return {"key": key, "path": index_path, "entry": index_entry, "sha256": actual}
    checks.add("index.member_only", len(sets) == 1 and key in sets,
               f"expected exactly {{{key!r}}}; got {sorted(sets)}")
    checks.add("index.member_key", key in sets, f"expected key {key!r}; keys={sorted(sets)}")
    value = sets.get(key)
    if not isinstance(value, str) or not value:
        checks.fail("index.value", f"sets[{key!r}] must be a non-empty string; got {value!r}")
        value = next((item for item in sets.values() if isinstance(item, str) and item), "")
    target = resolve_index_value(index_path, value, root) if value else None
    checks.add("index.target_value", target is not None,
               f"resolved target={target}" if target is not None else f"unresolvable index value {value!r}")
    if target is not None:
        checks.add("index.target_exists", file_exists(target), str(target))
    return {"key": key, "path": index_path, "sha256": actual, "sets": sets, "target": target, "value": value}


def evaluate(source_path: Path, out_path: Path, root: Path, validator_path: Path,
             reader_path: Path) -> tuple[int, dict]:
    checks = Checks()
    result: dict = {
        "tool": TOOL,
        "tool_path": str(Path(__file__).resolve()),
        "tool_sha256": sha256_file(Path(__file__).resolve()),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "production",
        "scope": "independent combat source/index/export check; not art, motion, default or creator approval",
        "command": {"argv": sys.argv, "cwd": str(Path.cwd())},
        "source": {"path": str(source_path.resolve())},
        "index": {},
        "runtime_manifest": {},
        "sheet": {},
        "validator": {},
        "native_reader": {},
        "checks": checks.items,
        "failed_predicates": checks.failed,
    }
    if not file_exists(source_path):
        checks.fail("source.readable", f"missing source manifest: {source_path}")
        return finish(checks, result, out_path, None)
    raw = read_bytes(source_path)
    result["source"].update({"sha256": sha256_bytes(raw), "bytes": len(raw)})
    checks.add("source.readable", True, f"read {len(raw)} bytes; sha256={result['source']['sha256']}")
    try:
        source = json.loads(raw.decode("utf-8"))
        if not isinstance(source, dict):
            raise ValueError("top-level JSON is not an object")
    except Exception as exc:
        checks.fail("source.json", f"UTF-8 JSON parse failed: {exc}")
        return finish(checks, result, out_path, None)
    member, appearance = source_identity(source)
    result["source"]["member_id"] = member
    result["source"]["appearance"] = appearance
    checks.add("source.member", isinstance(member, str) and bool(member), f"member_id={member!r}")
    files = source.get("files")
    checks.add("source.files_object", isinstance(files, dict), f"files must be an object; got {type(files).__name__}")
    files = files if isinstance(files, dict) else {}
    result["source"]["file_entries"] = len(files)

    # Exact member-only index binding.
    index_info = check_index(source, source_path, root, checks)
    result["index"] = {
        "path": str(index_info.get("path")) if index_info.get("path") else None,
        "sha256": index_info.get("sha256"),
        "declared_sha256": index_info.get("entry", {}).get("sha256") if isinstance(index_info.get("entry"), dict) else None,
        "expected_key": index_info.get("key"),
        "keys": sorted(index_info.get("sets", {})) if isinstance(index_info.get("sets"), dict) else None,
        "target": str(index_info.get("target")) if index_info.get("target") else None,
    }

    pkg_manifest_entry = files.get("pkg.manifest") if isinstance(files, dict) else None
    pkg_manifest_path = resolve_entry(pkg_manifest_entry, root)
    target_path = index_info.get("target") if isinstance(index_info.get("target"), Path) else pkg_manifest_path
    if target_path is None or not file_exists(target_path):
        checks.fail("runtime_manifest.readable", f"missing target manifest: {target_path}")
        return finish(checks, result, out_path, None)
    if pkg_manifest_path is not None and index_info.get("target") is not None:
        checks.add("index.target_matches_pkg_manifest", same_path(target_path, pkg_manifest_path),
                   f"index target={target_path}; files.pkg.manifest={pkg_manifest_path}")

    target_raw = read_bytes(target_path)
    target_sha = sha256_bytes(target_raw)
    declared_target = pkg_manifest_entry.get("sha256") if isinstance(pkg_manifest_entry, dict) else None
    result["runtime_manifest"] = {
        "path": str(target_path.resolve()),
        "sha256": target_sha,
        "declared_sha256": declared_target,
        "bytes": len(target_raw),
    }
    checks.add("runtime_manifest.readable", True, f"read {len(target_raw)} bytes; sha256={target_sha}")
    checks.add("runtime_manifest.sha256_matches", declared_target == target_sha,
               f"files.pkg.manifest.sha256={declared_target!r}; actual={target_sha}")
    copy_entry = files.get("manifest") if isinstance(files, dict) else None
    if isinstance(copy_entry, dict):
        checks.add("runtime_manifest.copy_matches", copy_entry.get("sha256") == target_sha,
                   f"files.manifest.sha256={copy_entry.get('sha256')!r}; actual={target_sha}")
    try:
        target = json.loads(target_raw.decode("utf-8"))
        if not isinstance(target, dict):
            raise ValueError("top-level JSON is not an object")
    except Exception as exc:
        checks.fail("runtime_manifest.json", f"UTF-8 JSON parse failed: {exc}")
        return finish(checks, result, out_path, None)
    runtime_member = target.get("character", {}).get("member_id") if isinstance(target.get("character"), dict) else None
    result["runtime_manifest"]["member_id"] = runtime_member
    result["runtime_manifest"]["actions"] = sorted(target.get("actions", {})) if isinstance(target.get("actions"), dict) else None
    checks.add("runtime_manifest.member_matches_source", runtime_member == member,
               f"runtime member={runtime_member!r}; source member={member!r}")
    provenance = target.get("source_provenance")
    if isinstance(provenance, str) and provenance:
        checks.add("runtime_manifest.source_provenance", Path(provenance).name == source_path.name,
                   f"runtime source_provenance={provenance!r}; source basename={source_path.name!r}")
    else:
        checks.add("runtime_manifest.source_provenance", True, "source_provenance absent; no link invented")

    # Source sheet bytes bind to the production sheet actually loaded by the member manifest.
    pkg_sheet_entry = files.get("pkg.sheet") if isinstance(files, dict) else None
    pkg_sheet_path = resolve_entry(pkg_sheet_entry, root)
    target_sheet = target.get("sheet") if isinstance(target.get("sheet"), str) else None
    target_sheet_path = resolve_sheet(target_path, target_sheet, root) if target_sheet else None
    sheet_actual = None
    if target_sheet_path is None:
        checks.fail("sheet.declared", "runtime manifest has no sheet path")
    else:
        checks.add("sheet.file_exists", file_exists(target_sheet_path), str(target_sheet_path))
        if file_exists(target_sheet_path):
            sheet_actual = sha256_file(target_sheet_path)
            checks.add("sheet.sha256_matches_pkg", pkg_sheet_entry is not None
                       and pkg_sheet_entry.get("sha256") == sheet_actual,
                       f"files.pkg.sheet.sha256={pkg_sheet_entry.get('sha256') if isinstance(pkg_sheet_entry, dict) else None!r}; actual={sheet_actual}")
            source_sheet_entry = files.get("sheet") if isinstance(files, dict) else None
            if isinstance(source_sheet_entry, dict):
                source_sheet_path = resolve_entry(source_sheet_entry, root)
                checks.add("sheet.source_binding", file_exists(source_sheet_path)
                           and sha256_file(source_sheet_path) == sheet_actual,
                           f"files.sheet={source_sheet_entry.get('sha256')!r}; runtime sheet={sheet_actual}")
            declared_sheet = target.get("sheet_sha256")
            if declared_sheet is not None:
                checks.add("sheet.declared_sha256", declared_sheet == sheet_actual,
                           f"declared={declared_sheet!r}; actual={sheet_actual}")
    result["sheet"] = {
        "path": str(target_sheet_path) if target_sheet_path else None,
        "sha256": sheet_actual,
        "source_declared_sha256": pkg_sheet_entry.get("sha256") if isinstance(pkg_sheet_entry, dict) else None,
    }

    # Existing runtime validator: structural runtime predicate set.
    validator_report = out_path.with_name(out_path.stem + ".validator.json")
    val_code = None
    val_result: dict = {}
    try:
        val_code, val_result = run_existing_validator(validator_path, target_path, validator_report)
    except Exception:
        checks.add("validator.run", False, traceback.format_exc())
    else:
        val_ok = val_code == 0 and val_result.get("status") == "PASS"
        checks.add("validator.status", val_ok,
                   f"exit={val_code} status={val_result.get('status')!r} failed={len(val_result.get('failed_predicates', []))}")
        if val_result.get("manifest", {}).get("sha256") not in (None, target_sha):
            checks.add("validator.manifest_sha_matches", False,
                       f"validator read {val_result['manifest'].get('sha256')}; wrapper read {target_sha}")
    result["validator"] = {
        "path": str(validator_path.resolve()),
        "sha256": sha256_file(validator_path),
        "report": str(validator_report),
        "exit": val_code,
        "status": val_result.get("status"),
        "checks": val_result.get("summary", {}).get("checks"),
        "failed": len(val_result.get("failed_predicates", [])),
        "failed_predicates": val_result.get("failed_predicates", []),
        "manifest_sha256": val_result.get("manifest", {}).get("sha256"),
        "sheet_sha256": val_result.get("sheet", {}).get("actual_sha256"),
    }

    action_info = check_actions(source, target, val_result, checks)

    # Existing native reader: raw file hashes, PXO/ORA composition, atlas cell equality.
    reader_report = out_path.with_name(out_path.stem + ".native-reader.json")
    reader_code = None
    reader_result: dict = {}
    try:
        reader_code, reader_result = run_existing_reader(reader_path, source_path, reader_report, root)
    except Exception:
        checks.add("native_reader.run", False, traceback.format_exc())
    else:
        reader_checks = reader_result.get("checks") if isinstance(reader_result.get("checks"), list) else []
        hash_checks = [item for item in reader_checks if isinstance(item, dict)
                       and str(item.get("check", "")).startswith("raw hash ")]
        hash_failed = [item for item in hash_checks if not item.get("passed")]
        checks.add("native_reader.status", reader_code == 0 and reader_result.get("passed") is True,
                   f"exit={reader_code} passed={reader_result.get('passed')!r} checks={len(reader_checks)} failed={len(reader_checks) - sum(1 for c in reader_checks if c.get('passed'))}")
        checks.add("native_reader.hash_checks", bool(hash_checks) and not hash_failed,
                   f"{len(hash_checks)} raw-hash checks; failed={len(hash_failed)}")
        checks.add("native_reader.source_sha_matches", reader_result.get("manifestSha256Raw") == result["source"]["sha256"],
                   f"reader={reader_result.get('manifestSha256Raw')!r}; wrapper={result['source']['sha256']}")
    result["native_reader"] = {
        "path": str(reader_path.resolve()),
        "sha256": sha256_file(reader_path),
        "report": str(reader_report),
        "exit": reader_code,
        "passed": reader_result.get("passed"),
        "checks": len(reader_result.get("checks", [])) if isinstance(reader_result.get("checks"), list) else None,
        "failed": [item.get("check") for item in reader_result.get("checks", [])
                   if isinstance(item, dict) and not item.get("passed")] if isinstance(reader_result.get("checks"), list) else [],
        "manifest_sha256": reader_result.get("manifestSha256Raw"),
    }
    result["action_mapping"] = action_info
    return finish(checks, result, out_path, (val_result, reader_result))


def finish(checks: Checks, result: dict, out_path: Path | None, _raw: object) -> tuple[int, dict]:
    result["checks"] = checks.items
    result["failed_predicates"] = checks.failed
    result["summary"] = {
        "checks": len(checks.items),
        "failed": len(checks.failed),
        "validator": result.get("validator", {}).get("status"),
        "native_reader": result.get("native_reader", {}).get("passed"),
    }
    result["status"] = "PASS" if not checks.failed else "FAIL"
    result["hash_binding"] = {
        "algorithm": "sha256",
        "text_normalization": "none; raw bytes",
        "source_manifest_sha256": result.get("source", {}).get("sha256"),
        "runtime_manifest_sha256": result.get("runtime_manifest", {}).get("sha256"),
        "sheet_sha256": result.get("sheet", {}).get("sha256"),
        "tool_sha256": result.get("tool_sha256"),
    }
    result["limitations"] = LIMITATIONS
    code = 0 if not checks.failed else 1
    if out_path is not None:
        result["report_path"] = str(out_path)
        try:
            write_json(out_path, result)
        except OSError as exc:
            print(f"ERROR: cannot write {out_path}: {exc}", file=sys.stderr)
            return 2, result
    return code, result


# ---------------------------------------------------------------------------
# Self-test: derived from the target actor, never hardcoded to Zhao Ling.
# ---------------------------------------------------------------------------

def _copy_source_with_changes(source: dict, case_dir: Path,
                              changes: dict[str, Path], root: Path) -> Path:
    mutated = json.loads(json.dumps(source))
    files = mutated.get("files")
    if not isinstance(files, dict):
        raise RuntimeError("source manifest has no files object")
    for key, path in changes.items():
        if key not in files:
            files[key] = {}
        files[key]["path"] = os.path.relpath(path, root).replace("\\", "/")
        files[key]["sha256"] = sha256_file(path)
    target = case_dir / "src.json"
    write_json(target, mutated)
    return target


def _make_adv_cases(source: dict, source_path: Path, root: Path, work: Path) -> list[dict]:
    files = source["files"]
    key = expected_key(*source_identity(source))
    pkg_manifest = resolve_entry(files.get("pkg.manifest"), root)
    if pkg_manifest is None or not file_exists(pkg_manifest):
        raise RuntimeError("source manifest has no readable pkg.manifest")
    cases = []

    # A: an extra index member is structurally acceptable to the loader/validator.
    case_dir = work / "member-index-extra"
    case_dir.mkdir()
    runtime = read_json(pkg_manifest)
    runtime["source_provenance"] = "src.json"
    original_sheet = resolve_sheet(pkg_manifest, str(runtime.get("sheet", "")), root)
    if original_sheet is None or not file_exists(original_sheet):
        raise RuntimeError("cannot resolve the original runtime sheet for the member index case")
    runtime["sheet"] = str(original_sheet.resolve())
    member_runtime = case_dir / "runtime.json"
    write_json(member_runtime, runtime)
    extra_index = case_dir / "index-extra.json"
    write_json(extra_index, {"schema": INDEX_SCHEMA, "sets": {
        key: str(member_runtime.resolve()),
        "intruder": str(member_runtime.resolve()),
    }})
    extra_source = _copy_source_with_changes(source, case_dir, {
        "pkg.index": extra_index, "pkg.manifest": member_runtime, "manifest": member_runtime,
    }, root)
    cases.append({"name": "member_index_extra", "expected_failure": "index.member_only",
                  "expected_validator": "PASS", "source": extra_source, "dir": case_dir})

    # B: a valid runtime action whose cell no longer matches the source pose mapping.
    case_dir = work / "action-source-drift"
    case_dir.mkdir()
    runtime = read_json(pkg_manifest)
    skill = runtime.get("actions", {}).get("skill", {})
    frames = skill.get("frames") if isinstance(skill, dict) else None
    if not isinstance(frames, list) or not frames or not isinstance(frames[0], dict):
        raise RuntimeError("target runtime manifest has no skill frame 0 to mutate")
    cells = [frame.get("cell") for frame in frames if isinstance(frame, dict)]
    frames[0]["cell"] = (int(cells[0]) + 1) if type(cells[0]) is int else 1
    original_sheet = resolve_sheet(pkg_manifest, str(runtime.get("sheet", "")), root)
    if original_sheet is None or not file_exists(original_sheet):
        raise RuntimeError("cannot resolve the original runtime sheet for the action drift case")
    runtime["sheet"] = str(original_sheet.resolve())
    runtime["source_provenance"] = "src.json"
    drifted = case_dir / "runtime-action-drift.json"
    write_json(drifted, runtime)
    drift_index = case_dir / "index-drift.json"
    write_json(drift_index, {"schema": INDEX_SCHEMA, "sets": {
        key: str(drifted.resolve()),
    }})
    drift_source = _copy_source_with_changes(source, case_dir, {
        "pkg.index": drift_index, "pkg.manifest": drifted, "manifest": drifted,
    }, root)
    cases.append({"name": "action_source_drift", "expected_failure": "actions.skill.source_match",
                  "expected_validator": "PASS", "source": drift_source, "dir": case_dir})
    return cases


def run_self_test(source_path: Path, out_path: Path, root: Path,
                  validator_path: Path, reader_path: Path) -> tuple[int, dict]:
    work = out_path.parent / f"_lcombat29-selftest-{uuid.uuid4().hex[:8]}"
    work.mkdir(parents=True)
    report: dict = {
        "tool": TOOL,
        "mode": "self-test",
        "tool_sha256": sha256_file(Path(__file__).resolve()),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": {"path": str(source_path), "sha256": sha256_file(source_path)},
        "cases": [],
        "checks": [],
        "status": "FAIL",
    }
    failures: list[str] = []
    try:
        source = read_json(source_path)
        positive_path = work / "positive"
        positive_path.mkdir()
        code, positive = evaluate(source_path, positive_path / "report.json", root, validator_path, reader_path)
        report["cases"].append({
            "name": "positive_control", "expected_failure": None, "expected_validator": "PASS",
            "status": positive.get("status"), "exit": code,
            "failed_predicates": positive.get("failed_predicates", []),
            "validator": positive.get("validator", {}).get("status"),
            "native_reader": positive.get("native_reader", {}).get("passed"),
        })
        if code != 0 or positive.get("status") != "PASS":
            failures.append("positive_control did not pass")

        for case in _make_adv_cases(source, source_path, root, work):
            case_out = work / f"{case['name']}.json"
            code, result = evaluate(case["source"], case_out, root, validator_path, reader_path)
            failed = result.get("failed_predicates", [])
            matched = any(item.startswith(case["expected_failure"] + ":") for item in failed)
            validator_ok = result.get("validator", {}).get("status") == case["expected_validator"]
            reader_ok = result.get("native_reader", {}).get("passed") is True
            ok = code == 1 and result.get("status") == "FAIL" and matched and validator_ok and reader_ok
            if not ok:
                failures.append(f"{case['name']} did not isolate its expected gap")
            report["cases"].append({
                "name": case["name"], "expected_failure": case["expected_failure"],
                "expected_validator": case["expected_validator"],
                "status": result.get("status"), "exit": code, "failed_predicates": failed,
                "expected_failure_matched": matched,
                "validator": result.get("validator", {}).get("status"),
                "native_reader": result.get("native_reader", {}).get("passed"),
                "isolated": ok,
            })
    except Exception:
        failures.append(traceback.format_exc())
    finally:
        shutil.rmtree(work, ignore_errors=True)

    report["checks"] = [{"id": "selftest.positive", "ok": not any("positive_control" in item for item in failures)},
                        {"id": "selftest.adversarial", "ok": len(failures) == 0 or all("did not isolate" not in item for item in failures)},
                        {"id": "selftest.no_failures", "ok": not failures}]
    report["failed_predicates"] = failures
    report["status"] = "PASS" if not failures else "FAIL"
    report["summary"] = {"cases": len(report["cases"]), "failed": len(failures)}
    report["limitations"] = LIMITATIONS
    write_json(out_path, report)
    return (0 if not failures else 1), report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Independent index/action/source check for one production combat set.")
    parser.add_argument("--manifest", type=Path, help="source author manifest JSON (read only)")
    parser.add_argument("--out", type=Path, help="uniquely named JSON report")
    parser.add_argument("--root", type=Path, help="repository root (default: this tool's parent's parent)")
    parser.add_argument("--validator", type=Path, help="existing runtime-spritesheet validator")
    parser.add_argument("--reader", type=Path, help="existing PXO/ORA composition reader")
    parser.add_argument("--self-test", action="store_true", help="add positive + two adversarial cases derived from --manifest")
    args = parser.parse_args(argv)
    if args.manifest is None or args.out is None:
        parser.error("--manifest and --out are required")
    root = (args.root or Path(__file__).resolve().parents[1]).resolve()
    validator = (args.validator or first_existing(root, ["*combat-runtime-spritesheet_validator*.py"]) or Path(""))
    reader = (args.reader or first_existing(root, ["*combat-source_native-composition-check*.py"]) or Path(""))
    if not file_exists(validator):
        print(f"ERROR: runtime validator not found under {root / 'tools'}", file=sys.stderr)
        return 2
    if not file_exists(reader):
        print(f"ERROR: native composition reader not found under {root / 'tools'}", file=sys.stderr)
        return 2
    try:
        if args.self_test:
            code, _ = run_self_test(args.manifest, args.out, root, validator, reader)
        else:
            code, _ = evaluate(args.manifest, args.out, root, validator, reader)
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        return 2
    return code


if __name__ == "__main__":
    raise SystemExit(main())
