"""Bounded Heya NORTH source-fit capture through the existing generic scene-fit script and checked runner.

Test-only overlay: no runtime adoption, no defaults, no interaction or art approval. Uses Xvfb 640x360,
OpenGL3 and Dummy audio. Writes only under outputs/heya-n152/fit/.
"""
import hashlib, importlib.util, json, os
from pathlib import Path
from PIL import Image

R = Path(__file__).resolve().parents[1]
TAG = "20261024-134500-h152n001"
OUT = R / "outputs/heya-n152"
FIT = OUT / "fit"
if FIT.exists() and any(FIT.iterdir()):
    n = 2
    while (OUT / f"fit-r{n}").exists() and any((OUT / f"fit-r{n}").iterdir()):
        n += 1
    FIT = OUT / f"fit-r{n}"
FIT.mkdir(parents=True, exist_ok=True)
TMP = OUT / "tmp"
TMP.mkdir(parents=True, exist_ok=True)
HOMEDIR = OUT / "godot-home"
for sub in ("home", "config", "data", "cache", "run"):
    (HOMEDIR / sub).mkdir(parents=True, exist_ok=True)
os.environ["TMPDIR"] = str(TMP)
os.environ["HOME"] = str(HOMEDIR / "home")
os.environ["XDG_CONFIG_HOME"] = str(HOMEDIR / "config")
os.environ["XDG_DATA_HOME"] = str(HOMEDIR / "data")
os.environ["XDG_CACHE_HOME"] = str(HOMEDIR / "cache")
os.environ["XDG_RUNTIME_DIR"] = str(HOMEDIR / "run")
source = next((R / "game/assets/characters/heya-native-v01/north").glob("*heya_north-static*.png")).resolve()
gd = R / "tools/rpg-2-star-ocean-the-second_native-static_scene-fit-capture_test-only-v01_20261021-235007-514b9771.gd"
runner_path = R / "tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py"
godot = Path("/home/kel/projects/worlds-between/tooling/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


spec = importlib.util.spec_from_file_location("checked", runner_path)
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
before = sha(source)
cmd = ["xvfb-run", "-a", "-s", "-screen 0 640x360x24", str(godot), "--path", str(R / "game"),
       "--resolution", "640x360", "--rendering-driver", "opengl3", "--audio-driver", "Dummy",
       "--script", str(gd), "--", str(source), str(FIT.resolve()), TAG, "heya"]
i = 1
while (OUT / ("fit.runner.log" if i == 1 else f"fit-r{i}.runner.log")).exists():
    i += 1
log = OUT / ("fit.runner.log" if i == 1 else f"fit-r{i}.runner.log")
result = runner.run_checked(cmd, 90, ["JIANG37_SOURCE_FIT_PASS captures=4"], log)
result.pop("log", None)
man = next(FIT.glob("*source-fit-manifest*.json"))
m = json.loads(man.read_text(encoding="utf8"))
captures = sorted(FIT.glob("*source-fit-*.png"))
dims = {p.name: list(Image.open(p).size) for p in captures}
proof = {"task": "content.char.heya.static-north test-only source-fit", "command": cmd, "tag": TAG,
         "source": str(source.relative_to(R)), "sourceSha256": before, "sourceUnchanged": sha(source) == before,
         "script": str(gd.relative_to(R)), "scriptSha256": sha(gd),
         "runner": str(runner_path.relative_to(R)), "runnerSha256": sha(runner_path),
         "godot": str(godot), "godotSha256": sha(godot),
         "log": str(log.relative_to(R)), "result": result,
         "captures": [str(p.relative_to(R)) for p in captures], "captureDimensions": dims,
         "manifest": str(man.relative_to(R)), "manifestSha256": sha(man),
         "manifestCaptures": len(m.get("captures", [])),
         "runtimeAdopted": m.get("runtimeAdopted"), "artApproved": m.get("artApproved"),
         "testOnly": True, "note": "direct deterministic source-fit overlay through the existing generic harness "
                                   "(scifi.city bright + scifi.ruins dark, en/zh); not ordinary actor integration, "
                                   "motion review or creator art approval"}
(OUT / f"rpg-2-star-ocean-the-second_heya_north_source-fit-proof_test-only-v01_{TAG}-{FIT.name}.json").write_text(
    json.dumps(proof, indent=2) + "\n", encoding="utf8")
ok = (result.get("passed") and len(captures) == 4 and all(v == [640, 360] for v in dims.values())
      and proof["sourceUnchanged"] and m.get("runtimeAdopted") is False and m.get("artApproved") is False)
print(json.dumps({"passed": ok, "captures": proof["captures"], "dimensions": dims,
                  "sourceUnchanged": proof["sourceUnchanged"], "result": result}, indent=2))
print("HEYA_N152_NORTH_SOURCE_FIT " + ("PASS" if ok else "FAIL"))
raise SystemExit(0 if ok else 1)
