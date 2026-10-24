"""Independent Heya EAST static source check (content.char.heya.static-east). No runtime/art/motion approval.

Does not import the Heya author. Reuses only the ORA stack parser/compositor from the Jiang static-source check
(as the Heya south/west/north checkers do). Reads the game tree; writes only to --out. Supports a coordinator
independent rerun:  python -X utf8 -I <this> --root . --out outputs/heya-e155/independent-1

Malformed/wrong-facing controls are evaluated with the same gate functions on deliberately corrupted in-memory
copies: corrupt hash, tampered PNG pixel, visible guides, wrong direction (mirrored face), mirrored lighting,
high bun, teeth in the mouth, missing scarf, bag moved to the wrong hip, hidden charcoal dress. A control passes
only when the corrupted copy fails the corresponding gate.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, io, json, zipfile
from PIL import Image
import numpy as np

ap = argparse.ArgumentParser(); ap.add_argument('--root', default='.'); ap.add_argument('--out', required=True)
a = ap.parse_args()
R = Path(a.root).resolve(); O = Path(a.out).resolve(); O.mkdir(parents=True, exist_ok=False)
if __import__('os').name == 'nt':
    R = Path('\\\\?\\' + str(R)); O = Path('\\\\?\\' + str(O))
sp = importlib.util.spec_from_file_location(
    'ora_helpers', R / 'tools/rpg-2-star-ocean-the-second_jiang-lan_static-source-check_v01_20261021-235007-514b9771.py')
Hm = importlib.util.module_from_spec(sp); sp.loader.exec_module(Hm)
TAG = '20261024-141500-h155e001'
PORTRAIT = 'outputs/rpg-2-star-ocean-the-second_heya_character-sheet_v01_20261013-192811-6cbcb12e.png'
PORTRAIT_SHA = '918e8a17ea297a1eece49b4240712b19c08fab09eadc29eb7620d77b9a68e3e0'
SOUTH = R / 'game/assets/characters/heya-native-v01/south'
SOUTH_MANIFEST = SOUTH / 'rpg-2-star-ocean-the-second_heya_south-manifest_unapproved-v01_20261024-125310-a9210ea1.json'
SOUTH_MANIFEST_SHA = 'd6ddec7e38d74083e6a774d96e7235c9b64fe5ba7b7ec3664f5067f82217d80c'
WEST = R / 'game/assets/characters/heya-native-v01/west'
WEST_MANIFEST = WEST / 'rpg-2-star-ocean-the-second_heya_west-manifest_unapproved-v01_20261024-131500-164571cd.json'
WEST_MANIFEST_SHA = '75b0519c2b1282dc4441b38a90fa3bc64868a442f1779c436455928fd8897752'
NORTH = R / 'game/assets/characters/heya-native-v01/north'
NORTH_MANIFEST = NORTH / 'rpg-2-star-ocean-the-second_heya_north-manifest_unapproved-v01_20261024-134500-ee613b85.json'
NORTH_MANIFEST_SHA = '7445095eec59c152a0f580acf0d63f17ec900be4824c1eb35cd2fc7a8064c0f7'
PLACEHOLDER = 'game/assets/characters/native-animation'
ANCHORS = ('braid', 'scarf', 'bag', 'apron', 'coat', 'hair', 'face', 'herb', 'arms', 'boots', 'dress')
checks = []


def gate(n, v, detail=None):
    checks.append({'id': n, 'passed': bool(v), 'detail': detail})


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def hashes(m, f): return all(sha(f / v['file']) == v['rawsha256'] for v in m['files'].values())
def rgba(p): return np.array(Image.open(p).convert('RGBA'))
def mask(a): return a[:, :, 3] == 255


def east_facing(face):
    fm = mask(face)
    nose_rows = fm[24:28].any(axis=0); back_rows = fm[17:22].any(axis=0)
    if not (nose_rows.any() and back_rows.any()):
        return False
    return int(np.nonzero(nose_rows)[0].max()) >= 48 and int(np.nonzero(back_rows)[0].min()) <= 35


def one_eye(face, e1):
    fm = mask(face); n = 0
    for yy in range(21, 27):
        for xx in range(40, 50):
            if fm[yy, xx] and (face[yy, xx, :3] == np.frombuffer(e1, np.uint8)).all():
                n += 1
    return 1 <= n <= 8


def mature_face(face, s3):
    fm = mask(face); n = 0
    for yy in range(25, 33):
        for xx in range(36, 50):
            if fm[yy, xx] and (face[yy, xx, :3] == np.frombuffer(s3, np.uint8)).all():
                n += 1
    return n >= 10


def coil_ok(braid):
    bm = mask(braid)
    if bm.sum() < 80:
        return False
    by, bx = np.nonzero(bm)
    return by.min() >= 23 and by.max() <= 40 and float(bx.mean()) <= 37.0 and int(bx.min()) <= 30


def hair_ok(hair):
    hm = mask(hair)
    if not hm.any():
        return False
    hy, _ = np.nonzero(hm)
    return int(hy.max()) <= 30 and int(hy.min()) >= 8


def scarf_ok(scarf, cols):
    sm = mask(scarf)
    if sm.sum() < 160:
        return False
    sy, _ = np.nonzero(sm)
    sl = {tuple(c) for c in scarf[sm][:, :3]}
    return int(sy.min()) <= 34 and int(sy.max()) >= 52 and sl <= cols


def bag_ok(bag, brass, red):
    bm = mask(bag)
    if bm.sum() < 80:
        return False
    by, bx = np.nonzero(bm)
    bl = {tuple(c) for c in bag[bm][:, :3]}
    return (float(bx.mean()) <= 30.0 and int(bx.max()) <= 34 and bool(bl & red) and bool(bl & brass)
            and int(by.max() - by.min() + 1) >= 12)


def smile_ok(face, m1, e1):
    fm = mask(face); mouth = np.zeros_like(fm)
    for yy in range(27, 32):
        for xx in range(42, 50):
            if fm[yy, xx] and (face[yy, xx, :3] == np.frombuffer(m1, np.uint8)).all():
                mouth[yy, xx] = True
    if not (3 <= mouth.sum() <= 6):
        return False
    _, mx = np.nonzero(mouth)
    teeth = any(fm[yy, xx] and (face[yy, xx, :3] == np.frombuffer(e1, np.uint8)).all()
                for yy in range(28, 31) for xx in range(42, 50))
    return not teeth and mx.max() - mx.min() + 1 <= 4


def colour_mean_x(ar, keys, palette):
    m = np.zeros(ar.shape[:2], bool)
    for k in keys:
        m |= np.all(ar[:, :, :3] == np.frombuffer(bytes.fromhex(palette[k]), np.uint8), axis=2) & (ar[:, :, 3] == 255)
    _, xx = np.nonzero(m)
    return (float(xx.mean()), int(m.sum())) if len(xx) else (None, 0)


def upper_left_light(ar, palette):
    pairs = [('hair', ('h1',), ('h3',)), ('coat', ('w1',), ('w3',)), ('skin', ('s1',), ('s3',))]
    out = {}
    for name, lo, dk in pairs:
        a, b = colour_mean_x(ar, lo, palette), colour_mean_x(ar, dk, palette)
        out[name] = [list(a), list(b)]
        if a[0] is None or b[0] is None or a[1] < 20 or b[1] < 20 or not a[0] < b[0]:
            return False, out
    return True, out


f = R / 'game/assets/characters/heya-native-v01/east'
ms = list(f.glob('*manifest*.json')); assert len(ms) == 1, 'missing/ambiguous east manifest'
m = json.loads(ms[0].read_text(encoding='utf8'))
gate('identity', m['actor_id'] == 'heya' and m['content_id'] == 'content.char.heya.static-east'
     and m['direction'] == 'east' and m['status'] == 'UNAPPROVED')
gate('spec', m['canvas'] == [80, 112] and m['pivot'] == [40, 104] and m['body_rows'] == [8, 103]
     and m['display_scale'] == .5 and m['logical_height_px'] == 48)
gate('filehashes', hashes(m, f))
gate('portrait', m['portrait_ref']['file'] == PORTRAIT and m['portrait_ref']['expected_sha256'] == PORTRAIT_SHA
     and sha(R / PORTRAIT) == PORTRAIT_SHA and m['portrait_ref']['approval'] == 'UNAPPROVED')
gate('continuity_south', m['continuity_ref']['file'] == 'game/assets/characters/heya-native-v01/south/'
     + SOUTH_MANIFEST.name and m['continuity_ref']['rawsha256'] == SOUTH_MANIFEST_SHA
     and sha(SOUTH_MANIFEST) == SOUTH_MANIFEST_SHA)
gate('continuity_west', m['west_continuity_ref']['rawsha256'] == WEST_MANIFEST_SHA
     and sha(WEST_MANIFEST) == WEST_MANIFEST_SHA)
gate('continuity_north', m['north_continuity_ref']['rawsha256'] == NORTH_MANIFEST_SHA
     and sha(NORTH_MANIFEST) == NORTH_MANIFEST_SHA)
gate('filenames_lowercase_pattern', all(v['file'] == v['file'].lower()
     and v['file'].startswith('rpg-2-star-ocean-the-second_heya_east-') and '20261024' in v['file']
     for v in m['files'].values()))
png = f / m['files']['png']['file']; im = Image.open(png).convert('RGBA'); ar = np.array(im)
al = ar[:, :, 3]; ys, xs = np.nonzero(al)
gate('canvas', im.size == (80, 112))
gate('body_rows_8_103', ys.min() == 8 and ys.max() == 103, [int(ys.min()), int(ys.max())])
gate('logical_height_48', (ys.max() - ys.min() + 1) * .5 == 48)
feet = xs[ys == 103]
gate('pivot_x_within_feet_span', feet.min() <= 40 <= feet.max(), [int(feet.min()), int(feet.max())])
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
    s3 = bytes.fromhex(pal['colors']['s3'])
    scols = {tuple(bytes.fromhex(pal['colors'][k])) for k in ('f1', 'f2', 'f3')}
    brass = {tuple(bytes.fromhex(pal['colors'][k])) for k in ('y1', 'y2')}
    red = {tuple(bytes.fromhex(pal['colors'][k])) for k in ('b1', 'b2')}
    gate('profile_east_facing', east_facing(face_layer))
    gate('profile_face_narrow', int(np.ptp(np.nonzero(mask(face_layer))[1]) + 1) <= 20)
    gate('profile_depth_20_34', 20 <= int(xs.max() - xs.min() + 1) <= 34, int(xs.max() - xs.min() + 1))
    gate('profile_one_eye', one_eye(face_layer, e1))
    gate('mature_face_shading', mature_face(face_layer, s3))
    gate('coil_low_at_nape_east', coil_ok(braid), {'texels': int(mask(braid).sum())})
    gate('hair_not_high_bun_east', hair_ok(hair))
    gate('scarf_east', scarf_ok(scarf, scols), {'texels': int(mask(scarf).sum())})
    gate('bag_left_hip_far_east', bag_ok(bag, brass, red), {'texels': int(mask(bag).sum())})
    gate('restrained_smile_east', smile_ok(face_layer, m1, e1))
    dress_cols = {tuple(bytes.fromhex(pal['colors'][k])) for k in ('c1', 'c2')}
    dress_mask = np.zeros(ar.shape[:2], bool)
    for c in dress_cols:
        dress_mask |= np.all(ar[:, :, :3] == c, axis=2)
    charcoal_n = int((dress_mask & (al == 255)).sum())
    gate('charcoal_dress_visible', charcoal_n >= 12, charcoal_n)
    gate('herb_visible_east', int(mask(herb).sum()) >= 12, int(mask(herb).sum()))
    light_ok, light_detail = upper_left_light(ar, pal['colors'])
    gate('upper_left_light_east', light_ok, light_detail)
    gate('control_wrong_direction_detected', east_facing(face_layer[:, ::-1]) is False)
    gate('control_mirrored_light_detected', upper_left_light(ar[:, ::-1], pal['colors'])[0] is False)
    gate('control_high_bun_detected', not coil_ok(np.roll(braid, -12, axis=0)))
    gate('control_missing_scarf_detected', not scarf_ok(np.zeros_like(scarf), scols))
    gate('control_bag_wrong_hip_detected', not bag_ok(np.roll(bag, 10, axis=1), brass, red))
    bad_teeth = face_layer.copy(); bad_teeth[29, 46, :3] = np.frombuffer(e1, np.uint8); bad_teeth[29, 46, 3] = 255
    gate('control_teeth_detected', not smile_ok(bad_teeth, m1, e1))
    hidden = ar.copy(); hidden[dress_mask, :3] = np.frombuffer(bytes.fromhex(pal['colors']['w2']), np.uint8)
    hidden_n = sum(tuple(c) in dress_cols for c in hidden[al == 255, :3])
    gate('control_hidden_dress_detected', hidden_n < 12, hidden_n)
with zipfile.ZipFile(f / m['files']['pxo']['file']) as z:
    raw = z.read('data.json'); j = json.loads(raw); canvas = np.zeros_like(ar); roles = 0
    for i, l in enumerate(j['layers'], 1):
        x = np.frombuffer(z.read(f'image_data/frames/1/layer_{i}'), np.uint8).reshape(112, 80, 4)
        if l['visible']:
            maskx = x[:, :, 3] > 0; canvas[maskx] = x[maskx]
            roles += int(np.count_nonzero(maskx) >= 8 and not Hm.GUIDE_RE.search(l['name']))
    gate('pxo_composition', np.array_equal(canvas, ar))
    gate('pxo_roles', roles >= 8, roles)
    gate('pxo_labels', b'heya-east' in raw and all(s not in raw for s in (
        b'heya-south', b'heya-west', b'heya-north', b'protagonist-male', b'jiang-lan', b'lin-que', b'milo',
        b'muxiu', b'yanke')))
    gate('pxo_guides', any(l['name'] == 'guides' and not l['visible'] for l in j['layers']))
    gate('pxo_size', j['size_x'] == 80 and j['size_y'] == 112)
bad = json.loads(json.dumps(m)); bad['files']['png']['rawsha256'] = '0' * 64
gate('control_corrupt_hash_refused', hashes(m, f) and not hashes(bad, f))
(O / f'rpg-2-star-ocean-the-second_heya_east_corrupt-hash-control_test-only-v01_{TAG}.json').write_text(
    json.dumps(bad, indent=2) + '\n', encoding='utf8')
t = ar.copy(); t[60, 40, :3] ^= 0x10
gate('control_tampered_png_detected', comp.tobytes() != t.tobytes() and not np.array_equal(canvas, t))
ph = sorted((R / PLACEHOLDER).glob('*heya*.png'))
gate('not_placeholder', all(Image.open(x).size != (80, 112) or rgba(x).tobytes() != ar.tobytes() for x in ph),
     [x.name for x in ph])
mask_diff = {}
for who, path in (('south', SOUTH), ('west', WEST), ('north', NORTH)):
    others = [x for x in sorted(path.glob('*.png')) if 'static' in x.name]
    o = rgba(others[0]); mask_diff[who] = {'file': others[0].name,
                                           'differing_alpha_texels': int(np.count_nonzero((o[:, :, 3] > 0) != (al > 0)))}
gate('own_silhouette_not_recolour', all(v['differing_alpha_texels'] >= 400 for v in mask_diff.values()), mask_diff)
west_im = rgba([x for x in sorted(WEST.glob('*.png')) if 'static' in x.name][0])
mirror_diff = int(np.count_nonzero(np.fliplr(west_im[:, :, 3] > 0) != (al > 0)))
gate('not_mirrored_west', mirror_diff >= 250, mirror_diff)
gate('east_package_attrs', (f / '.gdignore').exists() and (f / '.gitattributes').read_text(encoding='utf8')
     == '* -text -eol\n')
for label, path, digest in (('south', SOUTH_MANIFEST, SOUTH_MANIFEST_SHA),
                            ('west', WEST_MANIFEST, WEST_MANIFEST_SHA),
                            ('north', NORTH_MANIFEST, NORTH_MANIFEST_SHA)):
    mm = json.loads(path.read_text(encoding='utf8'))
    files = {v['file']: sha(path.parent / v['file']) == v['rawsha256'] for v in mm['files'].values()}
    gate(label + '_package_unchanged', sha(path) == digest and all(files.values()), files)
pins = {x.name: sha(x) for x in sorted(f.iterdir()) if x.is_file()}
report = {'passed': all(c['passed'] for c in checks), 'checks': checks, 'sourceHashes': pins,
          'checkerSha256': sha(Path(__file__)), 'hash': 'sha256 of raw bytes, no normalization',
          'scope': 'editable static source only; no GUI reliability, motion, ordinary adoption or art approval'}
(O / f'rpg-2-star-ocean-the-second_heya_east_independent-source-proof_v01_{TAG}.json').write_text(
    json.dumps(report, indent=2) + '\n', encoding='utf8')
print('HEYA_E155_INDEPENDENT', sum(c['passed'] for c in checks), '/', len(checks))
print('FAILURES', [c['id'] for c in checks if not c['passed']])
for c in checks:
    if not c['passed'] or c['id'] in ('own_silhouette_not_recolour', 'anchor_roles_contribute',
                                      'coil_low_at_nape_east', 'scarf_east', 'bag_left_hip_far_east',
                                      'restrained_smile_east', 'profile_east_facing', 'charcoal_dress_visible',
                                      'upper_left_light_east', 'not_mirrored_west', 'mature_face_shading'):
        print(c['id'], c['passed'], json.dumps(c['detail']))
raise SystemExit(0 if report['passed'] else 1)
