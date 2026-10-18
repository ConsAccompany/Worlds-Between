"""Source, frame-cell and independent native editable export evidence for four idle loops."""
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
from concurrent.futures import ThreadPoolExecutor
import io,json,os,re,subprocess,tempfile,zipfile
import xml.etree.ElementTree as ET
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
AUTHOR=ROOT/'tools/rpg-2-star-ocean-the-second_female-idle-four-direction_native-build_unapproved-v01_20261018-175418-34294d7d.py'
spec=spec_from_file_location('idle_author',AUTHOR);a=module_from_spec(spec);spec.loader.exec_module(a)
MANIFEST=a.OUT/f'{a.SLUG}_female-idle-four_direction-manifest_unapproved-v01_{a.STAMP}-{a.ID}.json'
def main():
 m=json.loads(a.read(MANIFEST));g={};details=[];temp=Path(tempfile.mkdtemp(prefix='wb-idle-native-'))
 g['author_helpers_exact']=m['sourceSha256TextLf']==a.sha(a.read(AUTHOR),True) and all(a.sha(a.read(ROOT/p),True)==h for p,h in m['helpers'].items())
 g['cycle_timing']=abs(sum(p['seconds'] for p in m['phases'])-4.8)<1e-9 and len(m['phases'])==12
 native=a.module(a.NORTH,'idle_native_ora_check');native.LAYERS=a.ROLES
 palette={tuple(c) for c in a.rgba(a.read(ROOT/a.SOURCES['south'])).reshape(-1,4) if c[3]}
 jobs=[]
 for direction,row in m['directions'].items():
  source=a.rgba(a.read(ROOT/row['file']));frames=a.poses(source,direction)
  g[direction+'_static_sha']=a.sha(a.read(ROOT/row['file']))==row['sha256']
  def holes(image):
   o=image[:,:,3]>0;return (~o[1:-1,1:-1])&o[:-2,1:-1]&o[2:,1:-1]&o[1:-1,:-2]&o[1:-1,2:]
  g[direction+'_no_new_enclosed_pinholes']=all(not np.any(holes(a.flat(p))&~holes(source)) for p in frames)
  g[direction+'_fixed_lower_body']=all(np.array_equal(a.flat(p)[78:],source[78:]) for p in frames)
  g[direction+'_first_and_rest_exact']=all(np.array_equal(a.flat(frames[i]),source) for i in [0,9,10,11])
  g[direction+'_subtle_local_motion']=all(np.array_equal(p['fixed-body'],frames[0]['fixed-body']) for p in frames) and all(0<row['frames'][i]['changedTexels']<160 for i in [2,3,4,7])
  pxo=zipfile.ZipFile(io.BytesIO(a.read(ROOT/row['pxo']['file'])));d=json.loads(pxo.read('data.json'))
  g[direction+'_animated_native_metadata']=d['pxo_version']==7 and d['fps']==1. and [f['duration'] for f in d['frames']]==[p[1] for p in a.PHASES] and [l['name'] for l in d['layers']]==a.ROLES and not d['layers'][-1]['visible'] and d['layers'][-1]['locked']
  exact=True
  for i,(p,fr) in enumerate(zip(frames,row['frames'])):
   image=a.flat(p);p['guides']=native.v8t.guides_rgba(image)
   assert set(np.unique(image[:,:,3]))<={0,255}
   assert {tuple(c) for c in image.reshape(-1,4) if c[3]}<=palette
   for f in fr['files'].values():assert a.sha(a.read(ROOT/f['file']))==f['sha256']
   assert np.array_equal(a.rgba(a.read(ROOT/fr['files']['png']['file'])),image)
   ora=zipfile.ZipFile(io.BytesIO(a.read(ROOT/fr['files']['ora']['file'])));entries=list(reversed(ET.fromstring(ora.read('stack.xml')).find('stack').findall('layer')))
   exact &= [x.get('name') for x in entries]==a.ROLES and entries[-1].get('visibility')=='hidden'
   for j,role in enumerate(a.ROLES):
    exact &= pxo.read(f'image_data/frames/{i+1}/layer_{j+1}')==p[role].tobytes()
    exact &= np.array_equal(a.rgba(ora.read(entries[j].get('src'))),p[role])
   if i in [0,4,7]:jobs.append((direction,'ora',i,fr['files']['ora']['file'],[p]))
  g[direction+'_all12_png_ora_and_pxo_cells_exact']=bool(exact) and a.sha(a.read(ROOT/row['pxo']['file']))==row['pxo']['sha256']
  jobs.append((direction,'pxo',-1,row['pxo']['file'],frames))
 def export(job):
  direction,ext,phase,file,frames=job;folder=temp/f'{direction}-{ext}-{phase}';folder.mkdir();(folder/'exports').mkdir()
  for key in ['app','local']:(folder/key).mkdir()
  env=dict(os.environ);env['APPDATA']=str(folder/'app');env['LOCALAPPDATA']=str(folder/'local')
  source=folder/f'{a.SLUG}_female-{direction}_native-input-phase-{phase}_v01_{a.STAMP}-{a.ID}.{ext}';source.write_bytes(a.read(ROOT/file))
  output=folder/'exports'/f'{a.SLUG}_female-{direction}_native-export_v01_{a.STAMP}-{a.ID}.png'
  exe=ROOT/'../../work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe'
  run=subprocess.run([str(exe.resolve()),'--headless','--quit','--','--export','--split-layers','-o',str(output),str(source)],env=env,capture_output=True,text=True,timeout=90,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
  files=list((folder/'exports').glob('*.png'));matches={}
  for role in a.ROLES[:-1]:
   for i,p in enumerate(frames):
    suffix=f'_{i+1:04d}.png' if ext=='pxo' else '.png'
    hits=[x for x in files if '('+role+')' in x.name and (x.name.endswith(suffix) if ext=='pxo' else True)]
    matches[role+'/'+str(i)]=len(hits)==1 and np.array_equal(a.rgba(a.read(hits[0])),p[role])
  # Four shader-compiler diagnostics are a known Pixelorama headless backend issue, disclosed verbatim.
  errors=re.sub(r'ERROR: Condition "!actions.custom_samplers.has\(function->arguments\[j\].tex_builtin\)" is true\. Continuing\.\s+at: _dump_node_code \(servers/rendering/shader_compiler.cpp:1329\)','',run.stderr).strip()
  ok=run.returncode==0 and not errors and all(matches.values()) and not any('(guides)' in x.name for x in files)
  return f'{direction}_{ext}_{phase}_native_exact',ok,{'direction':direction,'format':ext,'phase':phase,'exit':run.returncode,'cells':len(matches),'allCellsExact':all(matches.values()),'stdout':run.stdout,'stderr':run.stderr,'unexpectedDiagnostics':errors}
 with ThreadPoolExecutor(max_workers=2) as pool:
  for key,ok,detail in pool.map(export,jobs):g[key]=ok;details.append(detail)
 report={'task':m['task'],'passed':sum(bool(v) for v in g.values()),'total':len(g),'gates':{k:bool(v) for k,v in g.items()},'nativeTemp':str(temp),'native':details,'nativeCoverage':'All4 PXOs /12frames /7visible role layers, plus12 separate critical phase ORAs (rest0,crest4,lag7). All48 ORA cell archives checked against source.','manifestSha256':a.sha(a.read(MANIFEST)),'artApproved':False,'motionApproved':False}
 from datetime import datetime
 import uuid
 path=a.OUT/f'{a.SLUG}_female-idle-four_native-report_v01_{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}.json';path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
 print('NATIVE IDLE',report['passed'],'/',report['total']);print(path)
 for key,ok in g.items():
  if not ok:print('FAIL',key)
 if not all(g.values()):raise SystemExit(1)
if __name__=='__main__':main()
