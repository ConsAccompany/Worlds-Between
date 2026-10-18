extends SceneTree

# TEST-ONLY capture + check for the global map v03r1 zoom label correction in game/scripts/scifi_world_map.gd
# (2026-10-17, UNAPPROVED). One bounded change over v03 (e8b8f8af): when no label slot is clear, a place's plate
# slides to the nearest clear position within CLAMP_REACH of its marker (_clamped_label_rect), instead of taking the
# first in-frame slot whatever it covers. At 1.5x zoom with the Washington car card open, v03 put Washington's plate
# over the Globe / region view buttons and New York's plate half under the card's edge.
#
# States, native 640x360, zh and en: the Northeast browse view, the zoomed-in (1.5x) Washington car card (the route-card
# readability check's state) and the Great Lakes Chicago flight card. In each, every visible place plate must stay in
# the map frame, clear of the fixed controls, the card, other markers and other plates, with click targets apart; the
# rendered control and card pixels must be identical with the place plates hidden, and every plate must be drawn.
# Travel minutes, the date-only arrival and the generic modes are pinned to v03's values.
#
# Needs a display renderer (no --headless). From the repo root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path to this file>
# Captures go to outputs/ unless WB_MAP_V03R1_OUT names another folder (used for the "before" run against v03).
# They are unapproved evidence; map art stays unaccepted and no counter changes.

const TAG := "test-only-v03r1_20261017-184737-5ef3676e"
const PREFIX := "rpg-2-star-ocean-the-second_global-map_v03r1"
const OUT_DIR := "res://../outputs"
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

var checks := 0
var failures: Array = []
var report := {"tag": TAG, "status": "UNAPPROVED test-only capture; map-art gate open; no counter changed", "checks": [], "captures": [], "failures": [], "facts": {}}
var out_dir := ""
var app: Node
var map: Node


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	out_dir = OS.get_environment("WB_MAP_V03R1_OUT")
	if out_dir.is_empty():
		out_dir = ProjectSettings.globalize_path(OUT_DIR)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = RES
	root.size = RES
	SaveStore.root_path = "user://test-saves/m2-map-v03r1-test-only-5ef3676e"
	app = root.get_node("AppState")
	app.begin_new_run()
	app.show_initial_guide = false
	app.language = "zh"
	change_scene_to_file("res://scenes/scifi_world_map.tscn")
	await _settle()
	await _settle()
	map = current_scene
	var start_minutes: int = app.calendar_minutes
	_check(app.current_location_id == NYC, "fresh run starts at New York City (%s)" % app.current_location_id)
	report["facts"]["clamp_reach"] = map.get("CLAMP_REACH")

	for language in ["zh", "en"]:
		app.language = language
		app.language_changed.emit()
		await _settle()
		map.enter_region("us_northeast")
		await _settle()
		var where := "%s northeast browse" % language
		_check_labels(where)
		await _check_plates_rendered(where)
		await _capture("us-northeast-%s" % language)

		# The route-card readability check's zoomed state: 1.5x about (320, 134), then Washington's card.
		map.zoom_view(Vector2(320, 134), 1.5)
		map.select_place(DC)
		await _settle()
		where = "%s zoomed Washington car card" % language
		_check(map.route_card.visible, "%s: card open" % where)
		_check(String(map.selected_route_option().get("mode", "")) == "car", "%s: car trip offered" % where)
		_check_route_rules(where)
		_check_trip_pins(DC, "car", language, where)
		_check_card_text(where)
		_check_labels(where)
		await _check_plates_rendered(where)
		var zoomed := await _capture("us-northeast-zoom-card-washington-car-%s" % language)
		_check_reticle_pixels(zoomed, DC, where)
		await _check_card_opaque(where)
		map.close_route_card()
		await _settle()

		map.enter_region("us_great_lakes")
		map.select_place(CHICAGO)
		await _settle()
		_choose_mode("air")
		await _settle()
		where = "%s Chicago flight card" % language
		_check(map.route_inset.is_visible_in_tree(), "%s: route strip on the card" % where)
		_check_route_rules(where)
		_check_trip_pins(CHICAGO, "air", language, where)
		_check_card_text(where)
		_check(map.card_coords.visible and map.card_from.visible, "%s: coordinates and origin lines kept (no overflow fallback)" % where)
		_check_labels(where)
		await _check_plates_rendered(where)
		var chicago := await _capture("us-great-lakes-card-chicago-air-%s" % language)
		_check_reticle_pixels(chicago, CHICAGO, where)
		await _check_card_opaque(where)
		map.close_route_card()
		await _settle()

	_check(app.calendar_minutes == start_minutes and app.travel_preview.is_empty(), "previews, zoom and language swaps charged nothing")
	_finish()


func _choose_mode(mode: String) -> void:
	for option in map.route_state.get("options", []):
		if option["mode"] == mode:
			map._choose_option(option["option_id"])
			return


func _frame_offset() -> Vector2:
	return map.map_frame.get_global_rect().position


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
		# Its own marker as drawn (party ring 9.5 px, else the 5.5 px dot); the diagonal slots touch the 18 px dot box by
		# design. The 11.5 px selection ring is recorded only: v03's standard "right" slot starts 10 px from the marker,
		# so a selected place labelled on the right (Chicago at default zoom) overlaps its ring by 1.5 px, unchanged here.
		var radius := 9.5 if place_id == app.current_location_id else 5.5
		var near := Vector2(clampf(marker.x + offset.x, plate.position.x, plate.end.x), clampf(marker.y + offset.y, plate.position.y, plate.end.y))
		var reach := near.distance_to(marker + offset)
		_check(reach >= radius, "%s: %s label clear of its own marker (r %.1f, nearest %.1f)" % [where, place_id, radius, reach])
		if card_open and place_id == map.selected_place_id:
			report["facts"]["selection_ring_overlap_px %s %s" % [where, place_id]] = snappedf(maxf(0.0, 11.5 - reach), 0.1)
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
	_check(String(option.get("mode", "")) == mode and int(option.get("total_minutes", -1)) == pin, "%s: %s trip charges %d min (pinned %d, as v03)" % [where, mode, option.get("total_minutes", -1), pin])
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
	_check(gold >= 3, "%s: selection reticle ticks drawn around %s (%d of 4)" % [where, place_id, gold])


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
		print("MAP_V03R1_ZOOM_LABEL_OK %d checks, %d captures" % [checks, report["captures"].size()])
		quit(0)
	else:
		print("MAP_V03R1_ZOOM_LABEL_FAIL %d/%d failed" % [failures.size(), checks])
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
