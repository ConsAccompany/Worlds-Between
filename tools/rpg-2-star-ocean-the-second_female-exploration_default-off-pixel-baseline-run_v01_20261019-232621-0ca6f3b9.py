import importlib.util,json,os,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
C=Path(__file__).resolve().parents[1];P=C.parents[1]
STOP=P/'work/dual01/control/rpg-2-star-ocean-the-second_dual-provider_global-stop_v01_20261019-001423-861097ca.json'
if STOP.exists():raise SystemExit('Global stop exists; no mutation.')
TAG='20261019-232621-0ca6f3b9'
folder=C/'outputs/fexp-default-off-baseline-v01';folder.mkdir(exist_ok=True)
work=P/'work/dual02/fexp-default-off-0ca6f3b9';work.mkdir(exist_ok=True)
os.environ['APPDATA']=str(work/'appdata');os.environ['LOCALAPPDATA']=str(work/'localappdata')
report=folder/('rpg-2-star-ocean-the-second_female-exploration_default-off-report_baseline-v01_'+TAG+'.json')
runner=C/'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py'
spec=importlib.util.spec_from_file_location('checked',str(runner));checked=importlib.util.module_from_spec(spec);spec.loader.exec_module(checked)
command=[str(P/'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'),'--path',str(C/'game'),'--audio-driver','Dummy','--resolution','640x360','--position','2000,100','--script',str(C/'tools/rpg-2-star-ocean-the-second_female-exploration_default-off-pixel-baseline_v01_20261019-232621-0ca6f3b9.gd'),'--',str(folder),str(report)]
log=folder/('rpg-2-star-ocean-the-second_female-exploration_default-off-run_baseline-v01_'+TAG+'.log')
result=checked.run_checked(command,90,['FEXP_DEFAULT_OFF_OK cases=6 repeatDiffPixels=0','FEXP_AUDIO_CLEANUP_MIX_BOUNDARIES 2'],str(log))
(folder/('rpg-2-star-ocean-the-second_female-exploration_default-off-run-receipt_baseline-v01_'+TAG+'.json')).write_text(json.dumps({'command':command,**result},indent=2),encoding='utf-8',newline='\n')
print(result['log']);print('PASSED',result['passed'],result['reason']);raise SystemExit(0 if result['passed'] else 1)
