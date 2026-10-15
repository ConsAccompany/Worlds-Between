"""Lossless Pixelorama .pxo source for the approved female south idle static (selout v8), plus a
headless Pixelorama round-trip check.

Scope (user permission: FEMALE, single direction, Pixelorama pilot): south idle static only. This
writes no other direction, action or character, and it never writes, re-encodes or touches the v8
PNG. The .pxo is a container for v8's decoded RGBA exactly as stored; it is not new art and it does
not change any approval.

Modes
  build  write the .pxo and its manifest into game/assets/characters/pixelorama-pilots. Refuses to
         overwrite: if a file already exists it must be byte-identical to the rebuild, else it stops.
  check  read the .pxo from disk, copy it into a fresh temp dir, run
             Pixelorama.exe --headless --quit -- --export -o <tmp>/f.png <copy>
         twice, and require each exported PNG to decode to RGBA bytes identical to v8's. Also checks
         the hidden guides layer is not exported, the v8 PNG / .pxo / manifest hashes are unchanged
         afterwards, and the two runs give byte-identical PNGs. Pixelorama rewrites `current_dir` in
         %APPDATA%\\pixelorama\\config.ini on each run, so the file is backed up first and restored
         byte-for-byte (with its mtime) after every run. Prints a JSON report; writes nothing in the repo.

Layer stack (Pixelorama layer 1 = bottom):
  1 `v8-baseline`  visible; every v8 texel (2,419 opaque, 32 colours) exactly as decoded
  2 `guides`       hidden; cell border, rows 8 / 103 (96-texel body), ground pin (40,104)
The doc's per-role split (hair-front, head-face, ...) is NOT made here: assigning v8 texels to roles
is an art decision nobody has signed off. A role split can later be cut from this file in the GUI.

Run with the real Python (see the pipeline doc) in isolated mode:
  python -I -B <this file> build
  python -I -B <this file> check [--pixelorama <exe>]
"""
import argparse, hashlib, io, json, os, shutil, subprocess, sys, tempfile, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
VARIANT = "m8-v08"
STAMP = "20261015-080907"
RUN_ID = "2ad6d314"
W, H = 80, 112
PIN = (40, 104)
BODY_ROWS = (8, 103)
PIX_DIR_REL = "game/assets/characters/pixelorama-pilots"
V8_REL = (f"{PIX_DIR_REL}/{SLUG}_protagonist-female_"
          "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
V8_SHA256 = "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
DECISION_REL = ("docs/character-visuals/rpg-2-star-ocean-the-second_protagonist-female_"
                "south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md")
PIXELORAMA_REL = "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"
PIXELORAMA_VERSION = "v1.2.3-stable"
LAYERS = ["v8-baseline", "guides"]          # bottom -> top
GUIDE_RGB = (255, 0, 255)


def fid(role):
    return hashlib.sha256(f"{RUN_ID}:{role}".encode()).hexdigest()[:8]


PXO_NAME = f"{SLUG}_protagonist-female_south-idle-selout-v8-editable_{VARIANT}_{STAMP}-{fid('pxo')}.pxo"
MANIFEST_NAME = f"{SLUG}_protagonist-female_south-idle-selout-v8-editable-manifest_{VARIANT}_{STAMP}-{fid('manifest')}.json"
TOOL_REL = "tools/" + os.path.basename(os.path.abspath(__file__))


# ============================================================================ paths / hashes
# Windows MAX_PATH is 260 and these names are ~120 characters; _fs() adds the \\?\ prefix when needed.
WIN_MAX_PATH = 259
WIN_LONG_PREFIX = "\\\\?\\"


def _fs(path):
    path = os.path.abspath(path)
    if os.name == "nt" and len(path) > WIN_MAX_PATH - 12 and not path.startswith(WIN_LONG_PREFIX):
        if path.startswith("\\\\"):
            return WIN_LONG_PREFIX + "UNC\\" + path[2:]
        return WIN_LONG_PREFIX + path
    return path


def repo_path(rel):
    return os.path.join(REPO, *rel.split("/"))


def read_bytes(path):
    with open(_fs(path), "rb") as f:
        return f.read()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def text_sha256_lf(data):
    """sha256-text-lf-v1: SHA-256 after CRLF -> LF, nothing else normalized."""
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def v8_checked():
    """Source hash gate, run first by every mode. Returns (png bytes, decoded RGBA array)."""
    path = repo_path(V8_REL)
    if not os.path.isfile(_fs(path)):
        raise SystemExit(f"v8 source missing: {V8_REL}; refusing to run")
    data = read_bytes(path)
    if sha256_bytes(data) != V8_SHA256:
        raise SystemExit(f"v8 source SHA-256 mismatch ({sha256_bytes(data)} != {V8_SHA256}); refusing to run")
    im = Image.open(io.BytesIO(data))
    if im.mode != "RGBA" or im.size != (W, H):
        raise SystemExit(f"v8 is {im.mode} {im.size}, expected RGBA {(W, H)}")
    return data, np.array(im)


def decode_rgba(png):
    im = Image.open(io.BytesIO(png))
    return im.mode, im.size, np.array(im.convert("RGBA"))


# ============================================================================ build
def guides_rgba(v8a):
    g = np.zeros((H, W, 4), np.uint8)
    pts = set()
    pts.update((x, 0) for x in range(W)); pts.update((x, H - 1) for x in range(W))
    pts.update((0, y) for y in range(H)); pts.update((W - 1, y) for y in range(H))
    for y in BODY_ROWS:                                  # short ticks just inside the border
        pts.update((x, y) for x in list(range(1, 7)) + list(range(W - 7, W - 1)))
    pts.add(PIN)
    for x, y in pts:
        g[y, x, :3] = GUIDE_RGB
        g[y, x, 3] = 255
    # Every guide texel must sit on a v8-transparent texel, so a leaked guide shows up in the check.
    if (v8a[..., 3][g[..., 3] > 0] != 0).any():
        raise SystemExit("a guide texel overlaps an opaque v8 texel")
    return g


def make_pxo(v8_png, v8a):
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": n == "guides", "metadata": {}, "name": n,
                   "new_cels_linked": False, "opacity": 1.0, "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": n != "guides"} for n in LAYERS]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0}
                             for _ in LAYERS], "duration": 1.0, "metadata": {}}]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": json.dumps("protagonist-female-south-idle-selout-v8"),
                      "frame_current_tag": "0", "include_tag_in_filename": "false", "interpolation": "0",
                      "lines_count": "1", "new_dir_for_each_frame_tag": "false", "number_of_digits": "4",
                      "number_of_frames": "1", "orientation": "0", "repeat_count": "0", "resize": "100",
                      "save_quality": "0.75", "separator_character": "\"_\"",
                      "sheet_layers_as_separate_files": "false", "split_layers": "false"}
    data = {"author_company": "", "author_contact": "", "author_display_name": "", "author_real_name": "",
            "brushes": [], "color_mode": 5, "current_frame": 0, "current_layer": 0, "export_profile": export_profile,
            "fps": 6.0, "frames": frames_json, "guides": [], "layers": layer_json, "license": "", "metadata": {},
            "next_keyframe_id": 0, "palettes": [], "pixelorama_version": PIXELORAMA_VERSION,
            "project_current_palette_name": "", "pxo_version": 7, "reference_images": [], "size_x": W, "size_y": H,
            "symmetry_points": [W - 1.0, H - 1.0], "tags": [], "tile_mode_x_basis_x": W, "tile_mode_x_basis_y": 0,
            "tile_mode_y_basis_x": 0, "tile_mode_y_basis_y": H, "tilesets": [], "user_data": "",
            "vanishing_points": []}
    blobs = {"v8-baseline": np.ascontiguousarray(v8a, np.uint8).tobytes(), "guides": guides_rgba(v8a).tobytes()}
    buf = io.BytesIO()
    dt = (2026, 10, 15, 8, 9, 6)        # fixed (zip needs even seconds) -> byte-identical rebuilds
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        def put(name, payload):
            z.writestr(zipfile.ZipInfo(name, dt), payload, zipfile.ZIP_DEFLATED)
        put("data.json", json.dumps(data, separators=(",", ":")))
        put("mimetype", "application/x-pixelorama")
        put("preview.png", v8_png)
        put("image_data/frames/1/", b"")
        for li, name in enumerate(LAYERS, start=1):
            put(f"image_data/frames/1/layer_{li}", blobs[name])
            put(f"image_data/frames/1/indices_layer_{li}", b"\x00")
    return buf.getvalue(), blobs


def pxo_layer_blob(pxo, name):
    with zipfile.ZipFile(io.BytesIO(pxo)) as z:
        data = json.loads(z.read("data.json"))
        names = [l["name"] for l in data["layers"]]
        return z.read(f"image_data/frames/1/layer_{names.index(name) + 1}"), data


def make_manifest(pxo, v8a):
    opaque = v8a[..., 3] > 0
    ys, xs = np.nonzero(opaque)
    colours = {tuple(int(c) for c in px) for px in v8a[opaque][:, :3]}
    decision = read_bytes(repo_path(DECISION_REL))
    m = {
        "project": "Worlds Between",
        "milestone": "M8",
        "visual_id": "protagonist-female",
        "purpose": "Lossless editable Pixelorama source for the user-approved female south idle static "
                   "(selout v8). Container only: v8's decoded RGBA is stored unchanged; no art was changed.",
        "status": "editable source for an approved static frame; pixel content identical to v8; "
                  "not a new candidate; not runtime-integrated; no animation; no other direction",
        "art_approved": False,
        "art_approved_note": "Approval of the v8 static baseline lives only in the decision doc below. This file "
                             "does not extend it to any sprite set, direction, animation or runtime use.",
        "human_reviewed": False,
        "runtime_integrated": False,
        "permission_scope": "female protagonist, single direction (south), Pixelorama pilot",
        "authorship": "Written by a deterministic Python tool authored and run by Claude (Claude Code).",
        "derived_from": {
            "file": V8_REL, "sha256": V8_SHA256, "hash_algorithm": "sha256-bytes",
            "decision_doc": DECISION_REL, "decision_doc_sha256": text_sha256_lf(decision),
            "decision_doc_hash_algorithm": "sha256-text-lf-v1",
        },
        "cell": {"w": W, "h": H, "pin": list(PIN), "display_scale": 0.5, "filter": "nearest",
                 "alpha": "binary", "opaque_texels": int(opaque.sum()), "colours": len(colours),
                 "alpha_bounds_inclusive": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]},
        "editable": {
            "file": f"{PIX_DIR_REL}/{PXO_NAME}", "sha256": sha256_bytes(pxo), "hash_algorithm": "sha256-bytes",
            "format": f"Pixelorama pxo_version 7 ({PIXELORAMA_VERSION}), color_mode 5 (RGBA8), 1 frame x "
                      f"{len(LAYERS)} layers, zip entries with fixed timestamps",
            "layers_bottom_to_top": [
                {"name": "v8-baseline", "visible": True, "locked": False,
                 "content": "all v8 texels, RGBA bytes identical to the decoded v8 PNG"},
                {"name": "guides", "visible": False, "locked": True,
                 "content": f"#ff00ff: cell border, ticks on rows {BODY_ROWS[0]} and {BODY_ROWS[1]}, pin {list(PIN)}; "
                            "every guide texel is on a v8-transparent texel"}],
            "preview_png": "the v8 PNG file bytes, unchanged",
            "role_layer_split": "not made; the per-role split in the pipeline doc needs art sign-off",
        },
        "tool": {"file": TOOL_REL, "sha256": text_sha256_lf(read_bytes(os.path.abspath(__file__))),
                 "hash_algorithm": "sha256-text-lf-v1", "python": sys.version.split()[0],
                 "pillow": Image.__version__, "numpy": np.__version__, "run_flags": "-I -B"},
        "roundtrip_check": {
            "command": f"python -I -B {TOOL_REL} check",
            "cli": f"{PIXELORAMA_REL} --headless --quit -- --export -o <empty temp dir>/f.png <temp copy of the .pxo>",
            "pass_condition": "each exported PNG decodes to RGBA bytes identical to the decoded v8 PNG; "
                              "two runs give byte-identical PNGs; v8 PNG and .pxo hashes unchanged; "
                              "config.ini restored byte-for-byte",
            "result": "see the QA note; this manifest is written before the check runs",
        },
    }
    return (json.dumps(m, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write_new(path, data):
    """Never overwrite: an existing file must already hold exactly these bytes."""
    if os.path.exists(_fs(path)):
        if read_bytes(path) != data:
            raise SystemExit(f"refusing to overwrite a different existing file: {path}")
        return "unchanged"
    with open(_fs(path), "xb") as f:
        f.write(data)
    return "written"


def build():
    v8_png, v8a = v8_checked()
    pxo, blobs = make_pxo(v8_png, v8a)
    if make_pxo(v8_png, v8a)[0] != pxo:
        raise SystemExit("pxo build is not deterministic")
    if blobs["v8-baseline"] != v8a.tobytes():
        raise SystemExit("v8-baseline layer is not the decoded v8 RGBA")
    out = repo_path(PIX_DIR_REL)
    pxo_path = os.path.join(out, PXO_NAME)
    st = write_new(pxo_path, pxo)
    print(st, PXO_NAME, sha256_bytes(pxo))
    man = make_manifest(pxo, v8a)
    st = write_new(os.path.join(out, MANIFEST_NAME), man)
    print(st, MANIFEST_NAME, text_sha256_lf(man), "(sha256-text-lf-v1)")
    if sha256_bytes(read_bytes(repo_path(V8_REL))) != V8_SHA256:
        raise SystemExit("v8 PNG changed during build")


# ============================================================================ check
def config_ini():
    appdata = os.environ.get("APPDATA")
    return os.path.join(appdata, "pixelorama", "config.ini") if appdata else None


def appdata_snapshot(cfg):
    """{relative path: (size, sha256)} for every file in %APPDATA%\\pixelorama, to report side effects."""
    root = os.path.dirname(cfg) if cfg else None
    snap = {}
    if root and os.path.isdir(root):
        for d, _, files in os.walk(root):
            for f in files:
                p = os.path.join(d, f)
                data = read_bytes(p)
                snap[os.path.relpath(p, root).replace("\\", "/")] = (len(data), sha256_bytes(data))
    return snap


def run_export(exe, pxo_copy, out_dir, cfg, cfg_backup):
    cfg_before = read_bytes(cfg) if cfg and os.path.isfile(cfg) else None
    try:
        p = subprocess.run([exe, "--headless", "--quit", "--", "--export", "-o",
                            os.path.join(out_dir, "f.png"), pxo_copy],
                           capture_output=True, text=True, timeout=180)
    finally:
        changed = restored = False
        if cfg_before is not None:
            now = read_bytes(cfg) if os.path.isfile(cfg) else None
            changed = now != cfg_before
            if changed:
                shutil.copy2(cfg_backup, cfg)      # bytes + mtime from the pre-check backup
                restored = read_bytes(cfg) == cfg_before
                if not restored:
                    raise SystemExit(f"could not restore {cfg}; backup kept at {cfg_backup}")
    pngs = sorted(f for f in os.listdir(out_dir) if f.lower().endswith(".png"))
    return p, pngs, changed, restored


def check(exe):
    v8_png, v8a = v8_checked()
    pxo_path = os.path.join(repo_path(PIX_DIR_REL), PXO_NAME)
    man_path = os.path.join(repo_path(PIX_DIR_REL), MANIFEST_NAME)
    pxo = read_bytes(pxo_path)
    man = json.loads(read_bytes(man_path))
    if man["editable"]["sha256"] != sha256_bytes(pxo):
        raise SystemExit("the .pxo on disk does not match its manifest hash")
    rebuilt = make_pxo(v8_png, v8a)[0]
    blob, data = pxo_layer_blob(pxo, "v8-baseline")
    report = {"pixelorama": exe, "v8": {"file": V8_REL, "sha256_before": V8_SHA256},
              "pxo": {"file": f"{PIX_DIR_REL}/{PXO_NAME}", "sha256_before": sha256_bytes(pxo),
                      "equals_rebuild": rebuilt == pxo, "pxo_version": data["pxo_version"],
                      "v8_baseline_layer_equals_v8_rgba": blob == v8a.tobytes(),
                      "layers": [{"name": l["name"], "visible": l["visible"]} for l in data["layers"]]},
              "runs": []}
    cfg = config_ini()
    snap_before = appdata_snapshot(cfg)
    tmp = tempfile.mkdtemp(prefix="wb-v8pxo-")
    try:
        cfg_backup = None
        if cfg and os.path.isfile(cfg):
            cfg_backup = os.path.join(tmp, "config.ini.bak")
            shutil.copy2(cfg, cfg_backup)
            report["config_ini"] = {"path": cfg, "sha256_before": sha256_bytes(read_bytes(cfg))}
        pxo_copy = os.path.join(tmp, "v8src.pxo")
        with open(pxo_copy, "wb") as f:
            f.write(pxo)
        exports = []
        for i in (1, 2):
            out_dir = os.path.join(tmp, f"export{i}")
            os.makedirs(out_dir)
            p, pngs, cfg_changed, cfg_restored = run_export(exe, pxo_copy, out_dir, cfg, cfg_backup)
            run = {"run": i, "exit_code": p.returncode, "pngs": pngs, "config_ini_changed": cfg_changed,
                   "config_ini_restored": cfg_restored,
                   "pxo_copy_unchanged": sha256_bytes(read_bytes(pxo_copy)) == sha256_bytes(pxo),
                   "stdout_tail": p.stdout.strip().splitlines()[-3:]}
            if len(pngs) == 1:
                png = read_bytes(os.path.join(out_dir, pngs[0]))
                mode, size, a = decode_rgba(png)
                diff = (a != v8a).any(axis=2) if a.shape == v8a.shape else None
                run.update({"png_sha256": sha256_bytes(png), "mode": mode, "size": list(size),
                            "rgba_bytes_equal_v8": a.shape == v8a.shape and a.tobytes() == v8a.tobytes(),
                            "differing_texels": None if diff is None else int(diff.sum()),
                            "guide_texels_leaked": None if diff is None else
                            int((a[..., 3][guides_rgba(v8a)[..., 3] > 0] != 0).sum()),
                            "png_file_bytes_equal_v8_png": png == v8_png})
                exports.append(png)
            report["runs"].append(run)
        report["runs_byte_identical"] = len(exports) == 2 and exports[0] == exports[1]
        if cfg:
            report["config_ini"]["sha256_after"] = sha256_bytes(read_bytes(cfg))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    snap_after = appdata_snapshot(cfg)
    report["appdata_pixelorama_other_changes"] = {
        "added": sorted(set(snap_after) - set(snap_before)),
        "removed": sorted(set(snap_before) - set(snap_after)),
        "modified": sorted(k for k in set(snap_before) & set(snap_after) if snap_before[k] != snap_after[k])}
    report["v8"]["sha256_after"] = sha256_bytes(read_bytes(repo_path(V8_REL)))
    report["pxo"]["sha256_after"] = sha256_bytes(read_bytes(pxo_path))
    report["manifest_sha256_text_lf_v1"] = text_sha256_lf(read_bytes(man_path))
    ok = (report["pxo"]["equals_rebuild"] and report["pxo"]["v8_baseline_layer_equals_v8_rgba"]
          and len(report["runs"]) == 2 and report["runs_byte_identical"]
          and all(r["exit_code"] == 0 and r.get("rgba_bytes_equal_v8") and r["pxo_copy_unchanged"]
                  and r.get("guide_texels_leaked") == 0 for r in report["runs"])
          and report["v8"]["sha256_after"] == V8_SHA256
          and report["pxo"]["sha256_after"] == report["pxo"]["sha256_before"]
          and (not cfg or report["config_ini"]["sha256_after"] == report["config_ini"]["sha256_before"]))
    report["result"] = "PASS" if ok else "FAIL"
    print(json.dumps(report, indent=2))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=["build", "check"])
    ap.add_argument("--pixelorama", default=repo_path(PIXELORAMA_REL))
    args = ap.parse_args()
    if args.mode == "build":
        build()
        return 0
    if not os.path.isfile(args.pixelorama):
        raise SystemExit(f"Pixelorama not found: {args.pixelorama}")
    return check(os.path.abspath(args.pixelorama))


if __name__ == "__main__":
    sys.exit(main())
