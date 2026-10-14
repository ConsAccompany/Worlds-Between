# 男主横向战斗动作接入复核（M8 样板）

**状态：运行中的未批准视觉样板。** 男主角的 20 张独立 `80×80` 原生像素帧已接入科技区战斗场地，未改变战斗数值、输入、AI、保存或其他角色的绘制方法。女主角外观仍走原来的几何占位绘制，等待她自己的横向战斗素材。

## 映射

| 战斗状态 | 男主视觉动作 |
|---|---|
| 无操作 | 两帧待机循环 |
| 向左右移动／AI 移动 | 四帧移动循环 |
| 攻击，包括射程外挥空 | 三帧攻击，约 0.39 秒 |
| 按住防御／AI 防御 | 两帧防御循环 |
| 闪避窗口 | 两帧闪避，跟随现有 0.27 秒闪避计时 |
| 实际受到伤害 | 两帧受击，约 0.24 秒 |
| HP 变为零 | 两帧倒下并停留在落地帧 |
| 个人技能或职业技能成功施放 | 三帧技能，约 0.45 秒 |

战斗暂停时动作计时暂停。战斗结束后仅视觉计时继续走到收招或倒地，不更新战斗状态。贴图以共同足底 `(30,73)` 对齐现有 `y=272` 战斗地面，按原生尺寸与 nearest 像素过滤绘制；脚底坐标随角色移动，伤害与攻击距离仍使用既有数值。

## 运行验证

- Godot 4.7.2 编辑器导入与脚本解析成功。
- `m3_smoke.gd` 与 `m5_smoke.gd` 均通过，覆盖攻击、闪避、防御、受击、胜负、技能、成长与场景返回的关键路径。
- [定向视觉测试](../../game/tests/rpg-2-star-ocean-the-second_protagonist-male_sideview-combat-smoke_m8-prototype_20261014-143000-2aee14b7.gd) 检查八种动作各自选中正确的 `80×80` 纹理，并验证攻击、个人技能、闪避、受击入口会设置对应视觉状态。使用实际 OpenGL Godot 640×360 视口保存了五张**分开的**运行截图：
  - [待机](../../outputs/rpg-2-star-ocean-the-second_scifi-battle_native-idle-phase-01_m8-prototype_20261014-142732-f3a86721.png)
  - [攻击第 2 帧](../../outputs/rpg-2-star-ocean-the-second_scifi-battle_native-attack-phase-02_m8-prototype_20261014-142732-9071dfd6.png)
  - [倒地第 2 帧](../../outputs/rpg-2-star-ocean-the-second_scifi-battle_native-down-phase-02_m8-prototype_20261014-142732-5c7849bd.png)
  - [技能第 3 帧](../../outputs/rpg-2-star-ocean-the-second_scifi-battle_native-skill-phase-03_m8-prototype_20261014-142732-afb3cd06.png)
  - [女主角旧绘制对照](../../outputs/rpg-2-star-ocean-the-second_scifi-battle_native-female-legacy-phase-01_m8-prototype_20261014-142732-bf89dd9a.png)

截图中男主的蓬松短发、茶绿围巾和棕色外套在深色战斗场地上可辨；武器、倒地与技能姿态亦可辨。尚需人类在实时运动中审查节奏与五人同屏辨识度，也需生产女主及三名可玩伙伴的横向战斗图。当前横向场地本身仍为几何占位背景，未达到最终环境画质目标。

一轮并行 `m4_smoke.gd` 遇到另一项工作正更新郊外背景时的 Godot 导入缺失（`scifi_exploration_area.gd` 引用新 PNG，其 `.import` 当时尚不存在），并非本次战斗脚本错误。待该场景素材落稳并导入后复跑 M4；不得把这轮 M4 记为通过。
