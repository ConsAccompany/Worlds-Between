"""Keep source/native/captures compact; raw captured PNG sequences remain Temp-only."""
from pathlib import Path
import gzip,hashlib,json,os,shutil,subprocess
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];SLUG='rpg-2-star-ocean-the-second';STAMP='20261018-183043';ID='c704ea98';OUT=ROOT/'outputs/female-west-run-stop-v01';TEMP=Path(os.environ['TEMP'])
CORE='tools/rpg-2-star-ocean-the-second_female-west_run-stop-source_unapproved-v01_20261018-181150-a94f021c.gd'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return Path(p).read_bytes()
def main():
 native=OUT/f'{SLUG}_female-west-run-stop_native-source-manifest_unapproved-v01_20261018-182900-0817f0b2.json';n=json.loads(read(native));rgba={r['index']:sha(Image.open(ROOT/r['file']).convert('RGBA').tobytes()) for r in n['sets']['run']['frames']}
 m={'task':'content.char.protagonist-female.walk-west','productionScope':'One source-authored west run and phase-responsive stop. Produced candidate only, not final art/fluidity/full set.','artApproved':False,'motionApproved':False,'runtimeIntegrated':False,'core':CORE,'nativeManifest':native.relative_to(ROOT).as_posix(),'nativeReport':(OUT/f'{SLUG}_female-west-run-stop_native-report_v01_20261018-182900-0817f0b2.json').relative_to(ROOT).as_posix(),'captures':[],'transitionReports':[],'protectedAnchor':'86e0c54','protectedGameSources':{},'files':{}}
 for role,stem in [('initial-landing-failure','transitions'),('landing-corrected','transitions-fixed'),('initial-visible-contact-failure','visible-ground-transitions'),('visible-contact-corrected','visible-ground-transitions-fixed'),('startup-visible-contact','complete-visible-ground-transitions'),('pre-body-matched-boundary','exact-boundary-transitions'),('final-exact-boundary','exact-boundary-body-matched')]:
  source=TEMP/f'{SLUG}_female-west-run_{stem}_v01_20261018-182100-3be905c1.json';raw=read(source);report=json.loads(raw);name=f'{SLUG}_female-west-run_{role}-report_v01_{STAMP}-{ID}.json.gz';(OUT/name).write_bytes(gzip.compress(raw,compresslevel=9,mtime=0));m['transitionReports'].append({'role':role,'file':(OUT/name).relative_to(ROOT).as_posix(),'uncompressedSha256':sha(raw),'passed':report['passed'],'failed':report['failed'],'modelSha256':report['modelSha256']})
 for scene,fps in [('city-bright',30),('annex-room2-dark',60)]:
  folder=TEMP/'wb-west-run-final-bind-a94f021c'/scene;report_path=next((folder/'frames').glob('*report*.json'));r=json.loads(read(report_path));assert r['failed']==0 and r['modelSha256']==n['sources'][CORE]
  report_target=OUT/report_path.name;report_target.write_bytes(read(report_path))
  movie=next(folder.glob('*.mp4'));(OUT/movie.name).write_bytes(read(movie))
  log=next(folder.glob('*.log'));(OUT/log.name).write_bytes(read(log).replace(b'\r\r\n',b'\n').replace(b'\r\n',b'\n'))
  steady=[f for f in r['frames'] if f['state']['mode']=='run' and f['state']['age']>=.12];assert all(f['sourceRgbaSha256']==rgba[int(f['state']['q'])] for f in steady)
  start=[f for f in steady if f['segment']=='start-run'];selected=[]
  for label,q in [('contact',0),('passing',76),('flight',116)]:selected.append((label,min(start,key=lambda f:abs((f['state']['q']-q+64)%128-64))))
  selected.append(('release-first',next(f for f in r['frames'] if f['segment']=='release')))
  selected.append(('repress-first',next(f for f in r['frames'] if f['segment']=='repress')))
  selected.append(('settle-before-idle',next(f for f in reversed(r['frames']) if f['segment']=='final-stop' and f['state']['mode']=='stop')))
  selected.append(('final-static',r['frames'][-1]))
  critical=[]
  for label,f in selected:
   name=f'{SLUG}_female-west-run_critical-{scene}-{label}-640_v01_{STAMP}-{ID}.png';(OUT/name).write_bytes(read(folder/'frames'/f['file']));critical.append({'purpose':label,'tick':f['tick'],'phase':f['state']['q'],'file':(OUT/name).relative_to(ROOT).as_posix()})
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height,r_frame_rate,nb_frames,duration','-of','json',str(movie)]))['streams'][0]
  m['captures'].append({'scene':scene,'fps':fps,'report':report_target.relative_to(ROOT).as_posix(),'movie':(OUT/movie.name).relative_to(ROOT).as_posix(),'probe':probe,'simulationSeconds':len(r['frames'])/fps,'recordingWallClockMs':r['recordingWallClockMs'],'steadyRgbaMatches':len(steady),'critical':critical,'rawFramesTempOnly':str(folder/'frames')})
 for p in ['game/scripts/app_state.gd','game/scripts/scifi_exploration_area.gd','game/scripts/survey_annex.gd','game/project.godot']:
  data=read(ROOT/p).replace(b'\r\n',b'\n');baseline=subprocess.check_output(['git','show',m['protectedAnchor']+':'+p],cwd=ROOT).replace(b'\r\n',b'\n');assert data==baseline;m['protectedGameSources'][p]=sha(data)
 files=list(OUT.glob('*'))+list((ROOT/'tools').glob(f'{SLUG}_female-west_run-stop-*.*'))+list((ROOT/'docs/qa').glob(f'{SLUG}_female-west-run-stop_produced-candidate-unapproved-v01_{STAMP}-{ID}.md'))
 for p in files:
  if p.suffix=='.uid' or 'evidence-manifest' in p.name:continue
  relative=p.relative_to(ROOT).as_posix();data=read(p);text=p.suffix in ['.py','.gd','.md','.json','.log'];m['files'][relative]={'sha256':sha(data.replace(b'\r\n',b'\n') if text else data),'textLf':text,'bytes':len(data)}
 path=OUT/f'{SLUG}_female-west-run-stop_evidence-manifest_v01_{STAMP}-{ID}.json';path.write_text(json.dumps(m,indent=2)+'\n',newline='\n');print(path);print('files',len(m['files']),'bytes',sum(r['bytes'] for r in m['files'].values()))
if __name__=='__main__':main()
