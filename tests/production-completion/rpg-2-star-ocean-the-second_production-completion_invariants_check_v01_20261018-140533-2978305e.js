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
const NOW = '2026-10-18T18:30:00Z';
const sha = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const fresh = () => cli.load(LEDGER);
const snapshot = l => JSON.stringify(l.computed.production);
const set = (l, task, status, extra = {}) => cli.setTask(l, ROOT, {task, status, evidence: [], now: NOW, ...extra});
let passed = 0;
const pass = msg => { passed += 1; console.log('PASS ' + msg); };

const before = [LEDGER, PROGRESS].map(sha);

// 1. The tracked ledger validates and a recompute is byte-identical (idempotent), twice in a row.
{
  const l = fresh();
  assert.deepEqual(cli.validate(l, ROOT), []);
  const once = cli.serialize(cli.refresh(fresh(), ROOT));
  const twice = cli.serialize(cli.refresh(cli.refresh(fresh(), ROOT), ROOT));
  assert.equal(once, twice);
  assert.equal(once, fs.readFileSync(LEDGER, 'utf8').replace(/\r\n/g, '\n'));
  const out = spawnSync(process.execPath, [CLI_REL, 'check'], {cwd: ROOT, encoding: 'utf8'});
  assert.equal(out.status, 0, out.stdout + out.stderr);
  pass('tracked ledger validates; recompute is idempotent and byte-identical; CLI check exits 0');
}

// 2. One derivation, rounded once: production equals round1(40*c + 60*n) from task points.
{
  const l = fresh(), sum = (st, done) => l.tasks.filter(x => x.stage === st && (!done || cli.CREDITED.has(x.status))).reduce((s, x) => s + x.points, 0);
  const expected = Math.round(10 * (40 * sum('coding', true) / sum('coding') + 60 * sum('content', true) / sum('content'))) / 10;
  assert.equal(l.computed.production.percent, expected);
  assert.equal(l.computed.production.coding.done, sum('coding', true));
  assert.equal(l.computed.production.content.total, sum('content'));
  pass(`production ${expected}% = round1(40 x ${sum('coding', true)}/${sum('coding')} + 60 x ${sum('content', true)}/${sum('content')})`);
}

// 3. A finished deliverable whose review is still pending keeps its production credit; finishing the review moves only inspection.
{
  const l = fresh();
  const review = l.tasks.find(x => x.id === 'review.scene.city');
  assert.equal(l.tasks.find(x => x.id === 'content.scene.city.native-pass').status, 'done');
  assert.ok(l.computed.queue.items.some(q => q.id === review.id), 'city review is in the ready queue');
  const prod = snapshot(l), insp = l.computed.inspection.done;
  set(l, review.id, 'done', {outcome: 'changes_requested', evidence: ['docs/qa/rpg-2-star-ocean-the-second_nyc-city-hall-park_v06-cross-device-review-packet_unapproved-v01_20261017-174208-fe6b9f9d.md']});
  assert.equal(snapshot(l), prod);
  assert.equal(l.computed.inspection.done, insp + review.points);
  pass('review pending or done (even changes_requested) never changes production credit');
}

// 4. Toggling a creator approval cannot change production, coding or content.
{
  const l = fresh(), prod = snapshot(l), appr = l.computed.approval.done;
  set(l, 'creator.scene.city.accept', 'done', {evidence: ['docs/qa/rpg-2-star-ocean-the-second_nyc-city-hall-park_scene-candidate-640x360_qa-note_unapproved-v06_20261017-165253-4519dffe.md']});
  assert.equal(snapshot(l), prod);
  assert.equal(l.computed.approval.done, appr + 1);
  set(l, 'creator.scene.city.accept', 'changes_requested');
  assert.equal(snapshot(l), prod);
  set(l, 'creator.scene.city-survey-outer.accept', 'todo');
  assert.equal(snapshot(l), prod);
  assert.equal(l.tasks.find(x => x.id === 'review.scene.city-survey-outer').status, 'todo', 'a withdrawn approval voids its waiver');
  assert.deepEqual(cli.validate(l, ROOT), []);
  pass('approval done / changes_requested / withdrawn leaves production identical (a withdrawn waiver reopens its review)');
}

// 5. Rejection plus revision: completed initial work keeps its credit; the fixed rework milestone is visible and unfinished.
{
  const l = fresh(), prodBefore = l.computed.production, rev = l.baseline.revisions.length;
  set(l, 'creator.scene.ruins.accept', 'changes_requested');
  cli.addRework(l, ROOT, {for: 'creator.scene.ruins.accept', points: '6', titleEn: 'Capitol west revision after creator notes', titleZh: '按创作者意见修订国会大厦西侧', reasonEn: 'test rejection', now: NOW});
  const rework = l.tasks.find(x => x.id === 'content.scene.ruins.rework-r1');
  assert.ok(rework && rework.status === 'todo' && rework.owner === 'claude' && rework.dependsOn.includes('content.scene.ruins.native-pass'));
  assert.equal(l.tasks.find(x => x.id === 'content.scene.ruins.native-pass').status, 'done');
  assert.equal(l.computed.production.content.done, prodBefore.content.done, 'original production credit kept');
  assert.equal(l.computed.production.content.total, prodBefore.content.total + 6, 'rework only adds to the denominator');
  assert.ok(l.computed.production.percent <= prodBefore.percent, 'a revision can never raise the percent');
  assert.equal(l.baseline.revisions.length, rev + 1);
  assert.deepEqual(cli.validate(l, ROOT), [], 'revision is recorded, so the frozen-baseline check still passes');
  pass('reject + add-rework keeps prior production, shows the rework milestone, records a baseline revision');
}

// 6. No evidence, missing evidence, unmet dependencies or the rejected 32x48 baseline cannot complete a task.
{
  const l = fresh();
  assert.throws(() => set(l, 'content.char.milo.static-south', 'done'), /without evidence/);
  assert.throws(() => set(l, 'content.char.milo.static-south', 'done', {evidence: ['docs/qa/does-not-exist.md']}), /not found/);
  assert.throws(() => set(l, 'content.char.milo.static-west', 'done', {evidence: ['game/tests/m1_smoke.gd']}), /dependency/);
  const placeholder = 'game/assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-male_native-idle-west_m8-v01_20261014-135316-2d359882.png';
  assert.ok(fs.existsSync(path.join(ROOT, placeholder)));
  assert.throws(() => set(l, 'content.char.protagonist-male.static-west', 'done', {evidence: [placeholder]}), /rejected 32x48/);
  assert.throws(() => set(l, 'review.scene.city', 'not_required', {evidence: ['game/tests/m1_smoke.gd'], waivedBy: 'creator.scene.city.accept'}), /waivedBy/);
  for (const x of l.tasks.filter(t => cli.CREDITED.has(t.status))) assert.ok(x.evidence.length, x.id);
  pass('completion refused without evidence, with missing files, before dependencies, from the rejected baseline, or with an invalid waiver');
}

// 7. Owners, stable IDs, scope coverage and bounded points.
{
  const l = fresh();
  for (const x of l.tasks) assert.equal(x.owner, cli.STAGES[x.stage].owner, x.id);
  assert.equal(new Set(l.tasks.map(x => x.id)).size, l.tasks.length);
  const variants = new Set(l.tasks.filter(x => x.subject.kind === 'character-variant').map(x => x.subject.id));
  assert.equal(variants.size, 52);
  assert.equal(new Set(l.tasks.filter(x => x.subject.kind === 'scene-gate').map(x => x.subject.id)).size, 12);
  assert.equal(l.tasks.filter(x => /^content\.char\..*\.walk-(south|west|north|east)$/.test(x.id)).length, 208);
  assert.ok(l.tasks.every(x => x.points >= 1 && x.points <= 21));
  const mutated = fresh(); mutated.tasks[0].owner = 'codex';
  assert.ok(cli.validate(mutated, ROOT).some(e => /owner/.test(e)));
  const badId = fresh(); badId.tasks[0].id = 'Task 1';
  assert.ok(cli.validate(badId, ROOT).some(e => /stable pattern/.test(e)));
  pass(`${l.tasks.length} tasks: one owner per stage, unique stable IDs, 52 variants x all milestones, 12 scene gates, points 1-21`);
}

// 8. Frozen baseline: a new version, receipt or point change cannot inflate progress silently.
{
  const extra = fresh();
  extra.tasks.push({...extra.tasks.find(x => x.id === 'content.scene.city.native-pass'), id: 'content.scene.city.native-pass-v07', status: 'done'});
  assert.ok(cli.validate(extra, ROOT).some(e => /frozen baseline/.test(e)), 'adding a version as a task fails the baseline check');
  const repointed = fresh(); repointed.tasks.find(x => x.id === 'content.scene.city.plate').points = 21;
  assert.ok(cli.validate(repointed, ROOT).some(e => /frozen baseline/.test(e)), 'changing points fails the baseline check');
  const reweighted = fresh(); reweighted.baseline.weights.coding = 50;
  assert.ok(cli.validate(reweighted, ROOT).some(e => /weights/.test(e)));
  pass('extra version tasks, re-pointing and re-weighting are all rejected by the frozen baseline');
}

// 9. The legacy 40.8% acceptance meter is read only and reported separately.
{
  const l = fresh(), progress = JSON.parse(fs.readFileSync(PROGRESS, 'utf8'));
  assert.equal(l.computed.legacy.percent, progress.completionMeter.percent);
  assert.equal(l.computed.legacy.percent, 40.8);
  assert.equal(l.computed.release.finalAccepted, false);
  assert.equal(progress.completionMeter.formalApproval.mvpFormallyAccepted, false);
  pass('legacy meter mirrored read-only (40.8%), final acceptance false');
}

// 10. CLI end to end on a temp copy (set refuses without evidence; check catches a stale file).
{
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'pc-ledger-'));
  const copy = path.join(dir, 'ledger.json');
  fs.copyFileSync(LEDGER, copy);
  const run = (...args) => spawnSync(process.execPath, [CLI_REL, ...args, '--ledger', copy, '--now', NOW], {cwd: ROOT, encoding: 'utf8'});
  assert.notEqual(run('set', '--task', 'content.char.adi.static-south', '--status', 'done').status, 0);
  const ok = run('set', '--task', 'review.scene.chicago-loop', '--status', 'done', '--outcome', 'technical-pass', '--evidence', 'docs/qa/rpg-2-star-ocean-the-second_chicago-loop_state-lake-arrival-block-native-scene_qa-note_unapproved-v03r1_20261017-184340-49dde4dd.md');
  assert.equal(ok.status, 0, ok.stdout + ok.stderr);
  assert.equal(run('check').status, 0);
  const stale = JSON.parse(fs.readFileSync(copy, 'utf8')); stale.computed.production.percent = 99;
  fs.writeFileSync(copy, JSON.stringify(stale));
  assert.notEqual(run('check').status, 0);
  fs.rmSync(dir, {recursive: true, force: true});
  pass('CLI set/check on a temp copy: evidence enforced, stale derived numbers rejected');
}

// 11. Local Game Bible panel: the real v05 server serves the ledger and the served bible.js renders it without recomputing.
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
  for (const text of [c.production.percentLabel, `${c.production.coding.done} / ${c.production.coding.total}`, `${c.production.content.done} / ${c.production.content.total}`,
    `${c.inspection.done} / ${c.inspection.total}`, `${c.approval.done} / ${c.approval.total}`, '否 / false']) assert.ok(panel.includes(text), 'panel shows ' + text);
  assert.match(panel, /<details class="group"><summary>旧版验收加权估算（不同指标）· 40\.8%<\/summary>/, 'legacy 40.8% is collapsed and labelled');
  assert.ok(html.includes('id="cross-device-review-queue"'), 'existing review queue card still renders');
  pass(`local Bible panel renders ${c.production.percentLabel} (coding/content/inspection/approval), legacy collapsed, review queue intact`);
  assert.deepEqual([LEDGER, PROGRESS].map(sha), before, 'tracked ledger and progress state untouched');
  pass('read-only: tracked ledger and progress state hashes unchanged');
  console.log(`RESULT PASS (${passed} checks)`);
})().catch(error => { console.error(error); process.exit(1); });
