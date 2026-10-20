"""Bounded exact-package profile acceptance and restored byte-tamper refusals. Serial after recording."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,uuid,os
C=Path(__file__).resolve().parents[1];P=C.parents[1]
s=importlib.util.spec_from_file_location('checked',C/'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py');checked=importlib.util.module_from_spec(s);s.loader.exec_module(checked)
def run():
 tag=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8];out=C/'outputs/hsea-root09';runs=[]
 for key,sub in [('APPDATA','a'),('LOCALAPPDATA','l')]:os.environ[key]=str(P/'work/dual09/profiles/root-city'/sub)
 def check(label,reg,mode):
  log=out/f'rpg-2-star-ocean-the-second_heroine-sea_profile-{label}_root-check-v01_{tag}.log'
  cmd=[str(P/'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'),'--headless','--path',str(C/'game'),'--script',str(C/'tools/rpg-2-star-ocean-the-second_heroine-sea_distance-driver_root-fallback-v01_20261020-215430-e2459a30.gd'),'--','res://'+reg.relative_to(C/'game').as_posix(),mode]
  r=checked.run_checked(cmd,25,expected=['SEA_FALLBACK_ROOT_PASS'],log_path=log);runs.append({'case':label,'passed':r['passed'],'reason':r['reason'],'log':log.relative_to(C).as_posix()});print(label,r['passed'],r['log'][-160:],flush=True);assert r['passed']
 for folder in ['hsea-gait11','hsea-arms12']:check(folder+'-accept',next((C/'game/data'/folder).glob('*registry*.json')),'accept')
 folder=C/'game/data/hsea-arms12';reg=next(folder.glob('*registry*.json'))
 for label,f in [('bridge-byte',next(folder.glob('*transition-manifest*.json'))),('png-byte',next((folder/'png').glob('*.png')))]:
  raw=f.read_bytes()
  try:f.write_bytes(raw+b'\x00');check(label,reg,'refuse')
  finally:f.write_bytes(raw);assert hashlib.sha256(f.read_bytes()).digest()==hashlib.sha256(raw).digest()
 check('uninspected-v04-refuses',next((C/'game/data/hsea-gait09').glob('*registry*.json')),'refuse')
 report={'result':'PASS','cases':runs,'allMutationsRestored':True,'scope':'Two exact coordinator-pinned packages; wrong revision and altered asset refuse before target mutation. No default adoption or art approval.'}
 p=out/f'rpg-2-star-ocean-the-second_heroine-sea_two-profile-root-proof_v01_{tag}.json';p.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(p)
if __name__=='__main__':run()
