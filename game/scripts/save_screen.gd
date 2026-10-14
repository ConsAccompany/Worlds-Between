extends Control

var title_label: Label
var back_button: Button
var auto_title: Label
var feedback_label: Label
var manual_labels: Array[Label] = []
var manual_save_buttons: Array[Button] = []
var manual_load_buttons: Array[Button] = []
var auto_labels: Array[Label] = []
var auto_load_buttons: Array[Button] = []


func _ready() -> void:
	_build_ui()
	AppState.language_changed.connect(_refresh)
	_refresh()


func _build_ui() -> void:
	var background := ColorRect.new()
	background.color = Color("#142632")
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(background)
	title_label = _label(Vector2(20, 8), 21, Color("#edf5e8"))
	back_button = _button(Vector2(530, 7), Vector2(92, 31), _back)
	for index in SaveStore.MANUAL_SLOTS:
		var y := 46 + index * 37
		_row(Vector2(16, y - 2), Vector2(608, 34))
		manual_labels.append(_label(Vector2(24, y + 5), 11, Color("#d8e9e4")))
		manual_save_buttons.append(_button(Vector2(433, y + 1), Vector2(90, 27), _save.bind(index + 1)))
		manual_load_buttons.append(_button(Vector2(529, y + 1), Vector2(88, 27), _load_manual.bind(index + 1)))
	auto_title = _label(Vector2(20, 160), 14, Color("#e6d29f"))
	for index in SaveStore.MAX_AUTOS:
		var y := 181 + index * 31
		_row(Vector2(16, y - 2), Vector2(608, 29))
		auto_labels.append(_label(Vector2(24, y + 4), 10, Color("#d3e4dc")))
		auto_load_buttons.append(_button(Vector2(529, y), Vector2(88, 25), _load_auto.bind(index)))
	feedback_label = _label(Vector2(20, 340), 10, Color("#f3d298"))


func _row(at: Vector2, size: Vector2) -> void:
	var panel := ColorRect.new()
	panel.position = at
	panel.size = size
	panel.color = Color("#253c48")
	add_child(panel)


func _label(at: Vector2, size: int, color: Color) -> Label:
	var label := Label.new()
	label.position = at
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	add_child(label)
	return label


func _button(at: Vector2, size: Vector2, callback: Callable) -> Button:
	var button := Button.new()
	button.position = at
	button.size = size
	button.add_theme_font_size_override("font_size", 10)
	button.pressed.connect(callback)
	add_child(button)
	return button


func _latest_manual(slot: int, entries: Array[Dictionary]) -> Dictionary:
	for entry in entries:
		if entry.get("kind", "") == "manual" and int(entry.get("slot", 0)) == slot:
			return entry
	return {}


func _autos(entries: Array[Dictionary]) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for entry in entries:
		if entry.get("kind", "") == "auto":
			result.append(entry)
	return result


func _summary(entry: Dictionary) -> String:
	if int(entry.get("schemaVersion", -1)) != SaveStore.SCHEMA_VERSION:
		return AppState.text_for("save_version_old")
	var snapshot: Dictionary = entry.get("snapshot", {})
	var note := AppState.text_for("save_" + String(snapshot.get("note", "manual_note")))
	return AppState.text_for("save_summary") % [AppState.destination_name(String(snapshot.get("destination", "scifi.city"))), int(snapshot.get("hero", {}).get("level", 1)), snapshot.get("activeParty", []).size(), note]


func _refresh() -> void:
	var entries := SaveStore.list_entries()
	title_label.text = AppState.text_for("save_title")
	back_button.text = AppState.text_for("save_back")
	auto_title.text = AppState.text_for("save_auto")
	for index in SaveStore.MANUAL_SLOTS:
		var entry := _latest_manual(index + 1, entries)
		manual_labels[index].text = AppState.text_for("save_manual_slot") % (index + 1)
		manual_labels[index].text += " · " + (_summary(entry) if not entry.is_empty() else AppState.text_for("save_empty"))
		manual_save_buttons[index].visible = AppState.save_screen_mode == "save"
		manual_save_buttons[index].text = AppState.text_for("save_write")
		manual_load_buttons[index].text = AppState.text_for("save_load")
		manual_load_buttons[index].disabled = entry.is_empty() or int(entry.get("schemaVersion", -1)) != SaveStore.SCHEMA_VERSION
	var autos := _autos(entries)
	for index in SaveStore.MAX_AUTOS:
		auto_labels[index].text = _summary(autos[index]) if index < autos.size() else (AppState.text_for("save_no_records") if index == 0 else "—")
		auto_load_buttons[index].text = AppState.text_for("save_load")
		auto_load_buttons[index].disabled = index >= autos.size() or (index < autos.size() and int(autos[index].get("schemaVersion", -1)) != SaveStore.SCHEMA_VERSION)


func _save(slot: int) -> void:
	var id := AppState.write_manual_save(slot)
	feedback_label.text = AppState.text_for("save_ok") % (AppState.text_for("save_manual_slot") % slot) if id != "" else AppState.text_for("save_failed")
	_refresh()


func _load_manual(slot: int) -> void:
	var entry := _latest_manual(slot, SaveStore.list_entries())
	_load(String(entry.get("id", "")))


func _load_auto(index: int) -> void:
	var autos := _autos(SaveStore.list_entries())
	if index < autos.size():
		_load(String(autos[index]["id"]))


func _load(id: String) -> void:
	if not AppState.load_save(id):
		feedback_label.text = AppState.text_for("save_load_failed")
		return
	get_tree().change_scene_to_file(AppState.loaded_scene_path())


func _back() -> void:
	if AppState.save_screen_mode == "save" and AppState.save_return_scene.ends_with("scifi_exploration_area.tscn"):
		AppState.resume_area_pending = true
		AppState.resume_area_position = AppState.save_return_position
	elif AppState.save_screen_mode == "save" and AppState.save_return_scene.ends_with("survey_annex.tscn"):
		AppState.resume_annex_pending = true
		AppState.resume_annex_position = AppState.save_return_position
	get_tree().change_scene_to_file(AppState.save_return_scene)
