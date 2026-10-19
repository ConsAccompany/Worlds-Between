"""Independent four-crop oracle, original-byte preservation and same-runtime determinism."""
from pathlib import Path
from PIL import Image
import numpy as np
import hashlib, io, json, zipfile, xml.etree.ElementTree as ET, importlib.util, datetime, uuid
ROOT=Path(__file__).resolve().parents[1]
TAG='20261019-185434-7c95e421';SLUG='rpg-2-star-ocean-the-second'
OUT=ROOT/'outputs/mvp-portraits-v01';PKG=ROOT/'game/assets/portraits/mvp-display-v01'
BUILDER=ROOT/f'tools/{SLUG}_mvp-display_portrait-builder_v01_{TAG}.py'
EXPECTED={'protagonist-male':([948,54,1187,365],'d92a3c4442f71394bb118a5034c57d52a3e3e7b2142bcb2b0b69d964e3dc4765'),
          'liang-xu':([930,35,1235,403],'af2da3de75c8eea1779688b16396860721f7e2d9156fd90c28df13d0e2ffd56f'),
          'ji-cheng':([830,10,1190,420],'4165c47e28329e2d4fd2dd160886118a70cb06fd160172b90ba45f00584cc546'),
          'zhao-ling':([830,15,1210,360],'5fe7b5e8f41878e0a96883164afb7069300663e03e4e9815f2cb17dc9500d780')}
def read(p):return Path(chr(92)*2+'?'+chr(92)+str(p.resolve())).read_bytes()
def sha(b):return hashlib.sha256(b).hexdigest()
def rgba(b):return np.array(Image.open(io.BytesIO(b)).convert('RGBA'))
def main():
    assert not (ROOT.parents[1]/'work/dual01/control/rpg-2-star-ocean-the-second_dual-provider_global-stop_v01_20261019-001423-861097ca.json').exists()
    gates={};details=[];pixels=0
    producer=ROOT.parents[1]/'work/dual02/ds-portrait/game/assets/portraits/mvp-display-v01'
    for manifest in sorted(PKG.glob('*.json')):
      m=json.loads(read(manifest));subject=m['subject'];roi,source_sha=EXPECTED[subject];png=PKG/m['image']['path'];ora=PKG/next(o['path'] for o in m['outputs'] if o['kind']=='editable-openraster-ora');source=ROOT/m['source']['path'];art=rgba(read(png));z=zipfile.ZipFile(io.BytesIO(read(ora)));layers=ET.fromstring(z.read('stack.xml')).find('stack').findall('layer');l,t,r,b=roi
      checks={'source-sha':sha(read(source))==source_sha,'source-native1916x821':rgba(read(source)).shape==(821,1916,4),'all-roi-pixels-exact':np.array_equal(art,rgba(read(source))[t:b,l:r]),'native-crop-size':art.shape==(b-t,r-l,4),'one-layer-ora':len(layers)==1,'ora-layer-bytes-exact':z.read(layers[0].get('src'))==read(png),'ora-merged-exact':np.array_equal(rgba(z.read('mergedimage.png')),art),'producer-png-bytes-preserved':(read(png)==read(producer/png.name)) if subject!='ji-cheng' else m['crop']['right']==1190,'producer-ora-bytes-preserved':(read(ora)==read(producer/ora.name)) if subject!='ji-cheng' else m['crop']['width']==360,'manifest-output-hashes':all(sha(read(PKG/o['path']))==o['sha256'] for o in m['outputs']),'manifest-identity':m['content_id']=='content.char.'+subject+'.display' and m['display']['variant_key']==subject,'explicit-original-ai-no-new-generation':m['provenance']['original_source_ai_generated'] is True and m['provenance']['new_generative_processing'] is False,'no-human-canon-approval':m['provenance']['human_artist'] is False and m['provenance']['approval']=='none' and m['provenance']['accepted_character_canon'] is False and m['provenance']['full_sprite_approved'] is False,'fixed-display':m['display']['rect']=={'x':522,'y':88,'width':96,'height':124},'normalized-manifest-name':'_display-portrait-manifest_v0' in manifest.name and not manifest.name.endswith('.manifest.json')}
      if subject=='ji-cheng':
        checks.pop('producer-png-bytes-preserved');checks.pop('producer-ora-bytes-preserved')
        prior=OUT/'prior-ji-crop-v01'
        checks['producer-prior-png-bytes-preserved']=read(next(prior.glob('*.png')))==read(next(producer.glob('*ji-cheng*.png')))
        checks['producer-prior-ora-bytes-preserved']=read(next(prior.glob('*.ora')))==read(next(producer.glob('*ji-cheng*.ora')))
      for key,value in checks.items():gates[subject+'/'+key]=bool(value)
      pixels+=(r-l)*(b-t);details.append({'subject':subject,'roi':roi,'pixels':(r-l)*(b-t),'source':str(source.relative_to(ROOT)),'pngRawSha256':sha(read(png)),'oraRawSha256':sha(read(ora))})
    spec=importlib.util.spec_from_file_location('mvp_portrait_builder',BUILDER);builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    temps=[]
    for i in range(2):
      tmp=ROOT/'work'/('mvp-proof-'+uuid.uuid4().hex[:8]);tmp.mkdir();temps.append(tmp)
      for variant in builder.VARIANTS:builder.build_one(variant,datetime.datetime(2026,10,19,22,45,38,tzinfo=datetime.timezone.utc),'20261019-224538','7c41a9d2',str(tmp),str(ROOT))
    gates['same-runtime-rebuild-all-bytes-identical']=all(read(f)==read(temps[1]/f.name) for f in temps[0].iterdir())
    gates['rebuilt-pixels-all-exact']=all(np.array_equal(rgba(read(f)),rgba(read(PKG/f.name))) for f in temps[0].glob('*.png'))
    files=[BUILDER,ROOT/f'game/scripts/{SLUG}_mvp-display_portrait-helper_v01_{TAG}.gd',ROOT/'game/scripts/growth_screen.gd',Path(__file__),ROOT/f'tools/{SLUG}_mvp-display_actual-runtime-check_v01_{TAG}.gd']+list(PKG.iterdir())
    report={'passed':sum(gates.values()),'total':len(gates),'gates':gates,'pixelsChecked':pixels,'details':details,'sourceRawSha256':{f.relative_to(ROOT).as_posix():sha(read(f)) for f in files},'compressionNote':'Three original producer PNG/ORA pairs are byte-preserved; Ji v02 is a new narrower exact crop, with its original v01 producer art retained as prior evidence. Bundled Python rebuilds have identical decoded pixels and deterministic bytes in their own runtime; cross-runtime compression bytes are not claimed identical.','approved':False}
    path=OUT/f'{SLUG}_mvp-display_source-bound-proof_v01_{TAG}.json';path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print('MVP_PACKAGE',report['passed'],'/',report['total'],'pixels',pixels)
    if not all(gates.values()):raise SystemExit(1)
if __name__=='__main__':main()
