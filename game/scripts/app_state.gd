extends Node

signal language_changed

const STRINGS := {
	"zh": {
		"title": "界间行者",
		"subtitle": "探索世界 · 结识伙伴",
		"start": "开始探索",
		"setup_title": "创建主角",
		"setup_name": "姓名",
		"setup_gender": "外观",
		"setup_male": "男性外观", "setup_female": "女性外观",
		"setup_help": "18 岁，结束一年训练，即将首次探索地表。可按自己的节奏招募伙伴。",
		"setup_controls": "操作：地图选目的地；WASD 移动；E 交互；接触敌人进入战斗。",
		"setup_skip": "跳过指引并出发", "setup_start": "开始探索", "setup_back": "返回菜单",
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
		"battle_help": "A/D 移动 · J 攻击 · K 闪避 · L 防御 · Q 个人技 · R 职业技 · Tab 换人 · P 暂停 · T 自动",
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
		"growth_title": "角色成长与职业",
		"growth_open": "角色与职业",
		"growth_back": "返回地图",
		"growth_pending": "达到十级关口：请选择职业去向",
		"growth_level": "等级 %d · XP %d/%d · JP %d",
		"growth_aptitudes": "天分  武 %d · 变 %d · 学 %d · 灵 %d  （60 可入职）",
		"growth_job": "当前：%s · 第 %d 阶",
		"growth_stay": "留任当前职业",
		"growth_promote": "晋升当前系列",
		"growth_switch": "转入 %s",
		"growth_upgrade": "升级技能 %s · %d JP",
		"growth_skill": "职业技能：%s",
		"growth_personal": "个人技能 %s Lv%d · 升级 %d JP",
		"save_title": "存档与读取", "save_open": "存档", "save_load_open": "读取游戏",
		"save_back": "返回", "save_manual_slot": "手动栏 %d", "save_write": "保存到此栏",
		"save_load": "读取", "save_empty": "空栏位", "save_auto": "自动记录",
		"save_before_battle": "开战前", "save_after_battle": "胜利后", "save_manual_note": "手动保存",
		"save_summary": "%s · Lv%d · %d 人 · %s",
		"save_ok": "已保存至 %s", "save_failed": "存档失败", "save_load_failed": "读取失败或存档不兼容",
		"save_version_old": "旧版存档 · 无法读取", "save_no_records": "暂无自动记录",
		"growth_rewards": "战斗奖励：%d XP / %d JP；候补获得 25%%",
		"growth_locked": "天分未达到 60",
		"growth_done": "职业选择已完成",
		"job_skill_sword_slash": "破锋斩", "job_skill_sword_arc": "回旋剑势",
		"job_skill_firearms_shot": "精准射击", "job_skill_firearms_burst": "连发压制",
		"job_skill_tactics_mark": "战术标记", "job_skill_tactics_rally": "全队整备",
		"job_skill_relics_echo": "遗物共鸣", "job_skill_relics_delay": "时序迟滞",
		"bypass_notice": "已绕过敌人，抵达另一侧。",
		"field_log": "实地日志",
		"field_log_hint": "任意顺序探索三处地点；调查中继站与遗址记录；观察或击退一台机械，最后回城汇报。",
		"field_log_count": "地点 %d/3 · 中继 %s · 记录 %s · 机械 %s",
		"field_yes": "完成", "field_no": "待办",
		"relay_marker": "中继站", "relay_prompt": "靠近中继站按 E 调查",
		"relay_done": "中继站的故障来自一段被重复改写的线路图。赵铃已记下异常。",
		"relay_record": "中继站记录：维护图纸被多次改写；原始线路用途仍未确认。",
		"archive_record": "遗址记录：前文明资料残缺，其中一条能源调度记录与现行网络的编号相同。",
		"machine_record": "机械记录：已观察到自动机械的行动模式。",
		"report_marker": "实地汇报", "report_prompt": "靠近汇报台按 E 查看进度",
		"report_locked": "仍需完成实地日志中的调查项目。",
		"report_ready": "资料已齐备。靠近汇报台按 E 提交。",
		"report_title": "科技板块试玩完成",
		"report_summary": "%s 已走访三处地点、核对两份记录，并观察了自动机械。同行伙伴：%d/3。",
		"report_continue": "继续自由探索", "report_map": "返回世界地图",
		"report_note": "这份资料揭示了新的问题。完整故事将在后续章节展开。",
	},
	"en": {
		"title": "Worlds Between",
		"subtitle": "Explore worlds · Meet companions",
		"start": "Start exploring",
		"setup_title": "Create your traveler",
		"setup_name": "Name",
		"setup_gender": "Appearance",
		"setup_male": "Masculine", "setup_female": "Feminine",
		"setup_help": "At 18, you have finished a year of training and are ready to explore the surface. Recruit companions at your own pace.",
		"setup_controls": "Controls: choose a map destination; move with WASD; press E to interact; contact an enemy to fight.",
		"setup_skip": "Skip guide and depart", "setup_start": "Start exploring", "setup_back": "Main menu",
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
		"battle_help": "A/D move · J attack · K dodge · L guard · Q personal · R job · Tab swap · P pause · T auto",
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
		"growth_title": "Character Growth & Jobs",
		"growth_open": "Characters & Jobs",
		"growth_back": "Back to map",
		"growth_pending": "Level 10 threshold: choose a job path",
		"growth_level": "Level %d · XP %d/%d · JP %d",
		"growth_aptitudes": "Aptitudes  Martial %d · Adaptive %d · Scholarly %d · Spiritual %d  (60 required)",
		"growth_job": "Current: %s · Stage %d",
		"growth_stay": "Stay in current job",
		"growth_promote": "Promote in current series",
		"growth_switch": "Switch to %s",
		"growth_upgrade": "Upgrade %s · %d JP",
		"growth_skill": "Job skills: %s",
		"growth_personal": "Personal %s Lv%d · upgrade %d JP",
		"save_title": "Save & Load", "save_open": "Save", "save_load_open": "Load Game",
		"save_back": "Back", "save_manual_slot": "Manual slot %d", "save_write": "Save here",
		"save_load": "Load", "save_empty": "Empty slot", "save_auto": "Autosave",
		"save_before_battle": "Before battle", "save_after_battle": "After victory", "save_manual_note": "Manual save",
		"save_summary": "%s · Lv%d · %d party · %s",
		"save_ok": "Saved to %s", "save_failed": "Save failed", "save_load_failed": "Load failed or incompatible save",
		"save_version_old": "Old save · cannot load", "save_no_records": "No autosaves yet",
		"growth_rewards": "Battle rewards: %d XP / %d JP; reserves earn 25%%",
		"growth_locked": "Aptitude below 60",
		"growth_done": "Job choice complete",
		"job_skill_sword_slash": "Edge Break", "job_skill_sword_arc": "Sword Arc",
		"job_skill_firearms_shot": "Precision Shot", "job_skill_firearms_burst": "Suppressive Burst",
		"job_skill_tactics_mark": "Tactical Mark", "job_skill_tactics_rally": "Team Rally",
		"job_skill_relics_echo": "Relic Echo", "job_skill_relics_delay": "Time Delay",
		"bypass_notice": "You bypassed the enemy and reached the far side.",
		"field_log": "Field log",
		"field_log_hint": "Explore all three locations in any order. Check the relay and ruins records, observe or defeat a machine, then report back in the city.",
		"field_log_count": "Places %d/3 · Relay %s · Records %s · Machine %s",
		"field_yes": "Done", "field_no": "Open",
		"relay_marker": "Relay", "relay_prompt": "Approach the relay and press E",
		"relay_done": "The relay fault points to a circuit plan rewritten several times. Zhao Ling notes the anomaly.",
		"relay_record": "Relay record: the maintenance plan was repeatedly revised. Its original purpose is unknown.",
		"archive_record": "Ruin record: a fragmented energy dispatch entry shares an identifier with the current network.",
		"machine_record": "Machine record: an automated machine's behavior has been observed.",
		"report_marker": "Field report", "report_prompt": "Approach the report desk and press E",
		"report_locked": "The field log still has unfinished investigations.",
		"report_ready": "The evidence is ready. Press E at the report desk to submit it.",
		"report_title": "Science region demo complete",
		"report_summary": "%s visited three places, checked two records, and observed a machine. Companions: %d/3.",
		"report_continue": "Continue exploring", "report_map": "World map",
		"report_note": "The evidence raises further questions. The full story will develop in later chapters.",
	},
}

var language := "zh"
var hero_name := ""
var hero_appearance := "male"
var current_destination_id := "scifi.city"
var hero_state := {"hp": 100, "max_hp": 100, "energy": 60, "max_energy": 60}
var member_states: Dictionary = {}
var active_party_ids: Array[String] = ["hero"]
var recruited_members: Dictionary = {}
var ji_records_checked := false
var relay_checked := false
var areas_visited: Dictionary = {}
var machine_observed := false
var demo_completed := false
var show_initial_guide := false
var battle_enemy_id := ""
var battle_return_position := Vector2(82, 260)
var enemy_cleared_for_return := false
var returning_from_battle := false
var battle_transition_started_usec := 0
var last_battle_transition_ms := 0.0
var growth_return_scene := "res://scenes/scifi_world_map.tscn"
var save_screen_mode := "load"
var save_return_scene := "res://scenes/scifi_world_map.tscn"
var save_return_position := Vector2(82, 260)
var resume_area_pending := false
var resume_area_position := Vector2(82, 260)
var loaded_scene_kind := "map"

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
	hero_state = {"hp": 100, "max_hp": 100, "energy": 60, "max_energy": 60, "level": 1, "xp": 0, "jp": 0, "pending_job_choices": 0, "job_series": "sword", "job_stage": 1, "job_records": {"sword": {"stage": 1, "skills": {"sword_slash": 1}}}, "personal_skill_rank": 1, "aptitudes": [60, 60, 60, 60], "ai_policy": "balanced"}
	member_states.clear()
	active_party_ids = ["hero"]
	recruited_members.clear()
	ji_records_checked = false
	hero_name = ""
	hero_appearance = "male"
	relay_checked = false
	areas_visited.clear()
	machine_observed = false
	demo_completed = false
	show_initial_guide = false
	battle_enemy_id = ""
	enemy_cleared_for_return = false
	returning_from_battle = false
	current_destination_id = "scifi.city"
	growth_return_scene = "res://scenes/scifi_world_map.tscn"
	resume_area_pending = false
	loaded_scene_kind = "map"


func member_name(member_id: String) -> String:
	if member_id == "hero" and hero_name != "":
		return hero_name
	return text_for(String(MEMBER_DEFS.get(member_id, MEMBER_DEFS["hero"])["name_key"]))


func field_log_text() -> String:
	var state := text_for("field_yes")
	var open := text_for("field_no")
	return text_for("field_log_count") % [areas_visited.size(), state if relay_checked else open, state if ji_records_checked else open, state if machine_observed else open]


func can_submit_report() -> bool:
	return areas_visited.size() == DESTINATIONS.size() and relay_checked and ji_records_checked and machine_observed


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
		"level": level, "xp": 0, "jp": 0, "pending_job_choices": 0,
		"job_series": definition["job_series"], "job_stage": stage,
		"job_records": {definition["job_series"]: {"stage": stage, "skills": {String(GrowthRules.SERIES[definition["job_series"]]["skills"][0]): 1, String(GrowthRules.SERIES[definition["job_series"]]["skills"][stage - 1]): 1}}},
		"personal_skill_rank": mini(3, 1 + (level - 1) / 20),
		"ai_policy": "balanced",
		"learned_skill_ids": ["basic", "advanced"] if stage > 1 else ["basic"],
		"aptitudes": definition["aptitudes"].duplicate(),
	}
	recruited_members[member_id] = true
	active_party_ids.append(member_id)
	return true


func award_battle_rewards(enemy_id: String) -> Dictionary:
	var xp := 26 if enemy_id == "patrol" else 44
	var jp := 12 if enemy_id == "patrol" else 20
	for member_id in active_party_ids:
		_grant_growth(member_state(member_id), xp, jp)
	for member_id in member_states:
		if not active_party_ids.has(member_id):
			_grant_growth(member_states[member_id], ceili(float(xp) * 0.25), ceili(float(jp) * 0.25))
	return {"xp": xp, "jp": jp}


func _grant_growth(member: Dictionary, xp: int, jp: int) -> void:
	member["xp"] = int(member.get("xp", 0)) + xp
	member["jp"] = int(member.get("jp", 0)) + jp
	_process_levels(member)


func _process_levels(member: Dictionary) -> void:
	while int(member.get("pending_job_choices", 0)) == 0 and int(member["xp"]) >= GrowthRules.xp_to_next(int(member["level"])):
		member["xp"] = int(member["xp"]) - GrowthRules.xp_to_next(int(member["level"]))
		member["level"] = int(member["level"]) + 1
		member["max_hp"] = int(member["max_hp"]) + 3
		member["max_energy"] = int(member["max_energy"]) + 2
		member["hp"] = member["max_hp"]
		member["energy"] = member["max_energy"]
		if int(member["level"]) % 10 == 0:
			member["pending_job_choices"] = 1


func has_pending_job_choice() -> bool:
	for member_id in active_party_ids:
		if int(member_state(member_id).get("pending_job_choices", 0)) > 0:
			return true
	return false


func choose_job(member_id: String, action: String, target_series: String = "") -> bool:
	var member := member_state(member_id)
	if member.is_empty() or int(member.get("pending_job_choices", 0)) < 1:
		return false
	var current: String = member["job_series"]
	var records: Dictionary = member["job_records"]
	match action:
		"stay":
			pass
		"promote":
			if int(member["job_stage"]) >= 2:
				return false
			member["job_stage"] = int(member["job_stage"]) + 1
			var record: Dictionary = records[current]
			record["stage"] = member["job_stage"]
			record["skills"][GrowthRules.current_skill_id(member)] = 1
		"switch":
			if target_series == current or not GrowthRules.can_enter(member, target_series):
				return false
			if not records.has(target_series):
				records[target_series] = {"stage": 1, "skills": {String(GrowthRules.SERIES[target_series]["skills"][0]): 1}}
			member["job_series"] = target_series
			member["job_stage"] = int(records[target_series]["stage"])
		_:
			return false
	member["pending_job_choices"] = int(member["pending_job_choices"]) - 1
	_process_levels(member)
	return true


func upgrade_job_skill(member_id: String, skill_id: String) -> bool:
	var member := member_state(member_id)
	if member.is_empty():
		return false
	var series_id: String = member["job_series"]
	var skills: Array = GrowthRules.SERIES[series_id]["skills"]
	if not skills.has(skill_id) or skills.find(skill_id) >= int(member["job_stage"]):
		return false
	var record: Dictionary = member["job_records"][series_id]
	var rank := int(record["skills"].get(skill_id, 0))
	var cost := GrowthRules.jp_cost(member, series_id, rank + 1)
	if cost < 0 or int(member["jp"]) < cost:
		return false
	member["jp"] = int(member["jp"]) - cost
	record["skills"][skill_id] = rank + 1
	return true


func upgrade_personal_skill(member_id: String) -> bool:
	var member := member_state(member_id)
	if member.is_empty() or not MEMBER_DEFS.has(member_id):
		return false
	var rank := int(member.get("personal_skill_rank", 1))
	var home_series: String = MEMBER_DEFS[member_id]["job_series"]
	var cost := GrowthRules.jp_cost(member, home_series, rank + 1)
	if cost < 0 or int(member.get("jp", 0)) < cost:
		return false
	member["jp"] = int(member["jp"]) - cost
	member["personal_skill_rank"] = rank + 1
	return true


func begin_battle(enemy_id: String, return_position: Vector2) -> bool:
	if not ["patrol", "sentry"].has(enemy_id):
		return false
	battle_enemy_id = enemy_id
	battle_return_position = return_position
	battle_transition_started_usec = Time.get_ticks_usec()
	return true


func make_snapshot(scene_kind: String, position: Vector2, note: String) -> Dictionary:
	return {
		"scene": scene_kind,
		"position": [position.x, position.y],
		"destination": current_destination_id,
		"enemyCleared": enemy_cleared_for_return,
		"hero": hero_state.duplicate(true),
		"heroName": hero_name,
		"heroAppearance": hero_appearance,
		"members": member_states.duplicate(true),
		"activeParty": active_party_ids.duplicate(),
		"recruited": recruited_members.duplicate(true),
		"jiRecordsChecked": ji_records_checked,
		"relayChecked": relay_checked,
		"areasVisited": areas_visited.duplicate(true),
		"machineObserved": machine_observed,
		"demoCompleted": demo_completed,
		"language": language,
		"note": note,
	}


func write_manual_save(slot: int) -> String:
	var kind := "area" if save_return_scene.ends_with("scifi_exploration_area.tscn") else "map"
	return SaveStore.write_entry("manual", slot, make_snapshot(kind, save_return_position, "manual_note"))


func write_auto_save(scene_kind: String, position: Vector2, note: String) -> String:
	return SaveStore.write_entry("auto", 0, make_snapshot(scene_kind, position, note))


func load_save(id: String) -> bool:
	var entry := SaveStore.read_entry(id)
	if entry.is_empty() or int(entry.get("schemaVersion", -1)) != SaveStore.SCHEMA_VERSION:
		return false
	var snapshot: Dictionary = entry["snapshot"]
	if not _valid_snapshot(snapshot):
		return false
	var party: Array[String] = []
	for member_id in snapshot["activeParty"]:
		party.append(String(member_id))
	hero_state = snapshot["hero"].duplicate(true)
	hero_name = String(snapshot.get("heroName", ""))
	hero_appearance = String(snapshot.get("heroAppearance", "male"))
	member_states = snapshot["members"].duplicate(true)
	active_party_ids = party
	recruited_members = snapshot["recruited"].duplicate(true)
	ji_records_checked = bool(snapshot["jiRecordsChecked"])
	relay_checked = bool(snapshot.get("relayChecked", false))
	areas_visited = snapshot.get("areasVisited", {}).duplicate(true)
	machine_observed = bool(snapshot.get("machineObserved", false))
	demo_completed = bool(snapshot.get("demoCompleted", false))
	show_initial_guide = false
	current_destination_id = String(snapshot["destination"])
	language = String(snapshot["language"])
	enemy_cleared_for_return = bool(snapshot["enemyCleared"])
	loaded_scene_kind = String(snapshot["scene"])
	resume_area_position = Vector2(float(snapshot["position"][0]), float(snapshot["position"][1]))
	resume_area_pending = loaded_scene_kind == "area"
	returning_from_battle = false
	battle_enemy_id = ""
	battle_return_position = resume_area_position
	language_changed.emit()
	return true


func loaded_scene_path() -> String:
	var path := "res://scenes/scifi_exploration_area.tscn" if loaded_scene_kind == "area" else "res://scenes/scifi_world_map.tscn"
	if has_pending_job_choice():
		growth_return_scene = path
		return "res://scenes/growth_screen.tscn"
	return path


func _valid_snapshot(snapshot: Dictionary) -> bool:
	if snapshot.get("scene", "") not in ["map", "area"] or not DESTINATIONS.has(snapshot.get("destination", "")):
		return false
	var position: Variant = snapshot.get("position")
	if typeof(position) != TYPE_ARRAY or position.size() != 2:
		return false
	if typeof(snapshot.get("hero")) != TYPE_DICTIONARY or typeof(snapshot.get("members")) != TYPE_DICTIONARY or typeof(snapshot.get("activeParty")) != TYPE_ARRAY or typeof(snapshot.get("recruited")) != TYPE_DICTIONARY:
		return false
	var hero: Dictionary = snapshot["hero"]
	if not hero.has("level") or not hero.has("job_records") or not GrowthRules.SERIES.has(hero.get("job_series", "")):
		return false
	var party: Array = snapshot["activeParty"]
	if party.is_empty() or party.size() > PARTY_CAPACITY or party[0] != "hero":
		return false
	for member_id in party:
		if not MEMBER_DEFS.has(member_id) or (member_id != "hero" and not snapshot["members"].has(member_id)):
			return false
	if snapshot.get("language", "") not in ["zh", "en"] or typeof(snapshot.get("jiRecordsChecked")) != TYPE_BOOL or typeof(snapshot.get("enemyCleared")) != TYPE_BOOL:
		return false
	if typeof(snapshot.get("relayChecked", false)) != TYPE_BOOL or typeof(snapshot.get("areasVisited", {})) != TYPE_DICTIONARY or typeof(snapshot.get("machineObserved", false)) != TYPE_BOOL or typeof(snapshot.get("demoCompleted", false)) != TYPE_BOOL:
		return false
	if typeof(snapshot.get("heroName", "")) != TYPE_STRING or snapshot.get("heroAppearance", "male") not in ["male", "female"]:
		return false
	for destination_id in snapshot.get("areasVisited", {}).keys():
		if not DESTINATIONS.has(destination_id) or snapshot["areasVisited"][destination_id] != true:
			return false
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
	_add_key_action("battle_job_skill", KEY_R)


func _add_key_action(action: StringName, key: Key) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action)
	var event := InputEventKey.new()
	event.physical_keycode = key
	InputMap.action_add_event(action, event)

