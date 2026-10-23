"""Producer-side runs of the M8 city integration test through the checked runner (finite 120 s, Dummy audio)."""
import datetime
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys

R = pathlib.Path("/home/kel/projects/worlds-between/repo")
W = R / "work/m8reg63"
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
spec = importlib.util.spec_from_file_location("checked", R / "tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py")
checked = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checked)
godot = str(R.parent / "tooling/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64")
test = "res://tests/m8_city_integration_smoke.gd"
mode = sys.argv[1] if len(sys.argv) > 1 else "headless"
negatives = ["SOURCE", "SAME_ID_SET", "BREATHING", "SCALE", "PIVOT", "DIRECTION"]
if mode == "headless":
    command = [godot, "--headless", "--audio-driver", "Dummy", "--path", str(R / "game"), "--script", test]
else:
    evidence = W / f"renders-{stamp}"
    os.environ["WB_CITY_EVIDENCE_DIR"] = str(evidence)
    command = ["xvfb-run", "-a", "-s", "-screen 0 1280x720x24", godot, "--audio-driver", "Dummy", "--rendering-driver", "opengl3", "--path", str(R / "game"), "--script", test]
log = W / f"{mode}-{stamp}.log"
source_hash = hashlib.sha256((R / "game/tests/m8_city_integration_smoke.gd").read_bytes()).hexdigest()
result = checked.run_checked(command, 120, expected=["M8_CITY_INTEGRATION_OK"], log_path=log)
text = result.pop("log")
markers = {n: text.count(f"M8_NEGATIVE_{n}_REJECTED:") for n in negatives}
markers["ACTIVE_SET_VERIFIED"] = text.count("M8_ACTIVE_SET_VERIFIED:")
bad = [m for m in ("SCRIPT ERROR", "Parse Error", "CITY_INTEGRATION_FAILED") if m in text]
result.update(mode=mode, command=command, log=str(log.relative_to(R)), testSHA256=source_hash, negativeMarkers=markers, diagnostics=bad,
              head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=R, text=True).strip())
if mode != "headless" and evidence.exists():
    result["renders"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(evidence.iterdir())}
(W / f"{mode}-{stamp}-summary.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k != "command"}, indent=1))
print(text[-1500:])
