const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const output = path.join(root, 'outputs');
const inventoryPath = path.join(output, 'rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json');
const progressPath = path.join(output, 'rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json');
const screenshot = 'rpg-2-star-ocean-the-second_scifi-city_in-engine-visual-sample_m8-v02_20261013-232003-7881fcaa.png';
const inventory = JSON.parse(fs.readFileSync(inventoryPath, 'utf8'));
const progress = JSON.parse(fs.readFileSync(progressPath, 'utf8'));
const items = inventory.categories.flatMap(category => category.subcategories.flatMap(group => group.items));
const byId = id => {
  const item = items.find(entry => entry.id === id);
  if (!item) throw new Error(`Missing asset inventory item: ${id}`);
  return item;
};
const set = (id, note) => {
  const item = byId(id);
  item.stage = 'production';
  item.checked = false;
  item.file = '/assets/' + encodeURIComponent(screenshot);
  item.note = note;
};

set('art.scifi-reference', '原创方向样板：保留实用旧建筑，加入公共信息、物流与安保设施。比例、色彩和像素密度仍待人工确认。');
set('art.scifi-character-scale', '主角男版与梁序已在 1280×720 Godot 独立预览场景合成；单张静态透明图，尚未完成足底锚点与动画验收。');
set('art.scifi-city-sample', '科技城市 v02 已导入 Godot 并取得实际引擎截图；仍需人工确认视觉方向，之后拆分为可交互图层。');
set('display.protagonist-male', '已有身份一致的透明静态候选图并放入引擎画面；尚未接入角色 ID 的正式游戏内展示。');
set('display.liang-xu', '已有身份一致的透明静态候选图并放入引擎画面；来源设定图尚未验收，正式游戏内展示待接入。');
set('visual-scene.city', '城市视觉样板已在独立 Godot 场景截图；当前探索场景仍为功能原型，交互层、遮挡、碰撞与运行审查未完成。');

const now = new Date().toISOString();
inventory.updatedAt = now;
progress.updatedAt = now;
progress.currentStep = 'M8';
const m8 = progress.steps.find(step => step.id === 'M8');
if (!m8) throw new Error('Missing M8');
m8.status = 'in_progress';
m8.details = [
  ...m8.details.filter(line => !line.startsWith('先完成城市画面及两名角色')),
  '科技城市背景两版、主角男版和梁序单人透明图已制作。v02 补强公共信息、安保与自动物流设施。',
  '三张选用素材已导入独立 Godot 预览场景，并取得 1280×720 实际引擎截图；当前可玩场景尚未换图。',
  '本批素材仍是静态样板，不计入四方向探索精灵、已完成场景或已验收展示图。'
];
m8.remaining = [
  '人工确认城市与两名角色的视觉方向和游戏画面比例；检查科技特征、轮廓、光源与交互可读性。',
  '将确认的城市画面拆分为可交互图层，制作角色四方向待机与行走，接入现有科技区探索。',
  '审查其余人物设定图，完成 52 份展示、52 套探索精灵、科技区战斗动作和 11 项场景画质。'
];
m8.evidence.push('outputs/' + screenshot + ' (1280×720 Godot render; visual-direction candidate, not final acceptance)');

fs.writeFileSync(inventoryPath, JSON.stringify(inventory, null, 2) + '\n');
fs.writeFileSync(progressPath, JSON.stringify(progress, null, 2) + '\n');
console.log(JSON.stringify({m8:m8.status,sample:screenshot,productionCandidates:items.filter(item=>item.id.startsWith('art.scifi')&&item.stage==='production').length}));
