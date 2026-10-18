extends SceneTree

# Targeted map composition and destination-button regression check.
# The screenshots are visual evidence, not art acceptance.
#
# M8 (b1aff00) pinned a fixed three-point background: buttons at marker + (-68, 29), 136x39, whose click entered the
# area scene. Since 09d3689 this scene is the global Earth map (that QA note records the old geometry as superseded),
# so those expectations failed by design ("button geometry scifi.city"). Updated 2026-10-17 (map v03r1, art
# UNAPPROVED) to the current contract for the same three destination IDs: each is a place label plate in its region
# view, on its travel-data coordinates, readable, enabled, inside the frame and clear of the fixed controls and the
# other places' click targets; a click opens that place's route card and never leaves the map or charges time
# (departure only goes through Depart / confirm_travel, covered by the travel regressions).
const MAP_TEXTURE := preload("res://assets/environments/rpg-2-star-ocean-the-second_scifi-region_world-map-background_m8-concept_20261014-143410-5df78b23.png")
const DESTINATIONS := ["scifi.city", "scifi.outskirts", "scifi.ruins"]
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
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


# The place behind a destination button (several places may share a scene destination; the map keeps the last).
func _place_id_for(map: Node, button: Button) -> String:
	for place_id in map.place_buttons:
		if map.place_buttons[place_id] == button:
			return place_id
	return ""


func _check_button(map: Node, id: String) -> bool:
	var button: Button = map.get("destination_buttons").get(id)
	if not _check(button != null, "destination button exists " + id):
		return false
	var place_id := _place_id_for(map, button)
	var place: Dictionary = map.find_place(place_id)
	if not _check(not place.is_empty(), "destination button is a place marker " + id):
		return false
	map.enter_region(place["geo_region_id"])
	await _settle()
	var marker: Vector2 = map.marker_position(place_id)
	var plate_node: Control = button.get_node("LabelBackground")
	var plate := Rect2(button.position + plate_node.position, plate_node.size)
	var text := (button.get_node("Primary") as Label).text
	if not _check(marker.is_equal_approx(map.view.geo_to_screen(place["lon"], place["lat"])), "marker on travel-data coordinates " + id):
		return false
	if not _check(Rect2(button.position, button.size).has_point(marker), "button geometry %s covers its marker" % id):
		return false
	if not _check(Rect2(Vector2.ZERO, map.view.viewport.size).encloses(plate), "button geometry %s label inside the map frame" % id):
		return false
	for fixed in map.fixed_ui_rects():
		if not _check(not plate.intersects(fixed), "button geometry %s label clear of fixed control %s" % [id, fixed]):
			return false
	for other_id in map.place_buttons:
		var other: Button = map.place_buttons[other_id]
		if other != button and other.visible and not _check(not Rect2(button.position, button.size).intersects(Rect2(other.position, other.size)), "button geometry %s clear of %s" % [id, other_id]):
			return false
	return _check(button.visible and not button.disabled and not text.is_empty(), "button readable and enabled " + id)


func _run() -> void:
	# Native 640x360 window, as the map capture tools use (the project window is larger since M8).
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(640, 360)
	SaveStore.root_path = "user://test-saves/m8-world-map-visual"
	if not _check(MAP_TEXTURE.get_size() == Vector2(1672, 941), "background imported at source resolution"):
		return
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.show_initial_guide = false
	change_scene_to_file(MAP_SCENE)
	await _settle()
	await _settle()
	var map: Node = current_scene
	for variant in ["chinese", "english"]:
		for id in DESTINATIONS:
			if not await _check_button(map, id):
				return
		map.enter_region(map.find_place(_place_id_for(map, map.get("destination_buttons")[DESTINATIONS[0]]))["geo_region_id"])
		await _settle()
		await _capture(variant)
		app.toggle_language()
		await _settle()
	var start_minutes: int = app.calendar_minutes
	var start_destination: String = app.current_destination_id
	for id in DESTINATIONS:
		var button: Button = map.get("destination_buttons")[id]
		var place_id := _place_id_for(map, button)
		map.enter_region(map.find_place(place_id)["geo_region_id"])
		await _settle()
		button.pressed.emit()
		await _settle()
		if not _check(map.route_card.visible and map.selected_place_id == place_id, "destination click opens the route card " + id):
			return
		if not _check(current_scene == map and map.scene_file_path == MAP_SCENE and app.current_destination_id == start_destination and app.calendar_minutes == start_minutes, "destination click stays on the map and charges nothing " + id):
			return
		map.close_route_card()
		await _settle()
	var directory := OS.get_environment("WB_MAP_EVIDENCE_DIR")
	if not directory.is_empty() and captures.size() == 2:
		var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
		var filename := "rpg-2-star-ocean-the-second_scifi-world-map_visual-check-manifest_m8-v01_%s-%08x.json" % [stamp, randi()]
		var record := {"status": "visual_prototype_unapproved", "captures": captures, "map": "global Earth map (since 09d3689)",
			"destinations": DESTINATIONS, "destination_buttons_tested": DESTINATIONS.size(), "logical_viewport": [640, 360]}
		var file := FileAccess.open(directory.path_join(filename), FileAccess.WRITE)
		if _check(file != null, "open evidence manifest"):
			file.store_string(JSON.stringify(record, "\t") + "\n")
			file.close()
	print("WORLD_MAP_VISUAL_CHECK_OK captures=%d buttons=%d" % [captures.size(), DESTINATIONS.size()])
	quit(0)
