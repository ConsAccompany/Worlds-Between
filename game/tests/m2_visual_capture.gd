extends SceneTree


func _initialize() -> void:
	call_deferred("_capture")


func _capture() -> void:
	var app: Node = root.get_node("AppState")
	var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	var scenes := [
		["map", "", "res://scenes/scifi_world_map.tscn"],
		["city", "scifi.city", "res://scenes/scifi_exploration_area.tscn"],
		["outskirts", "scifi.outskirts", "res://scenes/scifi_exploration_area.tscn"],
		["ruins", "scifi.ruins", "res://scenes/scifi_exploration_area.tscn"],
	]
	for scene in scenes:
		if scene[1] != "":
			app.select_destination(scene[1])
		change_scene_to_file(scene[2])
		await process_frame
		await process_frame
		await process_frame
		var unique_id := "%08x" % randi()
		var path := "res://../outputs/rpg-2-star-ocean-the-second_scifi-%s_visual-proof_m2_%s-%s.png" % [scene[0], stamp, unique_id]
		var image := root.get_viewport().get_texture().get_image()
		if image == null:
			push_error("Capture requires a display renderer")
			quit(1)
			return
		var error := image.save_png(path)
		if error != OK:
			push_error("Capture failed: " + path)
			quit(1)
			return
		print("CAPTURED " + ProjectSettings.globalize_path(path))
	quit(0)
