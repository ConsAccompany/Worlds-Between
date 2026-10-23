"""Run the route55 packaged-PCK scripted-input route check from an empty dir with a fresh isolated profile.

Not a human playtest, normal-speed evidence or approval. Uses the delivered runtime + PCK (--main-pack), never
--path game. Bounded by the existing checked runner (finite deadline, diagnostic-marker stop).
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
RUNNER = ROOT / 'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py'
HARNESS = ROOT / 'tools/rpg-2-star-ocean-the-second_mvp_packaged-route-input-check_v01_20261022-204453-2d897ed8.gd'
BUNDLE = PROJECT / 'work/p54-c1425087/play test'
GODOT = BUNDLE / 'Godot_v4.7.2-stable_win64_console.exe'
PCK = BUNDLE / 'rpg-2-star-ocean-the-second_mvp_playtest-pack_developer_20261022-203718-2fd4b10c.pck'
SOURCE_COMMIT = 'd5f204373c17c62e45e92dea14c3a2e85c525062'


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--language', choices=['zh', 'en'], default='zh')
    a.add_argument('--appearance', choices=['female', 'male'], default='female')
    a.add_argument('--name', default='Lin')
    a.add_argument('--fps', type=int, choices=[30, 60], default=60)
    a.add_argument('--timeout', type=float, default=180)
    args = a.parse_args()
    tag = time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    out = ROOT / 'outputs/route55/producer' / ('r-' + tag)
    run = ROOT / 'work/route55' / tag
    for path in [out, run / 'cwd', run / 'appdata', run / 'localappdata']:
        path.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ)
    env['APPDATA'] = str(run / 'appdata')
    env['LOCALAPPDATA'] = str(run / 'localappdata')
    env.pop('ANTHROPIC_API_KEY', None)
    os.environ.update({'APPDATA': env['APPDATA'], 'LOCALAPPDATA': env['LOCALAPPDATA']})
    os.chdir(run / 'cwd')
    spec = importlib.util.spec_from_file_location('checked', RUNNER)
    checked = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checked)
    command = [str(GODOT), '--main-pack', str(PCK), '--resolution', '640x360', '--audio-driver', 'Dummy',
               '--fixed-fps', str(args.fps), '--script', str(HARNESS), '--',
               out.as_posix(), tag, args.language, args.appearance, args.name]
    log = out / f'rpg-2-star-ocean-the-second_route55_godot-log_{tag}.log'
    result = checked.run_checked(command, args.timeout, ['ROUTE55_DONE'], str(log))
    report_path = out / f'rpg-2-star-ocean-the-second_route55_report_{tag}.json'
    report = json.loads(report_path.read_text(encoding='utf-8')) if report_path.is_file() else None
    receipt = {
        'tag': tag, 'processes': [{'phase': 'session-1', 'passed': result['passed'], 'reason': result['reason'],
                                   'exitCode': result['exitCode'], 'elapsedSeconds': result['elapsedSeconds']}],
        'command': command, 'cwd': str(run / 'cwd'), 'profile': str(run), 'fixedFps': args.fps,
        'gameSourceCommit': SOURCE_COMMIT,
        'runtimeSha256': sha(GODOT), 'pckSha256': sha(PCK),
        'harnessSha256Raw': sha(HARNESS), 'runnerSha256Raw': sha(Path(__file__)),
        'reportPresent': report is not None,
        'furthestCheckpoint': ([c['label'] for c in (report or {}).get('checkpoints', []) if 'status' not in c] or [None])[-1],
        'failures': (report or {}).get('failures', ['no report written']),
        'rawErrorLines': [l for l in result['log'].splitlines() if 'ERROR' in l or 'SCRIPT_ERROR' in l][:200],
        'routeComplete': False, 'humanPlaytest': False, 'normalSpeedClaim': False, 'artApproved': False,
    }
    target = out / f'rpg-2-star-ocean-the-second_route55_receipt_{tag}.json'
    target.write_bytes((json.dumps(receipt, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))
    for line in result['log'].splitlines():
        if line.startswith('ROUTE55') or 'ERROR' in line:
            print(line)
    print('ROUTE55_RUN', 'PROCESS_PASS' if result['passed'] else 'PROCESS_FAIL', result['reason'], tag, result['elapsedSeconds'])
    print('RECEIPT', target)
    return 0 if result['passed'] and report and not report['failures'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
