"""Small companion to the native-bank compositor: actor/provenance/runtime parity.

Negative fixtures are in-memory read overrides; production files are never written.
This checks source contracts, not native application diagnostics, play, or art.
"""
import argparse,hashlib,json,os,uuid,io
from PIL import Image
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
DIRS={'south','west','north','east'}
def lp(p):return Path('\\\\?\\'+str(p.resolve())) if os.name=='nt' else p
def sha(b):return hashlib.sha256(b).hexdigest()

def validate(source,actor,south,overrides=None):
    checks=[];overrides=overrides or {}
    def raw(p):
        p=Path(p).resolve()
        return overrides[p] if p in overrides else lp(p).read_bytes()
    def load(p):return json.loads(raw(p))
    def ck(ok,label):checks.append({'check':label,'passed':bool(ok)})
    try:
        s=load(ROOT/source);pkg=s['package'];contract=s['contract']
        ck(s['visual_id']==actor,'source actor')
        ck(set(s['directions'])==DIRS,'exact source directions')
        ck(contract['cell']==[80,112] and contract['pivot']==[40,104] and contract['density']==2 and contract['logical_height']==48,'native geometry')
        for label,d in [*s['source_inputs'].items(),('author',s['tool']),('helper',s['reused_helpers'])]:
            if 'sha256_text_lf_v1' in d:
                ck(sha(raw(ROOT/d['file']).replace(b'\r\n',b'\n'))==d['sha256_text_lf_v1'],'LF provenance '+label)
            else:ck(sha(raw(ROOT/d['file']))==d['sha256'],'raw provenance '+label)
        ck(s['directions']['south']['static']['exact_source']==south,'caller-pinned original south source')
        original=raw(ROOT/south)
        ck(original==raw(ROOT/s['directions']['south']['static']['file'])==raw(ROOT/s['directions']['south']['idle'][0]['file']),'south static and idle f00 retained exactly')
        registry=load(ROOT/pkg['registry']);runtime_path=ROOT/pkg['sprite_set'];runtime=load(runtime_path)
        stop_path=ROOT/pkg['stop_supplemental'];stop=load(stop_path)
        ck(registry['schema']=='worlds-between.exploration-sprite-set-registry.v1' and set(registry['actors'])=={actor},'exact member registry')
        ck((ROOT/pkg['registry']).parent.joinpath(registry['actors'].get(actor,'')).resolve()==runtime_path.resolve(),'registry points to selected runtime set')
        ck(runtime['schema']=='worlds-between.exploration-sprite-set.v1' and runtime['actor_id']==actor,'runtime schema and actor')
        ck(runtime['frame_size']==contract['cell'] and runtime['pivot']==contract['pivot'] and runtime['density']==contract['density'],'runtime geometry parity')
        ck(sha(raw(runtime_path))==pkg['sprite_set_sha256'],'runtime manifest raw hash')
        ck(sha(raw(stop_path).replace(b'\r\n',b'\n'))==pkg['stop_supplemental_sha256_text_lf_v1'],'stop manifest LF hash')
        ck(stop['schema']=='worlds-between.exploration-stop-transition.supplemental.v1' and stop['actor_id']==actor and stop['pivot']==contract['pivot'],'stop schema actor and pivot')
        ck(stop['logical_height']==48 and stop['frame_ms']==s['walk_model']['frame_ms_reference'],'stop timing parity')
        ck(set(runtime['actions'])=={'idle','walk'} and set(stop['phase_bridges'])==DIRS,'exact runtime banks')
        for action in ['idle','walk']:
            ck(set(runtime['actions'][action])==DIRS,'directions '+action)
        for direction,bank in s['directions'].items():
            if direction in ['south','north']:
                # Read actual pixels, independently of the author's grounded-feet metadata.
                def sole(entry,left):
                    image=Image.open(io.BytesIO(raw(ROOT/entry['file']))).getchannel('A')
                    box=image.crop((0 if left else 40,84,40 if left else 80,112)).getbbox()
                    return box[3]+83 if box else -1
                base={key:sole(bank['static'],left) for key,left in [('ll',True),('rl',False)]}
                frames=bank['walk']+[e for b in bank['stop_bridges'].values() for e in b if 'file' in e]
                for n,frame in enumerate(frames):
                    for key,left in [('ll',True),('rl',False)]:
                        row=sole(frame,left);lift=int(frame['pose'].get(key,0))
                        ck(row==base[key] if lift==0 else 84<=row<base[key],'actual pixel foot contact '+direction+'/'+str(n)+'/'+key)
            for action in ['idle','walk']:
                src=bank[action];dst=runtime['actions'][action][direction]
                ck(len(src)==len(dst)>1,'frame count '+direction+'/'+action)
                expected=s['idle_model']['duration_ms'] if action=='idle' else [s['walk_model']['frame_ms_reference']]*len(src)
                ck([e['duration_ms'] for e in src]==[e['duration_ms'] for e in dst]==expected,'duration parity '+direction+'/'+action)
                for n,(a,b) in enumerate(zip(src,dst)):
                    ck(sha(raw(ROOT/a['file']))==a['sha256']==sha(raw(runtime_path.parent/b['file'])),'runtime PNG parity '+direction+'/'+action+'/'+str(n))
            ck(set(stop['phase_bridges'][direction])==set(bank['stop_bridges']),'stop phase coverage '+direction)
            for phase,bridge in bank['stop_bridges'].items():
                dst=stop['phase_bridges'][direction][phase]
                ck(len(bridge)==len(dst)==4 and bridge[0]==dst[0] and bridge[-1]==dst[-1],'stop endpoints '+direction+'/'+phase)
                for n,(a,b) in enumerate(zip(bridge[1:-1],dst[1:-1])):
                    ck(a['k']==b['k'] and a['sha256']==b['sha256']==sha(raw(ROOT/a['file']))==sha(raw(stop_path.parent/b['file'])),'stop runtime PNG parity '+direction+'/'+phase+'/'+str(n))
    except (KeyError,ValueError,TypeError,OSError) as e:ck(False,'contract exception '+type(e).__name__+': '+str(e))
    return {'passed':bool(checks) and all(x['passed'] for x in checks),'checks':checks}

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--actor',required=True);p.add_argument('--south-source',required=True);p.add_argument('--out-dir',required=True);a=p.parse_args()
    s=json.loads(lp(ROOT/a.manifest).read_bytes());pkg=s['package'];positive=validate(a.manifest,a.actor,a.south_source)
    reg_path=(ROOT/pkg['registry']).resolve();reg=json.loads(lp(reg_path).read_bytes());wrong=dict(reg);wrong['actors']={'wrong-actor':next(iter(reg['actors'].values()))}
    bad_registry=validate(a.manifest,a.actor,a.south_source,{reg_path:json.dumps(wrong).encode()})
    runtime_path=ROOT/pkg['sprite_set'];runtime=json.loads(lp(runtime_path).read_bytes());frame=runtime['actions']['walk']['south'][0]['file'];png=(runtime_path.parent/frame).resolve();data=lp(png).read_bytes()
    bad_copy=validate(a.manifest,a.actor,a.south_source,{png:b'bad'+data[3:]})
    passed=positive['passed'] and not bad_registry['passed'] and not bad_copy['passed']
    tag=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8];out=ROOT/a.out_dir;out.mkdir(parents=True,exist_ok=True)
    proof=out/f'rpg-2-star-ocean-the-second_exploration-source_runtime-parity-proof_test-only-v01_{tag}.json'
    result={'actor':a.actor,'manifest':a.manifest,'manifestSha256Raw':sha(lp(ROOT/a.manifest).read_bytes()),'checkerSha256Raw':sha(Path(__file__).read_bytes()),'positive':positive,'negativeFixtures':{'wrongRegistryActor':bad_registry,'changedRuntimePNG':bad_copy},'fixtureMethod':'In-memory read overrides only; no production files modified.','passed':passed,'artApproved':False,'humanPlaytest':False}
    lp(proof).write_bytes((json.dumps(result,indent=2)+'\n').encode());print('RUNTIME_PARITY',passed,len(positive['checks']),proof.relative_to(ROOT))
    for c in positive['checks']:
        if not c['passed']:print('FAIL',c['check'])
    return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
