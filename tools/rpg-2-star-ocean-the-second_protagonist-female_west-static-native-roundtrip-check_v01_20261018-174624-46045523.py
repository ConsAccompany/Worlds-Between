"""Check authored west source, approved palette, editable role layers and independent native exports."""
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
import hashlib,io,json,os,subprocess,tempfile,zipfile,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
AUTHOR=ROOT/'tools/rpg-2-star-ocean-the-second_protagonist-female_west-static-native-build-check_unapproved-v01_20261018-174421-618816ac.py'
def long(p):
 s=str(Path(p).resolve());pre=chr(92)*2+'?'+chr(92)
 return pre+s if os.name=='nt' and not s.startswith(pre) else s
def read(p):return Path(long(p)).read_bytes()
def sha(b,text=False):return hashlib.sha256(b.replace(bytes([13,10]),bytes([10])) if text else b).hexdigest()
def rgba(b):return np.array(Image.open(io.BytesIO(b)).convert('RGBA'))
def main():
 spec=spec_from_file_location('female_west_author_check',AUTHOR);a=module_from_spec(spec);spec.loader.exec_module(a)
 manifest=json.loads(read(next(a.OUT.glob('*manifest*.json'))));images=a.paint();flat=Image.new('RGBA',(80,112))
 for layer in images.values():flat.alpha_composite(layer)
 expect={k:np.array(v) for k,v in images.items()};expect['guides']=a.base.v8t.guides_rgba(np.array(flat))
 gates={}
 gates['current_source_hash']=sha(read(AUTHOR),True)==manifest['sourceSha256TextLf']
 gates['container_writer_hash']=sha(read(a.NORTH_TOOL),True)==manifest['containerWriterSha256TextLf']
 gates['approved_v8_unchanged']=sha(read(a.V8))=='ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd'
 gates['artifact_hashes']=all(sha(read(ROOT/v['file']))==v['sha256'] for v in manifest['files'].values())
 gates['source_rebuild_exact']=np.array_equal(rgba(read(ROOT/manifest['files']['png']['file'])),np.array(flat))
 arr=np.array(flat);op=arr[:,:,3]>0;v8=rgba(read(a.V8));ys,xs=np.nonzero(op)
 gates['native_body_pin_alpha']=arr.shape==(112,80,4) and set(np.unique(arr[:,:,3]))<={0,255} and (ys.min(),ys.max())==(8,103) and (xs.min(),xs.max())==(24,58) and xs[ys>=97].min()<=40<=xs[ys>=97].max()
 gates['approved_palette_subset']={tuple(p) for p in arr[op]}<={tuple(p) for p in v8[v8[:,:,3]>0]}
 archive=zipfile.ZipFile(io.BytesIO(read(ROOT/manifest['files']['pxo']['file'])));data=json.loads(archive.read('data.json'))
 gates['pxo_role_layers_exact']=data['pxo_version']==7 and [x['name'] for x in data['layers']]==list(expect) and all(archive.read(f'image_data/frames/1/layer_{i}')==expect[k].tobytes() for i,k in enumerate(expect,1))
 gates['pxo_guides_hidden_locked']=not data['layers'][-1]['visible'] and data['layers'][-1]['locked']
 ora=zipfile.ZipFile(io.BytesIO(read(ROOT/manifest['files']['ora']['file'])));entries=list(reversed(ET.fromstring(ora.read('stack.xml')).find('stack').findall('layer')))
 gates['ora_roles_exact']=[x.get('name') for x in entries]==list(expect) and all(np.array_equal(rgba(ora.read(x.get('src'))),expect[x.get('name')]) for x in entries)
 gates['ora_guide_hidden']=entries[-1].get('visibility')=='hidden'
 temp=Path(tempfile.mkdtemp(prefix='wb-female-west-native-'));details={}
 exe=ROOT/'../../work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe'
 for ext in ['pxo','ora']:
  folder=temp/ext;folder.mkdir();source=folder/f'rpg-2-star-ocean-the-second_female-west_native-source_{a.STAMP}-{a.IDENT}.{ext}';source.write_bytes(read(ROOT/manifest['files'][ext]['file']))
  env=dict(os.environ);env['APPDATA']=str(folder/'app');env['LOCALAPPDATA']=str(folder/'local');Path(env['APPDATA']).mkdir();Path(env['LOCALAPPDATA']).mkdir()
  exports=folder/'exports';exports.mkdir();name=f'rpg-2-star-ocean-the-second_female-west_native-export_{a.STAMP}-{a.IDENT}.png'
  run=subprocess.run([str(exe.resolve()),'--headless','--quit','--','--export','--split-layers','-o',str(exports/name),str(source)],env=env,capture_output=True,text=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
  files=list(exports.glob('*.png'));checks={}
  for layer in a.LAYERS:
   hits=[p for p in files if '('+layer+')' in p.name];checks[layer]=len(hits)==1 and np.array_equal(rgba(read(hits[0])),expect[layer])
  gates[ext+'_native_roles_exact']=run.returncode==0 and all(checks.values()) and not any('(guides)' in p.name for p in files)
  details[ext]={'exit':run.returncode,'roles':checks,'stdout':run.stdout,'stderr':run.stderr}
 gates={key:bool(value) for key,value in gates.items()}
 report={'gates':gates,'passed':sum(gates.values()),'total':len(gates),'native':details,'nativeTemp':str(temp),'artApproved':False,'sourceSha256TextLf':sha(read(AUTHOR),True)}
 from datetime import datetime
 import uuid
 path=a.OUT/f'rpg-2-star-ocean-the-second_protagonist-female_west-static-native-report_v01_{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}.json';Path(long(path)).write_text(json.dumps(report,indent=2)+chr(10),encoding='utf-8',newline=chr(10))
 for key,ok in gates.items():print(('PASS ' if ok else 'FAIL ')+key)
 print('REPORT',path)
 if not all(gates.values()):raise SystemExit(1)
if __name__=='__main__':main()
