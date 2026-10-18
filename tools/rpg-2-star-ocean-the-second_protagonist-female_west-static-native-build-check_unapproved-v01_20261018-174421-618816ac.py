"""One new west-profile static, not a transformed south image. Reuses only tracked native container writers/palette."""
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
import hashlib,io,json,os,subprocess,tempfile,zipfile,sys
from PIL import Image,ImageDraw
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
STAMP='20261018-174421'
IDENT='618816ac'
PREFIX='rpg-2-star-ocean-the-second_protagonist-female'
OUT=ROOT/'outputs/female-west-static-v01'
NORTH_TOOL=ROOT/'tools/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-build-and-check_unapproved-v01_20261018-090713-9af15df7.py'
spec=spec_from_file_location('female_native_container_reuse',NORTH_TOOL);base=module_from_spec(spec);spec.loader.exec_module(base)
V8=ROOT/base.v8t.V8_REL
LAYERS=['far-leg-boot','scarf-tail','backpack','coat','near-leg-boot','head-face','near-arm','canister','leather-straps','bedroll','hair','ponytail']
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
 # Far leg and boot: planted, toe points west. No attack/dodge pose or lifted heel.
 poly('far-leg-boot',[(39,68),(47,70),(47,89),(45,94),(38,93),(36,81)],'C')
 poly('far-leg-boot',[(41,73),(45,73),(45,88),(42,92),(39,90)],'E')
 line('far-leg-boot',[(44,77),(42,83),(43,88)],'O')
 poly('far-leg-boot',[(38,88),(47,89),(47,99),(45,103),(33,103),(32,100),(37,97)],'F')
 poly('far-leg-boot',[(39,90),(45,91),(44,99),(35,100),(35,102),(44,102),(45,98),(45,92)],'B')
 line('far-leg-boot',[(38,92),(45,93)],'J');box('far-leg-boot',(43,94,45,95),'b')
 # Far-side teal scarf tail is a narrow glimpse behind the coat, not a new cape.
 poly('scarf-tail',[(46,41),(50,43),(50,55),(55,68),(53,73),(49,68),(47,57)],'S')
 poly('scarf-tail',[(48,44),(49,48),(49,57),(53,68),(52,69),(48,60)],'M')
 # Side/back pack, warm leather flap and seams. Its canister remains on the character's left side.
 poly('backpack',[(44,39),(54,39),(58,45),(57,63),(53,67),(44,64),(41,49)],'F')
 poly('backpack',[(45,41),(52,41),(55,45),(55,59),(52,63),(44,61),(43,48)],'B')
 poly('backpack',[(45,42),(51,42),(54,46),(53,49),(45,48)],'L')
 line('backpack',[(54,46),(53,57),(51,61)],'H');line('backpack',[(45,42),(45,48),(51,48)],'K')
 box('backpack',(48,51,54,59),'H');line('backpack',[(49,52),(53,52),(53,57)],'L')
 box('backpack',(50,48,52,50),'b');box('backpack',(51,49,51,49),'U')
 # Storm-slate side coat. Front (west) opening shows a sliver of cream shirt; hem has a real profile/back vent.
 poly('coat',[(33,35),(43,35),(46,42),(45,57),(49,70),(47,75),(38,73),(35,70),(30,73),(27,68),(29,54),(27,43)],'C')
 poly('coat',[(33,37),(40,37),(43,43),(41,58),(45,70),(41,71),(36,67),(31,70),(30,65),(31,51),(29,44)],'D')
 line('coat',[(32,39),(30,44),(32,49),(32,61),(30,67)],'P')
 poly('coat',[(31,42),(34,44),(33,51),(30,55),(29,49)],'U')
 line('coat',[(32,42),(30,47),(30,53)],'X');line('coat',[(39,48),(38,56),(41,64),(43,69)],'C')
 line('coat',[(35,60),(36,64),(34,68)],'P');line('coat',[(43,61),(45,68),(46,72)],'b')
 line('coat',[(29,57),(42,60),(44,62)],'F');line('coat',[(30,58),(41,61)],'J')
 box('coat',(29,58,32,61),'b');box('coat',(30,59,31,60),'U')
 # Near trouser profile and boot, with a clear toe/heel at the shared floor row.
 poly('near-leg-boot',[(32,70),(41,72),(42,80),(39,91),(31,92),(29,84)],'C')
 poly('near-leg-boot',[(33,72),(39,74),(39,80),(36,89),(32,90),(31,84)],'E')
 line('near-leg-boot',[(33,76),(34,82),(32,87)],'O');line('near-leg-boot',[(39,79),(37,85),(37,90)],'C')
 poly('near-leg-boot',[(31,88),(40,89),(40,98),(42,100),(41,103),(25,103),(24,101),(27,98),(30,96)],'F')
 poly('near-leg-boot',[(32,90),(37,91),(37,98),(40,100),(39,101),(27,101),(28,99),(32,97)],'B')
 line('near-leg-boot',[(31,91),(38,92)],'K');line('near-leg-boot',[(32,94),(37,95)],'J')
 box('near-leg-boot',(34,94,36,95),'b');line('near-leg-boot',[(28,100),(31,99),(35,100)],'L')
 # True west-facing profile: one visible eye, forehead/nose/chin protrusions, ear behind the eye.
 poly('head-face',[(31,18),(39,18),(43,22),(42,31),(37,35),(35,39),(30,37),(30,34),(26,33),(26,30),(24,29),(25,27),(28,26),(28,22)],'B')
 poly('head-face',[(31,20),(38,20),(40,23),(39,30),(35,34),(31,33),(28,32),(28,29),(26,29),(29,27),(29,23)],'T')
 poly('head-face',[(31,21),(36,21),(36,25),(33,29),(28,29),(29,27),(30,23)],'R')
 box('head-face',(28,25,30,25),'Q');box('head-face',(28,24,30,24),'B');box('head-face',(29,25,29,25),'X');box('head-face',(28,25,28,25),'A')
 line('head-face',[(27,31),(29,31)],'B');box('head-face',(26,28,26,28),'R')
 poly('head-face',[(37,25),(40,25),(40,29),(38,30),(36,28)],'T');line('head-face',[(38,26),(39,27),(38,28)],'V')
 # Teal neck wrap and rolled sleeve, exposed forearm and fingerless glove.
 poly('near-arm',[(30,35),(35,37),(40,35),(43,38),(41,42),(33,44),(29,41),(27,38)],'S')
 poly('near-arm',[(29,36),(34,38),(39,37),(39,40),(33,42),(29,40)],'M');line('near-arm',[(29,36),(33,38),(37,38)],'G')
 poly('near-arm',[(35,42),(40,44),(40,49),(37,55),(29,56),(27,52),(28,45),(30,42)],'C')
 poly('near-arm',[(31,43),(35,43),(37,47),(35,52),(30,53),(29,50),(30,46)],'D');line('near-arm',[(30,44),(29,49),(31,52)],'P')
 poly('near-arm',[(29,52),(37,53),(36,57),(29,57),(27,55)],'I');line('near-arm',[(29,53),(35,54)],'X');line('near-arm',[(29,56),(35,56)],'N')
 poly('near-arm',[(29,57),(35,57),(34,63),(33,66),(28,65),(27,62)],'V');poly('near-arm',[(29,57),(32,58),(31,63),(28,63)],'T')
 poly('near-arm',[(28,63),(33,64),(34,68),(31,70),(27,69),(26,66)],'F');line('near-arm',[(28,64),(31,65),(32,67)],'H');box('near-arm',(29,68,30,69),'T')
 # Metal canister is near side; no new gear beyond the v8/sheet equipment.
 poly('canister',[(50,57),(54,57),(56,60),(56,71),(54,74),(49,72),(48,61)],'Z')
 poly('canister',[(50,59),(53,59),(54,61),(54,71),(52,72),(50,70)],'b');line('canister',[(50,61),(50,69)],'e');line('canister',[(52,61),(52,70)],'U')
 box('canister',(49,61,55,62),'S');box('canister',(50,61,54,61),'G');box('canister',(51,57,53,58),'b')
 # Near shoulder strap follows the side-facing chest contour.
 line('leather-straps',[(42,39),(39,42),(38,50),(39,58)],'F',3);line('leather-straps',[(42,39),(40,43),(39,48)],'J')
 box('leather-straps',(38,45,40,48),'b');box('leather-straps',(39,46,39,47),'U')
 # Bedroll end cap, foreshortened circular section (not a copied horizontal south roll).
 poly('bedroll',[(47,31),(52,31),(56,34),(56,40),(53,44),(47,44),(44,41),(44,35)],'S')
 poly('bedroll',[(47,32),(51,32),(54,35),(54,39),(52,42),(48,42),(46,39),(46,35)],'M')
 line('bedroll',[(48,33),(51,33),(53,35),(53,39),(51,41),(48,40),(47,37),(49,35),(51,36),(51,38),(49,38)],'G')
 line('bedroll',[(46,34),(45,37),(46,40)],'c');line('bedroll',[(44,35),(43,39),(45,42)],'F')
 # Hair is authored as side locks/fringe with the visible ear opening. Coherent clusters, no dithering/noise.
 poly('hair',[(30,16),(35,14),(41,15),(45,19),(45,27),(43,33),(39,34),(38,31),(40,27),(39,23),(36,21),(34,23),(32,23),(32,20),(29,21),(27,24),(26,22),(27,18)],'A')
 poly('hair',[(30,17),(35,16),(40,17),(43,20),(43,26),(41,30),(40,28),(41,23),(38,20),(34,19),(31,20),(28,22),(28,19)],'F')
 poly('hair',[(31,17),(35,16),(39,17),(40,19),(35,18),(31,19),(29,21)],'B')
 line('hair',[(32,17),(35,17),(38,18)],'L');line('hair',[(42,20),(43,23),(42,27)],'H')
 line('hair',[(33,20),(31,22),(30,24)],'Q');line('hair',[(43,29),(42,33),(44,35)],'A');line('hair',[(41,29),(40,32)],'B')
 # High ponytail on crown; real side arc and free hanging strands, not an affine front transformation.
 poly('ponytail',[(40,15),(41,11),(44,8),(48,8),(52,11),(55,15),(56,20),(54,25),(55,29),(53,34),(51,34),(52,28),(51,24),(53,19),(51,15),(47,13),(44,14),(43,17)],'A')
 poly('ponytail',[(42,13),(45,10),(48,10),(51,12),(53,16),(54,20),(52,24),(53,28),(52,31),(52,25),(51,23),(52,19),(49,15),(46,13),(43,15)],'F')
 line('ponytail',[(44,11),(47,10),(50,12),(52,15)],'L');line('ponytail',[(44,12),(47,11),(50,14)],'K');line('ponytail',[(54,17),(54,20),(52,24)],'B');line('ponytail',[(53,26),(54,30),(52,34)],'H')
 box('ponytail',(41,14,43,15),'J')
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
 # Reuse format code, but never retain north-facing export metadata in the west document.
 old=zipfile.ZipFile(io.BytesIO(pxo));buf=io.BytesIO()
 with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
  for item in old.infolist():
   payload=old.read(item.filename)
   if item.filename=='data.json':
    d=json.loads(payload);d['export_profile']['file_name']=json.dumps('protagonist-female-west-static-v01');d['user_data']=d['user_data'].replace('north pilot','west pilot');payload=json.dumps(d,separators=(',',':')).encode()
   z.writestr(item,payload)
 OUT.mkdir(parents=True,exist_ok=True);files={}
 for role,ext,data in [('static','png',png),('layered-source','pxo',buf.getvalue()),('layered-source','ora',ora)]:
  name=f'{PREFIX}_west-{role}_unapproved-v01_{STAMP}-{IDENT}.{ext}';(OUT/name).write_bytes(data);files[ext]={'file':str((OUT/name).relative_to(ROOT)).replace(chr(92),'/'),'sha256':sha(data)}
 manifest={'task':'content.char.protagonist-female.static-west','status':'unapproved, nonruntime, static-only','artApproved':False,'bodyRows':[8,103],'cell':[80,112],'pivot':[40,104],'scale':0.5,'logicalBodyHeight':48,'bounds':[int(xs.min()),8,int(xs.max()),103],'opaquePixels':int(op.sum()),'paletteSource':str(V8.relative_to(ROOT)).replace(chr(92),'/'),'paletteSourceSha256':sha(V8.read_bytes()),'source':str(Path(__file__).relative_to(ROOT)).replace(chr(92),'/'),'sourceSha256TextLf':sha(Path(__file__).read_bytes().replace(bytes([13,10]),bytes([10]))),'containerWriter':str(NORTH_TOOL.relative_to(ROOT)).replace(chr(92),'/'),'containerWriterSha256TextLf':sha(NORTH_TOOL.read_bytes().replace(bytes([13,10]),bytes([10]))),'layers':LAYERS+['guides'],'files':files,'proposals':['New west profile silhouette, visible ear/nose/chin and high ponytail arc.','Near side is character left: canister visible. Far-side scarf tail only glimpsed.','Relaxed near arm; no new equipment or animation.'],'authorship':'Code-authored coordinate clusters by Codex. South pixels were never sampled, mirrored, sheared or resampled; palette/reference read only.'}
 path=OUT/f'{PREFIX}_west-static-manifest_unapproved-v01_{STAMP}-{IDENT}.json';path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n');print(path);print('bounds',manifest['bounds'],'opaque',manifest['opaquePixels'],'palette',len({tuple(p) for p in arr[op]}));return manifest,blobs

if __name__=='__main__':build()
