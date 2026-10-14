# 科技城调查附楼第二房间背景概念 · M8

**状态：未接入、未验收的独立候选图。** [源图](../../game/assets/environments/rpg-2-star-ocean-the-second_scifi-survey-annex-room-02_environment-background_m8-concept_20261014-142926-e2e661fc.png) 为 1672×941 RGB；另有单张 [640×360 逻辑尺寸预览](rpg-2-star-ocean-the-second_scifi-survey-annex-room-02_environment-scale-preview_m8-concept_20261014-142931-f8cffbc0.png)。由内置 imagegen 制作，无拼贴或嵌入文字。

## 视觉方向与坐标审查

与第一房间的暖石砖、墨绿档案柜、铜件、琉璃青色装置和少量藤蔓保持材质连续。第二房间的后墙是更深的档案分析室：密集卷宗抽屉、中央蓝色资料透镜和独立的地面比较图纹，给两房间不同的辨识度。

`game/scripts/survey_annex.gd` 中，第二房间角色可行走 x=25–615、y=78–305，初始点 (87,261)；三条线索显示于 (163,165)、(320,165)、(477,165)，出口 (57,257)，分析终端 (320,263)。640×360 预览中，这六处都在同一连续石地上，未预绘可交互的线索、终端、出口门或角色。场景内原脚本会绘制自己的柜台、线索块、门与终端；接入时需要由整合方决定其与背景的层次关系，避免既有柜台压住后墙细节。

## 最终生成提示词

```text
Use case: stylized-concept. Create ONE standalone original 16:9 full-screen environment background for room 2 of a 640×360 top-down RPG science-city survey annex. Room 1, just outside, is an old-world records laboratory: warm limestone masonry, graphite-teal cabinets, brass hinges, blue glass tubes, small ivy, high-detail hand-painted pixel art, orthographic elevated three-quarter view, and a large unobstructed tile floor. This room is a deeper records and analysis chamber in the SAME building and visual language, more intimate and slightly darker: a vaultlike upper wall with tall archive drawers, layered manuscript shelves, brass-edged stone panels, a restrained cyan data lens and mechanical analysis instruments along the BACK WALL ONLY (upper 0–28% of image), amber lamps, subtle patina. Add two or three shallow floor inlay motifs that imply record comparison; no objects or furniture on the walking floor. Composition is a practical game map: the whole center and bottom, x=10–92% and y=31–88%, must be one continuous flat, uncluttered, walkable stone floor, with clear 50-pixel character-sized standing spaces at three clue overlay positions (x=25%,50%,75%, y=46%) and at an exit overlay (x=9%, y=71%) and terminal overlay (x=50%, y=73%). No drawn clue tablets, consoles, actual exit door, terminal, signs, characters, robots or props at those coordinates; the game places these later. Keep the broad floor center relatively calm so yellow/cyan interactable markers and the hero remain readable at game scale. The top 0–17% is covered by a UI header, bottom 88–100% by a footer. High craft comparable to a premium contemporary 2D pixel RPG, consistent palette and materials with the first room but a distinct archive-analysis identity. No lettering, numbers, symbols that resemble UI, watermark, collage, panel or split screen. One scene only.
```

## 待验证

- 顶部 HUD 覆盖 y=0–61、底部说明条覆盖 y=318–359；预览内柜体在 y≈62–115 尚有可见部分，但要以 Godot 实际叠加界面为准。
- 前缘石栏在 y≈306–318，贴近角色 y=305 的移动下界；需在实际角色图和碰撞感受中检查，不宜在未检查时视为可用场景。
- 高清源图未按原生 640×360 像素逐点整理，也未完成角色、热点及中英文标签的同屏验收。不要更新 M8 场景通过状态。
