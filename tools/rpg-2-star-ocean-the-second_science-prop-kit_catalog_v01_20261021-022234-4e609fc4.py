"""Build/check a reusable index of existing science-room props; never repaint, copy or approve art.
Usage: python -I <this> --out <unique.json> | --check <catalog.json>
"""
from pathlib import Path
import argparse,hashlib,json,os,io,zipfile
from datetime import datetime,timezone
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SOURCES=[
("nyc-public-facilities-room1","outputs/room1-fixtures-pilot/rpg-2-star-ocean-the-second_nyc-public-facilities-room1_three-pixel-fixtures-manifest_unapproved-v01_20261017-011700-b45e18a9.json"),
("nyc-public-facilities-room2","outputs/room2-fixtures-pilot/rpg-2-star-ocean-the-second_nyc-public-facilities-room2_three-pixel-fixtures-manifest_unapproved-v01_20261017-010000-7d3c8a91.json"),
("yonkers-maintenance-room2","outputs/yonkers-room2-fixtures-pilot/rpg-2-star-ocean-the-second_yonkers-maintenance-room2_four-pixel-fixtures-manifest_unapproved-v01_20261017-012500-a73e60b4.json")]
def resolve(rel):
 p=(ROOT/rel.replace("\\","/")).resolve()
 if not p.is_relative_to(ROOT):raise ValueError("source outside project")
 return p

def read(rel):
 p=resolve(rel)
 return Path("\\\\?\\"+str(p)).read_bytes() if os.name=="nt" else p.read_bytes()
def sha(b):return hashlib.sha256(b).hexdigest()
def record(rel):
 raw=read(rel);return {"file":rel.replace("\\","/"),"sha256":sha(raw),"bytes":len(raw)}
def build():
 items=[]
 for area,manifest in SOURCES:
  data=json.loads(read(manifest).decode("utf8"))
  for asset in data["assets"]:
   png=asset["png"].replace("\\","/");native=asset["ora"].replace("\\","/");runtime="game/assets/props/"+area+"/"+Path(png).name
   a,b=read(png),read(runtime)
   if a!=b:raise ValueError("source/runtime bytes differ: "+runtime)
   with Image.open(io.BytesIO(a)) as im:size=list(im.size);bounds=im.getchannel("A").getbbox()
   with zipfile.ZipFile(io.BytesIO(read(native))) as z:
    with Image.open(io.BytesIO(z.read("mergedimage.png"))) as merged:
     with Image.open(io.BytesIO(a)) as im:
      if merged.convert("RGBA").tobytes()!=im.convert("RGBA").tobytes():raise ValueError("native merged image differs")
   items.append({"id":area+"."+asset["purpose"],"purpose":asset["purpose"],"referenceRoom":area,"runtime":record(runtime),"sourcePng":record(png),"editableOra":record(native),"author":record(data["source"]),"sourceManifest":record(manifest),"canvas":size,"opaqueBounds":list(bounds) if bounds else None,"nativeLayers":asset["layers"],"referenceSceneOnly":True,"reuseInNewSceneApproved":False,"placementRule":"Reuse original survey_annex.gd Sprite2D offset/scale and authored blockers as reference; verify placement and occlusion in each new scene. No generic pivot inferred."})
 return items

def main():
 ap=argparse.ArgumentParser(description=__doc__);group=ap.add_mutually_exclusive_group(required=True);group.add_argument("--out");group.add_argument("--check");a=ap.parse_args();items=build()
 if a.check:
  saved=json.loads(read(a.check).decode("utf8"));assert saved["items"]==items;print("PROP_KIT_CHECK_PASS",len(items),"runtime/source/native/author hashes and merged exports; no art approval");return
 result={"schema":"worlds-between.science-prop-kit.catalog.v1","createdAt":datetime.now(timezone.utc).isoformat(),"purpose":"Reuse existing props by semantic purpose instead of redrawing; references existing files, no duplicated assets.","approvalScope":"Original scene acceptance does not approve reuse in a new scene or transfer standalone prop approval.","pixelRule":"640x360 logical scenes; preserve source pixels and original scale/offset; no automatic resizing, recolor or perspective conversion.","items":items};target=resolve(a.out);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8");print("PROP_KIT_CREATED",len(items),target.relative_to(ROOT))
if __name__=="__main__":main()
