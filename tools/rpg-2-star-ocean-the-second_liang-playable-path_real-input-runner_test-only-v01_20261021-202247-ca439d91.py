"""Bound the scripted real-input Liang path; isolate saves and retain source-bound evidence.

Not a human playtest or artistic/default approval. Movie mode preserves the engine's
authored frame rate; encoding or excerpts must not speed up the recorded motion.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]
RUNNER=ROOT/'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py'
HARNESS=ROOT/'tools/rpg-2-star-ocean-the-second_liang-playable-path_real-input-flow_test-only-v01_20261021-202247-ca439d91.gd'
GODOT=next((r/'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe' for r in [ROOT,*ROOT.parents] if (r/'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe').is_file()),None)

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--language',choices=['en','zh'],required=True)
    a.add_argument('--appearance',choices=['male','female'],default='male')
    a.add_argument('--scenario',choices=['victory','defeat-boundary'],required=True)
    a.add_argument('--fps',type=int,choices=[30,60],default=60)
    a.add_argument('--timeout',type=float,default=120)
    a.add_argument('--movie',action='store_true')
    args=a.parse_args()
    tag=time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]
    out=ROOT/'outputs/lpath30'/('rif-'+tag)
    profile=ROOT/'work/lpath30-profiles'/tag
    for path in [out,profile/'appdata',profile/'localappdata']:
        path.mkdir(parents=True,exist_ok=False)
    os.environ['APPDATA']=str(profile/'appdata')
    os.environ['LOCALAPPDATA']=str(profile/'localappdata')
    os.environ.pop('ANTHROPIC_API_KEY',None)
    spec=importlib.util.spec_from_file_location('checked',RUNNER)
    checked=importlib.util.module_from_spec(spec);spec.loader.exec_module(checked)
    command=[str(GODOT),'--path',str(ROOT/'game'),'--resolution','640x360','--audio-driver','Dummy','--fixed-fps',str(args.fps)]
    movie=profile/f'rpg-2-star-ocean-the-second_liang-playable-path_actual-input-normal-{args.fps}fps_{tag}.avi'
    if args.movie:
        command+=['--write-movie',str(movie)]
    command+=['--script',str(HARNESS),'--',out.as_posix(),args.language,tag,profile.as_posix(),args.scenario,'preview',args.appearance]
    log=out/f'rpg-2-star-ocean-the-second_liang-rif_{args.language}-{args.scenario}_godot-log_{tag}.log'
    result=checked.run_checked(command,args.timeout,['LRIF_ALL_PASS'],str(log))
    receipt={'tag':tag,'language':args.language,'appearance':args.appearance,'scenario':args.scenario,'mode':'preview',
        'passed':result['passed'],'reason':result['reason'],'exitCode':result['exitCode'],'elapsedSeconds':result['elapsedSeconds'],
        'fixedFps':args.fps,'command':command,'harnessSha256Raw':hashlib.sha256(HARNESS.read_bytes()).hexdigest(),
        'runnerSha256Raw':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'profile':str(profile),
        'movie':str(movie) if args.movie else None,'humanPlaytest':False,'artApproved':False,'defaultAdoption':False}
    target=out/f'rpg-2-star-ocean-the-second_liang-rif_{args.language}-{args.scenario}_receipt_{tag}.json'
    target.write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
    for line in result['log'].splitlines():
        if line.startswith('LRIF') or 'ERROR' in line:
            print(line)
    print('LIANG_RIF_RUN', 'PASS' if result['passed'] else 'FAIL',result['reason'],tag,result['elapsedSeconds'])
    print('RECEIPT',target.relative_to(ROOT).as_posix())
    return 0 if result['passed'] else 1

if __name__=='__main__':
    raise SystemExit(main())
