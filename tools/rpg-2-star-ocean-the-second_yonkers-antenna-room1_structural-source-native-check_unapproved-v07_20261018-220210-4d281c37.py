"""Independent final package, mask/anchor and actual Pixelorama export checks for corrected v07; no runtime/art acceptance."""
import argparse
import io
import json
import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from PIL import Image
import importlib.util

# Asset paths exceed MAX_PATH in canonical worktrees. Keep the Win32 extended
# root on every descendant Path (Pillow, zipfile and pathlib all receive it).
ROOT=Path(__file__).resolve().parents[1]
if os.name == 'nt' and not str(ROOT).startswith('\\\\?\\'):
 ROOT=Path('\\\\?\\UNC\\'+str(ROOT)[2:] if str(ROOT).startswith('\\\\') else '\\\\?\\'+str(ROOT))
OUT=ROOT/'outputs/yk1-v07_7a10f835'
STAMP='20261018-220210-4d281c37'
PREFIX='rpg-2-star-ocean-the-second_yonkers-antenna-room1'


def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def ora(path):
 with zipfile.ZipFile(path) as archive:
  xml=ET.fromstring(archive.read('stack.xml'))
  arrays={n.attrib['name']:np.array(Image.open(io.BytesIO(archive.read(n.attrib['src']))).convert('RGBA')) for n in xml.findall('.//layer')}
  flat=np.array(Image.open(io.BytesIO(archive.read('mergedimage.png'))).convert('RGBA'))
 return arrays,flat


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--pixelorama',required=True);args=ap.parse_args()
 author=module('v07_author',ROOT/'tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_structural-material-author_unapproved-v07_20261018-215722-7a10f835.py')
 A=author.A
 manifest=json.loads((OUT/f'{PREFIX}_structural-material-manifest_unapproved-v07_{STAMP}.json').read_text(encoding='utf-8'))
 base=json.loads((ROOT/manifest['base']['manifest']).read_text(encoding='utf-8'))
 arrays,flat=ora(ROOT/manifest['editable_sources']['ora']['file']);old,_=ora(ROOT/base['editable_sources']['ora']['file'])
 layers=[]
 for name in A.SCENE_LAYERS:
  lay=A.Layer();lay.a=arrays[name];layers.append(lay)
 export=manifest['runtime_exports']
 pinned=[*manifest['editable_sources'].values(),export['plate'],export['foreground'],*[i['runtime_png'] for i in export['antennas']]]
 checks={
  'base_manifest_hash':manifest['base']['hash_algorithm']=='sha256-text-lf-v1' and A.sha((ROOT/manifest['base']['manifest']).read_bytes().replace(b'\r\n',b'\n'))==manifest['base']['sha256'],
  'all_asset_hashes':all(A.sha((ROOT/i['file']).read_bytes())==i['sha256'] for i in pinned),
  'source_and_scene_hashes':all(A.sha((ROOT/i['file']).read_bytes().replace(b'\r\n',b'\n'))==i['sha256_text_lf'] for i in [*manifest['source_files'],manifest['protected_scene_script']]),
  'thirteen_native_layers':len(arrays)==13 and all(a.shape==(360,640,4) for a in arrays.values()),
  'protected_layers_exact':all(np.array_equal(arrays[n],old[n]) for n in manifest['unchanged_layers']),
  'antenna_foreground_alpha_exact':all(np.array_equal(arrays[n][...,3],old[n][...,3]) for n in manifest['unchanged_alpha']),
  'binary_alpha_and_declared_palette':all(set(np.unique(a[...,3]))<={0,255} and {tuple(c) for c in a[a[...,3]==255,:3]}<=set(A.RGB.values()) for a in arrays.values()),
  'flattened_composition_exact':np.array_equal(flat,A.composite(layers)),
 }
 with zipfile.ZipFile(ROOT/manifest['editable_sources']['pxo']['file']) as archive:
  data=json.loads(archive.read('data.json'))
  checks['pxo_native_layers_exact']=[i['name'] for i in data['layers']]==A.SCENE_LAYERS and all(archive.read(f'image_data/frames/1/layer_{index+1}')==layers[index].a.tobytes() for index in range(13))
 for key,expected in [('plate',A.composite(layers[:9])),('foreground',layers[12].a)]:
  checks[key+'_export_exact']=np.array_equal(np.array(Image.open(ROOT/export[key]['file']).convert('RGBA')),expected)
 checks['anchors_and_crops_exact']=all(item['anchor']==[x,210] and item['crop_from_layer_xywh']==[x-64,58,128,152] for x,item in zip([163,320,477],export['antennas']))
 for index,item in enumerate(export['antennas']):
  x,y,w,h=item['crop_from_layer_xywh']
  checks[f'antenna_{index}_export_exact']=np.array_equal(np.array(Image.open(ROOT/item['runtime_png']['file']).convert('RGBA')),layers[index+9].a[y:y+h,x:x+w])
 C=module('existing_native_export_check',ROOT/'tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_pixel-source-pixelorama-check_unapproved-v03_20261017-224447-15709be4.py')
 C.ROOT=ROOT
 # Keep native diagnostics separate from byte-exact export checks: exit zero alone is not a clean log.
 native_runs=[]
 original_run=C.run_pixelorama
 def logged_run(exe,argv,appdata):
  result=original_run(exe,argv,appdata)
  label=('split' if '--split-layers' in argv else 'flat')+'-'+Path(argv[-1]).suffix.lstrip('.')
  text='STDOUT\n'+result.stdout+'\nSTDERR\n'+result.stderr
  log=OUT/f'{PREFIX}_pixelorama-{label}-diagnostic-log_unapproved-v07_{STAMP}.txt'
  log.write_text(text,encoding='utf-8')
  problems=[line for line in text.splitlines() if any(token in line.lower() for token in ['error:', 'script error', 'get_child', 'ancestor', 'ancestry', 'orphan', 'leaked', 'still in use'])]
  native_runs.append({'mode':label,'exit':result.returncode,'log':log.relative_to(ROOT).as_posix(),'diagnostic_lines':problems})
  return result
 C.run_pixelorama=logged_run
 native=C.pixelorama_checks(args.pixelorama,A,layers,manifest)
 native['diagnostics']={'status':'errors_present' if any(run['diagnostic_lines'] for run in native_runs) else 'no_error_patterns_found','runs':native_runs}
 for ext in ['pxo','ora']:
  check=native[ext]
  checks[ext+'_pixelorama_exact']=check['split']['exit']==0 and check['split']['pngs']==13 and all(check['split']['layers_exact'].values()) and check['flat']['exit']==0 and check['flat']['exact'] and check['flat']['differing_texels']==0 and check['source_unchanged_by_cli']
 checks['real_pixelorama_preferences_untouched']=not native['real_appdata_pixelorama_changed']
 report={'status':'UNAPPROVED technical candidate; not final art','manifest':str((OUT/f'{PREFIX}_structural-material-manifest_unapproved-v07_{STAMP}.json').relative_to(ROOT)).replace('\\','/'),'checks':checks,'native_export':native,'passed':sum(checks.values()),'total':len(checks)}
 path=OUT/f'{PREFIX}_structural-source-native-report_unapproved-v07_{STAMP}.json'
 path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('V07_SOURCE_NATIVE',report['passed'],'/',report['total']);print(path)
 if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
