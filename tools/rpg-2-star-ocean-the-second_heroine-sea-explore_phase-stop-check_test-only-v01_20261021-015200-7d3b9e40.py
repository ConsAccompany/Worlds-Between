"""Read-only checker for the heroine Sea phase-aware side stop package (contract 99b25894).
Usage: python -I <this> --manifest <new transition json> --baseline <v08 transition json> --report <unique report json> [--mutations]
--mutations copies the run to a temp dir, applies bad-hash / missing-phase / mutated-idle / invalid-path / malformed-JSON
mutations and requires each to FAIL cleanly (exit 1, no traceback) without changing the original run.
"""
import hashlib, io, json, re, sys, zipfile, subprocess, tempfile, shutil
from pathlib import Path
import numpy as np
from PIL import Image

SCHEMA = "worlds-between.exploration-stop-transition.supplemental.v1"
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*_[a-z0-9-]+_[a-z0-9-]+_[a-z0-9-]+_\d{8}-\d{6}-[0-9a-f]{8}\.(png|pxo|json)$")
W, H = 80, 112
res = []
def ck(name, ok, info=""): res.append({"check": name, "pass": bool(ok), "info": str(info)})
sha = lambda b: hashlib.sha256(b).hexdigest()


def xp(p):
    p = str(Path(p).resolve())
    return Path("\\\\?\\" + p) if sys.platform == "win32" and not p.startswith("\\\\?\\") else Path(p)


def safe_read(d, fn):
    if not isinstance(fn, str) or "/" in fn or "\\" in fn or ".." in fn or not NAME.match(fn): return None, "invalid path/name"
    p = d / fn
    if not p.is_file(): return None, "missing"
    return p.read_bytes(), ""


def rgba(b):
    im = Image.open(io.BytesIO(b)); return im, np.array(im.convert("RGBA"))


def check(mpath, bpath):
    d, bd = mpath.parent, bpath.parent
    try:
        m = json.loads(mpath.read_text(encoding="utf-8")); bt = json.loads(bpath.read_text(encoding="utf-8"))
    except Exception as e:
        ck("manifest/baseline JSON parse", False, type(e).__name__); return
    ck("schema", m.get("schema") == SCHEMA and bt.get("schema") == SCHEMA)
    try: wms = json.loads((bd / bt["source_manifest"]).read_text(encoding="utf-8"))["actions"]["walk"]["east"][0]["duration_ms"]
    except Exception: wms = None
    # 120 ms is the inclusive settle (s1+s2+s3 at the walk frame duration), not a per-frame duration
    ck("timing/pivot/scale fields", wms is not None and m.get("frame_ms") == wms and 3 * wms == m.get("settle_ms_inclusive") == 120
       and m.get("pivot") == [40, 104] and m.get("logical_height") == 48, (m.get("frame_ms"), wms, m.get("settle_ms_inclusive"), m.get("pivot")))
    sb, why = safe_read(d, m.get("source_set"))
    ck("source_set present", sb is not None, why)
    if sb is None: return
    ck("source_set_sha256", sha(sb) == m.get("source_set_sha256"))
    ck("source_manifest == source_set", m.get("source_manifest") == m.get("source_set"))
    try: ss = json.loads(sb.decode("utf-8")); bs = json.loads((bd / bt["source_manifest"]).read_text(encoding="utf-8"))
    except Exception as e: ck("source set JSON parse", False, type(e).__name__); return
    ck("source set schema", ss.get("schema") == bs.get("schema") == "worlds-between.exploration-source.v1")
    ck("source set pivot/size/density", ss.get("pivot") == bs.get("pivot") and ss.get("frame_size") == bs.get("frame_size") and ss.get("density") == bs.get("density"))
    # 52 protected idle/walk frames
    n52, bad52 = 0, []
    pngs = {}
    for act in ("idle", "walk"):
        for dr in ("south", "west", "north", "east"):
            a, b = ss.get("actions", {}).get(act, {}).get(dr, []), bs["actions"][act][dr]
            if len(a) != len(b): bad52.append(f"{act}/{dr} count"); continue
            for i, (fa, fb) in enumerate(zip(a, b)):
                x, why = safe_read(d, fa.get("file")); y = (bd / fb["file"]).read_bytes()
                if x is None or x != y or fa.get("duration_ms") != fb["duration_ms"]: bad52.append(f"{act}/{dr}/f{i} {why}")
                else: n52 += 1; pngs[(act, dr, i)] = x
    ck("52 idle/walk PNG bytes equal v08 baseline", n52 == 52 and not bad52, f"{n52} equal; bad {bad52[:4]}")
    # legacy stop paths unchanged
    nl, badl = 0, []
    for dr, cs in bt["directions"].items():
        for c, e in cs.items():
            ne = m.get("directions", {}).get(dr, {}).get(c)
            if not ne or ne.get("from_walk_frame") != e["from_walk_frame"] or len(ne.get("bridge", [])) != len(e["bridge"]):
                badl.append(f"{dr}/{c} shape"); continue
            fb, _ = safe_read(d, ne.get("final"))
            if fb is None or fb != (bd / e["final"]).read_bytes(): badl.append(f"{dr}/{c} final")
            for k, (x, y) in enumerate(zip(ne["bridge"], e["bridge"])):
                xb, why = safe_read(d, x.get("file"))
                if xb is None or sha(xb) != x.get("sha256") or xb != (bd / y["file"]).read_bytes(): badl.append(f"{dr}/{c}/b{k} {why}")
                else: nl += 1
    ck("legacy contact0/contact6 stop images unchanged (16)", nl == 16 and not badl and set(m.get("directions", {})) == set(bt["directions"]), badl[:4])
    # phase bridges
    pb = m.get("phase_bridges", {})
    ck("phase_bridges east/west only", isinstance(pb, dict) and set(pb) == {"east", "west"}, sorted(pb) if isinstance(pb, dict) else type(pb).__name__)
    samples = {}
    for dr in ("east", "west"):
        ph = pb.get(dr, {}) if isinstance(pb, dict) else {}
        ck(f"{dr} 12 phase keys", isinstance(ph, dict) and set(ph) == {f"phase{p}" for p in range(12)}, len(ph) if isinstance(ph, dict) else 0)
        idle = pngs.get(("idle", dr, 0))
        for p in range(12):
            e = ph.get(f"phase{p}") if isinstance(ph, dict) else None
            if not isinstance(e, dict): ck(f"{dr} phase{p} entry", False, "missing"); continue
            br = e.get("bridge", [])
            bad = []
            if e.get("from_walk_frame") != p: bad.append("from_walk_frame")
            if len(br) != 4: bad.append(f"{len(br)} samples"); ck(f"{dr} phase{p}", False, bad); continue
            for s, f in enumerate(br):
                b, why = safe_read(d, f.get("file"))
                if b is None: bad.append(f"s{s} {why}"); continue
                if sha(b) != f.get("sha256"): bad.append(f"s{s} hash")
                im, a = rgba(b)
                if im.size != (W, H) or im.mode != "RGBA": bad.append(f"s{s} size/mode")
                al = a[..., 3]
                if not np.isin(al, (0, 255)).all(): bad.append(f"s{s} soft alpha")
                if al[0].any() or al[-1].any() or al[:, 0].any() or al[:, -1].any() or al[104:].any(): bad.append(f"s{s} bounds")
                samples[(dr, p, s)] = a
                if s == 0 and b != pngs.get(("walk", dr, p)): bad.append("s0 != walk")
                if s == 3 and b != idle: bad.append("s3 != idle0")
                if s in (1, 2) and (b == pngs.get(("walk", dr, p)) or b == idle): bad.append(f"s{s} not newly sampled")
            ck(f"{dr} phase{p} 4 samples", not bad, ",".join(bad) or "s0=walk, s3=idle0, s1/s2 new")
        # west mirrors east (disclosed)
    mir = sum(1 for (dr, p, s), a in samples.items() if dr == "west" and (("east", p, s) in samples) and np.array_equal(a, samples[("east", p, s)][:, ::-1]))
    ck("west samples = east mirrored (disclosed)", mir == 48, mir)
    # native PXO frames reconstruct every one of the 96 sample PNGs; glove layer only at s3
    for sf in ss.get("source_files", []):
        b, why = safe_read(d, sf.get("file"))
        if b is None: ck(f"pxo {sf.get('file')}", False, why); continue
        ck(f"pxo sha {sf['direction']}", sha(b) == sf.get("sha256"))
        try:
            z = zipfile.ZipFile(io.BytesIO(b)); meta = json.loads(z.read("data.json"))
        except Exception as e: ck(f"pxo {sf['direction']} open", False, type(e).__name__); continue
        names = [l["name"] for l in meta["layers"]]; dr = sf["direction"]
        ck(f"pxo {dr} 48 frames / layers", len(meta["frames"]) == 48 and names == sf.get("layers_bottom_to_top"), (len(meta["frames"]), len(names)))
        mism, glove_bad, meth = 0, [], []
        gi = names.index("idle-arm-glove"); si_ = names.index("near-arm-sleeve")
        for fi in range(min(48, len(meta["frames"]))):
            p, s = divmod(fi, 4)
            comp = np.zeros((H, W, 4), np.uint8); lay = []
            for li in range(len(names)):
                raw = np.frombuffer(z.read(f"image_data/frames/{fi + 1}/layer_{li + 1}"), np.uint8).reshape(H, W, 4); lay.append(raw)
                sel = raw[..., 3] > 0; comp[sel] = raw[sel]
            if (dr, p, s) not in samples or not np.array_equal(comp, samples[(dr, p, s)]): mism += 1
            if (lay[gi][..., 3].any()) != (s == 3): glove_bad.append(fi)
            if (lay[si_][..., 3].any()) != (s != 3): meth.append(fi)
        ck(f"pxo {dr} 48 native frames == sample PNGs", mism == 0, f"{mism} mismatched")
        ck(f"pxo {dr} original glove only at s3 (no swap before rest)", not glove_bad, glove_bad[:6])
        ck(f"pxo {dr} authored sleeve arm in s0..s2", not meth, meth[:6])
    ck("two side PXOs", sorted(s.get("direction") for s in ss.get("source_files", [])) == ["east", "west"])
    for o in ss.get("original_source_files", []):
        p = xp(Path(__file__).resolve().parents[1] / o["file"])
        ck(f"original v08 source read-only pin {o['direction']} {o['format']}", p.is_file() and sha(p.read_bytes()) == o["sha256"])
    # informational continuity metric (not an acceptance claim): wrist path per east phase
    poses = m.get("phase_bridge_poses_east", {})
    steps = []
    for p in range(12):
        e = poses.get(f"phase{p}", [])
        ws = [x.get("near_wrist") for x in e if x.get("near_wrist")]
        if len(ws) == 2: steps.append(round(float(np.hypot(*np.subtract(ws[1], ws[0]))), 2))
    ck("east s1->s2 near-wrist step recorded (info only)", len(steps) == 12, steps)


def mutations(args):
    src = xp(args.manifest).parent; tmp = Path(tempfile.mkdtemp(prefix="hss"))
    before = {p.name: sha(p.read_bytes()) for p in src.iterdir()}
    out = []
    def run(name, mutate):
        dd = tmp / name; shutil.copytree(src, dd); mp = dd / xp(args.manifest).name
        mutate(dd, mp)
        r = subprocess.run([sys.executable, "-I", __file__, "--manifest", str(mp), "--baseline", str(args.baseline),
                            "--report", str(tmp / f"{name}.json")], capture_output=True, text=True, encoding="utf-8")
        ok = r.returncode == 1 and "Traceback" not in r.stderr + r.stdout
        out.append((name, ok, r.returncode))
    def jm(mp, f):
        j = json.loads(mp.read_text(encoding="utf-8")); f(j); mp.write_text(json.dumps(j), encoding="utf-8")
    run("bad-hash", lambda dd, mp: jm(mp, lambda j: j["phase_bridges"]["east"]["phase3"]["bridge"][1].__setitem__("sha256", "0" * 64)))
    run("missing-phase", lambda dd, mp: jm(mp, lambda j: j["phase_bridges"]["west"].pop("phase7")))
    def idle(dd, mp):
        f = next(dd.glob("*explore-east-idle-f00*.png")); a = np.array(Image.open(f)); a[60, 40, :3] ^= 1; Image.fromarray(a).save(f)
    run("mutated-idle", idle)
    run("invalid-path", lambda dd, mp: jm(mp, lambda j: j["phase_bridges"]["east"]["phase0"]["bridge"][2].__setitem__("file", "../x.png")))
    run("malformed-json", lambda dd, mp: mp.write_text("{\"schema\": ", encoding="utf-8"))
    after = {p.name: sha(p.read_bytes()) for p in src.iterdir()}
    shutil.rmtree(tmp, ignore_errors=True)
    for n, ok, rc in out: ck(f"mutation {n} fails cleanly", ok, f"exit {rc}")
    ck("original run unchanged by mutation tests", before == after)


def main():
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--manifest", required=True); ap.add_argument("--baseline", required=True)
    ap.add_argument("--report", required=True); ap.add_argument("--mutations", action="store_true")
    args = ap.parse_args()
    rp = Path(args.report)
    if rp.exists(): print("FAIL report path exists (unique report required)"); sys.exit(1)
    try:
        check(xp(args.manifest), xp(args.baseline))
    except Exception as e:                      # malformed input must fail clearly, never with a traceback
        ck("checker completed without exception", False, f"{type(e).__name__}: {str(e)[:120]}")
    if args.mutations: mutations(args)
    nf = sum(1 for r in res if not r["pass"])
    for r in res: print(("PASS " if r["pass"] else "FAIL ") + r["check"] + (" :: " + r["info"] if r["info"] else ""))
    print(f"SUMMARY {len(res) - nf}/{len(res)} PASS")
    rp.write_text(json.dumps({"manifest": str(args.manifest), "manifest_sha256": sha(xp(args.manifest).read_bytes()) if xp(args.manifest).is_file() else None,
                              "baseline": str(args.baseline), "checker": Path(__file__).name,
                              "checker_sha256TextLf": sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n")),
                              "results": res, "failed": nf}, indent=1), encoding="utf-8", newline="\n")
    sys.exit(1 if nf else 0)


if __name__ == "__main__":
    main()
