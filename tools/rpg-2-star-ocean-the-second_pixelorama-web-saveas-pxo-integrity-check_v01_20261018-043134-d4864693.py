"""Pixelorama Save As .pxo integrity check (read-only on inputs).

Compares a GUI-saved .pxo against its original: zip container, data.json
(only web-save export_profile path/name drift allowed), raw layer blocks and
indices, layer metadata/order, and official Pixelorama CLI split + flat
exports of both files (each run with its own temp APPDATA). Optional runtime
PNGs must equal the flat composite. Writes one JSON report.

Usage:
  python -I <this> --original A.pxo --saved B.pxo --pixelorama Pixelorama.exe
         --report out.json [--runtime-png R.png ...]
"""
import argparse, hashlib, io, json, os, shutil, subprocess, sys, tempfile, zipfile
from PIL import Image

ALLOWED_DATA_DIFFS = {("export_profile", "directory_path"), ("export_profile", "file_name")}
LAYER_KEYS = ("name", "visible", "locked", "opacity", "blend_mode", "parent", "type",
              "clipping_mask", "effects", "ui_color")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load_pxo(path):
    raw = open(path, "rb").read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    return {"sha256": sha(raw), "bytes": len(raw), "zip_ok": z.testzip() is None,
            "names": sorted(z.namelist()), "files": {n: z.read(n) for n in z.namelist()}}


def flat_diffs(a, b, prefix=()):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            out += flat_diffs(a.get(k), b.get(k), prefix + (k,))
    elif a != b:
        out.append(prefix)
    return out


def rgba(path):
    return Image.open(path).convert("RGBA")


def cli_export(exe, pxo, split):
    work = tempfile.mkdtemp(prefix="pxo-saveas-cli-")
    try:
        appdata, out = os.path.join(work, "appdata"), os.path.join(work, "out")
        os.makedirs(appdata), os.makedirs(out)
        src = os.path.join(work, "in.pxo")
        shutil.copyfile(pxo, src)
        cmd = [os.path.abspath(exe), "--headless", "--quit", "--", "--export"] + (["--split-layers"] if split else []) + \
              ["-o", os.path.join(out, "f.png"), src]
        env = dict(os.environ, APPDATA=appdata)
        p = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=180)
        files = {f: rgba(os.path.join(out, f)).copy() for f in sorted(os.listdir(out))}
        return p.returncode, files
    finally:
        shutil.rmtree(work, ignore_errors=True)


def snapshot(d):
    snap = {}
    for root, _, files in os.walk(d):
        for f in files:
            if f == ".running":
                continue
            p = os.path.join(root, f)
            try:
                snap[os.path.relpath(p, d)] = sha(open(p, "rb").read())
            except OSError:
                pass
    return snap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--original", required=True)
    ap.add_argument("--saved", required=True)
    ap.add_argument("--pixelorama", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--runtime-png", action="append", default=[])
    a = ap.parse_args()

    o, s = load_pxo(a.original), load_pxo(a.saved)
    do, ds = json.loads(o["files"]["data.json"]), json.loads(s["files"]["data.json"])
    w, h, n = do["size_x"], do["size_y"], len(do["layers"])
    checks, rep = {}, {"original": {k: o[k] for k in ("sha256", "bytes")},
                       "saved": {k: s[k] for k in ("sha256", "bytes")},
                       "pixelorama_exe_sha256": sha(open(a.pixelorama, "rb").read())}

    checks["zip_ok"] = o["zip_ok"] and s["zip_ok"]
    checks["mimetype"] = s["files"].get("mimetype") == o["files"].get("mimetype") == b"application/x-pixelorama"
    checks["same_member_names"] = o["names"] == s["names"]
    diffs = flat_diffs(do, ds)
    rep["data_json_diffs"] = [".".join(map(str, d)) for d in diffs]
    checks["data_json_only_allowed_diffs"] = all(d in ALLOWED_DATA_DIFFS for d in diffs)
    checks["size_frames_layers"] = (ds["size_x"], ds["size_y"], len(ds["frames"]), len(ds["layers"])) == \
                                   (w, h, len(do["frames"]), n)
    checks["layer_metadata_order"] = [[l.get(k) for k in LAYER_KEYS] for l in do["layers"]] == \
                                     [[l.get(k) for k in LAYER_KEYS] for l in ds["layers"]]

    layers, comp = [], Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for i, l in enumerate(do["layers"], 1):
        ro = o["files"]["image_data/frames/1/layer_%d" % i]
        rs = s["files"].get("image_data/frames/1/layer_%d" % i)
        io_, is_ = o["files"].get("image_data/frames/1/indices_layer_%d" % i), \
                   s["files"].get("image_data/frames/1/indices_layer_%d" % i)
        if l.get("visible", True):
            comp = Image.alpha_composite(comp, Image.frombytes("RGBA", (w, h), ro))
        layers.append({"name": l["name"], "raw_equal": ro == rs, "indices_equal": io_ == is_,
                       "binary_alpha": set(ro[3::4]) <= {0, 255},
                       "opaque_px": sum(1 for x in ro[3::4] if x)})
    checks["raw_layers_equal"] = all(x["raw_equal"] and x["indices_equal"] for x in layers)
    cb = comp.tobytes()
    rep["composite_rgba_sha256"] = sha(cb)

    real = os.path.join(os.environ.get("APPDATA", ""), "pixelorama")
    before = snapshot(real) if os.path.isdir(real) else {}
    cli = {}
    for tag, path in (("original", a.original), ("saved", a.saved)):
        rc_s, split = cli_export(a.pixelorama, path, True)
        rc_f, flat = cli_export(a.pixelorama, path, False)
        per = {}
        for i, l in enumerate(do["layers"], 1):
            m = [f for f in split if "(" + l["name"] + ")" in f]
            per[l["name"]] = len(m) == 1 and split[m[0]].tobytes() == o["files"]["image_data/frames/1/layer_%d" % i]
        fb = next(iter(flat.values())).tobytes() if len(flat) == 1 else None
        cli[tag] = {"split_exit": rc_s, "split_pngs": len(split), "split_layers_exact": per,
                    "flat_exit": rc_f, "flat_pngs": len(flat), "flat_eq_composite": fb == cb}
    after = snapshot(real) if os.path.isdir(real) else {}
    rep["cli"] = cli
    rep["real_appdata_pixelorama_changed"] = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    for tag in cli:
        c = cli[tag]
        checks["cli_%s" % tag] = c["split_exit"] == 0 and c["flat_exit"] == 0 and c["split_pngs"] == n \
            and all(c["split_layers_exact"].values()) and c["flat_eq_composite"]

    rep["runtime"] = {}
    for p in a.runtime_png:
        im = rgba(p)
        rep["runtime"][p] = {"sha256": sha(open(p, "rb").read()), "size": im.size,
                             "eq_composite": im.size == (w, h) and im.tobytes() == cb}
    if a.runtime_png:
        checks["runtime_eq_composite"] = all(v["eq_composite"] for v in rep["runtime"].values())

    rep["layers_bottom_to_top"] = layers
    rep["checks"] = checks
    rep["pass"] = all(checks.values())
    rep["passed"] = "%d/%d" % (sum(checks.values()), len(checks))
    os.makedirs(os.path.dirname(os.path.abspath(a.report)), exist_ok=True)
    with open(a.report, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rep, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"pass": rep["pass"], "passed": rep["passed"], "checks": checks,
                      "data_json_diffs": rep["data_json_diffs"],
                      "real_appdata_changed": rep["real_appdata_pixelorama_changed"]}, indent=1))
    return 0 if rep["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
