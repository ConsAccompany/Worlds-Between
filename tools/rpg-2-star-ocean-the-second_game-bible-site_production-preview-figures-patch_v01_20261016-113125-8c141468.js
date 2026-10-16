// Ports the Game Bible Production preview figures into the private cloud Site client (public/bible.js + public/bible.css).
// The Site serves its own forked bible.js and fetches only the three state JSON files from GitHub, so the loop added to
// outputs/rpg-2-star-ocean-the-second_game-bible_app_v01_20261013-195526-90e7bc24.js never reaches the live page; there
// the Production tab shows only the inventory city sample and none of characterVisualReview.previews.
// The Site has no /assets route (those URLs 404), so every preview image is resolved to the committed PNG under outputs/
// on raw.githubusercontent.com, pinned to the commit the state was read from (main if that SHA is unknown). A file that is
// not a flat outputs/*.png name is shown as text with no image. The status badge comes from staticBaselinesAndPilots
// (creatorApproved / runtimeIntegrated, matched by capture file) or characterVisualReview.artAccepted, never from captions.
// Usage: node tools/<this file> <site-source-dir> [--write]
// Without --write it only reports what it would change. It never deploys, commits or touches this repository.
const fs = require('node:fs');
const path = require('node:path');

const MARKER = '// characterVisualReview.previews: one captioned figure per preview after the city sample, image pinned to the GitHub commit the state came from.';
const CSS_MARKER = '/* characterVisualReview.previews figures */';
// The Production template literal; the preview HTML is computed just before it.
const LOGIC_ANCHOR = "    content.innerHTML=`${head('制作路线',";
// The note that follows the city sample inside the visual card; the preview grid goes in front of it.
const TEMPLATE_ANCHOR = '<p class="muted small">静态候选图不计为四方向精灵';
const LOGIC = `    ${MARKER}
    // The Site has no /assets route: only flat outputs/*.png names (already rewritten to raw main by normalizeLinks) get an image.
    // Status comes from staticBaselinesAndPilots (matched by capture file) or characterVisualReview.artAccepted, never from caption text.
    const visualReview=state.bible.characterVisualReview||{};
    const previewSha=/^[a-f0-9]{40}$/.test(state.sourceSha)?state.sourceSha:'main';
    const previewRaw='https://raw.githubusercontent.com/ConsAccompany/Worlds-Between/'+previewSha+'/outputs/';
    const outputName=file=>{if(typeof file!=='string')return '';const prefix=[RAW,'/assets/','outputs/'].find(x=>file.startsWith(x));if(!prefix)return '';let name;try{name=decodeURIComponent(file.slice(prefix.length));}catch{return '';}return /^[A-Za-z0-9][A-Za-z0-9._-]{0,250}\\.png$/.test(name)?name:'';};
    const pilots=Object.values(visualReview.staticBaselinesAndPilots||{}).filter(r=>r&&typeof r==='object'&&Array.isArray(r.captures));
    const previewStatus=name=>{const pilot=name&&pilots.find(r=>r.captures.some(c=>outputName(c)===name));if(pilot){const ok=pilot.creatorApproved===true,live=pilot.runtimeIntegrated===true;return [(ok?'已批准静态基准':'未批准')+' · '+(live?'已接入运行时':'未接入运行时')+' / '+(ok?'Approved static baseline':'Unapproved')+' · '+(live?'runtime':'nonruntime'),ok?'good':'warn'];}return visualReview.artAccepted===true?['审查截图 / Review capture','']:['审查截图 · 未验收 / Review capture · not accepted','warn'];};
    const cityName=outputName(citySample?.file);
    const previewList=(Array.isArray(visualReview.previews)?visualReview.previews:[]).filter(p=>p&&typeof p.file==='string'&&!(cityName&&outputName(p.file)===cityName));
    const previewFigures=previewList.map(p=>{const name=outputName(p.file),src=name?previewRaw+encodeURIComponent(name):'';const [label,kind]=previewStatus(name);return \`<figure class="visual-sample character-preview" data-preview="\${esc(name||p.file)}">\${src?\`<a href="\${esc(src)}" target="_blank" rel="noopener"><img src="\${esc(src)}" alt="\${esc((p.label||'角色')+' · 角色画质审查截图')}" loading="lazy"></a>\`:'<div class="empty small">图片路径无法解析，未显示 / Image path not resolvable</div>'}<figcaption><span class="preview-head"><strong>\${esc(p.label||'未命名 / Untitled')}</strong>\${badge(label,kind)}</span>\${esc(p.caption||'')}</figcaption></figure>\`;}).join('');
    const previewGrid=previewFigures?\`<div class="visual-previews" id="character-visual-previews"><p class="small preview-intro"><strong>角色画质审查截图 / Character preview captures（\${previewList.length}）</strong> <span class="muted">图片来自 GitHub 提交 \${esc(previewSha.slice(0,7))} 的 outputs/；状态标签读取自项目状态，均不改变上方验收数。</span></p>\${previewFigures}</div>\`:'';
`;
const CSS = `${CSS_MARKER}
.visual-previews{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin:14px 0}.visual-previews .preview-intro{grid-column:1/-1;margin:0}.visual-previews .visual-sample{margin:0}.visual-previews figcaption{font-size:13px;line-height:1.55;color:var(--text)}.visual-previews .preview-head{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-bottom:4px}.visual-previews .badge{white-space:normal}
`;

function once(text, needle, what) {
  const first = text.indexOf(needle);
  if (first < 0 || text.indexOf(needle, first + 1) >= 0) throw new Error(`expected exactly one ${what} in bible.js`);
  return first;
}

function patchSiteBibleJs(text) {
  if (text.includes(MARKER)) return {changed: false, text, reason: 'already patched'};
  if (/characterVisualReview\?*\.previews/.test(text)) throw new Error('bible.js already reads previews some other way; patch by hand');
  const logicAt = once(text, LOGIC_ANCHOR, 'Production template (content.innerHTML=`${head(\'制作路线\'…)');
  const start = text.lastIndexOf('function renderProduction()', logicAt);
  const next = start < 0 ? -1 : text.indexOf('\n  function ', start + 1);
  if (start < 0 || (next >= 0 && next < logicAt)) throw new Error('Production template is not inside renderProduction');
  if (!text.slice(start, logicAt).includes('const citySample=')) throw new Error('renderProduction no longer defines citySample');
  if (!/const RAW='https:\/\/raw\.githubusercontent\.com\/ConsAccompany\/Worlds-Between\/main\/outputs\/'/.test(text)) throw new Error('bible.js no longer defines the RAW outputs prefix');
  if (!/const badge = /.test(text) || !/const esc = /.test(text)) throw new Error('bible.js no longer defines esc/badge');
  const templateAt = once(text, TEMPLATE_ANCHOR, 'static-candidate note after the city sample');
  if (templateAt < logicAt || templateAt > text.indexOf('`;', logicAt)) throw new Error('static-candidate note is not in the Production template');
  const eol = text.includes('\r\n') ? '\r\n' : '\n';
  const out = text.slice(0, logicAt) + LOGIC.replace(/\n/g, eol) + text.slice(logicAt, templateAt) + '${previewGrid}' + text.slice(templateAt);
  return {changed: true, text: out, reason: 'inserted preview figures with pinned GitHub raw images'};
}

function patchSiteBibleCss(text) {
  if (text.includes(CSS_MARKER)) return {changed: false, text, reason: 'already patched'};
  if (!/\.visual-sample\{/.test(text)) throw new Error('bible.css has no .visual-sample rule; patch by hand');
  const eol = text.includes('\r\n') ? '\r\n' : '\n';
  const base = text.endsWith('\n') ? text : text + eol;
  return {changed: true, text: base + CSS.replace(/\n/g, eol), reason: 'appended preview grid styles'};
}

module.exports = {patchSiteBibleJs, patchSiteBibleCss, MARKER, CSS_MARKER};

if (require.main === module) {
  const [dir, flag] = process.argv.slice(2);
  if (!dir || (flag && flag !== '--write')) {
    console.error('usage: node <this file> <site-source-dir> [--write]');
    process.exit(2);
  }
  for (const [name, patch] of [['bible.js', patchSiteBibleJs], ['bible.css', patchSiteBibleCss]]) {
    const file = path.join(dir, 'public', name);
    const result = patch(fs.readFileSync(file, 'utf8'));
    if (result.changed && flag === '--write') fs.writeFileSync(file, result.text);
    console.log(`SITE_PREVIEW_PATCH ${result.changed ? (flag === '--write' ? 'WRITTEN' : 'WOULD_CHANGE') : 'NO_CHANGE'} ${file} (${result.reason})`);
  }
}
