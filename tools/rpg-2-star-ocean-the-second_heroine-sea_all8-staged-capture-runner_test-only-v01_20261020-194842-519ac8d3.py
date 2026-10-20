"""Source-bound actual-Godot staged all8 action reel. Not normal input or hit-sync proof."""
import argparse,hashlib,importlib.util,json,os,subprocess,sys,uuid
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
PRIMARY=next(x for x in ROOT.parents if (x/'work/tooling').is_dir())
def lp(p):return Path('\\\\?\\'+str(p.resolve()))
def sha(p):return hashlib.sha256(lp(p).read_bytes()).hexdigest()
def read(p):return json.loads(lp(p).read_text(encoding='utf8'))
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--override');a=parser.parse_args()
 tag=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]
 out=ROOT/'outputs'/('hero-sea-all8-'+tag);out.mkdir()
 manifests=[next((ROOT/f'outputs/hero-sea-motion-v0{i}').glob('*_manifest_*.json')) for i in [1,2]]
 if a.override:manifests.append(Path(a.override))
 poses={};clips={};bound={}
 for path in manifests:
  m=read(path);bound[path.relative_to(ROOT).as_posix()]=sha(path);clips.update(m['clips'])
  if 'poseFiles' in m:
   entries=m['poseFiles']
   for key,v in entries.items():
    p=ROOT/v['path'] if 'path' in v else path.parent/v['name'];assert sha(p)==v['sha256'];poses[key]={'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
  else:
   for key,v in m['files'].items():
    if key.endswith('.png'):
     p=path.parent/v['name'];assert sha(p)==v['sha256'];poses[key[:-4]]={'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
  author=ROOT/m['source']['file'];bound[author.relative_to(ROOT).as_posix()]=sha(author)
 order=['idle','move','attack','guard','dodge','hit','skill','down'];assert all(k in clips for k in order)
 timeline=[]
 def add(action,pose,n,label='',critical=False):
  assert isinstance(n,int) and n>0 and pose in poses
  for j in range(n):timeline.append({'action':action,'pose':pose,'critical':critical and j==0,'label':label})
 for action in order:
  add(action,'base',6)
  clip=clips[action];frames=clip.get('enter',[])+clip['frames']*(2 if action in ['move','guard'] else 1)
  for i,f in enumerate(frames):add(action,f['pose'],f['ticks'],action+('-first' if i==0 else '-last'),i==0 or i==len(frames)-1)
  if action=='down':add(action,frames[-1]['pose'],12)
  add(action,'base',12)
 cfg={'root':str(ROOT),'tag':tag,'poses':poses,'timeline':timeline,'staged':True,'normalInputGameplay':False,'authoredTicksPerSecond':30,'sourceHashes':bound,'states':order}
 cfgpath=out/f'rpg-2-star-ocean-the-second_heroine-sea-all8_config_staged-v01_{tag}.json';cfgpath.write_text(json.dumps(cfg,indent=1)+'\n',encoding='utf8')
 harness=ROOT/'tools/rpg-2-star-ocean-the-second_heroine-sea_all8-staged-gameplay-view_test-only-v01_20261020-194645-e65718cb.gd'
 checked=ROOT/'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py'
 godot=PRIMARY/'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'
 spec=importlib.util.spec_from_file_location('ds_capture_helpers',ROOT/'tools/rpg-2-star-ocean-the-second_heroine-sea_motion-capture-runner_test-only-v01_20261020-153144-3fb36c1a.py');helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
 ff=helpers.find_ffmpeg();fp=helpers.ffprobe_for(ff);reports=[]
 for lang,fps,plate in [('en',30,'outskirts'),('zh',60,'default')]:
  env=dict(os.environ)
  for key in ['APPDATA','LOCALAPPDATA']:
   d=out/f'{key}-{lang}';d.mkdir();env[key]=str(d)
  log=out/f'rpg-2-star-ocean-the-second_heroine-sea-all8_{lang}-engine_staged-v01_{tag}.log'
  cmd=[sys.executable,'-I',str(checked),'--timeout','120','--expect','HSEA_ALL8_STAGED_OK','--log',str(log),'--',str(godot),'--path',str(ROOT/'game'),'--resolution','1280x720','--position','2000,100','--audio-driver','Dummy','--script',str(harness),'--',str(cfgpath),str(out),lang,str(fps),plate]
  run=subprocess.run(cmd,env=env,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=135)
  rp=out/f'rpg-2-star-ocean-the-second_heroine-sea-all8_{lang}-command_staged-v01_{tag}.log';rp.write_text(run.stdout+run.stderr,encoding='utf8')
  assert run.returncode==0 and 'CHECKED_RUN PASS' in run.stdout,(run.returncode,run.stdout[-2000:])
  data=read(out/f'rpg-2-star-ocean-the-second_heroine-sea-all8_{lang}-report_staged-v01_{tag}.json')
  assert data['posesByTick']==[t['pose'] for t in timeline] and data['frames']==len(timeline)*fps//30
  assert {v['action'] for v in data['critical']}==set(order) and all(v['outsideHero']==0 for v in data['critical'])
  for v in data['critical']:assert sha(out/v['file'])==v['sha256']
  movie=out/f'rpg-2-star-ocean-the-second_heroine-sea-all8_{lang}-{fps}fps_staged-v01_{tag}.mp4'
  ec=[str(ff),'-hide_banner','-v','error','-framerate',str(fps),'-i',str(out/f'frames-{lang}/frame_%05d.png'),'-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)]
  enc=subprocess.run(ec,capture_output=True,text=True,timeout=60);assert enc.returncode==0 and not enc.stderr,enc.stderr
  probe=subprocess.run([str(fp),'-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames:format=duration','-of','json',str(movie)],capture_output=True,text=True,timeout=30)
  pd=json.loads(probe.stdout);st=pd['streams'][0];assert st['width']==1280 and st['height']==720 and st['r_frame_rate']==f'{fps}/1' and int(st['nb_read_frames'])==data['frames'] and abs(float(pd['format']['duration'])-len(timeline)/30)<0.02
  reports.append({'language':lang,'fps':fps,'movie':movie.relative_to(ROOT).as_posix(),'sha256':sha(movie),'probe':pd,'stateCoverage':order,'warningLines':[l for l in (run.stdout+run.stderr).splitlines() if 'WARNING' in l],'data':data})
 assert all(sha(ROOT/k)==v for k,v in bound.items())
 report={'staged':True,'continuousNormalInputGameplay':False,'creatorApproved':False,'hitSynchronized':False,'fullSpriteAccepted':False,'sourceHashes':bound,'configuration':cfgpath.relative_to(ROOT).as_posix(),'configurationSha256':sha(cfgpath),'captureSource':harness.relative_to(ROOT).as_posix(),'captureSourceSha256':sha(harness),'runnerSha256':sha(Path(__file__)),'clips':reports,'result':'PASS','limitations':['authored8state visual reel only','real attack damage atpress, current visualcontact166.667ms later','hero skill is buff, not direct damage','neither1xdecoding nor static frame inspection certifies continuous fluidity']}
 (out/f'rpg-2-star-ocean-the-second_heroine-sea-all8_source-playback-proof_staged-v01_{tag}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
 print('HSEA_ALL8_ROOT_PASS',str(out))
if __name__=='__main__':main()
