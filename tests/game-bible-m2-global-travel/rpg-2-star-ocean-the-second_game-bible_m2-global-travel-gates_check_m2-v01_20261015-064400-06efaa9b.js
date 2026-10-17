// Focused check for the Game Bible M2 global-travel gates, the scoped approval ledger and the candidate/blocked decision list.
// Reflects the creator decisions of 2026-10-15 (NYC science hub, Catskills community, start 2537-05-25, NYC-Chicago first air route,
// five Earth spheres plus a portal final planet, Washington, D.C. Capitol Pixelorama pilot) and the US runtime migration that followed:
// the anchor, start-year and air-route gates are implemented technical candidates, M2 stays in progress, and no art, route-figure or
// human acceptance is claimed. The provisional v01 (Shanghai) travel file is checked as an unchanged record only.
// 2026-10-16: the route-data gate is the implemented "Route times (whole-hour rule)" gate (fixed whole hours, date-only calendar);
// M2 is 10/12 with map art and human review still open.
// Data audit first (counters, scopes, evidence paths, implemented vs open M2 gates, route figures cross-checked read-only against the
// active v02 game travel data), then the real v05 panel server on a
// spare local port renders the Production view in a VM with a minimal DOM stub. A second render feeds hostile/missing progress
// fields through an intercepted /state to check escaping and graceful omission. Read-only: no project file is written.
// Run from the repository root: node tests/game-bible-m2-global-travel/<this file>
const assert = require('node:assert/strict');
const fs = require('node:fs');
const net = require('node:net');
const path = require('node:path');
const vm = require('node:vm');
const {spawn} = require('node:child_process');

const root = path.resolve(__dirname, '..', '..');
const out = name => path.join(root, 'outputs', name);
const readJson = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const server = path.join(root, 'tools', 'rpg-2-star-ocean-the-second_game-bible_server_v05_20261013-222437-3d5b8a9f.js');
const progressPath = out('rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json');
const biblePath = out('rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json');
const inventoryPath = out('rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json');
const checklistPath = path.join(root, 'game', 'data', 'character-visuals', 'rpg-2-star-ocean-the-second_character-sprite-readiness-checklist_m8-v01_20261014-184413-53da3710.json');
const rulesDoc = 'docs/design/rpg-2-star-ocean-the-second_global-earth-map-real-place-travel_rules-v01_20261014-235354-2b5d4d98.md';
const packetDoc = 'docs/design/rpg-2-star-ocean-the-second_shanghai-liangzhu_geography-route-art-packet_provisional-v01_20261015-000319-a3e65b7c.md';
const airPacketDoc = 'docs/design/rpg-2-star-ocean-the-second_shanghai-cross-city-air-route_research-packet_unapproved-v01_20261015-031235-9d63971b.md';
const runV3Audit = 'docs/qa/rpg-2-star-ocean-the-second_protagonist-female_south-run-v3-build_pre-run-technical-audit_qa-note_m8-w03_20261015-071053-86f9c79f.md';
const creatorNote = 'docs/design/rpg-2-star-ocean-the-second_creator-decisions-2026-10-15_world-skills-ai-endgame_reconciliation-note_v01_20261015-174559-39efc292.md';
const usQaNote = 'docs/qa/rpg-2-star-ocean-the-second_us-science-sphere_runtime-migration_qa-note_m2-v02_20261015-175011-364131c8.md';
const usTravelData = 'game/data/world-travel/rpg-2-star-ocean-the-second_global-earth-travel_locations-routes_m2-us-science-v02_20261015-175011-c454007b.json';
const travelDataPath = path.join(root, usTravelData);
const provisionalTravelPath = path.join(root, 'game', 'data', 'world-travel', 'rpg-2-star-ocean-the-second_global-earth-travel_locations-routes_m2-provisional-v01_20261015-024215-b876e53d.json');
const gateOrder = ['map-ui', 'place-registry', 'route-preview', 'calendar', 'save-migration', 'acceptance-test', 'anchor', 'start-year', 'route-data', 'air-route', 'map-art', 'visual-review'];
const migratedGates = ['anchor', 'start-year', 'air-route'];
const openGates = {'map-art': 'not_started', 'visual-review': 'human_pending'};
const implementedGates = gateOrder.filter(id => !(id in openGates));
const usPlaces = ['earth.us.ny.new-york-city', 'earth.us.ny.yonkers-outskirts', 'earth.us.dc.washington-ruins', 'earth.us.il.chicago'];
const resolvedDecisionIds = ['first-city', 'world-start-year', 'air-route-pair', 'songjiang-label'];
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const pass = label => console.log('PASS ' + label);

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

// Optional stateOverride replaces the served /state body so hostile or missing fields can be rendered.
async function renderProduction(base, stateOverride) {
  const element = () => ({innerHTML: '', textContent: '', value: '', dataset: {}, addEventListener() {}, setAttribute() {}, querySelector: () => element(), querySelectorAll: () => []});
  const content = {...element(), querySelector: () => element()};
  const elements = {content, search: element(), edition: element(), pitch: element(), 'footer-status': element()};
  const nav = ['home', 'world', 'rules', 'characters', 'production', 'assets'].map(view => {
    const button = {...element(), dataset: {view}, handlers: {}};
    button.addEventListener = (type, handler) => { button.handlers[type] = handler; };
    return button;
  });
  const fetchFor = (url, options) => stateOverride && url.startsWith('/state')
    ? Promise.resolve(new Response(JSON.stringify(stateOverride), {headers: {'content-type': 'application/json'}}))
    : fetch(base + url, options);
  const context = vm.createContext({
    document: {getElementById: id => elements[id], querySelectorAll: () => nav, addEventListener() {}, hidden: true, createElement: () => element()},
    fetch: fetchFor, setInterval() {}, localStorage: {getItem: () => '', setItem() {}}, console,
  });
  vm.runInContext(await (await fetch(base + '/bible.js')).text(), context, {filename: 'bible.js'});
  await waitFor(() => elements.edition.textContent !== '', 'initial bible load');
  nav.find(button => button.dataset.view === 'production').handlers.click();
  await waitFor(() => content.innerHTML.includes('id="global-map-travel-rule"'), 'production view');
  return content.innerHTML;
}

const cardById = (html, id) => {
  const start = html.indexOf(`<section class="card" id="${id}">`);
  assert.ok(start > 0, id + ' card present');
  assert.equal(html.split(`id="${id}"`).length, 2, 'exactly one ' + id + ' card');
  return html.slice(start, html.indexOf('</section>', start) + '</section>'.length);
};

(async () => {
  const progress = readJson(progressPath);
  const bible = readJson(biblePath);

  // 1. Counters in the ledger equal the inventory and readiness checklist; none was incremented.
  const items = readJson(inventoryPath).categories.flatMap(c => c.subcategories.flatMap(s => s.items));
  const tally = p => { const list = items.filter(i => i.id.startsWith(p)); return [list.filter(i => i.checked).length, list.length]; };
  const checklist = readJson(checklistPath);
  const c = progress.approvalLedger.counters;
  assert.deepEqual(tally('runtime-sprite.'), [c.runtimeSpritesAccepted, c.runtimeSpritesTarget]);
  assert.deepEqual(tally('visual-scene.'), [c.sceneVisualsAccepted, c.sceneVisualsTarget]);
  assert.deepEqual([c.runtimeSpritesAccepted, c.runtimeSpritesTarget, c.sceneVisualsAccepted, c.sceneVisualsTarget, c.humanPlaytests, c.humanPlaytestsTarget], [0, 52, 0, 12, 0, 2]);
  assert.equal(checklist.scope.character_identities, c.identities);
  assert.equal(checklist.variants.length, c.visualVariants);
  assert.deepEqual([c.identities, c.visualVariants], [51, 52]);
  assert.equal(bible.environmentVisualReview.sceneQualityAccepted, 0);
  assert.equal(bible.environmentVisualReview.sceneQualityTarget, 12);
  pass('counters: sprites 0/52 and scenes 0/12 match the inventory; 51 identities / 52 variants match the checklist; human playtests 0/2');

  // 2. Approval scopes exactly as given: two scoped approvals, two direction acceptances, the animated variant not accepted.
  const byId = Object.fromEntries(progress.approvalLedger.items.map(i => [i.id, i]));
  assert.deepEqual(progress.approvalLedger.items.filter(i => i.status === 'approved').map(i => i.id).sort(), ['display-scale-48', 'female-v8-south-idle-static']);
  assert.ok(byId['female-v8-south-idle-static'].scope.includes('仅一张南向静态基准帧'));
  assert.equal(byId['female-four-direction-animated'].status, 'not_accepted');
  assert.ok(byId['female-four-direction-animated'].scope.includes('v3 跑步构建脚本未通过运行前技术审计') && byId['female-four-direction-animated'].evidence.includes(runV3Audit), 'run v3 failed its pre-run audit; animation still not accepted');
  assert.equal(byId['sentry-direction'].status, 'direction_accepted');
  assert.ok(byId['sentry-direction'].scope.includes('创作者已批准动画 v2 作为动作方向基准') && byId['sentry-direction'].scope.includes('不是完整精灵或美术验收') && byId['sentry-direction'].scope.includes('美术验收 0') && !byId['sentry-direction'].scope.includes('待审阅'), 'sentry v2: action-direction baseline only, art acceptance 0');
  assert.equal(byId['liangzhu-terrain-direction'].status, 'direction_accepted');
  assert.ok(byId['liangzhu-terrain-direction'].scope.includes('高精度像素场景未制作') && byId['liangzhu-terrain-direction'].scope.includes('v03／v04 为未批准概念'));
  const lz = bible.environmentVisualReview.liangzhu;
  assert.deepEqual([lz.terrainDirectionAccepted, lz.highPrecisionPixelSceneAuthored, lz.runtimeIntegrated], [true, false, false]);
  assert.equal(bible.environmentVisualReview.currentMapSatisfiesGeographyRule, false);
  pass('approval ledger: only the 48 px scale and v8 static frame approved; sentry and Liangzhu are direction-only; four-direction animation not accepted');

  // 3. M2 stays in progress: ten gates implemented with QA evidence (the anchor, start-year and air-route gates moved from
  // decided_runtime_pending after the US runtime migration; route-data after the 2026-10-16 whole-hour rule), two still open;
  // none is "done"; every referenced file exists.
  const m2 = progress.steps.find(s => s.id === 'M2');
  assert.equal(m2.status, 'in_progress');
  for (const phrase of ['NYC', 'Yonkers', 'Washington, D.C.', 'NYC-Chicago', 'Chicago Loop', '2537-05-25', 'technical candidates', 'hidden save aliases', 'M2 stays in progress', '0/2']) {
    assert.ok(m2.blocker && m2.blocker.includes(phrase), 'M2 blocker: ' + phrase);
  }
  assert.ok(!/runtime still|not migrated|尚未迁移/.test(m2.blocker + m2.summary), 'M2 no longer says the runtime is unmigrated');
  const x = progress.m2Expansion;
  // The anchor record now describes the migrated runtime: NYC, as a technical candidate with unaccepted art.
  assert.equal(x.anchor.status, 'implemented_technical_candidate');
  assert.ok(x.anchor.zh.includes('纽约') && x.anchor.zh.includes('市政厅公园') && x.anchor.zh.includes('技术候选') && x.anchor.zh.includes('美术未验收') && x.anchor.en.includes('New York City') && x.anchor.en.includes('art not accepted'));
  assert.ok(x.anchor.note.includes('卡茨基尔山') && x.anchor.note.includes('尚无运行时地点') && x.anchor.note.includes('隐藏的旧档别名') && x.anchor.note.includes('不属于 MVP'));
  const cd = x.creatorDecision;
  assert.deepEqual([cd.scienceHub, cd.undergroundCommunity, cd.firstAirRoute, cd.adventureStart, cd.runtimeImplemented], ['纽约 / New York City', '卡茨基尔山附近 / near the Catskills', '纽约—芝加哥 / NYC-Chicago', '2537-05-25', true], 'progress creator decision recorded and implemented in the runtime');
  assert.ok(cd.runtimeStatus.includes('technical candidate') && cd.runtimeEvidence === usQaNote);
  assert.ok(cd.washingtonDC.includes('Pixelorama') && cd.note === creatorNote);
  assert.deepEqual(x.gates.map(g => g.id), gateOrder);
  const allEvidence = [...x.gates, ...progress.approvalLedger.items].flatMap(g => g.evidence);
  // Active route links are the current US sources; the superseded Shanghai packets survive only as labelled archive entries.
  assert.deepEqual([x.researchPacket, x.airRoutePacket, x.activeTravelData], [usQaNote, usTravelData, usTravelData], 'active route links point at the US sources');
  assert.deepEqual(x.archivedResearchPackets.map(a => [a.path, a.status]), [[packetDoc, 'archived_superseded'], [airPacketDoc, 'archived_superseded']], 'Shanghai packets archived, not active');
  assert.ok(x.archivedResearchPackets.every(a => a.note.includes('归档') && a.note.includes('Archive')));
  for (const file of [...allEvidence, ...x.archivedResearchPackets.map(a => a.path), x.rule, x.researchPacket, x.airRoutePacket, cd.note, cd.runtimeEvidence]) assert.ok(fs.existsSync(path.join(root, file)), 'exists: ' + file);
  const gate = Object.fromEntries(x.gates.map(g => [g.id, g]));
  for (const g of x.gates) assert.ok(g.zh && g.en && g.owner && g.detail, g.id + ' bilingual label, owner and detail');
  for (const id of implementedGates) {
    assert.equal(gate[id].status, 'implemented', id + ' implemented');
    assert.ok(gate[id].evidence.some(file => file.startsWith('docs/qa/')), id + ' cites a QA note');
  }
  for (const [id, status] of Object.entries(openGates)) assert.equal(gate[id].status, status, id + ' stays open as ' + status);
  assert.ok(!x.gates.some(g => g.status === 'done' || g.status === 'decided_runtime_pending'), 'no M2 gate claims final acceptance or still waits for the migration');
  assert.ok(['212', '105', '149', '32', '不代表'].every(t => gate['acceptance-test'].detail.includes(t)), 'test gate states the re-run counts and its limit');
  for (const id of ['anchor', 'start-year']) assert.equal(gate[id].owner, '创作者决定 · 旅行核心实现', id + ' decided by the creator, implemented by the travel core');
  for (const id of migratedGates) assert.ok(gate[id].detail.includes('已决定并已') && gate[id].evidence.includes(usQaNote) && !gate[id].detail.includes('尚未迁移'), id + ' decided and implemented, citing the migration QA note');
  assert.ok(['纽约', '曼哈顿下城市政厅公园', '扬克斯', '华盛顿特区国会大厦废墟', '卡茨基尔山', '尚无运行时地点', '美术未制作'].every(t => gate.anchor.detail.includes(t)), 'anchor gate: NYC set implemented, Catskills place and art still open');
  assert.ok(gate['air-route'].detail.includes('纽约—芝加哥') && gate['air-route'].detail.includes('初步估算') && gate['air-route'].detail.includes('卢普区'));
  assert.ok(gate['route-data'].detail.includes('初步估算') && gate['route-data'].detail.includes('OSRM') && gate['route-data'].detail.includes('无路线'), 'reference figures stay preliminary');
  assert.deepEqual([gate['route-data'].zh, gate['route-data'].en], ['路线旅时（整点规则）', 'Route times (whole-hour rule)'], 'route-data gate is the whole-hour route-times gate');
  assert.deepEqual([gate.calendar.zh, gate.calendar.en], ['日历（整点旅时，只显示日期）', 'Calendar (whole-hour trips, date-only display)'], 'calendar gate label states the date-only display');
  assert.ok(['已实现', '整点', '抵达日期', '不显示机场名、分项或钟点', '不代表地图美术或人工验收'].every(t => gate['route-data'].detail.includes(t)) && gate.calendar.detail.includes('只显示年月日'), 'route-data and calendar details state the current rule and its limit');
  assert.ok(!x.gates.some(g => /门到门|整数分钟|door-to-door|integer-minute/i.test(g.zh + ' ' + g.en)), 'no current gate label keeps the superseded door-to-door or integer-minute wording');
  assert.ok(['m2-v10_20261016-145448-d4c46b62.md', 'date-only-cards_manifest_m2-v11'].every(t => gate['route-data'].evidence.some(file => file.includes(t))), 'route-data cites the whole-hour QA note and the date-only capture manifest');
  assert.ok(gate['map-art'].detail.includes('功能占位') && gate['visual-review'].detail.includes('0/2') && gate['visual-review'].detail.includes('0/12'));
  // Route figures shown in the Bible must equal the active v02 game travel data.
  const travel = readJson(travelDataPath);
  const seg = id => travel.segments.find(s => s.id === id);
  const route = gate['route-data'].detail;
  for (const id of ['seg.car.nyc__yonkers', 'seg.car.nyc__washington-ruins', 'seg.car.yonkers__washington-ruins']) {
    const car = seg(id);
    assert.ok(route.includes(car.roadDistanceKm.toFixed(1) + ' km／' + car.referenceDurationMinutes + ' 分'), 'car figure matches game data: ' + id);
  }
  // 2026-10-16 whole-hour rule: the gates state the charged hours and the internal reference minutes of the game data.
  const hours = s => s.gameplayDurationMinutes / 60;
  for (const [id, h] of [['seg.car.nyc__yonkers', 1], ['seg.car.nyc__washington-ruins', 5], ['seg.car.yonkers__washington-ruins', 5]]) {
    assert.ok(hours(seg(id)) === h && route.includes(h + ' 小时（参考 ' + seg(id).roadDistanceKm.toFixed(1) + ' km'), 'car hours match game data: ' + id);
  }
  const outbound = seg('seg.air.nyc-lga__chicago-ord'), inbound = seg('seg.air.chicago-ord__nyc-lga');
  assert.ok(hours(outbound) === 6 && hours(inbound) === 6 && route.includes('往返各 6 小时（内部参考 ' + outbound.referenceDurationMinutes + '／' + inbound.referenceDurationMinutes + ' 分') &&
    gate['air-route'].detail.includes('往返各按 6 小时结算') && gate['air-route'].detail.includes(outbound.referenceDurationMinutes + '／' + inbound.referenceDurationMinutes + ' 分') && gate['air-route'].detail.includes(outbound.flightDistanceKm + ' km'), 'air figures match game data');
  assert.ok(!/机场名|值机/.test(gate['air-route'].detail.replace('界面不显示机场名或值机等分项', '')), 'air gate names no airport or check-in step except to say the UI hides them');
  assert.ok(travel.segments.every(s => s.gameplayDurationMinutes % 60 === 0 && s.gameplayDurationMinutes >= 60 && !('doorToDoorAllowanceMinutes' in s) && !('flightMinutes' in s) && s.verification.status === 'preliminary-estimate'), 'data: every leg charges whole hours and is a preliminary estimate with no top-level components');
  assert.ok(travel.routes.filter(r => r.status === 'pending').length === 2, 'data: Yonkers/Washington to Chicago stay pending');
  // implemented must stay true of the game data: if the runtime changes, these gates and this check change together.
  assert.deepEqual(travel.locations.map(l => l.id), usPlaces, 'runtime is the US science set');
  assert.ok(travel.locations.every(l => l.regionId === 'science' && ['US', 'CA'].includes(l.countryCode)), 'every active place is a science place in the US or Canada');
  assert.deepEqual(travel.retiredLocations.map(l => l.id), ['earth.cn.shanghai', 'earth.cn.shanghai.songjiang-outskirts', 'earth.cn.liangzhu-ruins'], 'Shanghai set kept only as hidden save aliases');
  const regions = Object.fromEntries(travel.regions.map(r => [r.id, r]));
  assert.deepEqual(travel.regions.filter(r => r.planet === 'earth').map(r => r.id), ['science', 'magic', 'wuxia', 'nature', 'culture'], 'five Earth spheres');
  assert.ok(regions.offworld.planet !== 'earth' && regions.offworld.access === 'portal', 'separate portal-only final planet');
  assert.ok(!regions.fantasy && regions.culture.legacyIds.includes('fantasy') && regions.science.countryCodes.join() === 'US,CA', 'fantasy is only an alias of culture; science is US + Canada');
  assert.equal(travel.calendar.startDate, '2537-05-25');
  assert.ok(gate['start-year'].detail.includes(travel.calendar.startDate + ' ' + travel.calendar.startTime) && gate['start-year'].detail.includes('序章'), 'start-year gate names the implemented start');
  const provisional = readJson(provisionalTravelPath);
  assert.deepEqual(provisional.locations.map(l => l.id), ['earth.cn.shanghai', 'earth.cn.shanghai.songjiang-outskirts', 'earth.cn.liangzhu-ruins'], 'provisional v01 record kept on disk');
  const decisions = Object.fromEntries(progress.decisions.map(d => [d.id, d]));
  for (const id of resolvedDecisionIds) assert.ok(!decisions[id], 'decided item no longer listed as pending: ' + id);
  assert.equal(decisions['prologue-start-date'].kind, 'blocked');
  assert.ok(decisions['prologue-start-date'].detail.includes('2537-05-25') && decisions['prologue-start-date'].detail.includes('未给出'), 'the prologue date stays open');
  assert.ok(decisions['old-save-dates'].kind === 'blocked' && decisions['old-save-dates'].detail.includes('2026') && decisions['old-save-dates'].awaiting === '用户', 'old-save date shift is an open creator decision');
  assert.ok(decisions['skill-tree-redesign'].detail.includes('200 + 510'), '710 skill nodes stay open');
  assert.ok(decisions['companion-sphere-mapping'].detail.includes('奇幻即文化') && !decisions['companion-sphere-mapping'].detail.includes('复核'), 'Culture is the former Fantasy, no review question left');
  assert.ok(decisions['female-south-locomotion'].detail.includes('v3') && decisions['female-south-locomotion'].detail.includes('未通过运行前技术审计'));
  for (const d of progress.decisions) assert.ok(['blocked', 'candidate'].includes(d.kind) && d.zh && d.en && d.awaiting, d.id);
  // Bible: the geography decisions are implemented runtime candidates; skills, AI, reputation and endgame are not.
  const bcd = bible.creatorDecisions;
  assert.equal(bcd.runtimeImplemented, 'partial');
  assert.ok(bcd.status.includes('技术候选') && bcd.status.includes('尚未实现') && bcd.note === creatorNote && bcd.runtimeEvidence === usQaNote);
  assert.deepEqual([bcd.geography.scienceHub, bcd.geography.adventureStart, bcd.geography.undergroundCommunity, bcd.geography.firstAirRoute], ['纽约（New York City）', '2537-05-25', '卡茨基尔山（Catskills）附近', '纽约—芝加哥（NYC–Chicago）']);
  const science = bcd.spheres.find(s => s.id === 'science');
  assert.deepEqual([science.region, science.hubs], ['美国 + 加拿大', ['纽约']], 'science sphere: US + Canada, hub NYC');
  assert.deepEqual(bcd.spheres.map(s => s.id), ['science', 'magic', 'wuxia', 'nature', 'culture'], 'five Earth spheres in the Bible');
  assert.ok(bcd.spheres.find(s => s.id === 'magic').hubs[0].startsWith('马瑙斯'), 'Manaus is 马瑙斯');
  assert.deepEqual(bcd.reputation.dimensions.map(t => t.slice(0, 2)), ['求知', '果敢', '共情', '公正', '守诺'], 'exact reputation names');
  assert.ok(bcd.endgame.repeatableScenes.includes('各 2 个') && bcd.endgame.repeatableScenes.includes('终局星球 2 个') && bcd.endgame.scope.includes('不属于 MVP'), 'endgame 2 per sphere + 2 final planet, full game not MVP');
  assert.ok(['0/52', '0/11', '0/2', '未改变'].every(t => bcd.counters.includes(t)), 'creator decisions leave the counters unchanged');
  const worldBody = bible.chapters[1].body;
  assert.ok(worldBody.includes('没有固定顺序') && !worldBody.includes('待创作者确认') && !worldBody.includes('待复核'), 'mainline order and Culture = former Fantasy are not open questions');
  assert.ok(!/游戏运行时仍使用已被取代/.test(worldBody) && worldBody.includes('技术候选'), 'world chapter describes the migrated runtime');
  assert.ok(!bible.openQuestions.some(q => q.title.includes('地理锚点')), 'stale provisional-anchor question removed');
  const migrationQ = bible.openQuestions.find(q => q.title.includes('运行时地理迁移'));
  assert.ok(migrationQ && migrationQ.title.includes('已实现为技术候选') && migrationQ.title.includes('未验收') && ['纽约', '卡茨基尔山', '纽约—芝加哥', '上海'].every(t => migrationQ.detail.includes(t)), 'bible open question: runtime geography migration implemented as a candidate');
  const dateQ = bible.openQuestions.find(q => q.title.includes('新游戏日期'));
  assert.ok(dateQ && dateQ.title.includes('已实现') && dateQ.detail.includes(travel.calendar.startDate) && dateQ.detail.includes('旧档'), 'bible open question: new-game date implemented, prologue and old-save dates open');
  assert.ok(bible.openQuestions.find(q => q.title.includes('组合技与 AI')).detail.includes('关系阶段名称与阈值'), 'relationship tuning stays open');
  // Washington, D.C. is the Capitol Pixelorama pilot: unapproved walkable v01-v04 and cinematic v01-v02 candidates exist; none is integrated or accepted.
  const dc = bible.environmentVisualReview.washingtonDC;
  assert.ok(dc.role.includes('Pixelorama') && dc.role.includes('试点') && dc.setting.includes('国会大厦') && dc.note === creatorNote);
  assert.deepEqual([dc.sceneBriefAuthored, dc.highPrecisionPixelSceneAuthored, dc.runtimeIntegrated, dc.artAccepted], [false, false, false, false], 'DC pilot: no runtime-ready or accepted scene');
  assert.ok(dc.unapprovedCandidates.status.includes('未批准候选') && dc.unapprovedCandidates.runtimeIntegrated === false && dc.unapprovedCandidates.artAccepted === false && dc.unapprovedCandidates.evidence.every(file => fs.existsSync(path.join(root, file))), 'DC unapproved candidates recorded with evidence');
  assert.ok(!bible.openQuestions.some(q => q.detail.includes('尚未制作')), 'no open question says the Washington scene is not yet made');
  assert.equal(bible.environmentVisualReview.artAccepted, false);
  const geoMap = bible.environmentVisualReview.runtimeGeographyMap;
  assert.deepEqual([geoMap.implemented, geoMap.automatedTestsPass, geoMap.artAccepted, geoMap.humanReviewed], [true, true, false, false]);
  pass(`M2 in progress with ${x.gates.length} gates (${implementedGates.length} implemented with QA evidence incl. ${migratedGates.length} migrated from decided/runtime-pending, ${Object.keys(openGates).length} open, 0 done), ${allEvidence.length} evidence paths exist, US runtime (NYC, Yonkers, Washington, Chicago, 2537-05-25) matches the v02 travel data, five Earth spheres + portal final planet with fantasy only an alias, route figures match (whole hours 1/5/5/6 h from preliminary reference figures, 2 pending), v01 record kept, ${progress.decisions.length} labelled decisions, ${resolvedDecisionIds.length} resolved ones removed`);

  // 4. Served Production view.
  const port = await freePort();
  const base = `http://127.0.0.1:${port}`;
  const child = spawn(process.execPath, [server], {cwd: root, env: {...process.env, WORLDS_BETWEEN_BIBLE_PORT: String(port)}, stdio: 'ignore'});
  try {
    await waitFor(async () => { try { return (await fetch(base + '/health')).ok; } catch (_) { return false; } }, 'server health');
    const html = await renderProduction(base);
    const order = ['id="global-map-travel-rule"', 'id="m2-global-travel-gates"', 'id="approval-ledger"', 'id="pending-decisions"', '<div class="section-label">新版画面验收</div>'].map(s => html.indexOf(s));
    assert.ok(order.every((at, i) => at > 0 && (i === 0 || at > order[i - 1])), 'rule → gates → ledger → decisions → visual acceptance');

    const gates = cardById(html, 'm2-global-travel-gates');
    assert.equal([...gates.matchAll(/<li class="m2-gate" data-gate="/g)].length, 12, 'twelve gate rows');
    const [builtList, openList] = gates.split('<ol class="m2-gates"').slice(1);
    assert.ok(builtList && openList && gates.indexOf('已实现 / Implemented（10）') < gates.indexOf('仍未完成 / Still open（2）'), 'implemented group before open group');
    assert.deepEqual([...builtList.matchAll(/data-gate="([^"]+)"/g)].map(m => m[1]), implementedGates, 'implemented group holds exactly the ten implemented gates');
    assert.ok(!gates.includes('已决定 · 运行时未迁移'), 'no gate still shows the runtime-pending badge');
    assert.ok(!gates.includes('待用户决定 / Awaiting user decision</span>') && !gates.includes('仅研究资料 / Research only'), 'no stale awaiting/research-only badge');
    assert.ok(!/<table|<tr /.test(gates), 'gates are stacked rows, not a wide table');
    assert.ok(gates.includes('10 / 12 已实现 · M2 未完成 / Not complete'), 'gate implementation count and M2 not complete');
    assert.ok(gates.includes('路线旅时（整点规则）') && gates.includes('Route times (whole-hour rule)') && !/门到门路线数值|Door-to-door route figures|仅初步估算/.test(gates), 'route-times gate shown implemented; no door-to-door label or preliminary-estimate badge left');
    assert.ok(!/已完成 · Done|M2 已完成|M2 complete/.test(gates), 'no completion claim');
    for (const label of ['负责 / Owner', '暂无来源 / No source yet', '查看来源 / View source（1）', '查看当前美国路线来源 / View current US route sources', '归档：已取代的上海／良渚路线研究 / Archive: superseded Shanghai-Liangzhu route research', '已实现 · 自动测试通过 / Implemented, tests pass', '未开始 / Not started', '待人工审阅 / Awaiting human review', '不是程序缺陷', x.anchor.zh, x.anchor.en, '纽约—芝加哥', '旧三点 M2_SMOKE_OK 不计入新规则']) {
      assert.ok(gates.includes(label), 'gates card shows: ' + label);
    }
    // Provenance is collapsed: raw docs/ paths appear only inside <details class="sources"> (never open by default) or a title attribute.
    for (const card of [gates, cardById(html, 'global-map-travel-rule')]) {
      const visible = card.replace(/<details class="sources">[\s\S]*?<\/details>/g, '').replace(/title="[^"]*"/g, '');
      assert.ok(!/docs\/|outputs\//.test(visible), 'no raw path outside collapsed sources');
    }
    assert.ok(!/<details class="sources" open/.test(html), 'sources collapsed by default');
    assert.ok(html.includes('查看规则与验收 / View rules &amp; acceptance'), 'rule card link is labelled');
    const ruleCard = cardById(html, 'global-map-travel-rule');
    assert.ok(ruleCard.includes('规则已定 · 地图与旅时核心已实现 · M2 未完成') && !ruleCard.includes('尚未完成本次修改') && ruleCard.includes('初步估算'), 'rule card reflects the implemented runtime and open gates');
    assert.ok(['固定整点旅时', '只看到年月日', '纽约⇄扬克斯 1 小时', '纽约⇄芝加哥 6 小时', '整点旅时已实现'].every(t => ruleCard.includes(t)) && !/路线分钟|旅时参考真实地理距离/.test(ruleCard), 'rule card states fixed whole-hour trips and the date-only calendar');
    assert.ok(['技术候选', '2537-05-25', '纽约—芝加哥', '卡茨基尔山附近', '卢普区', '美国东北部'].every(t => ruleCard.includes(t)) && !/尚未迁移|长江三角洲|没有航空路线/.test(ruleCard), 'rule card: US runtime implemented as a technical candidate');
    const ledger = cardById(html, 'approval-ledger');
    assert.equal(ledger.split('<details class="sources">').length - 1, progress.approvalLedger.items.length, 'one collapsed source list per ledger item');
    assert.ok(ledger.includes('查看来源 / View source（2）') && ledger.includes('QA 记录 / QA note') && ledger.includes('产出文件 / Output · 图片 / Image'), 'ledger source labels');
    for (const label of ['探索精灵 / Runtime sprites 0 / 52', '科技区场景画质 / Science scene visuals 0 / 12', '人工计时试玩 / Human playtests 0 / 2', '角色 51 位 / 52 个视觉版本', '验收数未增加 · No counter incremented', '方向已接受 / Direction accepted', '未接受 / Not accepted']) {
      assert.ok(ledger.includes(label), 'ledger shows: ' + label);
    }
    assert.equal(ledger.split('已批准（限定范围）/ Approved, scoped').length - 1, 2, 'exactly two scoped approval badges');
    const decisionsCard = cardById(html, 'pending-decisions');
    assert.equal([...decisionsCard.matchAll(/<li data-decision="/g)].length, progress.decisions.length);
    assert.ok(decisionsCard.includes('受阻 · 待决定 / Blocked') && decisionsCard.includes('候选 · 待审 / Candidate'));
    for (const card of [gates, ledger, decisionsCard]) assert.ok(!/<button|<input|<textarea|<select|data-check|asset-check|checkbox/i.test(card), 'no acceptance controls');
    assert.ok(html.includes('场景画质 0 / 12') && html.includes('探索精灵 0 / 52'), 'inventory summary unchanged');
    // Existing approved v8 card is untouched.
    assert.ok(cardById(html, 'idle-selout-v8').includes('用户已批准 · 仅南向待机静态基准帧'));

    // Design-doc links are served byte-identical; nothing else under /source is opened up.
    for (const [href, file] of [['/source/earth-rules', rulesDoc], ['/source/shanghai-liangzhu', packetDoc]]) {
      assert.ok(html.includes(`href="${href}"`), 'linked: ' + href);
      const response = await fetch(base + href);
      assert.equal(response.status, 200, href);
      assert.ok(response.headers.get('content-type').startsWith('text/markdown'), href + ' type');
      assert.ok(Buffer.from(await response.arrayBuffer()).equals(fs.readFileSync(path.join(root, file))), href + ' bytes');
    }
    for (const probe of ['/source/..%2Fdocs%2Fprogress.md', '/source/design', '/source/earth-rules/', '/docs/progress.md']) assert.equal((await fetch(base + probe)).status, 404, 'rejected: ' + probe);
    // Every evidence link resolves through /evidence to the exact cited file; uncited, traversal and non-allowlisted paths are 404.
    const links = [...html.matchAll(/href="(\/evidence\?path=[^"]+)"/g)].map(m => m[1]);
    const cited = [...new Set(allEvidence)];
    assert.equal(new Set(links).size, cited.length, 'one link target per cited evidence file');
    for (const href of new Set(links)) {
      const file = decodeURIComponent(href.slice('/evidence?path='.length));
      const response = await fetch(base + href);
      assert.equal(response.status, 200, href);
      assert.ok(Buffer.from(await response.arrayBuffer()).equals(fs.readFileSync(path.join(root, file))), file + ' bytes');
    }
    const evidenceProbes = ['docs/progress.md', 'docs/qa/../progress.md', '../outputs/x.md', 'tools/rpg-2-star-ocean-the-second_game-bible_server_v05_20261013-222437-3d5b8a9f.js', 'game/scripts/app_state.gd', '/etc/passwd', 'C:/Windows/win.ini', ''];
    for (const probe of evidenceProbes) assert.equal((await fetch(base + '/evidence?path=' + encodeURIComponent(probe))).status, 404, 'evidence rejected: ' + probe);
    pass(`Production view: gates, ledger and decisions cards in order after the rule card, bilingual labels, 10/12 gates implemented in their own group and M2 not complete, no runtime-pending badge left, counters 0/52 0/11 0/2 and 51/52, two scoped approvals, no controls; raw paths only in collapsed sources; ${cited.length} evidence files served byte-identical, ${evidenceProbes.length} evidence probes 404; two design docs served byte-identical, 4 probes 404`);

    // 5. Hostile values are escaped; missing sections are omitted without breaking the view.
    const hostile = JSON.parse(JSON.stringify(progress));
    hostile.updatedAt = 'hostile';
    hostile.m2Expansion.gates[0].zh = '<img src=x onerror=alert(1)>';
    hostile.m2Expansion.gates[1].status = '<b>odd</b>';
    hostile.approvalLedger.items[0].scope = '"><script>bad()</script>';
    hostile.decisions[0].detail = '<iframe>';
    hostile.m2Expansion.gates[0].evidence = ['javascript:alert(1)', '../../secret.md', 42, null, 'docs/qa/"><svg onload=x>.md'];
    hostile.approvalLedger.items[1].evidence = undefined;
    const hostileHtml = await renderProduction(base, hostile);
    assert.ok(!/<img src=x|<script>bad|<iframe>|<b>odd<\/b>/.test(hostileHtml), 'hostile markup not rendered');
    const hostileGate = cardById(hostileHtml, 'm2-global-travel-gates');
    assert.ok(!/javascript:|secret\.md|<svg/.test(hostileGate), 'unsafe evidence never linked or echoed');
    assert.equal(hostileGate.split('来源路径无效或缺失 / Source path unavailable').length - 1, 5, 'each unsafe/missing evidence entry shows the fallback');
    assert.ok(cardById(hostileHtml, 'approval-ledger').includes('暂无来源 / No source yet'), 'missing evidence list falls back');
    assert.ok(hostileHtml.includes('&lt;img src=x onerror=alert(1)&gt;') && hostileHtml.includes('&lt;b&gt;odd&lt;/b&gt;'), 'escaped text and unknown status shown verbatim');
    const bare = JSON.parse(JSON.stringify(progress));
    delete bare.m2Expansion; delete bare.approvalLedger; delete bare.decisions;
    const bareHtml = await renderProduction(base, bare);
    assert.ok(!bareHtml.includes('id="m2-global-travel-gates"') && !bareHtml.includes('id="approval-ledger"') && !bareHtml.includes('id="pending-decisions"'));
    assert.ok(bareHtml.includes('id="global-map-travel-rule"') && bareHtml.includes('分步实施'), 'rest of the view still renders');
    pass('hostile gate/ledger/decision fields and unsafe evidence paths render escaped or as a safe fallback; a state without the new fields omits the three cards and still renders');
  } finally {
    child.kill();
  }
  console.log('RESULT PASS (5 checks)');
})().catch(error => { console.error('FAIL', error); process.exitCode = 1; });
