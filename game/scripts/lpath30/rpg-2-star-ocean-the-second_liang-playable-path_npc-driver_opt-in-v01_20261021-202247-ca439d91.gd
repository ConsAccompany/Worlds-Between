extends "res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_npc-driver_opt-in-v01_20261021-223218-3246d731.gd"

# Liang Xu (梁序) field-NPC driver (creator-authorized MVP default; art/motion UNAPPROVED). Reuses the zpath27 Zhao driver's
# instance behaviour unchanged (four-direction idle/walk, phase-aware stop bridges, frame_ms clock, state()). Only the
# actor, the frozen lexplore28 package paths and a separate per-actor cache differ: the parent's ACTOR constant and its
# static cache are Zhao's, so validation is re-run here with LIANG_ACTOR using the same rules as zpath27. The node only
# picks textures for the existing scifi.city recruit Sprite2D; it never moves it, adds no wandering AI and no follower.

const LIANG_ACTOR := "liang-xu"
const LIANG_REGISTRY_PATH := "res://data/lexplore28/rpg-2-star-ocean-the-second_liang-xu_explore-sprite-set-registry_unapproved-lexplore28-v01_20261021-194350-4041cca1.json"
const LIANG_SUPPLEMENT_PATH := "res://data/lexplore28/rpg-2-star-ocean-the-second_liang-xu_explore-stop-transition-supplemental_unapproved-lexplore28-v01_20261021-194350-aeb675f2.json"

static var _liang_prepared := {}


static func clear_liang_cache() -> void:
	_liang_prepared.clear()


# Whole-package validation for Liang; cached per (registry, supplement) separately from the Zhao cache.
static func prepare_liang_package(registry: String, supplement: String) -> Dictionary:
	var key := registry + "|" + supplement
	if not _liang_prepared.has(key):
		_liang_prepared[key] = _prepare_actor(LIANG_ACTOR, registry, supplement)
	return _liang_prepared[key]


# Same checks as the zpath27 _prepare_uncached, parameterized by actor.
static func _prepare_actor(actor: String, registry: String, supplement: String) -> Dictionary:
	var errors: Array[String] = []
	if not FileAccess.file_exists(registry):
		errors.append("registry missing: " + registry)
		return _refused(errors)
	var checked := load_registry(registry)
	if not checked["ok"]:
		errors.append("registry rejected: %s" % str(checked["errors"]))
		return _refused(errors)
	var set_path: String = checked["actors"].get(actor, "")
	if set_path == "":
		errors.append("registry lists no %s set" % actor)
		return _refused(errors)
	var loaded := load_set(set_path, actor)
	if not loaded["ok"]:
		errors.append("set rejected: %s" % str(loaded["errors"]))
		return _refused(errors)
	var data_set: Dictionary = loaded["set"]
	if not FileAccess.file_exists(supplement):
		errors.append("stop supplement missing: " + supplement)
		return _refused(errors)
	var json := JSON.new()
	var data = json.data if json.parse(FileAccess.get_file_as_string(supplement)) == OK else null
	if typeof(data) != TYPE_DICTIONARY:
		errors.append("stop supplement is not a JSON object")
		return _refused(errors)
	if data.get("schema") != SUPPLEMENT_SCHEMA or data.get("actor_id") != actor:
		errors.append("stop supplement schema/actor mismatch")
	var ms := _int_or(data.get("frame_ms"), -1)
	if ms < MIN_DURATION_MS or ms > MAX_DURATION_MS:
		errors.append("stop supplement frame_ms %s out of range" % str(data.get("frame_ms")))
	if _int_or(data.get("settle_ms_inclusive"), -1) != ms * (BRIDGE_LENGTH - 1):
		errors.append("settle_ms_inclusive must equal frame_ms * %d" % (BRIDGE_LENGTH - 1))
	if Vector2(_pair(data.get("pivot"))) != data_set["pivot"]:
		errors.append("stop supplement pivot differs from the set pivot")
	var by_direction = data.get("phase_bridges")
	if not by_direction is Dictionary or by_direction.size() != DIRECTIONS.size() or not by_direction.has_all(DIRECTIONS):
		errors.append("phase_bridges must list exactly south, west, north and east")
		return _refused(errors)
	var base_dir := supplement.get_base_dir()
	var density: int = data_set["density"]
	var frame_size := Vector2i(data_set["frame_size"])
	var pivot := Vector2i(data_set["pivot"])
	var out := {}
	for direction in DIRECTIONS:
		var walk_clip: Dictionary = data_set["clips"]["walk"][direction]
		var idle_clip: Dictionary = data_set["clips"]["idle"][direction]
		var phases = by_direction[direction]
		var count: int = walk_clip["textures"].size()
		if not phases is Dictionary or phases.size() != count:
			errors.append("%s needs exactly %d phase bridges" % [direction, count])
			continue
		var lists := []
		for phase in count:
			var entries = phases.get("phase%d" % phase)
			var where := "%s/phase%d" % [direction, phase]
			if not entries is Array or entries.size() != BRIDGE_LENGTH:
				errors.append("%s must have %d entries" % [where, BRIDGE_LENGTH])
				continue
			var first = entries[0]
			var last = entries[BRIDGE_LENGTH - 1]
			if not first is Dictionary or first.get("ref") != "walk" or _int_or(first.get("index"), -1) != phase:
				errors.append("%s must start on walk frame %d" % [where, phase])
			if not last is Dictionary or last.get("ref") != "idle" or _int_or(last.get("index"), -1) != 0:
				errors.append("%s must end on idle frame 0" % where)
			var textures := [walk_clip["textures"][phase]]
			for middle in range(1, BRIDGE_LENGTH - 1):
				var entry = entries[middle]
				if not entry is Dictionary or not (entry.get("file") is String) or not (entry.get("sha256") is String):
					errors.append("%s entry %d needs file and sha256" % [where, middle])
					textures.append(null)
					continue
				var path := _resolve(base_dir, entry["file"])
				if not FileAccess.file_exists(path):
					errors.append("%s: missing %s" % [where, path])
					textures.append(null)
					continue
				if _sha256(path) != String(entry["sha256"]).to_lower():
					errors.append("%s: sha256 mismatch for %s" % [where, path])
				textures.append(_texture(path, where, "walk", density, frame_size, pivot, errors))
			textures.append(idle_clip["textures"][0])
			lists.append(textures)
		out[direction] = lists
	if not errors.is_empty():
		return _refused(errors)
	return {"ok": true, "errors": errors, "set": data_set, "bridges": out, "frame_ms": ms}


# Returns the driver now drawing the Liang recruit NPC, or null (other member, or package refused whole: legacy texture).
static func attach_liang_npc(target: Sprite2D, member_id: String, registry: String, supplement: String) -> Node:
	if member_id != LIANG_ACTOR or target == null:
		return null
	var prepared := prepare_liang_package(registry, supplement)
	if not prepared["ok"]:
		return null
	var driver = new()
	driver.name = "LiangFieldNpcDriver"
	driver.sprite = target
	driver.actor_id = LIANG_ACTOR
	driver.sprite_set = prepared["set"]
	driver.bridges = prepared["bridges"]
	driver.frame_ms = prepared["frame_ms"]
	driver.facing = "south"
	var density: int = prepared["set"]["density"]
	var frame_size: Vector2 = prepared["set"]["frame_size"]
	var pivot: Vector2 = prepared["set"]["pivot"]
	# Presentation only, same convention as zpath27: Sprite2D.position and z_index are never touched.
	target.scale = Vector2.ONE / float(density)
	target.offset = frame_size * 0.5 - pivot + Vector2(0.0, FLOOR_DROP_LOGICAL * density)
	target.add_child(driver)
	driver._apply()
	return driver
