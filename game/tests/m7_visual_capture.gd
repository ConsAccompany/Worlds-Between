extends SceneTree


func _initialize() -> void:
	call_deferred("_capture")


func _capture() -> void:
	SaveStore.root_path = "user://test-saves/m7-visual"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	change_scene_to_file("res://scenes/hero_setup.tscn")
	await _settle()
	current_scene.get("name_input").text = "阿澈"
	current_scene.get("female_button").pressed.emit()
	await _settle()
	if not _save("protagonist", "female-setup", stamp): return
	current_scene.get("skip_button").pressed.emit()
	await _settle()
	current_scene._open_field_log()
	await _settle()
	if not _save("scifi-map", "field-log-chinese", stamp): return
	current_scene._close_field_log()
	current_scene._enter_destination("scifi.outskirts")
	await _settle()
	if not _save("scifi-outskirts", "relay-exploration", stamp): return
	app.relay_checked = true
	app.machine_observed = true
	app.areas_visited = {"scifi.city": true, "scifi.outskirts": true, "scifi.ruins": true}
	app.ji_records_checked = true
	app.current_destination_id = "scifi.city"
	change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	await _settle()
	current_scene.get("hero").position = Vector2(558, 143)
	current_scene._unhandled_input(_interact())
	await _settle()
	if not _save("scifi-city", "survey-outer-room", stamp): return
	current_scene._inspect_clue(0)
	await _settle()
	if not _save("scifi-city", "survey-clue-chinese", stamp): return
	current_scene._close_overlay()
	for index in [1, 2]:
		current_scene._inspect_clue(index)
		current_scene._close_overlay()
	current_scene._go_next_room()
	await _settle()
	for index in [3, 4, 5]:
		current_scene._inspect_clue(index)
		current_scene._close_overlay()
	current_scene._open_question()
	await _settle()
	if not _save("scifi-city", "survey-question-chinese", stamp): return
	app.toggle_language()
	await _settle()
	if not _save("scifi-city", "survey-question-english", stamp): return
	current_scene._choose_answer(1)
	current_scene._close_overlay()
	current_scene._back_room()
	await _settle()
	current_scene._back_room()
	await _settle()
	app.toggle_language()
	app.survey_solved["scifi.outskirts"] = true
	app.survey_solved["scifi.ruins"] = true
	current_scene.get("hero").position = Vector2(470, 247)
	current_scene._unhandled_input(_interact())
	await _settle()
	if not _save("scifi-city", "completion-report-chinese", stamp): return
	app.toggle_language()
	await _settle()
	if not _save("scifi-city", "completion-report-english", stamp): return
	current_scene.get("map_button").pressed.emit()
	await _settle()
	current_scene._open_field_log()
	await _settle()
	if not _save("scifi-map", "field-log-english", stamp): return
	quit(0)


func _interact() -> InputEventAction:
	var event := InputEventAction.new()
	event.action = "interact"
	event.pressed = true
	return event


func _settle() -> void:
	await process_frame
	await process_frame
	await process_frame


func _save(area: String, purpose: String, stamp: String) -> bool:
	var path := "res://../outputs/rpg-2-star-ocean-the-second_%s_%s_m7_%s-%08x.png" % [area, purpose, stamp, randi()]
	var image := root.get_viewport().get_texture().get_image()
	if image == null or image.save_png(path) != OK:
		push_error("Capture failed: " + path)
		quit(1)
		return false
	print("CAPTURED " + ProjectSettings.globalize_path(path))
	return true
