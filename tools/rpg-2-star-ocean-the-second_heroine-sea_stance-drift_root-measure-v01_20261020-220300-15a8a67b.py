"""Compare the same normal-input traces using authored opaque-sole anchors. Measurements, not art approval.
The samples cover cardinal east/west stances only. Quantized source frames cannot establish exact foot lock.
"""
from pathlib import Path
import datetime, hashlib, json, zipfile
import numpy as np

C=Path(__file__).resolve().parents[1]
OUT=C/'outputs/hsea-root09'


def anchors(folder):
    source=next((C/folder).glob('*/*transition-manifest*.json'))
    # Derive the anchors from the editable leg layer bytes, rather than trusting target metadata.
    result={}
    for facing in ['east','west']:
        pxo=next(source.parent.glob(f'*explore-{facing}-layers*.pxo'))
        result[facing]=[]
        with zipfile.ZipFile(pxo) as archive:
            meta=json.loads(archive.read('data.json'))
            names=[x['name'] for x in meta['layers']]
            for phase in range(12):
                row={'phase':phase}
                for foot in ['near','far']:
                    index=names.index(foot+'-leg')
                    raw=archive.read(f'image_data/frames/{phase+2}/layer_{index+1}')
                    alpha=np.frombuffer(raw,np.uint8).reshape(112,80,4)[:,:,3]
                    ys=np.nonzero(alpha.any(1))[0]
                    xs=np.nonzero(alpha[ys[-1]])[0]
                    row[foot]=[float(xs[0]+xs[-1])/2.0,int(ys[-1])]
                result[facing].append(row)
    return result, source


def measure(trace, art):
    groups={}; previous=None; last_phase=0.0; cycle=0
    for row in trace:
        state=row['state']; facing=state['facing']
        if state['action']!='walk' or facing not in ('east','west'):
            previous=None
            continue
        key=(row['case'],facing)
        phase=float(state['phase'])
        if key!=previous:
            cycle=0
        elif phase<last_phase:
            cycle+=1
        frame=int(state['frame']); foot='near' if frame<6 else 'far'
        anchor=art[facing][frame][foot]
        if anchor is None or anchor[1]!=103:
            continue
        group=groups.setdefault((key[0],facing,cycle,foot),[])
        group.append({'frame':frame,'worldX':float(row['position'][0])+(float(anchor[0])-40.0)/2.0,'hostX':float(row['position'][0])})
        previous=key;last_phase=phase
    return [{'case':k[0],'facing':k[1],'cycle':k[2],'foot':k[3],'sampleCount':len(v),
             'worldXRangeLogical':max(p['worldX'] for p in v)-min(p['worldX'] for p in v),
             'hostXRangeLogical':max(p['hostX'] for p in v)-min(p['hostX'] for p in v),
             'frames':[p['frame'] for p in v]} for k,v in groups.items() if len(v)>=2]


def main():
    tags={'v04':'20261020-215109-5c852157','v06':'20261020-220030-0b3a34af'}
    art={v:anchors(folder) for v,folder in [('v04','outputs/hsea-gait09'),('v06','outputs/hsea-gait11')]}
    records=[]
    for context in ['city','room']:
        runs={}
        for revision,tag in tags.items():
            path=OUT/f'rpg-2-star-ocean-the-second_heroine-sea-distance_{context}-root-proof_v01_{tag}.json'
            runs[revision]=(json.loads(path.read_text(encoding='utf8')),path)
        fields=lambda r:[(x['case'],x['position'],x['state']['action'],x['state']['facing'],x['state']['frame'],x['state']['phase']) for x in r['trace']]
        parity=fields(runs['v04'][0])==fields(runs['v06'][0])
        row={'context':context,'identicalMovementAndPhaseTrace':parity,'versions':{}}
        for revision,(run,path) in runs.items():
            samples=measure(run['trace'],art[revision][0])
            row['versions'][revision]={'trace':path.relative_to(C).as_posix(),'traceSha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'anchorManifest':art[revision][1].relative_to(C).as_posix(),'maxSampledStanceWorldXRangeLogical':max(s['worldXRangeLogical'] for s in samples), 'groups':samples}
        records.append(row)
    tag=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')+'-15a8a67b'
    report={'measuredAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cases':records,
            'method':'Independently decode PXO leg layers; use midpoint of opaque lowest-row bounding span. host world x + (sole x - pivot40)/density2; frame0..5 near /6..11 far. Group only continuous walking/facing/phase cycle.',
            'limits':'Cardinal side stances and sampled frames only; not optical flow, continuous foot lock, front/back quality, fluidity or art approval.'}
    output=OUT/f'rpg-2-star-ocean-the-second_heroine-sea_stance-drift-root-proof_v01_{tag}.json'
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'file':str(output),'summary':[{'context':r['context'],'traceParity':r['identicalMovementAndPhaseTrace'],**{v:round(x['maxSampledStanceWorldXRangeLogical'],4) for v,x in r['versions'].items()}} for r in records]}))
    assert all(r['identicalMovementAndPhaseTrace'] for r in records), 'comparison path/phase differs'


if __name__=='__main__':main()
