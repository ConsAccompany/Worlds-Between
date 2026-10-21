extends "res://scripts/exploration_sprite_set_pilot.gd"

# Opt-in male exploration driver (motion and art UNAPPROVED). Presentation only: the host keeps its own position,
# 140 logical px/s speed and collision; this node only picks textures. It plays the generic mexplore23 idle/walk set
# (validated whole by the unchanged generic loader) plus the authored phase-aware stop supplement: when the host
# stops at walk frame p, play [walk p, s1, s2, idle f00] at frame_ms each, then idle. Any walk() during a bridge
# (re-press or reversal) cancels it at once and restarts walk frame 0; a facing change cancels it too.
# Off unless enabled_override = 1 (set by the mpath24 config) or DEFAULT_ADOPTED is true. DEFAULT_ADOPTED is the
# creator-authorized ordinary default (2026-10-21); battle consults the same switch. Art/motion remain unapproved.

const REGISTRY_PATH := "res://data/mexplore23/rpg-2-star-ocean-the-second_protagonist-male_explore-sprite-set-registry_unapproved-mexplore23-v01_20261021-162551-15fcefc2.json"
const SUPPLEMENT_PATH := "res://data/mexplore23/rpg-2-star-ocean-the-second_protagonist-male_explore-stop-transition-supplemental_unapproved-mexplore23-v01_20261021-162551-76a51a59.json"
const SUPPLEMENT_SCHEMA := "worlds-between.exploration-stop-transition.supplemental.v1"
const ACTOR := "protagonist-male"
const COMBAT_INDEX_PATH := "res://data/mcombat22/rpg-2-star-ocean-the-second_protagonist-male-combat_runtime-index_unapproved-v01_20261021-154716-8dee0dda.json"
const COMBAT_LOADER_PATH := "res://scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd"
const DEFAULT_ADOPTED := true
const BRIDGE_LENGTH := 4

static var male_enabled_override := -1
static var registry_path_override := ""
static var supplement_path_override := ""
static var _prepared := {}

var bridges := {}
var frame_ms := 40
var bridge_active := false
var bridge_phase := -1


static func male_enabled() -> bool:
	if male_enabled_override >= 0:
		return male_enabled_override == 1
	if not DEFAULT_ADOPTED:
		return false
	# Preserve explicit generic exploration choices when the ordinary male default is later authorized.
	var generic = load("res://scripts/exploration_sprite_set_pilot.gd")
	if generic.enabled_override >= 0 or generic.registry_override != "" or OS.get_cmdline_user_args().has(generic.FLAG):
		return false
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with(generic.REGISTRY_ARG):
			return false
	return true


static func male_registry_path() -> String:
	return registry_path_override if registry_path_override != "" else REGISTRY_PATH


static func male_supplement_path() -> String:
	return supplement_path_override if supplement_path_override != "" else SUPPLEMENT_PATH


static func clear_male_cache() -> void:
	_prepared.clear()


# Whole-package validation: {"ok", "errors", "set", "bridges", "frame_ms"}. Cached per (registry, supplement) pair.
static func prepare_package(registry: String, supplement: String) -> Dictionary:
	var key := registry + "|" + supplement
	if _prepared.has(key):
		return _prepared[key]
	var result := _prepare_uncached(registry, supplement)
	_prepared[key] = result
	return result


static func _refused(errors: Array[String]) -> Dictionary:
	return {"ok": false, "errors": errors, "set": {}, "bridges": {}, "frame_ms": 0}


static func _prepare_uncached(registry: String, supplement: String) -> Dictionary:
	var errors: Array[String] = []
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
	var sprite_set_data: Dictionary = loaded["set"]
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
	if Vector2(_pair(data.get("pivot"))) != sprite_set_data["pivot"]:
		errors.append("stop supplement pivot differs from the set pivot")
	var by_direction = data.get("phase_bridges")
	if not by_direction is Dictionary or by_direction.size() != DIRECTIONS.size() or not by_direction.has_all(DIRECTIONS):
		errors.append("phase_bridges must list exactly south, west, north and east")
		return _refused(errors)
	var base_dir := supplement.get_base_dir()
	var density: int = sprite_set_data["density"]
	var frame_size := Vector2i(sprite_set_data["frame_size"])
	var pivot := Vector2i(sprite_set_data["pivot"])
	var out := {}
	for direction in DIRECTIONS:
		var walk_clip: Dictionary = sprite_set_data["clips"]["walk"][direction]
		var idle_clip: Dictionary = sprite_set_data["clips"]["idle"][direction]
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
	# Validate combat as well: default adoption must never mix a new exploration set with a broken battle set.
	var combat = load(COMBAT_LOADER_PATH)
	var index: Dictionary = combat.load_index(COMBAT_INDEX_PATH)
	if String(index.get("status", "")) != "loaded" or not index.get("sets", {}).has("hero:male"):
		errors.append("male combat index missing or rejected")
		return _refused(errors)
	var battle_set: Dictionary = combat.load_set(String(index["sets"]["hero:male"]), "hero:male")
	if String(battle_set.get("status", "")) != "loaded":
		errors.append("male combat set rejected")
		return _refused(errors)
	return {"ok": true, "errors": errors, "set": sprite_set_data, "bridges": out, "frame_ms": ms}


static func _sha256(path: String) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(FileAccess.get_file_as_bytes(path))
	return context.finish().hex_encode()


# Returns the male driver drawing `target`, or null (off, other actor, or package refused whole: legacy textures).
static func attach_male(target: Sprite2D, actor: String, initial_facing: String) -> Node:
	if actor != ACTOR or target == null or not male_enabled():
		return null
	var prepared := prepare_package(male_registry_path(), male_supplement_path())
	if not prepared["ok"]:
		return null
	var driver = new()
	driver.name = "MalePlayablePathDriver"
	driver.sprite = target
	driver.actor_id = actor
	driver.sprite_set = prepared["set"]
	driver.bridges = prepared["bridges"]
	driver.frame_ms = prepared["frame_ms"]
	driver.facing = initial_facing if DIRECTIONS.has(initial_facing) else "south"
	var density: int = prepared["set"]["density"]
	var frame_size: Vector2 = prepared["set"]["frame_size"]
	var pivot: Vector2 = prepared["set"]["pivot"]
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
		# Settled on idle f00 (same texture as the bridge's last entry); continue the idle clip from its start.
		_end_bridge()
		clock_us -= (BRIDGE_LENGTH - 1) * frame_ms * 1000
	super._apply()


func state() -> Dictionary:
	if bridge_active:
		return {"actor_id": actor_id, "set_id": sprite_set["set_id"], "action": "stop", "facing": facing,
			"frame": frame, "clock_us": clock_us, "phase": bridge_phase, "path": ""}
	return super.state()
