"""WDC Capitol west v12r2: sentry-encounter viewport fix — clean-HEAD replay + main-worktree run + gates.

Usage: python <this file> [all|analyze]
  all      reuse (or rebuild) the v12r1 clean tracked-HEAD tree, re-verify every HEAD blob, lay the v12r1 overlay plus
           the v12r2 selector, scene line and harness on top, run the targeted harness there and once in the shared
           worktree, then write the gates report into outputs/wdc-cw-v12r2_20261018-042200-7c1e5b39/.
  analyze  recompute the gates from the saved reports and captures.
Helpers (export, hashing, overlay list) come from the v12r1 check tool, imported read-only. Never stages or commits.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("r1tool", os.path.join(
    HERE, "rpg-2-star-ocean-the-second_wdc-capitol-west_integration-fix-check_unapproved-v12r1_20261018-034933-23596520.py"))
r1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r1)

RUN = "wdc-cw-v12r2_20261018-042200-7c1e5b39"
TAG = "unapproved-v12r2_20261018-042200-7c1e5b39"
P = r1.P
OUT_REL = f"outputs/{RUN}"
R2_SELECTOR = f"game/scripts/{P}exploration-opt-in-selector_{TAG}.gd"
R2_HARNESS = f"tools/{P}sentry-viewport-harness_{TAG}.gd"
R2_LINE = f'path="res://scripts/{P}exploration-opt-in-selector_{TAG}.gd"'
CAM = {"start": 238, "ease": 12.0, "rate": 1.7, "top": 104.0}
SENTRY = (566, 320)
# _draw_enemy feet blocks: Rect2(enemy + (-17, 11), (8, 7)) and Rect2(enemy + (9, 11), (8, 7)), colour #463942.
FEET_RECTS = [(SENTRY[0] - 17, SENTRY[1] + 11, 8, 7), (SENTRY[0] + 9, SENTRY[1] + 11, 8, 7)]
FEET_RGB = (0x46, 0x39, 0x42)
FEET_BOTTOM_ROW = SENTRY[1] + 17


def out(name, ext="json"):
    return r1.rp(f"{OUT_REL}/{P}{name}_{TAG}.{ext}")


def r2_scroll_for(feet):
    d = float(feet) - CAM["start"]
    e, r, top = CAM["ease"], CAM["rate"], CAM["top"]
    rise = 0.5 * r * e
    hold = (top - 2.0 * rise) / r
    if d <= 0:
        s = 0.0
    elif d < e:
        s = 0.5 * r * d * d / e
    elif d < e + hold:
        s = rise + r * (d - e)
    elif d < 2 * e + hold:
        rest = 2 * e + hold - d
        s = top - 0.5 * r * rest * rest / e
    else:
        s = top
    lowest = int(np.floor(float(feet) + 0.5)) + 3 - 255
    return int(min(max(max(int(np.floor(s + 0.5)), lowest), 0), 104))


def raw_slope(feet):
    def raw(f):
        d = f - CAM["start"]
        e, r, top = CAM["ease"], CAM["rate"], CAM["top"]
        rise, hold = 0.5 * r * e, (top - r * e) / r
        if d <= 0:
            return 0.0
        if d < e:
            return 0.5 * r * d * d / e
        if d < e + hold:
            return rise + r * (d - e)
        if d < 2 * e + hold:
            return top - 0.5 * r * (2 * e + hold - d) ** 2 / e
        return top
    return (raw(feet + 0.25) - raw(feet - 0.25)) / 0.5


def contract(walk_abs):
    c = json.loads(r1.read(r1.rp(r1.V12_CONTRACT)))
    return {"spawn": r1.R1["spawn"], "routes": {"sentry": c["routes"]["sentry"]},
            "north_column_route": [r1.R1["spawn"], [372, 214], [400, 214], [469, 283], [507, 283], [513, 289], [555, 289],
                                   [566, 279], [566, 300]],
            "south_end": [372, 354], "camera_lane": [[300, 230], [300, 354]], "walkmask_abs": walk_abs.replace("\\", "/")}


def scene_bytes():
    # r1 (2026-10-18): works before and after the hook is committed; only the pinned hook lines are accepted
    # (see the v12r1 tool's scene_with_hook and its pinned baseline).
    assert R2_LINE == r1.SCENE_LINE_R2_SUCCESSOR
    return r1.scene_with_hook(r1.git("show", f"HEAD:{r1.SCENE}", binary=True), R2_LINE)


def prepare_clean():
    root = r1.CLEAN_ROOT
    info = {"root": root}
    if not os.path.exists(r1.fs(os.path.join(root, "game", "project.godot"))):
        info["export"] = r1.export_head(root)
        info["reused"] = False
    else:
        info["reused"] = True
    # Re-verify every tracked HEAD blob that the overlay does not replace.
    overlay_paths = {f[0] for f in r1.overlay_files()}
    listing = r1.git("-c", "core.quotepath=off", "ls-tree", "-r", "HEAD", "game")
    total, bad = 0, []
    import hashlib
    for line in listing.splitlines():
        meta, path = line.split("\t", 1)
        mode, kind, blob = meta.split()
        if kind != "blob" or mode == "120000" or path in overlay_paths:
            continue
        total += 1
        data = r1.read(os.path.join(root, *path.split("/")))
        if hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest() != blob:
            bad.append(path)
    info["head_blobs_checked"] = total
    info["head_blob_mismatches"] = bad
    manifest = r1.apply_overlay(root)  # v12r1 overlay (scene line rewritten below)
    extra = [[r1.SCENE, scene_bytes(), "modified tracked file: one script path line (HEAD base -> v12r2 selector)"],
             [R2_SELECTOR, r1.read(r1.rp(R2_SELECTOR)), "v12r2 selector (new; extends v12r1)"],
             [R2_HARNESS, r1.read(r1.rp(R2_HARNESS)), "v12r2 targeted harness (-s, outside game/)"]]
    manifest = [m for m in manifest if m["path"] != r1.SCENE]
    for rel, data, role in extra:
        target = os.path.join(root, *rel.split("/"))
        os.makedirs(r1.fs(os.path.dirname(target)), exist_ok=True)
        with open(r1.fs(target), "wb") as f:
            f.write(data)
        manifest.append({"path": rel, "role": role, "pin": r1.pin(rel, data), "bytes": len(data),
                         "equals_worktree_lf": r1.sha_text(data) == r1.sha_text(r1.read(r1.rp(rel)))})
    info["overlay"] = manifest
    info["import"] = r1.run([r1.godot(), "--headless", "--path", os.path.join(root, "game"), "--import"], timeout=1800)
    info["smokes"] = r1.smokes(os.path.join(root, "game"))
    return info


def harness(game_dir, harness_path, work):
    caps, probe = os.path.join(work, "caps"), os.path.join(work, "probe")
    for d in (caps, probe):
        os.makedirs(r1.fs(d), exist_ok=True)
    walk = os.path.join(game_dir, "assets", "environments", "candidates", r1.V12_RUN, f"{P}rt-walk_{r1.V12_TAG}.png")
    cpath = os.path.join(probe, "contract.json")
    with open(r1.fs(cpath), "w", encoding="utf-8") as f:
        json.dump(contract(walk), f, indent=1)
    v8 = os.path.join(game_dir, *r1.V8_PNG[5:].split("/"))
    res = r1.run([r1.godot(), "--path", game_dir, "--resolution", "640x360", "-s", harness_path, "--",
                  "--wdc-capitol-west-v12r2", f"--wdc12r2-contract={cpath}", f"--wdc12r2-out={probe}",
                  f"--wdc12r2-cap={caps}", f"--wdc12r2-v8={v8}"], timeout=1500)
    rep_path = os.path.join(probe, "wdc12r2-harness-report.json")
    rep = json.loads(r1.read(rep_path)) if os.path.exists(r1.fs(rep_path)) else None
    return rep, res, caps


def run_all():
    os.makedirs(r1.fs(r1.rp(OUT_REL)), exist_ok=True)
    info = {"started": time.strftime("%Y-%m-%d %H:%M:%S")}
    info["clean"] = prepare_clean()
    root = r1.CLEAN_ROOT
    work = os.path.join(root, "r2work")
    if os.path.exists(r1.fs(work)):
        shutil.rmtree(r1.fs(work))
    rep, info["clean_run"], caps = harness(os.path.join(root, "game"), os.path.join(root, *R2_HARNESS.split("/")), work)
    info["captures"] = {}
    for name in sorted(os.listdir(r1.fs(caps))):
        shutil.copyfile(r1.fs(os.path.join(caps, name)), r1.fs(r1.rp(f"{OUT_REL}/{name}")))
        info["captures"][name] = r1.sha_bytes(r1.read(os.path.join(caps, name)))
    with open(r1.fs(out("clean-harness-report")), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1)
    # Shared worktree, temp capture dir, git status diffed around it.
    before = r1.git("status", "--porcelain", "--untracked-files=all")
    tmp = tempfile.mkdtemp(prefix="w12r2m-")
    mrep, info["main_run"], mcaps = harness(r1.rp("game"), r1.rp(R2_HARNESS), tmp)
    after = r1.git("status", "--porcelain", "--untracked-files=all")
    new_lines = sorted(set(after.splitlines()) - set(before.splitlines()))
    info["main_new_status_lines"] = new_lines
    info["main_captures"] = {n: r1.sha_bytes(r1.read(os.path.join(mcaps, n))) for n in sorted(os.listdir(mcaps))}
    with open(r1.fs(out("main-harness-report")), "w", encoding="utf-8") as f:
        json.dump(mrep, f, indent=1)
    shutil.rmtree(tmp, ignore_errors=True)
    with open(r1.fs(out("replay-run")), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=1)


def rect_hit(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def layout_ok(state):
    labels, glyphs = state["labels"], state["glyphs"]
    hero = state["hero"]
    fx, fy = round(hero[0]), round(hero[1])
    hero_rect = [fx - 16, fy - 44 - state["scroll"] + 62, 32, 48]
    bad = []
    for i, a in enumerate(labels):
        s = a["screen"]
        if s[1] < 62 or s[1] + s[3] > 318:
            bad.append(("out", a["name"]))
        for b in labels[i + 1:]:
            if rect_hit(s, b["screen"]):
                bad.append(("label", a["name"], b["name"]))
        for g in glyphs:
            if rect_hit(s, g["screen"]):
                bad.append(("glyph", a["name"], g["key"]))
        if rect_hit(s, hero_rect):
            bad.append(("hero", a["name"]))
    for g in glyphs:
        s = g["screen"]
        if s[1] < 62 or s[1] + s[3] > 318:
            bad.append(("glyph-out", g["key"]))
    return bad


def v8_visibility(img, state):
    """Share of the approved v8 frame's opaque texels (drawn at 0.5 scale, nearest) shown unchanged. The GPU's
    nearest-sample phase (which of each 2x2 source block lands on screen) is measured: best of the 4 phases."""
    src = np.asarray(Image.open(r1.fs(r1.rp(r1.V8_PNG))).convert("RGBA"))
    px, py = state["v8"]["position"]
    left, top = int(round(px - 20.0)), int(round(py - 52.0 - state["scroll"] + 62))
    best = None
    for oy in (0, 1):
        for ox in (0, 1):
            total = same = 0
            rows = set()
            for y in range(top, top + 56):
                sy = 2 * (y - top) + oy
                for x in range(left, left + 40):
                    sx = 2 * (x - left) + ox
                    if sy >= src.shape[0] or sx >= src.shape[1] or src[sy, sx, 3] < 128:
                        continue
                    total += 1
                    rows.add(y)
                    if 0 <= y < img.shape[0] and 0 <= x < img.shape[1] and tuple(int(v) for v in img[y, x, :3]) == tuple(int(v) for v in src[sy, sx, :3]):
                        same += 1
            cand = {"phase": [ox, oy], "opaque_texels": total, "shown_unchanged": same, "opaque_rows": len(rows),
                    "rows": [min(rows), max(rows)] if rows else None,
                    "rows_in_play_band": bool(rows) and min(rows) >= 62 and max(rows) <= 317}
            if best is None or same > best["shown_unchanged"]:
                best = cand
    return best


ART_FRONT = None


def art_layers_in_front():
    # Layers drawn above the root canvas (where _draw_enemy paints the sentry): the 4 Y-sort layers and rt-fg.
    global ART_FRONT
    if ART_FRONT is None:
        ART_FRONT = {}
        for purpose in ("rt-ys-mast", "rt-ys-tripod", "rt-ys-beacon", "rt-ys-elm", "rt-fg"):
            path = r1.rp(f"{r1.V12_CAND}/{P}{purpose}_{r1.V12_TAG}.png")
            ART_FRONT[purpose] = np.asarray(Image.open(r1.fs(path)).convert("RGBA"))[..., 3] > 127
    return ART_FRONT


def feet_pixels(img, scroll):
    total = same = in_band = 0
    covered = {}
    unexplained = []
    for x0, y0, w, h in FEET_RECTS:
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                total += 1
                sy = y - scroll + 62
                if not 62 <= sy <= 317:
                    continue
                in_band += 1
                if tuple(int(v) for v in img[sy, x, :3]) == FEET_RGB:
                    same += 1
                    continue
                layers = [k for k, a in art_layers_in_front().items() if a[y, x]]
                if layers:
                    covered[layers[0]] = covered.get(layers[0], 0) + 1
                else:
                    unexplained.append([x, y])
    return {"texels": total, "in_play_band": in_band, "visible_exact": same, "covered_by_world_art": covered,
            "unexplained": unexplained, "bottom_screen_row": FEET_BOTTOM_ROW - scroll + 62}


def analyze(write=True):
    info = json.loads(r1.read(out("replay-run")))
    rep = json.loads(r1.read(out("clean-harness-report")))
    mrep = json.loads(r1.read(out("main-harness-report")))
    g, notes = {}, {}
    c = info["clean"]
    g["clean_head_blobs_exact"] = c["head_blobs_checked"] > 1200 and not c["head_blob_mismatches"]
    g["clean_overlay_equals_worktree"] = all(m["equals_worktree_lf"] for m in c["overlay"])
    g["clean_smokes_pass"] = all(v["exit"] == 0 and not v["fail_lines"] for v in c["smokes"].values())
    g["harness_clean_and_main_exit_0_no_errors"] = (info["clean_run"]["exit"] == 0 and info["main_run"]["exit"] == 0
                                                     and not rep["errors"] and not mrep["errors"])
    g["cmdline_flag_enables_r2"] = rep["cmdline_flag_enables_r2"] is True
    pt = rep["passthrough"]
    g["flags_off_equals_base_city_outskirts_ruins"] = all(
        pt["off_" + d]["entry_equal"] and pt["off_" + d]["after_equal"] and pt["off_" + d]["positions_equal"]
        and not pt["off_" + d]["r2_active"] and not pt["off_" + d]["r1_active"] and not pt["off_" + d]["v12_active"]
        for d in ("scifi.city", "scifi.outskirts", "scifi.ruins"))
    g["r1_flag_only_equals_v12r1"] = (pt["r1_only_ruins"]["entry_equal"] and pt["r1_only_ruins"]["after_equal"]
                                      and pt["r1_only_ruins"]["positions_equal"] and pt["r1_only_ruins"]["r1_active"]
                                      and not pt["r1_only_ruins"]["r2_active"])
    g["v12_flag_only_equals_v12"] = (pt["v12_only_ruins"]["entry_equal"] and pt["v12_only_ruins"]["after_equal"]
                                     and pt["v12_only_ruins"]["positions_equal"] and pt["v12_only_ruins"]["v12_active"]
                                     and not pt["v12_only_ruins"]["r1_active"])
    # Camera curve
    curve = rep["curve"]
    g["curve_godot_equals_tool"] = all(int(s2) == r2_scroll_for(f) for f, s2, _ in curve)
    slopes = [raw_slope(f) for f in np.arange(200, 359, 0.5)]
    changes = [abs(slopes[i + 1] - slopes[i]) for i in range(len(slopes) - 1)]
    mask = np.asarray(Image.open(r1.fs(r1.rp(f"{r1.V12_CAND}/{P}rt-walk_{r1.V12_TAG}.png"))).convert("RGBA"))[..., 3] > 127
    ys, xs = np.nonzero(mask)
    g["curve_monotonic_peak_1_7_eased"] = (all(r2_scroll_for(f + 1) >= r2_scroll_for(f) for f in range(0, 359))
                                          and max(slopes) <= 1.7 + 1e-9 and max(changes) <= 0.075 + 1e-9)
    g["curve_spawn_scroll_0"] = r2_scroll_for(238) == 0
    g["canvas_in_play_band_every_walkable_row"] = all(
        f - 44 - r2_scroll_for(f) + 62 >= 62 and f + 3 - r2_scroll_for(f) + 62 <= 317 for f in sorted(set(ys.tolist())))
    zone = {}
    for radius in (23, 28):
        rows = [y for x, y in zip(xs, ys) if (x - SENTRY[0]) ** 2 + (y - SENTRY[1]) ** 2 < radius * radius]
        worst = min(r2_scroll_for(y) for y in rows)
        zone[radius] = {"walkable_feet": len(rows), "min_scroll": worst, "feet_bottom_screen_row_max": FEET_BOTTOM_ROW - worst + 62,
                        "r1_min_scroll": min(r1.r1_scroll_for(y) for y in rows),
                        "r1_feet_bottom_screen_row_max": FEET_BOTTOM_ROW - min(r1.r1_scroll_for(y) for y in rows) + 62}
    notes["sentry_zone"] = zone
    g["sentry_feet_above_footer_for_every_walkable_foot_within_28px"] = zone[28]["feet_bottom_screen_row_max"] <= 317
    notes["curve_compare"] = {str(f): {"v12r2": r2_scroll_for(f), "v12r1": r1.r1_scroll_for(f), "v12": r1.v12_scroll_for(f)}
                              for f in (238, 246, 250, 262, 280, 290, 298, 305, 315, 330)}
    notes["peak_rate"] = round(max(slopes), 3)
    notes["max_slope_change_per_half_row"] = round(max(changes), 4)
    # Per-language real runs
    caps_meta = {}
    for lang in ("zh", "en"):
        run = rep["runs"][lang]
        pre = run.get("pre_trigger")
        e = run["encounter"]
        entry_img = np.asarray(Image.open(r1.fs(r1.rp(f"{OUT_REL}/{run['entry']['file']}"))).convert("RGBA"))
        flat = np.asarray(Image.open(r1.fs(r1.rp(r1.V12_FLAT))).convert("RGBA"))
        d = r1.DOME
        dome_exact = run["entry"]["state"]["scroll"] == 0 and bool(
            (entry_img[d["top"] + 62:d["bottom"] + 63, d["left"]:d["right"] + 1, :3] == flat[d["top"]:d["bottom"] + 1, d["left"]:d["right"] + 1, :3]).all())
        meta = {"approach_walk_ok": run["approach"]["walk_ok"], "approach_into_battle": run["approach"]["scene_changed"],
                "approach_max_scroll_step": run["approach"]["max_scroll_step"], "entry_dome_exact": dome_exact}
        for key in ("entry", "pre_trigger", "battle_return", "south_end"):
            if key not in run:
                meta[key] = None
                continue
            st = run[key]["state"]
            img = np.asarray(Image.open(r1.fs(r1.rp(f"{OUT_REL}/{run[key]['file']}"))).convert("RGBA"))
            m = {"scroll": st["scroll"], "hero": st["hero"], "hero_canvas_rows": st["hero_canvas_screen_rows"],
                 "layout_problems": layout_ok(st), "v8": v8_visibility(img, st), "size": run[key]["size"]}
            if key == "pre_trigger":
                m["dist_to_sentry"] = round(st["dist_to_enemy"], 2)
                m["sentry_feet"] = feet_pixels(img, st["scroll"])
            meta[key] = m
        meta["battle"] = {k: e.get(k) for k in ("battle_scene", "battle_enemy", "auto_mode_by_input", "battle_won", "enemy_hp_start",
                                                 "enemy_hp_end", "flags", "result_button_focused", "scene_after_result")}
        br = run.get("battle_return", {})
        meta["battle_return_texel"] = br.get("equals_return_texel")
        meta["battle_return_scroll_expected"] = br.get("state", {}).get("scroll") == br.get("expected_scroll")
        caps_meta[lang] = meta
    notes["runs"] = caps_meta
    langs = caps_meta.values()
    g["entry_scroll_0_dome_pixel_exact"] = all(m["entry_dome_exact"] for m in langs)
    g["real_route_walks_into_real_battle"] = all(m["approach_walk_ok"] and m["approach_into_battle"] for m in langs)
    g["pre_trigger_frame_is_last_drawn_before_encounter"] = all(
        m["pre_trigger"] and 23.0 <= m["pre_trigger"]["dist_to_sentry"] < 28.0 for m in langs)
    # Every feet texel is inside the play band (nothing under the HUD); a texel that is not the feet colour must be
    # behind a v11 art layer drawn above the root canvas (inherited v12 draw order), never unexplained.
    g["pre_trigger_sentry_feet_clear_of_hud"] = all(
        m["pre_trigger"]["sentry_feet"]["in_play_band"] == m["pre_trigger"]["sentry_feet"]["texels"] == 112
        and m["pre_trigger"]["sentry_feet"]["bottom_screen_row"] <= 317 and not m["pre_trigger"]["sentry_feet"]["unexplained"]
        and m["pre_trigger"]["sentry_feet"]["visible_exact"] >= 56 for m in langs)
    shots = [m[k] for m in langs for k in ("entry", "pre_trigger", "battle_return", "south_end")]
    g["all_shots_640x360"] = all(s and s["size"] == [640, 360] for s in shots)
    g["heroine_48_row_canvas_in_play_band_all_shots"] = all(s["hero_canvas_rows"][0] >= 62 and s["hero_canvas_rows"][1] <= 317 for s in shots)
    g["v8_reference_48_rows_in_play_band_all_shots"] = all(s["v8"]["opaque_rows"] == 48 and s["v8"]["rows_in_play_band"] for s in shots)
    g["v8_reference_unobstructed_all_shots"] = all(s["v8"]["shown_unchanged"] == s["v8"]["opaque_texels"] > 500 for s in shots)
    g["labels_glyphs_clean_all_shots"] = all(not s["layout_problems"] for s in shots)
    g["approach_camera_step_at_most_4"] = all(m["approach_max_scroll_step"] <= 4 for m in langs)
    g["battle_won_through_battle_outcome_path"] = all(
        m["battle"]["battle_scene"] == "res://scenes/battle_arena.tscn" and m["battle"]["battle_enemy"] == "sentry"
        and m["battle"]["auto_mode_by_input"] and m["battle"]["battle_won"] and m["battle"]["enemy_hp_end"] == 0
        and m["battle"]["flags"] == [True, True] and m["battle"]["result_button_focused"] for m in langs)
    g["battle_return_restores_position_and_camera"] = all(
        m["battle"]["scene_after_result"] == "res://scenes/scifi_exploration_area.tscn" and m["battle_return_texel"]
        and m["battle_return_scroll_expected"] for m in langs)
    g["south_end_full_scroll"] = all(m["south_end"]["scroll"] == 104 for m in langs)
    samples = rep["camera"]["samples"]
    legs = {}
    for leg in ("move_down", "move_up"):
        s = [x for x in samples if x[0] == leg]
        steps = [s[i + 1][2] - s[i][2] for i in range(len(s) - 1)]
        legs[leg] = {"frames": len(s), "max_step": max(abs(v) for v in steps), "reversals": sum(1 for i in range(len(steps) - 1) if steps[i] * steps[i + 1] < 0),
                     "first_last": [s[0][2], s[-1][2]], "hero_screen_feet": [round(min(x[1] - x[2] + 62 for x in s), 1), round(max(x[1] - x[2] + 62 for x in s), 1)]}
    notes["camera_lane"] = legs
    g["camera_lane_smooth_steps_at_most_4_no_reversal"] = all(v["max_step"] <= 4 and v["reversals"] == 0 for v in legs.values()) \
        and legs["move_down"]["first_last"][1] == 104
    g["real_user_saves_unchanged"] = rep["saves"]["real_unchanged"] and mrep["saves"]["real_unchanged"]
    g["main_run_left_no_game_side_effects"] = not [l for l in info["main_new_status_lines"] if l[3:].startswith("game/")]
    det = [n for n in info["captures"] if "-entry-v8ref" in n or "-south-end-v8ref" in n]
    notes["clean_vs_main_deterministic_captures"] = {n: info["captures"][n] == info["main_captures"].get(n) for n in det}
    g["clean_and_main_entry_south_end_byte_identical"] = len(det) == 4 and all(notes["clean_vs_main_deterministic_captures"].values())
    notes["main_pre_trigger_states"] = {lang: {"dist": round(mrep["runs"][lang]["pre_trigger"]["state"]["dist_to_enemy"], 2),
                                               "scroll": mrep["runs"][lang]["pre_trigger"]["state"]["scroll"]}
                                        for lang in ("zh", "en") if "pre_trigger" in mrep["runs"][lang]}
    g = {k: bool(v) for k, v in g.items()}
    passed = sum(1 for v in g.values() if v)
    report = {"candidate": RUN, "status": "UNAPPROVED technical viewport fix; art not accepted; opt-in only",
              "generated": time.strftime("%Y-%m-%d %H:%M:%S"), "passed": passed, "total": len(g),
              "verdict": "PASS" if passed == len(g) else "FAIL", "gates": g, "notes": notes,
              "overlay": c["overlay"], "captures_sha256": info["captures"],
              "counters_unchanged": {"meter": "40.8%", "m2": "10/12", "scenes": "3/12", "sprites": "0/52", "playtests": "0/2"}}
    for k, v in g.items():
        print(("PASS " if v else "FAIL ") + k)
    print(f"{report['verdict']} {passed}/{len(g)}")
    if write:
        with open(r1.fs(out("technical-check-report")), "w", encoding="utf-8") as f:
            json.dump(report, f, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    return report


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "analyze"
    if mode == "all":
        run_all()
    analyze(True)
