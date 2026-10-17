// Focused check for the Game Bible cross-device visual review queue (environmentVisualReview.crossDeviceReviewQueue) and the
// Chicago Loop scene-denominator review. Badges must follow the recorded approval flags, every queue image must be an actual
// Godot capture served byte-identical (two live in run subdirectories), generated concepts must never render as images, the
// sync state must match Git, and no counter or the 35.8% meter may move.
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

  // 1. Six actual Godot captures, in order, each with its own QA note; badges follow the recorded flags.
  assert.ok(queue && Array.isArray(queue.items), 'queue present');
  assert.deepEqual(queue.items.map(item => item.order), [1, 2, 3, 4, 5, 6]);
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
  pass('queue: 6 actual Godot captures in order, QA notes on disk, only #1 (selout v8 still) creator-approved, all nonruntime and unaccepted');

  // 2. Sync state matches Git: committed items are tracked with the recorded blob; staged items are in the index with the recorded
  // blob and never claim a commit; local-only items are untracked and hash-pinned. Every present file matches its recorded sha256.
  const staged = queue.items.filter(item => item.syncState === 'staged-not-pushed');
  for (const item of queue.items) {
    if (present(item)) assert.equal(sha256(fs.readFileSync(rel(item.file))), item.sha256, 'recorded sha256 matches the file: ' + item.order);
    if (item.syncState === 'staged-not-pushed') {
      assert.ok(tracked(item.file), 'staged item is in the Git index: ' + item.file);
      assert.equal(git('ls-files', '-s', '--', item.file).stdout.trim().split(/\s+/)[1], item.gitBlob, 'index blob matches: ' + item.order);
      if (present(item)) assert.equal(git('hash-object', '--', item.file).stdout.trim(), item.gitBlob, 'file blob matches: ' + item.order);
      assert.match(item.file, /unapproved/, 'staged capture is labelled unapproved in its name: ' + item.order);
      const index = JSON.stringify(JSON.parse(fs.readFileSync(rel(item.hashPinnedIn), 'utf8')));
      assert.ok(index.includes(item.sha256), 'staged item sha256 pinned in its evidence index: ' + item.order);
    } else if (item.syncState === 'local-only') {
      assert.equal(tracked(item.file), false, 'local-only item is untracked: ' + item.file);
      const index = JSON.stringify(JSON.parse(fs.readFileSync(rel(item.hashPinnedIn), 'utf8')));
      assert.ok(index.includes(path.posix.basename(item.file)), 'local-only item named in its evidence index: ' + item.order);
      if (present(item)) assert.ok(index.includes(sha256(fs.readFileSync(rel(item.file)))), 'local-only item sha256 pinned in its evidence index: ' + item.order);
    } else {
      assert.match(item.syncState, /^committed-at-[0-9a-f]{7}$/);
      assert.ok(tracked(item.file), 'committed item is tracked: ' + item.file);
      assert.equal(git('hash-object', item.file).stdout.trim(), item.gitBlob, 'blob matches: ' + item.order);
      assert.equal(git('cat-file', '-e', item.syncState.slice('committed-at-'.length) + ':' + item.file).status, 0, 'present at the recorded commit: ' + item.order);
    }
  }
  assert.deepEqual(staged.map(item => item.order), queue.gitProposal.items, 'staged items are exactly the Git proposal');
  assert.ok(fs.existsSync(rel(queue.gitProposal.qa)), 'Git proposal QA note exists');
  assert.ok(/staged-not-pushed/.test(queue.siteRendering) && !/local-only/.test(queue.siteRendering), 'Site note names the staged items, not a stale local-only state');
  const committed = queue.items.filter(item => /^committed-at-/.test(item.syncState)).length;
  pass(`sync state: ${committed} committed items match their recorded blob at the recorded commit; ${staged.length} staged-not-pushed items (#${staged.map(i => i.order).join(', #')}) in the index with the recorded blob and sha256 pinned in the evidence index`);

  // 3. Generated concepts are a separate, gallery-ineligible list and never appear among queue items or Site previews.
  const concepts = queue.nonruntimeConcepts;
  assert.equal(concepts.galleryEligible, false);
  assert.equal(concepts.items.length, 5);
  assert.ok(concepts.items.every(c => ['generated-concept', 'identity-reference'].includes(c.kind) && /^outputs\/[^/]+\.png$/.test(c.file)));
  const queueFiles = new Set(queue.items.map(item => item.file));
  const previewNames = (bible.characterVisualReview.previews || []).map(p => path.posix.basename(p.file));
  assert.ok(concepts.items.every(c => !queueFiles.has(c.file) && !previewNames.includes(path.posix.basename(c.file))), 'no concept in the queue or Site previews');
  pass('concepts: 5 nonruntime references, galleryEligible false, none in the queue or characterVisualReview.previews');

  // 4. Counters and meter unchanged; Chicago denominator proposal recorded but not applied, with the meter recomputed from the formula.
  const counters = progress.approvalLedger.counters;
  assert.deepEqual([counters.runtimeSpritesAccepted, counters.runtimeSpritesTarget, counters.sceneVisualsAccepted, counters.sceneVisualsTarget, counters.humanPlaytests, counters.humanPlaytestsTarget], [0, 52, 0, 12, 0, 2]);
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
  assert.match(meter.stdout, /CHECK OK 35\.8%/);
  const cats = Object.fromEntries(progress.completionMeter.categories.map(c => [c.id, c]));
  const points = denominatorForEnv => Object.values(cats).reduce((sum, c) => sum + c.weight * c.numerator / (c.id === 'science-environment-art' ? denominatorForEnv : c.denominator), 0);
  assert.equal(cats['science-environment-art'].numerator, 0);
  assert.equal(Math.round(points(11) * 10) / 10, 35.8);
  assert.equal(Math.round(points(12) * 10) / 10, 35.8, 'with 0 accepted scenes a 12th gate leaves the meter at 35.8%');
  assert.equal(progress.completionMeter.percent, 35.8);
  pass('counters 0/52 0/12 0/2; meter CLI CHECK OK 35.8%; Chicago gate 12 applied by a dated baseline-revision closeout; formula gives 35.8% for /11 and /12');

  // 5. Rendered Production view: one card, six figures with flag-derived badges, images served byte-identical, concepts as text only.
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
    assert.equal(figures.length, 6);
    assert.equal((card.match(/badge good">已批准静态基准 · 未接入运行时 · 未验收</g) || []).length, 1);
    assert.equal((card.match(/badge warn">未批准 · 未接入运行时 · 未验收</g) || []).length, 5);
    assert.equal((card.match(/仅本机 · 尚未同步到 GitHub/g) || []).length, queue.items.filter(item => item.syncState === 'local-only').length);
    assert.equal((card.match(/badge warn">已暂存为 Git 候选 · 尚未推送，其他设备不可见</g) || []).length, staged.length);
    assert.equal((card.match(/已在 GitHub（[0-9a-f]{7}）/g) || []).length, committed);
    assert.ok(!/已验收|通过验收/.test(card.replace(/未验收/g, '')), 'no acceptance claim');
    assert.ok(!/<button|<input|type="checkbox"/.test(card), 'no approval controls');
    const imgs = [...card.matchAll(/<img src="([^"]+)"/g)].map(m => m[1]);
    assert.equal(imgs.length, 6);
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
    pass(`Production view: one queue card, 6 figures (1 approved-static, 5 unapproved, all nonruntime/unaccepted), ${committed} GitHub + ${staged.length} staged-not-pushed sync badges, 6 images served byte-identical, 5 concepts as text only, 4 nested/traversal probes 404`);
  } finally { child.kill(); }

  const after = [biblePath, progressPath, inventoryPath].map(file => sha256(fs.readFileSync(rel(file))));
  assert.deepEqual(after, before);
  pass('read-only: Game Bible, progress and inventory hashes unchanged');
  console.log('RESULT PASS (6 checks)');
})().catch(error => { console.error('FAIL ' + (error.stack || error.message)); process.exit(1); });
