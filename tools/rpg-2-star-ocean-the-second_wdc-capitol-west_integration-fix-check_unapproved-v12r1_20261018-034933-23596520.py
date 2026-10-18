"""WDC Capitol west v12r1: isolated clean-HEAD replay + checks for the bounded integration fixes (UNAPPROVED).

Modes (run from anywhere; the repository root is found from this file):
  replay   export the exact tracked HEAD `game/` tree (git archive, autocrlf off, every blob re-hashed) into a
           private temp root, run the HEAD smokes there, copy ONLY the enumerated candidate overlay (hash-pinned),
           re-import, run the overlay smokes, the v12r1 harness (640x360 full + 1280x720 v8 pair) and the
           unchanged v12 harness (reproduction). Captures/reports are copied into outputs/<run dir>/.
  main     run the v12r1 harness once in the shared worktree (temp capture dir) and diff git status around it.
  analyze  turn the saved reports and captures into gates; --write-report writes the check report JSON.
  all      replay + main + analyze --write-report.
It never stages, commits, edits the Git index, or touches progress/ledger/Bible files.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = "wdc-cw-v12r1_20261018-034933-23596520"
TAG = "unapproved-v12r1_20261018-034933-23596520"
V12_RUN = "wdc-cw-v12_20261017-235608-66d00477"
V12_TAG = "unapproved-v12_20261017-235608-66d00477"
OUT_REL = f"outputs/{RUN}"
GODOT_REL = "work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe"
CLEAN_ROOT = os.path.join(os.environ.get("LOCALAPPDATA", tempfile.gettempdir()), "Temp", "w12r1-23596520")
P = "rpg-2-star-ocean-the-second_wdc-capitol-west_"
V12_CAND = f"game/assets/environments/candidates/{V12_RUN}"
V12_SELECTOR = f"game/scripts/{P}exploration-opt-in-selector_{V12_TAG}.gd"
R1_SELECTOR = f"game/scripts/{P}exploration-opt-in-selector_{TAG}.gd"
SCENE = "game/scenes/scifi_exploration_area.tscn"
R1_HARNESS = f"tools/{P}real-scene-probe-harness_{TAG}.gd"
V12_HARNESS = f"tools/{P}real-scene-capture-probe-harness_{V12_TAG}.gd"
V12_CONTRACT = f"{V12_CAND}/{P}rt-contract_{V12_TAG}.json"
V12_FLAT = f"{V12_CAND}/{P}scene-flat-640x360_{V12_TAG}.png"
V8_PNG = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_"
          "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
V8_SHA = "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
RUNTIME_PURPOSES = ["rt-base", "rt-fg", "rt-walk", "rt-ys-mast", "rt-ys-tripod", "rt-ys-beacon", "rt-ys-elm"]
SMOKES = ["m4_smoke", "m6_smoke", "m7_smoke", "m8_city_reentry_smoke"]
SCENE_LINE_HEAD = 'path="res://scripts/scifi_exploration_area.gd"'
SCENE_LINE_R1 = f'path="res://scripts/{P}exploration-opt-in-selector_{TAG}.gd"'
SCENE_LINE_R2_SUCCESSOR = f'path="res://scripts/{P}exploration-opt-in-selector_unapproved-v12r2_20261018-042200-7c1e5b39.gd"'
R1 = {"spawn": [372, 238], "cam_start": 238, "cam_ease": 20.0, "cam_rate": 1.5, "scroll_max": 104}
VIEW_TOP, VIEW_BOTTOM = 62, 317
DOME = {"top": 3, "bottom": 110, "left": 330, "right": 412}


# ---------------------------------------------------------------------------- helpers
def rp(rel):
    return os.path.join(REPO, *rel.split("/"))


def fs(path):
    p = os.path.abspath(path)
    return "\\\\?\\" + p if os.name == "nt" and not p.startswith("\\\\?\\") else p


def read(path):
    with open(fs(path), "rb") as f:
        return f.read()


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_text(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def is_text(rel):
    return rel.endswith((".gd", ".tscn", ".json", ".import", ".md", ".py", ".txt", ".cfg", ".godot"))


def pin(rel, data):
    return ("sha256-text-lf-v1:" + sha_text(data)) if is_text(rel) else ("sha256-bytes:" + sha_bytes(data))


def git(*args, binary=False):
    p = subprocess.run(["git", "-C", REPO, *args], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode('utf-8', 'replace')}")
    return p.stdout if binary else p.stdout.decode("utf-8", "replace")


def godot():
    return rp(GODOT_REL)


def run(args, cwd=None, timeout=1800):
    t0 = time.time()
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, cwd=cwd)
    out = p.stdout + p.stderr
    keep = [l for l in out.splitlines() if any(k in l for k in ("ERROR", "SCRIPT", "WARNING", "FAIL", "WDC12", "PASS"))]
    return {"exit": p.returncode, "seconds": round(time.time() - t0, 1), "log": keep[-60:]}


def out_path(name):
    return rp(f"{OUT_REL}/{P}{name}_{TAG}")


def overlay_files():
    """Exact candidate overlay over tracked HEAD: [repo-relative path, role]."""
    files = [[SCENE, "modified tracked file: one script path line (HEAD base -> v12r1 selector)"],
             [V12_SELECTOR, "pre-existing v12 candidate hook (untracked); v12r1 extends it"],
             [R1_SELECTOR, "v12r1 selector (new)"]]
    for purpose in RUNTIME_PURPOSES:
        png = f"{V12_CAND}/{P}{purpose}_{V12_TAG}.png"
        files.append([png, "v12 runtime layer PNG (untracked, loaded by the v12 selector)"])
        files.append([png + ".import", "Godot import sidecar of that PNG (untracked; repo convention tracks sidecars)"])
    return files


def tool_files():
    return [[R1_HARNESS, "v12r1 test-only harness (-s, outside game/)"],
            [V12_HARNESS, "v12 test-only harness, unchanged, used for the v12 reproduction run"]]


# r1 (2026-10-18): the replay must also work after the hook is committed. HEAD's scene may carry exactly one of these
# pinned hook lines; with that line set back to the base script it must equal the pinned baseline scene (LF sha256 of
# scifi_exploration_area.tscn at 7370739/7553581). Any other hook, a second hook or any other edit is rejected.
ALLOWED_HOOK_LINES = (SCENE_LINE_HEAD, SCENE_LINE_R1, SCENE_LINE_R2_SUCCESSOR)
SCENE_BASE_SHA256_TEXT_LF = "df063dd9f2c9a6665f575c0146fb27a349d8879e581f1f2259b5fca5f8ea587c"


def scene_with_hook(head, target_line):
    lf = head.replace(b"\r\n", b"\n")
    present = [line for line in ALLOWED_HOOK_LINES if line.encode() in lf]
    assert len(present) == 1 and lf.count(present[0].encode()) == 1, "scene hook is not exactly one pinned allowed hook line"
    base = lf.replace(present[0].encode(), SCENE_LINE_HEAD.encode())
    assert hashlib.sha256(base).hexdigest() == SCENE_BASE_SHA256_TEXT_LF, "scene differs from the pinned baseline beyond its hook line"
    return base.replace(SCENE_LINE_HEAD.encode(), target_line.encode())


def scene_overlay_bytes():
    return scene_with_hook(git("show", f"HEAD:{SCENE}", binary=True), SCENE_LINE_R1)


def r1_scroll_for(feet):
    d = float(feet - R1["cam_start"])
    e, r, top = R1["cam_ease"], R1["cam_rate"], float(R1["scroll_max"])
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
    # Godot round()/roundi() is half away from zero; every value here is >= 0.
    lowest = int(np.floor(feet + 0.5)) + 3 - (VIEW_BOTTOM - VIEW_TOP)
    return int(min(max(max(int(np.floor(s + 0.5)), lowest), 0), R1["scroll_max"]))


def v12_scroll_for(feet):
    return int(min(max(max(2 * (feet - 250), feet + 3 - 255), 0), 104))


def contract(walkmask_abs):
    c = json.loads(read(rp(V12_CONTRACT)))
    poses = {"entry": {"at": R1["spawn"], "face": "south"},
             "interaction": c["review_poses"]["interaction"],
             "occlusion": c["review_poses"]["occlusion"],
             "patrol_bypass": c["review_poses"]["patrol_extra"],
             "strata_near": {"at": [520, 276], "face": "east"}}
    routes = dict(c["routes"])
    routes["records"] = [R1["spawn"]] + routes["records"]
    return {"candidate": RUN, "status": "UNAPPROVED technical integration fix candidate; opt-in only",
            "flag": "--wdc-capitol-west-v12r1", "review_poses": poses, "routes": routes, "sweeps": c["sweeps"],
            "anchors": c["anchors"], "dome": c["dome"], "walkmask_abs": walkmask_abs.replace("\\", "/"),
            "camera_lane": {"from": [300, 230], "to": [300, 354]},
            "v8_reference": {"png": V8_PNG, "sha256": V8_SHA, "foot_anchor_px": [40, 103], "scale": 0.5,
                             "offset_from_hero": [44, 0]}}


# ---------------------------------------------------------------------------- replay (clean tree)
def export_head(root):
    head = git("rev-parse", "HEAD").strip()
    tree = git("rev-parse", "HEAD:game").strip()
    if os.path.exists(fs(root)):
        shutil.rmtree(fs(root))
    os.makedirs(fs(root))
    proc = subprocess.Popen(["git", "-C", REPO, "-c", "core.autocrlf=false", "archive", "--format=tar", "HEAD", "game"],
                            stdout=subprocess.PIPE)
    with tarfile.open(fileobj=proc.stdout, mode="r|") as tar:
        for member in tar:
            target = os.path.join(root, *member.name.split("/"))
            if member.isdir():
                os.makedirs(fs(target), exist_ok=True)
            elif member.isfile():
                os.makedirs(fs(os.path.dirname(target)), exist_ok=True)
                with open(fs(target), "wb") as f:
                    f.write(tar.extractfile(member).read())
    proc.wait()
    # Every tracked blob under game/ must be present with its exact git blob id.
    listing = git("-c", "core.quotepath=off", "ls-tree", "-r", "HEAD", "game")
    total, mismatch, longest = 0, [], 0
    for line in listing.splitlines():
        meta, path = line.split("\t", 1)
        mode, kind, blob = meta.split()
        if kind != "blob" or mode == "120000":
            continue
        total += 1
        full = os.path.join(root, *path.split("/"))
        longest = max(longest, len(os.path.abspath(full)))
        data = read(full)
        got = hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()
        if got != blob:
            mismatch.append(path)
    return {"head": head, "game_tree": tree, "blobs": total, "blob_mismatches": mismatch, "longest_path": longest,
            "root": root}


def apply_overlay(root):
    manifest = []
    for rel, role in overlay_files():
        data = scene_overlay_bytes() if rel == SCENE else read(rp(rel))
        worktree = read(rp(rel))
        target = os.path.join(root, *rel.split("/"))
        os.makedirs(fs(os.path.dirname(target)), exist_ok=True)
        with open(fs(target), "wb") as f:
            f.write(data)
        tracked = subprocess.run(["git", "-C", REPO, "cat-file", "-e", f"HEAD:{rel}"], capture_output=True).returncode == 0
        equal = sha_text(data) == sha_text(worktree)
        if rel == SCENE and not equal:
            # r1 (2026-10-18): the worktree hook may name the v12r2 successor (it extends v12r1; with only the v12r1
            # flag it is exactly v12r1). Only that one pinned line is accepted besides the v12r1 line itself.
            equal = sha_text(data.replace(SCENE_LINE_R1.encode(), SCENE_LINE_R2_SUCCESSOR.encode())) == sha_text(worktree)
        manifest.append({"path": rel, "role": role, "tracked_at_head": tracked, "pin": pin(rel, data),
                         "bytes": len(data), "equals_worktree_lf": equal})
    for rel, role in tool_files():
        data = read(rp(rel))
        target = os.path.join(root, *rel.split("/"))
        os.makedirs(fs(os.path.dirname(target)), exist_ok=True)
        with open(fs(target), "wb") as f:
            f.write(data)
        manifest.append({"path": rel, "role": role, "tracked_at_head": False, "pin": pin(rel, data), "bytes": len(data),
                         "equals_worktree_lf": True})
    return manifest


def smokes(game_dir):
    res = {}
    for name in SMOKES:
        r = run([godot(), "--headless", "--path", game_dir, "-s", f"res://tests/{name}.gd"], timeout=900)
        res[name] = {"exit": r["exit"], "seconds": r["seconds"], "fail_lines": [l for l in r["log"] if "FAIL" in l or "SCRIPT ERROR" in l][:8]}
    return res


def harness(game_dir, harness_path, cap_dir, probe_dir, res, mode):
    walk = os.path.join(game_dir, "assets", "environments", "candidates", V12_RUN, f"{P}rt-walk_{V12_TAG}.png")
    cpath = os.path.join(probe_dir, "contract.json")
    with open(fs(cpath), "w", encoding="utf-8") as f:
        json.dump(contract(walk), f, indent=1)
    args = [godot(), "--path", game_dir]
    if res:
        args += ["--resolution", res]
    args += ["-s", harness_path, "--", "--wdc-capitol-west-v12r1", f"--wdc12r1-contract={cpath}",
             f"--wdc12r1-out={probe_dir}", f"--wdc12r1-cap={cap_dir}", f"--wdc12r1-v8={os.path.join(game_dir, *V8_PNG[5:].split('/'))}",
             f"--wdc12r1-mode={mode}"]
    r = run(args, timeout=1500)
    rep = os.path.join(probe_dir, f"wdc12r1-harness-report-{mode}.json")
    return (json.loads(read(rep)) if os.path.exists(fs(rep)) else None), r


def v12_reproduction(game_dir, root, probe_dir):
    cap = os.path.join(probe_dir, "v12caps")
    os.makedirs(fs(cap), exist_ok=True)
    c = json.loads(read(rp(V12_CONTRACT)))
    c["walkmask_abs"] = os.path.join(game_dir, "assets", "environments", "candidates", V12_RUN,
                                     f"{P}rt-walk_{V12_TAG}.png").replace("\\", "/")
    cpath = os.path.join(probe_dir, "v12-contract.json")
    with open(fs(cpath), "w", encoding="utf-8") as f:
        json.dump(c, f)
    r = run([godot(), "--path", game_dir, "--resolution", "640x360", "-s", os.path.join(root, *V12_HARNESS.split("/")), "--",
             "--wdc-capitol-west-v12", f"--wdc12-contract={cpath}", f"--wdc12-out={probe_dir}", f"--wdc12-cap={cap}"],
            timeout=1500)
    hashes = {}
    for name in sorted(os.listdir(fs(cap))):
        hashes[name] = sha_bytes(read(os.path.join(cap, name)))
    rep = os.path.join(probe_dir, "wdc12-harness-report.json")
    report = json.loads(read(rep)) if os.path.exists(fs(rep)) else None
    return {"run": r, "capture_sha256": hashes, "flow_sentry": (report or {}).get("flow", {}).get("sentry"),
            "errors": (report or {}).get("errors")}


def replay():
    os.makedirs(fs(rp(OUT_REL)), exist_ok=True)
    root = CLEAN_ROOT
    info = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "clean_root": root}
    info["export"] = export_head(root)
    game_dir = os.path.join(root, "game")
    info["head_import"] = run([godot(), "--headless", "--path", game_dir, "--import"], timeout=1800)
    info["head_smokes"] = smokes(game_dir)
    info["overlay"] = apply_overlay(root)
    info["overlay_import"] = run([godot(), "--headless", "--path", game_dir, "--import"], timeout=1800)
    info["overlay_smokes"] = smokes(game_dir)
    probe = os.path.join(root, "probe")
    caps = os.path.join(root, "caps")
    for d in (probe, caps):
        os.makedirs(fs(d), exist_ok=True)
    r1_harness = os.path.join(root, *R1_HARNESS.split("/"))
    full, info["harness_full_run"] = harness(game_dir, r1_harness, caps, probe, "640x360", "full")
    hd, info["harness_v8hd_run"] = harness(game_dir, r1_harness, caps, probe, "", "v8hd")
    info["v12_reproduction"] = v12_reproduction(game_dir, root, probe)
    # Copy evidence into the run's outputs dir.
    copied = {}
    for name in sorted(os.listdir(fs(caps))):
        shutil.copyfile(fs(os.path.join(caps, name)), fs(rp(f"{OUT_REL}/{name}")))
        copied[name] = sha_bytes(read(rp(f"{OUT_REL}/{name}")))
    info["captures"] = copied
    for mode, rep in (("full", full), ("v8hd", hd)):
        with open(fs(out_path(f"clean-harness-report-{mode}") + ".json"), "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=1)
    with open(fs(out_path("clean-contract") + ".json"), "w", encoding="utf-8") as f:
        json.dump(contract("<clean root>/game/assets/environments/candidates/" + V12_RUN + f"/{P}rt-walk_{V12_TAG}.png"), f, indent=1)
    with open(fs(out_path("clean-replay-run") + ".json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=1)
    print("replay done", info["harness_full_run"]["exit"], info["harness_v8hd_run"]["exit"])
    return info


# ---------------------------------------------------------------------------- main worktree run
def main_run():
    before = git("status", "--porcelain", "--untracked-files=all")
    tmp = tempfile.mkdtemp(prefix="w12r1m-")
    caps, probe = os.path.join(tmp, "caps"), os.path.join(tmp, "probe")
    os.makedirs(caps)
    os.makedirs(probe)
    rep, r = harness(rp("game"), rp(R1_HARNESS), caps, probe, "640x360", "full")
    hashes = {name: sha_bytes(read(os.path.join(caps, name))) for name in sorted(os.listdir(caps))}
    after = git("status", "--porcelain", "--untracked-files=all")
    new_lines = sorted(set(after.splitlines()) - set(before.splitlines()))
    info = {"run": r, "capture_sha256": hashes, "git_status_unchanged": before == after,
            "game_dir_status_unchanged": not [l for l in new_lines if l[3:].startswith("game/")],
            "git_status_new_lines": sorted(set(after.splitlines()) - set(before.splitlines())),
            "errors": (rep or {}).get("errors"), "saves": (rep or {}).get("saves", {}).get("real_unchanged"),
            "battle_return": (rep or {}).get("flow", {}).get("battle_return", {}).get("equals_return_texel")}
    os.makedirs(fs(rp(OUT_REL)), exist_ok=True)
    with open(fs(out_path("main-worktree-run") + ".json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=1)
    with open(fs(out_path("main-harness-report-full") + ".json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1)
    shutil.rmtree(tmp, ignore_errors=True)
    print("main run done", r["exit"], info["git_status_unchanged"])
    return info


# ---------------------------------------------------------------------------- analyze
def load_png(name):
    return np.asarray(Image.open(rp(f"{OUT_REL}/{name}")).convert("RGBA"))


def cap_name(view):
    return f"{P}{view}_{TAG}.png"


def analyze(write):
    replay_info = json.loads(read(out_path("clean-replay-run") + ".json"))
    full = json.loads(read(out_path("clean-harness-report-full") + ".json"))
    hd = json.loads(read(out_path("clean-harness-report-v8hd") + ".json"))
    main_path = out_path("main-worktree-run") + ".json"
    main = json.loads(read(main_path)) if os.path.exists(fs(main_path)) else None
    g, info = {}, {}
    ex = replay_info["export"]
    # -- clean replay
    g["clean_export_every_head_blob_exact"] = ex["blobs"] > 0 and not ex["blob_mismatches"]
    g["clean_head_smokes_pass"] = all(v["exit"] == 0 and not v["fail_lines"] for v in replay_info["head_smokes"].values())
    g["clean_overlay_smokes_pass"] = all(v["exit"] == 0 and not v["fail_lines"] for v in replay_info["overlay_smokes"].values())
    g["overlay_matches_worktree_candidate_files"] = all(m["equals_worktree_lf"] for m in replay_info["overlay"])
    g["overlay_only_enumerated_files"] = sorted(m["path"] for m in replay_info["overlay"]) == sorted(
        [f[0] for f in overlay_files()] + [f[0] for f in tool_files()])
    g["harness_runs_exit_0"] = replay_info["harness_full_run"]["exit"] == 0 and replay_info["harness_v8hd_run"]["exit"] == 0
    g["harness_no_errors"] = not full["errors"] and not hd["errors"]
    # -- v12 reproduction from clean HEAD + overlay
    repro = replay_info["v12_reproduction"]["capture_sha256"]
    v12_out = rp(f"outputs/{V12_RUN}")
    v12_disk = {n: sha_bytes(read(os.path.join(v12_out, n))) for n in os.listdir(fs(v12_out)) if n.endswith(".png")}
    same = [n for n in repro if v12_disk.get(n) == repro[n]]
    info["v12_reproduction"] = {"captures": len(repro), "byte_identical_to_v12_outputs": len(same),
                                "differs": sorted(set(repro) - set(same))}
    g["v12_reproduces_byte_identical_from_clean_head"] = len(repro) == 12 and len(same) == 12
    # -- default runtime and v12 pass-through
    dr = full["default_runtime"]
    g["default_runtime_flags_off_equals_base"] = len(dr) == 3 and all(
        x["entry_image_equal"] and x["after_input_image_equal"] and x["positions_equal"] and x["texts_equal"]
        and x["state_equal"] and not x["selector_v12_active"] and not x["selector_r1_active"] for x in dr.values())
    vp = full["v12_passthrough"]
    g["v12_flag_only_equals_unamended_v12"] = (vp["selector_v12_active"] and not vp["selector_r1_active"] and
        vp["entry_image_equal"] and vp["after_input_image_equal"] and vp["positions_equal"] and vp["texts_equal"]
        and vp["state_equal"] and vp["spawn"] == [372.0, 246.0])
    g["cmdline_flag_enables_r1"] = full["cmdline_flag_enables_r1"] is True
    # -- camera
    curve = full["camera"]["curve"]
    g["camera_curve_godot_equals_tool"] = all(int(s) == r1_scroll_for(int(f)) for f, s, _ in curve)
    walk = rp(f"{V12_CAND}/{P}rt-walk_{V12_TAG}.png")
    mask = np.asarray(Image.open(fs(walk)).convert("RGBA"))[..., 3] > 127
    rows = sorted(set(np.nonzero(mask)[0].tolist()))
    slopes = [r1_scroll_for(f + 1) - r1_scroll_for(f) for f in range(200, 359)]
    # Continuous-curve slope (before rounding): numeric derivative of the unrounded function.
    def raw(feet):
        d = float(feet - R1["cam_start"])
        e, r, top = R1["cam_ease"], R1["cam_rate"], float(R1["scroll_max"])
        rise = 0.5 * r * e
        hold = (top - 2.0 * rise) / r
        if d <= 0:
            return 0.0
        if d < e:
            return 0.5 * r * d * d / e
        if d < e + hold:
            return rise + r * (d - e)
        if d < 2 * e + hold:
            rest = 2 * e + hold - d
            return top - 0.5 * r * rest * rest / e
        return top
    raw_slopes = [(raw(f + 0.5) - raw(f - 0.5)) for f in np.arange(200, 359, 0.5)]
    raw_accel = [abs(raw_slopes[i + 1] - raw_slopes[i]) for i in range(len(raw_slopes) - 1)]
    v12_slopes = [v12_scroll_for(f + 1) - v12_scroll_for(f) for f in range(200, 359)]
    unsafe = [f for f in rows if f - 44 - r1_scroll_for(f) + 62 < 62 or f + 3 - r1_scroll_for(f) + 62 > 317]
    info["camera"] = {"r1_max_raw_slope": round(max(raw_slopes), 3), "r1_max_slope_change_per_half_row": round(max(raw_accel), 4),
                      "v12_max_slope": max(v12_slopes), "v12_slope_jump_at_250": v12_scroll_for(251) - v12_scroll_for(250),
                      "r1_scroll_at": {str(f): r1_scroll_for(f) for f in (238, 246, 250, 258, 270, 290, 298, 310, 320, 330, 356)},
                      "v12_scroll_at": {str(f): v12_scroll_for(f) for f in (238, 246, 250, 258, 270, 290, 298, 310, 320, 330, 356)},
                      "r1_rounded_slope_values": sorted(set(slopes))}
    g["camera_curve_monotonic_no_overshoot"] = all(s >= 0 for s in slopes)
    g["camera_peak_rate_at_most_1_5"] = max(raw_slopes) <= 1.5 + 1e-9
    g["camera_rate_eases_no_instant_kink"] = max(raw_accel) <= 0.04 + 1e-9
    g["camera_every_walkable_row_keeps_canvas_in_play_band"] = not unsafe and full["probes"]["unsafe_count"] == 0
    samples = full["camera"]["samples"]
    downs = [s for s in samples if s[0] == "move_down"]
    ups = [s for s in samples if s[0] == "move_up"]
    def leg_stats(leg):
        steps = [leg[i + 1][2] - leg[i][2] for i in range(len(leg) - 1)]
        feet = [leg[i + 1][1] - leg[i][1] for i in range(len(leg) - 1)]
        screen = [s[1] - s[2] + 62 for s in leg]
        return {"frames": len(leg), "max_abs_scroll_step": max(abs(x) for x in steps) if steps else 0,
                "max_abs_feet_step": round(max(abs(x) for x in feet), 3) if feet else 0,
                "direction_reversals": sum(1 for i in range(len(steps) - 1) if steps[i] * steps[i + 1] < 0),
                "hero_screen_feet_min": round(min(screen), 1), "hero_screen_feet_max": round(max(screen), 1),
                "scroll_first_last": [leg[0][2], leg[-1][2]] if leg else []}
    info["camera"]["real_walk_south"] = leg_stats(downs)
    info["camera"]["real_walk_north"] = leg_stats(ups)
    g["camera_real_walk_smooth"] = (info["camera"]["real_walk_south"]["direction_reversals"] == 0 and
                                    info["camera"]["real_walk_north"]["direction_reversals"] == 0 and
                                    info["camera"]["real_walk_south"]["max_abs_scroll_step"] <= 4 and
                                    info["camera"]["real_walk_north"]["max_abs_scroll_step"] <= 4 and
                                    downs[-1][2] == 104 and ups[-1][2] == r1_scroll_for(ups[-1][1]))
    # -- layout sweep (every walkable foot on a 8x6 grid, two objective states)
    lay = full["layout"]
    info["layout_sweep"] = {"positions": lay["positions"], "label_hero_overlap_positions": lay["label_hero_overlaps"],
                            "pinned_glyph_counts": lay["pinned_glyphs"]}
    g["layout_no_label_overlaps_anywhere"] = lay["positions"] > 1000 and not lay["label_overlaps"]
    g["layout_no_label_over_glyph_anywhere"] = not lay["label_glyph_overlaps"]
    g["layout_labels_inside_play_band_anywhere"] = not lay["labels_outside"]
    g["layout_glyphs_whole_inside_play_band_anywhere"] = not lay["glyphs_outside"]
    # -- review captures
    flat = np.asarray(Image.open(fs(rp(V12_FLAT))).convert("RGBA"))
    cap_gates = {}
    for lang in ("zh", "en"):
        caps = full["captures"][lang]
        for view, c in caps.items():
            img = load_png(c["file"])
            p = c["probe"]
            lay_state = p["layout"]
            hero = p["hero"]
            feet, x = int(round(hero[1])), int(round(hero[0]))
            top, bottom = feet - 44 - p["scroll"] + 62, feet + 3 - p["scroll"] + 62
            key = f"{lang}:{view}"
            cap_gates[key] = {
                "size_640x360": img.shape[:2] == (360, 640),
                "hero_canvas_in_play_band": top >= 62 and bottom <= 317 and x - 16 >= 0 and x + 15 <= 639,
                "no_label_overlap": not lay_state["label_overlaps"],
                "no_label_over_glyph": not lay_state["label_glyph_overlaps"],
                "no_label_over_hero": not lay_state["label_hero_overlaps"],
                "labels_in_band": not lay_state["labels_outside_band"],
                "glyphs_whole_in_band": not lay_state["glyphs_outside_band"],
                "hint_left_of_save": p["hint_end_x"] <= p["save_x"],
                "scroll": p["scroll"],
            }
            if view in ("entry",):
                d = DOME
                region = img[d["top"] + 62 - p["scroll"]:d["bottom"] + 63 - p["scroll"], d["left"]:d["right"] + 1, :3]
                art = flat[d["top"]:d["bottom"] + 1, d["left"]:d["right"] + 1, :3]
                cap_gates[key]["dome_pixel_exact"] = p["scroll"] == 0 and region.shape == art.shape and bool((region == art).all())
    info["captures"] = cap_gates
    g["captures_all_640x360"] = all(v["size_640x360"] for v in cap_gates.values())
    g["captures_hero_canvas_in_play_band"] = all(v["hero_canvas_in_play_band"] for v in cap_gates.values())
    g["captures_no_label_overlap"] = all(v["no_label_overlap"] for v in cap_gates.values())
    g["captures_no_label_over_glyph"] = all(v["no_label_over_glyph"] for v in cap_gates.values())
    g["captures_no_label_over_hero"] = all(v["no_label_over_hero"] for v in cap_gates.values())
    g["captures_labels_and_glyphs_in_band"] = all(v["labels_in_band"] and v["glyphs_whole_in_band"] for v in cap_gates.values())
    g["captures_hint_left_of_save"] = all(v["hint_left_of_save"] for v in cap_gates.values())
    g["entry_dome_pixel_exact_zh_en"] = cap_gates["zh:entry"].get("dome_pixel_exact") and cap_gates["en:entry"].get("dome_pixel_exact")
    for lang in ("zh", "en"):
        pb = full["captures"][lang]["patrol_bypass"]["probe"]["layout"]
        names = {l["name"] for l in pb["labels"]}
        info.setdefault("patrol_bypass_labels", {})[lang] = {l["name"]: l["screen"] for l in pb["labels"]}
        info.setdefault("patrol_bypass_glyphs", {})[lang] = {gl["key"]: gl["screen"] for gl in pb["glyphs"]}
    g["patrol_bypass_view_scrolled_enemy_label_and_bypass_glyph_clear"] = all(
        full["captures"][lang]["patrol_bypass"]["probe"]["scroll"] >= 90 and
        "enemy" in {l["name"] for l in full["captures"][lang]["patrol_bypass"]["probe"]["layout"]["labels"]} and
        "bypass" in {gl["key"] for gl in full["captures"][lang]["patrol_bypass"]["probe"]["layout"]["glyphs"]}
        for lang in ("zh", "en"))
    g["records_prompt_glyph_and_label_shown"] = all(
        "records" in {gl["key"] for gl in full["captures"][lang]["interaction_prompt"]["probe"]["layout"]["glyphs"]} and
        "records" in {l["name"] for l in full["captures"][lang]["interaction_prompt"]["probe"]["layout"]["labels"]} and
        full["captures"][lang]["interaction"]["probe"]["ji_records_checked"] for lang in ("zh", "en"))
    # -- v8 reference pair (640x360 and 1280x720 window)
    v8 = {}
    for prefix, rep, scale in (("rt640", full, 1), ("rt1280", hd, 2)):
        for lang in ("zh", "en"):
            entry = rep["captures"][f"{prefix}_{lang}_v8ref"]
            on, off = load_png(entry["on"]["file"]), load_png(entry["off"]["file"])
            diff = np.any(on[..., :3] != off[..., :3], axis=2)
            ys, xs = np.nonzero(diff)
            v8[f"{prefix}:{lang}"] = {"size": [on.shape[1], on.shape[0]], "diff_pixels": int(diff.sum()),
                                      "bbox_rows": [int(ys.min()), int(ys.max())] if len(ys) else None,
                                      "bbox_cols": [int(xs.min()), int(xs.max())] if len(xs) else None,
                                      "opaque_height_px": int(ys.max() - ys.min() + 1) if len(ys) else 0,
                                      "logical_height": (int(ys.max() - ys.min() + 1) / scale) if len(ys) else 0,
                                      "hero_feet": entry["hero_feet"], "scroll": entry["probe"]["scroll"]}
    info["v8_reference"] = v8
    g["v8_reference_pair_exactly_48_logical_rows"] = all(v["logical_height"] == 48 for v in v8.values())
    g["v8_reference_bottom_row_level_with_runtime_feet"] = all(
        v["bbox_rows"] and v["bbox_rows"][1] == (int(v["hero_feet"][1]) - v["scroll"] + 62) * (2 if k.startswith("rt1280") else 1)
        + (1 if k.startswith("rt1280") else 0) for k, v in v8.items())
    g["v8_reference_png_is_approved_hash"] = sha_bytes(read(rp(V8_PNG))) == V8_SHA
    # -- flow, battle and return
    fl = full["flow"]
    g["flow_enter_via_world_map_r1_active"] = fl["enter"]["r1_active"] and fl["enter"]["hero"] == [372.0, 238.0] and fl["enter"]["scroll"] == 0
    g["flow_objectives_by_real_input"] = (fl["records"]["ji_records_checked"] and fl["npc"]["dialogue_opened"] and fl["npc"]["recruited"]
        and fl["trace0"]["recorded"] and fl["trace1"]["recorded"] and fl["assist"]["insight"] and fl["bypass"]["bypass_reached"]
        and fl["bypass"]["battle_not_started"] and all(fl[k]["walk"]["ok"] for k in ("records", "npc", "trace0", "trace1", "assist", "bypass")))
    g["flow_survey_annex_round_trip"] = (fl["survey"]["annex_scene"] == "res://scenes/survey_annex.tscn" and
                                         fl["survey"]["returned_r1_active"])
    s = fl["sentry"]
    g["battle_real_handoff"] = s["battle_scene"] == "res://scenes/battle_arena.tscn" and s["battle_enemy"] == "sentry"
    g["battle_won_through_battle_outcome_path"] = (s.get("auto_mode_by_input") and s.get("battle_finished") and s.get("battle_won")
        and s.get("enemy_hp_end") == 0 and s["flags_after_finish"]["returning_from_battle"]
        and s["flags_after_finish"]["enemy_cleared_for_return"] and s.get("result_button_focused"))
    br = fl["battle_return"]
    g["battle_return_via_result_button_restores_position_and_camera"] = (
        br["scene_after_result"] == "res://scenes/scifi_exploration_area.tscn" and not br["via_growth_screen"]
        and br.get("r1_active") and br.get("equals_return_texel") and br.get("walkable")
        and br.get("scroll") == br.get("expected_scroll") and br.get("camera_current")
        and br.get("camera_y") == br.get("scroll") - 62 and br.get("enemy_visible") is False and br.get("returning_flag_consumed"))
    g["battle_return_layout_clean"] = (not br["layout"]["label_overlaps"] and not br["layout"]["label_glyph_overlaps"]
                                       and not br["layout"]["glyphs_outside_band"] and not br["layout"]["labels_outside_band"])
    g["world_map_exit"] = fl.get("world_map", {}).get("scene") == "res://scenes/scifi_world_map.tscn"
    fm, sm = full["flow_monitor"], full["sweep_monitor"]
    info["monitors"] = {"flow": {k: fm[k] for k in fm if k not in ("nonwalkable", "outside_view")},
                        "sweep": {k: sm[k] for k in sm if k not in ("nonwalkable", "outside_view")}}
    g["flow_and_sweeps_walkable_and_in_band"] = (not fm["nonwalkable"] and not fm["outside_view"] and not sm["nonwalkable"]
        and not sm["outside_view"] and fm["frames"] > 500 and fm["max_scroll_step"] <= 4 and sm["max_scroll_step"] <= 4)
    g["sweeps_end_walkable"] = all(x["walkable"] and x["scene_unchanged"] for x in full["sweeps"])
    g["mask_runtime_equals_png"] = full["probes"]["mask_mismatch"] == 0
    g["spawn_r1_scroll_0"] = full["probes"]["spawn"] == [372.0, 238.0] and full["probes"]["spawn_scroll"] == 0
    # -- saves and side effects
    g["real_user_saves_unchanged"] = full["saves"]["real_unchanged"] and hd["saves"]["real_unchanged"]
    if main:
        g["main_worktree_run_ok"] = main["run"]["exit"] == 0 and not main["errors"] and main["saves"] and main["battle_return"]
        g["main_worktree_run_left_no_game_side_effects"] = main["game_dir_status_unchanged"]
        clean_caps = replay_info["captures"]
        # The battle-return frame depends on where real-time stepping ends the walk into the sentry (sub-pixel,
        # frame-timing dependent), so it is compared by state (own return texel + expected scroll), not bytes.
        shared = [n for n in main["capture_sha256"] if n in clean_caps and "battle-return" not in n]
        info["clean_vs_main_capture_equal"] = {"compared": len(shared),
                                               "equal": sum(1 for n in shared if clean_caps[n] == main["capture_sha256"][n]),
                                               "differs": [n for n in shared if clean_caps[n] != main["capture_sha256"][n]]}
        g["clean_and_main_captures_byte_identical"] = len(shared) >= 15 and not info["clean_vs_main_capture_equal"]["differs"]
    passed = sum(1 for v in g.values() if v)
    report = {"candidate": RUN, "status": "UNAPPROVED technical integration fixes; art not accepted; opt-in only",
              "generated": time.strftime("%Y-%m-%d %H:%M:%S"), "passed": passed, "total": len(g),
              "verdict": "PASS" if passed == len(g) else "FAIL", "gates": g, "info": info,
              "clean_export": {k: ex[k] for k in ("head", "game_tree", "blobs", "longest_path")},
              "overlay_manifest": replay_info["overlay"], "capture_sha256": replay_info["captures"],
              "v12_reproduction_capture_sha256": repro,
              "smokes": {"head": replay_info["head_smokes"], "overlay": replay_info["overlay_smokes"]},
              "counters_unchanged": {"meter": "40.8%", "m2": "10/12", "scenes": "3/12", "sprites": "0/52", "playtests": "0/2"}}
    for k, v in g.items():
        print(("PASS " if v else "FAIL ") + k)
    print(f"{report['verdict']} {passed}/{len(g)}")
    if write:
        with open(fs(out_path("technical-check-report") + ".json"), "w", encoding="utf-8") as f:
            json.dump(report, f, indent=1)
    return report


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "analyze"
    if mode in ("replay", "all"):
        replay()
    if mode in ("main", "all"):
        main_run()
    if mode in ("analyze", "all"):
        analyze("--write-report" in sys.argv or mode == "all")
