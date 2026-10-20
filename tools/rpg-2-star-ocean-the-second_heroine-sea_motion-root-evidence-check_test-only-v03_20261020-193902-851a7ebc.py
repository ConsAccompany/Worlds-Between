"""Independent frozen-capture evidence check; preserves the producer and first root failures."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
CAP=ROOT/'outputs/hero-sea-motion-capture-v02'
REPORT=CAP/'rpg-2-star-ocean-the-second_heroine-sea-motion_report_v02_20261020-193528-841e9bf3.json'
OUT=CAP/'rpg-2-star-ocean-the-second_heroine-sea-motion_root-path-and-source-check_v03_20261020-193902-851a7ebc.json'
def raw(p): return Path('\\\\?\\'+str(p.resolve())).read_bytes()
def sha(p): return hashlib.sha256(raw(p)).hexdigest()
def js(p): return json.loads(raw(p).decode('utf8'))
checks=[]
def ck(name,value):
 checks.append({'check':name,'pass':bool(value)})
 assert value,name
r=js(REPORT)
ck('original root failure preserved exactly: two long-path anticipation is_file false negatives',r['failures']==['en30: critical anticipation not full-size PNG','zh60: critical anticipation not full-size PNG'])
ck('frozen current arena raw sha matches',sha(ROOT/'game/scripts/battle_arena.gd')==r['arenaSha256Expected']==r['arenaSha256'])
ck('all bound source/input hashes unchanged',r['boundSha256AtStart']==r['boundSha256AtEnd'])
ck('staged labels: no continuous-input, fullset or creator-approval claim',r['testOnly'] and r['staged'] and not r['continuousNormalInputCombat'] and not r['allEightActions'] and not r['creatorApproved'])
for rel,h in r['boundSha256AtEnd'].items():
 # The producer stores complete source paths; these remain local locators in the frozen report.
 p=Path(rel)
 if p.is_absolute(): ck('bound on-disk '+p.name,sha(p)==h)
m=js(ROOT/r['input']['manifest'])
ck('manifest exact',sha(ROOT/r['input']['manifest'])==r['input']['manifestSha256'])
for k,v in r['input']['poseFiles'].items(): ck('pose '+k,sha(ROOT/v['file'])==v['sha256'])
expected=[]
for tick in range(204):
 local=tick%102
 if 60<=local<72: frames=m['clips']['attack']['frames']; phase=local-60
 else: frames=m['clips']['idle']['frames']; phase=(local if local<60 else local-72)%28
 for f in frames:
  if phase<int(f['ticks']):expected.append(f['pose']);break
  phase-=int(f['ticks'])
ck('independent authored pose count',len(expected)==204)
critical=[]; warnings=[]
for v in r['verification']:
 lang,fps=v['language'],v['fps']; src=js(CAP/f'raw-{lang}-{fps}.json')
 ck(f'{lang}{fps} all204 authored selections exact',src['poseAtTick']==expected)
 for label,tick in {'base':0,'anticipation':62,'contact':65,'recovery':69}.items():
  x=v['critical'][label]; p=CAP/x['file']; b=raw(p)
  ck(f'{lang}{fps} {label} full PNG hash and1280x720',b[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',b[16:24])==(1280,720) and sha(p)==x['sha256'])
  ck(f'{lang}{fps} {label} exact authored tick/pose',x['tick']==tick and x['pose']==expected[tick] and x['frame']==tick*fps//30)
  critical.append({'language':lang,'fps':fps,'label':label,'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p)})
 ck(f'{lang}{fps} no outsidehero change/restore/UI movement',v['data']['changedOutsideHeroBounds']==0 and v['data']['restoredEqualsBaselineRgba'] and v['data']['finalRestoreEqualsBaselineRgba'] and v['data']['controlsBeforeEqualsAfter'])
 frames=sorted((CAP/f'frames_{lang}_{fps}').glob('frame_*.png'))
 ck(f'{lang}{fps} actualframe count',len(frames)==204*fps//30)
 hashes=[sha(f) for f in frames]
 ck(f'{lang}{fps} frame sequence hash',hashlib.sha256('\n'.join(hashes).encode()).hexdigest()==src['frames']['sha256ListSha256'])
 ck(f'{lang}{fps} restore PNG byte exact',raw(CAP/f'verify-baseline_{lang}_{fps}.png')==raw(CAP/f'verify-restored_{lang}_{fps}.png'))
for clip in r['clips']:
 ck('encoded clip all original gates '+clip['language'],all(clip['checks'].values()) and sha(ROOT/clip['mp4'])==clip['mp4Sha256'])
 cmd=[r['ffmpeg']['ffprobe'],'-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames:format=duration','-of','json',str(ROOT/clip['mp4'])]
 run=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',timeout=30); d=json.loads(run.stdout); st=d['streams'][0]
 ck('independent ffprobe '+clip['language'],run.returncode==0 and not run.stderr and st['width']==1280 and st['height']==720 and st['r_frame_rate']==str(clip['fps'])+'/1' and int(st['nb_read_frames'])==clip['frameCount'] and abs(float(d['format']['duration'])-6.8)<0.02)
for run in r['runnerRuns']:
 log=raw(ROOT/run['log']).decode('utf8',errors='replace')
 ck('unfiltered engine ERROR gate '+run['rule'],run['exit']==0 and run['checkedRunnerPass'] and not any(x in log for x in ['ERROR:','SCRIPT ERROR','SCRIPT_ERROR','Parse Error']))
 warnings.extend({'run':run['rule'],'line':line} for line in log.splitlines() if 'WARNING' in line)
ck('real event probe shows19damage atpress and166.667ms mismatch',r['realAttackEventProbe']['immediateDamage']==19 and r['realAttackEventProbe']['immediateGameDamageAtSeconds']==0 and r['realAttackEventProbe']['mismatch'] and not r['realAttackEventProbe']['synchronizedGameplayContact'])
proof={'generatedAt':datetime.now(timezone.utc).isoformat(),'status':'technical capture proof, not fluidity/art approval','originalReport':REPORT.relative_to(ROOT).as_posix(),'originalReportSha256':sha(REPORT),'rootCaptureSource':r['harness'],'rootCaptureSourceSha256':r['harnessSha256'],'pathCorrection':'Windows extended-length reads; no image, time, range or diagnostic threshold changed. Both original failures preserved.','passed':len(checks),'total':len(checks),'checks':checks,'warningsNotSuppressed':warnings,'applicationWarningFree':not warnings,'clips':r['clips'],'critical':critical,'fullActionTask':'in_progress, partial2of8','creatorApproved':False,'continuousFluidityCertified':False,'hitSynchronized':False,'sourceFiles':{p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'outputs/hero-sea-motion-v01').glob('*')},'hashNormalization':'sha256 raw bytes'}
OUT.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print('HSEA_ROOT_PATH_SOURCE_PASS',len(checks),'/',len(checks),'warnings',len(warnings),'proof',OUT.name)
