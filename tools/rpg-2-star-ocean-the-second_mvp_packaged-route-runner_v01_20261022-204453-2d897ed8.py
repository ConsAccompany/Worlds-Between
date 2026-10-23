"""Run the route55 packaged-PCK scripted-input route check from an empty dir with a fresh isolated profile.

Not a human playtest, normal-speed evidence or approval. Uses the delivered runtime + PCK (--main-pack), never
--path game. Bounded by the existing checked runner (finite deadline, diagnostic-marker stop).
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
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
    a.add_argument('--timeout', type=float, default=300)
    a.add_argument('--native-exe', type=Path, help='Native release executable; no --main-pack is passed')
    a.add_argument('--native-manifest', type=Path, help='Native bundle manifest with files bytes/sha256')
    a.add_argument('--smoke', action='store_true', help='Menu/new game/map/NYC movement/save/quit/reload only')
    args = a.parse_args()
    if args.native_exe:
        help_result = subprocess.run([str(args.native_exe.resolve()), '--help'], capture_output=True, text=True, encoding='utf-8', timeout=15, check=True)
        help_text = re.sub(r'\x1b\[[0-9;]*m', '', help_result.stdout)
        if not any(line.strip().startswith('--script ') for line in help_text.splitlines()):
            raise SystemExit('Native release has no --script option: this external harness cannot test it. Use actual window UI; do not treat an ignored argument as a pass.')
    tag = time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    out = ROOT / ('outputs/native56/root' if args.native_exe else 'outputs/route55/root') / ('r-' + tag)
    run = PROJECT / 'work' / ('r55-' + tag[-8:])
    for path in [out, run / 'cwd', run / 'appdata', run / 'localappdata']:
        path.mkdir(parents=True, exist_ok=False)
    os.environ.update(APPDATA=str(run / 'appdata'), LOCALAPPDATA=str(run / 'localappdata'))
    assert 'ANTHROPIC_API_KEY' not in os.environ
    stop = PROJECT / 'work/dual01/control/rpg-2-star-ocean-the-second_dual-provider_global-stop_v01_20261019-001423-861097ca.json'
    assert not stop.exists(), 'global credit stop'
    godot, pck = GODOT, PCK
    if args.native_exe:
        assert args.native_manifest and args.smoke, 'Native mode requires bound manifest and targeted smoke'
        godot = args.native_exe.resolve()
        pck = godot.with_suffix('.pck')
        manifest = json.loads(args.native_manifest.read_text(encoding='utf-8'))
    else:
        manifest = json.loads((ROOT / 'outputs/play54/producer/rpg-2-star-ocean-the-second_mvp_playtest-manifest_developer_20261022-203718-2fd4b10c.json').read_text(encoding='utf-8'))
    assert sha(pck) == manifest['files'][pck.name]['sha256']
    assert sha(godot) == manifest['files'][godot.name]['sha256']
    os.chdir(run / 'cwd')
    spec = importlib.util.spec_from_file_location('checked', RUNNER)
    checked = importlib.util.module_from_spec(spec); spec.loader.exec_module(checked)
    expected = out / f'rpg-2-star-ocean-the-second_mvp_restart-expected_v01_{tag}.json'
    receipt = {'tag': tag, 'processes': [], 'profile': str(run), 'gameSourceCommit': SOURCE_COMMIT,
               'runtimeSha256': sha(godot), 'pckSha256': sha(pck), 'harnessSha256Raw': sha(HARNESS),
               'runnerSha256Raw': sha(Path(__file__)), 'routeComplete': False, 'humanPlaytest': False,
               'normalSpeedClaim': False, 'artApproved': False}
    phases = [('native-smoke', 'ROUTE55_SAVED_FOR_RESTART'), ('native-reload', 'ROUTE55_ALL_PASS')] if args.smoke else [('journey', 'ROUTE55_SAVED_FOR_RESTART'), ('reload', 'ROUTE55_ALL_PASS')]
    receipt['scope'] = 'native-targeted-smoke' if args.smoke else 'complete-science-route'
    receipt['nativeExecutable'] = bool(args.native_exe)
    for phase, marker in phases:
        assert not stop.exists(), 'global credit stop'
        phase_out = out / phase; phase_out.mkdir()
        command = [str(godot)] + ([] if args.native_exe else ['--main-pack', str(pck)]) + ['--resolution', '640x360', '--audio-driver', 'Dummy',
                   '--fixed-fps', str(args.fps), '--script', str(HARNESS), '--', phase_out.as_posix(), tag,
                   args.language, args.appearance, args.name, phase, expected.as_posix()]
        log = phase_out / f'rpg-2-star-ocean-the-second_route55_godot-log_{tag}.log'
        result = checked.run_checked(command, args.timeout, [marker], str(log))
        report_path = phase_out / f'rpg-2-star-ocean-the-second_route55_report_{tag}.json'
        report = json.loads(report_path.read_text(encoding='utf-8')) if report_path.is_file() else None
        good = result['passed'] and report is not None and not report['failures'] and report['restartReady']
        receipt['processes'].append({'phase': phase, 'command': command, 'cwd': str(run / 'cwd'),
            'passed': bool(good), 'reason': result['reason'], 'exitCode': result['exitCode'],
            'elapsedSeconds': result['elapsedSeconds'], 'processId': (report or {}).get('processId'),
            'failures': (report or {}).get('failures', ['no report written']),
            'report': report_path.relative_to(ROOT).as_posix(), 'log': log.relative_to(ROOT).as_posix()})
        for line in result['log'].splitlines():
            if line.startswith('ROUTE55') or 'ERROR' in line: print(line)
        print('PHASE', phase, bool(good), flush=True)
        if not good: break
    if len(receipt['processes']) == 2 and all(x['passed'] for x in receipt['processes']):
        assert receipt['processes'][0]['processId'] != receipt['processes'][1]['processId']
        receipt['routeComplete'] = True
    target = out / f'rpg-2-star-ocean-the-second_route55_receipt_{tag}.json'
    target.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('RECEIPT', target.relative_to(ROOT).as_posix(), 'COMPLETE', receipt['routeComplete'])
    return 0 if receipt['routeComplete'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
