extends SceneTree

# TEST-ONLY visual candidate: a two-endpoint NYC -> Chicago air-route inset on the Great Lakes
# route-card view. Answers the 2026-10-16 corridor audit (…nyc-chicago-air-corridor_visual-audit…bb294d29.md):
# with Chicago selected, New York is off-screen and nothing on the map shows the trip's direction.
#
# Nothing in game/ is edited. The inset is a Control added at run time to the live map's MapFrame;
# it reads place coordinates, labels and the selected air option from the running map / route core
# and reuses existing MapText strings only. Needs a display renderer (no --headless). From the repo root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game \
#     -s <absolute path to this file> -- [variant]
# variant "v01" (default) or "v01r1", the single revision after the v01 visual review: label backing
# plates in the map-marker style, plus the inset's own scale bar, so the main map's 100 km bar below is not
# read as the inset's scale.
# Captures are unapproved test evidence, not map-art acceptance. M2 stays open.

const GeoProjection := preload("res://scripts/world_geo_projection.gd")
const MapData := preload("res://scripts/world_map_data.gd")
# world_map_text.gd (MapText) names the AppState autoload, so AirInset loads it at run time; a preload
# here compiles it before autoloads exist and breaks MapText.t for the live map as well.
const NYC := "earth.us.ny.new-york-city"
const CHICAGO := "earth.us.il.chicago"
const TAG := "test-only-v01_20261016-065443-adea3798"
const OUT_DIR := "res://../outputs"

var variant := "v01"
var checks := 0
var failures: Array = []
var report := {"tag": TAG, "checks": [], "captures": [], "failures": []}
var calendar_events := 0
var travel_events := 0


# --- The inset ------------------------------------------------------------------

class AirInset:
	extends Control

	const COLOR_BG := Color(0.04, 0.08, 0.12, 0.92)
	const COLOR_BORDER := Color("#79cfc0")
	const COLOR_OCEAN := Color("#123544")
	const COLOR_LAND := Color("#566f58")
	const COLOR_COAST := Color("#a9c6a4")
	const COLOR_AIR := Color("#e8f6ff")
	const COLOR_AIR_EDGE := Color(0.03, 0.07, 0.1, 0.9)
	const COLOR_MARKER := Color("#79cfc0")
	const COLOR_MARKER_EDGE := Color("#0b1c24")
	const COLOR_HERE := Color("#f0d68a")
	const COLOR_TEXT := Color("#f2f7f2")
	const COLOR_SUBTEXT := Color("#a9c7c4")
	const DASH := 4.0
	const GAP := 3.0

	var map: Node
	var area := Rect2()
	var caption_height := 14.0
	var projection: GeoProjection
	var clip: Control
	var lines: Node2D
	var arc := PackedVector2Array()
	var origin_pt := Vector2.ZERO
	var dest_pt := Vector2.ZERO
	var plane_pt := Vector2.ZERO
	var plane_dir := Vector2.LEFT
	var origin_label: Label
	var dest_label: Label
	var caption: Label
	var origin_side := "below"
	var dest_side := "above"
	var coasts: Array = []
	var revised := false
	var scale_km := 0.0
	var scale_px := 0.0
	var scale_text_rect := Rect2()

	func setup(live_map: Node, rect: Rect2, sides: Array, revision: bool) -> void:
		map = live_map
		revised = revision
		name = "AirRouteInsetTestOnly"
		position = rect.position
		size = rect.size
		mouse_filter = Control.MOUSE_FILTER_IGNORE
		dest_side = sides[0]
		origin_side = sides[1]
		area = Rect2(Vector2(1, 1), Vector2(size.x - 2, size.y - caption_height - 2))
		clip = Control.new()
		clip.position = area.position
		clip.size = area.size
		clip.clip_contents = true
		clip.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(clip)
		var o: Dictionary = map.find_place(NYC_ID)
		var d: Dictionary = map.find_place(CHICAGO_ID)
		var key := MapData.geodata_key("us_great_lakes")
		var mid_lat := (float(o["lat"]) + float(d["lat"])) * 0.5
		var mid_lon := (float(o["lon"]) + float(d["lon"])) * 0.5
		projection = GeoProjection.new(mid_lon, mid_lat)
		projection.configure(Rect2(Vector2.ZERO, area.size), projection.project_bbox(MapData.region_clip_bbox(key)), true, 60.0)
		# Both endpoints fitted with room for one label row above and below the corridor.
		var pad_lon := 1.7
		var frame := [minf(o["lon"], d["lon"]) - pad_lon, minf(o["lat"], d["lat"]) - 1.3, maxf(o["lon"], d["lon"]) + pad_lon, maxf(o["lat"], d["lat"]) + 1.3]
		projection.frame_geo_box(frame, Rect2(Vector2.ZERO, area.size))
		var land := Node2D.new()
		clip.add_child(land)
		var ocean := ColorRect.new()
		ocean.color = COLOR_OCEAN
		ocean.size = area.size
		ocean.mouse_filter = Control.MOUSE_FILTER_IGNORE
		land.add_child(ocean)
		var rings := MapData.region_land_rings(key)
		for hole_pass in [false, true]:
			for ring in rings:
				if ring["hole"] != hole_pass:
					continue
				var poly := Polygon2D.new()
				var pts := PackedVector2Array()
				for p in ring["points"]:
					pts.append(projection.geo_to_screen(p.x, p.y))
				poly.polygon = pts
				poly.color = COLOR_OCEAN if hole_pass else COLOR_LAND
				land.add_child(poly)
				var closed := pts.duplicate()
				closed.append(pts[0])
				coasts.append(closed)
		lines = Node2D.new()
		lines.draw.connect(_draw_lines)
		clip.add_child(lines)
		origin_pt = projection.geo_to_screen(o["lon"], o["lat"])
		dest_pt = projection.geo_to_screen(d["lon"], d["lat"])
		arc = great_circle_points(o["lon"], o["lat"], d["lon"], d["lat"], 48, projection)
		var half := arc.size() / 2
		plane_pt = arc[half]
		plane_dir = (arc[half + 1] - arc[half - 1]).normalized()
		origin_label = _label(10, COLOR_TEXT)
		dest_label = _label(10, COLOR_TEXT)
		caption = _label(9, COLOR_SUBTEXT)
		caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT if revised else HORIZONTAL_ALIGNMENT_CENTER
		if revised:
			for label in [origin_label, dest_label]:
				var plate := StyleBoxFlat.new()
				plate.bg_color = Color(0.04, 0.08, 0.12, 0.88)
				plate.content_margin_left = 3
				plate.content_margin_right = 3
				plate.content_margin_top = 0
				plate.content_margin_bottom = 0
				label.add_theme_stylebox_override("normal", plate)
			# Inset scale bar: the longest of these that fits in 48 px.
			var km_per_px := projection.km_per_pixel()
			for candidate in [50.0, 100.0, 200.0, 250.0, 500.0]:
				if candidate / km_per_px <= 48.0:
					scale_km = candidate
			scale_px = scale_km / km_per_px
		refresh_text()

	const NYC_ID := "earth.us.ny.new-york-city"
	const CHICAGO_ID := "earth.us.il.chicago"

	func _label(font_size: int, color: Color) -> Label:
		var label := Label.new()
		label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		label.add_theme_font_size_override("font_size", font_size)
		label.add_theme_color_override("font_color", color)
		label.add_theme_color_override("font_outline_color", Color("#0a121b"))
		label.add_theme_constant_override("outline_size", 3)
		add_child(label)
		return label

	# Labels, caption and positions for the current language; the figures come from the selected option.
	func refresh_text() -> void:
		var language: String = get_node("/root/AppState").language
		origin_label.text = MapData.text(map.find_place(NYC_ID), "map_label", language)
		dest_label.text = MapData.text(map.find_place(CHICAGO_ID), "map_label", language)
		var option := selected_option()
		var km := float(option.get("air_distance_km", -1.0))
		var map_text: GDScript = load("res://scripts/world_map_text.gd")
		caption.text = map_text.t("mode_" + String(option.get("mode", "air"))) + (" · " + map_text.t("air_km") % ("%.1f" % km) if km > 0.0 else "")
		for label in [origin_label, dest_label, caption]:
			label.reset_size()
		origin_label.position = _label_pos(origin_pt, origin_side, origin_label.size)
		dest_label.position = _label_pos(dest_pt, dest_side, dest_label.size)
		caption.position = Vector2(0, size.y - caption_height - 2)
		caption.size = Vector2(size.x - (6.0 if revised else 0.0), caption_height)
		queue_redraw()
		lines.queue_redraw()

	func _label_pos(at: Vector2, side: String, s: Vector2) -> Vector2:
		var p := area.position + at
		var out: Vector2
		match side:
			"above":
				out = p + Vector2(-s.x * 0.5, -6.0 - s.y)
			"below":
				out = p + Vector2(-s.x * 0.5, 4.0)
			"left":
				out = p + Vector2(-8.0 - s.x, -s.y * 0.5)
			_:
				out = p + Vector2(8.0, -s.y * 0.5)
		# Keep the label inside the map area; it slides along its edge rather than flipping.
		out.x = clampf(out.x, area.position.x + 1.0, area.end.x - s.x - 1.0)
		out.y = clampf(out.y, area.position.y, area.end.y - s.y)
		return out

	func selected_option() -> Dictionary:
		for option in map.route_state.get("options", []):
			if option["option_id"] == map.selected_option_id:
				return option
		return {}

	# Shown only while the NYC -> Chicago card offers a selected air option.
	func sync() -> void:
		var option := selected_option()
		var wanted: bool = map.route_card.visible and map.mode == "region" and map.active_region_id == "us_great_lakes" \
			and String(map.route_state.get("status", "")) == "ready" and map.selected_place_id == CHICAGO_ID \
			and map.route_adapter.current_place_id() == NYC_ID and ["air", "air_car"].has(String(option.get("mode", "")))
		if wanted != visible:
			visible = wanted
		if wanted:
			refresh_text()

	func _draw() -> void:
		draw_rect(Rect2(Vector2.ZERO, size), COLOR_BG)
		draw_rect(Rect2(Vector2(0.5, 0.5), size - Vector2.ONE), COLOR_BORDER, false, 1.0)
		draw_line(Vector2(1, area.end.y + 0.5), Vector2(size.x - 1, area.end.y + 0.5), Color(0.15, 0.25, 0.29), 1.0)
		if revised and scale_px > 0.0:
			var y := size.y - caption_height * 0.5 - 1.0
			var x0 := 6.0
			draw_line(Vector2(x0, y), Vector2(x0 + scale_px, y), COLOR_TEXT, 1.0)
			draw_line(Vector2(x0, y - 3), Vector2(x0, y + 1), COLOR_TEXT, 1.0)
			draw_line(Vector2(x0 + scale_px, y - 3), Vector2(x0 + scale_px, y + 1), COLOR_TEXT, 1.0)
			var font := get_theme_default_font()
			var text := "%d km" % int(scale_km)
			var at := Vector2(x0 + scale_px + 4.0, y + font.get_ascent(9) * 0.5 - 1.0)
			draw_string(font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, 9, COLOR_SUBTEXT)
			scale_text_rect = Rect2(Vector2(x0, y - 4), Vector2(scale_px + 4.0 + font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 9).x, 8))

	func _draw_lines() -> void:
		for ring in coasts:
			lines.draw_polyline(ring, COLOR_COAST, 1.0)
		for dash in dashes(arc):
			lines.draw_line(dash[0], dash[1], COLOR_AIR_EDGE, 3.0)
		for dash in dashes(arc):
			lines.draw_line(dash[0], dash[1], COLOR_AIR, 1.5)
		# Plane glyph at mid-route, nose toward the destination.
		var f := plane_dir * 5.0
		var s := Vector2(-plane_dir.y, plane_dir.x)
		var body := PackedVector2Array([plane_pt + f, plane_pt - f * 0.7 + s * 3.6, plane_pt - f * 0.35, plane_pt - f * 0.7 - s * 3.6])
		lines.draw_colored_polygon(body, COLOR_AIR_EDGE)
		var inner := PackedVector2Array()
		for p in body:
			inner.append(plane_pt + (p - plane_pt) * 0.72)
		lines.draw_colored_polygon(inner, COLOR_AIR)
		# Origin: party-here ring; destination: selected ring. Same language as the map markers.
		lines.draw_circle(origin_pt, 4.0, COLOR_MARKER_EDGE)
		lines.draw_circle(origin_pt, 2.8, COLOR_MARKER)
		lines.draw_arc(origin_pt, 5.6, 0.0, TAU, 20, COLOR_HERE, 1.5)
		lines.draw_circle(dest_pt, 4.0, COLOR_MARKER_EDGE)
		lines.draw_circle(dest_pt, 2.8, COLOR_MARKER)
		lines.draw_arc(dest_pt, 5.6, 0.0, TAU, 20, Color.WHITE, 1.2)

	# Dash segments along a polyline: DASH on, GAP off, measured along the path.
	static func dashes(points: PackedVector2Array) -> Array:
		var out := []
		var on := true
		var left := DASH
		for i in points.size() - 1:
			var a := points[i]
			var b := points[i + 1]
			var length := a.distance_to(b)
			var t := 0.0
			while t < length - 0.001:
				var step := minf(left, length - t)
				var p0 := a.lerp(b, t / length)
				var p1 := a.lerp(b, (t + step) / length)
				if on:
					out.append([p0, p1])
				t += step
				left -= step
				if left <= 0.001:
					on = not on
					left = DASH if on else GAP
		return out

	# True great-circle path (slerp on the unit sphere), projected into the inset.
	static func great_circle_points(lon_a: float, lat_a: float, lon_b: float, lat_b: float, n: int, proj: GeoProjection) -> PackedVector2Array:
		var a := _unit(lon_a, lat_a)
		var b := _unit(lon_b, lat_b)
		var omega := acos(clampf(a.dot(b), -1.0, 1.0))
		var out := PackedVector2Array()
		for i in n + 1:
			var t := float(i) / n
			var v := (a * sin((1.0 - t) * omega) + b * sin(t * omega)) / sin(omega)
			var lat := rad_to_deg(asin(v.z))
			var lon := rad_to_deg(atan2(v.y, v.x))
			out.append(proj.geo_to_screen(lon, lat))
		return out

	static func _unit(lon: float, lat: float) -> Vector3:
		var p := deg_to_rad(lat)
		var l := deg_to_rad(lon)
		return Vector3(cos(p) * cos(l), cos(p) * sin(l), sin(p))


# --- Run ---------------------------------------------------------------------------

func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if not args.is_empty():
		variant = String(args[0])
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = Vector2i(640, 360)
	root.size = Vector2i(1280, 720)
	SaveStore.root_path = "user://test-saves/m2-air-corridor-inset-test-only"
	var app: Node = root.get_node("AppState")
	app.begin_new_run()
	app.show_initial_guide = false
	app.language = "zh"
	app.calendar_advanced.connect(func(_a, _b, _c): calendar_events += 1)
	app.travel_completed.connect(func(_r): travel_events += 1)
	change_scene_to_file("res://scenes/scifi_world_map.tscn")
	await _settle()
	var map: Node = current_scene
	var start_minutes: int = app.calendar_minutes
	var start_place: String = app.current_location_id
	_check(start_place == NYC, "start place is New York City (%s)" % start_place)

	# v01: inset left of the card, under the Chicago label, above the scale bar. Labels: Chicago above, NYC below.
	# v01r1 keeps the rect and label sides; it adds label plates and the inset scale bar.
	var inset_local := Rect2(200, 150, 190, 94)
	var sides := ["above", "below"]
	map.enter_region("us_great_lakes")
	map.select_place(CHICAGO)
	await _settle()
	_choose_air(map)
	var inset := AirInset.new()
	map.map_frame.add_child(inset)
	inset.setup(map, inset_local, sides, variant == "v01r1")
	process_frame.connect(inset.sync)
	await _settle()

	_check_route(app, map, inset)
	_check_path(map, inset)
	for language in ["zh", "en"]:
		app.language = language
		app.language_changed.emit()
		await _settle()
		_check_collisions(map, inset, language)
	await _check_clicks(app, map, inset)

	for res in [Vector2i(1280, 720), Vector2i(640, 360)]:
		root.size = res
		await _settle()
		await _settle()
		for language in ["zh", "en"]:
			app.language = language
			app.language_changed.emit()
			await _settle()
			if not map.route_card.visible:
				map.enter_region("us_great_lakes")
				map.select_place(CHICAGO)
			_choose_air(map)
			await _settle()
			_check(inset.visible, "inset visible on the air card (%s %dx%d)" % [language, res.x, res.y])
			var image := await _capture(res, "%s-%dx%d" % [language, res.x, res.y])
			if image != null:
				_check_pixels(image, res, inset, language)
			inset.visible = false
			process_frame.disconnect(inset.sync)
			await _settle()
			await _capture(res, "baseline-no-inset-%s-%dx%d" % [language, res.x, res.y])
			process_frame.connect(inset.sync)
			await _settle()

	map.close_route_card()
	await _settle()
	_check(not inset.visible, "inset hides when the card closes")
	_check(app.calendar_minutes == start_minutes, "calendar unchanged %d == %d" % [app.calendar_minutes, start_minutes])
	_check(app.current_location_id == start_place, "party still at %s" % app.current_location_id)
	_check(calendar_events == 0 and travel_events == 0, "no calendar_advanced / travel_completed signals (%d, %d)" % [calendar_events, travel_events])
	_check(app.travel_preview.is_empty(), "no pending travel preview after close")
	report["failures"] = failures
	report["checks_total"] = checks
	report["variant"] = variant
	var report_path := ProjectSettings.globalize_path(OUT_DIR).path_join("rpg-2-star-ocean-the-second_global-map_nyc-chicago-air-inset_checks-%s_%s.json" % [variant, TAG])
	var file := FileAccess.open(report_path, FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	print("REPORT " + report_path)
	app.language = "zh"
	if failures.is_empty():
		print("AIR_INSET_OK %s %d checks, %d captures" % [variant, checks, report["captures"].size()])
		quit(0)
	else:
		print("AIR_INSET_FAIL %s %d/%d failed" % [variant, failures.size(), checks])
		for f in failures:
			print("  FAIL " + f)
		quit(1)


func _choose_air(map: Node) -> void:
	for option in map.route_state.get("options", []):
		if option["mode"] == "air":
			map._choose_option(option["option_id"])
			return


func _check(ok: bool, what: String) -> void:
	checks += 1
	report["checks"].append({"ok": ok, "check": what})
	print(("PASS " if ok else "FAIL ") + what)
	if not ok:
		failures.append(what)


# Route state: the card the inset illustrates is the core's NYC -> Chicago air option.
func _check_route(app: Node, map: Node, inset: AirInset) -> void:
	_check(String(map.route_state.get("status", "")) == "ready", "route state ready")
	_check(map.route_adapter.current_place_id() == NYC and map.selected_place_id == CHICAGO, "route NYC -> Chicago")
	var option := inset.selected_option()
	_check(String(option.get("mode", "")) == "air", "selected option is air (%s)" % option.get("option_id", "?"))
	var km := float(option.get("air_distance_km", -1.0))
	var o: Dictionary = map.find_place(NYC)
	var d: Dictionary = map.find_place(CHICAGO)
	var gc := GeoProjection.great_circle_km(o["lon"], o["lat"], d["lon"], d["lat"])
	report["air_distance_km"] = km
	report["great_circle_km_from_coords"] = snappedf(gc, 0.1)
	report["duration_text"] = String(option.get("duration_text", ""))
	_check(km > 0.0, "air distance from route core %.1f km" % km)
	_check(km >= gc - 0.5 and km < gc * 1.25, "core air km %.1f is within [great circle %.1f, +25%%]" % [km, gc])
	_check(inset.caption.text.contains("%.1f" % km), "caption uses the core figure: '%s'" % inset.caption.text)
	_check(inset.visible, "inset visible while the air card is open")


# Path: endpoints sit on the projected coordinates, the arc stays inside the inset and runs west.
func _check_path(map: Node, inset: AirInset) -> void:
	var o: Dictionary = map.find_place(NYC)
	var d: Dictionary = map.find_place(CHICAGO)
	var arc := inset.arc
	_check(arc[0].distance_to(inset.projection.geo_to_screen(o["lon"], o["lat"])) < 0.01, "arc starts at NYC coordinates")
	_check(arc[arc.size() - 1].distance_to(inset.projection.geo_to_screen(d["lon"], d["lat"])) < 0.01, "arc ends at Chicago coordinates")
	var inside := true
	var monotonic := true
	var max_dev := 0.0
	for i in arc.size():
		inside = inside and Rect2(Vector2.ZERO, inset.area.size).grow(-6).has_point(arc[i])
		if i > 0:
			monotonic = monotonic and arc[i].x < arc[i - 1].x
		max_dev = maxf(max_dev, _dist_to_segment(arc[i], arc[0], arc[arc.size() - 1]))
	_check(inside, "arc stays >= 6 px inside the inset map area")
	_check(monotonic, "arc runs monotonically west (origin east, destination west)")
	_check(inset.plane_dir.x < 0.0, "plane glyph points west toward Chicago")
	var chord := arc[0].distance_to(arc[arc.size() - 1])
	report["inset_chord_px"] = snappedf(chord, 0.1)
	report["arc_bulge_px"] = snappedf(max_dev, 0.01)
	report["inset_km_per_px"] = snappedf(inset.projection.km_per_pixel(), 0.01)
	_check(chord >= 100.0, "endpoints at least 100 canvas px apart (%.1f)" % chord)
	# Northward bulge of the true great circle (y up is negative).
	_check(arc[arc.size() / 2].y < (arc[0].y + arc[arc.size() - 1].y) * 0.5, "great-circle bows north of the chord (%.2f px)" % max_dev)
	_check(not inset.dashes(arc).is_empty() and inset.dashes(arc).size() >= 10, "air line is dashed (%d dashes)" % inset.dashes(arc).size())


# Collision: the inset touches no other map UI, and its own text touches neither itself nor the arc.
func _check_collisions(map: Node, inset: AirInset, language: String) -> void:
	var rect := inset.get_global_rect()
	report["inset_rect_canvas"] = [rect.position.x, rect.position.y, rect.size.x, rect.size.y]
	var frame_offset: Vector2 = map.map_frame.get_global_rect().position
	var others := {
		"route_card": map.route_card.get_global_rect(),
		"status_backing": Rect2(map.status_rect().position + frame_offset, map.status_rect().size),
		"zoom_in": map.zoom_in_button.get_global_rect(),
		"zoom_out": map.zoom_out_button.get_global_rect(),
		"globe_button": map.globe_button.get_global_rect(),
		"region_button": map.region_button.get_global_rect(),
		"calendar_label": map.calendar_label.get_global_rect(),
		"scale_bar": Rect2((map.get_script().get_script_constant_map()["SCALE_BAR_ORIGIN"] as Vector2) + frame_offset - Vector2(1, 8), Vector2(140, 14)),
		"bottom_strip": Rect2(0, 313, 640, 47),
		"header": Rect2(0, 0, 640, 44),
	}
	for place_id in map.place_buttons:
		var button: Button = map.place_buttons[place_id]
		if button.visible:
			others["place_" + place_id] = button.get_global_rect()
	var index := 0
	for entry in map.annotation_label_rects():
		var r: Rect2 = entry["rect"]
		others["annotation_%d_%s" % [index, entry["text"]]] = Rect2(r.position + frame_offset, r.size)
		index += 1
	for key in others:
		_check(not rect.intersects(others[key]), "%s: inset clear of %s" % [language, key])
	_check(map.map_frame.get_global_rect().encloses(rect), "%s: inset inside the map frame" % language)
	var area := Rect2(inset.area.position, inset.area.size)
	var labels := {"origin": inset.origin_label, "destination": inset.dest_label}
	for key in labels:
		var label: Label = labels[key]
		var lr := Rect2(label.position, label.size)
		_check(area.encloses(lr), "%s: %s label '%s' inside inset map area" % [language, key, label.text])
		var hit_arc := false
		for p in inset.arc:
			hit_arc = hit_arc or lr.has_point(p + area.position)
		var plane := Rect2(inset.plane_pt + area.position - Vector2(6, 6), Vector2(12, 12))
		_check(not hit_arc and not lr.intersects(plane), "%s: %s label clear of arc and plane" % [language, key])
		_check(label.get_theme_font_size("font_size") >= 10, "%s: %s label font >= 10 canvas px" % [language, key])
	var o_rect := Rect2(inset.origin_label.position, inset.origin_label.size)
	var d_rect := Rect2(inset.dest_label.position, inset.dest_label.size)
	_check(not o_rect.intersects(d_rect), "%s: endpoint labels do not overlap" % language)
	_check(not o_rect.intersects(Rect2(inset.dest_pt + area.position - Vector2(6, 6), Vector2(12, 12))) \
		and not d_rect.intersects(Rect2(inset.origin_pt + area.position - Vector2(6, 6), Vector2(12, 12))), "%s: labels clear of the other endpoint" % language)
	var font := inset.caption.get_theme_font("font")
	var caption_w := font.get_string_size(inset.caption.text, HORIZONTAL_ALIGNMENT_LEFT, -1, 9).x
	report["caption_width_" + language] = snappedf(caption_w, 0.1)
	_check(caption_w <= inset.size.x - 8.0, "%s: caption '%s' fits (%.1f <= %.1f)" % [language, inset.caption.text, caption_w, inset.size.x - 8.0])
	if inset.revised:
		var cap_rect := Rect2(inset.caption.position + Vector2(inset.caption.size.x - caption_w, 0), Vector2(caption_w, inset.caption_height))
		_check(inset.scale_text_rect.has_area() and not inset.scale_text_rect.grow(3).intersects(cap_rect), "%s: inset scale bar %d km (%.1f px) clear of caption" % [language, int(inset.scale_km), inset.scale_px])
		_check(absf(inset.scale_px * inset.projection.km_per_pixel() - inset.scale_km) < 0.01, "%s: inset scale bar length matches projection" % language)
		_check(inset.origin_label.has_theme_stylebox_override("normal") and inset.dest_label.has_theme_stylebox_override("normal"), "%s: endpoint labels have backing plates" % language)
		report["inset_scale_km"] = inset.scale_km
	_check(_contrast(AirInset.COLOR_TEXT, AirInset.COLOR_BG) >= 7.0 and _contrast(AirInset.COLOR_SUBTEXT, AirInset.COLOR_BG) >= 4.5, "%s: text contrast (%.1f, %.1f)" % [language, _contrast(AirInset.COLOR_TEXT, AirInset.COLOR_BG), _contrast(AirInset.COLOR_SUBTEXT, AirInset.COLOR_BG)])


# Click: the inset swallows no input. Real mouse events through the window.
func _check_clicks(app: Node, map: Node, inset: AirInset) -> void:
	var minutes: int = app.calendar_minutes
	var center_before: Vector2 = map.view.center
	var scale := float(root.size.x) / 640.0
	map.close_route_card()
	await _settle()
	var button: Button = map.place_buttons[CHICAGO]
	await _click(button.get_global_rect().get_center() * scale)
	_check(map.route_card.visible and map.selected_place_id == CHICAGO, "real click on the Chicago marker opens its card")
	_choose_air(map)
	await _settle()
	_check(inset.visible, "inset appears after a real marker click")
	var preview_before: Dictionary = app.travel_preview.duplicate(true)
	await _click(inset.get_global_rect().get_center() * scale)
	_check(map.route_card.visible and map.selected_place_id == CHICAGO and app.travel_preview == preview_before, "click on the inset changes no route state")
	_check(map.view.center.is_equal_approx(center_before), "click on the inset does not pan the map")
	_check(app.calendar_minutes == minutes, "click on the inset charges no time")
	var depart_rect: Rect2 = map.depart_button.get_global_rect()
	_check(not depart_rect.intersects(inset.get_global_rect()), "Depart button not covered by the inset")
	await _click(map.cancel_button.get_global_rect().get_center() * scale)
	_check(not map.route_card.visible and app.travel_preview.is_empty(), "real click on Cancel closes the card and clears the preview")
	await _settle()
	_check(not inset.visible, "inset hidden after Cancel")
	_check(app.calendar_minutes == minutes and app.current_location_id == NYC, "Cancel charges no time")
	map.select_place(CHICAGO)
	_choose_air(map)
	await _settle()


func _click(at: Vector2) -> void:
	var motion := InputEventMouseMotion.new()
	motion.position = at
	motion.global_position = at
	root.push_input(motion)
	await _settle()
	for pressed in [true, false]:
		var event := InputEventMouseButton.new()
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = pressed
		event.position = at
		event.global_position = at
		root.push_input(event)
		await _settle()


# The rendered frame really carries the inset: dash pixels and the border inside its rectangle.
func _check_pixels(image: Image, res: Vector2i, inset: AirInset, language: String) -> void:
	var k := float(res.x) / 640.0
	var rect := inset.get_global_rect()
	var air_px := 0
	var border_px := 0
	for y in range(int(rect.position.y * k), int(rect.end.y * k)):
		for x in range(int(rect.position.x * k), int(rect.end.x * k)):
			var c := image.get_pixel(x, y)
			if c.r > 0.82 and c.g > 0.9 and c.b > 0.94:
				air_px += 1
	for x in range(int(rect.position.x * k) + 2, int(rect.end.x * k) - 2):
		var c := image.get_pixel(x, int(rect.position.y * k))
		if absf(c.g - AirInset.COLOR_BORDER.g) < 0.12 and absf(c.b - AirInset.COLOR_BORDER.b) < 0.12:
			border_px += 1
	report["air_pixels_%s_%dx%d" % [language, res.x, res.y]] = air_px
	_check(air_px >= int(40 * k * k), "%s %dx%d: dashed air line rendered (%d light pixels)" % [language, res.x, res.y, air_px])
	_check(border_px >= int(rect.size.x * k * 0.8), "%s %dx%d: inset border rendered (%d px)" % [language, res.x, res.y, border_px])


func _capture(res: Vector2i, label: String) -> Image:
	await _settle()
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	if image == null or image.get_size() != res:
		_check(false, "capture %s is %s, expected %s (run without --headless)" % [label, image.get_size() if image else "null", res])
		return null
	var path := ProjectSettings.globalize_path(OUT_DIR).path_join("rpg-2-star-ocean-the-second_global-map_nyc-chicago-air-inset_%s-%s_%s.png" % [variant, label, TAG])
	if image.save_png(path) != OK:
		_check(false, "capture failed: " + path)
		return null
	report["captures"].append(path.get_file())
	print("CAPTURED " + path)
	return image


func _settle() -> void:
	for i in 3:
		await process_frame


static func _dist_to_segment(p: Vector2, a: Vector2, b: Vector2) -> float:
	return p.distance_to(Geometry2D.get_closest_point_to_segment(p, a, b))


static func _luminance(c: Color) -> float:
	var out := 0.0
	var weights := [0.2126, 0.7152, 0.0722]
	var channels := [c.r, c.g, c.b]
	for i in 3:
		var v: float = channels[i]
		v = v / 12.92 if v <= 0.03928 else pow((v + 0.055) / 1.055, 2.4)
		out += weights[i] * v
	return out


static func _contrast(a: Color, b: Color) -> float:
	var la := _luminance(a)
	var lb := _luminance(b)
	return (maxf(la, lb) + 0.05) / (minf(la, lb) + 0.05)
