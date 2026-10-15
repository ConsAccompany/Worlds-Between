extends SceneTree

# Core checks for the revised M2 global travel calendar and route data (no map UI).
# Run: Godot --headless --path game --script res://tests/<this file>
# 2026-10-15: creator-approved US science sphere. The Shanghai set is kept as hidden retired aliases.
const NEW_YORK := "earth.us.ny.new-york-city"
const YONKERS := "earth.us.ny.yonkers-outskirts"
const WASHINGTON := "earth.us.dc.washington-ruins"
const CHICAGO := "earth.us.il.chicago"
const RETIRED := {"earth.cn.shanghai": NEW_YORK, "earth.cn.shanghai.songjiang-outskirts": YONKERS, "earth.cn.liangzhu-ruins": WASHINGTON}
const AIR_NYC_CHICAGO := "route.air.nyc__chicago"
const PENDING_YONKERS_CHICAGO := "route.pending.yonkers__chicago"
const SAVE_ROOT := "user://test-saves/m2-global-travel"

var app: Node
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
	_test_calendar_facts()
	_test_route_data()
	_test_validator_rules()
	_test_cumulative_short_trips()
	_test_rollover_by_travel()
	_test_cancel_stale_and_free_actions()
	_test_map_adapter_contract()
	_test_week_hook()
	_test_save_load_without_recharge()
	_test_legacy_and_unknown_id_migration()
	_test_shanghai_era_save_migration()
	_test_air_trip()
	_test_bilingual_text()
	_clear_saves()
	if failures > 0:
		push_error("GLOBAL_TRAVEL_CORE failed checks: %d" % failures)
		quit(1)
		return
	print("GLOBAL_TRAVEL_CORE_OK")
	quit(0)


func _test_calendar_facts() -> void:
	_check(TravelCalendar.days_from_civil(1970, 1, 1) == 0, "epoch day 0")
	_check(TravelCalendar.days_from_civil(2000, 1, 1) == 10957, "2000-01-01 is 10957 days after 1970-01-01")
	# Known weekdays (1 = Monday): 2000-01-01 Saturday, 2024-02-29 Thursday, 2026-10-15 Thursday.
	_check(int(TravelCalendar.from_minutes(TravelCalendar.to_minutes(2000, 1, 1))["weekday"]) == 6, "2000-01-01 Saturday")
	_check(int(TravelCalendar.from_minutes(TravelCalendar.to_minutes(2024, 2, 29))["weekday"]) == 4, "2024-02-29 Thursday")
	_check(int(TravelCalendar.from_minutes(TravelCalendar.to_minutes(2026, 10, 15, 12, 0))["weekday"]) == 4, "2026-10-15 Thursday")
	# Sweep 1900..2100: each day round-trips, years have 365/366 days, and century rules hold.
	var per_year: Dictionary = {}
	var leap_years_1901_2000 := 0
	var first := TravelCalendar.days_from_civil(1900, 1, 1)
	var last := TravelCalendar.days_from_civil(2100, 12, 31)
	var round_trip_ok := true
	for day in range(first, last + 1):
		var date := TravelCalendar.civil_from_days(day)
		if TravelCalendar.days_from_civil(int(date["year"]), int(date["month"]), int(date["day"])) != day:
			round_trip_ok = false
		per_year[date["year"]] = int(per_year.get(date["year"], 0)) + 1
	for year in per_year:
		if int(year) >= 1901 and int(year) <= 2000 and int(per_year[year]) == 366:
			leap_years_1901_2000 += 1
	_check(round_trip_ok, "every day 1900-2100 round-trips")
	_check(per_year.size() == 201 and per_year[1900] == 365 and per_year[2000] == 366 and per_year[2023] == 365 and per_year[2024] == 366 and per_year[2100] == 365, "year lengths incl. 1900/2100 non-leap and 2000 leap")
	_check(leap_years_1901_2000 == 25, "25 leap years in 1901-2000")
	_check(TravelCalendar.to_minutes(2026, 12, 31, 23, 59) + 1 == TravelCalendar.to_minutes(2027, 1, 1), "one minute past 2026-12-31 23:59 is 2027-01-01 00:00")
	var sunday_end := TravelCalendar.to_minutes(2026, 10, 18, 23, 59)
	_check(TravelCalendar.week_index(TravelCalendar.to_minutes(2026, 10, 12)) == TravelCalendar.week_index(sunday_end), "Mon 10-12 and Sun 10-18 share a week")
	_check(TravelCalendar.week_index(sunday_end + 1) == TravelCalendar.week_index(sunday_end) + 1, "week changes at Monday 2026-10-19 00:00")
	var leap_helper_agrees := true
	for year in per_year:
		leap_helper_agrees = leap_helper_agrees and TravelCalendar.is_leap_year(int(year)) == (int(per_year[year]) == 366) and TravelCalendar.days_in_month(int(year), 2) == int(per_year[year]) - 337
	_check(leap_helper_agrees, "is_leap_year/days_in_month agree with counted year lengths 1900-2100")
	# Far-future checks for the 2537 timeline: proleptic Gregorian, so 2600 is not a leap year.
	_check(int(TravelCalendar.from_minutes(TravelCalendar.to_minutes(2537, 5, 25))["weekday"]) == 6, "2537-05-25 is a Saturday (proleptic Gregorian)")
	var far_ok := true
	for day in range(TravelCalendar.days_from_civil(2500, 1, 1), TravelCalendar.days_from_civil(2700, 12, 31) + 1):
		var far := TravelCalendar.civil_from_days(day)
		far_ok = far_ok and TravelCalendar.days_from_civil(int(far["year"]), int(far["month"]), int(far["day"])) == day
	_check(far_ok and TravelCalendar.is_leap_year(2540) and not TravelCalendar.is_leap_year(2600) and TravelCalendar.is_leap_year(2800), "2500-2700 round-trips; 2540 leap, 2600 not")
	_check(TravelCalendar.iso_text(TravelCalendar.to_minutes(2537, 5, 25, 8, 0)) == "2537-05-25 08:00", "far-future ISO text")
	_check(not bool(TravelCalendar.parse_minutes("2027-02-29")["ok"]) and bool(TravelCalendar.parse_minutes("2028-02-29")["ok"]) and not bool(TravelCalendar.parse_minutes("2100-02-29")["ok"]) and bool(TravelCalendar.parse_minutes("2000-02-29")["ok"]), "Feb 29 only parses in Gregorian leap years")


func _test_route_data() -> void:
	var registry: WorldRouteRegistry = app.travel_registry()
	_check(registry.is_valid(), "shipped travel data validates: " + "; ".join(registry.errors))
	var earth := 0
	for region_id in registry.regions:
		earth += int(registry.regions[region_id]["planet"] == "earth")
	_check(earth == 5 and registry.regions["offworld"]["access"] == "portal" and registry.regions["offworld"]["planet"] != "earth", "five Earth spheres plus a separate portal-only final planet")
	var sphere_ids: Array = registry.regions.keys()
	sphere_ids.sort()
	_check(sphere_ids == ["culture", "magic", "nature", "offworld", "science", "wuxia"], "regions are science, magic, wuxia, nature, culture and the final planet: " + str(sphere_ids))
	# Culture is the former Fantasy sphere: "fantasy" survives only as an explicit alias, never as an active region.
	_check(not registry.regions.has("fantasy") and registry.resolve_region_id("fantasy") == "culture" and registry.resolve_region_id("nonexistent") == "", "fantasy is an alias of culture, not an active region")
	for region_id in registry.regions:
		if region_id != "science":
			var has_place := false
			for location_id in registry.location_order:
				has_place = has_place or registry.locations[location_id]["regionId"] == region_id
			_check(not has_place, "no places yet outside the science sphere: " + region_id)
	_check(registry.regions["science"].get("countryCodes", []) == ["US", "CA"], "science sphere is the US and Canada only")
	for location_id in registry.location_order:
		var place: Dictionary = registry.locations[location_id]
		if place["regionId"] == "science":
			_check(place.get("countryCode", "") in ["US", "CA"], "science place is in the US or Canada: " + location_id)
	_check(registry.calendar_start_minutes == TravelCalendar.to_minutes(2537, 5, 25, 8, 0), "new runs start 2537-05-25 (08:00 is an engineering placeholder time of day)")
	_check(registry.start_location_id == NEW_YORK, "New York City is the science hub and start location")
	_check(registry.location_for_scene("scifi.city") == NEW_YORK and registry.location_for_scene("scifi.outskirts") == YONKERS and registry.location_for_scene("scifi.ruins") == WASHINGTON and registry.location_for_scene("scifi.loop") == CHICAGO, "scene IDs bind to the US places")
	# Retired Shanghai-set IDs resolve to their successors but are never listed or discoverable.
	for retired_id in RETIRED:
		_check(registry.resolve_location_id(retired_id) == RETIRED[retired_id] and not registry.location_order.has(retired_id) and registry.retired_locations.has(retired_id), "retired id resolves to its US successor and stays hidden: " + retired_id)
	_check(not app.travel_location_ids().has("earth.cn.shanghai") and app.travel_location_ids().size() == 4, "only the four US places are listed")
	# Geography sanity from the stored coordinates.
	var nyc: Dictionary = registry.location(NEW_YORK)["coordinates"]
	var yonkers: Dictionary = registry.location(YONKERS)["coordinates"]
	var dc: Dictionary = registry.location(WASHINGTON)["coordinates"]
	var chicago: Dictionary = registry.location(CHICAGO)["coordinates"]
	_check(float(yonkers["lat"]) > float(nyc["lat"]) and absf(float(yonkers["lon"]) - float(nyc["lon"])) < 0.3, "Yonkers lies north of Lower Manhattan")
	_check(float(dc["lat"]) < float(nyc["lat"]) and float(dc["lon"]) < float(nyc["lon"]), "Washington lies south-west of New York")
	_check(float(chicago["lon"]) < -87.0 and float(chicago["lat"]) > 41.5, "Chicago lies far west on Lake Michigan")
	var gc_yonkers := registry.great_circle_km(NEW_YORK, YONKERS)
	var gc_dc := registry.great_circle_km(NEW_YORK, WASHINGTON)
	var gc_chicago := registry.great_circle_km(NEW_YORK, CHICAGO)
	_check(gc_yonkers > 15.0 and gc_yonkers < 35.0 and gc_dc > 300.0 and gc_dc < 350.0 and gc_chicago > 1100.0 and gc_chicago < 1200.0, "real-distance plausible (%.1f, %.1f, %.1f km)" % [gc_yonkers, gc_dc, gc_chicago])
	var seen_air := false
	for route_id in registry.route_order:
		var stored: Dictionary = registry.routes[route_id]
		for option in registry.routes_between(stored["fromLocationId"], stored["toLocationId"]):
			if not option["available"]:
				continue
			_check(not option["verified"] and option["estimate"], "every shipped figure is an estimate, never verified: " + String(option["option_id"]))
			for leg in option["legs"]:
				_check(String(leg["source"].get("url", "")) != "" and leg["verification_status"] == "preliminary-estimate", "leg has a source and is a preliminary estimate: " + String(leg["segment_id"]))
				var straight: float = registry.great_circle_km(leg["from_location_id"], leg["to_location_id"])
				if leg["mode"] == "car":
					# A road can never be shorter than the straight line; average speed must be plausible.
					_check(float(leg["road_distance_km"]) >= straight, "road km >= great-circle km: " + String(leg["segment_id"]))
					_check(float(leg["road_distance_km"]) / (float(leg["minutes"]) / 60.0) <= 130.0, "car average speed <= 130 km/h: " + String(leg["segment_id"]))
				else:
					seen_air = true
					var segment: Dictionary = registry.segments[leg["segment_id"]]
					var parts := 0
					for field in WorldRouteRegistry.AIR_MINUTE_FIELDS:
						parts += int(segment[field])
					_check(int(leg["minutes"]) == parts + int(segment.get("doorToDoorAllowanceMinutes", 0)) and int(segment["checkInAndWaitMinutes"]) > 0 and int(segment["airportAccessMinutes"]) > 0 and int(segment["airportEgressMinutes"]) > 0, "air leg is door to door (access + check-in/wait + flight + egress): " + String(leg["segment_id"]))
					_check(absf(float(leg["air_distance_km"]) - straight) < 0.1 * straight, "flight km near the city great circle: " + String(leg["segment_id"]))
					_check(float(leg["air_distance_km"]) / (float(segment["flightMinutes"]) / 60.0) < 900.0, "flight speed below airliner cruise: " + String(leg["segment_id"]))
	_check(seen_air, "the NYC-Chicago air route is present")
	var air: Array[Dictionary] = registry.routes_between(NEW_YORK, CHICAGO)
	_check(air.size() == 1 and air[0]["option_id"] == AIR_NYC_CHICAGO and air[0]["available"] and air[0]["mode"] == "air" and air[0]["road_distance_km"] == null and float(air[0]["air_distance_km"]) > 1000.0, "NYC to Chicago is one air option with a flight distance")
	var back: Array[Dictionary] = registry.routes_between(CHICAGO, NEW_YORK)
	_check(back.size() == 1 and back[0]["available"] and back[0]["legs"][0]["from_location_id"] == CHICAGO and int(back[0]["total_minutes"]) > 0, "Chicago to NYC has its own sourced return flight")
	var pending: Array[Dictionary] = registry.routes_between(YONKERS, CHICAGO)
	_check(pending.size() == 1 and pending[0]["option_id"] == PENDING_YONKERS_CHICAGO and not pending[0]["available"] and int(pending[0]["total_minutes"]) < 0, "Yonkers-Chicago has no researched route and shows no time")
	app.begin_new_run()
	_check(app.preview_travel("earth.xx.nowhere")["reason"] == "unknown-destination", "unknown destination rejected")
	app.discovered_locations.erase(WASHINGTON)
	_check(app.preview_travel(WASHINGTON)["reason"] == "destination-not-discovered", "undiscovered destination rejected")
	app.begin_new_run()


func _fixture() -> Dictionary:
	var source := {"name": "fixture", "url": "https://example.invalid/fixture"}
	return {
		"schemaVersion": 1,
		"calendar": {"startDate": "2026-01-01", "startTime": "00:00"},
		"regions": [
			{"id": "r.a", "planet": "earth", "names": {"zh": "甲", "en": "A"}, "access": "car-air"},
			{"id": "r.b", "planet": "earth", "names": {"zh": "乙", "en": "B"}, "access": "car-air"},
			{"id": "r.c", "planet": "earth", "names": {"zh": "丙", "en": "C"}, "access": "car-air"},
			{"id": "r.d", "planet": "earth", "names": {"zh": "丁", "en": "D"}, "access": "car-air"},
			{"id": "r.e", "planet": "earth", "names": {"zh": "戊", "en": "E"}, "access": "car-air", "legacyIds": ["r.old"]},
			{"id": "r.portal", "planet": "elsewhere", "names": {"zh": "外", "en": "Out"}, "access": "portal"},
		],
		"startLocationId": "loc.one",
		"locations": [
			{"id": "loc.one", "names": {"zh": "一", "en": "One"}, "type": "city", "regionId": "r.a", "coordinates": {"lat": 10.0, "lon": 10.0}, "coordinateSource": source, "discovery": {"initial": true}},
			{"id": "loc.two", "names": {"zh": "二", "en": "Two"}, "type": "city", "regionId": "r.a", "coordinates": {"lat": 10.0, "lon": 12.0}, "coordinateSource": source, "discovery": {"initial": true}},
			{"id": "loc.three", "names": {"zh": "三", "en": "Three"}, "type": "ruins", "regionId": "r.a", "coordinates": {"lat": 11.0, "lon": 12.0}, "coordinateSource": source, "discovery": {"initial": true}},
			{"id": "loc.gate", "names": {"zh": "门", "en": "Gate"}, "type": "portal", "regionId": "r.portal", "coordinates": {"lat": 0.0, "lon": 0.0}, "discovery": {"initial": false}},
		],
		"segments": [
			{"id": "seg.air", "mode": "air", "fromLocationId": "loc.one", "toLocationId": "loc.two", "flightDistanceKm": 219.0, "airportAccessMinutes": 50, "checkInAndWaitMinutes": 90, "flightMinutes": 55, "airportEgressMinutes": 40, "bidirectional": true, "verification": {"status": "verified", "source": source}},
			{"id": "seg.car", "mode": "car", "fromLocationId": "loc.two", "toLocationId": "loc.three", "roadDistanceKm": 140.0, "referenceDurationMinutes": 100, "doorToDoorAllowanceMinutes": 15, "bidirectional": true, "verification": {"status": "verified", "source": source}},
		],
		"routes": [
			{"id": "route.mixed", "fromLocationId": "loc.one", "toLocationId": "loc.three", "status": "available", "bidirectional": true, "viaLocationIds": ["loc.two"], "legs": [{"segmentId": "seg.air"}, {"segmentId": "seg.car"}]},
		],
	}


func _test_validator_rules() -> void:
	var good := WorldRouteRegistry.from_dictionary(_fixture())
	_check(good.is_valid(), "fixture validates: " + "; ".join(good.errors))
	var mixed: Dictionary = good.routes_between("loc.one", "loc.three")[0]
	# Air legs count airport access, check-in/wait and egress, not just flight time.
	_check(int(mixed["total_minutes"]) == (50 + 90 + 55 + 40) + (100 + 15) and mixed["modes"] == ["air", "car"], "air+car itinerary sums door-to-door minutes")
	_check(is_equal_approx(float(mixed["road_distance_km"]), 140.0) and is_equal_approx(float(mixed["air_distance_km"]), 219.0), "road and flight distances kept in separate fields")
	var cases := {
		"air leg without airport access": func(d: Dictionary) -> void: d["segments"][0].erase("airportAccessMinutes"),
		"walking mode": func(d: Dictionary) -> void: d["segments"][1]["mode"] = "walk",
		"car into portal region": func(d: Dictionary) -> void: d["segments"][1]["toLocationId"] = "loc.gate",
		"leg without source url": func(d: Dictionary) -> void: d["segments"][1]["verification"]["source"].erase("url"),
		"declared total mismatch": func(d: Dictionary) -> void: d["routes"][0]["declaredTotalMinutes"] = 300,
		"legs that do not chain": func(d: Dictionary) -> void: d["routes"][0]["legs"].reverse(),
		"via list not matching stops": func(d: Dictionary) -> void: d["routes"][0]["viaLocationIds"] = [],
		"duplicate id": func(d: Dictionary) -> void: d["locations"][1]["id"] = "loc.one",
		"only four Earth regions": func(d: Dictionary) -> void: d["regions"].remove_at(3),
		"legacy region id reused by an active region": func(d: Dictionary) -> void: d["regions"][4]["legacyIds"] = ["r.a"],
		"location in an aliased region id": func(d: Dictionary) -> void: d["locations"][2]["regionId"] = "r.old",
		"place outside its region's countries (fixture places have no US or CA code)": func(d: Dictionary) -> void: d["regions"][0]["countryCodes"] = ["US", "CA"],
		"fractional minutes": func(d: Dictionary) -> void: d["segments"][1]["referenceDurationMinutes"] = 99.5,
		"available route with no legs": func(d: Dictionary) -> void: d["routes"][0]["legs"] = [],
	}
	for label in cases:
		var broken := _fixture()
		cases[label].call(broken)
		_check(not WorldRouteRegistry.from_dictionary(broken).is_valid(), "validator rejects " + label)


func _set_clock(year: int, month: int, day: int, hour: int, minute: int) -> void:
	app.calendar_minutes = TravelCalendar.to_minutes(year, month, day, hour, minute)
	app.calendar_week_index = TravelCalendar.week_index(app.calendar_minutes)


func _travel(destination: String, route_id: String = "") -> Dictionary:
	var preview: Dictionary = app.preview_travel(destination, route_id)
	if not preview.get("ok", false):
		return preview
	return app.settle_travel()


func _test_cumulative_short_trips() -> void:
	app.begin_new_run()
	_set_clock(2537, 5, 25, 22, 50)
	var start: int = app.calendar_minutes
	var leg := int(app.travel_registry().routes_between(NEW_YORK, YONKERS)[0]["total_minutes"])
	var targets := [YONKERS, NEW_YORK, YONKERS, NEW_YORK, YONKERS]
	var charged_each_ok := true
	for target in targets:
		var before: int = app.calendar_minutes
		var result := _travel(target)
		charged_each_ok = charged_each_ok and result.get("departed", false) and int(result["minutes_charged"]) == leg and app.calendar_minutes - before == leg
	_check(charged_each_ok, "each short trip charges exactly its minutes (no rounding to hours or days)")
	_check(app.calendar_minutes == start + leg * targets.size(), "short trips accumulate")
	var expected_minute_of_day := (22 * 60 + 50 + leg * targets.size())
	var dt: Dictionary = app.calendar_datetime()
	_check(int(dt["day"]) == 25 + expected_minute_of_day / 1440 and int(dt["minute_of_day"]) == expected_minute_of_day % 1440 and int(dt["month"]) == 5, "carried-over minutes roll the date only past midnight")
	_check(app.current_location_id == YONKERS and app.current_destination_id == "scifi.outskirts", "arrival sets location and its scene")


func _test_rollover_by_travel() -> void:
	app.begin_new_run()
	var leg := int(app.travel_registry().routes_between(NEW_YORK, WASHINGTON)[0]["total_minutes"])
	_set_clock(2537, 12, 31, 23, 0)
	var before: int = app.calendar_minutes
	var preview: Dictionary = app.preview_travel(WASHINGTON)
	_check(app.calendar_minutes == before and preview["arrival"]["year"] == 2538, "preview shows next-year arrival without moving the clock")
	app.confirm_travel()
	var dt: Dictionary = app.calendar_datetime()
	_check(int(dt["year"]) == 2538 and int(dt["month"]) == 1 and int(dt["day"]) == 1 and int(dt["minute_of_day"]) == 23 * 60 + leg - 1440, "travel across New Year's midnight")
	_check(int(dt["minute_of_day"]) == int(preview["arrival"]["minute_of_day"]) and int(preview["calendar_days_advanced"]) == 1, "confirmed arrival matches preview")
	app.begin_new_run()
	_set_clock(2540, 2, 28, 23, 30)
	_travel(WASHINGTON)
	_check(int(app.calendar_datetime()["month"]) == 2 and int(app.calendar_datetime()["day"]) == 29, "leap year 2540 arrives on Feb 29")
	app.begin_new_run()
	_set_clock(2539, 2, 28, 23, 30)
	_travel(WASHINGTON)
	_check(int(app.calendar_datetime()["month"]) == 3 and int(app.calendar_datetime()["day"]) == 1, "non-leap 2539 arrives on Mar 1")
	app.begin_new_run()
	_set_clock(2600, 2, 28, 23, 30)
	_travel(WASHINGTON)
	_check(int(app.calendar_datetime()["month"]) == 3 and int(app.calendar_datetime()["day"]) == 1, "century year 2600 is not leap")


func _test_cancel_stale_and_free_actions() -> void:
	app.begin_new_run()
	calendar_events.clear()
	var start: int = app.calendar_minutes
	var preview: Dictionary = app.preview_travel(WASHINGTON)
	_check(preview["kind"] == "travel" and int(preview["total_minutes"]) > 0 and app.calendar_minutes == start, "preview is free")
	app.cancel_travel_preview()
	var after_cancel: Dictionary = app.settle_travel()
	_check(not after_cancel["departed"] and app.calendar_minutes == start and app.current_location_id == NEW_YORK and calendar_events.is_empty(), "cancel costs zero time and leaves nothing to confirm")
	app.preview_travel(WASHINGTON)
	app.advance_calendar(30, "rest")
	var stale: Dictionary = app.settle_travel()
	_check(not stale["departed"] and stale["reason"] == "stale-preview" and app.calendar_minutes == start + 30 and app.current_location_id == NEW_YORK, "preview made before the clock changed cannot be confirmed")
	var before: int = app.calendar_minutes
	var same: Dictionary = app.preview_travel(NEW_YORK)
	var same_result: Dictionary = app.settle_travel()
	_check(same["kind"] == "same_location" and not same_result["departed"] and int(same_result["minutes_charged"]) == 0 and app.calendar_minutes == before, "same-location choice charges nothing")
	_check(app.enter_current_location_scene() and app.current_destination_id == "scifi.city" and app.calendar_minutes == before, "entering the local scene is free")
	app.select_destination("scifi.city")
	_check(app.calendar_minutes == before, "legacy scene entry does not touch the calendar")
	var first: Dictionary = _travel(YONKERS)
	var after_first: int = app.calendar_minutes
	var again: Dictionary = app.settle_travel()
	_check(first["departed"] and not again["departed"] and app.calendar_minutes == after_first, "a confirmed trip cannot be charged twice")
	app.preview_travel(CHICAGO, PENDING_YONKERS_CHICAGO)
	var blocked: Dictionary = app.settle_travel()
	_check(not blocked["departed"] and app.calendar_minutes == after_first and app.current_location_id == YONKERS, "a route with no researched figures cannot be travelled")
	var none: Dictionary = app.preview_travel(CHICAGO)
	_check(none["kind"] == "unavailable" and int(none["total_minutes"]) == 0 and app.calendar_minutes == after_first, "Yonkers to Chicago offers no invented time")
	var direct: Dictionary = app.preview_travel(WASHINGTON)
	_check(direct["kind"] == "travel" and direct["option_id"] == "route.car.yonkers__washington-ruins", "Yonkers to Washington uses its own sourced drive")
	app.cancel_travel_preview()
	_check(not app.advance_calendar(-5, "test") and app.calendar_minutes == after_first, "the clock never runs backwards")


# The world map adapter calls travel_route_options(from, to), travel_arrival_preview(minutes) and
# confirm_travel(to, option_id) -> bool with scene destination IDs.
func _test_map_adapter_contract() -> void:
	app.begin_new_run()
	var options: Array = app.travel_route_options("scifi.city", "scifi.outskirts")
	_check(options.size() == 1, "scene-ID route query finds the New York-Yonkers route")
	if options.is_empty():
		return
	var option: Dictionary = options[0]
	_check(option.has_all(["option_id", "mode", "road_distance_km", "air_distance_km", "total_minutes", "verified", "source"]) and option["mode"] == "car" and option["air_distance_km"] == null and typeof(option["total_minutes"]) == TYPE_INT and String(option["source"]).contains("OSRM"), "route option has the map adapter shape")
	_check(not option["verified"] and option["estimate"], "preliminary third-party figures are flagged as estimates, never as verified")
	var arrival: Dictionary = app.travel_arrival_preview(int(option["total_minutes"]))
	_check(arrival.has_all(["year", "month", "day"]) and int(arrival["minutes"]) == app.calendar_minutes + int(option["total_minutes"]), "arrival preview is computed from the current clock")
	var before: int = app.calendar_minutes
	_check(app.confirm_travel("scifi.outskirts", String(option["option_id"])) and app.calendar_minutes == before + int(option["total_minutes"]) and app.current_location_id == YONKERS, "one-shot confirm with a scene ID and option departs")
	var after: int = app.calendar_minutes
	_check(not app.confirm_travel("scifi.loop", PENDING_YONKERS_CHICAGO) and app.calendar_minutes == after, "one-shot confirm of an unavailable option does not depart")
	_check(not app.confirm_travel("scifi.outskirts") and app.calendar_minutes == after, "one-shot confirm to the current place does not depart")


func _test_week_hook() -> void:
	app.begin_new_run()
	# 2537-05-26 is a Sunday; the Washington drive runs past Monday 00:00.
	_set_clock(2537, 5, 26, 22, 30)
	week_events.clear()
	var week: int = app.calendar_week_index
	var preview: Dictionary = app.preview_travel(WASHINGTON)
	_check(week_events.is_empty() and int(preview["weeks_crossed"]) == 1, "preview reports the week change without emitting it")
	app.confirm_travel()
	_check(week_events == [[week, week + 1]], "Sunday-night trip into Monday emits one week transition")
	_travel(NEW_YORK)
	_check(week_events.size() == 1, "trip within the week emits nothing")
	app.advance_calendar(TravelCalendar.MINUTES_PER_WEEK * 3, "rest")
	_check(week_events.size() == 2 and week_events[1] == [week + 1, week + 4], "multi-week advance reports all weeks crossed in one event")


func _test_save_load_without_recharge() -> void:
	app.begin_new_run()
	_set_clock(2537, 5, 26, 23, 0)
	_travel(WASHINGTON)
	var saved_minutes: int = app.calendar_minutes
	var saved_week: int = app.calendar_week_index
	app.save_return_scene = "res://scenes/scifi_world_map.tscn"
	var id: String = app.write_manual_save(1)
	_check(id != "", "manual save written after arrival")
	_travel(NEW_YORK)
	app.preview_travel(YONKERS)
	week_events.clear()
	calendar_events.clear()
	_check(app.load_save(id), "save loads")
	_check(app.calendar_minutes == saved_minutes and typeof(app.calendar_minutes) == TYPE_INT and app.calendar_week_index == saved_week and app.current_location_id == WASHINGTON, "load restores exact clock and location")
	_check(week_events.is_empty() and calendar_events.is_empty(), "loading emits no calendar or week settlement events")
	_check(not app.confirm_travel() and app.calendar_minutes == saved_minutes, "a preview from before loading cannot be confirmed")
	app.load_save(id)
	_check(app.calendar_minutes == saved_minutes and week_events.is_empty(), "loading twice adds no time")
	var entry := SaveStore.read_entry(id)
	_check(entry["snapshot"]["travel"]["calendarText"] == TravelCalendar.iso_text(saved_minutes), "save carries a readable date beside the minute count")
	var broken: Dictionary = entry["snapshot"].duplicate(true)
	broken["travel"]["calendarMinutes"] = "tomorrow"
	var broken_id := SaveStore.write_entry("manual", 3, broken)
	_travel(NEW_YORK)
	var before_broken: int = app.calendar_minutes
	_check(not app.load_save(broken_id) and app.calendar_minutes == before_broken and app.current_location_id == NEW_YORK, "malformed travel block is rejected without changing state")


func _test_legacy_and_unknown_id_migration() -> void:
	app.begin_new_run()
	var legacy: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	legacy.erase("travel")
	# A real pre-travel save is older than the commerce block too, so it has neither.
	legacy.erase("commerce")
	legacy["destination"] = "scifi.outskirts"
	legacy["areasVisited"] = {"scifi.ruins": true, "scifi.outskirts": true}
	legacy["playTimeSeconds"] = 36000.0
	var legacy_id := SaveStore.write_entry("manual", 2, legacy)
	_set_clock(2031, 6, 1, 12, 0)
	week_events.clear()
	_check(app.load_save(legacy_id), "pre-travel save still loads")
	var registry: WorldRouteRegistry = app.travel_registry()
	_check(app.calendar_minutes == registry.calendar_start_minutes and app.travel_state_migrated, "legacy save starts at the calendar start, no phantom days from 10 h play time")
	_check(app.current_location_id == YONKERS and app.discovered_locations.has(WASHINGTON) and app.discovered_locations.has(NEW_YORK), "legacy scene and visits map to real places")
	_check(week_events.is_empty(), "migration emits no week settlement")
	app.save_return_scene = "res://scenes/scifi_world_map.tscn"
	var resaved: String = app.write_manual_save(2)
	app.load_save(resaved)
	_check(not app.travel_state_migrated and app.calendar_minutes == registry.calendar_start_minutes, "migrated save re-saves with a travel block")
	var future: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	future["travel"]["locationId"] = "earth.xx.retired-place"
	future["travel"]["discovered"]["earth.xx.retired-place"] = true
	future["destination"] = "scifi.ruins"
	var future_id := SaveStore.write_entry("manual", 3, future)
	_check(app.load_save(future_id), "save naming an unknown place still loads")
	_check(app.current_location_id == WASHINGTON and app.discovered_locations.has("earth.xx.retired-place") and not app.travel_location_ids().has("earth.xx.retired-place"), "unknown location falls back to its scene place; unknown discovery is kept but hidden")


# A save made with the v01 (Shanghai set) data: old location IDs, an old 2026 date and old
# lastTravel IDs. It must load, keep its exact clock and land on the US successors.
func _test_shanghai_era_save_migration() -> void:
	app.begin_new_run()
	_set_clock(2026, 4, 8, 15, 30)
	# A real v01 save had its commerce cursor on its own clock's week.
	app._reset_commerce_state()
	var old: Dictionary = app.make_snapshot("map", Vector2.ZERO, "manual_note")
	old["destination"] = "scifi.ruins"
	old["travel"]["locationId"] = "earth.cn.liangzhu-ruins"
	old["travel"]["discovered"] = {"earth.cn.shanghai": true, "earth.cn.shanghai.songjiang-outskirts": true, "earth.cn.liangzhu-ruins": true}
	old["travel"]["lastTravel"] = {"optionId": "route.car.shanghai__liangzhu-ruins", "fromLocationId": "earth.cn.shanghai", "toLocationId": "earth.cn.liangzhu-ruins", "minutes": 120}
	var old_minutes: int = app.calendar_minutes
	var old_id := SaveStore.write_entry("manual", 2, old)
	app.begin_new_run()
	week_events.clear()
	calendar_events.clear()
	_check(app.load_save(old_id), "a Shanghai-era save still loads")
	_check(app.calendar_minutes == old_minutes and TravelCalendar.iso_text(app.calendar_minutes) == "2026-04-08 15:30", "its saved date is kept exactly (no shift to 2537)")
	_check(app.current_location_id == WASHINGTON and app.current_destination_id == "scifi.ruins", "Liangzhu ID resolves to the Washington ruins and the same scene")
	_check(app.discovered_locations.has(NEW_YORK) and app.discovered_locations.has(YONKERS) and not app.discovered_locations.has("earth.cn.shanghai") and not app.travel_location_ids().has("earth.cn.liangzhu-ruins"), "old discoveries map to US places; retired IDs never show")
	_check(week_events.is_empty() and calendar_events.is_empty(), "migration emits no calendar or week events")
	var trip := _travel(NEW_YORK)
	_check(trip.get("departed", false) and app.calendar_minutes == old_minutes + int(trip["minutes_charged"]), "after migration a trip charges only its own time")
	app.save_return_scene = "res://scenes/scifi_world_map.tscn"
	var resaved := SaveStore.read_entry(app.write_manual_save(2))
	_check(resaved["snapshot"]["travel"]["locationId"] == NEW_YORK and not resaved["snapshot"]["travel"]["discovered"].has("earth.cn.shanghai"), "re-saving writes only US IDs")


func _test_air_trip() -> void:
	app.begin_new_run()
	_set_clock(2537, 5, 25, 8, 0)
	var start: int = app.calendar_minutes
	var preview: Dictionary = app.preview_travel(CHICAGO)
	_check(preview["kind"] == "travel" and preview["mode"] == "air" and preview["road_distance_km"] == null and float(preview["air_distance_km"]) > 1000.0 and app.calendar_minutes == start, "air preview shows flight distance and is free")
	var expected := int(preview["total_minutes"])
	_check(expected > 240 and expected < 600, "NYC-Chicago door to door is several hours, not minutes (%d min)" % expected)
	var result := _travel(CHICAGO)
	_check(result.get("departed", false) and app.calendar_minutes == start + expected and app.current_location_id == CHICAGO and app.current_destination_id == "scifi.loop", "the flight charges door-to-door time once and arrives at the Loop")
	_check(app.area_scene_path("scifi.loop").ends_with("rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn") and app.area_scene_path("scifi.city").ends_with("scifi_exploration_area.tscn"), "each destination names its walkable scene")
	_check(app.commerce_city_block_reason(CHICAGO) == "", "Chicago is a discovered city that can host a company")
	_check(not app.DESTINATIONS.has("scifi.loop") and not app.areas_visited.has("scifi.loop"), "the placeholder Loop never joins the three-place demo goal")
	var back := _travel(NEW_YORK)
	_check(back.get("departed", false) and int(back["minutes_charged"]) > 0 and app.current_location_id == NEW_YORK, "the return flight charges its own time")


func _test_bilingual_text() -> void:
	app.begin_new_run()
	_set_clock(2537, 12, 31, 23, 0)
	app.language = "zh"
	var zh_preview: Dictionary = app.preview_travel(WASHINGTON)
	var zh_lines: String = "\n".join(app.travel_preview_lines(zh_preview))
	var zh_label: String = app.travel_location_dual_name(WASHINGTON)
	app.language = "en"
	var en_preview: Dictionary = app.preview_travel(WASHINGTON)
	var en_lines: String = "\n".join(app.travel_preview_lines(en_preview))
	_check(zh_label == app.travel_location_dual_name(WASHINGTON) and zh_label.contains("华盛顿特区废墟") and zh_label.contains("Washington, D.C. Ruins"), "map label carries both names in either language")
	_check(int(zh_preview["total_minutes"]) == int(en_preview["total_minutes"]) and is_equal_approx(float(zh_preview["road_distance_km"]), float(en_preview["road_distance_km"])), "same figures in Chinese and English")
	_check(zh_lines.contains("2538年1月1日") and zh_lines.contains("汽车") and zh_lines.contains("估算"), "Chinese preview shows arrival date, mode and estimate note")
	_check(en_lines.contains("Jan 1, 2538") and en_lines.contains("Car") and en_lines.contains("estimated"), "English preview shows arrival date, mode and estimate note")
	_check(app.travel_duration_text(26) == "26 min" and app.travel_duration_text(120) == "2 h" and app.travel_duration_text(146) == "2 h 26 min", "English durations")
	app.language = "zh"
	_check(app.travel_duration_text(146) == "2小时26分钟" and app.calendar_date_text_at(TravelCalendar.to_minutes(2028, 2, 29)) == "2028年2月29日", "Chinese duration and date")
	app.cancel_travel_preview()


func _clear_saves() -> void:
	var directory := DirAccess.open(SAVE_ROOT)
	if directory == null:
		return
	for name in directory.get_files():
		directory.remove(name)


func _check(condition: bool, label: String) -> bool:
	if condition:
		return true
	failures += 1
	push_error("Global travel core check failed: " + label)
	return false
