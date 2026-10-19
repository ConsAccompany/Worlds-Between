"""Independent exact-crop/provenance check; two finite local rebuilds, no game/provider writes."""
from pathlib import Path
from PIL import Image
import numpy as np
import hashlib, io, json, zipfile, xml.etree.ElementTree as ET
import importlib.util, types, uuid
ROOT=Path(__file__).resolve().parents[1]
TAG='20261019-182839-4d72f1c6'
SLUG='rpg-2-star-ocean-the-second'
OUT=ROOT/'outputs/female-portrait-v01'
PKG=ROOT/'game/assets/portraits/female-display-v01'
SOURCE=ROOT/'outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_female_20261013-153316-8fa4d0c3.png'
BUILDER=ROOT/f'tools/{SLUG}_protagonist-female_display-portrait-builder_v01_{TAG}.py'
HELPER=ROOT/f'game/scripts/{SLUG}_protagonist-female_display-portrait-helper_v01_{TAG}.gd'
def read(p):return Path(chr(92)*2+'?'+chr(92)+str(p.resolve())).read_bytes()
def sha(b):return hashlib.sha256(b).hexdigest()
def rgba(b):return np.array(Image.open(io.BytesIO(b)).convert('RGBA'))
def main():
    stop=ROOT.parents[1]/'work/dual01/control/rpg-2-star-ocean-the-second_dual-provider_global-stop_v01_20261019-001423-861097ca.json'
    if stop.exists():raise SystemExit('GLOBAL STOP')
    source=read(SOURCE);png=next(PKG.glob('*.png'));ora=next(PKG.glob('*.ora'));manifest=next(PKG.glob('*.json'));meta=json.loads(read(manifest))
    z=zipfile.ZipFile(io.BytesIO(read(ora)));stack=ET.fromstring(z.read('stack.xml'));layers=stack.find('stack').findall('layer')
    gates={
      'source-sha':sha(source)=='3d876c4f666913d6110fe8a058b79a55ce82ac225577d87f1f02624affeea58d',
      'source-size':rgba(source).shape==(821,1916,4),
      'all74329-pixels-exact':np.array_equal(rgba(read(png)),rgba(source)[42:353,952:1191]),
      'native239x311':rgba(read(png)).shape==(311,239,4),
      'original-producer-png-sha':sha(read(png))=='481182891a0bf9b110a2ba05ca69c9c902b9d208255cf76bddd1aeb6c15868f6',
      'original-producer-ora-sha':sha(read(ora))=='2351f7f6a501974db81b857053ea26082dc78d111dc8607df6bb651465260a85',
      'one-layer-ora':len(layers)==1 and layers[0].get('name')=='original-illustration-crop-952-42-1191-353',
      'ora-layer-png-byte-identical':z.read(layers[0].get('src'))==read(png),
      'ora-merged-exact':np.array_equal(rgba(z.read('mergedimage.png')),rgba(read(png))),
      'manifest-raw-sha-fields':all(sha(read(PKG/o['path']))==o['sha256'] for o in meta['outputs']),
      'display-fixed-contract':meta['display']['rect']=={'x':522,'y':88,'width':96,'height':124} and meta['display']['image_sha256']==sha(read(png)),
      'source-ai-no-new-generation':meta['provenance']['original_source_ai_generated'] is True and meta['provenance']['new_generative_processing'] is False,
      'unapproved-no-human-canon':meta['provenance']['unapproved'] is True and meta['provenance']['approval']=='none' and all(meta['provenance'][k] is False for k in ['human_artist','accepted_character_canon','approved_static','full_sprite_approved']),
      'safe-bare-artifact-paths':all(Path(o['path']).name==o['path'] and '..' not in o['path'] for o in meta['outputs']),
    }
    spec=importlib.util.spec_from_file_location('portrait_native_builder',BUILDER);builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    temps=[]
    for i in range(2):
      temp=ROOT/'work'/('portrait-proof-'+uuid.uuid4().hex[:8]);temp.mkdir();temps.append(temp)
      builder.build(types.SimpleNamespace(workspace=str(ROOT),source=str(SOURCE),out_dir=str(temp),timestamp_utc='2026-10-19T22:13:07Z',run_id='97f0236e',force=False))
    gates['same-runtime-all-rebuild-bytes-identical']=all(read(f)==read(temps[1]/f.name) for f in temps[0].iterdir())
    gates['rebuilt-png-pixels-identical']=np.array_equal(rgba(read(next(temps[0].glob('*.png')))),rgba(read(png)))
    rz=zipfile.ZipFile(io.BytesIO(read(next(temps[0].glob('*.ora')))))
    gates['rebuilt-ora-pixels-identical']=np.array_equal(rgba(rz.read('data/layer1.png')),rgba(read(png)))
    # Cross-runtime compression equality is recorded, not falsely required or claimed.
    cross=read(next(temps[0].glob('*.png')))==read(png)
    sources=[SOURCE,BUILDER,HELPER,ROOT/'game/scripts/growth_screen.gd',Path(__file__),ROOT/f'tools/{SLUG}_female-display_actual-runtime-check_v01_{TAG}.gd']+list(PKG.iterdir())
    report={'passed':sum(gates.values()),'total':len(gates),'gates':gates,'allRoiPixels':74329,'originalProducerCompressedBytesEqualLocalRebuild':cross,'compressionNote':'Producer art bytes preserved. Different Python/zlib binaries can encode identical PNG pixels differently; two same-runtime rebuilds are byte-exact.','hashAlgorithm':'raw-sha256; source text uses LF, no implicit normalization','sourceHashes':{p.relative_to(ROOT).as_posix():sha(read(p)) for p in sources},'actualRuntimeReport':f'{SLUG}_female-display_actual-runtime-report_v01_{TAG}.json','artApproval':False,'pxoClaimed':False}
    path=OUT/f'{SLUG}_female-display_source-bound-proof_v01_{TAG}.json';path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'passed':report['passed'],'total':report['total'],'crossRuntimeByteEquality':cross,'proof':str(path)},indent=2))
    if not all(gates.values()):raise SystemExit(1)
if __name__=='__main__':main()
