"""Bounded Godot normal-speed south walk/stop source-fit for Heya h165sw (test-only).

Uses the checked runner (finite deadline + diagnostic stop), Xvfb 640x360, OpenGL3 and Dummy audio. Loads the
optional source sprite set and stop supplement from the opt-in package, renders a 3x source preview plus the
0.5x game-scale sprite with pivot (40,104), and captures at walk phase 2/11/7 then stop s1/s2/idle f00. It records
the actual elapsed time and independently re-derives the expected frame from that time. No runtime adoption,
default change or art approval. Writes only under outputs/heya-sw165/fit/.
"""
import hashlib, importlib.util, json, os
from pathlib import Path
from PIL import Image

R = Path(__file__).resolve().parents[1]
TAG = "20261024-143000-h165s001"
OUT = R / "outputs/heya-sw165/fit"
OUT.mkdir(parents=True, exist_ok=True)
FIT = OUT / "capture"
n = 1
while FIT.exists() and any(FIT.iterdir()):
    n += 1
    FIT = OUT / f"capture-r{n}"
FIT.mkdir(parents=True, exist_ok=True)
HOMEDIR = R / "outputs/heya-sw165/godot-home"
for sub in ("home", "config", "data", "cache", "run", "tmp"):
    (HOMEDIR / sub).mkdir(parents=True, exist_ok=True)
os.environ.update(TMPDIR=str(HOMEDIR / "tmp"), HOME=str(HOMEDIR / "home"),
                  XDG_CONFIG_HOME=str(HOMEDIR / "config"), XDG_DATA_HOME=str(HOMEDIR / "data"),
                  XDG_CACHE_HOME=str(HOMEDIR / "cache"), XDG_RUNTIME_DIR=str(HOMEDIR / "run"))
PKG = R / "game/assets/characters/heya-native-v01/south-walk"
runtime = next(PKG.glob("*sprite-set-runtime*.json")).resolve()
stop = next(PKG.glob("*stop-transition-supplemental*.json")).resolve()
gd = R / "tools/rpg-2-star-ocean-the-second_heya_walk-south_normal-speed-fit_test-only-v01_20261024-143000-h165s001.gd"
runner_path = R / "tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py"
godot = Path("/home/kel/projects/worlds-between/tooling/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def state_at(ms):
    if ms < 800:
        return ("walk", (ms // 40) % 12)
    if ms < 840:
        return ("s1", 0)
    if ms < 880:
        return ("s2", 0)
    return ("idle", 0)


spec = importlib.util.spec_from_file_location("checked", runner_path)
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
before = {str(p): sha(p) for p in [runtime, stop, gd, runner_path]}
cmd = ["xvfb-run", "-a", "-s", "-screen 0 640x360x24", str(godot), "--path", str(R / "game"),
       "--resolution", "640x360", "--rendering-driver", "opengl3", "--audio-driver", "Dummy",
       "--script", str(gd), "--", str(runtime), str(stop), str(FIT.resolve()), TAG]
log = OUT / f"normal-speed-{FIT.name}.runner.log"
res = runner.run_checked(cmd, 75, ["HEYA_H165SW_SOUTH_WALK_NORMAL_SPEED_PASS captures=6"], log)
res.pop("log", None)
man = next(FIT.glob("*normal-speed-manifest*.json"))
m = json.loads(man.read_text(encoding="utf8"))
captures = sorted(FIT.glob("*normal-speed-*.png"))
dims = {p.name: list(Image.open(p).size) for p in captures}
runtime_j = json.loads(runtime.read_text(encoding="utf8"))
stop_j = json.loads(stop.read_text(encoding="utf8"))
walk = runtime_j["actions"]["walk"]["south"]
idle = runtime_j["actions"]["idle"]["south"]
bridge = stop_j["phase_bridges"]["south"]["phase7"]
path_for = {("walk", i): walk[i]["file"] for i in range(12)}
path_for[("idle", 0)] = idle[0]["file"]
path_for[("s1", 0)] = bridge[1]["file"]
path_for[("s2", 0)] = bridge[2]["file"]
frame_ok, sha_ok, target_ok, size_ok, fit_ok = True, True, True, True, True
for c in m["captures"]:
    exp = state_at(c["elapsed_ms"])
    frame_ok &= (c["kind"], c["frame_index"]) == exp
    target_ok &= (c["target_kind"], c["target_frame_index"]) == state_at(c["target_ms"])
    rel = path_for[exp]
    src = PKG / rel
    sha_ok &= c.get("frame_file") == rel and c.get("frame_sha256") == sha(src)
    fit_ok &= c["pivot"] == [40, 104] and abs(c["scale"] - 0.5) < 1e-9 and c["logical_height_px"] == 48 \
        and c["texture_size"] == [80, 112] and c["sprite_rect"] == [40.0, 56.0]
size_ok = len(captures) == 6 and all(v == [640, 360] for v in dims.values())
span_ok = sorted({(c["kind"], c["frame_index"]) for c in m["captures"]}) == [("idle", 0), ("s1", 0), ("s2", 0),
                                                                           ("walk", 2), ("walk", 7), ("walk", 11)]
speed_ok = all(c["elapsed_ms"] <= c["target_ms"] + 250 for c in m["captures"])
after = {str(p): sha(p) for p in [runtime, stop, gd, runner_path]}
proof = {"task": "content.char.heya.walk-south normal-speed Godot source-fit (test-only)",
         "command": cmd, "tag": TAG, "runtimeManifest": str(runtime.relative_to(R)),
         "runtimeManifestSha256": before[str(runtime)], "stopManifest": str(stop.relative_to(R)),
         "stopManifestSha256": before[str(stop)], "script": str(gd.relative_to(R)),
         "scriptSha256": before[str(gd)], "runner": str(runner_path.relative_to(R)),
         "runnerSha256": before[str(runner_path)], "godot": str(godot), "godotSha256": sha(godot),
         "log": str(log.relative_to(R)), "result": res, "captures": [str(p.relative_to(R)) for p in captures],
         "captureDimensions": dims, "manifest": str(man.relative_to(R)), "manifestSha256": sha(man),
         "normalSpeedFramesExact": frame_ok, "frameHashesExact": sha_ok, "targetStatesExact": target_ok,
         "phaseSpanExact": span_ok, "fitContractExact": fit_ok, "elapsedWithinBound": speed_ok,
         "expectedStates": {str(c["target_ms"]): list(state_at(c["target_ms"])) for c in m["captures"]},
         "runtimeAdopted": m.get("runtimeAdopted"), "artApproved": m.get("artApproved"), "testOnly": True,
         "audioDriver": "Dummy", "renderingDriver": "opengl3", "xvfb": "640x360x24",
         "note": "direct deterministic animated source-fit overlay through the existing checked runner; south walk "
                 "phases 2/11/7 then phase-7 stop s1/s2/idle f00 at 40 ms, settle 120 ms inclusive; not ordinary "
                 "actor integration, not human motion review"}
proof["passed"] = bool(res.get("passed") and size_ok and frame_ok and sha_ok and target_ok and fit_ok and span_ok
                       and speed_ok and before == after and m.get("runtimeAdopted") is False
                       and m.get("artApproved") is False)
proof_path = OUT / f"rpg-2-star-ocean-the-second_heya_walk-south_normal-speed-proof_test-only-v01_{TAG}-{FIT.name}.json"
proof_path.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf8")
print(json.dumps({"passed": proof["passed"], "captures": proof["captures"], "frame_ok": frame_ok,
                  "sha_ok": sha_ok, "target_ok": target_ok, "fit_ok": fit_ok, "speed_ok": speed_ok,
                  "dims": dims, "result": res}, indent=2))
print("HEYA_H165SW_SOUTH_WALK_NORMAL_SPEED_FIT " + ("PASS" if proof["passed"] else "FAIL"))
raise SystemExit(0 if proof["passed"] else 1)
