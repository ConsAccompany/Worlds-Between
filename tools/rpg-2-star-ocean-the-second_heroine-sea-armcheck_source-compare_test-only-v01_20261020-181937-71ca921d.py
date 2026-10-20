"""Structural arm/source comparison for heroine-sea exploration manifests.

Usage:
  python -I <this> BASELINE source-manifest.json CANDIDATE source-manifest.json [--out report.json]
  python -I <this> --selftest BASELINE source-manifest.json

Read-only toward both inputs. Decodes Pixelorama PXO layers with zipfile/json
and compares reconstructed 80x112 RGBA frames with exported PNGs. Root correction: arm roles accept explicit *-arm-sleeve aliases and require nonempty WALK layers only;
exact-rest layers may legitimately own idle and final bridge. Structural
gates only; bridge/arm pixel distances are descriptive, not artistic thresholds.
"""
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import uuid
import zipfile
from datetime import datetime, timezone

import numpy as np
from PIL import Image

W, H, GROUND = 80, 112, 104
DIRS = ("south", "west", "north", "east")
SIDE = ("east", "west")
IDLE = ("south", "west", "north", "east")
WALKS = ("north", "south")
CONTACTS = ("contact0", "contact6")


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


def load_json(path):
    return json.loads(rb(path).decode("utf-8-sig"))


def dump_json(path, obj):
    wb(path, (json.dumps(obj, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))


def load_png(data):
    with Image.open(io.BytesIO(data)) as im:
        if im.size != (W, H) or im.mode != "RGBA":
            raise ValueError("not 80x112 RGBA (%s %s)" % (im.size, im.mode))
        return np.array(im.convert("RGBA"), dtype=np.uint8)


def save_png(path, arr):
    buf = io.BytesIO()
    Image.fromarray(arr, "RGBA").save(buf, format="PNG")
    wb(path, buf.getvalue())


def bbox_of(mask):
    ys, xs = np.nonzero(mask)
    if not len(xs):
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


def stats(arr):
    mask = arr[..., 3] > 0
    ys, xs = np.nonzero(mask)
    out = {"bbox": bbox_of(mask), "opaque": int(len(xs))}
    if len(xs):
        out["centroid"] = [round(float(xs.mean()), 2), round(float(ys.mean()), 2)]
    else:
        out["centroid"] = None
    return out


def child(directory, name):
    if not isinstance(name, str) or name in ("", ".", "..") or os.path.basename(name) != name:
        raise ValueError("unsafe file name %r" % (name,))
    return os.path.join(directory, name)


def load_manifest(path):
    mp = os.path.abspath(path)
    d = os.path.dirname(mp)
    m = load_json(mp)
    if m.get("schema") != "worlds-between.exploration-source.v1":
        raise ValueError("unexpected source schema %r" % (m.get("schema"),))
    if m.get("actor_id") != "protagonist-female" or m.get("density") != 2:
        raise ValueError("unexpected actor_id/density")
    if m.get("frame_size") != [W, H] or m.get("pivot") != [40, 104]:
        raise ValueError("unexpected frame_size/pivot")
    acts = m.get("actions")
    if not isinstance(acts, dict) or set(acts) != {"idle", "walk"}:
        raise ValueError("actions must contain idle/walk")
    for act in ("idle", "walk"):
        if not isinstance(acts.get(act), dict) or set(acts[act]) != set(DIRS):
            raise ValueError("%s must contain all four directions" % act)
    for d0 in DIRS:
        if not isinstance(acts["idle"][d0], list) or len(acts["idle"][d0]) != 1:
            raise ValueError("idle/%s must have exactly 1 frame" % d0)
        if not isinstance(acts["walk"][d0], list) or len(acts["walk"][d0]) != 12:
            raise ValueError("walk/%s must have exactly 12 frames" % d0)
    names = [n for n in os.listdir(xp(d)) if "stop-transition-manifest" in n and n.endswith(".json")]
    if len(names) != 1:
        raise ValueError("expected exactly one stop-transition manifest, found %d" % len(names))
    bpath = child(d, names[0])
    bm = load_json(bpath)
    if bm.get("schema") != "worlds-between.exploration-stop-transition.supplemental.v1":
        raise ValueError("unexpected transition schema")
    if not isinstance(bm.get("directions"), dict) or set(bm["directions"]) != set(DIRS):
        raise ValueError("transition directions incomplete")
    specs = {}
    final_ok = True
    bridge_entries = []
    for d0 in DIRS:
        specs[d0] = [{"frame": 0, "role": "idle", "file": acts["idle"][d0][0]["file"]}]
        for i, f in enumerate(acts["walk"][d0]):
            specs[d0].append({"frame": i + 1, "role": "walk%02d" % i, "file": f["file"]})
        cs = bm["directions"][d0]
        if set(cs) != set(CONTACTS):
            raise ValueError("transition contacts incomplete for %s" % d0)
        for ci, c in enumerate(CONTACTS):
            e = cs[c]
            if not isinstance(e.get("bridge"), list) or len(e["bridge"]) != 2:
                raise ValueError("bridge %s/%s must have 2 frames" % (d0, c))
            if e.get("final") != acts["idle"][d0][0]["file"]:
                final_ok = False
            for bi, b in enumerate(e["bridge"]):
                specs[d0].append({"frame": 13 + 2 * ci + bi, "role": "%s-b%d" % (c, bi),
                                  "file": b["file"], "sha256": b.get("sha256")})
                bridge_entries.append({"dir": d0, "contact": c, "index": bi,
                                       "file": b["file"], "sha256": b.get("sha256")})
    for d0 in DIRS:
        if [s["frame"] for s in specs[d0]] != list(range(17)):
            raise ValueError("frame order mismatch for %s" % d0)
    return {"path": mp, "dir": d, "raw": m, "actions": acts, "bridge": bm,
            "bridge_path": bpath, "specs": specs, "bridge_entries": bridge_entries,
            "final_ok": final_ok}


def decode_pxo(path):
    with zipfile.ZipFile(xp(path)) as z:
        znames = z.namelist()
        meta = json.loads(z.read("data.json").decode("utf-8-sig"))
        if meta.get("size_x") != W or meta.get("size_y") != H:
            raise ValueError("PXO canvas is not 80x112")
        layers = [l.get("name") for l in meta.get("layers", [])]
        if not layers or len(layers) != len(set(layers)):
            raise ValueError("PXO layers missing or duplicated")
        nframes = len(meta.get("frames", []))
        raw = {n: [] for n in layers}
        comps = []
        for fi in range(nframes):
            comp = np.zeros((H, W, 4), np.uint8)
            for li, name in enumerate(layers):
                ent = "image_data/frames/%d/layer_%d" % (fi + 1, li + 1)
                if ent not in znames:
                    raise ValueError("PXO missing %s" % ent)
                b = z.read(ent)
                if len(b) != W * H * 4:
                    raise ValueError("PXO layer size mismatch %s" % ent)
                a = np.frombuffer(b, np.uint8).reshape(H, W, 4).copy()
                raw[name].append(a)
                s = a[..., 3] > 0
                comp[s] = a[s]
            comps.append(comp)
        return {"layers": layers, "raw": raw, "comps": comps, "frames": nframes}


def prepare(path):
    man = load_manifest(path)
    pngs, raws, issues = {}, {}, []
    for d0 in DIRS:
        for spec in man["specs"][d0]:
            key = (d0, spec["frame"])
            try:
                b = rb(child(man["dir"], spec["file"]))
                pngs[key] = load_png(b)
                raws[key] = b
            except Exception as exc:
                issues.append("%s/%s: %s: %s" % (d0, spec["role"], type(exc).__name__, exc))
    pxo, src_bad, bridge_bad = {}, [], []
    srcs = man["raw"].get("source_files")
    if not isinstance(srcs, list):
        issues.append("source_files missing")
        srcs = []
    for sf in srcs:
        try:
            b = rb(child(man["dir"], sf["file"]))
            if sha(b) != sf.get("sha256"):
                src_bad.append(sf["file"])
            if sf.get("format") == "pixelorama-pxo":
                pxo[sf["direction"]] = decode_pxo(child(man["dir"], sf["file"]))
        except Exception as exc:
            issues.append("source %s: %s: %s" % (sf.get("file"), type(exc).__name__, exc))
    for e in man["bridge_entries"]:
        try:
            b = rb(child(man["dir"], e["file"]))
            if sha(b) != e.get("sha256"):
                bridge_bad.append(e["file"])
        except Exception as exc:
            issues.append("bridge %s: %s: %s" % (e["file"], type(exc).__name__, exc))
    counts = {"action_png": sum(len(man["actions"][a][d0]) for a in ("idle", "walk") for d0 in DIRS),
              "bridge_png": len(man["bridge_entries"]),
              "pxo": len(pxo), "ora": sum(1 for sf in srcs if sf.get("format") != "pixelorama-pxo")}
    counts["total_png"] = counts["action_png"] + counts["bridge_png"]
    return {"man": man, "png": pngs, "raw": raws, "pxo": pxo, "issues": issues,
            "src_bad": src_bad, "bridge_bad": bridge_bad, "counts": counts}


def raw_equal(a, b):
    return a is not None and b is not None and a == b


def compare_prepared(B, C):
    gates, meas = {}, {}

    def gate(name, ok, detail):
        gates[name] = {"ok": bool(ok), "detail": detail}

    gate("manifest_structure", not B["issues"] and not C["issues"],
         {"baseline_issues": B["issues"][:10], "candidate_issues": C["issues"][:10]})
    gate("png_counts_52_16", all(not x["issues"] for x in (B, C)) and
         all(x["counts"]["action_png"] == 52 and x["counts"]["bridge_png"] == 16 and
             x["counts"]["total_png"] == 68 and x["counts"]["pxo"] == 4 for x in (B, C)),
         {"baseline": B["counts"], "candidate": C["counts"]})
    hard_bad = []
    for label, x in (("baseline", B), ("candidate", C)):
        for key, arr in x["png"].items():
            a = arr[..., 3]
            if not np.isin(a, (0, 255)).all():
                hard_bad.append("%s/%s/%s soft alpha" % (label, key[0], key[1]))
            if a[0].any() or a[-1].any() or a[:, 0].any() or a[:, -1].any():
                hard_bad.append("%s/%s/%s border alpha" % (label, key[0], key[1]))
            if a[GROUND:].any():
                hard_bad.append("%s/%s/%s ground alpha" % (label, key[0], key[1]))
    gate("hard_alpha_ground_bounds", not hard_bad, hard_bad[:10])
    gate("declared_source_hashes", not B["src_bad"] and not C["src_bad"],
         {"baseline": B["src_bad"][:10], "candidate": C["src_bad"][:10]})
    gate("declared_bridge_hashes", not B["bridge_bad"] and not C["bridge_bad"],
         {"baseline": B["bridge_bad"][:10], "candidate": C["bridge_bad"][:10]})
    gate("pxo_frames_17", all(d0 in x["pxo"] and x["pxo"][d0]["frames"] == 17
                              for x in (B, C) for d0 in DIRS),
         {label: {d0: x["pxo"][d0]["frames"] for d0 in x["pxo"]} for label, x in (("baseline", B), ("candidate", C))})

    recon_bad = []
    for label, x in (("baseline", B), ("candidate", C)):
        for d0 in DIRS:
            if d0 not in x["pxo"]:
                recon_bad.append("%s/%s missing PXO" % (label, d0))
                continue
            comps = x["pxo"][d0]["comps"]
            for spec in x["man"]["specs"][d0]:
                key = (d0, spec["frame"])
                if key not in x["png"] or spec["frame"] >= len(comps) or not np.array_equal(comps[spec["frame"]], x["png"][key]):
                    recon_bad.append("%s/%s/%s" % (label, d0, spec["role"]))
    gate("reconstruction_all_17", not recon_bad, recon_bad[:12])

    idle_bad = []
    for d0 in IDLE:
        if not raw_equal(B["raw"].get((d0, 0)), C["raw"].get((d0, 0))):
            idle_bad.append(d0)
    gate("protected_idle_raw_equality", not idle_bad, {"mismatched": idle_bad, "checked": 4})
    walk_bad = []
    for d0 in WALKS:
        for i in range(12):
            if not raw_equal(B["raw"].get((d0, i + 1)), C["raw"].get((d0, i + 1))):
                walk_bad.append("%s/walk%02d" % (d0, i))
    gate("protected_north_south_walk_raw_equality", not walk_bad,
         {"mismatched": walk_bad[:12], "checked": 24})
    side_leg_bad = []
    for d0 in SIDE:
        if d0 not in B["pxo"] or d0 not in C["pxo"]:
            side_leg_bad.append("%s missing PXO" % d0)
            continue
        for name in ("near-leg", "far-leg"):
            if name not in B["pxo"][d0]["layers"] or name not in C["pxo"][d0]["layers"]:
                side_leg_bad.append("%s missing layer %s" % (d0, name))
                continue
            for i in range(12):
                if not np.array_equal(B["pxo"][d0]["raw"][name][i + 1], C["pxo"][d0]["raw"][name][i + 1]):
                    side_leg_bad.append("%s/%s/walk%02d" % (d0, name, i))
    gate("side_walk_leg_layer_equality", not side_leg_bad,
         {"mismatched": side_leg_bad[:12], "checked_layers": 2, "checked_frames": 12})

    arm_meas, arm_bad = {}, []
    for d0 in SIDE:
        arm_meas[d0] = {}
        for role in ("near-arm", "far-arm"):
            # An authored arm may be blank at idle/last bridge, where the exact original glove owns rest.
            names = [n for n in C["pxo"].get(d0, {}).get("layers", []) if n in (role, role + "-sleeve")]
            name = names[0] if len(names) == 1 else role
            counts = []
            if len(names) == 1:
                counts = [int((C["pxo"][d0]["raw"][name][i][..., 3] > 0).sum()) for i in range(1, 13)]
            else:
                arm_bad.append("%s missing or ambiguous layer %s" % (d0, role))
            if len(counts) != 12 or not all(counts):
                arm_bad.append("%s/%s empty walk arm" % (d0, role))
            arm_meas[d0][name] = {"min": min(counts) if counts else None,
                                  "max": max(counts) if counts else None,
                                  "frames_nonempty": sum(1 for c in counts if c > 0)}
    gate("side_arm_layers_present_nonempty", not arm_bad, arm_bad[:10])
    gate("bridge_final_idle_reference", B["man"]["final_ok"] and C["man"]["final_ok"],
         {"baseline": B["man"]["final_ok"], "candidate": C["man"]["final_ok"]})

    frames = {}
    for d0 in DIRS:
        f = {"roles": [], "sha16": [], "png_equal_baseline": [], "delta_px": [],
             "bbox": [], "opaque": [], "centroid": []}
        if d0 in SIDE:
            f["near_arm"] = {"bbox": [], "opaque": [], "delta_px": []}
            f["far_arm"] = {"bbox": [], "opaque": [], "delta_px": []}
        for spec in C["man"]["specs"][d0]:
            key = (d0, spec["frame"])
            if key not in C["png"]:
                continue
            arr, base_arr = C["png"][key], B["png"].get(key)
            f["roles"].append(spec["role"])
            f["sha16"].append(sha(C["raw"][key])[:16])
            f["png_equal_baseline"].append(raw_equal(C["raw"].get(key), B["raw"].get(key)))
            f["delta_px"].append(int(np.any(arr != base_arr, axis=2).sum()) if base_arr is not None else None)
            st = stats(arr)
            f["bbox"].append(st["bbox"])
            f["opaque"].append(st["opaque"])
            f["centroid"].append(st["centroid"])
            if d0 in SIDE:
                for role in ("near-arm", "far-arm"):
                    name = role if role in C["pxo"].get(d0, {}).get("layers", []) else role + "-sleeve"
                    if d0 in C["pxo"] and name in C["pxo"][d0]["layers"]:
                        arm = stats(C["pxo"][d0]["raw"][name][spec["frame"]])
                        ak = f[role.replace("-", "_")]
                        ak["bbox"].append(arm["bbox"])
                        ak["opaque"].append(arm["opaque"])
                        dp = None
                        if d0 in B["pxo"] and name in B["pxo"][d0]["layers"]:
                            dp = int(np.any(C["pxo"][d0]["raw"][name][spec["frame"]] !=
                                            B["pxo"][d0]["raw"][name][spec["frame"]], axis=2).sum())
                        ak["delta_px"].append(dp)
        frames[d0] = f

    def leg_mask(pxo, fi):
        m = np.zeros((H, W), bool)
        for name in ("near-leg", "far-leg"):
            if name in pxo["layers"]:
                m |= pxo["raw"][name][fi][..., 3] > 0
        return m

    def nn(mask_a, mask_b):
        A, Bp = np.argwhere(mask_a), np.argwhere(mask_b)
        if not len(A) or not len(Bp):
            return None
        total = 0.0
        for chunk in np.array_split(A, max(1, (len(A) + 255) // 256)):
            d = ((chunk[:, None, :] - Bp[None, :, :]) ** 2).sum(-1)
            total += float(np.sqrt(d.min(axis=1)).sum())
        fwd = total / len(A)
        total = 0.0
        for chunk in np.array_split(Bp, max(1, (len(Bp) + 255) // 256)):
            d = ((chunk[:, None, :] - A[None, :, :]) ** 2).sum(-1)
            total += float(np.sqrt(d.min(axis=1)).sum())
        return round((fwd + total / len(Bp)) / 2.0, 3)

    bridge_dist = []
    for d0 in SIDE:
        if d0 not in C["pxo"]:
            continue
        for c in CONTACTS:
            e = C["man"]["bridge"]["directions"][d0][c]
            fw = e.get("from_walk_frame")
            if fw not in (0, 6):
                bridge_dist.append({"dir": d0, "contact": c, "error": "from_walk_frame=%r" % (fw,)})
                continue
            ci = CONTACTS.index(c)
            idle_mask = leg_mask(C["pxo"][d0], 0)
            stages = [("contact", fw + 1), ("b0", 13 + 2 * ci), ("b1", 14 + 2 * ci), ("idle", 0)]
            rows = []
            for label, fi in stages:
                mask = leg_mask(C["pxo"][d0], fi)
                rows.append({"stage": label, "frame": fi, "leg_px": int(mask.sum()),
                             "delta_px_to_idle": int((mask != idle_mask).sum()),
                             "mean_nn_to_idle_px": nn(mask, idle_mask)})
            bridge_dist.append({"dir": d0, "contact": c, "from_walk_frame": fw, "stages": rows,
                                "final_b1_to_idle_px": rows[2]["mean_nn_to_idle_px"]})

    meas.update({"counts": {"baseline": B["counts"], "candidate": C["counts"]},
                 "protected_raw": {"idle": {"checked": 4, "mismatched": idle_bad},
                                   "north_south_walk": {"checked": 24, "mismatched": walk_bad}},
                 "side_walk_legs": {"checked_frames_per_side": 12, "mismatched": side_leg_bad[:24]},
                 "side_arms": arm_meas,
                 "side_bridge_leg_distance": bridge_dist,
                 "frames": frames})
    ok = all(g["ok"] for g in gates.values())
    return ok, gates, meas


def report_for(bp, cp):
    rep = {"schema": "worlds-between.heroine-sea-armcheck.v1",
           "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "baseline": {"manifest": os.path.abspath(bp), "sha256": sha(rb(bp))},
           "candidate": {"manifest": os.path.abspath(cp), "sha256": sha(rb(cp))},
           "note": "Structural byte/source checks only. No motion, cadence, art-quality, GUI, or gameplay inference.",
           "limitations": [
               "Bridge leg distances and arm extents/changes are descriptive measurements, not artistic pass thresholds.",
               "Layer equality is matched by layer name so candidate layer count/order may change legitimately.",
               "Protected raw-PNG equality covers all 4 idle PNGs and north/south walk PNGs only; east/west walks may change."]}
    try:
        B, C = prepare(bp), prepare(cp)
        ok, gates, meas = compare_prepared(B, C)
        rep.update({"ok": ok, "gates": gates, "measurements": meas})
    except Exception as exc:
        rep.update({"ok": False, "error": {"type": type(exc).__name__, "message": str(exc)},
                    "gates": {}, "measurements": {}})
    return rep


def tree_hashes(root):
    out, base = {}, xp(os.path.abspath(root))
    for dp, _dn, fn in os.walk(base):
        for f in fn:
            p = os.path.join(dp, f)
            out[os.path.relpath(p, base)] = sha(rb(p))
    return out


def makedirs_host(path):
    path = os.path.abspath(path)
    if os.path.isdir(xp(path)):
        return
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mkdir", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        os.makedirs(path, exist_ok=True)
    if not os.path.isdir(xp(path)):
        raise PermissionError("cannot create directory %s" % path)


def copy_tree(src, dst):
    src, dst = os.path.abspath(src), os.path.abspath(dst)
    makedirs_host(dst)
    for name in os.listdir(xp(src)):
        sp, dp = os.path.join(src, name), os.path.join(dst, name)
        if os.path.isdir(xp(sp)):
            copy_tree(sp, dp)
        else:
            wb(dp, rb(sp))


def selftest(baseline):
    cases, ok_all = [], True
    outroot = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "hsea-armcheck12")
    makedirs_host(outroot)
    tmp = os.path.join(outroot, "hsarm-" + uuid.uuid4().hex[:8])
    makedirs_host(tmp)
    base = os.path.join(tmp, "base")
    copy_tree(os.path.dirname(os.path.abspath(baseline)), base)
    base_manifest = os.path.join(base, os.path.basename(baseline))
    base_before = tree_hashes(base)
    orig_dir = os.path.dirname(os.path.abspath(baseline))
    orig_before = tree_hashes(orig_dir)
    for name, expected, mutate in (
            ("unchanged", True, None),
            ("mutated_protected_leg", False, "leg"),
            ("mutated_idle_png", False, "idle"),
            ("corrupt_native", False, "native"),
            ("corrupt_export", False, "export"),
            ("malformed_manifest", False, "malformed")):
        cand = os.path.join(tmp, name)
        copy_tree(base, cand)
        cm = os.path.join(cand, os.path.basename(baseline))
        reason = None
        try:
            if mutate:
                man = load_json(cm)
                if mutate == "malformed":
                    wb(cm, b"{not valid json\n")
                elif mutate == "leg":
                    sf = next(s for s in man["source_files"] if s.get("format") == "pixelorama-pxo" and s.get("direction") == "east")
                    pp = child(cand, sf["file"])
                    with zipfile.ZipFile(xp(pp)) as z:
                        infos = z.infolist()
                        data = {i.filename: z.read(i.filename) for i in infos}
                    meta = json.loads(data["data.json"].decode("utf-8-sig"))
                    names = [l["name"] for l in meta["layers"]]
                    li = names.index("near-leg")
                    ent = "image_data/frames/2/layer_%d" % (li + 1)
                    a = np.frombuffer(data[ent], np.uint8).reshape(H, W, 4).copy()
                    a[50, 40] = (255, 0, 255, 255)
                    data[ent] = a.tobytes()
                    with zipfile.ZipFile(xp(pp), "w", zipfile.ZIP_DEFLATED) as z:
                        for i in infos:
                            z.writestr(i, data[i.filename])
                    sf["sha256"] = sha(rb(pp))
                    dump_json(cm, man)
                    pxo = decode_pxo(pp)
                    save_png(child(cand, man["actions"]["walk"]["east"][0]["file"]), pxo["comps"][1])
                elif mutate == "idle":
                    pp = child(cand, man["actions"]["idle"]["south"][0]["file"])
                    a = load_png(rb(pp))
                    a[50, 40] = (255, 0, 255, 255)
                    save_png(pp, a)
                elif mutate == "native":
                    sf = next(s for s in man["source_files"] if s.get("format") == "pixelorama-pxo")
                    wb(child(cand, sf["file"]), b"not a zip\n")
                elif mutate == "export":
                    wb(child(cand, man["actions"]["walk"]["east"][0]["file"]), b"not a png\n")
        except Exception as exc:
            reason = "mutation failed: %s: %s" % (type(exc).__name__, exc)
        before = tree_hashes(cand)
        try:
            proc = subprocess.run([sys.executable, "-I", os.path.abspath(__file__), base_manifest, cm],
                                  capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        except Exception as exc:
            proc = None
            reason = "invoke failed: %s: %s" % (type(exc).__name__, exc)
        after = tree_hashes(cand)
        parsed, tb = None, False
        if proc is not None:
            try:
                parsed = json.loads(proc.stdout)
            except Exception:
                pass
            tb = "Traceback" in (proc.stdout + proc.stderr)
        actual = bool(parsed and parsed.get("ok"))
        gates = (parsed or {}).get("gates", {})
        if name == "mutated_protected_leg" and gates.get("side_walk_leg_layer_equality", {}).get("ok"):
            reason = "leg mutation not caught by leg gate"
        if name == "mutated_idle_png" and gates.get("protected_idle_raw_equality", {}).get("ok"):
            reason = "idle mutation not caught by raw gate"
        case_ok = (actual == expected and not tb and before == after and reason is None)
        ok_all = ok_all and case_ok
        cases.append({"name": name, "expected_ok": expected, "actual_ok": actual,
                      "cli_exit": None if proc is None else proc.returncode,
                      "traceback": tb, "source_hashes_unchanged": before == after,
                      "failed_gates": sorted(k for k, v in gates.items() if not v.get("ok")),
                      "reason": reason, "ok": case_ok})
    base_unchanged = base_before == tree_hashes(base)
    orig_unchanged = orig_before == tree_hashes(orig_dir)
    ok_all = ok_all and base_unchanged and orig_unchanged
    out = {"schema": "worlds-between.heroine-sea-armcheck.selftest.v1", "ok": ok_all,
           "baseline_manifest": os.path.abspath(baseline), "baseline_hashes_unchanged": base_unchanged,
           "original_baseline_hashes_unchanged": orig_unchanged, "cases": cases,
           "limitations": ["Negative tests use copies in a temp directory; original sources are never mutated."]}
    assert os.path.commonpath([os.path.abspath(tmp), os.path.abspath(outroot)]) == os.path.abspath(outroot) and os.path.basename(tmp).startswith("hsarm-")
    shutil.rmtree(xp(tmp), ignore_errors=True)
    return out


def main(argv):
    args = [a for a in argv if a != "--out"]
    if "--selftest" in args:
        args.remove("--selftest")
        if len(args) != 1:
            print("usage: checker --selftest BASELINE_MANIFEST", file=sys.stderr)
            return 2
        out = selftest(args[0])
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0 if out["ok"] else 1
    outpath = None
    if "--out" in argv:
        i = argv.index("--out")
        if i + 1 >= len(argv):
            print("usage: checker BASELINE_MANIFEST CANDIDATE_MANIFEST [--out JSON]", file=sys.stderr)
            return 2
        outpath = argv[i + 1]
        args = [a for j, a in enumerate(argv) if j not in (i, i + 1)]
    if len(args) != 2:
        print("usage: checker BASELINE_MANIFEST CANDIDATE_MANIFEST [--out JSON]", file=sys.stderr)
        return 2
    rep = report_for(args[0], args[1])
    text = json.dumps(rep, indent=1, ensure_ascii=False)
    if outpath:
        wb(outpath, (text + "\n").encode("utf-8"))
    print(text)
    return 0 if rep.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
