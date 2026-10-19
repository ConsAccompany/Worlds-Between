"""Portable integrity check for the EAST v03 run/stop package (no Godot, no Temp inputs).

Usage (checkout root, Codex-runtime Python 3.12): python -I <this>
Re-derives every PXO cel hash and flattened RGBA, critical native/gameplay frames, stored
gz reports, root body report binding and protected game sources from the evidence manifest.
"""
from pathlib import Path
import gzip, hashlib, io, json, os, subprocess, zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'outputs/female-east-run-v03/rpg-2-star-ocean-the-second_female-east-run-stop_evidence-manifest_v03_20261018-194932-3a1839f6.json'
CORE_SHA = 'e783de5d8ab6b1e3f678299eb8cffde11109d1aab06c47155831ebc4388bb07f'


def long(p):
    s = str(Path(p).resolve()); prefix = chr(92) * 2 + '?' + chr(92)
    return prefix + s if os.name == 'nt' and not s.startswith(prefix) else s


def read(p): return Path(long(p)).read_bytes()
def sha(b): return hashlib.sha256(b).hexdigest()
def tsha(b): return sha(b.replace(b'\r\n', b'\n'))
def rgba_sha(b): return sha(Image.open(io.BytesIO(b)).convert('RGBA').tobytes())


def main():
    m = json.loads(read(ROOT / MANIFEST)); checks = {}
    checks['model_locked'] = sha(read(ROOT / m['model']['path'])) == CORE_SHA == m['model']['sha256Bytes']
    for p, row in m['files'].items():
        checks['file:' + p] = (tsha(read(ROOT / p)) if row['textLf'] else sha(read(ROOT / p))) == row['sha256']
    n = json.loads(read(ROOT / m['nativeManifest'])); nr = json.loads(read(ROOT / m['nativeReport']))
    checks['native_report_bound'] = nr['manifestSha256'] == sha(read(ROOT / m['nativeManifest'])) and not nr['failedGates']
    checks['native_export_exact'] = all(j['exit'] == 0 and j['exact'] == j['cells'] and not j['unexpectedDiagnostics'] for j in nr['native'])
    checks['native_clean_app_not_overclaimed'] = all(not j['cleanAppSuccess'] for j in m['nativeExport'] if j['knownInheritedShaderDiagnostics'] > 0)
    for p, h in n['sources'].items():
        checks['source:' + p] = (tsha(read(ROOT / p)) if p.endswith(('.py', '.gd')) else sha(read(ROOT / p))) == h
    flat = {}
    for kind, entry in n['sets'].items():
        raw = read(ROOT / entry['pxo']['file']); checks[kind + ':pxo_sha'] = sha(raw) == entry['pxo']['sha256']
        z = zipfile.ZipFile(io.BytesIO(raw)); d = json.loads(z.read('data.json'))
        checks[kind + ':metadata'] = (d['size_x'], d['size_y']) == (80, 112) and len(d['frames']) == len(entry['frames']) and d['fps'] == entry['fps'] and \
            [x['duration'] for x in d['frames']] == entry['durations'] and [x['name'] for x in d['layers']] == n['layers'] and \
            not d['layers'][-1]['visible'] and d['layers'][-1]['locked'] and n['pivot'] == [40, 104] and n['scale'] == .5
        for i, row in enumerate(entry['frames']):
            full = Image.new('RGBA', (80, 112)); ok = True
            for j, role in enumerate(n['layers']):
                data = z.read(f'image_data/frames/{i + 1}/layer_{j + 1}'); ok &= sha(data) == row['rolesSha256'][role]
                if role == 'guides': ok &= data[(104 * 80 + 40) * 4 + 3] == 255
                else: full.alpha_composite(Image.frombytes('RGBA', (80, 112), data))
            b = full.tobytes(); a = b[3::4]
            checks[f'{kind}:{i}'] = ok and sha(b) == row['rgbaSha256'] and set(a) <= {0, 255}
            flat[(kind, i)] = row['rgbaSha256']
    for c in n['critical']:
        checks['critical-native:' + c['file']] = sha(read(ROOT / c['file'])) == c['sha256'] and rgba_sha(read(ROOT / c['file'])) == flat[(c['kind'], c['index'])]
    eb = m['exactBoundary']; raw = gzip.decompress(read(ROOT / eb['report']['file'])); r = json.loads(raw)
    checks['exact_boundary'] = sha(raw) == eb['report']['uncompressedSha256'] and r['failed'] == 0 and r['passed'] == eb['passed'] == 25381 and r['modelSha256'] == CORE_SHA
    body = m['rootBodyReport']; braw = read(ROOT / body['file']); b = json.loads(braw)
    checks['root_body_report'] = sha(braw) == body['sha256Bytes'] and b['valid'] and b['failed'] == 0 and b['passed'] == 15744 and b['modelSha256'] == CORE_SHA
    for p, h in body['slowFailureEvidence'].items(): checks['root_slow:' + p] = sha(read(ROOT / p)) == h
    for c in m['captures']:
        raw = gzip.decompress(read(ROOT / c['report']['file'])); r = json.loads(raw); key = c['scene']
        checks[key + ':report'] = sha(raw) == c['report']['uncompressedSha256'] and r['failed'] == 0 and r['modelSha256'] == CORE_SHA and len(r['frames']) == c['frames']
        steady = [f for f in r['frames'] if f['steadyRun'] and f['torsoEqualsNativeCel']]
        checks[key + ':steady_native'] = len(steady) == c['steadyEqualNativeCel'] and all(f['sourceRgbaSha256'] == flat[('run', int(f['state']['q']))] for f in steady)
        checks[key + ':movie'] = sha(read(ROOT / c['movie']['file'])) == c['movie']['sha256']
        for k in c['critical']:
            f = next(x for x in r['frames'] if x['tick'] == k['tick'])
            checks['critical-capture:' + k['file']] = sha(read(ROOT / k['file'])) == f['sha256'] == k['sha256']
    for p, h in m['protectedGameSourcesHead'].items():
        base = subprocess.run(['git', 'show', m['baseRevision'] + ':' + p], cwd=ROOT, capture_output=True, check=True).stdout
        checks['unchanged:' + p] = tsha(read(ROOT / p)) == h == tsha(base)
    for p, h in m['preservedEarlierEvidence'].items(): checks['preserved:' + p] = sha(read(ROOT / p)) == h
    if 'integration' in m:
        for p, row in m['integration']['frozenProducerEvidence'].items():
            raw = read(ROOT / p)
            checks['producer-snapshot:' + p] = sha(raw) == row['sha256'] and sha(gzip.decompress(raw)) == row['uncompressedSha256']
        checks['producer-protected-hashes-retained'] = json.loads(gzip.decompress(read(ROOT / m['integration']['producerManifestSnapshot'])))['protectedGameSourcesHead'] == m['protectedGameSourcesHead']
    checks['body-checker-portable'] = sha(read(ROOT / m['rootBodyReport']['checker'])) == m['rootBodyReport']['checkerSha256']
    failed = [k for k, v in checks.items() if not v]
    print('EAST V03 EVIDENCE CHECK', len(checks) - len(failed), '/', len(checks))
    for k in failed[:20]: print('FAIL', k)
    if failed: raise SystemExit(1)


if __name__ == '__main__':
    main()
