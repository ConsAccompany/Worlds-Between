// Focused portability check for the content-hash locks in the character sprite readiness checklist.
// Clean checkouts used to fail because text locks had been taken over CRLF working copies while the Git blobs are LF.
// This proves every text lock (sha256-text-lf-v1) gives the same value for the LF and the CRLF rendering of each file
// and equals the raw SHA-256 of the committed LF blob, that binary PNG locks stay exact-byte and unchanged, and that
// the Node helper and the Python readiness builder implement the same algorithm.
// Read-only: writes only to a temporary directory. Needs Python 3.10+ for the parity step: set PYTHON to the
// interpreter if neither `python3` nor `python` on PATH is one.
// Run from the repository root: node tests/content-hash-portability/<this file>
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');

const root = path.resolve(__dirname, '..', '..');
const {BYTES_HASH, TEXT_HASH, sha256, textLfBytes, textSha256, contentHash} =
  require(path.join(root, 'tools', 'rpg-2-star-ocean-the-second_content-hash_text-lf-v1_m8-v01_20261014-224905-022124e7.js'));
const builder = path.join(root, 'tools', 'rpg-2-star-ocean-the-second_character-sprite-readiness_build-and-check_m8-v01_20261014-184413-c8e6c511.py');
const checklistPath = path.join(root, 'game', 'data', 'character-visuals', 'rpg-2-star-ocean-the-second_character-sprite-readiness-checklist_m8-v01_20261014-184413-53da3710.json');

let passed = 0;
const pass = message => { passed++; console.log('PASS ' + message); };
const toLf = buffer => textLfBytes(buffer);
const toCrlf = buffer => Buffer.from(toLf(buffer).toString('utf8').replace(/\n/g, '\r\n'), 'utf8');

// 1. The algorithm itself.
const lf = Buffer.from('{\n  "a": "é",\n  "b": 1\n}\n', 'utf8');
const crlf = Buffer.from('{\r\n  "a": "é",\r\n  "b": 1\r\n}\r\n', 'utf8');
assert.notEqual(sha256(lf), sha256(crlf), 'raw hashes differ by line ending');
assert.equal(textSha256(lf), textSha256(crlf));
assert.equal(textSha256(lf), sha256(lf), 'an LF file hashes the same under both algorithms');
assert.equal(textSha256(Buffer.from('a\r\nb\nc', 'utf8')), sha256(Buffer.from('a\nb\nc', 'utf8')), 'mixed endings');
assert.notEqual(textSha256(Buffer.from('a\rb', 'utf8')), textSha256(Buffer.from('a\nb', 'utf8')), 'a lone CR is not rewritten');
assert.equal(textSha256(Buffer.from('a\r\r\nb', 'utf8')), sha256(Buffer.from('a\r\nb', 'utf8')), 'only the CRLF pair is collapsed');
assert.equal(textSha256(Buffer.alloc(0)), sha256(Buffer.alloc(0)));
assert.throws(() => textSha256(Buffer.from([0x61, 0x00, 0x62])), /NUL/);
assert.throws(() => textSha256(Buffer.from([0x61, 0xff, 0x62])), TypeError, 'invalid UTF-8 is refused');
assert.throws(() => contentHash(lf, 'sha256'), /unknown hash algorithm/);
pass(`${TEXT_HASH}: LF == CRLF == mixed, lone CR kept, NUL / invalid UTF-8 refused, unknown algorithm refused`);

// 2. Collect every lock the checklist records.
const checklist = JSON.parse(fs.readFileSync(checklistPath, 'utf8'));
const locks = [];
for (const key of ['registry', 'inventory']) locks.push({role: 'sources.' + key, ...checklist.sources[key]});
const baselines = checklist.variants.filter(v => v.gates.exploration_animation.static_idle_baseline);
assert.deepEqual(baselines.map(v => v.visual_id), ['protagonist-female']);
const baseline = baselines[0].gates.exploration_animation.static_idle_baseline;
for (const [role, f] of Object.entries(baseline.files)) if (f.sha256) locks.push({role: 'baseline.' + role, ...f});
assert.deepEqual(Object.keys(checklist.policy.content_hashes).sort(), [BYTES_HASH, TEXT_HASH].sort());
const textLocks = locks.filter(l => l.sha256_algorithm === TEXT_HASH);
const byteLocks = locks.filter(l => l.sha256_algorithm === BYTES_HASH);
assert.equal(textLocks.length + byteLocks.length, locks.length, 'every lock names a known algorithm');
for (const l of locks) assert.equal(l.sha256_algorithm, l.path.endsWith('.png') ? BYTES_HASH : TEXT_HASH, l.role + ': PNG = bytes, text = text-lf');
assert.deepEqual(textLocks.map(l => l.role), ['sources.registry', 'sources.inventory', 'baseline.manifest', 'baseline.qa_report']);

// 3. Text locks are line-ending independent and match the file as checked out.
for (const l of textLocks) {
  const bytes = fs.readFileSync(path.join(root, l.path));
  const asLf = toLf(bytes), asCrlf = toCrlf(bytes);
  assert.ok(asLf.includes(0x0a), l.role + ' has line breaks');
  assert.equal(textSha256(bytes), l.sha256, l.role + ' as checked out');
  assert.equal(textSha256(asLf), l.sha256, l.role + ' LF rendering');
  assert.equal(textSha256(asCrlf), l.sha256, l.role + ' CRLF rendering');
  assert.equal(sha256(asLf), l.sha256, l.role + ' lock = raw hash of the LF rendering');
  assert.notEqual(sha256(asCrlf), l.sha256, l.role + ' a raw-byte lock would have depended on the checkout');
}
pass(`${textLocks.length} text locks match the checkout and both the LF and CRLF renderings (${textLocks.map(l => l.role).join(', ')})`);

// 4. The text locks equal the committed LF blobs.
const git = args => spawnSync('git', ['-C', root, ...args], {encoding: 'buffer', maxBuffer: 64 << 20});
const inside = git(['rev-parse', '--is-inside-work-tree']);
if (inside.status !== 0 || inside.stdout.toString().trim() !== 'true') {
  console.log('SKIP git blob cross-check: not a git checkout');
} else {
  for (const l of textLocks) {
    const blob = git(['cat-file', 'blob', 'HEAD:' + l.path]);
    assert.equal(blob.status, 0, `${l.path} is committed at HEAD: ${blob.stderr}`);
    assert.ok(!blob.stdout.includes(Buffer.from('\r\n')), l.role + ' blob is stored with LF');
    assert.equal(sha256(blob.stdout), l.sha256, l.role + ' lock = SHA-256 of the HEAD blob');
  }
  pass(`text locks equal the SHA-256 of the LF blobs at HEAD (${git(['rev-parse', '--short', 'HEAD']).stdout.toString().trim()})`);
}

// 5. Binary locks: exact bytes, unchanged approval values, never treated as text.
const approved = {
  'baseline.png': 'ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd',
  'baseline.capture_city_bright': '0b8e67ac75539fdac46e7843687d660d0dfa98697f7bf229b0079437351d9e65',
  'baseline.capture_outskirts_bright': 'b4cedaddc7832850e2904e798e92c36ca479966e8c59453f1bb05e11d881c12f',
  'baseline.capture_annex_dark': 'da444d274b21a529859b306af612d46859087ef2785bc0d66f9e19f9682d5b0c',
};
assert.deepEqual(byteLocks.map(l => l.role).sort(), Object.keys(approved).sort());
for (const l of byteLocks) {
  const bytes = fs.readFileSync(path.join(root, l.path));
  assert.equal(l.sha256, approved[l.role], l.role + ' recorded value is the approved one');
  assert.equal(sha256(bytes), l.sha256, l.role + ' exact bytes');
  assert.ok(bytes.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])), l.role + ' PNG signature intact');
  assert.throws(() => textSha256(bytes), /NUL|decode|invalid|encoded/i, l.role + ' is refused as text');
}
pass(`${byteLocks.length} PNG locks stay ${BYTES_HASH} with the approved v8 values; the text algorithm refuses them`);

// 6. Python builder parity on the same inputs.
const pythonCandidates = [process.env.PYTHON, 'python3', 'python'].filter(Boolean);
const python = pythonCandidates.find(cmd => {
  const r = spawnSync(cmd, ['-c', 'import sys; print(sys.version_info >= (3, 10))'], {encoding: 'utf8'});
  return r.status === 0 && r.stdout.trim() === 'True';
});
assert.ok(python, 'Python 3.10+ not found (tried ' + pythonCandidates.join(', ') + '); set PYTHON to run the parity step');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'content-hash-portability-'));
try {
  const samples = {lf, crlf, mixed: Buffer.from('a\r\nb\nc', 'utf8'), lone_cr: Buffer.from('a\rb', 'utf8'),
    nul: Buffer.from([0x61, 0x00]), bad_utf8: Buffer.from([0xff]), png: fs.readFileSync(path.join(root, baseline.files.png.path))};
  for (const l of textLocks) {
    const bytes = fs.readFileSync(path.join(root, l.path));
    samples[l.role + '.lf'] = toLf(bytes);
    samples[l.role + '.crlf'] = toCrlf(bytes);
  }
  const files = {};
  for (const [name, bytes] of Object.entries(samples)) {
    // Prefixed so no sample lands on a reserved Windows device name such as "nul".
    files[name] = path.join(tmp, 'sample-' + name.replace(/[^a-z0-9_.-]/gi, '_') + '.bin');
    fs.writeFileSync(files[name], bytes);
  }
  const script = [
    'import importlib.util, json, sys',
    'from pathlib import Path',
    'spec = importlib.util.spec_from_file_location("readiness", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)',
    'out = {"text": m.TEXT_HASH, "bytes": m.BYTES_HASH, "hashes": {}}',
    'for name, p in json.loads(sys.argv[2]).items():',
    '    try: out["hashes"][name] = m.text_sha256(Path(p))',
    '    except ValueError as e: out["hashes"][name] = "refused"',
    'print(json.dumps(out))',
  ].join('\n');
  const r = spawnSync(python, ['-c', script, builder, JSON.stringify(files)], {encoding: 'utf8'});
  assert.equal(r.status, 0, 'python parity run failed: ' + r.stderr);
  const py = JSON.parse(r.stdout);
  assert.deepEqual([py.text, py.bytes], [TEXT_HASH, BYTES_HASH]);
  for (const [name, bytes] of Object.entries(samples)) {
    let js;
    try { js = textSha256(bytes); } catch { js = 'refused'; }
    assert.equal(py.hashes[name], js, name + ': Python and Node agree');
  }
  for (const l of textLocks) for (const form of ['lf', 'crlf']) assert.equal(py.hashes[`${l.role}.${form}`], l.sha256);
  assert.deepEqual([py.hashes.nul, py.hashes.bad_utf8, py.hashes.png], ['refused', 'refused', 'refused']);
  pass(`Python builder (${python}) and Node helper agree on ${Object.keys(samples).length} inputs, including every lock in LF and CRLF form and the refused binary/NUL/invalid-UTF-8 inputs`);
} finally {
  fs.rmSync(tmp, {recursive: true, force: true});
}

console.log(`RESULT PASS (${passed} checks)`);
