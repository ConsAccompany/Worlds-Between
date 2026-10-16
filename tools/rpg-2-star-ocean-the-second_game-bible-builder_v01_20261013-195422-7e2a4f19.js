// Game Bible state builder.
// Characters (51 identities), the approved 20-series job roster and the superseded 7-node / 5-node skill drafts are derived
// from the source files in outputs/. The v01 design brief predates the creator decisions of 2026-10-15 (five Earth
// civilization spheres plus a separate portal planet, NYC / Catskills / 2537-05-25, 10-node skill rules), so the brief only
// supplies chapter ids and titles: the reconciled chapter bodies, open questions, review blocks and creatorDecisions are carried
// forward from the tracked state and every build is checked against that canon. The builder refuses to write rather than
// regenerate superseded brief text, old board labels as new geography, or approved 10-node trees that nobody has written.
// Run from the repository root:
//   node tools/<this file>          rebuild and write the tracked state
//   node tools/<this file> --check  rebuild in memory and compare with the tracked state; writes nothing
const fs = require('node:fs');
const path = require('node:path');
const util = require('node:util');

const root = path.resolve(__dirname, '..');
const out = path.join(root, 'outputs');
const names = {
  brief: 'rpg-2-star-ocean-the-second_game-design-brief_v01_20261012-233611-7c2e1f4a.md',
  core: 'rpg-2-star-ocean-the-second_core-cast_character-bible_v01_20261012-234158-cc7e91a4.md',
  extra: 'rpg-2-star-ocean-the-second_remaining-companions_character-bible_v01_20261013-181920-6d2a4f8c.md',
  mvp: 'rpg-2-star-ocean-the-second_mvp-implementation-plan_visual-first_v02_20261013-230524-29cf8a61.md',
  jobs: 'rpg-2-star-ocean-the-second_all-jobs_five-tier-proposal_v01_20261013-224236-6f2b9c11.json',
  skillTrees: 'rpg-2-star-ocean-the-second_four-job-trees_skill-node-proposal_v01_20261013-224554-5a72d0be.json',
  martialTrees: 'rpg-2-star-ocean-the-second_martial-job-trees_skill-node-proposal_v01_20261013-224832-1c9e73ab.json',
  adaptiveTrees: 'rpg-2-star-ocean-the-second_adaptive-job-trees_skill-node-proposal_v01_20261013-225032-9b7e26c4.json',
  scholarlyTrees: 'rpg-2-star-ocean-the-second_scholarly-job-trees_skill-node-proposal_v01_20261013-225251-3e6a19d8.json',
  spiritualTrees: 'rpg-2-star-ocean-the-second_spiritual-job-trees_skill-node-proposal_v01_20261013-225530-b2e8f4a1.json',
  personalTrees: 'rpg-2-star-ocean-the-second_core-cast_personal-skill-trees-proposal_v01_20261013-230015-4ce1a8d2.json',
  inventory: 'rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json',
};
const dest = path.join(out, 'rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json');
const builderFile = 'tools/' + path.basename(__filename);
const decisionNote = 'docs/design/rpg-2-star-ocean-the-second_creator-decisions-2026-10-15_world-skills-ai-endgame_reconciliation-note_v01_20261015-174559-39efc292.md';
// Sections that cannot be derived from the proposal sources. They are carried from the tracked state; openQuestions keeps its
// slot before sources and the rest follow in this order. Any other key found in the tracked state is carried after them.
const curatedKeys = ['openQuestions', 'citySampleReview', 'characterVisualReview', 'environmentVisualReview', 'creatorDecisions'];
const sphereIds = ['science', 'magic', 'wuxia', 'nature', 'culture'];
// Character data still stores the pre-decision board labels (奇幻 = Culture, 星外 = final planet); the UI maps them. Wuxia has
// no companions yet, so the builder must not invent a sphere assignment.
const legacyBoardCounts = {'地下社区': 1, '科技': 11, '自然': 11, '奇幻': 11, '魔法': 10, '星外': 7};
const careerRules = {tiers: 5, nodesPerSeries: 10, nodesUnlockedPerTier: 2, unlock: '进入该阶时立即开放', rankMaximum: 5, rankUpgrade: 'JP', branches: '所有分支最终都可学会'};
const personalRules = {identities: 51, nodesPerIdentity: 10, allUnlockedByPersonalLevel: 100, exclusiveSkillOnJoin: '加入时立即拥有至少一项专属个人技能', rankMaximum: 5, rankUpgrade: 'JP', usableInAnyJob: true};
const careerNodesRequired = 20 * careerRules.nodesPerSeries;
const personalNodesRequired = personalRules.identities * personalRules.nodesPerIdentity;

const need = (ok, message) => { if (!ok) throw new Error(message); };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const read = key => fs.readFileSync(path.join(out, names[key]), 'utf8').replace(/\r\n/g, '\n');
const readState = () => JSON.parse(fs.readFileSync(dest, 'utf8'));
const serialize = bible => JSON.stringify(bible, null, 2) + '\n';
const slug = text => text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

const chapterSummaries = {
  '1': '核心定位、平台、视角与视觉原则。',
  '2': '历史、五个地球文明圈与终局星球、幕后势力与结局结构。',
  '3': '探索、横向即时战斗、恢复与存档规则。',
  '4': '等级、四项天分、20 条职业系列与 JP。',
  '5': '50 位伙伴、招募、关系与组合技。',
  '6': '装备、考古、贸易、商会与日历。',
  '7': '通关后的持续探索与二周目继承。',
  '8': '从设计工具到终局内容的实施顺序。',
  '9': '原始设计稿中仍需细化的内容。',
};

function build({base = readState(), updatedAt = new Date().toISOString()} = {}) {
  need(base && base.creatorDecisions && base.creatorDecisions.note === decisionNote && Array.isArray(base.chapters),
    'Refusing to build: the tracked state lacks the 2026-10-15 creatorDecisions and reconciled chapters. The v01 design brief is superseded and would revert the canon.');
  for (const key of curatedKeys) need(base[key] !== undefined, 'Refusing to build: tracked state lacks curated section ' + key);

  const brief = read('brief');
  const core = read('core');
  const extra = read('extra');
  const inventory = JSON.parse(read('inventory'));
  const jobs = JSON.parse(read('jobs'));
  const skillTrees = JSON.parse(read('skillTrees'));
  const martialTrees = JSON.parse(read('martialTrees'));
  const adaptiveTrees = JSON.parse(read('adaptiveTrees'));
  const scholarlyTrees = JSON.parse(read('scholarlyTrees'));
  const spiritualTrees = JSON.parse(read('spiritualTrees'));
  const personalSource = JSON.parse(read('personalTrees'));
  if (jobs.series?.length !== 20 || !['武艺','应变','研学','灵觉'].every(aptitude => jobs.series.filter(series => series.aptitude === aptitude).length === 5) || jobs.series.some(series => series.stages?.length !== 5 || !series.finalQuest)) {
    throw new Error('Job proposal must contain four aptitudes with five complete series each');
  }
  // The career drafts are validated as what they are: twenty superseded seven-node trees (rank max 3), kept for reference.
  const draftTrees = [...skillTrees.trees, ...martialTrees.trees, ...adaptiveTrees.trees, ...scholarlyTrees.trees, ...spiritualTrees.trees];
  if (draftTrees.length !== 20 || new Set(draftTrees.map(tree => tree.seriesId)).size !== 20 || draftTrees.some(tree => !jobs.series.some(series => series.id === tree.seriesId) || tree.nodes?.length !== 7 || [1,2,3,4,5].some(tier => tree.nodes.filter(node => node.tier === tier).length !== ([1,3,5].includes(tier) ? 1 : 2))) || new Set(draftTrees.flatMap(tree => tree.nodes.map(node => node.id))).size !== 140) {
    throw new Error('Superseded skill-tree draft must still contain twenty seven-node series');
  }
  const portraits = new Map(inventory.categories[0].subcategories[0].items.map(item => [item.id.slice(9), item]));

  const baseChapters = new Map(base.chapters.map(chapter => [chapter.id, chapter]));
  const chapters = brief.split(/^## /m).slice(1).map(chunk => {
    const newline = chunk.indexOf('\n');
    const rawTitle = chunk.slice(0, newline).trim();
    const id = rawTitle.match(/^(\d+)\./)?.[1];
    const title = rawTitle.replace(/^\d+\.\s*/, '');
    const reconciled = baseChapters.get('chapter-' + id);
    need(reconciled && reconciled.title === title && reconciled.body, 'Missing reconciled body for chapter ' + id + ' (' + title + ') in the tracked state');
    return {
      id: 'chapter-' + id,
      number: Number(id),
      title,
      summary: chapterSummaries[id] || '',
      body: reconciled.body,
      source: 'brief',
      status: id === '8' ? '建议' : id === '9' ? '待细化' : '需求基线',
    };
  });

  const characters = [];
  function addCharacter({number,cn,en,group,board,body,source}) {
    const portrait = portraits.get(slug(en));
    if (!portrait) throw new Error('Missing portrait inventory entry for ' + en);
    characters.push({
      id: 'character-' + String(number).padStart(2, '0'),
      number, cn, en, group, board, body: body.trim(), source,
      portrait: portrait.file, portraitStage: portrait.stage,
      portraitAccepted: Boolean(portrait.checked), status: '人物提案',
    });
  }
  const heroMatch = core.match(/^## 主角\n([\s\S]*?)(?=^## )/m);
  if (!heroMatch) throw new Error('Missing hero profile');
  characters.push({
    id:'hero', number:0, cn:'主角（玩家命名）', en:'Protagonist', group:'主角',
    board:'地下社区', body:heroMatch[1].trim(), source:'core',
    portraits:[
      portraits.get('protagonist-male')?.file,
      portraits.get('protagonist-female')?.file,
    ].filter(Boolean),
    status:'人物提案',
  });

  let coreBoard = '';
  const coreLines = core.split('\n');
  for (let i=0; i<coreLines.length; i++) {
    const boardLine = coreLines[i].match(/^## (科技|自然|奇幻|魔法|星外)板块/);
    if (boardLine) coreBoard = boardLine[1];
    const match = coreLines[i].match(/^### (\d{2}) (.+?) \/ (.+)$/);
    if (!match) continue;
    let end=i+1;
    while (end<coreLines.length && !/^#{2,3} /.test(coreLines[end])) end++;
    addCharacter({number:Number(match[1]),cn:match[2],en:match[3],group:'主线伙伴',board:coreBoard,body:coreLines.slice(i+1,end).join('\n'),source:'core'});
  }
  let extraGroup = '';
  let extraBoard = '';
  const extraLines = extra.split('\n');
  for (let i=0; i<extraLines.length; i++) {
    if (/^## 支线伙伴/.test(extraLines[i])) extraGroup='支线伙伴';
    if (/^## 情境招募伙伴/.test(extraLines[i])) extraGroup='情境招募伙伴';
    const boardLine = extraLines[i].match(/^### (科技|自然|奇幻|魔法|星外)板块/);
    if (boardLine) extraBoard=boardLine[1];
    const match = extraLines[i].match(/^\*\*(\d{2}) (.+?) \/ ([^｜]+)｜(.+)\*\*$/);
    if (!match) continue;
    let end=i+1;
    while(end<extraLines.length && !/^\*\*\d{2} /.test(extraLines[end]) && !/^## /.test(extraLines[end]) && !/^### /.test(extraLines[end])) end++;
    addCharacter({number:Number(match[1]),cn:match[2],en:match[3],group:extraGroup,board:extraBoard,body:extraLines.slice(i,end).join('\n'),source:'extra'});
  }
  characters.sort((a,b)=>a.number-b.number);
  if (chapters.length!==9 || characters.length!==51 || characters.at(-1).number!==50) {
    throw new Error('Unexpected bible count: '+chapters.length+' chapters, '+characters.length+' characters');
  }
  const coreCharacters = characters.filter(character => character.group === '主角' || character.group === '主线伙伴');
  const personalNodes = personalSource.trees.flatMap(tree => tree.nodes);
  // The personal drafts are validated as sixteen superseded five-node trees (hero + fifteen core companions, rank max 3).
  if (coreCharacters.length !== 16 || personalSource.trees.length !== 16 || new Set(personalSource.trees.map(tree => tree.characterId)).size !== 16 ||
      personalNodes.length !== 80 || new Set(personalNodes.map(node => node.id)).size !== 80 ||
      personalSource.trees.some(tree => {
        const character = coreCharacters.find(entry => entry.id === tree.characterId);
        return !character || !character.body.includes(tree.skill) || tree.nodes?.length !== 5 ||
          [1,10,20,30,40].some((level,index) => tree.nodes[index]?.level !== level) ||
          tree.nodes[0].name !== tree.skill || tree.nodes.some(node => !node.name || !node.effect ||
            (node.level === 1 && !Array.isArray(node.tags)) || (node.mode === '主动' ? node.energy <= 0 : node.energy !== 0));
      })) {
    throw new Error('Superseded personal skill draft must match the hero and fifteen core companion profiles');
  }

  // Creator decisions 2026-10-15: roster, stage names and final quests approved verbatim; the drafts are superseded.
  const jobProposal = {
    ...jobs,
    status: '系列名单、五阶名称与终阶任务已获创作者批准（2026-10-15，原文不改）；设计边界条目与定位描述仍为提案',
    approvedAt: '2026-10-15',
    approvalScope: '20 个系列名单；每个系列 stages 中的五阶名称与 finalQuest 原文。role（定位）与 rules 未单独确认。',
  };
  const skillTreeProposal = {
    ...skillTrees,
    status: '已被取代的草案（2026-10-15）：7 节点、3 级上限不是已批准的 10 节点设计，待重新设计',
    designNotes: [...scholarlyTrees.rules, ...spiritualTrees.rules],
    trees: draftTrees,
    superseded: true,
    pendingRedesign: true,
    approvedRules: careerRules,
    redesignNodesRequired: careerNodesRequired,
  };
  const personalSkillTrees = {
    ...personalSource,
    status: '已被取代的草案（2026-10-15）：5 节点、3 级上限不是已批准的 10 节点设计，待重新设计',
    superseded: true,
    pendingRedesign: true,
    approvedRules: personalRules,
    redesignNodesRequired: personalNodesRequired,
  };

  const sources = Object.entries(names).filter(([key])=>!['inventory','jobs','skillTrees','martialTrees','adaptiveTrees','scholarlyTrees','spiritualTrees','personalTrees'].includes(key)).map(([id,filename])=>({id,filename,url:'/source/'+id}));
  const bible = {
    schemaVersion:1,
    project:'rpg-2-star-ocean-the-second',
    title:'世界之间',
    englishTitle:'Worlds Between',
    edition:'设计基线 v0.2 · 2026-10-15 创作者决定',
    updatedAt,
    note:'规则以玩家确认的设计稿为基线，并已并入 2026-10-15 创作者决定；人物姓名与外观是待审提案，具体剧情留待后续设计。',
    pitch:'从地下社区走出的旅人，以好奇心探索多元文明，招募伙伴，并成为不同世界认知差异的桥梁。',
    pillars:['自由探索','招募与陪伴','横向即时战斗','无等级上限的职业成长'],
    facts:[
      {label:'平台',value:'PC · 单人 · 中英双语'},
      {label:'画面',value:'2D 像素 · 俯视探索 / 横向战斗'},
      {label:'世界',value:'5 个地球文明圈 · 终局星球经传送门'},
      {label:'同伴',value:'50 位 · 最多 5 人上场'},
      {label:'职业',value:'20 系列 × 5 阶 · 名称已批准'},
    ],
    chapters, characters, jobProposal, skillTreeProposal, personalSkillTrees,
    openQuestions: base.openQuestions,
    sources,
    canonBasis: {
      decisionNote,
      builder: builderFile,
      brief: 'outputs/' + names.brief,
      briefStatus: '原设计稿 v01 早于 2026-10-15 创作者决定；与决定冲突的表述（五个板块、星外为第五板块、四条地球主线、7 节点／5 节点技能树、首城待定）已被取代。构建器只从中取章节编号与标题，已核对的章节正文、待定问题、评审记录与 creatorDecisions 从本文件沿用并逐项校验。',
      characterBoards: '人物数据仍存旧板块标签：奇幻即文化文明圈，星外即终局星球；武侠文明圈暂无伙伴，未作新的文明圈分配。',
      skillNodes: {
        approvedRequired: careerNodesRequired + personalNodesRequired,
        approvedCareerRequired: careerNodesRequired,
        approvedPersonalRequired: personalNodesRequired,
        approvedAuthored: 0,
        supersededDraftCareerNodes: draftTrees.reduce((sum, tree) => sum + tree.nodes.length, 0),
        supersededDraftPersonalNodes: personalNodes.length,
      },
    },
  };
  for (const key of curatedKeys.slice(1)) bible[key] = base[key];
  for (const [key, value] of Object.entries(base)) if (!(key in bible)) bible[key] = value;
  checkCanon(bible);
  return bible;
}

// Canon checks shared by the builder and its test. Returns the check labels; throws on the first failure.
function checkCanon(bible) {
  const passed = [];
  const check = (ok, label) => { need(ok, 'Canon check failed: ' + label); passed.push(label); };
  const chapter = number => bible.chapters.find(entry => entry.number === number)?.body || '';
  const has = (text, parts) => parts.every(part => text.includes(part));
  const hasNone = (text, parts) => parts.every(part => !text.includes(part));

  check(same(bible.chapters.map(entry => entry.id), [1,2,3,4,5,6,7,8,9].map(n => 'chapter-' + n)), 'nine chapters');
  check(bible.characters.length === 51 && bible.characters[0].id === 'hero' && same(bible.characters.slice(1).map(entry => entry.number), Array.from({length: 50}, (_, i) => i + 1)), '51 identities: hero plus companions 1-50');
  const boards = {};
  for (const entry of bible.characters) boards[entry.board] = (boards[entry.board] || 0) + 1;
  check(same(Object.keys(legacyBoardCounts).map(key => boards[key] || 0), Object.values(legacyBoardCounts)) && Object.keys(boards).length === Object.keys(legacyBoardCounts).length, 'character board labels unchanged (legacy labels, no reassignment)');
  check(bible.characters.every(entry => !('sphere' in entry) && !('sphereId' in entry) && !('region' in entry)), 'no character carries an invented sphere assignment');

  check(bible.facts.find(fact => fact.label === '世界')?.value === '5 个地球文明圈 · 终局星球经传送门' && bible.facts.every(fact => !fact.value.includes('板块')), 'world fact: five Earth spheres plus portal planet');
  const decisions = bible.creatorDecisions;
  check(decisions && decisions.note === decisionNote && same(decisions.spheres.map(sphere => sphere.id), sphereIds), 'creator decisions: five Earth spheres in canon order');
  const hubs = Object.fromEntries(decisions.spheres.map(sphere => [sphere.id, sphere.hubs]));
  const regions = Object.fromEntries(decisions.spheres.map(sphere => [sphere.id, sphere.region]));
  check(same(hubs.science, ['纽约']) && hubs.magic[0].startsWith('马瑙斯') && same(hubs.wuxia, ['重庆']) && hubs.nature[0].startsWith('布里斯班') && same(hubs.culture, ['雅典', '开罗']), 'sphere hubs: NYC, Manaus, Chongqing, Brisbane, Athens + Cairo');
  check(same([regions.science, regions.magic, regions.wuxia, regions.nature, regions.culture], ['美国 + 加拿大', '南美洲', '亚洲', '大洋洲', '欧洲 + 非洲']), 'sphere regions');
  check(has(decisions.finalPlanet, ['传送门', '不属于五个文明圈']) && !decisions.spheres.some(sphere => /终局|星外|offworld/.test(sphere.id + sphere.zh)), 'final planet is separate from the five spheres');
  const geo = decisions.geography;
  check(geo.adventureStart === '2537-05-25' && geo.undergroundCommunity.includes('卡茨基尔山') && geo.scienceHub.includes('纽约') && geo.firstPlayableArea.includes('市政厅公园') && geo.outskirts.includes('扬克斯') && geo.firstAirRoute.includes('芝加哥') && geo.liangzhu.includes('不属于 MVP'), 'geography: NYC, City Hall Park, Yonkers, Catskills, 2537-05-25, NYC-Chicago');
  check(has(decisions.counters, ['0/52', '0/11', '0/2', '未改变']), 'creator decisions leave the counters unchanged');

  check(has(chapter(2), ['五个地球文明圈与终局星球', '卡茨基尔山', '2537-05-25', '传送门', '五条地球主线', 'Wuxia', 'Culture', '纽约']) &&
    hasNone(chapter(2), ['### 五个板块', '四条地球主线完成后', '| Exterritorial／星外 |', '待科技区首城确定后登记']), 'world chapter carries the new canon, not the v01 brief board table');
  check(has(chapter(4), ['每条职业系列 10 个节点', '现有 7 节点职业树提案已被取代']), 'jobs chapter: 10-node rule, 7-node draft superseded');
  check(has(chapter(5), ['10 个个人节点', '现有 5 节点个人树提案已被取代']), 'companions chapter: 10 personal nodes, 5-node draft superseded');
  check(has(chapter(9), ['共 200 个', '共 510 个']), 'open design list names the 200 + 510 unwritten nodes');

  const jobsBlock = bible.jobProposal;
  check(jobsBlock.series.length === 20 && jobsBlock.series.every(series => series.stages.length === 5 && series.finalQuest) && jobsBlock.status.includes('已获创作者批准') && jobsBlock.approvedAt === '2026-10-15', 'job roster: 20 series x 5 stages approved');
  const career = bible.skillTreeProposal;
  check(career.superseded === true && career.pendingRedesign === true && career.status.startsWith('已被取代的草案') && same(career.approvedRules, careerRules) && career.redesignNodesRequired === careerNodesRequired, 'career trees: 7-node draft labelled superseded, approved 10-node rule attached');
  check(career.trees.length === 20 && career.trees.every(tree => tree.nodes.length === 7), 'career draft kept as written (no node presented as an approved 10-node design)');
  const personal = bible.personalSkillTrees;
  check(personal.superseded === true && personal.pendingRedesign === true && personal.status.startsWith('已被取代的草案') && same(personal.approvedRules, personalRules) && personal.redesignNodesRequired === personalNodesRequired, 'personal trees: 5-node draft labelled superseded, approved 10-node rule attached');
  check(personal.trees.length === 16 && personal.trees.every(tree => tree.nodes.length === 5), 'personal draft kept as written');
  const nodes = bible.canonBasis?.skillNodes;
  check(nodes && nodes.approvedRequired === 710 && nodes.approvedCareerRequired + nodes.approvedPersonalRequired === 710 && nodes.approvedAuthored === 0 && nodes.supersededDraftCareerNodes === 140 && nodes.supersededDraftPersonalNodes === 80, 'skill nodes: 0 of 710 approved nodes authored; 140 + 80 superseded draft nodes');

  check(bible.openQuestions.some(question => question.title.includes('待按新规则重设计')) && !bible.openQuestions.some(question => /地理锚点|首城|开始年份/.test(question.title)), 'open questions: skill redesign open, resolved geography questions gone');
  check(bible.environmentVisualReview.sceneQualityAccepted === 0 && bible.environmentVisualReview.sceneQualityTarget === 11 && bible.environmentVisualReview.artAccepted === false, 'scene visuals 0/11, art not accepted');
  check(bible.characterVisualReview.runtimeSpritesAccepted === 0 && bible.characterVisualReview.artAccepted === false, 'runtime sprites accepted 0');
  // Washington, D.C.: unapproved Pixelorama candidates exist (walkable v01-v06, separate cinematic v01-v02); none is wired or accepted.
  const dc = bible.environmentVisualReview.washingtonDC;
  const dcCandidates = dc?.unapprovedCandidates;
  const artRoute = bible.openQuestions.find(question => question.title === 'MVP 美术技术路线')?.detail || '';
  check(dcCandidates && same(dcCandidates.walkable, ['v01', 'v02', 'v03', 'v04', 'v05', 'v06']) && same(dcCandidates.cinematic, ['v01', 'v02']) &&
    dcCandidates.runtimeIntegrated === false && dcCandidates.artAccepted === false && dc.runtimeIntegrated === false && dc.artAccepted === false &&
    dc.highPrecisionPixelSceneAuthored === false && has(dcCandidates.status, ['v01–v06', 'v01–v02']) && !dcCandidates.status.includes('v01–v05') &&
    has(artRoute, ['未批准候选', 'v01–v06', 'v01–v02', '未接入运行时、未验收']) && !artRoute.includes('v01–v05') && !artRoute.includes('尚未制作'), 'Washington Pixelorama: unapproved walkable v01-v06 and cinematic v01-v02 candidates, none in the runtime or accepted');
  // v06 (run 18b9cea3): technical 47/47 after the integration erratum (the QA note's 48/48 was a miscount); no scene approval.
  const v06 = dcCandidates?.latestWalkable;
  check(v06 && v06.version === 'v06' && v06.runId === '18b9cea3' && v06.status === 'UNAPPROVED / NONRUNTIME' && v06.technicalGates === '47/47' &&
    v06.runtimeIntegrated === false && v06.artAccepted === false && v06.sceneApproved === false && has(v06.technicalGatesNote, ['47/47', '48/48', '不是画面验收']) &&
    has(artRoute, ['v06', '47/47', '不是场景验收']) && [v06.qa, v06.codexVisualAudit].every(file => file && dcCandidates.evidence.includes(file) && fs.existsSync(path.join(root, file))) &&
    /_walkable-scale-depth_qa-note_unapproved-v06_20261016-071733-18b9cea3\.md$/.test(v06.qa) && /_walkable-v06-codex-visual-audit_unapproved-v01_20261016-134646-35af3a0d\.md$/.test(v06.codexVisualAudit),
    'Washington walkable v06: UNAPPROVED / NONRUNTIME, technical 47/47 after erratum, QA note and Codex audit linked, no scene approval');
  // M2 door-to-door route figures: research draft (m2-v08) and audit supplement (m2-v08a) are cited only; nothing is implemented.
  const routeEvidence = bible.environmentVisualReview.runtimeGeographyMap?.routeFigureEvidence;
  check(routeEvidence && routeEvidence.status === 'research-only' && routeEvidence.doorToDoorImplemented === false && routeEvidence.evidence.length === 2 &&
    routeEvidence.evidence.every(file => fs.existsSync(path.join(root, file))) && has(routeEvidence.zh, ['尚未写入运行时', '9/12']) && has(routeEvidence.en, ['nothing is implemented', '9/12']),
    'M2 route-figure evidence cited as research only: door-to-door not implemented, M2 stays 9/12');
  return passed;
}

function main(argv) {
  const base = readState();
  const file = path.relative(root, dest);
  if (argv.includes('--check')) {
    const built = build({base, updatedAt: base.updatedAt});
    const contentEqual = util.isDeepStrictEqual(built, base);
    const bytesEqual = serialize(built) === fs.readFileSync(dest, 'utf8').replace(/\r\n/g, '\n');
    console.log(JSON.stringify({mode: 'check', file, contentEqual, bytesEqual, canonChecks: checkCanon(built).length}));
    if (!contentEqual) process.exitCode = 1;
    return;
  }
  const bible = build({base});
  fs.writeFileSync(dest, serialize(bible), 'utf8');
  console.log(JSON.stringify({file, chapters: bible.chapters.length, characters: bible.characters.length, sources: bible.sources.length, canonChecks: checkCanon(bible).length}));
}

module.exports = {build, checkCanon, serialize, readState, dest, names, decisionNote, careerRules, personalRules};
if (require.main === module) main(process.argv.slice(2));
