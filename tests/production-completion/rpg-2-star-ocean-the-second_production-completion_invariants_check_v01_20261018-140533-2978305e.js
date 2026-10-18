#!/usr/bin/env node
// Invariant checks for the production-completion task ledger and its one updater/checker CLI.
// Works on in-memory or temp copies; the tracked ledger and progress state must stay byte-identical (checked at the end).
// Run from the repository root: node tests/production-completion/<this file>
'use strict';
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const CLI_REL = 'tools/rpg-2-star-ocean-the-second_production-completion_ledger-cli_v01_20261018-140533-3b436630.js';
const cli = require(path.join(ROOT, CLI_REL));
const LEDGER = path.join(ROOT, cli.LEDGER_REL);
const PROGRESS = path.join(ROOT, cli.PROGRESS_REL);
const NOW = '2026-10-19T09:00:00Z';
const QA = name => 'docs/qa/rpg-2-star-ocean-the-second_' + name;
const sha = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const fresh = () => cli.load(LEDGER);
const task = (l, id) => l.tasks.find(x => x.id === id);
const prodSnap = l => JSON.stringify(l.computed.production);
const set = (l, id, status, extra = {}) => cli.setTask(l, ROOT, {task: id, status, evidence: [], now: NOW, ...extra});
let passed = 0;
const pass = msg => { passed += 1; console.log('PASS ' + msg); };
// Review invariants never depend on a real review still being todo: an existing non-waived visual review is reopened in a
// temporary in-memory copy only (real verdicts are never touched) and the copy's meters are recomputed as its baseline.
const reopenVisualReview = l => {
  for (const x of l.tasks.filter(t => t.stage === 'visual-review' && t.status !== 'not_required')) {
    const copy = structuredClone(l), y = task(copy, x.id);
    Object.assign(y, {status: 'todo', evidence: []}); delete y.outcome;
    if (!cli.validate(copy, ROOT).length) return {l: cli.refresh(copy, ROOT), id: x.id};
  }
  assert.fail('no non-waived visual review can be reopened in a temporary copy');
};
// A review verdict (even changes_requested) moves only the inspection meter.
const checkReviewMovesInspectionOnly = base => {
  const {l, id} = reopenVisualReview(base), prod = prodSnap(l), insp = l.computed.inspection.done;
  set(l, id, 'done', {outcome: 'changes_requested', evidence: [QA('nyc-city-hall-park_v06-cross-device-review-packet_unapproved-v01_20261017-174208-fe6b9f9d.md')]});
  assert.equal(prodSnap(l), prod);
  assert.equal(l.computed.inspection.done, insp + task(l, id).points);
};
// Status and notes stay mutable while the frozen task-definition hash is unchanged.
const checkStatusMutableHashFrozen = base => {
  const {l, id} = reopenVisualReview(base), hash = cli.taskSetHash(l.tasks);
  Object.assign(task(l, id), {status: 'in_progress', note: {zh: 'x', en: 'y'}});
  assert.deepEqual(cli.validate(l, ROOT), [], 'status and notes stay mutable');
  assert.equal(cli.taskSetHash(l.tasks), hash, 'task-definition hash unchanged by status/note edits');
};

const before = [LEDGER, PROGRESS].map(sha);

// 1. Tracked ledger validates; recompute is byte-identical and idempotent; CLI check exits 0.
{
  assert.deepEqual(cli.validate(fresh(), ROOT), []);
  const once = cli.serialize(cli.refresh(fresh(), ROOT));
  assert.equal(once, cli.serialize(cli.refresh(cli.refresh(fresh(), ROOT), ROOT)));
  assert.equal(once, fs.readFileSync(LEDGER, 'utf8').replace(/\r\n/g, '\n'));
  const out = spawnSync(process.execPath, [CLI_REL, 'check'], {cwd: ROOT, encoding: 'utf8'});
  assert.equal(out.status, 0, out.stdout + out.stderr);
  pass('tracked ledger validates; recompute is idempotent and byte-identical; CLI check exits 0');
}

// 2. One derivation, rounded once, from points (task counts are reported separately).
{
  const l = fresh(), pts = (st, done) => l.tasks.filter(x => x.stage === st && (!done || x.status === 'done')).reduce((s, x) => s + x.points, 0);
  const expected = Math.round(10 * (40 * pts('coding', true) / pts('coding') + 60 * pts('content', true) / pts('content'))) / 10;
  assert.equal(l.computed.production.percent, expected);
  assert.equal(l.computed.production.content.tasks, l.tasks.filter(x => x.stage === 'content').length);
  assert.notEqual(l.computed.production.content.tasks, l.computed.production.content.total, 'points and task counts are different numbers');
  pass(`production ${expected}% = round1(40 x ${pts('coding', true)}/${pts('coding')} + 60 x ${pts('content', true)}/${pts('content')}) points; task counts separate`);
}

// 3. Delivered movement keeps its credit; later directions may progress only with native QA evidence.
{
  const l = fresh(), walk = task(l, 'content.char.protagonist-female.walk-south'), bucket = task(l, 'content.char.protagonist-female.walk-south.revision');
  assert.equal(walk.status, 'done');
  assert.ok(walk.evidence.some(e => /south-run-v07/.test(e)) && walk.evidence.includes(cli.PROGRESS_REL));
  assert.ok(bucket && bucket.status === 'done' && bucket.points === 2 && bucket.owner === walk.owner && bucket.evidence.some(e => /v10r1/.test(e)), 'run/stop polish revision produced (v10r1)');
  for (const d of ['west', 'north', 'east']) {
    const direction = task(l, `content.char.protagonist-female.walk-${d}`);
    assert.ok(['todo', 'in_progress', 'blocked', 'done'].includes(direction.status));
    if (direction.status === 'done') assert.ok(direction.evidence.some(e => e.startsWith('docs/qa/')) && direction.evidence.every(e => !/32x48|m8-prototype/.test(e)), d + ' production needs native QA, not rejected placeholder evidence');
  }
  assert.equal(l.tasks.filter(x => /^creator\.char\..*\.accept-runtime-sprite$/.test(x.id) && x.status === 'done').length, 0, 'runtime sprite acceptance stays 0/52');
  pass('v07 south run credited as delivered; v10r1 run/stop polish credited as its one produced revision; other direction states follow actual native production; 0/52 sprite acceptances');
}

// 4. A pending or changes-requested review never changes production credit.
{
  checkReviewMovesInspectionOnly(fresh());
  pass('review done (even changes_requested) moves only the inspection meter');
}

// 4b. Regression: the review invariants hold even when every real non-waived visual review is finished.
{
  const all = fresh();
  for (const x of all.tasks.filter(t => t.stage === 'visual-review' && t.status !== 'not_required')) Object.assign(x, {status: 'done', outcome: x.outcome || 'passed', evidence: x.evidence.length ? x.evidence : [cli.PROGRESS_REL], statusAt: x.statusAt || NOW});
  cli.refresh(all, ROOT);
  assert.equal(all.tasks.filter(x => x.stage === 'visual-review' && x.status === 'todo').length, 0);
  assert.deepEqual(cli.validate(all, ROOT), []);
  checkReviewMovesInspectionOnly(all);
  checkStatusMutableHashFrozen(all);
  pass('review invariants need no real todo visual review (all-finished temporary copy)');
}

// 5. Waivers are not work: excluded from the inspection numerator and denominator; approval/waiver toggles leave production alone.
{
  const l = fresh(), c = l.computed;
  const waived = l.tasks.filter(x => x.status === 'not_required');
  assert.equal(c.inspection.waived.tasks, waived.length);
  const performed = l.tasks.filter(x => ['technical-inspection', 'visual-review', 'content-qa'].includes(x.stage) && x.status === 'done').reduce((s, x) => s + x.points, 0);
  const active = l.tasks.filter(x => ['technical-inspection', 'visual-review', 'content-qa'].includes(x.stage) && x.status !== 'not_required').reduce((s, x) => s + x.points, 0);
  assert.equal(c.inspection.done, performed);
  assert.equal(c.inspection.total, active);
  const prod = prodSnap(l), insp = {...c.inspection};
  set(l, 'creator.scene.city-survey-outer.accept', 'todo');
  assert.equal(task(l, 'review.scene.city-survey-outer').status, 'todo', 'withdrawn approval reopens the waived review');
  assert.equal(l.computed.inspection.done, insp.done, 'reopening a waiver adds no performed work');
  assert.equal(l.computed.inspection.total, insp.total + 1, 'the reopened review now counts in the denominator');
  assert.equal(prodSnap(l), prod);
  set(l, 'creator.scene.city.accept', 'done', {evidence: [QA('nyc-city-hall-park_scene-candidate-640x360_qa-note_unapproved-v06_20261017-165253-4519dffe.md')]});
  assert.equal(prodSnap(l), prod);
  assert.deepEqual(cli.validate(l, ROOT), []);
  pass(`${waived.length} waived reviews excluded from inspection ${c.inspection.done}/${c.inspection.total}; approval and waiver toggles leave production identical`);
}

// 6. One fixed revision bucket per deliverable: no version farming.
{
  // Use a delivered scene without a revision for the first-bucket case; Chicago now has a completed bucket.
  const l = fresh(), before6 = l.computed.production, revs = l.baseline.revisions.length;
  assert.ok(!l.tasks.some(x => x.id === 'content.scene.ruins-survey-inner.native-pass.revision'));
  cli.revise(l, ROOT, {for: 'content.scene.ruins-survey-inner.native-pass', reasonEn: 'Codex asked for changes', now: NOW});
  const bucket = task(l, 'content.scene.ruins-survey-inner.native-pass.revision');
  assert.ok(bucket && bucket.points === 6 && bucket.status === 'in_progress');
  assert.equal(l.computed.production.content.done, before6.content.done, 'initial credit kept');
  assert.equal(l.computed.production.content.total, before6.content.total + 6);
  assert.equal(l.baseline.revisions.length, revs + 1);
  const count = l.tasks.length, total = l.computed.production.content.total;
  cli.revise(l, ROOT, {for: 'content.scene.ruins-survey-inner.native-pass', reasonEn: 'v06 candidate', now: NOW});
  cli.revise(l, ROOT, {for: 'content.scene.ruins-survey-inner.native-pass', reasonEn: 'v07 candidate', now: NOW});
  assert.equal(l.tasks.length, count, 'later versions add no task');
  assert.equal(l.computed.production.content.total, total, 'later versions add no points');
  assert.equal(l.baseline.revisions.length, revs + 1);
  assert.throws(() => cli.revise(l, ROOT, {for: 'content.scene.ruins-survey-inner.native-pass.revision', reasonEn: 'x', now: NOW}), /another revision/);
  assert.throws(() => cli.revise(l, ROOT, {for: 'review.scene.chicago-loop', reasonEn: 'x', now: NOW}), /production deliverable/);
  assert.deepEqual(cli.validate(l, ROOT), []);
  const second = fresh(); second.tasks.push({...task(second, 'content.scene.city.native-pass.revision'), id: 'content.scene.city.native-pass.revision2'});
  assert.ok(cli.validate(second, ROOT).some(e => /one fixed revision bucket|frozen baseline/.test(e)));
  const inflated = fresh(); task(inflated, 'content.scene.city.native-pass.revision').points = 12;
  assert.ok(cli.validate(inflated, ROOT).some(e => /ceil\(deliverable points \/ 2\)/.test(e)));
  // Reopening Chicago's existing completed bucket removes only its revision credit; the initial pass stays done.
  const completed = fresh(), current = task(completed, 'content.scene.chicago-loop.native-pass.revision');
  assert.equal(current.status, 'done');
  const before = completed.computed.production.content, beforeTasks = completed.tasks.length, beforeRevisions = completed.baseline.revisions.length;
  cli.revise(completed, ROOT, {for: 'content.scene.chicago-loop.native-pass', reasonEn: 'Another bounded revision requested', now: NOW});
  assert.equal(task(completed, 'content.scene.chicago-loop.native-pass').status, 'done');
  assert.equal(completed.computed.production.content.done, before.done - current.points);
  assert.equal(completed.computed.production.content.total, before.total);
  assert.equal(completed.tasks.length, beforeTasks);
  assert.equal(completed.baseline.revisions.length, beforeRevisions);
  assert.deepEqual(cli.validate(completed, ROOT), []);
  pass('first revision adds one fixed denominator bucket; completed revision reopens without removing initial credit or adding tasks/points; second buckets and re-pointing rejected');
}

// 7. Review reconciliation: a changes-requested verdict blocks "ready for acceptance" until a later revision is delivered.
{
  const l = fresh(), c = l.computed;
  for (const id of ['creator.scene.outskirts-survey-outer.accept', 'creator.scene.ruins.accept', 'creator.char.liang-xu.approve-static-south']) {
    assert.ok(c.queue.needsRevision.items.some(q => q.id === id), id + ' needs a revision');
    assert.ok(!c.queue.items.some(q => q.id === id), id + ' is not offered as ready');
  }
  const yonkers = task(l, 'review.scene.outskirts-survey-outer');
  assert.ok(yonkers.status === 'done' && yonkers.outcome === 'changes_requested' && yonkers.evidence.some(e => e.startsWith('docs/qa/') && /v0[67]/.test(e)));
  const ruins = task(l, 'review.scene.ruins');
  assert.ok(ruins.status === 'done' && ruins.outcome === 'changes_requested' && ruins.evidence.some(e => /v13/.test(e)));
  assert.equal(task(l, 'content.scene.ruins.native-pass.revision').status, 'done', 'v13 revision delivered and credited');
  const det = task(l, 'qa.scene.ruins.check');
  assert.ok(det.status === 'done' && det.outcome === 'passed' && det.evidence.some(e => /deterministic-check/.test(e)), 'WDC technical inspection done from the root-accepted deterministic 22/22 check');
  assert.equal(task(l, 'creator.scene.ruins.accept').status, 'todo', 'technical inspection is not art acceptance');
  assert.equal(task(l, 'content.scene.ruins.native-default').status, 'todo', 'v13 is opt-in, not default');
  const prod = prodSnap(l);
  cli.revise(l, ROOT, {for: 'content.scene.outskirts-survey-outer.native-pass', reasonEn: 'answer root v06 notes', now: NOW});
  assert.ok(l.computed.queue.needsRevision.items.some(q => q.id === 'creator.scene.outskirts-survey-outer.accept'), 'still gated while the revision is in progress');
  set(l, 'content.scene.outskirts-survey-outer.native-pass.revision', 'done', {evidence: [QA('yonkers-antenna-corridor-room1_v06-outdoor-readability-refinement_qa-note_unapproved-v06_20261018-084726-c8f0d900.md')]});
  const reopened = task(l, 'review.scene.outskirts-survey-outer');
  assert.ok(reopened.status === 'todo' && reopened.history.at(-1).outcome === 'changes_requested', 'the answered review reopens and keeps its history');
  assert.ok(l.computed.queue.items.some(q => q.id === 'creator.scene.outskirts-survey-outer.accept'), 'acceptance is ready again after the revision');
  assert.equal(task(l, 'creator.scene.outskirts-survey-outer.accept').status, 'todo', 'no approval auto-completion');
  assert.equal(task(l, 'content.scene.outskirts-survey-outer.native-pass').status, 'done');
  assert.ok(JSON.parse(prodSnap(l)).content.done >= JSON.parse(prod).content.done, 'produced credit retained');
  pass('Current Yonkers and WDC root verdicts recorded as changes_requested; their acceptances show a revision requirement until a later revision; WDC deterministic check credited as technical inspection only');
}

// 8. Baseline owners follow the task type; transfers require their own audited reassign command below.
{
  const l = fresh();
  for (const x of l.tasks) if (x.type !== 'revision') {
    assert.equal(x.stage, cli.TASK_TYPES[x.type].stage, x.id);
    const lastAssignment = l.baseline.revisions.filter(r => r.kind === 'owner-assignment' && r.taskId === x.id).at(-1);
    assert.equal(x.owner, lastAssignment ? lastAssignment.toOwner : cli.TASK_TYPES[x.type].owner, x.id);
  }
  const portraits = l.tasks.filter(x => /^content\.char\..*\.portrait$/.test(x.id));
  assert.equal(portraits.length, 52); assert.ok(portraits.every(x => x.type === 'concept-generation' && x.stage === 'content'));
  assert.ok(l.tasks.filter(x => x.type === 'native-pixel').every(x => ['codex', 'claude'].includes(x.owner)));
  const audio = task(l, 'review.content.audio');
  assert.ok(audio.stage === 'content-qa' && audio.owner === 'codex' && /audio QA/.test(audio.title.en) && !/visual review/i.test(audio.title.en));
  const ops = l.tasks.filter(x => x.stage === 'operations');
  assert.ok(ops.length === 2 && ops.every(x => x.owner === 'codex'));
  assert.equal(l.computed.byOwner.codex.operationsTasks, 2, 'owner list includes remaining Codex operations work');
  const opsPoints = ops.reduce((s, x) => s + x.points, 0);
  const totalPoints = ['coding', 'content', 'technical-inspection', 'visual-review', 'content-qa', 'creator-approval'].reduce((s, st) => s + l.computed.stageTotals[st].total + l.computed.stageTotals[st].waivedPoints, 0);
  assert.equal(totalPoints + opsPoints, l.tasks.reduce((s, x) => s + x.points, 0), 'operations are outside every meter');
  const wrong = fresh(), p = task(wrong, 'content.char.milo.portrait'); p.owner = p.owner === 'codex' ? 'claude' : 'codex';
  assert.ok(cli.validate(wrong, ROOT).some(e => /audited reassign|hash chain|frozen baseline/.test(e)));
  const wrong2 = fresh(), n = task(wrong2, 'content.char.milo.static-south'); n.owner = n.owner === 'codex' ? 'claude' : 'codex';
  assert.ok(cli.validate(wrong2, ROOT).some(e => /audited reassign|hash chain|frozen baseline/.test(e)));
  pass('owners follow type defaults or their audited transfers; 52 image-generation portraits, fixed content/audio QA and 2 operations tasks outside meters');
}

// 8a. Ownership is operational: moving responsibility never changes delivered work, denominators or creator approval.
const assign = (l, id, owner, extra = {}) => cli.reassign(l, ROOT, {task: id, owner, reasonEn: 'Creator-authorized Codex takeover during Claude quota gap', now: NOW, ...extra});
const scoreSnap = l => JSON.stringify({production: l.computed.production, inspection: l.computed.inspection, approval: l.computed.approval,
  operations: l.computed.operations, release: l.computed.release, stageTotals: l.computed.stageTotals, legacy: l.computed.legacy, weights: l.baseline.weights});
const tasksExceptOwners = l => JSON.stringify(l.tasks.map(({owner, ...rest}) => rest));
{
  const l = fresh(), score = scoreSnap(l), unchanged = tasksExceptOwners(l), count = l.tasks.length;
  const baseRevisions = l.baseline.revisions.length, baseHash = cli.taskSetHash(l.tasks);
  const moved = ['code.runtime.character-sprite-pipeline', 'code.runtime.combat-sprite-pipeline', 'code.runtime.vfx-system', 'code.runtime.audio-cues', 'qa.scene.map.check'];
  const nextOwners = new Map(moved.map(id => [id, task(l, id).owner === 'codex' ? 'claude' : 'codex']));
  const movedPoints = moved.reduce((n, id) => n + (nextOwners.get(id) === 'codex' ? 1 : -1) * task(l, id).points, 0), codexPoints = l.computed.byOwner.codex.points;
  for (const id of moved) assign(l, id, nextOwners.get(id));
  assert.equal(l.tasks.length, count);
  assert.equal(tasksExceptOwners(l), unchanged, 'reassign preserves every task property other than owner (including status/evidence/statusAt)');
  assert.equal(scoreSnap(l), score, 'all scored numerators/denominators and release/approval states identical');
  assert.equal(l.baseline.revisions.length, baseRevisions + moved.length);
  assert.equal(l.baseline.revisions[baseRevisions].previousTaskSetSha256, baseHash);
  assert.equal(l.computed.byOwner.codex.points, codexPoints + movedPoints);
  for (const id of moved) assert.equal(task(l, id).owner, nextOwners.get(id));
  assert.deepEqual(cli.validate(l, ROOT), []);
  pass('audited producer/technical-check takeover moves owner workload only; every status, evidence, task count, score/denominator and approval remains unchanged');
}

// Revision ownership follows the parent, regardless of whether the revision is created before or after transfer.
{
  const l = fresh(), parent = 'content.scene.outskirts-survey-outer.native-pass', bucket = parent + '.revision';
  const score = scoreSnap(l), beforeTasks = tasksExceptOwners(l);
  const original = task(l, parent).owner, recipient = original === 'codex' ? 'claude' : 'codex';
  const beforeCounts = structuredClone(l.computed.byOwner);
  assign(l, parent, recipient);
  const record = l.baseline.revisions.at(-1);
  assert.deepEqual(record.changedTaskIds, [parent, bucket].sort());
  assert.equal(task(l, bucket).owner, recipient);
  const q = l.computed.queue.needsRevision.items.find(x => x.id === 'creator.scene.outskirts-survey-outer.accept');
  assert.equal(q.nextOwner, recipient, 'revision queue routes to its actual producer');
  assert.equal(l.computed.byOwner[recipient].revisionsBlockingApproval, beforeCounts[recipient].revisionsBlockingApproval + 1);
  assert.equal(l.computed.byOwner[original].revisionsBlockingApproval, beforeCounts[original].revisionsBlockingApproval - 1);
  const same = cli.serialize(l);
  assign(l, parent, recipient);
  assert.equal(cli.serialize(l), same, 'same-owner retry adds no audit entry or timestamp churn');
  assign(l, parent, original);
  assert.equal(task(l, bucket).owner, original);
  assert.equal(tasksExceptOwners(l), beforeTasks);
  assert.equal(scoreSnap(l), score);
  assert.equal(cli.taskSetHash(l.tasks), cli.taskSetHash(fresh().tasks), 'reverse transfer restores original definitions');
  assert.deepEqual(cli.validate(l, ROOT), []);
  // No bucket yet: missing-revision routing follows the parent, then the newly created bucket inherits Codex.
  const n = fresh(), newScene = 'content.scene.ruins-survey-inner.native-pass';
  assert.ok(!task(n, newScene + '.revision'));
  set(n, 'review.scene.ruins-survey-inner', 'done', {outcome: 'changes_requested', evidence: [QA('nyc-city-hall-park_v06-cross-device-review-packet_unapproved-v01_20261017-174208-fe6b9f9d.md')]});
  assign(n, newScene, 'codex');
  assert.equal(n.computed.queue.needsRevision.items.find(x => x.id === 'creator.scene.ruins-survey-inner.accept').nextOwner, 'codex');
  cli.revise(n, ROOT, {for: newScene, reasonEn: 'bounded material pass', now: NOW});
  assert.equal(task(n, newScene + '.revision').owner, 'codex');
  assign(n, newScene, 'claude');
  assign(n, newScene, 'codex');
  assert.deepEqual(cli.validate(n, ROOT), [], 'assignment/bucket/assignment chain fully replayable');
  pass('existing/new revision buckets follow producer transfers; missing/existing revision routing and per-owner counts are dynamic; retries idempotent and reverse/mixed chains valid');
}

// Reject unaudited transfers and forged records even if someone replaces the last result hash with their modified hash.
{
  const id = 'code.runtime.audio-cues';
  for (const [target, owner, extra] of [
    ['creator.scene.city.accept', 'codex', {}], ['review.scene.city', 'claude', {}], ['review.content.audio', 'claude', {}],
    ['ops.codex.site-publication', 'claude', {}], ['content.scene.city.native-pass.revision', 'codex', {}],
    [id, 'creator', {}], [id, 'codex', {reasonEn: ' '}], [id, 'codex', {now: 'not-a-time'}], ['code.missing', 'codex', {}]
  ]) {
    const l = fresh(), before = cli.serialize(l);
    assert.throws(() => assign(l, target, owner, extra));
    assert.equal(cli.serialize(l), before, 'refused assignment is atomic: ' + target);
  }
  const direct = fresh(); task(direct, id).owner = task(direct, id).owner === 'codex' ? 'claude' : 'codex';
  assert.ok(cli.validate(direct, ROOT).some(e => /audited reassign|frozen baseline/.test(e)));
  const valid = fresh(); assign(valid, 'content.scene.city.native-pass', 'codex');
  const mutate = fn => { const x = structuredClone(valid); fn(x, x.baseline.revisions.at(-1)); assert.ok(cli.validate(x, ROOT).length, 'forged chain must fail'); };
  mutate((x, r) => { r.kind = 'unsupported-owner-override'; });
  mutate((x, r) => { r.fromOwner = 'creator'; });
  mutate((x, r) => { r.reason.en = ''; });
  mutate((x, r) => { delete r.previousTaskSetSha256; });
  mutate((x, r) => { r.changedTaskIds = [r.taskId]; });
  mutate((x, r) => { task(x, 'content.scene.city.native-pass.revision').owner = 'claude'; r.taskSetSha256 = cli.taskSetHash(x.tasks); });
  mutate((x, r) => { task(x, 'content.scene.city.plate').points += 1; r.taskSetSha256 = cli.taskSetHash(x.tasks); });
  mutate((x, r) => { task(x, r.taskId).doneCriterion.en = 'weakened'; r.taskSetSha256 = cli.taskSetHash(x.tasks); });
  mutate((x, r) => { r.previousTaskSetSha256 = r.taskSetSha256; });
  mutate((x, r) => { x.baseline.revisions = []; });
  const forgedReview = fresh(), review = task(forgedReview, 'review.scene.city'), reviewBefore = cli.taskSetHash(forgedReview.tasks);
  review.owner = 'claude';
  forgedReview.baseline.revisions.push({at: NOW, kind: 'owner-assignment', taskId: review.id, fromOwner: 'codex', toOwner: 'claude', changedTaskIds: [review.id], reason: {en: 'forged review reassignment'}, previousTaskSetSha256: reviewBefore, taskSetSha256: cli.taskSetHash(forgedReview.tasks)});
  assert.ok(cli.validate(forgedReview, ROOT).some(e => /producer or technical-check/.test(e)), 'a hash-consistent audit cannot reassign fixed review ownership');
  const dropped = fresh(), firstOwner = task(dropped, id).owner, otherOwner = firstOwner === 'codex' ? 'claude' : 'codex';
  assign(dropped, id, otherOwner); assign(dropped, id, firstOwner);
  dropped.baseline.revisions.splice(0, 1);
  assert.ok(cli.validate(dropped, ROOT).length, 'an intermediate audit may not be dropped even after reverse transfer');
  const bad = fresh(); task(bad, id).owner = task(bad, id).owner === 'codex' ? 'claude' : 'codex'; const badBefore = cli.serialize(bad);
  assert.throws(() => assign(bad, id, 'claude'), /invalid ledger/);
  assert.equal(cli.serialize(bad), badBefore, 'reassign cannot launder a preexisting unaudited owner edit');
  pass('creator/review/operations owners fixed; direct edits, malformed requests, forged hashes/records, score/criterion changes and omitted audit history rejected atomically');
}

// 8b. Coding measures normal runtime capability: no dependency on approval or default art adoption; criteria and dependencies are frozen.
{
  const l = fresh();
  for (const x of l.tasks.filter(x => x.stage === 'coding')) {
    assert.ok(!/\bby default\b/.test(x.doneCriterion.en), 'coding criterion without default adoption: ' + x.id);
    for (const d of x.dependsOn) assert.ok(task(l, d).stage !== 'creator-approval' && task(l, d).type !== 'integration', 'coding dependency: ' + x.id);
  }
  for (const id of ['code.runtime.character-sprite-pipeline', 'code.runtime.combat-sprite-pipeline', 'code.runtime.battle-arena-backdrop']) {
    const x = task(l, id);
    assert.ok(/Normal runtime capability/.test(x.doneCriterion.en) && /opt-in flag or test fixture with targeted tests/.test(x.doneCriterion.en), 'capability criterion: ' + id);
    // Status is mutable: todo, in_progress (no credit), or done with code evidence (a capability closeout never implies default adoption or approval).
    assert.ok(['todo', 'in_progress'].includes(x.status) || (x.status === 'done' && x.evidence.some(e => /^game\/scripts\//.test(e)) && x.evidence.some(e => /^docs\/qa\//.test(e))), 'todo/in_progress or done with code + QA evidence: ' + id);
  }
  // The backdrop capability and the battle-arena art tasks are independent (temp fixture, not the tracked statuses): any
  // status of the default-adoption and approval tasks leaves the backdrop status and the coding meter alone, and flipping
  // the backdrop leaves those tasks as they were. Either side may complete later without touching the other.
  const BACKDROP = 'code.runtime.battle-arena-backdrop', ART = ['content.scene.battle-arena.native-default', 'creator.scene.battle-arena.accept'];
  const fixture = (backdropStatus, artStatuses) => {
    const f = fresh();
    task(f, BACKDROP).status = backdropStatus;
    ART.forEach((id, i) => { task(f, id).status = artStatuses[i]; });
    return cli.refresh(f, ROOT);
  };
  const codingWith = {todo: fixture('todo', ['todo', 'todo']).computed.production.coding.done, done: fixture('done', ['todo', 'todo']).computed.production.coding.done};
  assert.equal(codingWith.done, codingWith.todo + task(l, BACKDROP).points);
  for (const b of ['todo', 'done']) for (const a0 of ['todo', 'in_progress', 'done']) for (const a1 of ['todo', 'done']) {
    const f = fixture(b, [a0, a1]), label = `${BACKDROP}=${b}, ${ART[0]}=${a0}, ${ART[1]}=${a1}`;
    assert.equal(task(f, BACKDROP).status, b, 'backdrop status independent of art tasks: ' + label);
    assert.deepEqual(ART.map(id => task(f, id).status), [a0, a1], 'art task statuses independent of backdrop: ' + label);
    assert.equal(f.computed.production.coding.done, codingWith[b], 'coding meter independent of art tasks: ' + label);
    assert.ok(!cli.validate(f, ROOT).some(e => e.includes(BACKDROP)), 'no backdrop validation error from art statuses: ' + label);
  }
  // A legitimate coding status change moves the meter by the frozen formula alone; no numeric fixture needs editing.
  const flip = fresh(), open = flip.tasks.find(x => x.stage === 'coding' && x.status === 'todo' && x.dependsOn.length === 0);
  if (open) {
    const hash = cli.taskSetHash(flip.tasks), was = flip.computed.production.coding.done;
    set(flip, open.id, 'done', {evidence: [CLI_REL]});
    assert.equal(cli.taskSetHash(flip.tasks), hash, 'status change keeps the frozen task set');
    assert.equal(flip.computed.production.coding.done, was + open.points);
    const c = flip.computed.production;
    assert.equal(c.percent, Math.round(10 * (40 * c.coding.done / c.coding.total + 60 * c.content.done / c.content.total)) / 10);
  }
  const dep = fresh(); task(dep, 'code.runtime.battle-arena-backdrop').dependsOn = ['creator.scene.battle-arena.accept'];
  assert.ok(cli.validate(dep, ROOT).some(e => /may not depend on approval or default art adoption/.test(e)));
  const adopt = fresh(); task(adopt, 'code.runtime.battle-arena-backdrop').dependsOn = ['content.scene.battle-arena.native-default'];
  assert.ok(cli.validate(adopt, ROOT).some(e => /may not depend on approval or default art adoption/.test(e)));
  const weak = fresh(); task(weak, 'code.runtime.character-sprite-pipeline').doneCriterion = {zh: '载入', en: 'loads something'};
  assert.ok(cli.validate(weak, ROOT).some(e => /frozen baseline/.test(e)), 'weakening a done criterion fails the freeze');
  const strong = fresh(); task(strong, 'code.runtime.character-sprite-pipeline').doneCriterion = {zh: 'x', en: 'Runtime loads the set by default'};
  assert.ok(cli.validate(strong, ROOT).some(e => /may not require default art adoption/.test(e)));
  const deps = fresh(); task(deps, 'content.char.milo.static-west').dependsOn = [];
  assert.ok(cli.validate(deps, ROOT).some(e => /frozen baseline/.test(e)), 'dropping a dependency fails the freeze');
  checkStatusMutableHashFrozen(fresh());
  pass('coding = normal runtime capability via opt-in/fixtures (no approval or default-adoption dependency); pipeline tasks todo, in_progress or done with code evidence; a coding closeout recomputes by formula; freeze covers criteria and dependencies, status stays mutable');
}

// 9. No evidence, missing evidence, unmet dependencies or the rejected 32x48 baseline cannot complete a task.
{
  const l = fresh();
  assert.throws(() => set(l, 'content.char.milo.static-south', 'done'), /without evidence/);
  assert.throws(() => set(l, 'content.char.milo.static-south', 'done', {evidence: ['docs/qa/does-not-exist.md']}), /not found/);
  assert.throws(() => set(l, 'content.char.milo.static-west', 'done', {evidence: ['game/tests/m1_smoke.gd']}), /dependency/);
  const placeholder = 'game/assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-male_native-idle-west_m8-v01_20261014-135316-2d359882.png';
  assert.ok(fs.existsSync(path.join(ROOT, placeholder)));
  assert.throws(() => set(l, 'content.char.protagonist-male.static-west', 'done', {evidence: [placeholder]}), /rejected 32x48/);
  assert.throws(() => set(l, 'review.scene.city', 'not_required', {evidence: ['game/tests/m1_smoke.gd'], waivedBy: 'creator.scene.city.accept'}), /waivedBy/);
  pass('completion refused without evidence, with missing files, before dependencies, from the rejected baseline, or with an invalid waiver');
}

// 10. Frozen baseline: a new version, receipt or point change cannot inflate progress silently.
{
  const extra = fresh(); extra.tasks.push({...task(extra, 'content.scene.city.native-pass'), id: 'content.scene.city.native-pass-v07'});
  assert.ok(cli.validate(extra, ROOT).some(e => /frozen baseline/.test(e)));
  const repointed = fresh(); task(repointed, 'content.scene.city.plate').points = 21;
  assert.ok(cli.validate(repointed, ROOT).some(e => /frozen baseline/.test(e)));
  const reweighted = fresh(); reweighted.baseline.weights.coding = 50;
  assert.ok(cli.validate(reweighted, ROOT).some(e => /weights/.test(e)));
  const l = fresh(); assert.equal(new Set(l.tasks.map(x => x.subject.id).filter((_, i) => l.tasks[i].subject.kind === 'character-variant')).size, 52);
  assert.equal(new Set(l.tasks.filter(x => x.subject.kind === 'scene-gate').map(x => x.subject.id)).size, 12);
  pass('extra version tasks, re-pointing and re-weighting rejected; 52 variants and 12 scene gates covered');
}

// 11. The legacy 40.8% meter is read only, labelled as a mixed delivery/acceptance estimate, and final acceptance is false.
{
  const l = fresh(), progress = JSON.parse(fs.readFileSync(PROGRESS, 'utf8'));
  assert.equal(l.computed.legacy.percent, 40.8);
  assert.equal(progress.completionMeter.percent, 40.8);
  assert.match(l.computed.legacy.en, /mixed delivery\/acceptance estimate \(not formal acceptance\)/);
  assert.equal(l.computed.release.finalAccepted, false);
  const closeouts = progress.completionMeter.taskCloseouts;
  assert.equal(closeouts.length, 140);
  assert.equal(closeouts.at(-1).id, l.closeouts[0].legacyCloseoutId);
  assert.equal(closeouts.at(-1).impact.changed, false);
  pass('legacy meter 40.8% read only and labelled; 140th closeout is the zero-change baseline record; final acceptance false');
}

// 12. CLI end to end on a temp copy.
{
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'pc-ledger-'));
  const copy = path.join(dir, 'ledger.json');
  fs.copyFileSync(LEDGER, copy);
  const run = (...args) => spawnSync(process.execPath, [CLI_REL, ...args, '--ledger', copy, '--now', NOW], {cwd: ROOT, encoding: 'utf8'});
  assert.notEqual(run('set', '--task', 'content.char.adi.static-south', '--status', 'done').status, 0);
  assert.equal(run('revise', '--for', 'content.scene.map.native-pass', '--reason-en', 'reopen').status, 0);
  const n = JSON.parse(fs.readFileSync(copy, 'utf8')).tasks.length;
  assert.equal(run('revise', '--for', 'content.scene.map.native-pass', '--reason-en', 'again').status, 0);
  assert.equal(JSON.parse(fs.readFileSync(copy, 'utf8')).tasks.length, n);
  assert.equal(run('check').status, 0);
  const snapshot = fs.readFileSync(copy, 'utf8');
  assert.equal(run('reassign', '--task', 'code.runtime.audio-cues', '--owner', 'codex', '--reason-en', 'Quota takeover', '--dry-run').status, 0);
  assert.equal(fs.readFileSync(copy, 'utf8'), snapshot, 'dry-run assignment never writes');
  assert.equal(run('reassign', '--task', 'code.runtime.audio-cues', '--owner', 'codex', '--reason-en', 'Quota takeover').status, 0);
  assert.equal(JSON.parse(fs.readFileSync(copy, 'utf8')).tasks.find(x => x.id === 'code.runtime.audio-cues').owner, 'codex');
  const assigned = fs.readFileSync(copy, 'utf8');
  assert.notEqual(run('reassign', '--task', 'creator.scene.city.accept', '--owner', 'claude', '--reason-en', 'unsupported').status, 0);
  assert.equal(fs.readFileSync(copy, 'utf8'), assigned, 'failed CLI transfer does not write');
  assert.equal(run('reassign', '--task', 'code.runtime.audio-cues', '--owner', 'codex', '--reason-en', 'retry').status, 0);
  assert.equal(fs.readFileSync(copy, 'utf8'), assigned, 'same-owner CLI retry idempotent');
  assert.equal(run('reassign', '--task', 'code.runtime.audio-cues', '--owner', 'claude', '--reason-en', 'Return after reset').status, 0);
  assert.equal(run('check').status, 0, 'CLI audit chain validates after reversing transfer');
  const stale = JSON.parse(fs.readFileSync(copy, 'utf8')); stale.computed.production.percent = 99;
  fs.writeFileSync(copy, JSON.stringify(stale));
  assert.notEqual(run('check').status, 0);
  fs.rmSync(dir, {recursive: true, force: true});
  pass('CLI: evidence enforced, repeated revise reopens one bucket, audited assignment/dry-run/retry/reverse supported, fixed-owner transfer and stale numbers rejected');
}

// 13. Local Game Bible panel: the real v05 server serves the ledger and the served bible.js renders it without recomputing.
async function renderPanel() {
  const net = require('node:net'), vm = require('node:vm');
  const port = await new Promise((resolve, reject) => { const probe = net.createServer().once('error', reject); probe.listen(0, '127.0.0.1', () => { const p = probe.address().port; probe.close(() => resolve(p)); }); });
  const server = require('node:child_process').spawn(process.execPath, ['tools/rpg-2-star-ocean-the-second_game-bible_server_v05_20261013-222437-3d5b8a9f.js'], {cwd: ROOT, env: {...process.env, WORLDS_BETWEEN_BIBLE_PORT: String(port)}, stdio: 'ignore'});
  const base = 'http://127.0.0.1:' + port, sleep = ms => new Promise(r => setTimeout(r, ms));
  const waitFor = async (check, label) => { const end = Date.now() + 8000; while (Date.now() < end) { try { if (await check()) return; } catch (_) {} await sleep(50); } throw new Error('timeout ' + label); };
  try {
    await waitFor(async () => (await fetch(base + '/health')).ok, 'server');
    const served = await (await fetch(base + '/production')).json();
    assert.deepEqual(served.computed, fresh().computed);
    const element = () => ({innerHTML: '', textContent: '', value: '', dataset: {}, addEventListener() {}, setAttribute() {}, querySelector: () => element(), querySelectorAll: () => []});
    const content = {...element(), querySelector: () => element()};
    const elements = {content, search: element(), edition: element(), pitch: element(), 'footer-status': element()};
    const nav = ['home', 'world', 'rules', 'characters', 'production', 'assets'].map(view => { const b = {...element(), dataset: {view}, handlers: {}}; b.addEventListener = (t, h) => { b.handlers[t] = h; }; return b; });
    const context = vm.createContext({document: {getElementById: id => elements[id], querySelectorAll: () => nav, addEventListener() {}, hidden: true, createElement: () => element()},
      fetch: (url, options) => fetch(base + url, options), setInterval() {}, localStorage: {getItem: () => '', setItem() {}}, console});
    vm.runInContext(await (await fetch(base + '/bible.js')).text(), context, {filename: 'bible.js'});
    await waitFor(() => elements.edition.textContent !== '', 'bible load');
    nav.find(b => b.dataset.view === 'production').handlers.click();
    await waitFor(() => content.innerHTML.includes('id="production-completion"'), 'production panel');
    return {html: content.innerHTML, served};
  } finally { server.kill(); }
}

(async () => {
  const {html, served} = await renderPanel();
  const panel = html.slice(html.indexOf('id="production-completion"'), html.indexOf('</section>', html.indexOf('id="production-completion"')));
  const c = served.computed;
  assert.equal((panel.match(/role="progressbar"/g) || []).length, 5, 'one main bar plus coding, content, inspection and approval bars');
  for (const text of [c.production.percentLabel, `${c.production.coding.done} / ${c.production.coding.total} 分 points`, `${c.production.content.tasksDone} / ${c.production.content.tasks} 项任务 tasks`,
    `${c.inspection.done} / ${c.inspection.total} 分 points`, `${c.approval.done} / ${c.approval.total} 分 points`, '否 / false', `Needs revision（${c.queue.needsRevision.count}）`, `Ready（${c.queue.count}）`]) assert.ok(panel.includes(text), 'panel shows ' + text);
  assert.match(panel, /<details class="group"><summary>公式与分值 \/ Formula and points<\/summary><p class="small"><code>round1\(40/);
  assert.match(panel, /<details class="group"><summary>旧版混合交付／验收估算（不是正式验收）\/ Legacy mixed delivery\/acceptance estimate \(not formal acceptance\) · 40\.8%<\/summary>/);
  assert.ok(html.includes('id="cross-device-review-queue"'), 'existing review queue card still renders');
  pass(`local Bible panel: ${c.production.percentLabel} with 4 separate bars, formula/points in details, points vs tasks, ready ${c.queue.count} / needs revision ${c.queue.needsRevision.count}, legacy collapsed`);
  assert.deepEqual([LEDGER, PROGRESS].map(sha), before, 'tracked ledger and progress state untouched');
  pass('read-only: tracked ledger and progress state hashes unchanged');
  console.log(`RESULT PASS (${passed} checks)`);
})().catch(error => { console.error(error); process.exit(1); });
