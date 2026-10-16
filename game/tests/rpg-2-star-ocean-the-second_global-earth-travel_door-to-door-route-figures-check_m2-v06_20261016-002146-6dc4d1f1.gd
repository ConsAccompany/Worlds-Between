extends SceneTree

# Focused check for the M2 door-to-door route figures (2026-10-16, gate still OPEN):
#   - the runtime stays on the v02 data; no measured candidate figure is promoted (Chicago rideshare
#     ORD -> Loop sample is incomplete, the arrival allowance and time-of-day policy are undecided);
#   - every documented air component equals the minute field the runtime charges, and the registry
#     rejects a component that drifts from its field or a raw median that does not round to it;
#   - every segment stays a preliminary estimate with a zero door-to-door allowance;
#   - NYC <-> Chicago still offers one unverified estimate route per direction at the v02 totals.
# Nothing here accepts a figure.
# From the repository root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --headless --path game \
#     --script res://tests/rpg-2-star-ocean-the-second_global-earth-travel_door-to-door-route-figures-check_m2-v06_20261016-002146-6dc4d1f1.gd

const DATA_V02 := "res://data/world-travel/rpg-2-star-ocean-the-second_global-earth-travel_locations-routes_m2-us-science-v02_20261015-175011-c454007b.json"
const NEW_YORK := "earth.us.ny.new-york-city"
const CHICAGO := "earth.us.il.chicago"
const WESTBOUND := "seg.air.nyc-lga__chicago-ord"
const EASTBOUND := "seg.air.chicago-ord__nyc-lga"
const AIR_FIELDS := ["airportAccessMinutes", "checkInAndWaitMinutes", "flightMinutes", "airportEgressMinutes"]
# v02 runtime figures (access, check-in, flight, egress) and totals. Change only with a reviewed data revision.
const EXPECTED_AIR := {
	WESTBOUND: [24, 120, 166, 55, 365],
	EASTBOUND: [54, 120, 142, 22, 338],
}

var checks := 0
var failures := 0


func _initialize() -> void:
	var registry := WorldRouteRegistry.load_default()
	_check(WorldRouteRegistry.DEFAULT_DATA_PATH == DATA_V02 and registry.is_valid(), "runtime loads the valid v02 data: " + "; ".join(registry.errors))
	if registry.is_valid():
		_test_air_figures(registry)
		_test_status(registry)
		_test_validator_guard(registry)
		_test_route_options(registry)
		_test_car_labels(registry)
	if failures == 0:
		print("M2_ROUTE_FIGURES_V06_OK checks=%d" % checks)
		quit(0)
	else:
		print("M2_ROUTE_FIGURES_V06_FAILED failures=%d checks=%d" % [failures, checks])
		quit(1)


func _test_air_figures(registry: WorldRouteRegistry) -> void:
	for segment_id in EXPECTED_AIR:
		var seg: Dictionary = registry.segments[segment_id]
		var expected: Array = EXPECTED_AIR[segment_id]
		var fields_ok := true
		for i in AIR_FIELDS.size():
			fields_ok = fields_ok and int(seg[AIR_FIELDS[i]]) == int(expected[i]) and int(seg["components"][AIR_FIELDS[i]]["value"]) == int(expected[i])
		_check(fields_ok, segment_id + " charged fields equal their documented components")
		_check(registry.segment_minutes(seg) == int(expected[4]), "%s total stays %d" % [segment_id, int(expected[4])])


func _test_status(registry: WorldRouteRegistry) -> void:
	var ok := registry.segments.size() == 8
	for segment_id in registry.segments:
		var seg: Dictionary = registry.segments[segment_id]
		ok = ok and seg["verification"]["status"] == "preliminary-estimate" and int(seg["doorToDoorAllowanceMinutes"]) == 0
	_check(ok, "all 8 segments stay preliminary estimates with a 0 door-to-door allowance")


func _test_validator_guard(registry: WorldRouteRegistry) -> void:
	var drifted: Dictionary = registry.data.duplicate(true)
	for seg in drifted["segments"]:
		if seg["id"] == WESTBOUND:
			seg["airportEgressMinutes"] = int(seg["airportEgressMinutes"]) + 5
	var bad := WorldRouteRegistry.from_dictionary(drifted)
	_check(not bad.is_valid() and "; ".join(bad.errors).contains("components.airportEgressMinutes.value disagrees"), "a charged field that drifts from its documented component is rejected")
	var rounded: Dictionary = registry.data.duplicate(true)
	for seg in rounded["segments"]:
		if seg["id"] == EASTBOUND:
			seg["components"]["airportEgressMinutes"]["rawMedianMinutes"] = 22.5
	var bad_raw := WorldRouteRegistry.from_dictionary(rounded)
	_check(not bad_raw.is_valid() and "; ".join(bad_raw.errors).contains("rawMedianMinutes does not round"), "a raw median that does not round (half up) to the charged minutes is rejected")
	var good_raw: Dictionary = registry.data.duplicate(true)
	for seg in good_raw["segments"]:
		if seg["id"] == EASTBOUND:
			seg["components"]["airportEgressMinutes"]["rawMedianMinutes"] = 22.49
	_check(WorldRouteRegistry.from_dictionary(good_raw).is_valid(), "a raw median that rounds to the charged minutes is accepted")
	var not_object: Dictionary = registry.data.duplicate(true)
	not_object["segments"][0]["components"] = [1]
	_check(not WorldRouteRegistry.from_dictionary(not_object).is_valid(), "components that are not an object are rejected")


func _test_route_options(registry: WorldRouteRegistry) -> void:
	for pair in [[NEW_YORK, CHICAGO, WESTBOUND], [CHICAGO, NEW_YORK, EASTBOUND]]:
		var options := registry.routes_between(pair[0], pair[1])
		var expected_total: int = EXPECTED_AIR[pair[2]][4]
		_check(options.size() == 1 and options[0]["available"] and int(options[0]["total_minutes"]) == expected_total and options[0]["estimate"] and not options[0]["verified"], "%s -> %s offers one unverified estimate route of %d min" % [pair[0], pair[1], expected_total])


# OSRM demo output is a routing-model estimate, not measured free-flow; only the negation may mention free-flow.
func _test_car_labels(registry: WorldRouteRegistry) -> void:
	var car_notes := 0
	var ok := true
	for segment_id in registry.segments:
		var seg: Dictionary = registry.segments[segment_id]
		if seg["mode"] != "car":
			continue
		car_notes += 1
		var note: String = seg["verification"]["note"]
		ok = ok and note.contains("no live traffic") and not note.replace("not measured free-flow", "").to_lower().contains("free-flow")
	_check(car_notes == 6 and ok, "all 6 car notes are model estimates with no live traffic and none claims free-flow")
	var airport_legs := 0
	var air_ok := true
	for segment_id in EXPECTED_AIR:
		for field in ["airportAccessMinutes", "airportEgressMinutes"]:
			var component: Dictionary = registry.segments[segment_id]["components"][field]
			if component["source"]["sourceId"] != "osrm-demo-osm":
				continue
			airport_legs += 1
			var basis: String = component["basis"]
			air_ok = air_ok and basis.contains("no live traffic") and not basis.replace("not measured free-flow", "").to_lower().contains("free-flow")
	_check(airport_legs == 4 and air_ok, "all 4 OSRM airport car legs are model estimates with no live traffic and none claims free-flow")


func _check(condition: bool, label: String) -> bool:
	checks += 1
	if not condition:
		failures += 1
		push_error("FAIL: " + label)
		print("FAIL: " + label)
	return condition
