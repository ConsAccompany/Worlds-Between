# 女主角高精度样稿：城市比例复核

**结论：暂以可见高度 48 逻辑像素作为下一轮角色尺寸基准。** 这是静止样稿的场景比例判断，仍需用户美术确认；没有替换正式角色、制作其他方向或调整游戏运行时。

同一张[透明源图](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-exploration-premium-pixel_m8-concept_20261014-145800-62c3a10f.png)在 Godot 科技城市中独立截取。全部使用 `canvas_items` 模式、逻辑画布 640×360、实机输出 1280×720、最近邻人物采样、线性城市场景和独立柔和接地影。源图 alpha≥64 主体顶点为 `y=47`，足底锚点 `(638,1328)` 固定到城市 `(340,253)`；有效源图高度为 `1281px`。

| 可见高度 | 缩放率 | 单独实机画面 |
| --- | ---: | --- |
| 52px | 0.040593 | [52px](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-character-quality-h52-canvas-items_m8-v02_20261014-151019-ba36a56e.png) |
| 56px | 0.043716 | [56px](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-character-quality-h56-canvas-items_m8-v02_20261014-151024-f2e9ec27.png) |
| 60px | 0.046838 | [60px](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-character-quality-h60-canvas-items_m8-v02_20261014-151030-9e2dea41.png) |
| 64px | 0.049961 | [64px](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-character-quality-h64-canvas-items_m8-v02_20261014-151035-810be0e2.png) |

前四张捕获隐藏了梁序，因此增加两个**同一脚点高度的梁序对照**：[48px 女主与梁序](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-character-quality-h48-canvas-items-with-liang_m8-v02_20261014-151442-b75b310e.png)、[52px 女主与梁序](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-character-quality-h52-canvas-items-with-liang_m8-v02_20261014-151401-81330838.png)。每张图旁有同名 JSON，记录画布尺寸、缩放率、脚点和透明度检查。

视觉判断：64px 明显压过附近店门、候车设施与街景；60px 仍偏醒目；56px 的发型和围巾很清楚，但在该城市里人物仍显偏大。52px 兼顾细节与比例，不过与同脚点梁序并排时还略显突出。48px 的高侧马尾、面部和茶绿色围巾仍可辨，身高与门、市政设施及梁序更协调。48px 的比例约为 `48/1281 = 0.0374707`，在 1280×720 输出中约高 96 物理像素。

梁序当前仍是旧的低精度角色，他的造型和可见高度不能直接当作全队最终标准。正式锁定前应让男女主和至少一名高精度伙伴在相同脚点并排、同样光照下复核，检查行走动画及低亮度场景。源图边缘有少量低 alpha 像素，缩小时应特别检查深色地面上的暗晕。
