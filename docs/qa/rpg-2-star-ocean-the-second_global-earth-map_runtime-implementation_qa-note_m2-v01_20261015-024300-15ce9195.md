# 全球地球地图实机实现检查（M2）

状态：**Godot 实机地图与地理投影已实现，自动测试通过；地点仍为暂定，地图表层美术未验收，未经真人试玩**。这些结果不能算作视觉验收或 M2 全部完成，日历与路线核心由另一工作流负责。核验日期：2026-10-15。

## 实现内容

- `game/scripts/scifi_world_map.gd` 改写为全球地图。旧版虚构三角布局和旧区域背景已不再使用。地图分两层，共用一套缩放与平移：
  - **全球层**：等距圆柱投影（plate carrée）。最小缩放时可看到经度 −180°～180°、纬度 −90°～90° 的完整地球，陆地为 Natural Earth 110m。
  - **长江三角洲地区层**：等距圆柱投影，标准纬线 30.8°N。底图为 Natural Earth 50m 陆地和 10m 概略道路，另有经纬网和比例尺。比例尺按投影计算，只在经线方向和标准纬线上准确。
  - 用滚轮、触控板缩放手势或 ＋／－ 缩放，拖动平移。在全球层放大到上限时，若光标靠近该地区，就进入地区层；在地区层缩小到下限时回到全球层，并定位在该地区。另有“全球”“长江三角洲”两个直达按钮，点全球层的地区标记也能进入地区层。
- 地区层有三个可选地点：上海、松江郊外、良渚古城遗址。杭州只作参照点，不能选择。标签同时显示当前语言名和另一语言名，越出画框时会换边。地图上没有角色，也不能步行。
- 选中地点后打开路线卡，显示真实地名、行政名、类型、“待用户确认”、经纬度和出发地。下列内容全部取自 AppState 的路线 API，地图不计算任何数字：交通方式、公路／航程里程、总旅时、抵达日期与时刻、途经地、“参考估算”标记。未核实的路线只提示“未核实”，不显示数字，“出发”按钮也会禁用。当前所在地显示“进入场景”，不花时间。“取消”和 Esc 会调用 `cancel_travel_preview()`，不扣时间。
- 实地日志、存档、角色与职业、主菜单、实地状态栏、伙伴对话入口都保留。Esc 依次关闭实地日志、路线卡，然后回主菜单。
- 科技板块是唯一可玩的板块。登记表里还有自然、奇幻、魔法板块（`location_pending`，没有坐标）和星外板块（`portal_only_not_on_earth_map`），全球层的说明也写明“地点待定”。地图没有虚构任何其他地点。

## 新文件

| 文件 | 作用 |
|---|---|
| `game/scripts/world_geo_projection.gd` | 投影、反投影、视图缩放／平移／限位、按经纬框取景、大圆距离（只用于测试的合理性检查，不显示在界面上） |
| `game/scripts/world_map_data.gd` | 读取地点登记表和运行时地理数据，判断点是否在陆地上 |
| `game/scripts/world_map_route_adapter.gd` | 连接 AppState 路线核心；方法缺失或参数个数不符时退回“待接入”，不显示数字 |
| `game/scripts/world_map_text.gd` | 地图专用的中英文字串 |
| `game/data/world-map/…_earth-map_place-registry_…-36903495.json` | 地点呈现字段（标签方位、所属地区）、板块结构、地区视图范围，以及后备坐标及其来源 |
| `game/data/world-map/…_earth-map_runtime-geodata_…-2595ada6.json` | 110m 全球陆地 128 个环；50m 陆地按 115–127°E、27–35°N 裁剪后的 11 个环；道路 623 条。sha256 `500c5a12…b9be49` |
| `tools/…_earth-map_runtime-geodata-build_…-7ef4d180.gd` | 从 `assets/reference/geography/` 重建上项数据（坐标取整到 0.001°，用 Godot Clipper 裁剪）。重跑后输出逐字节相同 |
| `game/tests/…_global-earth-map_smoke_…-7b4550d6.gd` | 无头冒烟测试 |
| `game/tests/…_global-earth-map_visual-capture_…-9b2fac94.gd` | 1280×720 实机截图 |

运行时地理数据里记录了三份来源文件的 `sha256-text-lf-v1`。110m 来源的散列为 `9e0729ee…2835d9`，与[全球样稿检查](rpg-2-star-ocean-the-second_global-atlas_geography-grounded-visual-study_qa-note_unapproved-v02_20261015-001640-5b0c8af7.md)记录的一致。

## 坐标来源

接入路线核心后，地点的坐标、名称和场景入口都以核心数据 `game/data/world-travel/…` 为准，地图登记表只在核心不可用时作后备。两份坐标都有出处，但来源点不同：上海相差 2.27 km（Natural Earth 与 GeoNames 1796236），松江相差 3.32 km（GeoNames 镇点与区参考点），良渚相差 0.05 km（两者都用 UNESCO 城址分区点）。冒烟测试要求两者相差小于 5 km，且场景入口一致。地图点只用于浏览，不是场景门口。

## 实际 QA 结果（2026-10-15）

命令都在仓库根目录运行，引擎为 `work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe`。

- `--headless --path game --script res://tests/…_global-earth-map_smoke_m2-v01_20261015-024300-7b4550d6.gd` → `GLOBAL_EARTH_MAP_SMOKE_OK checks=193`，`route core API available: true`。检查范围：
  - 全球最小缩放覆盖整个地球；投影往返；缩放时光标下的点不动；
  - 来源散列；全部全球环可以三角化；三处地点在 50m 陆地上，东海和太平洋采样点在海上；
  - 滚轮缩放进入地区层；标签在画框内、互不重叠；方位关系为松江在上海西南、良渚更偏西南；屏幕距离与地面距离相差小于 6 km；
  - 路线卡显示公路里程、旅时和抵达日期；取消后时间、地点和预览都不变；
  - 退回旧版提供者时不显示数字；测试专用夹具验证了飞机加汽车的格式和未核实路线（夹具数值不进游戏）；
  - 中英文名称；实地日志、角色与职业、存档的往返；
  - 当前地免费进入；去松江只扣一次核心给出的分钟数；缩小后回到全球层。
- `m2_smoke.gd`（已改为“选地点 → 出发”）→ `M2_SMOKE_OK`。
- `m1_smoke`、`m3_smoke`、`m4_smoke`、`m5_smoke`、`m6_smoke`、`m6_restart_smoke`、`m7_smoke`、`m8_city_integration_smoke`、`m8_city_navigation_smoke`、`m8_city_reentry_smoke` 全部退出码 0，并输出各自的 OK 标记。
- 指针回归测试 `…_scifi-canvas-pointer-regression_m8-v01_…-6e24b8a1.gd`（有窗口，真实 1280×720 窗口像素点击）→ `CANVAS_POINTER_REGRESSION_OK`。旧版写死了城市按钮坐标，现在改为点击地区标记、上海标记，再点路线卡里的按钮，并保留“未缩放坐标必须点空”的检查。
- 引擎渲染截图（1280×720，未验收）：[全球·中文](../../outputs/rpg-2-star-ocean-the-second_global-earth-map_globe-zh-runtime-capture_m2-v01_20261015-030226-8c4f01d1.png)、[长江三角洲·中文](../../outputs/rpg-2-star-ocean-the-second_global-earth-map_yangtze-delta-zh-runtime-capture_m2-v01_20261015-030226-8c4f01d1.png)、[良渚路线卡·中文](../../outputs/rpg-2-star-ocean-the-second_global-earth-map_yangtze-delta-liangzhu-card-zh-runtime-capture_m2-v01_20261015-030226-8c4f01d1.png)、[松江路线卡·英文](../../outputs/rpg-2-star-ocean-the-second_global-earth-map_yangtze-delta-songjiang-card-en-runtime-capture_m2-v01_20261015-030226-8c4f01d1.png)、[全球·英文](../../outputs/rpg-2-star-ocean-the-second_global-earth-map_globe-en-runtime-capture_m2-v01_20261015-030226-8c4f01d1.png)。截图里的里程、旅时和日期是截图当时核心数据给出的值，不是地图写入的。

## 限制与未完成

- **视觉未验收**：配色、标签框和道路粗细都是功能占位，没有按本作像素美术定稿，也没有在真人试玩中检查过可读性。
- Natural Earth 陆地数据不挖出湖泊，所以太湖等内湖显示为陆地。道路是概略几何，没有路名，也不是路线图。地区层只覆盖 115–127°E、27–35°N。
- 只有长江三角洲一个地区层。其他板块的地点和地区层要等用户选址后，在登记表和构建工具里加入。
- `…_scifi-world-map_background-visual-check_m8-v01_20261014-143900-239f6b80.gd` 检查的是已被取代的旧三点背景和按钮坐标，按设计不再适用，本次没有修改，也没有运行。
- 项目还没有导出预设（`game/export_presets.cfg`）。将来建立时，需要加入 `*.json` 非资源文件筛选，地图数据才会打包。
- 键盘只能在按钮之间移动焦点，不能平移地图。
