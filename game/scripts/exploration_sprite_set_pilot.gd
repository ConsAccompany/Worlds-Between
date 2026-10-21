extends Node

# Opt-in high-density four-direction idle + walk sprite sets for the exploration avatar (pilot capability,
# not art adoption). Off by default: without `-- --exploration-sprite-set-pilot` (or enabled_override = 1)
# attach() returns null before reading any file, and the host keeps its legacy 32x48 textures unchanged.
# With the flag, attach() reads the registry (`--exploration-sprite-set-registry=<res:// or user:// json>`,
# default DEFAULT_REGISTRY, which lists no sets because no high-density set is approved yet), validates the
# set listed for the actor and, only if every frame passes, drives the host's Sprite2D from it. A set with
# any bad frame is rejected whole (no mixing with legacy frames); the actor then keeps the legacy textures.
# Exception (prepared, creator adoption pending, art UNAPPROVED): with no explicit exploration flag/override the
# female protagonist gets the front17 Sea distance driver via the hsea18 heroine default policy, or legacy if refused.
#
# Set contract (schema SET_SCHEMA, one JSON per actor, frame files relative to the JSON or res://):
#   density: 2..4 source texels per logical px (display scale 1/density; 2 = the 80x112 master cell).
#   frame_size: [w, h] texels, every frame exactly this size, at most 64 logical px each way.
#   pivot: [x, y] ground pin in texels; y is the floor line just under the soles (last opaque row + 1).
#   actions: exactly {"idle", "walk"}, each with exactly south/west/north/east frame lists
#            (idle 1..16 frames, walk 2..16), each frame {"file", "duration_ms": integer 40..2000}.
#   frames: res:// Texture2D, uncompressed, binary alpha, nothing opaque on the cell border, no opaque
#           texel at or below the floor line; idle frames stand on it with a 48 logical px (+-1 texel) body.
# Rendering: the pin's floor line is drawn FLOOR_DROP_LOGICAL px below the node position, the row legacy
# 32x48 soles occupy (texel row 44 at offset (0, -20)), so feet, collision, y-sort and occlusion keep their
# legacy contact row. Frames advance on a microsecond clock from real frame deltas (this node processes
# before its host), so cadence does not depend on the frame rate; any (action, facing) change restarts at
# frame 0. Textures are loaded and checked once per set path and cached for the session; drawing never
# reads files.

const FLAG := "--exploration-sprite-set-pilot"
const REGISTRY_ARG := "--exploration-sprite-set-registry="
const DEFAULT_REGISTRY := "res://data/exploration-sprite-sets/rpg-2-star-ocean-the-second_exploration-sprite-set-registry_no-approved-sets-v01_20261018-153932-9f31902d.json"
const REGISTRY_SCHEMA := "worlds-between.exploration-sprite-set-registry.v1"
const SET_SCHEMA := "worlds-between.exploration-sprite-set.v1"
const DIRECTIONS := ["south", "west", "north", "east"]
const ACTIONS := ["idle", "walk"]
const MIN_FRAMES := {"idle": 1, "walk": 2}
const MAX_FRAMES := 16
const FemaleCompletePilot := preload("res://scripts/fexp/rpg-2-star-ocean-the-second_female-complete-explore_driver_pilot-v01_20261019-184900-f2c0a7e1.gd")
const HeroineDefault := preload("res://scripts/hsea18/rpg-2-star-ocean-the-second_heroine-normal-default_policy_runtime-v01_20261021-032237-7c02af94.gd")
const MIN_DURATION_MS := 40
const MAX_DURATION_MS := 2000
const BODY_LOGICAL := 48
const MAX_LOGICAL := 64
const FLOOR_DROP_LOGICAL := 1.0

static var enabled_override := -1
static var registry_override := ""
# path -> {"ok", "errors", "actors"} / {"ok", "errors", "set"}; failures are cached too.
static var _registries := {}
static var _sets := {}
static var texture_loads := 0
static var manifest_reads := 0

var sprite: Sprite2D
var actor_id := ""
var sprite_set := {}
var facing := "south"
var action := "idle"
var clock_us := 0
var _clock_fraction_us := 0.0
var frame := -1


static func enabled() -> bool:
	if enabled_override >= 0:
		return enabled_override == 1
	return OS.get_cmdline_user_args().has(FLAG)


static func registry_path() -> String:
	if registry_override != "":
		return registry_override
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with(REGISTRY_ARG):
			return arg.substr(REGISTRY_ARG.length())
	return DEFAULT_REGISTRY


static func clear_cache() -> void:
	_registries.clear()
	_sets.clear()
	texture_loads = 0
	manifest_reads = 0
	HeroineDefault.clear_cache()


# Returns the driver now drawing `target`, or null (flag off, no set for the actor, or set rejected).
static func attach(target: Sprite2D, actor: String, initial_facing: String) -> Node:
	# Separate Sea-style distance pilot: opt-in, whole-package refusal, unchanged default.
	var sea_driver = load("res://scripts/hsea09/rpg-2-star-ocean-the-second_heroine-sea_distance-driver_opt-in-v01_20261020-214620-4be375a2.gd")
	# Prepared heroine default (creator adoption pending, art UNAPPROVED): only with no explicit exploration knob.
	# A refused package returns null here (legacy textures), never a generic or partial presentation of it.
	if HeroineDefault.exploration_default_applies(actor):
		if not HeroineDefault.package_ok():
			return null
		return sea_driver.attach_registry(target, actor, initial_facing, HeroineDefault.REGISTRY_PATH)
	if sea_driver.enabled():
		return sea_driver.attach(target, actor, initial_facing)
	# Separate opt-in female complete-exploration pilot (own flag, default off); null falls through unchanged.
	if FemaleCompletePilot.enabled():
		var complete: Node = FemaleCompletePilot.attach(target, actor, initial_facing)
		if complete != null:
			return complete
	if not enabled():
		return null
	var registry := load_registry(registry_path())
	if not registry["ok"]:
		return null
	var set_path: String = registry["actors"].get(actor, "")
	if set_path == "":
		return null
	var result := load_set(set_path, actor)
	if not result["ok"]:
		return null
	var driver = new()
	driver.name = "ExplorationSpriteSetPilot"
	driver.sprite = target
	driver.actor_id = actor
	driver.sprite_set = result["set"]
	driver.facing = initial_facing if DIRECTIONS.has(initial_facing) else "south"
	var density: int = result["set"]["density"]
	var frame_size: Vector2 = result["set"]["frame_size"]
	var pivot: Vector2 = result["set"]["pivot"]
	target.scale = Vector2.ONE / float(density)
	target.offset = frame_size * 0.5 - pivot + Vector2(0.0, FLOOR_DROP_LOGICAL * density)
	target.add_child(driver)
	driver._apply()
	return driver


static func load_registry(path: String) -> Dictionary:
	if _registries.has(path):
		return _registries[path]
	var errors: Array[String] = []
	var actors := {}
	var data = _read_json(path, errors)
	if data is Dictionary:
		if data.get("schema") != REGISTRY_SCHEMA:
			errors.append("registry schema is not " + REGISTRY_SCHEMA)
		var listed = data.get("actors")
		if not listed is Dictionary:
			errors.append("registry actors is not an object")
		else:
			for key in listed:
				if not key is String or not listed[key] is String or String(listed[key]) == "":
					errors.append("registry entry %s is not actor id -> set path" % str(key))
				else:
					actors[key] = _resolve(path.get_base_dir(), listed[key])
	elif errors.is_empty():
		errors.append("registry is not a JSON object")
	var result := {"ok": errors.is_empty(), "errors": errors, "actors": actors if errors.is_empty() else {}}
	if not errors.is_empty():
		push_warning("Exploration sprite set registry %s rejected: %s" % [path, "; ".join(errors)])
	_registries[path] = result
	return result


static func load_set(path: String, expected_actor: String) -> Dictionary:
	var key := path + "|" + expected_actor
	if _sets.has(key):
		return _sets[key]
	var errors: Array[String] = []
	var data = _read_json(path, errors)
	var result := {"ok": false, "errors": errors, "set": {}}
	if data is Dictionary:
		result = validate_set(data, path.get_base_dir(), expected_actor)
	elif errors.is_empty():
		errors.append("set manifest is not a JSON object")
	if not result["ok"]:
		push_warning("Exploration sprite set %s rejected for %s: %s" % [path, expected_actor, "; ".join(result["errors"])])
	_sets[key] = result
	return result


# Checks every field and frame; the set is usable only if the error list comes back empty.
static func validate_set(data: Dictionary, base_dir: String, expected_actor: String) -> Dictionary:
	var errors: Array[String] = []
	if data.get("schema") != SET_SCHEMA:
		errors.append("set schema is not " + SET_SCHEMA)
	if data.get("actor_id") != expected_actor:
		errors.append("set actor_id %s is not %s" % [str(data.get("actor_id")), expected_actor])
	var density := _int_or(data.get("density"), -1)
	if density < 2 or density > 4:
		errors.append("density must be an integer 2..4")
	var frame_size := _pair(data.get("frame_size"))
	var pivot := _pair(data.get("pivot"))
	if density >= 2 and density <= 4:
		if frame_size.x < 1 or frame_size.y < 1 or frame_size.x > MAX_LOGICAL * density or frame_size.y > MAX_LOGICAL * density:
			errors.append("frame_size must be [w, h] within 1..%d texels" % (MAX_LOGICAL * density))
		if pivot.x < 0 or pivot.x >= frame_size.x or pivot.y < 1 or pivot.y > frame_size.y:
			errors.append("pivot must be [x, y] inside the frame (0 <= x < w, 1 <= y <= h)")
	var actions = data.get("actions")
	var clips := {}
	if not actions is Dictionary or actions.size() != ACTIONS.size() or not actions.has_all(ACTIONS):
		errors.append("actions must be exactly idle and walk")
	elif errors.is_empty():
		for action_name in ACTIONS:
			var by_direction = actions[action_name]
			if not by_direction is Dictionary or by_direction.size() != DIRECTIONS.size() or not by_direction.has_all(DIRECTIONS):
				errors.append("%s must list exactly south, west, north and east" % action_name)
				continue
			clips[action_name] = {}
			for direction in DIRECTIONS:
				var clip := _clip(by_direction[direction], "%s/%s" % [action_name, direction], action_name, base_dir, density, frame_size, pivot, errors)
				clips[action_name][direction] = clip
	if not errors.is_empty():
		return {"ok": false, "errors": errors, "set": {}}
	return {"ok": true, "errors": errors, "set": {
		"set_id": str(data.get("set_id", "")), "actor_id": expected_actor, "density": density,
		"frame_size": Vector2(frame_size), "pivot": Vector2(pivot), "clips": clips}}


static func _clip(frames, label: String, action_name: String, base_dir: String, density: int, frame_size: Vector2i, pivot: Vector2i, errors: Array[String]) -> Dictionary:
	var clip := {"textures": [], "paths": [], "ends_us": [], "cycle_us": 0}
	if not frames is Array or frames.size() < MIN_FRAMES[action_name] or frames.size() > MAX_FRAMES:
		errors.append("%s needs %d..%d frames" % [label, MIN_FRAMES[action_name], MAX_FRAMES])
		return clip
	var total := 0
	for index in frames.size():
		var entry = frames[index]
		var where := "%s frame %d" % [label, index + 1]
		if not entry is Dictionary or not entry.get("file") is String:
			errors.append(where + " needs a file")
			continue
		var duration := _int_or(entry.get("duration_ms"), -1)
		if duration < MIN_DURATION_MS or duration > MAX_DURATION_MS:
			errors.append("%s duration_ms must be an integer %d..%d" % [where, MIN_DURATION_MS, MAX_DURATION_MS])
		var path := _resolve(base_dir, entry["file"])
		var texture := _texture(path, where, action_name, density, frame_size, pivot, errors)
		total += maxi(duration, 0) * 1000
		clip["textures"].append(texture)
		clip["paths"].append(path)
		clip["ends_us"].append(total)
	clip["cycle_us"] = total
	return clip


static func _texture(path: String, where: String, action_name: String, density: int, frame_size: Vector2i, pivot: Vector2i, errors: Array[String]) -> Texture2D:
	if not path.begins_with("res://") or not ResourceLoader.exists(path, "Texture2D"):
		errors.append("%s: %s is not an imported res:// texture" % [where, path])
		return null
	var texture := ResourceLoader.load(path, "Texture2D") as Texture2D
	texture_loads += 1
	if texture == null:
		errors.append("%s: %s did not load as Texture2D" % [where, path])
		return null
	if Vector2i(texture.get_size()) != frame_size:
		errors.append("%s: %s is %s, not %s" % [where, path, str(Vector2i(texture.get_size())), str(frame_size)])
		return null
	var image := texture.get_image()
	if image == null or image.is_empty() or image.is_compressed():
		errors.append("%s: %s pixels are not readable uncompressed" % [where, path])
		return null
	image = image.duplicate()
	image.convert(Image.FORMAT_RGBA8)
	var bytes := image.get_data()
	var width := frame_size.x
	var height := frame_size.y
	var partial := 0
	var border := 0
	for i in range(3, bytes.size(), 4):
		var alpha := bytes[i]
		if alpha == 0:
			continue
		if alpha != 255:
			partial += 1
		var texel := i >> 2
		var x := texel % width
		var y := texel / width
		if x == 0 or y == 0 or x == width - 1 or y == height - 1:
			border += 1
	var used := image.get_used_rect()
	if partial > 0:
		errors.append("%s: %d partial-alpha texels (alpha must be 0 or 255)" % [where, partial])
	if border > 0:
		errors.append("%s: %d opaque texels on the cell border" % [where, border])
	if used.size.y == 0:
		errors.append("%s: frame is empty" % where)
		return texture
	if used.end.y > pivot.y:
		errors.append("%s: opaque texels below the floor line (row %d > pivot %d)" % [where, used.end.y - 1, pivot.y - 1])
	if used.size.y > BODY_LOGICAL * density + 1:
		errors.append("%s: body %d texels is taller than %d logical px" % [where, used.size.y, BODY_LOGICAL])
	if action_name == "idle":
		if used.end.y != pivot.y:
			errors.append("%s: idle soles end on row %d, not on the floor line row %d" % [where, used.end.y - 1, pivot.y - 1])
		if absi(used.size.y - BODY_LOGICAL * density) > 1:
			errors.append("%s: idle body is %d texels, not %d +-1 (%d logical px)" % [where, used.size.y, BODY_LOGICAL * density, BODY_LOGICAL])
	return texture


static func _read_json(path: String, errors: Array[String]):
	if not (path.begins_with("res://") or path.begins_with("user://")) or not FileAccess.file_exists(path):
		errors.append("manifest %s does not exist (res:// or user:// only)" % path)
		return null
	manifest_reads += 1
	var json := JSON.new()
	if json.parse(FileAccess.get_file_as_string(path)) != OK:
		errors.append("manifest %s is not valid JSON (line %d: %s)" % [path, json.get_error_line(), json.get_error_message()])
		return null
	return json.data


static func _resolve(base_dir: String, file: String) -> String:
	if file.contains("://"):
		return file
	return base_dir.path_join(file).simplify_path()


static func _int_or(value, fallback: int) -> int:
	if (value is int) or (value is float and is_finite(value) and value == floorf(value)):
		return int(value)
	return fallback


static func _pair(value) -> Vector2i:
	if value is Array and value.size() == 2 and _int_or(value[0], -1) >= 0 and _int_or(value[1], -1) >= 0:
		return Vector2i(_int_or(value[0], -1), _int_or(value[1], -1))
	return Vector2i(-1, -1)


func _init() -> void:
	# Advance the clock before the host's _process reads it, so a host that mirrors the texture in the same
	# frame (the science city canopy silhouette) never lags.
	process_priority = -1


func _process(delta: float) -> void:
	advance(delta)


func advance(delta: float) -> void:
	# Carry sub-microsecond time between ticks; rounding each delta alone drifts at
	# common 30/60 fps clip boundaries (e.g. 400 ms). Round the accumulated time.
	var elapsed_us := maxf(delta, 0.0) * 1000000.0 + _clock_fraction_us
	var whole_us := int(round(elapsed_us))
	clock_us += whole_us
	_clock_fraction_us = elapsed_us - whole_us


# Host calls: face() on a facing change, walk() each frame the avatar moved, idle() each frame it did not.
func face(next_facing: String) -> void:
	if next_facing != facing and DIRECTIONS.has(next_facing):
		facing = next_facing
		clock_us = 0
		_clock_fraction_us = 0.0
	_apply()


func walk() -> void:
	_set_action("walk")


func idle() -> void:
	_set_action("idle")


func _set_action(next_action: String) -> void:
	if next_action != action:
		action = next_action
		clock_us = 0
		_clock_fraction_us = 0.0
	_apply()


static func frame_at(clip: Dictionary, elapsed_us: int) -> int:
	var ends: Array = clip["ends_us"]
	var t := elapsed_us % int(clip["cycle_us"])
	for index in ends.size():
		if t < int(ends[index]):
			return index
	return ends.size() - 1


func _apply() -> void:
	var clip: Dictionary = sprite_set["clips"][action][facing]
	frame = frame_at(clip, clock_us)
	var texture: Texture2D = clip["textures"][frame]
	if sprite.texture != texture:
		sprite.texture = texture


func state() -> Dictionary:
	var clip: Dictionary = sprite_set["clips"][action][facing]
	return {"actor_id": actor_id, "set_id": sprite_set["set_id"], "action": action, "facing": facing,
		"frame": frame, "clock_us": clock_us, "path": clip["paths"][frame]}
