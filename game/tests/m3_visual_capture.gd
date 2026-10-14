extends SceneTree


func _initialize() -> void:
	call_deferred("_capture")


func _capture() -> void:
	var app: Node = root.get_node("AppState")
	var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	for enemy_id in ["patrol", "sentry"]:
		app.begin_new_run()
		app.begin_battle(enemy_id, Vector2(82, 260))
		change_scene_to_file("res://scenes/battle_arena.tscn")
		await process_frame
		await process_frame
		await process_frame
		var path := "res://../outputs/rpg-2-star-ocean-the-second_scifi-%s_battle-visual-proof_m3_%s-%08x.png" % [enemy_id, stamp, randi()]
		if not _save_capture(path):
			quit(1)
			return
		if enemy_id == "patrol":
			current_scene._finish_battle(true)
			await process_frame
			var result_path := "res://../outputs/rpg-2-star-ocean-the-second_scifi-patrol_victory-visual-proof_m3_%s-%08x.png" % [stamp, randi()]
			if not _save_capture(result_path):
				quit(1)
				return
	quit(0)


func _save_capture(path: String) -> bool:
	var image := root.get_viewport().get_texture().get_image()
	if image == null or image.save_png(path) != OK:
		push_error("Capture failed: " + path)
		return false
	print("CAPTURED " + ProjectSettings.globalize_path(path))
	return true
