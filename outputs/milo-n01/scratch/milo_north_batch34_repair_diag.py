"""Scratch (read-only QA aid, batch34): verify the pre-repair backup and original failing proof, and measure the
pixel change between the backed-up original north PNG and the current repaired PNG. Stdlib only. Writes nothing."""
import hashlib, json, pathlib, struct, sys, zlib

R = pathlib.Path(__file__).resolve().parents[3]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def rgba(path):
    """Minimal PNG decoder: 8-bit RGBA (type 6) or 8-bit palette (type 3, with tRNS), non-interlaced."""
    b = path.read_bytes()
    assert b[:8] == b'\x89PNG\r\n\x1a\n'
    i, idat, plte, trns = 8, b'', b'', b''
    while i < len(b):
        n, t = struct.unpack('>I4s', b[i:i + 8]); d = b[i + 8:i + 8 + n]; i += 12 + n
        if t == b'IHDR':
            w, h, bd, ct, _, _, il = struct.unpack('>IIBBBBB', d)
            assert bd == 8 and ct in (3, 6) and il == 0, (bd, ct, il)
        elif t == b'PLTE': plte = d
        elif t == b'tRNS': trns = d
        elif t == b'IDAT': idat += d
    bpp = 4 if ct == 6 else 1
    raw, stride, prev, rows, o = zlib.decompress(idat), w * bpp, bytearray(w * bpp), [], 0
    for _ in range(h):
        f, line = raw[o], bytearray(raw[o + 1:o + 1 + stride]); o += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0; up = prev[x]; c = prev[x - bpp] if x >= bpp else 0
            if f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + up) & 255
            elif f == 3: line[x] = (line[x] + (a + up) // 2) & 255
            elif f == 4:
                p = a + up - c; pa, pb, pc = abs(p - a), abs(p - up), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else up if pb <= pc else c)) & 255
        rows.append(line); prev = line
    if ct == 6:
        return w, h, [[tuple(r[x * 4:x * 4 + 4]) for x in range(w)] for r in rows]
    pal = lambda k: tuple(plte[k * 3:k * 3 + 3]) + ((trns[k] if k < len(trns) else 255),)
    return w, h, [[pal(r[x]) for x in range(w)] for r in rows]


bk = R / 'outputs/milo-n01/backup-pre-hand-repair_v01_20261023-repair1'
m = json.loads((bk / 'backup-manifest.json').read_text())
ok = True
for rel, v in m['files'].items():
    p = bk / rel
    good = sha(p) == v['sha256'] and p.stat().st_size == v['size']
    ok &= good
    print('BACKUP', 'OK ' if good else 'BAD', v['action'], v['sha256'], rel)
pr = R / ('outputs/milo-n01/logs/source1/independent/'
          'rpg-2-star-ocean-the-second_milo_north-independent-source-proof_v01_20261023-225642-1b612f93.json')
print('ORIGINAL_PROOF', pr.relative_to(R), sha(pr))
j = json.loads(pr.read_text())
print('ORIGINAL_PROOF_FAILURE_KEYS', {k: j[k] for k in j if 'fail' in k.lower()})
n = 'rpg-2-star-ocean-the-second_milo_north-static_unapproved-v01_20261023-225642-5968ba0c.png'
w, h, o = rgba(bk / 'game/assets/characters/milo-native-v01/north' / n)
w2, h2, c = rgba(R / 'game/assets/characters/milo-native-v01/north' / n)
assert (w, h) == (w2, h2) == (80, 112)
diff = [(y, x) for y in range(h) for x in range(w) if o[y][x] != c[y][x]]
print('DIFF_TEXELS', len(diff), 'rows', min(y for y, _ in diff), max(y for y, _ in diff),
      'x', min(x for _, x in diff), max(x for _, x in diff))
by_row = {}
for y, x in diff:
    by_row.setdefault(y, []).append(x)
print('DIFF_BY_ROW', by_row)
print('DIFF_SCREEN_LEFT(x<40)', sum(x < 40 for _, x in diff), 'DIFF_SCREEN_RIGHT(x>=40)', sum(x >= 40 for _, x in diff))
for img, lab in ((o, 'original'), (c, 'repaired')):
    op = lambda y, x: img[y][x][3] > 0
    print('CASE_REGION', lab, 'rows63..76 opaque x<=22:', sum(op(y, x) for y in range(63, 77) for x in range(23)),
          'x>=58:', sum(op(y, x) for y in range(63, 77) for x in range(58, w)))
    print('   screen-left opaque x in rows 63..69:', sorted({x for y in range(63, 70) for x in range(40) if op(y, x)}))
sys.exit(0 if ok else 1)
