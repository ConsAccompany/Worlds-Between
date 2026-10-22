"""Independent fixed-schema package check; no application GUI or art-approval claims."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from PIL import Image


def lp(p):
    s = str(Path(p).resolve())
    return Path(s if s.startswith('\\\\?\\') else '\\\\?\\' + s)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    manifest = Path(args.manifest)
    if not manifest.is_absolute():
        manifest = root / manifest
    if not lp(manifest).exists():
        print('PENDING manifest missing')
        return 2
    data = json.loads(lp(manifest).read_text(encoding='utf8'))
    checks = []

    def check(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(name)

    def file(rel):
        rel = Path(rel)
        check('safe-relative-' + str(rel), not rel.is_absolute() and '..' not in rel.parts)
        return lp(root / rel)

    def image(path):
        return Image.open(path).convert('RGBA')

    def same(a, b):
        return a.size == b.size and np.array_equal(np.asarray(a), np.asarray(b))

    try:
        check('native-size', data['native_size'] == [640, 360])
        check('approval-boundary', data['default_adopted'] is False and data['art_unapproved'] is True)
        for rel, info in data['files'].items():
            raw = file(rel).read_bytes()
            algorithm = info['hash_algorithm']
            if algorithm in ['sha256-text-lf-v1', 'sha256-text-lf']:
                raw = raw.replace(b'\r\n', b'\n')
            else:
                check('declared-raw-hash-' + rel, algorithm in ['sha256', 'sha256-raw', 'sha256-raw-bytes', 'sha256-bytes'])
            check('hash-' + rel, hashlib.sha256(raw).hexdigest() == info['sha256'])
        reference = data['source_reference']
        raw = file(reference['file']).read_bytes()
        check('reference-sha256', hashlib.sha256(raw).hexdigest() == reference['sha256'])
        bg = image(file(data['background']))
        nearest = image(io.BytesIO(raw)).resize((640, 360), Image.Resampling.NEAREST)
        check('exact-nearest-background', same(bg, nearest))
        expected = ['machine-translation', 'parallel-inscription', 'erased-heading', 'analysis-light-table']
        positions = [[115, 164], [272, 164], [429, 164], [272, 278]]
        check('four-fixtures', len(data['fixtures']) == 4)
        flat = bg.copy()
        for i, fixture in enumerate(data['fixtures']):
            pinned = ('game/assets/props/wdc-annex-room2/rpg-2-star-ocean-the-second_wdc-annex-room2_'
                      + expected[i] + '-pixel-fixture_unapproved-v01_20261018-001157-151fb8d0.png')
            check('original-prop-path-' + str(i), fixture['file'] == pinned)
            check('original-prop-position-' + str(i), fixture['position'] == positions[i])
            raw = file(pinned).read_bytes()
            check('prop-hash-' + str(i), hashlib.sha256(raw).hexdigest() == fixture['sha256'])
            im = image(io.BytesIO(raw))
            check('prop-canvas-' + str(i), im.size == ((96, 40) if i == 3 else (96, 72)))
            flat.alpha_composite(im, tuple(positions[i]))
        oras = [rel for rel in data['files'] if rel.endswith('.ora')]
        pxos = [rel for rel in data['files'] if rel.endswith('.pxo')]
        check('one-native-package-each', len(oras) == 1 and len(pxos) == 1)
        with zipfile.ZipFile(file(oras[0])) as archive:
            check('ora-merged', same(image(io.BytesIO(archive.read('mergedimage.png'))), flat))
            stack = ET.fromstring(archive.read('stack.xml')).find('stack')
            canvas = Image.new('RGBA', (640, 360))
            visible = [layer for layer in stack if layer.get('visibility') != 'hidden']
            check('five-visible-layers', len(visible) == 5)
            for layer in reversed(visible):
                im = image(io.BytesIO(archive.read(layer.get('src'))))
                canvas.alpha_composite(im, (int(layer.get('x', '0')), int(layer.get('y', '0'))))
            check('ora-independent-visible-composite', same(canvas, flat))
        with zipfile.ZipFile(file(pxos[0])) as archive:
            d = json.loads(archive.read('data.json'))
            check('pxo-canvas', [d['size_x'], d['size_y']] == [640, 360])
            check('pxo-preview', same(image(io.BytesIO(archive.read('preview.png'))), flat))
            check('pxo-single-frame', len(d['frames']) == 1)
            canvas = Image.new('RGBA', (640, 360))
            count = 0
            for i, layer in enumerate(d['layers'], 1):
                raw = archive.read('image_data/frames/1/layer_' + str(i))
                check('pxo-cel-size-' + str(i), len(raw) == 640 * 360 * 4)
                if layer['visible']:
                    canvas.alpha_composite(Image.frombytes('RGBA', (640, 360), raw))
                    count += 1
                else:
                    check('hidden-guide-locked', layer['locked'])
            check('pxo-five-visible', count == 5)
            check('pxo-independent-cels', same(canvas, flat))
        result = {'passed': True, 'checks': checks, 'manifest': str(manifest),
                  'scope': 'Bytes, geometry and independent native layer reconstruction; no GUI/art approval.'}
    except Exception as exc:
        result = {'passed': False, 'checks': checks, 'error': str(exc)}
    out = lp(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding='utf8')
    print('STYLE48_PACKAGE', 'PASS' if result['passed'] else 'FAIL', len(checks), result.get('error', ''))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
