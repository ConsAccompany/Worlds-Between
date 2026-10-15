// Focused check for the Game Bible M2 global-travel gates, the scoped approval ledger and the candidate/blocked decision list.
// Data audit first (counters, scopes, evidence paths, implemented vs open M2 gates, route figures cross-checked read-only against the
// game travel data), then the real v05 panel server on a
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
const travelDataPath = path.join(root, 'game', 'data', 'world-travel', 'rpg-2-star-ocean-the-second_global-earth-travel_locations-routes_m2-provisional-v01_20261015-024215-b876e53d.json');
const implementedGates = ['map-ui', 'place-registry', 'route-preview', 'calendar', 'save-migration', 'acceptance-test'];
const openGates = {anchor: 'awaiting_decision', 'start-year': 'awaiting_decision', 'route-data': 'estimate_only', 'air-route': 'research_only', 'map-art': 'not_started', 'visual-review': 'human_pending'};
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
  assert.deepEqual([c.runtimeSpritesAccepted, c.runtimeSpritesTarget, c.sceneVisualsAccepted, c.sceneVisualsTarget, c.humanPlaytests, c.humanPlaytestsTarget], [0, 52, 0, 11, 0, 2]);
  assert.equal(checklist.scope.character_identities, c.identities);
  assert.equal(checklist.variants.length, c.visualVariants);
  assert.deepEqual([c.identities, c.visualVariants], [51, 52]);
  assert.equal(bible.environmentVisualReview.sceneQualityAccepted, 0);
  assert.equal(bible.environmentVisualReview.sceneQualityTarget, 11);
  pass('counters: sprites 0/52 and scenes 0/11 match the inventory; 51 identities / 52 variants match the checklist; human playtests 0/2');

  // 2. Approval scopes exactly as given: two scoped approvals, two direction acceptances, the animated variant not accepted.
  const byId = Object.fromEntries(progress.approvalLedger.items.map(i => [i.id, i]));
  assert.deepEqual(progress.approvalLedger.items.filter(i => i.status === 'approved').map(i => i.id).sort(), ['display-scale-48', 'female-v8-south-idle-static']);
  assert.ok(byId['female-v8-south-idle-static'].scope.includes('仅一张南向静态基准帧'));
  assert.equal(byId['female-four-direction-animated'].status, 'not_accepted');
  assert.ok(byId['female-four-direction-animated'].scope.includes('v3 跑步构建脚本未通过运行前技术审计') && byId['female-four-direction-animated'].evidence.includes(runV3Audit), 'run v3 failed its pre-run audit; animation still not accepted');
  assert.equal(byId['sentry-direction'].status, 'direction_accepted');
  assert.ok(byId['sentry-direction'].scope.includes('动画 v2 待审阅') && byId['sentry-direction'].scope.includes('美术验收 0'));
  assert.equal(byId['liangzhu-terrain-direction'].status, 'direction_accepted');
  assert.ok(byId['liangzhu-terrain-direction'].scope.includes('高精度像素场景未制作') && byId['liangzhu-terrain-direction'].scope.includes('v03／v04 为未批准概念'));
  const lz = bible.environmentVisualReview.liangzhu;
  assert.deepEqual([lz.terrainDirectionAccepted, lz.highPrecisionPixelSceneAuthored, lz.runtimeIntegrated], [true, false, false]);
  assert.equal(bible.environmentVisualReview.currentMapSatisfiesGeographyRule, false);
  pass('approval ledger: only the 48 px scale and v8 static frame approved; sentry and Liangzhu are direction-only; four-direction animation not accepted');

  // 3. M2 stays in progress: six gates implemented with evidence, six still open; none is "done"; every referenced file exists.
  const m2 = progress.steps.find(s => s.id === 'M2');
  assert.equal(m2.status, 'in_progress');
  assert.ok(m2.blocker && m2.blocker.includes('Shanghai is provisional') && m2.blocker.includes('start year'));
  const x = progress.m2Expansion;
  assert.equal(x.anchor.status, 'provisional');
  assert.ok(x.anchor.zh.includes('上海') && x.anchor.note.includes('松江是上海市的一个区，不是独立城市'));
  assert.deepEqual(x.gates.map(g => g.id), [...implementedGates, ...Object.keys(openGates)]);
  const allEvidence = [...x.gates, ...progress.approvalLedger.items].flatMap(g => g.evidence);
  for (const file of [...allEvidence, x.rule, x.researchPacket, x.airRoutePacket]) assert.ok(fs.existsSync(path.join(root, file)), 'exists: ' + file);
  const gate = Object.fromEntries(x.gates.map(g => [g.id, g]));
  for (const g of x.gates) assert.ok(g.zh && g.en && g.owner && g.detail, g.id + ' bilingual label, owner and detail');
  for (const id of implementedGates) {
    assert.equal(gate[id].status, 'implemented', id + ' implemented');
    assert.ok(gate[id].evidence.some(file => file.startsWith('docs/qa/')), id + ' cites a QA note');
  }
  for (const [id, status] of Object.entries(openGates)) assert.equal(gate[id].status, status, id + ' stays open as ' + status);
  assert.ok(!x.gates.some(g => g.status === 'done'), 'no M2 gate claims final acceptance');
  assert.ok(gate['acceptance-test'].detail.includes('201') && gate['acceptance-test'].detail.includes('103') && gate['acceptance-test'].detail.includes('不代表'), 'test gate states counts and its limit');
  for (const id of ['anchor', 'start-year']) assert.ok(gate[id].owner === '用户决定', id + ' owned by the user');
  assert.ok(gate.anchor.detail.includes('不是程序缺陷'), 'user decision is not framed as a defect');
  assert.ok(gate['air-route'].evidence.includes(airPacketDoc) && gate['air-route'].detail.includes('都未选定') && gate['air-route'].detail.includes('没有新增可玩城市'));
  assert.ok(gate['map-art'].detail.includes('功能占位') && gate['visual-review'].detail.includes('0/2') && gate['visual-review'].detail.includes('0/11'));
  // Route figures shown in the Bible must equal the game travel data, which still has no air segment and no door-to-door allowance.
  const travel = readJson(travelDataPath);
  const seg = id => travel.segments.find(s => s.id === id);
  const sj = seg('seg.car.shanghai__songjiang-outskirts'), lzSeg = seg('seg.car.shanghai__liangzhu-ruins');
  const route = gate['route-data'].detail;
  assert.ok(route.includes(sj.roadDistanceKm + ' km／' + sj.referenceDurationMinutes + ' 分') && route.includes(lzSeg.roadDistanceKm + ' km／' + lzSeg.referenceDurationMinutes / 60 + ' 小时'), 'figures match game data');
  assert.ok(route.includes('经上海 ' + (sj.referenceDurationMinutes + lzSeg.referenceDurationMinutes) + ' 分') && route.includes('非门到门') && route.includes('松江→良渚未核验'));
  assert.ok(travel.segments.every(s => s.doorToDoorAllowanceMinutes === 0 && s.verification.status === 'preliminary-estimate' && s.mode === 'car'), 'data: car-only preliminary estimates, door-to-door 0');
  assert.ok(travel.pendingRouteRequests.some(r => r.mode === 'air' && r.status === 'pending-place-pair'), 'data: air route still pending');
  assert.deepEqual(travel.locations.map(l => l.id), ['earth.cn.shanghai', 'earth.cn.shanghai.songjiang-outskirts', 'earth.cn.liangzhu-ruins'], 'no new playable place');
  assert.equal(travel.calendar.status, 'engineering-placeholder');
  assert.ok(gate['start-year'].detail.includes(travel.calendar.startDate + ' ' + travel.calendar.startTime), 'start-year gate names the placeholder');
  const decisions = Object.fromEntries(progress.decisions.map(d => [d.id, d]));
  assert.equal(decisions['first-city'].kind, 'blocked');
  assert.equal(decisions['world-start-year'].kind, 'blocked');
  assert.equal(decisions['air-route-pair'].kind, 'candidate');
  assert.ok(decisions['air-route-pair'].detail.includes('未选定') && decisions['air-route-pair'].detail.includes('没有新增可玩城市'));
  assert.ok(decisions['female-south-locomotion'].detail.includes('v3') && decisions['female-south-locomotion'].detail.includes('未通过运行前技术审计'));
  assert.ok(decisions['songjiang-label'].detail.includes('松江是上海的区'));
  for (const d of progress.decisions) assert.ok(['blocked', 'candidate'].includes(d.kind) && d.zh && d.en && d.awaiting, d.id);
  const anchorQ = bible.openQuestions.find(q => q.title.includes('地理锚点'));
  assert.ok(anchorQ && anchorQ.detail.includes('暂定') && anchorQ.detail.includes('不是另一座城市') && anchorQ.detail.includes('均未选定'), 'bible open question records the provisional anchor');
  assert.ok(bible.openQuestions.some(q => q.title.includes('开始年份')), 'bible open question for the start year');
  const geoMap = bible.environmentVisualReview.runtimeGeographyMap;
  assert.deepEqual([geoMap.implemented, geoMap.automatedTestsPass, geoMap.artAccepted, geoMap.humanReviewed], [true, true, false, false]);
  pass(`M2 in progress with ${x.gates.length} gates (${implementedGates.length} implemented with QA evidence, ${Object.keys(openGates).length} open, 0 done), ${allEvidence.length} evidence paths exist, route figures match game data (car only, door-to-door 0, air pending, 3 places), ${progress.decisions.length} labelled decisions`);

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
    assert.ok(builtList && openList && gates.indexOf('已实现 / Implemented（6）') < gates.indexOf('仍未完成 / Still open（6）'), 'implemented group before open group');
    assert.deepEqual([...builtList.matchAll(/data-gate="([^"]+)"/g)].map(m => m[1]), implementedGates, 'implemented group holds exactly the six implemented gates');
    assert.equal(gates.split('<span class="badge accent">待用户决定 / Awaiting user decision</span>').length - 1, 2, 'user decisions use the neutral badge');
    assert.ok(!/<table|<tr /.test(gates), 'gates are stacked rows, not a wide table');
    assert.ok(gates.includes('6 / 12 已实现 · M2 未完成 / Not complete'), 'gate implementation count and M2 not complete');
    assert.ok(!/已完成 · Done|M2 已完成|M2 complete/.test(gates), 'no completion claim');
    for (const label of ['负责 / Owner', '暂无来源 / No source yet', '查看来源 / View source（1）', '查看路线研究 / View route research', '已实现 · 自动测试通过 / Implemented, tests pass', '仅初步估算 / Preliminary estimate', '仅研究资料 / Research only', '未开始 / Not started', '待人工审阅 / Awaiting human review', '不是程序缺陷', '上海（暂定，待用户决定）', 'Shanghai (provisional, pending user decision)', '旧三点 M2_SMOKE_OK 不计入新规则']) {
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
    assert.ok(ruleCard.includes('规则已定 · 地图与旅时核心已实现 · M2 未完成') && !ruleCard.includes('尚未完成本次修改') && ruleCard.includes('没有航空路线'), 'rule card reflects the implemented runtime and open gates');
    const ledger = cardById(html, 'approval-ledger');
    assert.equal(ledger.split('<details class="sources">').length - 1, progress.approvalLedger.items.length, 'one collapsed source list per ledger item');
    assert.ok(ledger.includes('查看来源 / View source（2）') && ledger.includes('QA 记录 / QA note') && ledger.includes('产出文件 / Output · 图片 / Image'), 'ledger source labels');
    for (const label of ['探索精灵 / Runtime sprites 0 / 52', '科技区场景画质 / Science scene visuals 0 / 11', '人工计时试玩 / Human playtests 0 / 2', '角色 51 位 / 52 个视觉版本', '验收数未增加 · No counter incremented', '方向已接受 / Direction accepted', '未接受 / Not accepted']) {
      assert.ok(ledger.includes(label), 'ledger shows: ' + label);
    }
    assert.equal(ledger.split('已批准（限定范围）/ Approved, scoped').length - 1, 2, 'exactly two scoped approval badges');
    const decisionsCard = cardById(html, 'pending-decisions');
    assert.equal([...decisionsCard.matchAll(/<li data-decision="/g)].length, progress.decisions.length);
    assert.ok(decisionsCard.includes('受阻 · 待决定 / Blocked') && decisionsCard.includes('候选 · 待审 / Candidate'));
    for (const card of [gates, ledger, decisionsCard]) assert.ok(!/<button|<input|<textarea|<select|data-check|asset-check|checkbox/i.test(card), 'no acceptance controls');
    assert.ok(html.includes('场景画质 0 / 11') && html.includes('探索精灵 0 / 52'), 'inventory summary unchanged');
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
    pass(`Production view: gates, ledger and decisions cards in order after the rule card, bilingual labels, 6/12 gates implemented in their own group and M2 not complete, user decisions neutral, counters 0/52 0/11 0/2 and 51/52, two scoped approvals, no controls; raw paths only in collapsed sources; ${cited.length} evidence files served byte-identical, ${evidenceProbes.length} evidence probes 404; two design docs served byte-identical, 4 probes 404`);

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
