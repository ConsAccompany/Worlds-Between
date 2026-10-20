"""Unfiltered checked Godot run with fresh per-run APPDATA and LOCALAPPDATA. No certificate filtering."""
from pathlib import Path
import importlib.util,datetime,uuid,json,os,sys
D=Path(__file__).resolve().parents[1];P=next(x for x in D.parents if (x/"work/tooling/godot-4-7-2").is_dir());C=P/"work/max0840-sentry-sync"
assert not (P/"work/dual01/control/rpg-2-star-ocean-the-second_dual-provider_global-stop_v01_20261019-001423-861097ca.json").exists()
tag=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")+"-"+uuid.uuid4().hex[:8];O=D/"outputs/ui-root-v02";w=D/"work"/("ui-root-"+tag)
(w/"app").mkdir(parents=True);(w/"local").mkdir();os.environ["APPDATA"]=str(w/"app");os.environ["LOCALAPPDATA"]=str(w/"local")
s=importlib.util.spec_from_file_location("rr",C/"tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py");rr=importlib.util.module_from_spec(s);s.loader.exec_module(rr)
t=next((D/"game/tests").glob("*root-runtime-check*.gd"));cmd=[str(P/"work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe"),"--path",str(D/"game"),"--audio-driver","Dummy","--script","res://tests/"+t.name,"--",str(O)]
r=rr.run_checked(cmd,100,expected=["CHARACTER_UI_RUNTIME","CHARACTER_UI_AUDIO_MIX_BOUNDARIES 2"],log_path=O/("rpg-2-star-ocean-the-second_character-ui-portraits_root-unfiltered-log_v02_"+tag+".log"))
(O/("rpg-2-star-ocean-the-second_character-ui-portraits_root-unfiltered-result_v02_"+tag+".json")).write_text(json.dumps({"command":cmd,"checkedRunner":r},indent=2),encoding="utf-8");print(json.dumps(r));sys.exit(0 if r["passed"] else 1)
