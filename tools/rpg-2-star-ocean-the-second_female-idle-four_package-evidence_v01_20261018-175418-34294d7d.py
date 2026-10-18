"""Compact evidence package: two real-time movies, twelve independent critical images, not raw-frame Git bloat."""
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
from datetime import datetime
import hashlib,json,os,subprocess,tempfile,uuid
ROOT=Path(__file__).resolve().parents[1]
AUTHOR=ROOT/'tools/rpg-2-star-ocean-the-second_female-idle-four-direction_native-build_unapproved-v01_20261018-175418-34294d7d.py'
spec=spec_from_file_location('idle_package_author',AUTHOR);a=module_from_spec(spec);spec.loader.exec_module(a)
PROOF=a.OUT/f'{a.SLUG}_female-idle-four_evidence-manifest_v01_{a.STAMP}-{a.ID}.json'
def write_json(path,data):Path(a.long(path)).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
def main():
 manifest=next(a.OUT.glob('*direction-manifest*.json'));m=json.loads(a.read(manifest));native=max(a.OUT.glob('*native-report*.json'),key=lambda p:p.stat().st_mtime)
 n=json.loads(a.read(native));assert n['manifestSha256']==a.sha(a.read(manifest))
 assert all(d['allCellsExact'] and d['exit']==0 for d in n['native'])
 assert all(not d['unexpectedDiagnostics'] for d in n['native'] if d['format']=='pxo')
 assert len([d for d in n['native'] if d['format']=='ora' and d['unexpectedDiagnostics']])==12
 stamp=datetime.now().strftime('%Y%m%d-%H%M%S');ident=uuid.uuid4().hex[:8];bound={};movies=[];critical=[];capture_reports=[]
 def bind(path,data):
  Path(a.long(path)).write_bytes(data);rel=path.relative_to(ROOT).as_posix();bound[rel]=a.sha(data);return rel
 for fps in [30,60]:
  temp=Path(os.environ['TEMP'])/f'wb-idle-four-timed-{fps}-34294d7d';raw=temp/'frames';report_path=next(raw.glob('*actual-report*.json'));report=json.loads(report_path.read_text(encoding='utf-8'))
  assert report['manifestSha256']==a.sha(a.read(manifest)) and len(report['frames'])==int(20.8*fps)
  assert report['canvas']==[640,360] and not report['artApproved'] and not report['motionApproved']
  for f in report['frames']:assert a.sha(a.read(raw/f['file']))==f['sha256']
  log=next(temp.glob('*capture-log*.txt'));b=log.read_bytes();text=b.decode('utf-16') if b.startswith(b'\xff\xfe') else b.decode('utf-8-sig')
  assert 'IDLE_FOUR_CAPTURE PASS' in text and not any(line.startswith(('ERROR:','SCRIPT ERROR')) for line in text.splitlines())
  scene=report['scene'];base=f'{a.SLUG}_female-idle-{scene}-{fps}fps'
  log_rel=bind(a.OUT/f'{base}_capture-log_v01_{stamp}-{ident}.txt',text.replace('\r\n','\n').encode())
  report_rel=bind(a.OUT/f'{base}_actual-report_v01_{stamp}-{ident}.json',report_path.read_bytes());capture_reports.append(report_rel)
  pattern=raw/report['frames'][0]['file'].replace('frame-0000','frame-%04d')
  encoded=temp/f'{base}_normal1x-movie_v01_{stamp}-{ident}.mp4'
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(fps),'-i',str(pattern),'-c:v','libx264','-preset','fast','-crf','12','-pix_fmt','yuv420p','-movflags','+faststart',str(encoded)],check=True)
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,nb_frames,r_frame_rate,duration','-of','json',str(encoded)]))['streams'][0]
  assert int(probe['nb_frames'])==len(report['frames']) and probe['r_frame_rate']==f'{fps}/1' and (probe['width'],probe['height'])==(640,360) and abs(float(probe['duration'])-20.8)<.001
  movie_rel=bind(a.OUT/encoded.name,encoded.read_bytes());movies.append({'file':movie_rel,'probe':probe,'captureReport':report_rel,'inputFramesSha256Digest':hashlib.sha256(''.join(f['sha256'] for f in report['frames']).encode()).hexdigest(),'rawFramesRetainedInTemp':True,'normalPlaybackRate':1.0})
  for c in report['critical']:
   if c['direction'] not in (['south','west'] if fps==30 else ['north','east']):continue
   name=f"{a.SLUG}_female-{c['direction']}_idle-{scene}-phase-{c['phase']:02d}-640_v01_{stamp}-{ident}.png"
   rel=bind(a.OUT/name,a.read(raw/c['file']));critical.append({**c,'file':rel,'scene':scene,'fps':fps})
 # Preserve the initial strict diagnostic failure and unchanged-WEST control, not a success rewrite.
 initial=a.OUT/f'{a.SLUG}_female-idle-four_native-report_v01_20261018-175828-280aa3dd.json'
 control=Path(os.environ['TEMP'])/'wb-idle-ora-baseline-5hx42z3u'/f'{a.SLUG}_female-idle_native-ora-baseline-control_v01_{a.STAMP}-{a.ID}.json'
 control_rel=bind(a.OUT/control.name,control.read_bytes().replace(b'\r\n',b'\n'))
 evidence_sources=[AUTHOR,ROOT/'tools/rpg-2-star-ocean-the-second_female-idle-four_native-check_v01_20261018-175418-34294d7d.py',ROOT/'tools/rpg-2-star-ocean-the-second_female-idle-four_actual-playback-capture_test-only-v01_20261018-175418-34294d7d.gd',Path(__file__),ROOT/'tools/rpg-2-star-ocean-the-second_female-idle-four_evidence-check_v01_20261018-175418-34294d7d.py']
 protected=['game/scripts/scifi_exploration_area.gd','game/scripts/survey_annex.gd','game/scripts/character_directional_idle.gd']
 proof={'task':m['task'],'createdAt':datetime.now().astimezone().isoformat(),'baseCommit':subprocess.check_output(['git','rev-parse','86e0c54'],cwd=ROOT).decode().strip(),'baseCommitPurpose':'Canonical game-source anchor reachable from main; no runtime source changes in this producer task','sources':{p.relative_to(ROOT).as_posix():a.sha(a.read(p),True) for p in evidence_sources},'sourceHashAlgorithm':'SHA256 text normalized CRLF to LF','protectedGameSource':{p:a.sha(a.read(ROOT/p),True) for p in protected},'manifest':manifest.relative_to(ROOT).as_posix(),'manifestSha256':a.sha(a.read(manifest)),'nativeReport':native.relative_to(ROOT).as_posix(),'nativeReportSha256':a.sha(a.read(native)),'initialStrictFailure':initial.relative_to(ROOT).as_posix(),'initialStrictFailureSha256':a.sha(a.read(initial)),'oraControl':control_rel,'boundFiles':bound,'captureReports':capture_reports,'movies':movies,'critical':critical,'primaryNativeFormat':'Four animated PXOs; all frame/role native exports exact. Supplemental phase ORAs export exact but diagnostic-clean failed in12/12 jobs, inherited unchanged-WEST control. GUI SaveAs unverified.','uniquePixelPosesPerDirection':8,'timedPhasesPerCycle':12,'maxAuthoredTranslationSourcePixels':1,'maxAuthoredTranslationLogicalPixels':.5,'cycleSeconds':4.8,'artApproved':False,'motionApproved':False,'runtimeIntegrated':False}
 write_json(PROOF,proof);print(PROOF)
if __name__=='__main__':main()
