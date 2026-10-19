import hashlib, io, json, shutil, subprocess, sys, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'game/assets/ui/battle-skin-v01'
TAG = '20261019-174000-89f5e61d'
OUT = ROOT / 'outputs/battle-ui-skin-v01'
FIXTURE = ROOT / 'work' / ('hudn-'+TAG[-8:])
rows = []
def ck(key, value):
    rows.append({'key': key, 'pass': bool(value)})
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
manifest_path = next(PACKAGE.glob('*manifest*.json'))
m = json.loads(manifest_path.read_text(encoding='utf-8'))
ck('eleven-skins', len(m['skins']) == 11)
ck('34-authored-files', len([p for p in PACKAGE.iterdir() if p.suffix in ('.png','.pxo','.ora','.json')]) == 34)
for label in ('source', 'helper'):
    path = (PACKAGE / m[label]['path']).resolve()
    ck(label+'-raw-sha', sha(path) == m[label]['sha256'])
for key, e in m['skins'].items():
    image = Image.open(PACKAGE/e['png']).convert('RGBA')
    ck(key+'-size', list(image.size) == e['size'])
    ck(key+'-binary-alpha', set(image.getchannel('A').getdata()) <= {0,255})
    ck(key+'-color-count', len({p for p in image.getdata() if p[3]}) == e['opaqueColorCount'])
    for name, digest in e['sha256'].items(): ck(key+'-raw-sha-'+Path(name).suffix, sha(PACKAGE/name) == digest)
    s=e['slices']; w,h=image.size
    ck(key+'-ninepatch-center-positive',s['left']+s['right']<w and s['top']+s['bottom']<h)
    ck(key+'-stretch-horizontal',all(len({image.getpixel((x,y)) for x in range(s['left'],w-s['right'])}) == 1 for y in range(h)))
    ck(key+'-stretch-vertical',all(len({image.getpixel((x,y)) for y in range(s['top'],h-s['bottom'])}) == 1 for x in range(w)))
    pxlayers=[]
    with zipfile.ZipFile(PACKAGE/e['pxo']) as z:
        data=json.loads(z.read('data.json'))
        ck(key+'-pxo-native-header',data['pxo_version']==7 and data['pixelorama_version']=='v1.2.3-stable' and [data['size_x'],data['size_y']]==e['size'])
        ck(key+'-pxo-one-frame',len(data['frames'])==1 and data['frames'][0]['duration']==1.0)
        ck(key+'-pxo-editable-role-layers',[p['name'] for p in data['layers']]==e['layerRoles'] and all(p['type']==0 and p['visible'] and not p['locked'] and p['opacity']==1.0 for p in data['layers']))
        merged=Image.new('RGBA',image.size)
        for i,name in enumerate(e['layerRoles'],1):
            raw=z.read(f'image_data/frames/1/layer_{i}')
            ck(key+'-pxo-layer-bytes-'+name,len(raw)==w*h*4)
            layer=Image.frombytes('RGBA',image.size,raw); pxlayers.append(layer); merged.alpha_composite(layer)
        ck(key+'-pxo-composite-equals-png',merged.tobytes()==image.tobytes())
        ck(key+'-pxo-preview-equals-png',Image.open(io.BytesIO(z.read('preview.png'))).convert('RGBA').tobytes()==image.tobytes())
    with zipfile.ZipFile(PACKAGE/e['ora']) as z:
        stack=ET.fromstring(z.read('stack.xml'))
        layers=list(stack.find('stack'))
        ck(key+'-ora-layer-names',[p.attrib['name'] for p in reversed(layers)]==e['layerRoles'])
        merged=Image.new('RGBA',image.size)
        for i, item in enumerate(reversed(layers)):
            layer=Image.open(io.BytesIO(z.read(item.attrib['src']))).convert('RGBA')
            ck(key+'-ora-pxo-role-equality-'+item.attrib['name'],layer.tobytes()==pxlayers[i].tobytes())
            ck(key+'-ora-role-visible-origin-'+item.attrib['name'],item.attrib['opacity']=='1.0' and item.attrib['visibility']=='visible' and item.attrib['x']=='0' and item.attrib['y']=='0')
            merged.alpha_composite(layer)
        ck(key+'-ora-composite-equals-png',merged.tobytes()==image.tobytes())
        ck(key+'-ora-merged-equals-png',Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA').tobytes()==image.tobytes())
build_package=FIXTURE
# Author's CLI uses non-extended pathlib writes and exceeds MAX_PATH in a deep
# mirrored checkout. Preserve that failed first-attempt report; invoke the exact
# author's render function in a fresh process with the original package path for
# manifest-relative provenance, writing its unmodified bytes into a short ignored peer.
build_author=(PACKAGE/m['source']['path']).resolve()
build_code="""import importlib.util, pathlib, sys
spec=importlib.util.spec_from_file_location('hud_author',sys.argv[1]);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
files=mod.render(pathlib.Path(sys.argv[2]));failures=mod.self_check(files)
assert not failures, failures
out=pathlib.Path(sys.argv[3]);out.mkdir(parents=True,exist_ok=True)
for name,raw in files.items(): (out/name).write_bytes(raw)
print('REBUILD',len(files),'PASS')
"""
result=subprocess.run([sys.executable,'-c',build_code,str(build_author),str(PACKAGE),str(build_package)],capture_output=True,text=True,encoding='utf-8',timeout=30)
ck('deterministic-build-exit',result.returncode==0)
for p in PACKAGE.iterdir():
    if p.suffix in ('.png','.pxo','.ora','.json'):
        ck('rebuild-exact-'+p.name,(build_package/p.name).is_file() and p.read_bytes()==(build_package/p.name).read_bytes())
OUT.mkdir(parents=True,exist_ok=True)
report={'tag':TAG,'sourceRevision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'sourceAndHelperRawSha256':{role:sha((PACKAGE/m[role]['path']).resolve()) for role in ('source','helper')},'checks':rows,'count':len(rows),'failed':[r['key'] for r in rows if not r['pass']],'rebuildStdout':result.stdout,'rebuildStderr':result.stderr,'limitations':['Independent archive/pixel/rebuild checks only; no Pixelorama application or GUI save/reopen verification; no artistic acceptance.']}
(OUT/f'rpg-2-star-ocean-the-second_battle-ui_native-independent-report_v01_{TAG}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('HUD_NATIVE_INDEPENDENT',len(rows)-len(report['failed']),'/',len(rows),'PASS' if not report['failed'] else 'FAIL',report['failed'])
sys.exit(bool(report['failed']))
