"""Deterministic + file-level check for the UNAPPROVED / NONRUNTIME female south compact locomotion pilot v02 (m8-w05).

Re-measures from the files on disk; never imports the builder:
  01 v8 source sha256-bytes lock
  02 rebuild into a temp dir is byte-identical to the asset folder (all files)
  03 manifest: LF only, flags all false, display 48 px / scale 0.5 / no flip, part / keyframe / .pxo / .ora hashes
  04 every part and keyframe PNG: 80x120 RGBA, binary alpha, colours inside v8's palette
  05 an independent re-implementation of the documented compositor rule (rig in the manifest) stacks the PART PNGs
     into every keyframe PNG exactly, and into v8 exactly at the neutral state
  06 upper-body identity: keyframe rows 8..57 outside the declared arm / hair zones == v8 moved by the bob
  07 the manifest's nominal per-px gait table: every stance run lasts stance_px and its boot's world row
     (phase + ground + o) is constant (0 px planted-boot world displacement), the swing never leaves the cell
  08 the part-library .ora: mimetype first and stored, one stack.xml layer per part, each layer == its part PNG
  09 no runtime script / scene references the pilot
  10 (--pixelorama) Pixelorama 1.2.3 headless (isolated APPDATA): the keyframes .pxo exports to the keyframe PNGs and
     the .ora --split-layers exports to the part PNGs
  11 (--receipt <capture receipt>) the Godot capture receipt: flags false, every listed output PNG exists with its
     sha256, every walk / stop / re-press record has 0 planted-boot world displacement, 0-pixel switch to v8 and
     re-press alternation; (with the GIF receipt next to it) every GIF hash matches
Usage (repository root): python -I tests/<this dir>/<this> [--pixelorama] [--receipt outputs/<capture receipt>.json]
"""
import argparse, glob, hashlib, io, json, os, shutil, subprocess, sys, tempfile, zipfile
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ASSET_REL = "game/assets/characters/locomotion-pilots-compact-v02"
BUILDER_GLOB = "tools/rpg-2-star-ocean-the-second_protagonist-female_south-locomotion-compact-v02-build_m8-w05_20261016-200500-*.py"
V8_REL = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_"
          "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
V8_SHA256 = "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
PIXELORAMA_REL = "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"
W, H = 80, 120
INK = (0x0a, 0x0a, 0x0e)
HTAG = {-1: "m1", 0: "0", 1: "p1"}

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("OK   " if ok else "FAIL ") + name + ("" if not detail else "  " + str(detail)[:600]))


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def rgba(path):
    return np.array(Image.open(path).convert("RGBA"))


def texels(a):
    ys, xs = np.nonzero(a[:, :, 3])
    return {(int(x), int(y)): tuple(int(c) for c in a[y, x, :3]) for x, y in zip(xs, ys)}


# ---------------------------------------------------------------- independent compositor (from the manifest's rule)
def rdiv(n, d):
    return (2 * n + d) // (2 * d)


def pick(src, n):
    return [src[min(len(src) - 1, (i * len(src)) // n)] for i in range(n)]


def compose(parts, rig, state):
    b, h = state["bob"], state["hdy"]
    hip, boot_top = rig["hip_row"], rig["boot_top_row"]

    def sh(role):
        return {(x, y + b): c for (x, y), c in parts[role].items()}

    legs = {}
    for side in ("vl", "vr"):
        f = state["feet"][side]
        dy = f["o"] - f["lift"]
        boot = {(x, y + dy): c for (x, y), c in parts[f"boot-{side}-{f['view']}"].items()}
        bt = min(y for (_, y) in boot)
        k0, k1 = rig["knee_band_rows"][side]
        T, K, S = list(range(hip, k0)), list(range(k0, k1 + 1)), list(range(k1 + 1, boot_top))
        n = bt - (hip + b)
        if n < len(K) + 2:
            th, kn, shn = [T[0]], pick(K, n - 2), [S[-1]]
        else:
            rest = n - len(K)
            nt = max(1, min(rest - 1, rdiv(rest * len(T), len(T) + len(S))))
            th, kn, shn = pick(T, nt), K, pick(S, rest - nt)
        kdx = f["kin"] * rig["inward_dx"][side]
        rows = {}
        for (x, y), c in parts[f"leg-src-{side}"].items():
            rows.setdefault(y, []).append((x, c))
        out, y = {}, hip + b
        for i, sy in enumerate(th):
            dx = rdiv(kdx * i * i, (len(th) - 1) ** 2) if len(th) > 1 else 0
            out.update({(x + dx, y): c for x, c in rows.get(sy, [])})
            y += 1
        for sy in kn:
            out.update({(x + kdx, y): c for x, c in rows.get(sy, [])})
            y += 1
        for i, sy in enumerate(shn):
            dx = kdx + rdiv(-kdx * (i + 1), len(shn) + 1)
            out.update({(x + dx, y): c for x, c in rows.get(sy, [])})
            y += 1
        out.update(boot)
        legs[side] = out
    fe = state["feet"]
    contact = {s: fe[s]["lift"] == 0 and fe[s]["view"] == "v8" for s in ("vl", "vr")}
    if contact["vl"] != contact["vr"]:
        near = "vl" if not contact["vl"] else "vr"
    else:
        near = "vl" if fe["vl"]["o"] > fe["vr"]["o"] else "vr"
    far = "vl" if near == "vr" else "vr"
    R, L = state["arms"]["R"], state["arms"]["L"]
    g = {}
    for role in (f"cape-hdy-{HTAG[h]}", f"arm-vl-{R}-back", f"arm-vr-{L}-back"):
        g.update(sh(role))
    hips = sh("hips")
    g.update(hips)
    g.update(legs[far])
    g.update(legs[near])
    for role in ("coat-skirt", "upper-body", f"arm-vl-{R}-seam", f"arm-vr-{L}-seam", f"hair-hdy-{HTAG[h]}",
                 f"arm-vl-{R}-front", f"arm-vr-{L}-front"):
        g.update(sh(role))
    legmask = set(hips) | set(legs[far]) | set(legs[near])
    holes = [(x, y) for y in range(hip + b, H) for x in range(1, W - 1) if (x, y) not in g and
             all(q in g for q in ((x - 1, y), (x + 1, y), (x, y - 1))) and
             any(q in legmask for q in ((x - 1, y), (x + 1, y), (x, y - 1)))]
    for q in holes:
        g[q] = INK
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pixelorama", action="store_true")
    ap.add_argument("--receipt")
    args = ap.parse_args()
    os.chdir(REPO)
    check("01 v8 sha256-bytes", sha(V8_REL) == V8_SHA256)
    builders = glob.glob(BUILDER_GLOB)
    check("02a single builder", len(builders) == 1, builders)
    tmp = tempfile.mkdtemp(prefix="wb-locochk-")
    try:
        out = os.path.join(tmp, "b")
        r = subprocess.run([sys.executable, "-I", "-B", builders[0], "--out-dir", out], capture_output=True, text=True)
        names = sorted(os.listdir(ASSET_REL))
        same = r.returncode == 0 and sorted(os.listdir(out)) == names and all(
            open(os.path.join(out, n), "rb").read() == open(os.path.join(ASSET_REL, n), "rb").read() for n in names)
        check("02 rebuild byte-identical to asset folder", same, f"{len(names)} files" + ("" if r.returncode == 0 else r.stderr[-300:]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    mpath = glob.glob(os.path.join(ASSET_REL, "*-manifest_*.json"))[0]
    raw = open(mpath, "rb").read()
    m = json.loads(raw)
    check("03a manifest LF only", b"\r" not in raw)
    flags = ["art_approved", "human_reviewed", "runtime_integrated", "walk_animation_approved",
             "stop_animation_approved", "counts_toward_art_acceptance"]
    check("03b manifest flags false", not any(m[f] for f in flags))
    d = m["display"]
    check("03c display 48 px / 0.5 / no flip / nearest", d["scale"] == 0.5 and d["logical_height_px"] == 48 and not d["flip_h"]
          and d["filter"] == "nearest")
    entries = m["parts"] + m["keyframes"]
    check("03d part + keyframe PNG hashes", all(sha(os.path.join(ASSET_REL, e["file"])) == e["sha256"] for e in entries),
          f"{len(m['parts'])} parts + {len(m['keyframes'])} keyframes")
    es = m["editable_sources"]
    check("03e .pxo / .ora hashes", sha(os.path.join(ASSET_REL, es["keyframes_pxo"])) == es["keyframes_pxo_sha256"] and
          sha(os.path.join(ASSET_REL, es["part_library_ora"])) == es["part_library_ora_sha256"])
    v8 = rgba(V8_REL)
    pal = {tuple(int(c) for c in px[:3]) for px in v8.reshape(-1, 4) if px[3]}
    bad = []
    imgs = {}
    for e in entries:
        a = rgba(os.path.join(ASSET_REL, e["file"]))
        imgs[e["file"]] = a
        cols = {tuple(int(c) for c in px[:3]) for px in a.reshape(-1, 4) if px[3]}
        if a.shape != (H, W, 4) or not set(np.unique(a[:, :, 3])) <= {0, 255} or not cols <= pal:
            bad.append(e["file"])
    check("04 80x120 RGBA / binary alpha / v8 palette", not bad, bad)
    parts = {e["role"]: texels(imgs[e["file"]]) for e in m["parts"]}
    v8t = texels(v8)
    neutral = {"bob": 0, "hdy": 0, "arms": {"R": "N", "L": "N"},
               "feet": {s: {"o": 0, "lift": 0, "view": "v8", "kin": 0} for s in ("vl", "vr")}}
    check("05a independent compositor: neutral state == v8", compose(parts, m["rig"], neutral) == v8t)
    mism = [k["key"] for k in m["keyframes"] if compose(parts, m["rig"], k["state"]) != texels(imgs[k["file"]])]
    check("05b independent compositor: parts -> every keyframe PNG", not mism, mism or f"{len(m['keyframes'])} keyframes")
    idm = {}
    for k in m["keyframes"]:
        a, b = imgs[k["file"]], k["state"]["bob"]
        n = 0
        for y in range(8, 58):
            for x in range(80):
                if (y >= 40 and (x <= 27 or x >= 45)) or (23 <= y <= 32 and x <= 24):
                    continue
                n += not np.array_equal(v8[y, x], a[y + b, x])
        if n:
            idm[k["key"]] = n
    check("06 upper-body identity vs v8 + bob", not idm, idm)
    g = m["gait"]
    table = m["metrics"]["nominal_per_px"]
    runs_ok, runs = True, {}
    for side in ("vl", "vr"):
        rows, lens = [], []
        for ph in range(2 * len(table)):
            f = table[ph % len(table)]["feet"][side]
            if f["contact"]:
                rows.append(ph + m["rig"]["ground_rows"][side] + f["o"])
            elif rows:
                lens.append(len(rows))
                runs_ok &= max(rows) == min(rows)
                rows = []
        runs[side] = lens
        runs_ok &= all(n == g["stance_px"] for n in lens[1:])
    swing_ok = all(0 <= r["feet"][s]["sole_row"] < H for r in table for s in ("vl", "vr"))
    check("07 nominal gait: stance runs of stance_px with a constant world row; soles inside the cell", runs_ok and swing_ok,
          {"stance_runs_px": runs, "stance_ms_at_140": g["stance_ms_at_140"], "cycle_ms_at_140": g["cycle_ms_at_140"]})
    z = zipfile.ZipFile(os.path.join(ASSET_REL, es["part_library_ora"]))
    infos = z.infolist()
    ok = infos[0].filename == "mimetype" and infos[0].compress_type == zipfile.ZIP_STORED and z.read("mimetype") == b"image/openraster"
    root = ET.fromstring(z.read("stack.xml"))
    layers = [(l.get("name"), l.get("src")) for l in root.iter("layer")]
    ok &= sorted(n for n, _ in layers) == sorted(parts) and root.get("w") == str(W) and root.get("h") == str(H)
    for n, src in layers:
        ok &= texels(np.array(Image.open(io.BytesIO(z.read(src))).convert("RGBA"))) == parts[n]
    ok &= texels(np.array(Image.open(io.BytesIO(z.read("mergedimage.png"))).convert("RGBA"))) == v8t
    check("08 part-library .ora: structure + every layer == its part PNG; merged == v8", ok, f"{len(layers)} layers")
    refs = []
    for rdir in ("game/scripts", "game/scenes"):
        for dp, _, fs in os.walk(rdir):
            for fn in fs:
                t = open(os.path.join(dp, fn), encoding="utf-8", errors="ignore").read()
                if "locomotion-pilots-compact" in t or "south-locomotion-compact" in t:
                    refs.append(os.path.join(dp, fn))
    check("09 no runtime script / scene references the pilot", not refs, refs)
    if args.pixelorama:
        px = os.path.join(REPO, PIXELORAMA_REL)
        tmp = tempfile.mkdtemp(prefix="wb-locopxo-")
        try:
            env = dict(os.environ, APPDATA=os.path.join(tmp, "appdata"))
            os.makedirs(env["APPDATA"])
            src = os.path.join(tmp, "k.pxo")
            shutil.copyfile(os.path.join(ASSET_REL, es["keyframes_pxo"]), src)
            od = os.path.join(tmp, "out-pxo")
            os.makedirs(od)
            n = len(m["keyframes"])
            r = subprocess.run([px, "--headless", "--quit", "--", "--export", "-f", f"1-{n}", "-o", os.path.join(od, "f.png"), src],
                               capture_output=True, text=True, env=env, timeout=240)
            outs = sorted(os.listdir(od))
            okp = r.returncode == 0 and len(outs) == n and all(
                texels(rgba(os.path.join(od, o))) == texels(imgs[k["file"]]) for o, k in zip(outs, m["keyframes"]))
            check("10a Pixelorama 1.2.3 headless: keyframes .pxo export == keyframe PNGs (isolated APPDATA)", okp, f"{len(outs)} frames")
            osrc = os.path.join(tmp, "parts.ora")
            shutil.copyfile(os.path.join(ASSET_REL, es["part_library_ora"]), osrc)
            od2 = os.path.join(tmp, "out-ora")
            os.makedirs(od2)
            r = subprocess.run([px, "--headless", "--quit", "--", "--export", "--split-layers", "-o", os.path.join(od2, "p.png"), osrc],
                               capture_output=True, text=True, env=env, timeout=240)
            outs = sorted(os.listdir(od2))
            got = [texels(rgba(os.path.join(od2, o))) for o in outs]
            # Pixelorama names split layers by layer name; match by content (empty parts export as empty PNGs)
            want = sorted((sorted(p.items()) for p in parts.values()), key=str)
            have = sorted((sorted(t.items()) for t in got), key=str)
            check("10b Pixelorama 1.2.3 headless: .ora --split-layers == part PNGs (by content)", r.returncode == 0 and want == have,
                  f"{len(outs)} layer PNGs for {len(parts)} parts")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    if args.receipt:
        rp = args.receipt if os.path.isabs(args.receipt) else os.path.join(REPO, args.receipt)
        rec = json.load(open(rp, encoding="utf-8"))
        odir = os.path.dirname(rp)
        check("11a receipt flags false", not rec["art_approved"] and not rec["human_reviewed"] and not rec["runtime_integrated"])
        miss = [n for n, o in rec["outputs"].items() if not os.path.exists(os.path.join(odir, n)) or sha(os.path.join(odir, n)) != o["sha256_bytes"]]
        check("11b every captured output PNG exists with its receipt sha256", not miss, miss or f"{len(rec['outputs'])} PNGs")
        badw, bads, badr, n_s, n_r = [], [], [], 0, 0
        for sk, sr in rec["scenes"].items():
            for mode, w in sr["walk"].items():
                if w["planted_sole_row_world_disp_max_px"] or w["planted_sole_x_world_disp_max_px"] or w["planted_boot_texels_changed"]:
                    badw.append((sk, mode))
            for tag, s in sr["stops"].items():
                n_s += 1
                for part in ("walk", "stop"):
                    x = s[part]
                    if x["planted_sole_row_world_disp_max_px"] or x["planted_sole_x_world_disp_max_px"] or x["planted_boot_texels_changed"]:
                        bads.append(tag)
                if s["switch_to_v8_xor"] != 0:
                    bads.append(tag + " switch")
            for tag, r2 in sr["repress"].items():
                n_r += 1
                if not r2["alternation_ok_next_touchdown_is_the_other_boot"]:
                    badr.append(tag)
        check("11c walks 30/60/144: 0 planted-boot world displacement", not badw, badw)
        check("11d stops: 0 planted-boot displacement, 0-pixel switch to v8", not bads, bads or f"{n_s} stops")
        check("11e re-press: next touchdown is the other boot", not badr, badr or f"{n_r} re-press cases")
        gr = glob.glob(os.path.join(odir, os.path.basename(rp).replace("capture-receipt", "preview-gif-receipt")))
        if gr:
            g2 = json.load(open(gr[0], encoding="utf-8"))
            ok = g2["source_capture_receipt_sha256_bytes"] == sha(rp)
            gm = [n for n, h in g2["gifs_sha256_bytes"].items() if not os.path.exists(os.path.join(odir, n)) or sha(os.path.join(odir, n)) != h]
            check("11f GIF receipt: source receipt hash + every GIF hash", ok and not gm, gm or f"{len(g2['gifs_sha256_bytes'])} GIFs")
    fails = [r for r in results if not r[1]]
    print(f"{len(results) - len(fails)}/{len(results)} OK")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
