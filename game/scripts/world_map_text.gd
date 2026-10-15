extends RefCounted

# Map-only bilingual strings. Shared labels (save, growth, field log) still come from AppState.
# Player-facing only: production state (provisional picks, art review) and data sources stay in
# the Game Bible and QA notes, never on screen. Travel figures keep their "estimate" marker.

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
		"estimate": "里程与旅时为估算",
		"mode_car": "汽车",
		"mode_air": "飞机",
		"mode_air_car": "飞机＋汽车",
		"road_km": "公路 %s km",
		"air_km": "航程 %s km",
		"arrival_text": "抵达 %s",
		"depart": "出发",
		"enter_here": "进入场景",
		"cancel": "取消",
		"travel_failed": "出发未完成，未扣除时间。",
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
		"estimate": "estimated distance and time",
		"mode_car": "Car",
		"mode_air": "Air",
		"mode_air_car": "Air + car",
		"road_km": "Road %s km",
		"air_km": "Flight %s km",
		"arrival_text": "Arrive %s",
		"depart": "Depart",
		"enter_here": "Enter scene",
		"cancel": "Cancel",
		"travel_failed": "Departure did not complete. No time was spent.",
	},
}


static func t(key: String) -> String:
	return STRINGS.get(AppState.language, STRINGS["en"]).get(key, key)


static func other_language() -> String:
	return "en" if AppState.language == "zh" else "zh"
