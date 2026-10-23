"""Bounded audio fixture capture against the shipped native PCK, using editor host for --script."""
from pathlib import Path
import argparse, datetime, hashlib, importlib.util, json, os, uuid

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT.parents[1]
SLUG = 'rpg-2-star-ocean-the-second'


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--themed', action='store_true')
    args = a.parse_args()
    assert not (PRIMARY / 'work/dual01/control/rpg-2-star-ocean-the-second_dual-provider_global-stop_v01_20261019-001423-861097ca.json').exists()
    tag = datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    out = ROOT / 'outputs/audio57/root' / tag
    local = PRIMARY / 'work' / ('a57-' + tag[-8:])
    for d in [out, local / 'app', local / 'local']:
        d.mkdir(parents=True, exist_ok=False)
    os.environ.update(APPDATA=str(local / 'app'), LOCALAPPDATA=str(local / 'local'))
    checker = ROOT / 'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py'
    spec = importlib.util.spec_from_file_location('checked', checker)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    exe = PRIMARY / 'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'
    pck = PRIMARY / 'work/n56t-2ddf51cd/play test/rpg-2-star-ocean-the-second_mvp_native-playtest_unsigned_20261022-211046-8ef48084.pck'
    harness = ROOT / 'tools/rpg-2-star-ocean-the-second_audio_real-mix-capture_test-only-v01_20261022-212657-710850bf.gd'
    kind = 'themed' if args.themed else 'legacy'
    avi = local / f'{SLUG}_audio57_actual-master_{kind}-v01_{tag}.avi'
    report = out / f'{SLUG}_audio57_capture-report_{kind}-v01_{tag}.txt'
    log = out / f'{SLUG}_audio57_godot-log_{kind}-v01_{tag}.log'
    command = [str(exe), '--main-pack', str(pck), '--resolution', '640x360', '--fixed-fps', '60',
               '--write-movie', str(avi), '--script', str(harness), '--', '--out=' + report.as_posix()]
    if args.themed:
        command.append('--themed-music-pilot')
    source = harness.read_bytes()
    snapshot = out / f'{SLUG}_audio57_executed-fixture-source_{kind}-v01_{tag}.gd'
    snapshot.write_bytes(source)
    r = m.run_checked(command, 100, ['AUDIO57_CAPTURE_READY'], str(log))
    r.pop('log', None)
    receipt = {'tag': tag, 'kind': kind, 'command': command, 'harnessSha256': hashlib.sha256(source).hexdigest(),
               'runnerSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'pckSha256': hashlib.file_digest(pck.open('rb'), 'sha256').hexdigest(),
               'localAvi': str(avi), 'report': str(report.with_suffix('.json')), 'result': r,
               'sourceSnapshot': snapshot.relative_to(ROOT).as_posix(), 'humanAudition': False}
    (out / f'{SLUG}_audio57_capture-receipt_{kind}-v01_{tag}.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    (ROOT / f'work/audio57-{kind}-pointer.json').write_text(json.dumps(receipt), encoding='utf-8')
    print(json.dumps(receipt))
    return 0 if r['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
