extends SceneTree

# Renders the global Earth map at the real 1280x720 window over the 640x360 canvas.
# Needs a display renderer (do not pass --headless). From the repository root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game \
#     --script res://tests/rpg-2-star-ocean-the-second_global-earth-map_visual-capture_m2-v01_20261015-024300-9b2fac94.gd
# Captures are unapproved runtime evidence, not visual acceptance.

const RouteAdapter := preload("res://scripts/world_map_route_adapter.gd")
const OUT_DIR := "res://../outputs"
const CHICAGO := "earth.us.il.chicago"
var stamp := ""
var run_id := ""
var captures: Array = []


# Stands in for an AppState without the route API, to capture the disabled-departure card.
class NoRouteApiProvider:
	extends RefCounted
	var current_destination_id := "scifi.city"


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	stamp = Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	run_id = "%08x" % randi()
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	SaveStore.root_path = "user://test-saves/m2-global-map-capture"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.show_initial_guide = false
	app.language = "zh"
	change_scene_to_file("res://scenes/scifi_world_map.tscn")
	await _settle()
	var map: Node = current_scene
	for language in ["zh", "en"]:
		app.language = language
		app.language_changed.emit()
		await _settle()
		map.enter_global()
		await _capture("globe-" + language)
		map.enter_region("us_northeast")
		await _capture("us-northeast-" + language)
		for place in [["earth.us.dc.washington-ruins", "washington"], ["earth.us.ny.yonkers-outskirts", "yonkers"], ["earth.us.ny.new-york-city", "new-york-here"]]:
			map.select_place(place[0])
			await _capture("us-northeast-%s-card-%s" % [place[1], language])
			map.close_route_card()
		var real_adapter = map.route_adapter
		map.route_adapter = RouteAdapter.new(NoRouteApiProvider.new())
		map.select_place("earth.us.dc.washington-ruins")
		await _capture("us-northeast-washington-no-route-api-card-" + language)
		map.close_route_card()
		map.route_adapter = real_adapter
	if not await _capture_chicago(app, map):
		quit(1)
		return
	app.language = "zh"
	print("GLOBAL_MAP_CAPTURE_OK %d" % captures.size())
	quit(0)


# Great Lakes from the New York start: the NYC-to-Chicago air card, then a real departure through
# the map (charged once by the route core) into the Loop and back to the map with Chicago as here.
func _capture_chicago(app: Node, map: Node) -> bool:
	if map.find_place(CHICAGO).is_empty():
		push_error("Chicago is not a map place in this run; no Great Lakes captures")
		return false
	var air_id := ""
	for language in ["zh", "en"]:
		app.language = language
		app.language_changed.emit()
		await _settle()
		map.enter_region("us_great_lakes")
		await _capture("us-great-lakes-" + language)
		map.select_place(CHICAGO)
		if map.route_state.get("status", "") != "ready":
			push_error("NYC-to-Chicago card status is %s, not ready" % map.route_state.get("status", ""))
			return false
		for option in map.route_state["options"]:
			if option["mode"] == "air":
				air_id = option["option_id"]
		if air_id.is_empty():
			push_error("no available air option from %s to Chicago" % map.route_adapter.current_place_id())
			return false
		map._choose_option(air_id)
		for option in map.route_state["options"]:
			print("ROUTE %s %s%s: %s" % [language, option["option_id"], " [selected]" if option["option_id"] == map.selected_option_id else "", map.route_option_text(option).replace("\n", " / ")])
		await _capture("us-great-lakes-chicago-air-route-card-" + language)
		map.close_route_card()
	print("BEFORE %s %s" % [map.route_adapter.current_place_id(), map.route_adapter.calendar_text()])
	map.select_place(CHICAGO)
	map._choose_option(air_id)
	map.depart()
	await _settle()
	if not current_scene.scene_file_path.ends_with("rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn"):
		push_error("depart did not enter the Loop scene: " + current_scene.scene_file_path)
		return false
	for language in ["zh", "en"]:
		app.language = language
		app.language_changed.emit()
		await _capture("chicago-loop-arrival-" + language)
	change_scene_to_file("res://scenes/scifi_world_map.tscn")
	await _settle()
	map = current_scene
	print("AFTER %s %s" % [map.route_adapter.current_place_id(), map.route_adapter.calendar_text()])
	if map.route_adapter.current_place_id() != CHICAGO:
		push_error("party is not at Chicago after departure")
		return false
	for language in ["zh", "en"]:
		app.language = language
		app.language_changed.emit()
		await _settle()
		map.enter_region("us_great_lakes")
		await _capture("us-great-lakes-chicago-here-" + language)
		map.select_place(CHICAGO)
		await _capture("us-great-lakes-chicago-here-card-" + language)
		map.close_route_card()
	return true


func _capture(label: String) -> void:
	await _settle()
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	if image == null or image.get_size() != Vector2i(1280, 720):
		push_error("expected a rendered 1280x720 window (run without --headless)")
		quit(1)
		return
	var path := ProjectSettings.globalize_path(OUT_DIR).path_join("rpg-2-star-ocean-the-second_global-earth-map_%s-runtime-capture_m2-v02_%s-%s.png" % [label, stamp, run_id])
	if image.save_png(path) != OK:
		push_error("capture failed: " + path)
		quit(1)
		return
	captures.append(path)
	print("CAPTURED " + path)


func _settle() -> void:
	for i in 3:
		await process_frame
