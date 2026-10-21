from pathlib import Path
import datetime,uuid,sys,os,json,importlib.util
C=Path(__file__).resolve().parents[1];P=C.parents[1]
s=importlib.util.spec_from_file_location('checked',C/'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py');checked=importlib.util.module_from_spec(s);s.loader.exec_module(checked)
mode=sys.argv[1];assert mode in ['default','legacy'];tag=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8];out=C/'outputs/outskirts-adopt14';out.mkdir(exist_ok=True)
for k,n in [('APPDATA','a'),('LOCALAPPDATA','l')]:
 folder=P/'work/dual13/profiles'/mode/n;folder.mkdir(parents=True,exist_ok=True);os.environ[k]=str(folder)
cmd=[str(P/'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'),'--path',str(C/'game'),'--resolution','640x360','--fixed-fps','60','--audio-driver','Dummy','--script',str(C/'tools/rpg-2-star-ocean-the-second_yonkers-outskirts_default-adoption-walkthrough_v01_20261021-005428-1631f133.gd'),'--',str(out),tag,mode]
if mode=='legacy':cmd.append('--yonkers-outskirts-legacy')
r=checked.run_checked(cmd,90,expected=['OUTSKIRTS_DEFAULT_PASS'],log_path=out/f'rpg-2-star-ocean-the-second_yonkers-outskirts-adopted_runtime-raw_{mode}_{tag}.log');print(json.dumps({'passed':r['passed'],'reason':r['reason'],'tail':r['log'][-1000:],'tag':tag,'noArtOptInFlag':mode=='default'}));assert r['passed']
