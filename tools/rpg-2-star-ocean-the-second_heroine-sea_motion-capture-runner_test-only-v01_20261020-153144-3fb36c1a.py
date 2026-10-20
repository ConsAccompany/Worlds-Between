"""Run the staged heroine-sea partial-pilot motion capture and write source-bound evidence.

TEST-ONLY. Reads the sibling cl-motion manifest/pose PNGs, runs the bounded checked
runner twice (EN 30 fps bright outskirts, ZH 60 fps dark default) plus one real
_try_attack probe, verifies the frozen-state baseline/injection/restore, encodes
H.264/yuv420p MP4s from the real viewport PNGs, and writes a report.

No game/source/ledger/index edit, no provider/auth/credit action, no download.
Usage: python -I <this>
"""
import glob
import hashlib
import importlib.util
import json
import os
import shutil
import struct
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT.parents[2]
CL = PRIMARY / "work/dual05/cl-motion"
MANIFEST = CL / "outputs/hero-sea-motion-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_manifest_test-only-v01_20261020-192028-7e93a93c.json"
AUTHOR = CL / "tools/rpg-2-star-ocean-the-second_heroine-sea_combat-motion-author_test-only-v01_20261020-192028-9bab493d.py"
GODOT = PRIMARY / "work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe"
CHECKED = ROOT / "tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py"
HARNESS = ROOT / "tools/rpg-2-star-ocean-the-second_heroine-sea_motion-capture_test-only-v01_20261020-153144-3fb36c1a.gd"
OUT = ROOT / "outputs/hero-sea-motion-capture-v01"
STAMP = "v01_20261020-153144-3fb36c1a"
SLUG = "rpg-2-star-ocean-the-second_heroine-sea-motion"
ARENA = ROOT / "game/scripts/battle_arena.gd"
PROJECT = ROOT / "game/project.godot"
ARENA_SHA = "41548c86eb04fb12a988c211373601f7c08d579b408d4951aa6d0f03302cb197"
BASE_SHA = "4ce65a7915c0c0270a4ca353152b45b7d68b42672cb1483dd4f3e9cf4ac9d5e6"
CRITICAL_TICKS = {"base": 0, "anticipation": 62, "contact": 65, "recovery": 69}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha_text_lf(p):
    text = Path(p).read_text(encoding="utf-8")
    return hashlib.sha256(text.replace("\r\n", "\n").replace("\r", "\n").encode()).hexdigest()


def png_size(p):
    data = Path(p).read_bytes()[:33]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"not a PNG: {p}")
    return struct.unpack(">II", data[16:24])


def find_ffmpeg():
    for key in ("HSEA_FFMPEG", "IMAGEIO_FFMPEG_EXE"):
        if os.environ.get(key) and Path(os.environ[key]).is_file():
            return Path(os.environ[key])
    try:
        spec = importlib.util.find_spec("imageio_ffmpeg")
        if spec is not None:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            p = Path(mod.get_ffmpeg_exe())
            if p.is_file():
                return p
    except Exception:
        pass
    p = shutil.which("ffmpeg")
    if p:
        return Path(p)
    hits = glob.glob(str(Path.home() / "AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg*/**/bin/ffmpeg.exe"), recursive=True)
    if hits:
        return Path(hits[0])
    raise SystemExit("READY_BUT_BLOCKED: no installed bundled imageio_ffmpeg/ffmpeg found; no download attempted")


def ffprobe_for(ffmpeg):
    p = Path(ffmpeg).with_name("ffprobe.exe")
    if p.is_file():
        return p
    q = shutil.which("ffprobe")
    if q:
        return Path(q)
    raise SystemExit("ffprobe missing next to installed ffmpeg; cannot verify encoded MP4")


def load_inputs():
    assert AUTHOR.is_file(), f"missing author tool {AUTHOR}"
    assert MANIFEST.is_file(), f"missing manifest {MANIFEST}"
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected_author = manifest["source"]["sha256TextLf"]
    actual_author = sha_text_lf(AUTHOR)
    assert actual_author == expected_author, f"author tool LF text hash {actual_author} != manifest {expected_author}"
    assert manifest["poseFiles"]["base"]["sha256"] == BASE_SHA
    base_path = CL / manifest["poseFiles"]["base"]["path"]
    assert base_path.is_file() and sha(base_path) == BASE_SHA, "approved base source missing or changed"
    pose_paths = {}
    for pid, entry in manifest["poseFiles"].items():
        p = CL / entry["path"] if entry.get("path") else MANIFEST.parent / entry["name"]
        assert p.is_file(), f"missing pose {pid}: {p}"
        assert sha(p) == entry["sha256"], f"pose hash mismatch {pid}"
        assert png_size(p) == (136, 144), f"pose not 136x144 native {pid}: {png_size(p)}"
        pose_paths[pid] = p
    assert manifest["cell"] == [136, 144] and manifest["logicalExtent"] == [68, 72]
    assert manifest["pinNative"] == [64, 136] and manifest["pinLogical"] == [32, 68]
    assert manifest["clips"]["idle"]["total_ticks"] == 28 and manifest["clips"]["attack"]["total_ticks"] == 12
    assert manifest["clips"]["attack"]["then"] == "base"
    assert abs(float(manifest["stagedContact"]["start_s"]) - 0.166667) < 1e-6
    assert manifest["hitSynchronized"] is False
    assert sha(ARENA) == ARENA_SHA, "raw current arena SHA changed"
    return manifest, base_path, pose_paths


def rel(p):
    try:
        return Path(p).relative_to(ROOT).as_posix()
    except ValueError:
        return Path(p).relative_to(PRIMARY).as_posix()


def status_snapshot():
    tracked = [ARENA, PROJECT, CHECKED, HARNESS, AUTHOR, MANIFEST]
    return {rel(p): sha(p) for p in tracked}


def run_checked(rule, user_args, env):
    log = OUT / f"log-{rule}_{STAMP}.txt"
    cmd = [sys.executable, "-I", str(CHECKED), "--timeout", "90", "--expect", "HSEA_MOTION_CAPTURE_OK",
           "--log", str(log), "--", str(GODOT), "--path", str(ROOT / "game"), "--resolution", "1280x720",
           "--position", "2000,100", "--audio-driver", "Dummy", "--log-file", str(OUT / f"godot-{rule}_{STAMP}.log"),
           "--script", str(HARNESS), "--"] + [str(x) for x in user_args]
    started = datetime.now()
    run = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    (OUT / f"runner-{rule}-stdout_{STAMP}.log").write_text(run.stdout, encoding="utf-8", newline="\n")
    (OUT / f"runner-{rule}-stderr_{STAMP}.log").write_text(run.stderr, encoding="utf-8", newline="\n")
    rec = {"rule": rule, "command": cmd, "exit": run.returncode, "seconds": round((datetime.now() - started).total_seconds(), 3),
           "checkedRunnerPass": "CHECKED_RUN PASS" in run.stdout, "log": log.relative_to(ROOT).as_posix(),
           "stdoutTail": run.stdout[-1200:], "stderrTail": run.stderr[-1200:],
           "diagnosticsNotFiltered": True}
    return rec


def encode(ffmpeg, ffprobe, raw, language, fps):
    clip = next(c for c in raw if c["language"] == language and c["fps"] == fps)
    fdir = OUT / clip["frames"]["dir"]
    files = sorted(fdir.glob("frame_*.png"))
    if len(files) != clip["frames"]["count"]:
        raise AssertionError(f"{language}{fps}: frames on disk {len(files)} != {clip['frames']['count']}")
    for p in (files[0], files[-1]):
        assert png_size(p) == (1280, 720), f"non-1280x720 viewport frame {p}"
    mp4 = OUT / f"{SLUG}_{language}{fps}-{'outskirts-bright' if language == 'en' else 'default-dark'}_staged-partialpilot_{STAMP}.mp4"
    title = f"STAGED partial pilot - heroine-sea {language} {fps}fps - not continuous normal-input combat"
    cmd = [str(ffmpeg), "-hide_banner", "-v", "warning", "-y", "-framerate", str(fps), "-start_number", "0",
           "-i", str(fdir / "frame_%05d.png"), "-c:v", "libx264", "-preset", "slow", "-crf", "14",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-metadata", f"title={title}",
           "-metadata", f"comment=STAGED partial pilot; process frozen; authored 1/30s ticks; {fps}fps sampling", str(mp4)]
    started = datetime.now()
    enc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if enc.returncode != 0 or enc.stderr.strip():
        raise AssertionError(f"ffmpeg {language}{fps}: exit {enc.returncode} stderr={enc.stderr.strip()[:500]}")
    probe_cmd = [str(ffprobe), "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                 "stream=codec_name,profile,pix_fmt,width,height,r_frame_rate,avg_frame_rate,time_base,nb_frames,nb_read_frames,duration:format=duration,size",
                 "-of", "json", str(mp4)]
    probe = json.loads(subprocess.run(probe_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout)
    st = probe["streams"][0]
    expected = clip["frames"]["count"]
    checks = {
        "codecH264": st.get("codec_name") == "h264",
        "pixFmtYuv420p": st.get("pix_fmt") == "yuv420p",
        "size1280x720": (st.get("width"), st.get("height")) == (1280, 720),
        "frameCount": int(st.get("nb_read_frames", -1)) == expected,
        "fps": st.get("avg_frame_rate") == f"{fps}/1" and st.get("r_frame_rate") == f"{fps}/1",
        "duration6_8": abs(float(probe["format"]["duration"]) - 6.8) <= 0.02,
    }
    return {"language": language, "fps": fps, "plate": clip["plate"], "frameCount": expected,
            "capturedFrames": len(files), "mp4": mp4.relative_to(ROOT).as_posix(), "mp4Sha256": sha(mp4),
            "mp4Bytes": mp4.stat().st_size, "encodeCommand": cmd, "encodeSeconds": round((datetime.now() - started).total_seconds(), 3),
            "ffmpegStderr": enc.stderr, "probe": probe, "checks": checks, "allChecksPass": all(checks.values()),
            "source": clip}


def main():
    if any(OUT.glob("*.mp4")) or any(OUT.glob(f"{SLUG}_report_*.json")):
        raise SystemExit("REFUSING_OVERWRITE: completed capture evidence already exists in " + str(OUT))
    manifest, base_path, pose_paths = load_inputs()
    assert GODOT.is_file(), f"missing Godot {GODOT}"
    assert CHECKED.is_file() and HARNESS.is_file()
    assert sha(HARNESS) and sha(CHECKED)
    ffmpeg = find_ffmpeg()
    ffprobe = ffprobe_for(ffmpeg)
    ffver = subprocess.run([str(ffmpeg), "-version"], capture_output=True, text=True, encoding="utf-8").stdout.splitlines()[0]
    bound_before = status_snapshot()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "frames").mkdir(exist_ok=True)
    (OUT / "profiles").mkdir(exist_ok=True)
    run_id = datetime.now().strftime("%H%M%S")
    failures = []
    runs = []
    raw_reports = []
    contexts = [("en", 30, "outskirts"), ("zh", 60, "default")]
    for idx, (language, fps, plate) in enumerate(contexts):
        env = dict(os.environ)
        for key in ("APPDATA", "LOCALAPPDATA"):
            d = OUT / "profiles" / f"{'app' if key == 'APPDATA' else 'local'}-{idx}-{language}{fps}-{run_id}"
            d.mkdir()
            env[key] = str(d)
        env.pop("ANTHROPIC_API_KEY", None)
        rec = run_checked(f"capture-{language}{fps}", ["capture", MANIFEST, OUT, CL, language, fps, plate, STAMP], env)
        runs.append(rec)
        raw_path = OUT / f"raw-{language}-{fps}.json"
        if rec["exit"] != 0 or not rec["checkedRunnerPass"]:
            failures.append(f"{language}{fps}: checked runner failed exit={rec['exit']} pass={rec['checkedRunnerPass']}")
        if not raw_path.is_file():
            failures.append(f"{language}{fps}: raw capture report missing")
            continue
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        raw_reports.append(raw)
        if raw.get("processFrozen") is not True or raw.get("staged") is not True or raw.get("continuousNormalInputCombat") is not False:
            failures.append(f"{language}{fps}: staged/frozen labels wrong")
        if raw["frames"]["count"] != 204 * fps // 30:
            failures.append(f"{language}{fps}: frame count {raw['frames']['count']}")
        if raw["verification"]["changedOutsideHeroBounds"] != 0:
            failures.append(f"{language}{fps}: changed pixels outside hero bounds")
        if not raw["verification"]["restoredEqualsBaselineRgba"] or not raw["verification"]["finalRestoreEqualsBaselineRgba"]:
            failures.append(f"{language}{fps}: restore not byte-identical")
        if raw["verification"]["controlsLogical"] is None:
            failures.append(f"{language}{fps}: controls missing")
        if raw["baseSourceByteExact"] is not True:
            failures.append(f"{language}{fps}: base source not byte-exact")
        if len(raw["poseAtTick"]) != 204:
            failures.append(f"{language}{fps}: poseAtTick length {len(raw['poseAtTick'])}")
        for label, tick in CRITICAL_TICKS.items():
            c = raw["critical"].get(label)
            if not c:
                failures.append(f"{language}{fps}: missing critical {label}")
                continue
            p = OUT / c["file"]
            if not p.is_file() or png_size(p) != (1280, 720):
                failures.append(f"{language}{fps}: critical {label} not full-size PNG")
            elif sha(p) != c["sha256"]:
                failures.append(f"{language}{fps}: critical {label} hash changed")
            if c["tick"] != tick:
                failures.append(f"{language}{fps}: critical {label} tick {c['tick']} != {tick}")
    # REAL normal _try_attack probe.
    env = dict(os.environ)
    for key in ("APPDATA", "LOCALAPPDATA"):
        d = OUT / "profiles" / f"{'app' if key == 'APPDATA' else 'local'}-2-probe-{run_id}"
        d.mkdir()
        env[key] = str(d)
    env.pop("ANTHROPIC_API_KEY", None)
    probe_run = run_checked("probe", ["probe", MANIFEST, OUT, CL], env)
    runs.append(probe_run)
    probe = None
    probe_path = OUT / "raw-probe.json"
    if probe_run["exit"] != 0 or not probe_run["checkedRunnerPass"] or not probe_path.is_file():
        failures.append(f"probe: checked runner failed or report missing exit={probe_run['exit']}")
    else:
        probe = json.loads(probe_path.read_text(encoding="utf-8"))
        setup = probe["setup"]
        if not probe["tryAttackReturned"] or probe["immediateDamage"] != 19:
            failures.append("probe: normal _try_attack did not land/19 damage")
        if probe["after"]["visualElapsed"] != 0.0 or probe["synchronizedGameplayContact"] is not False or not probe["mismatch"]:
            failures.append("probe: immediate damage/synchronized contact claim/elapsed wrong")
        if setup["hpInjection"] or setup["timerInjection"] or setup["cooldownInjection"] or not setup["singlePress"]:
            failures.append("probe: injection/single-press contract broken")
        if abs(float(probe["stagedContactStartSeconds"]) - 0.166667) > 1e-6:
            failures.append("probe: staged contact duration mismatch")
    # Pose sampling at shared timestamps (same authored tick, 30 vs 60 frame index).
    shared = []
    if len(raw_reports) == 2:
        by = {(r["language"], r["fps"]): r for r in raw_reports}
        r30, r60 = by[("en", 30)], by[("zh", 60)]
        for t in [0.0, 2.0, 2.066667, 2.166667, 2.3, 2.4, 3.4]:
            tick = round(t * 30)
            p30 = r30["poseAtTick"][tick]
            p60 = r60["poseAtTick"][tick]
            f30 = round(t * 30)
            f60 = round(t * 60)
            shared.append({"t": t, "tick": tick, "pose": p30, "frame30": f30, "frame60": f60,
                           "pose30": p30, "pose60": p60, "samePose": p30 == p60,
                           "frame30File": f"frames_en_30/frame_{f30:05d}.png",
                           "frame60File": f"frames_zh_60/frame_{f60:05d}.png"})
        if not all(x["samePose"] for x in shared):
            failures.append("30/60 shared-timestamp pose selection differs")
    else:
        failures.append("both capture reports required for shared-timestamp sampling")
    clips = []
    for language, fps, plate in contexts:
        if any(r["language"] == language and r["fps"] == fps for r in raw_reports):
            try:
                clip = encode(ffmpeg, ffprobe, raw_reports, language, fps)
                clips.append(clip)
                if not clip["allChecksPass"]:
                    failures.append(f"{language}{fps}: MP4 checks failed {clip['checks']}")
            except AssertionError as e:
                failures.append(str(e))
    bound_after = status_snapshot()
    changed = [k for k in bound_before if bound_before[k] != bound_after.get(k)]
    if changed:
        failures.append(f"bound source/input changed during run: {changed}")
    pose_hashes = {pid: {"file": p.relative_to(CL).as_posix(), "sha256": sha(p)} for pid, p in pose_paths.items()}
    report = {
        "status": "STAGED partial2-action motion pilot (idle + attack only). NOT all 8 actions, NOT creator-approved, NOT continuous normal-input combat, NOT a full combat-loader claim. Process frozen for deterministic pose play.",
        "testOnly": True, "staged": True, "partialPilot": True, "processFrozen": True,
        "continuousNormalInputCombat": False, "allEightActions": False, "creatorApproved": False,
        "gameSourceEdited": False, "sharedLedgerEdited": False, "gitIndexTouched": False, "committed": False,
        "providerCalled": False, "creditPurchased": False, "authChanged": False, "downloads": False,
        "stamp": STAMP, "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "gitHead": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout.strip(),
        "hashNormalization": "sha256 bytes for files; author-tool manifest hash uses text LF normalization as declared in the manifest",
        "arenaSha256": sha(ARENA), "arenaSha256Expected": ARENA_SHA, "projectSha256": sha(PROJECT),
        "harness": HARNESS.relative_to(ROOT).as_posix(), "harnessSha256": sha(HARNESS),
        "runner": Path(__file__).relative_to(ROOT).as_posix(), "runnerSha256": sha(__file__),
        "checkedRunner": CHECKED.relative_to(ROOT).as_posix(), "checkedRunnerSha256": sha(CHECKED),
        "input": {"manifest": MANIFEST.relative_to(CL).as_posix(), "manifestSha256": sha(MANIFEST),
                  "authorTool": AUTHOR.relative_to(CL).as_posix(), "authorToolSha256TextLf": sha_text_lf(AUTHOR),
                  "authorToolSha256Bytes": sha(AUTHOR), "baseSource": base_path.relative_to(CL).as_posix(),
                  "baseSourceSha256": sha(base_path), "poseFiles": pose_hashes,
                  "cell": [136, 144], "logicalExtent": [68, 72], "pinNative": [64, 136], "pinLogical": [32, 68],
                  "stagedContactStartSeconds": manifest["stagedContact"]["start_s"]},
        "capture": {"backing": [1280, 720], "logicalVisible": [640, 360], "contentScaleMode": "canvas_items", "stretchFactor": 2,
                    "windowTitle": None, "framesRealViewport": True, "pythonCompositing": False, "interpolation": False,
                    "equalFrameRetiming": False, "contactSheet": False,
                    "draw": "in-memory subclass of CURRENT battle_arena.gd; ONLY hero draw overridden; 136x144 source -> 68x72 logical at pivot 32/68; nearest; no mipmaps",
                    "cameraUiPartyChanged": False, "partyX": [135.0, 171.0, 207.0, 243.0],
                    "schedule": {"leadIdleSeconds": 2.0, "attackSeconds": 0.4, "tailIdleSeconds": 1.0, "attacks": 2,
                                 "totalSeconds": 6.8, "tickSeconds": 1 / 30, "fpsParity": "30fps one sample per authored tick; 60fps two samples per authored tick"}},
        "clips": clips, "sharedTimestampSampling": shared,
        "verification": [{"language": r["language"], "fps": r["fps"], "data": r["verification"], "critical": r["critical"]} for r in raw_reports],
        "realAttackEventProbe": probe,
        "probe": {"status": "separate REAL normal _try_attack at a declared single in-range setup; immediate damage is at t=0, staged contact is a visual timeline only; not synchronized",
                  "stagedContactStartSeconds": 0.166667, "stagedContactAbsoluteClipSeconds": 2.166667,
                  "synchronizedGameplayContact": False},
        "logicalScale1Helper": {"used": False, "reason": "the existing combat sprite-set loader only accepts logical_scale 1; a 136-texel source cannot be drawn at 136 logical px for a 68x72 extent; a full combat-loader claim would require more actions/loader work"},
        "runnerRuns": runs,
        "ffmpeg": {"path": str(ffmpeg), "sha256": sha(ffmpeg), "version": ffver, "ffprobe": str(ffprobe),
                   "source": "installed imageio_ffmpeg if importable, otherwise installed ffmpeg; no download"},
        "boundSha256AtStart": bound_before, "boundSha256AtEnd": bound_after,
        "rawLogs": [r["log"] for r in runs], "failures": failures,
        "result": "PASS" if not failures else "FAIL",
        "limitations": ["staged visual timeline, not continuous normal input combat", "partial2 actions only", "not creator-approved",
                        "the immediate game damage is not synchronized to the staged 166ms contact", "raw frames remain local/ignored"]
    }
    path = OUT / f"{SLUG}_report_{STAMP}.json"
    path.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(("HSEA_MOTION_RUN PASS" if not failures else "HSEA_MOTION_RUN FAIL") + f" clips={len(clips)} report={path.name}")
    for f in failures:
        print("FAIL", f)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
