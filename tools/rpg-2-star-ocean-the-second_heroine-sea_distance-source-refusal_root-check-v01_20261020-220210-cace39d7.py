"""Real byte-tamper refusal checks; restore owned package files in finally before returning.
Run serially after recording, without editor import in parallel. No account/network access.
"""
from pathlib import Path
import datetime, hashlib, importlib.util, json, subprocess, uuid

C = Path(__file__).resolve().parents[1]
P = C.parents[1]
spec = importlib.util.spec_from_file_location('checked', C/'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py')
checked = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checked)


def main():
    tag = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]
    out = C/'outputs/hsea-root09'
    folder = C/'game/data/hsea-gait11'
    registry = next(folder.glob('*registry*.json'))
    bridge = next(folder.glob('*transition-manifest*.json'))
    png = next((folder/'png').glob('*.png'))
    old = next((C/'game/data/hsea-gait09').glob('*registry*.json'))
    runs = []
    for label, resource, mutate, reg in [('bridge-byte',bridge,True,registry), ('source-png-byte',png,True,registry), ('wrong-revision',None,False,old)]:
        original = resource.read_bytes() if resource else None
        try:
            if mutate:
                resource.write_bytes(original + (b'\n' if resource.suffix == '.json' else b'\x00'))
            log = out/f'rpg-2-star-ocean-the-second_heroine-sea-distance_{label}-refusal_v01_{tag}.log'
            command = [str(P/'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'), '--headless', '--path', str(C/'game'),
                       '--script', str(C/'tools/rpg-2-star-ocean-the-second_heroine-sea_distance-driver_root-fallback-v01_20261020-215430-e2459a30.gd'),
                       '--', 'res://'+reg.relative_to(C/'game').as_posix(), 'refuse']
            result = checked.run_checked(command,25,expected=['SEA_FALLBACK_ROOT_PASS'],log_path=log)
            runs.append({'case':label,'passed':result['passed'],'reason':result['reason'],'log':log.relative_to(C).as_posix()})
            print(label,result['passed'],result['log'][-180:],flush=True)
            assert result['passed'], result['log']
        finally:
            if resource:
                resource.write_bytes(original)
                assert resource.read_bytes() == original, 'restore mismatch'
    report = {'completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':'PASS','cases':runs,
              'allMutatedFilesRestored':True,'scope':'Refusal before any target texture/transform/child mutation; not art acceptance.'}
    target=out/f'rpg-2-star-ocean-the-second_heroine-sea-distance_source-refusal-proof_v01_{tag}.json'
    target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print('SEA_SOURCE_REFUSAL_ROOT_PASS',target)


if __name__=='__main__':
    main()
