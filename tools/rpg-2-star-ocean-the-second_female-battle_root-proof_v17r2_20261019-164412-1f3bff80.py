from pathlib import Path
import hashlib,io,json,zipfile,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
c=Path(__file__).resolve().parents[1];o=c/"outputs/battle-static-v17r2";checks=[];detail=[]
def ck(k,v):checks.append({"key":k,"pass":bool(v)})
def img(p):
 if isinstance(p,Path):p="\\\\?\\"+str(p.resolve())
 return Image.open(p).convert("RGBA")
m=json.loads(next(o.glob("*source-manifest*.json")).read_text(encoding="utf8"));png=o/m["files"]["png"]["name"];native=np.array(img(png));old=np.array(img(c/"outputs/battle-static-v17r1/rpg-2-star-ocean-the-second_female-battle-idle-right_dense-native136_unapproved-v17r1_20261018-224310-6e037d3b.png"))
ck("protected-head-rows0-44-exact",np.array_equal(native[:45],old[:45]));ck("protected-sole-rows132-143-exact",np.array_equal(native[132:],old[132:]));ck("declared-native-sha",hashlib.sha256(png.read_bytes()).hexdigest()==m["files"]["png"]["sha256"])
z=zipfile.ZipFile(o/m["files"]["pxo"]["name"]);d=json.loads(z.read("data.json"));baked=Image.new("RGBA",(136,144));ck("native-one-frame-25layers",len(d["frames"])==1 and len(d["layers"])==25)
oz=zipfile.ZipFile(o/m["files"]["ora"]["name"]);layers=ET.fromstring(oz.read("stack.xml")).find("stack").findall("layer");omap={l.attrib["name"]:l.attrib["src"] for l in layers}
for index,layer in enumerate(d["layers"],1):
 cel=Image.frombytes("RGBA",(136,144),z.read(f"image_data/frames/1/layer_{index}"));baked.alpha_composite(cel);ck("pxo-ora-role-"+layer["name"],cel.tobytes()==img(io.BytesIO(oz.read(omap[layer["name"]]))).tobytes())
ck("raw-cel-composite-exact",np.array_equal(np.array(baked),native));ck("ora-merged-exact",img(io.BytesIO(oz.read("mergedimage.png"))).tobytes()==baked.tobytes())
for directory in o.glob("root-*-v02-20261019-164412-1f3bff80"):
 report=json.loads(Path("\\\\?\\"+str(next(directory.glob("*report*.json")).resolve())).read_text(encoding="utf8"));ck(directory.name+"-current-arena",report["arenaSha256"]==hashlib.sha256((c/"game/scripts/battle_arena.gd").read_bytes()).hexdigest())
 for r in report["records"]:
  label=report["plate"]+"-"+r["language"];actual=np.array(img(directory/r["injected"]));x,y,w,h=r["candidatePhysicalRect"];crop=actual[y:y+h,x:x+w];op=native[:,:,3]==255;different=np.any(crop!=native,axis=2)&op
  a=np.array(img(directory/"diag-occl"/r["occluderDiagnostic"]["keyA"]));b=np.array(img(directory/"diag-occl"/r["occluderDiagnostic"]["keyB"]));matte=np.all(a==b,axis=2)[y:y+h,x:x+w];occ=a[y:y+h,x:x+w];fully_explained=matte&np.all(crop==occ,axis=2)
  face=np.zeros_like(op);face[22:44,72:95]=True;face&=op
  ck(label+"-face-exact-unoccluded",not np.any(different&face));ck(label+"-every-body-mismatch-is-exact-postdraw-occluder",not np.any(different&~fully_explained));ck(label+"-unchanged-normal-party",r["partyX"]==[135.,171.,207.,243.]);ck(label+"-no-diff-outside-hero",r["changedOutsideHeroBounds"]==0);ck(label+"-restored-normal-frame",r["occluderDiagnostic"]["restoredEqualsInjected"])
  detail.append({"scene":label,"exactFaceTexels":int(face.sum()),"bodyTexelsOccluded":int(different.sum()),"unexplainedBodyMismatches":int((different&~fully_explained).sum())})
failed=[x for x in checks if not x["pass"]];r={"passed":len(checks)-len(failed),"failed":len(failed),"failures":failed,"checks":checks,"actualRender":detail,"nativeSha256":m["files"]["png"]["sha256"],"artApproved":False,"motionApproved":False,"runtimeDefaultChanged":False};path=o/"rpg-2-star-ocean-the-second_female-battle_root-proof_v17r2_20261019-164412-1f3bff80.json";path.write_text(json.dumps(r,indent=2)+"\n",encoding="utf8");print(json.dumps({k:r[k] for k in ["passed","failed","failures","actualRender"]}));raise SystemExit(1 if failed else 0)
