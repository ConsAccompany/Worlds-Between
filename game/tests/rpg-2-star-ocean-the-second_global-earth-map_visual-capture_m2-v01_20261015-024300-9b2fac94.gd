extends SceneTree

# Renders the global Earth map at the real 1280x720 window over the 640x360 canvas.
# Needs a display renderer (do not pass --headless). From the repository root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game \
#     --script res://tests/rpg-2-star-ocean-the-second_global-earth-map_visual-capture_m2-v01_20261015-024300-9b2fac94.gd
# Captures are unapproved runtime evidence, not visual acceptance.

const RouteAdapter := preload("res://scripts/world_map_route_adapter.gd")
const OUT_DIR := "res://../outputs"
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
		map.enter_region("yangtze_delta")
		await _capture("yangtze-delta-" + language)
		for place in [["earth.cn.liangzhu-ruins", "liangzhu"], ["earth.cn.shanghai.songjiang-outskirts", "songjiang"], ["earth.cn.shanghai", "shanghai-here"]]:
			map.select_place(place[0])
			await _capture("yangtze-delta-%s-card-%s" % [place[1], language])
			map.close_route_card()
		var real_adapter = map.route_adapter
		map.route_adapter = RouteAdapter.new(NoRouteApiProvider.new())
		map.select_place("earth.cn.liangzhu-ruins")
		await _capture("yangtze-delta-liangzhu-no-route-api-card-" + language)
		map.close_route_card()
		map.route_adapter = real_adapter
	app.language = "zh"
	print("GLOBAL_MAP_CAPTURE_OK %d" % captures.size())
	quit(0)


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
