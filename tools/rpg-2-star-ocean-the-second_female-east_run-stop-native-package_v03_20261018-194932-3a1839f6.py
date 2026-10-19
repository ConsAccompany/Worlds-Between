"""Package the v03 EAST run/stop advance() cels into editable PXOs and independently reopen them.

Follows the WEST v01 packager conventions (south-run-v06 PXO writer, v8 guide layout, 12 named
role layers + hidden locked guides, 70 fps x 0.25 run cels = 128/280 s). EAST stop is the bake's
representative 60 fps settle (fps 60, 1-duration cels). Full 128-frame PNG/RGBA bake stays in Temp;
the PXOs hold every cel and the manifest stores per-frame hashes. Only the six critical native
poses are copied to outputs/. Pixelorama exactness and Pixelorama diagnostics are reported
separately: inherited headless shader-compiler errors are NOT a clean-app result.

Usage (checkout root, Codex-runtime Python 3.12): python -I <this> <bake temp folder>
Text hashes sha256-text-lf-v1 (CRLF->LF); binary sha256-bytes.
"""
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
import json, hashlib, io, zipfile, os, subprocess, re, sys, tempfile
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'rpg-2-star-ocean-the-second'
TAG = 'v03_20261018-194932-3a1839f6'
OUT = ROOT / 'outputs/female-east-run-v03'
CORE = 'tools/rpg-2-star-ocean-the-second_female-east_run-stop-source_unapproved-v03_20261018-193030-48da69c1.gd'
CORE_SHA = 'e783de5d8ab6b1e3f678299eb8cffde11109d1aab06c47155831ebc4388bb07f'
BAKE = 'tools/rpg-2-star-ocean-the-second_female-east_run-stop-native-bake_test-only-v03_20261018-194932-3a1839f6.gd'
WRITER = 'tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py'
NORTH = 'tools/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-build-and-check_unapproved-v01_20261018-090713-9af15df7.py'
EAST = 'outputs/female-east-static-v01/rpg-2-star-ocean-the-second_protagonist-female_east-layered-source_unapproved-v01_20261018-175114-d55a2ba6.pxo'
SOUTH = 'outputs/female-idle-four-v01/rpg-2-star-ocean-the-second_female-south_idle-phase-00_unapproved-v01_20261018-175418-34294d7d.png'
PIXELORAMA = ROOT / '../tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe'
KNOWN = re.compile(r'ERROR: Condition "!actions\.custom_samplers\.has\(function->arguments\[j\]\.tex_builtin\)" is true\. Continuing\.\s+at: _dump_node_code \(servers/rendering/shader_compiler\.cpp:1329\)')
CRITICAL_RUN = [('contact', 0), ('passing', 19), ('flight', 51)]


def long(p):
    s = str(Path(p).resolve()); prefix = chr(92) * 2 + '?' + chr(92)
    return prefix + s if os.name == 'nt' and not s.startswith(prefix) else s


def read(p): return Path(long(p)).read_bytes()
def write(p, b): Path(long(p)).write_bytes(b)
def sha(b): return hashlib.sha256(b).hexdigest()
def tsha(b): return sha(b.replace(b'\r\n', b'\n'))
def rgba(b): return np.array(Image.open(io.BytesIO(b)).convert('RGBA'))


def mod(p, n):
    s = spec_from_file_location(n, ROOT / p); m = module_from_spec(s); s.loader.exec_module(m); return m


def main():
    folder = Path(sys.argv[1])
    bake = json.loads(read(folder / f'{SLUG}_female-east-run_native-bake-report_{TAG}.json'))
    core_before = sha(read(ROOT / CORE))
    assert core_before == CORE_SHA == bake['modelSha256Before'] == bake['modelSha256After'], 'model hash'
    assert not bake['problems'] and bake['allStopFinalsExact']
    OUT.mkdir(parents=True, exist_ok=True)
    writer = mod(WRITER, 'east_run_pxo_writer'); native = mod(NORTH, 'east_run_guides')
    writer.W, writer.H = 80, 112
    writer.to_rgba = lambda a: np.ascontiguousarray(a, np.uint8)
    east = zipfile.ZipFile(io.BytesIO(read(ROOT / EAST)))
    east_data = json.loads(east.read('data.json'))
    roles = [x['name'] for x in east_data['layers'] if x['name'] != 'guides'] + ['guides']
    east_static = Image.new('RGBA', (80, 112))
    for i, layer in enumerate(east_data['layers']):
        if layer['name'] != 'guides':
            east_static.alpha_composite(Image.frombytes('RGBA', (80, 112), east.read(f'image_data/frames/1/layer_{i + 1}')))
    east_static = np.array(east_static)
    palette = {tuple(x) for x in rgba(read(ROOT / SOUTH)).reshape(-1, 4) if x[3]}
    pin = tuple(native.v8t.PIN)
    manifest = {
        'task': 'content.char.protagonist-female.walk-east', 'artApproved': False, 'motionApproved': False, 'runtimeIntegrated': False,
        'cell': [80, 112], 'pivot': [40, 104], 'scale': .5, 'cadenceStepsPerSecond': 4.375, 'strideSourcePixels': 128, 'contactSourcePixels': 38,
        'flightSeconds': 26 / 280, 'guidePin': list(pin),
        'sourceHashEncoding': 'sha256-text-lf-v1 for .py/.gd (CRLF->LF only); sha256-bytes for binary assets',
        'sources': {p: (tsha(read(ROOT / p)) if p.endswith(('.py', '.gd')) else sha(read(ROOT / p))) for p in [CORE, BAKE, WRITER, NORTH, EAST, SOUTH]},
        'modelSha256Bytes': core_before, 'layers': roles, 'sets': {},
        'bake': {'runReference': bake['runReference'], 'stopReference': bake['stopReference'], 'representativeStop': bake['representativeStop'],
                 'stopScan60Phases': len(bake['stopScan60']), 'allStopFinalsExact': bake['allStopFinalsExact']},
        'scope': 'One EAST run (128 real advance() phases at the 280 Hz reference) and one representative 60 fps stop (worst final-settle phase). '
                 'WEST reversal shows the produced WEST static placeholder only; no WEST motion. Live presentation rasterizes the same controller; '
                 'at 30/60 fps the v03 torso step guard can hold the torso 1 source px from the 280 Hz cel for a frame (see capture evidence).',
        'fullFramePngsTempOnly': str(folder)}
    gates = {}
    jobs = []
    critical = []
    for kind in ['run', 'stop']:
        rows = [r for r in bake['poses'] if r['kind'] == kind]
        frames = []; records = []
        for row in rows:
            data = read(folder / row['full']['file']); image = rgba(data); parts = {}
            assert sha(data) == row['full']['sha256'] and sha(image.tobytes()) == row['full']['rgbaSha256']
            for role in roles[:-1]:
                raw = read(folder / row['roles'][role]['file']); assert sha(raw) == row['roles'][role]['sha256']
                parts[role] = np.frombuffer(raw, np.uint8).reshape(112, 80, 4).copy()
            full = Image.new('RGBA', (80, 112))
            for role in roles[:-1]: full.alpha_composite(Image.fromarray(parts[role]))
            key = f'{kind}:{row["index"]}'
            gates[key + ':roles_compose_full'] = bool(np.array_equal(np.array(full), image))
            gates[key + ':binary_alpha'] = set(np.unique(image[:, :, 3])) <= {0, 255} and all(set(np.unique(parts[r][:, :, 3])) <= {0, 255} for r in roles[:-1])
            gates[key + ':approved_palette'] = {tuple(x) for x in image.reshape(-1, 4) if x[3]} <= palette
            gates[key + ':no_edge_texels'] = not np.any(image[[0, -1], :, 3]) and not np.any(image[:, [0, -1], 3])
            parts['guides'] = native.v8t.guides_rgba(image)   # refuses guide/sprite overlap
            gates[key + ':guide_pin'] = parts['guides'][pin[1], pin[0], 3] == 255
            frames.append(parts)
            records.append({'index': row['index'], 'state': row['state'], 'alphaBoundsExclusive': list(Image.fromarray(image).getbbox()),
                            'tempPng': row['full']['file'], 'pngSha256': row['full']['sha256'], 'rgbaSha256': row['full']['rgbaSha256'],
                            'rolesSha256': {r: sha(parts[r].tobytes()) for r in roles}})
        fps = 70. if kind == 'run' else 60.
        durations = [.25 if kind == 'run' else 1.] * len(frames)
        export_name = f'{SLUG}_female-east-{kind}_native-export_{TAG}'
        raw = writer.make_pxo(frames, durations, read(folder / rows[0]['full']['file']), export_name, fps, order=roles, dt=(2026, 10, 18, 19, 49, 32))
        z0 = zipfile.ZipFile(io.BytesIO(raw)); out = io.BytesIO()
        with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
            for info in z0.infolist():
                data = z0.read(info.filename)
                if info.filename == 'data.json':
                    d = json.loads(data); d['layers'][-1]['visible'] = False; d['layers'][-1]['locked'] = True
                    d['tags'] = [{'name': 'east-' + kind, 'from': 1, 'to': len(frames), 'color': '1a9999'}]
                    d['user_data'] = ('Unapproved EAST v03 %s: real advance() poses of model e783de5d, binary alpha, 80x112, pivot40/104, scale0.5. '
                                      'No runtime adoption.' % kind)
                    data = json.dumps(d, separators=(',', ':')).encode()
                z.writestr(info, data)
        pxo = out.getvalue()
        path = OUT / f'{SLUG}_female-east-{kind}_animated-source_unapproved-{TAG}.pxo'; write(path, pxo)
        # Reopen our own bytes: metadata + every cel equals the source role.
        zr = zipfile.ZipFile(io.BytesIO(read(path))); dr = json.loads(zr.read('data.json'))
        gates[kind + ':pxo_metadata'] = (dr['size_x'], dr['size_y']) == (80, 112) and len(dr['frames']) == len(frames) and dr['fps'] == fps and \
            [x['duration'] for x in dr['frames']] == durations and [x['name'] for x in dr['layers']] == roles and \
            not dr['layers'][-1]['visible'] and dr['layers'][-1]['locked'] and all(x['visible'] for x in dr['layers'][:-1])
        gates[kind + ':pxo_cels_exact'] = all(zr.read(f'image_data/frames/{i + 1}/layer_{j + 1}') == frames[i][r].tobytes()
                                              for i in range(len(frames)) for j, r in enumerate(roles))
        manifest['sets'][kind] = {'pxo': {'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(pxo)}, 'fps': fps, 'durations': durations,
                                  'frames': records, 'seconds': sum(durations) / fps}
        # Independent Pixelorama 1.2.3 process; never the user's open editor or settings.
        temp = Path(tempfile.mkdtemp(prefix='wb-e3-' + kind + '-')); (temp / 'x').mkdir()
        env = dict(os.environ); env['APPDATA'] = str(temp / 'app'); env['LOCALAPPDATA'] = str(temp / 'local')
        inp = temp / ('east-' + kind + '.pxo'); inp.write_bytes(pxo)
        proc = subprocess.run([str(PIXELORAMA.resolve()), '--headless', '--quit', '--', '--export', '--split-layers', '-o', str(temp / 'x' / f'e3{kind}.png'), str(inp)],
                              env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300,
                              creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        files = list((temp / 'x').glob('*.png')); matches = {}
        for i, parts in enumerate(frames):
            for role in roles[:-1]:
                hits = [p for p in files if '(' + role + ')' in p.name and p.name.endswith(f'_{i + 1:04d}.png')]
                matches[role + '/' + str(i)] = len(hits) == 1 and np.array_equal(rgba(read(hits[0])), parts[role])
        known = KNOWN.findall(proc.stderr)
        residual = KNOWN.sub('', proc.stderr).strip()
        gates[kind + ':pixelorama_exit0'] = proc.returncode == 0
        gates[kind + ':pixelorama_export_exact'] = bool(matches) and all(matches.values()) and len(files) == len(matches)
        gates[kind + ':pixelorama_guides_not_exported'] = not any('(guides)' in p.name for p in files)
        gates[kind + ':pixelorama_no_unexpected_diagnostics'] = residual == '' and 'SCRIPT ERROR' not in proc.stdout
        jobs.append({'kind': kind, 'exit': proc.returncode, 'cells': len(matches), 'exact': sum(matches.values()), 'exportedFiles': len(files),
                     'knownInheritedShaderDiagnostics': len(known), 'unexpectedDiagnostics': residual,
                     'cleanAppSuccess': proc.stderr.strip() == '', 'stdout': proc.stdout, 'stderr': proc.stderr, 'tempOnlyExports': str(temp)})
        # Separate critical native PNGs (exact bake bytes).
        pick = CRITICAL_RUN if kind == 'run' else []
        if kind == 'stop':
            rs = bake['representativeStop']; n = len(rows)
            pick = [('lastmoving', rs['lastMovingFrame']), ('penultimate', n - 2), ('final', n - 1)]
        for label, index in pick:
            row = rows[index]
            name = (f'{SLUG}_female-east-run_native-{label}-q{index:03d}_{TAG}.png' if kind == 'run' else
                    f'{SLUG}_female-east-stop_native-{label}-60fps-f{index:02d}-q{bake["representativeStop"]["phase"]:03d}_{TAG}.png')
            data = read(folder / row['full']['file']); write(OUT / name, data)
            critical.append({'kind': kind, 'purpose': label, 'index': index, 'file': (OUT / name).relative_to(ROOT).as_posix(), 'sha256': sha(data),
                             'rgbaSha256': row['full']['rgbaSha256'], 'stopAge': row['state'].get('stopAge'), 'mode': row['state']['mode']})
    stop_rows = manifest['sets']['stop']['frames']
    gates['stop:final_equals_east_static_composite'] = stop_rows[-1]['rgbaSha256'] == sha(east_static.tobytes())
    gates['stop:final_equals_east_static_preview'] = stop_rows[-1]['rgbaSha256'] == sha(rgba(east.read('preview.png')).tobytes())
    gates['stop:first_is_running_release'] = stop_rows[0]['state']['mode'] == 'run' and stop_rows[-1]['state']['mode'] == 'idle'
    manifest['critical'] = critical
    heights = [r['alphaBoundsExclusive'][3] - r['alphaBoundsExclusive'][1] for e in manifest['sets'].values() for r in e['frames']]
    manifest['visibleExtentSourceHeightRange'] = [min(heights), max(heights)]
    manifest['staticDisplayBaselineLogicalPixels'] = 48
    gates['model_hash_unchanged'] = sha(read(ROOT / CORE)) == core_before
    gates = {k: bool(v) for k, v in gates.items()}
    mpath = OUT / f'{SLUG}_female-east-run-stop_native-source-manifest_unapproved-{TAG}.json'
    write(mpath, (json.dumps(manifest, indent=2) + '\n').encode('utf-8'))
    report = {'passed': sum(bool(v) for v in gates.values()), 'total': len(gates), 'failedGates': [k for k, v in gates.items() if not v], 'gates': gates,
              'native': jobs, 'manifestSha256': sha(read(mpath)), 'modelSha256Before': core_before, 'modelSha256After': sha(read(ROOT / CORE)),
              'artApproved': False, 'motionApproved': False, 'nativeGuiSaveAsVerified': False,
              'diagnosticsPolicy': 'Exact export is gated. Known inherited headless shader-compiler diagnostics are counted and kept verbatim; '
                                   'they are not a clean-app success (cleanAppSuccess false whenever stderr is non-empty). Any other diagnostic fails.'}
    rpath = OUT / f'{SLUG}_female-east-run-stop_native-report_{TAG}.json'
    write(rpath, (json.dumps(report, indent=2) + '\n').encode('utf-8'))
    print(rpath); print('gates', report['passed'], '/', report['total'], report['failedGates'][:10])
    for j in jobs: print(j['kind'], 'exit', j['exit'], 'exact', j['exact'], '/', j['cells'], 'known', j['knownInheritedShaderDiagnostics'], 'unexpected', repr(j['unexpectedDiagnostics'][:200]), 'clean', j['cleanAppSuccess'])
    if report['failedGates']: raise SystemExit(1)


if __name__ == '__main__':
    main()
