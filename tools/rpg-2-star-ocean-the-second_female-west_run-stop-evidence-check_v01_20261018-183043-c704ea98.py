"""Portable integrity/native/source check for the one-direction west run pilot."""
from pathlib import Path
import gzip,hashlib,io,json,os,subprocess,zipfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
MANIFEST='outputs/female-west-run-stop-v01/rpg-2-star-ocean-the-second_female-west-run-stop_evidence-manifest_v01_20261018-183043-c704ea98.json'
def long(p):
 s=str(Path(p).resolve());prefix=chr(92)*2+'?'+chr(92)
 return prefix+s if os.name=='nt' and not s.startswith(prefix) else s
def read(p):return Path(long(p)).read_bytes()
def sha(b):return hashlib.sha256(b).hexdigest()
def textsha(b):return sha(b.replace(b'\r\n',b'\n'))
def main():
 m=json.loads(read(ROOT/MANIFEST));checks={}
 for p,row in m['files'].items():checks['file:'+p]=(textsha(read(ROOT/p)) if row['textLf'] else sha(read(ROOT/p)))==row['sha256']
 n=json.loads(read(ROOT/m['nativeManifest']))
 for p,h in n['sources'].items():checks['source:'+p]=(textsha(read(ROOT/p)) if p.endswith(('.py','.gd')) else sha(read(ROOT/p)))==h
 native=json.loads(read(ROOT/m['nativeReport']));checks['native_manifest_bound']=native['manifestSha256']==sha(read(ROOT/m['nativeManifest']))
 checks['native_all_cells_exact']=all(x['exit']==0 and x['exact']==x['cells'] and not x['unexpectedDiagnostics'] for x in native['native']) and native['gates']['final_west_static_exact']
 rgba_hashes={}
 for kind,entry in n['sets'].items():
  z=zipfile.ZipFile(io.BytesIO(read(ROOT/entry['pxo']['file'])));d=json.loads(z.read('data.json'))
  checks[kind+':metadata']=len(d['frames'])==len(entry['frames']) and d['fps']==entry['fps'] and [x['duration'] for x in d['frames']]==entry['durations'] and [x['name'] for x in d['layers']]==n['layers'] and not d['layers'][-1]['visible'] and d['layers'][-1]['locked']
  for i,row in enumerate(entry['frames']):
   full=Image.new('RGBA',(80,112))
   for j,role in enumerate(n['layers']):
    data=z.read(f'image_data/frames/{i+1}/layer_{j+1}');checks[f'{kind}:{i}:{role}']=sha(data)==row['rolesSha256'][role]
    if role!='guides':full.alpha_composite(Image.frombytes('RGBA',(80,112),data))
   expected=Image.open(io.BytesIO(read(ROOT/row['file']))).convert('RGBA')
   checks[f'{kind}:{i}:flat']=full.tobytes()==expected.tobytes()
   if kind=='run':rgba_hashes[i]=sha(full.tobytes())
 core=n['sources'][m['core']]
 for row in m['transitionReports']:
  raw=gzip.decompress(read(ROOT/row['file']));r=json.loads(raw);checks['report:'+row['role']]=sha(raw)==row['uncompressedSha256'] and r['failed']==row['failed']
  if row['role']=='final-exact-boundary':checks['final_transition_closed']=r['failed']==0 and r['passed']==25260 and r['modelSha256']==core
 for row in m['captures']:
  r=json.loads(read(ROOT/row['report']));checks[row['scene']+':capture_checks']=r['failed']==0 and r['modelSha256']==core
  steady=[f for f in r['frames'] if f['state']['mode']=='run' and f['state']['age']>=.12]
  checks[row['scene']+':actual_native_cells']=all(f['sourceRgbaSha256']==rgba_hashes[int(f['state']['q'])] for f in steady) and len(steady)==row['steadyRgbaMatches']
  checks[row['scene']+':declared_duration']=abs(len(r['frames'])/r['fps']-row['simulationSeconds'])<1e-9
  for c in row['critical']:
   original=next(f for f in r['frames'] if f['tick']==c['tick']);checks[c['file']+':actual_frame']=sha(read(ROOT/c['file']))==original['sha256']
 for p,h in m['protectedGameSources'].items():
  baseline=subprocess.check_output(['git','show',m['protectedAnchor']+':'+p],cwd=ROOT);checks['unchanged:'+p]=textsha(read(ROOT/p))==h==textsha(baseline)
 print('WEST RUN EVIDENCE',sum(checks.values()),'/',len(checks))
 for k,v in checks.items():
  if not v:print('FAIL',k)
 if not all(checks.values()):raise SystemExit(1)
 return checks
if __name__=='__main__':main()
