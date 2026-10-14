extends SceneTree


func _initialize() -> void:
	call_deferred("_capture")


func _capture() -> void:
	SaveStore.root_path = "user://test-saves/m7-notes-visual"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.current_destination_id = "scifi.city"
	app.current_annex_room = 2
	for index in 6:
		app.survey_clues["scifi.city:%d" % index] = true
	change_scene_to_file("res://scenes/survey_annex.tscn")
	await _settle()
	current_scene._open_question()
	current_scene.get("notes_button").pressed.emit()
	await _settle()
	if not _save("chinese"):
		return
	app.toggle_language()
	await _settle()
	if not _save("english"):
		return
	quit(0)


func _settle() -> void:
	await process_frame
	await process_frame
	await process_frame


func _save(locale: String) -> bool:
	var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	var path := "res://../outputs/rpg-2-star-ocean-the-second_scifi-city_clue-notes-%s_m7_%s-%08x.png" % [locale, stamp, randi()]
	var image := root.get_viewport().get_texture().get_image()
	if image == null or image.save_png(path) != OK:
		push_error("Capture failed: " + path)
		quit(1)
		return false
	print("CAPTURED " + ProjectSettings.globalize_path(path))
	return true
