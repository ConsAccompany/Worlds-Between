extends Node2D

const AREA_SCENE := "res://scenes/scifi_exploration_area.tscn"
const MARKERS := {
	"scifi.city": Vector2(136, 174),
	"scifi.outskirts": Vector2(324, 230),
	"scifi.ruins": Vector2(510, 150),
}

var title_label: Label
var help_label: Label
var back_button: Button
var growth_button: Button
var save_button: Button
var destination_buttons: Dictionary = {}


func _ready() -> void:
	_build_ui()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()


func _draw() -> void:
	draw_rect(Rect2(0, 0, 640, 360), Color("#132733"))
	draw_rect(Rect2(17, 71, 606, 258), Color("#24444b"))
	for x in range(17, 624, 24):
		draw_line(Vector2(x, 71), Vector2(x, 329), Color("#2b4e54"), 1.0)
	for y in range(71, 330, 24):
		draw_line(Vector2(17, y), Vector2(623, y), Color("#2b4e54"), 1.0)
	draw_line(MARKERS["scifi.city"], MARKERS["scifi.outskirts"], Color("#d0b982"), 7.0)
	draw_line(MARKERS["scifi.outskirts"], MARKERS["scifi.ruins"], Color("#d0b982"), 7.0)
	draw_line(MARKERS["scifi.city"], MARKERS["scifi.outskirts"], Color("#6e8b8b"), 2.0)
	draw_line(MARKERS["scifi.outskirts"], MARKERS["scifi.ruins"], Color("#6e8b8b"), 2.0)
	for id in AppState.DESTINATIONS:
		var position: Vector2 = MARKERS[id]
		draw_circle(position, 27.0, Color("#112b34"))
		draw_circle(position, 21.0, Color("#79cfc0"))
		draw_circle(position, 15.0, Color("#263e49"))


func _build_ui() -> void:
	var canvas := CanvasLayer.new()
	add_child(canvas)
	var header := ColorRect.new()
	header.color = Color("#0d1723")
	header.size = Vector2(640, 62)
	canvas.add_child(header)

	title_label = Label.new()
	title_label.position = Vector2(18, 7)
	title_label.add_theme_font_size_override("font_size", 19)
	title_label.add_theme_color_override("font_color", Color("#eef8f5"))
	canvas.add_child(title_label)
	help_label = Label.new()
	help_label.position = Vector2(18, 35)
	help_label.add_theme_font_size_override("font_size", 11)
	help_label.add_theme_color_override("font_color", Color("#a4c1c3"))
	canvas.add_child(help_label)
	back_button = Button.new()
	back_button.position = Vector2(528, 12)
	back_button.size = Vector2(94, 37)
	back_button.pressed.connect(_return_to_menu)
	canvas.add_child(back_button)
	save_button = Button.new()
	save_button.position = Vector2(295, 12)
	save_button.size = Vector2(102, 37)
	save_button.pressed.connect(_open_save)
	canvas.add_child(save_button)
	growth_button = Button.new()
	growth_button.position = Vector2(404, 12)
	growth_button.size = Vector2(117, 37)
	growth_button.pressed.connect(_open_growth)
	canvas.add_child(growth_button)

	var ids := ["scifi.city", "scifi.outskirts", "scifi.ruins"]
	for id in ids:
		var button := Button.new()
		button.name = id.replace(".", "_") + "_button"
		button.position = MARKERS[id] + Vector2(-68, 29)
		button.size = Vector2(136, 39)
		button.pressed.connect(_enter_destination.bind(id))
		canvas.add_child(button)
		destination_buttons[id] = button


func _refresh_text() -> void:
	title_label.text = AppState.text_for("map_title")
	help_label.text = AppState.text_for("map_help")
	back_button.text = AppState.text_for("map_back")
	growth_button.text = AppState.text_for("growth_open")
	save_button.text = AppState.text_for("save_open")
	for id in destination_buttons:
		destination_buttons[id].text = AppState.destination_name(id)


func _enter_destination(destination_id: String) -> void:
	if not AppState.select_destination(destination_id):
		return
	get_tree().change_scene_to_file(AREA_SCENE)


func _return_to_menu() -> void:
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func _open_growth() -> void:
	AppState.growth_return_scene = "res://scenes/scifi_world_map.tscn"
	get_tree().change_scene_to_file("res://scenes/growth_screen.tscn")


func _open_save() -> void:
	AppState.save_screen_mode = "save"
	AppState.save_return_scene = "res://scenes/scifi_world_map.tscn"
	AppState.save_return_position = Vector2.ZERO
	get_tree().change_scene_to_file("res://scenes/save_screen.tscn")


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_return_to_menu()
