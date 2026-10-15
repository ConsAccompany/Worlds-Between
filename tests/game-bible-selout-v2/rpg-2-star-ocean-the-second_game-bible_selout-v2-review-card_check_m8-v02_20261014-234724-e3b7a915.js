// Focused check for the Game Bible selout v2 review card and the files it points at.
// Starts the real v05 panel server on a spare local port (the user's 18727 instance is left alone), then runs the
// served bible.js in a VM with a minimal DOM stub. Also verifies the v2 sprite, the eight separate QA captures and the
// ZIP structure of the editable selout v1 Pixelorama baseline. Also covers the separate selout v4 technical-candidate
// card and its eight same-run captures (v4 + v3 reference), and the separate selout v5 technical-candidate card and its
// eight same-run captures (v5 + v4 reference), and the separate selout v6 technical-candidate card and its eight same-run
// captures (v6 + v5 reference), and the separate selout v8 card (user-approved ONLY as the female south idle static
// still-frame baseline), its six same-run captures (v8 + v7 reference), the decision record, the readiness checklist's
// static_idle_baseline record and the docs/progress.md entry. Read-only: no project file is written.
// Text files (JSON/Markdown) are compared with sha256-text-lf-v1 so the check passes in LF and CRLF checkouts alike;
// PNG and other binary files keep exact-byte SHA-256.
// Run from the repository root: node tests/game-bible-selout-v2/<this file>
const assert = require('node:assert/strict');
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
// Selout v5 lower-body/hair technical candidate (separate card). The user reviewed the v5 city and dark captures and
// replied "更接近了，继续精修" (closer, keep refining): reviewed, NOT approved, further refinement requested.
const v5Png = path.join(pilots, prefix + 'selout-v5-lowerbody-hair-candidate_m8-v05_20261015-004000-8b3e5c07.png');
const v5ManifestRel = 'game/assets/characters/pixelorama-pilots/' + prefix + 'selout-v5-lowerbody-hair-manifest_m8-v05_20261015-004000-f41a7d92.json';
const v5ReportPath = path.join(root, 'outputs', 'rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v5-visual-qa-report_m8-v05_20261015-002513-a59b7bc1.json');
const v5Stem = 'm8-v05_20261015-002513-a59b7bc1';
// Selout v6 value/separation technical candidate (separate card). The user reviewed v6 and replied
// "明亮场景对比度仍不足" (contrast in bright scenes is still not enough): reviewed, NOT approved.
const v6Png = path.join(pilots, prefix + 'selout-v6-value-separation-candidate_m8-v06_20261015-010000-5a7d3f18.png');
const v6ManifestRel = 'game/assets/characters/pixelorama-pilots/' + prefix + 'selout-v6-value-separation-manifest_m8-v06_20261015-010000-c2e9081b.json';
const v6ReportPath = path.join(root, 'outputs', 'rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v6-visual-qa-report_m8-v06_20261015-003321-9bfd5b9e.json');
const v6Stem = 'm8-v06_20261015-003321-9bfd5b9e';
// Selout v7 slate-coat technical candidate (no user verdict, not approved, no separate card) and selout v8 cloth/leather,
// which the user approved ("够了，可作为静止帧基准") ONLY as the female south idle static still-frame baseline at 48 px.
const v7Png = path.join(pilots, prefix + 'selout-v7-slate-coat-candidate_m8-v07_20261015-015010-05615df5.png');
const v7ManifestRel = 'game/assets/characters/pixelorama-pilots/' + prefix + 'selout-v7-slate-coat-manifest_m8-v07_20261015-015010-ed510f85.json';
const v8Png = path.join(pilots, prefix + 'selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png');
const v8ManifestRel = 'game/assets/characters/pixelorama-pilots/' + prefix + 'selout-v8-cloth-leather-manifest_m8-v08_20261015-021600-2d6c5eff.json';
const v8ReportPath = path.join(root, 'outputs', 'rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v8-visual-qa-report_m8-v08_20261015-022215-e2203167.json');
const v8Stem = 'm8-v08_20261015-022215-e2203167';
const v8QaNote = 'docs/qa/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8_visual-qa-note_m8-v08_20261015-021600-c1694107.md';
const v8Decision = 'docs/character-visuals/rpg-2-star-ocean-the-second_protagonist-female_south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md';
// Historical experimental walk-frame prototypes (part of the rejected four-phase test loop). They exist as files; none is
// approved. A manifest's walk_frames: 0 means that static candidate has no walk frames, not that the project has none.
const historicalWalkPrototypes = ['01-44edae33', '02-8a297561', '03-ba73f592', '04-70d3f0b5'].map(s =>
  path.join(root, 'game', 'assets', 'characters', 'native-animation', `rpg-2-star-ocean-the-second_protagonist-female_native-walk-south-phase-${s.slice(0, 2)}_m8-prototype_20261014-140955-${s.slice(3)}.png`));
const {BYTES_HASH, TEXT_HASH, sha256, textSha256, contentHash} = require(path.join(root, 'tools', 'rpg-2-star-ocean-the-second_content-hash_text-lf-v1_m8-v01_20261014-224905-022124e7.js'));
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
  await waitFor(() => content.innerHTML.includes('class="readiness-row"'), 'readiness checklist rows (v8 static baseline check)');
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
  assert.equal(checklist.sources.inventory.sha256_algorithm, TEXT_HASH);
  assert.equal(checklist.sources.inventory.sha256, textSha256(fs.readFileSync(inventoryPath)), 'readiness checklist records the current inventory hash');
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
  assert.equal(textSha256(fs.readFileSync(v4ReportPath)), v4Manifest.qa_captures.report_sha256, 'manifest records the v4 report hash');
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

  // 4c. v5 sprite, manifest, report and its eight captures (v5 + same-run v4 reference). Reviewed by the user (closer,
  // keep refining) and still unapproved. human_reviewed: false in the manifest and report is generation-time provenance,
  // not the current status: the report predates the reply and the manifest value is a fixed field written by the v5 edit
  // script; neither is rewritten after the fact. The v5 edit script was re-run with
  // --qa-report, so the manifest's qa_captures now embeds the report name, its SHA-256 and all eight capture hashes.
  const v5Manifest = JSON.parse(fs.readFileSync(path.join(root, v5ManifestRel), 'utf8'));
  const v5Report = JSON.parse(fs.readFileSync(v5ReportPath, 'utf8'));
  const v5Bytes = fs.readFileSync(v5Png);
  assert.equal(sha256(v5Bytes), '8ddac8acb4261cfc4e42ae9727b7cb5a4ff70791973909ab80cea33920ad7ace');
  assert.equal(sha256(v5Bytes), v5Manifest.output.sha256);
  assert.equal(v5Manifest.source.sha256, v4Manifest.output.sha256, 'v5 source is the unchanged v4');
  assert.deepEqual(pngSize(v5Bytes), [80, 112]);
  assert.equal(v5Manifest.output.measured.unique_opaque_rgb_colours, 27);
  assert.equal(v5Manifest.output.measured.opaque_texels, 2419);
  assert.deepEqual([v5Manifest.output.measured.visible_body_width_texels, v5Manifest.output.measured.visible_body_height_texels], [43, 96]);
  assert.equal(v5Manifest.pixel_changes.total, 309);
  assert.equal(v5Manifest.pixel_changes.texels.length, 309);
  assert.equal(v5Report.sources['selout-v5'].sha256, v5Manifest.output.sha256);
  assert.equal(v5Report.sources['selout-v4-reference'].sha256, v4Manifest.output.sha256);
  for (const doc of [v5Manifest, v5Report]) { assert.equal(doc.art_approved, false); assert.equal(doc.human_reviewed, false); }
  assert.equal(v5Manifest.walk_frames, 0, 'the v5 static candidate itself contains no walk frames');
  assert.equal(v5Manifest.runtime_integrated, false);
  assert.deepEqual(v5Report.acceptance_counters_unchanged, {runtime_exploration_sprites_accepted: '0/52', scene_quality_gates_passed: '0/11'});
  assert.equal(v5Report.captures.length, 8);
  const v5CaptureFiles = [];
  for (const scene of scenes) {
    assert.equal(v5Report.v5_vs_v4_same_scene[scene].changed_window_pixels, 309, scene + ' changed window pixels');
    assert.equal(v5Report.v5_vs_v4_same_scene[scene].matches_expected, true);
    for (const variant of ['selout-v5', 'selout-v4-reference']) {
      const capture = v5Report.captures.find(c => c.scene === scene && c.variant === variant);
      assert.ok(capture, `${scene}/${variant} capture recorded`);
      const name = `rpg-2-star-ocean-the-second_${scene}_protagonist-female-south-idle-${variant}-h48_${v5Stem}.png`;
      assert.equal(path.basename(capture.capture), name);
      const bytes = fs.readFileSync(path.join(root, 'outputs', name));
      assert.equal(sha256(bytes), capture.capture_sha256, name);
      assert.deepEqual(pngSize(bytes), [1280, 720]);
      assert.equal(capture.pilot_source_sha256, variant === 'selout-v5' ? v5Manifest.output.sha256 : v4Manifest.output.sha256);
      assert.equal(capture.pilot_texel_fidelity.exact_rgb_matches, capture.pilot_texel_fidelity.opaque_texels);
      assert.equal(capture.pilot_texel_fidelity.opaque_texels, variant === 'selout-v5' ? 2419 : 2443);
      assert.deepEqual([capture.pilot_window_diff_bounds_measured.w, capture.pilot_window_diff_bounds_measured.h], [43, 96]);
      v5CaptureFiles.push({name, sha: capture.capture_sha256});
    }
  }
  assert.equal(new Set(v5CaptureFiles.map(c => c.sha)).size, 8, 'eight distinct v5-run capture files');
  // The manifest's embedded QA record must point at this exact report and these exact captures.
  assert.ok(v5Manifest.qa_captures && typeof v5Manifest.qa_captures === 'object', 'v5 manifest embeds qa_captures');
  assert.equal(v5Manifest.qa_captures.report, path.basename(v5ReportPath));
  assert.equal(v5Manifest.qa_captures.report_sha256, textSha256(fs.readFileSync(v5ReportPath)), 'manifest records the current report hash');
  assert.equal(v5Manifest.qa_captures.captures.length, 8);
  for (const mc of v5Manifest.qa_captures.captures) {
    const rc = v5Report.captures.find(c => c.scene === mc.scene && c.variant === mc.variant);
    assert.ok(rc, `${mc.scene}/${mc.variant} in report`);
    assert.equal(mc.capture_sha256, rc.capture_sha256, `${mc.scene}/${mc.variant} capture hash in manifest = report`);
  }
  assert.ok(femaleVariant.gates.exploration_animation.unregistered_manifests.includes(v5ManifestRel), 'checklist lists the v5 manifest');
  pass('v5 sprite 80x112 27 colours 2419 opaque 309 changed texels; source = v4; report source hashes match; manifest qa_captures = report name/hash + 8 capture hashes; 8 separate 1280x720 captures (v5 + same-run v4) match, 2419/2419 texels, 309 changed window pixels per scene; art_approved false; human_reviewed false kept as capture-time provenance; v5 candidate adds no walk frames; checklist lists v5 manifest');

  // 4d. v6 sprite, manifest, report and its eight captures (v6 + same-run v5 reference). Reviewed by the user ("明亮场景
  // 对比度仍不足"), NOT approved. human_reviewed: false in the report and manifest is generation-time provenance.
  const v6Manifest = JSON.parse(fs.readFileSync(path.join(root, v6ManifestRel), 'utf8'));
  const v6Report = JSON.parse(fs.readFileSync(v6ReportPath, 'utf8'));
  const v6Bytes = fs.readFileSync(v6Png);
  assert.equal(sha256(v6Bytes), 'f606afeb70e422b5f0c44373126a7112830e8ed47c22433b18255829fedd283b');
  assert.equal(sha256(v6Bytes), v6Manifest.output.sha256);
  assert.equal(v6Manifest.source.sha256, v5Manifest.output.sha256, 'v6 source is the unchanged v5');
  assert.equal(sha256(v5Bytes), v6Manifest.source.sha256, 'v5 PNG still matches the v6 source lock');
  assert.deepEqual(pngSize(v6Bytes), [80, 112]);
  assert.equal(v6Manifest.output.measured.unique_opaque_rgb_colours, 27);
  assert.deepEqual(v6Manifest.new_colours, []);
  assert.equal(v6Manifest.output.measured.opaque_texels, 2419);
  assert.deepEqual([v6Manifest.output.measured.visible_body_width_texels, v6Manifest.output.measured.visible_body_height_texels], [43, 96]);
  assert.equal(v6Manifest.pixel_changes.total, 301);
  assert.equal(v6Manifest.pixel_changes.texels.length, 301);
  assert.deepEqual(v6Manifest.pixel_changes.per_op, {coat_darken: 275, contour_ink: 26});
  assert.equal(v6Manifest.protected_invariants.alpha_identical_everywhere, true);
  assert.equal(v6Report.sources['selout-v6'].sha256, v6Manifest.output.sha256);
  assert.equal(v6Report.sources['selout-v5-reference'].sha256, v5Manifest.output.sha256);
  for (const doc of [v6Manifest, v6Report]) { assert.equal(doc.art_approved, false); assert.equal(doc.human_reviewed, false); }
  assert.equal(v6Manifest.walk_frames, 0, 'the v6 static candidate itself contains no walk frames');
  assert.equal(v6Manifest.runtime_integrated, false);
  assert.deepEqual(v6Report.acceptance_counters_unchanged, {runtime_exploration_sprites_accepted: '0/52', scene_quality_gates_passed: '0/11'});
  assert.equal(v6Report.captures.length, 8);
  const v6CaptureFiles = [];
  for (const scene of scenes) {
    assert.equal(v6Report.v6_vs_v5_same_scene[scene].changed_window_pixels, 301, scene + ' changed window pixels');
    assert.equal(v6Report.v6_vs_v5_same_scene[scene].matches_expected, true);
    for (const variant of ['selout-v6', 'selout-v5-reference']) {
      const capture = v6Report.captures.find(c => c.scene === scene && c.variant === variant);
      assert.ok(capture, `${scene}/${variant} capture recorded`);
      const name = `rpg-2-star-ocean-the-second_${scene}_protagonist-female-south-idle-${variant}-h48_${v6Stem}.png`;
      assert.equal(path.basename(capture.capture), name);
      const bytes = fs.readFileSync(path.join(root, 'outputs', name));
      assert.equal(sha256(bytes), capture.capture_sha256, name);
      assert.deepEqual(pngSize(bytes), [1280, 720]);
      assert.equal(capture.pilot_source_sha256, variant === 'selout-v6' ? v6Manifest.output.sha256 : v5Manifest.output.sha256);
      assert.equal(capture.pilot_texel_fidelity.exact_rgb_matches, capture.pilot_texel_fidelity.opaque_texels);
      assert.equal(capture.pilot_texel_fidelity.opaque_texels, 2419);
      assert.deepEqual([capture.pilot_window_diff_bounds_measured.w, capture.pilot_window_diff_bounds_measured.h], [43, 96]);
      v6CaptureFiles.push({name, sha: capture.capture_sha256});
    }
  }
  assert.equal(new Set(v6CaptureFiles.map(c => c.sha)).size, 8, 'eight distinct v6-run capture files');
  assert.ok(v6Manifest.qa_captures && typeof v6Manifest.qa_captures === 'object', 'v6 manifest embeds qa_captures');
  assert.equal(v6Manifest.qa_captures.report, path.basename(v6ReportPath));
  assert.equal(v6Manifest.qa_captures.report_sha256, textSha256(fs.readFileSync(v6ReportPath)), 'manifest records the current report hash');
  assert.equal(v6Manifest.qa_captures.captures.length, 8);
  for (const mc of v6Manifest.qa_captures.captures) {
    const rc = v6Report.captures.find(c => c.scene === mc.scene && c.variant === mc.variant);
    assert.ok(rc, `${mc.scene}/${mc.variant} in report`);
    assert.equal(mc.capture_sha256, rc.capture_sha256, `${mc.scene}/${mc.variant} capture hash in manifest = report`);
  }
  assert.ok(femaleVariant.gates.exploration_animation.unregistered_manifests.includes(v6ManifestRel), 'checklist lists the v6 manifest');
  pass('v6 sprite 80x112 27 colours (none new) 2419 opaque 301 changed texels (275 coat darken + 26 contour ink), alpha identical; source = v5; report source hashes match; manifest qa_captures = report name/hash + 8 capture hashes; 8 separate 1280x720 captures (v6 + same-run v5) match, 2419/2419 texels, 301 changed window pixels per scene; art_approved false; human_reviewed false kept as capture-time provenance; v6 candidate adds no walk frames; checklist lists v6 manifest');

  // 4e. v8 sprite, manifest, report and its six captures (v8 + same-position v7 reference). The user reviewed the bright
  // city + bright outskirts captures and replied "够了，可作为静止帧基准": approved ONLY as the female south idle static
  // still-frame baseline at 48 logical px. Manifest/report flags stay as generation-time provenance; counters unchanged.
  const v8Manifest = JSON.parse(fs.readFileSync(path.join(root, v8ManifestRel), 'utf8'));
  const v8Report = JSON.parse(fs.readFileSync(v8ReportPath, 'utf8'));
  const v8Bytes = fs.readFileSync(v8Png);
  assert.equal(sha256(v8Bytes), 'ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd');
  assert.equal(sha256(v8Bytes), v8Manifest.output.sha256);
  // Was locked as 0fa7937d…5992, the raw hash of the CRLF Windows working copy; same content, line-ending independent:
  assert.equal(textSha256(fs.readFileSync(path.join(root, v8ManifestRel))), '3ba35811bf4d55b061b7719c6451908bdbb1eb68425bdda2c2303cc669f310ed');
  assert.equal(sha256(fs.readFileSync(v7Png)), v8Manifest.source.sha256, 'v7 PNG still matches the v8 source lock');
  assert.equal(sha256(v6Bytes), v8Manifest.source.also_preserved.v6.sha256, 'v6 PNG unchanged');
  assert.deepEqual(pngSize(v8Bytes), [80, 112]);
  assert.equal(v8Manifest.output.measured.unique_opaque_rgb_colours, 32);
  assert.equal(v8Manifest.output.measured.opaque_texels, 2419);
  assert.equal(v8Manifest.pixel_changes.total, 793);
  assert.equal(v8Manifest.pixel_changes.texels.length, 793);
  assert.equal(v8Manifest.protected_invariants.alpha_identical_everywhere, true);
  for (const doc of [v8Manifest, v8Report]) { assert.equal(doc.art_approved, false); assert.equal(doc.human_reviewed, false); }
  assert.equal(v8Manifest.walk_frames, 0, 'the v8 static baseline itself contains no walk frames');
  assert.equal(v8Manifest.runtime_integrated, false, 'v8 is not wired into the runtime');
  assert.deepEqual(v8Report.acceptance_counters_unchanged, {runtime_exploration_sprites_accepted: '0/52', scene_quality_gates_passed: '0/11'});
  assert.equal(v8Report.sources['selout-v8'].sha256, v8Manifest.output.sha256);
  assert.equal(v8Report.sources['selout-v7-reference'].sha256, v8Manifest.source.sha256);
  assert.equal(textSha256(fs.readFileSync(v8ReportPath)), v8Manifest.qa_captures.report_sha256, 'manifest records the v8 report hash');
  assert.equal(v8Report.captures.length, 6);
  const v8Scenes = ['city-bright', 'outskirts-bright', 'survey-annex-room2-dark'];
  const v8CaptureFiles = [];
  for (const scene of v8Scenes) {
    assert.equal(v8Report.v8_vs_v7_same_scene[scene].changed_window_pixels, 793, scene + ' changed window pixels');
    assert.equal(v8Report.v8_vs_v7_same_scene[scene].matches_expected, true);
    for (const variant of ['selout-v8', 'selout-v7-reference']) {
      const capture = v8Report.captures.find(c => c.scene === scene && c.variant === variant);
      assert.ok(capture, `${scene}/${variant} capture recorded`);
      const name = `rpg-2-star-ocean-the-second_${scene}_protagonist-female-south-idle-${variant}-h48_${v8Stem}.png`;
      assert.equal(path.basename(capture.capture), name);
      const bytes = fs.readFileSync(path.join(root, 'outputs', name));
      assert.equal(sha256(bytes), capture.capture_sha256, name);
      assert.deepEqual(pngSize(bytes), [1280, 720]);
      assert.equal(capture.pilot_texel_fidelity.exact_rgb_matches, 2419);
      assert.deepEqual([capture.pilot_window_diff_bounds_measured.w, capture.pilot_window_diff_bounds_measured.h], [43, 96]);
      const mc = v8Manifest.qa_captures.captures.find(c => c.scene === scene && c.variant === variant);
      assert.equal(mc.capture_sha256, capture.capture_sha256, `${scene}/${variant} capture hash in manifest = report`);
      v8CaptureFiles.push({name, sha: capture.capture_sha256, scene, variant});
    }
  }
  assert.equal(new Set(v8CaptureFiles.map(c => c.sha)).size, 6, 'six distinct v8-run capture files');
  for (const file of [v8QaNote, v8Decision]) assert.ok(fs.existsSync(path.join(root, file)), file);
  const decisionText = fs.readFileSync(path.join(root, v8Decision), 'utf8');
  assert.ok(decisionText.includes('够了，可作为静止帧基准') && decisionText.includes('0/52') && decisionText.includes('0/11') && decisionText.includes('0/2'));
  for (const c of v8CaptureFiles.filter(c => c.variant === 'selout-v8')) assert.ok(decisionText.includes(c.name) && decisionText.includes(c.sha), 'decision record links ' + c.name);
  // The static baseline is recorded separately in the readiness checklist and never passes a gate or counter.
  const baseline = femaleVariant.gates.exploration_animation.static_idle_baseline;
  assert.ok(baseline, 'checklist records the female static idle baseline');
  assert.deepEqual([baseline.facing, baseline.pose, baseline.frames, baseline.display_height_logical_px, baseline.user_reply_zh], ['south', 'idle', 1, 48, '够了，可作为静止帧基准']);
  assert.equal(baseline.decision_record, v8Decision);
  assert.equal(baseline.files.png.sha256, v8Manifest.output.sha256);
  assert.ok(Object.values(baseline.files).every(f => f.exists && f.sha256_matches !== false), 'all baseline files exist with matching hashes');
  // Recompute every lock here rather than trusting the stored flag; PNGs must stay on exact bytes.
  for (const [role, f] of Object.entries(baseline.files)) {
    if (!f.sha256) continue;
    assert.equal(f.sha256_algorithm, f.path.endsWith('.png') ? BYTES_HASH : TEXT_HASH, role + ' hash algorithm');
    assert.equal(contentHash(fs.readFileSync(path.join(root, f.path)), f.sha256_algorithm), f.sha256, role + ' lock');
  }
  assert.equal(femaleVariant.gates.exploration_animation.status, 'pending');
  assert.deepEqual(femaleVariant.gates.four_facing.production_directions_done, []);
  assert.equal(femaleVariant.gates.art_acceptance.status, 'pending');
  assert.deepEqual(checklist.summary.static_idle_baselines_user_approved, ['protagonist-female']);
  assert.equal(checklist.variants.filter(v => v.gates.exploration_animation.static_idle_baseline).length, 1, 'only the female variant has a static baseline');
  assert.equal(female.checked, false, 'inventory runtime-sprite.protagonist-female stays unchecked');
  for (const rel of [v7ManifestRel, v8ManifestRel]) assert.ok(femaleVariant.gates.exploration_animation.unregistered_manifests.includes(rel), 'checklist lists ' + rel);
  const progressMd = fs.readFileSync(path.join(root, 'docs', 'progress.md'), 'utf8');
  const v8Section = progressMd.slice(progressMd.indexOf('## 2026-10-14 - Selout v7 and v8'));
  assert.ok(v8Section.includes('够了，可作为静止帧基准') && v8Section.includes('**0/52**') && v8Section.includes('**0/11**') && v8Section.includes('**0/2**'));
  assert.ok(progressMd.includes('## 2026-10-14 - Selout v6 value/separation static candidate: technical captures, user reviewed (bright-scene contrast still insufficient), not approved'), 'v6 history kept');
  pass('v8 sprite 80x112 32 colours 2419 opaque 793 changed texels, alpha identical; source = v7, v6 unchanged; 6 separate 1280x720 captures (v8 + same-position v7) match report + manifest, 2419/2419 texels, 793 changed window pixels; decision record + QA note present; checklist static_idle_baseline (south idle, 1 frame, 48 px) hash-locked while G1/G2/G5 stay pending; inventory unchecked; progress.md records decision with 0/52, 0/11, 0/2');

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

    // v5: its own card after the v4 card, inline v5 captures only, v4 comparisons and prototype room as links, no acceptance controls.
    const v5Start = html.indexOf('<section class="card" id="idle-selout-v5">');
    const v5Card = html.slice(v5Start, html.indexOf('</section>', v5Start) + '</section>'.length);
    assert.ok(v5Start > v4Start && v5Card.length > 100, 'v5 card follows the v4 card');
    assert.equal((html.match(/id="idle-selout-v5"/g) || []).length, 1, 'exactly one v5 card');
    assert.ok(!v4Card.includes('selout-v5') && !card.includes('selout-v5'), 'v2 and v4 cards do not mention v5 captures');
    assert.ok(v5Card.includes('状态：未批准') && v5Card.includes('更接近了，继续精修') && v5Card.includes('继续精修'), 'unapproved; user reviewed and asked for more refinement');
    assert.ok(!v5Card.includes('尚未回复') && !v5Card.includes('待用户回复'), 'no stale awaiting-reply wording');
    assert.ok(v5Card.includes('human_reviewed: false') && v5Card.includes('早于用户回复'), 'capture-time human_reviewed:false explained');
    assert.ok(!/已批准|已验收|approved/i.test(v5Card.replace(/未批准|未获美术批准|没有任何行走动画获批准/g, '')), 'no approval wording');
    assert.ok(!/<button|<input|<select|<textarea/.test(v5Card), 'no acceptance controls on the v5 card');
    assert.ok(v5Card.includes('0/52') && v5Card.includes('0/11') && v5Card.includes('行走帧仍暂停'));
    assert.ok(v5Card.includes('309') && v5Card.includes('2419/2419') && v5Card.includes('已知局限'));
    assert.ok(v5Card.includes('实验性行走帧原型') && v5Card.includes('动画验收为 0'), 'walk prototypes exist; animation acceptance 0');
    const v5Imgs = [...v5Card.matchAll(/<img src="([^"]+)"/g)].map(m => m[1]);
    assert.deepEqual(v5Imgs, ['city', 'outskirts-bright', 'survey-annex-room2-dark'].map(s => `/assets/rpg-2-star-ocean-the-second_${s}_protagonist-female-south-idle-selout-v5-h48_${v5Stem}.png`));
    const v5Hrefs = new Set([...v5Card.matchAll(/href="([^"]+)"/g)].map(m => m[1]));
    for (const c of v5CaptureFiles) {
      const href = '/assets/' + c.name;
      assert.ok(v5Hrefs.has(href), 'v5 card links ' + c.name);
      const response = await fetch(base + href);
      assert.equal(response.status, 200, href);
      assert.equal(sha256(Buffer.from(await response.arrayBuffer())), c.sha, href + ' served bytes');
    }
    assert.equal(v5Hrefs.size, 8, 'v5 card links exactly its eight captures');
    pass('Production view: one separate v5 card after the v4 card, 3 inline v5 captures (city/bright/dark), 4 v4 references + dark prototype room as links, all 8 served byte-identical, user-reviewed (closer, keep refining) and unapproved, no acceptance controls, 0/52 and 0/11 unchanged');

    // v6: its own card after the v5 card, inline v6 captures only, v5 comparisons and prototype room as links, no acceptance controls.
    const v6Start = html.indexOf('<section class="card" id="idle-selout-v6">');
    const v6Card = html.slice(v6Start, html.indexOf('</section>', v6Start) + '</section>'.length);
    assert.ok(v6Start > v5Start && v6Card.length > 100, 'v6 card follows the v5 card');
    assert.equal((html.match(/id="idle-selout-v6"/g) || []).length, 1, 'exactly one v6 card');
    assert.ok(![card, v4Card, v5Card].some(c => c.includes('selout-v6')), 'v2, v4 and v5 cards do not mention v6 captures');
    assert.ok(v6Card.includes('状态：未批准') && v6Card.includes('明亮场景对比度仍不足'), 'unapproved; records the user reply on bright-scene contrast');
    assert.ok(!v6Card.includes('尚未回复') && !v6Card.includes('待用户回复') && !v6Card.includes('未经用户审阅'), 'no stale awaiting-review wording');
    assert.ok(v6Card.includes('human_reviewed: false') && v6Card.includes('不代表当前审阅状态'), 'capture-time human_reviewed:false explained');
    assert.ok(!/已批准|已验收|approved/i.test(v6Card.replace(/未批准|未获美术批准|没有任何行走动画获批准/g, '')), 'no approval wording');
    assert.ok(!/<button|<input|<select|<textarea/.test(v6Card), 'no acceptance controls on the v6 card');
    assert.ok(v6Card.includes('0/52') && v6Card.includes('0/11') && v6Card.includes('0/2') && v6Card.includes('行走帧仍暂停'));
    assert.ok(v6Card.includes('301') && v6Card.includes('2419/2419') && v6Card.includes('已知局限'));
    assert.ok(v6Card.includes('实验性行走帧原型') && v6Card.includes('动画验收为 0'), 'walk prototypes exist; animation acceptance 0');
    const v6Imgs = [...v6Card.matchAll(/<img src="([^"]+)"/g)].map(m => m[1]);
    assert.deepEqual(v6Imgs, ['city', 'outskirts-bright', 'survey-annex-room2-dark'].map(s => `/assets/rpg-2-star-ocean-the-second_${s}_protagonist-female-south-idle-selout-v6-h48_${v6Stem}.png`));
    const v6Hrefs = new Set([...v6Card.matchAll(/href="([^"]+)"/g)].map(m => m[1]));
    for (const c of v6CaptureFiles) {
      const href = '/assets/' + c.name;
      assert.ok(v6Hrefs.has(href), 'v6 card links ' + c.name);
      const response = await fetch(base + href);
      assert.equal(response.status, 200, href);
      assert.equal(sha256(Buffer.from(await response.arrayBuffer())), c.sha, href + ' served bytes');
    }
    assert.equal(v6Hrefs.size, 8, 'v6 card links exactly its eight captures');
    assert.ok(v6Card.includes(path.basename(v6Png)) && v6Card.includes(path.basename(v6ReportPath)), 'v6 card names its source PNG and QA report');
    pass('Production view: one separate v6 card after the v5 card, 3 inline v6 captures (city/bright/dark), 4 v5 references + dark prototype room as links, all 8 served byte-identical, user-reviewed (bright-scene contrast still insufficient) and unapproved, no acceptance controls, 0/52, 0/11 and 0/2 unchanged');

    // v8: its own card after the v6 card. Approved ONLY as the south idle static still-frame baseline; every exclusion and
    // counter is stated, earlier cards keep their unapproved status, and no acceptance controls appear.
    const v8Start = html.indexOf('<section class="card" id="idle-selout-v8">');
    const v8Card = html.slice(v8Start, html.indexOf('</section>', v8Start) + '</section>'.length);
    assert.ok(v8Start > v6Start && v8Card.length > 100, 'v8 card follows the v6 card');
    assert.ok(v8Start < html.indexOf('id="character-readiness"'), 'v8 card precedes the readiness checklist');
    assert.equal((html.match(/id="idle-selout-v8"/g) || []).length, 1, 'exactly one v8 card');
    assert.equal((html.match(/id="idle-selout-v7"/g) || []).length, 0, 'v7 has no separate card');
    assert.ok(![card, v4Card, v5Card, v6Card].some(c => c.includes('selout-v8') || c.includes('静止帧基准')), 'earlier cards untouched by v8');
    assert.ok(v6Card.includes('状态：未批准') && v6Card.includes('明亮场景对比度仍不足'), 'v6 keeps its earlier unapproved status');
    assert.ok(v8Card.includes('用户已批准 · 仅南向待机静态基准帧') && v8Card.includes('够了，可作为静止帧基准'), 'approval badge and verbatim user reply');
    assert.ok(v8Card.includes('48 逻辑像素') && v8Card.includes('南向待机这一张静态帧'), 'scope: south idle static frame at 48 px');
    for (const excluded of ['探索动画', '北／东／西其他朝向', '替换游戏内运行时精灵', '0/52', '0/11', '0/2', '动画验收为 0', 'v6 仍是“明亮场景对比度仍不足”、未批准', 'v7', '未批准'])
      assert.ok(v8Card.includes(excluded), 'v8 card states: ' + excluded);
    assert.ok(!/已验收|art_approved: true/.test(v8Card), 'no acceptance wording');
    assert.ok(!/<button|<input|<select|<textarea/.test(v8Card), 'no acceptance controls on the v8 card');
    assert.ok(v8Card.includes('human_reviewed: false') && v8Card.includes('早于用户回复'), 'generation-time flags explained');
    for (const receipt of [path.basename(v8Png), path.basename(v8ManifestRel), path.basename(v8ReportPath), path.basename(v8QaNote), path.basename(v8Decision)])
      assert.ok(v8Card.includes(receipt), 'v8 card names ' + receipt);
    const v8Imgs = [...v8Card.matchAll(/<img src="([^"]+)"/g)].map(m => m[1]);
    assert.deepEqual(v8Imgs, v8Scenes.map(s => `/assets/rpg-2-star-ocean-the-second_${s}_protagonist-female-south-idle-selout-v8-h48_${v8Stem}.png`));
    const v8Hrefs = new Set([...v8Card.matchAll(/href="([^"]+)"/g)].map(m => m[1]));
    for (const c of v8CaptureFiles) {
      const href = '/assets/' + c.name;
      assert.ok(v8Hrefs.has(href), 'v8 card links ' + c.name);
      const response = await fetch(base + href);
      assert.equal(response.status, 200, href);
      assert.equal(sha256(Buffer.from(await response.arrayBuffer())), c.sha, href + ' served bytes');
    }
    assert.equal(v8Hrefs.size, 6, 'v8 card links exactly its six captures');
    assert.ok(html.includes('用户已批准 selout v8 作为女主南向待机静态帧基准') && !html.includes('待新的静态待机获用户批准后再开始'), 'visual-acceptance summary updated');
    assert.ok(html.includes('探索精灵 0 / 52') && html.includes('场景画质 0 / 11'), 'page counters unchanged');
    const readinessStart = html.indexOf('id="character-readiness"');
    const femaleRowStart = html.indexOf('data-readiness-open="readiness.protagonist-female"', readinessStart);
    const femaleRow = html.slice(femaleRowStart, html.indexOf('</details>', femaleRowStart));
    assert.ok(femaleRowStart > 0 && femaleRow.includes('静态基准帧：south idle selout v8 cloth-leather') && femaleRow.includes('本闸门不因此通过'), 'readiness G2 row shows the static baseline');
    assert.ok(femaleRow.includes('美术验收 待定'), 'female art acceptance still pending');
    pass('Production view: one separate v8 card after the v6 card, 3 inline v8 captures (bright city/bright outskirts/dark annex), 3 v7 references as links, all 6 served byte-identical; badge = south idle static baseline only; verbatim reply; exclusions (animation, other facings, runtime swap) and 0/52, 0/11, 0/2 stated; v6 stays unapproved; no controls; readiness G2 row shows baseline with art acceptance pending');
  } finally {
    child.kill();
  }
  console.log(`RESULT PASS (${results.length} checks)`);
})().catch(error => { console.error('RESULT FAIL'); console.error(error); process.exitCode = 1; });
