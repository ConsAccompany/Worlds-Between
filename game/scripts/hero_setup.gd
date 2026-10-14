extends Control

const HERO_SPRITE_MALE := preload("res://assets/characters/rpg-2-star-ocean-the-second_protagonist_exploration-sprite-male_m7_20261013-211119-a51e0b63.svg")
const HERO_SPRITE_FEMALE := preload("res://assets/characters/rpg-2-star-ocean-the-second_protagonist_exploration-sprite-female_m7_20261013-211119-8c2d9e47.svg")

var title_label: Label
var name_label: Label
var name_input: LineEdit
var appearance_label: Label
var male_button: Button
var female_button: Button
var story_label: Label
var controls_label: Label
var start_button: Button
var skip_button: Button
var back_button: Button
var preview: Sprite2D
var appearance := "male"


func _ready() -> void:
	_build_ui()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()
	name_input.grab_focus()


func _build_ui() -> void:
	var background := ColorRect.new()
	background.color = Color("#132733")
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(background)
	var panel := ColorRect.new()
	panel.position = Vector2(45, 34)
	panel.size = Vector2(550, 292)
	panel.color = Color("#25434b")
	add_child(panel)
	var preview_frame := ColorRect.new()
	preview_frame.position = Vector2(467, 85)
	preview_frame.size = Vector2(82, 95)
	preview_frame.color = Color("#17333e")
	add_child(preview_frame)
	preview = Sprite2D.new()
	preview.position = Vector2(508, 133)
	preview.scale = Vector2(3, 3)
	preview.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(preview)
	title_label = _label(Vector2(66, 47), 23, Color("#f0e8cc"))
	name_label = _label(Vector2(68, 98), 13, Color("#c9e0db"))
	name_input = LineEdit.new()
	name_input.position = Vector2(155, 95)
	name_input.size = Vector2(288, 31)
	name_input.max_length = 18
	add_child(name_input)
	appearance_label = _label(Vector2(68, 142), 13, Color("#c9e0db"))
	male_button = Button.new()
	male_button.position = Vector2(155, 137)
	male_button.size = Vector2(137, 31)
	male_button.pressed.connect(_choose_appearance.bind("male"))
	add_child(male_button)
	female_button = Button.new()
	female_button.position = Vector2(305, 137)
	female_button.size = Vector2(138, 31)
	female_button.pressed.connect(_choose_appearance.bind("female"))
	add_child(female_button)
	story_label = _label(Vector2(68, 185), 11, Color("#e4d7b1"))
	story_label.size = Vector2(480, 36)
	story_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	controls_label = _label(Vector2(68, 227), 11, Color("#b7d1cd"))
	controls_label.size = Vector2(480, 34)
	controls_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	start_button = _button(Vector2(67, 274), Vector2(145, 35), _depart.bind(true))
	skip_button = _button(Vector2(224, 274), Vector2(177, 35), _depart.bind(false))
	back_button = _button(Vector2(413, 274), Vector2(139, 35), _back)


func _label(position: Vector2, size: int, color: Color) -> Label:
	var item := Label.new()
	item.position = position
	item.add_theme_font_size_override("font_size", size)
	item.add_theme_color_override("font_color", color)
	add_child(item)
	return item


func _button(position: Vector2, size: Vector2, action: Callable) -> Button:
	var item := Button.new()
	item.position = position
	item.size = size
	item.pressed.connect(action)
	add_child(item)
	return item


func _choose_appearance(selected: String) -> void:
	appearance = selected
	_refresh_text()


func _refresh_text() -> void:
	title_label.text = AppState.text_for("setup_title")
	name_label.text = AppState.text_for("setup_name")
	name_input.placeholder_text = AppState.text_for("member_hero")
	appearance_label.text = AppState.text_for("setup_gender")
	male_button.text = ("✓ " if appearance == "male" else "") + AppState.text_for("setup_male")
	female_button.text = ("✓ " if appearance == "female" else "") + AppState.text_for("setup_female")
	story_label.text = AppState.text_for("setup_help")
	controls_label.text = AppState.text_for("setup_controls")
	start_button.text = AppState.text_for("setup_start")
	skip_button.text = AppState.text_for("setup_skip")
	back_button.text = AppState.text_for("setup_back")
	preview.texture = HERO_SPRITE_FEMALE if appearance == "female" else HERO_SPRITE_MALE


func _depart(show_guide: bool) -> void:
	AppState.hero_name = name_input.text.strip_edges()
	AppState.hero_appearance = appearance
	AppState.show_initial_guide = show_guide
	get_tree().change_scene_to_file("res://scenes/scifi_world_map.tscn")


func _back() -> void:
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
