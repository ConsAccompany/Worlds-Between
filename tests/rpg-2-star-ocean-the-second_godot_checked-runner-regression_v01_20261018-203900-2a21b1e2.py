"""Regression for the observed compiler-error + non-terminating SceneTree test incident."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py'
spec=importlib.util.spec_from_file_location('checked_runner', TOOL)
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)

def main():
    checks=[]
    def case(name, code, reason, expected=(), timeout=4):
        result=runner.run_checked([sys.executable,'-u','-c',code],timeout,expected)
        assert result['reason']==reason,(name,result)
        assert result['passed']==(reason is None),(name,result)
        checks.append({'case':name,'pass':True,'reason':result['reason'],'seconds':result['elapsedSeconds']})
        return result
    case('success-with-required-marker',"print('EXPECTED_OK')",None,['EXPECTED_OK'])
    case('nonzero-even-with-marker',"import sys;print('EXPECTED_OK');sys.exit(7)",'exit-code',['EXPECTED_OK'])
    case('missing-required-marker',"print('different output')",'missing-marker',['EXPECTED_OK'])
    case('script-error-even-exit-zero',"print('SCRIPT ERROR: Parse Error: unknown type')",'diagnostic')
    case('colored-compiler-error',"print('\\x1b[31mSCRIPT ERROR: Parse Error: bad type\\x1b[0m')",'diagnostic')
    r=case('compiler-error-and-hang',"import time;print('SCRIPT ERROR: Parse Error: cannot infer type',flush=True);time.sleep(60)",'diagnostic',timeout=4)
    assert r['elapsedSeconds']<3,r
    r=case('partial-line-and-hang-timeout',"import sys,time;sys.stdout.write('partial');sys.stdout.flush();time.sleep(60)",'timeout',timeout=.4)
    assert .3<=r['elapsedSeconds']<3,r
    # The failing run must not kill another independently started process.
    opts={'creationflags':subprocess.CREATE_NO_WINDOW} if os.name=='nt' else {}
    other=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'],**opts)
    try:
        case('unrelated-process-preserved',"import time;print('ERROR: failed',flush=True);time.sleep(60)",'diagnostic')
        assert other.poll() is None,'Unrelated process was terminated'
    finally:
        other.terminate();other.wait(timeout=5)
    with tempfile.TemporaryDirectory(prefix='rpg-2-star-ocean-the-second_checked-runner-') as folder:
        log=Path(folder)/'rpg-2-star-ocean-the-second_test_child-log_v01_20261018-203900-2a21b1e2.log'
        r=runner.run_checked([sys.executable,'-u','-c',"print('EXPECTED_OK')"],4,['EXPECTED_OK'],log)
        assert r['passed'] and log.read_text()=='EXPECTED_OK\n'
        try:
            runner.run_checked([sys.executable,'-c',"print('overwrite')"],4,log_path=log)
        except FileExistsError:
            pass
        else:
            raise AssertionError('Existing evidence log was overwritten')
        assert log.read_text()=='EXPECTED_OK\n'
        checks.append({'case':'log-preserved-and-overwrite-refused','pass':True})
    for timeout in (0,-1,float('nan'),float('inf')):
        try:runner.run_checked([sys.executable,'-c',"print('bad')"],timeout)
        except ValueError:pass
        else:raise AssertionError('Nonpositive timeout accepted')
    checks.append({'case':'nonpositive-or-nonfinite-timeout-refused','pass':True})
    print(json.dumps({'passed':len(checks),'failed':0,'checks':checks},indent=2))

if __name__=='__main__':main()
