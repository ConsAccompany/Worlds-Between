# 赵铃｜侧视战斗样机接入复核

**状态：运行中，视觉仍未批准。** 赵铃的 20 张独立 `80×80` 战斗帧已接入科技区战斗场地。本轮只扩展角色的画面选择和定向检查；数值、攻击范围、AI、输入、奖励、存档逻辑未改变。

## 接入

- [战斗场地脚本](../../game/scripts/battle_arena.gd)在队员 ID 为 `zhao-ling` 时读取[赵铃帧集](../../game/scripts/rpg-2-star-ocean-the-second_zhao-ling_sideview-combat-frames_m8-prototype_20261014-144510-9d264ec4.gd)。帧集只预载[有效清单](../../game/assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-combat-manifest_m8-prototype_20261014-144336-7d0dd6cc.json)内的 `_20261014-144336-` 素材。
- 赵铃与已接入的男主、女主、梁序共用八类动作判定、动作时钟、`(30,73)` 足底锚点以及 nearest 像素过滤。`y=272` 为战斗地面。其他同伴仍沿用原有占位画法。
- 玩家操纵赵铃或由 AI 控制时，攻击、闪避、个人／职业技能、受击与倒地都使用现有战斗事件选择对应画面。

## 自动检查与游戏内证据

- Godot 4.7.2 编辑器导入 20 张新图成功。[赵铃定向测试](../../game/tests/rpg-2-star-ocean-the-second_zhao-ling_sideview-combat-smoke_m8-prototype_20261014-144600-2b99cd63.gd)通过：核对 8 个动作指定阶段的有效纹理，以及实际攻击、个人技能、闪避和受击入口。
- 男主、女主、梁序、赵铃四项定向测试均通过；`m3_smoke.gd` 与 `m5_smoke.gd` 输出通过。`git diff --check` 无空白错误。
- Godot OpenGL Compatibility 实际 `640×360` 视口中，分别保存并检查[待机](../../outputs/rpg-2-star-ocean-the-second_zhao-ling_scifi-battle-native-idle-phase-01_m8-prototype_20261014-144529-9092d5fb.png)、[攻击第 2 帧](../../outputs/rpg-2-star-ocean-the-second_zhao-ling_scifi-battle-native-attack-phase-02_m8-prototype_20261014-144529-107c66a4.png)和[技能第 3 帧](../../outputs/rpg-2-star-ocean-the-second_zhao-ling_scifi-battle-native-skill-phase-03_m8-prototype_20261014-144529-493fba0e.png)。赵铃与男主并排，耳机和天线仍清楚，短射线和同心圆技能可辨。
- [截图清单](../../outputs/rpg-2-star-ocean-the-second_zhao-ling_scifi-battle-native-capture-manifest_m8-prototype_20261014-144529-4a4e7ff7.json)记录三张视口图与未批准状态。

## 后续视觉验收

这三张图是固定阶段的画面证据，尚未检验连续动作时的脚底稳定、帧节奏、五人同屏、角色重叠或人类试玩感受。当前角色只画朝右，朝左时耳机、侧分发与背包的非对称关系仍需专门审查。场地背景仍是几何占位，未达到目标环境美术质量。
