"""Independently verify the current portable developer ZIP in a clean, short path.

Usage: python <tool> outputs/play54/producer/<successful-build-report>.json
Runs external scene fixtures against the actual PCK, never the source project.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib, importlib.util, json, os, shutil, sys, uuid, zipfile

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT.parents[1]
SLUG = 'rpg-2-star-ocean-the-second'
TOOL_TAG = '20261022-202347-7fea20f0'
PROBE = ROOT / f'tools/{SLUG}_mvp_packed-defaults-probe_test-only-v01_{TOOL_TAG}.gd'
RUNNER = ROOT / 'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py'
STOP = PRIMARY / 'work/dual01/control/rpg-2-star-ocean-the-second_dual-provider_global-stop_v01_20261019-001423-861097ca.json'


def lp(p):
    s = str(Path(p).resolve())
    return Path(s if s.startswith('\\\\?\\') else '\\\\?\\' + s)


def sha(p):
    h = hashlib.sha256()
    with lp(p).open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    assert not STOP.exists(), 'global stop'
    source_report = ROOT / sys.argv[1]
    build = json.loads(source_report.read_text(encoding='utf-8'))
    assert build['passed'] is True
    tag = datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    dest = PRIMARY / 'work' / ('p54-' + tag[-8:])
    assert not dest.exists(), 'unique delivery folder required'
    dest.mkdir()
    output = ROOT / 'outputs/play54/root' / tag
    output.mkdir(parents=True)
    manifest = json.loads(lp(ROOT / build['manifest']).read_text(encoding='utf-8'))
    assert manifest['sourceCommit'] == build['sourceCommit']
    assert sha(ROOT / manifest['builder']) == manifest['builderSha256']
    zip_source = ROOT / build['zip']
    assert sha(zip_source) == build['zipSha256']
    delivered_zip = dest / zip_source.name
    shutil.copy2(lp(zip_source), lp(delivered_zip))
    assert sha(delivered_zip) == build['zipSha256']
    play = dest / 'play test'
    play.mkdir()
    with zipfile.ZipFile(lp(delivered_zip)) as z:
        assert z.testzip() is None
        members = z.infolist()
        assert len(members) == len(manifest['files']) + 1
        for item in members:
            path = Path(item.filename)
            assert len(path.parts) == 2 and path.name not in ('.', '..')
            assert path.parts[0] == f'{SLUG}_playtest_' + build['tag']
            with z.open(item) as src, lp(play / path.name).open('xb') as out:
                shutil.copyfileobj(src, out)
    for name, info in manifest['files'].items():
        assert sha(play / name) == info['sha256']
        assert lp(play / name).stat().st_size == info['bytes']
    assert sha(play / Path(build['manifest']).name) == sha(ROOT / build['manifest'])
    empty = dest / 'empty'
    empty.mkdir()
    os.environ['APPDATA'] = str(dest / 'profile')
    os.environ['LOCALAPPDATA'] = str(dest / 'local')
    os.environ['WB_PLAY54_EMPTY'] = str(empty)
    spec = importlib.util.spec_from_file_location('checked', RUNNER)
    checked = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checked)
    pck = next(play.glob('*.pck'))
    console = play / 'Godot_v4.7.2-stable_win64_console.exe'
    report = {'startedUtc': datetime.now(timezone.utc).isoformat(), 'sourceCommit': build['sourceCommit'],
              'buildReport': source_report.relative_to(ROOT).as_posix(), 'buildReportSha256': sha(source_report),
              'zipSha256': sha(delivered_zip), 'zipBytes': delivered_zip.stat().st_size,
              'verifiedBundleFileCount': len(manifest['files']) + 1,
              'localDeliveryZip': str(delivered_zip), 'localPlayDirectory': str(play),
              'sourceProjectUsed': False, 'profileIsolated': True,
              'probeSha256': sha(PROBE), 'verifierSha256': sha(__file__), 'steps': [],
              'humanPlaytest': False, 'artApproval': False, 'nativeReleaseExport': False}
    old = Path.cwd()
    try:
        os.chdir(empty)
        commands = [
            ('normal-launcher', f'cmd /d /s /c ""{play / manifest["launchers"]["normal"]}" --headless --quit-after 10"', 45, []),
            ('packed-contexts', [str(console), '--path', str(empty), '--main-pack', str(pck), '--resolution', '640x360',
                                 '--max-fps', '60', '--audio-driver', 'Dummy', '--script', str(PROBE), '--', str(output), tag],
             120, ['PLAY54_PACKED_DEFAULTS_OK'])]
        for name, command, deadline, markers in commands:
            assert not STOP.exists(), 'global stop'
            log = output / f'{SLUG}_mvp_{name}-log_v01_{tag}.log'
            result = checked.run_checked(command, deadline, expected=markers, log_path=log)
            raw = result.pop('log')
            report['steps'].append({'name': name, 'command': command, 'cwd': str(empty),
                                    'log': log.relative_to(ROOT).as_posix(), **result})
            print(name, result, flush=True)
            if not result['passed']:
                print(raw[-2500:], flush=True)
                raise RuntimeError(name + ' failed')
        probe_report = next(output.glob('*packed-defaults-report*.json'))
        actual = json.loads(probe_report.read_text(encoding='utf-8'))
        assert len(actual['captures']) == 20
        assert actual['checks'] and all(c['pass'] for c in actual['checks'])
        report['actualPackedChecks'] = actual['count']
        report['actualPackedCaptures'] = len(actual['captures'])
        report['probeReport'] = probe_report.relative_to(ROOT).as_posix()
        before = json.loads((ROOT / 'work/play54-before.json').read_text(encoding='utf-8'))
        drift = [name for name, digest in before['files'].items() if sha(ROOT / name) != digest]
        assert not drift, 'protected game changed: ' + str(drift[:5])
        report['protectedGameFilesUnchanged'] = len(before['files'])
        report['passed'] = True
    except Exception as e:
        report.update(passed=False, failure=type(e).__name__ + ': ' + str(e))
    finally:
        os.chdir(old)
    report['endedUtc'] = datetime.now(timezone.utc).isoformat()
    receipt = output / f'{SLUG}_mvp_portable-verification_v01_{tag}.json'
    receipt.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'passed': report['passed'], 'receipt': receipt.relative_to(ROOT).as_posix(),
                      'zip': str(delivered_zip), 'play': str(play)}, indent=2))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
