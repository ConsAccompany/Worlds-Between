from pathlib import Path
import importlib.util,datetime,uuid,json,os,sys
C=Path(__file__).resolve().parents[1];P=C.parents[1];tag=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")+"-"+uuid.uuid4().hex[:8];O=C/"outputs/fexp-merged-v01";w=C/"work"/("fcx-run-"+tag);(w/"app").mkdir(parents=True);(w/"local").mkdir();os.environ["APPDATA"]=str(w/"app");os.environ["LOCALAPPDATA"]=str(w/"local")
assert not (P/"work/dual01/control/rpg-2-star-ocean-the-second_dual-provider_global-stop_v01_20261019-001423-861097ca.json").exists()
s=importlib.util.spec_from_file_location("rr",C/"tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py");rr=importlib.util.module_from_spec(s);s.loader.exec_module(rr)
probe=next((C/"tools").glob("*normal-cli-pack-probe*.gd"));godot=str(P/"work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe");prefix="rpg-2-star-ocean-the-second_female-complete-explore_";mode=sys.argv[1] if len(sys.argv)>1 else "normal";report={"mode":mode,"tag":tag}
if mode=="pack":
 pack=w/(prefix+"engine-pack_v01_"+tag+".pck")
 r=rr.run_checked([godot,"--headless","--path",str(C/"game"),"--export-pack","Windows Desktop",str(pack),"--quit"],120,expected=["RAW_INPUT_EXPORT_FILE_COUNTS"],log_path=O/(prefix+"pack-export-log_v01_"+tag+".log"));report["export"]=r
 if not r["passed"]: print(json.dumps(r));raise SystemExit(1)
 empty=w/"empty";empty.mkdir();os.chdir(empty);base=["--path",str(empty),"--main-pack",str(pack)];import hashlib
 report["pack"]={"path":str(pack),"sha256":hashlib.sha256(pack.read_bytes()).hexdigest(),"bytes":pack.stat().st_size}
else:base=["--path",str(C/"game")]
command=[godot]+base+["--audio-driver","Dummy","--fixed-fps","60","--script",str(probe),"--",str(O),str(O/(prefix+mode+"-report_v01_"+tag+".json")),"--female-complete-exploration-pilot"]
r=rr.run_checked(command,100,expected=["FEXP_NORMAL_CLI_PACK_OK cases=6"],log_path=O/(prefix+mode+"-log_v01_"+tag+".log"));report["run"]=r;report["command"]=command;(O/(prefix+mode+"-runner_v01_"+tag+".json")).write_text(json.dumps(report,indent=2),encoding="utf-8");print(json.dumps(r));raise SystemExit(0 if r["passed"] else 1)
