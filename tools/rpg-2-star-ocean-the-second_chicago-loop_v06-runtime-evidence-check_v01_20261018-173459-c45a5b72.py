"""Verify exact current Chicago v06 source, native export and real Godot/isolation evidence."""
from pathlib import Path
import hashlib,json,os,re,subprocess
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/chicago-loop-state-lake-v06'
PROOF='rpg-2-star-ocean-the-second_chicago-loop_v06-runtime-evidence-manifest_20261018-173428-fca4766d.json'
def long(path):
    value=str(Path(path).resolve());prefix=chr(92)*2+'?'+chr(92)
    return prefix+value if os.name=='nt' and not value.startswith(prefix) else value
def read(path):return Path(long(path)).read_bytes()
def sha(path,text=False):
    b=read(path);return hashlib.sha256(b.replace(bytes([13,10]),bytes([10])) if text else b).hexdigest()
def main():
    p=json.loads(read(OUT/PROOF))
    for source,value in p['sources'].items():assert sha(ROOT/source,True)==value,source
    for source,value in p['protectedGameSourceEqualsBase'].items():
        assert sha(ROOT/source,True)==value,source
        b=subprocess.check_output(['git','show',p['baseCommit']+':'+source],cwd=ROOT)
        assert hashlib.sha256(b.replace(bytes([13,10]),bytes([10]))).hexdigest()==value,source
    for source,value in p['captureAndLogFiles'].items():assert sha(ROOT/source)==value,source
    native=json.loads(read(ROOT/p['nativeReport']));assert native['passed']==native['total']==15
    assert sha(ROOT/p['nativeReport'])==p['nativeReportSha256']
    manifest=json.loads(read(next(OUT.glob('*layer-manifest*.json'))))
    for value in manifest['files'].values():assert sha(ROOT/value['file'],value.get('hash_algorithm')=='sha256-text-lf-v1')==value['sha256'],value['file']
    reports=list((OUT/'godot-runtime').glob('*harness-report*.json'));assert len(reports)==1
    runtime=json.loads(read(reports[0]));assert runtime['ok'] and runtime['checks']==17 and all(v==0 for v in runtime['diffs'].values()),runtime
    originals=[('outputs/room1-visual-review','011400-d3590c0a'),('outputs/room2-fixtures-pilot','010418-6b3138d8'),('outputs/yonkers-room2-visual-review','011814-94cebca4')]
    differences={}
    for folder,tag in originals:
        for baseline in (ROOT/folder).glob('*_20261017-'+tag+'.png'):
            stem=baseline.name.split('_20261017-')[0];copies=list((OUT/'accepted-replay').glob(stem+'_*.png'));assert len(copies)==1,stem
            a=np.array(Image.open(long(baseline)).convert('RGBA'));b=np.array(Image.open(long(copies[0])).convert('RGBA'));count=int(np.count_nonzero(np.any(a!=b,axis=2)));assert count==0,baseline.name;differences[stem]=count
    assert len(differences)==8
    for path in OUT.glob('*check-log*.txt'):
        text=read(path).decode('utf-8-sig')
        assert not re.search(r'(?m)^(SCRIPT ERROR|ERROR|.*FAIL)',text),path
    replay=''.join(read(p).decode('utf-8-sig') for p in OUT.glob('*accepted-replay-check-log*.txt'))
    assert 'ACCEPTED_REPLAY_CHICAGO_V06_OVERRIDE textures=6' in replay and 'ACCEPTED_REPLAY_ALL_OK' in replay
    assert replay.count('_INTERACTIONS_OK 3')==3
    assert not p['humanArtApproved']
    print('CHICAGO V06 EVIDENCE PASS: source/native15, realGodot17, 8acceptedroom0px/9clues, exact source and capture hashes; unapproved nonruntime')
if __name__=='__main__':main()
