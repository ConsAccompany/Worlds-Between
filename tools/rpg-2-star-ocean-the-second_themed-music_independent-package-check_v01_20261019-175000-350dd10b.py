"""Independent score/MIDI/PCM validation; no hearing, aesthetic or authorship claim."""
import argparse, collections, hashlib, importlib.util, io, json, shutil, struct, subprocess, sys, wave
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
TAG='20261019-175000-350dd10b'
rows=[]
def ck(key, value): rows.append({'key':key,'pass':bool(value)})
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def vlq(data,p):
    value=0
    for _ in range(4):
        b=data[p];p+=1;value=(value<<7)|(b&127)
        if not b&128:return value,p
    raise ValueError('VLQ longer than four bytes')
def parse_midi(blob):
    assert blob[:4]==b'MThd'
    length,fmt,tracks,division=struct.unpack('>IHHH',blob[4:14]);assert length==6
    p=8+length; result=[]
    for _ in range(tracks):
        assert blob[p:p+4]==b'MTrk';size=int.from_bytes(blob[p+4:p+8],'big');data=blob[p+8:p+8+size];p+=8+size
        q=tick=0;status=None;events=[]
        while q<len(data):
            delta,q=vlq(data,q);tick+=delta
            if data[q]&128:status=data[q];q+=1
            assert status is not None
            if status==255:
                kind=data[q];q+=1;n,q=vlq(data,q);payload=data[q:q+n];q+=n;events.append((tick,'meta',kind,payload));status=None
            elif status in (240,247):
                n,q=vlq(data,q);q+=n;status=None
            else:
                kind=status>>4;ch=status&15;n=1 if kind in (12,13) else 2
                payload=data[q:q+n];assert len(payload)==n;q+=n
                events.append((tick,kind,ch,tuple(payload)))
        assert q==len(data)
        result.append(events)
    assert p==len(blob)
    return fmt,division,result
def validate(package, out, rebuild):
    manifest_path=next(package.glob('*manifest*.json'));m=json.loads(manifest_path.read_text(encoding='utf-8'))
    source=package/m['source']['path'];ck('source-raw-hash',sha(source)==m['source']['sha256'])
    ck('four-distinct-subjects',len(m['tracks'])==4 and len({r['subject'] for r in m['tracks']})==4)
    expected_tempos={'city':76,'town':76,'field':92,'ruins':62,'battle':116}
    lead_signatures=[];audio_hashes=[];track_metrics=[];total_wav=0
    module=None
    if rebuild:
        spec=importlib.util.spec_from_file_location('frozen_music_author',source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    for rec in m['tracks']:
        key=rec['subject'];score=json.loads((package/rec['files']['score']['path']).read_text(encoding='utf-8'))
        for role,item in rec['files'].items():
            p=package/item['path'];ck(key+'-'+role+'-raw-hash',sha(p)==item['sha256']);ck(key+'-'+role+'-size',p.stat().st_size==item['bytes'])
        bpm=score['tempo_bpm'];expected=next((v for k,v in expected_tempos.items() if key.startswith(k)),None)
        ck(key+'-tempo-contract',bpm==expected and rec['tempo_bpm']==bpm)
        ck(key+'-sixteen-bars-4-4-480ppq',score['bars']==16 and score['beats_per_bar']==4 and score['ticks_per_quarter']==480 and score['ticks_per_bar']==1920 and score['meter']=='4/4')
        ck(key+'-loop-full64beats',score['loop_start_tick']==0 and score['loop_end_tick']==30720)
        ck(key+'-four-section-boundaries',[(s['start_tick'],s['end_tick']) for s in score['structure']]==[(0,7680),(7680,15360),(15360,23040),(23040,30720)])
        ck(key+'-sixteen-harmony-bars',[h['bar'] for h in score['harmony']]==list(range(1,17)))
        notes=[n for p in score['parts'] for n in p['notes']]
        ck(key+'-note-count',len(notes)==score['notes_total']==rec['notes_total'])
        ck(key+'-notes-in-loop-and-midi-range',all(isinstance(n['start_tick'],int) and isinstance(n['duration_ticks'],int) and 0<=n['start_tick']<30720 and 0<n['duration_ticks']<=30720-n['start_tick'] and 0<=n['midi']<=127 and 1<=n['velocity']<=127 for n in notes))
        lead=next(p['notes'] for p in score['parts'] if p['name']=='lead')
        first=[n for n in lead if n['start_tick']<1920];origin=first[0]['midi']
        signature=[(n['start_tick'],n['duration_ticks'],n['midi']-origin) for n in first]
        lead_signatures.append(signature)
        fmt,division,tracks=parse_midi((package/rec['files']['midi']['path']).read_bytes())
        ck(key+'-midi-format1-480',fmt==1 and division==480)
        ck(key+'-midi-part-track-count',len(tracks)==len(score['parts'])+1)
        metas=[e for t in tracks for e in t if e[1]=='meta']
        tempos=[(e[0],int.from_bytes(e[3],'big')) for e in metas if e[2]==81]
        ck(key+'-midi-exact-tempo',tempos==[(0,round(60000000/bpm))])
        ck(key+'-midi-meter',[(e[0],e[3]) for e in metas if e[2]==88]==[(0,bytes([4,2,24,8]))])
        ck(key+'-midi-all-end-of-tracks',all([(e[0],e[3]) for e in t if e[1]=='meta' and e[2]==47]==[(30720,b'')] for t in tracks))
        for part,track in zip(score['parts'],tracks[1:]):
            channel=score['instruments'][part['instrument']]['midi_channel']
            expected_on=collections.Counter((n['start_tick'],channel,n['midi'],n['velocity']) for n in part['notes'])
            expected_off=collections.Counter((n['start_tick']+n['duration_ticks'],channel,n['midi']) for n in part['notes'])
            actual_on=collections.Counter((e[0],e[2],e[3][0],e[3][1]) for e in track if e[1]==9 and e[3][1]>0)
            actual_off=collections.Counter((e[0],e[2],e[3][0]) for e in track if e[1]==8 or e[1]==9 and e[3][1]==0)
            ck(key+'-'+part['name']+'-exact-midi-note-on',actual_on==expected_on)
            ck(key+'-'+part['name']+'-exact-midi-note-off',actual_off==expected_off)
        wav_path=package/rec['files']['wav']['path'];blob=wav_path.read_bytes();audio_hashes.append(hashlib.sha256(blob).hexdigest());total_wav+=len(blob)
        with wave.open(io.BytesIO(blob),'rb') as f:
            ck(key+'-pcm-wave-format',f.getnchannels()==2 and f.getsampwidth()==2 and f.getframerate()==24000 and f.getcomptype()=='NONE')
            frames=f.getnframes();raw=f.readframes(frames)
        ck(key+'-exact-sample-count',frames==round(64*60/bpm*24000)==rec['wav']['frames']==rec['loop']['end_frame'])
        ck(key+'-expected-duration',abs(frames/24000-64*60/bpm)<=.5/24000)
        pcm=np.frombuffer(raw,dtype='<i2').reshape((-1,2));signal=pcm.astype(np.float64)/32768
        peak=float(np.abs(signal).max());dc=signal.mean(axis=0);rms=float(np.sqrt(np.mean(signal**2)))
        ck(key+'-peak-headroom',0<peak<=.85)
        ck(key+'-zero-clipped-samples',not np.any((pcm==32767)|(pcm==-32768)))
        ck(key+'-dc-under1e-5',np.max(np.abs(dc))<=1e-5)
        ck(key+'-exact-zero-endpoints',np.all(pcm[0]==0) and np.all(pcm[-1]==0))
        ck(key+'-stereo-not-duplicated-mono',np.any(pcm[:,0]!=pcm[:,1]))
        ck(key+'-under8MB',len(blob)<8000000)
        ck(key+'-metrics-match-manifest',abs(peak-rec['metrics']['peak_linear'])<1e-9 and abs(rms-rec['metrics']['rms_linear'])<1e-9 and abs(dc[0]-rec['metrics']['dc_offset_left'])<1e-12 and abs(dc[1]-rec['metrics']['dc_offset_right'])<1e-12)
        if module:
            midi,_=module.build_midi(score);rebuilt_pcm,_=module.render_track(score,int(score['render']['seed']));wav=module.wav_bytes(rebuilt_pcm,24000)
            ck(key+'-deterministic-midi-byte-equality',midi==(package/rec['files']['midi']['path']).read_bytes())
            ck(key+'-deterministic-wav-byte-equality',wav==blob)
            (out/(key+'-rebuilt.mid')).write_bytes(midi);(out/(key+'-rebuilt.wav')).write_bytes(wav)
        track_metrics.append({'subject':key,'bpm':bpm,'notes':len(notes),'frames':frames,'seconds':frames/24000,'peak':peak,'rms':rms,'dc':dc.tolist(),'openingLeadRelativeMotif':signature,'wavSha256':sha(wav_path)})
    ck('four-distinct-relative-opening-motifs',len({json.dumps(s) for s in lead_signatures})==4)
    ck('four-distinct-wave-files',len(set(audio_hashes))==4)
    ck('total-wavs-under24MB',total_wav<24000000 and total_wav==m['totals']['wav_bytes'])
    return {'tag':TAG,'manifest':str(manifest_path),'manifestRawSha256':sha(manifest_path),'sourceRawSha256':sha(source),'checks':rows,'count':len(rows),'failed':[r['key'] for r in rows if not r['pass']],'tracks':track_metrics,'listened':False,'artisticQualityClaim':False,'creatorApproval':False,'limitations':['Distinct note patterns and PCM do not certify aesthetic quality or originality against all existing music.','No audio listening or subjective loop/mix judgment performed.','Renderer byte rebuild uses frozen producer source; independent parsers establish score/MIDI/PCM relationships.']}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('package',type=Path);parser.add_argument('--label',default='original');parser.add_argument('--rebuild',action='store_true');args=parser.parse_args()
    fixture=ROOT/'work'/('musn-'+TAG[-8:]+'-'+args.label);fixture.mkdir(parents=True,exist_ok=True)
    # Freeze bytes, not symlinks; producer package remains read-only while another worker revises it.
    for p in args.package.iterdir():
        if p.is_file() and p.suffix in ('.json','.py','.mid','.wav','.txt'):shutil.copyfile(p,fixture/p.name)
    rebuild=fixture/'rebuilt';rebuild.mkdir(exist_ok=True)
    report=validate(fixture,rebuild,args.rebuild)
    out=ROOT/'outputs/themed-music-v01';out.mkdir(parents=True,exist_ok=True)
    name=f'rpg-2-star-ocean-the-second_themed-music_independent-{args.label}-report_v01_{TAG}.json';(out/name).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('MUSIC_INDEPENDENT',report['count']-len(report['failed']),'/',report['count'],'PASS' if not report['failed'] else 'FAIL',report['failed'])
    sys.exit(bool(report['failed']))
