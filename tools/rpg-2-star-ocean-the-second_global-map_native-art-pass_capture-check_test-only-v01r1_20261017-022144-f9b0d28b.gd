extends SceneTree

# TEST-ONLY capture + check for the native map-art pass in game/scripts/scifi_world_map.gd (2026-10-17,
# UNAPPROVED). Answers the first map-art gate brief
# (docs/qa/rpg-2-star-ocean-the-second_global-map_first-art-gate-visual-brief_unapproved-v01_20261016-231801-a4c79e20.md):
#   - land, lake and sea in three value families, measured on the live 640x360 frame;
#   - real relief and coastal shelf from the baked us_east relief layer (no invented terrain);
#   - a faint grid; NYC / Yonkers / Washington labels separated and readable;
#   - the NYC <-> Chicago inset with a header, drop shadow and a gold flight path;
#   - markers on travel-data coordinates, real mouse clicks, Cancel free, Depart charging whole hours once.
# Forked from the 5a17c3e9 route-inset tool, without its optional v02 skin presentation.
# r1 (2026-10-17, f9b0d28b) adds, after Codex's globe review:
#   - five distinct, restrained civilization-sphere land colours on the globe (sampled on the live frame),
#     each still in the land value family above lakes and sea; borderland and Antarctica DLC kept apart;
#   - the relief credit plate (regional views only, clear of every map control) and the map credits
#     panel it opens with the Tilezen / Mapzen, USGS and NOAA attribution, by real clicks.
#
# Needs a display renderer (no --headless). From the repo root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path to this file>
# Captures are native 640x360 (zh and en) in outputs/, one checks JSON beside them. They are unapproved
# evidence for Codex / creator review; map art stays unaccepted and no counter changes.

const MapData := preload("res://scripts/world_map_data.gd")
const TAG := "test-only-v01r1_20261017-022144-f9b0d28b"
const PREFIX := "rpg-2-star-ocean-the-second_global-map_native-art"
const OUT_DIR := "res://../outputs"
const NYC := "earth.us.ny.new-york-city"
const YONKERS := "earth.us.ny.yonkers-outskirts"
const DC := "earth.us.dc.washington-ruins"
const CHICAGO := "earth.us.il.chicago"
const RES := Vector2i(640, 360)
const FOOTER_TOP := 313.0
const FORBIDDEN := ["LGA", "ORD", "JFK", "EWR", "MDW", "LaGuardia", "O'Hare", "OHare", "Midway", "Newark Liberty",
	"airport", "Airport", "terminal", "check-in", "机场", "航站", "值机", "拉瓜迪亚", "奥黑尔"]
const INSET_BORDER := Color("#79cfc0")
const ROUTE_GOLD := Color("#f2d27e")
# Interior land points per sphere (lon, lat), away from the globe's region badges, status panel and buttons.
# Off the 30-degree graticule, so a grid line never tints a sample.
const SPHERE_SAMPLES := {
	"science": [Vector2(-112, 58), Vector2(-100, 62), Vector2(-98, 31), Vector2(-75, 55)],
	"magic": [Vector2(-56, -10), Vector2(-65, -25), Vector2(-52, -5), Vector2(-68, -40)],
	"wuxia": [Vector2(100, 35), Vector2(80, 25), Vector2(112, 28), Vector2(75, 45)],
	"nature": [Vector2(135, -25), Vector2(125, -22), Vector2(145, -26), Vector2(117, -26)],
	"culture": [Vector2(20, 10), Vector2(25, -15), Vector2(10, 49), Vector2(4, 20)],
	"borderland": [Vector2(-102, 24), Vector2(-100, 20)],
	"dlc_antarctica": [Vector2(40, -76), Vector2(125, -76), Vector2(-100, -79)],
	"unassigned": [Vector2(95, 63), Vector2(65, 58), Vector2(-40, 72)],
}
const SEA_SAMPLES := [Vector2(-25, 5), Vector2(-145, 10), Vector2(75, -25), Vector2(-140, -40)]
const FIVE := ["science", "magic", "wuxia", "nature", "culture"]
const CREDIT_WORDS := ["Mapzen", "Tilezen", "U.S. Geological Survey", "GMTED2010", "SRTM",
	"National Oceanic and Atmospheric Administration", "ETOPO1", "github.com/tilezen/joerd/blob/master/docs/attribution.md", "Natural Earth"]

var checks := 0
var failures: Array = []
var report := {"tag": TAG, "status": "UNAPPROVED test-only capture; map-art gate open; no counter changed", "checks": [], "captures": [], "failures": [], "facts": {}}
var calendar_events := 0
var travel_events := 0
var app: Node
var map: Node
var map_text: Script


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.content_scale_size = RES
	root.size = RES
	SaveStore.root_path = "user://test-saves/m2-native-map-art-test-only-f9b0d28b"
	app = root.get_node("AppState")
	map_text = load("res://scripts/world_map_text.gd")
	app.begin_new_run()
	app.show_initial_guide = false
	app.language = "zh"
	app.calendar_advanced.connect(func(_a, _b, _c): calendar_events += 1)
	app.travel_completed.connect(func(_r): travel_events += 1)
	await _open_map()
	var start_minutes: int = app.calendar_minutes
	_check(app.current_location_id == NYC, "fresh run starts at New York City (%s)" % app.current_location_id)
	_check_art_constants()

	for language in ["zh", "en"]:
		await _set_language(language)
		map.enter_region("us_northeast")
		await _settle()
		_check(not map.route_inset.visible, "%s northeast browse: no inset without a card" % language)
		_check_labels("%s northeast browse" % language)
		var browse := await _capture("us-northeast-%s" % language)
		_check_values(browse, "%s northeast browse" % language, true)
		_check_grid(browse, "%s northeast browse" % language)
		_check_browse_nyc_yonkers(language)
		_check_credit_plate("%s northeast browse" % language)
		await _check_credits_panel(language)
		# Car route: Washington from New York, both ends on this view, so no inset.
		map.select_place(DC)
		await _settle()
		_check(map.route_card.visible and not map.route_inset.visible, "%s Washington card: no inset (both ends on the view)" % language)
		_check(String(map.selected_route_option().get("mode", "")) == "car", "%s Washington card offers a car trip" % language)
		_check_route_rules("%s Washington car card" % language)
		_check_labels("%s northeast card Washington" % language)
		_check_credit_plate("%s northeast card Washington" % language)
		await _capture("us-northeast-card-washington-car-%s" % language)
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
		_check_credit_plate("%s great lakes card Chicago" % language)
		var chicago := await _capture("us-great-lakes-card-chicago-air-%s" % language)
		_check_inset_pixels(chicago, "%s Chicago card" % language)
		_check_values(chicago, "%s great lakes card" % language, false)
		map.close_route_card()
		await _settle()
		_check(not map.route_inset.visible, "%s inset hides when the card closes" % language)
		map.enter_global()
		await _settle()
		_check(not map.relief_credit_button.visible, "%s globe: no relief credit (no relief drawn)" % language)
		var globe := await _capture("globe-%s" % language)
		_check_globe(globe, language)

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


func _set_language(language: String) -> void:
	app.language = language
	app.language_changed.emit()
	await _settle()


func _choose_mode(mode: String) -> void:
	for option in map.route_state.get("options", []):
		if option["mode"] == mode:
			map._choose_option(option["option_id"])
			return


# --- Art checks ---------------------------------------------------------------------

func _check_art_constants() -> void:
	var relief: Dictionary = MapData.region_relief("us_east")
	_check(not relief.is_empty(), "us_east relief layer loads")
	if relief.is_empty():
		return
	var texture: Texture2D = relief["texture"]
	_check(texture.get_size() == Vector2(1728, 966), "relief texture is 1728x966 (%s)" % texture.get_size())
	_check(Color(relief["land_low_color"]).is_equal_approx(map.COLOR_LAND), "relief flat lowland equals the map's COLOR_LAND")
	var layer: Node2D = map.region_layers["us_northeast"]
	_check(layer.has_node("Relief") and layer.get_node("Relief").texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST, "Northeast land layer draws the relief with nearest filtering")
	_check(map.COLOR_GRID.a <= 0.2, "grid alpha %.2f <= 0.20" % map.COLOR_GRID.a)
	var tint: Dictionary = MapData.globe_sphere_tint()
	_check(not tint.is_empty(), "globe sphere tint layer loads")
	if not tint.is_empty():
		_check((tint["texture"] as Texture2D).get_size() == Vector2(1440, 720), "sphere tint texture is 1440x720")
		_check(tint["ring_spheres"].size() == MapData.global_land_rings().size(), "sphere tint covers every global land ring (%d)" % tint["ring_spheres"].size())
		var polygons: int = map.global_layer.get_children().filter(func(n): return n is Polygon2D).size()
		_check(polygons == MapData.global_land_rings().size(), "globe draws one polygon per land ring, as before (%d)" % polygons)
		report["facts"]["sphere_palette"] = {}
		for i in tint["roles"].size():
			report["facts"]["sphere_palette"][tint["roles"][i]] = (tint["colors"][i] as Color).to_html(false)
	report["facts"]["palette"] = {"sea": map.COLOR_OCEAN.to_html(false), "lake": map.COLOR_LAKE.to_html(false), "land": map.COLOR_LAND.to_html(false), "grid_alpha": map.COLOR_GRID.a}


# Mean luma of sea, lake and land on an 8 px lattice of the live frame. A sample counts only away from coasts
# (its 4-neighbours 4 px away share its class) and away from every control, plate, marker and the inset.
func _check_values(image: Image, where: String, expect_sea: bool) -> void:
	if image == null:
		return
	var key := MapData.geodata_key(map.active_region_id)
	var rings: Array = MapData.region_land_rings(key)
	var holes := rings.filter(func(r): return r["hole"])
	var blocked := _ui_rects_global()
	var offset := _frame_offset()
	var sums := {"sea": [0.0, 0], "lake": [0.0, 0], "land": [0.0, 0]}
	var land_colors := {}
	for y in range(4, int(map.map_frame.size.y) - 4, 8):
		for x in range(4, int(map.map_frame.size.x) - 4, 8):
			var at := Vector2(x, y)
			var screen := at + offset
			var skip := false
			for r in blocked:
				if (r as Rect2).grow(2).has_point(screen):
					skip = true
					break
			if skip:
				continue
			var kind := _class_at(at, rings, holes)
			var same := true
			for d in [Vector2(4, 0), Vector2(-4, 0), Vector2(0, 4), Vector2(0, -4)]:
				same = same and _class_at(at + d, rings, holes) == kind
			if not same:
				continue
			var c := image.get_pixelv(Vector2i(screen))
			sums[kind][0] += c.get_luminance()
			sums[kind][1] += 1
			if kind == "land":
				land_colors[c.to_html(false)] = true
	var means := {}
	for kind in sums:
		means[kind] = snappedf(sums[kind][0] / sums[kind][1], 0.001) if sums[kind][1] > 0 else -1.0
	report["facts"]["value_means " + where] = means
	report["facts"]["value_samples " + where] = {"sea": sums["sea"][1], "lake": sums["lake"][1], "land": sums["land"][1], "land_colors": land_colors.size()}
	_check(means["land"] - means["lake"] >= 0.08 or sums["lake"][1] == 0, "%s: land luma %.3f above lakes %.3f by >= 0.08" % [where, means["land"], means["lake"]])
	if expect_sea:
		_check(means["land"] - means["sea"] >= 0.15, "%s: land luma %.3f above sea %.3f by >= 0.15" % [where, means["land"], means["sea"]])
		_check(land_colors.size() >= 5, "%s: land shows relief (%d distinct sampled colours >= 5)" % [where, land_colors.size()])
	if sums["lake"][1] > 0 and sums["sea"][1] > 0:
		_check(means["lake"] - means["sea"] >= 0.08, "%s: lakes %.3f lighter than sea %.3f by >= 0.08" % [where, means["lake"], means["sea"]])
	elif sums["lake"][1] > 0:
		_check(Color(map.COLOR_LAKE).get_luminance() - Color(map.COLOR_OCEAN).get_luminance() >= 0.08, "%s: lake colour lighter than sea colour by >= 0.08" % where)


func _class_at(at: Vector2, rings: Array, holes: Array) -> String:
	var geo: Vector2 = map.view.screen_to_geo(at)
	for ring in holes:
		if Geometry2D.is_point_in_polygon(geo, ring["points"]):
			return "lake"
	return "land" if MapData.is_on_land(geo.x, geo.y, rings) else "sea"


# Grid contrast: luma step across a whole-degree meridian at sea, against the pixel 3 px beside it.
func _check_grid(image: Image, where: String) -> void:
	if image == null:
		return
	var offset := _frame_offset()
	var steps := []
	for lat in [39.0, 39.4, 38.6]:
		var at: Vector2 = map.view.geo_to_screen(-72.0, lat)
		if not Rect2(Vector2(8, 8), map.map_frame.size - Vector2(16, 16)).has_point(at):
			continue
		var x := int(roundf(at.x - 0.5))
		var line := image.get_pixel(int(offset.x) + x, int(offset.y + at.y)).get_luminance()
		var beside := image.get_pixel(int(offset.x) + x + 3, int(offset.y + at.y)).get_luminance()
		steps.append(absf(line - beside))
	report["facts"]["grid_luma_step " + where] = steps
	_check(not steps.is_empty() and steps.max() <= 0.05, "%s: grid line luma step %s <= 0.05" % [where, steps])


# Globe: each sphere's land, sampled (3x3 mean) at interior points of the live frame, has one colour; the five
# civilization spheres differ from each other by >= 0.10 (RGB distance) and from the neutral borderland,
# unassigned and DLC tones by >= 0.06; every land tone stays >= 0.15 luma above the sea and >= 0.08 above lakes.
func _check_globe(image: Image, language: String) -> void:
	if image == null:
		return
	var where := "%s globe" % language
	var blocked := _ui_rects_global()
	var offset := _frame_offset()
	var means := {}
	for sphere in SPHERE_SAMPLES:
		var colors := []
		for geo in SPHERE_SAMPLES[sphere]:
			var at: Vector2 = map.view.geo_to_screen(geo.x, geo.y)
			var screen := (at + offset).round()
			var skip: bool = not map.map_frame.get_global_rect().grow(-3).has_point(screen)
			for r in blocked:
				skip = skip or (r as Rect2).grow(2).has_point(screen)
			_check(not skip, "%s: %s sample %s is clear of UI" % [where, sphere, geo])
			if not skip:
				colors.append(_mean3(image, Vector2i(screen)))
		if colors.is_empty():
			continue
		var mean := Color(0, 0, 0)
		for c in colors:
			mean += c
		mean = mean / float(colors.size())
		mean.a = 1.0
		var spread := 0.0
		for c in colors:
			spread = maxf(spread, _rgb_distance(c, mean))
		means[sphere] = mean
		report["facts"]["globe_sphere_color %s %s" % [where, sphere]] = {"mean": mean.to_html(false), "luma": snappedf(mean.get_luminance(), 0.001), "spread": snappedf(spread, 0.001)}
		_check(spread <= 0.03, "%s: %s samples share one colour (spread %.3f <= 0.03)" % [where, sphere, spread])
	var sea := Color(0, 0, 0)
	for geo in SEA_SAMPLES:
		sea += _mean3(image, Vector2i((map.view.geo_to_screen(geo.x, geo.y) + offset).round()))
	sea = sea / float(SEA_SAMPLES.size())
	report["facts"]["globe_sea_luma " + where] = snappedf(sea.get_luminance(), 0.001)
	var lake_luma: float = Color(map.COLOR_LAKE).get_luminance()
	for sphere in means:
		var luma: float = means[sphere].get_luminance()
		_check(luma - sea.get_luminance() >= 0.15, "%s: %s land luma %.3f above sea %.3f by >= 0.15" % [where, sphere, luma, sea.get_luminance()])
		_check(luma - lake_luma >= 0.08, "%s: %s land luma %.3f above the lake colour %.3f by >= 0.08" % [where, sphere, luma, lake_luma])
	for i in FIVE.size():
		for j in range(i + 1, FIVE.size()):
			if means.has(FIVE[i]) and means.has(FIVE[j]):
				var d := _rgb_distance(means[FIVE[i]], means[FIVE[j]])
				report["facts"]["globe_sphere_distance %s %s/%s" % [where, FIVE[i], FIVE[j]]] = snappedf(d, 0.001)
				_check(d >= 0.10, "%s: %s and %s distinguishable (RGB distance %.3f >= 0.10)" % [where, FIVE[i], FIVE[j], d])
		for other in ["borderland", "unassigned", "dlc_antarctica"]:
			if means.has(FIVE[i]) and means.has(other):
				var d := _rgb_distance(means[FIVE[i]], means[other])
				_check(d >= 0.06, "%s: %s apart from %s (RGB distance %.3f >= 0.06)" % [where, FIVE[i], other, d])
	var clips := 0
	for child in map.global_layer.get_children():
		if String(child.name).begins_with("SphereClip"):
			clips += 1
			_check(child.clip_children == CanvasItem.CLIP_CHILDREN_AND_DRAW and child.has_node("SphereTint"), "%s: %s clips the sphere texture to its own polygon" % [where, child.name])
	_check(clips == 4, "%s: 4 land rings shared by several spheres use the clipped texture (%d)" % [where, clips])


static func _mean3(image: Image, at: Vector2i) -> Color:
	var sum := Color(0, 0, 0, 0)
	for dy in [-1, 0, 1]:
		for dx in [-1, 0, 1]:
			sum += image.get_pixel(at.x + dx, at.y + dy)
	return sum / 9.0


static func _rgb_distance(a: Color, b: Color) -> float:
	return Vector3(a.r - b.r, a.g - b.g, a.b - b.b).length()


# Relief credit plate: on regional views with relief, inside the frame on the bottom row, clear of the scale
# bar, the date text, view buttons, card, inset, markers, labels and degree labels; names the providers.
func _check_credit_plate(where: String) -> void:
	var plate: Button = map.relief_credit_button
	_check(plate.visible, "%s: relief credit plate visible" % where)
	if not plate.visible:
		return
	var rect := Rect2(plate.position, plate.size)
	_check(Rect2(Vector2.ZERO, map.map_frame.size).encloses(rect), "%s: credit plate inside the map frame %s" % [where, rect])
	_check(plate.text == map_text.t("credit_relief") and plate.text.contains("Mapzen") and plate.text.contains("USGS") and plate.text.contains("NOAA"), "%s: credit plate reads '%s'" % [where, plate.text])
	_check(not rect.intersects(map.SCALE_BAR_RECT), "%s: credit plate clear of the scale bar" % where)
	var font: Font = map.calendar_label.get_theme_font("font")
	var width := font.get_string_size(map.calendar_label.text, HORIZONTAL_ALIGNMENT_LEFT, -1, 10).x
	var date := Rect2(map.calendar_label.position + Vector2(map.calendar_label.size.x - width, 0), Vector2(width, map.calendar_label.size.y))
	_check(_gap(rect, date) >= 4.0, "%s: credit plate %.0f px clear of the date text (>= 4)" % [where, _gap(rect, date)])
	for control in [map.zoom_in_button, map.zoom_out_button, map.globe_button, map.region_button]:
		_check(not rect.intersects(Rect2(control.position, control.size)), "%s: credit plate clear of %s" % [where, control.text])
	if map.route_card.visible:
		_check(not rect.intersects(map._card_local_rect()), "%s: credit plate clear of the route card" % where)
	if map.route_inset.visible:
		_check(not rect.intersects(map.route_inset_rect().grow_individual(0, 0, 2, 2)), "%s: credit plate clear of the inset" % where)
	for button in map.place_buttons.values():
		if button.visible:
			_check(not rect.intersects(Rect2(button.position, button.size)), "%s: credit plate clear of %s" % [where, button.name])
	for entry in map.annotation_label_rects():
		_check(not rect.intersects(entry["rect"]), "%s: credit plate clear of degree label %s" % [where, entry["text"]])
	report["facts"]["credit_plate_rect " + where] = [rect.position.x, rect.position.y, rect.size.x, rect.size.y]


# Real clicks: the plate opens the credits panel with the required attribution; Back closes it, nothing charged.
func _check_credits_panel(language: String) -> void:
	var minutes: int = app.calendar_minutes
	await _click(map.relief_credit_button.get_global_rect().get_center())
	_check(map.credits_overlay.visible, "%s: real click on the relief credit opens the map credits" % language)
	var body: String = map.credits_body.get_parsed_text()
	for word in CREDIT_WORDS:
		_check(body.contains(word), "%s credits: names '%s'" % [language, word])
	_check(map.credits_title.text == map_text.t("credits_title"), "%s credits: title '%s'" % [language, map.credits_title.text])
	await _settle()
	_check(map.credits_body.get_content_height() <= map.credits_body.size.y, "%s credits: body fits without scrolling (%d <= %d px)" % [language, map.credits_body.get_content_height(), map.credits_body.size.y])
	await _capture("map-credits-%s" % language)
	await _click(map.credits_close.get_global_rect().get_center())
	_check(not map.credits_overlay.visible and map.mode == "region" and app.calendar_minutes == minutes, "%s: real click on Back closes the credits, map unchanged, nothing charged" % language)


func _check_browse_nyc_yonkers(language: String) -> void:
	var nyc: Rect2 = (map.place_buttons[NYC].get_node("LabelBackground") as Control).get_global_rect()
	var yon: Rect2 = (map.place_buttons[YONKERS].get_node("LabelBackground") as Control).get_global_rect()
	var nyc_dot: Vector2 = map.marker_position(NYC) + _frame_offset()
	var yon_dot: Vector2 = map.marker_position(YONKERS) + _frame_offset()
	# Diagonally apart (registry sides): New York City below-left of its dot, Yonkers above-right of its own.
	_check(nyc.end.x < nyc_dot.x and nyc.position.y > nyc_dot.y, "%s browse: New York City label below-left of its marker" % language)
	_check(yon.position.x > yon_dot.x and yon.end.y < yon_dot.y, "%s browse: Yonkers label above-right of its marker" % language)
	var gap := _gap(nyc, yon)
	report["facts"]["nyc_yonkers_browse_gap_px " + language] = gap
	_check(gap >= 6.0, "%s browse: New York City / Yonkers plates %.0f px apart (>= 6)" % [language, gap])


func _ui_rects_global() -> Array:
	var offset := _frame_offset()
	var out := []
	for r in map.fixed_ui_rects():
		out.append(Rect2((r as Rect2).position + offset, (r as Rect2).size))
	for button in map.place_buttons.values() + map.region_buttons.values():
		if button.visible:
			out.append(button.get_global_rect())
	if map.route_inset.visible:
		out.append(map.route_inset.get_global_rect())
	if map.route_card.visible:
		out.append(map.route_card.get_global_rect())
	for entry in map.annotation_label_rects():
		out.append(Rect2((entry["rect"] as Rect2).position + offset, (entry["rect"] as Rect2).size))
	return out


# --- Layout and route checks ----------------------------------------------------------

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
		var edge: Rect2 = (button.get_node("LabelEdge") as Control).get_global_rect()
		_check(edge.is_equal_approx(plate), "%s: %s plate edge matches its plate" % [where, place_id])
		for fixed in map.fixed_ui_rects():
			var r: Rect2 = fixed
			_check(not plate.intersects(Rect2(r.position + offset, r.size)), "%s: %s label clear of fixed UI %s" % [where, place_id, r])
			# fixed_ui_rects() are grown by LABEL_GAP; the marker as drawn (dot, party or selection ring) must not touch the control itself.
			var radius := 11.5 if place_id == map.selected_place_id else (9.5 if place_id == app.current_location_id else 5.5)
			_check(not Rect2(marker - Vector2(radius, radius), Vector2(radius, radius) * 2.0).intersects(r.grow(-3.0)), "%s: %s marker (r %.1f) clear of fixed UI %s" % [where, place_id, radius, r.grow(-3.0)])
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
			# Click targets (dot + plate) never overlap, as the global earth map smoke requires.
			var a: Rect2 = map.place_buttons[ids[i]].get_global_rect()
			var b: Rect2 = map.place_buttons[ids[j]].get_global_rect()
			_check(not a.intersects(b), "%s: %s / %s click targets do not overlap" % [where, ids[i], ids[j]])
	if plates.has(NYC) and plates.has(YONKERS):
		report["facts"]["nyc_yonkers_gap_px " + where] = _gap(plates[NYC], plates[YONKERS])
	# With the card open, every visible marker as drawn (selection ring 11.5 px, party ring 9.5 px, else the
	# 5.5 px dot) stays >= 6 px left of the card.
	if map.route_card.visible:
		var card_x: float = map._card_local_rect().position.x
		for place_id in plates:
			var radius := 11.5 if place_id == map.selected_place_id else (9.5 if place_id == app.current_location_id else 5.5)
			var right: float = map.marker_position(place_id).x + radius
			report["facts"]["card_clearance_px %s %s" % [where, place_id]] = snappedf(card_x - right, 0.1)
			_check(right <= card_x - 6.0, "%s: %s marker (r %.1f) %.0f px clear of the card (>= 6)" % [where, place_id, radius, card_x - right])
	if plates.has(DC):
		report["facts"]["washington_footer_clearance_px " + where] = FOOTER_TOP - plates[DC].end.y
	# Degree labels never print over each other (e.g. a latitude label on the longitude row).
	var notes: Array = map.annotation_label_rects()
	for i in notes.size():
		for j in range(i + 1, notes.size()):
			_check(not (notes[i]["rect"] as Rect2).intersects(notes[j]["rect"]), "%s: degree labels %s / %s do not overlap" % [where, notes[i]["text"], notes[j]["text"]])


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
		texts.append_array([map.route_inset.origin_label.text, map.route_inset.dest_label.text, map.route_inset.caption.text, map.route_inset.header.text])
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
	_check(inset.air and inset.dashes(arc, inset.DASH, inset.GAP).size() >= 10, "%s: flight drawn as a dashed line" % where)
	_check((inset.plane_dir.x < 0.0) == (d["lon"] < o["lon"]), "%s: aircraft points toward the destination" % where)
	_check(inset.header.text == map_text.t("inset_title_air") and not inset.header.text.is_empty(), "%s: inset header '%s'" % [where, inset.header.text])
	var rect: Rect2 = map.route_inset_rect()
	_check(Rect2(Vector2.ZERO, map.map_frame.size).encloses(rect.grow_individual(0, 0, 2, 2)), "%s: inset and its shadow inside the map frame" % where)
	_check(rect.end.x <= map._card_local_rect().position.x - 2.0, "%s: inset left of the card" % where)
	for fixed in map.fixed_ui_rects():
		_check(not rect.intersects(fixed), "%s: inset clear of fixed UI %s" % [where, fixed])
	for place_id in map.place_buttons:
		var button: Button = map.place_buttons[place_id]
		if button.visible:
			_check(not rect.grow_individual(0, 0, 2, 2).intersects(Rect2(button.position, button.size)), "%s: inset and shadow clear of %s marker and label" % [where, place_id])
	for entry in map.annotation_label_rects():
		_check(not rect.intersects(entry["rect"]), "%s: inset clear of degree label %s" % [where, entry["text"]])
	_check(not map.route_inset.get_global_rect().intersects(map.depart_button.get_global_rect()), "%s: Depart not covered" % where)
	var option: Dictionary = map.selected_route_option()
	var mode_text: String = map_text.t("mode_" + String(option["mode"]))
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
		_check(not hit and not lr.intersects(Rect2(inset.plane_pt + area.position - Vector2(7, 7), Vector2(14, 14))), "%s: inset label '%s' clear of line and aircraft" % [where, label.text])
	_check(not label_rects[0].intersects(label_rects[1]), "%s: inset labels do not overlap" % where)
	var font: Font = inset.caption.get_theme_font("font")
	var caption_w := font.get_string_size(inset.caption.text, HORIZONTAL_ALIGNMENT_LEFT, -1, 9).x
	_check(6.0 + inset.scale_px + 40.0 + caption_w <= inset.size.x, "%s: caption '%s' (%.0f px) fits beside the scale bar" % [where, inset.caption.text, caption_w])
	_check(absf(inset.scale_px * inset.projection.km_per_pixel() - inset.scale_km) < 0.01, "%s: inset scale bar %d km matches its projection" % [where, int(inset.scale_km)])
	report["facts"]["inset_rect " + where] = [rect.position.x, rect.position.y, rect.size.x, rect.size.y]
	report["facts"]["inset_chord_px " + where] = snappedf(chord, 0.1)


func _check_inset_pixels(image: Image, where: String) -> void:
	if image == null or not map.route_inset.visible:
		return
	var rect: Rect2 = map.route_inset.get_global_rect()
	var gold := 0
	for y in range(int(rect.position.y), int(rect.end.y)):
		for x in range(int(rect.position.x), int(rect.end.x)):
			var c := image.get_pixel(x, y)
			if absf(c.r - ROUTE_GOLD.r) < 0.08 and absf(c.g - ROUTE_GOLD.g) < 0.08 and absf(c.b - ROUTE_GOLD.b) < 0.1:
				gold += 1
	var border := 0
	for x in range(int(rect.position.x) + 2, int(rect.end.x) - 2):
		var c := image.get_pixel(x, int(rect.position.y))
		if absf(c.g - INSET_BORDER.g) < 0.12 and absf(c.b - INSET_BORDER.b) < 0.12:
			border += 1
	report["facts"]["inset_gold_px " + where] = gold
	_check(gold >= 120, "%s: gold flight path rendered in the inset (%d px >= 120)" % [where, gold])
	_check(border >= int(rect.size.x * 0.8), "%s: inset border rendered (%d px)" % [where, border])


# Real mouse input: the marker opens the card, the inset swallows nothing, Cancel closes and charges nothing.
func _check_clicks(start_minutes: int) -> void:
	await _set_language("zh")
	map.enter_region("us_northeast")
	await _settle()
	await _click(map.place_buttons[DC].get_global_rect().get_center())
	_check(map.route_card.visible and map.selected_place_id == DC, "real click on the Washington marker opens its card")
	await _click(map.cancel_button.get_global_rect().get_center())
	_check(not map.route_card.visible and app.travel_preview.is_empty(), "real click on Cancel closes the Washington card")
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
		_check_credit_plate("%s northeast card New York from Chicago" % language)
		var reverse := await _capture("us-northeast-card-nyc-from-chicago-air-%s" % language)
		_check_inset_pixels(reverse, "%s reverse card" % language)
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
		print("NATIVE_MAP_ART_OK %d checks, %d captures" % [checks, report["captures"].size()])
		quit(0)
	else:
		print("NATIVE_MAP_ART_FAIL %d/%d failed" % [failures.size(), checks])
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
