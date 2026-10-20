"""Independent whole-head nearest sample, source/ORA/hash/rebuild oracle. No producer assertion is trusted."""
from pathlib import Path
import hashlib,json,io,zipfile,subprocess,sys,uuid,datetime
from xml.etree import ElementTree as ET
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parents[1];P=next(x for x in D.parents if (x/"work/tooling/godot-4-7-2").is_dir());C=P/"work/max0840-sentry-sync";A=D/"game/assets/portraits/ui-kit-v02";O=D/"outputs/ui-root-v02";checks=[]
def rb(p):return Path("\\\\?\\"+str(p.resolve())).read_bytes()
def sha(b):return hashlib.sha256(b).hexdigest()
def ck(name,value):checks.append({"key":name,"pass":bool(value)});assert value,name
assert not (P/"work/dual01/control/rpg-2-star-ocean-the-second_dual-provider_global-stop_v01_20261019-001423-861097ca.json").exists()
k=json.loads(rb(next(A.glob("*character-ui-kit*.json"))));rois={"protagonist-female":(8,12,224,228),"protagonist-male":(17,5,222,210),"liang-xu":(31,4,290,263),"zhao-ling":(40,0,320,280),"ji-cheng":(29,4,329,304)};ck("exact-five-subjects",set(k["variants"])==set(rois));pixel_count=0
for subject,(l,t,r,b) in rois.items():
 v=k["variants"][subject];source=rb(D/v["display_crop"]);ck(subject+"-committed-source-exact",source==rb(C/v["display_crop"]) and sha(source)==v["display_crop_sha256"])
 im=np.array(Image.open(io.BytesIO(source)).convert("RGBA"));roi=im[t:b,l:r];indices=(((2*np.arange(28)+1)*(r-l))//56).astype(int);expected=roi[indices[:,None],indices[None,:]]
 entry=v["party_icon"];png=rb(D/"game"/entry["png"][6:]);actual=np.array(Image.open(io.BytesIO(png)).convert("RGBA"));ck(subject+"-28-square",actual.shape==(28,28,4));ck(subject+"-independent-nearest-pixels",np.array_equal(actual,expected));pixel_count+=28*28
 ck(subject+"-source-square-roi",entry["roi"]=={"left":l,"top":t,"right":r,"bottom":b,"width":r-l,"height":b-t});ck(subject+"-truthful-resample",entry["resampled"] is True and entry["transform"]=="whole-head-roi-nearest-neighbor-downscale-to-28x28");ck(subject+"-png-hash",sha(png)==entry["png_sha256"])
 archive=rb(D/"game"/entry["ora"][6:]);ck(subject+"-ora-hash",sha(archive)==entry["ora_sha256"])
 with zipfile.ZipFile(io.BytesIO(archive)) as z:
  ck(subject+"-ora-mime",z.namelist()[0]=="mimetype" and z.read("mimetype")==b"image/openraster");xml=ET.fromstring(z.read("stack.xml"));layers=list(xml.iter("layer"));ck(subject+"-ora-one-layer",len(layers)==1 and xml.get("w")=="28" and xml.get("h")=="28");ck(subject+"-ora-exact-native-png",z.read(layers[0].get("src"))==png and z.read("mergedimage.png")==png)
 ck(subject+"-dialogue-original-bytes",rb(D/"game"/v["dialogue"]["png"][6:])==source);m=next(x for x in k["outputs"] if x["subject"]==subject);manifest_bytes=rb(A/m["manifest"]);ck(subject+"-manifest-hash",sha(manifest_bytes)==m["manifest_sha256"]);mf=json.loads(manifest_bytes);ck(subject+"-no-synthesis-or-approval",mf["approval"]=="none" and mf["source"]["original_ai_generated"] is True and mf["transform"]["resampled"] is True and mf["transform"]["new_generation"] is False)
ck("truthful-global-provenance",k["provenance"]["original_source_ai_generated"] is True and k["provenance"]["new_generative_processing"] is False and k["provenance"]["approval"]=="none")
for subject in rois:
 path=k["variants"][subject]["dialogue"]["source_manifest"];ck(subject+"-source-manifest-unchanged",rb(D/path)==rb(C/path))
builder=D/k["verification"]["builder"];ck("builder-raw-hash",sha(rb(builder))==k["verification"]["builder_raw_sha256"]);temp=D/"work"/("whole-head-independent-rebuild-"+uuid.uuid4().hex[:8]);run=subprocess.run([sys.executable,str(builder),"--output",str(temp)],capture_output=True,text=True,encoding="utf-8",timeout=30);ck("rebuild-exit-clean",run.returncode==0 and not run.stderr);ck("rebuild-file-set",{f.name for f in temp.iterdir()}=={f.name for f in A.iterdir() if f.suffix in [".png",".ora",".json",".sha256"]})
for f in temp.iterdir():ck("deterministic-same-runtime-"+f.name,rb(f)==rb(A/f.name))
for f in A.glob("*.sha256"):
 for line in rb(f).decode().splitlines():
  digest,name=line.split("  ",1);ck("checksum-"+name,sha(rb(A/name))==digest)
tag=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")+"-"+uuid.uuid4().hex[:8];report={"passed":all(x["pass"] for x in checks),"checks":checks,"count":len(checks),"independentRgbaPixels":pixel_count,"sameRuntimeDeterminism":True,"crossRuntimeCompressedEqualityClaimed":False,"artApproved":False,"builderRun":run.stdout};out=O/("rpg-2-star-ocean-the-second_character-ui-portraits_root-package-oracle-proof_v02_"+tag+".json");out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8");print(json.dumps({"passed":report["passed"],"checks":len(checks),"pixels":pixel_count,"report":str(out)}))
