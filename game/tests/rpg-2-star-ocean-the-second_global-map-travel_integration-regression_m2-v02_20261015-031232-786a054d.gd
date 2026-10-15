extends SceneTree

# Integration regression for the global map and the travel/calendar core, driven through the
# real map scene and its route-card buttons:
#   - Depart settles exactly one trip and loads exactly one area scene, even on a double press;
#   - Cancel / Esc / switching places charge nothing; the current place and re-entry are free;
#   - a pre-travel save migrates without phantom days and the map starts from its place;
#   - save, load and departing again charge only the new trip;
#   - a missing or mismatched route API disables every departure (no untimed path);
#   - a departure the core refuses charges nothing and keeps saying so;
#   - markers use only the travel data's coordinates; no production or data-source labels show;
#   - no game script other than the travel core selects a scene destination directly.
# From the repository root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --headless --path game \
#     --script res://tests/rpg-2-star-ocean-the-second_global-map-travel_integration-regression_m2-v02_20261015-031232-786a054d.gd

const MapData := preload("res://scripts/world_map_data.gd")
const RouteAdapter := preload("res://scripts/world_map_route_adapter.gd")
const MAP_SCENE := "res://scenes/scifi_world_map.tscn"
const NEW_YORK := "earth.us.ny.new-york-city"
const YONKERS := "earth.us.ny.yonkers-outskirts"
const WASHINGTON := "earth.us.dc.washington-ruins"
const SAVE_ROOT := "user://test-saves/m2-map-travel-integration"
# Production state, review state and data-source names belong in the Game Bible and QA notes.
const FORBIDDEN_UI := [
	"待用户确认", "未验收", "试玩", "待定", "暂定", "待制作", "未核实", "不计旅时", "参照",
	"Natural Earth", "50m", "110m", "GeoNames", "Rome2Rio", "UNESCO", "OSRM", "OpenStreetMap", "GNIS", "OurAirports", "BTS",
	"untimed", "awaiting", "not accepted", "demo", "provisional", "placeholder", "not verified", "pending",
]
# The only scripts allowed to call select_destination(): the travel core itself, and the map
# adapter's no-API fallback, which re-selects the scene the party is already in.
const SELECT_DESTINATION_ALLOWED := ["app_state.gd", "world_map_route_adapter.gd"]

var app: Node
var MapScript: GDScript
var checks := 0
var failed := false
var area_loads := 0
var map_loads := 0
var travel_events: Array = []
var calendar_events: Array = []
var week_events: Array = []


# Every route-core method exists, but confirm_travel has drifted to a new signature.
class MismatchedProvider:
	extends RefCounted
	var app: Node
	var current_location_id := ""
	var current_destination_id := ""
	var calendar_minutes := 0

	func _init(source: Node) -> void:
		app = source
		current_location_id = source.current_location_id
		current_destination_id = source.current_destination_id
		calendar_minutes = source.calendar_minutes

	func travel_location_ids(region_id: String) -> Array: return app.travel_location_ids(region_id)
	func travel_location(id: String) -> Dictionary: return app.travel_location(id)
	func travel_location_name(id: String) -> String: return app.travel_location_name(id)
	func travel_route_options(from_id: String, to_id: String) -> Array: return app.travel_route_options(from_id, to_id)
	func travel_arrival_preview(minutes: int) -> Dictionary: return app.travel_arrival_preview(minutes)
	func preview_travel(to_id: String, option_id: String) -> Dictionary: return app.preview_travel(to_id, option_id)
	func cancel_travel_preview() -> void: app.cancel_travel_preview()
	func confirm_travel(to_id: String, option_id: String, _speed: float) -> bool: return app.confirm_travel(to_id, option_id)
	func enter_current_location_scene() -> bool: return app.enter_current_location_scene()
	func calendar_date_text_at(minutes: int) -> String: return app.calendar_date_text_at(minutes)
	func calendar_time_text_at(minutes: int) -> String: return app.calendar_time_text_at(minutes)
	func travel_duration_text(minutes: int) -> String: return app.travel_duration_text(minutes)
	func select_destination(id: String) -> bool: return app.select_destination(id)


# Correct API, but the core refuses to settle (as it would for a stale or invalid trip).
class RefusingProvider:
	extends RefCounted
	var app: Node
	var current_location_id := ""
	var current_destination_id := ""
	var calendar_minutes := 0
	var confirm_calls := 0

	func _init(source: Node) -> void:
		app = source
		current_location_id = source.current_location_id
		current_destination_id = source.current_destination_id
		calendar_minutes = source.calendar_minutes

	func travel_location_ids(region_id: String) -> Array: return app.travel_location_ids(region_id)
	func travel_location(id: String) -> Dictionary: return app.travel_location(id)
	func travel_location_name(id: String) -> String: return app.travel_location_name(id)
	func travel_route_options(from_id: String, to_id: String) -> Array: return app.travel_route_options(from_id, to_id)
	func travel_arrival_preview(minutes: int) -> Dictionary: return app.travel_arrival_preview(minutes)
	func preview_travel(to_id: String, option_id: String) -> Dictionary: return app.preview_travel(to_id, option_id)
	func cancel_travel_preview() -> void: app.cancel_travel_preview()
	func confirm_travel(_to_id: String, _option_id: String) -> bool:
		confirm_calls += 1
		return false
	func enter_current_location_scene() -> bool: return app.enter_current_location_scene()
	func calendar_date_text_at(minutes: int) -> String: return app.calendar_date_text_at(minutes)
	func calendar_time_text_at(minutes: int) -> String: return app.calendar_time_text_at(minutes)
	func travel_duration_text(minutes: int) -> String: return app.travel_duration_text(minutes)


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	app = root.get_node("AppState")
	MapScript = load("res://scripts/scifi_world_map.gd")
	SaveStore.root_path = SAVE_ROOT
	_clear_saves()
	node_added.connect(_on_node_added)
	app.travel_completed.connect(func(result: Dictionary) -> void: travel_events.append(result))
	app.calendar_advanced.connect(func(previous: int, current: int, reason: String) -> void: calendar_events.append([previous, current, reason]))
	app.calendar_week_transition.connect(func(previous: int, current: int) -> void: week_events.append([previous, current]))
	var steps := [
		_static_select_destination_guard,
		_confirm_settles_once,
		_cancel_and_free_entries,
		_save_load_then_depart,
		_legacy_save_on_map,
		_api_mismatch_blocks_departure,
		_refused_confirm_charges_nothing,
		_labels_and_coordinates,
	]
	for step in steps:
		await step.call()
		if failed:
			return
	_clear_saves()
	print("GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=%d" % checks)
	quit(0)


func _on_node_added(node: Node) -> void:
	if node.get_parent() != root:
		return
	if node.name == "ScifiExplorationArea":
		area_loads += 1
	elif node.name == "ScifiWorldMap":
		map_loads += 1


func _static_select_destination_guard() -> void:
	var directory := DirAccess.open("res://scripts")
	for file_name in directory.get_files():
		if not file_name.ends_with(".gd") or SELECT_DESTINATION_ALLOWED.has(file_name):
			continue
		var source := FileAccess.get_file_as_string("res://scripts/" + file_name)
		# Command-line capture tools (--script entry points) are never loaded by the game.
		if source.begins_with("extends SceneTree"):
			continue
		if not _check(not source.contains("select_destination(") and not source.contains("current_destination_id ="), "no direct scene selection outside the travel core: " + file_name):
			return


func _open_map(language := "zh") -> Node:
	app.language = language
	MapScript.last_mode = "region"
	change_scene_to_file(MAP_SCENE)
	await _settle()
	return current_scene


func _back_to_map() -> Node:
	current_scene.get("back_button").pressed.emit()
	await _settle()
	return current_scene


func _reset_counters() -> void:
	area_loads = 0
	map_loads = 0
	travel_events.clear()
	calendar_events.clear()
	week_events.clear()


func _selected_minutes(map: Node) -> int:
	for option in map.route_state.get("options", []):
		if option["option_id"] == map.route_state["selected"]:
			return int(option["total_minutes"])
	return -1


func _confirm_settles_once() -> void:
	app.begin_new_run()
	app.show_initial_guide = false
	var map: Node = await _open_map()
	map.destination_buttons["scifi.ruins"].pressed.emit()
	await _settle()
	var minutes := _selected_minutes(map)
	if not _check(map.route_state["status"] == "ready" and minutes > 0 and app.travel_preview.get("kind", "") == "travel", "Washington ruins card previews a timed trip"):
		return
	var start: int = app.calendar_minutes
	_reset_counters()
	map.depart_button.pressed.emit()
	map.depart_button.pressed.emit()
	map.depart()
	await _settle()
	_check(travel_events.size() == 1 and calendar_events.size() == 1 and calendar_events[0] == [start, start + minutes, "travel"], "triple Depart press settles one trip (%d travel, %d calendar events)" % [travel_events.size(), calendar_events.size()])
	_check(app.calendar_minutes == start + minutes and app.current_location_id == WASHINGTON and app.last_travel.get("minutes", -1) == minutes, "clock advanced by the route minutes once and the party is at Washington ruins")
	_check(area_loads == 1 and current_scene.name == "ScifiExplorationArea" and app.current_destination_id == "scifi.ruins", "exactly one area scene load, at the ruins (%d loads)" % area_loads)
	_check(app.travel_preview.is_empty(), "preview consumed by departure")


func _cancel_and_free_entries() -> void:
	var map: Node = await _back_to_map()
	var start: int = app.calendar_minutes
	_reset_counters()
	# Cancel button, Esc, and switching between places before cancelling.
	map.destination_buttons["scifi.city"].pressed.emit()
	await _settle()
	map.cancel_button.pressed.emit()
	map.destination_buttons["scifi.outskirts"].pressed.emit()
	await _settle()
	map.destination_buttons["scifi.city"].pressed.emit()
	await _settle()
	var cancel := InputEventAction.new()
	cancel.action = "ui_cancel"
	cancel.pressed = true
	map._unhandled_input(cancel)
	await _settle()
	_check(current_scene == map and not map.route_card.visible and app.travel_preview.is_empty(), "Cancel and Esc close the card and clear the preview")
	_check(app.calendar_minutes == start and app.current_location_id == WASHINGTON and travel_events.is_empty() and calendar_events.is_empty(), "previewing and cancelling charge no time")
	# The current place: free entry, then leave and re-enter twice more.
	for attempt in 3:
		map.destination_buttons["scifi.ruins"].pressed.emit()
		await _settle()
		if not _check(map.route_state["status"] == "same_place" and map.depart_button.text == "进入场景" and not map.depart_button.disabled, "current place offers free entry (attempt %d)" % attempt):
			return
		map.depart_button.pressed.emit()
		map.depart_button.pressed.emit()
		await _settle()
		if not _check(current_scene.name == "ScifiExplorationArea" and app.current_destination_id == "scifi.ruins", "free entry opens the ruins (attempt %d)" % attempt):
			return
		map = await _back_to_map()
	_check(app.calendar_minutes == start and travel_events.is_empty() and calendar_events.is_empty() and area_loads == 3, "same-place entry and re-entry charge nothing (%d area loads)" % area_loads)


func _save_load_then_depart() -> void:
	var map: Node = current_scene
	map.save_button.pressed.emit()
	await _settle()
	var id: String = app.write_manual_save(1)
	var saved_minutes: int = app.calendar_minutes
	if not _check(id != "", "manual save after a trip"):
		return
	_reset_counters()
	if not _check(app.load_save(id) and app.calendar_minutes == saved_minutes and app.current_location_id == WASHINGTON, "load restores clock and place"):
		return
	app.load_save(id)
	map = await _open_map()
	_check(calendar_events.is_empty() and week_events.is_empty() and travel_events.is_empty() and app.calendar_minutes == saved_minutes, "loading twice and reopening the map charge nothing")
	_check(map.route_adapter.current_place_id() == WASHINGTON and map.calendar_label.text == "%s %s" % [app.calendar_date_text_at(saved_minutes), app.calendar_time_text_at(saved_minutes)], "map origin and date follow the loaded save")
	map.destination_buttons["scifi.city"].pressed.emit()
	await _settle()
	var minutes := _selected_minutes(map)
	map.depart_button.pressed.emit()
	await _settle()
	_check(minutes > 0 and travel_events.size() == 1 and app.calendar_minutes == saved_minutes + minutes and app.current_location_id == NEW_YORK and app.current_destination_id == "scifi.city", "after loading, only the new trip is charged")


func _legacy_save_on_map() -> void:
	app.begin_new_run()
	var legacy: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	legacy.erase("travel")
	# A real pre-travel save is older than the commerce block too, so it has neither.
	legacy.erase("commerce")
	legacy["destination"] = "scifi.outskirts"
	legacy["areasVisited"] = {"scifi.outskirts": true, "scifi.ruins": true}
	legacy["playTimeSeconds"] = 90000.0
	var legacy_id := SaveStore.write_entry("manual", 2, legacy)
	# Leave the clock somewhere else first, so a load that kept it would be caught.
	app.advance_calendar(3 * TravelCalendar.MINUTES_PER_DAY, "rest")
	_reset_counters()
	if not _check(app.load_save(legacy_id) and app.travel_state_migrated, "pre-travel save loads and migrates"):
		return
	var start: int = app.travel_registry().calendar_start_minutes
	var map: Node = await _open_map()
	_check(app.calendar_minutes == start and calendar_events.is_empty() and week_events.is_empty(), "migration starts at the calendar start, no phantom days from 25 h play time")
	_check(map.route_adapter.current_place_id() == YONKERS, "map starts from the saved scene's place (Yonkers)")
	map.destination_buttons["scifi.outskirts"].pressed.emit()
	await _settle()
	if not _check(map.route_state["status"] == "same_place", "the migrated place is the current place"):
		return
	map.depart_button.pressed.emit()
	await _settle()
	_check(current_scene.name == "ScifiExplorationArea" and app.current_destination_id == "scifi.outskirts" and app.calendar_minutes == start and travel_events.is_empty(), "entering the migrated place is free")
	await _back_to_map()


func _api_mismatch_blocks_departure() -> void:
	var map: Node = current_scene
	var start: int = app.calendar_minutes
	var place_before: String = app.current_location_id
	var mismatched := RouteAdapter.new(MismatchedProvider.new(app))
	if not _check(not mismatched.api_available() and "; ".join(mismatched.api_problems()).contains("confirm_travel"), "signature drift is detected and named"):
		return
	map.route_adapter = mismatched
	map.places = mismatched.places()
	_reset_counters()
	for language in ["zh", "en"]:
		app.language = language
		map.select_place(WASHINGTON)
		await _settle()
		_check(map.route_state["status"] == "pending_api" and map.depart_button.disabled and not map.card_route.text.is_empty() and map.card_options.get_child_count() == 0, "mismatched API: departure disabled with an explanation (%s)" % language)
		_check(not _has_digit(map.card_route.text) and not map.depart_button.text.to_lower().contains("enter") and not map.depart_button.text.contains("进入"), "mismatched API: no numbers and no entry offer (%s)" % language)
		_check(_forbidden_in(map) == "", "mismatched API card has no development labels (%s): %s" % [language, _forbidden_in(map)])
		map.depart_button.pressed.emit()
		map.depart()
		await _settle()
		_check(current_scene == map and app.current_location_id == place_before and app.calendar_minutes == start and travel_events.is_empty() and area_loads == 0, "mismatched API: Depart changes nothing (%s)" % language)
		map.close_route_card()
	app.language = "zh"
	# The place the party is at stays enterable, free.
	map.select_place(place_before)
	await _settle()
	if not _check(map.route_state["status"] == "same_place" and not map.depart_button.disabled, "mismatched API: current place still enterable"):
		return
	map.depart_button.pressed.emit()
	await _settle()
	_check(current_scene.name == "ScifiExplorationArea" and app.current_location_id == place_before and app.calendar_minutes == start and travel_events.is_empty(), "mismatched API: local entry is free and moves nobody")
	await _back_to_map()


func _refused_confirm_charges_nothing() -> void:
	var map: Node = current_scene
	var start: int = app.calendar_minutes
	var place_before: String = app.current_location_id
	var refusing := RefusingProvider.new(app)
	map.route_adapter = RouteAdapter.new(refusing)
	map.places = map.route_adapter.places()
	_reset_counters()
	map.select_place(WASHINGTON)
	await _settle()
	if not _check(map.route_state["status"] == "ready" and not map.depart_button.disabled, "refusing core still previews the trip"):
		return
	map.depart_button.pressed.emit()
	map.depart_button.pressed.emit()
	await _settle()
	var failure_zh: String = map.card_route.text
	_check(refusing.confirm_calls == 1 and current_scene == map and app.calendar_minutes == start and app.current_location_id == place_before and travel_events.is_empty() and area_loads == 0, "refused confirm: one attempt, no time, no scene change")
	_check(map.depart_button.disabled and failure_zh.contains("未扣除时间") and app.travel_preview.is_empty(), "refused confirm: card says no time was spent and the preview is cleared")
	app.toggle_language()
	await _settle()
	_check(map.route_card.visible and map.card_route.text.contains("No time was spent") and map.depart_button.disabled, "refused confirm message survives a language switch")
	app.toggle_language()
	map.close_route_card()
	map.route_adapter = RouteAdapter.new(app)
	map.places = map.route_adapter.places()


func _labels_and_coordinates() -> void:
	app.begin_new_run()
	app.show_initial_guide = false
	for language in ["zh", "en"]:
		var map: Node = await _open_map(language)
		map.enter_global()
		await _settle()
		_check(_forbidden_in(map) == "", "globe has no development labels (%s): %s" % [language, _forbidden_in(map)])
		map.enter_region("us_northeast")
		await _settle()
		_check(_forbidden_in(map) == "", "region has no development labels (%s): %s" % [language, _forbidden_in(map)])
		for place_id in [NEW_YORK, YONKERS, WASHINGTON]:
			var location: Dictionary = app.travel_location(place_id)
			var expected: Vector2 = map.region_view.geo_to_screen(float(location["coordinates"]["lon"]), float(location["coordinates"]["lat"]))
			_check(map.marker_position(place_id) == expected, "marker drawn at route-core coordinates: " + place_id)
			_check((map.place_buttons[place_id].get_node("Primary") as Label).text == String(location["names"][language]), "marker name is the route-core name (%s): %s" % [language, place_id])
			map.select_place(place_id)
			await _settle()
			_check(_forbidden_in(map) == "", "route card has no development labels (%s, %s): %s" % [language, place_id, _forbidden_in(map)])
			_check(map.card_title.text == String(location["names"][language]), "card title is the route-core name (%s): %s" % [language, place_id])
			if map.route_state["status"] == "ready":
				var option_text: String = map.card_options.get_child(0).text
				_check(option_text.contains("估算" if language == "zh" else "estimated"), "travel figures stay marked as estimates (%s): %s" % [language, place_id])
			map.close_route_card()
	app.language = "zh"


func _forbidden_in(node: Node) -> String:
	var found: PackedStringArray = []
	for text in _visible_texts(node):
		for word in FORBIDDEN_UI:
			if text.to_lower().contains(String(word).to_lower()):
				found.append("%s in '%s'" % [word, text.replace("\n", " | ")])
	return "; ".join(found)


func _visible_texts(node: Node) -> PackedStringArray:
	var texts: PackedStringArray = []
	if node is CanvasItem and not (node as CanvasItem).is_visible_in_tree():
		return texts
	if node is Label:
		texts.append((node as Label).text)
	elif node is Button:
		texts.append((node as Button).text)
		texts.append((node as Button).tooltip_text)
	elif node is RichTextLabel:
		texts.append((node as RichTextLabel).get_parsed_text())
	for child in node.get_children():
		texts.append_array(_visible_texts(child))
	return texts


static func _has_digit(text: String) -> bool:
	for c in text:
		if c >= "0" and c <= "9":
			return true
	return false


func _clear_saves() -> void:
	var directory := DirAccess.open(SAVE_ROOT)
	if directory == null:
		return
	for name in directory.get_files():
		directory.remove(name)


func _settle() -> void:
	for i in 3:
		await process_frame


func _check(condition: bool, label: String) -> bool:
	checks += 1
	if condition:
		return true
	if not failed:
		failed = true
		push_error("Global map travel integration failed: " + label)
		quit(1)
	return false
