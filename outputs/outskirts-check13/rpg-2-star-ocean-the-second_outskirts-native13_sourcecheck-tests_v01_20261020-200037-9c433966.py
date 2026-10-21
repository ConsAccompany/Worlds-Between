#!/usr/bin/env python3
"""Positive/negative/no-mutation tests for the outskirts native13 checker.

Fixtures are synthetic, local and unapproved. They exercise source structure,
not art, collisions, runtime, or GUI behavior.
"""
from __future__ import annotations

import hashlib
import io
import json
import shutil
import subprocess
import sys
import unittest
import uuid
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
CHECKER = next(p for p in sorted(HERE.glob("*_sourcecheck_*.py")) if "tests" not in p.name)
STAMP = "20261020-200037"
BASE_REL = "game/assets/environments/rpg-2-star-ocean-the-second_scifi-outskirts_environment-background_m8-candidate_20261014-142557-58f0c3a1.png"
BASE_W, BASE_H = 1672, 941
W, H = 640, 360
PROTECTED = {
    "walkBounds": [24, 77, 616, 306],
    "spawn": [82, 260],
    "relay": [470, 128],
    "survey": [558, 277],
    "assist": [505, 258],
    "traces": [[125, 240], [408, 95]],
    "npc": [190, 150],
    "encounter": [355, 238],
}


def _name(purpose, variant, ext, n):
    return f"rpg-2-star-ocean-the-second_outskirts-native13_{purpose}_{variant}_{STAMP}-{n:08x}.{ext}"


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _text_lf_sha(p):
    text = p.read_bytes().decode("utf-8")
    return hashlib.sha256(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")).hexdigest()


def _rect(a, x0, y0, x1, y1, color):
    a[y0:y1, x0:x1] = color


def _png_bytes(a):
    buf = io.BytesIO()
    Image.fromarray(np.ascontiguousarray(a), "RGBA").save(buf, format="PNG")
    return buf.getvalue()


def build_fixture(root: Path) -> Path:
    root = root.resolve()
    src = root / "src"
    src.mkdir()

    x = np.arange(BASE_W)[None, :]
    y = np.arange(BASE_H)[:, None]
    base = np.stack(
        [
            (42 + (x * 7 + y * 3) % 110).astype(np.uint8),
            (37 + (x * 3 + y * 11) % 85).astype(np.uint8),
            (31 + (x * 5 + y * 5) % 76).astype(np.uint8),
        ],
        axis=2,
    )
    base_path = root / BASE_REL
    base_path.parent.mkdir(parents=True)
    Image.fromarray(base, "RGB").save(base_path)

    base_layer = np.asarray(Image.fromarray(base, "RGB").resize((W, H), Image.Resampling.NEAREST)).copy()
    base_layer_path = root / _name("base-layer", "v01", "png", 2)
    Image.fromarray(base_layer, "RGB").save(base_layer_path)

    specs = [
        ("relay-floor-panel", [(430, 108, 512, 152, (146, 116, 78, 255)), (440, 116, 478, 122, (50, 122, 128, 255))]),
        ("survey-threshold", [(520, 258, 598, 298, (111, 83, 62, 255)), (548, 268, 570, 272, (197, 158, 86, 255))]),
        ("inspection-workpad", [(466, 224, 548, 262, (86, 91, 98, 255)), (476, 234, 514, 244, (61, 137, 141, 255))]),
        ("trace-plate-west", [(104, 220, 148, 260, (153, 123, 83, 255)), (112, 232, 136, 238, (58, 134, 125, 255))]),
        ("trace-plate-east", [(388, 76, 432, 116, (148, 119, 81, 255)), (396, 88, 420, 94, (198, 161, 92, 255))]),
        ("cable-raceway-botanical", [(610, 80, 632, 300, (65, 73, 74, 255)), (600, 300, 634, 318, (65, 116, 74, 255))]),
    ]
    native_arrays, native_paths = [], []
    for i, (purpose, rects) in enumerate(specs, start=3):
        a = np.zeros((H, W, 4), dtype=np.uint8)
        for r in rects:
            _rect(a, *r)
        p = root / _name(purpose, "v01", "png", i)
        Image.fromarray(a, "RGBA").save(p)
        native_arrays.append(a)
        native_paths.append(p)

    flat = np.dstack([base_layer, np.full((H, W), 255, np.uint8)])
    for a in native_arrays:
        mask = a[..., 3] == 255
        flat[mask] = a[mask]
    flat_path = root / _name("flat-merged", "v01", "png", 20)
    Image.fromarray(flat, "RGBA").save(flat_path)

    names = ["fixture-base", *[s[0] for s in specs]]
    arrays = [np.dstack([base_layer, np.full((H, W), 255, np.uint8)])] + native_arrays
    layers = [
        {"name": names[0], "file": base_layer_path.name, "sha256": _sha(base_layer_path), "kind": "inherited-base"},
        *[
            {"name": names[i], "file": native_paths[i - 1].name, "sha256": _sha(native_paths[i - 1]), "kind": "native-authored"}
            for i in range(1, 7)
        ],
    ]

    pxo_path = root / _name("editable-layers", "v01", "pxo", 21)
    pxo_meta = {
        "size_x": W,
        "size_y": H,
        "frames": [{"cels": []}],
        "layers": [
            {"name": n, "visible": True, "opacity": 1.0, "blend_mode": 0, "clipping_mask": False}
            for n in names
        ],
    }
    with zipfile.ZipFile(pxo_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mimetype", "application/x-pixelorama")
        z.writestr("data.json", json.dumps(pxo_meta, separators=(",", ":")))
        for i, a in enumerate(arrays, start=1):
            z.writestr(f"image_data/frames/1/layer_{i}", a.tobytes())

    ora_path = root / _name("supplementary-stack", "v01", "ora", 22)
    stack = ['<?xml version="1.0" encoding="UTF-8"?>', f'<image version="0.0.3" w="{W}" h="{H}">', "<stack>"]
    with zipfile.ZipFile(ora_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mimetype", "image/openraster")
        for i, (n, a) in enumerate(reversed(list(zip(names, arrays)))):
            member = f"data/layer{i:02d}.png"
            z.writestr(member, _png_bytes(a))
            stack.append(
                f'<layer name="{n}" src="{member}" x="0" y="0" opacity="1.0" '
                'visibility="visible" composite-op="svg:src-over"/>'
            )
        stack += ["</stack>", "</image>"]
        z.writestr("stack.xml", "\n".join(stack))
        z.writestr("mergedimage.png", _png_bytes(flat))

    author_path = src / _name("author", "v01", "py", 30)
    author_path.write_text("# synthetic fixture author; not art\n", encoding="utf-8", newline="\n")

    manifest = {
        "schema": "worlds-between.outskirts-environment-source.v1",
        "canvas": [W, H],
        "base": {
            "file": BASE_REL,
            "sha256": _sha(base_path),
            "method": "nearest-neighbor 640x360 downsample of the inherited 1672x941 plate",
        },
        "layers": layers,
        "flat": {"file": flat_path.name, "sha256": _sha(flat_path)},
        "pxo": {"file": pxo_path.name, "sha256": _sha(pxo_path)},
        "ora": {"file": ora_path.name, "sha256": _sha(ora_path)},
        "author": {"file": author_path.relative_to(root).as_posix(), "sha256TextLf": _text_lf_sha(author_path)},
        "protected": PROTECTED,
        "artApproved": False,
        "defaultAdopted": False,
    }
    manifest_path = root / _name("manifest", "v01", "json", 40)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest_path


class SourceCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = (REPO_ROOT / f"oc13-{uuid.uuid4().hex[:8]}").resolve()
        self.tmp.mkdir()
        self.assertTrue(self.tmp.is_relative_to(REPO_ROOT))
        self.addCleanup(self._cleanup)
        self.manifest = build_fixture(self.tmp)

    def _cleanup(self):
        p = self.tmp.resolve()
        self.assertTrue(p.is_relative_to(REPO_ROOT), f"cleanup escaped workspace: {p}")
        self.assertNotEqual(p, REPO_ROOT)
        self.assertTrue(p.name.startswith("oc13-"), f"unexpected cleanup target: {p}")
        shutil.rmtree(p)

    def _run(self, manifest=None, out=None):
        cmd = [sys.executable, str(CHECKER), str(manifest or self.manifest), "--repo-root", str(self.tmp)]
        if out is not None:
            cmd += ["--out", str(out)]
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=str(REPO_ROOT))
        try:
            result = json.loads(proc.stdout)
        except Exception:
            result = None
        return proc, result

    def _manifest_variant(self, filename, mutate):
        m = json.loads(self.manifest.read_text(encoding="utf-8"))
        mutate(m)
        p = self.tmp / filename
        p.write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8", newline="\n")
        return p

    def test_positive_valid_fixture_passes(self):
        out = self.tmp / "check-result.json"
        proc, result = self._run(out=out)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIsNotNone(result, proc.stdout + proc.stderr)
        self.assertTrue(result["passed"], result.get("errors"))
        self.assertEqual(result["errors"], [])
        self.assertTrue(all(c["ok"] for c in result["checks"].values()), result["checks"])
        self.assertEqual(result["canvas"], [640, 360])
        self.assertEqual(result["inheritedBase"]["dimensions"], [1672, 941])
        self.assertEqual(result["protected"], PROTECTED)
        self.assertEqual(len(result["nativeLayers"]), 6)
        for layer in result["nativeLayers"]:
            self.assertTrue(layer["nonempty"])
            self.assertTrue(layer["hardAlpha"])
            self.assertIsNotNone(layer["bounds"])
        self.assertTrue(out.is_file())
        self.assertEqual(json.loads(out.read_text(encoding="utf-8")), result)

    def test_bad_declared_hash_rejects(self):
        def mutate(m):
            m["layers"][3]["sha256"] = "0" * 64

        proc, result = self._run(self._manifest_variant("bad-hash.json", mutate))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIsNotNone(result)
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["hashes"]["ok"])
        self.assertIn("layers[3]", result["checks"]["hashes"]["detail"])

    def test_traversal_path_rejects(self):
        def mutate(m):
            m["layers"][1]["file"] = "../escape.png"

        proc, result = self._run(self._manifest_variant("traversal.json", mutate))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["structure"]["ok"])
        self.assertIn("sibling", result["checks"]["structure"]["detail"])

    def test_pxo_layer_mismatch_rejects_even_with_updated_hash(self):
        m = json.loads(self.manifest.read_text(encoding="utf-8"))
        pxo_path = self.tmp / m["pxo"]["file"]
        with zipfile.ZipFile(pxo_path) as z:
            members = {n: z.read(n) for n in z.namelist()}
        members["image_data/frames/1/layer_2"] = np.zeros((H, W, 4), dtype=np.uint8).tobytes()
        with zipfile.ZipFile(pxo_path, "w", zipfile.ZIP_DEFLATED) as z:
            for n, data in members.items():
                z.writestr(n, data)

        def mutate(mm):
            mm["pxo"]["sha256"] = _sha(pxo_path)

        proc, result = self._run(self._manifest_variant("pxo-layer-mismatch.json", mutate))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertFalse(result["passed"])
        self.assertTrue(result["checks"]["hashes"]["ok"], result["checks"]["hashes"])
        self.assertFalse(result["checks"]["pxo"]["ok"])
        self.assertIn("layer_2", result["checks"]["pxo"]["detail"])

    def test_check_does_not_mutate_sources(self):
        before = {p.relative_to(self.tmp).as_posix(): _sha(p) for p in self.tmp.rglob("*") if p.is_file()}
        proc, result = self._run()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(result["passed"])
        after = {p.relative_to(self.tmp).as_posix(): _sha(p) for p in self.tmp.rglob("*") if p.is_file()}
        self.assertEqual(before, after)


    def test_native_pxo_directory_record_is_valid(self):
        m = json.loads(self.manifest.read_text(encoding="utf-8"))
        pxo_path = self.tmp / m["pxo"]["file"]
        with zipfile.ZipFile(pxo_path, "a") as z:
            z.writestr("image_data/frames/1/", b"")
        def mutate(mm): mm["pxo"]["sha256"] = _sha(pxo_path)
        proc, result = self._run(self._manifest_variant("valid-directory.json", mutate))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(result["passed"], result["errors"])

    def test_native_pxo_traversal_directory_is_rejected(self):
        m = json.loads(self.manifest.read_text(encoding="utf-8"))
        pxo_path = self.tmp / m["pxo"]["file"]
        with zipfile.ZipFile(pxo_path, "a") as z:
            z.writestr("../escape/", b"")
        def mutate(mm): mm["pxo"]["sha256"] = _sha(pxo_path)
        proc, result = self._run(self._manifest_variant("unsafe-directory.json", mutate))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertFalse(result["passed"])
        self.assertIn("unsafe archive member", result["checks"]["pxo"]["detail"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
