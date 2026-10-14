extends SceneTree

const NativeMotion := preload("res://scripts/character_directional_motion.gd")

var captured: Array[Dictionary] = []


func _initialize() -> void:
	call_deferred("_run")


func _capture(character_id: String, direction: String, phase: int) -> void:
	await RenderingServer.frame_post_draw
	var directory := OS.get_environment("WB_MOTION_EVIDENCE_DIR")
	DirAccess.make_dir_recursive_absolute(directory)
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var name := "rpg-2-star-ocean-the-second_%s_native-walk-in-engine-%s-phase-%02d_m8-v01_%s-%08x.png" % [character_id, direction, phase, stamp, randi()]
	var error := root.get_texture().get_image().save_png(directory.path_join(name))
	assert(error == OK)
	captured.append({"character": character_id, "direction": direction, "phase": phase, "file": name})


func _run() -> void:
	if DisplayServer.get_name() == "headless":
		push_error("Rendered capture requires a display")
		quit(1)
		return
	var directory := OS.get_environment("WB_MOTION_EVIDENCE_DIR")
	if directory.is_empty():
		push_error("WB_MOTION_EVIDENCE_DIR required")
		quit(1)
		return
	var app: Node = root.get_node("AppState")
	for appearance in ["male", "female"]:
		app.begin_new_run()
		app.hero_appearance = appearance
		app.select_destination("scifi.city")
		change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
		await process_frame
		await process_frame
		var area: Node2D = current_scene
		area.set_process(false)
		var actor: Sprite2D = area.get("hero")
		for direction in ["south", "west", "north", "east"]:
			actor.texture = NativeMotion.texture_for("protagonist-" + appearance, "walk", direction, 2)
			await _capture("protagonist-" + appearance, direction, 2)
	# Liang Xu is static in the playable scene; pose his walk frames here only
	# for game-scale visual inspection against the same city background.
	var area: Node2D = current_scene
	var npc: Sprite2D = area.get("city_npc")
	if npc != null:
		for direction in ["south", "west", "north", "east"]:
			npc.texture = NativeMotion.texture_for("liang-xu", "walk", direction, 2)
			await _capture("liang-xu", direction, 2)
	var manifest_name := "rpg-2-star-ocean-the-second_scifi-city_native-motion-capture-manifest_m8-v01_%s-%08x.json" % [Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-"), randi()]
	var file := FileAccess.open(directory.path_join(manifest_name), FileAccess.WRITE)
	file.store_string(JSON.stringify({"canvas": [640, 360], "accepted": false, "captures": captured}, "\t") + "\n")
	print("M8_MOTION_CAPTURE_OK " + directory.path_join(manifest_name))
	quit(0)
