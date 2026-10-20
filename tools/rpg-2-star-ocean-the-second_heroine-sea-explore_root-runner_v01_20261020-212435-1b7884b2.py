import os,json,subprocess,importlib.util,hashlib,uuid
from pathlib import Path
from datetime import datetime,timezone
C=Path(__file__).resolve().parents[1];P=next(p for p in C.parents if (p/'work/tooling/godot-4-7-2').is_dir())
def lp(p):return Path('\\\\?\\'+str(p.resolve()))
def sha(p):return hashlib.sha256(lp(p).read_bytes()).hexdigest()
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
ck=module('checked',C/'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py')
media=module('media',C/'tools/rpg-2-star-ocean-the-second_heroine-sea_motion-capture-runner_test-only-v01_20261020-153144-3fb36c1a.py')
godot=P/'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe';ffmpeg=media.find_ffmpeg();probe=media.ffprobe_for(ffmpeg)
tag=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8];out=C/'outputs/hse-root08';out.mkdir(exist_ok=True)
h=next((C/'tools').glob('*heroine-sea-explore_normal-input-root-check*'));reg=next((C/'game/data/heroine-sea-explore-v03').glob('*registry*.json'));registry='res://'+reg.relative_to(C/'game').as_posix();records=[]
for context,fps in [('city',30),('room',60)]:
 raw=P/'work/dual08/root-movies'/tag/context;raw.mkdir(parents=True)
 for key,suffix in [('APPDATA','a'),('LOCALAPPDATA','l')]:
  profile=P/'work/dual08/profiles'/('rt'+context)/suffix;profile.mkdir(parents=True,exist_ok=True);os.environ[key]=str(profile)
 stem='rpg-2-star-ocean-the-second_'+context+'_raw_'+tag
 cmd=[str(godot),'--path',str(C/'game'),'--resolution','1280x720','--position','40,40','--audio-driver','Dummy','--fixed-fps',str(fps),'--write-movie',str(raw/(stem+'.png')),'--script',str(h),'--',registry,str(out),tag,context,str(fps)]
 log=out/f'rpg-2-star-ocean-the-second_heroine-sea-explore_{context}-root-run_v01_{tag}.log';result=ck.run_checked(cmd,100,expected=['EXP_NORMAL_ROOT_PASS'],log_path=lp(log))
 print(context,result['passed'],result['reason'],result['log'][-650:],flush=True);assert result['passed'],result['log'][-3000:]
 frames=list(raw.glob(stem+'*.png'));movie=out/f'rpg-2-star-ocean-the-second_heroine-sea-explore_{context}-{fps}fps-normal-input_unapproved-v03_{tag}.mp4'
 enc=subprocess.run([str(ffmpeg),'-hide_banner','-v','error','-y','-framerate',str(fps),'-i',str(raw/(stem+'%08d.png')),'-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],capture_output=True,text=True,encoding='utf-8');assert enc.returncode==0,enc.stderr
 rr=subprocess.run([str(probe),'-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,avg_frame_rate,nb_read_frames:format=duration,size','-of','json',str(movie)],capture_output=True,text=True,encoding='utf-8');assert rr.returncode==0,rr.stderr
 info=json.loads(rr.stdout);st=info['streams'][0];assert st['width']==1280 and st['height']==720 and st['avg_frame_rate']==f'{fps}/1' and int(st['nb_read_frames'])==len(frames) and movie.stat().st_size<=16*1024*1024
 records.append({'context':context,'fps':fps,'movie':movie.relative_to(C).as_posix(),'sha256':sha(movie),'probe':info,'command':cmd,'log':log.relative_to(C).as_posix(),'warnings':[x for x in result['log'].splitlines() if 'WARNING' in x]})
 print('EXP_MOVIE_PASS',context,len(frames),flush=True)
report={'completedAt':datetime.now(timezone.utc).isoformat(),'result':'PASS','runs':records,'harnessSha256':sha(h),'registry':registry,'registrySha256':sha(reg),'sourceManifestSha256':sha(next((C/'outputs/hsea-exp03').glob('*source-manifest*.json'))),'defaultAdoption':False,'artApproved':False,'fluidityCertified':False}
f=out/f'rpg-2-star-ocean-the-second_heroine-sea-explore_combined-root-proof_v01_{tag}.json';lp(f).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('ROOT_SEA_EXPLORE_COMBINED_PASS',f,flush=True)
