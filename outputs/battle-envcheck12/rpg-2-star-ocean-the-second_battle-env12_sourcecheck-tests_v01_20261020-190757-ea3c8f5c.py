#!/usr/bin/env python3
"""Negative/positive tests for the battle-env12 source checker.

The fixture is synthetic, tiny, local and unapproved. It is built inside the
workspace so Windows recursive cleanup can be containment-checked first.
"""
from __future__ import annotations

import hashlib
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
STAMP = "20261020-190757"


def _name(subject, purpose, ext, n):
    return f"wb-battle-env12_{subject}_{purpose}_fixture_{STAMP}-{n:08x}.{ext}"


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _text_lf_sha(p):
    text = p.read_bytes().decode("utf-8")
    return hashlib.sha256(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")).hexdigest()


def _rect(a, x0, y0, x1, y1, color):
    a[y0:y1, x0:x1] = color


def _png_bytes(a):
    import io

    buf = io.BytesIO()
    Image.fromarray(np.ascontiguousarray(a), "RGBA").save(buf, format="PNG")
    return buf.getvalue()


def build_fixture(root: Path) -> Path:
    root = root.resolve()
    src = root / "src"
    src.mkdir()
    h, w = 424, 1280
    x = np.arange(w)[None, :]
    y = np.arange(h)[:, None]
    base = np.stack(
        [
            (40 + (x * 7 + y * 3) % 120).astype(np.uint8),
            (35 + (x * 3 + y * 11) % 90).astype(np.uint8),
            (30 + (x * 5 + y * 5) % 80).astype(np.uint8),
        ],
        axis=2,
    )
    base_path = src / _name("base", "src", "png", 1)
    Image.fromarray(base, "RGB").save(base_path)

    base_layer = np.asarray(Image.fromarray(base, "RGB").resize((640, 212), Image.Resampling.NEAREST)).copy()
    base_layer_path = root / _name("base", "layer", "png", 2)
    Image.fromarray(base_layer, "RGB").save(base_layer_path)

    specs = [
        ("deck-plate", [(20, 20, 120, 60, (150, 120, 80, 255))]),
        ("console-inset", [(180, 40, 230, 90, (60, 130, 140, 255))]),
        ("signal-mast", [(300, 15, 360, 55, (200, 170, 90, 255))]),
        ("conduit-bracket", [(420, 60, 500, 100, (90, 95, 105, 255))]),
        ("vine-tuft", [(540, 30, 610, 80, (60, 120, 70, 255))]),
        (
            "brass-ground-detail",
            [(250, 110, 300, 140, (180, 140, 70, 255)), (100, 200, 102, 202, (70, 60, 50, 255))],
        ),
    ]
    native_arrays, native_paths = [], []
    for i, (subject, rects) in enumerate(specs, start=3):
        a = np.zeros((212, 640, 4), dtype=np.uint8)
        for r in rects:
            _rect(a, *r)
        p = root / _name(subject, "layer", "png", i)
        Image.fromarray(a, "RGBA").save(p)
        native_arrays.append(a)
        native_paths.append(p)

    flat = np.dstack([base_layer, np.full((212, 640), 255, np.uint8)])
    for a in native_arrays:
        mask = a[..., 3] == 255
        flat[mask, :3] = a[mask, :3]
    flat_path = root / _name("flat", "merged", "png", 20)
    Image.fromarray(flat).save(flat_path)

    names = ["fixture-base", *[s[0] for s in specs]]
    arrays = [np.dstack([base_layer, np.full((212, 640), 255, np.uint8)])] + native_arrays
    layers = [
        {"name": names[0], "file": base_layer_path.name, "sha256": _sha(base_layer_path), "kind": "inherited-base"},
        *[
            {"name": names[i], "file": native_paths[i - 1].name, "sha256": _sha(native_paths[i - 1]), "kind": "native-authored"}
            for i in range(1, 7)
        ],
    ]

    pxo_path = root / _name("layers", "source", "pxo", 21)
    pxo_meta = {
        "size_x": 640,
        "size_y": 212,
        "frames": [{"cels": []}],
        "layers": [{"name": n} for n in names],
    }
    with zipfile.ZipFile(pxo_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mimetype", "application/x-pixelorama")
        z.writestr("data.json", json.dumps(pxo_meta, separators=(",", ":")))
        for i, a in enumerate(arrays, start=1):
            z.writestr(f"image_data/frames/1/layer_{i}", a.tobytes())

    ora_path = root / _name("layers", "stack", "ora", 22)
    stack = ['<?xml version="1.0" encoding="UTF-8"?>', '<image version="0.0.3" w="640" h="212">', "<stack>"]
    with zipfile.ZipFile(ora_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mimetype", "image/openraster")
        for i, (n, a) in enumerate(reversed(list(zip(names, arrays)))):
            member = f"data/{i:02d}-{n}.png"
            z.writestr(member, _png_bytes(a))
            stack.append(f'<layer name="{n}" src="{member}" x="0" y="0" opacity="1.0" visibility="visible"/>')
        stack += ["</stack>", "</image>"]
        z.writestr("stack.xml", "\n".join(stack))
        z.writestr("mergedimage.png", _png_bytes(flat))

    author_path = src / _name("author", "source", "py", 30)
    author_path.write_text("# synthetic fixture author; not art\n", encoding="utf-8", newline="\n")

    manifest = {
        "schema": "worlds-between.battle-environment-source.v1",
        "canvas": [640, 212],
        "base": {
            "file": base_path.relative_to(root).as_posix(),
            "sha256": _sha(base_path),
            "method": "nearest-neighbor 2x downsample of flattened inherited RGB plate",
        },
        "layers": layers,
        "flat": {"file": flat_path.name, "sha256": _sha(flat_path)},
        "pxo": {"file": pxo_path.name, "sha256": _sha(pxo_path)},
        "ora": {"file": ora_path.name, "sha256": _sha(ora_path)},
        "author": {"file": author_path.relative_to(root).as_posix(), "sha256TextLf": _text_lf_sha(author_path)},
        "protected": {
            "arenaFloorScreenY": 272,
            "playBand": [0, 90, 640, 212],
            "openLaneLocalY": [150, 211],
        },
        "artApproved": False,
        "defaultAdopted": False,
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest_path


class SourceCheckTests(unittest.TestCase):
    def setUp(self):
        # Path.mkdir (not tempfile.mkdtemp) creates a directory this sandbox can write
        # and clean up; the temp root is still resolved and checked inside the workspace.
        self.tmp = (REPO_ROOT / f"bec-{uuid.uuid4().hex[:8]}").resolve()
        self.tmp.mkdir()
        self.assertTrue(self.tmp.is_relative_to(REPO_ROOT))
        self.addCleanup(self._cleanup)
        self.manifest = build_fixture(self.tmp)

    def _cleanup(self):
        p = self.tmp.resolve()
        self.assertTrue(p.is_relative_to(REPO_ROOT), f"cleanup escaped workspace: {p}")
        self.assertNotEqual(p, REPO_ROOT)
        self.assertTrue(p.name.startswith("bec-"), f"unexpected cleanup target: {p}")
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

    def test_positive_valid_passes(self):
        out = self.tmp / "check-result.json"
        proc, result = self._run(out=out)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIsNotNone(result, proc.stdout + proc.stderr)
        self.assertTrue(result["passed"], result.get("errors"))
        self.assertTrue(all(c["ok"] for c in result["checks"].values()), result["checks"])
        self.assertEqual(len(result["nativeLayers"]), 6)
        for layer in result["nativeLayers"]:
            self.assertTrue(layer["nonempty"])
            self.assertTrue(layer["hardAlpha"])
            self.assertIsNotNone(layer["bounds"])
        self.assertTrue(result["protectedFrontLane"]["anyNativePixels"])
        self.assertFalse(result["productionCreditAwarded"])
        self.assertFalse(result["artApproved"])
        self.assertFalse(result["defaultAdopted"])
        self.assertTrue(out.is_file())
        self.assertEqual(json.loads(out.read_text(encoding="utf-8")), result)

    def test_bad_hash_rejects(self):
        def mutate(m):
            m["layers"][3]["sha256"] = "0" * 64

        proc, result = self._run(self._manifest_variant("bad-hash.json", mutate))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["hashes"]["ok"])

    def test_native_layer_corruption_rejects(self):
        path = self.tmp / json.loads(self.manifest.read_text(encoding="utf-8"))["layers"][3]["file"]
        im = Image.open(path).convert("RGBA")
        im.putpixel((10, 10), (255, 0, 0, 255))
        im.save(path)

        def mutate(m):
            m["layers"][3]["sha256"] = _sha(path)

        proc, result = self._run(self._manifest_variant("corrupt-native.json", mutate))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["pxo"]["ok"])

    def test_wrong_flat_pixels_rejects(self):
        m = json.loads(self.manifest.read_text(encoding="utf-8"))
        path = self.tmp / m["flat"]["file"]
        im = Image.open(path).convert("RGBA")
        im.putpixel((0, 0), (0, 255, 0, 255))
        im.save(path)

        def mutate(mm):
            mm["flat"]["sha256"] = _sha(path)

        proc, result = self._run(self._manifest_variant("wrong-flat.json", mutate))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["pxo"]["ok"] or result["checks"]["ora"]["ok"])

    def test_malformed_json_rejects(self):
        p = self.tmp / "malformed.json"
        p.write_text("{", encoding="utf-8")
        proc, result = self._run(p)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIsNotNone(result)
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["json"]["ok"])

    def test_traversal_refuses(self):
        def mutate(m):
            m["layers"][1]["file"] = "../escape.png"

        proc, result = self._run(self._manifest_variant("traversal.json", mutate))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["structure"]["ok"])
        self.assertIn("sibling", result["checks"]["structure"]["detail"])

    def test_source_files_not_mutated(self):
        before = {p.relative_to(self.tmp).as_posix(): _sha(p) for p in self.tmp.rglob("*") if p.is_file()}
        proc, result = self._run()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(result["passed"])
        after = {p.relative_to(self.tmp).as_posix(): _sha(p) for p in self.tmp.rglob("*") if p.is_file()}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main(verbosity=2)
