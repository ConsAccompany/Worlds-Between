# 遗迹调查附楼第二房间背景概念 · M8

**状态：未接入、未验收。** 单张 [源图](../../game/assets/environments/rpg-2-star-ocean-the-second_scifi-ruins-survey-annex-room-02_environment-background_m8-concept_20261014-143300-042ae336.png) 为 1672×941 RGB，另有单张 [640×360 逻辑尺寸预览](rpg-2-star-ocean-the-second_scifi-ruins-survey-annex-room-02_environment-scale-preview_m8-concept_20261014-143326-4058e8aa.png)。使用内置 imagegen；没有拼贴、内嵌人物或界面。

## 场景定位与坐标

第一房间的外环档案室有沙色石砖、红砖断面、废旧青铜导管及后墙的封存装置。第二房间延续这套材质，在后墙加入破损的圆形实验设备与两侧封存壁龛，令它成为更深的**旧实验核心**，但设备不发光、不说明旧实验真正用途。低对比度地面线刻帮助连接两个房间，不把谜团写成既定事实。

`game/scripts/survey_annex.gd` 的第二房间仍使用与其他调查室相同的站位：三处线索 `(163,165)`、`(320,165)`、`(477,165)`，返回出口 `(57,257)`，分析终端 `(320,263)`，主角初始 `(87,261)`。在 640×360 预览中，这些位置都落在连续平整石地上；墙、碎石和实验设备位于靠后或极侧边。没有把线索、终端或门绘进背景，因此可由运行时状态绘制。当前移动夹限 x=25–615、y=78–305；画面前缘断墙约在 y=313 以外，最下方行走仍需实机检查。

## 最终生成提示词

```text
Use case: stylized-concept. Create ONE original 16:9 standalone background plate for room 2, the former experiment core inside an archaeological ruin's survey annex, playable as a 640×360 top-down RPG map. Room 1 immediately before it uses warm sandy limestone and exposed reddish brick, collapsed arches, small dark-oxidized teal conduits, inactive weathered machines along the upper rear wall, and an almost orthographic elevated three-quarter view. Preserve that exact material family and premium hand-painted pixel-art craft, but make this room visibly deeper and older: a partially exposed experimental apparatus embedded in the BACK WALL ONLY, with a cracked circular stone/metal housing, dormant glass conduits, sealed archive niches, old repair patches and readable strata. Keep it intriguing, not an active glowing reactor; the story has not proven what the apparatus did. Visual palette: desaturated ocher sandstone, muted charcoal, rust, sparse oxidized teal, soft natural light falling from a broken upper wall. Strict practical layout: all of the central walking region from x=8% to 92%, y=31% to 88% is one flat continuous level stone floor without holes, pools, rails, steps, rubble piles, columns, debris, foreground walls or furniture. Reserve clear 50-pixel standing areas at game-map clue placements (x=25%, 50%, 75%, y=46%), exit overlay (x=9%, y=71%), analysis terminal overlay (x=50%, y=73%), hero start (x=14%, y=73%). Put NO pre-rendered interactable clue tablets, console, active terminal, actual exit door, character, person, robot, creature, text or icons at these spots; runtime draws them. Keep detail along top 0–29% and extreme sides, with fine worn seams and faint archaeological scoring across the floor. At x=50%, y=73% the ground must stay visibly flat even if it carries a subtle faded inlay. UI will cover top 0–17% and bottom 88–100%. High-detail 2D pixel RPG environment, legible once downscaled to 640×360. No signage, legible writing, UI, watermark, collage, split screen or multiple panels. One room only.
```

## 待完成验收

- 真实 Godot 场景需要同时显示三处运行时线索、出口、终端、主角和中英文标签，确认前缘墙与最下方人物不冲突。
- 生成图从高分辨率缩放，未按原生 640×360 逐像素清理；美术质量门槛仍待人工审查。
- 原脚本还会绘制自身的背景和房间二圆环；接入时需统一层次与视觉语义，避免重复装饰。未修改任何共享运行时、登记表或跟踪状态。
