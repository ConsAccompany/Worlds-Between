"""Independently compose source PXO/ORA role layers; compare exported PNG and runtime atlas.

No imports from the procedural author; no file changes except the requested proof.
This checks source/editability correspondence, not artistic quality or fluidity.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
def lp(p):
    p = Path(p).resolve()
    return Path(chr(92)*2+'?'+chr(92)+str(p)) if os.name == 'nt' else p
def digest(b):
    return hashlib.sha256(b).hexdigest()
def same(a, b):
    return a.size == b.size and ImageChops.difference(a, b).getbbox() is None and a.tobytes() == b.tobytes()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    path = (ROOT / args.manifest).resolve()
    raw = lp(path).read_bytes()
    data = json.loads(raw)
    checks, hashes = [], {}
    def ck(ok, label):
        checks.append({'check':label, 'passed':bool(ok)})
    def read(entry):
        p = ROOT / entry['path'] if 'path' in entry else path.parent / entry['name']
        b = lp(p).read_bytes()
        hashes[p.relative_to(ROOT).as_posix()] = digest(b)
        ck(digest(b) == entry['sha256'], 'raw hash '+p.name)
        return b
    files = data['files']
    for key, entry in files.items():
        if not key.endswith('.pxo'):
            continue
        stem = key[:-4]
        expected = Image.open(io.BytesIO(read(files[stem+'.png']))).convert('RGBA')
        ck(expected.size == (136,144), 'source cell '+stem)
        bb = expected.getbbox()
        ck(bb and bb[0]>0 and bb[1]>0 and bb[2]<136 and bb[3]<=136, 'unclipped source '+stem)
        with zipfile.ZipFile(io.BytesIO(read(entry))) as z:
            d = json.loads(z.read('data.json'))
            size = (d['size_x'],d['size_y'])
            ck(size == expected.size and len(d['frames'])==1, 'native geometry '+stem)
            ck(len(d['layers'])>=2, 'editable native role layers '+stem)
            flat = Image.new('RGBA', size)
            for i, layer in enumerate(d['layers']):
                ck(layer.get('opacity',1)==1 and layer.get('blend_mode',0)==0, 'normal native opacity '+stem+'/'+str(i))
                ck(d['frames'][0]['cels'][i].get('opacity',1)==1,'native cel opacity '+stem+'/'+str(i))
                if layer.get('visible',True):
                    flat.alpha_composite(Image.frombytes('RGBA',size,z.read('image_data/frames/1/layer_'+str(i+1))))
            ck(same(flat,expected),'raw PXO composition exact '+stem)
        with zipfile.ZipFile(io.BytesIO(read(files[stem+'.ora']))) as z:
            xml = ET.fromstring(z.read('stack.xml'))
            layers = xml.find('stack').findall('layer')
            ck(len(layers)>=2,'editable ORA role layers '+stem)
            flat = Image.new('RGBA',expected.size)
            for layer in reversed(layers):
                if layer.get('visibility','visible')!='visible':
                    continue
                ck(float(layer.get('opacity','1'))==1,'normal ORA opacity '+stem)
                tile = Image.open(io.BytesIO(z.read(layer.attrib['src']))).convert('RGBA')
                flat.alpha_composite(tile,(int(layer.get('x','0')),int(layer.get('y','0'))))
            ck(same(flat,expected),'ORA composition exact '+stem)
            ck(same(Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA'),expected),'ORA merged exact '+stem)
    ck(any(k.endswith('.pxo') for k in files),'nonempty native package')
    if 'sheet' in files:
        sheet = Image.open(io.BytesIO(read(files['sheet']))).convert('RGBA')
        ck(sheet.width % 136 == 0 and sheet.height % 144 == 0,'atlas cell geometry')
        cols = sheet.width // 136
        for name, pose in data['poses'].items():
            cell = pose.get('runtimeCell')
            if cell is None:
                continue
            ck(type(cell) is int and 0 <= cell < cols*(sheet.height//144),'atlas index '+name)
            x,y=(cell%cols)*136,(cell//cols)*144
            expected=Image.open(io.BytesIO(read(files[name+'.png']))).convert('RGBA')
            ck(same(sheet.crop((x,y,x+136,y+144)),expected),'source to atlas exact '+name)
    report={'scope':'independent source composition; not art/motion/default approval','manifest':path.relative_to(ROOT).as_posix(),'manifestSha256Raw':digest(raw),'checkerSha256Raw':digest(lp(__file__).read_bytes()),'files':hashes,'checks':checks,'passed':all(c['passed'] for c in checks)}
    out=ROOT/args.out
    lp(out.parent).mkdir(parents=True,exist_ok=True)
    lp(out).write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps({'passed':report['passed'],'checks':len(checks),'failed':[c['check'] for c in checks if not c['passed']]}))
    return 0 if report['passed'] else 1
if __name__=='__main__':
    raise SystemExit(main())
