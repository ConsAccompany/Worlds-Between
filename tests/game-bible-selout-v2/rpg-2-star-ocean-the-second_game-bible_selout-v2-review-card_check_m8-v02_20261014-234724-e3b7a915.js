// Focused check for the Game Bible selout v2 review card and the files it points at.
// Starts the real v05 panel server on a spare local port (the user's 18727 instance is left alone), then runs the
// served bible.js in a VM with a minimal DOM stub. Also verifies the v2 sprite, the eight separate QA captures and the
// ZIP structure of the editable selout v1 Pixelorama baseline. Also covers the separate selout v4 technical-candidate
// card and its eight same-run captures (v4 + v3 reference). Read-only: no project file is written.
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
// Selout v4 structural technical candidate (separate card; unapproved, no user review).
const v3Png = path.join(pilots, prefix + 'selout-v3-polish-candidate_m8-v03_20261014-234700-3c9a5d27.png');
const v4Png = path.join(pilots, prefix + 'selout-v4-structural-candidate_m8-v04_20261015-001500-e5b81f36.png');
const v4ManifestRel = 'game/assets/characters/pixelorama-pilots/' + prefix + 'selout-v4-structural-manifest_m8-v04_20261015-001500-0c9d3a74.json';
const v4ReportPath = path.join(root, 'outputs', 'rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v4-visual-qa-report_m8-v04_20261015-001305-7973118b.json');
const v4Stem = 'm8-v04_20261015-001305-7973118b';
// Historical experimental walk-frame prototypes (part of the rejected four-phase test loop). They exist as files; none is
// approved. A manifest's walk_frames: 0 means that static candidate has no walk frames, not that the project has none.
const historicalWalkPrototypes = ['01-44edae33', '02-8a297561', '03-ba73f592', '04-70d3f0b5'].map(s =>
  path.join(root, 'game', 'assets', 'characters', 'native-animation', `rpg-2-star-ocean-the-second_protagonist-female_native-walk-south-phase-${s.slice(0, 2)}_m8-prototype_20261014-140955-${s.slice(3)}.png`));
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
  assert.equal(manifest.walk_frames, 0, 'the v2 static candidate itself contains no walk frames');
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

  // 4b. v4 sprite, manifest, report and its eight captures (v4 + same-run v3 reference); still unapproved.
  const v4Manifest = JSON.parse(fs.readFileSync(path.join(root, v4ManifestRel), 'utf8'));
  const v4Report = JSON.parse(fs.readFileSync(v4ReportPath, 'utf8'));
  const v4Bytes = fs.readFileSync(v4Png);
  assert.equal(sha256(v4Bytes), 'da8a1ce11db136f7061206a3d8f5038b7d995016e36af2fc011d0a6f0dbcf4d7');
  assert.equal(sha256(v4Bytes), v4Manifest.output.sha256);
  assert.equal(sha256(fs.readFileSync(v3Png)), v4Manifest.source.sha256);
  assert.deepEqual(pngSize(v4Bytes), [80, 112]);
  assert.equal(v4Manifest.output.measured.unique_opaque_rgb_colours, 27);
  assert.deepEqual([v4Manifest.output.measured.visible_body_width_texels, v4Manifest.output.measured.visible_body_height_texels], [43, 96]);
  assert.equal(v4Manifest.pixel_changes.total, 358);
  assert.equal(sha256(fs.readFileSync(v4ReportPath)), v4Manifest.qa_captures.report_sha256, 'manifest records the v4 report hash');
  for (const doc of [v4Manifest, v4Report]) { assert.equal(doc.art_approved, false); assert.equal(doc.human_reviewed, false); }
  assert.equal(v4Manifest.walk_frames, 0, 'the v4 static candidate itself contains no walk frames');
  assert.equal(v4Manifest.runtime_integrated, false);
  for (const file of historicalWalkPrototypes) assert.ok(fs.existsSync(file), 'historical walk prototype still exists: ' + path.basename(file));
  assert.deepEqual(v4Report.acceptance_counters_unchanged, {runtime_exploration_sprites_accepted: '0/52', scene_quality_gates_passed: '0/11'});
  assert.equal(v4Report.captures.length, 8);
  const v4CaptureFiles = [];
  for (const scene of scenes) {
    assert.equal(v4Report.v4_vs_v3_same_scene[scene].changed_window_pixels, 358, scene + ' changed window pixels');
    for (const variant of ['selout-v4', 'selout-v3-reference']) {
      const capture = v4Report.captures.find(c => c.scene === scene && c.variant === variant);
      assert.ok(capture, `${scene}/${variant} capture recorded`);
      const name = `rpg-2-star-ocean-the-second_${scene}_protagonist-female-south-idle-${variant}-h48_${v4Stem}.png`;
      assert.equal(path.basename(capture.capture), name);
      const bytes = fs.readFileSync(path.join(root, 'outputs', name));
      assert.equal(sha256(bytes), capture.capture_sha256, name);
      assert.deepEqual(pngSize(bytes), [1280, 720]);
      assert.equal(capture.pilot_source_sha256, variant === 'selout-v4' ? v4Manifest.output.sha256 : v4Manifest.source.sha256);
      assert.equal(capture.pilot_texel_fidelity.exact_rgb_matches, capture.pilot_texel_fidelity.opaque_texels);
      if (variant === 'selout-v4') assert.equal(capture.pilot_texel_fidelity.opaque_texels, 2443);
      assert.deepEqual([capture.pilot_window_diff_bounds_measured.w, capture.pilot_window_diff_bounds_measured.h], [43, 96]);
      v4CaptureFiles.push({name, sha: capture.capture_sha256});
    }
  }
  assert.equal(new Set(v4CaptureFiles.map(c => c.sha)).size, 8, 'eight distinct v4-run capture files');
  const femaleVariant = checklist.variants.find(v => v.visual_id === 'protagonist-female');
  assert.ok(femaleVariant.gates.exploration_animation.unregistered_manifests.includes(v4ManifestRel), 'checklist lists the v4 manifest');
  pass('v4 sprite 80x112 27 colours 358 changed texels; report hash in manifest; 8 separate 1280x720 captures (v4 + same-run v3) match, 2443/2443 texels, 358 changed window pixels per scene; art_approved/human_reviewed false; v4 candidate adds no walk frames; historical walk prototypes still present (none approved)');

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
    assert.ok(!card.includes('尚未开始任何行走帧') && card.includes('实验性行走帧原型'), 'historical walk prototypes acknowledged, not denied');
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

    // v4: its own card after the v2 card, inline v4 captures only, v3 comparisons as links.
    const v4Start = html.indexOf('<section class="card" id="idle-selout-v4">');
    const v4Card = html.slice(v4Start, html.indexOf('</section>', v4Start) + '</section>'.length);
    assert.ok(v4Start > start && v4Card.length > 100, 'v4 card follows the v2 card');
    assert.equal((html.match(/id="idle-selout-v4"/g) || []).length, 1, 'exactly one v4 card');
    assert.ok(!card.includes('selout-v4'), 'v2 card does not mention v4 captures');
    assert.ok(v4Card.includes('状态：未批准') && v4Card.includes('未经用户审阅') && v4Card.includes('human_reviewed: false'), 'unapproved, unreviewed status');
    assert.ok(!/已批准|已验收|approved/i.test(v4Card.replace(/未批准|未获美术批准|没有任何行走动画获批准|未经用户审阅/g, '')), 'no approval wording');
    assert.ok(v4Card.includes('0/52') && v4Card.includes('0/11') && v4Card.includes('行走帧仍暂停'));
    assert.ok(v4Card.includes('358') && v4Card.includes('2443/2443') && v4Card.includes('已知局限'));
    assert.ok(!v4Card.includes('未看过渲染结果') && v4Card.includes('第二张 8 倍预览'), 'records the two 8x preview rounds');
    assert.ok(v4Card.includes('实验性行走帧原型') && v4Card.includes('动画验收为 0'), 'walk prototypes exist; animation acceptance 0');
    const v4Imgs = [...v4Card.matchAll(/<img src="([^"]+)"/g)].map(m => m[1]);
    assert.deepEqual(v4Imgs, ['city', 'outskirts-bright', 'survey-annex-room2-dark'].map(s => `/assets/rpg-2-star-ocean-the-second_${s}_protagonist-female-south-idle-selout-v4-h48_${v4Stem}.png`));
    const v4Hrefs = new Set([...v4Card.matchAll(/href="([^"]+)"/g)].map(m => m[1]));
    for (const c of v4CaptureFiles) {
      const href = '/assets/' + c.name;
      assert.ok(v4Hrefs.has(href), 'v4 card links ' + c.name);
      const response = await fetch(base + href);
      assert.equal(response.status, 200, href);
      assert.equal(sha256(Buffer.from(await response.arrayBuffer())), c.sha, href + ' served bytes');
    }
    assert.equal(v4Hrefs.size, 8, 'v4 card links exactly its eight captures');
    pass('Production view: one separate v4 card after the v2 card, 3 inline v4 captures (city/bright/dark), 4 v3 references + dark prototype room as links, all 8 served byte-identical, unapproved/unreviewed status, 0/52 and 0/11 unchanged');
  } finally {
    child.kill();
  }
  console.log(`RESULT PASS (${results.length} checks)`);
})().catch(error => { console.error('RESULT FAIL'); console.error(error); process.exitCode = 1; });
