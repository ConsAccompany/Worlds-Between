from pathlib import Path
import datetime,uuid,sys,os,json,importlib.util
C=Path(__file__).resolve().parents[1];P=C.parents[1]
spec=importlib.util.spec_from_file_location('checked',C/'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py');checked=importlib.util.module_from_spec(spec);spec.loader.exec_module(checked)
mode=sys.argv[1];assert mode in ['default','native'];tag=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8];out=C/'outputs/outskirts-root13';out.mkdir(exist_ok=True)
for k,n in [('APPDATA','a'),('LOCALAPPDATA','l')]:
 folder=P/'work/dual12/profiles'/mode/n;folder.mkdir(parents=True,exist_ok=True);os.environ[k]=str(folder)
cmd=[str(P/'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'),'--path',str(C/'game'),'--resolution','640x360','--fixed-fps','60','--audio-driver','Dummy','--script',str(C/'tools/rpg-2-star-ocean-the-second_yonkers-outskirts_native-root-walkthrough_v01_20261021-000137-89d8d457.gd'),'--',str(out),tag,mode]
if mode=='native':cmd.append('--yonkers-outskirts-native-v01')
r=checked.run_checked(cmd,90,expected=['OUTSKIRTS_NATIVE_PASS'],log_path=out/f'rpg-2-star-ocean-the-second_yonkers-outskirts_runtime-raw_{mode}_{tag}.log');print(json.dumps({'passed':r['passed'],'reason':r['reason'],'tail':r['log'][-2200:],'tag':tag}));assert r['passed']
