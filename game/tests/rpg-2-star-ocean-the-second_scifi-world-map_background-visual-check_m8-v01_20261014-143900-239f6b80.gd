extends SceneTree

# Targeted map composition and destination-button regression check.
# The screenshots are visual evidence, not art acceptance.
const MAP_TEXTURE := preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-region_world-map-background_m8-concept_20261014-143410-5df78b23.png")
const MARKERS := {
	"scifi.city": Vector2(136, 174),
	"scifi.outskirts": Vector2(324, 230),
	"scifi.ruins": Vector2(510, 150),
}
var captures: Array[String] = []


func _initialize() -> void:
	call_deferred("_run")


func _settle() -> void:
	await process_frame
	await process_frame
	await process_frame


func _check(ok: bool, detail: String) -> bool:
	if not ok:
		push_error("WORLD_MAP_VISUAL_CHECK_FAILED: " + detail)
		quit(1)
	return ok


func _capture(variant: String) -> void:
	var directory := OS.get_environment("WB_MAP_EVIDENCE_DIR")
	if directory.is_empty() or DisplayServer.get_name() == "headless":
		return
	DirAccess.make_dir_recursive_absolute(directory)
	await RenderingServer.frame_post_draw
	var frame := root.get_texture().get_image()
	if not _check(frame.get_size() == Vector2i(640, 360), "capture logical viewport"):
		return
	var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	var filename := "rpg-2-star-ocean-the-second_scifi-world-map_in-engine-%s_m8-v01_%s-%08x.png" % [variant, stamp, randi()]
	if not _check(frame.save_png(directory.path_join(filename)) == OK, "save " + variant):
		return
	captures.append(filename)


func _run() -> void:
	SaveStore.root_path = "user://test-saves/m8-world-map-visual"
	if not _check(MAP_TEXTURE.get_size() == Vector2(1672, 941), "background imported at source resolution"):
		return
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	change_scene_to_file("res://scenes/scifi_world_map.tscn")
	await _settle()
	for id in MARKERS:
		var button: Button = current_scene.get("destination_buttons")[id]
		var marker: Vector2 = MARKERS[id]
		if not _check(button.position == marker + Vector2(-68, 29) and button.size == Vector2(136, 39), "button geometry " + id):
			return
		if not _check(not button.disabled and not button.text.is_empty(), "button readable and enabled " + id):
			return
	await _capture("chinese")
	app.toggle_language()
	await _settle()
	await _capture("english")
	for id in ["scifi.city", "scifi.outskirts", "scifi.ruins"]:
		var button: Button = current_scene.get("destination_buttons")[id]
		button.pressed.emit()
		await _settle()
		if not _check(app.current_destination_id == id and current_scene.scene_file_path == "res://scenes/scifi_exploration_area.tscn", "destination click " + id):
			return
		change_scene_to_file("res://scenes/scifi_world_map.tscn")
		await _settle()
	var directory := OS.get_environment("WB_MAP_EVIDENCE_DIR")
	if not directory.is_empty() and captures.size() == 2:
		var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
		var filename := "rpg-2-star-ocean-the-second_scifi-world-map_visual-check-manifest_m8-v01_%s-%08x.json" % [stamp, randi()]
		var record := {"status": "visual_prototype_unapproved", "captures": captures,
			"markers": {"scifi.city": [136, 174], "scifi.outskirts": [324, 230], "scifi.ruins": [510, 150]},
			"destination_buttons_tested": 3, "logical_viewport": [640, 360]}
		var file := FileAccess.open(directory.path_join(filename), FileAccess.WRITE)
		if _check(file != null, "open evidence manifest"):
			file.store_string(JSON.stringify(record, "\t") + "\n")
			file.close()
	print("WORLD_MAP_VISUAL_CHECK_OK captures=%d buttons=3" % captures.size())
	quit(0)
