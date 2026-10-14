extends Control

# Internal art review scene only. It is intentionally absent from the game flow.
const REGISTRY_PATH := "res://data/character-visuals/rpg-2-star-ocean-the-second_character-visual-registry_m8-v01_20261014-134810-2a5d1b3c.json"
const IMAGE_BOX := Rect2(16, 60, 608, 238)

var entries: Array = []
var current_index := -1
var current_image_size := Vector2i.ZERO
var last_error := ""
var portrait: TextureRect
var name_label: Label
var status_label: Label
var count_label: Label
var identity_label: Label
var source_label: Label


func _ready() -> void:
	_build_ui()
	if load_registry():
		show_index(0)
	else:
		name_label.text = "无法读取视觉注册表 / Registry unavailable"
		status_label.text = last_error


func load_registry() -> bool:
	last_error = ""
	var file := FileAccess.open(REGISTRY_PATH, FileAccess.READ)
	if file == null:
		last_error = "Registry file missing"
		return false
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	file.close()
	if not parsed is Dictionary or not parsed.has("entries") or not parsed["entries"] is Array:
		last_error = "Registry structure invalid"
		return false
	entries = parsed["entries"]
	if entries.size() != 52:
		last_error = "Expected 52 visual variants"
		return false
	return true


func show_index(index: int) -> bool:
	if entries.is_empty():
		last_error = "No entries"
		return false
	var next_index := posmod(index, entries.size())
	var entry: Dictionary = entries[next_index]
	var portrait_data: Dictionary = entry.get("source_portrait", {})
	var source_path := String(portrait_data.get("path", ""))
	var texture := _load_portrait(source_path)
	if texture == null:
		return false
	current_index = next_index
	portrait.texture = texture
	portrait.tooltip_text = source_path
	current_image_size = texture.get_size()
	var approved := String(portrait_data.get("approval", "")) == "approved"
	name_label.text = "%s  ·  %s" % [String(entry.get("display_name_zh", "")), String(entry.get("visual_id", ""))]
	status_label.text = "来源画像：已批准 / APPROVED" if approved else "来源画像：概念待审 / CONCEPT"
	status_label.add_theme_color_override("font_color", Color("#9ce0bd") if approved else Color("#e9ca85"))
	count_label.text = "%02d / %02d" % [current_index + 1, entries.size()]
	identity_label.text = "%s  ·  %s" % [String(entry.get("region", "")), String(entry.get("identity_and_hair_anchor", ""))]
	source_label.text = "来源已批准 9 · 概念 43 · 游戏内精灵未因此验收"
	return true


func _load_portrait(relative_path: String) -> ImageTexture:
	last_error = ""
	if not relative_path.begins_with("outputs/") or relative_path.contains(".."):
		last_error = "Unsafe source path: " + relative_path
		return null
	var game_dir := ProjectSettings.globalize_path("res://").trim_suffix("/").trim_suffix("\\")
	var repo_dir := game_dir.get_base_dir()
	var source_path := repo_dir.path_join(relative_path)
	var image := Image.new()
	var result := image.load(source_path)
	if result != OK or image.is_empty():
		last_error = "Image unavailable: " + relative_path
		return null
	return ImageTexture.create_from_image(image)


func _label(parent: Node, at: Vector2, size: Vector2, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.position = at
	label.size = size
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.clip_text = true
	parent.add_child(label)
	return label


func _build_ui() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var background := ColorRect.new()
	background.color = Color("#101a22")
	background.size = Vector2(640, 360)
	add_child(background)
	var header := ColorRect.new()
	header.color = Color("#172b32")
	header.size = Vector2(640, 56)
	add_child(header)
	_label(self, Vector2(18, 7), Vector2(410, 25), 17, Color("#e8ece5")).text = "人物设定图审查 / Character Source Art"
	_label(self, Vector2(344, 13), Vector2(218, 19), 10, Color("#b5c9c6")).text = "来源已批准 9  ·  概念 43"
	name_label = _label(self, Vector2(18, 33), Vector2(315, 21), 12, Color("#cad9d1"))
	status_label = _label(self, Vector2(337, 34), Vector2(236, 20), 11, Color("#e9ca85"))
	count_label = _label(self, Vector2(574, 10), Vector2(52, 23), 13, Color("#d4e7e1"))
	count_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	var image_back := ColorRect.new()
	image_back.color = Color("#27343a")
	image_back.position = IMAGE_BOX.position
	image_back.size = IMAGE_BOX.size
	add_child(image_back)
	portrait = TextureRect.new()
	portrait.position = IMAGE_BOX.position
	portrait.size = IMAGE_BOX.size
	portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	portrait.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	add_child(portrait)
	var footer := ColorRect.new()
	footer.color = Color("#172b32")
	footer.position = Vector2(0, 302)
	footer.size = Vector2(640, 58)
	add_child(footer)
	var previous := Button.new()
	previous.name = "PreviousButton"
	previous.text = "← 上一张"
	previous.position = Vector2(16, 311)
	previous.size = Vector2(96, 34)
	previous.add_theme_font_size_override("font_size", 12)
	previous.pressed.connect(func() -> void: show_index(current_index - 1))
	add_child(previous)
	var next := Button.new()
	next.name = "NextButton"
	next.text = "下一张 →"
	next.position = Vector2(528, 311)
	next.size = Vector2(96, 34)
	next.add_theme_font_size_override("font_size", 12)
	next.pressed.connect(func() -> void: show_index(current_index + 1))
	add_child(next)
	identity_label = _label(self, Vector2(122, 307), Vector2(395, 21), 10, Color("#b5cec4"))
	source_label = _label(self, Vector2(122, 328), Vector2(395, 18), 9, Color("#8ea9a7"))


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_LEFT:
			show_index(current_index - 1)
		elif event.keycode == KEY_RIGHT:
			show_index(current_index + 1)
		elif event.keycode == KEY_ESCAPE:
			get_tree().quit()
