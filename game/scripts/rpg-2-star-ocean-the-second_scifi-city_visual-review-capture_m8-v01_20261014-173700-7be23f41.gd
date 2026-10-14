extends SceneTree

# Run with a rendered Godot window and WB_CITY_EVIDENCE_DIR set to an absolute
# directory. Captures are actual playable-scene viewport images, not mockups.
var captures: Array[String] = []
var evidence_dir := ""


func _initialize() -> void:
	call_deferred("_run")


func _settle() -> void:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw


func _capture(variant: String) -> void:
	await _settle()
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var filename := "rpg-2-star-ocean-the-second_scifi-city_engine-viewport_m8-%s_%s-%08x.png" % [variant, stamp, randi()]
	var result := root.get_texture().get_image().save_png(evidence_dir.path_join(filename))
	if result != OK:
		push_error("Capture failed: " + variant)
		quit(1)
		return
	captures.append(filename)


func _city(appearance: String) -> Node2D:
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.language = "en" if appearance == "female" else "zh"
	app.hero_appearance = appearance
	app.select_destination("scifi.city")
	change_scene_to_file("res://scenes/scifi_exploration_area.tscn")
	await _settle()
	var area: Node2D = current_scene
	area.set_process(false)
	return area


func _run() -> void:
	evidence_dir = OS.get_environment("WB_CITY_EVIDENCE_DIR")
	if evidence_dir.is_empty() or DisplayServer.get_name() == "headless":
		push_error("Set WB_CITY_EVIDENCE_DIR and use a rendered display")
		quit(1)
		return
	DirAccess.make_dir_recursive_absolute(evidence_dir)
	SaveStore.root_path = "user://test-saves/m8-city-review"
	var area := await _city("male")
	area.hero.position = Vector2(128, 187)
	area.hero.z_index = 187
	area._update_city_labels()
	await _capture("male-garden-occlusion")
	area = await _city("female")
	area.hero.position = Vector2(444, 244)
	area.hero.z_index = 244
	area._update_city_labels()
	await _capture("female-report-hotspot")
	area.hero.position = Vector2(282, 180)
	area.hero.z_index = 180
	area._update_city_labels()
	await _capture("female-liang-before")
	root.get_node("AppState").recruit_member("liang-xu")
	area._refresh_text()
	await _capture("female-liang-after")
	var stamp := Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	var manifest_name := "rpg-2-star-ocean-the-second_scifi-city_engine-capture-manifest_m8-v01_%s-%08x.json" % [stamp, randi()]
	var file := FileAccess.open(evidence_dir.path_join(manifest_name), FileAccess.WRITE)
	file.store_string(JSON.stringify({"scene": "scifi.city", "canvas": [640, 360], "source": "Godot 4.7.2 rendered playable scene", "artAccepted": false, "humanPlaytest": false, "captures": captures}, "\t") + "\n")
	print("CITY_VISUAL_CAPTURE_OK " + str(captures.size()))
	quit(0)
