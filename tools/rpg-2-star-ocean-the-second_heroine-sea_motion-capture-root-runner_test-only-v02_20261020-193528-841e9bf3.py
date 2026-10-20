"""Root reproduction of DeepSeek capture. Original strict diagnostic gates retained. Fresh isolated evidence; only fixture node cleanup added."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location("ds_motion_capture", ROOT / "tools/rpg-2-star-ocean-the-second_heroine-sea_motion-capture-runner_test-only-v01_20261020-153144-3fb36c1a.py")
m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
m.PRIMARY=next(a for a in ROOT.parents if (a/"work/tooling").is_dir())
m.CL=ROOT
m.MANIFEST=ROOT/"outputs/hero-sea-motion-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_manifest_test-only-v01_20261020-192028-7e93a93c.json"
m.AUTHOR=ROOT/"tools/rpg-2-star-ocean-the-second_heroine-sea_combat-motion-author_test-only-v01_20261020-192028-9bab493d.py"
m.GODOT=m.PRIMARY/"work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe"
m.HARNESS=ROOT/"tools/rpg-2-star-ocean-the-second_heroine-sea_motion-capture-root_test-only-v02_20261020-193528-841e9bf3.gd"
m.OUT=ROOT/"outputs/hero-sea-motion-capture-v02"
m.STAMP="v02_20261020-193528-841e9bf3"
if __name__=="__main__": raise SystemExit(m.main())
