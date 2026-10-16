extends RefCounted
class_name WorldRouteRegistry

# Loads and validates the global Earth location and route data. Road and flight distances are
# kept apart from the great-circle distance, which is computed from coordinates for reference only.
# v02: creator-approved US science sphere (2026-10-15). The provisional v01 file (Shanghai set) stays as
# a record; its location IDs live on in v02 as hidden retiredLocations so old saves still resolve.
# Travel time (creator rule, 2026-10-16): each car or air leg charges gameplayDurationMinutes, a fixed whole
# number of hours (at least one) equal to its referenceDurationMinutes rounded to the nearest hour. Nothing
# else is charged: no airport, check-in, waiting, traffic or departure-clock component. referenceEvidence is
# provenance for the reference figure only and is never read to price a trip.
const DEFAULT_DATA_PATH := "res://data/world-travel/rpg-2-star-ocean-the-second_global-earth-travel_locations-routes_m2-us-science-v02_20261015-175011-c454007b.json"
const SCHEMA_VERSION := 1
const MODES := ["car", "air"]
const LOCATION_TYPES := ["city", "outskirts", "ruins", "community", "wild", "facility", "portal"]
const ROUTE_STATUSES := ["available", "unverified", "pending"]
const LEG_VERIFICATION_STATUSES := ["verified", "preliminary-estimate"]
const CHARGED_FIELD := "gameplayDurationMinutes"
const REFERENCE_FIELD := "referenceDurationMinutes"
const HOUR_MINUTES := 60
# Timing fields of the superseded door-to-door model. A segment carrying any of them at its top level is
# rejected, so no record can look as if it adds to the charge; the parts live in referenceEvidence.
const RETIRED_TIMING_FIELDS := ["airportAccessMinutes", "checkInAndWaitMinutes", "flightMinutes", "airportEgressMinutes", "doorToDoorAllowanceMinutes"]
const EARTH_MEAN_RADIUS_KM := 6371.0088
# Creator decision 2026-10-15: five Earth spheres (science, magic, wuxia, nature, culture) plus a
# separate portal-only final planet.
const EARTH_REGION_COUNT := 5

var errors: PackedStringArray = []
var data: Dictionary = {}
var regions: Dictionary = {}
var locations: Dictionary = {}
var location_order: Array[String] = []
var segments: Dictionary = {}
var routes: Dictionary = {}
var route_order: Array[String] = []
var alias_to_location: Dictionary = {}
# Old region ID -> active region ID (culture keeps "fantasy"). An alias is never an active region.
var alias_to_region: Dictionary = {}
# Retired location ID -> its record. Retired places are never listed, discovered or routed; their IDs
# only resolve to the successor location so saves made before a place set changed still load.
var retired_locations: Dictionary = {}
var scene_to_location: Dictionary = {}
var start_location_id := ""
var calendar_start_minutes := 0


static func load_default() -> WorldRouteRegistry:
	return load_file(DEFAULT_DATA_PATH)


static func load_file(path: String) -> WorldRouteRegistry:
	var registry := WorldRouteRegistry.new()
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		registry.errors.append("cannot open travel data: " + path)
		return registry
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	file.close()
	if typeof(parsed) != TYPE_DICTIONARY:
		registry.errors.append("travel data is not a JSON object: " + path)
		return registry
	registry._build(parsed)
	return registry


static func from_dictionary(source: Dictionary) -> WorldRouteRegistry:
	var registry := WorldRouteRegistry.new()
	registry._build(source.duplicate(true))
	return registry


func is_valid() -> bool:
	return errors.is_empty()


# Accepts a location ID, a legacy alias, or a scene destination ID such as "scifi.city".
func resolve_location_id(location_id: String) -> String:
	if locations.has(location_id):
		return location_id
	if alias_to_location.has(location_id):
		return String(alias_to_location[location_id])
	return String(scene_to_location.get(location_id, ""))


func resolve_region_id(region_id: String) -> String:
	if regions.has(region_id):
		return region_id
	return String(alias_to_region.get(region_id, ""))


func location(location_id: String) -> Dictionary:
	return locations.get(resolve_location_id(location_id), {})


func location_for_scene(scene_destination_id: String) -> String:
	return String(scene_to_location.get(scene_destination_id, ""))


func initial_location_ids() -> Array[String]:
	var result: Array[String] = []
	for location_id in location_order:
		if bool(locations[location_id].get("discovery", {}).get("initial", false)):
			result.append(location_id)
	return result


func great_circle_km(from_id: String, to_id: String) -> float:
	var a := location(from_id)
	var b := location(to_id)
	if a.is_empty() or b.is_empty():
		return 0.0
	var lat1 := deg_to_rad(float(a["coordinates"]["lat"]))
	var lat2 := deg_to_rad(float(b["coordinates"]["lat"]))
	var dlat := lat2 - lat1
	var dlon := deg_to_rad(float(b["coordinates"]["lon"]) - float(a["coordinates"]["lon"]))
	var h := sin(dlat / 2.0) * sin(dlat / 2.0) + cos(lat1) * cos(lat2) * sin(dlon / 2.0) * sin(dlon / 2.0)
	return 2.0 * EARTH_MEAN_RADIUS_KM * asin(minf(1.0, sqrt(h)))


# The only figure a trip charges for a leg. Same for every departure time.
func segment_minutes(segment: Dictionary) -> int:
	return int(segment.get(CHARGED_FIELD, 0))


# The whole-hour gameplay value for a reference estimate: nearest hour (half up), never under one hour.
static func whole_hour_minutes(reference_minutes: int) -> int:
	return maxi(1, int(floorf(float(reference_minutes) / HOUR_MINUTES + 0.5))) * HOUR_MINUTES


# Player-facing distance: whole km under 100 km, else the nearest 10 km. Display only; never charged.
static func approximate_km(km: float) -> int:
	if km < 100.0:
		return maxi(1, roundi(km))
	return roundi(km / 10.0) * 10


# Every route record between two places, in either stored direction, resolved into travel order.
# Unavailable routes are included with "available": false so the map can show them as pending.
func routes_between(from_id: String, to_id: String) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	var origin := resolve_location_id(from_id)
	var destination := resolve_location_id(to_id)
	if origin == "" or destination == "" or origin == destination:
		return result
	for route_id in route_order:
		var route: Dictionary = routes[route_id]
		var forward: bool = route["fromLocationId"] == origin and route["toLocationId"] == destination
		var backward: bool = bool(route.get("bidirectional", false)) and route["fromLocationId"] == destination and route["toLocationId"] == origin
		if forward or backward:
			result.append(_resolve_route(route, not forward))
	return result


func _resolve_route(route: Dictionary, reversed: bool) -> Dictionary:
	var legs: Array[Dictionary] = []
	var stored_legs: Array = route.get("legs", [])
	var ordered: Array = stored_legs.duplicate()
	if reversed:
		ordered.reverse()
	var modes: Array[String] = []
	var total := 0
	var road_km := 0.0
	var air_km := 0.0
	var verified := true
	var sources: Array[Dictionary] = []
	var source_names: PackedStringArray = []
	for leg_ref in ordered:
		var segment: Dictionary = segments[String(leg_ref["segmentId"])]
		var leg_reversed: bool = bool(leg_ref.get("reverse", false)) != reversed
		var minutes := segment_minutes(segment)
		var mode := String(segment["mode"])
		if not modes.has(mode):
			modes.append(mode)
		total += minutes
		road_km += float(segment.get("roadDistanceKm", 0.0)) if mode == "car" else 0.0
		air_km += float(segment.get("flightDistanceKm", 0.0)) if mode == "air" else 0.0
		var verification: Dictionary = segment.get("verification", {})
		verified = verified and verification.get("status", "") == "verified" and (not leg_reversed or segment.get("reverseBasis", "verified") == "verified")
		var source: Dictionary = verification.get("source", {})
		sources.append(source.duplicate(true))
		if not source_names.has(String(source.get("name", ""))):
			source_names.append(String(source.get("name", "")))
		legs.append({
			"segment_id": segment["id"],
			"mode": mode,
			"from_location_id": segment["toLocationId"] if leg_reversed else segment["fromLocationId"],
			"to_location_id": segment["fromLocationId"] if leg_reversed else segment["toLocationId"],
			"reversed": leg_reversed,
			"road_distance_km": float(segment["roadDistanceKm"]) if mode == "car" else null,
			"air_distance_km": float(segment["flightDistanceKm"]) if mode == "air" else null,
			"minutes": minutes,
			"verification_status": verification.get("status", ""),
			"source": source.duplicate(true),
		})
	var via: Array = route.get("viaLocationIds", []).duplicate()
	if reversed:
		via.reverse()
	var available: bool = route.get("status", "") == "available" and not legs.is_empty()
	var mode_name := "air_car" if modes.size() > 1 else (modes[0] if not modes.is_empty() else "")
	return {
		"option_id": route["id"],
		"available": available,
		"status": route.get("status", ""),
		"unavailable_reason": "" if available else String(route.get("unavailableReason", "route-" + String(route.get("status", "unknown")))),
		"from_location_id": route["toLocationId"] if reversed else route["fromLocationId"],
		"to_location_id": route["fromLocationId"] if reversed else route["toLocationId"],
		"via_location_ids": via,
		"mode": mode_name,
		"modes": modes,
		"legs": legs if available else [],
		"total_minutes": total if available else -1,
		"road_distance_km": snappedf(road_km, 0.1) if available and modes.has("car") else null,
		"air_distance_km": snappedf(air_km, 0.1) if available and modes.has("air") else null,
		"great_circle_km": snappedf(great_circle_km(route["fromLocationId"], route["toLocationId"]), 0.1),
		# verified: every leg (and any reversed use of it) is verified. estimate is the complement.
		"verified": available and verified,
		"estimate": not (available and verified),
		"source": " · ".join(source_names) if available else "",
		"sources": sources if available else [],
		"note": String(route.get("note", "")),
	}


func _build(source: Dictionary) -> void:
	data = source
	if int(source.get("schemaVersion", -1)) != SCHEMA_VERSION:
		errors.append("unsupported travel data schemaVersion")
		return
	var calendar: Dictionary = source.get("calendar", {}) if typeof(source.get("calendar")) == TYPE_DICTIONARY else {}
	var start := TravelCalendar.parse_minutes(String(calendar.get("startDate", "")), String(calendar.get("startTime", "00:00")))
	if not bool(start.get("ok", false)):
		errors.append("calendar.startDate/startTime invalid")
	else:
		calendar_start_minutes = int(start["minutes"])
	_check_time_rule(source.get("travelTimeRule"))
	var seen_ids: Dictionary = {}
	for region in _array(source, "regions"):
		var region_id := String(region.get("id", ""))
		if not _claim_id(seen_ids, region_id, "region"):
			continue
		if region.get("access", "") not in ["car-air", "portal"]:
			errors.append("region %s has invalid access" % region_id)
		if not _has_names(region):
			errors.append("region %s needs zh and en names" % region_id)
		regions[region_id] = region
	var earth_regions := 0
	for region_id in regions:
		earth_regions += int(regions[region_id].get("planet", "") == "earth")
		for alias in regions[region_id].get("legacyIds", []):
			if regions.has(alias) or alias_to_region.has(alias):
				errors.append("legacy region id %s collides" % alias)
			alias_to_region[String(alias)] = region_id
	if earth_regions != EARTH_REGION_COUNT:
		errors.append("expected %d Earth regions, found %d" % [EARTH_REGION_COUNT, earth_regions])
	for entry in _array(source, "locations"):
		_add_location(entry, seen_ids)
	for entry in _array(source, "retiredLocations"):
		_add_retired_location(entry, seen_ids)
	start_location_id = String(source.get("startLocationId", ""))
	if not locations.has(start_location_id):
		errors.append("startLocationId is not a known location")
	for entry in _array(source, "segments"):
		_add_segment(entry, seen_ids)
	for entry in _array(source, "routes"):
		_add_route(entry, seen_ids)


func _add_location(entry: Dictionary, seen_ids: Dictionary) -> void:
	var location_id := String(entry.get("id", ""))
	if not _claim_id(seen_ids, location_id, "location"):
		return
	if not _has_names(entry):
		errors.append("location %s needs zh and en names" % location_id)
	if entry.get("type", "") not in LOCATION_TYPES:
		errors.append("location %s has invalid type" % location_id)
	if not regions.has(entry.get("regionId", "")):
		errors.append("location %s has unknown region" % location_id)
	# A region may limit its places to some countries (the science sphere is the US and Canada only).
	var allowed: Variant = regions.get(entry.get("regionId", ""), {}).get("countryCodes")
	if typeof(allowed) == TYPE_ARRAY and not allowed.has(entry.get("countryCode", "")):
		errors.append("location %s country %s is outside region %s" % [location_id, String(entry.get("countryCode", "")), String(entry.get("regionId", ""))])
	var coordinates: Variant = entry.get("coordinates")
	if typeof(coordinates) != TYPE_DICTIONARY or not _is_number(coordinates.get("lat")) or not _is_number(coordinates.get("lon")) or absf(float(coordinates["lat"])) > 90.0 or absf(float(coordinates["lon"])) > 180.0:
		errors.append("location %s has invalid coordinates" % location_id)
		return
	if regions.get(entry.get("regionId", ""), {}).get("planet", "") == "earth" and typeof(entry.get("coordinateSource")) != TYPE_DICTIONARY:
		errors.append("location %s needs a coordinateSource" % location_id)
	var scene_id := String(entry.get("sceneDestinationId", ""))
	if scene_id != "":
		if scene_to_location.has(scene_id):
			errors.append("scene %s bound to two locations" % scene_id)
		scene_to_location[scene_id] = location_id
	for alias in entry.get("legacyIds", []):
		if seen_ids.has(alias) or alias_to_location.has(alias):
			errors.append("legacy id %s collides" % alias)
		alias_to_location[String(alias)] = location_id
	locations[location_id] = entry
	location_order.append(location_id)


# Runs after every active location is known, so a retired ID can only point at a live place.
func _add_retired_location(entry: Dictionary, seen_ids: Dictionary) -> void:
	var retired_id := String(entry.get("id", ""))
	if not _claim_id(seen_ids, retired_id, "retired location"):
		return
	if alias_to_location.has(retired_id):
		errors.append("retired id %s is also a legacy id" % retired_id)
		return
	var successor := String(entry.get("migratesToLocationId", ""))
	if not locations.has(successor):
		errors.append("retired location %s must migrate to an active location" % retired_id)
		return
	if not _has_names(entry):
		errors.append("retired location %s needs zh and en names" % retired_id)
	alias_to_location[retired_id] = successor
	retired_locations[retired_id] = entry


func _add_segment(entry: Dictionary, seen_ids: Dictionary) -> void:
	var segment_id := String(entry.get("id", ""))
	if not _claim_id(seen_ids, segment_id, "segment"):
		return
	var mode := String(entry.get("mode", ""))
	if not MODES.has(mode):
		errors.append("segment %s has invalid mode (only car or air)" % segment_id)
		return
	for field in ["fromLocationId", "toLocationId"]:
		var endpoint := String(entry.get(field, ""))
		if not locations.has(endpoint):
			errors.append("segment %s %s unknown" % [segment_id, field])
			return
		if regions.get(locations[endpoint]["regionId"], {}).get("access", "") != "car-air":
			errors.append("segment %s reaches a portal-only region by %s" % [segment_id, mode])
			return
	if entry["fromLocationId"] == entry["toLocationId"]:
		errors.append("segment %s starts and ends at the same place" % segment_id)
	if mode == "car":
		if not _is_number(entry.get("roadDistanceKm")) or float(entry["roadDistanceKm"]) <= 0.0:
			errors.append("car segment %s needs roadDistanceKm" % segment_id)
	elif not _is_number(entry.get("flightDistanceKm")) or float(entry["flightDistanceKm"]) <= 0.0:
		errors.append("air segment %s needs flightDistanceKm" % segment_id)
	_check_duration(entry, segment_id)
	var verification: Variant = entry.get("verification")
	if typeof(verification) != TYPE_DICTIONARY or verification.get("status", "") not in LEG_VERIFICATION_STATUSES or typeof(verification.get("source")) != TYPE_DICTIONARY or String(verification["source"].get("url", "")) == "":
		errors.append("segment %s needs verification status and a source url" % segment_id)
	_check_reference_evidence(entry, segment_id)
	segments[segment_id] = entry


# The data must declare the same rule the code applies, so the file cannot describe another charge.
func _check_time_rule(rule: Variant) -> void:
	if typeof(rule) != TYPE_DICTIONARY:
		errors.append("travelTimeRule must be an object")
		return
	var whole_hours: bool = _is_number(rule.get("stepMinutes")) and int(rule["stepMinutes"]) == HOUR_MINUTES and _is_number(rule.get("minimumMinutes")) and int(rule["minimumMinutes"]) == HOUR_MINUTES
	if rule.get("chargedField", "") != CHARGED_FIELD or rule.get("referenceField", "") != REFERENCE_FIELD or not whole_hours or rule.get("rounding", "") != "nearest-hour-half-up":
		errors.append("travelTimeRule must charge gameplayDurationMinutes in whole hours (step 60, minimum 60, nearest hour half up)")


# A leg charges a whole number of hours, at least one, and that value is its reference rounded to the hour.
func _check_duration(entry: Dictionary, segment_id: String) -> void:
	for field in RETIRED_TIMING_FIELDS:
		if entry.has(field):
			errors.append("segment %s still has retired timing field %s (keep evidence in referenceEvidence)" % [segment_id, field])
	var charged: Variant = entry.get(CHARGED_FIELD)
	if not _is_whole(charged, HOUR_MINUTES) or int(charged) % HOUR_MINUTES != 0:
		errors.append("segment %s %s must be a whole number of hours (a multiple of 60, at least 60)" % [segment_id, CHARGED_FIELD])
		return
	var reference: Variant = entry.get(REFERENCE_FIELD)
	if not _is_whole(reference, 1):
		errors.append("segment %s needs %s, the real-world estimate its hours are rounded from" % [segment_id, REFERENCE_FIELD])
		return
	if int(charged) != whole_hour_minutes(int(reference)):
		errors.append("segment %s %s %d is not %s %d rounded to the hour (%d)" % [segment_id, CHARGED_FIELD, int(charged), REFERENCE_FIELD, int(reference), whole_hour_minutes(int(reference))])


# Optional provenance. componentMinutes must add up to the reference, each documented component must match
# the number it explains (a componentMinutes entry or a top-level field such as flightDistanceKm), and a
# rawMedianMinutes must round (half up) to its component. None of it is charged.
func _check_reference_evidence(entry: Dictionary, segment_id: String) -> void:
	if not entry.has("referenceEvidence"):
		return
	var evidence: Variant = entry["referenceEvidence"]
	if typeof(evidence) != TYPE_DICTIONARY or evidence.get("runtimeUse", "") != "none":
		errors.append("segment %s referenceEvidence must be an object with runtimeUse none" % segment_id)
		return
	var parts: Variant = evidence.get("componentMinutes", {})
	if typeof(parts) != TYPE_DICTIONARY:
		errors.append("segment %s referenceEvidence.componentMinutes must be an object" % segment_id)
		return
	if not parts.is_empty():
		var total := 0
		for field in parts:
			if not _is_whole(parts[field], 0):
				errors.append("segment %s referenceEvidence.componentMinutes.%s must be whole minutes" % [segment_id, field])
				return
			total += int(parts[field])
		if _is_number(entry.get(REFERENCE_FIELD)) and total != int(entry[REFERENCE_FIELD]):
			errors.append("segment %s referenceEvidence.componentMinutes sum %d != %s %d" % [segment_id, total, REFERENCE_FIELD, int(entry[REFERENCE_FIELD])])
	var components: Variant = evidence.get("components", {})
	if typeof(components) != TYPE_DICTIONARY:
		errors.append("segment %s referenceEvidence.components must be an object" % segment_id)
		return
	for field in components:
		var component: Variant = components[field]
		if typeof(component) != TYPE_DICTIONARY or not component.has("value"):
			continue
		var explained: Variant = parts.get(field, entry.get(field))
		if not _is_number(component["value"]) or not _is_number(explained) or float(component["value"]) != float(explained):
			errors.append("segment %s referenceEvidence.components.%s.value disagrees with the figure it documents" % [segment_id, field])
			continue
		if component.has("rawMedianMinutes") and (not _is_number(component["rawMedianMinutes"]) or int(floorf(float(component["rawMedianMinutes"]) + 0.5)) != int(explained)):
			errors.append("segment %s referenceEvidence.components.%s.rawMedianMinutes does not round to its value" % [segment_id, field])


func _add_route(entry: Dictionary, seen_ids: Dictionary) -> void:
	var route_id := String(entry.get("id", ""))
	if not _claim_id(seen_ids, route_id, "route"):
		return
	var origin := String(entry.get("fromLocationId", ""))
	var destination := String(entry.get("toLocationId", ""))
	if not locations.has(origin) or not locations.has(destination) or origin == destination:
		errors.append("route %s has invalid endpoints" % route_id)
		return
	if entry.get("status", "") not in ROUTE_STATUSES:
		errors.append("route %s has invalid status" % route_id)
		return
	var legs: Variant = entry.get("legs", [])
	if typeof(legs) != TYPE_ARRAY:
		errors.append("route %s legs must be an array" % route_id)
		return
	if entry["status"] == "available" and legs.is_empty():
		errors.append("available route %s has no legs" % route_id)
		return
	var cursor := origin
	var stops: Array[String] = []
	for leg_ref in legs:
		var segment: Dictionary = segments.get(String(leg_ref.get("segmentId", "")) if typeof(leg_ref) == TYPE_DICTIONARY else "", {})
		if segment.is_empty():
			errors.append("route %s references an unknown segment" % route_id)
			return
		var reverse := bool(leg_ref.get("reverse", false))
		if (reverse or bool(entry.get("bidirectional", false))) and not bool(segment.get("bidirectional", false)):
			errors.append("route %s uses one-way segment %s in reverse" % [route_id, segment["id"]])
			return
		var leg_start := String(segment["toLocationId"] if reverse else segment["fromLocationId"])
		if leg_start != cursor:
			errors.append("route %s legs do not chain at %s" % [route_id, cursor])
			return
		cursor = String(segment["fromLocationId"] if reverse else segment["toLocationId"])
		stops.append(cursor)
	if not legs.is_empty() and cursor != destination:
		errors.append("route %s legs end at %s, not %s" % [route_id, cursor, destination])
		return
	if not stops.is_empty():
		stops.pop_back()
	var declared_via: Variant = entry.get("viaLocationIds", [])
	if typeof(declared_via) != TYPE_ARRAY or (not legs.is_empty() and PackedStringArray(declared_via) != PackedStringArray(stops)):
		errors.append("route %s viaLocationIds must name the intermediate stops" % route_id)
	if entry.has("declaredTotalMinutes"):
		var computed := 0
		for leg_ref in legs:
			computed += segment_minutes(segments[String(leg_ref["segmentId"])])
		if int(entry["declaredTotalMinutes"]) != computed:
			errors.append("route %s declaredTotalMinutes %d != legs %d" % [route_id, int(entry["declaredTotalMinutes"]), computed])
	routes[route_id] = entry
	route_order.append(route_id)


func _claim_id(seen_ids: Dictionary, id: String, kind: String) -> bool:
	if id == "":
		errors.append("%s without id" % kind)
		return false
	if seen_ids.has(id):
		errors.append("duplicate id " + id)
		return false
	seen_ids[id] = kind
	return true


func _array(source: Dictionary, key: String) -> Array:
	var value: Variant = source.get(key, [])
	if typeof(value) != TYPE_ARRAY:
		errors.append(key + " must be an array")
		return []
	var result: Array = []
	for item in value:
		if typeof(item) == TYPE_DICTIONARY:
			result.append(item)
		else:
			errors.append(key + " entry is not an object")
	return result


func _has_names(entry: Dictionary) -> bool:
	var names: Variant = entry.get("names")
	return typeof(names) == TYPE_DICTIONARY and String(names.get("zh", "")) != "" and String(names.get("en", "")) != ""


func _is_number(value: Variant) -> bool:
	return typeof(value) in [TYPE_INT, TYPE_FLOAT] and is_finite(float(value))


func _is_whole(value: Variant, minimum: int) -> bool:
	return _is_number(value) and float(value) == roundf(float(value)) and int(value) >= minimum
