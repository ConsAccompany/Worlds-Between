# 科技区世界地图：引擎视觉接入检查

**状态：可撤回的运行时视觉样板；美术仍未验收。** 来源背景为 [单张概念图](../../game/assets/environments/rpg-2-star-ocean-the-second_scifi-region_world-map-background_m8-concept_20261014-143410-5df78b23.png)。

## 接入

`game/scripts/scifi_world_map.gd` 现在在 640×360 地图区域绘制该背景，替换先前的纯色网格。三处标记、两段路线、目的地按钮、顶部与底部 UI 仍由原脚本绘制在背景上，未改变目的地 ID、坐标、按钮大小或点击逻辑。英文按钮原字号在背景接入后的实机截图中出现顶部文字拥挤，因此把顶部按钮与三处目的地按钮的字号缩小；按钮触发范围未变。删除背景 `preload` 并恢复原 `_draw()` 底图语句即可撤回本次视觉接入。

## 验证

- Godot 4.7.2 资源导入成功，背景纹理保持 1672×941 源尺寸；场景绘制到 640×360 逻辑画面。
- 定向检查脚本 [`game/tests/rpg-2-star-ocean-the-second_scifi-world-map_background-visual-check_m8-v01_20261014-143900-239f6b80.gd`](../../game/tests/rpg-2-star-ocean-the-second_scifi-world-map_background-visual-check_m8-v01_20261014-143900-239f6b80.gd) 在无头和有画面运行均通过。三个目的地按钮的中心/尺寸不变，分别点击后仍进入对应科技区场景。
- [中文实机画面](../../outputs/rpg-2-star-ocean-the-second_scifi-world-map_in-engine-review_m8-v02_20261014-144300-b0dc81ae/rpg-2-star-ocean-the-second_scifi-world-map_in-engine-chinese_m8-v01_20261014-143714-9e3faae6.png) 和 [英文实机画面](../../outputs/rpg-2-star-ocean-the-second_scifi-world-map_in-engine-review_m8-v02_20261014-144300-b0dc81ae/rpg-2-star-ocean-the-second_scifi-world-map_in-engine-english_m8-v01_20261014-143714-b238f4e2.png) 均为 Godot 实际 640×360 捕获；[检查清单](../../outputs/rpg-2-star-ocean-the-second_scifi-world-map_in-engine-review_m8-v02_20261014-144300-b0dc81ae/rpg-2-star-ocean-the-second_scifi-world-map_visual-check-manifest_m8-v01_20261014-143716-6f3c05d3.json)记录按钮与捕获数量。

## 视觉判断与剩余风险

三处深底青绿圆环从城市、林地、遗址背景中分离；浅色直线路线在树冠和岩坡上仍可追踪；按钮深色底可承载中文、英文地名。首轮英文顶部按钮在原字号下互相拥挤，减小字号后第二轮画面已能完整显示“Characters & Jobs”、“Main menu”和“Old civilization ruins”。

地图缩到 640×360 后仍很密，路线与地形交汇处略忙，地名的 11 像素字体也比其他界面小。西侧城市建筑规模偏宏伟，需人工确认是否符合科技板块设定。该视觉检查证明交互未回归及基础可读性，不等于玩家视距、视觉障碍或美术质量的最终验收；资产清单中的地图背景仍应保留待审状态。
