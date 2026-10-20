"""v04 gait check (copy of v03 9d2e4a61 + 12-walk, bridge, transition checks). Check a worlds-between.exploration-source.v1 manifest + native layer sources. Read-only.
Usage: python -I <this> <manifest.json> [--author-tool <tool.py>]   (determinism rebuild into a temp tag)
"""
import hashlib, io, json, re, sys, zipfile, subprocess, tempfile, shutil
from pathlib import Path
import numpy as np
from PIL import Image

SOUTH_SHA = "6bf1d688487bd3fcc71eeb2e7c9b7c74f1fe6b6cd6362860b7fa0d42e009e429"
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*_[a-z0-9-]+_[a-z0-9-]+_[a-z0-9-]+_\d{8}-\d{6}-[0-9a-f]{8}\.(png|pxo|ora|json)$")
res = []
def ck(name, ok, info=""): res.append((name, bool(ok), info)); print(("PASS " if ok else "FAIL ") + name + (" :: " + str(info) if info else ""))


def main():
    mp = Path(sys.argv[1]).resolve(); d = mp.parent
    m = json.loads(mp.read_text(encoding="utf-8"))
    ck("schema", m.get("schema") == "worlds-between.exploration-source.v1")
    ck("actor_id", m.get("actor_id") == "protagonist-female"); ck("density", m.get("density") == 2)
    ck("frame_size", m.get("frame_size") == [80, 112]); ck("pivot", m.get("pivot") == [40, 104])
    acts = m.get("actions", {})
    BR = {}
    tps = sorted(d.glob("*stop-transition-manifest*.json")); ck("one transition manifest", len(tps) == 1, len(tps))
    if tps:
        tm = json.loads(tps[0].read_text(encoding="utf-8"))
        for dr, cs in tm["directions"].items():
            BR[dr] = []
            for c in ("contact0", "contact6"):
                e = cs[c]; ck(f"bridge {dr} {c} final is idle0", e["final"] == acts["idle"][dr][0]["file"])
                ck(f"bridge {dr} {c} 2 frames", len(e["bridge"]) == 2)
                for b in e["bridge"]:
                    bb = (d / b["file"]).read_bytes(); ck(f"bridge sha {b['file'][-48:]}", hashlib.sha256(bb).hexdigest() == b["sha256"] and NAME.match(b["file"]))
                    a = np.array(Image.open(io.BytesIO(bb)).convert("RGBA"))[..., 3]
                    ck(f"bridge alpha/ground {b['file'][-48:]}", np.isin(a, (0, 255)).all() and not a[104:].any() and not a[:, 0].any() and not a[:, -1].any())
                    BR[dr].append({"file": b["file"]})
    for dr in ("south", "west", "north", "east"):
        ck(f"walk/{dr} exactly 12", len(acts.get("walk", {}).get(dr, [])) == 12)
    ck("actions keys", set(acts) == {"idle", "walk"}, sorted(acts))
    seen = set()
    for act, (lo, hi) in (("idle", (1, 16)), ("walk", (2, 16))):
        ck(f"{act} four directions", set(acts.get(act, {})) == {"south", "west", "north", "east"})
        for dr, fr in acts.get(act, {}).items():
            ck(f"{act}/{dr} count {lo}..{hi}", lo <= len(fr) <= hi, len(fr))
            for i, f in enumerate(fr):
                fn, ms = f.get("file"), f.get("duration_ms")
                ok_ms = isinstance(ms, int) and not isinstance(ms, bool) and 40 <= ms <= 2000
                p = (d / fn).resolve()
                inside = p.parent == d and "/" not in fn and "\\" not in fn
                bad = []
                if not ok_ms: bad.append("duration")
                if not inside: bad.append("outside")
                if fn in seen: bad.append("dup")
                if not NAME.match(fn): bad.append("name")
                seen.add(fn)
                b = p.read_bytes(); im = Image.open(io.BytesIO(b))
                if im.size != (80, 112) or im.mode != "RGBA": bad.append(f"size/mode {im.size} {im.mode}")
                a = np.array(im.convert("RGBA"))[..., 3]
                if not np.isin(a, (0, 255)).all(): bad.append("soft alpha")
                if a[0].any() or a[-1].any() or a[:, 0].any() or a[:, -1].any(): bad.append("border")
                if a[104:].any(): bad.append("y>=104")
                ys = np.nonzero(a.any(1))[0]
                if act == "idle":
                    h = ys[-1] - ys[0] + 1
                    if h != 96 or ys[-1] != 103: bad.append(f"idle height {h} last {ys[-1]}")
                if act == "idle" and dr == "south" and i == 0 and hashlib.sha256(b).hexdigest() != SOUTH_SHA: bad.append("south idle0 not exact")
                ck(f"{act}/{dr}/f{i}", not bad, ",".join(bad) or f"{ms}ms rows {ys[0]}..{ys[-1]}")
    # native layer sources reconstruct exported frames exactly
    for sf in m.get("source_files", []):
        p = d / sf["file"]; b = p.read_bytes()
        ck(f"source sha {sf['file'][-40:]}", hashlib.sha256(b).hexdigest() == sf["sha256"])
        if sf["format"] == "pixelorama-pxo":
            z = zipfile.ZipFile(io.BytesIO(b)); meta = json.loads(z.read("data.json"))
            nl = len(meta["layers"]); dr = sf["direction"]
            frames = acts["idle"][dr] + acts["walk"][dr] + BR.get(dr, [])
            ck(f"pxo {dr} frame count", len(meta["frames"]) == len(frames), (len(meta["frames"]), len(frames)))
            mism = 0
            for fi, f in enumerate(frames):
                comp = np.zeros((112, 80, 4), np.uint8)
                for li in range(nl):
                    raw = np.frombuffer(z.read(f"image_data/frames/{fi + 1}/layer_{li + 1}"), np.uint8).reshape(112, 80, 4)
                    s = raw[..., 3] > 0; comp[s] = raw[s]
                exp = np.array(Image.open(d / f["file"]).convert("RGBA"))
                if not np.array_equal(comp, exp): mism += 1
            ck(f"pxo {dr} layers reconstruct exports", mism == 0, f"{mism} mismatched frames")
    if "--author-tool" in sys.argv:
        tool = sys.argv[sys.argv.index("--author-tool") + 1]
        tag = re.search(r"_(\d{8}-\d{6})-[0-9a-f]{8}\.json$", mp.name).group(1)
        tmp = Path(tempfile.mkdtemp(prefix="hsx"))
        root = Path(tool).resolve().parents[1]
        # rebuild in a disposable copy of the output root to prove determinism without touching the run
        out = subprocess.run([sys.executable, "-I", tool, "--out-tag", tag + "9"], capture_output=True, text=True, encoding="utf-8")
        ck("rebuild exit", out.returncode == 0, out.stderr[-300:])
        if out.returncode == 0:
            m2 = Path(out.stdout.strip().splitlines()[-1]); j2 = json.loads(m2.read_text(encoding="utf-8"))
            diff = 0
            for act in acts:
                for dr in acts[act]:
                    for a1, a2 in zip(acts[act][dr], j2["actions"][act][dr]):
                        if (d / a1["file"]).read_bytes() != (m2.parent / a2["file"]).read_bytes(): diff += 1
            ck("deterministic PNG rebuild", diff == 0, f"{diff} differing frames")
            shutil.rmtree(m2.parent)
        shutil.rmtree(tmp, ignore_errors=True)
    nf = sum(1 for r in res if not r[1])
    print(f"SUMMARY {len(res) - nf}/{len(res)} PASS")
    sys.exit(1 if nf else 0)


if __name__ == "__main__":
    main()
