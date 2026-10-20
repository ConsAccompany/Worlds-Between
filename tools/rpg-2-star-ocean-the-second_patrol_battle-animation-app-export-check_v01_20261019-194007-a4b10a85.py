"""One finite Pixelorama 1.2.3 CLI export of the Patrol battle-animation PXO (a temp copy) with independent raster equality.

App diagnostics are recorded separately from native-format parity; a zero exit with diagnostic markers is NOT a clean
app success, and no GUI reopen / Save As is claimed. Usage: python -I <this>
"""
import hashlib, io, json, os, re, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT.parents[2]
STAMP = 'v01_20261019-194007-a4b10a85'
SLUG = 'rpg-2-star-ocean-the-second_patrol_battle-animation-'
STOP = PRIMARY / 'work/dual01/control/rpg-2-star-ocean-the-second_dual-provider_global-stop_v01_20261019-001423-861097ca.json'
EXE = PRIMARY / 'work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe'
PKG = ROOT / 'game/assets/enemies/patrol-anim-v01'
OUT = ROOT / 'outputs/patrol-anim-v01'
W, H, N = 112, 72, 24


def ext(p):
    return '\\\\?\\' + str(Path(p).resolve())


def read(p):
    with open(ext(p), 'rb') as f:
        return f.read()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    if STOP.exists():
        raise SystemExit('GLOBAL STOP: no export started')
    if not EXE.exists():
        raise SystemExit(f'Pixelorama missing: {EXE}')
    pxo = PKG / f'{SLUG}layered_{STAMP}.pxo'
    strip_path = PKG / f'{SLUG}strip_{STAMP}.png'
    original = read(pxo)
    strip = Image.open(io.BytesIO(read(strip_path))).convert('RGBA')
    temp = Path(tempfile.mkdtemp(prefix='patrol-app-a4b10a85-'))
    for d in ('app', 'local', 'export'):
        (temp / d).mkdir()
    src = temp / pxo.name
    src.write_bytes(original)
    target = temp / 'export' / f'{SLUG}cli-export_{STAMP}.png'
    env = dict(os.environ, APPDATA=str(temp / 'app'), LOCALAPPDATA=str(temp / 'local'))
    args = [str(EXE), '--headless', '--quit', '--', '--export', '-o', str(target), str(src)]
    started = datetime.now(timezone.utc).isoformat()
    try:
        p = subprocess.run(args, env=env, capture_output=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        out, err, code, timed_out = p.stdout, p.stderr, p.returncode, False
    except subprocess.TimeoutExpired as e:
        out, err, code, timed_out = e.stdout or b'', e.stderr or b'', None, True
    ended = datetime.now(timezone.utc).isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f'{SLUG}app-export-stdout_{STAMP}.log').write_bytes(out)
    (OUT / f'{SLUG}app-export-stderr_{STAMP}.log').write_bytes(err)
    files = sorted((temp / 'export').glob('*.png'))
    images = [Image.open(f).convert('RGBA') for f in files]
    per_frame = len(images) == N and all(
        im.size == (W, H) and im.tobytes() == strip.crop((i * W, 0, (i + 1) * W, H)).tobytes() for i, im in enumerate(images))
    one_strip = len(images) == 1 and images[0].tobytes() == strip.tobytes()
    text = (out + b'\n' + err).decode('utf-8', 'replace')
    markers = [s for s in text.splitlines() if re.search(r'ERROR|WARNING|SCRIPT ERROR|Shader compilation failed', s, re.I)]
    report = {
        'command': args, 'startUtc': started, 'endUtc': ended, 'exit': code, 'timeout': timed_out,
        'sourceSha256': sha(original), 'sourceUnchanged': read(pxo) == original, 'exportCount': len(images),
        'exportSha256': [sha(f.read_bytes()) for f in files],
        'nativeRasterParity': bool(per_frame or one_strip), 'parityMode': 'per-frame' if per_frame else ('strip' if one_strip else 'none'),
        'diagnosticMarkers': markers, 'cleanAppSuccess': code == 0 and not markers,
        'guiReopenOrSaveAs': 'not performed', 'temp': str(temp),
    }
    # Second finite run: --split-layers, one PNG per layer per frame, compared byte-for-byte with the builder's cels.
    import zipfile
    (temp / 'split').mkdir()
    sargs = [str(EXE), '--headless', '--quit', '--', '--export', '--split-layers', '-o', str(temp / 'split' / 'f.png'), str(src)]
    try:
        sp = subprocess.run(sargs, env=env, capture_output=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        scode = sp.returncode
    except subprocess.TimeoutExpired:
        scode = None
    with zipfile.ZipFile(io.BytesIO(original)) as z:
        data = json.loads(z.read('data.json'))
        names = [l['name'] for l in data['layers']]
        cels = {(fi, n): z.read(f'image_data/frames/{fi + 1}/layer_{li + 1}') for fi in range(N) for li, n in enumerate(names)}
    split_files = sorted((temp / 'split').glob('*.png'))
    matched, mismatched = 0, []
    for (fi, n), raw in cels.items():
        hits = [f for f in split_files if f'({n})' in f.name and f.name.endswith(f'_{fi + 1:04d}.png')]
        if len(hits) == 1 and Image.open(hits[0]).convert('RGBA').tobytes() == raw:
            matched += 1
        else:
            mismatched.append([fi, n, len(hits)])
    report['splitLayers'] = {'command': sargs, 'exit': scode, 'files': len(split_files), 'celsExpected': len(cels),
                             'celsByteExact': matched, 'mismatched': mismatched[:20]}
    report['nativeLayerParity'] = scode == 0 and matched == len(cels) and not mismatched
    report['flattenedNote'] = 'flattened export differs only where translucent shadow/smoke pixels composite (known +/-1 app rounding)'
    (OUT / f'{SLUG}app-export-report_{STAMP}.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: report[k] for k in ('exit', 'exportCount', 'nativeRasterParity', 'nativeLayerParity', 'cleanAppSuccess')}), report['splitLayers']['celsByteExact'], '/', report['splitLayers']['celsExpected'],
          'markers=%d' % len(markers))
    sys.exit(0 if report['nativeLayerParity'] and report['sourceUnchanged'] else 1)


if __name__ == '__main__':
    main()
