"""Independent read-only checker for the heroine-sea phase-aware side stop.

CLI:
  python -I <this> --manifest NEW_TRANSITION_JSON --baseline V08_TRANSITION_JSON \
      --report REPORT_JSON [--evidence-class synthetic_fixture|real_candidate]

The checker never imports candidate code. Every referenced asset is a basename
resolved under the manifest or source-set directory. PXO frames are parsed
dynamically and mapped through the source-set export declarations; no 49/65
project-frame count is assumed.

Structural contract only. No motion, cadence, art-quality, GUI or gameplay
inference. SYNTHETIC fixtures are labelled and are not runtime art approval.
"""
import hashlib
import io
import json
import os
import re
import sys
import zipfile
from datetime import datetime, timezone

import numpy as np
from PIL import Image

W, H, GROUND = 80, 112, 104
DIRS = ("south", "west", "north", "east")
SIDE = ("east", "west")
CONTACTS = ("contact0", "contact6")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class CheckError(Exception):
    def __init__(self, gate, message):
        Exception.__init__(self, message)
        self.gate = gate
        self.message = message


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


def load_json_bytes(data, label):
    try:
        return json.loads(data.decode("utf-8-sig"))
    except Exception as exc:
        raise CheckError("inputs_parse", "%s is not valid UTF-8 JSON: %s: %s" %
                         (label, type(exc).__name__, exc))


def load_json(path, label):
    try:
        return load_json_bytes(rb(path), label)
    except CheckError:
        raise
    except Exception as exc:
        raise CheckError("inputs_parse", "%s cannot be read: %s: %s" %
                         (label, type(exc).__name__, exc))


def safe_file(base, name, label="asset"):
    if not isinstance(name, str) or not name:
        raise CheckError("path_safety", "%s has an empty/non-string file reference" % label)
    if (name in (".", "..") or "\x00" in name or ":" in name or "/" in name or
            "\\" in name or os.path.basename(name) != name):
        raise CheckError("path_safety", "%s is not a plain basename: %r" % (label, name))
    base_abs = os.path.abspath(base)
    path = os.path.abspath(os.path.join(base_abs, name))
    try:
        inside = os.path.commonpath([path, base_abs]) == base_abs
    except Exception:
        inside = False
    if not inside:
        raise CheckError("path_safety", "%s escapes its root: %r" % (label, name))
    if os.path.islink(xp(path)):
        raise CheckError("path_safety", "%s is a symlink/reparse path: %r" % (label, name))
    return path


def load_png_bytes(data, label):
    try:
        with Image.open(io.BytesIO(data)) as im:
            if im.size != (W, H) or im.mode != "RGBA":
                raise ValueError("not 80x112 RGBA (%s %s)" % (im.size, im.mode))
            return np.array(im.convert("RGBA"), dtype=np.uint8)
    except Exception as exc:
        raise CheckError("png_format", "%s is not a valid 80x112 RGBA PNG: %s: %s" %
                         (label, type(exc).__name__, exc))


def png_bounds_ok(arr):
    a = arr[..., 3]
    issues = []
    if not np.isin(a, (0, 255)).all():
        issues.append("non-binary alpha")
    if a[0].any() or a[-1].any() or a[:, 0].any() or a[:, -1].any():
        issues.append("alpha on canvas border")
    if a[GROUND:].any():
        issues.append("alpha at/below ground row %d" % GROUND)
    return (not issues), "; ".join(issues)


def decode_pxo(path, label):
    try:
        with zipfile.ZipFile(xp(path)) as z:
            names = z.namelist()
            meta = json.loads(z.read("data.json").decode("utf-8-sig"))
            if meta.get("size_x") != W or meta.get("size_y") != H:
                raise ValueError("canvas is not 80x112")
            layers = [l.get("name") for l in meta.get("layers", [])]
            if not layers or len(layers) != len(set(layers)):
                raise ValueError("missing/duplicate layer names")
            nframes = len(meta.get("frames", []))
            if nframes <= 0:
                raise ValueError("no frames")
            comps = []
            for fi in range(nframes):
                comp = np.zeros((H, W, 4), np.uint8)
                for li in range(len(layers)):
                    ent = "image_data/frames/%d/layer_%d" % (fi + 1, li + 1)
                    if ent not in names:
                        raise ValueError("missing %s" % ent)
                    b = z.read(ent)
                    if len(b) != W * H * 4:
                        raise ValueError("layer size mismatch %s" % ent)
                    a = np.frombuffer(b, np.uint8).reshape(H, W, 4).copy()
                    mask = a[..., 3] > 0
                    comp[mask] = a[mask]
                comps.append(comp)
            return {"frames": nframes, "layers": layers, "comps": comps}
    except CheckError:
        raise
    except Exception as exc:
        raise CheckError("native_parse", "%s is not a readable PXO: %s: %s" %
                         (label, type(exc).__name__, exc))


def norm_tokens(value):
    return [t for t in re.split(r"[^a-z0-9]+", str(value).lower()) if t]


def role_key(value, direction=None, action=None, frame=None):
    toks = norm_tokens(value)
    d0 = direction if direction in DIRS else next((d for d in DIRS if d in toks), None)
    a0 = action if action in ("idle", "walk") else next((a for a in ("idle", "walk") if a in toks), None)
    idx = frame
    if idx is None:
        m = re.search(r"(?:^|[^a-z0-9])f(?:rame)?(\d{1,2})(?:[^0-9]|$)", str(value).lower())
        if m:
            idx = int(m.group(1))
        else:
            nums = [int(t) for t in toks if t.isdigit()]
            if a0 == "walk" and nums:
                idx = nums[-1]
    if a0 == "idle" and idx is None:
        idx = 0
    if d0 not in DIRS or a0 not in ("idle", "walk") or not isinstance(idx, int) or idx < 0:
        raise CheckError("source_set_structure", "cannot resolve protected role from %r" % (value,))
    if a0 == "idle" and idx != 0:
        raise CheckError("source_set_structure", "idle role must be frame 0: %r" % (value,))
    if a0 == "walk" and idx > 11:
        raise CheckError("source_set_structure", "walk role frame out of range: %r" % (value,))
    return (d0, a0, idx)


def extract_protected(ss):
    entries = []
    if isinstance(ss.get("actions"), dict):
        for action in ("idle", "walk"):
            for d0 in DIRS:
                fl = ss["actions"].get(action, {}).get(d0)
                if not isinstance(fl, list):
                    continue
                for i, ent in enumerate(fl):
                    if not isinstance(ent, dict):
                        raise CheckError("source_set_structure", "action entry is not an object")
                    entries.append({"role": "%s/%s/%02d" % (action, d0, i),
                                    "file": ent.get("file"), "sha256": ent.get("sha256")})
    for key in ("protected", "protected_pngs", "protected_png", "protected_files"):
        val = ss.get(key)
        if val is None:
            continue
        if isinstance(val, dict):
            for role, ent in val.items():
                if isinstance(ent, str):
                    entries.append({"role": role, "file": ent})
                elif isinstance(ent, dict):
                    item = dict(ent)
                    item.setdefault("role", role)
                    entries.append(item)
                else:
                    raise CheckError("source_set_structure", "unsupported protected entry %r" % (role,))
        elif isinstance(val, list):
            for ent in val:
                if isinstance(ent, str):
                    entries.append({"file": ent})
                elif isinstance(ent, dict):
                    entries.append(dict(ent))
                else:
                    raise CheckError("source_set_structure", "unsupported protected entry")
        else:
            raise CheckError("source_set_structure", "unsupported protected collection")
    out = {}
    for ent in entries:
        if not isinstance(ent, dict) or not isinstance(ent.get("file"), str):
            raise CheckError("source_set_structure", "protected entry lacks file")
        key = role_key(ent.get("role", ent["file"]), ent.get("direction"),
                       ent.get("action"), ent.get("frame"))
        if key in out:
            raise CheckError("source_set_structure", "duplicate protected role %s" % (key,))
        out[key] = ent
    expected = set((d0, "idle", 0) for d0 in DIRS) | set((d0, "walk", i) for d0 in DIRS for i in range(12))
    missing = sorted(expected - set(out))
    extra = sorted(set(out) - expected)
    if missing or extra or len(out) != 52:
        raise CheckError("source_set_structure",
                         "protected set must be exactly 52 (4 idle + 48 walk); missing=%r extra=%r" %
                         (missing[:8], extra[:8]))
    return out


def extract_native_sources(ss):
    srcs = ss.get("native_sources")
    if srcs is None:
        srcs = ss.get("sources")
    if srcs is None:
        srcs = ss.get("source_files")
    if not isinstance(srcs, list):
        raise CheckError("source_set_structure", "source set has no native source list")
    return [s for s in srcs if isinstance(s, dict) and s.get("format") == "pixelorama-pxo"]


def extract_exports(src):
    for key in ("frame_exports", "frames", "exports"):
        val = src.get(key)
        if isinstance(val, list):
            return val
        if isinstance(val, dict):
            rows = []
            for slot, ent in val.items():
                if isinstance(ent, dict):
                    item = dict(ent)
                    item.setdefault("slot", slot)
                    rows.append(item)
            if rows:
                return rows
    return None


def slot_from_export(ent, sample_by_file):
    if not isinstance(ent, dict):
        raise CheckError("source_set_structure", "native export entry is not an object")
    if isinstance(ent.get("file"), str) and ent["file"] in sample_by_file:
        return sample_by_file[ent["file"]]
    if isinstance(ent.get("phase"), int) and isinstance(ent.get("sample"), int):
        return (ent["phase"], ent["sample"])
    for key in ("slot", "role", "name"):
        val = ent.get(key)
        if isinstance(val, str):
            m = re.search(r"phase[\s_/-]*(\d{1,2})[\s_/-]*(?:sample|s)[\s_/-]*(\d)", val.lower())
            if m:
                return (int(m.group(1)), int(m.group(2)))
            m = re.search(r"(\d{1,2})[\s_/-]+(\d)", val)
            if m:
                return (int(m.group(1)), int(m.group(2)))
    return None


def tree_hashes(root):
    out, base = {}, xp(os.path.abspath(root))
    for dp, _dn, fn in os.walk(base):
        for f in sorted(fn):
            p = os.path.join(dp, f)
            out[os.path.relpath(p, base)] = sha(rb(p))
    return out


def prep_baseline(path):
    bdir = os.path.dirname(os.path.abspath(path))
    bm = load_json(path, "baseline transition")
    if bm.get("schema") != "worlds-between.exploration-stop-transition.supplemental.v1":
        raise CheckError("baseline_integrity", "baseline transition schema is not supplemental.v1")
    if not isinstance(bm.get("directions"), dict) or set(bm["directions"]) != set(DIRS):
        raise CheckError("baseline_integrity", "baseline directions are incomplete")
    sm_name = bm.get("source_manifest")
    sm_path = safe_file(bdir, sm_name, "baseline source_manifest")
    sm = load_json(sm_path, "baseline source manifest")
    if sm.get("schema") != "worlds-between.exploration-source.v1":
        raise CheckError("baseline_integrity", "baseline source manifest schema mismatch")
    if sm.get("actor_id") != "protagonist-female" or sm.get("density") != 2:
        raise CheckError("baseline_integrity", "baseline actor_id/density mismatch")
    if sm.get("frame_size") != [W, H] or sm.get("pivot") != [40, GROUND]:
        raise CheckError("baseline_integrity", "baseline frame_size/pivot mismatch")
    acts = sm.get("actions")
    if not isinstance(acts, dict) or set(acts) != {"idle", "walk"}:
        raise CheckError("baseline_integrity", "baseline actions must be idle/walk")
    for d0 in DIRS:
        if not isinstance(acts["idle"].get(d0), list) or len(acts["idle"][d0]) != 1:
            raise CheckError("baseline_integrity", "baseline idle/%s must have 1 frame" % d0)
        if not isinstance(acts["walk"].get(d0), list) or len(acts["walk"][d0]) != 12:
            raise CheckError("baseline_integrity", "baseline walk/%s must have 12 frames" % d0)
    protected, bridge = {}, {}
    for d0 in DIRS:
        ent = acts["idle"][d0][0]
        p = safe_file(bdir, ent["file"], "baseline idle/%s" % d0)
        data = rb(p)
        protected[(d0, "idle", 0)] = {"role": "idle/%s" % d0, "path": p, "bytes": data,
                                      "sha": sha(data), "arr": load_png_bytes(data, "baseline idle/%s" % d0)}
        for i, ent in enumerate(acts["walk"][d0]):
            p = safe_file(bdir, ent["file"], "baseline walk/%s/%02d" % (d0, i))
            data = rb(p)
            protected[(d0, "walk", i)] = {"role": "walk/%s/%02d" % (d0, i), "path": p, "bytes": data,
                                          "sha": sha(data), "arr": load_png_bytes(data, "baseline walk/%s/%02d" % (d0, i))}
    for d0 in DIRS:
        cs = bm["directions"].get(d0)
        if not isinstance(cs, dict) or set(cs) != set(CONTACTS):
            raise CheckError("baseline_integrity", "baseline contacts incomplete for %s" % d0)
        for c in CONTACTS:
            ent = cs[c]
            if not isinstance(ent, dict) or set(ent) != {"from_walk_frame", "bridge", "final"}:
                raise CheckError("baseline_integrity", "baseline %s/%s entry shape mismatch" % (d0, c))
            want = 0 if c == "contact0" else 6
            if ent["from_walk_frame"] != want:
                raise CheckError("baseline_integrity", "baseline %s/%s from_walk_frame mismatch" % (d0, c))
            if not isinstance(ent["bridge"], list) or len(ent["bridge"]) != 2:
                raise CheckError("baseline_integrity", "baseline %s/%s bridge must have 2 entries" % (d0, c))
            rows = []
            for i, be in enumerate(ent["bridge"]):
                if not isinstance(be, dict) or set(be) != {"file", "sha256"}:
                    raise CheckError("baseline_integrity", "baseline bridge entry shape mismatch")
                p = safe_file(bdir, be["file"], "baseline bridge %s/%s/%d" % (d0, c, i))
                data = rb(p)
                if sha(data) != be["sha256"]:
                    raise CheckError("baseline_integrity", "baseline bridge hash mismatch %s/%s/%d" % (d0, c, i))
                arr = load_png_bytes(data, "baseline bridge %s/%s/%d" % (d0, c, i))
                rows.append({"file": be["file"], "sha256": be["sha256"], "bytes": data, "arr": arr})
            fp = safe_file(bdir, ent["final"], "baseline final %s/%s" % (d0, c))
            fdata = rb(fp)
            bridge[(d0, c)] = {"from_walk_frame": ent["from_walk_frame"], "bridge": rows,
                               "final": ent["final"], "final_sha": sha(fdata)}
    pxo = {}
    srcs = sm.get("source_files")
    if not isinstance(srcs, list):
        raise CheckError("baseline_integrity", "baseline source_files missing")
    for sf in srcs:
        if not isinstance(sf, dict) or not isinstance(sf.get("file"), str):
            raise CheckError("baseline_integrity", "baseline source_files entry malformed")
        p = safe_file(bdir, sf["file"], "baseline source %s" % sf["file"])
        data = rb(p)
        if sha(data) != sf.get("sha256"):
            raise CheckError("baseline_integrity", "baseline source hash mismatch %s" % sf["file"])
        if sf.get("format") == "pixelorama-pxo":
            d0 = sf.get("direction")
            if d0 not in DIRS:
                raise CheckError("baseline_integrity", "baseline PXO direction invalid")
            pxo[d0] = decode_pxo(p, "baseline PXO %s" % d0)
    for d0 in DIRS:
        if d0 not in pxo or pxo[d0]["frames"] != 17:
            raise CheckError("baseline_integrity", "baseline PXO %s must have 17 parsed frames" % d0)
        specs = [("idle", 0)] + [("walk%02d" % i, i + 1) for i in range(12)]
        for c, basef in zip(CONTACTS, (13, 15)):
            specs.append((c + "-b0", basef))
            specs.append((c + "-b1", basef + 1))
        for role, fi in specs:
            if role == "idle":
                arr = protected[(d0, "idle", 0)]["arr"]
            elif role.startswith("walk"):
                arr = protected[(d0, "walk", int(role[4:]))]["arr"]
            else:
                c = role.split("-")[0]
                bi = int(role.split("-b")[1])
                arr = bridge[(d0, c)]["bridge"][bi]["arr"]
            if not np.array_equal(pxo[d0]["comps"][fi], arr):
                raise CheckError("baseline_integrity",
                                 "baseline PXO %s frame %d does not export %s" % (d0, fi, role))
    return {"dir": bdir, "transition": bm, "protected": protected, "bridge": bridge, "pxo": pxo}


def validate(manifest_path, baseline_path, report_path, evidence_class):
    before_base = tree_hashes(os.path.dirname(os.path.abspath(baseline_path)))
    before_cand = tree_hashes(os.path.dirname(os.path.abspath(manifest_path)))
    rep = {
        "schema": "worlds-between.heroine-sea-phase-aware-stop-check.v1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "evidence_class": evidence_class,
        "note": "Structural, read-only validation of copied/synthetic or real candidate bytes. "
                "No motion, cadence, art-quality, GUI, gameplay or native-runtime inference.",
        "inputs": {"manifest": os.path.abspath(manifest_path),
                   "baseline": os.path.abspath(baseline_path),
                   "report": os.path.abspath(report_path)},
        "limitations": [
            "Synthetic fixtures reuse exact v08 protected bytes plus synthetic phase endpoints; they are not art approval.",
            "Native PXO layers are parsed dynamically from PXO data.json; frame counts are not fixed to 49/65.",
            "The fixture builder does not require the real hsea-stop15 producer output; when present the same CLI is run read-only against it as a separate real-candidate report.",
            "No GUI reopening, Godot runtime, motion review, network, provider or source mutation is performed."],
        "gates": {},
        "measurements": {},
        "ok": False,
    }
    gates = rep["gates"]

    def gate(name, ok, detail):
        gates[name] = {"ok": bool(ok), "detail": detail}

    try:
        base = prep_baseline(baseline_path)
        gate("baseline_integrity", True, {"source_manifest_checked": True,
                                          "protected_png": 52, "legacy_bridge_png": 16,
                                          "pxo_frames_per_direction": 17})
        bdir = base["dir"]
        man = load_json(manifest_path, "candidate transition")
        cdir = os.path.dirname(os.path.abspath(manifest_path))
        if man.get("schema") != "worlds-between.exploration-stop-transition.supplemental.v1":
            raise CheckError("manifest_structure", "candidate schema is not supplemental.v1")
        if not isinstance(man.get("source_set"), str):
            raise CheckError("manifest_structure", "manifest source_set must name a source-set JSON")
        if not isinstance(man.get("source_set_sha256"), str) or not HEX64.match(man["source_set_sha256"]):
            raise CheckError("manifest_structure", "manifest source_set_sha256 must be 64 lowercase hex")
        ss_path = safe_file(cdir, man["source_set"], "source_set")
        ss_data = rb(ss_path)
        if sha(ss_data) != man["source_set_sha256"]:
            raise CheckError("source_set_pin", "source_set_sha256 does not match source-set bytes")
        ss = load_json_bytes(ss_data, "source set")
        if not isinstance(ss, dict) or not isinstance(ss.get("schema"), str):
            raise CheckError("source_set_structure", "source set must be a JSON object with schema")
        gate("source_set_pin", True, {"file": man["source_set"], "sha256": man["source_set_sha256"]})
        protected_ss = extract_protected(ss)

        legacy_issues, hash_issues, path_issues = [], [], []
        cand = {}
        for d0 in DIRS:
            cs = man.get("directions", {}).get(d0) if isinstance(man.get("directions"), dict) else None
            if not isinstance(cs, dict) or set(cs) != set(CONTACTS):
                raise CheckError("manifest_structure", "candidate legacy contacts incomplete for %s" % d0)
            for c in CONTACTS:
                ent = cs[c]
                if not isinstance(ent, dict) or set(ent) != {"from_walk_frame", "bridge", "final"}:
                    raise CheckError("manifest_structure", "candidate %s/%s legacy entry shape mismatch" % (d0, c))
                b = base["bridge"][(d0, c)]
                if ent["from_walk_frame"] != b["from_walk_frame"]:
                    legacy_issues.append("%s/%s from_walk_frame" % (d0, c))
                if not isinstance(ent["bridge"], list) or len(ent["bridge"]) != 2:
                    raise CheckError("manifest_structure", "candidate %s/%s bridge must have 2 entries" % (d0, c))
                rows = []
                for i, be in enumerate(ent["bridge"]):
                    if not isinstance(be, dict) or set(be) != {"file", "sha256"}:
                        raise CheckError("manifest_structure", "candidate bridge entry shape mismatch")
                    p = safe_file(cdir, be["file"], "legacy bridge %s/%s/%d" % (d0, c, i))
                    data = rb(p)
                    arr = load_png_bytes(data, "legacy bridge %s/%s/%d" % (d0, c, i))
                    if sha(data) != be["sha256"]:
                        hash_issues.append("legacy bridge %s/%s/%d" % (d0, c, i))
                    if be["sha256"] != b["bridge"][i]["sha256"]:
                        legacy_issues.append("%s/%s/bridge%d" % (d0, c, i))
                    okb, why = png_bounds_ok(arr)
                    if not okb:
                        path_issues.append("legacy bridge %s/%s/%d: %s" % (d0, c, i, why))
                    rows.append({"file": be["file"], "sha256": be["sha256"], "bytes": data, "arr": arr})
                if not isinstance(ent.get("final"), str):
                    raise CheckError("manifest_structure", "candidate %s/%s final missing" % (d0, c))
                fp = safe_file(cdir, ent["final"], "legacy final %s/%s" % (d0, c))
                fdata = rb(fp)
                if sha(fdata) != b["final_sha"]:
                    legacy_issues.append("%s/%s/final" % (d0, c))
                cand[(d0, c)] = {"bridge": rows, "final": ent["final"], "final_sha": sha(fdata)}
        if legacy_issues:
            gate("legacy_schema_unchanged", False, legacy_issues[:12])
        else:
            gate("legacy_schema_unchanged", True, {"contacts": 8, "from_walk_frame_and_hashes": "equal baseline"})

        protected, prot_bytes_bad, png_bad = {}, [], []
        for key, ent in protected_ss.items():
            p = safe_file(cdir, ent["file"], "protected %s" % (key,))
            data = rb(p)
            arr = load_png_bytes(data, "protected %s" % (key,))
            if ent.get("sha256") is not None and ent["sha256"] != sha(data):
                hash_issues.append("protected %s declared hash" % (key,))
            if data != base["protected"][key]["bytes"]:
                prot_bytes_bad.append("%s/%s/%02d" % key)
            okb, why = png_bounds_ok(arr)
            if not okb:
                png_bad.append("protected %s/%s/%02d: %s" % (key[0], key[1], key[2], why))
            protected[key] = {"file": ent["file"], "bytes": data, "arr": arr, "sha": sha(data)}
        gate("protected_52_bytes_equal_baseline", not prot_bytes_bad,
             {"checked": 52, "mismatched": prot_bytes_bad[:12]})

        pb = man.get("phase_bridges")
        if not isinstance(pb, dict) or set(pb) != set(SIDE):
            raise CheckError("manifest_structure", "phase_bridges must contain exactly east/west")
        expected_phases = ["phase%d" % i for i in range(12)]
        samples, sample_by_file = {}, {}
        for d0 in SIDE:
            phases = pb.get(d0)
            if not isinstance(phases, dict) or set(phases) != set(expected_phases):
                raise CheckError("manifest_structure", "%s must contain phase0..phase11" % d0)
            for pi in range(12):
                ph = phases["phase%d" % pi]
                if not isinstance(ph, dict) or set(ph) != {"from_walk_frame", "bridge"}:
                    raise CheckError("manifest_structure", "%s/phase%d shape mismatch" % (d0, pi))
                if ph["from_walk_frame"] != pi:
                    raise CheckError("manifest_structure", "%s/phase%d from_walk_frame must equal phase" % (d0, pi))
                if not isinstance(ph["bridge"], list) or len(ph["bridge"]) != 4:
                    raise CheckError("manifest_structure", "%s/phase%d bridge must have 4 samples" % (d0, pi))
                for si, be in enumerate(ph["bridge"]):
                    if not isinstance(be, dict) or set(be) != {"file", "sha256"}:
                        raise CheckError("manifest_structure", "phase bridge entry shape mismatch")
                    if not isinstance(be["sha256"], str) or not HEX64.match(be["sha256"]):
                        raise CheckError("manifest_structure",
                                         "%s/phase%d/sample%d sha256 must be lowercase hex" % (d0, pi, si))
                    p = safe_file(cdir, be["file"], "phase %s/%d/%d" % (d0, pi, si))
                    data = rb(p)
                    if sha(data) != be["sha256"]:
                        hash_issues.append("phase %s/%d/%d declared hash" % (d0, pi, si))
                    arr = load_png_bytes(data, "phase %s/%d/%d" % (d0, pi, si))
                    okb, why = png_bounds_ok(arr)
                    if not okb:
                        png_bad.append("phase %s/%d/%d: %s" % (d0, pi, si, why))
                    key = (d0, pi, si)
                    samples[key] = {"file": be["file"], "sha256": be["sha256"], "data": data,
                                    "arr": arr, "sha": sha(data)}
                    if be["file"] in sample_by_file:
                        raise CheckError("manifest_structure", "duplicate phase sample file %r" % be["file"])
                    sample_by_file[be["file"]] = (pi, si)

        endpoint_bad = []
        for d0 in SIDE:
            for pi in range(12):
                if samples[(d0, pi, 0)]["data"] != protected[(d0, "walk", pi)]["bytes"]:
                    endpoint_bad.append("%s/phase%d/s0!=walk" % (d0, pi))
                if samples[(d0, pi, 3)]["data"] != protected[(d0, "idle", 0)]["bytes"]:
                    endpoint_bad.append("%s/phase%d/s3!=idle" % (d0, pi))
        gate("phase_endpoints_walk_idle", not endpoint_bad,
             {"checked": 24, "mismatched": endpoint_bad[:12]})
        gate("png_format_alpha_bounds_148", not png_bad,
             {"checked": 52 + 96, "invalid": png_bad[:12]})
        gate("declared_hashes", not hash_issues, hash_issues[:12])
        gate("path_safety", True, {"refs": "all basenames confined to manifest/source-set dirs"})

        native = extract_native_sources(ss)
        if len(native) != 2 or set(s.get("direction") for s in native) != set(SIDE):
            raise CheckError("native_sources", "source set must declare exactly one PXO per side")
        expected_slots = set((pi, si) for pi in range(12) for si in range(4))
        native_ok, native_bad, native_checked = [], [], 0
        for src in native:
            d0 = src["direction"]
            p = safe_file(cdir, src.get("file"), "native %s" % d0)
            data = rb(p)
            if sha(data) != src.get("sha256"):
                native_bad.append("%s source hash" % d0)
            pxo = decode_pxo(p, "native %s" % d0)
            exports = extract_exports(src)
            mapping = {}
            if exports is None:
                if pxo["frames"] == 48:
                    order = [(pi, si) for pi in range(12) for si in range(4)]
                    mapping = {slot: i for i, slot in enumerate(order)}
                else:
                    raise CheckError("native_sources",
                                     "%s PXO has %d frames and no export mapping" % (d0, pxo["frames"]))
            else:
                if len(exports) != 48:
                    raise CheckError("native_sources", "%s must declare 48 frame exports, got %d" %
                                     (d0, len(exports)))
                for i, ent in enumerate(exports):
                    slot = slot_from_export(ent, sample_by_file)
                    if slot is None:
                        slot = [(pi, si) for pi in range(12) for si in range(4)][i]
                    if slot not in expected_slots:
                        raise CheckError("native_sources", "%s export slot out of range %r" % (d0, slot))
                    if slot in mapping:
                        raise CheckError("native_sources", "%s duplicate export slot %r" % (d0, slot))
                    fi = ent.get("frame", i)
                    if not isinstance(fi, int) or fi < 0:
                        raise CheckError("native_sources", "%s invalid frame index" % d0)
                    mapping[slot] = fi
                    if isinstance(ent.get("file"), str):
                        sp = safe_file(cdir, ent["file"], "native export %s" % d0)
                        sdata = rb(sp)
                        key = (d0, slot[0], slot[1])
                        if key in samples and sdata != samples[key]["data"]:
                            native_bad.append("%s/%d/%d export file bytes" % (d0, slot[0], slot[1]))
                        if ent.get("sha256") is not None and sha(sdata) != ent["sha256"]:
                            native_bad.append("%s/%d/%d export hash" % (d0, slot[0], slot[1]))
            if set(mapping) != expected_slots:
                native_bad.append("%s export slots incomplete" % d0)
            if len(set(mapping.values())) != len(mapping):
                raise CheckError("native_sources", "%s reuses a native frame for multiple samples" % d0)
            if mapping and max(mapping.values()) >= pxo["frames"]:
                raise CheckError("native_sources", "%s export frame exceeds parsed PXO frame count" % d0)
            for pi, si in sorted(expected_slots):
                fi = mapping.get((pi, si))
                if fi is None:
                    continue
                native_checked += 1
                if not np.array_equal(pxo["comps"][fi], samples[(d0, pi, si)]["arr"]):
                    native_bad.append("%s/phase%d/sample%d native export mismatch" % (d0, pi, si))
            native_ok.append({"direction": d0, "file": src["file"], "parsed_frames": pxo["frames"],
                              "declared_exports": 48, "layers": len(pxo["layers"])})
        gate("native_sources_and_dynamic_exports", not native_bad,
             {"sources": native_ok, "problems": native_bad[:12]})
        gate("native_pxo_exports_equal_96_png", native_checked == 96 and not native_bad,
             {"checked": native_checked, "mismatched": native_bad[:12]})

        after_base = tree_hashes(bdir)
        after_cand = tree_hashes(cdir)
        gate("read_only_inputs_unchanged", before_base == after_base and before_cand == after_cand,
             {"baseline_changed": before_base != after_base,
              "candidate_changed": before_cand != after_cand})
        rep["measurements"] = {
            "protected_png": 52, "legacy_stop_png": 16,
            "phase_samples": 96, "native_sources": 2, "native_exports_checked": native_checked,
            "baseline_pxo_frames_per_direction": 17,
            "candidate_pxo_frames": {s["direction"]: s["parsed_frames"] for s in native_ok},
        }
    except CheckError as exc:
        gate(exc.gate, False, {"error": exc.message})
    except Exception as exc:
        gate("internal_error", False, {"error": "%s: %s" % (type(exc).__name__, exc)})
    rep["ok"] = bool(gates) and all(g.get("ok") for g in gates.values())
    if not rep["ok"]:
        rep["failed_gates"] = sorted(k for k, v in gates.items() if not v.get("ok"))
    wb(report_path, (json.dumps(rep, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    return rep


def parse_args(argv):
    allowed = {"--manifest", "--baseline", "--report", "--evidence-class"}
    vals, i = {}, 0
    while i < len(argv):
        k = argv[i]
        if k not in allowed or k in vals or i + 1 >= len(argv):
            raise ValueError("usage: checker --manifest NEW.json --baseline V08.json --report OUT.json "
                             "[--evidence-class synthetic_fixture|real_candidate]")
        vals[k] = argv[i + 1]
        i += 2
    for k in ("--manifest", "--baseline", "--report"):
        if k not in vals:
            raise ValueError("missing required %s; usage: checker --manifest NEW.json --baseline V08.json "
                             "--report OUT.json" % k)
    cls = vals.get("--evidence-class", "unclassified")
    if cls not in ("synthetic_fixture", "real_candidate", "unclassified"):
        raise ValueError("--evidence-class must be synthetic_fixture, real_candidate or unclassified")
    return vals["--manifest"], vals["--baseline"], vals["--report"], cls


def main(argv):
    try:
        manifest, baseline, report, cls = parse_args(argv)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    for inp, label in ((manifest, "manifest"), (baseline, "baseline")):
        root = os.path.dirname(os.path.abspath(inp))
        rp = os.path.abspath(report)
        try:
            if os.path.commonpath([rp, root]) == root:
                print("report must not be written inside the %s directory: %s" % (label, rp), file=sys.stderr)
                return 2
        except ValueError:
            pass
    try:
        rep = validate(manifest, baseline, report, cls)
    except Exception as exc:
        print("checker failed safely: %s: %s" % (type(exc).__name__, exc), file=sys.stderr)
        return 1
    text = json.dumps(rep, indent=1, ensure_ascii=False)
    print(text)
    if not rep.get("ok"):
        print("FAIL: " + ", ".join(rep.get("failed_gates", ["unknown"])), file=sys.stderr)
    return 0 if rep.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
