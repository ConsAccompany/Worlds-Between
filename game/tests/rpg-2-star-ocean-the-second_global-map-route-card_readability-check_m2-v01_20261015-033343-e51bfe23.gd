extends SceneTree

# Route card readability check for the global map (M2). The card must hide the map
# beneath it completely: no grid lines, degree labels, markers or coast may show through.
# For every card view it renders the window twice, once normally and once with the map
# frame hidden, and requires the card's pixels to be identical. It also checks that the
# degree labels stay clear of the card and that open cards keep every latitude label.
# Needs a display renderer (do not pass --headless). From the repository root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game \
#     --script res://tests/rpg-2-star-ocean-the-second_global-map-route-card_readability-check_m2-v01_20261015-033343-e51bfe23.gd
# Set M2_CARD_CAPTURE_DIR to write the 1280x720 card captures somewhere other than outputs/.
# Captures are unapproved runtime evidence, not visual acceptance.

const RouteAdapter := preload("res://scripts/world_map_route_adapter.gd")
const OUT_DIR := "res://../outputs"
var stamp := ""
var run_id := ""
var out_dir := ""
var checks := 0
var failures: Array = []


# Stands in for an AppState without the route API, to check the disabled-departure card.
class NoRouteApiProvider:
	extends RefCounted
	var current_destination_id := "scifi.city"


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	stamp = Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	run_id = "%08x" % randi()
	out_dir = OS.get_environment("M2_CARD_CAPTURE_DIR")
	if out_dir.is_empty():
		out_dir = ProjectSettings.globalize_path(OUT_DIR)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	SaveStore.root_path = "user://test-saves/m2-route-card-readability"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.show_initial_guide = false
	app.language = "zh"
	change_scene_to_file("res://scenes/scifi_world_map.tscn")
	await _settle()
	var map: Node = current_scene

	var style: StyleBoxFlat = map.route_card.get_theme_stylebox("panel")
	_check(style.bg_color.a == 1.0, "route card background is opaque (alpha %.2f)" % style.bg_color.a)

	for language in ["zh", "en"]:
		app.language = language
		app.language_changed.emit()
		await _settle()
		map.enter_region("us_northeast")
		for place in [["earth.us.dc.washington-ruins", "washington"], ["earth.us.ny.yonkers-outskirts", "yonkers"], ["earth.us.ny.new-york-city", "new-york-here"]]:
			map.select_place(place[0])
			await _check_card(map, "%s-%s" % [place[1], language])
			map.close_route_card()
		# Zoomed in, more degree lines cross the card.
		map.zoom_view(Vector2(320, 134), 1.5)
		map.select_place("earth.us.dc.washington-ruins")
		await _check_card(map, "washington-zoomed-%s" % language)
		map.close_route_card()
		map.enter_region("us_northeast")
		var real_adapter = map.route_adapter
		map.route_adapter = RouteAdapter.new(NoRouteApiProvider.new())
		map.select_place("earth.us.dc.washington-ruins")
		await _check_card(map, "washington-no-route-api-%s" % language)
		map.close_route_card()
		map.route_adapter = real_adapter
		await _settle()
		_check(_lat_label_count(map) > 0, "%s: latitude labels drawn with the card closed" % language)
	app.language = "zh"

	if failures.is_empty():
		print("ROUTE_CARD_READABILITY_OK %d checks" % checks)
		quit(0)
	else:
		for failure in failures:
			push_error("FAILED: " + failure)
		print("ROUTE_CARD_READABILITY_FAILED %d of %d checks" % [failures.size(), checks])
		quit(1)


func _check_card(map: Node, label: String) -> void:
	await _settle()
	_check(map.route_card.visible, label + ": card visible")
	var card: Rect2 = map.route_card.get_global_rect()
	_check(card.size.y <= map.CARD_RECT.size.y + 0.5, label + ": card height stays %d px (got %.1f)" % [map.CARD_RECT.size.y, card.size.y])
	var card_local := Rect2(card.position - map.MAP_RECT.position, card.size)
	var labels: Array = _label_rects(map)
	var lat_seen := 0
	for entry in labels:
		_check(not entry["rect"].intersects(card_local), "%s: label %s clear of the card" % [label, entry["text"]])
		if entry["text"].ends_with("°N"):
			lat_seen += 1
	var with_map := await _grab()
	_save(with_map, label)
	map.map_frame.visible = false
	var without_map := await _grab()
	map.map_frame.visible = true
	var differing := _differing_pixels(with_map, without_map, Rect2i(Vector2i(card.position * 2.0), Vector2i(card.size * 2.0)))
	_check(differing == 0, label + ": map shows through the card in %d pixels" % differing)
	# The card moves latitude labels beside it; it must not drop any. Hiding the card
	# drops button focus, so this runs after the captures.
	map.route_card.visible = false
	var lat_closed := _lat_label_count(map)
	map.route_card.visible = true
	_check(lat_seen == lat_closed, label + ": latitude labels kept beside the card (%d of %d)" % [lat_seen, lat_closed])


func _lat_label_count(map: Node) -> int:
	var count := 0
	for entry in _label_rects(map):
		if entry["text"].ends_with("°N"):
			count += 1
	return count


func _label_rects(map: Node) -> Array:
	if not map.has_method("annotation_label_rects"):
		_check(false, "map exposes annotation_label_rects()")
		return []
	return map.annotation_label_rects()


func _differing_pixels(a: Image, b: Image, rect: Rect2i) -> int:
	var count := 0
	for y in range(rect.position.y, rect.end.y):
		for x in range(rect.position.x, rect.end.x):
			if a.get_pixel(x, y) != b.get_pixel(x, y):
				count += 1
	return count


func _grab() -> Image:
	await _settle()
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	if image == null or image.get_size() != Vector2i(1280, 720):
		push_error("expected a rendered 1280x720 window (run without --headless)")
		quit(1)
	return image


func _save(image: Image, label: String) -> void:
	var path := out_dir.path_join("rpg-2-star-ocean-the-second_global-map-route-card_%s-readability-capture_m2-v01_%s-%s.png" % [label, stamp, run_id])
	if image.save_png(path) != OK:
		_check(false, "capture saved: " + path)
		return
	print("CAPTURED " + path)


func _check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures.append(message)


func _settle() -> void:
	for i in 3:
		await process_frame
