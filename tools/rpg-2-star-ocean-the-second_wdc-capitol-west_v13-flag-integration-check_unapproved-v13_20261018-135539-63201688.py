#!/usr/bin/env python3
"""Washington Capitol west v13: normal-game opt-in flag `--wdc-capitol-west-v13` (UNAPPROVED, off by default).

What this run adds (run wdc-cw-v13flag_20261018-135539-63201688)
    game/scripts/...exploration-opt-in-selector_unapproved-v13_20261018-135539-63201688.gd
        extends the v12r2 selector; with the flag it turns v12r2 on and resolves only the rt-base layer to the
        committed v13 art (run wdc-cw-v13_20261018-100938-075675cf). Without the flag every override hands
        straight to v12r2, which is itself inert without its own flag.
    game/scenes/scifi_exploration_area.tscn: one script path line, v12r2 selector -> v13 selector.
    game/assets/.../wdc-cw-v13_20261018-100938-075675cf/...rt-base...png.import: the import sidecar, written by
        Godot's own --import in an isolated temp tree (mode `import-sidecar`), same parameters as v12's rt-base.
    The v13 art itself is not touched.

Modes (runtime Python, isolated):  python -I -B <this file> import-sidecar | check [--write-report]
    import-sidecar  export HEAD + this run's game/ changes to a temp tree, run Godot --import there, copy only the
                    v13 rt-base .import back into the worktree
    check           export HEAD + this run's game/ changes, import, then through the normal flag path (no in-memory
                    override): the flag-path harness with `--wdc-capitol-west-v13` and with
                    `--wdc-capitol-west-v12r2`, the tracked accepted-rooms replay with the v13 flag present, and
                    the four existing smokes. Captures are compared with the committed v13 run's frames.
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
V13_TOOL = os.path.join(HERE, "rpg-2-star-ocean-the-second_wdc-capitol-west_ruin-material-collapse_pixelorama-author-check_"
                              "unapproved-v13_20261018-100938-075675cf.py")
_spec = importlib.util.spec_from_file_location("wdc_v13_tool", V13_TOOL)
v13 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v13)
rp, _fs, read_bytes, write_bytes, sha, sha_text, git, run_cmd = (
    v13.rp, v13._fs, v13.read_bytes, v13.write_bytes, v13.sha, v13.sha_text, v13.git, v13.run_cmd)
REPO, SLUG, AREA, GODOT = v13.REPO, v13.SLUG, v13.AREA, v13.GODOT

STAMP, RUN_ID = "20261018-135539", "63201688"
RUN = f"wdc-cw-v13flag_{STAMP}-{RUN_ID}"
OUT_REL = f"outputs/{RUN}"
TOOL_REL = "tools/" + os.path.basename(os.path.abspath(__file__))
HARNESS_REL = f"tools/{SLUG}_{AREA}_v13-flag-path-harness_unapproved-v13_{STAMP}-{RUN_ID}.gd"
QA_REL = f"docs/qa/{SLUG}_{AREA}_v13-flag-integration_qa-note_unapproved-v13_{STAMP}-{RUN_ID}.md"
SELECTOR_REL = f"game/scripts/{SLUG}_{AREA}_exploration-opt-in-selector_unapproved-v13_{STAMP}-{RUN_ID}.gd"
R2_SELECTOR_REL = f"game/scripts/{SLUG}_{AREA}_exploration-opt-in-selector_unapproved-v12r2_20261018-042200-7c1e5b39.gd"
SCENE_REL = "game/scenes/scifi_exploration_area.tscn"
V13_BASE_REL = f"{v13.CAND_REL}/" + v13.fname("rt-base", "png")
V13_IMPORT_REL = V13_BASE_REL + ".import"
V12_BASE_REL = f"{v13.V12_CAND_REL}/" + v13.V12_STEM % ("rt-base", "png")
V12_WALK_REL = f"{v13.V12_CAND_REL}/" + v13.V12_STEM % ("rt-walk", "png")
V12_FG_REL = f"{v13.V12_CAND_REL}/" + v13.V12_STEM % ("rt-fg", "png")
OVERLAY = [SCENE_REL, SELECTOR_REL, V13_IMPORT_REL]
V13_OUT_REL = v13.OUT_REL
OLD_SUFFIX = "_20261018-100938-075675cf.png"
TREE = os.path.join(os.environ.get("LOCALAPPDATA", os.environ.get("TEMP", ".")), "Temp", "wr13f-" + RUN_ID)
SMOKES = v13.SMOKES
DETERMINISTIC = ["entry", "records-prompt", "records-checked", "occlusion", "breach-view"]
VARIABLE = ["traversal", "traversal-end", "battle-return"]
KEYS = {"entry": "entry", "records-prompt": "records_prompt", "records-checked": "records_checked",
        "occlusion": "occlusion", "breach-view": "breach_view", "traversal": "traversal",
        "traversal-end": "traversal_end", "battle-return": "battle_return"}
MODES = {"v13flag": ("--wdc-capitol-west-v13", "flag-v13", "test-only-v13"),
         "v12r2flag": ("--wdc-capitol-west-v12r2", "flag-v12r2", "test-only-v12ref")}


def out_name(purpose, ext):
    return f"{SLUG}_{AREA}_{purpose}_unapproved-v13_{STAMP}-{RUN_ID}.{ext}"


def res(rel):
    return "res://" + rel[len("game/"):]


def pixels(path):
    return np.array(Image.open(_fs(path)).convert("RGBA"))


def portable(text):
    # Logs and reports keep no machine paths: the temp tree and the repo become placeholders.
    for real, token in ((TREE, "<TEMP_TREE>"), (TREE.replace("\\", "/"), "<TEMP_TREE>"),
                        (REPO, "<REPO>"), (REPO.replace("\\", "/"), "<REPO>")):
        text = text.replace(real, token).replace(real.replace("\\", "\\\\"), token)
    return text


def export_tree():
    if os.path.exists(_fs(TREE)):
        shutil.rmtree(_fs(TREE))
    os.makedirs(_fs(TREE))
    head = git("rev-parse", "HEAD").strip()
    proc = subprocess.Popen(["git", "-C", REPO, "-c", "core.autocrlf=false", "archive", "--format=tar", head,
                             "game", v13.REPLAY_BASE_REL, v13.HARNESS_REL], stdout=subprocess.PIPE)
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
    # this run's game/ changes, as LF bytes (what git will store)
    status = git("-c", "core.quotepath=off", "status", "--porcelain", "--untracked-files=all", "--", "game")
    changed = sorted(line[3:].strip() for line in status.splitlines() if line.strip())
    overlaid = []
    for rel in OVERLAY:
        if os.path.exists(_fs(rp(rel))):
            data = read_bytes(rp(rel)).replace(b"\r\n", b"\n")
            target = os.path.join(TREE, *rel.split("/"))
            os.makedirs(_fs(os.path.dirname(target)), exist_ok=True)
            with open(_fs(target), "wb") as f:
                f.write(data)
            overlaid.append(rel)
    target = os.path.join(TREE, *HARNESS_REL.split("/"))
    shutil.copyfile(_fs(rp(HARNESS_REL)), _fs(target))
    listing = git("-c", "core.quotepath=off", "ls-tree", "-r", head, "game")
    total, bad = 0, []
    for line in listing.splitlines():
        meta, path = line.split("\t", 1)
        mode, kind, blob = meta.split()
        if kind != "blob" or mode == "120000" or path in overlaid:
            continue
        total += 1
        data = read_bytes(os.path.join(TREE, *path.split("/")))
        import hashlib
        if hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest() != blob:
            bad.append(path)
    return {"head": head, "blobs_checked": total, "blob_mismatches": bad, "worktree_game_changes": changed,
            "overlaid": overlaid}


def godot_env(work):
    os.makedirs(_fs(os.path.join(work, "appdata")), exist_ok=True)
    return dict(os.environ, APPDATA=os.path.join(work, "appdata"))


def import_sidecar():
    info = export_tree()
    if V13_IMPORT_REL in info["overlaid"]:
        print("sidecar already in the worktree; nothing to do")
        return 0
    work = os.path.join(TREE, "w")
    r = run_cmd([GODOT, "--headless", "--path", os.path.join(TREE, "game"), "--import"], env=godot_env(work))
    src = os.path.join(TREE, *V13_IMPORT_REL.split("/"))
    if r["exit"] != 0 or not os.path.exists(_fs(src)):
        print("import failed", r["exit"], r["log"][-10:])
        return 1
    data = read_bytes(src).replace(b"\r\n", b"\n")
    write_bytes(rp(V13_IMPORT_REL), data)
    print("wrote", V13_IMPORT_REL, sha(data))
    return 0


def import_params(path):
    lines = read_bytes(path).decode().replace("\r\n", "\n").split("\n")
    out, section = {}, ""
    for line in lines:
        if line.startswith("["):
            section = line
        elif "=" in line and section == "[params]":
            k, v = line.split("=", 1)
            out[k] = v
    return out, "\n".join(lines)


def check(write_report):
    t0 = time.strftime("%Y-%m-%d %H:%M:%S")
    status_before = git("status", "--porcelain", "--untracked-files=all", "--", "game")
    info = {"started_local": t0, "godot_sha256": sha(read_bytes(GODOT))}
    info["export"] = export_tree()
    work = os.path.join(TREE, "w")
    for d in ("caps", "probe", "acc"):
        os.makedirs(_fs(os.path.join(work, d)), exist_ok=True)
    env = godot_env(work)
    game = os.path.join(TREE, "game")
    contract = v13.harness_contract()
    cpath = os.path.join(work, "probe", "contract.json")
    with open(_fs(cpath), "w", encoding="utf-8") as f:
        json.dump(contract, f, indent=1)
    imp = run_cmd([GODOT, "--headless", "--path", game, "--import"], env=env)
    runs = {}
    for mode, (flag, _, _) in MODES.items():
        runs[mode] = run_cmd([GODOT, "--path", game, "--resolution", "640x360", "-s",
                              os.path.join(TREE, *HARNESS_REL.split("/")), "--", flag, f"--wdc13-mode={mode}",
                              f"--wdc13-contract={cpath}", f"--wdc13-out={os.path.join(work, 'probe')}",
                              f"--wdc13-cap={os.path.join(work, 'caps')}"], env=env, timeout=1500)
    replay = run_cmd([GODOT, "--path", game, "-s", os.path.join(TREE, *v13.REPLAY_BASE_REL.split("/")), "--",
                      os.path.join(work, "acc"), f"{STAMP}-{RUN_ID}", "--wdc-capitol-west-v13"], env=env, timeout=900)
    smokes = {}
    for name in SMOKES:
        r = run_cmd([GODOT, "--headless", "--path", game, "-s", f"res://tests/{name}.gd"], env=env, timeout=900)
        smokes[name] = {"exit": r["exit"], "seconds": r["seconds"],
                        "fail_lines": [l for l in r["log"] if "FAIL" in l or "SCRIPT ERROR" in l][:8]}
    info["worktree_game_status_unchanged_by_runs"] = status_before == git(
        "status", "--porcelain", "--untracked-files=all", "--", "game")
    reports = {}
    for mode in MODES:
        p = os.path.join(work, "probe", f"wdc13-harness-report-{mode}.json")
        reports[mode] = json.loads(read_bytes(p)) if os.path.exists(_fs(p)) else None
    g, notes = gates(info, imp, runs, reports, replay, smokes, contract, work)
    passed = sum(1 for v in g.values() if v)
    for k, v in g.items():
        print(("PASS " if v else "FAIL ") + k)
    print(json.dumps(notes, indent=1)[:6000])
    print(f"V13FLAG CHECK {passed}/{len(g)}")
    if write_report:
        write_evidence(g, notes, info, imp, runs, reports, replay, smokes, work, passed)
    return 0 if passed == len(g) else 1


def gates(info, imp, runs, reports, replay, smokes, contract, work):
    g, notes = collections.OrderedDict(), collections.OrderedDict()
    ex = info["export"]
    g["F01_tree_is_head_plus_exactly_this_runs_game_changes"] = not ex["blob_mismatches"] and \
        ex["blobs_checked"] > 1000 and sorted(ex["overlaid"]) == sorted(OVERLAY) and \
        sorted(ex["worktree_game_changes"]) == sorted([SCENE_REL, SELECTOR_REL, V13_IMPORT_REL])
    # narrow change: one scene line, v13 art untouched, sidecar parameters equal v12's rt-base
    head_scene = git("show", f"HEAD:{SCENE_REL}").replace("\r\n", "\n").split("\n")
    work_scene = read_bytes(rp(SCENE_REL)).decode().replace("\r\n", "\n").split("\n")
    diff = [i for i, (a, b) in enumerate(zip(head_scene, work_scene)) if a != b]
    g["F02_scene_change_is_one_script_path_line"] = len(head_scene) == len(work_scene) and len(diff) == 1 and \
        res(R2_SELECTOR_REL) in head_scene[diff[0]] and \
        work_scene[diff[0]] == head_scene[diff[0]].replace(res(R2_SELECTOR_REL), res(SELECTOR_REL))
    manifest = json.loads(read_bytes(rp(f"{v13.CAND_REL}/" + v13.fname("scene-manifest", "json"))))
    v13_base_bytes = read_bytes(rp(V13_BASE_REL))
    g["F03_v13_art_unchanged_vs_committed_manifest"] = all(
        sha(read_bytes(rp(f"{v13.CAND_REL}/{f}"))) == h for f, h in manifest["files_sha256_bytes"].items()
        if os.path.exists(_fs(rp(f"{v13.CAND_REL}/{f}")))) and \
        sha(v13_base_bytes) == manifest["files_sha256_bytes"][v13.fname("rt-base", "png")] and \
        not git("status", "--porcelain", "--", v13.CAND_REL + "/" + v13.fname("rt-base", "png"))
    p13, t13 = import_params(rp(V13_IMPORT_REL))
    p12, _ = import_params(rp(V12_BASE_REL + ".import"))
    g["F04_sidecar_points_at_v13_rt_base_with_v12_import_params"] = p13 == p12 and \
        f'source_file="{res(V13_BASE_REL)}"' in t13
    g["F05_import_ok"] = imp["exit"] == 0
    g["F06_both_flag_runs_completed_without_errors"] = all(
        runs[m]["exit"] == 0 and reports[m] is not None and not reports[m]["errors"] and
        not any("SCRIPT ERROR" in l for l in runs[m]["log"]) for m in MODES)
    if not g["F06_both_flag_runs_completed_without_errors"]:
        notes["run_logs"] = {m: runs[m]["log"][-20:] for m in MODES}
        return g, notes
    rf, rr = reports["v13flag"], reports["v12r2flag"]
    g["F07_shared_scene_runs_the_v13_selector_and_flags_select"] = \
        rf["scene_script"] == res(SELECTOR_REL) == rr["scene_script"] and \
        rf["cmdline_flag_enables_v13"] is True and rr["cmdline_flag_enables_v13"] is False and \
        rr["cmdline_flag_enables_r2"] is True and rf["override"] == {"in_memory_override": False} and \
        rf["viewport"] == [640, 360]
    # flags off: the shared scene equals the base script, and the same frames as before this run (the committed
    # v13 harness reports recorded the same probes at the previous scene line)
    old = json.loads(read_bytes(rp(f"{V13_OUT_REL}/" + v13.fname("godot-harness-report-test-only-v12ref", "json"))))
    g["F08_flags_off_equals_base_script_and_pre_change_frames"] = all(
        v["entry_equal"] and v["after_equal"] and v["positions_equal"] and v["v12_active"] is not True
        for r in (rf, rr) for v in r["passthrough"].values()) and all(
        r["passthrough"][k]["entry_sha256"] == old["passthrough"][k]["entry_sha256"] and
        r["passthrough"][k]["after_sha256"] == old["passthrough"][k]["after_sha256"]
        for r in (rf, rr) for k in old["passthrough"])
    v13_px, v12_px = sha(pixels(rp(V13_BASE_REL)).tobytes()), sha(pixels(rp(V12_BASE_REL)).tobytes())
    # Walk mask and foreground: Godot's import (fix_alpha_border, as in v12's committed sidecars) rewrites the RGB
    # under transparent texels, so the loaded image cannot hash like the PNG. The first definition of F09/F10 did
    # that and failed; they now require the v12 file paths and the identical loaded image under both flags.
    walk_px = rf["runs"]["zh"]["entry"]["base_layer"]["walk_sha256"]
    fg_px = rf["runs"]["zh"]["entry"]["base_layer"]["fg_image_sha256"]
    shots = [(l, k) for l in ("zh", "en") for k in DETERMINISTIC + VARIABLE]
    expect_paths = {p: v13.V12_RES_DIR + v13.V12_STEM % (p, "png") for p in
                    ["rt-base", "rt-fg", "rt-walk", "rt-ys-mast", "rt-ys-tripod", "rt-ys-beacon", "rt-ys-elm"]}
    v13_paths = dict(expect_paths, **{"rt-base": res(V13_BASE_REL)})

    def layer_ok(rep, base_sha, paths, active):
        return all(KEYS[k] in rep["runs"][l] and
                   rep["runs"][l][KEYS[k]]["base_layer"]["image_sha256"] == base_sha and
                   rep["runs"][l][KEYS[k]]["base_layer"]["is_override"] is False and
                   rep["runs"][l][KEYS[k]]["base_layer"]["layer_paths"] == paths and
                   rep["runs"][l][KEYS[k]]["base_layer"]["walk_sha256"] == walk_px and
                   rep["runs"][l][KEYS[k]]["base_layer"]["fg_image_sha256"] == fg_px and
                   rep["runs"][l][KEYS[k]]["base_layer"]["v13_active"] is active for l, k in shots)
    notes["walk_and_fg_loaded_image_sha"] = {"walk": walk_px[:12], "fg": fg_px[:12]}
    g["F09_v13_flag_draws_v13_rt_base_from_its_file_rest_is_v12"] = layer_ok(rf, v13_px, v13_paths, True)
    g["F10_v12r2_flag_draws_v12_layers_unchanged"] = layer_ok(rr, v12_px, expect_paths, False)
    # captures against the committed v13 run's frames (v13 flag vs test-only v13; v12r2 flag vs test-only v12ref)
    olds = {"v13flag": json.loads(read_bytes(rp(f"{V13_OUT_REL}/" + v13.fname("godot-harness-report-test-only-v13", "json")))),
            "v12r2flag": old}
    px = {}
    exact = {m: True for m in MODES}
    variable_ok = {m: True for m in MODES}
    for mode, (_, tag, old_tag) in MODES.items():
        rep, ref = reports[mode], olds[mode]
        for lang in ("zh", "en"):
            for k in DETERMINISTIC + VARIABLE:
                new = pixels(os.path.join(work, "caps", f"{SLUG}_{AREA}_rt640-{lang}-{k}_{tag}{OLD_SUFFIX}"))
                was = pixels(rp(f"{V13_OUT_REL}/{SLUG}_{AREA}_rt640-{lang}-{k}_{old_tag}{OLD_SUFFIX}"))
                n = int(np.any(new != was, axis=2).sum())
                sa, sb = rep["runs"][lang][KEYS[k]]["state"], ref["runs"][lang][KEYS[k]]["state"]
                px[f"{mode}:{lang}:{k}"] = {"differing_px": n, "state_equal": sa == sb, "hero": sa["hero"],
                                            "ref_hero": sb["hero"], "scroll": sa["scroll"]}
                if k in DETERMINISTIC:
                    # Pixel-exact, or the one inherited variance: v12r1's label solver keeps each label's previous
                    # slot (r1_slots), so where the real-time traversal stopped can move a label in later shots.
                    # Then everything but label rects must match and every differing pixel must lie inside the
                    # old or new rect (+3 px outline) of a label that moved. (First definition: exact only; it
                    # failed once on the unchanged v12r2 path, zh trace0 label x 104 -> 167.)
                    if n == 0 and sa == sb:
                        continue
                    rest_equal = {x: y for x, y in sa.items() if x != "labels"} == \
                        {x: y for x, y in sb.items() if x != "labels"}
                    moved = [r for r in sa["labels"] + sb["labels"]
                             if r not in sa["labels"] or r not in sb["labels"]]
                    allowed = np.zeros(new.shape[:2], bool)
                    for r in moved:
                        x0, y0, w, h = (int(round(v)) for v in r["screen"])
                        allowed[max(0, y0 - 3): y0 + h + 3, max(0, x0 - 3): x0 + w + 3] = True
                    inside = not np.any(np.any(new != was, axis=2) & ~allowed)
                    px[f"{mode}:{lang}:{k}"]["label_slot_variance"] = {
                        "rest_equal": rest_equal, "moved_labels": sorted({r["name"] for r in moved}),
                        "all_differing_px_inside_moved_label_rects": bool(inside)}
                    exact[mode] = exact[mode] and rest_equal and bool(moved) and inside
                else:
                    # real-time walks stop on a frame step: pixel-exact when the state matches, otherwise within one
                    # scroll row and 3 px of the committed frame. The first definition demanded the same scroll and
                    # failed once (en traversal-end under the v13 flag: scroll 13 vs 14, hero 0.9 px apart).
                    near = abs(sa["scroll"] - sb["scroll"]) <= 1 and v13._vec_dist(sa["hero"], sb["hero"]) <= 3.0
                    variable_ok[mode] = variable_ok[mode] and ((sa == sb and n == 0) or (sa != sb and near))
    notes["captures_vs_committed_v13_run"] = px
    g["F11_v13_flag_deterministic_shots_exact_or_label_slot_only_vs_committed_v13"] = exact["v13flag"]
    g["F12_v12r2_flag_deterministic_shots_exact_or_label_slot_only_vs_committed_v12ref"] = exact["v12r2flag"]
    g["F13_traversal_and_battle_return_exact_or_within_1_scroll_row_and_3px"] = all(variable_ok.values())
    g["F14_records_checked_by_real_interact"] = all(
        r["runs"][l]["records_checked"]["state"]["records_checked"] and
        not r["runs"][l]["records_prompt"]["state"]["records_checked"] for r in (rf, rr) for l in ("zh", "en"))
    enc_ok = True
    for r in (rf, rr):
        for lang in ("zh", "en"):
            run = r["runs"][lang]
            e, br = run.get("encounter", {}), run.get("battle_return", {})
            enc_ok = enc_ok and run["traversal_walk"]["ok"] and run["approach"]["walk_ok"] and \
                run["approach"]["scene_changed"] and e.get("battle_scene") == "res://scenes/battle_arena.tscn" and \
                e.get("auto_mode_by_input") and e.get("battle_won") and e.get("flags") == [True, True] and \
                e.get("result_button_focused") and br.get("equals_return_texel") and br.get("camera_current") and \
                br["state"]["scroll"] == br.get("expected_scroll")
    g["F15_real_walks_battle_and_return_both_flags_both_languages"] = enc_ok
    g["F16_heroine_canvas_inside_play_band"] = all(
        62 <= r["runs"][l][KEYS[k]]["state"]["hero_canvas_screen_rows"][0] and
        r["runs"][l][KEYS[k]]["state"]["hero_canvas_screen_rows"][1] <= 317 for r in (rf, rr) for l, k in shots)
    g["F17_real_saves_untouched"] = rf["saves"]["real_unchanged"] and rr["saves"]["real_unchanged"]
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
    g["F18_accepted_rooms_8_of_8_zero_px_with_v13_flag_present"] = len(acc) == 8 and \
        all(v == 0 for v in acc.values()) and sum(full.count(k) for k in (
            "NYC_ROOM1_INTERACTIONS_OK 3", "NYC_ROOM2_INTERACTIONS_OK 3", "YONKERS_ROOM2_INTERACTIONS_OK 3")) == 3 and \
        "ACCEPTED_REPLAY_ALL_OK" in full and "SCRIPT ERROR" not in full
    g["F19_existing_smokes_pass"] = all(s["exit"] == 0 and not s["fail_lines"] for s in smokes.values())
    g["F20_worktree_game_dir_untouched_by_runs"] = info["worktree_game_status_unchanged_by_runs"]
    g["F21_harness_contract_equals_committed_v13_run"] = contract == json.loads(read_bytes(rp(
        f"{V13_OUT_REL}/" + v13.fname("godot-runtime-check-report", "json"))))["contract"]
    return g, notes


def write_evidence(g, notes, info, imp, runs, reports, replay, smokes, work, passed):
    out = {}
    for f in sorted(os.listdir(_fs(os.path.join(work, "caps")))):
        new = f.replace(OLD_SUFFIX, f"_{STAMP}-{RUN_ID}.png")
        b = read_bytes(os.path.join(work, "caps", f))
        write_bytes(rp(f"{OUT_REL}/{new}"), b)
        out[new] = sha(b)
    for mode in MODES:
        b = portable(read_bytes(os.path.join(work, "probe", f"wdc13-harness-report-{mode}.json")).decode()).encode()
        b = b.replace(b"\r\n", b"\n")
        f = out_name(f"godot-flag-harness-report-{mode}", "json")
        write_bytes(rp(f"{OUT_REL}/{f}"), b + (b"" if b.endswith(b"\n") else b"\n"))
        out[f] = sha(read_bytes(rp(f"{OUT_REL}/{f}")))
    rlog = portable("\n".join(replay["full"].replace("\r\n", "\n").splitlines()[-200:])).encode() + b"\n"
    f = out_name("accepted-rooms-replay-log-with-v13-flag", "txt")
    write_bytes(rp(f"{OUT_REL}/{f}"), rlog)
    out[f] = sha(rlog)
    report = {"run": RUN, "mode": "check", "gates": g, "passed": passed, "total": len(g), "notes": notes,
              "info": json.loads(portable(json.dumps(info))),
              "import": {"exit": imp["exit"], "seconds": imp["seconds"]},
              "flag_runs": {m: {"exit": r["exit"], "seconds": r["seconds"],
                                "log": [portable(l) for l in r["log"]]} for m, r in runs.items()},
              "replay_run": {"exit": replay["exit"], "seconds": replay["seconds"],
                             "log": [portable(l) for l in replay["log"]]}, "smokes": smokes}
    f = out_name("flag-integration-check-report", "json")
    b = (json.dumps(report, indent=1) + "\n").encode()
    write_bytes(rp(f"{OUT_REL}/{f}"), b)
    out[f] = sha(b)
    manifest = {
        "project": SLUG, "area": AREA, "run": RUN, "status": "UNAPPROVED runtime art; opt-in only, off by default",
        "art_approved": False, "default_runtime_changed": False, "flag": "--wdc-capitol-west-v13",
        "precedence": "v13 builds on v12r2: the v13 flag turns v12r2/v12r1/v12 on and wins over their flags; "
                      "the records chamber (--wdc-records-chamber-v01) is independent",
        "head_at_check": info["export"]["head"], "art_run": v13.RUN,
        "art_manifest_sha256": sha(read_bytes(rp(f"{v13.CAND_REL}/" + v13.fname("scene-manifest", "json")))),
        "sources_sha256_text_lf_v1": {rel: sha_text(read_bytes(rp(rel))) for rel in
                                      [SELECTOR_REL, SCENE_REL, V13_IMPORT_REL, HARNESS_REL, TOOL_REL]},
        "evidence_sha256_bytes": out,
        "authoring": "Claude Code (claude.ai Max, firstParty); no API key, no image model, no paid fallback",
        "qa_note": QA_REL}
    f = out_name("flag-integration-manifest", "json")
    write_bytes(rp(f"{OUT_REL}/{f}"), (json.dumps(manifest, indent=1) + "\n").encode())
    print("evidence written:", len(out) + 1, "files")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "import-sidecar":
        return import_sidecar()
    if mode == "check":
        return check("--write-report" in sys.argv)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
