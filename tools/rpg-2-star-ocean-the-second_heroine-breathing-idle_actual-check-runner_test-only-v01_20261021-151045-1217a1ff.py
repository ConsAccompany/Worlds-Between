"""Bounded actual normal-default breathing capture. Scripted input, never a human playtest."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,subprocess,sys,uuid
C=Path(__file__).resolve().parents[1]
P=next(p for p in [C,*C.parents] if (p/"work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe").exists())
GODOT=P/"work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe"
CHECKED=C/"tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py"
HARNESS=C/"tools/rpg-2-star-ocean-the-second_heroine-breathing-idle_actual-flow-capture_test-only-v01_20261021-151045-1217a1ff.gd"
def main():
    p=argparse.ArgumentParser();p.add_argument('--destination',choices=['scifi.city','scifi.ruins'],required=True);p.add_argument('--language',choices=['en','zh'],required=True);p.add_argument('--fps',type=int,choices=[30,60],required=True);a=p.parse_args()
    tag=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]
    out=C/'outputs/idle21';out.mkdir(exist_ok=True)
    profile=out/'profiles'/tag;profile.mkdir(parents=True)
    env=dict(os.environ,APPDATA=str(profile),LOCALAPPDATA=str(profile))
    stem='rpg-2-star-ocean-the-second_heroine-breathing-idle_'+a.destination.split('.')[1]+'-'+a.language+'-'+str(a.fps)+'fps_actual-default-v01_'+tag
    raw=profile/(stem+'.avi');log=out/(stem+'.log');movie=out/(stem+'.mp4')
    cmd=[sys.executable,'-X','utf8','-I',str(CHECKED),'--timeout','75','--expect','BREATH21_CAPTURE_PASS','--log',str(log),'--',str(GODOT),'--resolution','1280x720','--position','40,40','--audio-driver','Dummy','--fixed-fps',str(a.fps),'--write-movie',str(raw),'--path',str(C/'game'),'--script',str(HARNESS),'--',str(out),tag,a.destination,a.language,str(a.fps)]
    r=subprocess.run(cmd,env=env,capture_output=True,text=True,encoding='utf-8',timeout=90)
    if r.returncode:
        print(r.stdout[-5000:]);print(r.stderr[-1000:]);raise SystemExit(r.returncode)
    ffmpeg=shutil.which('ffmpeg') or r'C:/Users/hkzha/AppData/Local/Microsoft/WinGet/Links/ffmpeg.EXE'
    subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-i',str(raw),'-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],check=True,capture_output=True,timeout=90)
    reports=list(out.glob('*actual-proof-v01_'+tag+'.json'));assert len(reports)==1
    report=json.loads(reports[0].read_text());assert not report['failures'];assert report['fps']==a.fps
    report['movie']={'file':movie.name,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'normalPlaybackSpeed':True,'engineFps':a.fps,'testOnly':True}
    reports[0].write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    raw.resolve().relative_to(profile.resolve());raw.unlink()
    print('BREATH21_ACTUAL_PASS',a.destination,a.language,a.fps,len(report['checks']),reports[0].relative_to(C).as_posix());print('MOVIE',movie.relative_to(C).as_posix())
if __name__=='__main__':main()
