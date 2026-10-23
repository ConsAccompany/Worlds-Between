"""Cross-host source-content diagnostic; strict raw rebuild remains a separate failed gate.

No sources or old receipts are rewritten. Checks decoded PNG payloads, all PXO
members, ORA content, runtime metadata and original raw hash references.
"""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import zipfile
import zlib

from PIL import Image, features

ROOT = Path(__file__).resolve().parent.parent
TAG = '20261023-050631-c52d784a'
AUTHOR = ROOT / 'tools/rpg-2-star-ocean-the-second_lin-que_exploration-source-author_unapproved-lexplore59-v01_20261022-231558-6875dc75.py'
OUT = ROOT / 'outputs/lexplore59/hermes61'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def png_payload(b):
    chunks, pos = [], 8
    while pos < len(b):
        size = struct.unpack('>I', b[pos:pos + 4])[0]
        chunks.append((b[pos + 4:pos + 8], b[pos + 8:pos + 8 + size]))
        pos += size + 12
    image = Image.open(io.BytesIO(b)).convert('RGBA')
    return image.size, image.tobytes(), zlib.decompress(b''.join(v for k, v in chunks if k == b'IDAT'))


def strip_hash_fields(obj):
    if isinstance(obj, dict):
        return {k: strip_hash_fields(v) for k, v in obj.items() if 'sha256' not in k}
    if isinstance(obj, list):
        return [strip_hash_fields(v) for v in obj]
    return obj


def main():
    spec = importlib.util.spec_from_file_location('lin_source_diagnostic', AUTHOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _, generated, source = module.build_all()
    _, again, _ = module.build_all()
    checks, comparisons, archives = [], [], []
    checks.append({'check': 'Linux two independent rebuilds deterministic',
                   'passed': generated.keys() == again.keys() and all(v == again[k] for k, v in generated.items())})
    for name, new in generated.items():
        original = (ROOT / name).read_bytes()
        entry = {'file': name, 'incomingSha256Raw': sha(original), 'linuxSha256Raw': sha(new),
                 'rawExact': new == original, 'contentExact': new == original}
        if name.endswith('.png'):
            entry['contentExact'] = png_payload(original) == png_payload(new)
        elif name.endswith(('.pxo', '.ora')):
            with zipfile.ZipFile(io.BytesIO(original)) as oldzip, zipfile.ZipFile(io.BytesIO(new)) as newzip:
                same = oldzip.namelist() == newzip.namelist()
                differences = []
                for member in oldzip.namelist():
                    a, b = oldzip.read(member), newzip.read(member)
                    if a != b:
                        exact = member.endswith('.png') and png_payload(a) == png_payload(b)
                        same = same and exact
                        differences.append({'member': member, 'decodedPngExact': exact})
                entry['contentExact'] = same
                a, b = oldzip.infolist()[0], newzip.infolist()[0]
                archives.append({'file': name, 'originalCreateSystem': a.create_system,
                                 'linuxCreateSystem': b.create_system,
                                 'differentMemberPayloads': differences, 'allMemberContentExact': same})
        elif name.endswith('.json'):
            # Hash differences are only isolated after every original/generated file
            # is compared, with all original hash references independently checked below.
            entry['contentExact'] = strip_hash_fields(json.loads(original)) == strip_hash_fields(json.loads(new))
        comparisons.append(entry)
    listing_path = ROOT / module.OUT_REL / module.fname('file-list', 'json')
    listing = json.loads(listing_path.read_bytes())['files']
    checks.append({'check': 'All340 original file-list raw SHA256 values match disk',
                   'passed': len(listing) == len(generated) == 340 and set(listing) == set(generated)
                             and all(sha((ROOT / name).read_bytes()) == digest for name, digest in listing.items())})
    checks.append({'check': 'All340 reconstructed content entries exact; encoded bytes judged separately',
                   'passed': len(comparisons) == 340 and all(c['contentExact'] for c in comparisons)})
    checks.append({'check': 'All12 frozen neutral source pins remain raw exact',
                   'passed': len(module.J.pins_state()) == 12 and all(module.J.pins_state().values())})
    # Re-measure frame-hold excursion independently from sole-row source cels.
    excursion = {}
    for direction in ('west', 'east'):
        bank = source['directions'][direction]
        with zipfile.ZipFile(ROOT / bank['pxo']['file']) as archive:
            native = json.loads(archive.read('data.json'))
            indices = {x['name']: i + 1 for i, x in enumerate(native['layers'])}
            best = 0.0
            sign = -1 if direction == 'west' else 1
            for layer in ('boots', 'far-limbs'):
                run = []
                for sample in range(int(2 * 12 * 40 * 60 / 1000)):
                    t = sample / 60.0
                    phase = int(t * 1000 // 40) % 12
                    pixels = archive.read(f'image_data/frames/{phase + 6}/layer_{indices[layer]}')
                    alpha = [pixels[(103 * 80 + x) * 4 + 3] for x in range(80)]
                    xs = [x for x, a in enumerate(alpha) if a == 255]
                    if xs:
                        toe = min(xs) if sign < 0 else max(xs)
                        run.append(sign * (toe - 40) + 280 * t)
                    else:
                        if len(run) > 1:
                            best = max(best, max(run) - min(run))
                        run = []
                if len(run) > 1:
                    best = max(best, max(run) - min(run))
            excursion[direction] = round(best, 3)
            checks.append({'check': direction + '60fps excursion independently measured, NOT a footlock pass',
                           'passed': round(best, 3) == source['contact_check'][direction]['walk_planted_foot_world_excursion_src_60fps_samples']})
    result = {'base': 'b677e2902c57d0ab327b7733ad9ad89dccb65f2f',
              'checkerSha256Raw': sha(Path(__file__).read_bytes()), 'authorSha256Raw': sha(AUTHOR.read_bytes()),
              'environment': {'pillow': Image.__version__, 'zlibRuntime': zlib.ZLIB_RUNTIME_VERSION, 'pillowZlib': features.version('zlib')},
              'checks': checks, 'comparisons': comparisons, 'archiveMetadata': archives,
              'independentSide60fpsExcursionSourcePx': excursion,
              'rawCrossHostRebuildPassed': False,
              'sourceContentDiagnosticPassed': all(c['passed'] for c in checks),
              'hashNormalization': 'SHA256 raw except producer text_lf_v1: replace CRLF with LF only (not lone CR). Earlier boundary checker description of lone CR was inaccurate; actual producer implementation unchanged.',
              'productionCriterion': 'Existing committed idle/cycle/stop source with QA/contact checks; no all-pass runtime or visual task completed.',
              'artApproved': False, 'guiSaveAsReopenVerified': False}
    target = OUT / f'rpg-2-star-ocean-the-second_lin-que_cross-host-content-proof_technical-v01_{TAG}.json'
    with target.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print('CONTENT', sum(c['contentExact'] for c in comparisons), '/', len(comparisons),
          'ORIGINAL_HASHES', len(listing), 'CHECKS', sum(c['passed'] for c in checks), '/', len(checks))
    print('EXCURSION', excursion, 'RAW_CROSS_HOST_REBUILD', False)
    assert result['sourceContentDiagnosticPassed']


if __name__ == '__main__':
    main()
