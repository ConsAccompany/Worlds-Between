"""v06 copy of the v05 packager re-bound to the frozen v06 model (binding/tag/labels only; every gate unchanged).
Package the NORTH v05 run/stop advance() cels into editable PXO + ORA sources and independently reopen them.

Follows the EAST v03 / WEST v01 packager conventions (south-run-v06 PXO writer, named role layers + hidden
locked guides, 70 fps x 0.25-duration run cels = 128/280 s; stop = the bake's representative 60 fps settle,
fps 60, 1-duration cels). NORTH cell is 80x128, pivot 40/104, display scale 0.5 (static body 96 source rows
= 48 logical px). Role layers are the 13 layers of the produced NORTH static pilot .pxo 99e861ce.
ORA: one layered strip per set (cells left to right, roles + hidden guides), for editors without PXO.
Pixelorama exactness and Pixelorama diagnostics are reported separately: inherited headless shader-compiler
diagnostics are NOT a clean-app result; GUI Save As is not verified.

Usage (checkout root, Codex-runtime Python 3.12): python -I <this> <bake temp folder> [<second bake folder>]
The optional second bake (an independent re-run of the bake tool) must be byte-identical (exact rebuild).
Text hashes sha256-text-lf-v1 (CRLF->LF); binary sha256-bytes.
"""
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
import json, hashlib, io, zipfile, os, subprocess, re, sys, tempfile
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'rpg-2-star-ocean-the-second'
TAG = 'v06_20261019-004238-ad92c263'
OUT = ROOT / 'outputs/female-north-run-v06'
CORE = 'tools/rpg-2-star-ocean-the-second_female-north_run-stop-source_unapproved-v06_20261019-001844-7759f49b.gd'
CORE_SHA = '1f25c2aac2837d14a21eb2c8ddd60f93c19f2570cd486716003394e6f7789562'
BAKE = 'tools/rpg-2-star-ocean-the-second_female-north_run-stop-native-bake_test-only-v06_20261019-004238-ad92c263.gd'
WRITER = 'tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py'
V8TOOL = 'tools/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-pxo-source-roundtrip_m8-v08_20261015-080907-05c22e55.py'
V8TOOL_SHA_LF = '53d492fb9e4a7cbd9cdc8991a105140cd8a23aa507040d888993310323754f73'
NORTH_PXO = ('game/assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/'
             'rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-editable_unapproved-v01_20261018-090713-99e861ce.pxo')
NORTH_PNG = ('game/assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/'
             'rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot_unapproved-v01_20261018-090713-6ed8d8dd.png')
# Approved SOUTH v8 palette source: the short committed copy (same bytes as the v8 candidate PNG, see the WEST
# long-path correction note); its hash is pinned.
SOUTH = 'outputs/female-idle-four-v01/rpg-2-star-ocean-the-second_female-south_idle-phase-00_unapproved-v01_20261018-175418-34294d7d.png'
SOUTH_SHA = 'ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd'
PIXELORAMA = ROOT / '../tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe'
KNOWN = re.compile(r'ERROR: Condition "!actions\.custom_samplers\.has\(function->arguments\[j\]\.tex_builtin\)" is true\. Continuing\.\s+at: _dump_node_code \(servers/rendering/shader_compiler\.cpp:1329\)')
W, H, PIN, BODY_ROWS = 80, 128, (40, 104), (8, 103)
GUIDE_RGB = (255, 0, 255)
CRITICAL_RUN = [('contact', 0), ('passing', 10), ('late-stance', 19), ('peel', 20), ('peel-b', 24), ('flight', 40), ('tucked-sole', 64)]
STAMPED = ['pack', 'canister', 'straps', 'bedroll', 'collar', 'hair']
ZIP_DT = (2026, 10, 19, 0, 42, 38)


def long(p):
    s = str(Path(p).resolve()); prefix = chr(92) * 2 + '?' + chr(92)
    return prefix + s if os.name == 'nt' and not s.startswith(prefix) else s


def read(p): return Path(long(p)).read_bytes()
def write(p, b): Path(long(p)).write_bytes(b)
def sha(b): return hashlib.sha256(b).hexdigest()
def tsha(b): return sha(b.replace(b'\r\n', b'\n'))
def rgba(b): return np.array(Image.open(io.BytesIO(b)).convert('RGBA'))
def png(a):
    out = io.BytesIO(); Image.fromarray(np.ascontiguousarray(a, np.uint8), 'RGBA').save(out, 'PNG', optimize=False); return out.getvalue()


def mod(p, n):
    s = spec_from_file_location(n, ROOT / p); m = module_from_spec(s); s.loader.exec_module(m); return m


def guides(full):
    g = np.zeros((H, W, 4), np.uint8); pts = set()
    pts.update((x, 0) for x in range(W)); pts.update((x, H - 1) for x in range(W))
    pts.update((0, y) for y in range(H)); pts.update((W - 1, y) for y in range(H))
    for y in BODY_ROWS: pts.update((x, y) for x in list(range(1, 7)) + list(range(W - 7, W - 1)))
    pts.add(PIN)
    for x, y in pts: g[y, x, :3] = GUIDE_RGB; g[y, x, 3] = 255
    overlap = bool((full[..., 3][g[..., 3] > 0] != 0).any())
    return g, overlap


def make_ora(frames, roles, merged):
    """Layered strip: cell i occupies x = i*W .. i*W+W-1. Top layer listed first (ORA order)."""
    n = len(frames); sw = W * n
    stack = ['<?xml version="1.0" encoding="UTF-8"?>', f'<image version="0.0.3" w="{sw}" h="{H}" xres="72" yres="72">', '<stack>']
    for name in reversed(roles):
        vis = 'hidden' if name == 'guides' else 'visible'
        stack.append(f'<layer name="{name}" src="data/{name}.png" x="0" y="0" opacity="1.0" visibility="{vis}" composite-op="svg:src-over"/>')
    stack += ['</stack>', '</image>']
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        z.writestr(zipfile.ZipInfo('mimetype', ZIP_DT), 'image/openraster', zipfile.ZIP_STORED)
        z.writestr(zipfile.ZipInfo('stack.xml', ZIP_DT), '\n'.join(stack) + '\n', zipfile.ZIP_DEFLATED)
        for name in roles:
            strip = np.concatenate([f[name] for f in frames], axis=1)
            z.writestr(zipfile.ZipInfo(f'data/{name}.png', ZIP_DT), png(strip), zipfile.ZIP_DEFLATED)
        mstrip = np.concatenate(merged, axis=1)
        z.writestr(zipfile.ZipInfo('mergedimage.png', ZIP_DT), png(mstrip), zipfile.ZIP_DEFLATED)
        th = Image.fromarray(mstrip[:, :min(sw, 256)]); tb = io.BytesIO(); th.save(tb, 'PNG')
        z.writestr(zipfile.ZipInfo('Thumbnails/thumbnail.png', ZIP_DT), tb.getvalue(), zipfile.ZIP_DEFLATED)
    return buf.getvalue()


def build_pxo(writer, frames, durations, preview, kind, fps, roles):
    export_name = f'{SLUG}_female-north-{kind}_native-export_{TAG}'
    raw = writer.make_pxo(frames, durations, preview, export_name, fps, order=roles, dt=ZIP_DT)
    z0 = zipfile.ZipFile(io.BytesIO(raw)); out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for info in z0.infolist():
            data = z0.read(info.filename)
            if info.filename == 'data.json':
                d = json.loads(data); d['layers'][-1]['visible'] = False; d['layers'][-1]['locked'] = True
                d['tags'] = [{'name': 'north-' + kind, 'from': 1, 'to': len(frames), 'color': '1a9999'}]
                d['user_data'] = ('Unapproved NORTH v06 %s: real advance() poses of model 1f25c2aa, binary alpha, 80x128, pivot40/104, '
                                  'scale0.5. No runtime adoption.' % kind)
                data = json.dumps(d, separators=(',', ':')).encode()
            z.writestr(info, data)
    return out.getvalue()


def main():
    folder = Path(sys.argv[1]); second = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    bname = f'fn-native-bake-report_{TAG}.json'
    bake = json.loads(read(folder / bname))
    core_before = sha(read(ROOT / CORE))
    assert core_before == CORE_SHA == bake['modelSha256Before'] == bake['modelSha256After'], 'model hash'
    assert not bake['problems'] and bake['allStopFinalsExact']
    assert tsha(read(ROOT / V8TOOL)) == V8TOOL_SHA_LF
    OUT.mkdir(parents=True, exist_ok=True)
    writer = mod(WRITER, 'north_run_pxo_writer')
    writer.W, writer.H = W, H
    writer.to_rgba = lambda a: np.ascontiguousarray(a, np.uint8)
    north = zipfile.ZipFile(io.BytesIO(read(ROOT / NORTH_PXO)))
    north_data = json.loads(north.read('data.json'))
    roles = [x['name'] for x in north_data['layers'] if x['name'] != 'guides'] + ['guides']
    assert roles[:-1] == bake['roleOrder'], (roles, bake['roleOrder'])
    static_roles = {}
    north_static = Image.new('RGBA', (80, 112))
    for i, layer in enumerate(north_data['layers']):
        if layer['name'] != 'guides':
            im = Image.frombytes('RGBA', (80, 112), north.read(f'image_data/frames/1/layer_{i + 1}'))
            north_static.alpha_composite(im)
            pad = np.zeros((H, W, 4), np.uint8); pad[:112] = np.array(im); static_roles[layer['name']] = pad
    static_pad = np.zeros((H, W, 4), np.uint8); static_pad[:112] = np.array(north_static)
    south_bytes = read(ROOT / SOUTH); assert sha(south_bytes) == SOUTH_SHA
    v8_palette = {tuple(x) for x in rgba(south_bytes).reshape(-1, 4) if x[3]}
    north_png = rgba(read(ROOT / NORTH_PNG))
    north_palette = {tuple(x) for x in north_png.reshape(-1, 4) if x[3]}
    gates = {}
    gates['north_static_png_equals_pxo_composite'] = bool(np.array_equal(north_png, np.array(north_static)))
    gates['north_static_palette_subset_of_approved_v8'] = north_palette <= v8_palette
    ys, xs = np.nonzero(static_pad[..., 3])
    gates['static_body_rows_8_103_is_96_source_48_logical'] = int(ys.min()) == 8 and int(ys.max()) == 103
    manifest = {
        'task': 'content.char.protagonist-female.walk-north', 'artApproved': False, 'motionApproved': False, 'runtimeIntegrated': False,
        'cell': [W, H], 'pivot': list(PIN), 'scale': .5, 'cadenceStepsPerSecond': 4.375, 'stanceSourceRows': 20, 'strideSourceRows': 64,
        'groundedShareOfStep': 20 / 64, 'flightShareOfStep': 44 / 64, 'guidePin': list(PIN), 'staticBodyRows': list(BODY_ROWS),
        'staticDisplayBaselineLogicalPixels': 48,
        'sourceHashEncoding': 'sha256-text-lf-v1 for .py/.gd (CRLF->LF only); sha256-bytes for binary assets',
        'sources': {p: (tsha(read(ROOT / p)) if p.endswith(('.py', '.gd')) else sha(read(ROOT / p))) for p in [CORE, BAKE, WRITER, V8TOOL, NORTH_PXO, NORTH_PNG, SOUTH]},
        'modelSha256Bytes': core_before, 'layers': roles, 'sets': {},
        'bake': {'runReference': bake['runReference'], 'stopReference': bake['stopReference'], 'representativeStop': bake['representativeStop'],
                 'stopScan60Phases': len(bake['stopScan60']), 'allStopFinalsExact': bake['allStopFinalsExact'],
                 'stopScan60FirstStaticStopAgeMax': max(s['firstStaticStopAge'] for s in bake['stopScan60']),
                 'bakeToolSha256Bytes': bake['bakeToolSha256']},
        'scope': 'One NORTH run (128 real advance() phases at the 280 Hz reference) and one representative 60 fps stop (worst final-settle phase). '
                 'Arbitrary release/re-press uses the same source controller (transition matrix), not extra baked clips. Static endpoint is the produced, '
                 'UNAPPROVED NORTH idle static pilot (matched to the approved SOUTH v8 palette/scale); it is not creator-approved.',
        'fullFramePngsTempOnly': str(folder)}
    jobs = []; critical = []; body = []
    for kind in ['run', 'stop']:
        rows = [r for r in bake['poses'] if r['kind'] == kind]
        frames = []; records = []; merged = []
        for row in rows:
            data = read(folder / row['full']['file']); image = rgba(data); parts = {}
            assert sha(data) == row['full']['sha256'] and sha(image.tobytes()) == row['full']['rgbaSha256']
            for role in roles[:-1]:
                raw = read(folder / row['roles'][role]['file']); assert sha(raw) == row['roles'][role]['sha256']
                parts[role] = np.frombuffer(raw, np.uint8).reshape(H, W, 4).copy()
            full = Image.new('RGBA', (W, H))
            for role in roles[:-1]: full.alpha_composite(Image.fromarray(parts[role]))
            key = f'{kind}:{row["index"]}'
            gates[key + ':roles_compose_full'] = bool(np.array_equal(np.array(full), image))
            gates[key + ':binary_alpha'] = set(np.unique(image[:, :, 3])) <= {0, 255} and all(set(np.unique(parts[r][:, :, 3])) <= {0, 255} for r in roles[:-1])
            cols = {tuple(x) for x in image.reshape(-1, 4) if x[3]}
            gates[key + ':north_static_palette_only'] = cols <= north_palette
            gates[key + ':approved_v8_palette'] = cols <= v8_palette
            gates[key + ':no_edge_texels'] = not np.any(image[[0, -1], :, 3]) and not np.any(image[:, [0, -1], 3])
            g, overlap = guides(image); parts['guides'] = g
            gates[key + ':guides_do_not_overlap_sprite'] = not overlap
            # Body preservation: stamped torso roles are the static roles shifted by the integer body offset;
            # no enlargement, no identity change. Upper-body top row moves only with the body offset.
            bx, by = (0, 0) if row['state']['mode'] == 'idle' else (int(row['state']['body'][0]), int(row['state']['body'][1]))
            ok = True
            for role in STAMPED:
                exp = np.zeros_like(static_roles[role])
                src = static_roles[role]
                ys0, ye0 = max(0, -by), min(H, H - by); xs0, xe0 = max(0, -bx), min(W, W - bx)
                exp[ys0 + by:ye0 + by, xs0 + bx:xe0 + bx] = src[ys0:ye0, xs0:xe0]
                ok = ok and np.array_equal(parts[role], exp)
            gates[key + ':stamped_torso_roles_equal_static_shifted_by_body'] = bool(ok)
            ab = Image.fromarray(image).getbbox()
            gates[key + ':top_row_is_static_top_plus_body_y'] = ab[1] == 8 + by
            body.append({'kind': kind, 'index': row['index'], 'body': [bx, by], 'alphaBoundsExclusive': list(ab), 'heightSourceRows': ab[3] - ab[1]})
            frames.append(parts); merged.append(image)
            records.append({'index': row['index'], 'state': row['state'], 'alphaBoundsExclusive': list(ab), 'tempPng': row['full']['file'],
                            'pngSha256': row['full']['sha256'], 'rgbaSha256': row['full']['rgbaSha256'], 'rolesSha256': {r: sha(parts[r].tobytes()) for r in roles}})
        fps = 70. if kind == 'run' else 60.
        durations = [.25 if kind == 'run' else 1.] * len(frames)
        preview = read(folder / rows[0]['full']['file'])
        pxo = build_pxo(writer, frames, durations, preview, kind, fps, roles)
        gates[kind + ':pxo_exact_rebuild_bytes'] = build_pxo(writer, frames, durations, preview, kind, fps, roles) == pxo
        path = OUT / f'{SLUG}_female-north-{kind}_animated-source_unapproved-{TAG}.pxo'; write(path, pxo)
        zr = zipfile.ZipFile(io.BytesIO(read(path))); dr = json.loads(zr.read('data.json'))
        gates[kind + ':pxo_metadata'] = (dr['size_x'], dr['size_y']) == (W, H) and len(dr['frames']) == len(frames) and dr['fps'] == fps and \
            [x['duration'] for x in dr['frames']] == durations and [x['name'] for x in dr['layers']] == roles and \
            not dr['layers'][-1]['visible'] and dr['layers'][-1]['locked'] and all(x['visible'] for x in dr['layers'][:-1])
        gates[kind + ':pxo_cels_exact'] = all(zr.read(f'image_data/frames/{i + 1}/layer_{j + 1}') == frames[i][r].tobytes()
                                              for i in range(len(frames)) for j, r in enumerate(roles))
        ora = make_ora(frames, roles, merged)
        gates[kind + ':ora_exact_rebuild_bytes'] = make_ora(frames, roles, merged) == ora
        opath = OUT / f'{SLUG}_female-north-{kind}_layered-strip-source_unapproved-{TAG}.ora'; write(opath, ora)
        zo = zipfile.ZipFile(io.BytesIO(read(opath))); st = ET.fromstring(zo.read('stack.xml'))
        names = [l.get('name') for l in st.iter('layer')]
        ora_ok = names == list(reversed(roles)) and int(st.get('w')) == W * len(frames) and int(st.get('h')) == H
        for l in st.iter('layer'):
            strip = rgba(zo.read(l.get('src')))
            ora_ok = ora_ok and all(np.array_equal(strip[:, i * W:(i + 1) * W], frames[i][l.get('name')]) for i in range(len(frames)))
            ora_ok = ora_ok and ((l.get('visibility') == 'hidden') == (l.get('name') == 'guides'))
        mstrip = rgba(zo.read('mergedimage.png'))
        ora_ok = ora_ok and all(np.array_equal(mstrip[:, i * W:(i + 1) * W], merged[i]) for i in range(len(frames)))
        gates[kind + ':ora_layers_and_merged_exact'] = bool(ora_ok)
        manifest['sets'][kind] = {'pxo': {'file': path.relative_to(ROOT).as_posix(), 'sha256': sha(pxo)}, 'ora': {'file': opath.relative_to(ROOT).as_posix(), 'sha256': sha(ora)},
                                  'fps': fps, 'durations': durations, 'frames': records, 'seconds': sum(durations) / fps}
        # Independent Pixelorama 1.2.3 process; isolated APPDATA/LOCALAPPDATA; never the user's editor or settings.
        temp = Path(tempfile.mkdtemp(prefix='fn6-' + kind + '-')); (temp / 'x').mkdir()
        env = dict(os.environ); env['APPDATA'] = str(temp / 'app'); env['LOCALAPPDATA'] = str(temp / 'local')
        inp = temp / ('north-' + kind + '.pxo'); inp.write_bytes(pxo)
        proc = subprocess.run([str(PIXELORAMA.resolve()), '--headless', '--quit', '--', '--export', '--split-layers', '-o', str(temp / 'x' / f'n5{kind}.png'), str(inp)],
                              env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600,
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
        pick = CRITICAL_RUN if kind == 'run' else []
        if kind == 'stop':
            rs = bake['representativeStop']; n = len(rows)
            pick = [('release', 0), ('lastmoving', rs['lastMovingFrame']), ('final', n - 1)]
        for label, index in pick:
            row = rows[index]
            name = (f'{SLUG}_female-north-run_native-{label}-q{index:03d}_{TAG}.png' if kind == 'run' else
                    f'{SLUG}_female-north-stop_native-{label}-60fps-f{index:02d}-q{bake["representativeStop"]["phase"]:03d}_{TAG}.png')
            data = read(folder / row['full']['file']); write(OUT / name, data)
            critical.append({'kind': kind, 'purpose': label, 'index': index, 'file': (OUT / name).relative_to(ROOT).as_posix(), 'sha256': sha(data),
                             'rgbaSha256': row['full']['rgbaSha256'], 'stopAge': row['state'].get('stopAge'), 'mode': row['state']['mode']})
    stop_rows = manifest['sets']['stop']['frames']
    gates['stop:final_equals_north_static_composite_padded'] = stop_rows[-1]['rgbaSha256'] == sha(static_pad.tobytes())
    gates['stop:first_is_running_release_last_is_idle'] = stop_rows[0]['state']['mode'] == 'run' and stop_rows[-1]['state']['mode'] == 'idle'
    gates['run:128_distinct_phases_0_127'] = sorted(r['state']['q'] for r in manifest['sets']['run']['frames']) == list(range(128))
    if second is not None:
        b2 = json.loads(read(second / bname))
        same = len(b2['poses']) == len(bake['poses']) and all(
            a['full']['sha256'] == b['full']['sha256'] and a['roles'] == b['roles'] for a, b in zip(bake['poses'], b2['poses']))
        gates['bake_exact_rebuild_second_independent_run'] = bool(same) and b2['representativeStop'] == bake['representativeStop']
    manifest['critical'] = critical
    manifest['bodyPreservation'] = {'heightSourceRowsRange': [min(b['heightSourceRows'] for b in body), max(b['heightSourceRows'] for b in body)],
                                    'bodyOffsetsSeen': sorted({tuple(b['body']) for b in body}), 'perFrame': body}
    gates['model_hash_unchanged'] = sha(read(ROOT / CORE)) == core_before
    gates = {k: bool(v) for k, v in gates.items()}
    mpath = OUT / f'{SLUG}_female-north-run-stop_native-source-manifest_unapproved-{TAG}.json'
    write(mpath, (json.dumps(manifest, indent=1, default=list) + '\n').encode('utf-8'))
    report = {'passed': sum(bool(v) for v in gates.values()), 'total': len(gates), 'failedGates': [k for k, v in gates.items() if not v], 'gates': gates,
              'native': jobs, 'manifestSha256': sha(read(mpath)), 'modelSha256Before': core_before, 'modelSha256After': sha(read(ROOT / CORE)),
              'packagerSha256TextLf': tsha(read(Path(__file__))), 'artApproved': False, 'motionApproved': False, 'nativeGuiSaveAsVerified': False,
              'diagnosticsPolicy': 'Exact export is gated. Known inherited headless shader-compiler diagnostics are counted and kept verbatim; '
                                   'they are not a clean-app success (cleanAppSuccess false whenever stderr is non-empty). Any other diagnostic fails.'}
    rpath = OUT / f'{SLUG}_female-north-run-stop_native-report_{TAG}.json'
    write(rpath, (json.dumps(report, indent=1) + '\n').encode('utf-8'))
    print(rpath); print('gates', report['passed'], '/', report['total'], report['failedGates'][:10])
    for j in jobs: print(j['kind'], 'exit', j['exit'], 'exact', j['exact'], '/', j['cells'], 'known', j['knownInheritedShaderDiagnostics'], 'unexpected', repr(j['unexpectedDiagnostics'][:200]), 'clean', j['cleanAppSuccess'])
    if report['failedGates']: raise SystemExit(1)
    print('NORTH_V06_PACKAGE_OK')


if __name__ == '__main__':
    main()
