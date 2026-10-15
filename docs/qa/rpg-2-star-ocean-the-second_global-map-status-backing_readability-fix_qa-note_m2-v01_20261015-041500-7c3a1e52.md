# 全球地图左上角状态行可读性修正（M2）

状态：**小修正已完成，自动检查与 1280×720 实机截图检查通过；M2 全球地图与旅行仍未最终验收**。地图美术未验收，未经真人试玩。核验日期：2026-10-15。

## 问题

`outputs/rpg-2-star-ocean-the-second_global-earth-map_globe-en-runtime-capture_m2-v02_20261015-031426-9a107595.png` 中，全球层左上角的状态行 “Open: Science region · other regions not yet open” 直接压在格陵兰、北美海岸线和经纬网上，只靠 3 px 描边与底图区分，显得拥挤、不易读。地区层同一位置显示的地区名（如 “长江三角洲 · Yangtze River Delta”）也有同样的问题。

## 修正（只改 `game/scripts/scifi_world_map.gd`）

1. 状态行（`legend_label`）改放进一个新的 `StatusBacking` 面板（`PanelContainer`），位置在地图局部坐标 (6, 4)：
   - 底色用已有的 `COLOR_LABEL_BG`（与地点标签底色相同，透明度 0.88），1 px 边框 `#25404b`（与实地日志面板相同），左右内边距 5 px、上下 1 px；
   - 面板宽度贴合文字，不铺满整行，全球视图仍然完整可见；文字超过 264 px（基准分辨率）才自动换行，目前中英文都是一行；
   - 字号、颜色、描边与修正前相同，文案没有改动。
2. 地区层的经度标签（如 120°E）原来基线在 y=26，会与新面板相交，现在整排下移到面板下方（基线约 y=30），所有经度标签照常显示。其他标注标签若落在面板下面，这一帧不画（与路线卡的处理方式一致）。
3. 新增 `status_rect()` 供测试读取面板范围。
4. 保留上一次路线卡修正：路线卡仍为不透明，31°N/30°N 仍移到卡片左侧，122°E、123°E 在卡片打开时仍不显示。
5. 没有改动：路线登记表、游戏数据、Game Bible、路线 API、预览／确认／取消流程、标记坐标、美术验收计数、其他玩法。

## 测试

新增 `game/tests/rpg-2-star-ocean-the-second_global-map-status-backing_readability-check_m2-v01_20261015-041500-2d7e93b1.gd`（需显示渲染器，不加 `--headless`；`M2_STATUS_CAPTURE_DIR` 可改截图目录）。中英文各检查 5 个画面：全球层、全球层放大 2 倍、地区层、地区层打开良渚路线卡、地区层放大 2.5 倍。每个画面检查：

- 状态行在面板内，面板按最小尺寸排版，宽度不超过上限，高度为一行（≤ 20.5 px）；
- 面板不碰缩放按钮、“全球／地区” 按钮、日历、可见的地区或地点标记，也不碰路线卡区域；
- 地区层所有度数和参照地名标签都不在面板下，且仍有经度标签显示；
- **像素比对**：同一画面渲染两次，一次正常，一次隐藏地图各层（底色、陆地、经纬网、海岸线、道路），面板范围内每个像素的通道变化不得超过 0.14，也就是底图只能留下很淡的色调；
- 路线卡背景仍为不透明（透明度 1.0）。

结果：**185 项全部通过**（`STATUS_BACKING_READABILITY_OK 185 checks`）。

变异检查：临时把面板底色改成全透明后重跑，面板透明度检查和全部 10 个像素比对都失败（底图造成的最大通道变化 0.68 至 0.72），确认这项测试能抓到回退；之后已恢复原文件并核对一致。

回归（Godot 4.7.2）：

| 测试 | 结果 |
|---|---|
| `m2_smoke.gd`（`--headless`） | `M2_SMOKE_OK` |
| 全球地图 smoke m2-v01（`--headless`） | `GLOBAL_EARTH_MAP_SMOKE_OK checks=201` |
| 全球地图旅行整合回归 m2-v02（`--headless`） | `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=103` |
| 日历路线核心 smoke m2-v01（`--headless`） | `GLOBAL_TRAVEL_CORE_OK` |
| 导出数据包含 smoke m2-v01（`--headless`） | `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24` |
| 路线卡可读性检查 m2-v01（显示渲染） | `ROUTE_CARD_READABILITY_OK 99 checks` |

## 截图（1280×720，未验收的实机证据）

`outputs/rpg-2-star-ocean-the-second_global-map-status_<画面>-readability-capture_m2-v01_20261015-034738-cbfe63b8.png`，共 10 张：`globe-zh/en`、`globe-zoomed-zh/en`、`region-zh/en`、`region-card-zh/en`、`region-zoomed-zh/en`。

逐张查看的结果：

- 全球层：“Open: Science region · other regions not yet open” 和 “可前往：科技板块 · 其他板块尚未开放” 都在深色面板上，一行显示，清楚可读；海岸线和经纬网不再穿过文字。面板只占左上角一小块，世界地图其余部分不受影响。
- 地区层：“长江三角洲 · Yangtze River Delta” / “Yangtze River Delta · 长江三角洲” 在同样的面板上；119°E、120°E、121°E 一排显示在面板下方，没有被盖住。
- 打开路线卡时：卡片仍不透明，内容与上一次修正后的截图一致，31°N、30°N 仍在卡片左侧。

## 已知、未处理（不在本次范围）

- 右下角日历文字（“Apr 1, 2026 08:00”）同样直接压在地图上，没有底色。
- 地区层放大 2.5 倍时，“松江郊外” 地点标签被地图上缘截掉一半（标签贴着地图框上边）。标记排版代码本次未改，与状态面板无关；没有另外截修正前的同一画面对照。
- 换行分支（文字超过 264 px）目前没有任何文案会触发，测试只能确认现有中英文为一行，没有实际看到换行效果。
