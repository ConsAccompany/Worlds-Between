from pathlib import Path
import json,subprocess,sys,importlib.util,numpy as np,hashlib
c=Path(__file__).resolve().parents[3]
tool=c/'tools/rpg-2-star-ocean-the-second_audio_movie-pcm-read_v01_20261022-212657-710850bf.py'
spec=importlib.util.spec_from_file_location('pcm57',tool);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for kind in ['legacy','themed']:
 r=json.loads((c/f'work/audio57-{kind}-pointer.json').read_text(encoding='utf-8'));assert r['result']['passed'];f=Path(r['report']);out=f.parent;tag=r['tag'];wav=out/f'rpg-2-star-ocean-the-second_audio57_actual-mix_{kind}-v01_{tag}.wav';stat=out/f'rpg-2-star-ocean-the-second_audio57_pcm-read_{kind}-v01_{tag}.json'
 if not stat.exists():
  p=subprocess.run([sys.executable,str(tool),'--avi',r['localAvi'],'--wav',str(wav),'--output',str(stat)],capture_output=True,text=True,encoding='utf-8');assert p.returncode==0,p.stderr
 prior=json.loads(stat.read_text(encoding='utf-8'));assert prior['wavSha256']==hashlib.sha256(wav.read_bytes()).hexdigest();assert prior['toolSha256']==hashlib.sha256(tool.read_bytes()).hexdigest()
 x,raw,info,_=m.read_avi(r['localAvi']);s=json.loads(f.read_text(encoding='utf-8'));rate=info['rate'];ph=s['phases'];segments={}
 for i,p in enumerate(ph):
  start=p['frame']/60;end=ph[i+1]['frame']/60 if i+1<len(ph) else s['final_frame']/60
  if i<3:segments[p['phase']]=m.stats(x[int((start+.3)*rate):int((end-.2)*rate)])
 for cue in s['cues']:
  start=cue['frame']/60;segments['cue:'+cue['event']]=m.stats(x[int(start*rate):int((start+.4)*rate)])
 segments['last_silence']=m.stats(x[int((s['final_frame']/60-.65)*rate):int((s['final_frame']/60-.15)*rate)])
 a=segments['A_music100']['rms'];b=segments['B_music50_restart0']['rms'];ratio=b/a if a else None
 checks={'nonzeroMusic':a>1e-5,'masterHalfGain':ratio is not None and .465<=ratio<=.535,'masterMutePostmixZero':segments['C_master0_music_playing']['allZero'],'11CuesHaveActualNonzeroOutput':all(segments['cue:'+q['event']]['rms']>1e-5 for q in s['cues']),'noFullScaleClip':np.max(np.abs(x))<.9999,'finalSilenceZero':segments['last_silence']['allZero'],'readyNotOnlyDispatch':s['status']=='READY','samePlayerRestart':s['restart_same_player_instance_id']==s['restart_same_player_after_instance_id']};checks={k:bool(v) for k,v in checks.items()}
 proof={'sourceCommit':'f1d2faca0a353cc2d916351eaac69ee8897850bc','gameSourceCommit':'d5f204373c17c62e45e92dea14c3a2e85c525062','pckSha256':r['pckSha256'],'harnessSha256':r['harnessSha256'],'readerSha256':hashlib.sha256(tool.read_bytes()).hexdigest(),'evaluationSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'kind':kind,'captureReceipt':str(out/f'rpg-2-star-ocean-the-second_audio57_capture-receipt_{kind}-v01_{tag}.json'),'wav':str(wav),'wavSha256':hashlib.sha256(wav.read_bytes()).hexdigest(),'aviSha256':info['aviSha256'],'audioInfo':info,'halfGainRatio':ratio,'checks':checks,'segments':segments,'allTechnicalChecksPassed':all(checks.values()),'actualListeningPerformed':False,'audioQaGatePassed':False,'thresholdsPredeclared':{'halfGainMin':.465,'halfGainMax':.535,'nonzeroRmsMin':1e-5,'clippingAbsMax':.9999,'silenceExactZero':True},'limitations':'Offline movie mix, scene fixture plus direct cue APIs, not ordinary input or physical speaker listening; city music contexts only'}
 target=out/f'rpg-2-star-ocean-the-second_audio57_output-verdict_{kind}-v01_{tag}.json';target.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(kind,'ratio',ratio,'checks',checks,'diagnostics',info['probeDiagnostics'],info['decoderDiagnostics'])
