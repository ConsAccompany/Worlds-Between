#!/usr/bin/env python3
"""Independent read-only STYLE45 WDC contract check: reference/alpha/composite/ORA/PXO bytes + negative fixtures."""
import argparse, copy, hashlib, io, json, os, sys, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath
import numpy as np
from PIL import Image

W, H = 640, 360; TAG = "20261022-182109-a780b895"
REF_REL = "outputs/style43/rpg-2-star-ocean-the-second_wdc-capitol-west_common-style-reference_nonruntime-v01_20261022-180616-f9471bf4.png"
REF_SHA = "8e3a1cb78b3ba7bd645fa7c0e3c57194fb62147079369d6dc7ae4a6bad7cafe4"
YS = ["rt-ys-mast", "rt-ys-tripod", "rt-ys-beacon", "rt-ys-elm"]; FG = YS + ["rt-fg"]
PURPOSES = ["rt-base"] + FG + ["rt-walk"]; NEED = ["base", "ys-mast", "ys-tripod", "ys-beacon", "ys-elm", "fg", "walk"]
RMAP = dict(zip(NEED, PURPOSES)); REPORT = f"rpg-2-star-ocean-the-second_wdc-capitol-west_style45-native-contract-check_v01_{TAG}.json"
def sha(b): return hashlib.sha256(b).hexdigest()
def text_sha(b): return sha(b.replace(b"\r\n", b"\n"))
def lp(p): return Path("\\\\?\\" + str(Path(p).resolve()))
def arr(b):
    if b is None: return None
    try: return np.array(Image.open(io.BytesIO(b)).convert("RGBA"))
    except Exception: return None
def ok(a): return a is not None and a.shape == (H, W, 4)
def over(d, s):
    a = s[..., 3].astype(np.uint16)[..., None]; o = d.astype(np.uint16).copy()
    o[..., :3] = (s[..., :3].astype(np.uint16) * a + d[..., :3].astype(np.uint16) * (255 - a) + 127) // 255; o[..., 3] = 255
    return o.astype(np.uint8)
def safe(p):
    if not isinstance(p, str) or "\\" in p or ":" in p: raise ValueError("path")
    q = PurePosixPath(p); okp = not q.is_absolute() and q.parts and not any(x in ("..", ".", "") for x in q.parts)
    if not okp: raise ValueError("path")
    return q.as_posix()
def parse_files(m):
    f = m.get("files")
    if not isinstance(f, dict) or not f: raise ValueError("files")
    out = {}
    for p, v in f.items():
        np_ = safe(p)
        if np_ in out: raise ValueError("duplicate path")
        if isinstance(v, str): h, algo, role = v, "sha256-bytes", ""
        elif isinstance(v, dict): h = v.get("sha256"); algo = v.get("hash_algorithm") or "sha256-bytes"; role = str(v.get("role") or "")
        else: raise ValueError("file row")
        if not isinstance(h, str) or len(h) != 64: raise ValueError("sha256")
        out[np_] = (h.lower(), algo, role)
    return out
def digest(b, algo):
    if algo in ("sha256-bytes", "sha256", None, ""): return sha(b)
    if algo == "sha256-text-lf-v1": return text_sha(b)
    raise ValueError("hash_algorithm")
def normkey(k):
    s = str(k).lower().replace("_", "-").strip()
    for pre in ("rt-", "texture-"):
        if s.startswith(pre): s = s[len(pre):]
    return s.replace("ysort-", "ys-").replace("walkmask", "walk").replace("walk-mask", "walk").replace("foreground", "fg")
def val_path(v):
    if isinstance(v, str): return v
    if isinstance(v, dict):
        for k in ("path", "file", "file_path", "new", "target"):
            if isinstance(v.get(k), str): return v[k]
    return None
def collect(x, out):
    if isinstance(x, dict):
        d = {normkey(k): v for k, v in x.items() if normkey(k) in NEED}
        if set(d) == set(NEED): out.append(d)
        for v in x.values(): collect(v, out)
    elif isinstance(x, list):
        d = {normkey(it.get("purpose") or it.get("name") or ""): it for it in x if isinstance(it, dict) and normkey(it.get("purpose") or it.get("name") or "") in NEED}
        if set(d) == set(NEED): out.append(d)
        for it in x: collect(it, out)
def purpose_map(m):
    out = []; collect(m, out)
    if not out: raise ValueError("purpose map missing")
    res = []
    for d in out:
        if any(not val_path(d[k]) for k in NEED): raise ValueError("purpose value")
        res.append(tuple(sorted({k: safe(val_path(d[k])) for k in NEED}.items())))
    if len(set(res)) != 1: raise ValueError("purpose map ambiguous")
    return dict(res[0])
def one(d, needle):
    xs = [x for x in os.listdir(lp(d)) if needle in x.lower()]
    if len(xs) != 1: raise ValueError(f"{needle}:{xs}")
    return lp(d) / xs[0]
def load_old(root):
    cd = root / "game/assets/environments/candidates"; names = os.listdir(lp(cd))
    v12n = [x for x in names if x.startswith("wdc-cw-v12_")]; v13n = [x for x in names if x.startswith("wdc-cw-v13_")]
    if len(v12n) != 1 or len(v13n) != 1: raise ValueError("candidate dirs")
    v12, v13 = lp(cd / v12n[0]), lp(cd / v13n[0]); v12b = one(v12, "scene-manifest").read_bytes()
    v12m = json.loads(v12b.decode("utf-8-sig")); v13m = json.loads(one(v13, "scene-manifest").read_bytes().decode("utf-8-sig"))
    v13c = json.loads(one(v13, "rt-override-contract").read_bytes().decode("utf-8-sig")); v12c = json.loads(one(v12, "rt-contract").read_bytes().decode("utf-8-sig"))
    if v13m["predecessor"]["manifest_sha256"] != sha(v12b): raise ValueError("predecessor")
    f12, un = v12m["files_sha256_bytes"], v13c["unchanged_runtime_layers_v12_sha256"]; old = {"alpha": {}}
    for p in FG + ["rt-walk"]:
        fn = v12c["files"][p]; b = (v12 / fn).read_bytes(); a = arr(b)
        if f12.get(fn) != sha(b) or un.get(p) != sha(b) or not ok(a): raise ValueError("v12 " + p)
        old["walk" if p == "rt-walk" else "alpha"] = b if p == "rt-walk" else a[..., 3]
    bfn = v13c["override"]["file"]; bb = (v13 / bfn).read_bytes(); ba = arr(bb)
    if v13m["files_sha256_bytes"].get(bfn) != sha(bb) or not ok(ba) or not (ba[..., 3] == 255).all(): raise ValueError("v13 base")
    old["base"] = ba[..., :3]; return old
def load_pkg(root, mp):
    m = json.loads(lp(mp).read_bytes().decode("utf-8-sig"))
    if not isinstance(m, dict): raise ValueError("manifest root")
    data = {}
    for p in parse_files(m):
        q = lp(root / p); data[p] = q.read_bytes() if q.exists() else None
    q = lp(root / REF_REL)
    return {"manifest": m, "data": data, "ref": q.read_bytes() if q.exists() else None, "old": load_old(root)}


def add(checks, errs, name, cond, msg):
    checks[name] = bool(cond)
    if not cond: errs.append(msg)


def evaluate(pkg):
    errs, checks = [], {}
    try: files = parse_files(pkg["manifest"])
    except Exception as e: return ["schema:files:" + str(e)], checks
    data, old = pkg["data"], pkg["old"]; hok = True
    for p, (want, algo, role) in files.items():
        b = data.get(p)
        if b is None: errs.append("missing:" + p); hok = False; continue
        try: got = digest(b, algo)
        except Exception: errs.append("algo:" + p); hok = False; continue
        if got != want: errs.append("hash:" + p); hok = False
    checks["manifest_hashes"] = hok
    try: pm = purpose_map(pkg["manifest"])
    except Exception as e: return errs + ["schema:purpose:" + str(e)], checks
    purposes = {RMAP[k]: pm[k] for k in NEED}
    if any(p not in files for p in purposes.values()): return errs + ["schema:purpose_path"], checks
    fc = [p for p, (_, _, r) in files.items() if p.lower().endswith(".png") and ("flat" in p.lower() or "flat" in r.lower())]
    oc = [p for p in files if p.lower().endswith(".ora")]; xc = [p for p in files if p.lower().endswith(".pxo")]
    if len(fc) != 1 or len(oc) != 1 or len(xc) != 1: return errs + ["schema:flat/ora/pxo"], checks
    flatp, orap, pxop = fc[0], oc[0], xc[0]; ref = arr(pkg["ref"])
    add(checks, errs, "reference_sha256", pkg["ref"] is not None and sha(pkg["ref"]) == REF_SHA, "reference:sha256")
    add(checks, errs, "reference_oversized", ok(ref) and ref.shape[0] > H and ref.shape[1] > W, "reference:size")
    if not ok(ref): return errs, checks
    flat = arr(data.get(flatp))
    if not ok(flat): return errs + ["flat:canvas"], checks
    sx = (np.arange(W) * 2 + 1) * ref.shape[1] // (2 * W); sy = (np.arange(H) * 2 + 1) * ref.shape[0] // (2 * H)
    add(checks, errs, "flat_nearest_reference", bool(np.array_equal(flat, ref[sy][:, sx])), "flat:nearest")
    new = {k: arr(data.get(p)) for k, p in purposes.items()}
    for k, a in new.items():
        if not ok(a): errs.append("canvas:" + k)
    cover = np.zeros((H, W), bool)
    for k in FG: cover |= old["alpha"][k] == 255
    fa = fr = True
    for k in FG:
        a = new.get(k)
        if not ok(a): fa = fr = False; continue
        if not np.array_equal(a[..., 3], old["alpha"][k]): fa = False; errs.append("alpha:" + k)
        on = a[..., 3] == 255
        if not np.array_equal(a[on][:, :3], flat[on][:, :3]): fr = False; errs.append("fg_rgb:" + k)
    checks["five_foreground_alphas"] = fa; checks["foreground_opaque_rgb"] = fr
    base = new.get("rt-base")
    bok = ok(base) and (base[..., 3] == 255).all() and np.array_equal(base[~cover][:, :3], flat[~cover][:, :3]) and np.array_equal(base[cover][:, :3], old["base"][cover])
    if not bok: errs.append("base")
    checks["base_hidden_plate"] = bool(bok)
    add(checks, errs, "walk_bytes", data.get(purposes["rt-walk"]) == old["walk"], "walk:bytes")
    comp = False
    if ok(base) and all(ok(new.get(k)) for k in FG):
        c = base.copy()
        for k in FG: c = over(c, new[k])
        comp = bool(np.array_equal(c, flat))
    if not comp: errs.append("runtime_composite")
    checks["runtime_composite"] = comp
    onames, oa, ovis = [], [], []; ora_ok = pxo_ok = guide_ok = False; ob = data.get(orap)
    if ob is None: errs.append("missing:ora")
    else:
        try:
            z = zipfile.ZipFile(io.BytesIO(ob)); st = ET.fromstring(z.read("stack.xml")); stk = st.find("stack")
            if stk is None or int(st.attrib.get("w", 0)) != W or int(st.attrib.get("h", 0)) != H: raise ValueError("canvas")
            ls = stk.findall("layer")[::-1]
            if len(ls) != 7: raise ValueError("layers")
            for l in ls:
                a = arr(z.read(l.attrib["src"]))
                if not ok(a): raise ValueError("layer")
                onames.append(l.attrib.get("name", "")); oa.append(a); ovis.append(l.attrib.get("visibility", "visible") == "visible")
            add(checks, errs, "ora_merged", bool(np.array_equal(arr(z.read("mergedimage.png")), flat)), "ora:merged")
            c = None
            for a, v in zip(oa, ovis):
                if v: c = a.copy() if c is None else over(c, a)
            ora_ok = bool(c is not None and np.array_equal(c, flat))
            if not ora_ok: errs.append("ora:composite")
            guide_ok = len([i for i, v in enumerate(ovis) if not v]) == 1
            checks["ora_composite"] = ora_ok; checks["ora_guide"] = guide_ok
        except Exception as e: errs.append("ora:" + str(e))
    pb = data.get(pxop)
    if pb is None: errs.append("missing:pxo")
    elif oa:
        try:
            pz = zipfile.ZipFile(io.BytesIO(pb)); pd = json.loads(pz.read("data.json")); pl = pd.get("layers", [])
            if (pd.get("size_x"), pd.get("size_y")) != (W, H) or len(pl) != 7 or [l.get("name") for l in pl] != onames: raise ValueError("canvas/layers")
            for i, l in enumerate(pl, 1):
                raw = pz.read(f"image_data/frames/1/layer_{i}")
                if len(raw) != W * H * 4 or not np.array_equal(np.frombuffer(raw, np.uint8).reshape(H, W, 4), oa[i - 1]): raise ValueError("cel")
            pxo_ok = True; guide_ok = guide_ok and pl[-1].get("visible") is False and pl[-1].get("locked") is True and all(l.get("visible") is True for l in pl[:-1])
            if not guide_ok: errs.append("pxo:guide")
        except Exception as e: errs.append("pxo:" + str(e))
    checks["pxo_cels"] = bool(pxo_ok); checks["pxo_guide"] = bool(guide_ok)
    return errs, checks


def png(a):
    b = io.BytesIO(); Image.fromarray(a, "RGBA").save(b, "PNG"); return b.getvalue()
def rawkey(m, p): return next(k for k in m["files"] if safe(k) == p)
def set_hash(m, p, h):
    v = m["files"][rawkey(m, p)]
    if isinstance(v, dict): v["sha256"] = h
    else: m["files"][rawkey(m, p)] = h


def fixtures(pkg):
    out = {}; pm = purpose_map(pkg["manifest"]); basep, fp = pm["base"], pm["fg"]
    flatp = [p for p, (_, _, r) in parse_files(pkg["manifest"]).items() if p.lower().endswith(".png") and ("flat" in p.lower() or "flat" in r.lower())][0]
    q = copy.deepcopy(pkg); f = q["manifest"]["files"]; f["../escape.png"] = f.pop(rawkey(q["manifest"], basep)); out["malformed_path"] = q
    q = copy.deepcopy(pkg); set_hash(q["manifest"], flatp, "0" * 64); out["bad_hash"] = q
    q = copy.deepcopy(pkg); a = arr(q["data"][basep]); q["data"][basep] = png(np.array(Image.fromarray(a, "RGBA").resize((W - 1, H), Image.NEAREST))); set_hash(q["manifest"], basep, sha(q["data"][basep])); out["bad_size"] = q
    q = copy.deepcopy(pkg); a = arr(q["data"][fp]).copy(); ys, xs = np.where(a[..., 3] == 255); a[ys[0], xs[0], 3] = 0; q["data"][fp] = png(a); set_hash(q["manifest"], fp, sha(q["data"][fp])); out["bad_alpha"] = q
    res = {}
    for name, p in out.items():
        try: e, _ = evaluate(p); res[name] = {"rejected": bool(e), "errors": e[:3]}
        except Exception as ex: res[name] = {"rejected": True, "errors": [type(ex).__name__ + ":" + str(ex)]}
    return res


def write_report(out, rep):
    out = Path(out).resolve(); out.mkdir(parents=True, exist_ok=True)
    p = out / REPORT; lp(p).write_bytes((json.dumps(rep, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return str(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True); ap.add_argument("--manifest", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); root = Path(a.root).resolve(); mp = Path(a.manifest); mp = mp if mp.is_absolute() else root / mp
    rep = {"tool": "style45-native-contract-check", "tag": TAG, "root": str(root), "manifest": str(mp), "status": "FAIL",
           "checks": {}, "fixtures": {}, "errors": [], "reference": {"file": REF_REL, "sha256": REF_SHA},
           "limitations": ["Static archive/pixel checks only; no Pixelorama/GUI, Godot runtime, native editor, performance, art or default approval claim.",
                           "Never writes producer files; the fixed generated reference is oversized and is not native hand-authored art.",
                           "Flat is required to be its exact floor-centre NEAREST sample; generated provenance is not art approval."]}
    if not lp(mp).exists():
        rep["status"] = "PENDING"; rep["errors"] = ["manifest_missing"]
        print(json.dumps({"status": "PENDING", "errors": rep["errors"], "report": write_report(a.out, rep)})); return 2
    try:
        pkg = load_pkg(root, mp); errs, checks = evaluate(pkg); rep["checks"] = checks
        if errs: rep["errors"] = errs; rep["status"] = "FAIL"
        else:
            fx = fixtures(pkg); rep["fixtures"] = fx; bad = [k for k, v in fx.items() if not v["rejected"]]
            if bad: rep["errors"] = ["negative_fixture_not_rejected:" + ",".join(bad)]; rep["status"] = "FAIL"
            else: rep["status"] = "PASS"
    except Exception as e: rep["errors"] = [type(e).__name__ + ":" + str(e)]
    print(json.dumps({"status": rep["status"], "errors": rep["errors"], "report": write_report(a.out, rep)}))
    return {"PASS": 0, "FAIL": 1, "PENDING": 2}[rep["status"]]


if __name__ == "__main__":
    sys.exit(main())
