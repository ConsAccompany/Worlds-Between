# 全球地图地理底图样稿检查

状态：**独立视觉样稿，未获玩家确认，未导入 Godot，不满足 M2 实机验收**。

[v2 图像](../../outputs/rpg-2-star-ocean-the-second_global-atlas_geography-grounded-visual-study_unapproved-v02_20261015-001640-881a28c4.png)为 1920×1080 单张画面。曾生成的 v1 有陆地轮廓越出画框的缺陷；v2 已按地图画框裁切，检查时标题、上海标记与下方信息栏均清晰。图片只提供全球视角的美术和版面方向；没有真实可点击图钉、缩放、旅行选择和日期结算。

海岸线和陆地形状来自 [Natural Earth 官方维护的 GeoJSON](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_land.geojson)。[数据源副本](../../assets/reference/geography/rpg-2-star-ocean-the-second_earth_natural-earth-110m-land-source_v01_20261015-000900-c6a2de83.geojson)的 SHA-256 为 `9E0729EE253CA7D7A5C4AE9395FB1902264C5377C52E224D13DD85010E2835D9`；[Natural Earth 使用条款](https://www.naturalearthdata.com/about/terms-of-use/)允许修改和使用该数据。渲染脚本位于 [`tools/`](../../tools/rpg-2-star-ocean-the-second_global-atlas_geography-grounded-visual-study-render_v01_20261015-001113-9b6e53ac.py)，输入地理数据及输出文件路径后可重现。

上海经纬度仅用于定位**暂定首城的视觉标记**；图像没有将松江与良渚在全球比例尺下硬塞成三个可分辨图钉。世界总览到地区道路、再到场景入口的缩放层级仍需设计与实机验证。科技、自然、奇幻、魔法各板块的地理分布尚未获用户确认，因此本图没有凭空分配世界区域或画线路。地图用实际地理轮廓，旅行里程与旅时仍须使用独立路线资料。

实机准备门槛：UI 中英文布局、1280×720 可读性、缩放与点击命中、地区层道路/地点、取消不耗时、汽车/飞机路线卡、抵达日期、存档迁移。此样稿不增加已完成资产或场景计数。
