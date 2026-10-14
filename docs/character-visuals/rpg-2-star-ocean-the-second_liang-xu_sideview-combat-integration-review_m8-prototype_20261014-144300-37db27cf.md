# 梁序｜侧视战斗样机接入复核

**状态：未批准的运行中视觉样机。** 梁序的 20 张独立 `80×80` 侧视帧已接入实际战斗场地。此轮只改绘制路径与定向验证；伤害、AI、输入、能量、奖励与存档逻辑未改变。

## 接入

- [战斗场地](../../game/scripts/battle_arena.gd)在队员 ID 为 `liang-xu` 时使用[梁序帧集](../../game/scripts/rpg-2-star-ocean-the-second_liang-xu_sideview-combat-frames_m8-prototype_20261014-144100-a41f6b9c.gd)。只引用[有效清单](../../game/assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-combat-manifest_m8-prototype_20261014-143736-ddc3e7f9.json)内 `_20261014-143736-` 的 20 张图。
- 共用现有 `(30,73)` 足底锚点、`y=272` 战斗地面和 nearest 像素过滤。静止、移动、防御、攻击、闪避、受击、倒地、个人／职业技能使用与男女主相同的动作选择和计时。
- 男、女主仍按既有外观设置选取原帧；其他伙伴仍走原占位绘制。梁序可由 AI 控制，也可切换为当前操纵者，视觉状态沿用同一套战斗事件。

## 验证

- Godot 4.7.2 编辑器资源导入退出码 0；[梁序定向检查](../../game/tests/rpg-2-star-ocean-the-second_liang-xu_sideview-combat-smoke_m8-prototype_20261014-144200-83ea9d25.gd)通过，核对 8 个动作指定帧、实际攻击／技能／闪避／受击入口，确认每个纹理来自有效时间戳。
- 男主、女主原定向检查继续通过；`m3_smoke.gd` 与 `m5_smoke.gd` 均输出通过标记。`git diff --check` 无空白错误。
- 在 Godot OpenGL Compatibility 实际 `640×360` 视口中分别截取并目视检查：[梁序待机](../../outputs/rpg-2-star-ocean-the-second_liang-xu_scifi-battle-native-idle-phase-01_m8-prototype_20261014-144034-493acfdb.png)、[终端攻击第 2 帧](../../outputs/rpg-2-star-ocean-the-second_liang-xu_scifi-battle-native-attack-phase-02_m8-prototype_20261014-144034-e1f87c60.png)、[校准技能第 3 帧](../../outputs/rpg-2-star-ocean-the-second_liang-xu_scifi-battle-native-skill-phase-03_m8-prototype_20261014-144034-a4d7f4bd.png)。三张均看得到梁序与男主并排，银色侧发、石墨外套、终端与蓝色脉冲可辨。
- 截图[清单](../../outputs/rpg-2-star-ocean-the-second_liang-xu_scifi-battle-native-capture-manifest_m8-prototype_20261014-144034-41d4d01c.json)记录了三张视口图，状态仍为未批准。

## 尚待处理

这些截图固定了代表性帧，尚需真人试玩评估连续动画、五人同屏识别和相邻角色遮挡。全部侧视角色目前只画朝右；朝左时银色单侧发束与终端不能简单镜像后就视为已审。战斗场地背景仍是几何占位，尚未达到环境画质目标。

绘制失败轮次留下的 `_20261014-143727-` 12 张孤立 PNG 及其 `.import` 未被任何帧集引用，也未清理或提交。自动审批阻止了清理命令；集成提交时应排除它们，仅纳入有效清单指向的素材。
