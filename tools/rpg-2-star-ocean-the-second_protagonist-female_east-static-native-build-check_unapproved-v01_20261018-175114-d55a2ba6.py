"""One new east-profile static, not a transformed south image. Reuses only tracked native container writers/palette."""
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
import hashlib,io,json,os,subprocess,tempfile,zipfile,sys
from PIL import Image,ImageDraw
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
STAMP='20261018-175114'
IDENT='d55a2ba6'
PREFIX='rpg-2-star-ocean-the-second_protagonist-female'
OUT=ROOT/'outputs/female-east-static-v01'
NORTH_TOOL=ROOT/'tools/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-build-and-check_unapproved-v01_20261018-090713-9af15df7.py'
spec=spec_from_file_location('female_native_container_reuse',NORTH_TOOL);base=module_from_spec(spec);spec.loader.exec_module(base)
V8=ROOT/base.v8t.V8_REL
LAYERS=['far-leg-boot','far-canister','backpack','coat','near-leg-boot','head-face','near-arm','leather-straps','bedroll','scarf-tail','hair','ponytail']
base.LAYERS=LAYERS+['guides'];base.ZIP_DT=(2026,10,18,17,40,0)
PAL={k:tuple(bytes.fromhex(v))+(255,) for k,v in base.PAL.items()}

def sha(data):return hashlib.sha256(data).hexdigest()
def native(path):
 value=str(Path(path).resolve());prefix=chr(92)*2+'?'+chr(92)
 return prefix+value if os.name=='nt' and not value.startswith(prefix) else value

def paint():
 images={name:Image.new('RGBA',(80,112)) for name in LAYERS}
 def poly(layer,coords,color):ImageDraw.Draw(images[layer]).polygon(coords,fill=PAL[color])
 def line(layer,coords,color,width=1):ImageDraw.Draw(images[layer]).line(coords,fill=PAL[color],width=width)
 def box(layer,rect,color):ImageDraw.Draw(images[layer]).rectangle(rect,fill=PAL[color])
 # Far left leg is behind the near right leg; planted rightward toe, no lifted heel.
 poly('far-leg-boot',[(33,69),(41,69),(43,81),(41,91),(34,93),(32,85)],'C')
 poly('far-leg-boot',[(35,73),(39,73),(40,82),(38,90),(35,90)],'E')
 line('far-leg-boot',[(36,77),(37,83),(35,88)],'O')
 poly('far-leg-boot',[(33,89),(41,88),(43,96),(48,100),(47,103),(33,103),(31,100)],'F')
 poly('far-leg-boot',[(35,91),(39,90),(40,97),(45,100),(45,101),(34,101)],'B')
 line('far-leg-boot',[(34,93),(40,92)],'J');box('far-leg-boot',(35,94,37,95),'b')
 # The character-left canister is far side in this view: narrow end glimpse behind the pack/coat.
 poly('far-canister',[(25,58),(29,57),(32,61),(31,71),(28,74),(24,71),(23,62)],'Z')
 poly('far-canister',[(25,61),(28,60),(29,63),(28,71),(26,71)],'b')
 line('far-canister',[(25,63),(25,69)],'e');box('far-canister',(24,62,30,63),'S');box('far-canister',(25,62,28,62),'G')
 # Rear pack left of the torso: same leather kit, alternate-side seam, no added pocket.
 poly('backpack',[(27,39),(36,39),(40,46),(39,61),(35,67),(25,64),(22,46)],'F')
 poly('backpack',[(28,41),(34,41),(37,46),(36,59),(33,63),(26,61),(25,47)],'B')
 poly('backpack',[(28,42),(34,42),(36,46),(34,49),(27,48)],'L')
 line('backpack',[(25,47),(26,57),(29,61)],'H');line('backpack',[(34,42),(34,48),(28,48)],'K')
 box('backpack',(25,51,31,59),'H');line('backpack',[(26,52),(30,52),(30,57)],'L');box('backpack',(29,48,31,50),'b')
 # Authored right-facing coat opening and overlapping rear vent; source shapes differ from WEST.
 poly('coat',[(38,35),(48,36),(52,44),(50,56),(54,68),(51,73),(44,70),(39,74),(31,73),(29,69),(33,57),(32,45)],'C')
 poly('coat',[(39,37),(46,38),(49,44),(47,54),(50,66),(49,70),(44,67),(39,71),(33,70),(35,59),(34,46)],'D')
 line('coat',[(46,39),(49,44),(47,49),(48,60),(51,67)],'P')
 poly('coat',[(48,42),(46,44),(46,51),(50,55),(51,49)],'U')
 line('coat',[(48,42),(50,47),(49,53)],'X');line('coat',[(40,47),(41,55),(37,63),(35,69)],'C')
 line('coat',[(44,60),(43,65),(46,69)],'P');line('coat',[(35,60),(33,68),(32,71)],'b')
 line('coat',[(49,57),(37,60),(35,62)],'F');line('coat',[(48,58),(38,61)],'J');box('coat',(46,58,49,61),'b');box('coat',(47,59,48,60),'U')
 # Near right trouser profile and boot, both authored with rightward toe at floor row103.
 poly('near-leg-boot',[(40,71),(48,70),(51,83),(49,91),(41,92),(38,82)],'C')
 poly('near-leg-boot',[(42,74),(47,72),(48,82),(46,89),(42,90),(41,82)],'E')
 line('near-leg-boot',[(46,76),(45,82),(47,87)],'O');line('near-leg-boot',[(40,79),(42,85),(42,90)],'C')
 poly('near-leg-boot',[(41,89),(49,88),(50,96),(54,98),(56,101),(55,103),(39,103),(38,100),(40,98)],'F')
 poly('near-leg-boot',[(43,91),(47,90),(47,97),(52,99),(53,101),(41,101),(41,99)],'B')
 line('near-leg-boot',[(42,92),(48,91)],'K');line('near-leg-boot',[(43,95),(48,94)],'J');box('near-leg-boot',(43,94,45,95),'b');line('near-leg-boot',[(47,100),(51,99),(53,100)],'L')
 # Real east-facing face: eye/brow then nose tip/chin to right; visible ear is behind the eye.
 poly('head-face',[(39,18),(47,18),(51,22),(51,26),(54,27),(56,29),(54,30),(54,33),(50,34),(49,37),(44,39),(42,35),(37,32),(36,24)],'B')
 poly('head-face',[(40,20),(46,20),(49,23),(49,27),(52,29),(54,29),(52,31),(50,32),(46,34),(41,31),(39,25)],'T')
 poly('head-face',[(44,21),(48,22),(48,26),(50,28),(52,29),(47,29),(44,26)],'R')
 box('head-face',(49,25,51,25),'Q');box('head-face',(49,24,51,24),'B');box('head-face',(50,25,50,25),'X');box('head-face',(51,25,51,25),'A')
 line('head-face',[(51,31),(53,31)],'B');box('head-face',(53,28,53,28),'R')
 poly('head-face',[(38,25),(41,25),(42,28),(40,30),(37,29)],'T');line('head-face',[(39,26),(38,27),(39,28)],'V')
 # Near right shoulder: relaxed sleeve, cream cuff, skin and glove. Far accessory remains behind.
 poly('near-arm',[(49,35),(44,37),(39,35),(36,38),(38,42),(46,44),(50,41),(52,38)],'S')
 poly('near-arm',[(50,36),(45,38),(40,37),(40,40),(46,42),(50,40)],'M');line('near-arm',[(49,36),(46,38),(42,38)],'G')
 poly('near-arm',[(43,42),(48,42),(51,46),(51,52),(48,56),(41,55),(39,49),(40,44)],'C')
 poly('near-arm',[(44,43),(47,43),(49,47),(49,51),(45,53),(42,51),(42,47)],'D');line('near-arm',[(48,44),(50,49),(48,52)],'P')
 poly('near-arm',[(42,53),(49,52),(51,55),(49,57),(42,57)],'I');line('near-arm',[(43,54),(49,53)],'X');line('near-arm',[(43,56),(49,56)],'N')
 poly('near-arm',[(43,57),(49,57),(51,62),(50,65),(45,66),(44,63)],'V');poly('near-arm',[(46,58),(49,57),(50,63),(47,63)],'T')
 poly('near-arm',[(45,64),(50,63),(52,66),(51,69),(47,70),(44,68)],'F');line('near-arm',[(47,65),(50,64),(50,67)],'H');box('near-arm',(48,68,49,69),'T')
 # Visible right-side shoulder webbing passes across the rear shoulder, away from the sleeve opening.
 line('leather-straps',[(37,39),(40,42),(41,50),(39,58)],'F',3);line('leather-straps',[(37,39),(39,43),(40,48)],'J');box('leather-straps',(39,45,41,48),'b');box('leather-straps',(40,46,40,47),'U')
 # Opposite bedroll end: a smaller shaded end cap with straps, not the WEST highlight spiral copied.
 poly('bedroll',[(28,31),(33,31),(37,35),(37,40),(34,44),(28,44),(24,40),(24,35)],'S')
 poly('bedroll',[(29,32),(33,33),(35,35),(35,39),(33,42),(29,42),(26,39),(26,35)],'M')
 line('bedroll',[(29,34),(32,34),(34,36),(34,39),(31,40),(28,38),(29,36),(31,36),(32,38)],'G');line('bedroll',[(25,35),(25,39),(28,42)],'c');line('bedroll',[(35,34),(38,38),(36,42)],'F')
 # Right-side scarf tail is the near accessory, therefore visible over the pack/coat rear edge.
 poly('scarf-tail',[(38,40),(34,42),(32,49),(30,58),(25,67),(24,72),(28,70),(34,62),(36,52),(40,44)],'S')
 poly('scarf-tail',[(37,42),(35,45),(34,52),(32,60),(27,68),(26,70),(30,65),(35,59),(37,49)],'M');line('scarf-tail',[(35,45),(34,53),(31,61)],'G')
 # Separate fringe/ear opening and locks; light remains upper left rather than mirrored with face.
 poly('hair',[(49,16),(44,14),(38,15),(34,19),(34,27),(36,33),(40,34),(41,31),(39,27),(40,23),(43,21),(45,23),(47,23),(47,20),(50,21),(52,24),(53,22),(52,18)],'A')
 poly('hair',[(48,17),(44,16),(39,17),(36,20),(36,26),(38,30),(39,28),(38,23),(41,20),(45,19),(48,20),(51,22),(51,19)],'F')
 poly('hair',[(39,17),(43,16),(47,17),(49,19),(45,18),(41,19),(38,21)],'B');line('hair',[(39,17),(42,17),(45,18)],'L');line('hair',[(36,20),(35,23),(36,27)],'H')
 line('hair',[(46,20),(48,22),(49,24)],'Q');line('hair',[(36,29),(37,33),(35,35)],'A');line('hair',[(38,29),(39,32)],'B')
 # High pony has a distinct, slightly looser side arc; top row8 maintains approved master bounds.
 poly('ponytail',[(39,15),(38,12),(35,8),(31,8),(27,10),(24,14),(23,19),(25,24),(23,29),(25,34),(27,35),(27,30),(28,26),(26,21),(27,16),(31,13),(35,14),(36,17)],'A')
 poly('ponytail',[(37,13),(34,10),(31,10),(28,12),(26,16),(25,19),(27,24),(25,29),(26,32),(26,27),(28,24),(27,20),(29,16),(32,13),(35,15)],'F')
 line('ponytail',[(28,12),(31,10),(34,11),(36,14)],'L');line('ponytail',[(27,15),(29,12),(32,11)],'K');line('ponytail',[(24,17),(24,20),(26,24)],'B');line('ponytail',[(25,27),(24,30),(26,34)],'H');box('ponytail',(36,14,38,15),'J')
 return images

def build():
 base.v8t.v8_checked();images=paint();full=Image.new('RGBA',(80,112))
 for image in images.values():full.alpha_composite(image)
 arr=np.array(full);op=arr[:,:,3]>0;ys,xs=np.nonzero(op);palette={tuple(p) for p in np.array(Image.open(native(V8)).convert('RGBA'))[np.array(Image.open(native(V8)).convert('RGBA'))[:,:,3]>0]}
 assert set(np.unique(arr[:,:,3]))<={0,255} and ys.min()==8 and ys.max()==103 and xs.min()>0 and xs.max()<79
 assert {tuple(p) for p in arr[op]}<=palette
 assert xs[ys>=97].min()<=40<=xs[ys>=97].max()
 blobs={k:np.array(v) for k,v in images.items()};blobs['guides']=base.v8t.guides_rgba(arr)
 png=base.png_bytes(arr);pxo=base.make_pxo(blobs,png);ora=base.make_ora(blobs,png)
 # Reuse format code, but never retain north-facing export metadata in the east document.
 old=zipfile.ZipFile(io.BytesIO(pxo));buf=io.BytesIO()
 with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
  for item in old.infolist():
   payload=old.read(item.filename)
   if item.filename=='data.json':
    d=json.loads(payload);d['export_profile']['file_name']=json.dumps('protagonist-female-east-static-v01');d['user_data']=d['user_data'].replace('north pilot','east pilot');payload=json.dumps(d,separators=(',',':')).encode()
   z.writestr(item,payload)
 OUT.mkdir(parents=True,exist_ok=True);files={}
 for role,ext,data in [('static','png',png),('layered-source','pxo',buf.getvalue()),('layered-source','ora',ora)]:
  name=f'{PREFIX}_east-{role}_unapproved-v01_{STAMP}-{IDENT}.{ext}';(OUT/name).write_bytes(data);files[ext]={'file':str((OUT/name).relative_to(ROOT)).replace(chr(92),'/'),'sha256':sha(data)}
 manifest={'task':'content.char.protagonist-female.static-east','status':'unapproved, nonruntime, static-only','artApproved':False,'bodyRows':[8,103],'cell':[80,112],'pivot':[40,104],'scale':0.5,'logicalBodyHeight':48,'bounds':[int(xs.min()),8,int(xs.max()),103],'opaquePixels':int(op.sum()),'paletteSource':str(V8.relative_to(ROOT)).replace(chr(92),'/'),'paletteSourceSha256':sha(V8.read_bytes()),'source':str(Path(__file__).relative_to(ROOT)).replace(chr(92),'/'),'sourceSha256TextLf':sha(Path(__file__).read_bytes().replace(bytes([13,10]),bytes([10]))),'containerWriter':str(NORTH_TOOL.relative_to(ROOT)).replace(chr(92),'/'),'containerWriterSha256TextLf':sha(NORTH_TOOL.read_bytes().replace(bytes([13,10]),bytes([10]))),'layers':LAYERS+['guides'],'files':files,'proposals':['New east profile silhouette, visible ear/nose/chin and high ponytail arc.','Near side is character right: scarf tail visible. Character-left canister is far-side and partially occluded.','Relaxed near arm; no new equipment or animation.'],'authorship':'Code-authored coordinate clusters by Codex. East shapes were explicitly authored. No WEST/SOUTH PNG flipping or resampling; approved palette/reference read only.'}
 path=OUT/f'{PREFIX}_east-static-manifest_unapproved-v01_{STAMP}-{IDENT}.json';path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n');print(path);print('bounds',manifest['bounds'],'opaque',manifest['opaquePixels'],'palette',len({tuple(p) for p in arr[op]}));return manifest,blobs

if __name__=='__main__':build()
