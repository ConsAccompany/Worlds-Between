"""Shared, character-agnostic helpers for hand-placed static pilots in the approved female selout v8 format
(80x112 cell, pin (40,104), body rows 8..103, 0.5 display scale, binary alpha, 1-texel outer ink).

Factored out of the Liang Xu (baa30d44) and male protagonist (3c35d8cf / ca1d6e0a) pilot tools so a new pilot tool only
carries its own literal MAP/ROLE grids, ramps, references and identity metrics. Those older tools are left unchanged.
Nothing here draws, resamples, filters, quantizes or dithers: it composes literal grids, writes the Pixelorama .pxo
(pxo_version 7) / OpenRaster .ora containers, runs the technical gates and drives Pixelorama's official headless CLI
with APPDATA redirected to a throwaway directory.

Import by path (the file name has hyphens), e.g.
    spec = importlib.util.spec_from_file_location("v8fmt", path); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
A pilot passes a Spec (see make_spec) to every function.
"""
import hashlib, io, json, os, shutil, subprocess, tempfile, zipfile
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

W, H = 80, 112
GRID_W, GRID_H = 56, 96
GRID_OFFSET = (12, 8)                 # grid (0,0) -> cell (12,8); body rows 8..103 like v8
PIN = (40, 104)
BODY_ROWS = (8, 103)
DISPLAY_SCALE = 0.5                   # 96 texels -> 48 logical px; 1 texel = 1 window px at 1280x720
GUIDE_RGB = (255, 0, 255)
PIXELORAMA_REL = "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"
PIXELORAMA_VERSION = "v1.2.3-stable"
V8_REL = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-"
          "v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
V8_SHA256 = "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
V8_P4_RAMPS = {"coat": ["5e6e8c", "3a4560", "222839"], "trousers": ["4a625c", "324542"]}
HARD_GATES = ["P1_binary_alpha", "P1_no_opaque_on_border", "P2_pass", "P3_all_colours_declared",
              "P3_no_declared_unused", "S1_pass", "S1_pin_inside_feet_span"]
GUI_OWNED = (".running", "backups/")  # an open GUI's heartbeat and ~62 s autosaves; never written by our runs
WIN_MAX_PATH = 259
WIN_LONG_PREFIX = "\\\\?\\"


def make_spec(repo, map_rows, role_rows, ramps, role_layers, export_name, zip_dt, p4_exempt=()):
    """ramps: {name: {key: 'rrggbb'}}; role_layers: [(layer name, role key)] bottom to top (guides appended)."""
    pal = {k: v for ramp in ramps.values() for k, v in ramp.items()}
    return {"repo": repo, "MAP": map_rows, "ROLE": role_rows, "RAMPS": ramps, "PAL": pal,
            "ROLE_LAYERS": role_layers, "LAYERS": [n for n, _ in role_layers] + ["guides"],
            "export_name": export_name, "zip_dt": zip_dt, "p4_exempt": tuple(p4_exempt)}


# ============================================================================ paths / hashes
def fs(path):
    path = os.path.abspath(path)
    if os.name == "nt" and len(path) > WIN_MAX_PATH - 12 and not path.startswith(WIN_LONG_PREFIX):
        return WIN_LONG_PREFIX + path
    return path


def repo_path(repo, rel):
    return os.path.join(repo, *rel.split("/"))


def read_bytes(path):
    with open(fs(path), "rb") as f:
        return f.read()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def text_sha256_lf(data):
    """sha256-text-lf-v1: SHA-256 after CRLF -> LF, nothing else normalized."""
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def ref_hash(repo, rel, kind):
    data = read_bytes(repo_path(repo, rel))
    return (sha256_bytes(data), "sha256-bytes") if kind == "bytes" else (text_sha256_lf(data), "sha256-text-lf-v1")


def write_new(path, data, text=False):
    """Write once; an existing file must already hold the same content (text compared CRLF-insensitively)."""
    if os.path.exists(fs(path)):
        old = read_bytes(path)
        same = text_sha256_lf(old) == text_sha256_lf(data) if text else old == data
        if not same:
            raise SystemExit(f"refusing to overwrite a different existing file: {path}")
        return "unchanged"
    with open(fs(path), "xb") as f:
        f.write(data)
    return "written"


# ============================================================================ composition
def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def validate_maps(spec):
    m_rows, r_rows, pal = spec["MAP"], spec["ROLE"], spec["PAL"]
    keys = {k for _, k in spec["ROLE_LAYERS"]}
    if len(m_rows) != GRID_H or len(r_rows) != GRID_H:
        raise SystemExit("MAP/ROLE must have 96 rows")
    for y, (m, r) in enumerate(zip(m_rows, r_rows)):
        if len(m) != GRID_W or len(r) != GRID_W:
            raise SystemExit(f"row {y}: MAP/ROLE rows must be {GRID_W} wide")
        for x, (mk, rk) in enumerate(zip(m, r)):
            if (mk == ".") != (rk == "."):
                raise SystemExit(f"MAP/ROLE opacity differs at grid ({x},{y})")
            if mk != "." and mk not in pal:
                raise SystemExit(f"undeclared colour key {mk!r} at grid ({x},{y})")
            if rk != "." and rk not in keys:
                raise SystemExit(f"unknown role key {rk!r} at grid ({x},{y})")


def compose(spec, role_key=None):
    """RGBA cell; with role_key, only that role's texels."""
    a = np.zeros((H, W, 4), np.uint8)
    ox, oy = GRID_OFFSET
    for y in range(GRID_H):
        for x in range(GRID_W):
            k = spec["MAP"][y][x]
            if k == "." or (role_key is not None and spec["ROLE"][y][x] != role_key):
                continue
            a[oy + y, ox + x, :3] = hex_rgb(spec["PAL"][k])
            a[oy + y, ox + x, 3] = 255
    return a


def guides_rgba(full):
    g = np.zeros((H, W, 4), np.uint8)
    pts = set()
    pts.update((x, 0) for x in range(W)); pts.update((x, H - 1) for x in range(W))
    pts.update((0, y) for y in range(H)); pts.update((W - 1, y) for y in range(H))
    for y in BODY_ROWS:
        pts.update((x, y) for x in list(range(1, 4)) + list(range(W - 4, W - 1)))
    pts.add(PIN)
    for x, y in pts:
        g[y, x, :3] = GUIDE_RGB
        g[y, x, 3] = 255
    if (full[..., 3][g[..., 3] > 0] != 0).any():
        raise SystemExit("a guide texel overlaps an opaque sprite texel")
    return g


def png_bytes(a):
    buf = io.BytesIO()
    Image.fromarray(a, "RGBA").save(buf, "PNG", optimize=False, compress_level=9)
    return buf.getvalue()


def decode(png):
    return np.array(Image.open(io.BytesIO(png)).convert("RGBA"))


def make_pxo(spec, blobs, preview_png):
    layers = spec["LAYERS"]
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": n == "guides", "metadata": {}, "name": n,
                   "new_cels_linked": False, "opacity": 1.0, "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": n != "guides"} for n in layers]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0}
                             for _ in layers], "duration": 1.0, "metadata": {}}]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": json.dumps(spec["export_name"]),
                      "frame_current_tag": "0", "include_tag_in_filename": "false", "interpolation": "0",
                      "lines_count": "1", "new_dir_for_each_frame_tag": "false", "number_of_digits": "4",
                      "number_of_frames": "1", "orientation": "0", "repeat_count": "0", "resize": "100",
                      "save_quality": "0.75", "separator_character": "\"_\"",
                      "sheet_layers_as_separate_files": "false", "split_layers": "false"}
    palette = {"name": spec["export_name"], "comment": "declared ramps", "width": 8,
               "height": (len(spec["PAL"]) + 7) // 8,
               "colors": {str(i): {"color": "(%s, %s, %s, 1.0)" % tuple(round(c / 255, 6) for c in hex_rgb(v)), "index": i}
                          for i, v in enumerate(spec["PAL"].values())}}
    data = {"author_company": "", "author_contact": "", "author_display_name": "", "author_real_name": "",
            "brushes": [], "color_mode": 5, "current_frame": 0, "current_layer": len(layers) - 2,
            "export_profile": export_profile, "fps": 6.0, "frames": frames_json, "guides": [], "layers": layer_json,
            "license": "", "metadata": {}, "next_keyframe_id": 0, "palettes": [],
            "pixelorama_version": PIXELORAMA_VERSION, "project_current_palette_name": "", "pxo_version": 7,
            "reference_images": [], "size_x": W, "size_y": H, "symmetry_points": [W - 1.0, H - 1.0], "tags": [],
            "tile_mode_x_basis_x": W, "tile_mode_x_basis_y": 0, "tile_mode_y_basis_x": 0, "tile_mode_y_basis_y": H,
            "tilesets": [], "user_data": json.dumps({"declared_palette": palette}), "vanishing_points": []}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        def put(name, payload):
            z.writestr(zipfile.ZipInfo(name, spec["zip_dt"]), payload, zipfile.ZIP_DEFLATED)
        put("data.json", json.dumps(data, separators=(",", ":")))
        put("mimetype", "application/x-pixelorama")
        put("preview.png", preview_png)
        put("image_data/frames/1/", b"")
        for li, name in enumerate(layers, start=1):
            put(f"image_data/frames/1/layer_{li}", blobs[name].tobytes())
            put(f"image_data/frames/1/indices_layer_{li}", b"\x00")
    return buf.getvalue()


def make_ora(spec, blobs, png):
    dt = spec["zip_dt"]
    stack = ['<?xml version="1.0" encoding="UTF-8"?>',
             f'<image version="0.0.3" w="{W}" h="{H}" xres="72" yres="72">', "<stack>"]
    for name in reversed(spec["LAYERS"]):                  # ORA lists the top layer first
        vis = "hidden" if name == "guides" else "visible"
        stack.append(f'<layer name="{name}" src="data/{name}.png" x="0" y="0" opacity="1.0" '
                     f'visibility="{vis}" composite-op="svg:src-over"/>')
    stack += ["</stack>", "</image>"]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", dt), "image/openraster", zipfile.ZIP_STORED)
        z.writestr(zipfile.ZipInfo("stack.xml", dt), "\n".join(stack) + "\n", zipfile.ZIP_DEFLATED)
        for name in spec["LAYERS"]:
            z.writestr(zipfile.ZipInfo(f"data/{name}.png", dt), png_bytes(blobs[name]), zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("mergedimage.png", dt), png, zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("Thumbnails/thumbnail.png", dt), png, zipfile.ZIP_DEFLATED)
    return buf.getvalue()


def artifacts(spec):
    """-> full RGBA, png, pxo, ora, per-layer blobs; role layers must not overlap and must reassemble the PNG."""
    validate_maps(spec)
    full = compose(spec)
    union = np.zeros_like(full)
    blobs = {}
    for name, k in spec["ROLE_LAYERS"]:
        part = compose(spec, k)
        if ((union[..., 3] > 0) & (part[..., 3] > 0)).any():
            raise SystemExit("role layers overlap")
        union[part[..., 3] > 0] = part[part[..., 3] > 0]
        blobs[name] = part
    if union.tobytes() != full.tobytes():
        raise SystemExit("role layers do not reassemble the full sprite")
    blobs["guides"] = guides_rgba(full)
    png = png_bytes(full)
    return full, png, make_pxo(spec, blobs, png), make_ora(spec, blobs, png), blobs


def read_ora_layers(ora):
    """Parse an .ora: [(name, RGBA, visibility)] top-first, hidden layer names, merged image, mimetype-first flag."""
    with zipfile.ZipFile(io.BytesIO(ora)) as z:
        root = ET.fromstring(z.read("stack.xml"))
        layers, hidden = [], []
        for el in root.iter("layer"):
            layers.append((el.get("name"), decode(z.read(el.get("src"))), el.get("visibility", "visible")))
            if el.get("visibility") == "hidden":
                hidden.append(el.get("name"))
        merged = decode(z.read("mergedimage.png"))
        first = z.infolist()[0]
        mimetype_first = first.filename == "mimetype" and first.compress_type == zipfile.ZIP_STORED
    return layers, hidden, merged, mimetype_first


def recompose(layers_bottom_up):
    comp = np.zeros((H, W, 4), np.uint8)
    for _, a in layers_bottom_up:
        m = a[..., 3] == 255
        comp[m] = a[m]
    return comp


# ============================================================================ gates and metrics
def lab(rgb):
    c = []
    for v in rgb:
        v = v / 255.0
        c.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    x = (0.4124 * c[0] + 0.3576 * c[1] + 0.1805 * c[2]) / 0.95047
    y = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    z = (0.0193 * c[0] + 0.1192 * c[1] + 0.9505 * c[2]) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return (116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z)))


def de76(a, b):
    return sum((p - q) ** 2 for p, q in zip(lab(a), lab(b))) ** 0.5


def v8_rgba(repo):
    p = repo_path(repo, V8_REL)
    if os.path.isfile(fs(p)) and sha256_bytes(read_bytes(p)) == V8_SHA256:
        return decode(read_bytes(p))
    return None


def isolated_texels(full):
    """Opaque texels whose colour differs from all 8 neighbours (single-texel speckle; noise proxy)."""
    rgb = full[..., :3].astype(int); op = full[..., 3] > 0
    n = 0
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not op[y, x]:
                continue
            same = False
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if (dx or dy) and op[y + dy, x + dx] and (rgb[y + dy, x + dx] == rgb[y, x]).all():
                        same = True
            n += 0 if same else 1
    return n


def gates(spec, full):
    alpha = full[..., 3]
    opaque = alpha > 0
    ys, xs = np.nonzero(opaque)
    colours = {tuple(int(c) for c in px) for px in full[opaque][:, :3]}
    declared = {hex_rgb(v) for v in spec["PAL"].values()}
    border = np.zeros_like(opaque); border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
    ramp_steps = {}
    for name, ramp in spec["RAMPS"].items():
        if name in spec["p4_exempt"] or len(ramp) < 2:
            continue
        ls = sorted((lab(hex_rgb(v))[0] for v in ramp.values()), reverse=True)
        ramp_steps[name] = [round(a - b, 2) for a, b in zip(ls, ls[1:])]
    v8_steps = []
    for r in V8_P4_RAMPS.values():
        ls = sorted((lab(hex_rgb(v))[0] for v in r), reverse=True)
        v8_steps += [a - b for a, b in zip(ls, ls[1:])]
    all_steps = [s for v in ramp_steps.values() for s in v]
    body_h = int(ys.max() - ys.min() + 1)
    sole = int(ys.max())
    feet = xs[ys == sole]
    low = xs[ys >= sole - 12]
    v8 = v8_rgba(spec["repo"])
    bench = {}
    if v8 is not None:
        va = v8[..., 3] > 0
        vys, vxs = np.nonzero(va)
        bench = {"v8_visible_size": [int(vxs.max() - vxs.min() + 1), int(vys.max() - vys.min() + 1)],
                 "v8_opaque_texels": int(va.sum()), "v8_colours": len({tuple(int(c) for c in px) for px in v8[va][:, :3]}),
                 "v8_isolated_single_texels": isolated_texels(v8)}
    return {
        "P1_binary_alpha": bool(set(np.unique(alpha).tolist()) <= {0, 255}),
        "P1_no_opaque_on_border": not bool((opaque & border).any()),
        "P2_colour_count": len(colours), "P2_cap": 48, "P2_pass": len(colours) <= 48,
        "P3_all_colours_declared": colours <= declared,
        "P3_declared_unused": sorted("#" + "%02x%02x%02x" % c for c in declared - colours),
        "P3_no_declared_unused": not (declared - colours),
        "P4_ramp_adjacent_Lstar_steps": ramp_steps, "P4_exempt": list(spec["p4_exempt"]),
        "P4_min_step": round(min(all_steps), 2), "P4_v8_reference_min_step": round(min(v8_steps), 2),
        "P4_pass_report_only": min(all_steps) >= min(v8_steps),
        "S1_body_height": body_h, "S1_pass": body_h == 96 and sole == PIN[1] - 1 and int(ys.min()) == BODY_ROWS[0],
        "S1_alpha_bounds_inclusive": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
        "S1_sole_row": sole, "S1_pin": list(PIN), "S1_sole_span_x": [int(feet.min()), int(feet.max())],
        "S1_pin_inside_feet_span": bool(int(low.min()) <= PIN[0] <= int(low.max())),
        "opaque_texels": int(opaque.sum()),
        "visible_size": [int(xs.max() - xs.min() + 1), body_h],
        "isolated_single_texels": isolated_texels(full),
        "benchmark_v8": bench,
    }


# ============================================================================ Pixelorama CLI (isolated)
def real_pixelorama_snapshot():
    root = os.path.join(os.environ.get("APPDATA", ""), "pixelorama")
    snap = {}
    if os.path.isdir(root):
        for d, _, files in os.walk(root):
            for f in files:
                p = os.path.join(d, f)
                rel = os.path.relpath(p, root).replace("\\", "/")
                try:
                    snap[rel] = sha256_bytes(read_bytes(p))
                except OSError:
                    snap[rel] = "unreadable"
    return snap


def pixelorama_export(exe, src, out_dir, split):
    """Headless export with APPDATA redirected to a fresh temp dir (never touches the real config)."""
    env = dict(os.environ)
    env["APPDATA"] = tempfile.mkdtemp(prefix="wb-pxappdata-")
    args = [exe, "--headless", "--quit", "--", "--export"] + (["--split-layers"] if split else []) + \
           ["-o", os.path.join(out_dir, "f.png"), src]
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=240, env=env)
    finally:
        shutil.rmtree(fs(env["APPDATA"]), ignore_errors=True)
    files = sorted(f for f in os.listdir(fs(out_dir)) if f.lower().endswith(".png"))
    return p.returncode, {f: read_bytes(os.path.join(out_dir, f)) for f in files}


def container_checks(spec, exe, disk, full, blobs):
    """.ora structure + Pixelorama CLI flat (x2) and split-layer exports of both the .pxo and the .ora."""
    rep = {}
    layers, hidden, merged, mt = read_ora_layers(disk["ora"])
    bottom_up = [(n, a) for n, a, vis in reversed(layers) if vis != "hidden"]
    rep["ora_structure"] = {"mimetype_first_and_stored": mt, "hidden_layers": hidden,
                            "layer_names_bottom_up": [n for n, _ in bottom_up],
                            "visible_layers_recompose_to_png": recompose(bottom_up).tobytes() == full.tobytes(),
                            "each_layer_equals_role_blob": all(a.tobytes() == blobs[n].tobytes() for n, a in bottom_up),
                            "mergedimage_equals_png": merged.tobytes() == full.tobytes()}
    px = {}
    snap0 = real_pixelorama_snapshot()
    tmp = tempfile.mkdtemp(prefix="wb-v8fmt-")
    try:
        for kind in ("pxo", "ora"):
            src = os.path.join(tmp, f"cand.{kind}")
            with open(fs(src), "wb") as f:
                f.write(disk[kind])
            flats = []
            for run, split in ((1, False), (2, False), (3, True)):
                od = os.path.join(tmp, f"{kind}-{run}")
                os.makedirs(fs(od))
                rc, outs = pixelorama_export(exe, src, od, split)
                arrs = {f: decode(b) for f, b in outs.items()}
                if split:
                    want = {n: blobs[n].tobytes() for n, _ in spec["ROLE_LAYERS"]}
                    matched = sorted(n for n, b in want.items() if any(o.tobytes() == b for o in arrs.values()))
                    leak = any(o.tobytes() == blobs["guides"].tobytes() for o in arrs.values())
                    r = {"mode": "split-layers", "exit": rc, "pngs": len(outs), "visible_layers_matched": len(matched),
                         "visible_layers": len(want), "guides_exported": leak,
                         "pass": rc == 0 and len(matched) == len(want) and len(outs) == len(want) and not leak}
                else:
                    ok = rc == 0 and len(outs) == 1 and next(iter(arrs.values())).tobytes() == full.tobytes()
                    r = {"mode": "flattened", "run": run, "exit": rc, "pngs": len(outs), "rgba_equals_png": ok, "pass": ok}
                    if len(outs) == 1:
                        flats.append(next(iter(outs.values())))
                px[f"{kind}_{run}"] = r
            px[f"{kind}_flat_runs_byte_identical"] = len(flats) == 2 and flats[0] == flats[1]
            with open(fs(src), "rb") as f:
                px[f"{kind}_input_unchanged_by_cli"] = f.read() == disk[kind]
    finally:
        shutil.rmtree(fs(tmp), ignore_errors=True)
    snap1 = real_pixelorama_snapshot()
    changed = sorted(k for k in set(snap0) | set(snap1) if snap0.get(k) != snap1.get(k))
    rep["pixelorama"] = px
    rep["real_appdata_pixelorama_changed"] = {"ours": [k for k in changed if not k.startswith(GUI_OWNED)],
                                              "gui_owned_heartbeat_or_autosave": [k for k in changed if k.startswith(GUI_OWNED)]}
    o = rep["ora_structure"]
    rep["pass"] = (o["mimetype_first_and_stored"] and o["hidden_layers"] == ["guides"]
                   and o["visible_layers_recompose_to_png"] and o["each_layer_equals_role_blob"] and o["mergedimage_equals_png"]
                   and all(v["pass"] for v in px.values() if isinstance(v, dict))
                   and px["pxo_flat_runs_byte_identical"] and px["ora_flat_runs_byte_identical"]
                   and px["pxo_input_unchanged_by_cli"] and px["ora_input_unchanged_by_cli"]
                   and not rep["real_appdata_pixelorama_changed"]["ours"])
    return rep
