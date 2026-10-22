#!/usr/bin/env python3
"""Independent source validator for the upcoming Jiang Lan 4-direction exploration set.

Read-only over --root; writes only --out.  It does not import or run the target
author and never writes into the source/package trees.  It validates the existing
exploration-sprite-set schema: static + 4 idle + 12 walk + phase-aware stop bridge,
9 declared Jiang role layers plus hidden guides, frozen neutral statics, runtime
copies, and real-pixel contact/slip diagnostics at 140 logical px/s.

Usage:
  python ...py --root PATH --out PATH
Exit: 0 pass, 1 failure, 2 pending-source (manifest/package not produced yet).
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import math
import os
import shutil
import sys
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image

TAG = "20261022-154032-5bca7193"
PROJECT = "rpg-2-star-ocean-the-second"
ACTOR = "jiang-lan"
DIRS = ("south", "west", "north", "east")
ROLE_NAMES = ("boots", "trousers", "shirt", "vest", "arms", "devices", "face", "hair", "goggles")
W, H = 80, 112
PIVOT = (40, 104)
LOGICAL_H = 48
DENSITY = 2
SPEED = 140.0
WALK_MS = 40
NPH = 12
NIDLE = 4
SOURCE_REL = "outputs/jexplore39"
PACKAGE_REL = "game/data/jexplore39"


# --------------------------------------------------------------------------- io
def lp(path):
    p = Path(path)
    if os.name != "nt":
        return p
    s = str(p.resolve())
    return Path("\\\\?\\" + s) if not s.startswith("\\\\?\\") else p


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    return sha(lp(path).read_bytes())


def load_json(data):
    return json.loads(data.decode("utf-8-sig"))


def write_file(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(lp(path)), "wb") as handle:
        handle.write(data)


def write_json(path, obj):
    write_file(path, (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class Ctx:
    """Filesystem facade with in-memory overrides for refusal tests."""

    def __init__(self, root):
        self.root = Path(root).resolve()
        self.overrides = {}
        self.missing = set()

    @staticmethod
    def key(path):
        return os.path.normcase(os.path.abspath(str(path)))

    def read(self, path):
        k = self.key(path)
        if k in self.missing:
            raise FileNotFoundError(str(path))
        if k in self.overrides:
            return self.overrides[k]
        return lp(path).read_bytes()

    def exists(self, path):
        k = self.key(path)
        if k in self.missing:
            return False
        if k in self.overrides:
            return True
        return os.path.isfile(str(lp(path)))

    def resolve(self, ref, bases=()):
        p = Path(str(ref))
        if p.is_absolute():
            return p
        for base in bases:
            if base is None:
                continue
            q = Path(base) / p
            if self.exists(q):
                return q
        q = self.root / p
        if self.exists(q):
            return q
        return q


# ------------------------------------------------------------------ small utils
def add(checks, cid, ok, detail="", status=None):
    status = status or ("pass" if ok else "fail")
    checks.append({"id": cid, "ok": bool(ok), "status": status, "detail": detail})


def num(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def positive_durations(values):
    return bool(values) and all(num(v) and v > 0 for v in values)


def as_entries(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [v for v in value if isinstance(v, dict)]
    if isinstance(value, dict):
        if "file" in value or "path" in value or "ref" in value:
            return [value]
        return []
    return []


def entry_ref(entry):
    if not isinstance(entry, dict):
        return None
    ref = entry.get("file") or entry.get("path")
    return ref if isinstance(ref, str) else None


def read_entry(ctx, entry, bases):
    """Resolve one manifest entry and verify its declared raw hash."""
    ref = entry_ref(entry)
    if not ref:
        return {"ok": False, "error": "no-file"}
    path = ctx.resolve(ref, bases)
    if not ctx.exists(path):
        return {"ok": False, "ref": ref, "path": path, "error": "missing"}
    try:
        raw = ctx.read(path)
    except OSError as exc:
        return {"ok": False, "ref": ref, "path": path, "error": type(exc).__name__}
    declared = entry.get("sha256") or entry.get("rawsha256")
    actual = sha(raw)
    return {"ok": True, "ref": ref, "path": path, "bytes": raw, "sha": actual,
            "declared": declared, "hash_ok": declared is None or declared == actual}


def png_array(raw):
    return np.array(Image.open(io.BytesIO(raw)).convert("RGBA"))


def image_metrics(raw):
    a = png_array(raw)
    alpha = a[..., 3]
    ys, xs = np.nonzero(alpha)
    bbox = None
    if len(ys):
        bbox = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
    colors = {tuple(int(v) for v in c) for c in a[alpha == 255][:, :3]}
    border = bool(alpha[0].any() or alpha[-1].any() or alpha[:, 0].any() or alpha[:, -1].any())
    return {"size": (int(a.shape[1]), int(a.shape[0])), "alpha": set(int(v) for v in np.unique(alpha)),
            "bbox": bbox, "colors": colors, "border": border, "array": a}


def over_images(images):
    canvas = Image.new("RGBA", (W, H))
    for image in images:
        canvas.alpha_composite(image)
    return np.array(canvas)


def ora_layers(z):
    root = ET.fromstring(z.read("stack.xml"))
    out = []

    def walk(el, parent_visible=True, parent_opacity=1.0):
        for child in el:
            visible = parent_visible and child.get("visibility", "visible") != "hidden"
            opacity = parent_opacity * float(child.get("opacity", "1") or 1)
            if child.tag == "layer":
                out.append({"name": child.get("name", ""), "src": child.get("src", ""),
                            "x": int(child.get("x", "0") or 0), "y": int(child.get("y", "0") or 0),
                            "visible": visible, "opacity": opacity})
            elif child.tag == "stack":
                walk(child, visible, opacity)

    walk(root)
    return out


def compose_ora(z, layers):
    canvas = Image.new("RGBA", (W, H))
    for layer in reversed(layers):  # ORA XML is top-to-bottom
        if not layer["visible"] or layer["opacity"] <= 0 or not layer["src"]:
            continue
        image = Image.open(io.BytesIO(z.read(layer["src"]))).convert("RGBA")
        if layer["opacity"] < 1:
            image.putalpha(image.getchannel("A").point(lambda a: int(a * layer["opacity"])))
        canvas.alpha_composite(image, (layer["x"], layer["y"]))
    return np.array(canvas)


def pxo_compose(z, data, frame_number):
    canvas = Image.new("RGBA", (W, H))
    cels = data.get("frames", [{}])[frame_number - 1].get("cels", [])
    for index, layer in enumerate(data.get("layers", [])):
        if not layer.get("visible", True):
            continue
        raw = z.read(f"image_data/frames/{frame_number}/layer_{index + 1}")
        cel = Image.frombytes("RGBA", (W, H), raw)
        opacity = float(layer.get("opacity", 1.0)) * float(cels[index].get("opacity", 1.0) if index < len(cels) else 1.0)
        if opacity < 1:
            cel.putalpha(cel.getchannel("A").point(lambda a: int(a * opacity)))
        canvas.alpha_composite(cel)
    return np.array(canvas)


# ------------------------------------------------------------------- discovery
def locate_source(ctx, source_dir):
    if not source_dir.is_dir():
        return []
    found = []
    for path in sorted(source_dir.rglob("*.json")):
        try:
            data = load_json(ctx.read(path))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and isinstance(data.get("directions"), dict) and \
                (data.get("package") or data.get("visual_id") or data.get("actor_id")):
            found.append((path, data))
    found.sort(key=lambda item: (0 if "source-manifest" in item[0].name.lower() else 1, str(item[0])))
    return found


def locate_package(ctx, package_dir):
    out = {"runtime": [], "registry": [], "stop": []}
    if not package_dir.is_dir():
        return out
    for path in sorted(package_dir.rglob("*.json")):
        try:
            data = load_json(ctx.read(path))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        schema = str(data.get("schema", ""))
        if schema == "worlds-between.exploration-sprite-set.v1":
            out["runtime"].append((path, data))
        elif schema == "worlds-between.exploration-sprite-set-registry.v1":
            out["registry"].append((path, data))
        elif schema == "worlds-between.exploration-stop-transition.supplemental.v1":
            out["stop"].append((path, data))
    out["runtime"].sort(key=lambda item: (0 if item[0].parent == package_dir else 1, str(item[0])))
    return out


def frozen_neutrals(ctx):
    """The four existing Jiang static packages used as frozen neutral source."""
    root = ctx.root
    out = {}
    south_dir = root / "game/assets/characters/jiang-lan-native-south-v01"
    if south_dir.is_dir():
        for path in sorted(south_dir.glob("*manifest*.json")):
            try:
                data = load_json(ctx.read(path))
            except (OSError, ValueError):
                continue
            files = data.get("files") if isinstance(data, dict) else None
            png = files.get("png") if isinstance(files, dict) else None
            if isinstance(png, dict) and png.get("file"):
                out["south"] = frozen_record(ctx, path, png, south_dir)
                break
    directions = root / "game/assets/characters/jiang-lan-native-directions-v01"
    for direction in ("west", "north", "east"):
        folder = directions / direction
        if not folder.is_dir():
            continue
        candidates = sorted(folder.glob(f"*_{direction}-manifest_*.json"))
        if not candidates:
            candidates = sorted(folder.glob(f"*{direction}*manifest*.json"))
        for path in candidates:
            try:
                data = load_json(ctx.read(path))
            except (OSError, ValueError):
                continue
            files = data.get("files") if isinstance(data, dict) else None
            png = files.get("png") if isinstance(files, dict) else None
            if isinstance(png, dict) and png.get("file"):
                out[direction] = frozen_record(ctx, path, png, folder)
                break
    return out


def frozen_record(ctx, manifest_path, png_entry, folder):
    png_path = ctx.resolve(png_entry.get("file"), [folder])
    declared = png_entry.get("rawsha256") or png_entry.get("sha256")
    record = {"manifest": str(manifest_path), "png": str(png_path), "declared": declared,
              "sha": None, "ok": False}
    if ctx.exists(png_path):
        raw = ctx.read(png_path)
        record["sha"] = sha(raw)
        record["bytes"] = raw
        record["ok"] = declared is None or declared == record["sha"]
    return record


# ---------------------------------------------------------------- foot / slip
def _foot_windows(neutral, direction):
    alpha = neutral[..., 3] > 0
    ys, _ = np.nonzero(alpha)
    bottom = int(ys.max())
    band = alpha[max(0, bottom - 2):bottom + 1, :]
    windows = {}
    if direction in ("south", "north"):
        for key, (lo, hi) in {"L": (0, PIVOT[0]), "R": (PIVOT[0], W)}.items():
            xs = np.nonzero(band[:, lo:hi])[1]
            if len(xs):
                windows[key] = (max(0, lo + int(xs.min()) - 6), min(W, lo + int(xs.max()) + 6))
            else:
                windows[key] = (lo, hi)
    else:
        xs = np.nonzero(band)[1]
        windows["C"] = (max(0, int(xs.min()) - 12), min(W, int(xs.max()) + 12)) if len(xs) else (0, W)
    return windows, bottom


def _foot_point(frame, window, ground_row):
    lo, hi = window
    alpha = frame[:, lo:hi, 3] > 0
    ys, _ = np.nonzero(alpha)
    if not len(ys):
        return None
    max_row = int(ys.max())
    if max_row < ground_row - 14:
        return None
    contact = alpha[max(0, max_row - 1):max_row + 1, :]
    xs = np.nonzero(contact)[1] + lo
    if not len(xs):
        return None
    return {"x": float(xs.mean()), "row": max_row, "area": int(contact.sum()),
            "spread": int(xs.max() - xs.min())}


def _planted(points, direction):
    if not points:
        return set()
    if direction in ("south", "north"):
        lowest = max(p["row"] for p in points.values())
        return {k for k, p in points.items() if p["row"] >= lowest}
    return {"C"} if "C" in points else set()


def _sign(direction):
    return 1 if direction == "east" else -1


def foot_diagnostics(neutral_raw, walk, walk_ms, stop, direction):
    """Real-pixel footpoint displacement.  Diagnostic, never a pivot-only footlock claim."""
    neutral = png_array(neutral_raw)
    windows, ground_row = _foot_windows(neutral, direction)
    pairs = 0
    dxs, implied, slips = [], [], []
    jumps, spreads = [], []
    for index in range(len(walk) - 1):
        first, second = walk[index], walk[index + 1]
        p0 = {k: _foot_point(first, win, ground_row) for k, win in windows.items()}
        p1 = {k: _foot_point(second, win, ground_row) for k, win in windows.items()}
        common = _planted(p0, direction) & _planted(p1, direction)
        dt = float(walk_ms[index]) / 1000.0 if index < len(walk_ms) else WALK_MS / 1000.0
        for key in sorted(common):
            dx = p1[key]["x"] - p0[key]["x"]
            dxs.append(dx)
            jumps.append(abs(dx))
            spreads.append(max(p0[key]["spread"], p1[key]["spread"]))
            advance_src = SPEED * dt * DENSITY
            if direction in ("west", "east"):
                speed = -_sign(direction) * (dx / DENSITY) / dt
                implied.append(speed)
                slips.append((advance_src - (-_sign(direction) * dx)) / DENSITY)
            else:
                implied.append(0.0)
                slips.append(advance_src / DENSITY)
            pairs += 1
    stop_dx = []
    for phase in sorted(stop):
        frames = stop[phase]
        for index in range(len(frames) - 1):
            p0 = {k: _foot_point(frames[index], win, ground_row) for k, win in windows.items()}
            p1 = {k: _foot_point(frames[index + 1], win, ground_row) for k, win in windows.items()}
            for key in sorted(_planted(p0, direction) & _planted(p1, direction)):
                stop_dx.append(abs(p1[key]["x"] - p0[key]["x"]) / DENSITY)
    measured = pairs >= 4 and not any(x > 20 for x in jumps) and not any(x > 32 for x in spreads)
    mean_implied = float(np.mean(implied)) if implied else 0.0
    mean_abs_slip = float(np.mean([abs(x) for x in slips])) if slips else 0.0
    max_abs_slip = float(max([abs(x) for x in slips])) if slips else 0.0
    mean_abs_dx = float(np.mean([abs(x) for x in dxs])) if dxs else 0.0
    return {
        "direction": direction,
        "status": "measured" if measured else "not_verified",
        "reason": "" if measured else "insufficient or unstable per-foot ground landmarks",
        "method": "lowest two alpha rows per source-ground foot window; centroid x; pivot split at x=40 for south/north",
        "neutral_ground_row": ground_row,
        "windows": {k: list(v) for k, v in windows.items()},
        "walk_pairs": pairs,
        "mean_abs_dx_source": round(mean_abs_dx, 3),
        "max_abs_dx_source": round(max(jumps), 3) if jumps else None,
        "mean_implied_speed_logical": round(mean_implied, 3),
        "gait_speed_mismatch_logical": round(SPEED - mean_implied, 3),
        "in_place": bool(mean_abs_dx < 0.75),
        "mean_abs_slip_logical": round(mean_abs_slip, 3),
        "max_abs_slip_logical": round(max_abs_slip, 3),
        "residual_source_px_per_frame": round(SPEED * (WALK_MS / 1000.0) * DENSITY, 3),
        "stop_pairs": len(stop_dx),
        "stop_mean_abs_displacement_logical": round(float(np.mean(stop_dx)), 3) if stop_dx else None,
        "pivot": list(PIVOT),
        "pivot_is_not_footlock": True,
        "note": "measured in-place/gaitspeed residual only; fixed pivot is not treated as footlock",
    }


# ------------------------------------------------------------------ validation
def validate(ctx, source_path, source_data, source_dir, package_dir, runtime, registry, stop):
    checks = []
    info = {"source_manifest": {"path": str(source_path), "sha256_raw": sha_file(source_path)},
            "directions": {}, "frozen_neutrals": {}, "runtime": {}}

    def ref(entry, bases):
        return read_entry(ctx, entry, bases)

    bases = [source_dir, package_dir, source_path.parent]
    actor = source_data.get("visual_id") or source_data.get("actor_id")
    add(checks, "source.actor", actor == ACTOR, f"actor={actor!r}")
    directions = source_data.get("directions")
    add(checks, "source.directions_exact", isinstance(directions, dict) and set(directions) == set(DIRS),
        f"directions={sorted(directions) if isinstance(directions, dict) else type(directions).__name__}")
    if not isinstance(directions, dict) or set(directions) != set(DIRS):
        return finish(checks, info)

    geom = source_data.get("contract") if isinstance(source_data.get("contract"), dict) else {}
    if not geom:
        geom = source_data
    cell = geom.get("cell") or geom.get("frame_size")
    pivot = geom.get("pivot")
    density = geom.get("density")
    logical = geom.get("logical_height")
    if logical is None:
        logical = geom.get("logical_height_px")
    if logical is None and geom.get("body_texels") == 96:
        logical = 48
    add(checks, "source.contract_geometry",
        list(cell or []) == [W, H] and list(pivot or []) == list(PIVOT) and density == DENSITY and logical == LOGICAL_H,
        {"cell": cell, "pivot": pivot, "density": density, "logical_height": logical})

    # declared palette, if the source exposes one
    palette = None
    def find_palette(value, depth=0):
        if depth > 6:
            return None
        if isinstance(value, dict):
            if "colors" in value and isinstance(value["colors"], dict):
                return value["colors"]
            for child in value.values():
                hit = find_palette(child, depth + 1)
                if hit:
                    return hit
        elif isinstance(value, list):
            for child in value:
                hit = find_palette(child, depth + 1)
                if hit:
                    return hit
        return None
    palette = find_palette(source_data)
    declared_colors = None
    if isinstance(palette, dict):
        try:
            declared_colors = {tuple(bytes.fromhex(str(v).lstrip("#"))[:3]) for v in palette.values()}
        except (ValueError, TypeError):
            declared_colors = None
    add(checks, "source.declared_palette", declared_colors is None or len(declared_colors) >= 8,
        f"colors={len(declared_colors) if declared_colors else 'not_declared'}")

    frozen = frozen_neutrals(ctx)
    for direction in DIRS:
        record = frozen.get(direction)
        if not record:
            add(checks, f"neutral.{direction}.frozen_source", False, "frozen neutral manifest/PNG not found")
            continue
        add(checks, f"neutral.{direction}.frozen_source", record["ok"],
            {"manifest": record["manifest"], "png": record["png"], "declared": record["declared"],
             "actual": record["sha"]})
        info["frozen_neutrals"][direction] = {"manifest": record["manifest"], "png": record["png"],
                                              "sha256": record["sha"], "declared_ok": record["ok"]}
    if len(frozen) == 4:
        add(checks, "neutral.four_present", True, sorted(frozen))
        add(checks, "neutral.four_distinct", len({r["sha"] for r in frozen.values() if r["sha"]}) == 4,
            {d: r["sha"] for d, r in frozen.items()})
    else:
        add(checks, "neutral.four_present", False, f"found={sorted(frozen)}")

    # per-direction source checks
    direction_data = {}
    for direction in DIRS:
        bank = directions.get(direction)
        if not isinstance(bank, dict):
            add(checks, f"source.{direction}.bank", False, "direction missing")
            continue
        static = as_entries(bank.get("static"))
        idle = as_entries(bank.get("idle"))
        walk = as_entries(bank.get("walk"))
        stop_raw = bank.get("stop_bridges") or bank.get("stop") or {}
        stops = {}
        if isinstance(stop_raw, dict):
            for key, value in stop_raw.items():
                digits = "".join(ch for ch in str(key) if ch.isdigit())
                if digits.isdigit() and 0 <= int(digits) < NPH:
                    stops[int(digits)] = as_entries(value)
        add(checks, f"source.{direction}.shape",
            len(static) == 1 and len(idle) == NIDLE and len(walk) == NPH and len(stops) == NPH,
            {"static": len(static), "idle": len(idle), "walk": len(walk), "stop_phases": len(stops)})

        resolved = {}
        bad = []
        for kind, entries in [("static", static), ("idle", idle), ("walk", walk)] + \
                [("stop-p%02d" % p, [e for e in stops.get(p, []) if entry_ref(e)]) for p in range(NPH)]:
            items = [ref(entry, bases) for entry in entries]
            resolved[kind] = items
            for item in items:
                if not item["ok"] or not item["hash_ok"]:
                    bad.append({"kind": kind, "ref": item.get("ref"), "path": str(item.get("path")),
                                "error": item.get("error"), "declared": item.get("declared"),
                                "actual": item.get("sha")})
        add(checks, f"source.{direction}.refs_exist_and_raw_hash", not bad, bad[:6])

        # durations
        static_ms = static[0].get("duration_ms") if static else None
        idle_ms = [e.get("duration_ms") for e in idle]
        walk_ms = [e.get("duration_ms") for e in walk]
        stop_ms = [e.get("duration_ms") for p in range(NPH) for e in stops.get(p, []) if entry_ref(e)]
        add(checks, f"source.{direction}.durations",
            (static_ms is None or (num(static_ms) and static_ms > 0)) and positive_durations(idle_ms) and
            positive_durations(walk_ms) and positive_durations(stop_ms),
            {"static": static_ms, "idle": idle_ms, "walk": walk_ms, "stop": stop_ms[:4]})
        add(checks, f"source.{direction}.walk_40ms", len(walk_ms) == NPH and all(abs(float(v) - WALK_MS) < 1e-9 for v in walk_ms),
            walk_ms)

        # stop endpoint semantics
        endpoint_bad = []
        for phase in range(NPH):
            bridge = stops.get(phase, [])
            if len(bridge) != 4:
                endpoint_bad.append((phase, "length", len(bridge)))
                continue
            first, last = bridge[0], bridge[-1]
            if not (isinstance(first, dict) and str(first.get("ref", "")).lower() == "walk" and
                    int(first.get("index", -1)) == phase and float(first.get("k", -1)) == 0.0):
                endpoint_bad.append((phase, "start", first))
            if not (isinstance(last, dict) and str(last.get("ref", "")).lower() == "idle" and
                    int(last.get("index", -1)) == 0 and float(last.get("k", -1)) == 1.0):
                endpoint_bad.append((phase, "end", last))
        add(checks, f"source.{direction}.stop_endpoints", not endpoint_bad, endpoint_bad[:4])

        # real pixels
        all_items = [(k, item) for k, items in resolved.items() for item in items if item["ok"]]
        pixel_bad, neutral_bad, bounds_bad, palette_bad = [], [], [], []
        idle_hashes, walk_lower = [], set()
        for kind, item in all_items:
            try:
                metrics = image_metrics(item["bytes"])
            except Exception as exc:
                pixel_bad.append((kind, item.get("ref"), type(exc).__name__))
                continue
            bbox = metrics["bbox"]
            if metrics["size"] != (W, H) or not metrics["alpha"] <= {0, 255} or metrics["border"] or bbox is None:
                pixel_bad.append((kind, item.get("ref"), {"size": metrics["size"], "alpha": metrics["alpha"],
                                                          "border": metrics["border"], "bbox": bbox}))
            if bbox:
                height = bbox[3] - bbox[1] + 1
                if bbox[3] > PIVOT[1] or bbox[3] < 96 or height > 97:
                    bounds_bad.append((kind, item.get("ref"), bbox, height))
                if kind in ("static", "idle") and not (7 <= bbox[1] <= 9 and 103 <= bbox[3] <= 104 and 95 <= height <= 97):
                    neutral_bad.append((kind, item.get("ref"), bbox, height))
            if len(metrics["colors"]) > 48 or (declared_colors is not None and not metrics["colors"] <= declared_colors):
                palette_bad.append((kind, item.get("ref"), len(metrics["colors"])))
            if kind == "idle":
                idle_hashes.append(item["sha"])
            if kind == "walk":
                walk_lower.add(metrics["array"][78:104].tobytes())
        add(checks, f"png.{direction}.native_80x112_binary_alpha_border", not pixel_bad, pixel_bad[:4])
        add(checks, f"png.{direction}.neutral_body_96_logical", not neutral_bad, neutral_bad[:4])
        add(checks, f"png.{direction}.motion_bounds", not bounds_bad, bounds_bad[:4])
        add(checks, f"png.{direction}.palette_le_48_and_declared", not palette_bad, palette_bad[:4])
        add(checks, f"png.{direction}.idle_not_duplicate", len(set(idle_hashes)) >= 3, len(set(idle_hashes)))
        add(checks, f"png.{direction}.walk_lower_body_changes", len(walk_lower) >= 6, len(walk_lower))

        # frozen neutral equality, all four neutral and stop endpoints
        frozen_record_d = frozen.get(direction)
        static_bytes = resolved["static"][0]["bytes"] if resolved.get("static") and resolved["static"][0]["ok"] else None
        idle0_bytes = resolved["idle"][0]["bytes"] if resolved.get("idle") and resolved["idle"][0]["ok"] else None
        if frozen_record_d and static_bytes is not None and idle0_bytes is not None:
            add(checks, f"neutral.{direction}.static_frozen", sha(static_bytes) == frozen_record_d["sha"],
                {"source": sha(static_bytes), "frozen": frozen_record_d["sha"]})
            add(checks, f"neutral.{direction}.idle_f00_frozen", sha(idle0_bytes) == frozen_record_d["sha"],
                {"source": sha(idle0_bytes), "frozen": frozen_record_d["sha"]})
            stop_ok = True
            stop_detail = []
            for phase in range(NPH):
                bridge = stops.get(phase, [])
                if len(bridge) < 2:
                    stop_ok = False
                    continue
                last = bridge[-1]
                if isinstance(last, dict) and str(last.get("ref", "")).lower() == "idle":
                    stop_detail.append((phase, "ref-idle0"))
                elif entry_ref(last):
                    item = ref(last, bases)
                    if not item["ok"] or sha(item["bytes"]) != frozen_record_d["sha"]:
                        stop_ok = False
                        stop_detail.append((phase, "file-mismatch"))
                else:
                    stop_ok = False
                    stop_detail.append((phase, "no-endpoint"))
            add(checks, f"neutral.{direction}.stop_endpoints_frozen", stop_ok, stop_detail[:4])

        direction_data[direction] = {"resolved": resolved, "stops": stops, "static": static,
                                      "idle": idle, "walk": walk, "walk_ms": walk_ms}

    # PXO / ORA
    for direction in DIRS:
        bank = directions.get(direction, {})
        data_d = direction_data.get(direction)
        if not data_d:
            continue
        pxo_entry = bank.get("pxo")
        ora_entry = bank.get("ora")
        static_bytes = data_d["resolved"]["static"][0]["bytes"] if data_d["resolved"].get("static") else None

        # PXO order: static, idle, walk, then stop intermediates
        order = [item for item in data_d["resolved"].get("static", []) if item["ok"]]
        order += [item for item in data_d["resolved"].get("idle", []) if item["ok"]]
        order += [item for item in data_d["resolved"].get("walk", []) if item["ok"]]
        for phase in range(NPH):
            order += [item for item in data_d["resolved"].get("stop-p%02d" % phase, []) if item["ok"]]
        pxo_result = validate_pxo(ctx, direction, pxo_entry, order, data_d, bases, checks)
        if pxo_result:
            info["directions"][direction] = {"pxo": pxo_result}
        validate_ora(ctx, direction, ora_entry, static_bytes, bases, checks)

    # runtime package
    validate_runtime(ctx, source_data, source_path, package_dir, runtime, registry, stop,
                     direction_data, frozen, checks, info)

    # contact diagnostics
    for direction in DIRS:
        data_d = direction_data.get(direction)
        frozen_record_d = frozen.get(direction)
        if not data_d or not frozen_record_d:
            add(checks, f"contact.{direction}.diagnostic", True,
                {"status": "not_verified", "reason": "source or frozen neutral unavailable"}, status="not_verified")
            continue
        try:
            walk = [item["bytes"] for item in data_d["resolved"].get("walk", []) if item["ok"]]
            stop_frames = {}
            for phase in range(NPH):
                stop_frames[phase] = [item["bytes"] for item in data_d["resolved"].get("stop-p%02d" % phase, []) if item["ok"]]
            diag = foot_diagnostics(frozen_record_d["bytes"], walk, data_d["walk_ms"], stop_frames, direction)
        except Exception as exc:
            diag = {"direction": direction, "status": "not_verified", "reason": type(exc).__name__,
                    "pivot": list(PIVOT), "pivot_is_not_footlock": True}
        info["directions"].setdefault(direction, {})["contact"] = diag
        add(checks, f"contact.{direction}.diagnostic", True, diag, status=diag["status"])
        add(checks, f"contact.{direction}.pivot_not_footlock", True,
            "fixed pivot is not accepted as proof of footlock")
        claims = find_slip_claim(source_data)
        if diag["status"] == "measured" and diag["max_abs_slip_logical"] > 1.0 and claims is not None:
            add(checks, f"contact.{direction}.disclosure_not_false", claims > 0.5,
                {"measured_max_abs_slip_logical": diag["max_abs_slip_logical"], "declared": claims})

    return finish(checks, info)


def find_slip_claim(value, depth=0):
    if depth > 8:
        return None
    if isinstance(value, dict):
        for key, child in value.items():
            low = key.lower()
            if low in ("footlock", "foot_lock") and child is True:
                return 0.0
            if isinstance(child, (int, float)) and not isinstance(child, bool) and \
                    ("max_abs_slip" in low or "world_drift_per_phase_logical" in low or
                     "mean_abs_slip" in low):
                return float(child)
            hit = find_slip_claim(child, depth + 1)
            if hit is not None:
                return hit
    elif isinstance(value, list):
        for child in value:
            hit = find_slip_claim(child, depth + 1)
            if hit is not None:
                return hit
    return None


def validate_pxo(ctx, direction, entry, order, data_d, bases, checks):
    item = read_entry(ctx, entry, bases) if entry else {"ok": False, "error": "no-pxo-entry"}
    add(checks, f"pxo.{direction}.raw_hash", item["ok"] and item["hash_ok"],
        {"ref": item.get("ref"), "declared": item.get("declared"), "actual": item.get("sha")})
    if not item["ok"]:
        return None
    try:
        z = zipfile.ZipFile(io.BytesIO(item["bytes"]))
    except (zipfile.BadZipFile, OSError) as exc:
        add(checks, f"pxo.{direction}.archive", False, type(exc).__name__)
        return None
    with z:
        try:
            data = load_json(z.read("data.json"))
        except (KeyError, ValueError) as exc:
            add(checks, f"pxo.{direction}.archive", False, "data.json " + type(exc).__name__)
            return None
        layers = data.get("layers", [])
        names = [str(layer.get("name", "")) for layer in layers]
        role_names = [n for n in names if n.lower() not in ("guides", "guide") and "guide" not in n.lower()]
        guide_ok = any("guide" in n.lower() and not layers[i].get("visible", True) for i, n in enumerate(names))
        layer_ok = (data.get("size_x") == W and data.get("size_y") == H and
                    set(role_names) in (set(ROLE_NAMES), set(ROLE_NAMES) | {"far-limbs"}) and
                    len(layers) == len(role_names) + 1 and guide_ok and
                    all(layer.get("visible", True) and float(layer.get("opacity", 1.0)) == 1.0 and
                        int(layer.get("blend_mode", 0)) == 0 for layer in layers
                        if "guide" not in str(layer.get("name", "")).lower()))
        add(checks, f"pxo.{direction}.nine_role_layers_plus_hidden_guides", layer_ok,
            {"layers": names, "size": [data.get("size_x"), data.get("size_y")]})

        frames = data.get("frames", [])
        frame_ok = len(frames) == len(order) and len(order) > 0
        compose_bad = []
        for number, expected in enumerate(order, start=1):
            try:
                comp = pxo_compose(z, data, number)
                if not np.array_equal(comp, png_array(expected["bytes"])):
                    compose_bad.append(number)
            except (KeyError, OSError, ValueError) as exc:
                compose_bad.append((number, type(exc).__name__))
        add(checks, f"pxo.{direction}.frame_count", frame_ok, {"pxo": len(frames), "expected": len(order)})
        add(checks, f"pxo.{direction}.per_frame_9role_composition", not compose_bad, compose_bad[:6])

        # tags derived from the manifest order
        tags = data.get("tags", [])
        spans = sorted({(int(t.get("from", 0)), int(t.get("to", 0))) for t in tags if isinstance(t, dict)})
        expected_spans = []
        cursor = 2  # frame 1 is static
        if data_d["resolved"].get("idle"):
            expected_spans.append(("idle", cursor, cursor + len(data_d["resolved"]["idle"]) - 1))
            cursor += len(data_d["resolved"]["idle"])
        if data_d["resolved"].get("walk"):
            expected_spans.append(("walk", cursor, cursor + len(data_d["resolved"]["walk"]) - 1))
            cursor += len(data_d["resolved"]["walk"])
        for phase in range(NPH):
            files = [x for x in data_d["resolved"].get("stop-p%02d" % phase, []) if x["ok"]]
            if files:
                expected_spans.append(("stop-p%02d" % phase, cursor, cursor + len(files) - 1))
                cursor += len(files)
        tag_bad = [list(span) for span in expected_spans if (span[1], span[2]) not in spans]
        overlap = any(b[0] <= a[1] for a, b in zip(spans, spans[1:]))
        add(checks, f"pxo.{direction}.tags", not tag_bad and not overlap,
            {"expected": expected_spans, "actual": spans, "missing": tag_bad, "overlap": overlap})
        durations = [frame.get("duration") for frame in frames]
        add(checks, f"pxo.{direction}.frame_durations_positive", positive_durations(durations),
            {"count": len(durations), "min": min(durations) if durations else None,
             "max": max(durations) if durations else None})
        raw_data = z.read("data.json")
        add(checks, f"pxo.{direction}.metadata", b"protagonist-male" not in raw_data,
            "no male actor metadata")
        return {"layers": names, "frames": len(frames), "tags": len(tags)}


def validate_ora(ctx, direction, entry, static_bytes, bases, checks):
    item = read_entry(ctx, entry, bases) if entry else {"ok": False, "error": "no-ora-entry"}
    add(checks, f"ora.{direction}.raw_hash", item["ok"] and item["hash_ok"],
        {"ref": item.get("ref"), "declared": item.get("declared"), "actual": item.get("sha")})
    if not item["ok"] or static_bytes is None:
        return
    try:
        z = zipfile.ZipFile(io.BytesIO(item["bytes"]))
    except (zipfile.BadZipFile, OSError) as exc:
        add(checks, f"ora.{direction}.archive", False, type(exc).__name__)
        return
    with z:
        try:
            layers = ora_layers(z)
        except (KeyError, ET.ParseError) as exc:
            add(checks, f"ora.{direction}.archive", False, type(exc).__name__)
            return
        names = [layer["name"] for layer in layers]
        roles = [n for n in names if "guide" not in n.lower()]
        nonempty = 0
        for layer in layers:
            if layer["visible"] and layer["src"]:
                try:
                    alpha = np.array(Image.open(io.BytesIO(z.read(layer["src"]))).convert("RGBA"))[..., 3]
                    if int(np.count_nonzero(alpha)) >= 8:
                        nonempty += 1
                except OSError:
                    pass
        guide_ok = any("guide" in n.lower() and not layers[i]["visible"] for i, n in enumerate(names))
        add(checks, f"ora.{direction}.nine_roles_hidden_guides",
            len(roles) == len(ROLE_NAMES) and set(roles) == set(ROLE_NAMES) and guide_ok and nonempty == 9,
            {"layers": names, "nonempty": nonempty, "hidden_guide": guide_ok})
        try:
            comp = compose_ora(z, layers)
            merged = np.array(Image.open(io.BytesIO(z.read("mergedimage.png"))).convert("RGBA"))
            expected = png_array(static_bytes)
            add(checks, f"ora.{direction}.static_composition", np.array_equal(comp, expected),
                "visible role layers recompose to frozen static")
            add(checks, f"ora.{direction}.merged_equals_static", np.array_equal(merged, expected),
                "mergedimage.png equals static")
        except (KeyError, OSError, ValueError) as exc:
            add(checks, f"ora.{direction}.static_composition", False, type(exc).__name__)
        infos = z.infolist()
        add(checks, f"ora.{direction}.mimetype_first_stored",
            bool(infos) and infos[0].filename == "mimetype" and infos[0].compress_type == zipfile.ZIP_STORED,
            [infos[0].filename, infos[0].compress_type] if infos else [])


def validate_runtime(ctx, source_data, source_path, package_dir, runtime, registry, stop,
                     direction_data, frozen, checks, info):
    package = source_data.get("package") if isinstance(source_data.get("package"), dict) else {}

    def pick(key, collection, name_hint=None):
        declared = package.get(key)
        if isinstance(declared, str):
            p = ctx.resolve(declared, [ctx.root, package_dir])
            for path, data in collection:
                if ctx.key(path) == ctx.key(p):
                    return path, data
            if ctx.exists(p):
                try:
                    return p, load_json(ctx.read(p))
                except (OSError, ValueError):
                    pass
        if name_hint:
            for path, data in collection:
                if name_hint in path.name.lower():
                    return path, data
        return collection[0] if collection else (None, None)

    runtime_path, runtime_data = pick("sprite_set", runtime, "sprite-set")
    registry_path, registry_data = pick("registry", registry, "registry")
    stop_path, stop_data = pick("stop_supplemental", stop, "stop")

    if runtime_path is None or runtime_data is None:
        add(checks, "runtime.sprite_set_present", False, "no runtime sprite-set manifest")
        return
    add(checks, "runtime.sprite_set_present", True, str(runtime_path))
    info["runtime"] = {"sprite_set": str(runtime_path), "sha256_raw": sha_file(runtime_path),
                       "registry": str(registry_path) if registry_path else None,
                       "stop_supplemental": str(stop_path) if stop_path else None}
    add(checks, "runtime.schema_actor_geometry",
        runtime_data.get("schema") == "worlds-between.exploration-sprite-set.v1" and
        runtime_data.get("actor_id") == ACTOR and runtime_data.get("density") == DENSITY and
        list(runtime_data.get("frame_size") or []) == [W, H] and list(runtime_data.get("pivot") or []) == list(PIVOT),
        {"schema": runtime_data.get("schema"), "actor": runtime_data.get("actor_id"),
         "density": runtime_data.get("density"), "frame_size": runtime_data.get("frame_size"),
         "pivot": runtime_data.get("pivot")})
    actions = runtime_data.get("actions")
    allowed = {"static", "idle", "walk", "stop"}
    action_shape = isinstance(actions, dict) and set(actions) <= allowed and {"idle", "walk"} <= set(actions) and \
        all(isinstance(actions[a], dict) and set(actions[a]) == set(DIRS) for a in actions)
    add(checks, "runtime.actions_directions", action_shape,
        f"actions={sorted(actions) if isinstance(actions, dict) else type(actions).__name__}")
    if not action_shape:
        return

    copy_bad, count_bad, duration_bad = [], [], []
    for direction in DIRS:
        source_bank = direction_data.get(direction, {})
        runtime_bank = actions.get("idle", {}).get(direction, []) if "idle" in actions else []
        for action, src_key, expected_count in [("idle", "idle", NIDLE), ("walk", "walk", NPH)]:
            src_items = source_bank.get("resolved", {}).get(src_key, [])
            dst_entries = as_entries(actions[action].get(direction))
            if len(src_items) != expected_count or len(dst_entries) != expected_count:
                count_bad.append((direction, action, len(src_items), len(dst_entries), expected_count))
            src_ms = [e.get("duration_ms") for e in source_bank.get(src_key, [])]
            dst_ms = [e.get("duration_ms") for e in dst_entries]
            if not positive_durations(dst_ms) or src_ms != dst_ms:
                duration_bad.append((direction, action, src_ms, dst_ms))
            for index, (src_item, dst_entry) in enumerate(zip(src_items, dst_entries)):
                ref = entry_ref(dst_entry)
                if not ref or Path(ref).is_absolute() or ".." in Path(ref).parts:
                    copy_bad.append((direction, action, index, "bad-relative-path", ref))
                    continue
                dst_path = runtime_path.parent / ref
                if not ctx.exists(dst_path):
                    copy_bad.append((direction, action, index, "missing", ref))
                    continue
                if not src_item["ok"] or sha(ctx.read(dst_path)) != src_item["sha"]:
                    copy_bad.append((direction, action, index, "bytes-differ", ref))
        if "static" in actions:
            dst = as_entries(actions["static"].get(direction))
            if len(dst) != 1:
                count_bad.append((direction, "static", 1, len(dst), 1))
            elif source_bank.get("resolved", {}).get("static"):
                src_item = source_bank["resolved"]["static"][0]
                ref = entry_ref(dst[0])
                dst_path = runtime_path.parent / ref if ref else None
                if not ref or not src_item.get("ok") or not ctx.exists(dst_path) or \
                        sha(ctx.read(dst_path)) != src_item["sha"]:
                    copy_bad.append((direction, "static", 0, "bytes-or-path", ref))
        if "stop" in actions:
            dst = as_entries(actions["stop"].get(direction))
            if len(dst) != 24:
                count_bad.append((direction, "stop", 24, len(dst), 24))
    add(checks, "runtime.frame_counts", not count_bad, count_bad[:6])
    add(checks, "runtime.durations", not duration_bad, duration_bad[:6])
    add(checks, "runtime.lossless_png_copies", not copy_bad, copy_bad[:8])

    if runtime_data.get("frame_size") is not None:
        add(checks, "runtime.logical_height", list(runtime_data.get("frame_size") or []) == [W, H] and
            runtime_data.get("pivot") == list(PIVOT), "80x112 / pivot 40,104")

    if registry_path is None or registry_data is None:
        add(checks, "runtime.registry", False, "no registry")
    else:
        actors = registry_data.get("actors")
        target = runtime_path.name
        add(checks, "runtime.registry",
            registry_data.get("schema") == "worlds-between.exploration-sprite-set-registry.v1" and
            isinstance(actors, dict) and list(actors) == [ACTOR] and actors.get(ACTOR) == target,
            {"actors": actors, "runtime": target})

    if stop_path is None or stop_data is None:
        add(checks, "runtime.stop_supplemental", False, "no stop supplemental")
    else:
        add(checks, "runtime.stop_schema",
            stop_data.get("schema") == "worlds-between.exploration-stop-transition.supplemental.v1" and
            stop_data.get("actor_id") == ACTOR and list(stop_data.get("pivot") or []) == list(PIVOT) and
            stop_data.get("logical_height") == LOGICAL_H and num(stop_data.get("frame_ms")) and
            float(stop_data.get("frame_ms")) == WALK_MS,
            {"schema": stop_data.get("schema"), "actor": stop_data.get("actor_id"),
             "pivot": stop_data.get("pivot"), "logical_height": stop_data.get("logical_height"),
             "frame_ms": stop_data.get("frame_ms")})
        bridges = stop_data.get("phase_bridges")
        bad = []
        if not isinstance(bridges, dict) or set(bridges) != set(DIRS):
            bad.append(("directions", sorted(bridges) if isinstance(bridges, dict) else None))
        else:
            for direction in DIRS:
                phases = bridges.get(direction, {})
                normalized = {}
                if isinstance(phases, dict):
                    for key, value in phases.items():
                        digits = "".join(ch for ch in str(key) if ch.isdigit())
                        if digits.isdigit():
                            normalized[int(digits)] = as_entries(value)
                if set(normalized) != set(range(NPH)):
                    bad.append((direction, "phases", sorted(normalized)))
                    continue
                for phase in range(NPH):
                    source_bridge = direction_data.get(direction, {}).get("stops", {}).get(phase, [])
                    dst_entries = normalized[phase]
                    if len(source_bridge) != 4 or len(dst_entries) != 4:
                        bad.append((direction, phase, "length", len(source_bridge), len(dst_entries)))
                        continue
                    for index in (0, 3):
                        def endpoint(value):
                            return (str(value.get("ref", "")).lower(), value.get("index"), float(value.get("k", -1)))
                        if endpoint(source_bridge[index]) != endpoint(dst_entries[index]):
                            bad.append((direction, phase, index, "endpoint"))
                    for index in (1, 2):
                        src = source_bridge[index]
                        dst = dst_entries[index]
                        if src.get("k") != dst.get("k"):
                            bad.append((direction, phase, index, "k"))
                        ref = entry_ref(dst)
                        src_item = direction_data[direction]["resolved"].get("stop-p%02d" % phase, [])
                        if not ref:
                            bad.append((direction, phase, index, "no-file"))
                            continue
                        dst_path = stop_path.parent / ref
                        if not ctx.exists(dst_path):
                            bad.append((direction, phase, index, "missing"))
                        elif not src_item or sha(ctx.read(dst_path)) != src_item[index - 1]["sha"]:
                            bad.append((direction, phase, index, "bytes"))
                        if dst.get("sha256") and src_item and dst["sha256"] != src_item[index - 1]["sha"]:
                            bad.append((direction, phase, index, "sha"))
        add(checks, "runtime.stop_bridges", not bad, bad[:8])

    if isinstance(package.get("sprite_set_sha256"), str):
        add(checks, "runtime.sprite_set_sha256", package["sprite_set_sha256"] == sha_file(runtime_path),
            "declared raw hash")
    if isinstance(package.get("stop_supplemental_sha256_text_lf_v1"), str) and stop_path:
        add(checks, "runtime.stop_sha256_lf", package["stop_supplemental_sha256_text_lf_v1"] ==
            sha(ctx.read(stop_path).replace(b"\r\n", b"\n")), "declared LF-normalized hash")
    add(checks, "runtime.no_gdignore",
        not ctx.exists(package_dir / ".gdignore") and not ctx.exists(package_dir / "png/.gdignore"),
        "no .gdignore in runtime package")


def finish(checks, info):
    failed = [c for c in checks if not c["ok"]]
    return {"status": "pass" if not failed else "fail", "checks": checks,
            "failed": [c["id"] for c in failed], "details": info}


# -------------------------------------------------------------------- selftest
def _gate_hash(manifest, base):
    entry = manifest["frame"]
    path = Path(base) / entry["file"]
    return path.is_file() and sha(path.read_bytes()) == entry["sha256"]


def _gate_present(manifest, base):
    return (Path(base) / manifest["frame"]["file"]).is_file()


def _gate_duration(manifest):
    return positive_durations(manifest["durations"])


def _frozen_role_selftest(ctx, frozen):
    results = {}
    for direction in DIRS:
        record = frozen.get(direction)
        if not record or not record.get("bytes"):
            results[direction] = {"status": "not_verified", "reason": "frozen PNG absent"}
            continue
        expected = png_array(record["bytes"])
        entry_data = frozen_record_paths(ctx, direction)
        pxo_ok = ora_ok = False
        detail = {}
        if entry_data.get("pxo"):
            try:
                with zipfile.ZipFile(io.BytesIO(ctx.read(entry_data["pxo"]))) as z:
                    data = load_json(z.read("data.json"))
                    names = [layer["name"] for layer in data.get("layers", [])]
                    comp = pxo_compose(z, data, 1)
                    pxo_ok = names[:len(ROLE_NAMES)] == list(ROLE_NAMES) and names[-1:] == ["guides"] and \
                        not data["layers"][-1].get("visible", True) and np.array_equal(comp, expected)
                    detail["pxo_layers"] = names
            except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
                detail["pxo_error"] = type(exc).__name__
        if entry_data.get("ora"):
            try:
                with zipfile.ZipFile(io.BytesIO(ctx.read(entry_data["ora"]))) as z:
                    layers = ora_layers(z)
                    names = [layer["name"] for layer in layers]
                    comp = compose_ora(z, layers)
                    merged = np.array(Image.open(io.BytesIO(z.read("mergedimage.png"))).convert("RGBA"))
                    ora_ok = set(names) == set(ROLE_NAMES) | {"guides"} and \
                        any("guide" in n.lower() and not layers[i]["visible"] for i, n in enumerate(names)) and \
                        np.array_equal(comp, expected) and np.array_equal(merged, expected)
                    detail["ora_layers"] = names
            except (OSError, KeyError, ET.ParseError, ValueError, zipfile.BadZipFile) as exc:
                detail["ora_error"] = type(exc).__name__
        results[direction] = {"status": "pass" if pxo_ok and ora_ok else "fail",
                              "pxo_9_role_composition": pxo_ok, "ora_hidden_guide_static_composition": ora_ok,
                              "detail": detail}
    return results


def frozen_record_paths(ctx, direction):
    """Resolve the PXO/ORA next to the selected frozen neutral manifest."""
    root = ctx.root
    if direction == "south":
        folder = root / "game/assets/characters/jiang-lan-native-south-v01"
        manifests = sorted(folder.glob("*manifest*.json"))
    else:
        folder = root / f"game/assets/characters/jiang-lan-native-directions-v01/{direction}"
        manifests = sorted(folder.glob(f"*_{direction}-manifest_*.json")) or sorted(folder.glob(f"*{direction}*manifest*.json"))
    for path in manifests:
        try:
            data = load_json(ctx.read(path))
        except (OSError, ValueError):
            continue
        files = data.get("files") if isinstance(data, dict) else None
        if not isinstance(files, dict):
            continue
        pxo = files.get("pxo", {}).get("file")
        ora = files.get("ora", {}).get("file")
        return {"pxo": ctx.resolve(pxo, [folder]) if pxo else None,
                "ora": ctx.resolve(ora, [folder]) if ora else None}
    return {}


def run_selftest(ctx, out_dir, uid):
    frozen = frozen_neutrals(ctx)
    role_results = _frozen_role_selftest(ctx, frozen)
    cases = []
    temp_root = out_dir / (".selftest-" + uid)
    temp_root.mkdir(parents=True, exist_ok=True)
    marker = temp_root / ".jexplore39-selftest"
    write_file(marker, (TAG + "-" + uid).encode())
    cleanup = {"target": str(temp_root), "marker": str(marker), "removed": False}
    try:
        source_png = next((record["bytes"] for record in frozen.values() if record.get("bytes")), None)
        selected = next((d for d, record in frozen.items() if record.get("bytes")), None)
        if source_png is None:
            cases.append({"id": "fixture", "passed": False, "reason": "frozen neutral PNG unavailable"})
        else:
            frame = temp_root / "frame.png"
            frame.write_bytes(source_png)
            manifest = {"frame": {"file": "frame.png", "sha256": sha(source_png)},
                        "durations": [700, 200, 400, 200]}
            clean = {"hash": _gate_hash(manifest, temp_root), "present": _gate_present(manifest, temp_root),
                     "duration": _gate_duration(manifest)}
            cases.append({"id": "clean-control", "expected": "accept", "passed": all(clean.values()),
                          "observed": clean})
            wrong = copy.deepcopy(manifest)
            wrong["frame"]["sha256"] = "0" * 64
            observed = _gate_hash(wrong, temp_root)
            cases.append({"id": "wrong-hash", "expected": "refuse", "passed": not observed,
                          "observed": observed, "mutation": "temporary manifest hash flipped"})
            frame.unlink()
            observed = _gate_present(manifest, temp_root)
            cases.append({"id": "missing-frame", "expected": "refuse", "passed": not observed,
                          "observed": observed, "mutation": "temporary frame copy removed"})
            frame.write_bytes(source_png)
            zero = copy.deepcopy(manifest)
            zero["durations"][0] = 0
            observed = _gate_duration(zero)
            cases.append({"id": "zero-duration", "expected": "refuse", "passed": not observed,
                          "observed": observed, "mutation": "temporary manifest duration set to 0"})
            cases.append({"id": "source-untouched", "expected": "unchanged",
                          "passed": sha(source_png) == frozen[selected]["sha"] if selected else False,
                          "observed": "fixture used copies only"})
    finally:
        try:
            marker_ok = marker.is_file() and marker.read_text(encoding="utf-8").strip() == TAG + "-" + uid
            within = os.path.commonpath([str(temp_root), str(out_dir)]) == str(out_dir)
            if marker_ok and within:
                shutil.rmtree(str(lp(temp_root)))
                cleanup["removed"] = not temp_root.exists()
        except OSError:
            cleanup["removed"] = False
    passed = all(case.get("passed") for case in cases) and all(
        item.get("status") == "pass" for item in role_results.values()) if role_results else False
    return {
        "schema": "worlds-between.jiang-lan.independent-explore-source-check.selftest.v1",
        "status": "pass" if passed else "fail",
        "actor": ACTOR,
        "cases": cases,
        "frozen_role_checks": role_results,
        "cleanup": cleanup,
        "source_touched": False,
        "limitations": ["Selftest uses existing frozen neutral assets and temporary copies only.",
                        "It does not approve art, motion or runtime integration."],
    }


# ----------------------------------------------------------------------- main
def find_runtime_for_pending(ctx, package_dir):
    located = locate_package(ctx, package_dir)
    return located["runtime"][0][1] if located["runtime"] else None


def output_name(purpose, uid, ext):
    stem = f"{PROJECT}_{ACTOR}_independent-explore-source-check"
    if purpose:
        stem += "_" + purpose
    return f"{stem}_v01_{TAG}-{uid}.{ext}"


def main():
    global ACTOR
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", required=True)
    parser.add_argument("--actor", default=ACTOR)
    parser.add_argument("--source-rel", default=SOURCE_REL)
    parser.add_argument("--package-rel", default=PACKAGE_REL)
    args = parser.parse_args()
    ACTOR = args.actor
    root = Path(args.root).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    ctx = Ctx(root)
    uid = uuid.uuid4().hex[:8]
    started = utc_now()
    source_dir = root / args.source_rel
    package_dir = root / args.package_rel
    selftest = run_selftest(ctx, out, uid)
    selftest_path = out / output_name("selftest", uid, "json")
    write_json(selftest_path, selftest)

    source_candidates = locate_source(ctx, source_dir)
    runtime_pending = find_runtime_for_pending(ctx, package_dir)
    if not source_candidates and runtime_pending is None:
        report = {
            "schema": "worlds-between.jiang-lan.independent-explore-source-check.v1",
            "status": "pending-source",
            "actor": ACTOR,
            "root": str(root),
            "startedUtc": started,
            "finishedUtc": utc_now(),
            "source": {"expected": str(source_dir), "present": False},
            "package": {"expected": str(package_dir), "present": bool(package_dir.exists())},
            "checks": [{"id": "source.present", "ok": False, "status": "pending",
                        "detail": f"no source manifest under {source_dir}"},
                       {"id": "package.present", "ok": False, "status": "pending",
                        "detail": f"no runtime package under {package_dir}"}],
            "frozen_neutrals": {d: {"png": r["png"], "sha256": r["sha"]} for d, r in frozen_neutrals(ctx).items()},
            "selftest": {"path": str(selftest_path), "status": selftest["status"]},
            "approval": "unapproved technical source only; no art/motion/creator approval",
            "limitations": ["Target source was not produced at run time; ROOT must rerun after production.",
                            "No source/package/producer files were written."],
        }
        report_path = out / output_name("", uid, "json")
        write_json(report_path, report)
        note_path = out / output_name("qa-note", uid, "md")
        write_file(note_path, pending_note(report, report_path, selftest_path).encode("utf-8"))
        print("JEXPLORE39_INDEPENDENT PENDING_SOURCE", str(report_path), str(selftest_path))
        return 2

    if not source_candidates:
        report = {"schema": "worlds-between.jiang-lan.independent-explore-source-check.v1",
                  "status": "fail", "actor": ACTOR, "root": str(root), "startedUtc": started,
                  "finishedUtc": utc_now(), "source": {"expected": str(source_dir), "present": False},
                  "package": {"expected": str(package_dir), "present": runtime_pending is not None},
                  "checks": [{"id": "source.present", "ok": False, "status": "fail",
                              "detail": "package exists but source manifest is absent"}],
                  "selftest": {"path": str(selftest_path), "status": selftest["status"]},
                  "approval": "unapproved technical source only"}
        report_path = out / output_name("", uid, "json")
        write_json(report_path, report)
        print("JEXPLORE39_INDEPENDENT FAIL source-manifest-missing", str(report_path))
        return 1

    source_path, source_data = source_candidates[0]
    located = locate_package(ctx, package_dir)
    result = validate(ctx, source_path, source_data, source_dir, package_dir,
                      located["runtime"], located["registry"], located["stop"])
    if selftest["status"] != "pass":
        result["checks"].append({"id": "selftest", "ok": False, "status": "fail",
                                 "detail": "checker selftest failed"})
        result["status"] = "fail"
    result.update({
        "schema": "worlds-between.jiang-lan.independent-explore-source-check.v1",
        "actor": ACTOR, "root": str(root), "startedUtc": started, "finishedUtc": utc_now(),
        "source": {"path": str(source_path), "sha256_raw": sha_file(source_path)},
        "package": {"dir": str(package_dir)},
        "selftest": {"path": str(selftest_path), "status": selftest["status"]},
        "checker": {"path": str(Path(__file__).resolve()), "sha256_raw": sha_file(__file__)},
        "approval": "unapproved technical source only; no art/motion/creator approval",
        "limitations": ["This checks the declared native source/package contract, not GUI application diagnostics.",
                        "Contact/slip is a pixel-derived diagnostic; not_verified is reported honestly.",
                        "No runtime integration, art approval or full motion acceptance is claimed."],
    })
    report_path = out / output_name("", uid, "json")
    write_json(report_path, result)
    note_path = out / output_name("qa-note", uid, "md")
    write_file(note_path, result_note(result, report_path, selftest_path).encode("utf-8"))
    passed = result["status"] == "pass"
    print("JEXPLORE39_INDEPENDENT", result["status"].upper(),
          f"{sum(1 for c in result['checks'] if c['ok'])}/{len(result['checks'])}",
          str(report_path))
    for check in result["checks"]:
        if not check["ok"]:
            print("FAIL", check["id"], check.get("detail"))
    return 0 if passed else 1


def pending_note(report, report_path, selftest_path):
    return "\n".join([
        "# Jiang Lan exploration source - independent validator",
        "",
        f"- Status: **{report['status']}** (exit 2)",
        f"- Root: `{report['root']}`",
        f"- Expected source: `{report['source']['expected']}`",
        f"- Expected package: `{report['package']['expected']}`",
        f"- Main report: `{report_path}`",
        f"- Checker selftest: `{selftest_path}` ({report['selftest']['status']})",
        "",
        "## What was checked",
        "",
        "- Pending-source discovery only; no target author was imported or run.",
        "- Existing four Jiang Lan frozen neutral statics were inventoried and selftested.",
        "- Temporary-copy refusal gates: wrong hash, missing frame, zero duration.",
        "",
        "## Limitations",
        "",
        "- Target source is absent, so no actual manifest/PXO/ORA/foot diagnostics were run.",
        "- ROOT must rerun this checker after the producer writes `outputs/jexplore39` and `game/data/jexplore39`.",
        "- No art, motion, runtime integration or creator approval is claimed.",
        "",
    ])


def result_note(result, report_path, selftest_path):
    failed = [c for c in result["checks"] if not c["ok"]]
    return "\n".join([
        "# Jiang Lan exploration source - independent validator",
        "",
        f"- Status: **{result['status']}**",
        f"- Root: `{result['root']}`",
        f"- Source manifest: `{result['source']['path']}`",
        f"- Main report: `{report_path}`",
        f"- Checker selftest: `{selftest_path}` ({result['selftest']['status']})",
        f"- Checks: {sum(1 for c in result['checks'] if c['ok'])}/{len(result['checks'])} passed",
        "",
        "## Failed checks",
        "",
        *[f"- `{c['id']}`: {c.get('detail')}" for c in failed][:40],
        "" if failed else "- None.",
        "",
        "## Contact / slip disclosure",
        "",
        *[f"- {d}: {json.dumps(result['details']['directions'].get(d, {}).get('contact', {}), ensure_ascii=False)}"
          for d in DIRS],
        "",
        "## Limitations",
        "",
        "- Technical source contract only; no art/motion/creator approval.",
        "- Pixel-derived foot landmarks can be `not_verified`; fixed pivots are never treated as footlock.",
        "",
    ])


if __name__ == "__main__":
    raise SystemExit(main())
