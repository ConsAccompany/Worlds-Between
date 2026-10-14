# 纪澄｜侧视战斗样机接入复核

**状态：运行中、视觉未批准。** 纪澄的 20 张独立 `80×80` 侧视帧已接入科技区战斗场地。战斗数值、范围、AI、玩家输入、奖励与存档没有改变。

## 接入与性能

- [战斗场地](../../game/scripts/battle_arena.gd)在队员 ID 为 `ji-cheng` 时使用[纪澄帧集](../../game/scripts/rpg-2-star-ocean-the-second_ji-cheng_sideview-combat-frames_m8-prototype_20261014-144950-51da030d.gd)，只读取[有效清单](../../game/assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-combat-manifest_m8-prototype_20261014-144815-54f4a48b.json)中 `_20261014-144815-` 的 20 帧。共用既有八类动作计时、`(30,73)` 足底锚点、`y=272` 地面与 nearest 像素过滤。
- 五套角色动作集加入后，原来在场景解析时预载全部 100 张纹理，使 M3 的首次战斗转场连续两次超过一秒（约 1083、1113 ms）。已把五套帧集改为首次取用单张图时加载，并在帧集中缓存；未改变帧路径或动作选择。随后首次战斗转场在自动检查中为 301–353 ms，`m3_smoke.gd` 的一秒门槛恢复通过。这个数值是本机自动测试观察值，仍需在目标设备试玩确认。

## 验证与画面

- Godot 4.7.2 导入纪澄 20 张 PNG 成功。[纪澄定向测试](../../game/tests/rpg-2-star-ocean-the-second_ji-cheng_sideview-combat-smoke_m8-prototype_20261014-145020-320a558c.gd)核对 8 类动作指定帧，及实际攻击、个人技能、闪避、受击入口。
- 改为按需加载后，男主、女主、梁序、赵铃、纪澄五项定向测试均通过；`m3_smoke.gd`、`m5_smoke.gd` 均通过。`git diff --check` 没有空白错误。
- 按需加载之后，在 Godot OpenGL Compatibility 实际 `640×360` 视口中分别保存并目视检查[待机](../../outputs/rpg-2-star-ocean-the-second_ji-cheng_scifi-battle-native-idle-phase-01_m8-prototype_20261014-145155-3d14544c.png)、[攻击第 2 帧](../../outputs/rpg-2-star-ocean-the-second_ji-cheng_scifi-battle-native-attack-phase-02_m8-prototype_20261014-145155-8ba50c77.png)、[技能第 3 帧](../../outputs/rpg-2-star-ocean-the-second_ji-cheng_scifi-battle-native-skill-phase-03_m8-prototype_20261014-145155-63f2a55c.png)。森林绿外套、银色发尾、放大镜与遗迹菱形可辨；[截图清单](../../outputs/rpg-2-star-ocean-the-second_ji-cheng_scifi-battle-native-capture-manifest_m8-prototype_20261014-145155-68271a3f.json)标记为未批准。

## 后续验收

截图固定了三帧，尚未检验连续动画、五人同屏辨识、相邻角色遮挡或玩家手感。当前素材只朝右；纪澄剃发与银色发尾的非对称关系在朝左时须单独处理。战斗背景仍是几何占位，未达到环境美术目标。
