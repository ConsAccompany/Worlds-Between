extends SceneTree

# Builds the compact runtime geodata used by the Godot global Earth map.
# Input is the repository's Natural Earth source copies under assets/reference/geography.
# Nothing is invented: rings and road lines are the source coordinates, rounded to
# 0.001 degrees and (for the regional layer) clipped to a lon/lat box with Godot's
# Clipper-backed Geometry2D. Road lines are approximate geometry only; they carry no
# routing, distance or travel-time meaning.
#
# Run from the repository root:
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --headless --path game \
#     --script ../tools/rpg-2-star-ocean-the-second_earth-map_runtime-geodata-build_m2-v01_20261015-024300-7ef4d180.gd

const TOOL_PATH := "tools/rpg-2-star-ocean-the-second_earth-map_runtime-geodata-build_m2-v01_20261015-024300-7ef4d180.gd"
const OUTPUT_PATH := "game/data/world-map/rpg-2-star-ocean-the-second_earth-map_runtime-geodata_m2-v01_20261015-024300-2595ada6.json"
const SOURCE_DIR := "assets/reference/geography/"
const SOURCES := {
	"ne_110m_land": {
		"file": "rpg-2-star-ocean-the-second_earth_natural-earth-110m-land-source_v01_20261015-000900-c6a2de83.geojson",
		"upstream": "https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_land.geojson",
	},
	"ne_50m_land": {
		"file": "rpg-2-star-ocean-the-second_earth_natural-earth-50m-land-source_v01_20261015-001400-4420ef51.geojson",
		"upstream": "https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_50m_land.geojson",
	},
	"ne_10m_roads_yangtze_delta_subset": {
		"file": "rpg-2-star-ocean-the-second_yangtze-delta_natural-earth-10m-road-subset-source_v01_20261015-001400-f70c8f29.geojson",
		"upstream": "https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_10m_roads.geojson",
	},
}
const LICENSE := "Natural Earth vector data is public domain: https://www.naturalearthdata.com/about/terms-of-use/"
const PRECISION := 0.001
# West, south, east, north in degrees. Wider than the regional view's pan limit so the
# clipped coast never ends inside the visible frame.
const YANGTZE_DELTA_CLIP := [115.0, 27.0, 127.0, 35.0]


func _initialize() -> void:
	var root_dir := ProjectSettings.globalize_path("res://").path_join("..").simplify_path()
	var sources_meta := []
	var parsed := {}
	for id in SOURCES:
		var path: String = root_dir.path_join(SOURCE_DIR + SOURCES[id]["file"])
		var bytes := FileAccess.get_file_as_bytes(path)
		if bytes.is_empty():
			_fail("missing source " + path)
			return
		var data = JSON.parse_string(bytes.get_string_from_utf8())
		if typeof(data) != TYPE_DICTIONARY:
			_fail("invalid GeoJSON " + path)
			return
		parsed[id] = data
		sources_meta.append({
			"id": id,
			"path": SOURCE_DIR + SOURCES[id]["file"],
			"hash_algorithm": "sha256-text-lf-v1",
			"sha256": text_lf_sha256(bytes),
			"upstream": SOURCES[id]["upstream"],
			"license": LICENSE,
		})

	var global_rings := _land_rings(parsed["ne_110m_land"], [])
	var regional_rings := _land_rings(parsed["ne_50m_land"], YANGTZE_DELTA_CLIP)
	var roads := _road_lines(parsed["ne_10m_roads_yangtze_delta_subset"], YANGTZE_DELTA_CLIP)
	var failures := _triangulation_failures(global_rings) + _triangulation_failures(regional_rings)
	if failures > 0:
		_fail("%d land rings do not triangulate" % failures)
		return

	var output := {
		"schema": "worlds-between.world-map.runtime-geodata.v1",
		"status": "geodata_for_placement_not_approved_art",
		"generated_by": TOOL_PATH,
		"coordinate_order": "lon,lat pairs in WGS84 degrees, flattened",
		"precision_degrees": PRECISION,
		"sources": sources_meta,
		"layers": {
			"global_land": {"source": "ne_110m_land", "rings": global_rings},
			"regions": {
				"yangtze_delta": {
					"clip_bbox_wsen": YANGTZE_DELTA_CLIP,
					"land": {"source": "ne_50m_land", "rings": regional_rings},
					"roads": {
						"source": "ne_10m_roads_yangtze_delta_subset",
						"note": "Approximate road geometry for display only. No road names, routing graph, distance or travel time.",
						"lines": roads,
					},
				},
			},
		},
	}
	var out_path := root_dir.path_join(OUTPUT_PATH)
	DirAccess.make_dir_recursive_absolute(out_path.get_base_dir())
	var file := FileAccess.open(out_path, FileAccess.WRITE)
	if file == null:
		_fail("cannot write " + out_path)
		return
	file.store_string(JSON.stringify(output) + "\n")
	file.close()
	print("GEODATA_BUILD_OK global_rings=%d regional_rings=%d road_lines=%d -> %s" % [global_rings.size(), regional_rings.size(), roads.size(), OUTPUT_PATH])
	quit(0)


static func text_lf_sha256(bytes: PackedByteArray) -> String:
	var lf := PackedByteArray()
	lf.resize(bytes.size())
	var n := 0
	for i in bytes.size():
		if bytes[i] == 0x0d and i + 1 < bytes.size() and bytes[i + 1] == 0x0a:
			continue
		lf[n] = bytes[i]
		n += 1
	lf.resize(n)
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(lf)
	return context.finish().hex_encode()


func _land_rings(geojson: Dictionary, clip: Array) -> Array:
	var rings := []
	for feature in geojson["features"]:
		var geometry: Dictionary = feature["geometry"]
		var polygons: Array = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
		for polygon in polygons:
			for ring_index in polygon.size():
				var points := _to_points(polygon[ring_index])
				if points.size() < 3:
					continue
				var pieces: Array = [points]
				if not clip.is_empty():
					if not _bbox_overlaps(points, clip):
						continue
					pieces = Geometry2D.intersect_polygons(points, _clip_polygon(clip))
				var source_hole: bool = ring_index > 0
				var kept := []
				for piece in pieces:
					var rounded := _rounded(piece, true)
					if rounded.size() >= 3 and absf(_area(rounded)) > 0.0000005:
						kept.append(rounded)
				for piece in kept:
					# Clipper reports holes as rings contained by another output ring.
					var hole := source_hole
					for other in kept:
						if other != piece and Geometry2D.is_point_in_polygon(piece[0], other) and absf(_area(other)) > absf(_area(piece)):
							hole = not hole
							break
					rings.append({"hole": hole, "points": _flatten(piece)})
	return rings


func _road_lines(geojson: Dictionary, clip: Array) -> Array:
	var lines := []
	var clip_polygon := _clip_polygon(clip)
	for feature in geojson["features"]:
		var geometry: Dictionary = feature["geometry"]
		var parts: Array = [geometry["coordinates"]] if geometry["type"] == "LineString" else geometry["coordinates"]
		var properties: Dictionary = feature["properties"]
		for part in parts:
			var points := _to_points(part)
			if points.size() < 2:
				continue
			for piece in Geometry2D.intersect_polyline_with_polygon(points, clip_polygon):
				var rounded := _rounded(piece, false)
				if rounded.size() >= 2:
					lines.append({
						"type": String(properties.get("type", "Unknown")),
						"scalerank": int(properties.get("scalerank", 0)),
						"points": _flatten(rounded),
					})
	return lines


func _triangulation_failures(rings: Array) -> int:
	var failures := 0
	for ring in rings:
		var points := PackedVector2Array()
		var flat: Array = ring["points"]
		for i in range(0, flat.size(), 2):
			points.append(Vector2(flat[i], -float(flat[i + 1])))
		if Geometry2D.triangulate_polygon(points).is_empty():
			failures += 1
			push_error("ring fails triangulation: %d points near %s" % [points.size(), str(points[0])])
	return failures


static func _to_points(coordinates: Array) -> PackedVector2Array:
	var points := PackedVector2Array()
	for pair in coordinates:
		points.append(Vector2(float(pair[0]), float(pair[1])))
	return points


static func _rounded(points: PackedVector2Array, closed: bool) -> PackedVector2Array:
	var out := PackedVector2Array()
	for point in points:
		var snapped := Vector2(snappedf(point.x, PRECISION), snappedf(point.y, PRECISION))
		if out.is_empty() or not out[out.size() - 1].is_equal_approx(snapped):
			out.append(snapped)
	if closed and out.size() > 1 and out[0].is_equal_approx(out[out.size() - 1]):
		out.remove_at(out.size() - 1)
	return out


static func _flatten(points: PackedVector2Array) -> Array:
	var flat := []
	for point in points:
		flat.append(snappedf(point.x, PRECISION))
		flat.append(snappedf(point.y, PRECISION))
	return flat


static func _area(points: PackedVector2Array) -> float:
	var sum := 0.0
	for i in points.size():
		var a := points[i]
		var b := points[(i + 1) % points.size()]
		sum += a.x * b.y - b.x * a.y
	return sum * 0.5


static func _clip_polygon(clip: Array) -> PackedVector2Array:
	return PackedVector2Array([Vector2(clip[0], clip[1]), Vector2(clip[2], clip[1]), Vector2(clip[2], clip[3]), Vector2(clip[0], clip[3])])


static func _bbox_overlaps(points: PackedVector2Array, clip: Array) -> bool:
	var rect := Rect2(points[0], Vector2.ZERO)
	for point in points:
		rect = rect.expand(point)
	return rect.intersects(Rect2(clip[0], clip[1], clip[2] - clip[0], clip[3] - clip[1]), true)


func _fail(message: String) -> void:
	push_error("GEODATA_BUILD_FAILED: " + message)
	quit(1)
