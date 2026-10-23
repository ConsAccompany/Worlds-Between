"""Scratch QA (not source): pixel-exact comparison of Pixelorama-emitted PNGs with the authored north static PNG.

Adapted from outputs/milo-w01/scratch/milo_west_pxl_compare.py. argv[1]: the orchestrator pixelorama log dir name
(outputs/milo-n01/logs/<dir>). Pixel equality is the verdict; application diagnostics from the Pixelorama logs
are counted and reported separately and never turn an export into "app-clean".
"""
import glob, hashlib, json, os, re, sys
import numpy as np
from PIL import Image

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
D = os.path.join(R, "outputs/milo-n01/logs", sys.argv[1])
src = glob.glob(os.path.join(R, "game/assets/characters/milo-native-v01/north/*north-static_*.png"))
assert len(src) == 1, src
ref = np.array(Image.open(src[0]).convert("RGBA"))
out = {"reference": os.path.relpath(src[0], R), "reference_sha256": hashlib.sha256(open(src[0], "rb").read()).hexdigest()}
diag = {}
for ext in ("pxo", "ora"):
    em = sorted(glob.glob(os.path.join(D, f"export-{ext}/*.png")))
    r = []
    for p in em:
        im = Image.open(p); a = np.array(im.convert("RGBA"))
        r.append({"file": os.path.relpath(p, R), "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest(),
                  "mode": im.mode, "size": list(im.size), "pixel_exact": a.shape == ref.shape and bool((a == ref).all()),
                  "differing_texels": int(np.count_nonzero(np.any(a != ref, axis=2))) if a.shape == ref.shape else None})
    out[ext] = r
    log = open(os.path.join(D, f"pixelorama-{ext}.log"), encoding="utf-8").read()
    lines = [x for x in log.splitlines() if re.match(r"(ERROR|WARNING|SCRIPT_ERROR)", x)]
    diag[ext] = {"rc": re.search(r"^rc: (\S+)", log, re.M).group(1), "error_lines": sum(x.startswith("ERROR") for x in lines),
                 "warning_lines": sum(x.startswith("WARNING") for x in lines),
                 "script_error_lines": sum(x.startswith("SCRIPT_ERROR") for x in lines), "distinct": sorted(set(lines))}
out["application_diagnostics_separate"] = diag
print(json.dumps(out, indent=1))
ok = all(e["pixel_exact"] for ext in ("pxo", "ora") for e in out[ext]) and all(out[ext] for ext in ("pxo", "ora"))
print("MILO_NORTH_PXL_EXPORT_" + ("PIXEL_EXACT" if ok else "MISMATCH"))
print("MILO_NORTH_PXL_APP_DIAGNOSTICS", {k: (v["error_lines"], v["warning_lines"], v["script_error_lines"]) for k, v in diag.items()},
      "(errors, warnings, script errors; not app-clean if nonzero)")
raise SystemExit(0 if ok else 1)
