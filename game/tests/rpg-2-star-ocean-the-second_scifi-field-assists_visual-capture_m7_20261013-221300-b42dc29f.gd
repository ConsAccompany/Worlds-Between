extends SceneTree


func _initialize() -> void:
	call_deferred("_capture")


func _capture() -> void:
	SaveStore.root_path = "user://test-saves/m7-field-assists-visual"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.select_destination("scifi.city")
	app.recruit_member("liang-xu")
	change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	await _settle()
	current_scene.get("hero").position = Vector2(120, 187)
	await _settle()
	if not _save("city-station-chinese"):
		return
	current_scene._open_field_assist()
	await _settle()
	if not _save("liang-xu-ready-chinese"):
		return
	current_scene.get("invite_button").pressed.emit()
	app.toggle_language()
	await _settle()
	if not _save("liang-xu-result-english"):
		return
	current_scene._close_dialogue()
	current_scene._return_to_map()
	await _settle()
	current_scene._open_field_log()
	await _settle()
	if not _save("field-log-english"):
		return
	app.begin_new_run()
	app.select_destination("scifi.city")
	change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	await _settle()
	current_scene._open_field_assist()
	await _settle()
	if not _save("liang-xu-locked-english"):
		return
	quit(0)


func _settle() -> void:
	await process_frame
	await process_frame
	await process_frame


func _save(variant: String) -> bool:
	var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	var path := "res://../outputs/rpg-2-star-ocean-the-second_scifi-field-assists_%s_m7_%s-%08x.png" % [variant, stamp, randi()]
	var image := root.get_viewport().get_texture().get_image()
	if image == null or image.save_png(path) != OK:
		push_error("Capture failed: " + path)
		quit(1)
		return false
	print("CAPTURED " + ProjectSettings.globalize_path(path))
	return true
