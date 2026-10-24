"""Independent Muxiu west static source check (content.char.muxiu.static-west). No runtime/art/motion approval.

Adapted from the Milo west and Muxiu south checkers. Does not import any Muxiu author. Reuses only the ORA stack
parser/compositor from the Jiang static-source check (as the Lin Que, Milo and Muxiu south checkers do). Reads the
game tree; writes only to --out (must be new). Image-level west predicates (one eye, face leads screen left, hair at
the back, profile asymmetry) plus Muxiu profile identity (braid knot at the nape AND plait hanging at the chest
front; rope bracelet on the near wrist; moss cloak dominant), each also run on negative controls (mirrored west,
south image, mirrored south, squashed south, corrupt hash, tampered PNG, visible guides, tampered south manifest).

  python -X utf8 -I <this> --root . --out outputs/muxiu-w01/independent-<new>
Exit 0 all checks pass, 1 any failure.
"""
from pathlib import Path
from collections import deque
import argparse, hashlib, importlib.util, io, json, os, zipfile
from PIL import Image
import numpy as np

ap = argparse.ArgumentParser(); ap.add_argument('--root', default='.'); ap.add_argument('--out', required=True); a = ap.parse_args()
R = Path(a.root).resolve(); O = Path(a.out).resolve(); O.mkdir(parents=True, exist_ok=False)
if os.name == 'nt': R = Path('\\\\?\\' + str(R)); O = Path('\\\\?\\' + str(O))
sp = importlib.util.spec_from_file_location('ora_helpers', R / 'tools/rpg-2-star-ocean-the-second_jiang-lan_static-source-check_v01_20261021-235007-514b9771.py')
Hm = importlib.util.module_from_spec(sp); sp.loader.exec_module(Hm)
TAG = '20261024-055724-17c9961a'
PORTRAIT = 'outputs/rpg-2-star-ocean-the-second_muxiu_character-sheet_v01_20261013-153818-25247999.png'
PORTRAIT_SHA = '9d80d2d7fc26ea10edd36948e620fbb5a5557db143eacb99fcb202347c22d606'
SOUTH = 'game/assets/characters/muxiu-native-v01/south'
SOUTH_MANIFEST = 'rpg-2-star-ocean-the-second_muxiu_south-manifest_unapproved-v01_20261024-071500-dd478113.json'
SOUTH_MANIFEST_SHA = '24c751575fe02a4857628dbfb8b379cd1d42344167062ae8ddbb033024e114de'   # committed f556e74e
PLACEHOLDER = 'game/assets/characters/native-animation'
OTHERS = {'jiang-lan-south': 'game/assets/characters/jiang-lan-native-south-v01', 'lin-que-south': 'game/assets/characters/lin-que-native-v01/south',
          'lin-que-west': 'game/assets/characters/lin-que-native-v01/west', 'milo-south': 'game/assets/characters/milo-native-v01/south',
          'muxiu-south': SOUTH}
ANCHORS = ('cloak', 'braid', 'bracelet', 'whistle', 'hair', 'face')
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


def west_view(ar, pal):
    """Image-level west predicates. Thresholds copied unchanged from the Milo west checker (fixed before any run)."""
    def keys(*k): return {tuple(bytes.fromhex(pal[x])) for x in k}
    rgb = ar[:, :, :3]; op = ar[:, :, 3] == 255
    inset = lambda ks: np.array([[op[y, x] and tuple(rgb[y, x]) in ks for x in range(ar.shape[1])] for y in range(ar.shape[0])])
    skin, hair = keys('s1', 's2', 's3', 's4', 'm1', 'e1', 'e2'), keys('h1', 'h2', 'h3', 'h4')
    iris = inset(keys('e2')); iris[34:] = False; iris[:12] = False
    iris_n = components(iris)
    ys, xs = np.nonzero(op[8:34]); head_mid = (xs.min() + xs.max()) / 2
    front_skin = sum(tuple(rgb[y, np.nonzero(op[y])[0].min()]) in skin for y in range(18, 31))     # 13 rows
    back_hair = sum(tuple(rgb[y, np.nonzero(op[y])[0].max()]) in hair for y in range(12, 27))      # 15 rows
    yb, xb = np.nonzero(op); m = op[yb.min():yb.max() + 1, xb.min():xb.max() + 1]
    mirror_iou = float((m & m[:, ::-1]).sum() / (m | m[:, ::-1]).sum())
    r = {'iris_components': iris_n, 'iris_x_mean': float(np.nonzero(iris)[1].mean()) if iris.any() else None,
         'head_mid_x': float(head_mid), 'front_edge_skin_rows_of_13': int(front_skin), 'back_edge_hair_rows_of_15': int(back_hair),
         'mirror_iou': round(mirror_iou, 4), 'bbox_width': int(xb.max() - xb.min() + 1)}
    r['one_eye'] = bool(iris_n == 1)
    r['eye_in_front_half'] = bool(r['iris_x_mean'] is not None and r['iris_x_mean'] < head_mid)
    r['face_leads_left'] = bool(front_skin >= 8)
    r['hair_at_back'] = bool(back_hair >= 10)
    r['profile_asymmetric'] = bool(mirror_iou <= .80)
    r['west'] = all(r[k] for k in ('one_eye', 'eye_in_front_half', 'face_leads_left', 'hair_at_back', 'profile_asymmetric'))
    return r


def squash_to(src, ref):
    """Nearest-neighbour squash of src's opaque bbox into ref's opaque bbox (the shortcut west must not be)."""
    yb, xb = np.nonzero(src[:, :, 3]); crop = Image.fromarray(src[yb.min():yb.max() + 1, xb.min():xb.max() + 1])
    yr, xr = np.nonzero(ref[:, :, 3]); out = np.zeros_like(ref)
    out[yr.min():yr.max() + 1, xr.min():xr.max() + 1] = np.array(crop.resize((int(xr.max() - xr.min() + 1), int(yr.max() - yr.min() + 1)), Image.NEAREST))
    return out


f = R / 'game/assets/characters/muxiu-native-v01/west'
ms = list(f.glob('*manifest*.json')); assert len(ms) == 1, 'missing/ambiguous manifest'
m = json.loads(ms[0].read_text(encoding='utf8'))
gate('identity', m['actor_id'] == 'muxiu' and m['content_id'] == 'content.char.muxiu.static-west' and m['direction'] == 'west' and m['status'] == 'UNAPPROVED')
gate('spec', m['canvas'] == [80, 112] and m['pivot'] == [40, 104] and m['body_rows'] == [8, 103] and m['display_scale'] == .5 and m['logical_height_px'] == 48)
gate('filehashes', hashes(m, f))
p = m['portrait_ref']; gate('portrait', p['file'] == PORTRAIT and p['expected_sha256'] == PORTRAIT_SHA and sha(R / PORTRAIT) == PORTRAIT_SHA and p['approval'] == 'UNAPPROVED')
gate('filenames_lowercase_pattern', all(v['file'] == v['file'].lower() and v['file'].startswith('rpg-2-star-ocean-the-second_muxiu_west-') and TAG.split('-')[0] in v['file'] for v in m['files'].values()))
gate('parent_gdignore', (R / 'game/assets/characters/muxiu-native-v01/.gdignore').is_file())
png = f / m['files']['png']['file']; im = Image.open(png).convert('RGBA'); ar = np.array(im); al = ar[:, :, 3]; ys, xs = np.nonzero(al)
gate('canvas', im.size == (80, 112)); gate('body_rows_8_103', ys.min() == 8 and ys.max() == 103, [int(ys.min()), int(ys.max())])
gate('logical_height_48', (ys.max() - ys.min() + 1) * .5 == 48)
feet = xs[ys == 103]; gate('pivot_x_within_feet_span', feet.min() <= 40 <= feet.max(), [int(feet.min()), int(feet.max())])
gate('binary_alpha', set(np.unique(al)) <= {0, 255}); gate('borders', not (al[0].any() or al[-1].any() or al[:, 0].any() or al[:, -1].any()))
pal = json.loads((f / m['files']['palette']['file']).read_text(encoding='utf8')); decl = {tuple(bytes.fromhex(v.lstrip('#'))) for v in pal['colors'].values()}
used = {tuple(x) for x in ar[al == 255, :3]}; gate('palette', 24 <= len(used) <= 48 and used <= decl and len(decl) <= 40, len(used))
def has(*hx): return bool(used & {tuple(bytes.fromhex(pal['colors'][k])) for k in hx})
gate('identity_colours', has('c1', 'c2') and has('h1', 'h2') and has('w1', 'w2') and has('q1', 'q2') and has('t1', 't2'),
     'moss cloak, brown hair, cream shirt, tan rope, olive trousers present')
moss = {tuple(bytes.fromhex(pal['colors'][k])) for k in ('c1', 'c2', 'c3')}
moss_n = int(sum(tuple(x) in moss for x in ar[al == 255, :3])); gate('moss_cloak_dominant', moss_n >= 0.2 * int((al == 255).sum()), moss_n)
iso = isolated(ar); gate('isolated_texels_le_24', iso <= 24, iso)
# south continuity: committed south package unchanged and the west palette is identical in colours
sd = R / SOUTH; smp = sd / SOUTH_MANIFEST; sm = json.loads(smp.read_text(encoding='utf8'))
gate('south_manifest_pinned', sha(smp) == SOUTH_MANIFEST_SHA)
gate('south_files_unchanged', hashes(sm, sd), {v['file']: v['rawsha256'][:12] for v in sm['files'].values()})
spal = json.loads((sd / sm['files']['palette']['file']).read_text(encoding='utf8'))
gate('palette_colours_identical_to_south', spal['colors'] == pal['colors'])
bad_s = json.loads(json.dumps(sm)); bad_s['files']['png']['rawsha256'] = 'f' * 64
gate('control_tampered_south_manifest_refused', hashes(sm, sd) and not hashes(bad_s, sd))
head_mid = None
with zipfile.ZipFile(f / m['files']['ora']['file']) as z:
    ls = Hm.ora_layers(z); comp = Hm.compose(z, ls)
    gate('ora_composition', comp.tobytes() == ar.tobytes())
    gate('ora_merged', Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA').tobytes() == ar.tobytes())
    gate('ora_mimetype', z.infolist()[0].filename == 'mimetype' and z.infolist()[0].compress_type == zipfile.ZIP_STORED)
    gate('ora_layer_names_match_south', sorted(l['name'] for l in ls) == sorted(x['name'] for x in sm['layers']), [l['name'] for l in ls])
    visible = [l for l in ls if l['visible'] and not Hm.GUIDE_RE.search(l['name'])]; contrib = {}
    for l in visible:
        without = Hm.compose(z, [x for x in ls if x is not l]); contrib[l['name']] = int(np.count_nonzero(np.any(np.array(without) != ar, axis=2)))
    genuine = [n for n, c in contrib.items() if c >= 8]
    gate('genuine_ora_roles_ge_8', len(genuine) >= 8, contrib)
    gate('anchor_roles_contribute', all(contrib.get(n, 0) >= 12 for n in ANCHORS), {n: contrib.get(n) for n in ANCHORS})
    lay = lambda n: np.array(Hm.compose(z, [next(l for l in ls if l['name'] == n)]))[:, :, 3] > 0
    hy, hx = np.nonzero(al[8:34] > 0); head_mid = (hx.min() + hx.max()) / 2
    by, bx = np.nonzero(lay('braid'))
    knot = (by <= 33) & (bx > head_mid); hang = (by >= 45) & (bx < head_mid)
    # profile braid: knot at the nape (back of head, screen right) AND plait hanging past the chest front, below row 60
    gate('braid_nape_knot_and_front_hang', knot.sum() >= 12 and hang.sum() >= 24 and by.max() >= 60,
         {'knot': int(knot.sum()), 'front_hang': int(hang.sum()), 'max_row': int(by.max()), 'head_mid_x': float(head_mid)})
    qy, qx = np.nonzero(lay('bracelet')); ay, axx = np.nonzero(lay('arms'))
    gate('bracelet_on_near_wrist', 60 <= qy.min() and qy.max() <= 76 and axx.min() <= qx.mean() <= axx.max(),
         {'rows': [int(qy.min()), int(qy.max())], 'x_mean': float(qx.mean()), 'arm_x': [int(axx.min()), int(axx.max())]})
    wy, wx = np.nonzero(lay('whistle'))
    gate('whistle_at_chest_front', 32 <= wy.min() and wy.max() <= 48 and wx.mean() < 40, {'rows': [int(wy.min()), int(wy.max())], 'x_mean': float(wx.mean())})
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
    gate('pxo_labels', all(s not in raw for s in (b'protagonist-male', b'jiang-lan', b'lin-que', b'milo', b'muxiu-south')) and b'muxiu-west' in raw)
    gate('pxo_guides', any(l['name'] == 'guides' and not l['visible'] for l in j['layers']))
    gate('pxo_size', j['size_x'] == 80 and j['size_y'] == 112)
bad = json.loads(json.dumps(m)); bad['files']['png']['rawsha256'] = '0' * 64
gate('control_corrupt_hash_refused', hashes(m, f) and not hashes(bad, f))
(O / f'rpg-2-star-ocean-the-second_muxiu_west-corrupt-hash-control_test-only-v01_{TAG}.json').write_text(json.dumps(bad, indent=2) + '\n', encoding='utf8')
t = ar.copy(); t[60, 40, :3] ^= 0x10
gate('control_tampered_png_detected', comp.tobytes() != t.tobytes() and not np.array_equal(canvas, t))
# west view: the real image must pass; mirrored west, south, mirrored south and squashed south must each fail
C = pal['colors']; sa = rgba(sd / sm['files']['png']['file'])
views = {'west': west_view(ar, C), 'control_mirrored_west': west_view(ar[:, ::-1].copy(), C), 'control_south': west_view(sa, C),
         'control_mirrored_south': west_view(sa[:, ::-1].copy(), C), 'control_squashed_south': west_view(squash_to(sa, ar), C)}
for k in ('one_eye', 'eye_in_front_half', 'face_leads_left', 'hair_at_back', 'profile_asymmetric'):
    gate(f'west_{k}', views['west'][k], {kk: views['west'][kk] for kk in views['west'] if not isinstance(views['west'][kk], bool)})
for k in ('control_mirrored_west', 'control_south', 'control_mirrored_south', 'control_squashed_south'):
    gate(f'{k}_rejected', not views[k]['west'], views[k])
sq = squash_to(sa, ar); diff = int(np.count_nonzero((sq[:, :, 3] > 0) != (al > 0)))
col = int(np.count_nonzero(np.any(sq[:, :, :3] != ar[:, :, :3], axis=2) & (al > 0)))
gate('not_south_squash_pixels', col >= .5 * np.count_nonzero(al), {'alpha_diff': diff, 'opaque_colour_diff': col, 'west_opaque': int(np.count_nonzero(al))})
ph = sorted((R / PLACEHOLDER).glob('*muxiu*.png'))
gate('not_placeholder', all(Image.open(x).size != (80, 112) or rgba(x).tobytes() != ar.tobytes() for x in ph), [x.name for x in ph])
mask_diff = {}
for who, rel in OTHERS.items():
    others = [x for x in sorted((R / rel).glob('*.png')) if 'static' in x.name]
    o = rgba(others[0]); mask_diff[who] = {'file': others[0].name, 'differing_alpha_texels': int(np.count_nonzero((o[:, :, 3] > 0) != (al > 0))),
                                           'mirror_differing_alpha_texels': int(np.count_nonzero((o[:, ::-1, 3] > 0) != (al > 0)))}
gate('own_silhouette_not_recolour_or_mirror', all(min(v['differing_alpha_texels'], v['mirror_differing_alpha_texels']) >= 400 for v in mask_diff.values()), mask_diff)
pins = {x.name: sha(x) for x in sorted(f.iterdir()) if x.is_file()}
report = {'passed': all(c['passed'] for c in checks), 'checks': checks, 'views': views, 'sourceHashes': pins,
          'southHashes': {x.name: sha(x) for x in sorted(sd.iterdir()) if x.is_file()}, 'checkerSha256': sha(Path(__file__)),
          'hash': 'sha256 of raw bytes, no normalization',
          'scope': 'editable static source only; no GUI reliability, motion, ordinary adoption or art approval'}
(O / f'rpg-2-star-ocean-the-second_muxiu_west-independent-source-proof_v01_{TAG}.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
print(json.dumps(views, indent=1))
print('MUXIU_W01_INDEPENDENT', sum(c['passed'] for c in checks), '/', len(checks)); print('FAILURES', [c['id'] for c in checks if not c['passed']])
for c in checks:
    if not c['passed'] or c['id'] in ('own_silhouette_not_recolour_or_mirror', 'anchor_roles_contribute', 'braid_nape_knot_and_front_hang',
                                      'bracelet_on_near_wrist', 'whistle_at_chest_front', 'isolated_texels_le_24', 'not_placeholder'):
        print(c['id'], c['passed'], json.dumps(c['detail']))
raise SystemExit(0 if report['passed'] else 1)
