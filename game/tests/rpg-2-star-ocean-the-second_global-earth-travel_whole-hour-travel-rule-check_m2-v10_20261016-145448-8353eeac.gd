extends SceneTree

# M2 whole-hour travel rule (creator rule 2026-10-16: "这不是一款模拟游戏，不用在时间上那么精细，把rules变简单化").
#   - every available car or air leg charges gameplayDurationMinutes: a whole number of hours, at least one,
#     equal to its referenceDurationMinutes rounded to the nearest hour; a route charges the sum of its legs;
#   - science MVP: New York <-> Yonkers 1 h by car, New York <-> Washington 5 h by car,
#     Yonkers <-> Washington 5 h by car, New York <-> Chicago 6 h by air, both directions;
#   - the charge never depends on the departure clock, airports, check-in or waiting: retired component
#     fields are rejected at a segment's top level, and referenceEvidence is provenance that is never charged;
#   - cancel costs nothing, short trips add up, arrivals roll past midnight and New Year, a Sunday-night trip
#     crosses the week once, and a save made under the old minute figures loads with its exact clock;
#   - the route text players see (zh and en) shows mode, approximate distance, whole hours and the arrival,
#     and no game string names an airport, an IATA code, check-in, baggage, waiting or timetables.
# Replaces the door-to-door component check (m2-v06), whose model the 2026-10-16 rule supersedes.
# Nothing here accepts M2 or any figure as final.
# From the repository root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --headless --path game \
#     --script res://tests/rpg-2-star-ocean-the-second_global-earth-travel_whole-hour-travel-rule-check_m2-v10_20261016-145448-8353eeac.gd

# The map scripts use the AppState autoload, so they are loaded at run time, not preloaded.
const MAP_ADAPTER_PATH := "res://scripts/world_map_route_adapter.gd"
const WORLD_MAP_PATH := "res://scripts/scifi_world_map.gd"
const NEW_YORK := "earth.us.ny.new-york-city"
const YONKERS := "earth.us.ny.yonkers-outskirts"
const WASHINGTON := "earth.us.dc.washington-ruins"
const CHICAGO := "earth.us.il.chicago"
const EXPECTED_LEGS := {
	"seg.car.nyc__yonkers": 60, "seg.car.yonkers__nyc": 60,
	"seg.car.nyc__washington-ruins": 300, "seg.car.washington-ruins__nyc": 300,
	"seg.car.yonkers__washington-ruins": 300, "seg.car.washington-ruins__yonkers": 300,
	"seg.air.nyc-lga__chicago-ord": 360, "seg.air.chicago-ord__nyc-lga": 360,
}
# [from, to, route id, mode, minutes]
const TRIPS := [
	[NEW_YORK, YONKERS, "route.car.nyc__yonkers", "car", 60],
	[YONKERS, NEW_YORK, "route.car.yonkers__nyc", "car", 60],
	[NEW_YORK, WASHINGTON, "route.car.nyc__washington-ruins", "car", 300],
	[WASHINGTON, NEW_YORK, "route.car.washington-ruins__nyc", "car", 300],
	[YONKERS, WASHINGTON, "route.car.yonkers__washington-ruins", "car", 300],
	[WASHINGTON, YONKERS, "route.car.washington-ruins__yonkers", "car", 300],
	[NEW_YORK, CHICAGO, "route.air.nyc__chicago", "air", 360],
	[CHICAGO, NEW_YORK, "route.air.chicago__nyc", "air", 360],
]
const RETIRED_FIELDS := ["airportAccessMinutes", "checkInAndWaitMinutes", "flightMinutes", "airportEgressMinutes", "doorToDoorAllowanceMinutes", "departureAirport", "arrivalAirport", "components"]
const SAVE_ROOT := "user://test-saves/m2-whole-hour-v10"
# Player-facing wording that the simple rule rules out. Checked against route text and every string
# literal in the game's scripts and scenes (the route registry holds only data-validation messages).
const FORBIDDEN_TEXT := "(?i)airport|laguardia|o'hare|check-in|check in|baggage|boarding|timetable|rush.hour|layover|door.to.door|机场|值机|行李|候机|登机|时刻表|高峰|拉瓜迪亚|奥黑尔|航站楼|门到门"
const FORBIDDEN_CODES := "\\b(LGA|ORD|JFK|EWR|MDW|DCA|IAD)\\b"
# Player-facing calendar text is a date only (creator correction 2026-10-16): no HH:MM clock time.
const CLOCK_TEXT := "\\d{1,2}:\\d{2}"

var app: Node
var checks := 0
var failures := 0
var week_events: Array = []
var calendar_events: Array = []


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	app = root.get_node("AppState")
	SaveStore.root_path = SAVE_ROOT
	_clear_saves()
	app.calendar_week_transition.connect(func(previous: int, current: int) -> void: week_events.append([previous, current]))
	app.calendar_advanced.connect(func(previous: int, current: int, reason: String) -> void: calendar_events.append([previous, current, reason]))
	var registry: WorldRouteRegistry = app.travel_registry()
	_check(registry.is_valid(), "runtime travel data validates: " + "; ".join(registry.errors))
	if registry.is_valid():
		_test_rounding_helpers()
		_test_data(registry)
		_test_validator(registry)
		_test_multi_leg_sum(registry)
		_test_clock_independence()
		_test_calendar()
		_test_old_minute_saves()
		_test_player_text()
		_test_string_tables()
	_clear_saves()
	app.language = "zh"
	app.begin_new_run()
	if failures == 0:
		print("M2_WHOLE_HOUR_TRAVEL_OK checks=%d" % checks)
		quit(0)
	else:
		push_error("M2_WHOLE_HOUR_TRAVEL failed checks: %d of %d" % [failures, checks])
		quit(1)


func _test_rounding_helpers() -> void:
	var cases := {1: 60, 29: 60, 30: 60, 35: 60, 89: 60, 90: 120, 286: 300, 289: 300, 306: 300, 329: 300, 330: 360, 332: 360, 364: 360, 389: 360, 390: 420}
	var ok := true
	for reference in cases:
		ok = ok and WorldRouteRegistry.whole_hour_minutes(reference) == int(cases[reference])
	_check(ok, "reference minutes round to the nearest hour (half up), never under one hour")
	var km := {0.3: 1, 28.2: 28, 28.3: 28, 99.4: 99, 361.4: 360, 363.2: 360, 383.4: 380, 388.0: 390, 1177.1: 1180}
	ok = true
	for value in km:
		ok = ok and WorldRouteRegistry.approximate_km(value) == int(km[value])
	_check(ok, "display distance: whole km under 100 km, nearest 10 km above")


func _test_data(registry: WorldRouteRegistry) -> void:
	var rule: Dictionary = registry.data.get("travelTimeRule", {})
	_check(rule.get("chargedField", "") == "gameplayDurationMinutes" and int(rule.get("stepMinutes", 0)) == 60 and int(rule.get("minimumMinutes", 0)) == 60 and String(rule.get("creatorDirection", "")).contains("不是一款模拟游戏"), "the data declares the whole-hour rule and its creator direction")
	_check(registry.segments.size() == EXPECTED_LEGS.size(), "eight legs in the science set")
	for segment_id in EXPECTED_LEGS:
		var segment: Dictionary = registry.segments.get(segment_id, {})
		var charged := int(segment.get("gameplayDurationMinutes", -1))
		_check(charged == int(EXPECTED_LEGS[segment_id]) and registry.segment_minutes(segment) == charged, "%s charges %d min (%d h)" % [segment_id, int(EXPECTED_LEGS[segment_id]), int(EXPECTED_LEGS[segment_id]) / 60])
		_check(charged % 60 == 0 and charged >= 60 and charged == WorldRouteRegistry.whole_hour_minutes(int(segment["referenceDurationMinutes"])), "%s is its reference %d min rounded to whole hours" % [segment_id, int(segment.get("referenceDurationMinutes", -1))])
		var stray: PackedStringArray = []
		for field in RETIRED_FIELDS:
			if segment.has(field):
				stray.append(field)
		_check(stray.is_empty(), "%s carries no top-level trip components or airports: %s" % [segment_id, ", ".join(stray)])
		if segment["mode"] == "air":
			var evidence: Dictionary = segment.get("referenceEvidence", {})
			var parts := 0
			for field in evidence.get("componentMinutes", {}):
				parts += int(evidence["componentMinutes"][field])
			_check(evidence.get("runtimeUse", "") == "none" and parts == int(segment["referenceDurationMinutes"]) and evidence.has("departureAirport"), "%s keeps its airport research as uncharged evidence that sums to the reference" % segment_id)
	for trip in TRIPS:
		var options: Array[Dictionary] = registry.routes_between(trip[0], trip[1])
		_check(options.size() == 1 and options[0]["option_id"] == trip[2] and options[0]["available"] and options[0]["mode"] == trip[3] and int(options[0]["total_minutes"]) == int(trip[4]), "%s is one %s route of %d h" % [trip[2], trip[3], int(trip[4]) / 60])
		if options.is_empty():
			continue
		var option: Dictionary = options[0]
		var car: bool = trip[3] == "car"
		_check((option["road_distance_km"] != null) == car and (option["air_distance_km"] != null) == not car, "%s keeps road and flight distance apart" % trip[2])
		if car:
			_check(float(option["road_distance_km"]) >= registry.great_circle_km(trip[0], trip[1]), "%s road distance is at least the straight line" % trip[2])
	# No car crosses to Chicago and no figure is invented for the pending pairs.
	for pair in [[YONKERS, CHICAGO], [WASHINGTON, CHICAGO], [CHICAGO, YONKERS], [CHICAGO, WASHINGTON]]:
		var pending: Array[Dictionary] = registry.routes_between(pair[0], pair[1])
		_check(pending.size() == 1 and not pending[0]["available"] and int(pending[0]["total_minutes"]) == -1, "no researched route %s -> %s, so no time is shown" % pair)
	var chicago_modes := []
	for option in registry.routes_between(NEW_YORK, CHICAGO):
		chicago_modes.append(option["mode"])
	_check(chicago_modes == ["air"], "New York -> Chicago is air only")


func _test_validator(registry: WorldRouteRegistry) -> void:
	var cases := {
		"a leg of 35 min (not whole hours)": func(d: Dictionary) -> void: _segment(d, "seg.car.nyc__yonkers")["gameplayDurationMinutes"] = 35,
		"a leg of 0 min": func(d: Dictionary) -> void: _segment(d, "seg.car.nyc__yonkers")["gameplayDurationMinutes"] = 0,
		"a leg of 1.5 h": func(d: Dictionary) -> void: _segment(d, "seg.car.nyc__yonkers")["gameplayDurationMinutes"] = 90,
		"hours that are not the rounded reference (Yonkers 2 h)": func(d: Dictionary) -> void: _segment(d, "seg.car.nyc__yonkers")["gameplayDurationMinutes"] = 120,
		"hours that are not the rounded reference (Chicago -> NYC 5 h)": func(d: Dictionary) -> void: _segment(d, "seg.air.chicago-ord__nyc-lga")["gameplayDurationMinutes"] = 300,
		"a leg without a reference estimate": func(d: Dictionary) -> void: _segment(d, "seg.car.nyc__washington-ruins").erase("referenceDurationMinutes"),
		"a leg without gameplay hours": func(d: Dictionary) -> void: _segment(d, "seg.car.nyc__washington-ruins").erase("gameplayDurationMinutes"),
		"a top-level flightMinutes on an air leg": func(d: Dictionary) -> void: _segment(d, "seg.air.nyc-lga__chicago-ord")["flightMinutes"] = 165,
		"a top-level checkInAndWaitMinutes on an air leg": func(d: Dictionary) -> void: _segment(d, "seg.air.nyc-lga__chicago-ord")["checkInAndWaitMinutes"] = 120,
		"a door-to-door allowance on a car leg": func(d: Dictionary) -> void: _segment(d, "seg.car.yonkers__nyc")["doorToDoorAllowanceMinutes"] = 0,
		"evidence parts that no longer add up to the reference": func(d: Dictionary) -> void: _segment(d, "seg.air.nyc-lga__chicago-ord")["referenceEvidence"]["componentMinutes"]["flightMinutes"] = 150,
		"an evidence note that disagrees with its part": func(d: Dictionary) -> void: _segment(d, "seg.air.nyc-lga__chicago-ord")["referenceEvidence"]["components"]["flightMinutes"]["value"] = 166,
		"evidence marked as charged": func(d: Dictionary) -> void: _segment(d, "seg.air.nyc-lga__chicago-ord")["referenceEvidence"]["runtimeUse"] = "charged",
		"a rule that charges the reference minutes": func(d: Dictionary) -> void: d["travelTimeRule"]["chargedField"] = "referenceDurationMinutes",
		"a rule with 30-minute steps": func(d: Dictionary) -> void: d["travelTimeRule"]["stepMinutes"] = 30,
		"no travel-time rule": func(d: Dictionary) -> void: d.erase("travelTimeRule"),
	}
	for label in cases:
		var broken: Dictionary = registry.data.duplicate(true)
		cases[label].call(broken)
		_check(not WorldRouteRegistry.from_dictionary(broken).is_valid(), "validator rejects " + label)
	# Revising evidence inside the same hour is accepted and does not change the charge.
	var revised: Dictionary = registry.data.duplicate(true)
	var west := _segment(revised, "seg.air.nyc-lga__chicago-ord")
	west["referenceEvidence"]["componentMinutes"]["airportEgressMinutes"] = 40
	west["referenceEvidence"]["components"]["airportEgressMinutes"]["value"] = 40
	west["referenceDurationMinutes"] = 349
	var revised_registry := WorldRouteRegistry.from_dictionary(revised)
	_check(revised_registry.is_valid() and int(revised_registry.routes_between(NEW_YORK, CHICAGO)[0]["total_minutes"]) == 360, "a corrected airport drive within the same hour keeps the 6 h charge")
	# A correction that crosses the half hour cannot silently keep the old hours: it needs an explicit change.
	var crossed: Dictionary = registry.data.duplicate(true)
	var east := _segment(crossed, "seg.air.chicago-ord__nyc-lga")
	var access := int(east["referenceEvidence"]["componentMinutes"]["airportAccessMinutes"])
	east["referenceEvidence"]["componentMinutes"]["airportAccessMinutes"] = access - 3
	east["referenceEvidence"]["components"]["airportAccessMinutes"]["value"] = access - 3
	east["referenceDurationMinutes"] = int(east["referenceDurationMinutes"]) - 3
	_check(not WorldRouteRegistry.from_dictionary(crossed).is_valid(), "an eastbound reference that drops below 5.5 h (%d min) is rejected until its hours are changed explicitly" % int(east["referenceDurationMinutes"]))


# Multi-leg routes charge the sum of their fixed legs. Built on the live data, never shipped.
func _test_multi_leg_sum(registry: WorldRouteRegistry) -> void:
	var extended: Dictionary = registry.data.duplicate(true)
	extended["routes"].append({
		"id": "route.test.yonkers__chicago-via-nyc", "fromLocationId": YONKERS, "toLocationId": CHICAGO, "status": "available",
		"bidirectional": false, "viaLocationIds": [NEW_YORK], "declaredTotalMinutes": 420,
		"legs": [{"segmentId": "seg.car.yonkers__nyc", "reverse": false}, {"segmentId": "seg.air.nyc-lga__chicago-ord", "reverse": false}],
	})
	var test_registry := WorldRouteRegistry.from_dictionary(extended)
	_check(test_registry.is_valid(), "a two-leg test route validates: " + "; ".join(test_registry.errors))
	var chained: Dictionary = {}
	for option in test_registry.routes_between(YONKERS, CHICAGO):
		if option["option_id"] == "route.test.yonkers__chicago-via-nyc":
			chained = option
	_check(not chained.is_empty() and int(chained["total_minutes"]) == 60 + 360 and chained["mode"] == "air_car" and chained["via_location_ids"] == [NEW_YORK], "car 1 h + air 6 h charges 7 h via New York")
	_check(not chained.is_empty() and is_equal_approx(float(chained["road_distance_km"]), 28.3) and is_equal_approx(float(chained["air_distance_km"]), 1177.1), "the chained route keeps road and flight distance apart")
	extended["routes"][-1]["declaredTotalMinutes"] = 424
	_check(not WorldRouteRegistry.from_dictionary(extended).is_valid(), "a declared total that is not the sum of whole-hour legs is rejected")


# The same trip charges the same hours at any departure time, including odd minutes from old saves.
func _test_clock_independence() -> void:
	var clocks := [[2537, 5, 25, 0, 0], [2537, 5, 25, 7, 59], [2537, 5, 25, 8, 0], [2537, 5, 25, 13, 37], [2537, 5, 26, 23, 59], [2537, 12, 31, 23, 30], [2540, 2, 29, 17, 5]]
	var ok := true
	for trip in TRIPS:
		for clock in clocks:
			app.begin_new_run()
			app.current_location_id = trip[0]
			app.discovered_locations[trip[1]] = true
			_set_clock(clock[0], clock[1], clock[2], clock[3], clock[4])
			var before: int = app.calendar_minutes
			var preview: Dictionary = app.preview_travel(trip[1])
			ok = ok and preview.get("ok", false) and int(preview["total_minutes"]) == int(trip[4]) and int(preview["arrival_minutes"]) == before + int(trip[4]) and app.calendar_minutes == before
	app.cancel_travel_preview()
	_check(ok, "all 8 trips preview the same whole hours at 7 departure times, and previewing is free")


func _test_calendar() -> void:
	# Cancel costs nothing.
	app.begin_new_run()
	calendar_events.clear()
	var start: int = app.calendar_minutes
	_check(TravelCalendar.iso_text(start) == "2537-05-25 08:00", "a new run starts 2537-05-25 08:00 in New York")
	app.preview_travel(CHICAGO)
	app.cancel_travel_preview()
	var cancelled: Dictionary = app.settle_travel()
	_check(not cancelled["departed"] and int(cancelled["minutes_charged"]) == 0 and app.calendar_minutes == start and app.current_location_id == NEW_YORK and calendar_events.is_empty(), "a cancelled flight charges no time and emits nothing")
	# Continuous short trips: each is exactly one hour and the clock stays on the hour.
	var targets := [YONKERS, NEW_YORK, YONKERS, NEW_YORK, YONKERS, NEW_YORK]
	var each_ok := true
	for target in targets:
		var before: int = app.calendar_minutes
		var result := _travel(target)
		each_ok = each_ok and result.get("departed", false) and int(result["minutes_charged"]) == 60 and app.calendar_minutes - before == 60
	_check(each_ok and app.calendar_minutes == start + 360 and TravelCalendar.iso_text(app.calendar_minutes) == "2537-05-25 14:00", "six 1 h hops add up to 6 h: 08:00 -> 14:00")
	# A chain over every pair: 1 + 5 + 5 + 6 + 6 = 23 h.
	app.begin_new_run()
	var chain_ok := true
	for target in [YONKERS, WASHINGTON, NEW_YORK, CHICAGO, NEW_YORK]:
		chain_ok = chain_ok and _travel(target).get("departed", false)
	_check(chain_ok and app.calendar_minutes == start + 23 * 60 and TravelCalendar.iso_text(app.calendar_minutes) == "2537-05-26 07:00", "Yonkers, Washington, New York, Chicago, New York charges 23 h: arrive 2537-05-26 07:00")
	# Past midnight.
	app.begin_new_run()
	_set_clock(2537, 5, 25, 22, 30)
	_travel(WASHINGTON)
	_check(TravelCalendar.iso_text(app.calendar_minutes) == "2537-05-26 03:30" and app.current_location_id == WASHINGTON, "a 5 h drive at 22:30 arrives 03:30 the next day")
	# Past New Year: the preview shows the new year without moving the clock.
	app.begin_new_run()
	_set_clock(2537, 12, 31, 20, 0)
	var before_year: int = app.calendar_minutes
	var preview: Dictionary = app.preview_travel(CHICAGO)
	_check(int(preview["arrival"]["year"]) == 2538 and app.calendar_minutes == before_year, "a New Year's Eve flight previews a 2538 arrival and charges nothing yet")
	app.settle_travel()
	_check(TravelCalendar.iso_text(app.calendar_minutes) == "2538-01-01 02:00" and app.current_destination_id == "scifi.loop", "the 6 h flight at 20:00 on 2537-12-31 lands 2538-01-01 02:00 at the Loop")
	# Week boundary: 2537-05-26 is a Sunday; one 5 h drive at 22:00 crosses into Monday once.
	app.begin_new_run()
	_set_clock(2537, 5, 26, 22, 0)
	week_events.clear()
	var week: int = app.calendar_week_index
	_travel(WASHINGTON)
	_check(week_events == [[week, week + 1]] and int(app.calendar_datetime()["weekday"]) == 1 and TravelCalendar.iso_text(app.calendar_minutes) == "2537-05-27 03:00", "a Sunday 22:00 drive arrives Monday 03:00 and crosses the week once")
	_travel(NEW_YORK)
	_check(week_events.size() == 1, "the drive back inside the week crosses nothing")


# Saves written under the old minute figures keep their exact clock and history; only new trips use hours.
func _test_old_minute_saves() -> void:
	app.begin_new_run()
	_travel(YONKERS)
	var old: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	var old_arrival: int = TravelCalendar.to_minutes(2537, 5, 25, 8, 35)
	old["travel"]["calendarMinutes"] = old_arrival
	old["travel"]["calendarWeekIndex"] = TravelCalendar.week_index(old_arrival)
	old["travel"]["calendarText"] = TravelCalendar.iso_text(old_arrival)
	old["travel"]["lastTravel"]["arrivedAtMinutes"] = old_arrival
	old["travel"]["lastTravel"]["minutes"] = 35
	var old_id := SaveStore.write_entry("manual", 1, old)
	app.begin_new_run()
	week_events.clear()
	calendar_events.clear()
	_check(app.load_save(old_id), "a save from the 35-minute Yonkers drive still loads")
	_check(app.calendar_minutes == old_arrival and TravelCalendar.iso_text(app.calendar_minutes) == "2537-05-25 08:35" and app.current_location_id == YONKERS and int(app.last_travel["minutes"]) == 35, "it keeps its 08:35 clock and 35-minute history exactly; nothing is re-priced or rounded")
	_check(week_events.is_empty() and calendar_events.is_empty(), "loading it emits no calendar or week events")
	var back := _travel(NEW_YORK)
	_check(back.get("departed", false) and int(back["minutes_charged"]) == 60 and TravelCalendar.iso_text(app.calendar_minutes) == "2537-05-25 09:35", "the next drive charges the whole hour: 08:35 -> 09:35")
	app.save_return_scene = "res://scenes/scifi_world_map.tscn"
	var resaved: String = app.write_manual_save(2)
	var expected_clock: int = app.calendar_minutes
	app.begin_new_run()
	_check(app.load_save(resaved) and app.calendar_minutes == expected_clock and app.current_location_id == NEW_YORK and int(app.last_travel["minutes"]) == 60, "re-saving and loading keeps the whole-hour trip and clock")
	# A Chicago save from the 365-minute door-to-door figure.
	app.begin_new_run()
	_travel(CHICAGO)
	var chicago: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	var chicago_arrival: int = app.travel_registry().calendar_start_minutes + 365
	chicago["travel"]["calendarMinutes"] = chicago_arrival
	chicago["travel"]["calendarWeekIndex"] = TravelCalendar.week_index(chicago_arrival)
	chicago["travel"]["calendarText"] = TravelCalendar.iso_text(chicago_arrival)
	chicago["travel"]["lastTravel"]["arrivedAtMinutes"] = chicago_arrival
	chicago["travel"]["lastTravel"]["minutes"] = 365
	var chicago_id := SaveStore.write_entry("manual", 3, chicago)
	app.begin_new_run()
	_check(app.load_save(chicago_id) and TravelCalendar.iso_text(app.calendar_minutes) == "2537-05-25 14:05" and app.current_location_id == CHICAGO and int(app.last_travel["minutes"]) == 365, "a save from the 365-minute flight keeps 14:05 and its history")
	_travel(NEW_YORK)
	_check(TravelCalendar.iso_text(app.calendar_minutes) == "2537-05-25 20:05", "the return flight then charges 6 h: 14:05 -> 20:05")


# Route text as the map shows it and as the core describes it, in both languages.
func _test_player_text() -> void:
	var forbidden := RegEx.create_from_string(FORBIDDEN_TEXT)
	var codes := RegEx.create_from_string(FORBIDDEN_CODES)
	var decimal := RegEx.create_from_string("\\d\\.\\d")
	var clock := RegEx.create_from_string(CLOCK_TEXT)
	var expected_zh := {60: "1小时", 300: "5小时", 360: "6小时"}
	var expected_en := {60: "1 h", 300: "5 h", 360: "6 h"}
	var map_adapter: GDScript = load(MAP_ADAPTER_PATH)
	var world_map: GDScript = load(WORLD_MAP_PATH)
	var texts_checked := 0
	for language in ["zh", "en"]:
		app.language = language
		for trip in TRIPS:
			app.begin_new_run()
			app.current_location_id = trip[0]
			app.discovered_locations[trip[1]] = true
			var adapter = map_adapter.new(app)
			var state: Dictionary = adapter.preview(trip[1])
			if not _check(state["status"] == "ready" and state["options"].size() == 1, "map card is ready for %s (%s)" % [trip[2], language]):
				continue
			var card: String = world_map.route_option_text(state["options"][0])
			var lines: String = "\n".join(app.travel_preview_lines(app.preview_travel(trip[1])))
			adapter.cancel()
			var hours: String = (expected_zh if language == "zh" else expected_en)[int(trip[4])]
			var arrival: String = app.calendar_date_text_at(app.calendar_minutes + int(trip[4]))
			for text: String in [card, lines]:
				texts_checked += 1
				var flat: String = text.replace("\n", " | ")
				_check(text.contains(hours) and text.contains(arrival) and not text.contains("分钟") and not text.contains(" min"), "%s shows %s and the arrival date, no minutes (%s): %s" % [trip[2], hours, language, flat])
				_check(clock.search(text) == null, "%s shows the arrival date only, no clock time (%s): %s" % [trip[2], language, flat])
				_check(text.contains(app.text_for("travel_mode_" + String(trip[3]))) and text.contains("约" if language == "zh" else ("~" if text == card else "about")), "%s names the mode and an approximate distance (%s): %s" % [trip[2], language, flat])
				_check(forbidden.search(text) == null and codes.search(text) == null and decimal.search(text) == null and not text.contains("估算") and not text.to_lower().contains("estimat"), "%s has no airport, component, decimal or estimate wording (%s): %s" % [trip[2], language, flat])
	# The map calendar shows the date alone, also for an old save's off-hour clock (08:35).
	var dates_checked := 0
	for language in ["zh", "en"]:
		app.language = language
		app.begin_new_run()
		_set_clock(2537, 5, 25, 8, 35)
		var shown: String = map_adapter.new(app).calendar_text()
		dates_checked += 1
		_check(shown == app.calendar_date_text() and clock.search(shown) == null and TravelCalendar.iso_text(app.calendar_minutes) == "2537-05-25 08:35", "map calendar shows the date only while the internal clock keeps 08:35 (%s): %s" % [language, shown])
	_check(dates_checked == 2, "map calendar checked in zh and en")
	app.language = "zh"
	# A runtime error ends this function early without failing a check; the count catches that.
	_check(texts_checked == 2 * TRIPS.size() * 2, "route text checked for all 8 trips, map card and core lines, zh and en (%d of 32)" % texts_checked)


# Every string literal in the game's scripts and scenes, so no dialogue or label brings airports back.
func _test_string_tables() -> void:
	var forbidden := RegEx.create_from_string(FORBIDDEN_TEXT)
	var codes := RegEx.create_from_string(FORBIDDEN_CODES)
	var literal := RegEx.create_from_string("\"(?:[^\"\\\\\\n]|\\\\.)*\"")
	var hits: PackedStringArray = []
	var scanned := 0
	for folder in ["res://scripts", "res://scenes"]:
		for file_name in DirAccess.get_files_at(folder):
			if not (file_name.ends_with(".gd") or file_name.ends_with(".tscn")) or file_name == "world_route_registry.gd":
				continue
			scanned += 1
			var source := FileAccess.get_file_as_string(folder + "/" + file_name)
			for line in source.split("\n"):
				if line.strip_edges().begins_with("#"):
					continue
				for found in literal.search_all(line):
					var text := found.get_string()
					if forbidden.search(text) != null or codes.search(text) != null:
						hits.append("%s: %s" % [file_name, text])
	_check(scanned > 20 and hits.is_empty(), "no string in %d game scripts and scenes names an airport or trip component: %s" % [scanned, "; ".join(hits)])


func _segment(data: Dictionary, segment_id: String) -> Dictionary:
	for segment in data["segments"]:
		if segment["id"] == segment_id:
			return segment
	return {}


func _set_clock(year: int, month: int, day: int, hour: int, minute: int) -> void:
	app.calendar_minutes = TravelCalendar.to_minutes(year, month, day, hour, minute)
	app.calendar_week_index = TravelCalendar.week_index(app.calendar_minutes)


func _travel(destination: String) -> Dictionary:
	var preview: Dictionary = app.preview_travel(destination)
	if not preview.get("ok", false):
		return preview
	return app.settle_travel()


func _clear_saves() -> void:
	var directory := DirAccess.open(SAVE_ROOT)
	if directory == null:
		return
	for name in directory.get_files():
		directory.remove(name)


func _check(condition: bool, label: String) -> bool:
	checks += 1
	if not condition:
		failures += 1
		push_error("M2 whole-hour check failed: " + label)
	return condition
