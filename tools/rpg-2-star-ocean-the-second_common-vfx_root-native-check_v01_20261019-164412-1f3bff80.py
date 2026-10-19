from pathlib import Path
import hashlib, io, json, subprocess, sys, zipfile, xml.etree.ElementTree as ET
from PIL import Image
c=Path(__file__).resolve().parents[1]
p=c/"game/assets/vfx/common-v01"
mf=next(p.glob("*manifest*.json"));m=json.loads(mf.read_text(encoding="utf8"));checks=[]
def ck(k,v):checks.append({"key":k,"pass":bool(v)})
for kind,e in m["events"].items():
 z=zipfile.ZipFile(p/e["pxo"]);d=json.loads(z.read("data.json"));ck(kind+"-64x64",(d["size_x"],d["size_y"])==(64,64));ck(kind+"-8-native-cels",len(d["frames"])==8);ck(kind+"-native-total",abs(sum(f["duration"] for f in d["frames"])/d["fps"]-e["durationSeconds"])<1e-12)
 for i,fn in enumerate(e["frames"]):
  baked=Image.new("RGBA",(64,64))
  for j,l in enumerate(d["layers"]):baked.alpha_composite(Image.frombytes("RGBA",(64,64),z.read(f"image_data/frames/{i+1}/layer_{j+1}")))
  png=Image.open(p/fn).convert("RGBA");ck(kind+f"-cel-{i}-exact",baked.tobytes()==png.tobytes());ck(kind+f"-cel-{i}-alpha-cap",png.getchannel("A").getextrema()[1]<=166);ck(kind+f"-cel-{i}-nonempty",png.getbbox() is not None)
 oz=zipfile.ZipFile(p/e["ora"]);stack=ET.fromstring(oz.read("stack.xml"));baked=Image.new("RGBA",(64,64))
 for layer in reversed(stack.find("stack").findall("layer")):baked.alpha_composite(Image.open(io.BytesIO(oz.read(layer.attrib["src"]))).convert("RGBA"))
 ck(kind+"-ora-middle-exact",baked.tobytes()==Image.open(p/e["frames"][e["oraFrame"]]).convert("RGBA").tobytes())
for fn,h in m["sha256"].items():ck("hash-"+fn,hashlib.sha256((p/fn).read_bytes()).hexdigest()==h)
for field in ["source","helper"]:ck(field+"-raw-hash",hashlib.sha256((p/m[field]["path"]).resolve().read_bytes()).hexdigest()==m[field]["sha256"])
rebuilt=p.with_name("common-v01-root-rebuild")
proc=subprocess.run([sys.executable,str((p/m["source"]["path"]).resolve()),"--out-dir",str(rebuilt)],capture_output=True,text=True,encoding="utf8",timeout=45)
ck("independent-rebuild-exit",proc.returncode==0)
ck("independent-rebuild-file-set",sorted(x.name for x in p.iterdir() if x.is_file())==sorted(x.name for x in rebuilt.iterdir() if x.is_file()))
for source in p.iterdir():
 if source.is_file():ck("rebuilt-exact-"+source.name,(rebuilt/source.name).exists() and source.read_bytes()==(rebuilt/source.name).read_bytes())
failed=[x for x in checks if not x["pass"]];r={"passed":len(checks)-len(failed),"failed":len(failed),"failures":failed,"checks":checks,"sourceHashNormalization":"raw bytes","manifest":str(mf.relative_to(c)),"nativeApplicationClean":False,"guiSaveAsVerified":False,"artApproved":False}
out=c/"outputs/common-vfx-v01/rpg-2-star-ocean-the-second_common-vfx_root-native-report_v01_20261019-164412-1f3bff80.json";out.write_text(json.dumps(r,indent=2)+"\n",encoding="utf8");print(json.dumps({k:r[k] for k in ["passed","failed","failures"]}));raise SystemExit(1 if failed else 0)
