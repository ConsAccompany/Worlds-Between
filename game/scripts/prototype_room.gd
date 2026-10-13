extends Node2D

const HERO_SPRITE := preload("res://assets/characters/rpg-2-star-ocean-the-second_hero-temp_exploration-sprite_m1_20261013-185701-b7e41a93.svg")
const MOVE_SPEED := 95.0

var hero: Sprite2D
var title_label: Label
var help_label: Label
var back_button: Button


func _ready() -> void:
	_build_room()
	_build_ui()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()


func _process(delta: float) -> void:
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	hero.position += direction * MOVE_SPEED * delta
	hero.position.x = clampf(hero.position.x, 20.0, 620.0)
	hero.position.y = clampf(hero.position.y, 85.0, 340.0)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_return_to_menu()


func _draw() -> void:
	draw_rect(Rect2(0, 0, 640, 360), Color("#182b33"))
	draw_rect(Rect2(16, 72, 608, 274), Color("#28434a"))
	for x in range(16, 625, 32):
		draw_line(Vector2(x, 72), Vector2(x, 346), Color("#33545c"), 1.0)
	for y in range(72, 347, 32):
		draw_line(Vector2(16, y), Vector2(624, y), Color("#33545c"), 1.0)
	draw_rect(Rect2(238, 110, 164, 92), Color("#375760"))
	draw_rect(Rect2(266, 125, 108, 62), Color("#7caa9f"))
	draw_rect(Rect2(293, 144, 54, 23), Color("#122e39"))


func _build_room() -> void:
	hero = Sprite2D.new()
	hero.texture = HERO_SPRITE
	hero.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	hero.scale = Vector2(2, 2)
	hero.position = Vector2(320, 270)
	add_child(hero)


func _build_ui() -> void:
	var canvas := CanvasLayer.new()
	add_child(canvas)

	var header := ColorRect.new()
	header.color = Color("#0d1723")
	header.size = Vector2(640, 66)
	canvas.add_child(header)

	title_label = Label.new()
	title_label.position = Vector2(18, 9)
	title_label.add_theme_font_size_override("font_size", 17)
	title_label.add_theme_color_override("font_color", Color("#eff9f6"))
	canvas.add_child(title_label)

	help_label = Label.new()
	help_label.position = Vector2(18, 38)
	help_label.add_theme_color_override("font_color", Color("#a2c3c5"))
	canvas.add_child(help_label)

	back_button = Button.new()
	back_button.position = Vector2(480, 13)
	back_button.size = Vector2(142, 38)
	back_button.pressed.connect(_return_to_menu)
	canvas.add_child(back_button)


func _refresh_text() -> void:
	title_label.text = AppState.text_for("room_title")
	help_label.text = AppState.text_for("room_help")
	back_button.text = AppState.text_for("back")


func _return_to_menu() -> void:
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")

