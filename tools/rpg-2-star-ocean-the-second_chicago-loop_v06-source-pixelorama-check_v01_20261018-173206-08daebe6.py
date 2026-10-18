"""Focused v06 source/native-editor verification. No game, creator approval or runtime default changes."""
from pathlib import Path
from importlib.util import module_from_spec,spec_from_file_location
import hashlib,io,json,os,subprocess,tempfile,zipfile,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
AUTHOR=ROOT/'tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-author_unapproved-v06_20261018-155129-19790a70.py'
V05=ROOT/'outputs/chicago-loop-state-lake-v05/rpg-2-star-ocean-the-second_chicago-loop_state-lake_layer-manifest_unapproved-v05_20261017-234337-84862412.json'
NATIVE=ROOT/'../../work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe'
def native(path):
    path=str(Path(path).resolve())
    prefix=chr(92)*2+"?"+chr(92)
    return prefix+path if os.name=="nt" and not path.startswith(prefix) else path

def sha(data,text=False):return hashlib.sha256(data.replace(bytes([13,10]),bytes([10])) if text else data).hexdigest()
def read(path):return Path(native(path)).read_bytes()
def rgba(path_or_bytes):return np.array(Image.open(io.BytesIO(path_or_bytes) if isinstance(path_or_bytes,bytes) else native(path_or_bytes)).convert('RGBA'))
def load_author():
    spec=spec_from_file_location('chicago6_validation_author',AUTHOR);mod=module_from_spec(spec);spec.loader.exec_module(mod);return mod

def main():
    author=load_author();path=author.OUT/f'{author.PREFIX}_layer-manifest_{author.VARIANT}_{author.STAMP}.json'
    manifest=json.loads(read(path));base=json.loads(read(V05));layers,props=author.build_layers();guide=author.v5.walkmask();flat=author.v5.merged(layers)
    gates={};details={}
    gates['source_hash']=manifest['source_sha256_text_lf']==sha(read(AUTHOR),True)
    gates['file_hashes']=all(sha(read(ROOT/v['file']),v.get('hash_algorithm')=='sha256-text-lf-v1')==v['sha256'] for v in manifest['files'].values())
    gates['geometry_props_visibility_exact']=all(manifest[k]==base[k] for k in ['geometry','ysort_props','hero_visibility'])
    gates['walk_reveal_exact']=all(read(ROOT/manifest['files'][k]['file'])==read(ROOT/base['files'][k]['file']) for k in ['walkmask-guide','occlusion-reveal-mask'])
    gates['ysort_alpha_exact']=all(np.array_equal(rgba(ROOT/manifest['files'][k]['file'])[:,:,3],rgba(ROOT/base['files'][k]['file'])[:,:,3]) for k in author.YSORT)
    gates['runtime_export_exact']=all(np.array_equal(rgba(ROOT/manifest['files'][k]['file']),np.array(img)) for k,img in author.v5.runtime_layers(layers).items())
    gates['flat_exact']=np.array_equal(rgba(ROOT/manifest['files']['flat-source']['file']),np.array(flat))
    expect={**{k:np.array(v) for k,v in layers.items()},author.GUIDE:np.array(guide)}
    gates['native_size_binary_alpha']=all(v.shape==(360,640,4) and np.isin(v[:,:,3],[0,255]).all() for v in expect.values())
    pxo=zipfile.ZipFile(io.BytesIO(read(ROOT/manifest['files']['pixelorama']['file'])));data=json.loads(pxo.read('data.json'))
    gates['pxo_layers_exact']=data['pxo_version']==7 and [v['name'] for v in data['layers']]==list(expect) and all(pxo.read(f'image_data/frames/1/layer_{i}')==expect[k].tobytes() for i,k in enumerate(expect,1))
    gates['pxo_guide_hidden_locked']=not data['layers'][-1]['visible'] and data['layers'][-1]['locked']
    ora=zipfile.ZipFile(io.BytesIO(read(ROOT/manifest['files']['openraster']['file'])));entries=list(reversed(ET.fromstring(ora.read('stack.xml')).find('stack').findall('layer')))
    gates['ora_layers_exact']=[v.get('name') for v in entries]==list(expect) and all(np.array_equal(rgba(ora.read(v.get('src'))),expect[v.get('name')]) for v in entries)
    gates['ora_guide_hidden']=entries[-1].get('visibility')=='hidden'
    before=sha(read(ROOT/'game/scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v05_20261017-234337-84862412.gd'),True)
    tmp=Path(tempfile.mkdtemp(prefix='wb-chi6-native-'))
    # The editor opens independent file copies under fresh APPDATA/LOCALAPPDATA. It never accesses the user's open editor.
    for extension,key in [('pxo','pixelorama'),('ora','openraster')]:
        folder=tmp/extension;folder.mkdir();source=folder/Path(manifest['files'][key]['file']).name;source.write_bytes(read(ROOT/manifest['files'][key]['file']))
        out=folder/'exports';out.mkdir();env=dict(os.environ);env['APPDATA']=str(folder/'app');env['LOCALAPPDATA']=str(folder/'local');Path(env['APPDATA']).mkdir();Path(env['LOCALAPPDATA']).mkdir()
        prefix='rpg-2-star-ocean-the-second_chicago-v06_native-layer-export_20261018-155129-19790a70.png'
        proc=subprocess.run([str(NATIVE.resolve()),'--headless','--quit','--','--export','--split-layers','-o',str(out/prefix),str(source)],env=env,capture_output=True,text=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        exports=list(out.glob('*.png'));checks={}
        for layer in author.LAYERS:
            hits=[p for p in exports if '('+layer+')' in p.name];checks[layer]=len(hits)==1 and np.array_equal(rgba(hits[0]),expect[layer])
        details[extension]={'exit':proc.returncode,'layers':checks,'pngs':len(exports),'guide_hidden':not any('('+author.GUIDE+')' in p.name for p in exports),'source_unchanged':sha(read(source))==manifest['files'][key]['sha256'],'stdout':proc.stdout,'stderr':proc.stderr}
        gates[extension+'_native_reopen_export_exact']=proc.returncode==0 and all(checks.values()) and details[extension]['guide_hidden'] and details[extension]['source_unchanged']
    gates['scene_source_unchanged']=before==sha(read(ROOT/'game/scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v05_20261017-234337-84862412.gd'),True)
    # Retain native exports in the isolated temporary folder for inspection; never recursively delete computed targets.
    report={'gates':gates,'passed':sum(gates.values()),'total':len(gates),'native_exports':details,'native_temp':str(tmp),'layer_count':len(layers),'guide_layers':1,'author_sha256_text_lf':sha(read(AUTHOR),True),'native_executable_sha256':sha(read(NATIVE))}
    from datetime import datetime
    import uuid
    stamp=datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]
    output=author.OUT/f'rpg-2-star-ocean-the-second_chicago-loop_source-native-pixelorama-report_v06_{stamp}.json';output.write_text(json.dumps(report,indent=2)+'\n')
    for name,ok in gates.items():print(('PASS ' if ok else 'FAIL ')+name)
    print('REPORT',output)
    if not all(gates.values()):raise SystemExit(1)
if __name__=='__main__':main()
