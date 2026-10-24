"""Heya i159 native Pixelorama export check, repair v02.

Adds an explicit export-subprocess success gate (exit 0, no timeout, input unchanged) to the exported
equality verdict instead of ignoring it. Image equality, export success and shader/application diagnostic
cleanliness stay separate. Cell count is reported as 13 visible roles x 4 frames x 4 directions = 208
(the producer QA's 224 claim is corrected in a new addendum, not by editing the producer QA).
Writes only under outputs/heya-i159/repair2/native-<runid>/.
"""
import hashlib, io, json, os, re, subprocess, sys, uuid, zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PKG = os.path.join(ROOT, "game/assets/characters/heya-native-v01/idle")
PIX = os.path.join(os.path.dirname(ROOT), "tooling/pixelorama-1.2.3/Pixelorama-Linux-64bit/Pixelorama.x86_64")
DIRS = ("south", "west", "north", "east")
ROLES = ["boots", "dress", "coat", "apron", "belt", "strap", "bag", "arms", "herb", "face", "hair", "braid",
         "scarf"]
CELLS_EXPECTED_TOTAL = len(ROLES) * 4 * len(DIRS)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rb(p):
    with open(p, "rb") as f:
        return f.read()


def dec(b):
    return np.array(Image.open(io.BytesIO(b)).convert("RGBA"))


def run(exe, src, label, dest, split):
    work = os.path.join(dest, label)
    os.makedirs(work, exist_ok=True)
    for n in ("home", "config", "data", "cache", "export"):
        os.makedirs(os.path.join(work, n), exist_ok=True)
    env = dict(os.environ)
    env.update(HOME=os.path.join(work, "home"), XDG_CONFIG_HOME=os.path.join(work, "config"),
               XDG_DATA_HOME=os.path.join(work, "data"), XDG_CACHE_HOME=os.path.join(work, "cache"))
    args = [exe, "--headless", "--quit", "--", "--export"]
    if split:
        args.append("--split-layers")
    args += ["-o", os.path.join(work, "export", "out.png"), src]
    before = sha(rb(src))
    try:
        p = subprocess.run(args, env=env, capture_output=True, timeout=120)
        out, err, code, timeout = p.stdout, p.stderr, p.returncode, False
    except subprocess.TimeoutExpired as e:
        out, err, code, timeout = e.stdout or b"", e.stderr or b"", None, True
    open(os.path.join(work, "stdout.log"), "wb").write(out)
    open(os.path.join(work, "stderr.log"), "wb").write(err)
    text = (out + b"\n" + err).decode("utf-8", "replace")
    markers = [x for x in text.splitlines() if re.search(r"ERROR|SCRIPT ERROR|Shader compilation failed", x, re.I)]
    files = sorted(os.listdir(os.path.join(work, "export")))
    unchanged = sha(rb(src)) == before
    # Explicit export gate: normal exit, no timeout, source PXO unchanged.
    export_success = code == 0 and not timeout and unchanged
    return {"label": label, "exit": code, "timeout": timeout, "input_unchanged": unchanged,
            "export_success": export_success, "markers": markers,
            "diagnostic_clean": code == 0 and not timeout and not markers,
            "files": [os.path.join(work, "export", f) for f in files], "dir": work}


def export_one(d):
    pxo = [os.path.join(PKG, d, f) for f in os.listdir(os.path.join(PKG, d)) if "animated" in f][0]
    pngs = [os.path.join(PKG, d, f) for f in sorted(os.listdir(os.path.join(PKG, d))) if "-f0" in f]
    z = zipfile.ZipFile(io.BytesIO(rb(pxo)))
    data = json.loads(z.read("data.json"))
    dest = os.path.join(OUT, d)
    split = run(PIX, pxo, "split", str(dest), True)
    flat = run(PIX, pxo, "flat", str(dest), False)
    cell = {}
    for f in split["files"]:
        m = re.search(r"\(([^)]+)\)\s*_(\d{4})\.png$", os.path.basename(f))
        if m:
            cell[(m.group(1), int(m.group(2)) - 1)] = dec(rb(f))
    layer_ok, nlayer = True, 0
    for i in range(4):
        for li, n in enumerate(ROLES, 1):
            e = np.frombuffer(z.read(f"image_data/frames/{i + 1}/layer_{li}"), np.uint8).reshape((112, 80, 4))
            layer_ok &= (n, i) in cell and np.array_equal(cell[(n, i)], e)
            nlayer += (n, i) in cell and np.array_equal(cell[(n, i)], e)
    merge_ok = True
    for i in range(4):
        comp = np.zeros((112, 80, 4), np.uint8)
        for n in ROLES:
            a = cell[(n, i)]
            m = a[..., 3] == 255
            comp[m] = a[m]
        merge_ok &= np.array_equal(comp, dec(rb(pngs[i])))
    flatmap = {os.path.basename(f): f for f in flat["files"]}
    flat_ok = len(flat["files"]) == 4
    for i in range(4):
        hit = [v for k, v in flatmap.items() if k.endswith(f"_{i + 1:04d}.png")]
        flat_ok &= len(hit) == 1 and np.array_equal(dec(rb(hit[0])), dec(rb(pngs[i])))
    no_guides = not any("(guides)" in os.path.basename(f) for f in split["files"])
    return d, {"pxo": os.path.relpath(pxo, ROOT), "pxo_sha256": sha(rb(pxo)),
               "split_gates": {"layer_count": len(cell), "layer_cells_exact": nlayer,
                               "layer_cells_expected": len(ROLES) * 4,
                               "all_layer_cells_exact": layer_ok,
                               "merged_frames_exact": merge_ok, "guides_not_exported": no_guides,
                               "input_unchanged": split["input_unchanged"],
                               "export_success": split["export_success"]},
               "flat_gates": {"four_frames": len(flat["files"]) == 4, "frames_exact": flat_ok,
                              "input_unchanged": flat["input_unchanged"],
                              "export_success": flat["export_success"]},
               "runs": {"split": {k: v for k, v in split.items() if k != "files"},
                        "flat": {k: v for k, v in flat.items() if k != "files"}},
               "export_success": split["export_success"] and flat["export_success"],
               "diagnostic_clean": split["diagnostic_clean"] and flat["diagnostic_clean"]}


def main():
    global OUT
    assert os.path.isfile(PIX), PIX
    runid = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    OUT = os.path.join(ROOT, "outputs/heya-i159/repair2/native-" + runid)
    os.makedirs(OUT)
    results = {}
    with ThreadPoolExecutor(max_workers=2) as ex:
        for d, r in ex.map(export_one, DIRS):
            results[d] = r
    gates, cells = {}, 0
    for d, r in results.items():
        for k, v in r["split_gates"].items():
            gates[f"{d}_split_{k}"] = bool(v)
        for k, v in r["flat_gates"].items():
            gates[f"{d}_flat_{k}"] = bool(v)
        cells += int(r["split_gates"]["layer_cells_exact"])
    equality = all(gates[k] for k in gates if not k.endswith("_export_success")
                   and not k.endswith("_input_unchanged"))
    export_ok = all(v for k, v in gates.items() if k.endswith("_export_success"))
    input_ok = all(v for k, v in gates.items() if k.endswith("_input_unchanged"))
    # Export success is explicitly part of the verdict; diagnostic cleanliness is not.
    verdict = equality and export_ok and input_ok and cells == CELLS_EXPECTED_TOTAL
    diagnostics = {d: {"split": results[d]["runs"]["split"]["markers"],
                       "flat": results[d]["runs"]["flat"]["markers"]} for d in DIRS}
    shader = {d: sum("custom_samplers" in x for y in diagnostics[d].values() for x in y) for d in DIRS}
    report = {"task": "content.char.heya.idle-anim native Pixelorama animated export equality (repair v02)",
              "status": "UNAPPROVED", "native_executable": PIX, "native_executable_sha256": sha(rb(PIX)),
              "run_id": runid, "directions": results, "gates": gates,
              "cells_expected_total": CELLS_EXPECTED_TOTAL,
              "cells_exact_total": cells,
              "cells_expected_formula": "13 visible roles * 4 frames * 4 directions = 208",
              "image_equality_passed": equality,
              "export_success_passed": export_ok,
              "input_unchanged_passed": input_ok,
              "export_gated_verdict_passed": verdict,
              "equality_passed": verdict,
              "diagnostic_clean": all(r["diagnostic_clean"] for r in results.values()),
              "shader_sampler_diagnostic_counts": shader,
              "diagnostic_note": "Application/shader diagnostics are retained separately and are NOT export equality; "
                                 "diagnostic_clean=false is not claimed as a pass.",
              "gui_saveas_tested": False, "art_approved": False, "runtime_default_changed": False}
    path = os.path.join(OUT, f"rpg-2-star-ocean-the-second_heya_idle_native-pixelorama-repair-report_v02_{runid}.json")
    with open(path, "x") as f:
        f.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"report": os.path.relpath(path, ROOT), "export_gated_verdict_passed": verdict,
                      "image_equality_passed": equality, "export_success_passed": export_ok,
                      "cells_exact_total": cells, "cells_expected_total": CELLS_EXPECTED_TOTAL,
                      "gates_passed": sum(gates.values()), "gates_total": len(gates),
                      "diagnostic_clean": report["diagnostic_clean"],
                      "shader_counts": shader}, indent=2))
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
