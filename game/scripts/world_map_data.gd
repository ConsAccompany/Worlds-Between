extends RefCounted

# Read-only access to the world-map display registry and the Natural Earth runtime geodata.
# The display registry holds no coordinates or names for travel places: those come only
# from the global travel data (world_route_registry.gd), so map and route core share one
# source. This script only parses files and never adds coordinates of its own.

# v02 (2026-10-15): US science sphere. The v01 registry and geodata (Yangtze Delta) stay on disk
# as records for later Asia work; nothing reads them at run time.
const REGISTRY_PATH := "res://data/world-map/rpg-2-star-ocean-the-second_earth-map_place-registry_m2-us-science-v02_20261015-175011-eeaa6baa.json"
const GEODATA_PATH := "res://data/world-map/rpg-2-star-ocean-the-second_earth-map_runtime-geodata_m2-us-science-v02_20261015-175011-944d9635.json"

# Relief and coastal-shelf layer per geodata key (unapproved map art, 2026-10-17): real elevation and depth
# classes on a lon/lat grid, masked by the same land and lake rings. Baked by
# tools/rpg-2-star-ocean-the-second_global-map_us-east-relief-bake_m2-map-art-native-v01_20261017-015515-aa01b973.py.
const RELIEF_PATHS := {
	"us_east": "res://data/world-map/rpg-2-star-ocean-the-second_earth-map_us-east-relief-layer_m2-map-art-native-v01_20261017-015515-7bf04753.json",
}
# Globe sphere tints (unapproved map art, 2026-10-17): one restrained land colour per Earth civilization sphere,
# on a lon/lat grid, with each global land ring's sphere (or -1 when several share it). Baked from Natural Earth
# countries by tools/rpg-2-star-ocean-the-second_global-map_globe-sphere-tint-bake_m2-map-art-native-v01r1_20261017-022144-f9b0d28b.py.
const GLOBE_TINT_PATH := "res://data/world-map/rpg-2-star-ocean-the-second_earth-map_globe-sphere-tint-layer_m2-map-art-native-v01r1_20261017-022144-f9b0d28b.json"

static var _registry: Dictionary = {}
static var _geodata: Dictionary = {}
static var _relief: Dictionary = {}
static var _globe_tint = null
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


# Geodata layer a display region draws from. Several regions may share one layer.
static func geodata_key(region_id: String) -> String:
	return String(geo_region(region_id).get("geodata_key", region_id))


# Lon/lat box a region opens on: its explicit frame box, else the box of its places.
static func region_frame_bbox(region_id: String, source: Array) -> Array:
	var frame: Variant = geo_region(region_id).get("frame_bbox_wsen")
	if typeof(frame) == TYPE_ARRAY and frame.size() == 4:
		return frame
	return region_places_bbox(region_id, source)


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


# region_key is a geodata layer key (see geodata_key()). Lakes are stored as hole rings.
static func region_land_rings(region_key: String) -> Array:
	return _rings("region:" + region_key, geodata()["layers"]["regions"][region_key]["land"]["rings"])


static func region_roads(region_key: String) -> Array:
	var cache_key := "roads:" + region_key
	if not _ring_cache.has(cache_key):
		var lines := []
		# A layer may have no road subset (the US layer has none yet).
		for line in geodata()["layers"]["regions"][region_key].get("roads", {}).get("lines", []):
			lines.append({"major": line["type"] == "Major Highway", "points": _points(line["points"])})
		_ring_cache[cache_key] = lines
	return _ring_cache[cache_key]


# {"texture": ImageTexture, "bbox_wsen": Array, "land_low_color": String} for a geodata layer, else {}.
# The texture's rows run north to south and its columns west to east, one cell per lon/lat step.
static func region_relief(region_key: String) -> Dictionary:
	if not _relief.has(region_key):
		var entry := {}
		if RELIEF_PATHS.has(region_key) and FileAccess.file_exists(RELIEF_PATHS[region_key]):
			var data := _load_json(RELIEF_PATHS[region_key])
			var image := Image.new()
			if not data.is_empty() and image.load_png_from_buffer(Marshalls.base64_to_raw(String(data["png_base64"]))) == OK:
				entry = {"texture": ImageTexture.create_from_image(image), "bbox_wsen": data["bbox_wsen"], "land_low_color": String(data["land_low_color"])}
		_relief[region_key] = entry
	return _relief[region_key]


# {"texture": ImageTexture, "bbox_wsen": Array, "ring_spheres": Array, "colors": Array[Color], "roles": Array}
# for the globe, else {} (missing file, or baked for a different global land layer). ring_spheres[i] is the
# palette index of global land ring i's one sphere, -1 when several spheres share it, 0 for a hole.
static func globe_sphere_tint() -> Dictionary:
	if _globe_tint == null:
		_globe_tint = {}
		if FileAccess.file_exists(GLOBE_TINT_PATH):
			var data := _load_json(GLOBE_TINT_PATH)
			var image := Image.new()
			if not data.is_empty() and int(data["global_ring_count"]) == global_land_rings().size() 					and image.load_png_from_buffer(Marshalls.base64_to_raw(String(data["png_base64"]))) == OK:
				var colors := []
				var roles := []
				for entry in data["palette"]:
					colors.append(Color(entry["color"]) if entry["color"] != null else Color(0, 0, 0, 0))
					roles.append(String(entry["role"]))
				_globe_tint = {"texture": ImageTexture.create_from_image(image), "bbox_wsen": data["bbox_wsen"],
					"ring_spheres": data["ring_spheres"], "colors": colors, "roles": roles}
	return _globe_tint


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
