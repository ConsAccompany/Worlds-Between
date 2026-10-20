import sys,os,json,subprocess,hashlib,importlib.util,uuid
from pathlib import Path
from datetime import datetime,timezone
def lp(p):return Path('\\\\?\\'+str(p.resolve()))
C=Path(__file__).resolve().parents[1];P=C.parents[1];D=P/'work/dual06/ds-pack'
tag=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8];out=C/'outputs/hero-sea-contact-root-v01'/('combined-'+tag);out.mkdir()
spec=importlib.util.spec_from_file_location('checked',C/'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py');check=importlib.util.module_from_spec(spec);spec.loader.exec_module(check)
godot=P/'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe';results=[]
def run(name,root,script=None,extra=(),headless=True,marker=None,editor=False):
 env=dict(os.environ)
 for k in ['APPDATA','LOCALAPPDATA']:
  p=P/'work/dual06/profiles'/tag/(name+'-'+k);p.mkdir(parents=True);env[k]=str(p)
 cmd=[str(godot)]+(['--headless'] if headless else ['--resolution','640x360','--position','2000,100','--audio-driver','Dummy'])+['--path',str(root/'game')]
 if editor:cmd+=['--editor','--import','--quit']
 if script:cmd+=['--script',str(root/script)]
 if extra:cmd+=['--']+list(extra)
 # checked runner inherits this isolated process environment, restored afterwards.
 old=dict(os.environ);os.environ.clear();os.environ.update(env)
 log=out/('rpg-2-star-ocean-the-second_heroine-contact_'+name+'_root-v01_'+tag+'.log')
 try:r=check.run_checked(cmd,100,expected=([marker] if marker else []),log_path=lp(log))
 finally:os.environ.clear();os.environ.update(old)
 results.append({k:v for k,v in r.items() if k!='log'}|{'name':name,'command':cmd,'log':log.relative_to(C).as_posix(),'warnings':[x for x in r['log'].splitlines() if 'WARNING' in x]})
 print(name,r['passed'],r['reason'],r['log'].splitlines()[-3:],flush=True)
 assert r['passed'],r['log'][-3000:]
legacy='game/tests/rpg-2-star-ocean-the-second_combat-sprite-set_pilot-check-capture_v01_20261018-153656-9efd4413.gd'
run('base-import',D,editor=True)
base=out/'base-captures';base.mkdir();run('base-capture',D,legacy,['--baseline-only','--capture-dir='+str(base)],False,'COMBAT_SET_PILOT BASELINE PASS')
current=out/'combined-captures';current.mkdir();run('combined-legacy-windowed',C,legacy,['--baseline-dir='+str(base),'--capture-dir='+str(current)],False,'COMBAT_SET_PILOT PASS')
run('combined-contact80',C,'tools/rpg-2-star-ocean-the-second_heroine-contact_timing-check_v01_20261020-203500-c7e41a2d.gd',marker='HEROINE_CONTACT PASS checks=80')
run('combined-rational220',C,'tools/rpg-2-star-ocean-the-second_combat-rational-clock_root-check_v01_20261020-201636-582fa0ef.gd',marker='ROOT_RATIONAL_CLOCK_PASS checks=220')
original=C/'outputs/combat-half-scale-v01/rpg-2-star-ocean-the-second_combat-half-scale_check-report_v01_20261020-154048-7d4bddce.json';before=original.read_bytes()
try:
 run('combined-half273',C,'tools/rpg-2-star-ocean-the-second_combat-half-scale_check_v01_20261020-154048-7d4bddce.gd',marker='COMBAT_HALF_SCALE PASS checks=273 failures=0')
 lp(out/('rpg-2-star-ocean-the-second_half-scale_actual-report_v01_'+tag+'.json')).write_bytes(original.read_bytes())
finally:original.write_bytes(before)
sha=lambda p:hashlib.sha256(lp(p).read_bytes()).hexdigest()
report={'result':'PASS','base':'11973af6492ef60a99ca1f2eacb01e12c091ccb9','sourceHashes':{str(p.relative_to(C)):sha(p) for p in [C/'game/scripts/battle_arena.gd',C/'game/scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd']},'runs':results,'artApproved':False,'defaultAdoption':False,'completedAt':datetime.now(timezone.utc).isoformat()}
f=out/('rpg-2-star-ocean-the-second_heroine-contact_combined-proof_v01_'+tag+'.json');lp(f).write_text(json.dumps(report,indent=2)+'\n');print('ROOT_COMBINED_CONTACT_PASS',f,flush=True)
