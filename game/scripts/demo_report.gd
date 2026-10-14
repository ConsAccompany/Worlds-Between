extends Control

var title_label: Label
var summary_label: Label
var note_label: Label
var continue_button: Button
var map_button: Button


func _ready() -> void:
	_build_ui()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()
	continue_button.grab_focus()


func _build_ui() -> void:
	var background := ColorRect.new()
	background.color = Color("#0c2029")
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(background)
	var stripe := ColorRect.new()
	stripe.color = Color("#71cabe")
	stripe.position = Vector2(58, 59)
	stripe.size = Vector2(8, 242)
	add_child(stripe)
	title_label = Label.new()
	title_label.position = Vector2(91, 76)
	title_label.add_theme_font_size_override("font_size", 24)
	title_label.add_theme_color_override("font_color", Color("#f0ead1"))
	add_child(title_label)
	summary_label = Label.new()
	summary_label.position = Vector2(91, 130)
	summary_label.size = Vector2(460, 64)
	summary_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	summary_label.add_theme_font_size_override("font_size", 14)
	add_child(summary_label)
	note_label = Label.new()
	note_label.position = Vector2(91, 201)
	note_label.size = Vector2(460, 59)
	note_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	note_label.add_theme_font_size_override("font_size", 11)
	note_label.add_theme_color_override("font_color", Color("#aecac6"))
	add_child(note_label)
	continue_button = Button.new()
	continue_button.position = Vector2(91, 279)
	continue_button.size = Vector2(211, 40)
	continue_button.pressed.connect(_return_to_city)
	add_child(continue_button)
	map_button = Button.new()
	map_button.position = Vector2(314, 279)
	map_button.size = Vector2(211, 40)
	map_button.pressed.connect(_return_to_map)
	add_child(map_button)


func _refresh_text() -> void:
	title_label.text = AppState.text_for("report_title")
	summary_label.text = AppState.text_for("report_summary") % [AppState.member_name("hero"), AppState.recruited_members.size()]
	note_label.text = AppState.text_for("report_note")
	note_label.text += "\n" + AppState.play_time_text()
	if AppState.playtest_receipt_path != "":
		note_label.text += "\n" + AppState.text_for("report_receipt")
	continue_button.text = AppState.text_for("report_continue")
	map_button.text = AppState.text_for("report_map")


func _return_to_city() -> void:
	get_tree().change_scene_to_file("res://scenes/scifi_exploration_area.tscn")


func _return_to_map() -> void:
	AppState.resume_area_pending = false
	get_tree().change_scene_to_file("res://scenes/scifi_world_map.tscn")
