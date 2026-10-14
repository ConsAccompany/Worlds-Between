const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const output = path.join(root, 'outputs');
const inventoryPath = path.join(output, 'rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json');
const progressPath = path.join(output, 'rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json');
const inventory = JSON.parse(fs.readFileSync(inventoryPath, 'utf8'));
const progress = JSON.parse(fs.readFileSync(progressPath, 'utf8'));
const now = new Date().toISOString();

const sub = (categoryId, subcategoryId) => {
  const category = inventory.categories.find(item => item.id === categoryId);
  const found = category.subcategories.find(item => item.id === subcategoryId);
  if (!found) throw new Error(`Missing ${categoryId}/${subcategoryId}`);
  return found;
};
const addSub = (categoryId, id, name, items) => {
  const category = inventory.categories.find(item => item.id === categoryId);
  if (category.subcategories.some(item => item.id === id)) return;
  category.subcategories.push({id, name, items});
};
const pending = (id, name, board, note = '') => ({id, name, scope:'MVP', board, target:1, stage:'planned', checked:false, ...(note ? {note} : {})});

const portraits = sub('characters', 'portraits').items;
if (portraits.length !== 52) throw new Error('Expected 52 source character sheets');
for (const item of portraits) item.scope = 'MVP';
const entries = portraits.map(item => ({key:item.id.slice('portrait.'.length),name:item.name.replace(' · 21:9 人物设定图',''),board:item.board}));
addSub('characters','runtime-displays','游戏内角色展示图',entries.map(entry => pending(`display.${entry.key}`,`${entry.name} · 游戏内展示图`,entry.board,'以角色设定图为身份依据；实际游戏内查看，未验收概念稿先修订。')));
addSub('characters','runtime-exploration','四方向探索精灵',entries.map(entry => pending(`runtime-sprite.${entry.key}`,`${entry.name} · 四方向待机与行走`,entry.board,'标准像素格、足底锚点、发型与服装辨识度逐人检查。')));
sub('characters','exploration-sprites').items.find(item => item.id === 'sprite.other-companions').scope = 'MVP';
addSub('characters','playable-combat-identity','科技区可玩队伍战斗形象',[
  ['protagonist-male','主角·男'],['protagonist-female','主角·女'],['liang-xu','梁序'],['zhao-ling','赵铃'],['ji-cheng','纪澄']
].map(([key,name]) => pending(`playable-combat.${key}`,`${name} · 横向战斗动作`,'科技','待机、移动、攻击、防御、闪避、受击、倒下、个人技能与角色画像一致。')));

addSub('world','visual-direction','科技区美术基准',[
  pending('art.scifi-reference','官方参考画面与原创科技区视觉准则','科技','确定场景尺度、像素密度、色彩、材质、灯光与前中后层次。'),
  pending('art.scifi-character-scale','角色与场景比例样板','科技','选定主角和梁序，在实际游戏窗口中检查轮廓、足底锚点与光源一致。'),
  pending('art.scifi-city-sample','城市完成画面样板','科技','经实际引擎截图和人工审查后，才扩展到其余场景。')
]);
addSub('world','scene-quality','科技区场景画质验收',[
  ['map','科技区世界地图'],['city','科技城市'],['outskirts','城外通道'],['ruins','旧文明遗址'],
  ['city-survey-outer','城市档案馆外层'],['city-survey-inner','城市档案馆内层'],
  ['outskirts-survey-outer','城外中继区外层'],['outskirts-survey-inner','城外中继区内层'],
  ['ruins-survey-outer','遗址调查区外层'],['ruins-survey-inner','遗址调查区内层'],
  ['battle-arena','科技区横向战场']
].map(([key,name]) => pending(`visual-scene.${key}`,`${name} · 完成画面`,'科技','实际引擎截图通过材质、层次、光影、辨识度、交互可读性与性能审查。')));

const ids = inventory.categories.flatMap(category => category.subcategories.flatMap(group => group.items.map(item => item.id)));
if (ids.length !== new Set(ids).size) throw new Error('Duplicate asset ID');
inventory.updatedAt = now;
inventory.definition = 'A check means that the specific asset has been accepted for its stated purpose. Source character sheets, in-game displays, exploration sprites, combat sprites and scene quality have separate acceptance gates.';

progress.planVersion = 'v0.2';
progress.updatedAt = now;
progress.currentStep = 'M8';
const m7 = progress.steps.find(step => step.id === 'M7');
m7.remaining = [
  '从新档进行两条不同顺序的真实计时试玩，确认科技区内容是否达到 25–35 分钟且没有人为等待。',
  '按实际试玩结果补足内容或调整节奏；这项内容验收与 M8 美术样板可并行。'
];
const m8 = progress.steps.find(step => step.id === 'M8');
Object.assign(m8, {
  title:'Visual identity and environment quality',
  status:'ready',
  summary:'Use all 52 existing character identities in-engine; make the science-region map, three locations, six survey rooms and battle arena reach the approved visual quality target.',
  acceptance:'52 identity displays and four-direction sprites load by character ID; playable team uses individual art; all eleven scene-quality gates pass screenshot and in-game review.',
  details:[
    '主角男女两版与 50 位伙伴，共 52 份来源画像；只有 9 份设定图已在旧清单中标为验收，未验收的图仍须逐张修订或批准。',
    '51 位角色均有游戏内展示图和四方向探索形象；试玩仍只开放科技区角色。',
    '主角两版、梁序、赵铃、纪澄另有独立战斗动作；其他角色战斗动作留待其可玩阶段。',
    '科技地图、三个主场景、六个勘察空间及战斗场地共 11 项独立画质验收。',
    '先完成城市画面及两名角色的比例样板，依据实际画面决定是否需要调整 2D／2.5D 技术路线。'
  ],
  remaining:[
    '建立原创视觉基准，审查 43 份未验收的人物概念图。',
    '制作并导入 52 份展示图、52 套四方向探索精灵和科技区可玩队伍战斗动画。',
    '完成 11 项场景画质升级并逐场检查读图、性能和交互。'
  ],
  evidence:[
    '52 份角色设定图已在资产清单登记；9 份已验收，其余是概念稿。',
    '当前游戏的城市和遗址运行截图显示功能原型，尚不能证明新画质要求。',
    'outputs/rpg-2-star-ocean-the-second_mvp-implementation-plan_visual-first_v02_20261013-230524-29cf8a61.md'
  ],
  blocker:null
});
if (!progress.steps.some(step => step.id === 'M9')) progress.steps.push({
  id:'M9',title:'Final integrated acceptance',status:'todo',
  summary:'Review the combined playable route and completed visual assets in two fresh human playthroughs.',
  acceptance:'Two different route orders complete in 25–35 minutes without blockers; all visual, bilingual, save and recruitment checks pass.',
  details:['M7 内容与 M8 美术均通过后，进行整体验收。'],
  remaining:['完成两轮真实试玩并处理问题。'],evidence:[],blocker:null
});

fs.writeFileSync(inventoryPath, JSON.stringify(inventory,null,2)+'\n');
fs.writeFileSync(progressPath, JSON.stringify(progress,null,2)+'\n');
console.log(JSON.stringify({inventoryItems:ids.length,sourcePortraits:portraits.length,steps:progress.steps.length}));
