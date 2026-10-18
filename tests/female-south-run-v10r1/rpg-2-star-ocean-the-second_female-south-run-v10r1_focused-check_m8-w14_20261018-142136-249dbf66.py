"""Focused check: female SOUTH RUN v10r1, bounded amendment of v10 (UNAPPROVED / NONRUNTIME, m8-w14).

  01 v06 / v07 sources, the v8 PNG and the shared runtime scenes / scripts are unchanged against git HEAD; the v09 and v10
     sources are the pinned files; every v10 asset matches the v10 manifest and every v10 MP4 / PNG matches the v10 reel
     receipt (v10 preserved)
  02 the v10r1 builder rebuilds every v10r1 asset byte-identically (temp dir)
  03 manifest flags false; parent = the v10 manifest (hash); keyframe / shadow sha256 match; v8 palette only; neutral ==
     v8; same cadence as v10 (stride 128, stance 44, 4.375 steps/s, 68.75 % contact) with land +8 / lift-off -36 (v10
     +12 / -32): the leading boot reaches 4 source px less
  04 seams / holes: no transparent texel enclosed on four sides in any keyframe; every keyframe is one 8-connected
     silhouette; every reachable leg state (both sides, bob 0..2) draws a leg + visible boot without an empty row
  05 (--pixelorama) Pixelorama 1.2.3 headless, isolated APPDATA: the keyframes .pxo --split-layers restacks to every
     keyframe PNG and its shadow layer equals the shadow PNG; the new-parts .ora --split-layers equals the part PNGs
  06 (--sim-receipt) state-level sweep, every gate explicit: steady == per-px and cadence 4.0..4.5 steps/s at 30 / 60 /
     144 fps; release -> v8 <= 250 ms at 30 and at 60 fps; EVERY boot down <= 100 ms after release at 30 fps, at 60 fps,
     at every other constant rate >= 30 fps, and in every mixed-frame-time stop (24 existing seed-6061 cases + 600 more;
     0 stops over); mixed release -> v8 <= 300 ms; 0 rise faults, 0 alternation failures.  24 fps is printed, not gated
  07 (--receipt) capture receipt: art v10r1, full sweep, 0 rise faults, steady ticks checked, planted row 0 px, every stop
     and uninterrupted reel release <= 250 ms, re-press alternation
  08 (--reel-receipt) the two 1x MP4s and the critical-frame PNGs exist with their recorded sha256; PNGs are 1280x720

Usage (repository root): python -I -B tests/female-south-run-v10/<this> [--pixelorama] [--sim-receipt J] [--receipt J]
                          [--reel-receipt J]
"""
import argparse, hashlib, importlib.util, json, os, shutil, subprocess, sys, tempfile

import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ASSET = "game/assets/characters/run-v10r1-unapproved"
V10_ASSET = "game/assets/characters/run-v10-unapproved"
V09_ASSET = "game/assets/characters/run-v09-unapproved"
BUILDER = "tools/rpg-2-star-ocean-the-second_female-south-run-v10r1_reach-landing-amendment-build_m8-w14_20261018-142136-249dbf66.py"
V10_PINS = {"tools/rpg-2-star-ocean-the-second_female-south-run-v10_authored-gait-pushoff-build_m8-w13_20261018-143213-ed496e32.py":
            "1516f7f2ca8fa36ab5c354b625f1b2a5b41e0a1241bc3e995bc5d73126e8b859",
            "tools/rpg-2-star-ocean-the-second_female-south-run-v10-godot-capture_m8-w13_20261018-143213-ed496e32.gd":
            "52ff5ffdf35c8572ef5e971ac59138dda8f65911ce63558972103b9bf1c68101",
            "tools/rpg-2-star-ocean-the-second_female-south-run-v10-showreel-mp4-and-critical-frames_m8-w13_20261018-143213-ed496e32.py":
            "09981eff40927d41d3d3d3497486b29d226280a352456fd437906208e80c6ed3"}
V10_REEL_RECEIPT = "outputs/rpg-2-star-ocean-the-second_city-annex_female-south-run-v10-showreel-and-critical-frames-receipt_unapproved_20261018-143213-6bcf95ec.json"
V09_GD = ("tools/rpg-2-star-ocean-the-second_female-south-run-v09-godot-capture_m8-w12_20261018-133700-4d620536.gd",
          "9839568e7e0c1e76c26053b95de940f0eaece6ba79d7c150edbf1fae48e24189")
PIXELORAMA = os.path.join(REPO, "..", "tooling", "pixelorama-1-2-3", "Pixelorama-Windows-64bit", "Pixelorama.exe")
V8 = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-"
      "cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
UNCHANGED = ["game/assets/characters/run-v06-unapproved", "game/assets/characters/run-v07-unapproved",
             "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py",
             "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-godot-capture_m8-w09_20261017-211600-ff47ce98.gd",
             "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v07-godot-capture_m8-w10_20261018-082500-8770ac39.gd",
             V8, "game/scenes/scifi_exploration_area.tscn", "game/scenes/survey_annex.tscn",
             "game/scripts/scifi_exploration_area.gd", "game/scripts/survey_annex.gd"]
LIMIT, LIMIT_MIXED, RAISED = 250.0, 300.0, 100.0
results = []


def _fs(p):
    p = os.path.abspath(p)
    return "\\\\?\\" + p if os.name == "nt" and len(p) > 247 and not p.startswith("\\\\?\\") else p


def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(("OK   " if ok else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))


def rgba(path):
    return np.array(Image.open(_fs(path)).convert("RGBA"))


def texels(a):
    ys, xs = np.nonzero(a[..., 3])
    return {(int(x), int(y)): tuple(int(v) for v in a[y, x, :3]) for y, x in zip(ys, xs)}


def sha(path):
    with open(_fs(path), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def sha_lf(path):
    with open(_fs(path), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def load(path):
    with open(_fs(path), encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pixelorama", action="store_true")
    ap.add_argument("--sim-receipt")
    ap.add_argument("--receipt")
    ap.add_argument("--reel-receipt")
    a = ap.parse_args()
    os.chdir(REPO)
    adir = os.path.join(REPO, ASSET)
    m = load(os.path.join(adir, [f for f in os.listdir(_fs(adir)) if "_gait-pose-manifest_" in f][0]))
    # 01
    r = subprocess.run(["git", "diff", "--quiet", "HEAD", "--"] + UNCHANGED, capture_output=True)
    st = subprocess.run(["git", "status", "--porcelain", "--"] + UNCHANGED, capture_output=True, text=True).stdout.strip()
    bo = m["based_on"]
    v10dir = os.path.join(REPO, V10_ASSET)
    m10 = load(os.path.join(REPO, m["parent"]["v10_manifest"]))
    m9 = load(os.path.join(REPO, bo["v09_manifest"]))
    v9dir = os.path.join(REPO, V09_ASSET)
    v9ok = sha_lf(os.path.join(REPO, bo["v09_builder"])) == bo["v09_builder_sha256_text_lf_v1"] \
        and sha_lf(os.path.join(REPO, bo["v09_manifest"])) == bo["v09_manifest_sha256_text_lf_v1"] \
        and sha_lf(os.path.join(REPO, V09_GD[0])) == V09_GD[1] \
        and all(sha(os.path.join(v9dir, e["file"])) == e["sha256"] for e in m9["parts_new"]) \
        and all(sha(os.path.join(v9dir, e["file"])) == e["sha256"] and sha(os.path.join(v9dir, e["shadow_file"])) == e["shadow_sha256"]
                for e in m9["keyframes"])
    v10ok = all(sha_lf(os.path.join(REPO, p)) == h for p, h in V10_PINS.items()) \
        and sha_lf(os.path.join(REPO, m["parent"]["v10_manifest"])) == m["parent"]["v10_manifest_sha256_text_lf_v1"] \
        and all(sha(os.path.join(v10dir, e["file"])) == e["sha256"] for e in m10["parts_new"]) \
        and all(sha(os.path.join(v10dir, e["file"])) == e["sha256"] and sha(os.path.join(v10dir, e["shadow_file"])) == e["shadow_sha256"]
                for e in m10["keyframes"]) \
        and sha(os.path.join(v10dir, m10["editable_sources"]["keyframes_pxo"])) == m10["editable_sources"]["keyframes_pxo_sha256"]
    rr10 = load(os.path.join(REPO, V10_REEL_RECEIPT))
    v10ev = all(sha(os.path.join(REPO, "outputs", n)) == e["sha256_bytes"] for n, e in list(rr10["mp4"].items()) + list(rr10["critical_frames"].items()))
    check("01 v06 / v07 sources, v8, shared scenes / scripts unchanged vs HEAD; v09 + v10 sources pinned; v10 assets + evidence preserved",
          r.returncode == 0 and st == "" and v9ok and v10ok and v10ev, st[:200] or f"v09 {v9ok} v10 {v10ok} v10 evidence {v10ev}")
    # 02
    tmp = tempfile.mkdtemp(prefix="wb-v10r1chk-")
    try:
        rb = subprocess.run([sys.executable, "-I", "-B", BUILDER, "--out-dir", tmp], capture_output=True, text=True)
        have = sorted(os.listdir(_fs(adir)))
        got = sorted(os.listdir(tmp))
        same = rb.returncode == 0 and have == got and all(sha(os.path.join(adir, f)) == sha(os.path.join(tmp, f)) for f in got)
        check("02 builder rebuild byte-identical", same, f"{len(got)} files" if same else (rb.stderr[-300:] or str(set(have) ^ set(got))))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # 03
    flags = ["art_approved", "human_reviewed", "runtime_integrated", "walk_animation_approved", "run_animation_approved",
             "stop_animation_approved", "counts_toward_art_acceptance"]
    bad = [f for f in flags if m.get(f) is not False]
    hashes = all(sha(os.path.join(v10dir, e["file"])) == e["sha256"] for e in m["parts_new"]) and all(
        sha(os.path.join(adir, e["file"])) == e["sha256"] and sha(os.path.join(adir, e["shadow_file"])) == e["shadow_sha256"]
        for e in m["keyframes"])
    palette = set(texels(rgba(V8)).values())
    off = [e["file"][-40:] for e in m["keyframes"] if not set(texels(rgba(os.path.join(adir, e["file"]))).values()) <= palette]
    spec = importlib.util.spec_from_file_location("b10r1", os.path.join(REPO, BUILDER))
    r1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r1)
    b10 = r1.b10                       # the v10 module with the r1 gait applied
    v8g, parts, _, _ = b10.build_parts10()
    neutral = b10.b6.stack(b10.compose10(parts, b10.b6.NEUTRAL)[0])
    g = m["gait"]
    g10 = m10["gait"]
    cad = g["stride_px"] == 128 == g10["stride_px"] and g["stance_px"] == 44 == g10["stance_px"] and g["steps_per_s"] == g10["steps_per_s"] == 4.375 \
        and abs(g["ground_contact_share_of_cycle"] - 0.6875) < 1e-9 and g["land_offset"] == 8 and g["liftoff_offset"] == -36 \
        and g10["land_offset"] == 12 and g10["liftoff_offset"] == -32 and max(k[1] for k in g["swing_keys"]) == 8
    check("03 flags false, parent v10 hash, hashes, v8 palette only, neutral == v8, same cadence as v10, land +8 / lift-off -36",
          not bad and hashes and not off and neutral == v8g and cad,
          f"flags {bad} hashes {hashes} off-palette {off} steps/s {g['steps_per_s']} land {g['land_offset']} lift-off {g['liftoff_offset']}")
    # 04
    holes, comps, gaps = [], [], []
    for e in m["keyframes"]:
        al = rgba(os.path.join(adir, e["file"]))[..., 3] > 0
        H, W = al.shape
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                if not al[y, x] and al[y, x - 1] and al[y, x + 1] and al[y - 1, x] and al[y + 1, x]:
                    holes.append((e["key"], x, y))
        seen = np.zeros_like(al)
        n = 0
        for y0, x0 in zip(*np.nonzero(al)):
            if seen[y0, x0]:
                continue
            n += 1
            stack = [(y0, x0)]
            seen[y0, x0] = True
            while stack:
                y, x = stack.pop()
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < H and 0 <= xx < W and al[yy, xx] and not seen[yy, xx]:
                            seen[yy, xx] = True
                            stack.append((yy, xx))
        if n != 1:
            comps.append((e["key"], n))
    n_states = 0
    for (o, lift, view, kin) in sorted(b10.reachable_feet(), key=str):
        for side in ("vl", "vr"):
            for bob in (0, 1, 2):
                full, boot, _, info = b10.compose_leg10(parts, side, bob, {"o": o, "lift": lift, "view": view, "kin": kin})
                n_states += 1
                rows = {y for (_, y) in full}
                if any(y not in rows for y in range(min(rows), max(rows) + 1)):
                    gaps.append((side, bob, view, o, lift, info["mode"]))
    check("04 no enclosed holes, one 8-connected silhouette per keyframe, no empty row in any reachable leg (leg + visible boot)",
          not holes and not comps and not gaps, f"{n_states} leg states; holes {holes[:4]} components {comps} gaps {len(gaps)} {gaps[:4]}")
    # 05
    if a.pixelorama:
        tmp = tempfile.mkdtemp(prefix="wb-v10r1pxo-")
        try:
            env = dict(os.environ, APPDATA=os.path.join(tmp, "appdata"))
            os.makedirs(env["APPDATA"])
            es = m["editable_sources"]
            src = os.path.join(tmp, "k.pxo")
            shutil.copyfile(_fs(os.path.join(adir, es["keyframes_pxo"])), src)
            od = os.path.join(tmp, "out-pxo")
            os.makedirs(od)
            n = len(m["keyframes"])
            r = subprocess.run([PIXELORAMA, "--headless", "--quit", "--", "--export", "--split-layers", "-f", f"1-{n}", "-o",
                                os.path.join(od, "f.png"), src], capture_output=True, text=True, env=env, timeout=300)
            by = {}
            for o in sorted(os.listdir(od)):
                if "(" in o and ")" in o:
                    by[(int(o.rsplit("_", 1)[1].split(".")[0]), o[o.index("(") + 1:o.rindex(")")])] = texels(rgba(os.path.join(od, o)))
            order = es["keyframes_pxo_layers"]
            badf = []
            for fi, k in enumerate(m["keyframes"], start=1):
                stk = {}
                for layer in order[1:]:
                    stk.update(by.get((fi, layer), {}))
                if stk != texels(rgba(os.path.join(adir, k["file"]))) or by.get((fi, order[0])) != texels(rgba(os.path.join(adir, k["shadow_file"]))):
                    badf.append(k["key"])
            check("05a Pixelorama 1.2.3 headless .pxo --split-layers restacks to every keyframe + shadow",
                  r.returncode == 0 and len(by) == n * len(order) and not badf, f"{len(by)} layer PNGs for {n} frames x {len(order)} layers; bad {badf}")
            osrc = os.path.join(tmp, "p.ora")
            shutil.copyfile(_fs(os.path.join(REPO, es["new_parts_ora"])), osrc)
            od2 = os.path.join(tmp, "out-ora")
            os.makedirs(od2)
            r = subprocess.run([PIXELORAMA, "--headless", "--quit", "--", "--export", "--split-layers", "-o", os.path.join(od2, "p.png"), osrc],
                               capture_output=True, text=True, env=env, timeout=300)
            got = sorted((sorted(texels(rgba(os.path.join(od2, o))).items()) for o in os.listdir(od2)), key=str)
            want = sorted((sorted(texels(rgba(os.path.join(v10dir, e["file"]))).items()) for e in m["parts_new"]), key=str)
            check("05b Pixelorama 1.2.3 headless .ora (v10 push-boot parts, used unchanged) --split-layers == part PNGs", r.returncode == 0 and got == want,
                  f"{len(got)} layers for {len(want)} parts")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    # 06
    if a.sim_receipt:
        s = load(a.sim_receipt)
        st_ = s["stops"]
        steady_ok = all(int(s["steady"][f]["state_mismatches_vs_per_px"]) == 0 and int(s["steady"][f]["ticks_checked"]) > 0
                        and 4.0 <= float(s["steady"][f]["measured_steps_per_s"]) <= 4.5 for f in ("30", "60", "144"))
        check("06a sim: steady state == per-px table, measured cadence 4.0..4.5 steps/s (30 / 60 / 144 fps)", steady_ok,
              [round(s["steady"][f]["measured_steps_per_s"], 3) for f in ("30", "60", "144")])
        for fps in ("30", "60"):
            row = st_[fps]
            check(f"06b sim {fps} fps: every phase release -> v8 <= 250 ms and every boot down <= 100 ms",
                  float(row["release_to_v8_ms"][1]) <= LIMIT + 1e-3 and float(row["raised_max_ms"]) <= RAISED + 1e-3
                  and int(row["rise_faults"]) == 0 and int(row["errors"]) == 0,
                  f"v8 {row['release_to_v8_ms']} boot down max {row['raised_max_ms']}")
        others = {k: v for k, v in st_.items() if k.isdigit() and int(k) >= 30 and k not in ("30", "60")}
        check("06c sim every other constant rate >= 30 fps: every boot down <= 100 ms, 0 rise faults",
              all(float(v["raised_max_ms"]) <= RAISED + 1e-3 and int(v["rise_faults"]) == 0 and int(v["errors"]) == 0 for v in others.values()),
              {k: round(v["raised_max_ms"], 1) for k, v in others.items()})
        for key in ("mixed_existing_seed_6061", "mixed_extra_seed_8081_choice", "mixed_extra_seed_8082_uniform"):
            mx = st_[key]
            check(f"06d sim mixed frame times {key}: 0 stops with a boot raised > 100 ms, release -> v8 <= 300 ms",
                  int(mx["stops_raised_over_100ms"]) == 0 and float(mx["raised_max_ms"]) <= RAISED + 1e-3
                  and float(mx["release_to_v8_ms"][1]) <= LIMIT_MIXED + 1e-3 and int(mx["errors"]) == 0 and int(mx["rise_faults"]) == 0,
                  f"{mx['trials']} stops, boot down max {round(mx['raised_max_ms'], 1)}, v8 {mx['release_to_v8_ms']}")
        t = s["repress"]["totals"]
        check("06e sim re-press: 0 alternation failures, 0 both-rise frames", int(t["rise_fault_frames"]) == 0 and int(t["alternation_failures"]) == 0, t)
        r24 = st_["24"]
        print(f"INFO 24 fps (informative, not gated): release -> v8 {r24['release_to_v8_ms']} ms, boot down max {r24['raised_max_ms']} ms")
    # 07
    if a.receipt:
        c = load(a.receipt)
        ok = c["art"] == "v10r1" and int(c["rise_faults_total"]) == 0 and int(c["steady_state_ticks_checked"]) > 0 and not c.get("reels_only")
        detail = []
        for sk, sc in c["scenes"].items():
            for mode, w in sc.get("walk", {}).items():
                ok = ok and int(w["planted_row_disp_max"]) == 0 and int(w["planted_x_disp_max_same_view"]) == 0 \
                    and int(w["planted_boot_texels_changed_same_view"]) == 0
            for tag, sv in sc.get("stops", {}).items():
                if float(sv["v8_after_ms"]) > LIMIT + 1e-3:
                    ok = False
                    detail.append(tag)
            for rl in sc["showreel"]["releases"]:
                if not rl["interrupted_by_input_before_v8"]:
                    ok = ok and float(rl["v8_after_ms"]) <= LIMIT + 1e-3
            for tag, rp in sc.get("repress", {}).items():
                ok = ok and bool(rp["alternation_ok"]) and not rp["rise_faults"] and rp["next_touchdown_after_repress"] != ""
            ok = ok and len(sc.get("stops", {})) > 0 and len(sc.get("repress", {})) > 0 and len(sc.get("reversal", {})) > 0
        check("07 v10r1 capture receipt: 0 rise faults, planted 0 px, stops / reel releases <= 250 ms, re-press alternation", ok, detail[:4])
    # 08
    if a.reel_receipt:
        rr = load(a.reel_receipt)
        od = os.path.dirname(os.path.abspath(a.reel_receipt))
        ok = len(rr["mp4"]) == 2 and all(os.path.exists(_fs(os.path.join(od, n))) and sha(os.path.join(od, n)) == e["sha256_bytes"]
                                         for n, e in rr["mp4"].items())
        ok = ok and len(rr["critical_frames"]) >= 10 and all(
            os.path.exists(_fs(os.path.join(od, n))) and sha(os.path.join(od, n)) == e["sha256_bytes"]
            and Image.open(_fs(os.path.join(od, n))).size == (1280, 720) for n, e in rr["critical_frames"].items())
        check("08 1x MP4s (2) and separate critical-frame PNGs (1280x720) present with recorded sha256", ok,
              f"{len(rr['mp4'])} MP4, {len(rr['critical_frames'])} PNG")
    n_ok = sum(ok for _, ok in results)
    print(f"{n_ok}/{len(results)} OK")
    sys.exit(0 if n_ok == len(results) else 1)


if __name__ == "__main__":
    main()
