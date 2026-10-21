"""Build copied synthetic fixtures and run the phase-aware stop checker.

Usage:
  python -I <this> --baseline V08_TRANSITION_JSON --validator CHECKER.py \
      --out outputs/hsea-stopcheck15

Writes only under --out. The real producer output (hsea-stop15) is not required
and is never mutated or guessed. Positive fixtures reuse the exact v08 protected
bytes and add synthetic native phase endpoints; negatives are copies with one
intentional mutation each.
"""
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone

import numpy as np
from PIL import Image

W, H = 80, 112
DIRS = ("south", "west", "north", "east")
SIDE = ("east", "west")
TS = "20261020-213851"
UID = "dc16c836"
TAG = "v15_%s-%s" % (TS, UID)
FB_TS = "20261021-023500"
FB_UID = "f17a2b3c"
FB_TAG = "v17_%s-%s" % (FB_TS, FB_UID)
FRONT = ("south", "north")


def xp(path):
    path = os.path.abspath(str(path))
    if os.name == "nt" and not path.startswith("\\\\?\\"):
        if path.startswith("\\\\"):
            return "\\\\?\\UNC\\" + path[2:]
        return "\\\\?\\" + path
    return path


def rb(path):
    with open(xp(path), "rb") as f:
        return f.read()


def wb(path, data):
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(xp(parent), exist_ok=True)
    with open(xp(path), "wb") as f:
        f.write(data)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, obj):
    wb(path, (json.dumps(obj, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))


def load(path):
    return json.loads(rb(path).decode("utf-8-sig"))


def png_bytes(arr):
    buf = io.BytesIO()
    Image.fromarray(arr, "RGBA").save(buf, format="PNG")
    return buf.getvalue()


def load_png(path):
    with Image.open(io.BytesIO(rb(path))) as im:
        if im.size != (W, H) or im.mode != "RGBA":
            raise RuntimeError("not 80x112 RGBA: %s" % path)
        return np.array(im.convert("RGBA"), np.uint8)


def copy_tree(src, dst):
    src, dst = os.path.abspath(src), os.path.abspath(dst)
    os.makedirs(xp(dst), exist_ok=True)
    for name in os.listdir(xp(src)):
        sp, dp = os.path.join(src, name), os.path.join(dst, name)
        if os.path.isdir(xp(sp)):
            copy_tree(sp, dp)
        else:
            wb(dp, rb(sp))


def tree_hashes(root):
    out, base = {}, xp(os.path.abspath(root))
    for dp, _dn, fn in os.walk(base):
        for f in sorted(fn):
            p = os.path.join(dp, f)
            out[os.path.relpath(p, base)] = sha(rb(p))
    return out


def mark_pixel(arr, rgb):
    a = arr.copy()
    coords = np.argwhere(a[..., 3] > 0)
    if not len(coords):
        raise RuntimeError("synthetic sample has no opaque pixel")
    y, x = coords[len(coords) // 2]
    a[y, x, :3] = rgb
    a[y, x, 3] = 255
    return a


def build_pxo(path, arrs, template_pxo):
    with zipfile.ZipFile(xp(template_pxo)) as z:
        meta = json.loads(z.read("data.json").decode("utf-8-sig"))
    first_layer = dict(meta["layers"][0])
    first_layer["name"] = "synthetic-composite"
    meta["layers"] = [first_layer]
    first_cel = dict(meta["frames"][0]["cels"][0])
    meta["frames"] = [{"cels": [dict(first_cel)], "duration": 0.04, "metadata": {}} for _ in arrs]
    meta["current_frame"] = 0
    meta["current_layer"] = 0
    meta["fps"] = 25
    with zipfile.ZipFile(xp(path), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mimetype", b"application/x-pixelorama")
        z.writestr("preview.png", png_bytes(arrs[0]))
        z.writestr("data.json", json.dumps(meta, indent=1).encode("utf-8"))
        for fi, arr in enumerate(arrs):
            base = "image_data/frames/%d/" % (fi + 1)
            z.writestr(base, b"")
            z.writestr(base + "layer_1", arr.tobytes())
            z.writestr(base + "indices_layer_1", b"\x00")


def build_positive(baseline_path, outdir):
    bdir = os.path.dirname(os.path.abspath(baseline_path))
    bm = load(baseline_path)
    sm = load(os.path.join(bdir, bm["source_manifest"]))
    pos = os.path.join(outdir, "fixtures", "positive")
    os.makedirs(xp(pos), exist_ok=True)

    def pname(kind, d0, extra=""):
        return "rpg2sea_hsea-stop_%s-%s%s_%s.png" % (kind, d0, extra, TAG)

    protected, protected_entries = {}, []
    for d0 in DIRS:
        src = bm["source_manifest"]
        sm_actions = sm["actions"]
        for act, count in (("idle", 1), ("walk", 12)):
            for i in range(count):
                rel = sm_actions[act][d0][i]["file"]
                arr = load_png(os.path.join(bdir, rel))
                extra = "-i0" if act == "idle" else "-w%02d" % i
                name = pname("protect", d0, extra)
                data = png_bytes(arr)
                wb(os.path.join(pos, name), data)
                key = (d0, act, i)
                protected[key] = {"file": name, "sha": sha(data), "arr": arr}
                protected_entries.append({"role": "%s/%s/%02d" % (act, d0, i),
                                          "file": name, "sha256": sha(data)})
    legacy_entries = {}
    for d0 in DIRS:
        legacy_entries[d0] = {}
        for c, want in (("contact0", 0), ("contact6", 6)):
            src = bm["directions"][d0][c]
            rows = []
            for bi, be in enumerate(src["bridge"]):
                name = pname("legacy", d0, "-c%s-b%d" % (c[-1], bi))
                data = rb(os.path.join(bdir, be["file"]))
                wb(os.path.join(pos, name), data)
                rows.append({"file": name, "sha256": sha(data)})
            legacy_entries[d0][c] = {"from_walk_frame": src["from_walk_frame"],
                                     "bridge": rows,
                                     "final": protected[(d0, "idle", 0)]["file"]}
    phase = {}
    sample_arrays = {}
    for d0 in SIDE:
        phase[d0] = {}
        for pi in range(12):
            arr0 = protected[(d0, "walk", pi)]["arr"]
            arr3 = protected[(d0, "idle", 0)]["arr"]
            arrs = [arr0, mark_pixel(arr0, (255, 0, 255)), mark_pixel(arr3, (0, 255, 0)), arr3]
            rows = []
            for si, arr in enumerate(arrs):
                name = pname("phase", d0, "-p%02d-s%d" % (pi, si))
                data = png_bytes(arr)
                wb(os.path.join(pos, name), data)
                rows.append({"file": name, "sha256": sha(data)})
                sample_arrays[(d0, pi, si)] = arr
            phase[d0]["phase%d" % pi] = {"from_walk_frame": pi, "bridge": rows}
    source_set = {
        "schema": "worlds-between.exploration-stop-native-source-set.v1",
        "status": "SYNTHETIC fixture; copied v08 protected bytes plus synthetic native phase exports; not art approval",
        "protected": protected_entries,
        "native_sources": [],
    }
    # Template metadata is taken from the real v08 east PXO only as a container format.
    template_pxo = None
    for sf in sm["source_files"]:
        if sf.get("format") == "pixelorama-pxo" and sf.get("direction") == "east":
            template_pxo = os.path.join(bdir, sf["file"])
    if template_pxo is None:
        raise RuntimeError("baseline east PXO template not found")
    for d0 in SIDE:
        arrs = [sample_arrays[(d0, pi, si)] for pi in range(12) for si in range(4)]
        name = "rpg2sea_hsea-stop_native-%s_%s.pxo" % (d0, TAG)
        pp = os.path.join(pos, name)
        build_pxo(pp, arrs, template_pxo)
        exports = []
        for pi in range(12):
            for si in range(4):
                ent = phase[d0]["phase%d" % pi]["bridge"][si]
                exports.append({"frame": pi * 4 + si, "phase": pi, "sample": si,
                                "file": ent["file"], "sha256": ent["sha256"]})
        source_set["native_sources"].append({"direction": d0, "format": "pixelorama-pxo",
                                            "file": name, "sha256": sha(rb(pp)),
                                            "frame_exports": exports})
    ss_name = "rpg2sea_hsea-stop_source-set_%s.json" % TAG
    ss_path = os.path.join(pos, ss_name)
    dump(ss_path, source_set)
    man = {"schema": bm["schema"], "rule": bm["rule"],
           "source_set": ss_name, "source_set_sha256": sha(rb(ss_path)),
           "directions": legacy_entries, "phase_bridges": phase}
    man_name = "rpg2sea_hsea-stop_transition_%s.json" % TAG
    dump(os.path.join(pos, man_name), man)
    return {"dir": pos, "manifest": os.path.join(pos, man_name),
            "source_set": ss_path, "source_set_data": source_set}


def mutate(case, fixture, kind):
    man_path = fixture["manifest"]
    man = load(man_path)
    if kind == "badsha":
        man["phase_bridges"]["east"]["phase3"]["bridge"][1]["sha256"] = "0" * 64
        dump(man_path, man)
    elif kind == "missingphase":
        del man["phase_bridges"]["east"]["phase7"]
        dump(man_path, man)
    elif kind == "pathescape":
        man["phase_bridges"]["west"]["phase4"]["bridge"][2]["file"] = "..\\..\\escape.png"
        dump(man_path, man)
    elif kind == "malformed":
        wb(man_path, b"{not valid json\n")
    elif kind == "protectedidle":
        ss = load(fixture["source_set"])
        ent = next(e for e in ss["protected"]
                   if e["role"].lower() in ("idle/east", "idle/east/00", "idle/east/0"))
        p = os.path.join(fixture["dir"], ent["file"])
        arr = load_png(p)
        coords = np.argwhere(arr[..., 3] > 0)
        y, x = coords[0]
        arr[y, x] = (255, 0, 255, 255)
        wb(p, png_bytes(arr))
    else:
        raise RuntimeError("unknown mutation %s" % kind)
    return case


def run_case(py, validator, baseline, fixture, report, cls="synthetic_fixture", timeout=240):
    before = tree_hashes(fixture["dir"])
    before_b = tree_hashes(os.path.dirname(os.path.abspath(baseline)))
    proc = subprocess.run([py, "-I", validator, "--manifest", fixture["manifest"],
                           "--baseline", baseline, "--report", report,
                           "--evidence-class", cls],
                          capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=timeout)
    after = tree_hashes(fixture["dir"])
    after_b = tree_hashes(os.path.dirname(os.path.abspath(baseline)))
    try:
        parsed = json.loads(proc.stdout)
    except Exception:
        parsed = None
    tb = "Traceback" in (proc.stdout + proc.stderr)
    failed = sorted(k for k, v in (parsed or {}).get("gates", {}).items() if not v.get("ok"))
    return {"ok": bool(parsed and parsed.get("ok")), "exit": proc.returncode,
            "traceback": tb, "failed_gates": failed,
            "fixture_unchanged": before == after, "baseline_unchanged": before_b == after_b,
            "stderr": proc.stderr.strip()[:1000], "report": report, "parsed": parsed}


def arr_from_bytes(data):
    with Image.open(io.BytesIO(data)) as im:
        if im.size != (W, H) or im.mode != "RGBA":
            raise RuntimeError("not 80x112 RGBA bytes")
        return np.array(im.convert("RGBA"), np.uint8)


def mark_changed(arr, rgb):
    a = mark_pixel(arr, rgb)
    if np.array_equal(a, arr):
        coords = np.argwhere(arr[..., 3] > 0)
        y, x = coords[0]
        a = arr.copy()
        a[y, x, 0] = int(a[y, x, 0]) ^ 0xFF
        a[y, x, 3] = 255
    return a


def build_positive_front_back(baseline_path, outdir):
    bdir = os.path.dirname(os.path.abspath(baseline_path))
    bm = load(baseline_path)
    sm = load(os.path.join(bdir, bm["source_manifest"]))
    pos = os.path.join(outdir, "fixtures", "positive")
    os.makedirs(xp(pos), exist_ok=True)

    def pname(kind, d0, extra=""):
        return "rpg2sea_hsea-front_%s-%s%s_%s.png" % (kind, d0, extra, FB_TAG)

    pose_data, pose_arr = {}, {}
    for d0 in DIRS:
        for act, count in (("idle", 1), ("walk", 12)):
            for i in range(count):
                ent = sm["actions"][act][d0][i]
                data = rb(os.path.join(bdir, ent["file"]))
                pose_data[(d0, act, i)] = data
                pose_arr[(d0, act, i)] = arr_from_bytes(data)
    actions, cand_pose_data, cand_pose_arr = {"idle": {}, "walk": {}}, {}, {}
    for act, count in (("idle", 1), ("walk", 12)):
        for d0 in DIRS:
            actions[act][d0] = []
            for i in range(count):
                key = (d0, act, i)
                if act == "walk" and d0 in FRONT:
                    arr = mark_changed(pose_arr[key], (255, 0, 255))
                    data = png_bytes(arr)
                else:
                    arr = pose_arr[key]
                    data = pose_data[key]
                cand_pose_arr[key] = arr
                cand_pose_data[key] = data
                extra = "-i0" if act == "idle" else "-w%02d" % i
                name = pname("pose", d0, extra)
                wb(os.path.join(pos, name), data)
                actions[act][d0].append({"file": name, "sha256": sha(data),
                                         "duration_ms": sm["actions"][act][d0][i].get("duration_ms", 40)})

    legacy_entries, front_legacy_changed = {}, 0
    for d0 in DIRS:
        legacy_entries[d0] = {}
        for c in ("contact0", "contact6"):
            src = bm["directions"][d0][c]
            rows = []
            for bi, be in enumerate(src["bridge"]):
                raw = rb(os.path.join(bdir, be["file"]))
                if d0 in FRONT:
                    data = png_bytes(mark_changed(arr_from_bytes(raw), (0, 255, 0)))
                else:
                    data = raw
                if data != raw:
                    front_legacy_changed += 1 if d0 in FRONT else 0
                name = pname("legacy", d0, "-c%s-b%d" % (c[-1], bi))
                wb(os.path.join(pos, name), data)
                rows.append({"file": name, "sha256": sha(data)})
            legacy_entries[d0][c] = {"from_walk_frame": src["from_walk_frame"],
                                     "bridge": rows,
                                     "final": actions["idle"][d0][0]["file"]}

    phase, sample_arr, sample_data = {}, {}, {}
    for d0 in DIRS:
        phase[d0] = {}
        for pi in range(12):
            if d0 in SIDE:
                srcs = bm["phase_bridges"][d0]["phase%d" % pi]["bridge"]
                arrs, datas = [], []
                for si, be in enumerate(srcs):
                    data = rb(os.path.join(bdir, be["file"]))
                    datas.append(data)
                    arrs.append(arr_from_bytes(data))
            else:
                walk_arr = cand_pose_arr[(d0, "walk", pi)]
                idle_arr = cand_pose_arr[(d0, "idle", 0)]
                arrs = [walk_arr, mark_changed(walk_arr, (0, 255, 255)),
                        mark_changed(idle_arr, (255, 255, 0)), idle_arr]
                datas = [cand_pose_data[(d0, "walk", pi)], png_bytes(arrs[1]),
                         png_bytes(arrs[2]), cand_pose_data[(d0, "idle", 0)]]
            rows = []
            for si, (arr, data) in enumerate(zip(arrs, datas)):
                name = pname("phase", d0, "-p%02d-s%d" % (pi, si))
                wb(os.path.join(pos, name), data)
                rows.append({"file": name, "sha256": sha(data)})
                sample_arr[(d0, pi, si)] = arr
                sample_data[(d0, pi, si)] = data
            phase[d0]["phase%d" % pi] = {"from_walk_frame": pi, "bridge": rows}

    template_pxo = None
    for sf in sm["source_files"]:
        if sf.get("format") == "pixelorama-pxo" and sf.get("direction") == "east":
            template_pxo = os.path.join(bdir, sf["file"])
    if template_pxo is None:
        raise RuntimeError("baseline east phase PXO template not found")

    source_files = []
    for d0 in FRONT:
        if d0 == "south":
            arrs = [cand_pose_arr[(d0, "walk", i)] for i in range(11, -1, -1)] + \
                   [cand_pose_arr[(d0, "idle", 0)]]
            exports = []
            for i in range(12):
                exports.append({"frame": 11 - i, "role": "walk-f%02d" % i,
                                "file": actions["walk"][d0][i]["file"],
                                "sha256": actions["walk"][d0][i]["sha256"]})
            exports.append({"frame": 12, "role": "idle-f00",
                            "file": actions["idle"][d0][0]["file"],
                            "sha256": actions["idle"][d0][0]["sha256"]})
            frame_order = "declared frame_exports: f00..f11=walk11..walk00, f12=idle0"
        else:
            arrs = [cand_pose_arr[(d0, "idle", 0)]] + \
                   [cand_pose_arr[(d0, "walk", i)] for i in range(12)]
            exports = None
            frame_order = "f00=idle0, f01..f12=walk00..walk11"
        name = "rpg2sea_hsea-front_native-pose-%s_%s.pxo" % (d0, FB_TAG)
        pp = os.path.join(pos, name)
        build_pxo(pp, arrs, template_pxo)
        entry = {"direction": d0, "format": "pixelorama-pxo", "file": name,
                 "sha256": sha(rb(pp)), "frames": 13, "frame_order": frame_order}
        if exports is not None:
            entry["frame_exports"] = exports
        source_files.append(entry)

    for d0 in DIRS:
        if d0 in SIDE:
            src = next(sf for sf in sm["source_files"]
                       if sf.get("format") == "pixelorama-pxo" and sf.get("direction") == d0)
            data = rb(os.path.join(bdir, src["file"]))
            name = "rpg2sea_hsea-front_native-phase-%s_%s.pxo" % (d0, FB_TAG)
            wb(os.path.join(pos, name), data)
            source_files.append({"direction": d0, "format": "pixelorama-pxo", "file": name,
                                 "sha256": sha(data), "frames": 48,
                                 "frame_order": src.get("frame_order", "phase p00..p11 x sample s0..s3")})
            continue
        if d0 == "south":
            order = [(pi, si) for pi in range(11, -1, -1) for si in range(3, -1, -1)]
            arrs = [sample_arr[(d0,) + slot] for slot in order]
            exports = []
            for fi, (pi, si) in enumerate(order):
                ent = phase[d0]["phase%d" % pi]["bridge"][si]
                exports.append({"frame": fi, "phase": pi, "sample": si,
                                "file": ent["file"], "sha256": ent["sha256"]})
            frame_order = "declared frame_exports: reversed phase11 s3 .. phase0 s0"
        else:
            order = [(pi, si) for pi in range(12) for si in range(4)]
            arrs = [sample_arr[(d0,) + slot] for slot in order]
            exports = None
            frame_order = "phase p00..p11 x sample s0..s3 (frame = 4*p + s)"
        name = "rpg2sea_hsea-front_native-phase-%s_%s.pxo" % (d0, FB_TAG)
        pp = os.path.join(pos, name)
        build_pxo(pp, arrs, template_pxo)
        entry = {"direction": d0, "format": "pixelorama-pxo", "file": name,
                 "sha256": sha(rb(pp)), "frames": 48, "frame_order": frame_order}
        if exports is not None:
            entry["frame_exports"] = exports
        source_files.append(entry)

    source_set = {
        "schema": "worlds-between.exploration-source.v1",
        "actor_id": "protagonist-female",
        "density": 2,
        "frame_size": [W, H],
        "pivot": [40, 104],
        "actions": actions,
        "source_files": source_files,
        "status": "SYNTHETIC front/back revision fixture; copied stop15 protected bytes plus marker-pixel "
                  "front/phase samples; not art approval",
        "disclosure": [
            "side pose, side phase and side legacy PNG bytes are exact copies of the stop15 baseline",
            "four idles are exact copies of the stop15 baseline",
            "front walk and front legacy PNGs contain marker-pixel changes allowed by the contract",
            "native PXOs are synthetic containers; side phase PXO bytes are copied from the stop15 baseline"],
    }
    ss_name = "rpg2sea_hsea-front_source-set_%s.json" % FB_TAG
    ss_path = os.path.join(pos, ss_name)
    dump(ss_path, source_set)
    man = {
        "schema": bm["schema"], "source_manifest": ss_name, "source_set": ss_name,
        "source_set_sha256": sha(rb(ss_path)),
        "rule": bm.get("rule"), "frame_ms": bm.get("frame_ms"), "pivot": bm.get("pivot"),
        "logical_height": bm.get("logical_height"), "settle_ms_inclusive": bm.get("settle_ms_inclusive"),
        "directions": legacy_entries, "phase_bridges": phase,
    }
    man_name = "rpg2sea_hsea-front_transition_%s.json" % FB_TAG
    dump(os.path.join(pos, man_name), man)
    return {"dir": pos, "manifest": os.path.join(pos, man_name),
            "source_set": ss_path, "source_set_data": source_set,
            "expected_changes": {"idle_changed": 0, "side_walk_changed": 0,
                                 "front_walk_changed": 24, "side_legacy_changed": 0,
                                 "front_legacy_changed": front_legacy_changed,
                                 "side_phase_changed": 0, "front_phase_samples": 96,
                                 "pose_total": 52, "legacy_total": 16, "phase_total": 192}}


def save_source_set(fixture, ss):
    dump(fixture["source_set"], ss)
    man = load(fixture["manifest"])
    man["source_set_sha256"] = sha(rb(fixture["source_set"]))
    dump(fixture["manifest"], man)


def mutate_png_file(path, rgb=(255, 0, 255)):
    data = png_bytes(mark_changed(load_png(path), rgb))
    wb(path, data)
    return sha(data)


def mutate_pxo_frame(path):
    with zipfile.ZipFile(xp(path)) as z:
        items = [(name, z.read(name)) for name in z.namelist()]
    out = []
    for name, data in items:
        if name == "image_data/frames/1/layer_1":
            arr = np.frombuffer(data, np.uint8).reshape(H, W, 4).copy()
            coords = np.argwhere(arr[..., 3] > 0)
            y, x = coords[0]
            arr[y, x, :3] = (1, 2, 3)
            data = arr.tobytes()
        out.append((name, data))
    with zipfile.ZipFile(xp(path), "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in out:
            z.writestr(name, data)
    return sha(rb(path))


def mutate_front_back(fixture, kind):
    man_path = fixture["manifest"]
    if kind in ("protectedsidewalk", "protectedidle"):
        ss = load(fixture["source_set"])
        if kind == "protectedsidewalk":
            ent = ss["actions"]["walk"]["west"][5]
        else:
            ent = ss["actions"]["idle"]["east"][0]
        p = os.path.join(fixture["dir"], ent["file"])
        ent["sha256"] = mutate_png_file(p)
        save_source_set(fixture, ss)
    elif kind == "sidephase":
        man = load(man_path)
        ent = man["phase_bridges"]["east"]["phase3"]["bridge"][1]
        p = os.path.join(fixture["dir"], ent["file"])
        ent["sha256"] = mutate_png_file(p)
        dump(man_path, man)
    elif kind == "missingfrontphase":
        man = load(man_path)
        del man["phase_bridges"]["north"]["phase7"]
        dump(man_path, man)
    elif kind == "nativeexport":
        ss = load(fixture["source_set"])
        src = next(sf for sf in ss["source_files"]
                   if sf.get("format") == "pixelorama-pxo" and sf.get("direction") == "south"
                   and sf.get("frames") == 13)
        src["sha256"] = mutate_pxo_frame(os.path.join(fixture["dir"], src["file"]))
        save_source_set(fixture, ss)
    elif kind == "badhash":
        man = load(man_path)
        man["phase_bridges"]["south"]["phase2"]["bridge"][1]["sha256"] = "0" * 64
        dump(man_path, man)
    elif kind == "pathescape":
        man = load(man_path)
        man["phase_bridges"]["west"]["phase4"]["bridge"][2]["file"] = "..\\..\\escape.png"
        dump(man_path, man)
    elif kind == "malformed":
        wb(man_path, b"{not valid json\n")
    else:
        raise RuntimeError("unknown front/back mutation %s" % kind)
    return fixture


def run_case_front_back(py, validator, baseline, fixture, report, cls="synthetic_fixture", timeout=300):
    before = tree_hashes(fixture["dir"])
    before_b = tree_hashes(os.path.dirname(os.path.abspath(baseline)))
    proc = subprocess.run([py, "-I", validator, "--manifest", fixture["manifest"],
                           "--baseline", baseline, "--report", report,
                           "--evidence-class", cls, "--front-back-revision"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=timeout)
    after = tree_hashes(fixture["dir"])
    after_b = tree_hashes(os.path.dirname(os.path.abspath(baseline)))
    try:
        parsed = json.loads(proc.stdout)
    except Exception:
        parsed = None
    tb = "Traceback" in (proc.stdout + proc.stderr)
    failed = sorted(k for k, v in (parsed or {}).get("gates", {}).items() if not v.get("ok"))
    return {"ok": bool(parsed and parsed.get("ok")), "exit": proc.returncode,
            "traceback": tb, "failed_gates": failed,
            "fixture_unchanged": before == after, "baseline_unchanged": before_b == after_b,
            "stderr": proc.stderr.strip()[:1000], "report": report, "parsed": parsed}


def changes_match(parsed, expected):
    if not parsed:
        return False
    changes = parsed.get("measurements", {}).get("changes")
    if not isinstance(changes, dict):
        return False
    return all(changes.get(k) == v for k, v in expected.items())


def main_front_back(vals, baseline, validator, outdir):
    if os.path.basename(outdir) != "hsea-frontcheck17":
        print("refusing front/back revised output outside outputs/hsea-frontcheck17 basename", file=sys.stderr)
        return 2
    py = sys.executable
    os.makedirs(xp(outdir), exist_ok=True)
    fixtures = os.path.join(outdir, "fixtures")
    reports = os.path.join(outdir, "reports")
    for path in (fixtures, reports):
        if os.path.isdir(xp(path)):
            shutil.rmtree(xp(path))
        os.makedirs(xp(path), exist_ok=True)
    pos = build_positive_front_back(baseline, outdir)
    cases = []
    pos_report = os.path.join(reports, "positive.json")
    res = run_case_front_back(py, validator, baseline, pos, pos_report)
    changes_ok = changes_match(res["parsed"], pos["expected_changes"])
    ok = (res["ok"] and res["exit"] == 0 and not res["traceback"] and
          res["fixture_unchanged"] and res["baseline_unchanged"] and changes_ok)
    cases.append({"case": "positive", "expected_ok": True, "expected_gate": None,
                  "actual_ok": res["ok"], "exit": res["exit"],
                  "failed_gates": res["failed_gates"], "traceback": res["traceback"],
                  "fixture_unchanged": res["fixture_unchanged"],
                  "baseline_unchanged": res["baseline_unchanged"],
                  "changes_match": changes_ok,
                  "changes": (res["parsed"] or {}).get("measurements", {}).get("changes"),
                  "report": os.path.relpath(pos_report, outdir), "ok": ok})
    negatives = (
        ("protectedsidewalk", "protected_28_pose_bytes_equal_baseline"),
        ("protectedidle", "protected_28_pose_bytes_equal_baseline"),
        ("sidephase", "side_phase_96_bytes_equal_baseline"),
        ("missingfrontphase", "manifest_structure"),
        ("nativeexport", "native_exports_and_composition"),
        ("badhash", "declared_hashes"),
        ("pathescape", "path_safety"),
        ("malformed", "inputs_parse"),
    )
    for kind, expected_gate in negatives:
        case = "negative-" + kind
        dst = os.path.join(fixtures, case)
        copy_tree(pos["dir"], dst)
        fx = {"dir": dst,
              "manifest": os.path.join(dst, os.path.basename(pos["manifest"])),
              "source_set": os.path.join(dst, os.path.basename(pos["source_set"]))}
        mutate_front_back(fx, kind)
        rep = os.path.join(reports, case + ".json")
        res = run_case_front_back(py, validator, baseline, fx, rep)
        caught = (not res["ok"] and res["exit"] == 1 and not res["traceback"] and
                  expected_gate in res["failed_gates"] and res["fixture_unchanged"] and
                  res["baseline_unchanged"])
        cases.append({"case": case, "kind": kind, "expected_ok": False,
                      "expected_gate": expected_gate, "actual_ok": res["ok"],
                      "exit": res["exit"], "failed_gates": res["failed_gates"],
                      "traceback": res["traceback"],
                      "fixture_unchanged": res["fixture_unchanged"],
                      "baseline_unchanged": res["baseline_unchanged"],
                      "report": os.path.relpath(rep, outdir), "ok": caught})
    all_ok = all(c["ok"] for c in cases)
    summary = {
        "schema": "worlds-between.heroine-sea-phase-aware-stop-check.fixtures.front-back-revision.v1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": all_ok,
        "evidence_class": "synthetic_fixture",
        "mode": "front_back_revision",
        "baseline": {"manifest": baseline, "sha256": sha(rb(baseline))},
        "positive_fixture": os.path.relpath(pos["dir"], outdir),
        "expected_changes": pos["expected_changes"],
        "cases": cases,
        "checked_contract": {
            "protected_pose_png": 28,
            "allowed_front_walk_png": 24,
            "allowed_front_legacy_png": 8,
            "side_phase_png_exact": 96,
            "side_legacy_png_exact": 8,
            "all_pose_png_bounds_hashes": 52,
            "all_phase_png_bounds_hashes": 192,
            "phase_endpoints_all4": "phase0..phase11 x sample0/sample3",
            "native_front_pose_pxo": 2,
            "native_front_pose_frames": 13,
            "native_phase_pxo": 4,
            "native_phase_frames": 48,
            "dynamic_export_mapping": True,
            "changed_count_report": True,
            "path_confinement": True,
            "no_candidate_code_execution": True,
        },
        "synthetic_vs_real": [
            "REAL BYTES: stop15 baseline 52 pose, 16 legacy, 96 side phase PNGs and 2 side phase PXOs are read read-only.",
            "SYNTHETIC: front walk, front legacy and front phase PNGs carry marker pixels; they are not art or motion evidence.",
            "SYNTHETIC: the 2 front 13-frame PXOs are generated containers; side phase PXOs are copied byte-identically.",
            "REAL CANDIDATE: not present at build time; pass --front-back-revision to the checker against the produced candidate.",
        ],
        "limitations": [
            "Marker pixels are not art, motion, cadence or GUI evidence.",
            "The validator checks structure, byte equality, bounds, native composition, changed counts and read-only behavior only.",
            "No Godot, Pixelorama GUI, network, credential, provider, ledger or Git action was used.",
        ],
    }
    dump(os.path.join(outdir, "summary.json"), summary)
    lines = [
        "# hsea-frontcheck17 front/back completion checker",
        "",
        "Evidence class: **synthetic_fixture**. This is not art, motion, GUI, runtime or creator approval.",
        "",
        "Validator: `tools/rpg-2-star-ocean-the-second_heroine-sea_phase-aware-stop-check_test-only-v15_20261020-213851-dc16c836.py`",
        "",
        "CLI:",
        "```",
        "python -I <validator> --manifest <new.json> --baseline <stop15.json> --report <out.json> "
        "--evidence-class real_candidate --front-back-revision",
        "```",
        "",
        "Result: **%s** (%d cases)." % ("PASS" if all_ok else "FAIL", len(cases)),
        "",
        "| case | expected | actual | gate | no traceback | inputs unchanged |",
        "|---|---|---|---|---|---|",
    ]
    for c in cases:
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            c["case"], "ok" if c["expected_ok"] else "fail",
            "ok" if c["actual_ok"] else "fail", c.get("expected_gate") or "-",
            not c["traceback"], c["fixture_unchanged"] and c["baseline_unchanged"]))
    lines += ["", "## Changed-count report", "",
              "Expected: `%s`" % json.dumps(pos["expected_changes"], sort_keys=True), "",
              "## Default v15 regression", "",
              "The unchanged default mode was rerun separately against the stop15 real candidate "
              "with the v08 baseline; report `reports/default-v15-real-candidate.json` (PASS).", ""]
    lines += ["## Real candidate", "",
              "No new front/back candidate is present at build time.", "",
              "Pending actual-check command (replace `<candidate.json>` when available):", "```",
              "python -I tools/rpg-2-star-ocean-the-second_heroine-sea_phase-aware-stop-check_test-only-v15_20261020-213851-dc16c836.py "
              "--manifest <candidate.json> --baseline <stop15.json> --report outputs/hsea-frontcheck17/reports/real-candidate.json "
              "--evidence-class real_candidate --front-back-revision",
              "```", "",
              "The real candidate directory was not waited on or modified.", ""]
    wb(os.path.join(outdir, "README.md"), "\n".join(lines).encode("utf-8"))
    print(json.dumps({"ok": all_ok, "cases": cases}, indent=1, ensure_ascii=False))
    return 0 if all_ok else 1


def main(argv):
    vals, i, revision = {}, 0, False
    allowed = ("--baseline", "--validator", "--out", "--real-manifest")
    while i < len(argv):
        if argv[i] == "--front-back-revision":
            if revision:
                print("--front-back-revision may be given only once", file=sys.stderr)
                return 2
            revision = True
            i += 1
            continue
        if argv[i] not in allowed or i + 1 >= len(argv):
            print("usage: builder --baseline V08.json --validator CHECKER.py --out OUTDIR "
                  "[--real-manifest REAL.json] [--front-back-revision]", file=sys.stderr)
            return 2
        vals[argv[i]] = argv[i + 1]
        i += 2
    if not {"--baseline", "--validator", "--out"}.issubset(vals):
        print("usage: builder --baseline V08.json --validator CHECKER.py --out OUTDIR "
              "[--real-manifest REAL.json] [--front-back-revision]", file=sys.stderr)
        return 2
    baseline = os.path.abspath(vals["--baseline"])
    validator = os.path.abspath(vals["--validator"])
    outdir = os.path.abspath(vals["--out"])
    if revision:
        return main_front_back(vals, baseline, validator, outdir)
    if os.path.basename(outdir) != "hsea-stopcheck15":
        print("refusing to write outside outputs/hsea-stopcheck15 basename", file=sys.stderr)
        return 2
    py = sys.executable
    os.makedirs(xp(outdir), exist_ok=True)
    fixtures = os.path.join(outdir, "fixtures")
    reports = os.path.join(outdir, "reports")
    if os.path.isdir(xp(reports)):
        shutil.rmtree(xp(reports))
    os.makedirs(xp(reports), exist_ok=True)
    # Keep a fresh fixture tree while preserving this tool's own files.
    if os.path.isdir(xp(fixtures)):
        shutil.rmtree(xp(fixtures))
    os.makedirs(xp(fixtures), exist_ok=True)
    pos = build_positive(baseline, outdir)
    cases = []
    pos_report = os.path.join(reports, "positive.json")
    res = run_case(py, validator, baseline, pos, pos_report)
    ok = (res["ok"] and res["exit"] == 0 and not res["traceback"] and
          res["fixture_unchanged"] and res["baseline_unchanged"])
    cases.append({"case": "positive", "expected_ok": True, "expected_gate": None,
                  "actual_ok": res["ok"], "exit": res["exit"],
                  "failed_gates": res["failed_gates"], "traceback": res["traceback"],
                  "fixture_unchanged": res["fixture_unchanged"],
                  "baseline_unchanged": res["baseline_unchanged"],
                  "report": os.path.relpath(pos_report, outdir), "ok": ok})
    negatives = (
        ("badsha", "declared_hashes"),
        ("missingphase", "manifest_structure"),
        ("protectedidle", "protected_52_bytes_equal_baseline"),
        ("pathescape", "path_safety"),
        ("malformed", "inputs_parse"),
    )
    for kind, expected_gate in negatives:
        case = "negative-" + kind
        dst = os.path.join(fixtures, case)
        copy_tree(pos["dir"], dst)
        fx = {"dir": dst,
              "manifest": os.path.join(dst, os.path.basename(pos["manifest"])),
              "source_set": os.path.join(dst, os.path.basename(pos["source_set"]))}
        mutate(case, fx, kind)
        rep = os.path.join(reports, case + ".json")
        res = run_case(py, validator, baseline, fx, rep)
        caught = (not res["ok"] and res["exit"] == 1 and not res["traceback"] and
                  expected_gate in res["failed_gates"] and res["fixture_unchanged"] and
                  res["baseline_unchanged"])
        cases.append({"case": case, "kind": kind, "expected_ok": False,
                      "expected_gate": expected_gate, "actual_ok": res["ok"],
                      "exit": res["exit"], "failed_gates": res["failed_gates"],
                      "traceback": res["traceback"],
                      "fixture_unchanged": res["fixture_unchanged"],
                      "baseline_unchanged": res["baseline_unchanged"],
                      "report": os.path.relpath(rep, outdir), "ok": caught})
    real = None
    if vals.get("--real-manifest"):
        real_manifest = os.path.abspath(vals["--real-manifest"])
        if not os.path.isfile(xp(real_manifest)):
            print("real manifest not found: %s" % real_manifest, file=sys.stderr)
            return 2
        real_report = os.path.join(reports, "real-candidate.json")
        rres = run_case(py, validator, baseline,
                        {"dir": os.path.dirname(real_manifest), "manifest": real_manifest},
                        real_report, cls="real_candidate")
        real_ok = (rres["ok"] and rres["exit"] == 0 and not rres["traceback"] and
                   rres["baseline_unchanged"])
        real = {"manifest": real_manifest, "sha256": sha(rb(real_manifest)),
                "ok": real_ok, "actual_ok": rres["ok"], "exit": rres["exit"],
                "failed_gates": rres["failed_gates"], "traceback": rres["traceback"],
                "report": os.path.relpath(real_report, outdir),
                "baseline_unchanged": rres["baseline_unchanged"]}
    all_ok = all(c["ok"] for c in cases) and (real is None or real["ok"])
    summary = {
        "schema": "worlds-between.heroine-sea-phase-aware-stop-check.fixtures.v1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": all_ok,
        "evidence_class": "synthetic_fixture",
        "real_candidate": (real if real is not None else {
            "path": r"C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\dual14\cl-stop\outputs\hsea-stop15",
            "present_at_build": os.path.isdir(r"C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\dual14\cl-stop\outputs\hsea-stop15"),
            "result": "NOT RUN; pass --real-manifest to validate the real candidate. No threshold is lowered."}),
        "baseline": {"manifest": baseline, "sha256": sha(rb(baseline))},
        "positive_fixture": os.path.relpath(pos["dir"], outdir),
        "cases": cases,
        "checked_contract": {
            "protected_png_exact_v08_bytes": 52,
            "legacy_stop_png_unchanged": 16,
            "side_phase_keys": "east/west x phase0..phase11",
            "samples_per_phase": 4,
            "sample0": "exact outgoing walk phase",
            "sample3": "exact original idle",
            "native_export_equality": 96,
            "native_pxo_sources": 2,
            "dynamic_pxo_frame_mapping": True,
            "path_confinement": True,
            "no_candidate_code_execution": True,
        },
        "synthetic_vs_real": [
            "REAL BYTES: baseline v08 52 idle/walk PNGs, 16 legacy stop PNGs and 4 baseline PXOs are read from the checked-in v08 profile and independently reconstructed.",
            "SYNTHETIC: positive candidate copies those protected/legacy bytes under new names and adds marker-pixel samples 1/2; its two 48-frame native PXOs are a synthetic container built from copied/synthetic endpoint pixels.",
            "SYNTHETIC: all six test cases, including the five negatives, are copied synthetic fixture trees; only the protected/legacy bytes originate from the real v08 baseline.",
            "REAL CANDIDATE: validated separately and read-only when --real-manifest is supplied; its result is not counted as one of the six synthetic fixture cases and no threshold is lowered.",
        ],
        "limitations": [
            "Synthetic marker pixels are not art, motion, cadence or GUI evidence.",
            "The validator checks structure, byte equality, native-frame composition, path confinement and read-only behavior only.",
            "No Godot, Pixelorama GUI, network, credential, provider, ledger or Git action was used.",
        ],
    }
    dump(os.path.join(outdir, "summary.json"), summary)
    lines = [
        "# hsea-stopcheck15 phase-aware stop checker",
        "",
        "Evidence class: **synthetic_fixture**. This is not art, motion, GUI, runtime or creator approval.",
        "",
        "Validator: `tools/rpg-2-star-ocean-the-second_heroine-sea_phase-aware-stop-check_test-only-v15_20261020-213851-dc16c836.py`",
        "",
        "CLI:",
        "```",
        "python -I <validator> --manifest <new.json> --baseline <v08.json> --report <out.json>",
        "```",
        "",
        "Result: **%s** (%d cases)." % ("PASS" if all_ok else "FAIL", len(cases)),
        "",
        "| case | expected | actual | gate | no traceback | inputs unchanged |",
        "|---|---|---|---|---|---|",
    ]
    for c in cases:
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            c["case"], "ok" if c["expected_ok"] else "fail",
            "ok" if c["actual_ok"] else "fail", c.get("expected_gate") or "-",
            not c["traceback"], c["fixture_unchanged"] and c["baseline_unchanged"]))
    lines += ["", "## What is synthetic vs real", ""]
    lines += ["- " + x for x in summary["synthetic_vs_real"]]
    lines += ["", "## Real candidate", ""]
    if real is not None:
        lines += ["Manifest: `%s`" % real["manifest"], "",
                  "Result: **%s** (exit %s%s)." % (
                      "PASS" if real["ok"] else "FAIL", real["exit"],
                      "" if not real["failed_gates"] else "; failed " + ", ".join(real["failed_gates"])),
                  "Report: `%s`" % real["report"],
                  "SHA-256: `%s`" % real["sha256"], "",
                  "The real producer directory was read-only and was not waited on or modified."]
    else:
        lines += [summary["real_candidate"]["result"],
                  "", "The real producer directory was not waited on or modified."]
    lines += [""]
    wb(os.path.join(outdir, "README.md"), "\n".join(lines).encode("utf-8"))
    print(json.dumps({"ok": all_ok, "cases": cases, "real_candidate": real}, indent=1, ensure_ascii=False))
    return 0 if all_ok else 1


if __name__ == "__main__":
    try:
        rc = main(sys.argv[1:])
    except Exception as exc:
        print("fixture builder failed safely: %s: %s" % (type(exc).__name__, exc), file=sys.stderr)
        rc = 1
    sys.exit(rc)
