import importlib.util,json,os,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8');C=Path(__file__).resolve().parents[1];P=C.parents[1]
STOP=P/'work/dual01/control/rpg-2-star-ocean-the-second_dual-provider_global-stop_v01_20261019-001423-861097ca.json'
if STOP.exists():raise SystemExit('Global stop exists; no mutation.')
TAG='20261019-233752-d81336a7';folder=C/'outputs/fexp-clear-plaza-v01';folder.mkdir(exist_ok=True)
work=P/'work/dual02/fexp-clear-plaza-d81336a7';work.mkdir(exist_ok=True)
os.environ['APPDATA']=str(work/'appdata');os.environ['LOCALAPPDATA']=str(work/'localappdata')
report=folder/('rpg-2-star-ocean-the-second_female-exploration_clear-plaza-report_unapproved-v01_'+TAG+'.json')
runner=C/'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py'
spec=importlib.util.spec_from_file_location('checked',str(runner));checked=importlib.util.module_from_spec(spec);spec.loader.exec_module(checked)
command=[str(P/'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'),'--path',str(C/'game'),'--audio-driver','Dummy','--resolution','640x360','--position','2000,100','--script',str(C/'tools/rpg-2-star-ocean-the-second_female-exploration_clear-plaza-critical-poses_v01_20261019-233752-d81336a7.gd'),'--',str(folder),str(report),'--female-complete-exploration-pilot']
result=checked.run_checked(command,60,['FEXP_CLEAR_PLAZA_OK captures=2','FEXP_CLEAR_PLAZA_AUDIO_MIX_BOUNDARIES 2'],str(folder/('rpg-2-star-ocean-the-second_female-exploration_clear-plaza-run_unapproved-v01_'+TAG+'.log')))
(folder/('rpg-2-star-ocean-the-second_female-exploration_clear-plaza-receipt_unapproved-v01_'+TAG+'.json')).write_text(json.dumps({'command':command,**result},indent=2),encoding='utf-8',newline='\n')
print(result['log']);print('PASSED',result['passed'],result['reason']);raise SystemExit(0 if result['passed'] else 1)
