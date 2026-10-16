// Focused check for the cloud Site Production tab preview figures.
// Runs each Game Bible client (the repo app JS at HEAD and in the working tree, and the private Site's own public/bible.js
// before and after the preview patch) in a VM with a minimal DOM stub, feeds it this checkout's Game Bible state,
// inventory and progress JSON, opens Production, and reads every `.visual-sample` figure (template + appended).
// Expected: the unpatched Site client shows only the city sample (reproduces the live DOM: 1 figure); the patched Site
// client shows the city sample plus all characterVisualReview.previews, each image on raw.githubusercontent.com pinned to
// the state's commit (never the Site's missing /assets/ route), with a status badge read from staticBaselinesAndPilots:
// battle v08 and Liang Xu south v01 say UNAPPROVED · NONRUNTIME, the other previews say "not accepted", none says approved.
// If the Site file is already patched, the pre-patch revision is taken from the Site's git history and the working-tree
// files must equal the helper's output byte for byte. Read-only: nothing is written to disk.
// Site source: argv[2], else WB_SITE_SOURCE, else the 2026-10-15 audit checkout in %LOCALAPPDATA%\Temp. If absent, the
// Site cases are reported as SKIP and only the repo client runs.
// Run from the repository root: node tests/game-bible-site-preview-figures/<this file> [site-source-dir]
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {execFileSync} = require('node:child_process');

const root = path.resolve(__dirname, '..', '..');
const outputs = path.join(root, 'outputs');
const appRel = 'outputs/rpg-2-star-ocean-the-second_game-bible_app_v01_20261013-195526-90e7bc24.js';
const bible = JSON.parse(fs.readFileSync(path.join(outputs, 'rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json'), 'utf8'));
const inventory = JSON.parse(fs.readFileSync(path.join(outputs, 'rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json'), 'utf8'));
const progress = JSON.parse(fs.readFileSync(path.join(outputs, 'rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json'), 'utf8'));
const {patchSiteBibleJs, patchSiteBibleCss, MARKER, CSS_MARKER} = require(path.join(root, 'tools', 'rpg-2-star-ocean-the-second_game-bible-site_production-preview-figures-patch_v01_20261016-113125-8c141468.js'));
const siteDir = process.argv[2] || process.env.WB_SITE_SOURCE ||
  path.join(process.env.LOCALAPPDATA || '', 'Temp', 'worlds-between-tracker-source-audit-20261015-2315');
const git = (cwd, ...args) => execFileSync('git', args, {cwd, encoding: 'utf8', maxBuffer: 1 << 26});
const SHA = git(root, 'rev-parse', 'HEAD').trim();
const RAW_MAIN = 'https://raw.githubusercontent.com/ConsAccompany/Worlds-Between/main/outputs/';
const rawAt = sha => `https://raw.githubusercontent.com/ConsAccompany/Worlds-Between/${sha}/outputs/`;
const nameOf = file => file.replace(/^\/assets\//, '');

const previews = bible.characterVisualReview.previews;
const pilots = bible.characterVisualReview.staticBaselinesAndPilots;
const city = inventory.categories.flatMap(c => c.subcategories.flatMap(s => s.items)).find(i => i.id === 'art.scifi-city-sample');
const v08 = previews.find(p => p.file.includes('sideview-idle-right-static-native0p65_party-capture-ruins_unapproved-v08'));
const liang = previews.find(p => p.file.includes('liang-xu-south-idle-static-pilot-h48_unapproved-v01'));
assert.equal(previews.length, 9, 'state carries 9 previews');
assert.ok(pilots?.femaleBattleSideviewV08 && pilots?.liangXuSouthIdleV01, 'state carries staticBaselinesAndPilots');
for (const key of ['femaleBattleSideviewV08', 'liangXuSouthIdleV01']) {
  assert.equal(pilots[key].creatorApproved, false, key + ' is unapproved in state');
  assert.equal(pilots[key].runtimeIntegrated, false, key + ' is nonruntime in state');
}
assert.notEqual(bible.characterVisualReview.artAccepted, true, 'state does not mark character art accepted');
assert.ok(city?.file && v08 && liang, 'city sample, battle v08 and Liang v01 previews present');
for (const p of [v08, liang]) assert.match(p.caption, /未批准/, p.label + ' caption keeps UNAPPROVED');
for (const p of previews) {
  assert.match(p.file, /^\/assets\/[A-Za-z0-9._-]+\.png$/, 'preview is a flat outputs PNG: ' + p.file);
  assert.doesNotThrow(() => git(root, 'cat-file', '-e', 'HEAD:outputs/' + nameOf(p.file)), 'preview PNG committed at HEAD: ' + p.file);
}

function element(tag = 'div') {
  const el = {tag, className: '', textContent: '', value: '', href: '', src: '', alt: '', dataset: {}, children: [], parentElement: null,
    set innerHTML(v) { this._html = String(v); this.children = []; }, get innerHTML() { return this._html || ''; },
    addEventListener() {}, setAttribute() {}, focus() {}, scrollTo() {}, querySelectorAll: () => [],
    querySelector: () => element(), append(...nodes) { for (const n of nodes) { n.parentElement = this; this.children.push(n); } }};
  return el;
}
// The content pane: a string template plus appended DOM nodes. Only the selectors the repo app's preview loop uses are modeled.
function contentPane() {
  const pane = element('main');
  const card = element('section');
  // Replacing innerHTML discards the old card in a real DOM, so a re-render must not keep previously appended figures.
  Object.defineProperty(pane, 'innerHTML', {get() { return this._html || ''; }, set(v) { this._html = String(v); this.children = []; card.children = []; }});
  pane.querySelector = sel => {
    const html = pane.innerHTML;
    if (sel === '.visual-sample:not(.idle-refine)' || sel === '.visual-sample:not(.idle-refine) figcaption') {
      if (!/<figure class="visual-sample[" ]/.test(html)) return null;
      const m = html.match(/<figure class="visual-sample( [^"]*)?"/);
      if (m[1] && m[1].includes('idle-refine')) return null;
      return sel.endsWith('figcaption') ? element('figcaption') : Object.assign(element('figure'), {parentElement: card});
    }
    return element();
  };
  return {pane, card};
}
const unescape = s => s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&');
const text = html => unescape(html.replace(/<[^>]*>/g, ''));
// Every figure in document order: template figures first, then nodes appended by the repo app's DOM loop.
const figures = dom => {
  // Only the city sample (class "visual-sample") and Site previews ("visual-sample character-preview"); the repo app's
  // idle-refine and other comparison figures are separate cards.
  const inline = [...dom.pane.innerHTML.matchAll(/<figure class="(visual-sample(?: character-preview)?)"[^>]*>([\s\S]*?)<\/figure>/g)].map(([, cls, body]) => ({
    className: cls, src: unescape(body.match(/<img src="([^"]*)"/)?.[1] ?? ''), href: unescape(body.match(/<a href="([^"]*)"/)?.[1] ?? ''),
    caption: text(body.match(/<figcaption>([\s\S]*?)<\/figcaption>/)?.[1] ?? ''), badge: text(body.match(/<span class="badge[^"]*">([\s\S]*?)<\/span>/)?.[1] ?? ''), body}));
  const appended = dom.card.children.filter(n => n.tag === 'figure' && n.className === 'visual-sample')
    .map(f => ({className: f.className, src: f.children[0].children[0].src, href: f.children[0].href, caption: f.children[1].textContent, badge: ''}));
  return {inline, appended, all: [...inline, ...appended], html: dom.pane.innerHTML};
};

async function run(code, label, {state = bible, sha = SHA} = {}) {
  const dom = contentPane();
  const ids = {content: dom.pane};
  const buttons = ['home', 'world', 'rules', 'characters', 'production', 'assets'].map(view => {
    const b = element('button'); b.dataset.view = view; b.handlers = [];
    b.addEventListener = (type, fn) => type === 'click' && b.handlers.push(fn); return b;
  });
  const json = body => ({ok: true, status: 200, json: async () => structuredClone(body), text: async () => JSON.stringify(body)});
  const fetch = async url => {
    const name = String(url).replace(/^\/api\//, '/').split('?')[0];
    if (name === '/bible') return json(state);
    if (name === '/inventory') return json(inventory);
    if (name === '/state') return json(progress);
    if (name === '/meta') return json({sha, live: true, checkedAt: '2026-10-16T00:00:00Z'});
    if (name === '/feedback') return json({records: []});
    if (name === '/playtests') return json({runs: []});
    if (name === '/playtest-status') return json({phase: 'idle'});
    return {ok: false, status: 404, json: async () => ({})};
  };
  const context = vm.createContext({
    document: {getElementById: id => (ids[id] ||= element()), querySelectorAll: () => buttons, addEventListener() {}, hidden: true,
      createElement: tag => element(tag), body: element('body')},
    window: {addEventListener() {}}, localStorage: {getItem: () => null, setItem() {}}, fetch, setInterval: () => 0, setTimeout: () => 0, clearTimeout() {},
    console, structuredClone, URL, Promise, encodeURIComponent, decodeURIComponent, Date, JSON, Math, Set, Map,
  });
  vm.runInContext(code, context, {filename: label});
  for (let i = 0; i < 20; i++) await new Promise(r => setImmediate(r));
  assert.ok(dom.pane.innerHTML.length > 0 && !dom.pane.innerHTML.includes('暂时无法读取'), label + ': client booted');
  buttons.find(b => b.dataset.view === 'production').handlers.forEach(fn => fn());
  for (let i = 0; i < 20; i++) await new Promise(r => setImmediate(r));
  assert.ok(dom.pane.innerHTML.includes('制作路线'), label + ': Production rendered');
  return figures(dom);
}

function expectRepo(result, label) {
  assert.equal(result.inline.length, 1, label + ': one city sample in the template');
  assert.equal(result.appended.length, previews.length, label + ': every preview appended');
  assert.deepEqual(result.appended.map(f => f.src), previews.map(p => p.file), label + ': preview order and URLs');
  for (const p of [v08, liang]) assert.ok(/未批准/.test(result.appended.find(f => f.src === p.file)?.caption), label + ': ' + p.label + ' UNAPPROVED caption');
  console.log(`PASS ${label}: ${result.all.length} .visual-sample figures (city + ${result.appended.length} previews, v08 + Liang v01 present)`);
}

function expectSite(result, label, sha = SHA) {
  const [cityFig, ...rest] = result.all;
  assert.equal(result.appended.length, 0, label + ': figures are rendered in the template, not appended');
  assert.equal(result.all.length, 1 + previews.length, label + ': city sample + every preview');
  assert.equal(cityFig.src, RAW_MAIN + encodeURIComponent(nameOf(city.file)), label + ': city sample first, unchanged');
  const want = previews.map(p => rawAt(sha) + encodeURIComponent(nameOf(p.file)));
  assert.deepEqual(rest.map(f => f.src), want, label + ': preview order and pinned raw URLs');
  assert.deepEqual(rest.map(f => f.href), want, label + ': preview links open the same pinned raw image');
  for (const f of result.all) assert.ok(!f.src.includes('/assets/') && !f.href.includes('/assets/'), label + ': no /assets/ URL: ' + f.src);
  rest.forEach((f, i) => {
    const p = previews[i];
    assert.ok(f.className.includes('character-preview'), label + ': preview figure class');
    assert.ok(f.caption.startsWith(p.label) && f.caption.endsWith(p.caption), label + ': caption shows label and full caption for ' + p.label);
    if (p === v08 || p === liang) {
      assert.equal(f.badge, '未批准 · 未接入运行时 / Unapproved · nonruntime', label + ': ' + p.label + ' badge from staticBaselinesAndPilots');
    } else {
      assert.equal(f.badge, '审查截图 · 未验收 / Review capture · not accepted', label + ': ' + p.label + ' badge is not-accepted');
    }
    assert.ok(!/已批准|Approved/.test(f.badge), label + ': no preview badge claims approval');
  });
  assert.ok(result.html.includes(`角色画质审查截图 / Character preview captures（${previews.length}）`), label + ': preview grid heading with count');
  assert.ok(result.html.includes(`GitHub 提交 ${sha.slice(0, 7)} 的 outputs/`), label + ': grid names the pinned commit');
  assert.ok(result.html.indexOf('id="character-visual-previews"') < result.html.indexOf('静态候选图不计为四方向精灵'), label + ': grid sits above the static-candidate note');
  console.log(`PASS ${label}: ${result.all.length} .visual-sample figures (city + ${rest.length} previews); all images ${rawAt(sha).slice(0, 72)}…; v08 + Liang v01 badged UNAPPROVED · NONRUNTIME, 7 others "not accepted"`);
}

async function siteEdgeCases(code, label) {
  // Badges follow state data, not captions: flipping the v08 record's flag changes only the v08 badge.
  const flipped = structuredClone(bible);
  flipped.characterVisualReview.staticBaselinesAndPilots.femaleBattleSideviewV08.creatorApproved = true;
  const a = await run(code, label + ' [v08 flag flipped]', {state: flipped});
  assert.equal(a.all.find(f => f.src.endsWith(encodeURIComponent(nameOf(v08.file)))).badge, '已批准静态基准 · 未接入运行时 / Approved static baseline · nonruntime');
  assert.equal(a.all.find(f => f.src.endsWith(encodeURIComponent(nameOf(liang.file)))).badge, '未批准 · 未接入运行时 / Unapproved · nonruntime');
  // Unresolvable or hostile paths get no image or link, and labels are escaped.
  const hostile = structuredClone(bible);
  hostile.characterVisualReview.previews = [
    {label: '<b>x</b>', file: '/assets/../escape.png', caption: '<i>c</i>'},
    {label: 'js', file: 'javascript:alert(1)', caption: 'c'},
    {label: 'nested', file: '/assets/sub/dir.png', caption: 'c'},
  ];
  const b = await run(code, label + ' [hostile paths]', {state: hostile});
  assert.equal(b.all.length, 4, 'hostile: city + 3 text-only figures');
  for (const f of b.all.slice(1)) {
    assert.equal(f.src, '', 'hostile: no image for ' + f.caption);
    assert.equal(f.href, '', 'hostile: no link for ' + f.caption);
    assert.match(f.body, /Image path not resolvable/);
  }
  assert.ok(!b.html.includes('<b>x</b>') && !b.html.includes('<i>c</i>'), 'hostile: label and caption escaped');
  // Without a valid source SHA the images fall back to main, never to /assets/.
  expectSite(await run(code, label + ' [no source sha]', {sha: 'unknown'}), label + ' [no source sha]', 'main');
  console.log(`PASS ${label}: badges follow state flags; unsafe paths render text only; invalid SHA falls back to main`);
}

(async () => {
  expectRepo(await run(git(root, 'show', 'HEAD:' + appRel), 'repo app JS @HEAD'), 'repo app JS @HEAD');
  expectRepo(await run(fs.readFileSync(path.join(root, appRel), 'utf8'), 'repo app JS (working tree)'), 'repo app JS (working tree)');

  const siteFile = path.join(siteDir, 'public', 'bible.js');
  const cssFile = path.join(siteDir, 'public', 'bible.css');
  if (!fs.existsSync(siteFile)) { console.log('SKIP Site cases: no Site source at ' + siteDir); console.log('SITE_PREVIEW_FIGURES PASS (repo only)'); return; }
  const working = fs.readFileSync(siteFile, 'utf8');
  const workingCss = fs.readFileSync(cssFile, 'utf8');
  let original = working, originalCss = workingCss, base = 'working tree';
  if (working.includes(MARKER)) {
    // Find the newest committed bible.js without the patch; it is the client that produced the live 1-figure DOM.
    const revs = git(siteDir, 'log', '--format=%H', '--', 'public/bible.js').split('\n').filter(Boolean);
    const rev = revs.find(r => !git(siteDir, 'show', `${r}:public/bible.js`).includes(MARKER));
    assert.ok(rev, 'Site history has an unpatched bible.js');
    original = git(siteDir, 'show', `${rev}:public/bible.js`);
    originalCss = git(siteDir, 'show', `${rev}:public/bible.css`);
    base = rev.slice(0, 7);
  }
  const before = await run(original, `Site bible.js (unpatched, ${base})`);
  assert.equal(before.all.length, 1, 'unpatched Site: city sample only');
  assert.equal(before.all[0].src, RAW_MAIN + encodeURIComponent(nameOf(city.file)), 'unpatched Site: the one figure is the old inventory city sample');
  console.log(`PASS Site bible.js (unpatched, ${base}): reproduces live DOM, 1 .visual-sample figure (old city sample), 0 previews`);

  const patched = patchSiteBibleJs(original);
  const patchedCss = patchSiteBibleCss(originalCss);
  assert.ok(patched.changed && patchedCss.changed);
  assert.equal(patchSiteBibleJs(patched.text).changed, false, 'JS patch is idempotent');
  assert.equal(patchSiteBibleCss(patchedCss.text).changed, false, 'CSS patch is idempotent');
  assert.ok(patchedCss.text.startsWith(originalCss) && patchedCss.text.includes(CSS_MARKER) && /\.visual-previews\{display:grid/.test(patchedCss.text) &&
    /\.visual-previews figcaption\{font-size:13px/.test(patchedCss.text), 'CSS appends the preview grid and larger captions only');
  expectSite(await run(patched.text, 'Site bible.js (patched in memory)'), 'Site bible.js (patched in memory)');
  await siteEdgeCases(patched.text, 'Site bible.js (patched in memory)');
  if (working.includes(MARKER)) {
    // git show yields LF; a Windows checkout may hold CRLF. Compare content, not line endings.
    const lf = s => s.replace(/\r\n/g, '\n');
    assert.equal(lf(working), lf(patched.text), 'Site working-tree bible.js equals the helper output');
    assert.equal(lf(workingCss), lf(patchedCss.text), 'Site working-tree bible.css equals the helper output');
    expectSite(await run(working, 'Site bible.js (working tree)'), 'Site bible.js (working tree)');
  }
  assert.throws(() => patchSiteBibleJs('function renderProduction(){}'), /exactly one/, 'patch refuses an unknown layout');
  assert.throws(() => patchSiteBibleJs(original.replace('静态候选图不计为四方向精灵', '已改写')), /exactly one static-candidate note/, 'patch refuses a moved template');
  assert.equal(fs.readFileSync(siteFile, 'utf8'), working, 'Site bible.js left unchanged');
  assert.equal(fs.readFileSync(cssFile, 'utf8'), workingCss, 'Site bible.css left unchanged');
  console.log('SITE_PREVIEW_FIGURES PASS');
})().catch(error => { console.error(error); process.exit(1); });
