extends Node

signal language_changed

const STRINGS := {
	"zh": {
		"title": "界间行者",
		"subtitle": "探索世界 · 结识伙伴",
		"start": "开始探索",
		"language": "语言：中文",
		"quit": "退出",
		"room_title": "工程原型 · 地下社区",
		"room_help": "WASD / 方向键移动 · Esc 返回主菜单",
		"back": "返回主菜单",
		"map_title": "世界地图 · 科技板块",
		"map_help": "点击目的地进入场景 · 普通旅行不推进日期",
		"map_back": "主菜单",
		"area_city": "科技城市片区",
		"area_outskirts": "城外通道",
		"area_ruins": "旧文明遗址",
		"area_city_hint": "街道与公共设施 · 可与维修员交谈",
		"area_outskirts_hint": "开阔路线 · 可绕过巡逻机械",
		"area_ruins_hint": "前文明设施 · 小心自动防卫机",
		"area_help": "WASD / 方向键移动 · E 交谈 · Esc 返回地图",
		"area_back": "世界地图",
		"npc_city": "维修员：这里的旧设备还能继续使用。",
		"npc_outskirts": "巡路者：走北侧就能绕开巡逻机械。",
		"npc_ruins": "勘察员：遗址记录需要仔细核对。",
		"npc_prompt": "靠近人物按 E 交谈",
		"enemy_label": "自动机械",
		"encounter_title": "遭遇可见敌人",
		"encounter_note": "战斗将在 M3 加入。此处先验证接敌与避战路线。",
		"encounter_continue": "继续探索",
		"bypass_notice": "已绕过敌人，抵达另一侧。",
	},
	"en": {
		"title": "Worlds Between",
		"subtitle": "Explore worlds · Meet companions",
		"start": "Start exploring",
		"language": "Language: English",
		"quit": "Quit",
		"room_title": "Foundation prototype · Underground community",
		"room_help": "WASD / arrows to move · Esc for menu",
		"back": "Back to menu",
		"map_title": "World map · Science region",
		"map_help": "Click a destination · Ordinary travel does not advance the calendar",
		"map_back": "Main menu",
		"area_city": "Science city district",
		"area_outskirts": "Outer passage",
		"area_ruins": "Old civilization ruins",
		"area_city_hint": "Streets and public works · Talk to a technician",
		"area_outskirts_hint": "Open routes · Bypass a patrol machine",
		"area_ruins_hint": "Pre-reset facility · Watch for automated defense",
		"area_help": "WASD / arrows to move · E to talk · Esc for map",
		"area_back": "World map",
		"npc_city": "Technician: These old devices still work well.",
		"npc_outskirts": "Path watcher: Take the north route past the patrol.",
		"npc_ruins": "Surveyor: The ruin records need careful checking.",
		"npc_prompt": "Approach someone and press E to talk",
		"enemy_label": "Automated machine",
		"encounter_title": "Visible enemy encounter",
		"encounter_note": "Combat arrives in M3. This checks contact and the bypass route.",
		"encounter_continue": "Keep exploring",
		"bypass_notice": "You bypassed the enemy and reached the far side.",
	},
}

var language := "zh"
var current_destination_id := "scifi.city"

const DESTINATIONS := ["scifi.city", "scifi.outskirts", "scifi.ruins"]
const DESTINATION_KEYS := {
	"scifi.city": "area_city",
	"scifi.outskirts": "area_outskirts",
	"scifi.ruins": "area_ruins",
}


func _ready() -> void:
	_install_default_controls()


func text_for(key: String) -> String:
	return STRINGS[language].get(key, key)


func destination_name(destination_id: String) -> String:
	return text_for(DESTINATION_KEYS.get(destination_id, "area_city"))


func select_destination(destination_id: String) -> bool:
	if not DESTINATIONS.has(destination_id):
		return false
	current_destination_id = destination_id
	return true


func toggle_language() -> void:
	language = "en" if language == "zh" else "zh"
	language_changed.emit()


func _install_default_controls() -> void:
	_add_key_action("move_left", KEY_A)
	_add_key_action("move_left", KEY_LEFT)
	_add_key_action("move_right", KEY_D)
	_add_key_action("move_right", KEY_RIGHT)
	_add_key_action("move_up", KEY_W)
	_add_key_action("move_up", KEY_UP)
	_add_key_action("move_down", KEY_S)
	_add_key_action("move_down", KEY_DOWN)
	_add_key_action("interact", KEY_E)


func _add_key_action(action: StringName, key: Key) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action)
	var event := InputEventKey.new()
	event.physical_keycode = key
	InputMap.action_add_event(action, event)

