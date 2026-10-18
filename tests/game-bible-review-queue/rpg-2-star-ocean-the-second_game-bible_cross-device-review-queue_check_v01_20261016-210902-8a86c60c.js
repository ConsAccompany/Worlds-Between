// Focused check for the Game Bible cross-device visual review queue (environmentVisualReview.crossDeviceReviewQueue) and the
// Chicago Loop scene-denominator review. Badges must follow the recorded approval flags, every queue image must be an actual
// Godot capture served byte-identical (three live in run subdirectories; #11 is a root-level byte copy of its nested capture), generated concepts must never render as images, all eleven
// must be committed with the exact recorded blob at the recorded commit (none staged), and no counter or the 40.8% meter may move.
// #10 is the one runtime item: the global map v03 art the live map draws, unapproved, a technical candidate with an inherited failing check.
// #11 is the Chicago State/Lake v03r1 zh arrival: opt-in only (off by default), partly generated underpainting, two directories deep.
// 2026-10-17 stale-text correction: #3 City Hall Park v04 is a creator-rejected historical comparison, #7/#8 v11 was reviewed and
// rejected for more static polish, #1 names run v04 as the latest creator-reviewed locomotion; no item removed, pinned fields unchanged.
// Starts the real v05 panel server on a spare local port, then runs the served bible.js in a VM with a minimal DOM stub.
// Read-only: no project file is written. Run from the repository root: node tests/game-bible-review-queue/<this file>
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const net = require('node:net');
const path = require('node:path');
const vm = require('node:vm');
const {spawn, spawnSync} = require('node:child_process');

const root = path.resolve(__dirname, '..', '..');
const rel = file => path.join(root, ...file.split('/'));
const server = rel('tools/rpg-2-star-ocean-the-second_game-bible_server_v05_20261013-222437-3d5b8a9f.js');
const meterCli = 'tools/rpg-2-star-ocean-the-second_mvp-completion-meter_recompute-and-task-closeout-cli_v01_20261015-233032-d296a2cb.js';
const biblePath = 'outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json';
const progressPath = 'outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json';
const inventoryPath = 'outputs/rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json';
const sha256 = data => crypto.createHash('sha256').update(data).digest('hex');
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const pass = label => console.log('PASS ' + label);
const git = (...args) => spawnSync('git', args, {cwd: root, encoding: 'utf8'});
const tracked = file => git('ls-files', '--error-unmatch', file).status === 0;

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
async function renderProduction(base) {
  const element = () => ({innerHTML: '', textContent: '', value: '', dataset: {}, addEventListener() {}, setAttribute() {}, querySelector: () => element(), querySelectorAll: () => []});
  const content = {...element(), querySelector: () => element()};
  const elements = {content, search: element(), edition: element(), pitch: element(), 'footer-status': element()};
  const nav = ['home', 'world', 'rules', 'characters', 'production', 'assets'].map(view => {
    const button = {...element(), dataset: {view}, handlers: {}};
    button.addEventListener = (type, handler) => { button.handlers[type] = handler; };
    return button;
  });
  const context = vm.createContext({
    document: {getElementById: id => elements[id], querySelectorAll: () => nav, addEventListener() {}, hidden: true, createElement: () => element()},
    fetch: (url, options) => fetch(base + url, options), setInterval() {}, localStorage: {getItem: () => '', setItem() {}}, console,
  });
  vm.runInContext(await (await fetch(base + '/bible.js')).text(), context, {filename: 'bible.js'});
  await waitFor(() => elements.edition.textContent !== '', 'initial bible load');
  nav.find(button => button.dataset.view === 'production').handlers.click();
  await waitFor(() => content.innerHTML.includes('id="cross-device-review-queue"'), 'review queue card');
  return content.innerHTML;
}

(async () => {
  // Local-only captures are absent in a clean clone; their checks then reduce to 'untracked and pinned', and they must not be served.
  const present = item => fs.existsSync(rel(item.file));
  const before = [biblePath, progressPath, inventoryPath].map(file => sha256(fs.readFileSync(rel(file))));
  const bible = JSON.parse(fs.readFileSync(rel(biblePath), 'utf8'));
  const progress = JSON.parse(fs.readFileSync(rel(progressPath), 'utf8'));
  const env = bible.environmentVisualReview;
  const queue = env.crossDeviceReviewQueue;

  // 1. Nine actual Godot captures, in order, each with its own QA note; badges follow the recorded flags.
  assert.ok(queue && Array.isArray(queue.items), 'queue present');
  assert.deepEqual(queue.items.map(item => item.order), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
  assert.ok(queue.items.every(item => item.kind === 'actual-godot-capture'), 'every queue item is an actual Godot capture');
  assert.ok(fs.existsSync(rel(queue.source)), 'queue source note exists');
  const v8Baseline = bible.characterVisualReview.staticBaselinesAndPilots.femaleExplorationSouthBaseline;
  for (const item of queue.items) {
    assert.match(item.file, /^outputs\/([A-Za-z0-9][A-Za-z0-9._-]*\/){0,2}[A-Za-z0-9][A-Za-z0-9._-]*\.png$/, 'queue file is a PNG under outputs/');
    assert.ok(item.syncState === 'local-only' || present(item), 'committed queue image exists: ' + item.file);
    assert.ok(item.qa && fs.existsSync(rel(item.qa)), 'queue QA note exists: ' + item.qa);
    assert.equal(item.runtimeIntegrated, item.order === 10, 'only #10 (live map art v03) is runtime: ' + item.order);
    assert.equal(item.artAccepted, false, 'not accepted: ' + item.order);
    assert.equal(item.creatorApproved, item.order === 1, 'only the selout v8 still is creator-approved');
    assert.equal(item.badge.tone, item.creatorApproved ? 'good' : 'warn');
    assert.ok(item.creatorApproved ? /Approved static baseline/.test(item.badge.en) : /^Unapproved/.test(item.badge.en), 'stored badge matches flag: ' + item.order);
    if (item.runtimeIntegrated) assert.ok(/runtime map art \(not accepted\)/.test(item.badge.en) && /已接入运行时/.test(item.badge.zh) && /technical candidate/.test(item.badge.en), 'stored badge says runtime, technical candidate, not accepted: ' + item.order);
    else assert.ok(/nonruntime/.test(item.badge.en) && /未接入运行时/.test(item.badge.zh), 'stored badge says nonruntime: ' + item.order);
  }
  assert.equal(v8Baseline.creatorApproved, true);
  assert.equal(v8Baseline.runtimeIntegrated, false);
  assert.match(queue.items[0].approvalScope, /static south still/);
  // #7/#8: female battle v11 bright/dark captures for creator feedback. Only the 0.65 proportion is approved; the editable
  // source is tracked at the same commit and its manifest still says unapproved and not runtime-integrated.
  const v11 = queue.items.slice(6, 8);
  assert.deepEqual(v11.map(item => item.file.match(/party-capture-([a-z]+)-640_unapproved-v11_/)?.[1]), ['archive', 'outskirts']);
  for (const item of v11) {
    assert.equal(item.syncState, 'committed-at-53a912f', 'v11 capture committed at 53a912f: ' + item.order);
    assert.equal(item.approvedScopeOnly, '0.65 battle display proportion');
    assert.ok(/v11/.test(item.label.en) && /v11/.test(item.label.zh), 'v11 label: ' + item.order);
    assert.ok(fs.existsSync(rel(item.reviewPacket)) && fs.existsSync(rel(item.captureManifest)), 'v11 review packet and capture manifest exist: ' + item.order);
    const captureManifest = JSON.parse(fs.readFileSync(rel(item.captureManifest), 'utf8'));
    assert.equal(captureManifest.captureSha256, item.sha256, 'capture manifest pins the queue sha256: ' + item.order);
    for (const source of Object.values(item.editableSource)) {
      assert.ok(git('rev-parse', '--verify', '--quiet', '53a912f:' + source).status === 0 && tracked(source), 'v11 source tracked at 53a912f: ' + source);
    }
    const sprite = JSON.parse(fs.readFileSync(rel(item.editableSource.manifest), 'utf8'));
    assert.deepEqual([sprite.art_approved, sprite.runtime_integrated], [false, false], 'v11 sprite manifest: unapproved, nonruntime');
    assert.equal(captureManifest.candidateSha256, sha256(fs.readFileSync(rel(item.editableSource.png))), 'capture used the tracked v11 sprite: ' + item.order);
  }
  assert.ok(/^Unapproved static pilot/.test(v11[0].caption.en) && /only the 0.65 proportion is approved/.test(v11[0].caption.en) && /Not a complete character sprite; no animation/.test(v11[0].caption.en), 'v11 caption states its limits');
  assert.equal(git('grep', '-l', 'unapproved-v11_20261017-023937-873fe1e6', 'HEAD', '--', 'game/scripts', 'game/scenes').stdout.trim(), '', 'no runtime script or scene references the v11 sprite');
  for (const item of v11) {
    assert.deepEqual([item.creatorReview.date, item.creatorReview.outcome, item.creatorReview.creatorAnswer], ['2026-10-17', 'rejected-more-static-polish', '继续精修静止帧'], 'v11 creator review recorded: ' + item.order);
    assert.ok(fs.existsSync(rel(item.creatorReview.evidence)) && /rejected for more static polish/.test(item.badge.en) && /继续精修静止帧/.test(item.badge.zh), 'v11 review evidence and badge: ' + item.order);
    assert.ok(/继续精修静止帧/.test(item.caption.zh) && /more static polish/.test(item.caption.en) && !/for creator feedback only/.test(item.caption.en), 'v11 caption no longer says it awaits feedback: ' + item.order);
  }
  // Stale-text correction of 2026-10-17: #3 City Hall Park v04 rejected (historical comparison), #1 names the latest reviewed run.
  const chp4 = queue.items[2];
  assert.equal(chp4.syncState, 'committed-at-15d153b');
  assert.deepEqual([chp4.creatorReview.date, chp4.creatorReview.outcome, chp4.creatorReview.useNow], ['2026-10-16', 'rejected', 'historical-comparison-only']);
  assert.ok(tracked(chp4.creatorReview.evidence) && /Withdraw v04 from final scene-quality review/.test(fs.readFileSync(rel(chp4.creatorReview.evidence), 'utf8')), 'v04 rejection evidence is the tracked style-alignment note');
  assert.ok(/v04/.test(chp4.label.en) && /rejected, historical comparison/.test(chp4.label.en) && /已否决/.test(chp4.label.zh), 'v04 label says rejected');
  assert.ok(/^Rejected historical comparison/.test(chp4.caption.en) && /^已否决的历史对照/.test(chp4.caption.zh) && !/still under review/.test(chp4.caption.en), 'v04 caption no longer says under review');
  const motion = queue.items[0].motionStatus;
  assert.deepEqual([motion.creatorChoice, motion.outcome], ['继续打磨跑动或停步', 'revision-requested']);
  assert.ok(/south run v04/.test(motion.latestCreatorReviewed) && fs.existsSync(rel(motion.evidence)) && fs.readFileSync(rel(motion.evidence), 'utf8').includes('继续打磨跑动或停步'), 'run v04 creator choice evidence');
  assert.ok(/south run v04/.test(queue.items[0].caption.en) && /smoother run and stop/.test(queue.items[0].caption.en) && /跑步 v04/.test(queue.items[0].caption.zh), '#1 caption names the latest reviewed run');
  const correction = (queue.corrections || []).find(c => c.date === '2026-10-17');
  assert.ok(correction && fs.existsSync(rel(correction.qa)) && /No item was removed/.test(correction.en), 'correction record with QA note');
  assert.deepEqual(correction.items, [1, 3, 7, 8, 10]);
  pass('stale-text correction: #3 v04 rejected historical comparison (tracked evidence), #7/#8 v11 reviewed and rejected for more static polish, #1 names run v04 (smoother run/stop requested), correction record and QA note present');
  // #9: City Hall Park v06 zh entry. Generated source (about 80% of visible pixels from an AI-generated reference), opt-in only
  // and off by default; the capture, editable source and generated reference are tracked at 1548c9e and still say unapproved.
  const chp6 = queue.items[8];
  assert.equal(chp6.syncState, 'committed-at-1548c9e');
  assert.match(chp6.file, /^outputs\/nyc-chp-v06_20261017-165253-4519dffe\/[^/]+_godot-zh-entry-640x360_unapproved-v06_20261017-165253-4519dffe\.png$/);
  assert.ok(/v06/.test(chp6.label.en) && /v06/.test(chp6.label.zh), 'v06 label');
  assert.equal(chp6.sourceProvenance.kind, 'generated-source');
  assert.ok(chp6.sourceProvenance.visiblePixelShareFromReference >= 0.8 && /Not hand-painted/.test(chp6.sourceProvenance.note), 'generated share and no hand-painted claim');
  assert.ok(/generated source/.test(chp6.badge.en) && /生成源/.test(chp6.badge.zh), 'badge says generated source');
  assert.ok(/AI-generated reference/.test(chp6.caption.en) && /not hand-painted/.test(chp6.caption.en) && /Off by default/.test(chp6.caption.en), 'v06 caption states provenance and opt-in');
  assert.deepEqual([chp6.optInOnly.flag, chp6.optInOnly.defaultOff], ['-- --city-hall-park-v06', true]);
  assert.ok(fs.existsSync(rel(chp6.reviewPacket)) && fs.existsSync(rel(chp6.qa)), 'v06 review packet and QA note exist');
  const chp6Tracked = [chp6.file, chp6.captureManifest, chp6.sourceProvenance.generatedReference, ...Object.values(chp6.editableSource)];
  for (const source of chp6Tracked) {
    assert.ok(git('rev-parse', '--verify', '--quiet', '1548c9e:' + source).status === 0 && tracked(source), 'v06 file tracked at 1548c9e: ' + source);
  }
  assert.equal(sha256(fs.readFileSync(rel(chp6.sourceProvenance.generatedReference))), chp6.sourceProvenance.generatedReferenceSha256, 'generated reference hash');
  assert.equal(JSON.parse(fs.readFileSync(rel(chp6.captureManifest), 'utf8')).captures[path.posix.basename(chp6.file)], chp6.sha256, 'capture manifest pins the queue sha256');
  assert.match(JSON.parse(fs.readFileSync(rel(chp6.editableSource.manifest), 'utf8')).status, /^UNAPPROVED/, 'v06 scene manifest: unapproved');
  const park = fs.readFileSync(rel('game/scripts/city_hall_park_v06_scene.gd'), 'utf8');
  assert.ok(['static var enabled_override := -1', 'OS.get_cmdline_user_args().has(CLI_FLAG)', 'const CLI_FLAG := "--city-hall-park-v06"'].every(text => park.includes(text)),'v06 runtime is off unless the flag or a test override is set');
  pass('#9: City Hall Park v06 zh entry, generated source (>=80% reference), opt-in only/off by default, capture + .pxo/.ora/flat/manifest + generated reference tracked at 1548c9e, manifest unapproved');

  // #10: global map v03 Chicago flight card (zh). Technical candidate: the live map draws this art since ec8b8f5, but it is
  // unapproved and unaccepted. The raw URL is pinned to the full commit SHA, and the inherited background-visual-check failure
  // is stated on the item and in its caption (it fails identically with the parent commit's map scripts; not all-pass).
  const map3 = queue.items[9];
  const map3Commit = 'ec8b8f564ff80d137df903b1b11186fd01bf4215';
  assert.equal(map3.syncState, 'committed-at-ec8b8f5');
  assert.equal(map3.technicalCandidate, true);
  assert.match(map3.file, /^outputs\/rpg-2-star-ocean-the-second_global-map_native-art_us-great-lakes-card-chicago-air-zh-640x360_test-only-v03_20261017-175314-e8b8f8af\.png$/);
  assert.equal(map3.rawUrl, 'https://raw.githubusercontent.com/ConsAccompany/Worlds-Between/' + map3Commit + '/' + map3.file, 'raw URL pinned to the full commit SHA');
  assert.ok(/v03/.test(map3.label.en) && /v03/.test(map3.label.zh), 'v03 label');
  assert.ok(/^Unapproved technical candidate/.test(map3.caption.en) && /^未批准的技术候选/.test(map3.caption.zh), 'caption says unapproved technical candidate');
  assert.ok(/background-visual-check still fails \(button geometry scifi\.city\)/.test(map3.caption.en) && /background-visual-check 仍失败/.test(map3.caption.zh), 'caption states the inherited failure');
  assert.equal(map3.inheritedTestFailure.failure, 'WORLD_MAP_VISUAL_CHECK_FAILED: button geometry scifi.city');
  assert.equal(map3.inheritedTestFailure.sameWithParentMapScripts, true);
  assert.ok(fs.existsSync(rel(map3.inheritedTestFailure.test)) && /not all-pass/.test(map3.inheritedTestFailure.note), 'inherited failing test exists and is not called all-pass');
  assert.ok(fs.existsSync(rel(map3.reviewPacket)) && fs.existsSync(rel(map3.qa)), 'v03 review packet and QA note exist');
  const map3Runtime = ['game/scripts/scifi_world_map.gd', 'game/scripts/world_map_data.gd', 'game/scripts/world_map_text.gd',
    'game/data/world-map/rpg-2-star-ocean-the-second_earth-map_us-east-relief-layer_m2-map-art-native-v03_20261017-175314-e8b8f8af.json'];
  for (const source of [map3.file, map3.captureManifest, map3.qa, ...map3Runtime]) {
    assert.ok(git('rev-parse', '--verify', '--quiet', map3Commit + ':' + source).status === 0 && tracked(source), 'v03 file tracked at ec8b8f5: ' + source);
  }
  const map3Manifest = JSON.parse(fs.readFileSync(rel(map3.captureManifest), 'utf8'));
  assert.equal(map3Manifest.captures.find(c => c.file === path.posix.basename(map3.file))?.sha256, map3.sha256, 'capture manifest pins the queue sha256');
  // The live map reads the v03 relief at ec8b8f5, or the later UNAPPROVED v03r2 relief once that pass is synced (laterLocalPasses).
  const mapData = fs.readFileSync(rel('game/scripts/world_map_data.gd'), 'utf8');
  const v03r2Relief = 'game/data/world-map/rpg-2-star-ocean-the-second_earth-map_us-east-relief-layer_m2-map-art-native-v03r2_20261017-224631-9875b9e2.json';
  assert.ok(mapData.includes('us-east-relief-layer_m2-map-art-native-v03_20261017-175314-e8b8f8af.json')
    || (mapData.includes(path.posix.basename(v03r2Relief)) && fs.existsSync(rel(v03r2Relief))), 'the live map reads the v03 relief or the v03r2 relief that supersedes it');
  assert.ok(map3.laterLocalPasses.qa.every(file => fs.existsSync(rel(file))) && /Neither pass is accepted/.test(map3.laterLocalPasses.note), 'later v03r1/v03r2 passes noted, unaccepted');
  pass('#10: global map v03 Chicago flight card zh, technical candidate, runtime map art but unapproved/unaccepted, raw URL pinned to ec8b8f5, capture + manifest + QA + map scripts + v03 relief tracked at ec8b8f5, inherited background-visual-check failure stated');
  // #11: Chicago State/Lake v03r1 zh arrival. Opt-in only (off by default: the Loop stays v02), about 20% of visible pixels from a
  // generated-reference underpainting; capture, editable source, generated reference and the opt-in wiring are tracked at cdc5865.
  // The deployed Site rejects the two-directory capture path, so the queue file is an exact byte copy at outputs/ root, committed at 6795926.
  const chi = queue.items[10];
  const chiCommit = 'cdc58657a247cb5741e1afa59989e0d3b5bacc91';
  const chiRootCommit = '67959265715fe356b29b41e51051d35fe1d9d23f';
  assert.equal(chi.syncState, 'committed-at-6795926');
  assert.match(chi.file, /^outputs\/rpg-2-star-ocean-the-second_chicago-loop_state-lake-godot-zh-entry-640x360-site-root-copy_unapproved-v03r1_20261017-191314-8f6d4a7f\.png$/);
  assert.equal(chi.rawUrl, 'https://raw.githubusercontent.com/ConsAccompany/Worlds-Between/' + chiRootCommit + '/' + chi.file, 'raw URL pinned to the full commit SHA');
  const chiOriginal = chi.siteRootCopy.originalFile;
  assert.match(chiOriginal, /^outputs\/chicago-loop-state-lake-v03r1\/godot-runtime\/rpg-2-star-ocean-the-second_chicago-loop_state-lake-godot-zh-entry-640x360_v03r1_20261017-184340-44bc6d7f\.png$/);
  assert.equal(chi.siteRootCopy.originalSyncState, 'committed-at-cdc5865');
  assert.equal(chi.siteRootCopy.originalRawUrl, 'https://raw.githubusercontent.com/ConsAccompany/Worlds-Between/' + chiCommit + '/' + chiOriginal, 'original raw URL pinned to cdc5865');
  assert.equal(git('rev-parse', chiCommit + ':' + chiOriginal).stdout.trim(), chi.gitBlob, 'nested original at cdc5865 has the same blob');
  assert.ok(tracked(chiOriginal) && fs.readFileSync(rel(chiOriginal)).equals(fs.readFileSync(rel(chi.file))), 'nested original kept and byte-identical to the root copy');
  assert.ok(/v03r1/.test(chi.label.en) && /v03r1/.test(chi.label.zh), 'v03r1 label');
  assert.deepEqual([chi.optInOnly.flag, chi.optInOnly.defaultOff], ['-- --chicago-state-lake-v03r1', true]);
  assert.ok(/opt-in, off by default/.test(chi.badge.en) && /默认关闭/.test(chi.badge.zh) && /partly generated/.test(chi.badge.en), 'badge says opt-in and partly generated');
  assert.equal(chi.sourceProvenance.kind, 'partly-generated-underpainting');
  assert.ok(chi.sourceProvenance.visiblePixelShareFromReference > 0.2 && chi.sourceProvenance.visiblePixelShareFromReference < 0.21, 'underpainted share recorded');
  assert.equal(sha256(fs.readFileSync(rel(chi.sourceProvenance.generatedReference))), chi.sourceProvenance.generatedReferenceSha256, 'generated reference hash');
  assert.ok(/^Unapproved actual Godot/.test(chi.caption.en) && /Off by default/.test(chi.caption.en) && /busy and muddy/.test(chi.caption.en) && /scenes stay 3\/12/.test(chi.caption.en), 'caption states opt-in, facade defect and unchanged count');
  assert.ok(/^未批准/.test(chi.caption.zh) && /默认关闭/.test(chi.caption.zh) && /杂乱/.test(chi.caption.zh), 'zh caption states opt-in and facade defect');
  assert.ok(fs.existsSync(rel(chi.reviewPacket)) && fs.existsSync(rel(chi.qa)), 'v03r1 sync closeout and QA note exist');
  const loopScene = 'game/scenes/rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn';
  const chiSelector = 'game/scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-scene-opt-in-selector_unapproved-v03r1_20261017-183235-a00fabf3.gd';
  for (const source of [chiOriginal, chi.qa, chi.reviewPacket, chi.sourceProvenance.generatedReference, ...Object.values(chi.editableSource), loopScene, chiSelector]) {
    assert.ok(git('rev-parse', '--verify', '--quiet', chiCommit + ':' + source).status === 0 && tracked(source), 'v03r1 file tracked at cdc5865: ' + source);
  }
  assert.match(JSON.parse(fs.readFileSync(rel(chi.editableSource.manifest), 'utf8')).status, /^UNAPPROVED/, 'v03r1 layer manifest: unapproved');
  const selector = fs.readFileSync(rel(chiSelector), 'utf8');
  assert.ok(fs.readFileSync(rel(loopScene), 'utf8').includes(path.posix.basename(chiSelector)), 'the Loop scene runs the opt-in selector');
  assert.ok(['extends "res://scripts/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-scene_unapproved-v02_20261017-160959-55667f46.gd"',
    'static var v03r1_override := -1', 'OS.get_cmdline_user_args().has(V03R1_FLAG)', 'const V03R1_FLAG := "--chicago-state-lake-v03r1"', '\t\tsuper()'].every(text => selector.includes(text)),
    'v03r1 is off unless the flag or a test override is set; otherwise the selector falls through to v02');
  pass('#11: Chicago State/Lake v03r1 zh arrival, opt-in only/off by default (Loop stays v02), partly generated underpainting (~20%), root byte copy with raw URL pinned to 6795926, nested original capture + .pxo/.ora/preview/manifest + generated reference + Loop scene + selector tracked at cdc5865, manifest unapproved');
  pass('queue: 11 actual Godot captures in order, QA notes on disk, only #1 (selout v8 still) creator-approved, only #10 runtime, none accepted; #7/#8 v11 archive/outskirts with tracked .pxo/.ora/PNG/manifest at 53a912f, unreferenced by runtime');

  // 2. Sync state matches Git: all eight are committed, none staged or local-only. Each recorded short SHA resolves to a commit in
  // HEAD's history, and the blob at <sha>:<file> is exactly the recorded gitBlob; the working file has the recorded blob and sha256.
  // The three former Git-proposal captures (#3, #5, #6) are committed at 15d153b and stay sha256-pinned in their evidence index.
  const staged = queue.items.filter(item => item.syncState === 'staged-not-pushed');
  assert.equal(staged.length, 0, 'no queue image is still staged-not-pushed');
  assert.equal(queue.items.filter(item => item.syncState === 'local-only').length, 0, 'no queue image is local-only');
  for (const item of queue.items) {
    assert.match(item.syncState, /^committed-at-[0-9a-f]{7}$/, 'committed: ' + item.order);
    assert.match(item.gitBlob, /^[0-9a-f]{40}$/, 'recorded blob: ' + item.order);
    const commit = git('rev-parse', '--verify', '--quiet', item.syncState.slice('committed-at-'.length) + '^{commit}').stdout.trim();
    assert.match(commit, /^[0-9a-f]{40}$/, 'recorded commit resolves: ' + item.order);
    assert.equal(git('merge-base', '--is-ancestor', commit, 'HEAD').status, 0, 'recorded commit is in HEAD history: ' + item.order);
    assert.equal(git('rev-parse', commit + ':' + item.file).stdout.trim(), item.gitBlob, 'exact blob at the recorded commit: ' + item.order);
    assert.ok(tracked(item.file), 'committed item is tracked: ' + item.file);
    assert.equal(git('hash-object', '--', item.file).stdout.trim(), item.gitBlob, 'working file blob matches: ' + item.order);
    assert.equal(sha256(fs.readFileSync(rel(item.file))), item.sha256, 'recorded sha256 matches the file: ' + item.order);
    if (item.hashPinnedIn) {
      const index = JSON.stringify(JSON.parse(fs.readFileSync(rel(item.hashPinnedIn), 'utf8')));
      assert.ok(index.includes(item.sha256), 'sha256 still pinned in its evidence index: ' + item.order);
    }
  }
  const proposal = queue.gitProposal;
  assert.deepEqual(proposal.items, [3, 5, 6]);
  assert.equal(proposal.state, 'committed-at-15d153b');
  for (const order of proposal.items) {
    const item = queue.items[order - 1];
    assert.equal(item.syncState, 'committed-at-15d153b', 'proposal item committed at 15d153b: ' + order);
    assert.match(item.file, /unapproved/, 'proposal capture is labelled unapproved in its name: ' + order);
    assert.ok(item.hashPinnedIn, 'proposal item keeps its evidence index: ' + order);
  }
  assert.ok(fs.existsSync(rel(proposal.qa)) && fs.existsSync(rel(proposal.syncQa)), 'Git proposal and sync QA notes exist');
  assert.ok(!/stag/i.test(proposal.state + ' ' + proposal.note), 'Git proposal no longer claims a staged state');
  assert.ok(/site version 11/.test(queue.siteRendering) && !/site version 10/.test(queue.siteRendering), 'Site note names deployed site version 11');
  assert.ok(/eleven actual Godot captures are on GitHub/.test(queue.siteRendering), 'Site note says eleven captures are on GitHub');
  assert.ok(!/staged|local-only|until the coordinator/.test(queue.siteRendering), 'Site note has no stale staged or local-only claim');
  const committed = queue.items.length;
  pass(`sync state: ${committed}/11 committed (#1, #2, #4 at a87ac16; #3, #5, #6 at 15d153b; #7, #8 at 53a912f; #9 at 1548c9e; #10 at ec8b8f5; #11 root copy at 6795926), each exact recorded blob at its recorded commit in HEAD history, 0 staged, 0 local-only; Site note says site version 11`);

  // 3. Generated concepts are a separate, gallery-ineligible list and never appear among queue items or Site previews.
  const concepts = queue.nonruntimeConcepts;
  assert.equal(concepts.galleryEligible, false);
  assert.equal(concepts.items.length, 5);
  assert.ok(concepts.items.every(c => ['generated-concept', 'identity-reference'].includes(c.kind) && /^outputs\/[^/]+\.png$/.test(c.file)));
  const queueFiles = new Set(queue.items.map(item => item.file));
  const previewNames = (bible.characterVisualReview.previews || []).map(p => path.posix.basename(p.file));
  assert.ok(concepts.items.every(c => !queueFiles.has(c.file) && !previewNames.includes(path.posix.basename(c.file))), 'no concept in the queue or Site previews');
  pass('concepts: 5 nonruntime references, galleryEligible false, none in the queue or characterVisualReview.previews');

  // 4. Counters and meter as recorded (sprites 0/52, scenes 3/12, playtests 0/2, 40.8%); Chicago denominator proposal recorded but not applied, with the meter recomputed from the formula.
  const counters = progress.approvalLedger.counters;
  assert.deepEqual([counters.runtimeSpritesAccepted, counters.runtimeSpritesTarget, counters.sceneVisualsAccepted, counters.sceneVisualsTarget, counters.humanPlaytests, counters.humanPlaytestsTarget], [0, 52, 3, 12, 0, 2]);
  assert.equal(env.sceneQualityAccepted, counters.sceneVisualsAccepted, 'Bible scene count equals the ledger (three creator acceptances of 2026-10-17)');
  assert.equal(env.sceneQualityTarget, 12);
  const review = env.sceneQualityDenominatorReview;
  assert.equal(review.applied, true);
  assert.equal(review.currentDenominator, 12);
  assert.equal(review.previousDenominator, 11);
  const revision = progress.completionMeter.taskCloseouts.find(c => c.id === review.appliedCloseoutId);
  assert.ok(revision && revision.kind === 'baseline-revision' && revision.impact.changed === false && revision.impact.percentAfter === 35.8, 'dated baseline-revision closeout recorded');
  assert.deepEqual(revision.impact.baselineChanges, [{category: 'science-environment-art', field: 'denominator', from: 11, to: 12}]);
  assert.equal(review.proposedGateId, 'chicago-loop-outdoor');
  assert.equal(review.originalGates.length, 11);
  assert.ok(!review.originalGates.includes(review.proposedGateId));
  assert.ok(review.qa && fs.existsSync(rel(review.qa)), 'denominator QA note exists');
  assert.equal(review.secondBatch.outcome, 'applied');
  assert.equal(review.secondBatch.creatorConflictFound, false);
  assert.ok(fs.existsSync(rel(review.secondBatch.qa)), 'second-batch QA note exists');
  const meter = spawnSync(process.execPath, [meterCli, 'check'], {cwd: root, encoding: 'utf8'});
  assert.equal(meter.status, 0, meter.stdout + meter.stderr);
  assert.match(meter.stdout, /CHECK OK 40\.8%/);
  const cats = Object.fromEntries(progress.completionMeter.categories.map(c => [c.id, c]));
  const points = denominatorForEnv => Object.values(cats).reduce((sum, c) => sum + c.weight * c.numerator / (c.id === 'science-environment-art' ? denominatorForEnv : c.denominator), 0);
  assert.equal(cats['science-environment-art'].numerator, 3);
  assert.equal(Math.round(points(12) * 10) / 10, 40.8, 'formula with 3/12 scenes gives the recorded 40.8%');
  assert.equal(progress.completionMeter.percent, 40.8);
  pass('counters 0/52 3/12 0/2; meter CLI CHECK OK 40.8%; Chicago gate 12 applied by a dated baseline-revision closeout (35.8% at the time); formula gives 40.8% for /12');

  // 5. Rendered Production view: one card, eleven figures with flag-derived badges, images served byte-identical, concepts as text only.
  const port = await freePort();
  const child = spawn(process.execPath, [server], {cwd: root, env: {...process.env, WORLDS_BETWEEN_BIBLE_PORT: String(port)}, stdio: 'ignore'});
  const base = 'http://127.0.0.1:' + port;
  try {
    await waitFor(async () => { try { return (await fetch(base + '/health')).ok; } catch { return false; } }, 'server');
    const html = await renderProduction(base);
    const start = html.indexOf('<section class="card" id="cross-device-review-queue">');
    assert.ok(start > 0);
    assert.equal(html.split('id="cross-device-review-queue"').length, 2, 'exactly one queue card');
    const card = html.slice(start, html.indexOf('</section>', start) + '</section>'.length);
    const figures = card.split('<figure class="visual-sample review-queue-item"').slice(1);
    assert.equal(figures.length, 11);
    assert.equal((card.match(/badge good">已批准静态基准 · 未接入运行时 · 未验收</g) || []).length, 1);
    assert.equal((card.match(/badge warn">未批准 · 未接入运行时 · 未验收</g) || []).length, 9);
    assert.equal((card.match(/badge warn">未批准 · 已接入运行时 · 未验收</g) || []).length, 1, '#10 renders as unapproved runtime, unaccepted');
    assert.equal((card.match(/仅本机 · 尚未同步到 GitHub/g) || []).length, 0, 'no local-only badge');
    assert.equal((card.match(/已暂存为 Git 候选/g) || []).length, 0, 'no staged badge');
    assert.equal((card.match(/已在 GitHub（[0-9a-f]{7}）/g) || []).length, 11);
    assert.equal((card.match(/已在 GitHub（ec8b8f5）/g) || []).length, 1);
    assert.equal((card.match(/已在 GitHub（6795926）/g) || []).length, 1);
    assert.equal((card.match(/已在 GitHub（1548c9e）/g) || []).length, 1);
    assert.equal((card.match(/已在 GitHub（a87ac16）/g) || []).length, 3);
    assert.equal((card.match(/已在 GitHub（15d153b）/g) || []).length, 3);
    assert.equal((card.match(/已在 GitHub（53a912f）/g) || []).length, 2);
    assert.ok(!/已验收|通过验收/.test(card.replace(/未验收/g, '')), 'no acceptance claim');
    assert.ok(!/<button|<input|type="checkbox"/.test(card), 'no approval controls');
    const imgs = [...card.matchAll(/<img src="([^"]+)"/g)].map(m => m[1]);
    assert.equal(imgs.length, 11);
    for (const [i, src] of imgs.entries()) {
      const response = await fetch(base + src);
      if (!present(queue.items[i])) { assert.equal(response.status, 404, 'absent local-only capture is not served: ' + src); continue; }
      assert.equal(response.status, 200, src);
      assert.equal(response.headers.get('content-type'), 'image/png');
      assert.equal(sha256(Buffer.from(await response.arrayBuffer())), sha256(fs.readFileSync(rel(queue.items[i].file))), 'served byte-identical: ' + src);
    }
    for (const c of concepts.items) assert.ok(!imgs.some(src => src.includes(path.posix.basename(c.file))) && card.includes(c.file), 'concept listed as text only');
    for (const probe of ['/assets/wdc-cw-v08_20261016-155827-6cf49486/technical-check-report.png', '/assets/nyc-chp-v04_20261016-172144-eb092a52/..%2F..%2Fpackage.png',
      '/assets/..%2Ftools%2Fx.png', '/assets/wdc-cw-v08_20261016-155827-6cf49486%2Frpg-2-star-ocean-the-second_wdc-capitol-west_godot-1280x720-entry_unapproved-v08_20261016-155827-6cf49486.png']) {
      assert.equal((await fetch(base + probe)).status, 404, 'non-allowlisted nested path 404: ' + probe);
    }
    pass(`Production view: one queue card, 11 figures (1 approved-static, 9 unapproved nonruntime, 1 unapproved runtime, none accepted), ${committed} GitHub sync badges (3 a87ac16 + 3 15d153b + 2 53a912f + 1 1548c9e + 1 ec8b8f5 + 1 6795926, 0 staged, 0 local-only), 11 images served byte-identical, 5 concepts as text only, 4 nested/traversal probes 404`);
  } finally { child.kill(); }

  const after = [biblePath, progressPath, inventoryPath].map(file => sha256(fs.readFileSync(rel(file))));
  assert.deepEqual(after, before);
  pass('read-only: Game Bible, progress and inventory hashes unchanged');
  console.log('RESULT PASS (7 checks)');
})().catch(error => { console.error('FAIL ' + (error.stack || error.message)); process.exit(1); });
