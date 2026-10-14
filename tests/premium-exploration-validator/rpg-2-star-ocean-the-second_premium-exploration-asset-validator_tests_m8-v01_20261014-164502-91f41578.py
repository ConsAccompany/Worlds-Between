"""Tests for the premium exploration asset validator.

Every PNG, manifest and registry used here is synthetic and lives in a temporary
directory outside the repository. Run with:

    python tests/premium-exploration-validator/<this file>
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageOps


REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "rpg-2-star-ocean-the-second_premium-exploration-asset-validator_m8-v01_20261014-164502-c988a0a6.py"
SLUG = "rpg-2-star-ocean-the-second"
REGISTRY_REL = ("game/data/character-visuals/"
                "rpg-2-star-ocean-the-second_character-visual-registry_m8-v01_20261014-134810-2a5d1b3c.json")
PORTRAIT_REL = "outputs/rpg-2-star-ocean-the-second_test-hero_character-sheet_v01_20261014-120000-aaaa0001.png"
FRAME_DIR = "game/assets/characters/premium-test"
STAMP = "20261014-120000"
DIRECTIONS = ("south", "west", "north", "east")

sys.dont_write_bytecode = True  # keep the repository untouched when importing the tool
spec = importlib.util.spec_from_file_location("premium_validator", TOOL)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def counts(idle: int, walk: int, **extra: int) -> dict:
    result = {"idle": {d: idle for d in DIRECTIONS}, "walk": {d: walk for d in DIRECTIONS}}
    for action, value in extra.items():
        result[action] = {d: value for d in DIRECTIONS}
    return result


def phases_for(count: int) -> list:
    return [0] if count == 1 else list(range(1, count + 1))


def measured_bounds(image: Image.Image, threshold: int) -> list:
    """Independent bounding-box measurement used to write the expected manifest values."""
    width, height = image.size
    alpha = image.getchannel("A").tobytes()
    xs = [i % width for i, a in enumerate(alpha) if a >= threshold]
    ys = [i // width for i, a in enumerate(alpha) if a >= threshold]
    return [min(xs), min(ys), max(xs), max(ys)]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SyntheticRepo:
    """A throwaway repository layout with a registry, a portrait and separate frame PNGs."""

    def __init__(self, base: Path) -> None:
        self.root = base / "repo"
        self.uid = 0
        (self.root / FRAME_DIR).mkdir(parents=True)
        registry = self.root / REGISTRY_REL
        registry.parent.mkdir(parents=True)
        registry.write_text(json.dumps({
            "schema_version": 1,
            "direction_order": list(DIRECTIONS),
            "entries": [
                {"visual_id": "test-hero", "source_portrait": {"path": PORTRAIT_REL}},
                {"visual_id": "test-rival", "source_portrait": {"path": PORTRAIT_REL}},
            ],
        }), encoding="utf-8")
        portrait = self.root / PORTRAIT_REL
        portrait.parent.mkdir(parents=True)
        Image.new("RGBA", (4, 4)).save(portrait)

    def next_uid(self) -> str:
        self.uid += 1
        return f"{0x10000000 + self.uid:08x}"

    def figure(self, cell: list, pin: list, height: int, tint: tuple, partial: bool = True) -> Image.Image:
        width = max(4, cell[0] // 3)
        image = Image.new("RGBA", tuple(cell), (0, 0, 0, 0))
        x0 = pin[0] - width // 2
        for y in range(pin[1] - height + 1, pin[1] + 1):
            for x in range(x0, x0 + width):
                image.putpixel((x, y), tint + (255,))
        image.putpixel((x0 + width, pin[1] - height + 2), (250, 250, 250, 255))  # asymmetric accessory
        if partial:
            image.putpixel((x0 - 2, pin[1]), tint + (40,))  # faint fringe below threshold 64
            image.putpixel((x0 - 1, pin[1] - 1), tint + (128,))
        return image

    def build(self, frame_counts: dict, cell=(16, 24), pin=(8, 22), scale=1.0, idle_height=18,
              visual_id="test-hero", mirror_west=False, threshold=64) -> dict:
        cell, pin = list(cell), list(pin)
        master_name = f"{SLUG}_{visual_id}_premium-idle-master_m8-test_{STAMP}-{self.next_uid()}.png"
        master_path = self.root / FRAME_DIR / master_name
        self.figure(cell, pin, idle_height, (90, 60, 30)).save(master_path)
        frames = []
        images = {}
        for a_index, (action, per_direction) in enumerate(frame_counts.items()):
            for d_index, direction in enumerate(DIRECTIONS):
                count = per_direction[direction]
                for phase in phases_for(count):
                    bob = 0 if action == "idle" else phase % 2
                    tint = ((phase * 23) % 256, 40 + 50 * d_index, 20 + 70 * a_index)
                    image = self.figure(cell, pin, idle_height - bob, tint)
                    if direction == "west" and mirror_west:
                        image = None  # filled from east below
                    images[(action, direction, phase)] = image
                    frames.append((action, direction, phase, count))
        if mirror_west:
            for (action, direction, phase), image in list(images.items()):
                if direction == "west":
                    images[(action, direction, phase)] = ImageOps.mirror(images[(action, "east", phase)])
        entries = []
        for action, direction, phase, count in frames:
            token = "" if count == 1 else f"-phase-{phase:02d}"
            name = f"{SLUG}_{visual_id}_premium-{action}-{direction}{token}_m8-test_{STAMP}-{self.next_uid()}.png"
            path = self.root / FRAME_DIR / name
            image = images[(action, direction, phase)]
            image.save(path)
            foot = "left" if phase % 2 else "right"
            contacts = ([{"foot": "left", "point": [pin[0] - 2, pin[1]]}, {"foot": "right", "point": [pin[0] + 1, pin[1]]}]
                        if action == "idle" else [{"foot": foot, "point": [pin[0], pin[1]]}])
            entry = {
                "visual_id": visual_id,
                "action": action,
                "direction": direction,
                "phase": phase,
                "path": f"{FRAME_DIR}/{name}",
                "sha256": sha(path).upper(),
                "source_size": cell,
                "alpha_bounds_inclusive": measured_bounds(image, threshold),
                "alpha_threshold": threshold,
                "contact_points": contacts,
                "identity_reference": PORTRAIT_REL,
                "stage": "generated-concept",
                "review_receipt": None,
            }
            if direction == "west":
                entry["west_authoring"] = "mirrored_east" if mirror_west else "independent"
            entries.append(entry)
        return {
            "schema_version": 1,
            "project": SLUG,
            "visual_id": visual_id,
            "frame_counts": frame_counts,
            "master": {"path": f"{FRAME_DIR}/{master_name}", "sha256": sha(master_path)},
            "scale": scale,
            "cell_size": cell,
            "ground_pin": pin,
            "frames": entries,
        }

    def write_manifest(self, manifest: object, name: str | None = None) -> Path:
        name = name or f"{SLUG}_test-hero_premium-exploration-manifest_m8-test_{STAMP}-{self.next_uid()}.json"
        path = self.root.parent / "manifests" / name
        path.parent.mkdir(exist_ok=True)
        text = manifest if isinstance(manifest, str) else json.dumps(manifest, indent=1)
        path.write_text(text, encoding="utf-8")
        return path

    def validate(self, *manifests: object) -> dict:
        paths = [m if isinstance(m, Path) else self.write_manifest(m) for m in manifests]
        return validator.Validator(self.root, self.root / REGISTRY_REL).run(paths)


def codes(report: dict) -> set:
    found = {f["code"] for r in report["manifests"] for f in r["failures"]}
    return found | {f["code"] for f in report["cross_manifest_failures"]}


def warning_codes(report: dict) -> set:
    return {w["code"] for r in report["manifests"] for w in r["warnings"]}


class ValidatorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="premium-validator-test-")
        base = Path(self._tmp.name).resolve()
        self.assertNotIn(REPO, [base, *base.parents], "synthetic files must live outside the repository")
        self.repo = SyntheticRepo(base)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def assertPasses(self, report: dict) -> None:
        self.assertEqual(codes(report), set(), json.dumps(report, indent=1)[:4000])
        self.assertTrue(report["automated_checks_passed"])

    def assertFailsWith(self, report: dict, code: str) -> None:
        self.assertFalse(report["automated_checks_passed"])
        self.assertIn(code, codes(report))


class DeclaredFrameCounts(ValidatorTestCase):
    def test_any_declared_frame_count_passes(self) -> None:
        uneven = counts(2, 6, run=3)
        uneven["walk"]["west"] = 5
        for frame_counts in (counts(1, 4), counts(4, 8), counts(3, 5), uneven, counts(1, 1)):
            with self.subTest(frame_counts=frame_counts):
                manifest = self.repo.build(frame_counts)
                report = self.repo.validate(manifest)
                self.assertPasses(report)
                expected = sum(sum(d.values()) for d in frame_counts.values())
                facts = report["manifests"][0]["facts"]
                self.assertEqual(facts["declared_frame_total"], expected)
                self.assertEqual(facts["frame_entries"], expected)

    def test_twenty_frame_set_against_forty_eight_declaration_fails(self) -> None:
        manifest = self.repo.build(counts(1, 4))
        manifest["frame_counts"] = counts(4, 8)
        self.assertFailsWith(self.repo.validate(manifest), "frame-count-mismatch")

    def test_missing_frame_counts_fails_without_default(self) -> None:
        manifest = self.repo.build(counts(1, 4))
        del manifest["frame_counts"]
        report = self.repo.validate(manifest)
        self.assertFailsWith(report, "missing-field")
        self.assertNotIn("declared_frame_counts", report["manifests"][0]["facts"])

    def test_frame_counts_shape_errors(self) -> None:
        cases = {
            "missing direction": lambda c: c["walk"].pop("north"),
            "extra direction": lambda c: c["walk"].__setitem__("northeast", 4),
            "missing walk": lambda c: c.pop("walk"),
            "zero": lambda c: c["idle"].__setitem__("south", 0),
            "bool": lambda c: c["idle"].__setitem__("south", True),
            "string": lambda c: c["idle"].__setitem__("south", "4"),
            "float": lambda c: c["idle"].__setitem__("south", 4.0),
        }
        expected = {"missing direction": "frame-counts-direction", "extra direction": "frame-counts-direction",
                    "missing walk": "frame-counts-action", "zero": "frame-counts-value",
                    "bool": "frame-counts-value", "string": "frame-counts-value", "float": "frame-counts-value"}
        base = self.repo.build(counts(1, 4))
        for label, mutate in cases.items():
            with self.subTest(label):
                manifest = copy.deepcopy(base)
                mutate(manifest["frame_counts"])
                self.assertFailsWith(self.repo.validate(manifest), expected[label])
        for bad in ([], {}, "20", None):
            with self.subTest(frame_counts=bad):
                manifest = copy.deepcopy(base)
                manifest["frame_counts"] = bad
                self.assertFailsWith(self.repo.validate(manifest), "frame-counts-malformed")

    def test_missing_extra_and_gapped_frames_fail(self) -> None:
        base = self.repo.build(counts(2, 4))
        missing = copy.deepcopy(base)
        missing["frames"] = [f for f in missing["frames"]
                             if (f["action"], f["direction"], f["phase"]) != ("walk", "north", 3)]
        self.assertFailsWith(self.repo.validate(missing), "frame-count-mismatch")

        extra = copy.deepcopy(base)
        extra["frame_counts"]["walk"]["east"] = 3
        report = self.repo.validate(extra)
        self.assertFailsWith(report, "frame-phase")

        gap = copy.deepcopy(base)
        target = next(f for f in gap["frames"] if (f["action"], f["direction"], f["phase"]) == ("walk", "south", 2))
        target["phase"] = 7
        report = self.repo.validate(gap)
        self.assertFailsWith(report, "frame-phase")
        self.assertIn("frame-count-mismatch", codes(report))

        duplicate = copy.deepcopy(base)
        duplicate["frames"].append(copy.deepcopy(duplicate["frames"][0]))
        self.assertFailsWith(self.repo.validate(duplicate), "frame-duplicate")

    def test_single_frame_action_uses_phase_zero(self) -> None:
        manifest = self.repo.build(counts(1, 4))
        idle = next(f for f in manifest["frames"] if f["action"] == "idle")
        idle["phase"] = 1
        self.assertFailsWith(self.repo.validate(manifest), "frame-phase")

    def test_undeclared_action_frame_fails(self) -> None:
        manifest = self.repo.build(counts(1, 4, run=2))
        del manifest["frame_counts"]["run"]
        self.assertFailsWith(self.repo.validate(manifest), "frame-undeclared")


class VariantLevelDeclarations(ValidatorTestCase):
    def test_each_variant_field_is_required(self) -> None:
        base = self.repo.build(counts(1, 4))
        for key in ("master", "scale", "cell_size", "ground_pin", "frames", "visual_id", "schema_version", "project"):
            with self.subTest(key=key):
                manifest = copy.deepcopy(base)
                del manifest[key]
                self.assertFailsWith(self.repo.validate(manifest), "missing-field")

    def test_malformed_variant_values(self) -> None:
        base = self.repo.build(counts(1, 4))
        cases = [
            ("scale", 0, "scale"), ("scale", -0.5, "scale"), ("scale", "0.5", "scale"), ("scale", True, "scale"),
            ("cell_size", [16], "cell-size"), ("cell_size", [16.0, 24], "cell-size"), ("cell_size", [0, 24], "cell-size"),
            ("ground_pin", [8], "ground-pin"), ("ground_pin", [16, 22], "ground-pin"), ("ground_pin", [8, -1], "ground-pin"),
            ("master", "x.png", "master"), ("master", {"path": FRAME_DIR + "/nope.png"}, "master"),
            ("frames", [], "frames-malformed"), ("schema_version", 2, "schema-version"), ("project", "other", "project"),
        ]
        for key, value, code in cases:
            with self.subTest(key=key, value=value):
                manifest = copy.deepcopy(base)
                manifest[key] = value
                self.assertFailsWith(self.repo.validate(manifest), code)

    def test_frame_carrying_its_own_scale_or_anchor_fails(self) -> None:
        base = self.repo.build(counts(1, 4))
        for key, value in (("scale", 1.0), ("ground_pin", [8, 22]), ("cell_size", [16, 24]),
                           ("foot_anchor_source_pixels", [8, 22]), ("anchor", [8, 22])):
            with self.subTest(key=key):
                manifest = copy.deepcopy(base)
                manifest["frames"][3][key] = value
                self.assertFailsWith(self.repo.validate(manifest), "frame-own-scale-or-anchor")

    def test_master_hash_mismatch_fails(self) -> None:
        manifest = self.repo.build(counts(1, 4))
        manifest["master"]["sha256"] = "0" * 64
        self.assertFailsWith(self.repo.validate(manifest), "sha256-mismatch")

    def test_same_variant_in_two_manifests_fails(self) -> None:
        first = self.repo.build(counts(1, 4))
        second = self.repo.build(counts(1, 4))
        self.assertFailsWith(self.repo.validate(first, second), "variant-declared-twice")

    def test_two_different_variants_pass_together(self) -> None:
        hero = self.repo.build(counts(1, 4))
        rival = self.repo.build(counts(2, 6), visual_id="test-rival")
        self.assertPasses(self.repo.validate(hero, rival))


class PixelChecks(ValidatorTestCase):
    def _replace_image(self, manifest: dict, index: int, image: Image.Image, update_hash: bool = True) -> None:
        path = self.repo.root / manifest["frames"][index]["path"]
        image.save(path)
        if update_hash:
            manifest["frames"][index]["sha256"] = sha(path)

    def test_hash_mismatch_and_hash_case(self) -> None:
        manifest = self.repo.build(counts(1, 4))
        bad = copy.deepcopy(manifest)
        bad["frames"][0]["sha256"] = "A" * 64
        self.assertFailsWith(self.repo.validate(bad), "sha256-mismatch")
        mixed = copy.deepcopy(manifest)
        digest = mixed["frames"][0]["sha256"].lower()
        mixed["frames"][0]["sha256"] = digest[:10] + digest[10:].upper()
        if mixed["frames"][0]["sha256"] not in (digest, digest.upper()):
            self.assertFailsWith(self.repo.validate(mixed), "sha256-malformed")
        lower = copy.deepcopy(manifest)
        lower["frames"][0]["sha256"] = digest
        self.assertPasses(self.repo.validate(lower))

    def test_non_rgba_modes_fail(self) -> None:
        for mode in ("RGB", "P", "LA", "L"):
            with self.subTest(mode=mode):
                manifest = self.repo.build(counts(1, 4))
                path = self.repo.root / manifest["frames"][2]["path"]
                Image.open(path).convert(mode).save(path)
                manifest["frames"][2]["sha256"] = sha(path)
                self.assertFailsWith(self.repo.validate(manifest), "png-not-rgba")

    def test_combined_image_with_wrong_cell_size_fails(self) -> None:
        manifest = self.repo.build(counts(1, 4))
        path = self.repo.root / manifest["frames"][1]["path"]
        single = Image.open(path).convert("RGBA")
        sheet = Image.new("RGBA", (single.width * 2, single.height))
        sheet.paste(single, (0, 0))
        sheet.paste(single, (single.width, 0))
        self._replace_image(manifest, 1, sheet)
        manifest["frames"][1]["source_size"] = list(sheet.size)
        self.assertFailsWith(self.repo.validate(manifest), "cell-size-mismatch")

    def test_multi_frame_png_fails(self) -> None:
        manifest = self.repo.build(counts(1, 4))
        path = self.repo.root / manifest["frames"][1]["path"]
        first = Image.open(path).convert("RGBA")
        second = ImageOps.mirror(first)
        first.save(path, save_all=True, append_images=[second])
        manifest["frames"][1]["sha256"] = sha(path)
        self.assertFailsWith(self.repo.validate(manifest), "png-multi-frame")

    def test_non_png_file_fails(self) -> None:
        manifest = self.repo.build(counts(1, 4))
        path = self.repo.root / manifest["frames"][1]["path"]
        Image.open(path).convert("RGB").save(path, format="JPEG")
        manifest["frames"][1]["sha256"] = sha(path)
        self.assertFailsWith(self.repo.validate(manifest), "not-png")

    def test_opaque_corner_fails(self) -> None:
        manifest = self.repo.build(counts(1, 4))
        image = Image.open(self.repo.root / manifest["frames"][0]["path"]).convert("RGBA")
        image.putpixel((image.width - 1, image.height - 1), (0, 0, 0, 255))
        self._replace_image(manifest, 0, image)
        manifest["frames"][0]["alpha_bounds_inclusive"] = measured_bounds(image, 64)
        self.assertFailsWith(self.repo.validate(manifest), "corners-not-transparent")

    def test_alpha_bounds_and_size_must_match_record(self) -> None:
        base = self.repo.build(counts(1, 4))
        bounds = copy.deepcopy(base)
        bounds["frames"][0]["alpha_bounds_inclusive"][3] += 1
        self.assertFailsWith(self.repo.validate(bounds), "alpha-bounds-mismatch")
        threshold = copy.deepcopy(base)
        threshold["frames"][0]["alpha_threshold"] = 20  # the faint fringe pixel now counts
        self.assertFailsWith(self.repo.validate(threshold), "alpha-bounds-mismatch")
        size = copy.deepcopy(base)
        size["frames"][0]["source_size"] = [16, 25]
        self.assertFailsWith(self.repo.validate(size), "source-size-mismatch")
        for bad in (0, 256, "64", None):
            with self.subTest(alpha_threshold=bad):
                manifest = copy.deepcopy(base)
                manifest["frames"][0]["alpha_threshold"] = bad
                self.assertFailsWith(self.repo.validate(manifest), "alpha-threshold")

    def test_empty_frame_fails(self) -> None:
        manifest = self.repo.build(counts(1, 4))
        self._replace_image(manifest, 0, Image.new("RGBA", (16, 24)))
        self.assertFailsWith(self.repo.validate(manifest), "frame-empty")

    def test_alpha_facts_are_reported(self) -> None:
        report = self.repo.validate(self.repo.build(counts(1, 4)))
        frame = report["manifests"][0]["facts"]["frames"][0]
        self.assertEqual(frame["corner_alpha"], [0, 0, 0, 0])
        self.assertEqual(frame["partial_alpha_pixels"], 2)
        self.assertEqual(frame["low_alpha_pixels_below_threshold"], 1)
        self.assertEqual(frame["border_nonzero_alpha_pixels"], 0)

    def test_idle_visible_height_is_reported_not_judged(self) -> None:
        manifest = self.repo.build(counts(4, 8), cell=(80, 112), pin=(40, 104), scale=0.5, idle_height=96)
        report = self.repo.validate(manifest)
        self.assertPasses(report)
        summary = report["manifests"][0]["facts"]["per_action_direction"]
        for direction in DIRECTIONS:
            self.assertEqual(summary["idle"][direction]["visible_height_logical_px_range"], [48.0, 48.0])
            self.assertEqual(summary["walk"][direction]["alpha_bounds_height_range_texels"], [95, 96])
        short = self.repo.build(counts(1, 4), cell=(80, 112), pin=(40, 104), scale=0.5, idle_height=70,
                                visual_id="test-rival")
        report = self.repo.validate(short)
        self.assertPasses(report)  # tolerance undecided: reported only
        self.assertEqual(report["manifests"][0]["facts"]["per_action_direction"]["idle"]["south"]
                         ["visible_height_logical_px_range"], [35.0, 35.0])


class PathsAndNames(ValidatorTestCase):
    def test_bad_paths_fail(self) -> None:
        base = self.repo.build(counts(1, 4))
        real = base["frames"][0]["path"]
        outside = self.repo.root / "outputs" / Path(real).name
        shutil.copy(self.repo.root / real, outside)
        cases = {
            "outputs/" + Path(real).name: "path-outside-assets",
            "game/assets/../outputs/" + Path(real).name: "path-malformed",
            real.replace("/", "\\"): "path-malformed",
            (self.repo.root / real).as_posix(): "path-not-relative",
            "/" + real: "path-not-relative",
            FRAME_DIR + "/missing.png": "file-missing",
            "": "path-malformed",
        }
        for value, code in cases.items():
            with self.subTest(path=value):
                manifest = copy.deepcopy(base)
                manifest["frames"][0]["path"] = value
                self.assertFailsWith(self.repo.validate(manifest), code)
        manifest = copy.deepcopy(base)
        manifest["master"]["path"] = "outputs/" + Path(real).name
        self.assertFailsWith(self.repo.validate(manifest), "path-outside-assets")

    def test_path_case_must_match_disk(self) -> None:
        manifest = self.repo.build(counts(1, 4))
        manifest["frames"][0]["path"] = manifest["frames"][0]["path"].replace("premium-idle", "Premium-idle")
        report = self.repo.validate(manifest)
        self.assertFalse(report["automated_checks_passed"])
        self.assertTrue(codes(report) & {"path-case-mismatch", "file-missing"})

    def _rename(self, manifest: dict, index: int, new_name: str) -> None:
        entry = manifest["frames"][index]
        source = self.repo.root / entry["path"]
        target = source.with_name(new_name)
        source.rename(target)
        entry["path"] = f"{FRAME_DIR}/{new_name}"

    def test_filename_rules(self) -> None:
        base = self.repo.build(counts(1, 4))
        index = next(i for i, f in enumerate(base["frames"])
                     if (f["action"], f["direction"], f["phase"]) == ("walk", "east", 2))
        uid = "2fffff01"
        cases = {
            f"{SLUG}_test_hero_premium-walk-east-phase-02_m8-test_{STAMP}-{uid}.png": "filename-format",
            f"{SLUG}_liang-xu_premium-walk-east-phase-02_m8-test_{STAMP}-{uid}.png": "filename-visual-id",
            f"{SLUG}_test-hero_premium-walk-west-phase-02_m8-test_{STAMP}-{uid}.png": "filename-descriptor",
            f"{SLUG}_test-hero_premium-walk-east-phase-03_m8-test_{STAMP}-{uid}.png": "filename-phase",
            f"{SLUG}_test-hero_premium-walk-east-phase-2_m8-test_{STAMP}-{uid}.png": "filename-phase",
            f"{SLUG}_test-hero_premium-walk-east_m8-test_{STAMP}-{uid}.png": "filename-phase",
            f"{SLUG}_test-hero_walk-east-phase-02_m8-test_{STAMP}-{uid}.png": "filename-descriptor",
            f"{SLUG}_test-hero_premium-walk-east-phase-02_m8-test_20261399-120000-{uid}.png": "filename-timestamp",
            f"{SLUG}_test-hero_premium-walk-east-phase-02_m8-test_{STAMP}-ABCDEF01.png": "filename-format",
            f"other-project_test-hero_premium-walk-east-phase-02_m8-test_{STAMP}-{uid}.png": "filename-format",
            f"{SLUG}_test-hero_premium-walk-east-phase-02_M8_{STAMP}-{uid}.png": "filename-format",
        }
        for name, code in cases.items():
            with self.subTest(name=name):
                manifest = copy.deepcopy(base)
                self._rename(manifest, index, name)
                try:
                    self.assertFailsWith(self.repo.validate(manifest), code)
                finally:
                    (self.repo.root / manifest["frames"][index]["path"]).rename(self.repo.root / base["frames"][index]["path"])

    def test_single_frame_idle_may_carry_phase_01(self) -> None:
        manifest = self.repo.build(counts(1, 4))
        index = next(i for i, f in enumerate(manifest["frames"]) if f["action"] == "idle")
        name = Path(manifest["frames"][index]["path"]).name.replace("-idle-south_", "-idle-south-phase-01_")
        self._rename(manifest, index, name)
        self.assertPasses(self.repo.validate(manifest))

    def test_unique_id_collision_across_repository_fails(self) -> None:
        manifest = self.repo.build(counts(1, 4))
        frame_path = self.repo.root / manifest["frames"][0]["path"]
        uid = frame_path.stem.rsplit("-", 1)[1]
        Path(str(frame_path) + ".import").write_text("[remap]\n", encoding="utf-8")  # Godot sidecar is not a collision
        self.assertPasses(self.repo.validate(manifest))
        (self.repo.root / "outputs" / f"{SLUG}_other_review_m8_{STAMP}-{uid}.md").write_text("x", encoding="utf-8")
        self.assertFailsWith(self.repo.validate(manifest), "unique-id-collision")

    def test_duplicate_filename_in_two_folders_fails(self) -> None:
        manifest = self.repo.build(counts(1, 4))
        source = self.repo.root / manifest["frames"][0]["path"]
        other = self.repo.root / FRAME_DIR / "alt"
        other.mkdir()
        shutil.copy(source, other / source.name)
        manifest["frames"][0]["path"] = f"{FRAME_DIR}/alt/{source.name}"
        sibling = copy.deepcopy(manifest["frames"][0])
        sibling["path"] = f"{FRAME_DIR}/{source.name}"
        manifest["frames"].append(sibling)
        self.assertFailsWith(self.repo.validate(manifest), "filename-duplicate")

    def test_identity_reference_and_receipt_must_exist(self) -> None:
        base = self.repo.build(counts(1, 4))
        missing = copy.deepcopy(base)
        missing["frames"][0]["identity_reference"] = "outputs/nope.png"
        self.assertFailsWith(self.repo.validate(missing), "file-missing")
        receipt = copy.deepcopy(base)
        receipt["frames"][0]["review_receipt"] = "outputs/nope.json"
        self.assertFailsWith(self.repo.validate(receipt), "file-missing")
        other_portrait = copy.deepcopy(base)
        for frame in other_portrait["frames"]:
            frame["identity_reference"] = other_portrait["master"]["path"]
        report = self.repo.validate(other_portrait)
        self.assertPasses(report)
        self.assertIn("identity-reference", warning_codes(report))


class FrameRecords(ValidatorTestCase):
    def test_required_frame_fields(self) -> None:
        base = self.repo.build(counts(1, 4))
        for key in validator.FRAME_REQUIRED:
            with self.subTest(key=key):
                manifest = copy.deepcopy(base)
                del manifest["frames"][5][key]
                self.assertFailsWith(self.repo.validate(manifest), "frame-missing-field")

    def test_malformed_frame_values(self) -> None:
        base = self.repo.build(counts(1, 4))
        cases = [
            ("direction", "up", "frame-direction"), ("direction", "South", "frame-direction"),
            ("phase", "1", "frame-phase"), ("phase", -1, "frame-phase"), ("phase", 1.0, "frame-phase"),
            ("action", "Walk", "frame-action"), ("visual_id", "liang_xu", "frame-visual-id"),
            ("stage", "", "stage"), ("source_size", "16x24", "source-size-malformed"),
            ("alpha_bounds_inclusive", [1, 2, 3], "alpha-bounds-malformed"),
        ]
        for key, value, code in cases:
            with self.subTest(key=key, value=value):
                manifest = copy.deepcopy(base)
                manifest["frames"][5][key] = value
                self.assertFailsWith(self.repo.validate(manifest), code)
        not_object = copy.deepcopy(base)
        not_object["frames"][0] = "frame.png"
        self.assertFailsWith(self.repo.validate(not_object), "frame-malformed")

    def test_contact_points(self) -> None:
        base = self.repo.build(counts(1, 4))
        cases = [
            ("missing", None, "frame-missing-field"),
            ("not list", {"foot": "left", "point": [8, 22]}, "contact-points-malformed"),
            ("outside cell", [{"foot": "left", "point": [16, 22]}], "contact-points-outside-cell"),
            ("negative", [{"foot": "left", "point": [-1, 22]}], "contact-points-outside-cell"),
            ("bad foot", [{"foot": "tail", "point": [8, 22]}], "contact-points-foot"),
            ("same foot twice", [{"foot": "left", "point": [8, 22]}, {"foot": "left", "point": [9, 22]}], "contact-points-foot"),
            ("float point", [{"foot": "left", "point": [8.5, 22]}], "contact-points-malformed"),
            ("extra key", [{"foot": "left", "point": [8, 22], "scale": 2}], "contact-points-malformed"),
        ]
        for label, value, code in cases:
            with self.subTest(label):
                manifest = copy.deepcopy(base)
                if value is None:
                    del manifest["frames"][6]["contact_points"]
                else:
                    manifest["frames"][6]["contact_points"] = value
                self.assertFailsWith(self.repo.validate(manifest), code)

    def test_contact_facts_follow_each_frame(self) -> None:
        report = self.repo.validate(self.repo.build(counts(1, 4)))
        self.assertPasses(report)
        summary = report["manifests"][0]["facts"]["per_action_direction"]
        self.assertEqual(summary["walk"]["south"]["contact_feet_by_phase"],
                         {"1": ["left"], "2": ["right"], "3": ["left"], "4": ["right"]})
        self.assertEqual(summary["idle"]["east"]["contact_feet_by_phase"], {"0": ["left", "right"]})
        frame = next(f for f in report["manifests"][0]["facts"]["frames"] if f.get("action") == "walk")
        self.assertEqual(frame["contact_points"][0]["alpha_at_point"], 255)

    def test_west_authoring(self) -> None:
        base = self.repo.build(counts(1, 4))
        west = next(i for i, f in enumerate(base["frames"]) if f["direction"] == "west")
        for value in (None, "mirrored", "MIRRORED_EAST"):
            with self.subTest(value=value):
                manifest = copy.deepcopy(base)
                if value is None:
                    del manifest["frames"][west]["west_authoring"]
                else:
                    manifest["frames"][west]["west_authoring"] = value
                self.assertFailsWith(self.repo.validate(manifest), "west-authoring")

    def test_west_mirror_is_flagged_not_failed(self) -> None:
        mirrored = self.repo.build(counts(2, 4), mirror_west=True)
        report = self.repo.validate(mirrored)
        self.assertPasses(report)
        comparison = report["manifests"][0]["facts"]["west_mirror_comparison"]
        self.assertEqual(len(comparison), 6)
        self.assertTrue(all(c["west_is_pixel_mirror_of_east"] for c in comparison))
        self.assertIn("west-mirror-flag", warning_codes(report))

        mislabelled = copy.deepcopy(mirrored)
        for frame in mislabelled["frames"]:
            if frame["direction"] == "west":
                frame["west_authoring"] = "independent"
        report = self.repo.validate(mislabelled)
        self.assertPasses(report)
        self.assertTrue(any("west_authoring is 'independent'" in w["message"]
                            for w in report["manifests"][0]["warnings"]))

        independent = self.repo.build(counts(2, 4), visual_id="test-rival")
        report = self.repo.validate(independent)
        self.assertPasses(report)
        self.assertFalse(any(c["west_is_pixel_mirror_of_east"]
                             for c in report["manifests"][0]["facts"]["west_mirror_comparison"]))
        self.assertNotIn("west-mirror-flag", warning_codes(report))


class RegistryAndApproval(ValidatorTestCase):
    def test_unregistered_visual_id_fails(self) -> None:
        manifest = self.repo.build(counts(1, 4), visual_id="not-in-registry")
        self.assertFailsWith(self.repo.validate(manifest), "visual-id-unregistered")

    def test_missing_or_broken_registry_fails(self) -> None:
        manifest_path = self.repo.write_manifest(self.repo.build(counts(1, 4)))
        report = validator.Validator(self.repo.root, self.repo.root / "nope.json").run([manifest_path])
        self.assertFailsWith(report, "registry")
        broken = self.repo.root / "broken.json"
        broken.write_text("{", encoding="utf-8")
        self.assertFailsWith(validator.Validator(self.repo.root, broken).run([manifest_path]), "registry")

    def test_approval_fields_and_wording_fail(self) -> None:
        base = self.repo.build(counts(1, 4))
        frame_flag = copy.deepcopy(base)
        frame_flag["frames"][0]["approval"] = "approved"
        self.assertFailsWith(self.repo.validate(frame_flag), "approval-field")
        top_flag = copy.deepcopy(base)
        top_flag["review_status"] = "pending"
        self.assertFailsWith(self.repo.validate(top_flag), "approval-field")
        nested = copy.deepcopy(base)
        nested["notes"] = {"art": {"art_approval": True}}
        self.assertFailsWith(self.repo.validate(nested), "approval-field")
        for stage in ("user-approved", "accepted", "用户美术验收"):
            with self.subTest(stage=stage):
                manifest = copy.deepcopy(base)
                manifest["frames"][0]["stage"] = stage
                self.assertFailsWith(self.repo.validate(manifest), "stage-approval")

    def test_report_never_sets_approval(self) -> None:
        report = self.repo.validate(self.repo.build(counts(1, 4)))
        self.assertPasses(report)
        self.assertEqual(validator.find_approval_keys(report), [])
        self.assertIn("does not approve art", report["notice"])


class MalformedManifests(ValidatorTestCase):
    def test_malformed_json_is_reported_not_raised(self) -> None:
        for text in ("{not json", '{"a": 1, "a": 2}', '{"scale": NaN}', "[]", '"text"', ""):
            with self.subTest(text=text):
                report = self.repo.validate(self.repo.write_manifest(text))
                self.assertFailsWith(report, "manifest-malformed")

    def test_missing_manifest_file(self) -> None:
        report = self.repo.validate(self.repo.root / "absent.json")
        self.assertFailsWith(report, "manifest-missing")

    def test_manifest_name_warning(self) -> None:
        path = self.repo.write_manifest(self.repo.build(counts(1, 4)), name="manifest.json")
        report = self.repo.validate(path)
        self.assertPasses(report)
        self.assertIn("manifest-name", warning_codes(report))


class CommandLine(ValidatorTestCase):
    def snapshot(self) -> dict:
        state = {}
        for directory, _, files in os.walk(self.repo.root.parent):
            for name in files:
                path = Path(directory, name)
                stat = path.stat()
                state[str(path)] = (stat.st_size, stat.st_mtime_ns, sha(path))
        return state

    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-I", str(TOOL), "--repo-root", str(self.repo.root), *args],
                              capture_output=True, cwd=self.repo.root.parent, timeout=120)

    def test_cli_exit_codes_json_and_read_only(self) -> None:
        good = self.repo.write_manifest(self.repo.build(counts(4, 8)))
        bad_manifest = self.repo.build(counts(1, 4), visual_id="test-rival")
        del bad_manifest["frame_counts"]
        bad = self.repo.write_manifest(bad_manifest)
        before = self.snapshot()

        result = self.run_cli("--format", "json", str(good))
        self.assertEqual(result.returncode, 0, result.stdout.decode("utf-8")[:3000])
        report = json.loads(result.stdout.decode("utf-8"))
        self.assertTrue(report["automated_checks_passed"])
        self.assertEqual(report["manifests"][0]["facts"]["declared_frame_total"], 48)

        result = self.run_cli(str(good), str(bad))
        self.assertEqual(result.returncode, 1)
        text = result.stdout.decode("utf-8")
        self.assertIn("FAIL missing-field: top-level field 'frame_counts' is missing", text)
        self.assertIn("does not approve art", text)

        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.snapshot(), before, "validator must not create or modify any file")


if __name__ == "__main__":
    unittest.main(verbosity=2)
