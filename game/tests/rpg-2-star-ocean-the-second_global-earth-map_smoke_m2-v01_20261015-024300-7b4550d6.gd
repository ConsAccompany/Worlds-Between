extends SceneTree

# Global Earth map smoke: projection math, geodata integrity, place positions, zoom
# between globe and region, route card with the AppState route core, fallback without
# that core (no numbers, no departure), and the existing save / growth / field-log flows.
# From the repository root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --headless --path game \
#     --script res://tests/rpg-2-star-ocean-the-second_global-earth-map_smoke_m2-v01_20261015-024300-7b4550d6.gd

const GeoProjection := preload("res://scripts/world_geo_projection.gd")
const MapData := preload("res://scripts/world_map_data.gd")
const RouteAdapter := preload("res://scripts/world_map_route_adapter.gd")
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
# 2026-10-15: US science sphere. The first three share the US Northeast view; Chicago has its own.
const PLACE_IDS := ["earth.us.ny.new-york-city", "earth.us.ny.yonkers-outskirts", "earth.us.dc.washington-ruins"]
const CHICAGO := "earth.us.il.chicago"
const NE := "us_northeast"
const LAKES := "us_great_lakes"
# Natural Earth 10m coastlines are generalised; a shoreline place may sit just off the polygon.
const COAST_TOLERANCE_KM := 2.0

var checks := 0
# Loaded at run time: the map script references the AppState autoload, which a --script
# entry point cannot see at its own compile time.
var MapScript: GDScript


# Provider without the route core: places still come from the travel data, no numbers, no departure.
class LegacyProvider:
	extends RefCounted
	var current_destination_id := "scifi.city"


# Test-only fixture so air formatting and unverified handling can be checked before the core
# has an air route. These numbers never reach the game.
class FixtureProvider:
	extends RefCounted
	var current_location_id := "earth.us.ny.new-york-city"
	var current_destination_id := "scifi.city"
	var calendar_minutes := 0
	var confirmed := []

	func travel_location_ids(_region_id: String) -> Array: return Array(MapData.travel_data().initial_location_ids())
	func travel_location(id: String) -> Dictionary: return MapData.travel_data().location(id).duplicate(true)
	func travel_location_name(id: String) -> String: return String(MapData.travel_data().location(id)["names"]["en"])
	func travel_route_options(_from_id: String, _to_id: String) -> Array:
		return [
			{"option_id": "fixture.air", "available": true, "mode": "air_car", "total_minutes": 250, "road_distance_km": 12.5, "air_distance_km": 1000.0, "estimate": false, "via_location_ids": []},
			{"option_id": "fixture.unverified", "available": false, "mode": "car", "total_minutes": -1, "road_distance_km": null, "air_distance_km": null},
		]
	func travel_arrival_preview(total_minutes: int) -> Dictionary: return {"text": "FIXTURE-DATE", "time_text": "+%d" % total_minutes}
	func preview_travel(_to_id: String, _option_id: String) -> Dictionary: return {"ok": true, "kind": "travel", "option_id": "fixture.air"}
	func cancel_travel_preview() -> void: pass
	func confirm_travel(to_id: String, option_id: String) -> bool:
		confirmed.append([to_id, option_id])
		return true
	func enter_current_location_scene() -> bool: return true
	func calendar_date_text_at(_minutes: int) -> String: return "FIXTURE-DATE"
	func calendar_time_text_at(_minutes: int) -> String: return "00:00"
	func travel_duration_text(minutes: int) -> String: return "%d min" % minutes


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	MapScript = load("res://scripts/scifi_world_map.gd")
	if not _projection_checks() or not _geodata_checks() or not _adapter_checks():
		return
	if not await _ui_checks():
		return
	print("GLOBAL_EARTH_MAP_SMOKE_OK checks=%d" % checks)
	quit(0)


func _projection_checks() -> bool:
	var globe := GeoProjection.new(0.0, 0.0)
	globe.configure(Rect2(0, 0, 640, 268), Rect2(-180, -90, 360, 180), false, 7.0)
	var world := globe.visible_geo_rect()
	if not _check(world.position.x <= -180.0 and world.end.x >= 180.0 and world.position.y <= -90.0 and world.end.y >= 90.0, "globe minimum zoom shows the full Earth extent"):
		return false
	if not _check(globe.geo_to_screen(-180, 90).is_equal_approx(Vector2(52.0, 0.0)) and globe.geo_to_screen(180, -90).is_equal_approx(Vector2(588.0, 268.0)), "plate carrée corners fill a 2:1 frame"):
		return false
	for sample in [Vector2(121.4, 31.2), Vector2(-74.0, 40.7), Vector2(151.2, -33.9), Vector2(0, 0)]:
		var back := globe.screen_to_geo(globe.geo_to_screen(sample.x, sample.y))
		if not _check(back.distance_to(sample) < 0.0001, "round trip " + str(sample)):
			return false
	var anchor := globe.geo_to_screen(121.4, 31.2)
	globe.zoom_at(anchor, 3.0)
	if not _check(globe.geo_to_screen(121.4, 31.2).distance_to(anchor) < 0.01 and is_equal_approx(globe.scale, globe.min_scale * 3.0), "zoom keeps the point under the cursor"):
		return false
	var region := GeoProjection.new(121.0, 30.8)
	if not _check(is_equal_approx(region.x_factor, cos(deg_to_rad(30.8))), "regional projection uses its standard parallel"):
		return false
	var nyc := _core_coordinates(PLACE_IDS[0])
	var yonkers := _core_coordinates(PLACE_IDS[1])
	var dc := _core_coordinates(PLACE_IDS[2])
	var nyc_yk := GeoProjection.great_circle_km(nyc.x, nyc.y, yonkers.x, yonkers.y)
	var nyc_dc := GeoProjection.great_circle_km(nyc.x, nyc.y, dc.x, dc.y)
	if not _check(nyc_yk > 15.0 and nyc_yk < 35.0 and nyc_dc > 300.0 and nyc_dc < 350.0, "travel-data places are real-distance plausible (%.1f km, %.1f km)" % [nyc_yk, nyc_dc]):
		return false
	if not _check(GeoProjection.format_lat_lon(-77.009, 38.890) == "38.890°N  77.009°W" and GeoProjection.format_lat_lon(119.991, 30.396) == "30.396°N  119.991°E", "coordinate text in both hemispheres"):
		return false
	return _check(MapScript.degree_text(-74, "E", "W") == "74°W" and MapScript.degree_text(41, "N", "S") == "41°N" and MapScript.degree_text(0, "E", "W") == "0°E", "grid labels name W longitudes")


func _geodata_checks() -> bool:
	var data := MapData.geodata()
	var repo := ProjectSettings.globalize_path("res://").path_join("..").simplify_path()
	for source in data["sources"]:
		# Sources not kept in the repository are checked for upstream URL and hash below.
		if source.get("path") == null:
			continue
		var bytes := FileAccess.get_file_as_bytes(repo.path_join(source["path"]))
		if not _check(not bytes.is_empty() and _text_lf_sha256(bytes) == source["sha256"], "source hash matches " + String(source["id"])):
			return false
	var global_rings := MapData.global_land_rings()
	for source in data["sources"]:
		if source.get("path") == null:
			if not _check(String(source.get("upstream", "")).begins_with("https://") and String(source.get("sha256", "")).length() == 64 and source.get("retained_copy") == false, "unretained source names its upstream and hash: " + String(source["id"])):
				return false
	var region_rings := MapData.region_land_rings(MapData.geodata_key(NE))
	if not _check(MapData.geodata_key(NE) == "us_east" and MapData.geodata_key(LAKES) == "us_east", "both US regions draw from the us_east layer"):
		return false
	if not _check(global_rings.size() >= 100 and region_rings.size() >= 5 and MapData.region_roads("us_east").is_empty(), "land layers loaded; the US layer has no road subset yet"):
		return false
	var west := 0.0
	var east := 0.0
	for ring in global_rings:
		for point in ring["points"]:
			west = minf(west, point.x)
			east = maxf(east, point.x)
		if not _check(not Geometry2D.triangulate_polygon(ring["points"]).is_empty(), "global ring triangulates"):
			return false
	if not _check(west <= -179.9 and east >= 179.9, "global land spans the antimeridian"):
		return false
	for id in PLACE_IDS + [CHICAGO]:
		var at := _core_coordinates(id)
		if not _check(MapData.is_on_land(at.x, at.y, region_rings) or _km_to_land(at, region_rings) < COAST_TOLERANCE_KM, "on or within %.0f km of 10m land: %s" % [COAST_TOLERANCE_KM, id]):
			return false
	if not _check(not MapData.is_on_land(-70.0, 39.0, region_rings) and not MapData.is_on_land(-87.0, 43.0, region_rings) and not MapData.is_on_land(-81.5, 42.2, region_rings) and MapData.is_on_land(-77.0, 38.9, region_rings), "Atlantic, Lake Michigan and Lake Erie are water; Washington is land"):
		return false
	if not _check(not MapData.is_on_land(-150.0, 0.0, global_rings) and MapData.is_on_land(20.0, 10.0, global_rings), "global sea and land samples"):
		return false
	return true


func _adapter_checks() -> bool:
	var legacy := RouteAdapter.new(LegacyProvider.new())
	var pending := legacy.preview("earth.us.dc.washington-ruins")
	if not _check(not legacy.api_available() and not legacy.api_problems().is_empty() and pending["status"] == "pending_api" and pending["options"].is_empty(), "no route core -> pending, no options"):
		return false
	if not _check(legacy.places().size() == 4 and legacy.current_place_id() == "earth.us.ny.new-york-city" and legacy.calendar_text() == "", "fallback places and no calendar"):
		return false
	for place in legacy.places():
		if not _check(Vector2(place["lon"], place["lat"]) == _core_coordinates(place["id"]), "fallback marker uses travel-data coordinates: " + String(place["id"])):
			return false
	if not _check(not legacy.confirm("earth.us.dc.washington-ruins", "")["ok"], "no route core -> confirm refuses to depart"):
		return false
	var fixture := FixtureProvider.new()
	var adapter := RouteAdapter.new(fixture)
	var ready := adapter.preview("earth.us.dc.washington-ruins")
	if not _check(adapter.api_available() and ready["status"] == "ready" and ready["options"].size() == 1 and ready["unverified"].size() == 1, "fixture splits available and unverified"):
		return false
	var text: String = MapScript.route_option_text(ready["options"][0])
	if not _check(text.contains("1000.0") and text.contains("12.5") and text.contains("250 min") and text.contains("FIXTURE-DATE"), "air+car option text uses provider numbers: " + text.replace("\n", " | ")):
		return false
	if not _check(not ready["unverified"][0].has("total_minutes"), "unverified option carries no minutes"):
		return false
	var confirm := adapter.confirm("earth.us.dc.washington-ruins", "fixture.air")
	return _check(confirm["ok"] and fixture.confirmed == [["earth.us.dc.washington-ruins", "fixture.air"]], "confirm passes destination and option to the core")


func _ui_checks() -> bool:
	var app: Node = root.get_node("AppState")
	SaveStore.root_path = "user://test-saves/m2-global-earth-map"
	app.begin_new_run()
	app.show_initial_guide = false
	app.language = "zh"
	MapScript.last_mode = "global"
	change_scene_to_file(MAP_SCENE)
	await _settle()
	var map: Node = current_scene
	var core := RouteAdapter.new(app).api_available()
	print("route core API available: ", core)
	if not _check(map.mode == "global" and map.destination_buttons.size() == 4 and map.region_buttons[NE].visible and map.region_buttons[LAKES].visible, "map opens on the globe with a region marker"):
		return false
	for id in map.place_buttons:
		if not _check(not map.place_buttons[id].visible, "place markers hidden at globe scale: " + id):
			return false
	if not _check(map.title_label.text.contains("科技板块") and map.legend_label.text.contains("科技板块"), "Chinese title and open-board legend"):
		return false
	# One coordinate source: the display registry has no coordinates or names, and every
	# marker uses exactly the route core's coordinates and scene link.
	for display in MapData.display_places():
		if not _check(not display.has("lon") and not display.has("lat") and not display.has("name") and not display.has("scene_destination_id"), "display registry carries no place data: " + String(display["id"])):
			return false
	if core:
		for place in map.places:
			var location: Dictionary = app.travel_location(place["id"])
			if not _check(place["lon"] == float(location["coordinates"]["lon"]) and place["lat"] == float(location["coordinates"]["lat"]) and place["scene_destination_id"] == location["sceneDestinationId"], "marker uses route-core coordinates exactly: " + String(place["id"])):
				return false

	var ne_rect := Rect2(map.region_buttons[NE].position, map.region_buttons[NE].size)
	var lakes_rect := Rect2(map.region_buttons[LAKES].position, map.region_buttons[LAKES].size)
	if not _check(not ne_rect.intersects(lakes_rect), "the two US region markers do not overlap on the globe"):
		return false
	# Wheel zoom over New York until the regional layer opens.
	var anchor: Vector2 = map.view.geo_to_screen(-74.5, 40.5)
	for step in 12:
		if map.mode == "region":
			break
		var wheel := InputEventMouseButton.new()
		wheel.button_index = MOUSE_BUTTON_WHEEL_UP
		wheel.pressed = true
		wheel.position = map.view.geo_to_screen(-74.5, 40.5)
		map._on_map_input(wheel)
	if not _check(map.mode == "region" and map.active_region_id == NE and map.region_layer.visible and not map.global_layer.visible and not map.region_layers[LAKES].visible, "wheel zoom reaches the US Northeast layer only"):
		return false
	var frame := Rect2(Vector2.ZERO, MapScript.MAP_RECT.size)
	var rects := []
	for id in PLACE_IDS:
		var button: Button = map.place_buttons[id]
		var place: Dictionary = map.find_place(id)
		var marker: Vector2 = map.marker_position(id)
		if not _check(button.visible and frame.encloses(Rect2(button.position, button.size)) and Rect2(button.position, button.size).has_point(marker), "visible, in frame, covers its marker: " + id):
			return false
		if not _check(marker.is_equal_approx(map.region_view.geo_to_screen(place["lon"], place["lat"])), "marker at projected coordinates: " + id):
			return false
		rects.append(Rect2(button.position, button.size))
	for i in rects.size():
		for j in range(i + 1, rects.size()):
			if not _check(not rects[i].intersects(rects[j]), "labels do not overlap: %s / %s" % [PLACE_IDS[i], PLACE_IDS[j]]):
				return false
	var ny: Vector2 = map.marker_position(PLACE_IDS[0])
	var yk: Vector2 = map.marker_position(PLACE_IDS[1])
	var dc: Vector2 = map.marker_position(PLACE_IDS[2])
	if not _check(yk.y < ny.y and absf(yk.x - ny.x) < 12.0 and dc.x < ny.x and dc.y > ny.y, "Yonkers north of Lower Manhattan, Washington to the south-west"):
		return false
	var km_screen: float = ny.distance_to(dc) * map.view.km_per_pixel()
	var km_ground := GeoProjection.great_circle_km(map.find_place(PLACE_IDS[0])["lon"], map.find_place(PLACE_IDS[0])["lat"], map.find_place(PLACE_IDS[2])["lon"], map.find_place(PLACE_IDS[2])["lat"])
	if not _check(absf(km_screen - km_ground) < 0.02 * km_ground, "screen distance matches ground distance within 2%% at the region scale (%.1f vs %.1f km)" % [km_screen, km_ground]):
		return false
	var before_center: Vector2 = map.view.center
	var drag := InputEventMouseButton.new()
	drag.button_index = MOUSE_BUTTON_LEFT
	drag.pressed = true
	map._on_map_input(drag)
	var motion := InputEventMouseMotion.new()
	motion.relative = Vector2(-20, 10)
	map._on_map_input(motion)
	drag.pressed = false
	map._on_map_input(drag)
	if not _check(not map.view.center.is_equal_approx(before_center), "drag pans the map"):
		return false
	map.enter_region(NE)

	# Route card: preview and cancel never change the clock or location.
	var minutes_before: int = app.calendar_minutes if core else 0
	var location_before: String = app.current_location_id if core else ""
	map.destination_buttons["scifi.ruins"].pressed.emit()
	await _settle()
	if not _check(map.route_card.visible and map.card_title.text == "华盛顿特区废墟", "Washington ruins card opens with its real name"):
		return false
	if core:
		var option_text: String = map.card_options.get_child(0).text if map.card_options.get_child_count() > 0 else ""
		if not _check(map.route_state["status"] == "ready" and option_text.contains("汽车") and option_text.contains("km") and option_text.contains("抵达"), "car route shows road km, time and arrival: " + option_text.replace("\n", " | ")):
			return false
	else:
		if not _check(map.route_state["status"] == "pending_api" and not _has_digit(map.card_route.text), "no core: pending text without numbers"):
			return false
	var cancel := InputEventAction.new()
	cancel.action = "ui_cancel"
	cancel.pressed = true
	map._unhandled_input(cancel)
	if not _check(not map.route_card.visible and current_scene == map, "Esc closes the route card before leaving the map"):
		return false
	if core and not _check(app.calendar_minutes == minutes_before and app.current_location_id == location_before and app.travel_preview.is_empty(), "cancel charges no time and clears the preview"):
		return false

	# Fallback presentation with no core: departure disabled, no digits, nothing changes.
	var real_adapter = map.route_adapter
	map.route_adapter = RouteAdapter.new(LegacyProvider.new())
	map.select_place("earth.us.dc.washington-ruins")
	if not _check(map.depart_button.disabled and map.depart_button.text == "无法出发" and not _has_digit(map.card_route.text) and map.card_options.get_child_count() == 0, "legacy provider disables departure without numbers"):
		return false
	var fallback_destination: String = app.current_destination_id
	map.depart()
	if not _check(current_scene == map and app.current_destination_id == fallback_destination and (not core or app.calendar_minutes == minutes_before), "no route core: depart call does nothing"):
		return false
	map.close_route_card()
	map.route_adapter = real_adapter

	# English labels show both names.
	app.toggle_language()
	await _settle()
	var primary: Label = map.place_buttons["earth.us.dc.washington-ruins"].get_node("Primary")
	var secondary: Label = map.place_buttons["earth.us.dc.washington-ruins"].get_node("Secondary")
	if not _check(map.title_label.text.contains("Science region") and primary.text == "Washington, D.C. Ruins" and secondary.text == "华盛顿特区废墟", "English title and bilingual place label"):
		return false
	app.toggle_language()
	await _settle()

	# Existing flows: field log, growth, save.
	map.field_button.pressed.emit()
	if not _check(map.field_overlay.visible, "field log opens"):
		return false
	map._unhandled_input(cancel)
	if not _check(not map.field_overlay.visible, "Esc closes field log"):
		return false
	map.growth_button.pressed.emit()
	await _settle()
	if not _check(current_scene.name == "GrowthScreen" or current_scene.scene_file_path.ends_with("growth_screen.tscn"), "growth opens"):
		return false
	change_scene_to_file(MAP_SCENE)
	await _settle()
	map = current_scene
	if not _check(map.mode == "region", "map reopens on the last layer"):
		return false
	map.save_button.pressed.emit()
	await _settle()
	if not _check(current_scene.scene_file_path.ends_with("save_screen.tscn") and app.save_return_scene == MAP_SCENE, "save opens and returns to map"):
		return false
	change_scene_to_file(MAP_SCENE)
	await _settle()
	map = current_scene

	# Same place enters free; another place departs through the core and charges its minutes.
	map.destination_buttons["scifi.city"].pressed.emit()
	await _settle()
	if not _check(map.route_state["status"] == "same_place" and map.depart_button.text == "进入场景", "current place offers free entry"):
		return false
	map.depart_button.pressed.emit()
	await _settle()
	if not _check(current_scene.name == "ScifiExplorationArea" and app.current_destination_id == "scifi.city", "enter the City Hall Park scene"):
		return false
	if core and not _check(app.calendar_minutes == minutes_before, "entering the current place is free"):
		return false
	current_scene.get("back_button").pressed.emit()
	await _settle()
	map = current_scene
	map.destination_buttons["scifi.outskirts"].pressed.emit()
	await _settle()
	var expected_minutes := 0
	if core:
		var option: Dictionary = map.route_state["options"][0]
		expected_minutes = int(option["total_minutes"])
	map.depart_button.pressed.emit()
	await _settle()
	if not _check(current_scene.name == "ScifiExplorationArea" and app.current_destination_id == "scifi.outskirts", "depart reaches the Yonkers scene"):
		return false
	if core and not _check(app.current_location_id == "earth.us.ny.yonkers-outskirts" and app.calendar_minutes == minutes_before + expected_minutes, "travel charged the core's minutes once"):
		return false
	current_scene.get("back_button").pressed.emit()
	await _settle()
	map = current_scene
	if core and not _check(map.route_adapter.current_place_id() == "earth.us.ny.yonkers-outskirts", "map origin follows the party"):
		return false
	map.select_place(CHICAGO)
	await _settle()
	var air_text: String = map.card_options.get_child(0).text if map.card_options.get_child_count() > 0 else ""
	if not _check(map.active_region_id == LAKES and map.region_layers[LAKES].visible and not map.region_layers[NE].visible and map.place_buttons[CHICAGO].visible and not map.place_buttons[PLACE_IDS[0]].visible, "picking Chicago opens the Great Lakes view"):
		return false
	if core and not _check(map.route_state["status"] == "no_route" and map.depart_button.disabled, "no researched Yonkers-Chicago route: departure disabled, no time shown"):
		return false
	map.close_route_card()
	map.enter_region(NE)
	# Zooming out past the region minimum returns to the globe.
	for step in 12:
		if map.mode == "global":
			break
		map.zoom_view(map.view.viewport.get_center(), 0.8)
	if not _check(map.mode == "global" and map.view.scale > map.view.min_scale, "zoom out returns to the globe near the region"):
		return false
	map.globe_button.pressed.emit()
	return _check(is_equal_approx(map.view.scale, map.view.min_scale), "globe button shows the whole Earth")


static func _core_coordinates(location_id: String) -> Vector2:
	var coordinates: Dictionary = MapData.travel_data().location(location_id)["coordinates"]
	return Vector2(float(coordinates["lon"]), float(coordinates["lat"]))


# Shortest distance from a point to any land-ring vertex, in km (an upper bound on the true distance).
static func _km_to_land(at: Vector2, rings: Array) -> float:
	var best := INF
	for ring in rings:
		if ring["hole"]:
			continue
		for point in ring["points"]:
			if absf(point.x - at.x) < 0.2 and absf(point.y - at.y) < 0.2:
				best = minf(best, GeoProjection.great_circle_km(at.x, at.y, point.x, point.y))
	return best


static func _has_digit(text: String) -> bool:
	for c in text:
		if c >= "0" and c <= "9":
			return true
	return false


static func _text_lf_sha256(bytes: PackedByteArray) -> String:
	if bytes.find(0x0d) == -1:
		return _sha256(bytes)
	var lf := PackedByteArray()
	for i in bytes.size():
		if bytes[i] == 0x0d and i + 1 < bytes.size() and bytes[i + 1] == 0x0a:
			continue
		lf.append(bytes[i])
	return _sha256(lf)


static func _sha256(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(bytes)
	return context.finish().hex_encode()


func _settle() -> void:
	for i in 3:
		await process_frame


func _check(condition: bool, label: String) -> bool:
	checks += 1
	if condition:
		return true
	push_error("Global earth map smoke failed: " + label)
	quit(1)
	return false
