extends RefCounted

# Read-only access to the world-map display registry and the Natural Earth runtime geodata.
# The display registry holds no coordinates or names for travel places: those come only
# from the global travel data (world_route_registry.gd), so map and route core share one
# source. This script only parses files and never adds coordinates of its own.

const REGISTRY_PATH := "res://data/world-map/rpg-2-star-ocean-the-second_earth-map_place-registry_m2-v01_20261015-024300-36903495.json"
const GEODATA_PATH := "res://data/world-map/rpg-2-star-ocean-the-second_earth-map_runtime-geodata_m2-v01_20261015-024300-2595ada6.json"

static var _registry: Dictionary = {}
static var _geodata: Dictionary = {}
static var _ring_cache: Dictionary = {}
static var _travel_data: WorldRouteRegistry = null


static func registry() -> Dictionary:
	if _registry.is_empty():
		_registry = _load_json(REGISTRY_PATH)
	return _registry


static func geodata() -> Dictionary:
	if _geodata.is_empty():
		_geodata = _load_json(GEODATA_PATH)
	return _geodata


# Display metadata per travel location ID: kind, board, geo region and label side only.
static func display_places() -> Array:
	return registry().get("places", [])


static func display_place(place_id: String) -> Dictionary:
	for entry in display_places():
		if entry["id"] == place_id:
			return entry
	return {}


# The global travel data, read directly. AppState reads the same file; the map uses this
# copy only when the AppState route API is unavailable, so markers never change source.
static func travel_data() -> WorldRouteRegistry:
	if _travel_data == null:
		_travel_data = WorldRouteRegistry.load_default()
	return _travel_data


static func reference_places() -> Array:
	return registry().get("reference_places", [])


static func boards() -> Array:
	return registry().get("boards", [])


static func geo_regions() -> Array:
	return registry().get("geo_regions", [])


static func geo_region(region_id: String) -> Dictionary:
	for entry in geo_regions():
		if entry["id"] == region_id:
			return entry
	return {}


# source: map places that already carry core coordinates (world_map_route_adapter.places()).
static func places_in_region(region_id: String, source: Array) -> Array:
	return source.filter(func(entry): return entry["geo_region_id"] == region_id)


# Lon/lat bounding box [west, south, east, north] of a region's places.
static func region_places_bbox(region_id: String, source: Array) -> Array:
	var box := [180.0, 90.0, -180.0, -90.0]
	for entry in places_in_region(region_id, source):
		box = [minf(box[0], entry["lon"]), minf(box[1], entry["lat"]), maxf(box[2], entry["lon"]), maxf(box[3], entry["lat"])]
	return box


# Rings as {"hole": bool, "points": PackedVector2Array of (lon, lat)}.
static func global_land_rings() -> Array:
	return _rings("global", geodata()["layers"]["global_land"]["rings"])


static func region_land_rings(region_key: String) -> Array:
	return _rings("region:" + region_key, geodata()["layers"]["regions"][region_key]["land"]["rings"])


static func region_roads(region_key: String) -> Array:
	var cache_key := "roads:" + region_key
	if not _ring_cache.has(cache_key):
		var lines := []
		for line in geodata()["layers"]["regions"][region_key]["roads"]["lines"]:
			lines.append({"major": line["type"] == "Major Highway", "points": _points(line["points"])})
		_ring_cache[cache_key] = lines
	return _ring_cache[cache_key]


static func region_clip_bbox(region_key: String) -> Array:
	return geodata()["layers"]["regions"][region_key]["clip_bbox_wsen"]


static func is_on_land(lon: float, lat: float, rings: Array) -> bool:
	var inside := false
	var point := Vector2(lon, lat)
	for ring in rings:
		if Geometry2D.is_point_in_polygon(point, ring["points"]):
			inside = not inside
	return inside


static func text(entry: Dictionary, field: String, language: String) -> String:
	var names: Dictionary = entry.get(field, entry.get("name", {}))
	return String(names.get(language, names.get("en", "")))


static func _rings(cache_key: String, source: Array) -> Array:
	if not _ring_cache.has(cache_key):
		var rings := []
		for ring in source:
			rings.append({"hole": bool(ring["hole"]), "points": _points(ring["points"])})
		_ring_cache[cache_key] = rings
	return _ring_cache[cache_key]


static func _points(flat: Array) -> PackedVector2Array:
	var points := PackedVector2Array()
	points.resize(flat.size() / 2)
	for i in points.size():
		points[i] = Vector2(flat[i * 2], flat[i * 2 + 1])
	return points


static func _load_json(path: String) -> Dictionary:
	var data = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(data) != TYPE_DICTIONARY:
		push_error("World map data missing or invalid: " + path)
		return {}
	return data
