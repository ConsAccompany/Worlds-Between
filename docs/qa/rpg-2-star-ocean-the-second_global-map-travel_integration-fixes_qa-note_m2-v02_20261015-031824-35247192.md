# 全球地图与旅行核心整合修正检查（M2）

状态：**整合缺口已修正，自动测试与实机截图检查通过；M2 全球地图与旅行仍未最终验收**。路线数值仍为初步估算，没有门到门附加时间，也没有航空路线。地图美术未验收，未经真人试玩。核验日期：2026-10-15。

本次修正针对两个工作流在同一工作区分别完成的两份成果：[地图实机实现](rpg-2-star-ocean-the-second_global-earth-map_runtime-implementation_qa-note_m2-v01_20261015-024300-15ce9195.md)与日历路线核心。该说明中关于“待用户确认”标签、5 km 坐标容差和无核心时“进入（不计旅时）”的描述，以本文为准。

## 修正内容

### 1. 游戏画面不再显示制作状态与资料来源

地图字串见 `game/scripts/world_map_text.gd`，下列文字已从游戏画面移除：

| 位置 | 旧文字 | 现文字 |
|---|---|---|
| 标题 | 全球地图 · 科技板块试玩 / …Science region demo | 全球地图 · 科技板块 / Global map · Science region |
| 全球层图例 | 可玩：科技板块 · 自然／奇幻／魔法板块地点待定 | 可前往：科技板块 · 其他板块尚未开放 / Open: Science region · other regions not yet open |
| 地图左下角说明 | 底图：Natural Earth 地理数据 · 表层美术未验收；海岸 Natural Earth 50m · 道路为概略几何… | 整行删除 |
| 路线卡类型 | 真实城市 · 暂定首城 · 待用户确认 等 | 城市／城郊／世界遗产 · 遗址（City / Outskirts / World Heritage · ruins） |
| 杭州参照点 | 杭州 Hangzhou (参照) | 杭州 Hangzhou |
| 未开放路线 | 这条路线尚未核实… / 另有路线尚未核实… | 目前没有可用路线。／另有路线暂不可用。 |

`app_state.gd` 里没有地方使用的 `map_help` 原写“全球地图与旅时功能更新中”，也一并改为中性文字。真实地名（上海、松江郊外／上海市松江区、良渚古城遗址及英文通名）照旧显示。旅时估算标记保留并写得更明确：“里程与旅时为估算” / “estimated distance and time”。制作状态与资料来源仍记录在 Game Bible、数据文件和 QA 文档中，画面上不声称美术已验收。

### 2. 不存在不计旅时的跨地点路径

- 路线 API 缺失或签名不符时，前往其他地点的路线卡显示“暂时无法查询路线，现在不能出发。”，按钮为灰色的“无法出发／Cannot depart”，不显示数字。`depart()` 中“不计旅时进入”的分支已删除，即使直接调用也不会换场景，也不扣时间。
- 适配器新增 `api_problems()`，逐项列出缺少的属性或方法和参数个数不符之处。地图启动时若有问题，会用 `push_warning` 写入开发日志；这条信息不显示给玩家。
- 队伍所在地仍可免费进入：有 API 时调用 `enter_current_location_scene()`；没有 API 时只重新选择当前所在场景，不移动队伍。
- 地图本身不再调用 `select_destination()`。场景只能由核心选定：确认出发时由 `settle_travel` 选定，进入所在地时由 `enter_current_location_scene` 选定。地图的 `_enter_scene()` 只在 `AppState.current_destination_id` 与目标一致时才切换场景。
- 核心拒绝出发时（例如预览已过期），路线卡显示“出发未完成，未扣除时间。”并禁用按钮。这一状态保存为 `failed`，切换语言后提示仍在。

### 3. 只用一份地点坐标与名称

- 地图登记表 `game/data/world-map/…_place-registry_m2-v01_…-36903495.json`（schema 升为 v2）的 `places` 只保留显示字段：`id`、`kind`、`board_id`、`geo_region_id`、`label_side`。经纬度、名称、行政名、场景入口、发现条件和来源都已删除。
- 每个标记的坐标、名称、行政名和场景入口都取自全球旅行数据 `game/data/world-travel/…-b876e53d.json`。有 API 时通过 AppState 读取；API 不可用时，`world_map_data.gd` 的 `travel_data()` 直接读取同一文件。原先的 5 km 容差检查改为严格相等：标记必须等于 `app.travel_location(id)` 的坐标。核心里的地点若在地图登记表中没有显示条目，会 `push_error`，不会被悄悄隐藏。
- 稳定 ID 不变：`earth.cn.shanghai`、`earth.cn.shanghai.songjiang-outskirts`、`earth.cn.liangzhu-ruins`。三处地点仍是暂定。现在的标记坐标是核心坐标：上海 31.22222°N 121.45806°E（GeoNames 1796236），松江 31.00583°N 121.23333°E，良渚 30.39556°N 119.99083°E。
- 杭州只是不可选的参照点，不是旅行地点，仍保留在地图登记表中，并附自己的来源。

### 4. 出发、取消、进入与存档迁移

新增回归测试 `game/tests/rpg-2-star-ocean-the-second_global-map-travel_integration-regression_m2-v02_20261015-031232-786a054d.gd`（103 项检查），在真实地图场景里按路线卡按钮操作：

- **确认出发**：连按三次“出发”（两次按钮信号加一次直接调用），只产生 1 次 `travel_completed` 和 1 次 `calendar_advanced(start, start+分钟, "travel")`，区域场景只载入 1 次，时钟只增加所选路线的分钟数。
- **取消**：“取消”按钮、Esc 以及在不同地点之间切换选择，都不扣时间、不改变地点，并清空预览。
- **进入所在地与再次进入**：连续进入、返回 3 次，0 分钟，没有旅行事件。
- **存读档**：读档两次再打开地图，没有日历或周结算事件。地图的出发地与日期跟随存档。读档后再出发，只计这一次的旅时。
- **旧存档**：存档没有 `travel` 区块，场景为城郊，游戏时间 25 小时。读档后日期为日历起点，没有凭空增加的天数，也不触发周结算。地图出发地为松江，进入免费。
- **API 签名不符**（`confirm_travel` 多一个参数）：中英文都禁止出发，显示说明，不显示数字。按“出发”不改变任何状态，只能免费进入所在地。
- **核心拒绝出发**：只尝试一次，不扣时间，不换场景，提示经语言切换仍保留。
- **画面文字**：全球层、地区层、三张路线卡和无 API 路线卡（中英文）的可见文字里，都没有“待用户确认、未验收、试玩、待定、暂定、待制作、未核实、不计旅时、Natural Earth、50m、GeoNames、Rome2Rio、UNESCO、demo、provisional、pending”等字样。有路线时必须带估算标记。
- **静态检查**：在 `game/scripts/` 的游戏脚本里，只有 `app_state.gd` 和地图适配器（仅用于无 API 时重新选择当前场景）调用 `select_destination(`，其他游戏脚本也不直接给 `current_destination_id` 赋值。以 `extends SceneTree` 开头的命令行截图工具不在检查范围内。

为确认测试真能抓到问题，做了两次变异测试：把“暂定首城”加回类型文字，以及让无 API 时“出发”可按。两次都使测试失败，之后已逐字节还原。

`m2_smoke.gd` 改为点地点、看路线卡、连按两次“出发”。每次进入都检查：去其他地点只扣所选路线的分钟数一次，进入所在地或再次进入扣 0 分钟。

**下游检查**：其他游戏脚本中没有直接调用 `select_destination()` 的路径。`hero_setup.gd`、`party_talk.gd`、`demo_report.gd`、`scifi_exploration_area.gd` 只回到地图场景；`survey_annex.gd` 与 `battle_arena.gd` 只读取当前场景。M3–M8 和视觉截图测试里的 `app.select_destination(...)` 都是测试准备步骤，保留不改。`select_destination()` 仍是公开方法，供核心和测试使用；有了静态检查，游戏脚本不能绕过旅行结算。

### 5. 路线数值如实保留为估算

路线数据未修改：上海—松江汽车 34.8 km、26 分钟；上海—良渚汽车 187.9 km、120 分钟；松江—良渚经上海 146 分钟。三者均为 Rome2Rio 地点到地点的初步估算，`doorToDoorAllowanceMinutes` 为 0。松江—良渚直达路线仍为未核实，不可选。数据中没有航空路线，本次也没有编造。截图期间另一工作流新建了 `docs/design/…_shanghai-cross-city-air-route_research-packet_unapproved-v01_20261015-031235-9d63971b.md`，本次没有读取，也没有并入数据。首城与游戏开始年份都未决定，日历起点 2026-04-01 08:00 仍是数据中注明的工程占位值，本次未改动。

## 接口约定（地图 ↔ AppState）

适配器 `world_map_route_adapter.gd` 的 `REQUIRED_METHODS` 未变，参数个数必须完全一致：

| AppState 成员 | 参数个数／类型 | 地图用途 |
|---|---|---|
| `current_location_id`、`current_destination_id`、`calendar_minutes` | 属性 | 出发地、场景、日期 |
| `travel_location_ids(region_id)` | 1 | 已发现地点列表（地图传入 `""`） |
| `travel_location(id)` | 1 | `coordinates.lat/lon`、`names`、`administrativeName`、`sceneDestinationId`、`type` |
| `travel_location_name(id)` | 1 | 途经地名称 |
| `travel_route_options(from, to)` | 2 | 路线选项（snake_case 键） |
| `travel_arrival_preview(minutes)` | 1 | 抵达日期与时刻文字 |
| `preview_travel(to, option_id)` | 2 | 选定路线的预览，只改动待定预览 |
| `cancel_travel_preview()` | 0 | 取消 |
| `confirm_travel(to, option_id)` → bool | 2 | 一次性结算并选定目的地场景 |
| `enter_current_location_scene()` → bool | 0 | 免费进入所在地 |
| `calendar_date_text_at`、`calendar_time_text_at`、`travel_duration_text` | 各 1 | 文字格式 |

参数个数或类型若有改动，`api_available()` 会变为 false，所有前往其他地点的出发都被禁用（不会再退回不计时进入），开发日志会写明不符的方法。新增旅行地点时，须在地图登记表中加一条只含显示字段、ID 相同的条目。

## 改动的文件

- `game/scripts/scifi_world_map.gd`：删除不计时分支和说明行；新增 `_enter_scene`、`_show_departure_failed` 和 `failed` 状态；无 API 时开发日志写警告。
- `game/scripts/world_map_route_adapter.gd`：坐标只来自核心数据；新增 `api_problems()`；无 API 时 `confirm` 拒绝出发，`enter_here` 只进入所在地。
- `game/scripts/world_map_data.gd`：新增 `display_places()`、`display_place()`、`travel_data()`；删除带坐标的 `places()`、`place()`、`place_for_destination()`；`places_in_region`、`region_places_bbox` 改为必须传入地点。
- `game/scripts/world_map_text.gd`：玩家可见字串。
- `game/scripts/app_state.gd`：只改了没有地方使用的 `map_help` 中英文两行。
- `game/data/world-map/…_place-registry_m2-v01_…-36903495.json`：只保留显示字段。
- `game/tests/m2_smoke.gd`、`game/tests/…_global-earth-map_smoke_m2-v01_…-7b4550d6.gd`、`game/tests/…_global-earth-map_visual-capture_m2-v01_…-9b2fac94.gd`：改为新的交互方式和单一坐标来源。
- 新增 `game/tests/…_global-map-travel_integration-regression_m2-v02_20261015-031232-786a054d.gd`。
- Godot 导入为本工作流的地图脚本和测试生成了 `.uid`：`world_geo_projection`、`world_map_data`、`world_map_route_adapter`、`world_map_text`、两份地图测试及新测试。导入也为其他工作流的三份测试脚本重建了 `.uid`（`south-locomotion-v2-capture`、`sentry…battle-check-capture_m8-anim-v02`、`sentry…v1-runtime-entry-helper`），已删除。

## 实际执行的命令与结果（2026-10-15）

以下命令都在仓库根目录运行，`G=work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe`。最后一处代码修改之后，全部重跑一遍，结果如下：

```text
$G --headless --path game --import                                                      → exit 0，0 个错误
$G --headless --path game --script res://tests/rpg-2-star-ocean-the-second_global-earth-travel_calendar-route-core-smoke_m2-v01_20261015-024215-a19d5ae7.gd → GLOBAL_TRAVEL_CORE_OK
$G --headless --path game --script res://tests/rpg-2-star-ocean-the-second_global-earth-map_smoke_m2-v01_20261015-024300-7b4550d6.gd → GLOBAL_EARTH_MAP_SMOKE_OK checks=201
$G --headless --path game --script res://tests/rpg-2-star-ocean-the-second_global-map-travel_integration-regression_m2-v02_20261015-031232-786a054d.gd → GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=103
$G --headless --path game --script res://tests/m1_smoke.gd  → M1_SMOKE_OK      （m2_smoke → M2_SMOKE_OK，m3 → M3_SMOKE_OK，m4 → M4_SMOKE_OK，m5 → M5_SMOKE_OK）
$G --headless --path game --script res://tests/m6_smoke.gd  → M6_SMOKE_OK      （m6_restart_smoke → M6_RESTART_OK，m7_smoke → M7_SMOKE_OK）
$G --headless --path game --script res://tests/m8_city_integration_smoke.gd → M8_CITY_INTEGRATION_OK（m8_city_navigation_smoke → M8_CITY_NAVIGATION_OK，m8_city_reentry_smoke → M8_CITY_REENTRY_OK）
$G --path game --script res://tests/rpg-2-star-ocean-the-second_scifi-canvas-pointer-regression_m8-v01_20261014-195000-6e24b8a1.gd → CANVAS_POINTER_REGRESSION_OK（有窗口，1280×720 真实像素点击）
$G --path game --script res://tests/rpg-2-star-ocean-the-second_global-earth-map_visual-capture_m2-v01_20261015-024300-9b2fac94.gd → GLOBAL_MAP_CAPTURE_OK 12
git diff --check → exit 0
```

上述各项退出码均为 0，日志中没有 `ERROR` 或 `SCRIPT ERROR`。m5、m6_restart、m8_city_integration、m8_city_reentry 偶尔在退出时出现“ObjectDB instances leaked”警告。用 `--verbose` 查看，泄漏对象是战斗音效的 `AudioStreamWAV` 和 `AudioStreamPlaybackWAV`，与地图和旅行无关，并非每次都出现。

指针回归测试的凭据：`outputs/rpg-2-star-ocean-the-second_scifi-canvas_pointer-regression-receipt_m8-v01_20261015-071805-548c0f0f.json`。点击上海标记（窗口像素 757, 176），再点路线卡“进入场景”（998, 528），进入城市场景。

## 实机截图（1280×720，未验收）

截图运行编号为 `m2-v02_20261015-031426-9a107595`，文件位于 `outputs/rpg-2-star-ocean-the-second_global-earth-map_<名称>-runtime-capture_m2-v02_20261015-031426-9a107595.png`。中英文各 6 张：`globe`、`yangtze-delta`、`yangtze-delta-liangzhu-card`、`yangtze-delta-songjiang-card`、`yangtze-delta-shanghai-here-card`、`yangtze-delta-liangzhu-no-route-api-card`，名称后加 `-zh` 或 `-en`。

逐张查看的结果：

- 没有文字被截断或越出画框。英文良渚卡片的标题占两行，估算说明行仍完整显示在按钮上方。
- 卡片显示真实地名、行政名、类型、经纬度、出发地、“汽车 · 公路 187.9 km · 2小时”、抵达日期时刻和估算标记。
- 无 API 卡片显示说明，“无法出发”为灰色。所在地卡片显示“进入场景”。
- 画面上没有制作状态或资料来源文字。
- 小问题（原有，未修改）：卡片背景不透明度为 0.96，地区层右侧的“31°N”“122°E”网格标注在卡片后面隐约可见。

## 仍未完成的关卡

1. **M2 最终验收未完成**：路线是 Rome2Rio 地点到地点的初步估算，没有门到门附加时间，反向行程按对称假设，未核实；没有航空路线，所以飞机模式和“飞机＋汽车”只用测试夹具检查过格式。
2. 首城、地下社区的地理锚点和游戏开始年份都等用户决定。上海、松江、良渚仍是暂定组合；日历起点是工程占位值。
3. 地图表层美术未验收，未经真人试玩。截图只是运行证据。
4. M7 结束报告的标题仍为“科技板块试玩完成”。它不在地图上，不属于本次范围，是否改动交给对应工作流决定。
5. 项目还没有导出预设。将来建立时，需要把 `game/data/**/*.json` 加入非资源文件筛选。
6. 静态检查只扫描 `game/scripts/`。将来若在其他目录加游戏脚本，需要扩大检查范围。
