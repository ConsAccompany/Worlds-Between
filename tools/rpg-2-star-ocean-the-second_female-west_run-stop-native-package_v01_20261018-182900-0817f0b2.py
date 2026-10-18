"""Package source-authored west gait cells and independently reopen both animated PXOs."""
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
import json,hashlib,io,zipfile,os,subprocess,re,sys,tempfile
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];SLUG='rpg-2-star-ocean-the-second';STAMP='20261018-182900';ID='0817f0b2'
OUT=ROOT/'outputs/female-west-run-stop-v01'
CORE='tools/rpg-2-star-ocean-the-second_female-west_run-stop-source_unapproved-v01_20261018-181150-a94f021c.gd'
WRITER='tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py'
NORTH='tools/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-build-and-check_unapproved-v01_20261018-090713-9af15df7.py'
WEST='outputs/female-west-static-v01/rpg-2-star-ocean-the-second_protagonist-female_west-layered-source_unapproved-v01_20261018-174421-618816ac.pxo'
SOUTH='outputs/female-idle-four-v01/rpg-2-star-ocean-the-second_female-south_idle-phase-00_unapproved-v01_20261018-175418-34294d7d.png'
def long(p):
 s=str(Path(p).resolve());prefix=chr(92)*2+'?'+chr(92)
 return prefix+s if os.name=='nt' and not s.startswith(prefix) else s
def read(p):return Path(long(p)).read_bytes()
def sha(b):return hashlib.sha256(b).hexdigest()
def rgba(b):return np.array(Image.open(io.BytesIO(b)).convert('RGBA'))
def mod(p,n):
 s=spec_from_file_location(n,ROOT/p);m=module_from_spec(s);s.loader.exec_module(m);return m
def main():
 folder=Path(sys.argv[1]);bake=json.loads(read(folder/f'{SLUG}_female-west-run_native-bake-report_v01_20261018-181150-a94f021c.json'))
 assert bake['modelSha256']==sha(read(ROOT/CORE))
 OUT.mkdir(parents=True,exist_ok=True)
 old_manifest_path=OUT/f'{SLUG}_female-west-run-stop_native-source-manifest_unapproved-v01_{STAMP}-{ID}.json'
 old_report_path=OUT/f'{SLUG}_female-west-run-stop_native-report_v01_{STAMP}-{ID}.json'
 cached_manifest=json.loads(read(old_manifest_path)) if '--reuse-native-exact' in sys.argv and Path(long(old_manifest_path)).exists() else None
 cached_report=json.loads(read(old_report_path)) if cached_manifest else None
 writer=mod(WRITER,'west_run_pxo_writer');native=mod(NORTH,'west_run_guides')
 writer.W,writer.H=80,112;writer.to_rgba=lambda a:np.ascontiguousarray(a,np.uint8)
 west=zipfile.ZipFile(io.BytesIO(read(ROOT/WEST)));roles=[x['name'] for x in json.loads(west.read('data.json'))['layers'] if x['name']!='guides'];roles+=['guides']
 palette={tuple(x) for x in rgba(read(ROOT/SOUTH)).reshape(-1,4) if x[3]}
 manifest={'task':'content.char.protagonist-female.walk-west','artApproved':False,'motionApproved':False,'runtimeIntegrated':False,'cell':[80,112],'pivot':[40,104],'scale':.5,'cadenceStepsPerSecond':4.375,'strideSourcePixels':128,'contactSourcePixels':38,'flightSeconds':26/280,'approvedPaletteProvenance':{'originalPath':'game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png','originalSourceAnchor':'ff8acd8caa7406b8300ba53891dd75a275ac1303','originalCanonicalVerifiedAt':'098fcd1e3183f7163e61af305947195a677dd289','portabilityFinding':'Original tracked canonical input full path263 characters; ordinary Python FileNotFoundError, extended-length read exact. Short committed idle-rest path avoids MAX_PATH.','portableCanonicalAnchor':'7ef4f39','portablePath':SOUTH,'exactPngSha256':'ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd','scope':'Approved SOUTH v8 static bytes; idle rest0 is byte-identical. No idle/motion approval inferred.'},'sourceHashEncoding':'UTF-8 code hashes normalize CRLF to LF; binary assets exact bytes','sources':{p:sha(read(ROOT/p).replace(b'\r\n',b'\n') if p.endswith(('.py','.gd')) else read(ROOT/p)) for p in [CORE,WRITER,NORTH,WEST,SOUTH]},'layers':roles,'sets':{},'scope':'One west run. East reversal uses existing produced EAST STATIC placeholder; no east locomotion is claimed. Live test presenter rasterizes source phases from the same controller; native128-phase run and representative25ms settle sequence are editable primary sources.'}
 gates={}
 jobs=[]
 for kind in ['run','stop']:
  rows=[r for r in bake['poses'] if r['kind']==kind];frames=[];records=[]
  for row in rows:
   image=rgba(read(folder/row['full']['file']));parts={}
   for role in roles[:-1]:
    raw=read(folder/row['roles'][role]['file']);assert sha(raw)==row['roles'][role]['sha256'];parts[role]=np.frombuffer(raw,np.uint8).reshape(112,80,4).copy()
   full=Image.new('RGBA',(80,112))
   for role in roles[:-1]:full.alpha_composite(Image.fromarray(parts[role]))
   assert np.array_equal(np.array(full),image)
   assert set(np.unique(image[:,:,3]))<={0,255}
   assert {tuple(x) for x in image.reshape(-1,4) if x[3]}<=palette
   assert not np.any(image[[0,-1],:,3]) and not np.any(image[:,[0,-1],3])
   parts['guides']=native.v8t.guides_rgba(image);frames.append(parts)
   data=read(folder/row['full']['file']);target=OUT/row['full']['file'];Path(long(target)).write_bytes(data)
   records.append({'alphaBoundsExclusive':list(Image.fromarray(image).getbbox()),'index':row['index'],'state':row['state'],'file':target.relative_to(ROOT).as_posix(),'sha256':sha(data),'rolesSha256':{r:sha(parts[r].tobytes()) for r in roles}})
  fps=70. if kind=='run' else 40.;durations=[.25 if kind=='run' else 1.]*len(frames)
  export_name=f'{SLUG}_female-west-{kind}_native-export_v01_{STAMP}-{ID}'
  raw=writer.make_pxo(frames,durations,read(folder/rows[0]['full']['file']),export_name,fps,order=roles,dt=(2026,10,18,18,29,0))
  z0=zipfile.ZipFile(io.BytesIO(raw));out=io.BytesIO()
  with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
   for info in z0.infolist():
    data=z0.read(info.filename)
    if info.filename=='data.json':
     d=json.loads(data);d['layers'][-1]['visible']=False;d['layers'][-1]['locked']=True;d['tags']=[{'name':'west-'+kind,'from':1,'to':len(frames),'color':'1a9999'}];d['user_data']='Unapproved source-authored west gait/settle, binary alpha,80x112,pivot40/104,scale0.5. No runtime adoption.';data=json.dumps(d,separators=(',',':')).encode()
    z.writestr(info,data)
  path=OUT/f'{SLUG}_female-west-{kind}_animated-source_unapproved-v01_{STAMP}-{ID}.pxo';Path(long(path)).write_bytes(out.getvalue())
  manifest['sets'][kind]={'pxo':{'file':path.relative_to(ROOT).as_posix(),'sha256':sha(out.getvalue())},'fps':fps,'durations':durations,'frames':records,'seconds':sum(durations)/fps}
  # Reuse an independent export only for an identical rebuilt PXO byte stream.
  if cached_manifest and cached_report and cached_manifest['sets'][kind]['pxo']['sha256']==sha(out.getvalue()):
   previous=next(x for x in cached_report['native'] if x['kind']==kind)
   assert previous['exit']==0 and previous['exact']==previous['cells'] and not previous['unexpectedDiagnostics']
   previous['reusedExactArtifact']=True;jobs.append(previous);gates[kind+'_native_exact']=True
   continue
  # Independent Pixelorama process, never the user's open editor or save state.
  temp=Path(tempfile.mkdtemp(prefix='wb-west-'+kind+'-native-'));(temp/'exports').mkdir();env=dict(os.environ);env['APPDATA']=str(temp/'app');env['LOCALAPPDATA']=str(temp/'local')
  inp=temp/path.name;inp.write_bytes(out.getvalue());exe=(ROOT/'../../work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe').resolve()
  proc=subprocess.run([str(exe),'--headless','--quit','--','--export','--split-layers','-o',str(temp/'exports'/f'{export_name}.png'),str(inp)],env=env,capture_output=True,text=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
  files=list((temp/'exports').glob('*.png'));matches={}
  for i,parts in enumerate(frames):
   for role in roles[:-1]:
    hits=[p for p in files if '('+role+')' in p.name and p.name.endswith(f'_{i+1:04d}.png')]
    matches[role+'/'+str(i)]=len(hits)==1 and np.array_equal(rgba(read(hits[0])),parts[role])
  errors=re.sub(r'ERROR: Condition "!actions.custom_samplers.has\(function->arguments\[j\].tex_builtin\)" is true\. Continuing\.\s+at: _dump_node_code \(servers/rendering/shader_compiler.cpp:1329\)','',proc.stderr).strip()
  ok=proc.returncode==0 and not errors and all(matches.values()) and not any('(guides)' in p.name for p in files)
  gates[kind+'_native_exact']=ok
  jobs.append({'kind':kind,'exit':proc.returncode,'cells':len(matches),'exact':sum(matches.values()),'stdout':proc.stdout,'stderr':proc.stderr,'unexpectedDiagnostics':errors,'tempOnlyExports':str(temp)})
 gates['final_west_static_exact']=np.array_equal(rgba(read(ROOT/manifest['sets']['stop']['frames'][-1]['file'])),rgba(west.read('preview.png')))
 manifest['staticDisplayBaselineLogicalPixels']=48
 manifest['visibleExtentSourceHeightRange']=[min(r['alphaBoundsExclusive'][3]-r['alphaBoundsExclusive'][1] for e in manifest['sets'].values() for r in e['frames']),max(r['alphaBoundsExclusive'][3]-r['alphaBoundsExclusive'][1] for e in manifest['sets'].values() for r in e['frames'])]
 manifest_path=OUT/f'{SLUG}_female-west-run-stop_native-source-manifest_unapproved-v01_{STAMP}-{ID}.json';Path(long(manifest_path)).write_text(json.dumps(manifest,indent=2)+'\n',newline='\n')
 report={'passed':sum(gates.values()),'total':len(gates),'gates':gates,'native':jobs,'manifestSha256':sha(read(manifest_path)),'artApproved':False,'motionApproved':False,'nativeGuiSaveAsVerified':False,'knownBackendDiagnostics':'Four inherited headless shader-compiler diagnostics retained verbatim per process. No source/parser/ancestry errors permitted.'}
 path=OUT/f'{SLUG}_female-west-run-stop_native-report_v01_{STAMP}-{ID}.json';Path(long(path)).write_text(json.dumps(report,indent=2)+'\n',newline='\n');print(path);print(gates)
 if not all(gates.values()):raise SystemExit(1)
if __name__=='__main__':main()
