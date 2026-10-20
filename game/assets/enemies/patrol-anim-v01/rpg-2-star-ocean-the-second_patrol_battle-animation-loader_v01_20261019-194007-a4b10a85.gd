extends RefCounted

# Patrol machine battle animation pilot loader (UNAPPROVED, visual only). The battle loads this script only when
# `-- --patrol-battle-animation-pilot` is on. load_package() validates the JSON package, the strip file and every value
# type. Any defect returns {}, and the battle then keeps its placeholder block. It never touches stats, AI, timers or positions.

const REQUIRED_STATES := ["idle", "move", "windup", "strike", "hit", "defeat"]
const TIMED_STATES := ["idle", "strike", "hit", "defeat"]
const PACKAGE_DIR := "res://assets/enemies/patrol-anim-v01/"
const MAX_BYTES := 65536


static func _integral(value: Variant, low: float, high: float) -> bool:
	return (value is float or value is int) and float(value) == floorf(float(value)) and float(value) >= low and float(value) <= high


static func _number(value: Variant, low: float, high: float) -> bool:
	return (value is float or value is int) and is_finite(float(value)) and float(value) >= low and float(value) <= high


static func _pair(value: Variant, low: float, high: float, integral: bool) -> bool:
	if not value is Array or value.size() != 2:
		return false
	for item in value:
		if not (_integral(item, low, high) if integral else _number(item, low, high)):
			return false
	return true


static func _confined_path(path: String, extension: String) -> bool:
	# FileAccess normalizes dot segments and duplicate slashes; require the original spelling to be canonical.
	return path.begins_with(PACKAGE_DIR) and path.ends_with(extension) and not path.contains("\\") and path.simplify_path() == path


static func load_package(path: String) -> Dictionary:
	if not _confined_path(path, ".json") or not FileAccess.file_exists(path):
		return {}
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null or file.get_length() <= 0 or file.get_length() > MAX_BYTES:
		return {}
	var data: Variant = JSON.parse_string(file.get_as_text())
	if not data is Dictionary:
		return {}
	if data.get("schema") != "worlds-between.enemy-battle-animation.v1" or data.get("enemy") != "patrol":
		return {}
	if not _pair(data.get("cell"), 1, 512, true) or not _pair(data.get("anchor"), 0, 512, false):
		return {}
	if not _integral(data.get("frame_count"), 1, 256) or not _number(data.get("body_center_x"), 0, 512):
		return {}
	if not _number(data.get("gait_step_px"), 0, 64) or not _number(data.get("move_grace"), 0, 1):
		return {}
	if not _number(data.get("telegraph_center_y"), 0, 360) or not _pair(data.get("telegraph_scale"), 0.1, 8, false):
		return {}
	if not data.get("windup_phases") is bool or not data.get("front_states") is Array:
		return {}
	var frame_count := int(data["frame_count"])
	var states: Variant = data.get("states")
	var times: Variant = data.get("frame_time")
	if not states is Dictionary or not times is Dictionary:
		return {}
	var clean_states := {}
	for state in REQUIRED_STATES:
		var frames: Variant = states.get(state)
		if not frames is Array or frames.is_empty():
			return {}
		var clean: Array[int] = []
		for frame in frames:
			if not _integral(frame, 0, frame_count - 1):
				return {}
			clean.append(int(frame))
		clean_states[state] = clean
	var clean_times := {}
	for state in TIMED_STATES:
		if not _number(times.get(state), 0.01, 5.0):
			return {}
		clean_times[state] = float(times[state])
	if float(data["gait_step_px"]) <= 0.0:
		if not _number(times.get("move"), 0.01, 5.0):
			return {}
		clean_times["move"] = float(times["move"])
	var front: Array[String] = []
	for state in data["front_states"]:
		if not state is String or not REQUIRED_STATES.has(state):
			return {}
		front.append(state)
	var strip_path: Variant = data.get("strip")
	if not strip_path is String or not _confined_path(strip_path, ".png"):
		return {}
	var strip_sha: Variant = data.get("strip_sha256")
	if not strip_sha is String or strip_sha.length() != 64 or not FileAccess.file_exists(strip_path):
		return {}
	if FileAccess.get_sha256(strip_path) != strip_sha:
		return {}
	if not ResourceLoader.exists(strip_path):
		return {}
	var strip := load(strip_path) as Texture2D
	var cell := Vector2(float(data["cell"][0]), float(data["cell"][1]))
	if strip == null or strip.get_width() != int(cell.x) * frame_count or strip.get_height() != int(cell.y):
		return {}
	var anchor := Vector2(float(data["anchor"][0]), float(data["anchor"][1]))
	return {
		"texture": strip,
		"telegraph_center_y": float(data["telegraph_center_y"]),
		"telegraph_scale": Vector2(float(data["telegraph_scale"][0]), float(data["telegraph_scale"][1])),
		"animation": {
			"path": strip_path,
			"cell": cell,
			"anchor": anchor,
			"body_center_x": float(data["body_center_x"]),
			"states": clean_states,
			"frame_time": clean_times,
			"gait_step_px": float(data["gait_step_px"]),
			"move_grace": float(data["move_grace"]),
			"front_states": front,
			"windup_phases": bool(data["windup_phases"]),
		},
	}
