extends SceneTree


func _initialize() -> void:
	call_deferred("_capture")


func _capture() -> void:
	var app: Node = root.get_node("AppState")
	var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	app.begin_new_run()
	app._grant_growth(app.hero_state, 630, 100)
	change_scene_to_file("res://scenes/growth_screen.tscn")
	await _settle()
	if not _save("hero", "mandatory-job-choice", stamp):
		quit(1)
		return
	current_scene.get("promote_button").pressed.emit()
	await _settle()
	if not _save("hero", "promoted-skill-growth", stamp):
		quit(1)
		return
	app.toggle_language()
	await _settle()
	if not _save("hero", "job-growth-english", stamp):
		quit(1)
		return
	quit(0)


func _settle() -> void:
	await process_frame
	await process_frame
	await process_frame


func _save(area: String, purpose: String, stamp: String) -> bool:
	var path := "res://../outputs/rpg-2-star-ocean-the-second_%s_%s_m5_%s-%08x.png" % [area, purpose, stamp, randi()]
	var image := root.get_viewport().get_texture().get_image()
	if image == null or image.save_png(path) != OK:
		push_error("Capture failed: " + path)
		return false
	print("CAPTURED " + ProjectSettings.globalize_path(path))
	return true
