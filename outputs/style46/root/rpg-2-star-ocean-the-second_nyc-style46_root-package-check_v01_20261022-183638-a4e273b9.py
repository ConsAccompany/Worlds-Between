from pathlib import Path
import json,hashlib,io,zipfile,copy,subprocess,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
TAG="20261022-183638-a4e273b9"
lp=lambda p:Path('\\\\?\\'+str(p.resolve()))
read=lambda rel:lp(ROOT/rel).read_bytes()
arr=lambda b:np.array(Image.open(io.BytesIO(b)).convert('RGBA'))
sha=lambda b:hashlib.sha256(b).hexdigest()
m=json.loads(read((ROOT/'work/style46-manifest.txt').read_text()))
checks={}
def ck(name,condition):
 checks[name]=bool(condition)
 assert condition,name
for rel,v in m['files'].items():
 b=read(rel);algo=v['hash_algorithm'];ck('hash:'+rel,sha(b.replace(b'\r\n',b'\n') if algo=='sha256-text-lf-v1' else b)==v['sha256'])
old_dir='game/assets/environments/candidates/nyc-chp-v06_20261017-165253-4519dffe/'
old=json.loads(read(old_dir+'rpg-2-star-ocean-the-second_nyc-city-hall-park_scene_unapproved-v06_20261017-165253-4519dffe.json'))
newp=next(p for p in m['files'] if p.startswith('game/') and p.endswith('.json'))
new=json.loads(read(newp));nd=newp.rsplit('/',1)[0]+'/'
a=copy.deepcopy(old);b=copy.deepcopy(new)
for x in [a,b]:
 for k in ['run','source','status','base','walkmask']:x.pop(k)
 for row in x['ysort']:row.pop('png')
ck('scene_gameplay_contract_exact',a==b)
ck('walk_raw_bytes_exact',read(old_dir+old['walkmask'])==read(nd+new['walkmask']))
reference=arr(read(m['generated_provenance']['file']));h,w=reference.shape[:2]
flatp=next(p for p in m['files'] if '-flat-640x360_' in p);flat=arr(read(flatp))
sx=(np.arange(640)*2+1)*w//1280;sy=(np.maximum(0,np.arange(360)-24)*2+1)*h//720
ck('nearest_reference_pixels_exact',np.array_equal(flat,reference[sy][:,sx]))
base=arr(read(nd+new['base']));oldbase=arr(read(old_dir+old['base']));layers=[base];cover=np.zeros((360,640),bool)
for index,(o,n) in enumerate(zip(old['ysort'],new['ysort'])):
 oa=arr(read(old_dir+o['png']));na=arr(read(nd+n['png']));on=oa[:,:,3]==255;cover|=on
 ck('alpha_exact:'+str(index),np.array_equal(oa[:,:,3],na[:,:,3]));ck('opaque_rgb:'+str(index),np.array_equal(na[on],flat[on]));layers.append(na)
ck('base_uncovered_new',np.array_equal(base[~cover],flat[~cover]));ck('base_hidden_old',np.array_equal(base[cover],oldbase[cover]))
composite=Image.fromarray(base)
for a in layers[1:]:composite.alpha_composite(Image.fromarray(a))
ck('runtime_composite_flat_exact',np.array_equal(np.array(composite),flat))
ora=zipfile.ZipFile(io.BytesIO(read(next(p for p in m['files'] if p.endswith('.ora')))))
stack=ET.fromstring(ora.read('stack.xml')).find('stack');ordered=list(stack)[::-1]
ck('ora_11layers',len(ordered)==11);ck('ora_hidden_guide',ordered[-1].get('visibility')=='hidden')
ck('ora_merged_exact',np.array_equal(arr(ora.read('mergedimage.png')),flat))
for i,l in enumerate(ordered[:-1]):ck('ora_layer_exact:'+str(i),np.array_equal(arr(ora.read(l.get('src'))),layers[i]))
px=zipfile.ZipFile(io.BytesIO(read(next(p for p in m['files'] if p.endswith('.pxo')))));pd=json.loads(px.read('data.json'))
ck('pxo_11layers',len(pd['layers'])==11);ck('pxo_hidden_locked_guide',pd['layers'][-1]['visible']==False and pd['layers'][-1]['locked']==True)
for i,a in enumerate(layers,1):ck('pxo_cel_exact:'+str(i),px.read('image_data/frames/1/layer_'+str(i))==a.tobytes())
tres=read(next(p for p in m['files'] if p.endswith('.tres'))).decode();text=tres.split('metadata/scene_json = ',1)[1].strip();ck('tres_json_metadata_exact',json.loads(json.loads(text))==new)
protected=json.loads((ROOT/'work/style46-protected.json').read_bytes());changed=[p for p,h in protected.items() if sha(read(p))!=h]
ck('only_nyc_module_changed',changed==['game/scripts/city_hall_park_v06_scene.gd'])
before=json.loads(read('outputs/style46/root/rpg-2-star-ocean-the-second_nyc-style46_default-off-before_v01_'+TAG+'.json'));afterp=ROOT/('outputs/style46/root/rpg-2-star-ocean-the-second_nyc-style46_default-off-after_v01_'+TAG+'.json')
if afterp.exists():ck('default_off_all_three_destinations_exact',before==json.loads(afterp.read_bytes()))
result={'passed':len(checks),'checks':checks,'protectedFiles':len(protected),'unchangedRawFiles':len(protected)-1,'hiddenPlatePixels':int(cover.sum()),'generatedRasterNotHandPlacedPixels':True,'defaultAdopted':False,'artAccepted':False,'sourceHashes':{p:sha(read(p)) for p in [m['source'],'game/scripts/city_hall_park_v06_scene.gd']}}
path=ROOT/('outputs/style46/root/rpg-2-star-ocean-the-second_nyc-style46_root-package-and-scope-proof_v01_'+TAG+'.json');path.write_bytes((json.dumps(result,indent=2)+'\n').encode());print('STYLE46_PACKAGE_OK',len(checks))
