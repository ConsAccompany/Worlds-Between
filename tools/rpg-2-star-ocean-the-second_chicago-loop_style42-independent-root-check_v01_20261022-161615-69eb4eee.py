"""Codex independent native raster-plane package check; no art/default/GUI acceptance."""
import argparse, hashlib, importlib.util, io, json, pathlib, zipfile
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

def read(p): return pathlib.Path('\\\\?\\'+str(p.resolve())).read_bytes()
def sha(p): return hashlib.sha256(read(p)).hexdigest()
def img(p): return Image.open(io.BytesIO(read(p))).convert('RGBA')
def equal(a,b): return a.size==b.size and a.tobytes()==b.tobytes()
def pixelsize(a): return a.size==(640,360)
def samealpha(a,b): return pixelsize(a) and pixelsize(b) and a.getchannel('A').tobytes()==b.getchannel('A').tobytes()
def contained(root,p):
 try:p.resolve().relative_to(root.resolve());return True
 except ValueError:return False

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--manifest',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();root=pathlib.Path(a.root).resolve();mp=root/a.manifest;out=root/a.out;out.mkdir(parents=True,exist_ok=True);m=json.loads(read(mp));checks=[]
 def ck(v,label):
  checks.append({'ok':bool(v),'label':label})
  if not v:raise AssertionError(label)
 def source(v):
  p=root/v;ck(contained(root,p),'scoped path '+v);return p
 files=m['files'];files=[dict(v,file=k) if 'file' not in v and 'path' not in v else v for k,v in files.items()] if isinstance(files,dict) else files;assets={}
 for v in files:
  p=source(v.get('file',v.get('path','')));expected=v.get('sha256',v.get('file_sha256'));ck(expected is not None,'file has hash '+p.name);got=sha(p)
  if v.get('hash_algorithm')=='sha256-text-lf-v1':got=hashlib.sha256(read(p).replace(b'\r\n',b'\n')).hexdigest()
  ck(got==expected,'exact hash '+p.name);assets[p.suffix+':'+p.name]=p
 pngs=[p for p in assets.values() if p.suffix=='.png']
 for p in pngs:ck(pixelsize(img(p)),'native640x360 '+p.name)
 ora=next(p for p in assets.values() if p.suffix=='.ora');pxo=next(p for p in assets.values() if p.suffix=='.pxo');layers={}
 with zipfile.ZipFile(io.BytesIO(read(ora))) as z:
  xml=ET.fromstring(z.read('stack.xml'));ck((int(xml.attrib['w']),int(xml.attrib['h']))==(640,360),'ORA native canvas')
  merged=Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA');composite=Image.new('RGBA',(640,360));entries=list(xml.iter('layer'))
  for e in reversed(entries):
   im=Image.open(io.BytesIO(z.read(e.attrib['src']))).convert('RGBA');ck(pixelsize(im),'ORA native plane '+e.attrib['name']);layers[e.attrib['name']]=im
   if e.attrib.get('visibility')!='hidden':composite=Image.alpha_composite(composite,im)
  ck(equal(composite,merged),'ORA actual plane composition equals merged preview')
 reference=source('outputs/style41/rpg-2-star-ocean-the-second_chicago-loop_science-style-alignment-reference_nonruntime-v01_20261022-161221-0e519466.png')
 ck(sha(reference)=='6cc3069cc15cb41f17c80c49073a9d841b1647c8eaafbfdf8e4a76d85c6d9f52','approved reference bytes')
 expected=img(reference).resize((640,360),Image.Resampling.NEAREST)
 ck(equal(expected,merged),'native flat equals exactly declared nearest sampling of style reference')
 with zipfile.ZipFile(io.BytesIO(read(pxo))) as z:
  j=json.loads(z.read('data.json'));ck((j['size_x'],j['size_y'])==(640,360) and j['pxo_version']==7,'PXO native format/canvas')
  names=[l['name'] for l in j['layers']];ck(set(names)==set(layers),'PXO/ORA same layer identities')
  for i,l in enumerate(j['layers'],1):ck(z.read('image_data/frames/1/layer_'+str(i))==layers[l['name']].tobytes(),'PXO raw cel exact '+l['name'])
  ck(equal(Image.open(io.BytesIO(z.read('preview.png'))).convert('RGBA'),merged),'PXO preview exact merged')
 base=root/'tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-author_unapproved-v05_20261017-234337-84862412.py';sp=importlib.util.spec_from_file_location('old',base);b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b);old,props=b.build_layers();rt=b.runtime_layers(old)
 for name in b.YSORT:
  p=next(p for p in pngs if '_'+name+'_' in p.name);new=img(p);ck(samealpha(new,rt[name]),'existing foreground alpha exact '+name)
  mask=np.array(new)[...,3]>0;ck(np.array_equal(np.array(new)[...,:3][mask],np.array(merged)[...,:3][mask]),'foreground material pixels equal flat '+name)
 for name,expected in [('occlusion-reveal-mask',b.reveal_mask_image(b.visibility_report(old,props)[1])),('guides-walkmask',b.walkmask())]:
  p=next(p for p in pngs if '_'+name+'_' in p.name);ck(equal(img(p),expected.convert('RGBA')),'original guide exact '+name)
 geometry={'walk':b.WALK,'blocks':b.BLOCKS,'spawn':b.SPAWN,'kiosk':b.KIOSK,'stair':b.STAIR,'pylon':b.PYLON,'interact_radius':b.INTERACT_RADIUS,'deck_rows':[b.DECK_TOP,b.DECK_BOTTOM],'station_plate':b.PLATE}
 ck(json.loads(json.dumps(geometry))==m['geometry'],'all original geometry constants exact');ck(json.loads(json.dumps(props))==m['ysort_props'],'all original prop regions and pivots exact')
 ground=img(next(p for p in pngs if '_ground-far_' in p.name));comp=ground
 for name in b.YSORT:comp=Image.alpha_composite(comp,img(next(p for p in pngs if '_'+name+'_' in p.name)))
 ck(equal(comp,merged),'six runtime plane composition exact new native flat')
 ck(not equal(expected,Image.new('RGBA',(639,360))),'wrong dimension refused')
 zero=Image.new('RGBA',(640,360));ck(not samealpha(zero,rt[b.YSORT[0]]),'wrong alpha refused')
 ck(sha(reference)!='0'*64,'wrong file hash refused')
 report={'passed':True,'checks':checks,'manifest':a.manifest,'sha256':sha(mp),'native':[640,360],'negativeFixtures':3,'limitations':['reference-derived raster planes, not manually authored pixel art','no GUI SaveAs/reopen claim','alpha equality proves old geometry only, not visual alignment of generated silhouettes','Codex must inspect actual gameplay occlusion']};(out/'rpg-2-star-ocean-the-second_chicago-loop_style42-root-source-result_v01_20261022-161615-69eb4eee.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode());print('STYLE42_ROOT_SOURCE_OK',len(checks))
if __name__=='__main__':main()
