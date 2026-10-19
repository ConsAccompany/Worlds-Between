"""Template-free PCK export, then actual launch from an empty directory. No native EXE or release claim."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json, os, uuid
ROOT=Path(__file__).resolve().parents[1];PRIMARY=ROOT.parents[1]
SLUG='rpg-2-star-ocean-the-second';TOOL_TAG='20261019-191758-4650fe2a'
GODOT=PRIMARY/'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'
OUT=ROOT/'outputs/export-boundary-v01'
PROBE=ROOT/f'tools/{SLUG}_export-pack_complete-raw-boundary-probe_v01_{TOOL_TAG}.gd'
def read(p):return Path(chr(92)*2+'?'+chr(92)+str(p.resolve())).read_bytes()
def sha(p):return hashlib.sha256(read(p)).hexdigest()
def main():
    stop=PRIMARY/'work/dual01/control/rpg-2-star-ocean-the-second_dual-provider_global-stop_v01_20261019-001423-861097ca.json'
    assert not stop.exists(),'GLOBAL STOP'
    tag=datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]
    work=ROOT/'work'/('raw-pack-'+tag);work.mkdir(parents=True)
    empty=work/'empty';empty.mkdir()
    for name in ['app','local']:(work/name).mkdir()
    os.environ['APPDATA']=str(work/'app');os.environ['LOCALAPPDATA']=str(work/'local')
    out_prefix=f'{SLUG}_export-pack'
    report_path=OUT/f'{out_prefix}_canonical-boundary-results_v01_{tag}.json'
    pack=work/f'{out_prefix}_canonical-raw-boundary_v01_{tag}.pck'
    spec=importlib.util.spec_from_file_location('checked_runner',ROOT/'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    addons=ROOT/'game/addons/raw-png-export-v01'
    source_files=[ROOT/'game/project.godot',ROOT/'game/export_presets.cfg',ROOT/'game/scripts/growth_screen.gd',PROBE,Path(__file__)]+[p for p in addons.iterdir() if p.suffix in ['.gd','.cfg']]
    protected=list((ROOT/'game/assets/portraits/mvp-display-v01').glob('*'))+list((ROOT/'game/assets/portraits/female-display-v01').glob('*'))
    before={p.relative_to(ROOT).as_posix():sha(p) for p in source_files+protected}
    export_command=[str(GODOT),'--headless','--path',str(ROOT/'game'),'--export-pack','Windows Desktop',str(pack),'--quit']
    export_log=OUT/f'{out_prefix}_canonical-export-log_v01_{tag}.log'
    report={'startedUtc':datetime.now(timezone.utc).isoformat(),'sourceRawSha256':before,'exportCommand':export_command,'pack':str(pack),'notReleaseOrNativeExe':True,'artApproval':False}
    OUT.mkdir(exist_ok=True)
    exported=runner.run_checked(export_command,120,expected=['RAW_INPUT_EXPORT_FILE_COUNTS'],log_path=export_log)
    report['export']=exported;report['exportLog']=export_log.relative_to(ROOT).as_posix()
    report['packExists']=pack.is_file()
    # Checked runner return keys are tested explicitly below; no launch follows a failed export.
    okay=exported.get('passed') is True
    if okay and pack.is_file():
      assert not stop.exists(),'GLOBAL STOP before launch'
      report['packBytes']=pack.stat().st_size;report['packSha256']=sha(pack)
      assert not list(empty.iterdir()),'Launch directory must start empty'
      os.chdir(empty)
      command=[str(GODOT),'--headless','--path',str(empty),'--main-pack',str(pack),'--audio-driver','Dummy','--script',str(PROBE),'--','--management-ui-skin-pilot','--mvp-display-portraits-pilot']
      log=OUT/f'{out_prefix}_canonical-empty-pack-log_v01_{tag}.log'
      launched=runner.run_checked(command,60,expected=['PACK_COMPLETE_RAW_BOUNDARY_PROBE_OK','PACK_COMPLETE_RAW_BOUNDARY'],log_path=log)
      report['launchCommand']=command;report['cwd']=str(empty);report['launch']=launched;report['launchLog']=log.relative_to(ROOT).as_posix()
      report['observations']=[]
      for line in read(log).decode('utf-8').splitlines():
        if line.startswith(('PACK_RAW_PNG_PLUGIN ','PACK_HELPER_DIAG ','PACK_COMPLETE_RAW_BOUNDARY ')):
          report['observations'].append(json.loads(line.split(' ',1)[1]))
      okay=launched.get('passed') is True
    report['protectedBytesUnchanged']=all(sha(ROOT/path)==value for path,value in before.items())
    report['passed']=bool(okay and report['protectedBytesUnchanged'])
    report['endedUtc']=datetime.now(timezone.utc).isoformat()
    report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'passed':report['passed'],'report':str(report_path),'pack':str(pack),'packBytes':report.get('packBytes')},indent=2))
    if not report['passed']:raise SystemExit(1)
if __name__=='__main__':main()
