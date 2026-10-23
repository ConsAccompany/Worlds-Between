"""Hermes independent Lin Que bank reconciliation; no defaults or visual approval.

Preserves Claude's author/source bytes and DeepSeek's checker. Reuses existing
raw-native checker separately. All SHA256 values are raw bytes except fields
explicitly named text_lf_v1 (CRLF/CR replaced by LF).
"""
import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import subprocess
import time
import zipfile

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
INCOMING = ROOT.parent / 'incoming/lexplore59'
TAG = '20261023-050631-c52d784a'
PREFIX = 'rpg-2-star-ocean-the-second_lin-que'
OUT = ROOT / 'outputs/lexplore59/hermes61'
AUTHOR = 'rpg-2-star-ocean-the-second_lin-que_exploration-source-author_unapproved-lexplore59-v01_20261022-231558-6875dc75.py'
MANIFEST = 'outputs/lexplore59/rpg-2-star-ocean-the-second_lin-que_explore-source-manifest_unapproved-lexplore59-v01_20261022-231558-7d9a8dba.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def receipt(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / f'{PREFIX}_{name}_technical-v01_{TAG}.json'
    with target.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    print(target.relative_to(ROOT), flush=True)


def materialize():
    raw = (INCOMING / 'incoming-manifest.json').read_bytes()
    manifest = json.loads(raw)
    entries = manifest['files']
    assert len(entries) == 346 and len({e['path'] for e in entries}) == 346
    planned = []
    for entry in entries:
        path = PurePosixPath(entry['path'])
        assert not path.is_absolute() and '..' not in path.parts and '\\' not in entry['path']
        assert str(path).startswith(('outputs/lexplore59/', 'game/data/lexplore59/', 'tools/', 'docs/qa/'))
        src, dst = INCOMING / path, ROOT / path
        assert not src.is_symlink() and src.resolve().is_relative_to(INCOMING.resolve())
        assert dst.resolve().is_relative_to(ROOT)
        assert not any(p.is_symlink() for p in [dst, *dst.parents] if p.is_relative_to(ROOT))
        payload = src.read_bytes()
        assert len(payload) == entry['bytes'] and sha(payload) == entry['sha256'], str(path)
        state = 'identical' if dst.exists() else 'absent'
        if dst.exists():
            assert dst.is_file() and dst.read_bytes() == payload, f'CONFLICT {path}'
        planned.append((entry, dst, payload, state))
    # Entire preflight finishes before the first write; exclusive creation never overwrites.
    before = {}
    for name in subprocess.check_output(['git', 'ls-files', '-z', 'game'], cwd=ROOT).decode().split('\0'):
        if name:
            before[name] = sha((ROOT / name).read_bytes())
    for entry, dst, payload, state in planned:
        if state == 'absent':
            dst.parent.mkdir(parents=True, exist_ok=True)
            with dst.open('xb') as stream:
                stream.write(payload)
        assert sha(dst.read_bytes()) == entry['sha256']
    receipt('materialization', {
        'base': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
        'incomingManifestSha256Raw': sha(raw), 'entries': len(planned),
        'created': sum(s == 'absent' for _, _, _, s in planned),
        'byteIdenticalExisting': sum(s == 'identical' for _, _, _, s in planned),
        'files': entries, 'protectedTrackedGameFiles': before,
        'attribution': {'sourceAuthor': 'Claude (completed PC producer)',
                        'packageChecker': 'DeepSeek (completed PC producer)',
                        'reconciliationAndIndependentValidation': 'Hermes'},
        'ordinaryDefaultsChanged': False})
    print('MATERIALIZED', len(planned), flush=True)


def source():
    spec = importlib.util.spec_from_file_location('lin_bank', ROOT / 'tools' / AUTHOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pins_before = module.J.pins_state()
    sets, files, data = module.build_all()
    _, again, _ = module.build_all()
    deterministic = files.keys() == again.keys() and all(b == again[k] for k, b in files.items())
    listing = f'{module.OUT_REL}/{module.fname("file-list", "json")}'
    files[listing] = (json.dumps({'run': f'{module.STAMP}-{module.RUN}', 'hash': 'sha256-bytes',
                               'files': {p: sha(b) for p, b in sorted(files.items())}}, indent=2) + '\n').encode()
    matches = {name: (ROOT / name).read_bytes() == payload for name, payload in files.items()}
    checks = module.J.source_checks(sets, files, data)
    pins_after = module.J.pins_state()
    # Do not rewrite the historical producer check-result.
    result = {'rebuild': {'checked': len(matches), 'passed': sum(matches.values()),
                         'mismatches': [p for p, ok in matches.items() if not ok]},
              'deterministic': deterministic, 'sourceChecks': checks,
              'pinsBefore': pins_before, 'pinsAfter': pins_after,
              'manifestSha256Raw': sha((ROOT / MANIFEST).read_bytes()),
              'authorSha256Raw': sha((ROOT / 'tools' / AUTHOR).read_bytes()),
              'authorSha256TextLfV1': data['tool']['sha256_text_lf_v1'],
              'hashRule': 'raw SHA256; text_lf_v1 normalizes CRLF and CR to LF only',
              'attribution': 'Claude author; Hermes reruns deterministic reconstruction and source checks',
              'passed': all(matches.values()) and deterministic and all(c['pass'] for c in checks)
                        and all(pins_before.values()) and all(pins_after.values())}
    receipt('source-reproduction', result)
    print('SOURCE', result['rebuild'], sum(c['pass'] for c in checks), '/', len(checks), flush=True)
    assert result['passed']


def contacts():
    data = json.loads((ROOT / MANIFEST).read_bytes())
    checks, results = [], {}
    for direction, bank in data['directions'].items():
        with zipfile.ZipFile(ROOT / bank['pxo']['file']) as archive:
            native = json.loads(archive.read('data.json'))
            layers = {l['name']: i + 1 for i, l in enumerate(native['layers'])}
            def cel(frame, layer):
                return np.frombuffer(archive.read(f'image_data/frames/{frame + 1}/layer_{layers[layer]}'), np.uint8).reshape(112, 80, 4)
            def feet(frame):
                boots = cel(frame, 'boots')
                if direction in ('west', 'east') and frame > 4:
                    return [boots[103, :, 3] == 255, cel(frame, 'far-limbs')[103, :, 3] == 255]
                if direction in ('west', 'east'):
                    f = (np.arange(80) - 40) * (1 if direction == 'east' else -1)
                    return [(boots[103, :, 3] == 255) & (f <= 5), (boots[103, :, 3] == 255) & (f > 5)]
                return [(boots[103, :, 3] == 255) & (np.arange(80) < 40), (boots[103, :, 3] == 255) & (np.arange(80) >= 40)]
            def toe(mask):
                x = np.flatnonzero(mask)
                return int(x.min() if direction == 'west' else x.max()) if len(x) else None
            walk = [feet(i) for i in range(5, 17)]
            slip, stop_slip = [], []
            sign = -1 if direction == 'west' else 1
            for phase in range(12):
                for foot in range(2):
                    a, b = toe(walk[phase][foot]), toe(walk[(phase + 1) % 12][foot])
                    if a is not None and b is not None:
                        if direction in ('west', 'east'):
                            # Near toe AND heel, far toe only (occluded far heel is not certified).
                            values = [abs(sign * (b - a) + 11.2)]
                            if foot == 0:
                                aa, bb = np.flatnonzero(walk[phase][foot]), np.flatnonzero(walk[(phase + 1) % 12][foot])
                                values.append(abs(sign * (int(bb.max() if sign < 0 else bb.min()) - int(aa.max() if sign < 0 else aa.min())) + 11.2))
                            slip.append(max(values))
                        else:
                            slip.append(11.2)
                seq = [walk[phase], feet(17 + phase * 2), feet(18 + phase * 2), feet(1)]
                for a, b in zip(seq, seq[1:]):
                    for foot in range(2):
                        x, y = toe(a[foot]), toe(b[foot])
                        if x is not None and y is not None:
                            stop_slip.append(abs(y - x))
                            if foot == 0 and direction in ('west', 'east'):
                                aa, bb = np.flatnonzero(a[foot]), np.flatnonzero(b[foot])
                                stop_slip.append(abs(int(aa.min()) - int(bb.min())))
            boundary = round(max(slip), 3)
            settle = max(stop_slip)
            claimed = data['contact_check'][direction]
            checks.append({'check': direction + ' independent raw-cel measured contact agrees',
                           'passed': boundary == claimed['walk_max_world_slip_src_at_40ms_boundaries']
                           and settle == claimed['stop_bridge_grounded_slip_src_max'] == 0})
            results[direction] = {'boundaryWorldSlipSourcePx': boundary, 'boundaryWorldSlipLogicalPx': boundary / 2,
                                  'stopGroundedSlipSourcePx': settle, 'groundedPairs': len(slip),
                                  'flightPhases': [p for p, pair in enumerate(walk) if not any(m.any() for m in pair)],
                                  'disclosed60fpsExcursionSourcePx': claimed['walk_planted_foot_world_excursion_src_60fps_samples']}
    result = {'manifestSha256Raw': sha((ROOT / MANIFEST).read_bytes()), 'method': 'No author imports: raw native boots/far-limbs sole row103; side near toe+heel, far toe; front/back split x40. Host140 logical px/s, density2,40ms. Not a full outline/occlusion/continuous footlock pass.',
              'checks': checks, 'contacts': results, 'fullFootlockPassed': False, 'passed': all(c['passed'] for c in checks)}
    receipt('independent-contact', result)
    print('CONTACT', json.dumps(results), flush=True)
    assert result['passed']


def native():
    data = json.loads((ROOT / MANIFEST).read_bytes())
    runs = []
    for direction, bank in data['directions'].items():
        run = OUT / ('native-' + direction + '-' + TAG)
        run.mkdir(parents=True, exist_ok=False)
        state = ROOT.parent / 'handoff' / (PREFIX + '_native-app-' + direction + '_v01_' + TAG)
        state.mkdir(exist_ok=False)
        env = dict(os.environ)
        for key in ('DATA', 'CONFIG', 'CACHE'):
            folder = state / key.lower()
            folder.mkdir()
            env['XDG_' + key + '_HOME'] = str(folder)
        src = ROOT / bank['pxo']['file']
        before = sha(src.read_bytes())
        command = [os.environ['PIXELORAMA'], '--headless', '--audio-driver', 'Dummy', '--quit', '--', '--export', '-o', str(run / ('requested_' + TAG + '.png')), str(src)]
        started = time.monotonic()
        process = subprocess.Popen(command, cwd=run, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
        timeout = False
        try:
            log = process.communicate(timeout=90)[0]
        except subprocess.TimeoutExpired:
            timeout = True
            os.killpg(process.pid, signal.SIGKILL)
            log = process.communicate()[0]
        logfile = OUT / f'{PREFIX}_native-{direction}_v01_{TAG}.log'
        logfile.write_bytes(log)
        actual = sorted(run.glob('*.png'), key=lambda p: [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', p.name)])
        order = [bank['static'], *bank['idle'], *bank['walk']]
        order.extend(e for p in range(12) for e in bank['stop_bridges']['phase' + str(p)][1:3])
        equal, outputs = 0, []
        for index, path in enumerate(actual):
            got = Image.open(path).convert('RGBA')
            expected = Image.open(ROOT / order[index]['file']).convert('RGBA') if index < len(order) else None
            exact = expected is not None and got.size == expected.size and got.tobytes() == expected.tobytes()
            equal += exact
            outputs.append({'actualSavedName': path.name, 'sha256Raw': sha(path.read_bytes()), 'rgbaSha256': sha(got.tobytes()), 'size': list(got.size), 'frameIndex': index, 'source': order[index] if index < len(order) else None, 'rgbaExact': exact})
            if exact:
                renamed = run / f'{PREFIX}_native-{direction}-f{index:02d}_unapproved-v01_{TAG}.png'
                path.rename(renamed)
                outputs[-1]['file'] = renamed.relative_to(ROOT).as_posix()
        text = log.decode('utf-8', 'replace')
        diagnostics = [line for line in text.splitlines() if any(s in line for s in ('ERROR:', 'SCRIPT ERROR', 'Parse Error', 'WARNING:'))]
        result = {'direction': direction, 'command': command, 'exit': process.returncode, 'timeout': timeout,
                  'elapsedSeconds': round(time.monotonic() - started, 3), 'nativeSourceSha256Before': before,
                  'nativeSourceSha256After': sha(src.read_bytes()), 'expectedFrames': len(order), 'actualFrames': len(actual), 'exactFrames': equal,
                  'outputs': outputs, 'log': logfile.relative_to(ROOT).as_posix(), 'diagnostics': diagnostics,
                  'applicationClean': process.returncode == 0 and not timeout and not diagnostics,
                  'guiSaveAsReopenVerified': False,
                  'sourceExportPassed': process.returncode == 0 and not timeout and len(actual) == len(order) == equal and sha(src.read_bytes()) == before}
        receipt('native-' + direction, result)
        runs.append(result)
        print('NATIVE', direction, 'exact', equal, '/', len(order), 'diagnostics', len(diagnostics), flush=True)
    receipt('native-summary', {'runs': [{k:v for k,v in run.items() if k != 'outputs'} for run in runs], 'sourceExportPassed': all(r['sourceExportPassed'] for r in runs), 'applicationClean': all(r['applicationClean'] for r in runs), 'guiSaveAsReopenVerified': False})
    assert all(r['sourceExportPassed'] for r in runs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['materialize', 'source', 'contacts', 'native'])
    args = parser.parse_args()
    globals()[args.mode]()
