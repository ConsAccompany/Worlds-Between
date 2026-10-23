"""Independent Lin Que static source checks. No runtime/art/motion approval."""
from pathlib import Path
import argparse,hashlib,importlib.util,io,json,os,zipfile
from PIL import Image
import numpy as np
ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',required=True);a=ap.parse_args()
R=Path(a.root).resolve();O=Path(a.out).resolve();O.mkdir(parents=True,exist_ok=True)
if os.name=='nt':R=Path('\\\\?\\'+str(R));O=Path('\\\\?\\'+str(O))
sp=importlib.util.spec_from_file_location('ora_helpers',R/'tools/rpg-2-star-ocean-the-second_jiang-lan_static-source-check_v01_20261021-235007-514b9771.py');H=importlib.util.module_from_spec(sp);sp.loader.exec_module(H)
TAG='20261022-222500-3d61c74e';checks=[];pins={};images={};clean={}
def gate(n,v,detail=None):checks.append({'id':n,'passed':bool(v),'detail':detail})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes(m,f):return all(sha(f/v['file'])==v['rawsha256'] for v in m['files'].values())
for d in ('south','west','north','east'):
 f=R/'game/assets/characters/lin-que-native-v01'/d;ms=list(f.glob('*manifest*.json'));assert len(ms)==1,(d,'missing/ambiguous manifest')
 m=json.loads(ms[0].read_text(encoding='utf8'));clean[d]=(m,f)
 gate(d+'.identity',m['actor_id']=='lin-que' and m['content_id']=='content.char.lin-que.static-'+d and m['direction']==d and m['status']=='UNAPPROVED')
 gate(d+'.spec',m['canvas']==[80,112] and m['pivot']==[40,104] and m['body_rows']==[8,103] and m['display_scale']==.5 and m['logical_height_px']==48)
 gate(d+'.filehashes',hashes(m,f));p=m['portrait_ref'];gate(d+'.portrait',p['file']=='outputs/rpg-2-star-ocean-the-second_lin-que_character-sheet_v01_20261013-153556-88b92720.png' and sha(R/p['file'])==p['expected_sha256']=='24007e147c9dd67b330af4a84ac13054f65989cddb9bdf2702dc5c80de7fb352')
 im=Image.open(f/m['files']['png']['file']).convert('RGBA');ar=np.array(im);images[d]=ar;al=ar[:,:,3];ys,xs=np.nonzero(al)
 gate(d+'.canvas',im.size==(80,112));gate(d+'.body',ys.min()==8 and ys.max()==103);gate(d+'.binary_alpha',set(np.unique(al))<={0,255});gate(d+'.borders',not(al[0].any() or al[-1].any() or al[:,0].any() or al[:,-1].any()))
 pal=json.loads((f/m['files']['palette']['file']).read_text(encoding='utf8'));decl={tuple(bytes.fromhex(v.lstrip('#'))) for v in pal['colors'].values()};used={tuple(x) for x in ar[al==255,:3]};gate(d+'.palette',24<=len(used)<=48 and used<=decl,len(used))
 with zipfile.ZipFile(f/m['files']['ora']['file']) as z:
  ls=H.ora_layers(z);comp=H.compose(z,ls);gate(d+'.ora_composition',comp.tobytes()==ar.tobytes());gate(d+'.ora_merged',Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA').tobytes()==ar.tobytes());gate(d+'.ora_mimetype',z.infolist()[0].filename=='mimetype' and z.infolist()[0].compress_type==zipfile.ZIP_STORED)
  visible=[l for l in ls if l['visible'] and not H.GUIDE_RE.search(l['name'])];contrib=[]
  for l in visible:
   without=H.compose(z,[x for x in ls if x is not l]);count=np.count_nonzero(np.any(np.array(without)!=ar,axis=2))
   if count>=8:contrib.append(l['name'])
  gate(d+'.genuine_ora_roles',len(contrib)>=8,contrib);gate(d+'.hidden_guides',any(H.GUIDE_RE.search(l['name']) and not l['visible'] for l in ls) and not any(H.GUIDE_RE.search(l['name']) and l['visible'] for l in ls))
 with zipfile.ZipFile(f/m['files']['pxo']['file']) as z:
  raw=z.read('data.json');j=json.loads(raw);canvas=np.zeros_like(ar);roles=0
  for i,l in enumerate(j['layers'],1):
   x=np.frombuffer(z.read(f'image_data/frames/1/layer_{i}'),np.uint8).reshape(112,80,4)
   if l['visible']:
    mask=x[:,:,3]>0;canvas[mask]=x[mask];roles+=int(np.count_nonzero(mask)>=8 and not H.GUIDE_RE.search(l['name']))
  gate(d+'.pxo_composition',np.array_equal(canvas,ar));gate(d+'.pxo_roles',roles>=8,roles);gate(d+'.pxo_labels',b'protagonist-male' not in raw and b'jiang-lan' not in raw);gate(d+'.pxo_guides',any(l['name']=='guides' and not l['visible'] for l in j['layers']))
 bad=json.loads(json.dumps(m));bad['files']['png']['rawsha256']='0'*64;gate(d+'.corrupt_hash_refused',hashes(m,f) and not hashes(bad,f))
 if d=='south':(O/f'rpg-2-star-ocean-the-second_lin-que_corrupt-hash-control_test-only-v01_{TAG}.json').write_text(json.dumps(bad,indent=2)+'\n',encoding='utf8')
 pins[d]={x.name:sha(x) for x in f.iterdir() if x.is_file()}
gate('east_not_blind_mirror',not np.array_equal(images['east'],np.fliplr(images['west'])))
gate('all_directions_distinct',len({x.tobytes() for x in images.values()})==4)
report={'passed':all(c['passed'] for c in checks),'checks':checks,'sourceHashes':pins,'checkerSha256':sha(Path(__file__)),'scope':'editable static source only; no GUI reliability/motion/ordinary adoption/art approval'}
(O/f'rpg-2-star-ocean-the-second_lin-que_independent-source-proof_v01_{TAG}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print('LIN58D_INDEPENDENT',sum(c['passed'] for c in checks),'/',len(checks));print('FAILURES',[c['id'] for c in checks if not c['passed']]);raise SystemExit(0 if report['passed'] else 1)
