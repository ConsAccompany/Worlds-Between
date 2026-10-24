"""Independent Milo east static source check (content.char.milo.static-east). No runtime/art/motion approval.

Adapted from the Milo west/north checkers. Does not import any Milo author. Reuses only the ORA stack
parser/compositor from the Jiang static-source check (as the Lin Que and Milo south/north checkers do). Reads the game
tree; writes only to --out. Implements the eight image-level east predicates fixed in the east source contract
(outputs/milo-e01/...style-source-contract...md) before the first run, and runs them on negative controls (Milo south,
Milo north, stored Milo west read-only, mirrored stored west, mirrored east, Lin Que east). Retained controls: corrupt
hash, tampered PNG, visible guides, tampered south manifest, tampered north manifest.

  python -X utf8 -I <this> --root . --out outputs/milo-e01/<dir>
Exit 0 all checks pass, 1 any failure.
"""
from pathlib import Path
from collections import deque
import argparse, hashlib, importlib.util, io, json, os, zipfile
from PIL import Image
import numpy as np

ap = argparse.ArgumentParser(); ap.add_argument('--root', default='.'); ap.add_argument('--out', required=True); a = ap.parse_args()
R = Path(a.root).resolve(); O = Path(a.out).resolve(); O.mkdir(parents=True, exist_ok=True)
if os.name == 'nt': R = Path('\\\\?\\' + str(R)); O = Path('\\\\?\\' + str(O))
sp = importlib.util.spec_from_file_location('ora_helpers', R / 'tools/rpg-2-star-ocean-the-second_jiang-lan_static-source-check_v01_20261021-235007-514b9771.py')
Hm = importlib.util.module_from_spec(sp); sp.loader.exec_module(Hm)
TAG = '20261024-000137-e4a1c7d2'
PORTRAIT = 'outputs/rpg-2-star-ocean-the-second_milo_character-sheet_hairstyle-v02_20261013-161317-f1651dc0.png'
PORTRAIT_SHA = '79a02c532681042ec389cfb6eae0577e3f967652641be7b853461e6adc4c244f'
BASE = 'game/assets/characters/milo-native-v01'
PINNED = {  # committed packages that must stay byte-identical: dir, manifest, manifest sha
    'south': ('south', 'rpg-2-star-ocean-the-second_milo_south-manifest_unapproved-v01_20261023-215823-e604f893.json',
              '913d3070528bfb8539c65e7570e73c5f7bedc1b45a23928ec9aa091db7324cf7'),   # committed 8fb2c8e4
    'north': ('north', 'rpg-2-star-ocean-the-second_milo_north-manifest_unapproved-v01_20261023-225642-163cf811.json',
              '0cb2b25f115117795dbc2788e9a2f448218c0899b8f2fc9929154ddb324402b1')}  # committed 70ac7793
PLACEHOLDER = 'game/assets/characters/native-animation'
OTHERS = {'jiang-lan-south': 'game/assets/characters/jiang-lan-native-south-v01', 'lin-que-south': 'game/assets/characters/lin-que-native-v01/south',
          'lin-que-east': 'game/assets/characters/lin-que-native-v01/east', 'lin-que-west': 'game/assets/characters/lin-que-native-v01/west'}
PRED = ('one_eye', 'eye_in_front_half', 'face_leads_right', 'hair_at_back', 'silver_near_temple', 'case_cross_behind_centre',
        'wristband_in_front', 'profile_asymmetric')
checks = []


def gate(n, v, detail=None): checks.append({'id': n, 'passed': bool(v), 'detail': detail})
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes(m, f): return all(sha(f / v['file']) == v['rawsha256'] for v in m['files'].values())
def rgba(p): return np.array(Image.open(p).convert('RGBA'))


def isolated(ar):
    """Opaque texels whose 4-neighbours are all a different colour or transparent (retained south gate <= 24)."""
    op = ar[:, :, 3] == 255; rgb = ar[:, :, :3].astype(int); n = 0
    for y, x in zip(*np.nonzero(op)):
        n += not any(0 <= y + dy < ar.shape[0] and 0 <= x + dx < ar.shape[1] and op[y + dy, x + dx]
                     and (rgb[y + dy, x + dx] == rgb[y, x]).all() for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    return int(n)


def components(mask):
    seen = np.zeros_like(mask); n = 0
    for y, x in zip(*np.nonzero(mask)):
        if seen[y, x]: continue
        n += 1; dq = deque([(y, x)])
        while dq:
            cy, cx = dq.popleft()
            if 0 <= cy < mask.shape[0] and 0 <= cx < mask.shape[1] and mask[cy, cx] and not seen[cy, cx]:
                seen[cy, cx] = True; dq.extend((cy + dy, cx + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1))
    return n


def east_view(ar, pal):
    """Image-level east predicates, screen coordinates. Thresholds fixed in the east source contract before the first run."""
    def keys(*k): return {tuple(bytes.fromhex(pal[x])) for x in k}
    rgb = ar[:, :, :3]; op = ar[:, :, 3] == 255
    inset = lambda ks: np.array([[op[y, x] and tuple(rgb[y, x]) in ks for x in range(ar.shape[1])] for y in range(ar.shape[0])])
    skin, hair = keys('s1', 's2', 's3', 's4', 'j1', 'm1', 'e1', 'e2'), keys('h1', 'h2', 'h3', 'h4', 'a1', 'a2', 'a3')
    iris = inset(keys('e2')); iris[34:] = False; iris[:12] = False
    iris_n = components(iris)
    ys, xs = np.nonzero(op[8:34]); head_mid = (xs.min() + xs.max()) / 2
    edge = lambda y, f: f(np.nonzero(op[y])[0]) if op[y].any() else None
    front_skin = sum(edge(y, np.max) is not None and tuple(rgb[y, edge(y, np.max)]) in skin for y in range(18, 31))   # 13 rows
    back_hair = sum(edge(y, np.min) is not None and tuple(rgb[y, edge(y, np.min)]) in hair for y in range(12, 27))    # 15 rows
    silver = int(inset(keys('a1', 'a2', 'a3'))[8:27].sum())
    green3 = inset(keys('g1', 'g2', 'g3')); case_green = int(green3[64:77, :41].sum())
    band = inset(keys('g1', 'g2', 'g3', 'g4'))[58:65]; band_x = float(np.nonzero(band)[1].mean()) if band.any() else None
    yb, xb = np.nonzero(op); m = op[yb.min():yb.max() + 1, xb.min():xb.max() + 1]
    mirror_iou = float((m & m[:, ::-1]).sum() / (m | m[:, ::-1]).sum())
    r = {'iris_components': iris_n, 'iris_x_mean': float(np.nonzero(iris)[1].mean()) if iris.any() else None,
         'head_mid_x': float(head_mid), 'front_edge_skin_rows_of_13': int(front_skin), 'back_edge_hair_rows_of_15': int(back_hair),
         'silver_texels_rows_8_26': silver, 'case_green_rows_64_76_x_le_40': case_green, 'band_green_x_mean_rows_58_64': band_x,
         'mirror_iou': round(mirror_iou, 4), 'bbox_width': int(xb.max() - xb.min() + 1)}
    r['one_eye'] = bool(iris_n == 1)
    r['eye_in_front_half'] = bool(r['iris_x_mean'] is not None and r['iris_x_mean'] > head_mid)
    r['face_leads_right'] = bool(front_skin >= 8)
    r['hair_at_back'] = bool(back_hair >= 10)
    r['silver_near_temple'] = bool(silver >= 16)
    r['case_cross_behind_centre'] = bool(case_green >= 12)
    r['wristband_in_front'] = bool(band_x is not None and band_x > 44)
    r['profile_asymmetric'] = bool(mirror_iou <= .80)
    r['east'] = all(r[k] for k in PRED)
    return r


f = R / BASE / 'east'
ms = list(f.glob('*manifest*.json')); assert len(ms) == 1, 'missing/ambiguous manifest'
m = json.loads(ms[0].read_text(encoding='utf8'))
gate('identity', m['actor_id'] == 'milo' and m['content_id'] == 'content.char.milo.static-east' and m['direction'] == 'east' and m['status'] == 'UNAPPROVED')
gate('spec', m['canvas'] == [80, 112] and m['pivot'] == [40, 104] and m['body_rows'] == [8, 103] and m['display_scale'] == .5 and m['logical_height_px'] == 48)
gate('filehashes', hashes(m, f))
p = m['portrait_ref']; gate('portrait', p['file'] == PORTRAIT and p['expected_sha256'] == PORTRAIT_SHA and sha(R / PORTRAIT) == PORTRAIT_SHA)
gate('filenames_lowercase_pattern', all(v['file'] == v['file'].lower() and v['file'].startswith('rpg-2-star-ocean-the-second_milo_east-') and TAG.split('-')[0] in v['file'] for v in m['files'].values()))
gate('parent_gdignore', (R / BASE / '.gdignore').is_file())
png = f / m['files']['png']['file']; im = Image.open(png).convert('RGBA'); ar = np.array(im); al = ar[:, :, 3]; ys, xs = np.nonzero(al)
gate('canvas', im.size == (80, 112)); gate('body_rows_8_103', ys.min() == 8 and ys.max() == 103, [int(ys.min()), int(ys.max())])
gate('logical_height_48', (ys.max() - ys.min() + 1) * .5 == 48)
feet = xs[ys == 103]; gate('pivot_x_within_feet_span', feet.min() <= 40 <= feet.max(), [int(feet.min()), int(feet.max())])
gate('binary_alpha', set(np.unique(al)) <= {0, 255}); gate('borders', not (al[0].any() or al[-1].any() or al[:, 0].any() or al[:, -1].any()))
pal = json.loads((f / m['files']['palette']['file']).read_text(encoding='utf8')); decl = {tuple(bytes.fromhex(v.lstrip('#'))) for v in pal['colors'].values()}
used = {tuple(x) for x in ar[al == 255, :3]}; gate('palette', 24 <= len(used) <= 48 and used <= decl, len(used))
def has(*hx): return bool(used & {tuple(bytes.fromhex(pal['colors'][k])) for k in hx})
gate('identity_colours', has('g1', 'g2', 'g3') and has('a1', 'a2') and has('w1', 'w2') and has('n1', 'n2'), 'green, silver, white coat, navy present')
iso = isolated(ar); gate('isolated_texels_le_24', iso <= 24, iso)
# continuity: committed south and north packages unchanged; east palette colours byte-identical to both
pk = {}
for name, (d, mf, msha) in PINNED.items():
    dd = R / BASE / d; mp = dd / mf; mm = json.loads(mp.read_text(encoding='utf8')); pk[name] = (dd, mm)
    gate(f'{name}_manifest_pinned', sha(mp) == msha)
    gate(f'{name}_files_unchanged', hashes(mm, dd), {v['file']: v['rawsha256'][:12] for v in mm['files'].values()})
    gate(f'palette_colours_identical_to_{name}', json.loads((dd / mm['files']['palette']['file']).read_text(encoding='utf8'))['colors'] == pal['colors'])
    bad_m = json.loads(json.dumps(mm)); bad_m['files']['png']['rawsha256'] = 'f' * 64
    gate(f'control_tampered_{name}_manifest_refused', hashes(mm, dd) and not hashes(bad_m, dd))
sd, sm = pk['south']; nd, nm = pk['north']
with zipfile.ZipFile(f / m['files']['ora']['file']) as z:
    ls = Hm.ora_layers(z); comp = Hm.compose(z, ls)
    gate('ora_composition', comp.tobytes() == ar.tobytes())
    gate('ora_merged', Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA').tobytes() == ar.tobytes())
    gate('ora_mimetype', z.infolist()[0].filename == 'mimetype' and z.infolist()[0].compress_type == zipfile.ZIP_STORED)
    gate('ora_layer_names_match_south', [l['name'] for l in ls] == [x['name'] for x in sm['layers']][::-1] or [l['name'] for l in ls] == [x['name'] for x in sm['layers']],
         [l['name'] for l in ls])
    visible = [l for l in ls if l['visible'] and not Hm.GUIDE_RE.search(l['name'])]; contrib = {}
    for l in visible:
        without = Hm.compose(z, [x for x in ls if x is not l]); contrib[l['name']] = int(np.count_nonzero(np.any(np.array(without) != ar, axis=2)))
    genuine = [n for n, c in contrib.items() if c >= 8]
    gate('genuine_ora_roles_ge_8', len(genuine) >= 8, contrib)
    gate('anchor_roles_contribute', all(contrib.get(n, 0) >= 12 for n in ('case', 'wristband', 'coat', 'hair', 'face')), {n: contrib.get(n) for n in ('case', 'wristband', 'coat', 'hair', 'face')})
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
    gate('pxo_labels_east', all(s not in raw for s in (b'protagonist-male', b'jiang-lan', b'lin-que', b'milo-south', b'milo-north', b'milo-west')) and b'milo-east' in raw)
    gate('pxo_guides', any(l['name'] == 'guides' and not l['visible'] for l in j['layers']))
    gate('pxo_size', j['size_x'] == 80 and j['size_y'] == 112)
bad = json.loads(json.dumps(m)); bad['files']['png']['rawsha256'] = '0' * 64
gate('control_corrupt_hash_refused', hashes(m, f) and not hashes(bad, f))
(O / f'rpg-2-star-ocean-the-second_milo_east-corrupt-hash-control_test-only-v01_{TAG}.json').write_text(json.dumps(bad, indent=2) + '\n', encoding='utf8')
t = ar.copy(); t[60, 40, :3] ^= 0x10
gate('control_tampered_png_detected', comp.tobytes() != t.tobytes() and not np.array_equal(canvas, t))
# east view: the real image must pass all eight; every control must fail at least one
C = pal['colors']; sa = rgba(sd / sm['files']['png']['file']); na = rgba(nd / nm['files']['png']['file'])
views = {'east': east_view(ar, C), 'control_mirrored_east': east_view(ar[:, ::-1].copy(), C), 'control_south': east_view(sa, C),
         'control_north': east_view(na, C)}
wp = sorted((R / BASE / 'west').glob('*west-static_*.png'))   # dirty, uncommitted west: read only, control use only
if wp:
    wa = rgba(wp[0]); views['control_stored_west'] = east_view(wa, C); views['control_mirrored_stored_west'] = east_view(wa[:, ::-1].copy(), C)
lq = sorted((R / OTHERS['lin-que-east']).glob('*east-static_*.png')); views['control_lin_que_east'] = east_view(rgba(lq[0]), C)
for k in PRED:
    gate(f'east_{k}', views['east'][k], {kk: views['east'][kk] for kk in views['east'] if not isinstance(views['east'][kk], bool)})
for k in views:
    if k.startswith('control_'):
        gate(f'{k}_rejected', not views[k]['east'], {kk: v for kk, v in views[k].items() if kk in PRED and not v})
opq = int(np.count_nonzero(al))
def coldiff(o): return int(np.count_nonzero((np.any(o[:, :, :3] != ar[:, :, :3], axis=2) | (o[:, :, 3] != al)) & (al > 0)))
if wp:
    d = coldiff(wa[:, ::-1]); gate('not_mirrored_west_pixels', d >= .35 * opq, {'opaque_colour_diff': d, 'east_opaque': opq, 'min': .35})
else:
    gate('not_mirrored_west_pixels', True, 'stored west absent; control skipped (disclosed)')
d = coldiff(sa); gate('not_south_recolour_pixels', d >= .40 * opq, {'opaque_colour_diff': d, 'east_opaque': opq, 'min': .40})
ph = sorted((R / PLACEHOLDER).glob('*milo*east*.png'))
gate('not_placeholder', all(Image.open(x).size != (80, 112) or rgba(x).tobytes() != ar.tobytes() for x in ph), [x.name for x in ph])
mask_diff = {}
for who, rel in OTHERS.items():
    others = [x for x in sorted((R / rel).glob('*.png')) if 'static' in x.name]
    o = rgba(others[0]); mask_diff[who] = {'file': others[0].name, 'differing_alpha_texels': int(np.count_nonzero((o[:, :, 3] > 0) != (al > 0))),
                                           'mirror_differing_alpha_texels': int(np.count_nonzero((o[:, ::-1, 3] > 0) != (al > 0)))}
gate('own_silhouette_not_recolour_or_mirror', all(min(v['differing_alpha_texels'], v['mirror_differing_alpha_texels']) >= 400 for v in mask_diff.values()), mask_diff)
pins = {x.name: sha(x) for x in sorted(f.iterdir()) if x.is_file()}
report = {'passed': all(c['passed'] for c in checks), 'checks': checks, 'views': views, 'sourceHashes': pins,
          'southHashes': {x.name: sha(x) for x in sorted(sd.iterdir()) if x.is_file()},
          'northHashes': {x.name: sha(x) for x in sorted(nd.iterdir()) if x.is_file()},
          'westControlRead': [x.name for x in wp], 'checkerSha256': sha(Path(__file__)),
          'hash': 'sha256 of raw bytes, no normalization',
          'scope': 'editable static source only; no GUI reliability, motion, ordinary adoption or art approval'}
(O / f'rpg-2-star-ocean-the-second_milo_east-independent-source-proof_v01_{TAG}.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
print(json.dumps(views, indent=1))
print('MILO_E01_INDEPENDENT', sum(c['passed'] for c in checks), '/', len(checks)); print('FAILURES', [c['id'] for c in checks if not c['passed']])
raise SystemExit(0 if report['passed'] else 1)
