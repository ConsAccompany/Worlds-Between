"""Verify current VFX plus combat loader source-bound evidence, not historical art approval."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'outputs/vfx-capability_20261018-172526-e9e7344f'
def sha(path,text=False):
    b=path.read_bytes()
    return hashlib.sha256(b.replace(b'\r\n',b'\n') if text else b).hexdigest()
def main():
    v=json.loads((DIR/'rpg-2-star-ocean-the-second_battle-vfx_capability-report_v01_20261018-172526-e9e7344f.json').read_text())
    c=json.loads((DIR/'rpg-2-star-ocean-the-second_combat-set-pilot_capture-manifest_20261018-172542-b9cf9e3e.json').read_text())
    assert v['checks']==53 and v['sourceHashAlgorithm']=='sha256-text-lf-v1'
    for path,value in v['sources'].items():assert sha(ROOT/path.replace('res://','game/'),True)==value,path
    for field,path in {'battleScriptSha256':'game/scripts/battle_arena.gd','helperSha256':'game/scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd','checkScriptSha256':c['checkScript']}.items():assert sha(ROOT/path,True)==c[field],path
    assert len(v['captures'])==10 and len(c['captures'])==12
    for capture in v['captures']+c['captures']:assert sha(DIR/capture['file'])==capture['sha256'],capture['file']
    assert {x['case'] for x in v['captures']}=={'attack','dodge','guard','hit','heal'}
    for x in v['captures']:assert x['outsidePixels']==0 and 0<x['changedPixels']<=160
    for x in v['report']['simulationParity']:assert x['steps']==600 and x['snapshotsEqual'] and x['onEffects']>0
    for x in c['report']['simulationParity'].values():assert x['traceSha256']==x['baseCommitTraceSha256'] and x['firstDifferentStep']==-1 and x['saveSnapshotEqual']
    for key,x in c['report']['flagOffRenders'].items():
        if isinstance(x,dict):assert sha(DIR/x['file'])==x['sha256'] and x['sha256']==x['baseSha256']
    for filename in ['rpg-2-star-ocean-the-second_battle-vfx_runtime-check-log_v01_20261018-172526-e9e7344f.txt','rpg-2-star-ocean-the-second_battle-vfx_combined-loader-check-log_v01_20261018-172542-b9cf9e3e.txt']:
        text=(DIR/filename).read_text(encoding='utf-8-sig')
        assert not re.search(r'(?m)^(SCRIPT ERROR|ERROR|FAIL|WARNING:.*leaked)',text),filename
        assert 'PASS checks=' in text,filename
    assert not v['artApproved'] and v['healLimitation']
    print('VFX COMBINED EVIDENCE PASS: current sources, 22 bilingual captures, 5 local effects, VFX/loader combat parity, clean logs and unchanged default renders')
if __name__=='__main__':main()
