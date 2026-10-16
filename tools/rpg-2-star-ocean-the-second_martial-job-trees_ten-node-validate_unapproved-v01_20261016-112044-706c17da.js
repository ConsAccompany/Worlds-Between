#!/usr/bin/env node
// Deterministic validator for the 武艺 (martial) ten-node job-tree PROPOSAL.
// Read-only: it loads the proposal and its sources, recomputes every check, and (in CLI mode) compares the
// recomputed results with the results embedded in the proposal's `validation` block. It never writes files.
//
//   node tools/rpg-2-star-ocean-the-second_martial-job-trees_ten-node-validate_unapproved-v01_20261016-112044-706c17da.js [proposal.json]
//
// Exit code 0 = every check passes (warnings allowed) and the embedded results match; 1 otherwise.
// No external libraries. Text hashes use sha256-text-lf-v1 (CRLF -> LF only), like the shared Node helper.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const ROOT = path.resolve(__dirname, '..');
const DEFAULT_PROPOSAL = 'outputs/rpg-2-star-ocean-the-second_martial-job-trees_ten-node-skill-proposal_unapproved-v01_20261016-112044-4e3b550a.json';
const SOURCE_PATHS = {
  roster: 'outputs/rpg-2-star-ocean-the-second_all-jobs_five-tier-proposal_v01_20261013-224236-6f2b9c11.json',
  gameBible: 'outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json',
  martialDraft: 'outputs/rpg-2-star-ocean-the-second_martial-job-trees_skill-node-proposal_v01_20261013-224832-1c9e73ab.json',
  fourTreeDraft: 'outputs/rpg-2-star-ocean-the-second_four-job-trees_skill-node-proposal_v01_20261013-224554-5a72d0be.json',
  researchProposal: 'outputs/rpg-2-star-ocean-the-second_research-job-trees_ten-node-skill-proposal_unapproved-v01_20261015-232143-842e0540.json',
  growthRules: 'game/scripts/growth_rules.gd',
  appState: 'game/scripts/app_state.gd',
};

function textLf(buffer) {
  if (buffer.includes(0)) throw new Error('NUL byte: not a text file');
  new TextDecoder('utf-8', {fatal: true}).decode(buffer);
  const out = Buffer.allocUnsafe(buffer.length);
  let n = 0;
  for (let i = 0; i < buffer.length; i++) {
    if (buffer[i] === 0x0d && buffer[i + 1] === 0x0a) continue;
    out[n++] = buffer[i];
  }
  return out.subarray(0, n);
}
const textSha256 = buffer => crypto.createHash('sha256').update(textLf(buffer)).digest('hex');

function loadContext(root = ROOT) {
  const read = rel => fs.readFileSync(path.join(root, rel));
  const json = rel => JSON.parse(read(rel).toString('utf8'));
  return {
    root,
    roster: json(SOURCE_PATHS.roster),
    gameBible: json(SOURCE_PATHS.gameBible),
    martialDraft: json(SOURCE_PATHS.martialDraft),
    fourTreeDraft: json(SOURCE_PATHS.fourTreeDraft),
    researchProposal: json(SOURCE_PATHS.researchProposal),
    growthRules: read(SOURCE_PATHS.growthRules).toString('utf8'),
    appState: read(SOURCE_PATHS.appState).toString('utf8'),
    hashOf: rel => textSha256(read(rel)),
  };
}

// ---- minimal JSON Schema subset (type, enum, const, pattern, minimum, maximum, minItems, maxItems,
// ---- required, properties, additionalProperties:false, items, $ref "#/$defs/x") --------------------------
function typeOf(v) {
  if (v === null) return 'null';
  if (Array.isArray(v)) return 'array';
  if (Number.isInteger(v)) return 'integer';
  return typeof v;
}
function schemaErrors(value, schema, rootSchema, at, errors) {
  if (schema.$ref) {
    const name = schema.$ref.replace('#/$defs/', '');
    return schemaErrors(value, rootSchema.$defs[name], rootSchema, at, errors);
  }
  if (schema.type) {
    const types = Array.isArray(schema.type) ? schema.type : [schema.type];
    const t = typeOf(value);
    const ok = types.some(x => x === t || (x === 'number' && t === 'integer'));
    if (!ok) { errors.push(`${at}: type ${t} not in ${types.join('|')}`); return errors; }
  }
  if ('const' in schema && JSON.stringify(value) !== JSON.stringify(schema.const)) errors.push(`${at}: const ${JSON.stringify(schema.const)}`);
  if (schema.enum && !schema.enum.some(e => JSON.stringify(e) === JSON.stringify(value))) errors.push(`${at}: not in enum`);
  if (typeof value === 'string' && schema.pattern && !new RegExp(schema.pattern).test(value)) errors.push(`${at}: pattern ${schema.pattern}`);
  if (typeof value === 'string' && schema.minLength && value.length < schema.minLength) errors.push(`${at}: minLength ${schema.minLength}`);
  if (typeof value === 'number') {
    if ('minimum' in schema && value < schema.minimum) errors.push(`${at}: < ${schema.minimum}`);
    if ('maximum' in schema && value > schema.maximum) errors.push(`${at}: > ${schema.maximum}`);
  }
  if (Array.isArray(value)) {
    if ('minItems' in schema && value.length < schema.minItems) errors.push(`${at}: minItems ${schema.minItems}`);
    if ('maxItems' in schema && value.length > schema.maxItems) errors.push(`${at}: maxItems ${schema.maxItems}`);
    if (schema.items) value.forEach((v, i) => schemaErrors(v, schema.items, rootSchema, `${at}[${i}]`, errors));
  }
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    for (const k of schema.required || []) if (!(k in value)) errors.push(`${at}: missing ${k}`);
    const props = schema.properties || {};
    if (schema.additionalProperties === false) for (const k of Object.keys(value)) if (!(k in props)) errors.push(`${at}: extra ${k}`);
    for (const [k, s] of Object.entries(props)) if (k in value) schemaErrors(value[k], s, rootSchema, `${at}.${k}`, errors);
  }
  return errors;
}

// ---- helpers ---------------------------------------------------------------------------------------------
const allNodes = p => p.series.flatMap(s => s.nodes);
const nodeTexts = n => {
  // Every free-text field of a node (stageName excluded: it is approved roster text).
  const parts = [n.name, n.nameEn, n.target, n.baseEffect, n.tacticalRoleZh, n.ai.useWhen, n.ai.avoidWhen || '',
    n.stacking.note, ...n.scaling.map(s => s.label), ...Object.values(n.rankProgression)];
  if (n.scienceMvpUtility) parts.push(n.scienceMvpUtility.name, n.scienceMvpUtility.effect);
  if (n.lineageNote) parts.push(n.lineageNote);
  return parts.join('\n');
};
const effectTexts = n => [n.baseEffect, n.target, n.ai.useWhen, n.ai.avoidWhen || '', n.stacking.note].join('\n');
const fmt = v => (Number.isInteger(v) ? String(v) : String(Math.round(v * 1000) / 1000));
const r5 = s => s.values[4];
const jaccard = (a, b) => { const A = new Set(a), B = new Set(b); const i = [...A].filter(x => B.has(x)).length; return i / new Set([...A, ...B]).size; };

// Keyword -> required cap category (text in baseEffect/target/ai/stacking note).
const KEYWORD_CAPS = [
  [/减伤|伤害降低/, 'ally_damage_reduction'],
  [/防御降低|无视目标\s*\d+%?\s*防御|无视目标.{0,8}防御/, 'enemy_defense_down'],
  [/受到全队伤害提高/, 'enemy_damage_taken_up'],
  [/护层/, 'shield_total'],
  [/异常抗性/, 'status_resistance'],
  [/速度降低|减速/, 'enemy_slow'],
  [/打断|硬直|击退/, 'control_diminishing'],
  [/起手延后/, 'windup_delay'],
  [/回复\s*\d+\s*点能量/, 'energy_return'],
  [/恢复自身生命/, 'self_heal_per_battle'],
  [/反震/, 'reflect_cap'],
  [/蓄力时间缩短/, 'charge_time_reduction'],
  [/必须以守护者为目标/, 'forced_target'],
  [/原始伤害的\s*\d+%/, 'damage_floor'],
  [/分担/, 'damage_redirect'],
];
// Words that belong to exactly one series' node text.
const EXCLUSIVE_VOCAB = [
  [/击退/, 'polearm'], [/枪尖区/, 'polearm'],
  [/分担|代受|护线/, 'guardian'],
  [/反击|反打|反震|劲/, 'martial'],
  [/蓄力|裂甲|护甲值|防护板|霸体/, 'heavy'],
  [/剑势|看破/, 'sword'],
];

// ---- checks ----------------------------------------------------------------------------------------------
function runChecks(p, ctx, opts = {}) {
  const checks = [];
  const add = (id, description, ok, detail, level = 'fail') => checks.push({id, description, result: ok ? 'pass' : level, detail});
  const nodes = allNodes(p);
  const vp = p.validationParameters;
  const caps = p.rules.stackingCaps;
  const martialRoster = ctx.roster.series.filter(s => s.aptitude === '武艺');
  const bibleSeries = ctx.gameBible.jobProposal.series.filter(s => s.aptitude === '武艺');

  // 1 file status
  add('file-proposal-status', '文件本身标为 PROPOSAL，待数值平衡与创作者审核',
    p.status === 'PROPOSAL' && p.reviewStatus === 'pending balance and creator review', `${p.status} / ${p.reviewStatus}`);

  // 2 series set
  {
    const ids = p.series.map(s => s.id), want = martialRoster.map(s => s.id);
    add('series-set', '恰好 5 条系列，且正是已批准名单中天分为武艺的 5 条（顺序一致）',
      JSON.stringify(ids) === JSON.stringify(want), ids.join(', '));
  }

  // 3 verbatim approved text (roster file and Game Bible jobProposal)
  {
    const bad = [];
    p.series.forEach((s, i) => {
      for (const [label, src] of [['roster', martialRoster[i]], ['gameBible', bibleSeries[i]]]) {
        if (!src) { bad.push(`${s.id}:${label}:missing`); continue; }
        for (const k of ['id', 'aptitude', 'name', 'en', 'role', 'finalQuest']) if (s[k] !== src[k]) bad.push(`${s.id}.${k}≠${label}`);
        if (JSON.stringify(s.stages) !== JSON.stringify(src.stages)) bad.push(`${s.id}.stages≠${label}`);
      }
      s.nodes.forEach(n => { if (n.stageName !== s.stages[n.stage - 1]) bad.push(`${n.id}.stageName`); });
    });
    add('approved-text-verbatim', '系列名、英文名、定位、五阶名称、终阶任务与已批准名单 JSON 及 Game Bible jobProposal 逐字一致；每个节点的 stageName 与其阶名称逐字一致',
      bad.length === 0, bad.length ? bad.join('; ') : '5 系列 × (名称/定位/5 阶/终阶任务) 与两处来源逐字一致；50 个 stageName 一致');
  }

  // 4 ten nodes, two per stage
  {
    const bad = [];
    for (const s of p.series) {
      if (s.nodes.length !== 10) bad.push(`${s.id}:${s.nodes.length}`);
      for (let st = 1; st <= 5; st++) {
        const slots = s.nodes.filter(n => n.stage === st).map(n => n.slot).sort().join(',');
        if (slots !== '1,2') bad.push(`${s.id}:stage${st}:${slots}`);
      }
      s.nodes.forEach((n, i) => { if (n.seriesId !== s.id || n.stage !== Math.floor(i / 2) + 1 || n.slot !== (i % 2) + 1) bad.push(`${n.id}:order`); });
    }
    add('ten-nodes-two-per-stage', '每系列恰好 10 个节点，5 阶各 2 个（slot 1、2，按阶排序）；合计 50 个',
      bad.length === 0 && nodes.length === 50, bad.length ? bad.join('; ') : `5 × 10 = ${nodes.length}；每阶 2 个`);
  }

  // 5 schema (whole document + every node)
  {
    const docErr = schemaErrors(p, p.schema, p.schema, '$', []);
    const nodeErr = nodes.flatMap(n => schemaErrors(n, p.schema.$defs.node, p.schema, n.id, []));
    const errs = [...docErr, ...nodeErr];
    add('node-schema', '整份文件与每个节点都符合内嵌 JSON Schema（必填字段、类型、枚举、常量、id 格式、additionalProperties:false；脚本内自写校验器，未使用外部库）',
      errs.length === 0, errs.length ? errs.slice(0, 12).join('; ') : `文件通过；${nodes.length}/${nodes.length} 节点通过`);
  }

  // 6 distinct ids and names (also vs the 研学 proposal)
  {
    const research = allNodes(ctx.researchProposal);
    const rZh = new Set(research.map(n => n.name)), rEn = new Set(research.map(n => n.nameEn.toLowerCase()));
    const ids = new Set(nodes.map(n => n.id)), zh = new Set(nodes.map(n => n.name)), en = new Set(nodes.map(n => n.nameEn.toLowerCase()));
    const clash = nodes.filter(n => rZh.has(n.name) || rEn.has(n.nameEn.toLowerCase())).map(n => n.id);
    add('distinct-nodes', '50 个节点的 id、中文名、英文名全局唯一，且不与研学 10 节点提案的 50 个节点重名',
      ids.size === 50 && zh.size === 50 && en.size === 50 && clash.length === 0,
      `${ids.size} 个 id / ${zh.size} 个中文名 / ${en.size} 个英文名；与研学提案重名 ${clash.length} 个${clash.length ? '：' + clash.join(', ') : ''}`);
  }

  // 7 unlock + rank + JP rules
  {
    const bad = [];
    for (const n of nodes) {
      if (!n.unlock.onStageEntry || n.unlock.jpCost !== 0) bad.push(`${n.id}:unlock`);
      if (n.unlock.unlockedAtRank !== 1) bad.push(`${n.id}:entryRank`);
      if (n.unlock.requiresFinalQuest !== (n.stage === 5)) bad.push(`${n.id}:finalQuestGate`);
      if (n.maxRank !== 5) bad.push(`${n.id}:maxRank`);
      if (JSON.stringify(Object.keys(n.rankProgression)) !== '["2","3","4","5"]') bad.push(`${n.id}:rankKeys`);
      for (const r of [2, 3, 4, 5]) for (const s of n.scaling) if (!n.rankProgression[r].includes(fmt(s.values[r - 1]))) bad.push(`${n.id}:r${r}:${s.key}`);
    }
    const jpKeys = Object.keys(p.jpProposal.rankUpgradeBaseJp).join(',');
    if (jpKeys !== '2,3,4,5' || p.jpProposal.unlockJp !== 0) bad.push('jpTable');
    if (p.rules.exclusiveBranches !== false) bad.push('exclusiveBranches');
    add('unlock-and-rank-rules', '每个节点进入该阶即以第 1 级开放（jpCost 0）；第 5 阶节点另需终阶任务；最高 5 级；JP 表只含第 2–5 级；无互斥分支；rankProgression 与 scaling 数值一致',
      bad.length === 0, bad.length ? bad.join('; ') : `${nodes.length}/${nodes.length}；JP 表只含第 2–5 级；无互斥分支`);
  }

  // 8 active/passive, energy bands, cooldowns
  {
    const bad = [], summary = [];
    for (const s of p.series) {
      const a = s.nodes.filter(n => n.type === 'active'), ps = s.nodes.filter(n => n.type === 'passive');
      summary.push(`${s.id} ${a.length}A/${ps.length}P`);
      if (a.length < 5 || ps.length < 2) bad.push(`${s.id}:mix`);
      for (let st = 1; st <= 5; st++) if (!s.nodes.some(n => n.stage === st && n.type === 'active')) bad.push(`${s.id}:stage${st}:noActive`);
      for (const n of s.nodes) {
        if (n.typeZh !== (n.type === 'active' ? '主动' : '被动')) bad.push(`${n.id}:typeZh`);
        if (n.type === 'active') {
          const [lo, hi] = vp.energyBandsByStage[n.stage];
          if (!Number.isInteger(n.energyCost) || n.energyCost < lo || n.energyCost > hi) bad.push(`${n.id}:energy ${n.energyCost}∉[${lo},${hi}]`);
          if (!(n.cooldownSec >= vp.minActiveCooldownSec)) bad.push(`${n.id}:cooldown`);
          if (n.stage === 5 && n.cooldownSec < vp.minStage5CooldownSec) bad.push(`${n.id}:stage5cooldown`);
          if (n.ai.mode !== 'active_condition') bad.push(`${n.id}:aiMode`);
        } else {
          if (n.energyCost !== null || n.cooldownSec !== null) bad.push(`${n.id}:passiveCost`);
          if (!n.ai.mode.startsWith('passive_auto')) bad.push(`${n.id}:aiMode`);
        }
      }
    }
    add('active-passive-energy', '主动技能有整数能量消耗（按阶区间）与冷却（≥ 下限，第 5 阶 ≥ 40 秒）；被动技能无消耗与冷却；每系列 ≥5 主动、≥2 被动，每阶至少 1 个主动',
      bad.length === 0, bad.length ? bad.join('; ') : summary.join('; '));
  }

  // 9 non-exponential rank curves
  {
    const bad = []; let maxRatio = 0;
    for (const n of nodes) for (const s of n.scaling) {
      const v = s.values;
      const steps = v.slice(1).map((x, i) => x - v[i]);
      if (steps.some(d => !(d > 0))) bad.push(`${n.id}.${s.key}:notIncreasing`);
      for (let i = 1; i < steps.length; i++) if (steps[i] > steps[i - 1] + 1e-9) bad.push(`${n.id}.${s.key}:accelerating`);
      const ratio = v[4] / v[0]; maxRatio = Math.max(maxRatio, ratio);
      if (ratio > vp.rank5ToRank1MaxRatio + 1e-9) bad.push(`${n.id}.${s.key}:ratio ${ratio.toFixed(2)}`);
    }
    add('non-exponential-ranks', '所有等级数值严格递增、步长固定或递减（无加速增长），第 5 级 / 第 1 级 ≤ 2；能量消耗、冷却、触发次数为单一值，不随等级变化',
      bad.length === 0, bad.length ? bad.join('; ') : `全部为固定或递减加法步长；最大 r5/r1 = ${maxRatio.toFixed(2)}`);
  }

  // 10 unlimited-level safety: no character-level scaling, only stat-relative or bounded units
  {
    const bad = [];
    const levelRe = /角色等级|随等级|人物等级|每升一级|按等级|character level|per level/i;
    for (const n of nodes) {
      for (const s of n.scaling) if (!vp.allowedScalingUnits.includes(s.unit)) bad.push(`${n.id}.${s.key}:unit ${s.unit}`);
      if (levelRe.test(nodeTexts(n))) bad.push(`${n.id}:levelText`);
    }
    add('unlimited-level-safe', '无等级上限下仍可用：没有数值随角色等级增长；伤害、治疗、护层只按攻击力或生命上限的百分比计算，其余只用秒、px、点能量（返还/上限）与百分比',
      bad.length === 0, bad.length ? bad.join('; ') : `${nodes.length}/${nodes.length}；单位限于 ${vp.allowedScalingUnits.join('、')}`);
  }

  // 11 capped stacking
  {
    const bad = [], worst = {};
    for (const n of nodes) {
      const st = n.stacking;
      if (!(Number.isInteger(st.maxStacks) && st.maxStacks >= 1 && st.maxStacks <= vp.maxStacksPerEffect)) bad.push(`${n.id}:maxStacks`);
      for (const c of st.capCategories) if (!caps[c]) bad.push(`${n.id}:unknownCap ${c}`);
      const contributions = [...st.fixedContributions];
      for (const s of n.scaling) if (s.capCategory) contributions.push({category: s.capCategory, value: r5(s) * (s.perStack ? st.maxStacks : 1)});
      if (n.energyReturn) {
        const s = n.scaling.find(x => x.key === n.energyReturn.perTriggerKey);
        contributions.push({category: 'energy_return', value: r5(s) * n.energyReturn.maxTriggersPerBattle});
      }
      if (n.maxTriggersPerBattle && n.scaling.some(s => s.capCategory === 'self_heal_per_battle')) {
        const s = n.scaling.find(x => x.capCategory === 'self_heal_per_battle');
        contributions.push({category: 'self_heal_per_battle', value: r5(s) * n.maxTriggersPerBattle});
      }
      for (const c of contributions) {
        if (!st.capCategories.includes(c.category)) bad.push(`${n.id}:undeclared ${c.category}`);
        const cap = caps[c.category];
        if (!cap || cap.limit === null) continue;
        const ok = cap.kind === 'min' ? c.value >= cap.limit - 1e-9 : c.value <= cap.limit + 1e-9;
        if (!ok) bad.push(`${n.id}:${c.category} ${fmt(c.value)} vs ${cap.kind} ${cap.limit}`);
        const k = c.category;
        worst[k] = cap.kind === 'min' ? Math.min(worst[k] ?? Infinity, c.value) : Math.max(worst[k] ?? -Infinity, c.value);
      }
      const text = effectTexts(n);
      for (const [re, cat] of KEYWORD_CAPS) if (re.test(text) && !st.capCategories.includes(cat)) bad.push(`${n.id}:text→${cat}`);
    }
    const w = Object.entries(worst).map(([k, v]) => `${k} ${fmt(v)}/${caps[k].kind === 'min' ? '≥' : '≤'}${caps[k].limit}`).join('；');
    add('capped-stacking', '每个节点声明叠加规则（层数 ≤ 5）与所属全来源上限类别；第 5 级单节点贡献不超过上限（伤害下限类不低于下限）；文本出现减伤、防御降低、护层、抗性、减速、打断/硬直/击退、起手延后、能量回复、自愈、反震、蓄力缩短、强制目标、分担等效果时必须声明对应上限类别',
      bad.length === 0, bad.length ? bad.join('; ') : `50/50；各类别第 5 级单节点最大贡献：${w}`);
  }

  // 12 energy returns capped
  {
    const bad = [], seen = [];
    for (const s of p.series) {
      const minActive = Math.min(...s.nodes.filter(n => n.type === 'active').map(n => n.energyCost));
      for (const n of s.nodes) {
        const mentions = /回复\s*\d+\s*点能量/.test(n.baseEffect);
        if (mentions && !n.energyReturn) bad.push(`${n.id}:undeclaredReturn`);
        if (!n.energyReturn) continue;
        const sc = n.scaling.find(x => x.key === n.energyReturn.perTriggerKey);
        const per = r5(sc), trig = n.energyReturn.maxTriggersPerBattle;
        if (!(per < minActive)) bad.push(`${n.id}:perTrigger ${per} ≥ ${minActive}`);
        if (!(Number.isInteger(trig) && trig <= vp.maxEnergyReturnTriggersPerBattle)) bad.push(`${n.id}:triggers ${trig}`);
        if (per * trig > caps.energy_return.limit) bad.push(`${n.id}:total ${per * trig}`);
        seen.push(`${n.id} 单次 ≤${per}（本系列最低主动 ${minActive}）× ${trig} 次 = ${per * trig}`);
      }
    }
    add('energy-return-capped', '返还能量的节点都有每场次数上限；单次返还低于本系列最低主动消耗；每场合计 ≤ 上限',
      bad.length === 0, bad.length ? bad.join('; ') : seen.join('；'));
  }

  // 13 banned terms
  {
    const zh = vp.bannedTerms.filter(t => !/^[a-z ]+$/i.test(t));
    const en = vp.bannedTerms.filter(t => /^[a-z ]+$/i.test(t));
    const enRe = new RegExp(`\\b(${en.map(t => t.replace(/ /g, '\\s+')).join('|')})\\b`, 'i');
    const hits = [];
    const scan = (id, t) => { for (const w of zh) if (t.includes(w)) hits.push(`${id}:${w}`); const m = t.match(enRe); if (m) hits.push(`${id}:${m[0]}`); };
    for (const n of nodes) scan(n.id, nodeTexts(n));
    for (const s of p.series) scan(s.id, [s.identity, s.contrast, s.finalQuestFit].join('\n'));
    add('no-terrain-elevation-obstacle-jump-stealth', '节点文本、系列定位说明与科技区实用效果都不含地形、高低差、障碍、掩体、跳跃、浮空或潜入/隐身相关词（英文按整词匹配；已批准的阶名与终阶任务不扫描）',
      hits.length === 0, hits.length ? hits.join('; ') : `${vp.bannedTerms.length} 个禁用词，50 个节点与 5 段系列说明 0 命中`);
  }

  // 14 distinct roles
  {
    const bad = []; let max = 0, pair = '';
    for (const s of p.series) {
      const roles = s.nodes.map(n => n.tacticalRole);
      if (new Set(roles).size !== 10) bad.push(`${s.id}:dupRole`);
      for (const n of s.nodes) if (p.roleVocabulary[n.tacticalRole] !== n.tacticalRoleZh) bad.push(`${n.id}:roleZh`);
    }
    for (let i = 0; i < 5; i++) for (let j = i + 1; j < 5; j++) {
      const a = p.series[i], b = p.series[j];
      const v = jaccard(a.nodes.map(n => n.tacticalRole), b.nodes.map(n => n.tacticalRole));
      if (v > max) { max = v; pair = `${a.id}/${b.id}`; }
    }
    if (max > vp.crossSeriesRoleJaccardMax) bad.push(`jaccard ${max.toFixed(2)} ${pair}`);
    add('distinct-roles', '每系列 10 个节点的战术定位互不相同；任意两条武艺系列的定位集合 Jaccard 相似度 ≤ 0.4',
      bad.length === 0, bad.length ? bad.join('; ') : `系列内 10/10 不同；最大跨系列 Jaccard ${max.toFixed(2)}（${pair}）`);
  }

  // 15 signature mechanics: present and exclusive
  {
    const bad = [], counts = [];
    const owner = {};
    for (const [tag, def] of Object.entries(p.mechanicTagVocabulary)) if (def.signatureOf) owner[tag] = def.signatureOf;
    for (const s of p.series) {
      let own = 0;
      for (const n of s.nodes) {
        for (const t of n.mechanicTags) {
          if (!p.mechanicTagVocabulary[t]) bad.push(`${n.id}:unknownTag ${t}`);
          if (owner[t] && owner[t] !== s.id) bad.push(`${n.id}:foreignSignature ${t}`);
        }
        if (n.mechanicTags.some(t => owner[t] === s.id)) own++;
      }
      counts.push(`${s.id} ${own}/10`);
      if (own < vp.minSignatureNodesPerSeries) bad.push(`${s.id}:signature ${own}`);
    }
    add('series-signature-mechanics', '每条系列至少 6 个节点带本系列标志机制标签，且没有节点带其他系列的标志机制（守护：分担/强制转向/代受；剑术：起手抢先/剑势；重武：蓄力/破甲/圆形冲击/霸体；武道：受击后反击/劲/调息；长兵：枪尖区/击退/直线贯穿/迎击）',
      bad.length === 0, bad.length ? bad.join('; ') : counts.join('; '));
  }

  // 16 exclusive vocabulary in node effect text
  {
    const bad = [];
    for (const s of p.series) for (const n of s.nodes) for (const [re, sid] of EXCLUSIVE_VOCAB) {
      if (sid !== s.id && re.test(effectTexts(n) + '\n' + n.name)) bad.push(`${n.id}:${re.source}`);
    }
    add('exclusive-vocabulary', '各系列专属效果词只出现在本系列节点：击退/枪尖区（长兵）、分担/代受/护线（守护）、反击/反打/反震/劲（武道）、蓄力/裂甲/护甲值/防护板/霸体（重武）、剑势/看破（剑术）',
      bad.length === 0, bad.length ? bad.join('; ') : '50 个节点 0 越界');
  }

  // 17 AI fields
  {
    const bad = [];
    for (const n of nodes) {
      const t = [n.ai.useWhen, n.ai.avoidWhen || ''].join('\n');
      if (!n.ai.useWhen || n.ai.useWhen.length < 8) bad.push(`${n.id}:useWhen`);
      if (/道具|消耗品/.test(t)) bad.push(`${n.id}:consumable`);
      if (/组合技/.test(t)) bad.push(`${n.id}:combo`);
      if (n.type === 'active' && typeof n.ai.defaultEnabled !== 'boolean') bad.push(`${n.id}:default`);
    }
    add('ai-use', '每个节点写明 AI 使用条件（主动：何时施放/何时不施放；被动：自动触发方式与可否在策略中关闭）；AI 条件不涉及消耗道具或组合技（两者默认关闭）',
      bad.length === 0, bad.length ? bad.join('; ') : `${nodes.length}/${nodes.length}`);
  }

  // 18 science MVP utility: optional only
  {
    const bad = [], list = [];
    const allowed = new Set(vp.approvedMvpLocations);
    for (const n of nodes) {
      const u = n.scienceMvpUtility; if (!u) continue;
      list.push(`${n.id}(${u.name})`);
      if (n.stage > 2) bad.push(`${n.id}:stage`);
      if (u.gate !== 'optional-advantage-only' || u.requiresCurrentSeries !== true || u.storyMandatory !== false) bad.push(`${n.id}:gate`);
      for (const l of u.mvpLocations) if (!allowed.has(l)) bad.push(`${n.id}:loc ${l}`);
      if (/捷径|通路|通道|开路|清障|档案条目/.test(u.effect)) bad.push(`${n.id}:pathOrArchive`);
    }
    add('science-mvp-utility-optional', '科技区实用效果只出现在第 1–2 阶、只在当前系列可用、只用于已批准的 MVP 地点，只给可选普通补给，不开启路线、不给剧情物品或档案，永不为剧情必需（可以没有）',
      bad.length === 0, bad.length ? bad.join('; ') : `${list.length} 个：${list.join(', ') || '无'}；其余 ${nodes.length - list.length} 个节点为 null`);
  }

  // 19 PROPOSAL marking
  {
    const ok = nodes.filter(n => n.status === 'PROPOSAL' && n.reviewStatus === 'pending balance and creator review').length;
    add('proposal-marking', '50/50 节点标为 PROPOSAL，待数值平衡与创作者审核', ok === 50, `${ok}/50`);
  }

  // 20 superseded-draft lineage
  {
    const bad = [];
    const draft = {};
    for (const t of ctx.martialDraft.trees) for (const n of t.nodes) draft[n.id] = t.seriesId;
    for (const t of ctx.fourTreeDraft.trees.filter(t => t.seriesId === 'guardian')) for (const n of t.nodes) draft[n.id] = t.seriesId;
    const used = new Map();
    for (const n of nodes) {
      const d = n.supersedesDraftNodeId; if (!d) continue;
      if (!(d in draft)) bad.push(`${n.id}:unknown ${d}`);
      else if (draft[d] !== n.seriesId) bad.push(`${n.id}:series ${d}`);
      if (used.has(d)) bad.push(`${d}:reused`); used.set(d, n.id);
      if (Object.keys(draft).includes(n.id)) bad.push(`${n.id}:idCollision`);
    }
    const dropped = Object.keys(draft).filter(d => !used.has(d)).sort();
    const declared = p.lineage.droppedDraftNodes.map(x => x.id).sort();
    if (JSON.stringify(dropped) !== JSON.stringify(declared)) bad.push(`dropped ${dropped.join(',')} ≠ declared ${declared.join(',')}`);
    add('superseded-lineage', '节点 id 不与被取代草案冲突；supersedesDraftNodeId 只引用同系列真实草案节点且各用一次；未继承的草案节点与文件中的舍弃清单一致',
      bad.length === 0, bad.length ? bad.join('; ') : `${used.size}/${Object.keys(draft).length} 个草案节点有继承关系；舍弃 ${dropped.length} 个：${dropped.join(', ')}`);
  }

  // 21 runtime lineage (existing MVP sword skills keep their slot, name and cost)
  {
    const bad = [], seen = [];
    const m = ctx.growthRules.match(/"sword":\s*\{"aptitude":\s*"martial",\s*"skills":\s*\[([^\]]*)\]/);
    const runtimeSkills = m ? [...m[1].matchAll(/"([a-z_]+)"/g)].map(x => x[1]) : [];
    if (!runtimeSkills.length) bad.push('growth_rules sword skills not found');
    for (const n of nodes.filter(x => x.runtimeLineage)) {
      const rl = n.runtimeLineage, idx = runtimeSkills.indexOf(rl.skillId);
      if (idx < 0) { bad.push(`${n.id}:missing ${rl.skillId}`); continue; }
      if (n.seriesId !== 'sword' || n.stage !== idx + 1 || n.slot !== 1) bad.push(`${n.id}:stage/slot`);
      if (n.energyCost !== 10 + 3 * (idx + 1)) bad.push(`${n.id}:runtimeCost`);
      const zhOk = ctx.appState.includes(`"${rl.nameKey}": "${n.name}"`), enOk = ctx.appState.includes(`"${rl.nameKey}": "${n.nameEn}"`);
      if (!zhOk || !enOk) bad.push(`${n.id}:runtimeName`);
      seen.push(`${n.id}=${rl.skillId}`);
    }
    for (const sk of runtimeSkills) if (!nodes.some(n => n.runtimeLineage && n.runtimeLineage.skillId === sk)) bad.push(`unmapped ${sk}`);
    add('runtime-lineage', '运行时已有的 2 个剑术 MVP 技能（growth_rules.gd / app_state.gd，只读）保留其阶、名称与当前能量消耗（10 + 3 × 阶）',
      bad.length === 0, bad.length ? bad.join('; ') : seen.join(', '));
  }

  // 22 source hashes (drift is a warning, not a failure)
  {
    const drift = [];
    for (const [k, src] of Object.entries(p.sources)) {
      if (!src.sha256) continue;
      try { if (ctx.hashOf(src.path) !== src.sha256) drift.push(k); } catch (e) { drift.push(`${k}:missing`); }
    }
    add('source-hashes', '记录的来源文件 sha256-text-lf-v1 与当前文件一致（不一致只记为 warn：来源已在本提案之后被他人修改）',
      drift.length === 0, drift.length ? `drift: ${drift.join(', ')}` : `${Object.values(p.sources).filter(s => s.sha256).length} 个来源一致`, 'warn');
  }

  // 23 embedded results (CLI only)
  if (opts.compareEmbedded) {
    const emb = (p.validation && p.validation.checks) || [];
    const key = c => `${c.id}|${c.result}|${c.detail}`;
    const a = checks.map(key), b = emb.map(key);
    const diff = a.filter(x => !b.includes(x)).concat(b.filter(x => !a.includes(x)));
    add('embedded-results-match', '文件内嵌的校验结果与本次重新计算的结果逐项一致（id、结果、细节）',
      diff.length === 0, diff.length ? `差异 ${diff.length} 项：${diff.slice(0, 4).join(' / ')}` : `${b.length} 项一致`);
  }

  const metrics = computeMetrics(p);
  const failed = checks.filter(c => c.result === 'fail').length;
  const warned = checks.filter(c => c.result === 'warn').length;
  return {passed: checks.filter(c => c.result === 'pass').length, failed, warned, total: checks.length, checks, metrics};
}

// Deterministic, informational: how cooldowns bound throughput as energy grows without a level cap.
function computeMetrics(p) {
  const battleSec = p.validationParameters.metricsBattleSeconds;
  const out = {};
  for (const s of p.series) {
    const actives = s.nodes.filter(n => n.type === 'active');
    const castsAll = actives.map(n => Math.floor(battleSec / n.cooldownSec) + 1);
    const energyAllCooldownBound = actives.reduce((acc, n, i) => acc + castsAll[i] * n.energyCost, 0);
    const levelForPool = Math.max(1, Math.ceil((energyAllCooldownBound - 60) / 2) + 1);
    out[s.id] = {
      activeCount: actives.length,
      castsPerBattleIfOnCooldown: Object.fromEntries(actives.map((n, i) => [n.id, castsAll[i]])),
      energyToCastEverythingOnCooldown: energyAllCooldownBound,
      levelWhereLowPoolCoversIt: levelForPool,
    };
  }
  return {battleSeconds: battleSec, energyPoolModel: '60 + 2 × (level − 1)（运行时下限 60–80，取 60）', perSeries: out};
}

module.exports = {runChecks, loadContext, schemaErrors, textSha256, SOURCE_PATHS};

if (require.main === module) {
  const rel = process.argv[2] || DEFAULT_PROPOSAL;
  const abs = path.isAbsolute(rel) ? rel : path.join(ROOT, rel);
  const proposal = JSON.parse(fs.readFileSync(abs, 'utf8'));
  const ctx = loadContext();
  const res = runChecks(proposal, ctx, {compareEmbedded: true});
  for (const c of res.checks) console.log(`${c.result.toUpperCase().padEnd(4)} ${c.id} — ${c.detail}`);
  console.log(`proposal sha256-text-lf-v1 ${textSha256(fs.readFileSync(abs))}`);
  console.log(`${res.passed}/${res.total} pass, ${res.warned} warn, ${res.failed} fail`);
  process.exit(res.failed === 0 ? 0 : 1);
}
