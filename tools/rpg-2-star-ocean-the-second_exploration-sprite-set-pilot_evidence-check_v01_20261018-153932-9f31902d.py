"""Runs and checks every piece of evidence for the exploration sprite set pilot (code.runtime.character-sprite-pipeline).

Capability only: the TEST-ONLY diagnostic fixtures are not art, nothing is approved or made default, and the
captures prove which frame the normal runtime selected and drew, not smooth motion or character design.

Steps (all Godot runs use an isolated APPDATA/LOCALAPPDATA under %TEMP%, so real saves and settings are untouched):
  1. fixture builder --check (byte-identical rebuild of the 55 fixture files)
  2. export the base commit's game/ (git archive, pre-pilot origin/main) to %TEMP% and import it
  3. Godot logic check (flag off/default registry/actor ids/cache/malformed/partial/timing/transitions)
  4. Godot gameplay check with the pilot CLI flags + fixture registry at --fixed-fps 60 and 30 (every rendered
     frame verified), then bilingual 640x360, density 1280x720 and motion 1280x720 capture runs
  5. default-render parity captures: base tree, base tree again (noise), branch flag off, branch flag on with the
     shipped (empty) registry
  6. the existing accepted-rooms replay (read-only) on the branch flag off / flag on / flag on + fixture registry,
     compared with the eight acceptance-record images
Then writes the report JSON and copies the selected evidence (bilingual + density captures, motion APNG) to
outputs/spriteset-pilot-9f31902d/.
Usage: python -I <this file> [--godot <console exe>] [--base <commit>]
"""
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261018-153932-9f31902d"
SLUG = "rpg-2-star-ocean-the-second"
BASE_COMMIT = "3e040a9ae3bd410d8fab4b0921bcb63e8bb3c9b7"
TOOLS = ROOT / "tools"
BUILDER = TOOLS / f"{SLUG}_exploration-sprite-set-pilot_diagnostic-fixture-build_test-only-v01_{STAMP}.py"
LOGIC = TOOLS / f"{SLUG}_exploration-sprite-set-pilot_godot-logic-check_v01_{STAMP}.gd"
GAMEPLAY = TOOLS / f"{SLUG}_exploration-sprite-set-pilot_godot-gameplay-check_v01_{STAMP}.gd"
PARITY = TOOLS / f"{SLUG}_exploration-sprite-set-pilot_default-parity-capture_v01_{STAMP}.gd"
REPLAY = TOOLS / f"{SLUG}_wdc-annex-room1_v02-review-gate-accepted-rooms-replay_check-v01_20261017-172907-03286bf3.gd"
REGISTRY = f"res://tests/fixtures/spriteset-diag-test-only-9f31902d/{SLUG}_spriteset-diag_fixture-registry_{STAMP}.json"
FLAG = "--exploration-sprite-set-pilot"
OUT_REL = "outputs/spriteset-pilot-9f31902d"
ACCEPTED = {  # acceptance-record images of the three creator-accepted rooms (same table as the replay's own checks)
    "nyc-public-facilities-room1_existing-scene-godot-%s-640x360-review-v01": ("outputs/room1-visual-review", "20261017-011400-d3590c0a", ("zh", "en")),
    "nyc-public-facilities-room2_three-pixel-fixtures-godot-%s-640x360_unapproved-v01": ("outputs/room2-fixtures-pilot", "20261017-010418-6b3138d8", ("zh", "en")),
    "nyc-public-facilities-room2_repair-manual-approach-godot-%s-640x360_unapproved-v01": ("outputs/room2-fixtures-pilot", "20261017-010418-6b3138d8", ("zh",)),
    "nyc-public-facilities-room2_repair-manual-interaction-godot-%s-640x360_unapproved-v01": ("outputs/room2-fixtures-pilot", "20261017-010418-6b3138d8", ("zh",)),
    "yonkers-maintenance-room2_four-pixel-fixtures-godot-%s-640x360-review-v01": ("outputs/yonkers-room2-visual-review", "20261017-011814-94cebca4", ("zh", "en")),
}


def long_path(p):
    """Windows extended-length path so >260-char acceptance records still open."""
    p = os.path.abspath(p)
    return "\\\\?\\" + p if os.name == "nt" and not p.startswith("\\\\?\\") else p


def rgba(p):
    with Image.open(long_path(p)) as im:
        return np.array(im.convert("RGBA"))


def sha(p):
    return hashlib.sha256(Path(long_path(p)).read_bytes()).hexdigest()


def hash_entry(rel):
    data = Path(long_path(ROOT / rel)).read_bytes()
    if rel.endswith(".png"):
        return {"file": rel, "hash_algorithm": "sha256-bytes", "sha256": hashlib.sha256(data).hexdigest()}
    return {"file": rel, "hash_algorithm": "sha256-text-lf-v1", "sha256": hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()}


CODE_FILES = [
    "game/scripts/exploration_sprite_set_pilot.gd", "game/scripts/exploration_sprite_set_pilot.gd.uid",
    "game/scripts/scifi_exploration_area.gd", "game/scripts/survey_annex.gd",
    f"game/scripts/{SLUG}_chicago-loop_state-lake-block-scene_unapproved-v02_20261017-160959-55667f46.gd",
    f"game/data/exploration-sprite-sets/{SLUG}_exploration-sprite-set-registry_no-approved-sets-v01_{STAMP}.json",
]


def godot_default():
    for cand in (ROOT / "work/tooling", ROOT.parent / "tooling"):
        exe = cand / "godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe"
        if exe.is_file():
            return str(exe)
    return ""


class Runner:
    def __init__(self, godot, tmp):
        self.godot = godot
        self.tmp = Path(tmp)
        self.env = dict(os.environ)
        for key, sub in (("APPDATA", "Roaming"), ("LOCALAPPDATA", "Local")):
            (self.tmp / "appdata" / sub).mkdir(parents=True, exist_ok=True)
            self.env[key] = str(self.tmp / "appdata" / sub)
        self.runs = {}

    def run(self, name, game_dir, args, timeout=900):
        log = self.tmp / f"{name}.log"
        cmd = [self.godot, "--path", str(game_dir)] + args
        with open(log, "w", encoding="utf-8", errors="replace") as fh:
            proc = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, env=self.env, timeout=timeout)
        text = log.read_text(encoding="utf-8", errors="replace")
        self.runs[name] = {"exit": proc.returncode, "args": [x for x in args if not os.path.isabs(x)], "script_errors": text.count("SCRIPT ERROR")}
        return proc.returncode, text


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT)] + list(args), capture_output=True, text=True, check=True).stdout


def export_base(commit, dest):
    dest.mkdir(parents=True, exist_ok=True)
    archive = dest / "base.tar"
    with open(archive, "wb") as fh:
        subprocess.run(["git", "-C", str(ROOT), "archive", commit, "game"], stdout=fh, check=True)
    with tarfile.open(archive) as tar:
        # Extract by hand through extended-length paths (some asset paths pass 260 chars under %TEMP%).
        for member in tar.getmembers():
            target = long_path(os.path.join(dest, *member.name.split("/")))
            if member.isdir():
                os.makedirs(target, exist_ok=True)
            elif member.isfile() and ".." not in member.name.split("/"):
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with tar.extractfile(member) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
    archive.unlink()
    return dest / "game"


DURATIONS = {"protagonist-female": {"idle": [470, 410], "walk": [130] * 4}, "protagonist-male": {"idle": [500, 350], "walk": [150] * 4}}


def analytic(actor, action, clock_us):
    ends = np.cumsum(DURATIONS[actor][action]) * 1000
    return int(np.searchsorted(ends, clock_us % ends[-1], side="right")), ends


def near_boundary(actor, action, clock_us):
    ends = np.concatenate([[0], np.cumsum(DURATIONS[actor][action]) * 1000])
    c = clock_us % ends[-1]
    return bool(np.min(np.abs(ends - c)) < 1000)


def timeline_compare(r60, r30):
    """Cadence is a function of time since the last (action, facing) change, i.e. the pilot clock, which integrates the
    real frame deltas. (a) In each run every rendered tick shows the analytic frame for its clock. (b) Across runs, ticks
    with the same clock (within 1 microsecond) of the same leg show the same frame, including boundaries. (c) Each leg ends on the same position at 30 and 60 fps. The state change itself is seen on the first
    frame after the input changes, so it lands 1/30 s or 1/60 s after the press; that input-sampling step is not cadence."""
    out = {}
    for s60, s30 in zip(r60["scenes"], r30["scenes"]):
        assert s60["scene"] == s30["scene"] and s60["actor"] == s30["actor"]
        actor = s60["actor"]
        row = {"ticks_60": len(s60["ticks"]), "ticks_30": len(s30["ticks"])}
        for tag, s in (("60", s60), ("30", s30)):
            row[f"analytic_mismatch_{tag}"] = sum(1 for t in s["ticks"] if analytic(actor, t["action"], t["clock_us"])[0] != t["frame"])
        legs60 = {}
        for t in s60["ticks"]:
            legs60.setdefault(t["leg"], []).append(t)
        compared = skipped = mismatched = 0
        for t in s30["ticks"]:
            same = [u for u in legs60.get(t["leg"], []) if u["action"] == t["action"] and u["facing"] == t["facing"] and abs(u["clock_us"] - t["clock_us"]) <= 1]
            if not same:
                continue
            u = same[0]
            compared += 1
            mismatched += u["frame"] != t["frame"]
        row.update({"equal_clock_compared": compared, "boundary_samples_skipped": 0, "equal_clock_mismatched": mismatched})
        ends = {}
        for tag, s in (("60", s60), ("30", s30)):
            for t in s["ticks"]:
                ends.setdefault(t["leg"], {})[tag] = (t["x"], t["y"])
        row["max_leg_end_position_diff_px"] = round(max(max(abs(v["60"][0] - v["30"][0]), abs(v["60"][1] - v["30"][1])) for v in ends.values()), 4)
        out[s60["scene"]] = row
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--godot", default=godot_default())
    ap.add_argument("--base", default=BASE_COMMIT)
    ap.add_argument("--keep", default="")
    a = ap.parse_args()
    tmp = Path(a.keep) if a.keep else Path(tempfile.mkdtemp(prefix="ssp9f-"))
    tmp.mkdir(parents=True, exist_ok=True)
    game = ROOT / "game"
    r = Runner(a.godot, tmp)
    gates, notes = {}, {}

    spec = importlib.util.spec_from_file_location("ssp_fixture_builder", BUILDER)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    built = builder.build()
    mism = [f for f, data in built.items() if not (builder.OUT / f).is_file() or (builder.OUT / f).read_bytes() != data]
    gates["G01_fixtures_rebuild_byte_identical"] = not mism and len(built) == 55
    notes["fixture_files"] = len(built)

    base_game = export_base(a.base, tmp / "base")
    for name, path in (("import-branch", game), ("import-base", base_game)):
        r.run(name, path, ["--headless", "--import"])
    # Snapshot after the imports: an import may rewrite tracked .import sidecars (line endings only); the
    # gate below is about the logic, gameplay, parity and replay runs themselves.
    tracked_before = git("status", "--porcelain", "--untracked-files=no", "--", "game")

    logic_json = tmp / "logic.json"
    code, _ = r.run("logic", game, ["-s", str(LOGIC), "--", str(logic_json)])
    logic = json.loads(logic_json.read_text(encoding="utf-8")) if logic_json.is_file() else {"passed": 0, "total": -1, "checks": []}
    gates["G02_logic_checks_all_pass"] = code == 0 and logic["passed"] == logic["total"] == 12
    notes["logic"] = [{"check": c["check"], "ok": c["ok"]} for c in logic["checks"]]

    plays = {}
    for tag, fps, width, mode in (("fps60", 60, "640", "none"), ("fps30", 30, "640", "none"), ("bilingual", 60, "640", "bilingual"),
                                  ("density", 60, "1280", "density"), ("motion", 30, "1280", "motion")):
        out = tmp / f"play-{tag}"
        shutil.rmtree(out, ignore_errors=True)
        code, _ = r.run(f"play-{tag}", game, ["--fixed-fps", str(fps), "-s", str(GAMEPLAY), "--", str(out), tag, width, mode, str(fps),
                                               FLAG, "--exploration-sprite-set-registry=" + REGISTRY])
        rep = next(out.glob("*gameplay-*-report_*.json"), None)
        plays[tag] = {"exit": code, "report": json.loads(rep.read_text(encoding="utf-8")) if rep else None, "dir": out}
    for tag in ("fps60", "fps30"):
        rep = plays[tag]["report"] or {"failures": ["no report"], "seen": {}, "scenes": []}
        scripts = sorted({s["script"].rsplit("/", 1)[-1] for s in rep["scenes"]})
        gates[f"G03_{tag}_every_rendered_frame_verified_48_states"] = plays[tag]["exit"] == 0 and not rep["failures"] and len(rep["seen"]) == 48 \
            and len(rep["scenes"]) == 6 and all(s["verified"] == len(s["ticks"]) for s in rep["scenes"]) and rep.get("pilot_enabled_by_cli")
        notes[f"{tag}_scenes"] = [{"scene": s["scene"], "actor": s["actor"], "ticks": len(s["ticks"]), "verified": s["verified"],
                                   "script": s["script"].rsplit("/", 1)[-1], "hero_scale": s["hero_scale"], "hero_offset": s["hero_offset"]} for s in rep["scenes"]]
        notes[f"{tag}_texture_loads_manifest_reads"] = [rep.get("texture_loads"), rep.get("manifest_reads")]
        notes[f"{tag}_host_scripts"] = scripts
    if plays["fps60"]["report"] and plays["fps30"]["report"]:
        tc = timeline_compare(plays["fps60"]["report"], plays["fps30"]["report"])
        gates["G04_cadence_is_time_based_at_30_and_60_fps"] = all(v["analytic_mismatch_60"] == 0 and v["analytic_mismatch_30"] == 0 and v["equal_clock_mismatched"] == 0
                                                                 and v["equal_clock_compared"] > 100 and v["max_leg_end_position_diff_px"] < 0.01 for v in tc.values())
        notes["fps_timeline_compare"] = tc

    captures = {}
    for tag in ("bilingual", "density"):
        rep = plays[tag]["report"] or {"failures": ["no report"], "captures": []}
        ok = plays[tag]["exit"] == 0 and not rep["failures"] and all(c["verified"] for c in rep["captures"])
        size = (640, 360) if tag == "bilingual" else (1280, 720)
        files = [plays[tag]["dir"] / c["file"] for c in rep["captures"]]
        ok = ok and all(f.is_file() and Image.open(f).size == size for f in files)
        want = 12 if tag == "bilingual" else 2
        gates[f"G05_{tag}_captures_{want}_verified"] = ok and len(files) == want
        captures[tag] = rep["captures"]
    mrep = plays["motion"]["report"] or {"failures": ["no report"], "captures": []}
    mframes = sorted(plays["motion"]["dir"].glob("*_motion-frame-*.png"))
    gates["G06_motion_frames_30_verified"] = plays["motion"]["exit"] == 0 and not mrep["failures"] and len(mframes) == 30

    parity = {}
    for tag, path, extra in (("base", base_game, []), ("base-repeat", base_game, []), ("branch-flag-off", game, []), ("branch-flag-default-registry", game, [FLAG])):
        out = tmp / f"parity-{tag}"
        shutil.rmtree(out, ignore_errors=True)
        code, _ = r.run(f"parity-{tag}", path, ["--fixed-fps", "60", "-s", str(PARITY), "--", str(out)] + extra)
        parity[tag] = {"exit": code, "files": sorted(p.name for p in out.glob("*.png")), "dir": out}
    names = parity["base"]["files"]
    diffs = {}
    for tag in ("base-repeat", "branch-flag-off", "branch-flag-default-registry"):
        d = {}
        for n in names:
            other = parity[tag]["dir"] / n
            d[n] = int((rgba(parity["base"]["dir"] / n) != rgba(other)).any(axis=2).sum()) if other.is_file() else "missing"
        diffs[tag] = {"files": len(d), "differing": {k: v for k, v in d.items() if v != 0}}
    moved = {}
    for n in names:
        if "_entry-zh" in n:
            walk = n.replace("_entry-zh", "_walk-east-zh")
            moved[n.split("_parity_")[1].split("_")[0]] = int((rgba(parity["base"]["dir"] / n) != rgba(parity["base"]["dir"] / walk)).any(axis=2).sum())
    gates["G07_default_render_pixel_identical_to_base"] = len(names) == 45 and all(p["exit"] == 0 for p in parity.values()) \
        and all(v["files"] == 45 and not v["differing"] for v in diffs.values())
    gates["G08_parity_walks_really_moved_the_hero"] = len(moved) == 9 and all(v > 0 for v in moved.values())
    notes["parity"] = diffs
    notes["parity_entry_vs_walk_changed_pixels"] = moved

    accepted = {}
    for tag, extra in (("flag-off", []), ("flag-default-registry", [FLAG]), ("flag-fixture-registry", [FLAG, "--exploration-sprite-set-registry=" + REGISTRY])):
        out = tmp / f"accepted-{tag}"
        shutil.rmtree(out, ignore_errors=True)
        code, text = r.run(f"accepted-{tag}", game, ["-s", str(REPLAY), "--", str(out), f"ssp-{tag}"] + extra)
        res = {}
        for name, (sub, stamp, langs) in ACCEPTED.items():
            for lang in langs:
                n = name % lang
                ref = ROOT / sub / f"{SLUG}_{n}_{stamp}.png"
                got = next(out.glob(f"{SLUG}_{n}_*.png"), None)
                res[n] = int((rgba(ref) != rgba(got)).any(axis=2).sum()) if got and os.path.isfile(long_path(ref)) else "missing"
        accepted[tag] = {"exit": code, "all_ok_marker": "ACCEPTED_REPLAY_ALL_OK" in text, "differing_pixels": res}
    gates["G09_eight_accepted_rooms_byte_identical"] = all(v["exit"] == 0 and v["all_ok_marker"] and len(v["differing_pixels"]) == 8
                                                          and all(x == 0 for x in v["differing_pixels"].values()) for v in accepted.values())
    notes["accepted_rooms"] = accepted

    gates["G10_no_tracked_game_file_written_by_the_runs"] = git("status", "--porcelain", "--untracked-files=no", "--", "game") == tracked_before

    gates["G11_no_script_errors"] = all(v["script_errors"] == 0 and v["exit"] == 0 for v in r.runs.values())

    # Selected evidence -> outputs/.
    out_dir = ROOT / OUT_REL
    out_dir.mkdir(parents=True, exist_ok=True)
    evidence = []
    for tag in ("bilingual", "density"):
        for c in captures.get(tag, []):
            src = plays[tag]["dir"] / c["file"]
            shutil.copyfile(src, long_path(out_dir / c["file"]))
            evidence.append({"file": f"{OUT_REL}/{c['file']}", "sha256": sha(out_dir / c["file"]), "scene": c["scene"], "language": c["language"],
                             "drawn_state": {k: c["state"][k] for k in ("actor_id", "action", "facing", "frame")}, "hero_feet": c["hero"], "verified_on_screen": c["verified"]})
    motion_name = f"{SLUG}_spriteset-pilot_city_walk-stop-motion-30fps-1280x720_test-only_{STAMP}.png"
    if mframes:
        frames = [Image.open(f).convert("RGB") for f in mframes]
        frames[0].save(long_path(out_dir / motion_name), format="PNG", save_all=True, append_images=frames[1:], duration=[33, 33, 34] * 10, loop=0)
        with Image.open(long_path(out_dir / motion_name)) as apng:
            stored = apng.n_frames
        evidence.append({"file": f"{OUT_REL}/{motion_name}", "sha256": sha(out_dir / motion_name),
                         "kind": "animated PNG (APNG), 30 real rendered frames (1.0 s) at --fixed-fps 30, 1280x720 window, 1:1; the encoder stores "
                                 f"{stored} frames because identical consecutive frames are merged with their durations summed",
                         "states": [{k: c["state"][k] for k in ("action", "facing", "frame")} | {"tick": c["tick"]} for c in mrep["captures"]]})
    report = {
        "task": "code.runtime.character-sprite-pipeline",
        "status": "capability evidence only; fixtures are TEST-ONLY diagnostics (not art, not approved, never default); no smooth-motion or design claim",
        "base_commit": a.base, "head": git("rev-parse", "HEAD").strip(), "godot": Path(a.godot).name,
        "gates": gates, "passed": sum(1 for v in gates.values() if v), "total": len(gates),
        "notes": notes, "runs": r.runs, "evidence": evidence,
        "files": [hash_entry(f) for f in CODE_FILES]
                 + [hash_entry(f"tools/{p.name}") for p in (BUILDER, LOGIC, GAMEPLAY, PARITY, Path(__file__))]
                 + [hash_entry(f"{builder.DIR_REL}/{f}") for f in sorted(built)]
                 + [hash_entry(f"{builder.DIR_REL}/{f}.import") for f in sorted(built) if f.endswith(".png")],
    }
    rep_path = out_dir / f"{SLUG}_spriteset-pilot_evidence-report_{STAMP}.json"
    rep_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"gates": gates, "passed": report["passed"], "total": report["total"], "tmp": str(tmp)}, indent=1))
    sys.exit(0 if report["passed"] == report["total"] else 1)


if __name__ == "__main__":
    main()
