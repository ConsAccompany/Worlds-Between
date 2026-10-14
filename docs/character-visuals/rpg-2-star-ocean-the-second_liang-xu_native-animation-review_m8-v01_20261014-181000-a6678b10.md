# 梁旭：原生像素动作原型 M8 v01

状态：**制作原型，尚未通过游戏内验收**。

## 交付

- 四方向行走：每个方向 4 帧，共 16 张独立 PNG。
- 朝南攻击：抬起随身终端与能量脉冲，共 2 张独立 PNG。
- 朝南受击：手臂与衣摆收缩的反应，共 1 张独立 PNG。
- 每张为透明 RGBA、32 × 48 像素；脚底基线为 y=44，建议锚点 `(16,44)`。
- 清单：`game/assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-manifest_m8-v01_20261014-181000-c09d742e.json`。每帧给出 `action`、`direction`、从 1 开始的 `phase` 和项目相对路径。
- 可复现绘制脚本：`game/assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_liang-xu_native-animation-generator_m8-v01_20261014-181000-703a5e11.py`。

## 视觉依据与检查

四个方向现有待机图分别作为严格的人物身份参考。所有新帧的 y=0–18 区域与对应待机图逐像素一致：高发髻、浅色侧发和面部没有改变。脚步、手臂、长外套下摆与终端位置分别绘制，角色头部和躯干没有整体位移。

脚本已重新生成全套素材；Pillow 回读确认 19/19 张尺寸与 RGBA 格式正确，19 张像素内容均不同，四角透明，每张在 y=44 保持脚底像素。抽看了朝南行走、朝东行走与朝南攻击各一张。

## 待验收

尚需导入 Godot，在 1:1 最近邻渲染和实际城市背景中检查循环速度、衣摆可读性、战斗动作节奏，以及与男女主动作的统一性。当前清单不能计入正式通过数量。
