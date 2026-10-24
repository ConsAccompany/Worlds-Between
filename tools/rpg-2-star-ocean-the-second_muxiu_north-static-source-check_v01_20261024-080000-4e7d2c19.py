"""Independent Muxiu north static source check (content.char.muxiu.static-north). No runtime/art/motion approval.

Does not import any Muxiu author. Reads the game tree only; writes only to --out (must be new). Package checks
(manifest hashes, 80x112, binary alpha, pivot/body rows, colours declared, ORA merged image == PNG, ORA guides
hidden, PXO labels north, south/west unchanged vs pinned manifests), then image-level BACK-VIEW predicates that are
also run on negative controls (south image, mirrored south, squashed south, west profile, mirrored west, mirrored
north). Back-view predicates do NOT demand front details (no whistle, no eyes):
  no_face_features   no eye-white/iris/mouth colours anywhere
  head_is_hair       >= 80% of opaque head texels (rows 8..28) are hair colours (back of the head)
  symmetric_frame    body silhouette not a profile: left/right opaque count ratio of rows 30..103 in 0.8..1.25
  braid_screen_right hair-coloured texels on the shoulders (rows 31..41) right of x=44 >= 20 and > 3x left of x=36
  bracelet_screen_left tan+moss rope texels at the wrist (rows 66..73) only at x < 30
  moss_dominant      moss cloak colours are the most frequent opaque colour group
  full_height        opaque rows span 8..103 (rejects squash)
Exit 0 all checks pass, 1 any failure.
  python -X utf8 -I <this> --root . --out outputs/muxiu-n01/independent-<new>
"""
from pathlib import Path
import argparse, hashlib, io, json, zipfile
from PIL import Image
import numpy as np

ap = argparse.ArgumentParser(); ap.add_argument('--root', default='.'); ap.add_argument('--out', required=True); a = ap.parse_args()
R = Path(a.root).resolve(); O = Path(a.out).resolve(); O.mkdir(parents=True, exist_ok=False)
BASE = R / 'game/assets/characters/muxiu-native-v01'
N = BASE / 'north'
PINNED = {'south/rpg-2-star-ocean-the-second_muxiu_south-manifest_unapproved-v01_20261024-071500-dd478113.json':
          '24c751575fe02a4857628dbfb8b379cd1d42344167062ae8ddbb033024e114de',
          'west/rpg-2-star-ocean-the-second_muxiu_west-manifest_unapproved-v01_20261024-055724-a2f2ac0f.json':
          'c92fb90c2f6a54b778856329f1c60b6db269070244e38c897bee5f7a13dc4772'}
checks = []


def gate(n, v, detail=None): checks.append({'id': n, 'passed': bool(v), 'detail': detail})
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rgba(p): return np.array(Image.open(p).convert('RGBA'))


mf = sorted(N.glob('*manifest*.json')); gate('one_manifest', len(mf) == 1, [x.name for x in mf])
m = json.loads(mf[0].read_text())
pal = json.loads((N / m['files']['palette']['file']).read_text())['colors']
C = lambda *ks: {tuple(int(pal[k][i:i + 2], 16) for i in (0, 2, 4)) for k in ks}
gate('manifest_hashes', all(sha(N / v['file']) == v['rawsha256'] for v in m['files'].values()))
gate('direction_north_unapproved', m['direction'] == 'north' and m['status'] == 'UNAPPROVED')
gate('pivot_rows_scale', m['pivot'] == [40, 104] and m['body_rows'] == [8, 103] and m['display_scale'] == 0.5
     and m['logical_height_px'] == 48, [m['pivot'], m['body_rows'], m['logical_height_px']])
img = rgba(N / m['files']['png']['file'])
gate('canvas_80x112', img.shape[:2] == (112, 80))
al = img[..., 3]; op = al == 255
gate('binary_alpha', set(np.unique(al)) <= {0, 255})
gate('transparent_border', not (op[0].any() or op[-1].any() or op[:, 0].any() or op[:, -1].any()))
used = {tuple(c) for c in img[op][:, :3]}; declared = C(*pal)
gate('colours_declared_24_48', used <= declared and 24 <= len(used) <= 48, len(used))
with zipfile.ZipFile(N / m['files']['ora']['file']) as z:
    merged = np.array(Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA'))
    stack = z.read('stack.xml').decode()
gate('ora_merged_equals_png', merged.shape == img.shape and (merged == img).all())
gate('ora_guides_hidden', 'name="guides"' in stack and 'visibility="hidden"' in stack)
with zipfile.ZipFile(N / m['files']['pxo']['file']) as z:
    dj = z.read('data.json')
gate('pxo_labels_north', b'muxiu-north' in dj and b'muxiu-south' not in dj)
for rel, want in PINNED.items():
    p = BASE / rel; sm = json.loads(p.read_text())
    gate(f'sibling_unchanged:{rel.split("/")[0]}', sha(p) == want and
         all(sha(p.parent / v['file']) == v['rawsha256'] for v in sm['files'].values()))
gate('placeholder_not_used', 'native-animation' not in json.dumps(m['files']))

HAIR, FACE, MOSS, ROPE = C('h1', 'h2', 'h3', 'h4'), C('e1', 'e2', 'm1'), C('c1', 'c2', 'c3'), C('q1', 'q2', 'c2')


def preds(im):
    o = im[..., 3] == 255; rgb = im[..., :3]
    inset = lambda s, ys, xs: sum(1 for y in ys for x in xs if o[y, x] and tuple(rgb[y, x]) in s)
    head = [(y, x) for y in range(8, 29) for x in range(80) if o[y, x]]
    hair_head = sum(1 for y, x in head if tuple(rgb[y, x]) in HAIR)
    body = o[30:104]; lft, rgt = body[:, :40].sum(), body[:, 40:].sum()
    br_r, br_l = inset(HAIR, range(31, 42), range(45, 80)), inset(HAIR, range(31, 42), range(0, 36))
    rope_l, rope_r = inset(ROPE - C('c2') | C('q1'), range(66, 74), range(0, 30)), inset(C('q1'), range(66, 74), range(50, 80))
    groups = {g: sum(1 for c in im[o][:, :3] if tuple(c) in s) for g, s in
              {'moss': MOSS, 'hair': HAIR, 'trousers': C('t1', 't2', 't3'), 'skin': C('s1', 's2', 's3')}.items()}
    ys = np.nonzero(o.any(1))[0]
    return {'no_face_features': not any(tuple(c) in FACE for c in im[o][:, :3]),
            'head_is_hair': bool(head) and hair_head / len(head) >= 0.8,
            'symmetric_frame': rgt > 0 and 0.8 <= lft / rgt <= 1.25,
            'braid_screen_right': br_r >= 20 and br_r > 3 * br_l,
            'bracelet_screen_left': rope_l >= 4 and rope_r == 0,
            'moss_dominant': max(groups, key=groups.get) == 'moss',
            'full_height': len(ys) > 0 and ys.min() == 8 and ys.max() == 103}


pn = preds(img)
for k, v in pn.items():
    gate(f'north:{k}', v)
south = rgba(next((BASE / 'south').glob('*static*.png'))); west = rgba(next((BASE / 'west').glob('*static*.png')))
sq = np.zeros_like(south); s2 = np.array(Image.fromarray(south).resize((80, 56), Image.NEAREST)); sq[56:112] = s2
controls = {'south': south, 'mirrored_south': south[:, ::-1], 'squashed_south': sq, 'west': west,
            'mirrored_west': west[:, ::-1], 'mirrored_north': img[:, ::-1]}
neg = {}
for name, im in controls.items():
    p = preds(im); neg[name] = p
    gate(f'negative_rejected:{name}', not all(p.values()), [k for k, v in p.items() if not v])
gate('north_differs_from_south_pixels', (img != south).any(axis=2).sum() >= 400, int((img != south).any(axis=2).sum()))
ok = all(c['passed'] for c in checks)
res = {'checks': checks, 'north_predicates': pn, 'negative_predicates': neg,
       'files': {k: v for k, v in m['files'].items()}, 'result': 'PASS' if ok else 'FAIL',
       'passed': sum(c['passed'] for c in checks), 'total': len(checks)}
(O / 'muxiu-north-independent-check.json').write_text(json.dumps(res, indent=1, default=str) + '\n')
for c in checks:
    print(('PASS ' if c['passed'] else 'FAIL ') + c['id'], '' if c['detail'] is None else c['detail'])
print(f"MUXIU_NORTH_INDEPENDENT_{res['result']} {res['passed']}/{res['total']}")
raise SystemExit(0 if ok else 1)
