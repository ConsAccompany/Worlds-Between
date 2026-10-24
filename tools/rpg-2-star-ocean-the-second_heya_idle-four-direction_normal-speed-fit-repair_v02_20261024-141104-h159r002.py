"""Heya i159 normal-speed four-direction idle SOURCE-FIT repair v02 (test-only; EN/ZH; city/ruins).

Repairs the v01 harness: frame_at is a real modulo-1500 loop, the original 120 ms elapsed bound is
retained (not relaxed to 250 ms), explicit before/at/after boundaries use independent literal expected
constants, and malformed runtime manifests (duration/frame count) are rejected through the same checked
runner. This is source-fit playback evidence only: not SpriteFrames engine integration, not runtime
adoption, not motion/art acceptance. Writes only under outputs/heya-i159/repair2/.
"""
import hashlib, importlib.util, json, os
from pathlib import Path
from PIL import Image

R = Path(__file__).resolve().parents[1]
TAG = "20261024-141104-h159r002"
OUT = R / "outputs/heya-i159/repair2"
FIT = OUT / "captures" / f"normal-speed-{TAG}"
n = 1
while FIT.exists():
    n += 1
    FIT = OUT / "captures" / f"normal-speed-{TAG}-r{n}"
FIT.mkdir(parents=True)
SCRATCH = OUT / "scratch" / f"malformed-{FIT.name}"
SCRATCH.mkdir(parents=True)
HOMEDIR = R / "outputs/heya-i159/godot-home"
for sub in ("home", "config", "data", "cache", "run", "tmp"):
    (HOMEDIR / sub).mkdir(parents=True, exist_ok=True)
os.environ.update(TMPDIR=str(HOMEDIR / "tmp"), HOME=str(HOMEDIR / "home"),
                  XDG_CONFIG_HOME=str(HOMEDIR / "config"), XDG_DATA_HOME=str(HOMEDIR / "data"),
                  XDG_CACHE_HOME=str(HOMEDIR / "cache"), XDG_RUNTIME_DIR=str(HOMEDIR / "run"))
runtime = next((R / "game/assets/characters/heya-native-v01/idle").glob("*sprite-set-runtime*.json")).resolve()
gd = R / "tools/rpg-2-star-ocean-the-second_heya_idle-four-direction_normal-speed-fit-repair_test-only-v02_20261024-141104-h159r002.gd"
runner_path = R / "tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py"
godot = Path("/home/kel/projects/worlds-between/tooling/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64")
DURATIONS = [700, 200, 400, 200]
PERIOD = 1500
# Independent literal expected constants; these are NOT derived from the GDS frame function.
BOUNDARIES = [(699, 0), (700, 1), (899, 1), (900, 2), (1299, 2), (1300, 3),
              (1499, 3), (1500, 0), (1501, 0), (2199, 0), (2200, 1),
              (2699, 2), (2700, 2), (2999, 3), (3000, 0), (3001, 0)]
EXPECTED_AT_TARGET = {100: 0, 1000: 2, 1350: 3}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def frame_at(ms):
    t = ms % PERIOD
    acc = 0
    for i, dur in enumerate(DURATIONS):
        acc += dur
        if t < acc:
            return i
    return 0


spec = importlib.util.spec_from_file_location("checked", runner_path)
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
watched = [runtime, gd, runner_path]
before = {str(p): sha(p) for p in watched}
cmd = ["xvfb-run", "-a", "-s", "-screen 0 640x360x24", str(godot), "--path", str(R / "game"),
       "--resolution", "640x360", "--rendering-driver", "opengl3", "--audio-driver", "Dummy",
       "--script", str(gd), "--", str(runtime), str(FIT.resolve()), TAG]
log = OUT / "logs" / f"normal-speed-{FIT.name}.runner.log"
res = runner.run_checked(cmd, 75, ["HEYA_I159_IDLE_NORMAL_SPEED_PASS captures=12"], log)
run_result = {k: v for k, v in res.items() if k != "log"}
man = next(FIT.glob("*normal-speed-manifest*.json"))
m = json.loads(man.read_text(encoding="utf8"))
captures = sorted(FIT.glob("*normal-speed-*.png"))
dims = {p.name: list(Image.open(p).size) for p in captures}
frame_ok = all(all(v == frame_at(c["elapsed_ms"]) for v in c["frame_indices"].values()) for c in m["captures"])
span_ok = sorted({v for c in m["captures"] for v in c["frame_indices"].values()}) == [0, 2, 3]
speed_ok = all(c["elapsed_ms"] <= c["target_ms"] + 120 for c in m["captures"])
target_frames_ok = all(frame_at(c["target_ms"]) == EXPECTED_AT_TARGET[c["target_ms"]] for c in m["captures"])
gds_boundaries = {(int(x["elapsed_ms"]), int(x["expected"])): (int(x["actual"]), bool(x["ok"]))
                 for x in m["boundaryChecks"]}
boundaries_ok = all(gds_boundaries.get(pair) == (expected, True) for pair, expected in
                    [((ms, exp), exp) for ms, exp in BOUNDARIES])
boundaries_ok = boundaries_ok and len(gds_boundaries) == len(BOUNDARIES)
loop_ok = bool(m.get("boundaryChecksAllOk") and m.get("loopAt1500EqualsZero") and m.get("loopAt3000EqualsZero")
               and frame_at(1500) == 0 and frame_at(1501) == 0 and frame_at(3000) == 0 and frame_at(2999) == 3)
manifest_ok = (m.get("runtimeAdopted") is False and m.get("artApproved") is False
               and m.get("sourceFitOnly") is True and m.get("motionAcceptance") is False
               and len(m.get("captures", [])) == 12)
# Malformed manifest coverage through the SAME checked runner / GDS validator.
malformed = []
source_m = json.loads(runtime.read_text(encoding="utf8"))
cases = {}
bad_dur = json.loads(json.dumps(source_m))
bad_dur["actions"]["idle"]["west"][1]["duration_ms"] = 201
cases["duration_mismatch"] = bad_dur
bad_frames = json.loads(json.dumps(source_m))
bad_frames["actions"]["idle"]["north"] = bad_frames["actions"]["idle"]["north"][:3]
cases["frame_count_3"] = bad_frames
for name, obj in cases.items():
    p = SCRATCH / f"{name}.json"
    p.write_text(json.dumps(obj), encoding="utf8")
    mlog = OUT / "logs" / f"malformed-{name}-{FIT.name}.runner.log"
    mcmd = ["xvfb-run", "-a", "-s", "-screen 0 640x360x24", str(godot), "--path", str(R / "game"),
            "--resolution", "640x360", "--rendering-driver", "opengl3", "--audio-driver", "Dummy",
            "--script", str(gd), "--", str(p), str((SCRATCH / name).resolve()), TAG]
    mres = runner.run_checked(mcmd, 30, ["HEYA_I159_IDLE_MALFORMED_REJECTED"], mlog)
    malformed.append({"case": name, "exitCode": mres.get("exitCode"), "timedOut": mres.get("reason") == "timeout",
                      "rejectedMarker": "HEYA_I159_IDLE_MALFORMED_REJECTED" in mres.get("log", ""),
                      "accepted": bool(mres.get("passed")), "log": str(mlog.relative_to(R))})
malformed_ok = all(x["exitCode"] == 2 and x["rejectedMarker"] and not x["timedOut"] for x in malformed)
after = {str(p): sha(p) for p in watched}
proof = {"task": "content.char.heya.idle-anim normal-speed four-direction SOURCE-FIT repair (test-only)",
         "repair_of": "tools/..._normal-speed-fit_v01_20261024-140235-a159i001.py",
         "repair_tag": TAG, "command": cmd, "run_result": run_result,
         "runtimeManifest": str(runtime.relative_to(R)), "runtimeManifestSha256": before[str(runtime)],
         "script": str(gd.relative_to(R)), "scriptSha256": before[str(gd)],
         "runner": str(runner_path.relative_to(R)), "runnerSha256": before[str(runner_path)],
         "godot": str(godot), "godotSha256": sha(godot), "log": str(log.relative_to(R)),
         "captures": [str(p.relative_to(R)) for p in captures], "captureDimensions": dims,
         "manifest": str(man.relative_to(R)), "manifestSha256": sha(man),
         "frameAtModulo1500": True, "loopPeriodMs": PERIOD,
         "boundariesExecuted": [{"elapsed_ms": ms, "independentExpected": exp, "actual": frame_at(ms)}
                                for ms, exp in BOUNDARIES],
         "boundaryCount": len(BOUNDARIES), "boundariesAllOk": boundaries_ok,
         "gdsReportedBoundaries": m.get("boundaryChecks"),
         "loopAt1500": frame_at(1500), "loopAt1501": frame_at(1501),
         "loopAt2999": frame_at(2999), "loopAt3000": frame_at(3000), "loopProofOk": loop_ok,
         "frameAtExpectedAtTargets": {str(k): v for k, v in EXPECTED_AT_TARGET.items()},
         "targetFramesOk": target_frames_ok,
         "normalSpeedFramesExact": frame_ok, "phaseSpanExact": span_ok,
         "elapsedBoundMs": 120, "elapsedWithinOriginal120msBound": speed_ok,
         "captureCount": len(captures), "manifestStructureOk": manifest_ok,
         "malformedManifestControls": malformed, "malformedManifestAllRejected": malformed_ok,
         "sourceFitOnly": True, "motionAcceptance": False, "runtimeAdopted": False,
         "artApproved": False, "testOnly": True, "audioDriver": "Dummy",
         "renderingDriver": "opengl3", "xvfb": "640x360x24",
         "limitations": ["not SpriteFrames/runtime engine playback; direct source-fit overlay only",
                         "not ordinary actor integration", "not human motion review or art acceptance",
                         "wall-clock capture phases are approximate; boundary proof is function-level"],
         "unchangedBeforeAfter": before == after}
proof["passed"] = bool(res.get("passed") and len(captures) == 12
                       and all(v == [640, 360] for v in dims.values())
                       and frame_ok and span_ok and speed_ok and target_frames_ok and boundaries_ok
                       and loop_ok and manifest_ok and malformed_ok and before == after)
proof_path = OUT / f"rpg-2-star-ocean-the-second_heya_idle-four-direction_normal-speed-repair-proof_test-only-v02_{FIT.name}.json"
proof_path.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf8")
print(json.dumps({"passed": proof["passed"], "captures": len(captures), "frame_ok": frame_ok,
                  "boundaries_ok": boundaries_ok, "loop_ok": loop_ok, "speed_ok_120": speed_ok,
                  "malformed_ok": malformed_ok, "run": run_result}, indent=2))
print("HEYA_I159_IDLE_NORMAL_SPEED_REPAIR " + ("PASS" if proof["passed"] else "FAIL"))
raise SystemExit(0 if proof["passed"] else 1)
