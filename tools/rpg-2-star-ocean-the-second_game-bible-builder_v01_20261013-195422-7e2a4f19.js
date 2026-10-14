const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const out = path.join(root, 'outputs');
const names = {
  brief: 'rpg-2-star-ocean-the-second_game-design-brief_v01_20261012-233611-7c2e1f4a.md',
  core: 'rpg-2-star-ocean-the-second_core-cast_character-bible_v01_20261012-234158-cc7e91a4.md',
  extra: 'rpg-2-star-ocean-the-second_remaining-companions_character-bible_v01_20261013-181920-6d2a4f8c.md',
  mvp: 'rpg-2-star-ocean-the-second_mvp-implementation-plan_v01_20261013-183550-0f7c4d21.md',
  jobs: 'rpg-2-star-ocean-the-second_all-jobs_five-tier-proposal_v01_20261013-224236-6f2b9c11.json',
  skillTrees: 'rpg-2-star-ocean-the-second_four-job-trees_skill-node-proposal_v01_20261013-224554-5a72d0be.json',
  martialTrees: 'rpg-2-star-ocean-the-second_martial-job-trees_skill-node-proposal_v01_20261013-224832-1c9e73ab.json',
  inventory: 'rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json',
};
const dest = path.join(out, 'rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json');
const read = key => fs.readFileSync(path.join(out, names[key]), 'utf8').replace(/\r\n/g, '\n');
const brief = read('brief');
const core = read('core');
const extra = read('extra');
const inventory = JSON.parse(read('inventory'));
const jobs = JSON.parse(read('jobs'));
const skillTrees = JSON.parse(read('skillTrees'));
const martialTrees = JSON.parse(read('martialTrees'));
const skillTreeProposal = {...skillTrees, trees:[...skillTrees.trees, ...martialTrees.trees]};
if (jobs.series?.length !== 20 || !['武艺','应变','研学','灵觉'].every(aptitude => jobs.series.filter(series => series.aptitude === aptitude).length === 5) || jobs.series.some(series => series.stages?.length !== 5 || !series.finalQuest)) {
  throw new Error('Job proposal must contain four aptitudes with five complete series each');
}
if (skillTreeProposal.trees.length !== 8 || new Set(skillTreeProposal.trees.map(tree => tree.seriesId)).size !== 8 || skillTreeProposal.trees.some(tree => !jobs.series.some(series => series.id === tree.seriesId) || tree.nodes?.length !== 7 || [1,2,3,4,5].some(tier => tree.nodes.filter(node => node.tier === tier).length !== ([1,3,5].includes(tier) ? 1 : 2))) || new Set(skillTreeProposal.trees.flatMap(tree => tree.nodes.map(node => node.id))).size !== 56) {
  throw new Error('Skill tree proposal must contain eight complete seven-node series');
}
const portraits = new Map(inventory.categories[0].subcategories[0].items.map(item => [item.id.slice(9), item]));
const slug = text => text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

const chapterSummaries = {
  '1': '核心定位、平台、视角与视觉原则。',
  '2': '历史、五个板块、幕后势力与结局结构。',
  '3': '探索、横向即时战斗、恢复与存档规则。',
  '4': '等级、四项天分、20 条职业系列与 JP。',
  '5': '50 位伙伴、招募、关系与组合技。',
  '6': '装备、考古、贸易、商会与日历。',
  '7': '通关后的持续探索与二周目继承。',
  '8': '从设计工具到终局内容的实施顺序。',
  '9': '原始设计稿中仍需细化的内容。',
};
const chapters = brief.split(/^## /m).slice(1).map(chunk => {
  const newline = chunk.indexOf('\n');
  const rawTitle = chunk.slice(0, newline).trim();
  const id = rawTitle.match(/^(\d+)\./)?.[1];
  return {
    id: 'chapter-' + id,
    number: Number(id),
    title: rawTitle.replace(/^\d+\.\s*/, ''),
    summary: chapterSummaries[id] || '',
    body: chunk.slice(newline + 1).trim(),
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

const openQuestions = [
  {title:'10 位可恋爱伙伴',detail:'人选与开放阶段尚未确定；不要从角色画像推断恋爱资格。'},
  {title:'职业技能与数值',detail:'20 个系列的五阶名称及终阶任务已有待确认提案；八条系列已有七节点技能树样板，其余十二条与实际平衡数值仍需设计。'},
  {title:'地点与任务内容',detail:'五个板块的城市、社区、野外地点和独立主线任务尚需逐项命名与编写。'},
  {title:'数值与经营平衡',detail:'JP 折扣、敌人数值、终局难度奖励、商会利润与日历结算需试玩后定稿。'},
  {title:'组合技与 AI 细则',detail:'关系及技能标签的组合规则、AI 条件冲突与自动战斗优先级需细化。'},
];
const sources = Object.entries(names).filter(([key])=>!['inventory','jobs','skillTrees','martialTrees'].includes(key)).map(([id,filename])=>({id,filename,url:'/source/'+id}));
const bible = {
  schemaVersion:1,
  project:'rpg-2-star-ocean-the-second',
  title:'世界之间',
  englishTitle:'Worlds Between',
  edition:'设计基线 v0.1',
  updatedAt:new Date().toISOString(),
  note:'规则以玩家确认的设计稿为基线；人物姓名与外观是待审提案，具体剧情留待后续设计。',
  pitch:'从地下社区走出的旅人，以好奇心探索多元文明，招募伙伴，并成为不同世界认知差异的桥梁。',
  pillars:['自由探索','招募与陪伴','横向即时战斗','无等级上限的职业成长'],
  facts:[
    {label:'平台',value:'PC · 单人 · 中英双语'},
    {label:'画面',value:'2D 像素 · 俯视探索 / 横向战斗'},
    {label:'世界',value:'5 个板块 · 地球与传送门另一端'},
    {label:'同伴',value:'50 位 · 最多 5 人上场'},
    {label:'职业',value:'20 系列 × 5 阶'},
  ],
  chapters, characters, jobProposal:jobs, skillTreeProposal, openQuestions, sources,
};
fs.writeFileSync(dest,JSON.stringify(bible,null,2)+'\n','utf8');
console.log(JSON.stringify({file:path.relative(root,dest),chapters:chapters.length,characters:characters.length,sources:sources.length}));
