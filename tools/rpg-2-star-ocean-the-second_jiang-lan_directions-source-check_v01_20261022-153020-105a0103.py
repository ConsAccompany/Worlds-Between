"""Codex independent native direction checker. No runtime or approval claims."""
from pathlib import Path
import argparse,hashlib,io,json,zipfile,importlib.util
from PIL import Image
import numpy as np
P=argparse.ArgumentParser();P.add_argument('--root',default='.');P.add_argument('--out',required=True);A=P.parse_args();R=Path(A.root).resolve();O=Path(A.out).resolve();O.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('ora_check',R/'tools/rpg-2-star-ocean-the-second_jiang-lan_static-source-check_v01_20261021-235007-514b9771.py');H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
checks=[];pins={};images={};roles={'boots','trousers','shirt','vest','arms','devices','face','hair','goggles'}
def gate(name,ok):checks.append({'id':name,'ok':bool(ok)})
def sha(b):return hashlib.sha256(b).hexdigest()
def hashes_ok(m,folder):return all(sha((folder/v['file']).read_bytes())==v['rawsha256'] for v in m['files'].values())
for d in ['west','north','east']:
 folder=R/'game/assets/characters/jiang-lan-native-directions-v01'/d;ms=list(folder.glob('*manifest*.json'));assert len(ms)==1,(d,ms);m=json.loads(ms[0].read_bytes());gate(d+'.identity',m['actor_id']=='jiang-lan' and m['direction']==d and m['content_id']=='content.char.jiang-lan.static-'+d);gate(d+'.unapproved',m['status']=='UNAPPROVED');gate(d+'.dimensions',m['canvas']==[80,112]);gate(d+'.pivot',m['pivot']==[40,104]);gate(d+'.body',m['body_rows']==[8,103] and m['display_scale']==.5 and m['logical_height_px']==48);gate(d+'.filehashes',hashes_ok(m,folder));bad=json.loads(json.dumps(m));bad['files']['png']['rawsha256']='0'*64;gate(d+'.bad_hash_refused',not hashes_ok(bad,folder));port=R/m['portrait_ref']['file'];gate(d+'.portrait',sha(port.read_bytes())==m['portrait_ref']['expected_sha256']=='bbddf46f3c1370742c86d1934e36adf7969e5f43a4e6d67ddbf9ba8d44902e4a')
 png=folder/m['files']['png']['file'];im=Image.open(png).convert('RGBA');a=np.array(im);images[d]=a;gate(d+'.native_size',im.size==(80,112));al=a[:,:,3];ys,xs=np.nonzero(al);gate(d+'.actual_height',int(ys.min())==8 and int(ys.max())==103);gate(d+'.binary_alpha',set(np.unique(al))<={0,255});gate(d+'.transparent_border',not (al[0].any() or al[-1].any() or al[:,0].any() or al[:,-1].any()));palette=json.loads((folder/m['files']['palette']['file']).read_bytes());decl={tuple(bytes.fromhex(x)) for x in palette['colors'].values()};cols={tuple(x) for x in a[al==255,:3]};gate(d+'.palette',24<=len(cols)<=48 and cols<=decl)
 with zipfile.ZipFile(folder/m['files']['ora']['file']) as z:
  layers=H.ora_layers(z);comp=H.compose(z,layers);gate(d+'.ora_composition',comp.tobytes()==im.tobytes());gate(d+'.ora_merged',Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA').tobytes()==im.tobytes());visible=[x for x in layers if x['visible']];nonempty=[x for x in visible if np.count_nonzero(np.array(Image.open(io.BytesIO(z.read(x['src']))).convert('RGBA'))[:,:,3])>=8];gate(d+'.ora_roles',len({x['name'] for x in nonempty}&roles)>=8);gate(d+'.hidden_guides',any(x['name']=='guides' and not x['visible'] for x in layers));gate(d+'.ora_mimetype',z.infolist()[0].filename=='mimetype' and z.infolist()[0].compress_type==zipfile.ZIP_STORED)
 with zipfile.ZipFile(folder/m['files']['pxo']['file']) as z:
  j=json.loads(z.read('data.json'));canvas=np.zeros_like(a);count=0
  for i,l in enumerate(j['layers'],1):
   ar=np.frombuffer(z.read(f'image_data/frames/1/layer_{i}'),np.uint8).reshape(112,80,4)
   if l['visible']:
    mask=ar[:,:,3]>0;canvas[mask]=ar[mask];count+=int(l['name'] in roles and np.count_nonzero(mask)>=8)
  gate(d+'.pxo_composition',np.array_equal(canvas,a));gate(d+'.pxo_roles',count>=8);gate(d+'.pxo_metadata',b'protagonist-male' not in z.read('data.json'));gate(d+'.pxo_guides',any(x['name']=='guides' and not x['visible'] for x in j['layers']))
 pins[d]={x.name:sha(x.read_bytes()) for x in folder.iterdir() if x.is_file()}
gate('east_not_blind_mirror',not np.array_equal(images['east'],np.fliplr(images['west'])));gate('directions_distinct',all(not np.array_equal(images[x],images[y]) for x,y in [('west','north'),('north','east'),('west','east')]))
report={'checks':checks,'passed':all(x['ok'] for x in checks),'hashes':pins,'checkerSha256':sha(Path(__file__).read_bytes()),'scope':'independent native source only; not GUI/app-clean, motion, actor adoption or creator approval'};tag='20261022-153020-105a0103';(O/f'rpg-2-star-ocean-the-second_jiang-lan_independent-three-direction-check_v01_{tag}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print('JIANG38_INDEPENDENT',sum(x['ok'] for x in checks),'/',len(checks));print('FAILURES',[x['id'] for x in checks if not x['ok']]);raise SystemExit(0 if report['passed'] else 1)
