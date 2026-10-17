extends RefCounted

# Map-only bilingual strings. Shared labels (save, growth, field log) still come from AppState.
# Player-facing only: production state (provisional picks, art review) and data sources stay in
# the Game Bible and QA notes, never on screen. The one exception is the attribution that map data
# providers require (credit_relief, credits_*). A route shows only its mode, an approximate distance,
# the whole-hour trip time and the arrival; no airports, check-in, waiting or other trip components.

const STRINGS := {
	"zh": {
		"title": "全球地图 · 科技板块",
		"help_global": "滚轮或＋－缩放 · 拖动平移 · 点选地区",
		"help_region": "点选地点查看路线 · 场景内才步行",
		"view_globe": "全球",
		"view_region": "地区",
		"region_sub": "科技板块 · %d 处地点",
		"boards_legend": "可前往：科技板块（美国、加拿大）· 其他板块尚未开放",
		"kind_city": "城市",
		"kind_outskirts": "城郊",
		"kind_heritage_ruins": "世界遗产 · 遗址",
		"kind_ruins": "遗址",
		"kind_capital_ruins": "废弃首都 · 国会大厦遗址",
		"here": "队伍当前位置",
		"from": "出发地：%s",
		"route_pending_api": "暂时无法查询路线，现在不能出发。",
		"route_no_route": "目前没有可用路线。",
		"route_same": "已在此地，无需旅行。",
		"route_unverified": "另有路线暂不可用。",
		"route_pending_button": "无法出发",
		"via": "经 %s",
		"mode_car": "汽车",
		"mode_air": "飞机",
		"mode_air_car": "飞机＋汽车",
		"road_km": "公路约 %s km",
		"air_km": "航程约 %s km",
		"arrival_text": "抵达 %s",
		"depart": "出发",
		"enter_here": "进入场景",
		"cancel": "取消",
		"travel_failed": "出发未完成，未扣除时间。",
		"inset_title_air": "飞行路线",
		"inset_title_car": "车行路线",
		"credit_relief": "地形数据：Mapzen · USGS · NOAA",
		"credits_title": "地图数据来源",
		"credits_body": "美国东北部、五大湖区视图与飞行路线小图中的地形、近岸大陆架与浅水带，取自 Tilezen / Mapzen Terrarium 地形瓦片（缩放级 7），所用瓦片只含 SRTM、GMTED2010 与 ETOPO1 数据。数据方要求的署名（原文）：\n• Mapzen\n• Global ETOPO1 terrain data U.S. National Oceanic and Atmospheric Administration\n• Global GMTED2010 and SRTM terrain data courtesy of the U.S. Geological Survey.\n（NOAA：美国国家海洋和大气管理局；USGS：美国地质调查局）\n来源：github.com/tilezen/joerd/blob/master/docs/attribution.md\n海岸线、湖泊、边界与全球板块配色基于 Natural Earth 公有领域数据。",
		"credits_close": "返回",
	},
	"en": {
		"title": "Global map · Science region",
		"help_global": "Wheel or +/- to zoom · drag to pan · pick a region",
		"help_region": "Pick a place for its route · walking is in scenes",
		"view_globe": "Globe",
		"view_region": "Region",
		"region_sub": "Science region · %d places",
		"boards_legend": "Open: Science (US & Canada) · others not yet open",
		"kind_city": "City",
		"kind_outskirts": "Outskirts",
		"kind_heritage_ruins": "World Heritage · ruins",
		"kind_ruins": "Ruins",
		"kind_capital_ruins": "Abandoned capital · U.S. Capitol ruins",
		"here": "Party is here",
		"from": "From: %s",
		"route_pending_api": "Route information is unavailable right now, so you cannot depart.",
		"route_no_route": "No route is available yet.",
		"route_same": "Already here. No travel needed.",
		"route_unverified": "Another route is not available yet.",
		"route_pending_button": "Cannot depart",
		"via": "via %s",
		"mode_car": "Car",
		"mode_air": "Air",
		"mode_air_car": "Air + car",
		"road_km": "Road ~%s km",
		"air_km": "Flight ~%s km",
		"arrival_text": "Arrive %s",
		"depart": "Depart",
		"enter_here": "Enter scene",
		"cancel": "Cancel",
		"travel_failed": "Departure did not complete. No time was spent.",
		"inset_title_air": "Flight path",
		"inset_title_car": "Drive route",
		"credit_relief": "Relief data: Mapzen · USGS · NOAA",
		"credits_title": "Map data credits",
		"credits_body": "The relief, coastal shelf and shallows in the US Northeast and US Great Lakes views and the flight inset are baked from Tilezen / Mapzen Terrarium terrain tiles (zoom 7); the tiles used hold only SRTM, GMTED2010 and ETOPO1 data. Required attribution:\n• Mapzen\n• Global ETOPO1 terrain data U.S. National Oceanic and Atmospheric Administration\n• Global GMTED2010 and SRTM terrain data courtesy of the U.S. Geological Survey.\nSource: github.com/tilezen/joerd/blob/master/docs/attribution.md\nCoastlines, lakes, borders and the globe's sphere colours are based on Natural Earth public-domain data.",
		"credits_close": "Back",
	},
}


static func t(key: String) -> String:
	return STRINGS.get(AppState.language, STRINGS["en"]).get(key, key)


static func other_language() -> String:
	return "en" if AppState.language == "zh" else "zh"
