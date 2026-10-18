"""Compare corrected v07 actual Godot evidence against its native source and a fresh, fixed-60fps v06 control."""
import json
from pathlib import Path
import importlib.util
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/yk1-v07_7a10f835'
STAMP='20261018-220210-4d281c37'
P='rpg-2-star-ocean-the-second_yonkers-antenna-room1'


def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def main():
 S=load('source_check',ROOT/f'tools/{P}_structural-source-native-check_unapproved-v07_{STAMP}.py')
 A=load('asset_author',ROOT/f'tools/{P}_structural-material-author_unapproved-v07_20261018-215722-7a10f835.py').A
 manifest=json.loads((OUT/f'{P}_structural-material-manifest_unapproved-v07_{STAMP}.json').read_text(encoding='utf-8'))
 arrays,_=S.ora(ROOT/manifest['editable_sources']['ora']['file']);layers=[]
 for name in A.SCENE_LAYERS:
  l=A.Layer();l.a=arrays[name];layers.append(l)
 log=(OUT/f'{P}_structural-runtime-check-log_unapproved-v07_{STAMP}.txt').read_text(encoding='utf-8')
 control=(OUT/f'{P}_v06-control-runtime-check-log_test-only_{STAMP}.txt').read_text(encoding='utf-8')
 C=load('existing_pixel_check',ROOT/f'tools/{P}_pixel-source-pixelorama-check_unapproved-v03_20261017-224447-15709be4.py')
 C.CAP=OUT/'cap-final';C.cap=lambda lang,label:C.CAP/f'{P}_v07-test-only-godot-{lang}-{label}-640x360_{STAMP}.png'
 pixels=C.capture_checks(A,layers,log.replace('YK1_V06_','YK1_V03_'))
 prefixes=('HUD_CLEAR','HEADER_','CAPTION_','DEPTH','ROOM1_INTERACTIONS_OK','REACHABILITY_OK','ALL_SIX_CLUES_OK','TRANSITION_',
           'ISOLATION_OK','ANTENNA ','COLLISION ','SLIDE_OK','ESCAPE_OK','LANE_WALK_OK')
 def behaviour(text):
  return [line[len('YK1_V06_'):] for line in text.splitlines() if line.startswith('YK1_V06_') and line[len('YK1_V06_'):].startswith(prefixes)]
 candidate_lines,control_lines=behaviour(log),behaviour(control)
 required=['TEXTURES_IN_USE','ROOM1_INTERACTIONS_OK','ALL_SIX_CLUES_OK 6/6','TRANSITION_NEXT_OK','TRANSITION_BACK_OK','TRANSITION_EXIT_OK','LANE_WALK_OK','REACHABILITY_OK','ISOLATION_OK','SLIDE_OK','ESCAPE_OK','ALL_OK']
 checks={
  'v07_manifest_injected':'YK1_V07_INJECTED manifest=' in log and str(manifest['editable_sources']['ora']['file']).endswith(f'{STAMP}.ora'),
  'v07_v06_clean_logs':all('SCRIPT ERROR' not in text and 'SCRIPT_ERROR' not in text and 'YK1_V06_FAIL' not in text and '\nERROR:' not in text for text in [log,control]),
  'required_runtime_protocol':all('YK1_V06_'+tag in log for tag in required),
  'fourteen_collision_cases':log.count('YK1_V06_COLLISION ')==14,
  'fresh_control_behaviour_exact':len(candidate_lines)>35 and candidate_lines==control_lines,
  'thirty_native_captures':pixels['capture_count']==30 and pixels['captures_640x360'],
  'actual_bilingual_native_pixels':all(pixels[f'{lang}_entry_scene_exact_outside_ui']['differing']==0 for lang in ['zh','en']),
 }
 captures=[]
 for path in sorted((OUT/'cap-final').glob('*.png')):
  captures.append({'file':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':A.sha(path.read_bytes())})
 evidence={'status':'UNAPPROVED technical candidate, root art verdict changes_requested','checks':checks,'passed':sum(checks.values()),'total':len(checks),
   'pixel_comparison':pixels,'behaviour_lines':len(candidate_lines),'control_v06_same_fixed_fps':True,'differences':[[a,b] for a,b in zip(candidate_lines,control_lines) if a!=b],
   'captures':captures,'logs':[{'file':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':A.sha(path.read_bytes().replace(b'\r\n',b'\n')),'hash_algorithm':'sha256-text-lf-v1'} for path in [OUT/f'{P}_structural-runtime-check-log_unapproved-v07_{STAMP}.txt',OUT/f'{P}_v06-control-runtime-check-log_test-only_{STAMP}.txt']]}
 path=OUT/f'{P}_structural-runtime-evidence-report_test-only-v07_{STAMP}.json'
 path.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('V07_RUNTIME_EVIDENCE',evidence['passed'],'/',evidence['total'],'behaviour_lines',len(candidate_lines));print(json.dumps(pixels['zh_entry_scene_exact_outside_ui']));print(path)
 if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
