extends RefCounted

# Equidistant cylindrical projection plus a pan/zoom view over it.
# Projected units: x = (lon - central_meridian) * cos(standard_parallel), y = -lat.
# One unit is one degree of latitude, so screen distance stays proportional to ground
# distance near the standard parallel. With standard_parallel 0 this is plate carrée,
# which shows the whole Earth (lon -180..180, lat -90..90) in a 2:1 frame.

const EARTH_RADIUS_KM := 6371.0088
const KM_PER_DEGREE_LAT := PI * EARTH_RADIUS_KM / 180.0

var central_meridian := 0.0
var standard_parallel := 0.0
var x_factor := 1.0

# View state. viewport is in logical canvas pixels; center is in projected units.
var viewport := Rect2(0, 0, 640, 360)
var bounds := Rect2(-180, -90, 360, 180)
var center := Vector2.ZERO
var scale := 1.0
var min_scale := 1.0
var max_scale := 1.0


func _init(meridian := 0.0, parallel := 0.0) -> void:
	central_meridian = meridian
	standard_parallel = parallel
	x_factor = cos(deg_to_rad(parallel))


func project(lon: float, lat: float) -> Vector2:
	return Vector2((lon - central_meridian) * x_factor, -lat)


func unproject(unit: Vector2) -> Vector2:
	return Vector2(unit.x / x_factor + central_meridian, -unit.y)


func project_bbox(wsen: Array) -> Rect2:
	var a := project(wsen[0], wsen[3])
	var b := project(wsen[2], wsen[1])
	return Rect2(a, b - a)


func geo_to_screen(lon: float, lat: float) -> Vector2:
	return unit_to_screen(project(lon, lat))


func unit_to_screen(unit: Vector2) -> Vector2:
	return viewport.get_center() + (unit - center) * scale


func screen_to_geo(point: Vector2) -> Vector2:
	return unproject(center + (point - viewport.get_center()) / scale)


func unit_transform() -> Transform2D:
	return Transform2D(0.0, Vector2(scale, scale), 0.0, viewport.get_center() - center * scale)


# Smallest zoom shows the entire bounds ("contain") or fills the frame with them ("cover").
func configure(view_rect: Rect2, unit_bounds: Rect2, cover: bool, zoom_range: float) -> void:
	viewport = view_rect
	bounds = unit_bounds
	var sx := viewport.size.x / bounds.size.x
	var sy := viewport.size.y / bounds.size.y
	min_scale = maxf(sx, sy) if cover else minf(sx, sy)
	max_scale = min_scale * zoom_range
	scale = min_scale
	center = bounds.get_center()


func set_scale_clamped(value: float) -> void:
	scale = clampf(value, min_scale, max_scale)
	clamp_center()


func zoom_at(screen_point: Vector2, factor: float) -> void:
	var anchor := center + (screen_point - viewport.get_center()) / scale
	var new_scale := clampf(scale * factor, min_scale, max_scale)
	center = anchor - (screen_point - viewport.get_center()) / new_scale
	scale = new_scale
	clamp_center()


func pan_pixels(delta: Vector2) -> void:
	center -= delta / scale
	clamp_center()


# Keeps the frame inside the bounds; an axis larger than the bounds is centred.
func clamp_center() -> void:
	var half := viewport.size / (2.0 * scale)
	for axis in 2:
		var low := bounds.position[axis] + half[axis]
		var high := bounds.end[axis] - half[axis]
		center[axis] = bounds.get_center()[axis] if low > high else clampf(center[axis], low, high)


# Centres and zooms so a lon/lat box fits inside target (a sub-rect of viewport).
func frame_geo_box(wsen: Array, target: Rect2) -> void:
	var box := project_bbox(wsen)
	var fit := minf(target.size.x / maxf(box.size.x, 0.0001), target.size.y / maxf(box.size.y, 0.0001))
	scale = clampf(fit, min_scale, max_scale)
	center = box.get_center() - (target.get_center() - viewport.get_center()) / scale
	clamp_center()


func visible_geo_rect() -> Rect2:
	var nw := screen_to_geo(viewport.position)
	var se := screen_to_geo(viewport.end)
	return Rect2(nw.x, se.y, se.x - nw.x, nw.y - se.y)


func km_per_pixel() -> float:
	return KM_PER_DEGREE_LAT / scale


static func great_circle_km(lon_a: float, lat_a: float, lon_b: float, lat_b: float) -> float:
	var p1 := deg_to_rad(lat_a)
	var p2 := deg_to_rad(lat_b)
	var dp := p2 - p1
	var dl := deg_to_rad(lon_b - lon_a)
	var h := sin(dp / 2.0) ** 2 + cos(p1) * cos(p2) * sin(dl / 2.0) ** 2
	return 2.0 * EARTH_RADIUS_KM * asin(minf(1.0, sqrt(h)))


static func format_lat_lon(lon: float, lat: float) -> String:
	return "%.3f°%s  %.3f°%s" % [absf(lat), "N" if lat >= 0.0 else "S", absf(lon), "E" if lon >= 0.0 else "W"]
