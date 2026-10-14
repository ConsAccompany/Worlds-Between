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
		"battle_help": "A/D 移动 · J 攻击 · K 闪避 · L 防御 · Q 技能 · Tab 换人 · P 暂停 · T 自动",
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
		"member_hero": "旅人",
		"member_liang": "梁序",
		"member_zhao": "赵铃",
		"member_ji": "纪澄",
		"recruit_prompt": "靠近人物按 E 交谈",
		"recruit_invite": "邀请入队",
		"recruit_later": "暂不邀请",
		"recruit_full": "当前队伍已满（最多 5 人）。",
		"recruit_joined": "%s 已加入队伍。",
		"recruit_liang": "梁序：训练结束了。若你愿意，我仍能同行，帮你判断情势。",
		"recruit_zhao": "赵铃：这座中继站正在失去信号。修好它以后，我想看看更远的地方。",
		"recruit_ji_locked": "纪澄：先看看遗址中央的记录台，再谈同行的事。",
		"recruit_ji": "纪澄：资料不完整，正好需要有人一起验证。要同行吗？",
		"relic_prompt": "靠近记录台按 E 调查",
		"relic_marker": "记录台",
		"relic_done": "已协助纪澄核对一条旧记录。现在可以邀请她同行。",
		"battle_pause_title": "暂停指令 · 当前操纵：%s",
		"battle_resume": "继续战斗",
		"battle_skill_use": "使用技能",
		"battle_target": "指令对象：%s",
		"battle_focus": "集中攻击",
		"battle_defend": "优先防御",
		"battle_skill_order": "优先技能",
		"battle_default": "按 AI 策略",
		"ai_policy_balanced": "AI：平衡",
		"ai_policy_aggressive": "AI：进攻",
		"ai_policy_cautious": "AI：谨慎",
		"battle_auto_on": "全自动：开",
		"battle_auto_off": "全自动：关",
		"battle_skill_hero": "临场理解",
		"battle_skill_liang": "战术校准",
		"battle_skill_zhao": "回声测距",
		"battle_skill_ji": "断层回读",
		"battle_skill_used": "%s 使用了 %s。",
		"battle_member_down": "%s 倒下了。",
		"battle_party_status": "队伍：%s",
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
		"battle_help": "A/D move · J attack · K dodge · L guard · Q skill · Tab swap · P pause · T auto",
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
		"member_hero": "Traveler",
		"member_liang": "Liang Xu",
		"member_zhao": "Zhao Ling",
		"member_ji": "Ji Cheng",
		"recruit_prompt": "Approach someone and press E to talk",
		"recruit_invite": "Invite to party",
		"recruit_later": "Maybe later",
		"recruit_full": "The active party is full (maximum 5).",
		"recruit_joined": "%s joined your party.",
		"recruit_liang": "Liang Xu: Your training is over. I can still travel with you and help assess what we find.",
		"recruit_zhao": "Zhao Ling: This relay is losing signal. Once it's fixed, I want to see what lies farther away.",
		"recruit_ji_locked": "Ji Cheng: Examine the records console in the center first. Then we can talk about traveling together.",
		"recruit_ji": "Ji Cheng: These records are incomplete. I'd welcome help checking them. Shall we travel together?",
		"relic_prompt": "Approach the records console and press E",
		"relic_marker": "Records",
		"relic_done": "You helped Ji Cheng verify an old record. You can now invite her.",
		"battle_pause_title": "Paused · Controlling: %s",
		"battle_resume": "Resume battle",
		"battle_skill_use": "Use skill",
		"battle_target": "Order target: %s",
		"battle_focus": "Focus attacks",
		"battle_defend": "Defend first",
		"battle_skill_order": "Use skill first",
		"battle_default": "Follow AI policy",
		"ai_policy_balanced": "AI: Balanced",
		"ai_policy_aggressive": "AI: Attack",
		"ai_policy_cautious": "AI: Cautious",
		"battle_auto_on": "Full auto: on",
		"battle_auto_off": "Full auto: off",
		"battle_skill_hero": "Situational Insight",
		"battle_skill_liang": "Tactical Calibration",
		"battle_skill_zhao": "Echo Ranging",
		"battle_skill_ji": "Fault-Line Recall",
		"battle_skill_used": "%s used %s.",
		"battle_member_down": "%s fell.",
		"battle_party_status": "Party: %s",
		"bypass_notice": "You bypassed the enemy and reached the far side.",
	},
}

var language := "zh"
var current_destination_id := "scifi.city"
var hero_state := {"hp": 100, "max_hp": 100, "energy": 60, "max_energy": 60}
var member_states: Dictionary = {}
var active_party_ids: Array[String] = ["hero"]
var recruited_members: Dictionary = {}
var ji_records_checked := false
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
const PARTY_CAPACITY := 5
const MEMBER_DEFS := {
	"hero": {"name_key": "member_hero", "job_series": "sword", "aptitudes": [60, 60, 60, 60], "max_hp": 100, "max_energy": 60, "attack_damage": 19, "attack_range": 61.0, "skill_key": "battle_skill_hero", "color": Color("#5eb6af")},
	"liang-xu": {"name_key": "member_liang", "job_series": "tactics", "aptitudes": [48, 67, 94, 42], "max_hp": 95, "max_energy": 70, "attack_damage": 16, "attack_range": 65.0, "skill_key": "battle_skill_liang", "color": Color("#a6b4b8")},
	"zhao-ling": {"name_key": "member_zhao", "job_series": "firearms", "aptitudes": [51, 84, 68, 40], "max_hp": 82, "max_energy": 75, "attack_damage": 14, "attack_range": 164.0, "skill_key": "battle_skill_zhao", "color": Color("#69bbce")},
	"ji-cheng": {"name_key": "member_ji", "job_series": "relics", "aptitudes": [41, 67, 79, 83], "max_hp": 80, "max_energy": 80, "attack_damage": 12, "attack_range": 100.0, "skill_key": "battle_skill_ji", "color": Color("#6da78b")},
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
	hero_state = {"hp": 100, "max_hp": 100, "energy": 60, "max_energy": 60, "level": 1, "job_series": "sword", "job_stage": 1, "ai_policy": "balanced"}
	member_states.clear()
	active_party_ids = ["hero"]
	recruited_members.clear()
	ji_records_checked = false
	battle_enemy_id = ""
	enemy_cleared_for_return = false
	returning_from_battle = false
	current_destination_id = "scifi.city"


func member_name(member_id: String) -> String:
	return text_for(String(MEMBER_DEFS.get(member_id, MEMBER_DEFS["hero"])["name_key"]))


func member_state(member_id: String) -> Dictionary:
	return hero_state if member_id == "hero" else member_states.get(member_id, {})


func recruit_member(member_id: String) -> bool:
	if not MEMBER_DEFS.has(member_id) or member_id == "hero" or recruited_members.has(member_id):
		return false
	if active_party_ids.size() >= PARTY_CAPACITY:
		return false
	if member_id == "ji-cheng" and not ji_records_checked:
		return false
	var definition: Dictionary = MEMBER_DEFS[member_id]
	var level := maxi(1, int(hero_state.get("level", 1)))
	var stage := mini(2, 1 + (level - 1) / 10)
	member_states[member_id] = {
		"hp": int(definition["max_hp"]), "max_hp": int(definition["max_hp"]),
		"energy": int(definition["max_energy"]), "max_energy": int(definition["max_energy"]),
		"level": level, "job_series": definition["job_series"], "job_stage": stage,
		"ai_policy": "balanced",
		"learned_skill_ids": ["basic", "advanced"] if stage > 1 else ["basic"],
		"aptitudes": definition["aptitudes"].duplicate(),
	}
	recruited_members[member_id] = true
	active_party_ids.append(member_id)
	return true


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
	_add_key_action("battle_switch", KEY_TAB)
	_add_key_action("battle_pause", KEY_P)
	_add_key_action("battle_auto", KEY_T)
	_add_key_action("battle_skill", KEY_Q)


func _add_key_action(action: StringName, key: Key) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action)
	var event := InputEventKey.new()
	event.physical_keycode = key
	InputMap.action_add_event(action, event)

