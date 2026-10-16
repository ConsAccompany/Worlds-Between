// Focused check for the MVP completion meter and its closeout CLI.
// 1. The real progress state carries a consistent meter: exactly 35.0% from 5/5, 9/12, 3/4, 0/52, 0/11 and 0/2 at fixed weights.
// 2. A zero-change task writes a receipt with no increment; claiming an unchanged gate is refused and writes nothing.
// 3. Real gate changes move the count only when claimed with evidence; unclaimed changes are refused.
// 4. Visual counters never rise from unbacked counters, concept/unapproved/smoke evidence or pre-art playtests.
// 5. Unknown categories, gates, statuses and drifted gate sets are rejected.
// Mutating cases run the CLI against copies in the system temp folder; the tracked state file is hash-checked unchanged.
// Run from the repository root: node tests/mvp-completion-meter/<this file>
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');

const root = path.resolve(__dirname, '..', '..');
const cliPath = path.join(root, 'tools', 'rpg-2-star-ocean-the-second_mvp-completion-meter_recompute-and-task-closeout-cli_v01_20261015-233032-d296a2cb.js');
const cli = require(cliPath);
const statePath = path.join(root, cli.STATE_REL);
const sha = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const readJson = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const pass = label => console.log('PASS ' + label);
const realHash = sha(statePath);
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'wb-meter-'));
let copies = 0;
const evidenceQa = 'docs/qa/rpg-2-star-ocean-the-second_us-science-sphere_runtime-migration_qa-note_m2-v02_20261015-175011-364131c8.md';

function copy(mutate) {
  const file = path.join(tmp, 'state-' + (++copies) + '.json');
  const state = readJson(statePath);
  if (mutate) mutate(state);
  fs.writeFileSync(file, JSON.stringify(state, null, 2) + '\n');
  return file;
}
function run(file, ...args) {
  const result = spawnSync(process.execPath, [cliPath, ...args, '--state', file, '--now', '2026-10-16T09:00:00Z'], {cwd: root, encoding: 'utf8'});
  return {status: result.status, out: result.stdout + result.stderr};
}
const meterOf = file => readJson(file).completionMeter;
const cat = (meter, id) => meter.categories.find(c => c.id === id);
function refused(file, pattern, ...args) {
  const before = sha(file);
  const result = run(file, ...args);
  assert.equal(result.status, 1, 'expected refusal: ' + args.join(' ') + '\n' + result.out);
  assert.match(result.out, pattern);
  assert.equal(sha(file), before, 'a refused command must not write');
}

try {
  // 1. Initial 35% on the real state.
  const state = readJson(statePath);
  const meter = state.completionMeter;
  assert.ok(meter, 'completionMeter present');
  assert.equal(meter.kind, 'weighted_delivery_estimate');
  assert.equal(meter.percent, 35);
  assert.equal(meter.percentLabel, '35.0%');
  assert.equal(meter.weightTotal, 100);
  const expected = {
    'core-gameplay': [20, 5, 5, 20], 'global-world-travel': [10, 9, 12, 7.5], 'science-playable-content': [10, 3, 4, 7.5],
    'character-art': [25, 0, 52, 0], 'science-environment-art': [20, 0, 11, 0], 'final-integrated-validation': [15, 0, 2, 0],
  };
  assert.deepEqual(meter.categories.map(c => c.id), Object.keys(expected));
  for (const c of meter.categories) {
    const [weight, numerator, denominator, points] = expected[c.id];
    assert.deepEqual([c.weight, c.numerator, c.denominator, c.weightedPoints], [weight, numerator, denominator, points], c.id);
    assert.ok(c.zh && c.en && c.nextGate.zh && c.nextGate.en && c.source.rule.zh && c.source.rule.en, c.id + ' bilingual');
    assert.ok(Array.isArray(c.evidence) && c.evidence.length > 0, c.id + ' evidence');
  }
  assert.deepEqual(cat(meter, 'global-world-travel').openGateIds, ['route-data', 'map-art', 'visual-review']);
  assert.deepEqual(cat(meter, 'science-playable-content').openGateIds, ['human-timed-pacing']);
  assert.equal(meter.formalApproval.mvpFormallyAccepted, false);
  assert.deepEqual([meter.formalApproval.runtimeSpritesAccepted, meter.formalApproval.sceneVisualsAccepted, meter.formalApproval.humanPlaytests], ['0/52', '0/11', '0/2']);
  assert.ok(meter.formalApproval.scopedApprovalsNotCountedAsAcceptance.some(item => item.id === 'female-v8-south-idle-static' && item.status === 'approved'), 'scoped static approval listed as not counted');
  assert.equal(meter.lastUpdated.closeoutId, meter.taskCloseouts.at(-1).id);
  const check = cli.validate(state, meter);
  assert.deepEqual(check.errors, []);
  assert.deepEqual(cli.snapshotDiff(meter, cli.compute(state, meter)), [], 'stored meter matches recomputation');
  const real = run(statePath, 'check');
  assert.equal(real.status, 0, real.out);
  assert.match(real.out, /CHECK OK 35\.0%/);
  pass('real state: 35.0% = 20 + 7.5 + 7.5 + 0 + 0 + 0 from 5/5, 9/12, 3/4, 0/52, 0/11, 0/2; bilingual categories with evidence and next gate; formal approval false and separate; CLI check OK');

  // 2. Zero-change task receipt and claimed-but-unchanged refusal.
  const zero = copy();
  const zeroBefore = meterOf(zero);
  const r0 = run(zero, 'record', '--title-en', 'Docs-only tidy', '--title-zh', '仅整理文档');
  assert.equal(r0.status, 0, r0.out);
  const zeroAfter = meterOf(zero);
  const receipt = zeroAfter.taskCloseouts.at(-1);
  assert.equal(zeroAfter.taskCloseouts.length, zeroBefore.taskCloseouts.length + 1);
  assert.equal(receipt.kind, 'task');
  assert.deepEqual(receipt.title, {zh: '仅整理文档', en: 'Docs-only tidy'});
  assert.deepEqual(receipt.impact, {changed: false, percentBefore: 35, percentAfter: 35, deltaPoints: 0, gateChanges: [], categoryChanges: []});
  assert.equal(zeroAfter.percent, 35);
  assert.deepEqual(zeroAfter.categories, zeroBefore.categories);
  assert.equal(zeroAfter.lastUpdated.closeoutId, receipt.id);
  assert.equal(run(zero, 'check').status, 0);
  refused(zero, /did not change in the authoritative state/, 'record', '--title-en', 'Map art pass', '--gate', 'global-world-travel/map-art', '--evidence', evidenceQa);
  refused(zero, /did not change in the authoritative state/, 'record', '--title-en', 'Concept sheet', '--gate', 'character-art', '--evidence', evidenceQa);
  refused(zero, /needs --title/, 'record');
  pass('zero-change task: receipt appended with changed=false, 35 -> 35, delta 0, categories untouched; claims for unchanged gates and untitled records are refused without writing');

  // 3. Count changes: claimed and evidenced gate changes move the count; unclaimed or unevidenced ones are refused.
  const travel = copy(s => { s.m2Expansion.gates.find(g => g.id === 'route-data').status = 'implemented'; });
  assert.equal(run(travel, 'check').status, 1, 'stale meter detected after an authoritative change');
  refused(travel, /changed without a claim.*global-world-travel\/route-data/, 'record', '--title-en', 'Verify routes', '--evidence', evidenceQa);
  refused(travel, /needs at least one --evidence/, 'record', '--title-en', 'Verify routes', '--gate', 'global-world-travel/route-data');
  const r1 = run(travel, 'record', '--title-en', 'Verify routes', '--gate', 'global-world-travel/route-data', '--evidence', evidenceQa);
  assert.equal(r1.status, 0, r1.out);
  let m = meterOf(travel);
  assert.equal(cat(m, 'global-world-travel').ratio, '10/12');
  assert.equal(m.percent, 35.8);
  assert.equal(m.percentLabel, '35.8%');
  let last = m.taskCloseouts.at(-1);
  assert.equal(last.impact.changed, true);
  assert.equal(last.impact.deltaPoints, 0.83);
  assert.deepEqual(last.impact.gateChanges, [{key: 'global-world-travel/route-data', category: 'global-world-travel', gate: 'route-data', from: 'not_counted', to: 'counted'}]);
  assert.deepEqual(last.impact.categoryChanges.map(c => [c.id, c.before, c.after]), [['global-world-travel', '9/12', '10/12']]);
  assert.equal(run(travel, 'check').status, 0);
  refused(travel, /changed the authoritative state|did not change/, 'record', '--title-en', 'Repeat', '--gate', 'global-world-travel/route-data', '--evidence', evidenceQa);
  // Science gate stored in the meter, set through the CLI with evidence.
  refused(travel, /done without evidence/, 'record', '--title-en', 'Timed run', '--set-gate', 'science-playable-content/human-timed-pacing=done', '--gate', 'science-playable-content/human-timed-pacing');
  const r2 = run(travel, 'record', '--title-en', 'Timed run', '--set-gate', 'science-playable-content/human-timed-pacing=done', '--gate', 'science-playable-content/human-timed-pacing', '--evidence', 'game/tests/m7_smoke.gd');
  assert.equal(r2.status, 0, r2.out);
  m = meterOf(travel);
  assert.equal(cat(m, 'science-playable-content').ratio, '4/4');
  assert.equal(m.percent, 38.3);
  // A regression is recorded as a negative change when claimed.
  const back = copy(s => { s.steps.find(x => x.id === 'M4').status = 'in_progress'; });
  const r3 = run(back, 'record', '--title-en', 'Reopen M4', '--gate', 'core-gameplay/M4', '--evidence', 'game/tests/m4_smoke.gd');
  assert.equal(r3.status, 0, r3.out);
  m = meterOf(back);
  assert.equal(cat(m, 'core-gameplay').ratio, '4/5');
  assert.equal(m.percent, 31);
  assert.equal(m.taskCloseouts.at(-1).impact.deltaPoints, -4);
  pass('count changes: route-data 9/12 -> 10/12 gives 35.8% (+0.83) only when claimed with evidence; pacing gate done via CLI gives 4/4 and 38.3%; reopening M4 gives 4/5 and 31.0% (-4); unclaimed, unevidenced and repeated claims are refused');

  // 4. Visual and playtest counters need accepted, non-concept ledger backing; post-art playtests wait for art.
  const accepted = (id, kind, evidence, extra = {}) => ({id, status: 'accepted', acceptanceKind: kind, zh: id, en: id, scope: 'test', evidence, ...extra});
  const unbacked = copy(s => { s.approvalLedger.counters.runtimeSpritesAccepted = 1; });
  const staleMirror = run(unbacked, 'check');
  assert.equal(staleMirror.status, 1, 'raw counter mirror in formalApproval goes stale');
  assert.match(staleMirror.out, /formalApproval differs/);
  assert.doesNotMatch(staleMirror.out, /character-art\.numerator/, 'the unbacked counter does not change the count');
  assert.equal(cli.compute(readJson(unbacked), meterOf(unbacked)).categories.find(c => c.id === 'character-art').numerator, 0);
  refused(unbacked, /did not change in the authoritative state/, 'record', '--title-en', 'Bump counter', '--gate', 'character-art', '--evidence', evidenceQa);
  const r5 = run(unbacked, 'record', '--title-en', 'Counter edited without ledger item');
  assert.equal(r5.status, 0, r5.out);
  m = meterOf(unbacked);
  last = m.taskCloseouts.at(-1);
  assert.equal(last.impact.changed, false);
  assert.equal(m.percent, 35);
  assert.equal(cat(m, 'character-art').ratio, '0/52');
  assert.equal(m.formalApproval.runtimeSpritesAccepted, '1/52');
  assert.ok(last.warnings.some(w => /only 0 accepted runtime-sprite unit/.test(w)), 'receipt carries the unbacked-counter warning');
  const conceptOnly = copy(s => {
    s.approvalLedger.counters.runtimeSpritesAccepted = 1;
    s.approvalLedger.items.push(accepted('concept-sheet', 'runtime-sprite', ['outputs/rpg-2-star-ocean-the-second_scifi-city_liang-xu-male-female-south-scale-review_m8-concept_20261014-153644-9226ceab.png']));
  });
  assert.equal(cli.compute(readJson(conceptOnly), meterOf(conceptOnly)).categories.find(c => c.id === 'character-art').numerator, 0, 'concept evidence never counts');
  const backed = copy(s => {
    s.approvalLedger.counters.runtimeSpritesAccepted = 1;
    s.approvalLedger.items.push(accepted('sprite-set-one', 'runtime-sprite', [evidenceQa]));
  });
  refused(backed, /cannot back an acceptance count/, 'record', '--title-en', 'Sprite accepted', '--gate', 'character-art', '--evidence', 'game/tests/m7_smoke.gd');
  const r4 = run(backed, 'record', '--title-en', 'Sprite accepted', '--gate', 'character-art', '--evidence', evidenceQa);
  assert.equal(r4.status, 0, r4.out);
  m = meterOf(backed);
  assert.equal(cat(m, 'character-art').ratio, '1/52');
  assert.equal(m.percent, 35.5);
  assert.equal(m.taskCloseouts.at(-1).impact.deltaPoints, 0.48);
  const preArt = copy(s => {
    s.approvalLedger.counters.humanPlaytests = 1;
    s.approvalLedger.items.push(accepted('playtest-one', 'post-art-playtest', [evidenceQa]));
  });
  const preArtComputed = cli.compute(readJson(preArt), meterOf(preArt));
  assert.equal(preArtComputed.categories.find(c => c.id === 'final-integrated-validation').numerator, 0);
  assert.ok(preArtComputed.warnings.some(w => /held back/.test(w)));
  pass('visual counters: an unbacked counter, concept-evidence acceptance and pre-art playtests count 0; an accepted runtime-sprite item counts 1/52 (+0.48, 35.5%); smoke-test evidence cannot back it');

  // 5. Unknown and invalid gates.
  const plain = copy();
  refused(plain, /unknown category/, 'record', '--title-en', 'x', '--gate', 'bogus-category', '--evidence', evidenceQa);
  refused(plain, /unknown gate nonexistent in global-world-travel/, 'record', '--title-en', 'x', '--gate', 'global-world-travel/nonexistent', '--evidence', evidenceQa);
  refused(plain, /name the gate/, 'record', '--title-en', 'x', '--gate', 'global-world-travel', '--evidence', evidenceQa);
  refused(plain, /ledger counter/, 'record', '--title-en', 'x', '--gate', 'character-art/some-gate', '--evidence', evidenceQa);
  refused(plain, /derived from m2Expansion\.gates/, 'record', '--title-en', 'x', '--set-gate', 'global-world-travel/route-data=implemented', '--gate', 'global-world-travel/route-data', '--evidence', evidenceQa);
  refused(plain, /unknown status finished/, 'record', '--title-en', 'x', '--set-gate', 'science-playable-content/human-timed-pacing=finished');
  refused(plain, /unknown gate extra-gate in science-playable-content/, 'record', '--title-en', 'x', '--set-gate', 'science-playable-content/extra-gate=done');
  refused(plain, /evidence file not found/, 'record', '--title-en', 'x', '--evidence', 'docs/qa/does-not-exist.md');
  const drift = [
    [s => s.m2Expansion.gates.push({id: 'new-gate', zh: 'x', en: 'x', status: 'implemented', evidence: []}), /unknown m2Expansion gate new-gate/],
    [s => { s.m2Expansion.gates = s.m2Expansion.gates.filter(g => g.id !== 'map-art'); }, /missing m2Expansion gate map-art/],
    [s => { s.m2Expansion.gates.find(g => g.id === 'map-art').status = 'mostly_done'; }, /unknown status "mostly_done" on m2Expansion gate map-art/],
    [s => { s.steps.find(x => x.id === 'M3').status = 'complete'; }, /unknown status "complete" on step M3/],
    [s => { s.approvalLedger.counters.sceneVisualsTarget = 12; }, /fixed baseline denominator is 11/],
    [s => { s.steps.find(x => x.id === 'M7').status = 'done'; }, /M7 is done but science-playable-content gates are not all done/],
    [s => { s.approvalLedger.items.push(accepted('odd', 'mood-board', [evidenceQa])); }, /unknown acceptanceKind "mood-board"/],
  ];
  for (const [mutate, pattern] of drift) {
    const file = copy(mutate);
    refused(file, pattern, 'check');
    refused(file, pattern, 'record', '--title-en', 'x');
  }
  pass('invalid input: unknown category, unknown or unnamed gate, gate on a counter, --set-gate on a derived category, unknown status, missing evidence file, added/missing/unknown-status M2 gates, unknown step status, changed denominator, M7 done with open gates and unknown acceptance kind are all refused without writing');

  assert.equal(sha(statePath), realHash, 'tracked progress state unchanged');
  pass('read-only: tracked progress state hash unchanged');
  console.log('RESULT PASS (6 checks)');
} finally {
  fs.rmSync(tmp, {recursive: true, force: true});
}
