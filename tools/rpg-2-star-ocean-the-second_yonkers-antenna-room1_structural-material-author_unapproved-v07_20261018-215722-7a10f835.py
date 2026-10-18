"""Bounded v07: structural bays + shared service surface + aged contacts, using the committed v06 native layers.

No game/default/ledger writes. Reuses the native ORA/PXO packers, not the prior multi-version procedural author chain.
"""
import importlib.util
import io
import json
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
STAMP='20261018-220210-4d281c37'
OUT=ROOT/'outputs/yk1-v07_7a10f835'
PREFIX='rpg-2-star-ocean-the-second_yonkers-antenna-room1'
BASE=ROOT/'outputs/yonkers-room1-v06_c8f0d900'
BASE_MANIFEST=BASE/f'{PREFIX}_readability-manifest_unapproved-v06_20261018-084726-c8f0d900.json'


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


A=load('yonkers_native_formats',ROOT/'tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-scene-author_unapproved-v03_20261017-224447-15709be4.py')
KIT_PATH=ROOT/'tools/rpg-2-star-ocean-the-second_science-utility_native-material-kit_v01_20261018-215722-7a10f835.py'
K=load('science_utility_material_kit',KIT_PATH)
M=json.loads(BASE_MANIFEST.read_text(encoding='utf-8'))
for key,value in M['palette'].items():
    rgb=tuple(int(value[i:i+2],16) for i in (1,3,5))
    A.HEX[key]=value;A.RGB[key]=rgb;A.RGBA[key]=np.array((*rgb,255),np.uint8);A.NAME_OF[rgb]=key


def base_layers():
    path=ROOT/M['editable_sources']['ora']['file']
    with zipfile.ZipFile(path) as archive:
        xml=ET.fromstring(archive.read('stack.xml'))
        by_name={node.attrib['name']:np.array(Image.open(io.BytesIO(archive.read(node.attrib['src']))).convert('RGBA')) for node in xml.findall('.//layer')}
    result=[]
    for name in A.SCENE_LAYERS:
        layer=A.Layer();layer.a=by_name[name].copy();result.append(layer)
    return result


def build():
    old=base_layers();layers=base_layers()
    for x0,x1,courses,arch in [(111,240,[(42,85),(27,73),(51,96)],False),(264,397,[(45,91),(32,78),(57,101)],True),(421,555,[(49,95),(25,75),(43,103)],False)]:
        K.recessed_bay(layers[1],x0,x1,courses,arch)
    K.maintenance_path(layers[3])
    # Remove only the faded front safety-paint row, whose three isolated segments implied separate pads.
    for x0,x1 in [(121,194),(287,361),(429,541)]:
        for x in range(x0,x1+1):
            if tuple(layers[5].a[213,x,:3]) in (A.RGB['dk_hi'],A.RGB['dk_rust']):layers[5].a[213,x]=0
    for index,rect in [(9,(141,192,189,209)),(10,(292,192,348,209)),(11,(461,194,493,209))]:
        K.aged_base(layers[index],M['palette'],*rect)
    for x0,x1 in [(141,189),(292,348),(461,493)]:K.contact_cluster(layers[6],x0,x1)
    # Protected physical/occlusion geometry and its independently authored v06 masks are never changed.
    for index in [0,2,4,7,8,12]:assert np.array_equal(layers[index].a,old[index].a),A.SCENE_LAYERS[index]
    for index in [9,10,11,12]:assert np.array_equal(layers[index].a[...,3],old[index].a[...,3]),'alpha '+A.SCENE_LAYERS[index]
    for layer in layers:assert set(np.unique(layer.a[...,3]))<={0,255}
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'exp').mkdir(exist_ok=True)
    plate=A.composite(layers[:9]);flat=A.composite(layers)
    assert (plate[...,3]==255).all()
    images=[A.to_img(layer.a) for layer in layers]
    files={}
    def save(purpose,data,ext='png',folder=OUT):
        path=folder/f'{PREFIX}_{purpose}_unapproved-v07_{STAMP}.{ext}';path.write_bytes(data)
        info={'file':A.rel(path),'sha256':A.sha(data),'hash_algorithm':'sha256-bytes'};files[purpose]=info;return info
    src=save('structural-material-layers',A.ora_bytes('yonkers-v07',A.SCENE_LAYERS,images,A.to_img(flat)),'ora')
    pxo=save('structural-material-editable',A.pxo_bytes('yonkers-v07',A.SCENE_LAYERS,images,A.to_img(flat)),'pxo')
    flat_info=save('structural-material-native-flat',A.png_bytes(A.to_img(flat)))
    plate_info=save('corridor-plate-structural',A.png_bytes(A.to_img(plate)),folder=OUT/'exp')
    fg_info=save('foreground-occluder',A.png_bytes(images[12]),folder=OUT/'exp')
    antennas=[]
    for index,slug in enumerate(A.ANTENNA_SLUGS):
        x0,y0,x1,y1=A.sprite_box(index)
        info=save(slug,A.png_bytes(A.to_img(np.ascontiguousarray(layers[index+9].a[y0:y1,x0:x1]))),folder=OUT/'exp')
        antennas.append({'clue':f'scifi.outskirts:{index}','anchor':[A.ANTENNA_X[index],A.BASE_Y],'crop_from_layer_xywh':[x0,y0,A.SPRITE_W,A.SPRITE_H],'runtime_png':info})
    manifest={'project':'rpg-2-star-ocean-the-second','canvas':[640,360],'status':'UNAPPROVED NONRUNTIME test injection only; no default/source adoption or creator approval',
      'method':'Authored structural bays and shared maintenance floor, aged stone bases and contact clusters; no added noise or line-density tuning',
      'base':{'manifest':A.rel(BASE_MANIFEST),'sha256':A.sha(BASE_MANIFEST.read_bytes().replace(b'\r\n',b'\n')),'hash_algorithm':'sha256-text-lf-v1'},'palette':M['palette'],'layers_bottom_to_top':A.SCENE_LAYERS,
      'editable_sources':{'ora':src,'pxo':pxo,'png':flat_info},'runtime_exports':{'plate':plate_info,'foreground':fg_info,'antennas':antennas},
      'source_files':[{'file':A.rel(path),'sha256_text_lf':A.sha(path.read_bytes().replace(b'\r\n',b'\n'))} for path in [Path(__file__),KIT_PATH]],
      'protected_scene_script':{'file':'game/scripts/survey_annex.gd','sha256_text_lf':A.sha((ROOT/'game/scripts/survey_annex.gd').read_bytes().replace(b'\r\n',b'\n'))},
      'unchanged_layers':[A.SCENE_LAYERS[i] for i in [0,2,4,7,8,12]],'unchanged_alpha':[A.SCENE_LAYERS[i] for i in [9,10,11,12]],
      'changes_per_layer':{name:int((layers[i].a!=old[i].a).any(axis=2).sum()) for i,name in enumerate(A.SCENE_LAYERS)},
      'approval_scope':'Environment candidate only. 48-logical female static in review captures is a reference, not character/motion/full-set approval.'}
    path=OUT/f'{PREFIX}_structural-material-manifest_unapproved-v07_{STAMP}.json'
    path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(path);print(manifest['changes_per_layer'])
    return manifest


if __name__=='__main__':build()
