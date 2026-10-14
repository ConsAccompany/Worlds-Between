extends SceneTree


func _initialize() -> void:
	call_deferred("_capture")


func _capture() -> void:
	var app: Node = root.get_node("AppState")
	var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	app.begin_new_run()
	app.select_destination("scifi.city")
	change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	await _settle()
	var area: Node2D = current_scene
	if not _save("scifi-city", "companion-exploration", stamp):
		quit(1)
		return
	area.get("hero").position = area.get("npc_position")
	area._open_dialogue()
	await _settle()
	if not _save("scifi-liang-xu", "recruitment-dialogue", stamp):
		quit(1)
		return
	app.recruit_member("liang-xu")
	app.recruit_member("zhao-ling")
	app.ji_records_checked = true
	app.recruit_member("ji-cheng")
	app.begin_battle("sentry", Vector2(82, 260))
	change_scene_to_file("res://scenes/battle_arena.tscn")
	await _settle()
	if not _save("scifi-party", "battle-hud", stamp):
		quit(1)
		return
	current_scene._choose_control(1)
	current_scene._toggle_pause()
	current_scene._select_order_target("zhao-ling")
	current_scene._issue_order("defend")
	await _settle()
	if not _save("scifi-party", "pause-orders", stamp):
		quit(1)
		return
	quit(0)


func _settle() -> void:
	await process_frame
	await process_frame
	await process_frame


func _save(area: String, purpose: String, stamp: String) -> bool:
	var path := "res://../outputs/rpg-2-star-ocean-the-second_%s_%s_m4_%s-%08x.png" % [area, purpose, stamp, randi()]
	var image := root.get_viewport().get_texture().get_image()
	if image == null or image.save_png(path) != OK:
		push_error("Capture failed: " + path)
		return false
	print("CAPTURED " + ProjectSettings.globalize_path(path))
	return true
