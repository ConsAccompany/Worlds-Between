extends SceneTree

# TEST-ONLY capture + check for the native map legibility pass v03 in game/scripts/scifi_world_map.gd (2026-10-17,
# UNAPPROVED). Forked from the v02 tool (dacc5102); every v02 check stays, adapted where v03 changed the map:
#   - the NYC <-> Chicago route is a compact strip INSIDE the route card (v02: a 196 x 108 inset left of the card,
#     whose east end sat against the card): both endpoints, their names and the dashed great circle are on the card,
#     nothing is drawn on the map under or beside the card, and the strip repeats no mode, time or distance;
#   - re-valued land / lake / sea (land lifted, lakes darker and bluer, brighter shore rims and coast line), measured
#     live against v02's recorded means;
#   - 12 / 10 px map label plates (v02 10 / 9) and 11 px card text, still clear of each other, the card and controls;
#   - the route data and travel rules are unchanged: the same whole-hour trips and arrival dates as v02, preview,
#     confirm and cancel by real clicks, Depart charged once.
#
# Needs a display renderer (no --headless). From the repo root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path to this file>
# Captures are native 640x360 (zh and en) in outputs/, with a checks JSON and a capture manifest beside them. They
# are unapproved evidence for Codex / creator review; map art stays unaccepted and no counter changes.

const MapData := preload("res://scripts/world_map_data.gd")
const TAG := "test-only-v03_20261017-175314-e8b8f8af"
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
const INSET_BORDER := Color("#d4b062")
const RELIEF_JSON := "res://data/world-map/rpg-2-star-ocean-the-second_earth-map_us-east-relief-layer_m2-map-art-native-v03_20261017-175314-e8b8f8af.json"
const V02_RELIEF_JSON := "res://data/world-map/rpg-2-star-ocean-the-second_earth-map_us-east-relief-layer_m2-map-art-native-v02_20261017-165006-dacc5102.json"
const ALLOWED_SOURCES := ["etopo1", "gmted", "srtm"]
const ROUTE_GOLD := Color("#f2d27e")
# v02's measured value means (its checks JSON, same lattice and frames); v03 must separate the families further.
const V02_MEANS := {"northeast browse": {"land": 0.479, "sea": 0.194}, "great lakes card": {"land": 0.474, "lake": 0.347},
	"northeast reverse card": {"land": 0.486, "sea": 0.228}}
# The trips themselves are unchanged from v02 (route data and whole-hour rule): minutes and arrival dates per language.
const TRIP_PINS := {"car %s" % DC: 300, "air %s" % CHICAGO: 360, "air %s" % NYC: 360}
const ARRIVAL_PINS := {"zh": "2537年5月25日", "en": "May 25, 2537"}
# Interior land points per sphere (lon, lat), away from the globe's region badges, status panel and buttons.
# Off the 30-degree graticule, so a grid line never tints a sample.
const SPHERE_SAMPLES := {
	"science": [Vector2(-112, 58), Vector2(-100, 62), Vector2(-98, 31), Vector2(-75, 55)],
	"magic": [Vector2(-56, -10), Vector2(-65, -25), Vector2(-52, -5), Vector2(-68, -40)],
	"wuxia": [Vector2(100, 35), Vector2(80, 25), Vector2(112, 28), Vector2(75, 45)],
	"nature": [Vector2(135, -25), Vector2(125, -22), Vector2(145, -26), Vector2(117, -26)],
	# v03: (10, 49) moved to (18, 50); the 12 px US Northeast plate now reaches 10 deg E on the en globe.
	"culture": [Vector2(20, 10), Vector2(25, -15), Vector2(18, 50), Vector2(4, 20)],
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
	SaveStore.root_path = "user://test-saves/m2-native-map-art-test-only-e8b8f8af"
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
		_check(not map.route_inset.is_visible_in_tree(), "%s northeast browse: no route strip without a card" % language)
		_check_labels("%s northeast browse" % language)
		_check_texel_scale("us_northeast")
		var browse := await _capture("us-northeast-%s" % language)
		_check_values(browse, "%s northeast browse" % language, true)
		_check_grid(browse, "%s northeast browse" % language)
		_check_browse_nyc_yonkers(language)
		_check_credit_plate("%s northeast browse" % language)
		await _check_credits_panel(language)
		# Car route: Washington from New York, both ends on this view, so no strip; the dotted connector shows it.
		map.select_place(DC)
		await _settle()
		_check(map.route_card.visible and not map.route_inset.visible, "%s Washington card: no route strip (both ends on the view)" % language)
		_check(String(map.selected_route_option().get("mode", "")) == "car", "%s Washington card offers a car trip" % language)
		_check_route_rules("%s Washington car card" % language)
		_check_trip_pins(DC, "car", language, "%s Washington car card" % language)
		_check_card_layout("%s Washington card" % language)
		_check_labels("%s northeast card Washington" % language)
		_check_credit_plate("%s northeast card Washington" % language)
		_check_focus_styling("%s Washington card" % language)
		var car := await _capture("us-northeast-card-washington-car-%s" % language)
		_check_connector_pixels(car, NYC, DC, "%s Washington card" % language)
		_check_reticle_pixels(car, DC, "%s Washington card" % language)
		await _check_card_opaque("%s Washington card" % language)
		map.close_route_card()
		# Chicago by air from New York: the origin is in another region, so the strip on the card shows both ends.
		map.select_place(CHICAGO)
		await _settle()
		_choose_mode("air")
		await _settle()
		_check(map.route_inset.is_visible_in_tree(), "%s Chicago air card: route strip visible" % language)
		_check_texel_scale("us_great_lakes")
		_check_route_rules("%s Chicago card" % language)
		_check_trip_pins(CHICAGO, "air", language, "%s Chicago air card" % language)
		_check_strip(NYC, CHICAGO, "%s Chicago card" % language)
		_check_card_layout("%s Chicago card" % language)
		_check_labels("%s great lakes card Chicago" % language)
		_check_credit_plate("%s great lakes card Chicago" % language)
		_check_focus_styling("%s Chicago card" % language)
		var chicago := await _capture("us-great-lakes-card-chicago-air-%s" % language)
		_check_strip_pixels(chicago, NYC, CHICAGO, "%s Chicago card" % language)
		_check_no_route_on_map(chicago, CHICAGO, "%s Chicago card" % language)
		_check_reticle_pixels(chicago, CHICAGO, "%s Chicago card" % language)
		_check_values(chicago, "%s great lakes card" % language, false)
		await _check_card_opaque("%s Chicago card" % language)
		map.close_route_card()
		await _settle()
		_check(not map.route_inset.is_visible_in_tree(), "%s route strip hides when the card closes" % language)
		map.enter_global()
		await _settle()
		_check(not map.relief_credit_button.visible, "%s globe: no relief credit (no relief drawn)" % language)
		var globe := await _capture("globe-%s" % language)
		_check_globe(globe, language)

	map.enter_global()
	await _settle()
	_check(not map.route_inset.is_visible_in_tree(), "no route strip on the globe")
	_check(app.calendar_minutes == start_minutes and calendar_events == 0 and travel_events == 0, "previews, language swaps and cancels charged nothing")
	_check(app.travel_preview.is_empty(), "no pending travel preview after the preview pass")
	await _check_clicks(start_minutes)
	await _travel_and_reverse()
	await _check_save_click()
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
	var data = JSON.parse_string(FileAccess.get_file_as_string(RELIEF_JSON))
	_check(typeof(data) == TYPE_DICTIONARY and data.get("schema", "") == "worlds-between.world-map.relief-layer.v2", "v02 relief JSON loads (schema v2)")
	if typeof(data) != TYPE_DICTIONARY:
		return
	var source: Dictionary = data["sources"][0]
	var families: Array = source["observed_imagery_source_families"]
	_check(not families.is_empty() and families.all(func(f): return ALLOWED_SOURCES.has(f)), "relief tiles' observed sources %s are only SRTM / GMTED2010 / ETOPO1" % [families])
	_check(source["tiles"].size() == 77 and source["tiles"].all(func(t): return t["v01_pin_match"] and not t["imagery_source_families"].is_empty()), "all 77 z7 tiles match the v01 sha256 pins and carry observed source headers")
	for word in ["3DEP", "NED/", "(formerly NED)", "CDEM"]:
		var claims: bool = JSON.stringify(source["attribution_lines"]).contains(word) or JSON.stringify(data["classes"]).contains(word)
		_check(not claims, "relief JSON attribution lines and classes do not claim '%s'" % word)
	_check(String(source.get("attribution_note", "")).contains("omitted"), "relief JSON records why the 3DEP clause is omitted")
	report["facts"]["relief_observed_sources"] = families
	# v03 re-values the palette and re-fits only the route strip layer: the regional layers keep v02's exact grids.
	_check(String(data.get("supersedes", "")).ends_with(V02_RELIEF_JSON.get_file()), "v03 relief JSON names the v02 layer it supersedes")
	_check(source["tiles"].all(func(t): return t.get("v02_record_match", false)), "every tile matches the v02 bake's recorded sha256 and source header")
	var v02 = JSON.parse_string(FileAccess.get_file_as_string(V02_RELIEF_JSON))
	if typeof(v02) == TYPE_DICTIONARY:
		for layer_id in ["us_northeast", "us_great_lakes"]:
			var a: Dictionary = data["layers"][layer_id]
			var b: Dictionary = v02["layers"][layer_id]
			_check(a["bbox_wsen"] == b["bbox_wsen"] and a["grid"]["width"] == b["grid"]["width"] and a["grid"]["height"] == b["grid"]["height"],
				"%s keeps v02's grid (%dx%d over the same lon/lat box)" % [layer_id, a["grid"]["width"], a["grid"]["height"]])
		var v02_roles := {}
		for entry in v02["palette"]:
			v02_roles[entry["role"]] = entry["color"]
		var changed := []
		for entry in data["palette"]:
			if v02_roles.get(entry["role"], null) != entry["color"]:
				changed.append(entry["role"])
		_check(data["palette"].size() == v02["palette"].size() and changed.size() > 0, "same %d palette roles as v02; %d re-valued" % [data["palette"].size(), changed.size()])
		report["facts"]["palette_roles_changed_from_v02"] = changed
	_check(map.PLATE_FONT >= 12 and map.PLATE_SUB_FONT >= 10, "map label plates use %d / %d px text (v02: 10 / 9)" % [map.PLATE_FONT, map.PLATE_SUB_FONT])
	var flat: Dictionary = data["map_flat_colors"]
	_check(Color(flat["land"]).is_equal_approx(map.COLOR_LAND) and Color(flat["ocean"]).is_equal_approx(map.COLOR_OCEAN) and Color(flat["lake"]).is_equal_approx(map.COLOR_LAKE), "relief JSON's flat colours equal the map's COLOR_LAND / COLOR_OCEAN / COLOR_LAKE")
	for layer_id in ["us_northeast", "us_great_lakes", "route_inset"]:
		var relief: Dictionary = MapData.region_relief(layer_id)
		_check(not relief.is_empty(), "%s relief layer loads" % layer_id)
		if relief.is_empty():
			continue
		var grid: Dictionary = relief["grid"]
		_check((relief["texture"] as Texture2D).get_size() == Vector2(grid["width"], grid["height"]), "%s texture is %dx%d" % [layer_id, grid["width"], grid["height"]])
		_check(Color(relief["land_low_color"]).is_equal_approx(map.COLOR_LAND), "%s flat lowland equals the map's COLOR_LAND" % layer_id)
		report["facts"]["relief_grid " + layer_id] = [grid["width"], grid["height"]]
	for region_id in ["us_northeast", "us_great_lakes"]:
		var layer: Node2D = map.region_layers[region_id]
		_check(layer.has_node("Relief") and layer.get_node("Relief").texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST, "%s land layer draws its own relief with nearest filtering" % region_id)
	_check(map.GRID_DOT_STEP >= 3, "graticule is dotted (one dot every %d px)" % map.GRID_DOT_STEP)
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
	report["facts"]["palette"] = {"sea": map.COLOR_OCEAN.to_html(false), "lake": map.COLOR_LAKE.to_html(false), "land": map.COLOR_LAND.to_html(false),
		"coast": map.COLOR_COAST.to_html(false), "grid": map.COLOR_GRID.to_html(true), "grid_dot_step": map.GRID_DOT_STEP}


# One relief texel is one screen pixel at the region's default zoom (texture rect in screen px / texture size).
func _check_texel_scale(region_id: String) -> void:
	var relief: Dictionary = MapData.region_relief(region_id)
	if relief.is_empty():
		return
	var bbox: Array = relief["bbox_wsen"]
	var a: Vector2 = map.view.geo_to_screen(bbox[0], bbox[3])
	var b: Vector2 = map.view.geo_to_screen(bbox[2], bbox[1])
	var texel := (b - a) / Vector2(relief["grid"]["width"], relief["grid"]["height"])
	report["facts"]["texel_px " + region_id] = [snappedf(texel.x, 0.0001), snappedf(texel.y, 0.0001)]
	_check(absf(texel.x - 1.0) <= 0.005 and absf(texel.y - 1.0) <= 0.005, "%s default zoom: one relief texel is %.4f x %.4f screen px (1 +- 0.005)" % [region_id, texel.x, texel.y])


# Mean luma of sea, lake and land on an 8 px lattice of the live frame. A sample counts only away from coasts
# (its 4-neighbours 4 px away share its class) and away from every control, plate, marker and the card.
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
		_check(land_colors.size() >= 12, "%s: land shows relief (%d distinct sampled colours >= 12)" % [where, land_colors.size()])
	if sums["lake"][1] > 0 and sums["sea"][1] > 0:
		_check(means["lake"] - means["sea"] >= 0.08, "%s: lakes %.3f lighter than sea %.3f by >= 0.08" % [where, means["lake"], means["sea"]])
	elif sums["lake"][1] > 0:
		_check(Color(map.COLOR_LAKE).get_luminance() - Color(map.COLOR_OCEAN).get_luminance() >= 0.08, "%s: lake colour lighter than sea colour by >= 0.08" % where)
	# Against v02 (same lattice, same frame): the land / lake step (the hierarchy Codex found too low-contrast at
	# 640x360) must widen by >= 0.06 luma, the land / sea step by >= 0.03 (the brighter v03 sea shore rim lifts the
	# near-coast sea samples, so the sea step widens less; first target 0.04, missed by 0.006 on the reverse card).
	var v02: Dictionary = V02_MEANS.get(where.substr(3), {})
	for water in ["lake", "sea"]:
		if v02.has(water) and sums[water][1] > 0:
			var before: float = v02["land"] - v02[water]
			var after: float = means["land"] - means[water]
			var need := 0.06 if water == "lake" else 0.03
			report["facts"]["land_%s_step_vs_v02 %s" % [water, where]] = {"v02": snappedf(before, 0.001), "v03": snappedf(after, 0.001)}
			_check(after >= before + need, "%s: land - %s step %.3f is >= %.2f above v02's %.3f" % [where, water, after, need, before])


func _class_at(at: Vector2, rings: Array, holes: Array) -> String:
	var geo: Vector2 = map.view.screen_to_geo(at)
	for ring in holes:
		if Geometry2D.is_point_in_polygon(geo, ring["points"]):
			return "lake"
	return "land" if MapData.is_on_land(geo.x, geo.y, rings) else "sea"


# Grid weight: mean luma step between the -72 deg meridian column at sea and the column 3 px beside it, over about one
# degree of latitude, less the same step between two grid-free columns (x+3 vs x+6), so shelf and shore texture
# does not count as grid. The v01r1 solid line measures 0.0445 here (same column, same frame); v02 must stay
# at or below 0.025 and still show (a dot's own step above 0.02).
const V01R1_GRID_WEIGHT := 0.0445

func _check_grid(image: Image, where: String) -> void:
	if image == null:
		return
	var offset := _frame_offset()
	var top: Vector2 = map.view.geo_to_screen(-72.0, 39.6)
	var bottom: Vector2 = map.view.geo_to_screen(-72.0, 38.6)
	var x := int(floorf(top.x))
	var grid_sum := 0.0
	var background_sum := 0.0
	var rows := 0
	var peak := 0.0
	for y in range(int(top.y), int(bottom.y)):
		if not Rect2(Vector2(8, 8), map.map_frame.size - Vector2(16, 16)).has_point(Vector2(x + 6, y)):
			continue
		var at := Vector2i(int(offset.x) + x, int(offset.y) + y)
		var line := image.get_pixelv(at).get_luminance()
		var beside := image.get_pixelv(at + Vector2i(3, 0)).get_luminance()
		var further := image.get_pixelv(at + Vector2i(6, 0)).get_luminance()
		grid_sum += absf(line - beside)
		background_sum += absf(beside - further)
		peak = maxf(peak, absf(line - beside))
		rows += 1
	var weight := (grid_sum - background_sum) / maxf(1.0, rows)
	report["facts"]["grid_weight " + where] = {"excess_mean_step": snappedf(weight, 0.0001), "peak_step": snappedf(peak, 0.0001), "rows": rows, "v01r1_reference": V01R1_GRID_WEIGHT}
	_check(rows >= 40 and weight <= 0.025, "%s: dotted grid weight %.4f <= 0.025 (v01r1 solid line %.4f) over %d rows" % [where, weight, V01R1_GRID_WEIGHT, rows])
	_check(peak > 0.02, "%s: grid still visible (peak step %.3f > 0.02)" % [where, peak])


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
	if map.route_inset.is_visible_in_tree():
		_check(not rect.intersects(map.route_inset_rect()), "%s: credit plate clear of the route strip" % where)
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
	for word in ["3DEP", "NED", "CDEM"]:
		_check(not body.contains(word), "%s credits: no claim of '%s' (not in any tile used)" % [language, word])
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
	if map.route_inset.is_visible_in_tree():
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


# Card rules: whole hours, date-only arrival, generic modes, no airport names anywhere on the card or its strip.
func _check_route_rules(where: String) -> void:
	_check(String(map.route_state.get("status", "")) == "ready", "%s: route ready" % where)
	var clock := RegEx.create_from_string("\\d{1,2}:\\d{2}")
	for option in map.route_state.get("options", []):
		_check(int(option["total_minutes"]) > 0 and int(option["total_minutes"]) % 60 == 0, "%s: %s charges whole hours (%d min)" % [where, option["option_id"], option["total_minutes"]])
		_check(clock.search(String(option["arrival_text"])) == null and clock.search(String(option["duration_text"])) == null, "%s: %s arrival '%s' and duration '%s' show no clock time" % [where, option["option_id"], option["arrival_text"], option["duration_text"]])
		_check(["car", "air", "air_car"].has(String(option["mode"])), "%s: %s mode is generic (%s)" % [where, option["option_id"], option["mode"]])
	var texts := [map.card_title.text, map.card_subtitle.text, map.card_kind.text, map.card_coords.text, map.card_from.text, map.card_route.text]
	for child in map.card_options.get_children():
		texts.append((child as Button).text)
	if map.route_inset.is_visible_in_tree():
		texts.append_array([map.route_inset.origin_label.text, map.route_inset.dest_label.text])
	var joined := "\n".join(texts)
	for word in FORBIDDEN:
		_check(not joined.contains(word), "%s: no '%s' on the card or strip" % [where, word])


# Route strip on the card: a child of the route card (never of the map frame), between the origin line and the trip
# options; both endpoints sit on their own coordinates with room around their badges, both names are on the strip and
# clear of the line, and the strip carries no mode, distance, time or clock text (the card's option line has those).
func _check_strip(origin_id: String, dest_id: String, where: String) -> void:
	var strip = map.route_inset
	_check(map.route_card.is_ancestor_of(strip) and not map.map_frame.is_ancestor_of(strip), "%s: route strip is part of the card, not of the map" % where)
	var map_insets: Array = map.map_frame.find_children("RouteInset*", "", true, false)
	_check(map_insets.is_empty(), "%s: no route inset drawn on the map frame (%d found)" % [where, map_insets.size()])
	var card: Rect2 = map.route_card.get_global_rect()
	var rect: Rect2 = strip.get_global_rect()
	_check(card.grow(-8).encloses(rect), "%s: strip %s inside the card's content area %s" % [where, rect, card.grow(-8)])
	_check(rect.position.y >= map.card_from.get_global_rect().end.y and rect.end.y <= map.card_options.get_global_rect().position.y, "%s: strip sits between the origin line and the trip options" % where)
	_check(not rect.intersects(map.depart_button.get_global_rect()) and not rect.intersects(map.cancel_button.get_global_rect()), "%s: Depart and Cancel not covered" % where)
	var o: Dictionary = map.find_place(origin_id)
	var d: Dictionary = map.find_place(dest_id)
	var arc: PackedVector2Array = strip.arc
	_check(arc[0].distance_to(strip.projection.geo_to_screen(o["lon"], o["lat"])) < 0.01 and strip.origin_pt.distance_to(arc[0]) < 0.01, "%s: line starts at %s coordinates" % [where, origin_id])
	_check(arc[arc.size() - 1].distance_to(strip.projection.geo_to_screen(d["lon"], d["lat"])) < 0.01 and strip.dest_pt.distance_to(arc[arc.size() - 1]) < 0.01, "%s: line ends at %s coordinates" % [where, dest_id])
	var map_area := Rect2(Vector2.ZERO, strip.area.size)
	# Both ends clearly visible: each badge (ring and reticle, 8 px) at least 10 px inside the strip's map edge.
	for end in [["origin", strip.origin_pt], ["destination", strip.dest_pt]]:
		var p: Vector2 = end[1]
		var margin := minf(minf(p.x, p.y), minf(map_area.size.x - p.x, map_area.size.y - p.y))
		report["facts"]["strip_%s_edge_margin_px %s" % [end[0], where]] = snappedf(margin, 0.1)
		_check(margin >= 18.0, "%s: %s endpoint %.1f px inside the strip edge (>= 18: badge 8 px + 10 px clear)" % [where, end[0], margin])
	var inside := true
	for p in arc:
		inside = inside and map_area.grow(-6).has_point(p)
	_check(inside, "%s: line stays >= 6 px inside the strip map" % where)
	var chord: float = arc[0].distance_to(arc[arc.size() - 1])
	_check(chord >= 120.0, "%s: endpoints %.0f px apart (>= 120; v02 inset 156)" % [where, chord])
	_check(strip.air and strip.dashes(arc, strip.DASH, strip.GAP).size() >= 10, "%s: flight drawn as a dashed line" % where)
	_check((strip.plane_dir.x < 0.0) == (d["lon"] < o["lon"]), "%s: aircraft points toward the destination" % where)
	_check(strip.origin_label.text == MapData.text(o, "map_label", app.language) and strip.dest_label.text == MapData.text(d, "map_label", app.language), "%s: strip names '%s' -> '%s'" % [where, strip.origin_label.text, strip.dest_label.text])
	var digits := RegEx.create_from_string("\\d")
	for label in [strip.origin_label, strip.dest_label]:
		_check(digits.search(label.text) == null, "%s: strip name '%s' carries no number (no time or distance breakdown)" % [where, label.text])
	var strip_texts: Array = strip.find_children("*", "Label", true, false)
	_check(strip_texts.size() == 2, "%s: the strip's only text nodes are the two names (%d)" % [where, strip_texts.size()])
	var area_rect: Rect2 = strip.area
	var label_rects := []
	var ring_rects := [Rect2(strip.origin_pt + area_rect.position - Vector2(8, 8), Vector2(16, 16)), Rect2(strip.dest_pt + area_rect.position - Vector2(8.5, 8.5), Vector2(17, 17))]
	# As drawn: the origin's gold ring (6.5 px, 1.5 px stroke), the destination's white ring and its four gold ticks
	# (5 to 8 px, 1.5 px stroke).
	var badge_points := []
	for center in [strip.origin_pt + area_rect.position, strip.dest_pt + area_rect.position]:
		for i in 32:
			badge_points.append(center + Vector2.from_angle(TAU * i / 32.0) * 7.25)
		for dir in [Vector2.UP, Vector2.DOWN, Vector2.LEFT, Vector2.RIGHT]:
			for t in [5.0, 6.5, 8.0]:
				badge_points.append(center + dir * t)
	var plane := Rect2(strip.plane_pt + area_rect.position - Vector2(8, 8), Vector2(16, 16))
	for label in [strip.origin_label, strip.dest_label]:
		var lr := Rect2(label.position, label.size)
		label_rects.append(lr)
		_check(area_rect.encloses(lr), "%s: strip name '%s' inside the strip map" % [where, label.text])
		var hit := false
		for p in arc:
			# The line is 3 px gold on a 5 px casing: 2.5 px either side of the path.
			hit = hit or lr.grow(2.5).has_point(p + area_rect.position)
		_check(not hit and not lr.intersects(plane), "%s: strip name '%s' clear of the line (with its casing) and the aircraft" % [where, label.text])
		var on_badge := false
		for bp in badge_points:
			on_badge = on_badge or lr.grow(0.75).has_point(bp)
		_check(not on_badge, "%s: strip name '%s' clear of the endpoint badges as drawn" % [where, label.text])
		_check(label.get_theme_font_size("font_size") >= 11, "%s: strip name '%s' at %d px (v02 inset 10)" % [where, label.text, label.get_theme_font_size("font_size")])
	_check(not label_rects[0].intersects(label_rects[1]), "%s: strip names do not overlap" % where)
	var scale: Rect2 = strip.scale_rect()
	_check(scale.has_area() and area_rect.encloses(scale), "%s: strip scale bar plate %s inside the strip map" % [where, scale])
	for other in label_rects + ring_rects:
		_check(not scale.intersects(other), "%s: scale bar plate clear of %s" % [where, other])
	var on_line := false
	for p in arc:
		on_line = on_line or scale.grow(2.5).has_point(p + area_rect.position)
	_check(not on_line, "%s: scale bar plate clear of the line" % where)
	_check(absf(strip.scale_px * strip.projection.km_per_pixel() - strip.scale_km) < 0.01, "%s: strip scale bar %d km matches its projection" % [where, int(strip.scale_km)])
	var sheet: Node = strip.land.get_node_or_null("InsetRelief")
	_check(sheet != null and sheet.texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST, "%s: strip draws its own relief layer, nearest filtered" % where)
	var relief: Dictionary = MapData.region_relief("route_inset")
	if not relief.is_empty():
		var bbox: Array = relief["bbox_wsen"]
		var span: Vector2 = strip.projection.geo_to_screen(bbox[2], bbox[1]) - strip.projection.geo_to_screen(bbox[0], bbox[3])
		var texel := span / Vector2(relief["grid"]["width"], relief["grid"]["height"])
		report["facts"]["strip_texel_px " + where] = [snappedf(texel.x, 0.0001), snappedf(texel.y, 0.0001)]
		_check(absf(texel.x - 1.0) <= 0.005 and absf(texel.y - 1.0) <= 0.005, "%s: one strip relief texel is %.4f x %.4f px" % [where, texel.x, texel.y])
	report["facts"]["strip_rect " + where] = [rect.position.x, rect.position.y, rect.size.x, rect.size.y]
	report["facts"]["strip_chord_px " + where] = snappedf(chord, 0.1)


# Rendered strip: the gold dashed path, the gold frame, and both endpoint badges (the origin's gold ring, the
# destination's white ring) are on screen.
func _check_strip_pixels(image: Image, origin_id: String, dest_id: String, where: String) -> void:
	if image == null or not map.route_inset.is_visible_in_tree():
		return
	var strip = map.route_inset
	var rect: Rect2 = strip.get_global_rect()
	var gold := 0
	for y in range(int(rect.position.y), int(rect.end.y)):
		for x in range(int(rect.position.x), int(rect.end.x)):
			var c := image.get_pixel(x, y)
			if absf(c.r - ROUTE_GOLD.r) < 0.08 and absf(c.g - ROUTE_GOLD.g) < 0.08 and absf(c.b - ROUTE_GOLD.b) < 0.1:
				gold += 1
	var border := 0
	for x in range(int(rect.position.x) + 2, int(rect.end.x) - 2):
		var c := image.get_pixel(x, int(rect.position.y))
		if absf(c.r - INSET_BORDER.r) < 0.08 and absf(c.g - INSET_BORDER.g) < 0.08 and absf(c.b - INSET_BORDER.b) < 0.08:
			border += 1
	report["facts"]["strip_gold_px " + where] = gold
	_check(gold >= 200, "%s: gold flight path rendered in the strip (%d px >= 200)" % [where, gold])
	_check(border >= int(rect.size.x * 0.8), "%s: gold strip frame rendered (%d of %d px on the top edge)" % [where, border, int(rect.size.x)])
	var base: Vector2 = rect.position + strip.area.position
	var origin_ring := _ring_hits(image, base + strip.origin_pt, 6.5, map.COLOR_HERE)
	var dest_ring := _ring_hits(image, base + strip.dest_pt, 6.5, Color.WHITE)
	report["facts"]["strip_endpoint_ring_hits " + where] = {origin_id: origin_ring, dest_id: dest_ring}
	_check(origin_ring >= 10, "%s: origin %s badge (gold ring) rendered on the strip (%d of 16 samples)" % [where, origin_id, origin_ring])
	_check(dest_ring >= 8, "%s: destination %s badge (white ring) rendered on the strip (%d of 16 samples)" % [where, dest_id, dest_ring])


func _ring_hits(image: Image, center: Vector2, radius: float, color: Color) -> int:
	var hits := 0
	for i in 16:
		var a := TAU * float(i) / 16.0
		var best := 9.0
		for dr in [-0.6, 0.0, 0.6]:
			var c := image.get_pixelv(Vector2i((center + Vector2(cos(a), sin(a)) * (radius + dr)).floor()))
			best = minf(best, absf(c.r - color.r) + absf(c.g - color.g) + absf(c.b - color.b))
		if best < 0.3:
			hits += 1
	return hits


# Nothing of the off-view trip is drawn on the map itself: no route gold anywhere in the map frame outside the card,
# except the selected marker's reticle ticks and gold plate edge.
func _check_no_route_on_map(image: Image, selected_id: String, where: String) -> void:
	if image == null:
		return
	var frame: Rect2 = map.map_frame.get_global_rect()
	var card: Rect2 = map.route_card.get_global_rect().grow(3)
	var marker: Vector2 = map.marker_position(selected_id) + frame.position
	var plate: Rect2 = (map.place_buttons[selected_id] as Control).get_global_rect().grow(1)
	# The date (and other fixed controls) share the gold; they are not route.
	var fixed := []
	for r in map.fixed_ui_rects():
		fixed.append(Rect2((r as Rect2).position + frame.position, (r as Rect2).size))
	var gold := 0
	for y in range(int(frame.position.y), int(frame.end.y)):
		for x in range(int(frame.position.x), int(frame.end.x)):
			var at := Vector2(x, y)
			if card.has_point(at) or plate.has_point(at) or at.distance_to(marker) <= 13.0:
				continue
			var in_fixed := false
			for r in fixed:
				in_fixed = in_fixed or (r as Rect2).has_point(at)
			if in_fixed:
				continue
			var c := image.get_pixel(x, y)
			if absf(c.r - ROUTE_GOLD.r) < 0.06 and absf(c.g - ROUTE_GOLD.g) < 0.06 and absf(c.b - ROUTE_GOLD.b) < 0.08:
				gold += 1
	report["facts"]["map_route_gold_px_outside_card " + where] = gold
	_check(gold <= 6, "%s: no route line on the map beside or under the card (%d gold px outside the card and marker)" % [where, gold])


# The trip itself is unchanged from v02: the same whole-hour minutes and the arrival date only, for this language.
func _check_trip_pins(place_id: String, mode: String, language: String, where: String) -> void:
	var option: Dictionary = map.selected_route_option()
	var pin: int = TRIP_PINS.get("%s %s" % [mode, place_id], -1)
	report["facts"]["trip %s" % where] = {"mode": option.get("mode", ""), "total_minutes": option.get("total_minutes", -1), "arrival_text": option.get("arrival_text", "")}
	_check(String(option.get("mode", "")) == mode and int(option.get("total_minutes", -1)) == pin, "%s: %s trip charges %d min (pinned %d, as v02)" % [where, mode, option.get("total_minutes", -1), pin])
	_check(String(option.get("arrival_text", "")) == ARRIVAL_PINS[language], "%s: arrival '%s' is the date only, as v02 ('%s')" % [where, option.get("arrival_text", ""), ARRIVAL_PINS[language]])
	var button_text := ""
	for child in map.card_options.get_children():
		if (child as Button).button_pressed:
			button_text = (child as Button).text
	_check(button_text == map.route_option_text(option), "%s: card option line is the unchanged route_option_text '%s'" % [where, button_text.replace("\n", " | ")])


# Card: CARD_RECT-sized, 11 px text (10 px coordinates), kind and coordinates on one row when both fit.
func _check_card_layout(where: String) -> void:
	var card: Rect2 = map.route_card.get_global_rect()
	_check(card.position.is_equal_approx(map.CARD_RECT.position) and card.size.y <= map.CARD_RECT.size.y + 0.5 and is_equal_approx(card.size.x, map.CARD_RECT.size.x), "%s: card stays at CARD_RECT %s (got %s)" % [where, map.CARD_RECT, card])
	# These cards have room: the overflow fallback (_fit_card_height) keeps the coordinates and origin lines.
	_check(map.card_coords.visible and map.card_from.visible, "%s: coordinates and origin lines shown (no overflow fallback)" % where)
	for entry in [[map.card_subtitle, 10], [map.card_kind, 11], [map.card_from, 11], [map.card_coords, 10]]:
		_check((entry[0] as Label).get_theme_font_size("font_size") >= entry[1], "%s: card text '%s' at >= %d px" % [where, (entry[0] as Label).text.get_slice("\n", 0), entry[1]])
	for child in map.card_options.get_children():
		_check((child as Button).get_theme_font_size("font_size") >= 11, "%s: option line at >= 11 px" % where)
	var kind: Rect2 = map.card_kind.get_global_rect()
	var coords: Rect2 = map.card_coords.get_global_rect()
	var font: Font = map.card_kind.get_theme_font("font")
	var fits: bool = font.get_string_size(map.card_kind.text, HORIZONTAL_ALIGNMENT_LEFT, -1, 11).x + 6.0 + coords.size.x <= map.CARD_RECT.size.x - 16.0
	if fits:
		_check(coords.position.y < kind.end.y and coords.end.y > kind.position.y and coords.position.x >= kind.position.x and coords.end.x <= card.end.x - 7.0, "%s: kind and coordinates share one row" % where)
	else:
		_check(coords.position.y >= kind.end.y - 0.5, "%s: long kind wraps, coordinates flow under it" % where)
	_check(card.grow(-6).encloses(kind) and card.grow(-6).encloses(coords), "%s: kind and coordinates inside the card" % where)
	report["facts"]["card_rows " + where] = {"kind": [kind.position.y, kind.size.y], "coords": [coords.position.y, coords.size.y], "from": map.card_from.get_global_rect().position.y,
		"options": map.card_options.get_global_rect().position.y, "depart": map.depart_button.get_global_rect().position.y}


# The card still hides the map completely (as the route-card readability check requires): its pixels are identical with
# the map frame hidden, strip included.
func _check_card_opaque(where: String) -> void:
	var with_map := await _grab()
	map.map_frame.visible = false
	var without_map := await _grab()
	map.map_frame.visible = true
	await _settle()
	var card: Rect2 = map.route_card.get_global_rect()
	var differing := 0
	for y in range(int(card.position.y), int(card.end.y)):
		for x in range(int(card.position.x), int(card.end.x)):
			if with_map.get_pixel(x, y) != without_map.get_pixel(x, y):
				differing += 1
	_check(differing == 0, "%s: no map pixel shows through the card, strip included (%d differ)" % [where, differing])


func _grab() -> Image:
	await _settle()
	await RenderingServer.frame_post_draw
	return root.get_texture().get_image()


# Card focus: the selected place's plate edge and accent turn gold; other visible places' names step back to the
# subtext colour; their buttons stay visible and clickable.
func _check_focus_styling(where: String) -> void:
	for place_id in map.place_buttons:
		var button: Button = map.place_buttons[place_id]
		if not button.visible:
			continue
		var edge := (button.get_node("LabelEdge") as Panel).get_theme_stylebox("panel") as StyleBoxFlat
		var primary := (button.get_node("Primary") as Label).get_theme_color("font_color")
		if place_id == map.selected_place_id:
			_check(edge.border_color.is_equal_approx(map.COLOR_HERE) and primary.is_equal_approx(map.COLOR_TEXT), "%s: selected %s plate has the gold edge and full-white name" % [where, place_id])
		else:
			_check(edge.border_color.is_equal_approx(map.COLOR_PLATE_EDGE) and primary.is_equal_approx(map.COLOR_SUBTEXT), "%s: %s name stepped back while the card is open" % [where, place_id])
			_check(not button.disabled and button.mouse_filter != Control.MOUSE_FILTER_IGNORE, "%s: %s stays clickable" % [where, place_id])


# Selection reticle: gold tick pixels above, below and beside the selected marker (within its 11.5 px radius).
func _check_reticle_pixels(image: Image, place_id: String, where: String) -> void:
	if image == null:
		return
	var at: Vector2 = map.marker_position(place_id) + _frame_offset()
	var gold := 0
	for d in [Vector2(0, -10), Vector2(0, 10), Vector2(-10, 0), Vector2(10, 0)]:
		var c := image.get_pixelv(Vector2i((at + d).floor()))
		if absf(c.r - map.COLOR_HERE.r) < 0.12 and absf(c.g - map.COLOR_HERE.g) < 0.12 and absf(c.b - map.COLOR_HERE.b) < 0.15:
			gold += 1
	_check(gold >= 3, "%s: selection reticle ticks drawn around %s (%d of 4)" % [where, place_id, gold])


# Car trip with both ends on the view: a dotted gold connector between the two markers on the main map.
func _check_connector_pixels(image: Image, from_id: String, to_id: String, where: String) -> void:
	if image == null:
		return
	var a: Vector2 = map.marker_position(from_id) + _frame_offset()
	var b: Vector2 = map.marker_position(to_id) + _frame_offset()
	var gold := 0
	var samples := 0
	for i in range(1, 40):
		var p := a.lerp(b, 0.1 + 0.8 * float(i) / 40.0)
		samples += 1
		for dy in [-1, 0, 1]:
			var c := image.get_pixelv(Vector2i(p.floor()) + Vector2i(0, dy))
			if absf(c.r - ROUTE_GOLD.r) < 0.1 and absf(c.g - ROUTE_GOLD.g) < 0.1 and absf(c.b - ROUTE_GOLD.b) < 0.12:
				gold += 1
				break
	report["facts"]["connector_gold_samples " + where] = [gold, samples]
	_check(gold >= 12 and gold < samples, "%s: dotted car connector drawn (%d of %d samples gold, gaps present)" % [where, gold, samples])


# Real click on the header Save button opens the save screen in save mode, set to return to the map.
func _check_save_click() -> void:
	await _open_map()
	var minutes: int = app.calendar_minutes
	await _click(map.save_button.get_global_rect().get_center())
	await _settle()
	var scene_path := current_scene.scene_file_path if current_scene != null else ""
	_check(scene_path == "res://scenes/save_screen.tscn" and app.save_screen_mode == "save" and app.save_return_scene == "res://scenes/scifi_world_map.tscn", "real click on Save opens the save screen in save mode (%s)" % scene_path)
	_check(app.calendar_minutes == minutes, "opening Save charges no time")
	map = null


# Real mouse input: the marker opens the card, the route strip swallows nothing, Cancel closes and charges nothing.
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
	_check(map.route_inset.is_visible_in_tree(), "route strip appears on the card after a real marker click")
	var preview_before: Dictionary = app.travel_preview.duplicate(true)
	var option_before: String = map.selected_option_id
	await _click(map.route_inset.get_global_rect().get_center())
	_check(map.route_card.visible and app.travel_preview == preview_before and map.selected_option_id == option_before, "click on the route strip changes no route state")
	_check(map.view.center.is_equal_approx(center_before), "click on the route strip does not pan the map")
	await _click(map.cancel_button.get_global_rect().get_center())
	_check(not map.route_card.visible and app.travel_preview.is_empty() and not map.route_inset.is_visible_in_tree(), "real click on Cancel closes the card, clears the preview and hides the strip")
	_check(app.calendar_minutes == start_minutes and app.current_location_id == NYC, "Cancel charges no time")


# Real Depart click: the trip is charged once in whole hours; then the reverse card shows the strip from Chicago.
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
		_check(map.route_inset.is_visible_in_tree(), "%s Chicago -> New York card: route strip visible" % language)
		if map.route_inset.is_visible_in_tree():
			_check_route_rules("%s reverse card" % language)
			_check_trip_pins(NYC, "air", language, "%s reverse card" % language)
			_check_strip(CHICAGO, NYC, "%s reverse card" % language)
			_check_card_layout("%s reverse card" % language)
		_check_labels("%s northeast card New York from Chicago" % language)
		_check_credit_plate("%s northeast card New York from Chicago" % language)
		_check_focus_styling("%s reverse card" % language)
		var reverse := await _capture("us-northeast-card-nyc-from-chicago-air-%s" % language)
		_check_strip_pixels(reverse, CHICAGO, NYC, "%s reverse card" % language)
		_check_no_route_on_map(reverse, NYC, "%s reverse card" % language)
		_check_reticle_pixels(reverse, NYC, "%s reverse card" % language)
		_check_values(reverse, "%s northeast reverse card" % language, true)
		map.close_route_card()
		await _settle()
	_check(app.calendar_minutes == minutes_before + charged, "reverse previews charged nothing")


func _finish() -> void:
	if map != null and is_instance_valid(map):
		map.close_route_card()
	app.language = "zh"
	report["failures"] = failures
	report["checks_total"] = checks
	var manifest := {"tag": TAG, "status": "UNAPPROVED test-only captures; map-art gate open; no counter changed", "resolution": "640x360 native", "captures": []}
	for capture_name in report["captures"]:
		var capture_path := ProjectSettings.globalize_path(OUT_DIR).path_join(capture_name)
		manifest["captures"].append({"file": capture_name, "sha256": FileAccess.get_sha256(capture_path)})
	var manifest_file := FileAccess.open(ProjectSettings.globalize_path(OUT_DIR).path_join("%s_capture-manifest_%s.json" % [PREFIX, TAG]), FileAccess.WRITE)
	manifest_file.store_string(JSON.stringify(manifest, "  ") + "\n")
	manifest_file.close()
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
