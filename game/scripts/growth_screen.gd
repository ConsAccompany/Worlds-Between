extends Control

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


func _ready() -> void:
	_build_ui()
	AppState.language_changed.connect(_refresh)
	_refresh()


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


func _label(at: Vector2, size: int, color: Color) -> Label:
	var label := Label.new()
	label.position = at
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	add_child(label)
	return label


func _button(at: Vector2, size: Vector2, callback: Callable) -> Button:
	var button := Button.new()
	button.position = at
	button.size = size
	button.add_theme_font_size_override("font_size", 11)
	button.pressed.connect(callback)
	add_child(button)
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
		if not skills_have_effect:
			button.text = AppState.text_for("growth_placeholder_skill") % skill_name
			button.disabled = true
	skill_label.text = AppState.text_for("growth_skill" if skills_have_effect else "growth_skill_placeholder") % " / ".join(unlocked)
	var personal_rank := int(member.get("personal_skill_rank", 1))
	var personal_series: String = AppState.MEMBER_DEFS[selected_id]["job_series"]
	var personal_cost := GrowthRules.jp_cost(member, personal_series, personal_rank + 1)
	var personal_name := AppState.text_for(String(AppState.MEMBER_DEFS[selected_id]["skill_key"]))
	personal_upgrade_button.text = AppState.text_for("growth_personal") % [personal_name, personal_rank, personal_cost] if personal_cost >= 0 else personal_name + " MAX"
	personal_upgrade_button.disabled = personal_cost < 0 or int(member.get("jp", 0)) < personal_cost
	var pending := int(member.get("pending_job_choices", 0)) > 0
	pending_label.text = AppState.text_for("growth_pending") if pending else (AppState.text_for("growth_merchant_note") if member["job_series"] == CommerceLedger.MERCHANT_SERIES_ID else "")
	stay_button.text = AppState.text_for("growth_stay")
	stay_button.disabled = not pending
	promote_button.text = AppState.text_for("growth_promote")
	promote_button.disabled = not pending or int(member["job_stage"]) >= 2
	for index in SERIES_IDS.size():
		var series_id: String = SERIES_IDS[index]
		series_buttons[index].text = AppState.text_for("growth_switch") % GrowthRules.stage_name(series_id, 1, AppState.language)
		series_buttons[index].disabled = not pending or series_id == member["job_series"] or not GrowthRules.can_enter(member, series_id)
