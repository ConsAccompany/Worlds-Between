extends Control

const CONTENT := preload("res://scripts/party_talk_content.gd")

var available_topics: Array[Dictionary] = []
var active_topic: Dictionary = {}
var line_index := 0
var title_label: Label
var help_label: Label
var empty_label: Label
var bond_label: Label
var back_button: Button
var topic_buttons: Array[Button] = []
var overlay: ColorRect
var conversation_title: Label
var speaker_label: Label
var body_label: Label
var next_button: Button
var topics_button: Button


func _ready() -> void:
	for topic in CONTENT.TOPICS:
		var allowed := true
		for member_id in topic["participants"]:
			if not AppState.recruited_members.has(member_id):
				allowed = false
		for destination_id in topic["requires"]:
			if not AppState.survey_solved.has(destination_id):
				allowed = false
		if allowed:
			available_topics.append(topic)
	_build_ui()
	AppState.language_changed.connect(_refresh_text)
	_refresh_text()
	back_button.grab_focus()


func _build_ui() -> void:
	var background := ColorRect.new()
	background.color = Color("#11232d")
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(background)
	var header := ColorRect.new()
	header.color = Color("#0d1723")
	header.size = Vector2(640, 63)
	add_child(header)
	title_label = _label(Vector2(24, 11), Vector2(430, 29), 20, Color("#f1e5c5"))
	back_button = _button(Vector2(506, 11), Vector2(109, 39), _back)
	help_label = _label(Vector2(24, 76), Vector2(590, 31), 12, Color("#bdd3cd"))
	help_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	for index in 6:
		var button := _button(Vector2(24 + (index % 2) * 305, 115 + (index / 2) * 57), Vector2(287, 47), _open_topic.bind(index))
		button.add_theme_font_size_override("font_size", 12)
		topic_buttons.append(button)
	empty_label = _label(Vector2(38, 154), Vector2(555, 70), 15, Color("#e8d9b4"))
	empty_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	bond_label = _label(Vector2(24, 316), Vector2(585, 30), 11, Color("#9fcac2"))
	_build_overlay()


func _build_overlay() -> void:
	overlay = ColorRect.new()
	overlay.color = Color(0.04, 0.08, 0.12, 0.95)
	overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	overlay.visible = false
	add_child(overlay)
	var panel := ColorRect.new()
	panel.color = Color("#29434d")
	panel.position = Vector2(52, 43)
	panel.size = Vector2(536, 274)
	overlay.add_child(panel)
	conversation_title = _label(Vector2(76, 62), Vector2(480, 31), 19, Color("#f2e5c1"), overlay)
	topics_button = _button(Vector2(445, 58), Vector2(118, 34), _back, overlay)
	speaker_label = _label(Vector2(76, 117), Vector2(480, 27), 15, Color("#92ded0"), overlay)
	body_label = _label(Vector2(76, 151), Vector2(485, 80), 14, Color("#e9f4f0"), overlay)
	body_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	next_button = _button(Vector2(367, 265), Vector2(196, 36), _next_line, overlay)


func _label(position: Vector2, size: Vector2, font_size: int, color: Color, parent: Node = self) -> Label:
	var label := Label.new()
	label.position = position
	label.size = size
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	parent.add_child(label)
	return label


func _button(position: Vector2, size: Vector2, callback: Callable, parent: Node = self) -> Button:
	var button := Button.new()
	button.position = position
	button.size = size
	button.pressed.connect(callback)
	parent.add_child(button)
	return button


func _refresh_text() -> void:
	title_label.text = AppState.text_for("talk_title")
	help_label.text = AppState.text_for("talk_help")
	back_button.text = AppState.text_for("talk_back")
	topics_button.text = AppState.text_for("talk_topics")
	empty_label.text = AppState.text_for("talk_empty")
	empty_label.visible = available_topics.is_empty()
	for index in topic_buttons.size():
		var button := topic_buttons[index]
		button.visible = index < available_topics.size()
		if button.visible:
			var topic: Dictionary = available_topics[index]
			button.text = String(topic[AppState.language]["title"]) + ("  ✓" if AppState.party_talk_seen.has(topic["id"]) else "")
	var bond_parts: Array[String] = []
	for member_id in ["liang-xu", "zhao-ling", "ji-cheng"]:
		if AppState.recruited_members.has(member_id):
			bond_parts.append(AppState.member_name(member_id) + " · " + AppState.text_for("talk_bond") % int(AppState.party_bonds.get(member_id, 0)))
	bond_label.text = "  |  ".join(bond_parts)
	if overlay.visible:
		_refresh_line()


func _open_topic(index: int) -> void:
	if index < 0 or index >= available_topics.size():
		return
	active_topic = available_topics[index]
	line_index = 0
	overlay.visible = true
	_refresh_line()
	next_button.grab_focus()


func _refresh_line() -> void:
	if active_topic.is_empty():
		return
	var data: Dictionary = active_topic[AppState.language]
	var lines: Array = data["lines"]
	var line: Array = lines[line_index]
	conversation_title.text = String(data["title"])
	speaker_label.text = AppState.member_name(String(line[0]))
	body_label.text = String(line[1])
	next_button.text = AppState.text_for("talk_finish" if line_index == lines.size() - 1 else "talk_next")


func _next_line() -> void:
	var lines: Array = active_topic[AppState.language]["lines"]
	if line_index + 1 < lines.size():
		line_index += 1
		_refresh_line()
		return
	AppState.record_party_talk(String(active_topic["id"]), active_topic["participants"])
	overlay.visible = false
	active_topic = {}
	_refresh_text()
	back_button.grab_focus()


func _back() -> void:
	if overlay.visible:
		overlay.visible = false
		active_topic = {}
		back_button.grab_focus()
	else:
		get_tree().change_scene_to_file("res://scenes/scifi_world_map.tscn")


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_back()
