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
		"battle_title": "即时战斗 · %s",
		"battle_help": "A/D 或 ←/→ 移动 · J 攻击 · K 闪避 · 按住 L 防御",
		"battle_attack": "攻击",
		"battle_dodge": "闪避",
		"battle_guard": "防御",
		"battle_hp": "生命",
		"battle_energy": "能量",
		"battle_enemy_hp": "敌人生命",
		"battle_telegraph": "敌人蓄力中！",
		"battle_ready": "靠近敌人并攻击。闪避消耗 12 能量；防御受击消耗 6 能量。",
		"battle_far": "距离过远",
		"battle_hit": "命中敌人",
		"battle_no_energy": "能量不足",
		"battle_dodge_feedback": "闪避成功",
		"battle_guard_feedback": "防御减伤",
		"battle_hurt": "受到攻击",
		"battle_win": "战斗胜利",
		"battle_loss": "战斗失败",
		"battle_win_note": "战后生命与能量各增加上限的 20%，最多回满。",
		"battle_loss_note": "队伍倒下，返回主菜单。",
		"battle_continue": "继续探索",
		"battle_menu": "返回主菜单",
		"enemy_patrol": "巡逻机械",
		"enemy_sentry": "自动防卫机",
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
		"battle_title": "Real-time battle · %s",
		"battle_help": "A/D or ←/→ move · J attack · K dodge · Hold L to guard",
		"battle_attack": "Attack",
		"battle_dodge": "Dodge",
		"battle_guard": "Guard",
		"battle_hp": "HP",
		"battle_energy": "Energy",
		"battle_enemy_hp": "Enemy HP",
		"battle_telegraph": "Enemy winding up!",
		"battle_ready": "Close in and attack. Dodge costs 12 energy; guarding a hit costs 6.",
		"battle_far": "Too far away",
		"battle_hit": "Hit the enemy",
		"battle_no_energy": "Not enough energy",
		"battle_dodge_feedback": "Dodged the attack",
		"battle_guard_feedback": "Guard reduced damage",
		"battle_hurt": "Took a hit",
		"battle_win": "Victory",
		"battle_loss": "Defeat",
		"battle_win_note": "After battle, HP and energy each gain 20% of their maximum, capped at full.",
		"battle_loss_note": "Your party fell. Returning to the main menu.",
		"battle_continue": "Keep exploring",
		"battle_menu": "Main menu",
		"enemy_patrol": "Patrol machine",
		"enemy_sentry": "Defense machine",
		"bypass_notice": "You bypassed the enemy and reached the far side.",
	},
}

var language := "zh"
var current_destination_id := "scifi.city"
var hero_state := {"hp": 100, "max_hp": 100, "energy": 60, "max_energy": 60}
var battle_enemy_id := ""
var battle_return_position := Vector2(82, 260)
var enemy_cleared_for_return := false
var returning_from_battle := false
var battle_transition_started_usec := 0
var last_battle_transition_ms := 0.0

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
	enemy_cleared_for_return = false
	returning_from_battle = false
	return true


func begin_new_run() -> void:
	hero_state = {"hp": 100, "max_hp": 100, "energy": 60, "max_energy": 60}
	battle_enemy_id = ""
	enemy_cleared_for_return = false
	returning_from_battle = false
	current_destination_id = "scifi.city"


func begin_battle(enemy_id: String, return_position: Vector2) -> bool:
	if not ["patrol", "sentry"].has(enemy_id):
		return false
	battle_enemy_id = enemy_id
	battle_return_position = return_position
	battle_transition_started_usec = Time.get_ticks_usec()
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
	_add_key_action("battle_attack", KEY_J)
	_add_key_action("battle_dodge", KEY_K)
	_add_key_action("battle_guard", KEY_L)


func _add_key_action(action: StringName, key: Key) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action)
	var event := InputEventKey.new()
	event.physical_keycode = key
	InputMap.action_add_event(action, event)

