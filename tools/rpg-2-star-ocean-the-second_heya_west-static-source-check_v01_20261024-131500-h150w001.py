"""Independent Heya WEST static source check (content.char.heya.static-west). No runtime/art/motion approval.

Does not import the Heya author. Reuses only the ORA stack parser/compositor from the Jiang static-source check
(as the Heya south, Lin Que, Muxiu and Yanke checkers do). Reads the game tree; writes only to --out.

Malformed controls are evaluated with the same gate functions on deliberately corrupted in-memory copies:
corrupt hash, tampered PNG pixel, visible guides, wrong direction (mirrored face), high bun, teeth in the mouth,
missing scarf, bag moved to the wrong hip, hidden charcoal dress. A control passes only when the corrupted copy
fails the corresponding gate.

  python -X utf8 -I <this> --root . --out outputs/heya-w150/independent-1
Exit 0 all checks pass, 1 any failure.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, io, json, os, zipfile
from PIL import Image
import numpy as np

ap = argparse.ArgumentParser(); ap.add_argument('--root', default='.'); ap.add_argument('--out', required=True)
a = ap.parse_args()
R = Path(a.root).resolve(); O = Path(a.out).resolve(); O.mkdir(parents=True, exist_ok=False)
if os.name == 'nt':
    R = Path('\\\\?\\' + str(R)); O = Path('\\\\?\\' + str(O))
sp = importlib.util.spec_from_file_location('ora_helpers', R / 'tools/rpg-2-star-ocean-the-second_jiang-lan_static-source-check_v01_20261021-235007-514b9771.py')
Hm = importlib.util.module_from_spec(sp); sp.loader.exec_module(Hm)
TAG = '20261024-131500-h150w001'
PORTRAIT = 'outputs/rpg-2-star-ocean-the-second_heya_character-sheet_v01_20261013-192811-6cbcb12e.png'
PORTRAIT_SHA = '918e8a17ea297a1eece49b4240712b19c08fab09eadc29eb7620d77b9a68e3e0'
SOUTH = R / 'game/assets/characters/heya-native-v01/south'
SOUTH_MANIFEST = SOUTH / 'rpg-2-star-ocean-the-second_heya_south-manifest_unapproved-v01_20261024-125310-a9210ea1.json'
SOUTH_MANIFEST_SHA = 'd6ddec7e38d74083e6a774d96e7235c9b64fe5ba7b7ec3664f5067f82217d80c'
PLACEHOLDER = 'game/assets/characters/native-animation'
OTHERS = {'heya-south': 'game/assets/characters/heya-native-v01/south',
          'muxiu-west': 'game/assets/characters/muxiu-native-v01/west'}
ANCHORS = ('braid', 'scarf', 'bag', 'apron', 'coat', 'hair', 'face', 'herb')
checks = []


def gate(n, v, detail=None): checks.append({'id': n, 'passed': bool(v), 'detail': detail})
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def hashes(m, f): return all(sha(f / v['file']) == v['rawsha256'] for v in m['files'].values())
def rgba(p): return np.array(Image.open(p).convert('RGBA'))
def mask_rgba(a): return a[:, :, 3] == 255


def west_facing(face):
    fm = face[:, :, 3] == 255
    nose_rows = fm[24:28].any(axis=0); back_rows = fm[17:22].any(axis=0)
    if not (nose_rows.any() and back_rows.any()):
        return False
    return int(np.nonzero(nose_rows)[0].min()) <= 32 and int(np.nonzero(back_rows)[0].max()) >= 45


def one_eye(face, e1):
    fm = face[:, :, 3] == 255
    n = 0
    for yy in range(22, 27):
        for xx in range(30, 40):
            if fm[yy, xx] and (face[yy, xx, :3] == np.frombuffer(e1, np.uint8)).all():
                n += 1
    return 1 <= n <= 8


def coil_ok(braid, h1, h3):
    bm = braid[:, :, 3] == 255
    if bm.sum() < 80:
        return False
    by, bx = np.nonzero(bm)
    return by.min() >= 23 and by.max() <= 40 and float(bx.mean()) >= 44.0 and int(bx.max()) >= 49


def hair_ok(hair):
    hm = hair[:, :, 3] == 255
    if not hm.any():
        return False
    hy, _ = np.nonzero(hm)
    return int(hy.max()) <= 30 and int(hy.min()) >= 8


def scarf_ok(scarf, cols):
    sm = scarf[:, :, 3] == 255
    if sm.sum() < 160:
        return False
    sy, _ = np.nonzero(sm)
    sl = {tuple(c) for c in scarf[sm][:, :3]}
    return int(sy.min()) <= 34 and int(sy.max()) >= 52 and sl <= cols


def bag_ok(bag, brass):
    bm = bag[:, :, 3] == 255
    if bm.sum() < 120:
        return False
    by, bx = np.nonzero(bm)
    bl = {tuple(c) for c in bag[bm][:, :3]}
    return 32.0 <= float(bx.mean()) <= 44.0 and bool(bl & brass) and int(by.max() - by.min() + 1) >= 12


def smile_ok(face, m1, e1):
    fm = face[:, :, 3] == 255
    mouth = np.zeros_like(fm)
    for yy in range(27, 32):
        for xx in range(28, 37):
            if fm[yy, xx] and (face[yy, xx, :3] == np.frombuffer(m1, np.uint8)).all():
                mouth[yy, xx] = True
    if not (3 <= mouth.sum() <= 6):
        return False
    my, mx = np.nonzero(mouth)
    teeth = any(fm[yy, xx] and (face[yy, xx, :3] == np.frombuffer(e1, np.uint8)).all()
                for yy in range(28, 31) for xx in range(28, 37))
    return not teeth and mx.max() - mx.min() + 1 <= 4


f = R / 'game/assets/characters/heya-native-v01/west'
ms = list(f.glob('*manifest*.json')); assert len(ms) == 1, 'missing/ambiguous manifest'
m = json.loads(ms[0].read_text(encoding='utf8'))
gate('identity', m['actor_id'] == 'heya' and m['content_id'] == 'content.char.heya.static-west'
     and m['direction'] == 'west' and m['status'] == 'UNAPPROVED')
gate('spec', m['canvas'] == [80, 112] and m['pivot'] == [40, 104] and m['body_rows'] == [8, 103]
     and m['display_scale'] == .5 and m['logical_height_px'] == 48)
gate('filehashes', hashes(m, f))
gate('portrait', m['portrait_ref']['file'] == PORTRAIT and m['portrait_ref']['expected_sha256'] == PORTRAIT_SHA
     and sha(R / PORTRAIT) == PORTRAIT_SHA and m['portrait_ref']['approval'] == 'UNAPPROVED')
gate('continuity_manifest', m['continuity_ref']['file'] == 'game/assets/characters/heya-native-v01/south/'
     + os.path.basename(str(SOUTH_MANIFEST)) and m['continuity_ref']['rawsha256'] == SOUTH_MANIFEST_SHA
     and sha(SOUTH_MANIFEST) == SOUTH_MANIFEST_SHA)
gate('filenames_lowercase_pattern', all(v['file'] == v['file'].lower()
     and v['file'].startswith('rpg-2-star-ocean-the-second_heya_west-') and '20261024' in v['file']
     for v in m['files'].values()))
png = f / m['files']['png']['file']; im = Image.open(png).convert('RGBA'); ar = np.array(im)
al = ar[:, :, 3]; ys, xs = np.nonzero(al)
gate('canvas', im.size == (80, 112)); gate('body_rows_8_103', ys.min() == 8 and ys.max() == 103,
                                          [int(ys.min()), int(ys.max())])
gate('logical_height_48', (ys.max() - ys.min() + 1) * .5 == 48)
feet = xs[ys == 103]; gate('pivot_x_within_feet_span', feet.min() <= 40 <= feet.max(), [int(feet.min()), int(feet.max())])
gate('binary_alpha', set(np.unique(al)) <= {0, 255})
gate('borders', not (al[0].any() or al[-1].any() or al[:, 0].any() or al[:, -1].any()))
pal = json.loads((f / m['files']['palette']['file']).read_text(encoding='utf8'))
decl = {tuple(bytes.fromhex(v.lstrip('#'))) for v in pal['colors'].values()}
used = {tuple(x) for x in ar[al == 255, :3]}
gate('palette', 24 <= len(used) <= 48 and used <= decl and len(decl) <= 40, len(used))
def has(*hx): return bool(used & {tuple(bytes.fromhex(pal['colors'][k])) for k in hx})
gate('identity_colours', has('h1', 'h2') and has('f1', 'f2') and has('b1', 'b2') and has('w1', 'w2')
     and has('v1', 'v2') and has('c1', 'c2') and has('r1', 'r2') and has('y1', 'y2') and has('n1', 'n2'),
     'auburn hair, grey-white scarf, dark-red bag, ivory coat, pale apron, charcoal dress, leather, brass, herb')
with zipfile.ZipFile(f / m['files']['ora']['file']) as z:
    ls = Hm.ora_layers(z); comp = Hm.compose(z, ls)
    gate('ora_composition', comp.tobytes() == ar.tobytes())
    gate('ora_merged', Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA').tobytes() == ar.tobytes())
    gate('ora_mimetype', z.infolist()[0].filename == 'mimetype' and z.infolist()[0].compress_type == zipfile.ZIP_STORED)
    visible = [l for l in ls if l['visible'] and not Hm.GUIDE_RE.search(l['name'])]
    contrib = {}
    for l in visible:
        without = Hm.compose(z, [x for x in ls if x is not l])
        contrib[l['name']] = int(np.count_nonzero(np.any(np.array(without) != ar, axis=2)))
    genuine = [n for n, c in contrib.items() if c >= 8]
    gate('genuine_ora_roles_ge_8', len(genuine) >= 8, contrib)
    gate('anchor_roles_contribute', all(contrib.get(n, 0) >= 12 for n in ANCHORS),
         {n: contrib.get(n) for n in ANCHORS})
    gate('hidden_guides', any(Hm.GUIDE_RE.search(l['name']) and not l['visible'] for l in ls)
         and not any(Hm.GUIDE_RE.search(l['name']) and l['visible'] for l in ls))
    shown = [dict(l, visible=True) if Hm.GUIDE_RE.search(l['name']) else l for l in ls]
    gate('control_visible_guides_detected', Hm.compose(z, shown).tobytes() != ar.tobytes())
    layers = {l['name']: np.array(Hm.compose(z, [l])) for l in ls}
    braid = layers['braid']; scarf = layers['scarf']; bag = layers['bag']; face_layer = layers['face']
    hair = layers['hair']; dress = layers['dress']; herb = layers['herb']
    e1 = bytes.fromhex(pal['colors']['e1']); m1 = bytes.fromhex(pal['colors']['m1'])
    scols = {tuple(bytes.fromhex(pal['colors'][k])) for k in ('f1', 'f2', 'f3')}
    brass = {tuple(bytes.fromhex(pal['colors'][k])) for k in ('y1', 'y2')}
    gate('profile_west_facing', west_facing(face_layer))
    gate('profile_face_narrow', int(np.ptp(np.nonzero(mask_rgba(face_layer))[1]) + 1) <= 20)
    gate('profile_depth_20_34', 20 <= int(xs.max() - xs.min() + 1) <= 34, int(xs.max() - xs.min() + 1))
    gate('profile_one_eye', one_eye(face_layer, e1))
    gate('coil_low_at_nape_west', coil_ok(braid, None, None), {'texels': int(mask_rgba(braid).sum())})
    gate('hair_not_high_bun_west', hair_ok(hair))
    gate('scarf_west', scarf_ok(scarf, scols), {'texels': int(mask_rgba(scarf).sum())})
    gate('bag_left_hip_west', bag_ok(bag, brass), {'texels': int(mask_rgba(bag).sum())})
    gate('restrained_smile_west', smile_ok(face_layer, m1, e1))
    dress_cols = {tuple(bytes.fromhex(pal['colors'][k])) for k in ('c1', 'c2')}
    dress_mask = np.zeros(ar.shape[:2], bool)
    for c in dress_cols:
        dress_mask |= np.all(ar[:, :, :3] == c, axis=2)
    charcoal_n = int(dress_mask.sum())
    gate('charcoal_dress_visible', charcoal_n >= 12, charcoal_n)
    gate('herb_visible_west', int(mask_rgba(herb).sum()) >= 12, int(mask_rgba(herb).sum()))
    gate('control_wrong_direction_detected', west_facing(face_layer[:, ::-1]) is False)
    gate('control_high_bun_detected', not coil_ok(np.roll(braid, -12, axis=0), None, None))
    gate('control_missing_scarf_detected', not scarf_ok(np.zeros_like(scarf), scols))
    gate('control_bag_wrong_hip_detected', not bag_ok(np.roll(bag, 10, axis=1), brass))
    bad_teeth = face_layer.copy(); bad_teeth[29, 35, :3] = np.frombuffer(e1, np.uint8); bad_teeth[29, 35, 3] = 255
    gate('control_teeth_detected', not smile_ok(bad_teeth, m1, e1))
    hidden = ar.copy(); hidden[dress_mask, :3] = np.frombuffer(bytes.fromhex(pal['colors']['w2']), np.uint8)
    hidden_n = sum(tuple(c) in dress_cols for c in hidden[al == 255, :3])
    gate('control_hidden_dress_detected', hidden_n < 12, hidden_n)
with zipfile.ZipFile(f / m['files']['pxo']['file']) as z:
    raw = z.read('data.json'); j = json.loads(raw); canvas = np.zeros_like(ar); roles = 0
    for i, l in enumerate(j['layers'], 1):
        x = np.frombuffer(z.read(f'image_data/frames/1/layer_{i}'), np.uint8).reshape(112, 80, 4)
        if l['visible']:
            mask = x[:, :, 3] > 0; canvas[mask] = x[mask]
            roles += int(np.count_nonzero(mask) >= 8 and not Hm.GUIDE_RE.search(l['name']))
    gate('pxo_composition', np.array_equal(canvas, ar)); gate('pxo_roles', roles >= 8, roles)
    gate('pxo_labels', b'heya-west' in raw and b'heya-south' not in raw
         and all(s not in raw for s in (b'protagonist-male', b'jiang-lan', b'lin-que', b'milo', b'muxiu', b'yanke')))
    gate('pxo_guides', any(l['name'] == 'guides' and not l['visible'] for l in j['layers']))
    gate('pxo_size', j['size_x'] == 80 and j['size_y'] == 112)
bad = json.loads(json.dumps(m)); bad['files']['png']['rawsha256'] = '0' * 64
gate('control_corrupt_hash_refused', hashes(m, f) and not hashes(bad, f))
(O / f'rpg-2-star-ocean-the-second_heya_corrupt-hash-control_test-only-v01_{TAG}.json').write_text(
    json.dumps(bad, indent=2) + '\n', encoding='utf8')
t = ar.copy(); t[60, 40, :3] ^= 0x10
gate('control_tampered_png_detected', comp.tobytes() != t.tobytes() and not np.array_equal(canvas, t))
ph = sorted((R / PLACEHOLDER).glob('*heya*.png'))
gate('not_placeholder', all(Image.open(x).size != (80, 112) or rgba(x).tobytes() != ar.tobytes() for x in ph),
     [x.name for x in ph])
mask_diff = {}
for who, rel in OTHERS.items():
    others = [x for x in sorted((R / rel).glob('*.png')) if 'static' in x.name]
    o = rgba(others[0]); mask_diff[who] = {'file': others[0].name,
                                           'differing_alpha_texels': int(np.count_nonzero((o[:, :, 3] > 0) != (al > 0)))}
gate('own_silhouette_not_recolour', all(v['differing_alpha_texels'] >= 400 for v in mask_diff.values()), mask_diff)
gate('west_only_package', f.is_dir() and not (f.parent / 'north').exists() and not (f.parent / 'east').exists()
     and (f / '.gdignore').exists())
sm = json.loads(SOUTH_MANIFEST.read_text(encoding='utf8'))
south_files = {v['file']: sha(SOUTH / v['file']) == v['rawsha256'] for v in sm['files'].values()}
gate('south_package_unchanged', all(south_files.values()), south_files)
pins = {x.name: sha(x) for x in sorted(f.iterdir()) if x.is_file()}
report = {'passed': all(c['passed'] for c in checks), 'checks': checks, 'sourceHashes': pins,
          'checkerSha256': sha(Path(__file__)), 'hash': 'sha256 of raw bytes, no normalization',
          'scope': 'editable static source only; no GUI reliability, motion, ordinary adoption or art approval'}
(O / f'rpg-2-star-ocean-the-second_heya_independent-source-proof_v01_{TAG}.json').write_text(
    json.dumps(report, indent=2) + '\n', encoding='utf8')
print('HEYA_W150_INDEPENDENT', sum(c['passed'] for c in checks), '/', len(checks))
print('FAILURES', [c['id'] for c in checks if not c['passed']])
for c in checks:
    if not c['passed'] or c['id'] in ('own_silhouette_not_recolour', 'anchor_roles_contribute',
                                      'coil_low_at_nape_west', 'scarf_west', 'bag_left_hip_west',
                                      'restrained_smile_west', 'profile_west_facing', 'charcoal_dress_visible'):
        print(c['id'], c['passed'], json.dumps(c['detail']))
raise SystemExit(0 if report['passed'] else 1)
