const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const outDir = path.join(root, 'outputs');
const dest = path.join(outDir, 'rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json');
const existing = fs.existsSync(dest) ? JSON.parse(fs.readFileSync(dest, 'utf8')) : null;
const oldItems = new Map((existing?.categories || []).flatMap(c => c.subcategories.flatMap(s => s.items)).map(i => [i.id, i]));
const outputFiles = fs.readdirSync(outDir).filter(n => n.endsWith('.png'));

const core = [
  ['liang-xu','梁序','科技'],['jiang-lan','蒋岚','科技'],['lin-que','林阙','科技'],['milo','米洛','科技'],
  ['adi','阿荻','自然'],['muxiu','牧修','自然'],['yanke','岩柯','自然'],['sangguo','桑果','自然'],
  ['nalia','娜丽娅','奇幻'],['isai','伊赛','奇幻'],['sain','赛恩','奇幻'],['daga','达伽','奇幻'],
  ['chenxian','晨弦','魔法'],['yelan','夜澜','魔法'],['luowen','洛纹','魔法'],
];
const extra = [
  ['ji-cheng','纪澄','科技'],['zhou-he','周赫','科技'],['aiti','艾缇','科技'],
  ['ye-qiao','叶乔','自然'],['mi-yi','米漪','自然'],['luo-qi','罗栖','自然'],
  ['avila','阿维拉','奇幻'],['kern','克恩','奇幻'],['lairui','莱芮','奇幻'],
  ['mi-luo','弥罗','魔法'],['heya','赫娅','魔法'],['wu-li','乌礼','魔法'],
  ['huan-7','环七','星外'],['suiya','穗芽','星外'],['zhongdu','钟渡','星外'],
  ['zhao-ling','赵铃','科技'],['pei-zhi','裴支','科技'],['an-suo','安索','科技'],['su-yan','苏砚','科技'],
  ['tao-yu','陶榆','自然'],['ruan-tian','阮田','自然'],['bu-he','布禾','自然'],['han-ze','韩泽','自然'],
  ['xida','席妲','奇幻'],['gu-lin','顾鳞','奇幻'],['ruima','瑞玛','奇幻'],['tao-li','陶粒','奇幻'],
  ['lin-yan','霖砚','魔法'],['he-huai','何槐','魔法'],['xuan-ya','玄芽','魔法'],['que-zhi','雀枝','魔法'],
  ['menling','门铃','星外'],['lingbing','零饼','星外'],['lengjing','棱镜','星外'],['yuyin','余音','星外'],
];
const approvedHair = new Set(['jiang-lan','milo','adi','nalia','isai','daga','chenxian','yelan','luowen']);
function portrait(slug, name, board, scope) {
  const matches = outputFiles.filter(f => f.includes(`_${slug}_character-sheet_`));
  matches.sort((a,b) => Number(b.includes('hairstyle-v02')) - Number(a.includes('hairstyle-v02')) || b.localeCompare(a));
  const file = matches[0] || null;
  const id = `portrait.${slug}`;
  return {id,name:`${name} · 21:9 人物设定图`,scope,board,target:1,stage:file ? (approvedHair.has(slug) ? 'approved' : 'concept') : 'planned',checked:oldItems.get(id)?.checked ?? approvedHair.has(slug),file:file ? `/assets/${encodeURIComponent(file)}` : null};
}
function fixed(id,name,scope,target=1,stage='planned',note='',file=null) {
  return {id,name,scope,target,stage,checked:oldItems.get(id)?.checked ?? stage==='approved',note,file:file ? `/assets/${encodeURIComponent(file)}` : null};
}
function sub(id,name,items) {return {id,name,items};}
function cat(id,name,subcategories) {return {id,name,subcategories};}

const heroPortraits = [
  {id:'portrait.protagonist-male',name:'主角·男 · 21:9 人物设定图',scope:'MVP',board:'地下社区',target:1,stage:'concept',checked:oldItems.get('portrait.protagonist-male')?.checked ?? false,file:'/assets/'+encodeURIComponent(outputFiles.find(f=>f.includes('_protagonist_character-sheet_male_')))},
  {id:'portrait.protagonist-female',name:'主角·女 · 21:9 人物设定图',scope:'MVP',board:'地下社区',target:1,stage:'concept',checked:oldItems.get('portrait.protagonist-female')?.checked ?? false,file:'/assets/'+encodeURIComponent(outputFiles.find(f=>f.includes('_protagonist_character-sheet_female_')))},
];
const portraits = [...heroPortraits,...core.map(([s,n,b],i)=>portrait(s,n,b,i===0?'MVP':'Full')),...extra.map(([s,n,b],i)=>portrait(s,n,b,[0,15].includes(i)?'MVP':'Full'))];

const categories = [
  cat('characters','角色',[
    sub('portraits','21:9 人物设定图',portraits),
    sub('exploration-sprites','俯视探索精灵',[
      fixed('sprite.hero','主角男女探索精灵与方向动画','MVP',2,'production','M7 已接入男女不同发型的静态探索精灵；逐方向动画仍待制作','rpg-2-star-ocean-the-second_scifi-outskirts_relay-exploration_m7_20261013-211403-6b319708.png'),
      fixed('sprite.mvp-companions','MVP 三位伙伴探索精灵：梁序、赵铃、纪澄','MVP',3,'production','M4 临时几何形与发型识别已接入；正式逐方向像素动画待制作','rpg-2-star-ocean-the-second_scifi-city_companion-exploration_m4_20261013-203138-5e777182.png'),
      fixed('sprite.other-companions','其余 47 位伙伴探索精灵','Full',47),
      fixed('sprite.job-outfits','职业外观细节变化与辨识度校验','Full',52,'planned','沿用角色个人发型和识别道具'),
    ]),
    sub('combat-sprites','横向战斗动画',[
      fixed('combat-sprite.hero','主角男女战斗动作组','MVP',2,'concept'),
      fixed('combat-sprite.mvp-companions','MVP 三位伙伴战斗动作组','MVP',3,'production','M4 三人已可战斗，保留发型与配色差异；正式动作帧待制作','rpg-2-star-ocean-the-second_scifi-party_battle-hud_m4_20261013-203138-11f66e25.png'),
      fixed('combat-sprite.other-companions','其余 47 位伙伴战斗动作组','Full',47),
    ]),
    sub('character-ui','角色界面素材',[
      fixed('character-ui.portraits','队伍头像与对话立绘裁切','MVP',4),
      fixed('character-ui.relationships','关系与招募状态图标','Full'),
    ]),
  ]),
  cat('world','世界与场景',[
    sub('world-map','世界地图',[
      fixed('world-map.mvp','科技板块三地点地图与道路','MVP',1,'production','M2 可玩原型；正式地图美术待制作','rpg-2-star-ocean-the-second_scifi-map_visual-proof_m2_20261013-201352-8194746e.png'),
      fixed('world-map.full','五板块全世界地图及传送门入口','Full',5),
    ]),
    sub('scenes','可探索场景',[
      fixed('scene.mvp-city','MVP 科技城市片区','MVP',1,'production','M2 可玩原型；正式场景美术待制作','rpg-2-star-ocean-the-second_scifi-city_visual-proof_m2_20261013-201352-4940f7f5.png'),
      fixed('scene.mvp-outskirts','MVP 城外场景','MVP',1,'production','M2 可玩原型；正式场景美术待制作','rpg-2-star-ocean-the-second_scifi-outskirts_visual-proof_m2_20261013-201352-7e3fc6e6.png'),
      fixed('scene.mvp-ruin','MVP 遗址室内场景','MVP',1,'production','M2 可玩原型；正式场景美术待制作','rpg-2-star-ocean-the-second_scifi-ruins_visual-proof_m2_20261013-201352-0302dc4c.png'),
      fixed('scene.mvp-surveys','MVP 三地各两处勘察空间','MVP',6,'production','M7 城市、城外、遗址各有外层与内层；目前为可玩几何场景，正式像素图块待制作','rpg-2-star-ocean-the-second_scifi-city_survey-outer-room_m7_20261013-212250-336fb175.png'),
      fixed('scene.cities','五板块大城市基础场景','Full',25),fixed('scene.communities','五板块小社区基础场景','Full',25),fixed('scene.wilderness','五板块野外基础场景','Full',25),
      fixed('scene.special','板块专属遗迹、传送门与地下社区扩展场景','Full',1,'planned','实际数量随地点设计增加'),
    ]),
    sub('tiles-props','地图图块与物件',[
      fixed('tiles.board','五板块地表/建筑图块组','Full',5),fixed('props.interactive','可调查物、商店、营地与门的状态素材','Full'),fixed('props.archaeology','考古资料、器物和线索图像','Full'),
    ]),
    sub('battle-fields','战斗场地',[
      fixed('arena.mvp','MVP 固定尺寸平地战斗场地','MVP',1,'production','M3 可玩原型；正式战场美术待制作','rpg-2-star-ocean-the-second_scifi-patrol_battle-visual-proof_m3_20261013-201830-fa18b3d5.png'),
      fixed('arena.boards','五板块战斗背景与变体','Full',5),
    ]),
  ]),
  cat('combat','战斗视觉',[
    sub('enemies','敌人与首领',[
      fixed('enemy.mvp','科技板块两类普通敌人动画','MVP',2,'production','巡逻机与防卫机已可战斗；正式逐帧动画待制作','rpg-2-star-ocean-the-second_scifi-sentry_battle-visual-proof_m3_20261013-201830-6ee1e4e4.png'),
      fixed('enemy.board','各板块普通敌人动画组','Full',5),fixed('enemy.boss','主要首领与组织机械设计','Full'),
    ]),
    sub('effects','动作与技能效果',[
      fixed('vfx.common','攻击、闪避、防御、受击、治疗通用效果','MVP',5),fixed('vfx.mvp-skills','MVP 个人与职业技能效果','MVP'),fixed('vfx.jobs','20 职业系列技能效果库','Full',20),fixed('vfx.personal','50 位同伴个人专属技能效果','Full',50),
    ]),
    sub('transitions','转场与反馈',[
      fixed('vfx.encounter','接敌、胜利、战败及战后恢复反馈','MVP',4,'production','M3 已有接敌、胜败与恢复文字反馈；正式特效待制作','rpg-2-star-ocean-the-second_scifi-patrol_victory-visual-proof_m3_20261013-201830-4cdeebfa.png'),
    ]),
  ]),
  cat('interface','界面',[
    sub('navigation','导航与探索',[
      fixed('ui.menu','中英文主菜单与基础按钮','MVP',1,'approved'),
      fixed('ui.map','世界地图地点选择','MVP',1,'production','M2 已实现中英文可点击地点选择','rpg-2-star-ocean-the-second_scifi-map_visual-proof_m2_20261013-201352-8194746e.png'),
      fixed('ui.explore','探索提示、交互、对话与招募','MVP',1,'production','M4 三种招募入口、暂缓邀请、回访及双语对话已实现','rpg-2-star-ocean-the-second_scifi-liang-xu_recruitment-dialogue_m4_20261013-203138-d211470b.png'),
      fixed('ui.field-log','MVP 实地日志与发现记录','MVP',1,'production','M7 可滚动中英文日志、三地勘察状态、调查记录和试玩用时已接入','rpg-2-star-ocean-the-second_scifi-map_field-log-english_m7_20261013-212705-3687dd8f.png'),
      fixed('ui.survey','MVP 线索阅读与研判界面','MVP',1,'production','M7 18 条双语线索、三处可重试判断、JP 奖励与存档恢复已接入','rpg-2-star-ocean-the-second_scifi-city_survey-question-english_m7_20261013-212250-e614975c.png'),
      fixed('ui.demo-completion','MVP 试玩完成反馈','MVP',1,'production','M7 提交调查资料后显示总结、用时，并可继续探索','rpg-2-star-ocean-the-second_scifi-city_completion-report-chinese_m7_20261013-212705-9cef7d14.png'),
    ]),
    sub('battle-ui','战斗界面',[
      fixed('ui.battle-hud','五人队伍、HP/能量、角色切换','MVP',1,'production','M4 五人位、角色切换及全自动开关已实现；正式视觉待制作','rpg-2-star-ocean-the-second_scifi-party_battle-hud_m4_20261013-203138-11f66e25.png'),
      fixed('ui.skills','快捷技能与暂停指令菜单','MVP',1,'production','M5 已接入 Q 个人技、R 当前职业技、暂停菜单选择职业前两阶技能；正式技能动效待制作','rpg-2-star-ocean-the-second_scifi-party_job-skills-pause_m5_20261013-204216-b5254efa.png'),
      fixed('ui.results','战斗结算与收益','MVP',1,'production','M5 已接入独立 XP/JP、升级回满与职业关口；正式结算视觉待制作','rpg-2-star-ocean-the-second_scifi-patrol_victory-visual-proof_m3_20261013-201830-4cdeebfa.png'),
    ]),
    sub('management','角色与系统',[
      fixed('ui.party','队伍与候补','MVP',1,'production','M4 五人上场位已实现；候补管理在队伍扩容时补齐','rpg-2-star-ocean-the-second_scifi-party_battle-hud_m4_20261013-203138-11f66e25.png'),
      fixed('ui.jobs','天分、职业树、技能 JP','MVP',1,'production','M5 四项天分、四系列前两阶、十级必选、职业与个人技能 JP 升级已可操作；正式视觉待制作','rpg-2-star-ocean-the-second_hero_promoted-skill-growth_m5_20261013-204016-031a5f3d.png'),fixed('ui.saves','自动/手动存档和加载','MVP',1,'production','M6 三个手动栏、五条自动记录、主菜单读取与中英界面已可操作；正式视觉待制作','rpg-2-star-ocean-the-second_save-screen_manual-and-auto_m6_20261013-204655-26f8e92b.png'),fixed('ui.settings','语言、声音与输入设置','MVP'),
      fixed('ui.guild','商会经营和周结算','Full'),fixed('ui.reputation','板块与全球名声','Full'),fixed('ui.relationship','关系与组合技','Full'),fixed('ui.codex','考古记录与发现图鉴','Full'),
    ]),
  ]),
  cat('audio','声音',[
    sub('music','音乐',[
      fixed('music.mvp','MVP 城镇、野外、遗址、战斗音乐','MVP',4,'production','M7 接入四段原创合成环境循环；主题配乐仍待制作'),fixed('music.boards','五板块地区主题与战斗变体','Full',5),fixed('music.endgame','星外与终局音乐','Full'),
    ]),
    sub('sound-effects','音效与环境',[
      fixed('sfx.ui','按钮、菜单、提示音','MVP'),fixed('sfx.discovery','调查发现提示音','MVP',1,'production','M7 中继站和遗址调查已触发音效'),fixed('sfx.combat','攻击、防御、技能、胜败音效','MVP'),fixed('sfx.ambience','五板块环境声库','Full',5),fixed('sfx.characters','角色与机械动作声库','Full'),
    ]),
  ]),
  cat('text-data','文本与数据',[
    sub('localization','中英文文本',[
      fixed('text.ui','菜单与基础界面中英文键值','MVP',1,'approved'),fixed('text.mvp','MVP 三地点、三伙伴与线索文本','MVP',1,'production','M7 已接入 18 条现场线索、三道研判题、中继与遗址记录、完成反馈双语文本；正式剧情待后续设计','rpg-2-star-ocean-the-second_scifi-city_survey-clue-chinese_m7_20261013-212250-ac53f069.png'),fixed('text.full','五板块任务、人物、物品、图鉴双语文本','Full'),
    ]),
    sub('game-data','可维护内容数据',[
      fixed('data.characters','50 同伴与主角职业/天分数据','Full',51),fixed('data.jobs','20 系列 × 5 阶职业定义','Full',100),fixed('data.items','装备、道具、合成与商会货物定义','Full'),fixed('data.enemies','固定地区敌人及可选终局难度数据','Full'),
    ]),
  ]),
];

const inventory = {schemaVersion:1,project:'rpg-2-star-ocean-the-second',updatedAt:new Date().toISOString(),definition:'A check means that the specific asset has been accepted for its stated purpose. Concept art remains distinct from game-ready sprites.',categories};
fs.writeFileSync(dest, JSON.stringify(inventory,null,2)+'\n','utf8');
const all = categories.flatMap(c=>c.subcategories.flatMap(s=>s.items));
console.log(JSON.stringify({file:path.relative(root,dest),items:all.length,accepted:all.filter(i=>i.checked).length,portraits:portraits.length,portraitConcepts:portraits.filter(i=>i.stage!=='planned').length}));
