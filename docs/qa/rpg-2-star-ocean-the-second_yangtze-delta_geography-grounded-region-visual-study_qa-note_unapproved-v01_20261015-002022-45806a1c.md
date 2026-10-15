# 上海—松江—良渚地区地图样稿检查

状态：**单张视觉样稿，尚未获得玩家确认；未接入游戏，也未增加 M2 完成计数**。

[1920×1080 地区样稿](../../outputs/rpg-2-star-ocean-the-second_yangtze-delta_geography-grounded-region-visual-study_unapproved-v01_20261015-002022-906b13e8.png)把上海、松江、良渚古城遗址及杭州放在同一真实地理范围。右栏只展示从暂定首城上海出发的两条已查证**参考**驾车路线：上海→松江 34.8 km／26 分钟，上海→良渚古城遗址 187.9 km／2 小时。数据出自 [Rome2Rio 上海—松江](https://www.rome2rio.com/s/Shanghai/Songjiang)及[上海—良渚](https://www.rome2rio.com/s/Shanghai/Archaeological-ruins-of-Liangzhu-City)。这些仍不是已经加入接驳、存档时间轴与出发点的最终游戏旅时。

地图陆地轮廓来自 [Natural Earth 50m land](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_50m_land.geojson)，道路形状来自 [Natural Earth 10m roads](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_10m_roads.geojson)。为保持项目轻量，仅把本区 634 条命中路线要素的[子集](../../assets/reference/geography/rpg-2-star-ocean-the-second_yangtze-delta_natural-earth-10m-road-subset-source_v01_20261015-001400-f70c8f29.geojson)纳入仓库；[50m 陆地数据](../../assets/reference/geography/rpg-2-star-ocean-the-second_earth_natural-earth-50m-land-source_v01_20261015-001400-4420ef51.geojson)也单独保留。道路图层是**概略道路几何**，并无可用的道路名称或可直接计算车程的路由图；右栏旅时独立引用路线查询。数据可按 [Natural Earth 条款](https://www.naturalearthdata.com/about/terms-of-use/)使用。

位置依据：上海、杭州使用 [Natural Earth populated places](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_10m_populated_places_simple.geojson)中的点；松江标记使用 [GeoNames 的松江镇／区治所在点](https://www.geonames.org/search.html?country=CN&q=shanghai)；良渚标记采用[联合国教科文组织定期报告](https://whc.unesco.org/document/218056)中“城址”分区的 `30.396°N, 119.991°E`，并非遗址所有分区的中心。地图点是区域浏览标记，不等于最终可玩的具体门口。

## 视觉核对

- 地理相对位置可见：上海位于松江东北，良渚与杭州在西南；地图保留东侧海面和真实海岸轮廓。
- 三个可玩地点使用中文和英文标签，杭州仅作真实城市参照；未把松江误称为独立城市。
- 道路细线可见且没有直接用图钉间直线充当道路。高等级道路显示更亮；交叉密集处仍可能需要实机缩放及简化。
- 标题、地点卡和地图在 1920×1080 审阅尺寸可读；**尚未检查游戏原生 1280×720 尺寸**。

## 实机前仍需解决

点击命中与地图缩放、游戏年月日和日内时间、真实门到门路线定值、汽车／飞机选择、取消旅行不扣时、连续短途时间累计、场景进入点与存档兼容。未核验的松江→良渚直达车程不可用这两条已查证路线相减。除上海暂定外，其他地球板块的城市分布仍待选址。[可复现渲染脚本](../../tools/rpg-2-star-ocean-the-second_yangtze-delta_geography-grounded-region-visual-study-render_v01_20261015-002022-70a92bce.py)输出的是视觉稿，不是 Godot 运行地图。
