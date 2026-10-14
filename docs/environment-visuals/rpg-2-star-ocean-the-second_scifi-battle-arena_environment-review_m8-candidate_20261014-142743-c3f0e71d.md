# 科技区横向战斗场地背景候选图 · M8

**状态：独立背景概念，未接入、未验收。** [源图](../../game/assets/environments/rpg-2-star-ocean-the-second_scifi-battle-arena_environment-background_m8-candidate_20261014-142723-7442fd01.png) 为 1672×941 RGB；[640×360 逻辑尺寸预览](rpg-2-star-ocean-the-second_scifi-battle-arena_environment-scale-preview_m8-candidate_20261014-142729-0761e853.png) 由源图缩放以检查实际小画面表现。使用内置 imagegen 生成一张独立图像，没有拼贴、文字或角色。

## 与现有战斗脚本的适配

`game/scripts/battle_arena.gd` 的战斗是固定侧视横向场地。五名队员初始 x=135、171、207、243、279；敌人初始 x=493。双方横向移动区间为 x=28–612。角色脚底在 y≈272，身体主要占 y≈199–272；敌人预警在 y≈210–270。顶部 HUD 覆盖 y=0–89，底部覆盖 y=302–359。

本候选图的连续石台横贯全宽，台面上沿约 y=251，角色脚底 y=272 落在其上。y≈155–250 是较暗、低对比度的石墙，适合衬托浅色角色、红色敌人及预警；拱廊、青色玻璃柱和远处科技城市集中在高处。场地没有中途障碍、高低差、前景遮挡或内嵌敌人。暖石材、青色科技装置和少量藤蔓与科技区环境配套。

两个视觉关注点：顶部 HUD 会遮住画中不少远景细节，只剩拱廊下部作为游戏时可见的环境叙事；在 x 接近 28 或 612 时，宽动作帧可能靠近两侧柱体。整合后须确认画面阅读性，不应凭静态预览批准。

## 最终生成提示词

```text
Use case: stylized-concept. Create ONE standalone original 16:9 widescreen background plate for a 640×360 side-view real-time RPG combat arena in a science-region archaeological site. The visual family is a polished, detailed hand-painted pixel-art retrofuturist city built of warm limestone, graphite metal, restrained teal-glass devices, small vines, and old-world craft. Camera: strict side-on 2D stage, level horizontal ground, no elevated isometric or top-down perspective and no camera tilt. Composition for game UI: top 0–90 pixels (25%) will be covered by a dark HUD and bottom 302–360 pixels (16%) by a footer. Between them, the combat floor occupies y=266–301 as one continuous flat stone surface from x=20 to x=620, same height across the full stage. Actor feet align near y=272; actor bodies and attacks occupy y=190–270. Keep the entire actor band x=30–610 and y=185–278 physically empty of props, platforms, debris, rocks, stairs, rails, furnishings, silhouettes or foreground occluders. Background behind actor band may show a subtle desaturated masonry wall, darker than the figures, with low contrast pattern so small character sprites and red enemy telegraphs read clearly. Put most architectural detail in the upper wall from y=90–180: weathered arches, ancient research alcoves, cyan glass conduits, a hint of ivy, layered stone seams. Add subdued side columns at far x<25 and x>615 only. A narrow floor-wall separation line at y≈270 should make grounding obvious. Lighting warm amber mixed with restrained turquoise, readable at small scale, consistent with high-end contemporary 2D pixel RPG environments. No characters, enemies, creatures, robots, particles, weapons, hit effects, health bars, UI, labels, signage, lettering, logos, watermark, collage, panel or split screen. No vertical obstacles and no objects embedded into the fighting lane. Treat the level layout as more important than decorative density.
```

## 待整合与验收

- 背景与现有男性主角横向战斗帧、其他队员的临时绘制、敌人、预警圈和 HUD 尚未一起在 Godot 实际画面检查。
- 脚本现在会自己绘制原有色块背景；整合时应由负责运行时的工作流决定替换方式，同时保持角色、特效和界面图层次序。
- 高分辨率源图未逐像素清理。M8 场景视觉门槛、战斗可读性及用户艺术批准均仍待审。
