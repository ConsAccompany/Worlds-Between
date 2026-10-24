"""Focused Yanke north static native Pixelorama export-equality check.

Reads the installed package; writes only under --out. Uses the repository's established
`Pixelorama --headless --quit -- --export [--split-layers]` command with isolated
HOME/XDG dirs. Source/export equality and application diagnostic cleanliness are
reported as separate fields: this tool never claims a diagnostic-clean or GUI result.
"""
import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SLUG = "rpg-2-star-ocean-the-second"
PKG = ROOT / "game/assets/characters/yanke-native-v01/north"
STAMP = "20261024-092500-n101north"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rgba(data):
    return np.array(Image.open(io.BytesIO(data)).convert("RGBA"))


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def run(exe, source, label, out, split=False):
    work = out / label
    work.mkdir(parents=True, exist_ok=True)
    input_path = work / f"{label}-input{source.suffix}"
    original = source.read_bytes()
    write(input_path, original)
    for name in ("home", "config", "data", "cache"):
        (work / name).mkdir(exist_ok=True)
    env = dict(os.environ)
    env["HOME"] = str(work / "home")
    env["XDG_CONFIG_HOME"] = str(work / "config")
    env["XDG_DATA_HOME"] = str(work / "data")
    env["XDG_CACHE_HOME"] = str(work / "cache")
    export_dir = work / "export"
    export_dir.mkdir(exist_ok=True)
    args = [str(exe), "--headless", "--quit", "--", "--export"]
    if split:
        args.append("--split-layers")
    args += ["-o", str(export_dir / "out.png"), str(input_path)]
    started = datetime.now(timezone.utc).isoformat()
    timed_out = False
    try:
        proc = subprocess.run(args, env=env, capture_output=True, timeout=120)
        stdout, stderr, code = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, code, timed_out = exc.stdout or b"", exc.stderr or b"", None, True
    ended = datetime.now(timezone.utc).isoformat()
    write(work / "stdout.log", stdout)
    write(work / "stderr.log", stderr)
    combined = (stdout + b"\n" + stderr).decode("utf-8", "replace")
    markers = [line for line in combined.splitlines()
               if re.search(r"ERROR|WARNING|SCRIPT ERROR|Shader compilation failed", line, re.I)]
    files = sorted(export_dir.glob("*.png"))
    return {
        "label": label,
        "command": args,
        "start_utc": started,
        "end_utc": ended,
        "exit": code,
        "timeout": timed_out,
        "input_sha256": sha(original),
        "input_unchanged": input_path.read_bytes() == original,
        "source_unchanged": source.read_bytes() == original,
        "stdout_log": str((work / "stdout.log").relative_to(ROOT)),
        "stderr_log": str((work / "stderr.log").relative_to(ROOT)),
        "diagnostic_markers": markers,
        "diagnostic_clean": code == 0 and not timed_out and not markers,
        "exports": [{"path": str(f.relative_to(ROOT)), "sha256": sha(f.read_bytes()),
                     "size": list(rgba(f.read_bytes()).shape[1::-1])} for f in files],
        "export_paths": files,
    }


def match_layer(files, name):
    hits = [f for f in files if f"({name})" in f.name]
    return hits[0] if len(hits) == 1 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--pixelorama", default=str(ROOT.parent / "tooling/pixelorama-1.2.3/Pixelorama-Linux-64bit/Pixelorama.x86_64"))
    args = ap.parse_args()
    out = (ROOT / args.out).resolve()
    out.relative_to(ROOT)  # refuse writes outside the repository
    exe = Path(args.pixelorama).resolve()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    dest = out / run_id
    dest.mkdir(parents=True)
    static_png = next(PKG.glob("*yanke_north-static*.png"))
    pxo_path = next(PKG.glob("*.pxo"))
    ora_path = next(PKG.glob("*.ora"))
    static = rgba(static_png.read_bytes())
    before = {p: sha(p.read_bytes()) for p in (static_png, pxo_path, ora_path)}
    gates = {}

    pxo_flat = run(exe, pxo_path, "pxo-flat", dest)
    pxo_split = run(exe, pxo_path, "pxo-split", dest, split=True)
    pxo = zipfile.ZipFile(io.BytesIO(pxo_path.read_bytes()))
    data = json.loads(pxo.read("data.json"))
    visible = [(i, layer["name"]) for i, layer in enumerate(data["layers"], 1) if layer["visible"]]
    layer_rows = {}
    for index, name in visible:
        target = match_layer(pxo_split["export_paths"], name)
        expected = np.frombuffer(pxo.read(f"image_data/frames/1/layer_{index}"),
                                 dtype=np.uint8).reshape(static.shape)
        layer_rows[name] = bool(target) and np.array_equal(rgba(target.read_bytes()), expected)
    # Composite the exported layers bottom-to-top and compare with the flat package PNG.
    composite = Image.new("RGBA", (static.shape[1], static.shape[0]), (0, 0, 0, 0))
    for _, name in visible:
        target = match_layer(pxo_split["export_paths"], name)
        if target:
            composite = Image.alpha_composite(composite, Image.open(target).convert("RGBA"))
    pxo_merged_exact = np.array_equal(np.array(composite), static)

    gates["pxo_flat_one_export"] = len(pxo_flat["exports"]) == 1
    gates["pxo_flat_exact_static"] = gates["pxo_flat_one_export"] and np.array_equal(
        rgba(Path(ROOT / pxo_flat["exports"][0]["path"]).read_bytes()), static)
    gates["pxo_split_layer_count"] = len(pxo_split["export_paths"]) == len(visible)
    gates["pxo_split_each_layer_exact"] = len(layer_rows) == len(visible) and all(layer_rows.values())
    gates["pxo_split_merged_exact_static"] = pxo_merged_exact
    gates["pxo_no_visible_guide_export"] = not any("(guides)" in f.name for f in pxo_split["export_paths"])
    gates["pxo_inputs_unchanged"] = all(r["input_unchanged"] and r["source_unchanged"] for r in (pxo_flat, pxo_split))

    ora_flat = run(exe, ora_path, "ora-flat", dest)
    gates["ora_flat_one_export"] = len(ora_flat["exports"]) == 1
    gates["ora_flat_exact_static"] = gates["ora_flat_one_export"] and np.array_equal(
        rgba(Path(ROOT / ora_flat["exports"][0]["path"]).read_bytes()), static)
    gates["ora_inputs_unchanged"] = ora_flat["input_unchanged"] and ora_flat["source_unchanged"]

    gates["package_bytes_unchanged"] = all(sha(p.read_bytes()) == digest for p, digest in before.items())
    diagnostics = {"pxo-flat": pxo_flat["diagnostic_markers"],
                   "pxo-split": pxo_split["diagnostic_markers"],
                   "ora-flat": ora_flat["diagnostic_markers"]}
    shader = {(k): sum("custom_samplers" in line for line in v) for k, v in diagnostics.items()}
    report = {
        "task": "content.char.yanke.static-north native Pixelorama export equality (test-only)",
        "tool": str(Path(__file__).resolve().relative_to(ROOT)),
        "tool_sha256": sha(Path(__file__).read_bytes()),
        "native_executable": str(exe),
        "native_executable_sha256": sha(exe.read_bytes()),
        "run_id": run_id,
        "package": {"static_png": str(static_png.relative_to(ROOT)), "static_sha256": sha(static_png.read_bytes()),
                    "pxo": str(pxo_path.relative_to(ROOT)), "pxo_sha256": sha(pxo_path.read_bytes()),
                    "ora": str(ora_path.relative_to(ROOT)), "ora_sha256": sha(ora_path.read_bytes())},
        "gates": gates,
        "equality_passed": all(gates.values()),
        "layer_rows": layer_rows,
        "runs": {r["label"]: {k: v for k, v in r.items() if k != "export_paths"}
                 for r in (pxo_flat, pxo_split, ora_flat)},
        "diagnostic_clean": all(r["diagnostic_clean"] for r in (pxo_flat, pxo_split, ora_flat)),
        "shader_sampler_diagnostic_counts": shader,
        "diagnostic_note": "Application diagnostics are retained separately and are NOT part of export equality; diagnostic_clean=false is not claimed as a pass.",
        "gui_saveas_tested": False,
        "runtime_or_default_changed": False,
        "art_approved": False,
    }
    path = dest / f"{SLUG}_yanke_north_native-pixelorama-export-report_test-only-v01_{STAMP}.json"
    write(path, (json.dumps(report, indent=2) + "\n").encode())
    print(json.dumps({"report": str(path.relative_to(ROOT)), "equality_passed": report["equality_passed"],
                      "gates": gates, "diagnostic_clean": report["diagnostic_clean"],
                      "shader_sampler_diagnostics": shader}, indent=2))
    print("YANKE_N101_NORTH_NATIVE_PIXELORAMA " + ("PASS" if report["equality_passed"] else "FAIL"))
    if not report["equality_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
