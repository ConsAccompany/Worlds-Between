extends SceneTree


func _initialize() -> void:
	call_deferred("_capture")


func _capture() -> void:
	SaveStore.root_path = "user://test-saves/m7-field-traces-visual"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.select_destination("scifi.city")
	app.recruit_member("liang-xu")
	change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	await _settle()
	_save("city-traces-surface-chinese")
	current_scene._open_field_assist()
	await _settle()
	_save("liang-xu-traces-needed-chinese")
	current_scene._close_dialogue()
	current_scene._open_field_trace(0)
	await _settle()
	_save("city-first-trace-chinese")
	current_scene._close_dialogue()
	current_scene._open_field_trace(1)
	app.toggle_language()
	await _settle()
	_save("city-second-trace-english")
	current_scene._close_dialogue()
	current_scene._open_field_assist()
	await _settle()
	_save("liang-xu-traces-ready-english")
	current_scene.get("invite_button").pressed.emit()
	await _settle()
	_save("liang-xu-traces-result-english")
	current_scene._close_dialogue()
	current_scene._return_to_map()
	await _settle()
	current_scene._open_field_log()
	await _settle()
	_save("field-log-traces-english")
	for destination in ["scifi.outskirts", "scifi.ruins"]:
		app.select_destination(destination)
		change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
		await _settle()
		_save(destination.trim_prefix("scifi.") + "-traces-surface-english")
	quit(0)


func _settle() -> void:
	await process_frame
	await process_frame
	await process_frame


func _save(variant: String) -> void:
	var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	var path := "res://../outputs/rpg-2-star-ocean-the-second_scifi-field-traces_%s_m7_%s-%08x.png" % [variant, stamp, randi()]
	var snapshot := root.get_viewport().get_texture().get_image()
	if snapshot == null or snapshot.save_png(path) != OK:
		push_error("Capture failed: " + path)
		quit(1)
		return
	print("CAPTURED " + ProjectSettings.globalize_path(path))
