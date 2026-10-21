extends "res://scripts/exploration_sprite_set_pilot.gd"

# Opt-in Zhao Ling field-NPC driver (art/motion UNAPPROVED). Zhao is a recruitable companion, not a hero: this node only
# picks textures for the existing field NPC Sprite2D. It never moves the NPC, adds no wandering AI and no follower; the
# host's visibility (hidden on recruitment/return) is unchanged. Ordinary play makes no face/walk/idle calls, so the NPC
# shows the zexplore25 south idle f00 statically, as before. Scripted callers can drive face()/walk()/idle() to prove the
# whole four-direction idle/walk banks and the phase-aware stop supplement: on idle() after walk frame p it plays
# [walk p, s1, s2, idle f00] at frame_ms each; walk() or a facing change during a bridge cancels it.

const ACTOR := "zhao-ling"
const REGISTRY_PATH := "res://data/zexplore25/rpg-2-star-ocean-the-second_zhao-ling_explore-sprite-set-registry_unapproved-zexplore25-v01_20261021-172651-e4428fa8.json"
const SUPPLEMENT_PATH := "res://data/zexplore25/rpg-2-star-ocean-the-second_zhao-ling_explore-stop-transition-supplemental_unapproved-zexplore25-v01_20261021-172651-dfdd3586.json"
const SUPPLEMENT_SCHEMA := "worlds-between.exploration-stop-transition.supplemental.v1"
const BRIDGE_LENGTH := 4

static var _prepared := {}

var bridges := {}
var frame_ms := 40
var bridge_active := false
var bridge_phase := -1


static func clear_zhao_cache() -> void:
	_prepared.clear()


static func _refused(errors: Array[String]) -> Dictionary:
	return {"ok": false, "errors": errors, "set": {}, "bridges": {}, "frame_ms": 0}


static func _sha256(path: String) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(FileAccess.get_file_as_bytes(path))
	return context.finish().hex_encode()


# Whole-package validation (registry, 4-direction idle/walk set, every stop bridge); cached per (registry, supplement).
static func prepare_package(registry: String, supplement: String) -> Dictionary:
	var key := registry + "|" + supplement
	if not _prepared.has(key):
		_prepared[key] = _prepare_uncached(registry, supplement)
	return _prepared[key]


static func _prepare_uncached(registry: String, supplement: String) -> Dictionary:
	var errors: Array[String] = []
	if not FileAccess.file_exists(registry):
		errors.append("registry missing: " + registry)
		return _refused(errors)
	var checked := load_registry(registry)
	if not checked["ok"]:
		errors.append("registry rejected: %s" % str(checked["errors"]))
		return _refused(errors)
	var set_path: String = checked["actors"].get(ACTOR, "")
	if set_path == "":
		errors.append("registry lists no %s set" % ACTOR)
		return _refused(errors)
	var loaded := load_set(set_path, ACTOR)
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
	if data.get("schema") != SUPPLEMENT_SCHEMA or data.get("actor_id") != ACTOR:
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


# Returns the driver now drawing the Zhao field NPC, or null (other member, or package refused whole: legacy texture).
static func attach_npc(target: Sprite2D, member_id: String, registry: String, supplement: String) -> Node:
	if member_id != ACTOR or target == null:
		return null
	var prepared := prepare_package(registry, supplement)
	if not prepared["ok"]:
		return null
	var driver = new()
	driver.name = "ZhaoFieldNpcDriver"
	driver.sprite = target
	driver.actor_id = ACTOR
	driver.sprite_set = prepared["set"]
	driver.bridges = prepared["bridges"]
	driver.frame_ms = prepared["frame_ms"]
	driver.facing = "south"
	var density: int = prepared["set"]["density"]
	var frame_size: Vector2 = prepared["set"]["frame_size"]
	var pivot: Vector2 = prepared["set"]["pivot"]
	# Presentation only: same pivot convention as the hero drivers; Sprite2D.position is never touched.
	target.scale = Vector2.ONE / float(density)
	target.offset = frame_size * 0.5 - pivot + Vector2(0.0, FLOOR_DROP_LOGICAL * density)
	target.add_child(driver)
	driver._apply()
	return driver


func face(next_facing: String) -> void:
	if next_facing != facing and DIRECTIONS.has(next_facing):
		_end_bridge()
	super.face(next_facing)


func walk() -> void:
	if bridge_active:
		_end_bridge()
		action = "walk"
		clock_us = 0
		_clock_fraction_us = 0.0
	super.walk()


func idle() -> void:
	if action == "walk" and not bridge_active:
		bridge_phase = frame_at(sprite_set["clips"]["walk"][facing], clock_us)
		bridge_active = true
		action = "idle"
		clock_us = 0
		_clock_fraction_us = 0.0
	_apply()


func _end_bridge() -> void:
	bridge_active = false
	bridge_phase = -1


func _apply() -> void:
	if bridge_active:
		var index := int(clock_us / (frame_ms * 1000))
		if index < BRIDGE_LENGTH - 1:
			frame = index
			var texture: Texture2D = bridges[facing][bridge_phase][index]
			if sprite.texture != texture:
				sprite.texture = texture
			return
		_end_bridge()
		clock_us -= (BRIDGE_LENGTH - 1) * frame_ms * 1000
	super._apply()


func state() -> Dictionary:
	if bridge_active:
		return {"actor_id": actor_id, "set_id": sprite_set["set_id"], "action": "stop", "facing": facing,
			"frame": frame, "clock_us": clock_us, "phase": bridge_phase, "path": ""}
	return super.state()
