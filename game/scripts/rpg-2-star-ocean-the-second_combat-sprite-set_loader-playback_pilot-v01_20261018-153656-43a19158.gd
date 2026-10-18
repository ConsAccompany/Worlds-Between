extends RefCounted

# Combat sprite set pilot: a data-driven loader and playback for high-density SIDE-VIEW fighter action sets in normal battle.
# TECHNICAL capability only. battle_arena.gd creates this helper only under the opt-in `-- --combat-sprite-set-pilot`; without
# it nothing here runs and every fighter keeps its existing frames. No set is approved art, and none is a default.
#
# Rendering only: playback reads the fighter's existing combat state (visual_action / visual_elapsed, dodge_time, guard,
# visual_moving, HP) and the enemy's x for facing. It never writes to a fighter, the enemy, AppState or the save, so reach,
# HP, AI, input, hit timing, positions and party order are the same with the pilot on or off.
#
# Index JSON (schema worlds-between.combat-sprite-set-index/1): {"sets": {"<key>": "<manifest path>"}}, where the key is
# the member id, or "hero:<appearance>" for the protagonist.
# Set manifest JSON (schema worlds-between.combat-sprite-set/1):
#   character        {"member_id", "appearance" (hero only)}; must match the key it is loaded for
#   sheet            PNG of equal cells, left to right then top to bottom (res:// path, or a file name next to the manifest)
#   cell_size        [w, h]; pivot [x, y] = the cell pixel drawn at (round(fighter x), floor y), i.e. the ground anchor
#   authored_facing  "right" or "left"; the other facing is the sheet mirrored about the pivot column, so feet stay put
#   logical_scale    1 only (native logical pixels; the 0.65 battle display proportion is authored into the frames)
#   actions          {name: {"loop": bool, "frames": [{"cell": int, "ms": int, "pivot": [x, y] (optional)}]}}
#                    idle, move, guard loop; attack, dodge, hit, defeat play once (defeat holds its last frame).
#                    skill is optional and falls back to the attack frames.
# A set is validated and cached once per manifest path. Anything missing, malformed, unknown or partial rejects the whole set
# (atomic): that fighter keeps the existing renderer, and the reason is kept in set_status().

const SET_SCHEMA := "worlds-between.combat-sprite-set/1"
const INDEX_SCHEMA := "worlds-between.combat-sprite-set-index/1"
# Required actions and whether each loops.
const REQUIRED_ACTIONS := {"idle": true, "move": true, "guard": true, "attack": false, "dodge": false, "hit": false, "defeat": false}
const OPTIONAL_ACTIONS := {"skill": false}
const SKILL_FALLBACK := "attack"
# One-shot actions started by the combat state's visual_action event.
const EVENT_ACTIONS := ["attack", "hit", "skill"]
const DISPLAY_PROPORTION := "0.65"
# Frame boundaries are compared with this slack, so 30 and 60 fps clocks pick the same frame at shared timestamps.
const CLOCK_EPSILON := 0.000001

static var _set_cache: Dictionary = {}
static var _index_cache: Dictionary = {}
# Counts real manifest validations (cache misses), for the cache test.
static var validation_count := 0

var index_path := ""
var index_status := "off"
# Per fighter index: the loaded set (empty when the fighter falls back), its status and its playback state.
var sets: Array[Dictionary] = []
var statuses: Array[String] = []
var states: Array[Dictionary] = []


static func clear_cache() -> void:
	_set_cache.clear()
	_index_cache.clear()
	validation_count = 0


static func set_key(member_id: String, appearance: String) -> String:
	return "hero:" + appearance if member_id == "hero" else member_id


static func load_index(path: String) -> Dictionary:
	if _index_cache.has(path):
		return _index_cache[path]
	var result := {"status": "loaded", "sets": {}}
	var data: Variant = _read_json(path)
	if data is String:
		result["status"] = data
	elif not data.get("schema") is String or data["schema"] != INDEX_SCHEMA or not data.get("sets") is Dictionary:
		result["status"] = "unknown_index_schema"
	else:
		for key in data["sets"]:
			if not key is String or key.is_empty() or not data["sets"][key] is String or data["sets"][key].is_empty():
				result = {"status": "invalid_index", "sets": {}}
				break
			result["sets"][String(key)] = _resolve(path, String(data["sets"][key]))
	_index_cache[path] = result
	return result


static func load_set(path: String, key: String) -> Dictionary:
	var cache_key := path + "|" + key
	if not _set_cache.has(cache_key):
		validation_count += 1
		_set_cache[cache_key] = _validate(path, key)
	return _set_cache[cache_key]


static func _read_json(path: String) -> Variant:
	if not FileAccess.file_exists(path):
		return "missing_manifest"
	var json := JSON.new()
	if json.parse(FileAccess.get_file_as_string(path)) != OK or not json.data is Dictionary:
		return "invalid_json"
	return json.data


static func _resolve(base_path: String, path: String) -> String:
	return path if path.contains("://") else base_path.get_base_dir().path_join(path)


# JSON numbers are floats. Validate range and finiteness before narrowing to an integer.
static func _integer(value: Variant, minimum: int, maximum: int) -> bool:
	return (value is int or value is float) and is_finite(float(value)) and float(value) == floorf(float(value)) and float(value) >= minimum and float(value) <= maximum


static func _vec2i(value: Variant) -> Variant:
	if not value is Array or value.size() != 2:
		return null
	for part in value:
		if not _integer(part, -2147483648, 2147483647):
			return null
	return Vector2i(int(value[0]), int(value[1]))


static func _fail(status: String) -> Dictionary:
	return {"status": status}


static func _validate(path: String, key: String) -> Dictionary:
	var data: Variant = _read_json(path)
	if data is String:
		return _fail(data)
	if not data.get("schema") is String or data["schema"] != SET_SCHEMA:
		return _fail("unknown_schema")
	var character: Variant = data.get("character")
	if not character is Dictionary:
		return _fail("identity_mismatch")
	if not character.get("member_id") is String or character["member_id"].is_empty():
		return _fail("identity_mismatch")
	if character.has("appearance") and not character["appearance"] is String:
		return _fail("identity_mismatch")
	var member_id: String = character["member_id"]
	var appearance: String = character.get("appearance", "")
	if member_id == "hero" and appearance not in ["male", "female"]:
		return _fail("identity_mismatch")
	if set_key(member_id, appearance) != key:
		return _fail("identity_mismatch")
	if not (data.get("logical_scale") is float or data.get("logical_scale") is int) or float(data["logical_scale"]) != 1.0:
		return _fail("unsupported_scale")
	if not data.get("display_proportion") is String or data["display_proportion"] != DISPLAY_PROPORTION:
		return _fail("unsupported_proportion")
	if not data.get("authored_facing") is String:
		return _fail("invalid_facing")
	var facing: String = data["authored_facing"]
	if facing != "right" and facing != "left":
		return _fail("invalid_facing")
	var cell: Variant = _vec2i(data.get("cell_size"))
	var pivot: Variant = _vec2i(data.get("pivot"))
	if cell == null or cell.x <= 0 or cell.y <= 0:
		return _fail("invalid_cell")
	if pivot == null or not Rect2i(Vector2i.ZERO, cell).has_point(pivot):
		return _fail("invalid_pivot")
	var actions_data: Variant = data.get("actions")
	if not actions_data is Dictionary:
		return _fail("missing_action")
	for action in actions_data:
		if not REQUIRED_ACTIONS.has(action) and not OPTIONAL_ACTIONS.has(action):
			return _fail("unknown_action")
	for action in REQUIRED_ACTIONS:
		if not actions_data.has(action):
			return _fail("missing_action")
	for field in ["set_id", "art_status"]:
		if data.has(field) and not data[field] is String:
			return _fail("invalid_metadata")
	if data.has("art_approved") and not data["art_approved"] is bool:
		return _fail("invalid_metadata")
	if not data.get("sheet") is String or data["sheet"].is_empty():
		return _fail("missing_sheet")
	var sheet_path := _resolve(path, data["sheet"])
	if not ResourceLoader.exists(sheet_path):
		return _fail("missing_sheet")
	var texture := load(sheet_path) as Texture2D
	if texture == null:
		return _fail("missing_sheet")
	var sheet_size := Vector2i(texture.get_size())
	if sheet_size.x % cell.x != 0 or sheet_size.y % cell.y != 0:
		return _fail("sheet_not_cell_multiple")
	var columns: int = sheet_size.x / cell.x
	var cell_count: int = columns * (sheet_size.y / cell.y)
	var image := texture.get_image()
	if image == null:
		return _fail("missing_sheet")
	if image.is_compressed():
		image.decompress()
	var actions := {}
	var all_modes := REQUIRED_ACTIONS.merged(OPTIONAL_ACTIONS)
	var empty_checked := {}
	for action in actions_data:
		var entry: Variant = actions_data[action]
		if not entry is Dictionary or not entry.get("loop") is bool or not entry.get("frames") is Array or entry["frames"].is_empty():
			return _fail("invalid_action")
		if bool(entry["loop"]) != bool(all_modes[action]):
			return _fail("invalid_mode")
		var frames: Array[Dictionary] = []
		var end_time := 0.0
		for frame_data in entry["frames"]:
			if not frame_data is Dictionary or not _integer(frame_data.get("cell"), 0, cell_count - 1):
				return _fail("frame_out_of_range")
			var cell_index := int(frame_data["cell"])
			if float(frame_data["cell"]) != float(cell_index) or cell_index < 0 or cell_index >= cell_count:
				return _fail("frame_out_of_range")
			var ms: Variant = frame_data.get("ms")
			if not _integer(ms, 1, 2147483647):
				return _fail("invalid_frame")
			var frame_pivot: Variant = pivot
			if frame_data.has("pivot"):
				frame_pivot = _vec2i(frame_data["pivot"])
				if frame_pivot == null or not Rect2i(Vector2i.ZERO, cell).has_point(frame_pivot):
					return _fail("invalid_pivot")
			var origin := Vector2i(cell_index % columns * cell.x, cell_index / columns * cell.y)
			if not empty_checked.has(cell_index):
				if image.get_region(Rect2i(origin, cell)).is_invisible():
					return _fail("empty_frame")
				empty_checked[cell_index] = true
			end_time += int(ms) / 1000.0
			frames.append({"cell": cell_index, "origin": origin, "pivot": frame_pivot, "end": end_time})
		actions[action] = {"loop": bool(entry["loop"]), "frames": frames, "duration": end_time, "source": action}
	if not actions.has("skill"):
		actions["skill"] = actions[SKILL_FALLBACK].duplicate()
		actions["skill"]["source"] = SKILL_FALLBACK
	var mirrored_image := image.duplicate() as Image
	mirrored_image.flip_x()
	return {
		"status": "loaded",
		"key": key,
		"set_id": String(data.get("set_id", "")),
		"art_status": String(data.get("art_status", "")),
		"art_approved": data.get("art_approved") == true,
		"manifest": path,
		"sheet": sheet_path,
		"texture": texture,
		"mirrored": ImageTexture.create_from_image(mirrored_image),
		"sheet_size": sheet_size,
		"cell": cell,
		"facing": 1 if facing == "right" else -1,
		"actions": actions,
	}


# Frame index into action["frames"] after `clock` seconds: loops wrap, one-shots hold the last frame.
static func frame_at(action: Dictionary, clock: float) -> int:
	var frames: Array = action["frames"]
	var duration: float = action["duration"]
	var t := clock
	if bool(action["loop"]):
		t = fmod(clock + CLOCK_EPSILON, duration) - CLOCK_EPSILON
	for index in frames.size():
		if t + CLOCK_EPSILON < float(frames[index]["end"]):
			return index
	return frames.size() - 1


# Loads one set per fighter from the index. `keys` holds the set key of each fighter, in party order.
func configure(path: String, keys: Array[String]) -> void:
	index_path = path
	var index := load_index(path)
	index_status = String(index["status"])
	sets.clear()
	statuses.clear()
	states.clear()
	for key in keys:
		var loaded := {}
		var status := index_status
		if index_status == "loaded":
			if not index["sets"].has(key):
				status = "no_set"
			else:
				loaded = load_set(String(index["sets"][key]), key)
				status = String(loaded["status"])
				if status != "loaded":
					loaded = {}
		sets.append(loaded)
		statuses.append(status)
		states.append({"action": "", "clock": 0.0, "facing": int(loaded.get("facing", 1)), "last_visual_action": "", "last_visual_elapsed": 0.0, "last_dodge_time": 0.0})


func has_set(index: int) -> bool:
	return index >= 0 and index < sets.size() and not sets[index].is_empty()


func set_status(index: int) -> String:
	return statuses[index] if index >= 0 and index < statuses.size() else "no_set"


func loaded_count() -> int:
	var total := 0
	for index in sets.size():
		total += 1 if has_set(index) else 0
	return total


# Advances one fighter's playback after the combat step. Reads combat state only.
func advance(index: int, fighter: Dictionary, alive: bool, enemy_x: float, delta: float) -> void:
	if not has_set(index):
		return
	var sprite_set: Dictionary = sets[index]
	var state: Dictionary = states[index]
	var dx := enemy_x - float(fighter["x"])
	# Face the enemy; within half a pixel keep the current facing so it never flickers.
	if absf(dx) >= 0.5:
		state["facing"] = 1 if dx > 0.0 else -1
	var visual_action := String(fighter["visual_action"])
	var visual_elapsed := float(fighter["visual_elapsed"])
	var dodge_time := float(fighter["dodge_time"])
	# A new attack / hit / skill: the event action changed, or the same one restarted (its elapsed time went back).
	var event := EVENT_ACTIONS.has(visual_action) and (visual_action != String(state["last_visual_action"]) or visual_elapsed < float(state["last_visual_elapsed"]))
	var current := String(state["action"])
	var next := "idle"
	var restart := false
	if not alive:
		next = "defeat"
	elif dodge_time > 0.0:
		next = "dodge"
		restart = dodge_time > float(state["last_dodge_time"]) and current == "dodge"
	elif event:
		next = visual_action
		restart = true
	elif EVENT_ACTIONS.has(current) and float(state["clock"]) + delta + CLOCK_EPSILON < float(sprite_set["actions"][current]["duration"]):
		# A one-shot plays to its own end unless defeat, a dodge or a new event cuts it.
		next = current
	elif bool(fighter["guard"]):
		next = "guard"
	elif bool(fighter["visual_moving"]):
		next = "move"
	state["last_visual_action"] = visual_action
	state["last_visual_elapsed"] = visual_elapsed
	state["last_dodge_time"] = dodge_time
	if restart or next != current:
		state["action"] = next
		state["clock"] = 0.0
	else:
		state["clock"] = float(state["clock"]) + delta


# The frame a fighter shows now: {"action", "source", "frame", "cell", "pivot", "facing", "mirrored"}; empty without a set.
func current_frame(index: int) -> Dictionary:
	if not has_set(index):
		return {}
	var sprite_set: Dictionary = sets[index]
	var state: Dictionary = states[index]
	var action_name := String(state["action"]) if String(state["action"]) != "" else "idle"
	var action: Dictionary = sprite_set["actions"][action_name]
	var frame_index := frame_at(action, float(state["clock"]))
	var frame: Dictionary = action["frames"][frame_index]
	return {"action": action_name, "source": action["source"], "frame": frame_index, "cell": frame["cell"], "origin": frame["origin"], "pivot": frame["pivot"], "facing": state["facing"], "mirrored": int(state["facing"]) != int(sprite_set["facing"])}


# Top-left screen pixel of the drawn cell. Mirrored cells reflect about the pivot column: a cell pixel at column c lands on
# x - pivot.x + c unmirrored and on x + pivot.x - c mirrored, so the pivot pixel stays on round(x) either way.
func cell_screen_origin(index: int, x: float, floor_y: float) -> Vector2i:
	var frame := current_frame(index)
	var cell: Vector2i = sets[index]["cell"]
	var pivot: Vector2i = frame["pivot"]
	var anchor_x := roundi(x)
	var left := anchor_x - pivot.x if not frame["mirrored"] else anchor_x - (cell.x - 1 - pivot.x)
	return Vector2i(left, int(floor_y) - pivot.y)


func draw_fighter(canvas: CanvasItem, index: int, x: float, floor_y: float) -> bool:
	if not has_set(index):
		return false
	var sprite_set: Dictionary = sets[index]
	var frame := current_frame(index)
	var cell: Vector2i = sprite_set["cell"]
	var origin: Vector2i = frame["origin"]
	var texture: Texture2D = sprite_set["texture"]
	if frame["mirrored"]:
		# The mirrored sheet is the whole sheet flipped, so a cell's column moves to the other side.
		texture = sprite_set["mirrored"]
		origin.x = int(sprite_set["sheet_size"].x) - origin.x - cell.x
	canvas.draw_texture_rect_region(texture, Rect2(Vector2(cell_screen_origin(index, x, floor_y)), Vector2(cell)), Rect2(Vector2(origin), Vector2(cell)))
	return true
