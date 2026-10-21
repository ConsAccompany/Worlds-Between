"""Combined heroine playable-path v16 checked runner (TEST-ONLY evidence, not human playtest or art approval).

Runs the single reusable Godot harness through the existing checked runner. Each Godot execution is wall-bounded at
120 s, requires an explicit success marker and fails on SCRIPT/ERROR/parser diagnostics. Saves use per-run temporary
APPDATA/LOCALAPPDATA profiles, never the real user profile. If the shared config or combat package is absent in this
disjoint checkout, the runner parse-checks the harness, records helper checks and reports PENDING_INTEGRATION (exit 3);
it does not claim success. Root reruns it after the combined integration checkout exists.

Usage (default en+zh patrol):
  python -I <this>
  python -I <this> --language en --movie
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path

C = Path(__file__).resolve().parents[1]
GODOT = Path(r"C:/Users/hkzha/Documents/Codex/2026-10-12/rpg-2-star-ocean-the-second/work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe")
CHECKED = C / "tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py"
HARNESS = C / "tools/rpg-2-star-ocean-the-second_heroine-playable-path_combined-flow-check_test-only-v16_20261021-015641-e106bdfa.gd"
OUT = C / "outputs/heroine-path16"
CONFIG_RES = "res://scripts/hsea16/rpg-2-star-ocean-the-second_heroine-playable-path_config_opt-in-v01_20261021-015453-1036fbad.gd"
CONFIG_FILE = C / "game/scripts/hsea16/rpg-2-star-ocean-the-second_heroine-playable-path_config_opt-in-v01_20261021-015453-1036fbad.gd"
ENTRY_RES = "res://scripts/hsea16/rpg-2-star-ocean-the-second_heroine-playable-path_entry_opt-in-v01_20261021-015453-1036fbad.gd"
ENTRY_FILE = C / "game/scripts/hsea16/rpg-2-star-ocean-the-second_heroine-playable-path_entry_opt-in-v01_20261021-015453-1036fbad.gd"
INDEX_RES = "res://data/heroine-sea-combat-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet-index_v01_20261020-201338-38ecfcb0.json"
INDEX_FILE = C / "game/data/heroine-sea-combat-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet-index_v01_20261020-201338-38ecfcb0.json"
REGISTRY_RES = "res://data/hsea-stop15/rpg-2-star-ocean-the-second_heroine-phase-stop_registry_test-only-v01_20261021-015453-1036fbad.json"
REGISTRY_FILE = C / "game/data/hsea-stop15/rpg-2-star-ocean-the-second_heroine-phase-stop_registry_test-only-v01_20261021-015453-1036fbad.json"
MAX_WALL = 120.0


def lp(p):
    p = Path(p).resolve()
    return Path("\\\\?\\" + str(p)) if os.name == "nt" and len(str(p)) > 240 else p


def sha(p):
    return hashlib.sha256(lp(p).read_bytes()).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def png_size(path):
    data = lp(path).read_bytes()[:33]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + "-" + os.urandom(4).hex()


def parse_languages(values):
    if not values:
        return ["en", "zh"]
    seen = []
    for value in values:
        for part in value.split(","):
            lang = part.strip().lower()
            if lang not in ("en", "zh"):
                raise SystemExit(f"unsupported language: {part!r} (only en/zh)")
            if lang not in seen:
                seen.append(lang)
    return seen


def helper_checks(languages):
    checks = {}
    checks["two_language_patrol_default"] = languages == ["en", "zh"]
    checks["language_order_preserved"] = parse_languages(["zh,en"]) == ["zh", "en"]
    checks["rejects_other_language"] = False
    try:
        parse_languages(["fr"])
    except SystemExit:
        checks["rejects_other_language"] = True
    checks["harness_name_lowercase_unique"] = bool(re.fullmatch(r"rpg-2-star-ocean-the-second_heroine-playable-path_combined-flow-check_test-only-v16_20261021-015641-e106bdfa\.gd", HARNESS.name))
    checks["runner_name_lowercase_unique"] = bool(re.fullmatch(r"rpg-2-star-ocean-the-second_heroine-playable-path_root-runner_test-only-v16_20261021-015641-e106bdfa\.py", Path(__file__).name))
    checks["config_res_matches_expected"] = CONFIG_RES.endswith("_config_opt-in-v01_20261021-015453-1036fbad.gd") and CONFIG_RES.startswith("res://scripts/hsea16/")
    checks["index_res_matches_expected"] = INDEX_RES.endswith("_spritesheet-index_v01_20261020-201338-38ecfcb0.json")
    checks["wall_bound_120"] = MAX_WALL == 120.0
    checks["success_marker_shape"] = all(f"PATH16_ALL_PASS language={lang} checks=" in f"PATH16_ALL_PASS language={lang} checks=1" for lang in languages)
    return checks


def parse_check(tag):
    """GDScript parse check in real Godot. --check-only parses the harness without booting this checkout's autoloads,
    so unrelated partial-checkout autoload errors cannot mask or fake the harness result."""
    log = OUT / f"rpg-2-star-ocean-the-second_heroine-playable-path_harness-parse-check_v16_{tag}.log"
    cmd = [str(GODOT), "--headless", "--check-only", "--script", str(HARNESS)]
    checked = module("checked", CHECKED)
    return checked.run_checked(cmd, 60, expected=[], log_path=lp(log)), log


def encode_movie(ffmpeg, ffprobe, raw_dir, stem, language, tag):
    avi = raw_dir / (stem + ".avi")
    if avi.exists():
        probe0 = subprocess.run([str(ffprobe), "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=width,height,avg_frame_rate,nb_read_frames", "-of", "json", str(avi)], capture_output=True, text=True, encoding="utf8", check=True)
        original = json.loads(probe0.stdout)["streams"][0]
        assert (original["width"],original["height"],original["avg_frame_rate"]) == (1280,720,"30/1")
        movie = OUT / f"rpg-2-star-ocean-the-second_heroine-playable-path_{language}-patrol_normal-speed_v16_{tag}.mp4"
        subprocess.run([str(ffmpeg),"-hide_banner","-v","error","-y","-i",str(avi),"-an","-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(movie)],capture_output=True,text=True,encoding="utf8",check=True)
        probe = subprocess.run([str(ffprobe),"-v","error","-count_frames","-select_streams","v:0","-show_entries","stream=codec_name,width,height,avg_frame_rate,nb_read_frames:format=duration,size","-of","json",str(movie)],capture_output=True,text=True,encoding="utf8",check=True)
        info=json.loads(probe.stdout);st=info["streams"][0]
        assert (st["codec_name"],st["width"],st["height"],st["avg_frame_rate"],st["nb_read_frames"]) == ("h264",1280,720,"30/1",original["nb_read_frames"])
        assert 0 < movie.stat().st_size <= 24*1024*1024
        return {"file":movie.relative_to(C).as_posix(),"sha256":sha(movie),"frames":int(st["nb_read_frames"]),"probe":info,"normalSpeedFps":30,"rawFormat":"Godot native AVI; exact frame count retained, no speed change"}
    frames = sorted(raw_dir.glob(stem + "*.png"))
    if not frames:
        raise AssertionError(f"no raw movie frames for {language}")
    nums = [int(re.search(r"(\d+)\.png$", f.name).group(1)) for f in frames]
    start = min(nums)
    movie = OUT / f"rpg-2-star-ocean-the-second_heroine-playable-path_{language}-patrol_normal-speed_v16_{tag}.mp4"
    cmd = [str(ffmpeg), "-hide_banner", "-v", "error", "-y", "-framerate", "30", "-start_number", str(start),
           "-i", str(raw_dir / (stem + "%08d.png")), "-c:v", "libx264", "-preset", "slow", "-crf", "18",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(movie)]
    enc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if enc.returncode != 0:
        raise AssertionError(f"ffmpeg {language}: {enc.stderr[:800]}")
    probe = subprocess.run([str(ffprobe), "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                            "stream=codec_name,width,height,avg_frame_rate,nb_read_frames:format=duration,size",
                            "-of", "json", str(movie)], capture_output=True, text=True, encoding="utf-8")
    if probe.returncode != 0:
        raise AssertionError(f"ffprobe {language}: {probe.stderr[:800]}")
    data = json.loads(probe.stdout)
    st = data["streams"][0]
    assert st["codec_name"] == "h264", st
    assert st["width"] == 1280 and st["height"] == 720, st
    assert st["avg_frame_rate"] == "30/1", st
    assert int(st["nb_read_frames"]) == len(frames), (st["nb_read_frames"], len(frames))
    assert movie.stat().st_size <= 24 * 1024 * 1024, movie.stat().st_size
    return {"file": movie.relative_to(C).as_posix(), "sha256": sha(movie), "frames": len(frames), "probe": data, "normalSpeedFps": 30}


def run_full(languages, make_movie, tag):
    if not GODOT.is_file():
        raise SystemExit(f"Godot missing: {GODOT}")
    checked = module("checked", CHECKED)
    ffmpeg = ffprobe = None
    if make_movie:
        media = module("media", C / "tools/rpg-2-star-ocean-the-second_heroine-sea_motion-capture-runner_test-only-v01_20261020-153144-3fb36c1a.py")
        ffmpeg = media.find_ffmpeg()
        ffprobe = media.ffprobe_for(ffmpeg)
    old_env = {k: os.environ.get(k) for k in ("APPDATA", "LOCALAPPDATA")}
    runs = []
    try:
        for language in languages:
            profile = OUT / "profiles" / tag / language
            appdata = profile / "appdata"
            localappdata = profile / "localappdata"
            for p in (appdata, localappdata):
                p.mkdir(parents=True, exist_ok=False)
            os.environ["APPDATA"] = str(appdata)
            os.environ["LOCALAPPDATA"] = str(localappdata)
            raw_dir = OUT / "raw" / tag / language
            raw_dir.mkdir(parents=True)
            stem = f"rpg-2-star-ocean-the-second_heroine-playable-path_{language}-raw_v16_{tag}"
            cmd = [str(GODOT), "--resolution", "1280x720", "--position", "40,40", "--audio-driver", "Dummy",
                   "--fixed-fps", "30"]
            if make_movie:
                cmd += ["--write-movie", str(raw_dir / (stem + ".avi"))]
            cmd += ["--path", str(C / "game"), "--script", str(HARNESS), "--",
                    str(OUT), CONFIG_RES, INDEX_RES, language, tag, str(profile)]
            log = OUT / f"rpg-2-star-ocean-the-second_heroine-playable-path_{language}-combined-flow_v16_{tag}.log"
            r = checked.run_checked(cmd, MAX_WALL, expected=[f"PATH16_ALL_PASS language={language}"], log_path=lp(log))
            print(language, r["passed"], r["reason"], r["elapsedSeconds"], flush=True)
            if not r["passed"]:
                raise AssertionError(f"{language} failed: {r['reason']}\n{r['log'][-2500:]}")
            flow = next(OUT.glob(f"*{language}-combined-flow-report*{tag}.json"))
            report = json.loads(lp(flow).read_text(encoding="utf-8"))
            assert not report["failures"], report["failures"]
            assert report["package"]["poseCount"] == 29, report["package"]
            assert report["package"]["artApproved"] is False and report["package"]["defaultAdoption"] is False
            labels = {c["label"] for c in report["captures"]}
            for required in ("explore-start", "explore-move", "anticipation", "contact", "result", "return"):
                assert required in labels, (required, labels)
            for cap in report["captures"]:
                path = OUT / cap["file"]
                assert path.is_file() and png_size(path) == (1280, 720), cap
                assert sha(path) == cap["sha256"], cap
            movie = None
            if make_movie:
                movie = encode_movie(ffmpeg, ffprobe, raw_dir, stem, language, tag)
            runs.append({"language": language, "status": "pass", "command": cmd, "elapsedSeconds": r["elapsedSeconds"],
                         "checks": len(report["checks"]), "flowReport": flow.relative_to(C).as_posix(),
                         "log": log.relative_to(C).as_posix(), "captures": report["captures"], "movie": movie,
                         "profile": profile.relative_to(C).as_posix(),
                         "warnings": [line for line in r["log"].splitlines() if "WARNING" in line]})
            print("PATH16_RUN_PASS", language, len(report["checks"]), flush=True)
    finally:
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    proof = {"status": "PASS", "completedAt": datetime.now(timezone.utc).isoformat(), "tag": tag,
             "runs": runs, "allPass": True, "harness": HARNESS.relative_to(C).as_posix(), "harnessSha256": sha(HARNESS),
             "runner": Path(__file__).relative_to(C).as_posix(), "runnerSha256": sha(Path(__file__)),
             "config": {"path": CONFIG_RES, "sha256": sha(CONFIG_FILE)},
             "entry": {"path": ENTRY_RES, "sha256": sha(ENTRY_FILE) if ENTRY_FILE.is_file() else None},
             "packageIndex": {"path": INDEX_RES, "sha256": sha(INDEX_FILE)},
             "registry": {"path": REGISTRY_RES, "sha256": sha(REGISTRY_FILE) if REGISTRY_FILE.is_file() else None},
             "saveProfiles": "per-run APPDATA/LOCALAPPDATA under outputs/heroine-path16/profiles; actual user saves untouched",
             "humanPlaytest": False, "artApproved": False, "defaultAdoption": False,
             "note": "Scripted normal-input evidence. Not a human playtest, motion/art/default approval or score change."}
    proof_file = OUT / f"rpg-2-star-ocean-the-second_heroine-playable-path_combined-root-proof_v16_{tag}.json"
    lp(proof_file).write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    print("PATH16_ROOT_PASS", proof_file, flush=True)


def run_pending(languages, tag):
    missing = [{"path": p.relative_to(C).as_posix(), "kind": kind} for p, kind in [
        (CONFIG_FILE, "shared config module"), (INDEX_FILE, "combat package index"), (ENTRY_FILE, "entry module"),
        (REGISTRY_FILE, "phase-stop registry")] if not p.is_file()]
    checked = module("checked", CHECKED)
    parse = parse_check(tag)
    r, log = parse
    helpers = helper_checks(languages)
    report = {"status": "PENDING_INTEGRATION", "allPass": False, "why": "Shared config/package not present in this disjoint checkout; no integrated run was attempted.",
              "missing": missing, "tag": tag, "languages": languages, "harness": HARNESS.relative_to(C).as_posix(),
              "harnessSha256": sha(HARNESS), "runner": Path(__file__).relative_to(C).as_posix(), "runnerSha256": sha(Path(__file__)),
              "parseCheck": {"passed": r["passed"], "reason": r["reason"], "exitCode": r["exitCode"], "elapsedSeconds": r["elapsedSeconds"],
                             "log": log.relative_to(C).as_posix(), "expectedMarker": "exit 0 plus no SCRIPT/ERROR diagnostic (Godot --check-only)"},
              "helperChecks": helpers, "helperChecksPass": all(helpers.values()),
              "rootCommandAfterIntegration": f"python -I {Path(__file__).relative_to(C).as_posix()}",
              "movieCommandAfterIntegration": f"python -I {Path(__file__).relative_to(C).as_posix()} --movie",
              "humanPlaytest": False, "artApproved": False, "defaultAdoption": False}
    report_file = OUT / f"rpg-2-star-ocean-the-second_heroine-playable-path_pending-integration-report_v16_{tag}.json"
    lp(report_file).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PATH16_PARSE_CHECK", "PASS" if r["passed"] else "FAIL", r["reason"], r["elapsedSeconds"], flush=True)
    print("PATH16_HELPER_CHECKS", helpers, flush=True)
    if not r["passed"] or not all(helpers.values()):
        print("PATH16_PENDING_CHECK_FAILED", report_file, flush=True)
        return 1
    print("PATH16_PENDING_INTEGRATION", report_file, flush=True)
    return 3


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", action="append", default=[], help="en or zh; repeat or comma-separate; default en+zh")
    parser.add_argument("--movie", action="store_true", help="one normal-speed 30 fps movie per language")
    parser.add_argument("--timeout", type=float, default=MAX_WALL, help="per-Godot wall bound (max 120)")
    args = parser.parse_args()
    if not (0 < args.timeout <= MAX_WALL):
        raise SystemExit("--timeout must be >0 and <=120")
    languages = parse_languages(args.language)
    OUT.mkdir(parents=True, exist_ok=True)
    tag = stamp()
    if not CONFIG_FILE.is_file() or not INDEX_FILE.is_file():
        return run_pending(languages, tag)
    run_full(languages, args.movie, tag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
