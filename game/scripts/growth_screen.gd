extends Control

const ManagementUiSkin := preload("res://scripts/rpg-2-star-ocean-the-second_management-ui_skin-helper_v01_20261019-173546-f3412b43.gd")
static var management_ui_skin_override := -1
var management_ui_skin: RefCounted = null
var management_ui_skin_status := "off"

const FemalePortraitPilot := preload("res://scripts/rpg-2-star-ocean-the-second_protagonist-female_display-portrait-helper_v01_20261019-182839-4d72f1c6.gd")
static var female_display_portrait_override := -1
static var female_display_portrait_manifest := "res://assets/portraits/female-display-v01/rpg-2-star-ocean-the-second_protagonist-female_display-portrait-manifest_v01_20261019-221307-97f0236e.json"
var female_display_portrait: Control = null

const MvpDisplayPortraits := preload("res://scripts/rpg-2-star-ocean-the-second_mvp-display_portrait-helper_v01_20261019-185434-7c95e421.gd")
static var mvp_display_portraits_override := -1
var mvp_display_portraits: Control = null

# Opt-in UNAPPROVED five-variant party-icon kit. This flag takes precedence over
# the legacy female/MVP display flags so only one portrait helper is ever created.
const CharacterUiPortraits := preload("res://scripts/rpg-2-star-ocean-the-second_character-ui-portraits_helper_v01_20261019-233832-b7c4e912.gd")
static var character_ui_portraits_override := -1
var character_ui_portraits: Control = null

const SERIES_IDS := ["sword", "firearms", "tactics", "relics", "merchant"]

var selected_id := "hero"
var title_label: Label
var info_label: Label
var aptitude_label: Label
var job_label: Label
var skill_label: Label
var pending_label: Label
var back_button: Button
var upgrade_buttons: Array[Button] = []
var personal_upgrade_button: Button
var stay_button: Button
var promote_button: Button
var member_buttons: Array[Button] = []
var series_buttons: Array[Button] = []
# Ten-node overlay: 10 career nodes (column = stage) and 10 personal nodes (by unlock order).
var nodes_button: Button
var node_panel: Control
var node_title_label: Label
var node_career_label: Label
var node_personal_label: Label
var node_summary_label: Label
var node_close_button: Button
var career_node_buttons: Array[Button] = []
var personal_node_buttons: Array[Button] = []
var career_node_ids: Array[String] = []
var personal_node_ids: Array[String] = []


func _ready() -> void:
	_build_ui()
	AppState.language_changed.connect(_refresh)
	_refresh()
	if management_ui_skin_override == 1 or (management_ui_skin_override < 0 and OS.get_cmdline_user_args().has("--management-ui-skin-pilot")):
		management_ui_skin = ManagementUiSkin.new("res://assets/ui/battle-skin-v01")
		management_ui_skin_status = "applied" if management_ui_skin.apply(self) else "fallback"
	var new_party_portraits := character_ui_portraits_override == 1 or (character_ui_portraits_override < 0 and CharacterUiPortraits.pilot_requested(OS.get_cmdline_user_args()))
	if new_party_portraits:
		character_ui_portraits = CharacterUiPortraits.new()
		character_ui_portraits.install_party(self, member_buttons)
		call_deferred("_refresh_character_ui_portraits")
	elif mvp_display_portraits_override == 1 or (mvp_display_portraits_override < 0 and MvpDisplayPortraits.pilot_requested(OS.get_cmdline_user_args())):
		mvp_display_portraits = MvpDisplayPortraits.new()
		mvp_display_portraits.install(self, node_panel)
		call_deferred("_refresh_display_portrait")
	elif female_display_portrait_override == 1 or (female_display_portrait_override < 0 and FemalePortraitPilot.pilot_requested(OS.get_cmdline_user_args())):
		female_display_portrait = FemalePortraitPilot.new()
		female_display_portrait.install(self, node_panel)
		call_deferred("_refresh_display_portrait")


func _build_ui() -> void:
	var background := ColorRect.new()
	background.color = Color("#122431")
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(background)
	title_label = _label(Vector2(20, 10), 20, Color("#e8f5e9"))
	back_button = _button(Vector2(500, 8), Vector2(121, 31), _leave)
	for index in AppState.PARTY_CAPACITY:
		var button := _button(Vector2(18 + index * 124, 47), Vector2(117, 29), _select.bind(index))
		member_buttons.append(button)
	info_label = _label(Vector2(21, 91), 14, Color("#e9d6aa"))
	aptitude_label = _label(Vector2(21, 121), 11, Color("#b6d5d0"))
	job_label = _label(Vector2(21, 148), 14, Color("#b7dfcd"))
	skill_label = _label(Vector2(21, 174), 12, Color("#d5e8dc"))
	pending_label = _label(Vector2(21, 201), 12, Color("#f6c3a0"))
	for stage in 2:
		upgrade_buttons.append(_button(Vector2(20 + stage * 151, 225), Vector2(146, 31), _upgrade.bind(stage)))
	stay_button = _button(Vector2(329, 225), Vector2(141, 31), _choose.bind("stay", ""))
	promote_button = _button(Vector2(478, 225), Vector2(143, 31), _choose.bind("promote", ""))
	for index in SERIES_IDS.size():
		var series_button := _button(Vector2(20 + index * 122, 279), Vector2(116, 41), _choose.bind("switch", SERIES_IDS[index]))
		series_button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		series_buttons.append(series_button)
	personal_upgrade_button = _button(Vector2(20, 324), Vector2(300, 29), _upgrade_personal)
	nodes_button = _button(Vector2(329, 324), Vector2(141, 29), _show_nodes.bind(true))
	_build_node_panel()


func _build_node_panel() -> void:
	node_panel = Control.new()
	node_panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	node_panel.visible = false
	add_child(node_panel)
	var shade := ColorRect.new()
	shade.color = Color("#0f1d28")
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	node_panel.add_child(shade)
	node_title_label = _label(Vector2(20, 10), 18, Color("#e8f5e9"), node_panel)
	node_close_button = _button(Vector2(500, 8), Vector2(121, 31), _show_nodes.bind(false), node_panel)
	node_career_label = _label(Vector2(20, 44), 11, Color("#b7dfcd"), node_panel)
	for index in 10:
		career_node_buttons.append(_node_button(Vector2(20 + (index / 2) * 122, 62 + (index % 2) * 37), _upgrade_career_node.bind(index)))
	node_personal_label = _label(Vector2(20, 140), 11, Color("#e9d6aa"), node_panel)
	for index in 10:
		personal_node_buttons.append(_node_button(Vector2(20 + (index % 5) * 122, 158 + (index / 5) * 37), _upgrade_personal_node.bind(index)))
	node_summary_label = _label(Vector2(20, 236), 11, Color("#d5e8dc"), node_panel)
	node_summary_label.size = Vector2(600, 110)
	node_summary_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART


func _node_button(at: Vector2, callback: Callable) -> Button:
	var button := _button(at, Vector2(116, 33), callback, node_panel)
	button.add_theme_font_size_override("font_size", 10)
	button.clip_text = true
	return button


func _label(at: Vector2, size: int, color: Color, parent: Node = self) -> Label:
	var label := Label.new()
	label.position = at
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	parent.add_child(label)
	return label


func _button(at: Vector2, size: Vector2, callback: Callable, parent: Node = self) -> Button:
	var button := Button.new()
	button.position = at
	button.size = size
	button.add_theme_font_size_override("font_size", 11)
	button.pressed.connect(callback)
	parent.add_child(button)
	return button


func _select(index: int) -> void:
	if index < AppState.active_party_ids.size():
		selected_id = AppState.active_party_ids[index]
		_refresh()


func _choose(action: String, series_id: String) -> void:
	if AppState.choose_job(selected_id, action, series_id):
		for member_id in AppState.active_party_ids:
			if int(AppState.member_state(member_id).get("pending_job_choices", 0)) > 0:
				selected_id = member_id
				break
		_refresh()


func _upgrade(stage: int) -> void:
	var member: Dictionary = AppState.member_state(selected_id)
	var skill_id: String = GrowthRules.SERIES[String(member["job_series"])]["skills"][stage]
	AppState.upgrade_job_skill(selected_id, skill_id)
	_refresh()


func _upgrade_personal() -> void:
	AppState.upgrade_personal_skill(selected_id)
	_refresh()


func _show_nodes(shown: bool) -> void:
	node_panel.visible = shown
	_refresh()


func _upgrade_career_node(index: int) -> void:
	if index < career_node_ids.size():
		AppState.upgrade_job_skill(selected_id, career_node_ids[index])
		_refresh()


func _upgrade_personal_node(index: int) -> void:
	if index < personal_node_ids.size():
		AppState.upgrade_personal_node(selected_id, personal_node_ids[index])
		_refresh()


func _leave() -> void:
	if AppState.has_pending_job_choice():
		return
	get_tree().change_scene_to_file(AppState.growth_return_scene)


func _refresh() -> void:
	var member := AppState.member_state(selected_id)
	if member.is_empty():
		return
	title_label.text = AppState.text_for("growth_title")
	back_button.text = AppState.text_for("growth_back")
	back_button.disabled = AppState.has_pending_job_choice()
	for index in member_buttons.size():
		member_buttons[index].visible = index < AppState.active_party_ids.size()
		if index < AppState.active_party_ids.size():
			var id: String = AppState.active_party_ids[index]
			member_buttons[index].text = AppState.member_name(id) + (" !" if int(AppState.member_state(id).get("pending_job_choices", 0)) > 0 else "")
			member_buttons[index].disabled = id == selected_id
	info_label.text = AppState.member_name(selected_id) + " · " + (AppState.text_for("growth_level") % [int(member["level"]), int(member.get("xp", 0)), GrowthRules.xp_to_next(int(member["level"])), int(member.get("jp", 0))])
	var aptitudes: Array = member.get("aptitudes", [60, 60, 60, 60])
	aptitude_label.text = AppState.text_for("growth_aptitudes") % [int(aptitudes[0]), int(aptitudes[1]), int(aptitudes[2]), int(aptitudes[3])]
	job_label.text = AppState.text_for("growth_job") % [GrowthRules.stage_name(String(member["job_series"]), int(member["job_stage"]), AppState.language), int(member["job_stage"])]
	var unlocked: Array[String] = []
	var skills_have_effect := GrowthRules.job_skills_have_effect(String(member["job_series"]))
	for stage in upgrade_buttons.size():
		var skill_id: String = GrowthRules.SERIES[String(member["job_series"])]["skills"][stage]
		var button: Button = upgrade_buttons[stage]
		button.visible = stage < int(member["job_stage"])
		if not button.visible:
			continue
		var skill_name := AppState.text_for("job_skill_" + skill_id)
		var rank := GrowthRules.skill_rank(member, skill_id)
		unlocked.append("%s Lv%d" % [skill_name, rank])
		var cost := GrowthRules.jp_cost(member, String(member["job_series"]), rank + 1)
		button.text = AppState.text_for("growth_upgrade") % [skill_name, cost] if cost >= 0 else skill_name + " MAX"
		button.disabled = cost < 0 or int(member.get("jp", 0)) < cost
		if not GrowthRules.job_skill_upgradable(String(member["job_series"]), skill_id):
			button.text = AppState.text_for("growth_placeholder_skill") % skill_name
			button.disabled = true
		elif AppState.fair_quote_frozen(selected_id, skill_id):
			button.text = AppState.text_for("growth_fair_quote_frozen_button") % skill_name
			button.disabled = true
	skill_label.text = AppState.text_for("growth_skill" if skills_have_effect else "growth_skill_placeholder") % " / ".join(unlocked)
	var personal_rank := int(member.get("personal_skill_rank", 1))
	var personal_series: String = AppState.MEMBER_DEFS[selected_id]["job_series"]
	var personal_cost := GrowthRules.jp_cost(member, personal_series, personal_rank + 1)
	var personal_name := AppState.text_for(String(AppState.MEMBER_DEFS[selected_id]["skill_key"]))
	personal_upgrade_button.text = AppState.text_for("growth_personal") % [personal_name, personal_rank, personal_cost] if personal_cost >= 0 else personal_name + " MAX"
	personal_upgrade_button.disabled = personal_cost < 0 or int(member.get("jp", 0)) < personal_cost
	var pending := int(member.get("pending_job_choices", 0)) > 0
	var fair_quote_rank := GrowthRules.fair_quote_rank(member)
	var merchant_note := AppState.text_for("growth_fair_quote_note") % [fair_quote_rank, CommerceLedger.companion_rate_percent(fair_quote_rank) - 100] if fair_quote_rank > 0 else AppState.text_for("growth_merchant_note")
	if fair_quote_rank > 0 and AppState.fair_quote_frozen(selected_id):
		merchant_note = AppState.text_for("growth_fair_quote_frozen")
	pending_label.text = AppState.text_for("growth_pending") if pending else (merchant_note if member["job_series"] == CommerceLedger.MERCHANT_SERIES_ID else "")
	stay_button.text = AppState.text_for("growth_stay")
	stay_button.disabled = not pending
	var can_promote := GrowthRules.can_promote(member, AppState.cleared_final_quests)
	var final_quest_blocked := int(member["job_stage"]) == GrowthRules.LEVEL_CHOICE_STAGE_CAP and not can_promote
	promote_button.text = AppState.text_for("growth_promote_final_quest" if final_quest_blocked else "growth_promote")
	promote_button.disabled = not pending or not can_promote
	for index in SERIES_IDS.size():
		var series_id: String = SERIES_IDS[index]
		series_buttons[index].text = AppState.text_for("growth_switch") % GrowthRules.stage_name(series_id, 1, AppState.language)
		series_buttons[index].disabled = not pending or series_id == member["job_series"] or not GrowthRules.can_enter(member, series_id)
	nodes_button.text = AppState.text_for("growth_nodes_open")
	if node_panel.visible:
		_refresh_nodes(member)
	if character_ui_portraits != null:
		call_deferred("_refresh_character_ui_portraits")
	elif female_display_portrait != null or mvp_display_portraits != null:
		call_deferred("_refresh_display_portrait")


func _refresh_nodes(member: Dictionary) -> void:
	var series_id := String(member["job_series"])
	var jp := int(member.get("jp", 0))
	node_title_label.text = AppState.text_for("growth_nodes_title") % AppState.member_name(selected_id)
	node_close_button.text = AppState.text_for("growth_nodes_close")
	node_career_label.text = AppState.text_for("growth_nodes_career") % GrowthRules.stage_name(series_id, int(member["job_stage"]), AppState.language)
	node_personal_label.text = AppState.text_for("growth_nodes_personal")
	career_node_ids.clear()
	var career_effects := 0
	var career_frozen := false
	var nodes: Array = GrowthRules.career_nodes(series_id)
	for index in career_node_buttons.size():
		var button: Button = career_node_buttons[index]
		button.visible = index < nodes.size()
		if not button.visible:
			continue
		var node: Dictionary = nodes[index]
		var node_id := String(node["id"])
		career_node_ids.append(node_id)
		var has_effect := GrowthRules.job_skill_upgradable(series_id, node_id)
		career_effects += 1 if has_effect else 0
		var node_name := AppState.text_for(String(node["nameKey"])) if node.has("nameKey") else AppState.text_for("growth_node_career_name") % [int(node["stage"]), String(node["slot"]).to_upper()]
		var rank := GrowthRules.skill_rank(member, node_id)
		var cost := GrowthRules.jp_cost(member, series_id, rank + 1)
		var opened := GrowthRules.job_node_open(member, series_id, node_id)
		button.text = node_name + "\n" + _node_state_text(opened, has_effect, rank, cost, AppState.text_for("growth_node_stage_locked") % int(node["stage"]))
		button.disabled = not opened or not has_effect or cost < 0 or jp < cost
		if opened and has_effect and AppState.fair_quote_frozen(selected_id, node_id):
			button.text = node_name + "\n" + AppState.text_for("growth_node_frozen") % rank
			button.disabled = true
			career_frozen = true
	personal_node_ids.clear()
	var personal_effects := 0
	var personal: Array = GrowthRules.personal_nodes(selected_id)
	var home_series := String(AppState.MEMBER_DEFS[selected_id]["job_series"])
	for index in personal_node_buttons.size():
		var button: Button = personal_node_buttons[index]
		button.visible = index < personal.size()
		if not button.visible:
			continue
		var node: Dictionary = personal[index]
		var node_id := String(node["id"])
		personal_node_ids.append(node_id)
		var has_effect := GrowthRules.personal_node_upgradable(selected_id, node_id)
		personal_effects += 1 if has_effect else 0
		var node_name := AppState.text_for(String(node["nameKey"])) if node.has("nameKey") else AppState.text_for("growth_node_personal_name") % int(node["order"])
		var rank := GrowthRules.personal_node_rank(member, selected_id, node_id)
		var cost := GrowthRules.jp_cost(member, home_series, rank + 1)
		button.text = node_name + "\n" + _node_state_text(rank >= 1, has_effect, rank, cost, AppState.text_for("growth_node_level_locked") % int(node["unlockLevel"]))
		button.disabled = rank < 1 or not has_effect or cost < 0 or jp < cost
	var quest_state := AppState.text_for("growth_final_quest_done" if AppState.cleared_final_quests.has(series_id) else "growth_final_quest_pending")
	node_summary_label.text = AppState.text_for("growth_nodes_summary") % [career_effects, personal_effects] + "\n" + AppState.text_for("growth_nodes_final_quest") % quest_state
	if career_frozen:
		node_summary_label.text += "\n" + AppState.text_for("growth_fair_quote_frozen")


func _node_state_text(opened: bool, has_effect: bool, rank: int, cost: int, locked_text: String) -> String:
	if not opened:
		return locked_text
	if not has_effect:
		return AppState.text_for("growth_node_skeleton") % rank
	if cost < 0:
		return AppState.text_for("growth_node_max") % rank
	return AppState.text_for("growth_node_upgrade") % [rank, cost]


func _refresh_character_ui_portraits() -> void:
	if character_ui_portraits != null:
		character_ui_portraits.apply_party(AppState.active_party_ids, AppState.hero_appearance, true)


func _refresh_display_portrait() -> void:
	if mvp_display_portraits != null:
		mvp_display_portraits.update(AppState.hero_appearance, selected_id, not node_panel.visible)
	elif female_display_portrait != null:
		female_display_portrait.apply_appstate(female_display_portrait_manifest, AppState, "hero", selected_id, not node_panel.visible, true)


func _exit_tree() -> void:
	if character_ui_portraits != null:
		character_ui_portraits.revert()
		character_ui_portraits = null
	if mvp_display_portraits != null:
		mvp_display_portraits.revert()
	if female_display_portrait != null:
		female_display_portrait.revert()
	if management_ui_skin != null:
		management_ui_skin.revert()
