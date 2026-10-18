"""Four-direction idle only: exact static rests, local breath contours and delayed free tips.
No locomotion, whole-body bob, shearing, palette expansion or runtime adoption.
Reuses the inspected v06 animated PXO writer with RGBA cels; ORA is explicitly per phase.
"""
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
import hashlib,io,json,os,zipfile
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
STAMP='20261018-175418';ID='34294d7d';SLUG='rpg-2-star-ocean-the-second'
OUT=ROOT/'outputs/female-idle-four-v01'
WRITER='tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py'
NORTH='tools/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-build-and-check_unapproved-v01_20261018-090713-9af15df7.py'
SOURCES={
 'south':'game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png',
 'north':'game/assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot_unapproved-v01_20261018-090713-6ed8d8dd.png',
 'west':'outputs/female-west-static-v01/rpg-2-star-ocean-the-second_protagonist-female_west-static_unapproved-v01_20261018-174421-618816ac.png',
 'east':'outputs/female-east-static-v01/rpg-2-star-ocean-the-second_protagonist-female_east-static_unapproved-v01_20261018-175114-d55a2ba6.png'}
# Phase durations are seconds (PXO fps1); total4.8s. Chest precedes shoulders, free tips follow.
PHASES=[('rest',.60,0,0,0),('inhale-start',.40,1,0,0),('inhale-shoulder',.40,1,1,0),
 ('inhale-follow',.40,1,1,1),('inhale-crest',.40,2,1,1),('crest-settle',.40,2,1,0),
 ('exhale-start',.40,1,1,0),('exhale-cloth',.40,1,0,-1),('exhale-ease',.40,0,0,-1),
 ('cloth-settle',.30,0,0,0),('rest-enter',.30,0,0,0),('rest-hold',.40,0,0,0)]
ROLES=['fixed-body','seam-underlay','chest-breath','shoulder-breath','scarf-free-tip','coat-free-tip','pony-free-tip','guides']
# Direction-specific source masks; head, pack, canister, feet, hands stay fixed.
MASKS={
 'south':{'chest':[(29,37),(44,37),(45,54),(30,54)],'shoulder':[(24,38),(28,38),(28,49),(24,50)],'scarf':[(12,63),(24,63),(24,76),(12,76)],'pony':[(13,24),(23,24),(23,34),(13,34)],'front':0,'tip':-1},
 'north':{'chest':[(24,37),(27,37),(27,53),(24,53)],'shoulder':[(50,38),(55,38),(55,50),(50,50)],'scarf':[(49,62),(57,62),(57,77),(49,77)],'pony':[(48,25),(61,25),(61,36),(48,36)],'front':0,'tip':1},
 'west':{'chest':[(27,39),(33,39),(33,52),(27,52)],'shoulder':[(34,41),(40,42),(40,50),(34,49)],'scarf':[(50,68),(56,68),(56,74),(50,74)],'pony':[(50,26),(56,26),(56,36),(50,36)],'front':-1,'tip':1},
 'east':{'chest':[(46,39),(52,39),(52,52),(46,52)],'shoulder':[(40,41),(46,42),(46,50),(40,49)],'scarf':[(23,61),(32,61),(32,73),(23,73)],'pony':[(23,26),(29,26),(29,36),(23,36)],'front':1,'tip':-1}}

def long(p):
 s=str(Path(p).resolve());pre=chr(92)*2+'?'+chr(92)
 return pre+s if os.name=='nt' and not s.startswith(pre) else s
def read(p):return Path(long(p)).read_bytes()
def sha(b,text=False):return hashlib.sha256(b.replace(b'\r\n',b'\n') if text else b).hexdigest()
def module(path,name):
 spec=spec_from_file_location(name,ROOT/path);m=module_from_spec(spec);spec.loader.exec_module(m);return m
def rgba(b):return np.array(Image.open(io.BytesIO(b)).convert('RGBA'))
def png(a):
 b=io.BytesIO();Image.fromarray(a).save(b,format='PNG',compress_level=9);return b.getvalue()
def mask(points):
 m=Image.new('1',(80,112));ImageDraw.Draw(m).polygon(points,fill=1);return np.array(m,dtype=bool)
def flat(parts):
 im=Image.new('RGBA',(80,112))
 for name,a in parts.items():
  if name!='guides':im.alpha_composite(Image.fromarray(a))
 return np.array(im)
COAT_TIPS={'south':[(43,68),(51,68),(51,76),(43,76)],'north':[(26,68),(33,68),(33,76),(26,76)],'west':[(27,65),(32,65),(32,74),(27,74)],'east':[(49,65),(54,65),(54,74),(49,74)]}

def split(source,direction):
 spec=MASKS[direction];parts={k:np.zeros_like(source) for k in ROLES};remaining=source.copy()
 # Explicit material filtering prevents masks from taking skin, pack leather or metal.
 colors={'chest-breath':{'222839','3a4560','5e6e8c'},'shoulder-breath':{'222839','3a4560','5e6e8c','b09986','d7c0a8','faead4'},'coat-free-tip':{'222839','3a4560','5e6e8c'},'scarf-free-tip':{'0a323b','11525b','1a767b','249b98'},'pony-free-tip':{'0a0a0e','302526','533b32','41302b','634739','845436','714730'}}
 for role,key in [('pony-free-tip','pony'),('scarf-free-tip','scarf'),('coat-free-tip','coat'),('shoulder-breath','shoulder'),('chest-breath','chest')]:
  allowed={tuple(bytes.fromhex(c)) for c in colors[role]};region=mask(COAT_TIPS[direction] if key=='coat' else spec[key])
  select=region & (remaining[:,:,3]>0) & np.array([[tuple(c[:3]) in allowed for c in row] for row in remaining])
  parts[role][select]=remaining[select];remaining[select]=0
 parts['fixed-body']=remaining
 return parts
def free_tip(a,dx):
 if not dx:return a.copy()
 result=np.zeros_like(a);ys,xs=np.nonzero(a[:,:,3]);top=int(ys.min()) if len(ys) else 0
 # Attachment row remains pinned; lower free cluster translates a single source texel.
 for y,x in zip(ys,xs):result[y,x+(dx if y>top+1 else 0)]=a[y,x]
 return result
def contour(a,level,front,shoulder=False):
 result=a.copy()
 if not level:return result
 ys,xs=np.nonzero(a[:,:,3]);rows=sorted(set(ys))
 if not shoulder:
  # A local coat/chest fold lifts one texel; head/pack and the source patch boundary stay pinned.
  for y,x in zip(ys,xs):
   if a[y+1,x,3] and (level==2 or y<=rows[len(rows)//2]):result[y,x]=a[y+1,x]
 # Breathing locally opens the coat contour, not the skeleton or head. Inhale levels stagger rows.
 for y in rows:
  if y%2 and level==1:continue
  row=xs[ys==y]
  if shoulder:
   if y in rows[:2]:
    for x in row:result[y-1,x]=a[y,x]
  elif front:
   x=int(row.min() if front<0 else row.max());result[y,x+front]=a[y,x]
  elif y in rows[:3]:
   for x in row:result[y-1,x]=a[y,x]
 return result
def poses(source,direction):
 rest=split(source,direction);frames=[]
 assert np.array_equal(flat(rest),source)
 for _,_,chest,shoulder,lag in PHASES:
  p={k:a.copy() for k,a in rest.items()}
  p['chest-breath']=contour(rest['chest-breath'],chest,MASKS[direction]['front'])
  p['shoulder-breath']=contour(rest['shoulder-breath'],shoulder,0,True)
  p['coat-free-tip']=free_tip(rest['coat-free-tip'],lag*MASKS[direction]['tip'])
  p['scarf-free-tip']=free_tip(rest['scarf-free-tip'],lag*MASKS[direction]['tip'])
  p['pony-free-tip']=free_tip(rest['pony-free-tip'],lag*MASKS[direction]['tip'])
  # Restore only source texels vacated into a new enclosed single-pixel air gap.
  image=flat(p);o=image[:,:,3]>0;inside=(~o[1:-1,1:-1])&o[:-2,1:-1]&o[2:,1:-1]&o[1:-1,:-2]&o[1:-1,2:]
  ys,xs=np.nonzero(inside)
  for y,x in zip(ys+1,xs+1):
   if source[y,x,3]:p['seam-underlay'][y,x]=source[y,x]
  frames.append(p)
 return frames
def build():
 writer=module(WRITER,'idle_animated_writer');native=module(NORTH,'idle_ora_writer')
 writer.W,writer.H=80,112;writer.to_rgba=lambda a:np.ascontiguousarray(a,dtype=np.uint8)
 native.LAYERS=ROLES;native.ZIP_DT=(2026,10,18,17,54,18)
 OUT.mkdir(exist_ok=True,parents=True)
 manifest={'task':'content.char.protagonist-female.idle-anim','artApproved':False,'motionApproved':False,'runtimeIntegrated':False,'cell':[80,112],'pivot':[40,104],'scale':.5,'layers':ROLES,'cycleSeconds':4.8,'phases':[{'name':n,'seconds':d,'chest':c,'shoulder':s,'lag':l} for n,d,c,s,l in PHASES],'source':str(Path(__file__).relative_to(ROOT)).replace(chr(92),'/'),'sourceSha256TextLf':sha(read(__file__),True),'helpers':{p:sha(read(ROOT/p),True) for p in [WRITER,NORTH]},'directions':{},'oraRepresentation':'One separate editable layered ORA per direction/phase. ORA is not a multiframe format. Timing is defined by phases and the native animated PXO.','scope':'Only south rest static is creator approved. North/east/west statics and all idle motion remain proposals.'}
 palette={tuple(c) for c in rgba(read(ROOT/SOURCES['south'])).reshape(-1,4) if c[3]}
 for direction,path in SOURCES.items():
  source=rgba(read(ROOT/path));frames=poses(source,direction);source_entry={'file':path,'sha256':sha(read(ROOT/path)),'frames':[]}
  for i,parts in enumerate(frames):
   a=flat(parts);assert set(np.unique(a[:,:,3]))<={0,255};assert np.array_equal(a[78:],source[78:]);assert {tuple(c) for c in a.reshape(-1,4) if c[3]}<=palette
   assert (np.nonzero(a[:,:,3])[0].min(),np.nonzero(a[:,:,3])[0].max())==(8,103)
   if i in [0,9,10,11]:assert np.array_equal(a,source)
   parts['guides']=native.v8t.guides_rgba(a)
   stem=f'{SLUG}_female-{direction}_idle-phase-{i:02d}_unapproved-v01_{STAMP}-{ID}'
   files={}
   for ext,data in [('png',png(a)),('ora',native.make_ora(parts,png(a)))]:
    name=stem+'.'+ext;Path(long(OUT/name)).write_bytes(data);files[ext]={'file':str((OUT/name).relative_to(ROOT)).replace(chr(92),'/'),'sha256':sha(data)}
   source_entry['frames'].append({'phase':i,'changedTexels':int(np.any(a!=source,axis=2).sum()),'files':files})
  pxo=writer.make_pxo(frames,[p[1] for p in PHASES],png(source),f'{SLUG}_female-{direction}_idle-export_unapproved-v01_{STAMP}-{ID}',1.,order=ROLES,dt=(2026,10,18,17,54,18))
  src=zipfile.ZipFile(io.BytesIO(pxo));b=io.BytesIO()
  with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
   for info in src.infolist():
    data=src.read(info.filename)
    if info.filename=='data.json':
     d=json.loads(data);d['layers'][-1]['visible']=False;d['layers'][-1]['locked']=True;d['tags']=[{'name':'idle-'+direction,'from':1,'to':12,'color':'1a9999'}];d['user_data']='Unapproved static-preserving local idle breath; cycle4.8s; no runtime defaults.';data=json.dumps(d,separators=(',',':')).encode()
    z.writestr(info,data)
  name=f'{SLUG}_female-{direction}_idle-animated-source_unapproved-v01_{STAMP}-{ID}.pxo';Path(long(OUT/name)).write_bytes(b.getvalue());source_entry['uniqueRgbaPoses']=len({f['files']['png']['sha256'] for f in source_entry['frames']});source_entry['pxo']={'file':str((OUT/name).relative_to(ROOT)).replace(chr(92),'/'),'sha256':sha(b.getvalue())};manifest['directions'][direction]=source_entry
 path=OUT/f'{SLUG}_female-idle-four_direction-manifest_unapproved-v01_{STAMP}-{ID}.json';path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n');print(path)
 for k,v in manifest['directions'].items():print(k,[f['changedTexels'] for f in v['frames']])
 return manifest
if __name__=='__main__':build()
