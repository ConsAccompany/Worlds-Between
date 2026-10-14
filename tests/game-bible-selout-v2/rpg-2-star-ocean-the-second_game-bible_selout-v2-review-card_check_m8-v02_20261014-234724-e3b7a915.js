// Focused check for the Game Bible selout v2 review card and the files it points at.
// Starts the real v05 panel server on a spare local port (the user's 18727 instance is left alone), then runs the
// served bible.js in a VM with a minimal DOM stub. Also verifies the v2 sprite, the eight separate QA captures and the
// ZIP structure of the editable selout v1 Pixelorama baseline. Read-only: no project file is written.
// Run from the repository root: node tests/game-bible-selout-v2/<this file>
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const net = require('node:net');
const path = require('node:path');
const vm = require('node:vm');
const zlib = require('node:zlib');
const {spawn} = require('node:child_process');

const root = path.resolve(__dirname, '..', '..');
const server = path.join(root, 'tools', 'rpg-2-star-ocean-the-second_game-bible_server_v05_20261013-222437-3d5b8a9f.js');
const pilots = path.join(root, 'game', 'assets', 'characters', 'pixelorama-pilots');
const prefix = 'rpg-2-star-ocean-the-second_protagonist-female_south-idle-';
const v1Png = path.join(pilots, prefix + 'refine-selout-candidate_m8-v01_20261014-231100-4d141ad5.png');
const v2Png = path.join(pilots, prefix + 'selout-v2-polish-candidate_m8-v02_20261014-233300-d2eeefa2.png');
const v2Manifest = path.join(pilots, prefix + 'selout-v2-polish-manifest_m8-v02_20261014-233300-d4a8a850.json');
const v1Pxo = path.join(pilots, prefix + 'selout-pixelorama-baseline_m8-v01_20261014-233500-5e93c40a.pxo');
const reportPath = path.join(root, 'outputs', 'rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v2-visual-qa-report_m8-v02_20261014-234215-2a1b6b58.json');
const inventoryPath = path.join(root, 'outputs', 'rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json');
const progressPath = path.join(root, 'outputs', 'rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json');
const checklistPath = path.join(root, 'game', 'data', 'character-visuals', 'rpg-2-star-ocean-the-second_character-sprite-readiness-checklist_m8-v01_20261014-184413-53da3710.json');
const sha256 = data => crypto.createHash('sha256').update(data).digest('hex');
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const results = [];
const pass = label => { results.push(label); console.log('PASS ' + label); };

function freePort() {
  return new Promise((resolve, reject) => {
    const probe = net.createServer().once('error', reject);
    probe.listen(0, '127.0.0.1', () => { const {port} = probe.address(); probe.close(() => resolve(port)); });
  });
}
async function waitFor(check, label, timeout = 8000) {
  const end = Date.now() + timeout;
  while (Date.now() < end) { if (await check()) return; await sleep(50); }
  throw new Error('Timed out waiting for ' + label);
}
const pngSize = bytes => {
  assert.equal(bytes.subarray(0, 8).toString('hex'), '89504e470d0a1a0a', 'PNG signature');
  return [bytes.readUInt32BE(16), bytes.readUInt32BE(20)];
};

// Minimal ZIP reader: end-of-central-directory, central directory, then each local header. Stored and deflate only.
function readZip(bytes) {
  let eocd = -1;
  for (let i = bytes.length - 22; i >= Math.max(0, bytes.length - 65557); i--) if (bytes.readUInt32LE(i) === 0x06054b50) { eocd = i; break; }
  assert.ok(eocd >= 0, 'ZIP end-of-central-directory record');
  const count = bytes.readUInt16LE(eocd + 10), cdOffset = bytes.readUInt32LE(eocd + 16);
  const entries = [];
  for (let i = 0, p = cdOffset; i < count; i++) {
    assert.equal(bytes.readUInt32LE(p), 0x02014b50, 'central directory signature');
    const method = bytes.readUInt16LE(p + 10), crc = bytes.readUInt32LE(p + 16), compressed = bytes.readUInt32LE(p + 20), size = bytes.readUInt32LE(p + 24);
    const nameLength = bytes.readUInt16LE(p + 28), extra = bytes.readUInt16LE(p + 30), comment = bytes.readUInt16LE(p + 32), local = bytes.readUInt32LE(p + 42);
    const name = bytes.subarray(p + 46, p + 46 + nameLength).toString('utf8');
    assert.equal(bytes.readUInt32LE(local), 0x04034b50, 'local header signature for ' + name);
    const start = local + 30 + bytes.readUInt16LE(local + 26) + bytes.readUInt16LE(local + 28);
    const raw = bytes.subarray(start, start + compressed);
    assert.ok(method === 0 || method === 8, `${name}: compression method ${method}`);
    const data = method === 0 ? Buffer.from(raw) : zlib.inflateRawSync(raw);
    assert.equal(data.length, size, name + ' size');
    assert.equal(zlib.crc32(data) >>> 0, crc, name + ' CRC-32');
    entries.push({name, data});
    p += 46 + nameLength + extra + comment;
  }
  return entries;
}

async function renderProduction(base) {
  const element = () => ({innerHTML: '', textContent: '', value: '', dataset: {}, addEventListener() {}, setAttribute() {}, querySelector: () => element(), querySelectorAll: () => []});
  const content = {...element(), querySelector: () => element()};
  const elements = {content, search: element(), edition: element(), pitch: element(), 'footer-status': element()};
  const nav = ['home', 'world', 'rules', 'characters', 'production', 'assets'].map(view => {
    const button = {...element(), dataset: {view}, handlers: {}};
    button.addEventListener = (type, handler) => { button.handlers[type] = handler; };
    return button;
  });
  const context = vm.createContext({
    document: {getElementById: id => elements[id], querySelectorAll: () => nav, addEventListener() {}, hidden: true, createElement: () => element()},
    fetch: (url, options) => fetch(base + url, options), setInterval() {}, localStorage: {getItem: () => '', setItem() {}}, console,
  });
  vm.runInContext(await (await fetch(base + '/bible.js')).text(), context, {filename: 'bible.js'});
  await waitFor(() => elements.edition.textContent !== '', 'initial bible load');
  nav.find(button => button.dataset.view === 'production').handlers.click();
  await waitFor(() => content.innerHTML.includes('id="idle-selout-v2"'), 'selout v2 card');
  return content.innerHTML;
}

(async () => {
  // 1. v2 sprite, manifest and QA report agree; nothing is approved.
  const manifest = JSON.parse(fs.readFileSync(v2Manifest, 'utf8'));
  const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
  const v2Bytes = fs.readFileSync(v2Png);
  assert.equal(sha256(v2Bytes), manifest.output.sha256);
  assert.equal(sha256(fs.readFileSync(v1Png)), manifest.source.sha256);
  assert.deepEqual(pngSize(v2Bytes), [80, 112]);
  assert.equal(manifest.art_approved, false);
  assert.equal(manifest.runtime_integrated, false);
  assert.equal(manifest.walk_frames, 0);
  assert.equal(report.art_approved, false);
  assert.equal(report.human_reviewed, false);
  assert.deepEqual(report.acceptance_counters_unchanged, {runtime_exploration_sprites_accepted: '0/52', scene_quality_gates_passed: '0/11'});
  pass(`v2 sprite 80x112 sha256 ${manifest.output.sha256.slice(0, 16)}… matches manifest; v1 source unchanged; art_approved/human_reviewed false`);

  // 2. Eight separate captures: four scenes x {v2, v1 reference}, each file present with the recorded hash.
  const scenes = ['city', 'outskirts-bright', 'survey-annex-room2-dark', 'prototype-room-dark'];
  assert.equal(report.captures.length, 8);
  const captureFiles = [];
  for (const scene of scenes) for (const variant of ['selout-v2', 'selout-v1-reference']) {
    const capture = report.captures.find(c => c.scene === scene && c.variant === variant);
    assert.ok(capture, `${scene}/${variant} capture recorded`);
    const name = `rpg-2-star-ocean-the-second_${scene}_protagonist-female-south-idle-${variant}-h48_m8-v02_20261014-234215-2a1b6b58.png`;
    assert.equal(path.basename(capture.capture), name);
    const bytes = fs.readFileSync(path.join(root, 'outputs', name));
    assert.equal(sha256(bytes), capture.capture_sha256, name);
    assert.deepEqual(pngSize(bytes), [1280, 720]);
    assert.equal(capture.pilot_source_sha256, variant === 'selout-v2' ? manifest.output.sha256 : manifest.source.sha256);
    assert.equal(capture.pilot_texel_fidelity.exact_rgb_matches, capture.pilot_texel_fidelity.opaque_texels);
    assert.deepEqual([capture.pilot_window_diff_bounds_measured.w, capture.pilot_window_diff_bounds_measured.h], [43, 96]);
    captureFiles.push({name, sha: capture.capture_sha256, variant, scene});
  }
  assert.equal(new Set(captureFiles.map(c => c.sha)).size, 8, 'eight distinct capture files');
  pass('8 separate 1280x720 captures (city, bright outskirts, dark annex, dark prototype room; v2 + same-run v1) match report hashes, 43x96 window, exact texels');

  // 3. The .pxo is a valid ZIP Pixelorama project of the selout v1 baseline (not v2).
  const pxoBytes = fs.readFileSync(v1Pxo);
  const entries = readZip(pxoBytes);
  const names = entries.map(e => e.name);
  const dataJson = entries.find(e => e.name === 'data.json');
  assert.ok(dataJson, 'data.json present; entries: ' + names.join(', '));
  const project = JSON.parse(dataJson.data.toString('utf8'));
  assert.deepEqual([project.size_x, project.size_y], [80, 112], 'project canvas 80x112');
  const layers = (project.layers || []).map(l => l.name), frames = (project.frames || []).length;
  assert.ok(layers.length >= 1 && frames >= 1, 'at least one layer and one frame');
  // Each layer's cel is stored as raw RGBA8 bytes; compare composite of the first frame against v1 and v2 opaque texels.
  const images = entries.filter(e => e.name !== 'data.json' && !e.name.endsWith('/'));
  const celSize = 80 * 112 * 4;
  const rawCels = images.filter(e => e.data.length === celSize);
  assert.ok(rawCels.length >= 1, 'at least one raw 80x112 RGBA cel: ' + images.map(e => `${e.name}(${e.data.length})`).join(', '));
  pass(`.pxo is a valid ZIP (${entries.length} entries, CRC-32 verified): data.json pxo_version ${project.pxo_version ?? '?'}, ${project.pixelorama_version ?? 'unknown editor version'}, 80x112, ${frames} frame(s), layers [${layers.join(', ')}]`);

  // Decode both PNGs is beyond this check; instead compare cel alpha coverage to the manifests' opaque texel counts.
  const opaque = cel => { let n = 0; for (let i = 3; i < cel.length; i += 4) if (cel[i]) n++; return n; };
  const coverage = rawCels.map(e => opaque(e.data));
  const v1Opaque = report.captures.find(c => c.variant === 'selout-v1-reference').pilot_texel_fidelity.opaque_texels;
  const v2Opaque = manifest.output.measured.opaque_texels;
  assert.ok(coverage.includes(v1Opaque), `a cel has v1's ${v1Opaque} opaque texels (cels: ${coverage.join(', ')})`);
  assert.ok(!coverage.includes(v2Opaque), `no cel has v2's ${v2Opaque} opaque texels`);
  pass(`.pxo cel coverage ${coverage.join('/')} opaque texels = selout v1 (${v1Opaque}), not v2 (${v2Opaque}); sha256 ${sha256(pxoBytes).slice(0, 16)}…`);

  // 4. State files: counters unchanged, inventory links exist, readiness checklist hash matches the inventory.
  const inventory = JSON.parse(fs.readFileSync(inventoryPath, 'utf8'));
  const items = inventory.categories.flatMap(c => c.subcategories.flatMap(s => s.items));
  const tally = p => { const list = items.filter(i => i.id.startsWith(p)); return [list.filter(i => i.checked).length, list.length]; };
  assert.deepEqual(tally('runtime-sprite.'), [0, 52]);
  assert.deepEqual(tally('visual-scene.'), [0, 11]);
  const female = items.find(i => i.seloutV2PolishCandidate);
  assert.ok(female && female.checked === false, 'female runtime sprite stays unchecked');
  for (const key of ['seloutV2PolishCandidate', 'seloutV2PolishManifest', 'seloutV2VisualQaReport', 'seloutV1PixeloramaBaselinePxo']) assert.ok(fs.existsSync(path.join(root, female[key])), key);
  assert.match(female.seloutV2Status, /NOT approved/);
  assert.match(female.seloutV2Status, /editable selout v1 baseline, not v2/);
  const checklist = JSON.parse(fs.readFileSync(checklistPath, 'utf8'));
  assert.equal(checklist.sources.inventory.sha256, sha256(fs.readFileSync(inventoryPath)), 'readiness checklist records the current inventory hash');
  assert.equal(checklist.variants.length, 52);
  assert.equal(checklist.scope.character_identities, 51);
  assert.equal(checklist.summary.art_accepted, 0);
  const progress = JSON.parse(fs.readFileSync(progressPath, 'utf8'));
  const m8 = progress.steps.find(s => s.id === 'M8');
  assert.equal(m8.status, 'in_progress');
  assert.match(m8.summary, /NOT approved/);
  assert.match(m8.summary, /48-logical-pixel display scale/);
  pass('inventory 0/52 sprites, 0/11 scenes; v2 + v1 .pxo fields resolve; checklist inventory hash current (52 variants, 51 identities, 0 accepted); M8 in progress');

  // 5. Served Production view: separate v2 card with individual captures and clear unapproved status.
  const port = await freePort();
  const base = `http://127.0.0.1:${port}`;
  const child = spawn(process.execPath, [server], {cwd: root, env: {...process.env, WORLDS_BETWEEN_BIBLE_PORT: String(port)}, stdio: 'ignore'});
  try {
    await waitFor(async () => { try { return (await fetch(base + '/health')).ok; } catch (_) { return false; } }, 'server health');
    const html = await renderProduction(base);
    const start = html.indexOf('<section class="card" id="idle-selout-v2">');
    const card = html.slice(start, html.indexOf('</section>', start) + '</section>'.length);
    assert.ok(start > 0 && card.length > 100);
    assert.ok(html.indexOf('id="idle-refine-selout"') < start, 'v2 card follows the v1 candidate cards');
    assert.equal((html.match(/id="idle-selout-v2"/g) || []).length, 1, 'exactly one v2 card');
    assert.ok(card.includes('仍未批准') && card.includes('状态：未批准'), 'unapproved badge and status line');
    assert.ok(!/已批准|已验收|approved/i.test(card.replace(/未批准/g, '')), 'no approval wording');
    assert.ok(card.includes('0/52') && card.includes('0/11') && card.includes('行走帧仍暂停'));
    assert.ok(card.includes('selout-pixelorama-baseline_m8-v01_20261014-233500-5e93c40a.pxo') && card.includes('内容为 v1，不是 v2'));
    const imgs = [...card.matchAll(/<img src="([^"]+)"/g)].map(m => m[1]);
    assert.deepEqual(imgs, ['city', 'outskirts-bright', 'survey-annex-room2-dark'].map(s => `/assets/rpg-2-star-ocean-the-second_${s}_protagonist-female-south-idle-selout-v2-h48_m8-v02_20261014-234215-2a1b6b58.png`));
    const hrefs = new Set([...card.matchAll(/href="([^"]+)"/g)].map(m => m[1]));
    for (const c of captureFiles) {
      const href = '/assets/' + c.name;
      assert.ok(hrefs.has(href), 'card links ' + c.name);
      const response = await fetch(base + href);
      assert.equal(response.status, 200, href);
      assert.equal(sha256(Buffer.from(await response.arrayBuffer())), c.sha, href + ' served bytes');
    }
    assert.equal(hrefs.size, 8, 'card links exactly the eight captures');
    assert.ok(html.includes(`探索精灵 0 / 52`) && html.includes(`场景画质 0 / 11`), 'page counters unchanged');
    pass('Production view: one separate v2 card after the v1 cards, 3 inline v2 captures (city/bright/dark), all 8 captures linked and served byte-identical, unapproved status, v1 .pxo labelled not v2, 0/52 and 0/11 unchanged');
  } finally {
    child.kill();
  }
  console.log(`RESULT PASS (${results.length} checks)`);
})().catch(error => { console.error('RESULT FAIL'); console.error(error); process.exitCode = 1; });
