extends SceneTree

# Map-status readability check for the global map (M2). The top-left status line
# ("Open: Science region · other regions not yet open", or the region name) must sit on
# its own dark panel, so coastlines and grid lines do not run through the text. For each
# view it renders the window twice, once normally and once with the map layers hidden,
# and requires the panel's pixels to stay within a small tint of each other. It also checks
# that the panel hugs one line of text, stays clear of the other map controls, and that
# no region-view degree or reference label sits under it.
# Needs a display renderer (do not pass --headless). From the repository root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game \
#     --script res://tests/rpg-2-star-ocean-the-second_global-map-status-backing_readability-check_m2-v01_20261015-041500-2d7e93b1.gd
# Set M2_STATUS_CAPTURE_DIR to write the 1280x720 captures somewhere other than outputs/.
# Captures are unapproved runtime evidence, not visual acceptance.

const OUT_DIR := "res://../outputs"
# Largest per-channel change the map may cause inside the panel (0.88 alpha backing).
const MAX_SHOW_THROUGH := 0.14
var stamp := ""
var run_id := ""
var out_dir := ""
var checks := 0
var failures: Array = []


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	stamp = Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	run_id = "%08x" % randi()
	out_dir = OS.get_environment("M2_STATUS_CAPTURE_DIR")
	if out_dir.is_empty():
		out_dir = ProjectSettings.globalize_path(OUT_DIR)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	SaveStore.root_path = "user://test-saves/m2-status-backing-readability"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.show_initial_guide = false
	app.language = "zh"
	change_scene_to_file("res://scenes/scifi_world_map.tscn")
	await _settle()
	var map: Node = current_scene

	_check(map.legend_backing != null and map.legend_label.get_parent() == map.legend_backing, "status label sits in its backing panel")
	var style: StyleBoxFlat = map.legend_backing.get_theme_stylebox("panel")
	_check(style.bg_color.a >= 0.85, "status backing is near-opaque (alpha %.2f)" % style.bg_color.a)
	var card_style: StyleBoxFlat = map.route_card.get_theme_stylebox("panel")
	_check(card_style.bg_color.a == 1.0, "route card stays opaque (alpha %.2f)" % card_style.bg_color.a)

	for language in ["zh", "en"]:
		app.language = language
		app.language_changed.emit()
		map.enter_global()
		await _check_view(map, "globe-%s" % language)
		map.zoom_view(Vector2(500, 90), 2.0)
		await _check_view(map, "globe-zoomed-%s" % language)
		map.enter_region("us_northeast")
		await _check_view(map, "region-%s" % language)
		map.select_place("earth.us.dc.washington-ruins")
		await _check_view(map, "region-card-%s" % language)
		map.close_route_card()
		map.zoom_view(Vector2(320, 134), 2.5)
		await _check_view(map, "region-zoomed-%s" % language)
		map.enter_global()
	app.language = "zh"

	if failures.is_empty():
		print("STATUS_BACKING_READABILITY_OK %d checks" % checks)
		quit(0)
	else:
		for failure in failures:
			push_error("FAILED: " + failure)
		print("STATUS_BACKING_READABILITY_FAILED %d of %d checks" % [failures.size(), checks])
		quit(1)


func _check_view(map: Node, label: String) -> void:
	await _settle()
	var backing: PanelContainer = map.legend_backing
	var text: Label = map.legend_label
	_check(backing.visible and not text.text.is_empty(), label + ": status visible with text")
	var panel: Rect2 = map.status_rect()
	_check(panel.is_equal_approx(Rect2(backing.position, backing.size)), "%s: panel laid out at its minimum size (%s vs %s)" % [label, panel, Rect2(backing.position, backing.size)])
	_check(panel.size.x <= map.STATUS_MAX_TEXT_WIDTH + 12.5, "%s: panel width %.1f within limit" % [label, panel.size.x])
	_check(panel.size.y <= 20.5, "%s: one line of text (panel height %.1f)" % [label, panel.size.y])
	var text_rect := Rect2(backing.position + text.position, text.size)
	_check(panel.encloses(text_rect), "%s: text inside its panel" % label)
	# Clear of the other controls inside the map frame (map-local pixels).
	var others := {
		"zoom in": map.zoom_in_button, "zoom out": map.zoom_out_button,
		"globe": map.globe_button, "region": map.region_button, "calendar": map.calendar_label}
	for key in others:
		var control: Control = others[key]
		_check(not panel.intersects(Rect2(control.position, control.size)), "%s: panel clear of %s" % [label, key])
	for buttons in [map.region_buttons, map.place_buttons]:
		for id in buttons:
			var button: Button = buttons[id]
			if button.visible:
				_check(not panel.intersects(Rect2(button.position, button.size)), "%s: panel clear of marker %s" % [label, id])
	var card_local := Rect2(map.CARD_RECT.position - map.MAP_RECT.position, map.CARD_RECT.size)
	_check(not panel.intersects(card_local), label + ": panel clear of the route card area")
	if map.mode == "region":
		var lon_count := 0
		for entry in map.annotation_label_rects():
			_check(not entry["rect"].intersects(panel), "%s: label %s clear of the status panel" % [label, entry["text"]])
			if entry["text"].ends_with("°E") or entry["text"].ends_with("°W"):
				lon_count += 1
		_check(lon_count > 0, "%s: longitude labels still drawn (%d)" % [label, lon_count])
	var with_map := await _grab()
	_save(with_map, label)
	var layers: Array = [map.underlay, map.global_layer, map.region_layer, map.overlay]
	var shown: Array = []
	for layer in layers:
		shown.append(layer.visible)
		layer.visible = false
	var without_map := await _grab()
	for i in layers.size():
		layers[i].visible = shown[i]
	var global_panel := Rect2(panel.position + map.MAP_RECT.position, panel.size)
	var worst := _max_difference(with_map, without_map, Rect2i(Vector2i(global_panel.position * 2.0), Vector2i(global_panel.size * 2.0)))
	_check(worst <= MAX_SHOW_THROUGH, "%s: map shows through the status panel (max channel change %.3f)" % [label, worst])


func _max_difference(a: Image, b: Image, rect: Rect2i) -> float:
	var worst := 0.0
	for y in range(rect.position.y, rect.end.y):
		for x in range(rect.position.x, rect.end.x):
			var p := a.get_pixel(x, y)
			var q := b.get_pixel(x, y)
			worst = maxf(worst, maxf(absf(p.r - q.r), maxf(absf(p.g - q.g), absf(p.b - q.b))))
	return worst


func _grab() -> Image:
	await _settle()
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	if image == null or image.get_size() != Vector2i(1280, 720):
		push_error("expected a rendered 1280x720 window (run without --headless)")
		quit(1)
	return image


func _save(image: Image, label: String) -> void:
	var path := out_dir.path_join("rpg-2-star-ocean-the-second_global-map-status_%s-readability-capture_m2-v01_%s-%s.png" % [label, stamp, run_id])
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
