"""Bounded Godot normal-speed four-direction idle source-fit (test-only, EN/ZH, city/ruins).

Uses the checked runner (finite deadline + diagnostic stop), Xvfb 640x360, OpenGL3 and Dummy audio.
No runtime adoption, default change or art approval. Writes only under outputs/heya-i159/fit/.
"""
import hashlib, importlib.util, json, os, shutil
from pathlib import Path
from PIL import Image

R = Path(__file__).resolve().parents[1]
TAG = "20261024-140235-a159i001"
OUT = R / "outputs/heya-i159" / "fit"
OUT.mkdir(parents=True, exist_ok=True)
FIT = OUT / "capture"
n = 1
while FIT.exists() and any(FIT.iterdir()):
    n += 1
    FIT = OUT / f"capture-r{n}"
FIT.mkdir(parents=True, exist_ok=True)
HOMEDIR = R / "outputs/heya-i159/godot-home"
for sub in ("home", "config", "data", "cache", "run", "tmp"):
    (HOMEDIR / sub).mkdir(parents=True, exist_ok=True)
os.environ.update(TMPDIR=str(HOMEDIR / "tmp"), HOME=str(HOMEDIR / "home"),
                  XDG_CONFIG_HOME=str(HOMEDIR / "config"), XDG_DATA_HOME=str(HOMEDIR / "data"),
                  XDG_CACHE_HOME=str(HOMEDIR / "cache"), XDG_RUNTIME_DIR=str(HOMEDIR / "run"))
runtime = next((R / "game/assets/characters/heya-native-v01/idle").glob("*sprite-set-runtime*.json")).resolve()
gd = R / "tools/rpg-2-star-ocean-the-second_heya_idle-four-direction_normal-speed-fit_test-only-v01_20261024-140235-a159i001.gd"
runner_path = R / "tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py"
godot = Path("/home/kel/projects/worlds-between/tooling/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


spec = importlib.util.spec_from_file_location("checked", runner_path)
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
before = {str(p): sha(p) for p in [runtime, gd, runner_path]}
cmd = ["xvfb-run", "-a", "-s", "-screen 0 640x360x24", str(godot), "--path", str(R / "game"),
       "--resolution", "640x360", "--rendering-driver", "opengl3", "--audio-driver", "Dummy",
       "--script", str(gd), "--", str(runtime), str(FIT.resolve()), TAG]
log = OUT / f"normal-speed-{FIT.name}.runner.log"
res = runner.run_checked(cmd, 75, ["HEYA_I159_IDLE_NORMAL_SPEED_PASS captures=12"], log)
res.pop("log", None)
man = next(FIT.glob("*normal-speed-manifest*.json"))
m = json.loads(man.read_text(encoding="utf8"))
captures = sorted(FIT.glob("*normal-speed-*.png"))
dims = {p.name: list(Image.open(p).size) for p in captures}
expected = {100: 0, 1000: 2, 1350: 3}

def frame_at(ms):
    acc = 0
    for i, dur in enumerate([700, 200, 400, 200]):
        acc += dur
        if ms < acc:
            return i
    return 3

frame_ok = all(all(v == frame_at(c["elapsed_ms"]) for v in c["frame_indices"].values()) for c in m["captures"])
span_ok = sorted({v for c in m["captures"] for v in c["frame_indices"].values()}) == [0, 2, 3]
speed_ok = all(c["elapsed_ms"] <= c["target_ms"] + 250 for c in m["captures"])
after = {str(p): sha(p) for p in [runtime, gd, runner_path]}
proof = {"task": "content.char.heya.idle-anim normal-speed four-direction source-fit (test-only)",
         "command": cmd, "tag": TAG, "runtimeManifest": str(runtime.relative_to(R)),
         "runtimeManifestSha256": before[str(runtime)], "script": str(gd.relative_to(R)),
         "scriptSha256": before[str(gd)], "runner": str(runner_path.relative_to(R)),
         "runnerSha256": before[str(runner_path)], "godot": str(godot), "godotSha256": sha(godot),
         "log": str(log.relative_to(R)), "result": res, "captures": [str(p.relative_to(R)) for p in captures],
         "captureDimensions": dims, "manifest": str(man.relative_to(R)), "manifestSha256": sha(man),
         "normalSpeedFramesExact": frame_ok, "phaseSpanExact": span_ok, "elapsedWithinBound": speed_ok,
         "expectedFrameAtTarget": {str(k): v for k, v in expected.items()},
         "runtimeAdopted": m.get("runtimeAdopted"), "artApproved": m.get("artApproved"), "testOnly": True,
         "audioDriver": "Dummy", "renderingDriver": "opengl3", "xvfb": "640x360x24",
         "note": "direct deterministic animated source-fit overlay through the existing checked runner; four directions "
                 "play simultaneously at 1.5 s normal-speed loop; not ordinary actor integration, not human motion review"}
proof["passed"] = bool(res.get("passed") and len(captures) == 12 and all(v == [640, 360] for v in dims.values())
                       and frame_ok and span_ok and speed_ok and before == after and m.get("runtimeAdopted") is False
                       and m.get("artApproved") is False)
proof_path = OUT / f"rpg-2-star-ocean-the-second_heya_idle-four-direction_normal-speed-proof_test-only-v01_{TAG}-{FIT.name}.json"
proof_path.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf8")
print(json.dumps({"passed": proof["passed"], "captures": proof["captures"], "frame_ok": frame_ok,
                  "speed_ok": speed_ok, "dims": dims, "result": res}, indent=2))
print("HEYA_I159_IDLE_NORMAL_SPEED_FIT " + ("PASS" if proof["passed"] else "FAIL"))
raise SystemExit(0 if proof["passed"] else 1)
