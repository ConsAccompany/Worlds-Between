# 女主角横向战斗动作接入复核（M8 样板）

**状态：运行中的未批准视觉样板。** 女主 20 张单独的 `80×80` 横向战斗帧已接入实际战斗场地。男主使用此前相同的贴图和动作计时；三名科技区伙伴继续使用现有占位图。战斗数值、输入、AI、自动战斗和存档流程没有改动。

## 接入方法

- [战斗场地脚本](../../game/scripts/battle_arena.gd)按主角外观读取[男主帧集](../../game/scripts/rpg-2-star-ocean-the-second_protagonist-male_sideview-combat-frames_m8-prototype_20261014-142500-75b6d7ec.gd)或[女主帧集](../../game/scripts/rpg-2-star-ocean-the-second_protagonist-female_sideview-combat-frames_m8-prototype_20261014-143330-d94057ea.gd)。两套共用待机、移动、攻击、防御、闪避、受击、倒下、个人／职业技能八类状态与计时。
- 贴图按 `(30,73)` 足底锚点对齐现有战斗地面 `y=272`，使用 nearest 像素过滤。画布与动作阶段均与男主一致，使选择角色外观不改变攻击范围、位置或结果。
- [女主定向测试](../../game/tests/rpg-2-star-ocean-the-second_protagonist-female_sideview-combat-smoke_m8-prototype_20261014-143400-b7f46120.gd)核对八类动作与期望阶段的女主纹理，并验证实际攻击、技能、闪避和受击入口。旧的[男主定向测试](../../game/tests/rpg-2-star-ocean-the-second_protagonist-male_sideview-combat-smoke_m8-prototype_20261014-143000-2aee14b7.gd)仍通过。

## Godot 运行证据

在 Godot 4.7.2 的 OpenGL 实际 `640×360` 视口中，分别保存并查看以下三张截图。马尾在三种姿态下都从后脑伸出，与男主的短发区别可辨：

- [女主待机](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_scifi-battle-native-idle-phase-01_m8-prototype_20261014-143323-a466e616.png)
- [女主攻击第 2 帧](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_scifi-battle-native-attack-phase-02_m8-prototype_20261014-143323-ee4d98be.png)
- [女主技能第 3 帧](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_scifi-battle-native-skill-phase-03_m8-prototype_20261014-143323-8665de18.png)

女主与男主的定向视觉测试均通过；`m3_smoke.gd` 与 `m5_smoke.gd` 也通过，覆盖战斗胜负、输入、恢复、技能与成长。Godot 编辑器导入 20 张女主新素材成功；`git diff --check` 没有空白错误。

## 后续验收

两套主角动画仍只画向右；向左必须核对马尾／围巾／徽记／背包的非对称关系。短剑仍画在人体同层，其他职业与装备换装需要拆分或另画。此轮截图是静态阶段检查，正式验收还需连续运动的脚底、帧节奏、五人同屏辨识，以及最终战斗环境美术。现有战斗场地在截图中仍是几何占位背景，画质目标未达成。
