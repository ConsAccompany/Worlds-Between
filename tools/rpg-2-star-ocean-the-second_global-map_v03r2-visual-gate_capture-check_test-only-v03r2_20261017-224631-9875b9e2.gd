extends SceneTree

# TEST-ONLY capture + check for the global map v03r2 bounded visual gate (2026-10-17, UNAPPROVED map art). v03r2 is
# one visual pass over v03r1 (5ef3676e) on the targets in Codex's v03r1 native judgment (66d8a7b4):
#   - land / water value hierarchy: v03r2 relief bake (lighter, calmer land; darker sea), quiet pale-stone roads so the
#     trip line is the only gold, a fainter grid and a stepped edge shade on regional views;
#   - Northeast route and Great Lakes focal path: a heavier trip line with a chevron; when the origin is off the view or
#     under the card, the destination's end of the same line runs to the card's edge and points into it;
#   - selected marker and card edge: a brass reticle on a dark halo, plates kept clear of it, a pan on opening a card
#     only when the reticle would be boxed in by a control or the frame, and a brass pointer on a plate whose dot is
#     under the card;
#   - teal / brass science UI on the route card, its buttons and the map's view and zoom buttons.
# Geography, routes, travel minutes, dates, click handling and bilingual labels are pinned to v03r1's values.
#
# States, native 640x360, zh and en: globe, Northeast browse, Washington car card (default zoom), Washington car card
# at 1.5x (the route-card readability check's state) and the Great Lakes Chicago flight card. It also measures the
# captured land / lake / sea values and land texture so the same tool can be run against the v03r1 scripts.
#
# Needs a display renderer (no --headless). From the repo root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path to this file>
# Captures go to outputs/ unless WB_MAP_V03R2_OUT names another folder (used for the "before" run against v03r1).
# They are unapproved evidence; map art stays unaccepted and no counter changes.

const TAG := "test-only-v03r2_20261017-224631-9875b9e2"
const PREFIX := "rpg-2-star-ocean-the-second_global-map_v03r2"
const OUT_DIR := "res://../outputs"
const MapData := preload("res://scripts/world_map_data.gd")
const NYC := "earth.us.ny.new-york-city"
const YONKERS := "earth.us.ny.yonkers-outskirts"
const DC := "earth.us.dc.washington-ruins"
const CHICAGO := "earth.us.il.chicago"
const RES := Vector2i(640, 360)
const FOOTER_TOP := 313.0
const FORBIDDEN := ["LGA", "ORD", "JFK", "EWR", "MDW", "LaGuardia", "O'Hare", "OHare", "Midway", "Newark Liberty",
	"airport", "Airport", "terminal", "check-in", "机场", "航站", "值机", "拉瓜迪亚", "奥黑尔"]
const TRIP_PINS := {"car %s" % DC: 300, "air %s" % CHICAGO: 360}
const ARRIVAL_PINS := {"zh": "2537年5月25日", "en": "May 25, 2537"}
# Coordinates pinned to the travel data v03r1 read (locations-routes m2-us-science-v02 c454007b), lon / lat.
const COORD_PINS := {NYC: Vector2(-74.00708, 40.71205), YONKERS: Vector2(-73.89789, 40.9304), DC: Vector2(-77.00887, 38.88983),
	CHICAGO: Vector2(-87.6333, 41.88407)}
const SAMPLE_STEP := 5

var checks := 0
var failures: Array = []
var report := {"tag": TAG, "status": "UNAPPROVED test-only capture; map-art gate open; no counter changed", "checks": [], "captures": [], "failures": [], "facts": {}, "values": {}}
var out_dir := ""
var app: Node
var map: Node
var v03r2 := false


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	out_dir = OS.get_environment("WB_MAP_V03R2_OUT")
	if out_dir.is_empty():
		out_dir = ProjectSettings.globalize_path(OUT_DIR)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = RES
	root.size = RES
	SaveStore.root_path = "user://test-saves/m2-map-v03r2-test-only-9875b9e2"
	app = root.get_node("AppState")
	app.begin_new_run()
	app.show_initial_guide = false
	app.language = "zh"
	change_scene_to_file("res://scenes/scifi_world_map.tscn")
	await _settle()
	await _settle()
	map = current_scene
	v03r2 = map.has_method("route_path_points")
	report["facts"]["scripts"] = "v03r2" if v03r2 else "baseline (no v03r2 functions)"
	var start_minutes: int = app.calendar_minutes
	_check(app.current_location_id == NYC, "fresh run starts at New York City (%s)" % app.current_location_id)
	_check_places_pinned()
	_check_palette()

	for language in ["zh", "en"]:
		app.language = language
		app.language_changed.emit()
		await _settle()

		map.enter_global()
		await _settle()
		var where := "%s globe" % language
		_check_globe(where)
		_check_controls_styled(where)
		await _capture("globe-%s" % language)

		map.enter_region("us_northeast")
		await _settle()
		where = "%s northeast browse" % language
		_check_labels(where)
		await _check_plates_rendered(where)
		var browse := await _capture("us-northeast-%s" % language)
		_measure_values(browse, "us_northeast", where)

		# Washington by car at default zoom: both ends on the view, so the line runs marker to marker.
		var center_before: Vector2 = map.view.center
		map.select_place(DC)
		await _settle()
		where = "%s Washington car card" % language
		_check(map.view.center.is_equal_approx(center_before), "%s: default-zoom card opens without panning" % where)
		await _check_card_state(where, DC, "car", language)
		_check(not map.route_inset.is_visible_in_tree(), "%s: both ends on the view, no strip" % where)
		var card := await _capture("us-northeast-card-washington-car-%s" % language)
		_check_reticle_pixels(card, DC, where)
		_check_route_pixels(card, where)
		await _check_card_opaque(where)
		map.close_route_card()
		await _settle()

		# The route-card readability check's zoomed state: 1.5x about (320, 134), then Washington's card.
		map.zoom_view(Vector2(320, 134), 1.5)
		await _settle()
		var dc_before: Vector2 = map.marker_position(DC)
		var scale_before: float = map.view.scale
		# Before the card opens, Washington's reticle is boxed in here (recorded): the reason the view may pan.
		var region_rect := Rect2(map.region_button.position, map.region_button.size)
		var region_near := Vector2(clampf(dc_before.x, region_rect.position.x, region_rect.end.x), clampf(dc_before.y, region_rect.position.y, region_rect.end.y))
		report["facts"]["boxed_before_open %s" % language] = {"region_button_px": snappedf(region_near.distance_to(dc_before), 0.1), "frame_bottom_px": snappedf(map.MAP_RECT.size.y - dc_before.y, 0.1)}
		map.select_place(DC)
		await _settle()
		where = "%s zoomed Washington car card" % language
		var dc_after: Vector2 = map.marker_position(DC)
		report["facts"]["selection_pan_px %s" % where] = [snappedf(dc_after.x - dc_before.x, 0.1), snappedf(dc_after.y - dc_before.y, 0.1)]
		_check(is_equal_approx(map.view.scale, scale_before), "%s: zoom kept (scale %.3f)" % [where, map.view.scale])
		_check(dc_after.distance_to(dc_before) <= 64.0, "%s: the reticle pan stays short (%.1f px, limit 64)" % [where, dc_after.distance_to(dc_before)])
		await _check_card_state(where, DC, "car", language)
		var zoomed := await _capture("us-northeast-zoom-card-washington-car-%s" % language)
		_check_reticle_pixels(zoomed, DC, where)
		_check_route_pixels(zoomed, where)
		await _check_card_opaque(where)
		map.close_route_card()
		await _settle()

		map.enter_region("us_great_lakes")
		await _settle()
		_measure_values(await _grab(), "us_great_lakes", "%s great lakes browse" % language)
		map.select_place(CHICAGO)
		await _settle()
		_choose_mode("air")
		await _settle()
		where = "%s Chicago flight card" % language
		_check(map.route_inset.is_visible_in_tree(), "%s: route strip on the card" % where)
		await _check_card_state(where, CHICAGO, "air", language)
		_check(map.card_coords.visible and map.card_from.visible, "%s: coordinates and origin lines kept (no overflow fallback)" % where)
		var chicago := await _capture("us-great-lakes-card-chicago-air-%s" % language)
		_check_reticle_pixels(chicago, CHICAGO, where)
		_check_route_pixels(chicago, where)
		await _check_card_opaque(where)
		map.close_route_card()
		await _settle()

	_check(app.calendar_minutes == start_minutes and app.travel_preview.is_empty(), "previews, zoom, pans and language swaps charged nothing")
	_check(app.current_location_id == NYC, "the party never left New York City")
	_finish()


func _choose_mode(mode: String) -> void:
	for option in map.route_state.get("options", []):
		if option["mode"] == mode:
			map._choose_option(option["option_id"])
			return


func _frame_offset() -> Vector2:
	return map.map_frame.get_global_rect().position


func _selected_half() -> float:
	var half = map.get("SELECTED_HALF")
	return 11.5 if half == null else float(half)


# The reticle's outer edge (12.5 px) plus 1.5 px clear: the v03r2 RETICLE_REACH, also applied to the baseline scripts.
func _reticle_reach() -> float:
	var reach = map.get("RETICLE_REACH")
	return 14.0 if reach == null else float(reach)


# --- Static pins ---------------------------------------------------------------

func _check_places_pinned() -> void:
	for place_id in COORD_PINS:
		var place: Dictionary = map.find_place(place_id)
		var pin: Vector2 = COORD_PINS[place_id]
		_check(not place.is_empty() and absf(float(place["lon"]) - pin.x) < 1e-5 and absf(float(place["lat"]) - pin.y) < 1e-5,
			"%s stays at its travel-data coordinates (%s, %s)" % [place_id, place.get("lon"), place.get("lat")])


# The land colour must equal the bake's land_low_color (the transparent coast band shows it); roads are quiet and not
# gold, so the trip line is the only gold line.
func _check_palette() -> void:
	var relief: Dictionary = MapData.region_relief("us_northeast")
	_check(not relief.is_empty(), "relief layer loads for the Northeast")
	if not relief.is_empty():
		_check(Color(relief["land_low_color"]).is_equal_approx(map.COLOR_LAND), "COLOR_LAND equals the bake's land_low_color (%s)" % relief["land_low_color"])
	var road: Color = map.COLOR_ROAD
	var line: Color = map.COLOR_ROUTE_LINE
	report["facts"]["road_color"] = [road.to_html(), snappedf(road.s, 0.01), road.a]
	report["facts"]["route_line_color"] = [line.to_html(), snappedf(line.s, 0.01)]
	if v03r2:
		_check(road.s < 0.25 and road.a <= 0.4, "major roads are quiet pale stone (s %.2f, a %.2f), not trip gold (s %.2f)" % [road.s, road.a, line.s])
		_check((map.COLOR_ROAD_MINOR as Color).a <= 0.2, "minor roads stay faint (a %.2f)" % (map.COLOR_ROAD_MINOR as Color).a)


# --- Globe ---------------------------------------------------------------------

func _check_globe(where: String) -> void:
	_check(map.mode == "global", "%s: globe mode" % where)
	var frame: Rect2 = map.map_frame.get_global_rect()
	var offset := _frame_offset()
	for region_id in map.region_buttons:
		var button: Button = map.region_buttons[region_id]
		_check(button.visible and button.text == "" and not (button.get_node("Primary") as Label).text.is_empty(), "%s: %s region plate shown and named" % [where, region_id])
		var plate: Rect2 = (button.get_node("LabelBackground") as Control).get_global_rect()
		_check(frame.encloses(plate), "%s: %s plate inside the frame" % [where, region_id])
		for fixed in map.fixed_ui_rects():
			var r: Rect2 = fixed
			_check(not plate.intersects(Rect2(r.position + offset, r.size)), "%s: %s plate clear of fixed UI %s" % [where, region_id, r])


# The map view and zoom buttons wear the science UI (StyleBoxFlat plates with a 1 px edge), and the active view reads
# as the active tab.
func _check_controls_styled(where: String) -> void:
	if not v03r2:
		_check(false, "%s: v03r2 control styling present" % where)
		return
	for control in [map.zoom_in_button, map.zoom_out_button, map.globe_button, map.region_button]:
		var normal := (control as Button).get_theme_stylebox("normal") as StyleBoxFlat
		var disabled := (control as Button).get_theme_stylebox("disabled") as StyleBoxFlat
		_check(normal != null and normal.border_color.is_equal_approx(map.COLOR_TEAL_EDGE) and normal.border_width_left == 1 and normal.corner_radius_top_left == 0,
			"%s: '%s' is a teal-edged science plate" % [where, (control as Button).text])
		_check(disabled != null and disabled.bg_color.is_equal_approx(map.COLOR_UI_ACTIVE), "%s: '%s' active-view state is a lifted plate" % [where, (control as Button).text])


# --- Card states -------------------------------------------------------------------

func _check_card_state(where: String, place_id: String, mode: String, language: String) -> void:
	_check(map.route_card.visible and map.selected_place_id == place_id, "%s: card open for %s" % [where, place_id])
	_check(String(map.selected_route_option().get("mode", "")) == mode, "%s: %s trip offered" % [where, mode])
	_check_route_rules(where)
	_check_trip_pins(place_id, mode, language, where)
	_check_card_text(where)
	_check_card_style(where)
	_check_labels(where)
	_check_reticle_clear(where, place_id)
	_check_route_line(where)
	await _check_plates_rendered(where)


func _check_card_style(where: String) -> void:
	var style := map.route_card.get_theme_stylebox("panel") as StyleBoxFlat
	_check(style != null and style.bg_color.a == 1.0, "%s: card opaque" % where)
	if not v03r2:
		_check(false, "%s: v03r2 card trim present" % where)
		return
	_check(style.border_color.is_equal_approx(map.COLOR_BRASS), "%s: card rim is brass" % where)
	var depart := map.depart_button.get_theme_stylebox("normal") as StyleBoxFlat
	_check(depart != null and depart.border_color.is_equal_approx(map.COLOR_BRASS), "%s: Depart is a brass-rimmed plate" % where)
	var cancel := map.cancel_button.get_theme_stylebox("normal") as StyleBoxFlat
	_check(cancel != null and cancel.border_color.is_equal_approx(map.COLOR_TEAL_EDGE), "%s: Cancel is a teal-edged plate" % where)
	for child in map.card_options.get_children():
		var button := child as Button
		var chosen := button.get_theme_stylebox("pressed") as StyleBoxFlat
		_check(chosen != null and chosen.border_width_left == 3 and chosen.border_color.is_equal_approx(map.COLOR_BRASS), "%s: chosen trip line takes the brass bar" % where)


# The selected reticle (its ring plus a 2 px gap) is clear of every fixed control, the card and the frame edge.
func _check_reticle_clear(where: String, place_id: String) -> void:
	var marker: Vector2 = map.marker_position(place_id)
	var reach := _reticle_reach()
	var frame := Rect2(Vector2.ZERO, map.MAP_RECT.size)
	var edge := minf(minf(marker.x, frame.end.x - marker.x), minf(marker.y, frame.end.y - marker.y))
	report["facts"]["reticle_edge_px %s" % where] = snappedf(edge, 0.1)
	_check(edge >= reach, "%s: reticle %.1f px from the frame edge (needs %.1f)" % [where, edge, reach])
	var controls := {"zoom in": map.zoom_in_button, "zoom out": map.zoom_out_button, "globe": map.globe_button, "region": map.region_button}
	var rects := {}
	for key in controls:
		rects[key] = Rect2((controls[key] as Control).position, (controls[key] as Control).size)
	rects["card"] = map._card_local_rect()
	rects["status"] = map.status_rect()
	for key in rects:
		var r: Rect2 = rects[key]
		var near := Vector2(clampf(marker.x, r.position.x, r.end.x), clampf(marker.y, r.position.y, r.end.y))
		var gap := near.distance_to(marker)
		report["facts"]["reticle_gap_px %s %s" % [where, key]] = snappedf(gap, 0.1)
		_check(gap >= reach, "%s: reticle clear of the %s (%.1f px, needs %.1f)" % [where, key, gap, reach])


# The trip line: marker to marker when both ends are free, else the destination's end running to the card or frame.
func _check_route_line(where: String) -> void:
	if not v03r2:
		_check(false, "%s: v03r2 route path present" % where)
		return
	var origin: Dictionary = map.find_place(app.current_location_id)
	var destination: Dictionary = map.find_place(map.selected_place_id)
	var air := String(map.selected_route_option()["mode"]) != "car"
	var path: PackedVector2Array = map.route_path_points(origin, destination, air)
	var focus: bool = map.route_inset_wanted()
	var length := 0.0
	for i in path.size() - 1:
		length += path[i].distance_to(path[i + 1])
	report["facts"]["route_path %s" % where] = {"focus": focus, "points": path.size(), "length_px": snappedf(length, 0.1),
		"first": [snappedf(path[0].x, 0.1), snappedf(path[0].y, 0.1)] if path.size() > 0 else [], "last": [snappedf(path[path.size() - 1].x, 0.1), snappedf(path[path.size() - 1].y, 0.1)] if path.size() > 0 else []}
	_check(length >= 40.0, "%s: trip line drawn on the map (%.0f px)" % [where, length])
	if path.size() < 2:
		return
	var dest_pt: Vector2 = map.marker_position(map.selected_place_id)
	var near_dest := path[0] if focus else path[path.size() - 1]
	_check(near_dest.distance_to(dest_pt) <= _selected_half() + 1.5, "%s: line starts at the selected reticle (%.1f px)" % [where, near_dest.distance_to(dest_pt)])
	var free: Rect2 = map.route_focus_rect()
	for p in path:
		if not free.grow(0.5).has_point(p) and focus:
			_check(false, "%s: focal path stays left of the card and inside the frame (%s)" % [where, p])
			return
	if focus:
		var last := path[path.size() - 1]
		var to_edge := minf(minf(absf(last.x - free.end.x), absf(last.x - free.position.x)), minf(absf(last.y - free.end.y), absf(last.y - free.position.y)))
		var span := path[0].distance_to(last)
		var cap: float = map.FOCAL_REACH
		_check(span <= cap + 1.5, "%s: focal path at most %.0f px from the reticle (%.1f)" % [where, cap, span])
		_check(to_edge <= 1.5 or span >= cap - 1.5, "%s: focal path runs on to the card edge, the frame or its %.0f px cap (%.1f px short of an edge, span %.1f)" % [where, cap, to_edge, span])
		var card_edge := absf(last.x - free.end.x) <= 1.5
		report["facts"]["focal_path_meets %s" % where] = "card edge" if card_edge else ("frame edge" if to_edge <= 1.5 else "length cap")
	else:
		var origin_pt: Vector2 = map.marker_position(origin["id"])
		_check(path[0].distance_to(origin_pt) <= 12.5, "%s: line runs from the origin's marker (%.1f px)" % [where, path[0].distance_to(origin_pt)])


# Gold line pixels really drawn along the path: at least 40% of samples every 4 px find the line colour within 1 px.
func _check_route_pixels(image: Image, where: String) -> void:
	if image == null or not v03r2:
		return
	var origin: Dictionary = map.find_place(app.current_location_id)
	var destination: Dictionary = map.find_place(map.selected_place_id)
	var path: PackedVector2Array = map.route_path_points(origin, destination, String(map.selected_route_option()["mode"]) != "car")
	var offset := _frame_offset()
	var gold: Color = map.COLOR_ROUTE_LINE
	var samples := 0
	var hits := 0
	for i in path.size() - 1:
		var a := path[i]
		var b := path[i + 1]
		var steps := maxi(1, int(a.distance_to(b) / 4.0))
		for s in steps:
			var p := a.lerp(b, float(s) / steps) + offset
			samples += 1
			var found := false
			for dy in range(-1, 2):
				for dx in range(-1, 2):
					var q := Vector2i(p.floor()) + Vector2i(dx, dy)
					if Rect2i(Vector2i.ZERO, RES).has_point(q):
						var c := image.get_pixelv(q)
						found = found or (absf(c.r - gold.r) < 0.08 and absf(c.g - gold.g) < 0.08 and absf(c.b - gold.b) < 0.1)
			if found:
				hits += 1
	report["facts"]["route_gold_samples %s" % where] = [hits, samples]
	_check(samples > 0 and hits * 10 >= samples * 4, "%s: gold trip line visible along its path (%d of %d samples)" % [where, hits, samples])


# --- Labels -----------------------------------------------------------------------

# A plate is checked when its button is shown and its marker is inside the map frame (a marker outside the frame
# keeps an off-frame plate that is clipped, as before). Markers are never moved; one under the open card is recorded.
func _visible_plates() -> Dictionary:
	var out := {}
	var frame: Rect2 = map.map_frame.get_global_rect()
	for place_id in map.place_buttons:
		var button: Button = map.place_buttons[place_id]
		if not button.visible:
			continue
		var marker: Vector2 = map.marker_position(place_id) + _frame_offset()
		if not frame.has_point(marker):
			report["facts"]["marker_outside_frame %s" % place_id] = [marker.x, marker.y]
			continue
		out[place_id] = (button.get_node("LabelBackground") as Control).get_global_rect()
	return out


func _check_labels(where: String) -> void:
	var offset := _frame_offset()
	var plates := _visible_plates()
	var card_open: bool = map.route_card.visible
	var card: Rect2 = map.route_card.get_global_rect()
	for place_id in plates:
		var plate: Rect2 = plates[place_id]
		var button: Button = map.place_buttons[place_id]
		var place: Dictionary = map.find_place(place_id)
		var marker: Vector2 = map.marker_position(place_id)
		report["facts"]["plate %s %s" % [where, place_id]] = [plate.position.x, plate.position.y, plate.size.x, plate.size.y]
		_check(marker.is_equal_approx(map.view.geo_to_screen(place["lon"], place["lat"])), "%s: %s marker on its coordinates" % [where, place_id])
		_check(button.get_global_rect().has_point(marker + offset), "%s: %s button covers its marker" % [where, place_id])
		_check(map.map_frame.get_global_rect().encloses(plate), "%s: %s label inside the map frame" % [where, place_id])
		_check(plate.end.y <= FOOTER_TOP - 3.0, "%s: %s label above the footer (bottom %.0f)" % [where, place_id, plate.end.y])
		_check((button.get_node("LabelEdge") as Control).get_global_rect().is_equal_approx(plate), "%s: %s plate edge matches its plate" % [where, place_id])
		_check((button.get_node("Primary") as Label).get_theme_font_size("font_size") >= 12, "%s: %s name at >= 12 px" % [where, place_id])
		_check(not (button.get_node("Primary") as Label).text.is_empty() and not (button.get_node("Secondary") as Label).text.is_empty(), "%s: %s plate names both languages" % [where, place_id])
		for fixed in map.fixed_ui_rects():
			var r: Rect2 = fixed
			_check(not plate.intersects(Rect2(r.position + offset, r.size)), "%s: %s label clear of fixed UI %s" % [where, place_id, r])
		for control in [map.zoom_in_button, map.zoom_out_button, map.globe_button, map.region_button]:
			_check(not plate.intersects((control as Control).get_global_rect()), "%s: %s label clear of the %s button" % [where, place_id, (control as Button).text])
		if card_open:
			_check(not plate.intersects(card), "%s: %s label not under or across the route card" % [where, place_id])
			if card.has_point(marker + offset):
				report["facts"]["marker_under_card %s %s" % [where, place_id]] = card.position.x - plate.end.x
		for other_id in map.place_buttons:
			if other_id != place_id and map.place_buttons[other_id].visible:
				var dot: Rect2 = map._dot_rect(map.marker_position(other_id))
				_check(not plate.intersects(Rect2(dot.position + offset, dot.size)), "%s: %s label clear of %s marker" % [where, place_id, other_id])
		# Its own marker as drawn: the selected reticle (SELECTED_HALF) while its card is open, else the party ring
		# (9.5 px) or the 5.5 px dot. v03r2 keeps a selected plate off its reticle; v03 let Chicago's cut 2 px into it.
		var selected: bool = card_open and place_id == map.selected_place_id
		var radius := _selected_half() - 0.5 if selected else (9.5 if place_id == app.current_location_id else 5.5)
		var near := Vector2(clampf(marker.x + offset.x, plate.position.x, plate.end.x), clampf(marker.y + offset.y, plate.position.y, plate.end.y))
		var reach := near.distance_to(marker + offset)
		_check(reach >= radius, "%s: %s label clear of its own marker%s (r %.1f, nearest %.1f)" % [where, place_id, " reticle" if selected else "", radius, reach])
		report["facts"]["leader_px %s %s" % [where, place_id]] = snappedf(reach, 0.1)
		_check(reach <= 64.0, "%s: %s label within 64 px of its marker (%.1f)" % [where, place_id, reach])
	var ids := plates.keys()
	for i in ids.size():
		for j in range(i + 1, ids.size()):
			var gap := _gap(plates[ids[i]], plates[ids[j]])
			_check(gap >= 2.0, "%s: %s / %s labels separated (%.0f px)" % [where, ids[i], ids[j], gap])
			var a: Rect2 = map.place_buttons[ids[i]].get_global_rect()
			var b: Rect2 = map.place_buttons[ids[j]].get_global_rect()
			_check(not a.intersects(b), "%s: %s / %s click targets do not overlap" % [where, ids[i], ids[j]])


# Rendered proof: with the place buttons hidden, every view/zoom button and the open card render identically (no plate
# pixel on a control or the card), and every checked plate rect changes (the plate is really drawn, not clipped away).
func _check_plates_rendered(where: String) -> void:
	var plates := _visible_plates()
	var shown := await _grab()
	var hidden_ids := []
	for place_id in map.place_buttons:
		if map.place_buttons[place_id].visible:
			map.place_buttons[place_id].visible = false
			hidden_ids.append(place_id)
	map.overlay.queue_redraw()
	var hidden := await _grab()
	for place_id in hidden_ids:
		map.place_buttons[place_id].visible = true
	map.overlay.queue_redraw()
	await _settle()
	var controls := [map.zoom_in_button, map.zoom_out_button, map.globe_button, map.region_button]
	for control in controls:
		var differ := _differing(shown, hidden, (control as Control).get_global_rect())
		_check(differ == 0, "%s: '%s' button pixels untouched by place labels (%d differ)" % [where, (control as Button).text, differ])
	if map.route_card.visible:
		var differ := _differing(shown, hidden, map.route_card.get_global_rect())
		_check(differ == 0, "%s: route card pixels untouched by place labels (%d differ)" % [where, differ])
	for place_id in plates:
		var plate: Rect2 = plates[place_id]
		var area := int(plate.size.x * plate.size.y)
		var differ := _differing(shown, hidden, plate)
		report["facts"]["plate_drawn_px %s %s" % [where, place_id]] = [differ, area]
		_check(differ * 2 >= area, "%s: %s plate drawn in full view (%d of %d px)" % [where, place_id, differ, area])


func _differing(a: Image, b: Image, rect: Rect2) -> int:
	var count := 0
	var r := Rect2i(rect.position.floor(), rect.size.ceil()).intersection(Rect2i(Vector2i.ZERO, RES))
	for y in range(r.position.y, r.end.y):
		for x in range(r.position.x, r.end.x):
			if a.get_pixel(x, y) != b.get_pixel(x, y):
				count += 1
	return count


# --- Trips and card ------------------------------------------------------------------

func _check_route_rules(where: String) -> void:
	_check(String(map.route_state.get("status", "")) == "ready", "%s: route ready" % where)
	var clock := RegEx.create_from_string("\\d{1,2}:\\d{2}")
	for option in map.route_state.get("options", []):
		_check(int(option["total_minutes"]) > 0 and int(option["total_minutes"]) % 60 == 0, "%s: %s charges whole hours (%d min)" % [where, option["option_id"], option["total_minutes"]])
		_check(clock.search(String(option["arrival_text"])) == null and clock.search(String(option["duration_text"])) == null, "%s: %s arrival and duration show no clock time" % [where, option["option_id"]])
		_check(["car", "air", "air_car"].has(String(option["mode"])), "%s: %s mode is generic (%s)" % [where, option["option_id"], option["mode"]])
	var texts := [map.card_title.text, map.card_subtitle.text, map.card_kind.text, map.card_coords.text, map.card_from.text, map.card_route.text]
	for child in map.card_options.get_children():
		texts.append((child as Button).text)
	if map.route_inset.is_visible_in_tree():
		texts.append_array([map.route_inset.origin_label.text, map.route_inset.dest_label.text])
	for place_id in map.place_buttons:
		texts.append((map.place_buttons[place_id].get_node("Primary") as Label).text)
	var joined := "\n".join(texts)
	for word in FORBIDDEN:
		_check(not joined.contains(word), "%s: no '%s' on the card, strip or labels" % [where, word])


func _check_trip_pins(place_id: String, mode: String, language: String, where: String) -> void:
	var option: Dictionary = map.selected_route_option()
	var pin: int = TRIP_PINS.get("%s %s" % [mode, place_id], -1)
	report["facts"]["trip %s" % where] = {"mode": option.get("mode", ""), "total_minutes": option.get("total_minutes", -1), "arrival_text": option.get("arrival_text", "")}
	_check(String(option.get("mode", "")) == mode and int(option.get("total_minutes", -1)) == pin, "%s: %s trip charges %d min (pinned %d, as v03r1)" % [where, mode, option.get("total_minutes", -1), pin])
	_check(String(option.get("arrival_text", "")) == ARRIVAL_PINS[language], "%s: arrival '%s' is the date only ('%s')" % [where, option.get("arrival_text", ""), ARRIVAL_PINS[language]])
	var button_text := ""
	for child in map.card_options.get_children():
		if (child as Button).button_pressed:
			button_text = (child as Button).text
	_check(button_text == map.route_option_text(option), "%s: option line is route_option_text '%s'" % [where, button_text.replace("\n", " | ")])


# Card readable at native size: CARD_RECT width, height within CARD_RECT, 10-11 px text, every shown line and both
# buttons inside the card. The zoomed card may drop the coordinates (and en the origin) line by v03's overflow rule.
func _check_card_text(where: String) -> void:
	var card: Rect2 = map.route_card.get_global_rect()
	_check(card.position.is_equal_approx(map.CARD_RECT.position) and card.size.y <= map.CARD_RECT.size.y + 0.5 and is_equal_approx(card.size.x, map.CARD_RECT.size.x), "%s: card stays at CARD_RECT (got %s)" % [where, card])
	report["facts"]["card_lines %s" % where] = {"coords": map.card_coords.visible, "from": map.card_from.visible, "height": card.size.y}
	for entry in [[map.card_title, 11], [map.card_subtitle, 10], [map.card_kind, 11], [map.card_from, 11], [map.card_coords, 10]]:
		var label: Label = entry[0]
		_check(label.get_theme_font_size("font_size") >= entry[1], "%s: card text '%s' at >= %d px" % [where, label.text.get_slice("\n", 0), entry[1]])
		if label.is_visible_in_tree() and not label.text.is_empty():
			_check(card.encloses(label.get_global_rect()), "%s: card text '%s' inside the card" % [where, label.text.get_slice("\n", 0)])
	for child in map.card_options.get_children():
		_check((child as Button).get_theme_font_size("font_size") >= 11 and card.encloses((child as Button).get_global_rect()), "%s: option line at >= 11 px inside the card" % where)
	for button in [map.depart_button, map.cancel_button]:
		_check((button as Button).is_visible_in_tree() and card.encloses((button as Button).get_global_rect()), "%s: '%s' inside the card" % [where, (button as Button).text])


func _check_card_opaque(where: String) -> void:
	var with_map := await _grab()
	map.map_frame.visible = false
	var without_map := await _grab()
	map.map_frame.visible = true
	await _settle()
	var differ := _differing(with_map, without_map, map.route_card.get_global_rect())
	_check(differ == 0, "%s: no map pixel shows through the card (%d differ)" % [where, differ])


func _check_reticle_pixels(image: Image, place_id: String, where: String) -> void:
	if image == null:
		return
	var at: Vector2 = map.marker_position(place_id) + _frame_offset()
	var gold := 0
	for d in [Vector2(0, -10), Vector2(0, 10), Vector2(-10, 0), Vector2(10, 0)]:
		var p := Vector2i((at + d).floor())
		if not Rect2i(Vector2i.ZERO, RES).has_point(p):
			continue
		var c := image.get_pixelv(p)
		if absf(c.r - map.COLOR_HERE.r) < 0.12 and absf(c.g - map.COLOR_HERE.g) < 0.12 and absf(c.b - map.COLOR_HERE.b) < 0.15:
			gold += 1
	_check(gold == 4, "%s: all four selection reticle ticks drawn around %s (%d of 4)" % [where, place_id, gold])


# --- Values -----------------------------------------------------------------------------

# Mean Rec. 709 luma of captured land, lake and sea pixels on a SAMPLE_STEP grid in the map frame, away from controls,
# plates, markers, the status panel and coasts (a sample counts only when the points 2 px around it share its class),
# plus land texture: mean absolute luma step between a land sample and the land pixel 1 px to its right.
func _measure_values(image: Image, region_id: String, where: String) -> void:
	if image == null:
		return
	var rings: Array = MapData.region_land_rings(MapData.geodata_key(region_id))
	var holes := []
	for ring in rings:
		if ring["hole"]:
			holes.append(ring)
	var offset := _frame_offset()
	var avoid := []
	for fixed in map.fixed_ui_rects():
		avoid.append((fixed as Rect2).grow(2))
	for place_id in map.place_buttons:
		var button: Button = map.place_buttons[place_id]
		if button.visible:
			avoid.append(Rect2(button.position, button.size).grow(6))
	var sums := {"land": 0.0, "lake": 0.0, "sea": 0.0}
	var counts := {"land": 0, "lake": 0, "sea": 0}
	var texture := 0.0
	var texture_n := 0
	var size: Vector2 = map.MAP_RECT.size
	for y in range(SAMPLE_STEP, int(size.y) - SAMPLE_STEP, SAMPLE_STEP):
		for x in range(SAMPLE_STEP, int(size.x) - SAMPLE_STEP, SAMPLE_STEP):
			var p := Vector2(x + 0.5, y + 0.5)
			var skip := false
			for r in avoid:
				if (r as Rect2).has_point(p):
					skip = true
					break
			if skip:
				continue
			var kind := _class_at(p, rings, holes)
			var same := true
			for d in [Vector2(2, 0), Vector2(-2, 0), Vector2(0, 2), Vector2(0, -2)]:
				if _class_at(p + d, rings, holes) != kind:
					same = false
					break
			if not same:
				continue
			var at := Vector2i((p + offset).floor())
			var l := _luma(image.get_pixelv(at))
			sums[kind] += l
			counts[kind] += 1
			if kind == "land" and _class_at(p + Vector2(1, 0), rings, holes) == "land":
				texture += absf(_luma(image.get_pixelv(at + Vector2i(1, 0))) - l)
				texture_n += 1
	var out := {}
	for kind in sums:
		out[kind] = snappedf(sums[kind] / maxf(1.0, counts[kind]), 0.001)
		out[kind + "_samples"] = counts[kind]
	out["land_texture_step"] = snappedf(texture / maxf(1.0, texture_n), 0.0001)
	if counts["sea"] > 0:
		out["land_minus_sea"] = snappedf(out["land"] - out["sea"], 0.001)
	if counts["lake"] > 0:
		out["land_minus_lake"] = snappedf(out["land"] - out["lake"], 0.001)
	report["values"][where] = out
	print("VALUES %s %s" % [where, JSON.stringify(out)])


func _class_at(p: Vector2, rings: Array, holes: Array) -> String:
	var geo: Vector2 = map.view.screen_to_geo(p)
	if MapData.is_on_land(geo.x, geo.y, rings):
		return "land"
	for ring in holes:
		if Geometry2D.is_point_in_polygon(geo, ring["points"]):
			return "lake"
	return "sea"


static func _luma(c: Color) -> float:
	return 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b


# --- Capture and report -----------------------------------------------------------------

func _grab() -> Image:
	await _settle()
	await RenderingServer.frame_post_draw
	return root.get_texture().get_image()


func _capture(label: String) -> Image:
	var image := await _grab()
	if image == null or image.get_size() != RES:
		_check(false, "capture %s is %s, expected %s (run without --headless)" % [label, image.get_size() if image else "null", RES])
		return null
	var path := out_dir.path_join("%s_%s-640x360_%s.png" % [PREFIX, label, TAG])
	if image.save_png(path) != OK:
		_check(false, "capture failed: " + path)
		return null
	report["captures"].append(path.get_file())
	print("CAPTURED " + path)
	return image


func _finish() -> void:
	report["failures"] = failures
	report["checks_total"] = checks
	var manifest := {"tag": TAG, "status": "UNAPPROVED test-only captures; map-art gate open; no counter changed", "resolution": "640x360 native", "captures": []}
	for capture_name in report["captures"]:
		manifest["captures"].append({"file": capture_name, "sha256": FileAccess.get_sha256(out_dir.path_join(capture_name))})
	var manifest_file := FileAccess.open(out_dir.path_join("%s_capture-manifest_%s.json" % [PREFIX, TAG]), FileAccess.WRITE)
	manifest_file.store_string(JSON.stringify(manifest, "  ") + "\n")
	manifest_file.close()
	var path := out_dir.path_join("%s_checks_%s.json" % [PREFIX, TAG])
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  ") + "\n")
	file.close()
	print("REPORT " + path)
	if failures.is_empty():
		print("MAP_V03R2_VISUAL_GATE_OK %d checks, %d captures" % [checks, report["captures"].size()])
		quit(0)
	else:
		print("MAP_V03R2_VISUAL_GATE_FAIL %d/%d failed" % [failures.size(), checks])
		for f in failures:
			print("  FAIL " + f)
		quit(1)


func _check(ok: bool, what: String) -> void:
	checks += 1
	report["checks"].append({"ok": ok, "check": what})
	if not ok:
		failures.append(what)


static func _gap(a: Rect2, b: Rect2) -> float:
	var dx := maxf(b.position.x - a.end.x, a.position.x - b.end.x)
	var dy := maxf(b.position.y - a.end.y, a.position.y - b.end.y)
	return maxf(0.0, maxf(dx, dy))


func _settle() -> void:
	for i in 3:
		await process_frame
