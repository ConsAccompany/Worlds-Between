"""Independent Milo north static source check (content.char.milo.static-north). No runtime/art/motion approval.

Does not import any Milo author. Reuses only the ORA stack parser/compositor from the Jiang static-source check
(as the committed Milo south checker does) and that checker's gate structure. North image predicates and
thresholds come from outputs/milo-n01/...north-style-source-contract...md (fixed before the first run).
Reads the game tree; writes only to --out.

  python -X utf8 -I <this> --root . --out outputs/milo-n01/independent
Exit 0 all checks pass, 1 any failure.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, io, json, os, zipfile
from PIL import Image
import numpy as np

ap = argparse.ArgumentParser(); ap.add_argument('--root', default='.'); ap.add_argument('--out', required=True); a = ap.parse_args()
R = Path(a.root).resolve(); O = Path(a.out).resolve(); O.mkdir(parents=True, exist_ok=True)
if os.name == 'nt': R = Path('\\\\?\\' + str(R)); O = Path('\\\\?\\' + str(O))
sp = importlib.util.spec_from_file_location('ora_helpers', R / 'tools/rpg-2-star-ocean-the-second_jiang-lan_static-source-check_v01_20261021-235007-514b9771.py')
Hm = importlib.util.module_from_spec(sp); sp.loader.exec_module(Hm)
TAG = '20261023-225642-1b612f93'
PORTRAIT = 'outputs/rpg-2-star-ocean-the-second_milo_character-sheet_hairstyle-v02_20261013-161317-f1651dc0.png'
PORTRAIT_SHA = '79a02c532681042ec389cfb6eae0577e3f967652641be7b853461e6adc4c244f'
SOUTH = 'game/assets/characters/milo-native-v01/south'
SOUTH_MANIFEST = SOUTH + '/rpg-2-star-ocean-the-second_milo_south-manifest_unapproved-v01_20261023-215823-e604f893.json'
SOUTH_MANIFEST_SHA = '913d3070528bfb8539c65e7570e73c5f7bedc1b45a23928ec9aa091db7324cf7'
OTHERS = {'jiang-lan-south': 'game/assets/characters/jiang-lan-native-south-v01',
          'lin-que-south': 'game/assets/characters/lin-que-native-v01/south',
          'lin-que-north': 'game/assets/characters/lin-que-native-v01/north'}
checks = []


def gate(n, v, detail=None): checks.append({'id': n, 'passed': bool(v), 'detail': detail})
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes(m, f): return all(sha(f / v['file']) == v['rawsha256'] for v in m['files'].values())
def rgba(p): return np.array(Image.open(p).convert('RGBA'))


f = R / 'game/assets/characters/milo-native-v01/north'
ms = list(f.glob('*manifest*.json')); assert len(ms) == 1, 'missing/ambiguous manifest'
m = json.loads(ms[0].read_text(encoding='utf8'))
gate('identity', m['actor_id'] == 'milo' and m['content_id'] == 'content.char.milo.static-north' and m['direction'] == 'north' and m['status'] == 'UNAPPROVED')
gate('spec', m['canvas'] == [80, 112] and m['pivot'] == [40, 104] and m['body_rows'] == [8, 103] and m['display_scale'] == .5 and m['logical_height_px'] == 48)
gate('filehashes', hashes(m, f))
p = m['portrait_ref']; gate('portrait', p['file'] == PORTRAIT and p['expected_sha256'] == PORTRAIT_SHA and sha(R / PORTRAIT) == PORTRAIT_SHA)
gate('filenames_lowercase_pattern', all(v['file'] == v['file'].lower() and v['file'].startswith('rpg-2-star-ocean-the-second_milo_north-') and TAG.split('-')[0] in v['file'] for v in m['files'].values()))
png = f / m['files']['png']['file']; im = Image.open(png).convert('RGBA'); ar = np.array(im); al = ar[:, :, 3]; ys, xs = np.nonzero(al)
gate('canvas', im.size == (80, 112)); gate('body_rows_8_103', ys.min() == 8 and ys.max() == 103, [int(ys.min()), int(ys.max())])
gate('logical_height_48', (ys.max() - ys.min() + 1) * .5 == 48)
feet = xs[ys == 103]; gate('pivot_x_within_feet_span', feet.min() <= 40 <= feet.max(), [int(feet.min()), int(feet.max())])
gate('binary_alpha', set(np.unique(al)) <= {0, 255}); gate('borders', not (al[0].any() or al[-1].any() or al[:, 0].any() or al[:, -1].any()))
pal = json.loads((f / m['files']['palette']['file']).read_text(encoding='utf8')); decl = {tuple(bytes.fromhex(v.lstrip('#'))) for v in pal['colors'].values()}
used = {tuple(x) for x in ar[al == 255, :3]}; gate('palette', 24 <= len(used) <= 48 and used <= decl, len(used))
def C(*hx): return {tuple(bytes.fromhex(pal['colors'][k])) for k in hx}
def has(*hx): return bool(used & C(*hx))
gate('identity_colours', has('g1', 'g2', 'g3') and has('a1', 'a2') and has('w1', 'w2') and has('n1', 'n2'), 'green, silver, white coat, navy present')

# --- south continuity: committed south package and palette unchanged; tampered south manifest refused ---
sm_path = R / SOUTH_MANIFEST; sm = json.loads(sm_path.read_text(encoding='utf8'))
gate('south_manifest_pinned', sha(sm_path) == SOUTH_MANIFEST_SHA)
gate('south_files_match_manifest', hashes(sm, R / SOUTH))
spal = json.loads((R / SOUTH / sm['files']['palette']['file']).read_text(encoding='utf8'))
gate('palette_colors_identical_to_south', spal['colors'] == pal['colors'])
tsm = json.loads(json.dumps(sm)); tsm['files']['png']['rawsha256'] = 'f' * 64
gate('control_tampered_south_manifest_refused', hashes(sm, R / SOUTH) and not hashes(tsm, R / SOUTH))


# --- north image predicates (contract 1..6) ---
def mask(a, cols, r0, r1, x0=0, x1=80):
    s = a[r0:r1 + 1, x0:x1 + 1]; op = s[:, :, 3] == 255
    hit = np.zeros(op.shape, bool)
    for c in cols: hit |= np.all(s[:, :, :3] == c, axis=2)
    return op, hit & op


def predicates(a):
    r = {}
    _, h = mask(a, C('e1', 'e2', 'm1'), 8, 40); r['no_face_features'] = int(h.sum()) == 0
    op, h = mask(a, C('h1', 'h2', 'h3', 'h4', 'a1', 'a2', 'a3'), 10, 26); r['head_hair_cover'] = op.sum() > 0 and h.sum() >= .75 * op.sum()
    _, h = mask(a, C('g1', 'g2', 'g3', 'g4'), 58, 64); gx = np.nonzero(h)[1]
    r['wristband_screen_left'] = gx.size > 0 and gx.mean() < 40
    op, _ = mask(a, set(), 63, 76); cx = np.nonzero(op)[1]
    r['case_screen_right'] = int((cx >= 58).sum()) >= 40 and int((cx <= 22).sum()) < 10
    op, h = mask(a, C('a1', 'a2', 'a3'), 8, 34); sx = np.nonzero(h)[1]; hx = np.nonzero(op)[1]
    r['silver_screen_right'] = sx.size > 0 and hx.size > 0 and sx.mean() > (hx.min() + hx.max()) / 2
    _, h = mask(a, C('n2', 'n3', 'x2'), 40, 56, 38, 42); r['no_front_opening'] = int(h.sum()) <= 5
    return r


real = predicates(ar)
for k, v in real.items(): gate(f'north_{k}', v)
sp_png = rgba(R / SOUTH / sm['files']['png']['file'])
controls = {'milo_south': sp_png, 'milo_south_mirrored': sp_png[:, ::-1], 'milo_north_mirrored': ar[:, ::-1]}
ctrl = {n: predicates(c) for n, c in controls.items()}
gate('control_predicates_reject_south_and_mirrors', all(not all(v.values()) for v in ctrl.values()),
     {n: [k for k, v in r.items() if not v] for n, r in ctrl.items()})

# not a mirror/recolour of Milo south: opaque-colour difference over north opaque texels
nop = al == 255; n_op = int(nop.sum()); cdiff = {}
for n in ('milo_south', 'milo_south_mirrored'):
    o = controls[n]; d = nop & ((o[:, :, 3] != 255) | np.any(o[:, :, :3] != ar[:, :, :3], axis=2))
    cdiff[n] = round(float(d.sum()) / n_op, 4)
gate('colour_content_differs_from_south_ge_40pct', all(v >= .40 for v in cdiff.values()), cdiff)

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
    gate('anchor_roles_contribute', all(contrib.get(n, 0) >= 12 for n in ('case', 'wristband', 'coat', 'hair', 'face')), {n: contrib.get(n) for n in ('case', 'wristband', 'coat', 'hair', 'face')})
    gate('hidden_guides', any(Hm.GUIDE_RE.search(l['name']) and not l['visible'] for l in ls) and not any(Hm.GUIDE_RE.search(l['name']) and l['visible'] for l in ls))
    shown = [dict(l, visible=True) if Hm.GUIDE_RE.search(l['name']) else l for l in ls]
    gate('control_visible_guides_detected', Hm.compose(z, shown).tobytes() != ar.tobytes())
with zipfile.ZipFile(f / m['files']['pxo']['file']) as z:
    raw = z.read('data.json'); j = json.loads(raw); canvas = np.zeros_like(ar); roles = 0
    for i, l in enumerate(j['layers'], 1):
        x = np.frombuffer(z.read(f'image_data/frames/1/layer_{i}'), np.uint8).reshape(112, 80, 4)
        if l['visible']:
            mk = x[:, :, 3] > 0; canvas[mk] = x[mk]; roles += int(np.count_nonzero(mk) >= 8 and not Hm.GUIDE_RE.search(l['name']))
    gate('pxo_composition', np.array_equal(canvas, ar)); gate('pxo_roles', roles >= 8, roles)
    gate('pxo_labels', all(s not in raw for s in (b'protagonist-male', b'jiang-lan', b'lin-que')) and b'milo' in raw)
    gate('pxo_labels_north', b'milo-north' in raw and b'milo-south' not in raw)
    gate('pxo_guides', any(l['name'] == 'guides' and not l['visible'] for l in j['layers']))
    gate('pxo_size', j['size_x'] == 80 and j['size_y'] == 112)
bad = json.loads(json.dumps(m)); bad['files']['png']['rawsha256'] = '0' * 64
gate('control_corrupt_hash_refused', hashes(m, f) and not hashes(bad, f))
(O / f'rpg-2-star-ocean-the-second_milo_north-corrupt-hash-control_test-only-v01_{TAG}.json').write_text(json.dumps(bad, indent=2) + '\n', encoding='utf8')
t = ar.copy(); t[60, 40, :3] ^= 0x10
gate('control_tampered_png_detected', comp.tobytes() != t.tobytes() and not np.array_equal(canvas, t))
# own silhouette vs other actors (direct and mirrored); Milo south excluded by contract (colour gate above instead)
mask_diff = {}
for who, rel in OTHERS.items():
    others = [x for x in sorted((R / rel).glob('*.png')) if 'static' in x.name]
    oa = rgba(others[0])[:, :, 3] > 0
    mask_diff[who] = {'file': others[0].name, 'direct': int(np.count_nonzero(oa != (al > 0))), 'mirrored': int(np.count_nonzero(oa[:, ::-1] != (al > 0)))}
gate('own_silhouette_not_recolour', all(v['direct'] >= 400 and v['mirrored'] >= 400 for v in mask_diff.values()), mask_diff)
pins = {x.name: sha(x) for x in sorted(f.iterdir()) if x.is_file()}
report = {'passed': all(c['passed'] for c in checks), 'checks': checks, 'northPredicates': real, 'controlPredicates': ctrl,
          'sourceHashes': pins, 'checkerSha256': sha(Path(__file__)), 'hash': 'sha256 of raw bytes, no normalization',
          'scope': 'editable static source only; no GUI reliability, motion, runtime integration or art approval'}
(O / f'rpg-2-star-ocean-the-second_milo_north-independent-source-proof_v01_{TAG}.json').write_text(json.dumps(report, indent=2, default=bool) + '\n', encoding='utf8')
print('MILO_N01_INDEPENDENT', sum(c['passed'] for c in checks), '/', len(checks)); print('FAILURES', [c['id'] for c in checks if not c['passed']])
print('CONTROL_FAILED_PREDICATES', {n: [k for k, v in r.items() if not v] for n, r in ctrl.items()}); print('COLOUR_DIFF', cdiff); print('MASK_DIFF', mask_diff)
raise SystemExit(0 if report['passed'] else 1)
