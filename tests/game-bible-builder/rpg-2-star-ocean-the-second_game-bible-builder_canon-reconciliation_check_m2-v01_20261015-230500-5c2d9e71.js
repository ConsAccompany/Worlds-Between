// Focused check for the migrated Game Bible builder and the tracked Game Bible / MVP progress JSON after the creator decisions
// of 2026-10-15 (five Earth civilization spheres plus a separate portal planet, NYC / Catskills / 2537-05-25, M2 technical
// state (10/12 since the 2026-10-16 whole-hour route-times gate), 10-node skill rules with 0 of 710 nodes written). The builder must reproduce the tracked state from its sources
// (51 characters, approved 20-series job roster, superseded 7-node / 5-node drafts) plus the canon carried from the tracked state,
// and must refuse a base that lost that canon instead of regenerating the superseded v01 brief text.
// Read-only: the builder is required as a module and only build() / checkCanon() run in memory; no project file is written.
// Run from the repository root: node tests/game-bible-builder/<this file>
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const util = require('node:util');

const root = path.resolve(__dirname, '..', '..');
const builder = require(path.join(root, 'tools', 'rpg-2-star-ocean-the-second_game-bible-builder_v01_20261013-195422-7e2a4f19.js'));
const out = name => path.join(root, 'outputs', name);
const readJson = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const clone = value => JSON.parse(JSON.stringify(value));
const digest = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const pass = label => console.log('PASS ' + label);
const progressPath = out('rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json');
const before = {bible: digest(builder.dest), progress: digest(progressPath)};
const bible = readJson(builder.dest);
const progress = readJson(progressPath);

// 1. The tracked Game Bible passes every canon check.
const labels = builder.checkCanon(bible);
assert.ok(labels.length >= 20, 'canon check count');
pass(`tracked Game Bible canon: ${labels.length} checks (five Earth spheres + portal planet, NYC/Catskills/2537-05-25, 51 identities with legacy board labels, superseded 7-node/5-node drafts, 0 of 710 approved nodes, scene 0/11, sprites 0)`);

// 2. A rebuild from the sources reproduces the tracked state; the approved job names are the source text unchanged.
const built = builder.build({base: clone(bible), updatedAt: bible.updatedAt});
if (!util.isDeepStrictEqual(built, bible)) {
  const differing = [...new Set([...Object.keys(built), ...Object.keys(bible)])].filter(key => !util.isDeepStrictEqual(built[key], bible[key]));
  assert.fail('rebuild differs from the tracked state in: ' + differing.join(', '));
}
assert.deepEqual(Object.keys(built), Object.keys(bible), 'top-level key order preserved');
const jobsSource = readJson(out(builder.names.jobs));
assert.deepEqual(bible.jobProposal.series, jobsSource.series, 'approved stage names and final quests equal the source verbatim');
const bytesEqual = builder.serialize(built) === fs.readFileSync(builder.dest, 'utf8').replace(/\r\n/g, '\n');
pass(`rebuild reproduces the tracked state (content identical, key order identical; serialized bytes ${bytesEqual ? 'identical' : 'differ in formatting only'}); 20 approved series equal the source`);

// 3. Regression guards: the builder refuses a base without the canon, and the checks reject stale or overstated data.
const withoutDecisions = clone(bible);
delete withoutDecisions.creatorDecisions;
assert.throws(() => builder.build({base: withoutDecisions, updatedAt: 'x'}), /Refusing to build/, 'missing creatorDecisions refused');
const withoutReview = clone(bible);
delete withoutReview.environmentVisualReview;
assert.throws(() => builder.build({base: withoutReview, updatedAt: 'x'}), /curated section environmentVisualReview/, 'missing review block refused');
const brief = fs.readFileSync(out(builder.names.brief), 'utf8').replace(/\r\n/g, '\n');
const oldWorld = brief.split(/^## /m)[2];
assert.ok(oldWorld.startsWith('2. 世界与剧情结构') && oldWorld.includes('### 五个板块'), 'fixture: v01 brief world chapter');
const staleBase = clone(bible);
staleBase.chapters[1].body = oldWorld.slice(oldWorld.indexOf('\n') + 1).trim();
assert.throws(() => builder.build({base: staleBase, updatedAt: 'x'}), /world chapter carries the new canon/, 'v01 brief world text rejected');
const mutations = [
  ['invented sphere on a companion', b => { b.characters[1].sphere = 'science'; }, /invented sphere/],
  ['approved nodes claimed as written', b => { b.canonBasis.skillNodes.approvedAuthored = 710; }, /0 of 710/],
  ['old five-board world fact', b => { b.facts.find(f => f.label === '世界').value = '5 个板块 · 地球与传送门另一端'; }, /world fact/],
  ['final planet listed as an Earth sphere', b => { b.creatorDecisions.spheres.push({id: 'offworld', zh: '星外', region: '另一颗星球', hubs: []}); }, /five Earth spheres/],
  ['career draft no longer superseded', b => { b.skillTreeProposal.superseded = false; }, /career trees/],
  ['personal draft rank rule rewritten', b => { b.personalSkillTrees.approvedRules.rankMaximum = 3; }, /personal trees/],
  ['scene counter incremented', b => { b.environmentVisualReview.sceneQualityAccepted = 1; }, /scene visuals 0\/11/],
  ['wrong start date', b => { b.creatorDecisions.geography.adventureStart = '2026-04-01'; }, /geography/],
  ['selout v8 baseline claimed as animated', b => { b.characterVisualReview.staticBaselinesAndPilots.femaleExplorationSouthBaseline.animation = true; }, /selout v8/],
  ['battle v08 pilot claimed as approved', b => { b.characterVisualReview.staticBaselinesAndPilots.femaleBattleSideviewV08.status = 'APPROVED'; }, /battle side-view v08/],
  ['battle v08 pilot claimed as wired', b => { b.characterVisualReview.staticBaselinesAndPilots.femaleBattleSideviewV08.runtimeIntegrated = true; }, /battle side-view v08/],
  ['Liang pilot claimed as four-direction', b => { b.characterVisualReview.staticBaselinesAndPilots.liangXuSouthIdleV01.directions = ['south', 'east', 'north', 'west']; }, /Liang Xu south v01/],
  ['Liang pilot gendered', b => { b.characterVisualReview.staticBaselinesAndPilots.liangXuSouthIdleV01.openIssues.push('his coat'); }, /Liang Xu south v01/],
  ['static pilots claim a progress increase', b => { b.characterVisualReview.staticBaselinesAndPilots.counters.runtimeSpritesAccepted = '1/52'; }, /static pilots/],
];
for (const [label, mutate, pattern] of mutations) {
  const copy = clone(bible);
  mutate(copy);
  assert.throws(() => builder.checkCanon(copy), pattern, label);
}
pass(`builder refuses a base without creatorDecisions or a curated review block and rejects the v01 brief world chapter; ${mutations.length} stale/overstated mutations rejected`);

// 4. MVP progress JSON: M2 10/12 implemented technical state (route-data = whole-hour route times since 2026-10-16), none done; counters honest and consistent with the Bible.
const m2 = progress.steps.find(step => step.id === 'M2');
assert.equal(m2.status, 'in_progress');
for (const phrase of ['five Earth spheres', 'portal-only final planet', 'Catskills', '2537-05-25', 'M2 is not complete']) assert.ok(m2.summary.includes(phrase), 'M2 summary: ' + phrase);
assert.ok(!m2.evidence.some(line => line.includes('source of the current preliminary figures')), 'Shanghai packet no longer named as the source of the current figures');
assert.ok(m2.evidence.filter(line => line.includes('shanghai')).every(line => line.includes('superseded')), 'Shanghai research evidence labelled superseded');
const gates = progress.m2Expansion.gates;
const implemented = gates.filter(gate => gate.status === 'implemented').map(gate => gate.id);
assert.equal(gates.length, 12);
assert.equal(implemented.length, 10, '10 of 12 gates implemented');
assert.deepEqual(gates.filter(gate => gate.status !== 'implemented').map(gate => [gate.id, gate.status]), [['map-art', 'not_started'], ['visual-review', 'human_pending']]);
assert.equal(gates.find(gate => gate.id === 'route-data').en, 'Route times (whole-hour rule)', 'route-data is the whole-hour route-times gate');
assert.ok(!gates.some(gate => /done|accepted|approved/.test(gate.status)), 'no gate claims acceptance');
const counters = progress.approvalLedger.counters;
assert.deepEqual(counters, {identities: 51, visualVariants: 52, runtimeSpritesAccepted: 0, runtimeSpritesTarget: 52, sceneVisualsAccepted: 0, sceneVisualsTarget: 11, humanPlaytests: 0, humanPlaytestsTarget: 2});
assert.equal(bible.characters.length, counters.identities, 'Bible identities equal the ledger');
assert.equal(bible.environmentVisualReview.sceneQualityTarget, counters.sceneVisualsTarget);
assert.equal(bible.creatorDecisions.geography.adventureStart, progress.m2Expansion.creatorDecision.adventureStart);
const redesign = progress.decisions.find(decision => decision.id === 'skill-tree-redesign');
assert.ok(redesign && redesign.kind === 'blocked' && redesign.detail.includes('200 + 510') && bible.canonBasis.skillNodes.approvedRequired === 200 + 510, 'skill redesign stays blocked at 200 + 510 = 710');
pass(`progress: M2 in progress, ${implemented.length}/${gates.length} gates implemented, 2 open, none accepted; counters sprites 0/52, scenes 0/11, playtests 0/2, 51 identities / 52 variants; start date and 710-node redesign consistent with the Bible`);

// 5. Nothing was written.
assert.deepEqual({bible: digest(builder.dest), progress: digest(progressPath)}, before, 'tracked JSON untouched');
pass('read-only: tracked Game Bible and progress JSON hashes unchanged');
console.log('RESULT PASS (5 checks)');
