extends SceneTree

# Complements the city path tests: decline, leave, return, switch language,
# recruit, and reload. It checks state and cues, not visual quality.


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	SaveStore.root_path = "user://test-saves/m8-qa-reentry"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.select_destination("scifi.city")
	change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	await _settle()
	var city: Node2D = current_scene
	if not _check(city.get("city_npc") != null and city.get("city_npc").visible, "Liang appears before invitation"):
		return
	if not _check(_cues_match(city, app), "Chinese city cues are present"):
		return
	if not _check(_nearby_cues_appear(city), "Chinese proximity cues appear near their hotspots"):
		return
	city.get("hero").position = Vector2(282, 180)
	city._unhandled_input(_interact())
	if not _check(city.get("dialogue_open") and city.get("dialogue_mode") == "recruit", "Liang conversation opens"):
		return
	city.get("later_button").pressed.emit()
	if not _check(not app.recruited_members.has("liang-xu") and city.get("city_npc").visible, "declining leaves Liang available"):
		return
	city.get("back_button").pressed.emit()
	await _settle()
	if not _check(current_scene.name == "ScifiWorldMap", "leave city after declining"):
		return
	app.toggle_language()
	app.select_destination("scifi.city")
	change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	await _settle()
	city = current_scene
	if not _check(city.get("city_npc").visible and city.get("npc_label").visible, "Liang remains visible on revisit"):
		return
	if not _check(_cues_match(city, app), "English city cues are present on revisit"):
		return
	if not _check(_nearby_cues_appear(city), "English proximity cues appear near their hotspots"):
		return
	city.get("hero").position = Vector2(282, 180)
	city._unhandled_input(_interact())
	city.get("invite_button").pressed.emit()
	if not _check(app.recruited_members.has("liang-xu") and not city.get("city_npc").visible and not city.get("npc_label").visible, "invitation hides Liang and label"):
		return
	city._open_save()
	await _settle()
	if not _check(current_scene.name == "SaveScreen", "city opens manual save screen"):
		return
	current_scene.get("manual_save_buttons")[0].pressed.emit()
	var save_id := ""
	for entry in SaveStore.list_entries():
		if entry.get("kind", "") == "manual" and int(entry.get("slot", 0)) == 1:
			save_id = String(entry["id"])
			break
	if not _check(save_id != "", "recruited state can be saved"):
		return
	app.begin_new_run()
	if not _check(app.load_save(save_id), "recruited state can be loaded"):
		return
	change_scene_to_file(app.loaded_scene_path())
	await _settle()
	city = current_scene
	if not _check(city.name == "ScifiExplorationArea" and app.recruited_members.has("liang-xu") and not city.get("city_npc").visible and not city.get("npc_label").visible, "Liang stays hidden after reload"):
		return
	if not _check(_cues_match(city, app), "English city cues survive reload"):
		return
	print("M8_CITY_REENTRY_OK")
	quit(0)


func _cues_match(city: Node2D, app: Node) -> bool:
	return city.get("survey_label").visible and city.get("survey_label").text == app.text_for("survey_marker") \
		and city.get("assist_label").text == app.text_for("field_assist_marker_city") \
		and city.get("station_label").visible and city.get("station_label").text == app.text_for("report_marker") \
		and city.get("trace_labels").size() == 2 and city.get("trace_labels")[0].text.begins_with(app.text_for("field_trace_marker"))


func _nearby_cues_appear(city: Node2D) -> bool:
	var actor: Sprite2D = city.get("hero")
	var original_position := actor.position
	actor.position = city.FIELD_ASSISTS["scifi.city"]["position"]
	city._update_city_labels()
	var assist_visible: bool = city.get("assist_label").visible
	actor.position = city.FIELD_TRACES["scifi.city"][0]
	city._update_city_labels()
	var trace_visible: bool = city.get("trace_labels")[0].visible
	actor.position = original_position
	city._update_city_labels()
	return assist_visible and trace_visible


func _interact() -> InputEventAction:
	var event := InputEventAction.new()
	event.action = "interact"
	event.pressed = true
	return event


func _settle() -> void:
	await process_frame
	await process_frame


func _check(condition: bool, description: String) -> bool:
	if condition:
		return true
	push_error("M8 city reentry failed: " + description)
	quit(1)
	return false
