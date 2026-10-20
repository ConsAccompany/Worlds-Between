"""Bounded native arena production proof, explicit source pins and ordinary-context profiles."""
from pathlib import Path
import datetime,importlib.util,json,os,sys,uuid
C=Path(__file__).resolve().parents[1];P=C.parents[1]
s=importlib.util.spec_from_file_location('checked',C/'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py');checked=importlib.util.module_from_spec(s);s.loader.exec_module(checked)
def main():
 mode=sys.argv[1];assert mode in ['default','plate','native']
 tag=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8];out=C/'outputs/benv12';out.mkdir(exist_ok=True)
 for key,sub in [('APPDATA','a'),('LOCALAPPDATA','l')]:
  folder=P/'work/dual11/profiles'/mode/sub;folder.mkdir(parents=True,exist_ok=True);os.environ[key]=str(folder)
 log=out/f'rpg-2-star-ocean-the-second_battle-native_gameplay-raw_{mode}_{tag}.log'
 cmd=[str(P/'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'),'--path',str(C/'game'),'--resolution','640x360','--audio-driver','Dummy','--fixed-fps','60','--script',str(C/'tools/rpg-2-star-ocean-the-second_battle-native_normal-arena-root-check_v01_20261020-230547-9a3d6edc.gd'),'--',str(out),tag,mode]
 if mode=='native':cmd.append('--battle-native-environment-v01')
 result=checked.run_checked(cmd,65,expected=['BATTLE_NATIVE_ROOT_PASS'],log_path=log)
 print(json.dumps({'passed':result['passed'],'reason':result['reason'],'log':str(log),'tail':result['log'][-1600:]}));assert result['passed']
if __name__=='__main__':main()
