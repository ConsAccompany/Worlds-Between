"""Five whole-head ROI icons: explicit nearest-neighbor downsample of existing AI concept display crops.
No repaint, new generation or identity invention. Original full display/portrait bytes and dialogue layout unchanged.
The archived original kit provides only immutable source/provenance; rejected eye-only assets are never regenerated.
"""
from pathlib import Path
import argparse,hashlib,json,io,zipfile,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SLUG="rpg-2-star-ocean-the-second"
TAG='20261020-001030-9be4a34f'
TEMPLATE='outputs/ui-root-v02/rpg-2-star-ocean-the-second_character-ui-portraits_original-kit-frozen_v01_20261020-001030-9be4a34f.json'
TEMPLATE_SHA='324a90c4a4639dea5661d55d9c3f2345e7573ad4522e8882f1dc176a634a5542'
ROIS={"protagonist-female":(8,12,224,228),"protagonist-male":(17,5,222,210),"liang-xu":(31,4,290,263),"zhao-ling":(40,0,320,280),"ji-cheng":(29,4,329,304)}
TRANSFORM="whole-head-roi-nearest-neighbor-downscale-to-28x28"
def read(p):return Path("\\\\?\\"+str(p.resolve())).read_bytes()
def write(p,b):p.parent.mkdir(parents=True,exist_ok=True);Path("\\\\?\\"+str(p.resolve())).write_bytes(b)
def sha(b):return hashlib.sha256(b).hexdigest()
def encode(image):
 b=io.BytesIO();image.save(b,format="PNG",compress_level=9);return b.getvalue()
def ora(png):
 b=io.BytesIO()
 with zipfile.ZipFile(b,"w") as z:
  for name,data in [("mimetype",b"image/openraster"),("stack.xml",b'<image version="0.0.3" w="28" h="28"><stack><layer name="whole-head-nearest-downsample" src="data/layer1.png" x="0" y="0" opacity="1.0" visibility="visible" composite-op="svg:src-over"/></stack></image>'),("data/layer1.png",png),("mergedimage.png",png),("Thumbnails/thumbnail.png",png)]:
   i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_STORED;z.writestr(i,data)
 return b.getvalue()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output");args=ap.parse_args();out=Path(args.output) if args.output else ROOT/"game/assets/portraits/ui-kit-v02"
 source=read(ROOT/TEMPLATE);assert sha(source)==TEMPLATE_SHA;kit=json.loads(source)
 kit["run"]={"timestamp_compact_utc":TAG[:15],"unique_id":TAG[16:],"id":TAG};kit["kit_id"]=SLUG+"_character-ui-kit_manifest_v02_"+TAG
 kit["provenance"]["approval_note"]="Original concept sheets remain AI-generated and unapproved. Whole-head square ROIs are explicitly nearest-neighbor downsampled to28x28; no synthesis/repaint/new identity. Dialogue uses unchanged full display crops; no art/canon/full-sprite approval."
 kit["outputs"]=[];kit["verification"]={"builder":"tools/"+Path(__file__).name,"builder_raw_sha256":sha(read(Path(__file__))),"historical_template":TEMPLATE,"historical_template_sha256":TEMPLATE_SHA,"icon_transform":TRANSFORM,"nearest_center_rule":"floor((2*target_index+1)*source_size/56)","same_runtime_determinism_only":True,"cross_runtime_compression_equality_claimed":False}
 for subject,roi in ROIS.items():
  v=kit["variants"][subject];raw=read(ROOT/v["display_crop"]);assert sha(raw)==v["display_crop_sha256"];im=Image.open(io.BytesIO(raw)).convert("RGBA");l,t,r,b=roi;assert 0<=l<r<=im.width and 0<=t<b<=im.height and r-l==b-t and r-l>28
  cropped=im.crop(roi);icon=Image.new("RGBA",(28,28))
  for yy in range(28):
   for xx in range(28):icon.putpixel((xx,yy),cropped.getpixel((((2*xx+1)*(r-l))//56,((2*yy+1)*(b-t))//56)))
  png=encode(icon);archive=ora(png);uid=sha((TAG+subject).encode())[:8];stem=SLUG+"_"+subject+"_whole-head-party-icon_v02_"+TAG[:15]+"-"+uid
  names={"png":stem+".png","ora":stem.replace("_whole-head-party-icon_","_whole-head-party-icon-editable_")+".ora","manifest":stem.replace("_whole-head-party-icon_","_whole-head-party-icon-manifest_")+".json"}
  rect={"left":l,"top":t,"right":r,"bottom":b,"width":r-l,"height":b-t}
  manifest={"schema":"worlds-between.ui-whole-head-icon.v2","subject":subject,"source":{"path":v["display_crop"],"sha256":sha(raw),"width":im.width,"height":im.height,"original_ai_generated":True},"source_roi":rect,"transform":{"method":TRANSFORM,"resampled":True,"target_width":28,"target_height":28,"repainted":False,"new_generation":False},"png":{"path":names["png"],"sha256":sha(png)},"ora":{"path":names["ora"],"sha256":sha(archive),"layers":1},"approval":"none","builder":kit["verification"]}
  mb=(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n").encode();assets={names["png"]:png,names["ora"]:archive,names["manifest"]:mb};cs="".join(sha(bb)+"  "+nn+"\n" for nn,bb in assets.items()).encode();assets[stem.replace("_whole-head-party-icon_","_whole-head-party-icon-checksums_")+".sha256"]=cs
  for nn,bb in assets.items():
   assert not (out/nn).exists();write(out/nn,bb)
  root="res://assets/portraits/ui-kit-v02/";v["party_icon"].update({"png":root+names["png"],"png_file":names["png"],"png_repo_path":"game/assets/portraits/ui-kit-v02/"+names["png"],"png_sha256":sha(png),"ora":root+names["ora"],"ora_sha256":sha(archive),"roi":rect,"transform":TRANSFORM,"resampled":True});v["party_icon"]["frame"]["placement"]="runtime decoration around a28x28 whole-head nearest downsample"
  kit["outputs"].append({"subject":subject,"icon":names["png"],"icon_sha256":sha(png),"ora":names["ora"],"ora_sha256":sha(archive),"manifest":names["manifest"],"manifest_sha256":sha(mb),"source_display_crop":v["display_crop"],"source_display_crop_sha256":sha(raw),"roi":rect,"transform":TRANSFORM})
 name=SLUG+"_character-ui-kit_manifest_v02_"+TAG+".json";write(out/name,(json.dumps(kit,ensure_ascii=False,indent=2)+"\n").encode());print("WHOLE_HEAD_KIT_BUILT",str(out/name))
if __name__=="__main__":main()
