extends Control

var title_label: Label
var subtitle_label: Label
var start_button: Button
var language_button: Button
var quit_button: Button


func _ready() -> void:
	_build_ui()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()
	start_button.grab_focus()


func _build_ui() -> void:
	var background := ColorRect.new()
	background.color = Color("#0d1723")
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(background)

	var accent := ColorRect.new()
	accent.color = Color("#54c4be")
	accent.position = Vector2(0, 0)
	accent.size = Vector2(10, 360)
	add_child(accent)

	var column := VBoxContainer.new()
	column.set_anchors_and_offsets_preset(Control.PRESET_TOP_LEFT)
	column.position = Vector2(160, 64)
	column.size = Vector2(320, 240)
	column.add_theme_constant_override("separation", 10)
	add_child(column)

	title_label = Label.new()
	title_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_label.add_theme_font_size_override("font_size", 28)
	title_label.add_theme_color_override("font_color", Color("#eff9f6"))
	column.add_child(title_label)

	subtitle_label = Label.new()
	subtitle_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle_label.add_theme_color_override("font_color", Color("#9dbbc0"))
	column.add_child(subtitle_label)

	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(0, 16)
	column.add_child(spacer)

	start_button = Button.new()
	start_button.custom_minimum_size = Vector2(0, 36)
	start_button.pressed.connect(_start_game)
	column.add_child(start_button)

	language_button = Button.new()
	language_button.custom_minimum_size = Vector2(0, 36)
	language_button.pressed.connect(AppState.toggle_language)
	column.add_child(language_button)

	quit_button = Button.new()
	quit_button.custom_minimum_size = Vector2(0, 36)
	quit_button.pressed.connect(func(): get_tree().quit())
	column.add_child(quit_button)


func _refresh_text() -> void:
	title_label.text = AppState.text_for("title")
	subtitle_label.text = AppState.text_for("subtitle")
	start_button.text = AppState.text_for("start")
	language_button.text = AppState.text_for("language")
	quit_button.text = AppState.text_for("quit")


func _start_game() -> void:
	AppState.begin_new_run()
	get_tree().change_scene_to_file("res://scenes/scifi_world_map.tscn")

