extends SceneTree

# Exercises physical window-pixel clicks through Viewport.push_input(false),
# rather than emitting button signals directly. No production scene is changed.
const OUT_DIR := "res://../outputs"
var evidence: Array[String] = []
var run_stamp := ""
var run_id := ""
var city_physical := Vector2.ZERO
var depart_physical := Vector2.ZERO


func _initialize() -> void:
	call_deferred("_run")


func _fail(detail: String) -> void:
	push_error("CANVAS_POINTER_REGRESSION_FAILED: " + detail)
	quit(1)


func _settle() -> void:
	await process_frame
	await process_frame
	await process_frame


func _click_window_pixel(position: Vector2) -> void:
	var motion := InputEventMouseMotion.new()
	motion.position = position
	motion.global_position = position
	root.push_input(motion, false)
	var press := InputEventMouseButton.new()
	press.button_index = MOUSE_BUTTON_LEFT
	press.pressed = true
	press.position = position
	press.global_position = position
	root.push_input(press, false)
	var release := InputEventMouseButton.new()
	release.button_index = MOUSE_BUTTON_LEFT
	release.pressed = false
	release.position = position
	release.global_position = position
	root.push_input(release, false)
	await _settle()


# Canvas-items stretch at 2x: logical canvas pixels map to window pixels by a factor of two.
func _physical_center(control: Control) -> Vector2:
	return control.get_global_rect().get_center() * 2.0


func _enter_city_by_clicks() -> bool:
	var map: Node = current_scene
	await _click_window_pixel(_physical_center(map.get("destination_buttons")["scifi.city"]))
	if not map.get("route_card").visible:
		_fail("physical city-marker click did not open the route card")
		return false
	depart_physical = _physical_center(map.get("depart_button"))
	await _click_window_pixel(depart_physical)
	if current_scene.scene_file_path != "res://scenes/scifi_exploration_area.tscn" or root.get_node("AppState").current_destination_id != "scifi.city":
		_fail("physical route-card click did not enter the city")
		return false
	return true


func _key(keycode: Key, pressed: bool) -> void:
	var event := InputEventKey.new()
	event.physical_keycode = keycode
	event.pressed = pressed
	Input.parse_input_event(event)
	await process_frame


func _capture(label: String) -> void:
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	if image == null or image.get_size() != Vector2i(1280, 720):
		_fail("expected actual 1280x720 rendered viewport")
		return
	var path: String = ProjectSettings.globalize_path(OUT_DIR).path_join("rpg-2-star-ocean-the-second_scifi-canvas_ui-regression-%s_m8-v01_%s-%s.png" % [label, run_stamp, run_id])
	if image.save_png(path) != OK:
		_fail("capture " + label)
		return
	evidence.append(path)


func _check_map_header() -> bool:
	var map: Node2D = current_scene
	var help: Label = map.get("help_label")
	var save: Button = map.get("save_button")
	var right_edge := help.position.x + help.get_combined_minimum_size().x
	if right_edge > save.position.x - 8.0:
		_fail("map help overlaps Save: right=" + str(right_edge) + " save=" + str(save.position.x))
		return false
	return true


func _run() -> void:
	run_stamp = Time.get_datetime_string_from_system(true).replace("-", "").replace(":", "").replace("T", "-")
	run_id = "%08x" % randi()
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	SaveStore.root_path = "user://test-saves/m8-canvas-pointer-regression"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.show_initial_guide = false
	app.language = "zh"
	change_scene_to_file("res://scenes/scifi_world_map.tscn")
	await _settle()
	if root.size != Vector2i(1280, 720) or root.content_scale_size != Vector2i(640, 360):
		_fail("window and logical canvas size")
		return
	if not _check_map_header():
		return
	await _capture("map-zh")
	# The global map places buttons from real coordinates, so positions are read from the
	# scene: region marker -> Shanghai marker -> route card Depart/Enter, all as window pixels.
	var region_button: Button = current_scene.get("region_buttons")["yangtze_delta"]
	await _click_window_pixel(_physical_center(region_button))
	if current_scene.get("mode") != "region":
		_fail("physical region-marker click did not open the Yangtze Delta layer")
		return
	var city_button: Button = current_scene.get("destination_buttons")["scifi.city"]
	city_physical = _physical_center(city_button)
	# An unscaled click at the logical center must miss the marker.
	await _click_window_pixel(city_button.get_global_rect().get_center())
	if current_scene.scene_file_path != "res://scenes/scifi_world_map.tscn" or current_scene.get("route_card").visible:
		_fail("unscaled physical coordinate unexpectedly hit city marker")
		return
	if not await _enter_city_by_clicks():
		return
	var area: Node2D = current_scene
	await _capture("city-zh")
	var before: Vector2 = area.get("hero").position
	await _key(KEY_D, true)
	for frame in 12:
		await process_frame
	await _key(KEY_D, false)
	var after: Vector2 = area.get("hero").position
	if after.x <= before.x + 1.0:
		_fail("physical D key did not move hero: " + str(before) + " -> " + str(after))
		return
	area.get("hero").position = area.get("npc_position")
	await _key(KEY_E, true)
	await _key(KEY_E, false)
	if not area.get("dialogue_open"):
		_fail("E at city NPC hotspot did not open dialogue")
		return
	area._close_dialogue()
	# The city back button center is logical (574,31), physical (1148,62).
	await _click_window_pixel(Vector2(1148, 62))
	if current_scene.scene_file_path != "res://scenes/scifi_world_map.tscn":
		_fail("physical city back-button click did not return to map")
		return
	app.language = "en"
	current_scene._refresh_text()
	if not _check_map_header():
		return
	await _capture("map-en")
	if not await _enter_city_by_clicks():
		_fail("English city-marker click did not enter area")
		return
	await _capture("city-en")
	var receipt := {"mode": "canvas_items", "window": [1280, 720], "logical_canvas": [640, 360], "city_button_physical": [city_physical.x, city_physical.y], "depart_button_physical": [depart_physical.x, depart_physical.y], "city_back_physical": [1148, 62], "wasd_start": [before.x, before.y], "wasd_end": [after.x, after.y], "npc_interact": true, "captures": evidence, "human_playtest": false, "art_accepted": false}
	var path: String = ProjectSettings.globalize_path(OUT_DIR).path_join("rpg-2-star-ocean-the-second_scifi-canvas_pointer-regression-receipt_m8-v01_%s-%s.json" % [run_stamp, run_id])
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		_fail("open receipt")
		return
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()
	print("CANVAS_POINTER_REGRESSION_OK")
	quit(0)
