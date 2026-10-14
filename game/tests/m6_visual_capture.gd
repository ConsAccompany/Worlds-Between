extends SceneTree


func _initialize() -> void:
	call_deferred("_capture")


func _capture() -> void:
	SaveStore.root_path = "user://test-saves/m6-visual"
	var directory := DirAccess.open(SaveStore.root_path)
	if directory != null:
		for name in directory.get_files():
			if name.ends_with(".json"):
				DirAccess.remove_absolute(ProjectSettings.globalize_path(SaveStore.root_path.path_join(name)))
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.select_destination("scifi.ruins")
	app.recruit_member("liang-xu")
	app.save_return_scene = "res://scenes/scifi_exploration_area.tscn"
	app.save_return_position = Vector2(268, 230)
	app.write_manual_save(1)
	app.write_auto_save("area", Vector2(230, 210), "before_battle")
	app.enemy_cleared_for_return = true
	app.write_auto_save("area", Vector2(230, 210), "after_battle")
	var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	change_scene_to_file("res://scenes/main_menu.tscn")
	await _settle()
	if not _save("main-menu", "load-entry", stamp):
		quit(1)
		return
	current_scene.get("load_button").pressed.emit()
	await _settle()
	if not _save("save-screen", "load-records", stamp):
		quit(1)
		return
	app.save_screen_mode = "save"
	current_scene._refresh()
	await _settle()
	if not _save("save-screen", "manual-and-auto", stamp):
		quit(1)
		return
	app.toggle_language()
	await _settle()
	if not _save("save-screen", "records-english", stamp):
		quit(1)
		return
	quit(0)


func _settle() -> void:
	await process_frame
	await process_frame
	await process_frame


func _save(area: String, purpose: String, stamp: String) -> bool:
	var path := "res://../outputs/rpg-2-star-ocean-the-second_%s_%s_m6_%s-%08x.png" % [area, purpose, stamp, randi()]
	var image := root.get_viewport().get_texture().get_image()
	if image == null or image.save_png(path) != OK:
		push_error("Capture failed: " + path)
		return false
	print("CAPTURED " + ProjectSettings.globalize_path(path))
	return true
