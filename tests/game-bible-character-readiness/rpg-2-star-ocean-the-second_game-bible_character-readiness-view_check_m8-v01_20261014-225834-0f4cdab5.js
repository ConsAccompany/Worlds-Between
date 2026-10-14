// Focused check for the Game Bible character sprite readiness view.
// Starts the real v05 panel server on a spare local port (the user's 18727 instance is left alone), then runs the
// served bible.js in a VM with a minimal DOM stub. Read-only: no project file is written.
// Run from the repository root: node tests/game-bible-character-readiness/<this file>
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const net = require('node:net');
const path = require('node:path');
const vm = require('node:vm');
const {spawn} = require('node:child_process');

const root = path.resolve(__dirname, '..', '..');
const server = path.join(root, 'tools', 'rpg-2-star-ocean-the-second_game-bible_server_v05_20261013-222437-3d5b8a9f.js');
const checklistPath = path.join(root, 'game', 'data', 'character-visuals', 'rpg-2-star-ocean-the-second_character-sprite-readiness-checklist_m8-v01_20261014-184413-53da3710.json');
const inventoryPath = path.join(root, 'outputs', 'rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json');
const progressPath = path.join(root, 'outputs', 'rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json');
const sha256 = data => crypto.createHash('sha256').update(data).digest('hex');
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const results = [];
const pass = label => { results.push(label); console.log('PASS ' + label); };

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

// Runs the served app against a DOM stub. `override` may replace any fetched route with a canned response.
async function renderProduction(base, override = {}) {
  const element = () => ({innerHTML: '', textContent: '', value: '', dataset: {}, addEventListener() {}, setAttribute() {}, querySelector: () => element(), querySelectorAll: () => []});
  const content = {...element(), querySelector: () => element()};
  const elements = {content, search: element(), edition: element(), pitch: element(), 'footer-status': element()};
  const nav = ['home', 'world', 'rules', 'characters', 'production', 'assets'].map(view => {
    const button = {...element(), dataset: {view}, handlers: {}};
    button.addEventListener = (type, handler) => { button.handlers[type] = handler; };
    return button;
  });
  const fetchStub = async (url, options) => {
    if (Object.hasOwn(override, url)) return override[url]();
    return fetch(base + url, options);
  };
  const context = vm.createContext({
    document: {getElementById: id => elements[id], querySelectorAll: () => nav, addEventListener() {}, hidden: true, createElement: () => element()},
    fetch: fetchStub, setInterval() {}, localStorage: {getItem: () => '', setItem() {}}, console,
  });
  vm.runInContext(await (await fetch(base + '/bible.js')).text(), context, {filename: 'bible.js'});
  await waitFor(() => elements.edition.textContent !== '', 'initial bible load');
  nav.find(button => button.dataset.view === 'production').handlers.click();
  await waitFor(() => content.innerHTML.includes('id="character-readiness"') && !content.innerHTML.includes('正在读取角色就绪清单'), 'readiness section');
  return content.innerHTML;
}
const readinessSlice = html => {
  const start = html.indexOf('<div class="section-label">角色精灵就绪清单');
  const end = html.indexOf('</section>', html.indexOf('id="character-readiness"')) + '</section>'.length;
  assert.ok(start > 0 && end > start, 'readiness section boundaries');
  return {section: html.slice(start, end), rest: html.slice(0, start) + html.slice(end)};
};
const jsonResponse = body => () => new Response(typeof body === 'string' ? body : JSON.stringify(body), {status: 200, headers: {'content-type': 'application/json'}});

(async () => {
  const port = await freePort();
  const base = `http://127.0.0.1:${port}`;
  const child = spawn(process.execPath, [server], {cwd: root, env: {...process.env, WORLDS_BETWEEN_BIBLE_PORT: String(port)}, stdio: 'ignore'});
  try {
    await waitFor(async () => { try { return (await fetch(base + '/health')).ok; } catch (_) { return false; } }, 'server health');

    // 1. Served checklist is the unmodified file with safe headers.
    const fileBytes = fs.readFileSync(checklistPath);
    const served = await fetch(base + '/character-readiness');
    assert.equal(served.status, 200);
    assert.match(served.headers.get('content-type'), /^application\/json/);
    assert.equal(served.headers.get('x-content-type-options'), 'nosniff');
    assert.equal(served.headers.get('cache-control'), 'no-store');
    const servedBytes = Buffer.from(await served.arrayBuffer());
    assert.equal(sha256(servedBytes), sha256(fileBytes));
    pass(`/character-readiness serves the checklist byte-for-byte (sha256 ${sha256(fileBytes).slice(0, 16)}…) with nosniff/no-store`);

    // 2. Checklist facts the view depends on.
    const checklist = JSON.parse(fileBytes.toString('utf8'));
    assert.equal(checklist.kind, 'character_sprite_production_readiness_checklist');
    assert.equal(checklist.variants.length, 52);
    assert.equal(new Set(checklist.variants.map(v => v.visual_id)).size, 52);
    assert.equal(checklist.hair_review.candidate_confusion_groups.length, 13);
    assert.ok(checklist.hair_review.candidate_confusion_groups.every(g => g.decision === 'pending_human_review'));
    assert.ok(checklist.variants.every(v => v.gates.art_acceptance.status === 'pending'));
    assert.equal(checklist.summary.art_accepted, 0);
    pass('checklist has 52 unique variants, 13 pending hair review groups, 0 art accepted');

    // 3. Routing stays closed: no traversal into game/data through other routes.
    for (const probe of ['/character-readiness/x', '/assets/..%2F..%2Fgame%2Fdata%2Fcharacter-visuals%2Fx.png', '/game/data/character-visuals/' + path.basename(checklistPath)]) {
      assert.equal((await fetch(base + probe)).status, 404, probe);
    }
    assert.equal((await fetch(base + '/character-readiness', {method: 'POST'})).status, 405);
    pass('traversal and non-GET probes are rejected (404/405)');

    // 4. Real data renders all variants and groups; the rest of the Production page is unchanged.
    const html = await renderProduction(base);
    const {section, rest} = readinessSlice(html);
    assert.equal((section.match(/<details class="readiness-row"/g) || []).length, 52);
    assert.equal((section.match(/<span class="kicker">复核提示<\/span>/g) || []).length, 13);
    assert.equal((section.match(/立绘已批准/g) || []).length, checklist.summary.source_portraits.approved);
    assert.equal((section.match(/美术验收 待定/g) || []).length, 52);
    assert.ok(!/美术验收 (已|accepted)/.test(section), 'no art acceptance is shown as granted');
    for (const href of section.match(/href="[^"]*"/g) || []) assert.match(href, /^href="\/assets\/[A-Za-z0-9._%-]+\.png"$/);
    for (const v of checklist.variants) assert.ok(section.includes(`<code>${v.visual_id}</code>`), v.visual_id);
    pass('Production view lists 52 variants, 13 review-prompt groups, 9 approved source portraits, 52 pending art gates');

    const unavailable = await renderProduction(base, {'/character-readiness': () => new Response('gone', {status: 503})});
    const fallback = readinessSlice(unavailable);
    assert.ok(fallback.section.includes('角色就绪清单暂时无法读取'));
    assert.equal(rest, fallback.rest, 'Production page outside the readiness section is identical');
    const inventory = JSON.parse(fs.readFileSync(inventoryPath, 'utf8'));
    const items = inventory.categories.flatMap(c => c.subcategories.flatMap(s => s.items));
    const tally = prefix => { const list = items.filter(i => i.id.startsWith(prefix)); return `${list.filter(i => i.checked).length} / ${list.length}`; };
    const progress = JSON.parse(fs.readFileSync(progressPath, 'utf8'));
    const done = progress.steps.filter(s => s.status === 'done').length;
    assert.ok(rest.includes(`来源设定图 ${tally('portrait.')} 已验收 · 游戏内展示图 ${tally('display.')} · 探索精灵 ${tally('runtime-sprite.')} · 场景画质 ${tally('visual-scene.')}`));
    assert.ok(rest.includes(`${done} / ${progress.steps.length} 阶段`));
    pass(`existing counters unchanged (portraits ${tally('portrait.')}, sprites ${tally('runtime-sprite.')}, scenes ${tally('visual-scene.')}, stages ${done}/${progress.steps.length}); failure shows a fallback only`);

    // 5. HTML injection: hostile values are escaped and unsafe links are dropped; unknown status is not translated to approval.
    const hostile = JSON.parse(fileBytes.toString('utf8'));
    const v0 = hostile.variants[0];
    v0.display_name_zh = '<img src=x onerror=alert(1)>';
    v0.visual_id = 'x" onmouseover="alert(1)';
    v0.identity_and_hair_anchor = '"><script>alert(1)</script>';
    v0.gates.source_art.portrait.path = 'javascript:alert(1)';
    v0.gates.art_acceptance.status = 'accepted';
    hostile.variants[1].gates.source_art.portrait.path = 'outputs/../../game/x.png';
    hostile.hair_review.candidate_confusion_groups[0].concern = '<b onclick="alert(1)">x</b>';
    hostile.hair_review.candidate_confusion_groups[0].members[0].anchor = '<iframe src="//evil">';
    const injected = readinessSlice(await renderProduction(base, {'/character-readiness': jsonResponse(hostile)})).section;
    for (const bad of ['<img src=x', '<script>', 'onmouseover="alert', '<b onclick', '<iframe', 'href="javascript:', 'href="/assets/..']) assert.ok(!injected.includes(bad), bad);
    assert.ok(injected.includes('&lt;img src=x onerror=alert(1)&gt;'));
    assert.ok(injected.includes('&lt;script&gt;'));
    for (const href of injected.match(/href="[^"]*"/g) || []) assert.match(href, /^href="\/assets\/[A-Za-z0-9._%-]+\.png"$/);
    assert.ok(injected.includes('美术验收 accepted') && !injected.includes('美术验收 已'));
    pass('hostile names, ids, anchors, concerns and portrait paths render escaped; unsafe hrefs omitted; unknown status shown verbatim');

    const wrongKind = readinessSlice(await renderProduction(base, {'/character-readiness': jsonResponse({...checklist, kind: 'other'})})).section;
    assert.ok(wrongKind.includes('角色就绪清单暂时无法读取') && !wrongKind.includes('readiness-row'));
    pass('a checklist with an unexpected kind is rejected');

    console.log(`RESULT PASS (${results.length} checks)`);
  } finally {
    child.kill();
  }
})().catch(error => { console.error('RESULT FAIL'); console.error(error); process.exitCode = 1; });
