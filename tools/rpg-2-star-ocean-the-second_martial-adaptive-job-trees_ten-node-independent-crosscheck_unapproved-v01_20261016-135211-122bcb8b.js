// Worlds Between — independent cross-check of the 武艺 + 应变 ten-node job-tree PROPOSALS (unapproved).
// Written separately from the two companion validators; read-only, no dependencies.
// Compares both proposals with the approved roster, Game Bible jobProposal.series, the runtime skeleton
// catalog, runtime MVP skill names/costs, the 研学 proposal and all personal skill names, and checks the
// 100-node rules (10 series × 5 tiers × 2, rank max 5, JP for ranks 2–5 only, no exclusive branches).
// WARN = a provisional cross-proposal balance difference recorded in the QA notes (not a data error).
// Usage: node <this file> [repoRoot]   (default: the folder above tools/). Exit 1 only on FAIL.
'use strict';
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = process.argv[2] || path.resolve(__dirname, '..');
const P = (r) => path.join(root, r);
const load = (r) => JSON.parse(fs.readFileSync(P(r), 'utf8'));
const lfHash = (r) => crypto.createHash('sha256').update(fs.readFileSync(P(r), 'utf8').replace(/\r\n/g, '\n')).digest('hex');

const F = {
  martial: 'outputs/rpg-2-star-ocean-the-second_martial-job-trees_ten-node-skill-proposal_unapproved-v01_20261016-112044-4e3b550a.json',
  adaptive: 'outputs/rpg-2-star-ocean-the-second_adaptive-job-trees_ten-node-skill-proposal_unapproved-v01_20261016-112114-ec58fa23.json',
  research: 'outputs/rpg-2-star-ocean-the-second_research-job-trees_ten-node-skill-proposal_unapproved-v01_20261015-232143-842e0540.json',
  roster: 'outputs/rpg-2-star-ocean-the-second_all-jobs_five-tier-proposal_v01_20261013-224236-6f2b9c11.json',
  bible: 'outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json',
  catalog: 'game/data/growth/rpg-2-star-ocean-the-second_progression-ten-node_science-mvp-skeleton_v01_20261016-005300-e36e5d2c.json',
  personal: 'outputs/rpg-2-star-ocean-the-second_core-cast_personal-skills-ten-node-proposal_hero-c01-c03-v01_20261015-232129-dfc60394.json',
};
const M = load(F.martial), A = load(F.adaptive), RS = load(F.research);
const roster = load(F.roster), G = load(F.bible), CAT = load(F.catalog), PERS = load(F.personal);

const results = [];
const check = (id, ok, detail, level) => { results.push({ id, ok, detail, level: ok ? 'PASS' : (level || 'FAIL') }); };

// ---------- 1. Approved roster / Game Bible verbatim ----------
const rosterById = Object.fromEntries(roster.series.map((s) => [s.id, s]));
const bibleById = Object.fromEntries(G.jobProposal.series.map((s) => [s.id, s]));
const EXPECT = { martial: ['guardian', 'sword', 'heavy', 'martial', 'polearm'], adaptive: ['archery', 'firearms', 'skirmish', 'beast', 'merchant'] };
const APT = { martial: '武艺', adaptive: '应变' };
{
  const errs = [];
  for (const [k, doc] of [['martial', M], ['adaptive', A]]) {
    const ids = doc.series.map((s) => s.id);
    if (JSON.stringify(ids) !== JSON.stringify(EXPECT[k])) errs.push(`${k} ids ${ids}`);
    const rosterIds = roster.series.filter((s) => s.aptitude === APT[k]).map((s) => s.id);
    if (JSON.stringify(rosterIds) !== JSON.stringify(EXPECT[k])) errs.push(`${k} roster aptitude group ${rosterIds}`);
    for (const s of doc.series) {
      for (const src of [['roster', rosterById[s.id]], ['bible', bibleById[s.id]]]) {
        const r = src[1];
        if (!r) { errs.push(`${s.id} missing in ${src[0]}`); continue; }
        for (const f of ['aptitude', 'name', 'en', 'role', 'finalQuest']) if (s[f] !== r[f]) errs.push(`${s.id}.${f} != ${src[0]} (${JSON.stringify(s[f])} vs ${JSON.stringify(r[f])})`);
        if (JSON.stringify(s.stages) !== JSON.stringify(r.stages)) errs.push(`${s.id}.stages != ${src[0]}`);
      }
      for (const n of s.nodes) if (n.stageName !== s.stages[n.stage - 1]) errs.push(`${n.id} stageName ${n.stageName}`);
    }
  }
  // roster and Bible agree with each other for all 20
  for (const r of roster.series) {
    const b = bibleById[r.id];
    if (!b || JSON.stringify([r.name, r.en, r.stages, r.finalQuest]) !== JSON.stringify([b.name, b.en, b.stages, b.finalQuest])) errs.push(`roster/bible disagree ${r.id}`);
  }
  // runtime catalog Chinese stage names agree too
  for (const s of [...M.series, ...A.series]) {
    const c = CAT.series.find((x) => x.id === s.id);
    if (!c) errs.push(`catalog missing ${s.id}`);
    else if (JSON.stringify(c.stageNamesZh) !== JSON.stringify(s.stages) || c.nameZh !== s.name) errs.push(`catalog names differ ${s.id}`);
  }
  check('approved-text-vs-roster-bible-catalog', errs.length === 0, errs.length ? errs.join('; ') : '10 series: aptitude/name/en/role/5 stages/finalQuest == roster == Game Bible jobProposal.series; 100 stageNames ok; catalog zh names agree');
}

// ---------- 2. 100 nodes, 2 per tier, rank 5, unlock & JP ----------
const allNodes = [];
for (const [k, doc] of [['martial', M], ['adaptive', A]]) for (const s of doc.series) for (const n of s.nodes) allNodes.push({ k, s, n });
{
  const errs = [];
  for (const [k, doc] of [['martial', M], ['adaptive', A]]) for (const s of doc.series) {
    if (s.nodes.length !== 10) errs.push(`${s.id} has ${s.nodes.length}`);
    for (let t = 1; t <= 5; t++) {
      const tier = s.nodes.filter((n) => n.stage === t);
      if (tier.length !== 2) errs.push(`${s.id} tier ${t} has ${tier.length}`);
      const slots = tier.map((n) => n.slot).sort().join(',');
      if (slots !== '1,2') errs.push(`${s.id} tier ${t} slots ${slots}`);
    }
  }
  for (const { n } of allNodes) {
    if (n.maxRank !== 5) errs.push(`${n.id} maxRank ${n.maxRank}`);
    const u = n.unlock || {};
    if (u.onStageEntry !== true || u.jpCost !== 0) errs.push(`${n.id} unlock ${JSON.stringify(u)}`);
    if ('unlockedAtRank' in u && u.unlockedAtRank !== 1) errs.push(`${n.id} unlockedAtRank`);
    if (u.requiresFinalQuest !== (n.stage === 5)) errs.push(`${n.id} finalQuest gate ${u.requiresFinalQuest} at stage ${n.stage}`);
    if ('levelGate' in u || 'requiresLevel' in u) errs.push(`${n.id} level gate`);
    for (const sc of n.scaling || []) if (!Array.isArray(sc.values) || sc.values.length !== 5) errs.push(`${n.id}.${sc.key} values len`);
    if (!n.scaling || n.scaling.length === 0) errs.push(`${n.id} no scaling`);
    const rp = Object.keys(n.rankProgression || {}).sort().join(',');
    if (rp !== '2,3,4,5') errs.push(`${n.id} rankProgression keys ${rp}`);
  }
  for (const [k, doc] of [['martial', M], ['adaptive', A]]) {
    const t = doc.jpProposal.rankUpgradeBaseJp;
    if (Object.keys(t).sort().join(',') !== '2,3,4,5') errs.push(`${k} JP keys`);
    if (doc.jpProposal.unlockJp !== 0) errs.push(`${k} unlockJp`);
    if (doc.jpProposal.status !== 'PROPOSAL') errs.push(`${k} jp status`);
  }
  check('hundred-nodes-two-per-tier-rank5-jp-upgrade-only', errs.length === 0, errs.length ? errs.join('; ') : `${allNodes.length} nodes = 10 series × 5 tiers × 2; maxRank 5; unlock at rank 1 for 0 JP on stage entry; JP keys 2–5 only; final-quest gate exactly on tier 5`);
}

// ---------- 3. No exclusive branches (deep key + text scan) ----------
{
  const badKeys = []; const badText = [];
  const keyRe = /branch|exclusive|mutual|choice|chooseOne|either/i;
  const walk = (o, p) => {
    if (Array.isArray(o)) o.forEach((v, i) => walk(v, `${p}[${i}]`));
    else if (o && typeof o === 'object') for (const [k, v] of Object.entries(o)) { if (keyRe.test(k)) badKeys.push(`${p}.${k}`); walk(v, `${p}.${k}`); }
    else if (typeof o === 'string' && /二选一|互斥|只能选择其一|择一|choose one|mutually exclusive/i.test(o)) badText.push(p);
  };
  for (const { n } of allNodes) walk(n, n.id);
  check('no-exclusive-branches', badKeys.length + badText.length === 0, badKeys.length + badText.length ? `keys: ${badKeys.join(', ')} text: ${badText.join(', ')}` : '0 branch/exclusive keys and 0 exclusive-choice phrases in 100 nodes; file rules: martial exclusiveBranches=' + M.rules.exclusiveBranches);
}

// ---------- 4. Provisional marking; no approval / implementation / art-done claims ----------
{
  const errs = [];
  for (const [k, doc] of [['martial', M], ['adaptive', A]]) {
    if (doc.status !== 'PROPOSAL' || !/pending/.test(doc.reviewStatus)) errs.push(`${k} file status`);
    if (!/未修改运行时|not/.test(doc.notImplemented || '')) errs.push(`${k} notImplemented missing`);
  }
  for (const { n } of allNodes) if (n.status !== 'PROPOSAL' || !/pending/.test(n.reviewStatus || '')) errs.push(`${n.id} status`);
  // claims: scan node strings for approval / implemented / art-complete wording
  const claimRe = /已批准|已获批|创作者批准|approved|已实现|已上线|implemented|美术完成|已完成美术|art (is )?(done|complete|final)|final art|定稿/i;
  const hits = [];
  const walk = (o, p) => {
    if (Array.isArray(o)) o.forEach((v, i) => walk(v, `${p}[${i}]`));
    else if (o && typeof o === 'object') for (const [k, v] of Object.entries(o)) walk(v, `${p}.${k}`);
    else if (typeof o === 'string' && claimRe.test(o)) hits.push(`${p}: ${o.slice(0, 120)}`);
  };
  for (const { n } of allNodes) walk(n, n.id);
  // file-level text excluding schema/validation
  for (const [k, doc] of [['martial', M], ['adaptive', A]]) for (const key of Object.keys(doc)) if (!['series', 'schema', 'validation'].includes(key)) walk(doc[key], `${k}.${key}`);
  check('proposal-only-no-approval-claims', errs.length === 0, `${errs.join('; ') || '100/100 nodes + 2 files PROPOSAL/pending'}; claim-word hits for manual review: ${hits.length}`);
  results[results.length - 1].hits = hits;
}

// ---------- 5. Name / id uniqueness across all 150 job nodes + personal names ----------
{
  const errs = [];
  const research = []; for (const s of RS.series) for (const n of s.nodes) research.push(n);
  const pool = [...allNodes.map((x) => x.n), ...research];
  for (const f of ['id', 'name', 'nameEn']) {
    const seen = new Map();
    for (const n of pool) { const v = String(n[f]).toLowerCase(); if (seen.has(v)) errs.push(`dup ${f} "${n[f]}" ${seen.get(v)} / ${n.id}`); else seen.set(v, n.id); }
  }
  // personal skill names: Game Bible character cards + superseded personal trees + core-cast personal proposal
  const pnames = new Set();
  for (const c of G.characters) for (const re of [/独有技能——([^：:*]+)/g, /专属个人技能提案——([^：:*]+)/g, /个人技能「([^」]+)」/g]) for (const m of (c.body || '').matchAll(re)) pnames.add(m[1].trim());
  const cardCount = pnames.size;
  for (const t of (G.personalSkillTrees.trees || [])) for (const n of t.nodes || []) pnames.add(n.name);
  for (const t of PERS.trees) for (const n of t.nodes) pnames.add(n.nameZh);
  const clash = allNodes.filter(({ n }) => pnames.has(n.name)).map(({ n }) => n.id + '=' + n.name);
  errs.push(...clash.map((c) => 'personal clash ' + c));
  check('unique-names-across-150-job-nodes-and-personal', errs.length === 0, errs.length ? errs.join('; ') : `150 job nodes (武艺+应变+研学): unique id/zh/en; 0 clashes with ${pnames.size} personal names (${cardCount} character-card signature skills, superseded 5-node trees, core-cast 10-node proposal)`);
}

// ---------- 6. rankProgression and baseEffect agree with scaling values; non-accelerating ----------
{
  const errs = []; let maxRatio = 0, maxAt = '';
  const fmt = (v) => String(Math.round(v * 1000) / 1000);
  for (const { n } of allNodes) {
    for (const sc of n.scaling) {
      const v = sc.values;
      for (let r = 2; r <= 5; r++) if (!String(n.rankProgression[r]).includes(fmt(v[r - 1]))) errs.push(`${n.id} r${r} text lacks ${v[r - 1]} (${sc.key})`);
      if (!n.baseEffect.includes(fmt(v[0])) && !n.baseEffect.includes(fmt(Math.abs(v[0])))) errs.push(`${n.id} baseEffect lacks r1 ${v[0]} (${sc.key})`);
      const d = v.slice(1).map((x, i) => Math.round((x - v[i]) * 1e6) / 1e6);
      const sign = Math.sign(d[0]);
      if (d.some((x) => Math.sign(x) !== sign && x !== 0)) errs.push(`${n.id}.${sc.key} non-monotone`);
      for (let i = 1; i < d.length; i++) if (Math.abs(d[i]) > Math.abs(d[i - 1]) + 1e-9) errs.push(`${n.id}.${sc.key} accelerating ${d}`);
      if (v[0] !== 0) { const ratio = Math.abs(v[4] / v[0]); if (sc.direction !== 'lower_is_better' && ratio > maxRatio) { maxRatio = ratio; maxAt = n.id + '.' + sc.key; } if (sc.direction !== 'lower_is_better' && ratio > 2 + 1e-9) errs.push(`${n.id}.${sc.key} r5/r1 ${ratio}`); }
    }
  }
  check('rank-text-matches-values-and-curves', errs.length === 0, errs.length ? errs.slice(0, 30).join('; ') + (errs.length > 30 ? ` …(+${errs.length - 30})` : '') : `every r2–r5 text and r1 baseEffect carries its scaling value; all steps flat/shrinking; max r5/r1 ${maxRatio.toFixed(2)} (${maxAt})`);
}

// ---------- 7. Energy / cooldown sanity vs stage bands; actives vs passives ----------
{
  const errs = []; const bands = M.validationParameters.energyBandsByStage;
  if (JSON.stringify(bands) !== JSON.stringify(A.validationParameters.energyBandsByStage) || JSON.stringify(bands) !== JSON.stringify(RS.validationParameters.energyBandsByStage)) errs.push('energy bands differ across the three proposals');
  for (const { n } of allNodes) {
    if (n.type === 'active') {
      const [lo, hi] = bands[n.stage];
      if (!(n.energyCost >= lo && n.energyCost <= hi)) errs.push(`${n.id} energy ${n.energyCost} outside ${lo}-${hi}`);
      if (!(n.cooldownSec > 0)) errs.push(`${n.id} cooldown ${n.cooldownSec}`);
    } else if (n.type === 'passive') { if (n.energyCost != null && n.energyCost !== 0) errs.push(`${n.id} passive with energy`); }
    else errs.push(`${n.id} type ${n.type}`);
    if (n.rangePx != null && n.rangePx > 584) errs.push(`${n.id} range ${n.rangePx} > field 584`);
  }
  for (const s of [...M.series, ...A.series]) for (let t = 1; t <= 5; t++) if (!s.nodes.some((n) => n.stage === t && n.type === 'active')) errs.push(`${s.id} tier ${t} no active`);
  check('energy-bands-and-field-range', errs.length === 0, errs.length ? errs.join('; ') : 'identical energy bands in 研学/武艺/应变; every active inside its stage band with cooldown > 0; passives cost 0; every tier has an active; all ranges ≤ 584 px field');
}

// ---------- 8. JP table / caps consistency across the three proposals (provisional) ----------
{
  const errs = []; const notes = [];
  const jt = (d) => JSON.stringify(d.jpProposal.rankUpgradeBaseJp);
  if (jt(M) !== jt(A) || jt(A) !== jt(RS)) errs.push(`JP tables differ: R ${jt(RS)} M ${jt(M)} A ${jt(A)}`);
  const runtime = JSON.stringify(CAT.rules.upgradeJpBase);
  notes.push(`proposal JP ${jt(M)} vs runtime catalog ${runtime} (${CAT.rules.upgradeJpBaseStatus})`);
  const mFlag = /35\/55\/80\/110/.test(M.jpProposal.conflictNote || ''), aFlag = /35/.test(JSON.stringify(A.jpProposal.runtimeDifference || ''));
  if (!mFlag || !aFlag) errs.push(`runtime JP divergence not stated (martial ${mFlag}, adaptive ${aFlag})`);
  check('jp-table-shared-and-divergence-flagged', errs.length === 0, (errs.join('; ') || 'R/M/A share the provisional JP table; both files state the runtime-catalog divergence') + '; ' + notes.join('; '));
}

// ---------- 9. Runtime lineage vs catalog / runtime cost ----------
{
  const errs = []; const lines = [];
  const catNodes = new Map(); for (const s of CAT.series) for (const n of s.nodes) catNodes.set(n.id, { ...n, series: s.id });
  for (const { s, n } of allNodes) {
    const rid = n.runtimeCatalogNodeId || (n.runtimeLineage && (n.runtimeLineage.runtimeId || n.runtimeLineage.id || n.runtimeLineage.skillId || n.runtimeLineage.catalogNodeId));
    if (n.runtimeLineage) lines.push(`${n.id}→${JSON.stringify(n.runtimeLineage).slice(0, 140)}`);
    if (rid) {
      const c = catNodes.get(rid);
      if (!c) errs.push(`${n.id} → unknown catalog id ${rid}`);
      else {
        if (c.series !== s.id) errs.push(`${n.id} → ${rid} wrong series`);
        if (c.stage !== n.stage) errs.push(`${n.id} stage ${n.stage} → ${rid} stage ${c.stage}`);
        const slot = { a: 1, b: 2 }[c.slot];
        if (slot !== n.slot) errs.push(`${n.id} slot ${n.slot} → ${rid} slot ${c.slot}`);
      }
    }
  }
  // catalog nodes with real runtime effect for these 10 series must each be claimed by a proposal node
  const claimed = new Set(allNodes.map(({ n }) => n.runtimeCatalogNodeId || (n.runtimeLineage && JSON.stringify(n.runtimeLineage))).filter(Boolean).join('|').match(/[a-z_0-9]+/g));
  for (const s of CAT.series.filter((x) => [...EXPECT.martial, ...EXPECT.adaptive].includes(x.id))) for (const c of s.nodes) if (c.status !== 'skeleton-pending-design' && !claimed.has(c.id)) errs.push(`runtime node ${c.id} (${c.status}) not mapped`);
  check('runtime-lineage-vs-catalog', errs.length === 0, (errs.join('; ') || 'every mapped catalog id exists with matching series/stage/slot; every runtime-backed catalog node in the 10 series is claimed') + ' | martial lineage: ' + lines.join('; '));
}

// ---------- 10. Canon scans: geography, reputation, banned systems ----------
{
  const errs = [];
  const text = (o) => JSON.stringify(o);
  const nodesText = (doc) => text(doc.series);
  const stale = /上海|松江|良渚|长三角|Shanghai|Songjiang|Liangzhu|星外|奇幻|玛瑙斯|好奇（|勇气（|同理（|好奇记录|勇气记录|同理记录/;
  for (const [k, doc] of [['martial', M], ['adaptive', A]]) { const m = nodesText(doc).match(new RegExp(stale.source, 'g')); if (m) errs.push(`${k} stale canon terms: ${[...new Set(m)]}`); }
  // reputation words used must be approved five
  const repUsed = new Set(); for (const [, doc] of [['m', M], ['a', A]]) for (const m of nodesText(doc).matchAll(/(求知|果敢|共情|公正|守诺|好奇|勇气|同理)[”」"\\]*(行为)?(记录|声望|名声)/g)) repUsed.add(m[1]);
  for (const r of repUsed) if (!['求知', '果敢', '共情', '公正', '守诺'].includes(r)) errs.push(`unapproved reputation name ${r}`);
  // MVP utility places must be from the approved US science MVP place set
  const okPlace = /市政厅公园|City Hall Park|扬克斯|Yonkers|华盛顿|国会大厦|Capitol|芝加哥|卢普|Loop|纽约|NYC/;
  const places = [];
  for (const { n } of allNodes) if (n.scienceMvpUtility) {
    const u = n.scienceMvpUtility; const locs = u.locations || u.mvpLocations || u.places || [];
    if (!locs.length) errs.push(`${n.id} utility without places`);
    for (const l of locs) { places.push(l); if (!okPlace.test(l)) errs.push(`${n.id} place ${l}`); }
    const t = text(u);
    if (u.storyMandatory !== false && !/可选|optional|不是唯一|并非唯一/.test(t)) errs.push(`${n.id} utility not marked optional`);
    if (/捷径|shortcut|新路线|唯一途径|必须/.test(t.replace(/不是唯一|并非唯一|不是.*唯一/g, ''))) errs.push(`${n.id} utility gating wording: ${t.slice(0, 100)}`);
  }
  // AI: no consumables
  for (const { n } of allNodes) { const ai = text(n.ai || n.aiBehavior); if (!ai || ai === 'undefined') errs.push(`${n.id} no AI`); if (/使用(道具|消耗品)|服用|喝下|药水/.test(ai)) errs.push(`${n.id} AI uses items`); }
  check('canon-geography-reputation-ai', errs.length === 0, (errs.join('; ') || 'no superseded Shanghai/Songjiang/Liangzhu/星外/奇幻 or misspelt reputation/Manaus terms; reputation words ⊂ {求知,果敢,共情,公正,守诺}; utility places ⊂ US science MVP set; utilities optional; 100/100 AI present, none uses items') + ` | reputation used: ${[...repUsed]} | places: ${[...new Set(places)].join(' / ')}`);
}

// ---------- 11. Heal / revive AI ordering (creator §3) ----------
{
  const errs = []; const seen = [];
  for (const { n } of allNodes) {
    const t = n.baseEffect + ' ' + (n.summaryEn || '');
    const heals = /恢复.*(HP|生命)|治疗|heal/i.test(t) && !/不恢复|不治疗/.test(t);
    const revive = /复活|revive/i.test(t) && !/不复活|不能复活|does not revive|cannot revive/i.test(t);
    if (heals || revive) {
      const ai = JSON.stringify(n.ai || n.aiBehavior);
      const selfOnly = /自身|仅自己|self/.test(n.target || '') ;
      seen.push(`${n.id}(${n.name}; target ${n.target}; ${selfOnly ? 'self' : 'party'})`);
      if (!selfOnly && !/倒下/.test(ai)) errs.push(`${n.id} party heal AI lacks downed-ally rule`);
    }
  }
  check('heal-ai-downed-first', errs.length === 0, (errs.join('; ') || 'party heals defer to downed-ally handling') + ' | heal nodes: ' + seen.join('; '));
}

// ---------- 12. Cross-proposal cap consistency (same quantity, different limits?) ----------
{
  const mc = M.rules.stackingCaps; const ac = A.validationParameters.stackingCapsPct;
  const pairs = [['enemy_damage_taken_up', 'enemyDamageTaken'], ['enemy_defense_down', 'enemyDefenseDown'], ['enemy_slow', 'enemyMoveSlow'], ['ally_damage_reduction', 'allyDamageReduction'], ['damage_redirect', 'allyDamageRedirect']];
  const diffs = pairs.filter(([m, a]) => mc[m].limit !== ac[a]).map(([m, a]) => `${m} ${mc[m].limit} vs ${a} ${ac[a]}`);
  // worst case: rank-5 guardian redirect + rank-5 beast redirect on the same hit
  const r5 = (doc, sid, pred) => doc.series.find((s) => s.id === sid).nodes.flatMap((n) => (n.scaling || []).filter((sc) => pred(n, sc)).map((sc) => `${n.name} ${sc.values[4]}`));
  const g = r5(M, 'guardian', (n, sc) => sc.capCategory === 'damage_redirect');
  const b = A.series.find((s) => s.id === 'beast').nodes.flatMap((n) => (n.caps || []).filter((c) => c.category === 'allyDamageRedirect').map((c) => `${n.name} ${c.rank5Value}`));
  const combineStated = /兽伴|beast|驯兽/.test(mc.damage_redirect.zh + JSON.stringify(M.rules.stacking)) || /守护|guardian|护线/.test(A.rules.stacking);
  check('cross-proposal-cap-consistency', diffs.length === 0 || combineStated, (diffs.length ? 'differs: ' + diffs.join('; ') : 'shared cap categories agree') + ` | guardian redirect r5: ${g.join(', ')} | beast redirect r5: ${b.join(', ')} | combination rule stated in either file: ${combineStated}`, 'WARN');
  // energy-return ceilings differ between the three proposals
  const mRet = M.rules.stackingCaps.energy_return.limit;
  const aNone = /没有凭空返还能量的节点/.test(A.rules.energy);
  const rRet = [...JSON.stringify(RS.series).matchAll(/合计最多返还 (\d+) 点|返还 (\d+) 点能量；每场战斗最多触发 (\d+) 次/g)].map((m) => Number(m[1] || m[2] * m[3]));
  const rMax = Math.max(0, ...rRet);
  check('cross-proposal-energy-return-ceiling', mRet === rMax || (!mRet && !rMax), `per-node energy return per battle: 武艺 ≤ ${mRet}; 研学 max ${rMax}; 应变 ${aNone ? 'none (no refund nodes)' : '?'}`, 'WARN');
}

// ---------- 13. Independent JSON Schema (2020-12 subset) validation against each embedded schema ----------
function validate(schema, data, rootSchema, p, errs) {
  if (schema.$ref) { const ref = schema.$ref.replace(/^#\//, '').split('/').reduce((o, k) => o[k], rootSchema); return validate(ref, data, rootSchema, p, errs); }
  const typeOf = (v) => v === null ? 'null' : Array.isArray(v) ? 'array' : Number.isInteger(v) ? 'integer' : typeof v;
  if (schema.type) {
    const types = [].concat(schema.type); const t = typeOf(data);
    if (!types.some((x) => x === t || (x === 'number' && t === 'integer'))) { errs.push(`${p}: type ${t} not ${types}`); return; }
  }
  if ('const' in schema && JSON.stringify(schema.const) !== JSON.stringify(data)) errs.push(`${p}: const`);
  if (schema.enum && !schema.enum.some((e) => JSON.stringify(e) === JSON.stringify(data))) errs.push(`${p}: enum ${JSON.stringify(data)}`);
  if (typeof data === 'number') {
    if ('minimum' in schema && data < schema.minimum) errs.push(`${p}: < minimum`);
    if ('maximum' in schema && data > schema.maximum) errs.push(`${p}: > maximum`);
    if ('exclusiveMinimum' in schema && data <= schema.exclusiveMinimum) errs.push(`${p}: <= exclusiveMinimum`);
  }
  if (typeof data === 'string') {
    if ('minLength' in schema && [...data].length < schema.minLength) errs.push(`${p}: minLength`);
    if (schema.pattern && !new RegExp(schema.pattern, 'u').test(data)) errs.push(`${p}: pattern ${schema.pattern}`);
  }
  if (Array.isArray(data)) {
    if ('minItems' in schema && data.length < schema.minItems) errs.push(`${p}: minItems`);
    if ('maxItems' in schema && data.length > schema.maxItems) errs.push(`${p}: maxItems`);
    if (schema.items) data.forEach((v, i) => validate(schema.items, v, rootSchema, `${p}[${i}]`, errs));
  }
  if (data && typeof data === 'object' && !Array.isArray(data)) {
    for (const r of schema.required || []) if (!(r in data)) errs.push(`${p}: missing ${r}`);
    const props = schema.properties || {};
    for (const [k, v] of Object.entries(data)) {
      if (props[k]) validate(props[k], v, rootSchema, `${p}.${k}`, errs);
      else if (schema.additionalProperties === false) errs.push(`${p}: extra ${k}`);
      else if (schema.additionalProperties && typeof schema.additionalProperties === 'object') validate(schema.additionalProperties, v, rootSchema, `${p}.${k}`, errs);
    }
  }
}
{
  const out = [];
  let ok = true;
  for (const [k, doc] of [['martial', M], ['adaptive', A]]) {
    const errs = []; validate(doc.schema, doc, doc.schema, k, errs);
    // node key-set uniformity (catches optional-field drift the schema may allow)
    const sets = new Map(); for (const s of doc.series) for (const n of s.nodes) { const ks = Object.keys(n).filter((x) => x !== 'caps' && x !== 'energyTransfer' && x !== 'commerceContext' && x !== 'runtimeNote').join(','); sets.set(ks, (sets.get(ks) || 0) + 1); }
    if (errs.length) ok = false;
    out.push(`${k}: ${errs.length} schema errors${errs.length ? ' [' + errs.slice(0, 10).join('; ') + ']' : ''}; ${sets.size} node key-shape(s)`);
  }
  check('independent-embedded-schema-validation', ok, out.join(' | '));
}

// ---------- 14. Runtime MVP skill names / energy carried forward unchanged ----------
{
  const errs = [];
  const appState = fs.readFileSync(P('game/scripts/app_state.gd'), 'utf8');
  const arena = fs.readFileSync(P('game/scripts/battle_arena.gd'), 'utf8');
  if (!/var cost := 10 \+ 3 \* skill_stage/.test(arena)) errs.push('arena cost formula changed');
  const want = [
    [M, 'sword_n01_edge_break', 'sword_slash'], [M, 'sword_n03_sword_arc', 'sword_arc'],
    [A, 'firearms_n01_precision_shot', 'firearms_shot'], [A, 'firearms_n03_suppressive_burst', 'firearms_burst'],
    [A, 'merchant_n01_supply_pact', 'merchant_supply_pact'], [A, 'merchant_n03_fair_quote', 'merchant_fair_quote'],
  ];
  const lines = [];
  for (const [doc, nid, rid] of want) {
    const n = doc.series.flatMap((s) => s.nodes).find((x) => x.id === nid);
    if (!n) { errs.push(`missing ${nid}`); continue; }
    const zh = new RegExp(`"job_skill_${rid}": "([^"]+)"`, 'g'); const names = [...appState.matchAll(zh)].map((m) => m[1]);
    if (names[0] !== n.name || names[1] !== n.nameEn) errs.push(`${nid} name ${n.name}/${n.nameEn} vs runtime ${names}`);
    if (n.type === 'active' && ['sword', 'firearms'].includes(n.seriesId) && n.energyCost !== 10 + 3 * n.stage) errs.push(`${nid} energy ${n.energyCost} vs runtime ${10 + 3 * n.stage}`);
    lines.push(`${n.name}/${n.nameEn} s${n.stage} ${n.type}${n.energyCost != null ? ' E' + n.energyCost : ''}`);
  }
  check('runtime-mvp-skills-carried-forward', errs.length === 0, (errs.join('; ') || 'zh/en names equal app_state.gd; battle energy equals 10 + 3 × stage') + ' | ' + lines.join('; '));
}

// ---------- output ----------
const count = { PASS: 0, WARN: 0, FAIL: 0 };
for (const r of results) { count[r.level]++; console.log(`${r.level}  ${r.id}  ${r.detail}`); if (r.hits && r.hits.length) for (const h of r.hits) console.log('      claim-scan (benign if source/roster reference): ' + h); }
console.log(`hashes (sha256-text-lf-v1): martial ${lfHash(F.martial)} adaptive ${lfHash(F.adaptive)} roster ${lfHash(F.roster)} bible ${lfHash(F.bible)}`);
console.log(`${count.PASS}/${results.length} pass, ${count.WARN} warn, ${count.FAIL} fail`);
process.exitCode = count.FAIL === 0 ? 0 : 1;
