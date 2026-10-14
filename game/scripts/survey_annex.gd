extends Node2D

const CONTENT := preload("res://scripts/survey_content.gd")
const NativeIdle := preload("res://scripts/character_directional_idle.gd")
const NativeMotion := preload("res://scripts/character_directional_motion.gd")
const ROOM_ONE_BACKGROUND := {
	"scifi.city": preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-survey-annex-room-01_environment-background_m8-concept_20261014-142350-f2ab83d1.png"),
	"scifi.outskirts": preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-outskirts-survey-annex-room-01_environment-background_m8-concept_20261014-142650-1b4ca8d2.png"),
	"scifi.ruins": preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-ruins-survey-annex-room-01_environment-background_m8-concept_20261014-142840-0ce7a91b.png"),
}
const ROOM_TWO_BACKGROUND := {
	"scifi.city": preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-survey-annex-room-02_environment-background_m8-concept_20261014-142926-e2e661fc.png"),
	"scifi.outskirts": preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-outskirts-survey-annex-room-02_environment-background_m8-concept_20261014-143030-3784c1e2.png"),
	"scifi.ruins": preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-ruins-survey-annex-room-02_environment-background_m8-concept_20261014-143300-042ae336.png"),
}
const DISCOVERY_CUE := preload("res://assets/audio/rpg-2-star-ocean-the-second_discovery_interaction-cue_m7_20261013-211230-ad781e52.wav")
const CLUE_POSITIONS := [Vector2(163, 165), Vector2(320, 165), Vector2(477, 165)]
const EXIT_POSITION := Vector2(57, 257)
const NEXT_POSITION := Vector2(580, 257)
const TERMINAL_POSITION := Vector2(320, 263)
const MOVE_SPEED := 140.0
const PALETTES := {
	"scifi.city": [Color("#284652"), Color("#94bbb1")],
	"scifi.outskirts": [Color("#455d56"), Color("#a7c5a3")],
	"scifi.ruins": [Color("#5d574a"), Color("#d0b98a")],
}
const AMBIENCE := {
	"scifi.city": "res://assets/audio/rpg-2-star-ocean-the-second_scifi-city_ambient-loop_m7_20261013-211230-c8e1159a.wav",
	"scifi.outskirts": "res://assets/audio/rpg-2-star-ocean-the-second_scifi-outskirts_ambient-loop_m7_20261013-211230-57ad4b20.wav",
	"scifi.ruins": "res://assets/audio/rpg-2-star-ocean-the-second_scifi-ruins_ambient-loop_m7_20261013-211230-6be0d93f.wav",
}

var destination_id := "scifi.city"
var room := 1
var hero: Sprite2D
var hero_facing := "south"
var walk_time := 0.0
var walk_phase := 0
var title_label: Label
var progress_label: Label
var help_label: Label
var back_button: Button
var save_button: Button
var clue_labels: Array[Label] = []
var exit_label: Label
var next_label: Label
var terminal_label: Label
var overlay: ColorRect
var overlay_title: Label
var overlay_body: RichTextLabel
var option_buttons: Array[Button] = []
var link_buttons: Array[Button] = []
var notes_button: Button
var previous_note_button: Button
var next_note_button: Button
var close_button: Button
var overlay_mode := ""
var notes_return_mode := ""
var notes_index := 0
var overlay_clue_index := -1
var link_selected_index := -1
var overlay_message := ""
var cue_player: AudioStreamPlayer


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	destination_id = AppState.current_destination_id
	if not CONTENT.DATA.has(destination_id):
		destination_id = "scifi.city"
	room = clampi(AppState.current_annex_room, 1, 2)
	_build_hero()
	if AppState.resume_annex_pending:
		hero.position = AppState.resume_annex_position
		AppState.resume_annex_pending = false
	_build_ui()
	_start_audio()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()


func _data() -> Dictionary:
	return CONTENT.DATA[destination_id][AppState.language]


func _clue_key(index: int) -> String:
	return "%s:%d" % [destination_id, index]


func _clue_count() -> int:
	var count := 0
	for index in 6:
		if AppState.survey_clues.has(_clue_key(index)):
			count += 1
	return count


func _link_key(index: int) -> String:
	return "%s:%d" % [destination_id, index]


func _link_count() -> int:
	var count := 0
	for index in 3:
		if AppState.survey_links.has(_link_key(index)):
			count += 1
	return count


func _linked_clue(index: int) -> bool:
	var links: Array = _data()["links"]
	for link_index in 3:
		if AppState.survey_links.has(_link_key(link_index)) and links[link_index]["pair"].has(index):
			return true
	return false


func _process(delta: float) -> void:
	if overlay.visible:
		_reset_walk_animation()
		return
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if direction != Vector2.ZERO:
		_set_hero_facing(direction)
		var previous_position := hero.position
		hero.position += direction * MOVE_SPEED * delta
		hero.position.x = clampf(hero.position.x, 25.0, 615.0)
		hero.position.y = clampf(hero.position.y, 78.0, 305.0)
		if hero.position.distance_to(previous_position) > 0.05:
			_update_walk_animation(delta)
		else:
			_reset_walk_animation()
	else:
		_reset_walk_animation()


func _set_hero_facing(direction: Vector2) -> void:
	var facing := "east" if direction.x > 0.0 else "west"
	if absf(direction.y) >= absf(direction.x):
		facing = "south" if direction.y > 0.0 else "north"
	if facing == hero_facing:
		return
	hero_facing = facing
	walk_time = 0.0
	walk_phase = 0
	hero.texture = NativeIdle.texture_for("protagonist-" + AppState.hero_appearance, hero_facing)


func _update_walk_animation(delta: float) -> void:
	walk_time += delta
	var phase := int(floor(walk_time / 0.12)) % 4 + 1
	if phase == walk_phase:
		return
	walk_phase = phase
	hero.texture = NativeMotion.texture_for("protagonist-" + AppState.hero_appearance, "walk", hero_facing, walk_phase)


func _reset_walk_animation() -> void:
	if walk_phase == 0:
		return
	walk_time = 0.0
	walk_phase = 0
	hero.texture = NativeIdle.texture_for("protagonist-" + AppState.hero_appearance, hero_facing)


func _draw() -> void:
	var palette: Array = PALETTES[destination_id]
	var floor_color: Color = palette[0].darkened(0.10) if room == 2 else palette[0]
	draw_rect(Rect2(0, 0, 640, 360), Color("#11232c"))
	draw_rect(Rect2(16, 67, 608, 250), floor_color)
	for x in range(25, 625, 38):
		draw_line(Vector2(x, 68), Vector2(x, 317), floor_color.lightened(0.07), 1.0)
	for y in range(75, 317, 38):
		draw_line(Vector2(16, y), Vector2(624, y), floor_color.lightened(0.07), 1.0)
	match destination_id:
		"scifi.city":
			for x in [90, 235, 405, 548]:
				draw_rect(Rect2(x, 91, 43, 50), Color("#1b3541"))
				draw_rect(Rect2(x + 7, 98, 29, 9), Color("#749c9f"))
			if room == 2:
				draw_line(Vector2(42, 293), Vector2(590, 293), Color("#91aaa1"), 5.0)
				for x in [120, 270, 430, 550]:
					draw_circle(Vector2(x, 293), 7.0, Color("#c4a67a"))
		"scifi.outskirts":
			for x in [90, 235, 405, 548]:
				draw_rect(Rect2(x, 86, 7, 51), Color("#263f42"))
				draw_line(Vector2(x + 3, 91), Vector2(x + 30, 82), Color("#b0c7af"), 2.0)
			if room == 2:
				for x in [110, 260, 420, 555]:
					draw_rect(Rect2(x, 285, 37, 18), Color("#273f43"))
					draw_rect(Rect2(x + 5, 290, 27, 5), Color("#92b5a8"))
		"scifi.ruins":
			for x in [78, 233, 398, 553]:
				draw_rect(Rect2(x, 83, 30, 58), Color("#aa9670"))
				draw_rect(Rect2(x - 7, 78, 44, 8), Color("#d3b985"))
			if room == 2:
				draw_circle(Vector2(320, 266), 59.0, Color("#87775a"))
				draw_circle(Vector2(320, 266), 46.0, floor_color)
	if room == 1 and ROOM_ONE_BACKGROUND.has(destination_id):
		draw_texture_rect(ROOM_ONE_BACKGROUND[destination_id], Rect2(0, 0, 640, 360), false)
	elif room == 2 and ROOM_TWO_BACKGROUND.has(destination_id):
		draw_texture_rect(ROOM_TWO_BACKGROUND[destination_id], Rect2(0, 0, 640, 360), false)
	for index in CLUE_POSITIONS.size():
		var position: Vector2 = CLUE_POSITIONS[index]
		var already := AppState.survey_clues.has(_clue_key((room - 1) * 3 + index))
		var clue_color: Color = palette[1] if already else Color("#e2bb77")
		draw_circle(position, 16.0, Color(0.04, 0.12, 0.16, 0.82))
		draw_arc(position, 14.0, 0.0, TAU, 28, clue_color, 2.0)
		draw_rect(Rect2(position + Vector2(-6, -6), Vector2(12, 12)), clue_color, false, 1.7)
		draw_line(position + Vector2(-3, -2), position + Vector2(3, -2), clue_color, 1.5)
		draw_line(position + Vector2(-3, 2), position + Vector2(2, 2), clue_color, 1.5)
	_draw_annex_marker(EXIT_POSITION, Color("#8bcfca"), false)
	if room == 1:
		_draw_annex_marker(NEXT_POSITION, Color("#e4c377"), false)
	else:
		_draw_annex_marker(TERMINAL_POSITION, palette[1] if AppState.survey_solved.has(destination_id) else Color("#e4c377"), true)


func _draw_annex_marker(at: Vector2, color: Color, terminal: bool) -> void:
	draw_circle(at, 16.0, Color(0.04, 0.12, 0.16, 0.82))
	draw_arc(at, 14.0, 0.0, TAU, 28, color, 2.0)
	if terminal:
		draw_rect(Rect2(at + Vector2(-6, -5), Vector2(12, 9)), color, false, 1.5)
		draw_line(at + Vector2(-3, 7), at + Vector2(3, 7), color, 1.5)
	else:
		draw_line(at + Vector2(-4, -5), at + Vector2(3, 0), color, 2.0)
		draw_line(at + Vector2(3, 0), at + Vector2(-4, 5), color, 2.0)


func _build_hero() -> void:
	hero = Sprite2D.new()
	hero.texture = NativeIdle.texture_for("protagonist-" + AppState.hero_appearance, "south")
	hero.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	hero.offset = Vector2(0, -20)
	hero.position = Vector2(87, 261)
	add_child(hero)


func _start_audio() -> void:
	var ambience := AudioStreamPlayer.new()
	var stream: AudioStreamWAV = load(AMBIENCE[destination_id]).duplicate()
	stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
	ambience.stream = stream
	ambience.volume_db = -12.0
	add_child(ambience)
	ambience.play()
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
	title_label = _label(canvas, Vector2(18, 6), 18, Color("#edf7f3"))
	progress_label = _label(canvas, Vector2(18, 34), 11, Color("#acc9c5"))
	save_button = _button(canvas, Vector2(418, 12), Vector2(98, 38), _open_save)
	back_button = _button(canvas, Vector2(525, 12), Vector2(98, 38), _back_room)
	for index in CLUE_POSITIONS.size():
		var label := _label(canvas, CLUE_POSITIONS[index] + Vector2(-48, -45), 11, Color("#f4e4b7"))
		label.size = Vector2(96, 36)
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		label.add_theme_color_override("font_outline_color", Color("#0d1920"))
		label.add_theme_constant_override("outline_size", 2)
		clue_labels.append(label)
	exit_label = _label(canvas, EXIT_POSITION + Vector2(-38, -52), 10, Color("#e0e5cf"))
	next_label = _label(canvas, NEXT_POSITION + Vector2(-33, -52), 10, Color("#e0e5cf"))
	terminal_label = _label(canvas, TERMINAL_POSITION + Vector2(-46, -48), 11, Color("#f1e0ac"))
	for label in [exit_label, next_label, terminal_label]:
		label.add_theme_color_override("font_outline_color", Color("#0d1920"))
		label.add_theme_constant_override("outline_size", 2)
	var footer := ColorRect.new()
	footer.color = Color("#0d1723")
	footer.position = Vector2(0, 318)
	footer.size = Vector2(640, 42)
	canvas.add_child(footer)
	help_label = _label(canvas, Vector2(18, 327), 11, Color("#c0d5d1"))
	_build_overlay(canvas)


func _build_overlay(canvas: CanvasLayer) -> void:
	overlay = ColorRect.new()
	overlay.color = Color(0.04, 0.08, 0.12, 0.93)
	overlay.size = Vector2(640, 360)
	overlay.visible = false
	canvas.add_child(overlay)
	var panel := ColorRect.new()
	panel.position = Vector2(53, 41)
	panel.size = Vector2(534, 278)
	panel.color = Color("#29434d")
	overlay.add_child(panel)
	overlay_title = _label(overlay, Vector2(75, 58), 19, Color("#f0e2bd"))
	overlay_body = RichTextLabel.new()
	overlay_body.position = Vector2(75, 95)
	overlay_body.size = Vector2(488, 92)
	overlay_body.scroll_active = true
	overlay_body.add_theme_font_size_override("normal_font_size", 13)
	overlay.add_child(overlay_body)
	for index in 3:
		var button := _button(overlay, Vector2(75, 190 + index * 34), Vector2(488, 30), _choose_answer.bind(index))
		button.add_theme_font_size_override("font_size", 11)
		option_buttons.append(button)
	for index in 6:
		var button := _button(overlay, Vector2(75 + (index % 2) * 249, 155 + (index / 2) * 37), Vector2(239, 32), _select_link_clue.bind(index))
		button.add_theme_font_size_override("font_size", 11)
		link_buttons.append(button)
	notes_button = _button(overlay, Vector2(409, 56), Vector2(154, 29), _open_notes)
	previous_note_button = _button(overlay, Vector2(75, 275), Vector2(145, 32), _shift_note.bind(-1))
	next_note_button = _button(overlay, Vector2(232, 275), Vector2(145, 32), _shift_note.bind(1))
	close_button = _button(overlay, Vector2(409, 275), Vector2(154, 32), _on_close_button)


func _label(parent: Node, position: Vector2, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.position = position
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	parent.add_child(label)
	return label


func _button(parent: Node, position: Vector2, size: Vector2, callback: Callable) -> Button:
	var button := Button.new()
	button.position = position
	button.size = size
	button.pressed.connect(callback)
	parent.add_child(button)
	return button


func _refresh_text() -> void:
	var data := _data()
	title_label.text = AppState.destination_name(destination_id) + " · " + String(data["rooms"][room - 1])
	progress_label.text = AppState.text_for("survey_progress") % [_clue_count(), AppState.text_for("field_yes" if AppState.survey_solved.has(destination_id) else "field_no")]
	help_label.text = AppState.text_for("survey_help")
	back_button.text = AppState.text_for("survey_leave" if room == 1 else "survey_previous")
	save_button.text = AppState.text_for("save_open")
	for index in CLUE_POSITIONS.size():
		clue_labels[index].text = String(data["clues"][(room - 1) * 3 + index]["name"])
	exit_label.text = AppState.text_for("survey_leave" if room == 1 else "survey_previous")
	next_label.text = AppState.text_for("survey_next")
	next_label.visible = room == 1
	terminal_label.text = AppState.text_for("survey_terminal")
	terminal_label.visible = room == 2
	if overlay.visible:
		_refresh_overlay()
	queue_redraw()


func _refresh_overlay() -> void:
	var data := _data()
	for button in option_buttons:
		button.visible = overlay_mode == "question"
	for button in link_buttons:
		button.visible = overlay_mode == "link"
	notes_button.visible = overlay_mode in ["link", "question", "message"] and _clue_count() > 0
	notes_button.text = AppState.text_for("survey_notes")
	previous_note_button.visible = overlay_mode == "notes"
	next_note_button.visible = overlay_mode == "notes"
	previous_note_button.text = AppState.text_for("survey_notes_previous")
	next_note_button.text = AppState.text_for("survey_notes_next")
	close_button.visible = overlay_mode != "question"
	close_button.text = AppState.text_for("survey_notes_back" if overlay_mode == "notes" else ("survey_link_continue" if overlay_mode == "link" and _link_count() == 3 else "survey_close"))
	overlay_body.size.y = 151 if overlay_mode == "notes" else (50 if overlay_mode == "link" else 92)
	match overlay_mode:
		"clue":
			var clue: Dictionary = data["clues"][overlay_clue_index]
			overlay_title.text = String(clue["name"])
			overlay_body.text = String(clue["text"])
		"question":
			overlay_title.text = AppState.text_for("survey_terminal")
			overlay_body.text = String(data["question"]) + ("\n" + overlay_message if overlay_message != "" else "")
			for index in 3:
				option_buttons[index].text = String(data["options"][index])
		"link":
			overlay_title.text = AppState.text_for("survey_link_title")
			overlay_body.text = overlay_message if overlay_message != "" else AppState.text_for("survey_link_instruction") % _link_count()
			for index in 6:
				var prefix := "▶ " if link_selected_index == index else ("✓ " if _linked_clue(index) else "")
				link_buttons[index].text = prefix + String(data["clues"][index]["name"])
		"message":
			overlay_title.text = AppState.text_for("survey_terminal")
			overlay_body.text = overlay_message
		"notes":
			var clue: Dictionary = data["clues"][notes_index]
			overlay_title.text = AppState.text_for("survey_notes") + " %d/6" % (notes_index + 1)
			overlay_body.text = String(clue["name"]) + "\n\n" + String(clue["text"])
			previous_note_button.disabled = _clue_count() < 2
			next_note_button.disabled = _clue_count() < 2


func _inspect_clue(index: int) -> void:
	if index < 0 or index >= 6:
		return
	if not AppState.survey_clues.has(_clue_key(index)):
		AppState.survey_clues[_clue_key(index)] = true
		AppState.write_auto_save("annex", hero.position, "survey_note")
		cue_player.play()
	overlay_clue_index = index
	overlay_mode = "clue"
	overlay.visible = true
	_refresh_text()
	close_button.grab_focus()


func _open_question() -> void:
	overlay.visible = true
	if AppState.survey_solved.has(destination_id):
		overlay_mode = "message"
		overlay_message = AppState.text_for("survey_completed")
	elif _clue_count() < 6:
		overlay_mode = "message"
		overlay_message = AppState.text_for("survey_locked")
	elif _link_count() < 3:
		overlay_mode = "link"
		overlay_message = ""
		link_selected_index = -1
	else:
		overlay_mode = "question"
		overlay_message = ""
	_refresh_text()
	(option_buttons[0] if overlay_mode == "question" else (link_buttons[0] if overlay_mode == "link" else close_button)).grab_focus()


func _select_link_clue(index: int) -> void:
	if overlay_mode != "link" or index < 0 or index >= 6:
		return
	if link_selected_index < 0:
		link_selected_index = index
		overlay_message = AppState.text_for("survey_link_instruction") % _link_count()
		_refresh_overlay()
		return
	if link_selected_index == index:
		link_selected_index = -1
		overlay_message = ""
		_refresh_overlay()
		return
	var first := link_selected_index
	link_selected_index = -1
	var data := _data()
	for link_index in 3:
		var link: Dictionary = data["links"][link_index]
		var pair: Array = link["pair"]
		if pair.has(first) and pair.has(index):
			if AppState.survey_links.has(_link_key(link_index)):
				overlay_message = AppState.text_for("survey_link_found")
			else:
				AppState.survey_links[_link_key(link_index)] = true
				AppState.write_auto_save("annex", hero.position, "survey_note")
				cue_player.play()
				overlay_message = String(link["insight"]) + "\n" + AppState.text_for("survey_link_instruction") % _link_count()
			_refresh_overlay()
			return
	overlay_message = AppState.text_for("survey_link_wrong")
	AppState.record_playtest_mistake("pair", destination_id)
	_refresh_overlay()


func _on_close_button() -> void:
	if overlay_mode == "notes":
		overlay_mode = notes_return_mode
		_refresh_overlay()
		(notes_button if notes_button.visible else close_button).grab_focus()
	elif overlay_mode == "link" and _link_count() == 3:
		_open_question()
	else:
		_close_overlay()


func _open_notes() -> void:
	if not overlay.visible or overlay_mode == "notes" or _clue_count() == 0:
		return
	AppState.record_playtest_event("notes_open", destination_id)
	notes_return_mode = overlay_mode
	for index in 6:
		if AppState.survey_clues.has(_clue_key(index)):
			notes_index = index
			break
	overlay_mode = "notes"
	_refresh_overlay()
	next_note_button.grab_focus()


func _shift_note(direction: int) -> void:
	if overlay_mode != "notes":
		return
	var available: Array[int] = []
	for index in 6:
		if AppState.survey_clues.has(_clue_key(index)):
			available.append(index)
	if available.size() < 2:
		return
	var current := available.find(notes_index)
	notes_index = available[posmod(current + direction, available.size())]
	_refresh_overlay()


func _choose_answer(index: int) -> void:
	if overlay_mode != "question":
		return
	var data := _data()
	if index != int(data["answer"]):
		overlay_message = AppState.text_for("survey_retry")
		AppState.record_playtest_mistake("judgment", destination_id)
		_refresh_overlay()
		return
	if not AppState.survey_solved.has(destination_id):
		AppState.survey_solved[destination_id] = true
		AppState.record_playtest_event("survey_complete", destination_id)
		AppState.award_survey_jp()
		AppState.write_auto_save("annex", hero.position, "survey_note")
		cue_player.play()
	overlay_mode = "message"
	overlay_message = String(data["success"]) + "\n" + AppState.text_for("survey_reward")
	_refresh_text()
	close_button.grab_focus()


func _close_overlay() -> void:
	overlay.visible = false
	overlay_mode = ""
	back_button.grab_focus()


func _go_next_room() -> void:
	if room != 1:
		return
	AppState.current_annex_room = 2
	AppState.resume_annex_pending = false
	get_tree().change_scene_to_file("res://scenes/survey_annex.tscn")


func _back_room() -> void:
	if overlay.visible:
		if overlay_mode == "notes":
			_on_close_button()
		else:
			_close_overlay()
		return
	if room == 2:
		AppState.current_annex_room = 1
		AppState.resume_annex_position = Vector2(555, 257)
		AppState.resume_annex_pending = true
		get_tree().change_scene_to_file("res://scenes/survey_annex.tscn")
	else:
		AppState.resume_area_position = AppState.annex_surface_return_position
		AppState.resume_area_pending = true
		get_tree().change_scene_to_file("res://scenes/scifi_exploration_area.tscn")


func _open_save() -> void:
	AppState.save_screen_mode = "save"
	AppState.save_return_scene = "res://scenes/survey_annex.tscn"
	AppState.save_return_position = hero.position
	get_tree().change_scene_to_file("res://scenes/save_screen.tscn")


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_back_room()
	elif event.is_action_pressed("interact"):
		if overlay.visible:
			return
		for index in CLUE_POSITIONS.size():
			if hero.position.distance_to(CLUE_POSITIONS[index]) < 45.0:
				_inspect_clue((room - 1) * 3 + index)
				return
		if room == 2 and hero.position.distance_to(TERMINAL_POSITION) < 46.0:
			_open_question()
		elif hero.position.distance_to(EXIT_POSITION) < 46.0:
			_back_room()
		elif room == 1 and hero.position.distance_to(NEXT_POSITION) < 46.0:
			_go_next_room()
