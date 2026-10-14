extends SceneTree

# Takes actual 640x360 engine viewports for visual review. It does not approve art.
var captures: Array[String] = []


func _initialize() -> void:
	call_deferred("_run")


func _settle() -> void:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw


func _capture(scene_name: String) -> void:
	var directory := OS.get_environment("WB_M8_SCENE_EVIDENCE_DIR")
	if directory.is_empty() or DisplayServer.get_name() == "headless":
		return
	DirAccess.make_dir_recursive_absolute(directory)
	await RenderingServer.frame_post_draw
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var name := "rpg-2-star-ocean-the-second_%s_in-engine-capture_m8-v01_%s-%08x.png" % [scene_name, stamp, randi()]
	if root.get_texture().get_image().save_png(directory.path_join(name)) != OK:
		push_error("Unable to save " + name)
		quit(1)
		return
	captures.append(name)


func _run() -> void:
	SaveStore.root_path = "user://test-saves/m8-region-art-capture"
	var app: Node = root.get_node("AppState")
	for destination in ["scifi.outskirts", "scifi.ruins"]:
		app.begin_new_run()
		app.hero_appearance = "male" if destination == "scifi.outskirts" else "female"
		app.select_destination(destination)
		change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
		await _settle()
		current_scene.set_process(false)
		await _capture(destination.replace(".", "-") + "-recruit")
	for destination in ["scifi.city", "scifi.outskirts", "scifi.ruins"]:
		for room in [1, 2]:
			app.begin_new_run()
			app.hero_appearance = "male" if room == 1 else "female"
			app.select_destination(destination)
			app.current_annex_room = room
			change_scene_to_file("res://scenes/survey_annex.tscn")
			await _settle()
			current_scene.set_process(false)
			await _capture(destination.replace(".", "-") + "-annex-%02d" % room)
	var directory := OS.get_environment("WB_M8_SCENE_EVIDENCE_DIR")
	if not directory.is_empty():
		var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
		var name := "rpg-2-star-ocean-the-second_scifi-region_art-capture-manifest_m8-v01_%s-%08x.json" % [stamp, randi()]
		var file := FileAccess.open(directory.path_join(name), FileAccess.WRITE)
		file.store_string(JSON.stringify({"canvas": [640, 360], "artAccepted": false, "humanPlaytest": false, "captures": captures}, "\t") + "\n")
	print("M8_REGION_ART_CAPTURE_OK " + str(captures.size()))
	quit(0)
