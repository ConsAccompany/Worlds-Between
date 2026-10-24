"""Independent Yanke south static source check (content.char.yanke.static-south). No runtime/art/motion approval.

Does not import the Yanke author. Reuses only the ORA stack parser/compositor from the Jiang static-source check
(as the Lin Que, Milo and Muxiu checkers do). Reads the game tree; writes only to --out.

  python -X utf8 -I <this> --root . --out outputs/yanke-s93/independent-<new>
Exit 0 all checks pass, 1 any failure.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, io, json, os, zipfile
from PIL import Image
import numpy as np

ap = argparse.ArgumentParser(); ap.add_argument('--root', default='.'); ap.add_argument('--out', required=True); a = ap.parse_args()
R = Path(a.root).resolve(); O = Path(a.out).resolve(); O.mkdir(parents=True, exist_ok=False)
if os.name == 'nt': R = Path('\\\\?\\' + str(R)); O = Path('\\\\?\\' + str(O))
sp = importlib.util.spec_from_file_location('ora_helpers', R / 'tools/rpg-2-star-ocean-the-second_jiang-lan_static-source-check_v01_20261021-235007-514b9771.py')
Hm = importlib.util.module_from_spec(sp); sp.loader.exec_module(Hm)
TAG = '20261024-084428-b93c1a4e'
PORTRAIT = 'outputs/rpg-2-star-ocean-the-second_yanke_character-sheet_v01_20261013-153818-244380f3.png'
PORTRAIT_SHA = '65ded437ee36afd47f2bbd17cefc72a2ec0afe5914d54bcb6f46f17855b8b23f'
PLACEHOLDER = 'game/assets/characters/native-animation'
OTHERS = {'jiang-lan': 'game/assets/characters/jiang-lan-native-south-v01',
          'lin-que': 'game/assets/characters/lin-que-native-v01/south',
          'milo': 'game/assets/characters/milo-native-v01/south',
          'muxiu': 'game/assets/characters/muxiu-native-v01/south'}
ANCHORS = ('hammer', 'grip', 'harness', 'trousers', 'apron', 'hair', 'beard', 'face')
checks = []


def gate(n, v, detail=None): checks.append({'id': n, 'passed': bool(v), 'detail': detail})
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes(m, f): return all(sha(f / v['file']) == v['rawsha256'] for v in m['files'].values())
def rgba(p): return np.array(Image.open(p).convert('RGBA'))


f = R / 'game/assets/characters/yanke-native-v01/south'
ms = list(f.glob('*manifest*.json')); assert len(ms) == 1, 'missing/ambiguous manifest'
m = json.loads(ms[0].read_text(encoding='utf8'))
gate('identity', m['actor_id'] == 'yanke' and m['content_id'] == 'content.char.yanke.static-south' and m['direction'] == 'south' and m['status'] == 'UNAPPROVED')
gate('spec', m['canvas'] == [80, 112] and m['pivot'] == [40, 104] and m['body_rows'] == [8, 103] and m['display_scale'] == .5 and m['logical_height_px'] == 48)
gate('filehashes', hashes(m, f))
p = m['portrait_ref']; gate('portrait', p['file'] == PORTRAIT and p['expected_sha256'] == PORTRAIT_SHA and sha(R / PORTRAIT) == PORTRAIT_SHA and p['approval'] == 'UNAPPROVED')
gate('filenames_lowercase_pattern', all(v['file'] == v['file'].lower() and v['file'].startswith('rpg-2-star-ocean-the-second_yanke_south-') and TAG.split('-')[0] in v['file'] for v in m['files'].values()))
png = f / m['files']['png']['file']; im = Image.open(png).convert('RGBA'); ar = np.array(im); al = ar[:, :, 3]; ys, xs = np.nonzero(al)
gate('canvas', im.size == (80, 112)); gate('body_rows_8_103', ys.min() == 8 and ys.max() == 103, [int(ys.min()), int(ys.max())])
gate('logical_height_48', (ys.max() - ys.min() + 1) * .5 == 48)
feet = xs[ys == 103]; gate('pivot_x_within_feet_span', feet.min() <= 40 <= feet.max(), [int(feet.min()), int(feet.max())])
gate('binary_alpha', set(np.unique(al)) <= {0, 255}); gate('borders', not (al[0].any() or al[-1].any() or al[:, 0].any() or al[:, -1].any()))
pal = json.loads((f / m['files']['palette']['file']).read_text(encoding='utf8')); decl = {tuple(bytes.fromhex(v.lstrip('#'))) for v in pal['colors'].values()}
used = {tuple(x) for x in ar[al == 255, :3]}; gate('palette', 24 <= len(used) <= 48 and used <= decl and len(decl) <= 40, len(used))
def has(*hx): return bool(used & {tuple(bytes.fromhex(pal['colors'][k])) for k in hx})
gate('identity_colours', has('r1', 'r2') and has('t1', 't2') and has('k1', 'k2') and has('a1', 'a2') and has('c1', 'c2') and has('f1', 'f2'),
     'leather, dark-brown trousers, steel tool, olive apron, cream shirt, red rag present')
# the notched steel head must be a real mass, not a token accent
steel = {tuple(bytes.fromhex(pal['colors'][k])) for k in ('k1', 'k2', 'k3')}
steel_n = int(sum(tuple(x) in steel for x in ar[al == 255, :3])); gate('steel_tool_mass', steel_n >= 120, steel_n)
with zipfile.ZipFile(f / m['files']['ora']['file']) as z:
    ls = Hm.ora_layers(z); comp = Hm.compose(z, ls)
    gate('ora_composition', comp.tobytes() == ar.tobytes())
    gate('ora_merged', Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA').tobytes() == ar.tobytes())
    gate('ora_mimetype', z.infolist()[0].filename == 'mimetype' and z.infolist()[0].compress_type == zipfile.ZIP_STORED)
    visible = [l for l in ls if l['visible'] and not Hm.GUIDE_RE.search(l['name'])]; contrib = {}
    for l in visible:
        without = Hm.compose(z, [x for x in ls if x is not l]); contrib[l['name']] = int(np.count_nonzero(np.any(np.array(without) != ar, axis=2)))
    genuine = [n for n, c in contrib.items() if c >= 8]
    gate('genuine_ora_roles_ge_8', len(genuine) >= 8, contrib)
    gate('anchor_roles_contribute', all(contrib.get(n, 0) >= 12 for n in ANCHORS), {n: contrib.get(n) for n in ANCHORS})
    gate('hidden_guides', any(Hm.GUIDE_RE.search(l['name']) and not l['visible'] for l in ls) and not any(Hm.GUIDE_RE.search(l['name']) and l['visible'] for l in ls))
    shown = [dict(l, visible=True) if Hm.GUIDE_RE.search(l['name']) else l for l in ls]
    gate('control_visible_guides_detected', Hm.compose(z, shown).tobytes() != ar.tobytes())
with zipfile.ZipFile(f / m['files']['pxo']['file']) as z:
    raw = z.read('data.json'); j = json.loads(raw); canvas = np.zeros_like(ar); roles = 0
    for i, l in enumerate(j['layers'], 1):
        x = np.frombuffer(z.read(f'image_data/frames/1/layer_{i}'), np.uint8).reshape(112, 80, 4)
        if l['visible']:
            mask = x[:, :, 3] > 0; canvas[mask] = x[mask]; roles += int(np.count_nonzero(mask) >= 8 and not Hm.GUIDE_RE.search(l['name']))
    gate('pxo_composition', np.array_equal(canvas, ar)); gate('pxo_roles', roles >= 8, roles)
    gate('pxo_labels', all(s not in raw for s in (b'protagonist-male', b'jiang-lan', b'lin-que', b'milo', b'muxiu')) and b'yanke' in raw)
    gate('pxo_guides', any(l['name'] == 'guides' and not l['visible'] for l in j['layers']))
    gate('pxo_size', j['size_x'] == 80 and j['size_y'] == 112)
bad = json.loads(json.dumps(m)); bad['files']['png']['rawsha256'] = '0' * 64
gate('control_corrupt_hash_refused', hashes(m, f) and not hashes(bad, f))
(O / f'rpg-2-star-ocean-the-second_yanke_corrupt-hash-control_test-only-v01_{TAG}.json').write_text(json.dumps(bad, indent=2) + '\n', encoding='utf8')
t = ar.copy(); t[60, 40, :3] ^= 0x10
gate('control_tampered_png_detected', comp.tobytes() != t.tobytes() and not np.array_equal(canvas, t))
ph = sorted((R / PLACEHOLDER).glob('*yanke*.png'))
gate('not_placeholder', all(Image.open(x).size != (80, 112) or rgba(x).tobytes() != ar.tobytes() for x in ph), [x.name for x in ph])
mask_diff = {}
for who, rel in OTHERS.items():
    others = [x for x in sorted((R / rel).glob('*.png')) if 'static' in x.name]
    o = rgba(others[0]); mask_diff[who] = {'file': others[0].name, 'differing_alpha_texels': int(np.count_nonzero((o[:, :, 3] > 0) != (al > 0)))}
gate('own_silhouette_not_recolour', all(v['differing_alpha_texels'] >= 400 for v in mask_diff.values()), mask_diff)
# scope: one south package only, no runtime/default/other-direction assets introduced by this checker
gate('south_only_package', not any((f / n).exists() for n in ('west', 'north', 'east'))
     and (f / '.gdignore').exists())
pins = {x.name: sha(x) for x in sorted(f.iterdir()) if x.is_file()}
report = {'passed': all(c['passed'] for c in checks), 'checks': checks, 'sourceHashes': pins, 'checkerSha256': sha(Path(__file__)),
          'hash': 'sha256 of raw bytes, no normalization',
          'scope': 'editable static source only; no GUI reliability, motion, ordinary adoption or art approval'}
(O / f'rpg-2-star-ocean-the-second_yanke_independent-source-proof_v01_{TAG}.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
print('YANKE_S93_INDEPENDENT', sum(c['passed'] for c in checks), '/', len(checks)); print('FAILURES', [c['id'] for c in checks if not c['passed']])
for c in checks:
    if not c['passed'] or c['id'] in ('own_silhouette_not_recolour', 'anchor_roles_contribute', 'steel_tool_mass', 'not_placeholder'):
        print(c['id'], c['passed'], json.dumps(c['detail']))
raise SystemExit(0 if report['passed'] else 1)
