extends SceneTree


func _initialize() -> void:
	call_deferred("_capture")


func _capture() -> void:
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app._grant_growth(app.hero_state, 630, 0)
	app.choose_job("hero", "promote")
	app.recruit_member("liang-xu")
	app.recruit_member("zhao-ling")
	app.ji_records_checked = true
	app.recruit_member("ji-cheng")
	app.begin_battle("sentry", Vector2(330, 215))
	change_scene_to_file("res://scenes/battle_arena.tscn")
	await process_frame
	await process_frame
	await process_frame
	var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	if not _save("job-skills-battle", stamp):
		quit(1)
		return
	current_scene._toggle_pause()
	await process_frame
	await process_frame
	if not _save("job-skills-pause", stamp):
		quit(1)
		return
	quit(0)


func _save(purpose: String, stamp: String) -> bool:
	var path := "res://../outputs/rpg-2-star-ocean-the-second_scifi-party_%s_m5_%s-%08x.png" % [purpose, stamp, randi()]
	var image := root.get_viewport().get_texture().get_image()
	if image == null or image.save_png(path) != OK:
		push_error("Capture failed: " + path)
		return false
	print("CAPTURED " + ProjectSettings.globalize_path(path))
	return true
