#!/usr/bin/env node
// Deterministic checker for the 应变 (adaptive) ten-node job-tree PROPOSAL
//   outputs/rpg-2-star-ocean-the-second_adaptive-job-trees_ten-node-skill-proposal_unapproved-v01_20261016-112114-ec58fa23.json
// Read-only: it reads the proposal and its recorded sources and never writes a file.
//
// Usage (from any directory):
//   node tools/<this file>                      check the proposal; also confirm its embedded results match
//   node tools/<this file> --proposal <path>    check another copy (used for mutation tests)
//   node tools/<this file> --json               print the recomputed check list as JSON
// Exit 0 only when every check passes and the embedded `validation` block equals the recomputed one
// (same check ids, results and details; `ranAt` is ignored).
//
// The generator that assembled the proposal requires runChecks() from this file to fill `validation`, so the
// embedded results and a later run come from the same code. Status: PROPOSAL tooling, unapproved.
'use strict';
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const {TEXT_HASH, textSha256, sha256} = require(path.join(ROOT, 'tools', 'rpg-2-star-ocean-the-second_content-hash_text-lf-v1_m8-v01_20261014-224905-022124e7.js'));
const PROPOSAL_REL = 'outputs/rpg-2-star-ocean-the-second_adaptive-job-trees_ten-node-skill-proposal_unapproved-v01_20261016-112114-ec58fa23.json';

const SERIES_IDS = ['archery', 'firearms', 'skirmish', 'beast', 'merchant'];
const EPS = 1e-9;

const readJson = rel => JSON.parse(fs.readFileSync(path.join(ROOT, rel), 'utf8'));
const fmt = v => String(Math.round(v * 1e6) / 1e6);

// ---- minimal JSON Schema subset (type, enum, const, pattern, required, properties, additionalProperties:false,
// items, minItems, maxItems, minimum, maximum, exclusiveMinimum, $ref to #/$defs/*). Enough for the embedded schema.
function typeOf(v) {
  if (v === null) return 'null';
  if (Array.isArray(v)) return 'array';
  if (typeof v === 'number') return Number.isInteger(v) ? 'integer' : 'number';
  return typeof v;
}
function schemaErrors(value, schema, root, at, out) {
  if (schema.$ref) {
    const name = schema.$ref.replace('#/$defs/', '');
    return schemaErrors(value, root.$defs[name], root, at, out);
  }
  if (schema.type) {
    const types = Array.isArray(schema.type) ? schema.type : [schema.type];
    const t = typeOf(value);
    if (!types.includes(t) && !(t === 'integer' && types.includes('number'))) { out.push(`${at}: type ${t} not in ${types}`); return out; }
  }
  if ('const' in schema && JSON.stringify(value) !== JSON.stringify(schema.const)) out.push(`${at}: not const ${JSON.stringify(schema.const)}`);
  if (schema.enum && !schema.enum.some(e => JSON.stringify(e) === JSON.stringify(value))) out.push(`${at}: ${JSON.stringify(value)} not in enum`);
  if (schema.pattern && typeof value === 'string' && !new RegExp(schema.pattern).test(value)) out.push(`${at}: pattern ${schema.pattern}`);
  if (typeof value === 'number') {
    if ('minimum' in schema && value < schema.minimum) out.push(`${at}: < minimum`);
    if ('maximum' in schema && value > schema.maximum) out.push(`${at}: > maximum`);
    if ('exclusiveMinimum' in schema && value <= schema.exclusiveMinimum) out.push(`${at}: <= exclusiveMinimum`);
  }
  if (Array.isArray(value)) {
    if ('minItems' in schema && value.length < schema.minItems) out.push(`${at}: minItems`);
    if ('maxItems' in schema && value.length > schema.maxItems) out.push(`${at}: maxItems`);
    if (schema.items) value.forEach((item, i) => schemaErrors(item, schema.items, root, `${at}[${i}]`, out));
  }
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    for (const key of schema.required || []) if (!(key in value)) out.push(`${at}: missing ${key}`);
    const props = schema.properties || {};
    for (const [key, sub] of Object.entries(props)) if (key in value) schemaErrors(value[key], sub, root, `${at}.${key}`, out);
    if (schema.additionalProperties === false) for (const key of Object.keys(value)) if (!(key in props)) out.push(`${at}: extra ${key}`);
  }
  return out;
}

function nodeTexts(node) {
  const parts = [node.name, node.nameEn, node.summaryEn, node.target, node.baseEffect, ...Object.values(node.rankProgression || {})];
  for (const s of node.scaling || []) parts.push(s.label, s.unit);
  if (node.aiBehavior) parts.push(node.aiBehavior.condition, node.aiBehavior.avoid);
  if (node.scienceMvpUtility) parts.push(node.scienceMvpUtility.name, node.scienceMvpUtility.effect);
  if (node.passiveBounds) parts.push(node.passiveBounds.trigger);
  if (node.runtimeNote) parts.push(node.runtimeNote);
  return parts.filter(p => typeof p === 'string').join('\n');
}

function rankText(s, i) {
  return `${s.label} ${fmt(s.values[i])}${s.unit}（+${fmt(s.values[i] - s.values[i - 1])}）`;
}

// JP cost for raising a skill to `rank` (2..5) at an aptitude score; same formula as GrowthRules.jp_cost.
function jpCost(base, score) {
  const s = Math.min(100, Math.max(60, score));
  return Math.ceil(base * (1 - 0.5 * (s - 60) / 40));
}

function economics(p) {
  const base = p.jpProposal.rankUpgradeBaseJp;
  const ranks = ['2', '3', '4', '5'];
  const nodesPerSeries = 10;
  const rows = p.economics.aptitudeScores.map(score => {
    const perRank = Object.fromEntries(ranks.map(r => [r, jpCost(base[r], score)]));
    const perSkill = ranks.reduce((a, r) => a + perRank[r], 0);
    return {aptitude: score, perRank, perSkill, perSeries: perSkill * nodesPerSeries};
  });
  const rewards = p.economics.runtimeJpRewards;
  const at = score => rows.find(r => r.aptitude === score);
  const battles = [60, 100].map(score => ({
    aptitude: score,
    sentryWinsPerStage: Math.ceil(at(score).perSkill * 2 / rewards.sentryWin),
    patrolWinsPerStage: Math.ceil(at(score).perSkill * 2 / rewards.patrolWin),
    sentryWinsPerSeries: Math.ceil(at(score).perSeries / rewards.sentryWin),
    patrolWinsPerSeries: Math.ceil(at(score).perSeries / rewards.patrolWin),
  }));
  return {rows, battles};
}

function curveShape(table) {
  const v = ['2', '3', '4', '5'].map(k => table[k]);
  const inc = v.slice(1).map((x, i) => x - v[i]);
  const ratios = v.slice(1).map((x, i) => Math.round(x / v[i] * 1000) / 1000);
  return {values: v, increments: inc, successiveRatios: ratios, total: v.reduce((a, b) => a + b, 0),
    rank5OverRank2: Math.round(v[3] / v[0] * 1000) / 1000};
}

function jaccard(a, b) {
  const A = new Set(a), B = new Set(b);
  const inter = [...A].filter(x => B.has(x)).length;
  return inter / new Set([...A, ...B]).size;
}

function runChecks(p, opts = {}) {
  const checks = [];
  const add = (id, description, ok, detail) => checks.push({id, description, result: ok ? 'pass' : 'fail', detail});
  const series = p.series || [];
  const nodes = series.flatMap(s => s.nodes || []);
  const roster = readJson(p.sources.approvedRoster.path);
  const rosterById = Object.fromEntries(roster.series.map(s => [s.id, s]));

  // 1 source locks
  {
    const bad = [], info = [];
    for (const [key, src] of Object.entries(p.sources)) {
      const now = textSha256(fs.readFileSync(path.join(ROOT, src.path)));
      if (src.hashAlgorithm !== TEXT_HASH) bad.push(`${key}: algorithm`);
      else if (now !== src.sha256) (src.lockEnforced ? bad : info).push(`${key}${src.lockEnforced ? '' : '（仅记录，不强制）'} 已变化`);
    }
    const enforced = Object.values(p.sources).filter(s => s.lockEnforced).length;
    add('source-locks', '强制锁定的来源文件（已批准名单、被取代草案、研学提案、决定记录、运行时骨架目录）与记录的 sha256-text-lf-v1 一致；Game Bible 正被其他工作流编辑，只记录不强制',
      bad.length === 0, bad.length ? bad.join('; ') : `${enforced} 个强制锁定一致${info.length ? '；' + info.join('; ') : ''}`);
  }

  // 2 series set
  {
    const ids = series.map(s => s.id);
    const adaptive = roster.series.filter(s => s.aptitude === '应变').map(s => s.id);
    const ok = JSON.stringify(ids) === JSON.stringify(SERIES_IDS) && JSON.stringify(adaptive) === JSON.stringify(SERIES_IDS)
      && series.every(s => s.aptitude === '应变');
    add('series-set', '恰好 5 条系列，且正是已批准名单中天分为应变的 5 条（顺序一致）', ok, ids.join(', '));
  }

  // 3 approved text verbatim
  {
    const bad = [];
    for (const s of series) {
      const r = rosterById[s.id];
      if (!r) { bad.push(`${s.id}: not in roster`); continue; }
      for (const k of ['name', 'en', 'role', 'finalQuest']) if (s[k] !== r[k]) bad.push(`${s.id}.${k}`);
      if (JSON.stringify(s.stages) !== JSON.stringify(r.stages)) bad.push(`${s.id}.stages`);
      for (const n of s.nodes) if (n.stageName !== r.stages[n.stage - 1]) bad.push(`${n.id}.stageName`);
    }
    add('approved-text-verbatim', '系列名、英文名、定位、五阶名称、终阶任务与已批准名单逐字一致；每个节点的 stageName 与其阶名称逐字一致',
      bad.length === 0, bad.length ? bad.join('; ') : `5 系列 × (名称 + 英文名 + 定位 + 5 阶 + 终阶任务) 逐字一致；${nodes.length} 个 stageName 一致`);
  }

  // 4 ten nodes, two per stage
  {
    const bad = [];
    for (const s of series) {
      if (s.nodes.length !== 10) bad.push(`${s.id}: ${s.nodes.length} nodes`);
      for (let st = 1; st <= 5; st++) {
        const slots = s.nodes.filter(n => n.stage === st).map(n => n.slot).sort().join(',');
        if (slots !== '1,2') bad.push(`${s.id} stage ${st}: slots ${slots}`);
      }
      s.nodes.forEach((n, i) => { if (n.id.indexOf(`_n${String(i + 1).padStart(2, '0')}_`) < 0 || n.stage !== Math.floor(i / 2) + 1 || n.slot !== i % 2 + 1) bad.push(`${n.id}: order`); });
    }
    add('ten-nodes-two-per-stage', '每系列恰好 10 个节点，按 n01–n10 排列，5 阶各 2 个（slot 1、2）；合计 50 个', bad.length === 0 && nodes.length === 50,
      bad.length ? bad.join('; ') : `5 × 10 = ${nodes.length}；每阶 2 个`);
  }

  // 5 schema
  {
    const errs = schemaErrors(p, p.schema, p.schema, '$', []);
    add('node-schema', '整个文件符合内嵌 JSON Schema（含 $defs.node 的必填字段、类型、枚举、常量与 id 格式；本脚本自带子集校验器，不用外部库）',
      errs.length === 0, errs.length ? errs.slice(0, 8).join('; ') + (errs.length > 8 ? ` …(+${errs.length - 8})` : '') : `${nodes.length}/${nodes.length} 节点与文件结构通过`);
  }

  // 6 distinct + collisions
  {
    const dup = arr => arr.filter((x, i) => arr.indexOf(x) !== i);
    const d = [...dup(nodes.map(n => n.id)), ...dup(nodes.map(n => n.name)), ...dup(nodes.map(n => n.nameEn.toLowerCase()))];
    const research = readJson(p.sources.researchTenNodeProposal.path);
    const rNames = new Set(research.series.flatMap(s => s.nodes.flatMap(n => [n.name, n.nameEn.toLowerCase()])));
    const gbText = fs.readFileSync(path.join(ROOT, p.sources.gameBibleState.path), 'utf8');
    const personal = new Set();
    for (const re of [/独有技能——([^：:]+)[：:]/g, /专属个人技能提案——([^：:]+)[：:]/g, /个人技能「([^」]+)」/g]) for (const m of gbText.matchAll(re)) personal.add(m[1].trim());
    const hits = nodes.filter(n => rNames.has(n.name) || rNames.has(n.nameEn.toLowerCase()) || personal.has(n.name)).map(n => n.id);
    add('distinct-nodes', '50 个节点的 id、中文名、英文名全局唯一；不与研学 50 节点重名，也不与 Game Bible 中任何角色个人技能重名',
      d.length === 0 && hits.length === 0, d.length || hits.length ? [...d, ...hits].join('; ')
        : `${nodes.length} 个 id / 中文名 / 英文名唯一；对照研学节点 ${research.series.flatMap(s => s.nodes).length} 个、个人技能名 ${personal.size} 个，0 重名`);
  }

  // 7 unlock and rank rules
  {
    const bad = [];
    for (const n of nodes) {
      const u = n.unlock || {};
      if (u.onStageEntry !== true || u.jpCost !== 0 || u.requiresFinalQuest !== (n.stage === 5)) bad.push(n.id);
      if (n.maxRank !== 5) bad.push(`${n.id}: maxRank`);
      if ('branch' in n || 'exclusiveWith' in n) bad.push(`${n.id}: branch`);
    }
    const keys = Object.keys(p.jpProposal.rankUpgradeBaseJp).join(',');
    if (keys !== '2,3,4,5') bad.push(`jp keys ${keys}`);
    if (p.jpProposal.unlockJp !== 0) bad.push('unlockJp');
    if (p.rules.allBranchesLearnable == null) bad.push('rules.allBranchesLearnable');
    add('unlock-and-rank-rules', '每个节点进入该阶即以第 1 级开放（jpCost 0），只有第 5 阶节点另需终阶任务；最高 5 级；JP 表只含第 2–5 级；没有任何分支或互斥字段',
      bad.length === 0, bad.length ? bad.join('; ') : `${nodes.length}/${nodes.length}；JP 表键 = 2,3,4,5；0 个分支字段`);
  }

  // 8 active / passive / energy bands
  {
    const bands = p.validationParameters.energyBandsByStage;
    const bad = [], tally = [];
    for (const s of series) {
      let a = 0, ps = 0;
      for (const n of s.nodes) {
        if (n.type === 'active') {
          a++;
          const [lo, hi] = bands[String(n.stage)];
          if (!Number.isInteger(n.energyCost) || n.energyCost < lo || n.energyCost > hi) bad.push(`${n.id}: energy ${n.energyCost} not in ${lo}-${hi}`);
          if (!(n.cooldownSec > 0)) bad.push(`${n.id}: cooldown`);
          if (n.typeZh !== '主动') bad.push(`${n.id}: typeZh`);
        } else {
          ps++;
          if (n.energyCost !== null || n.cooldownSec !== null || n.typeZh !== '被动') bad.push(`${n.id}: passive fields`);
        }
      }
      for (let st = 1; st <= 5; st++) if (!s.nodes.some(n => n.stage === st && n.type === 'active')) bad.push(`${s.id} stage ${st}: no active`);
      if (a < 5 || ps < 2) bad.push(`${s.id}: ${a}A/${ps}P`);
      tally.push(`${s.id} ${a}A/${ps}P`);
    }
    add('active-passive-energy', '主动技能有按阶区间的整数能量消耗与冷却，被动技能二者皆为 null；每系列 ≥5 主动、≥2 被动，每阶至少 1 个主动',
      bad.length === 0, bad.length ? bad.join('; ') : tally.join('; '));
  }

  // 9 non-exponential ranks
  {
    const maxRatio = p.validationParameters.rank5ToRank1MaxRatio;
    const bad = [];
    let worst = 0, worstId = '';
    for (const n of nodes) {
      for (const s of n.scaling) {
        const v = s.values;
        const steps = v.slice(1).map((x, i) => x - v[i]);
        if (steps.some(d => d <= 0)) bad.push(`${n.id}.${s.key}: not increasing`);
        if (steps.some((d, i) => i > 0 && d > steps[i - 1] + EPS)) bad.push(`${n.id}.${s.key}: accelerating`);
        const r = v[4] / v[0];
        if (r > maxRatio + EPS) bad.push(`${n.id}.${s.key}: r5/r1 ${r.toFixed(2)}`);
        if (r > worst) { worst = r; worstId = n.id; }
      }
      const main = n.scaling[0];
      for (let i = 1; i < 5; i++) if (n.rankProgression[String(i + 1)] !== rankText(main, i)) bad.push(`${n.id}: rankProgression ${i + 1}`);
      if (!n.baseEffect.includes(fmt(main.values[0]))) bad.push(`${n.id}: baseEffect lacks rank-1 value ${fmt(main.values[0])}`);
    }
    add('non-exponential-ranks', '所有等级数值严格递增，步长固定或递减（无加速增长），第 5 级 / 第 1 级 ≤ 2；rankProgression 文本由主数值逐级生成；baseEffect 写出第 1 级数值；能量与冷却为单一值',
      bad.length === 0, bad.length ? bad.join('; ') : `全部为固定或递减步长；最大 r5/r1 = ${worst.toFixed(2)}（${worstId}）`);
  }

  // 10 passive bounds (no permanent unconditional combat passive)
  {
    const bad = [], kinds = {nonCombat: 0, perBattle: 0, windowed: 0, consumedStacks: 0};
    for (const n of nodes.filter(x => x.type === 'passive')) {
      const b = n.passiveBounds;
      if (!b || typeof b.trigger !== 'string' || b.trigger.length < 2) { bad.push(`${n.id}: no trigger`); continue; }
      if (b.nonCombat) { kinds.nonCombat++; continue; }
      if (Number.isInteger(b.maxTriggersPerBattle) && b.maxTriggersPerBattle >= 1 && b.maxTriggersPerBattle <= p.validationParameters.passiveMaxTriggersPerBattle) { kinds.perBattle++; continue; }
      if (b.effectDurationSec > 0 && b.effectDurationSec <= p.validationParameters.passiveMaxWindowSec && b.internalCooldownSec >= b.effectDurationSec) { kinds.windowed++; continue; }
      if (Number.isInteger(b.maxStacks) && b.consumedOnUse === true) { kinds.consumedStacks++; continue; }
      bad.push(`${n.id}: unbounded`);
    }
    for (const n of nodes.filter(x => x.type === 'active')) if ('passiveBounds' in n) bad.push(`${n.id}: active with passiveBounds`);
    const total = nodes.filter(x => x.type === 'passive').length;
    add('passive-bounds', `每个被动都有触发条件，且属于下列之一：非战斗（经营／交易）、每场次数上限（≤ ${p.validationParameters.passiveMaxTriggersPerBattle}）、短窗口（≤ ${p.validationParameters.passiveMaxWindowSec} 秒且内置冷却 ≥ 窗口）、或用后清空的层数；没有常驻无条件战斗加成`,
      bad.length === 0, bad.length ? bad.join('; ') : `${total} 个被动：非战斗 ${kinds.nonCombat}、每场上限 ${kinds.perBattle}、短窗口 ${kinds.windowed}、用后清空层数 ${kinds.consumedStacks}`);
  }

  // 11 energy transfer / refund caps
  {
    const bad = [], seen = [];
    for (const n of nodes) {
      if (n.energyReturn) bad.push(`${n.id}: refund node (none expected)`);
      const t = n.energyTransfer;
      if (!t) continue;
      seen.push(n.id);
      if (n.type === 'active' && t.casterCost !== n.energyCost) bad.push(`${n.id}: casterCost ≠ energyCost`);
      if (t.kind === 'ratio-pay') { if (!(t.casterPaysRatio > 1)) bad.push(`${n.id}: pay ratio`); }
      else if (!(t.maxAllyGainPerCast < t.casterCost)) bad.push(`${n.id}: gain ${t.maxAllyGainPerCast} ≥ cost ${t.casterCost}`);
    }
    add('energy-transfer-capped', '没有凭空返还能量的节点；调配能量的节点每次让队友获得或节省的总量都少于施放者付出的能量（按比例代付者代付比例 > 1）',
      bad.length === 0, bad.length ? bad.join('; ') : `0 个返还节点；${seen.length} 个调配节点均净亏：${seen.join(', ')}`);
  }

  // 12 stacking caps
  {
    const caps = p.validationParameters.stackingCapsPct;
    const bad = [], sums = {};
    for (const s of series) for (const n of s.nodes) for (const c of n.caps || []) {
      if (!(c.category in caps)) { bad.push(`${n.id}: unknown cap ${c.category}`); continue; }
      if (c.scalingKey) {
        const sc = n.scaling.find(x => x.key === c.scalingKey);
        if (!sc || Math.abs(sc.values[4] - c.rank5Value) > EPS) bad.push(`${n.id}: cap value ≠ rank 5 of ${c.scalingKey}`);
      }
      if (c.rank5Value > caps[c.category]) bad.push(`${n.id}: ${c.category} ${c.rank5Value} > ${caps[c.category]}`);
      const k = `${s.id}.${c.category}`;
      sums[k] = (sums[k] || 0) + c.rank5Value;
    }
    for (const [k, v] of Object.entries(sums)) if (v > caps[k.split('.')[1]] + EPS) bad.push(`${k} sum ${v}`);
    const top = Object.entries(sums).map(([k, v]) => `${k}=${fmt(v)}/${caps[k.split('.')[1]]}`).join(', ');
    add('stacking-caps', '带增减益的节点按类别登记第 5 级数值；单节点与同系列全部节点同时生效的最坏合计都不超过提案的全来源上限',
      bad.length === 0, bad.length ? bad.join('; ') : top);
  }

  // 13 battlefield range
  {
    const max = p.validationParameters.battlefieldMaxSeparationPx;
    const bad = nodes.filter(n => n.rangePx !== null && !(n.rangePx > 0 && n.rangePx <= max)).map(n => `${n.id}: ${n.rangePx}`);
    add('battlefield-range', `所有射程为横向像素且不超过固定战场的最大横向间距 ${max} px（x 28–612）；null 表示自身或全场`,
      bad.length === 0, bad.length ? bad.join('; ') : `${nodes.filter(n => n.rangePx !== null).length} 个有射程节点，最大 ${Math.max(...nodes.map(n => n.rangePx || 0))} px`);
  }

  // 14 banned terrain / jump / stealth terms
  {
    const terms = p.validationParameters.bannedTerms;
    const hits = [];
    for (const n of nodes) { const t = nodeTexts(n).toLowerCase(); for (const w of terms) if (t.includes(w.toLowerCase())) hits.push(`${n.id}:${w}`); }
    add('no-terrain-elevation-jump-stealth', '节点文本（名称、效果、等级文本、AI、实用效果）不含地形、高低差、障碍、掩体、跳跃、潜入／隐身相关词（规则说明本身不在扫描范围内）',
      hits.length === 0, hits.length ? hits.join('; ') : `${terms.length} 个禁用词，${nodes.length} 个节点 0 命中`);
  }

  // 15 merchant: no goods carried, commerce context declared
  {
    const terms = p.validationParameters.merchantBannedTerms;
    const m = series.find(s => s.id === 'merchant');
    const bad = [];
    let commerce = 0;
    for (const n of m ? m.nodes : []) {
      const t = nodeTexts(n).toLowerCase();
      for (const w of terms) if (t.includes(w.toLowerCase())) bad.push(`${n.id}:${w}`);
      if (n.commerceContext) { commerce++; if (!['stationed', 'activeParty', 'stationedOrActiveParty', 'recall'].includes(n.commerceContext)) bad.push(`${n.id}: context`); }
    }
    if (!m || !m.commerceModel) bad.push('merchant.commerceModel');
    add('merchant-no-goods', '行商节点不出现随身货物、背包、道具或消耗品；经营类节点都写明生效场合（驻守／上场／召回）；系列带 commerceModel 说明',
      bad.length === 0, bad.length ? bad.join('; ') : `10 个行商节点 0 命中 ${terms.length} 个词；经营类 ${commerce} 个、战斗调配类 ${10 - commerce} 个`);
  }

  // 16 beast companions are living, not automata
  {
    const terms = p.validationParameters.beastAutomataTerms;
    const b = series.find(s => s.id === 'beast');
    const bad = [];
    for (const n of b ? b.nodes : []) {
      const t = nodeTexts(n);
      if (!t.includes('兽伴')) bad.push(`${n.id}: no 兽伴`);
      for (const w of terms) if (t.toLowerCase().includes(w.toLowerCase())) bad.push(`${n.id}:${w}`);
    }
    const model = b && b.companionModel;
    for (const k of ['nature', 'stamina', 'withdraw', 'notRepairable', 'cueResponse', 'temperaments', 'wildCreatures', 'contrastWithAutomata']) if (!model || !model[k]) bad.push(`companionModel.${k}`);
    add('beast-living-companion', '驯兽 10 个节点都以“兽伴”为对象，不出现机偶／维修／部署／模式等机械词；系列带 companionModel（体力、退场休整、不可维修、哨音反应、性情、不强制控制野生动物、与机偶对照）',
      bad.length === 0, bad.length ? bad.join('; ') : `10/10 节点提到兽伴；${terms.length} 个机械词 0 命中；companionModel 8 项齐全`);
  }

  // 17 distinct roles
  {
    const bad = [];
    const sets = series.map(s => ({id: s.id, roles: s.nodes.map(n => n.tacticalRole)}));
    for (const s of sets) if (new Set(s.roles).size !== 10) bad.push(`${s.id}: duplicate role`);
    for (const n of nodes) if (p.roleVocabulary[n.tacticalRole] !== n.tacticalRoleZh) bad.push(`${n.id}: roleZh`);
    let max = 0, pair = '';
    for (let i = 0; i < sets.length; i++) for (let j = i + 1; j < sets.length; j++) {
      const v = jaccard(sets[i].roles, sets[j].roles);
      if (v > max) { max = v; pair = `${sets[i].id}/${sets[j].id}`; }
    }
    const research = readJson(p.sources.researchTenNodeProposal.path);
    let rmax = 0, rpair = '';
    for (const s of sets) for (const r of research.series) {
      const v = jaccard(s.roles, r.nodes.map(n => n.tacticalRole));
      if (v > rmax) { rmax = v; rpair = `${s.id}/${r.id}`; }
    }
    const lim = p.validationParameters.crossSeriesRoleJaccardMax;
    if (max > lim) bad.push(`jaccard ${pair} ${max.toFixed(2)}`);
    if (rmax > lim) bad.push(`vs research ${rpair} ${rmax.toFixed(2)}`);
    add('distinct-roles', `每系列 10 个节点的战术定位互不相同；本提案任意两系列、以及与研学五系列之间的定位集合 Jaccard 相似度 ≤ ${lim}`,
      bad.length === 0, bad.length ? bad.join('; ') : `系列内 10/10 不同；应变内最大 ${max.toFixed(2)}（${pair}）；对研学最大 ${rmax.toFixed(2)}（${rpair}）`);
  }

  // 18 AI descriptions
  {
    const bad = [];
    for (const n of nodes) {
      const a = n.aiBehavior;
      if (!a || typeof a.defaultEnabled !== 'boolean' || !a.condition || a.condition.length < 6) { bad.push(`${n.id}: aiBehavior`); continue; }
      if (/道具|消耗品/.test(a.condition)) bad.push(`${n.id}: AI uses items`);
      if (/恢复.*HP|HP.*恢复|治疗/.test(n.baseEffect) && !/倒下/.test(a.condition + a.avoid)) bad.push(`${n.id}: heal AI lacks downed rule`);
      if (/组合技/.test(n.baseEffect) && !/组合技 AI/.test(a.condition)) bad.push(`${n.id}: combo AI default`);
      if (n.type === 'passive' && a.defaultEnabled !== true) bad.push(`${n.id}: passive AI flag`);
    }
    const off = nodes.filter(n => n.aiBehavior && n.aiBehavior.defaultEnabled === false).map(n => n.id);
    add('ai-descriptions', '每个节点都有 AI 说明（默认是否启用、按横向距离／生命比例写出的使用条件与回避条件）；AI 不使用道具；带治疗的节点写明倒下队友规则；涉及组合技的节点只在组合技 AI 开启时使用',
      bad.length === 0, bad.length ? bad.join('; ') : `${nodes.length}/${nodes.length}；默认关闭 ${off.length} 个${off.length ? '（' + off.join(', ') + '）' : ''}`);
  }

  // 19 science MVP utility
  {
    const allowed = new Set(p.validationParameters.scienceMvpLocations);
    const bad = [], list = [];
    for (const s of series) {
      const u = s.nodes.filter(n => n.scienceMvpUtility);
      if (!u.some(n => n.stage <= 2)) bad.push(`${s.id}: none at stage 1-2`);
      for (const n of u) {
        const m = n.scienceMvpUtility;
        if (m.gate !== 'optional-advantage-only' || m.requiresCurrentSeries !== true) bad.push(`${n.id}: gate`);
        if (!m.mvpLocations.length || m.mvpLocations.some(l => !allowed.has(l))) bad.push(`${n.id}: location`);
        if (!m.effect.includes('可选') || !/没有|不依赖|不是/.test(m.effect)) bad.push(`${n.id}: optional wording`);
        list.push(`${n.id}(${m.name})`);
      }
    }
    add('science-mvp-utility', '每系列至少 1 个第 1–2 阶节点带科技区 MVP 实用效果；全部为可选优势（写明可选且不是必经），需当前系列，地点限于已决定的 4 个 MVP 地点',
      bad.length === 0, bad.length ? bad.join('; ') : list.join(', '));
  }

  // 20 runtime catalog mapping
  {
    const cat = readJson(p.sources.runtimeSkeletonCatalog.path);
    const bad = [], linked = [];
    const used = new Set();
    for (const s of series) {
      const cs = cat.series.find(x => x.id === s.id);
      if (!cs) { bad.push(`${s.id}: not in catalog`); continue; }
      for (const n of s.nodes) {
        const c = cs.nodes.find(x => x.id === n.runtimeCatalogNodeId);
        if (!c) { bad.push(`${n.id}: ${n.runtimeCatalogNodeId} missing`); continue; }
        if (c.stage !== n.stage || c.slot !== (n.slot === 1 ? 'a' : 'b')) bad.push(`${n.id}: stage/slot`);
        if (used.has(c.id)) bad.push(`${n.id}: reused`);
        used.add(c.id);
        const isRuntime = String(c.status).startsWith('runtime-');
        if (isRuntime !== Boolean(n.runtimeNote)) bad.push(`${n.id}: runtimeNote`);
        if (isRuntime) linked.push(`${n.id}→${c.id}`);
      }
    }
    add('runtime-catalog-mapping', '每个节点对应运行时骨架目录中同系列、同阶、同槽位（slot 1↔a、2↔b）的唯一节点 id；目录中已有运行时行为的节点都附 runtimeNote 说明现行数值（本提案不改运行时）',
      bad.length === 0, bad.length ? bad.join('; ') : `50/50 映射唯一；带运行时行为的 ${linked.length} 个：${linked.join(', ')}`);
  }

  // 21 progression economics
  {
    const bad = [];
    const e = economics(p);
    if (JSON.stringify(e.rows) !== JSON.stringify(p.economics.aptitudeTable)) bad.push('aptitudeTable differs from recomputation');
    if (JSON.stringify(e.battles) !== JSON.stringify(p.economics.battleEstimates)) bad.push('battleEstimates differ');
    const shape = curveShape(p.jpProposal.rankUpgradeBaseJp);
    if (JSON.stringify(shape) !== JSON.stringify(p.economics.proposedCurve)) bad.push('proposedCurve differs');
    if (shape.increments.some((d, i) => i > 0 && d !== shape.increments[0])) bad.push('proposed table not linear');
    if (shape.successiveRatios.some((r, i) => i > 0 && r >= shape.successiveRatios[i - 1])) bad.push('successive ratios not falling');
    if (shape.rank5OverRank2 > p.validationParameters.jpRank5OverRank2Max) bad.push('rank5/rank2');
    for (let i = 1; i < e.rows.length; i++) for (const r of ['2', '3', '4', '5']) if (e.rows[i].perRank[r] > e.rows[i - 1].perRank[r]) bad.push(`not monotone at ${e.rows[i].aptitude}`);
    const lo = e.rows.find(r => r.aptitude === 100), hi = e.rows.find(r => r.aptitude === 60);
    const spread = lo.perSkill / hi.perSkill;
    if (spread < 0.5 - EPS || spread > 1) bad.push(`spread ${spread}`);
    const cat = readJson(p.sources.runtimeSkeletonCatalog.path);
    const rt = curveShape(cat.rules.upgradeJpBase);
    if (JSON.stringify(rt) !== JSON.stringify(p.economics.runtimeSkeletonCurve)) bad.push('runtimeSkeletonCurve differs from catalog');
    if (rt.successiveRatios.some((r, i) => i > 0 && r >= rt.successiveRatios[i - 1])) bad.push('runtime curve ratios not falling');
    add('progression-economics', '提案 JP 表为线性（每级 +15，逐级比值递减，第 5 级 / 第 2 级 ≤ 2.5）；天分折扣表、每阶战斗场数估算与运行时骨架曲线均由公式重算一致；天分 100 的成本不低于天分 60 的 50%，且随天分单调不增',
      bad.length === 0, bad.length ? bad.join('; ')
        : `提案 ${shape.values.join('/')}（总 ${shape.total}，比值 ${shape.successiveRatios.join('/')}）；运行时骨架 ${rt.values.join('/')}（总 ${rt.total}，增量 ${rt.increments.join('/')}，比值 ${rt.successiveRatios.join('/')}，非指数）；单技能 ${hi.perSkill}→${lo.perSkill} JP（天分 60→100，${Math.round(spread * 1000) / 10}%）`);
  }

  // 22 proposal marking
  {
    const ok = nodes.filter(n => n.status === 'PROPOSAL' && n.reviewStatus === 'pending balance and creator review').length;
    add('proposal-marking', '文件本身与 50/50 节点都标为 PROPOSAL、待数值平衡与创作者审核',
      ok === 50 && p.status === 'PROPOSAL' && p.reviewStatus === 'pending balance and creator review', `${ok}/50`);
  }

  // 23 superseded lineage
  {
    const adaptive = readJson(p.sources.supersededAdaptiveDraft.path);
    const four = readJson(p.sources.supersededSkirmishDraft.path);
    const draft = [...adaptive.trees, ...four.trees.filter(t => t.seriesId === 'skirmish')];
    const draftIds = new Set(draft.flatMap(t => t.nodes.map(n => n.id)));
    const bad = [];
    const refs = nodes.map(n => n.supersedesDraftNodeId).filter(Boolean);
    for (const r of refs) if (!draftIds.has(r)) bad.push(`missing ${r}`);
    if (new Set(refs).size !== refs.length) bad.push('reused draft id');
    for (const n of nodes) if (draftIds.has(n.id)) bad.push(`${n.id}: id collides with draft`);
    for (const n of nodes) if (n.supersedesDraftNodeId && !n.supersedesDraftNodeId.startsWith(n.seriesId + '_')) bad.push(`${n.id}: cross-series lineage`);
    const dropped = [...draftIds].filter(id => !refs.includes(id)).sort();
    if (JSON.stringify(dropped) !== JSON.stringify([...p.lineage.droppedDraftNodeIds].sort())) bad.push(`dropped list ≠ ${dropped.join(',')}`);
    add('superseded-lineage', '节点 id 不与被取代草案冲突；supersedesDraftNodeId 只引用同系列真实草案节点且各用一次；未继承的草案节点与 lineage.droppedDraftNodeIds 一致',
      bad.length === 0, bad.length ? bad.join('; ') : `${refs.length}/${draftIds.size} 个草案节点有继承关系；舍弃 ${dropped.length} 个：${dropped.join(', ')}`);
  }

  return checks;
}

function digest(checks) {
  return sha256(Buffer.from(JSON.stringify(checks.map(c => [c.id, c.result, c.detail])), 'utf8'));
}

module.exports = {runChecks, digest, economics, curveShape, rankText, fmt, jpCost, PROPOSAL_REL};

if (require.main === module) {
  const args = process.argv.slice(2);
  const i = args.indexOf('--proposal');
  const file = i >= 0 ? path.resolve(args[i + 1]) : path.join(ROOT, PROPOSAL_REL);
  const p = JSON.parse(fs.readFileSync(file, 'utf8'));
  const checks = runChecks(p);
  if (args.includes('--json')) { console.log(JSON.stringify(checks, null, 1)); }
  else for (const c of checks) console.log(`${c.result === 'pass' ? 'PASS' : 'FAIL'}  ${c.id}  ${c.detail}`);
  const passed = checks.filter(c => c.result === 'pass').length;
  const embedded = p.validation || {};
  const same = embedded.resultsDigest === digest(checks)
    && JSON.stringify((embedded.checks || []).map(c => [c.id, c.result, c.detail])) === JSON.stringify(checks.map(c => [c.id, c.result, c.detail]));
  console.log(`${passed}/${checks.length} pass; embedded results ${same ? 'match' : 'DO NOT match'} (digest ${digest(checks).slice(0, 16)})`);
  console.log(`proposal ${TEXT_HASH} ${textSha256(fs.readFileSync(file))}`);
  process.exit(passed === checks.length && same ? 0 : 1);
}
