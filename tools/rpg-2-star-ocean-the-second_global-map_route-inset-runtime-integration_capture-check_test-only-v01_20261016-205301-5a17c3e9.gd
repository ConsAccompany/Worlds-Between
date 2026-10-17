extends SceneTree

# TEST-ONLY capture + check for the runtime route inset and label layout in game/scripts/scifi_world_map.gd
# (Stream A, 2026-10-16). Answers the native-640 hierarchy review
# (docs/qa/…global-map-v02_native-640-visual-hierarchy-review_unapproved-v01_20261016-193000-6c4b527e.md):
#   - the NYC <-> Chicago two-endpoint inset (first shown by the test-only v01r1 tool, adea3798) now lives in
#     the live map: it appears while the card offers a trip whose origin is outside the regional view;
#   - marker labels take collision-free slots clear of fixed controls (NYC / Yonkers, Washington / bottom row);
#   - markers keep their travel-data coordinates and hitboxes; route confirm / cancel, whole-hour durations,
#     date-only arrivals and generic flights (no airport names) are unchanged.
# Optional second presentation: when the v02 map-art skin and its assets are present, the skin is loaded at
# run time through a generated subclass whose only change is _offscreen_marker: the far city's name is no
# longer drawn beside the stub like a local marker but pinned to the map edge with an outward chevron and an
# "off this map" suffix. The skin file itself is not edited.
#
# Needs a display renderer (no --headless). From the repo root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path to this file>
# Captures are native 640x360 (zh and en) in outputs/, one checks JSON beside them. They are unapproved
# evidence for Codex / creator review; they do not accept map art. M2 map-art stays open, meter unchanged.

const GeoProjection := preload("res://scripts/world_geo_projection.gd")
const MapData := preload("res://scripts/world_map_data.gd")
const TAG := "test-only-v01_20261016-205301-5a17c3e9"
const PREFIX := "rpg-2-star-ocean-the-second_global-map_route-inset-runtime"
const OUT_DIR := "res://../outputs"
const SKIN_FILE := "rpg-2-star-ocean-the-second_global-map-art_godot-runtime-skin_candidate-unapproved-v02_20261016-172153-ab9459d4.gd"
const META_REL := "assets/map-art/global-map-art-candidate-v02-ab9459d4/rpg-2-star-ocean-the-second_global-map-art_runtime-meta_candidate-unapproved-v02_20261016-172153-ab9459d4.json"
const NYC := "earth.us.ny.new-york-city"
const YONKERS := "earth.us.ny.yonkers-outskirts"
const DC := "earth.us.dc.washington-ruins"
const CHICAGO := "earth.us.il.chicago"
const RES := Vector2i(640, 360)
const FOOTER_TOP := 313.0
const FORBIDDEN := ["LGA", "ORD", "JFK", "EWR", "MDW", "LaGuardia", "O'Hare", "OHare", "Midway", "Newark Liberty",
	"airport", "Airport", "terminal", "check-in", "机场", "航站", "值机", "拉瓜迪亚", "奥黑尔"]
const OFF_MAP := {"zh": "%s · 不在本图", "en": "%s · off this map"}
# The map's COLOR_MARKER, which borders the inset.
const INSET_BORDER := Color("#79cfc0")

var checks := 0
var failures: Array = []
var report := {"tag": TAG, "status": "UNAPPROVED test-only capture; map-art gate open", "checks": [], "captures": [], "failures": [], "facts": {}}
var calendar_events := 0
var travel_events := 0
var app: Node
var map: Node
var skin: RefCounted
var tagger: EdgeTagger


# Draws the skin's off-screen cue as an edge-pinned tag: a dotted leader from the stub tip to the edge of
# the free map area, a plate pinned to that edge, an outward chevron and "<far place> · off this map".
class EdgeTagger:
	extends RefCounted

	var map: Node
	var app: Node
	var drawn: Array = []

	func draw_edge_tag(skin: Object, canvas: Node2D, stub: PackedVector2Array, far: Dictionary, color: Color) -> void:
		if stub.size() < 3:
			return
		var tip: Vector2 = stub[stub.size() - 1]
		var dir: Vector2 = (tip - stub[maxi(0, stub.size() - 6)]).normalized()
		if dir == Vector2.ZERO:
			return
		# The skin empties offscreen_label_rects at the start of each overlay draw: start this frame's list too.
		var skin_rects: Array = skin.get("offscreen_label_rects")
		if skin_rects.is_empty():
			drawn.clear()
		var map_size: Vector2 = map.map_frame.size
		var right := map_size.x - 4.0
		if map.route_card.visible:
			right = map._card_local_rect().position.x - 4.0
		var free := Rect2(Vector2(4, 4), Vector2(right - 4.0, map_size.y - 8.0))
		# Where the stub's bearing leaves the free area, and through which side.
		var t := INF
		var side := ""
		if dir.x < 0.0 and (free.position.x - tip.x) / dir.x < t:
			t = (free.position.x - tip.x) / dir.x
			side = "left"
		if dir.x > 0.0 and (free.end.x - tip.x) / dir.x < t:
			t = (free.end.x - tip.x) / dir.x
			side = "right"
		if dir.y < 0.0 and (free.position.y - tip.y) / dir.y < t:
			t = (free.position.y - tip.y) / dir.y
			side = "top"
		if dir.y > 0.0 and (free.end.y - tip.y) / dir.y < t:
			t = (free.end.y - tip.y) / dir.y
			side = "bottom"
		var edge := tip + dir * t
		var language := String(app.language)
		var text: String = OFF_MAP.get(language, OFF_MAP["en"]) % MapData.text(far, "map_label", language)
		var font := ThemeDB.fallback_font
		var text_size := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 9)
		var size := Vector2(text_size.x + 16.0, text_size.y + 2.0).round()
		var blocked: Array = skin.call("blocked_rects")
		var inset: Rect2 = map.route_inset_rect()
		if inset.has_area():
			blocked.append(inset.grow(2))
		for other in drawn:
			blocked.append((other["rect"] as Rect2).grow(2))
		var chosen := Rect2()
		for step in 40:
			for direction in [1, -1]:
				var shift := float(step * 2 * direction)
				var box := Rect2()
				match side:
					"left":
						box = Rect2(Vector2(free.position.x, edge.y - size.y * 0.5 + shift), size)
					"right":
						box = Rect2(Vector2(free.end.x - size.x, edge.y - size.y * 0.5 + shift), size)
					"top":
						box = Rect2(Vector2(edge.x - size.x * 0.5 + shift, free.position.y), size)
					_:
						box = Rect2(Vector2(edge.x - size.x * 0.5 + shift, free.end.y - size.y), size)
				box.position = box.position.round()
				var clear := free.encloses(box) and not box.grow(2).has_point(tip)
				for other in blocked:
					clear = clear and not box.intersects(other)
				if clear:
					chosen = box
					break
			if chosen.has_area():
				break
		if not chosen.has_area():
			return
		# Dotted leader from the stub tip to the tag, so the stub visibly continues off the map.
		var anchor := Vector2(clampf(tip.x, chosen.position.x, chosen.end.x), clampf(tip.y, chosen.position.y, chosen.end.y))
		skin.call("_pixel_line", canvas, tip.round(), anchor.round(), color, 1, [1, 3])
		var plate: Color = skin.get("C_PLATE")
		var text_color: Color = skin.get("C_TEXT")
		canvas.draw_rect(chosen, plate)
		canvas.draw_rect(Rect2(chosen.position + Vector2(0.5, 0.5), chosen.size - Vector2.ONE), color, false, 1.0)
		# Outward chevron on the plate's edge side; text after it.
		var mid := chosen.get_center().round()
		var chevron := PackedVector2Array()
		var text_x := chosen.position.x + 4.0
		match side:
			"left":
				chevron = PackedVector2Array([Vector2(chosen.position.x + 2, mid.y), Vector2(chosen.position.x + 7, mid.y - 4), Vector2(chosen.position.x + 7, mid.y + 4)])
				text_x = chosen.position.x + 10.0
			"right":
				chevron = PackedVector2Array([Vector2(chosen.end.x - 2, mid.y), Vector2(chosen.end.x - 7, mid.y - 4), Vector2(chosen.end.x - 7, mid.y + 4)])
			"top":
				chevron = PackedVector2Array([Vector2(chosen.end.x - 6, chosen.position.y + 2), Vector2(chosen.end.x - 10, chosen.position.y + 7), Vector2(chosen.end.x - 2, chosen.position.y + 7)])
			_:
				chevron = PackedVector2Array([Vector2(chosen.end.x - 6, chosen.end.y - 2), Vector2(chosen.end.x - 10, chosen.end.y - 7), Vector2(chosen.end.x - 2, chosen.end.y - 7)])
		canvas.draw_colored_polygon(chevron, color)
		canvas.draw_string(font, Vector2(text_x, chosen.position.y + font.get_ascent(9) + 1.0), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 9, text_color)
		drawn.append({"text": text, "rect": chosen, "side": side, "tip": tip, "far": String(far.get("id", ""))})
		skin_rects.append(chosen)


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = RES
	root.size = RES
	SaveStore.root_path = "user://test-saves/m2-route-inset-runtime-test-only-5a17c3e9"
	app = root.get_node("AppState")
	app.begin_new_run()
	app.show_initial_guide = false
	app.language = "zh"
	app.calendar_advanced.connect(func(_a, _b, _c): calendar_events += 1)
	app.travel_completed.connect(func(_r): travel_events += 1)
	await _open_map()
	var start_minutes: int = app.calendar_minutes
	_check(app.current_location_id == NYC, "fresh run starts at New York City (%s)" % app.current_location_id)
	_load_skin()

	for language in ["zh", "en"]:
		await _set_language(language)
		# Northeast, browsing: labels only, no card, no inset.
		map.enter_region("us_northeast")
		await _settle()
		_check(not map.route_inset.visible, "%s northeast browse: no inset without a card" % language)
		_check_labels("%s northeast browse" % language)
		await _capture_both("us-northeast-%s" % language)
		# Washington by car: both ends on this view, so no inset.
		map.select_place(DC)
		await _settle()
		_check(map.route_card.visible and not map.route_inset.visible, "%s Washington card: no inset (both ends on the view)" % language)
		_check_route_rules("%s Washington card" % language)
		_check_labels("%s northeast card Washington" % language)
		await _capture_both("us-northeast-card-washington-car-%s" % language)
		map.select_place(YONKERS)
		await _settle()
		_check(not map.route_inset.visible, "%s Yonkers card: no inset" % language)
		map.close_route_card()
		# Chicago by air from New York: the origin is in another region, so the inset shows both ends.
		map.select_place(CHICAGO)
		await _settle()
		_choose_mode("air")
		await _settle()
		_check(map.route_inset.visible, "%s Chicago air card: inset visible" % language)
		_check_route_rules("%s Chicago card" % language)
		_check_inset(NYC, CHICAGO, "%s Chicago card" % language)
		_check_labels("%s great lakes card Chicago" % language)
		await _capture_both("us-great-lakes-card-chicago-air-%s" % language)
		map.close_route_card()
		await _settle()
		_check(not map.route_inset.visible, "%s inset hides when the card closes" % language)

	map.enter_global()
	await _settle()
	_check(not map.route_inset.visible, "no inset on the globe")
	_check(app.calendar_minutes == start_minutes and calendar_events == 0 and travel_events == 0, "previews, language swaps and cancels charged nothing")
	_check(app.travel_preview.is_empty(), "no pending travel preview after the preview pass")
	await _check_clicks(start_minutes)
	await _travel_and_reverse()
	_finish()


# --- Map states --------------------------------------------------------------------

func _open_map() -> void:
	change_scene_to_file("res://scenes/scifi_world_map.tscn")
	await _settle()
	await _settle()
	map = current_scene
	# A reopened map is a new node: point the skin and the tagger at it.
	if skin != null:
		skin.setup(map, ProjectSettings.globalize_path("res://").path_join("..").simplify_path().path_join(META_REL))
	if tagger != null:
		tagger.map = map


func _set_language(language: String) -> void:
	app.language = language
	app.language_changed.emit()
	await _settle()


func _choose_mode(mode: String) -> void:
	for option in map.route_state.get("options", []):
		if option["mode"] == mode:
			map._choose_option(option["option_id"])
			return


func _load_skin() -> void:
	var tools_dir := String(get_script().resource_path).get_base_dir()
	var repo := ProjectSettings.globalize_path("res://").path_join("..").simplify_path()
	var skin_path := tools_dir.path_join(SKIN_FILE)
	var meta_path := repo.path_join(META_REL)
	if not FileAccess.file_exists(skin_path) or not FileAccess.file_exists(meta_path):
		report["facts"]["skin"] = "v02 skin or assets absent; runtime captures only"
		print("NOTE v02 skin or assets absent; runtime captures only")
		return
	var source := "extends \"%s\"\n\nvar tagger: Object\n\n\nfunc _offscreen_marker(canvas: Node2D, stub: PackedVector2Array, far: Dictionary, color: Color) -> void:\n\tif tagger != null:\n\t\ttagger.call(\"draw_edge_tag\", self, canvas, stub, far, color)\n" % skin_path
	var wrapper := GDScript.new()
	wrapper.source_code = source
	if wrapper.reload() != OK:
		_check(false, "edge-tag subclass of the v02 skin compiles")
		return
	tagger = EdgeTagger.new()
	tagger.map = map
	tagger.app = app
	skin = wrapper.new()
	skin.set("tagger", tagger)
	var problem: String = skin.setup(map, meta_path)
	_check(problem == "", "v02 skin setup (%s)" % (problem if problem != "" else "ok"))
	if problem != "":
		skin = null
	report["facts"]["skin"] = "v02 skin with edge-pinned off-map tag (subclass; skin file unchanged)"


# Runtime drawing first, then (if loaded) the v02 skin with edge-pinned off-map tags.
func _capture_both(state: String) -> void:
	var image := await _capture("%s-runtime" % state)
	if image != null and map.route_inset.visible:
		_check_inset_pixels(image, state)
	if skin == null:
		return
	skin.apply()
	await _settle()
	_check_edge_tags(state)
	await _capture("%s-skin-v02-edge-tag" % state)
	skin.remove()
	await _settle()
	_check(map.overlay.draw.is_connected(map._draw_overlay), "%s: skin removed, map's own drawing restored" % state)


# --- Checks -------------------------------------------------------------------------

func _frame_offset() -> Vector2:
	return map.map_frame.get_global_rect().position


# Labels: no two plates touch, none covers a fixed control, the card or the footer, none leaves the frame;
# every marker stays on its coordinates and inside its own button.
func _check_labels(where: String) -> void:
	var offset := _frame_offset()
	var plates := {}
	for place_id in map.place_buttons:
		var button: Button = map.place_buttons[place_id]
		if not button.visible:
			continue
		var plate: Rect2 = (button.get_node("LabelBackground") as Control).get_global_rect()
		plates[place_id] = plate
		var place: Dictionary = map.find_place(place_id)
		var marker: Vector2 = map.marker_position(place_id)
		_check(marker.is_equal_approx(map.view.geo_to_screen(place["lon"], place["lat"])), "%s: %s marker on its coordinates" % [where, place_id])
		_check(button.get_global_rect().has_point(marker + offset), "%s: %s button covers its marker" % [where, place_id])
		_check(map.map_frame.get_global_rect().encloses(plate), "%s: %s label inside the map frame" % [where, place_id])
		_check(plate.end.y <= FOOTER_TOP - 3.0, "%s: %s label above the footer (bottom %.0f)" % [where, place_id, plate.end.y])
		for fixed in map.fixed_ui_rects():
			var r: Rect2 = fixed
			_check(not plate.intersects(Rect2(r.position + offset, r.size)), "%s: %s label clear of fixed UI %s" % [where, place_id, r])
		if map.route_card.visible:
			_check(not plate.intersects(map.route_card.get_global_rect()), "%s: %s label not under the route card" % [where, place_id])
		for other_id in map.place_buttons:
			if other_id != place_id and map.place_buttons[other_id].visible:
				var dot: Rect2 = map._dot_rect(map.marker_position(other_id))
				_check(not plate.intersects(Rect2(dot.position + offset, dot.size)), "%s: %s label clear of %s marker" % [where, place_id, other_id])
	var ids := plates.keys()
	for i in ids.size():
		for j in range(i + 1, ids.size()):
			var gap := _gap(plates[ids[i]], plates[ids[j]])
			_check(gap >= 2.0, "%s: %s / %s labels separated (%.0f px)" % [where, ids[i], ids[j], gap])
	if plates.has(NYC) and plates.has(YONKERS):
		report["facts"]["nyc_yonkers_gap_px " + where] = _gap(plates[NYC], plates[YONKERS])
	if plates.has(DC):
		report["facts"]["washington_label_bottom " + where] = plates[DC].end.y
		report["facts"]["washington_footer_clearance_px " + where] = FOOTER_TOP - plates[DC].end.y


# Card rules: whole hours, date-only arrival, generic modes, no airport names anywhere on the card or inset.
func _check_route_rules(where: String) -> void:
	_check(String(map.route_state.get("status", "")) == "ready", "%s: route ready" % where)
	var clock := RegEx.create_from_string("\\d{1,2}:\\d{2}")
	for option in map.route_state.get("options", []):
		_check(int(option["total_minutes"]) > 0 and int(option["total_minutes"]) % 60 == 0, "%s: %s charges whole hours (%d min)" % [where, option["option_id"], option["total_minutes"]])
		_check(clock.search(String(option["arrival_text"])) == null and clock.search(String(option["duration_text"])) == null, "%s: %s arrival '%s' and duration '%s' show no clock time" % [where, option["option_id"], option["arrival_text"], option["duration_text"]])
		_check(["car", "air", "air_car"].has(String(option["mode"])), "%s: %s mode is generic (%s)" % [where, option["option_id"], option["mode"]])
	var texts := [map.card_title.text, map.card_subtitle.text, map.card_kind.text, map.card_from.text, map.card_route.text]
	for child in map.card_options.get_children():
		texts.append((child as Button).text)
	if map.route_inset.visible:
		texts.append_array([map.route_inset.origin_label.text, map.route_inset.dest_label.text, map.route_inset.caption.text])
	var joined := "\n".join(texts)
	for word in FORBIDDEN:
		_check(not joined.contains(word), "%s: no '%s' on the card or inset" % [where, word])


func _check_inset(origin_id: String, dest_id: String, where: String) -> void:
	var inset = map.route_inset
	var o: Dictionary = map.find_place(origin_id)
	var d: Dictionary = map.find_place(dest_id)
	var arc: PackedVector2Array = inset.arc
	_check(arc[0].distance_to(inset.projection.geo_to_screen(o["lon"], o["lat"])) < 0.01, "%s: line starts at %s coordinates" % [where, origin_id])
	_check(arc[arc.size() - 1].distance_to(inset.projection.geo_to_screen(d["lon"], d["lat"])) < 0.01, "%s: line ends at %s coordinates" % [where, dest_id])
	var inside := true
	for p in arc:
		inside = inside and Rect2(Vector2.ZERO, inset.area.size).grow(-6).has_point(p)
	_check(inside, "%s: line stays >= 6 px inside the inset map" % where)
	var chord: float = arc[0].distance_to(arc[arc.size() - 1])
	_check(chord >= 100.0, "%s: endpoints %.0f px apart (>= 100)" % [where, chord])
	_check(inset.air and inset.dashes(arc, 4.0, 3.0).size() >= 10, "%s: flight drawn as a dashed line" % where)
	var westward: bool = d["lon"] < o["lon"]
	_check((inset.plane_dir.x < 0.0) == westward, "%s: aircraft points toward the destination" % where)
	# Inset placement: inside the frame, left of the card, clear of every marker, label, fixed control and degree label.
	var rect: Rect2 = map.route_inset_rect()
	var offset := _frame_offset()
	_check(Rect2(Vector2.ZERO, map.map_frame.size).encloses(rect), "%s: inset inside the map frame" % where)
	_check(rect.end.x <= map._card_local_rect().position.x - 2.0, "%s: inset left of the card" % where)
	for fixed in map.fixed_ui_rects():
		_check(not rect.intersects(fixed), "%s: inset clear of fixed UI %s" % [where, fixed])
	for place_id in map.place_buttons:
		var button: Button = map.place_buttons[place_id]
		if button.visible:
			_check(not rect.intersects(Rect2(button.position, button.size)), "%s: inset clear of %s marker and label" % [where, place_id])
	for entry in map.annotation_label_rects():
		_check(not rect.intersects(entry["rect"]), "%s: inset clear of degree label %s" % [where, entry["text"]])
	_check(not map.route_inset.get_global_rect().intersects(map.depart_button.get_global_rect()), "%s: Depart not covered" % where)
	# Inset text: both place names, mode and distance exactly as the card words them; labels clear of the line.
	var option: Dictionary = map.selected_route_option()
	var mode_text: String = load("res://scripts/world_map_text.gd").t("mode_" + String(option["mode"]))
	_check(inset.origin_label.text == MapData.text(o, "map_label", app.language) and inset.dest_label.text == MapData.text(d, "map_label", app.language), "%s: inset names '%s' -> '%s'" % [where, inset.origin_label.text, inset.dest_label.text])
	_check(inset.caption.text.begins_with(mode_text), "%s: caption starts with the card's mode '%s'" % [where, mode_text])
	var card_first_line := ""
	for child in map.card_options.get_children():
		if (child as Button).button_pressed:
			card_first_line = (child as Button).text.get_slice("\n", 0)
	var km_text := String(inset.caption.text).get_slice(" · ", 1)
	_check(km_text != "" and card_first_line.contains(km_text), "%s: caption distance '%s' matches the card line '%s'" % [where, km_text, card_first_line])
	var area: Rect2 = inset.area
	var label_rects := []
	for label in [inset.origin_label, inset.dest_label]:
		var lr := Rect2(label.position, label.size)
		label_rects.append(lr)
		_check(area.encloses(lr), "%s: inset label '%s' inside the inset map" % [where, label.text])
		var hit := false
		for p in arc:
			hit = hit or lr.has_point(p + area.position)
		_check(not hit and not lr.intersects(Rect2(inset.plane_pt + area.position - Vector2(6, 6), Vector2(12, 12))), "%s: inset label '%s' clear of line and aircraft" % [where, label.text])
	_check(not label_rects[0].intersects(label_rects[1]), "%s: inset labels do not overlap" % where)
	var font: Font = inset.caption.get_theme_font("font")
	var caption_w := font.get_string_size(inset.caption.text, HORIZONTAL_ALIGNMENT_LEFT, -1, 9).x
	_check(6.0 + inset.scale_px + 40.0 + caption_w <= inset.size.x, "%s: caption '%s' (%.0f px) fits beside the scale bar" % [where, inset.caption.text, caption_w])
	_check(absf(inset.scale_px * inset.projection.km_per_pixel() - inset.scale_km) < 0.01, "%s: inset scale bar %d km matches its projection" % [where, int(inset.scale_km)])
	report["facts"]["inset_rect " + where] = [rect.position.x, rect.position.y, rect.size.x, rect.size.y]
	report["facts"]["inset_chord_px " + where] = snappedf(chord, 0.1)


func _check_inset_pixels(image: Image, state: String) -> void:
	var rect: Rect2 = map.route_inset.get_global_rect()
	var light := 0
	for y in range(int(rect.position.y), int(rect.end.y)):
		for x in range(int(rect.position.x), int(rect.end.x)):
			var c := image.get_pixel(x, y)
			if c.r > 0.82 and c.g > 0.9 and c.b > 0.94:
				light += 1
	var border := 0
	for x in range(int(rect.position.x) + 2, int(rect.end.x) - 2):
		var c := image.get_pixel(x, int(rect.position.y))
		if absf(c.g - INSET_BORDER.g) < 0.12 and absf(c.b - INSET_BORDER.b) < 0.12:
			border += 1
	report["facts"]["inset_light_px " + state] = light
	_check(light >= 40, "%s: dashed line rendered in the inset (%d light px)" % [state, light])
	_check(border >= int(rect.size.x * 0.8), "%s: inset border rendered (%d px)" % [state, border])


# Skin presentation: every far-place tag sits on the free area's edge, says "off this map", and covers no UI.
func _check_edge_tags(state: String) -> void:
	var language := String(app.language)
	for tag in tagger.drawn:
		var r: Rect2 = tag["rect"]
		_check(String(tag["text"]).ends_with(String(OFF_MAP[language]).get_slice("%s", 1)), "%s: far tag '%s' says it is off the map" % [state, tag["text"]])
		var right: float = map._card_local_rect().position.x - 4.0 if map.route_card.visible else map.map_frame.size.x - 4.0
		var on_edge := absf(r.position.x - 4.0) < 0.6 or absf(r.end.x - right) < 0.6 or absf(r.position.y - 4.0) < 0.6 or absf(r.end.y - (map.map_frame.size.y - 4.0)) < 0.6
		_check(on_edge, "%s: far tag '%s' pinned to the map edge (%s)" % [state, tag["text"], tag["side"]])
		for place_id in map.place_buttons:
			var button: Button = map.place_buttons[place_id]
			if button.visible:
				_check(not r.intersects(Rect2(button.position, button.size)), "%s: far tag clear of %s" % [state, place_id])
		_check(not r.intersects(map.route_inset_rect()), "%s: far tag clear of the inset" % state)
	report["facts"]["edge_tags " + state] = tagger.drawn.map(func(t): return {"text": t["text"], "side": t["side"], "rect": [t["rect"].position.x, t["rect"].position.y, t["rect"].size.x, t["rect"].size.y]})


# Real mouse input: the marker opens the card, the inset swallows nothing, Cancel closes and charges nothing.
func _check_clicks(start_minutes: int) -> void:
	await _set_language("zh")
	map.enter_region("us_great_lakes")
	await _settle()
	var center_before: Vector2 = map.view.center
	await _click(map.place_buttons[CHICAGO].get_global_rect().get_center())
	_check(map.route_card.visible and map.selected_place_id == CHICAGO, "real click on the Chicago marker opens its card")
	_choose_mode("air")
	await _settle()
	_check(map.route_inset.visible, "inset appears after a real marker click")
	var preview_before: Dictionary = app.travel_preview.duplicate(true)
	await _click(map.route_inset.get_global_rect().get_center())
	_check(map.route_card.visible and app.travel_preview == preview_before, "click on the inset changes no route state")
	_check(map.view.center.is_equal_approx(center_before), "click on the inset does not pan the map")
	await _click(map.cancel_button.get_global_rect().get_center())
	_check(not map.route_card.visible and app.travel_preview.is_empty() and not map.route_inset.visible, "real click on Cancel closes the card, clears the preview and hides the inset")
	_check(app.calendar_minutes == start_minutes and app.current_location_id == NYC, "Cancel charges no time")


# Real Depart click: the trip is charged once in whole hours; then the reverse card shows the inset from Chicago.
func _travel_and_reverse() -> void:
	map.select_place(CHICAGO)
	_choose_mode("air")
	await _settle()
	var option: Dictionary = map.selected_route_option()
	var minutes_before: int = app.calendar_minutes
	await _click(map.depart_button.get_global_rect().get_center())
	await _settle()
	await _settle()
	var charged: int = app.calendar_minutes - minutes_before
	_check(app.current_location_id == CHICAGO, "Depart arrives in Chicago (%s)" % app.current_location_id)
	_check(charged == int(option.get("total_minutes", -1)) and charged % 60 == 0, "Depart charged %d min = the card's whole-hour option" % charged)
	_check(travel_events == 1, "exactly one travel_completed (%d)" % travel_events)
	await _open_map()
	for language in ["zh", "en"]:
		await _set_language(language)
		map.enter_region("us_great_lakes")
		await _settle()
		_check_labels("%s great lakes browse from Chicago" % language)
		map.select_place(NYC)
		await _settle()
		_choose_mode("air")
		await _settle()
		_check(map.mode == "region" and map.active_region_id == "us_northeast", "%s reverse card opens the Northeast view" % language)
		_check(map.route_inset.visible, "%s Chicago -> New York card: inset visible" % language)
		if map.route_inset.visible:
			_check_route_rules("%s reverse card" % language)
			_check_inset(CHICAGO, NYC, "%s reverse card" % language)
		_check_labels("%s northeast card New York from Chicago" % language)
		await _capture_both("us-northeast-card-nyc-from-chicago-air-%s" % language)
		map.close_route_card()
		await _settle()
	_check(app.calendar_minutes == minutes_before + charged, "reverse previews charged nothing")


func _finish() -> void:
	if map != null:
		map.close_route_card()
	app.language = "zh"
	report["failures"] = failures
	report["checks_total"] = checks
	var path := ProjectSettings.globalize_path(OUT_DIR).path_join("%s_checks_%s.json" % [PREFIX, TAG])
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "  ") + "\n")
	file.close()
	print("REPORT " + path)
	if failures.is_empty():
		print("ROUTE_INSET_RUNTIME_OK %d checks, %d captures" % [checks, report["captures"].size()])
		quit(0)
	else:
		print("ROUTE_INSET_RUNTIME_FAIL %d/%d failed" % [failures.size(), checks])
		for f in failures:
			print("  FAIL " + f)
		quit(1)


# --- Helpers ------------------------------------------------------------------------

func _check(ok: bool, what: String) -> void:
	checks += 1
	report["checks"].append({"ok": ok, "check": what})
	print(("PASS " if ok else "FAIL ") + what)
	if not ok:
		failures.append(what)


# Clear pixels between two rectangles (0 when they touch or overlap).
static func _gap(a: Rect2, b: Rect2) -> float:
	var dx := maxf(b.position.x - a.end.x, a.position.x - b.end.x)
	var dy := maxf(b.position.y - a.end.y, a.position.y - b.end.y)
	return maxf(0.0, maxf(dx, dy))


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


func _capture(label: String) -> Image:
	await _settle()
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	if image == null or image.get_size() != RES:
		_check(false, "capture %s is %s, expected %s (run without --headless)" % [label, image.get_size() if image else "null", RES])
		return null
	var path := ProjectSettings.globalize_path(OUT_DIR).path_join("%s_%s-640x360_%s.png" % [PREFIX, label, TAG])
	if image.save_png(path) != OK:
		_check(false, "capture failed: " + path)
		return null
	report["captures"].append(path.get_file())
	print("CAPTURED " + path)
	return image


func _settle() -> void:
	for i in 3:
		await process_frame
