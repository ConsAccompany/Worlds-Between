extends RefCounted

# Foot-position geometry traced against the 640x360 city candidate.
# Includes a small clearance around solid bases; foliage is not a solid wall.
const MINIMUM := Vector2(24, 160)
const MAXIMUM := Vector2(616, 305)
static var OBSTACLES := [
	PackedVector2Array([Vector2(24, 214), Vector2(64, 214), Vector2(64, 204), Vector2(176, 204), Vector2(196, 216), Vector2(228, 216), Vector2(248, 244), Vector2(260, 278), Vector2(260, 305), Vector2(24, 305)]),
	PackedVector2Array([Vector2(234, 223), Vector2(246, 223), Vector2(246, 241), Vector2(234, 241)]),
	PackedVector2Array([Vector2(451, 280), Vector2(464, 270), Vector2(482, 274), Vector2(490, 292), Vector2(490, 305), Vector2(451, 305)]),
]


static func walkable(at: Vector2) -> bool:
	if at.x < MINIMUM.x or at.x > MAXIMUM.x or at.y < MINIMUM.y or at.y > MAXIMUM.y:
		return false
	for polygon in OBSTACLES:
		if Geometry2D.is_point_in_polygon(at, polygon):
			return false
	return true


static func safe_position(at: Vector2) -> Vector2:
	var bounded := at.clamp(MINIMUM, MAXIMUM)
	if walkable(bounded):
		return bounded
	var nearest := Vector2(340, 253)
	var best_distance := INF
	# Check both sides of each edge so polygon winding does not affect recovery.
	for polygon in OBSTACLES:
		for index in polygon.size():
			var start: Vector2 = polygon[index]
			var end: Vector2 = polygon[(index + 1) % polygon.size()]
			var edge_point := Geometry2D.get_closest_point_to_segment(bounded, start, end)
			var normal := (end - start).orthogonal().normalized()
			for sign_value in [-1.0, 1.0]:
				var candidate: Vector2 = edge_point + normal * sign_value * 0.5
				if walkable(candidate) and candidate.distance_squared_to(bounded) < best_distance:
					nearest = candidate
					best_distance = candidate.distance_squared_to(bounded)
	return nearest


static func slide_position(from: Vector2, to: Vector2) -> Vector2:
	var position := safe_position(from)
	var displacement := to - from
	# Sweep short steps rather than checking only the destination. A long frame
	# must not teleport through a narrow pedestal or across the garden corner.
	var steps := maxi(1, ceili(displacement.length() / 2.0))
	var step := displacement / steps
	for index in steps:
		var candidate := (position + step).clamp(MINIMUM, MAXIMUM)
		if walkable(candidate):
			position = candidate
		elif walkable(Vector2(candidate.x, position.y)):
			position.x = candidate.x
		elif walkable(Vector2(position.x, candidate.y)):
			position.y = candidate.y
	return position
