extends RefCounted

# Integration point between the world map and the calendar/route core in AppState.
# The map never computes distances, minutes or dates itself; it only formats what the
# provider's public API returns. Place coordinates, names and scene links always come from
# the global travel data: through the provider when its API is present, otherwise read
# straight from the same data file. The map registry adds display metadata only.
# Without the route API nobody can depart: every other place reads "pending_api" and only
# entering the scene the party is already at stays possible (it costs no time).
#
# Provider API used (AppState, owned by the travel/calendar workstream):
#   current_location_id, current_destination_id, calendar_minutes (properties)
#   travel_location_ids(region_id), travel_location(id), travel_location_name(id)
#   travel_route_options(from_id, to_id) -> Array[Dictionary]  (option_id, available, mode,
#       total_minutes, road_distance_km, air_distance_km, estimate, source, via_location_ids)
#   travel_arrival_preview(total_minutes) -> Dictionary  (text, time_text)
#   preview_travel(to_id, option_id) -> Dictionary  (ok, kind, option_id); picks the default route
#   cancel_travel_preview(), confirm_travel(to_id, option_id) -> bool, enter_current_location_scene()
#   calendar_date_text_at(minutes), calendar_time_text_at(minutes), travel_duration_text(minutes)

const MapData := preload("res://scripts/world_map_data.gd")
const REQUIRED_METHODS := {
	"travel_location_ids": 1, "travel_location": 1, "travel_location_name": 1,
	"travel_route_options": 2, "travel_arrival_preview": 1, "preview_travel": 2,
	"cancel_travel_preview": 0, "confirm_travel": 2, "enter_current_location_scene": 0,
	"calendar_date_text_at": 1, "calendar_time_text_at": 1, "travel_duration_text": 1,
}
const REQUIRED_PROPERTIES := ["current_location_id", "calendar_minutes"]
const MODES := ["car", "air", "air_car"]

var provider: Object


func _init(source: Object) -> void:
	provider = source


func api_available() -> bool:
	return api_problems().is_empty()


# Why the route API cannot be used, one entry per missing property or method (empty when usable).
# Argument counts guard against a signature change in the concurrently developed core.
func api_problems() -> PackedStringArray:
	var problems: PackedStringArray = []
	if provider == null:
		problems.append("no provider")
		return problems
	for property in REQUIRED_PROPERTIES:
		if not (property in provider):
			problems.append("missing property " + property)
	for method in REQUIRED_METHODS:
		if not provider.has_method(method):
			problems.append("missing method %s()" % method)
		elif provider.get_method_argument_count(method) != REQUIRED_METHODS[method]:
			problems.append("%s() takes %d arguments, map expects %d" % [method, provider.get_method_argument_count(method), REQUIRED_METHODS[method]])
	return problems


func current_place_id() -> String:
	if api_available():
		return String(provider.get("current_location_id"))
	if "current_destination_id" in provider:
		return MapData.travel_data().location_for_scene(String(provider.get("current_destination_id")))
	return ""


# Map places: core location data (names, coordinates, scene link) plus the display registry's
# presentation fields. With the API the provider's discovered list is used; without it, the
# travel data's initial locations. A location without display metadata is reported, not hidden.
func places() -> Array:
	var result := []
	var api := api_available()
	var ids: Array = provider.call("travel_location_ids", "") if api else Array(MapData.travel_data().initial_location_ids())
	for location_id in ids:
		var core: Dictionary = provider.call("travel_location", location_id) if api else MapData.travel_data().location(location_id).duplicate(true)
		var coordinates: Dictionary = core.get("coordinates", {})
		if not coordinates.has_all(["lat", "lon"]):
			continue
		var display := MapData.display_place(location_id)
		if display.is_empty():
			push_error("World map: travel location %s has no display entry in the map registry" % location_id)
		var names: Dictionary = core.get("names", {})
		result.append({
			"id": String(location_id),
			"lon": float(coordinates["lon"]),
			"lat": float(coordinates["lat"]),
			"coordinate_basis": String(coordinates.get("basis", "")),
			"map_label": names,
			"name": core.get("administrativeName", names),
			"scene_destination_id": String(core.get("sceneDestinationId", "")),
			"kind": String(display.get("kind", core.get("type", ""))),
			"board_id": String(display.get("board_id", core.get("regionId", ""))),
			"geo_region_id": String(display.get("geo_region_id", "")),
			"label_side": String(display.get("label_side", "right")),
		})
	return result


func calendar_text() -> String:
	if not api_available():
		return ""
	var minutes := int(provider.get("calendar_minutes"))
	return "%s %s" % [provider.call("calendar_date_text_at", minutes), provider.call("calendar_time_text_at", minutes)]


# status: "same_place" | "pending_api" | "no_route" | "ready".
# "options" holds available routes; "unverified" holds the ones the core marks unavailable.
# When route_id is empty the core picks its default route. Every option gets the core's arrival text.
func preview(to_id: String, route_id: String = "") -> Dictionary:
	if to_id == current_place_id():
		return {"status": "same_place", "options": [], "unverified": [], "selected": ""}
	if not api_available():
		return {"status": "pending_api", "options": [], "unverified": [], "selected": ""}
	var options := []
	var unverified := []
	for raw in provider.call("travel_route_options", current_place_id(), to_id):
		var option := _normalize(raw)
		if option.is_empty():
			continue
		if option["available"]:
			options.append(option)
		else:
			unverified.append(option)
	if options.is_empty():
		provider.call("cancel_travel_preview")
		return {"status": "no_route", "options": [], "unverified": unverified, "selected": ""}
	var core_preview: Dictionary = provider.call("preview_travel", to_id, route_id)
	if not bool(core_preview.get("ok", false)) or String(core_preview.get("kind", "")) != "travel":
		provider.call("cancel_travel_preview")
		return {"status": "no_route", "options": [], "unverified": unverified, "selected": ""}
	var selected := String(core_preview.get("option_id", ""))
	for option in options:
		var arrival: Dictionary = provider.call("travel_arrival_preview", option["total_minutes"])
		option["arrival_text"] = ("%s %s" % [arrival.get("text", ""), arrival.get("time_text", "")]).strip_edges()
	return {"status": "ready", "options": options, "unverified": unverified, "selected": selected}


# Settles the previewed trip through the core. Returns the scene destination on success.
# Without the route API there is no departure at all.
func confirm(to_id: String, route_id: String) -> Dictionary:
	if not api_available():
		return {"ok": false}
	if not bool(provider.call("confirm_travel", to_id, route_id)):
		provider.call("cancel_travel_preview")
		return {"ok": false}
	return {"ok": true, "scene_destination_id": String(provider.get("current_destination_id"))}


# Enters the scene of the place the party is already at; never moves the party and costs no time.
func enter_here() -> bool:
	if api_available():
		return bool(provider.call("enter_current_location_scene"))
	# No route API: re-select the scene the party is already in, which resets its entry state.
	if not ("current_destination_id" in provider) or not provider.has_method("select_destination"):
		return false
	return bool(provider.call("select_destination", String(provider.get("current_destination_id"))))


func cancel() -> void:
	if api_available():
		provider.call("cancel_travel_preview")


func _normalize(raw) -> Dictionary:
	if typeof(raw) != TYPE_DICTIONARY or String(raw.get("option_id", "")).is_empty():
		return {}
	var available := bool(raw.get("available", false)) and int(raw.get("total_minutes", -1)) > 0
	var mode := String(raw.get("mode", ""))
	var via := []
	for location_id in raw.get("via_location_ids", []):
		via.append(String(provider.call("travel_location_name", location_id)))
	var option := {
		"option_id": String(raw["option_id"]),
		"available": available and MODES.has(mode),
		"mode": mode,
		"via": via,
		"unavailable_reason": String(raw.get("unavailable_reason", "")),
		"estimate": bool(raw.get("estimate", true)),
		"source": String(raw.get("source", "")),
		"arrival_text": "",
	}
	if option["available"]:
		option["total_minutes"] = int(raw["total_minutes"])
		option["duration_text"] = String(provider.call("travel_duration_text", int(raw["total_minutes"])))
		option["road_distance_km"] = _optional_km(raw.get("road_distance_km"))
		option["air_distance_km"] = _optional_km(raw.get("air_distance_km"))
	return option


static func _optional_km(value) -> float:
	if typeof(value) == TYPE_INT or typeof(value) == TYPE_FLOAT:
		return float(value) if float(value) > 0.0 else -1.0
	return -1.0
