// Focused check for the Game Bible cross-device visual review queue (environmentVisualReview.crossDeviceReviewQueue) and the
// Chicago Loop scene-denominator review. Badges must follow the recorded approval flags, every queue image must be an actual
// Godot capture served byte-identical (two live in run subdirectories), generated concepts must never render as images, all eight
// must be committed with the exact recorded blob at the recorded commit (none staged), and no counter or the 40.8% meter may move.
// Starts the real v05 panel server on a spare local port, then runs the served bible.js in a VM with a minimal DOM stub.
// Read-only: no project file is written. Run from the repository root: node tests/game-bible-review-queue/<this file>
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const net = require('node:net');
const path = require('node:path');
const vm = require('node:vm');
const {spawn, spawnSync} = require('node:child_process');

const root = path.resolve(__dirname, '..', '..');
const rel = file => path.join(root, ...file.split('/'));
const server = rel('tools/rpg-2-star-ocean-the-second_game-bible_server_v05_20261013-222437-3d5b8a9f.js');
const meterCli = 'tools/rpg-2-star-ocean-the-second_mvp-completion-meter_recompute-and-task-closeout-cli_v01_20261015-233032-d296a2cb.js';
const biblePath = 'outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json';
const progressPath = 'outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json';
const inventoryPath = 'outputs/rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json';
const sha256 = data => crypto.createHash('sha256').update(data).digest('hex');
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const pass = label => console.log('PASS ' + label);
const git = (...args) => spawnSync('git', args, {cwd: root, encoding: 'utf8'});
const tracked = file => git('ls-files', '--error-unmatch', file).status === 0;

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
  await waitFor(() => content.innerHTML.includes('id="cross-device-review-queue"'), 'review queue card');
  return content.innerHTML;
}

(async () => {
  // Local-only captures are absent in a clean clone; their checks then reduce to 'untracked and pinned', and they must not be served.
  const present = item => fs.existsSync(rel(item.file));
  const before = [biblePath, progressPath, inventoryPath].map(file => sha256(fs.readFileSync(rel(file))));
  const bible = JSON.parse(fs.readFileSync(rel(biblePath), 'utf8'));
  const progress = JSON.parse(fs.readFileSync(rel(progressPath), 'utf8'));
  const env = bible.environmentVisualReview;
  const queue = env.crossDeviceReviewQueue;

  // 1. Eight actual Godot captures, in order, each with its own QA note; badges follow the recorded flags.
  assert.ok(queue && Array.isArray(queue.items), 'queue present');
  assert.deepEqual(queue.items.map(item => item.order), [1, 2, 3, 4, 5, 6, 7, 8]);
  assert.ok(queue.items.every(item => item.kind === 'actual-godot-capture'), 'every queue item is an actual Godot capture');
  assert.ok(fs.existsSync(rel(queue.source)), 'queue source note exists');
  const v8Baseline = bible.characterVisualReview.staticBaselinesAndPilots.femaleExplorationSouthBaseline;
  for (const item of queue.items) {
    assert.match(item.file, /^outputs\/([A-Za-z0-9][A-Za-z0-9._-]*\/)?[A-Za-z0-9][A-Za-z0-9._-]*\.png$/, 'queue file is a PNG under outputs/');
    assert.ok(item.syncState === 'local-only' || present(item), 'committed queue image exists: ' + item.file);
    assert.ok(item.qa && fs.existsSync(rel(item.qa)), 'queue QA note exists: ' + item.qa);
    assert.equal(item.runtimeIntegrated, false, 'nonruntime: ' + item.order);
    assert.equal(item.artAccepted, false, 'not accepted: ' + item.order);
    assert.equal(item.creatorApproved, item.order === 1, 'only the selout v8 still is creator-approved');
    assert.equal(item.badge.tone, item.creatorApproved ? 'good' : 'warn');
    assert.ok(item.creatorApproved ? /Approved static baseline/.test(item.badge.en) : /^Unapproved/.test(item.badge.en), 'stored badge matches flag: ' + item.order);
    assert.ok(/nonruntime/.test(item.badge.en) && /未接入运行时/.test(item.badge.zh), 'stored badge says nonruntime: ' + item.order);
  }
  assert.equal(v8Baseline.creatorApproved, true);
  assert.equal(v8Baseline.runtimeIntegrated, false);
  assert.match(queue.items[0].approvalScope, /static south still/);
  // #7/#8: female battle v11 bright/dark captures for creator feedback. Only the 0.65 proportion is approved; the editable
  // source is tracked at the same commit and its manifest still says unapproved and not runtime-integrated.
  const v11 = queue.items.slice(6);
  assert.deepEqual(v11.map(item => item.file.match(/party-capture-([a-z]+)-640_unapproved-v11_/)?.[1]), ['archive', 'outskirts']);
  for (const item of v11) {
    assert.equal(item.syncState, 'committed-at-53a912f', 'v11 capture committed at 53a912f: ' + item.order);
    assert.equal(item.approvedScopeOnly, '0.65 battle display proportion');
    assert.ok(/v11/.test(item.label.en) && /v11/.test(item.label.zh), 'v11 label: ' + item.order);
    assert.ok(fs.existsSync(rel(item.reviewPacket)) && fs.existsSync(rel(item.captureManifest)), 'v11 review packet and capture manifest exist: ' + item.order);
    const captureManifest = JSON.parse(fs.readFileSync(rel(item.captureManifest), 'utf8'));
    assert.equal(captureManifest.captureSha256, item.sha256, 'capture manifest pins the queue sha256: ' + item.order);
    for (const source of Object.values(item.editableSource)) {
      assert.ok(git('rev-parse', '--verify', '--quiet', '53a912f:' + source).status === 0 && tracked(source), 'v11 source tracked at 53a912f: ' + source);
    }
    const sprite = JSON.parse(fs.readFileSync(rel(item.editableSource.manifest), 'utf8'));
    assert.deepEqual([sprite.art_approved, sprite.runtime_integrated], [false, false], 'v11 sprite manifest: unapproved, nonruntime');
    assert.equal(captureManifest.candidateSha256, sha256(fs.readFileSync(rel(item.editableSource.png))), 'capture used the tracked v11 sprite: ' + item.order);
  }
  assert.ok(/^Unapproved static pilot/.test(v11[0].caption.en) && /only the 0.65 proportion is approved/.test(v11[0].caption.en) && /Not a complete character sprite; no animation/.test(v11[0].caption.en), 'v11 caption states its limits');
  assert.equal(git('grep', '-l', 'unapproved-v11_20261017-023937-873fe1e6', 'HEAD', '--', 'game/scripts', 'game/scenes').stdout.trim(), '', 'no runtime script or scene references the v11 sprite');
  pass('queue: 8 actual Godot captures in order, QA notes on disk, only #1 (selout v8 still) creator-approved, all nonruntime and unaccepted; #7/#8 v11 archive/outskirts with tracked .pxo/.ora/PNG/manifest at 53a912f, unreferenced by runtime');

  // 2. Sync state matches Git: all eight are committed, none staged or local-only. Each recorded short SHA resolves to a commit in
  // HEAD's history, and the blob at <sha>:<file> is exactly the recorded gitBlob; the working file has the recorded blob and sha256.
  // The three former Git-proposal captures (#3, #5, #6) are committed at 15d153b and stay sha256-pinned in their evidence index.
  const staged = queue.items.filter(item => item.syncState === 'staged-not-pushed');
  assert.equal(staged.length, 0, 'no queue image is still staged-not-pushed');
  assert.equal(queue.items.filter(item => item.syncState === 'local-only').length, 0, 'no queue image is local-only');
  for (const item of queue.items) {
    assert.match(item.syncState, /^committed-at-[0-9a-f]{7}$/, 'committed: ' + item.order);
    assert.match(item.gitBlob, /^[0-9a-f]{40}$/, 'recorded blob: ' + item.order);
    const commit = git('rev-parse', '--verify', '--quiet', item.syncState.slice('committed-at-'.length) + '^{commit}').stdout.trim();
    assert.match(commit, /^[0-9a-f]{40}$/, 'recorded commit resolves: ' + item.order);
    assert.equal(git('merge-base', '--is-ancestor', commit, 'HEAD').status, 0, 'recorded commit is in HEAD history: ' + item.order);
    assert.equal(git('rev-parse', commit + ':' + item.file).stdout.trim(), item.gitBlob, 'exact blob at the recorded commit: ' + item.order);
    assert.ok(tracked(item.file), 'committed item is tracked: ' + item.file);
    assert.equal(git('hash-object', '--', item.file).stdout.trim(), item.gitBlob, 'working file blob matches: ' + item.order);
    assert.equal(sha256(fs.readFileSync(rel(item.file))), item.sha256, 'recorded sha256 matches the file: ' + item.order);
    if (item.hashPinnedIn) {
      const index = JSON.stringify(JSON.parse(fs.readFileSync(rel(item.hashPinnedIn), 'utf8')));
      assert.ok(index.includes(item.sha256), 'sha256 still pinned in its evidence index: ' + item.order);
    }
  }
  const proposal = queue.gitProposal;
  assert.deepEqual(proposal.items, [3, 5, 6]);
  assert.equal(proposal.state, 'committed-at-15d153b');
  for (const order of proposal.items) {
    const item = queue.items[order - 1];
    assert.equal(item.syncState, 'committed-at-15d153b', 'proposal item committed at 15d153b: ' + order);
    assert.match(item.file, /unapproved/, 'proposal capture is labelled unapproved in its name: ' + order);
    assert.ok(item.hashPinnedIn, 'proposal item keeps its evidence index: ' + order);
  }
  assert.ok(fs.existsSync(rel(proposal.qa)) && fs.existsSync(rel(proposal.syncQa)), 'Git proposal and sync QA notes exist');
  assert.ok(!/stag/i.test(proposal.state + ' ' + proposal.note), 'Git proposal no longer claims a staged state');
  assert.ok(/site version 11/.test(queue.siteRendering) && !/site version 10/.test(queue.siteRendering), 'Site note names deployed site version 11');
  assert.ok(/eight actual Godot captures are on GitHub/.test(queue.siteRendering), 'Site note says eight captures are on GitHub');
  assert.ok(!/staged|local-only|until the coordinator/.test(queue.siteRendering), 'Site note has no stale staged or local-only claim');
  const committed = queue.items.length;
  pass(`sync state: ${committed}/8 committed (#1, #2, #4 at a87ac16; #3, #5, #6 at 15d153b; #7, #8 at 53a912f), each exact recorded blob at its recorded commit in HEAD history, 0 staged, 0 local-only; Site note says site version 11`);

  // 3. Generated concepts are a separate, gallery-ineligible list and never appear among queue items or Site previews.
  const concepts = queue.nonruntimeConcepts;
  assert.equal(concepts.galleryEligible, false);
  assert.equal(concepts.items.length, 5);
  assert.ok(concepts.items.every(c => ['generated-concept', 'identity-reference'].includes(c.kind) && /^outputs\/[^/]+\.png$/.test(c.file)));
  const queueFiles = new Set(queue.items.map(item => item.file));
  const previewNames = (bible.characterVisualReview.previews || []).map(p => path.posix.basename(p.file));
  assert.ok(concepts.items.every(c => !queueFiles.has(c.file) && !previewNames.includes(path.posix.basename(c.file))), 'no concept in the queue or Site previews');
  pass('concepts: 5 nonruntime references, galleryEligible false, none in the queue or characterVisualReview.previews');

  // 4. Counters and meter as recorded (sprites 0/52, scenes 3/12, playtests 0/2, 40.8%); Chicago denominator proposal recorded but not applied, with the meter recomputed from the formula.
  const counters = progress.approvalLedger.counters;
  assert.deepEqual([counters.runtimeSpritesAccepted, counters.runtimeSpritesTarget, counters.sceneVisualsAccepted, counters.sceneVisualsTarget, counters.humanPlaytests, counters.humanPlaytestsTarget], [0, 52, 3, 12, 0, 2]);
  assert.equal(env.sceneQualityAccepted, 0);
  assert.equal(env.sceneQualityTarget, 12);
  const review = env.sceneQualityDenominatorReview;
  assert.equal(review.applied, true);
  assert.equal(review.currentDenominator, 12);
  assert.equal(review.previousDenominator, 11);
  const revision = progress.completionMeter.taskCloseouts.find(c => c.id === review.appliedCloseoutId);
  assert.ok(revision && revision.kind === 'baseline-revision' && revision.impact.changed === false && revision.impact.percentAfter === 35.8, 'dated baseline-revision closeout recorded');
  assert.deepEqual(revision.impact.baselineChanges, [{category: 'science-environment-art', field: 'denominator', from: 11, to: 12}]);
  assert.equal(review.proposedGateId, 'chicago-loop-outdoor');
  assert.equal(review.originalGates.length, 11);
  assert.ok(!review.originalGates.includes(review.proposedGateId));
  assert.ok(review.qa && fs.existsSync(rel(review.qa)), 'denominator QA note exists');
  assert.equal(review.secondBatch.outcome, 'applied');
  assert.equal(review.secondBatch.creatorConflictFound, false);
  assert.ok(fs.existsSync(rel(review.secondBatch.qa)), 'second-batch QA note exists');
  const meter = spawnSync(process.execPath, [meterCli, 'check'], {cwd: root, encoding: 'utf8'});
  assert.equal(meter.status, 0, meter.stdout + meter.stderr);
  assert.match(meter.stdout, /CHECK OK 40\.8%/);
  const cats = Object.fromEntries(progress.completionMeter.categories.map(c => [c.id, c]));
  const points = denominatorForEnv => Object.values(cats).reduce((sum, c) => sum + c.weight * c.numerator / (c.id === 'science-environment-art' ? denominatorForEnv : c.denominator), 0);
  assert.equal(cats['science-environment-art'].numerator, 3);
  assert.equal(Math.round(points(12) * 10) / 10, 40.8, 'formula with 3/12 scenes gives the recorded 40.8%');
  assert.equal(progress.completionMeter.percent, 40.8);
  pass('counters 0/52 3/12 0/2; meter CLI CHECK OK 40.8%; Chicago gate 12 applied by a dated baseline-revision closeout (35.8% at the time); formula gives 40.8% for /12');

  // 5. Rendered Production view: one card, eight figures with flag-derived badges, images served byte-identical, concepts as text only.
  const port = await freePort();
  const child = spawn(process.execPath, [server], {cwd: root, env: {...process.env, WORLDS_BETWEEN_BIBLE_PORT: String(port)}, stdio: 'ignore'});
  const base = 'http://127.0.0.1:' + port;
  try {
    await waitFor(async () => { try { return (await fetch(base + '/health')).ok; } catch { return false; } }, 'server');
    const html = await renderProduction(base);
    const start = html.indexOf('<section class="card" id="cross-device-review-queue">');
    assert.ok(start > 0);
    assert.equal(html.split('id="cross-device-review-queue"').length, 2, 'exactly one queue card');
    const card = html.slice(start, html.indexOf('</section>', start) + '</section>'.length);
    const figures = card.split('<figure class="visual-sample review-queue-item"').slice(1);
    assert.equal(figures.length, 8);
    assert.equal((card.match(/badge good">已批准静态基准 · 未接入运行时 · 未验收</g) || []).length, 1);
    assert.equal((card.match(/badge warn">未批准 · 未接入运行时 · 未验收</g) || []).length, 7);
    assert.equal((card.match(/仅本机 · 尚未同步到 GitHub/g) || []).length, 0, 'no local-only badge');
    assert.equal((card.match(/已暂存为 Git 候选/g) || []).length, 0, 'no staged badge');
    assert.equal((card.match(/已在 GitHub（[0-9a-f]{7}）/g) || []).length, 8);
    assert.equal((card.match(/已在 GitHub（a87ac16）/g) || []).length, 3);
    assert.equal((card.match(/已在 GitHub（15d153b）/g) || []).length, 3);
    assert.equal((card.match(/已在 GitHub（53a912f）/g) || []).length, 2);
    assert.ok(!/已验收|通过验收/.test(card.replace(/未验收/g, '')), 'no acceptance claim');
    assert.ok(!/<button|<input|type="checkbox"/.test(card), 'no approval controls');
    const imgs = [...card.matchAll(/<img src="([^"]+)"/g)].map(m => m[1]);
    assert.equal(imgs.length, 8);
    for (const [i, src] of imgs.entries()) {
      const response = await fetch(base + src);
      if (!present(queue.items[i])) { assert.equal(response.status, 404, 'absent local-only capture is not served: ' + src); continue; }
      assert.equal(response.status, 200, src);
      assert.equal(response.headers.get('content-type'), 'image/png');
      assert.equal(sha256(Buffer.from(await response.arrayBuffer())), sha256(fs.readFileSync(rel(queue.items[i].file))), 'served byte-identical: ' + src);
    }
    for (const c of concepts.items) assert.ok(!imgs.some(src => src.includes(path.posix.basename(c.file))) && card.includes(c.file), 'concept listed as text only');
    for (const probe of ['/assets/wdc-cw-v08_20261016-155827-6cf49486/technical-check-report.png', '/assets/nyc-chp-v04_20261016-172144-eb092a52/..%2F..%2Fpackage.png',
      '/assets/..%2Ftools%2Fx.png', '/assets/wdc-cw-v08_20261016-155827-6cf49486%2Frpg-2-star-ocean-the-second_wdc-capitol-west_godot-1280x720-entry_unapproved-v08_20261016-155827-6cf49486.png']) {
      assert.equal((await fetch(base + probe)).status, 404, 'non-allowlisted nested path 404: ' + probe);
    }
    pass(`Production view: one queue card, 8 figures (1 approved-static, 7 unapproved, all nonruntime/unaccepted), ${committed} GitHub sync badges (3 a87ac16 + 3 15d153b + 2 53a912f, 0 staged, 0 local-only), 8 images served byte-identical, 5 concepts as text only, 4 nested/traversal probes 404`);
  } finally { child.kill(); }

  const after = [biblePath, progressPath, inventoryPath].map(file => sha256(fs.readFileSync(rel(file))));
  assert.deepEqual(after, before);
  pass('read-only: Game Bible, progress and inventory hashes unchanged');
  console.log('RESULT PASS (6 checks)');
})().catch(error => { console.error('FAIL ' + (error.stack || error.message)); process.exit(1); });
