"""Focused check for the UNAPPROVED / NONRUNTIME female SOUTH RUN motion pilot v03 (m8-w06, test-only, single direction).

Re-measures from the files on disk; never imports the builder.  Started from the v02 check
(tests/protagonist-female-south-locomotion-compact-v02/..._deterministic-check_m8-w05_20261016-200500-6d8d7fe7.py).
  01 source identity: the approved v8 PNG is byte-identical (sha256-bytes lock) and unchanged in git
  02 rebuild into a temp dir is byte-identical to the asset folder (all files)
  03 manifest: LF only, every approval flag false, motion_state is a run (not a walk), display 48 px / 0.5 / nearest,
     part / keyframe / keyframe-shadow / .pxo / .ora hashes
  04 alpha / palette: every character part and keyframe PNG is 80x120 RGBA, binary alpha, colours inside v8's palette;
     every shadow PNG is binary alpha in the single ink colour
  05 an independent re-implementation of the documented v03 compositor rule stacks the PART PNGs into every keyframe
     PNG and keyframe shadow PNG exactly, and into v8 exactly at the neutral state
  06 identity: head texels (manifest head rule) == v8 + bob; torso texels == v8 moved by (sx, bob) where the head or
     a swung arm does not cover them
  07 foot pinning (nominal table): every stance run lasts stance_px, its boot's world row (phase + ground + o) is
     constant and it rolls strike -> v8 -> heelup -> toe; swing lift >= 1 and <= 3; soles inside the cell
  08 display / collision bounds: lowest reachable sprite row and shadow row inside the cell and recorded; the
     runtime MOVE_SPEED is still 140 in both exploration scripts; no runtime script / scene references the pilot
  09 part-library .ora: mimetype first and stored, one stack.xml layer per part, each layer == its part PNG
  10 (--pixelorama) Pixelorama 1.2.3 headless (isolated APPDATA): the keyframes .pxo --split-layers exports equal the
     composed layers (shadow layer included) and the .ora --split-layers exports equal the part PNGs
  11 (--receipt <capture receipt>) the Godot capture receipt: flags false, every listed PNG exists with its sha256,
     planted boots 0 px world displacement on every walk / stop / re-press, 0-pixel switch to v8, no boot raised
     longer than the stop limit after a release, re-press alternation, sprite rows inside the recorded bounds; (with
     the preview receipt next to it) every GIF / MP4 hash matches
  12 (--import-receipt <json>) the isolated-copy Godot import validation printed RUN_V03_IMPORT PASS
Usage (repository root): python -I tests/<this dir>/<this> [--pixelorama] [--receipt <capture receipt>.json]
                         [--import-receipt <import receipt>.json]
"""
import argparse, glob, hashlib, io, json, os, shutil, subprocess, sys, tempfile, zipfile
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ASSET_REL = "game/assets/characters/run-v03-unapproved"
BUILDER_GLOB = "tools/rpg-2-star-ocean-the-second_protagonist-female_south-locomotion-compact-v03-build_m8-w06_20261017-012243-*.py"
V8_REL = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_"
          "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
V8_SHA256 = "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
PIXELORAMA_REL = "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"
W, H = 80, 120
INK = (0x0a, 0x0a, 0x0e)
HTAG = {-1: "m1", 0: "0", 1: "p1"}
STANCE = ("strike", "v8", "heelup", "toe")
STOP_RAISED_LIMIT_MS = 100.0

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("OK   " if ok else "FAIL ") + name + ("" if not detail else "  " + str(detail)[:700]))


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def rgba(path):
    return np.array(Image.open(path).convert("RGBA"))


def texels(a):
    ys, xs = np.nonzero(a[:, :, 3])
    return {(int(x), int(y)): tuple(int(c) for c in a[y, x, :3]) for x, y in zip(xs, ys)}


def head_texel(x, y):
    # the manifest's head rule: rows <= 28, rows 29..33 x <= 40, chin row 34 x 32..37, neck row 35 x 34..35
    return y <= 28 or (y <= 33 and x <= 40) or (y == 34 and 32 <= x <= 37) or (y == 35 and 34 <= x <= 35)


# ---------------------------------------------------------------- independent compositor (from the manifest's rule)
def rdiv(n, d):
    return (2 * n + d) // (2 * d)


def pick(src, n):
    return [src[min(len(src) - 1, (i * len(src)) // n)] for i in range(n)]


def leg_plan(rig, side, b, bt):
    hip, boot_top = rig["hip_row"], rig["boot_top_row"]
    k0, k1 = rig["knee_band_rows"][side]
    T, K, S = list(range(hip, k0)), list(range(k0, k1 + 1)), list(range(k1 + 1, boot_top))
    n = bt - (hip + b)
    full = len(T) + len(K) + len(S)
    if n < full:
        nk = max(5, rdiv(n * len(K), full))
        nt = max(1, rdiv((n - nk) * len(T), len(T) + len(S)))
        ns = n - nk - nt
        if ns < 1:
            nt, ns = nt - (1 - ns), 1
        return pick(T, nt), pick(K, nk), pick(S, ns)
    rest = n - len(K)
    nt = max(1, min(rest - 1, rdiv(rest * len(T), len(T) + len(S))))
    return pick(T, nt), K, pick(S, rest - nt)


def compose(parts, rig, state):
    b, h, sx, csx = state["bob"], state["hdy"], state["sx"], state["csx"]
    hip = rig["hip_row"]

    def sh(role, dx=0):
        return {(x + dx, y + b): c for (x, y), c in parts[role].items()}

    legs = {}
    for side in ("vl", "vr"):
        f = state["feet"][side]
        dy = f["o"] - f["lift"]
        boot = {(x, y + dy): c for (x, y), c in parts[f"boot-{side}-{f['view']}"].items()}
        th, kn, shn = leg_plan(rig, side, b, min(y for (_, y) in boot))
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
    contact = {s: fe[s]["lift"] == 0 and fe[s]["view"] in STANCE for s in ("vl", "vr")}
    if contact["vl"] != contact["vr"]:
        near = "vl" if not contact["vl"] else "vr"
    else:
        near = "vl" if fe["vl"]["o"] > fe["vr"]["o"] else "vr"
    far = "vl" if near == "vr" else "vr"
    R, L = state["arms"]["R"], state["arms"]["L"]
    g = {}
    g.update(sh(f"cape-hdy-{HTAG[h]}", csx))
    g.update(sh(f"arm-vl-{R}-back", sx))
    g.update(sh(f"arm-vr-{L}-back", sx))
    hips = sh("hips")
    g.update(hips)
    g.update(legs[far])
    g.update(legs[near])
    for role in ("coat-skirt", "torso", f"arm-vl-{R}-seam", f"arm-vr-{L}-seam"):
        g.update(sh(role, sx))
    g.update(sh("head"))
    g.update(sh(f"hair-hdy-{HTAG[h]}"))
    g.update(sh(f"arm-vl-{R}-front", sx))
    g.update(sh(f"arm-vr-{L}-front", sx))
    legmask = set(hips) | set(legs[far]) | set(legs[near])
    holes = [(x, y) for y in range(hip + b, H) for x in range(1, W - 1) if (x, y) not in g and
             all(q in g for q in ((x - 1, y), (x + 1, y), (x, y - 1))) and
             any(q in legmask for q in ((x - 1, y), (x + 1, y), (x, y - 1)))]
    for q in holes:
        g[q] = INK
    if sx:
        seams = [(x, y) for y in range(28 + b, 41 + b) for x in range(1, W - 1) if (x, y) not in g and
                 all(q in g for q in ((x - 1, y), (x + 1, y), (x, y - 1)))]
        for q in seams:
            g[q] = INK
    shadow = {}
    for side in ("vl", "vr"):
        f = fe[side]
        shadow.update({(x, y + f["o"]): c for (x, y), c in parts[f"shadow-{side}-l{min(f['lift'], 3)}"].items()})
    return g, shadow


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pixelorama", action="store_true")
    ap.add_argument("--receipt")
    ap.add_argument("--import-receipt")
    args = ap.parse_args()
    os.chdir(REPO)
    gd = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", V8_REL], capture_output=True)
    check("01 source identity: approved v8 PNG sha256-bytes lock + unchanged vs git HEAD",
          sha(V8_REL) == V8_SHA256 and gd.returncode == 0, V8_SHA256[:16])
    builders = glob.glob(BUILDER_GLOB)
    check("02a single builder", len(builders) == 1, builders)
    tmp = tempfile.mkdtemp(prefix="wb-runv03chk-")
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
    flags = ["art_approved", "human_reviewed", "runtime_integrated", "walk_animation_approved", "run_animation_approved",
             "stop_animation_approved", "counts_toward_art_acceptance"]
    check("03b manifest approval flags all false; UNAPPROVED / NONRUNTIME status", not any(m[f] for f in flags) and
          "UNAPPROVED / NONRUNTIME" in m["status"])
    check("03c motion state is a run, not a walk", m["motion_state"].startswith("run") and "NOT a walk" in m["motion_state"])
    d = m["display"]
    check("03d display 48 px / 0.5 / no flip / nearest", d["scale"] == 0.5 and d["logical_height_px"] == 48 and not d["flip_h"]
          and d["filter"] == "nearest")
    entries = m["parts"] + m["keyframes"]
    hok = all(sha(os.path.join(ASSET_REL, e["file"])) == e["sha256"] for e in entries) and all(
        sha(os.path.join(ASSET_REL, k["shadow_file"])) == k["shadow_sha256"] for k in m["keyframes"])
    check("03e part + keyframe + keyframe-shadow PNG hashes", hok, f"{len(m['parts'])} parts + {len(m['keyframes'])} keyframes (+ shadows)")
    es = m["editable_sources"]
    check("03f .pxo / .ora hashes", sha(os.path.join(ASSET_REL, es["keyframes_pxo"])) == es["keyframes_pxo_sha256"] and
          sha(os.path.join(ASSET_REL, es["part_library_ora"])) == es["part_library_ora_sha256"])
    v8 = rgba(V8_REL)
    pal = {tuple(int(c) for c in px[:3]) for px in v8.reshape(-1, 4) if px[3]}
    bad, bad_sh = [], []
    imgs = {}
    for e in entries:
        a = rgba(os.path.join(ASSET_REL, e["file"]))
        imgs[e["file"]] = a
        cols = {tuple(int(c) for c in px[:3]) for px in a.reshape(-1, 4) if px[3]}
        is_shadow = e.get("role", "").startswith("shadow-")
        if a.shape != (H, W, 4) or not set(np.unique(a[:, :, 3])) <= {0, 255}:
            bad.append(e["file"])
        elif is_shadow and cols != {INK}:
            bad_sh.append(e["file"])
        elif not is_shadow and not cols <= pal:
            bad.append(e["file"])
    for k in m["keyframes"]:
        a = rgba(os.path.join(ASSET_REL, k["shadow_file"]))
        imgs[k["shadow_file"]] = a
        cols = {tuple(int(c) for c in px[:3]) for px in a.reshape(-1, 4) if px[3]}
        if a.shape != (H, W, 4) or not set(np.unique(a[:, :, 3])) <= {0, 255} or cols != {INK}:
            bad_sh.append(k["shadow_file"])
    check("04a character PNGs: 80x120 RGBA / binary alpha / inside v8's 32-colour palette", not bad, bad or f"{len(pal)} palette colours")
    check("04b shadow PNGs: binary alpha, single ink colour (opacity only at draw time)", not bad_sh, bad_sh)
    parts = {e["role"]: texels(imgs[e["file"]]) for e in m["parts"]}
    v8t = texels(v8)
    neutral = {"bob": 0, "hdy": 0, "sx": 0, "csx": 0, "arms": {"R": "N", "L": "N"},
               "feet": {s: {"o": 0, "lift": 0, "view": "v8", "kin": 0} for s in ("vl", "vr")}}
    check("05a independent compositor: neutral state == v8", compose(parts, m["rig"], neutral)[0] == v8t)
    mism = []
    for k in m["keyframes"]:
        g, s = compose(parts, m["rig"], k["state"])
        if g != texels(imgs[k["file"]]) or s != texels(imgs[k["shadow_file"]]):
            mism.append(k["key"])
    check("05b independent compositor: parts -> every keyframe PNG and keyframe shadow PNG", not mism, mism or f"{len(m['keyframes'])} keyframes")
    idm, cov = {}, 0
    for k in m["keyframes"]:
        a, st = imgs[k["file"]], k["state"]
        b, sx = st["bob"], st["sx"]
        arm = set()
        for side, layer in (("R", "arm-vl"), ("L", "arm-vr")):
            arm |= {(x + sx, y + b) for (x, y) in parts[f"{layer}-{st['arms'][side]}-front"]}
        n = 0
        for (x, y), c in v8t.items():
            if y > 57 or (y >= 40 and (x <= 27 or x >= 45)) or (23 <= y <= 32 and x <= 24):
                continue
            if head_texel(x, y):
                n += tuple(int(v) for v in a[y + b, x, :3]) != c or a[y + b, x, 3] == 0
                continue
            q = (x + sx, y + b)
            if (sx and head_texel(q[0], y) and (q[0], y) in v8t) or q in arm:
                cov += 1
                continue
            n += tuple(int(v) for v in a[q[1], q[0], :3]) != c or a[q[1], q[0], 3] == 0
        if n:
            idm[k["key"]] = n
    check("06 identity: head == v8 + bob; torso / scarf / coat == v8 + (sx, bob) where not covered", not idm,
          idm or f"{cov} texel-checks skipped under the steady head / a swung arm")
    g = m["gait"]
    table = m["metrics"]["nominal_per_px"]
    runs_ok, runs, rolls = True, {}, set()
    for side in ("vl", "vr"):
        rows, lens, views = [], [], []
        for ph in range(2 * len(table)):
            f = table[ph % len(table)]["feet"][side]
            if f["contact"]:
                rows.append(ph + m["rig"]["ground_rows"][side] + f["o"])
                views.append(f["view"])
            elif rows:
                lens.append(len(rows))
                runs_ok &= max(rows) == min(rows)
                rolls.add(tuple(dict.fromkeys(views)))
                rows, views = [], []
        runs[side] = lens
        runs_ok &= all(n == g["stance_px"] for n in lens[1:])
    swing = [r["feet"][s]["lift"] for r in table for s in ("vl", "vr") if not r["feet"][s]["contact"]]
    swing_ok = all(0 <= r["feet"][s]["sole_row"] < H for r in table for s in ("vl", "vr")) and min(swing) >= 1 and max(swing) <= 3
    check("07 foot pinning (nominal): stance runs of stance_px, constant world row, roll strike->v8->heelup->toe; swing lift 1..3",
          runs_ok and swing_ok and rolls == {STANCE}, {"stance_runs_px": runs, "rolls": sorted(rolls), "swing_lift": [min(swing), max(swing)],
                                                       "stance_ms": g["stance_ms_at_140"], "airborne_share": g["airborne_share_of_cycle"]})
    bounds = m["metrics"]["bounds"]
    bok = bounds["sprite_lowest_row_any_reachable_state"] < H and bounds["shadow_lowest_row"] < H
    speeds = {}
    for p in ("game/scripts/scifi_exploration_area.gd", "game/scripts/survey_annex.gd"):
        t = open(p, encoding="utf-8").read()
        speeds[p] = "const MOVE_SPEED := 140.0" in t
    refs = []
    for rdir in ("game/scripts", "game/scenes"):
        for dp, _, fs in os.walk(rdir):
            for fn in fs:
                t = open(os.path.join(dp, fn), encoding="utf-8", errors="ignore").read()
                if "run-v03-unapproved" in t or "south-run-v03" in t:
                    refs.append(os.path.join(dp, fn))
    check("08 display / collision bounds recorded inside the cell; MOVE_SPEED 140 unchanged; no runtime reference",
          bok and all(speeds.values()) and not refs,
          {"lowest_sprite_row": bounds["sprite_lowest_row_any_reachable_state"],
           "rows_below_v8_ground": bounds["sprite_rows_below_v8_ground"], "shadow_lowest_row": bounds["shadow_lowest_row"],
           "move_speed_140": speeds, "refs": refs})
    z = zipfile.ZipFile(os.path.join(ASSET_REL, es["part_library_ora"]))
    infos = z.infolist()
    ok = infos[0].filename == "mimetype" and infos[0].compress_type == zipfile.ZIP_STORED and z.read("mimetype") == b"image/openraster"
    root = ET.fromstring(z.read("stack.xml"))
    layers = [(l.get("name"), l.get("src")) for l in root.iter("layer")]
    ok &= sorted(n for n, _ in layers) == sorted(parts) and root.get("w") == str(W) and root.get("h") == str(H)
    for n, src in layers:
        ok &= texels(np.array(Image.open(io.BytesIO(z.read(src))).convert("RGBA"))) == parts[n]
    ok &= texels(np.array(Image.open(io.BytesIO(z.read("mergedimage.png"))).convert("RGBA"))) == v8t
    check("09 part-library .ora: structure + every layer == its part PNG; merged == v8", ok, f"{len(layers)} layers")
    if args.pixelorama:
        px = os.path.join(REPO, PIXELORAMA_REL)
        tmp = tempfile.mkdtemp(prefix="wb-runv03pxo-")
        try:
            env = dict(os.environ, APPDATA=os.path.join(tmp, "appdata"))
            os.makedirs(env["APPDATA"])
            src = os.path.join(tmp, "k.pxo")
            shutil.copyfile(os.path.join(ASSET_REL, es["keyframes_pxo"]), src)
            od = os.path.join(tmp, "out-pxo")
            os.makedirs(od)
            n = len(m["keyframes"])
            r = subprocess.run([px, "--headless", "--quit", "--", "--export", "--split-layers", "-f", f"1-{n}", "-o",
                                os.path.join(od, "f.png"), src], capture_output=True, text=True, env=env, timeout=300)
            outs = sorted(os.listdir(od))
            # exported names are "<profile stem>(<layer name>) _<frame>.png" (Pixelorama 1.2.3); per frame, the
            # character layers restacked in the .pxo order must equal the keyframe PNG and the shadow layer its shadow PNG
            by = {}
            for o in outs:
                if "(" in o and ")" in o:
                    layer = o[o.index("(") + 1:o.rindex(")")]
                    frame = int(o.rsplit("_", 1)[1].split(".")[0])
                    by[(frame, layer)] = texels(rgba(os.path.join(od, o)))
            order = es["keyframes_pxo_layers"]
            bad_f = []
            for fi, k in enumerate(m["keyframes"], start=1):
                stack_ = {}
                for layer in order[1:]:
                    stack_.update(by.get((fi, layer), {}))
                if stack_ != texels(imgs[k["file"]]) or by.get((fi, order[0])) != texels(imgs[k["shadow_file"]]):
                    bad_f.append(k["key"])
            ok_n = len(by) == n * len(order)
            check("10a Pixelorama 1.2.3 headless: keyframes .pxo --split-layers: every layer x frame exported; character "
                  "layers restacked == keyframe PNG, shadow layer == shadow PNG (isolated APPDATA)",
                  r.returncode == 0 and ok_n and not bad_f, bad_f or f"{len(by)} layer PNGs = {n} frames x {len(order)} layers"
                  + ("" if ok_n else f"; names e.g. {outs[:2]}"))
            osrc = os.path.join(tmp, "parts.ora")
            shutil.copyfile(os.path.join(ASSET_REL, es["part_library_ora"]), osrc)
            od2 = os.path.join(tmp, "out-ora")
            os.makedirs(od2)
            r = subprocess.run([px, "--headless", "--quit", "--", "--export", "--split-layers", "-o", os.path.join(od2, "p.png"), osrc],
                               capture_output=True, text=True, env=env, timeout=300)
            outs = sorted(os.listdir(od2))
            got = [texels(rgba(os.path.join(od2, o))) for o in outs]
            want = sorted((sorted(p.items()) for p in parts.values()), key=str)
            have = sorted((sorted(t.items()) for t in got), key=str)
            check("10b Pixelorama 1.2.3 headless: .ora --split-layers == part PNGs (by content)", r.returncode == 0 and want == have,
                  f"{len(outs)} layer PNGs for {len(parts)} parts")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    if args.receipt:
        rp = args.receipt if os.path.isabs(args.receipt) else os.path.join(REPO, args.receipt)
        rb = open(rp, "rb").read()
        rec = json.loads(rb)
        odir = os.path.dirname(rp)
        check("11a receipt flags false; not a quick debug run", not rec["art_approved"] and not rec["human_reviewed"]
              and not rec["runtime_integrated"] and not rec["quick_debug_run"])
        miss = [n for n, o in rec["outputs"].items() if not os.path.exists(os.path.join(odir, n)) or sha(os.path.join(odir, n)) != o["sha256_bytes"]]
        check("11b every captured output PNG exists with its receipt sha256", not miss, miss or f"{len(rec['outputs'])} PNGs")

        def planted_bad(x):
            return (x["planted_sole_row_world_disp_max_px"] or x["planted_sole_x_world_disp_max_px_same_view"] or
                    x["planted_boot_texels_changed_same_view"] or x["planted_roll_sole_x_extent_change_max_px"] > 2)
        badw, bads, badr, badb, n_s, n_r, raised_max, lift_max, low_max = [], [], [], [], 0, 0, 0.0, 0, 0
        for sk, sr in rec["scenes"].items():
            for mode, w in sr["walk"].items():
                if planted_bad(w):
                    badw.append((sk, mode))
                low_max = max([low_max] + [t["lowest_cell_row"] for t in w["ticks"]])
            for tag, s in sr["stops"].items():
                n_s += 1
                if planted_bad(s["walk"]) or planted_bad(s["stop"]):
                    bads.append(tag)
                if s["switch_to_v8_xor"] != 0:
                    bads.append(tag + " switch")
                for side, x in s["raised_after_release"].items():
                    raised_max = max(raised_max, x["longest_raised_ms"])
                    lift_max = max(lift_max, x["max_lift_rows"])
                    if x["longest_raised_ms"] > STOP_RAISED_LIMIT_MS:
                        bads.append(f"{tag} {side} raised {x['longest_raised_ms']:.0f} ms")
                low_max = max([low_max] + [t["lowest_cell_row"] for t in s["ticks"]])
            for tag, r2 in sr["repress"].items():
                n_r += 1
                if not r2["alternation_ok_next_touchdown_is_the_other_boot"] or planted_bad(r2["repress_200ms"]):
                    badr.append(tag)
            if low_max > bounds["sprite_lowest_row_any_reachable_state"]:
                badb.append((sk, low_max))
        check("11c runs 30/60/144: planted boot 0 px world displacement (row always; x / texels while the view holds)", not badw, badw)
        check("11d stops: planted boot pinned, 0-pixel switch to v8, no boot raised > %d ms after release" % STOP_RAISED_LIMIT_MS,
              not bads, bads or f"{n_s} stops; longest raised {raised_max:.0f} ms; max lift {lift_max} rows")
        check("11e re-press: next touchdown is the other boot; planted boot pinned", not badr, badr or f"{n_r} re-press cases")
        check("11f captured sprite rows inside the recorded display bounds", not badb, badb or f"lowest captured cell row {low_max}")
        gr = glob.glob(os.path.join(odir, os.path.basename(rp).replace("capture-receipt", "preview-receipt")))
        if gr:
            g2 = json.load(open(gr[0], encoding="utf-8"))
            ok = g2["source_capture_receipt_sha256_bytes"] == hashlib.sha256(rb).hexdigest()
            gm = [n for n, h in g2["files_sha256_bytes"].items() if not os.path.exists(os.path.join(odir, n)) or sha(os.path.join(odir, n)) != h]
            check("11g preview receipt: source receipt hash + every GIF / MP4 hash", ok and not gm, gm or f"{len(g2['files_sha256_bytes'])} files")
    if args.import_receipt:
        ir = json.load(open(args.import_receipt, encoding="utf-8"))
        check("12 isolated-copy Godot import: lossless, no mipmaps, nearest default filter (RUN_V03_IMPORT PASS)",
              ir.get("exit_code") == 0 and any(l.startswith("RUN_V03_IMPORT PASS") for l in ir.get("stdout_lines", [])),
              [l for l in ir.get("stdout_lines", []) if l.startswith("RUN_V03_IMPORT")])
    fails = [r for r in results if not r[1]]
    print(f"{len(results) - len(fails)}/{len(results)} OK")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
