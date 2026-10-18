extends Control

var title_label: Label
var subtitle_label: Label
var start_button: Button
var load_button: Button
var language_button: Button
var settings_button: Button
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
	column.size = Vector2(320, 275)
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
	load_button = Button.new()
	load_button.custom_minimum_size = Vector2(0, 36)
	load_button.pressed.connect(_open_load)
	column.add_child(load_button)

	language_button = Button.new()
	language_button.custom_minimum_size = Vector2(0, 36)
	language_button.pressed.connect(AppState.toggle_language)
	column.add_child(language_button)

	# Settings shares the last row with Quit so the column keeps its height inside 360 px.
	var last_row := HBoxContainer.new()
	last_row.add_theme_constant_override("separation", 10)
	column.add_child(last_row)
	settings_button = Button.new()
	settings_button.custom_minimum_size = Vector2(0, 36)
	settings_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	settings_button.pressed.connect(func(): AppState.settings.open())
	last_row.add_child(settings_button)

	quit_button = Button.new()
	quit_button.custom_minimum_size = Vector2(0, 36)
	quit_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	quit_button.pressed.connect(func(): get_tree().quit())
	last_row.add_child(quit_button)


func _refresh_text() -> void:
	title_label.text = AppState.text_for("title")
	subtitle_label.text = AppState.text_for("subtitle")
	start_button.text = AppState.text_for("start")
	load_button.text = AppState.text_for("save_load_open")
	language_button.text = AppState.text_for("language")
	settings_button.text = AppState.text_for("settings_open")
	quit_button.text = AppState.text_for("quit")


func _start_game() -> void:
	AppState.begin_new_run()
	get_tree().change_scene_to_file("res://scenes/hero_setup.tscn")


func _open_load() -> void:
	AppState.save_screen_mode = "load"
	AppState.save_return_scene = "res://scenes/main_menu.tscn"
	get_tree().change_scene_to_file("res://scenes/save_screen.tscn")

