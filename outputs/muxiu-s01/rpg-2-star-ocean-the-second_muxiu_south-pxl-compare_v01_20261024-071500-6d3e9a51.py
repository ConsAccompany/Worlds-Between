"""Compare Pixelorama headless exports (from PXO and ORA) with the Muxiu south static PNG, RGBA pixel equality.

Usage (via the orchestrator): compare <new log dir> <pixelorama log dir name>. Read-only on sources.
"""
import hashlib, json, pathlib, sys
from PIL import Image

R = pathlib.Path(__file__).resolve().parents[2]
src = next((R / 'game/assets/characters/muxiu-native-v01/south').glob('*static*.png'))
ref = Image.open(src).convert('RGBA')
res = {'source_png': str(src.relative_to(R)), 'source_sha256': hashlib.sha256(src.read_bytes()).hexdigest()}
for ext in ('pxo', 'ora'):
    d = R / 'outputs/muxiu-s01/logs' / sys.argv[1] / f'export-{ext}'
    pngs = sorted(d.glob('*.png'))
    r = {'emitted': [p.name for p in pngs]}
    if len(pngs) == 1:
        im = Image.open(pngs[0]).convert('RGBA')
        r.update(size=list(im.size), sha256=hashlib.sha256(pngs[0].read_bytes()).hexdigest(),
                 rgba_equal=im.size == ref.size and im.tobytes() == ref.tobytes())
        if im.size == ref.size and not r['rgba_equal']:
            r['differing_texels'] = sum(a != b for a, b in zip(im.getdata(), ref.getdata()))
    else:
        r['rgba_equal'] = False
    res[ext] = r
res['all_equal'] = all(res[e]['rgba_equal'] for e in ('pxo', 'ora'))
print(json.dumps(res, indent=1))
print('MUXIU_PXL_EXPORT_' + ('EQUAL' if res['all_equal'] else 'MISMATCH'))
sys.exit(0 if res['all_equal'] else 1)
