#!/usr/bin/env python3
"""Source-only checker for the worlds-between battle-environment source manifest.

Verifies declared hashes, path containment, layer order/non-emptiness, nearest
base retention, hard alpha, and independent PXO/ORA reconstruction of the flat
640x212 RGBA image. It does not inspect Godot, a GUI, or art quality.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
from PIL import Image

SCHEMA = "worlds-between.battle-environment-source.v1"
RESULT_SCHEMA = "worlds-between.battle-environment-source-check.v1"
W, H = 640, 212
BW, BH = 1280, 424
F0, F1 = 150, 211
KINDS = ("inherited-base", "native-authored")
PROTECTED = {"arenaFloorScreenY": 272, "playBand": [0, 90, 640, 212], "openLaneLocalY": [150, 211]}
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*(?:_[a-z0-9][a-z0-9-]*){3}_[0-9]{8}-[0-9]{6}-[0-9a-f]{8}\.[a-z0-9]+$")
HEX_RE = re.compile(r"[0-9a-fA-F]{64}")
LIMITATIONS = [
    "Source-only: no Godot/runtime integration, GUI SaveAs/reopen, or normal-game-path evidence is claimed.",
    "No art-quality, craft, occlusion, timing, cadence, or animation score is produced.",
    "Front-lane pixel counts are descriptive and do not auto-approve or reject composition.",
    "Naming is pattern-checked (lowercase + timestamp + 8 hex); actual creation time is not proven.",
    "No production credit, default adoption, creator acceptance, or human-playtest state is awarded.",
    "Full-scene postfiltering cannot be detected by this checker; provenance and author review remain root checks.",
]


class CheckError(Exception):
    pass


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _sha_lf(p):
    t = p.read_bytes().decode("utf-8")
    return hashlib.sha256(t.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")).hexdigest()


def _png(p):
    with Image.open(p) as im:
        im.load()
        return im.copy()


def _pngb(data):
    with Image.open(io.BytesIO(data)) as im:
        im.load()
        return im.copy()


def _rgba(im):
    return im if im.mode == "RGBA" else im.convert("RGBA")


def _sib(name, base):
    q = Path(name) if isinstance(name, str) else None
    if not q or not name or q.name != name or q.is_absolute() or q.drive or name in (".", ".."):
        raise CheckError(f"unsafe sibling file name: {name!r}")
    try:
        p = (base / name).resolve(strict=True)
    except FileNotFoundError:
        raise CheckError(f"missing sibling file: {name!r}") from None
    if p.parent != base.resolve():
        raise CheckError(f"sibling file escapes manifest directory: {name!r}")
    return p


def _repo(name, root):
    q = Path(name) if isinstance(name, str) else None
    if not q or not name or q.is_absolute() or q.drive or ".." in q.parts or not q.parts:
        raise CheckError(f"unsafe repo-relative path: {name!r}")
    try:
        p = (root / name).resolve(strict=True)
    except FileNotFoundError:
        raise CheckError(f"missing repo file: {name!r}") from None
    if not p.is_relative_to(root.resolve()):
        raise CheckError(f"repo-relative path escapes repo root: {name!r}")
    return p


def _bounds(mask, y=0):
    ys, xs = np.nonzero(mask)
    return None if not len(xs) else [int(xs.min()), int(ys.min()) + y, int(xs.max()) + 1, int(ys.max()) + 1 + y]


def _comp(arrays):
    out = np.zeros((H, W, 4), dtype=np.float64)
    for a in arrays:
        s = a.astype(np.float64) / 255.0
        sa, da = s[..., 3:4], out[..., 3:4]
        oa = sa + da * (1.0 - sa)
        num = s[..., :3] * sa + out[..., :3] * da * (1.0 - sa)
        rgb = np.divide(num, oa, out=np.zeros_like(num), where=oa > 0)
        out = np.concatenate((rgb, oa), axis=2)
    return np.clip(np.rint(out * 255.0), 0, 255).astype(np.uint8)


def _diff(a, b):
    d = np.abs(a.astype(np.int16) - b.astype(np.int16))
    return f"{int((d > 0).sum())} differing pixels, max channel delta {int(d.max())}"


def _safe_member(name):
    return bool(name) and not name.startswith("/") and "\\" not in name and all(p not in ("", ".", "..") for p in name.split("/"))


def _pxo(path, names, refs, flat):
    errs = []
    with zipfile.ZipFile(path) as z:
        mem = set(z.namelist())
        if "data.json" not in mem:
            return ["PXO missing data.json"]
        try:
            meta = json.loads(z.read("data.json"))
        except Exception as e:
            return [f"PXO data.json is not valid JSON: {e}"]
        if not isinstance(meta, dict):
            return ["PXO data.json is not an object"]
        if (meta.get("size_x"), meta.get("size_y")) != (W, H):
            errs.append(f"PXO canvas is {meta.get('size_x')}x{meta.get('size_y')}, expected {W}x{H}")
        if not isinstance(meta.get("frames"), list) or len(meta["frames"]) != 1:
            errs.append("PXO must contain exactly one frame")
        pl = meta.get("layers")
        if not isinstance(pl, list) or len(pl) != len(names):
            errs.append("PXO layer count does not match manifest")
        else:
            if [l.get("name") if isinstance(l, dict) else None for l in pl] != names:
                errs.append("PXO data.json layer names/order do not match manifest bottom-to-top")
            for l in pl:
                if not isinstance(l, dict):
                    errs.append("PXO layer entry is not an object")
                    continue
                n = l.get("name")
                if l.get("visible", True) is not True:
                    errs.append(f"PXO layer '{n}' is not visible")
                if l.get("opacity", 1.0) != 1.0:
                    errs.append(f"PXO layer '{n}' opacity is not 1.0")
                if l.get("blend_mode", 0) != 0:
                    errs.append(f"PXO layer '{n}' blend mode is not normal")
                if l.get("clipping_mask", False) is not False:
                    errs.append(f"PXO layer '{n}' has a clipping mask")
        fids = {n.split("/")[2] for n in mem if n.split("/")[:2] == ["image_data", "frames"] and len(n.split("/")) >= 3}
        if fids != {"1"}:
            errs.append(f"PXO frame directories {sorted(fids)}; expected only '1'")
        expected = {f"image_data/frames/1/layer_{i + 1}" for i in range(len(names))}
        for n in mem:
            if re.fullmatch(r"image_data/frames/1/layer_\d+", n) and n not in expected:
                errs.append(f"PXO unexpected layer member {n}")
        raws = []
        for i in range(len(names)):
            member = f"image_data/frames/1/layer_{i + 1}"
            if member not in mem:
                errs.append(f"PXO missing {member}")
                raws.append(None)
                continue
            data = z.read(member)
            if len(data) != W * H * 4:
                errs.append(f"PXO {member} is {len(data)} bytes, expected {W * H * 4} raw RGBA")
                raws.append(None)
                continue
            raws.append(np.frombuffer(data, dtype=np.uint8).reshape(H, W, 4).copy())
        for i, (raw, ref) in enumerate(zip(raws, refs)):
            if raw is not None and not np.array_equal(raw, ref):
                errs.append(f"PXO layer_{i + 1} pixels differ from declared layer '{names[i]}'")
        if all(r is not None for r in raws):
            comp = _comp(raws)
            if not np.array_equal(comp, flat):
                errs.append(f"PXO raw composition differs from flat ({_diff(comp, flat)})")
    return errs


def _ora(path, names, flat):
    errs = []
    with zipfile.ZipFile(path) as z:
        mem = set(z.namelist())
        if "stack.xml" not in mem:
            return ["ORA missing stack.xml"]
        try:
            root = ET.fromstring(z.read("stack.xml"))
        except Exception as e:
            return [f"ORA stack.xml is not valid XML: {e}"]
        if root.tag != "image":
            errs.append("ORA stack.xml root is not <image>")
        if (root.get("w"), root.get("h")) != (str(W), str(H)):
            errs.append(f"ORA canvas is {root.get('w')}x{root.get('h')}, expected {W}x{H}")
        stack = root.find("stack")
        elems = list(stack.findall("layer")) if stack is not None else []
        if stack is None:
            errs.append("ORA stack.xml missing <stack>")
        if len(elems) != len(names):
            errs.append(f"ORA layer count is {len(elems)}, expected {len(names)}")
        bottom = list(reversed(elems))
        if [e.get("name") for e in bottom] != names:
            errs.append("ORA layer names/order do not match manifest bottom-to-top")
        arrs = []
        for e in bottom:
            label, src = e.get("name"), e.get("src") or ""
            if not _safe_member(src) or src not in mem:
                errs.append(f"ORA layer '{label}' has unsafe/missing src {src!r}")
                arrs.append(None)
                continue
            if (e.get("x") or "0") != "0" or (e.get("y") or "0") != "0":
                errs.append(f"ORA layer '{label}' has a nonzero offset")
            if (e.get("opacity") or "1") not in ("1", "1.0"):
                errs.append(f"ORA layer '{label}' opacity is not 1.0")
            if (e.get("visibility") or "visible") != "visible":
                errs.append(f"ORA layer '{label}' is not visible")
            im = _pngb(z.read(src))
            if im.size != (W, H):
                errs.append(f"ORA layer '{label}' is {im.size}, expected {W}x{H}")
                arrs.append(None)
                continue
            arrs.append(np.asarray(_rgba(im)))
        if "mergedimage.png" not in mem:
            errs.append("ORA missing mergedimage.png")
        if all(a is not None for a in arrs):
            comp = _comp(arrs)
            if not np.array_equal(comp, flat):
                errs.append(f"ORA PNG stack composition differs from flat ({_diff(comp, flat)})")
    return errs


def _result(mp, root, checks, errors, natives, front):
    try:
        msha, mrel = _sha(mp), mp.relative_to(root).as_posix()
    except Exception:
        msha, mrel = None, str(mp)
    return {
        "schema": RESULT_SCHEMA,
        "sourceManifest": {"file": mrel, "sha256": msha},
        "repoRoot": str(root),
        "passed": bool(checks) and all(c["ok"] for c in checks.values()),
        "checks": checks,
        "errors": errors,
        "nativeLayers": natives,
        "protectedFrontLane": {
            "openLaneLocalY": [F0, F1],
            "nativeLayers": front,
            "anyNativePixels": any(x["pixels"] > 0 for x in front),
            "note": "Descriptive only; source check does not judge occlusion, readability, or art quality. Strict root visual judgment remains required.",
        },
        "protected": PROTECTED,
        "limitations": LIMITATIONS,
        "productionCreditAwarded": False,
        "artApproved": False,
        "defaultAdopted": False,
    }


def _obj(m, key, fields, hex_fields=()):
    o = m.get(key)
    if not isinstance(o, dict):
        raise CheckError(f"{key} must be an object")
    for f in fields:
        if not isinstance(o.get(f), str) or not o[f]:
            raise CheckError(f"{key}.{f} must be a non-empty string")
    for f in hex_fields:
        if not HEX_RE.fullmatch(o[f]):
            raise CheckError(f"{key}.{f} must be 64 hex characters")
    return o


def run(manifest_path, repo_root):
    checks, errors, natives, front = {}, [], [], []

    def add(name, ok, detail):
        checks[name] = {"ok": bool(ok), "detail": str(detail)}
        if not ok:
            errors.append(f"{name}: {detail}")

    try:
        repo_root = Path(repo_root).resolve(strict=True)
        if not repo_root.is_dir():
            raise CheckError("repo root is not a directory")
        manifest_path = Path(manifest_path).resolve(strict=True)
        if not manifest_path.is_file():
            raise CheckError("source manifest is not a file")
        if not manifest_path.is_relative_to(repo_root):
            raise CheckError("source manifest is outside the explicit repo root")
    except Exception as e:
        add("paths", False, str(e))
        return _result(Path(manifest_path), Path(repo_root), checks, errors, natives, front)
    add("paths", True, "manifest resolves inside the explicit repo root")
    try:
        m = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        add("json", False, f"malformed JSON: {e}")
        return _result(manifest_path, repo_root, checks, errors, natives, front)
    if not isinstance(m, dict):
        add("json", False, "manifest root is not a JSON object")
        return _result(manifest_path, repo_root, checks, errors, natives, front)
    add("json", True, "UTF-8 JSON object parsed")

    try:
        if m.get("schema") != SCHEMA:
            raise CheckError(f"schema must be {SCHEMA}")
        if m.get("canvas") != [W, H]:
            raise CheckError(f"canvas must be [{W}, {H}]")
        if m.get("protected") != PROTECTED:
            raise CheckError("protected geometry must equal the frozen contract values")
        if m.get("artApproved") is not False or m.get("defaultAdopted") is not False:
            raise CheckError("artApproved and defaultAdopted must both be false")
        add("schema", True, SCHEMA)
        add("canvas", True, f"{W}x{H}")
        add("protected", True, "arenaFloorScreenY=272; playBand=[0,90,640,212]; openLaneLocalY=[150,211]")
        add("approvalFlags", True, "artApproved=false; defaultAdopted=false; no approval inferred")

        base = _obj(m, "base", ("file", "sha256", "method"), ("sha256",))
        if "nearest" not in base["method"].lower():
            raise CheckError("base.method must declare nearest resampling")
        author = _obj(m, "author", ("file", "sha256TextLf"), ("sha256TextLf",))
        base_p = _repo(base["file"], repo_root)
        author_p = _repo(author["file"], repo_root)

        raw = m.get("layers")
        if not isinstance(raw, list) or len(raw) < 7:
            raise CheckError("layers must contain one inherited-base plus at least six native-authored entries")
        names, kinds, paths = [], [], []
        for i, l in enumerate(raw):
            if not isinstance(l, dict):
                raise CheckError(f"layers[{i}] must be an object")
            for f in ("name", "file", "sha256", "kind"):
                if not isinstance(l.get(f), str) or not l[f]:
                    raise CheckError(f"layers[{i}].{f} must be a non-empty string")
            if l["kind"] not in KINDS:
                raise CheckError(f"layers[{i}].kind is invalid")
            if l["name"] in names:
                raise CheckError(f"duplicate layer name: {l['name']!r}")
            if not HEX_RE.fullmatch(l["sha256"]):
                raise CheckError(f"layers[{i}].sha256 must be 64 hex characters")
            names.append(l["name"])
            kinds.append(l["kind"])
            paths.append(_sib(l["file"], manifest_path.parent))
        if kinds.count("inherited-base") != 1 or kinds[0] != "inherited-base":
            raise CheckError("exactly one inherited-base layer is required at the bottom")
        native = [i for i, k in enumerate(kinds) if k == "native-authored"]
        if len(native) < 6:
            raise CheckError(f"{len(native)} native-authored layers; at least six are required")

        flat = _obj(m, "flat", ("file", "sha256"), ("sha256",))
        pxo = _obj(m, "pxo", ("file", "sha256"), ("sha256",))
        ora = _obj(m, "ora", ("file", "sha256"), ("sha256",))
        flat_p = _sib(flat["file"], manifest_path.parent)
        pxo_p = _sib(pxo["file"], manifest_path.parent)
        ora_p = _sib(ora["file"], manifest_path.parent)

        allp = [base_p, author_p, flat_p, pxo_p, ora_p] + paths
        dupes = sorted({str(p) for p in allp if allp.count(p) > 1})
        add("uniqueFiles", not dupes, "all declared files are distinct" if not dupes else f"reused files: {dupes}")
        bad = [p.name for p in allp if not NAME_RE.fullmatch(p.name)]
        add("naming", not bad, "lowercase timestamp+8hex names" if not bad else f"bad names: {bad}")

        he = []
        for label, p, decl in [("base", base_p, base["sha256"])] + [
            (f"layers[{i}] {l['name']}", p, l["sha256"]) for i, (l, p) in enumerate(zip(raw, paths))
        ] + [("flat", flat_p, flat["sha256"]), ("pxo", pxo_p, pxo["sha256"]), ("ora", ora_p, ora["sha256"])]:
            actual = _sha(p)
            if actual != decl.lower():
                he.append(f"{label}: declared {decl.lower()} actual {actual}")
        actual = _sha_lf(author_p)
        if actual != author["sha256TextLf"].lower():
            he.append(f"author text-LF: declared {author['sha256TextLf'].lower()} actual {actual}")
        add("hashes", not he, "all declared hashes match" if not he else "; ".join(he))

        bim = _png(base_p)
        if bim.size != (BW, BH) or bim.mode not in ("RGB", "RGBA"):
            raise CheckError(f"base is {bim.size} {bim.mode}, expected {BW}x{BH} RGB/RGBA")
        ba = np.asarray(_rgba(bim))
        if int(ba[..., 3].min()) != 255:
            raise CheckError("base must be flattened/opaque")
        add("baseOriginal", True, f"{BW}x{BH} opaque, hash declared")

        blim = _png(paths[0])
        if blim.size != (W, H):
            raise CheckError(f"inherited-base layer is {blim.size}, expected {W}x{H}")
        bl = np.asarray(_rgba(blim))
        exp = np.asarray(_rgba(bim.resize((W, H), Image.Resampling.NEAREST)))
        nearest_ok = np.array_equal(bl, exp)
        add("baseNearest", nearest_ok, "base layer equals nearest 640x212 resample" if nearest_ok else "base layer is not the nearest 640x212 resample")

        arrs, modes = [], []
        for i, p in enumerate(paths):
            im = _png(p)
            if im.size != (W, H):
                raise CheckError(f"layer '{names[i]}' is {im.size}, expected {W}x{H}")
            modes.append(im.mode)
            arrs.append(np.asarray(_rgba(im)))

        ne = []
        for i in native:
            a = arrs[i]
            mask = a[..., 3] > 0
            hard = bool(np.isin(a[..., 3], (0, 255)).all())
            nz = int(mask.sum())
            b = _bounds(mask)
            lane = mask[F0:H, :]
            ln, lb = int(lane.sum()), _bounds(lane, F0)
            natives.append({"name": names[i], "file": paths[i].name, "kind": "native-authored", "nonempty": nz > 0, "nonzeroPixels": nz, "bounds": b, "hardAlpha": hard, "frontLanePixels": ln, "frontLaneBounds": lb})
            front.append({"name": names[i], "file": paths[i].name, "pixels": ln, "bounds": lb})
            if modes[i] != "RGBA":
                ne.append(f"'{names[i]}' mode is {modes[i]}, expected RGBA")
            if not hard:
                ne.append(f"'{names[i]}' has soft alpha")
            if nz == 0:
                ne.append(f"'{names[i]}' is empty")
        add("nativeLayers", not ne, f"{len(natives)} native layers nonempty and hard-alpha; bounds reported" if not ne else "; ".join(ne))

        fim = _png(flat_p)
        if fim.size != (W, H) or fim.mode != "RGBA":
            raise CheckError(f"flat is {fim.size} {fim.mode}, expected {W}x{H} RGBA")
        fa = np.asarray(fim)
        add("flat", True, f"{W}x{H} RGBA")

        try:
            pe = _pxo(pxo_p, names, arrs, fa)
        except Exception as e:
            pe = [f"cannot read PXO: {e}"]
        add("pxo", not pe, "PXO raw layer stack composes to flat; names/order match" if not pe else "; ".join(pe))
        try:
            oe = _ora(ora_p, names, fa)
        except Exception as e:
            oe = [f"cannot read ORA: {e}"]
        add("ora", not oe, "ORA PNG stack composes to flat; names/order match" if not oe else "; ".join(oe))

        total = sum(x["pixels"] for x in front)
        add("frontLaneReport", True, f"{total} native-authored pixels in localY{F0}..{F1}; descriptive only, strict root visual judgment required")
    except CheckError as e:
        add("structure", False, str(e))
    except Exception as e:
        add("structure", False, f"{type(e).__name__}: {e}")
    return _result(manifest_path, repo_root, checks, errors, natives, front)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check a worlds-between battle-environment source manifest.")
    ap.add_argument("manifest", help="source manifest JSON")
    ap.add_argument("--repo-root", required=True, help="explicit repository root for base/author and manifest containment")
    ap.add_argument("--out", help="optional unique result JSON (refuses to overwrite)")
    args = ap.parse_args(argv)
    result = run(Path(args.manifest), Path(args.repo_root))
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    sys.stdout.write(text)
    if args.out:
        out = Path(args.out)
        if out.exists():
            sys.stderr.write(f"refusing to overwrite existing --out: {out}\n")
            return 2
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8", newline="\n")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
