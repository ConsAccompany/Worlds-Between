# M8 男主东／北向概念图实机 QA（48px，待美术验收）

在科技城市真实 Godot 场景中，临时用 `canvas_items` 以 1280×720 渲染，把男主东向和北向候选各自显示为约 **48 逻辑像素**。两张截图是独立的画面；每次只载入一个候选，并将旧版梁序放在同一地面 y=253 的右侧供尺度参照。游戏运行时角色、注册表、项目设置均未由此检查替换。

| 方向 | 原始透明候选 | 独立城市截图 | 渲染收据 |
|---|---|---|---|
| 南，既有参照 | [南向 v2 PNG](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-male_south-exploration-premium-pixel_m8-v02_20261014-190703-746cf39d.png) | [48px 南向实机](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-male-v2-character-quality-h48-canvas-items-with-liang_m8-v02_20261014-151710-7a499c3e.png) | [南向 JSON](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-male-v2-character-quality-h48-canvas-items-with-liang_m8-v02_20261014-151710-7a499c3e.json) |
| 东，新候选 | [东向 PNG](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-male_east-exploration-premium-pixel_m8-concept_20261014-151920-62113512.png) | [48px 东向实机](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-male-east-character-quality-h48-canvas-items-with-liang_m8-v02_20261014-152544-bf0ba265.png) | [东向 JSON](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-male-east-character-quality-h48-canvas-items-with-liang_m8-v02_20261014-152544-bf0ba265.json) |
| 北，新候选 | [北向 PNG](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-male_north-exploration-premium-pixel_m8-concept_20261014-152100-3feba4fb.png) | [48px 北向实机](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-male-north-character-quality-h48-canvas-items-with-liang_m8-v02_20261014-152550-387385f9.png) | [北向 JSON](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-male-north-character-quality-h48-canvas-items-with-liang_m8-v02_20261014-152550-387385f9.json) |

## 检查结果

- 三张候选均为 `1145×1374` RGBA，四角 alpha=0；以 alpha≥64 量得东向强可见边界 `(258,35)–(799,1340)`，北向 `(319,27)–(913,1315)`，均未碰画布边。东向脚点使用 `(640,1340)`，北向 `(590,1315)`，与南向 `(575,1352)` 一样落到城市 `(340,253)`。三向源身高与缩放率相近（约 0.0368–0.0373 逻辑倍数），故头顶／脚底在实机画面上基本齐平。两张新截图均验证为实际 `1280×720`；Godot 运行退出码 0。
- 两张 JSON 中的“低于 52–80px”是截图时检查脚本旧版尺度提示；随后按用户选定的较小比例更新了诊断范围。它不代表 PNG 或渲染失败。
- 东向确实侧看右方，轮廓比南向窄；散层短发、茶绿围巾、棕灰外套、背卷和金属水壶仍能辨认。北向的短发后层、横向背卷、背包、水壶及右侧围巾尾是明确的背影线索。装备在方向之间总体连贯，北向背包也没有把整个头肩轮廓遮成一个暗块。
- 48px 比先前 72px 更接近现有街道与建筑入口的画面比例。现有梁序仍是约 42px 高、低细节的旧原生图，两人的质感不一致；这证明后续伙伴也须统一升级，不能把这两张独立概念图直接接进运行场景当成完整角色组。

## 尚未解决

1. 东向末端头发与靴子的小纹理在 48px 下几乎不可读；北向主要靠背卷和围巾色块识别，人物自身服装纹理在繁密铺地上变弱。是否达到目标画质仍需用户在实际游戏中判断。
2. 源 PNG 有低透明度边缘像素（东约 22,492、北约 29,744）；当前明亮街面未出现明显矩形暗底，但必须再在深色建筑、树阴和其他板块检查晕边。图像的高分辨率细节、短发层与服饰皱褶仍未经过逐帧统一处理。
3. 东、北、南三向只是静态立绘概念。缺西向和四方向待机／行走帧；朝向切换时围巾尾、背卷、水壶、肩带与脚点必须稳定。上方俯视场景与立绘近乎平视的视角差，也需通过连续移动实测。

**结论：**东／北两张是可用于下一轮四向风格审查的概念候选，**不是批准的游戏精灵**。本次只做画质与比例 QA，没有运行时接入、动画制作或美术验收。
