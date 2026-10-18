"""Focused check for the UNAPPROVED / NONRUNTIME female SOUTH RUN motion pilot v07 (m8-w10, test-only, single direction).

v07 is a versioned AMENDMENT of v06: one control correction (the re-press RISE LOCK - a re-planned boot never rises while
the other boot is off the floor), no art, no gait, no stop change.  This check does not copy the v06 check: it RUNS it
(--run-v06-check: the untouched v06 check against the v06 receipts - rebuild byte-identical, compositor, palette,
Pixelorama editability, ...) and adds the v07 checks:
  01 the approved v8 PNG: sha256-bytes lock, unchanged vs git HEAD
  02 v06 immutability: every v06 file (assets, tools, check, QA note, outputs) + the v8 PNG hash to the listing pinned at
     2026-10-18 08:22:39 UTC, before any v07 file was written (258 files)
  03 the v07 amendment manifest: LF only, every approval flag false, pins the v06 manifest / capture tool / builder by
     sha256-text-lf-v1 (and they match on disk), rise_lock true; the v07 asset folder holds only .gdignore + the amendment
  04 the v07 capture tool EXTENDS the v06 tool by file name, pins it by hash, reads the v06 asset folder (no v07 art); no
     runtime script / scene references the v07 pilot
  05 steady gait invariant (independent, from the v06 manifest's per-px table, frame steps of 1..10 px = 28..240 fps): no
     step on which both boots rise or both leave the floor; while both are airborne the boot that lands next never rises
     - the property the rise lock extends to re-planned swings
  06 (--sim-receipt) gait-driver sweep: gates_ok; rise lock ON: 0 frames on which both boots rise and 0 alternation
     failures over every re-press case (14 frame rates x every release frame of one stride x gaps 1..30, plus 600
     mixed-frame-time re-presses); the same sweep with the lock OFF (v06 behaviour) shows the defect (> 0); every stop
     release -> v8 time per frame rate and the 24 jittered stops equal the v06 sim receipt's (stop rules unchanged)
  07 (--receipt) the v07 Godot capture receipt: flags false, full run, rise lock on, sources pinned; 0 rise-fault frames
     in every captured sequence; every fixed-rate re-press keeps alternation and its handoff (re-press frame through the
     next touchdown) within the steady run's per-frame pose change; v06 QA defect case replayed with 0 rise faults
  08 (--receipt) stops unchanged: for every stop sweep tag present in both receipts, the drawn state of every frame from
     the last moving frame to the v8 PNG and the release -> v8 time equal v06's; 30 fps <= 233.3 ms, 60 fps <= 200 ms,
     raised boot <= 100 ms; showreel releases on v8
  09 (--receipt) bounded review package: exactly 4 normal-speed showreels (2 scenes x 30 / 60 fps) and <= 4 worst-case
     clips, every hash matching the preview receipt; <= 4 diagnostic PNG stills, hashes matching the capture receipt
  10 (--run-v06-check) the v06 focused check exits 0 against the v06 receipts (with --pixelorama)
Usage (repository root): python -I tests/<this dir>/<this> [--receipt outputs/<v07 capture receipt>.json]
                         [--sim-receipt outputs/<v07 sim receipt>.json] [--run-v06-check]
"""
import argparse, glob, hashlib, json, os, subprocess, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
V8_REL = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_"
          "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
V8_SHA256 = "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
V06_PATTERNS = ["game/assets/characters/run-v06-unapproved/*", "game/assets/characters/run-v06-unapproved/.gdignore",
                "tools/*south-run-v06*", "tests/protagonist-female-south-run-v06/*", "docs/qa/*south-run-v06_*",
                "outputs/*south-run-v06*", V8_REL]
V06_LISTING_FILES = 258
V06_LISTING_DIGEST = "b7920bbf927a0bb788c03cc650fd8366f928e85d2ea7e189b795515c8d53875f"
V07_ASSET_REL = "game/assets/characters/run-v07-unapproved"
V06_ASSET_REL = "game/assets/characters/run-v06-unapproved"
TOOL_GLOB = "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v07-godot-capture_m8-w10_*.gd"
V06_TOOL = "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-godot-capture_m8-w09_20261017-211600-ff47ce98.gd"
V06_CHECK = ("tests/protagonist-female-south-run-v06/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06_focused-check_"
             "unapproved-m8-w09_20261017-211600-08ee01ad.py")
V06_CAPTURE_RECEIPT = ("outputs/rpg-2-star-ocean-the-second_city-annex_protagonist-female-south-run-v06-capture-receipt-h48_"
                       "unapproved-nonruntime_20261017-213159-3a390f7c.json")
V06_SIM_RECEIPT = ("outputs/rpg-2-star-ocean-the-second_gait-driver_protagonist-female-south-run-v06-sim-timing-receipt_"
                   "unapproved-nonruntime_20261017-213201-0e8fbdc3.json")
V06_IMPORT_RECEIPT = ("outputs/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-import-validation-receipt_"
                      "unapproved-nonruntime_20261017-213311-26392641.json")
FLAGS = ["art_approved", "human_reviewed", "runtime_integrated", "walk_animation_approved", "run_animation_approved",
         "stop_animation_approved", "counts_toward_art_acceptance"]
DEFECT_CASE = "city-bright_repress-30fps-006-gap-01"
STOP_V8_MAX = {30: 700.0 / 3.0, 60: 200.0}
RAISED_MAX_MS = 100.0

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("OK   " if ok else "FAIL ") + name + ("" if not detail else "  " + str(detail)[:700]))


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def sha_lf(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def listing(patterns):
    out = {}
    for pat in patterns:
        for f in sorted(glob.glob(pat)):
            out[f.replace("\\", "/")] = sha(f)
    return len(out), hashlib.sha256(json.dumps(out, sort_keys=True).encode()).hexdigest()


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def hgt(mode_lift):
    mode, lift = mode_lift
    return 0 if mode == "contact" else int(lift)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt")
    ap.add_argument("--sim-receipt")
    ap.add_argument("--run-v06-check", action="store_true")
    args = ap.parse_args()
    os.chdir(REPO)
    # 01
    gd = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", V8_REL], capture_output=True)
    check("01 approved v8 PNG: sha256-bytes lock + unchanged vs git HEAD", sha(V8_REL) == V8_SHA256 and gd.returncode == 0)
    # 02
    n6, d6 = listing(V06_PATTERNS)
    check("02 v06 immutability: every v06 file + the v8 PNG hash to the listing pinned before v07 (2026-10-18 08:22:39 UTC)",
          n6 == V06_LISTING_FILES and d6 == V06_LISTING_DIGEST, f"{n6} files, digest {d6[:16]}")
    # 03
    am_paths = glob.glob(os.path.join(V07_ASSET_REL, "*-restart-amendment-manifest_*.json"))
    raw = open(am_paths[0], "rb").read() if len(am_paths) == 1 else b""
    am = json.loads(raw) if raw else {}
    m6_path = glob.glob(os.path.join(V06_ASSET_REL, "*-manifest_*.json"))[0]
    pins = am.get("amends", {})
    folder = sorted(os.listdir(V07_ASSET_REL))
    check("03 v07 amendment manifest: LF only, flags false, pins v06 manifest / capture tool / builder (match on disk), rise_lock "
          "true; folder = .gdignore + amendment only",
          len(am_paths) == 1 and b"\r" not in raw and not any(am.get(f, True) for f in FLAGS)
          and pins.get("manifest_sha256_text_lf_v1") == sha_lf(m6_path) and pins.get("capture_tool_sha256_text_lf_v1") == sha_lf(V06_TOOL)
          and pins.get("builder_sha256_text_lf_v1") == sha_lf(pins.get("builder", "")) and am["restart_amendment"]["rise_lock"] is True
          and folder == sorted([".gdignore", os.path.basename(am_paths[0])]) and os.path.getsize(os.path.join(V07_ASSET_REL, ".gdignore")) == 0,
          f"{os.path.basename(am_paths[0]) if am_paths else 'missing'}; folder {folder}")
    # 04
    tools = glob.glob(TOOL_GLOB)
    src = open(tools[0], encoding="utf-8").read() if len(tools) == 1 else ""
    first = src.splitlines()[0] if src else ""
    refs = []
    for pat in ("game/scripts/**/*.gd", "game/scenes/**/*.tscn", "game/project.godot"):
        for f in glob.glob(pat, recursive=True):
            t = open(f, encoding="utf-8", errors="replace").read()
            if "run-v07" in t or "south-run-v07" in t:
                refs.append(f)
    check("04 v07 capture tool extends the v06 tool (pinned by hash), reads the v06 art folder; no runtime reference to v07",
          len(tools) == 1 and first == 'extends "%s"' % os.path.basename(V06_TOOL) and sha_lf(V06_TOOL) in src
          and "run-v07-unapproved/" in src and not refs, refs or os.path.basename(tools[0]) if tools else "missing tool")
    # 05 steady gait invariant on the v06 per-px table
    m6 = load(m6_path)
    table = m6["metrics"]["nominal_per_px"]
    n = len(table)
    bad = []
    for k in range(1, 11):
        for p in range(n):
            a, b = table[p], table[(p + k) % n]
            up = sum(1 for s in ("vl", "vr") if hgt(("contact" if b["feet"][s]["contact"] else "air", b["feet"][s]["lift"]))
                     > hgt(("contact" if a["feet"][s]["contact"] else "air", a["feet"][s]["lift"])))
            off = sum(1 for s in ("vl", "vr") if a["feet"][s]["contact"] and not b["feet"][s]["contact"])
            if up == 2 or off == 2:
                bad.append((k, p, "both-rise" if up == 2 else "both-leave"))
    lead_bad = []
    for p in range(n):
        a, b = table[p], table[(p + 1) % n]
        if a["feet"]["vl"]["contact"] or a["feet"]["vr"]["contact"] or b["feet"]["vl"]["contact"] or b["feet"]["vr"]["contact"]:
            continue
        # the boot that lands next: scan forward
        nxt = None
        for q in range(1, n):
            c = table[(p + q) % n]
            for s in ("vl", "vr"):
                if c["feet"][s]["contact"]:
                    nxt = s
                    break
            if nxt:
                break
        if b["feet"][nxt]["lift"] > a["feet"][nxt]["lift"]:
            lead_bad.append((p, nxt))
    check("05 steady gait (v06 per-px table, steps 1..10 px): never both boots rising / leaving the floor; while both are "
          "airborne the boot that lands next never rises", not bad and not lead_bad, (bad[:6], lead_bad[:6]) if bad or lead_bad else f"{n} px x 10 step sizes")
    # 06 sim receipt
    if args.sim_receipt:
        s7 = load(args.sim_receipt)
        s6 = load(V06_SIM_RECEIPT)
        on, off = s7["repress_v07_rise_lock_on"]["totals"], s7["repress_v06_behaviour_rise_lock_off"]["totals"]
        stops_eq = all(s7["fps"][f]["per_stop_v8_ms"] == [e["v8_ms"] for e in s6["fps"][f]["per_stop"]] for f in s6["fps"])
        jit_eq = s7["jitter"]["per_stop_v8_ms"] == [e["v8_ms"] for e in s6["jitter"]["per_stop"]]
        faults_stop = sum(int(s7["fps"][f]["rise_fault_frames_in_walk_and_stop"]) for f in s7["fps"])
        check("06 gait-driver sweep: gates_ok; lock ON 0 both-rise frames / 0 alternation failures over every re-press case; lock OFF "
              "(v06) shows the defect; stop and jitter-stop times == v06 sim receipt",
              s7["gates_ok"] and on["rise_fault_frames"] == 0 and on["alternation_failures"] == 0 and off["rise_fault_frames"] > 0
              and faults_stop == 0 and stops_eq and jit_eq and not s7["art_approved"],
              f"on {on}; off {off}; jitter stops {[round(v, 1) for v in s7['jitter']['release_to_v8_ms']]} ms (v06 equal: {jit_eq})")
    # 07 / 08 / 09 capture receipt
    if args.receipt:
        r = load(args.receipt)
        r6 = load(V06_CAPTURE_RECEIPT)
        src_ok = (r["sources"]["manifest"]["sha256_text_lf_v1"] == sha_lf(m6_path) and
                  r["sources"]["amendment"]["sha256_text_lf_v1"] == sha_lf(am_paths[0]) and
                  r["sources"]["parent_capture_tool"]["sha256_text_lf_v1"] == sha_lf(V06_TOOL) and r["sources"]["v8"] == V8_SHA256)
        check("07a capture receipt: flags false, full run, rise lock on, v06 manifest / amendment / parent tool / v8 pinned",
              not r["art_approved"] and not r["human_reviewed"] and not r["runtime_integrated"] and not r["quick_debug_run"]
              and r["rise_lock"] and src_ok and set(r["scenes"]) == {"city-bright", "annex-dark"})
        n_rep = 0
        bad_alt = []
        bad_hand = []
        recount = []
        for sk, sr in r["scenes"].items():
            for t, e in sr["repress"].items():
                n_rep += 1
                if not e["alternation_ok"]:
                    bad_alt.append(t)
                if not e["handoff_within_steady_run_xor"] or e["handoff_cell_xor_max"] > sr["steady_cell_xor_max_by_fps"][str(e["fps"])]:
                    bad_hand.append((t, e["handoff_cell_xor_max"]))
                # independent recount of both-rise frames on the receipt's compact feet rows
                rows = [x for x in e["feet"] if len(x) > 2]
                for a, b in zip(rows, rows[1:]):
                    ha = [0 if a[2] else hgt((a[3 + i][0], a[3 + i][2])) for i in range(2)]
                    hb = [0 if b[2] else hgt((b[3 + i][0], b[3 + i][2])) for i in range(2)]
                    if hb[0] > ha[0] and hb[1] > ha[1]:
                        recount.append((t, b[0]))
            for t, e in sr["repress_jitter"].items():
                n_rep += 1
                if not e["alternation_ok"]:
                    bad_alt.append(t)
        check("07b 0 rise-fault frames in every captured sequence (walk / stop / re-press / mixed frame times / showreel / reversal); "
              "independent recount on the re-press rows agrees", r["rise_faults_total"] == 0 and not r["rise_faults"] and not recount,
              recount[:6] or f"rise locks applied {r['rise_locks_total']}")
        check("07c every re-press (fixed-rate + mixed-frame-time): next touchdown is the other boot; fixed-rate handoff pose change "
              "<= the steady run's per-frame maximum at that frame rate", not bad_alt and not bad_hand and not r["handoff_over_steady_xor"],
              (bad_alt[:6], bad_hand[:6]) if bad_alt or bad_hand else f"{n_rep} re-press cases")
        d7 = r["scenes"]["city-bright"]["repress"].get(DEFECT_CASE)
        d6 = r6["scenes"]["city-bright"]["repress"].get(DEFECT_CASE)
        v6_rise = []
        if d6:
            tk = d6["ticks"]
            for a, b in zip(tk, tk[1:]):
                ha = [0 if a["modes"][s] == "contact" else a["state"]["feet"][s]["lift"] for s in ("vl", "vr")]
                hb = [0 if b["modes"][s] == "contact" else b["state"]["feet"][s]["lift"] for s in ("vl", "vr")]
                if hb[0] > ha[0] and hb[1] > ha[1]:
                    v6_rise.append(b["tick"])
        check("07d v06 QA defect 5 replayed (city-bright 30 fps, release frame 6, re-press +1): v06 had a both-rise frame, v07 none; "
              "same next touchdown", d7 is not None and d6 is not None and v6_rise and not d7["rise_faults"]
              and d7["next_touchdown_after_repress"] == d6["next_touchdown_after_repress"]
              and abs(d7["next_touchdown_ms_after_repress"] - d6["next_touchdown_ms_after_repress"]) < 1e-6,
              f"v06 both-rise ticks {v6_rise}; v07 per-frame pose change {[x[1] for x in d7['cell_xor_per_frame_200ms']] if d7 else None}")
        # 08 stops unchanged vs v06
        n_cmp = 0
        diff = []
        lim = []
        for sk, sr in r["scenes"].items():
            for t, e in sr["stops"].items():
                fps = e["fps"]
                if fps in STOP_V8_MAX and e["v8_after_ms"] > STOP_V8_MAX[fps] + 1e-3:
                    lim.append((t, e["v8_after_ms"]))
                if max(e["raised_after_release"][s]["longest_raised_ms"] for s in ("vl", "vr")) > RAISED_MAX_MS:
                    lim.append((t, "raised"))
                e6 = r6["scenes"][sk]["stops"].get(t)
                if e6 is None:
                    continue
                n_cmp += 1
                t6 = {x["tick"]: x for x in e6["ticks"]}
                rel = e["release_tick"]
                for row in e["states_release_to_v8"]:
                    x6 = t6.get(row["tick"])
                    if x6 is None or x6["state"] != row["state"] or x6["modes"] != row["modes"] or x6["show_v8"] != row["show_v8"]:
                        diff.append((t, row["tick"]))
                        break
                if abs(e["v8_after_ms"] - e6["v8_after_ms"]) > 1e-6 or rel != e6["release_tick"]:
                    diff.append((t, "timing"))
            for k in ("showreel_60fps", "showreel_30fps"):
                for rl in sr[k]["releases"]:
                    if not rl["interrupted_by_input_before_v8"] and rl["v8_after_ms"] > STOP_V8_MAX[sr[k]["fps"]] + 1e-3:
                        lim.append((k, rl["release_tick"]))
        n_st = sum(len(sr["stops"]) for sr in r["scenes"].values())
        check("08 stops unchanged: every stop tag shared with v06 draws the same state from the last moving frame to the v8 PNG with "
              "the same release -> v8 time; limits 30 fps <= 233.3 ms, 60 fps <= 200 ms, raised <= 100 ms; showreel releases",
              not diff and not lim and n_cmp > 0, (diff[:6], lim[:6]) if diff or lim else f"{n_st} stops, {n_cmp} compared with v06")
        # 09 bounded review package
        out_dir = os.path.dirname(args.receipt)
        stills = {k: v for k, v in r["outputs"].items()}
        miss = [k for k, v in stills.items() if not os.path.exists(os.path.join(out_dir, k)) or sha(os.path.join(out_dir, k)) != v["sha256_bytes"]]
        pr = args.receipt.replace("capture-receipt", "preview-receipt")
        ok_p = os.path.exists(pr)
        pm = []
        reels = clips = 0
        if ok_p:
            p = load(pr)
            ok_p = p["source_capture_receipt_sha256_bytes"] == sha(args.receipt)
            for k, v in p["files_sha256_bytes"].items():
                fp = os.path.join(out_dir, k)
                if not os.path.exists(fp) or sha(fp) != v or not k.endswith(".mp4"):
                    pm.append(k)
                reels += 1 if "-preview-showreel-1x-" in k else 0
                clips += 1 if "-preview-worst-" in k else 0
        stamp = os.path.basename(args.receipt).rsplit("_", 1)[1].rsplit(".", 1)[0]
        all_out = [f for f in glob.glob(os.path.join(out_dir, "*south-run-v07*")) if stamp in f]
        check("09 bounded package: 4 showreels (2 scenes x 60 / 30 fps) + <= 4 worst-case clips (MP4, hashes match), <= 4 diagnostic "
              "PNG stills (hashes match); nothing else with this stamp but the receipts",
              ok_p and not pm and reels == 4 and 1 <= clips <= 4 and len(stills) <= 4 and not miss
              and len(all_out) == len(stills) + reels + clips + 2,
              f"showreels {reels}, clips {clips}, stills {len(stills)}, files with stamp {len(all_out)}" + (f"; missing {miss + pm}" if miss or pm else ""))
    # 10 the v06 check itself
    if args.run_v06_check:
        cp = subprocess.run([sys.executable, "-I", "-B", V06_CHECK, "--pixelorama", "--receipt", V06_CAPTURE_RECEIPT,
                             "--sim-receipt", V06_SIM_RECEIPT, "--import-receipt", V06_IMPORT_RECEIPT], capture_output=True, text=True)
        lines = [ln for ln in cp.stdout.splitlines() if ln.startswith(("OK", "FAIL"))]
        n_ok = sum(1 for ln in lines if ln.startswith("OK"))
        check("10 the untouched v06 focused check (rebuild byte-identical, compositor, palette, Pixelorama .pxo / .ora editability, "
              "v06 receipts) exits 0", cp.returncode == 0, f"{n_ok}/{len(lines)} OK" + ("" if cp.returncode == 0 else " " + cp.stdout[-600:]))
    n_ok = sum(1 for x in results if x[1])
    print(f"\n{n_ok}/{len(results)} OK")
    sys.exit(0 if n_ok == len(results) else 1)


if __name__ == "__main__":
    main()
