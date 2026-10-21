extends RefCounted
# Presentation-only idle time; the existing distance/settle model remains authoritative.
const DIRECTIONS := ["south", "north", "east", "west"]
const EPSILON_US := 0.0001
var clips := {}
var elapsed_us := 0.0
var facing := "south"
var resting := true
var sample_index := 0

func reset(direction: String = "south") -> void:
	facing = direction
	elapsed_us = 0.0
	resting = true
	sample_index = 0

func step(delta: float, action: String, direction: String, reset_idle: bool = false) -> int:
	if not is_finite(delta) or delta < 0.0 or direction not in DIRECTIONS or action not in ["idle", "walk", "settle"]:
		return -1
	if action != "idle" or reset_idle or direction != facing or not resting:
		elapsed_us = 0.0
	else:
		var cycle: float = float(clips.get(direction, {}).get("cycle_us", 0))
		if cycle > 0.0:
			# Reduce before multiplication so any finite huge delta cannot overflow.
			elapsed_us = fposmod(elapsed_us + fposmod(delta, cycle / 1000000.0) * 1000000.0, cycle)
			if cycle - elapsed_us <= EPSILON_US:
				elapsed_us = 0.0
	facing = direction
	resting = action == "idle"
	sample_index = 0
	if resting:
		var ends: Array = clips.get(direction, {}).get("ends_us", [])
		for index in ends.size():
			if elapsed_us < float(ends[index]) - EPSILON_US:
				sample_index = index
				break
	return sample_index

static func load_supplement(path: String, expected_sha: String, source_set_sha: String, candidate: Dictionary, loader) -> Dictionary:
	if not FileAccess.file_exists(path) or FileAccess.get_sha256(path) != expected_sha:
		return {}
	var data = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not data is Dictionary or data.get("schema") != "worlds-between.exploration-breathing-idle.supplemental.v1" or data.get("source_set_sha256") != source_set_sha:
		return {}
	var directions = data.get("directions")
	if not directions is Dictionary or directions.size() != 4 or not directions.has_all(DIRECTIONS):
		return {}
	var duration = data.get("total_ms")
	if typeof(duration) not in [TYPE_INT, TYPE_FLOAT] or not is_finite(float(duration)) or duration < 800 or duration > 8000 or duration != floor(duration):
		return {}
	var result := {}
	for direction in DIRECTIONS:
		var spec = directions[direction]
		if not spec is Dictionary or not spec.get("frames") is Array:
			return {}
		var frames: Array = spec["frames"]
		if frames.size() < 8 or frames.size() > 12:
			return {}
		for index in frames.size():
			var entry = frames[index]
			if not entry is Dictionary or not entry.get("file") is String or not entry.get("sha256") is String:
				return {}
			var name: String = entry["file"]
			# Only a flat filename or one png/ child; no traversal, absolute paths or nested aliases.
			var filename := name.trim_prefix("png/")
			if filename.is_empty() or filename.contains("/") or filename.contains("\\") or filename.contains("..") or not filename.ends_with(".png"):
				return {}
			var frame_path := path.get_base_dir().path_join(name)
			if not FileAccess.file_exists(frame_path) or FileAccess.get_sha256(frame_path) != entry["sha256"]:
				return {}
			if index == 0 or index == frames.size() - 1:
				var neutral: String = candidate["clips"]["idle"][direction]["paths"][0]
				if FileAccess.get_sha256(neutral) != entry["sha256"]:
					return {}
		var errors: Array[String] = []
		var clip: Dictionary = loader._clip(frames, direction + " breathing idle", "idle", path.get_base_dir(), 2, Vector2i(80,112), Vector2i(40,104), errors)
		if not errors.is_empty() or int(clip["cycle_us"]) != int(duration) * 1000:
			return {}
		result[direction] = clip
	return result
