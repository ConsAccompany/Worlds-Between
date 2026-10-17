#!/usr/bin/env node
// Worlds Between MVP completion meter: recompute, validate and record task closeouts against the authoritative progress state.
// The meter is a weighted delivery estimate, never formal approval. Counts come only from authoritative fields:
// steps[].status, m2Expansion.gates[].status, the meter's own M7 content gates, and approvalLedger.counters backed by accepted
// approvalLedger items. Concepts, unapproved static frames, direction approvals and smoke tests never count as visual acceptance.
// A task that changes no gate records a zero-change receipt; every count change must be claimed with --gate and evidenced.
// Run from the repository root:
//   node tools/<this file> check
//   node tools/<this file> init        (once: adds completionMeter with a baseline closeout)
//   node tools/<this file> record --title-en "..." [--title-zh "..."] [--gate <category>[/<gate>]]...
//        [--set-gate science-playable-content/<gate>=<status>]... [--evidence <repo path>]... [--baseline-revision] [--dry-run]
// --baseline-revision records a change to a fixed denominator (kind baseline-revision); it may not change any count.
// Options for every command: --state <path> works on another copy (tests); --now <ISO time> fixes the timestamp.
'use strict';
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const STATE_REL = 'outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json';
const METER_ID = 'rpg-2-star-ocean-the-second_mvp-completion-meter_v01';
const COUNTERS_PTR = STATE_REL + '#/approvalLedger/counters';
const STEP_STATUSES = ['done', 'in_progress', 'todo', 'blocked'];
const M2_GATE_STATUSES = ['implemented', 'done', 'estimate_only', 'not_started', 'human_pending', 'in_progress', 'todo', 'blocked'];
const SCIENCE_GATE_STATUSES = ['done', 'human_pending', 'in_progress', 'todo', 'blocked'];
// Evidence for a visual acceptance or post-art playtest may not be a concept, an unapproved file or a smoke test.
const NON_ACCEPTANCE_EVIDENCE = /concept|unapproved|smoke/i;

// Fixed baseline weights, denominators and gate sets. Changing any of these is a deliberate baseline revision, not task progress.
const CATEGORIES = [
  {id: 'core-gameplay', weight: 20, denominator: 5, kind: 'steps', stepIds: ['M1', 'M3', 'M4', 'M5', 'M6'], countStatuses: ['done'],
    zh: '核心玩法系统', en: 'Core gameplay systems',
    rule: {zh: '按 steps 中 M1、M3、M4、M5、M6 的状态计数，仅 done 计入。', en: 'Counts steps M1, M3, M4, M5 and M6; only status done counts.'}},
  {id: 'global-world-travel', weight: 10, denominator: 12, kind: 'm2-gates', countStatuses: ['implemented', 'done'],
    gateIds: ['map-ui', 'place-registry', 'route-preview', 'calendar', 'save-migration', 'acceptance-test', 'anchor', 'start-year', 'route-data', 'air-route', 'map-art', 'visual-review'],
    zh: '全球世界与旅行', en: 'Global world and travel',
    rule: {zh: '按 m2Expansion.gates 的 12 道门计数，仅 implemented／done 计入。', en: 'Counts the 12 m2Expansion.gates; only status implemented or done counts.'}},
  {id: 'science-playable-content', weight: 10, denominator: 4, kind: 'meter-gates', countStatuses: ['done'],
    gateIds: ['three-area-route', 'investigations-companions', 'report-endpoint', 'human-timed-pacing'],
    zh: '科技圈可玩内容', en: 'Science-sphere playable content',
    rule: {zh: '按本表内 4 道 M7 内容门计数，仅 done 计入；真人计时节奏需真人试玩证据。', en: 'Counts the four M7 content gates in this meter; only done counts. Pacing needs human playtest evidence.'}},
  {id: 'character-art', weight: 25, denominator: 52, kind: 'ledger-counter', counter: 'runtimeSpritesAccepted', target: 'runtimeSpritesTarget', acceptanceKind: 'runtime-sprite',
    zh: '角色美术（已验收运行时精灵）', en: 'Character art (accepted runtime sprites)',
    rule: {zh: '取 approvalLedger.counters.runtimeSpritesAccepted，且须有 status=accepted、acceptanceKind=runtime-sprite 的台账条目支撑；概念稿、未批准静态帧和冒烟测试不计。', en: 'Uses approvalLedger.counters.runtimeSpritesAccepted, backed by ledger items with status accepted and acceptanceKind runtime-sprite. Concepts, unapproved static frames and smoke tests never count.'}},
  {id: 'science-environment-art', weight: 20, denominator: 12, kind: 'ledger-counter', counter: 'sceneVisualsAccepted', target: 'sceneVisualsTarget', acceptanceKind: 'scene-visual',
    zh: '科技圈环境美术（已验收场景画质门）', en: 'Science environment art (accepted scene-quality gates)',
    rule: {zh: '取 approvalLedger.counters.sceneVisualsAccepted，且须有 status=accepted、acceptanceKind=scene-visual 的台账条目支撑；概念图与方向认可不计。', en: 'Uses approvalLedger.counters.sceneVisualsAccepted, backed by ledger items with status accepted and acceptanceKind scene-visual. Concepts and direction approvals never count.'}},
  {id: 'final-integrated-validation', weight: 15, denominator: 2, kind: 'ledger-counter', counter: 'humanPlaytests', target: 'humanPlaytestsTarget', acceptanceKind: 'post-art-playtest', requiresArtComplete: true,
    zh: '最终整合验证（美术完成后的真人试玩）', en: 'Final integrated validation (post-art human playtests)',
    rule: {zh: '只计角色与环境美术全部验收后、由 acceptanceKind=post-art-playtest 台账条目支撑的真人试玩。', en: 'Counts only human playtests backed by acceptanceKind post-art-playtest ledger items, after both art categories are complete.'}},
];

// Baseline M7 content gates written by init (2026-10-15). After init the meter's own gates are the authoritative record.
const SCIENCE_GATE_BASELINE = [
  {id: 'three-area-route', status: 'done', zh: '三处地点自由顺序路线', en: 'Three-area free-order route',
    evidence: ['game/tests/m7_smoke.gd', 'game/tests/m2_smoke.gd']},
  {id: 'investigations-companions', status: 'done', zh: '勘察、证据关联与同行伙伴内容', en: 'Investigations, evidence links and companion content',
    evidence: ['game/tests/m7_smoke.gd', 'outputs/rpg-2-star-ocean-the-second_scifi-field-assists_visual-manifest_m7_20261013-221344-6c9a8f31.json', 'outputs/rpg-2-star-ocean-the-second_scifi-field-traces_visual-manifest_m7_20261013-223107-42db9171.json']},
  {id: 'report-endpoint', status: 'done', zh: '城市报告终点与试玩回执', en: 'City report endpoint and playtest receipt',
    evidence: ['game/tests/m7_smoke.gd', 'tools/rpg-2-star-ocean-the-second_scifi-region_playtest-launcher_m7_20261013-214924-6c8e0d47.ps1']},
  {id: 'human-timed-pacing', status: 'human_pending', zh: '真人计时 25–35 分钟节奏', en: 'Human-verified 25–35 minute pacing',
    evidence: [], note: {zh: '步行下限审计只是机械下限，不是试玩时长。', en: 'The walking lower-bound audit is a mechanical floor, not a playthrough duration.'},
    context: ['outputs/rpg-2-star-ocean-the-second_scifi-surveys_pacing-audit_m7_20261013-213603-4c1e9a70.md']},
];

const COUNTING_RULES = [
  {zh: '只计权威字段：steps 状态、m2Expansion 门状态、本表 M7 内容门，以及由已验收台账条目支撑的 approvalLedger 计数。', en: 'Only authoritative fields count: steps status, m2Expansion gate status, this meter\'s M7 content gates, and approvalLedger counters backed by accepted ledger items.'},
  {zh: '概念稿、未批准静态帧、方向认可、仅限范围的静态基准和冒烟／自动测试永远不算视觉验收。', en: 'Concepts, unapproved static frames, direction approvals, scoped static baselines and smoke or automated tests never count as visual acceptance.'},
  {zh: '美术完成后的真人试玩，须在角色与环境美术全部验收后才计入。', en: 'Post-art human playtests count only after both art categories are complete.'},
  {zh: '未改变任何门的任务只记零变化回执；百分比只能随已声明、有证据的门变化而变化。', en: 'A task that changes no gate records a zero-change receipt; the percentage moves only with a claimed, evidenced gate change.'},
  {zh: '权重与分母是固定基线；修改它们属于基线修订，不是任务进度。', en: 'Weights and denominators are a fixed baseline; changing them is a baseline revision, not task progress.'},
];

const round = (value, places) => Math.round(value * 10 ** places) / 10 ** places;
const unique = list => [...new Set(list)];
const ratio = c => c.numerator + '/' + c.denominator;
const isObj = value => value && typeof value === 'object' && !Array.isArray(value);

function readState(file) { return JSON.parse(fs.readFileSync(file, 'utf8')); }
function writeState(file, state) { fs.writeFileSync(file, JSON.stringify(state, null, 2) + '\n', 'utf8'); }

function resolvePointer(doc, pointer) {
  let node = doc;
  for (const part of pointer.split('/').slice(1).map(p => p.replace(/~1/g, '/').replace(/~0/g, '~'))) {
    if (node === null || typeof node !== 'object' || !(part in node)) return undefined;
    node = node[part];
  }
  return node;
}

// Repository evidence: a repo-relative file, optionally with #/json/pointer into that JSON file.
function evidenceProblem(ref, root, state, stateRel) {
  if (typeof ref !== 'string' || !ref.trim()) return 'empty evidence entry';
  if (path.isAbsolute(ref) || ref.includes('..') || ref.includes('\\')) return 'evidence must be a repo-relative path with forward slashes: ' + ref;
  const [rel, pointer] = ref.split('#');
  if (!fs.existsSync(path.join(root, rel))) return 'evidence file not found: ' + rel;
  if (pointer !== undefined) {
    const doc = rel === stateRel ? state : JSON.parse(fs.readFileSync(path.join(root, rel), 'utf8'));
    if (resolvePointer(doc, pointer) === undefined) return 'evidence pointer not found: ' + ref;
  }
  return null;
}

// Validates the authoritative inputs. Returns {errors, warnings}; any error blocks check and record.
function validate(state, meter, opts = {}) {
  const errors = [];
  const warnings = [];
  const root = opts.root || ROOT;
  const stateRel = opts.stateRel || STATE_REL;
  if (!Array.isArray(state.steps)) errors.push('state.steps missing');
  const steps = new Map((state.steps || []).map(step => [step.id, step]));
  for (const step of state.steps || []) {
    if (!STEP_STATUSES.includes(step.status)) errors.push(`unknown status "${step.status}" on step ${step.id}`);
  }
  const core = CATEGORIES[0];
  for (const id of core.stepIds) if (!steps.has(id)) errors.push('missing step ' + id);

  const travel = CATEGORIES[1];
  const gates = state.m2Expansion && state.m2Expansion.gates;
  if (!Array.isArray(gates)) errors.push('m2Expansion.gates missing');
  else {
    const ids = gates.map(g => g.id);
    for (const id of ids) if (!travel.gateIds.includes(id)) errors.push('unknown m2Expansion gate ' + id + ' (not in the fixed 12-gate baseline)');
    for (const id of travel.gateIds) if (!ids.includes(id)) errors.push('missing m2Expansion gate ' + id);
    if (new Set(ids).size !== ids.length) errors.push('duplicate m2Expansion gate id');
    for (const gate of gates) if (!M2_GATE_STATUSES.includes(gate.status)) errors.push(`unknown status "${gate.status}" on m2Expansion gate ${gate.id}`);
  }

  const science = CATEGORIES[2];
  if (meter) {
    const own = (meter.categories || []).find(c => c.id === science.id);
    const list = own && own.gates;
    if (!Array.isArray(list)) errors.push('completionMeter science-playable-content gates missing');
    else {
      const ids = list.map(g => g.id);
      for (const id of ids) if (!science.gateIds.includes(id)) errors.push('unknown science-playable-content gate ' + id);
      for (const id of science.gateIds) if (!ids.includes(id)) errors.push('missing science-playable-content gate ' + id);
      for (const gate of list) {
        if (!SCIENCE_GATE_STATUSES.includes(gate.status)) errors.push(`unknown status "${gate.status}" on science-playable-content gate ${gate.id}`);
        if (gate.status === 'done' && !(Array.isArray(gate.evidence) && gate.evidence.length)) errors.push('science-playable-content gate ' + gate.id + ' is done without evidence');
        for (const ref of gate.evidence || []) { const p = evidenceProblem(ref, root, state, stateRel); if (p) errors.push(gate.id + ': ' + p); }
      }
      const m7 = steps.get('M7');
      const allDone = list.every(g => g.status === 'done');
      if (m7 && m7.status === 'done' && !allDone) errors.push('steps M7 is done but science-playable-content gates are not all done');
      if (m7 && m7.status !== 'done' && allDone) warnings.push('all science-playable-content gates are done but steps M7 is still ' + m7.status);
    }
  }

  const ledger = state.approvalLedger;
  if (!isObj(ledger) || !isObj(ledger.counters)) errors.push('approvalLedger.counters missing');
  else {
    for (const c of CATEGORIES.filter(x => x.kind === 'ledger-counter')) {
      const value = ledger.counters[c.counter];
      const target = ledger.counters[c.target];
      if (!Number.isInteger(value) || value < 0) errors.push(`approvalLedger.counters.${c.counter} must be a non-negative integer`);
      if (target !== c.denominator) errors.push(`approvalLedger.counters.${c.target} is ${target}; the fixed baseline denominator is ${c.denominator}`);
      if (Number.isInteger(value) && value > c.denominator) errors.push(`approvalLedger.counters.${c.counter} exceeds ${c.denominator}`);
    }
    for (const item of ledger.items || []) {
      if (item.acceptanceKind === undefined) continue;
      if (!CATEGORIES.some(c => c.acceptanceKind === item.acceptanceKind)) errors.push(`unknown acceptanceKind "${item.acceptanceKind}" on ledger item ${item.id}`);
    }
  }
  return {errors, warnings};
}

// Accepted ledger items of one acceptance kind; items with concept/unapproved/smoke evidence are rejected, never counted.
function backedUnits(state, kind, warnings) {
  let units = 0;
  const evidence = [];
  for (const item of (state.approvalLedger && state.approvalLedger.items) || []) {
    if (item.acceptanceKind !== kind) continue;
    if (item.status !== 'accepted') { warnings.push(`ledger item ${item.id} has acceptanceKind ${kind} but status ${item.status}; not counted`); continue; }
    const refs = Array.isArray(item.evidence) ? item.evidence : [];
    if (!refs.length) { warnings.push(`ledger item ${item.id} is accepted without evidence; not counted`); continue; }
    const bad = refs.filter(ref => NON_ACCEPTANCE_EVIDENCE.test(ref));
    if (bad.length) { warnings.push(`ledger item ${item.id} cites concept/unapproved/smoke evidence (${bad.join(', ')}); not counted as acceptance`); continue; }
    units += Number.isInteger(item.units) && item.units > 0 ? item.units : 1;
    evidence.push(...refs);
  }
  return {units, evidence};
}

function gateName(gate) { return {zh: gate.zh || gate.id, en: gate.en || gate.id}; }
function nextFromOpen(open, doneText) {
  if (!open.length) return doneText;
  return {zh: '下一道门：' + open.map(g => gateName(g).zh).join('、'), en: 'Next gate: ' + open.map(g => gateName(g).en).join('; ')};
}

const NEXT_COUNTER = {
  'character-art': {zh: '下一道门：创作者在 approvalLedger 中验收第一套可运行的四方向精灵（含移动动画），并登记 acceptanceKind=runtime-sprite 条目。', en: 'Next gate: the creator accepts the first runtime four-direction sprite set (with locomotion) in approvalLedger, recorded as an acceptanceKind runtime-sprite item.'},
  'science-environment-art': {zh: '下一道门：创作者在 640×360 可玩画面中验收下一处科技圈场景画质，并登记 acceptanceKind=scene-visual 条目。', en: 'Next gate: the creator accepts another science-sphere scene-quality gate in the playable 640×360 view, recorded as an acceptanceKind scene-visual item.'},
  'final-integrated-validation': {zh: '下一道门：角色与环境美术全部验收后，完成第一轮全新存档的真人整合试玩（M9）。', en: 'Next gate: after all character and environment art is accepted, complete the first fresh-save integrated human playtest (M9).'},
};

// Recomputes the meter from the authoritative state. `meter` supplies the science gates (the meter's own authoritative record).
function compute(state, meter) {
  const warnings = [];
  const steps = new Map(state.steps.map(step => [step.id, step]));
  const out = [];
  for (const c of CATEGORIES) {
    const base = {id: c.id, zh: c.zh, en: c.en, weight: c.weight};
    let numerator;
    let extra = {};
    let evidence;
    let nextGate;
    if (c.kind === 'steps') {
      const counted = c.stepIds.filter(id => c.countStatuses.includes(steps.get(id).status));
      const open = c.stepIds.filter(id => !counted.includes(id)).map(id => ({id, zh: steps.get(id).title, en: steps.get(id).title}));
      numerator = counted.length;
      extra = {countedGateIds: counted, openGateIds: open.map(g => g.id)};
      evidence = c.stepIds.map(id => 'game/tests/' + id.toLowerCase() + '_smoke.gd');
      nextGate = nextFromOpen(open, {zh: '本类已完成；保持 M1、M3–M6 冒烟测试通过，回退会扣分。', en: 'Category complete; keep the M1 and M3–M6 smoke tests passing. A regression lowers it.'});
    } else if (c.kind === 'm2-gates') {
      const byId = new Map(state.m2Expansion.gates.map(g => [g.id, g]));
      const counted = c.gateIds.filter(id => c.countStatuses.includes(byId.get(id).status));
      const open = c.gateIds.filter(id => !counted.includes(id)).map(id => byId.get(id));
      numerator = counted.length;
      extra = {countedGateIds: counted, openGateIds: open.map(g => g.id)};
      evidence = unique(counted.flatMap(id => byId.get(id).evidence || []));
      nextGate = nextFromOpen(open, {zh: '本类已完成。', en: 'Category complete.'});
    } else if (c.kind === 'meter-gates') {
      const own = meter.categories.find(x => x.id === c.id);
      const byId = new Map(own.gates.map(g => [g.id, g]));
      const gates = c.gateIds.map(id => byId.get(id));
      const counted = gates.filter(g => c.countStatuses.includes(g.status)).map(g => g.id);
      const open = gates.filter(g => !counted.includes(g.id));
      numerator = counted.length;
      extra = {countedGateIds: counted, openGateIds: open.map(g => g.id), gates};
      evidence = unique(gates.filter(g => counted.includes(g.id)).flatMap(g => g.evidence || []));
      nextGate = nextFromOpen(open, {zh: '本类已完成。', en: 'Category complete.'});
    } else {
      const counter = state.approvalLedger.counters[c.counter];
      const backed = backedUnits(state, c.acceptanceKind, warnings);
      numerator = Math.min(counter, backed.units);
      if (counter > backed.units) warnings.push(`${c.id}: approvalLedger.counters.${c.counter}=${counter} but only ${backed.units} accepted ${c.acceptanceKind} unit(s) back it; counting ${numerator}`);
      if (backed.units > counter) warnings.push(`${c.id}: ${backed.units} accepted ${c.acceptanceKind} unit(s) but approvalLedger.counters.${c.counter}=${counter}; counting ${numerator}`);
      if (c.requiresArtComplete && numerator > 0) {
        const art = out.filter(x => x.id === 'character-art' || x.id === 'science-environment-art');
        if (!art.every(x => x.numerator === x.denominator)) {
          warnings.push(`${c.id}: ${numerator} playtest unit(s) held back because character and environment art are not fully accepted`);
          numerator = 0;
        }
      }
      extra = {counterField: 'approvalLedger.counters.' + c.counter, acceptanceKind: c.acceptanceKind};
      evidence = unique([COUNTERS_PTR + '/' + c.counter, ...backed.evidence]);
      nextGate = numerator === c.denominator ? {zh: '本类已完成。', en: 'Category complete.'} : NEXT_COUNTER[c.id];
    }
    out.push({...base, numerator, denominator: c.denominator, ratio: numerator + '/' + c.denominator,
      percent: round(numerator / c.denominator * 100, 1), weightedPoints: round(c.weight * numerator / c.denominator, 2),
      source: {path: c.kind === 'meter-gates' ? 'completionMeter.categories[science-playable-content].gates' : c.kind === 'steps' ? 'steps' : c.kind === 'm2-gates' ? 'm2Expansion.gates' : 'approvalLedger', rule: c.rule},
      ...extra, evidence, nextGate});
  }
  const exact = CATEGORIES.reduce((sum, c, i) => sum + c.weight * out[i].numerator / c.denominator, 0);
  const counters = state.approvalLedger.counters;
  const m9 = steps.get('M9');
  const notCounted = (state.approvalLedger.items || []).filter(item => !(item.status === 'accepted' && item.acceptanceKind)).map(item => ({id: item.id, status: item.status}));
  const formalApproval = {
    zh: '正式批准与加权估算分开：只有创作者记在 approvalLedger 的验收和 M9 两轮真人整合试玩才算批准。本百分比不批准任何素材、场景或里程碑。',
    en: 'Formal approval is separate from this weighted estimate: only creator acceptance recorded in approvalLedger and the two M9 integrated human playtests count as approval. This percentage approves no asset, scene or milestone.',
    mvpFormallyAccepted: Boolean(m9 && m9.status === 'done' && out.every(c => c.numerator === c.denominator)),
    runtimeSpritesAccepted: counters.runtimeSpritesAccepted + '/' + counters.runtimeSpritesTarget,
    sceneVisualsAccepted: counters.sceneVisualsAccepted + '/' + counters.sceneVisualsTarget,
    humanPlaytests: counters.humanPlaytests + '/' + counters.humanPlaytestsTarget,
    scopedApprovalsNotCountedAsAcceptance: notCounted,
    source: COUNTERS_PTR,
  };
  return {percent: round(exact, 1), percentLabel: round(exact, 1).toFixed(1) + '%', weightedPoints: round(exact, 2), categories: out, formalApproval, warnings};
}

const SNAPSHOT_KEYS = ['numerator', 'denominator', 'weight', 'percent', 'weightedPoints', 'countedGateIds', 'evidence', 'nextGate'];
function snapshotDiff(meter, computed) {
  const diffs = [];
  if (meter.percent !== computed.percent) diffs.push(`percent stored ${meter.percent}, recomputed ${computed.percent}`);
  if (meter.percentLabel !== computed.percentLabel) diffs.push(`percentLabel stored ${meter.percentLabel}, recomputed ${computed.percentLabel}`);
  for (const c of computed.categories) {
    const stored = meter.categories.find(x => x.id === c.id);
    if (!stored) { diffs.push('category missing from stored meter: ' + c.id); continue; }
    for (const key of SNAPSHOT_KEYS) if (JSON.stringify(stored[key]) !== JSON.stringify(c[key])) diffs.push(`${c.id}.${key} stored ${JSON.stringify(stored[key])}, recomputed ${JSON.stringify(c[key])}`);
  }
  if (JSON.stringify(meter.formalApproval) !== JSON.stringify(computed.formalApproval)) diffs.push('formalApproval differs from recomputed');
  return diffs;
}

// Changed gate keys between the stored snapshot and the recomputation: "category/gate" for gate lists, "category" for counters.
function gateChanges(meter, computed) {
  const changes = [];
  for (const c of computed.categories) {
    const stored = meter.categories.find(x => x.id === c.id) || {};
    if (c.countedGateIds) {
      const before = stored.countedGateIds || [];
      for (const id of c.countedGateIds.filter(id => !before.includes(id))) changes.push({key: c.id + '/' + id, category: c.id, gate: id, from: 'not_counted', to: 'counted'});
      for (const id of before.filter(id => !c.countedGateIds.includes(id))) changes.push({key: c.id + '/' + id, category: c.id, gate: id, from: 'counted', to: 'not_counted'});
    } else if (stored.numerator !== c.numerator) {
      changes.push({key: c.id, category: c.id, gate: null, from: stored.numerator + '/' + stored.denominator, to: ratio(c)});
    }
  }
  return changes;
}

function categoryOf(id) { return CATEGORIES.find(c => c.id === id); }
function parseClaim(text) {
  const [category, gate, ...rest] = String(text).split('/');
  const c = categoryOf(category);
  if (!c || rest.length) throw new Error('unknown category in --gate ' + text + ' (known: ' + CATEGORIES.map(x => x.id).join(', ') + ')');
  if (c.kind === 'ledger-counter') {
    if (gate !== undefined) throw new Error(`--gate ${text}: ${category} is a ledger counter; claim it as --gate ${category}`);
    return category;
  }
  const ids = c.stepIds || c.gateIds;
  if (gate === undefined) throw new Error(`--gate ${text}: name the gate, e.g. --gate ${category}/${ids[0]}`);
  if (!ids.includes(gate)) throw new Error(`unknown gate ${gate} in ${category} (known: ${ids.join(', ')})`);
  return category + '/' + gate;
}

function stamp(now) { return now.replace(/[-:]/g, '').replace('T', '-').slice(0, 15); }
function meterFields(computed) {
  const {warnings, ...rest} = computed;
  return rest;
}
function storedCategories(computed, meter) {
  return computed.categories.map(c => {
    if (c.id !== 'science-playable-content') return c;
    const own = meter.categories.find(x => x.id === c.id);
    return {...c, gates: own.gates};
  });
}

function buildInitialMeter(state, now) {
  const seed = {categories: [{id: 'science-playable-content', gates: SCIENCE_GATE_BASELINE.map(g => ({...g}))}]};
  const computed = compute(state, seed);
  const closeoutId = 'closeout-' + stamp(now) + '-' + crypto.randomBytes(4).toString('hex');
  return {
    id: METER_ID,
    schemaVersion: 1,
    kind: 'weighted_delivery_estimate',
    zh: 'MVP 加权交付估算（不是正式批准）',
    en: 'MVP weighted delivery estimate (not formal approval)',
    updatedAt: now,
    percent: computed.percent,
    percentLabel: computed.percentLabel,
    weightedPoints: computed.weightedPoints,
    weightTotal: CATEGORIES.reduce((sum, c) => sum + c.weight, 0),
    countingRules: COUNTING_RULES,
    formalApproval: computed.formalApproval,
    categories: storedCategories(computed, seed),
    updater: 'tools/' + path.basename(__filename),
    lastUpdated: {at: now, closeoutId, percent: computed.percent},
    taskCloseouts: [{
      id: closeoutId, recordedAt: now, kind: 'baseline',
      title: {zh: '建立 MVP 加权完成度基线', en: 'Establish the MVP weighted completion baseline'},
      impact: {changed: false, percentBefore: null, percentAfter: computed.percent, deltaPoints: 0, gateChanges: [], categoryChanges: []},
      evidence: [STATE_REL + '#/m2Expansion/gates', COUNTERS_PTR, 'game/tests/m7_smoke.gd'],
    }],
  };
}

function record(state, opts, ctx) {
  const meter = state.completionMeter;
  if (!meter) throw new Error('completionMeter missing; run init first');
  const claims = unique((opts.gates || []).map(parseClaim));
  const working = JSON.parse(JSON.stringify(meter));
  const science = working.categories.find(c => c.id === 'science-playable-content');
  for (const spec of opts.setGates || []) {
    const match = /^([^/=]+)\/([^=]+)=(.+)$/.exec(spec);
    if (!match) throw new Error('--set-gate expects <category>/<gate>=<status>: ' + spec);
    const [, category, gate, status] = match;
    const c = categoryOf(category);
    if (!c) throw new Error('unknown category in --set-gate ' + spec);
    if (c.kind !== 'meter-gates') throw new Error(`--set-gate ${spec}: ${category} is derived from ${c.kind === 'steps' ? 'steps' : c.kind === 'm2-gates' ? 'm2Expansion.gates' : 'approvalLedger'}; change that authoritative field instead`);
    const target = science.gates.find(g => g.id === gate);
    if (!target) throw new Error(`unknown gate ${gate} in ${category} (known: ${c.gateIds.join(', ')})`);
    if (!SCIENCE_GATE_STATUSES.includes(status)) throw new Error(`unknown status ${status} for ${category}/${gate} (known: ${SCIENCE_GATE_STATUSES.join(', ')})`);
    target.status = status;
    if (status === 'done') target.evidence = unique([...(target.evidence || []), ...(opts.evidence || [])]);
  }
  const check = validate(state, working, ctx);
  if (check.errors.length) throw new Error('authoritative state invalid:\n  ' + check.errors.join('\n  '));
  for (const ref of opts.evidence || []) { const p = evidenceProblem(ref, ctx.root, state, ctx.stateRel); if (p) throw new Error(p); }

  const computed = compute(state, working);
  const changes = gateChanges(meter, computed);
  const baselineChanges = computed.categories.map(c => ({c, stored: meter.categories.find(x => x.id === c.id)}))
    .filter(({c, stored}) => stored.denominator !== c.denominator)
    .map(({c, stored}) => ({category: c.id, field: 'denominator', from: stored.denominator, to: c.denominator}));
  if (baselineChanges.length && !opts.baselineRevision) throw new Error('fixed baseline denominator changed (' + baselineChanges.map(b => `${b.category} ${b.from} -> ${b.to}`).join(', ') + '); record it with --baseline-revision');
  if (opts.baselineRevision && !baselineChanges.length) throw new Error('--baseline-revision given but no baseline denominator changed');
  if (opts.baselineRevision && changes.length) throw new Error('a baseline revision may not change counts; record count changes in a separate closeout: ' + changes.map(c => c.key).join(', '));
  const changedKeys = changes.map(c => c.key);
  const unclaimed = changedKeys.filter(key => !claims.includes(key));
  const unchanged = claims.filter(key => !changedKeys.includes(key));
  if (unchanged.length) throw new Error('claimed gate did not change in the authoritative state, so no progress is recorded: ' + unchanged.join(', '));
  if (unclaimed.length) throw new Error('authoritative state changed without a claim; pass --gate for each with evidence, or revert: ' + unclaimed.join(', '));
  if (changes.length && !(opts.evidence || []).length) throw new Error('a gate change needs at least one --evidence path');
  const visualClaims = changes.filter(c => categoryOf(c.category).kind === 'ledger-counter');
  const badEvidence = (opts.evidence || []).filter(ref => NON_ACCEPTANCE_EVIDENCE.test(ref));
  if (visualClaims.length && badEvidence.length) throw new Error('concept, unapproved or smoke-test evidence cannot back an acceptance count: ' + badEvidence.join(', '));
  if (!opts.titleEn && !opts.titleZh) throw new Error('record needs --title-en and/or --title-zh');

  const now = opts.now;
  const closeoutId = 'closeout-' + stamp(now) + '-' + crypto.randomBytes(4).toString('hex');
  const categoryChanges = computed.categories.map(c => ({c, stored: meter.categories.find(x => x.id === c.id)}))
    .filter(({c, stored}) => stored.numerator !== c.numerator)
    .map(({c, stored}) => ({id: c.id, before: stored.numerator + '/' + stored.denominator, after: ratio(c), weightedPointsBefore: stored.weightedPoints, weightedPointsAfter: c.weightedPoints}));
  const closeout = {
    id: closeoutId, recordedAt: now, kind: opts.baselineRevision ? 'baseline-revision' : 'task',
    title: {zh: opts.titleZh || null, en: opts.titleEn || null},
    impact: {changed: categoryChanges.length > 0, percentBefore: meter.percent, percentAfter: computed.percent,
      deltaPoints: round(computed.weightedPoints - meter.weightedPoints, 2), gateChanges: changes, categoryChanges,
      ...(opts.baselineRevision ? {baselineChanges} : {})},
    evidence: unique(opts.evidence || []),
  };
  if (computed.warnings.length) closeout.warnings = computed.warnings;
  const next = {...meter, ...meterFields(computed), updatedAt: now, categories: storedCategories(computed, working),
    lastUpdated: {at: now, closeoutId, percent: computed.percent}, taskCloseouts: [...meter.taskCloseouts, closeout]};
  state.completionMeter = next;
  if (!state.updatedAt || state.updatedAt < now) state.updatedAt = now;
  return {closeout, computed};
}

function parseArgs(argv) {
  const opts = {command: argv[0] && !argv[0].startsWith('--') ? argv[0] : 'check', gates: [], setGates: [], evidence: []};
  const multi = {'--gate': 'gates', '--set-gate': 'setGates', '--evidence': 'evidence'};
  const single = {'--state': 'state', '--now': 'now', '--title-en': 'titleEn', '--title-zh': 'titleZh'};
  for (let i = opts.command === argv[0] ? 1 : 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--dry-run') opts.dryRun = true;
    else if (arg === '--baseline-revision') opts.baselineRevision = true;
    else if (multi[arg] && i + 1 < argv.length) opts[multi[arg]].push(argv[++i]);
    else if (single[arg] && i + 1 < argv.length) opts[single[arg]] = argv[++i];
    else throw new Error('unknown or incomplete argument: ' + arg);
  }
  opts.now = opts.now || new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(opts.now)) throw new Error('--now must be an ISO UTC time like 2026-10-16T03:30:00Z');
  return opts;
}

function printSummary(meter, warnings) {
  console.log(`${meter.en}: ${meter.percent.toFixed(1)}% (${meter.zh})`);
  for (const c of meter.categories) console.log(`  ${c.id.padEnd(28)} ${String(c.weight).padStart(2)}%  ${ratio(c).padStart(5)}  ${c.percent.toFixed(1).padStart(5)}%  +${c.weightedPoints}  ${c.nextGate.en}`);
  console.log('  formal approval: MVP accepted = ' + meter.formalApproval.mvpFormallyAccepted + '; sprites ' + meter.formalApproval.runtimeSpritesAccepted + ', scenes ' + meter.formalApproval.sceneVisualsAccepted + ', human playtests ' + meter.formalApproval.humanPlaytests);
  for (const w of warnings) console.log('WARN ' + w);
}

function main(argv) {
  const opts = parseArgs(argv);
  const file = path.resolve(opts.state || path.join(ROOT, STATE_REL));
  const ctx = {root: ROOT, stateRel: path.relative(ROOT, file).split(path.sep).join('/')};
  const state = readState(file);
  if (opts.command === 'init') {
    if (state.completionMeter) throw new Error('completionMeter already exists; use record');
    const meter = buildInitialMeter(state, opts.now);
    const check = validate(state, meter, ctx);
    if (check.errors.length) throw new Error('authoritative state invalid:\n  ' + check.errors.join('\n  '));
    state.completionMeter = meter;
    if (!state.updatedAt || state.updatedAt < opts.now) state.updatedAt = opts.now;
    if (!opts.dryRun) writeState(file, state);
    printSummary(meter, check.warnings);
    console.log((opts.dryRun ? 'DRY RUN ' : '') + 'INIT ' + meter.lastUpdated.closeoutId);
  } else if (opts.command === 'check') {
    const meter = state.completionMeter;
    if (!meter) throw new Error('completionMeter missing; run init first');
    const check = validate(state, meter, ctx);
    if (check.errors.length) throw new Error('authoritative state invalid:\n  ' + check.errors.join('\n  '));
    const computed = compute(state, meter);
    const diffs = snapshotDiff(meter, computed);
    printSummary(meter, [...check.warnings, ...computed.warnings]);
    if (diffs.length) throw new Error('stored meter is stale; record a task closeout:\n  ' + diffs.join('\n  '));
    console.log('CHECK OK ' + meter.percent.toFixed(1) + '% (last closeout ' + meter.lastUpdated.closeoutId + ')');
  } else if (opts.command === 'record') {
    const {closeout} = record(state, opts, ctx);
    if (!opts.dryRun) writeState(file, state);
    printSummary(state.completionMeter, closeout.warnings || []);
    console.log(`${opts.dryRun ? 'DRY RUN ' : ''}RECORDED ${closeout.id} ${closeout.impact.percentBefore.toFixed(1)}% -> ${closeout.impact.percentAfter.toFixed(1)}% (${closeout.impact.changed ? 'changed: ' + closeout.impact.gateChanges.map(c => c.key).join(', ') : 'zero change'})`);
  } else {
    throw new Error('unknown command ' + opts.command + ' (check, init, record)');
  }
}

module.exports = {CATEGORIES, SCIENCE_GATE_BASELINE, STATE_REL, validate, compute, record, gateChanges, snapshotDiff, parseClaim, buildInitialMeter};

if (require.main === module) {
  try { main(process.argv.slice(2)); } catch (error) { console.error('ERROR ' + error.message); process.exit(1); }
}
