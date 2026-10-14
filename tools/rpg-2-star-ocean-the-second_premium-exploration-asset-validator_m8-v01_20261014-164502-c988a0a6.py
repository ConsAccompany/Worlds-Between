"""Read-only validator for proposed premium exploration frame manifests.

Checks one or more production manifests against the M8 asset intake checklist
(docs/character-visuals/..._asset-intake-checklist_m8-design_20261014-162946-c4e7a19d.md).
It reports automated metadata and pixel facts only. It never writes files, never
edits manifests or registries, and never sets any approval or review status.

Exit codes: 0 = every automated check passed, 1 = at least one failure,
2 = command-line usage error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath

from PIL import Image, ImageOps


TOOL_NAME = "premium-exploration-asset-validator"
SCHEMA_VERSION = 1
PROJECT_SLUG = "rpg-2-star-ocean-the-second"
DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = (
    "game/data/character-visuals/"
    "rpg-2-star-ocean-the-second_character-visual-registry_m8-v01_20261014-134810-2a5d1b3c.json"
)
ASSET_ROOT = PurePosixPath("game/assets")
DIRECTIONS = ("south", "west", "north", "east")
REQUIRED_ACTIONS = ("idle", "walk")
APPROVED_VISIBLE_HEIGHT_LOGICAL_PX = 48
WEST_AUTHORING = ("independent", "mirrored_east")
FEET = ("left", "right")

TOP_LEVEL_REQUIRED = (
    "schema_version", "project", "visual_id", "frame_counts",
    "master", "scale", "cell_size", "ground_pin", "frames",
)
FRAME_REQUIRED = (
    "visual_id", "action", "direction", "phase", "path", "sha256", "source_size",
    "alpha_bounds_inclusive", "alpha_threshold", "contact_points",
    "identity_reference", "stage",
)
# Scale and anchor are declared once per variant; a frame carrying its own is a failure.
FRAME_FORBIDDEN = (
    "scale", "cell_size", "ground_pin", "pin", "anchor", "offset", "pivot", "origin",
    "foot_anchor", "foot_anchor_source_pixels",
)
# Approval lives only in the registry via a user-written receipt, never in a manifest.
APPROVAL_KEYS = ("approval", "approved", "approval_status", "art_approval", "review_status")
APPROVAL_WORDING = re.compile(r"approv|accept|sign[-_ ]?off|验收|批准|通过", re.IGNORECASE)

KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SHA256 = re.compile(r"^(?:[0-9a-f]{64}|[0-9A-F]{64})$")
GENERATED_NAME = re.compile(
    r"^" + re.escape(PROJECT_SLUG) + r"_(?P<body>.+)_(?P<stamp>\d{8}-\d{6})-(?P<uid>[0-9a-f]{8})\.png$"
)
MANIFEST_NAME = re.compile(r"^" + re.escape(PROJECT_SLUG) + r"_.+_\d{8}-\d{6}-[0-9a-f]{8}\.json$")
ANY_ID_NAME = re.compile(r"_(\d{8}-\d{6})-([0-9a-f]{8})\.[A-Za-z0-9]+$")
SIDECAR_SUFFIXES = (".import", ".uid")
SCAN_SKIP_DIRS = {".git", "work", ".godot", "__pycache__", ".playwright-cli", "node_modules"}


class ManifestError(ValueError):
    pass


def _reject_constant(name: str) -> None:
    raise ManifestError(f"non-finite JSON number {name} is not allowed")


def _unique_pairs(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ManifestError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def load_json_strict(path: Path) -> object:
    text = path.read_text(encoding="utf-8")
    return json.loads(text, object_pairs_hook=_unique_pairs, parse_constant=_reject_constant)


def is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def is_number(value: object) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def int_pair(value: object) -> bool:
    return isinstance(value, list) and len(value) == 2 and all(is_int(v) for v in value)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_approval_keys(node: object, trail: str = "$") -> list:
    found = []
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(key, str) and key.lower() in APPROVAL_KEYS:
                found.append(f"{trail}.{key}")
            found.extend(find_approval_keys(value, f"{trail}.{key}"))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found.extend(find_approval_keys(value, f"{trail}[{index}]"))
    return found


class Report:
    def __init__(self, label: str) -> None:
        self.label = label
        self.failures: list = []
        self.warnings: list = []

    def fail(self, code: str, message: str, where: str | None = None) -> None:
        self.failures.append({"code": code, "message": message, **({"where": where} if where else {})})

    def warn(self, code: str, message: str, where: str | None = None) -> None:
        self.warnings.append({"code": code, "message": message, **({"where": where} if where else {})})


class Validator:
    def __init__(self, root: Path, registry_path: Path) -> None:
        self.root = root.resolve()
        self.asset_root = (self.root / Path(*ASSET_ROOT.parts)).resolve()
        self.registry_path = registry_path
        self._listdir_cache: dict = {}
        self._id_index: dict | None = None
        self.registry_entries: dict = {}
        self.registry_directions: list | None = None
        self.registry_error: str | None = None
        self._load_registry()

    # ---- registry -------------------------------------------------------

    def _load_registry(self) -> None:
        try:
            data = load_json_strict(self.registry_path)
        except FileNotFoundError:
            self.registry_error = f"registry not found: {self.registry_path}"
            return
        except (OSError, ValueError) as exc:
            self.registry_error = f"registry unreadable: {exc}"
            return
        entries = data.get("entries") if isinstance(data, dict) else None
        if not isinstance(entries, list):
            self.registry_error = "registry has no 'entries' list"
            return
        for entry in entries:
            if isinstance(entry, dict) and isinstance(entry.get("visual_id"), str):
                self.registry_entries[entry["visual_id"]] = entry
        order = data.get("direction_order")
        if isinstance(order, list):
            self.registry_directions = order

    # ---- paths ----------------------------------------------------------

    def _listdir(self, directory: Path) -> list:
        if directory not in self._listdir_cache:
            try:
                self._listdir_cache[directory] = os.listdir(directory)
            except OSError:
                self._listdir_cache[directory] = []
        return self._listdir_cache[directory]

    def _case_mismatch(self, relative: PurePosixPath) -> str | None:
        current = self.root
        for part in relative.parts:
            names = self._listdir(current)
            if part not in names:
                matches = [n for n in names if n.lower() == part.lower()]
                return matches[0] if matches else part
            current = current / part
        return None

    def check_repo_path(self, report: Report, value: object, where: str, *,
                        inside_assets: bool, required: bool = True) -> Path | None:
        """Validate a repository-relative path string; return the absolute path if usable."""
        if value is None and not required:
            return None
        if not isinstance(value, str) or not value:
            report.fail("path-malformed", f"path must be a non-empty string, got {value!r}", where)
            return None
        if "\\" in value:
            report.fail("path-malformed", f"path must use forward slashes: {value}", where)
            return None
        posix = PurePosixPath(value)
        if posix.is_absolute() or re.match(r"^[A-Za-z]:", value):
            report.fail("path-not-relative", f"path must be repository-relative: {value}", where)
            return None
        if any(part in ("..", ".") for part in posix.parts) or value.endswith("/"):
            report.fail("path-malformed", f"path must not contain '.' or '..' segments: {value}", where)
            return None
        if inside_assets and posix.parts[:2] != ASSET_ROOT.parts:
            report.fail("path-outside-assets", f"path is not inside game/assets/: {value}", where)
            return None
        absolute = self.root / Path(*posix.parts)
        if not absolute.is_file():
            report.fail("file-missing", f"file does not exist: {value}", where)
            return None
        resolved = absolute.resolve()
        boundary = self.asset_root if inside_assets else self.root
        if resolved != boundary and boundary not in resolved.parents:
            report.fail("path-escapes", f"path resolves outside {'game/assets' if inside_assets else 'the repository'}: {value}", where)
            return None
        mismatch = self._case_mismatch(posix)
        if mismatch is not None:
            report.fail("path-case-mismatch", f"path case differs from disk ({mismatch!r}): {value}", where)
            return None
        return absolute

    # ---- repository-wide unique IDs -------------------------------------

    def id_index(self) -> dict:
        if self._id_index is None:
            index: dict = {}
            for directory, subdirs, files in os.walk(self.root):
                subdirs[:] = [d for d in subdirs if d not in SCAN_SKIP_DIRS]
                for name in files:
                    stem = name
                    for suffix in SIDECAR_SUFFIXES:
                        if stem.endswith(suffix):
                            stem = stem[: -len(suffix)]
                    match = ANY_ID_NAME.search(stem)
                    if match:
                        rel = Path(os.path.relpath(os.path.join(directory, stem), self.root)).as_posix()
                        index.setdefault(match.group(2), set()).add(rel)
            self._id_index = index
        return self._id_index

    # ---- manifest -------------------------------------------------------

    def validate_manifest(self, manifest_path: Path) -> dict:
        report = Report(str(manifest_path))
        facts: dict = {}
        result = {"manifest": str(manifest_path), "visual_id": None, "facts": facts,
                  "failures": report.failures, "warnings": report.warnings}
        try:
            manifest = load_json_strict(manifest_path)
        except FileNotFoundError:
            report.fail("manifest-missing", f"manifest not found: {manifest_path}")
            return result
        except UnicodeDecodeError as exc:
            report.fail("manifest-malformed", f"manifest is not UTF-8: {exc}")
            return result
        except (OSError, ValueError) as exc:
            report.fail("manifest-malformed", f"manifest is not valid strict JSON: {exc}")
            return result
        if not isinstance(manifest, dict):
            report.fail("manifest-malformed", "manifest top level must be a JSON object")
            return result

        if not MANIFEST_NAME.match(manifest_path.name):
            report.warn("manifest-name", "manifest filename does not follow slug_purpose_timestamp-id naming")
        for trail in find_approval_keys(manifest):
            report.fail("approval-field", f"approval/review status is not allowed in a production manifest: {trail}")

        missing = [key for key in TOP_LEVEL_REQUIRED if key not in manifest]
        for key in missing:
            report.fail("missing-field", f"top-level field '{key}' is missing")

        if "schema_version" in manifest and manifest["schema_version"] != SCHEMA_VERSION:
            report.fail("schema-version", f"schema_version must be {SCHEMA_VERSION}, got {manifest['schema_version']!r}")
        if "project" in manifest and manifest["project"] != PROJECT_SLUG:
            report.fail("project", f"project must be {PROJECT_SLUG!r}, got {manifest['project']!r}")

        visual_id = manifest.get("visual_id")
        if "visual_id" in manifest:
            if not isinstance(visual_id, str) or not KEBAB.match(visual_id):
                report.fail("visual-id", f"visual_id must be lowercase kebab-case, got {visual_id!r}")
                visual_id = None
            else:
                result["visual_id"] = visual_id
                self._check_registry(report, visual_id, facts)

        frame_counts = self._check_frame_counts(report, manifest.get("frame_counts"), "frame_counts" in manifest)
        variant = self._check_variant(report, manifest)
        facts["variant"] = variant.get("facts")

        frames = manifest.get("frames")
        if "frames" in manifest and (not isinstance(frames, list) or not frames):
            report.fail("frames-malformed", "frames must be a non-empty list")
            frames = None
        if frame_counts is not None:
            facts["declared_frame_counts"] = frame_counts
            facts["declared_frame_total"] = sum(sum(d.values()) for d in frame_counts.values())
        if frames is None:
            return result
        facts["frame_entries"] = len(frames)

        frame_results = []
        seen_keys: dict = {}
        seen_paths: dict = {}
        by_hash: dict = {}
        images: dict = {}
        for index, frame in enumerate(frames):
            where = f"frames[{index}]"
            info = self._check_frame(report, frame, where, visual_id, frame_counts, variant)
            if info is None:
                continue
            frame_results.append(info["facts"])
            key = info["key"]
            if key is not None:
                if key in seen_keys:
                    report.fail("frame-duplicate", f"duplicate action/direction/phase {key} (also {seen_keys[key]})", where)
                else:
                    seen_keys[key] = where
                    if info.get("image") is not None:
                        images[key] = info["image"]
            path_value = frame.get("path")
            if isinstance(path_value, str):
                if path_value in seen_paths:
                    report.fail("path-duplicate", f"path listed twice: {path_value} (also {seen_paths[path_value]})", where)
                seen_paths.setdefault(path_value, where)
            if info.get("sha256"):
                by_hash.setdefault(info["sha256"], []).append(where)
        facts["frames"] = frame_results

        for digest, wheres in by_hash.items():
            if len(wheres) > 1:
                report.warn("identical-frames", f"frames share identical file content: {', '.join(wheres)}")

        if frame_counts is not None:
            self._check_counts_against_frames(report, frame_counts, seen_keys)
        self._summaries(report, facts, frame_counts, frame_results, images, variant, frames)
        return result

    def _check_registry(self, report: Report, visual_id: str, facts: dict) -> None:
        if self.registry_error:
            report.fail("registry", self.registry_error)
            return
        if visual_id not in self.registry_entries:
            report.fail("visual-id-unregistered", f"visual_id {visual_id!r} is not in the visual registry")
        if self.registry_directions is not None and list(self.registry_directions) != list(DIRECTIONS):
            report.fail("registry-directions", f"registry direction_order {self.registry_directions} differs from {list(DIRECTIONS)}")
        entry = self.registry_entries.get(visual_id)
        if entry:
            source = entry.get("source_portrait")
            facts["registry_source_portrait"] = source.get("path") if isinstance(source, dict) else None

    def _check_frame_counts(self, report: Report, counts: object, present: bool) -> dict | None:
        if not present:
            return None  # already reported as missing; no default is assumed
        if not isinstance(counts, dict) or not counts:
            report.fail("frame-counts-malformed", "frame_counts must be a non-empty object of action -> direction -> count")
            return None
        valid = True
        for action in REQUIRED_ACTIONS:
            if action not in counts:
                report.fail("frame-counts-action", f"frame_counts has no '{action}' action")
                valid = False
        for action, per_direction in counts.items():
            if not KEBAB.match(action):
                report.fail("frame-counts-action", f"action name must be lowercase kebab-case: {action!r}")
                valid = False
            if not isinstance(per_direction, dict):
                report.fail("frame-counts-malformed", f"frame_counts.{action} must be an object of direction -> count")
                valid = False
                continue
            for direction in DIRECTIONS:
                if direction not in per_direction:
                    report.fail("frame-counts-direction", f"frame_counts.{action} has no '{direction}'")
                    valid = False
            for direction, count in per_direction.items():
                if direction not in DIRECTIONS:
                    report.fail("frame-counts-direction", f"frame_counts.{action} has unknown direction {direction!r}")
                    valid = False
                elif not is_int(count) or count < 1:
                    report.fail("frame-counts-value", f"frame_counts.{action}.{direction} must be a positive integer, got {count!r}")
                    valid = False
        return counts if valid else None

    def _check_variant(self, report: Report, manifest: dict) -> dict:
        variant: dict = {"facts": {}}
        facts = variant["facts"]
        scale = manifest.get("scale")
        if "scale" in manifest:
            if not is_number(scale) or scale <= 0:
                report.fail("scale", f"scale must be a positive finite number, got {scale!r}")
            else:
                variant["scale"] = facts["scale"] = scale
        cell = manifest.get("cell_size")
        if "cell_size" in manifest:
            if not int_pair(cell) or cell[0] < 1 or cell[1] < 1:
                report.fail("cell-size", f"cell_size must be [width, height] positive integers, got {cell!r}")
            else:
                variant["cell"] = facts["cell_size"] = cell
        pin = manifest.get("ground_pin")
        if "ground_pin" in manifest:
            if not int_pair(pin):
                report.fail("ground-pin", f"ground_pin must be [x, y] integers, got {pin!r}")
            else:
                facts["ground_pin"] = pin
                if "cell" in variant and not (0 <= pin[0] < cell[0] and 0 <= pin[1] < cell[1]):
                    report.fail("ground-pin", f"ground_pin {pin} lies outside cell_size {cell}")
                else:
                    variant["pin"] = pin
        master = manifest.get("master")
        if "master" in manifest:
            if not isinstance(master, dict):
                report.fail("master", "master must be an object with 'path' and 'sha256'")
            else:
                for key in ("path", "sha256"):
                    if key not in master:
                        report.fail("master", f"master.{key} is missing")
                absolute = self.check_repo_path(report, master.get("path"), "master.path", inside_assets=True) if "path" in master else None
                master_facts = {"path": master.get("path")}
                if absolute is not None:
                    self._check_generated_name(report, absolute.name, "master.path")
                    self._check_unique_id(report, absolute, "master.path")
                    if "sha256" in master:
                        master_facts["sha256_matches"] = self._check_sha(report, master["sha256"], absolute, "master.sha256")
                    try:
                        with Image.open(absolute) as image:
                            master_facts.update(format=image.format, mode=image.mode, size=list(image.size))
                    except (OSError, ValueError, Image.DecompressionBombError) as exc:
                        report.fail("master-unreadable", f"master is not a readable image: {exc}", "master.path")
                facts["master"] = master_facts
        return variant

    def _check_sha(self, report: Report, declared: object, absolute: Path, where: str) -> bool | None:
        if not isinstance(declared, str) or not SHA256.match(declared):
            report.fail("sha256-malformed", f"sha256 must be 64 hex characters in a single case, got {declared!r}", where)
            return None
        actual = sha256_file(absolute)
        if actual != declared.lower():
            report.fail("sha256-mismatch", f"sha256 does not match file (file is {actual})", where)
            return False
        return True

    def _check_generated_name(self, report: Report, name: str, where: str) -> re.Match | None:
        match = GENERATED_NAME.match(name)
        if not match:
            report.fail("filename-format", f"filename does not match {PROJECT_SLUG}_<...>_<YYYYMMDD-HHMMSS>-<8 hex>.png: {name}", where)
            return None
        try:
            datetime.strptime(match.group("stamp"), "%Y%m%d-%H%M%S")
        except ValueError:
            report.fail("filename-timestamp", f"filename timestamp is not a valid date/time: {match.group('stamp')}", where)
            return None
        return match

    def _check_unique_id(self, report: Report, absolute: Path, where: str) -> None:
        match = ANY_ID_NAME.search(absolute.name)
        if not match:
            return
        rel = absolute.relative_to(self.root).as_posix()
        others = sorted(self.id_index().get(match.group(2), set()) - {rel})
        if others:
            report.fail("unique-id-collision", f"8-hex ID {match.group(2)} is also used by: {', '.join(others)}", where)

    def _check_frame_name(self, report: Report, name: str, where: str, visual_id: str | None,
                          action: str, direction: str, phase: int, count: int | None) -> None:
        match = self._check_generated_name(report, name, where)
        if match is None:
            return
        parts = match.group("body").split("_")
        if len(parts) != 3:
            report.fail("filename-format", f"filename must be slug_<visual-id>_<kind-action-direction[-phase-NN]>_<milestone>_<stamp>-<id>.png: {name}", where)
            return
        name_visual, descriptor, milestone = parts
        if visual_id is not None and name_visual != visual_id:
            report.fail("filename-visual-id", f"filename visual id {name_visual!r} differs from {visual_id!r}", where)
        if not KEBAB.match(milestone):
            report.fail("filename-format", f"milestone/version token must be kebab-case: {milestone!r}", where)
        phase_match = re.search(r"-phase-(\d{2,})$", descriptor)
        core = descriptor[: phase_match.start()] if phase_match else descriptor
        if phase_match:
            token = phase_match.group(1)
            expected = 1 if count == 1 else phase
            if token != f"{expected:02d}":
                report.fail("filename-phase", f"filename phase token phase-{token} does not match phase {phase}", where)
        elif count is not None and count > 1:
            report.fail("filename-phase", "multi-frame action filename needs a -phase-NN token", where)
        suffix = f"-{action}-{direction}"
        if not core.endswith(suffix) or not KEBAB.match(core[: -len(suffix)] or "-"):
            report.fail("filename-descriptor", f"descriptor {descriptor!r} must be <kind>-{action}-{direction}[-phase-NN]", where)

    def _check_frame(self, report: Report, frame: object, where: str, visual_id: str | None,
                     frame_counts: dict | None, variant: dict) -> dict | None:
        if not isinstance(frame, dict):
            report.fail("frame-malformed", "frame entry must be an object", where)
            return None
        facts: dict = {"where": where, "path": frame.get("path")}
        info: dict = {"facts": facts, "key": None}
        for key in FRAME_REQUIRED:
            if key not in frame:
                report.fail("frame-missing-field", f"frame field '{key}' is missing", where)
        for key in FRAME_FORBIDDEN:
            if key in frame:
                report.fail("frame-own-scale-or-anchor", f"frame must not carry its own '{key}'; use the variant-level value", where)

        if "visual_id" in frame and visual_id is not None and frame["visual_id"] != visual_id:
            report.fail("frame-visual-id", f"frame visual_id {frame['visual_id']!r} differs from manifest {visual_id!r}", where)

        action, direction, phase = frame.get("action"), frame.get("direction"), frame.get("phase")
        key_ok = True
        if not isinstance(action, str) or not KEBAB.match(action):
            report.fail("frame-action", f"action must be a kebab-case string, got {action!r}", where)
            key_ok = False
        if direction not in DIRECTIONS:
            report.fail("frame-direction", f"direction must be one of {list(DIRECTIONS)}, got {direction!r}", where)
            key_ok = False
        if not is_int(phase) or phase < 0:
            report.fail("frame-phase", f"phase must be a non-negative integer, got {phase!r}", where)
            key_ok = False
        count = None
        if key_ok:
            info["key"] = (action, direction, phase)
            facts.update(action=action, direction=direction, phase=phase)
            if frame_counts is not None:
                count = frame_counts.get(action, {}).get(direction)
                if count is None:
                    report.fail("frame-undeclared", f"{action}/{direction} is not declared in frame_counts", where)
                elif count == 1 and phase != 0:
                    report.fail("frame-phase", f"single-frame {action}/{direction} must use phase 0, got {phase}", where)
                elif count > 1 and not 1 <= phase <= count:
                    report.fail("frame-phase", f"phase {phase} outside 1..{count} declared for {action}/{direction}", where)

        stage = frame.get("stage")
        if "stage" in frame:
            if not isinstance(stage, str) or not stage.strip():
                report.fail("stage", f"stage must be a non-empty string, got {stage!r}", where)
            elif APPROVAL_WORDING.search(stage):
                report.fail("stage-approval", f"stage records production stage only, not approval: {stage!r}", where)

        west = frame.get("west_authoring")
        if direction == "west" and west not in WEST_AUTHORING:
            report.fail("west-authoring", f"west frames need west_authoring in {list(WEST_AUTHORING)}, got {west!r}", where)
        elif west is not None and west not in WEST_AUTHORING:
            report.fail("west-authoring", f"west_authoring must be one of {list(WEST_AUTHORING)}, got {west!r}", where)
        facts["west_authoring"] = west

        if "identity_reference" in frame:
            self.check_repo_path(report, frame["identity_reference"], f"{where}.identity_reference", inside_assets=False)
        if frame.get("review_receipt") is not None:
            self.check_repo_path(report, frame["review_receipt"], f"{where}.review_receipt", inside_assets=False)

        cell = variant.get("cell")
        self._check_contacts(report, frame.get("contact_points"), "contact_points" in frame, cell, where, facts)

        threshold = frame.get("alpha_threshold")
        if "alpha_threshold" in frame and (not is_int(threshold) or not 1 <= threshold <= 255):
            report.fail("alpha-threshold", f"alpha_threshold must be an integer 1..255, got {threshold!r}", where)
            threshold = None
        declared_bounds = frame.get("alpha_bounds_inclusive")
        if "alpha_bounds_inclusive" in frame and not (
                isinstance(declared_bounds, list) and len(declared_bounds) == 4 and all(is_int(v) for v in declared_bounds)):
            report.fail("alpha-bounds-malformed", f"alpha_bounds_inclusive must be [x0, y0, x1, y1] integers, got {declared_bounds!r}", where)
            declared_bounds = None
        source_size = frame.get("source_size")
        if "source_size" in frame and not int_pair(source_size):
            report.fail("source-size-malformed", f"source_size must be [width, height] integers, got {source_size!r}", where)
            source_size = None

        absolute = self.check_repo_path(report, frame.get("path"), f"{where}.path", inside_assets=True) if "path" in frame else None
        if absolute is None:
            return info
        if absolute.suffix != ".png":
            report.fail("not-png", "frame file extension must be lowercase .png", where)
        if key_ok:
            self._check_frame_name(report, absolute.name, where, visual_id, action, direction, phase, count)
        self._check_unique_id(report, absolute, where)
        if "sha256" in frame:
            matches = self._check_sha(report, frame["sha256"], absolute, f"{where}.sha256")
            facts["sha256_matches"] = matches
            if matches:
                info["sha256"] = frame["sha256"].lower()

        image = self._inspect_png(report, absolute, where, facts, threshold)
        if image is None:
            return info
        info["image"] = image
        size = list(image.size)
        if source_size is not None and source_size != size:
            report.fail("source-size-mismatch", f"source_size {source_size} differs from actual {size}", where)
        if cell is not None and size != cell:
            report.fail("cell-size-mismatch", f"frame size {size} differs from variant cell_size {cell}", where)
        actual_bounds = facts.get("alpha_bounds_inclusive")
        if declared_bounds is not None and threshold is not None and declared_bounds != actual_bounds:
            report.fail("alpha-bounds-mismatch", f"declared alpha_bounds_inclusive {declared_bounds} differs from measured {actual_bounds}", where)
        for point in facts.get("contact_points", []):
            x, y = point["point"]
            if 0 <= x < size[0] and 0 <= y < size[1]:
                point["alpha_at_point"] = image.getpixel((x, y))[3]
        return info

    def _check_contacts(self, report: Report, contacts: object, present: bool, cell: list | None,
                        where: str, facts: dict) -> None:
        if not present:
            return
        if not isinstance(contacts, list):
            report.fail("contact-points-malformed", "contact_points must be a list of {foot, point}", where)
            return
        recorded = []
        feet_seen = set()
        for index, contact in enumerate(contacts):
            sub = f"{where}.contact_points[{index}]"
            if not isinstance(contact, dict) or set(contact) != {"foot", "point"}:
                report.fail("contact-points-malformed", "each contact point must be exactly {\"foot\", \"point\"}", sub)
                continue
            foot, point = contact["foot"], contact["point"]
            if foot not in FEET:
                report.fail("contact-points-foot", f"foot must be one of {list(FEET)}, got {foot!r}", sub)
                continue
            if foot in feet_seen:
                report.fail("contact-points-foot", f"foot {foot!r} listed twice", sub)
                continue
            feet_seen.add(foot)
            if not int_pair(point):
                report.fail("contact-points-malformed", f"point must be [x, y] integers, got {point!r}", sub)
                continue
            if cell is not None and not (0 <= point[0] < cell[0] and 0 <= point[1] < cell[1]):
                report.fail("contact-points-outside-cell", f"contact point {point} lies outside cell_size {cell}", sub)
                continue
            recorded.append({"foot": foot, "point": point})
        facts["contact_points"] = recorded

    def _inspect_png(self, report: Report, absolute: Path, where: str, facts: dict,
                     threshold: int | None) -> Image.Image | None:
        with absolute.open("rb") as handle:
            if handle.read(8) != b"\x89PNG\r\n\x1a\n":
                report.fail("not-png", "file does not have a PNG signature", where)
                return None
        try:
            with Image.open(absolute) as image:
                image.load()
                frames = getattr(image, "n_frames", 1)
                fmt, mode = image.format, image.mode
                pixels = image.copy()
        except (OSError, ValueError, Image.DecompressionBombError) as exc:
            report.fail("png-unreadable", f"PNG could not be decoded: {exc}", where)
            return None
        facts.update(format=fmt, mode=mode, size=list(pixels.size))
        if fmt != "PNG":
            report.fail("not-png", f"decoded format is {fmt}, not PNG", where)
            return None
        if frames != 1:
            report.fail("png-multi-frame", f"PNG contains {frames} frames; each frame must be its own file", where)
            return None
        if mode != "RGBA":
            report.fail("png-not-rgba", f"PNG mode is {mode}; separate RGBA PNG files are required", where)
            return None

        width, height = pixels.size
        alpha = pixels.getchannel("A")
        corners = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
        corner_alpha = [alpha.getpixel(c) for c in corners]
        facts["corner_alpha"] = corner_alpha
        if any(corner_alpha):
            report.fail("corners-not-transparent", f"corner alpha values {corner_alpha} must all be 0", where)
        histogram = alpha.histogram()
        facts["opaque_pixels"] = histogram[255]
        facts["partial_alpha_pixels"] = sum(histogram[1:255])
        border = 0
        for x in range(width):
            border += (alpha.getpixel((x, 0)) > 0) + (height > 1 and alpha.getpixel((x, height - 1)) > 0)
        for y in range(1, height - 1):
            border += (alpha.getpixel((0, y)) > 0) + (width > 1 and alpha.getpixel((width - 1, y)) > 0)
        facts["border_nonzero_alpha_pixels"] = int(border)
        if threshold is not None:
            facts["alpha_threshold"] = threshold
            facts["low_alpha_pixels_below_threshold"] = sum(histogram[1:threshold])
            box = alpha.point(lambda a: 255 if a >= threshold else 0).getbbox()
            if box is None:
                facts["alpha_bounds_inclusive"] = None
                report.fail("frame-empty", f"no pixel reaches alpha_threshold {threshold}", where)
            else:
                facts["alpha_bounds_inclusive"] = [box[0], box[1], box[2] - 1, box[3] - 1]
                facts["alpha_bounds_height_texels"] = box[3] - box[1]
        return pixels

    def _check_counts_against_frames(self, report: Report, frame_counts: dict, seen: dict) -> None:
        for action, per_direction in frame_counts.items():
            for direction, count in per_direction.items():
                expected = [0] if count == 1 else list(range(1, count + 1))
                present = sorted(p for (a, d, p) in seen if a == action and d == direction)
                missing = [p for p in expected if p not in present]
                if missing:
                    report.fail("frame-count-mismatch",
                                f"{action}/{direction} declares {count} frame(s) but phases {missing} are missing (found {len(present)})")

    def _summaries(self, report: Report, facts: dict, frame_counts: dict | None, frame_results: list,
                   images: dict, variant: dict, frames: list) -> None:
        scale = variant.get("scale")
        summary: dict = {}
        for item in frame_results:
            if "action" not in item:
                continue
            bucket = summary.setdefault(item["action"], {}).setdefault(item["direction"], {
                "frames_found": 0, "alpha_bounds_height_texels": [], "contact_feet_by_phase": {}})
            bucket["frames_found"] += 1
            if "alpha_bounds_height_texels" in item:
                bucket["alpha_bounds_height_texels"].append(item["alpha_bounds_height_texels"])
            if "contact_points" in item:
                bucket["contact_feet_by_phase"][str(item["phase"])] = [c["foot"] for c in item["contact_points"]]
        for action, per_direction in summary.items():
            for direction, bucket in per_direction.items():
                heights = bucket["alpha_bounds_height_texels"]
                if heights:
                    bucket["alpha_bounds_height_range_texels"] = [min(heights), max(heights)]
                    if scale is not None:
                        bucket["visible_height_logical_px_range"] = [round(min(heights) * scale, 3), round(max(heights) * scale, 3)]
                bucket["contact_feet_by_phase"] = dict(sorted(bucket["contact_feet_by_phase"].items(), key=lambda kv: int(kv[0])))
        facts["per_action_direction"] = summary
        facts["visible_height_note"] = (
            f"Approved display height is {APPROVED_VISIBLE_HEIGHT_LOGICAL_PX} logical px; tolerance is undecided, "
            "so idle visible height (alpha bounds height x scale) is reported, not judged.")

        mirror: list = []
        for (action, direction, phase), west_image in images.items():
            if direction != "west":
                continue
            east_image = images.get((action, "east", phase))
            if east_image is None or east_image.size != west_image.size:
                continue
            identical = ImageOps.mirror(east_image).tobytes() == west_image.tobytes()
            declared = next((f.get("west_authoring") for f in frames if isinstance(f, dict)
                             and (f.get("action"), f.get("direction"), f.get("phase")) == (action, "west", phase)), None)
            mirror.append({"action": action, "phase": phase, "west_is_pixel_mirror_of_east": identical,
                           "west_authoring": declared})
            if identical and declared != "mirrored_east":
                report.warn("west-mirror-flag", f"west {action} phase {phase} is a pixel mirror of east but west_authoring is {declared!r}; needs explicit user acceptance")
            elif identical:
                report.warn("west-mirror-flag", f"west {action} phase {phase} is mirrored from east; needs explicit user acceptance")
            elif declared == "mirrored_east":
                report.warn("west-mirror-flag", f"west {action} phase {phase} declared mirrored_east but is not a pixel mirror of east")
        facts["west_mirror_comparison"] = sorted(mirror, key=lambda m: (m["action"], m["phase"]))

        portrait = facts.get("registry_source_portrait")
        refs = {f.get("identity_reference") for f in frames if isinstance(f, dict) and "identity_reference" in f}
        facts["identity_references"] = sorted(r for r in refs if isinstance(r, str))
        if portrait and refs and refs != {portrait}:
            report.warn("identity-reference", f"identity_reference differs from registry source portrait {portrait}")

    # ---- run ------------------------------------------------------------

    def run(self, manifest_paths: list) -> dict:
        results = [self.validate_manifest(path) for path in manifest_paths]
        cross: list = []
        by_visual: dict = {}
        by_name: dict = {}
        for result in results:
            if result["visual_id"]:
                by_visual.setdefault(result["visual_id"], []).append(result["manifest"])
            for frame in result["facts"].get("frames", []):
                if isinstance(frame.get("path"), str):
                    name = PurePosixPath(frame["path"]).name
                    by_name.setdefault(name, set()).add(frame["path"])
        for visual_id, manifests in by_visual.items():
            if len(manifests) > 1:
                cross.append({"code": "variant-declared-twice",
                              "message": f"visual_id {visual_id!r} is declared by more than one manifest: {manifests}"})
        for name, paths in by_name.items():
            if len(paths) > 1:
                cross.append({"code": "filename-duplicate",
                              "message": f"filename {name} is used by several paths: {sorted(paths)}"})
        for result in results:
            result["automated_checks_passed"] = not result["failures"]
        failures = sum(len(r["failures"]) for r in results) + len(cross)
        return {
            "tool": TOOL_NAME,
            "schema_version": SCHEMA_VERSION,
            "repo_root": str(self.root),
            "registry": str(self.registry_path),
            "notice": ("Automated metadata and pixel facts only. Passing does not mean the art is visually "
                       "acceptable. This tool does not approve art and changes no approval or review_status field."),
            "automated_checks_passed": failures == 0,
            "failure_count": failures,
            "warning_count": sum(len(r["warnings"]) for r in results),
            "cross_manifest_failures": cross,
            "manifests": results,
        }


def format_text(report: dict) -> str:
    lines = [f"{TOOL_NAME}: {'PASS' if report['automated_checks_passed'] else 'FAIL'} "
             f"({report['failure_count']} failure(s), {report['warning_count']} warning(s))",
             report["notice"]]
    for result in report["manifests"]:
        facts = result["facts"]
        lines.append("")
        lines.append(f"[{'PASS' if result['automated_checks_passed'] else 'FAIL'}] {result['manifest']}")
        lines.append(f"  visual_id: {result['visual_id']}")
        if "declared_frame_counts" in facts:
            lines.append(f"  declared frames: {facts['declared_frame_total']} {json.dumps(facts['declared_frame_counts'])}")
        if "frame_entries" in facts:
            lines.append(f"  frame entries: {facts['frame_entries']}")
        variant = facts.get("variant") or {}
        if variant:
            lines.append(f"  variant: scale={variant.get('scale')} cell_size={variant.get('cell_size')} ground_pin={variant.get('ground_pin')}")
        for action, per_direction in (facts.get("per_action_direction") or {}).items():
            for direction, bucket in per_direction.items():
                height = bucket.get("visible_height_logical_px_range")
                lines.append(f"  {action}/{direction}: {bucket['frames_found']} frame(s)"
                             + (f", visible height {height} logical px" if height else ""))
        for item in result["failures"]:
            lines.append(f"  FAIL {item['code']}: {item['message']}" + (f" [{item['where']}]" if "where" in item else ""))
        for item in result["warnings"]:
            lines.append(f"  WARN {item['code']}: {item['message']}" + (f" [{item['where']}]" if "where" in item else ""))
    for item in report["cross_manifest_failures"]:
        lines.append(f"FAIL {item['code']}: {item['message']}")
    return "\n".join(lines)


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("manifests", nargs="+", type=Path, help="proposed production manifest JSON file(s)")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_ROOT,
                        help="repository root that manifest paths are relative to (default: this repository)")
    parser.add_argument("--registry", type=Path, default=None,
                        help=f"visual registry JSON (default: <repo-root>/{DEFAULT_REGISTRY})")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="report format on stdout")
    args = parser.parse_args(argv)
    registry = args.registry if args.registry is not None else args.repo_root / DEFAULT_REGISTRY
    report = Validator(args.repo_root, registry).run(args.manifests)
    output = json.dumps(report, ensure_ascii=False, indent=2) if args.format == "json" else format_text(report)
    sys.stdout.buffer.write((output + "\n").encode("utf-8"))
    return 0 if report["automated_checks_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
