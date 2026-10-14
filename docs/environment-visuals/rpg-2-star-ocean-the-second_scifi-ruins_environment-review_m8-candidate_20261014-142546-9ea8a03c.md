# 科技遗迹场景背景候选图 · M8

**状态：未接入、未验收的候选图。** 单张独立源图：[`game/assets/environments/rpg-2-star-ocean-the-second_scifi-ruins_environment-background_m8-candidate_20261014-142522-e254c01a.png`](../../game/assets/environments/rpg-2-star-ocean-the-second_scifi-ruins_environment-background_m8-candidate_20261014-142522-e254c01a.png)，1672×941 RGB。单张 [640×360 实际逻辑尺寸预览](rpg-2-star-ocean-the-second_scifi-ruins_environment-scale-preview_m8-candidate_20261014-142527-00bdf81f.png) 用 Lanczos 缩放源图检查小尺寸阅读性。使用内置 imagegen 生成；没有修改游戏运行代码或登记表。

## 场景适配检查

`game/scripts/scifi_exploration_area.gd` 的遗迹角色移动范围为 x=24–616、y=77–306，当前不对背景设置实体碰撞。候选图在下列坐标保留连续的平坦石地；原有运行时对象可以照常绘制在背景上。

| 实际 640×360 坐标 | 现有场景用途 | 背景检查 |
|---|---|---|
| (82,260) | 主角出生点 | 无墙、坑、台阶。 |
| (200,145) | 纪澄招募位置 | 开放石地。 |
| (115,245)、(470,115) | 两处线索 | 浅色石砖；可叠加运行时标记。 |
| (320,250) | 资料终端 | 地面无既有终端，避免重复物件。 |
| (420,225) | 野外敌人 | 可见且有绕行宽度。 |
| (548,142) | 调查入口 | 靠近右侧浅雕刻地面，周围可站立；运行时会叠加门图。 |
| (505,275) | 伙伴野外研究台 | 平坦地面，可叠加运行时研究台。 |

第一张生成候选图有前景断墙和悬崖，覆盖 (82,260) 等区域，因此**没有复制进项目**。已选第二张通过静态位置检查。它把遗迹柱、碎石、藤蔓集中在顶部及两侧，以精细石砖与浅金镶线维持中心地面的质感；青色科技痕迹克制，能与现有科技城的暖石材和青绿色调衔接。

## 最终生成提示词

```text
Use case: stylized-concept. Produce ONE original 16:9 standalone background plate for a playable 2D top-down RPG level: the science-region ancient excavation courtyard. Art style: richly detailed polished hand-painted pixel art, warm gold/limestone stone blocks, deep charcoal artifacts, subtle cyan research lighting, bits of foliage, same visual family as a welcoming high-detail retrofuturist stone science city. Critical gameplay layout: the entire image region from 8% to 94% of width and 18% to 90% of height is a FLAT, CONTINUOUS, UNBROKEN, WALKABLE PAVED FLOOR. No foreground cliff, water, ravine, stairway, rail, wall, raised platform, bush, crate, arch or sculpture anywhere in this region. Particularly keep the lower-left at x=13%, y=72% and lower-right at x=79%, y=76% bare flat floor; those are mandatory standable points. Frame the scene ONLY along the very top strip y=0–17% and outermost left/right 7% margins with old columns, fractured masonry, stratified excavation wall, ancient carved lintel, ivy, a few inert instruments. Upper right x=86%, y=40% can have a subtle floor inset suggesting a portal threshold but must remain walkable. Across the flat floor put refined faded masonry seams and a few shallow inlaid brass lines, not objects. Elevated almost orthographic three-quarter top-down camera, fixed 640×360 gameplay composition, no horizon or visible distant landscape. The image should remain visually interesting through highly crafted perimeter archaeology and floor texture while all character / enemy / interaction routes stay clear. No persons, creatures, robots, active consoles, chests, icons, labels, UI, lettering, logos, watermark, grid, collage, panel or split screen. Do not draw a foreground parapet, bridge, moat or stairs. Favor the strict walkable-floor layout over scenery density.
```

## 未完成的验收

- 需由整合方接入 Godot，在 640×360 真实场景中检查角色与七类运行时热点的可见性、遮挡、色差和四向行走。当前静态背景不能证明完整可玩性。
- 图像是在高分辨率生成后缩到游戏逻辑尺寸，未逐像素修整；若要求与原生像素角色完全一致，仍需像素修饰与人工视觉批准。
- 中央空地是为现有自由移动和多个热点留出的，实际镜头若显得过空，可以在不侵占坐标的前提下增加地面纹饰。不要将此审查标记为场景视觉验收通过。
