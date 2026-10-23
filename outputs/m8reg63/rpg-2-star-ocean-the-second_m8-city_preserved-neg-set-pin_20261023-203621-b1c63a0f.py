"""Mutated-copy negative: wrong pinned set-manifest sha256 for the male set must fail before the loader (work/ copy only)."""
import hashlib
import importlib.util
import json
import pathlib

R = pathlib.Path("/home/kel/projects/worlds-between/repo")
W = R / "work/m8reg63"
src = (R / "game/tests/m8_city_integration_smoke.gd").read_text(encoding="utf-8")
good = "6e3df976b3def0fdb56e1bd738dc13076e60108bf7b16b20a15824cd07dfd2da"
assert src.count(good) == 1
mutant = W / "neg-set-pin-mutant.gd"
mutant.write_text(src.replace(good, "0" + good[1:]), encoding="utf-8")
spec = importlib.util.spec_from_file_location("checked", R / "tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py")
checked = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checked)
godot = str(R.parent / "tooling/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64")
log = W / "neg-set-pin.log"
command = [godot, "--headless", "--audio-driver", "Dummy", "--path", str(R / "game"), "--script", str(mutant)]
result = checked.run_checked(command, 120, expected=["M8_CITY_INTEGRATION_OK"], log_path=log)
text = result.pop("log")
want = "CITY_INTEGRATION_FAILED: active hero source male: set manifest bytes are not pinned"
out = {"passedAsNegative": (not result["passed"]) and want in text and "SCRIPT ERROR" not in text,
       "runner": result, "mutantSHA256": hashlib.sha256(mutant.read_bytes()).hexdigest()}
(W / "neg-set-pin-summary.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
print(json.dumps(out, indent=1))
print(text[-600:])
