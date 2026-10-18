#!/usr/bin/env python3
"""Washington Capitol west v13 opt-in flag: reproducible check of the committed tree (UNAPPROVED art, off by default).

Why this replaces the published flag checker (tools/...v13-flag-integration-check...63201688.py) as the gate
    F01/F02 there compared the worktree's uncommitted game/ delta with HEAD, so on a clean committed checkout they
    fail by design. F13 compared real-time moving frames with frames captured in an earlier real-time run: the
    hero moves MOVE_SPEED * delta per frame and delta came from the wall clock, so where a walk stopped varied by a
    frame step between runs (at 14:12 EDT the unchanged v12r2 path stopped zh traversal-end at scroll 12 against the
    committed 14). That checker and its historical 21/21 report are kept as they are.

What this check does
    Static, from git only (works on a fresh clean checkout; needs the Godot tooling path for the runtime part):
      D01 the WDC commits since the pinned predecessor 6406bb8 change in game/ only the 7 v13 candidate files and
          the 3 flag files; D02 HEAD's 3 flag files equal their pins and the scene differs from 6406bb8 by exactly
          the one script-path line; D03 the selector chain and its inputs are byte-identical to 6406bb8; D04 the
          test tools live in tools/ and nothing in game/ refers to them; D05 the temp tree equals HEAD.
    Runtime, in an isolated temp tree exported from HEAD (own APPDATA):
      The flag-path harness runs with Godot `--fixed-fps 60`: every frame gets delta = 1/60 and real-time sync is
      off, so the same scripted inputs give the same deltas in the base (v12r2 flag) and the candidate (v13 flag).
      Each mode runs twice to prove repeatability (D08). Moving shots are then compared base vs candidate under
      identical input and deltas (D14); the declared bound stays one scroll row / 3 px, and actual values are
      reported. Fixed-position shots keep their exact gate against the committed frames (D13), and both kinds of
      shot must differ from v12r2 only inside the projected v13 art change (D14/D15).
      The accepted-rooms replay runs with the v13 flag present (D20).

Usage (runtime Python, isolated):  python -I -B <this file> check [--write-report]
"""
import collections
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("wdc_v13_flag_check", os.path.join(
    HERE, "rpg-2-star-ocean-the-second_wdc-capitol-west_v13-flag-integration-check_unapproved-v13_20261018-135539-63201688.py"))
fc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fc)
v13 = fc.v13
rp, _fs, read_bytes, write_bytes, sha, sha_text, git, run_cmd = (
    fc.rp, fc._fs, fc.read_bytes, fc.write_bytes, fc.sha, fc.sha_text, fc.git, fc.run_cmd)
REPO, SLUG, AREA, GODOT = fc.REPO, fc.SLUG, fc.AREA, fc.GODOT

STAMP, RUN_ID = "20261018-141558", "22d034ba"
RUN = f"wdc-cw-v13flagdet_{STAMP}-{RUN_ID}"
OUT_REL = f"outputs/{RUN}"
TOOL_REL = "tools/" + os.path.basename(os.path.abspath(__file__))
QA_REL = f"docs/qa/{SLUG}_{AREA}_v13-flag-deterministic-check_qa-note_unapproved-v13_{STAMP}-{RUN_ID}.md"
PREDECESSOR = "6406bb86c60b6fd7978414706afa07a5229105fa"
FIXED_FPS = "60"
TREE = os.path.join(os.environ.get("LOCALAPPDATA", os.environ.get("TEMP", ".")), "Temp", "wr13d-" + RUN_ID)
FLAG_FILES = [fc.SCENE_REL, fc.SELECTOR_REL, fc.V13_IMPORT_REL]
CAND_FILES = sorted(f"{v13.CAND_REL}/{n}" for n in (
    v13.fname(p, e) for p, e in (("scene-32layer", "pxo"), ("scene-32layer", "ora"), ("scene-flat-640x360", "png"),
                                 ("scene-palette", "gpl"), ("rt-base", "png"), ("rt-override-contract", "json"),
                                 ("scene-manifest", "json"))))
FLAG_MANIFEST_REL = f"{fc.OUT_REL}/" + fc.out_name("flag-integration-manifest", "json")
TEST_TOOLS = [fc.HARNESS_REL, v13.HARNESS_REL, v13.REPLAY_BASE_REL, fc.TOOL_REL, TOOL_REL]
CHAIN = ["game/scripts/scifi_exploration_area.gd", "game/scripts/survey_annex.gd",
         f"game/scripts/{SLUG}_{AREA}_exploration-opt-in-selector_unapproved-v12_20261017-235608-66d00477.gd",
         f"game/scripts/{SLUG}_{AREA}_exploration-opt-in-selector_unapproved-v12r1_20261018-034933-23596520.gd",
         fc.R2_SELECTOR_REL]
MODES = {"v13flag": "--wdc-capitol-west-v13", "v12r2flag": "--wdc-capitol-west-v12r2"}
REPEATS = ("a", "b")
DETERMINISTIC, VARIABLE, KEYS = fc.DETERMINISTIC, fc.VARIABLE, fc.KEYS
OLD_SUFFIX = fc.OLD_SUFFIX
TAGS = {"v13flag": "flag-v13", "v12r2flag": "flag-v12r2"}


def out_name(purpose, ext):
    return f"{SLUG}_{AREA}_{purpose}_unapproved-v13_{STAMP}-{RUN_ID}.{ext}"


def portable(text):
    for real, token in ((TREE, "<TEMP_TREE>"), (REPO, "<REPO>")):
        for v in (real, real.replace("\\", "/"), real.replace("\\", "\\\\")):
            text = text.replace(v, token)
    return text


def lines_at(rev, rel):
    return git("show", f"{rev}:{rel}").replace("\r\n", "\n").split("\n")


def blob(rev, rel):
    return git("rev-parse", f"{rev}:{rel}").strip()


# ---------------------------------------------------------------------------------------------- static (git only)
def static_gates():
    g, notes = collections.OrderedDict(), collections.OrderedDict()
    head = git("rev-parse", "HEAD").strip()
    notes["head"], notes["predecessor"] = head, PREDECESSOR
    wdc_paths = FLAG_FILES + CAND_FILES
    commits = git("log", "--no-merges", "--format=%H", f"{PREDECESSOR}..HEAD", "--", *wdc_paths).split()
    touched = {c: sorted(git("-c", "core.quotepath=off", "show", "--name-only", "--format=", c, "--", "game").split())
               for c in commits}
    notes["wdc_commits_game_changes"] = {c[:12]: t for c, t in touched.items()}
    union = sorted({p for t in touched.values() for p in t})
    g["D01_wdc_commits_change_only_the_v13_candidate_and_3_flag_files_in_game"] = \
        union == sorted(wdc_paths) and all(set(t) <= set(wdc_paths) for t in touched.values())
    since = sorted(git("-c", "core.quotepath=off", "diff", "--name-only", PREDECESSOR, "HEAD", "--", "game").split())
    others = [p for p in since if p not in wdc_paths]
    other_commits = git("log", "--no-merges", "--format=%H", f"{PREDECESSOR}..HEAD", "--", *others).split() if others else []
    notes["other_game_changes_since_predecessor"] = {"count": len(others), "commits": [c[:12] for c in other_commits],
                                                     "includes": [p for p in others if p.endswith(".gd")]}
    notes["other_game_changes_not_from_wdc_commits"] = not (set(other_commits) & set(commits))
    pins = json.loads(read_bytes(rp(FLAG_MANIFEST_REL)))["sources_sha256_text_lf_v1"]
    head_ok = all(sha_text(git("show", f"HEAD:{rel}", binary=True)) == pins[rel] for rel in FLAG_FILES)
    old_scene, new_scene = lines_at(PREDECESSOR, fc.SCENE_REL), lines_at("HEAD", fc.SCENE_REL)
    diff = [i for i, (a, b) in enumerate(zip(old_scene, new_scene)) if a != b]
    one_line = len(old_scene) == len(new_scene) and len(diff) == 1 and \
        new_scene[diff[0]] == old_scene[diff[0]].replace(fc.res(fc.R2_SELECTOR_REL), fc.res(fc.SELECTOR_REL)) and \
        fc.res(fc.R2_SELECTOR_REL) in old_scene[diff[0]]
    selector_head = git("show", f"HEAD:{fc.SELECTOR_REL}")
    g["D02_head_flag_files_equal_pins_and_scene_is_one_line_vs_predecessor"] = head_ok and one_line and \
        selector_head.startswith(f'extends "{fc.res(fc.R2_SELECTOR_REL)}"') and \
        sha(git("show", f"HEAD:{fc.V13_BASE_REL}", binary=True)) == json.loads(read_bytes(rp(
            f"{v13.CAND_REL}/" + v13.fname("scene-manifest", "json"))))["files_sha256_bytes"][v13.fname("rt-base", "png")]
    v12_files = git("-c", "core.quotepath=off", "ls-tree", "-r", "--name-only", PREDECESSOR, v13.V12_CAND_REL).split()
    chain = CHAIN + v12_files + [v13.REPLAY_BASE_REL]
    changed = [p for p in chain if blob(PREDECESSOR, p) != blob("HEAD", p)]
    # the v13 test harness did not exist at the predecessor (added by the v13 candidate commit): it must be
    # unchanged since the one commit that added it
    added = git("log", "--format=%H", f"{PREDECESSOR}..HEAD", "--", v13.HARNESS_REL).split()
    harness_ok = len(added) == 1 and blob(added[0], v13.HARNESS_REL) == blob("HEAD", v13.HARNESS_REL)
    notes["chain_files_checked"] = len(chain)
    g["D03_selector_chain_and_v12_inputs_identical_to_predecessor"] = not changed and len(v12_files) > 0 and harness_ok
    notes["chain_changed"] = changed
    notes["v13_harness_commits_since_predecessor"] = [c[:12] for c in added]
    # game/ may name tools in comments or manifests; it must never load one (no res://../tools reference)
    loads = git("grep", "-l", "-F", "res://../tools", "HEAD", "--", "game").split()
    mentions = git("grep", "-l", "-E", "v13-flag-path-harness|v13-flag-integration-check|v13-flag-deterministic-check|"
                   "v13-texture-override-harness", "HEAD", "--", "game").split()
    notes["game_files_mentioning_test_tools_by_name"] = [m.split(":", 1)[1] for m in mentions]
    g["D04_test_tools_outside_game_and_never_loaded_by_game"] = \
        all(t.startswith("tools/") for t in TEST_TOOLS) and not loads and \
        all(os.path.exists(_fs(rp(t))) for t in TEST_TOOLS)
    return g, notes


# ---------------------------------------------------------------------------------------------- runtime
def export_tree():
    if os.path.exists(_fs(TREE)):
        shutil.rmtree(_fs(TREE))
    os.makedirs(_fs(TREE))
    proc = subprocess.Popen(["git", "-C", REPO, "-c", "core.autocrlf=false", "archive", "--format=tar", "HEAD", "game",
                             v13.REPLAY_BASE_REL, v13.HARNESS_REL, fc.HARNESS_REL], stdout=subprocess.PIPE)
    with tarfile.open(fileobj=proc.stdout, mode="r|") as tar:
        for member in tar:
            target = os.path.join(TREE, *member.name.split("/"))
            if member.isdir():
                os.makedirs(_fs(target), exist_ok=True)
            elif member.isfile():
                os.makedirs(_fs(os.path.dirname(target)), exist_ok=True)
                with open(_fs(target), "wb") as f:
                    f.write(tar.extractfile(member).read())
    proc.wait()
    import hashlib
    total, bad = 0, []
    for line in git("-c", "core.quotepath=off", "ls-tree", "-r", "HEAD", "game").splitlines():
        meta, path = line.split("\t", 1)
        mode, kind, b = meta.split()
        if kind != "blob" or mode == "120000":
            continue
        total += 1
        data = read_bytes(os.path.join(TREE, *path.split("/")))
        if hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest() != b:
            bad.append(path)
    return {"blobs_checked": total, "blob_mismatches": bad}


def pixels(path):
    return np.array(Image.open(_fs(path)).convert("RGBA"))


def cap(work, mode, rep, lang, key):
    return os.path.join(work, f"caps-{mode}-{rep}", f"{SLUG}_{AREA}_rt640-{lang}-{key}_{TAGS[mode]}{OLD_SUFFIX}")


def check(write_report):
    t0 = time.time()
    status_before = git("status", "--porcelain", "--untracked-files=all", "--", "game")
    g, notes = static_gates()
    info = {"started_local": time.strftime("%Y-%m-%d %H:%M:%S"), "godot_sha256": sha(read_bytes(GODOT)),
            "fixed_fps": FIXED_FPS, "worktree_game_clean_at_start": status_before == ""}
    info["export"] = export_tree()
    g["D05_temp_tree_equals_head"] = not info["export"]["blob_mismatches"] and info["export"]["blobs_checked"] > 1000
    work = os.path.join(TREE, "w")
    os.makedirs(_fs(os.path.join(work, "acc")), exist_ok=True)
    env = dict(os.environ, APPDATA=os.path.join(work, "appdata"))
    os.makedirs(_fs(env["APPDATA"]), exist_ok=True)
    game = os.path.join(TREE, "game")
    contract = v13.harness_contract()
    cpath = os.path.join(work, "contract.json")
    with open(_fs(cpath), "w", encoding="utf-8") as f:
        json.dump(contract, f, indent=1)
    imp = run_cmd([GODOT, "--headless", "--path", game, "--import"], env=env)
    runs, reports = {}, {}
    for rep in REPEATS:
        for mode, flag in MODES.items():
            probe, caps = os.path.join(work, f"probe-{mode}-{rep}"), os.path.join(work, f"caps-{mode}-{rep}")
            os.makedirs(_fs(probe), exist_ok=True)
            os.makedirs(_fs(caps), exist_ok=True)
            runs[(mode, rep)] = run_cmd([GODOT, "--path", game, "--resolution", "640x360", "--fixed-fps", FIXED_FPS,
                                         "-s", os.path.join(TREE, *fc.HARNESS_REL.split("/")), "--", flag,
                                         f"--wdc13-mode={mode}", f"--wdc13-contract={cpath}", f"--wdc13-out={probe}",
                                         f"--wdc13-cap={caps}"], env=env, timeout=1500)
            p = os.path.join(probe, f"wdc13-harness-report-{mode}.json")
            reports[(mode, rep)] = json.loads(read_bytes(p)) if os.path.exists(_fs(p)) else None
    replay = run_cmd([GODOT, "--path", game, "-s", os.path.join(TREE, *v13.REPLAY_BASE_REL.split("/")), "--",
                      os.path.join(work, "acc"), f"{STAMP}-{RUN_ID}", "--wdc-capitol-west-v13"], env=env, timeout=900)
    info["worktree_game_status_unchanged_by_runs"] = status_before == git(
        "status", "--porcelain", "--untracked-files=all", "--", "game")
    rg, rnotes = runtime_gates(imp, runs, reports, replay, contract, work, info)
    g.update(rg)
    notes.update(rnotes)
    info["seconds"] = round(time.time() - t0, 1)
    passed = sum(1 for v in g.values() if v)
    for k, v in g.items():
        print(("PASS " if v else "FAIL ") + k)
    print(json.dumps(notes, indent=1, ensure_ascii=True)[:4000])
    print(f"V13FLAG DETERMINISTIC CHECK {passed}/{len(g)}")
    if write_report:
        write_evidence(g, notes, info, imp, runs, reports, replay, work, passed)
    return 0 if passed == len(g) else 1


def runtime_gates(imp, runs, reports, replay, contract, work, info):
    g, notes = collections.OrderedDict(), collections.OrderedDict()
    g["D06_import_ok"] = imp["exit"] == 0
    g["D07_four_fixed_fps_runs_completed_without_errors"] = all(
        runs[k]["exit"] == 0 and reports[k] is not None and not reports[k]["errors"] and
        not any("SCRIPT ERROR" in l for l in runs[k]["log"]) for k in runs)
    if not g["D07_four_fixed_fps_runs_completed_without_errors"]:
        notes["run_logs"] = {f"{m}-{r}": runs[(m, r)]["log"][-20:] for m, r in runs}
        return g, notes
    shots = [(l, k) for l in ("zh", "en") for k in DETERMINISTIC + VARIABLE]
    # repeatability: same mode twice gives byte-identical frames and identical recorded runs
    rep_px = {}
    for mode in MODES:
        a, b = reports[(mode, "a")], reports[(mode, "b")]
        n = sum(int(np.any(pixels(cap(work, mode, "a", l, k)) != pixels(cap(work, mode, "b", l, k)), axis=2).sum())
                for l, k in shots)
        rep_px[mode] = {"differing_px_total": n, "runs_equal": a["runs"] == b["runs"]}
    notes["repeatability"] = rep_px
    g["D08_each_mode_repeats_byte_identically_under_fixed_fps"] = all(
        v["differing_px_total"] == 0 and v["runs_equal"] for v in rep_px.values())
    rf, rr = reports[("v13flag", "a")], reports[("v12r2flag", "a")]
    g["D09_shared_scene_runs_v13_selector_and_flags_select"] = \
        rf["scene_script"] == fc.res(fc.SELECTOR_REL) == rr["scene_script"] and \
        rf["cmdline_flag_enables_v13"] is True and rr["cmdline_flag_enables_v13"] is False and \
        rr["cmdline_flag_enables_r2"] is True and rf["override"] == {"in_memory_override": False} and \
        rf["viewport"] == [640, 360]
    old = json.loads(read_bytes(rp(f"{fc.V13_OUT_REL}/" + v13.fname("godot-harness-report-test-only-v12ref", "json"))))
    g["D10_flags_off_equals_base_script_and_pre_change_frames"] = all(
        v["entry_equal"] and v["after_equal"] and v["positions_equal"] and v["v12_active"] is not True
        for r in (rf, rr) for v in r["passthrough"].values()) and all(
        r["passthrough"][k]["entry_sha256"] == old["passthrough"][k]["entry_sha256"] and
        r["passthrough"][k]["after_sha256"] == old["passthrough"][k]["after_sha256"]
        for r in (rf, rr) for k in old["passthrough"])
    v13_arr, v12_arr = pixels(rp(fc.V13_BASE_REL)), pixels(rp(fc.V12_BASE_REL))
    walk_px = rf["runs"]["zh"]["entry"]["base_layer"]["walk_sha256"]
    fg_px = rf["runs"]["zh"]["entry"]["base_layer"]["fg_image_sha256"]
    expect = {p: v13.V12_RES_DIR + v13.V12_STEM % (p, "png") for p in
              ["rt-base", "rt-fg", "rt-walk", "rt-ys-mast", "rt-ys-tripod", "rt-ys-beacon", "rt-ys-elm"]}

    def layer_ok(r, base_sha, paths, active):
        return all(r["runs"][l][KEYS[k]]["base_layer"]["image_sha256"] == base_sha and
                   r["runs"][l][KEYS[k]]["base_layer"]["is_override"] is False and
                   r["runs"][l][KEYS[k]]["base_layer"]["layer_paths"] == paths and
                   r["runs"][l][KEYS[k]]["base_layer"]["walk_sha256"] == walk_px and
                   r["runs"][l][KEYS[k]]["base_layer"]["fg_image_sha256"] == fg_px and
                   r["runs"][l][KEYS[k]]["base_layer"]["v13_active"] is active for l, k in shots)
    g["D11_v13_flag_draws_v13_rt_base_rest_is_v12_same_walk_and_fg"] = layer_ok(
        rf, sha(v13_arr.tobytes()), dict(expect, **{"rt-base": fc.res(fc.V13_BASE_REL)}), True)
    g["D12_v12r2_flag_draws_v12_layers"] = layer_ok(rr, sha(v12_arr.tobytes()), expect, False)
    # fixed-position shots against the committed frames: exact, or the one inherited label-slot variance
    olds = {"v13flag": json.loads(read_bytes(rp(f"{fc.V13_OUT_REL}/" + v13.fname("godot-harness-report-test-only-v13", "json")))),
            "v12r2flag": old}
    old_tag = {"v13flag": "test-only-v13", "v12r2flag": "test-only-v12ref"}
    fixed, fixed_ok = {}, True
    for mode in MODES:
        for lang in ("zh", "en"):
            for k in DETERMINISTIC:
                new = pixels(cap(work, mode, "a", lang, k))
                was = pixels(rp(f"{fc.V13_OUT_REL}/{SLUG}_{AREA}_rt640-{lang}-{k}_{old_tag[mode]}{OLD_SUFFIX}"))
                sa, sb = reports[(mode, "a")]["runs"][lang][KEYS[k]]["state"], olds[mode]["runs"][lang][KEYS[k]]["state"]
                n = int(np.any(new != was, axis=2).sum())
                entry = {"differing_px": n, "state_equal": sa == sb}
                if not (n == 0 and sa == sb):
                    rest = {x: y for x, y in sa.items() if x != "labels"} == {x: y for x, y in sb.items() if x != "labels"}
                    moved = [r for r in sa["labels"] + sb["labels"] if r not in sa["labels"] or r not in sb["labels"]]
                    allowed = np.zeros(new.shape[:2], bool)
                    for r in moved:
                        x0, y0, w, h = (int(round(v)) for v in r["screen"])
                        allowed[max(0, y0 - 3): y0 + h + 3, max(0, x0 - 3): x0 + w + 3] = True
                    inside = not np.any(np.any(new != was, axis=2) & ~allowed)
                    entry["label_slot_variance"] = {"rest_equal": rest, "moved": sorted({r["name"] for r in moved}),
                                                    "inside": bool(inside)}
                    fixed_ok = fixed_ok and rest and bool(moved) and inside
                fixed[f"{mode}:{lang}:{k}"] = entry
    notes["fixed_position_vs_committed"] = fixed
    notes["fixed_position_pixel_exact"] = sum(1 for v in fixed.values() if v["differing_px"] == 0 and v["state_equal"])
    g["D13_20_fixed_position_shots_exact_or_label_slot_only_vs_committed"] = fixed_ok and len(fixed) == 20
    # base vs candidate under identical inputs and deltas: states, then pixels only inside the projected v13 change
    m = np.any(v13_arr != v12_arr, axis=2)
    pair, move_ok, fixed_pair_ok = {}, True, True
    for lang in ("zh", "en"):
        for k in DETERMINISTIC + VARIABLE:
            sa, sb = rf["runs"][lang][KEYS[k]]["state"], rr["runs"][lang][KEYS[k]]["state"]
            ia, ib = pixels(cap(work, "v13flag", "a", lang, k)), pixels(cap(work, "v12r2flag", "a", lang, k))
            scroll = sa["scroll"]
            proj = np.zeros(m.shape, bool)
            for sy in range(62, 318):
                wy = sy - 62 + scroll
                if 0 <= wy < m.shape[0]:
                    proj[sy] = m[wy]
            d = np.any(ia != ib, axis=2)
            ys, xs = np.nonzero(proj)
            wys = ys - 62 + scroll
            bare = np.all(ib[ys, xs] == v12_arr[wys, xs], axis=1)
            art = bool(np.all(ia[ys[bare], xs[bare]] == v13_arr[wys[bare], xs[bare]]))
            dist = float(np.hypot(sa["hero"][0] - sb["hero"][0], sa["hero"][1] - sb["hero"][1]))
            within = abs(sa["scroll"] - sb["scroll"]) <= 1 and dist <= 3.0
            ok = sa == sb and within and not np.any(d & ~proj) and not np.any(d[:62]) and not np.any(d[318:]) and art
            pair[f"{lang}:{k}"] = {"state_equal": sa == sb, "scroll": [sa["scroll"], sb["scroll"]],
                                   "hero_distance_px": round(dist, 4), "changed_px": int(d.sum()),
                                   "outside_projected_change_px": int((d & ~proj).sum()),
                                   "bare_v13_texels_verified": int(bare.sum()), "v13_art_exact": art}
            if k in VARIABLE:
                move_ok = move_ok and ok
            else:
                fixed_pair_ok = fixed_pair_ok and ok and int(d.sum()) >= 1500
    notes["base_vs_candidate_same_inputs_and_deltas"] = pair
    g["D14_moving_shots_base_vs_candidate_identical_state_and_only_v13_art_differs"] = move_ok
    g["D15_fixed_shots_base_vs_candidate_only_v13_art_differs_and_collapse_visible"] = fixed_pair_ok
    g["D16_records_checked_by_real_interact"] = all(
        r["runs"][l]["records_checked"]["state"]["records_checked"] and
        not r["runs"][l]["records_prompt"]["state"]["records_checked"] for r in (rf, rr) for l in ("zh", "en"))
    enc_ok, enc = True, {}
    for name, r in (("v13flag", rf), ("v12r2flag", rr)):
        for lang in ("zh", "en"):
            run = r["runs"][lang]
            e, br = run.get("encounter", {}), run.get("battle_return", {})
            enc_ok = enc_ok and run["traversal_walk"]["ok"] and run["approach"]["walk_ok"] and \
                run["approach"]["scene_changed"] and e.get("battle_scene") == "res://scenes/battle_arena.tscn" and \
                e.get("battle_enemy") == "sentry" and e.get("auto_mode_by_input") and e.get("battle_won") and \
                e.get("flags") == [True, True] and e.get("result_button_focused") and \
                e.get("scene_after_result") == "res://scenes/scifi_exploration_area.tscn" and \
                br.get("equals_return_texel") and br.get("camera_current") and \
                br["state"]["scroll"] == br.get("expected_scroll")
            enc[f"{name}:{lang}"] = {"return_position": e.get("return_position"), "scroll": br.get("state", {}).get("scroll"),
                                     "approach_frames": run["approach"]["frames"], "traversal_frames": run["traversal_walk"]["frames"]}
    notes["battle"] = enc
    g["D17_real_traversal_battle_and_return_both_flags_both_languages"] = enc_ok
    g["D18_heroine_canvas_inside_play_band"] = all(
        62 <= r["runs"][l][KEYS[k]]["state"]["hero_canvas_screen_rows"][0] and
        r["runs"][l][KEYS[k]]["state"]["hero_canvas_screen_rows"][1] <= 317 for r in (rf, rr) for l, k in shots)
    g["D19_real_saves_untouched"] = all(reports[k]["saves"]["real_unchanged"] for k in reports)
    acc = {}
    for folder, tagx in v13.ACCEPTED:
        for ref in sorted(os.listdir(_fs(rp(folder)))):
            if ref.endswith(f"_20261017-{tagx}.png"):
                stem = ref[: -len(f"_20261017-{tagx}.png")]
                got = os.path.join(work, "acc", f"{stem}_{STAMP}-{RUN_ID}.png")
                if os.path.exists(_fs(got)):
                    a = np.array(Image.open(_fs(os.path.join(rp(folder), ref))).convert("RGB")).astype(np.int16)
                    b = np.array(Image.open(_fs(got)).convert("RGB")).astype(np.int16)
                    acc[ref] = int(np.any(a != b, axis=2).sum())
                else:
                    acc[ref] = "missing replay"
    notes["accepted_rooms_differing_px"] = acc
    full = replay["full"]
    g["D20_accepted_rooms_8_of_8_zero_px_with_v13_flag_present"] = len(acc) == 8 and \
        all(v == 0 for v in acc.values()) and sum(full.count(k) for k in (
            "NYC_ROOM1_INTERACTIONS_OK 3", "NYC_ROOM2_INTERACTIONS_OK 3", "YONKERS_ROOM2_INTERACTIONS_OK 3")) == 3 and \
        "ACCEPTED_REPLAY_ALL_OK" in full and "SCRIPT ERROR" not in full
    g["D21_worktree_game_dir_untouched_by_runs"] = info["worktree_game_status_unchanged_by_runs"]
    g["D22_harness_contract_equals_committed_v13_run"] = contract == json.loads(read_bytes(rp(
        f"{fc.V13_OUT_REL}/" + v13.fname("godot-runtime-check-report", "json"))))["contract"]
    return g, notes


def write_evidence(g, notes, info, imp, runs, reports, replay, work, passed):
    out = {}
    for mode in MODES:
        d = os.path.join(work, f"caps-{mode}-a")
        for f in sorted(os.listdir(_fs(d))):
            new = f.replace(f"_{TAGS[mode]}{OLD_SUFFIX}", f"_{TAGS[mode]}-fixedfps_{STAMP}-{RUN_ID}.png")
            b = read_bytes(os.path.join(d, f))
            write_bytes(rp(f"{OUT_REL}/{new}"), b)
            out[new] = sha(b)
        b = (portable(read_bytes(os.path.join(work, f"probe-{mode}-a", f"wdc13-harness-report-{mode}.json")).decode())
             .replace("\r\n", "\n").rstrip("\n") + "\n").encode()
        f = out_name(f"fixedfps-harness-report-{mode}", "json")
        write_bytes(rp(f"{OUT_REL}/{f}"), b)
        out[f] = sha(b)
    rlog = portable("\n".join(replay["full"].replace("\r\n", "\n").splitlines()[-200:])).encode() + b"\n"
    f = out_name("fixedfps-accepted-rooms-replay-log", "txt")
    write_bytes(rp(f"{OUT_REL}/{f}"), rlog)
    out[f] = sha(rlog)
    report = {"run": RUN, "mode": "check", "gates": g, "passed": passed, "total": len(g), "notes": notes,
              "info": json.loads(portable(json.dumps(info))), "import": {"exit": imp["exit"], "seconds": imp["seconds"]},
              "harness_runs": {f"{m}-{r}": {"exit": v["exit"], "seconds": v["seconds"],
                                            "log": [portable(l) for l in v["log"]]} for (m, r), v in runs.items()},
              "repeat_b_capture_sha256": {f"{m}": {f: sha(read_bytes(os.path.join(work, f"caps-{m}-b", f)))
                                                   for f in sorted(os.listdir(_fs(os.path.join(work, f"caps-{m}-b"))))}
                                          for m in MODES},
              "replay_run": {"exit": replay["exit"], "seconds": replay["seconds"],
                             "log": [portable(l) for l in replay["log"]]}}
    f = out_name("deterministic-check-report", "json")
    b = (json.dumps(report, indent=1) + "\n").encode()
    write_bytes(rp(f"{OUT_REL}/{f}"), b)
    out[f] = sha(b)
    manifest = {"project": SLUG, "area": AREA, "run": RUN, "status": "technical check only; art UNAPPROVED; no runtime change",
                "head_at_check": notes["head"], "predecessor": PREDECESSOR, "fixed_fps": FIXED_FPS,
                "sources_sha256_text_lf_v1": {TOOL_REL: sha_text(read_bytes(rp(TOOL_REL)))},
                "evidence_sha256_bytes": out, "qa_note": QA_REL,
                "authoring": "Claude Code (claude.ai Max, firstParty); no API key, no image model, no paid fallback"}
    f = out_name("deterministic-check-manifest", "json")
    write_bytes(rp(f"{OUT_REL}/{f}"), (json.dumps(manifest, indent=1) + "\n").encode())
    print("evidence written:", len(out) + 1, "files")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        return check("--write-report" in sys.argv)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
