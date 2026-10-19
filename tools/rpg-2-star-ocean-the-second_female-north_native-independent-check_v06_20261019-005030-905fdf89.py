"""Independently reconstruct retained PXO cells and ORA strips; no native app or model inference."""
from pathlib import Path
import hashlib, io, json, os, sys, zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/female-north-run-v06'
checks = []

def long_path(path):
    value = str(Path(path).resolve())
    return Path('\\\\?\\' + value) if os.name == 'nt' and not value.startswith('\\\\?\\') else Path(value)

def read(path):
    return long_path(path).read_bytes()

def digest(value):
    return hashlib.sha256(value).hexdigest()

def check(key, ok):
    checks.append({'key': key, 'pass': bool(ok)})

manifest = json.loads(read(next(OUT.glob('*native-source-manifest*.json'))))
for rel, expected in manifest['sources'].items():
    data = read(ROOT / rel)
    if Path(rel).suffix in ('.gd', '.py'):
        data = data.replace(b'\r\n', b'\n')
    check('source-' + rel, digest(data) == expected)

for kind, count in [('run', 128), ('stop', 17)]:
    entry = manifest['sets'][kind]
    for fmt in ('pxo', 'ora'):
        check(kind + '-' + fmt + '-hash', digest(read(ROOT / entry[fmt]['file'])) == entry[fmt]['sha256'])
    with zipfile.ZipFile(io.BytesIO(read(ROOT / entry['pxo']['file']))) as archive:
        data = json.loads(archive.read('data.json'))
        check(kind + '-frame-count', len(data['frames']) == count == len(entry['frames']))
        check(kind + '-native-cell', (data['size_x'], data['size_y']) == (80, 128))
        # Thirteen authored roles plus one additional hidden locked guide, not thirteen total layers.
        check(kind + '-layer-count', len(data['layers']) == 14)
        check(kind + '-authored-role-count', len([x for x in data['layers'] if x['name'] != 'guides']) == 13)
        check(kind + '-hidden-locked-guide', any(x['name'] == 'guides' and not x['visible'] and x['locked'] for x in data['layers']))
        seconds = sum(frame['duration'] for frame in data['frames']) / data['fps']
        check(kind + '-native-timing', abs(seconds - entry['seconds']) < 1e-9)
        strip = Image.new('RGBA', (80 * count, 128))
        for index, expected in enumerate(entry['frames']):
            full = Image.new('RGBA', (80, 128))
            for layer_index, layer in enumerate(data['layers'], 1):
                raw = archive.read(f'image_data/frames/{index + 1}/layer_{layer_index}')
                name = layer['name']
                check(f'{kind}-{index}-role-{name}', digest(raw) == expected['rolesSha256'][name])
                if layer['visible']:
                    full.alpha_composite(Image.frombytes('RGBA', (80, 128), raw))
            check(f'{kind}-{index}-rgba', digest(full.tobytes()) == expected['rgbaSha256'])
            strip.paste(full, (index * 80, 0))
        if kind == 'stop':
            source = next((ROOT / 'game/assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01').glob('*6ed8d8dd.png'))
            static = Image.new('RGBA', (80, 128))
            static.paste(Image.open(io.BytesIO(read(source))).convert('RGBA'), (0, 0))
            check('stop-final-static-exact', full.tobytes() == static.tobytes())
    with zipfile.ZipFile(io.BytesIO(read(ROOT / entry['ora']['file']))) as archive:
        merged = Image.open(io.BytesIO(archive.read('mergedimage.png'))).convert('RGBA')
        check(kind + '-ora-strip-exact', merged.size == strip.size and merged.tobytes() == strip.tobytes())

failed = [item for item in checks if not item['pass']]
result = {'passed': len(checks) - len(failed), 'failed': len(failed), 'checks': checks,
          'checkerSha256': digest(read(__file__)), 'nativeGuiSaveAsVerified': False,
          'limits': 'Independent archive/hash/pixel/timing checks; not clean native application or art/motion approval'}
path = OUT / 'rpg-2-star-ocean-the-second_female-north_root-native-verification_v06_20261019-005030-905fdf89.json'
long_path(path).write_text(json.dumps(result, indent=2) + '\n', encoding='utf8', newline='\n')
print(json.dumps({'passed': result['passed'], 'failed': result['failed'], 'failures': failed}))
sys.exit(1 if failed else 0)
