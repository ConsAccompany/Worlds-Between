extends Node2D

const HERO_SPRITE := preload("res://assets/characters/rpg-2-star-ocean-the-second_hero-temp_exploration-sprite_m1_20261013-185701-b7e41a93.svg")
const MOVE_SPEED := 140.0
const SPAWN := Vector2(82, 260)
const AREA_CONFIG := {
	"scifi.city": {"npc": Vector2(282, 180), "enemy": Vector2(-100, -100), "color": Color("#365463")},
	"scifi.outskirts": {"npc": Vector2(190, 150), "enemy": Vector2(355, 238), "color": Color("#546b57")},
	"scifi.ruins": {"npc": Vector2(200, 145), "enemy": Vector2(420, 225), "color": Color("#70644f")},
}

var destination_id := ""
var hero: Sprite2D
var npc_position := Vector2.ZERO
var enemy_position := Vector2(-100, -100)
var enemy_visible := false
var encounter_open := false
var encounter_count := 0
var bypass_reached := false
var safe_position := SPAWN
var title_label: Label
var hint_label: Label
var help_label: Label
var feedback_label: Label
var enemy_label: Label
var back_button: Button
var encounter_overlay: ColorRect
var encounter_title: Label
var encounter_note: Label
var continue_button: Button
var feedback_key := "npc_prompt"


func _ready() -> void:
	destination_id = AppState.current_destination_id
	if not AREA_CONFIG.has(destination_id):
		destination_id = "scifi.city"
	var config: Dictionary = AREA_CONFIG[destination_id]
	npc_position = config["npc"]
	enemy_position = config["enemy"]
	enemy_visible = destination_id != "scifi.city"
	_build_actors()
	_build_ui()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()


func _process(delta: float) -> void:
	if encounter_open:
		return
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if direction != Vector2.ZERO:
		hero.position += direction * MOVE_SPEED * delta
		hero.position.x = clampf(hero.position.x, 24.0, 616.0)
		hero.position.y = clampf(hero.position.y, 77.0, 306.0)
		if enemy_visible:
			if hero.position.distance_to(enemy_position) > 43.0:
				safe_position = hero.position
			if hero.position.distance_to(enemy_position) < 23.0:
				_open_encounter()
	if enemy_visible and not bypass_reached and not encounter_open and hero.position.x > 545.0 and hero.position.y < 205.0:
		bypass_reached = true
		feedback_key = "bypass_notice"
		_refresh_text()


func _draw() -> void:
	if not AREA_CONFIG.has(destination_id):
		return
	var color: Color = AREA_CONFIG[destination_id]["color"]
	draw_rect(Rect2(0, 0, 640, 360), Color("#13232d"))
	draw_rect(Rect2(16, 67, 608, 250), color)
	for x in range(16, 624, 32):
		draw_line(Vector2(x, 67), Vector2(x, 317), color.lightened(0.08), 1.0)
	for y in range(67, 318, 32):
		draw_line(Vector2(16, y), Vector2(624, y), color.lightened(0.08), 1.0)
	match destination_id:
		"scifi.city":
			_draw_city()
		"scifi.outskirts":
			_draw_outskirts()
		"scifi.ruins":
			_draw_ruins()
	_draw_npc()
	if enemy_visible:
		_draw_enemy()
		draw_rect(Rect2(566, 88, 13, 34), Color("#a2ded1"))
		draw_rect(Rect2(579, 88, 4, 34), Color("#233c47"))


func _draw_city() -> void:
	draw_rect(Rect2(65, 96, 152, 72), Color("#203b4a"))
	draw_rect(Rect2(88, 110, 106, 42), Color("#719e9c"))
	draw_rect(Rect2(405, 94, 160, 95), Color("#294958"))
	draw_rect(Rect2(430, 110, 110, 62), Color("#749ea4"))
	draw_rect(Rect2(30, 222, 580, 30), Color("#667e7a"))
	draw_rect(Rect2(150, 255, 340, 22), Color("#7f9990"))
	for x in range(80, 560, 70):
		draw_rect(Rect2(x, 236, 30, 3), Color("#d9c691"))


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
	draw_circle(npc_position + Vector2(0, 10), 15.0, Color("#1a333c"))
	draw_rect(Rect2(npc_position + Vector2(-8, -15), Vector2(16, 28)), Color("#8ed2c3"))
	draw_circle(npc_position + Vector2(0, -17), 9.0, Color("#e1c49a"))


func _draw_enemy() -> void:
	draw_circle(enemy_position, 24.0, Color(0.62, 0.20, 0.22, 0.32))
	draw_rect(Rect2(enemy_position + Vector2(-13, -14), Vector2(26, 27)), Color("#8a3a42"))
	draw_rect(Rect2(enemy_position + Vector2(-8, -8), Vector2(16, 8)), Color("#eaa88b"))
	draw_rect(Rect2(enemy_position + Vector2(-17, 11), Vector2(8, 7)), Color("#463942"))
	draw_rect(Rect2(enemy_position + Vector2(9, 11), Vector2(8, 7)), Color("#463942"))


func _build_actors() -> void:
	hero = Sprite2D.new()
	hero.texture = HERO_SPRITE
	hero.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	hero.scale = Vector2(2, 2)
	hero.position = SPAWN
	add_child(hero)


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
	_build_encounter_overlay(canvas)


func _build_encounter_overlay(canvas: CanvasLayer) -> void:
	encounter_overlay = ColorRect.new()
	encounter_overlay.color = Color(0.05, 0.09, 0.14, 0.82)
	encounter_overlay.size = Vector2(640, 360)
	encounter_overlay.visible = false
	canvas.add_child(encounter_overlay)
	var panel := ColorRect.new()
	panel.color = Color("#253543")
	panel.position = Vector2(113, 105)
	panel.size = Vector2(414, 155)
	encounter_overlay.add_child(panel)
	encounter_title = Label.new()
	encounter_title.position = Vector2(139, 125)
	encounter_title.add_theme_font_size_override("font_size", 20)
	encounter_title.add_theme_color_override("font_color", Color("#ffe0c2"))
	encounter_overlay.add_child(encounter_title)
	encounter_note = Label.new()
	encounter_note.position = Vector2(139, 163)
	encounter_note.size = Vector2(365, 50)
	encounter_note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	encounter_overlay.add_child(encounter_note)
	continue_button = Button.new()
	continue_button.position = Vector2(350, 216)
	continue_button.size = Vector2(152, 32)
	continue_button.pressed.connect(_close_encounter)
	encounter_overlay.add_child(continue_button)


func _refresh_text() -> void:
	var key := destination_id.trim_prefix("scifi.")
	title_label.text = AppState.destination_name(destination_id)
	hint_label.text = AppState.text_for("area_" + key + "_hint")
	help_label.text = AppState.text_for("area_help")
	feedback_label.text = AppState.text_for(feedback_key)
	back_button.text = AppState.text_for("area_back")
	enemy_label.text = AppState.text_for("enemy_label")
	encounter_title.text = AppState.text_for("encounter_title")
	encounter_note.text = AppState.text_for("encounter_note")
	continue_button.text = AppState.text_for("encounter_continue")


func _open_encounter() -> void:
	encounter_count += 1
	encounter_open = true
	hero.position = safe_position
	encounter_overlay.visible = true
	continue_button.grab_focus()


func _close_encounter() -> void:
	encounter_open = false
	encounter_overlay.visible = false
	back_button.grab_focus()


func _return_to_map() -> void:
	get_tree().change_scene_to_file("res://scenes/scifi_world_map.tscn")


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_return_to_map()
	elif event.is_action_pressed("interact") and not encounter_open:
		if hero.position.distance_to(npc_position) < 50.0:
			feedback_key = "npc_" + destination_id.trim_prefix("scifi.")
			_refresh_text()
