# 科技区真实地点试点：上海—松江—良渚

状态：**研究与美术方向，尚未进入游戏数据或实机**。上海是用户尚未确认首城时的暂定锚点；换首城时替换这一组路线，不改变全球地图与旅行规则。核验日期：2026-10-15。

## 地点身份

| 原三地点的功能 | 暂定地图名称（中 / 英） | 地理身份 | 游戏处理 |
|---|---|---|---|
| 科技城 | 上海 / Shanghai | 真实城市 | 科技板块首个可玩城市；城市里的导师、商会和调查机构可用架空名称。现实上海的当前政治、建筑和日常制度不直接等于重启后的游戏社会。 |
| 城外通道 | 上海市松江区 / Songjiang District, Shanghai | 上海的真实行政区，**不是另一座城市** | 可作为城郊场景的地理锚点；地图标签可写“松江郊外 / Songjiang Outskirts”，其中“郊外”是场景类型。松江位于上海西南，公路可达。[松江区政府](https://english.songjiang.gov.cn/facts/location/) |
| 旧文明遗址 | 良渚古城遗址 / Archaeological Ruins of Liangzhu City | 杭州地区的真实世界遗产地 | 地图使用真实遗址全名；场景内仍可有架空的调查站、采集机器与前文明线索。[联合国教科文组织](https://whc.unesco.org/en/list/1592/) |

这三个点**不能**继续在一张虚构的区域风景画上按等边三角形摆放。全球地图需先给出真实地理位置和缩放，再让玩家查看上海周边的道路与目的地。旧地图仍可作为历史原型截图，不能充当新规则的完成证据。

世界底图可使用 [Natural Earth 的地理矢量资料](https://www.naturalearthdata.com/downloads/)作为准确海岸线与陆地轮廓基础，再另绘符合本作视觉语言的表层。其官方[使用条款](https://www.naturalearthdata.com/about/terms-of-use/)将站内矢量及栅格地图数据列为公有领域。全球总览可选 1:110m 的简化数据，放大到地区时切换更高精度数据；**地图图像生成器不能替代地理坐标与海岸线数据**。道路和行车分钟仍须单独核对，不能从 Natural Earth 底图线条直接推算。

已制作两张**分开的未验收视觉稿**：[全球总览](../../outputs/rpg-2-star-ocean-the-second_global-atlas_geography-grounded-visual-study_unapproved-v02_20261015-001640-881a28c4.png)和[上海—良渚地区放大层](../../outputs/rpg-2-star-ocean-the-second_yangtze-delta_geography-grounded-region-visual-study_unapproved-v01_20261015-002022-906b13e8.png)。后者显示真实概略道路，并按真实位置放置上海、松江、良渚城址分区和杭州；它不是可点击游戏地图。[地区样稿的来源与限制](../qa/rpg-2-star-ocean-the-second_yangtze-delta_geography-grounded-region-visual-study_qa-note_unapproved-v01_20261015-002022-45806a1c.md)记录了点位、道路和旅时的不同来源。

## 驾车路线的可追溯参考

| 路段 | 现有路线参考 | 设计结论 |
|---|---|---|
| 上海 → 松江 | Rome2Rio 页面给出的驾车距离 **34.8 km**、估计 **26 分钟**。[路线页](https://www.rome2rio.com/s/Shanghai/Songjiang) | 这是特定站点间的路线估计，不是游戏中任意出发点到松江野外入口的门到门时间。登记精确出发点、入口点及接驳后再定稿游戏分钟数。 |
| 上海 → 良渚古城遗址 | Rome2Rio 页面给出的驾车距离 **187.9 km**、估计 **2 小时**。[路线页](https://www.rome2rio.com/s/Shanghai/Archaeological-ruins-of-Liangzhu-City) | 可作为汽车模式的初始校准值；补入城内出发与遗址入口接驳后，确定固定的游戏路线值。不得把该路线改成地图直线距离。 |
| 松江 → 良渚古城遗址 | **未核验直达道路里程与车程**。 | 路线数据暂空；不能通过上述两条路的相减得到准确值。可先经上海转乘两段已知路线，但那是另一条有绕行的行程。 |

以上仅是当代现实路线参考，非实时路况或时刻表。游戏按确定后的静态门到门分钟数运行；每次旅行累积到同一日历，跨过午夜才改变年月日。三地都适合汽车，**不提供只为测试而虚构的短途飞机**。跨城航空验收另找有实际航线的城市对，分别核对飞行、机场往返和候机时间。

## 场景美术修订点

联合国教科文组织记载，良渚的四部分包括瑶山、谷口高坝、平原低坝和城址。它描述的核心特征是**土遗迹、河网、地貌中的水利系统、墓葬与玉器**，缓冲区还有山、孤丘、水体和湿地。[遗产说明](https://whc.unesco.org/en/list/1592/)

当前 Godot 室外遗址背景是规整的浅色石板广场、石柱与机械圆形平台。它可表达架空科技设施，**不足以让玩家辨认真实良渚遗址**。下一版应使真实地貌成为主画面：土台轮廓、浅水及河渠、低坝与田野植被占据大部分场景；调查站或机械装置以可辨认的后建物件嵌入。保留俯视角、48 逻辑像素角色显示比例和已批准的女主 v8 南向静止帧的明亮场景对比度。图像概念只作为待审候选，不算场景验收。

室内调查室可以作为“设在良渚的架空前文明调查设施”，但地图名称仍是**良渚古城遗址**。如剧情要揭示现代式石板广场，应通过地下设施入口及过渡场景解释它与真实遗址地貌的关系。

室外探索还有一张[路径更清晰的 v02 候选图](../../outputs/rpg-2-star-ocean-the-second_liangzhu-ruins_topdown-exploration-concept_unapproved-v02_20261015-002825-097ebbe7.png)，[视觉审查](../qa/rpg-2-star-ocean-the-second_liangzhu-ruins_topdown-exploration-concept-visual-review_unapproved-v02_20261015-002825-097ebbe7.md)记录了窄桥和碰撞区域待验证的问题。横向战斗另有一张[湿地土台背景候选图](../../outputs/rpg-2-star-ocean-the-second_liangzhu-ruins_sideview-battle-arena-concept_unapproved-v01_20261015-002414-6ca0f109.png)及其[视觉审查](../qa/rpg-2-star-ocean-the-second_liangzhu-ruins_sideview-battle-arena-concept-visual-review_unapproved-v01_20261015-002414-6ca0f109.md)。三张场景图均未实机验收，不增加资产完成数。

## 待定与验收边界

- 上海是否为正式首城、地下社区的现实地理锚点、松江城郊具体入口和良渚内的可玩区域，尚未由用户确定。
- 此文没有核准场景美术，也没有完成地图、旅行计时、存档迁移或双语 UI。
- 交付实机时逐条检查真实地名、地点坐标、道路路线、日期累计、车辆/飞机模式、场景步行、旧存档迁移和视觉地貌；不能以原三点原型的 `M2_SMOKE_OK` 宣称新规则完成。
