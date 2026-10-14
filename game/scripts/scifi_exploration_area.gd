extends Node2D

const HERO_SPRITE_MALE := preload("res://assets/characters/rpg-2-star-ocean-the-second_protagonist_exploration-sprite-male_m7_20261013-211119-a51e0b63.svg")
const HERO_SPRITE_FEMALE := preload("res://assets/characters/rpg-2-star-ocean-the-second_protagonist_exploration-sprite-female_m7_20261013-211119-8c2d9e47.svg")
const CITY_BACKGROUND := preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-city_environment-background_m8-v02_20261013-232003-48d0ab67.png")
const CITY_HERO_MALE := preload("res://assets/characters/rpg-2-star-ocean-the-second_protagonist-male_exploration-cutout_m8-sample_20261013-231655-70b1e89d.png")
const CITY_HERO_FEMALE := preload("res://assets/characters/rpg-2-star-ocean-the-second_protagonist-female_exploration-cutout_m8-sample_20261013-233258-e2c0419a.png")
const CITY_LIANG_XU := preload("res://assets/characters/rpg-2-star-ocean-the-second_liang-xu_exploration-cutout_m8-sample_20261013-231655-2f45a173.png")
const BATTLE_SCENE := preload("res://scenes/battle_arena.tscn")
const MOVE_SPEED := 140.0
const SPAWN := Vector2(82, 260)
const CITY_SPAWN := Vector2(340, 253)
const RECORDS_POSITION := Vector2(320, 250)
const RELAY_POSITION := Vector2(470, 128)
const REPORT_POSITION := Vector2(470, 247)
const SURVEY_ENTRANCES := {
	"scifi.city": Vector2(558, 166),
	"scifi.outskirts": Vector2(558, 277),
	"scifi.ruins": Vector2(548, 142),
}
const FIELD_ASSISTS := {
	"scifi.city": {"position": Vector2(120, 187), "member": "liang-xu"},
	"scifi.outskirts": {"position": Vector2(505, 258), "member": "zhao-ling"},
	"scifi.ruins": {"position": Vector2(505, 275), "member": "ji-cheng"},
}
const FIELD_TRACES := {
	"scifi.city": [Vector2(285, 267), Vector2(378, 181)],
	"scifi.outskirts": [Vector2(125, 240), Vector2(408, 95)],
	"scifi.ruins": [Vector2(115, 245), Vector2(470, 115)],
}
const AMBIENCE := {
	"scifi.city": "res://assets/audio/rpg-2-star-ocean-the-second_scifi-city_ambient-loop_m7_20261013-211230-c8e1159a.wav",
	"scifi.outskirts": "res://assets/audio/rpg-2-star-ocean-the-second_scifi-outskirts_ambient-loop_m7_20261013-211230-57ad4b20.wav",
	"scifi.ruins": "res://assets/audio/rpg-2-star-ocean-the-second_scifi-ruins_ambient-loop_m7_20261013-211230-6be0d93f.wav",
}
const DISCOVERY_CUE := preload("res://assets/audio/rpg-2-star-ocean-the-second_discovery_interaction-cue_m7_20261013-211230-ad781e52.wav")
const AREA_CONFIG := {
	"scifi.city": {"npc": Vector2(282, 180), "recruit": "liang-xu", "enemy": Vector2(-100, -100), "color": Color("#365463")},
	"scifi.outskirts": {"npc": Vector2(190, 150), "recruit": "zhao-ling", "enemy": Vector2(355, 238), "color": Color("#546b57")},
	"scifi.ruins": {"npc": Vector2(200, 145), "recruit": "ji-cheng", "enemy": Vector2(420, 225), "color": Color("#70644f")},
}

var destination_id := ""
var hero: Sprite2D
var city_npc: Sprite2D
var npc_position := Vector2.ZERO
var recruit_id := ""
var enemy_position := Vector2(-100, -100)
var enemy_visible := false
var encounter_count := 0
var bypass_reached := false
var safe_position := SPAWN
var title_label: Label
var hint_label: Label
var help_label: Label
var feedback_label: Label
var enemy_label: Label
var back_button: Button
var save_button: Button
var npc_label: Label
var records_label: Label
var station_label: Label
var survey_label: Label
var assist_label: Label
var trace_labels: Array[Label] = []
var dialogue_overlay: ColorRect
var dialogue_title: Label
var dialogue_text: Label
var invite_button: Button
var later_button: Button
var dialogue_open := false
var dialogue_mode := "recruit"
var trace_index := -1
var feedback_key := "npc_prompt"
var feedback_message := ""
var cue_player: AudioStreamPlayer


func _ready() -> void:
	destination_id = AppState.current_destination_id
	if not AREA_CONFIG.has(destination_id):
		destination_id = "scifi.city"
	AppState.record_playtest_event("location", destination_id)
	var config: Dictionary = AREA_CONFIG[destination_id]
	npc_position = config["npc"]
	recruit_id = config["recruit"]
	enemy_position = config["enemy"]
	enemy_visible = destination_id != "scifi.city" and not AppState.enemy_cleared_for_return
	if destination_id == "scifi.city":
		texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	_build_actors()
	if AppState.returning_from_battle:
		hero.position = AppState.battle_return_position
		AppState.returning_from_battle = false
	elif AppState.resume_area_pending:
		hero.position = AppState.resume_area_position
		AppState.resume_area_pending = false
	if destination_id == "scifi.city":
		hero.position = _city_safe_position(hero.position)
		hero.z_index = int(hero.position.y)
	safe_position = hero.position
	if not AppState.areas_visited.has(destination_id):
		AppState.record_playtest_event("visit", destination_id)
	AppState.areas_visited[destination_id] = true
	_build_ui()
	_start_audio()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()


func _process(delta: float) -> void:
	if dialogue_open:
		return
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var was_in_bypass_zone := hero.position.x > 545.0 and hero.position.y < 205.0
	if direction != Vector2.ZERO:
		var next_position := hero.position + direction * MOVE_SPEED * delta
		if destination_id == "scifi.city":
			next_position = _city_slide_position(next_position)
		else:
			next_position.x = clampf(next_position.x, 24.0, 616.0)
			next_position.y = clampf(next_position.y, 77.0, 306.0)
		hero.position = next_position
		if destination_id == "scifi.city":
			hero.z_index = int(hero.position.y)
		if enemy_visible:
			if hero.position.distance_to(enemy_position) > 43.0:
				safe_position = hero.position
			if hero.position.distance_to(enemy_position) < 23.0:
				_open_encounter()
	if enemy_visible and not bypass_reached and direction != Vector2.ZERO and not was_in_bypass_zone and hero.position.x > 545.0 and hero.position.y < 205.0:
		bypass_reached = true
		if not AppState.machine_observed:
			AppState.record_playtest_event("machine_bypass", destination_id)
		AppState.machine_observed = true
		feedback_key = "bypass_notice"
		_refresh_text()


func _draw() -> void:
	if not AREA_CONFIG.has(destination_id):
		return
	if destination_id == "scifi.city":
		draw_texture_rect(CITY_BACKGROUND, Rect2(0, 0, 640, 360), false)
		_draw_city_hotspots()
		return
	var color: Color = AREA_CONFIG[destination_id]["color"]
	draw_rect(Rect2(0, 0, 640, 360), Color("#13232d"))
	draw_rect(Rect2(16, 67, 608, 250), color)
	for x in range(16, 624, 32):
		draw_line(Vector2(x, 67), Vector2(x, 317), color.lightened(0.08), 1.0)
	for y in range(67, 318, 32):
		draw_line(Vector2(16, y), Vector2(624, y), color.lightened(0.08), 1.0)
	match destination_id:
		"scifi.outskirts":
			_draw_outskirts()
		"scifi.ruins":
			_draw_ruins()
	if not AppState.recruited_members.has(recruit_id):
		_draw_npc()
	if enemy_visible:
		_draw_enemy()
		draw_rect(Rect2(566, 88, 13, 34), Color("#a2ded1"))
		draw_rect(Rect2(579, 88, 4, 34), Color("#233c47"))
	if destination_id == "scifi.outskirts":
		draw_rect(Rect2(RELAY_POSITION + Vector2(-18, -15), Vector2(36, 30)), Color("#1d3948"))
		draw_rect(Rect2(RELAY_POSITION + Vector2(-12, -9), Vector2(24, 15)), Color("#8fdecf" if AppState.relay_checked else "#e5bb77"))
	if destination_id == "scifi.city":
		draw_rect(Rect2(REPORT_POSITION + Vector2(-23, -14), Vector2(46, 28)), Color("#213b49"))
		draw_rect(Rect2(REPORT_POSITION + Vector2(-16, -8), Vector2(32, 15)), Color("#99d8c9"))
	var entrance: Vector2 = SURVEY_ENTRANCES[destination_id]
	draw_rect(Rect2(entrance + Vector2(-17, -21), Vector2(34, 42)), Color("#19313d"))
	draw_rect(Rect2(entrance + Vector2(-11, -16), Vector2(22, 33)), Color("#80d0c4" if AppState.survey_solved.has(destination_id) else "#d8be7f"))
	var assist_position: Vector2 = FIELD_ASSISTS[destination_id]["position"]
	draw_rect(Rect2(assist_position + Vector2(-15, -12), Vector2(30, 24)), Color("#172d39"))
	draw_rect(Rect2(assist_position + Vector2(-10, -7), Vector2(20, 14)), Color("#80d0c4" if AppState.field_insights.has(destination_id) else "#e3bf78"))
	for index in 2:
		var trace_position: Vector2 = FIELD_TRACES[destination_id][index]
		var recorded: bool = AppState.field_traces.has("%s:%d" % [destination_id, index])
		draw_circle(trace_position, 12.0, Color("#19313d"))
		draw_circle(trace_position, 7.0, Color("#80d0c4" if recorded else "#f4ca81"))
		draw_circle(trace_position, 2.0, Color("#17323d"))


func _draw_city_hotspots() -> void:
	_draw_city_marker(REPORT_POSITION, Color("#75d8ce"))
	_draw_city_marker(SURVEY_ENTRANCES[destination_id], Color("#75d8ce" if AppState.survey_solved.has(destination_id) else "#f2cb81"))
	_draw_city_marker(FIELD_ASSISTS[destination_id]["position"], Color("#75d8ce" if AppState.field_insights.has(destination_id) else "#f2cb81"))
	for index in 2:
		var recorded: bool = AppState.field_traces.has("%s:%d" % [destination_id, index])
		_draw_city_marker(FIELD_TRACES[destination_id][index], Color("#75d8ce" if recorded else "#f2cb81"))


func _draw_city_marker(at: Vector2, color: Color) -> void:
	draw_circle(at, 9.0, Color(color.r, color.g, color.b, 0.30))
	draw_arc(at, 8.0, 0.0, TAU, 24, Color(color.r, color.g, color.b, 0.85), 1.4)
	draw_circle(at, 2.0, color)


func _city_safe_position(at: Vector2) -> Vector2:
	var safe := Vector2(clampf(at.x, 24.0, 616.0), clampf(at.y, 160.0, 305.0))
	if safe.x < 252.0 and safe.y > 208.0:
		safe.y = 208.0
	return safe


func _city_slide_position(at: Vector2) -> Vector2:
	var bounded := Vector2(clampf(at.x, 24.0, 616.0), clampf(at.y, 160.0, 305.0))
	if _city_walkable(bounded):
		return bounded
	var horizontal := Vector2(bounded.x, hero.position.y)
	if _city_walkable(horizontal):
		return horizontal
	var vertical := Vector2(hero.position.x, bounded.y)
	if _city_walkable(vertical):
		return vertical
	return hero.position


func _city_walkable(at: Vector2) -> bool:
	return at.x >= 24.0 and at.x <= 616.0 and at.y >= 160.0 and at.y <= 305.0 and not (at.x < 252.0 and at.y > 208.0)


func _draw_outskirts() -> void:
	draw_rect(Rect2(45, 112, 550, 37), Color("#839381"))
	draw_rect(Rect2(33, 176, 570, 28), Color("#718e80"))
	draw_rect(Rect2(55, 266, 520, 20), Color("#6f8978"))
	draw_line(Vector2(80, 115), Vector2(525, 100), Color("#98b2ad"), 3.0)
	for x in range(90, 580, 75):
		draw_rect(Rect2(x, 82, 6, 56), Color("#334c4c"))
		draw_rect(Rect2(x + 20, 286, 24, 7), Color("#304a3d"))


func _draw_ruins() -> void:
	draw_rect(Rect2(43, 90, 554, 204), Color("#8c8066"))
	draw_rect(Rect2(72, 108, 496, 170), Color("#5d665b"))
	for x in [115, 280, 530]:
		draw_rect(Rect2(x, 94, 22, 65), Color("#c2b18a"))
		draw_rect(Rect2(x - 7, 91, 36, 8), Color("#dec397"))
	draw_rect(Rect2(274, 265, 90, 18), Color("#b4a17d"))
	draw_rect(Rect2(300, 246, 39, 19), Color("#2a4a53"))


func _draw_npc() -> void:
	var color: Color = AppState.MEMBER_DEFS[recruit_id]["color"]
	draw_circle(npc_position + Vector2(0, 10), 15.0, Color("#1a333c"))
	draw_rect(Rect2(npc_position + Vector2(-8, -15), Vector2(16, 28)), color)
	draw_circle(npc_position + Vector2(0, -17), 9.0, Color("#e1c49a"))
	match recruit_id:
		"liang-xu":
			draw_rect(Rect2(npc_position + Vector2(-9, -27), Vector2(18, 5)), Color("#c6c5bf"))
			draw_circle(npc_position + Vector2(10, -23), 5.0, Color("#b0b4b6"))
			draw_rect(Rect2(npc_position + Vector2(5, -5), Vector2(7, 10)), Color("#ba9973"))
		"zhao-ling":
			draw_rect(Rect2(npc_position + Vector2(-9, -27), Vector2(18, 5)), Color("#263747"))
			draw_circle(npc_position + Vector2(-9, -17), 4.0, Color("#66c7e1"))
			draw_circle(npc_position + Vector2(9, -17), 4.0, Color("#66c7e1"))
		"ji-cheng":
			draw_rect(Rect2(npc_position + Vector2(-9, -27), Vector2(14, 6)), Color("#aeb8ba"))
			draw_rect(Rect2(npc_position + Vector2(5, -24), Vector2(5, 14)), Color("#27363d"))


func _draw_enemy() -> void:
	draw_circle(enemy_position, 24.0, Color(0.62, 0.20, 0.22, 0.32))
	draw_rect(Rect2(enemy_position + Vector2(-13, -14), Vector2(26, 27)), Color("#8a3a42"))
	draw_rect(Rect2(enemy_position + Vector2(-8, -8), Vector2(16, 8)), Color("#eaa88b"))
	draw_rect(Rect2(enemy_position + Vector2(-17, 11), Vector2(8, 7)), Color("#463942"))
	draw_rect(Rect2(enemy_position + Vector2(9, 11), Vector2(8, 7)), Color("#463942"))


func _build_actors() -> void:
	hero = Sprite2D.new()
	if destination_id == "scifi.city":
		hero.texture = CITY_HERO_FEMALE if AppState.hero_appearance == "female" else CITY_HERO_MALE
		hero.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		hero.scale = Vector2(0.054, 0.054)
		hero.offset = Vector2(0, -704)
		hero.position = CITY_SPAWN
		hero.z_index = int(hero.position.y)
		city_npc = Sprite2D.new()
		city_npc.texture = CITY_LIANG_XU
		city_npc.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		city_npc.scale = Vector2(0.054, 0.054)
		city_npc.offset = Vector2(0, -704)
		city_npc.position = npc_position
		city_npc.z_index = int(npc_position.y)
		city_npc.visible = not AppState.recruited_members.has(recruit_id)
		add_child(city_npc)
	else:
		hero.texture = HERO_SPRITE_FEMALE if AppState.hero_appearance == "female" else HERO_SPRITE_MALE
		hero.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		hero.scale = Vector2(2, 2)
		hero.position = SPAWN
	add_child(hero)


func _start_audio() -> void:
	var ambient_player := AudioStreamPlayer.new()
	var ambient: AudioStreamWAV = load(AMBIENCE[destination_id]).duplicate()
	ambient.loop_mode = AudioStreamWAV.LOOP_FORWARD
	ambient_player.stream = ambient
	ambient_player.volume_db = -11.0
	add_child(ambient_player)
	ambient_player.play()
	cue_player = AudioStreamPlayer.new()
	cue_player.stream = DISCOVERY_CUE
	cue_player.volume_db = -7.0
	add_child(cue_player)


func _build_ui() -> void:
	var canvas := CanvasLayer.new()
	add_child(canvas)
	var header := ColorRect.new()
	header.color = Color("#0d1723")
	header.size = Vector2(640, 62)
	canvas.add_child(header)
	title_label = Label.new()
	title_label.position = Vector2(18, 5)
	title_label.add_theme_font_size_override("font_size", 18)
	title_label.add_theme_color_override("font_color", Color("#f0f8f4"))
	canvas.add_child(title_label)
	hint_label = Label.new()
	hint_label.position = Vector2(18, 33)
	hint_label.add_theme_font_size_override("font_size", 11)
	hint_label.add_theme_color_override("font_color", Color("#acc8c8"))
	canvas.add_child(hint_label)
	back_button = Button.new()
	back_button.position = Vector2(525, 12)
	back_button.size = Vector2(98, 38)
	back_button.pressed.connect(_return_to_map)
	canvas.add_child(back_button)
	save_button = Button.new()
	save_button.position = Vector2(418, 12)
	save_button.size = Vector2(98, 38)
	save_button.pressed.connect(_open_save)
	canvas.add_child(save_button)
	var footer := ColorRect.new()
	footer.color = Color("#0d1723")
	footer.position = Vector2(0, 318)
	footer.size = Vector2(640, 42)
	canvas.add_child(footer)
	feedback_label = Label.new()
	feedback_label.position = Vector2(18, 322)
	feedback_label.add_theme_font_size_override("font_size", 11)
	feedback_label.add_theme_color_override("font_color", Color("#e7cf9c"))
	canvas.add_child(feedback_label)
	help_label = Label.new()
	help_label.position = Vector2(18, 340)
	help_label.add_theme_font_size_override("font_size", 10)
	help_label.add_theme_color_override("font_color", Color("#9dbab9"))
	canvas.add_child(help_label)
	enemy_label = Label.new()
	enemy_label.position = enemy_position + Vector2(-39, -47)
	enemy_label.add_theme_font_size_override("font_size", 10)
	enemy_label.add_theme_color_override("font_color", Color("#ffe0cd"))
	enemy_label.visible = enemy_visible
	canvas.add_child(enemy_label)
	npc_label = Label.new()
	npc_label.position = npc_position + Vector2(-38, -49)
	npc_label.add_theme_font_size_override("font_size", 11)
	npc_label.add_theme_color_override("font_color", Color("#f4e6b9"))
	canvas.add_child(npc_label)
	records_label = Label.new()
	records_label.position = RECORDS_POSITION + Vector2(-25, -37)
	records_label.add_theme_font_size_override("font_size", 11)
	records_label.add_theme_color_override("font_color", Color("#e9dba8"))
	canvas.add_child(records_label)
	station_label = Label.new()
	station_label.position = (RELAY_POSITION if destination_id == "scifi.outskirts" else REPORT_POSITION) + Vector2(-40, -42)
	station_label.add_theme_font_size_override("font_size", 11)
	station_label.add_theme_color_override("font_color", Color("#f0dda8"))
	canvas.add_child(station_label)
	survey_label = Label.new()
	survey_label.position = SURVEY_ENTRANCES[destination_id] + Vector2(-50, -42)
	survey_label.add_theme_font_size_override("font_size", 11)
	survey_label.add_theme_color_override("font_color", Color("#f0dda8"))
	canvas.add_child(survey_label)
	assist_label = Label.new()
	assist_label.position = FIELD_ASSISTS[destination_id]["position"] + Vector2(-46, -38)
	assist_label.add_theme_font_size_override("font_size", 10)
	assist_label.add_theme_color_override("font_color", Color("#f0dda8"))
	canvas.add_child(assist_label)
	for index in 2:
		var trace_label := Label.new()
		trace_label.position = FIELD_TRACES[destination_id][index] + Vector2(-23, -34)
		trace_label.add_theme_font_size_override("font_size", 10)
		trace_label.add_theme_color_override("font_color", Color("#f0dda8"))
		canvas.add_child(trace_label)
		trace_labels.append(trace_label)
	_build_dialogue(canvas)


func _build_dialogue(canvas: CanvasLayer) -> void:
	dialogue_overlay = ColorRect.new()
	dialogue_overlay.color = Color(0.04, 0.08, 0.12, 0.82)
	dialogue_overlay.size = Vector2(640, 360)
	dialogue_overlay.visible = false
	canvas.add_child(dialogue_overlay)
	var panel := ColorRect.new()
	panel.position = Vector2(87, 93)
	panel.size = Vector2(466, 185)
	panel.color = Color("#263e48")
	dialogue_overlay.add_child(panel)
	dialogue_title = Label.new()
	dialogue_title.position = Vector2(110, 109)
	dialogue_title.add_theme_font_size_override("font_size", 19)
	dialogue_title.add_theme_color_override("font_color", Color("#f1e5c6"))
	dialogue_overlay.add_child(dialogue_title)
	dialogue_text = Label.new()
	dialogue_text.position = Vector2(110, 143)
	dialogue_text.size = Vector2(419, 74)
	dialogue_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dialogue_overlay.add_child(dialogue_text)
	invite_button = Button.new()
	invite_button.position = Vector2(110, 228)
	invite_button.size = Vector2(183, 35)
	invite_button.pressed.connect(_dialogue_primary)
	dialogue_overlay.add_child(invite_button)
	later_button = Button.new()
	later_button.position = Vector2(331, 228)
	later_button.size = Vector2(198, 35)
	later_button.pressed.connect(_close_dialogue)
	dialogue_overlay.add_child(later_button)


func _refresh_text() -> void:
	var key := destination_id.trim_prefix("scifi.")
	title_label.text = AppState.destination_name(destination_id)
	hint_label.text = AppState.text_for("area_" + key + "_hint")
	help_label.text = AppState.text_for("area_help")
	var feedback_text := AppState.text_for(feedback_key)
	if feedback_key == "field_assist_reward":
		feedback_text = feedback_text % AppState.member_name(FIELD_ASSISTS[destination_id]["member"])
	feedback_label.text = feedback_message if feedback_message != "" else feedback_text
	back_button.text = AppState.text_for("area_back")
	save_button.text = AppState.text_for("save_open")
	enemy_label.text = AppState.text_for("enemy_label")
	npc_label.text = AppState.member_name(recruit_id)
	npc_label.visible = not AppState.recruited_members.has(recruit_id)
	if city_npc != null:
		city_npc.visible = npc_label.visible
	records_label.text = AppState.text_for("relic_marker")
	records_label.visible = destination_id == "scifi.ruins" and not AppState.ji_records_checked
	station_label.visible = destination_id != "scifi.ruins"
	station_label.text = AppState.text_for("relay_marker" if destination_id == "scifi.outskirts" else "report_marker")
	survey_label.text = AppState.text_for("survey_marker")
	assist_label.text = AppState.text_for("field_assist_marker_" + key)
	for index in 2:
		trace_labels[index].text = AppState.text_for("field_trace_marker") + " %d" % (index + 1)
	if dialogue_mode == "trace":
		dialogue_title.text = AppState.text_for("field_trace_marker") + " %d/2" % (trace_index + 1)
		dialogue_text.text = AppState.text_for("field_trace_" + key + "_%d" % trace_index)
		invite_button.visible = false
		later_button.text = AppState.text_for("field_assist_close")
	elif dialogue_mode == "assist":
		invite_button.visible = true
		var assistant_id: String = FIELD_ASSISTS[destination_id]["member"]
		dialogue_title.text = assist_label.text + " · " + AppState.member_name(assistant_id)
		if not AppState.recruited_members.has(assistant_id):
			dialogue_text.text = AppState.text_for("field_assist_need") % AppState.member_name(assistant_id)
		elif AppState.field_insights.has(destination_id):
			dialogue_text.text = AppState.text_for("field_assist_result_" + key)
		elif AppState.field_trace_count(destination_id) < 2:
			dialogue_text.text = AppState.text_for("field_trace_need") % AppState.member_name(assistant_id)
		else:
			dialogue_text.text = AppState.text_for("field_assist_ready_" + key)
		invite_button.text = AppState.text_for("field_assist_recorded" if AppState.field_insights.has(destination_id) else "field_assist_use")
		invite_button.disabled = not AppState.recruited_members.has(assistant_id) or AppState.field_insights.has(destination_id) or AppState.field_trace_count(destination_id) < 2
		later_button.text = AppState.text_for("field_assist_close")
	else:
		invite_button.visible = true
		dialogue_title.text = AppState.member_name(recruit_id)
		dialogue_text.text = AppState.text_for("recruit_ji_locked" if recruit_id == "ji-cheng" and not AppState.ji_records_checked else "recruit_" + recruit_id.split("-")[0])
		invite_button.text = AppState.text_for("recruit_invite")
		invite_button.disabled = recruit_id == "ji-cheng" and not AppState.ji_records_checked
		later_button.text = AppState.text_for("recruit_later")


func _open_dialogue() -> void:
	dialogue_mode = "recruit"
	dialogue_open = true
	dialogue_overlay.visible = true
	_refresh_text()
	if invite_button.disabled:
		later_button.grab_focus()
	else:
		invite_button.grab_focus()


func _open_field_assist() -> void:
	dialogue_mode = "assist"
	dialogue_open = true
	dialogue_overlay.visible = true
	_refresh_text()
	if invite_button.disabled:
		later_button.grab_focus()
	else:
		invite_button.grab_focus()


func _open_field_trace(index: int) -> void:
	trace_index = index
	dialogue_mode = "trace"
	dialogue_open = true
	dialogue_overlay.visible = true
	if AppState.discover_field_trace(destination_id, index):
		cue_player.play()
		feedback_key = "field_trace_found"
		feedback_message = ""
		AppState.write_auto_save("area", hero.position, "field_assist")
		queue_redraw()
	_refresh_text()
	later_button.grab_focus()


func _dialogue_primary() -> void:
	if dialogue_mode == "assist":
		var assistant_id: String = FIELD_ASSISTS[destination_id]["member"]
		if AppState.complete_field_assist(destination_id, assistant_id):
			cue_player.play()
			feedback_key = "field_assist_reward"
			feedback_message = ""
			AppState.write_auto_save("area", hero.position, "field_assist")
			_refresh_text()
			queue_redraw()
			later_button.grab_focus()
	else:
		_invite_companion()


func _close_dialogue() -> void:
	dialogue_open = false
	dialogue_overlay.visible = false
	back_button.grab_focus()


func _invite_companion() -> void:
	if AppState.recruit_member(recruit_id):
		feedback_message = AppState.text_for("recruit_joined") % AppState.member_name(recruit_id)
		_close_dialogue()
		_refresh_text()
		queue_redraw()
		AppState.write_auto_save("area", hero.position, "manual_note")
	else:
		feedback_message = AppState.text_for("recruit_full")
		_close_dialogue()
		_refresh_text()


func _open_encounter() -> void:
	encounter_count += 1
	var enemy_id := "patrol" if destination_id == "scifi.outskirts" else "sentry"
	AppState.write_auto_save("area", safe_position, "before_battle")
	if AppState.begin_battle(enemy_id, safe_position):
		get_tree().change_scene_to_packed(BATTLE_SCENE)


func _open_save() -> void:
	AppState.save_screen_mode = "save"
	AppState.save_return_scene = "res://scenes/scifi_exploration_area.tscn"
	AppState.save_return_position = hero.position
	get_tree().change_scene_to_file("res://scenes/save_screen.tscn")


func _return_to_map() -> void:
	get_tree().change_scene_to_file("res://scenes/scifi_world_map.tscn")


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		if dialogue_open:
			_close_dialogue()
		else:
			_return_to_map()
	elif event.is_action_pressed("interact"):
		if dialogue_open:
			return
		if hero.position.distance_to(SURVEY_ENTRANCES[destination_id]) < 43.0:
			AppState.current_annex_room = 1
			AppState.annex_surface_return_position = hero.position
			AppState.resume_area_position = hero.position
			AppState.resume_area_pending = true
			get_tree().change_scene_to_file("res://scenes/survey_annex.tscn")
		elif destination_id == "scifi.city" and hero.position.distance_to(REPORT_POSITION) < 50.0:
			if AppState.can_submit_report():
				var first_report := not AppState.demo_completed
				AppState.demo_completed = true
				if first_report:
					AppState.record_playtest_event("report", destination_id)
				AppState.resume_area_position = hero.position
				AppState.resume_area_pending = true
				AppState.write_auto_save("area", hero.position, "manual_note")
				if first_report:
					AppState.write_playtest_receipt()
				get_tree().change_scene_to_file("res://scenes/demo_report.tscn")
			else:
				feedback_key = "report_locked"
				feedback_message = ""
				_refresh_text()
		elif destination_id == "scifi.outskirts" and hero.position.distance_to(RELAY_POSITION) < 46.0:
			if not AppState.relay_checked:
				AppState.record_playtest_event("relay_checked", destination_id)
			AppState.relay_checked = true
			cue_player.play()
			feedback_key = "relay_done"
			feedback_message = ""
			_refresh_text()
			queue_redraw()
		elif destination_id == "scifi.ruins" and not AppState.ji_records_checked and hero.position.distance_to(RECORDS_POSITION) < 43.0:
			AppState.ji_records_checked = true
			AppState.record_playtest_event("ruin_record_checked", destination_id)
			cue_player.play()
			feedback_message = AppState.text_for("relic_done")
			_refresh_text()
		elif not AppState.recruited_members.has(recruit_id) and hero.position.distance_to(npc_position) < 50.0:
			_open_dialogue()
		elif hero.position.distance_to(FIELD_ASSISTS[destination_id]["position"]) < 40.0:
			_open_field_assist()
		else:
			for index in 2:
				if hero.position.distance_to(FIELD_TRACES[destination_id][index]) < 34.0:
					_open_field_trace(index)
					return
