"""Heroine Sea-of-Stars four-direction breathing-idle SUPPLEMENTAL source, idle21 v01. UNAPPROVED, editable, not runtime-wired.

Neutral source: the current front17 runtime set (rpg-2-star-ocean-the-second_hero-female_exploration-sprite-set_runtime-v01_
20261020-222654-d77f7769.json, sha256 pinned below), one idle PNG per direction, 80x112, density 2, pivot (40,104).
Frame 0 and the last frame are the exact idle PNG bytes. Every other sample is built only from that idle's own pixels
(no new colours, binary alpha kept, no resampling):
  S  shoulders    : rows Yn..Ys-1 move up 1 px (neck/scarf row Yn dropped, chest row Ys duplicated): scarf, shoulders
                    and chest rise 1 native px (half a logical px) while the head stays.
  L  chest lift   : every row above Ys moves up 1 px -> head, hair, scarf and shoulders together +1.
  P  peak         : L, then rows Yn-1..Ys-1 up 1 again -> head +1, shoulders/chest +2.
  s  shallow      : rows Yn..Yn+2 up 1 only (scarf/shoulder line), exhale tail.
Rows >= Ys (lower arms/hands, hips, legs, feet, pivot row) are the neutral bytes in every frame. Ys/Yn are picked per
direction inside fixed bands: Ys = row whose duplication differs least from its neighbours, Yn = row closest to the row
below it (least visible to drop).
Sequence (8 samples, 2400 ms, quick eased inhale, longer eased exhale):
  f0 neutral 400 | f1 S 220 | f2 L 180 | f3 P 320 | f4 L 260 | f5 S 220 | f6 s 300 | f7 neutral 500
Editable sources: one Pixelorama .pxo per direction (8 frames x layers locked-lower / breath-upper / guides[hidden,
locked]) and one .ora per direction holding the peak pose layers. Guides mark pivot and Ys only.

Usage: python -I <this> --front17 <dir with front17 set json> [--out-tag YYYYMMDD-HHMMSS]   author into game/data/hsea-idle21
       python -I <this> --front17 <dir> --verify <manifest.json>          rebuild in memory, compare every byte
       python -I <this> --front17 <dir> --native-check <manifest.json> --pixelorama <exe> --evidence <dir>
"""
import datetime, hashlib, io, json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PRE = "rpg-2-star-ocean-the-second_heroine-sea"
SET_NAME = "rpg-2-star-ocean-the-second_hero-female_exploration-sprite-set_runtime-v01_20261020-222654-d77f7769.json"
SET_SHA = "3ccf615a536fef4938dafa869ea7f454860a3dca72fdb0c6c566e03f4fea3fa1"
SCHEMA = "worlds-between.exploration-breathing-idle.supplemental.v1"
W, H, PIVOT, DENSITY, LOGICAL = 80, 112, (40, 104), 2, 48
DIRS = ("south", "north", "east", "west")
YS_BAND = {"south": (47, 55), "north": (44, 50), "east": (45, 54), "west": (45, 54)}   # chest rows (inclusive)
YN_BAND = {"south": (37, 42), "north": (37, 41), "east": (37, 41), "west": (37, 41)}   # neck/scarf rows (inclusive)
SEQ = [("neutral", 400), ("S", 220), ("L", 180), ("P", 320), ("L", 260), ("S", 220), ("s", 300), ("neutral", 500)]
LAYERS = ["locked-lower", "breath-upper", "guides"]
ZIP_DT = (2026, 10, 21, 15, 13, 38)
PX_VER = "v1.2.3-stable"
DIAG = ("ERROR", "WARNING", "SCRIPT ERROR", "Shader", "shader", "Parse Error", "Traceback")


def sha(b): return hashlib.sha256(b).hexdigest()
def xp(p):
    s = str(Path(p).resolve())
    return Path(s if s.startswith("\\\\?\\") or os.name != "nt" else "\\\\?\\" + s)
def dec(b): return np.array(Image.open(io.BytesIO(b)).convert("RGBA"))
def png(a):
    buf = io.BytesIO(); Image.fromarray(np.ascontiguousarray(a, np.uint8), "RGBA").save(buf, "PNG", optimize=False, compress_level=9)
    return buf.getvalue()


def rowdiff(a, y0, y1): return int((a[y0] != a[y1]).any(-1).sum())


def pick_rows(a, d):
    """Ys = chest row duplicated (fewest changes vs both neighbours); Yn = neck/scarf row dropped (closest to the row
    below it, so removing it is least visible)."""
    ys = min(range(YS_BAND[d][0], YS_BAND[d][1] + 1), key=lambda y: (rowdiff(a, y, y - 1) + rowdiff(a, y, y + 1), y))
    yn = min(range(YN_BAND[d][0], YN_BAND[d][1] + 1), key=lambda y: (rowdiff(a, y, y + 1), y))
    assert yn + 4 < ys, (d, yn, ys)
    return ys, yn, {"ys_neighbour_diff_px": rowdiff(a, ys, ys - 1) + rowdiff(a, ys, ys + 1), "yn_drop_diff_px": rowdiff(a, yn, yn + 1)}


def shift_band(a, top, bot):
    o = a.copy(); o[top:bot] = a[top + 1:bot + 1]; return o   # rows top..bot-1 up 1 px; row top dropped, row bot duplicated


def pose(a, ys, yn, kind):
    if kind == "neutral": return a.copy()
    if kind == "S": return shift_band(a, yn, ys)                   # scarf/shoulders/chest +1, head 0
    if kind == "s": return shift_band(a, yn, yn + 3)               # scarf/shoulder line +1 only
    if kind == "L": return shift_band(a, 0, ys)                    # everything above Ys +1 (head included)
    if kind == "P": return shift_band(shift_band(a, 0, ys), yn - 1, ys)   # head +1, shoulders/chest +2
    raise ValueError(kind)


def split_layers(arr, ys):
    lo = np.zeros_like(arr); lo[ys:] = arr[ys:]
    up = np.zeros_like(arr); up[:ys] = arr[:ys]
    g = np.zeros_like(arr); g[ys, :, :] = (255, 0, 255, 255)
    g[PIVOT[1], PIVOT[0] - 2:PIVOT[0] + 3] = (0, 255, 255, 255); g[PIVOT[1] - 2:PIVOT[1] + 3, PIVOT[0]] = (0, 255, 255, 255)
    return {"locked-lower": lo, "breath-upper": up, "guides": g}


def compose(L):
    c = np.zeros((H, W, 4), np.uint8)
    for n in LAYERS[:-1]:
        m = L[n][..., 3] == 255; c[m] = L[n][m]
    return c


def put(z, name, payload): z.writestr(zipfile.ZipInfo(name, ZIP_DT), payload, zipfile.ZIP_DEFLATED)


def make_pxo(frames, durs_ms, export_name):
    lj = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0, "clipping_mask": False,
           "effects": [], "locked": n != "breath-upper", "metadata": {}, "name": n, "new_cels_linked": False, "opacity": 1.0,
           "parent": -1, "type": 0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": n != "guides"} for n in LAYERS]
    fj = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0} for _ in LAYERS],
           "duration": ms / 100.0, "metadata": {}} for ms in durs_ms]
    ep = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"", "erase_unselected_area": "false",
          "export_json": "false", "export_layers": "0", "file_format": "0", "file_name": json.dumps(export_name),
          "frame_current_tag": "0", "include_tag_in_filename": "false", "interpolation": "0", "lines_count": "1",
          "new_dir_for_each_frame_tag": "false", "number_of_digits": "4", "number_of_frames": str(len(frames)),
          "orientation": "0", "repeat_count": "0", "resize": "100", "save_quality": "0.75", "separator_character": "\"_\"",
          "sheet_layers_as_separate_files": "false", "split_layers": "false"}
    data = {"author_company": "", "author_contact": "", "author_display_name": "", "author_real_name": "", "brushes": [],
            "color_mode": 5, "current_frame": 0, "current_layer": 1, "export_profile": ep, "fps": 10.0, "frames": fj,
            "guides": [], "layers": lj, "license": "", "metadata": {}, "next_keyframe_id": 0, "palettes": [],
            "pixelorama_version": PX_VER, "project_current_palette_name": "", "pxo_version": 7, "reference_images": [],
            "size_x": W, "size_y": H, "symmetry_points": [W - 1.0, H - 1.0], "tags": [], "tile_mode_x_basis_x": W,
            "tile_mode_x_basis_y": 0, "tile_mode_y_basis_x": 0, "tile_mode_y_basis_y": H, "tilesets": [], "user_data": "",
            "vanishing_points": []}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        put(z, "data.json", json.dumps(data, separators=(",", ":")))
        put(z, "mimetype", "application/x-pixelorama")
        put(z, "preview.png", png(compose(frames[0])))
        for fi, L in enumerate(frames, start=1):
            put(z, f"image_data/frames/{fi}/", b"")
            for li, n in enumerate(LAYERS, start=1):
                put(z, f"image_data/frames/{fi}/layer_{li}", np.ascontiguousarray(L[n]).tobytes())
                put(z, f"image_data/frames/{fi}/indices_layer_{li}", b"\x00")
    return buf.getvalue()


def decode_pxo(b):
    z = zipfile.ZipFile(io.BytesIO(b)); data = json.loads(z.read("data.json"))
    assert [l["name"] for l in data["layers"]] == LAYERS and (data["size_x"], data["size_y"]) == (W, H)
    return [compose({n: np.frombuffer(z.read(f"image_data/frames/{fi}/layer_{li}"), np.uint8).reshape(H, W, 4)
                     for li, n in enumerate(LAYERS, start=1)}) for fi in range(1, len(data["frames"]) + 1)]


def make_ora(L):
    st = ['<?xml version="1.0" encoding="UTF-8"?>', f'<image version="0.0.3" w="{W}" h="{H}" xres="72" yres="72">', "<stack>"]
    for n in reversed(LAYERS):
        st.append(f'<layer name="{n}" src="data/{n}.png" x="0" y="0" opacity="1.0" visibility="{"hidden" if n == "guides" else "visible"}" composite-op="svg:src-over"/>')
    st += ["</stack>", "</image>"]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", ZIP_DT), "image/openraster", zipfile.ZIP_STORED)
        put(z, "stack.xml", "\n".join(st) + "\n")
        for n in LAYERS: put(z, f"data/{n}.png", png(L[n]))
        c = png(compose(L)); put(z, "mergedimage.png", c); put(z, "Thumbnails/thumbnail.png", c)
    return buf.getvalue()


def build(front17, tag):
    uid = sha(("hsea-idle21-v01" + tag).encode())[:8]
    nm = lambda s, ext: f"{PRE}_{s}_unapproved-idle21-v01_{tag}-{uid}.{ext}"
    sb = (xp(front17) / SET_NAME).read_bytes()
    assert sha(sb) == SET_SHA, "front17 set json is not the pinned current set"
    sset = json.loads(sb.decode("utf-8"))
    assert sset["frame_size"] == [W, H] and sset["pivot"] == list(PIVOT) and sset["density"] == DENSITY
    files, dirs, prov, poses, checks = {}, {}, {}, {}, []
    for d in DIRS:
        ent = sset["actions"]["idle"][d]; assert len(ent) == 1
        ib = (xp(front17) / ent[0]["file"]).read_bytes(); a = dec(ib)
        assert a.shape == (H, W, 4) and set(np.unique(a[..., 3]).tolist()) <= {0, 255}
        ys, yn, rowinfo = pick_rows(a, d)
        pal = {tuple(p) for p in a[a[..., 3] == 255].tolist()}
        prov[d] = {"neutral_file": f"game/data/hsea-front17/{ent[0]['file']}", "neutral_sha256": sha(ib),
                   "set_duration_ms": ent[0]["duration_ms"], "chest_row_ys": ys, "neck_row_yn": yn, **rowinfo}
        frames_L, lst, info = [], [], []
        for i, (kind, ms) in enumerate(SEQ):
            arr = pose(a, ys, yn, kind)
            b = ib if kind == "neutral" else png(arr)
            r = dec(b)
            assert np.array_equal(r, arr) and set(np.unique(r[..., 3]).tolist()) <= {0, 255}
            assert {tuple(p) for p in r[r[..., 3] == 255].tolist()} <= pal, (d, i, "new colour")
            assert np.array_equal(r[ys:], a[ys:]), (d, i, "rows >= Ys changed")
            fn = f"png/{nm(f'explore-{d}-breath-f{i:02d}', 'png')}"
            files[fn] = b; lst.append({"file": fn, "sha256": sha(b), "duration_ms": ms})
            L = split_layers(arr, ys); assert np.array_equal(compose(L), arr); frames_L.append(L)
            info.append({"frame": i, "pose": kind, "duration_ms": ms, "changed_px_vs_neutral": int((r != a).any(-1).sum()),
                         "head_rows_shift_px": {"neutral": 0, "S": 0, "s": 0, "L": 1, "P": 1}[kind],
                         "shoulder_chest_shift_px": {"neutral": 0, "S": 1, "s": 1, "L": 1, "P": 2}[kind],
                         "exact_neutral_bytes": kind == "neutral"})
        assert lst[0]["sha256"] == lst[-1]["sha256"] == sha(ib)
        dirs[d] = {"frames": lst}; poses[d] = info
        pf = f"src/{nm(f'explore-{d}-breath-layers', 'pxo')}"
        pb = make_pxo(frames_L, [ms for _, ms in SEQ], nm(f"explore-{d}-breath-export", "png")[:-4])
        for i, c in enumerate(decode_pxo(pb)): assert np.array_equal(c, dec(files[lst[i]["file"]])), (d, i)
        files[pf] = pb
        of = f"src/{nm(f'explore-{d}-breath-peak-layers', 'ora')}"
        files[of] = make_ora(frames_L[3])
        prov[d].update({"pxo": pf, "pxo_sha256": sha(pb), "ora_peak_f03": of, "ora_sha256": sha(files[of])})
    checks += ["front17 set json sha256 pinned; frame_size/pivot/density match",
               "f00 and f07 are the exact neutral idle bytes for every direction",
               "every frame 80x112 RGBA binary alpha, colours subset of that direction's neutral idle",
               "rows >= Ys (lower arms, hips, legs, feet, pivot row 104) byte-equal to neutral in every frame",
               "every frame equals its layer composite; every PXO frame decodes equal to its PNG"]
    tool = {"file": "tools/" + Path(__file__).name, "sha256TextLf": sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n"))}
    total = sum(ms for _, ms in SEQ)
    man = {"schema": SCHEMA, "status": "UNAPPROVED editable supplemental source; not runtime-wired; not creator-accepted",
           "actor_id": sset["actor_id"], "source_set": f"game/data/hsea-front17/{SET_NAME}", "source_set_sha256": SET_SHA,
           "frame_size": [W, H], "density": DENSITY, "pivot": list(PIVOT), "logical_height": LOGICAL,
           "total_ms": total, "loop": True, "directions": dirs,
           "method": {"poses": {"neutral": "exact idle bytes", "S": "rows Yn..Ys-1 up 1 (row Yn dropped, Ys duplicated): scarf/shoulders/chest +1, head 0",
                                "L": "rows above Ys up 1: head/hair/scarf/shoulders +1 together", "P": "L then rows Yn-1..Ys-1 up 1: head +1, shoulders/chest +2",
                                "s": "rows Yn..Yn+2 up 1: scarf/shoulder line +1 only"},
                      "sequence": [k for k, _ in SEQ], "ys_band": YS_BAND, "yn_band": YN_BAND,
                      "per_frame": poses},
           "neutral_provenance": prov, "author_tool": tool, "text_hash": "sha256 of raw PNG/PXO/ORA bytes; tool sha256TextLf",
           "self_checks": checks,
           "limitations": ["breathing amplitude is 1-2 native px (0.5-1 logical px); no sub-pixel shading change",
                           "S/P/s drop one neck/scarf row (hair hanging across that row loses that row while lifted)",
                           "hair/ponytail/scarf ride rigidly with the head in L/P; no follow-through lag",
                           "metric/byte checks only; no fluidity, GUI save/reopen or creator approval claim"]}
    mf = nm("explore-breathing-idle-manifest", "json")
    files[mf] = (json.dumps(man, indent=1) + "\n").encode("utf-8")
    return files, mf


def pixelorama_check(exe, man_path, front17, evid):
    run = man_path.parent; man = json.loads(man_path.read_bytes())
    real = os.path.join(os.environ.get("APPDATA", ""), "pixelorama")
    snap = lambda: sorted((str(p), p.stat().st_mtime_ns) for p in Path(real).rglob("*") if p.is_file() and p.name != ".running") if os.path.isdir(real) else []
    s0 = snap(); res = {}; tmp = tempfile.mkdtemp(prefix="wb-idle21-")
    try:
        for d in DIRS:
            pr = man["neutral_provenance"][d]; want = [dec((run / f["file"]).read_bytes()) for f in man["directions"][d]["frames"]]
            for kind, rel in (("pxo", pr["pxo"]), ("ora", pr["ora_peak_f03"])):
                for split in (False, True):
                    src = os.path.join(tmp, f"{d}.{kind}"); shutil.copyfile(xp(run / rel), src)
                    od = os.path.join(tmp, f"{d}-{kind}-{int(split)}"); os.makedirs(od)
                    env = dict(os.environ); env["APPDATA"] = tempfile.mkdtemp(prefix="wb-pxapp-")
                    args = [exe, "--headless", "--quit", "--", "--export"] + (["--split-layers"] if split else []) + ["-o", os.path.join(od, "f.png"), src]
                    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240, env=env)
                    shutil.rmtree(env["APPDATA"], ignore_errors=True)
                    outs = sorted(f for f in os.listdir(od) if f.lower().endswith(".png"))
                    arrs = [np.array(Image.open(os.path.join(od, f)).convert("RGBA")) for f in outs]
                    diag = sorted({l.strip() for l in (p.stdout + "\n" + p.stderr).splitlines() if any(m in l for m in DIAG)})
                    if kind == "pxo" and not split:
                        ok = p.returncode == 0 and len(arrs) == len(want) and all(np.array_equal(x, y) for x, y in zip(arrs, want))
                    elif kind == "ora" and not split:
                        ok = p.returncode == 0 and len(arrs) == 1 and np.array_equal(arrs[0], want[3])
                    else:
                        ys = pr["chest_row_ys"]; tgt = [want[3]] if kind == "ora" else want
                        need = [split_layers(t, ys)[n] for t in tgt for n in LAYERS[:-1]]
                        ok = p.returncode == 0 and all(any(np.array_equal(o, n) for o in arrs) for n in need)
                    res[f"{d}_{kind}_{'split' if split else 'flat'}"] = {"exit": p.returncode, "pngs": len(outs), "pass": bool(ok), "diagnostics": diag[:8]}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    out = {"schema": "worlds-between.native-export-check.v1", "manifest": man_path.name, "manifest_sha256": sha(man_path.read_bytes()),
           "pixelorama": exe, "appdata": "isolated temp APPDATA per run", "real_appdata_unchanged": snap() == s0,
           "results": res, "all_pixel_pass": all(r["pass"] for r in res.values()),
           "note": "pixel equality gated; application diagnostics recorded, not gated; no GUI reopen performed"}
    xp(evid).mkdir(parents=True, exist_ok=True)
    ef = xp(evid) / man_path.name.replace("explore-breathing-idle-manifest", "explore-breathing-idle-native-check")
    ef.write_bytes((json.dumps(out, indent=1) + "\n").encode("utf-8"))
    print(f"NATIVE {'PASS' if out['all_pixel_pass'] else 'FAIL'} runs={len(res)} diag_runs={sum(1 for r in res.values() if r['diagnostics'])} appdata_unchanged={out['real_appdata_unchanged']}")
    print(str(ef).replace("\\\\?\\", ""))
    return out["all_pixel_pass"]


def main():
    av = sys.argv; arg = lambda k, dflt=None: av[av.index(k) + 1] if k in av else dflt
    front17 = Path(arg("--front17", str(ROOT / "game/data/hsea-front17")))
    if "--verify" in av or "--native-check" in av:
        mp = Path(arg("--verify") or arg("--native-check")).resolve()
        tag = "-".join(mp.stem.split("_")[-1].split("-")[:2])
        files, mf = build(front17, tag); run = mp.parent
        bad = [n for n, b in files.items() if not (xp(run) / n).is_file() or (xp(run) / n).read_bytes() != b]
        on = {str(p.relative_to(xp(run))).replace("\\", "/") for p in xp(run).rglob("*") if p.is_file()}
        extra = sorted(on - set(files))
        print(f"VERIFY {'PASS' if not bad and not extra else 'FAIL'} rebuilt={len(files)} on_disk={len(on)} mismatched={bad[:4]} extra={extra[:4]}")
        if bad or extra: sys.exit(1)
        if "--native-check" in av:
            sys.exit(0 if pixelorama_check(arg("--pixelorama"), mp, front17, arg("--evidence")) else 1)
        return
    tag = arg("--out-tag") or datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    run = xp(ROOT / "game/data/hsea-idle21")
    files, mf = build(front17, tag)
    assert not any((run / n).exists() for n in files), "refusing to overwrite"
    for n, b in files.items():
        (run / n).parent.mkdir(parents=True, exist_ok=True); (run / n).write_bytes(b)
    print(f"WROTE {len(files)} files"); print(str(run / mf).replace("\\\\?\\", "")); print("manifest sha256", sha(files[mf]))


if __name__ == "__main__":
    main()
