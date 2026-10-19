"""Build the SHORT source contract for a complete female exploration motion pilot (read-only over sources).

Hashes: sha256-text-lf-v1 (CRLF->LF only) for .gd/.py/.json/.md text, sha256-bytes for binary (.png/.pxo).
Usage: python -I <this> <repo root> <out json>
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
OUT = Path(sys.argv[2])
TEXT = {'.gd', '.py', '.json', '.md'}


def digest(rel):
    # Extended-length prefix: several source paths exceed MAX_PATH (LongPathsEnabled is 0).
    with open('\\\\?\\' + str((ROOT / rel).resolve()), 'rb') as handle:
        data = handle.read()
    if Path(rel).suffix in TEXT:
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha256(data).hexdigest()


def commit(rel):
    out = subprocess.run(['git', '-C', str(ROOT), 'log', '-1', '--format=%h', '--', rel],
                         capture_output=True, text=True, encoding='utf-8', check=True).stdout.strip()
    if not out:
        raise SystemExit('not committed: ' + rel)
    return out


def entry(rel):
    return {'file': rel, 'sha256': digest(rel), 'commit': commit(rel)}


idle_manifest_rel = 'outputs/female-idle-four-v01/rpg-2-star-ocean-the-second_female-idle-four_direction-manifest_unapproved-v01_20261018-175418-34294d7d.json'
idle = json.loads((ROOT / idle_manifest_rel).read_text(encoding='utf-8'))
idle_dirs = {}
for name, d in idle['directions'].items():
    frames = [f['files']['png']['file'] for f in d['frames']]
    idle_dirs[name] = {'rest_static': entry(d['file']), 'phase_pngs': [entry(f) for f in frames],
                       'unique_rgba_poses': d['uniqueRgbaPoses'], 'pxo': entry(d['pxo']['file'])}

T = 'tools/'
contract = {
    'contract': 'worlds-between.female-complete-exploration-source-contract.v1',
    'status': 'UNSCORED integration-candidate source contract; no art, motion or full-sprite approval',
    'hashEncoding': 'sha256-text-lf-v1 for .gd/.py/.json/.md (CRLF->LF only); sha256-bytes for .png/.pxo',
    'renderScale': 0.5, 'logicalBodyPx': 48, 'sharedPivot': [40, 104],
    'idle': {'task': idle['task'], 'cell': idle['cell'], 'pivot': idle['pivot'], 'cycleSeconds': idle['cycleSeconds'],
             'phaseSeconds': [p['seconds'] for p in idle['phases']], 'phaseNames': [p['name'] for p in idle['phases']],
             'artApproved': idle['artApproved'], 'motionApproved': idle['motionApproved'],
             'manifest': entry(idle_manifest_rel), 'directions': idle_dirs,
             'approval': 'only the SOUTH selout-v8 static is creator-approved; all idle motion and N/W/E art unapproved'},
    'locomotion': {
        'south': {'version': 'v10r1', 'kind': 'inner classes Loco10r1 + Comp10 of test-only SceneTree capture chain',
                  'chain': [entry(T + n) for n in [
                      'rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-godot-capture_m8-w09_20261017-211600-ff47ce98.gd',
                      'rpg-2-star-ocean-the-second_protagonist-female_south-run-v07-godot-capture_m8-w10_20261018-082500-8770ac39.gd',
                      'rpg-2-star-ocean-the-second_female-south-run-v09-godot-capture_m8-w12_20261018-133700-4d620536.gd',
                      'rpg-2-star-ocean-the-second_female-south-run-v10-godot-capture_m8-w13_20261018-143213-ed496e32.gd',
                      'rpg-2-star-ocean-the-second_female-south-run-v10r1-godot-capture_m8-w14_20261018-142136-249dbf66.gd']],
                  'manifest': entry('game/assets/characters/run-v10r1-unapproved/rpg-2-star-ocean-the-second_female-south-run-v10r1_gait-pose-manifest_unapproved_20261018-142136-4b035d3e.json'),
                  'interface': 'setup(manifest, int y); tick(moving: bool, dt_seconds, int pin y) -> {show_v8, state}; comp.compose(state) -> {image, shadow}',
                  'cell': [80, 120], 'separatePartialAlphaShadow': True, 'stride': '128 px, 4.375 steps/s, MOVE_SPEED 140',
                  'status': 'UNAPPROVED / NONRUNTIME; no exported runtime frame set; north input in its harness is a runtime placeholder'},
        'east': {'version': 'v03', 'model': entry(T + 'rpg-2-star-ocean-the-second_female-east_run-stop-source_unapproved-v03_20261018-193030-48da69c1.gd'),
                 'staticPxo': entry('outputs/female-east-static-v01/rpg-2-star-ocean-the-second_protagonist-female_east-layered-source_unapproved-v01_20261018-175114-d55a2ba6.pxo'),
                 'interface': 'advance(delta_s, world_x, intent +1 east) -> state; render_pose(state) -> {full: new 80x112 Image}',
                 'cell': [80, 112], 'pivot': [40, 104], 'cadenceStepsPerSecond': 4.375, 'strideSourcePixels': 128,
                 'bakedNative': '128 run phases + ONE representative 60 fps stop (release phase 60), 15 frames',
                 'status': 'produced, art/motion unapproved; west input was a static placeholder; no reversal claimed'},
        'west': {'version': 'v01 (no west v03 exists in the repository)',
                 'model': entry(T + 'rpg-2-star-ocean-the-second_female-west_run-stop-source_unapproved-v01_20261018-181150-a94f021c.gd'),
                 'staticPxo': entry('outputs/female-west-static-v01/rpg-2-star-ocean-the-second_protagonist-female_west-layered-source_unapproved-v01_20261018-174421-618816ac.pxo'),
                 'interface': 'advance(delta_s, world_x, intent -1 west; intent > 0 => static reverse-placeholder) -> state; render_pose(state)',
                 'cell': [80, 112], 'pivot': [40, 104], 'status': 'produced candidate, unapproved'},
        'north': {'version': 'v06 (supersedes v05 903a75f3; v06 = v05 art + stop/re-press mechanical fix)',
                  'model': entry(T + 'rpg-2-star-ocean-the-second_female-north_run-stop-source_unapproved-v06_20261019-001844-7759f49b.gd'),
                  'staticPxo': entry('game/assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-editable_unapproved-v01_20261018-090713-99e861ce.pxo'),
                  'interface': 'advance(delta_s, world_y, intent +1 north) -> state; render_pose(state) -> {full: new 80x128 Image}',
                  'cell': [80, 128], 'pivot': [40, 104],
                  'bakedNative': '128 run phases + ONE representative 60 fps stop (release phase 25), 17 frames',
                  'status': 'produced, art/motion unapproved'},
    },
    'crossDirectionContract': None,
    'crossDirectionNote': 'No source defines turn/reverse between directions: each model is single-axis and each capture used placeholders for other inputs.',
}
OUT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
print('FCX_CONTRACT_OK', OUT.name)
