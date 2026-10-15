extends SceneTree

# Builds (or, with --check, re-derives and compares) the v02 runtime geodata for the US science
# sphere. It is kept beside the map tests because the task that made it owned only game/ data,
# scripts and tests. It mirrors tools/…runtime-geodata-build_m2-v01…7ef4d180.gd: source coordinates
# rounded to 0.001 degrees and clipped with Godot's Clipper-backed Geometry2D. Nothing is invented.
#
# Inputs:
#   - global_land: copied unchanged from the v01 runtime geodata (Natural Earth 110m land, whose
#     source copy is in assets/reference/geography and is hash-checked by the map smoke).
#   - us_east land: Natural Earth 10m land, release v5.1.2 (public domain).
#   - us_east lakes: Natural Earth 10m lakes v5.1.2, scalerank <= 3 (the Great Lakes, their large
#     bays, Lake Champlain and similar). Each lake's outer boundary becomes a "hole" ring, so the
#     map paints it as water and is_on_land() treats it as water. Lake islands are left out.
# The two 10m source files are NOT stored in the repository (about 15 MB; outside this task's file
# scope). Their upstream URLs and SHA-256 are recorded in the output, so anyone can re-download them
# and re-run this script to reproduce the file byte for byte:
#   curl -L -o <dir>/ne_10m_land.geojson  https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_10m_land.geojson
#   curl -L -o <dir>/ne_10m_lakes.geojson https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_10m_lakes.geojson
#   work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --headless --path game \
#     --script res://tests/<this file> -- --source-dir=<dir> [--check]

const SELF_PATH := "game/tests/rpg-2-star-ocean-the-second_us-science-sphere_runtime-geodata-build_m2-v02_20261015-175011-0a728533.gd"
const V01_PATH := "res://data/world-map/rpg-2-star-ocean-the-second_earth-map_runtime-geodata_m2-v01_20261015-024300-2595ada6.json"
const OUTPUT_PATH := "res://data/world-map/rpg-2-star-ocean-the-second_earth-map_runtime-geodata_m2-us-science-v02_20261015-175011-944d9635.json"
const LICENSE := "Natural Earth vector data is public domain: https://www.naturalearthdata.com/about/terms-of-use/"
const UPSTREAM := "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/"
const SOURCES := {
	"ne_10m_land_v5_1_2": {"file": "ne_10m_land.geojson", "sha256": "1ac90796408bc6ad6911d69448485d3c4dbf2190370080368a09976e1c9f7416"},
	"ne_10m_lakes_v5_1_2": {"file": "ne_10m_lakes.geojson", "sha256": "2d036f53dedec578001c5c30c2959ee7d4eebc1306900fa4367c49929ec8f2d9"},
}
const PRECISION := 0.001
const LAKE_MAX_SCALERANK := 3
# West, south, east, north. Covers New York, Washington, D.C. and Chicago with margin, wider than
# either display region's pan limit so the clipped coast never ends inside the visible frame.
const US_EAST_CLIP := [-93.0, 36.0, -66.0, 47.5]


func _initialize() -> void:
	var source_dir := ""
	var check := false
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--source-dir="):
			source_dir = arg.trim_prefix("--source-dir=")
		elif arg == "--check":
			check = true
	if source_dir == "":
		_fail("pass -- --source-dir=<dir with the two Natural Earth 10m files>")
		return
	var parsed := {}
	var sources_meta := []
	var v01: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(V01_PATH))
	for entry in v01["sources"]:
		if entry["id"] == "ne_110m_land":
			sources_meta.append(entry)
	for id in SOURCES:
		var bytes := FileAccess.get_file_as_bytes(source_dir.path_join(SOURCES[id]["file"]))
		if bytes.is_empty():
			_fail("missing source " + source_dir.path_join(SOURCES[id]["file"]))
			return
		var digest := text_lf_sha256(bytes)
		if digest != SOURCES[id]["sha256"]:
			_fail("source %s hash %s does not match the pinned %s" % [id, digest, SOURCES[id]["sha256"]])
			return
		parsed[id] = JSON.parse_string(bytes.get_string_from_utf8())
		sources_meta.append({
			"id": id,
			"path": null,
			"retained_copy": false,
			"upstream": UPSTREAM + SOURCES[id]["file"],
			"hash_algorithm": "sha256-text-lf-v1",
			"sha256": digest,
			"license": LICENSE,
			"retrieved_on": "2026-10-15",
		})
	var land := _rings(parsed["ne_10m_land_v5_1_2"], US_EAST_CLIP, false, func(_p: Dictionary) -> bool: return true)
	var lakes := _rings(parsed["ne_10m_lakes_v5_1_2"], US_EAST_CLIP, true, func(p: Dictionary) -> bool: return int(p.get("scalerank", 99)) <= LAKE_MAX_SCALERANK and String(p.get("featurecla", "")) == "Lake")
	var failures := _triangulation_failures(land + lakes)
	if failures > 0:
		_fail("%d rings do not triangulate" % failures)
		return
	var output := {
		"schema": "worlds-between.world-map.runtime-geodata.v1",
		"status": "geodata_for_placement_not_approved_art",
		"generated_by": SELF_PATH,
		"coordinate_order": "lon,lat pairs in WGS84 degrees, flattened",
		"precision_degrees": PRECISION,
		"sources": sources_meta,
		"layers": {
			"global_land": v01["layers"]["global_land"],
			"regions": {
				"us_east": {
					"clip_bbox_wsen": US_EAST_CLIP,
					"land": {
						"source": "ne_10m_land_v5_1_2",
						"lake_source": "ne_10m_lakes_v5_1_2",
						"note": "Land rings, then lake rings (hole true) for lakes with scalerank <= %d. Lake islands are omitted. No road layer yet." % LAKE_MAX_SCALERANK,
						"rings": land + lakes,
					},
				},
			},
		},
	}
	var text := JSON.stringify(output) + "\n"
	if check:
		var current := FileAccess.get_file_as_string(OUTPUT_PATH).replace("\r\n", "\n")
		if current != text:
			_fail("committed geodata differs from a fresh build")
			return
		print("US_GEODATA_REPRODUCED_OK land_rings=%d lake_rings=%d" % [land.size(), lakes.size()])
		quit(0)
		return
	var file := FileAccess.open(OUTPUT_PATH, FileAccess.WRITE)
	if file == null:
		_fail("cannot write " + OUTPUT_PATH)
		return
	file.store_string(text)
	file.close()
	print("US_GEODATA_BUILD_OK land_rings=%d lake_rings=%d bytes=%d" % [land.size(), lakes.size(), text.length()])
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


# Outer rings only for lakes (as_holes); land keeps the source's hole flags as in v01.
func _rings(geojson: Dictionary, clip: Array, as_holes: bool, keep: Callable) -> Array:
	var rings := []
	for feature in geojson["features"]:
		if not keep.call(feature.get("properties", {})):
			continue
		var geometry: Dictionary = feature["geometry"]
		var polygons: Array = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
		for polygon in polygons:
			for ring_index in polygon.size():
				if as_holes and ring_index > 0:
					continue
				var points := _to_points(polygon[ring_index])
				if points.size() < 3 or not _bbox_overlaps(points, clip):
					continue
				var kept := []
				for piece in Geometry2D.intersect_polygons(points, _clip_polygon(clip)):
					var rounded := _rounded(piece)
					if rounded.size() >= 3 and absf(_area(rounded)) > 0.0000005:
						kept.append(rounded)
				for piece in kept:
					var hole: bool = as_holes or ring_index > 0
					for other in kept:
						if other != piece and Geometry2D.is_point_in_polygon(piece[0], other) and absf(_area(other)) > absf(_area(piece)):
							hole = not hole
							break
					rings.append({"hole": hole, "points": _flatten(piece)})
	return rings


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


static func _rounded(points: PackedVector2Array) -> PackedVector2Array:
	var out := PackedVector2Array()
	for point in points:
		var snapped := Vector2(snappedf(point.x, PRECISION), snappedf(point.y, PRECISION))
		if out.is_empty() or not out[out.size() - 1].is_equal_approx(snapped):
			out.append(snapped)
	if out.size() > 1 and out[0].is_equal_approx(out[out.size() - 1]):
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
	push_error("US_GEODATA_BUILD_FAILED: " + message)
	quit(1)
